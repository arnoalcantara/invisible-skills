#!/usr/bin/env python3
"""Bootstrap da invisible-trilha-aplicador.

A skill é ffmpeg puro — a única dependência é o ffmpeg/ffprobe (medição de
loudness via ebur128, mix e reencode do áudio). Sem Node, sem WhisperX.

Uso:
    python3 scripts/bootstrap.py --check-only   # só relata o estado (JSON)
    python3 scripts/bootstrap.py                # tenta instalar via Homebrew
"""
import json
import shutil
import subprocess
import sys


def have(bin_name: str) -> bool:
    return shutil.which(bin_name) is not None


def main() -> int:
    check_only = "--check-only" in sys.argv
    estado = {"ffmpeg": have("ffmpeg"), "ffprobe": have("ffprobe")}

    if not check_only and not (estado["ffmpeg"] and estado["ffprobe"]):
        if have("brew"):
            subprocess.run(["brew", "install", "ffmpeg"], check=False)
            estado = {"ffmpeg": have("ffmpeg"), "ffprobe": have("ffprobe")}

    estado["pronto"] = estado["ffmpeg"] and estado["ffprobe"]
    if not estado["pronto"]:
        estado["dica"] = "Instale o ffmpeg: brew install ffmpeg"
    print(json.dumps(estado, ensure_ascii=False, indent=2))
    return 0 if estado["pronto"] else 1


if __name__ == "__main__":
    sys.exit(main())
