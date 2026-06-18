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
```
