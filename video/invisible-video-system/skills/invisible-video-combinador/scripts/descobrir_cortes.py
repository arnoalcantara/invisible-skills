#!/usr/bin/env python3
"""descobrir_cortes.py — acha os ganchos e desenvolvimentos de um projeto.

Varre a pasta do projeto procurando as pastas GANCHOS/ e DESENVOLVIMENTOS/
(produzidas pela invisible-video-bruto-desmembrador) e lista os vídeos de cada
lado. Tolerante a nomes alternativos (singular, com acento) e a caminhos dados
explicitamente pelo usuário.

Extrai o código de cada corte (ex.: VAV19, VAV23) do nome do arquivo, para a
matriz e a nomenclatura de saída. Se não houver código reconhecível, usa o nome
sem extensão como rótulo.

Uso:
    python3 descobrir_cortes.py <pasta_projeto>
        [--ganchos <dir>] [--desenvolvimentos <dir>]

Saída (stdout): JSON
    {"ganchos": [{"codigo","arquivo"}], "desenvolvimentos": [{"codigo","arquivo"}]}
"""
import argparse
import json
import os
import re
import sys

VIDEO_EXT = {".mp4", ".mov", ".mkv", ".m4v", ".avi", ".webm"}

# nomes aceitos para cada lado, em ordem de preferência
NOMES_GANCHOS = ["GANCHOS", "GANCHO", "Ganchos", "ganchos"]
NOMES_DESENV = ["DESENVOLVIMENTOS", "DESENVOLVIMENTO", "Desenvolvimentos",
                "desenvolvimentos"]

# código tipo VAV19, VAV123 — letras seguidas de dígitos
RE_CODIGO = re.compile(r"[A-Z]{2,5}\d{1,4}", re.IGNORECASE)


def achar_subpasta(projeto, candidatos):
    for nome in candidatos:
        caminho = os.path.join(projeto, nome)
        if os.path.isdir(caminho):
            return caminho
    return None


def extrair_codigo(base):
    m = RE_CODIGO.search(base)
    if m:
        return m.group(0).upper()
    return base


def listar_cortes(pasta):
    cortes = []
    if not pasta or not os.path.isdir(pasta):
        return cortes
    for entry in sorted(os.listdir(pasta)):
        caminho = os.path.join(pasta, entry)
        if not os.path.isfile(caminho) or entry.startswith("."):
            continue
        base, ext = os.path.splitext(entry)
        if ext.lower() not in VIDEO_EXT:
            continue
        cortes.append({"codigo": extrair_codigo(base), "arquivo": caminho})
    return cortes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("projeto")
    ap.add_argument("--ganchos", help="caminho explícito da pasta de ganchos")
    ap.add_argument("--desenvolvimentos",
                    help="caminho explícito da pasta de desenvolvimentos")
    args = ap.parse_args()

    projeto = os.path.abspath(args.projeto)
    if not os.path.isdir(projeto):
        print(json.dumps({"erro": f"pasta não existe: {projeto}"}))
        sys.exit(1)

    dir_ganchos = (os.path.abspath(args.ganchos) if args.ganchos
                   else achar_subpasta(projeto, NOMES_GANCHOS))
    dir_desenv = (os.path.abspath(args.desenvolvimentos)
                  if args.desenvolvimentos
                  else achar_subpasta(projeto, NOMES_DESENV))

    ganchos = listar_cortes(dir_ganchos)
    desenvolvimentos = listar_cortes(dir_desenv)

    print(json.dumps({
        "projeto": projeto,
        "dir_ganchos": dir_ganchos,
        "dir_desenvolvimentos": dir_desenv,
        "ganchos": ganchos,
        "desenvolvimentos": desenvolvimentos,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
