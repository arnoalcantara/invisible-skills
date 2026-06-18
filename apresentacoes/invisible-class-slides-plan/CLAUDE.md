# CLAUDE.md — Instruções do plugin `invisible-class-slides-plan`

Este arquivo orienta qualquer instância de Claude (Claude Code, Cowork) que trabalhe neste plugin. Leia antes de editar.

## O que é este plugin

A metade **didática** da criação de slides de aula. Transforma transcrição/roteiro/esboço de aula num **PLANO de slides** (storyboard) regido pela ciência da aprendizagem, no formato do contrato `slides-plan` v1. **Não gera HTML, não tem design system.** O render visual é feito pelo plugin irmão `invisible-slides-plan-visual`, que consome o plano. A skill é **fina** (orquestra); o conhecimento vive em `skills/invisible-class-slides-plan/references/`. Veja o `README.md` para a visão completa.

## Princípios (não quebrar ao editar)

1. **Skill fina, conhecimento nas references.** O SKILL.md orquestra (dials, Passada 1, output) e **aponta** para as references no momento certo. Nunca inline o conteúdo das references no SKILL.md. Mantenha o SKILL.md < 500 linhas.
2. **As 13 leis são a constituição.** Toda geração obedece ao princípio-mestre (memória de trabalho minúscula) e às 13 leis de `references/filosofia.md`. Não as enfraqueça.
3. **Emite semântica, nunca estética.** O plano descreve o que o slide é e diz (família/tipo, conteúdo, intenção visual), **jamais** CSS, cor, fonte ou pixel. Essa é a fronteira que mantém o plugin desacoplado do renderizador. Não traga HTML nem design system para cá.
4. **Portão de aprovação.** A Passada 1 gera o plano; o usuário **aprova**; só então o handoff para o renderizador. Nunca renderize aqui.
5. **Fidelidade à substância, liberdade na forma.** A skill reorganiza o linear da aula no arco e na tipologia, mas não inventa, não distorce, não "melhora" o argumento do professor. Material adicionado entra marcado (proveniência). Vale dobrado para conteúdo de formação/doutrinário.

## References (a base de conhecimento)

Vivem em `skills/invisible-class-slides-plan/references/`. Citam-se por caminho relativo e devem ser mantidas coerentes nos dois sentidos (regra de ouro: ao renomear/mover, atualize quem aponta). São:

- `filosofia.md` — princípio-mestre + 13 leis + foco (projeção ao vivo; autoestudo = roadmap).
- `arco-da-aula.md` — arco canônico, consciência posicional, processo de 2 passadas.
- `tipologia.md` — 8 famílias, ~47 tipos, TOC com link para cada ficha em `fichas/`.
- `fichas/` — uma ficha executável por tipo (gabarito fixo). ~15 completas + as demais enxutas.
- `proveniencia.md` — contrato de fidelidade e mapa de proveniência.
- `producao-visual.md` — roteamento de imagem (4 modos, regra de ouro do dado real): usado para **declarar** o campo `Visual:` de cada slide. A *execução* da imagem é do renderizador, que tem uma cópia deste mesmo documento — sincronize os dois ao editar.
- `slides-plan-spec.md` — o contrato `slides-plan` v1 (lado emissor): o formato que esta skill produz.

**Ao adicionar um tipo novo na tipologia:** crie a ficha em `fichas/` seguindo o gabarito, adicione a linha na tabela da família em `tipologia.md` com o link, e — do lado do renderizador — mapeie o tipo novo para uma classe em `tipo-layout-map.md` (no plugin `invisible-slides-plan-visual`).

## A fronteira com o renderizador

O contrato `slides-plan` v1 é a keystone entre os dois plugins. A mesma spec vive aqui (`references/slides-plan-spec.md`, lado emissor) e no `invisible-slides-plan-visual` (lado consumidor). **Ao mudar o formato do plano, atualize os dois lados e o número de versão do contrato** — senão o renderizador deixa de entender o que esta skill emite.

## Ingestão da fonte (portabilidade)

A Fase 0 lê a aula de forma **tool-agnóstica**: arquivo local (`Read`), texto colado, ou — para Google Drive/Notion/URL — qualquer ferramenta MCP disponível na sessão, com fallback para arquivo local / texto colado. **Nunca** referencie um ID de servidor MCP específico (ex.: `mcp__<hash>__...`) no SKILL.md ou nas references.

## Convenções

- **Nomes de arquivo:** kebab-case, sem espaços.
- **Idioma:** PT-BR.
- **Skill:** vive em `skills/<nome>/SKILL.md`, com prefixo `invisible-` no `name:` do frontmatter (convenção da Invisible — invocável como `/invisible-...`).
- **Output** vai para `class-slides/[nome-slug]/[nome-slug]_plano.md` no workspace do usuário — não versionado. O renderizador usa a mesma subpasta.

## Versionamento (semver)

A versão do plugin vive em `.claude-plugin/plugin.json` (campo `version`). Toda mudança que vai para a `main` e altera o comportamento do plugin precisa de bump — senão o marketplace não entrega nada novo a quem já instalou.

- **patch** (1.0.0 → 1.0.1): correção de bug, ajuste de texto, ponteiro quebrado, ficha enxuta aprofundada.
- **minor** (1.0.0 → 1.1.0): recurso novo compatível (tipo/ficha novo, passo novo no fluxo, extensão compatível do contrato).
- **major** (1.0.0 → 2.0.0): mudança incompatível (renomear/remover a skill, **quebra do contrato slides-plan** que exige o renderizador mudar junto).

Mudanças que **não** mexem no plugin entregue (só README/CLAUDE, organização interna) não exigem bump.

## Fluxo de trabalho (Git)

1. Edite os arquivos locais conforme o pedido.
2. Garanta a coerência das referências cruzadas (regra de ouro acima); rode `grep -rn` antes de concluir mudança estrutural. Se mexer no contrato, atualize também o plugin renderizador.
3. **Suba a versão em `.claude-plugin/plugin.json`** quando o comportamento do plugin mudar.
4. Commit com mensagem que descreve a intenção (`feat(...)`, `fix(...)`, `refactor:`, `docs:`, `chore:`).
5. Faça push apenas quando o usuário pedir.

## O que NÃO versionar

O `.gitignore` do repo ignora `.DS_Store` e `*.log`. As saídas da skill vão para `class-slides/[nome-slug]/` no workspace do usuário e não devem ser commitadas no plugin. Não versione transcrições/roteiros de aula do usuário a menos que ele peça.

## Roadmap (fora do v1)

- **Modo autoestudo** (slide se explica sozinho, sem narrador). Vários princípios de Mayer se invertem entre projeção e autoestudo. Documentado em `references/filosofia.md`.
- **Export PPTX e Canva** — sempre gerados do plano, nunca convertendo o HTML. São responsabilidade do renderizador (que recebe o mesmo plano). Recurso novo compatível → bump minor quando implementado.
- **Aprofundar as fichas enxutas** ao nível das completas, conforme o uso revelar necessidade.
