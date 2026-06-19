# invisible-video-system

Sistema de vídeo da Invisible para o Claude Code. Plugin do marketplace `invisible-skills`.

## Skills

### `invisible-video-bruto-desmembrador`

Desmembra vídeos brutos de aula em **um corte por seção do roteiro** (gancho,
desenvolvimento, CTA...). Invocada como `/invisible-video-bruto-desmembrador`.

A fronteira de uma seção é uma **frase**, não um silêncio. O pipeline:

1. **Descobre** os pares vídeo+roteiro na pasta (por prefixo de nome).
2. **Lê o roteiro** e detecta as seções + as frases-âncora de início e fim.
3. **Transcreve** cada bruta com **WhisperX** (timestamp medido por palavra, com cache).
4. **Acha as bordas** casando roteiro × transcrição × silêncio (âncora fuzzy, última
   tomada completa, respiro de 0.15s antes / 0.30s depois, refino no silêncio limpo).
5. **Recodifica** cada seção preservando as specs do bruto (codec, pix_fmt, fps, áudio).
6. **Salva** em pasta no plural: `GANCHOS/`, `DESENVOLVIMENTOS/`, `CTAS/`.

Pausa para confirmação nos pontos certos: pares, seções e timestamps passam pelo usuário
antes do corte.

#### Dependências

- **ffmpeg / ffprobe** (Homebrew)
- **WhisperX** em venv isolado por projeto (uv), modelo `large-v3` + alinhamento `pt`

A skill faz **bootstrap**: detecta o que falta e instala, sem refazer o que já existe.

#### Por que WhisperX e não whisper.cpp

`whisper.cpp -ml 1` interpola os tempos de palavra e erra a borda em segundos. WhisperX
mede (wav2vec2) e acerta dentro de ~40ms. Detalhe em
`skills/invisible-video-bruto-desmembrador/referencia/METODO.md`.

### `invisible-video-combinador`

Combina **ganchos × desenvolvimentos** (cortes que o desmembrador produziu) para
gerar anúncios novos — mas só os cruzamentos que fazem **sentido retórico**.
Invocada como `/invisible-video-combinador`.

1. **Descobre** os cortes em `GANCHOS/` e `DESENVOLVIMENTOS/`.
2. **Transcreve** cada corte com WhisperX (com cache; aqui só importa o texto).
3. **Analisa a matriz** N×M: casa o que o gancho **promete** com o **tipo de abertura**
   do desenvolvimento (dor, revelação, contestação, depoimento) — nunca pela forma
   gramatical. Apresenta tabela ✅/⚠️/❌ justificada e **espera aprovação**.
4. **Normaliza** cada corte para um alvo comum (`scale+pad+setsar=1`) e **concatena**
   por `-c copy` (specs mistas quebrariam o concat sem isso).
5. **Salva** em `COMBINAÇÕES/` como `GANCHO_VAV<xx>__DESENVOLVIMENTO_VAV<yy>.<ext>`.

Saída padrão: Full HD vertical (1080×1920), 30fps, HEVC, MP4. Oferece 4K, MOV,
resolução nativa e H.264 como alternativas.

### `invisible-video-otimizador`

Remove os **silêncios internos** de um vídeo montado **sem comer palavra**, deixando
o ritmo enxuto. Aceita arquivo único ou pasta (lote). Invocada como
`/invisible-video-otimizador`.

Critério validado: silêncio = trecho >0.5s abaixo de **-35dB**; **respiro assimétrico**
de 0.10s na entrada e 0.25s na saída (preserva ataque e cauda da fala); só silêncios
internos; corte ao frame exato. Verifica o resultado com `silencedetect`. Salva em
`OTIMIZADOS/` como `<nome>__OTIMIZADO.<ext>`. O porquê de cada número está em
`skills/invisible-video-otimizador/referencia/METODO.md`.

Só precisa de **ffmpeg** (não usa WhisperX).

## Estrutura

```
video/invisible-video-system/
  README.md
  CLAUDE.md
  .claude-plugin/plugin.json
  skills/invisible-video-bruto-desmembrador/
    SKILL.md
    scripts/   (bootstrap, descobrir_pares, parse_roteiro, transcrever, achar_bordas, cortar, pipeline)
    referencia/METODO.md
  skills/invisible-video-combinador/
    SKILL.md
    scripts/   (bootstrap, transcrever, descobrir_cortes, normalizar, combinar)
    referencia/METODO.md
  skills/invisible-video-otimizador/
    SKILL.md
    scripts/   (bootstrap, otimizar)
    referencia/METODO.md
```

`bootstrap.py` e `transcrever.py` são copiados em cada skill que precisa deles, para
que cada skill fique autocontida.
