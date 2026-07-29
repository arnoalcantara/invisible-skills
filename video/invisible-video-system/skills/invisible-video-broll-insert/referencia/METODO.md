# MÉTODO — invisible-video-broll-insert

Referência técnica de manutenção. O fluxo operacional está na `SKILL.md`.

## Arquitetura

Duas metades, propositalmente separadas:

1. **Geração (Artlist, sessão-dependente):** a SKILL.md conduz. Imagem Nano Banana 2 →
   animação Seedance i2v. Depende do MCP Artlist conectado. É a parte que NÃO roda em
   máquina sem o conector.
2. **Inserção (`inserir.py`, ffmpeg puro, portável):** determinística, roda em qualquer
   lugar. Recebe o alvo + B-rolls prontos + pontos, e entrega o vídeo coberto com o
   áudio original intacto.

Essa divisão é o que torna a inserção reaproveitável mesmo quando a geração muda de
motor no futuro (outro modelo, outro conector). O contrato entre as metades é o JSON
de pontos: `[{entrada, broll, ate_fim}]`.

## O contrato do `inserir.py`

- **Entrada:** vídeo-alvo com áudio + `--pontos <json>` + `--cobertura <s>` (default 2.0).
- **Cada ponto:** `entrada` (segundo de início da cobertura), `broll` (mp4 de qualquer
  grade/duração), `ate_fim` (estica até o fim do alvo — só no último).
- **Saída:** `<base>_BROLL_<resto>.mp4` na mesma pasta (token `_BROLL` antes de
  `--sufixo-pos`, default `OTIMIZADO`). Reporta JSON com verificação.

## Como a inserção preserva o áudio (o coração)

1. Recorta a faixa de **vídeo** do alvo (sem áudio) nos pedaços ENTRE as coberturas.
2. Reconcilia cada B-roll para a grade do alvo (crop de largura, fps, codec, pix_fmt).
3. Concatena **só vídeo** na ordem `[alvo][broll][alvo][broll]...`.
4. **Remuxa** esse vídeo com o **áudio original inteiro** do alvo:
   `-map 0:v:0 -map 1:a:0 -c:v copy -c:a copy -shortest`.

O áudio nunca passa por filtro nem corte. A fala e a sincronia ficam idênticas ao
original. Só a imagem troca nas janelas de cobertura.

## Aprendizados do teste (Lote 09 / VAV133, 29/07/2026) — o que quase quebrou

1. **Seedance mínimo = 2s.** Não existe geração de 1s no i2v. Gere 2s; se quiser
   cobertura menor, apare no `--cobertura` (o `inserir.py` corta o B-roll no `-t`).
2. **Largura 1088, não 1080.** O i2v vertical 1080p sai **1088×1920**. Crop central
   obrigatório: `scale=-2:<h>,crop=<w>:<h>`.
3. **fps 24, não 30.** O i2v sai a **24fps**; o otimizado é 30. Casar com `fps=<alvo>`
   senão o concat/esteira engasga.
4. **B-roll sem áudio.** O i2v vem mudo — por isso o remux com o áudio do alvo é limpo,
   não há áudio de B-roll competindo. O `inserir.py` força `-an` nos B-rolls.
5. **concat com caminho relativo FALHA (exit 254).** O demuxer resolve os caminhos
   relativos ao diretório do `concat.txt`, não ao cwd. `inserir.py` usa
   `os.path.abspath` em cada linha.
6. **`tpad` para esticar até o fim.** `tpad=stop_mode=clone:stop_duration=<grande>` +
   `-t <duração exata>` clona o último frame para cobrir o fim quando o B-roll (2s) é
   mais curto que a janela até o fim do clipe. Usado quando `ate_fim: true`.
7. **Higgsfield não autentica na sessão** (`higgsfield auth login` interativo). Foi o
   motivo de a skill NÃO depender da `invisible-image` e gerar direto no Artlist.

## IDs de modelo Artlist (verificados 29/07/2026)

| Uso | Modelo | modelId | Settings |
|---|---|---|---|
| Imagem | Nano Banana 2 T2I 2K | 2251 | aspect_ratio, resolution (2k), num_images |
| Animação | Seedance 1.0 Pro Fast I2V 1080p | 2406 | aspect_ratio, resolution (1080p), duration (min 2) |

> Os IDs do Artlist podem mudar. Se `generate_image`/`generate_video` reclamar do
> modelId, re-listar com `mcp__claude_ai_Artlist__list_models` (kind image/video) e
> achar o Nano Banana 2 T2I e o Seedance 1.0 Pro Fast I2V pelo displayName.

## Prompt de imagem — princípios de DP

Física em vez de adjetivo. Câmera (Alexa 35 / IMAX 65mm), lente do conjunto, luz
motivada (Kelvin/direção/IRE), stock Kodak coerente, grão **visible/organic/heavy**.
Ângulo inusitado (nunca altura-dos-olhos neutra). Sem buzzword, sem texto na imagem,
sem citar diretores. Formato: parágrafos com header em CAPS de `CAMERA:` a
`MOOD & ART DIRECTION:`. 1200–1450 caracteres.

## Prompt de animação — contido

Inserto de 2s: micro-movimento, respiração, leve drift. SEM zoom, SEM câmera rápida.
Movimento agressivo estraga o inserto e denuncia IA.

## Escopo (o que esta skill NÃO faz)

- Overlay / picture-in-picture (isto é cutaway: troca a tela inteira).
- Mexer na esteira de lote (skill avulsa).
- Gerar áudio/trilha no B-roll.
- Chamar invisible-image / Higgsfield.
