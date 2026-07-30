#!/usr/bin/env python3
"""Bootstrap da invisible-video-painel-animado.

Monta o que a skill precisa fora do plugin (portável):
1. Projeto Remotion de painéis em ~/.invisible-video/painel-animado-remotion
   (copia o template `remotion/` da skill e instala node_modules).
2. Venv rembg em ~/.invisible-video/rembgenv (recorte de fundo → alpha real),
   com o modelo u2net baixado no primeiro uso.
3. Checa ffmpeg/ffprobe (usados pela inserção).

A GERAÇÃO da imagem do personagem depende do MCP Artlist (sessão conectada) —
o bootstrap não consegue checá-lo; apenas avisa.

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
REMOTION_DST = os.path.join(BASE, "painel-animado-remotion")
REMBG_VENV = os.path.join(BASE, "rembgenv")
SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REMOTION_SRC = os.path.join(SKILL_DIR, "remotion")


def have(b):
    return shutil.which(b) is not None


def instalar_remotion():
    os.makedirs(BASE, exist_ok=True)
    # copia src/, package.json, config, tsconfig (não copia node_modules/out)
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
    # instala deps se faltar
    if not os.path.isdir(os.path.join(REMOTION_DST, "node_modules", "remotion")):
        npm = shutil.which("npm")
        if npm:
            subprocess.run([npm, "install", "--no-audit", "--no-fund"], cwd=REMOTION_DST, check=False)


def instalar_rembg():
    if os.path.isdir(REMBG_VENV):
        return
    py = shutil.which("python3") or sys.executable
    subprocess.run([py, "-m", "venv", REMBG_VENV], check=False)
    pip = os.path.join(REMBG_VENV, "bin", "pip")
    if os.path.exists(pip):
        subprocess.run([pip, "install", "--quiet", "--upgrade", "pip"], check=False)
        subprocess.run([pip, "install", "--quiet", "rembg[cpu]", "onnxruntime", "pillow", "numpy"], check=False)


def estado():
    node_ok = os.path.isdir(os.path.join(REMOTION_DST, "node_modules", "remotion"))
    rembg_py = os.path.join(REMBG_VENV, "bin", "python")
    rembg_ok = os.path.exists(rembg_py)
    return {
        "remotion_project": REMOTION_DST,
        "remotion_instalado": node_ok,
        "rembg_venv": REMBG_VENV,
        "rembg_python": rembg_py if rembg_ok else None,
        "rembg_instalado": rembg_ok,
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
        instalar_rembg()
        if not (have("ffmpeg") and have("ffprobe")) and have("brew"):
            subprocess.run(["brew", "install", "ffmpeg"], check=False)

    e = estado()
    e["pronto"] = e["remotion_instalado"] and e["rembg_instalado"] and e["ffmpeg"] and e["ffprobe"]
    e["nota_artlist"] = (
        "A geração da imagem do personagem usa o MCP Artlist (GPT Image 2), que só "
        "existe em sessão Claude conectada. O recorte (rembg), a composição (Remotion) "
        "e a inserção rodam sem ele."
    )
    if not e["pronto"]:
        e["dica"] = "Rode sem --check-only para instalar o que falta."
    print(json.dumps(e, ensure_ascii=False, indent=2))
    return 0 if e["pronto"] else 1


if __name__ == "__main__":
    sys.exit(main())
