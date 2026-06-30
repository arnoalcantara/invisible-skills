# invisible-carrossel-visual — plugin

## O que é

O **sistema visual de carrossel** da Invisible. É o lado VISUAL da produção de carrossel: recebe o roteiro pronto (texto card a card) e o **veste** numa linguagem visual decodificada de referências, gerando os cards finais como PNGs.

Complementa o lado COPY (`invisible-carrossel`, no plugin `invisible-copy`): aquele escreve o texto fiel à fonte; este o renderiza. Fronteira limpa — quem escreve não renderiza; quem renderiza não inventa texto.

## Skills

| Skill | Função |
|---|---|
| `invisible-estilo-decoder` | Decodificador de estilo: aponta uma pasta de referências → lê por visão (decompõe grids) → congela o briefing num `[Pasta]_ESTILO.md` salvo na pasta. Não gera imagem; só o contrato de estilo. |
| `invisible-carrossel-visual` | Produtor visual: roteiro pronto + pasta de referências → cards PNG. Lê o `*_ESTILO.md` (ou roda o decoder se não houver), veste o texto por papel de slide, e renderiza pelo **motor que o `_ESTILO.md` declara**: `html` (HTML/CSS → PNG, estilos tipográficos/UI) ou `higgsfield` (GPT Image 2, estilos com imagem gerada). |

> Fluxo: **decoder** congela o estilo de uma pasta uma vez → **produtor** usa esse `[Pasta]_ESTILO.md` em todos os carrosséis daquele estilo.

## Princípios de arquitetura

- **Identidade visual = referências.** Não há cadastro de estética por marca. O visual sai 100% das imagens da pasta, decodificadas por visão e congeladas num `_ESTILO.md` por pasta (briefing reutilizável).
- **Dois motores, escolha pelo `_ESTILO.md`.** O campo `motor:` decide: `html` (HTML/CSS → PNG via Chrome headless) para estilos tipográficos/UI-mockup — pixel-perfeito, texto nunca erra, custo zero, reproduzível; `higgsfield` (GPT Image 2) para estilos com imagem gerada. Regra dura: tipografia-sobre-fundo nunca vai pro Higgsfield.
- **Papel do slide.** Capa, interno e fecho têm repertórios próprios no `_ESTILO.md`. Interno nunca é tratado como capa.
- **Motor HTML: moldura fixa por estilo, texto do roteiro.** O `render_html.py` embute o template do estilo (a moldura) e veste o texto que vem do roteiro JSON. Adicionar um estilo HTML = uma função de montagem no dict `ESTILOS`.
- **Motor Higgsfield: coleta robusta.** O `--wait` dá 502 na coleta e cobra mesmo falhando. Dispara o job e recupera por id; nunca re-dispara um job que pode estar rodando.
- **Motores centrais, não por lote.** Chrome (HTML) e Higgsfield CLI (npm) vivem na máquina. `bootstrap.py` reporta o estado de cada um; só é preciso o motor que o estilo pede.

## Estilos recorrentes

Cada estilo de carrossel vive como uma **pasta de referências** com um `_ESTILO.md` congelado (que declara o `motor:`). O usuário aponta a pasta; a skill lê o briefing pronto. Trocar de estilo = trocar de pasta. Estilos com template HTML pronto: **`notes`** (app Notas do iOS), **`tweet_card`** (print de tweet do X, sub-modos `solido` e `imagem`) e **`tweet_editorial`** (sequência editorial em tweet estilo Pedro Sobral, componível por blocos, com sourcing de imagem em duas passadas).

## Roadmap

- **v0.1.0:** produtor visual com motor Higgsfield (texto-na-imagem).
- **v0.3.0:** motor HTML (HTML/CSS → PNG) para estilos tipográficos / UI-mockup; primeiro estilo: `notes` (validado à mão contra referências reais). Seleção de motor pelo `_ESTILO.md`.
- **v0.4.0:** segundo estilo HTML: `tweet_card` (print de tweet do X, sólido — cabeçalho editável nome/handle/avatar/selo/data, avatar local com fallback de inicial, dark/light, 4:5 e 1:1). Validado à mão contra referências reais.
- **v0.5.0:** `tweet_card` ganha o sub-modo `imagem` (card escuro flutuante sobre imagem de fundo; data + globo). A imagem de fundo chega pronta ao motor; a skill a obtém da pasta do usuário ou gerando via `/invisible-image` (mesmo aspect ratio do card). Validado à mão contra referência real.
- **v0.6.0:** terceiro estilo HTML: `tweet_editorial` (sequência editorial em tweet, estilo Pedro Sobral). **Componível por blocos** (cabecalho/breaking/paragrafos/imagem/cta sobre tema light/dark; ênfases inline cor-de-texto + highlight-de-bloco) — os tipos de card emergem das combinações. O bloco `imagem` tem modo placeholder e modo arquivo; a SKILL resolve as imagens em **duas passadas** (estrutura com placeholders primeiro; depois cadeia de sourcing: imagem real free Unsplash/Pexels/Wikimedia/Openverse → fallback `/invisible-image`). Cores das ênfases amostradas por pixel das refs; validado à mão contra 26 prints reais. Em paralelo, a copy ganha o formato `tweet-editorial` (cruzamento percepção×editorial) na `invisible-carrossel`.
- **Modo notícia:** vocação herdada do sistema de referência (Human Academy) — pesquisa pauta por nicho, gera texto (ou delega à `invisible-carrossel`) e veste no visual.

## Convenções

- Fluxo de código: worktree + branch, nunca direto na `main`.
- Documentação em português; código e variáveis em inglês.
- Convenção Invisible: skills com prefixo `invisible-`.
