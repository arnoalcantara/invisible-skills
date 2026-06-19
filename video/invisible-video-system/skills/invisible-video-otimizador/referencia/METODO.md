# Método — Otimizador (takes + remoção de silêncios internos)

Critério fechado em três iterações com o Arno numa sessão real. Os números são validados — não mexa sem motivo. Editou aqui, mudou o comportamento da skill.

## 0. Seleção de takes (quando o bruto tem várias tentativas)

Um gancho gravado bruto costuma ter **várias tentativas da mesma fala** — a pessoa erra no meio, volta, repete. Antes de cortar silêncio, a skill escolhe a take boa. O critério, fechado com o Arno: **vence sempre a última take** (a pessoa repete até acertar; a última tende a ser a definitiva).

### Como detecta sem o usuário informar a frase
Decisão de design: a skill **não pede** o texto esperado. Ela transcreve com WhisperX e deduz as repetições pelo próprio texto:

1. **Blocos de fala.** As palavras (com timestamp medido por palavra) são quebradas em blocos sempre que há uma pausa `≥ --gap` (0.6s default). Uma respirada longa marca o fim de uma tentativa e o começo de outra.
2. **Agrupamento por similaridade.** Blocos cujo texto normalizado (minúsculas, sem acento/pontuação) tem similaridade `≥ --sim` (0.75 default, via `difflib.SequenceMatcher`) são a mesma fala repetida. O agrupamento é transitivo (A~B, B~C ⇒ mesmo grupo).
3. **Última vence.** Em cada grupo com ≥2 takes, mantém o de maior timestamp; os anteriores entram na lista de descarte.

`--min-palavras` (4 default) protege blocos curtos: um "é..." ou "então" solto nunca é descartado, mesmo que se pareça com outro.

### Por que age sozinha (e mesmo assim é seguro)
O original **nunca é alterado** — a saída vai pra `OTIMIZADOS/`. Descartar a take errada não destrói nada: o bruto continua lá. Por isso a skill corta sozinha pela última take e só **reporta** no resumo o que descartou (texto + timestamp), em vez de travar pedindo confirmação a cada take.

### Por que fica no mesmo reencode do silêncio
Os intervalos de descarte são **subtraídos dos segmentos a manter** antes de montar o `filter_complex`. Assim o corte de take, o corte de silêncio e a normalização opcional acontecem num único reencode — zero geração extra, mesma filosofia da normalização fundida (seção 4).

### Limites conhecidos
- **Por arquivo.** Cada vídeo tem seus próprios intervalos; não roda em lote (`--descartar` vale só pra arquivo único).
- **Ganchos com repetição legítima.** Se a fala genuinamente repete uma frase (ênfase retórica), os parâmetros `--gap`/`--sim` podem agrupar errado. O relatório existe pra pegar isso a olho.

## 1. Detecção de silêncio (modos conservador -35dB/0.3s e justo -33dB/0.15s)

`silencedetect=noise=<X>dB:d=<T>` — silêncio = trecho **≥ T** abaixo de **X dB**. O `d` é a duração **mínima** pra contar como silêncio: pausa de T+ entra pro corte; pausa menor fica intacta. Os dois números viram um **preset escolhido na hora** (`--modo-silencio`), independente do modo de respiro:

- **`conservador`** (default): **-35dB / 0.3s**. O critério validado.
- **`justo`**: **-33dB / 0.15s**. Limiar mais alto = mais coisa cai como silêncio; duração menor = corta pausas mais curtas. Mais agressivo, com risco de raspar fala fraca (vale o aviso ao usuário).

### Por que -35dB e não -30 (no conservador)
A -30dB, a palavra final dita baixo caía como silêncio e era cortada. O professor naturalmente faz um **decrescendo** no fim da frase — a última sílaba sai fraca. A -30 esse final fraco é confundido com silêncio. **-35dB trata fala fraca como fala**, preservando o fim da frase. Mais permissivo que isso (ex.: -40) começa a deixar passar pausa real como se fosse fala. O modo `justo` aceita -33 (um passo na direção do agressivo) porque troca esse risco por ritmo mais seco — escolha do usuário, não default.

### Por que 0.3s de duração mínima (no conservador)
Começou em 0.5s. Apertado para **0.3s** (jun/2026): 0.5s deixava passar pausas mortas curtas que arrastavam o ritmo; 0.3s isola mais pausa morta sem ainda comer a respiração natural da fala (que fica abaixo de 0.3s). Abaixo de 0.3s o corte começa a ficar afobado e robótico — por isso 0.15s é o modo `justo`, não o default.

## 2. Respiro assimétrico (modos conservador 0.10/0.25 e justo 0.05/0.18)

Ao reconstruir os trechos de fala, cada um ganha uma margem (respiro) nas bordas para não cortar a palavra. A margem é **assimétrica de propósito**:

- **Entrada 0.10s** (antes de o trecho de fala começar, após `silence_end`): início de palavra tem **ataque alto e abrupto** — 0.10s já segura o começo.
- **Saída 0.25s** (depois de o trecho terminar, em `silence_start`): fim de palavra **decai suave** — a cauda baixa de um "S", de uma vogal átona, do decrescendo final. Precisa de mais margem ou come a consoante final.

### Dois modos: conservador e justo
O respiro vira um **preset escolhido na hora** (`--modo-respiro`), não um número fixo:

- **`conservador`** (default) — 0.10s entrada / 0.25s saída. Os números validados acima, com folga: prioriza não mutilar palavra, ao custo de deixar respiros um pouco mais longos.
- **`justo`** — 0.05s entrada / 0.18s saída. Aperta as duas pontas para um ritmo mais seco, quando o usuário aceita o risco de cortes mais rentes. Continua **assimétrico** (saída > entrada) pela mesma razão física: o fim da palavra decai suave e precisa de mais margem que o início.

A assimetria é mantida nos dois modos; o que muda é o aperto global. `--respiro-entrada`/`--respiro-saida` ainda existem para sobrepor ponta a ponta quando o usuário quer um valor específico.

### Por que NÃO simétrico
Respiro simétrico (mesmo valor dos dois lados) ou come a consoante final (se igualar pelo lado curto) ou deixa pausa demais no começo (se igualar pelo lado longo). A assimetria é o que dá ritmo enxuto **sem** mutilar palavra — e por isso ambos os modos a preservam.

## 3. Só silêncios internos

Começo e fim do vídeo ficam **intactos**. Um silêncio que vai até o fim do vídeo (sem `silence_end`) é ignorado — não é pausa interna. O complemento dos silêncios internos = os segmentos a manter.

## 4. Corte ao frame exato (+ normalização opcional no mesmo passo)

`trim`/`atrim` + `setpts`/`asetpts` + `concat` via `filter_complex`, num único reencode. Reencode (não copy) porque corte ao frame exato em HEVC exige reencode — copy só cortaria em keyframe.

Por padrão **preserva as specs do original** (pix_fmt, fps, códec, áudio lidos por ffprobe). Com `--normalizar`, no **mesmo reencode** aplica também `scale+pad+setsar=1` no ramo de vídeo e força códec/fps/áudio do alvo (default FHD vertical: 1080×1920, 30fps, libx265 CRF20 `-tag:v hvc1`, AAC 48k stereo, `.mp4`). A escolha de fundir corte+normalização num passo só existe pra **não pagar duas gerações de reencode**: se a normalização fosse uma etapa separada (como era no combinador), o corte seria reencodado e depois reencodado de novo pra padronizar. Juntando, é uma geração só — menos perda, e o corte sai pronto pra `concat -c copy`.

## 5. Verificação automática

Roda `silencedetect` de novo no resultado. **Não pode sobrar silêncio interno ≥ 0.3s.**

Pausas residuais ~0.3–0.49s são **esperadas, não erro**: são o respiro preservado. O silencedetect mede a partir do cruzamento do limiar (-35dB), não da última sílaba audível — então o respiro de 0.25s + a cauda já abaixo do limiar somam uma "pausa" medida. Só investigue se sobrarem pausas **longas** reais.

## 6. Parâmetros (defaults, ajustáveis por argumento)
- seleção de takes: **off** por padrão (só roda quando há repetição a resolver); `--gap 0.6`, `--sim 0.75`, `--min-palavras 4`.
- `modo_silencio = conservador` (-35dB / 0.3s) | `justo` (-33dB / 0.15s); `--silence-noise`/`--silence-min` sobrepõem cada um
- `modo_respiro = conservador` (0.10s / 0.25s) | `justo` (0.05s / 0.18s); `--respiro-entrada`/`--respiro-saida` sobrepõem ponta a ponta
- os dois eixos são **independentes** (qualquer combinação)
- `crf = 20`, `preset = medium`
- normalização: **off** por padrão; `--normalizar` liga, com alvo FHD vertical default.
