#!/usr/bin/env python3
"""Aplica um título (gancho visual) em cada gancho já legendado.

O título é uma cápsula branca única + um emoji, sobreposta por N segundos (default
3s) no INÍCIO do gancho. Aparece de imediato (sem animação de entrada) e some com
fade no fim. O texto é código Remotion de verdade (nunca quebra), sobreposto por
cutaway com ffmpeg mantendo áudio e legenda intactos.

Entrada: pasta com os ganchos legendados (03_PREPARADOS) + um JSON de títulos que
mapeia a BASE do gancho (ex.: "DS_VAV138_GANCHO_1") para {texto, emoji}.

Uso:
    python3 scripts/aplicar.py <pasta> --titulos titulos.json \
        [--dur 3] [--top 150] [--fonte 64] [--substituir]

titulos.json:
    { "DS_VAV138_GANCHO_1": {"texto": "NÃO tem filhos entre 2 e 6 anos?", "emoji": "👀"}, ... }

- Casa só arquivos que contêm "GANCHO" e "LEGENDADO" e batem uma chave do mapa.
  A chave é o prefixo do nome até o número do gancho (regex GANCHO_<n>).
- Gera "..._TITULO_<FMT>.mp4" (sufixo _TITULO antes do token de formato).
- --substituir: apaga o gancho legendado sem título após gerar o com título
  (recomendado — o combinador deve usar a versão com título).

O overlay é forçado à timebase 1/90000 (`-video_track_timescale 90000`) para casar
com o pipeline dos demais clipes; sem isso o concat da etapa de combinação gera PTS
quebrado (duração estoura). Ver referencia/METODO.md.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile

HOME = os.path.expanduser("~")
PROJ = os.path.join(HOME, ".invisible-video", "titulo-gancho-remotion")
FMT_TOKENS = ("VERTICAL", "QUADRADO", "RETRATO")


def ff(bin_):
    from shutil import which
    return which(bin_) or bin_


def base_e_formato(stem, regex):
    parts = stem.split("_")
    fmt = parts[-1] if parts[-1] in FMT_TOKENS else None
    m = re.match(regex, stem)
    return (m.group(1) if m else None), fmt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pasta")
    ap.add_argument("--titulos", required=True, help="JSON base→{texto,emoji}")
    ap.add_argument("--chave-regex", default=r"([A-Za-z0-9]+_(?:VAV\d+_)?GANCHO_\d+)",
                    help="regex que extrai a CHAVE do stem (grupo 1)")
    ap.add_argument("--dur", type=float, default=3.0)
    ap.add_argument("--top", type=int, default=150)
    ap.add_argument("--fonte", type=int, default=64)
    ap.add_argument("--substituir", action="store_true")
    args = ap.parse_args()

    ffmpeg = ff("ffmpeg")
    render_bin = os.path.join(PROJ, "node_modules", ".bin", "remotion")
    if not os.path.exists(render_bin):
        print(json.dumps({"erro": f"projeto Remotion não instalado em {PROJ}. Rode scripts/bootstrap.py."}))
        return 1

    with open(args.titulos, encoding="utf-8") as f:
        titulos = json.load(f)

    alvos = []
    for n in sorted(os.listdir(args.pasta)):
        if not n.lower().endswith(".mp4"):
            continue
        if "GANCHO" not in n or "LEGENDADO" not in n or "_TITULO" in n:
            continue
        stem = os.path.splitext(n)[0]
        chave, fmt = base_e_formato(stem, args.chave_regex)
        if chave in titulos:
            alvos.append((n, stem, chave, fmt))

    if not alvos:
        print(json.dumps({"erro": "nenhum gancho legendado casou o mapa de títulos",
                          "pasta": args.pasta, "chaves_mapa": list(titulos)}, ensure_ascii=False))
        return 1

    pub = os.path.join(PROJ, "public")
    os.makedirs(pub, exist_ok=True)
    resultados = []

    for n, stem, chave, fmt in alvos:
        info = titulos[chave]
        with open(os.path.join(pub, "props.json"), "w", encoding="utf-8") as f:
            json.dump({"texto": info["texto"], "emoji": info.get("emoji", ""),
                       "duracaoSeg": args.dur, "topOffset": args.top,
                       "fontSize": args.fonte}, f, ensure_ascii=False)
        overlay = os.path.join(tempfile.gettempdir(), f"titulo_overlay_{chave}.mov")
        r = subprocess.run([render_bin, "render", "Titulo", overlay],
                           cwd=PROJ, capture_output=True, text=True)
        if r.returncode != 0:
            resultados.append({"arquivo": n, "ok": False, "etapa": "render", "erro": r.stderr[-400:]})
            continue
        if fmt and stem.endswith("_" + fmt):
            novo = stem[: -(len(fmt) + 1)] + "_TITULO_" + fmt
        else:
            novo = stem + "_TITULO"
        entrada = os.path.join(args.pasta, n)
        saida = os.path.join(args.pasta, novo + ".mp4")
        cmd = [ffmpeg, "-y", "-i", entrada, "-i", overlay,
               "-filter_complex",
               f"[0:v][1:v]overlay=0:0:enable='lte(t,{args.dur})':format=auto[v]",
               "-map", "[v]", "-map", "0:a",
               "-c:v", "libx264", "-crf", "18", "-preset", "medium",
               "-pix_fmt", "yuv420p", "-video_track_timescale", "90000",
               "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", saida]
        r2 = subprocess.run(cmd, capture_output=True, text=True)
        if r2.returncode != 0:
            resultados.append({"arquivo": n, "ok": False, "etapa": "overlay", "erro": r2.stderr[-400:]})
            continue
        try:
            os.remove(overlay)
        except OSError:
            pass
        if args.substituir:
            os.remove(entrada)
        resultados.append({"arquivo": n, "ok": True, "chave": chave,
                           "emoji": info.get("emoji", ""), "saida": os.path.basename(saida),
                           "substituido": args.substituir})

    print(json.dumps({"total": len(alvos),
                      "ok": sum(1 for x in resultados if x.get("ok")),
                      "resultados": resultados}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
