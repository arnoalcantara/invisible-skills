#!/usr/bin/env python3
"""combinar.py — concatena gancho + desenvolvimento já normalizados.

Recebe dois (ou mais) cortes que JÁ passaram pela normalizar.py (mesmas specs) e
os junta por `concat -c copy` via demuxer de lista. Sem reencode: rápido e sem
perda. Falha de propósito se as specs divergirem — é sinal de que a normalização
não rodou antes.

Uso:
    python3 combinar.py --out <saida.mp4> <parte1> <parte2> [<parte3> ...]
    # opcional: junta também os sidecars de roteiro, na MESMA ordem das partes
    python3 combinar.py --out <saida.mp4> <p1> <p2> \
        --sidecars <p1.md> <p2.md> --out-md <saida.md>

Saída (stdout): JSON {"arquivo": "<saida>", "md": "<saida.md>"|null} ou {"erro": ...}
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile


def juntar_sidecars(sidecars, out_md):
    """Concatena os .md dos cortes (na ordem) num único .md da combinação.

    Cada sidecar já é `# SEÇÃO\\n\\n<texto>`; basta emendá-los em sequência. Sem
    tempos/offsets (decisão de projeto): a marcação por tempo nasce na legendagem,
    casando este texto contra a transcrição do vídeo já editado. Sidecar ausente
    é registrado, não interrompe."""
    blocos, faltando = [], []
    for md in sidecars:
        if md and os.path.isfile(md):
            with open(md, encoding="utf-8") as f:
                blocos.append(f.read().strip())
        else:
            faltando.append(md)
    if not blocos:
        return {"md": None, "faltando": faltando}
    with open(out_md, "w", encoding="utf-8") as f:
        f.write("\n\n".join(blocos) + "\n")
    return {"md": os.path.abspath(out_md), "faltando": faltando}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("partes", nargs="+", help="cortes normalizados, na ordem")
    ap.add_argument("--out", required=True)
    ap.add_argument("--sidecars", nargs="*", default=None,
                    help="sidecars .md dos cortes, na MESMA ordem das partes")
    ap.add_argument("--out-md", help="caminho do .md da combinação")
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

    resultado = {"arquivo": os.path.abspath(args.out)}

    # roteiro da combinação: junta os sidecars na ordem das partes
    if args.sidecars:
        out_md = args.out_md or (os.path.splitext(os.path.abspath(args.out))[0] + ".md")
        r = juntar_sidecars([os.path.abspath(m) for m in args.sidecars], out_md)
        resultado["md"] = r["md"]
        if r["faltando"]:
            resultado["sidecars_faltando"] = r["faltando"]
    else:
        resultado["md"] = None

    print(json.dumps(resultado, ensure_ascii=False))


if __name__ == "__main__":
    main()
