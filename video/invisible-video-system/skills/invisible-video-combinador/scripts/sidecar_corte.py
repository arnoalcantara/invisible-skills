#!/usr/bin/env python3
"""sidecar_corte.py — gera o sidecar .md de UM corte a partir da transcrição.

Fallback do combinador: quando um corte chega SEM .md ao lado (não passou pelo
desmembrador, que escreve o roteiro), a skill já transcreve esse corte para
julgar o encaixe retórico. Este utilitário pega esse JSON do WhisperX e grava o
`<corte>.md` com o rótulo do segmento + o texto transcrito — assim o corte passa
a ter sidecar para as próximas combinações (não se re-transcreve depois).

O texto vem cru da transcrição (menos pontuado que um roteiro). É o melhor
disponível quando não há roteiro; o MD nascido do desmembrador é preferível.

Uso:
    python3 sidecar_corte.py --json <wx.json> --rotulo GANCHO --out <corte>.md

Saída (stdout): JSON {"md": "<caminho>", "chars": N} ou {"erro": ...}
"""
import argparse
import json
import os
import re
import sys


def texto_da_transcricao(data):
    """Junta os segments[].text do WhisperX num texto contínuo e limpo."""
    partes = [(s.get("text") or "").strip() for s in data.get("segments", [])]
    texto = " ".join(p for p in partes if p)
    return re.sub(r"\s+", " ", texto).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", required=True, help="JSON do WhisperX (transcrição)")
    ap.add_argument("--rotulo", required=True, help="rótulo da seção, ex.: GANCHO")
    ap.add_argument("--out", required=True, help="caminho do .md a gravar")
    args = ap.parse_args()

    try:
        with open(args.json, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(json.dumps({"erro": f"json inválido: {e}"}))
        sys.exit(1)

    texto = texto_da_transcricao(data)
    if not texto:
        print(json.dumps({"erro": "transcrição sem texto"}))
        sys.exit(1)

    rotulo = args.rotulo.strip().upper()
    out = os.path.abspath(args.out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(f"# {rotulo}\n\n{texto}\n")

    print(json.dumps({"md": out, "chars": len(texto)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
