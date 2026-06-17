# FICHA — Ciclo / loop

**Família:** D — Processo, sequência e mudança · **ID:** `ciclo-loop`

**Função didática.** Mostrar um processo que **se repete sem início nem fim fixos** — cada etapa alimenta a seguinte e a última volta à primeira. O trabalho na cabeça do aluno: entender a circularidade, que não há "passo final", que o sistema gira. É a forma circular que separa este tipo do passo-a-passo (linear, com começo e fim).

**Posição no arco.** Desenvolver. Bom para modelar sistemas que se retroalimentam (hábito, mercado, feedback) depois que as partes já foram apresentadas.

**Quando usar.** Há um processo cíclico ou um laço de retroalimentação: a saída de uma volta vira a entrada da próxima. De 3 a 6 etapas no anel.

**Quando NÃO usar.** Sequência com começo e fim definidos → [passo-a-passo](passo-a-passo.md). Cadeia causal que termina num efeito → [causa-efeito](causa-efeito.md). Estágios crescentes de maturidade que não voltam ao início → [progressao-jornada](progressao-jornada.md). Caminhos condicionais → [arvore-de-decisao](arvore-de-decisao.md).

**Anatomia (slots).**
- *Título-asserção* (obrigatório) — afirma o que o ciclo perpetua ("Cada venda financia o próximo anúncio, e o anel se sustenta"), não "O ciclo de X".
- *Etapas no anel* (obrigatório) — 3 a 6, dispostas em círculo, cada uma com rótulo curto.
- *Setas de retorno* (obrigatório) — fechando o anel, deixando inequívoco que gira e não acaba.
- *Ponto de entrada / ruptura* (opcional) — onde se entra no ciclo ou onde uma intervenção o quebra.

**Regras de carga.** 3 a 6 etapas (mais que 6 → o anel vira confusão; agrupe). Cada etapa: rótulo de 2–4 palavras. Setas todas no mesmo sentido de giro (horário ou anti-horário, nunca misturado). Sem texto longo dentro do nó.

**Build.** Recomendado: revele etapa a etapa girando o anel, e só feche a seta de retorno no fim — é o momento que entrega o "ah, volta ao começo". Revelação progressiva (lei 8) deixa a circularidade explícita.

**Decisão visual (roteamento).** **Modo 0** — anel, nós e setas em HTML/CSS/SVG, rótulos precisos e giro único. Nunca um diagrama de ciclo gerado por gerador de imagem (erra a direção das setas e os rótulos). Ver [../producao-visual.md](../producao-visual.md). Geração só para ilustração conceitual ao lado, fora do anel.

**Conexão posicional.** *Pede antes:* as etapas já nomeadas e a noção de que o sistema é contínuo. *Aponta para:* o ponto de intervenção que quebra o ciclo, um exemplo concreto, ou um contraste com um processo linear.

**Erro comum.** Desenhar um ciclo que na verdade é linear (sem seta de retorno real, vira passo-a-passo torto). Sentido de giro misturado. Etapas demais. Título-tópico.

**Por dial de fidelidade.** *Transcrição:* as etapas e o fechamento do anel saem do que o professor descreveu; não force circularidade num processo que ele apresentou como linear. *Esboço:* você modela o ciclo, podendo pesquisar a forma canônica, marcada para aprovação.
