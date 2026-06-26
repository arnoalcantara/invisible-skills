#!/usr/bin/env python3
"""extrair_frames.py — extrai frames de um vídeo para o AGENTE ler o texto na tela.

A leitura do texto na tela (caixinha de pergunta, legenda queimada, título,
lower-thirds) é feita pelo AGENTE com visão — não por OCR. Este script só extrai
os frames; o agente os interpreta depois.

Amostragem inteligente, não uniforme: o texto que importa (caixinha do Instagram,
título do YouTube) costuma aparecer cedo e ficar fixo. Então amostramos DENSO nos
primeiros segundos e ESPARSO ao longo do resto — pega o texto inicial e ainda
flagra legendas que mudam no meio/fim.

Imprime JSON com a lista de frames (caminho + timestamp). O agente lê e, ao
terminar, a skill apaga a pasta de frames (são temporários).

Uso:
    python3 extrair_frames.py <video> --out-dir <dir-frames> [--max 10]
"""
import argparse
import json
import os
import subprocess
import sys


def duracao(video):
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nokey=1:noprint_wrappers=1", video],
        capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except (ValueError, AttributeError):
        return None


def tempos_amostra(dur, maxn):
    """Lista de timestamps: densos no início, esparsos no resto."""
    if not dur or dur <= 0:
        return [0.0]
    # Início denso: a caixinha/título mora aqui.
    densos = [t for t in (0, 1, 2, 3, 5, 8) if t < dur]
    # Resto esparso: pega mudanças de legenda no meio/fim.
    restantes = maxn - len(densos)
    esparsos = []
    if restantes > 0 and dur > 10:
        passo = (dur - 10) / (restantes + 1)
        esparsos = [round(10 + passo * (i + 1), 1) for i in range(restantes)]
        esparsos = [t for t in esparsos if t < dur]
    tempos = sorted(set(densos + esparsos))
    return tempos[:maxn]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--max", type=int, default=10, help="máximo de frames")
    args = ap.parse_args()

    if not os.path.exists(args.video):
        print(json.dumps({"ok": False, "erro": f"vídeo não encontrado: {args.video}"},
                         ensure_ascii=False))
        sys.exit(1)

    os.makedirs(args.out_dir, exist_ok=True)
    dur = duracao(args.video)
    tempos = tempos_amostra(dur, args.max)

    frames = []
    for t in tempos:
        nome = f"frame_{str(t).replace('.', '_')}s.jpg"
        caminho = os.path.join(args.out_dir, nome)
        r = subprocess.run(
            ["ffmpeg", "-y", "-ss", str(t), "-i", args.video,
             "-frames:v", "1", "-q:v", "2", caminho],
            capture_output=True, text=True)
        if r.returncode == 0 and os.path.exists(caminho):
            frames.append({"t": t, "arquivo": caminho})

    if not frames:
        print(json.dumps({"ok": False, "erro": "ffmpeg não extraiu nenhum frame"},
                         ensure_ascii=False))
        sys.exit(1)

    print(json.dumps({
        "ok": True,
        "duracao_seg": round(dur, 1) if dur else None,
        "frames": frames,
        "nota": "O AGENTE deve ler estes frames (visão), não rodar OCR. "
                "Apague a pasta de frames ao terminar.",
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
