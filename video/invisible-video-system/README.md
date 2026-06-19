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

Concatena cortes de **N segmentos** (cortes que o desmembrador produziu) numa
**cadeia ordenada** para gerar peças novas — anúncios curtos ou VSLs. Invocada como
`/invisible-video-combinador`.

Os segmentos têm **nome livre** e podem ser **dois ou mais**. O padrão Invisible é
GANCHO, DESENVOLVIMENTO, CTA, mas pode ser LEAD, HISTORIA, OFERTA, FECHAMENTO — o que
o projeto tiver. Os cortes podem estar em **subpastas** (`GANCHOS/`, `DESENVOLVIMENTOS/`)
ou **soltos na mesma pasta**, distinguidos pelo rótulo no nome do arquivo (o nome
sempre carrega o rótulo da sessão e o código/número, em qualquer ordem); o descobridor
detecta os dois layouts sozinho. **Quem dirige é o usuário:** ele diz quais segmentos
entram, em que ordem, quais **variam** (cruzam) e quais ficam **fixos/nativos** (o
corte de mesmo código de origem acompanha, sem cruzar).

1. **Descobre** os segmentos: toda subpasta com vídeo vira um segmento candidato
   (sugere a ordem retórica dos nomes conhecidos). Ou recebe `--segmentos` na ordem.
2. **Pergunta o esquema**: quais segmentos, ordem, o que varia × o que é nativo.
3. **Transcreve** os cortes dos segmentos que variam (com cache; só o texto importa).
4. **Julga par-a-par** cada transição variável: casa o que a peça anterior **promete**
   com o **tipo de abertura** da seguinte — nunca pela forma gramatical. Tabela
   ✅/⚠️/❌ justificada e **espera aprovação**.
5. **Normaliza** cada corte para um alvo comum (`scale+pad+setsar=1`) e **concatena**
   na ordem da cadeia por `-c copy` (specs mistas quebrariam o concat sem isso).
6. **Salva** em `COMBINAÇÕES/`, ex.: `GANCHO_VAV19__DESENVOLVIMENTO_VAV57__OFERTA_VAV19.<ext>`.

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
