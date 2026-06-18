#!/usr/bin/env python3
"""bootstrap.py — detecta e instala dependências (ffmpeg, uv, WhisperX).

Idempotente: não refaz o que já existe. Cria um venv isolado por projeto para
o WhisperX (com uv) e instala o pacote. NÃO baixa o modelo aqui — o modelo
large-v3 é baixado pelo próprio WhisperX na primeira transcrição.

Uso:
    python3 bootstrap.py --venv <.transcricao/.wxenv> [--check-only]

Saída (stdout): JSON com o estado de cada dependência e o que foi feito.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys


def existe(bin_):
    return shutil.which(bin_) is not None


def whisperx_no_venv(venv):
    return os.path.exists(os.path.join(venv, "bin", "whisperx"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--venv", required=True)
    ap.add_argument("--check-only", action="store_true")
    args = ap.parse_args()

    estado = {
        "ffmpeg": existe("ffmpeg"),
        "ffprobe": existe("ffprobe"),
        "uv": existe("uv"),
        "whisperx": whisperx_no_venv(args.venv),
        "acoes": [],
        "instrucoes": [],
    }

    if args.check_only:
        print(json.dumps(estado, ensure_ascii=False, indent=2))
        return

    # ffmpeg/ffprobe via brew
    if not estado["ffmpeg"] or not estado["ffprobe"]:
        if existe("brew"):
            r = subprocess.run(["brew", "install", "ffmpeg"], capture_output=True, text=True)
            estado["acoes"].append("brew install ffmpeg")
            if r.returncode != 0:
                estado["instrucoes"].append("Falha no brew install ffmpeg: " + r.stderr[-500:])
            estado["ffmpeg"] = existe("ffmpeg")
            estado["ffprobe"] = existe("ffprobe")
        else:
            estado["instrucoes"].append("Instale Homebrew e rode: brew install ffmpeg")

    # uv
    if not estado["uv"]:
        estado["instrucoes"].append(
            "uv não encontrado. Instale: curl -LsSf https://astral.sh/uv/install.sh | sh")

    # WhisperX no venv
    if not estado["whisperx"]:
        if estado["uv"]:
            os.makedirs(os.path.dirname(os.path.abspath(args.venv)), exist_ok=True)
            r1 = subprocess.run(["uv", "venv", args.venv], capture_output=True, text=True)
            estado["acoes"].append(f"uv venv {args.venv}")
            r2 = subprocess.run(
                ["uv", "pip", "install", "--python",
                 os.path.join(args.venv, "bin", "python"), "whisperx"],
                capture_output=True, text=True)
            estado["acoes"].append("uv pip install whisperx")
            if r2.returncode != 0:
                estado["instrucoes"].append("Falha ao instalar whisperx: " + r2.stderr[-800:])
            estado["whisperx"] = whisperx_no_venv(args.venv)
        else:
            estado["instrucoes"].append(
                f"Sem uv, não dá pra criar o venv. Manual: uv venv {args.venv} && "
                f"uv pip install --python {args.venv}/bin/python whisperx")

    estado["pronto"] = estado["ffmpeg"] and estado["ffprobe"] and estado["whisperx"]
    print(json.dumps(estado, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
