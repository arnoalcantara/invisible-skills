---
name: invisible-video-otimizador
description: >
  Pega um vídeo gravado e o deixa pronto: primeiro escolhe a melhor TAKE quando há várias tentativas da mesma fala (transcreve, agrupa as repetições e fica com a última), depois remove os silêncios internos sem comer palavra, e — opcionalmente — NORMALIZA o formato (resolução/fps/códec/áudio) no mesmo passo, entregando o corte pronto pra concatenar. Critério de silêncio validado: trecho ≥0.3s abaixo de -35dB; respiro assimétrico, em dois modos que o usuário escolhe — conservador (0.10s entrada / 0.25s saída, validado, default) ou justo (0.05s / 0.18s, corte mais seco); só silêncios internos, começo e fim intactos; corte ao frame exato. Aceita um arquivo único OU uma pasta inteira (lote). Use quando o usuário pedir "otimiza o vídeo", "tira os silêncios", "enxuga o ritmo", "remove as pausas", "corte mais justo/seco", "escolhe a melhor take", "esse gancho tem várias tentativas", "limpa as repetições", "otimiza essa pasta de vídeos", "padroniza esses vídeos". Saída em OTIMIZADOS/. Requer ffmpeg; a seleção de takes requer WhisperX (faz bootstrap).
---

# Otimizador de Vídeo (takes + silêncios + normalização)

Você pega um vídeo gravado e o deixa pronto para uso. São três coisas, nessa ordem:

1. **Seleção de takes** (opcional, quando o vídeo tem repetições): um gancho gravado bruto costuma ter várias tentativas da mesma fala — a pessoa erra no meio, volta, repete. Você transcreve, identifica as takes da mesma frase e fica com a **última** (o critério é sempre a última take), descartando as anteriores. Se não houver repetição, segue direto.
2. **Corte de silêncios internos** sem comer palavra, deixando o ritmo enxuto.
3. **Normalização de formato** (opcional): resolução, fps, códec, áudio — no mesmo reencode, entregando o corte já padronizado e pronto pra concatenar.

O original **nunca é tocado** — tudo sai em `OTIMIZADOS/`. O critério de silêncio foi afinado em iterações numa sessão real até ficar perfeito — está fechado, não reinvente os números sem motivo.

## Critério de silêncio validado (os números são sagrados)

- **Silêncio = trecho ≥ 0.3s abaixo de -35dB.** O `d` do `silencedetect` é a duração **mínima** pra contar como silêncio: pausa de 0.3s ou mais é cortada; pausa menor fica intacta.
  - **-35dB e não -30:** a -30 a palavra final dita baixo (o decrescendo natural do professor no fim da frase) caía como silêncio e era cortada. -35 trata fala fraca como fala.
- **Respiro assimétrico** (saída sempre maior que a entrada — o fim da palavra decai suave e precisa de mais margem que o início, que tem ataque alto). Dois modos, o usuário escolhe na hora:
  - **`conservador` (default, validado):** 0.10s na entrada, 0.25s na saída. O critério afinado em sessão real — preserva ataque e cauda com folga.
  - **`justo`:** 0.05s na entrada, 0.18s na saída. Corte mais apertado nas duas pontas, ritmo mais seco. Use quando o usuário pedir um corte "mais justo/seco/apertado".
  - **Respiro simétrico come consoante final — nenhum dos modos usa.**
- **Só silêncios internos.** Começo e fim do vídeo ficam intactos.
- **Corte ao frame exato** via `trim/atrim + setpts/asetpts + concat`.

## Fluxo de execução

### Fase 0 — Bootstrap
`python3 scripts/bootstrap.py --check-only`. O **ffmpeg** é sempre necessário (corte de silêncio/normalização). O **WhisperX** só é necessário se você for selecionar takes — confira `whisperx: true` no JSON apenas nesse caso. Se o usuário só quer enxugar silêncio/normalizar, ignore o estado do whisperx. Se faltar dependência, rode sem `--check-only` (instala) ou `brew install ffmpeg`. Se o JSON avisar que o modelo de transcrição não está em cache, avise o usuário do download (~1.5GB) **antes** de transcrever.

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

### Fase 2.5 — Escolher o modo de corte
Pergunte (ou deduza do pedido) o **modo de corte** — quão apertado o respiro em volta da fala:

- **`conservador`** (default) — `--modo conservador` (ou omitir): 0.10s entrada / 0.25s saída. O critério validado, com folga.
- **`justo`** — `--modo justo`: 0.05s entrada / 0.18s saída. Corte mais seco. Use quando o usuário pedir "mais justo", "mais apertado", "mais seco".

Na dúvida, fique no `conservador`. Só ofereça override fino (`--respiro-entrada`/`--respiro-saida`) se o usuário pedir um número específico.

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
No modo justo (corte mais seco):
```bash
python3 scripts/otimizar.py "<arquivo_ou_pasta>" --modo justo
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
Defaults já embutidos: `--silence-noise -35dB`, `--silence-min 0.3`, `--modo conservador` (respiro 0.10/0.25), `--crf 20`, `--preset medium`. O respiro vem do `--modo` (conservador ou justo); só passe `--respiro-entrada`/`--respiro-saida` se o usuário pedir um número específico — e avise que está saindo dos presets. Não mexa nos números de silêncio (-35dB, 0.3s) sem o usuário pedir.

`--descartar` vale **só para arquivo único**; em lote o script o ignora e avisa. O descarte de take, o corte de silêncio e a normalização acontecem no **mesmo reencode** — sem geração extra.

### Fase 4 — Ler a verificação
Cada resultado traz `verificacao`, `normalizado` e `takes_descartadas`:
- `silencios_residuais == 0` → ritmo limpo.
- Residuais **> 0** não são necessariamente erro: pausas ~0.3–0.49s são o **respiro preservado** (o silencedetect mede do cruzamento de limiar, não da última sílaba). Só investigue se sobrarem pausas longas reais.

Se um vídeo voltar com `aviso` de "nenhum silêncio interno detectado" e não houver takes a descartar, não há o que otimizar — informe e siga.

### Fase 5 — Resumo
Liste cada vídeo: nome de saída (`nome_saida`, já limpo pra `TIPO_ID_OTIMIZADO`), o modo de corte usado (`modo` + os `respiros`), takes descartadas (texto + tempo, se houve), silêncios cortados, segmentos mantidos, se foi normalizado (e pra qual alvo), e o caminho em `OTIMIZADOS/`.

## Saída
- Pasta `OTIMIZADOS/` ao lado da origem (ou `--out-dir`).
- Arquivo: `<TIPO>_<ID>_OTIMIZADO.<ext>` — o nome é **limpo** a partir do original: mantém o rótulo (GANCHO, DES...) e o código/numeração (VAV19, 34...), e **descarta** `BRUTA` e qualquer outro token de ruído. `GANCHO_VAV19_BRUTA.mov` → `GANCHO_VAV19_OTIMIZADO.mov`. A `<ext>` segue o `--container` quando normaliza. O campo `nome_saida` no JSON mostra o nome final de cada vídeo.

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

O nome limpo `TIPO_ID_OTIMIZADO` **não atrapalha** o combinador: ele extrai o código de origem (ex.: VAV19) do nome e trata `OTIMIZADO` como ruído, então os pares nativos seguem casando.

## Anti-padrões (não faça)
- Mexer nos números de silêncio (-35dB, 0.3s) sem o usuário pedir. O respiro tem preset: troque pelo `--modo` (conservador/justo), não por números soltos — a não ser que o usuário peça um valor específico.
- Usar respiro **simétrico** (come consoante final) — nenhum modo é simétrico.
- Cortar começo ou fim do vídeo — só silêncios **internos**.
- Tratar residuais ~0.3–0.4s como falha — é o respiro projetado.
- Reprocessar arquivos que já têm `OTIMIZADO` no nome num lote (o script já os pula).
- Normalizar pastas-segmento diferentes pra alvos diferentes quando vão ser combinadas.
- Transcrever um vídeo que é fala única e limpa só por transcrever — a seleção de takes é pra quem tem repetição.
- Tentar selecionar takes em lote (`--descartar` vale só pra arquivo único).

## Referência
O porquê de cada número, a lógica do respiro assimétrico e o critério de seleção de takes estão em `referencia/METODO.md`.
