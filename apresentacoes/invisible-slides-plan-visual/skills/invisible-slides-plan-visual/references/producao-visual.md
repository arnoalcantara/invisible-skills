# Produção visual — roteamento, modos e geração de imagem

> **Propósito.** A skill não "gera imagem"; faz **raciocínio visual em duas etapas** (diagnóstico de ferramenta → geração do prompt), invisível ao usuário. Este módulo evita os dois erros clássicos: pedir a um modelo de imagem algo que ele estraga (números, texto preciso) e poluir slides com imagem decorativa que gasta carga extrínseca (lei 3).
> **Lugar na cadeia:** última camada (filosofia → arco → tipologia → **produção visual**). Leia na Passada 2, quando um slide pede imagem.

---

## Os quatro modos visuais (Dial 2)

Definidos no arranque. Default conservador.

- **Modo 0 — Sem imagem.** Só o que o Claude desenha sozinho: tipografia, cor, layout, diagramas em HTML/CSS/SVG. Limpo, rápido, sempre disponível, totalmente fiel às 13 leis. **Melhor default para a maioria das aulas.**
- **Modo 1 — Stock free.** Foto de banco gratuito quando uma imagem *real* ajuda (uma planta, um instrumento, um lugar) e gerar seria desperdício.
- **Modo 2 — Geração sem texto.** Visual conceitual, cena, metáfora — sem número nem texto crítico. O texto fica na camada do slide (editável, legível). Precisa de um gerador de imagem por IA conectado.
- **Modo 3 — Geração com texto embutido.** Só quando o texto *é* a arte (slide-pôster, rótulo cozido num diagrama estilizado). **Exceção, não regra** — texto editável na camada do slide quase sempre vence texto cozido na imagem. Precisa de gerador conectado.

No Modo Transcrição, prefira *sugerir* onde uma imagem agregaria, em vez de espalhar imagem por todo slide.

---

## Portabilidade: detecção de gerador em runtime (regra dura)

Os Modos 2 e 3 dependem de uma ferramenta MCP de **geração de imagem** conectada à sessão. **Não assuma que existe e NUNCA fixe o nome de um servidor MCP no texto** (ex.: `mcp__<hash>__...` ou um nome de produto específico). Esses IDs pertencem à instalação de quem criou a skill e não existem em outra máquina — é o erro que o plugin-irmão já pagou para aprender.

No momento de gerar imagem:
1. **Descubra em runtime** se há na sessão alguma ferramenta MCP capaz de gerar imagem (procure pela função, não por um nome fixo).
2. **Se houver**, use-a; descubra os parâmetros/modelos que ela expõe naquele momento (não hardcode slugs frágeis).
3. **Se não houver**, **avise o usuário** ("não há gerador de imagem conectado nesta sessão; sigo em Modo 0/1") e **caia para o Modo 0/1**. Nunca pare a entrega por falta do gerador, nunca invente uma imagem.

Stock free (Modo 1) e desenho em código (Modo 0) **sempre** funcionam, em qualquer máquina.

---

## Etapa A — Diagnóstico e roteamento de ferramenta (a árvore que evita erro)

A partir da **função do slide**, decida o visual e **qual ferramenta resolve**:

- **Gráfico com dado real** (números que precisam estar corretos: barras, linhas, pizza, dispersão) → **NUNCA** um modelo de imagem. Ele inventa número e desalinha eixo. Renderize o **gráfico de verdade** em código/SVG (ou biblioteca de chart). Um gerador de imagem, se usado, só estiliza fundo/moldura — **jamais plota o dado.**
- **Visual conceitual / metáfora / cena / ideia-em-imagem** (sem número crítico) → é onde a geração por IA (Modo 2) brilha. Roteie para o gerador, se houver.
- **Diagrama estrutural** (anatomia rotulada, fluxo, comparação, taxonomia) → **Modo 0 em HTML/CSS/SVG**, quase sempre. Estrutura com rótulos precisos é trabalho de código, não de modelo de imagem (rótulo cozido fica ilegível e não editável).
- **Infográfico** → híbrido. Com dado = composição (chart real renderizado + arte ao redor). Conceitual (processo/anatomia estilizada, sem números críticos) = pode ir ao gerador, com cuidado redobrado em texto. Use com parcimônia (composto = mais carga).
- **Imagem real de algo que existe** (uma obra de arte, um animal, um aparelho) → Modo 1 (stock) costuma bastar e é mais honesto que gerar.

Regra de ouro do roteamento: **se o erro do modelo seria invisível para você mas grave para o aluno (um número errado, um rótulo trocado), não use o modelo.**

---

## Etapa B — Geração do prompt (ficha de prompt de imagem)

Quando rotear para um gerador (Modo 2/3), todo prompt tem slots fixos:

- **Sujeito + intenção didática** — o que a imagem precisa *ensinar* (não só "o que mostrar"). A imagem serve à ideia do slide.
- **Composição com espaço negativo planejado** — onde o título/rótulo entra na camada do slide. Ex.: "sujeito à direita, terço esquerdo limpo para sobreposição de título".
- **Tratamento de texto** — regra geral: peça imagem **sem texto embutido** (texto vai na camada do slide, editável e legível). Exceção = Modo 3.
- **Âncora de estilo** — injeta o *style bible* do deck (abaixo).
- **Aspect ratio + resolução** — 16:9, alta resolução, definido uma vez para o deck.
- **Negativos** — clichê de banco de imagem, número inventado, texto borrado, poluição visual, marca d'água.

---

## Style bible (coerência do deck)

O que faz 30 imagens parecerem do mesmo deck. Mesma lógica das 13 leis: define no topo, cascateia.

1. **Entrada de estilo:** o usuário manda uma referência visual, OU a skill puxa do contexto de curso/produto (paleta, tipografia, tom), OU — se não houver nada — a skill propõe um.
2. **Destilação:** transforme em um *style bible* curto: paleta, tratamento de imagem (flat / editorial / 3D / linha / fotográfico), mood, e uma lista de *do's e don'ts*.
3. **Herança:** **todo** prompt de imagem injeta o style bible. Para elementos recorrentes (um mascote, um personagem-guia, o produto), use a consistência de sujeito/personagem que o gerador oferecer, ao longo do deck.

O style bible também orienta o Modo 0: a paleta e a tipografia vêm do **design system escolhido** (`../../design-systems/[sistema].md`), que é a fonte visual primária. O style bible de imagem deve *concordar* com o design system, não brigar com ele.

---

## Como a IA deve usar este documento

- Decida o visual **slide a slide**, pela função — não escolha "o deck terá imagens" no atacado.
- Rode a árvore da Etapa A antes de qualquer geração. A maioria dos slides didáticos resolve em Modo 0.
- Antes de chamar um gerador, confirme que ele existe na sessão (regra de portabilidade). Sem ele, Modo 0/1.
- Para gráfico com dado, renderize de verdade. Sempre.

---

## Cruzamento com os outros módulos

- [slides-plan-spec.md](slides-plan-spec.md) — o campo `Visual:` do plano (Modo 0-3 + intenção) é o que este documento ensina a tratar.
- [tipo-layout-map.md](tipo-layout-map.md) — a classe de slide escolhida (ex.: `.slide-chart`, `.slide-image`) condiciona o tratamento visual.
- O design system em `../../design-systems/[sistema].md` é a fonte da paleta, tipografia e tipos de slide; o Modo 0 (HTML/CSS/SVG puro) vive nativo no render. O style bible de imagem deve concordar com ele.

> **Nota de proveniência.** Este documento veio do plugin antigo `invisible-class-slides`, que misturava didática e visual. As leis citadas no corpo (carga mínima, ponto focal, rótulo junto, espaço em branco) vivem agora no lado didático (`invisible-class-slides-plan/references/filosofia.md`); aqui funcionam como princípios de bom render, não como dependência de arquivo.
