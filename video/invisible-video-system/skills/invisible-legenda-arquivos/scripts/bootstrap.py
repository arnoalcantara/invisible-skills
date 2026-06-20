#!/usr/bin/env python3
"""bootstrap.py — detecta e instala dependências (ffmpeg, uv, WhisperX).

Idempotente e econômico: instala UMA vez, nunca rebaixa.

WhisperX é pesado (torch + numpy = vários GB). Por isso NÃO se instala um venv
por projeto — usa-se um WhisperX já no sistema, ou um venv CENTRAL único
(~/.invisible-video/wxenv por padrão) reusado por todos os projetos. A ordem de
resolução é:

  1. whisperx no PATH do sistema  → usa direto, não instala nada.
  2. venv central já existe       → usa, não instala nada.
  3. nenhum dos dois              → cria o venv central UMA vez (Python 3.12) e
                                     instala o whisperx. Da próxima, cai no caso 2.

Python 3.12 é forçado de propósito: o 3.14 (default recente do Homebrew) não tem
wheel binário de numpy e tenta compilar do zero, esbarrando nos headers do Xcode
CLT. O uv baixa o 3.12 sozinho se não houver.

O modelo (large-v3) NÃO é baixado aqui — o WhisperX o baixa na 1ª transcrição SE
não estiver no cache do Hugging Face. Este bootstrap detecta se o modelo já está
em cache e reporta `modelo_pronto`, para não prometer download de 1.5GB à toa.

Uso:
    python3 bootstrap.py [--venv <dir>] [--model large-v3] [--python 3.12] [--check-only]

`--venv` sobrescreve o local central (padrão ~/.invisible-video/wxenv). NUNCA
aponte para dentro da pasta do projeto — o objetivo é justamente não duplicar GB.

Saída (stdout): JSON com o estado de cada dependência, o whisperx_bin a usar e o
que foi feito.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys

VENV_CENTRAL_PADRAO = os.path.expanduser("~/.invisible-video/wxenv")


def existe(bin_):
    return shutil.which(bin_) is not None


def whisperx_no_venv(venv):
    return os.path.exists(os.path.join(venv, "bin", "whisperx"))


def resolver_whisperx(venv):
    """Acha o whisperx a usar, sem instalar nada.

    Retorna (caminho_do_bin | None, origem) onde origem ∈ {sistema, venv, ausente}.
    """
    no_path = shutil.which("whisperx")
    if no_path:
        return no_path, "sistema"
    if whisperx_no_venv(venv):
        return os.path.join(venv, "bin", "whisperx"), "venv"
    return None, "ausente"


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
    align = any(
        os.path.isdir(os.path.join(cache, d))
        for d in (os.listdir(cache) if os.path.isdir(cache) else [])
        if "wav2vec2" in d.lower() and ("portuguese" in d.lower() or "voxpopuli" in d.lower())
    )
    return {"cache_dir": cache, "asr": asr, "alinhamento_pt": align,
            "nome_esperado": alvo_asr}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--venv", default=VENV_CENTRAL_PADRAO,
                    help="local do venv CENTRAL (padrão ~/.invisible-video/wxenv)")
    ap.add_argument("--model", default="large-v3")
    ap.add_argument("--python", default="3.12",
                    help="versão de Python para o venv (3.14 quebra numpy)")
    ap.add_argument("--check-only", action="store_true")
    args = ap.parse_args()

    venv = os.path.abspath(os.path.expanduser(args.venv))
    wx_bin, origem = resolver_whisperx(venv)
    modelo = modelo_em_cache(args.model)

    estado = {
        "ffmpeg": existe("ffmpeg"),
        "ffprobe": existe("ffprobe"),
        "uv": existe("uv"),
        "whisperx": wx_bin is not None,
        "whisperx_bin": wx_bin,
        "whisperx_origem": origem,          # sistema | venv | ausente
        "venv_central": venv,
        "modelo": modelo,
        # modelo_pronto = não vai baixar nada na 1ª transcrição.
        "modelo_pronto": modelo["asr"] and modelo["alinhamento_pt"],
        "acoes": [],
        "instrucoes": [],
    }
    estado["pronto"] = estado["ffmpeg"] and estado["ffprobe"] and estado["whisperx"]

    # Aviso de download do modelo só quando faltar de fato.
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

    # WhisperX: só instala se NÃO existir no sistema NEM no venv central.
    if not estado["whisperx"]:
        if estado["uv"]:
            os.makedirs(os.path.dirname(venv), exist_ok=True)
            # Python 3.12 forçado — evita o tropeço do 3.14/numpy.
            r1 = subprocess.run(["uv", "venv", "--python", args.python, venv],
                                capture_output=True, text=True)
            estado["acoes"].append(f"uv venv --python {args.python} {venv}")
            if r1.returncode != 0:
                estado["instrucoes"].append("Falha ao criar venv: " + r1.stderr[-800:])
            r2 = subprocess.run(
                ["uv", "pip", "install", "--python",
                 os.path.join(venv, "bin", "python"), "whisperx"],
                capture_output=True, text=True)
            estado["acoes"].append("uv pip install whisperx (venv central)")
            if r2.returncode != 0:
                estado["instrucoes"].append("Falha ao instalar whisperx: " + r2.stderr[-800:])
            wx_bin, origem = resolver_whisperx(venv)
            estado["whisperx"] = wx_bin is not None
            estado["whisperx_bin"] = wx_bin
            estado["whisperx_origem"] = origem
        else:
            estado["instrucoes"].append(
                f"Sem uv, não dá pra criar o venv. Manual: "
                f"uv venv --python {args.python} {venv} && "
                f"uv pip install --python {venv}/bin/python whisperx")

    estado["pronto"] = estado["ffmpeg"] and estado["ffprobe"] and estado["whisperx"]
    print(json.dumps(estado, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
