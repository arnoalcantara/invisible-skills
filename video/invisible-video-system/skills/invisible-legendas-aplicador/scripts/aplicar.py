#!/usr/bin/env python3
"""aplicar.py — queima legenda animada num vídeo (ou pasta) com Remotion.

Consome o vídeo + o `.json` de timestamp por palavra (a saída da skill
invisible-legenda-arquivos, salva ao lado do vídeo com o mesmo nome) e renderiza
a legenda no estilo escolhido. NÃO transcreve — se o `.json` não existir, avisa
para rodar a invisible-legenda-arquivos antes.

Saída: <out-dir>/<nome>_LEGENDADO.mp4
Por padrão out-dir = <pasta-do-vídeo>/LEGENDADOS (ex.: dentro de COMBINAÇÕES).

Uso:
    python3 aplicar.py <video_ou_pasta> [<video2> ...] \
        --estilo reels|minimal|classic \
        [--projeto-dir <central>] [--out-dir <dir>] [--captions <json>]

Os estilos prontos são reels, minimal e classic. `hormozi` existe mas está em
ajuste (experimental).
"""
import argparse
import json
import os
import subprocess
import sys

PROJETO_CENTRAL_PADRAO = os.path.expanduser("~/.invisible-video/legendas-remotion")
EXTS_VIDEO = {".mp4", ".mov", ".mkv", ".webm", ".m4v"}
ESTILOS = ["reels", "minimal", "classic", "hormozi"]


def dims_video(video):
    """(largura, altura) do vídeo via ffprobe, ou (None, None)."""
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height", "-of", "csv=p=0", video],
        capture_output=True, text=True).stdout.strip()
    try:
        w, h = (int(float(x)) for x in out.split(","))
        return w, h
    except (ValueError, IndexError):
        return None, None


def estilo_default(video):
    """Default por formato: QUADRADO (1:1) → classic; vertical/outros → reels.

    No feed quadrado o estilo clássico (bloco no rodapé) é o que o Arno cravou
    como padrão; no vertical (Reels/Stories) o padrão segue sendo o reels."""
    w, h = dims_video(video)
    if w and h and w == h:
        return "classic"
    return "reels"


def coletar_videos(alvos):
    """Expande os alvos em arquivos de vídeo. Pasta → vídeos diretos (sem
    recursão, ignorando a própria LEGENDADOS)."""
    videos = []
    for a in alvos:
        a = os.path.abspath(os.path.expanduser(a))
        if os.path.isdir(a):
            for nome in sorted(os.listdir(a)):
                if nome == "LEGENDADOS":
                    continue
                p = os.path.join(a, nome)
                if os.path.isfile(p) and os.path.splitext(nome)[1].lower() in EXTS_VIDEO:
                    videos.append(p)
        elif os.path.isfile(a):
            videos.append(a)
        else:
            print(f"aviso: alvo inexistente ignorado: {a}", file=sys.stderr)
    return videos


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("alvos", nargs="+", help="vídeo(s) ou pasta")
    ap.add_argument("--estilo", default=None, choices=ESTILOS,
                    help="força um estilo pra todos. Sem isto, o default é por "
                         "formato: quadrado→classic, vertical→reels.")
    ap.add_argument("--projeto-dir", default=PROJETO_CENTRAL_PADRAO)
    ap.add_argument("--out-dir", default=None, help="default: <pasta>/LEGENDADOS")
    ap.add_argument(
        "--captions",
        default=None,
        help="json explícito (só faz sentido com 1 vídeo); default: <nome>.json irmão",
    )
    args = ap.parse_args()

    projeto_dir = os.path.expanduser(args.projeto_dir)
    public = os.path.join(projeto_dir, "public")
    convert = os.path.join(os.path.dirname(os.path.abspath(__file__)), "convert_captions.mjs")

    if not os.path.exists(os.path.join(projeto_dir, "node_modules")):
        print(
            json.dumps(
                {"erro": f"projeto Remotion não instalado em {projeto_dir}. "
                         "Rode bootstrap.py primeiro."},
                ensure_ascii=False,
            )
        )
        return 1

    videos = coletar_videos(args.alvos)
    if not videos:
        print(json.dumps({"erro": "nenhum vídeo encontrado nos alvos."}, ensure_ascii=False))
        return 1

    os.makedirs(public, exist_ok=True)
    resultados = []

    for video in videos:
        stem = os.path.splitext(os.path.basename(video))[0]
        parent = os.path.dirname(video)

        # localizar o json de timestamp por palavra
        if args.captions and len(videos) == 1:
            json_path = os.path.abspath(os.path.expanduser(args.captions))
        else:
            json_path = os.path.join(parent, stem + ".json")

        if not os.path.exists(json_path):
            resultados.append({
                "video": video,
                "ok": False,
                "erro": f"json de legenda ausente ({os.path.basename(json_path)}). "
                        "Rode invisible-legenda-arquivos neste vídeo antes.",
            })
            continue

        out_dir = os.path.abspath(os.path.expanduser(args.out_dir)) if args.out_dir \
            else os.path.join(parent, "LEGENDADOS")
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, f"{stem}_LEGENDADO.mp4")

        # 1) converter json -> public/captions.json
        c = subprocess.run(
            ["node", convert, json_path, os.path.join(public, "captions.json")]
        )
        if c.returncode != 0:
            resultados.append({"video": video, "ok": False, "erro": "conversão de legenda falhou"})
            continue

        # 2) encenar o vídeo em public/video.mp4 (cópia — robusto p/ o render)
        import shutil
        shutil.copyfile(video, os.path.join(public, "video.mp4"))

        # estilo: explícito (--estilo) sobrepõe; senão default por formato do vídeo.
        estilo = args.estilo or estilo_default(video)

        # 3) renderizar o preset (id da composição == nome do estilo)
        print(f"\n=== legendando ({estilo}): {os.path.basename(video)} ===", flush=True)
        r = subprocess.run(
            ["npx", "remotion", "render", estilo, out_path],
            cwd=projeto_dir,
        )
        if r.returncode != 0:
            resultados.append({"video": video, "ok": False, "erro": "render Remotion falhou"})
            continue

        resultados.append({
            "video": video,
            "ok": True,
            "estilo": estilo,
            "estilo_origem": "explícito" if args.estilo else "default-por-formato",
            "saida": out_path,
            "nome_saida": os.path.basename(out_path),
        })

    ok = sum(1 for r in resultados if r.get("ok"))
    print(json.dumps(
        {"estilo": args.estilo or "default-por-formato (quadrado→classic, vertical→reels)",
         "total": len(resultados), "ok": ok, "resultados": resultados},
        ensure_ascii=False, indent=2,
    ))
    return 0 if ok == len(resultados) else 1


if __name__ == "__main__":
    sys.exit(main())
