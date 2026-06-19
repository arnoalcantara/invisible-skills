#!/usr/bin/env python3
"""otimizar.py — remove silêncios internos de um vídeo sem comer palavra.

Critério validado em sessão real (ver referencia/METODO.md):
  - silêncio = trecho > 0.5s abaixo de -35dB (silencedetect).
    -35dB e não -30: a -30 a palavra final dita baixo (decrescendo do professor)
    caía como silêncio e era cortada. -35 trata fala fraca como fala.
  - respiro ASSIMÉTRICO: 0.10s na entrada (após silence_end), 0.25s na saída
    (após silence_start). Início de palavra tem ataque alto (0.1 basta); fim
    decai suave — cauda baixa de "S"/vogal átona — precisa 0.25 pra não comer.
    Respiro simétrico come consoante final: NÃO usar.
  - só silêncios INTERNOS: começo e fim do vídeo ficam intactos.

Constrói os segmentos a MANTER (complemento dos silêncios, com respiros), e os
recorta+concatena ao frame exato via filter_complex (trim/atrim + setpts/asetpts
+ concat). Reencode HEVC preservando specs do original.

Aceita um ARQUIVO ou uma PASTA (lote: otimiza todos os vídeos da pasta).

Uso:
    python3 otimizar.py <arquivo_ou_pasta> [--out-dir <dir>]
        [--silence-noise -35dB] [--silence-min 0.5]
        [--respiro-entrada 0.10] [--respiro-saida 0.25]
        [--crf 20] [--preset medium]

Saída (stdout): JSON {"resultados": [{origem, saida, silencios, segmentos, verificacao}]}
"""
import argparse
import json
import os
import re
import subprocess
import sys

VIDEO_EXT = {".mp4", ".mov", ".mkv", ".m4v", ".avi", ".webm"}

RE_START = re.compile(r"silence_start:\s*([\d.]+)")
RE_END = re.compile(r"silence_end:\s*([\d.]+)")


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
    a = probe("a:0", "stream=codec_name,sample_rate,channels")
    fmt_cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration",
               "-of", "json", video]
    try:
        dur = float(json.loads(
            subprocess.run(fmt_cmd, capture_output=True, text=True).stdout
        )["format"]["duration"])
    except (json.JSONDecodeError, KeyError, ValueError):
        dur = None
    vs = v[0] if v else {}
    as_ = a[0] if a else {}
    return {
        "vcodec": vs.get("codec_name", "hevc"),
        "pix_fmt": vs.get("pix_fmt", "yuv420p"),
        "fps": vs.get("r_frame_rate", "30"),
        "acodec": as_.get("codec_name", "aac"),
        "sample_rate": as_.get("sample_rate", "48000"),
        "channels": int(as_.get("channels", 2) or 2),
        "duracao": dur,
    }


def encoder_para_codec(codec):
    mapa = {"hevc": "libx265", "h265": "libx265", "h264": "libx264", "avc": "libx264"}
    return mapa.get(codec, "libx265")


def detectar_silencios(video, noise, dur_min):
    """Roda silencedetect e devolve lista de (inicio, fim) de cada silêncio."""
    cmd = ["ffmpeg", "-i", video, "-af",
           f"silencedetect=noise={noise}:d={dur_min}", "-f", "null", "-"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    log = proc.stderr
    silencios = []
    inicio = None
    for linha in log.splitlines():
        ms = RE_START.search(linha)
        me = RE_END.search(linha)
        if ms:
            inicio = float(ms.group(1))
        if me and inicio is not None:
            silencios.append((inicio, float(me.group(1))))
            inicio = None
    # silêncio que vai até o fim sem silence_end: ignorado (não é interno)
    return silencios


def segmentos_a_manter(silencios, duracao, resp_in, resp_out):
    """Complemento dos silêncios = trechos com fala. Aplica respiro assimétrico.

    Para cada silêncio (s_ini, s_fim):
      - o trecho de fala ANTES dele termina em s_ini + resp_out (cauda preservada)
      - o trecho de fala DEPOIS dele começa em s_fim - resp_in (ataque preservado)
    Começo (0) e fim (duracao) ficam intactos.
    """
    if not silencios:
        return [(0.0, duracao)]

    segmentos = []
    cursor = 0.0
    for (s_ini, s_fim) in silencios:
        fim_fala = min(s_ini + resp_out, duracao)
        if fim_fala > cursor:
            segmentos.append((cursor, fim_fala))
        cursor = max(s_fim - resp_in, fim_fala)
    if cursor < duracao:
        segmentos.append((cursor, duracao))
    # remove segmentos degenerados
    return [(a, b) for (a, b) in segmentos if b - a > 0.01]


def montar_filter_complex(segmentos):
    """Gera filter_complex que recorta cada segmento (v+a) e concatena."""
    partes = []
    labels = []
    for i, (a, b) in enumerate(segmentos):
        partes.append(
            f"[0:v]trim=start={a:.3f}:end={b:.3f},setpts=PTS-STARTPTS[v{i}];")
        partes.append(
            f"[0:a]atrim=start={a:.3f}:end={b:.3f},asetpts=PTS-STARTPTS[a{i}];")
        labels.append(f"[v{i}][a{i}]")
    n = len(segmentos)
    concat = "".join(labels) + f"concat=n={n}:v=1:a=1[vout][aout]"
    return "".join(partes) + concat


def otimizar_um(video, out_dir, noise, dur_min, resp_in, resp_out, crf, preset):
    specs = ffprobe_specs(video)
    if specs["duracao"] is None:
        return {"origem": video, "erro": "não consegui ler a duração (ffprobe)"}

    silencios = detectar_silencios(video, noise, dur_min)
    segmentos = segmentos_a_manter(silencios, specs["duracao"], resp_in, resp_out)

    nome = os.path.splitext(os.path.basename(video))[0]
    ext = os.path.splitext(video)[1] or ".mp4"
    os.makedirs(out_dir, exist_ok=True)
    saida = os.path.join(out_dir, f"{nome}__OTIMIZADO{ext}")

    if len(segmentos) <= 1 and not silencios:
        # nada a cortar — ainda assim entrega cópia reencodada? Não: só avisa.
        return {"origem": video, "saida": None,
                "silencios": [], "segmentos": len(segmentos),
                "aviso": "nenhum silêncio interno >%.2fs detectado; nada a otimizar"
                         % dur_min}

    fc = montar_filter_complex(segmentos)
    venc = encoder_para_codec(specs["vcodec"])

    cmd = [
        "ffmpeg", "-y", "-i", video,
        "-filter_complex", fc, "-map", "[vout]", "-map", "[aout]",
        "-c:v", venc, "-crf", str(crf), "-preset", preset,
        "-pix_fmt", specs["pix_fmt"], "-r", specs["fps"],
    ]
    if venc == "libx265":
        cmd += ["-tag:v", "hvc1"]
    cmd += ["-c:a", "aac", "-ar", str(specs["sample_rate"]),
            "-ac", str(specs["channels"]), saida]

    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        return {"origem": video, "erro": "ffmpeg falhou",
                "stderr": proc.stderr[-1500:]}

    # verificação: silencedetect no resultado. Não pode sobrar silêncio >dur_min.
    # Pausas ~0.35–0.49 são o respiro preservado (silencedetect mede do
    # cruzamento de limiar, não da última sílaba) — esperado.
    residuais = detectar_silencios(saida, noise, dur_min)
    return {
        "origem": video,
        "saida": saida,
        "silencios": len(silencios),
        "segmentos": len(segmentos),
        "verificacao": {
            "silencios_residuais": len(residuais),
            "ok": len(residuais) == 0,
            "nota": "residuais>0 só é problema se forem pausas longas reais; "
                    "respiros ~0.35-0.49s não disparam em d=%.2f" % dur_min,
        },
    }


def coletar_videos(caminho):
    if os.path.isfile(caminho):
        return [caminho]
    vids = []
    for entry in sorted(os.listdir(caminho)):
        p = os.path.join(caminho, entry)
        if (os.path.isfile(p) and not entry.startswith(".")
                and os.path.splitext(entry)[1].lower() in VIDEO_EXT
                and "__OTIMIZADO" not in entry):
            vids.append(p)
    return vids


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("entrada", help="arquivo de vídeo OU pasta (lote)")
    ap.add_argument("--out-dir", help="pasta de saída (padrão: OTIMIZADOS/ ao lado)")
    ap.add_argument("--silence-noise", default="-35dB")
    ap.add_argument("--silence-min", type=float, default=0.5)
    ap.add_argument("--respiro-entrada", type=float, default=0.10)
    ap.add_argument("--respiro-saida", type=float, default=0.25)
    ap.add_argument("--crf", type=int, default=20)
    ap.add_argument("--preset", default="medium")
    args = ap.parse_args()

    entrada = os.path.abspath(args.entrada)
    if not os.path.exists(entrada):
        print(json.dumps({"erro": f"não existe: {entrada}"}))
        sys.exit(1)

    videos = coletar_videos(entrada)
    if not videos:
        print(json.dumps({"erro": "nenhum vídeo encontrado"}))
        sys.exit(1)

    base = entrada if os.path.isdir(entrada) else os.path.dirname(entrada)
    out_dir = os.path.abspath(args.out_dir) if args.out_dir \
        else os.path.join(base, "OTIMIZADOS")

    resultados = []
    for v in videos:
        resultados.append(otimizar_um(
            v, out_dir, args.silence_noise, args.silence_min,
            args.respiro_entrada, args.respiro_saida, args.crf, args.preset))

    print(json.dumps({"out_dir": out_dir, "resultados": resultados},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
