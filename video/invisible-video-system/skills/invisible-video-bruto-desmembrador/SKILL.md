---
name: invisible-video-bruto-desmembrador
description: >
  Desmembra vídeos brutos de aula em um corte por seção do roteiro (gancho,
  desenvolvimento, CTA...). Acha os pares vídeo+roteiro na pasta, lê o roteiro e
  detecta as seções, transcreve cada bruta com WhisperX (timestamp medido por
  palavra, com cache), casa roteiro × transcrição × silêncio para achar as bordas
  precisas de cada seção, recodifica preservando as specs do bruto e salva cada
  seção numa pasta com o nome no plural (GANCHOS/, DESENVOLVIMENTOS/, CTAS/). Use
  SEMPRE que o usuário pedir para "cortar a bruta por seção", "desmembrar o vídeo
  pelo roteiro", "separar gancho e desenvolvimento", "picar a aula em cortes",
  "extrair as seções do roteiro do vídeo", ou tiver brutas + roteiros e quiser um
  vídeo por seção. Requer ffmpeg e WhisperX (a skill faz bootstrap).
---

# invisible-video-bruto-desmembrador

Você desmembra vídeos brutos em cortes por seção do roteiro. O método foi validado
numa sessão real e está em [referencia/METODO.md](referencia/METODO.md) — **leia-o
antes de começar**, sobretudo o que foi descartado (silêncio puro e `whisper.cpp`
para timestamp) para não reintroduzir.

A regra de ouro: a fronteira de uma seção é uma **frase-âncora**, não um silêncio.
WhisperX localiza a âncora no tempo (timestamp medido por palavra), o `silencedetect`
limpa a borda, o ffmpeg recodifica preservando as specs.

Os scripts vivem em `scripts/` (ao lado deste arquivo). Cada um imprime JSON e para;
**você** conduz as confirmações entre as etapas. Caminho dos scripts a partir desta
skill: `scripts/<nome>.py`.

---

## Pré-requisito: bootstrap

Antes de tudo, garanta as dependências. Rode:

```
python3 scripts/bootstrap.py --venv <pasta_projeto>/.transcricao/.wxenv --check-only
```

Se `pronto` for `false`, rode sem `--check-only` para instalar o que falta (ffmpeg via
brew; venv + WhisperX via uv). Siga as `instrucoes` que vierem no JSON se algo não puder
ser instalado automaticamente. O venv do WhisperX é **por projeto**, em
`.transcricao/.wxenv` dentro da pasta do projeto.

**Modelo já baixado?** O JSON traz `modelo_pronto` e o bloco `modelo` (com `asr` e
`alinhamento_pt`). Se `modelo_pronto: true`, o usuário **já tem** o modelo no cache do
Hugging Face — **não avise sobre download nem demora de baixar** na transcrição. Só se
`modelo_pronto: false` é que a 1ª transcrição baixa (~1.5GB o ASR) — aí sim avise. O
WhisperX usa o cache HF padrão automaticamente; não há o que configurar quando o modelo
já existe.

---

## O fluxo (com pontos de confirmação)

### 1. Descobrir os pares — `descobrir_pares.py`

```
python3 scripts/descobrir_pares.py <pasta_projeto>
```

Pareia vídeos e roteiros por prefixo comum de nome (tolerante a sufixos ROTEIRO /
VERTICAL / BRUTA). Procura vídeos também na subpasta `BRUTAS/`.

**PARE e confirme com o usuário** os pares encontrados. Avise de órfãos (vídeo sem
roteiro ou vice-versa). Só siga após o ok.

### 2. Parse do roteiro — `parse_roteiro.py`

```
python3 scripts/parse_roteiro.py <roteiro.md>
```

Detecta os headers de seção (linha isolada, `[COLCHETES]` e/ou `**negrito**`,
majoritariamente MAIÚSCULA). Ignora marcação de palco (colchetes no meio de
parágrafo). Para cada seção devolve nome, plural (pasta de saída), âncora de início e
âncora de fim.

**PARE e confirme** a lista de seções por vídeo (quantidade e nomes). Permita ajuste
manual — se o usuário corrigir, edite o JSON de seções antes de seguir. Salve o JSON
confirmado em `<pasta_projeto>/.transcricao/<prefixo>.secoes.json`.

### 3. Transcrever com cache — `transcrever.py`

```
python3 scripts/transcrever.py <video> \
  --venv <pasta_projeto>/.transcricao/.wxenv \
  --cache-dir <pasta_projeto>/.transcricao/wx_out
```

Extrai áudio mono 16k e roda WhisperX (`large-v3`, `pt`, `cpu`, `int8`). Cacheia o JSON
por nome+tamanho+mtime; em re-execução com o mesmo arquivo, não re-transcreve
(`"cacheado": true`). Se o bootstrap reportou `modelo_pronto: false`, a 1ª transcrição
baixa o modelo e demora — avise. Se `modelo_pronto: true`, não há download; é só o tempo
de transcrição em si (CPU).

### 4. Achar as bordas — `achar_bordas.py` (o coração)

```
python3 scripts/achar_bordas.py <video> <transcricao.json> <secoes.json>
```

Localiza as âncoras por similaridade fuzzy, desambigua tomadas (pega a **última
completa**, loga quantas havia), refina as bordas com silêncio e aplica os respiros
(0.15s antes, 0.30s depois). Devolve `(seção, ss, to, dur, n_tomadas, conf)`.

**PARE e mostre** os timestamps e durações por seção antes de cortar. Compare com a
expectativa do usuário. Se alguma seção vier com `erro` (âncora não localizada),
mostre e peça uma âncora melhor (ajuste o secoes.json) — não corte essa seção no
escuro. Se a confiança (`conf`) de uma seção for baixa, sinalize.

### 5. Cortar preservando specs — `cortar.py`

```
python3 scripts/cortar.py <video> <cortes.json> --out-base <pasta_projeto>
```

Lê as specs com ffprobe e recodifica cada seção (`libx265 -crf 18 -preset medium`,
preservando pix_fmt/fps/áudio), mapeando só v+a. Cria as pastas plural (GANCHOS/,
DESENVOLVIMENTOS/, CTAS/) e salva `<nome_bruto>__<SECAO>.<ext>`.

### 6. Fechamento

Mostre o resumo: quais arquivos foram gerados, em que pastas, com que durações. Avise
de qualquer seção pulada e por quê. Avise quantas tomadas havia quando > 1.

---

## Atalho

`pipeline.py` expõe as mesmas etapas como subcomandos (`descobrir`, `parse`,
`transcrever`, `bordas`, `cortar`) chamando os scripts individuais. Use-o ou chame os
scripts direto — tanto faz.

---

## Parâmetros (defaults validados — não mude sem motivo)

- `--respiro-inicio 0.15`, `--respiro-fim 0.30`
- `--silence-noise -30` (dB), `--silence-min 0.4` (s)
- `--crf 18`, `--preset medium`
- modelo `large-v3`, idioma `pt`

---

## Guardrails (não negociáveis)

- **Fronteira é frase, não silêncio.** Nunca corte por pausa pura.
- **WhisperX para timestamp, nunca whisper.cpp `-ml 1`** (interpola e erra segundos —
  ver METODO.md).
- **Recodificar, não copy-codec** — corte ao frame exato exige reencode.
- **Preservar specs** do bruto (codec, pix_fmt, fps, áudio) lidas com ffprobe.
- **Confirme antes de cortar.** Pares, seções e timestamps passam pelo usuário.
- **Última tomada completa** quando houver regravação; logar as demais.
- **Pasta no plural**, arquivo `<bruto>__<SECAO>.<ext>`.
- **Não invente conteúdo.** Âncora que não casa → peça âncora melhor, não chute o corte.
