#!/usr/bin/env python3
"""pipeline.py — orquestra o desmembramento por etapas, emitindo JSON por fase.

Não é interativo: cada etapa imprime JSON e para. Quem conduz a conversa (a
skill) lê a saída, confirma com o usuário e chama a próxima etapa. Isso mantém
os pontos de confirmação no controle do agente, não enterrados no script.

Etapas:
    descobrir   <pasta>                              → pares + órfãos
    parse       <roteiro>                            → seções
    transcrever <video> --venv --cache-dir           → json_path
    bordas      <video> <transcricao> <secoes>       → cortes
    cortar      <video> <cortes> --out-base          → arquivos gerados

Para conveniência também há:
    auto <pasta> --venv --cache-dir   → roda descobrir+parse de todos os pares
                                        (sem cortar; para revisão de uma vez)

Os scripts individuais existem e podem ser chamados direto; este é o atalho.
"""
import argparse
import json
import os
import subprocess
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))


def rodar(script, *a):
    cmd = [sys.executable, os.path.join(AQUI, script), *a]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        return {"erro": f"{script} falhou", "stderr": proc.stderr[-1500:], "stdout": proc.stdout[-1500:]}
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return {"erro": f"{script} não retornou JSON", "stdout": proc.stdout[-1500:]}


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("descobrir"); p.add_argument("pasta"); p.add_argument("--brutas-subdir", default="BRUTAS")
    p = sub.add_parser("parse"); p.add_argument("roteiro")
    p = sub.add_parser("transcrever"); p.add_argument("video"); p.add_argument("--venv", required=True); p.add_argument("--cache-dir", required=True); p.add_argument("--model", default="large-v3"); p.add_argument("--lang", default="pt")
    p = sub.add_parser("bordas"); p.add_argument("video"); p.add_argument("transcricao"); p.add_argument("secoes"); p.add_argument("--respiro-inicio", default="0.15"); p.add_argument("--respiro-fim", default="0.30")
    p = sub.add_parser("cortar"); p.add_argument("video"); p.add_argument("cortes"); p.add_argument("--out-base", required=True); p.add_argument("--crf", default="18"); p.add_argument("--preset", default="medium")

    args = ap.parse_args()

    if args.cmd == "descobrir":
        out = rodar("descobrir_pares.py", args.pasta, "--brutas-subdir", args.brutas_subdir)
    elif args.cmd == "parse":
        out = rodar("parse_roteiro.py", args.roteiro)
    elif args.cmd == "transcrever":
        out = rodar("transcrever.py", args.video, "--venv", args.venv,
                    "--cache-dir", args.cache_dir, "--model", args.model, "--lang", args.lang)
    elif args.cmd == "bordas":
        out = rodar("achar_bordas.py", args.video, args.transcricao, args.secoes,
                    "--respiro-inicio", str(args.respiro_inicio), "--respiro-fim", str(args.respiro_fim))
    elif args.cmd == "cortar":
        out = rodar("cortar.py", args.video, args.cortes, "--out-base", args.out_base,
                    "--crf", str(args.crf), "--preset", str(args.preset))
    else:
        out = {"erro": "comando desconhecido"}

    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
