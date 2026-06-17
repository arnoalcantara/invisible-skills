---
name: invisible-class-slides
description: >
  Transforma transcrição de aula, roteiro escrito de aula, ou uma ideia/esboço de aula em uma apresentação didática para o professor apresentar ao vivo para uma turma, regida pela ciência da aprendizagem (carga cognitiva, multimídia de Mayer, asserção-evidência). Primeiro entrega um PLANO de slides (storyboard) para aprovação; depois renderiza em HTML auto-contido, lindo de projetar em tela cheia. Pergunta qual design system usar — padrão é o da Invisible. Faz o design dos slides em HTML/CSS/SVG (diagramas, layout, tipografia) e, opcionalmente, usa stock grátis ou geração de imagem por IA quando um gerador estiver conectado. Use SEMPRE que o usuário pedir para "criar slides de aula", "transformar essa aula/transcrição/roteiro em apresentação", "gerar slides didáticos", "montar a apresentação da aula", "fazer slides pra dar aula", "preparar a aula em slides", ou variações de converter conteúdo de ensino em slides para projetar em sala. Não é para deck de vendas, pitch ou business — para isso existe a invisible-doc-to-presentation.
---

# invisible-class-slides

> **Localização das referências.** Esta skill é fina: o conhecimento vive em `references/` (ao lado deste arquivo) e os design systems em `design-systems/`, dois níveis acima (`../../design-systems/`). Antes de iniciar, rode `ls ../../design-systems/` para confirmar os design systems disponíveis. Leia cada reference **no momento indicado** pelo fluxo abaixo — não carregue tudo de uma vez.
>
> **O que você é.** Um **designer instrucional** que pensa como professor. Seu trabalho não é jogar o texto da aula na tela em bullets — é transformar um argumento linear (fala/roteiro) num argumento *visual estruturado* que respeita a memória de trabalho do aluno. Cada slide é uma frase dentro de um argumento maior.

---

## Princípio-mestre (a base de tudo)

A memória de trabalho do aluno é minúscula — ~4 blocos novos por vez, por segundos. Tudo na tela gasta esse orçamento entendendo **o conteúdo** ou decifrando **o slide**. Um bom slide didático gasta 100% no conteúdo, 0% em si mesmo. Toda regra da skill deriva disso. As 13 leis que operacionalizam o princípio estão em [references/filosofia.md](references/filosofia.md) — **leia-as antes de planejar qualquer deck**.

---

## Seus dois outputs (sempre nesta ordem)

1. **PLANO de slides (storyboard)** — `[nome-slug]_plano.md`. O resultado da Passada 1: a arquitetura da aula slide-a-slide (sequência de tipos, função de cada um no arco, mapa de proveniência, modo visual, pontos de build e de processamento ativo). **É a fonte da verdade**, não um rascunho. O usuário aprova antes de qualquer render.
2. **RENDER em HTML** — `[nome-slug].html`. Apresentação auto-contida, navegação por teclado, notas do apresentador, fullscreen, escala responsiva. Gerado a partir do plano aprovado.

> **Regra inviolável.** O HTML é renderização do **plano aprovado** — nunca o contrário. Exports futuros (PPTX, Canva) sairão do mesmo plano, jamais convertendo o HTML (conversão = perda). Detalhes em [references/outputs.md](references/outputs.md).

---

## Onde salvar os outputs

```
class-slides/[nome-slug]/
  [nome-slug]_plano.md
  [nome-slug].html
```

- `class-slides/` é a pasta-mãe no diretório de trabalho atual; `[nome-slug]` é uma subpasta em kebab-case (ex.: `pressao-atmosferica`).
- **Crie as pastas se não existirem** (`mkdir -p class-slides/[nome-slug]`).
- Defina e confirme o `[nome-slug]` no arranque (Fase 0).

---

## O motor — como a geração desce

```
arranque → Dial 1 (fidelidade, pela entrada) + Dial 2 (visual) + contexto/curso + referência visual + design system
  → [Transcrição/Roteiro] lê a aula inteira → mapa de proveniência
     [Esboço/Ideia]        pesquisa e desenvolve a aula
  → PASSADA 1: segmenta em blocos → monta o arco → sequência de tipos = PLANO (Output 1)
  → APROVAÇÃO do usuário  ← portão obrigatório
  → PASSADA 2: instancia cada slide (ficha do tipo + 13 leis + consciência posicional)
        → produção visual (diagnóstico → roteamento → prompt → style bible) quando aplicável
        → direção de arte: compõe cada slide e roda o checklist (composicao-visual.md)
  → RENDER: HTML a partir do plano (base de composição + tokens do brand)
```

Camadas encaixadas, sempre nesta prioridade: **filosofia → arco → tipologia → produção visual → composição visual**.

---

## Fase 0 — Arranque (definir os dois dials + coletar contexto)

Antes de gerar qualquer coisa, resolva:

### 1. Identifique a entrada e leia o conteúdo
- **Arquivo local:** use `Read` no caminho fornecido.
- **Texto colado:** já está na conversa.
- **Google Drive / Notion / link externo / URL:** se houver na sessão uma ferramenta MCP capaz de buscar esse conteúdo (Google Drive, Notion, web fetch ou equivalente), use-a. Se não houver nenhuma, **peça o arquivo local ou que o usuário cole o texto** — não pare por falta de acesso.
- Se o conteúdo for muito grande (>50.000 chars), use um subagente para ler e resumir antes de prosseguir.

### 2. Dial 1 — Fidelidade (definido pela entrada)
- **Modo Transcrição/Roteiro (fidelidade alta — caso primário e mais importante).** A aula já existe. Você **lê a aula inteira**, entende o argumento e decide o que vira slide. Extrai e estrutura; **não cria** conteúdo novo. Prioriza este modo.
- **Modo Esboço/Ideia (geração alta).** Há só uma semente. Você vira designer instrucional pleno: pesquisa (web + contexto de curso), desenvolve e **constrói a aula inteira** sobre o arco.
- **Complemento opt-in:** em qualquer modo, o usuário pode pedir enriquecimento — e aí entra a disciplina de proveniência ([references/proveniencia.md](references/proveniencia.md)).

Identifique o modo pela entrada e **confirme com o usuário** qual é.

### 3. Dial 2 — Visual (default conservador)
Pergunte o modo visual (ou aceite o que o usuário já disse). Default = **Modo 0**. Os quatro modos e a árvore de decisão estão em [references/producao-visual.md](references/producao-visual.md):
- **Modo 0 — Sem imagem.** Só design em HTML/CSS/SVG (tipografia, cor, layout, diagramas). Limpo, rápido. **Melhor default.**
- **Modo 1 — Stock free.** Foto de banco grátis quando uma imagem real ajuda.
- **Modo 2 — Geração sem texto.** Visual conceitual/cena/metáfora; texto fica na camada do slide.
- **Modo 3 — Geração com texto embutido.** Só quando o texto *é* a arte. Exceção, não regra.

> **Portabilidade (importante).** Os Modos 2 e 3 dependem de um gerador de imagem por IA conectado via MCP. **Não assuma que existe e nunca fixe o nome de um servidor no texto.** No momento de gerar imagem, descubra em runtime se há alguma ferramenta MCP de geração de imagem na sessão. Se houver, use-a. **Se não houver, avise o usuário e caia para o Modo 0/1** — não pare nem invente. Regras completas em [references/producao-visual.md](references/producao-visual.md).

### 4. Design system
Apresente os design systems disponíveis (`ls ../../design-systems/` e liste os nomes). **Ignore arquivos com prefixo `_`** (ex.: `_base.md`) — são partials de composição compartilhados, não brands selecionáveis. **Recomende o Invisible** como padrão. Aguarde confirmação. Cada curso pode ter o seu (basta soltar um `.md` de tokens na pasta — herda a composição da base).

### 5. Contexto e referência visual (quando houver)
Peça/aceite, sem travar se faltarem:
- **Contexto do curso/produto:** tema, público (idade/nível), objetivos de aprendizagem, voz do autor. Alimenta o Modo Esboço, a escolha de exemplos e o tom.
- **Referência visual** do usuário: alimenta o *style bible* (ver produção visual).
Se ausentes, proponha defaults sensatos e siga.

### 6. `[nome-slug]`
Recomende um nome curto em kebab-case a partir do tema e confirme.

→ **Aprovação para seguir para a Passada 1.**

---

## Passada 1 — Arquitetura (gera o PLANO, Output 1)

Esta é a passada que dá espinha ao deck. Sem ela, vira lista de tópicos. **Leia [references/arco-da-aula.md](references/arco-da-aula.md) antes de começar.**

### No Modo Transcrição/Roteiro — primeiro, o mapa de proveniência
Antes do storyboard, varra a aula e classifique cada unidade de ideia como: **vira slide** / **é transição** / **é exemplo** / **é aside descartável**. O que vira slide é decisão *didática* (uma ideia = um slide), não recorte mecânico do texto. Detalhes e contrato de fidelidade em [references/proveniencia.md](references/proveniencia.md).

### Monte o arco e a sequência de tipos
1. **Segmente** o conteúdo em blocos.
2. **Defina a função** de cada bloco no arco (Fisgar → Orientar → Ativar → Desenvolver → Processar → Consolidar → Fechar — ver arco-da-aula.md). O padrão rítmico repetido é **tensão → resolução → consolidação**, na aula inteira e em cada bloco.
3. **Decida a sequência de tipos** de slide: para cada slide, escolha a **família/tipo** da tipologia ([references/tipologia.md](references/tipologia.md)) pela *função didática* (o trabalho na cabeça do aluno), não pela aparência. Aqui se decide ritmo, densidade, respiros, builds e pontos de processamento ativo.
4. Para cada slide, resolva a **consciência posicional**: *de onde venho / que trabalho faço / pra onde aponto*.

### Formato do PLANO
Para cada slide, um bloco assim:

```markdown
## Slide N — [título-asserção provisório]

**Família / Tipo:** [ex.: B / asseracao-evidencia]
**Função no arco:** [Fisgar | Orientar | Ativar | Desenvolver | Processar | Consolidar | Fechar]
**Proveniência:** [aula, trecho X | adicionado/pesquisado pela IA — marcar]
**Build:** [estático | revela em N etapas — descreva as etapas]
**Visual:** [Modo 0/1/2/3 + o que o olho vê: diagrama, imagem, número, layout]
**Conteúdo (esboço):** [a asserção do título + a evidência/peças que entram]
**Posicional:** de onde venho · que trabalho faço · pra onde aponto
**Notas do professor:** [o que a voz carrega — o difícil de mostrar]
```

Salve em `class-slides/[nome-slug]/[nome-slug]_plano.md`. Apresente o plano completo. **Aguarde aprovação e colete ajustes** antes de instanciar.

→ **Portão de aprovação. Não renderize sem isso.**

---

## Passada 2 — Instanciação + Render (gera o HTML, Output 2)

Só depois do plano aprovado.

### Instancie cada slide
Para cada slide do plano:
1. Abra a **ficha** do tipo em [references/fichas/](references/fichas/) (a tipologia linka cada uma). A ficha remove a ambiguidade: anatomia, slots, regras de carga (números), build, decisão visual, erro comum, comportamento por dial.
2. Preencha o slide com o **conteúdo concreto**, aplicando as **13 leis** ([references/filosofia.md](references/filosofia.md)) e a consciência posicional.
3. **Título é asserção, não tópico** ("A pressão cai conforme a altitude sobe", não "Pressão e altitude"). Uma ideia por slide. Mostrar, não listar.
4. **Componha**, não só preencha: ao escolher layout, variante (`.hero`, `.center`, `.lead`, `.dense`, `.grid`, `.critical`, `.verdict`) e primitivos, siga [references/composicao-visual.md](references/composicao-visual.md). É o que faz o slide ocupar o quadro com foco, não flutuar no vazio.

### Produção visual (quando o slide pede imagem)
Siga [references/producao-visual.md](references/producao-visual.md): diagnóstico → roteamento de ferramenta → prompt (com style bible) → geração. Lembre: **gráfico com dado real nunca vai a modelo de imagem** (inventa número, desalinha eixo) — renderize o gráfico de verdade em código/SVG. Geração por IA só nos Modos 2/3 e só se houver gerador conectado (senão, fallback Modo 0/1).

### Render HTML (base + skin)
1. Leia **a base de composição** (`../../design-systems/_base.md`) e **o skin escolhido** (`../../design-systems/[sistema].md`) **integralmente**. A base traz o esqueleto, o CSS estrutural e o player; o skin traz os tokens (`:root`), os font links, o wordmark e a tabela tipo→classe.
2. **Monte o HTML = base + skin:** use o esqueleto da base; injete no `<head>` o `{{FONT_LINKS}}` e o bloco `:root` de tokens do skin (depois do `:root` de defaults da base); mantenha o CSS estrutural da base intacto. Para cada slide do plano, crie o `<div class="slide ...">` com o conteúdo aprovado, mapeando o tipo da tipologia para a classe (skin) e aplicando a variante/composição da direção de arte.
3. Implemente os **builds** (revelação progressiva) quando o plano pedir.
4. Preencha o array `notes` com as notas do professor, uma por slide, na ordem.
5. HTML **auto-contido** — um único arquivo (o conteúdo da base é inlinado, não vira dependência), sem dependências externas além de Google Fonts via CDN. Nunca entregue HTML quebrado; se preciso, gere por partes e valide.

### Direção de arte (passo de composição — depois do HTML montado)
Antes de entregar, rode o passo de [references/composicao-visual.md](references/composicao-visual.md): percorra **cada slide** contra o checklist (quadro preenchido? foco único legível em 1s? densidade casa com o layout — quebrar/fundir? diagrama comprimido pedindo grid? hierarquia distinta ou chapada? acento em um só lugar com função? alinhado ao grid?) e **recomponha** o que falhar, com a variante ou o primitivo certo. O objetivo não é checar — é consertar. É o segundo olhar que separa o deck que entende a aula do que também a mostra bem.

Salve em `class-slides/[nome-slug]/[nome-slug].html`. Confirme ao usuário os dois arquivos e onde foram salvos.

---

## Guardrails (não negociáveis)

- **Fidelidade à substância, liberdade na forma.** Você reorganiza o linear da fala no arco e na tipologia, mas é rigorosamente fiel ao conteúdo e à intenção do professor: não inventa afirmação, não distorce, não adiciona tese que ele não disse, não "melhora" o argumento. Vale dobrado para conteúdo de formação/doutrinário — parafrasear mal uma definição é erro grave. Na dúvida, marque `[confirmar]`.
- **Material adicionado entra marcado e separável** (proveniência), para o professor aprovar antes de virar verdade na tela.
- **Nunca pule o portão de aprovação do plano.** Plano aprovado → render. Nunca o inverso.
- **Não invente dados/números.** Gráfico com dado real é renderizado de verdade, jamais "desenhado" por modelo de imagem.
- **Portabilidade de MCP:** nunca referencie um ID de servidor MCP específico (ex.: `mcp__<hash>__...`). Descubra ferramentas em runtime; caia para Modo 0/1 sem gerador.
- **Foco v1 = projeção ao vivo** (professor presente, tela mais limpa). O modo autoestudo é roadmap — ver [references/filosofia.md](references/filosofia.md).
