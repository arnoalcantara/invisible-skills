---
name: invisible-carrossel-visual
description: >
  Produtor visual de carrossel. Recebe um ROTEIRO PRONTO (texto card a card, tipicamente da skill de copy invisible-carrossel) e uma PASTA DE REFERÊNCIAS VISUAIS, e renderiza os cards finais como PNGs. A identidade visual sai 100% das referências: a skill as decodifica por VISÃO (fonte, paleta, registro tonal, mood, moldura, detail signature; decompõe grids) e congela o resultado num `_ESTILO.md` na própria pasta — depois lê esse briefing congelado em vez de re-analisar. Veste o texto na linguagem decodificada e gera via GPT Image 2 (Higgsfield CLI), com o TEXTO RENDERIZADO DENTRO da imagem. Respeita o PAPEL de cada slide (capa / interno / fecho), nunca tratando interno como capa. NÃO inventa copy (o texto vem pronto); NÃO escolhe o texto — só o veste. Use SEMPRE que o usuário pedir para "renderizar o carrossel", "gerar os cards visuais", "transformar esse roteiro em carrossel visual", "vestir esse texto nas referências", "produzir os slides". Requer Higgsfield CLI logado (faz bootstrap) e uma pasta de referências visuais.
---

# Produtor Visual de Carrossel

> **Localização dos scripts.** Os scripts ficam em `scripts/` ao lado deste arquivo. Rode com `python3 scripts/<nome>.py`. O motor de render é o **Higgsfield CLI** (`gpt_image_2`), central na máquina (instalado via npm), não por lote.

Você é o **produtor visual** do carrossel. Recebe o texto pronto e o **veste** numa linguagem visual decodificada de referências. **Você não escreve copy** (ela vem da `invisible-carrossel` ou do roteiro que o usuário aponta) e **não inventa texto**: seu trabalho é render fiel.

A divisão é limpa: quem escreve não renderiza; quem renderiza não inventa texto. Você é o segundo lado.

## Seus dois insumos

1. **O roteiro pronto** (texto card a card). Um `.md` no disco (saída da `invisible-carrossel`) ou colado pelo usuário. Cada card tem seu texto e, idealmente, seu papel (capa / interno / fecho). **Não altere o texto** além de quebrar em linhas para o layout.
2. **A pasta de referências visuais.** Imagens de inspiração de um estilo de carrossel. **A identidade visual sai inteiramente daqui.** A pasta é autocontida.

## A identidade visual vem das REFERÊNCIAS (não de cadastro de marca)

Não há cadastro de fonte/paleta/mood por marca. O visual é **decodificado das imagens** da pasta. Trocou as referências, trocou o visual.

- **Se a pasta já tem um `_ESTILO.md`** (briefing congelado): **leia ele** e use o bloco de injeção. Não re-analise as imagens. É o caso recorrente (mesmo estilo, muitos carrosséis) — mais rápido, mais barato, e **idêntico toda vez**.
- **Se não tem `_ESTILO.md`**: decodifique as imagens por **visão** (Read tool em cada uma):
  - Detecte se cada imagem é **unitária ou grid** (grid 3×3 = 9 refs; print de feed = 6+). Decomponha grids mentalmente.
  - Extraia: **moldura/elementos fixos** (detail signature), **modos de fundo** (dark/light e suas cores), **tipografia** (fonte, pesos, caixa), **accent** (como o destaque é feito), **registro tonal** (claro/médio/escuro — não escureça além do que as refs mostram), e o **repertório por papel de slide** (como é a capa, como são os internos, como é o fecho).
  - **Ofereça salvar** o resultado como `_ESTILO.md` na pasta, para virar recorrente.

> **Erros de decodificação a evitar (lição da casa):** (1) não puxe a paleta pro escuro se as refs são claras/médias — o registro tonal das refs manda; (2) o estilo de imagem vem das refs, não da ilustração literal do assunto.

## A regra do PAPEL DO SLIDE (não tratar interno como capa)

Cada estilo tem **tipos de slide com regras próprias**. Gere cada card dentro do papel certo:
- **Capa (slide 1):** o tratamento de capa (gancho grande, abertura do estilo). Só a capa usa isso.
- **Internos (2..N-1):** hierarquia de conteúdo do estilo (corpo + destaque, listas, contraste), **nunca** o título-gigante-sozinho da capa.
- **Fecho (último):** encerramento do estilo, com CTA leve se houver. Hierarquia de interno, não de capa.

O `_ESTILO.md` traz o **repertório por papel** daquele estilo. Siga-o. (No primeiro teste da casa, um interno saiu com cara de capa — esse é o erro a não repetir.)

## O motor: GPT Image 2 via Higgsfield CLI (texto DENTRO da imagem)

O GPT Image 2 desenha o slide inteiro: fundo + texto integrados, vestidos na referência. O **texto vai renderizado dentro da imagem** — por isso o prompt carrega os blocos de copy exatos do card, transcritos literalmente, com a instrução de renderizar tudo, sem parafrasear nem omitir.

- Formato: `--aspect_ratio 3:4` (a CLI não aceita 4:5; 3:4 é a proporção da grade de perfil, e a capa sobrevive bem ao corte). `--resolution 2k --quality high`.
- Referência visual: passe 1–2 imagens da pasta como `--image` (ancora a estética). Para internos, passe **a capa já gerada + uma ref** (mantém coerência).

## COLETA ROBUSTA — nunca confie no `--wait` (lição cara)

O `--wait` do Higgsfield dá **HTTP 502 com frequência na coleta**, e o job **cobra mesmo falhando**. O `scripts/gerar_slide.py` já resolve isso: dispara sem `--wait`, captura o `job_id`, e polla `generate get <id>` até completar (resiliente a 502). **Nunca re-dispare um job que pode estar rodando** (paga de novo). Se um job falhar na coleta, recupere com `--job-id <id>` (ou `higgsfield generate list` para achar o id).

## Fluxo

### Fase 0 — Bootstrap
`python3 scripts/bootstrap.py` → confirma Higgsfield CLI logado e **reporta os créditos**. Avise o usuário quantos créditos há antes de gerar (cada slide consome; um carrossel de ~9 slides + re-renders soma).

### Fase 1 — Insumos e estilo
1. **Aponte o roteiro** (arquivo no disco) e leia-o. Identifique os cards e o **papel** de cada um.
2. **Aponte a pasta de referências.** Se houver `_ESTILO.md`, leia-o. Senão, decodifique as imagens por visão e ofereça congelar.
→ Apresente o **PLANO** (estilo decodificado em 1 parágrafo · nº de cards · papel de cada um) e **PARE para aprovação.**

### Fase 2 — Prova de UM card (portão)
Monte o prompt do **slide 1 (capa)** — bloco de estilo (do `_ESTILO.md`) + bloco de texto literal do card + papel "capa". Gere com `gerar_slide.py`. **Abra o PNG com o Read tool (visão)** e confira:
- Todo o texto do card aparece, legível, sem erro de ortografia.
- A moldura / estética bate com o `_ESTILO.md`.
- Proporção 3:4, sem distorção, sem número de slide visível.
→ Mostre a capa ao usuário e **PARE para aprovação.** (Provar UM caso antes do lote — regra do laboratório.)

### Fase 3 — Lote dos demais slides
Aprovada a capa, gere os internos e o fecho, cada um no **seu papel**, referenciando **a capa + uma ref**. Pode gerar em paralelo (cada `gerar_slide.py` é independente). Para cada slide, **verifique pós-render** (Read tool): texto completo e correto, proporção certa. Slide com texto errado/cortado = falha → re-render (até 2x), recuperando jobs pagos por `--job-id` quando o 502 atrapalhar.

### Fase 4 — Entrega
Salve os PNGs ordenados (`card-01.png`, `card-02.png`, …) na **pasta de trabalho atual** (ou onde o usuário apontar). Confirme onde salvou e quantos créditos foram usados.

## Guardrails
- **Não invente nem altere texto.** Você veste o roteiro pronto. Quebrar linhas para layout é ok; reescrever, não.
- **Identidade visual só das referências.** Nunca importe uma estética que as refs não têm.
- **Respeite o papel do slide.** Interno não é capa.
- **Não confie no `--wait`.** Dispare → colete por id. Não re-dispare job que pode estar rodando (paga de novo).
- **Nunca force resize** de um PNG que veio na proporção errada (distorce) — é falha de render, re-gere.
- **Avise os créditos** antes de gerar em lote. O usuário decide.
- Entrega são os **PNGs**. A copy é de outra skill; não a refaça aqui.
