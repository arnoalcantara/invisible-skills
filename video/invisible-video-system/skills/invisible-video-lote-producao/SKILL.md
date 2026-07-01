---
name: invisible-video-lote-producao
description: >
  Executa a produção de um lote de vídeo lendo o PLAN_LOTE.md que a invisible-video-lote-plano criou. É um MAESTRO: não reimplementa nenhuma etapa — invoca as skills da esteira v2.6.0 (otimizador, denoiser, legenda-arquivos, legendas-aplicador, var-gancho-escrito, combinador, acelerador, trilha-aplicador) na ordem certa, com os parâmetros que o plano definiu. Quando há aceleração, ela vem ANTES da trilha (senão a música aceleraria junto e sairia fora de tempo). Roda UMA etapa por vez e DEVOLVE o controle ao usuário ao fim de cada, sempre pedindo autorização antes da próxima. As pastas do lote são a fonte da verdade do progresso: ao retomar, lê o PLAN_LOTE.md e reconcilia com o disco para saber onde parou — é totalmente retomável entre sessões. Respeita os portões internos de cada skill filha (a prova do primeiro gancho na var-gancho, a aprovação da MATRIZ.md no combinador). Por padrão NÃO gera .json de combinação (os .json por segmento já existem). Use quando o usuário pedir "produzir o lote", "executar o lote", "rodar a esteira", "continuar a produção do lote X", "tocar o lote do bruto ao finalizado", "retomar o lote". Requer as skills da esteira instaladas e ffmpeg (faz bootstrap).
---

# Maestro de Produção de Lote

Você executa um lote seguindo o `PLAN_LOTE.md` que a `invisible-video-lote-plano`
gravou na raiz do lote. Você é um **maestro**, não um executor de baixo nível:
**não reimplementa** otimização, legenda, combinação, trilha. Você **invoca a skill
de cada etapa** com os parâmetros do plano, na ordem certa, pausando a cada etapa.

> **Regra mãe:** uma etapa por vez. Ao fim de CADA etapa, você devolve o controle ao
> usuário com um resumo e pede autorização antes de seguir. Nunca encadeie duas
> etapas sem o OK dele. (Exceção: dentro da etapa 1, otimizador→denoiser são dois
> passos de uma etapa só.)

## Como você sabe onde parou (retomável)

As **pastas são a fonte da verdade**, não os checkboxes. Sempre comece rodando:

```bash
python3 scripts/bootstrap.py --check-only
python3 scripts/estado_lote.py "<dir do lote>"
```

O `estado_lote.py` lê o `PLAN_LOTE.md` (as decisões) e **reconcilia com o disco**
(o que já está em cada pasta), devolvendo `proxima_etapa` e as `decisoes`. Você
executa **a próxima etapa não-feita** — nada antes. Se o usuário não disser qual
lote, procure os `Lote NN - .../PLAN_LOTE.md` na raiz do laboratório e confirme.

## Portão de entrada — nomes das brutas (antes da etapa 1)

**Só quando a `proxima_etapa` for a `1`** (o lote está começando; não faça isso ao
retomar no meio), olhe os nomes em `01_BRUTAS` **antes** de otimizar. As brutas
seguem o padrão `SECAO_N[_Vn]_BRUTA.mp4`, tudo MAIÚSCULO, com underscore separando
seção, número e take (ex.: `GANCHO_1_BRUTA`, `GANCHO_2_V3_BRUTA`,
`DESENVOLVIMENTO_1_BRUTA`). O otimizador e as etapas seguintes leem a seção pelo
nome — bruta torta contamina o lote inteiro.

**Dispara só se houver bruta fora do padrão.** Se todas já batem o padrão, **não
incomode** — siga direto pra etapa 1.

Quando houver nomes tortos:
1. **Infira o padrão dos próprios arquivos do lote** que já estão corretos (o lote
   dita o padrão; não há padrão canônico do sistema). Se nenhum estiver claro, ou a
   leitura for ambígua, **pergunte** ao usuário qual é o padrão / o que cada arquivo
   é. A leitura ambígua é dele — ex.: `Gancho2` (sem `_v`) é o take base do gancho 2?
   `gancho_1_v2` é a segunda take do gancho 1? Não adivinhe: confirme.
2. **Monte o mapa de→para** e mostre a tabela completa (`atual → novo`).
3. **Sempre peça OK** — mesmo no trivial (só caixa/espaço). **Nunca renomeie às
   cegas.** Aprovado, renomeie com `mv` (é `git`-free, trabalho trivial; não há
   script — o julgamento é o trabalho, o renomear é um `mv`).
4. Só então prossiga para a etapa 1.

> Isto **não é uma etapa numerada** (não entra no `estado_lote.py` nem tem checkbox):
> é um portão de higiene na entrada. Se o usuário jogar uma bruta nova torta no meio
> do lote, normalize-a do mesmo jeito antes da próxima etapa que a consumir.

## O fluxo em cada etapa (pausa B+C)

Para a `proxima_etapa`:
1. **Anuncie** o que vai fazer (qual skill, com quais parâmetros do plano).
2. **Execute** seguindo o método da skill filha (ver tabela abaixo). Onde a filha tem
   portão interno, **respeite-o** — a aprovação é do usuário, ali na conversa.
3. **Resuma** o que saiu (quantos arquivos, nomes-chave, qualquer aviso).
4. **Marque** o checkbox: `python3 scripts/marcar_etapa.py "<lote>" <etapa>`.
5. **Pare** e pergunte: "Etapa X concluída. Autoriza a etapa Y?". Espere o OK.

A inspeção visual acontece onde a filha já a oferece (folha-contato do quadrado,
prova do gancho, MATRIZ.md) — não invente inspeção onde não há o que ver (um `.json`
não tem o que olhar).

## A esteira — qual skill, com quais parâmetros

As skills-irmãs estão na mesma pasta `skills/` deste executor (o `bootstrap.py`
reporta o caminho em `skills_dir`). Monte os comandos a partir de
`<skills_dir>/<nome-da-skill>/scripts/...`. Os parâmetros vêm das `decisoes` do
`estado_lote.py`.

### Etapa 1 — Otimizar + Denoise `[01_BRUTAS → 02_OTIMIZADOS]`
Dois passos, uma etapa. Primeiro o otimizador, depois o denoiser por cima.
```bash
python3 "<skills_dir>/invisible-video-otimizador/scripts/otimizar.py" "<lote>/01_BRUTAS" \
  --modo-silencio <modo_silencio> --modo-respiro <modo_respiro>
python3 "<skills_dir>/invisible-denoiser/scripts/denoiser.py" "<lote>/02_OTIMIZADOS"
```
- O otimizador gera vertical + quadrado + `.md` em `02_OTIMIZADOS` (portão: folha de
  contato do quadrado, se houver dúvida de enquadramento — siga o SKILL.md dele).
- O denoiser **sobrescreve in-place mantendo o mesmo nome** (`-c:v copy`) — roda
  **depois** do otimizador e **antes** da transcrição, pra não transcrever áudio sujo.
  Como não muda o nome, os `_OTIMIZADO_VERTICAL`/`_QUADRADO` ficam intactos e a
  transcrição (etapa 2) acha o `.json` por base normalmente. Ele recusa rodar em
  `BRUTAS`; aqui roda em `02_OTIMIZADOS`, então segue normal. Sem marca no nome, o
  executor não deve re-rodar o denoiser na mesma pasta (reaplicaria o filtro).

### Etapa 2 — Transcrever `[02_OTIMIZADOS → .json]`
```bash
python3 "<skills_dir>/invisible-legenda-arquivos/scripts/bootstrap.py"   # pega o whisperx-bin
python3 "<skills_dir>/invisible-legenda-arquivos/scripts/legendar.py" "<lote>/02_OTIMIZADOS" \
  --whisperx-bin "<bin do bootstrap>"
```
Um `.json` por **segmento** (dedup por base). Sem portão.

### Etapa 3.1 — Legendar `[02_OTIMIZADOS → 03_PREPARADOS]`
```bash
python3 "<skills_dir>/invisible-legendas-aplicador/scripts/aplicar.py" "<lote>/02_OTIMIZADOS" \
  [--estilo <estilo se não for "auto">]
```
- Default `auto`: a skill escolhe por formato (vertical→`reels`, quadrado→`classic`).
  Se o plano fixou um estilo, passe `--estilo`.
- Pula os `_VAR`. Inspeção opcional: `aplicar.py … --still <frame>` gera uma prova
  `.png` na pasta de trabalho (não no projeto central) — mostre ao usuário antes do lote.

### Etapa 3.2 — Variações de gancho `[02_OTIMIZADOS → 03_PREPARADOS]` (só se o plano pediu VAR)
1. **Infira a ênfase** de cada gancho distinto (palavras-chave: substantivos/verbos
   fortes, 1–2 por frase). Salve um `enfase.json` (`{"VAV19": "palavra1,palavra2"}`).
   Essa inferência é sua — **não** peça aprovação dela.
2. ```bash
   python3 "<skills_dir>/invisible-video-var-gancho-escrito/scripts/aplicar.py" "<lote>/02_OTIMIZADOS" \
     --alvo segmento --var <n> --enfase-map enfase.json
   ```
   Repita por VAR pedido no plano. Se o plano definiu **fonte/fundo customizados**,
   ajuste-os conforme o SKILL.md da var-gancho antes de rodar (o estilo mora em
   `remotion/src/HookText.tsx`).
3. **Portão obrigatório:** a skill gera a prova do **primeiro** gancho e pede OK. É o
   usuário que aprova, na conversa. Só depois ela renderiza o lote.

### Etapa 4 — Combinar `[03_PREPARADOS → 04_COMBINADOS]`
1. Você **julga o encaixe retórico** par-a-par (só nos verticais não-VAR), seguindo o
   método do combinador, e ele **salva a `MATRIZ.md`** em `04_COMBINADOS`.
2. **Portão obrigatório:** o usuário aprova a `MATRIZ.md` antes de gerar qualquer
   vídeo.
3. Aprovado, o combinador expande variantes × formatos e concatena. **NÃO gere `.json`
   de combinação** (OFF por padrão — os `.json` por segmento já existem e os segmentos
   já estão legendados; só ligue se o usuário pedir explicitamente).
```bash
python3 "<skills_dir>/invisible-video-combinador/scripts/descobrir_cortes.py" "<lote>/03_PREPARADOS" --mesma-pasta "<lote>/03_PREPARADOS"
# ...julgar matriz, salvar MATRIZ.md, aprovar, então combinar.py por peça (sem --json)
```

### Etapa 5 — Acelerar `[04_COMBINADOS → 04_COMBINADOS]` (só se o plano pediu)
**Acelerar vem ANTES da trilha** — senão a trilha aceleraria junto e a música sairia
fora de tempo (o `atempo` muda o andamento dela). Por isso roda nas combinações, não
nos finalizados.
```bash
python3 "<skills_dir>/invisible-video-acelerador/scripts/acelerar.py" "<lote>/04_COMBINADOS" \
  --fator <fator_aceleracao>
```
Acelera **tudo** em `04_COMBINADOS` (vertical + quadrado); grava ao lado com
`_ACELERADO_<FATOR>`, originais intactos. Pula o que já tem `_ACELERADO`. Os
originais lentos ficam em `04_COMBINADOS` como subproduto — a trilha (etapa 6) vai
ignorá-los e processar **só** os `_ACELERADO_`.

### Etapa 6 — Trilha `[04_COMBINADOS → 99_FINALIZADOS]`
**Se houve aceleração (etapa 5), passe à trilha só os `_ACELERADO_`**
— não os originais lentos (senão você finaliza as duas versões). Sem aceleração,
processa as combinações normais.
```bash
# com aceleração: aponte os _ACELERADO_ (ex.: um glob ou rode arquivo a arquivo)
python3 "<skills_dir>/invisible-trilha-aplicador/scripts/aplicar.py" "<lote>/04_COMBINADOS" \
  --trilhas "<trilha_pasta do plano>" --alvo-fala <alvo_fala> --alvo-trilha <alvo_trilha>
```
`trilha_pasta` é relativa à raiz do laboratório (resolva pra caminho absoluto) ou já
absoluta. Recomendado validar uma amostra (um vídeo) antes do lote. Se a
trilha-aplicador não tiver filtro por sufixo, rode-a sobre os `_ACELERADO_` um a um
(ou mova os lentos pra um canto antes) — confira o SKILL.md dela.

### Etapa 7 — Nomear `[99_FINALIZADOS → 99_FINALIZADOS]` (só se o plano deu prefixo)
Última etapa. Renomeia os `*_FINALIZADO.mp4` **in-place**, prefixando
`<prefixo><contador>_` em ordem crescente a partir de `nome_inicio`. O sufixo
`_FINALIZADO` é **preservado** (o prefixo só entra na frente).

A **ordem** da numeração é a que o plano definiu (leva por leva, etc.) — o script
NÃO adivinha. **Você** monta a lista ordenada dos finalizados lendo a ordem do
`PLAN_LOTE.md` e a passa em `--arquivos` (um nome por linha) ou `--ordem-json`. Sem
isso, o script cai na ordem alfabética (fallback burro). Monte a ordem explícita
sempre que o plano especificar uma.
```bash
# monte a ordem num txt (um basename por linha, na ordem do plano), então:
python3 "<skills_dir>/invisible-video-lote-producao/scripts/nomear.py" "<lote>/99_FINALIZADOS" \
  --prefixo "<nome_prefixo>" --inicio <nome_inicio> --arquivos ordem.txt
```
Idempotente: um arquivo que já começa com o prefixo é pulado (não re-prefixa). Rode
`--dry-run` primeiro pra conferir o mapa de→para antes de renomear de verdade.

## Fechamento do lote
Quando a `proxima_etapa` for nula (`concluido: true`), resuma o lote (contagem de
finalizados e acelerados) e **sugira** `/invisible-upload` pra subir ao Drive — sem
rodar sozinho.

## Anti-padrões (não faça)
- **Reimplementar uma etapa.** Você invoca a skill filha; o método mora nela.
- **Encadear etapas sem autorização.** Uma por vez, sempre pausando.
- **Confiar no checkbox contra o disco.** A pasta manda; reconcilie com `estado_lote.py`.
- **Pular um portão interno** (prova do gancho, MATRIZ.md). A aprovação é do usuário.
- **Gerar `.json` de combinação** por padrão (os de segmento já bastam).
- **Rodar `/invisible-upload` sozinho** no fim — só sugira.
- **Transcrever áudio antes do denoiser.** Ordem: otimizar → denoiser → transcrever.

## Referência
O contrato do `PLAN_LOTE.md`, a heurística de reconciliação e a sequência completa
estão em `referencia/METODO.md`. O fluxo da esteira (humano) está em
`LINHA-DE-PRODUCAO.md` na raiz do laboratório.
