---
name: invisible-video-combinador
description: >
  Combina ganchos × desenvolvimentos (cortes da invisible-video-bruto-desmembrador) para gerar anúncios novos — mas só os cruzamentos que fazem sentido retórico, não cegamente. Transcreve cada corte (com cache), entende o que cada gancho promete e como cada desenvolvimento abre, monta uma MATRIZ de combinação justificada (✅/⚠️/❌ com o porquê de cada célula), pede aprovação, normaliza os cortes para um alvo comum e concatena. Use quando o usuário pedir "combina os ganchos com os desenvolvimentos", "cruza gancho × desenvolvimento", "monta os anúncios combinando os cortes", "gera as combinações de VAV". Saída padrão Full HD vertical MP4 em COMBINAÇÕES/. Requer ffmpeg e WhisperX (faz bootstrap).
---

# Combinador de Vídeo (gancho × desenvolvimento)

Você combina **ganchos** e **desenvolvimentos** — os cortes que a `invisible-video-bruto-desmembrador` produziu — para gerar anúncios novos. Cada gancho cruzado com cada desenvolvimento daria N×M vídeos, mas você **não cruza cegamente**: aprova só os pares que se encaixam retoricamente, e propõe a matriz para o usuário antes de gerar qualquer coisa.

## Princípio crítico (não esquecer)

Case pelo que o gancho **PROMETE** × o **tipo de abertura** do desenvolvimento — **NÃO pela forma gramatical do gancho.** Um gancho que promete "vou te mostrar a vida dos meus alunos" casa perfeitamente com um desenvolvimento que abre com depoimento de aluno, mesmo que gramaticalmente não seja uma pergunta. (Erro real de uma sessão: reprovar gancho+depoimento por regra gramatical cega.)

## Fluxo de execução

### Fase 0 — Bootstrap
`python3 scripts/bootstrap.py --check-only`. Garante ffmpeg + WhisperX (venv central). Se faltar, rode sem `--check-only`. Se o JSON disser que o modelo não está em cache, avise que a 1ª transcrição baixa ~1.5GB.

### Fase 1 — Descobrir os cortes
`python3 scripts/descobrir_cortes.py "<pasta_projeto>"`. Acha `GANCHOS/` e `DESENVOLVIMENTOS/` (ou use `--ganchos`/`--desenvolvimentos` se o usuário apontar caminhos). Lista cada corte com seu código (VAV19, VAV23...). **Confirme com o usuário** os cortes descobertos antes de transcrever.

### Fase 2 — Transcrever cada corte (com cache)
Para CADA gancho e CADA desenvolvimento, rode:
```bash
python3 scripts/transcrever.py "<corte>" --whisperx-bin <do bootstrap> \
    --cache-dir "<pasta_projeto>/.transcricao/wx_out"
```
Para a matriz só importa o texto — a borda não. **Não precisa de alinhamento por palavra aqui**; basta o texto dos segmentos. Reusa cache se já houver transcrição do corte (chave nome+tamanho+mtime).

### Fase 3 — Análise da matriz (seu trabalho, não de script)
Leia as transcrições e classifique:
- **Cada gancho:** o que ele **promete** / qual continuação pede (pergunta lida, pergunta retórica, ordem, promessa de mostrar algo...).
- **Cada desenvolvimento:** o **tipo de abertura** — dor, revelação, contestação, prova social/depoimento.

Julgue cada cruzamento N×M por **encaixe retórico**: o desenvolvimento abre como continuação natural daquele gancho — sem buraco lógico, sem repetir o que o gancho já disse, sem deixar promessa do gancho sem cumprir.

Rigor: **aprovar só os fluidos** (default). Inclua os **pares nativos** (gancho + desenvolvimento do mesmo vídeo) como combinações válidas.

### Fase 4 — Propor a matriz e pedir aprovação
Apresente uma **tabela justificada**: linhas = ganchos, colunas = desenvolvimentos, célula = ✅ (aprovado) / ⚠️ (limítrofe, com ressalva) / ❌ (não casa), **com o porquê de cada célula**. Diga quantas combinações isso gera. Deixe explícito: "Nada foi gerado ainda. Confirma esta matriz?" O usuário pode **forçar** células ⚠️/❌ ou **cortar** células ✅.

### Fase 5 — Config de saída
Pergunte a config, oferecendo o **default** entre colchetes:
- **[Full HD vertical 1080×1920, 30fps, HEVC/x265 CRF20, AAC 48k stereo, .mp4]** ← padrão.
- Alternativas: **4K** (2160×3840), **MOV**, **resolução nativa** (a maior entre os dois cortes, sem rebaixar), **H.264/x264**.

### Fase 6 — Normalizar e montar
Specs dos cortes podem divergir (4K/1080, mono/stereo, mp4/mov) e `concat -c copy` quebra com specs mistas. Por isso: **normalize cada corte uma vez** para o alvo, **depois** concatene por copy.

Para cada par aprovado (gancho G, desenvolvimento D):
1. Normalize G e D (se ainda não normalizou para este alvo — reuse entre pares):
```bash
python3 scripts/normalizar.py "<corte>" --out "<tmp>/<corte>.mp4" \
    --largura 1080 --altura 1920 --fps 30 --vcodec libx265 --crf 20 \
    --sample-rate 48000 --canais 2
```
2. Concatene:
```bash
python3 scripts/combinar.py "<G_norm>" "<D_norm>" \
    --out "<pasta_projeto>/COMBINAÇÕES/GANCHO_VAV<xx>__DESENVOLVIMENTO_VAV<yy>.mp4"
```

**Aspect ratio:** `normalizar.py` faz `scale+pad+setsar=1` preservando proporção (barras quando preciso), cobrindo entrada que não seja 9:16.

### Fase 7 — Resumo
Liste as combinações geradas em `COMBINAÇÕES/`, quantas nativas e quantas cruzadas, e aponte 1–2 decisões representativas da matriz (de preferência uma ⚠️ que você aprovou ou reprovou e por quê).

## Pontos de confirmação
1. Cortes descobertos. 2. Matriz justificada. 3. Config de saída (default FHD/MP4). 4. Resumo final.

## Nomenclatura
- Pasta: `COMBINAÇÕES/` na raiz do projeto.
- Arquivo: `GANCHO_VAV<xx>__DESENVOLVIMENTO_VAV<yy>.<ext>`.

## Anti-padrões (não faça)
- Cruzar cegamente todas as N×M sem julgar encaixe.
- Reprovar par por **forma gramatical** do gancho (a promessa é que manda).
- Concatenar sem normalizar antes (specs mistas quebram o `-c copy`).
- Gerar antes de o usuário aprovar a matriz.
- Rebaixar resolução quando o usuário pediu "nativa".

## Referência
O método de julgamento e as razões técnicas (por que normalizar antes de concatenar, specs do alvo) estão em `referencia/METODO.md`.
