#!/usr/bin/env python3
"""combinar.py — concatena gancho + desenvolvimento já normalizados.

Recebe dois (ou mais) cortes que JÁ passaram pela normalizar.py (mesmas specs) e
os junta por `concat -c copy` via demuxer de lista. Sem reencode: rápido e sem
perda. Falha de propósito se as specs divergirem — é sinal de que a normalização
não rodou antes.

Uso:
    python3 combinar.py --out <saida.mp4> <parte1> <parte2> [<parte3> ...]

Saída (stdout): JSON {"arquivo": "<saida>"} ou {"erro": ...}
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("partes", nargs="+", help="cortes normalizados, na ordem")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    partes = [os.path.abspath(p) for p in args.partes]
    for p in partes:
        if not os.path.isfile(p):
            print(json.dumps({"erro": f"parte não existe: {p}"}))
            sys.exit(1)

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)

    # demuxer concat: lista de arquivos. Caminhos com aspas simples escapadas.
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False,
                                     encoding="utf-8") as lst:
        for p in partes:
            seguro = p.replace("'", r"'\''")
            lst.write(f"file '{seguro}'\n")
        lista = lst.name

    try:
        cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0",
               "-i", lista, "-c", "copy", os.path.abspath(args.out)]
        proc = subprocess.run(cmd, capture_output=True, text=True)
    finally:
        os.unlink(lista)

    if proc.returncode != 0:
        print(json.dumps({
            "erro": "ffmpeg concat falhou (specs divergentes? normalize antes)",
            "stderr": proc.stderr[-1500:]}, ensure_ascii=False))
        sys.exit(1)

    print(json.dumps({"arquivo": os.path.abspath(args.out)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
