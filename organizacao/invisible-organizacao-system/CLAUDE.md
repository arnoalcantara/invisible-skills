# CLAUDE.md — Instruções do projeto `invisible-organizacao-system`

Este arquivo orienta qualquer instância de Claude que edite este plugin. Leia antes de mexer.

## O que é este repositório

Sistema de organização de pastas de empresa pelo método **PARA** (Tiago Forte) + **forma numerada** (Jeff Su). Uma skill — `invisible-organizacao-pastas` (`skills/invisible-organizacao-pastas/SKILL.md`) — consome o algoritmo central (`base/algoritmo-para.md`) para reorganizar a pasta de uma empresa: classifica itens soltos por acionabilidade, propõe um plano e aplica com reversibilidade. Veja o `README.md` para a visão completa.

## Princípios do sistema (não quebrar ao editar)

1. **A `base/` é a fonte única.** O algoritmo PARA vive em `base/algoritmo-para.md`. A skill é fina: orquestra o fluxo e consome a base. Nunca duplique o algoritmo dentro do SKILL.md.
2. **Propor antes de mover é inviolável.** A skill mapeia e classifica em modo read-only; só move depois do ok explícito. Qualquer edição que enfraqueça isso quebra o contrato com o usuário.
3. **Nunca apagar.** A skill só move e cria pastas. Não introduza remoção de arquivos.
4. **Reversibilidade.** Toda aplicação grava manifesto TSV + reversor `.sh`. Mantenha esse mecanismo em qualquer mudança no fluxo de aplicação.
5. **Acionabilidade, não tema.** A regra-mãe do PARA. Toda recomendação da skill deriva dela.

## Relação com o documento canônico

`base/algoritmo-para.md` é a versão empacotada (viaja com o plugin) do documento canônico do workspace do Arno: `00_Resources/PROTOCOLO Organização de Pastas Empresa Sistema PARA.md`. Os dois devem dizer a mesma coisa. **Ao mudar o algoritmo, atualize ambos** — o canônico governa o workspace, a cópia governa o plugin instalado.

## Convenções

- **Idioma:** PT-BR.
- **Nomes de arquivo:** kebab-case, sem espaços (caminhos seguros para CLI).
- **Prefixo `invisible-`:** convenção da Invisible para o `name:` das skills. A skill é `invisible-organizacao-pastas`; o plugin instalável é `invisible-organizacao`.
- **Caminhos na skill:** a skill vive em `skills/invisible-organizacao-pastas/` e referencia a base a partir de `../../base/`. `${CLAUDE_PLUGIN_ROOT}` não expande no corpo do SKILL.md, por isso a skill confirma o caminho com `ls ../../base` antes de ler.

## Versionamento (semver)

A versão vive em `.claude-plugin/plugin.json`. Toda mudança que vai para a `main` e altera o comportamento precisa de bump — senão quem instalou não recebe a atualização.

- **patch** (1.0.0 → 1.0.1): correção de texto, ajuste de ponteiro.
- **minor** (1.0.0 → 1.1.0): recurso novo compatível (novo passo no fluxo, nova área-padrão).
- **major** (1.0.0 → 2.0.0): mudança incompatível (renomear a skill, mudar o contrato do fluxo).

## Fluxo de trabalho (Git)

1. Edite os arquivos locais.
2. Se mexeu no algoritmo, sincronize `base/algoritmo-para.md` com o doc canônico do workspace.
3. **Suba a versão em `plugin.json`** quando o comportamento mudar.
4. Atualize a entrada deste plugin no `marketplace.json` da raiz se o nome/descrição/source mudarem.
5. Commit com mensagem que descreve a intenção (`feat:`, `fix:`, `docs:`, `chore:`). Push só quando o Arno pedir.
