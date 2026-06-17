# Design System: INVISIBLE — Didático (aula ao vivo)

> A identidade Invisible aplicada a **slides de aula projetados ao vivo**. Mantém o craft editorial escuro da marca, mas eleva o **piso de legibilidade** (lei 11): tipografia maior, contraste alto, um acento só.
>
> **Este arquivo é só o skin.** A estrutura — layouts, densidade, hierarquia, grid, primitivos e player — vive na camada de composição compartilhada, [`_base.md`](_base.md), escrita só com variáveis. Aqui ficam os **tokens** da marca (o que `_base.md` exige) e o **tratamento**. Render = `_base.md` + estes tokens. Brand novo = copiar este bloco, re-tematizar.
>
> Versão: junho 2026.

---

## Princípio visual

O design serve às 13 leis da skill ([../skills/invisible-class-slides/references/filosofia.md](../skills/invisible-class-slides/references/filosofia.md)), nesta ordem de prioridade:

- **Legível do fundo da sala** (lei 11): corpo nunca abaixo de ~24px na escala 1280×720; títulos grandes; contraste alto.
- **Um ponto focal** (lei 4): hierarquia explícita por tamanho/cor/posição.
- **Espaço em branco é estrutura** (lei 10): respiro generoso; conteúdo ocupa o quadro, nunca flutua.
- **Acento único** (coral) reservado para o que importa — nunca decorativo (lei 3).
- **Revelação progressiva nativa** (lei 8): o player suporta `fragment` para builds passo a passo.

**Modo padrão:** escuro (expressão nativa da marca). Para salas muito claras, troque os tokens de fundo por claros e inverta os de texto — o sistema é montado em variáveis para isso.

---

## Tokens da marca (o bloco `:root` que a base recebe)

Estes são os tokens que [`_base.md`](_base.md) exige, com os valores da Invisible. É o `{{ROOT_TOKENS}}` injetado no render.

```css
:root {
  /* Fundos — do mais escuro ao mais claro (profundidade por camadas, nunca por sombra) */
  --bg-0:        #000000;   /* capas, fechamento, citação, prompt */
  --bg-1:        #111111;   /* fundo padrão de slide */
  --surface-1:   #1C1C1C;   /* caixas, cards */
  --surface-2:   #252525;   /* segundo nível / caixa crítica */

  /* Bordas */
  --border:        #333333;
  --border-subtle: #2A2A2A;

  /* Texto — primário → terciário */
  --ink-1: #FFFFFF;   /* asserções, texto primário */
  --ink-2: #D2D2D2;   /* secundário (mais claro que o brand p/ legibilidade de sala) */
  --ink-3: #8A8A8A;   /* labels, terciário */

  /* Acento — um só */
  --accent:     #E85043;   /* coral: ênfase, destaque, passo crítico, "certo" */
  --accent-dim: #6E2A24;   /* coral esmaecido: índices estruturais, estados */

  /* Fontes */
  --font-display: 'Playfair Display', Georgia, serif;       /* asserção-herói, citação, número grande */
  --font-ui:      'DM Sans', system-ui, sans-serif;         /* corpo, listas */
  --font-label:   'Space Grotesk', system-ui, sans-serif;   /* labels, títulos-asserção, UI */

  /* Forma */
  --radius: 0px;   /* flat; máx. 2px */
}
```

**Wordmark (`{{WORDMARK}}`):** `INVISIBLE`.

**Font links (`{{FONT_LINKS}}`):**
```html
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,900;1,400;1,700&family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,700&family=Space+Grotesk:wght@500;700&display=swap" rel="stylesheet">
```

> A escala de espaçamento (8/12/16/24/32/48/64/80) é estrutural e vem da base. A Invisible usa o ritmo padrão — não sobrescreve.

---

## Tratamento da marca

- **Cor.** Coral só em ênfase singular (a asserção-chave, o passo crítico, o "certo" de um erro comum). Distinções de conteúdo (certo/errado, A/B) **nunca** dependem só de cor — use também posição, rótulo ou forma.
- **Profundidade** por camadas (`--bg-1` → `--surface-1` → `--surface-2`), nunca por gradiente ou sombra.
- **Tipografia (usos e tamanhos, escala 1280×720):**
  - *Título-asserção:* `--font-label` 700, 34–40px (lei 2 — sempre presente).
  - *Asserção-herói:* `--font-display` 900, 48–76px (declaração-soco, slide esparso).
  - *Corpo / itens:* `--font-ui` 400–500, **24–28px** (piso de legibilidade).
  - *Número grande:* `--font-display` 900, 96–140px.
  - *Citação:* `--font-display` italic, 40px.
  - *Label / tag:* `--font-label` 700, 12–13px, uppercase, letter-spacing 0.14em.
- **Fundamentos:** radius 0 (flat), sem sombra, sem emoji, ícones só funcionais e geométricos. Alinhamento à esquerda ou centralizado, nunca justificado. Animações = fades de opacidade 150–200ms, sem bounce.

---

## Tipos de slide → tipologia didática

Cada tipo da tipologia mapeia para uma classe CSS (definida em [`_base.md`](_base.md)). Tipos parentes compartilham classe (um molde serve vários). As variantes de composição (`.hero`, `.center`, `.lead`, `.dense`, `.grid`, `.critical`, `.verdict`) são escolhidas conforme [composicao-visual.md](../skills/invisible-class-slides/references/composicao-visual.md).

| Classe CSS | Tipos da tipologia que atende |
|---|---|
| `.slide-cover` | abertura-titulo |
| `.slide-assert` | asseracao-evidencia (padrão), definicao, declaracao-soco (`.hero`), exemplo-caso, analogia-metafora |
| `.slide-list` | objetivos, roteiro-agenda, sintese, recursos-referencias, takeaway (variante) |
| `.slide-two-col` | comparacao-lado-a-lado, trade-off-pros-contras, antes-depois, venn-sobreposicao |
| `.slide-diagram` | passo-a-passo, causa-efeito, ciclo-loop, arvore-de-decisao, taxonomia-hierarquia, anatomia-diagrama-rotulado, progressao-jornada |
| `.slide-timeline` | linha-do-tempo, espectro-continuum |
| `.slide-number` | numero-grande, destaque-sobre-dado |
| `.slide-chart` | grafico, infografico (chart real em SVG/código) |
| `.slide-image` | imagem-tela-cheia, imagem-texto, exemplo-anotado |
| `.slide-prompt` | pergunta-provocacao, predicao, enquete, problema-para-resolver, preencher-lacuna, pense-converse-compartilhe, verificacao-entendimento |
| `.slide-quote` | citacao-autoridade |
| `.slide-divider` | divisor-secao, voce-esta-aqui, ponte-transicao, ativacao-conhecimento-previo, erro-comum (variante), mnemonico |
| `.slide-closing` | fechamento da aula |

> A skill escolhe o **tipo** pela tipologia; aqui encontra a **classe**; em [composicao-visual.md](../skills/invisible-class-slides/references/composicao-visual.md) decide a **variante/composição**. Se um tipo precisar de layout que nenhuma classe cobre, componha com utilitários (`.label`, `.assert-title`, `.accent-bar`, `.rule`, `.fragment`) mantendo as regras acima.
