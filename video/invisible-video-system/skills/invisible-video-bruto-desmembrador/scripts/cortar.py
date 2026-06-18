#!/usr/bin/env python3
"""cortar.py — recodifica cada seção preservando as specs do bruto.

Lê as specs do bruto com ffprobe (codec de vídeo, pix_fmt, fps; codec/sample
rate/canais/bitrate de áudio) e recodifica cada corte ao frame exato com ffmpeg,
mapeando só v+a (descarta data/timecode). Salva em pasta com o nome PLURAL da
seção; arquivo nomeado <nome_bruto>__<SECAO>.<ext_orig>.

Recodifica (não copia) porque o corte ao frame exato em HEVC exige reencode —
copy-codec só cortaria em keyframe. CRF 18 preset medium preserva qualidade.

Uso:
    python3 cortar.py <video> <cortes.json> --out-base <pasta_projeto> \
        [--crf 18] [--preset medium]

cortes.json é a saída de achar_bordas.py.

Saída (stdout): JSON {"gerados": [{secao, arquivo, ss, to}]}
"""
import argparse
import json
import os
import subprocess
import sys


def ffprobe_specs(video):
    def probe(stream, entries):
        cmd = ["ffprobe", "-v", "error", "-select_streams", stream,
               "-show_entries", entries, "-of", "json", video]
        out = subprocess.run(cmd, capture_output=True, text=True).stdout
        try:
            return json.loads(out).get("streams", [])
        except json.JSONDecodeError:
            return []

    v = probe("v:0", "stream=codec_name,pix_fmt,r_frame_rate")
    a = probe("a:0", "stream=codec_name,sample_rate,channels,bit_rate")
    vs = v[0] if v else {}
    as_ = a[0] if a else {}

    # r_frame_rate vem como "30000/1001"; passamos direto ao -r
    return {
        "vcodec": vs.get("codec_name", "hevc"),
        "pix_fmt": vs.get("pix_fmt", "yuv420p"),
        "fps": vs.get("r_frame_rate", "30"),
        "acodec": as_.get("codec_name", "aac"),
        "sample_rate": as_.get("sample_rate", "48000"),
        "channels": as_.get("channels", 2),
        "bit_rate": as_.get("bit_rate"),
    }


def encoder_para_codec(codec):
    """Mapeia codec lido pelo ffprobe para o encoder do ffmpeg."""
    mapa = {"hevc": "libx265", "h265": "libx265", "h264": "libx264", "avc": "libx264"}
    return mapa.get(codec, "libx265")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("cortes")
    ap.add_argument("--out-base", required=True, help="pasta onde criar GANCHOS/, etc.")
    ap.add_argument("--crf", type=int, default=18)
    ap.add_argument("--preset", default="medium")
    args = ap.parse_args()

    video = os.path.abspath(args.video)
    with open(args.cortes, encoding="utf-8") as f:
        cortes = json.load(f)["cortes"]

    specs = ffprobe_specs(video)
    venc = encoder_para_codec(specs["vcodec"])
    nome_bruto = os.path.splitext(os.path.basename(video))[0]
    ext = os.path.splitext(video)[1] or ".mp4"

    gerados = []
    for c in cortes:
        if "erro" in c:
            gerados.append({"secao": c["secao"], "erro": c["erro"]})
            continue

        pasta = os.path.join(os.path.abspath(args.out_base), c["plural"])
        os.makedirs(pasta, exist_ok=True)
        saida = os.path.join(pasta, f"{nome_bruto}__{c['secao']}{ext}")

        cmd = [
            "ffmpeg", "-y", "-i", video,
            "-ss", str(c["ss"]), "-to", str(c["to"]),
            "-map", "0:v:0", "-map", "0:a:0",
            "-c:v", venc, "-crf", str(args.crf), "-preset", args.preset,
            "-pix_fmt", specs["pix_fmt"], "-r", specs["fps"],
        ]
        if venc == "libx265":
            cmd += ["-tag:v", "hvc1"]
        cmd += ["-c:a", specs["acodec"], "-ar", str(specs["sample_rate"]),
                "-ac", str(specs["channels"])]
        if specs.get("bit_rate"):
            cmd += ["-b:a", specs["bit_rate"]]
        cmd += [saida]

        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            gerados.append({"secao": c["secao"], "erro": "ffmpeg falhou",
                            "stderr": proc.stderr[-1500:]})
        else:
            gerados.append({"secao": c["secao"], "arquivo": saida,
                            "ss": c["ss"], "to": c["to"]})

    print(json.dumps({"gerados": gerados, "specs": specs}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
