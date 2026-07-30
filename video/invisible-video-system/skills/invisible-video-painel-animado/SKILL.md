---
name: invisible-video-painel-animado
description: >
  Cobre um trecho de um vídeo já otimizado com um PAINEL DIDÁTICO ANIMADO — um card explicativo (título grande, diagrama, texto) que traduz visualmente o método/conceito/mecânica que a pessoa está explicando naquele momento da fala. Diferente de B-roll: aqui o TEXTO é o ponto central e nunca pode quebrar. Por isso NÃO anima com IA generativa (que reescreve texto torto); usa um pipeline HÍBRIDO: a IA (GPT Image 2 no Artlist) gera só o PERSONAGEM ilustrado como elemento recortado, e o REMOTION compõe o quadro (card, nós, setas, selos e TODO o texto são código) animando cada elemento entrando em cena ao longo dos ~5s. A skill ELEGE os trechos sozinha e pede aprovação: lê a transcrição WhisperX, acha momentos de método/conceito/raciocínio, e para cada um propõe um TEMPLATE (fluxo-de-nós, erro-certo, conceito-nomeado) já preenchido com título e textos; o usuário aprova antes de gerar. Depois gera o personagem no Artlist, recorta o fundo com rembg (alpha real — o GPT Image não entrega transparência no download), renderiza o painel no Remotion e INSERE por SUBSTITUIÇÃO DE VÍDEO mantendo o ÁUDIO ORIGINAL 100% intacto (cutaway, não overlay). Salva um arquivo novo com _ANIMATION no nome, sem tocar no original. Cobertura default 5s (painel precisa de tempo de leitura). Skill AVULSA, fora da esteira de lote. Requer Node.js, ffmpeg (faz bootstrap) e o MCP Artlist conectado (para gerar o personagem). Use quando o usuário pedir "painel didático", "painel explicativo animado", "quadro explicativo", "animação didática", "explica isso com um painel", "painel de método/conceito".
---

# Painel didático animado

Você cobre um trecho de um vídeo otimizado com um **painel didático animado**: um card
que explica visualmente o **método, conceito ou mecânica** que a pessoa fala ali. O
painel entra por cima, a **fala continua intacta por baixo** (cutaway, não overlay).

> **Regra mãe 1 — áudio SAGRADO.** Só a faixa de **vídeo** é substituída; o áudio
> original é remuxado inteiro por cima, sem reprocessar. Se o alvo não tiver áudio, aborte.
>
> **Regra mãe 2 — texto NUNCA por IA.** O texto do painel é renderizado pelo Remotion
> (texto de verdade), jamais gerado dentro de uma imagem de IA. IA generativa reescreve
> texto torto ("ROTA DO SOM" → "ROTA DOI J"). A IA só faz o **personagem ilustrado**.

## Por que híbrido (o problema que isto resolve)

Animar um painel com i2v generativo (Seedance/etc.) quebra o texto e não compõe o
quadro de verdade (só "treme" a imagem pronta). A solução: a IA gera **só o personagem**
(que ela faz bem); o **Remotion** desenha e anima card, diagrama e texto (controle total,
texto perfeito). Custo ~600 créditos/painel (1 imagem) contra ~1350 do caminho i2v.

## Dependências

- **Node.js + Remotion** — o motor de composição (projeto central instalado pelo
  bootstrap em `~/.invisible-video/painel-animado-remotion`).
- **rembg** (venv do bootstrap) — recorta o fundo do personagem → alpha real.
- **ffmpeg/ffprobe** — a inserção (`inserir.py`).
- **MCP Artlist conectado** — gera o personagem (GPT Image 2). Sem ele, **pare e avise**;
  a composição e a inserção rodam, mas não há personagem a gerar.

Rode `python3 scripts/bootstrap.py --check-only` e trate `pronto: false`.

## Entrada

- Um vídeo **otimizado/legendado** (ex.: `..._OTIMIZADO_LEGENDADO_VERTICAL.mp4`).
- O `.json` WhisperX **por base** ao lado (tire o token de formato do nome). É a fonte
  de verdade dos timestamps.
- **Quantos painéis** o usuário quer neste run (ele diz).

## O fluxo (5 passos, portão de aprovação no passo 2)

### 1. Ler o alvo e a transcrição
```bash
python3 scripts/bootstrap.py --check-only
ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate,codec_name,pix_fmt -show_entries format=duration -of default=noprint_wrappers=1 ALVO.mp4
```
Ache o `.json` da base e leia `word_segments`.

### 2. Eleger os trechos + escolher TEMPLATE + PEDIR APROVAÇÃO (a inteligência)
Com a fala à mão e o N pedido, ache **momentos de método/conceito/mecânica** (não isca,
não frase solta). Para cada um:
- `entrada` = `start` da palavra-âncora onde o conceito é dito.
- Escolha o **template** que melhor traduz o conceito:
  - **`fluxo-de-nos`** — um processo/caminho de N passos (ex.: SOM → LETRA → LEITURA).
  - **`erro-certo`** — um erro comum contrastado com a consequência/certo.
  - **`conceito-nomeado`** — um diagnóstico/ideia com nome forte (ex.: "LEITURA FANTASMA").
- Redija o **conteúdo** do painel (título, nós/rótulos, selos, explicação) FIEL à fala.
- **Portão obrigatório:** mostre a tabela `# | entrada | template | título | conteúdo`
  e **peça aprovação**. O usuário corrige âncora, template, textos. Só siga com o OK.

Coberturas de **5s** cada (painel precisa de leitura), sem sobrepor.

### 3. Gerar o PERSONAGEM no Artlist + recortar
Para cada painel que pede personagem (a maioria pede um; alguns templates funcionam sem):

**a) Imagem** — `mcp__claude_ai_Artlist__generate_image`:
- **GPT Image 2** (`modelId 2341`), `settings: {aspect_ratio: "1:1", resolution: "high", num_images: 1}`.
- Prompt de **elemento isolado**: descreva SÓ o personagem (ex.: "a smiling mother
  reading a book with her son"), estilo flat vector, **e peça fundo transparente**
  ("fully transparent background, no scene, no ground, isolated like a sticker asset").
  (O GPT Image ignora o alpha no download, mas o fundo sai branco chapado, fácil de recortar.)
- Poll `get_generation_status`. Baixe o PNG (vem RGB opaco, fundo branco — normal).

**b) Recortar** — o GPT Image **não entrega alpha no download**. Rode o rembg:
```bash
<rembgenv>/bin/python scripts/recortar.py personagem.png personagem_ALPHA.png
```
O script valida o alpha (`transparente: true`) e sai !=0 se o fundo não foi removido.

**Gate de custo:** se `generate_image` retornar `confirmation_required`, PARE, mostre o
custo e só re-chame com `confirmCost: true` após o OK. Nunca ligue sozinho.

### 4. Renderizar o painel no Remotion
Monte o JSON de conteúdo do painel (conforme o schema do template) e renderize:
```bash
python3 scripts/render_painel.py \
  --template FluxoDeNos \
  --props painel.json \
  --personagem /abs/personagem_ALPHA.png \
  --out /abs/PAINEL_ANIM.mp4
```
O `painel.json` tem `duracaoSeg` (default 5) e os campos do template. Saída
1080×1920/30fps/h264. Um `.mp4` por painel.

**Ritmo:** os templates já espaçam as entradas pelos 5s (título → nós → setas → selos →
personagem). Não amontoe; painel didático quer tempo de leitura.

### 5. Inserir (motor determinístico) e verificar
Monte o JSON de pontos e chame o `inserir.py` (o mesmo motor da broll-insert), passando
`--out` com **`_ANIMATION`** antes do token de formato:
```json
[{"entrada": 95.415, "broll": "/abs/PAINEL_ANIM.mp4", "ate_fim": false}]
```
```bash
python3 scripts/inserir.py "ALVO.mp4" --pontos pontos.json --cobertura 5.0 \
  --out "ALVO_com_ANIMATION.mp4"
```
Ele recorta só a faixa de vídeo na janela, reconcilia a grade e **remuxa o áudio
original inteiro**. Reporta `ok`. Depois **peça ao usuário para assistir** — o timing da
troca e a leitura do painel só o olho valida.

## Nome de saída

`_ANIMATION` entra antes do token de etapa (OTIMIZADO/LEGENDADO), preservando o resto:
`DS_VAV133_DESENVOLVIMENTO_OTIMIZADO_LEGENDADO_VERTICAL.mp4` →
`..._LEGENDADO_ANIMATION_VERTICAL.mp4`. Passe esse nome no `--out`. Original nunca tocado.

## Templates (layout fixo, conteúdo paramétrico)

| Template | Quando | Campos principais |
|---|---|---|
| `FluxoDeNos` | processo/caminho de N passos | `titulo`, `subtitulo`, `nos[]{label,icone}`, `selos[]`, `fecho`, `personagem` |
| `ErroCerto` | erro comum × consequência | `titulo`, `esquerda{rotulo,icone}`, `direita{...}`, `personagem` |
| `ConceitoNomeado` | diagnóstico/ideia nomeada | `titulo`, `explicacao`, `icone`, `personagem` |

Ícones disponíveis (campo `icone`): `som, letra, livro, cerebro, lapis, check, x, mudo`.
A skill **não escreve layout novo** — só preenche o template. Se um conceito não couber
em nenhum, use `conceito-nomeado` (o mais genérico) ou avise o usuário.

## Defaults (travados)

| Item | Valor |
|---|---|
| Modelo de imagem | GPT Image 2 (`modelId 2341`), 1:1, high |
| Recorte | rembg (u2net), venv do bootstrap |
| Motor de painel | Remotion, 1080×1920/30fps/h264 |
| Duração da cobertura | 5.0s |
| Nº de painéis | o usuário diz por run |

## Anti-padrões (não faça)
- **Gerar texto por IA.** Texto é Remotion. IA só o personagem.
- **Animar com i2v.** É Remotion declarativo (composição), não imagem tremendo.
- **Tocar no áudio.** Só a faixa de vídeo troca; o áudio é remuxado intacto.
- **Confiar no preview de transparência do Artlist.** O download vem opaco; rembg sempre.
- **Pular o portão de aprovação** dos trechos/templates.
- **Cobertura curta** (2s). Painel didático precisa de ~5s de leitura.
- **Escrever layout Remotion do zero por painel.** Use os templates.

## Referência
Método completo, arquitetura híbrida e aprendizados do teste em `referencia/METODO.md`.
