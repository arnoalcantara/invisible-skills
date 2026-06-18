# Mapa tipo-didático → classe CSS

> **Propósito.** A tabela de tradução entre o vocabulário **semântico** do plano (as 8 famílias / ~47 tipos do contrato `slides-plan` v1) e as **classes CSS** do design system. O plano diz o que o slide *é*; aqui você acha a classe que o renderiza.
> **Regra de ouro.** Tipo que não estiver nesta tabela → fallback `.slide-content` + comentário HTML `<!-- tipo não mapeado: X -->`. Nunca quebre por um tipo desconhecido.

---

## Tabela

| Classe CSS | Tipos do plano que atende |
|---|---|
| `.slide-cover` | abertura-titulo |
| `.slide-content` | asseracao-evidencia **(padrão)**, declaracao-soco, definicao, exemplo-caso, analogia-metafora, objetivos, roteiro-agenda, sintese, takeaway, recursos-referencias, exemplo-resolvido, ativacao-conhecimento-previo (variante texto) |
| `.slide-two-col` | comparacao-lado-a-lado, trade-off-pros-contras, antes-depois, venn-sobreposicao, matriz-2x2 (variante) |
| `.slide-diagram` | passo-a-passo, causa-efeito, ciclo-loop, arvore-de-decisao, taxonomia-hierarquia, anatomia-diagrama-rotulado, progressao-jornada |
| `.slide-table-layout` | comparações densas/tabulares (quando a comparação tem muitas dimensões) |
| `.slide-number` | numero-grande, destaque-sobre-dado |
| `.slide-quote` | citacao-autoridade |
| `.slide-closing` | fechamento da aula |
| `.slide-timeline` | linha-do-tempo, espectro-continuum |
| `.slide-chart` | grafico, infografico (chart real em SVG/código) |
| `.slide-image` | imagem-tela-cheia, imagem-texto, exemplo-anotado |
| `.slide-prompt` | pergunta-provocacao, predicao, enquete, problema-para-resolver, preencher-lacuna, pense-converse-compartilhe, verificacao-entendimento |
| `.slide-divider` | divisor-secao, voce-esta-aqui, ponte-transicao, erro-comum, mnemonico |

---

## Notas de mapeamento

- **`.slide-content` é o workhorse.** Quando em dúvida, ou diante de tipo desconhecido, é o destino. Comporta título-asserção (`<h2>`), corpo em prosa (`.body p`), lista (`<ul><li>`) e grade de cards (`.card-grid`). Escolha o sub-layout pela forma do `Conteúdo:` do slide.
- **Tipos parentes compartilham classe.** Um molde serve vários tipos (ex.: comparação e trade-off vão ambos a `.slide-two-col`). Use os slots da classe; não invente classe nova por tipo.
- **`.slide-chart` exige chart real.** Nunca uma imagem de gráfico. Renderize barras/linhas/pizza em SVG ou HTML dentro de `.chart-area`, com os dados literais do `Conteúdo:`. Ver [producao-visual.md](producao-visual.md).
- **`.slide-image`** tem duas formas: tela cheia (com `.overlay` para legenda) e `.split` (imagem + texto lado a lado). Escolha pela intenção no campo `Visual:`.
- **`.slide-prompt`** é para processamento ativo: a pergunta em destaque, as opções/resposta tipicamente como `fragment` (revelar depois de a turma pensar). O campo `Build:` do plano costuma pedir isso.
- **Comparação: `.slide-two-col` vs `.slide-table-layout`.** Duas/três colunas com poucos pontos → `.slide-two-col`. Muitas linhas/dimensões → `.slide-table-layout`. Decida pela densidade do conteúdo.
- **Se o design system escolhido não tiver uma classe** desta tabela (um design system enxuto pode ter só as 8 da base), caia para a classe mais próxima que ele oferecer (quase sempre `.slide-content`) e registre o comentário de fallback.

---

## Cruzamento

- [slides-plan-spec.md](slides-plan-spec.md) — o contrato de onde vem o campo `Família / Tipo`.
- [producao-visual.md](producao-visual.md) — como tratar o campo `Visual:` (chart real, geração em runtime, modos).
- O design system em `../../design-systems/[sistema].md` — onde as classes desta tabela são definidas (CSS + template).
