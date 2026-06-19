# Método — Otimizador (remoção de silêncios internos)

Critério fechado em três iterações com o Arno numa sessão real. Os números são validados — não mexa sem motivo. Editou aqui, mudou o comportamento da skill.

## 1. Detecção de silêncio: -35dB, 0.5s

`silencedetect=noise=-35dB:d=0.5` — silêncio = trecho **> 0.5s** abaixo de **-35dB**.

### Por que -35dB e não -30
A -30dB, a palavra final dita baixo caía como silêncio e era cortada. O professor naturalmente faz um **decrescendo** no fim da frase — a última sílaba sai fraca. A -30 esse final fraco é confundido com silêncio. **-35dB trata fala fraca como fala**, preservando o fim da frase. Mais permissivo que isso (ex.: -40) começa a deixar passar pausa real como se fosse fala.

### Por que 0.5s de duração mínima
Abaixo de 0.5s a "pausa" é respiração e ritmo natural — cortar isso deixa o vídeo afobado e robótico. 0.5s isola só as pausas mortas de verdade.

## 2. Respiro assimétrico: 0.10s entrada, 0.25s saída

Ao reconstruir os trechos de fala, cada um ganha uma margem (respiro) nas bordas para não cortar a palavra. A margem é **assimétrica de propósito**:

- **Entrada 0.10s** (antes de o trecho de fala começar, após `silence_end`): início de palavra tem **ataque alto e abrupto** — 0.10s já segura o começo.
- **Saída 0.25s** (depois de o trecho terminar, em `silence_start`): fim de palavra **decai suave** — a cauda baixa de um "S", de uma vogal átona, do decrescendo final. Precisa de mais margem ou come a consoante final.

### Por que NÃO simétrico
Respiro simétrico (mesmo valor dos dois lados) ou come a consoante final (se igualar pelo lado curto) ou deixa pausa demais no começo (se igualar pelo lado longo). A assimetria é o que dá ritmo enxuto **sem** mutilar palavra.

## 3. Só silêncios internos

Começo e fim do vídeo ficam **intactos**. Um silêncio que vai até o fim do vídeo (sem `silence_end`) é ignorado — não é pausa interna. O complemento dos silêncios internos = os segmentos a manter.

## 4. Corte ao frame exato

`trim`/`atrim` + `setpts`/`asetpts` + `concat` via `filter_complex`, num único reencode. HEVC (libx265 CRF20, `-tag:v hvc1`), AAC 48k stereo, preservando pix_fmt e fps do original (lidos por ffprobe). Reencode (não copy) porque corte ao frame exato em HEVC exige reencode — copy só cortaria em keyframe.

## 5. Verificação automática

Roda `silencedetect` de novo no resultado. **Não pode sobrar silêncio interno > 0.5s.**

Pausas residuais ~0.35–0.49s são **esperadas, não erro**: são o respiro preservado. O silencedetect mede a partir do cruzamento do limiar (-35dB), não da última sílaba audível — então o respiro de 0.25s + a cauda já abaixo do limiar somam uma "pausa" medida que não chega aos 0.5s de corte. Só investigue se sobrarem pausas **longas** reais.

## 6. Parâmetros (defaults, ajustáveis por argumento)
- `silence_noise = -35dB`, `silence_min = 0.5s`
- `respiro_entrada = 0.10s`, `respiro_saida = 0.25s`
- `crf = 20`, `preset = medium`
