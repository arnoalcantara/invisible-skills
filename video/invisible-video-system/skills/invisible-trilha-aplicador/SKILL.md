---
name: invisible-trilha-aplicador
description: >
  Aplica trilha sonora de fundo num vídeo (ou pasta inteira), com normalização de
  loudness por LUFS — o jeito certo de controlar volume de trilha. A fala do vídeo é
  normalizada por ganho linear para um alvo (default -14 LUFS, padrão Reels) e a trilha
  para um alvo absoluto (default -37 LUFS, ~23 dB abaixo da fala), porque cada trilha vem
  masterizada num nível diferente e "X% de volume" não é consistente entre trilhas — LUFS
  é. O áudio original do vídeo nunca é removido: a trilha entra como camada de fundo, bem
  abaixo da fala, com fade in/out e loop quando a trilha é mais curta que o vídeo. Em lote,
  distribui as trilhas pelos vídeos o mais igualmente possível. Vídeo copiado sem
  recompressão (só o áudio é remixado). Saída em 99_FINALIZADOS/<nome>_FINALIZADO.mp4, sem
  tocar no original. Use SEMPRE que o usuário pedir para "colocar trilha", "aplicar trilha
  de fundo", "música de fundo no vídeo", "trilha sonora", "pôr uma trilha embaixo da fala",
  "trilhar os vídeos", "variar as trilhas no lote". Requer ffmpeg (faz bootstrap).
---

# Aplicador de Trilha (mix com normalização de loudness)

Você pega um vídeo com fala (professor, narração) e devolve **o mesmo vídeo com uma trilha
de fundo por baixo** — a fala original intacta no nível certo, a trilha discreta atrás. O
áudio original **nunca é removido**; a trilha é uma segunda camada, mixada bem abaixo.

> O vídeo original **nunca é tocado**. A saída nasce na pasta-irmã `99_FINALIZADOS/`
> (última etapa da linha; lê tipicamente de `04_COMBINADOS`), com o nome do vídeo de
> origem + `_FINALIZADO` no fim.

## A ideia central: LUFS, não porcentagem

Volume de trilha **não se controla em "%"**. Porcentagem é ganho relativo: multiplica o que
já existe. Como cada trilha vem masterizada num nível diferente (medido num acervo real:
de -7 a -16 LUFS, ~9 dB de diferença — quase o dobro de volume percebido), "8% de volume"
soa alto numa trilha e sumido em outra. O volume percebido se mede em **LUFS** (loudness).

Então o método normaliza **dois alvos absolutos em LUFS**, e tudo converge:

| Camada | Alvo (default) | Por quê |
|---|---|---|
| **Fala** | **-14 LUFS** | padrão Reels/social; a fala manda no resultado |
| **Trilha** | **-37 LUFS** | ~23 dB abaixo da fala — fundo presente, mas discreto |

Cada vídeo e cada trilha são **medidos individualmente** e recebem um ganho próprio que os
leva ao mesmo destino. Resultado: o lote inteiro fica consistente — a fala no mesmo nível
em todos, a trilha com a mesma presença em todos, não importa o material de origem.

A normalização da fala é **ganho linear** (sobe/desce o nível inteiro), **não compressão** —
preserva a dinâmica natural da voz, sem som "processado".

### Ajustar o nível da trilha

Controle por **um número só**: o alvo da trilha. Mais presente → suba para `-34`. Mais
discreta → desça para `-40`. Vale igual para qualquer trilha. (`--alvo-trilha`).

## Fluxo de execução

### Fase 0 — Bootstrap
```bash
python3 scripts/bootstrap.py --check-only
```
Única dependência é o **ffmpeg/ffprobe**. Se `pronto` for `false`, rode sem `--check-only`
(instala via Homebrew) ou `brew install ffmpeg`.

### Fase 1 — Confirmar alvo, trilhas e níveis
- **Alvo:** o vídeo ou a pasta que o usuário deu (numa pasta, pega os vídeos diretos, fora
  a própria `99_FINALIZADOS`).
- **Trilhas:** a pasta de trilhas (`--trilhas`). Numa pasta de trilhas, todas entram na
  distribuição.
- **Distribuir × fixa:** default em lote é **distribuir as trilhas o mais igualmente
  possível** (round-robin sobre a lista ordenada — N vídeos / M trilhas). Para uma trilha
  única em todos, `--trilha "<arquivo.mp3>"`.
- **Níveis:** defaults `--alvo-fala -14` e `--alvo-trilha -37`. Só mexa se o usuário pedir
  trilha mais alta/baixa.

### Fase 2 — Amostra primeiro (recomendado)
Antes do lote, valide o nível numa amostra: rode em **um vídeo** e deixe o usuário ouvir.
O ouvido decide o alvo da trilha. Foi assim que -37 LUFS foi calibrado.
```bash
python3 scripts/aplicar.py "<um_video.mp4>" --trilhas "<pasta_trilhas>"
```

### Fase 3 — Aplicar no lote
```bash
python3 scripts/aplicar.py "<pasta_videos>" --trilhas "<pasta_trilhas>"
```
Cada vídeo: mede a fala (LUFS), pega a próxima trilha do rodízio, mede a trilha (cacheada),
calcula os ganhos, mixa com `amix normalize=0` (não divide a fala), trilha com fade in/out
de 1.5s e `-stream_loop -1` (cobre vídeos mais longos que a trilha), `-c:v copy` (vídeo sem
recompressão), áudio AAC 192k. Rápido: ~1s por vídeo (só o áudio é reprocessado).

### Fase 4 — Conferir e resumir
O script imprime, por vídeo, a trilha usada e os ganhos. Confira o loudness final de
algumas amostras (deve bater no `--alvo-fala`):
```bash
ffmpeg -i "99_FINALIZADOS/<nome>_FINALIZADO.mp4" -af ebur128 -f null - 2>&1 | grep "I:" | tail -1
```

## Nomenclatura
- Pasta de saída oficial: **`99_FINALIZADOS/`** (pasta-**irmã** da entrada, não subpasta).
- Arquivo: **nome do vídeo de origem + `_FINALIZADO`** no fim.
  Ex.: `GANCHO_VAV19__DESENV_VAV57_VERTICAL.mp4` → `GANCHO_VAV19__DESENV_VAV57_VERTICAL_FINALIZADO.mp4`.

## Encadeamento no sistema de vídeo
Esta é a **última etapa** da linha de produção: otimizador (`02_OTIMIZADOS`) → legendagem/
variação (`03_PREPARADOS`) → combinador (`04_COMBINADOS`), e aqui ganha a trilha, indo
para a pasta-irmã `99_FINALIZADOS/`. Mas funciona em qualquer vídeo com fala.

## Anti-padrões (não faça)
- Controlar volume de trilha em "%". Use LUFS — é o único jeito consistente entre trilhas.
- Remover ou abaixar demais a fala original. A fala é a camada principal; a trilha é fundo.
- Usar `amix` sem `normalize=0` — o default do amix divide o volume da fala pela metade.
- Comprimir a fala para normalizar. Ganho linear preserva a voz; compressão a deixa
  processada.
- Recodificar o vídeo. `-c:v copy` mantém a imagem intacta; só o áudio muda.
- Esquecer o loop da trilha — trilha curta num vídeo longo deixaria silêncio no fim.
- Gravar fora de `99_FINALIZADOS` ou tocar no original.

## Referência
O método completo (por que LUFS, calibração do -37, medição do acervo) está em
`referencia/METODO.md`.
