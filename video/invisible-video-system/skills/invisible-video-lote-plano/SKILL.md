---
name: invisible-video-lote-plano
description: >
  Planeja um novo lote de produção de vídeo e monta o esqueleto dele. Conduz uma conversa curta com o usuário para capturar as PREFERÊNCIAS do lote — estilo de legenda, quais variações de gancho usar (e se com fonte/fundo customizados), qual pasta de trilha, e se os finalizados serão acelerados e em qual velocidade —, então cria a pasta do lote na raiz do laboratório com a estrutura de pastas da esteira v2.6.0 (01_BRUTAS, 02_OTIMIZADOS, 03_PREPARADOS, 04_COMBINADOS, 99_FINALIZADOS) e grava um PLAN_LOTE.md com as decisões e os checkboxes de cada etapa. NÃO decide a matriz de combinações (isso é do combinador, na execução) nem processa qualquer mídia — só planeja e cria a estrutura vazia. A pasta nasce VAZIA: ao fim, instrui o usuário a jogar as brutas em 01_BRUTAS e rodar a invisible-video-lote-producao. O PLAN_LOTE.md é o contrato lido pela invisible-video-lote-producao. Use quando o usuário pedir "planejar um lote novo", "criar um lote de vídeo", "começar um lote", "montar a estrutura de um lote", "novo lote do Gurgel/Filhos do Trovão...". Não requer ffmpeg nem nada — só cria pastas e um documento.
---

# Planejador de Lote de Vídeo

Você planeja um lote novo com o usuário e cria o esqueleto dele. Duas entregas: a
**pasta do lote** com a estrutura da esteira v2.6.0 (vazia) e o **`PLAN_LOTE.md`**
preenchido — o documento que a `invisible-video-lote-producao` vai ler e executar.

> Você **não decide a matriz** de combinações (gancho × desenvolvimento) — isso é
> trabalho do combinador, na execução, quando o material já existe. Você **não
> processa mídia**. Você captura preferências e monta a estrutura.

## O par de skills

- **`invisible-video-lote-plano`** (esta) — planeja e cria a estrutura. Roda uma vez.
- **`invisible-video-lote-producao`** — executa a esteira etapa a etapa, lendo o
  `PLAN_LOTE.md`. Roda quantas vezes precisar (retomável).

O `PLAN_LOTE.md` é o **contrato** entre as duas: você escreve, ela lê e marca os
checkboxes. A fonte da verdade do progresso são as **pastas**; o checkbox é resumo.

## A conversa (capture, não processe)

Conduza de forma direta, oferecendo o default em cada ponto. **A pasta vai nascer
vazia** — nenhuma decisão aqui depende de ver o material, então não peça brutas.

1. **Nome do lote.** Convenção: `Lote NN - <projeto>` (ex.: `Lote 02 - Gurgel DME`).
   Olhe a raiz do laboratório para sugerir o próximo número (`Lote 01...` já existe).

2. **Estilo de legenda.** Default **auto** (vertical → `reels`, quadrado → `classic`).
   Ofereça trocar para um estilo fixo: `reels` (palavra acende amarelo),
   `minimal` (branco, futuro esmaecido) ou `classic` (bloco no rodapé). Não ofereça
   `hormozi` (experimental).

3. **Variações de gancho.** Pergunte se o lote terá gancho escrito (tipografia
   animada). Hoje existe **VAR1**; o número é do usuário (pode haver VAR2, VAR3...
   no futuro). Se sim:
   - quais VARs (lista, ex.: `[1]`);
   - **fonte e fundo**: padrão (Hoefler Text, fundo preto) ou customizados — se
     customizados, anote a descrição que o usuário der.
   Se não houver variação, a etapa 3.2 nasce já marcada como pulada.

4. **Pasta de trilha.** Default `00_Recursos/Trilhas` (biblioteca compartilhada).
   Pergunte se este lote usa uma pasta específica de trilha. Anote o caminho
   (relativo à raiz do lab ou absoluto). Níveis de loudness são os defaults da
   trilha-aplicador (fala −14, trilha −37 LUFS) — só pergunte se o usuário quiser
   trilha mais presente/discreta.

5. **Aceleração.** Pergunte se os vídeos serão acelerados. Default da skill de
   aceleração é **1.2x**; ofereça 1.5x ou 2x. Se sim, a aceleração roda **antes da
   trilha** (etapa 5, em `04_COMBINADOS`) — porque acelerar depois aceleraria a
   música junto e a tiraria do tempo — e a trilha (etapa 6) entra por cima do ritmo
   final, consumindo só os `_ACELERADO_`. Acelera **tudo** (vertical + quadrado). Se
   não, a etapa 5 nasce pulada e a trilha lê as combinações normais.

6. **Modo de otimização** (opcional, só se o usuário tiver preferência): silêncio e
   respiro, cada um `conservador` (default, validado) ou `justo`.

Resuma as escolhas em uma frase e confirme antes de criar.

## Criar a estrutura

Monte o JSON de decisões e rode o `criar_lote.py`. A `--raiz` é a raiz do
laboratório (a pasta que contém `00_Recursos/` e os `Lote NN - ...`). A `--data` é
hoje (você tem a data atual no contexto; passe AAAA-MM-DD).

```bash
python3 scripts/bootstrap.py --raiz "<raiz do laboratório>" --check-only
```

Escreva as decisões num JSON temporário (campos ausentes assumem o default):

```json
{
  "estilo_legenda": "auto",
  "variacoes": [1],
  "var_fonte": "padrao",
  "var_fundo": "padrao",
  "trilha_pasta": "00_Recursos/Trilhas",
  "alvo_fala": -14,
  "alvo_trilha": -37,
  "acelerar": true,
  "fator_aceleracao": 1.2,
  "modo_silencio": "conservador",
  "modo_respiro": "conservador",
  "observacoes": ""
}
```

```bash
python3 scripts/criar_lote.py \
  --raiz "<raiz do laboratório>" \
  --nome "Lote 02 - Gurgel DME" \
  --data 2026-06-24 \
  --decisoes "<json temporário>"
```

O script cria as cinco pastas e grava o `PLAN_LOTE.md`. Ele **recusa sobrescrever**
um lote existente (exit 2) — só refaz com `--forcar`, e nesse caso confirme com o
usuário antes (reescrever apaga o progresso registrado nos checkboxes).

## Fechamento

Mostre ao usuário o `PLAN_LOTE.md` gerado e diga, em duas linhas:
1. **Jogue as brutas em `01_BRUTAS/`** (ganchos, desenvolvimentos, CTAs — ou um
   bruto longo + roteiro, se for usar o desmembrador).
2. **Rode `/invisible-video-lote-producao`** apontando para este lote, quando pronto.

## Anti-padrões (não faça)
- **Decidir a matriz de combinações.** Não é seu trabalho — é do combinador, na
  execução, com o material à mão.
- **Pedir as brutas / esperar material.** A pasta nasce vazia de propósito.
- **Processar mídia.** Você só cria pastas e o documento.
- **Sobrescrever um lote existente sem confirmar.** `--forcar` apaga o progresso.
- **Inventar uma etapa fora da esteira v2.6.0.** O fluxo é fixo; o que varia são os
  parâmetros (legenda, VAR, trilha, fator).

## Referência
O contrato do `PLAN_LOTE.md` e a sequência completa das etapas estão em
`referencia/METODO.md`. O fluxo da esteira (humano) está em `LINHA-DE-PRODUCAO.md`
na raiz do laboratório.
