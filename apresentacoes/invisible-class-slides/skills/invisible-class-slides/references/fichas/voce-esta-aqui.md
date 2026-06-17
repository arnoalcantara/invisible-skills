# FICHA — Você está aqui

**Família:** A — Orientação e estrutura · **ID:** `voce-esta-aqui`

**Função didática.** Retomar o mapa da aula destacando o progresso: mostra o que já foi percorrido, onde o aluno está agora e o que falta. Combate a desorientação em aulas longas e mantém a consciência posicional (lei 13). Re-ancora a moldura mental criada no roteiro.

**Posição no arco.** Recorrente, nas viradas de bloco de aulas longas. Sempre depois que um roteiro já estabeleceu o mapa.

**Quando usar.** Aula longa com vários blocos, onde o aluno corre risco de perder o fio; tipicamente nas transições, reusando o slide de roteiro com o bloco atual marcado.

**Quando NÃO usar.** Aula curta ou sem roteiro prévio → não há mapa a retomar; use [divisor-secao](divisor-secao.md) para só marcar a virada. Se o objetivo é costurar o argumento entre blocos, não rastrear posição → [ponte-transicao](ponte-transicao.md).

**Anatomia (slots).** *Mapa (a mesma lista do roteiro)* (obrig., idêntico em ordem e rótulos ao [roteiro-agenda](roteiro-agenda.md) — consistência é o que faz funcionar). *Marcação de progresso* (obrig.: feito / atual / a fazer, por cor ou estado visual). *Destaque do bloco atual* (obrig., ponto focal único — lei 4). *Título-asserção* (opc., pode reafirmar o percurso).

**Regras de carga.** Reusa o roteiro, então herda seu limite (3–5 blocos). O estado (feito/atual/futuro) deve ser legível num relance, sem o aluno decifrar legenda. Nada além do mapa e do marcador.

**Build.** Admite uma micro-revelação: mostrar o mapa e então acender o bloco atual, marcando a transição. Mais comum é estático com o atual já destacado.

**Decisão visual (roteamento).** **Modo 0** — herda o layout do roteiro, só muda o estado visual dos itens (cor/opacidade). HTML/CSS puro. Não vai para gerador de imagem. Ver [../producao-visual.md](../producao-visual.md).

**Conexão posicional.** *Pede antes:* o [roteiro-agenda](roteiro-agenda.md) que definiu o mapa; o fechamento do bloco anterior. *Aponta para:* o conteúdo do bloco que está sendo aberto. Frequentemente aparece colado a um [divisor-secao](divisor-secao.md).

**Erro comum.** Mapa que diverge do roteiro original (ordem ou rótulos diferentes) — quebra o reconhecimento. Marcação de progresso ambígua (não dá pra ver onde está). Repetir com frequência alta demais e virar ruído.

**Por dial de fidelidade.** *Transcrição:* o progresso reflete os marcos reais da aula gravada; só insira nos pontos onde o professor de fato fez balanço ou virou de fase. *Esboço:* você decide os pontos de re-orientação a partir do tamanho e da complexidade dos blocos planejados.
