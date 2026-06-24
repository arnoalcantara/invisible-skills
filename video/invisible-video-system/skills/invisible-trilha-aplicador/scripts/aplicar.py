#!/usr/bin/env python3
"""Aplica trilha de fundo num vídeo (ou pasta), com normalização de loudness.

Método (validado em sessão real):
- A fala do vídeo é normalizada por GANHO LINEAR para um alvo em LUFS (default -14,
  padrão Reels/social). Ganho linear, não compressão: preserva a dinâmica natural da voz.
- A trilha é normalizada para um alvo absoluto em LUFS (default -37, ~23 dB abaixo da
  fala). Como cada trilha vem masterizada num nível diferente, "X%" de volume não é
  consistente — LUFS é. Cada trilha recebe um ganho próprio que a leva ao mesmo destino.
- Mix com amix normalize=0 (não divide o volume da fala). Trilha com fade in/out de 1.5s
  e loop (-stream_loop) para cobrir vídeos mais longos que ela.
- Vídeo copiado sem recompressão (-c:v copy). Só o áudio é remixado (AAC 192k).

Em lote, as trilhas da pasta são distribuídas pelos vídeos o mais igualmente possível
(round-robin sobre a lista ordenada de trilhas).

Saída: <out-dir>/<nome>_FINALIZADO.mp4   (default out-dir = pasta-irmã 99_FINALIZADOS;
lê tipicamente de 04_COMBINADOS)
O original nunca é tocado.
"""
import argparse
import os
import re
import subprocess
import sys

VIDEO_EXTS = {".mp4", ".mov", ".m4v", ".mkv", ".webm"}
AUDIO_EXTS = {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg"}
OUT_DIR_NAME = "99_FINALIZADOS"


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def medir_lufs(path):
    """Integrated loudness (LUFS) via ebur128. Retorna float ou None."""
    r = run(["ffmpeg", "-i", path, "-af", "ebur128", "-f", "null", "-"])
    txt = r.stderr
    # pega o último "I:  -xx.x LUFS" do resumo
    matches = re.findall(r"I:\s*(-?\d+(?:\.\d+)?)\s*LUFS", txt)
    return float(matches[-1]) if matches else None


def duracao(path):
    r = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "csv=p=0", path])
    try:
        return float(r.stdout.strip())
    except ValueError:
        return None


def listar_videos(alvo):
    if os.path.isfile(alvo):
        return [alvo]
    out = []
    for nome in sorted(os.listdir(alvo)):
        p = os.path.join(alvo, nome)
        if os.path.isfile(p) and os.path.splitext(nome)[1].lower() in VIDEO_EXTS:
            out.append(p)
    return out


def listar_trilhas(trilhas_dir):
    out = []
    for nome in sorted(os.listdir(trilhas_dir)):
        p = os.path.join(trilhas_dir, nome)
        if os.path.isfile(p) and os.path.splitext(nome)[1].lower() in AUDIO_EXTS:
            out.append(p)
    return out


def aplicar(video, trilha, trilha_lufs, alvo_fala, alvo_trilha, out_dir):
    fala_lufs = medir_lufs(video)
    dur = duracao(video)
    if fala_lufs is None or dur is None:
        return None, "não consegui medir loudness/duração"

    g_fala = alvo_fala - fala_lufs
    g_trilha = alvo_trilha - trilha_lufs
    fade_out = max(0.0, dur - 1.5)

    stem = os.path.splitext(os.path.basename(video))[0]
    out = os.path.join(out_dir, f"{stem}_FINALIZADO.mp4")

    filtro = (
        f"[0:a]volume={g_fala:.2f}dB[fala];"
        f"[1:a]volume={g_trilha:.2f}dB,"
        f"afade=t=in:st=0:d=1.5,afade=t=out:st={fade_out:.3f}:d=1.5[bg];"
        f"[fala][bg]amix=inputs=2:duration=first:normalize=0[aout]"
    )
    cmd = [
        "ffmpeg", "-y", "-i", video,
        "-stream_loop", "-1", "-i", trilha,
        "-filter_complex", filtro,
        "-map", "0:v", "-map", "[aout]",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        out, "-loglevel", "error",
    ]
    r = run(cmd)
    if r.returncode != 0:
        return None, r.stderr.strip().splitlines()[-1] if r.stderr else "erro ffmpeg"
    info = (f"fala {fala_lufs}→{alvo_fala} ({g_fala:+.1f}dB) | "
            f"trilha {os.path.basename(trilha)} {trilha_lufs}→{alvo_trilha} ({g_trilha:+.1f}dB)")
    return out, info


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("alvo", help="vídeo único OU pasta de vídeos")
    ap.add_argument("--trilhas", required=True, help="pasta com as trilhas (áudio)")
    ap.add_argument("--trilha", help="usar UMA trilha fixa (nome do arquivo) em vez de distribuir")
    ap.add_argument("--alvo-fala", type=float, default=-14.0)
    ap.add_argument("--alvo-trilha", type=float, default=-37.0)
    ap.add_argument("--out-dir", help="default: pasta-irmã 99_FINALIZADOS")
    args = ap.parse_args()

    videos = listar_videos(args.alvo)
    if not videos:
        print("Nenhum vídeo encontrado no alvo.", file=sys.stderr)
        return 1

    trilhas = listar_trilhas(args.trilhas)
    if args.trilha:
        trilhas = [t for t in trilhas if os.path.basename(t) == args.trilha]
    if not trilhas:
        print("Nenhuma trilha encontrada.", file=sys.stderr)
        return 1

    # 99_FINALIZADOS é pasta-IRMÃ da entrada (última etapa da linha de produção),
    # não subpasta dela. A entrada é tipicamente 04_COMBINADOS → finalizados vai
    # como irmã, ao lado de 02_OTIMIZADOS/03_PREPARADOS/04_COMBINADOS.
    entrada = args.alvo if os.path.isdir(args.alvo) else os.path.dirname(args.alvo)
    base = os.path.dirname(os.path.abspath(entrada.rstrip("/")))
    out_dir = args.out_dir or os.path.join(base, OUT_DIR_NAME)
    os.makedirs(out_dir, exist_ok=True)

    # mede cada trilha uma vez (cache)
    trilha_lufs = {t: medir_lufs(t) for t in trilhas}

    print(f"{len(videos)} vídeo(s) | {len(trilhas)} trilha(s) | "
          f"fala→{args.alvo_fala} LUFS, trilha→{args.alvo_trilha} LUFS")
    print(f"saída: {out_dir}\n" + "-" * 80)

    ok = 0
    for i, v in enumerate(videos):
        t = trilhas[i % len(trilhas)]
        tl = trilha_lufs[t]
        if tl is None:
            print(f"[PULADO] {os.path.basename(v)} — trilha sem loudness medível")
            continue
        out, info = aplicar(v, t, tl, args.alvo_fala, args.alvo_trilha, out_dir)
        if out:
            ok += 1
            print(f"[{ok:2d}] {os.path.basename(out)}\n     {info}")
        else:
            print(f"[ERRO] {os.path.basename(v)} — {info}")

    print("-" * 80)
    print(f"TOTAL: {ok}/{len(videos)} em {out_dir}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
