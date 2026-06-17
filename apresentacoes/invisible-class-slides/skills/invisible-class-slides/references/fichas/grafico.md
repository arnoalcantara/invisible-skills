# FICHA — Gráfico (uma mensagem)

**Família:** E — Dados e quantidade · **ID:** `grafico`

**Função didática.** Trazer um dado correto à tela com **uma** mensagem para destacar — uma tendência, uma diferença, uma proporção. O trabalho na cabeça do aluno: ver o padrão (não decifrar uma planilha). O gráfico afirma visualmente o que o título já diz em palavras.

**Posição no arco.** Desenvolver (sustenta um ponto com evidência numérica) ou Consolidar (fecha um argumento com o dado que o prova).

**Quando usar.** Há um número que só faz sentido em comparação ou tendência (subiu, caiu, é maior, é a maior fatia). Quando o padrão *entre* valores é a mensagem.

**Quando NÃO usar.** Um único valor de impacto, sem comparação → [numero-grande](numero-grande.md). Quando a mensagem é "olhe ESTE ponto dentro do gráfico" → [destaque-sobre-dado](destaque-sobre-dado.md). Despejo de muitas séries sem foco → quebre ou simplifique.

**Anatomia (slots).**
- *Título-asserção* (obrigatório) — diz a conclusão, não o assunto. "As vendas dobraram após o lançamento", não "Vendas por mês" (lei 2).
- *Gráfico* (obrigatório) — barras, linha ou pizza, ponto focal. Eixos rotulados, escala honesta.
- *Realce da mensagem* (recomendado) — a barra/fatia/ponto que carrega a mensagem em cor de destaque; o resto esmaecido (lei 4).
- *Fonte* (opcional) — crédito discreto.

**Regras de carga.** Uma mensagem por gráfico. No máximo ~5–7 barras ou ~2–3 linhas; pizza com ≤ 5 fatias. Rótulo junto da barra/linha, não em legenda distante (lei 7). Sem grade pesada, sem 3D, sem efeito.

**Build.** Pode revelar eixos primeiro, depois plotar os dados, depois acender o realce — ou combinar com [predicao](predicao.md) ("para onde vai a curva?") antes de revelar.

**Decisão visual (roteamento).** **Modo 0, sempre.** Gráfico com dado real é renderizado de verdade em código/SVG (ou biblioteca de chart) — **NUNCA** vai a gerador de imagem: ele inventa número e desalinha eixo. Um gerador, se houver, no máximo estiliza fundo/moldura, jamais plota o dado. Regra de ouro, ver [../producao-visual.md](../producao-visual.md).

**Conexão posicional.** *Pede antes:* o que o eixo mede e por que importa (pré-treino, lei 9). *Aponta para:* a interpretação do padrão, ou um contraste com outro dado.

**Erro comum.** Título-tópico em vez de asserção. Mais de uma mensagem no mesmo gráfico (some o foco). Escala distorcida que mente sobre a magnitude. **Pior de todos: pedir o gráfico a um gerador de imagem** — número errado, eixo torto, e o erro é invisível para você e grave para o aluno.

**Por dial de fidelidade.** *Transcrição:* os números são exatamente os do professor — confira valor, unidade e escala. *Esboço:* se você traz o dado, marque a fonte e o status `[confirmar]`; nunca invente valores para "fechar" a curva.
