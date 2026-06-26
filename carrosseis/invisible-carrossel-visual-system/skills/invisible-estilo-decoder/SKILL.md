---
name: invisible-estilo-decoder
description: >
  Decodificador de estilo visual. Aponte uma PASTA DE REFERÊNCIAS VISUAIS (imagens de inspiração de um estilo de carrossel) e a skill as lê por VISÃO, extrai o sistema visual completo (conceito, moldura/detail signature, modos de fundo, tipografia, accent, registro tonal, repertório por papel de slide, anti-estética) e congela tudo num arquivo `[NomeDaPasta]_ESTILO.md` salvo NA PRÓPRIA PASTA. Esse arquivo é o briefing congelado que a skill invisible-carrossel-visual lê depois, em vez de re-analisar as imagens a cada carrossel — mais barato, mais rápido e idêntico toda vez. Decompõe grids (uma imagem em grade 3×3 = 9 referências). NÃO gera imagem nem renderiza carrossel — só produz o contrato de estilo. Use SEMPRE que o usuário pedir para "decodificar esse estilo", "gerar o _ESTILO desse carrossel", "criar o briefing visual dessas referências", "congelar esse estilo", "analisar essa pasta de referências". Requer só uma pasta com imagens (não precisa de Higgsfield nem nada externo).
---

# Decodificador de Estilo Visual

Você transforma uma **pasta de referências visuais** num **briefing de estilo congelado** (`[NomeDaPasta]_ESTILO.md`). É a ferramenta que alimenta a `invisible-carrossel-visual`: ela lê o briefing que você produz, em vez de re-analisar as imagens a cada carrossel.

Seu trabalho é **olhar as referências de verdade** (visão) e descrever o sistema visual com precisão suficiente para um gerador de imagem reproduzi-lo. Você **não gera imagem nem carrossel** — só o contrato de estilo.

## Insumo

Uma **pasta com imagens** de inspiração de um estilo de carrossel. Pode ser:
- Imagens unitárias (uma capa, um post solto) — cada uma vale como 1 referência.
- **Grids** (print de feed, página de Behance, moodboard) — cada região do grid vale como referência independente. Um grid 3×3 entrega 9 referências.

## Fluxo

### Fase 1 — Ler as referências por visão
1. Liste as imagens da pasta.
2. **Abra cada imagem com o Read tool** (visão nativa). Para cada uma, decida: **unitária ou grid?** Se grid, decomponha mentalmente em N exemplares e observe cada um.
3. Ao observar, extraia com precisão:
   - **Conceito** — o que o estilo imita ou é (ex.: "mockup do app de Notas do iOS", "revista editorial", "cartão de citação").
   - **Moldura / elementos fixos** (detail signature) — o que se repete em TODOS os exemplares (barra de topo, rodapé, assinatura, micro-grafismo). É o que faz o feed parecer uma coleção curada.
   - **Modos de fundo** — claro / escuro / colorido, com as **cores observadas** (aproxime em hex).
   - **Registro tonal** — predominante claro, médio ou escuro. **Regra:** não escureça além do que as refs mostram. Se as refs são claras, o estilo é claro.
   - **Tipografia** — a fonte (nomeie se reconhecer; senão descreva: "sans-serif neutra do sistema", "serifada de display"), pesos, caixa (sentence/uppercase). Trave: um valor por papel, não faixa.
   - **Accent** — como o destaque é feito, com precisão. (Ex.: "bloco de seleção retangular amarelo, bordas retas" é diferente de "pincelada com bordas irregulares" — descreva o certo.)
   - **Repertório por PAPEL de slide** — observe como é a **capa**, como são os **internos** e como é o **fecho** nas refs. Cada papel tem um tratamento próprio. Isto é crítico: sem ele, a render trata interno como capa.
   - **Recursos de conteúdo recorrentes** — listas, contrastes (❌/✅), setas, CTAs, que aparecem nas refs.
   - **Anti-estética** — o que o estilo NUNCA tem (e que o gerador deve evitar).

> **Dois erros a neutralizar no briefing:** (1) puxar a paleta pro escuro quando as refs são claras/médias; (2) descrever o accent/elementos de forma vaga. Seja literal.

### Fase 2 — Escrever o `[NomeDaPasta]_ESTILO.md`
Derive o nome do arquivo do **nome da pasta de referências** (ex.: pasta `Notes/` → `Notes_ESTILO.md`; pasta `Citacao Serif/` → `Citacao_Serif_ESTILO.md`, espaços viram `_`). Salve **na própria pasta de referências**.

O arquivo segue esta estrutura (todas as seções):
1. **Cabeçalho** — o que é o arquivo, que é o briefing congelado lido pela `invisible-carrossel-visual`, quando re-decodificar, e a data.
2. **Conceito.**
3. **Moldura fixa / detail signature** (em todos os slides).
4. **Modos de fundo** (cores).
5. **Tipografia travada** (copiar verbatim no prompt).
6. **Accent** (preciso).
7. **Papel do slide** — repertório de capa / interno / fecho. **Regra dura: só a capa usa tratamento de capa; interno e fecho usam hierarquia de conteúdo, nunca título-gigante-isolado.**
8. **Recursos de conteúdo recorrentes.**
9. **Anti-estética.**
10. **Formato** (3:4 para a Higgsfield CLI; a "peça" preenche o quadro 3:4).
11. **Bloco pronto para injeção no prompt** — um bloco em inglês que a skill de render cola direto no prompt do gerador, contendo VISUAL STYLE, FRAME, BACKGROUND, TYPOGRAPHY (locked), ACCENT, SLIDE ROLE e DO NOT.

> Use o `Notes_ESTILO.md` (pasta de referências `Notes/`) como **gabarito de estrutura e nível de detalhe** se existir no ambiente.

### Fase 3 — Salvar e resumir
1. Salve o arquivo na pasta de referências.
2. **Mostre ao usuário um resumo** do que foi decodificado (conceito + paleta + tipografia + papéis de slide em poucas linhas) e onde salvou. O `[Pasta]_ESTILO.md` é editável à mão: avise que ele pode ajustar o arquivo se quiser refinar.

## Guardrails
- **Olhe as imagens de verdade** (visão). Nunca invente um estilo que as refs não mostram.
- **Não escureça além das refs.** O registro tonal observado manda.
- **Seja literal no accent e na moldura.** Vago gera render errado.
- **Sempre inclua o repertório por papel de slide.** É o que evita interno-com-cara-de-capa.
- **Nome do arquivo = nome da pasta + `_ESTILO.md`**, salvo na própria pasta.
- Você **não gera imagem nem carrossel**. Só o contrato de estilo.
