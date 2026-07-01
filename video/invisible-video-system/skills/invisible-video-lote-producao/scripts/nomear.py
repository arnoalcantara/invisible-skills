#!/usr/bin/env python3
"""nomear.py — etapa 7 da esteira: renomeia os finalizados de 99_FINALIZADOS
in-place, prefixando <prefixo><contador> em ordem crescente.

É a ÚLTIMA etapa. Roda depois da trilha, quando 99_FINALIZADOS já tem os
`*_FINALIZADO.mp4`. Prefixa cada nome com `<prefixo><n>_`, com `n` crescente a
partir de `--inicio`. O sufixo original (`..._FINALIZADO.mp4`) é PRESERVADO — o
prefixo só entra na frente. Assim o gate da etapa 6 (trilha) continua válido e o
histórico do arquivo permanece legível.

A ORDEM da numeração é decisão do plano (leva por leva, etc.). Por isso o script
NÃO adivinha a ordem: recebe a lista JÁ ORDENADA de arquivos (--arquivos, um por
linha, ou --ordem-json com uma lista). O maestro (invisible-video-lote-producao)
monta essa ordem lendo o PLAN_LOTE.md e a passa aqui. Sem --arquivos/--ordem-json,
cai na ordem alfabética do nome como fallback (previsível, mas burra).

Idempotência: um arquivo que já começa com `<prefixo>` é considerado JÁ NOMEADO e
é pulado (não re-prefixa). Assim re-rodar a etapa não empilha prefixos.

Uso:
    python3 nomear.py "<lote>/99_FINALIZADOS" --prefixo "DME_VAV" --inicio 252 \
        [--arquivos lista.txt | --ordem-json ordem.json] [--dry-run]
Saída (stdout): JSON {"renomeados": [{"de":..., "para":...}], "pulados": [...], "total": N}
"""
from __future__ import annotations

import argparse
import json
import os
import sys

VIDEO_EXT = {".mp4", ".mov", ".mkv", ".m4v", ".webm"}


def finalizados(pasta: str) -> list[str]:
    return sorted(
        f for f in os.listdir(pasta)
        if os.path.splitext(f)[1].lower() in VIDEO_EXT
        and "_FINALIZADO" in f.upper()
        and not f.startswith(".")
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("pasta", help="99_FINALIZADOS do lote")
    ap.add_argument("--prefixo", required=True, help="prefixo dos nomes finais, ex.: DME_VAV")
    ap.add_argument("--inicio", type=int, default=1, help="primeiro número da sequência")
    ap.add_argument("--arquivos", help="txt com a ordem dos arquivos (um nome por linha)")
    ap.add_argument("--ordem-json", help="JSON com lista ordenada de nomes de arquivo")
    ap.add_argument("--dry-run", action="store_true", help="só mostra o plano, não renomeia")
    args = ap.parse_args()

    if not os.path.isdir(args.pasta):
        print(json.dumps({"erro": f"pasta não existe: {args.pasta}"}, ensure_ascii=False))
        return 1

    presentes = finalizados(args.pasta)
    if not presentes:
        print(json.dumps({"erro": "nenhum *_FINALIZADO em 99_FINALIZADOS"}, ensure_ascii=False))
        return 1

    # ordem: --arquivos ou --ordem-json têm prioridade; fallback = alfabética
    ordem: list[str] = []
    if args.ordem_json:
        with open(args.ordem_json, encoding="utf-8") as f:
            ordem = list(json.load(f))
    elif args.arquivos:
        with open(args.arquivos, encoding="utf-8") as f:
            ordem = [ln.strip() for ln in f if ln.strip()]
    else:
        ordem = presentes  # já vem sorted()

    # valida que a ordem cobre exatamente os finalizados presentes (basename)
    ordem = [os.path.basename(x) for x in ordem]
    faltando = [f for f in presentes if f not in ordem]
    sobrando = [f for f in ordem if f not in presentes]
    if faltando or sobrando:
        print(json.dumps({
            "erro": "a ordem não bate com os arquivos presentes",
            "faltando_na_ordem": faltando,
            "sobrando_na_ordem": sobrando,
        }, ensure_ascii=False))
        return 2

    renomeados, pulados = [], []
    n = args.inicio
    for nome in ordem:
        if nome.startswith(args.prefixo):
            pulados.append(nome)  # já nomeado; não consome contador, não re-prefixa
            continue
        novo = f"{args.prefixo}{n}_{nome}"
        de = os.path.join(args.pasta, nome)
        para = os.path.join(args.pasta, novo)
        if os.path.exists(para):
            print(json.dumps({"erro": f"destino já existe: {novo}"}, ensure_ascii=False))
            return 3
        if not args.dry_run:
            os.rename(de, para)
        renomeados.append({"de": nome, "para": novo})
        n += 1

    print(json.dumps({
        "renomeados": renomeados,
        "pulados": pulados,
        "total": len(renomeados),
        "dry_run": args.dry_run,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
