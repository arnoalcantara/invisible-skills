---
name: invisible-legendas-aplicador
description: >
  Queima legenda animada num vídeo vertical usando Remotion. O usuário aponta um
  vídeo OU uma pasta (tipicamente a COMBINAÇÕES) e a skill renderiza a legenda no
  estilo escolhido, gravando o resultado em LEGENDADOS/<nome>_LEGENDADO.mp4. NÃO
  transcreve: consome o `.json` de timestamp por palavra que a invisible-legenda-arquivos
  já gera ao lado de cada vídeo (mesmo nome). Estilos prontos: `reels` (palavra
  acende em amarelo, padrão de Reels/TikTok), `minimal` (branco, futuro esmaecido)
  e `classic` (legenda em bloco no rodapé). A legenda nunca vaza a margem (quebra
  de linha resolvida) e o vídeo original nunca é tocado. Use SEMPRE que o usuário
  pedir para "aplicar legenda", "legendar com remotion", "queimar legenda no vídeo",
  "burn das legendas", "colocar legenda animada", "legenda karaokê", "legendar as
  combinações", ou apontar vídeos pedindo a legenda embutida. Requer Node.js, npm
  e ffmpeg (faz bootstrap). Hormozi existe mas está em ajuste — não ofereça como pronto.
---

# Aplicador de Legendas (Remotion)

Você pega um vídeo vertical e devolve **o mesmo vídeo com a legenda animada queimada** —
karaokê palavra-a-palavra, no estilo que o usuário escolher. O motor é o Remotion: a
legenda é desenhada por código (HTML/CSS animado por frame), então o leque de estilo é
enorme.

> O vídeo original **nunca é tocado**. A saída nasce em `LEGENDADOS/`, com o nome do
> vídeo de origem + `_LEGENDADO`.

## De onde vem a legenda (encadeamento)

Esta skill é o **renderizador**, não o transcritor. O timestamp por palavra vem da
[`invisible-legenda-arquivos`](../invisible-legenda-arquivos/SKILL.md), que gera um
`<nome>.json` (`segments[].words[]` com start/end medido) ao lado de cada vídeo. O fluxo
completo numa pasta de combinações:

1. `invisible-legenda-arquivos "<COMBINAÇÕES>"` → cria `<nome>.json` por vídeo.
2. **esta skill** → lê vídeo + `<nome>.json` → `LEGENDADOS/<nome>_LEGENDADO.mp4`.

Se o `.json` não existir ao lado do vídeo, a skill avisa e pede para rodar a
`invisible-legenda-arquivos` antes — ela não inventa timestamp.

## Estilos (presets)

| Estilo | Marca | Quando |
|---|---|---|
| `reels` | palavra falada acende em **amarelo** com **pop animado** (spring + fade de cor + entrada deslizante), maiúsculas, contorno preto | padrão de Reels/TikTok, máxima atenção |
| `minimal` | tudo branco, minúsculas; palavras ainda-não-ditas **esmaecidas** | sóbrio, elegante |
| `classic` | legenda em **bloco** no rodapé, sem karaokê | legenda clássica de vídeo |
| ~~`hormozi`~~ | caixa amarela na palavra | **EXPERIMENTAL — em ajuste, não oferecer** |

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
- **Alvo:** o vídeo ou a pasta que o usuário deu (numa pasta, pega os vídeos diretos,
  fora a própria `LEGENDADOS`). Cheque que existe um `<nome>.json` irmão de cada vídeo;
  se faltar, rode antes a `invisible-legenda-arquivos`.
- **Estilo:** pergunte qual preset (`reels` / `minimal` / `classic`). Default `reels`.
  Não ofereça `hormozi` (em ajuste).
- **Saída:** default `LEGENDADOS/` dentro da pasta do vídeo (logo, dentro de COMBINAÇÕES
  quando é o caso). Sobrescreva com `--out-dir` só se o usuário pedir.

### Fase 2 — Aplicar
Um vídeo:
```bash
python3 scripts/aplicar.py "<video.mp4>" --estilo reels
```
Uma pasta inteira (todas as combinações), estilo único:
```bash
python3 scripts/aplicar.py "<COMBINAÇÕES>" --estilo reels
```
Cada vídeo: converte o `.json` → `Caption[]`, encena no projeto central e renderiza
(`npx remotion render <estilo>`). A composição se adapta sozinha à duração/dimensão de
cada vídeo (`parseMedia` no `calculateMetadata`). Render típico ~1–2 min por peça de
~60s a 1080×1920.

### Fase 3 — Resumo
Liste o que saiu em `LEGENDADOS/`: cada `nome_saida`, o estilo usado e quantos OK. Aponte
qualquer vídeo pulado por falta do `.json` (e o que fazer: rodar a transcrição antes).

## Conferir um estilo sem renderizar o vídeo todo (rápido)
Para validar altura/cor/quebra de um preset, renderize **um frame** (não o vídeo inteiro):
```bash
cd ~/.invisible-video/legendas-remotion
npx remotion still <estilo> out/check.png --frame=440   # com public/ já encenado
```
Foi assim que afinamos a posição da `classic` sem re-renderizar.

## Pontos de confirmação
1. `.json` presente ao lado de cada vídeo. 2. Estilo escolhido. 3. Pasta de saída. 4. Resumo.

## Nomenclatura
- Pasta de saída: `LEGENDADOS/` (default dentro da pasta do vídeo).
- Arquivo: **nome do vídeo de origem + `_LEGENDADO`**.
  Ex.: `GANCHO_VAV19__DESENVOLVIMENTO_VAV23.mp4` → `GANCHO_VAV19__DESENVOLVIMENTO_VAV23_LEGENDADO.mp4`.

## Anti-padrões (não faça)
- Transcrever aqui — o timestamp vem da `invisible-legenda-arquivos`. Sem `.json`, pare e avise.
- Oferecer `hormozi` como pronto (está em ajuste).
- Mexer na quebra de linha do `Captions.tsx` (o `width:100%` + espaço fora do inline-block
  é o que impede o vazamento de margem — resolvido).
- Renderizar o vídeo inteiro só pra conferir estilo — use `remotion still` num frame.
- Tocar no vídeo original ou gravar fora de `LEGENDADOS`.

## Referência
O método (formato Caption, presets, correção de borda, altura no Instagram, encadeamento
com a transcrição) está em `referencia/METODO.md`.
