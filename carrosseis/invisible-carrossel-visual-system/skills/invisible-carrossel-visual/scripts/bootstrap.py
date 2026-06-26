#!/usr/bin/env python3
"""bootstrap.py — resolve o Higgsfield CLI e reporta estado + créditos.

O motor de render desta skill é o Higgsfield CLI (gpt_image_2). Ao contrário das
skills de vídeo, não há venv pesado: só precisamos do CLI instalado e logado.

Resolução:
  1. `higgsfield` no PATH → ok.
  2. ausente → instrui a instalar (`npm install -g @higgsfield/cli` + `higgsfield auth login`).

Também lê `higgsfield account status` para reportar o plano e os CRÉDITOS restantes,
porque cada slide consome créditos e a skill avisa o usuário antes de gerar em lote.

Uso:
    python3 bootstrap.py [--check-only]

Saída (stdout): JSON com `pronto`, `higgsfield_bin`, `logado`, `creditos`, `instrucoes`.
"""
import argparse
import json
import re
import shutil
import subprocess
import sys


def existe(bin_):
    return shutil.which(bin_) is not None


def account_status():
    """Retorna (logado: bool, texto: str, creditos: int|None)."""
    try:
        r = subprocess.run(
            ["higgsfield", "account", "status"],
            capture_output=True, text=True, timeout=30,
        )
    except Exception as e:
        return False, f"erro ao rodar account status: {e}", None
    txt = (r.stdout or "") + (r.stderr or "")
    txt = txt.strip()
    logado = r.returncode == 0 and "@" in txt
    creditos = None
    m = re.search(r"(\d+)\s*credit", txt, re.IGNORECASE)
    if m:
        creditos = int(m.group(1))
    return logado, txt, creditos


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check-only", action="store_true",
                    help="só checa, não tenta instalar nada")
    args = ap.parse_args()

    out = {
        "pronto": False,
        "higgsfield_bin": None,
        "logado": False,
        "creditos": None,
        "status_texto": None,
        "instrucoes": [],
    }

    bin_ = shutil.which("higgsfield")
    out["higgsfield_bin"] = bin_

    if not bin_:
        out["instrucoes"] = [
            "Higgsfield CLI não encontrado no PATH.",
            "Instale: npm install -g @higgsfield/cli",
            "Faça login: higgsfield auth login",
            "Confira: higgsfield account status",
        ]
        print(json.dumps(out, ensure_ascii=False, indent=2))
        sys.exit(1)

    logado, txt, creditos = account_status()
    out["logado"] = logado
    out["status_texto"] = txt
    out["creditos"] = creditos

    if not logado:
        out["instrucoes"] = [
            "Higgsfield CLI instalado mas não logado.",
            "Faça login: higgsfield auth login",
        ]
        print(json.dumps(out, ensure_ascii=False, indent=2))
        sys.exit(1)

    out["pronto"] = True
    if creditos is not None and creditos < 20:
        out["instrucoes"] = [
            f"Atenção: só {creditos} créditos restantes. "
            "Cada slide consome créditos; recarregue se for gerar em lote."
        ]
    print(json.dumps(out, ensure_ascii=False, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
