---
name: invisible-legenda-arquivos
description: >
  Gera a transcrição de vídeos que já existem. O usuário aponta um vídeo OU uma pasta de vídeos e a skill transcreve cada um com WhisperX (português, large-v3) e salva UM arquivo irmão ao lado da origem, com o MESMO nome do vídeo: um `.json` com a transcrição completa e timestamp por palavra (`segments[].words[]`, cada palavra com start/end medido — a fonte pra animação palavra-a-palavra no Remotion). O vídeo nunca é tocado. Roda em lote numa pasta inteira e é resumível (pula o que já tem `.json`). Use SEMPRE que o usuário pedir para "gerar legenda", "transcrever esses vídeos", "transcrever a pasta", "gerar o json", "tirar a transcrição do vídeo", "fazer as legendas pra animar no Remotion", ou apontar uma pasta de vídeos pedindo a transcrição. Requer ffmpeg e WhisperX (faz bootstrap).
---

# Legendas (JSON com timestamp por palavra)

O usuário aponta **um vídeo ou uma pasta de vídeos** e você devolve, para cada um, um arquivo irmão salvo **na mesma pasta, com o mesmo nome do vídeo**:

- **`<nome>.json`** — transcrição **completa com timestamp por palavra** (`segments[].words[]`, cada palavra com `start`/`end` medido por wav2vec2, não interpolado). É a fonte pra animação palavra-a-palavra (estilo TikTok) no Remotion.

Geramos só o JSON: é o que o pipeline precisa. A `invisible-legendas-aplicador` consome esse `.json` pra queimar a legenda animada. O timestamp por palavra é o dado que importa — e só o JSON o carrega.

> O vídeo original **nunca é tocado**. Só nasce o `.json` ao lado dele.

## Por que esta skill é "fina"

Toda a lógica vive em `scripts/`. A `SKILL.md` só orquestra: bootstrap → legendar → resumo. Os pontos de decisão (idioma, aviso de download) ficam com você, não enterrados no código.

## Fluxo de execução

### Fase 0 — Bootstrap
```bash
python3 scripts/bootstrap.py --check-only
```
Lê o JSON. Precisa de **ffmpeg** (extração de áudio) e **WhisperX** (transcrição). Se faltar, rode sem `--check-only` (instala ffmpeg via brew e cria o venv central `~/.invisible-video/wxenv` uma única vez) ou siga as `instrucoes` do JSON.

Guarde dois campos: `whisperx_bin` (caminho a passar adiante) e `modelo_pronto`. **Se `modelo_pronto` for `false`**, a 1ª transcrição vai baixar o modelo `large-v3` (~1.5GB) + alinhamento PT — **avise o usuário antes de rodar**. Se for `true`, segue direto.

### Fase 1 — Confirmar o alvo
- **Alvo:** o caminho que o usuário deu. Pode ser um arquivo único ou uma pasta. Numa pasta, a skill pega os vídeos **diretos** nela (sem recursão), em ordem.
- **Idioma:** padrão `pt`. Só mude com `--lang` se o vídeo for em outro idioma.

Se a pasta tem muitos vídeos e o modelo ainda não está em cache, diga ao usuário que a primeira roda inclui o download e que cada vídeo leva ~1min de CPU.

### Fase 2 — Legendar
Caso típico (pasta inteira, português):
```bash
python3 scripts/legendar.py "<pasta>" --whisperx-bin "<whisperx_bin do bootstrap>"
```
Arquivo único:
```bash
python3 scripts/legendar.py "<video.mp4>" --whisperx-bin "<whisperx_bin>"
```
Re-transcrever e sobrescrever o que já existe:
```bash
python3 scripts/legendar.py "<pasta>" --whisperx-bin "<whisperx_bin>" --forcar
```

Defaults embutidos: `--lang pt`, `--model large-v3`. O script roda em **lote** e é **resumível** — por padrão pula o vídeo cujo `.json` já existe; passe `--forcar` pra refazer. O progresso por vídeo sai no stderr; o relatório final em JSON no stdout.

### Fase 3 — Ler o relatório e resumir
O stdout traz `total`, `gerados`, `pulados`, `erros` e um `relatorios[]` por vídeo. No resumo ao usuário, liste cada vídeo com seu status e o arquivo que nasceu (`saida`), e aponte a pasta onde ficou. Se algum vier com `status: erro`, mostre a `etapa` e o trecho de `stderr` — não declare sucesso geral se houve erro.

## Como nomeia e onde salva (a regra, fixa)
Para `<pasta>/CORTE.mp4`:
- `<pasta>/CORTE.json`

Mesmo nome do vídeo, mesma pasta, ao lado do original. Não há pasta de saída separada — a transcrição mora junto do vídeo a que pertence.

## Encadeamento com o Remotion (o destino do JSON)
O `.json` é o que o Remotion consome pra legenda animada palavra-a-palavra: cada `word` tem `start`/`end`, então dá pra destacar a palavra atual, agrupar de N em N, animar entrada/saída. É exatamente o que a `invisible-legendas-aplicador` lê pra queimar a legenda no vídeo.

## Marcação de seção (gancho/desenvolvimento) no JSON
Se houver um sidecar de roteiro `<video>.md` ao lado do vídeo (gerado pelo desmembrador/combinador, com seções `# GANCHO`, `# DESENVOLVIMENTO`... + texto), a skill **marca cada palavra do JSON** com o campo `"secao"` e adiciona um bloco `"secoes": [{nome, start, end}]` no topo. Ela descobre QUANDO cada seção começa **casando o texto do MD contra a transcrição** (similaridade fuzzy, via `marcar_secoes.py`) — não usa tempos pré-gravados. Por isso é robusto a edição: se o vídeo combinado foi cortado depois de combinar, o tempo da seção é medido sobre o vídeo atual. Sem MD ao lado, o JSON sai normal (sem `secao`). É o que permite uma skill futura (ex.: geração de imagem por seção) saber o que é gancho, o texto dele e onde ele está no tempo.

## Anti-padrões (não faça)
- Recodificar, cortar ou mover o vídeo — esta skill só transcreve, não toca no original.
- Salvar o `.json` em pasta separada ou com nome diferente do vídeo — a regra é mesmo nome, mesma pasta.
- Gerar `.srt` ou qualquer outro formato — a skill entrega só o `.json`. O timestamp por palavra é o que o pipeline usa; o resto é peso morto.
- Prometer ou esconder o download do modelo: cheque `modelo_pronto` e avise quando for `false`.
- Transcrever de novo o que já tem `.json` num lote sem `--forcar` — o script já pula; respeite o resumível.
- Assumir idioma: o padrão é `pt`; se o vídeo for em outro idioma, passe `--lang`.

## Os scripts
- `scripts/bootstrap.py` — detecta/instala ffmpeg + WhisperX (venv central reusado, nunca por projeto); reporta `whisperx_bin` e `modelo_pronto`. Cópia da do resto do sistema (cada skill autocontida).
- `scripts/legendar.py` — extrai áudio mono 16k, roda WhisperX uma vez por vídeo (`--output_format json`), e move o `.json` pro lado do vídeo com o nome da origem. Lote + resumível. Imprime relatório JSON.
