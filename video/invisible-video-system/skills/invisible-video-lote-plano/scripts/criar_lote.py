#!/usr/bin/env python3
"""criar_lote.py — cria a pasta de um lote novo e escreve o PLAN_LOTE.md.

Parte MECÂNICA da skill invisible-video-lote-plano. A conversa (capturar as
preferências) é conduzida pelo SKILL.md; este script só materializa o que foi
decidido: cria a pasta `<raiz>/<nome-do-lote>/` com as cinco pastas-irmãs da
esteira v2.6.0 (01_BRUTAS, 02_OTIMIZADOS, 03_PREPARADOS, 04_COMBINADOS,
99_FINALIZADOS) e grava o PLAN_LOTE.md na raiz do lote.

O PLAN_LOTE.md é o CONTRATO entre as duas skills: o planejador escreve, o
executor (invisible-video-lote-producao) lê as decisões e marca os checkboxes.
A fonte da verdade do progresso são as PASTAS — o checkbox é o resumo legível.

As preferências chegam por um JSON (--decisoes), não por dezenas de flags:
    {
      "estilo_legenda": "auto",        # auto | reels | minimal | classic
      "variacoes": [1],                 # lista de VARs de gancho; [] = nenhuma
      "var_fonte": "padrao",           # "padrao" ou descrição da fonte custom
      "var_fundo": "padrao",           # "padrao" ou descrição do fundo custom
      "trilha_pasta": "00_Recursos/Trilhas",   # relativo à raiz do lab, ou abs
      "alvo_fala": -14,
      "alvo_trilha": -37,
      "acelerar": true,
      "fator_aceleracao": 1.2,
      "modo_silencio": "conservador",  # conservador | justo
      "modo_respiro": "conservador",
      "observacoes": ""
    }
Campos ausentes assumem o default. `data` é passada de fora (--data AAAA-MM-DD)
porque o script não tem relógio confiável.

Uso:
    python3 criar_lote.py --raiz "<raiz do laboratório>" --nome "Lote 02 - X" \
        --data 2026-06-24 --decisoes decisoes.json [--forcar]
Saída (stdout): JSON {"lote_dir": ..., "plan": ..., "pastas": [...]} ou {"erro": ...}
"""
from __future__ import annotations

import argparse
import json
import os
import sys

PASTAS = ["01_BRUTAS", "02_OTIMIZADOS", "03_PREPARADOS", "04_COMBINADOS", "99_FINALIZADOS"]

DEFAULTS = {
    "estilo_legenda": "auto",
    "variacoes": [],
    "var_fonte": "padrao",
    "var_fundo": "padrao",
    "trilha_pasta": "00_Recursos/Trilhas",
    "alvo_fala": -14,
    "alvo_trilha": -37,
    "acelerar": False,
    "fator_aceleracao": 1.2,
    "modo_silencio": "conservador",
    "modo_respiro": "conservador",
    "observacoes": "",
}


def fator_token(fator: float) -> str:
    chave = f"{fator:.1f}"
    return {"1.2": "12X", "1.5": "15X", "2.0": "2X"}.get(chave, f"{fator:g}".replace(".", "") + "X")


def render_plan(nome: str, data: str, d: dict) -> str:
    estilo = d["estilo_legenda"]
    estilo_desc = (
        "auto (vertical→reels, quadrado→classic)" if estilo == "auto" else estilo
    )
    vars_ = d["variacoes"]
    if vars_:
        vars_desc = ", ".join(f"VAR{n}" for n in vars_)
        fonte = "padrão (Hoefler Text, fundo preto)" if d["var_fonte"] == "padrao" and d["var_fundo"] == "padrao" \
            else f"fonte: {d['var_fonte']} / fundo: {d['var_fundo']}"
    else:
        vars_desc = "nenhuma"
        fonte = "—"
    acel = (
        f"sim, {d['fator_aceleracao']}x (sufixo _ACELERADO_{fator_token(d['fator_aceleracao'])})"
        if d["acelerar"] else "não"
    )

    # Etapas condicionais: 3.2 só se há VAR; 5 (acelerar) só se acelerar.
    et_32 = (
        f"- [ ] **3.2 Variações de gancho** — `invisible-video-var-gancho-escrito --alvo segmento` "
        f"(02_OTIMIZADOS → 03_PREPARADOS) — {vars_desc}"
        if vars_ else
        "- [x] **3.2 Variações de gancho** — _(pulada: o plano não pediu VAR)_"
    )
    # Acelerar vem ANTES da trilha (senão a trilha aceleraria junto e sairia fora
    # de tempo). Roda em 04_COMBINADOS; a trilha (etapa 6) consome só os _ACELERADO_.
    et_5 = (
        f"- [ ] **5. Acelerar** — `invisible-video-acelerador --fator {d['fator_aceleracao']}` "
        f"(04_COMBINADOS → 04_COMBINADOS, acelera tudo, ao lado com _ACELERADO_{fator_token(d['fator_aceleracao'])})"
        if d["acelerar"] else
        "- [x] **5. Acelerar** — _(pulada: o plano não pediu aceleração)_"
    )
    # Entrada da trilha depende de ter havido aceleração.
    trilha_entrada = (
        "04_COMBINADOS (só os `_ACELERADO_`)" if d["acelerar"] else "04_COMBINADOS"
    )
    et_6 = (
        f"- [ ] **6. Trilha** — `invisible-trilha-aplicador` ({trilha_entrada} → 99_FINALIZADOS) — "
        f"trilha `{d['trilha_pasta']}`, fala {d['alvo_fala']}/trilha {d['alvo_trilha']} LUFS"
    )

    obs = d["observacoes"].strip()
    obs_bloco = f"\n## Observações\n\n{obs}\n" if obs else ""

    return f"""# PLAN_LOTE — {nome}

> Plano de produção deste lote. Criado pela `invisible-video-lote-plano` e
> executado pela `invisible-video-lote-producao`. **As pastas são a fonte da
> verdade do progresso**; os checkboxes abaixo são o resumo legível. O executor
> reconcilia com o disco antes de cada etapa e pula o que já está pronto.

- **Lote:** {nome}
- **Criado em:** {data}
- **Estrutura:** esteira v2.6.0 (01_BRUTAS → 02_OTIMIZADOS → 03_PREPARADOS → 04_COMBINADOS → 99_FINALIZADOS)

---

## Decisões do lote

| Decisão | Valor |
|---|---|
| Estilo de legenda | {estilo_desc} |
| Variações de gancho | {vars_desc} |
| Estilo do gancho escrito | {fonte} |
| Pasta de trilha | `{d['trilha_pasta']}` |
| Alvo de loudness — fala / trilha | {d['alvo_fala']} LUFS / {d['alvo_trilha']} LUFS |
| Aceleração | {acel} |
| Modo de otimização (silêncio / respiro) | {d['modo_silencio']} / {d['modo_respiro']} |

---

## Etapas (ordem da esteira)

> Dependências: 2 → (3.1, 3.2 em qualquer ordem) → 4 → 5 → 6.
> **Acelerar (5) vem ANTES da trilha (6)** — senão a trilha aceleraria junto e
> sairia fora de tempo. Ao fim de cada etapa o executor PARA e pede autorização.
> A 3.2 e a 5 só rodam se o plano pediu (já vêm marcadas como puladas quando não).

- [ ] **1. Otimizar + Denoise** — `invisible-video-otimizador` então `invisible-denoiser` (01_BRUTAS → 02_OTIMIZADOS; denoiser sobrescreve in-place) — modo {d['modo_silencio']}/{d['modo_respiro']}
- [ ] **2. Transcrever** — `invisible-legenda-arquivos` (02_OTIMIZADOS → .json por segmento)
- [ ] **3.1 Legendar** — `invisible-legendas-aplicador` (02_OTIMIZADOS → 03_PREPARADOS) — estilo {estilo_desc}
{et_32}
- [ ] **4. Combinar** — `invisible-video-combinador` (03_PREPARADOS → 04_COMBINADOS; salva MATRIZ.md e pede OK; .json de combinação OFF por padrão)
{et_5}
{et_6}

---

## Próximo passo

1. Jogue as brutas (ganchos, desenvolvimentos, CTAs...) em **`01_BRUTAS/`**.
2. Rode **`/invisible-video-lote-producao`** apontando para este lote.
{obs_bloco}"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raiz", required=True, help="raiz do laboratório (onde o lote nasce)")
    ap.add_argument("--nome", required=True, help="nome do lote, ex.: 'Lote 02 - Gurgel'")
    ap.add_argument("--data", required=True, help="data de criação AAAA-MM-DD")
    ap.add_argument("--decisoes", help="caminho de um JSON com as preferências")
    ap.add_argument("--forcar", action="store_true", help="permite reescrever lote existente")
    args = ap.parse_args()

    d = dict(DEFAULTS)
    if args.decisoes:
        if not os.path.isfile(args.decisoes):
            print(json.dumps({"erro": f"--decisoes não existe: {args.decisoes}"}, ensure_ascii=False))
            return 1
        with open(args.decisoes, encoding="utf-8") as f:
            d.update(json.load(f))

    if not os.path.isdir(args.raiz):
        print(json.dumps({"erro": f"raiz não existe: {args.raiz}"}, ensure_ascii=False))
        return 1

    lote_dir = os.path.join(args.raiz, args.nome)
    plan_path = os.path.join(lote_dir, "PLAN_LOTE.md")

    if os.path.exists(plan_path) and not args.forcar:
        print(json.dumps({
            "erro": "lote já existe (PLAN_LOTE.md presente). Use --forcar para reescrever.",
            "plan": plan_path}, ensure_ascii=False))
        return 2

    criadas = []
    for p in PASTAS:
        caminho = os.path.join(lote_dir, p)
        os.makedirs(caminho, exist_ok=True)
        criadas.append(caminho)

    with open(plan_path, "w", encoding="utf-8") as f:
        f.write(render_plan(args.nome, args.data, d))

    print(json.dumps({
        "lote_dir": lote_dir,
        "plan": plan_path,
        "pastas": criadas,
        "decisoes": d,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
