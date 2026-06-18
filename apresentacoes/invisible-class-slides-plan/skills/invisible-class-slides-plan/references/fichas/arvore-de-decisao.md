# FICHA — Árvore de decisão / fluxograma

**Família:** D — Processo, sequência e mudança · **ID:** `arvore-de-decisao`

**Função didática.** Mostrar **caminhos condicionais** — "se X, então A; se não, então B" — onde o percurso depende de uma resposta a cada bifurcação. O trabalho na cabeça do aluno: saber *escolher* o caminho diante de uma condição, internalizando a regra de decisão. A ramificação é o que separa este tipo do passo-a-passo (linha única, sem escolha).

**Posição no arco.** Desenvolver, ou consolidar. Bom para transformar um critério em ferramenta de decisão ("quando usar o quê") depois que as opções já foram apresentadas.

**Quando usar.** A ação correta depende de condições e há bifurcações de "se… então…": um critério de triagem, um fluxo de diagnóstico, um "qual escolher dado o caso". De 2 a 4 pontos de decisão.

**Quando NÃO usar.** Sequência linear sem escolhas → [passo-a-passo](passo-a-passo.md). Cadeia causal sem decisão → [causa-efeito](causa-efeito.md). Processo que se repete → [ciclo-loop](ciclo-loop.md). Categorias sem decisão (só classificação) → taxonomia.

**Anatomia (slots).**
- *Título-asserção* (obrigatório) — afirma a regra que a árvore entrega ("Se a dúvida é factual, pesquise; se é de gosto, decida e siga"), não "Árvore de decisão".
- *Nós de decisão* (obrigatório) — 2 a 4, cada um com uma pergunta de sim/não ou de poucas saídas.
- *Ramos rotulados* (obrigatório) — cada saída marcada com a condição que a aciona ("sim" / "não" / o caso), junto da seta (lei 7).
- *Nós-folha* (obrigatório) — os desfechos/ações ao fim de cada caminho.

**Regras de carga.** 2 a 4 decisões (mais → o aluno se perde na árvore; quebre por caso em slides sucessivos). Pergunta de cada nó: uma frase curta. Toda saída rotulada — ramo sem rótulo é o erro fatal aqui. Layout de cima para baixo ou da esquerda para a direita, direção única.

**Build.** Fortemente recomendado: revele decisão a decisão, percorrendo um caminho de cada vez, em vez de despejar a árvore inteira. A revelação progressiva (lei 8) impede que a ramificação vire um emaranhado e deixa o aluno acompanhar a lógica do percurso.

**Decisão visual (roteamento).** **Modo 0** — nós, ramos e rótulos em HTML/CSS/SVG, com cada condição precisa na seta. Nunca um fluxograma gerado por gerador de imagem: é o pior caso para o modelo, que erra setas, ramos e rótulos — exatamente o que carrega o sentido. Ver [../producao-visual.md](../producao-visual.md). Geração não tem papel aqui além de fundo neutro.

**Conexão posicional.** *Pede antes:* o vocabulário das condições e das opções de saída já nomeadas. *Aponta para:* um exemplo que percorre a árvore num caso real, ou um problema onde o aluno decide o caminho.

**Erro comum.** Ramo sem rótulo de condição (o aluno não sabe o que dispara cada saída). Decisões demais numa árvore só. Misturar decisão com mero passo sequencial. Título-tópico.

**Por dial de fidelidade.** *Transcrição:* os nós, as condições e os desfechos saem do critério que o professor expôs; não invente uma bifurcação para "cobrir todos os casos". *Esboço:* você estrutura a árvore, podendo pesquisar o critério canônico, marcado para aprovação.
