# Método validado — desmembrar bruta por seção do roteiro

Este documento registra o método que funcionou numa sessão real de edição (brutas
verticais de aula, roteiros com `[GANCHO]`/`[DESENVOLVIMENTO]`/...). Está aqui para
que ninguém reintroduza o que já se mostrou errado.

## O problema

Cortar cada bruta num vídeo por seção do roteiro, preservando qualidade técnica,
removendo silêncio inicial/final e a sujeira auditiva das bordas (tosse, respiração,
improviso).

## O que ERROU (não repetir)

**Cortar pelo silêncio puro.** Silêncio não é fronteira de roteiro: o professor
tosse, pausa, respira, improvisa. A primeira tentativa cortou pelas maiores pausas
e errou as fronteiras feio.

**`whisper.cpp` com `-ml 1` para timestamp.** Ele interpola os tempos de palavra
linearmente em vez de medir. Errou a borda de uma seção em **4s** e outra em **11s**.
Foi descartado para timestamping. (O modelo `ggml-large-v3.bin` em `~/.whisper-models/`
pode ficar para outros usos — só não para cravar tempo de palavra.)

## O que ACERTOU (o método)

A fronteira de uma seção é uma **frase** (a âncora), não um silêncio. O método casa
três fontes:

1. **Roteiro** — define *quais* seções existem e a frase-âncora de início e de fim de
   cada uma. (`parse_roteiro.py`)
2. **WhisperX** (Whisper + alinhamento forçado wav2vec2) — dá timestamp **medido** por
   palavra (não interpolado). Localiza cada âncora no tempo e desambigua palavras
   repetidas. Acertou dentro de **~40ms** do áudio real. (`transcrever.py`)
3. **silencedetect** (ffmpeg) — crava o frame exato da transição silêncio↔fala ao
   redor da âncora, limpando respiração/tosse das bordas. (`achar_bordas.py`)

Depois `ffmpeg` recodifica preservando todas as specs do bruto. (`cortar.py`)

### Por que fuzzy match e não match exato

O falado ≠ roteiro. O professor improvisa, troca palavras, repete. A âncora é casada
por **similaridade** (janela deslizante + `SequenceMatcher`), não por igualdade.

### Múltiplas tomadas

Quando a âncora de início casa em vários pontos (regravações), pega-se a **última
tomada completa** — o último início que tenha um fim correspondente depois dele.
Tomada truncada (início sem fim posterior) é descartada. O número de tomadas é logado.

### As bordas (aprovadas pelo Arno)

- **0.15s de respiro antes** da primeira palavra.
- **0.30s depois** da última palavra.
- Em seção que começa no meio de fala contínua, o início recua para o silêncio limpo
  mais próximo **antes** da âncora (`silence_end` ≤ início da fala).

### Por que recodificar (e não copy-codec)

Corte ao frame exato em HEVC exige reencode; `-c copy` só cortaria em keyframe (erro de
até ~1-2s na borda). Recodifica-se em `libx265 -crf 18 -preset medium`, preservando
pix_fmt, fps e specs de áudio lidas com `ffprobe`. Mapeia só vídeo+áudio (`-map 0:v:0
-map 0:a:0`), descartando streams de dados/timecode.

## Números de referência da sessão (teste de regressão)

Cortes validados na pasta `TESTE GURGEL VAV19/`:

| Vídeo | Seção | Duração |
|---|---|---|
| VAV19 | GANCHO | ~17.2s |
| VAV19 | DESENVOLVIMENTO | ~71.1s |
| VAV23 | GANCHO | ~17.2s |
| VAV23 | DESENVOLVIMENTO | ~63.2s |

Ao rodar a skill nessa pasta, as bordas devem reproduzir esses valores dentro de ±0.1s.

## Dependências

- **ffmpeg / ffprobe** (Homebrew, `/opt/homebrew/bin`).
- **WhisperX** em venv isolado por projeto (uv), modelo `large-v3` + alinhamento `pt`,
  `--device cpu --compute_type int8` (estável em Apple Silicon).
- O modelo é baixado pelo WhisperX na 1ª transcrição; o JSON por vídeo é cacheado
  (`transcrever.py`) por nome+tamanho+mtime e reusado em re-execuções.
