#!/usr/bin/env python3
"""Renderiza um painel didático animado no Remotion a partir de um JSON de props.

Recebe o template (FluxoDeNos | ErroCerto | ConceitoNomeado) e um JSON com o conteúdo
do painel (título, nós, texto...) + opcionalmente o PNG do personagem já recortado.
Escreve o props.json no public/ do projeto Remotion central e renderiza o .mp4.

A duração vem do campo "duracaoSeg" no JSON (default 5). Saída 1080x1920 / 30fps / h264.

Uso:
    python3 render_painel.py \
        --template FluxoDeNos \
        --props painel.json \
        [--personagem /caminho/personagem_ALPHA.png] \
        --out /caminho/PAINEL_ANIM.mp4

O projeto Remotion central é ~/.invisible-video/painel-animado-remotion (bootstrap).
"""
import argparse
import json
import os
import shutil
import subprocess
import sys

HOME = os.path.expanduser("~")
REMOTION = os.path.join(HOME, ".invisible-video", "painel-animado-remotion")
TEMPLATES = {"FluxoDeNos", "ErroCerto", "ConceitoNomeado"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--template", required=True, choices=sorted(TEMPLATES))
    ap.add_argument("--props", required=True, help="JSON com o conteúdo do painel")
    ap.add_argument("--personagem", default=None, help="PNG recortado (alpha) do personagem")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    node_bin = os.path.join(REMOTION, "node_modules", ".bin", "remotion")
    if not os.path.exists(node_bin):
        sys.stderr.write(f"Projeto Remotion não instalado em {REMOTION}. Rode o bootstrap.\n")
        return 1
    with open(args.props, encoding="utf-8") as f:
        props = json.load(f)

    public = os.path.join(REMOTION, "public")
    os.makedirs(public, exist_ok=True)

    # copia o personagem pro public e referencia pelo nome (staticFile)
    if args.personagem:
        if not os.path.exists(args.personagem):
            sys.stderr.write(f"Personagem não existe: {args.personagem}\n")
            return 1
        dst = os.path.join(public, "personagem.png")
        shutil.copy2(args.personagem, dst)
        props["personagem"] = "personagem.png"

    # escreve o props.json que o calculateMetadata lê
    with open(os.path.join(public, "props.json"), "w", encoding="utf-8") as f:
        json.dump(props, f, ensure_ascii=False)

    os.makedirs(os.path.dirname(os.path.abspath(args.out)) or ".", exist_ok=True)
    cmd = [node_bin, "render", args.template, os.path.abspath(args.out), "--codec=h264"]
    p = subprocess.run(cmd, cwd=REMOTION)
    if p.returncode != 0:
        sys.stderr.write("Falha ao renderizar o painel.\n")
        return p.returncode

    print(json.dumps({"saida": os.path.abspath(args.out), "template": args.template, "ok": True}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
