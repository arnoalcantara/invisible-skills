---
name: invisible-denoiser
description: >
  Reduz o ruído de fundo do áudio de um vídeo (ou de uma pasta inteira) com o filtro afftdn do ffmpeg, sem mexer em timbre nem dinâmica — só limpa chiado, hiss e ruído constante. Trabalha IN-PLACE: não gera arquivo novo, processa e salva com o sufixo _DENOISER no fim do nome, substituindo o original; o vídeo é copiado sem recompressão (só o áudio é reprocessado). Independente — roda em qualquer ponto da esteira (bruta derivada, otimizado, combinação, legendado). Três níveis: leve (nr=6), médio (nr=12) e forte (nr=21, padrão). NÃO faz EQ nem compressão (testado e reprovado em gravação limpa: soa artificial). Por segurança recusa rodar nas BRUTAS (fonte de verdade) sem --forcar. Use quando o usuário pedir "tira o ruído", "limpa o áudio", "reduz o chiado", "denoise", "limpa o som desse vídeo", "tira o barulho de fundo", ou apontar uma pasta pedindo limpeza de ruído. Requer ffmpeg (faz bootstrap).
---

# Denoiser (limpeza de ruído do áudio)

Reduz ruído de fundo do áudio com o filtro **`afftdn`** do ffmpeg. Só limpa ruído — **não** mexe em timbre (EQ) nem dinâmica (compressão). Essa decisão é deliberada: tratamento pesado de voz foi testado em material real e reprovado de ouvido (em gravação limpa, EQ+compressão soam "abertos", artificiais). O que agrega é o denoise discreto.

## Comportamento — IN-PLACE, sem arquivo novo

A skill **não cria um arquivo a mais**. Para cada alvo:
1. Processa o áudio com `afftdn`, copiando o vídeo sem recompressão (`-c:v copy`).
2. Salva com **`_DENOISER` no fim do nome** (`foo.mp4` → `foo_DENOISER.mp4`).
3. **Remove o original.** Sobra um arquivo só, no mesmo lugar, renomeado.

O sufixo acumula no fim, na convenção da esteira: `..._OTIMIZADO_DENOISER.mp4`, `..._LEGENDADO_DENOISER.mp4`.

> **Proteção das BRUTAS.** Como substitui o original, a skill **recusa** por padrão quando o alvo está numa pasta `BRUTAS/` (fonte de verdade, irreproduzível). Só roda lá com `--forcar`, e só se houver cópia. Em qualquer outro ponto (derivados) roda livre.

## Níveis

`nr` é a redução de ruído em dB do `afftdn`:

| Nível | `nr` | Quando |
|---|---|---|
| `leve` | 6 | ruído sutil; máxima preservação |
| `medio` | 12 | padrão do ffmpeg |
| **`forte`** | **21** | **default — validado de ouvido no Lote 01** |

Em gravação já limpa a diferença entre níveis é pequena; o forte foi o escolhido como padrão. Denoise excessivo pode dar timbre metálico/abafado — se acontecer, baixe o nível.

## Fluxo de execução

### Fase 0 — Bootstrap
```bash
python3 scripts/bootstrap.py --check-only
```
Garante ffmpeg/ffprobe. O `afftdn` é embutido no ffmpeg — não há modelo nem venv a instalar.

### Fase 1 — Confirmar o alvo e o nível
- Alvo: o arquivo ou a pasta que o usuário apontou. Numa pasta, processa toda a mídia (`.mp4 .mov .mkv .m4v .webm` e áudios), pulando o que já tem `_DENOISER` no nome.
- Nível: padrão `forte`. Se o usuário pediu mais sutil, use `--nivel medio` ou `--nivel leve` (ou `--nr N` direto).
- Se o alvo está em `BRUTAS/`, **avise** que vai substituir a fonte de verdade e só prossiga com `--forcar` após o ok.

### Fase 2 — Rodar
```bash
# arquivo único, padrão forte
python3 scripts/denoiser.py "<arquivo>"

# pasta inteira, nível médio
python3 scripts/denoiser.py "<pasta>" --nivel medio
```

### Fase 3 — Resumo
Liste o que virou `_DENOISER` (do JSON `saidas`), confirme que o vídeo não foi recodificado (`-c:v copy`) e, se útil, compare o piso de ruído antes/depois:
```bash
ffmpeg -hide_banner -nostats -i "<arquivo>" -af astats=measure_overall=Noise_floor -f null - 2>&1 | grep "Noise floor"
```

## Anti-padrões (não faça)
- **Adicionar EQ ou compressão.** Testado e reprovado — esta skill é só denoise.
- **Gerar arquivo novo / pasta nova.** É in-place, sufixo `_DENOISER`, original removido.
- **Recodificar o vídeo.** Sempre `-c:v copy`; só o áudio é tocado.
- **Rodar nas BRUTAS sem avisar.** Recusa por padrão; só com `--forcar` e cópia.
- **Reprocessar um `_DENOISER`.** A coleta de pasta já pula esses.

## Referência
O método e o que foi testado/descartado estão em `referencia/METODO.md`.
