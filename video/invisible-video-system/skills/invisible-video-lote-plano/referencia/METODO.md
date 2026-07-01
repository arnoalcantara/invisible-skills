# Método — invisible-video-lote-plano

## Por que duas skills (plano + produção)

Planejar e executar são ritmos diferentes. Planejar é uma conversa curta que
acontece **uma vez** no início do lote. Executar é um processo longo, em etapas,
que o usuário roda **várias vezes** ao longo de dias (fecha o laptop, volta, retoma).

Numa skill única, retomar a produção exigiria re-perguntar o plano ou adivinhar se
o usuário está planejando ou executando. Separadas, cada uma tem gatilho limpo, e o
`PLAN_LOTE.md` é a memória entre elas — o planejador escreve, o executor lê.

## O contrato: PLAN_LOTE.md

Mora na raiz do lote. Tem duas partes que o executor consome:

1. **Decisões do lote** — os parâmetros que cada etapa vai usar (estilo de legenda,
   quais VARs e com qual fonte/fundo, pasta de trilha, alvos de loudness, fator de
   aceleração, modo de otimização).
2. **Checkboxes das etapas** — um por etapa da esteira (1, 2, 3.1, 3.2, 4, 5, 6, 7).
   As etapas condicionais (3.2 sem VAR, 5 sem aceleração, 7 sem prefixo de nome) já
   nascem marcadas como puladas.

**Regra de ouro:** o checkbox é o resumo legível pra humano; **a fonte da verdade do
progresso são as pastas**. O executor reconcilia com o disco antes de cada etapa e
pula o que já está pronto. Texto e realidade nunca brigam — a realidade ganha.

## O que o planejador decide e o que ele NÃO decide

**Decide** (preferências, não dependem de ver o material):
- estilo de legenda; quais variações de gancho (+ fonte/fundo); pasta de trilha e
  níveis; acelerar e qual fator; modo de otimização (silêncio/respiro, ambos justo
  por default); nomeação final (prefixo + número inicial + ordem).

**NÃO decide:**
- A **matriz de combinações** (gancho VAV19 × desenvolvimento VAV57...). Isso é do
  combinador, na execução, quando os segmentos já existem em `02_OTIMIZADOS` e dá
  pra julgar o encaixe retórico. Decidir a matriz aqui duplicaria o combinador e não
  faria sentido com a pasta vazia.

## Ordem híbrida (pasta vazia)

O planejador cria a estrutura **vazia** e manda o usuário jogar as brutas depois.
Nenhuma decisão do planejador precisa do material — são escolhas de estilo do lote,
que o usuário já tem na cabeça quando decide produzir. O único momento que depende do
material (a matriz) está lá na frente, no combinador.

## A sequência da esteira (que o PLAN_LOTE.md instancia)

| Etapa | Skill(s) | Entrada → Saída | Portão |
|---|---|---|---|
| 1. Otimizar + Denoise | otimizador → denoiser | 01_BRUTAS → 02_OTIMIZADOS (denoiser sobrescreve) | folha-contato quadrado |
| 2. Transcrever | legenda-arquivos | 02_OTIMIZADOS → .json por segmento | — |
| 3.1 Legendar | legendas-aplicador | 02_OTIMIZADOS → 03_PREPARADOS | still (opcional) |
| 3.2 Variações de gancho | var-gancho-escrito --alvo segmento | 02_OTIMIZADOS → 03_PREPARADOS | prova do 1º (obrigatório) |
| 4. Combinar | combinador | 03_PREPARADOS → 04_COMBINADOS | MATRIZ.md (obrigatório) |
| 5. Acelerar | acelerador | 04_COMBINADOS → 04_COMBINADOS | — |
| 6. Trilha | trilha-aplicador | 04_COMBINADOS → 99_FINALIZADOS | amostra (recomendado) |
| 7. Nomear | lote-producao (nomear.py) | 99_FINALIZADOS → 99_FINALIZADOS (in-place) | — |

Dependências: `2 → (3.1, 3.2) → 4 → 5 → 6 → 7`. O denoiser roda **antes** da
transcrição (não transcrever áudio sujo). **Acelerar (5) vem ANTES da trilha (6)**:
acelerar depois aceleraria a música junto (o `atempo` a tiraria do tempo) — então
acelera-se a combinação e a trilha entra por cima do ritmo final, consumindo só os
`_ACELERADO_`. O `.json` de combinação fica **OFF** por padrão (os `.json` por
segmento já existem; o combinador só concatena).

## Decisões travadas

- **Processo embutido na skill, não lido de arquivo.** O `LINHA-DE-PRODUCAO.md` é
  referência humana (raiz do laboratório). Se a skill o lesse em runtime, quebraria a
  portabilidade do plugin. Custo: ao mudar a esteira, atualizar dois lugares (o
  documento e esta skill). É barato — a esteira muda raramente.
- **Decisões via JSON, não dezenas de flags.** `criar_lote.py --decisoes`.
- **Idempotente.** Recusa sobrescrever lote existente sem `--forcar`.
