---
name: invisible-video-otimizador
description: >
  Pega um vídeo gravado e o deixa pronto: primeiro escolhe a melhor TAKE quando há várias tentativas da mesma fala (transcreve, agrupa as repetições e fica com a última), depois remove os silêncios internos sem comer palavra, e — opcionalmente — NORMALIZA o formato (resolução/fps/códec/áudio) no mesmo passo, entregando o corte pronto pra concatenar. Dois eixos de modo independentes, cada um conservador (default, validado) ou justo: modo de silêncio (o que conta como silêncio — conservador -35dB/0.3s, justo -33dB/0.15s) e modo de respiro (margem nas bordas — conservador 0.10/0.25, justo 0.05/0.18, sempre assimétrico). Só silêncios internos, começo e fim intactos; corte ao frame exato. Gera também, na mesma pasta, a versão QUADRADA (1:1) de cada otimizado (sufixo _QUADRADO), reenquadrando o vertical por detecção de rosto (YuNet) ancorada nos olhos — para o feed do Instagram, em paralelo ao vertical pela esteira. Aceita um arquivo único OU uma pasta inteira (lote). Use quando o usuário pedir "otimiza o vídeo", "tira os silêncios", "enxuga o ritmo", "remove as pausas", "corte mais justo/seco", "escolhe a melhor take", "esse gancho tem várias tentativas", "limpa as repetições", "otimiza essa pasta de vídeos", "padroniza esses vídeos", "faz a versão quadrada". Saída em OTIMIZADOS/. Requer ffmpeg; a seleção de takes requer WhisperX e o quadrado requer OpenCV (faz bootstrap).
---

# Otimizador de Vídeo (takes + silêncios + normalização)

Você pega um vídeo gravado e o deixa pronto para uso. São três coisas, nessa ordem:

1. **Seleção de takes** (opcional, quando o vídeo tem repetições): um gancho gravado bruto costuma ter várias tentativas da mesma fala — a pessoa erra no meio, volta, repete. Você transcreve, identifica as takes da mesma frase e fica com a **última** (o critério é sempre a última take), descartando as anteriores. Se não houver repetição, segue direto.
2. **Corte de silêncios internos** sem comer palavra, deixando o ritmo enxuto.
3. **Normalização de formato** (opcional): resolução, fps, códec, áudio — no mesmo reencode, entregando o corte já padronizado e pronto pra concatenar.

O original **nunca é tocado** — tudo sai em `OTIMIZADOS/`. O critério de silêncio foi afinado em iterações numa sessão real até ficar perfeito — está fechado, não reinvente os números sem motivo.

## Critério de corte — dois eixos de modo (conservador/justo)

São **dois presets independentes**, cada um com modo `conservador` (default, validado) e `justo` (mais agressivo). **Não se acoplam** — o usuário pode pôr um em justo e o outro em conservador.

**1. Modo de silêncio** (`--modo-silencio`) — o que conta como silêncio cortável:
- **`conservador` (default):** silêncio = trecho **≥ 0.3s abaixo de -35dB**. O `d` do `silencedetect` é a duração mínima; pausa de 0.3s+ é cortada, menor fica intacta. **-35dB e não -30:** a -30 a palavra final dita baixo (decrescendo natural no fim da frase) caía como silêncio. -35 trata fala fraca como fala.
- **`justo`:** **-33dB / 0.15s**. Limiar mais alto pega mais coisa como silêncio; duração menor corta pausas mais curtas. Ritmo mais seco, com algum risco de raspar fala fraca.

**2. Modo de respiro** (`--modo-respiro`) — a margem deixada nas bordas da fala (assimétrica: saída > entrada, porque o fim da palavra decai suave e o início tem ataque alto):
- **`conservador` (default, validado):** 0.10s entrada / 0.25s saída. Preserva ataque e cauda com folga.
- **`justo`:** 0.05s entrada / 0.18s saída. Mais apertado nas duas pontas.
- **Respiro simétrico come consoante final — nenhum modo usa.**

- **Só silêncios internos.** Começo e fim do vídeo ficam intactos (em qualquer modo).
- **Corte ao frame exato** via `trim/atrim + setpts/asetpts + concat`.

## Fluxo de execução

### Fase 0 — Bootstrap
`python3 scripts/bootstrap.py --check-only`. O **ffmpeg** é sempre necessário (corte de silêncio/normalização). O **WhisperX** só é necessário se você for selecionar takes — confira `whisperx: true` no JSON apenas nesse caso. O **OpenCV** (`opencv: true`, com `python_cv2` apontando o python da venv) é necessário pra gerar o quadrado — o bootstrap instala o `opencv-python-headless` na venv central. Se o usuário só quer enxugar silêncio/normalizar, ignore whisperx e opencv. Se faltar dependência, rode sem `--check-only` (instala) ou `brew install ffmpeg`. Se o JSON avisar que o modelo de transcrição não está em cache, avise o usuário do download (~1.5GB) **antes** de transcrever. (O modelo do YuNet, ~230KB, já vem versionado em `referencia/modelos/` — sem download.)

### Fase 1 — Seleção de takes (só quando há repetições)
Pergunte (ou deduza do pedido) se o vídeo tem **várias tentativas da mesma fala**. Vale **só para arquivo único** — em lote, cada vídeo teria seus próprios intervalos, então a seleção de takes não roda em pasta.

Se o vídeo for uma fala única e limpa, **pule esta fase** e vá direto ao corte de silêncio. A transcrição só entra quando há repetição a resolver.

Quando há takes a resolver:

1. **Transcreva** com WhisperX (timestamp medido por palavra, não interpolado):
   ```bash
   python3 scripts/transcrever.py "<video>" \
     --whisperx-bin "<whisperx_bin do bootstrap>" \
     --cache-dir "<pasta do video>/.transcricao/wx_out"
   ```
   Pegue o `json_path` da saída.

2. **Selecione as takes** — agrupa blocos de fala com texto parecido e marca o que descartar (mantém a última de cada grupo):
   ```bash
   python3 scripts/selecionar_takes.py "<json_path>" --gap 0.6 --sim 0.75
   ```
   - `--gap 0.6` — pausa que separa uma take da outra (uma respirada longa marca o recomeço da fala).
   - `--sim 0.75` — quão parecido o texto precisa ser pra contar como a mesma fala (0–1).
   - `--min-palavras 4` — blocos curtos (um "é..." solto) nunca são descartados.

   A saída traz `descartar` (lista de intervalos `[ini, fim]`) e um `relatorio` legível (cada take, com texto e timestamp, marcada `manter` ou `descartar`).

3. **Mostre o relatório ao usuário** no resumo final: quais takes foram descartadas (texto + tempo) e qual ficou. Você age sozinho (o original não é tocado — nada se perde de verdade), mas deixa auditável o que cortou.

4. Monte a string de descartes pra passar ao `otimizar.py`: `"ini-fim,ini-fim"` a partir do campo `descartar`. Ex.: `descartar [[0.0,1.7],[3.0,5.05]]` → `--descartar "0.0-1.7,3.0-5.05"`.

Se `n_grupos_repetidos` for 0, não há repetição — siga sem `--descartar`.

### Fase 2 — Decidir o formato de saída (normalizar ou preservar)
Pergunte ao usuário se quer **normalizar** o formato no mesmo passo (recomendado quando os vídeos vão ser combinados depois, ou quando vêm com specs mistas):

- **Preservar specs do original** (default quando o usuário só quer enxugar o ritmo) — não passa `--normalizar`. Cada vídeo sai no mesmo formato em que entrou.
- **Normalizar para um alvo comum** — passa `--normalizar`. O alvo padrão é **Full HD vertical**: 1080×1920, 30fps, HEVC (libx265 CRF20, `-tag:v hvc1`), AAC 48kHz stereo, `.mp4`. Ofereça as alternativas e deixe o FHD/MP4 como default:
  - **4K** vertical: `--largura 2160 --altura 3840`
  - **MOV**: `--container mov`
  - **H.264**: `--vcodec libx264`
  - outra resolução/fps/áudio conforme o pedido.

A normalização usa `scale+pad+setsar=1` (encaixa preservando proporção, barras se preciso) — cobre entrada que não seja 9:16 sem distorcer.

### Fase 2.5 — Escolher os modos (silêncio e respiro)
Dois presets **independentes**, cada um conservador (default) ou justo. Pergunte (ou deduza do pedido); na dúvida, deixe os dois em `conservador`.

- **Modo de silêncio** (`--modo-silencio`): `conservador` (-35dB / 0.3s) ou `justo` (-33dB / 0.15s — pega mais silêncio e pausas mais curtas).
- **Modo de respiro** (`--modo-respiro`): `conservador` (0.10/0.25) ou `justo` (0.05/0.18 — bordas mais rentes).

Pode misturar (ex.: silêncio justo + respiro conservador). Quando o usuário pedir genericamente "corte mais seco/apertado/justo", o natural é pôr **os dois** em justo — confirme se ele quer um ou ambos. Override fino só se pedir número específico: `--silence-noise`/`--silence-min` e `--respiro-entrada`/`--respiro-saida` sobrepõem o preset correspondente.

### Fase 3 — Otimizar
Tudo num reencode só (descarte de take + corte de silêncio + normalização opcional).

Caso simples (sem takes, preservando specs):
```bash
python3 scripts/otimizar.py "<arquivo_ou_pasta>"
```
Com descarte de takes (vindo da Fase 1):
```bash
python3 scripts/otimizar.py "<video>" --descartar "0.0-1.7,3.0-5.05"
```
Corte mais seco (os dois eixos em justo):
```bash
python3 scripts/otimizar.py "<arquivo_ou_pasta>" --modo-silencio justo --modo-respiro justo
```
Só o silêncio mais agressivo, respiro com folga:
```bash
python3 scripts/otimizar.py "<arquivo_ou_pasta>" --modo-silencio justo
```
Otimizando **e** normalizando (FHD vertical default):
```bash
python3 scripts/otimizar.py "<arquivo_ou_pasta>" --normalizar
```
Tudo junto (takes + normalização 4K MOV H.264):
```bash
python3 scripts/otimizar.py "<video>" --descartar "0.0-1.7,3.0-5.05" --normalizar \
  --largura 2160 --altura 3840 --container mov --vcodec libx264
```
Defaults já embutidos: `--modo-silencio conservador` (-35dB / 0.3s), `--modo-respiro conservador` (0.10/0.25), `--crf 20`, `--preset medium`. Silêncio e respiro vêm dos respectivos `--modo-*`; só passe os overrides finos (`--silence-noise`/`--silence-min`, `--respiro-entrada`/`--respiro-saida`) se o usuário pedir um número específico — e avise que está saindo dos presets.

`--descartar` vale **só para arquivo único**; em lote o script o ignora e avisa. O descarte de take, o corte de silêncio e a normalização acontecem no **mesmo reencode** — sem geração extra.

### Fase 3.7 — Versão quadrada (1:1) para o feed
Depois de gerar os `_OTIMIZADO` (verticais), produza a versão **quadrada** de cada um, na **mesma pasta** `OTIMIZADOS/`. O quadrado caminha em paralelo ao vertical por toda a esteira (combinador, legendas, gancho-escrito, trilha) e sai junto no fim.

Rode com o **python da venv** (o que tem o OpenCV — campo `python_cv2` do bootstrap), apontando a pasta `OTIMIZADOS/`:
```bash
<python_cv2> scripts/quadrado.py "<.../OTIMIZADOS>" --contato
```

O que ele faz, por arquivo:
- Recorta um quadrado de **largura cheia** (lado = largura do vídeo; descarta só altura). O 1080×1920 vira 1080×1080.
- **Onde cortar é decidido por detecção de rosto (YuNet) ancorada nos OLHOS:** amostra ~8 frames, pega a mediana do y dos olhos e os põe a ~30% da altura do quadrado (respiro pra coroa da cabeça). Ancorar nos olhos (não no centro da caixa) é o que evita a barba puxar o crop pra baixo e cortar a cabeça.
- Sem rosto plausível → fallback de âncora alta segura (15% da folga).
- Áudio **idêntico** ao vertical (`-c:a copy`); só o vídeo é recortado/reencodado.
- **Não** gera `.md` pro quadrado: o roteiro é o mesmo da vertical (mesmo áudio) → um `.md` só por corte, o do vertical.

**Aprovação (folha de contato):** `--contato` gera `_CONTATO_QUADRADO.png` na pasta — uma grade com a miniatura de cada quadrado e o nome. Mostre ao usuário: o auto acerta a maioria; ele aprova em bloco e aponta os que ficaram tortos (o detector erra de vez em quando — mão na frente do rosto, cabeça muito virada).

**Nudge de um corte específico:** quando o usuário disser que um quadrado ficou alto/baixo demais, refaça **só aquele** com âncora manual (fração da folga, 0=topo, 0.5=centro, 1=base):
```bash
<python_cv2> scripts/quadrado.py "<.../OTIMIZADOS/DME_VAV19_GANCHO_OTIMIZADO.mp4>" --ancora 0.45
```

Pule esta fase só se o usuário disser explicitamente que **não** quer o quadrado (o padrão é sempre gerar os dois).

### Fase 4 — Ler a verificação
Cada resultado traz `verificacao`, `normalizado` e `takes_descartadas`:
- `silencios_residuais == 0` → ritmo limpo.
- Residuais **> 0** não são necessariamente erro: pausas ~0.3–0.49s são o **respiro preservado** (o silencedetect mede do cruzamento de limiar, não da última sílaba). Só investigue se sobrarem pausas longas reais.

Se um vídeo voltar com `aviso` de "nenhum silêncio interno detectado" e não houver takes a descartar, não há o que otimizar — informe e siga.

### Fase 5 — Resumo
Liste cada vídeo: nome de saída (`nome_saida`, já limpo — identificação preservada + `_OTIMIZADO`), os modos usados (`modo_silencio` + `silencio`, `modo_respiro` + `respiros`), takes descartadas (texto + tempo, se houve), silêncios cortados, segmentos mantidos, se foi normalizado (e pra qual alvo), e o caminho em `OTIMIZADOS/`.

## Saída
- Pasta `OTIMIZADOS/` ao lado da origem (ou `--out-dir`).
- Arquivo: nome **limpo** a partir do original + `_OTIMIZADO`. A regra é **preservar toda a identificação** (tipo, código, prefixo, número — na ordem original) e **descartar só os tokens de ruído de processamento**: `BRUTA`, `VERTICAL`, `HORIZONTAL`, `RAW`, `FINAL`, `OTIMIZADO`. Nada de tipo/código se perde. Exemplos:
  - `GANCHO_VAV19_BRUTA.mov` → `GANCHO_VAV19_OTIMIZADO.mov`
  - `DME__VAV23__VERTICAL__BRUTA__DESENVOLVIMENTO.mp4` → `DME_VAV23_DESENVOLVIMENTO_OTIMIZADO.mp4` (o `DESENVOLVIMENTO` **fica**)

  Separadores repetidos viram underscore único. A `<ext>` segue o `--container` quando normaliza. O campo `nome_saida` no JSON mostra o nome final de cada vídeo.
- **Sidecar de roteiro:** se houver um `<video>.md` ao lado da entrada (vindo do desmembrador), ele é **propagado** para a saída casando o nome `_OTIMIZADO.md` — o otimizador **não transcreve** pra isso, só carrega o roteiro adiante. O JSON traz `sidecar_propagado: true/false`.
- **Versão quadrada:** ao lado de cada `_OTIMIZADO.<ext>`, sai um `_OTIMIZADO_QUADRADO.<ext>` (1:1, largura cheia) e — com `--contato` — um `_CONTATO_QUADRADO.png` pra aprovação. A tag `_QUADRADO` entra logo após `_OTIMIZADO` e é carregada pelos sufixos seguintes da esteira (`..._OTIMIZADO_QUADRADO_LEGENDADO.mp4`). O quadrado **não** ganha `.md` próprio — o roteiro é o mesmo do vertical, um `.md` só por corte.

## Encadeamento com o combinador (otimizar+normalizar ANTES de combinar)

Esta skill é agnóstica de origem — otimiza qualquer vídeo ou pasta. A ordem **preferível** num projeto de combinação é otimizar **e normalizar** os cortes de segmento (GANCHOS, DESENVOLVIMENTOS...) **antes** de combiná-los:

```bash
python3 scripts/otimizar.py "<projeto>/GANCHOS" --normalizar
python3 scripts/otimizar.py "<projeto>/DESENVOLVIMENTOS" --normalizar
```

Assim cada corte é reencodado **uma única vez** (silêncio + normalização juntos), sai em `OTIMIZADOS/` já no alvo comum, e a combinação vira `concat -c copy` (cópia pura, sem reencode) — mínimo de gerações, mínimo de perda. Aponte o combinador às pastas otimizadas:
```
--segmentos GANCHOS/OTIMIZADOS DESENVOLVIMENTOS/OTIMIZADOS ...
```

> A seleção de takes é **por arquivo** — se os ganchos brutos têm várias tentativas, otimize cada um sozinho (com `--descartar`) **antes** de jogá-los no lote/combinação, ou resolva as takes na etapa de desmembramento. O lote não escolhe takes.

> Use o **mesmo alvo** ao normalizar todas as pastas-segmento. Specs divergentes entre segmentos quebram o `concat -c copy` — a combinadora tem rede de segurança (re-normaliza se detectar divergência), mas isso custa um reencode extra que o alvo único evita.

O nome limpo **não atrapalha** o combinador: como a identificação é preservada (rótulo + código no nome) e `OTIMIZADO` é tratado como ruído, ele extrai o código de origem (ex.: VAV19) e os pares nativos seguem casando.

## Anti-padrões (não faça)
- Trocar silêncio ou respiro por números soltos quando o usuário só pediu "mais justo/seco": use os presets `--modo-silencio`/`--modo-respiro`. Override fino (`--silence-*`, `--respiro-*`) só com valor pedido explicitamente.
- Acoplar os dois eixos: são independentes. Não force ambos em justo se o usuário só pediu um.
- Usar respiro **simétrico** (come consoante final) — nenhum modo é simétrico.
- Cortar começo ou fim do vídeo — só silêncios **internos**.
- Tratar residuais ~0.3–0.4s como falha — é o respiro projetado.
- Reprocessar arquivos que já têm `OTIMIZADO` no nome num lote (o script já os pula).
- Normalizar pastas-segmento diferentes pra alvos diferentes quando vão ser combinadas.
- Transcrever um vídeo que é fala única e limpa só por transcrever — a seleção de takes é pra quem tem repetição.
- Tentar selecionar takes em lote (`--descartar` vale só pra arquivo único).

## Referência
O porquê de cada número, a lógica do respiro assimétrico e o critério de seleção de takes estão em `referencia/METODO.md`.
