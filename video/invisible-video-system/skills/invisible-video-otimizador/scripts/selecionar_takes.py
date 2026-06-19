#!/usr/bin/env python3
"""selecionar_takes.py — acha takes repetidas numa transcrição e marca o que descartar.

Um bruto de gancho costuma ter VÁRIAS tentativas (takes) da mesma fala: a pessoa
erra no meio, volta, repete. Este script lê o JSON do WhisperX (segments com
timestamp por palavra) e detecta esses grupos de takes pelo TEXTO — sem o usuário
informar a frase. O critério de seleção é sempre a ÚLTIMA take: mantém a última de
cada grupo e marca as anteriores para descarte (corte de conteúdo, não de silêncio).

Como agrupa:
  1. Quebra a transcrição em BLOCOS de fala — sequências de palavras separadas por
     uma pausa >= --gap (uma pausa longa marca o fim de uma tentativa e o começo de
     outra). Cada bloco tem (inicio, fim, texto).
  2. Compara os blocos par a par pelo texto normalizado (difflib.SequenceMatcher).
     Blocos com similaridade >= --sim são a MESMA fala repetida (takes).
  3. Em cada grupo de takes (>= 2 blocos), mantém o de maior `inicio` (a última) e
     marca os intervalos dos anteriores como descartar.

Agrupamento transitivo: se A~B e B~C, então A,B,C são o mesmo grupo (mantém C).

NÃO toca no vídeo. Só devolve os intervalos a descartar — quem corta é o otimizar.py
(no mesmo filter_complex do corte de silêncio). O original nunca é alterado.

Uso:
    python3 selecionar_takes.py <json_whisperx> [--gap 0.6] [--sim 0.75] [--min-palavras 4]

Saída (stdout): JSON {
  "blocos": [...], "grupos": [...], "descartar": [(ini,fim),...], "relatorio": [...]
}
"""
import argparse
import json
import re
import sys
import unicodedata
from difflib import SequenceMatcher


def normalizar(texto):
    """Minúsculas, sem acento, sem pontuação, espaços colapsados — pra comparar fala."""
    t = unicodedata.normalize("NFKD", texto.lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = re.sub(r"[^\w\s]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def coletar_palavras(data):
    """Achata segments[].words[] numa lista de (inicio, fim, palavra).

    WhisperX às vezes não anota start/end numa palavra (caracteres soltos); nesse
    caso herda do vizinho pra não furar a linha do tempo.
    """
    palavras = []
    for seg in data.get("segments", []):
        for w in seg.get("words", []):
            tok = (w.get("word") or "").strip()
            if not tok:
                continue
            ini = w.get("start")
            fim = w.get("end")
            if ini is None or fim is None:
                # sem timestamp medido: usa o do segmento como aproximação
                ini = seg.get("start") if ini is None else ini
                fim = seg.get("end") if fim is None else fim
            if ini is None or fim is None:
                continue
            palavras.append((float(ini), float(fim), tok))
    palavras.sort(key=lambda p: p[0])
    return palavras


def montar_blocos(palavras, gap):
    """Agrupa palavras em blocos de fala; uma pausa >= gap quebra o bloco."""
    if not palavras:
        return []
    blocos = []
    cur = [palavras[0]]
    for ant, atual in zip(palavras, palavras[1:]):
        pausa = atual[0] - ant[1]
        if pausa >= gap:
            blocos.append(cur)
            cur = [atual]
        else:
            cur.append(atual)
    blocos.append(cur)

    out = []
    for grupo in blocos:
        ini = grupo[0][0]
        fim = grupo[-1][1]
        texto = " ".join(p[2] for p in grupo)
        out.append({"inicio": ini, "fim": fim, "texto": texto,
                    "n_palavras": len(grupo), "norm": normalizar(texto)})
    return out


def agrupar_takes(blocos, sim, min_palavras):
    """Une (transitivo) blocos com texto parecido. Devolve lista de grupos (índices).

    Só considera blocos com >= min_palavras: descartar uma tentativa exige texto com
    substância, não um "é..." solto. Blocos curtos ficam sozinhos (nunca descartados).
    """
    n = len(blocos)
    pai = list(range(n))

    def raiz(i):
        while pai[i] != i:
            pai[i] = pai[pai[i]]
            i = pai[i]
        return i

    def unir(i, j):
        pai[raiz(i)] = raiz(j)

    for i in range(n):
        if blocos[i]["n_palavras"] < min_palavras:
            continue
        for j in range(i + 1, n):
            if blocos[j]["n_palavras"] < min_palavras:
                continue
            r = SequenceMatcher(None, blocos[i]["norm"], blocos[j]["norm"]).ratio()
            if r >= sim:
                unir(i, j)

    grupos = {}
    for i in range(n):
        if blocos[i]["n_palavras"] < min_palavras:
            continue
        grupos.setdefault(raiz(i), []).append(i)
    # só grupos com repetição de verdade (>= 2 takes)
    return [sorted(idxs) for idxs in grupos.values() if len(idxs) >= 2]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("json_whisperx")
    ap.add_argument("--gap", type=float, default=0.6,
                    help="pausa (s) que separa uma take da outra")
    ap.add_argument("--sim", type=float, default=0.75,
                    help="similaridade de texto (0-1) pra tratar como mesma fala")
    ap.add_argument("--min-palavras", type=int, default=4,
                    help="bloco com menos palavras que isso nunca é descartado")
    args = ap.parse_args()

    try:
        with open(args.json_whisperx, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(json.dumps({"erro": f"não li o JSON: {e}"}, ensure_ascii=False))
        sys.exit(1)

    palavras = coletar_palavras(data)
    blocos = montar_blocos(palavras, args.gap)
    grupos = agrupar_takes(blocos, args.sim, args.min_palavras)

    descartar = []
    relatorio = []
    for g in grupos:
        manter = g[-1]  # maior índice = última take na linha do tempo
        for idx in g:
            b = blocos[idx]
            if idx == manter:
                relatorio.append({"acao": "manter", "inicio": round(b["inicio"], 3),
                                  "fim": round(b["fim"], 3), "texto": b["texto"]})
            else:
                descartar.append((b["inicio"], b["fim"]))
                relatorio.append({"acao": "descartar", "inicio": round(b["inicio"], 3),
                                  "fim": round(b["fim"], 3), "texto": b["texto"]})

    descartar.sort()
    print(json.dumps({
        "blocos": [{"inicio": round(b["inicio"], 3), "fim": round(b["fim"], 3),
                    "n_palavras": b["n_palavras"], "texto": b["texto"]} for b in blocos],
        "n_grupos_repetidos": len(grupos),
        "descartar": [[round(a, 3), round(b, 3)] for a, b in descartar],
        "relatorio": relatorio,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
