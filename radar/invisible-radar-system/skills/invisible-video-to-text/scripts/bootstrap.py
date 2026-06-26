#!/usr/bin/env python3
"""bootstrap.py — detecta e instala dependências (ffmpeg, uv, yt-dlp, WhisperX).

Idempotente e econômico: instala UMA vez, nunca rebaixa.

WhisperX é pesado (torch + numpy = vários GB) e o yt-dlp também é melhor isolado.
Por isso NÃO se instala um venv por projeto — usa-se o que já estiver no sistema,
ou um venv CENTRAL único (~/.invisible-radar/venv por padrão) reusado por todas as
skills do radar. Ordem de resolução, para CADA ferramenta (yt-dlp, whisperx):

  1. no PATH do sistema  → usa direto, não instala nada.
  2. no venv central     → usa, não instala nada.
  3. nenhum dos dois     → cria o venv central UMA vez (Python 3.12) e instala lá.

Python 3.12 é forçado de propósito: o 3.14 (default recente do Homebrew) não tem
wheel binário de numpy e tenta compilar do zero, esbarrando nos headers do Xcode
CLT. O uv baixa o 3.12 sozinho se não houver.

O modelo de transcrição (large-v3) NÃO é baixado aqui — o WhisperX o baixa na 1ª
transcrição SE não estiver no cache do Hugging Face. Este bootstrap detecta se já
está em cache e reporta `modelo_pronto`, para não prometer download de 1.5GB à toa.

Uso:
    python3 bootstrap.py [--venv <dir>] [--model large-v3] [--python 3.12] [--check-only]

Saída (stdout): JSON com o estado de cada dependência, os caminhos dos binários a
usar (yt_dlp_bin, whisperx_bin) e o que foi feito.
"""
import argparse
import json
import os
import shutil
import subprocess

VENV_CENTRAL_PADRAO = os.path.expanduser("~/.invisible-radar/venv")


def existe(bin_):
    return shutil.which(bin_) is not None


def venv_python(venv):
    return os.path.join(venv, "bin", "python")


def bin_no_venv(venv, nome):
    return os.path.join(venv, "bin", nome)


def resolver(venv, nome):
    """Acha o binário `nome` a usar, sem instalar. Retorna (caminho|None, origem)."""
    no_path = shutil.which(nome)
    if no_path:
        return no_path, "sistema"
    cand = bin_no_venv(venv, nome)
    if os.path.exists(cand):
        return cand, "venv"
    return None, "ausente"


def hf_cache_dir():
    for var in ("HF_HUB_CACHE", "HUGGINGFACE_HUB_CACHE"):
        if os.environ.get(var):
            return os.environ[var]
    home = os.environ.get("HF_HOME")
    if home:
        return os.path.join(home, "hub")
    return os.path.expanduser("~/.cache/huggingface/hub")


def modelo_em_cache(model):
    """Detecta se o modelo de transcrição do WhisperX já está baixado."""
    cache = hf_cache_dir()
    alvo_asr = f"models--Systran--faster-whisper-{model}"
    asr = os.path.isdir(os.path.join(cache, alvo_asr))
    align = any(
        os.path.isdir(os.path.join(cache, d))
        for d in (os.listdir(cache) if os.path.isdir(cache) else [])
        if "wav2vec2" in d.lower() and ("portuguese" in d.lower() or "voxpopuli" in d.lower())
    )
    return {"cache_dir": cache, "asr": asr, "alinhamento_pt": align,
            "nome_esperado": alvo_asr}


def garantir_venv(venv, python, estado, motivo):
    """Cria o venv central se ainda não existir. Registra ação/erro no estado."""
    if os.path.exists(venv_python(venv)):
        return True
    if not estado["uv"]:
        estado["instrucoes"].append(
            f"Sem uv, não dá pra criar o venv ({motivo}). "
            "Instale: curl -LsSf https://astral.sh/uv/install.sh | sh")
        return False
    os.makedirs(os.path.dirname(venv), exist_ok=True)
    r = subprocess.run(["uv", "venv", "--python", python, venv],
                       capture_output=True, text=True)
    estado["acoes"].append(f"uv venv --python {python} {venv} ({motivo})")
    if r.returncode != 0:
        estado["instrucoes"].append("Falha ao criar venv: " + r.stderr[-800:])
        return False
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--venv", default=VENV_CENTRAL_PADRAO,
                    help="local do venv CENTRAL (padrão ~/.invisible-radar/venv)")
    ap.add_argument("--model", default="large-v3")
    ap.add_argument("--python", default="3.12",
                    help="versão de Python para o venv (3.14 quebra numpy)")
    ap.add_argument("--check-only", action="store_true")
    args = ap.parse_args()

    venv = os.path.abspath(os.path.expanduser(args.venv))
    ytdlp_bin, ytdlp_origem = resolver(venv, "yt-dlp")
    wx_bin, wx_origem = resolver(venv, "whisperx")
    modelo = modelo_em_cache(args.model)

    estado = {
        "ffmpeg": existe("ffmpeg"),
        "ffprobe": existe("ffprobe"),
        "uv": existe("uv"),
        "yt_dlp": ytdlp_bin is not None,
        "yt_dlp_bin": ytdlp_bin,
        "yt_dlp_origem": ytdlp_origem,        # sistema | venv | ausente
        "whisperx": wx_bin is not None,
        "whisperx_bin": wx_bin,
        "whisperx_origem": wx_origem,         # sistema | venv | ausente
        "venv_central": venv,
        "modelo": modelo,
        "modelo_pronto": modelo["asr"] and modelo["alinhamento_pt"],
        "acoes": [],
        "instrucoes": [],
    }
    estado["pronto"] = (estado["ffmpeg"] and estado["ffprobe"]
                        and estado["yt_dlp"] and estado["whisperx"])

    if not modelo["asr"]:
        estado["instrucoes"].append(
            f"O modelo {args.model} NÃO está no cache HF ({modelo['cache_dir']}). "
            "A 1ª transcrição vai baixá-lo (~1.5GB) — avise o usuário.")
    if not modelo["alinhamento_pt"]:
        estado["instrucoes"].append(
            "O modelo de alinhamento PT (wav2vec2) pode ser baixado na 1ª "
            "transcrição. Com --no_align (padrão desta skill) ele nem é usado.")

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

    if not estado["uv"]:
        estado["instrucoes"].append(
            "uv não encontrado. Instale: curl -LsSf https://astral.sh/uv/install.sh | sh")

    # yt-dlp: instala no venv central se faltar (leve).
    if not estado["yt_dlp"]:
        if garantir_venv(venv, args.python, estado, "p/ yt-dlp"):
            r = subprocess.run(
                ["uv", "pip", "install", "--python", venv_python(venv), "yt-dlp"],
                capture_output=True, text=True)
            estado["acoes"].append("uv pip install yt-dlp (venv central)")
            if r.returncode != 0:
                estado["instrucoes"].append("Falha ao instalar yt-dlp: " + r.stderr[-800:])
            ytdlp_bin, ytdlp_origem = resolver(venv, "yt-dlp")
            estado["yt_dlp"] = ytdlp_bin is not None
            estado["yt_dlp_bin"] = ytdlp_bin
            estado["yt_dlp_origem"] = ytdlp_origem

    # WhisperX: só instala se não existir no sistema NEM no venv central (pesado).
    if not estado["whisperx"]:
        if garantir_venv(venv, args.python, estado, "p/ whisperx"):
            r = subprocess.run(
                ["uv", "pip", "install", "--python", venv_python(venv), "whisperx"],
                capture_output=True, text=True)
            estado["acoes"].append("uv pip install whisperx (venv central)")
            if r.returncode != 0:
                estado["instrucoes"].append("Falha ao instalar whisperx: " + r.stderr[-800:])
            wx_bin, wx_origem = resolver(venv, "whisperx")
            estado["whisperx"] = wx_bin is not None
            estado["whisperx_bin"] = wx_bin
            estado["whisperx_origem"] = wx_origem

    estado["pronto"] = (estado["ffmpeg"] and estado["ffprobe"]
                        and estado["yt_dlp"] and estado["whisperx"])
    print(json.dumps(estado, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
