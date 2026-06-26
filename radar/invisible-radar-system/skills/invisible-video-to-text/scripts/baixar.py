#!/usr/bin/env python3
"""baixar.py — baixa um vídeo (Instagram / TikTok / YouTube) via yt-dlp.

Recebe um link e grava `<out-dir>/<slug>.mp4`. Imprime JSON com o caminho final,
a plataforma detectada, a duração e a URL fonte — o que a skill precisa pro
cabeçalho do material.md.

Armadilhas já resolvidas (ver Radar de Referências, em TS, como referência):
- **Instagram** costuma exigir login: yt-dlp puxa os cookies do navegador
  (--cookies-from-browser). Tentamos Chrome, depois Safari, depois sem cookies.
  Se todos falharem, a saída JSON traz `ok: false` com instrução clara.
- **TikTok** às vezes precisa de impersonation de TLS; o yt-dlp recente resolve
  sozinho na maioria dos casos. Sem flag especial por padrão.
- **YouTube** baixa direto.

Uso:
    python3 baixar.py <link> --out-dir <dir> [--yt-dlp-bin <bin>] [--slug <nome>]
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from urllib.parse import urlparse


def detectar_plataforma(url):
    h = urlparse(url).netloc.lower()
    if "instagram" in h:
        return "instagram"
    if "tiktok" in h:
        return "tiktok"
    if "youtube" in h or "youtu.be" in h:
        return "youtube"
    return "desconhecida"


def slugificar(texto, fallback="video"):
    s = re.sub(r"[^\w\s-]", "", (texto or "").strip().lower())
    s = re.sub(r"[\s_-]+", "-", s).strip("-")
    return s[:60] or fallback


def resolver_ytdlp(arg_bin):
    if arg_bin and os.path.exists(arg_bin):
        return arg_bin
    no_path = shutil.which("yt-dlp")
    if no_path:
        return no_path
    cand = os.path.expanduser("~/.invisible-radar/venv/bin/yt-dlp")
    if os.path.exists(cand):
        return cand
    return None


def rodar(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def tentar_download(ytdlp, url, saida_tmpl, cookies_args):
    """Tenta um download com um conjunto de flags de cookie. Retorna o CompletedProcess."""
    cmd = [ytdlp, "-o", saida_tmpl, "--no-playlist",
           "-f", "mp4/bestvideo*+bestaudio/best", "--merge-output-format", "mp4"]
    cmd += cookies_args
    cmd += [url]
    return rodar(cmd)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--yt-dlp-bin", default=None)
    ap.add_argument("--slug", default=None, help="nome-base do arquivo (kebab-case)")
    args = ap.parse_args()

    ytdlp = resolver_ytdlp(args.yt_dlp_bin)
    if not ytdlp:
        print(json.dumps({"ok": False, "erro": "yt-dlp não encontrado — rode bootstrap.py"},
                         ensure_ascii=False))
        sys.exit(1)

    plataforma = detectar_plataforma(args.url)
    os.makedirs(args.out_dir, exist_ok=True)
    slug = slugificar(args.slug) if args.slug else None
    nome_base = slug or "video"
    saida_tmpl = os.path.join(args.out_dir, f"{nome_base}.%(ext)s")

    # Estratégias de cookie, em ordem. Instagram precisa; os outros tentam sem primeiro.
    if plataforma == "instagram":
        estrategias = [
            ["--cookies-from-browser", "chrome"],
            ["--cookies-from-browser", "safari"],
            [],  # última tentativa sem cookies
        ]
    else:
        estrategias = [[], ["--cookies-from-browser", "chrome"]]

    ultimo = None
    for cookies_args in estrategias:
        r = tentar_download(ytdlp, args.url, saida_tmpl, cookies_args)
        ultimo = r
        if r.returncode == 0:
            break

    if not ultimo or ultimo.returncode != 0:
        msg = (ultimo.stderr[-800:] if ultimo else "sem saída")
        instrucao = ""
        if plataforma == "instagram":
            instrucao = ("Instagram costuma exigir login. Faça login no Instagram no "
                         "Chrome (ou Safari) nesta máquina e tente de novo — o yt-dlp "
                         "puxa os cookies do navegador.")
        print(json.dumps({"ok": False, "plataforma": plataforma,
                          "erro": msg, "instrucao": instrucao}, ensure_ascii=False))
        sys.exit(1)

    # Acha o arquivo gerado (yt-dlp pode ter escolhido outra extensão antes do merge).
    final = None
    for f in os.listdir(args.out_dir):
        if f.startswith(nome_base + ".") and f.lower().endswith((".mp4", ".mkv", ".webm", ".mov")):
            final = os.path.join(args.out_dir, f)
            break
    if not final:
        print(json.dumps({"ok": False, "plataforma": plataforma,
                          "erro": "download terminou mas não achei o arquivo de saída"},
                         ensure_ascii=False))
        sys.exit(1)

    # Metadados via ffprobe (duração).
    dur = None
    rp = rodar(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                "-of", "default=nokey=1:noprint_wrappers=1", final])
    if rp.returncode == 0:
        try:
            dur = round(float(rp.stdout.strip()), 1)
        except ValueError:
            pass

    print(json.dumps({
        "ok": True,
        "arquivo": final,
        "plataforma": plataforma,
        "url": args.url,
        "duracao_seg": dur,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
