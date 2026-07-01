#!/usr/bin/env python3
"""estado_lote.py — lê o PLAN_LOTE.md e reconcilia com as pastas do lote.

Responde a pergunta "onde paramos?": qual a próxima etapa não-feita e com quais
parâmetros. A verdade do progresso são as PASTAS (não o texto do checkbox) — este
script conta o que já existe em cada pasta de saída e deriva o estado real.

Como cada etapa é detectada como "feita" (heurística por pasta/sufixo):
  1   Otimizar+Denoise  -> 02_OTIMIZADOS tem algum *_OTIMIZADO_*.mp4
  2   Transcrever       -> 02_OTIMIZADOS tem .json em número >= nº de BASES de vídeo
  3.1 Legendar          -> 03_PREPARADOS tem algum *_LEGENDADO_*.mp4
  3.2 Variações         -> 03_PREPARADOS tem algum *_VAR<n>_*.mp4 (só exigida se o plano pediu)
  4   Combinar          -> 04_COMBINADOS tem alguma combinação (nome com '__')
  5   Acelerar          -> 04_COMBINADOS tem algum *_ACELERADO_*.mp4 (só exigida se o plano pediu)
  6   Trilha            -> 99_FINALIZADOS tem algum *_FINALIZADO*.mp4
  7   Nomear            -> 99_FINALIZADOS tem *_FINALIZADO* começando com o prefixo do
                          plano (renomeação in-place; só exigida se o plano deu prefixo)

Acelerar vem ANTES da trilha de propósito: acelerar depois aceleraria a música
junto (e o atempo a tiraria do tempo). Acelerar roda em 04_COMBINADOS; a trilha
consome só os _ACELERADO_ de lá quando houve aceleração.

"feito" aqui é "começou e tem saída"; a skill filha de cada etapa é resumível e
pula o que já está pronto, então o executor pode re-rodar a etapa sem estragar nada.
A próxima etapa é a primeira (na ordem) cujo gate não está satisfeito e que não foi
pulada pelo plano.

Uso:
    python3 estado_lote.py "<dir do lote>"
Saída (stdout): JSON com decisoes, etapas (cada uma com feito/pulada/contagem) e
proxima_etapa.
"""
from __future__ import annotations

import json
import os
import re
import sys

VIDEO_EXT = {".mp4", ".mov", ".mkv", ".m4v", ".webm"}

# ordem canônica das etapas
ETAPAS = ["1", "2", "3.1", "3.2", "4", "5", "6", "7"]
ROTULOS = {
    "1": "Otimizar + Denoise",
    "2": "Transcrever",
    "3.1": "Legendar",
    "3.2": "Variações de gancho",
    "4": "Combinar",
    "5": "Acelerar",
    "6": "Trilha",
    "7": "Nomear",
}


def videos(pasta: str) -> list[str]:
    if not os.path.isdir(pasta):
        return []
    return [f for f in os.listdir(pasta)
            if os.path.splitext(f)[1].lower() in VIDEO_EXT and not f.startswith(".")]


def jsons(pasta: str) -> list[str]:
    if not os.path.isdir(pasta):
        return []
    return [f for f in os.listdir(pasta) if f.lower().endswith(".json") and not f.startswith(".")]


def parse_plan(plan_path: str) -> dict:
    """Extrai as decisões e os checkboxes pulados do PLAN_LOTE.md (parsing leve)."""
    with open(plan_path, encoding="utf-8") as f:
        txt = f.read()

    dec = {
        "estilo_legenda": "auto",
        "variacoes": [],
        "var_fonte": "padrao",
        "var_fundo": "padrao",
        "trilha_pasta": "00_Recursos/Trilhas",
        "alvo_fala": -14,
        "alvo_trilha": -37,
        "acelerar": False,
        "fator_aceleracao": 1.2,
        "nome_prefixo": "",
        "nome_inicio": 1,
    }

    # tabela de decisões: | Estilo de legenda | auto (...) |
    def linha(rotulo: str) -> str | None:
        m = re.search(rf"\|\s*{re.escape(rotulo)}\s*\|\s*(.+?)\s*\|", txt)
        return m.group(1).strip() if m else None

    v = linha("Estilo de legenda")
    if v:
        dec["estilo_legenda"] = v.split()[0]  # "auto", "reels", ...
    v = linha("Variações de gancho")
    if v and v.lower() != "nenhuma":
        dec["variacoes"] = [int(n) for n in re.findall(r"VAR(\d+)", v)]
    v = linha("Estilo do gancho escrito")
    if v and v not in ("—", "padrão (Hoefler Text, fundo preto)"):
        dec["var_custom"] = v
    v = linha("Pasta de trilha")
    if v:
        dec["trilha_pasta"] = v.strip("`")
    v = linha("Aceleração")
    if v and v.lower().startswith("sim"):
        dec["acelerar"] = True
        m = re.search(r"([\d.]+)x", v)
        if m:
            dec["fator_aceleracao"] = float(m.group(1))
    v = linha("Alvo de loudness — fala / trilha")
    if v:
        nums = re.findall(r"-?\d+", v)
        if len(nums) >= 2:
            dec["alvo_fala"], dec["alvo_trilha"] = int(nums[0]), int(nums[1])
    # Nomeação final: | Nomeação final (prefixo / início / ordem) | `DME_VAV` a partir de 252 — ... |
    # (rótulo literal — o linha() já faz re.escape internamente)
    v = linha("Nomeação final (prefixo / início / ordem)")
    if v and v.strip() != "—":
        m = re.search(r"`([^`]+)`\s*a partir de\s*(\d+)", v)
        if m:
            dec["nome_prefixo"] = m.group(1)
            dec["nome_inicio"] = int(m.group(2))

    # checkboxes pulados: linha da etapa marcada [x] que contém "pulada"
    pulados = set()
    for et in ETAPAS:
        # uma etapa está pulada se sua linha tem [x] e o texto "pulada"
        m = re.search(rf"- \[(x| )\] \*\*{re.escape(et)}[ .].*", txt)
        if m and "pulada" in m.group(0):
            pulados.add(et)

    return {"decisoes": dec, "pulados": sorted(pulados)}


def main() -> int:
    if len(sys.argv) < 2:
        print(json.dumps({"erro": "uso: estado_lote.py <dir do lote>"}, ensure_ascii=False))
        return 1
    lote = os.path.abspath(sys.argv[1])
    plan_path = os.path.join(lote, "PLAN_LOTE.md")
    if not os.path.isfile(plan_path):
        print(json.dumps({"erro": f"PLAN_LOTE.md não encontrado em {lote}"}, ensure_ascii=False))
        return 1

    parsed = parse_plan(plan_path)
    dec = parsed["decisoes"]
    pulados = set(parsed["pulados"])
    # uma etapa também é "pulada" pela lógica do plano (sem VAR / sem acelerar)
    if not dec["variacoes"]:
        pulados.add("3.2")
    if not dec["acelerar"]:
        pulados.add("5")  # acelerar é a etapa 5 (antes da trilha)
    if not dec.get("nome_prefixo"):
        pulados.add("7")  # nomear é a etapa 7 (última); sem prefixo, não roda

    d_brutas = os.path.join(lote, "01_BRUTAS")
    d_otim = os.path.join(lote, "02_OTIMIZADOS")
    d_prep = os.path.join(lote, "03_PREPARADOS")
    d_comb = os.path.join(lote, "04_COMBINADOS")
    d_fim = os.path.join(lote, "99_FINALIZADOS")

    otim_v = videos(d_otim)
    prep_v = videos(d_prep)
    comb_v = videos(d_comb)
    fim_v = videos(d_fim)

    # nº de BASES de vídeo em 02 (strip de _VERTICAL/_QUADRADO p/ contar segmentos únicos)
    bases = set()
    for f in otim_v:
        b = re.sub(r"_(VERTICAL|QUADRADO)", "", os.path.splitext(f)[0])
        bases.add(b)

    gates = {
        "1": len(otim_v) > 0,
        "2": len(jsons(d_otim)) >= len(bases) and len(bases) > 0,
        "3.1": any("_LEGENDADO" in f.upper() for f in prep_v),
        "3.2": any(re.search(r"_VAR\d+", f.upper()) for f in prep_v),
        "4": any("__" in f for f in comb_v),
        # 5 (acelerar) roda em 04_COMBINADOS, ANTES da trilha
        "5": any("_ACELERADO_" in f.upper() for f in comb_v),
        # 6 (trilha) grava em 99_FINALIZADOS com _FINALIZADO no nome
        "6": any("_FINALIZADO" in f.upper() for f in fim_v),
        # 7 (nomear) renomeia in-place: finalizados começam com o prefixo do plano.
        # Sem prefixo definido, a etapa está pulada (tratada acima) e o gate não importa.
        "7": bool(dec.get("nome_prefixo"))
             and any(f.startswith(dec["nome_prefixo"]) for f in fim_v)
             and any("_FINALIZADO" in f.upper() for f in fim_v),
    }

    etapas = []
    proxima = None
    for et in ETAPAS:
        pulada = et in pulados
        feito = gates[et] or pulada
        etapas.append({
            "etapa": et,
            "rotulo": ROTULOS[et],
            "feito": feito,
            "pulada": pulada,
        })
        if proxima is None and not feito:
            proxima = et

    estado = {
        "lote": lote,
        "plan": plan_path,
        "decisoes": dec,
        "contagens": {
            "01_BRUTAS": len(videos(d_brutas)),
            "02_OTIMIZADOS_videos": len(otim_v),
            "02_OTIMIZADOS_bases": len(bases),
            "02_OTIMIZADOS_json": len(jsons(d_otim)),
            "03_PREPARADOS": len(prep_v),
            "04_COMBINADOS": len(comb_v),
            "99_FINALIZADOS": len(fim_v),
        },
        "etapas": etapas,
        "proxima_etapa": proxima,
        "concluido": proxima is None,
    }
    print(json.dumps(estado, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
