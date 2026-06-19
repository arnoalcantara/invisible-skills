# Método — Combinador (gancho × desenvolvimento)

Conhecimento fechado em sessão real com o Arno. Editou aqui, mudou o comportamento da skill.

## 1. Julgamento da matriz: promessa × tipo de abertura

A regra de ouro é **casar pelo que o gancho PROMETE com o tipo de abertura do desenvolvimento — nunca pela forma gramatical do gancho.**

- **Gancho** — classifique pela promessa/continuação que ele pede: pergunta lida em voz alta, pergunta retórica, ordem ("presta atenção nisso"), promessa de mostrar algo ("vou te mostrar a vida dos meus alunos").
- **Desenvolvimento** — classifique pelo **tipo de abertura**: dor, revelação, contestação, prova social/depoimento.

Um cruzamento é **fluido** quando o desenvolvimento abre como continuação natural da promessa do gancho: sem buraco lógico, sem repetir o que o gancho já disse, sem deixar a promessa sem cumprir.

### O erro a não repetir
Numa sessão, um gancho que promete "a vida dos meus alunos" foi reprovado contra um desenvolvimento que abre com **depoimento de aluno**, por uma regra gramatical cega (o gancho "não era pergunta"). Está errado: a promessa casa perfeitamente com o depoimento. **A promessa manda, não a gramática.**

## 2. Rigor e pares nativos

- Default: **aprovar só os fluidos.** ⚠️ para limítrofes (com ressalva escrita); ❌ para os que não casam.
- **Pares nativos** (gancho + desenvolvimento extraídos do mesmo vídeo original) são combinações válidas — inclua sempre.
- O usuário tem a palavra final: pode forçar uma célula ⚠️/❌ ou cortar uma ✅.

## 3. Por que normalizar ANTES de concatenar

`concat -c copy` (sem reencode) exige que todas as partes tenham specs idênticas: mesma resolução, fps, pix_fmt, códec, sample rate e nº de canais. Os cortes vêm de brutas diferentes — podem ser 4K vs 1080, mono vs stereo, mp4 vs mov. Concatenar specs mistas por copy quebra ou gera vídeo corrompido.

**Solução validada:** normalizar **cada corte uma vez** para o alvo (reencode com `scale+pad+setsar=1` + fps + aformat de áudio), e só então concatenar por `-c copy` — rápido e sem segundo reencode. Normalizar é o único reencode; o concat é cópia.

### Aspect ratio
`scale=W:H:force_original_aspect_ratio=decrease,pad=W:H:(ow-iw)/2:(oh-ih)/2,setsar=1` — encaixa preservando proporção, com barras quando a entrada não for 9:16. `setsar=1` evita SAR herdado que distorceria.

## 4. Specs do alvo

- **Padrão:** Full HD vertical 1080×1920, 30fps, HEVC (libx265 CRF20, `-tag:v hvc1`), AAC 48kHz stereo, `.mp4`.
- **Alternativas oferecidas:** 4K (2160×3840); MOV; resolução nativa (a maior entre os dois cortes, sem rebaixar); H.264/x264.

## 5. Nomenclatura
- Pasta `COMBINAÇÕES/` na raiz do projeto.
- `GANCHO_VAV<xx>__DESENVOLVIMENTO_VAV<yy>.<ext>`.
