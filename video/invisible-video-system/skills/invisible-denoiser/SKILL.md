---
name: invisible-denoiser
description: >
  Reduz o ruído de fundo do áudio de um vídeo (ou de uma pasta inteira) com o filtro afftdn do ffmpeg, sem mexer em timbre nem dinâmica — só limpa chiado, hiss e ruído constante. Trabalha IN-PLACE e NÃO muda o nome: processa e substitui o original no mesmo nome (o arquivo limpo fica no lugar do antigo); o vídeo é copiado sem recompressão (só o áudio é reprocessado). Não há sufixo nem marca no nome — a skill faz o serviço e só avisa no fim que rodou. Independente — roda em qualquer ponto da esteira (bruta derivada, otimizado, combinação, legendado). Três níveis: leve (nr=6), médio (nr=12) e forte (nr=21, padrão). NÃO faz EQ nem compressão (testado e reprovado em gravação limpa: soa artificial). Por segurança recusa rodar nas BRUTAS (fonte de verdade) sem --forcar. Use quando o usuário pedir "tira o ruído", "limpa o áudio", "reduz o chiado", "denoise", "limpa o som desse vídeo", "tira o barulho de fundo", ou apontar uma pasta pedindo limpeza de ruído. Requer ffmpeg (faz bootstrap).
---

# Denoiser (limpeza de ruído do áudio)

Reduz ruído de fundo do áudio com o filtro **`afftdn`** do ffmpeg. Só limpa ruído — **não** mexe em timbre (EQ) nem dinâmica (compressão). Essa decisão é deliberada: tratamento pesado de voz foi testado em material real e reprovado de ouvido (em gravação limpa, EQ+compressão soam "abertos", artificiais). O que agrega é o denoise discreto.

## Comportamento — IN-PLACE, mesmo nome

A skill **não cria arquivo novo nem muda o nome**. Para cada alvo:
1. Processa o áudio com `afftdn`, copiando o vídeo sem recompressão (`-c:v copy`).
2. Escreve num temp e **substitui o original no mesmo nome** (`foo.mp4` continua `foo.mp4`).

Nenhum sufixo, nenhuma marca: o arquivo limpo ocupa o lugar do antigo. O nome de quem vem da esteira (`..._OTIMIZADO_VERTICAL.mp4` etc.) fica intacto — por isso o denoiser não atrapalha o contrato de nomes das outras skills.

> **Sem marca = sem idempotência por nome.** Como o nome não muda, a skill não tem como saber se um arquivo já passou pelo denoiser. Rodar de novo aplica o filtro outra vez sobre o já-limpo (em fonte limpa o efeito da 2ª passada é pequeno, mas existe). Rode uma vez por arquivo.

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
- Alvo: o arquivo ou a pasta que o usuário apontou. Numa pasta, processa **toda** a mídia (`.mp4 .mov .mkv .m4v .webm` e áudios) — como não há marca no nome, não pula nada; aponte só o que ainda não foi tratado.
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
Avise quais arquivos passaram pelo denoiser (do JSON `saidas` — os caminhos seguem com o mesmo nome), confirme que o vídeo não foi recodificado (`-c:v copy`) e, se útil, compare o piso de ruído antes/depois:
```bash
ffmpeg -hide_banner -nostats -i "<arquivo>" -af astats=measure_overall=Noise_floor -f null - 2>&1 | grep "Noise floor"
```

## Anti-padrões (não faça)
- **Adicionar EQ ou compressão.** Testado e reprovado — esta skill é só denoise.
- **Gerar arquivo novo / pasta nova / mudar o nome.** É in-place, mesmo nome; o limpo substitui o original.
- **Recodificar o vídeo.** Sempre `-c:v copy`; só o áudio é tocado.
- **Rodar nas BRUTAS sem avisar.** Recusa por padrão; só com `--forcar` e cópia.
- **Rodar duas vezes no mesmo arquivo.** Sem marca no nome, não há como pular o já-tratado — aponte só mídia que ainda não passou.

## Referência
O método e o que foi testado/descartado estão em `referencia/METODO.md`.
