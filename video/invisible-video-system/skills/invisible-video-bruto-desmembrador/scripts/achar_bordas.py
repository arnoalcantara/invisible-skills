#!/usr/bin/env python3
"""achar_bordas.py — casa roteiro × transcrição × silêncio → timestamps por seção.

O coração do método (ver referencia/METODO.md):

1. Localiza as âncoras (início e fim) na transcrição por SIMILARIDADE fuzzy —
   o falado != roteiro (o professor improvisa). Casa a sequência de palavras da
   âncora contra a sequência de palavras transcritas, achando a janela de melhor
   score.
2. Desambigua repetições/tomadas: se a âncora de início casa em vários pontos,
   escolhe a ÚLTIMA ocorrência completa da seção. Tomada truncada (início sem
   fim correspondente depois dela) é descartada. Loga quantas tomadas havia.
3. início_fala = start da 1ª palavra da âncora de início;
   fim_fala = end da última palavra da âncora de fim.
4. Refina com silêncio (silencedetect): início recua até a transição
   silêncio→som limpa mais próxima ANTES da âncora; fim avança até a transição
   som→silêncio logo após.
5. Aplica bordas: ss = início_fala - respiro_inicio; to = fim_fala + respiro_fim.
   Clampa a [0, duração].

Uso:
    python3 achar_bordas.py <video> <transcricao.json> <secoes.json> \
        [--respiro-inicio 0.15] [--respiro-fim 0.30] \
        [--silence-noise -30] [--silence-min 0.4]

Saída (stdout): JSON {"duracao", "cortes": [{secao, plural, ss, to, dur, n_tomadas, conf}]}
"""
import argparse
import json
import re
import subprocess
import sys
from difflib import SequenceMatcher


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
    """Acha janelas na transcrição que casam a âncora por similaridade.

    Retorna lista de (idx_inicio, idx_fim, score) ordenada por idx_inicio.
    Usa SequenceMatcher sobre janelas deslizantes do tamanho da âncora (±2).
    """
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
    # colapsa janelas sobrepostas mantendo a de melhor score
    ocorrencias.sort(key=lambda x: (x[0], -x[2]))
    colapsadas = []
    for occ in ocorrencias:
        if colapsadas and occ[0] <= colapsadas[-1][1]:
            if occ[2] > colapsadas[-1][2]:
                colapsadas[-1] = occ
        else:
            colapsadas.append(occ)
    return colapsadas


def silencios(video, noise_db, min_dur):
    """Roda silencedetect e retorna lista de (silence_start, silence_end)."""
    cmd = [
        "ffmpeg", "-i", video,
        "-af", f"silencedetect=noise={noise_db}dB:d={min_dur}",
        "-f", "null", "-",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    txt = proc.stderr
    starts = [float(m) for m in re.findall(r"silence_start:\s*([0-9.]+)", txt)]
    ends = [float(m) for m in re.findall(r"silence_end:\s*([0-9.]+)", txt)]
    # parea em ordem; o último start pode não ter end (silêncio até o fim)
    pares = []
    for k, s in enumerate(starts):
        e = ends[k] if k < len(ends) else None
        pares.append((s, e))
    return pares


def duracao(video):
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration",
           "-of", "default=nw=1:nk=1", video]
    out = subprocess.run(cmd, capture_output=True, text=True).stdout.strip()
    try:
        return float(out)
    except ValueError:
        return None


def refinar_inicio(inicio_fala, sils):
    """Recua para a transição silêncio→som limpa mais próxima antes da âncora.

    Procura o silêncio cujo fim (silence_end = começo da fala) seja o maior
    valor <= inicio_fala. Usa esse silence_end como início limpo da fala.
    """
    melhor = None
    for s, e in sils:
        if e is not None and e <= inicio_fala + 0.05:
            if melhor is None or e > melhor:
                melhor = e
    return melhor if melhor is not None else inicio_fala


def refinar_fim(fim_fala, sils):
    """Avança para a transição som→silêncio logo após a âncora (silence_start)."""
    melhor = None
    for s, e in sils:
        if s >= fim_fala - 0.05:
            if melhor is None or s < melhor:
                melhor = s
    return melhor if melhor is not None else fim_fala


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("transcricao")
    ap.add_argument("secoes")
    ap.add_argument("--respiro-inicio", type=float, default=0.15)
    ap.add_argument("--respiro-fim", type=float, default=0.30)
    ap.add_argument("--silence-noise", type=float, default=-30)
    ap.add_argument("--silence-min", type=float, default=0.4)
    ap.add_argument("--limiar", type=float, default=0.6)
    args = ap.parse_args()

    with open(args.transcricao, encoding="utf-8") as f:
        data = json.load(f)
    with open(args.secoes, encoding="utf-8") as f:
        secoes = json.load(f)["secoes"]

    palavras = palavras_transcricao(data)
    if not palavras:
        print(json.dumps({"erro": "transcrição sem palavras alinhadas"}))
        sys.exit(1)

    dur = duracao(args.video)
    sils = silencios(args.video, args.silence_noise, args.silence_min)

    cortes = []
    for s in secoes:
        a_ini = tokens_ancora(s["ancora_inicio"])
        a_fim = tokens_ancora(s["ancora_fim"])

        occ_ini = achar_ocorrencias(palavras, a_ini, args.limiar)
        occ_fim = achar_ocorrencias(palavras, a_fim, args.limiar)

        n_tomadas = len(occ_ini)
        if not occ_ini or not occ_fim:
            cortes.append({
                "secao": s["nome"], "plural": s["plural"],
                "erro": "âncora não localizada na transcrição",
                "n_tomadas": n_tomadas,
            })
            continue

        # Última tomada completa: para o último início, achar o primeiro fim
        # que venha DEPOIS dele. Se não houver, recua para inícios anteriores.
        escolha = None
        for ini in reversed(occ_ini):
            fins_depois = [f for f in occ_fim if f[0] >= ini[0]]
            if fins_depois:
                fim = min(fins_depois, key=lambda f: f[0])
                escolha = (ini, fim)
                break
        if escolha is None:
            cortes.append({
                "secao": s["nome"], "plural": s["plural"],
                "erro": "nenhuma tomada completa (início sem fim posterior)",
                "n_tomadas": n_tomadas,
            })
            continue

        ini, fim = escolha
        inicio_fala = palavras[ini[0]][1]   # start da 1ª palavra da âncora início
        fim_fala = palavras[fim[1]][2]       # end da última palavra da âncora fim

        inicio_fala = refinar_inicio(inicio_fala, sils)
        fim_fala = refinar_fim(fim_fala, sils)

        ss = max(0.0, inicio_fala - args.respiro_inicio)
        to = fim_fala + args.respiro_fim
        if dur is not None:
            to = min(to, dur)

        conf = round((ini[2] + fim[2]) / 2, 3)
        cortes.append({
            "secao": s["nome"], "plural": s["plural"],
            "ss": round(ss, 3), "to": round(to, 3), "dur": round(to - ss, 3),
            "n_tomadas": n_tomadas, "conf": conf,
        })

    print(json.dumps({"duracao": dur, "cortes": cortes}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
