#!/usr/bin/env python3
"""Bootstrap da invisible-video-titulo-gancho.

Monta o que a skill precisa fora do plugin (portável):
1. Projeto Remotion do overlay de título em ~/.invisible-video/titulo-gancho-remotion
   (copia o template `remotion/` da skill e instala node_modules).
2. Checa ffmpeg/ffprobe (usados pela sobreposição do overlay no gancho).

Uso:
    python3 scripts/bootstrap.py --check-only   # relata estado (JSON)
    python3 scripts/bootstrap.py                # instala o que faltar
"""
import json
import os
import shutil
import subprocess
import sys

HOME = os.path.expanduser("~")
BASE = os.path.join(HOME, ".invisible-video")
REMOTION_DST = os.path.join(BASE, "titulo-gancho-remotion")
SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REMOTION_SRC = os.path.join(SKILL_DIR, "remotion")


def have(b):
    return shutil.which(b) is not None


def instalar_remotion():
    os.makedirs(BASE, exist_ok=True)
    if not os.path.isdir(REMOTION_DST):
        os.makedirs(REMOTION_DST, exist_ok=True)
    for item in ("src", "package.json", "remotion.config.ts", "tsconfig.json"):
        s = os.path.join(REMOTION_SRC, item)
        d = os.path.join(REMOTION_DST, item)
        if os.path.isdir(s):
            if os.path.isdir(d):
                shutil.rmtree(d)
            shutil.copytree(s, d)
        elif os.path.isfile(s):
            shutil.copy2(s, d)
    os.makedirs(os.path.join(REMOTION_DST, "public"), exist_ok=True)
    if not os.path.isdir(os.path.join(REMOTION_DST, "node_modules", "remotion")):
        npm = shutil.which("npm")
        if npm:
            subprocess.run([npm, "install", "--no-audit", "--no-fund"], cwd=REMOTION_DST, check=False)


def estado():
    node_ok = os.path.isdir(os.path.join(REMOTION_DST, "node_modules", "remotion"))
    return {
        "remotion_project": REMOTION_DST,
        "remotion_instalado": node_ok,
        "ffmpeg": have("ffmpeg"),
        "ffprobe": have("ffprobe"),
        "node": have("node"),
        "npm": have("npm"),
    }


def main():
    check_only = "--check-only" in sys.argv
    if not check_only:
        if not (have("node") and have("npm")):
            print(json.dumps({"erro": "Node.js e npm são necessários. Instale antes (brew install node)."}, ensure_ascii=False))
            return 1
        instalar_remotion()
        if not (have("ffmpeg") and have("ffprobe")) and have("brew"):
            subprocess.run(["brew", "install", "ffmpeg"], check=False)

    e = estado()
    e["pronto"] = e["remotion_instalado"] and e["ffmpeg"] and e["ffprobe"]
    if not e["pronto"]:
        e["dica"] = "Rode sem --check-only para instalar o que falta."
    print(json.dumps(e, ensure_ascii=False, indent=2))
    return 0 if e["pronto"] else 1


if __name__ == "__main__":
    sys.exit(main())
