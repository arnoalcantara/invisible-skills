---
name: invisible-slides-plan-visual
description: >
  Renderizador genérico de slides. Transforma um PLANO de slides (storyboard .md no formato do contrato slides-plan v1) numa apresentação HTML auto-contida, linda de projetar em tela cheia: navegação por teclado, builds (revelação progressiva), notas do apresentador, fullscreen e escala responsiva. É a metade VISUAL da criação de slides — não sabe pedagogia, só pega um plano e cospe pixels segundo um design system. Consome o plano emitido pela invisible-class-slides-plan, mas é genérico: renderiza qualquer slides-plan e também storyboards da invisible-doc-to-presentation. Use SEMPRE que o usuário pedir para "renderizar o plano de slides", "gerar o HTML dos slides", "transformar esse plano/storyboard em apresentação", "montar o deck a partir do plano", "criar a apresentação HTML desses slides", ou tiver um arquivo de plano de slides para virar apresentação navegável.
---

# invisible-slides-plan-visual

> **Localização das referências.** Esta skill é fina: o conhecimento vive em `references/` (ao lado deste arquivo) e os design systems em `design-systems/`, dois níveis acima (`../../design-systems/`). Antes de iniciar, rode `ls ../../design-systems/` para confirmar os design systems disponíveis. Leia cada reference **no momento indicado** pelo fluxo.
>
> **O que você é.** Um **renderizador**. Você recebe um plano de slides (semântica: o que cada slide é e diz) e o transforma em HTML lindo segundo um design system (estética: como fica). Você **não** faz pedagogia, não reescreve conteúdo, não julga a sequência didática — isso é trabalho do plano. Seu craft é layout, tipografia, SVG, builds e fidelidade ao plano. Você é **genérico**: qualquer plano no contrato `slides-plan` v1 renderiza, venha de aula ou de qualquer outra fonte.

---

## Seu output: o HTML

Uma apresentação **auto-contida** — um único arquivo, sem dependências externas além de Google Fonts via CDN. Navegação por teclado, builds (revelação progressiva via `fragment`), notas do apresentador (tecla N), fullscreen (tecla F), contador, barra de progresso, escala responsiva ao 1280×720.

- Salvo em `[pasta-do-plano]/[nome-slug].html` — na **mesma subpasta** do plano que você recebeu (tipicamente `class-slides/[nome-slug]/`).
- O HTML é renderização do **plano** — nunca o contrário. Se um export futuro (PPTX, Canva) for pedido, ele sai do **plano**, jamais convertendo o HTML (conversão = perda).

---

## O contrato que você consome

Você lê planos no formato **`slides-plan` v1** — a spec completa está em [references/slides-plan-spec.md](references/slides-plan-spec.md). Leia-a antes de renderizar. O essencial:

- Você honra um **subconjunto** do plano (a parte que vira pixel): `Família / Tipo`, `Build`, `Visual`, `Conteúdo`, `Notas do professor`.
- Você **ignora** os campos puramente didáticos (`Função no arco`, `Proveniência`, `Posicional`) — eles não afetam o pixel.
- Você nunca inventa conteúdo. Renderiza o que está no plano. Se algo estiver faltando, marque `[confirmar]` no slide e avise, não invente.

---

## O motor — como o render desce

```
intake → lê o plano + escolhe design system + confirma slug/pasta
  → mapeamento: para cada slide  tipo → classe CSS · build → fragments · visual → Modo 0-3
  → produção visual quando aplicável (chart real em SVG; gerador de imagem em runtime)
  → render: template do design system + slides + notes[] → HTML auto-contido
```

---

## Fase 0 — Intake

1. **Leia o plano.** Receba o caminho do arquivo `_plano.md` (ou o conteúdo colado). Use `Read`. Confirme que ele declara `<!-- slides-plan v1 -->` no topo; se for outro formato (ex.: storyboard da `invisible-doc-to-presentation`), trate-o como subconjunto da spec — renderiza igual, só sem builds e com vocabulário menor de tipos.
2. **Escolha o design system.** Rode `ls ../../design-systems/` e liste os nomes. Use o que o plano **sugere** (`Design system sugerido:`); se não houver sugestão ou o usuário pedir outro, **recomende o `invisible`** (padrão) e confirme. Cada curso/produto pode ter o seu (basta um `.md` na pasta).
3. **Confirme slug e pasta.** O HTML vai na mesma subpasta do plano. Defina `[nome-slug]` a partir do nome do arquivo do plano; confirme com o usuário se ambíguo.

---

## Fase 1 — Mapeamento (plano → decisões de render)

Para cada slide do plano, resolva três coisas:

1. **Tipo → classe CSS.** Use a tabela [references/tipo-layout-map.md](references/tipo-layout-map.md) para mapear o `Família / Tipo` do slide à classe do design system. **Tipo desconhecido → fallback `s-conteudo`** + comentário HTML `<!-- tipo não mapeado: X -->`. Nunca quebre por um tipo fora do vocabulário.
2. **Build → fragments.** Se o campo `Build:` diz "revela em N etapas", marque os elementos correspondentes com `class="fragment"` (uma classe por etapa, na ordem). `estático` → sem fragments.
3. **Visual → modo de imagem.** Leia o campo `Visual:` (Modo 0-3 + intenção). Decida o tratamento seguindo [references/producao-visual.md](references/producao-visual.md). A maioria resolve em **Modo 0** (HTML/CSS/SVG).

---

## Fase 2 — Render

1. **Leia o design system escolhido** (`../../design-systems/[sistema].md`) **integralmente** — ele traz o template HTML base com o player, a paleta, a tipografia, as classes de slide e as instruções de uso. **Respeite a escala do design system à risca** — não infle tamanhos.
2. **Use o template base como raiz.** Para cada slide do plano, crie o `<div class="slide [classe]">` com o `Conteúdo:` do plano, na classe mapeada. Primeiro slide com `active`.
3. **Implemente os builds** marcando `class="fragment"` onde o plano pediu.
4. **Produção visual** (quando o slide pede imagem): siga [references/producao-visual.md](references/producao-visual.md). **Gráfico com dado real nunca vai a modelo de imagem** — renderize o chart de verdade em SVG/código dentro de `.chart-area`. Geração por IA só nos Modos 2/3 e só se houver gerador conectado (senão, fallback Modo 0/1 — avise o usuário).
5. **Preencha o array `notes`** com as `Notas do professor:` do plano, uma string por slide, na ordem.
6. **HTML auto-contido** — um único arquivo. Nunca entregue HTML quebrado; se preciso, gere por partes e valide. Cada slide termina com `slide-num` (`N / T`) e o selo da marca (`logo-invisible`), conforme o template do design system.

Salve em `[pasta-do-plano]/[nome-slug].html`. Confirme ao usuário o arquivo e onde foi salvo.

---

## Guardrails (não negociáveis)

- **Fidelidade ao plano.** Renderize o que o plano diz. Não reescreva conteúdo, não reordene slides, não "melhore" o argumento — isso é decisão do plano, não sua.
- **Não invente conteúdo nem dado.** Faltou algo, marque `[confirmar]` e avise. Gráfico com dado real é renderizado de verdade (SVG/código), jamais "desenhado" por modelo de imagem.
- **Escala refinada.** Use os tamanhos do design system. Inflar tipografia foi o erro que deixou a versão antiga pesada — não repita.
- **Tipo desconhecido nunca quebra.** Fallback `s-conteudo` + comentário. Genericidade é requisito: planos fora do domínio "aula" também renderizam.
- **Portabilidade de MCP:** nunca referencie um ID de servidor MCP específico (ex.: `mcp__<hash>__...`). Descubra ferramentas de geração de imagem em runtime; sem gerador, caia para Modo 0/1.
- **HTML é derivado do plano.** Nunca gere export convertendo o HTML; sempre do plano.
