#!/usr/bin/env python3
"""descobrir_cortes.py — descobre os SEGMENTOS de um projeto (N pastas, nomes livres).

Uma "peça" final é a concatenação ordenada de um corte de cada segmento escolhido:
gancho → desenvolvimento → CTA, ou para uma VSL lead → história → oferta →
fechamento, ou qualquer cadeia que o usuário montar. Cada SEGMENTO é uma subpasta
da pasta-projeto.

A skill NÃO trava em GANCHOS/DESENVOLVIMENTOS. Ela:
  - varre a pasta-projeto e lista TODAS as subpastas que contêm vídeo (candidatas
    a segmento);
  - marca quais batem com os nomes-padrão conhecidos (GANCHOS, DESENVOLVIMENTOS,
    CTAS, LEAD, OFERTA...) só para sugerir e ordenar — não para restringir;
  - ou, se o usuário passar --segmentos com uma lista ORDENADA de caminhos, usa
    exatamente esses, na ordem dada (essa ordem é a ordem de concatenação).

Para cada corte extrai o CÓDIGO (ex.: VAV19) do nome do arquivo. O código serve
para (a) a nomenclatura de saída e (b) casar os pares NATIVOS — cortes de
segmentos diferentes que compartilham o mesmo código vieram do mesmo vídeo de
origem.

Uso:
    python3 descobrir_cortes.py <pasta_projeto>
        [--segmentos <dir1> <dir2> ...]   # lista ordenada explícita; nomes livres

Saída (stdout): JSON
    {
      "projeto": "...",
      "segmentos": [
        {"nome": "GANCHOS", "dir": "...", "padrao_conhecido": "gancho",
         "cortes": [{"codigo": "VAV19", "arquivo": "..."}]},
        ...
      ],
      "subpastas_ignoradas": [...]   # subpastas sem vídeo (só quando auto-descobre)
    }
A ORDEM da lista "segmentos" é a ordem de concatenação proposta.
"""
import argparse
import json
import os
import re
import sys

VIDEO_EXT = {".mp4", ".mov", ".mkv", ".m4v", ".avi", ".webm"}

# nomes-padrão conhecidos -> rótulo singular (só para SUGERIR; não restringe).
PADROES_CONHECIDOS = {
    "GANCHO": "gancho", "GANCHOS": "gancho",
    "DESENVOLVIMENTO": "desenvolvimento", "DESENVOLVIMENTOS": "desenvolvimento",
    "CTA": "cta", "CTAS": "cta",
    "LEAD": "lead", "LEADS": "lead",
    "HISTORIA": "historia", "HISTORIAS": "historia",
    "OFERTA": "oferta", "OFERTAS": "oferta",
    "FECHAMENTO": "fechamento", "FECHAMENTOS": "fechamento",
    "PROVA": "prova", "PROVAS": "prova",
}

# ordem retórica natural para ordenar os segmentos auto-descobertos.
ORDEM_RETORICA = ["gancho", "lead", "desenvolvimento", "historia",
                  "prova", "oferta", "cta", "fechamento"]

RE_CODIGO = re.compile(r"[A-Z]{2,5}\d{1,4}", re.IGNORECASE)


def extrair_codigo(base):
    m = RE_CODIGO.search(base)
    return m.group(0).upper() if m else base


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


def padrao_de(nome_pasta):
    return PADROES_CONHECIDOS.get(nome_pasta.upper())


def montar_segmento(caminho_pasta):
    nome = os.path.basename(os.path.normpath(caminho_pasta))
    return {
        "nome": nome,
        "dir": os.path.abspath(caminho_pasta),
        "padrao_conhecido": padrao_de(nome),  # None se for nome livre
        "cortes": listar_cortes(caminho_pasta),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("projeto")
    ap.add_argument("--segmentos", nargs="+",
                    help="lista ORDENADA de pastas-segmento (nomes livres); "
                         "a ordem é a ordem de concatenação")
    args = ap.parse_args()

    projeto = os.path.abspath(args.projeto)
    if not os.path.isdir(projeto):
        print(json.dumps({"erro": f"pasta não existe: {projeto}"}))
        sys.exit(1)

    ignoradas = []

    if args.segmentos:
        # caminhos explícitos: relativos resolvem dentro do projeto.
        segmentos = []
        for s in args.segmentos:
            p = s if os.path.isabs(s) else os.path.join(projeto, s)
            if not os.path.isdir(p):
                print(json.dumps({"erro": f"segmento não é pasta: {p}"}))
                sys.exit(1)
            segmentos.append(montar_segmento(p))
    else:
        # auto-descoberta: toda subpasta com vídeo é um segmento candidato.
        segmentos = []
        for entry in sorted(os.listdir(projeto)):
            p = os.path.join(projeto, entry)
            if not os.path.isdir(p) or entry.startswith("."):
                continue
            seg = montar_segmento(p)
            if seg["cortes"]:
                segmentos.append(seg)
            else:
                ignoradas.append(entry)

        def chave(seg):
            pk = seg["padrao_conhecido"]
            return (ORDEM_RETORICA.index(pk) if pk in ORDEM_RETORICA else 99,
                    seg["nome"].upper())
        segmentos.sort(key=chave)

    print(json.dumps({
        "projeto": projeto,
        "segmentos": segmentos,
        "subpastas_ignoradas": ignoradas,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
