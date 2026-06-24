#!/usr/bin/env python3
"""Bootstrap da invisible-video-lote-plano.

Esta skill só conversa e cria pastas + o PLAN_LOTE.md — não processa mídia.
A única dependência real é o próprio python3 (já garantido por estar rodando).
O bootstrap serve para um sanity-check honesto: confirma o python3 e, se a raiz
do laboratório for passada, que ela existe, tem a pasta de trilhas padrão
(00_Recursos/Trilhas) e LISTA as pastas de trilha disponíveis dentro dela — pra
o planejador oferecer ao usuário, com a raiz de trilhas como default.

A PRODUÇÃO de fato (ffmpeg, WhisperX, Node/Remotion) é responsabilidade das
skills da esteira, checada pela invisible-video-lote-producao, não aqui.

Uso:
    python3 scripts/bootstrap.py --check-only
    python3 scripts/bootstrap.py --raiz "<raiz do laboratório>"
"""
from __future__ import annotations

import argparse
import json
import os
import sys

TRILHAS_REL = os.path.join("00_Recursos", "Trilhas")
AUDIO_EXT = {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg", ".aif", ".aiff"}


def conta_audios(pasta: str) -> int:
    try:
        return sum(
            1 for n in os.listdir(pasta)
            if not n.startswith(".")
            and os.path.splitext(n)[1].lower() in AUDIO_EXT
            and os.path.isfile(os.path.join(pasta, n))
        )
    except OSError:
        return 0


def listar_trilhas(raiz_trilhas: str) -> dict:
    """Mapeia a biblioteca de trilhas pra o planejador mostrar ao usuário: a
    própria raiz (com nº de áudios soltos) e cada subpasta (com nº de áudios).

    Suporta os dois layouts — áudios soltos na raiz e/ou subpastas por
    humor/projeto. O `rel` de cada opção é relativo à raiz do laboratório (é o
    que vai no PLAN_LOTE.md e no --trilhas da produção)."""
    info: dict = {"existe": os.path.isdir(raiz_trilhas), "padrao_rel": TRILHAS_REL}
    if not info["existe"]:
        return info
    info["audios_na_raiz"] = conta_audios(raiz_trilhas)
    subpastas = []
    for nome in sorted(os.listdir(raiz_trilhas)):
        p = os.path.join(raiz_trilhas, nome)
        if os.path.isdir(p) and not nome.startswith("."):
            subpastas.append({
                "nome": nome,
                "rel": os.path.join(TRILHAS_REL, nome),
                "audios": conta_audios(p),
            })
    info["subpastas"] = subpastas
    return info


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raiz", help="raiz do laboratório (opcional, para checar/listar trilhas)")
    ap.add_argument("--check-only", action="store_true")
    args = ap.parse_args()

    estado: dict = {"python3": True}
    if args.raiz:
        estado["raiz_existe"] = os.path.isdir(args.raiz)
        raiz_trilhas = os.path.join(args.raiz, TRILHAS_REL)
        # a pasta-raiz de trilhas (00_Recursos/Trilhas) é a PADRÃO; o planejador
        # lista as pastas disponíveis dentro dela pro usuário escolher.
        estado["trilhas"] = listar_trilhas(raiz_trilhas)
        if not estado["trilhas"]["existe"]:
            estado["dica"] = (
                f"Pasta de trilha padrão ({TRILHAS_REL}) não encontrada — "
                "o planejador vai perguntar qual pasta usar."
            )

    estado["pronto"] = True  # o planejador roda só com python3
    print(json.dumps(estado, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
