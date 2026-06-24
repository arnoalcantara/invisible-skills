---
name: invisible-video-var-gancho-escrito
description: >
  Gera uma variação de gancho escrito: substitui a IMAGEM do gancho por uma animação
  de tipografia sobre fundo preto (as palavras surgem sincronizadas com a fala,
  organizadas por frase, com ênfase nas palavras-chave), mantendo o ÁUDIO original.
  Dois alvos: (1) --alvo combinacao — varia o gancho DENTRO de um vídeo combinado;
  terminado o gancho, entra o desenvolvimento. (2) --alvo segmento — o clipe INTEIRO
  é um gancho isolado já otimizado (de 02_OTIMIZADOS): a tipografia cobre o clipe todo,
  sem desenvolvimento nem karaokê; o gancho variado é final por si. O número da variação
  é do usuário: PERGUNTE qual VAR ele está produzindo (VAR1, VAR2, VAR3…) e estampe esse
  número no nome da saída, ANTES do token de formato (<id>_OTIMIZADO_VAR<n>_VERTICAL.mp4).
  A saída vai pra pasta-irmã 03_PREPARADOS. No alvo combinacao, opera de preferência sobre
  o `_LEGENDADO` (não re-legenda o desenvolvimento); na falta, usa a combinação crua. NÃO
  transcreve: precisa do `.json` de timestamp por palavra (nomeado pela BASE, sem
  formato/VAR; com `secoes`/`secao` no alvo combinacao) que a invisible-legenda-arquivos
  gera. Use SEMPRE que o usuário pedir "gancho escrito", "gancho animado", "gancho em
  texto", "tela de texto no gancho", "variação do gancho", "VAR1/VAR2/VAR3", "animar o
  gancho", ou apontar segmentos/combinações pedindo o gancho em tipografia animada.
  Requer Node.js, npm e ffmpeg (faz bootstrap).
---

# Gancho Escrito (variação VAR&lt;n&gt;)

Você devolve uma **variação** em que o trecho do gancho deixa de mostrar a pessoa
falando e passa a mostrar **o texto do gancho animado** sobre fundo preto — palavra
surgindo no instante exato em que é dita, uma frase por vez, com as palavras-chave em
destaque. O **áudio é o original**.

Dois alvos:
- **`--alvo combinacao`** (default): vídeo combinado (gancho + desenvolvimento). A
  tipografia cobre só o gancho; quando ele acaba, entra o desenvolvimento como sempre.
- **`--alvo segmento`**: o clipe **inteiro** é um gancho isolado já otimizado (vindo de
  `02_OTIMIZADOS`). A tipografia cobre o clipe do começo ao fim — não há desenvolvimento
  nem karaokê. O gancho variado é **final por si**: vai direto pra `03_PREPARADOS` e segue
  pela esteira (combinador → trilha) como qualquer outro segmento pronto. É o modo da
  linha de produção nova: variar o gancho **antes** de combinar.

O **número da variação é do usuário**, não desta skill. Ele numera cada versão: VAR1,
VAR2, VAR3… **Sempre pergunte qual VAR este render é** antes de processar, e estampe o
número no nome da saída. Esta skill não "é a VAR1" — ela produz a VAR que o usuário disser.

> O vídeo de origem **nunca é tocado**. A saída nasce em `03_PREPARADOS/` com `_VAR<n>`
> inserido **antes do token de formato** (formato sempre o último token). Ex. no alvo
> segmento: `GANCHO_VAV19_OTIMIZADO_VERTICAL.mp4` → `GANCHO_VAV19_OTIMIZADO_VAR2_VERTICAL.mp4`.
> No alvo combinacao: `..._OTIMIZADO_LEGENDADO_VERTICAL.mp4` → `..._OTIMIZADO_LEGENDADO_VAR2_VERTICAL.mp4`.

O tratamento visual é **único e fixo**: fundo preto, fonte serifada (Hoefler Text),
branco quente, ênfase em itálico negrito maior, paginação por frase. O `VAR<n>` é só
o **rótulo da variação no título** — não muda o estilo. Outros estilos de gancho
(fontes, fundos, modos de animação) são evoluções futuras desta mesma skill; não
improvise outros estilos agora.

## Como funciona (render único no Remotion)

Um render só, sem cortar/concatenar com ffmpeg. A composição `gancho-escrito` se adapta
à **dimensão real** do vídeo de entrada (1080×1920 ou 1080×1080, via `parseMedia` no
`calculateMetadata`) — então rodar sobre o vertical e sobre o quadrado gera as duas
variantes no formato certo. Ela:
- toca o vídeo base do começo ao fim (é a fonte do **áudio** contínuo);
- até o **boundary**, cobre a imagem com fundo preto + a tipografia;
- do boundary em diante, mostra o vídeo (no alvo segmento o boundary = duração total,
  então a tipografia cobre o clipe inteiro e nunca revela a imagem crua).

### Alvo combinacao — dois modos de legenda (a skill escolhe pelo vídeo base)

| Modo | Vídeo base | Legenda do desenvolvimento | Virada |
|---|---|---|---|
| **legendado** (preferido) | `..._LEGENDADO_<FORMATO>.mp4` | já queimada e aprovada — **não re-renderiza** | corte seco |
| **crua** (fallback) | combinação crua | desenhada no render (estilo `reels`, do `.json`) | fade curto |

A skill detecta o modo pelo token `_LEGENDADO` no nome (ou force com `--modo`).

### Alvo segmento — sem desenvolvimento

No `--alvo segmento` não há desenvolvimento: o boundary é a duração do clipe, o
`captions.json` sai vazio e o render trata o vídeo como "já legendado" (nada de karaokê
por baixo). É o gancho em tipografia, do começo ao fim, e pronto.

## De onde vêm os dados (encadeamento)

O **JSON** (`segments[].words[]`; no alvo combinacao também `secoes`/`secao`) é **sempre**
necessário pelo **gancho** (onde termina + o tempo de cada palavra). É o mesmo que a
[`invisible-legenda-arquivos`](../invisible-legenda-arquivos/SKILL.md) gera, agora nomeado
pela **BASE** (sem formato nem VAR) — um `.json` serve vertical, quadrado e VARs. A skill
o acha removendo o token de formato/VAR do nome do clipe e procurando o irmão: ao lado do
vídeo → pasta-pai → `--json-dir` → busca recursiva em `--buscar-em`. Se não existir,
**gere antes** com a `invisible-legenda-arquivos` (peça confirmação) e siga.

## Fluxo de operação

1. **Bootstrap.** `python3 scripts/bootstrap.py` — garante node/npm/ffmpeg e instala o
   projeto Remotion central (`~/.invisible-video/gancho-escrito-remotion`). Idempotente.
2. **Identifique os vídeos base e o alvo.** No **alvo segmento** (linha de produção nova),
   o usuário aponta os clipes de gancho de `02_OTIMIZADOS` (vertical e/ou quadrado). No
   **alvo combinacao**, aponta combinações/legendados. Se ele não apontar, procure e
   **confirme** antes de processar. Garanta o `.json` da base de cada clipe (encadeamento
   acima). **Pergunte qual variação ele está produzindo** (VAR1, VAR2, VAR3…) — esse número
   vai no nome da saída (`_VAR<n>`, antes do formato). Se ele não disser, pergunte; só
   assuma `1` se ele pedir. Guarde o número para `--var <n>`.
3. **Infira a ênfase (sem pedir aprovação).** Para cada **gancho distinto** (ex.: VAV19,
   VAV23…), leia o texto do gancho (do `.json`/`.md`) e escolha as palavras-chave que
   ganham destaque — **substantivos e verbos fortes, o clímax retórico de cada frase**;
   1–2 por frase, nunca artigos/preposições/conjunções. Monte um mapa
   `{ "<gancho>": "palavra1,palavra2,..." }` e salve num arquivo (ex.: `enfase.json`).
   A inferência é sua; **não** peça aprovação dela ao usuário.
4. **Prova + aprovação (SEMPRE).** Antes do lote, gere uma prova do **primeiro** gancho e
   peça aprovação do usuário (este passo sempre precisa de OK):
   - prepare os dados: `python3 scripts/preparar.py <base>.json --video <clipe.mp4> --alvo <alvo> --enfase "<palavras>"`
   - still da 1ª frase: na pasta central, `npx remotion still gancho-escrito out/prova.png --frame=<N>`
     (escolha um frame onde a 1ª frase já apareceu inteira) — mostre o PNG;
   - se aprovado, renderize o VAR completo desse primeiro (`aplicar.py … --alvo <alvo> --var <n>`)
     e mostre o vídeo.
   Ajuste o que o usuário pedir e só então prossiga.
5. **Aplique a todos (em lanes paralelas).** Passe o alvo e a variação escolhidos:
   ```bash
   # alvo segmento (clipes de gancho de 02_OTIMIZADOS):
   python3 scripts/aplicar.py "<02_OTIMIZADOS>" \
       --alvo segmento --var <n> --enfase-map enfase.json --lanes 2
   # alvo combinacao (combinações/legendados):
   python3 scripts/aplicar.py "<pasta>" \
       --alvo combinacao --var <n> --enfase-map enfase.json --lanes 2
   ```
   A skill resolve o `.json` da base, infere o gancho do nome (`GANCHO_VAVxx…`) para puxar
   a ênfase do mapa, e grava cada saída em `03_PREPARADOS/` com `_VAR<n>` antes do formato.
   Sem `--var`, o default é `1`. Monta lanes isoladas (node_modules symlinkado) e as limpa
   no fim. Dimensione `--lanes` à máquina (2 é seguro em ~10 núcleos; cada render usa ~3).

## Scripts

| Script | Papel |
|---|---|
| `scripts/bootstrap.py` | detecta deps e instala o projeto Remotion central |
| `scripts/preparar.py` | do `.json` gera `public/hook.json` (frases do gancho + `emphasis` + `boundaryMs`) e `captions.json` (desenvolvimento; vazio no alvo segmento); copia o vídeo p/ `public/video.mp4`. `--alvo segmento` usa a duração do vídeo como boundary |
| `scripts/aplicar.py` | orquestrador: `--alvo`, detecção de modo, resolução do `.json` pela base (strip de formato/VAR), ênfase por gancho, nome com `_VAR<n>` antes do formato, saída em `03_PREPARADOS`, render em lanes paralelas |
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
