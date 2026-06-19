# invisible-organizacao-system

Sistema de organização de pastas de empresa da **Invisible**, pelo método **PARA** (Tiago Forte) sobre **forma numerada** (Jeff Su).

Uma skill — `invisible-organizacao-pastas` — pega a pasta de uma empresa, classifica cada item solto por **acionabilidade** (não por tema), propõe um plano e aplica com reversibilidade total. Nunca move nada antes de você aprovar. Nunca apaga.

---

## O método em uma frase

Não importa **sobre o que** o arquivo fala. Importa **quão perto de uma ação** ele está. Daí as quatro caixas:

```
00_<Empresa> Resources/   →  referência, consulta          (RESOURCES)
01_Projetos/              →  tem prazo e fim                (PROJECTS)
02_Areas/                 →  responsabilidade sem fim       (AREAS)
99_Arquivo/               →  o que morreu, preservado       (ARCHIVES)
```

Cada item é classificado por uma cascata de 4 perguntas; a primeira que responde "sim" vence. A decisão mais difícil — Projeto ou Área? — se resolve com "isto pode ser concluído?". Sim → Projeto (sprint). Não → Área (maratona). O algoritmo completo está em `base/algoritmo-para.md`.

---

## Como funciona (fluxo)

```
Pasta de empresa (bagunçada)
        │
        ▼
   MAPEAR (read-only)  →  lista o que está solto e quais caixas existem
        │
        ▼
   CLASSIFICAR  →  teste das 4 perguntas em cada item + semeia áreas-padrão
        │
        ▼
   PROPOR (dry-run)  →  mostra o plano: pastas a criar, item→destino→motivo, ambíguos
        │
        ▼
   [ você aprova ]
        │
        ▼
   APLICAR  →  cria pastas, move itens, grava manifesto + reversor
```

A skill **pausa para aprovação** e marca todo item ambíguo para você decidir. O que ela faz, dá para desfazer com um comando.

---

## Estrutura do plugin

```
invisible-organizacao-system/        # raiz do plugin (instalável como `invisible-organizacao`)
├── .claude-plugin/
│   └── plugin.json                  # manifesto do plugin
├── README.md
├── CLAUDE.md                        # instruções para quem edita o plugin
├── base/
│   └── algoritmo-para.md            # FONTE ÚNICA do algoritmo PARA
└── skills/
    └── invisible-organizacao-pastas/
        └── SKILL.md                 # a skill
```

A skill referencia a base a partir de `../../base/`. Não duplique o algoritmo dentro do SKILL.md — ele vive na base.

---

## Como usar

Dentro do Claude Code, apontando para uma pasta de empresa:

```
/invisible-organizacao-pastas  organiza a pasta da empresa <Nome>
```

ou simplesmente: *"organiza essa pasta de empresa pelo PARA"*, *"aplica o padrão de pastas na <empresa>"*.

A skill mapeia, classifica, mostra o plano e espera seu ok antes de mover. Depois de aplicar, grava na raiz da pasta-alvo:

- `_MANIFESTO_PARA.tsv` — registro de cada movimento (origem → destino).
- `_reverter_para.sh` — desfaz tudo: `bash _reverter_para.sh`.

---

## Garantias

- **Nada se move antes da aprovação.** Mapear e classificar são read-only.
- **Nada é apagado.** A skill só move e cria pastas.
- **Intocáveis:** `CLAUDE.md`, `MEMORY.md` e a pasta de Resources da empresa nunca são mexidos.
- **Reversível:** um comando desfaz a reorganização.

---

## Instalação (plugin do Claude Code)

```bash
/plugin marketplace add <repo-do-marketplace-invisible-skills>
/plugin install invisible-organizacao@invisible-skills
```

Isso instala a skill `invisible-organizacao-pastas` com a `base/` empacotada.
