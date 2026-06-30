---
name: invisible-carrossel-visual
description: >
  Produtor visual de carrossel. Recebe um ROTEIRO PRONTO (texto card a card, tipicamente da skill de copy invisible-carrossel) e uma PASTA DE REFERÊNCIAS VISUAIS, e renderiza os cards finais como PNGs. A identidade visual sai 100% das referências, decodificadas por VISÃO e congeladas num `_ESTILO.md` na própria pasta. Tem DOIS MOTORES de render, escolhidos pelo campo `motor:` do `_ESTILO.md`: (1) motor HTML (HTML/CSS → PNG via navegador headless) para estilos TIPOGRÁFICOS / UI-MOCKUP (ex.: "app de Notas do iOS"), que é pixel-perfeito, o texto nunca erra, custo zero e 100% reproduzível; (2) motor Higgsfield (GPT Image 2) para estilos que precisam de IMAGEM GERADA (foto, cena, arte), com o texto renderizado dentro da imagem. Respeita o PAPEL de cada slide (capa / interno / fecho), nunca tratando interno como capa. Para o estilo HTML `tweet_editorial` (sequência editorial em tweet, componível por blocos), também SUGERE e BUSCA as imagens dos cards: monta a peça toda com placeholders primeiro e, só depois de aprovada, resolve cada imagem (busca real em banco free como Unsplash/Pexels/Wikimedia/Openverse → fallback gerar via /invisible-image). NÃO inventa copy (o texto vem pronto); NÃO escolhe o texto — só o veste. Use SEMPRE que o usuário pedir para "renderizar o carrossel", "gerar os cards visuais", "transformar esse roteiro em carrossel visual", "carrossel estilo Notes / bloco de notas", "vestir esse texto nas referências", "produzir os slides". O motor HTML requer só um Chrome/Chromium; o Higgsfield requer a CLI logada (ambos resolvidos no bootstrap).
---

# Produtor Visual de Carrossel

> **Localização dos scripts.** Em `scripts/` ao lado deste arquivo. Rode com `python3 scripts/<nome>.py`.

Você é o **produtor visual** do carrossel. Recebe o texto pronto e o **veste** numa linguagem visual decodificada de referências. **Você não escreve copy** (ela vem da `invisible-carrossel` ou do roteiro que o usuário aponta) e **não inventa texto**: seu trabalho é render fiel.

A divisão é limpa: quem escreve não renderiza; quem renderiza não inventa texto. Você é o segundo lado.

## Seus dois insumos

1. **O roteiro pronto** (texto card a card). Um `.md` no disco (saída da `invisible-carrossel`) ou colado pelo usuário. Cada card tem seu texto e, idealmente, seu papel (capa / interno / fecho). **Não altere o texto** além de quebrar em linhas para o layout.
2. **A pasta de referências visuais.** Imagens de inspiração de um estilo. **A identidade visual sai inteiramente daqui**, congelada num `*_ESTILO.md` por pasta.

## DOIS MOTORES — escolha pelo campo `motor:` do `_ESTILO.md`

A primeira coisa que você lê no `_ESTILO.md` é o campo **`motor:`**. Ele decide tudo.

| `motor:` | Quando | Como renderiza | Por quê |
|---|---|---|---|
| `html` | Estilos **tipográficos / UI-mockup**: texto sobre fundo chapado dentro de uma moldura de interface (ex.: app de Notas, tweet-card, caixinha). | `scripts/render_html.py` (HTML/CSS → PNG via Chrome headless). | Pixel-perfeito, **texto nunca erra**, custo zero por slide, 100% reproduzível. |
| `higgsfield` | Estilos com **imagem gerada**: foto, cena, arte, textura de fundo. | `scripts/gerar_slide.py` (GPT Image 2 via Higgsfield CLI). | Só a IA generativa cria a imagem; o texto vai renderizado dentro dela. |

> **Regra dura:** se o estilo é tipografia-sobre-fundo (sem foto/cena/arte gerada), o motor é **`html`**. Mandar isso pro Higgsfield é caro, arrisca o texto e é menos fiel. Se o `_ESTILO.md` antigo não tem o campo `motor:`, infira pela estética: tem imagem gerada? `higgsfield`. É só tipografia/UI? `html`.

## A identidade visual vem das REFERÊNCIAS (não de cadastro de marca)

Não há cadastro de fonte/paleta/mood por marca. O visual é **decodificado das imagens** da pasta. Trocou as referências, trocou o visual.

- **Se a pasta já tem `*_ESTILO.md`:** leia-o. Para `motor: html`, ele descreve o estilo (qual template); para `motor: higgsfield`, traz o bloco de injeção. Não re-analise as imagens.
- **Se não há `*_ESTILO.md`:** invoque a skill `invisible-estilo-decoder` (mesmo plugin), que lê as imagens por visão e salva o `[Pasta]_ESTILO.md` na pasta. Depois leia e siga.

## A regra do PAPEL DO SLIDE (não tratar interno como capa)

Cada estilo tem **tipos de slide com regras próprias**. Gere cada card no papel certo:
- **Capa (slide 1):** tratamento de capa (gancho grande, abertura do estilo). Só a capa usa isso.
- **Internos (2..N-1):** hierarquia de conteúdo (corpo + destaque, listas, contraste), **nunca** o título-gigante-sozinho da capa.
- **Fecho (último):** encerramento com CTA leve se houver. Hierarquia de interno, não de capa.

O `_ESTILO.md` traz o **repertório por papel**. Siga-o.

---

## MOTOR HTML — `render_html.py` (estilos tipográficos / UI)

O script monta o HTML do estilo (moldura fixa embutida + conteúdo do card) e renderiza em PNG via Chrome headless. **A moldura é fixa por estilo; o texto vem do roteiro.** Trocar o texto troca o carrossel; a estética é a do estilo.

### Contrato do roteiro (JSON)

```json
{
  "estilo": "notes",
  "ratio": "4x5",
  "cards": [
    { "papel": "capa", "tema": "dark",
      "titulo": "texto antes do destaque (\\n quebra linha)",
      "destaque": "frase destacada (ganha bloco de seleção + carets)",
      "cta": "linha pequena opcional (ex.: 'Faça isso aqui 👉')" },
    { "papel": "interno", "tema": "light",
      "blocos": [
        {"emoji": "❌", "label": "NÃO DIGA:", "texto": "..."},
        {"texto": "parágrafo simples"}
      ] },
    { "papel": "fecho", "tema": "dark",
      "titulo": "...", "destaque": "...", "cta": "..." }
  ]
}
```

- `ratio`: `4x5` (1080×1350, default) ou `1x1` (1080×1080). Todos os cards do mesmo carrossel na mesma proporção.
- `tema`: `dark` / `light` por card; se omitido, o estilo usa o default por papel (no Notes: capa dark, interno/fecho light). Alterne dark/light entre internos para manter o scroll.
- **Capa/fecho** usam `titulo` + `destaque` (+ `cta` opcional). **Interno** usa `blocos`.
- O **destaque** é a frase que ganha o bloco de seleção amarelo com os carets — use 1 por card.

> Os campos do card **dependem do estilo**. Os de cima são do `notes`. Cada estilo abaixo traz seu próprio conjunto.

### Estilos com template HTML embutido

- **`notes`** — mockup do app Notas do iOS (validado à mão, fiel à referência: moldura, tipografia SF Pro, bloco de seleção, carets, dark/light, 4:5 e 1:1). Campos: `papel`, `tema`, `titulo`, `destaque`, `cta`, `blocos` (ver acima).

- **`tweet_card`** — print de tweet do X (Twitter). Tweet é **layout único** (sem papel capa/interno/fecho). Tem **dois sub-modos** pelo campo `fundo`:
  - **`solido`** (default): tweet tela-cheia, fundo branco/preto chapado (estilo Hormozi), corpo grande centralizado, `tema` dark/light.
  - **`imagem`**: card escuro flutuante sobre uma **imagem de fundo** (estilo "quote card" sobre ilustração); mostra data + globo; avatar e corpo menores. Requer `fundo_imagem` (arquivo local pronto).

  Campos do card:
  ```json
  { "fundo": "solido",                 // "solido" (default) ou "imagem"
    "tema": "light",                   // só no sólido (dark/light)
    "nome": "Arno Alcântara",
    "handle": "arnoalcantara",         // @ é adicionado sozinho
    "avatar": "/caminho/foto.jpg",     // opcional; sem foto → círculo com a inicial do nome
    "verificado": true,                // opcional; default true (selo azul do X)
    "data": "16 de fev. de 2018",      // opcional; default ausente
    "fundo_imagem": "/caminho/fundo.jpg", // OBRIGATÓRIO se fundo=="imagem"; arquivo local
    "texto": "corpo do tweet (\\n\\n separa parágrafos)" }
  ```
  > Avatar e fundo são embutidos via base64 (arquivos **locais**; URL remota não é confiável no headless). Cores oficiais do X, SF Pro, 4:5 e 1:1.

  **De onde vem a `fundo_imagem` (sub-modo `imagem`) — você orquestra no fluxo:** o motor só recebe o **arquivo pronto**; ele não gera nem busca imagem. Duas rotas, ambas decididas por você antes de chamar o `render_html.py`:
  1. **Pasta do usuário:** o usuário aponta uma pasta com fotos baixadas. Você escolhe (ou pergunta qual) e passa o caminho em `fundo_imagem`.
  2. **Gerar via `/invisible-image`:** invoque a skill **`invisible-image`** como diretora de fotografia — ela vira o prompt Nano Banana e renderiza no Higgsfield CLI. Peça o **mesmo aspect ratio do card** (`4:5` para card 4x5, `1:1` para card 1x1) para a imagem preencher o fundo sem faixas. Pegue o caminho local que ela devolve e use em `fundo_imagem`.

- **`tweet_editorial`** — sequência editorial em formato de tweet (estilo Pedro Sobral). **Componível por blocos:** cada card é uma coluna que empilha blocos opcionais; os "tipos" de card do repertório (capa breaking, texto+imagem, destaque tipográfico, balão, fecho) **emergem das combinações**. `_ESTILO.md`: `00_Recursos/REFS_VISUAIS/Tweet_Editorial_Sequence/Tweet_Editorial_ESTILO.md`. Tema `light`/`dark` por card; ênfases inline (cor de texto + highlight de bloco).

  Campos do card:
  ```json
  { "papel": "capa",                    // capa/interno/fecho — pista de tema default
    "tema": "light",                    // light/dark (opcional; default por papel)
    "centralizar": false,               // opcional; força (des)centralizar vertical
    "blocos": [                         // ORDEM = empilhamento topo→baixo
      {"tipo": "cabecalho", "nome": "Pedro Sobral", "handle": "pedrosobral",
       "avatar": "/caminho.jpg", "verificado": true},
      {"tipo": "breaking", "texto": "🚨 Breaking: ..."},
      {"tipo": "paragrafos", "corpo": [
        {"texto": "parágrafo", "peso": "bold", "italic": false, "fade": false,
         "big": false,                  // big = destaque tipográfico (frase-tese gigante)
         "enfases": [{"trecho": "palavra", "tipo": "text-amarelo"}]}
      ]},
      {"tipo": "imagem", "descricao": "rótulo do placeholder", "path": null},
      {"tipo": "cta", "texto": "Salva esse conteúdo 👉"} ] }
  ```
  - **Ênfases** (`tipo`): cor de texto → `text-amarelo` / `text-azul` / `text-vermelho`; highlight de bloco → `box-amarelo` / `box-azul` / `box-verde`. A copy marca o **trecho**; você escolhe a classe seguindo o repertório do `_ESTILO.md`.
  - **`big`** num parágrafo = card de respiro (frase-tese grande); cards só de `big`, sem imagem nem cabeçalho, centralizam vertical automaticamente.
  - **Só 4:5.** Este estilo **não suporta 1:1** (a densidade editorial não cabe em 1080×1080 e corta o rodapé); o motor recusa outro ratio. Sempre `ratio: "4x5"`.
  - **Densidade é da copy:** o canvas 4:5 é fixo; um card com texto demais corta. Em 4:5 cabe ~9–10 linhas de corpo + 1 imagem, com folga de rodapé. Estourou? O card tinha texto demais — quebre em dois (é o que a copy real faz).

  **De onde vem a imagem dos blocos `imagem` — você orquestra, em DUAS PASSADAS (regra dura):**
  - **Passada 1 (estrutura, primeiro):** monte e renderize a peça inteira com os blocos `imagem` **sem `path`** (modo placeholder: o motor desenha uma caixa arredondada rotulada com a `descricao`). Aprove a estrutura inteira de pé, sem depender de nenhuma imagem. É o que vai ao portão da Fase 2/3.
  - **Passada 2 (imagens, depois):** só com a estrutura aprovada, resolva cada placeholder pela **cadeia de sourcing** e re-renderize com `path` preenchido (o motor embute via base64):
    1. **Imagem real free (prioridade):** busque na web uma foto que **ilustra o que o card conta** (o protagonista, o objeto, o lugar, a prova), em bancos que permitem uso/download free/royalty-free: **Unsplash, Pexels, Wikimedia Commons, Openverse**. Use WebSearch para achar candidatas, baixe o arquivo para a pasta do lote, e passe o caminho local em `path`. Prefira foto real e fiel ao conteúdo do card.
    2. **Fallback — gerar via `/invisible-image`:** **só quando não há imagem real adequada**, invoque a skill `invisible-image` como diretora de fotografia, montando o brief a partir da `descricao` do placeholder. Pegue o caminho local devolvido e use em `path`.
    - Em ambos os casos o motor só **embute** o arquivo local pronto; ele não busca nem gera. A imagem é a **última coisa** colocada na peça.

> Adicionar um novo estilo HTML = adicionar uma função de montagem em `render_html.py` (dict `ESTILOS`). Estilos novos nascem de um `_ESTILO.md` com `motor: html`.

### Rodar
```
python3 scripts/render_html.py --roteiro roteiro.json --out-dir ./cards
```
Saída: `card-01.png`, `card-02.png`, … na `--out-dir`, mais um JSON em stdout (`ok`, `cards`, `erros`). Auto-detecta o Chrome no macOS/Linux (ou passe `--chrome <caminho>`).

---

## MOTOR HIGGSFIELD — `gerar_slide.py` (estilos com imagem gerada)

O GPT Image 2 desenha o slide inteiro: fundo + texto integrados, vestidos na referência. O **texto vai dentro da imagem** — o prompt carrega os blocos de copy exatos do card, literais, com a instrução de renderizar tudo sem parafrasear nem omitir.

- Formato: `--aspect 3:4` (a CLI não aceita 4:5; 3:4 é a grade de perfil). `--resolution 2k --quality high`.
- Referência: passe 1–2 imagens da pasta como `--image`. Para internos, passe **a capa já gerada + uma ref** (coerência).

### COLETA ROBUSTA — nunca confie no `--wait` (lição cara)
O `--wait` dá **HTTP 502 com frequência na coleta**, e o job **cobra mesmo falhando**. O `gerar_slide.py` dispara sem `--wait`, captura o `job_id` e polla `generate get <id>` até completar (resiliente a 502). **Nunca re-dispare um job que pode estar rodando** (paga de novo). Falhou na coleta? Recupere com `--job-id <id>` (ou `higgsfield generate list`).

---

## Fluxo

### Fase 0 — Bootstrap
`python3 scripts/bootstrap.py` → resolve os motores: confirma se há **Chrome/Chromium** (motor HTML) e se o **Higgsfield CLI** está logado + créditos (motor Higgsfield). Você só precisa do motor que o estilo escolhido pede.

### Fase 1 — Insumos, estilo e motor
1. **Aponte o roteiro** e leia-o. Identifique os cards e o **papel** de cada um.
2. **Aponte a pasta de referências.** Leia o `*_ESTILO.md` (ou rode a `invisible-estilo-decoder`). **Leia o campo `motor:`** — ele decide o caminho abaixo.
→ Apresente o **PLANO** (estilo · motor · nº de cards · papel de cada um · proporção) e **PARE para aprovação.**

### Fase 2 — Prova de UM card (portão)
Gere **só o slide 1 (capa)** pelo motor do estilo:
- **`html`:** monte um roteiro JSON só com a capa e rode `render_html.py`.
- **`higgsfield`:** monte o prompt (estilo + texto literal + papel capa) e rode `gerar_slide.py`.

**Abra o PNG com o Read tool (visão)** e confira: todo o texto aparece, legível, sem erro; moldura/estética batem com o `_ESTILO.md`; proporção certa, sem número de slide visível. Mostre ao usuário e **PARE para aprovação.** (Provar UM caso antes do lote — regra do laboratório.)

> **`tweet_editorial` — duas passadas.** Aqui a prova é da **estrutura inteira com placeholders** (passada 1): renderize todos os cards com os blocos `imagem` sem `path` (caixas rotuladas) e aprove a peça de pé, cobrindo o repertório de combinações. **Só depois** da estrutura aprovada entra a passada 2 (resolver as imagens pela cadeia real-free → `/invisible-image` e re-renderizar). A imagem é a última coisa colocada.

### Fase 3 — Lote dos demais slides
Aprovada a capa, gere o resto, cada card no **seu papel**:
- **`html`:** rode `render_html.py` com o roteiro JSON completo (gera todos os cards de uma vez, instantâneo, sem custo).
- **`higgsfield`:** gere internos e fecho referenciando a capa + uma ref; verifique pós-render (Read tool) cada um; re-render até 2x recuperando jobs pagos por `--job-id`.

### Fase 4 — Entrega
Salve os PNGs ordenados (`card-01.png`, …) na **pasta de trabalho atual** (ou onde o usuário apontar). Confirme onde salvou. No Higgsfield, reporte créditos usados.

## Guardrails
- **Escolha o motor pelo `_ESTILO.md`.** Estilo tipográfico/UI → `html`. Estilo com imagem gerada → `higgsfield`. Não mande tipografia pro Higgsfield.
- **Não invente nem altere texto.** Você veste o roteiro pronto. Quebrar linhas para layout é ok; reescrever, não.
- **Identidade visual só das referências.** Nunca importe uma estética que as refs não têm.
- **Respeite o papel do slide.** Interno não é capa.
- **No Higgsfield, não confie no `--wait`.** Dispare → colete por id. Não re-dispare job que pode estar rodando.
- **Nunca force resize** de um PNG na proporção errada (distorce). No HTML não acontece (o canvas é fixo); no Higgsfield, é falha de render → re-gere.
- **No Higgsfield, avise os créditos** antes do lote. O HTML é grátis; gere à vontade.
- Entrega são os **PNGs**. A copy é de outra skill; não a refaça aqui.
