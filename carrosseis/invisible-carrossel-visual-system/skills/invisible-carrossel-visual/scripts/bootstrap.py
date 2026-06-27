#!/usr/bin/env python3
"""bootstrap.py — resolve os DOIS MOTORES de render e reporta o estado de cada um.

Esta skill tem dois motores, escolhidos pelo `motor:` do `_ESTILO.md`:
  - motor HTML       -> precisa de um Chrome/Chromium (headless). Grátis, sem login.
  - motor Higgsfield -> precisa do Higgsfield CLI instalado e logado (consome créditos).

O bootstrap NÃO falha se só um motor estiver disponível: você só precisa do motor
que o estilo escolhido pede. Ele reporta o que está pronto e instrui o que falta.

Uso:
    python3 bootstrap.py

Saída (stdout): JSON com `html` {pronto, chrome_bin} e
`higgsfield` {pronto, bin, logado, creditos, status_texto}, mais `instrucoes`.
"""
import json
import os
import re
import shutil
import subprocess
import sys


def achar_chrome():
    candidatos = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    ]
    for c in candidatos:
        if os.path.exists(c):
            return c
    for nome in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome"):
        p = shutil.which(nome)
        if p:
            return p
    return None


def account_status():
    """Retorna (logado, texto, creditos|None) do Higgsfield CLI."""
    try:
        r = subprocess.run(["higgsfield", "account", "status"],
                           capture_output=True, text=True, timeout=30)
    except Exception as e:
        return False, f"erro ao rodar account status: {e}", None
    txt = ((r.stdout or "") + (r.stderr or "")).strip()
    logado = r.returncode == 0 and "@" in txt
    creditos = None
    m = re.search(r"(\d+)\s*credit", txt, re.IGNORECASE)
    if m:
        creditos = int(m.group(1))
    return logado, txt, creditos


def main():
    out = {"html": {}, "higgsfield": {}, "instrucoes": []}

    # --- motor HTML ---
    chrome = achar_chrome()
    out["html"] = {"pronto": chrome is not None, "chrome_bin": chrome}
    if not chrome:
        out["instrucoes"].append(
            "Motor HTML: Chrome/Chromium não encontrado. Instale o Google Chrome "
            "(ou passe --chrome <caminho> ao render_html.py)."
        )

    # --- motor Higgsfield ---
    hbin = shutil.which("higgsfield")
    hf = {"pronto": False, "bin": hbin, "logado": False, "creditos": None, "status_texto": None}
    if not hbin:
        out["instrucoes"].append(
            "Motor Higgsfield: CLI não encontrada. Instale com 'npm install -g @higgsfield/cli' "
            "e faça login com 'higgsfield auth login' (só necessário para estilos com imagem gerada)."
        )
    else:
        logado, txt, creditos = account_status()
        hf.update({"logado": logado, "status_texto": txt, "creditos": creditos, "pronto": logado})
        if not logado:
            out["instrucoes"].append("Motor Higgsfield: CLI instalada mas não logada. 'higgsfield auth login'.")
        elif creditos is not None and creditos < 20:
            out["instrucoes"].append(f"Motor Higgsfield: só {creditos} créditos restantes; recarregue antes de gerar em lote.")
    out["higgsfield"] = hf

    # pronto geral = pelo menos um motor disponível
    out["algum_motor_pronto"] = out["html"]["pronto"] or hf["pronto"]
    print(json.dumps(out, ensure_ascii=False, indent=2))
    sys.exit(0 if out["algum_motor_pronto"] else 1)


if __name__ == "__main__":
    main()
