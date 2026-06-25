# invisible-copy-system

Sistema de agentes de copy da **Invisible**. Dois agentes — **Estrategista** e **Copywriter** — operam sobre uma base de conhecimento compartilhada para produzir, com método, a estratégia e a copy de uma campanha.

A inteligência mora na `base/` (fonte única de verdade). Os agentes são finos: orquestram, conduzem o usuário com aprovação em cada etapa, e consomem os módulos da base.

---

## Como funciona (visão geral)

```
Arquivo Base de Curso  (pronto, feito fora deste sistema)
        │
        ▼
   AGENTE ESTRATEGISTA  (invisible-estrategista-copy/SKILL.md)
   lê o Arquivo Base → conduz com aprovação → produz o
        │
        ▼
   BRIEFING DE CAMPANHA  (a partir de briefing/template-briefing.md)
        │                 — pode haver vários por produto —
        ▼
   AGENTE COPYWRITER  (invisible-copywriter/SKILL.md)
   lê Briefing + Arquivo de Voz + módulo do formato → produz
        │
        ▼
   PEÇAS DE COPY  (anúncio, e-mail, VSL, carrossel, reels… em peça única ou matriz combinatória)
```

- O **Briefing de Campanha** é o artefato intermediário e o contrato entre os dois agentes.
- O **Arquivo de Voz** (DNA de escrita da marca/expert) é pré-existente e separado do briefing; o copywriter o aplica em toda peça.
- A separação é proposital: **pensar** (estratégia, uma vez por campanha) ≠ **escrever** (copy, muitas vezes).

---

## Estrutura do repositório

```
invisible-copy-system/          # raiz do plugin (instalável como `invisible-copy`)
├── .claude-plugin/
│   └── plugin.json             # manifesto do plugin
├── README.md
├── skills/                     # os agentes, descobertos pelo Claude Code
│   ├── estrategista/
│   │   └── SKILL.md            # agente Estrategista
│   └── copywriter/
│       └── SKILL.md            # agente Copywriter
├── base/                       # conhecimento compartilhado — FONTE ÚNICA
│   ├── icp.md                  # perfil do cliente ideal
│   ├── dores-e-desejos.md
│   ├── avatar.md
│   ├── objecoes.md
│   ├── mecanismo-unico.md
│   ├── grande-promessa.md
│   ├── big-idea.md
│   ├── niveis-de-consciencia.md
│   ├── sofisticacao.md
│   ├── produtos/               # perfis de produto (substituem Briefing+Voz)
│   │   ├── indice-produtos.md
│   │   └── desafio-memorize-escrita.md
│   ├── copy/                   # fundações de craft (cross-formato)
│   │   ├── estruturas-de-copy.md   # frameworks: PAS, AIDA, BAB, 4 Ps
│   │   ├── macroestrutura.md       # Gancho · Desenvolvimento · CTA (+ modo combinatório)
│   │   ├── angulos.md              # ângulos de variação de criativo
│   │   ├── figuras-de-retorica.md  # tricolon, anáfora, quiasmo… (cross-produto)
│   │   └── modelos/                # esqueletos de persuasão por produtor
│   └── formatos/               # regras estruturais por canal
│       ├── reels.md
│       ├── youtube.md
│       ├── aquecimento.md
│       ├── legenda-instagram.md
│       ├── carrossel.md
│       ├── email.md
│       ├── whatsapp.md
│       ├── landing-page.md
│       ├── vsl.md
│       └── pagina-obrigado.md
└── briefing/
    └── template-briefing.md    # estrutura do Briefing de Campanha
```

**Convenção de caminhos:** as skills vivem em `skills/<agente>/SKILL.md` e referenciam `base/...` e `briefing/...` **a partir da raiz do plugin** (dois níveis acima da skill: `../../base/`). A `base/` é compartilhada — nunca duplique módulos dentro das pastas dos agentes.

---

## Como a equipe usa

1. **Pré-requisitos por campanha:** um **Arquivo Base de Curso** e um **Arquivo de Voz** da marca (ambos produzidos fora deste sistema).
2. **Rodar o Estrategista** apontando para o Arquivo Base → ele conduz, com aprovação em cada etapa, e gera o briefing em `campanhas/[slug-campanha]/BRIEFING_[slug-campanha]_v[N].md`.
3. **Rodar o Copywriter** apontando para o Briefing + o Arquivo de Voz → escolher o formato e o modo de entrega (peça única ou matriz combinatória) → ele produz a copy, com aprovação.

Ambos os agentes **pausam para aprovação** e aceitam correções no meio do caminho.

### Onde os outputs são salvos

Todo output — o briefing do estrategista e as peças do copywriter — vai para uma **pasta única**, criada no diretório onde você roda a skill:

```
campanhas/
├── [slug-campanha]/                       # uma subpasta por campanha
│   ├── BRIEFING_[slug-campanha]_v1.md     # do estrategista
│   ├── email-aquecimento-01.md            # do copywriter
│   └── vsl-principal.md
└── [outra-campanha]/
    └── ...
```

O `[slug-campanha]` (kebab-case) é definido pelo estrategista no intake e **reusado** pelo copywriter, de modo que briefing e peças da mesma campanha fiquem juntos. A pasta `campanhas/` é criada automaticamente na primeira vez e **não é versionada** (está no `.gitignore`) — ela pertence ao trabalho de campanha, não ao sistema.

---

## Como atualizar (fluxo de manutenção)

A base é viva. Para evoluir o sistema:

1. Edite o(s) módulo(s) em `base/` (ou um SKILL.md / o template).
2. Mantenha as **referências cruzadas** coerentes (os módulos se citam por caminho, ex.: `base/sofisticacao.md`). Ao renomear um arquivo, atualize quem o referencia.
3. Commit + push:
   ```bash
   git add -A
   git commit -m "feat(base): refina módulo de objeções"
   git push
   ```
4. A equipe puxa a versão mais recente:
   ```bash
   git pull
   ```

**Princípios do sistema** (não quebrar ao editar): conhecimento na `base/` como fonte única; agentes finos; verdade e dignidade do público como critério de corte; específico vence genérico; canalizar desejo, não criar.

---

## Instalação (plugin do Claude Code)

Este sistema é distribuído como **plugin** dentro do marketplace público `arno-skills` (repositório `arnoalcantara/skills`). Para instalar em qualquer máquina, dentro do Claude Code:

```bash
/plugin marketplace add arnoalcantara/skills
/plugin install invisible-copy@arno-skills
```

Isso instala as duas skills: **`invisible-estrategista-copy`** e **`invisible-copywriter`**, já com a `base/` compartilhada e o `briefing/` juntos no plugin. Os outputs continuam indo para `campanhas/` no diretório onde você roda o Claude.

**Empacotamento (como funciona por dentro):** as skills vivem em `skills/<agente>/SKILL.md`; a `base/` e o `briefing/` ficam na raiz do plugin e são referenciados pelas skills a partir de `../../`. `${CLAUDE_PLUGIN_ROOT}` não expande no corpo do SKILL.md, por isso cada skill confirma o caminho da base com `ls ../../base` antes de ler os módulos.
