# CLAUDE.md — Instruções do plugin `invisible-slides-plan-visual`

Este arquivo orienta qualquer instância de Claude (Claude Code, Cowork) que trabalhe neste plugin. Leia antes de editar.

## O que é este plugin

O **renderizador genérico** de slides. Pega um PLANO de slides (contrato `slides-plan` v1) e produz uma apresentação **HTML auto-contida** segundo um **design system** (pasta `design-systems/`). É a metade **visual** da criação de slides: não sabe pedagogia, só transforma semântica (o plano) em estética (pixels). Consome o plano da `invisible-class-slides-plan` e também storyboards da `invisible-doc-to-presentation` — é genérico de propósito. A skill é **fina** (orquestra); o conhecimento vive em `skills/invisible-slides-plan-visual/references/` e o visual nos `design-systems/`. Veja o `README.md` para a visão completa.

## Princípios (não quebrar ao editar)

1. **Skill fina, visual nos design systems.** A skill orquestra (intake, mapeamento, render) e **aponta** para as references e o design system. Não embuta CSS nem template no SKILL.md; consome o design system escolhido. Mantenha o SKILL.md < 500 linhas.
2. **O design system manda no visual.** A aparência (cores, tipografia, classes de slide, template HTML, player) vive no design system e é seguida à risca. **Escala refinada sempre** — inflar a tipografia foi o erro do plugin antigo; não repita.
3. **Fidelidade ao plano.** Renderize o que o plano diz. Não reescreva conteúdo, não reordene slides, não "melhore" o argumento — isso é decisão do plano (didática), não do renderizador.
4. **Genérico, nunca quebra.** Tipo desconhecido → fallback `s-conteudo` + comentário HTML. Qualquer plano no contrato v1 renderiza, venha de aula ou não.
5. **Não inventar dado.** Gráfico com número real é renderizado de verdade (SVG/código), **nunca** "desenhado" por modelo de imagem.
6. **HTML auto-contido.** Um único arquivo, sem dependências além de Google Fonts via CDN. Nunca entregar HTML quebrado.

## References (a base de conhecimento)

Vivem em `skills/invisible-slides-plan-visual/references/`. Citam-se por caminho relativo; mantenha-as coerentes nos dois sentidos. São:

- `slides-plan-spec.md` — o contrato `slides-plan` v1 (lado consumidor): o que esta skill honra e o que ignora.
- `tipo-layout-map.md` — tabela tipo-didático → classe CSS, com a regra de fallback.
- `producao-visual.md` — roteamento de imagem, 4 modos, chart real, detecção de gerador em runtime.

## A fronteira com o gerador de planos

O contrato `slides-plan` v1 é a keystone entre os dois plugins. A mesma spec vive aqui (`references/slides-plan-spec.md`, lado consumidor) e na `invisible-class-slides-plan` (lado emissor, com o vocabulário completo de tipos em `tipologia.md`). **Ao mudar o formato do plano, atualize os dois lados e a versão do contrato** — senão o renderizador deixa de entender o que o gerador emite. Ao surgir um tipo novo na tipologia do gerador, mapeie-o em `tipo-layout-map.md`.

## Design systems (extensível)

- Vivem em `design-systems/`, na raiz do plugin. A skill os referencia a partir de `../../design-systems/` (dois níveis acima de `skills/invisible-slides-plan-visual/`) e confirma o caminho com `ls ../../design-systems/` antes de ler. **Mantenha esse padrão** — é o mesmo dos plugins `invisible-copy` e `invisible-doc-to-presentation` e funciona quando o plugin está instalado em outra máquina. Não troque por caminho absoluto nem variável no corpo em prosa do SKILL.md.
- O `invisible.md` deste plugin **adota integralmente** a inteligência visual da `invisible-doc-to-presentation` (a versão oficial testada): paleta, tipografia, escala, o sistema de classes `s-*` e o template. É um **sistema misto** (cada tipo decide fundo claro/escuro; o claro recebe a classe `light`), não um modo escuro fixo. Sobre essa base estão acopladas as extensões da aula: o player com **builds** (`fragment`) e 5 layouts didáticos extras (`s-timeline`, `s-chart`, `s-image`, `s-prompt`, `s-divider`) desenhados na **mesma escala e linguagem** `s-`. **Não alterar a lógica visual oficial — só acrescentar.** Há um comentário de proveniência no topo do arquivo; em mudança de marca, sincronize manualmente com a fonte (`invisible-doc-to-presentation/design-systems/invisible.md`).
- Adicionar um novo: criar um `.md` em `design-systems/` no formato do `invisible.md` (paleta, tipografia, fundamentos, tabela tipo→classe, template HTML completo com player, instruções). A skill o descobre sozinha — não é preciso editar o SKILL.md. Padrão = `invisible`.

## Geração de imagem (portabilidade)

Os Modos visuais 2 e 3 dependem de uma ferramenta MCP de geração de imagem. A skill **descobre em runtime** se existe na sessão; se houver, usa; se não, avisa e cai para Modo 0/1. **Nunca** referencie um ID/nome de servidor MCP específico (ex.: `mcp__<hash>__...`) no SKILL.md ou nas references: esses IDs são da instalação de quem criou e não existem em outra máquina. Stock free e desenho em código sempre funcionam.

## Convenções

- **Nomes de arquivo:** kebab-case, sem espaços.
- **Idioma:** PT-BR.
- **Skill:** vive em `skills/<nome>/SKILL.md`, com prefixo `invisible-` no `name:` do frontmatter (convenção da Invisible — invocável como `/invisible-...`).
- **Output** (o HTML) vai para a mesma subpasta do plano no workspace do usuário (tipicamente `class-slides/[nome-slug]/[nome-slug].html`) — não versionado.

## Versionamento (semver)

A versão do plugin vive em `.claude-plugin/plugin.json` (campo `version`). Toda mudança que vai para a `main` e altera o comportamento do plugin precisa de bump — senão o marketplace não entrega nada novo a quem já instalou.

- **patch** (1.0.0 → 1.0.1): correção de bug, ajuste de texto, ponteiro quebrado, ajuste fino de CSS.
- **minor** (1.0.0 → 1.1.0): recurso novo compatível (design system novo, layout novo, passo novo no fluxo, extensão compatível do contrato).
- **major** (1.0.0 → 2.0.0): mudança incompatível (renomear/remover a skill, **quebra do contrato slides-plan** que exige o gerador mudar junto).

Mudanças que **não** mexem no plugin entregue (só README/CLAUDE, organização interna) não exigem bump.

## Fluxo de trabalho (Git)

1. Edite os arquivos locais conforme o pedido.
2. Garanta a coerência das referências cruzadas; rode `grep -rn` antes de concluir mudança estrutural. Se mexer no contrato, atualize também o plugin gerador.
3. **Suba a versão em `.claude-plugin/plugin.json`** quando o comportamento do plugin mudar.
4. Commit com mensagem que descreve a intenção (`feat(...)`, `fix(...)`, `refactor:`, `docs:`, `chore:`).
5. Faça push apenas quando o usuário pedir.

## O que NÃO versionar

O `.gitignore` do repo ignora `.DS_Store` e `*.log`. As saídas da skill (o HTML) vão para a subpasta do plano no workspace do usuário e não devem ser commitadas no plugin.
