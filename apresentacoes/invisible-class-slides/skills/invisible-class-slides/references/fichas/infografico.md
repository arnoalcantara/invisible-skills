# FICHA — Infográfico

**Família:** E — Dados e quantidade · **ID:** `infografico`

**Função didática.** Compor **dados + arte** num único slide que conta uma micro-história visual — número, ícone, processo e legenda trabalhando juntos. O trabalho na cabeça do aluno: absorver um conjunto relacionado de informação de uma vez. É um tipo **composto** (vários trabalhos num slide), então custa mais carga: use com parcimônia, só quando a integração justifica.

**Posição no arco.** Consolidar (reúne fios de um bloco numa peça-resumo) ou Desenvolver, num ponto em que a relação entre vários elementos *é* a ideia. Pesado demais para fisgar.

**Quando usar.** Vários elementos só fazem sentido juntos e quebrá-los em slides separados perderia a relação. Quando a peça é a síntese visual de um bloco. Pense duas vezes: a maioria das ideias resolve melhor em primitivos (asserção-evidência, gráfico, passo-a-passo).

**Quando NÃO usar.** Um dado só → [grafico](grafico.md) ou [numero-grande](numero-grande.md). Uma sequência → [passo-a-passo](passo-a-passo.md). Sempre que um primitivo único der conta — ele gasta menos carga (lei 3). Não use só porque "fica bonito".

**Anatomia (slots).**
- *Título-asserção* (obrigatório) — a tese que a composição inteira sustenta (lei 2).
- *Núcleo de dado* (quando há números) — chart real renderizado, não desenho de número.
- *Arte/ícones de apoio* (obrigatório) — os elementos visuais que organizam e dão corpo.
- *Rótulos junto de cada parte* (obrigatório) — texto colado a cada elemento (lei 7).
- *Fluxo de leitura explícito* (recomendado) — a composição diz por onde começar e seguir (lei 4).

**Regras de carga.** Composto = teto de carga baixo. Máximo ~3–4 blocos de informação na peça. Um caminho de leitura claro, nunca um amontoado. Se passa de ~4 blocos, quebre em slides. A arte serve à informação, nunca decora vazio.

**Build.** Revele bloco a bloco no ritmo da narração — quase obrigatório aqui, senão o aluno enfrenta tudo de uma vez e estoura a memória de trabalho (lei 8).

**Decisão visual (roteamento).** **Híbrido.** **Com dado:** o núcleo é **chart real em Modo 0** (HTML/CSS/SVG); a arte ao redor é Modo 0 ou, se houver gerador conectado, Modo 2 só para fundo/elementos sem número. **Gráfico com dado real NUNCA vai a gerador de imagem** — inventa número e desalinha eixo. **Conceitual** (processo ou anatomia estilizada, sem números críticos): pode ir ao gerador de imagem com cuidado redobrado em texto (rótulos na camada do slide, não cozidos). Imagem só nos Modos 2/3 e só se houver gerador na sessão; senão, fallback Modo 0/1. Ver [../producao-visual.md](../producao-visual.md).

**Conexão posicional.** *Pede antes:* os elementos individuais já apresentados (o infográfico costuma *reunir* o que veio). *Aponta para:* o takeaway que destila a peça, ou a aplicação.

**Erro comum.** Amontoado sem hierarquia nem caminho de leitura (viola lei 4). Usar onde um primitivo bastava (carga desperdiçada). Mandar a parte de dado para gerador de imagem (número inventado). Texto cozido na arte gerada — ilegível e não editável. Excesso de blocos.

**Por dial de fidelidade.** *Transcrição:* todo número e relação saem do que o professor afirmou; a composição organiza, não acrescenta. *Esboço:* você estrutura a peça e marca dados/fontes com `[confirmar]`; sinalize no plano que é composição autoral para aprovação.
