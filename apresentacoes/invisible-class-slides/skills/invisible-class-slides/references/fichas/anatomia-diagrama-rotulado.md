# FICHA — Anatomia / diagrama rotulado

**Família:** C — Estrutura e relações · **ID:** `anatomia-diagrama-rotulado`

**Função didática.** Mostrar as **partes de um todo** e nomeá-las **no lugar** (lei 7, contiguidade espacial). O trabalho na cabeça do aluno: associar cada nome à sua posição/função sem o olho viajar entre figura e legenda distante. É como o aluno aprende a "ler" uma estrutura — um órgão, uma máquina, uma frase, uma molécula, um sistema.

**Posição no arco.** Desenvolver. Frequentemente um pré-treino (lei 9): nomear as peças antes de explicar como o todo funciona.

**Quando usar.** Há um objeto/estrutura com partes que precisam ser identificadas e localizadas. Quando saber *onde* cada parte está importa para entender a função.

**Quando NÃO usar.** Sequência de etapas → [passo-a-passo](passo-a-passo.md). Relação abstrata sem objeto físico/espacial → outra família. Quando as partes não têm posição relativa relevante → uma lista basta.

**Anatomia (slots).**
- *Título-asserção* (obrigatório) — afirma o que a estrutura faz/revela, não "Partes do X".
- *A figura/diagrama* (obrigatório) — o objeto, ocupando o peso visual central.
- *Rótulos in loco* (obrigatório) — cada nome junto da parte, ligado por linha curta se necessário. Nunca uma legenda numerada à parte.
- *Destaque da parte em foco* (opcional) — se a explicação trata de uma parte por vez.

**Regras de carga.** Quantos rótulos a estrutura exigir, mas raramente >7 de uma vez (se for muito, revele por grupos). Rótulo = nome curto, não definição. Linhas de chamada curtas e sem cruzamento. Um objeto por slide.

**Build.** Recomendado quando há muitas partes: revele rótulo por rótulo conforme nomeia, ou acenda grupos funcionais um de cada vez. Reduz o "muro de rótulos" inicial.

**Decisão visual (roteamento).** Depende da figura. Se a estrutura pode ser desenhada esquematicamente → **Modo 0** (SVG/HTML), com rótulos precisos e editáveis — ideal. Se exige uma imagem realista (anatomia humana, um instrumento real) → Modo 1 (stock) ou Modo 2 (geração da figura **sem texto**, rótulos sobrepostos na camada do slide). **Nunca** deixe o modelo de imagem escrever os rótulos (erra e fica ilegível).

**Conexão posicional.** *Pede antes:* o contexto do objeto. *Aponta para:* a explicação de como as partes interagem (função, processo), ou um exemplo anotado.

**Erro comum.** Rótulos em legenda distante numerada (1, 2, 3 → tabela ao lado) — viola a lei 7 e força o olho a viajar. Linhas de chamada que se cruzam. Rótulos demais de uma vez. Deixar o gerador "cozinhar" os rótulos na imagem.

**Por dial de fidelidade.** *Transcrição:* rotule as partes que o professor nomeou, com os termos dele. Não adicione partes que ele não tratou. *Esboço:* você monta o diagrama canônico, podendo pesquisar a estrutura, marcado para aprovação.
