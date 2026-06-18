# FICHA — Analogia / metáfora

**Família:** F — Concretizar o abstrato · **ID:** `analogia-metafora`

**Função didática.** Ancorar o **novo no familiar**: mapear uma ideia abstrata sobre algo que o aluno já entende ("a corrente elétrica é como água num cano"). O trabalho na cabeça do aluno: importar uma estrutura mental pronta e reaproveitá-la, poupando o esforço de montar um esquema do zero. Funciona pela correspondência entre relações, não entre coisas.

**Posição no arco.** Desenvolver — no primeiro contato com um conceito difícil, antes ou logo após a definição formal. Também no Consolidar, como gancho de memória.

**Quando usar.** O conceito é abstrato ou contraintuitivo e existe um domínio familiar com a *mesma estrutura de relações*. Quando "isto é como aquilo que você já conhece" derruba a barreira de entrada.

**Quando NÃO usar.** Quando o que ilustra é um episódio real, não uma semelhança estrutural (→ [exemplo-caso](exemplo-caso.md)). Quando não existe domínio familiar que case bem — analogia forçada confunde mais que ajuda. Quando o conceito já é concreto.

**Anatomia (slots).**
- *Título-asserção* (obrigatório) — o mapeamento como afirmação. "A memória de trabalho é uma mesa pequena: cabe pouco de cada vez".
- *Domínio familiar* (obrigatório) — a coisa conhecida, mostrada (imagem/diagrama).
- *Mapeamento* (obrigatório) — quais partes correspondem a quais (rótulo junto, lei 7): cano→fio, pressão→tensão, fluxo→corrente.
- *Limite da analogia* (recomendado) — onde ela **para de valer**. Sem isto, vaza.

**Regras de carga.** Uma analogia por slide. Mapeie no máximo 3–4 correspondências — além disso vira quebra-cabeça. Domínio familiar de verdade (do mundo do aluno), não outro abstrato. O limite explícito sempre que houver risco de inferência errada.

**Build.** Admite: mostre o domínio familiar primeiro, depois sobreponha o mapeamento par a par, e por fim marque onde a analogia deixa de valer. Revelar o limite por último evita que o aluno superestenda.

**Decisão visual (roteamento).** Default **Modo 0** — o mapeamento é um diagrama de correspondências (HTML/CSS/SVG), rótulos editáveis e precisos lado a lado. **Modo 2** quando a metáfora pede uma cena conceitual e há gerador de imagem conectado (sem texto crítico na imagem) — senão fallback Modo 0/1. Roteamento em [../producao-visual.md](../producao-visual.md).

**Conexão posicional.** *Pede antes:* que o domínio familiar seja mesmo familiar à turma (checar). *Aponta para:* a definição formal que a analogia preparou, ou o caso/exemplo que a aterra no conteúdo real.

**Erro comum (o que mais derruba este tipo).** **Analogia que vaza** — o aluno estende a semelhança até um ponto onde ela é falsa e tira uma conclusão errada (se "elétron é uma bolinha", ele espera que orbite como planeta). Por isso o slot *limite* não é opcional quando há risco. Outros: domínio "familiar" que o aluno não conhece; mapear coisas em vez de relações; analogia tão elaborada que ensinar a analogia custa mais que ensinar o conceito.

**Por dial de fidelidade.** *Transcrição:* use a analogia do professor, mesmo imperfeita — é a voz dele e a turma a ouviu. Só adicione o slot *limite* se ele próprio sinalizou a fronteira. *Esboço:* você propõe a analogia, marcada para aprovação, e **declara explicitamente onde ela vaza** antes de usar. Analogias do professor têm prioridade; a que você criar entra marcada.
