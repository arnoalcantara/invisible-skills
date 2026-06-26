# Invisible Skills

Repositório de skills compartilhadas da equipe Invisible para o Claude Code.

Cada skill é instalável individualmente — você não precisa baixar o repositório inteiro. O repo funciona como um *marketplace* de plugins do Claude Code: você adiciona o catálogo uma vez e instala só o que quiser.

## Como instalar

Dentro do Claude Code, rode:

```
/plugin marketplace add arnoalcantara/invisible-skills
/plugin install invisible-copy@invisible-skills
```

A primeira linha registra o catálogo (não instala nada). A segunda instala **apenas** a skill escolhida.

## Como atualizar

Quando uma skill receber melhorias e o push for feito aqui, cada pessoa atualiza com:

```
/plugin update invisible-copy@invisible-skills
```

Não precisa reinstalar do zero nem baixar arquivo manualmente.

## Skills disponíveis

| Skill | O que faz |
|-------|-----------|
| `invisible-copy` | Sistema de três agentes de copy: **Estrategista** (gera o Briefing de Campanha a partir do Arquivo Base), **Copywriter** (transforma Briefing + Arquivo de Voz em peças de copy em qualquer formato) e **Carrossel** (transforma material escrito bruto — transcrição, print, insight — em carrosséis posicionados, em três modos: autoridade prática, mudança de percepção e editorial, mais um modo de mapa de pauta). |

## Estrutura do repositório

```
.claude-plugin/marketplace.json   → catálogo de skills instaláveis
copy/                             → skills da categoria copy
  invisible-copy-system/          → skill invisible-copy
```

Cada skill tem seu próprio `.claude-plugin/plugin.json`. Para publicar uma skill nova, adicione a pasta na categoria certa e registre a entrada no `marketplace.json`.
