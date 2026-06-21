#!/usr/bin/env python3
"""bootstrap.py — prepara o ambiente da skill invisible-video-var-gancho-escrito.

A skill gera uma variação VAR<n> (gancho animado em texto) com Remotion. Precisa de:
  - node + npm (Remotion roda em Node)
  - ffmpeg (mux/encode do vídeo final)
  - um projeto Remotion instalado (o template embutido em ../remotion)

O projeto Remotion vive num diretório CENTRAL único — ~/.invisible-video/
gancho-escrito-remotion — separado do da skill de legendas (compositions
diferentes). Este bootstrap:

  1. detecta node/npm/ffmpeg;
  2. sincroniza os fontes do template para o diretório central;
  3. roda `npm install` no central UMA vez (ou de novo se o package.json mudou).

Idempotente. Uso:
    python3 bootstrap.py [--projeto-dir <dir>] [--check-only]
Saída (stdout): JSON com o estado de cada dependência e o projeto_dir a usar.
"""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys

PROJETO_CENTRAL_PADRAO = os.path.expanduser("~/.invisible-video/gancho-escrito-remotion")
ARQUIVOS_RAIZ = ["package.json", "tsconfig.json", "remotion.config.ts"]


def existe(bin_):
    return shutil.which(bin_) is not None


def versao(bin_, flag="--version"):
    try:
        out = subprocess.run([bin_, flag], capture_output=True, text=True, timeout=20)
        return out.stdout.strip() or out.stderr.strip()
    except Exception:
        return None


def hash_arquivo(p):
    try:
        with open(p, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except FileNotFoundError:
        return None


def sincronizar_template(template_dir, projeto_dir):
    """Copia os fontes do template para o projeto central. Retorna se o
    package.json mudou (gatilho de reinstalação)."""
    os.makedirs(projeto_dir, exist_ok=True)
    pkg_antes = hash_arquivo(os.path.join(projeto_dir, "package.json"))
    for nome in ARQUIVOS_RAIZ:
        src = os.path.join(template_dir, nome)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(projeto_dir, nome))
    src_dir = os.path.join(template_dir, "src")
    dst_dir = os.path.join(projeto_dir, "src")
    if os.path.isdir(dst_dir):
        shutil.rmtree(dst_dir)
    shutil.copytree(src_dir, dst_dir)
    os.makedirs(os.path.join(projeto_dir, "public"), exist_ok=True)
    pkg_depois = hash_arquivo(os.path.join(projeto_dir, "package.json"))
    return pkg_antes != pkg_depois


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--projeto-dir", default=PROJETO_CENTRAL_PADRAO)
    ap.add_argument("--check-only", action="store_true")
    args = ap.parse_args()

    template_dir = os.path.normpath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "remotion")
    )
    projeto_dir = os.path.expanduser(args.projeto_dir)

    estado = {
        "template_dir": template_dir,
        "projeto_dir": projeto_dir,
        "node": {"ok": existe("node"), "versao": versao("node")},
        "npm": {"ok": existe("npm"), "versao": versao("npm")},
        "ffmpeg": {"ok": existe("ffmpeg")},
        "acoes": [],
        "instrucoes": [],
    }
    node_ok, npm_ok, ffmpeg_ok = estado["node"]["ok"], estado["npm"]["ok"], estado["ffmpeg"]["ok"]

    if not node_ok or not npm_ok:
        estado["instrucoes"].append("Node.js + npm ausentes. Instale com `brew install node` (ou nvm).")
    if not ffmpeg_ok:
        estado["instrucoes"].append("ffmpeg ausente. Instale com `brew install ffmpeg`.")

    node_modules = os.path.join(projeto_dir, "node_modules")
    sources_ok = os.path.exists(template_dir)

    if not args.check_only and node_ok and npm_ok and sources_ok:
        pkg_mudou = sincronizar_template(template_dir, projeto_dir)
        estado["acoes"].append("template sincronizado para o projeto central")
        if not os.path.exists(node_modules) or pkg_mudou:
            estado["acoes"].append("npm install (1ª vez ou package.json mudou)")
            r = subprocess.run(["npm", "install"], cwd=projeto_dir)
            if r.returncode != 0:
                estado["instrucoes"].append(f"npm install falhou em {projeto_dir} — rode manualmente.")
    elif not args.check_only and sources_ok and node_ok:
        sincronizar_template(template_dir, projeto_dir)

    estado["projeto_pronto"] = os.path.exists(node_modules) and os.path.exists(
        os.path.join(projeto_dir, "src", "Root.tsx")
    )
    estado["pronto"] = bool(node_ok and npm_ok and ffmpeg_ok and estado["projeto_pronto"])
    print(json.dumps(estado, ensure_ascii=False, indent=2))
    return 0 if estado["pronto"] or args.check_only else 1


if __name__ == "__main__":
    sys.exit(main())
