# invisible-carrossel-visual

Sistema visual de carrossel da Invisible. Transforma um **roteiro pronto** (texto card a card) numa peça visual: os cards renderizados como PNGs, vestidos numa linguagem visual decodificada de **referências**.

É o lado VISUAL do carrossel. O lado COPY é a skill `invisible-carrossel` (plugin `invisible-copy`), que escreve o texto fiel à fonte. Aqui, esse texto é renderizado.

## Skills

### `invisible-estilo-decoder`

Aponte uma **pasta de referências visuais** (imagens de inspiração de um estilo) e a skill as lê por **visão** (decompondo grids) e congela o sistema visual num arquivo **`[NomeDaPasta]_ESTILO.md`** salvo na própria pasta. Esse briefing é o contrato que o produtor visual lê em vez de re-analisar as imagens a cada carrossel — mais barato, mais rápido e idêntico toda vez. Não gera imagem; só o contrato.

```
> decodifica o estilo dessas referências: <pasta>
```

O `[Pasta]_ESTILO.md` é editável à mão: é a fonte da verdade do estilo.

### `invisible-carrossel-visual`

Recebe dois insumos:
1. **Roteiro pronto** — um `.md` com o texto card a card (saída da `invisible-carrossel`).
2. **Pasta de referências visuais** — imagens de inspiração de um estilo de carrossel.

E entrega os **cards renderizados** (PNG), na estética das referências.

**Dois motores de render**, escolhidos pelo campo `motor:` do `_ESTILO.md`:

| `motor:` | Para | Como | Vantagem |
|---|---|---|---|
| `html` | Estilos **tipográficos / UI-mockup** (ex.: app de Notas, tweet-card) | HTML/CSS → PNG via Chrome headless (`render_html.py`) | Pixel-perfeito, texto nunca erra, custo zero, reproduzível |
| `higgsfield` | Estilos com **imagem gerada** (foto, cena, arte) | GPT Image 2 via Higgsfield CLI (`gerar_slide.py`), texto dentro da imagem | Único caminho quando o fundo é imagem generativa |

**Como funciona:**
- Decodifica as referências por **visão** e congela num `_ESTILO.md` na pasta (com o campo `motor:`). Da próxima vez, lê o briefing congelado.
- **Lê o `motor:`** e roteia para o render certo.
- Veste o texto respeitando o **papel** de cada slide (capa / interno / fecho).
- Prova UM card (a capa) antes do lote; verifica cada slide por visão pós-render.

**Motor HTML — contrato de roteiro (JSON):** cada card tem `papel` (capa/interno/fecho), `tema` (dark/light), e o conteúdo (`titulo`+`destaque`+`cta` na capa/fecho; `blocos` no interno). `ratio` = `4x5` (default) ou `1x1`. Ver a docstring de `render_html.py`.

**Motor Higgsfield — coleta robusta:** dispara o job e recupera por id; nunca confia no `--wait` (que dá 502 na coleta e cobra mesmo falhando).

### Estilos com template HTML pronto
- **`notes`** — mockup do app Notas do iOS (moldura, SF Pro, bloco de seleção amarelo com carets, dark/light, 4:5 e 1:1). Validado à mão contra referências reais.
- **`tweet_card`** — print de tweet do X (Twitter). Cabeçalho editável: nome, handle, avatar (arquivo local, fallback de inicial), selo verificado opcional, data opcional. SF Pro, 4:5 e 1:1. Dois sub-modos (campo `fundo`): **`solido`** (tweet tela-cheia, fundo branco/preto, dark/light) e **`imagem`** (card escuro flutuante sobre imagem de fundo; requer `fundo_imagem` local — a skill a obtém da pasta do usuário ou gerando via `/invisible-image`). Validado à mão contra referências reais.

## Requisitos

- **Motor HTML:** um **Chrome/Chromium** (no macOS, o Google Chrome basta). Sem login, grátis.
- **Motor Higgsfield** (só para estilos com imagem gerada):
  ```bash
  npm install -g @higgsfield/cli
  higgsfield auth login
  ```
- Uma **pasta de referências visuais** (com ou sem `_ESTILO.md`).

A skill faz bootstrap (`scripts/bootstrap.py`) e reporta o estado de cada motor.

## Uso

```
> renderiza esse carrossel: <roteiro.md>, usando as referências em <pasta>
```

A skill lê o estilo + motor, mostra o plano, gera a capa para aprovação, e então o lote.

## Roadmap

- **v0.1.0:** motor Higgsfield (texto-na-imagem).
- **v0.3.0:** motor HTML (HTML/CSS → PNG) para estilos tipográficos / UI-mockup; primeiro estilo: `notes`.
- **v0.4.0:** segundo estilo HTML: `tweet_card` (print de tweet do X, sólido).
- **v0.5.0:** `tweet_card` sub-modo `imagem` (card flutuante sobre imagem de fundo; imagem da pasta do usuário ou gerada via `/invisible-image`).
- **Modo notícia:** pesquisa pauta por nicho e gera o carrossel ponta a ponta.
