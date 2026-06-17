# FICHA — Problema para resolver

**Família:** G — Processamento ativo · **ID:** `problema-para-resolver`

**Função didática.** Pôr um problema na tela para a **sala atacar** — o aluno resolve, não assiste. O trabalho na cabeça do aluno: aplicar o que aprendeu a um caso real, lutando com a dificuldade antes de ver a solução. Diferente do exemplo resolvido, que *mostra* a solução passo a passo; aqui a tela traz só o problema, e a resolução é da turma.

**Posição no arco.** Fim do Desenvolver ou no Consolidar, depois que o conceito e (idealmente) um exemplo resolvido já passaram. É o teste de transferência: aplicar sozinho o que foi modelado.

**Quando usar.** Quando o aluno já viu o método e precisa praticá-lo para que pegue. Quando lutar com o problema antes da solução vale mais que receber a solução pronta.

**Quando NÃO usar.** Antes de o método ter sido ensinado (aluno sem ferramenta trava e desiste — comece por [exemplo-resolvido](exemplo-resolvido.md)). Quando você quer demonstrar a solução, não cobrá-la → [exemplo-resolvido](exemplo-resolvido.md). Problema longo demais para o tempo de aula.

**Anatomia (slots).**
- *O enunciado* (obrigatório) — o problema, completo e sem ambiguidade, com tudo que é preciso para resolver.
- *Os dados/condições* (opcional) — o que está dado, separado do que se pede.
- *O que se pede* (obrigatório) — o alvo, explícito.
- *A solução* (obrigatório, por build) — escondida até a turma tentar; idealmente o caminho, não só o resultado.

**Regras de carga.** Um problema por slide. Enunciado limpo, dados separados do pedido. Dificuldade calibrada ao que foi ensinado (transferência próxima, não pegadinha). A solução nunca na tela antes do build.

**Build.** Central. O problema aparece, a turma tenta (sozinha, em par ou na lousa), e só então a solução é revelada — de preferência o raciocínio, não apenas a resposta. Sem o intervalo da tentativa, vira mais um exemplo resolvido.

**Decisão visual (roteamento).** **Modo 0** quase sempre — enunciado e solução em texto/diagrama, revelação por build. Dado numérico ou gráfico se renderiza de verdade, nunca via gerador de imagem. Imagem só se o problema for sobre uma cena/figura real → ver [../producao-visual.md](../producao-visual.md).

**Conexão posicional.** *Pede antes:* o método e, de preferência, um exemplo resolvido que o modele. *Aponta para:* a correção e a discussão dos erros — a tentativa da turma alimenta o fechamento do bloco.

**Erro comum.** Cobrar antes de ensinar o método. Enunciado ambíguo ou faltando dado. Revelar a solução junto (sem tentativa). Dar só o resultado sem o caminho (não ensina a resolver, só confirma). Problema fora do alcance do que foi dado.

**Por dial de fidelidade.** *Transcrição:* se o professor passou um exercício à turma, use o problema dele e a resolução que conduziu. Se não, você pode propor um problema de transferência sobre o conteúdo dado, marcado como adição, fiel ao método ensinado. *Esboço:* você cria o problema que melhor testa a aplicação do conceito do bloco.
