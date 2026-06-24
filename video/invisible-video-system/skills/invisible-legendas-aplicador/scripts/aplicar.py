#!/usr/bin/env python3
"""aplicar.py — queima legenda animada num vídeo (ou pasta) com Remotion.

Consome o vídeo + o `.json` de timestamp por palavra (a saída da skill
invisible-legenda-arquivos, salva na pasta do segmento nomeada pela BASE — sem
formato nem VAR) e renderiza a legenda no estilo escolhido. NÃO transcreve — se o
`.json` não existir, avisa para rodar a invisible-legenda-arquivos antes.

Lugar na linha de produção: lê os segmentos otimizados de 02_OTIMIZADOS (vertical
e quadrado, não-VAR) e grava na pasta-irmã 03_PREPARADOS. As variações de gancho
(_VAR<n>) vêm prontas da var-gancho-escrito e são puladas no lote de pasta.

Saída: <out-dir>/<id>_OTIMIZADO_LEGENDADO_VERTICAL.mp4 — o token _LEGENDADO entra
ANTES do token de formato, porque o contrato da linha é: formato SEMPRE o último
token. Ex.: GANCHO_VAV19_OTIMIZADO_VERTICAL.mp4 → GANCHO_VAV19_OTIMIZADO_LEGENDADO_VERTICAL.mp4.
Por padrão out-dir = pasta-irmã 03_PREPARADOS.

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
import re
import subprocess
import sys

PROJETO_CENTRAL_PADRAO = os.path.expanduser("~/.invisible-video/legendas-remotion")
EXTS_VIDEO = {".mp4", ".mov", ".mkv", ".webm", ".m4v"}
ESTILOS = ["reels", "minimal", "classic", "hormozi"]

# o .json (da invisible-legenda-arquivos) é nomeado pela BASE, sem formato nem VAR.
# pra achá-lo a partir do clipe (que tem _VERTICAL/_QUADRADO no fim), removemos
# esses tokens do stem antes de procurar o irmão na mesma pasta.
RE_FORMATO = re.compile(r"(?i)_(VERTICAL|QUADRADO|HORIZONTAL)$")
RE_VAR = re.compile(r"(?i)_VAR\d+")


def base_sem_formato_var(stem):
    return RE_VAR.sub("", RE_FORMATO.sub("", stem))


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
    recursão, ignorando a pasta de saída 03_PREPARADOS). Clipes com _VAR<n> são
    pulados em lote de pasta: variações de gancho vêm prontas da var-gancho-escrito
    e não passam pela karaokê. (Um VAR apontado explicitamente como arquivo único
    ainda é aceito.)"""
    videos = []
    for a in alvos:
        a = os.path.abspath(os.path.expanduser(a))
        if os.path.isdir(a):
            for nome in sorted(os.listdir(a)):
                if nome in ("LEGENDADOS", "03_PREPARADOS"):
                    continue
                p = os.path.join(a, nome)
                stem = os.path.splitext(nome)[0]
                if (os.path.isfile(p)
                        and os.path.splitext(nome)[1].lower() in EXTS_VIDEO
                        and not RE_VAR.search(stem)):
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

        # localizar o json de timestamp por palavra: nomeado pela BASE (sem
        # formato/VAR), na mesma pasta do clipe (02_OTIMIZADOS).
        if args.captions and len(videos) == 1:
            json_path = os.path.abspath(os.path.expanduser(args.captions))
        else:
            base = base_sem_formato_var(stem)
            json_path = os.path.join(parent, base + ".json")

        if not os.path.exists(json_path):
            resultados.append({
                "video": video,
                "ok": False,
                "erro": f"json de legenda ausente ({os.path.basename(json_path)}). "
                        "Rode invisible-legenda-arquivos neste segmento antes.",
            })
            continue

        # saída na pasta-irmã 03_PREPARADOS (etapa da linha de produção), não numa
        # subpasta da entrada.
        out_dir = os.path.abspath(os.path.expanduser(args.out_dir)) if args.out_dir \
            else os.path.join(os.path.dirname(parent.rstrip("/")), "03_PREPARADOS")
        os.makedirs(out_dir, exist_ok=True)
        # _LEGENDADO entra ANTES do token de formato (formato sempre o último).
        m = RE_FORMATO.search(stem)
        if m:
            nome_saida = f"{stem[:m.start()]}_LEGENDADO{m.group(0)}"
        else:
            nome_saida = f"{stem}_LEGENDADO"
        out_path = os.path.join(out_dir, f"{nome_saida}.mp4")

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
