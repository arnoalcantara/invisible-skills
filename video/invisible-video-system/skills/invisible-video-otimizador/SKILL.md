---
name: invisible-video-otimizador
description: >
  Remove os silêncios internos de um vídeo montado sem comer palavra, deixando o ritmo enxuto. Critério validado: silêncio = trecho >0.5s abaixo de -35dB; respiro assimétrico de 0.10s na entrada e 0.25s na saída (preserva ataque e cauda da fala); só silêncios internos, começo e fim intactos; corte ao frame exato. Aceita um arquivo único OU uma pasta inteira (lote). Use quando o usuário pedir "otimiza o vídeo", "tira os silêncios", "enxuga o ritmo", "remove as pausas", "corta os silêncios internos", "otimiza essa pasta de vídeos". Saída em OTIMIZADOS/. Requer ffmpeg (faz bootstrap; não usa WhisperX).
---

# Otimizador de Vídeo (remove silêncios internos)

Você pega um vídeo já montado e **remove os silêncios internos sem comer palavra**, deixando o ritmo enxuto. O critério foi afinado em três iterações numa sessão real até ficar perfeito — está fechado, não reinvente os números sem motivo.

## Critério validado (os números são sagrados)

- **Silêncio = trecho > 0.5s abaixo de -35dB.**
  - **-35dB e não -30:** a -30 a palavra final dita baixo (o decrescendo natural do professor no fim da frase) caía como silêncio e era cortada. -35 trata fala fraca como fala.
- **Respiro assimétrico: 0.10s na entrada, 0.25s na saída.**
  - Início de palavra tem ataque alto → 0.10s basta para não cortar o começo.
  - Fim de palavra decai suave (cauda baixa: "S", vogal átona) → precisa 0.25s para não comer o final.
  - **Respiro simétrico come consoante final — não usar.**
- **Só silêncios internos.** Começo e fim do vídeo ficam intactos.
- **Corte ao frame exato** via `trim/atrim + setpts/asetpts + concat`. Reencode HEVC preservando specs.

## Fluxo de execução

### Fase 0 — Bootstrap
`python3 scripts/bootstrap.py --check-only`. Aqui só importa o **ffmpeg** (esta skill **não usa WhisperX**). Confira que `ffmpeg` e `ffprobe` estão `true` no JSON; ignore o estado do whisperx. Se faltar ffmpeg, rode sem `--check-only` ou `brew install ffmpeg`.

### Fase 1 — Resolver a entrada
A skill aceita **um arquivo** OU **uma pasta** (lote: otimiza todos os vídeos da pasta, pulando os já marcados `__OTIMIZADO`). Confirme com o usuário o que será processado.

### Fase 2 — Otimizar
```bash
python3 scripts/otimizar.py "<arquivo_ou_pasta>"
```
Defaults validados já embutidos: `--silence-noise -35dB`, `--silence-min 0.5`, `--respiro-entrada 0.10`, `--respiro-saida 0.25`, `--crf 20`, `--preset medium`. Só passe argumentos diferentes se o usuário pedir — e diga que está saindo do critério validado.

O script detecta os silêncios, monta os segmentos a manter (com o respiro assimétrico), recorta+concatena ao frame e **roda a verificação automática** (silencedetect no resultado).

### Fase 3 — Ler a verificação
Cada resultado traz `verificacao`:
- `silencios_residuais == 0` → ritmo limpo.
- Residuais **> 0** não são necessariamente erro: pausas ~0.35–0.49s são o **respiro preservado** (o silencedetect mede do cruzamento de limiar, não da última sílaba). Só investigue se sobrarem pausas longas reais.

Se um vídeo voltar com `aviso` de "nenhum silêncio interno detectado", não há o que otimizar — informe e siga.

### Fase 4 — Resumo
Liste cada vídeo: silêncios cortados, segmentos mantidos, e o caminho em `OTIMIZADOS/`.

## Saída
- Pasta `OTIMIZADOS/` ao lado da origem (ou `--out-dir`).
- Arquivo: `<nome_original>__OTIMIZADO.<ext>`.

## Encadeamento com o combinador (otimizar ANTES de combinar)

Esta skill é agnóstica de origem — otimiza qualquer vídeo ou pasta. Dá para
otimizar os **cortes de segmento** (GANCHOS, DESENVOLVIMENTOS...) **antes** de
combiná-los, e essa é a ordem **preferível**: cada corte é reencodado uma única vez
na otimização, e a combinação vira `concat -c copy` (cópia, sem reencode) — menos
gerações de reencode, menos perda acumulada do que otimizar a peça já combinada.

Para esse fluxo, otimize cada pasta-segmento em lote, deixando a saída em
`OTIMIZADOS/` (default), e aponte ao combinador via
`--segmentos GANCHOS/OTIMIZADOS DESENVOLVIMENTOS/OTIMIZADOS ...`:
```bash
python3 scripts/otimizar.py "<projeto>/GANCHOS"
python3 scripts/otimizar.py "<projeto>/DESENVOLVIMENTOS"
```

O sufixo `__OTIMIZADO` no nome **não atrapalha** o combinador: ele extrai o código
de origem (ex.: VAV19) mesmo com o sufixo, então os pares nativos seguem casando.

## Anti-padrões (não faça)
- Mexer nos números (-35dB, 0.5s, 0.10/0.25) sem o usuário pedir.
- Usar respiro **simétrico** (come consoante final).
- Cortar começo ou fim do vídeo — só silêncios **internos**.
- Tratar residuais ~0.4s como falha — é o respiro projetado.
- Reprocessar arquivos `__OTIMIZADO` num lote (o script já os pula).

## Referência
O porquê de cada número e a lógica do respiro assimétrico estão em `referencia/METODO.md`.
