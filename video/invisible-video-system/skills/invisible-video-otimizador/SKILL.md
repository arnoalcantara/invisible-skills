---
name: invisible-video-otimizador
description: >
  Remove os silêncios internos de um vídeo montado sem comer palavra, deixando o ritmo enxuto — e, opcionalmente, NORMALIZA o formato (resolução/fps/códec/áudio) no mesmo passo, entregando o corte pronto pra concatenar. Critério validado: silêncio = trecho ≥0.3s abaixo de -35dB; respiro assimétrico de 0.10s na entrada e 0.25s na saída (preserva ataque e cauda da fala); só silêncios internos, começo e fim intactos; corte ao frame exato. Aceita um arquivo único OU uma pasta inteira (lote). Use quando o usuário pedir "otimiza o vídeo", "tira os silêncios", "enxuga o ritmo", "remove as pausas", "corta os silêncios internos", "otimiza essa pasta de vídeos", "padroniza esses vídeos". Saída em OTIMIZADOS/. Requer ffmpeg (faz bootstrap; não usa WhisperX).
---

# Otimizador de Vídeo (silêncios + normalização)

Você pega um vídeo já montado e **remove os silêncios internos sem comer palavra**, deixando o ritmo enxuto. Se o usuário quiser, no mesmo reencode você também **normaliza o formato** (resolução, fps, códec, áudio) — entregando o corte já padronizado e pronto pra concatenar. O critério de silêncio foi afinado em iterações numa sessão real até ficar perfeito — está fechado, não reinvente os números sem motivo.

## Critério validado (os números são sagrados)

- **Silêncio = trecho ≥ 0.3s abaixo de -35dB.** O `d` do `silencedetect` é a duração **mínima** pra contar como silêncio: pausa de 0.3s ou mais é cortada; pausa menor fica intacta.
  - **-35dB e não -30:** a -30 a palavra final dita baixo (o decrescendo natural do professor no fim da frase) caía como silêncio e era cortada. -35 trata fala fraca como fala.
- **Respiro assimétrico: 0.10s na entrada, 0.25s na saída.**
  - Início de palavra tem ataque alto → 0.10s basta para não cortar o começo.
  - Fim de palavra decai suave (cauda baixa: "S", vogal átona) → precisa 0.25s para não comer o final.
  - **Respiro simétrico come consoante final — não usar.**
- **Só silêncios internos.** Começo e fim do vídeo ficam intactos.
- **Corte ao frame exato** via `trim/atrim + setpts/asetpts + concat`.

## Fluxo de execução

### Fase 0 — Bootstrap
`python3 scripts/bootstrap.py --check-only`. Aqui só importa o **ffmpeg** (esta skill **não usa WhisperX**). Confira que `ffmpeg` e `ffprobe` estão `true` no JSON; ignore o estado do whisperx. Se faltar ffmpeg, rode sem `--check-only` ou `brew install ffmpeg`.

### Fase 1 — Resolver a entrada
A skill aceita **um arquivo** OU **uma pasta** (lote: otimiza todos os vídeos da pasta, pulando os já marcados `__OTIMIZADO`). Confirme com o usuário o que será processado.

### Fase 2 — Decidir o formato de saída (normalizar ou preservar)
Pergunte ao usuário se quer **normalizar** o formato no mesmo passo (recomendado quando os vídeos vão ser combinados depois, ou quando vêm com specs mistas):

- **Preservar specs do original** (default quando o usuário só quer enxugar o ritmo) — não passa `--normalizar`. Cada vídeo sai no mesmo formato em que entrou.
- **Normalizar para um alvo comum** — passa `--normalizar`. O alvo padrão é **Full HD vertical**: 1080×1920, 30fps, HEVC (libx265 CRF20, `-tag:v hvc1`), AAC 48kHz stereo, `.mp4`. Ofereça as alternativas e deixe o FHD/MP4 como default:
  - **4K** vertical: `--largura 2160 --altura 3840`
  - **MOV**: `--container mov`
  - **H.264**: `--vcodec libx264`
  - outra resolução/fps/áudio conforme o pedido.

A normalização usa `scale+pad+setsar=1` (encaixa preservando proporção, barras se preciso) — cobre entrada que não seja 9:16 sem distorcer.

### Fase 3 — Otimizar
Preservando specs:
```bash
python3 scripts/otimizar.py "<arquivo_ou_pasta>"
```
Otimizando **e** normalizando (FHD vertical default):
```bash
python3 scripts/otimizar.py "<arquivo_ou_pasta>" --normalizar
```
Com alvo customizado (ex.: 4K MOV H.264):
```bash
python3 scripts/otimizar.py "<arquivo_ou_pasta>" --normalizar \
  --largura 2160 --altura 3840 --container mov --vcodec libx264
```
Defaults validados já embutidos: `--silence-noise -35dB`, `--silence-min 0.3`, `--respiro-entrada 0.10`, `--respiro-saida 0.25`, `--crf 20`, `--preset medium`. Só mexa nos números de silêncio/respiro se o usuário pedir — e avise que está saindo do critério validado.

O script detecta os silêncios, monta os segmentos a manter (com o respiro assimétrico), recorta+concatena ao frame (normalizando junto, se pedido) e **roda a verificação automática** (silencedetect no resultado).

### Fase 4 — Ler a verificação
Cada resultado traz `verificacao` e `normalizado` (true/false):
- `silencios_residuais == 0` → ritmo limpo.
- Residuais **> 0** não são necessariamente erro: pausas ~0.3–0.49s são o **respiro preservado** (o silencedetect mede do cruzamento de limiar, não da última sílaba). Só investigue se sobrarem pausas longas reais.

Se um vídeo voltar com `aviso` de "nenhum silêncio interno detectado", não há o que otimizar — informe e siga.

### Fase 5 — Resumo
Liste cada vídeo: silêncios cortados, segmentos mantidos, se foi normalizado (e pra qual alvo), e o caminho em `OTIMIZADOS/`.

## Saída
- Pasta `OTIMIZADOS/` ao lado da origem (ou `--out-dir`).
- Arquivo: `<nome_original>__OTIMIZADO.<ext>` (a `<ext>` segue o `--container` quando normaliza).

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

> Use o **mesmo alvo** ao normalizar todas as pastas-segmento. Specs divergentes entre segmentos quebram o `concat -c copy` — a combinadora tem rede de segurança (re-normaliza se detectar divergência), mas isso custa um reencode extra que o alvo único evita.

O sufixo `__OTIMIZADO` no nome **não atrapalha** o combinador: ele extrai o código de origem (ex.: VAV19) mesmo com o sufixo, então os pares nativos seguem casando.

## Anti-padrões (não faça)
- Mexer nos números de silêncio (-35dB, 0.3s, 0.10/0.25) sem o usuário pedir.
- Usar respiro **simétrico** (come consoante final).
- Cortar começo ou fim do vídeo — só silêncios **internos**.
- Tratar residuais ~0.3–0.4s como falha — é o respiro projetado.
- Reprocessar arquivos `__OTIMIZADO` num lote (o script já os pula).
- Normalizar pastas-segmento diferentes pra alvos diferentes quando vão ser combinadas.

## Referência
O porquê de cada número e a lógica do respiro assimétrico estão em `referencia/METODO.md`.
