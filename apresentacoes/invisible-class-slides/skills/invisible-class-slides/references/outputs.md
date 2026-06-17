# Os dois outputs — plano e render

> **Propósito.** Definir os dois entregáveis da skill, a relação entre eles e a regra inviolável que protege a fidelidade do design.
> **Lugar na cadeia:** fecha o ciclo. O Output 1 é o resultado da Passada 1; o Output 2, da Passada 2.

---

## Output 1 — Plano de slides (para aprovação)

O resultado da Passada 1: o storyboard slide-a-slide. Contém, para cada slide, a sequência de tipos, a função no arco, o mapa de proveniência, o modo visual, e os pontos de build e de processamento ativo. **É a fonte da verdade** — não um rascunho descartável.

- Salvo em `class-slides/[nome-slug]/[nome-slug]_plano.md`.
- O formato do bloco por slide está no SKILL.md (Passada 1).
- O usuário **aprova antes de qualquer render**. Este é o portão de controle humano.

---

## Output 2 — Render em HTML (a partir do plano aprovado)

**HTML é o entregável primário e único do v1.** É onde as 13 leis vivem com fidelidade total: tipografia, espaço e hierarquia ao pixel; o Modo 0 é HTML/CSS/SVG puro; os builds (revelação progressiva) funcionam nativamente; e o navegador em tela cheia apresenta lindo ao vivo.

- Salvo em `class-slides/[nome-slug]/[nome-slug].html`.
- Auto-contido: um único arquivo, sem dependências externas além de Google Fonts via CDN.
- Use a skill `frontend-design` como referência de qualidade visual quando precisar elevar o craft do HTML.
- O template base, os tipos de slide e as regras visuais vêm do **design system escolhido** (`../../design-systems/[sistema].md`) — leia-o integralmente antes de gerar.

---

## Regra inviolável: o plano é a fonte, o render é derivado

```
PLANO (aprovado)  ──render──▶  HTML
        │
        └──(roadmap)──▶  PPTX / Canva
```

Toda renderização sai do **mesmo plano aprovado**. **NUNCA** gere o HTML e depois converta para PPTX/Canva — conversão é perda de fidelidade. Se um export for pedido, ele se gera *do plano*, não do HTML.

---

## Roadmap de exports (fora do v1)

Documentados aqui para quando houver demanda; **não implementados no v1**:

- **PPTX — export opcional futuro.** Para quem precisa editar no PowerPoint ou projetar de qualquer lugar (caso Bernardo). Seja honesto quando chegar: é **downgrade de fidelidade** (via python-pptx; teto de design menor, builds mais toscos). Oferecer, nunca default. Gera-se do plano, slide a slide — não do HTML.
- **Canva — export opcional futuro (via MCP do Canva).** Meio-termo editável e apresentável sem código; geração mais templada/menos precisa que as fichas. Também sai do plano.

Quando um desses for implementado, é **recurso novo compatível** → bump **minor** no `plugin.json` (ver CLAUDE.md).

---

## Como a IA deve usar este documento

- Gere sempre o plano primeiro e **espere a aprovação**. Sem exceção.
- No v1, entregue HTML. Se o usuário pedir PPTX ou Canva, explique que é roadmap e ofereça o HTML (que projeta em qualquer navegador) como caminho atual.
- Nunca prometa fidelidade total em PPTX — quando existir, será um downgrade assumido.

---

## Cruzamento com os outros módulos

- [arco-da-aula.md](arco-da-aula.md) — Passada 1 → Output 1; Passada 2 → Output 2.
- [producao-visual.md](producao-visual.md) — o Modo 0 (HTML/CSS/SVG) vive nativo no render.
- [filosofia.md](filosofia.md) — o HTML é onde as 13 leis se realizam com precisão de pixel.
