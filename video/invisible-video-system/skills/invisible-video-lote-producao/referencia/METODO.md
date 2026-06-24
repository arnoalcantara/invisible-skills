# Método — invisible-video-lote-producao

## O executor é um maestro (Forma A)

Decisão central: o executor **não reimplementa** as skills da esteira. Ele segue um
roteiro (este SKILL.md) que, em cada etapa, **invoca a skill filha** com os
parâmetros do plano. O conhecimento de *como* otimizar/legendar/combinar continua
dentro de cada skill; o executor só sabe a *ordem* e os *parâmetros*.

Há dois tipos de etapa:
- **Etapas-script** (otimizar, denoiser, transcrever, legendar, trilha, acelerar): o
  executor monta o comando `python3 .../scripts/...` e roda. Mecânico.
- **Etapas-julgamento** (var-gancho, combinador): exigem o Claude **vestir o chapéu**
  da skill — inferir a ênfase, julgar o encaixe retórico — antes/durante o script.
  Esse julgamento acontece na mesma conversa, e os portões internos (prova do gancho,
  MATRIZ.md) são respondidos pelo usuário ali.

Por que Forma A e não subagentes (Forma B): os portões de aprovação são o coração do
pedido ("sempre autorizadas pelo usuário"). Num subagente isolado, pausar pra
perguntar ao usuário é desajeitado. Na mesma conversa, o portão é natural.

## A fonte da verdade são as pastas

O `PLAN_LOTE.md` tem checkboxes, mas eles são **resumo legível**. O estado real vem
do disco: `estado_lote.py` conta o que existe em cada pasta de saída e deriva a
próxima etapa. Isso torna o executor robusto a parar no meio — ao retomar, ele lê o
disco, não confia no texto. As skills filhas já são resumíveis (pulam o que existe),
então re-rodar uma etapa parcial é seguro.

### Heurística de "etapa feita" (gates em estado_lote.py)
| Etapa | Feita quando |
|---|---|
| 1 Otimizar+Denoise | `02_OTIMIZADOS` tem `*_OTIMIZADO_*.mp4` |
| 2 Transcrever | nº de `.json` em `02_OTIMIZADOS` ≥ nº de bases de vídeo |
| 3.1 Legendar | `03_PREPARADOS` tem `*_LEGENDADO_*` |
| 3.2 Variações | `03_PREPARADOS` tem `*_VAR<n>_*` (só exigida se o plano pediu) |
| 4 Combinar | `04_COMBINADOS` tem combinação (nome com `__`) |
| 5 Acelerar | `04_COMBINADOS` tem `*_ACELERADO_*` (só exigida se o plano pediu) |
| 6 Trilha | `99_FINALIZADOS` tem `*_FINALIZADO*` |

Limitação consciente: o gate da etapa 1 não distingue "otimizado mas ainda não
denoised". O denoiser é in-place e mantém o nome (não há marca `_DENOISER` para
pular), então re-rodar a etapa 1 num lote já limpo **reaplica** o filtro sobre o
já-tratado — em fonte limpa o efeito da 2ª passada é pequeno, mas não é nulo. Por
isso o executor roda os dois passos da etapa 1 **uma vez** e não volta a ela depois
de marcada. Se um dia precisar de retomada fina no meio da etapa 1, dá pra checar um
marcador de denoise (sidecar), não o nome.

## A ordem e suas dependências

`1 → 2 → (3.1, 3.2 em qualquer ordem) → 4 → 5 → 6`.

- **Denoiser antes da transcrição:** transcrever áudio sujo desperdiça WhisperX e
  pode degradar o alinhamento. Por isso denoiser fecha a etapa 1, antes da 2.
- **3.1 e 3.2 independentes, ambas dependem da 2:** o `.json` por segmento alimenta
  tanto a legenda quanto a var-gancho (que usa o boundary/tempos do gancho).
- **4 depende das duas:** o combinador lê `03_PREPARADOS` esperando segmentos já
  legendados e variações já prontas.
- **Acelerar (5) ANTES da trilha (6):** se acelerasse depois, o `atempo` aceleraria
  a música junto e a tiraria do tempo. Acelerar roda em `04_COMBINADOS` (grava ao
  lado com `_ACELERADO_`, originais lentos intactos como subproduto); a trilha
  consome **só os `_ACELERADO_`** quando houve aceleração, e as combinações normais
  quando não houve.

## `.json` de combinação OFF por padrão

O combinador sabe gerar `.json` das peças combinadas, mas é desnecessário no fluxo
v2.6.0: os `.json` por segmento já existem (etapa 2) e os segmentos já estão
legendados (etapa 3.1). A combinação só concatena peças prontas — não re-legenda nem
precisa de `.json` próprio. O executor mantém isso desligado; só liga se o usuário
pedir explicitamente (caso raro).

## Onde o executor acha as skills filhas

As irmãs estão na mesma pasta `skills/` do executor. O `bootstrap.py` descobre esse
caminho a partir da localização do próprio script (sobe até `skills/`), sem cravar
versão de cache — assim o executor acha as irmãs na mesma versão dele, no repo ou no
cache de plugins (`~/.claude/plugins/cache/invisible-skills/invisible-video-system/<versão>/skills/`).

## Decisões travadas
- **Maestro, não monólito** (Forma A): invoca, não reimplementa.
- **Uma etapa por vez**, pausa B+C ao fim (resumo + marca checkbox + pede OK).
- **Respeita portões internos** das filhas — aprovação é sempre do usuário.
- **Pastas mandam** sobre checkboxes (retomável entre sessões).
- **Não roda `/invisible-upload` sozinho** — só sugere ao fim.
