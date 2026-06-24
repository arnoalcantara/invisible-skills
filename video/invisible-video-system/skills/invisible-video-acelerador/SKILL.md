---
name: invisible-video-acelerador
description: >
  Acelera a velocidade de um vídeo (ou de uma pasta inteira) por um fator fixo à escolha: 1.2x (padrão), 1.5x ou 2x. Gera UM único arquivo acelerado, na velocidade escolhida. Acelera vídeo E áudio juntos, mantendo a sincronia e PRESERVANDO O TOM DA VOZ (atempo, não vira chipmunk). O vídeo é reencodado em H.264 qualidade alta (acelerar exige recompressão), preservando resolução e fps da fonte; o áudio sai em AAC. NÃO toca no original — grava ao lado, com _ACELERADO_<FATOR> no fim do nome (1.2x→_ACELERADO_12X, 1.5x→_ACELERADO_15X, 2x→_ACELERADO_2X), na convenção da esteira (sufixos acumulam no fim). Aceita um arquivo único OU uma pasta (lote); numa pasta pula o que já tem _ACELERADO. Independente — roda em qualquer ponto da esteira (otimizado, combinação, legendado, finalizado). Use quando o usuário pedir "acelera esse vídeo", "deixa mais rápido", "põe em 1.5x", "acelera o lote em 2x", "speed up". Requer ffmpeg (faz bootstrap).
---

# Acelerador de Vídeo (1.2x / 1.5x / 2x)

Acelera a velocidade de um vídeo (ou de uma pasta inteira) por um fator fixo. Gera **um único arquivo** acelerado, na velocidade escolhida (1.2x por padrão). Vídeo e áudio são acelerados **juntos**, sincronizados, e a voz **mantém o tom** — sem efeito chipmunk.

## Comportamento — grava ao lado, original intacto

Para cada alvo:
1. Acelera o vídeo (`setpts=PTS/FATOR`) e o áudio (`atempo=FATOR`) pelo mesmo fator.
2. Reencoda o vídeo em H.264 (acelerar exige recompressão), preservando **resolução e fps** da fonte; áudio em AAC.
3. Grava **ao lado do original**, com `_ACELERADO_<FATOR>` no fim do nome. O original **não é tocado**.

Sufixo por fator (acumula no fim, na convenção da esteira):

| Fator | Sufixo | Exemplo |
|---|---|---|
| 1.2x | `_ACELERADO_12X` | `..._FINALIZADO_ACELERADO_12X.mp4` |
| 1.5x | `_ACELERADO_15X` | `..._FINALIZADO_ACELERADO_15X.mp4` |
| 2x | `_ACELERADO_2X` | `..._FINALIZADO_ACELERADO_2X.mp4` |

O fator entra no nome de propósito: acelerar o mesmo vídeo em fatores diferentes gera arquivos distintos, sem colisão.

## A ideia central: tom preservado

Acelerar áudio "na marra" (mexendo no sample rate) sobe o tom — voz de desenho. O filtro **`atempo`** muda só o andamento, mantendo o tom natural da voz. Os três fatores (1.2, 1.5, 2.0) cabem no range `[0.5, 2.0]` do atempo, então um único filtro resolve.

No vídeo, `setpts=PTS/FATOR` re-cronometra os frames; forçando o **mesmo fps da fonte** na saída (`-r`), o ffmpeg descarta frames uniformemente — o resultado é o vídeo mais curto, fluido, no mesmo fps de sempre.

## Fluxo de execução

### Fase 0 — Bootstrap
```bash
python3 scripts/bootstrap.py --check-only
```
Única dependência é o **ffmpeg/ffprobe** (`setpts` e `atempo` são embutidos). Se `pronto` for `false`, rode sem `--check-only` (instala via Homebrew) ou `brew install ffmpeg`.

### Fase 1 — Confirmar alvo e fator
- **Alvo:** o arquivo ou a pasta que o usuário apontou. Numa pasta, processa os vídeos diretos (`.mp4 .mov .mkv .m4v .webm`), pulando o que já tem `_ACELERADO` no nome.
- **Fator:** **1.2x é o padrão**. Se o usuário não disser a velocidade, use 1.2x. Se pedir mais rápido, `--fator 1.5` ou `--fator 2`. Gera um arquivo só, na velocidade escolhida.

### Fase 2 — Aplicar
```bash
# arquivo único, padrão 1.2x
python3 scripts/acelerar.py "<arquivo>"

# pasta inteira, 2x
python3 scripts/acelerar.py "<pasta>" --fator 2
```

### Fase 3 — Conferir e resumir
Liste o que virou `_ACELERADO_<FATOR>` (do JSON `saidas`) e confira que a duração caiu pelo fator certo (2x ≈ metade) e que o fps se manteve:
```bash
ffprobe -v error -show_entries format=duration -of default=nokey=1:noprint_wrappers=1 "<saida>"
ffprobe -v error -select_streams v:0 -show_entries stream=avg_frame_rate -of default=nokey=1:noprint_wrappers=1 "<saida>"
```

## Anti-padrões (não faça)
- **Subir o tom da voz.** Use `atempo` (preserva o tom), nunca acelerar o áudio pelo sample rate.
- **Tocar no original.** Grava ao lado, com sufixo; o original fica intacto.
- **Esquecer o fator no nome.** Sempre `_ACELERADO_<FATOR>` — senão fatores diferentes colidem.
- **Gerar mais de um arquivo por execução.** Um arquivo só, na velocidade escolhida (1.2x por padrão).
- **Dessincronizar.** Vídeo e áudio aceleram pelo MESMO fator, sempre.
- **Reprocessar um `_ACELERADO`.** A coleta de pasta já pula esses.

## Referência
O método (por que `atempo` para o tom, por que `-r` preserva o fps) está em `referencia/METODO.md`.
