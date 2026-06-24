#!/usr/bin/env python3
"""acelerar.py — acelera a velocidade de um vídeo (ou pasta inteira).

Acelera vídeo E áudio juntos pelo mesmo fator, mantendo a sincronia:
    vídeo  -> setpts=PTS/FATOR   (mesmo fps da fonte, frames descartados)
    áudio  -> atempo=FATOR       (preserva o tom — sem voz de chipmunk)

Fatores oferecidos: 1.2x, 1.5x, 2x (todos dentro do range [0.5, 2.0] do
atempo, então um único filtro basta). O vídeo é reencodado (acelerar exige
recompressão) em H.264 yuv420p, qualidade alta (CRF 18), preservando a
resolução e o fps da fonte.

NÃO toca no original: grava ao lado, com `_ACELERADO_<FATOR>` no fim do nome,
na convenção da esteira (sufixos acumulam no fim):
    1.2x -> _ACELERADO_12X    1.5x -> _ACELERADO_15X    2x -> _ACELERADO_2X
Ex.: `..._FINALIZADO.mp4` -> `..._FINALIZADO_ACELERADO_2X.mp4`.

Aceita um arquivo único OU uma pasta (lote). Numa pasta, processa a mídia
direta, pulando o que já tem `_ACELERADO` no nome.

Uso:
    python3 acelerar.py <arquivo|pasta> [--fator 1.2]  [--crf 18] [--preset medium]
    # --fator: 1.2 (padrão), 1.5 ou 2 — um arquivo só, na velocidade escolhida.
Saída (stdout): JSON {"fator": F, "saidas": [...]} ou {"erro": ...}
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys

VIDEO_EXT = {".mp4", ".mov", ".mkv", ".m4v", ".webm"}
# rótulo do sufixo por fator (o que o Arno aprovou): ponto fora, "X" no fim
SUFIXOS = {"1.2": "12X", "1.5": "15X", "2.0": "2X"}


def sufixo_de(fator: float) -> str:
    """'2X' / '15X' / '12X'. Para fatores fora do mapa, deriva tirando o ponto."""
    chave = f"{fator:.1f}"
    if chave in SUFIXOS:
        return SUFIXOS[chave]
    txt = (f"{fator:g}").replace(".", "")  # 1.25 -> '125', 3 -> '3'
    return f"{txt}X"


def fps_fonte(arquivo: str) -> str | None:
    """avg_frame_rate da fonte (ex.: '30000/1001') p/ preservar o fps na saída."""
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0",
             "-show_entries", "stream=avg_frame_rate", "-of",
             "default=nokey=1:noprint_wrappers=1", arquivo],
            capture_output=True, text=True).stdout.strip()
        return out if out and out not in ("0/0", "N/A") else None
    except Exception:
        return None


def tem_audio(arquivo: str) -> bool:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries",
         "stream=index", "-of", "csv=p=0", arquivo],
        capture_output=True, text=True).stdout.strip()
    return bool(out)


def coletar(caminho: str) -> list[str]:
    """Um arquivo → [arquivo]. Uma pasta → vídeos da pasta, pulando já-acelerados."""
    if os.path.isfile(caminho):
        return [os.path.abspath(caminho)]
    alvos = []
    for entry in sorted(os.listdir(caminho)):
        p = os.path.join(caminho, entry)
        ext = os.path.splitext(entry)[1].lower()
        if (os.path.isfile(p) and not entry.startswith(".")
                and ext in VIDEO_EXT
                and "_ACELERADO" not in entry.upper()):
            alvos.append(os.path.abspath(p))
    return alvos


def acelerar_um(arquivo: str, fator: float, suf: str, crf: int,
                preset: str, bitrate: str) -> str:
    raiz, ext = os.path.splitext(arquivo)
    saida = f"{raiz}_ACELERADO_{suf}{ext}"

    cmd = ["ffmpeg", "-y", "-i", arquivo,
           "-filter:v", f"setpts=PTS/{fator}",
           "-c:v", "libx264", "-crf", str(crf), "-preset", preset,
           "-pix_fmt", "yuv420p"]
    fps = fps_fonte(arquivo)
    if fps:
        cmd += ["-r", fps]            # preserva o fps da fonte (dropa frames)
    if tem_audio(arquivo):
        cmd += ["-filter:a", f"atempo={fator}", "-c:a", "aac", "-b:a", bitrate]
    else:
        cmd += ["-an"]
    cmd += ["-movflags", "+faststart", saida]

    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        if os.path.exists(saida):
            os.remove(saida)
        raise RuntimeError(proc.stderr[-1500:])
    return saida


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("entrada", help="arquivo de vídeo OU pasta (lote)")
    ap.add_argument("--fator", type=float, default=1.2,
                    choices=[1.2, 1.5, 2.0],
                    help="velocidade: 1.2 (padrão), 1.5 ou 2")
    ap.add_argument("--crf", type=int, default=18, help="qualidade H.264 (menor=melhor)")
    ap.add_argument("--preset", default="medium", help="preset libx264")
    ap.add_argument("--aac-bitrate", default="192k")
    args = ap.parse_args()

    if not os.path.exists(args.entrada):
        print(json.dumps({"erro": f"não existe: {args.entrada}"}, ensure_ascii=False))
        sys.exit(1)

    suf = sufixo_de(args.fator)
    alvos = coletar(args.entrada)
    if not alvos:
        print(json.dumps({"erro": "nenhum vídeo encontrado (ou tudo já _ACELERADO)"},
                         ensure_ascii=False))
        sys.exit(1)

    saidas = []
    for a in alvos:
        try:
            saidas.append(acelerar_um(a, args.fator, suf, args.crf,
                                      args.preset, args.aac_bitrate))
        except RuntimeError as e:
            print(json.dumps({"erro": "ffmpeg falhou", "arquivo": a, "stderr": str(e)},
                             ensure_ascii=False))
            sys.exit(1)

    print(json.dumps({"fator": args.fator, "sufixo": suf, "saidas": saidas},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
