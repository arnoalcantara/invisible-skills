# FICHA — Causa-efeito / cadeia

**Família:** D — Processo, sequência e mudança · **ID:** `causa-efeito`

**Função didática.** Tornar visível uma **cadeia causal**: A leva a B, que leva a C. O trabalho na cabeça do aluno: entender que os elos não são independentes — um *produz* o seguinte. O que distingue este tipo do passo-a-passo é a relação: aqui cada elo é a *causa* do próximo, não só a etapa anterior dele.

**Posição no arco.** Desenvolver. Vem quando o aluno já conhece os elementos isolados e precisa ver como um dispara o outro. Boa para explicar mecanismos e consequências.

**Quando usar.** Há uma relação de causalidade encadeada (3 a 5 elos), em que cada elo explica o seguinte. Mecanismos, efeitos em cascata, consequências de uma decisão.

**Quando NÃO usar.** Etapas de um procedimento, onde a ordem importa mas não há causalidade → [passo-a-passo](passo-a-passo.md). Eventos só ordenados no tempo, sem nexo causal afirmado → [linha-do-tempo](linha-do-tempo.md). Processo que se realimenta e volta ao começo → [ciclo-loop](ciclo-loop.md). Caminhos condicionais → [arvore-de-decisao](arvore-de-decisao.md).

**Anatomia (slots).**
- *Título-asserção* (obrigatório) — afirma o nexo causal ("Cortar o sono derruba a memória no dia seguinte"), não "Causas e efeitos".
- *Elos* (obrigatório) — 3 a 5 caixas, cada uma com rótulo curto.
- *Setas causais* (obrigatório) — direção única, ligando cada causa ao seu efeito. Rótulo na seta ("por isso", "o que provoca") quando o nexo precisa ser nomeado.
- *Destaque do elo de virada* (opcional) — o ponto onde a cadeia se torna irreversível ou crítica.

**Regras de carga.** 3 a 5 elos (mais que isso, a cadeia vira diagrama de sistema — quebre ou simplifique). Cada elo: rótulo de 2–4 palavras. Uma só direção de leitura. Rótulo de seta só quando o nexo não é óbvio — não polua todas as setas.

**Build.** Fortemente recomendado: revele elo a elo, narrando o nexo de cada um. É onde a revelação progressiva (lei 8) mais rende neste tipo — o aluno acompanha a corrente sendo montada e não pula para a conclusão. Veja [../producao-visual.md](../producao-visual.md).

**Decisão visual (roteamento).** **Modo 0** — caixas e setas em HTML/CSS/SVG, com rótulos precisos. Nunca um diagrama causal gerado por gerador de imagem (erra setas, troca rótulos, inverte o sentido da causa). Geração só para uma ilustração conceitual ao lado de um elo, se necessário.

**Conexão posicional.** *Pede antes:* os elementos da cadeia já nomeados e o porquê de importarem. *Aponta para:* uma síntese da consequência final, um exemplo que mostra a cadeia rodando, ou um ponto de processamento (o aluno prevê o próximo elo).

**Erro comum.** Confundir sequência temporal com causa ("veio depois" não é "foi causado por"). Setas em mais de uma direção. Elos demais virando teia. Título-tópico. Afirmar nexo causal que o conteúdo não sustenta.

**Por dial de fidelidade.** *Transcrição:* a cadeia sai exatamente do nexo que o professor afirmou; não invente elos intermediários para "fechar a lógica". *Esboço:* você estrutura a cadeia, podendo pesquisar o mecanismo canônico, marcado para aprovação — e sem afirmar causalidade que a fonte não confirma.
