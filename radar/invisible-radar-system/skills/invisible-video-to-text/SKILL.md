---
name: invisible-video-to-text
description: >
  Transforma um vídeo (link do Instagram, TikTok ou YouTube — ou um arquivo local) num MATERIAL.MD unificado e rotulado, pronto para alimentar as skills de copy. Faz duas leituras complementares: (1) TRANSCREVE A FALA com WhisperX (pt) e (2) LÊ O TEXTO NA TELA — caixinha de pergunta do Instagram, legenda queimada, título, lower-thirds — extraindo frames e interpretando-os com visão (não OCR). Junta tudo num só arquivo com blocos rotulados: texto na tela (o gatilho/contexto), fala transcrita (o conteúdo) e notas de contexto (relação entre eles, cenário, aviso de que a voz do vídeo ≠ a voz de saída da copy). O entregável é insumo de COLETA — não escreve carrossel nem sugere ângulos (isso é da invisible-carrossel). Use SEMPRE que o usuário pedir para "transcrever esse vídeo", "baixa esse reels e transcreve", "pega esse vídeo do YouTube/TikTok e vira material", "transforma esse reels em material pra carrossel", "o que tem escrito na tela desse vídeo". Requer yt-dlp, ffmpeg e WhisperX (a skill faz bootstrap).
---

# Vídeo → Material (transcrição da fala + texto na tela)

> **Localização dos scripts.** Os scripts vivem em `scripts/` ao lado deste arquivo. Rode-os com `python3 scripts/<nome>.py`. A skill é fina: ela orquestra; a lógica de baixar/transcrever/extrair frames está nos scripts. **A leitura do texto na tela é sua** (você lê os frames com visão) — o script só os extrai.

Você pega um vídeo de referência e o transforma num **material de trabalho** para copy. O vídeo tem **duas camadas de informação** que você captura em paralelo:

1. **A fala** — o que a pessoa diz (transcrição). É o **conteúdo**: a tese, o mecanismo, os pilares.
2. **O texto na tela** — o que está escrito por cima do vídeo. No Instagram, tipicamente a **caixinha de pergunta** que originou o vídeo (o gatilho, a dor) e uma **legenda queimada** (o público-alvo). No YouTube, o título e lower-thirds. No TikTok, legendas e stickers. É o **contexto** que enquadra a fala.

As duas juntas, rotuladas num só `material.md`, dão à skill de copy tudo que ela precisa: a dor/gatilho (texto na tela) + o conteúdo/tese (fala).

## O que esta skill NÃO faz

- **Não escreve copy nem sugere ângulos** — isso é da `invisible-carrossel` (que tem o modo mapa). Esta skill só **coleta e organiza** o material.
- **Não usa OCR** — você lê os frames com sua própria visão. OCR erra em fonte estilizada e não separa caixinha de legenda de título; sua leitura entende layout e contexto.

## Insumos

- **Um link** (Instagram / TikTok / YouTube) **ou um arquivo de vídeo local** já baixado.
- **Uma pasta de trabalho** onde salvar o material (o usuário aponta; na dúvida, pergunte ou use a pasta atual).

## Onde salvar

Um arquivo só, na pasta de trabalho: `material-<slug>.md` (slug do tema/fonte, kebab-case). O vídeo baixado fica ao lado (`<slug>.mp4`); a transcrição bruta também (`<slug>.txt`, registro do WhisperX).

## Fluxo

### Fase 0 — Bootstrap
```bash
python3 scripts/bootstrap.py --check-only
```
Confira `pronto: true` (precisa de `ffmpeg`, `ffprobe`, `yt_dlp`, `whisperx`). Pegue `yt_dlp_bin` e `whisperx_bin` da saída e passe-os aos scripts seguintes (eles também resolvem sozinhos, mas passar é mais rápido). Se faltar dependência, rode sem `--check-only` (instala no venv central `~/.invisible-radar/venv`). Se o JSON avisar que o modelo de transcrição não está em cache, avise o usuário do download (~1.5GB) **antes** de transcrever.

> Se já houver um WhisperX de outra skill (ex.: `~/.invisible-video/wxenv`), o `transcrever.py` o reaproveita — não precisa reinstalar.

### Fase 1 — Baixar (pular se for arquivo local)
```bash
python3 scripts/baixar.py "<link>" --out-dir "<pasta>" --slug "<slug>" --yt-dlp-bin "<yt_dlp_bin>"
```
Pega `arquivo`, `plataforma`, `url`, `duracao_seg` da saída JSON.
- **Instagram** costuma exigir login: o script tenta os cookies do Chrome, depois Safari, depois sem. Se falhar com `ok: false`, mostre a `instrucao` ao usuário (fazer login no Instagram no navegador) e pare.
- Se o usuário já passou um arquivo local, pule esta fase.

### Fase 2 — Transcrever a fala
```bash
python3 scripts/transcrever.py "<video>" --out-dir "<pasta>" --whisperx-bin "<whisperx_bin>"
```
Pega `texto` da saída. **Limpe levemente** o texto: corrija erros óbvios de reconhecimento (palavras truncadas, termos mal ouvidos) **preservando o sentido e o tom**. Não reescreva nem resuma — é transcrição, não edição. (O `.txt` bruto fica como registro.)

### Fase 3 — Ler o texto na tela (você, com visão)
```bash
python3 scripts/extrair_frames.py "<video>" --out-dir "<pasta>/frames" --max 10
```
O script extrai frames (densos nos primeiros segundos, onde a caixinha/título mora; esparsos no resto). **Leia os frames** e identifique:
- **Caixinha de pergunta** (Instagram): título da caixinha (handle/identidade) + a pergunta enviada.
- **Legenda queimada / sticker**: texto fixo na tela (define público, dá ênfase).
- **Título / lower-thirds** (YouTube): texto editorial sobreposto.
- **Notas de cenário**: o que o ambiente revela e é relevante para a voz (ex.: contexto religioso, profissional, etc.).

Separe cada elemento — não junte caixinha com legenda num bloco só. **Ao terminar, apague a pasta `frames/`** (são temporários): `rm -rf "<pasta>/frames"`.

### Fase 4 — Montar o material.md
Escreva **um** arquivo `material-<slug>.md` na pasta de trabalho, com esta estrutura (rotulada e auto-explicativa, para a skill de copy entender cada parte):

```markdown
# Material-fonte — <tema> (<plataforma>)

> **Fonte:** <url> — <plataforma>, ~<duração>s.
> **O que é este arquivo:** material bruto de um vídeo, pronto para alimentar uma
> skill de copy. Reúne, rotulado, a fala transcrita e o texto na tela.
> **Como usar:** o texto na tela dá a dor/gatilho e o público; a fala dá a
> tese/mecanismo/pilares. O carrossel nasce do conjunto.

## 1. TEXTO NA TELA — o gatilho e o contexto
[caixinha de pergunta, legenda queimada, título — cada um rotulado]

## 2. FALA TRANSCRITA — o conteúdo
[a transcrição limpa]

## 3. NOTAS DE CONTEXTO
[relação caixinha × fala; cenário; aviso: a voz do vídeo ≠ a voz de saída da
copy — este material é a ideia/dor/mecanismo, não a voz; a voz da marca vem de
um Arquivo de Voz separado na hora de escrever]
```

→ Apresente o caminho do `material.md` e ofereça encadear com a `invisible-carrossel` (ou outra skill de copy).

## Guardrails
- **Não invente texto na tela** que você não conseguiu ler nos frames. Se um texto estiver ilegível, marque `[ilegível]` e diga ao usuário.
- **Limpeza de transcrição é leve** — corrigir reconhecimento, não reescrever. Preserve o sentido e o tom coloquial.
- **Um arquivo só.** Não espalhe em vários `.md`; o material unificado é o contrato com a skill de copy.
- **Apague os frames temporários** ao terminar.
- Esta skill é **coleta**, não copy. Não sugira ângulos nem escreva o carrossel — entregue o material e pare.
