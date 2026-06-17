# Prompt gerador — Skill `invisible-class-slides`

**Para:** Claude Code
**Objetivo:** construir, do zero, uma skill que transforma transcrições/roteiros de aula (ou ideias/esboços) em apresentações didáticas para o **professor apresentar ao vivo para uma turma**. Não é apresentação de vendas, prospecção ou business — é didática pura, regida pela ciência da aprendizagem.

Este documento é a especificação completa. Antes de escrever qualquer arquivo, leia a skill `skill-creator` (`/mnt/skills/examples/skill-creator/SKILL.md`) e siga a anatomia dela: progressive disclosure (SKILL.md enxuto + `references/`), `description` "pushy" no frontmatter, forma imperativa, explicar o *porquê* em vez de empilhar MUSTs. Ao final, proponha 2-3 casos de teste reais e rode.

---

## 0. O que construir

Uma skill chamada `invisible-class-slides` com **disclosure progressivo**:

```
invisible-class-slides/
├── SKILL.md                      # orquestrador: dials, processo de 2 passadas, 2 outputs, quando ler o quê
└── references/
    ├── filosofia.md              # princípio-mestre + as 13 leis
    ├── arco-da-aula.md           # arco, consciência posicional, 2 passadas
    ├── tipologia.md              # índice das 8 famílias + ~50 tipos (TOC no topo)
    ├── fichas/                   # uma ficha executável por tipo (gabarito na seção 7)
    │   └── *.md
    ├── producao-visual.md        # árvore de roteamento, modos 0–3, MCP, ficha de prompt de imagem, style bible
    ├── proveniencia.md           # contrato de fidelidade e disciplina de origem
    └── outputs.md                # plano → aprovação → render (HTML default, PPTX/Canva export)
```

O SKILL.md deve ficar < 500 linhas e **apontar** para as referências no momento certo do fluxo, não inlinar tudo.

### Identidade (frontmatter)

- **name:** `invisible-class-slides`
- **description (pushy):** algo como — "Transforma transcrição de aula, roteiro escrito de aula, ou uma ideia/esboço de aula em uma apresentação didática para o professor apresentar ao vivo para uma turma, regida pela ciência da aprendizagem (carga cognitiva, multimídia de Mayer, asserção-evidência). Primeiro entrega um PLANO de slides para aprovação; depois renderiza em HTML (padrão), com export opcional para PowerPoint/Canva. Gera imagens e infográficos via Higgsfield MCP (Nano Banana 2 / GPT Image 2) ou usa stock free, ou nenhuma imagem — opção do usuário. Use SEMPRE que o usuário pedir para 'criar slides de aula', 'transformar essa aula/transcrição/roteiro em apresentação', 'gerar slides didáticos', 'montar a apresentação da aula', 'fazer slides pra dar aula', ou variações de converter conteúdo de ensino em slides para projetar em sala."

---

## 1. Princípio-mestre (a base de tudo)

A memória de trabalho do aluno é minúscula (~4 blocos novos, por segundos). Tudo na tela gasta esse orçamento entendendo **o conteúdo** ou decifrando **o slide**. Um bom slide didático gasta 100% no conteúdo, 0% em si mesmo. Toda regra abaixo deriva disso.

Três corpos de pesquisa fundamentam a skill (detalhar em `filosofia.md`):
- **Teoria da Carga Cognitiva (Sweller):** carga intrínseca (sequenciar), extrínseca (eliminar — inimigo) e germânica (liberar orçamento para ela).
- **Teoria Cognitiva da Aprendizagem Multimídia (Mayer):** dois canais (visual/verbal) limitados → coerência, sinalização, redundância, contiguidade espacial, segmentação, pré-treino.
- **Asserção-Evidência (Alley, Penn State):** título em **frase completa** que afirma a ideia + **evidência visual** embaixo (não bullets). É a coluna vertebral estrutural da skill.

---

## 2. As 13 leis (a "constituição" — `filosofia.md`)

Toda geração obedece, sempre:

1. **Uma ideia por slide.** Duas ideias = dois slides.
2. **Título é asserção, não tópico.** A linha de cima diz a conclusão ("A pressão cai conforme a altitude sobe"), não o assunto ("Pressão e altitude").
3. **Carga extrínseca mínima.** Cada elemento se justifica ou é cortado.
4. **Hierarquia visual explícita.** Um único ponto focal; tamanho/cor/posição dizem o que ler primeiro.
5. **Mostrar, não listar.** Diagrama/imagem que *é* a evidência vence o bullet que a descreve. Bullet é último recurso.
6. **Slide não duplica a fala.** A voz carrega o difícil de mostrar; o slide carrega o difícil de dizer. (Princípio da redundância: nunca encher a tela com o texto que o professor vai ler em voz alta.)
7. **Rótulo junto da coisa.** Anotar o diagrama no lugar, não em legenda distante.
8. **Revelação progressiva.** Builds em etapas, no ritmo da explicação.
9. **Pré-treinar vocabulário.** As peças antes do todo.
10. **Espaço em branco é estrutura.**
11. **Piso de legibilidade.** Tipografia grande, alto contraste, sistema de cor/fonte enxuto e consistente.
12. **Pontos de processamento ativo.** Momentos de "preveja / compare / lembre" — aprender exige fazer.
13. **Espinha narrativa.** O deck tem um fio; cada slide avança nele e o aluno sempre sabe onde está.

### Foco e modo secundário
O alvo é **projeção ao vivo** (professor presente, a voz carrega parte da carga → tela mais limpa). A skill **também** deve poder gerar uma versão de **autoestudo** (slide explica sozinho → mais texto na tela, sem narrador), como saída secundária e opt-in. Atenção: vários princípios de Mayer se invertem entre os dois modos; o autoestudo separa camada de projeção (limpa) de camada de referência (notas). Default = projeção ao vivo.

---

## 3. Os dois dials (regulados no arranque, antes de gerar)

A skill começa todo trabalho definindo dois ajustes.

### Dial 1 — Fidelidade (definido pela entrada)
- **Modo Transcrição/Roteiro (fidelidade alta — caso primário, ex.: Bernardo).** A aula já existe. A skill **lê a aula inteira**, entende o argumento e decide o que vira slide. Extrai e estrutura; **não cria**.
- **Modo Esboço/Ideia (geração alta).** Existe só uma semente (começo-meio-fim, ou menos). A skill vira designer instrucional: pesquisa (web + contexto de curso/produto), desenvolve e **constrói a aula inteira** sobre o arco.
- **Complemento opt-in:** em qualquer modo, o usuário pode pedir enriquecimento — e aí entra a disciplina de proveniência (seção 8).

A **função primária e mais importante** é o Modo Transcrição. Priorize-a.

### Dial 2 — Visual (escolhido no início; default conservador)
Imagem é **opcional** e nunca o default exagerado (lei 3 e da coerência). Quatro modos:
- **Modo 0 — Sem imagem.** Só design que o Claude faz sozinho: tipografia, cor, layout, diagramas em HTML/CSS/SVG. Limpo, rápido. **Provável melhor default.**
- **Modo 1 — Stock free.** Foto de banco gratuito quando uma imagem real ajuda, sem gastar geração.
- **Modo 2 — Geração sem texto (Higgsfield → Nano Banana 2).** Visual conceitual/cena/metáfora; o texto fica na camada do slide.
- **Modo 3 — Geração com texto embutido (Higgsfield → GPT Image 2).** Só quando o texto *é* a arte (slide-pôster, rótulo cozido em diagrama estilizado). Exceção, não regra — texto editável na camada do slide quase sempre vence texto cozido.

A skill deve **perguntar o modo visual no início** (ou aceitar que o usuário já tenha dito) e, no Modo Transcrição, pode *sugerir* onde uma imagem agregaria em vez de espalhar imagem por todo slide.

---

## 4. O arco da aula (`arco-da-aula.md`)

O slide é uma frase dentro de um argumento. Antes da tipologia, a skill monta a **arquitetura da aula**. Esqueleto canônico (default adaptável):

1. **Fisgar** — abrir uma lacuna/tensão/pergunta; o aluno precisa *querer* a resposta.
2. **Orientar** — objetivos + mapa.
3. **Ativar** — puxar o que ele já sabe.
4. **Desenvolver** — corpo em *blocos*, cada bloco com mini-arco (apresenta → mostra → checa).
5. **Processar** — atividade ativa espalhada, não só no fim.
6. **Consolidar** — síntese, takeaway, antecipar erro comum.
7. **Fechar** — amarrar e abrir ponte pro próximo.

Padrão rítmico repetido em escalas: **tensão → resolução → consolidação** (aula inteira e cada bloco). Gagné, 5E e Rosenshine são variações disso — não dogmatize, capture o padrão.

### Consciência posicional
Cada slide responde três perguntas, e é assim que se decidem transições, "você está aqui", predições etc.:
- *De onde venho?* (o que o anterior estabeleceu)
- *Que trabalho faço?* (função na tipologia)
- *Pra onde aponto?* (o que preparo no próximo)

### Processo de duas passadas (núcleo do motor)
- **Passada 1 — arquitetura:** ler o conteúdo todo, segmentar em blocos, definir a função de cada bloco no arco e decidir a **sequência de tipos** (o storyboard/plano). Aqui se decide ritmo, densidade, respiros e checagens. **Este é o Output 1.**
- **Passada 2 — instanciação:** preencher cada slide do plano aprovado com o tipo escolhido, aplicando as 13 leis e o conteúdo concreto. **Este é o Output 2.**

Sem a Passada 1 o deck vira lista; com ela, ganha espinha.

---

## 5. A tipologia — 8 famílias (`tipologia.md`)

Organizada por **função didática** (o trabalho na cabeça do aluno), não por aparência. A skill classifica o trecho pela intenção → escolhe a família → instancia o tipo → aplica as leis.

**A — Orientação e estrutura:** abertura/título · objetivos · roteiro/agenda · divisor de seção · "você está aqui" · ponte/transição · ativação de conhecimento prévio.

**B — Apresentar uma ideia:** asserção+evidência (tipo-padrão) · declaração-soco · definição · citação/autoridade.

**C — Estrutura e relações:** comparação lado a lado · trade-off/prós e contras · matriz 2×2/quadrante · taxonomia/hierarquia/árvore · anatomia/diagrama rotulado · sobreposição/Venn · espectro/continuum.

**D — Processo, sequência e mudança:** passo a passo/fluxo · linha do tempo · causa-efeito/cadeia · ciclo/loop · progressão/caminho/jornada · antes-e-depois/transformação · árvore de decisão/fluxograma.

**E — Dados e quantidade:** gráfico (com UMA mensagem destacada) · número grande único · destaque sobre dado · infográfico (composto, com parcimônia).

**F — Concretizar o abstrato:** imagem em tela cheia · imagem+texto · exemplo/caso · analogia/metáfora · exemplo resolvido (worked example) · exemplo anotado/marcação.

**G — Processamento ativo:** pergunta/provocação · predição · enquete/mão pra cima · atividade (pense-converse-compartilhe) · preencher lacuna/revelar resposta · problema pra resolver · verificação de entendimento/quiz.

**H — Reforço e fechamento:** takeaway/ideia-chave · síntese · erro comum/equívoco · mnemônico · recursos/referências.

**Notas de implementação:**
- **Primitivos vs. compostos:** prefira primitivos (um trabalho). Infográfico, dashboard, jornada anotada são compostos — só componha quando a carga justificar.
- **Revelação progressiva é ortogonal:** não é um tipo, é um *atributo* do slide aplicável a quase todos.
- A `tipologia.md` deve ter TOC no topo e linkar cada ficha em `references/fichas/`.

---

## 6. As fichas executáveis (`references/fichas/`)

Cada um dos ~50 tipos vira uma **ficha** que remove a ambiguidade da geração — de modo que *qualquer IA* gere com consistência. Use o gabarito abaixo (campos fixos) para **todas**.

### Gabarito de ficha (campos obrigatórios)
- **Família / ID**
- **Função didática** — que trabalho faz; em que ponto do arco costuma aparecer.
- **Quando usar / quando NÃO usar** — gatilho e anti-gatilho.
- **Anatomia (slots)** — obrigatórios e opcionais.
- **Regras de carga** — limites concretos (números).
- **Build** — admite revelação progressiva? Em que ordem?
- **Decisão visual (roteamento)** — modo 0/1/2/3 default; quando manda pro Higgsfield e quando não.
- **Conexão posicional** — o que pede antes / pra onde aponta.
- **Erro comum** — a falha clássica a evitar.
- **Comportamento por dial de fidelidade** — como muda em Transcrição vs. Esboço.

### Ficha-gabarito de referência (já validada — use como modelo de nível de detalhe)

> **FICHA — Comparação lado a lado**
> **Família:** C — Estrutura e relações · **ID:** `comparacao-lado-a-lado`
>
> **Função didática.** Colocar 2 (máx. 3) itens em paralelo nas *mesmas* dimensões, para o aluno ler diferenças/semelhanças por varredura horizontal. O trabalho é *contrastar*: a diferença salta sozinha, sem o aluno segurar A na memória enquanto procura B.
>
> **Posição no arco.** Meio (Desenvolver). Quase sempre *depois* de os itens terem sido apresentados isoladamente. Costuma ser a resolução de uma pergunta ou a preparação de uma síntese.
>
> **Quando usar.** 2-3 conceitos/métodos/períodos/posições que o aluno precisa distinguir; quando confundi-los é risco real; quando a decisão entre eles importa.
>
> **Quando NÃO usar.** >3 itens → vira tabela de referência (handout, não slide). Itens sem dimensões comparáveis → outro tipo. Evolução de um item no tempo → Antes/Depois ou Linha do Tempo.
>
> **Anatomia.** *Título-asserção* (obrig., afirma o veredito/tensão, não rotula). *Colunas* (obrig., 2, máx. 3, rótulo curto). *Dimensões* (obrig., as linhas, **alinhadas horizontalmente**, máx. 3). *Marcação de veredito* (opc.). *Eixo-rótulo das dimensões* à esquerda (opc. recomendado).
>
> **Regras de carga.** Máx. 3 dimensões; máx. 3 colunas (ideal 2); cada célula = uma frase/dado, não parágrafo; mesmas dimensões, mesma ordem nos dois lados.
>
> **Build.** Recomendado com 3 dimensões: revela linha por linha, no ritmo da fala. A e B da mesma dimensão aparecem *juntas*; nunca uma coluna inteira antes da outra.
>
> **Decisão visual.** **Modo 0 por padrão** — é estrutura, resolve em HTML/CSS. *Não* manda pro Higgsfield. Imagem só se cada item *for* visual (duas obras, dois gráficos), e aí cada lado recebe seu visual pelo caminho próprio — nunca um "infográfico de comparação" gerado inteiro.
>
> **Conexão.** *Pede antes:* itens já apresentados isoladamente; idealmente uma pergunta que a comparação resolve. *Aponta pra:* síntese, veredito/takeaway, ou árvore de decisão.
>
> **Erro comum.** Dimensões desalinhadas (A fala "custo, velocidade, precisão"; B fala "preço, facilidade, qualidade") → mata a leitura paralela. Também: dimensões demais (vira tabela); título-tópico em vez de asserção.
>
> **Por dial.** *Transcrição:* só cria se o professor de fato contrastou; dimensões saem do que *ele* usou (não inventar). Se ele comparou em 5 dimensões, seleciona as 3 mais relevantes e sinaliza o corte (proveniência). *Esboço:* pode propor dimensões, marcadas como geradas para aprovação.

Gere as outras ~49 fichas nesse mesmo padrão e profundidade.

---

## 7. Produção visual (`producao-visual.md`)

A skill não "gera imagem"; faz **raciocínio visual em duas etapas**, invisível ao usuário (vaivém por MCP por baixo).

### Etapa A — Diagnóstico + roteamento de ferramenta (a árvore que evita erro)
A partir da função do slide, decida o visual e **qual ferramenta resolve**:
- **Gráfico com dado real** (números que precisam estar corretos) → **NUNCA** modelo de imagem (inventa número, desalinha eixo). Renderize gráfico de verdade (código/biblioteca de chart) ou Canva. Higgsfield só estiliza fundo/moldura, nunca plota o dado.
- **Visual conceitual / metáfora / cena / ideia-em-imagem** (sem número crítico) → **Higgsfield (Nano Banana 2)** brilha.
- **Infográfico** → híbrido. Com dado = composição (chart real + arte). Conceitual (processo/anatomia estilizada sem números críticos) = pode Higgsfield, com cuidado redobrado em texto.

### Etapa B — Geração do prompt (ficha de prompt de imagem)
Todo prompt enviado ao Higgsfield tem slots fixos:
- **Sujeito + intenção didática** — o que a imagem precisa *ensinar*.
- **Composição com espaço negativo planejado** — onde o título/rótulo entra na camada do slide (ex.: "sujeito à direita, terço esquerdo limpo para sobreposição de título").
- **Tratamento de texto** — regra geral: pedir imagem **sem texto embutido** (texto fica na camada do slide, editável/legível). Exceção = Modo 3.
- **Âncora de estilo** — injeta o *style bible* do deck (abaixo).
- **Aspect ratio + resolução** — 16:9, 4K, definido uma vez.
- **Negativos** — clichê de banco de imagem, número inventado, poluição.

### Style bible (coerência do deck)
1. **Entrada de estilo:** o usuário manda uma referência visual, OU a skill puxa do contexto de produto/curso (paleta, tipografia, tom). Se não houver nada, a skill propõe.
2. **Destilação:** transforma em um *style bible* curto (paleta, tratamento de imagem — flat/editorial/3D/linha —, mood, do's e don'ts).
3. **Herança:** **todo** prompt de imagem injeta o bible. É o que faz 30 imagens parecerem do mesmo deck. Mesma lógica das 13 leis: define no topo, cascateia.

Para elementos recorrentes (mascote, personagem-guia, o produto), use a consistência de personagem/produto do Higgsfield ao longo do deck.

### Integrações MCP (confirmadas)
- **Higgsfield:** servidor MCP hospedado em `https://mcp.higgsfield.ai/mcp` (HTTP, auth pela conta Higgsfield, sem API key separada; funciona em Claude Code). Modelos relevantes: **Nano Banana 2** (= Gemini 3.1 Flash Image: qualidade Pro em velocidade Flash, consistência de até 5 sujeitos, até 4K) para imagem sem texto; **GPT Image 2** para imagem com texto embutido. Detalhes de slugs/parâmetros não são documentados e mudam — a skill deve descobrir as ferramentas expostas pelo MCP em runtime e não hardcodar nomes frágeis.
- **Canva:** via MCP do Canva, para diagramação/montagem editável e como caminho de export (seção 8).

---

## 8. Proveniência e contrato de fidelidade (`proveniencia.md`)

**Fidelidade à substância, liberdade na forma.** A fala do professor é linear; o deck é argumento estruturado. A skill reorganiza o linear no arco e na tipologia (não joga parágrafo como bullet), mas é **rigorosamente fiel** ao conteúdo e à intenção: não inventa afirmação, não distorce, não adiciona tese que o professor não disse, não "melhora" o argumento dele. Isso vale dobrado para conteúdo de formação/doutrinário — parafrasear mal uma definição é erro grave, não estético.

**Disciplina de origem.** Cada slide carrega, por baixo, a procedência: *veio da aula (trecho X)* vs. *adicionado/pesquisado pela IA*. Com complemento ligado, o material novo entra **marcado e separável**, para o professor aprovar antes de virar verdade na tela.

**Sub-etapa no Modo Transcrição:** antes do storyboard, montar um **mapa de proveniência** — varrer a aula, identificar as unidades de ideia, marcar cada uma como (vira slide / é transição / é exemplo / é aside descartável) — e só então montar o arco. O que vira slide é decisão didática (uma ideia = um slide), não recorte mecânico do texto.

**Modo Esboço:** a skill assume autoria; **devolve o storyboard para aprovação antes** de instanciar todos os slides. O ponto de controle humano vem antes da produção, não depois.

---

## 9. Os dois outputs (`outputs.md`)

### Output 1 — Plano de slides (para aprovação)
O resultado da Passada 1: o storyboard slide-a-slide (sequência de tipos, função de cada um no arco, mapa de proveniência, modo visual, pontos de build e de processamento ativo). **É a fonte da verdade** — não um rascunho descartável. O usuário aprova antes de qualquer render.

### Output 2 — Render (a partir do plano aprovado)
- **HTML — entregável primário/padrão.** É onde as 13 leis vivem com fidelidade total (tipografia, espaço, hierarquia ao pixel); o Modo 0 é HTML/CSS/SVG puro; builds funcionam nativamente; navegador em tela cheia apresenta lindo ao vivo. Use a skill `frontend-design` como referência de qualidade visual.
- **PPTX — export opcional.** Para quem precisa editar no PowerPoint / projetar de qualquer lugar (caso Bernardo). Seja honesto: é downgrade de fidelidade (via python-pptx; teto de design menor, builds mais toscos). Oferecer, não default.
- **Canva — export opcional (via MCP).** Meio-termo editável e apresentável sem código; geração mais templada/menos precisa que as fichas.

**Regra inviolável:** os três renderizam a partir do **mesmo plano aprovado**. **Nunca** gerar HTML e converter para PPTX (conversão = perda). Plano é fonte; HTML/PPTX/Canva são renderizações dele.

---

## 10. Contexto de produto/curso e referência visual

A skill deve **pedir/aceitar** no arranque, quando disponíveis:
- **Contexto do produto/curso** (tema, público, objetivos, voz do autor) — alimenta Modo Esboço, escolha de exemplos e tom.
- **Referência visual** do usuário — alimenta o style bible.
Se ausentes, a skill propõe defaults sensatos e segue.

---

## 11. Como a geração desce (resumo do motor)

```
arranque → define Dial 1 (entrada) e Dial 2 (visual) + coleta contexto/referência
  → [Transcrição] lê aula inteira → mapa de proveniência
     [Esboço]     pesquisa e desenvolve
  → PASSADA 1: segmenta em blocos → arco → sequência de tipos = PLANO (Output 1)
  → APROVAÇÃO do usuário
  → PASSADA 2: instancia cada slide (ficha do tipo + 13 leis + consciência posicional)
        → produção visual (diagnóstico → roteamento → prompt → style bible) quando aplicável
  → RENDER: HTML (default) [+ PPTX / Canva opcionais] a partir do plano
```

Camadas encaixadas, sempre nesta ordem de prioridade: **filosofia → arco → tipologia → produção visual**.

---

## 12. Instruções finais para o build

1. Siga a anatomia de `skill-creator` (progressive disclosure; SKILL.md < 500 linhas apontando para `references/`; `description` pushy; forma imperativa; explicar o porquê).
2. Escreva primeiro o SKILL.md (orquestrador) e a `tipologia.md` com TOC; depois as fichas; depois as demais referências.
3. As ~50 fichas seguem o gabarito da seção 6, no nível de detalhe da ficha de Comparação.
4. Não hardcode slugs/parâmetros do Higgsfield — descubra as ferramentas do MCP em runtime.
5. Ao terminar o draft, proponha 2-3 casos de teste reais (ex.: "transcrição de aula do Bernardo sobre [tema] → plano + HTML, modo 0"; "esboço de 3 linhas → aula inteira para aprovação"; "roteiro + referência visual → HTML modo 2 com 3 imagens conceituais"), e rode para validar.
6. Empacote a skill ao final e entregue o caminho do `.skill` para instalação.
