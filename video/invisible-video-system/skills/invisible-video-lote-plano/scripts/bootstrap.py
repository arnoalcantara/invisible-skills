#!/usr/bin/env python3
"""Bootstrap da invisible-video-lote-plano.

Esta skill só conversa e cria pastas + o PLAN_LOTE.md — não processa mídia.
A única dependência real é o próprio python3 (já garantido por estar rodando).
O bootstrap serve para um sanity-check honesto: confirma o python3 e, se a raiz
do laboratório for passada, que ela existe e tem a pasta de trilhas padrão.

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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raiz", help="raiz do laboratório (opcional, para checar trilhas)")
    ap.add_argument("--check-only", action="store_true")
    args = ap.parse_args()

    estado: dict = {"python3": True}
    if args.raiz:
        estado["raiz_existe"] = os.path.isdir(args.raiz)
        trilhas = os.path.join(args.raiz, "00_Recursos", "Trilhas")
        estado["trilhas_padrao"] = os.path.isdir(trilhas)
        if not estado["trilhas_padrao"]:
            estado["dica"] = (
                "Pasta de trilha padrão (00_Recursos/Trilhas) não encontrada — "
                "o planejador vai perguntar qual pasta usar."
            )

    estado["pronto"] = True  # o planejador roda só com python3
    print(json.dumps(estado, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
