#!/usr/bin/env python3
"""bootstrap.py — detecta e instala dependências (ffmpeg, uv, WhisperX).

Idempotente: não refaz o que já existe. Cria um venv isolado por projeto para
o WhisperX (com uv) e instala o pacote. NÃO baixa o modelo — o WhisperX baixa
o large-v3 na 1ª transcrição SE não estiver em cache. Este bootstrap DETECTA se
o modelo já está no cache do Hugging Face e avisa, para não dar a impressão de
que vai baixar 1.5GB quando o usuário já tem o modelo.

Uso:
    python3 bootstrap.py --venv <.transcricao/.wxenv> [--model large-v3] [--check-only]

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


def hf_cache_dir():
    """Diretório de cache do Hugging Face, respeitando as env vars usuais."""
    for var in ("HF_HUB_CACHE", "HUGGINGFACE_HUB_CACHE"):
        if os.environ.get(var):
            return os.environ[var]
    home = os.environ.get("HF_HOME")
    if home:
        return os.path.join(home, "hub")
    return os.path.expanduser("~/.cache/huggingface/hub")


def modelo_em_cache(model):
    """Detecta se o modelo de transcrição do WhisperX já está baixado.

    WhisperX roda sobre faster-whisper, que guarda o modelo no cache do HF como
    'models--Systran--faster-whisper-<model>'. Confere também o alinhamento PT
    (wav2vec2), que o WhisperX baixa à parte. Retorna dict com o que achou.
    """
    cache = hf_cache_dir()
    alvo_asr = f"models--Systran--faster-whisper-{model}"
    asr = os.path.isdir(os.path.join(cache, alvo_asr))
    # modelo de alinhamento forçado para PT (nome padrão usado pelo WhisperX)
    align = any(
        os.path.isdir(os.path.join(cache, d))
        for d in (os.listdir(cache) if os.path.isdir(cache) else [])
        if "wav2vec2" in d.lower() and ("portuguese" in d.lower() or "voxpopuli" in d.lower())
    )
    return {"cache_dir": cache, "asr": asr, "alinhamento_pt": align,
            "nome_esperado": alvo_asr}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--venv", required=True)
    ap.add_argument("--model", default="large-v3")
    ap.add_argument("--check-only", action="store_true")
    args = ap.parse_args()

    modelo = modelo_em_cache(args.model)
    estado = {
        "ffmpeg": existe("ffmpeg"),
        "ffprobe": existe("ffprobe"),
        "uv": existe("uv"),
        "whisperx": whisperx_no_venv(args.venv),
        "modelo": modelo,
        # modelo_pronto = não vai baixar nada na 1ª transcrição.
        "modelo_pronto": modelo["asr"] and modelo["alinhamento_pt"],
        "acoes": [],
        "instrucoes": [],
    }
    # pronto = dá pra rodar agora (o modelo não bloqueia: WhisperX baixa sozinho).
    estado["pronto"] = estado["ffmpeg"] and estado["ffprobe"] and estado["whisperx"]

    # Aviso explícito sobre download do modelo (1.5GB) só quando faltar de fato.
    if not modelo["asr"]:
        estado["instrucoes"].append(
            f"O modelo {args.model} NÃO está no cache HF ({modelo['cache_dir']}). "
            "A 1ª transcrição vai baixá-lo (~1.5GB) — avise o usuário.")
    if not modelo["alinhamento_pt"]:
        estado["instrucoes"].append(
            "O modelo de alinhamento PT (wav2vec2) não foi detectado no cache; "
            "o WhisperX o baixa na 1ª transcrição (pequeno).")

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

    # recalcula pronto após eventual instalação (ffmpeg/whisperx podem ter mudado).
    estado["pronto"] = estado["ffmpeg"] and estado["ffprobe"] and estado["whisperx"]
    print(json.dumps(estado, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
