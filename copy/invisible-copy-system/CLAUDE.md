# CLAUDE.md — Instruções do projeto `invisible-copy-system`

Este arquivo orienta qualquer instância de Claude (Claude Code, Cowork) que trabalhe neste repositório. Leia antes de editar.

## O que é este repositório

Sistema de agentes de copy da Invisible. Dois agentes — **Estrategista** (`estrategista/SKILL.md`) e **Copywriter** (`copywriter/SKILL.md`) — operam sobre uma base de conhecimento compartilhada (`base/`) para produzir a estratégia e a copy de uma campanha. O artefato intermediário entre os dois é o **Briefing de Campanha** (`briefing/template-briefing.md`). Veja o `README.md` para a visão completa.

## Princípios do sistema (não quebrar ao editar)

1. **A `base/` é a fonte única de verdade.** Todo conhecimento vive em `base/`. Os agentes (SKILL.md) são finos: orquestram e consomem os módulos, não duplicam conteúdo. **Nunca** copie um módulo da base para dentro da pasta de um agente.
2. **Agentes finos, conhecimento na base.** Se uma instrução é conhecimento reutilizável, ela vai num módulo da `base/`. Se é orquestração/fluxo, vai no SKILL.md.
3. **Verdade e dignidade como critério de corte.** Nada de promessa que o produto não cumpre, dor fabricada, mecanismo inventado, avatar caricato ou exploração de vulnerabilidade. Isso atravessa todos os módulos e não se negocia.
4. **Específico vence genérico.** Em todo módulo e toda recomendação.
5. **Canalizar desejo, não criar** (Schwartz). O desejo de massa já existe; o sistema o conecta ao produto.
6. **Só o essencial.** Os módulos são enxutos de propósito. Ao expandir, evite sprawl: acrescente só o que tem valor operacional.

## Regra de ouro: referências cruzadas

Os módulos se citam por **caminho** (ex.: `base/sofisticacao.md`, `base/copy/angulos.md`) e por **seção** (ex.: "Seção 6.1"). Ao editar:

- **Ao renomear ou mover um arquivo**, atualize TODOS os módulos, SKILL.md e o template que o referenciam. Um ponteiro quebrado degrada o sistema silenciosamente.
- **Ao renumerar ou remover uma seção** que outros arquivos citam, corrija as citações.
- **Antes de concluir uma mudança estrutural**, faça uma varredura: `grep -rn "nome-do-arquivo\|Seção X" .` e conserte o que apontar para o lugar errado.
- **Não numere os arquivos da `base/`** (ex.: `01-...`). A base é agnóstica de agente e cada agente a usa em ordem diferente; a ordem de uso vive nos SKILL.md, não no nome do arquivo.

## Convenções

- **Nomes de arquivo:** kebab-case, sem espaços (caminhos sem espaço são seguros para CLI/skills). Títulos dentro dos arquivos podem ter espaço e maiúscula.
- **Idioma:** PT-BR.
- **Estilo dos módulos:** propósito + lugar na cadeia + escopo no topo; "Como a IA deve usar"; conteúdo operacional; cruzamento com os módulos; notas Brasil; checklist final.
- **Formatos de canal** ficam em `base/formatos/`; **craft de copy** (estruturas, macroestrutura, ângulos) em `base/copy/`; **conhecimento de público/oferta/ideia** na raiz de `base/`.

## Fluxo de trabalho (Git)

1. Edite os arquivos locais conforme o pedido.
2. Garanta a coerência das referências cruzadas (regra de ouro acima).
3. Commit com mensagem que descreve a intenção, no padrão:
   - `feat(base): ...` novo conhecimento ou módulo
   - `fix(base): ...` correção (inclui ponteiro quebrado)
   - `refactor: ...` reorganização sem mudar conteúdo
   - `docs: ...` README/CLAUDE/comentários
   - `chore: ...` estrutura, empacotamento
   Exemplo: `feat(base): adiciona ângulo de prova futura em angulos.md`
4. Faça push apenas quando o usuário pedir. Prefira commits pequenos e temáticos a um commit gigante.

## O que NÃO versionar

O `.gitignore` ignora insumos e saídas de campanha. As saídas dos agentes vão todas para a pasta única `campanhas/` (uma subpasta por campanha, com briefing + peças juntos), criada no workspace do usuário e **não versionada**. Também ignorados: `BRIEFING_*.md`, `*-arquivo-de-voz.md`, `*-arquivo-base.md`. Estes pertencem às campanhas, não ao sistema. Não os adicione ao repo a menos que o usuário peça explicitamente.

## Ao adicionar um módulo novo

1. Crie o `.md` no diretório certo (`base/`, `base/copy/` ou `base/formatos/`).
2. Siga o estilo dos módulos existentes.
3. Adicione as referências cruzadas necessárias **nos dois sentidos** (o novo módulo cita os relevantes; os relevantes passam a citá-lo onde fizer sentido).
4. Se um agente deve consumi-lo, adicione-o à lista de insumos do SKILL.md correspondente e ao ponto certo do fluxo.
5. Se entra no Briefing, acrescente a seção no `briefing/template-briefing.md`.
