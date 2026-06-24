---
name: invisible-legendas-aplicador
description: >
  Queima legenda animada num vídeo (vertical 9:16 ou quadrado 1:1) usando Remotion.
  Na linha de produção, o usuário aponta a pasta dos segmentos otimizados (02_OTIMIZADOS)
  e a skill legenda CADA SEGMENTO uma vez (vertical e quadrado, não-VAR), gravando o
  resultado na pasta-irmã 03_PREPARADOS como <id>_OTIMIZADO_LEGENDADO_VERTICAL.mp4 (o
  token de formato fica sempre por último). Assim a combinação lá na frente só concatena
  peças prontas, sem re-legendar. NÃO transcreve: consome o `.json` de timestamp por
  palavra que a invisible-legenda-arquivos gera por BASE (sem formato/VAR) — a skill acha
  o `.json` removendo o token de formato/VAR do nome do clipe. Estilos prontos: `reels` (palavra acende em amarelo, padrão de Reels/TikTok),
  `minimal` (branco, futuro esmaecido), `classic` (legenda em bloco no rodapé) e
  `capsula` (bloco estático por frase numa cápsula branca de cantos arredondados,
  texto preto — estilo legenda de repost/viral; opt-in via `--estilo capsula`). O
  default de estilo é POR FORMATO: vídeo vertical → reels; vídeo quadrado → classic
  (o bloco clássico no rodapé, padrão do feed). A composição se adapta à dimensão do
  vídeo (1080×1920 ou 1080×1080) e a posição da legenda escala com a altura, mantendo
  a mesma posição relativa. A legenda nunca vaza a margem (quebra de linha resolvida)
  e o vídeo original nunca é tocado. Use SEMPRE que o usuário pedir para "aplicar
  legenda", "legendar com remotion", "queimar legenda no vídeo", "burn das legendas",
  "colocar legenda animada", "legenda karaokê", "legendar as combinações", "legendar
  o quadrado", ou apontar vídeos pedindo a legenda embutida. Requer Node.js, npm e
  ffmpeg (faz bootstrap). Hormozi existe mas está em ajuste — não ofereça como pronto.
---

# Aplicador de Legendas (Remotion)

Você pega um vídeo vertical e devolve **o mesmo vídeo com a legenda animada queimada** —
karaokê palavra-a-palavra, no estilo que o usuário escolher. O motor é o Remotion: a
legenda é desenhada por código (HTML/CSS animado por frame), então o leque de estilo é
enorme.

> O vídeo original **nunca é tocado**. A saída nasce na pasta-irmã `03_PREPARADOS/`,
> com `_LEGENDADO` inserido antes do token de formato (`..._OTIMIZADO_LEGENDADO_VERTICAL.mp4`).

## Onde entra na linha de produção (etapa 02→03)

Esta skill é o **renderizador**, não o transcritor — e na linha nova ela legenda os
**segmentos otimizados**, não as combinações. Legenda-se cada segmento uma vez; a
combinação só concatena peças prontas.

O timestamp por palavra vem da
[`invisible-legenda-arquivos`](../invisible-legenda-arquivos/SKILL.md), que gera um
`<base>.json` (`segments[].words[]` com start/end medido) nomeado **sem formato nem VAR**.
A skill acha esse `.json` removendo o token de formato/VAR do nome do clipe. O fluxo:

1. `invisible-legenda-arquivos "<02_OTIMIZADOS>"` → cria `<base>.json` por segmento.
2. **esta skill** `"<02_OTIMIZADOS>"` → lê cada clipe vertical/quadrado não-VAR + o `.json` da base → `03_PREPARADOS/<id>_OTIMIZADO_LEGENDADO_VERTICAL.mp4` (e `_QUADRADO`).

Os clipes `_VAR<n>` (variações de gancho) são **pulados** no lote: vêm prontos da
`invisible-video-var-gancho-escrito` direto pra `03_PREPARADOS`. Se o `.json` da base não
existir, a skill avisa e pede para rodar a `invisible-legenda-arquivos` antes — ela não
inventa timestamp.

## Estilos (presets)

| Estilo | Marca | Quando |
|---|---|---|
| `reels` | palavra falada acende em **amarelo** com **pop animado** (spring + fade de cor + entrada deslizante), maiúsculas, contorno preto | padrão de Reels/TikTok, máxima atenção |
| `minimal` | tudo branco, minúsculas; palavras ainda-não-ditas **esmaecidas** | sóbrio, elegante |
| `classic` | legenda em **bloco** no rodapé, sem karaokê | legenda clássica de vídeo; **default do quadrado (feed)** |
| `capsula` | **bloco estático por frase** numa **cápsula branca** de cantos arredondados que abraça o texto (uma cápsula por linha), texto preto sans-serif bold, sem karaokê | estilo legenda de **repost/viral**; **opt-in** via `--estilo capsula` |
| ~~`hormozi`~~ | caixa amarela na palavra | **EXPERIMENTAL — em ajuste, não oferecer** |

**Default por formato.** Sem `--estilo`, a skill escolhe pela dimensão do vídeo: **vertical → `reels`**, **quadrado (1:1) → `classic`**. `--estilo` força um preset pra todos. O `capsula` **não é default de nenhum formato** — só entra quando pedido explicitamente (`--estilo capsula`). A largura é sempre 1080 (vertical e quadrado), então tipografia e margem lateral são iguais; só a posição vertical (`bottomOffset`) escala com a altura real (px do preset são em 1920) — a legenda fica na mesma posição relativa nos dois formatos.

Todos os parâmetros de cada preset (ritmo, fonte, tamanho, cor, posição, modo de
destaque) vivem no topo de `remotion/src/Captions.tsx`, em `PRESETS`. A legenda **não
vaza a margem**: o texto quebra em linha dentro de uma largura limitada (correção
embutida — não reverter).

Cada preset pode ligar uma **camada de animação** (campos opcionais; ausentes = destaque
"seco" de liga/desliga): `pop` (spring no scale da palavra ativa, com overshoot estilo
TikTok), `colorFadeFrames` (suaviza a troca de cor) e `enter` (entrada da página com
fade-in + slide de baixo). O `reels` já vem com a animação aprovada ligada. A interpolação
por frame (`spring`/`interpolate`/`interpolateColors`) é onde o Remotion ganha do `drawtext`
do ffmpeg — animação só se julga em movimento (use `remotion studio`, não `still`).

## Fluxo de execução

### Fase 0 — Bootstrap
```bash
python3 scripts/bootstrap.py --check-only
```
Lê o JSON. Precisa de **node + npm** (Remotion roda em Node) e **ffmpeg**. O template
Remotion é instalado num diretório central único (`~/.invisible-video/legendas-remotion`),
**uma vez**, e reusado. Se `pronto` for `false`, rode sem `--check-only` para sincronizar
o template e instalar (`npm install` na 1ª vez — alguns minutos; baixa o Remotion).

### Fase 1 — Confirmar alvo e estilo
- **Alvo:** tipicamente a pasta `02_OTIMIZADOS` (ou um vídeo). Numa pasta, pega os vídeos
  diretos, fora a `03_PREPARADOS` e os clipes `_VAR<n>` (que vêm prontos da var-gancho).
  Cheque que existe o `<base>.json` (sem formato/VAR) de cada segmento; se faltar, rode
  antes a `invisible-legenda-arquivos`.
- **Estilo:** pergunte qual preset (`reels` / `minimal` / `classic`). Default `reels`.
  Não ofereça `hormozi` (em ajuste).
- **Saída:** default pasta-irmã `03_PREPARADOS`. Sobrescreva com `--out-dir` só se o
  usuário pedir.

### Fase 2 — Aplicar
Um vídeo:
```bash
python3 scripts/aplicar.py "<video.mp4>" --estilo reels
```
Uma pasta inteira (todos os segmentos otimizados), estilo único:
```bash
python3 scripts/aplicar.py "<02_OTIMIZADOS>" --estilo reels
```
Cada vídeo: converte o `.json` → `Caption[]`, encena no projeto central e renderiza
(`npx remotion render <estilo>`). A composição se adapta sozinha à duração/dimensão de
cada vídeo (`parseMedia` no `calculateMetadata`). Render típico ~1–2 min por peça de
~60s a 1080×1920.

### Fase 3 — Resumo
Liste o que saiu em `03_PREPARADOS/`: cada `nome_saida`, o estilo usado e quantos OK. Aponte
qualquer vídeo pulado por falta do `.json` (e o que fazer: rodar a transcrição antes).

## Conferir um estilo sem renderizar o vídeo todo (rápido)
Para validar altura/cor/quebra de um preset, renderize **um frame** (não o vídeo inteiro):
```bash
cd ~/.invisible-video/legendas-remotion
npx remotion still <estilo> out/check.png --frame=440   # com public/ já encenado
```
Foi assim que afinamos a posição da `classic` sem re-renderizar.

Pra testar a **altura da legenda** num still sem editar o preset, passe o override `bottomOffsetPx` (px na altura real do vídeo) via `--props`:
```bash
npx remotion still classic out/h140.png --frame=240 \
  --props='{"videoSrc":"video.mp4","captionsSrc":"captions.json","preset":"classic","bottomOffsetPx":140}'
```
Quando achar a altura boa, crave no preset: `bottomOffset` (vertical) ou `bottomOffsetSquare` (quadrado) em `Captions.tsx`.

> **Editou um `.tsx`? Rode `bootstrap.py` ANTES de renderizar.** O render usa o projeto central (`~/.invisible-video/legendas-remotion`); o bootstrap sincroniza os fontes da skill pra lá. Sem isso, o render (still ou vídeo) usa o código antigo e parece que a edição "não fez nada".

## Pontos de confirmação
1. `<base>.json` presente (sem formato/VAR) pra cada segmento. 2. Estilo escolhido. 3. Pasta de saída `03_PREPARADOS`. 4. Resumo.

## Nomenclatura
- Pasta de saída: pasta-irmã `03_PREPARADOS/`.
- Arquivo: `_LEGENDADO` inserido **antes do token de formato** (formato sempre o último token).
  Ex.: `GANCHO_VAV19_OTIMIZADO_VERTICAL.mp4` → `GANCHO_VAV19_OTIMIZADO_LEGENDADO_VERTICAL.mp4`.
  E `..._OTIMIZADO_QUADRADO.mp4` → `..._OTIMIZADO_LEGENDADO_QUADRADO.mp4`.

## Anti-padrões (não faça)
- Transcrever aqui — o timestamp vem da `invisible-legenda-arquivos`. Sem `.json` da base, pare e avise.
- Legendar clipes `_VAR<n>` no lote — as variações de gancho vêm prontas da var-gancho-escrito.
- Pôr `_LEGENDADO` depois do token de formato — o formato é sempre o último token.
- Oferecer `hormozi` como pronto (está em ajuste).
- Mexer na quebra de linha do `Captions.tsx` (o `width:100%` + espaço fora do inline-block
  é o que impede o vazamento de margem — resolvido).
- Renderizar o vídeo inteiro só pra conferir estilo — use `remotion still` num frame.
- Tocar no vídeo original ou gravar fora de `03_PREPARADOS`.

## Referência
O método (formato Caption, presets, correção de borda, altura no Instagram, encadeamento
com a transcrição) está em `referencia/METODO.md`.
