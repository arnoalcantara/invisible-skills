#!/usr/bin/env python3
"""normalizar.py — normaliza um corte para um alvo comum de specs.

Cortes diferentes podem divergir em resolução (4K/1080), proporção, fps, códec,
áudio (mono/stereo, sample rate). `concat -c copy` exige specs idênticas, senão
quebra ou gera vídeo corrompido. A solução validada: normalizar CADA corte uma
vez para o alvo escolhido, e só depois concatenar por -c copy (rápido, sem
reencode duplo).

Vídeo: scale preservando proporção + pad (barras) + setsar=1 → encaixa em
qualquer alvo sem distorcer. fps fixado. Códec/CRF do alvo.
Áudio: aformat para sample rate + canais do alvo, AAC.

Uso:
    python3 normalizar.py <video> --out <saida> \
        --largura 1080 --altura 1920 --fps 30 \
        [--vcodec libx265] [--crf 20] [--preset medium] \
        [--sample-rate 48000] [--canais 2]

Saída (stdout): JSON {"arquivo": "<saida>"} ou {"erro": ...}
"""
import argparse
import json
import os
import subprocess
import sys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--out", required=True)
    ap.add_argument("--largura", type=int, default=1080)
    ap.add_argument("--altura", type=int, default=1920)
    ap.add_argument("--fps", default="30")
    ap.add_argument("--vcodec", default="libx265",
                    help="libx265 (HEVC) ou libx264 (H.264)")
    ap.add_argument("--crf", type=int, default=20)
    ap.add_argument("--preset", default="medium")
    ap.add_argument("--sample-rate", default="48000")
    ap.add_argument("--canais", type=int, default=2)
    args = ap.parse_args()

    video = os.path.abspath(args.video)
    if not os.path.isfile(video):
        print(json.dumps({"erro": f"vídeo não existe: {video}"}))
        sys.exit(1)

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)

    W, H = args.largura, args.altura
    # scale para caber dentro do alvo preservando proporção (decrease), depois
    # pad centralizando com barras, e setsar=1 para sample aspect ratio neutro.
    vf = (f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
          f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,setsar=1")

    cmd = [
        "ffmpeg", "-y", "-i", video,
        "-map", "0:v:0", "-map", "0:a:0?",
        "-vf", vf, "-r", str(args.fps),
        "-c:v", args.vcodec, "-crf", str(args.crf), "-preset", args.preset,
        "-pix_fmt", "yuv420p",
    ]
    if args.vcodec == "libx265":
        cmd += ["-tag:v", "hvc1"]
    cmd += ["-c:a", "aac", "-ar", str(args.sample_rate), "-ac", str(args.canais),
            args.out]

    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        print(json.dumps({"erro": "ffmpeg falhou", "stderr": proc.stderr[-1500:]},
                         ensure_ascii=False))
        sys.exit(1)

    print(json.dumps({"arquivo": os.path.abspath(args.out)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
