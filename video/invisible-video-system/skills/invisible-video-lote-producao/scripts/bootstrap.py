#!/usr/bin/env python3
"""Bootstrap da invisible-video-lote-producao.

O executor é um MAESTRO: ele não processa mídia, ele invoca as skills da esteira.
Então o bootstrap confere duas coisas:

  1. Que as skills-irmãs da esteira estão acessíveis (mesma pasta `skills/` deste
     executor) — é delas que sairão os comandos `python3 .../scripts/...`.
  2. Que as ferramentas de base existem: ffmpeg/ffprobe (todas as etapas) e um aviso
     se faltar Node (Remotion: legenda e gancho-escrito) ou WhisperX (transcrição).
     Cada skill-irmã tem seu próprio bootstrap que instala o que faltar; aqui só
     relatamos, para o maestro avisar o usuário cedo.

A pasta das skills-irmãs é descoberta a partir da localização DESTE script (sobe até
`skills/`), sem cravar versão de cache — assim o executor acha as irmãs na mesma
versão dele, seja no repo ou no cache de plugins.

Uso:
    python3 scripts/bootstrap.py --check-only
    python3 scripts/bootstrap.py
Saída (stdout): JSON com o estado.
"""
from __future__ import annotations

import json
import os
import shutil
import sys

# skills-irmãs que o maestro invoca, na ordem da esteira
IRMAS = [
    "invisible-video-otimizador",
    "invisible-denoiser",
    "invisible-legenda-arquivos",
    "invisible-legendas-aplicador",
    "invisible-video-var-gancho-escrito",
    "invisible-video-combinador",
    "invisible-trilha-aplicador",
    "invisible-video-acelerador",
]


def skills_dir() -> str:
    """Pasta `skills/` que contém este executor (e as irmãs)."""
    aqui = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # .../skills/<esta-skill>
    return os.path.dirname(aqui)  # .../skills


def main() -> int:
    sdir = skills_dir()
    irmas_ok = {nome: os.path.isdir(os.path.join(sdir, nome)) for nome in IRMAS}

    estado: dict = {
        "skills_dir": sdir,
        "irmas": irmas_ok,
        "todas_irmas": all(irmas_ok.values()),
        "ffmpeg": shutil.which("ffmpeg") is not None,
        "ffprobe": shutil.which("ffprobe") is not None,
        "node": shutil.which("node") is not None,
        "npm": shutil.which("npm") is not None,
    }

    avisos = []
    faltando = [n for n, ok in irmas_ok.items() if not ok]
    if faltando:
        avisos.append(f"skills-irmãs não encontradas em {sdir}: {', '.join(faltando)}")
    if not (estado["ffmpeg"] and estado["ffprobe"]):
        avisos.append("ffmpeg/ffprobe ausente — brew install ffmpeg")
    if not (estado["node"] and estado["npm"]):
        avisos.append("Node/npm ausente (legenda e gancho-escrito usam Remotion) — brew install node")
    # WhisperX vive numa venv própria da legenda-arquivos; não checamos aqui (o
    # bootstrap da legenda-arquivos cuida disso). Só registramos a expectativa.

    estado["avisos"] = avisos
    estado["pronto"] = estado["todas_irmas"] and estado["ffmpeg"] and estado["ffprobe"]
    print(json.dumps(estado, ensure_ascii=False, indent=2))
    return 0 if estado["pronto"] else 1


if __name__ == "__main__":
    sys.exit(main())
