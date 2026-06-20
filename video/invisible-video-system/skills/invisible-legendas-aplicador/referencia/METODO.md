# Método — Aplicador de Legendas (Remotion)

O porquê de cada decisão. A `SKILL.md` orquestra; aqui ficam as razões.

## O problema

Cortes já otimizados e combinados (saídas da `invisible-video-combinador`) precisam de
legenda **queimada** para Reels/TikTok. Legenda de player (SRT externo) não serve: o
Instagram não usa, e o estilo karaokê que segura atenção não existe em SRT. A legenda
tem que ser **desenhada e renderizada dentro do vídeo**.

Ferramenta: **Remotion** — vídeo por código React, cada frame é um componente. Permite
animar a legenda palavra-a-palavra com precisão de frame, coisa que ffmpeg/`drawtext`
não faz bem.

## Separação de responsabilidades

Duas skills, dois papéis — não se misturam:

- **`invisible-legenda-arquivos`** = transcrição. WhisperX (pt, large-v3) com timestamp
  **medido** por palavra (wav2vec2, não interpolado). Gera `<nome>.json` ao lado do vídeo.
- **`invisible-legendas-aplicador`** (esta) = render. Consome o `.json`, desenha e queima.

Por que separar: a transcrição é cara (CPU, modelo de 1.5GB) e o texto pode ser revisado
antes de queimar. Render é barato e iterável (troca de estilo sem re-transcrever). Uma
transcrição, N versões de legenda.

## Caption: o formato

O Remotion (`@remotion/captions`) trabalha com `Caption[]`:
```ts
type Caption = { text; startMs; endMs; timestampMs; confidence }
```
O `convert_captions.mjs` achata `segments[].words[]` do WhisperX numa Caption **por
palavra** (token), com o espaço preservado no início do `text` (` palavra`). Uma Caption
por palavra é o que permite o `createTikTokStyleCaptions` reagrupar em "páginas" e o
highlight saber qual palavra está ativa.

**Palavras sem timestamp** (score 0, sem start/end — acontece com monossílabos átonos):
o conversor interpola entre a borda da palavra anterior e o início da próxima. Sem isso,
a palavra "sumiria" da legenda.

## Páginas e ritmo (`combineMs`)

`createTikTokStyleCaptions({ combineTokensWithinMilliseconds })` agrupa as palavras em
páginas. Quanto maior o `combineMs`, mais palavras por página:
- `reels` 1200ms / `hormozi` 900ms — punchy, 1–4 palavras.
- `minimal` 1400ms — frases curtas.
- `classic` 2200ms — bloco de frase (legenda clássica).

## O destaque (highlightMode)

A palavra falada é detectada por `token.fromMs <= tempoAbsoluto < token.toMs`. Quatro modos:
- `color` (reels) — troca a cor para o destaque + leve `scale`.
- `box` (hormozi) — retângulo colorido atrás da palavra, texto invertido. **Em ajuste.**
- `opacity` (minimal) — a palavra falada fica 100%; as demais da página, esmaecidas (0.45).
- `none` (classic) — sem destaque; legenda em bloco.

## Correção de borda (não reverter)

Sintoma: com `whiteSpace: "pre"` no container, a frase ficava numa linha só e **vazava a
margem**. Causa: `pre` preserva o espaço mas **proíbe a quebra**.

Correção (validada na sessão de origem):
1. container com `width: "100%"` (largura limitada pela margem) e quebra normal;
2. o espaço entre palavras vai **fora** do `inline-block` (vira ponto de quebra natural);
3. a palavra fica **dentro** do `inline-block` para o `transform: scale` do destaque
   funcionar.

Assim a legenda quebra em linhas centradas dentro da margem, e o destaque continua animando.

## Altura no Instagram

O terço inferior da tela é onde o Instagram empilha legenda do post, @ e botões. Legenda
muito embaixo (a `classic` começou em `bottomOffset: 150`) fica ilegível ali. Subimos a
`classic` para `380`. Cada preset tem seu `bottomOffset` pensado para escapar dessa zona.

**Afinar sem re-render:** valide a altura/cor/quebra com `remotion still --frame=N` (um
frame só), não renderizando o vídeo inteiro. Foi como acertamos a `classic`.

## Projeto Remotion central

O template (`remotion/`) é instalado **uma vez** em `~/.invisible-video/legendas-remotion`
e reusado — node_modules do Remotion é pesado e não vai no repo de skills. O `bootstrap.py`
sincroniza os fontes (barato) e roda `npm install` só na 1ª vez ou quando o `package.json`
muda. Em runtime, o `aplicar.py` encena `public/video.mp4` + `public/captions.json` por
vídeo e dispara o render.

## Adaptação por vídeo

Cada combinação tem duração diferente. O `calculateMetadata` (Root) lê duração e dimensão
do próprio vídeo via `parseMedia` — a composição se molda sozinha, sem hardcode. Default de
fps é 30 (alvo da otimizadora/combinadora).

## Concat-copy não se aplica aqui

Diferente da combinadora (que faz `concat -c copy`), aqui há **reencode** obrigatório: a
legenda é pixel novo sobre o vídeo. Saída padrão do Remotion é H.264 + AAC. É a única etapa
do pipeline que necessariamente regenera o vídeo — por isso fica por último, depois de
otimizar e combinar.
