# ADR — Separar `invisible-class-slides` em didática + visual

**Status:** proposto (aguardando aprovação do Arno)
**Data:** 2026-06-18
**Decisão de origem:** a skill atual faz bem o roteiro didático (Passada 1) e mal o visual (Passada 2). Separar, como se fez no copy.

---

## 1. Diagnóstico

A `invisible-class-slides` já trabalha em duas passadas com um portão de aprovação no meio:

```
Passada 1 (didática)  →  PLANO de slides (.md)  →  [aprovação]  →  Passada 2 (visual)  →  HTML
```

A própria skill declara isso como **regra inviolável** (em `references/outputs.md`): *o plano é a fonte da verdade; o render é derivado*. A costura entre conteúdo e forma não é nova — já é sagrada dentro da skill. O problema é que as duas metades moram no mesmo arquivo e a metade ruim (visual) contamina a boa quando a gente mexe (foi o que matou a v1.1.0 e a v1.2.0).

**Prova de que o corte está no osso certo:** a metade didática não precisa saber nada de HTML; a metade visual não precisa saber nada de pedagogia. Quando os dois lados se ignoram limpos assim, a fronteira é real.

---

## 2. Decisão de arquitetura

**Dois plugins**, não um só com duas skills.

| Plugin | Papel | Entrada | Saída | Sabe de... | NÃO sabe de... |
|---|---|---|---|---|---|
| `invisible-class-slides-plan` | Designer instrucional. Transforma aula em arquitetura didática. | transcrição / roteiro / esboço de aula | **slides-plan** (`.md`) | ciência da aprendizagem, arco, tipologia, proveniência | HTML, CSS, design systems, geração de imagem |
| `invisible-slides-plan-visual` | Renderizador genérico. Transforma um plano em deck bonito. | qualquer **slides-plan** (`.md`) | HTML auto-contido | design systems, layout, tipografia, SVG, geração de imagem | pedagogia, arco, fidelidade ao professor |

### Por que dois plugins e não um (como o copy)?

O copy é um plugin só com duas skills porque as duas servem **só ao copy**. Aqui é diferente: a skill visual é **genérica** (sua escolha). Um renderizador que pega um *slides-plan* e cospe HTML não tem nada de "aula" — pode servir a `invisible-doc-to-presentation` (que hoje tem o próprio renderizador, redundante) e a qualquer deck futuro. Acoplá-lo ao plugin de aula mataria essa reutilização. Plugin próprio = o renderizador vira infraestrutura compartilhável.

Custo assumido: duas versões para versionar em vez de uma. Vale pelo reuso.

---

## 3. O contrato: o formato **slides-plan**

É a keystone. Se for bem definido, os dois plugins encaixam; se for frouxo, recriamos a bagunça em dois lugares. O nome no meio dos dois plugins (`...-plan` / `...-plan-visual`) é justamente o contrato.

O formato **já existe** hoje (SKILL.md, Passada 1). Vamos promovê-lo a **spec versionada**, presente nos dois plugins: um declara "isto é o que eu emito", o outro "isto é o que eu consumo".

Bloco por slide (v1 do contrato):

```markdown
## Slide N — [título-asserção]

**Família / Tipo:** B / asseracao-evidencia        ← vocabulário fechado (8 famílias, ~47 tipos)
**Função no arco:** Desenvolver                     ← Fisgar|Orientar|Ativar|Desenvolver|Processar|Consolidar|Fechar
**Proveniência:** aula, trecho X | adicionado-IA    ← contrato de fidelidade
**Build:** estático | revela em N etapas (descreve)
**Visual:** Modo 0 + o que o olho vê                ← Modo 0/1/2/3; descreve a intenção, não o CSS
**Conteúdo:** a asserção + as peças de evidência
**Posicional:** de onde venho · que faço · pra onde aponto
**Notas do professor:** o que a voz carrega
```

**Princípio do contrato:** o plano carrega **semântica** (o que o slide é e diz), nunca **estética** (como ele fica). O campo `Família/Tipo` diz ao renderizador qual layout escolher; o campo `Visual` descreve a *intenção* visual, não o pixel. Quem decide o pixel é o design system, do lado visual. É isso que mantém a separação honesta.

O **vocabulário de tipos** (as 8 famílias / ~47 tipos da tipologia) faz parte do contrato: o lado visual precisa conhecer o universo de tipos para mapear cada um a uma classe/layout do design system.

---

## 4. Mapa de migração dos arquivos

Partindo da v1.0.0 atual (estado bom, monolítico).

**Vão para `invisible-class-slides-plan` (didática):**
- `references/filosofia.md` — princípio-mestre + 13 leis
- `references/arco-da-aula.md` — arco, consciência posicional
- `references/tipologia.md` — 8 famílias, ~47 tipos
- `references/fichas/` — todas as fichas (anatomia, slots, regras de carga, build = estrutura didática)
- `references/proveniencia.md` — contrato de fidelidade
- `references/outputs.md` — só a metade "plano" (a metade "render/HTML" vai para o visual)
- a **spec do contrato slides-plan** (nova; declara o que emite)

**Vão para `invisible-slides-plan-visual` (visual):**
- `design-systems/` inteiro (hoje só `invisible.md`) — paleta, tipografia, tabela tipo→classe, template HTML
- `references/producao-visual.md` — 4 modos de imagem, detecção de gerador em runtime
- a craft de render (montar HTML, builds, player, notas, fullscreen)
- a **spec do contrato slides-plan** (mesma; declara o que consome)

**Detalhe das fichas:** ficam inteiras no lado didático (são majoritariamente estrutura de conteúdo). O pouco de "decisão visual" que carregam ou alimenta o campo `Visual:` do plano, ou migra para o design system durante a construção. O lado visual mapeia tipo→classe pelo design system, que já tem essa tabela.

---

## 5. Marketplace e migração

Estado atual: `invisible-class-slides` v1.3.0 publicada e instalável.

Proposta:
- **Remover** a entrada `invisible-class-slides` do `marketplace.json`.
- **Adicionar** `invisible-class-slides-plan` e `invisible-slides-plan-visual`.
- Quem tinha a antiga continua com ela instalada (não some da máquina), mas deixa de receber updates sob o nome antigo. Reinstalar sob os nomes novos.

Como é o seu próprio marketplace, o impacto é baixo. Cada plugin novo começa em `1.0.0`.

*(Alternativa, se preferir transição suave: manter `invisible-class-slides` como um plugin-casca que só aponta para os dois novos. Mais trabalho, provavelmente desnecessário. Recomendo remover.)*

---

## 6. O que este split NÃO resolve (honestidade de sócio)

Separar é **organização**, não conserta o visual sozinho. O visual feio vem do design system, não da fusão. O que o split entrega é o **lugar limpo** para atacar o problema: depois de separado, o `invisible-slides-plan-visual` nasce a partir do `invisible.md` da v1.0.0 (a melhor base visual que já tivemos) e a gente itera ali, sem risco de quebrar a didática e sem ressuscitar o base+skin (já tentado e rejeitado).

Sequência: **(1)** separar limpo, contrato fechado, paridade com o comportamento atual; **(2)** depois, e só depois, melhorar o craft visual dentro do plugin visual.

---

## 7. Plano de execução (worktree + branch)

1. Worktree isolada + branch `split/class-slides-plan-visual`.
2. Criar `apresentacoes/invisible-class-slides-plan/` — mover references didáticas, reescrever SKILL.md (Fase 0 + Passada 1 + emite slides-plan; remove tudo de HTML/design system), CLAUDE.md, README, plugin.json `1.0.0`.
3. Criar `apresentacoes/invisible-slides-plan-visual/` — mover design-systems + producao-visual, escrever SKILL.md (consome slides-plan + design system → HTML), CLAUDE.md, README, plugin.json `1.0.0`.
4. Escrever a **spec do contrato slides-plan** nos dois (fonte única de verdade do formato).
5. Atualizar `marketplace.json` (remove a antiga, adiciona as duas).
6. Remover `apresentacoes/invisible-class-slides/`.
7. Greps de coerência de referências cruzadas nos dois plugins.
8. **Você testa local:** rodar `invisible-class-slides-plan` numa aula → gerar um slides-plan → passar para `invisible-slides-plan-visual` → conferir o HTML. Confirmar paridade com o comportamento atual.
9. Aprovado → merge ff na main → push (você pediu antes; eu não empurro sem aval).

---

## 8. Decisões em aberto para você bater o martelo

1. **Dois plugins** (recomendado, honra o "genérico") **vs. um plugin com duas skills** (modelo do copy)?
2. **Remover** a `invisible-class-slides` do marketplace (recomendado) **vs. manter como casca de transição**?
3. **Escopo agora:** só separar a class-slides? Ou já apontar a `invisible-doc-to-presentation` para o renderizador novo nesta leva? (Recomendo deixar para depois — primeiro estabilizar o contrato.)
