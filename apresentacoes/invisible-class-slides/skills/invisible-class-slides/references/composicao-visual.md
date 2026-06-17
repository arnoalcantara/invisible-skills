# Composição visual — o ofício de montar o slide

> **O que esta camada resolve.** A tipologia decide *qual* slide. As fichas dizem *o que* entra. As 13 leis dão o *princípio*. Faltava o **ofício**: como ocupar o quadro 1280×720 com hierarquia, peso e equilíbrio — fazer o slide *parecer desenhado*, não gerado. Esta reference é a mão que usa o ferramental do design system.
>
> **Agnóstica de marca.** Aqui só se fala de estrutura e princípio. As variantes citadas (`.hero`, `.center`, `.lead`, `.dense`, `.grid`, `.critical`, `.verdict`) e os primitivos (`.accent-bar`, `.index-numeral`, `.rule`) vivem na base de composição do design system; cor e fonte são do skin.
>
> **Quando aplicar.** Na Passada 2, ao instanciar cada slide, e de novo no **passo de Direção de Arte** (o checklist no fim), depois do HTML montado.

---

## 1. Princípio: o slide é dono do quadro

Cada slide possui 1280×720. Ocupá-lo é obrigação, não opção. **Conteúdo flutuando no meio de um mar de preto é defeito** — o erro mais comum e o que mais faz o deck parecer amador.

O espaço em branco é estrutura **quando trabalha** (lei 10): quando agrupa, separa ou hierarquiza. Quando é só sobra em volta de um parágrafo centralizado, não é respiro — é vazio. A pergunta a cada slide: *este vazio está fazendo um trabalho, ou é só conteúdo que não soube preencher a tela?*

Vazio que trabalha: a margem que isola a asserção-herói; a calha entre duas colunas; o ar acima de uma lista curta deliberadamente centralizada. Vazio que falha: 400px mortos abaixo da última linha de uma comparação top-anchored.

---

## 1-bis. Anti-monotonia: varie a silhueta entre slides vizinhos

O defeito que faz um deck inteiro parecer template não está em nenhum slide isolado — está na **repetição**. Quando todo slide tem a mesma forma, o olho desliga: a tela vira papel de parede. Dois antipadrões matam decks por reincidência:

1. **"Título em cima + fileira de caixas cinza"** repetido slide após slide. Cada um é defensável; quinze seguidos são um campo cinza chapado.
2. **"Frase solta centralizada no preto"** repetida. Uma é dramática; dez são um deck que não soube preencher a tela.

A regra: **se o slide N tem uma silhueta, o N+1 tem outra.** Alterne o registro — tipográfico (`.hero`, `.emphasis`) → diagrama (`.flow.chain`/`.cycle`/`.tree`) → assimétrico (`.slide-rail`, `.slide-number`) → contraste (`.slide-contrast`) → comparação. Não é "use todo componente em toda aula" — novidade forçada é tão ruim quanto monotonia. É **não repetir a mesma forma em sequência**. Uma asserção limpa top-anchored é silhueta válida; três seguidas, não.

Pense na sequência como ritmo, não como grade: variação de forma é o que mantém a sala acordada entre um slide e o próximo.

---

## 2. Preencher o quadro (sem encher de filler)

Três movimentos, nesta ordem de preferência:

1. **Escalar o foco.** Slide com pouco conteúdo? O elemento focal cresce até *merecer* a tela. Uma asserção curta vira asserção-herói (`.hero`, `--font-display` grande). Uma lista de três itens vira lista-lead (`.lead`, itens grandes). Não se centraliza texto miúdo num vazio — aumenta-se o foco.
2. **Ancorar.** O default é top-anchored: título em cima, conteúdo desce a partir dele, alinhado ao topo. Centralizar no vertical (`.center`) é decisão consciente, reservada a quando há **um** bloco visual dominante (um diagrama, uma imagem, uma citação) que pede o centro óptico.
3. **Apoiar com elemento estrutural.** Quando o conteúdo é genuinamente pouco e não deve crescer, um primitivo dá peso e função: uma `.accent-bar` que ancora o foco, um `.index-numeral` que marca a posição na sequência, uma `.rule` que separa zonas. São estruturais (cumprem lei 4/10), nunca enfeite (lei 3).

Nunca preencher com texto inventado, ícone decorativo, ou repetir a fala do professor só para "ter algo" (viola lei 6).

---

## 2-bis. Lidere com tipografia, não com caixa

A caixa é o **último** recurso, não o primeiro. O reflexo de fechar todo conteúdo num retângulo de borda cinza é o que mais entope o deck e dilui o acento (que fica preso em labels de 13px). Antes de abrir uma `.fbox`, pergunte: *isto precisa de moldura, ou só de hierarquia?*

A relação entre N coisas raramente é N retângulos. Quase sempre é outra forma:

- **Cadeia causal** → `.flow.chain` (nós sem caixa, ligados por seta), não três caixas em fila.
- **Equívoco vs. correto** → `.slide-contrast` (assimétrico), não duas caixas espelhadas.
- **Hierarquia / ramificação** → `.flow.tree`, não caixas soltas.
- **Ênfase de uma frase** → `.emphasis` (display 900, palavra-chave em acento), não uma caixa com texto dentro.

A caixa só se justifica quando o conteúdo é **genuinamente paralelo e comparável** (itens da mesma natureza, lado a lado). Mesmo aí, escolha o **tratamento por função** — `.fill`, `.hairline`, `.edge` — nunca a borda-padrão por inércia. E o acento mora em **um** lugar de peso: uma aresta (`.edge`), o conector de um paralelo, o elo de virada (`.turn`), a palavra-chave (`<span class="accent">`). Coral diluído em seis labels não acentua nada.

---

## 3. Hierarquia de foco (lei 4)

Um ponto focal por slide. A ordem de leitura — primeiro, segundo, terceiro — tem que ser legível em **um segundo**. Constrói-se com quatro alavancas:

- **Tamanho:** o focal é nitidamente maior. Sem timidez — a diferença entre 38px e 30px não cria hierarquia; entre 64px e 26px, cria.
- **Peso:** display 900 vs. corpo 400.
- **Cor:** o acento (coral) marca **um** elemento. Branco para o primário, prata para o secundário, muted para o terciário.
- **Posição:** o que vem primeiro no quadro (alto, à esquerda) lê-se primeiro.

Se tudo grita, nada se ouve. Um slide com três coisas do mesmo tamanho não tem foco — tem três rascunhos de foco. Promova uma, rebaixe as outras (`.row.primary` vs. `.row`, `.li-sub` sob o item).

---

## 4. Densidade e respiro

O layout casa com o volume de conteúdo — não há padding único para tudo.

- **Esparso** (1–2 blocos curtos): escalar o foco (`.hero`, `.lead`) ou centralizar com apoio estrutural. Aumentar a margem é parte do design, não desleixo.
- **Médio** (o caso comum): top-anchored, ritmo da escala de espaçamento, respiro entre zonas.
- **Denso** (muitos itens legítimos): apertar o gap (`.dense`), agrupar (`.row-group`), reduzir o corpo um passo. Se ainda não cabe com respiro, é sinal de que são **dois slides** (ver §5).

O respiro entre elementos vem da escala (8/12/16/24/32/48/64/80), não de números soltos. Itens da mesma zona ficam perto (gap menor); zonas diferentes ficam longe (gap maior). A distância comunica relação.

---

## 5. Quando quebrar um slide

Uma ideia por slide (lei 1) é também decisão de composição. Quebre quando:

- A evidência tem **3+ parágrafos densos + um diagrama** — vira slide de asserção + slide de diagrama.
- Há **duas asserções defensáveis** competindo pelo título.
- O diagrama tem **mais de 6 caixas** — ou reagrupa em famílias, ou vira dois.
- A lista passa de **~6 itens** com respiro — quebrar ou hierarquizar em grupos.

Quebrar não é perder conteúdo; é dar a cada ideia o quadro que ela merece. Dois slides limpos batem um slide entupido. O custo (mais um avanço) é barato; o ganho (foco) é caro.

---

## 6. Peso e equilíbrio

- **Assimetria proposital.** Centralizar tudo é o default preguiçoso. Um bloco forte à esquerda com ar à direita tem mais tensão e direção que um bloco no meio. O `.slide-number` (número pesado à esquerda, contexto à direita) é o modelo.
- **Equilíbrio óptico, não matemático.** Um numeral grande e claro pesa mais que um parágrafo cinza — equilibre por peso visual, não por contagem de pixels.
- **O acento é o único momento de peso de cor.** Coral em um lugar, com função. Dois corais no mesmo slide dividem o foco e anulam os dois (lei 3, lei 4).

---

## 7. Disciplina de grid

- **Espaçamento pela escala.** Todo gap e margem sai de 8/12/16/24/32/48/64/80. Número fora da escala é ruído — alinha o olho a um ritmo invisível.
- **Alinhamento.** Bordas de texto e caixas compartilham linhas verticais. O título-asserção, a primeira linha da evidência e o rodapé alinham à mesma margem esquerda.
- **Margem coerente.** A margem externa do slide é estável dentro de um mesmo tipo — o conteúdo muda, a moldura não treme de um slide para o outro.

---

## 8. Receitas por tipo de alta frequência

Os workhorses, onde mora 80% do deck. Para os demais tipos, os princípios §1–§7 bastam.

**Asserção + evidência (`asseracao-evidencia`).** O caso comum é top-anchored: label + `.assert-title` no topo, evidência descendo alinhada ao topo, primeira linha como `.lead`. Se a evidência é **um** visual dominante (diagrama/imagem/citação), use `.center`. Se a evidência é magra e não cresce, vire **asserção-herói** (`.hero`): a frase é o slide, `.accent-bar` acima, sub-linha de apoio abaixo. Nunca dois parágrafos curtos boiando no centro.

**Diagrama (`slide-diagram` e família de processo).** Até 4 caixas: linha (`.flow`) com setas. **5–6 caixas: grid** (`.flow.grid`, 3×2; ou `.cols-2` para 2×2) — nunca seis caixas espremidas numa linha de 200px. O passo-chave ganha `.critical` (borda de acento). O índice (`.fn`) é estrutural e legível — dá peso à caixa e marca a sequência, não é fundo fantasma. Em grid, a leitura é por número, não por seta.

**Comparação (`comparacao-lado-a-lado`, trade-off).** Colunas com header de presença (não label miúdo), conteúdo equilibrado no vertical, dimensões **alinhadas entre as colunas** (mesma linha = mesma dimensão). Agrupe sub-itens com `.row-group`. Quando há veredito (uma coluna vence), marque com `.verdict` no rodapé da coluna — o acento entra aqui, uma vez.

**Lista (`slide-list`: objetivos, síntese, roteiro).** Poucos itens (3–4): `.lead`, itens grandes, preenchem o quadro. Muitos (5–6): ritmo normal ou `.dense`. Detalhe secundário sob um item vai em `.li-sub`, não vira item novo. Lista nunca é a fala do professor copiada (lei 6) — é a estrutura, o esqueleto.

**Contraste (`erro-comum`, `antes-depois`) → `.slide-contrast`.** Equívoco e correto **assimétricos**, não espelhados: o errado é hairline e esmaecido (`.side.wrong`), o certo é preenchido e carrega o acento numa aresta (`.side.right`). A distinção vem de rótulo + posição + aresta — **nunca só de cor** (acessibilidade, regra da ficha). Para o build "mostra erro → revela correto", `.contrast.stack` empilha e o lado certo entra como `.fragment`. *Gate:* há uma confusão real a desarmar, não só duas opções neutras (isso é comparação).

**Textos paralelos (`paralelo-textos`) → `.slide-parallel`.** Dois textos correspondentes (promessa/cumprimento, lei/evangelho, citação/eco) em `.ptext` **sem borda**, lidos como passagem, ligados por um `.connector` central que nomeia a relação ("cumpre-se em") e carrega o acento **uma vez**. *Gate:* os dois textos são genuinamente correspondentes — um ecoa, cumpre ou responde o outro. Para dois itens só comparados nas mesmas dimensões, use `.slide-two-col`.

**Cadeia causal (`causa-efeito`) → `.flow.chain`.** Nós **sem caixa** (`.cnode`: palavra-chave sobre um tick de acento) ligados por setas SVG em `--accent-dim`, com `.carrow-label` só quando o nexo precisa ser nomeado. O elo de virada ganha `.turn`. Cadeia longa ou com build → `.chain.vertical`. *Gate:* cada elo **causa** o próximo (não é mera sequência temporal — isso é passo-a-passo).

**A forma do diagrama casa o conceito.** Antes de cair no row de caixas, pergunte que forma a relação *tem*: processo que **retorna ao início** → `.flow.cycle` (a única forma que um row de caixas não finge); **ramificação / condição** → `.flow.tree` (com `.tree.decision` para sim/não); **cadeia** → `.flow.chain`; sequência ou conjunto paralelo → grid/flow. A forma errada mente sobre a relação; a certa a ensina sem uma palavra.

---

## 9. Checklist de Direção de Arte (passo de QA da Passada 2)

Depois de montar o HTML, percorra **cada slide** e responda. Qualquer "não" → recomponha com o ferramental da base antes de entregar.

1. **Quadro.** O conteúdo ocupa a tela, ou flutua num vazio morto? (Se flutua: escalar foco, ancorar, ou apoiar — §2.)
2. **Foco.** Há **um** ponto focal, legível em 1 segundo? A ordem de leitura é óbvia? (§3)
3. **Densidade.** O layout casa com o volume? Está apertado (quebrar) ou rarefeito (escalar/centralizar)? (§4, §5)
4. **Diagrama.** Alguma fileira de caixas espremida que pede grid? Passo-chave destacado? Índices legíveis? (§8)
5. **Hierarquia.** Primário, secundário e terciário se distinguem por tamanho/peso/cor — ou está tudo no mesmo cinza chapado? (§3)
6. **Acento.** O coral aparece em **um** lugar por slide, com função? (§6)
7. **Grid.** Margens, gaps e alinhamentos saem da escala e batem entre si? A moldura é estável entre slides do mesmo tipo? (§7)
8. **Inline / improviso.** Há algum `style="…"` ou classe inventada com CSS próprio? → mover o tratamento para a base; o componente certo já existe ou deve ser criado lá. (§2-bis)
9. **Monotonia.** Os últimos 3 slides têm formas diferentes, ou estão repetindo "fileira de caixas" / "frase no centro"? (§1-bis)
10. **Caixa justificada?** Cada `.fbox` está aí por função (conteúdo paralelo e comparável) ou por inércia? Caberia melhor em `.chain`/`.contrast`/`.tree`/`.emphasis`? (§2-bis)
11. **Acento concentrado.** O coral está num **lugar de peso** (aresta, conector, `.turn`, palavra-chave), ou diluído em labels pequenos? (§6)
12. **Regressão de marca.** Sem gradiente (exceto overlay de imagem), sem sombra, sem emoji, sem radius acima do `--radius` do brand; tipografia nos pisos de legibilidade (lei 11).

O objetivo do passo não é "checar" — é **recompor**. Encontrou vazio morto, diagrama espremido, hierarquia chapada? Conserte ali, com a variante ou o primitivo certo. É o segundo olhar que separa o deck que entende a aula do deck que também a *mostra* bem.
