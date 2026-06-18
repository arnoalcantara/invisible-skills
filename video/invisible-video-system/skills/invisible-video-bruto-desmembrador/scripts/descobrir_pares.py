#!/usr/bin/env python3
"""descobrir_pares.py — acha pares vídeo+roteiro por prefixo de nome.

Varre a pasta do projeto (e uma subpasta de brutas, ex. BRUTAS/) procurando
vídeos e roteiros, e pareia por prefixo comum de nome, tolerante a sufixos
como ROTEIRO, VERTICAL, BRUTA. Emite JSON com pares e órfãos.

Uso:
    python3 descobrir_pares.py <pasta_projeto> [--brutas-subdir BRUTAS]

Saída (stdout): JSON
    {"pares": [{"prefixo","video","roteiro"}], "orfaos_video": [...], "orfaos_roteiro": [...]}
"""
import argparse
import json
import os
import re
import sys

VIDEO_EXT = {".mp4", ".mov", ".mkv", ".m4v", ".avi", ".webm"}
ROTEIRO_EXT = {".md", ".txt"}

# Sufixos de ruído removidos do nome para achar o prefixo comum.
SUFIXOS_RUIDO = ["ROTEIRO", "VERTICAL", "HORIZONTAL", "BRUTA", "BRUTO", "RAW", "FINAL"]


def normalizar_prefixo(nome_sem_ext):
    """Remove sufixos de ruído e separadores das pontas para isolar o prefixo."""
    s = nome_sem_ext
    # remove sufixos de ruído repetidamente, em qualquer ordem, no fim do nome
    mudou = True
    while mudou:
        mudou = False
        for suf in SUFIXOS_RUIDO:
            # casa o sufixo precedido por separador comum (__ , _, -, espaço) no fim
            padrao = re.compile(r"(?:[_\-\s]|__)*" + re.escape(suf) + r"$", re.IGNORECASE)
            novo = padrao.sub("", s)
            if novo != s:
                s = novo
                mudou = True
    # limpa separadores residuais nas pontas
    s = s.strip("_-. ")
    return s.upper()


def coletar(pasta):
    videos, roteiros = [], []
    for entry in sorted(os.listdir(pasta)):
        caminho = os.path.join(pasta, entry)
        if not os.path.isfile(caminho):
            continue
        if entry.startswith("."):
            continue
        base, ext = os.path.splitext(entry)
        ext = ext.lower()
        if ext in VIDEO_EXT:
            videos.append((caminho, base))
        elif ext in ROTEIRO_EXT:
            roteiros.append((caminho, base))
    return videos, roteiros


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pasta")
    ap.add_argument("--brutas-subdir", default="BRUTAS")
    args = ap.parse_args()

    pasta = os.path.abspath(args.pasta)
    if not os.path.isdir(pasta):
        print(json.dumps({"erro": f"pasta não existe: {pasta}"}))
        sys.exit(1)

    # Vídeos podem estar na subpasta BRUTAS; roteiros normalmente na raiz do projeto.
    # Coletamos vídeos de ambas e roteiros de ambas, sem duplicar.
    videos, roteiros = coletar(pasta)
    sub = os.path.join(pasta, args.brutas_subdir)
    if os.path.isdir(sub):
        v2, r2 = coletar(sub)
        videos += v2
        roteiros += r2

    # indexa roteiros por prefixo normalizado
    idx_roteiro = {}
    for caminho, base in roteiros:
        idx_roteiro.setdefault(normalizar_prefixo(base), []).append(caminho)

    pares = []
    usados_roteiro = set()
    orfaos_video = []
    for caminho, base in videos:
        pref = normalizar_prefixo(base)
        candidatos = idx_roteiro.get(pref, [])
        if candidatos:
            roteiro = candidatos[0]
            usados_roteiro.add(roteiro)
            pares.append({"prefixo": pref, "video": caminho, "roteiro": roteiro})
        else:
            orfaos_video.append(caminho)

    orfaos_roteiro = [c for _, lst in idx_roteiro.items() for c in lst if c not in usados_roteiro]

    print(json.dumps({
        "pares": pares,
        "orfaos_video": orfaos_video,
        "orfaos_roteiro": sorted(orfaos_roteiro),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
