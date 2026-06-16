# CLAUDE.md — Instruções do plugin `invisible-doc-to-presentation`

Este arquivo orienta qualquer instância de Claude (Claude Code, Cowork) que trabalhe neste plugin. Leia antes de editar.

## O que é este plugin

Skill da Invisible que transforma um documento em apresentação: produz um storyboard `.md` slide-a-slide e, após aprovação, uma apresentação HTML navegável. O visual vem de um **design system** (pasta `design-systems/`), desacoplado da skill. Veja o `README.md` para a visão completa.

## Princípios (não quebrar ao editar)

1. **Não inventar.** Nenhum dado, número ou afirmação que não esteja no documento fonte. Na dúvida, marcar `[confirmar]`.
2. **Storyboard antes do HTML.** O `.md` é gerado e aprovado antes de gerar o HTML. Nunca pular o portão de aprovação.
3. **O design system manda no visual.** A skill cuida da narrativa e da estrutura; a aparência (cores, tipografia, tipos de slide, template) vive no design system e deve ser seguida à risca.
4. **HTML auto-contido.** Tudo num único arquivo, sem dependências além do Google Fonts via CDN. Nunca entregar HTML quebrado.
5. **Skill fina, visual nos design systems.** A skill não embute CSS nem template; consome o design system escolhido.

## Design systems (extensível)

- Os design systems vivem em `design-systems/`, na raiz do plugin. A skill os referencia a partir de `../../design-systems/` (dois níveis acima de `skills/invisible-doc-to-presentation/`) e confirma o caminho com `ls ../../design-systems/` antes de ler. **Mantenha esse padrão** — ele é o mesmo do plugin `invisible-copy` e funciona quando o plugin está instalado em outra máquina. Não troque por caminho absoluto nem variável no corpo em prosa do SKILL.md.
- Adicionar um novo: criar um `.md` em `design-systems/` seguindo o formato do `invisible.md` (paleta, tipografia, fundamentos, tipos de slide, template HTML completo, instruções). A skill o descobre sozinha — não é preciso editar o SKILL.md.

## Ingestão de documentos (portabilidade)

A Fase 0 lê o documento de forma **tool-agnóstica**: arquivo local (`Read`), texto colado, ou — para Google Drive/Notion/URL — qualquer ferramenta MCP disponível na sessão, com fallback para arquivo local / texto colado. **Nunca** referenciar um ID de servidor MCP específico (ex.: `mcp__<hash>__...`) no SKILL.md: esses IDs são da instalação de quem criou e não existem em outra máquina.

## Convenções

- **Nomes de arquivo:** kebab-case, sem espaços.
- **Idioma:** PT-BR.
- **Skill:** vive em `skills/<nome>/SKILL.md`, com prefixo `invisible-` no `name:` do frontmatter (convenção da Invisible — invocável como `/invisible-...`).
- **Outputs** vão para `apresentacoes/[nome-slug]/` no workspace do usuário — não versionados, pertencem ao trabalho, não ao plugin.

## Versionamento (semver)

A versão do plugin vive em `.claude-plugin/plugin.json` (campo `version`). Toda mudança que vai para a `main` e altera o comportamento do plugin precisa de bump — senão o marketplace não entrega nada novo a quem já instalou. Regra:

- **patch** (1.0.0 → 1.0.1): correção de bug, ajuste de texto, ponteiro quebrado.
- **minor** (1.0.0 → 1.1.0): recurso novo compatível (design system novo, passo novo no fluxo).
- **major** (1.0.0 → 2.0.0): mudança incompatível (renomear/remover a skill, mudar fluxo de forma que quebra uso existente).

Mudanças que **não** mexem no plugin entregue (só README/CLAUDE, organização interna) não exigem bump.

## Fluxo de trabalho (Git)

1. Edite os arquivos locais conforme o pedido.
2. **Suba a versão em `.claude-plugin/plugin.json`** quando o comportamento do plugin mudar (ver Versionamento).
3. Commit com mensagem que descreve a intenção (`feat:`, `fix:`, `refactor:`, `docs:`, `chore:`).
4. Faça push apenas quando o usuário pedir.

## O que NÃO versionar

O `.gitignore` do repo ignora `.DS_Store` e `*.log`. As saídas da skill vão para `apresentacoes/[nome-slug]/` no workspace do usuário e não devem ser commitadas no plugin.
