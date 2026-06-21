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
5. **Normaliza se preciso** (rede de segurança: o ideal é os cortes já chegarem
   normalizados da otimizadora) e **concatena** na ordem da cadeia por `-c copy`.
6. **Salva** em `COMBINAÇÕES/`, ex.: `GANCHO_VAV19__DESENVOLVIMENTO_VAV57__OFERTA_VAV19.<ext>`.

Saída padrão: Full HD vertical (1080×1920), 30fps, HEVC, MP4. Oferece 4K, MOV,
resolução nativa e H.264 como alternativas.

### `invisible-video-otimizador`

Deixa um vídeo gravado pronto pra uso, em três etapas (todas num reencode só):
**(1) escolhe a melhor take** quando o bruto tem várias tentativas da mesma fala —
transcreve com WhisperX, agrupa as repetições pelo texto e fica com a **última**;
**(2) remove os silêncios internos** sem comer palavra; **(3)** opcionalmente
**normaliza o formato** (resolução/fps/códec/áudio), entregando o corte pronto pra
concatenar. Aceita arquivo único ou pasta (lote). Invocada como `/invisible-video-otimizador`.

Dois eixos de modo independentes, cada um **conservador** (default, validado) ou **justo**:
**modo de silêncio** (o que conta como silêncio — conservador -35dB/0.3s, justo -33dB/0.15s)
e **modo de respiro** (margem nas bordas, assimétrica — conservador 0.10/0.25, justo
0.05/0.18). Preserva ataque e cauda da fala; só silêncios
internos; corte ao frame exato. Verifica o resultado com `silencedetect`. Salva em
`OTIMIZADOS/` com nome limpo: preserva toda a identificação (tipo, código, prefixo) e descarta só ruído de processo (`BRUTA`, `VERTICAL`, `RAW`...) + `_OTIMIZADO`. `DME_VAV23_VERTICAL_BRUTA_DESENVOLVIMENTO` → `DME_VAV23_DESENVOLVIMENTO_OTIMIZADO`. O porquê de cada número (e o critério
de seleção de takes) está em `skills/invisible-video-otimizador/referencia/METODO.md`.

A seleção de takes é **opcional e por arquivo** (só roda quando há repetição; o
original nunca é tocado, então corta sozinha pela última take e reporta o que
descartou). Com `--normalizar`, o corte de silêncio e a padronização viram **um
reencode só** (alvo default Full HD vertical; aceita 4K, MOV, H.264). É a ordem
preferível antes de combinar: cada corte é reencodado uma vez aqui, e a combinação
vira `concat -c copy`.

Precisa de **ffmpeg** sempre; a seleção de takes precisa de **WhisperX** (faz bootstrap).

### `invisible-trilha-aplicador`

Aplica **trilha sonora de fundo** num vídeo (ou pasta), **preservando a fala original** —
a trilha entra como segunda camada, bem abaixo da voz. Invocada como
`/invisible-trilha-aplicador`.

A chave é controlar o volume por **LUFS, não por "%"**: cada trilha vem masterizada num
nível diferente (medido num acervo real, ~9 dB entre a mais alta e a mais baixa), então
"8% de volume" é inconsistente entre trilhas. A skill normaliza **dois alvos absolutos**:
a fala por ganho linear a **-14 LUFS** (padrão Reels) e a trilha a **-37 LUFS** (~23 dB
abaixo da fala). Cada vídeo e cada trilha são medidos e recebem o ganho próprio que os leva
ao destino — o lote inteiro fica consistente.

Mix com `amix normalize=0` (não divide a fala), trilha com fade in/out de 1.5s e
`-stream_loop` (cobre vídeos mais longos que a trilha). Em lote, distribui as trilhas pelos
vídeos o mais igualmente possível (round-robin). Vídeo copiado sem recompressão (`-c:v
copy`); só o áudio é remixado (AAC 192k). Saída em `99_FINALIZADOS/<nome>_FINALIZADO.mp4`,
sem tocar no original. O nível da trilha é **um número** (`--alvo-trilha`): sobe pra -34
(mais presente), desce pra -40 (mais discreta).

Precisa só de **ffmpeg** (faz bootstrap). Método e calibração em
`skills/invisible-trilha-aplicador/referencia/METODO.md`.

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
    scripts/   (bootstrap, transcrever, selecionar_takes, otimizar)
    referencia/METODO.md
  skills/invisible-trilha-aplicador/
    SKILL.md
    scripts/   (bootstrap, aplicar)
    referencia/METODO.md
```

`bootstrap.py` e `transcrever.py` são copiados em cada skill que precisa deles, para
que cada skill fique autocontida.
