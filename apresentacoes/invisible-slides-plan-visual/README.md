# invisible-slides-plan-visual

Skill da Invisible que **renderiza um plano de slides em apresentação HTML**. Recebe um PLANO (storyboard no formato do contrato `slides-plan` v1) e produz um deck auto-contido, lindo de projetar em tela cheia: navegação por teclado, **builds** (revelação progressiva), notas do apresentador, fullscreen e escala responsiva. É a metade **visual** da criação de slides — não sabe pedagogia, só transforma semântica em pixels segundo um design system.

## Genérico de propósito

O renderizador não tem nada de "aula". Ele consome qualquer plano no contrato `slides-plan` v1 — venha da [`invisible-class-slides-plan`](../invisible-class-slides-plan/) (slides de aula) ou de outra fonte. Storyboards da `invisible-doc-to-presentation` são um subconjunto válido e também renderizam (sem builds). Separar a didática da visual deixou o motor visual reutilizável.

```
invisible-class-slides-plan   →   slides-plan.md   →   invisible-slides-plan-visual   →   HTML
       (didática)                   (contrato)                (visual, genérico)
```

## Como funciona (visão geral)

```
intake → lê o plano + escolhe design system + confirma slug/pasta
  → mapeamento: por slide  tipo → classe CSS · build → fragments · visual → Modo 0-3
  → produção visual quando aplicável (chart real em SVG; gerador de imagem em runtime)
  → render: template do design system + slides + notes[] → HTML auto-contido
```

O HTML é sempre **derivado do plano** — nunca o contrário. Exports futuros (PPTX, Canva) sairão do plano, jamais convertendo o HTML.

## Estrutura do plugin

```
invisible-slides-plan-visual/
├── .claude-plugin/plugin.json
├── README.md
├── CLAUDE.md
├── design-systems/
│   └── invisible.md                 # design system padrão (escala refinada + 5 layouts didáticos + builds)
└── skills/invisible-slides-plan-visual/
    ├── SKILL.md                     # orquestrador fino (intake, mapeamento, render)
    └── references/
        ├── slides-plan-spec.md      # o contrato slides-plan v1 (lado consumidor)
        ├── tipo-layout-map.md       # tabela tipo-didático → classe CSS (+ fallback)
        └── producao-visual.md       # roteamento de imagem, 4 modos, geração agnóstica
```

## Como usar

Tenha um plano de slides (gerado pela `invisible-class-slides-plan` ou compatível). Peça, em qualquer variação: "renderiza esse plano de slides", "gera o HTML desses slides", "transforma esse storyboard em apresentação", "monta o deck a partir do plano".

A skill pergunta no intake: o **plano** (caminho do arquivo `_plano.md`), o **design system** (padrão `invisible`) e confirma a **pasta/slug**. Depois renderiza o HTML na mesma subpasta do plano.

### Onde o output é salvo

```
class-slides/[nome-slug]/
  [nome-slug]_plano.md      # o plano (entrada, gerado pelo outro plugin)
  [nome-slug].html          # a apresentação (saída deste plugin)
```

O HTML **não** é versionado no plugin — pertence ao seu trabalho.

## Como adicionar um design system

Cada curso/produto pode ter o seu tema visual. Para adicionar um:

1. Crie um `.md` em `design-systems/` (ex.: `bem-grandes.md`), seguindo o formato do `invisible.md`: paleta, tipografia, fundamentos, tabela tipo → classe CSS, **template HTML completo com o player** e instruções de uso.
2. Pronto. A skill descobre o novo design system sozinha (`ls ../../design-systems/`) e o oferece na escolha. Não é preciso editar o SKILL.md.

O padrão é o **Invisible** (modo escuro editorial, escala refinada, com suporte a builds). Ele foi derivado do design system da `invisible-doc-to-presentation` (o visual aprovado), estendido para cobrir todos os tipos didáticos.

## Geração de imagem (portátil)

A skill faz design em HTML/CSS/SVG por conta própria (Modo 0, o default) e pode usar stock grátis (Modo 1). Para geração de imagem por IA (Modos 2/3), **detecta em tempo de execução** se há um gerador conectado via MCP; se não houver, avisa e segue em Modo 0/1. Não depende de nenhum servidor específico — funciona em qualquer máquina.

## Instalação (plugin do Claude Code)

```
/plugin marketplace add arnoalcantara/invisible-skills
/plugin install invisible-slides-plan-visual@invisible-skills
/plugin install invisible-class-slides-plan@invisible-skills
```

Instale os dois — um planeja, o outro renderiza.
