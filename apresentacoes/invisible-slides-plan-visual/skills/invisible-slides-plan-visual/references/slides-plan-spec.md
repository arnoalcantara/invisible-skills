# Contrato `slides-plan` v1 — lado consumidor

> **Propósito.** A spec do formato que esta skill **consome**. É emitida pela `invisible-class-slides-plan` (lado emissor) e renderizada aqui. A mesma versão (`v1`) vive nos dois plugins; é a keystone que os mantém desacoplados.
> **Princípio.** O plano carrega **semântica** (o que o slide é e diz). Você, renderizador, decide a **estética** (o pixel) segundo o design system. Você honra um **subconjunto** do plano — a parte que vira pixel — e ignora o resto sem reclamar.

---

## Cabeçalho do arquivo

Todo plano começa com:

```markdown
<!-- slides-plan v1 -->
# [Título]
**Design system sugerido:** invisible
**Total de slides:** N
```

- A linha `<!-- slides-plan v1 -->` declara a versão do contrato — confirme que você entende esse formato. Se vier sem ela (ex.: um storyboard da `invisible-doc-to-presentation`), trate como subconjunto válido: renderiza igual, só sem builds e com vocabulário menor de tipos.
- **Design system sugerido** é só um ponteiro; você confirma/troca na Fase 0.

---

## Bloco por slide

```markdown
## Slide N — [título-asserção]

**Família / Tipo:** B / asseracao-evidencia
**Função no arco:** Desenvolver
**Proveniência:** aula, trecho X | adicionado-IA
**Build:** estático | revela em N etapas — [descreve cada etapa]
**Visual:** Modo 0 + [o que o olho vê]
**Conteúdo:** [a asserção do título + as peças de evidência — texto literal]
**Posicional:** de onde venho · que faço · pra onde aponto
**Notas do professor:** [o que a voz carrega]
```

---

## O que você honra vs. ignora

| Campo | Você | Como |
|---|---|---|
| **título-asserção** | honra | vira o `<h2>` / título do slide |
| **Família / Tipo** | **honra (load-bearing)** | chave da tabela [tipo-layout-map.md](tipo-layout-map.md) → classe CSS. Desconhecido → fallback `.slide-content` + comentário |
| **Função no arco** | **ignora** | didático; não afeta pixel |
| **Proveniência** | **ignora** | contrato de fidelidade do lado didático; não afeta pixel |
| **Build** | **honra** | `revela em N etapas` → elementos `class="fragment"`, um por etapa, na ordem. `estático` → sem fragments |
| **Visual** | **honra** | `Modo 0-3` + intenção → tratamento (desenho/SVG/stock/geração). Ver [producao-visual.md](producao-visual.md) |
| **Conteúdo** | **honra** | o texto literal que entra no slide. Não reescreva |
| **Posicional** | **ignora** | consciência didática; não afeta pixel |
| **Notas do professor** | **honra** | preenche o array `notes[]` do player, uma string por slide |

> Ignorar ≠ apagar. Você apenas não transforma esses campos em pixel. Eles existem para o controle humano e a fidelidade, do lado do plano.

---

## Regras de consumo

- **Fidelidade ao plano.** Renderize o que está lá. Não invente conteúdo, não reordene, não "melhore". Faltou algo → `[confirmar]` + avise.
- **Dado real → chart real.** Se o `Visual:` indica gráfico com número, renderize em SVG/código (nunca imagem gerada).
- **Nunca quebre.** Tipo fora do vocabulário, campo ausente, build malformado → degrade com elegância (fallback + comentário), não pare.
- **Genericidade.** Nenhum campo honrado pressupõe "aula". Um plano de qualquer domínio (e storyboards da `invisible-doc-to-presentation`) renderiza por esta mesma spec.

---

## Cruzamento

- [tipo-layout-map.md](tipo-layout-map.md) — traduz `Família / Tipo` em classe CSS.
- [producao-visual.md](producao-visual.md) — como tratar o campo `Visual:`.
- Lado emissor: a mesma spec vive em `invisible-class-slides-plan` (`references/slides-plan-spec.md`), com o vocabulário completo de tipos (`tipologia.md`). **Mudou o formato? Atualize os dois lados e a versão.**
