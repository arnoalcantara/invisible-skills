# invisible-doc-to-presentation

Plugin da **Invisible** que transforma qualquer documento em apresentação. Você aponta um documento — transcrição de reunião, briefing, relatório, proposta, artigo — e a skill produz dois outputs: um **storyboard `.md`** slide-a-slide (aprovado antes de seguir) e uma **apresentação HTML** navegável, pronta para apresentar.

A skill não resume o documento: ela extrai os momentos de impacto, estrutura uma narrativa visual e entrega slides com ritmo e hierarquia. O visual segue um **design system** — o padrão é o da Invisible, e outros podem ser adicionados.

---

## Como funciona (visão geral)

```
Documento fonte  (arquivo local, texto colado, Google Drive, URL…)
        │
        ▼
   FASE 0 — Intake          confirma fonte, design system, nome e objetivo
        │
        ▼
   FASE 1 — Análise         extrai tese, momentos de impacto, arco, CTA  (interna)
        │
        ▼
   FASE 2 — Storyboard      roteiro slide-a-slide em .md  →  APROVAÇÃO
        │
        ▼
   FASE 3 — HTML            aplica o design system e gera o deck navegável
```

A skill **pausa para aprovação** no storyboard antes de gerar o HTML, e aceita ajustes no meio do caminho.

---

## Estrutura do plugin

```
invisible-doc-to-presentation/          # raiz do plugin (instalável como invisible-doc-to-presentation)
├── .claude-plugin/
│   └── plugin.json                     # manifesto do plugin
├── README.md
├── CLAUDE.md                           # instruções de manutenção
├── design-systems/                     # visual das apresentações — extensível
│   └── invisible.md                    # design system padrão (Invisible)
└── skills/
    └── invisible-doc-to-presentation/
        └── SKILL.md                    # a skill
```

**Convenção de caminho:** a skill vive em `skills/invisible-doc-to-presentation/SKILL.md` e referencia os design systems a partir de `../../design-systems/` (dois níveis acima, na raiz do plugin). A skill confirma o caminho com `ls ../../design-systems/` antes de ler.

---

## Como usar

1. Invoque a skill (`/invisible-doc-to-presentation`) apontando o documento — caminho de arquivo local, texto colado, ou link (Google Drive/URL, se houver uma ferramenta MCP disponível na sessão; senão, use arquivo local ou texto colado).
2. No **Intake**, confirme o design system (padrão: Invisible), o `[nome-slug]` da apresentação e o objetivo.
3. Aprove o **storyboard** `.md`.
4. Receba o **HTML** navegável.

### Onde os outputs são salvos

Tudo vai para uma pasta única no diretório onde você roda o Claude:

```
apresentacoes/
└── [nome-slug]/
    ├── [nome-slug]_storyboard.md       # roteiro slide-a-slide
    └── [nome-slug].html                # deck navegável (teclado, notas, fullscreen)
```

O `[nome-slug]` (kebab-case) é definido no Intake. A pasta é criada na primeira vez e pertence ao seu trabalho — não ao plugin.

---

## Como adicionar um design system

O visual é desacoplado da skill. Para criar um novo design system:

1. Crie um `.md` em `design-systems/` (ex.: `design-systems/cliente-x.md`), seguindo o formato do `invisible.md`: paleta, tipografia, fundamentos visuais, tipos de slide, **template HTML base completo** e instruções de uso.
2. Pronto — a skill o descobre automaticamente (lista a pasta no Intake) e passa a oferecê-lo como opção. Não é preciso editar o SKILL.md.

O `invisible.md` é a referência: modo escuro nativo (`#111111`), tipografia editorial (Playfair Display + DM Sans + Space Grotesk), acento coral `#E85043`, e um template HTML auto-contido com player (navegação por teclado, notas do apresentador, fullscreen, escala responsiva).

---

## Instalação (plugin do Claude Code)

Distribuído como plugin no marketplace `invisible-skills` (repositório `arnoalcantara/invisible-skills`). No Claude Code:

```bash
/plugin marketplace add arnoalcantara/invisible-skills
/plugin install invisible-doc-to-presentation@invisible-skills
```

Isso instala a skill `invisible-doc-to-presentation` com a pasta `design-systems/` junto. Os outputs continuam indo para `apresentacoes/` no diretório onde você roda o Claude.
