#!/usr/bin/env python3
"""transcrever.py — transcreve a FALA de um vídeo (texto, não timestamp).

Extrai o áudio (ffmpeg, mono 16k) e roda WhisperX em pt com --no_align: aqui não
precisamos de timestamp por palavra (isso é coisa de legenda de vídeo), só do
texto da fala. --no_align deixa mais rápido e dispensa o modelo de alinhamento.

Imprime JSON com o caminho do .txt gerado e o texto bruto. A LIMPEZA do texto
(corrigir erros de reconhecimento preservando o sentido) é feita depois pelo
AGENTE — o script entrega a transcrição crua.

Uso:
    python3 transcrever.py <video> --out-dir <dir> [--whisperx-bin <bin>] [--lang pt]
"""
import argparse
import json
import os
import shutil
import subprocess
import sys


def resolver_whisperx(arg_bin):
    if arg_bin and os.path.exists(arg_bin):
        return arg_bin
    no_path = shutil.which("whisperx")
    if no_path:
        return no_path
    cand = os.path.expanduser("~/.invisible-radar/venv/bin/whisperx")
    if os.path.exists(cand):
        return cand
    # fallback: venv do invisible-video, se o usuário já tiver
    cand2 = os.path.expanduser("~/.invisible-video/wxenv/bin/whisperx")
    if os.path.exists(cand2):
        return cand2
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--whisperx-bin", default=None)
    ap.add_argument("--lang", default="pt")
    ap.add_argument("--model", default="large-v3")
    args = ap.parse_args()

    if not os.path.exists(args.video):
        print(json.dumps({"ok": False, "erro": f"vídeo não encontrado: {args.video}"},
                         ensure_ascii=False))
        sys.exit(1)

    wx = resolver_whisperx(args.whisperx_bin)
    if not wx:
        print(json.dumps({"ok": False, "erro": "whisperx não encontrado — rode bootstrap.py"},
                         ensure_ascii=False))
        sys.exit(1)

    os.makedirs(args.out_dir, exist_ok=True)
    base = os.path.splitext(os.path.basename(args.video))[0]
    wav = os.path.join(args.out_dir, base + ".wav")

    # 1. Extrai áudio mono 16k (formato que o whisper espera; leve).
    r = subprocess.run(
        ["ffmpeg", "-y", "-i", args.video, "-ar", "16000", "-ac", "1",
         "-c:a", "pcm_s16le", wav],
        capture_output=True, text=True)
    if r.returncode != 0:
        print(json.dumps({"ok": False, "erro": "ffmpeg falhou ao extrair áudio: "
                          + r.stderr[-500:]}, ensure_ascii=False))
        sys.exit(1)

    # 2. WhisperX, pt, sem alinhamento (só texto).
    r2 = subprocess.run(
        [wx, wav, "--language", args.lang, "--model", args.model,
         "--no_align", "--output_format", "txt",
         "--output_dir", args.out_dir, "--print_progress", "False"],
        capture_output=True, text=True)
    # WhisperX nomeia o txt pelo basename do wav.
    txt = os.path.join(args.out_dir, base + ".txt")
    if r2.returncode != 0 or not os.path.exists(txt):
        print(json.dumps({"ok": False, "erro": "whisperx falhou: " + r2.stderr[-800:]},
                         ensure_ascii=False))
        sys.exit(1)

    with open(txt, encoding="utf-8") as f:
        texto = f.read().strip()

    # Limpa o wav temporário (o txt fica como registro bruto).
    try:
        os.remove(wav)
    except OSError:
        pass

    print(json.dumps({
        "ok": True,
        "txt": txt,
        "texto": texto,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
