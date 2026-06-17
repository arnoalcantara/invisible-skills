# FICHA — Textos paralelos / correspondência

**Família:** C — Estrutura e relações · **ID:** `paralelo-textos`

**Função didática.** Pôr **dois textos correspondentes** lado a lado (ou em sequência vertical) e tornar visível a **relação** entre eles: um cumpre, ecoa, responde ou contradiz o outro. O trabalho na cabeça do aluno: ver que as duas passagens não são independentes — uma ilumina a outra. É o tipo natural para promessa/cumprimento, profecia/realização, lei/evangelho, citação/eco, original/paráfrase.

**Posição no arco.** Desenvolver. Vem quando os dois textos já foram (ou serão) lidos e o ponto é a **ligação** entre eles, não cada um isolado.

**Quando usar.** Há dois trechos textuais genuinamente correspondentes e a mensagem é o nexo entre os dois ("o que A anuncia, B consuma"). Especialmente forte em conteúdo bíblico, literário, jurídico e doutrinário, onde a correspondência entre fontes *é* o argumento.

**Quando NÃO usar.** Dois itens comparados nas mesmas dimensões (prós/contras, A vs. B) → [comparacao-lado-a-lado](comparacao-lado-a-lado.md). Um equívoco contra o correto → [erro-comum](erro-comum.md) (`.slide-contrast`). Um único texto a ser marcado/anotado no lugar → [exemplo-anotado](exemplo-anotado.md). Uma sequência causal entre ideias → [causa-efeito](causa-efeito.md).

**Anatomia (slots).**
- *Título-asserção* (obrigatório) — afirma a relação ("O que Isaías anuncia, o Apocalipse consuma"), não "Dois textos".
- *Texto A* (obrigatório) — a primeira passagem, com sua referência (`.pref`). Lido como passagem (display itálico, sem caixa).
- *Conector* (obrigatório) — o elo central que **nomeia** a relação ("cumpre-se em", "ecoa", "responde a") e carrega o acento uma vez. Glifo geométrico + régua em acento esmaecido.
- *Texto B* (obrigatório) — a segunda passagem, no mesmo registro de A.
- *Nexo anotado* (opcional) — uma linha curta dizendo *por que* correspondem, se não for óbvio.

**Regras de carga.** Exatamente dois textos (é a essência do tipo; três viram lista). Cada passagem curta — o trecho que carrega a correspondência, não o capítulo inteiro. Os dois no mesmo registro tipográfico (paralelismo visual = paralelismo de conteúdo). O conector nomeia a relação em 1–3 palavras. O acento vive só no conector.

**Build.** Recomendado: mostre o Texto A, deixe assentar, então revele o conector + Texto B — a correspondência "fecha" na frente do aluno. Combina com [predicao](predicao.md) ("onde isso se cumpre?").

**Decisão visual (roteamento).** **Modo 0** — `.slide-parallel` em HTML/CSS, dois `.ptext` sem borda ligados pelo `.connector`. Nunca gerar a passagem por modelo de imagem (inventa ou corrompe o texto — erro grave em conteúdo de fonte). Fidelidade textual é inegociável.

**Conexão posicional.** *Pede antes:* as duas passagens já lidas, ou ao menos a primeira. *Aponta para:* a síntese do que a correspondência prova, ou um exemplo de como ela se aplica.

**Erro comum.** Pôr dois textos que não correspondem de verdade (correspondência forçada). Citação imprecisa (em conteúdo de fonte, citar errado é falha grave). Tratar como comparação de prós/contras. Conector vago que não nomeia a relação. Título-tópico.

**Por dial de fidelidade.** *Transcrição:* as duas passagens e o nexo saem do que o professor de fato ligou — não invente uma correspondência que ele não afirmou, e cite ao pé da letra. *Esboço:* você pode trazer a passagem correspondente canônica (pesquisada), marcada para aprovação, sem afirmar um cumprimento que a fonte não sustenta.
