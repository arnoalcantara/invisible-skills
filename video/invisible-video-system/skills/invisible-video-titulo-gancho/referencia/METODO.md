# METODO — invisible-video-titulo-gancho

Referência técnica do overlay de título (gancho visual). O SKILL.md tem o fluxo; aqui
ficam a arquitetura e as decisões.

## Arquitetura (2 metades)

1. **Remotion desenha o título** (composição `Titulo`, 1080×1920, 30fps): cápsula branca
   única + emoji + texto, tudo `<div>`. Render com **fundo transparente** (ProRes 4444,
   `yuva444p`) — só o título, resto do quadro vazio. Conteúdo paramétrico via
   `public/props.json` lido no `calculateMetadata`.
2. **ffmpeg sobrepõe** o overlay transparente no gancho legendado, só na janela do título:
   `overlay=0:0:enable='lte(t,<dur>)':format=auto`. Mapeia o áudio original (`-map 0:a`)
   sem reprocessar de forma perceptível. A legenda já está queimada no gancho — continua
   embaixo.

## Props (public/props.json)

```json
{ "texto": "NÃO tem filhos entre 2 e 6 anos?", "emoji": "👀",
  "duracaoSeg": 3, "topOffset": 150, "fontSize": 64 }
```

- `texto`: a frase. `" / "` força quebra de linha manual; senão o balão único abraça tudo
  e a frase flui (quebra natural do container, `maxWidth`).
- `emoji`: um emoji, exibido acima do texto. Renderiza **colorido** (o Chromium do render
  tem a fonte de emoji colorido; não vira preto-e-branco).
- `duracaoSeg`: quanto o título fica na tela (a composição dura isso × fps). Default 3s.
- `topOffset`, `fontSize`: posição e tamanho, calibráveis no still.

## Estilo (constantes em Titulo.tsx)

Fundo `#FFFFFF`, texto `#000000`, `Helvetica, Arial, sans-serif` bold 800, `borderRadius`
generoso, sombra suave. Deliberadamente igual ao vocabulário do estilo de legenda
`capsula`/`capsula-palavra`, pra título (topo) e legenda (rodapé) parecerem do mesmo
sistema.

## Timing

Sem entrada: `opacity` = 1 desde o frame 0 (o usuário quer o título já na tela). Só um
fade-out nos últimos ~8 frames da duração. Nada de spring/slide de entrada.

## A armadilha da TIMEBASE (aprendida no Lote 10/DS6)

O overlay reencoda o gancho com libx264. O libx264 default gera timebase `1/15360`; o
legendador (Remotion) emite `1/90000`. Se o gancho-com-título e o desenvolvimento chegam
ao `combinar.py` com timebases diferentes, o concat demuxer produz **PTS quebrado**: os
frames estão todos lá (ex.: 6004 = 200s×30), mas o `duration` do container fica esticado
(deu 1172s em vez de 200s) e o `avg_frame_rate` despenca. Sintoma: combinado com duração
absurda / câmera lenta.

**Fix (na origem):** `aplicar.py` força `-video_track_timescale 90000` no encode do
overlay. Assim o gancho-com-título casa a timebase do resto do pipeline e o concat sai
limpo.

**Fix (retroativo, se já gerou sem):** remux só do container, rápido, sem reencodar:
`ffmpeg -i entrada.mp4 -c copy -video_track_timescale 90000 saida.mp4`.

**Lição de processo:** teste **1 combinado** antes de rodar o lote todo. O bug foi pego
no teste de um par, não depois de 20 arquivos errados.

## Nome de saída

`_TITULO` entra antes do token de formato (formato sempre por último):
`..._OTIMIZADO_LEGENDADO_TITULO_VERTICAL.mp4`. Com `--substituir`, o `..._LEGENDADO_<FMT>`
sem título é apagado (o combinador deve usar a versão com título).

## Portabilidade

O bootstrap instala o projeto Remotion em `~/.invisible-video/titulo-gancho-remotion`
(igual às outras skills de vídeo: legendas, gancho-escrito, painel-animado). O plugin não
carrega `node_modules` — o bootstrap resolve. `aplicar.py` aponta pra esse projeto central.

## Teste de aceitação

Lote 10 - Bruna Botelho - DS6 (30/07/2026): 10 ganchos (5 VAVs × 2), cada um com título
+ emoji nos 3s iniciais, nos dois formatos (vertical + retrato). Frases de 3 a 12
palavras (quebra automática em 2-3 linhas), emojis coloridos, convivendo com a legenda
`capsula-palavra` embaixo. Combinado, acelerado, com trilha, entregue. ✅ Aprovado pelo Arno.
