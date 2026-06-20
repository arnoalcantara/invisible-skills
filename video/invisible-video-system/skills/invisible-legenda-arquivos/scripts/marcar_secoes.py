#!/usr/bin/env python3
"""marcar_secoes.py — marca cada palavra do JSON de legenda com a seção do roteiro.

Quando existe um sidecar `<video>.md` ao lado (gancho + desenvolvimento + texto,
gerado pelo desmembrador/combinador), este módulo descobre QUANDO cada seção
começa no vídeo e taggeia as palavras do JSON do WhisperX com `"secao"`.

Como acha o tempo: casa a 1ª frase de cada seção (texto do MD) contra a
transcrição por similaridade fuzzy — a mesma técnica de achar_bordas.py do
desmembrador. NÃO usa offsets gravados na combinação: o vídeo pode ter sido
editado depois, então o tempo é sempre medido sobre a transcrição do vídeo
atual. Robusto a corte/edição entre combinar e legendar.

Pode rodar como módulo (importar `marcar_secoes_no_json`) ou standalone:
    python3 marcar_secoes.py <legenda.json> <roteiro.md>
"""
import argparse
import json
import re
import sys
from difflib import SequenceMatcher


# --- casamento fuzzy (espelha achar_bordas.py do desmembrador) ---------------

def normalizar(palavra):
    p = palavra.lower()
    p = re.sub(r"[^\wáéíóúâêôãõàç]+", "", p, flags=re.UNICODE)
    return p


def palavras_transcricao(data):
    """Achata segments[].words[] numa lista [(word_norm, start, end)]."""
    out = []
    for seg in data.get("segments", []):
        for w in seg.get("words", []):
            txt = normalizar(w.get("word", ""))
            if not txt:
                continue
            start = w.get("start")
            end = w.get("end")
            if start is None or end is None:
                continue
            out.append((txt, float(start), float(end)))
    return out


def tokens_ancora(frase):
    return [normalizar(t) for t in frase.split() if normalizar(t)]


def achar_ocorrencias(palavras, ancora, limiar=0.6):
    """Janelas da transcrição que casam a âncora. [(idx_ini, idx_fim, score)]."""
    seq_t = [p[0] for p in palavras]
    n = len(ancora)
    if n == 0 or not seq_t:
        return []
    alvo = " ".join(ancora)
    ocorrencias = []
    larguras = {max(1, n - 2), n - 1, n, n + 1, n + 2}
    i = 0
    while i < len(seq_t):
        melhor_local = None
        for w in larguras:
            j = i + w
            if j > len(seq_t):
                continue
            janela = " ".join(seq_t[i:j])
            score = SequenceMatcher(None, alvo, janela).ratio()
            if melhor_local is None or score > melhor_local[2]:
                melhor_local = (i, j - 1, score)
        if melhor_local and melhor_local[2] >= limiar:
            ocorrencias.append(melhor_local)
        i += 1
    ocorrencias.sort(key=lambda x: (x[0], -x[2]))
    colapsadas = []
    for occ in ocorrencias:
        if colapsadas and occ[0] <= colapsadas[-1][1]:
            if occ[2] > colapsadas[-1][2]:
                colapsadas[-1] = occ
        else:
            colapsadas.append(occ)
    return colapsadas


# --- parse do sidecar .md ----------------------------------------------------

RE_HEADER = re.compile(r"^#{1,6}\s+(.+?)\s*$")


def parse_md_secoes(md_path):
    """Lê o sidecar e devolve [(nome, texto)] na ordem. Headers `# SEÇÃO`."""
    with open(md_path, encoding="utf-8") as f:
        linhas = f.readlines()
    secoes, atual = [], None
    for linha in linhas:
        m = RE_HEADER.match(linha)
        if m:
            atual = {"nome": m.group(1).strip(), "corpo": []}
            secoes.append(atual)
        elif atual is not None:
            atual["corpo"].append(linha)
    out = []
    for s in secoes:
        texto = re.sub(r"\s+", " ", "".join(s["corpo"])).strip()
        if texto:
            out.append((s["nome"], texto))
    return out


def primeira_frase(texto):
    partes = re.split(r"(?<=[.!?…])\s+", texto.strip())
    return partes[0] if partes else texto


# --- marcação ----------------------------------------------------------------

def marcar_secoes_no_json(data, md_path, limiar=0.6):
    """Anota `secao` em cada word/segment do `data` (JSON WhisperX). In-place.

    Retorna um dict de relatório. Se nada casa, deixa o JSON intacto."""
    secoes = parse_md_secoes(md_path)
    if not secoes:
        return {"marcado": False, "motivo": "md sem seções"}
    palavras = palavras_transcricao(data)
    if not palavras:
        return {"marcado": False, "motivo": "transcrição sem palavras com timestamp"}

    # acha o start de cada seção pela 1ª frase (melhor ocorrência)
    achados = []
    nao_casaram = []
    for nome, texto in secoes:
        occ = achar_ocorrencias(palavras, tokens_ancora(primeira_frase(texto)), limiar)
        if occ:
            melhor = max(occ, key=lambda o: o[2])
            achados.append((nome, palavras[melhor[0]][1], round(melhor[2], 3)))
        else:
            nao_casaram.append(nome)
    if not achados:
        return {"marcado": False, "motivo": "nenhuma âncora casou", "secoes_md": [n for n, _ in secoes]}

    # fronteiras sequenciais: a 1ª cobre desde 0; cada uma vai até o início da próxima
    achados.sort(key=lambda e: e[1])
    fronteiras = []
    for idx, (nome, start, score) in enumerate(achados):
        ini = 0.0 if idx == 0 else start
        fim = achados[idx + 1][1] if idx + 1 < len(achados) else None
        fronteiras.append((nome, ini, fim))

    def secao_de(t):
        for nome, ini, fim in fronteiras:
            if t >= ini and (fim is None or t < fim):
                return nome.lower()
        return fronteiras[-1][0].lower()

    for seg in data.get("segments", []):
        st = seg.get("start")
        if st is not None:
            seg["secao"] = secao_de(float(st))
        for w in seg.get("words", []):
            wt = w.get("start")
            if wt is not None:
                w["secao"] = secao_de(float(wt))
    for w in data.get("word_segments", []):
        wt = w.get("start")
        if wt is not None:
            w["secao"] = secao_de(float(wt))

    data["secoes"] = [
        {"nome": n.lower(), "start": round(ini, 3),
         "end": (round(fim, 3) if fim is not None else None)}
        for n, ini, fim in fronteiras
    ]
    rel = {"marcado": True, "secoes": [n.lower() for n, _, _ in fronteiras]}
    if nao_casaram:
        rel["nao_casaram"] = nao_casaram
    return rel


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("json_legenda")
    ap.add_argument("roteiro_md")
    ap.add_argument("--limiar", type=float, default=0.6)
    args = ap.parse_args()
    with open(args.json_legenda, encoding="utf-8") as f:
        data = json.load(f)
    rel = marcar_secoes_no_json(data, args.roteiro_md, args.limiar)
    if rel.get("marcado"):
        with open(args.json_legenda, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
    print(json.dumps(rel, ensure_ascii=False))


if __name__ == "__main__":
    main()
