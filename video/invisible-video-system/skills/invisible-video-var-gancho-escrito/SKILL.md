---
name: invisible-video-var-gancho-escrito
description: >
  Gera uma variação de gancho escrito de um vídeo combinado: substitui a IMAGEM do
  gancho por uma animação de tipografia sobre fundo preto (as palavras do gancho
  surgem sincronizadas com a fala, organizadas por frase, com ênfase nas
  palavras-chave), mantendo o ÁUDIO original; terminado o gancho, entra o
  desenvolvimento normal. O número da variação é do usuário: PERGUNTE qual VAR ele
  está produzindo (VAR1, VAR2, VAR3…) e estampe esse número no nome da saída
  (<comb>_LEGENDADO_VAR<n>.mp4). O usuário aponta os vídeos base (de preferência os
  já legendados, em LEGENDADOS/) e a skill renderiza com Remotion. Opera de
  preferência sobre o `_LEGENDADO.mp4` (não re-legenda o desenvolvimento, que já
  tem a legenda queimada e aprovada); na falta dele, usa a combinação crua e
  legenda o desenvolvimento no próprio render. NÃO transcreve: precisa do `.json`
  de timestamp por palavra (com `secoes`/`secao`) que a invisible-legenda-arquivos
  gera. Use SEMPRE que o usuário pedir "gancho escrito", "gancho animado",
  "gancho em texto", "tela de texto no gancho", "variação do gancho", "VAR1/VAR2/VAR3",
  "animar o gancho", ou apontar combinações/legendados pedindo o gancho em
  tipografia animada. Requer Node.js, npm e ffmpeg (faz bootstrap).
---

# Gancho Escrito (variação VAR&lt;n&gt;)

Você pega um vídeo combinado (gancho + desenvolvimento) e devolve uma **variação**:
o trecho do gancho deixa de mostrar a pessoa falando e passa a mostrar **o texto do
gancho animado** sobre fundo preto — palavra surgindo no instante exato em que é dita,
uma frase por vez, com as palavras-chave em destaque. O **áudio do gancho é o original**.
Quando o gancho acaba, entra o desenvolvimento como sempre.

O **número da variação é do usuário**, não desta skill. Ele está produzindo várias
versões do mesmo vídeo (gancho diferente, abertura diferente) e numera cada uma:
VAR1, VAR2, VAR3… **Sempre pergunte qual VAR este render é** antes de processar, e
estampe o número no nome da saída. Esta skill não "é a VAR1" — ela produz a VAR que
o usuário disser.

> O vídeo de origem **nunca é tocado**. A saída nasce com o nome da combinação +
> `_LEGENDADO_VAR<n>`, onde `<n>` é a variação informada (ex.: para a 2ª variação,
> `GANCHO_VAV19__DESENVOLVIMENTO_VAV23_LEGENDADO_VAR2.mp4`).

O tratamento visual é **único e fixo**: fundo preto, fonte serifada (Hoefler Text),
branco quente, ênfase em itálico negrito maior, paginação por frase. O `VAR<n>` é só
o **rótulo da variação no título** — não muda o estilo. Outros estilos de gancho
(fontes, fundos, modos de animação) são evoluções futuras desta mesma skill; não
improvise outros estilos agora.

## Como funciona (render único no Remotion)

Um render só, sem cortar/concatenar com ffmpeg. A composição `gancho-escrito`:
- toca o vídeo base do começo ao fim (é a fonte do **áudio** contínuo);
- até o **boundary** (fim do gancho), cobre a imagem com fundo preto + a tipografia;
- do boundary em diante, mostra o vídeo do desenvolvimento.

### Dois modos (a skill escolhe pelo vídeo base)

| Modo | Vídeo base | Legenda do desenvolvimento | Virada |
|---|---|---|---|
| **legendado** (preferido) | `<comb>_LEGENDADO.mp4` | já queimada e aprovada — **não re-renderiza** | corte seco |
| **crua** (fallback) | `<comb>.mp4` | desenhada no render (estilo `reels`, do `.json`) | fade curto |

Por que preferir o legendado: a tela preta cobre a legenda do gancho de qualquer jeito,
e o desenvolvimento legendado já está aprovado — reusá-lo é mais fiel e mais barato.
A skill detecta o modo pelo sufixo `_LEGENDADO` no nome (ou force com `--modo`).

## De onde vêm os dados (encadeamento)

O **JSON da combinação** (`<comb>.json`, com bloco `secoes` e `secao` por palavra) é
**sempre** necessário — mas só pelo **gancho** (onde termina + o tempo de cada palavra).
Ele é o mesmo que a [`invisible-legenda-arquivos`](../invisible-legenda-arquivos/SKILL.md)
gera e que o [sidecar de roteiro](../invisible-video-combinador/SKILL.md) enriquece com a
seção. Resolução automática do `.json`: ao lado do vídeo → pasta-pai (um `_LEGENDADO.mp4`
em `LEGENDADOS/` acha o `.json` em `COMBINAÇÕES/`) → `--json-dir` → busca recursiva em
`--buscar-em`. Se não existir em lugar nenhum, **gere antes** com a
`invisible-legenda-arquivos` na combinação (peça confirmação ao usuário) e siga.

## Fluxo de operação

1. **Bootstrap.** `python3 scripts/bootstrap.py` — garante node/npm/ffmpeg e instala o
   projeto Remotion central (`~/.invisible-video/gancho-escrito-remotion`). Idempotente.
2. **Identifique os vídeos base.** O usuário aponta a pasta (tipicamente `LEGENDADOS/`)
   ou vídeos. Se ele não apontar, procure os `_LEGENDADO.mp4`/combinações e **confirme**
   com ele antes de processar. Garanta o `.json` de cada combinação (encadeamento acima).
   **Pergunte qual variação ele está produzindo** (VAR1, VAR2, VAR3…) — esse número vai
   no nome da saída (`_VAR<n>`). Se ele não disser, pergunte; só assuma `1` se ele
   pedir explicitamente "a primeira" ou disser para usar o default. Guarde o número
   para passar adiante em `--var <n>`.
3. **Infira a ênfase (sem pedir aprovação).** Para cada **gancho distinto** (ex.: VAV19,
   VAV23…), leia o texto do gancho (do `.json`/`.md`) e escolha as palavras-chave que
   ganham destaque — **substantivos e verbos fortes, o clímax retórico de cada frase**;
   1–2 por frase, nunca artigos/preposições/conjunções. Monte um mapa
   `{ "<gancho>": "palavra1,palavra2,..." }` e salve num arquivo (ex.: `enfase.json`).
   A inferência é sua; **não** peça aprovação dela ao usuário.
4. **Prova + aprovação (SEMPRE).** Antes do lote, gere uma prova do **primeiro** gancho e
   peça aprovação do usuário (este passo sempre precisa de OK):
   - prepare os dados: `python3 scripts/preparar.py <comb>.json --video <base.mp4> --enfase "<palavras>"`
   - still da 1ª frase: na pasta central, `npx remotion still gancho-escrito out/prova.png --frame=<N>`
     (escolha um frame onde a 1ª frase já apareceu inteira) — mostre o PNG;
   - se aprovado, renderize o VAR completo desse primeiro (`aplicar.py … --var <n>`,
     com o número que o usuário deu no passo 2) e mostre o vídeo.
   Ajuste o que o usuário pedir e só então prossiga.
5. **Aplique a todos (em lanes paralelas).** Passe a variação que o usuário escolheu:
   ```bash
   python3 scripts/aplicar.py "<pasta LEGENDADOS ou COMBINAÇÕES>" \
       --var <n> --enfase-map enfase.json --lanes 2
   ```
   A skill detecta o modo por vídeo, resolve o `.json`, infere o gancho do nome
   (`GANCHO_VAVxx__…`) para puxar a ênfase do mapa, e grava cada
   `<comb>_LEGENDADO_VAR<n>.mp4` na `LEGENDADOS/`. Sem `--var`, o default é `1`.
   Monta lanes isoladas (node_modules symlinkado) e as limpa no fim. Dimensione
   `--lanes` à máquina (2 é seguro em ~10 núcleos; cada render usa ~3 núcleos).

## Scripts

| Script | Papel |
|---|---|
| `scripts/bootstrap.py` | detecta deps e instala o projeto Remotion central |
| `scripts/preparar.py` | do `<comb>.json` gera `public/hook.json` (frases do gancho + `emphasis` + `boundaryMs`) e `captions.json` (só desenvolvimento); copia o vídeo base p/ `public/video.mp4` |
| `scripts/aplicar.py` | orquestrador: detecção de modo, resolução do `.json`, ênfase por gancho, render em lanes paralelas |
| `scripts/convert_captions.mjs` | conversão WhisperX→`Caption[]` (reuso da skill de legendas) |

## Onde mora o estilo (para as variações futuras)

Toda a aparência vive em `remotion/src/`:
- `HookText.tsx` — animação do gancho: fonte (`FONT_FAMILY`), tamanhos (`SIZE_BASE`,
  `SIZE_EMPH`), cor (`COLOR`), entrada da palavra (`WORD_ENTER_FRAMES`), virada
  (`FADE_OUT_FRAMES`), paginação por frase. **É aqui que novas variações de estilo
  entram** (outras fontes, fundos, modos de animação).
- `Composition.tsx` — a composição `gancho-escrito` e o interruptor `videoJaLegendado`.
- `Captions.tsx` — presets de legenda do desenvolvimento (reuso do aplicador; modo crua).

Depois de mexer em `remotion/src/`, rode o `bootstrap.py` de novo (ele sincroniza os
fontes para o projeto central).

## Requisitos

Node.js + npm (Remotion) e ffmpeg. O `bootstrap.py` checa e orienta a instalação
(`brew install node ffmpeg`). A primeira execução instala o `node_modules` do projeto
central uma única vez.
