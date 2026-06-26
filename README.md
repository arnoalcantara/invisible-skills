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
| `invisible-doc-to-presentation` | Transforma qualquer documento em apresentação: produz storyboard `.md` slide a slide e HTML navegável. Suporta múltiplos design systems; padrão é o da Invisible. |
| `invisible-class-slides-plan` | Metade didática da criação de slides de aula: transforma transcrição, roteiro ou esboço num **plano** de slides (contrato slides-plan v1) regido pela ciência da aprendizagem. Emite semântica didática, nunca HTML — o render é da `invisible-slides-plan-visual`. |
| `invisible-slides-plan-visual` | Renderizador genérico de slides: transforma um plano (contrato slides-plan v1) numa apresentação HTML auto-contida com builds, notas, fullscreen e escala responsiva. Consome o plano da `invisible-class-slides-plan` e storyboards da `invisible-doc-to-presentation`. |
| `invisible-video-system` | Esteira de vídeo da Invisible: onze skills numa linha de produção por pastas de etapa numeradas (01_Brutas → 02_OTIMIZADOS → 03_PREPARADOS → 04_COMBINADOS → 99_FINALIZADOS). O nome do arquivo orquestra o fluxo. Inclui desmembrador, otimizador, legendagem (gerador + aplicador karaokê), variação de gancho escrito, combinador (matriz cartesiana), trilha, denoiser, acelerador e o par planejador/maestro de lote. WhisperX e Remotion como dependências. |
| `invisible-organizacao` | Reorganiza pastas de empresa pelo sistema PARA (Tiago Forte) + forma numerada (Jeff Su): classifica cada item por acionabilidade, propõe plano de movimentação e aplica com reversibilidade (manifesto + reversor). |
| `invisible-radar` | Radar de referências: coleta material de fontes públicas e o prepara para copy. A skill `invisible-video-to-text` transforma um vídeo (link do Instagram, TikTok ou YouTube — ou arquivo local) num `material.md` unificado: transcreve a fala (WhisperX) e lê o texto na tela (caixinha, legenda, título) por visão, não OCR. Entrega só coleta organizada — não escreve copy. |

## Estrutura do repositório

```
.claude-plugin/marketplace.json   → catálogo de skills instaláveis
copy/                             → skills de copy (estrategista, copywriter, carrossel)
apresentacoes/                    → skills de slides/apresentações
video/                            → invisible-video-system (esteira de vídeo)
organizacao/                      → invisible-organizacao-system
radar/                            → radar de referências (coleta → material p/ copy)
  invisible-radar-system/         → invisible-video-to-text
```

Cada skill tem seu próprio `.claude-plugin/plugin.json`. Para publicar uma skill nova, adicione a pasta na categoria certa e registre a entrada no `marketplace.json`.
