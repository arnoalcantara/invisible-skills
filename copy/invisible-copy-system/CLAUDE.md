# CLAUDE.md — Instruções do projeto `invisible-copy-system`

Este arquivo orienta qualquer instância de Claude (Claude Code, Cowork) que trabalhe neste repositório. Leia antes de editar.

## O que é este repositório

Sistema de agentes de copy da Invisible. Três agentes — **Estrategista** (`invisible-estrategista-copy/SKILL.md`), **Copywriter** (`invisible-copywriter/SKILL.md`) e **Carrossel** (`invisible-carrossel/SKILL.md`) — operam sobre uma base de conhecimento compartilhada (`base/`). Estrategista e Copywriter produzem a estratégia e a copy de uma campanha, com o **Briefing de Campanha** (`briefing/template-briefing.md`) como artefato intermediário. Carrossel transforma material escrito bruto (transcrição, print, insight) em carrosséis posicionados, em três modos (autoridade prática, mudança de percepção, editorial) lendo os métodos em `base/formatos/carrossel-[modo].md`. Veja o `README.md` para a visão completa.

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
- **Biblioteca de modelos** fica em `base/copy/modelos/` (esqueletos de persuasão de campanhas reais, um arquivo por produtor: `modelos-de-copy-[produtor].md`), com um `indice-modelos.md` que cataloga o que existe. **Esta camada é reproduzida com fidelidade máxima e não passa pelo corte de verdade/dignidade** — o usuário decide o que mantém na geração.
- **Perfis de produto** ficam em `base/produtos/` (um arquivo por produto recorrente, kebab-case descritivo: `desafio-memorize-escrita.md`), com um `indice-produtos.md` que cataloga o que existe. Um **perfil substitui o par Briefing + Arquivo de Voz**: reúne avatar, dores, mecanismo, promessa, objeções E a voz da marca num só arquivo, mais os padrões de criativo validados daquele produto. **Esta camada passa normalmente pelo corte de verdade/dignidade** (é conhecimento real do produto, não movimento de terceiro). O copywriter a oferece na Fase 0; o estrategista não a consome (perfil é alternativa ao briefing, não insumo dele).
- **Figuras de retórica** ficam em `base/copy/figuras-de-retorica.md` — craft de superfície agnóstico de produto (tricolon, anáfora, quiasmo etc.), consumido pelo copywriter na produção.

## Rotina: indexar modelo novo

Quando o Arno disser "coloquei um modelo novo" (ou pedir para indexar): leia o arquivo novo em `base/copy/modelos/`, extraia produtor + lista de modelos com "quando usar", acrescente a seção no Catálogo de `indice-modelos.md` (sem reescrever as existentes), confira a convenção de nome `modelos-de-copy-[produtor].md`, suba a versão (bump minor) e commite. O passo a passo completo está na seção "Manutenção do índice" do próprio `indice-modelos.md`.

## Rotina: indexar perfil de produto novo

Quando o Arno disser "criei um perfil de produto novo" (ou pedir para indexar): leia o arquivo novo em `base/produtos/`, extraia o nome do produto + a linha de "quando usar", acrescente a seção no Catálogo de `indice-produtos.md` (sem reescrever as existentes), confira a convenção de nome (kebab-case descritivo do produto), suba a versão (bump minor) e commite. O passo a passo completo está na seção "Manutenção do índice" do próprio `indice-produtos.md`.

## Fluxo de trabalho (Git)

1. Edite os arquivos locais conforme o pedido.
2. Garanta a coerência das referências cruzadas (regra de ouro acima).
3. **Suba a versão em `.claude-plugin/plugin.json`** (ver "Versionamento" abaixo). O marketplace só entrega a atualização a quem já instalou se o número de versão mudar — esquecer o bump deixa o time preso na versão antiga.
4. Commit com mensagem que descreve a intenção, no padrão:
   - `feat(base): ...` novo conhecimento ou módulo
   - `fix(base): ...` correção (inclui ponteiro quebrado)
   - `refactor: ...` reorganização sem mudar conteúdo
   - `docs: ...` README/CLAUDE/comentários
   - `chore: ...` estrutura, empacotamento (inclui bump de versão)
   Exemplo: `feat(base): adiciona ângulo de prova futura em angulos.md`
5. Faça push apenas quando o usuário pedir. Prefira commits pequenos e temáticos a um commit gigante.

## Versionamento (semver)

A versão do plugin vive em `.claude-plugin/plugin.json` (campo `version`). Toda mudança que vai para a `main` e altera o comportamento do plugin precisa de bump — senão os instaladores não recebem nada novo. Regra:

- **patch** (1.1.0 → 1.1.1): correção de bug, ajuste de texto, ponteiro quebrado.
- **minor** (1.1.0 → 1.2.0): recurso novo compatível (módulo novo, formato novo, passo novo no fluxo).
- **major** (1.1.0 → 2.0.0): mudança incompatível (renomear/remover skill, mudar fluxo de forma que quebra uso existente).

Mudanças que **não** mexem no plugin entregue (ex.: só README/CLAUDE, organização interna) não exigem bump.

## O que NÃO versionar

O `.gitignore` ignora insumos e saídas de campanha. As saídas dos agentes vão todas para a pasta única `campanhas/` (uma subpasta por campanha, com briefing + peças juntos), criada no workspace do usuário e **não versionada**. Também ignorados: `BRIEFING_*.md`, `*-arquivo-de-voz.md`, `*-arquivo-base.md`. Estes pertencem às campanhas, não ao sistema. Não os adicione ao repo a menos que o usuário peça explicitamente.

## Ao adicionar um módulo novo

1. Crie o `.md` no diretório certo (`base/`, `base/copy/` ou `base/formatos/`).
2. Siga o estilo dos módulos existentes.
3. Adicione as referências cruzadas necessárias **nos dois sentidos** (o novo módulo cita os relevantes; os relevantes passam a citá-lo onde fizer sentido).
4. Se um agente deve consumi-lo, adicione-o à lista de insumos do SKILL.md correspondente e ao ponto certo do fluxo.
5. Se entra no Briefing, acrescente a seção no `briefing/template-briefing.md`.
