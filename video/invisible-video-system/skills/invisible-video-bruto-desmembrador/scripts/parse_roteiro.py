#!/usr/bin/env python3
"""parse_roteiro.py — extrai seções e frases-âncora de um roteiro .md/.txt.

Detecta headers de seção: linha isolada, em [COLCHETES] e/ou **negrito**,
texto majoritariamente MAIÚSCULO. NÃO confunde com marcação de palco
(colchetes no meio de parágrafo, ex. "[o professor lê em voz alta]").

Para cada seção extrai:
    - nome (singular, do header)
    - plural (nome da pasta de saída)
    - ancora_inicio (primeira frase de conteúdo da seção)
    - ancora_fim (última frase de conteúdo antes do próximo header)

Uso:
    python3 parse_roteiro.py <arquivo_roteiro>

Saída (stdout): JSON {"secoes": [{nome, plural, ancora_inicio, ancora_fim}]}
"""
import argparse
import json
import re
import sys

# Header: linha isolada, possivelmente com **negrito** e/ou [colchetes],
# cujo TEXTO é curto e majoritariamente maiúsculo.
RE_NEGRITO = re.compile(r"^\s*\*\*(.+?)\*\*\s*$")
RE_COLCHETE_LINHA = re.compile(r"^\s*\[(.+?)\]\s*$")
RE_MD_HEADER = re.compile(r"^\s*#{1,6}\s+(.+?)\s*$")

# Plurais conhecidos; fallback heurístico no fim.
PLURAIS = {
    "GANCHO": "GANCHOS",
    "DESENVOLVIMENTO": "DESENVOLVIMENTOS",
    "CTA": "CTAS",
    "FECHAMENTO": "FECHAMENTOS",
    "ABERTURA": "ABERTURAS",
    "INTRO": "INTROS",
    "INTRODUCAO": "INTRODUCOES",
    "CONCLUSAO": "CONCLUSOES",
    "PROVA": "PROVAS",
    "OFERTA": "OFERTAS",
    "BONUS": "BONUS",
}


def desescapar_md(texto):
    """Remove escapes de markdown (\\[ \\] \\! \\* etc.) deixando o texto limpo."""
    return re.sub(r"\\([\[\]!*_().#+\-])", r"\1", texto)


def pluralizar(nome):
    n = nome.upper().strip()
    if n in PLURAIS:
        return PLURAIS[n]
    # heurística simples PT-BR
    if n.endswith("ÃO"):
        return n[:-2] + "ÕES"
    if n.endswith("AO"):
        return n[:-2] + "OES"
    if n.endswith(("R", "S", "Z")):
        return n + "ES"
    if n.endswith("L"):
        return n[:-1] + "IS"
    return n + "S"


def eh_header(linha):
    """Retorna o texto do header se a linha for um header de seção, senão None."""
    txt = desescapar_md(linha).strip()
    if not txt:
        return None
    # linha só de marcação (ex.: "**" ou "****") não é header
    if not re.search(r"[A-Za-zÀ-ÿ]", txt):
        return None

    candidato = None
    marcado = False  # veio com marcação explícita (md header, negrito, colchete)?
    m = RE_MD_HEADER.match(txt)
    if m:
        candidato = m.group(1).strip(); marcado = True
    if candidato is None:
        m = RE_NEGRITO.match(txt)
        if m:
            candidato = m.group(1).strip(); marcado = True
    if candidato is None:
        m = RE_COLCHETE_LINHA.match(txt)
        if m:
            candidato = m.group(1).strip(); marcado = True
    if candidato is None:
        # linha curta isolada terminada em ":" (ex.: "GANCHO:") — header sem marcação
        m = re.match(r"^(.{1,30}?):\s*$", txt)
        if m:
            candidato = m.group(1).strip()
    if candidato is None:
        # linha isolada que é exatamente uma keyword de seção conhecida (ex.: "Desenvolvimento")
        if txt.strip("[]*: ").strip().upper() in PLURAIS:
            candidato = txt.strip("[]*: ").strip()

    if candidato is None:
        return None

    # tira colchetes/negrito/dois-pontos internos do candidato
    candidato = candidato.strip("[]*: ").strip()
    if not candidato:
        return None

    letras = [c for c in candidato if c.isalpha()]
    if not letras:
        return None
    if len(candidato) > 40:
        return None

    base = candidato.upper()
    # keyword de seção conhecida vale como header mesmo sem MAIÚSCULAS nem marcação
    if base in PLURAIS:
        return base

    # senão, exige curto + majoritariamente MAIÚSCULO; sem marcação, no máx. 2 palavras
    maiusc = sum(1 for c in letras if c.isupper())
    if maiusc / len(letras) < 0.7:
        return None
    if not marcado and len(candidato.split()) > 2:
        return None
    return base


def limpar_palco(texto):
    """Remove marcação de palco entre colchetes (ex.: [cortar aqui]) e ênfase markdown."""
    t = desescapar_md(texto)
    t = re.sub(r"\[[^\]]*\]", "", t)   # marcação de palco
    t = re.sub(r"[*_`]+", "", t)        # ênfase markdown residual
    return t.strip()


def frases(bloco):
    """Quebra um bloco de texto em frases, limpando marcação de palco."""
    bloco = limpar_palco(bloco)
    # normaliza espaços
    bloco = re.sub(r"\s+", " ", bloco).strip()
    if not bloco:
        return []
    # quebra em sentenças por pontuação forte mantendo conteúdo
    partes = re.split(r"(?<=[.!?…])\s+", bloco)
    return [p.strip() for p in partes if p.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("roteiro")
    args = ap.parse_args()

    try:
        with open(args.roteiro, encoding="utf-8") as f:
            linhas = f.readlines()
    except OSError as e:
        print(json.dumps({"erro": str(e)}))
        sys.exit(1)

    # particiona em seções por header
    secoes = []
    atual = None
    for linha in linhas:
        h = eh_header(linha)
        if h is not None:
            atual = {"nome": h, "corpo": []}
            secoes.append(atual)
        elif atual is not None:
            atual["corpo"].append(linha)

    saida = []
    for s in secoes:
        corpo = "".join(s["corpo"])
        fs = frases(corpo)
        if not fs:
            # seção sem conteúdo textual; ignora (pode ser header decorativo)
            continue
        saida.append({
            "nome": s["nome"],
            "plural": pluralizar(s["nome"]),
            "ancora_inicio": fs[0],
            "ancora_fim": fs[-1],
            "n_frases": len(fs),
        })

    print(json.dumps({"secoes": saida}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
