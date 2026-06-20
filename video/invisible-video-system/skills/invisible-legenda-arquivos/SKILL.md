---
name: invisible-legenda-arquivos
description: >
  Gera legendas a partir de vídeos que já existem. O usuário aponta um vídeo OU uma pasta de vídeos e a skill transcreve cada um com WhisperX (português, large-v3) e salva DOIS arquivos irmãos ao lado da origem, com o MESMO nome do vídeo: um `.srt` (legenda por frase, legível, pronto pra revisar ou subir num player) e um `.json` (transcrição completa com timestamp por palavra — `segments[].words[]` com start/end medido, a fonte pra animação palavra-a-palavra no Remotion). O vídeo nunca é tocado. Roda em lote numa pasta inteira e é resumível (pula o que já tem legenda). Use SEMPRE que o usuário pedir para "gerar legenda", "criar os srt", "legendar esses vídeos", "transcrever a pasta", "gerar srt e json", "tirar a legenda do vídeo", "fazer as legendas pra animar no Remotion", ou apontar uma pasta de vídeos pedindo a transcrição. Requer ffmpeg e WhisperX (faz bootstrap).
---

# Legendas (SRT + JSON com timestamp por palavra)

O usuário aponta **um vídeo ou uma pasta de vídeos** e você devolve, para cada um, dois arquivos irmãos salvos **na mesma pasta, com o mesmo nome do vídeo**:

- **`<nome>.srt`** — legenda por **frase**. É o painel legível pra conferir/corrigir o texto, e o formato pronto pra subir num player (YouTube). No Remotion serve pra legenda básica em bloco.
- **`<nome>.json`** — transcrição **completa com timestamp por palavra** (`segments[].words[]`, cada palavra com `start`/`end` medido por wav2vec2, não interpolado). É a fonte pra animação palavra-a-palavra (estilo TikTok) no Remotion.

Geramos **os dois** de propósito: o SRT achata o tempo por palavra e esse dado não dá pra recuperar dele depois. Uma transcrição, dois arquivos — sem retrabalho lá na frente.

> O vídeo original **nunca é tocado**. Só nascem os arquivos de legenda ao lado dele.

## Por que esta skill é "fina"

Toda a lógica vive em `scripts/`. A `SKILL.md` só orquestra: bootstrap → legendar → resumo. Os pontos de decisão (formatos, idioma, aviso de download) ficam com você, não enterrados no código.

## Fluxo de execução

### Fase 0 — Bootstrap
```bash
python3 scripts/bootstrap.py --check-only
```
Lê o JSON. Precisa de **ffmpeg** (extração de áudio) e **WhisperX** (transcrição). Se faltar, rode sem `--check-only` (instala ffmpeg via brew e cria o venv central `~/.invisible-video/wxenv` uma única vez) ou siga as `instrucoes` do JSON.

Guarde dois campos: `whisperx_bin` (caminho a passar adiante) e `modelo_pronto`. **Se `modelo_pronto` for `false`**, a 1ª transcrição vai baixar o modelo `large-v3` (~1.5GB) + alinhamento PT — **avise o usuário antes de rodar**. Se for `true`, segue direto.

### Fase 1 — Confirmar o alvo e os formatos
- **Alvo:** o caminho que o usuário deu. Pode ser um arquivo único ou uma pasta. Numa pasta, a skill pega os vídeos **diretos** nela (sem recursão), em ordem.
- **Formatos:** o padrão é gerar **os dois** (`srt,json`). Só restrinja se o usuário pedir explicitamente ("só o srt", "só o json") — aí passe `--formatos srt` ou `--formatos json`.
- **Idioma:** padrão `pt`. Só mude com `--lang` se o vídeo for em outro idioma.

Se a pasta tem muitos vídeos e o modelo ainda não está em cache, diga ao usuário que a primeira roda inclui o download e que cada vídeo leva ~1min de CPU.

### Fase 2 — Legendar
Caso típico (pasta inteira, os dois formatos, português):
```bash
python3 scripts/legendar.py "<pasta>" --whisperx-bin "<whisperx_bin do bootstrap>"
```
Arquivo único:
```bash
python3 scripts/legendar.py "<video.mp4>" --whisperx-bin "<whisperx_bin>"
```
Só um formato:
```bash
python3 scripts/legendar.py "<pasta>" --whisperx-bin "<whisperx_bin>" --formatos srt
```
Re-transcrever e sobrescrever o que já existe:
```bash
python3 scripts/legendar.py "<pasta>" --whisperx-bin "<whisperx_bin>" --forcar
```

Defaults embutidos: `--lang pt`, `--model large-v3`, `--formatos srt,json`. O script roda em **lote** e é **resumível** — por padrão pula o vídeo cujos alvos (`.srt`/`.json`) já existem; passe `--forcar` pra refazer. O progresso por vídeo sai no stderr; o relatório final em JSON no stdout.

### Fase 3 — Ler o relatório e resumir
O stdout traz `total`, `gerados`, `pulados`, `erros` e um `relatorios[]` por vídeo. No resumo ao usuário, liste cada vídeo com seu status e os arquivos que nasceram (`saidas`), e aponte a pasta onde ficaram. Se algum vier com `status: erro`, mostre a `etapa` e o trecho de `stderr` — não declare sucesso geral se houve erro.

## Como nomeia e onde salva (a regra, fixa)
Para `<pasta>/CORTE.mp4`:
- `<pasta>/CORTE.srt`
- `<pasta>/CORTE.json`

Mesmo nome do vídeo, mesma pasta, ao lado do original. Não há pasta de saída separada — a legenda mora junto do vídeo a que pertence.

## Encadeamento com o Remotion (o destino do JSON)
O `.json` é o que o Remotion consome pra legenda animada palavra-a-palavra: cada `word` tem `start`/`end`, então dá pra destacar a palavra atual, agrupar de N em N, animar entrada/saída. O `@remotion/captions` também lê SRT, mas só pro estilo básico em bloco — a animação por palavra exige o JSON. Por isso a skill entrega os dois: SRT pro caminho simples e revisão, JSON pra animação.

> SRT e JSON **não se conversam**: corrigir o texto num não atualiza o outro. Se o usuário for revisar o texto à mão, o lugar é o SRT (legível); se confia na transcrição, vai direto ao JSON.

## Marcação de seção (gancho/desenvolvimento) no JSON
Se houver um sidecar de roteiro `<video>.md` ao lado do vídeo (gerado pelo desmembrador/combinador, com seções `# GANCHO`, `# DESENVOLVIMENTO`... + texto), a skill **marca cada palavra do JSON** com o campo `"secao"` e adiciona um bloco `"secoes": [{nome, start, end}]` no topo. Ela descobre QUANDO cada seção começa **casando o texto do MD contra a transcrição** (similaridade fuzzy, via `marcar_secoes.py`) — não usa tempos pré-gravados. Por isso é robusto a edição: se o vídeo combinado foi cortado depois de combinar, o tempo da seção é medido sobre o vídeo atual. Sem MD ao lado, o JSON sai normal (sem `secao`). É o que permite uma skill futura (ex.: geração de imagem por seção) saber o que é gancho, o texto dele e onde ele está no tempo.

## Anti-padrões (não faça)
- Recodificar, cortar ou mover o vídeo — esta skill só gera legenda, não toca no original.
- Salvar a legenda em pasta separada ou com nome diferente do vídeo — a regra é mesmo nome, mesma pasta.
- Gerar só o SRT por padrão "pra economizar" — o JSON é barato (sai na mesma transcrição) e é o que o Remotion precisa. Só restrinja se o usuário pedir.
- Prometer ou esconder o download do modelo: cheque `modelo_pronto` e avise quando for `false`.
- Transcrever de novo o que já tem legenda num lote sem `--forcar` — o script já pula; respeite o resumível.
- Assumir idioma: o padrão é `pt`; se o vídeo for em outro idioma, passe `--lang`.

## Os scripts
- `scripts/bootstrap.py` — detecta/instala ffmpeg + WhisperX (venv central reusado, nunca por projeto); reporta `whisperx_bin` e `modelo_pronto`. Cópia da do resto do sistema (cada skill autocontida).
- `scripts/legendar.py` — extrai áudio mono 16k, roda WhisperX uma vez por vídeo (`--output_format all`), e move só os formatos pedidos pro lado do vídeo com o nome da origem. Lote + resumível. Imprime relatório JSON.
