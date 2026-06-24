#!/usr/bin/env python3
"""marcar_etapa.py — marca (ou desmarca) o checkbox de uma etapa no PLAN_LOTE.md.

Edição cirúrgica: troca `- [ ] **<etapa>` por `- [x] **<etapa>` (ou o inverso com
--desmarcar). Não toca em mais nada do documento.

Uso:
    python3 marcar_etapa.py "<dir do lote>" 3.1            # marca feito
    python3 marcar_etapa.py "<dir do lote>" 3.1 --desmarcar
Saída (stdout): JSON {"etapa": ..., "marcada": true} ou {"erro": ...}
"""
from __future__ import annotations

import json
import os
import re
import sys

ETAPAS_VALIDAS = {"1", "2", "3.1", "3.2", "4", "5", "6"}


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    desmarcar = "--desmarcar" in sys.argv
    if len(args) < 2:
        print(json.dumps({"erro": "uso: marcar_etapa.py <dir do lote> <etapa> [--desmarcar]"},
                         ensure_ascii=False))
        return 1
    lote, etapa = os.path.abspath(args[0]), args[1]
    if etapa not in ETAPAS_VALIDAS:
        print(json.dumps({"erro": f"etapa inválida: {etapa}. Use uma de {sorted(ETAPAS_VALIDAS)}"},
                         ensure_ascii=False))
        return 1

    plan_path = os.path.join(lote, "PLAN_LOTE.md")
    if not os.path.isfile(plan_path):
        print(json.dumps({"erro": f"PLAN_LOTE.md não encontrado em {lote}"}, ensure_ascii=False))
        return 1

    with open(plan_path, encoding="utf-8") as f:
        txt = f.read()

    para = "[x]" if not desmarcar else "[ ]"
    # casa só a linha que começa a etapa: "- [ ] **3.1 " — o '**' e o ponto/espaço
    # após o número evitam casar "3.1" com "3" (ou um número dentro do texto).
    novo, n = re.subn(
        rf"(- )\[(?: |x)\]( \*\*{re.escape(etapa)}[ .])",
        rf"\g<1>{para}\g<2>",
        txt,
        count=1,
    )
    if n == 0:
        print(json.dumps({"erro": f"checkbox da etapa {etapa} não encontrado no PLAN_LOTE.md"},
                         ensure_ascii=False))
        return 1

    with open(plan_path, "w", encoding="utf-8") as f:
        f.write(novo)

    print(json.dumps({"etapa": etapa, "marcada": not desmarcar, "plan": plan_path},
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
