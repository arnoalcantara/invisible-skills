# CLAUDE.md — Instruções do plugin `invisible-class-slides`

Este arquivo orienta qualquer instância de Claude (Claude Code, Cowork) que trabalhe neste plugin. Leia antes de editar.

## O que é este plugin

Skill da Invisible que transforma transcrição/roteiro/esboço de aula em apresentação **didática para projeção ao vivo**, regida pela ciência da aprendizagem. Entrega um **plano** (storyboard) slide-a-slide e, após aprovação, um **HTML** auto-contido. A skill é **fina** (orquestra); o conhecimento vive em `skills/invisible-class-slides/references/` e o visual nos `design-systems/`. Veja o `README.md` para a visão completa.

## Princípios (não quebrar ao editar)

1. **Skill fina, conhecimento nas references.** O SKILL.md orquestra (dials, 2 passadas, 2 outputs) e **aponta** para as references no momento certo. Nunca inline o conteúdo das references no SKILL.md. Mantenha o SKILL.md < 500 linhas.
2. **As 13 leis são a constituição.** Toda geração obedece ao princípio-mestre (memória de trabalho minúscula) e às 13 leis de `references/filosofia.md`. Não as enfraqueça.
3. **Duas passadas, com portão.** Passada 1 (arquitetura) gera o plano; o usuário **aprova**; só então a Passada 2 (instanciação) renderiza. Nunca pule o portão.
4. **Fidelidade à substância, liberdade na forma.** A skill reorganiza o linear da aula no arco e na tipologia, mas não inventa, não distorce, não "melhora" o argumento do professor. Material adicionado entra marcado (proveniência). Vale dobrado para conteúdo de formação/doutrinário.
5. **Não inventar dado.** Gráfico com número real é renderizado de verdade (SVG/código), **nunca** "desenhado" por modelo de imagem.
6. **Composição compartilhada, skin por brand.** A *estrutura* visual (layouts, densidade, hierarquia, grid, primitivos, player) vive na base de composição `design-systems/_base.md`, escrita só com variáveis e herdada por todos os brands. Cada brand (`invisible.md` e futuros) é só o *skin*: tokens (cor, fonte, radius) e tratamento. O *ofício* de compor cada slide — preencher o quadro, foco, densidade — vive em `references/composicao-visual.md`. A skill cuida da didática; o visual é base + skin, seguidos à risca.
7. **HTML auto-contido.** Um único arquivo, sem dependências além de Google Fonts via CDN. Nunca entregar HTML quebrado.

## References (a base de conhecimento)

Vivem em `skills/invisible-class-slides/references/`. Citam-se por caminho relativo e devem ser mantidas coerentes nos dois sentidos (regra de ouro: ao renomear/mover, atualize quem aponta). São:

- `filosofia.md` — princípio-mestre + 13 leis + foco (projeção ao vivo; autoestudo = roadmap).
- `arco-da-aula.md` — arco canônico, consciência posicional, processo de 2 passadas.
- `tipologia.md` — 8 famílias, ~47 tipos, TOC com link para cada ficha em `fichas/`.
- `fichas/` — uma ficha executável por tipo (gabarito fixo). ~15 completas + as demais enxutas.
- `producao-visual.md` — roteamento de imagem, 4 modos, detecção de gerador em runtime.
- `composicao-visual.md` — o ofício de compor o slide (preencher o quadro, foco, densidade, peso, grid) + checklist de direção de arte da Passada 2.
- `proveniencia.md` — contrato de fidelidade e mapa de proveniência.
- `outputs.md` — plano → aprovação → HTML; PPTX/Canva = roadmap.

**Ao adicionar um tipo novo na tipologia:** crie a ficha em `fichas/` seguindo o gabarito, adicione a linha na tabela da família em `tipologia.md` com o link, defina a classe (layout) em `design-systems/_base.md` e adicione a linha na tabela tipo→classe do skin.

## Design systems: base + skin (extensível)

- Vivem em `design-systems/`, na raiz do plugin. A skill os referencia a partir de `../../design-systems/` (dois níveis acima de `skills/invisible-class-slides/`) e confirma o caminho com `ls ../../design-systems/` antes de ler. **Mantenha esse padrão** — é o mesmo dos plugins `invisible-copy` e `invisible-doc-to-presentation` e funciona quando o plugin está instalado em outra máquina. Não troque por caminho absoluto nem variável no corpo em prosa do SKILL.md.
- **Base de composição (`_base.md`).** Partial compartilhado (prefixo `_` = não é brand selecionável; a Fase 0 o ignora ao listar). Contém o esqueleto HTML, o CSS estrutural de todos os layouts, os primitivos de composição e o player — tudo escrito **só com variáveis** (`var(--…)`), sem nenhuma cor ou fonte literal. É a inteligência de composição: editar aqui melhora **todos** os brands de uma vez.
- **Skin de brand (`invisible.md` e futuros).** Só os tokens (`:root`: paleta, fontes, radius), o font link, o wordmark e a tabela tipo→classe. **Nenhum CSS estrutural.**
- **Adicionar um brand novo:** copiar o bloco de tokens de `invisible.md`, re-tematizar (outra paleta/fonte), ajustar a tabela tipo→classe se quiser. A composição vem de graça da base. Não precisa editar o SKILL.md — a skill descobre o brand sozinha. Padrão = `invisible`.
- **Render = base + skin:** a skill lê os dois e monta um HTML auto-contido (base inlinada + `:root` do skin). O contrato de tokens que todo skin precisa definir está no cabeçalho de `_base.md`.

## Geração de imagem (portabilidade)

Os Modos visuais 2 e 3 dependem de uma ferramenta MCP de geração de imagem. A skill **descobre em runtime** se existe na sessão; se houver, usa; se não, avisa e cai para Modo 0/1. **Nunca** referencie um ID/nome de servidor MCP específico (ex.: `mcp__<hash>__...` ou um nome de produto) no SKILL.md ou nas references: esses IDs são da instalação de quem criou e não existem em outra máquina. Stock free e desenho em código sempre funcionam. A ingestão da fonte (Drive/Notion/URL) segue a mesma regra: qualquer MCP disponível, com fallback para arquivo local / texto colado.

## Convenções

- **Nomes de arquivo:** kebab-case, sem espaços.
- **Idioma:** PT-BR.
- **Skill:** vive em `skills/<nome>/SKILL.md`, com prefixo `invisible-` no `name:` do frontmatter (convenção da Invisible — invocável como `/invisible-...`).
- **Outputs** vão para `class-slides/[nome-slug]/` no workspace do usuário — não versionados.

## Versionamento (semver)

A versão do plugin vive em `.claude-plugin/plugin.json` (campo `version`). Toda mudança que vai para a `main` e altera o comportamento do plugin precisa de bump — senão o marketplace não entrega nada novo a quem já instalou.

- **patch** (1.0.0 → 1.0.1): correção de bug, ajuste de texto, ponteiro quebrado, ficha enxuta aprofundada.
- **minor** (1.0.0 → 1.1.0): recurso novo compatível (design system novo, tipo/ficha novo, export PPTX/Canva, passo novo no fluxo).
- **major** (1.0.0 → 2.0.0): mudança incompatível (renomear/remover a skill, mudar o fluxo de forma que quebra uso existente).

Mudanças que **não** mexem no plugin entregue (só README/CLAUDE, organização interna) não exigem bump.

## Fluxo de trabalho (Git)

1. Edite os arquivos locais conforme o pedido.
2. Garanta a coerência das referências cruzadas (regra de ouro acima); rode `grep -rn` antes de concluir mudança estrutural.
3. **Suba a versão em `.claude-plugin/plugin.json`** quando o comportamento do plugin mudar.
4. Commit com mensagem que descreve a intenção (`feat(...)`, `fix(...)`, `refactor:`, `docs:`, `chore:`).
5. Faça push apenas quando o usuário pedir.

## O que NÃO versionar

O `.gitignore` do repo ignora `.DS_Store` e `*.log`. As saídas da skill vão para `class-slides/[nome-slug]/` no workspace do usuário e não devem ser commitadas no plugin. Não versione transcrições/roteiros de aula do usuário a menos que ele peça.

## Roadmap (fora do v1)

- **Modo autoestudo** (slide se explica sozinho, sem narrador). Vários princípios de Mayer se invertem entre projeção e autoestudo — exige separar camada de projeção de camada de notas. Documentado em `references/filosofia.md`.
- **Export PPTX e Canva** — sempre gerados do plano, nunca convertendo o HTML. Recurso novo compatível → bump minor quando implementado.
- **Aprofundar as fichas enxutas** ao nível das completas, conforme o uso revelar necessidade.
