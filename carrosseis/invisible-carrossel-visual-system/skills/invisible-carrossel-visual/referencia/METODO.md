# Método — Produtor Visual de Carrossel

Referência técnica do método de render. Lido pelo agente quando precisa de detalhe; a orquestração está na `SKILL.md`.

---

## 1. Dois motores — escolha pela natureza do estilo

A skill tem dois motores de render, declarados no campo `motor:` do `_ESTILO.md`:

**Motor HTML (`motor: html`) — estilos tipográficos / UI-mockup.** Quando o card é **tipografia sobre fundo chapado dentro de uma moldura de interface** (ex.: app de Notas, tweet-card, caixinha), o render certo é HTML/CSS → PNG por navegador headless (`render_html.py`). A moldura é reconstruída em código uma vez (fiel à referência, validada à mão), e o texto vem do roteiro. Vantagens: **pixel-perfeito, texto de verdade (nunca erra), custo zero por slide, 100% reproduzível**. Foi por isso que o estilo `notes` virou motor HTML: testá-lo no Higgsfield era caro, arriscava o texto e era menos fiel.

**Motor Higgsfield (`motor: higgsfield`) — estilos com imagem gerada.** Quando o estilo precisa de **foto, cena ou arte gerada** como fundo, só a IA generativa resolve. O GPT Image 2 desenha fundo + texto integrados, vestidos na referência (`gerar_slide.py`). Aqui a verificação pós-render (abrir o PNG com visão e conferir o texto) é obrigatória: texto errado = falha → re-gera.

> Regra dura: tipografia-sobre-fundo (sem imagem gerada) é sempre motor HTML. Não mande isso pro Higgsfield.

## 1.1. Motor HTML — como funciona por dentro

`render_html.py` embute, por estilo, a **moldura fixa** (CSS + SVGs da UI) e uma função de montagem que veste o conteúdo de cada card. O contrato de entrada é um **roteiro JSON** (ver `referencia/exemplo-roteiro-notes.json` e a docstring do script): `estilo`, `ratio` (`4x5`/`1x1`), e `cards[]` com `papel` (capa/interno/fecho), `tema` (dark/light) e o conteúdo por papel (`titulo`+`destaque`+`cta` na capa/fecho; `blocos` no interno). O script renderiza cada card via Chrome headless e valida a dimensão do PNG (não força resize).

Adicionar um **estilo HTML novo** = escrever uma função `montar_html_<estilo>(card, ratio)` e registrá-la no dict `ESTILOS`. O estilo nasce de um `_ESTILO.md` com `motor: html` (o briefing visual continua sendo o contrato; o template o implementa em código).

Estilos prontos:
- **`notes`** (app Notas do iOS — moldura, SF Pro, bloco de seleção amarelo com carets de seleção, dark/light, 4:5 e 1:1; cores amostradas por pixel da referência).
- **`tweet_card`** (print de tweet do X — cabeçalho editável `nome`/`handle`/`avatar`/`verificado`/`data`, SF Pro, 4:5 e 1:1; cores oficiais do X amostradas por pixel da referência). Tweet é layout único: **sem `papel`**. Avatar é arquivo local embutido via base64, com fallback de círculo+inicial quando não há foto. Dois sub-modos pelo campo `fundo`:
  - **`solido`** (default): tweet tela-cheia, fundo branco/preto chapado, `tema` dark/light, corpo grande centralizado.
  - **`imagem`**: card escuro flutuante sobre uma imagem de fundo (data + globo, avatar/corpo menores). Requer `fundo_imagem` (arquivo local pronto). **O motor não gera nem busca a imagem** — ela chega pronta. Quem a produz é a SKILL no fluxo: (1) pasta apontada pelo usuário, ou (2) geração via `/invisible-image` (diretora de fotografia → prompt Nano Banana → Higgsfield CLI), pedindo o mesmo aspect ratio do card.

## 2. O `_ESTILO.md` — briefing visual congelado por pasta

Cada pasta de referências de um estilo recorrente ganha um `_ESTILO.md` ao lado das imagens. É o briefing decodificado **uma vez** por visão, congelado como contrato. A skill lê esse arquivo em vez de re-analisar as imagens a cada carrossel: mais rápido, mais barato, e **idêntico toda vez** (consistência do feed).

Seções que um `_ESTILO.md` bem-feito tem:
- **Conceito** (o que o estilo imita / é).
- **Moldura / elementos fixos** (detail signature em todos os slides).
- **Modos de fundo** (dark/light + cores exatas).
- **Tipografia travada** (fonte, pesos, caixa — copiada verbatim no prompt).
- **Accent** (como o destaque é feito, com precisão — ex.: bloco de seleção vs. pincel).
- **Papel do slide** (repertório de capa / interno / fecho — a parte que evita interno-com-cara-de-capa).
- **Anti-estética** (o que nunca fazer).
- **Bloco de injeção** pronto para colar no prompt.

O `_ESTILO.md` é editável à mão: é a fonte da verdade do estilo. Para ajustar, edite o arquivo ou troque as refs e re-decodifique.

## 3. Coleta robusta — o problema do 502

O `higgsfield generate create ... --wait` dá **HTTP 502 com frequência na coleta** do resultado, e o job **cobra mesmo quando o --wait falha**. Por isso o `gerar_slide.py`:

1. Dispara o job **sem** `--wait` → captura o `job_id` na hora.
2. Polla `higgsfield generate get <job_id> --json` até `completed` (resiliente a 502 transitório: erro na coleta não significa erro na geração).
3. Baixa a `result_url` ao completar.

Se tudo falhar, o job pode ter rodado mesmo assim. Recupere com:
```bash
higgsfield generate list --image --size 12 --json   # ache o job_id pela timestamp/url
python3 scripts/gerar_slide.py --job-id <id> --out card.png --prompt-file x.txt
```
**Nunca re-dispare um job que pode estar rodando** — re-disparar = pagar de novo.

## 4. Formato e proporção

A Higgsfield CLI (`gpt_image_2`) aceita `--aspect_ratio` em `1:1,4:3,3:4,16:9,9:16,3:2,2:3`. **Não aceita 4:5.** Usa-se **3:4** (que é também a proporção da grade de perfil do Instagram — a capa sobrevive bem ao corte da grade). A saída vem em alta resolução (ex.: 1744×2336); entrega-se o PNG como veio, sem forçar resize.

Validação: ratio ≈ 0.75. Outra proporção = falha de render (re-gera, nunca força resize, que distorce).

## 5. Referências no prompt

- **Capa:** 1–2 imagens da pasta como `--image` (ancora fonte e estética).
- **Internos:** **a capa já gerada + uma ref** como `--image`. A capa dá a direção final; a ref dá repertório. Isso mantém os slides coerentes sem depender do slide anterior.

## 6. Créditos

Cada slide consome créditos do Higgsfield. Um carrossel de ~9 slides + re-renders soma. O `bootstrap.py` reporta os créditos restantes; a skill avisa o usuário antes de gerar em lote. Iterar pouco antes do render real; provar UM card (a capa) antes do lote.
