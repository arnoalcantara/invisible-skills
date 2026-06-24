---
name: invisible-legenda-arquivos
description: >
  Gera a transcrição de vídeos que já existem. O usuário aponta um vídeo OU uma pasta de vídeos e a skill transcreve com WhisperX (português, large-v3) e salva um `.json` irmão ao lado da origem — com a transcrição completa e timestamp por palavra (`segments[].words[]`, cada palavra com start/end medido — a fonte pra animação palavra-a-palavra no Remotion). Na linha de produção, o `.json` é nomeado pela BASE do corte, SEM o token de formato (_VERTICAL/_QUADRADO) nem _VAR<n>: um único `.json` serve o vertical, o quadrado e todas as variações do mesmo segmento (mesmo áudio). Em lote, roda WhisperX uma vez por base, não por arquivo. O vídeo nunca é tocado. Resumível (pula o que já tem `.json` da base). Use SEMPRE que o usuário pedir para "gerar legenda", "transcrever esses vídeos", "transcrever a pasta", "gerar o json", "tirar a transcrição do vídeo", "fazer as legendas pra animar no Remotion", ou apontar uma pasta de vídeos pedindo a transcrição. Requer ffmpeg e WhisperX (faz bootstrap).
---

# Legendas (JSON com timestamp por palavra)

O usuário aponta **um vídeo ou uma pasta de vídeos** e você devolve, por **base de segmento**, um `.json` irmão salvo **na mesma pasta**, nomeado **sem o token de formato nem _VAR**:

- **`<base>.json`** — transcrição **completa com timestamp por palavra** (`segments[].words[]`, cada palavra com `start`/`end` medido por wav2vec2, não interpolado). É a fonte pra animação palavra-a-palavra (estilo TikTok) no Remotion.

Um `.json` por base serve **todas as variantes do segmento** — vertical, quadrado e VARs — porque o áudio (logo, os timestamps) é idêntico. Ex.: `GANCHO_VAV19_OTIMIZADO_VERTICAL.mp4` e `GANCHO_VAV19_OTIMIZADO_QUADRADO.mp4` compartilham `GANCHO_VAV19_OTIMIZADO.json`.

Geramos só o JSON: é o que o pipeline precisa. A `invisible-legendas-aplicador` e a `invisible-video-var-gancho-escrito` consomem esse `.json` (achando-o pelo mesmo strip de formato/VAR). O timestamp por palavra é o dado que importa — e só o JSON o carrega.

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

Defaults embutidos: `--lang pt`, `--model large-v3`. O script roda em **lote**, **deduplica por base** (uma transcrição por segmento, mesmo havendo vertical+quadrado+VARs) e é **resumível** — por padrão pula a base cujo `.json` já existe; passe `--forcar` pra refazer. O progresso sai no stderr; o relatório final em JSON no stdout.

### Fase 3 — Ler o relatório e resumir
O stdout traz `total_videos`, `bases`, `gerados`, `pulados`, `erros` e um `relatorios[]` por base. No resumo ao usuário, liste cada `.json` que nasceu (`saida`) e a base a que pertence, e aponte a pasta. Mencione quando uma base foi transcrita uma vez só apesar de ter vertical+quadrado+VARs (é o ganho da linha). Se algum vier com `status: erro`, mostre a `etapa` e o trecho de `stderr` — não declare sucesso geral se houve erro.

## Como nomeia e onde salva (a regra da linha de produção)
O `.json` é nomeado pela **base do corte**, sem o token de formato (`_VERTICAL`/`_QUADRADO`) nem `_VAR<n>`, na mesma pasta dos vídeos (tipicamente `02_OTIMIZADOS`):
- `GANCHO_VAV19_OTIMIZADO_VERTICAL.mp4` → `GANCHO_VAV19_OTIMIZADO.json`
- `GANCHO_VAV19_OTIMIZADO_QUADRADO.mp4` → o mesmo `GANCHO_VAV19_OTIMIZADO.json`

Em lote, o representante transcrito é o `_VERTICAL` não-VAR. Não há pasta de saída separada — o `.json` mora junto dos vídeos do segmento.

## Encadeamento com o Remotion (o destino do JSON)
O `.json` é o que o Remotion consome pra legenda animada palavra-a-palavra: cada `word` tem `start`/`end`, então dá pra destacar a palavra atual, agrupar de N em N, animar entrada/saída. É exatamente o que a `invisible-legendas-aplicador` lê pra queimar a legenda no vídeo.

## Marcação de seção (gancho/desenvolvimento) no JSON
Se houver um sidecar de roteiro `<video>.md` ao lado do vídeo (gerado pelo desmembrador/combinador, com seções `# GANCHO`, `# DESENVOLVIMENTO`... + texto), a skill **marca cada palavra do JSON** com o campo `"secao"` e adiciona um bloco `"secoes": [{nome, start, end}]` no topo. Ela descobre QUANDO cada seção começa **casando o texto do MD contra a transcrição** (similaridade fuzzy, via `marcar_secoes.py`) — não usa tempos pré-gravados. Por isso é robusto a edição: se o vídeo combinado foi cortado depois de combinar, o tempo da seção é medido sobre o vídeo atual. Sem MD ao lado, o JSON sai normal (sem `secao`). É o que permite uma skill futura (ex.: geração de imagem por seção) saber o que é gancho, o texto dele e onde ele está no tempo.

## Anti-padrões (não faça)
- Recodificar, cortar ou mover o vídeo — esta skill só transcreve, não toca no original.
- Nomear o `.json` com o token de formato ou VAR no nome — a regra é nome-base (sem formato/VAR), pra um `.json` servir todas as variantes. Salvar em pasta separada também não: mora junto dos vídeos.
- Gerar `.srt` ou qualquer outro formato — a skill entrega só o `.json`. O timestamp por palavra é o que o pipeline usa; o resto é peso morto.
- Prometer ou esconder o download do modelo: cheque `modelo_pronto` e avise quando for `false`.
- Transcrever de novo o que já tem `.json` num lote sem `--forcar` — o script já pula; respeite o resumível.
- Assumir idioma: o padrão é `pt`; se o vídeo for em outro idioma, passe `--lang`.

## Os scripts
- `scripts/bootstrap.py` — detecta/instala ffmpeg + WhisperX (venv central reusado, nunca por projeto); reporta `whisperx_bin` e `modelo_pronto`. Cópia da do resto do sistema (cada skill autocontida).
- `scripts/legendar.py` — extrai áudio mono 16k, roda WhisperX (`--output_format json`) uma vez por **base** (deduplica vertical/quadrado/VARs pelo strip de formato+VAR), e move o `.json` pro lado dos vídeos nomeado pela base. Lote + resumível. Marca seções casando o `<base>_OTIMIZADO.md`. Imprime relatório JSON.
