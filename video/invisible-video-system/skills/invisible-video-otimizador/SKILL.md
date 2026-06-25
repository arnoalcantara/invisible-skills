---
name: invisible-video-otimizador
description: >
  Pega um vídeo gravado e o deixa pronto: APARA AS PONTAS pela fala (transcreve a bruta com WhisperX e usa a 1ª e a última palavra pra cortar tudo que vem antes/depois da fala — suspiro, estalo de boca, barulho de cadeira no fim; o silencedetect sozinho não pega isso porque ruído não é silêncio), escolhe a melhor TAKE quando há várias tentativas da mesma fala (agrupa as repetições e fica com a última), remove os silêncios internos sem comer palavra, e SEMPRE NORMALIZA o formato (resolução/fps/códec/áudio) no mesmo passo (alvo default FHD vertical 1080x1920/30fps/HEVC/AAC; trocável por flags), entregando o corte pronto pra concatenar. A transcrição da bruta é efêmera (só pra achar a borda da fala) e NÃO serve pra legenda — a legenda usa outro .json, gerado depois sobre o otimizado. Dois eixos de modo independentes, ambos justo por default: modo de silêncio (o que conta como silêncio — default justo -33dB/0.15s, ou conservador -35dB/0.3s) e modo de respiro (margem nas bordas — default justo 0.05/0.18, ou conservador 0.10/0.25, sempre assimétrico). Corte ao frame exato. Gera também, na mesma pasta, a versão QUADRADA (1:1) de cada otimizado (sufixo _QUADRADO), reenquadrando o vertical por detecção de rosto (YuNet) ancorada nos olhos — para o feed do Instagram, em paralelo ao vertical pela esteira. Aceita um arquivo único OU uma pasta inteira (lote). Use quando o usuário pedir "otimiza o vídeo", "tira os silêncios", "enxuga o ritmo", "remove as pausas", "corta o barulho do fim", "corte mais justo/seco", "escolhe a melhor take", "esse gancho tem várias tentativas", "limpa as repetições", "otimiza essa pasta de vídeos", "padroniza esses vídeos", "faz a versão quadrada". O vídeo otimizado é o vertical e sai como `<id>_OTIMIZADO_VERTICAL` (o token de formato é sempre o último); o quadrado troca `_VERTICAL` por `_QUADRADO`. Saída na pasta-irmã `02_OTIMIZADOS/` (primeira etapa da linha de produção, irmã da fonte `01_Brutas`). Requer ffmpeg e WhisperX (o aparo de pontas transcreve sempre); o quadrado requer OpenCV (faz bootstrap).
---

# Otimizador de Vídeo (aparo de pontas + takes + silêncios + normalização)

Você pega um vídeo gravado e o deixa pronto para uso. São quatro coisas, nessa ordem:

1. **Aparo de pontas** (sempre): o otimizador transcreve a **bruta** com WhisperX e usa a **primeira e a última palavra** pra cravar onde a fala de fato começa e termina. Tudo antes da 1ª palavra e depois da última — suspiro, estalo de boca, "tsc", o barulho da cadeira no fim — é **cortado**. O `silencedetect` sozinho não pega isso: pra ele, ruído é "som acima do limiar" = fala, então sobreviveria ao corte. É a transcrição que distingue palavra de ruído. **A borda é ancorada no silêncio**, não tomada crua do JSON: o WhisperX às vezes **estica o `end` da última palavra** através do silêncio até o ruído que vem depois (ex.: "futuro." marcada 6.6→11.3 num clipe onde a fala acaba em ~7s e há 4s de silêncio+ruído depois). Confiar nesse `end` faria o ruído sobreviver. Então, quando a última palavra é longa demais ou há um silêncio logo após ela, o fim real é o **início desse silêncio**.
2. **Seleção de takes** (opcional, quando o vídeo tem repetições): um gancho gravado bruto costuma ter várias tentativas da mesma fala — a pessoa erra no meio, volta, repete. Você transcreve, identifica as takes da mesma frase e fica com a **última** (o critério é sempre a última take), descartando as anteriores. Se não houver repetição, segue direto.
3. **Corte de silêncios internos** sem comer palavra, deixando o ritmo enxuto.
4. **Normalização de formato** (opcional): resolução, fps, códec, áudio — no mesmo reencode, entregando o corte já padronizado e pronto pra concatenar.

O original **nunca é tocado** — tudo sai na pasta-irmã `02_OTIMIZADOS/`. O critério de silêncio foi afinado em iterações numa sessão real até ficar perfeito — está fechado, não reinvente os números sem motivo.

**Dois `.json` diferentes, não confundir.** O aparo transcreve a **bruta** (JSON-1, timestamps pré-corte) só pra achar a borda da fala — é **efêmero** (cache em `.transcricao/` ao lado da entrada, não vai pra `02_OTIMIZADOS`). A legendagem usa outro `.json` (JSON-2), gerado **depois** pela `invisible-legenda-arquivos` sobre o vídeo **já otimizado** — timestamps diferentes, porque o corte deslocou tudo. Reaproveitar o JSON-1 pra legendar daria legenda fora de sincronia.

**WhisperX é obrigatório** (não mais só pra takes): sem transcrição não há como achar onde a fala termina, então o script **falha** se o WhisperX não estiver disponível.

## Critério de corte — dois eixos de modo (conservador/justo)

São **dois presets independentes**, cada um com modo `conservador` e `justo`. **Os dois vêm `justo` por default** (ritmo seco é o padrão pedido). **Não se acoplam** — o usuário pode pôr um em justo e o outro em conservador.

**1. Modo de silêncio** (`--modo-silencio`) — o que conta como silêncio cortável:
- **`justo` (default):** **-33dB / 0.15s**. Limiar mais alto pega mais coisa como silêncio; duração menor corta pausas mais curtas. Ritmo mais seco — é o padrão.
- **`conservador`:** silêncio = trecho **≥ 0.3s abaixo de -35dB**. O `d` do `silencedetect` é a duração mínima; pausa de 0.3s+ é cortada, menor fica intacta. **-35dB e não -30:** a -30 a palavra final dita baixo (decrescendo natural no fim da frase) caía como silêncio. -35 trata fala fraca como fala. Use quando preservar cauda/ataque importar mais que ritmo.

**2. Modo de respiro** (`--modo-respiro`) — a margem deixada nas bordas da fala (assimétrica: saída > entrada, porque o fim da palavra decai suave e o início tem ataque alto):
- **`justo` (default):** 0.05s entrada / 0.18s saída. Mais apertado nas duas pontas — é o padrão.
- **`conservador`:** 0.10s entrada / 0.25s saída. Preserva ataque e cauda com folga. Use quando o corte justo estiver comendo borda.
- **Respiro simétrico come consoante final — nenhum modo usa.**

- **Silêncios internos** são cortados; as **pontas** são aparadas pela borda da **fala** (1ª/última palavra do WhisperX), não pela borda do vídeo — com o mesmo respiro assimétrico. A fala em si nunca é tocada; o que cai fora é ruído.
- **Corte ao frame exato** via `trim/atrim + setpts/asetpts + concat`.

## Fluxo de execução

### Fase 0 — Bootstrap
`python3 scripts/bootstrap.py --check-only`. O **ffmpeg** é sempre necessário (corte de silêncio/normalização). O **WhisperX** também é **sempre necessário agora** — o aparo de pontas transcreve a bruta em toda otimização (não só pra takes); confira `whisperx: true` e pegue o `whisperx_bin` (passe-o ao `otimizar.py` via `--whisperx-bin`, senão ele resolve sozinho rodando o bootstrap em processo). O **OpenCV** (`opencv: true`, com `python_cv2` apontando o python da venv) é necessário pra gerar o quadrado — o bootstrap instala o `opencv-python-headless` na venv central. Se faltar dependência, rode sem `--check-only` (instala) ou `brew install ffmpeg`. Se o JSON avisar que o modelo de transcrição não está em cache, avise o usuário do download (~1.5GB) **antes** de transcrever. (O modelo do YuNet, ~230KB, já vem versionado em `referencia/modelos/` — sem download.)

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

### Fase 2 — Formato de saída (normalização sempre ativa)
A normalização é **sempre** aplicada — não é mais opcional. Toda otimização sai no alvo, no mesmo reencode do corte. O alvo padrão é **Full HD vertical**: 1080×1920, 30fps, HEVC (libx265 CRF20, `-tag:v hvc1`), AAC 48kHz stereo, `.mp4`. Não precisa passar nada pra isso acontecer.

Só toque no alvo se o pedido for específico (override dos defaults):
- **4K** vertical: `--largura 2160 --altura 3840`
- **MOV**: `--container mov`
- **H.264**: `--vcodec libx264`
- outra resolução/fps/áudio conforme o pedido.

A normalização usa `scale+pad+setsar=1` (encaixa preservando proporção, barras se preciso) — cobre entrada que não seja 9:16 sem distorcer. (Como o container default é `mp4`, uma entrada `.mov` sai `.mp4` — é o esperado da padronização.) A flag `--normalizar` ainda é aceita mas virou no-op.

### Fase 2.5 — Escolher os modos (silêncio e respiro)
Dois presets **independentes**, **ambos `justo` por default** (ritmo seco é o padrão). Na dúvida, deixe os defaults (silêncio justo + respiro justo) — não precisa passar nada.

- **Modo de silêncio** (`--modo-silencio`): `justo` (-33dB / 0.15s — default, pega mais silêncio e pausas mais curtas) ou `conservador` (-35dB / 0.3s — preserva mais cauda/ataque).
- **Modo de respiro** (`--modo-respiro`): `justo` (0.05/0.18 — default, bordas mais rentes) ou `conservador` (0.10/0.25 — mais folga). Suba o respiro pra conservador se o corte justo estiver comendo borda de palavra.

Pode misturar. Override fino só se pedir número específico: `--silence-noise`/`--silence-min` e `--respiro-entrada`/`--respiro-saida` sobrepõem o preset correspondente.

### Fase 3 — Otimizar
Tudo num reencode só (aparo de pontas + descarte de take + corte de silêncio + normalização — sempre).

Caso padrão (sem takes; já apara pontas, corta silêncio justo, respiro justo e normaliza FHD vertical):
```bash
python3 scripts/otimizar.py "<arquivo_ou_pasta>"
```
Com descarte de takes (vindo da Fase 1):
```bash
python3 scripts/otimizar.py "<video>" --descartar "0.0-1.7,3.0-5.05"
```
Respiro com mais folga (silêncio segue justo):
```bash
python3 scripts/otimizar.py "<arquivo_ou_pasta>" --modo-respiro conservador
```
Trocando o alvo de normalização (4K MOV H.264):
```bash
python3 scripts/otimizar.py "<arquivo_ou_pasta>" \
  --largura 2160 --altura 3840 --container mov --vcodec libx264
```
Tudo junto (takes + alvo 4K MOV H.264):
```bash
python3 scripts/otimizar.py "<video>" --descartar "0.0-1.7,3.0-5.05" \
  --largura 2160 --altura 3840 --container mov --vcodec libx264
```
Defaults já embutidos: `--modo-silencio justo` (-33dB / 0.15s), `--modo-respiro justo` (0.05/0.18), normalização FHD vertical, `--crf 20`, `--preset medium`. Silêncio e respiro vêm dos respectivos `--modo-*`; só passe os overrides finos (`--silence-noise`/`--silence-min`, `--respiro-entrada`/`--respiro-saida`) se o usuário pedir um número específico — e avise que está saindo dos presets.

`--descartar` vale **só para arquivo único**; em lote o script o ignora e avisa. O aparo de pontas, o descarte de take, o corte de silêncio e a normalização acontecem no **mesmo reencode** — sem geração extra.

### Fase 3.7 — Versão quadrada (1:1) para o feed
Depois de gerar os `_OTIMIZADO_VERTICAL` (verticais), produza a versão **quadrada** de cada um, na **mesma pasta** `02_OTIMIZADOS/`. O quadrado caminha em paralelo ao vertical por toda a esteira (combinador, legendas, gancho-escrito, trilha) e sai junto no fim. O nome **substitui** `_VERTICAL` por `_QUADRADO` (formato sempre o último token): `<id>_OTIMIZADO_VERTICAL.mp4` → `<id>_OTIMIZADO_QUADRADO.mp4`.

Rode com o **python da venv** (o que tem o OpenCV — campo `python_cv2` do bootstrap), apontando a pasta `02_OTIMIZADOS/`:
```bash
<python_cv2> scripts/quadrado.py "<.../02_OTIMIZADOS>" --contato
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
<python_cv2> scripts/quadrado.py "<.../02_OTIMIZADOS/DME_VAV19_GANCHO_OTIMIZADO_VERTICAL.mp4>" --ancora 0.45
```

Pule esta fase só se o usuário disser explicitamente que **não** quer o quadrado (o padrão é sempre gerar os dois).

### Fase 4 — Ler a verificação
Cada resultado traz `verificacao`, `fala`, `normalizado` e `takes_descartadas`:
- `silencios_residuais == 0` → ritmo limpo.
- Residuais **> 0** não são necessariamente erro: pausas ~0.3–0.49s são o **respiro preservado** (o silencedetect mede do cruzamento de limiar, não da última sílaba). Só investigue se sobrarem pausas longas reais.
- `fala` mostra onde a fala começa/termina (`inicio`/`fim`) e quanto o aparo cortou de cada ponta (`aparou_inicio_s`/`aparou_fim_s`) — é onde você vê o ruído do fim que foi removido.

Se um vídeo voltar com `aviso` de "nada a otimizar" (sem silêncio interno, sem take e sem ruído nas pontas), não há o que fazer — informe e siga. Se voltar com `erro` (ex.: transcrição falhou), o aparo não rodou — reporte e não siga com aquele vídeo.

### Fase 5 — Resumo
Liste cada vídeo: nome de saída (`nome_saida`, já limpo — identificação preservada + `_OTIMIZADO`), os modos usados (`modo_silencio` + `silencio`, `modo_respiro` + `respiros`), takes descartadas (texto + tempo, se houve), silêncios cortados, segmentos mantidos, se foi normalizado (e pra qual alvo), e o caminho em `02_OTIMIZADOS/`.

## Saída
- Pasta-irmã `02_OTIMIZADOS/` (primeira etapa da linha de produção, irmã da fonte `01_Brutas`; ou `--out-dir`).
- Arquivo: nome **limpo** a partir do original + `_OTIMIZADO` + token de formato `_VERTICAL` (sempre o último). A regra é **preservar toda a identificação** (tipo, código, prefixo, número — na ordem original) e **descartar só os tokens de ruído de processamento**: `BRUTA`, `VERTICAL`, `HORIZONTAL`, `RAW`, `FINAL`, `OTIMIZADO` (o `_VERTICAL` final é reescrito pela skill, não o herdado do bruto). Nada de tipo/código se perde. Exemplos:
  - `GANCHO_VAV19_BRUTA.mov` → `GANCHO_VAV19_OTIMIZADO_VERTICAL.mov`
  - `DME__VAV23__VERTICAL__BRUTA__DESENVOLVIMENTO.mp4` → `DME_VAV23_DESENVOLVIMENTO_OTIMIZADO_VERTICAL.mp4` (o `DESENVOLVIMENTO` **fica**)

  Separadores repetidos viram underscore único. A `<ext>` segue o `--container` quando normaliza. O campo `nome_saida` no JSON mostra o nome final de cada vídeo.
- **Sidecar de roteiro:** se houver um `<video>.md` ao lado da entrada (vindo do desmembrador), ele é **propagado** para a saída **sem token de formato** (`<id>_OTIMIZADO.md`) — um sidecar serve vertical e quadrado (mesmo áudio/texto). O otimizador **não transcreve** pra isso, só carrega o roteiro adiante. O JSON traz `sidecar_propagado: true/false`.
- **Versão quadrada:** ao lado de cada `_OTIMIZADO_VERTICAL.<ext>`, sai um `_OTIMIZADO_QUADRADO.<ext>` (1:1, largura cheia) — o token `_VERTICAL` é **substituído** por `_QUADRADO` (formato sempre o último token) — e, com `--contato`, um `_CONTATO_QUADRADO.png` pra aprovação. O quadrado **não** ganha `.md` próprio — o roteiro é o mesmo do vertical, um `.md` só por corte.

## Lugar na linha de produção (etapa 02)

Esta skill é a **primeira etapa** da linha de produção de vídeo. Lê os brutos (de `01_Brutas` ou de qualquer pasta/arquivo) e grava os segmentos otimizados — vertical e quadrado — em `02_OTIMIZADOS`. Daí em diante a esteira é:

```
01_Brutas → [otimizador] → 02_OTIMIZADOS → [legenda-arquivos: .json] →
            [legendas-aplicador / var-gancho-escrito] → 03_PREPARADOS →
            [combinador] → 04_COMBINADOS → [trilha] → 99_FINALIZADOS
```

A normalização (`--normalizar`) acontece **aqui**, no mesmo reencode do corte de silêncio: cada segmento sai já no alvo comum, então a combinação lá na frente vira `concat -c copy` (cópia pura, sem reencode) — mínimo de gerações, mínimo de perda.

```bash
python3 scripts/otimizar.py "<projeto>/01_Brutas/GANCHOS" --normalizar
python3 scripts/otimizar.py "<projeto>/01_Brutas/DESENVOLVIMENTOS" --normalizar
```

> A seleção de takes é **por arquivo** — se os ganchos brutos têm várias tentativas, otimize cada um sozinho (com `--descartar`) **antes**, ou resolva as takes na etapa de desmembramento. O lote não escolhe takes.

> Use o **mesmo alvo** ao normalizar todos os segmentos. Specs divergentes quebram o `concat -c copy` — o combinador tem rede de segurança (re-normaliza se detectar divergência), mas isso custa um reencode extra que o alvo único evita.

O nome carrega o contrato da linha: identificação preservada (rótulo + código), `_OTIMIZADO`, e o token de formato **sempre por último** (`_VERTICAL`/`_QUADRADO`). É o que a legenda-arquivos, a legendas-aplicador, a var-gancho e o combinador leem pra orquestrar tudo pelo nome.

## Anti-padrões (não faça)
- Trocar silêncio ou respiro por números soltos quando o usuário só pediu "mais justo/seco": use os presets `--modo-silencio`/`--modo-respiro`. Override fino (`--silence-*`, `--respiro-*`) só com valor pedido explicitamente.
- Acoplar os dois eixos: são independentes. Não force ambos em justo se o usuário só pediu um.
- Usar respiro **simétrico** (come consoante final) — nenhum modo é simétrico.
- Comer a **fala** nas pontas — o aparo corta só o que está fora da 1ª/última palavra (ruído), com respiro. A primeira e a última palavra ficam sempre.
- Tratar residuais ~0.3–0.4s como falha — é o respiro projetado.
- Reprocessar arquivos que já têm `OTIMIZADO` no nome num lote (o script já os pula).
- Normalizar pastas-segmento diferentes pra alvos diferentes quando vão ser combinadas.
- Reaproveitar o `.json` da bruta (JSON-1, do aparo) pra legendar — a legenda usa o JSON-2 da `invisible-legenda-arquivos`, gerado sobre o otimizado.
- Tentar selecionar takes em lote (`--descartar` vale só pra arquivo único).

## Referência
O porquê de cada número, a lógica do respiro assimétrico e o critério de seleção de takes estão em `referencia/METODO.md`.
