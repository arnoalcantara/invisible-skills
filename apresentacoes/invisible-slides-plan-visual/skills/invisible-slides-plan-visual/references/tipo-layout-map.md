# Mapa tipo-didático → classe CSS

> **Propósito.** A tabela de tradução entre o vocabulário **semântico** do plano (as 8 famílias / ~47 tipos do contrato `slides-plan` v1) e as **classes CSS** do design system. O plano diz o que o slide *é*; aqui você acha a classe que o renderiza.
> **Vocabulário de classe.** O design system `invisible` usa o prefixo **`s-`** (a inteligência visual da `invisible-doc-to-presentation`). Slides de fundo **claro** recebem também a classe `light`.
> **Regra de ouro.** Tipo que não estiver nesta tabela → fallback `s-conteudo` + comentário HTML `<!-- tipo não mapeado: X -->`. Nunca quebre por um tipo desconhecido.

---

## Tabela

| Classe CSS | Fundo | Tipos do plano que atende |
|---|---|---|
| `s-capa` | escuro | abertura-titulo |
| `s-conteudo` | claro (`light`) | asseracao-evidencia **(padrão)**, declaracao-soco, definicao, exemplo-caso, analogia-metafora, objetivos, roteiro-agenda, sintese, takeaway, recursos-referencias, exemplo-resolvido, ativacao-conhecimento-previo (variante texto) |
| `s-duo` | misto | comparacao-lado-a-lado, trade-off-pros-contras, antes-depois, venn-sobreposicao, matriz-2x2 (variante) |
| `s-diagrama` | claro (`light`) | passo-a-passo, causa-efeito, ciclo-loop, arvore-de-decisao, taxonomia-hierarquia, anatomia-diagrama-rotulado, progressao-jornada |
| `s-tabela` | claro (`light`) | comparações densas/tabulares (quando a comparação tem muitas dimensões) |
| `s-num` | misto (`light`) | numero-grande, destaque-sobre-dado |
| `s-citacao` | escuro | citacao-autoridade |
| `s-fechamento` | escuro | fechamento da aula |
| `s-timeline` | claro (`light`) | linha-do-tempo, espectro-continuum |
| `s-chart` | claro (`light`) | grafico, infografico (chart real em SVG/código) |
| `s-image` | escuro | imagem-tela-cheia, imagem-texto (`split`), exemplo-anotado (`split`) |
| `s-prompt` | escuro | pergunta-provocacao, predicao, enquete, problema-para-resolver, preencher-lacuna, pense-converse-compartilhe, verificacao-entendimento |
| `s-divider` | claro (`light`) | divisor-secao, voce-esta-aqui, ponte-transicao, erro-comum, mnemonico |
| `s-retrato` | escuro | quando o slide centra uma pessoa (autoridade, protagonista) com foto editorial |

---

## Notas de mapeamento

- **`s-conteudo` é o workhorse.** Quando em dúvida, ou diante de tipo desconhecido, é o destino. Comporta título-asserção (`<h2>`), corpo em prosa (`.body p`) e lista (`<ul><li>`). Escolha o sub-layout pela forma do `Conteúdo:` do slide. É **fundo claro** → leva `light`.
- **Tipos parentes compartilham classe.** Um molde serve vários tipos (ex.: comparação e trade-off vão ambos a `s-duo`). Use os slots da classe; não invente classe nova por tipo.
- **`light` segue o fundo.** Todo slide de fundo claro (`s-conteudo`, `s-titulo`, `s-diagrama`, `s-tabela`, `s-timeline`, `s-chart`, `s-divider`, e `s-num`/`s-duo` que são mistos mas têm chrome claro à direita) recebe a classe `light` para ajustar a cor de numeração e logo. Slides escuros (`s-capa`, `s-citacao`, `s-prompt`, `s-image`, `s-fechamento`, `s-retrato`) **não** levam `light`.
- **`s-chart` exige chart real.** Nunca uma imagem de gráfico. Renderize barras/linhas/pizza em SVG ou HTML dentro de `.chart-area`, com os dados literais do `Conteúdo:`. Ver [producao-visual.md](producao-visual.md).
- **`s-image`** tem duas formas: tela cheia (com `.overlay` para legenda) e `.split` (imagem + texto lado a lado). Escolha pela intenção no campo `Visual:`.
- **`s-prompt`** é para processamento ativo: a pergunta em destaque, as opções/resposta tipicamente como `fragment` (revelar depois de a turma pensar). O campo `Build:` do plano costuma pedir isso.
- **Comparação: `s-duo` vs `s-tabela`.** Duas/três colunas com poucos pontos → `s-duo`. Muitas linhas/dimensões → `s-tabela`. Decida pela densidade do conteúdo.
- **`s-titulo`** (tese/asserção de seção, fundo claro) é uma opção quando o slide é uma única frase declarativa sem corpo — útil para abrir um bloco. Para conteúdo com bullets, use `s-conteudo`.
- **Se o design system escolhido não tiver uma classe** desta tabela (um design system enxuto pode ter só as da base), caia para a classe mais próxima que ele oferecer (quase sempre `s-conteudo`) e registre o comentário de fallback.

---

## Cruzamento

- [slides-plan-spec.md](slides-plan-spec.md) — o contrato de onde vem o campo `Família / Tipo`.
- [producao-visual.md](producao-visual.md) — como tratar o campo `Visual:` (chart real, geração em runtime, modos).
- O design system em `../../design-systems/[sistema].md` — onde as classes desta tabela são definidas (CSS + template + exemplos).
