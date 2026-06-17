# FICHA — Destaque sobre dado

**Família:** E — Dados e quantidade · **ID:** `destaque-sobre-dado`

**Função didática.** Apontar **o que olhar** dentro de um dado ou gráfico — guiar o olho ao ponto que importa com anotação, seta ou realce sobre o próprio gráfico. O trabalho na cabeça do aluno: não procurar sozinho onde está a mensagem; o slide já leva o olho até ela (sinalização de Mayer). É o gráfico com o dedo apontando.

**Posição no arco.** Desenvolver — logo após apresentar um gráfico, quando você precisa dirigir a atenção a um pico, uma quebra, um outlier. Também no Consolidar, marcando no dado o ponto que se deve lembrar.

**Quando usar.** O gráfico já está na tela (ou acabou de aparecer) e há um lugar específico nele que carrega a ideia. Quando o risco é o aluno olhar o dado inteiro e não saber para onde olhar.

**Quando NÃO usar.** Ainda não há gráfico para anotar → mostre primeiro com [grafico](grafico.md). A mensagem é o dado inteiro, sem um ponto específico → o próprio gráfico com realce basta. Um único valor sem contexto de gráfico → [numero-grande](numero-grande.md).

**Anatomia (slots).**
- *Base de dado* (obrigatório) — o gráfico/tabela que recebe a marcação, renderizado de verdade.
- *Marcação* (obrigatório) — seta, círculo, faixa ou realce de cor sobre o ponto exato. Um foco só (lei 4).
- *Anotação-asserção* (recomendado) — a frase curta colada à marcação que diz o que aquilo significa. "Aqui a curva inverte", junto do ponto (lei 7).
- *Atenuação do resto* (recomendado) — o entorno recua (cinza, opacidade) para o destaque saltar.

**Regras de carga.** **Um** ponto de destaque por slide. Se há dois lugares a marcar, são dois slides ou um build. A anotação é curta (≤ ~8 palavras) e fica junto da marca, nunca em legenda distante. Sem múltiplas setas competindo.

**Build.** Forte aqui: mostre o gráfico limpo, deixe o aluno olhar, **depois** revele a marcação e a anotação. Combina com [predicao](predicao.md) — pergunte onde está a virada antes de apontar.

**Decisão visual (roteamento).** **Modo 0 — sempre.** Marcação e atenuação são camadas em HTML/CSS/SVG sobre o gráfico real. **Gráfico com dado real NUNCA vai a gerador de imagem** (inventa número, desalinha eixo); a anotação também é texto editável na camada do slide, jamais cozida numa imagem. Ver [../producao-visual.md](../producao-visual.md).

**Conexão posicional.** *Pede antes:* o gráfico-base apresentado e lido em forma geral. *Aponta para:* a explicação do porquê daquele ponto, uma consequência, ou um contraste com outro trecho do dado.

**Erro comum.** Várias setas/realces de uma vez (some o foco, viola lei 4). Anotação longe da marca (o olho viaja, viola lei 7). Anotar um gráfico gerado por modelo de imagem — o dado abaixo da seta pode estar errado. Texto da anotação descrevendo o óbvio em vez de afirmar a conclusão.

**Por dial de fidelidade.** *Transcrição:* marque o ponto que o professor de fato destacou; não invente um outlier que ele não citou. *Esboço:* se você escolhe o ponto a realçar, deixe explícito no plano e confira que o dado-base é real e correto.
