---
name: invisible-video-combinador
description: >
  Combina cortes de SEGMENTOS de roteiro (saídas da invisible-video-bruto-desmembrador) para gerar peças novas — anúncios, VSLs — concatenando um corte de cada segmento numa cadeia ordenada. Os segmentos são pastas de nomes LIVRES (padrão Invisible: GANCHOS, DESENVOLVIMENTOS, CTAS; mas pode ser LEAD, HISTORIA, OFERTA, FECHAMENTO ou o que o projeto tiver), e podem ser DOIS OU MAIS. O usuário dirige o esquema: quais segmentos entram, em que ordem, quais VARIAM (cruzam) e quais ficam FIXOS (a peça nativa de cada origem). A skill transcreve os cortes (com cache), julga o encaixe retórico de cada transição que vai variar, monta a matriz justificada (✅/⚠️/❌), pede aprovação, normaliza para um alvo comum e concatena. Use quando o usuário pedir "combina os cortes", "cruza gancho × desenvolvimento", "monta os anúncios", "varia o gancho mantendo a oferta nativa", "gera as combinações de VAV", "monta as VSLs combinando as seções". Saída padrão Full HD vertical MP4 em COMBINAÇÕES/. Requer ffmpeg e WhisperX (faz bootstrap).
---

# Combinador de Vídeo (cadeia de segmentos)

Você combina cortes de **segmentos** de roteiro — as saídas da `invisible-video-bruto-desmembrador` — concatenando um corte de cada segmento numa **cadeia ordenada** para gerar peças novas (anúncios curtos, VSLs longas).

Um segmento é uma pasta de cortes. O padrão Invisible é `GANCHOS/`, `DESENVOLVIMENTOS/`, `CTAS/`, mas **os nomes são livres e os segmentos podem ser dois ou mais** — uma VSL pode ter `LEAD/`, `HISTORIA/`, `OFERTA/`, `FECHAMENTO/`. Não trave em nome nenhum.

**Quem dirige o esquema é o usuário.** Ele decide, na execução: quais segmentos entram, em que ordem se concatenam, quais **variam** (cruzam, gerando combinações) e quais ficam **fixos/nativos** (acompanham a peça de origem, sem cruzar).

## Conceitos

- **Segmento** — uma pasta de cortes (GANCHOS, DESENVOLVIMENTOS, OFERTA...). Nome livre.
- **Cadeia** — a ordem em que os segmentos se concatenam. Ex.: gancho → desenvolvimento → CTA. Definida/confirmada pelo usuário; **não se inverte**.
- **Código nativo** — o código no nome do corte (ex.: VAV19). Cortes de segmentos diferentes com o **mesmo código** vieram do **mesmo vídeo de origem** → são a peça nativa daquele vídeo.
- **Eixo que varia × segmento fixo:**
  - **Varia** — todos os cortes daquele segmento entram no cruzamento.
  - **Fixo (nativo)** — o corte daquele segmento é o que tem o **mesmo código** da peça base; não cruza, acompanha. Ex.: "varia gancho × desenvolvimento, mas a OFERTA é a nativa de cada vídeo".

## Princípio crítico de julgamento (não esquecer)

Case pelo que a peça anterior **PROMETE** × o **tipo de abertura** da peça seguinte — **NÃO pela forma gramatical.** Um gancho que promete "vou te mostrar a vida dos meus alunos" casa com um desenvolvimento que abre com depoimento de aluno, mesmo sem ser pergunta. (Erro real de uma sessão: reprovar gancho+depoimento por regra gramatical cega.)

Com mais de dois segmentos, julgue **par-a-par cada transição vizinha que vai variar** (gancho→desenvolvimento, depois desenvolvimento→CTA). A cadeia é fluida quando toda transição variável é fluida. Transições para um segmento fixo nativo não precisam de julgamento (já vieram juntas do mesmo vídeo).

## Fluxo de execução

### Fase 0 — Bootstrap
`python3 scripts/bootstrap.py --check-only`. Garante ffmpeg + WhisperX. Se o modelo não estiver em cache, avise o download de ~1.5GB na 1ª transcrição.

### Fase 1 — Descobrir os segmentos
`python3 scripts/descobrir_cortes.py "<pasta_projeto>"`. A skill lista TODAS as subpastas com vídeo como segmentos candidatos, marcando as de nome conhecido e ordenando por ordem retórica natural. Mostre ao usuário os segmentos achados (nome, nº de cortes, códigos).

### Fase 2 — Definir o esquema de combinação (DIRIGIDO PELO USUÁRIO)
**Pergunte explicitamente** — não assuma. Confirme:
1. **Quais segmentos** entram na peça.
2. **A ordem** da cadeia (concatenação). Sugira a ordem retórica, mas confirme.
3. **Quais variam e quais ficam fixos (nativos).** Ex.: "varia GANCHOS × DESENVOLVIMENTOS; OFERTA fixa na nativa de cada vídeo".

Se o usuário não quiser usar a auto-descoberta, ele pode apontar os segmentos na ordem:
`python3 scripts/descobrir_cortes.py "<projeto>" --segmentos GANCHOS DESENVOLVIMENTOS OFERTA`

A combinação mais usual é só **gancho × desenvolvimento** — mas é o usuário que determina, sempre.

**Cortes já otimizados.** Otimizar os cortes de segmento ANTES de combinar é a ordem preferível (um reencode só; a combinação vira cópia). Se o usuário fez isso com a `invisible-video-otimizador`, os cortes podem estar numa subpasta `OTIMIZADOS/` de cada segmento — aponte-os direto: `--segmentos GANCHOS/OTIMIZADOS DESENVOLVIMENTOS/OTIMIZADOS`. O sufixo `__OTIMIZADO` não atrapalha: o código de origem (VAV19) é extraído mesmo assim, e os pares nativos seguem casando.

### Fase 3 — Transcrever os cortes que serão julgados (com cache)
Só os segmentos que **variam** precisam de transcrição (os fixos nativos não se julgam). Para cada corte desses:
```bash
python3 scripts/transcrever.py "<corte>" --whisperx-bin <do bootstrap> \
    --cache-dir "<pasta_projeto>/.transcricao/wx_out"
```
Para a matriz importa só o texto; a borda não. Reusa cache (chave nome+tamanho+mtime).

### Fase 4 — Analisar e propor a matriz
Classifique cada corte dos segmentos que variam:
- O que ele **promete** / qual continuação pede (se for o lado que abre a transição).
- O **tipo de abertura** — dor, revelação, contestação, prova social/depoimento (se for o lado que recebe).

Julgue **par-a-par** cada transição variável. Monte a matriz justificada: ✅ (fluido) / ⚠️ (limítrofe, com ressalva escrita) / ❌ (não casa), **com o porquê de cada célula**. Para cadeias de 3+ que variam em mais de uma transição, mostre a matriz de cada transição.

Inclua sempre os **pares nativos** (mesma origem) como combinações válidas.

Diga quantas peças isso gera. Deixe explícito: "Nada foi gerado ainda. Confirma este esquema e esta matriz?" O usuário pode forçar ⚠️/❌ ou cortar ✅.

### Fase 5 — Config de saída
Pergunte, oferecendo o default entre colchetes:
- **[Full HD vertical 1080×1920, 30fps, HEVC/x265 CRF20, AAC 48k stereo, .mp4]** ← padrão.
- Alternativas: **4K** (2160×3840), **MOV**, **resolução nativa** (a maior entre os cortes da cadeia, sem rebaixar), **H.264/x264**.

### Fase 6 — Normalizar e montar
`concat -c copy` quebra com specs mistas. Por isso: **normalize cada corte uma vez** para o alvo, depois concatene por copy. Reuse a normalização de um corte entre todas as cadeias em que ele aparece.

Para cada cadeia aprovada (corte do segmento 1, do segmento 2, ... do segmento N, **na ordem da cadeia**):
1. Normalize cada corte ainda não normalizado para este alvo:
```bash
python3 scripts/normalizar.py "<corte>" --out "<tmp>/<corte>.mp4" \
    --largura 1080 --altura 1920 --fps 30 --vcodec libx265 --crf 20 \
    --sample-rate 48000 --canais 2
```
2. Concatene **na ordem da cadeia** (combinar.py aceita N partes):
```bash
python3 scripts/combinar.py "<seg1_norm>" "<seg2_norm>" "<segN_norm>" \
    --out "<projeto>/COMBINAÇÕES/<nome_da_peça>.mp4"
```

### Fase 7 — Resumo
Liste as peças geradas em `COMBINAÇÕES/`, quantas e por qual esquema, e aponte 1–2 decisões representativas da matriz (de preferência uma ⚠️).

## Pontos de confirmação
1. Segmentos descobertos. 2. **Esquema** (quais, ordem, varia×fixo). 3. Matriz justificada. 4. Config de saída. 5. Resumo final.

## Nomenclatura
- Pasta: `COMBINAÇÕES/` na raiz do projeto.
- Arquivo: os **rótulos dos segmentos com seus códigos, na ordem da cadeia**, separados por `__`. Use o rótulo do segmento (singular, MAIÚSCULO) + código do corte:
  - duas peças: `GANCHO_VAV19__DESENVOLVIMENTO_VAV57.mp4`
  - três: `GANCHO_VAV19__DESENVOLVIMENTO_VAV57__OFERTA_VAV19.mp4`
  - nomes livres: `LEAD_VSL03__HISTORIA_VSL07__OFERTA_VSL03.mp4`

## Anti-padrões (não faça)
- Travar em GANCHOS/DESENVOLVIMENTOS — os segmentos são de nome livre e podem ser 2 ou mais.
- Decidir o esquema sozinho — quem diz o que varia, o que é fixo e a ordem é o **usuário**.
- Inverter a ordem da cadeia.
- Reprovar por **forma gramatical** (a promessa é que manda).
- Concatenar sem normalizar antes (specs mistas quebram o `-c copy`).
- Gerar antes da aprovação da matriz.
- Transcrever segmentos fixos nativos à toa (não se julgam).
- Rebaixar resolução quando o usuário pediu "nativa".

## Referência
O método de julgamento (par-a-par, promessa × abertura), o modelo de segmentos N-lados e as razões técnicas (normalizar antes de concatenar, specs do alvo) estão em `referencia/METODO.md`.
