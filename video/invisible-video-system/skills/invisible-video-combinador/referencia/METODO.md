# Método — Combinador (cadeia de segmentos)

Conhecimento fechado em sessão real com o Arno. Editou aqui, mudou o comportamento da skill.

## 0. Modelo: segmentos N-lados, dirigido pelo usuário

A peça final é a **concatenação ordenada** de um corte de cada segmento escolhido.
Um segmento é um grupo de cortes da mesma sessão. Os nomes são **livres** e os
segmentos podem ser **dois ou mais**:

- Anúncio curto (padrão Invisible): `GANCHOS/` → `DESENVOLVIMENTOS/` (→ `CTAS/`).
- VSL: `LEAD/` → `HISTORIA/` → `OFERTA/` → `FECHAMENTO/`.
- O que o projeto tiver. **Nunca travar em nomes.** `GANCHOS/DESENVOLVIMENTOS/CTAS`
  são só os padrões sugeridos (e a ordem retórica de auto-descoberta).

### Dois layouts no disco (o descobridor cobre os dois)

- **Subpastas:** cada segmento é uma pasta. `modo: subpastas`.
- **Mesma pasta:** todos os cortes soltos numa pasta só. Aqui o segmento de cada
  arquivo se lê do **nome**: o nome sempre carrega o **rótulo da sessão** (GANCHO,
  DESENVOLVIMENTO...) e o **código/número** (19, VAV19, 28...), em qualquer ordem e
  com qualquer separador (`_`, `-`, `.`, espaço). O descobridor agrupa por rótulo e
  extrai o código à parte. `modo: mesma_pasta`. Rótulos fora dos conhecidos entram
  por `--rotulos`. Tokens de processamento como `OTIMIZADO` são ignorados na leitura do código.

O código é extraído como `VAVxx` (regex de letras+dígitos) ou, na falta, como número
solto delimitado por não-dígito (tolerando `_`, que `\b` não delimita). É o mesmo
código que casa os **pares nativos** entre segmentos.

**Quem dirige é o usuário.** Na execução ele determina:
1. quais segmentos entram;
2. a ordem da cadeia (não se inverte);
3. quais segmentos **variam** (cruzam) e quais ficam **fixos/nativos**.

- **Varia:** todos os cortes do segmento entram no cruzamento.
- **Fixo (nativo):** o corte que tem o **mesmo código** da peça base acompanha sem
  cruzar. Ex.: "varia gancho × desenvolvimento, mas a OFERTA é a nativa de cada vídeo".

A combinação mais usual é só gancho × desenvolvimento — mas é sempre o usuário que diz.

## 1. Julgamento: promessa × tipo de abertura (par-a-par)

A regra de ouro: **casar pelo que a peça anterior PROMETE com o tipo de abertura da
peça seguinte — nunca pela forma gramatical.**

- **Lado que abre a transição** — classifique pela promessa/continuação que pede:
  pergunta lida, pergunta retórica, ordem, promessa de mostrar algo.
- **Lado que recebe** — classifique pelo tipo de abertura: dor, revelação,
  contestação, prova social/depoimento.

Uma transição é **fluida** quando o lado seguinte abre como continuação natural da
promessa do anterior: sem buraco lógico, sem repetir o que já foi dito, sem deixar
promessa sem cumprir.

**Com 3+ segmentos:** julgue **par-a-par cada transição vizinha que vai variar**
(gancho→desenvolvimento, depois desenvolvimento→CTA). A cadeia é aprovada quando
toda transição variável é fluida. Transições para um segmento **fixo nativo** não se
julgam — vieram juntas do mesmo vídeo. Par-a-par escala; evita explodir a análise no
produto cartesiano de N segmentos.

### O erro a não repetir
Um gancho que promete "a vida dos meus alunos" foi reprovado contra um desenvolvimento
que abre com **depoimento de aluno**, por regra gramatical cega ("não era pergunta").
Errado: a promessa casa com o depoimento. **A promessa manda, não a gramática.**

## 2. Rigor e pares nativos

- Default: **aprovar só os fluidos.** ⚠️ para limítrofes (com ressalva escrita); ❌
  para os que não casam.
- **Pares nativos** (cortes de mesma origem, mesmo código) são válidos — inclua sempre.
- O usuário tem a palavra final: força uma ⚠️/❌ ou corta uma ✅.

## 3. Código nativo

O código no nome do corte (ex.: VAV19) identifica a origem. Cortes de segmentos
diferentes com o mesmo código vieram do mesmo vídeo → peça nativa. É o que permite o
modo "segmento fixo nativo": para cada peça base, pega-se o corte de mesmo código no
segmento fixo.

## 4. Por que normalizar ANTES de concatenar

`concat -c copy` (sem reencode) exige specs idênticas em todas as partes: resolução,
fps, pix_fmt, códec, sample rate, nº de canais. Os cortes vêm de brutas diferentes —
4K vs 1080, mono vs stereo, mp4 vs mov. Concatenar specs mistas por copy quebra ou
corrompe.

**Solução validada:** normalizar **cada corte uma vez** para o alvo (reencode com
`scale+pad+setsar=1` + fps + aformat), e só então concatenar por `-c copy` — rápido,
sem segundo reencode. Reusar a normalização de um corte entre todas as cadeias em que
ele aparece.

### Aspect ratio
`scale=W:H:force_original_aspect_ratio=decrease,pad=W:H:(ow-iw)/2:(oh-ih)/2,setsar=1`
— encaixa preservando proporção, barras quando a entrada não for 9:16. `setsar=1`
evita SAR herdado que distorceria.

## 5. Specs do alvo

- **Padrão:** Full HD vertical 1080×1920, 30fps, HEVC (libx265 CRF20, `-tag:v hvc1`),
  AAC 48kHz stereo, `.mp4`.
- **Alternativas:** 4K (2160×3840); MOV; resolução nativa (a maior entre os cortes da
  cadeia, sem rebaixar); H.264/x264.

## 6. Nomenclatura
- Pasta `04_COMBINADOS/` (pasta-irmã, etapa da linha). A matriz vai em `04_COMBINADOS/MATRIZ.md`.
- Rótulos dos segmentos (singular, MAIÚSCULO) + código (+ `_VAR<n>` no segmento que varia),
  na ordem da cadeia, unidos por `__`, com o **token de formato sempre no fim**:
  `GANCHO_VAV19_VAR1__DESENV_VAV57_VERTICAL.mp4`.

## 7. Variantes por formato e VAR (expansão cartesiana)

O `descobrir_cortes.py` agrupa, por segmento+código, todas as variantes do mesmo corte: por formato (`VERTICAL`/`QUADRADO`), o clipe `base` e o dicionário de `vars` (`{1: …, 2: …}`). Nem formato nem VAR é um corte retórico novo — são variantes do mesmo corte (mesmo áudio/texto). Por quê e como:

- **Julga uma vez.** O encaixe retórico (promessa × abertura) é sobre o **áudio**, idêntico entre formatos e VARs. A matriz é julgada só sobre o `VERTICAL` `base` (não-VAR) e vale pra todos.
- **Salva a matriz antes.** Antes de gerar qualquer vídeo, a `MATRIZ.md` é escrita em `04_COMBINADOS` com o esquema, as células ✅/⚠️/❌ justificadas e a contagem de peças já expandida. Aprovação trava o gate.
- **Expande na hora de combinar.** Para cada par aprovado, para cada formato presente em **todos** os segmentos da cadeia, o produto cartesiano das variantes por segmento (`{base} ∪ {VARs}`) vira as peças concretas. Ex.: GANCHO base+VAR1 × DESENV base → 2 peças por formato.
- **Não cruza formato.** Vertical com vertical, quadrado com quadrado — `concat -c copy` direto (os quadrados saem do otimizador em 1080×1080). Formato ausente em algum segmento da cadeia → pula esse formato e avisa.
- **Um `.md` só.** O roteiro é o mesmo entre formatos/VARs (mesmo áudio). Só a peça vertical base gera `.md`; nenhum `.md` por formato nem por VAR.
