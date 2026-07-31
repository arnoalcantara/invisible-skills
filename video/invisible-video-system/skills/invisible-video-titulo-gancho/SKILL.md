---
name: invisible-video-titulo-gancho
description: >
  Sobrepõe um TÍTULO / GANCHO VISUAL no início de cada gancho de vídeo já legendado — um bloco de texto numa CÁPSULA branca única com um EMOJI acima, exibido por ~3s no começo do clipe. Diferente da legenda (que roda com a fala palavra a palavra): o título é um texto FIXO, escrito pelo editor (não vem da transcrição), que resume/provoca o gancho e prende o olho nos primeiros segundos. Aparece de imediato (SEM animação de entrada — já está na tela) e some com fade no fim. O texto é código Remotion de verdade (nunca quebra), renderizado como overlay transparente e sobreposto por cutaway com ffmpeg mantendo ÁUDIO e LEGENDA embaixo 100% intactos. Casa visualmente com o estilo de legenda `capsula`/`capsula-palavra` (cápsula branca, texto preto Helvetica bold). Gera um arquivo novo com _TITULO no nome (antes do token de formato), sem tocar no original. Recebe o texto+emoji de cada gancho num JSON (um por gancho). Roda DEPOIS de legendar e ANTES de combinar, só nos GANCHOS (o desenvolvimento não leva título). Requer Node.js + ffmpeg (faz bootstrap). Use quando o usuário pedir "título no gancho", "gancho visual", "texto/chamada no topo do vídeo", "cápsula de título", "headline no início".
---

# Título / gancho visual

Você sobrepõe um **título** (gancho visual) no começo de cada gancho já legendado: um
bloco de texto numa **cápsula branca única** com um **emoji** acima, por ~3s. O título
entra por cima, a **fala e a legenda continuam intactas por baixo** (cutaway, não overlay).

> **Regra mãe 1 — áudio e legenda SAGRADOS.** Só a faixa de **vídeo** recebe o overlay
> na janela do título; o áudio original é remuxado inteiro. A legenda (que já está
> queimada no clipe) continua rodando embaixo. Nada de reprocessar áudio.
>
> **Regra mãe 2 — o texto do título é DITADO, não transcrito.** Quem escreve as frases é
> o editor/usuário (uma por gancho), não o WhisperX. É um gancho de copy, não legenda.
>
> **Regra mãe 3 — só nos GANCHOS.** O desenvolvimento não leva título. Aplique apenas
> aos arquivos de gancho.

## Por que Remotion (o problema que isto resolve)

O texto do título tem que sair perfeito e legível. Renderizar como **texto Remotion**
(`<div>` de verdade) garante isso e dá controle total de cor, quebra, emoji e timing.
O overlay sai com fundo transparente (ProRes 4444) e é sobreposto por ffmpeg só nos N
segundos iniciais.

## Estilo (casa com a legenda cápsula)

Cápsula **branca única** (`#FFFFFF`) de cantos arredondados que abraça o texto inteiro,
texto **preto** (`#000000`) Helvetica bold, um **emoji** centralizado acima. Sem animação
de entrada (já está na tela no frame 0), fade-out no fim. É o mesmo vocabulário visual do
estilo de legenda `capsula`/`capsula-palavra`, então título (topo) e legenda (rodapé)
convivem no mesmo frame sem colidir.

## Dependências

- **Node.js + Remotion** — motor do overlay (projeto central instalado pelo bootstrap em
  `~/.invisible-video/titulo-gancho-remotion`).
- **ffmpeg/ffprobe** — a sobreposição do overlay no gancho.

Rode `python3 scripts/bootstrap.py --check-only` e trate `pronto: false`.

## Entrada

- Uma pasta com **ganchos já legendados** (ex.: `03_PREPARADOS/`), nomeados
  `..._LEGENDADO_<FORMATO>.mp4`, contendo `GANCHO` no nome.
- Um **JSON de títulos** que mapeia a BASE de cada gancho para `{texto, emoji}`:
  ```json
  {
    "DS_VAV138_GANCHO_1": {"texto": "NÃO tem filhos entre 2 e 6 anos?", "emoji": "👀"},
    "DS_VAV138_GANCHO_2": {"texto": "Incrível o que acontece no cérebro do seu filho.", "emoji": "🧠"}
  }
  ```
  A chave casa o prefixo do nome até `GANCHO_<n>`. Vertical e retrato do mesmo gancho
  compartilham a mesma chave (recebem o mesmo título).

## O fluxo

1. **Capture os títulos** com o usuário: uma frase por gancho + um emoji por frase.
   O emoji você pode sugerir pelo sentido da frase (barato de trocar); confirme com ele.
   Grave no `titulos.json`.
2. **Prova de 1 gancho** (portão de aprovação): rode `aplicar.py` numa cópia de um gancho
   e extraia um still (ffmpeg) mostrando o título + a legenda no mesmo frame. Mostre ao
   usuário. Confirme cor/tamanho/posição/quebra/tempo antes do lote.
3. **Aplique no lote**: `aplicar.py <pasta> --titulos titulos.json --substituir`.
   Gera `..._TITULO_<FMT>.mp4` e (com `--substituir`) apaga o legendado sem título.

```bash
python3 scripts/aplicar.py "<pasta 03_PREPARADOS>" \
  --titulos "<titulos.json>" [--dur 3] [--top 150] [--fonte 64] [--substituir]
```

- **Confira frases longas e o formato retrato** (mais estreito): extraia um still de um
  gancho de frase longa em cada formato antes de confiar no lote todo.

## Nome de saída

`_TITULO` acumula **antes** do token de formato:
`..._OTIMIZADO_LEGENDADO_TITULO_VERTICAL.mp4`. O nome conta o histórico da esquerda pra
direita, como o resto da esteira.

## Onde entra na esteira

Passo **entre legendar (3.1) e combinar (4)**, só nos ganchos. O combinador então usa o
gancho-com-título. É uma etapa **opcional** de lote (nem todo lote tem título de gancho).

## Armadilha da timebase (não pule)

O overlay reencoda o gancho com libx264. Se a timebase divergir da do resto do pipeline
(o legendador emite `1/90000`), o `combinar.py` da etapa seguinte concatena com PTS
quebrado e a **duração do combinado estoura** (frames certos, timestamps errados). Por
isso o `aplicar.py` já força `-video_track_timescale 90000`. Se pegar um combinado com
duração absurda, cheque a timebase das partes (`ffprobe ... time_base`) antes de tudo.
**Teste 1 combinado antes de rodar o lote todo.**

## Anti-padrões (não faça)

- **Usar a transcrição como título.** O título é copy ditada, não legenda.
- **Aplicar no desenvolvimento.** Só nos ganchos.
- **Animar a entrada.** O usuário quer o título já na tela (sem "entrar").
- **Cápsula por linha.** É uma cápsula única abraçando o bloco inteiro.
- **Pular o portão da prova.** Sempre um still aprovado antes do lote.
- **Ignorar a timebase.** Sem `90000`, a combinação quebra.
