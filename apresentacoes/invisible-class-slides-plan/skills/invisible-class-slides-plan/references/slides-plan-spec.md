# Contrato `slides-plan` v1 — lado emissor

> **Propósito.** A spec do formato que esta skill **emite** e que a `invisible-slides-plan-visual` **consome**. É a peça que mantém os dois plugins desacoplados: aqui se define o que um plano de slides carrega. O renderizador conhece a mesma spec do lado dele e sabe o que honrar.
> **Princípio.** O plano carrega **semântica** (o que o slide é e diz), **nunca estética** (como ele fica). Você descreve a *intenção* visual; o pixel é decisão do design system, do lado do renderizador.

---

## Cabeçalho do arquivo

Todo plano começa com:

```markdown
<!-- slides-plan v1 -->
# [Título da aula]
**Design system sugerido:** invisible
**Total de slides:** N
```

- A linha de comentário `<!-- slides-plan v1 -->` declara a versão do contrato. Mantenha-a — é como o renderizador confirma que entende o formato.
- **Design system sugerido** é uma *sugestão* (default `invisible`); o renderizador pode honrar ou trocar. Não é uma decisão estética sua, é um ponteiro.

---

## Bloco por slide

Para cada slide, um bloco neste formato exato (a ordem dos campos é fixa):

```markdown
## Slide N — [título-asserção]

**Família / Tipo:** B / asseracao-evidencia
**Função no arco:** Desenvolver
**Proveniência:** aula, trecho X | adicionado-IA
**Build:** estático | revela em N etapas — [descreve cada etapa]
**Visual:** Modo 0 + [o que o olho vê: diagrama, número, imagem, layout]
**Conteúdo:** [a asserção do título + as peças de evidência — texto literal que entra no slide]
**Posicional:** de onde venho · que trabalho faço · pra onde aponto
**Notas do professor:** [o que a voz carrega — o difícil de mostrar]
```

### Campos (definição e regras)

| Campo | O que é | Regra |
|---|---|---|
| **título-asserção** | O título do slide, em **frase completa que afirma** | "A pressão cai conforme a altitude sobe", nunca "Pressão e altitude". Lei 2. |
| **Família / Tipo** | Vocabulário fechado: 8 famílias (A–H), ~47 tipos | Escolhido pela *função didática*. É o campo **load-bearing**: o renderizador mapeia tipo → classe CSS. Use os nomes exatos da [tipologia.md](tipologia.md). |
| **Função no arco** | `Fisgar \| Orientar \| Ativar \| Desenvolver \| Processar \| Consolidar \| Fechar` | Didático. O renderizador **ignora**. |
| **Proveniência** | De onde veio o conteúdo do slide | `aula, trecho X` ou `adicionado-IA` / `pesquisado-IA`. Contrato de fidelidade ([proveniencia.md](proveniencia.md)). O renderizador **ignora**. |
| **Build** | Se o slide é estático ou revela em etapas | `estático` **ou** `revela em N etapas — [descreve cada etapa]`. O renderizador transforma cada etapa em elementos `class="fragment"`. |
| **Visual** | A **intenção** visual: o modo + o que o olho vê | `Modo 0/1/2/3` + descrição concreta da intenção ("diagrama de 3 caixas com seta", "número grande de impacto", "gráfico de barras com dado real"). **Descreve a intenção, nunca o CSS/pixel.** Dado real → diga "chart real" (Modo 0) para o renderizador desenhar de verdade. |
| **Conteúdo** | O **texto literal** que entra no slide | A asserção + as peças de evidência, já no fraseado final. Uma ideia por slide. Mostrar, não listar. |
| **Posicional** | Consciência posicional do slide | `de onde venho · que faço · pra onde aponto`. Didático. O renderizador **ignora**. |
| **Notas do professor** | O que a voz do professor carrega | O difícil de mostrar — vira a nota do apresentador no player. O renderizador **honra** (preenche `notes[]`). |

---

## O que o renderizador honra vs. ignora

O renderizador é genérico; consome um **subconjunto** do plano (a parte que vira pixel). Saber disso ajuda a escrever o campo certo com o peso certo.

| Campo | Renderizador | Como |
|---|---|---|
| Família / Tipo | **honra (load-bearing)** | chave da tabela tipo→layout → classe CSS |
| Build | **honra** | "revela em N etapas" → elementos `class="fragment"` |
| Visual | **honra** | Modo 0-3 + intenção concreta |
| Conteúdo | **honra** | texto que entra no slide |
| Notas do professor | **honra** | preenche `notes[]` do player |
| Função no arco · Proveniência · Posicional | **ignora** (didáticos) | não afetam o pixel; existem para o controle humano e a fidelidade |

Não corte os campos didáticos por isso: eles são o que o usuário aprova e o que protege a fidelidade. Eles só não viram pixel.

---

## Genericidade do contrato

Nenhum campo honrado menciona "aula" — por isso o renderizador é genérico. Um storyboard da `invisible-doc-to-presentation` (que usa um vocabulário de 8 tipos e não tem builds) é um **subconjunto válido** da spec v1 e renderiza também, só sem fragments. Tipo fora do vocabulário conhecido → o renderizador cai num fallback seguro (`.slide-content`) e nunca quebra.

---

## Cruzamento

- [tipologia.md](tipologia.md) — o vocabulário fechado de famílias/tipos que o campo `Família / Tipo` usa.
- [proveniencia.md](proveniencia.md) — o contrato que o campo `Proveniência` realiza.
- [filosofia.md](filosofia.md) — as 13 leis que governam o `Conteúdo` e o `título-asserção`.
- Do lado do renderizador, a mesma spec vive em `invisible-slides-plan-visual` com a tabela tipo→classe (`tipo-layout-map.md`).
