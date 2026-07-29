---
name: invisible-video-broll-insert
description: >
  Insere coberturas de B-roll geradas por IA num vídeo já otimizado, ancorando cada cobertura no timestamp EXATO da fala (lido do `.json` WhisperX que já existe ao lado do vídeo). A skill ELEGE os trechos sozinha e pede aprovação: lê a transcrição, propõe N momentos onde a imagem ilustra o que está sendo dito (distribuídos pelo arco do vídeo, não amontoados no começo) com uma ideia descritiva de cada imagem, e o usuário aprova/corrige (mover a âncora, cobrir o fim, trocar a descrição) antes de gerar. Depois GERA cada B-roll no Artlist (imagem Nano Banana 2 → animação Seedance image-to-video, 2s) e INSERE por SUBSTITUIÇÃO DE VÍDEO mantendo o ÁUDIO ORIGINAL 100% intacto (nunca cortado, deslocado ou remixado) — cutaway, não picture-in-picture. Reconcilia cada B-roll para a grade exata do alvo (resolução/fps/codec) e pode esticar o último até o fim do clipe. Salva um arquivo novo com _BROLL no nome, na mesma pasta, sem tocar no original. O usuário diz QUANTOS B-rolls por run (ex.: "2 no gancho", "5 no desenvolvimento"). Skill AVULSA, fora da esteira de lote. Requer ffmpeg (faz bootstrap) e o MCP Artlist conectado na sessão (para a geração). Use quando o usuário pedir "insere b-roll", "põe cobertura de imagem", "cobre com imagens geradas", "b-roll nesse vídeo", "cutaway".
---

# Inserção de B-roll gerado por IA

Você cobre trechos de um vídeo otimizado com **B-rolls gerados por IA**, ancorados no
**timestamp exato da fala**. A imagem entra por cima, a **fala continua intacta por
baixo**: é cutaway (troca a tela), não overlay/PiP. O áudio original nunca é tocado.

> **Regra mãe:** o áudio do alvo é SAGRADO. Você só substitui trechos da faixa de
> **vídeo**; o áudio original é remuxado inteiro por cima, sem reprocessar. Se o alvo
> não tiver áudio, aborte — não é o caso de uso.

## Dependências

- **ffmpeg/ffprobe** — o motor de inserção (`inserir.py`). Rode o bootstrap:
  `python3 scripts/bootstrap.py --check-only`.
- **MCP Artlist conectado** — a geração (imagem + animação) usa as ferramentas
  `mcp__claude_ai_Artlist__*`. Se elas não existirem na sessão, **pare e avise**: a
  skill não gera B-roll sem o Artlist. (A inserção em si roda sem ele, se o usuário já
  tiver B-rolls prontos.)

## Entrada

- Um vídeo **otimizado** (ex.: `..._OTIMIZADO_VERTICAL.mp4`).
- O `.json` WhisperX **por base** ao lado dele (ex.: `DS_VAV133_GANCHO_1_OTIMIZADO.json`)
  — achado removendo o token de formato do nome do vídeo. Tem `word_segments` com
  `start/end/word` **medidos**. É a fonte de verdade dos timestamps.
- **Quantos B-rolls** o usuário quer neste run (ele diz; não há default por duração).
- Restrições opcionais do usuário ("o primeiro antes dos 3s", "cobre o fim").

## O fluxo (5 passos, com portão de aprovação no passo 2)

### 1. Ler o alvo e a transcrição
```bash
python3 scripts/bootstrap.py --check-only
# specs do alvo (grade que os B-rolls terão que casar):
ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate,codec_name,pix_fmt -show_entries format=duration -of default=noprint_wrappers=1 ALVO.mp4
```
Ache o `.json` da base (tire `_VERTICAL`/`_QUADRADO`/`_RETRATO` do nome). Leia
`word_segments`.

### 2. Eleger os trechos e PEDIR APROVAÇÃO (a inteligência da skill)
Com a fala inteira à mão e o N pedido:
- Escolha **N momentos** onde a imagem **ilustra** o que está sendo dito. Distribua
  pelo **arco do vídeo** (começo/meio/fim), não amontoe no início. Respeite as
  restrições do usuário.
- Para cada trecho: `entrada` = timestamp da palavra-âncora (use o `start` da palavra
  onde a cobertura deve começar), a **fala coberta** (as palavras em [entrada,
  entrada+2s]) e uma **ideia descritiva da imagem** (concreta, específica, ligada ao
  que ela fala ali).
- Se o usuário pediu "cobrir o fim", marque o último com `ate_fim: true` (a cobertura
  vai da entrada até o fim do clipe).
- **Portão obrigatório:** mostre a tabela `# | entrada→fim | fala coberta | imagem` e
  **peça aprovação**. O usuário pode mover a âncora ("começa em 'bases'" → use o
  `start` dessa palavra), trocar a descrição, mudar quais cobrem o fim. Só siga com o OK.

Coberturas **não podem se sobrepor** (cada uma ocupa 2s, ou até o fim). Se o N pedido
não couber sem sobrepor, diga e proponha menos.

### 3. Gerar cada B-roll no Artlist (imagem → animação)
Para cada trecho aprovado, na ordem:

**a) Imagem** — `mcp__claude_ai_Artlist__generate_image`:
- `modelId: 2251` (Nano Banana 2 T2I 2K), `settings: {aspect_ratio: "9:16", resolution: "2k", num_images: 1}`.
  (Confirme o aspect certo pela grade do alvo: vertical → 9:16.)
- **Prompt no formato Diretor de Fotografia** (física, não adjetivo): parágrafos com
  header em CAPS — `CAMERA:` (ARRI Alexa 35 ISO 800 ou IMAX 65mm ISO 250; ângulo
  inusitado, nunca altura-dos-olhos neutra), `LENS:`, `LIGHT:` (fonte motivada,
  Kelvin, direção, IRE), `SUBJECT:` (posição, estado, "Intercepted"), `FOREGROUND/
  MIDGROUND/BACKGROUND:`, `WARDROBE TONAL BEHAVIOR:`, `MAKEUP SURFACE PHYSICS:`,
  `POST BEHAVIOR:` (stock Kodak coerente, grão **visible/organic/heavy**, halation),
  `COMPOSITIONAL GEOMETRY:`, `MOOD & ART DIRECTION: Composition and art direction
  inspired in the work of award-winning directors.`
  Proibido: buzzword (cinematic/epic/beautiful/dramatic...), texto/logo na imagem,
  citar diretores/filmes. Mire 1200–1450 caracteres.
- Poll `get_generation_status` até completar. Guarde o `assetUrl` da imagem.

**b) Animação** — `mcp__claude_ai_Artlist__generate_video` (image-to-video):
- Suba a imagem: `mcp__claude_ai_Artlist__upload_image` com o `imageUrl` = `assetUrl`
  da imagem → pegue o `assetId`.
- `modelId: 2406` (Seedance 1.0 Pro Fast I2V 1080p), `input: {assetId: <id>}`,
  `settings: {aspect_ratio: "9:16", resolution: "1080p", duration: "2"}`.
  (Seedance NÃO faz menos de 2s; sempre 2s.)
- **Prompt de movimento contido:** micro-movimento, respiração, leve drift de câmera.
  SEM zoom, SEM câmera rápida — é inserto curto de 2s. Ex.: "Subtle slow cinematic
  motion, gentle handheld micro-movement, [ação mínima do sujeito], no fast motion,
  no zoom, keep it calm."
- Poll até completar. Guarde o `assetUrl` do vídeo.

**c) Baixar** o `.mp4` para uma pasta de trabalho (não no projeto do usuário sem
necessidade; use uma subpasta tipo `_BROLL_TRABALHO/` ao lado do alvo, ou o scratchpad):
```bash
curl -sL "<assetUrl do video>" -o "_BROLL_TRABALHO/broll_<n>.mp4"
```

**Gate de custo:** se `generate_image`/`generate_video` retornar `confirmation_required`,
PARE, mostre o custo ao usuário e só re-chame com `confirmCost: true` após o OK dele.
Nunca ligue `confirmCost` por conta própria.

### 4. Inserir (motor determinístico)
Monte o JSON de pontos (um por cobertura aprovada) e chame o `inserir.py`:
```json
[
  {"entrada": 1.937, "broll": "/abs/_BROLL_TRABALHO/broll_1.mp4", "ate_fim": false},
  {"entrada": 6.570, "broll": "/abs/_BROLL_TRABALHO/broll_2.mp4", "ate_fim": true}
]
```
```bash
python3 scripts/inserir.py "ALVO.mp4" --pontos pontos.json --cobertura 2.0
```
O script reconcilia cada B-roll para a grade do alvo (crop de largura, `fps`, codec,
`pix_fmt`), recorta os pedaços do alvo entre as coberturas, concatena só vídeo e
**remuxa o áudio original inteiro** por cima. Ele valida sobreposição e recusa se
houver. Reporta um JSON com `saida`, `grade`, `dur_final` vs `dur_alvo`, `coberturas`
e `ok`.

### 5. Verificar e entregar
- O `inserir.py` já confere grade e duração (`ok: true`). Além disso, **peça ao
  usuário para assistir** — o timing da troca e a costura só o olho valida. Aponte os
  dois riscos: (1) a troca cai num corte natural ou num meio-de-palavra estranho?
  (2) se algum B-roll é `ate_fim`, o último frame congelado é imperceptível?
- Se um ponto incomodar, **recue/avance a âncora em décimos e re-rode só o `inserir.py`**
  (barato — não regera Artlist). Só regenere o B-roll no Artlist se a IMAGEM em si
  estiver ruim.

## Nome de saída

`_BROLL` entra no nome **antes** do token `OTIMIZADO` (default `--sufixo-pos OTIMIZADO`),
preservando o resto:
`DS_VAV133_GANCHO_1_OTIMIZADO_VERTICAL.mp4` → `DS_VAV133_GANCHO_1_BROLL_OTIMIZADO_VERTICAL.mp4`.
Salvo na mesma pasta do original. O original nunca é tocado.

## Defaults (travados)

| Item | Valor |
|---|---|
| Modelo de imagem | Nano Banana 2 T2I 2K (`modelId 2251`), 9:16, 2k |
| Modelo de vídeo | Seedance 1.0 Pro Fast I2V 1080p (`modelId 2406`), 2s |
| Duração da cobertura | 2.0s (mínimo do Seedance); último pode ir `ate_fim` |
| Nº de B-rolls | o usuário diz por run (sem default por duração) |
| Custo aproximado | ~530 créditos/B-roll (130 imagem + 400 vídeo) |

## Anti-padrões (não faça)
- **Tocar no áudio.** Só a faixa de vídeo é substituída; o áudio é remuxado intacto.
- **Sobrepor coberturas.** Cada uma ocupa 2s (ou até o fim); o `inserir.py` recusa colisão.
- **Amontoar B-rolls no começo.** Distribua pelo arco do vídeo.
- **Pular o portão de aprovação** dos trechos. O usuário aprova antes de gastar Artlist.
- **Ligar `confirmCost` sozinho.** A régua de custo do Artlist é do usuário.
- **Gerar movimento agressivo** no i2v (zoom, câmera rápida). É inserto curto: contido.
- **Chamar a `invisible-image`/Higgsfield.** Esta skill é autossuficiente no Artlist.

## Referência
O método completo, os aprendizados do teste (Seedance 2s, largura 1088→crop, 24→30fps,
tpad, concat absoluto) e o contrato técnico estão em `referencia/METODO.md`.
