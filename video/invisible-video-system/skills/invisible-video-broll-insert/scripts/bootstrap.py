#!/usr/bin/env python3
"""Bootstrap da invisible-video-broll-insert.

O MOTOR DE INSERÇÃO (inserir.py) é ffmpeg puro — roda em qualquer máquina.
A GERAÇÃO dos B-rolls depende do MCP Artlist, que só existe em sessão conectada;
o bootstrap não consegue checá-lo (é um conector da sessão do Claude, não um binário),
então apenas AVISA que ele é necessário para a etapa de geração.

Uso:
    python3 scripts/bootstrap.py --check-only   # relata o estado (JSON)
    python3 scripts/bootstrap.py                # tenta instalar ffmpeg via Homebrew
"""
import json
import shutil
import subprocess
import sys


def have(b):
    return shutil.which(b) is not None


def main():
    check_only = "--check-only" in sys.argv
    estado = {"ffmpeg": have("ffmpeg"), "ffprobe": have("ffprobe")}

    if not check_only and not (estado["ffmpeg"] and estado["ffprobe"]):
        if have("brew"):
            subprocess.run(["brew", "install", "ffmpeg"], check=False)
            estado = {"ffmpeg": have("ffmpeg"), "ffprobe": have("ffprobe")}

    estado["pronto_insercao"] = estado["ffmpeg"] and estado["ffprobe"]
    estado["nota_artlist"] = (
        "A geração de B-roll usa o MCP Artlist (imagem Nano Banana 2 + animação "
        "Seedance i2v), que só existe em sessão Claude conectada ao Artlist. "
        "A INSERÇÃO (inserir.py) roda sem ele; a GERAÇÃO não."
    )
    if not estado["pronto_insercao"]:
        estado["dica"] = "Instale o ffmpeg: brew install ffmpeg"
    print(json.dumps(estado, ensure_ascii=False, indent=2))
    return 0 if estado["pronto_insercao"] else 1


if __name__ == "__main__":
    sys.exit(main())
