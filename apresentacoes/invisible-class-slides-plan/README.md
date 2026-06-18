# invisible-class-slides-plan

Skill da Invisible que transforma **transcrição, roteiro ou esboço de aula** num **PLANO de slides** (storyboard slide-a-slide) para o professor projetar ao vivo numa turma. É a metade **didática** da criação de slides de aula: decide o que vira slide, em que ordem, com que tipo e que build — regida pela ciência da aprendizagem (carga cognitiva de Sweller, multimídia de Mayer, asserção-evidência de Alley). **Não gera HTML.** O render visual é feito pelo plugin irmão [`invisible-slides-plan-visual`](../invisible-slides-plan-visual/), que consome o plano.

## Por que dois plugins

A criação de slides de aula tem duas metades de natureza diferente: a **didática** (transformar a aula num argumento visual estruturado) e a **visual** (renderizar isso em pixels bonitos). Separá-las deixa cada uma evoluir sozinha e torna o renderizador **genérico** — ele serve qualquer plano de slides, não só aula. A keystone entre as duas é o contrato **`slides-plan` v1**.

```
invisible-class-slides-plan   →   slides-plan.md   →   invisible-slides-plan-visual   →   HTML
       (didática)                   (contrato)                (visual, genérico)
```

## Como funciona (visão geral)

A skill é um **designer instrucional**: não joga o texto da aula em bullets, transforma um argumento linear num argumento visual estruturado que respeita a memória de trabalho do aluno.

```
arranque → define os dials (fidelidade + intenção visual) + contexto
  → [Transcrição/Roteiro] lê a aula inteira → mapa de proveniência
     [Esboço/Ideia]        pesquisa e desenvolve a aula
  → PASSADA 1: arco da aula + sequência de tipos de slide = PLANO  ◀── output (slides-plan v1)
  → APROVAÇÃO do usuário  (portão obrigatório)
  → HANDOFF → /invisible-slides-plan-visual renderiza o HTML
```

O plano carrega **semântica** (o que cada slide é e diz), **nunca estética**. O pixel é decisão do renderizador. É essa fronteira que mantém os dois plugins desacoplados.

## Estrutura do plugin

```
invisible-class-slides-plan/
├── .claude-plugin/plugin.json
├── README.md
├── CLAUDE.md
└── skills/invisible-class-slides-plan/
    ├── SKILL.md                     # orquestrador fino (dials, Passada 1, output)
    └── references/
        ├── filosofia.md             # princípio-mestre + as 13 leis
        ├── arco-da-aula.md          # arco da aula + processo de 2 passadas
        ├── tipologia.md             # 8 famílias, ~47 tipos de slide (TOC + links)
        ├── fichas/                  # uma ficha executável por tipo
        ├── proveniencia.md          # contrato de fidelidade à aula do professor
        └── slides-plan-spec.md      # o contrato slides-plan v1 (lado emissor)
```

## Como usar

Peça, em qualquer variação: "planeja os slides dessa aula", "transforma essa transcrição em plano de slides de aula", "monta a estrutura da aula", "gera o storyboard didático desse roteiro".

A skill pergunta no arranque: a **fonte** (arquivo, texto colado, link), o **modo de fidelidade** (a aula já existe vs. é só um esboço), o **modo visual pretendido** e o **contexto do curso**. Entrega o plano para você aprovar e, aprovado, orienta o handoff para o renderizador.

### Onde o output é salvo

```
class-slides/[nome-slug]/
  [nome-slug]_plano.md      # o storyboard aprovável (slides-plan v1)
```

`class-slides/` é criada no diretório de trabalho atual. O renderizador grava o HTML na mesma subpasta. O output **não** é versionado no plugin.

## Instalação (plugin do Claude Code)

```
/plugin marketplace add arnoalcantara/invisible-skills
/plugin install invisible-class-slides-plan@invisible-skills
/plugin install invisible-slides-plan-visual@invisible-skills
```

Instale os dois — um planeja, o outro renderiza.

## Escopo (v1)

- **Foco:** projeção ao vivo (professor presente). Modo autoestudo é roadmap.
- **Output:** o plano (slides-plan v1). O HTML é responsabilidade do `invisible-slides-plan-visual`.
- **Export PPTX/Canva:** roadmap — sempre a partir do plano, nunca convertendo HTML.
