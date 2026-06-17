# FICHA — Erro comum / equívoco

**Família:** H — Reforço e fechamento · **ID:** `erro-comum`

**Função didática.** Antecipar e **desarmar a confusão clássica** — o erro que quase todo aluno comete, a intuição errada que parece certa. O trabalho na cabeça do aluno: confrontar a própria concepção equivocada (que muitas vezes ele nem sabe que tem) e substituí-la. A pesquisa mostra que *nomear* explicitamente o erro e contrastá-lo com o correto fixa melhor do que só ensinar o certo.

**Posição no arco.** Consolidar (depois de ensinar o correto, blinda contra o erro) ou Desenvolver (quando o erro é tão comum que vale enfrentá-lo de frente ao introduzir o conceito).

**Quando usar.** Há uma confusão recorrente, uma armadilha previsível, uma intuição que engana. Especialmente valioso quando o erro é "natural" e o aluno chega com ele pronto.

**Quando NÃO usar.** Para erros raros ou idiossincráticos (não vale o slide). Quando apontar o erro só confunde quem ainda não o cometeu (às vezes é melhor ensinar o certo direto). Vários erros num slide (dilui).

**Anatomia (slots).**
- *Título-asserção* (obrigatório) — nomeia o equívoco ou afirma o correto.
- *O erro* (obrigatório) — a concepção equivocada, enunciada com clareza (e empatia — é uma intuição compreensível).
- *O correto* (obrigatório) — em contraste visual direto com o erro.
- *Por que enganava* (opcional, recomendado) — a raiz da confusão, o que a torna sedutora.
- *Marcação visual* (recomendado) — distinção clara entre "errado" e "certo" (sem depender só de vermelho/verde — acessibilidade).

**Regras de carga.** Um erro por slide. Erro e correto lado a lado ou em sequência clara. Cada um curto. A distinção visual não pode depender exclusivamente de cor.

**Build.** Recomendado: mostre o erro primeiro (talvez peça à turma se concorda — combina com [predicao](predicao.md)), deixe a tensão, e então revele o correto. O contraste fica mais forte com o intervalo.

**Decisão visual (roteamento).** **Modo 0** — `.slide-contrast`: equívoco e correto **assimétricos**, o errado em hairline esmaecido (`.side.wrong`), o certo preenchido com aresta de acento (`.side.right`); distinção por rótulo + posição + aresta, nunca só cor. Para o build erro→correto, `.contrast.stack` com o lado certo em `.fragment`. Não roteia para gerador. Se o erro é visual (um gráfico mal lido, uma figura), mostre a figura pelo caminho próprio.

**Conexão posicional.** *Pede antes:* o conceito correto já apresentado (em geral). *Aponta para:* a consolidação/takeaway, ou uma verificação que confirma que o erro foi desarmado.

**Erro comum (da ficha).** Apresentar o erro sem deixar claro qual é o certo (reforça a confusão). Tom de deboche (humilha quem errou, fecha o aluno). Mostrar erro e certo juntos sem contraste visível. Depender só de cor para distinguir.

**Por dial de fidelidade.** *Transcrição:* use os erros que o professor apontou — ele conhece os da turma dele. Não invente um equívoco que ele não mencionou. *Esboço:* você traz os equívocos conhecidos do tema (pode pesquisar), marcados para aprovação.
