# Algoritmo PARA — fonte única da skill

> Conhecimento central da skill `invisible-organizacao-pastas`. A skill é fina: orquestra o fluxo e consome este módulo.
> Versão de referência do documento canônico do workspace (`00_Resources/PROTOCOLO Organização de Pastas Empresa Sistema PARA.md`).
> Editou aqui, mudou o comportamento da skill.

---

## Regra-mãe

Organize por **acionabilidade, nunca por tema.** A pergunta não é "sobre o que é isto?" e sim "quão perto está de uma ação?".

Quatro caixas, ordem fixa, da mais para a menos acionável:

| Caixa | Pasta | Guarda |
|---|---|---|
| Projects | `01_Projetos/` | esforços com prazo e fim |
| Areas | `02_Areas/` | responsabilidades contínuas, sem fim |
| Resources | `00_<Empresa> Resources/` | referência, consulta |
| Archives | `99_Arquivo/` | o que morreu, mas se preserva |

---

## Teste das 4 perguntas (cascata — a primeira "sim" vence)

1. **Em qual projeto ativo isto será útil?** → `01_Projetos/<projeto>/`
2. Se nenhum: **em qual área de responsabilidade se encaixa?** → `02_Areas/<area>/`
3. Se nenhuma: **a qual recurso/tema pertence?** → `00_<Empresa> Resources/`
4. Se nada: **arquivo.** → `99_Arquivo/`

A cascata empurra cada item ao lugar mais acionável possível. Pare na primeira resposta afirmativa.

---

## Projeto × Área (a decisão difícil)

- **Projeto:** meta, prazo, definição de "pronto". Sprint. Termina. → lançamento, campanha, ação pontual, contratação.
- **Área:** padrão mantido para sempre, sem linha de chegada. Maratona. → Financeiro, Marketing e Vendas, Operação, Atendimento, Equipe, Admin e Jurídico.

Pergunta decisiva: **"isto pode ser concluído?"** Sim → Projeto. "Mantido indefinidamente?" → Área.
Ambíguo: prazo no horizonte → Projeto; senão → Área. **Sinalize a dúvida para o humano decidir — nunca chute em silêncio.**

---

## Governança

- **Just-in-time:** pasta nasce de compromisso real, nunca de previsão. Exceção: as **Áreas de empresa são semeáveis** (existem desde o dia 1). Projetos e subpastas de Resources só sob demanda.
- **Sistema vivo:** itens migram de caixa conforme o status. Projeto concluído → Arquivo. Projeto que virou rotina → Área. Área abandonada → Arquivo. Manutenção é **mover**, não reorganizar.
- **Arquivar agressivamente:** intocado há ~6 meses → `99_Arquivo/`. Arquivar, nunca apagar.
- **Mesma estrutura em toda empresa.** Previsibilidade é metade do valor.
- **Forma numerada (Jeff Su):** `00_` Resources, `01_` Projetos, `02_` Áreas, `99_` Arquivo. Sem emoji/maiúscula gritada.

---

## Molde-alvo

```
<Empresa>/
├── CLAUDE.md, MEMORY.md            # INTOCÁVEIS
├── 00_<Empresa> Resources/         # Resources (referência)
├── 01_Projetos/                    # 1 subpasta por projeto vivo (sob demanda)
├── 02_Areas/                       # semeadas: Financeiro, Marketing-e-Vendas,
│                                   #   Operacao, Atendimento, Equipe, Admin-e-Juridico
└── 99_Arquivo/                     # recebe o que morre
```

Áreas default são semeáveis; áreas específicas da empresa (ex.: `Operacao-Pista` numa car wash) entram conforme a operação.

---

## Intocáveis (a reorganização NUNCA mexe)

- `CLAUDE.md`, `MEMORY.md` da empresa.
- A pasta `00_<Empresa> Resources/` e seu conteúdo (já é a caixa Resources).
- Arquivos declarados intocáveis pelo usuário.
- **Nada é apagado.** Só se move. Apagar é decisão humana.
- Nunca classificar "Empresa" como categoria — empresa é o container, não um item.
