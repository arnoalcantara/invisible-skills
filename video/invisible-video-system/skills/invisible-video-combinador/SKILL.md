---
name: invisible-video-combinador
description: >
  Combina segmentos de roteiro JÁ PRONTOS (legendados/variados, vindos de 03_PREPARADOS) para gerar peças novas — anúncios, VSLs — concatenando um corte de cada segmento numa cadeia ordenada, SEM re-legendar (as peças já chegam legendadas). Os segmentos são de nomes LIVRES (padrão Invisible: GANCHO, DESENVOLVIMENTO, CTA; mas pode ser LEAD, HISTORIA, OFERTA, FECHAMENTO), lidos pelo rótulo no nome (modo mesma-pasta, flat). O usuário dirige o esquema: quais segmentos entram, em que ordem, quais VARIAM (cruzam) e quais ficam FIXOS (a peça nativa de cada origem). A análise da matriz é feita SÓ sobre os clipes VERTICAIS não-VAR (um por segmento+código) — o áudio/texto é idêntico entre formatos e variações, então a matriz vale pra todos. A skill transcreve esses representantes (com cache), julga o encaixe retórico par-a-par, monta a matriz justificada (✅/⚠️/❌) e SALVA a MATRIZ.md em 04_COMBINADOS ANTES de gerar qualquer vídeo, pede aprovação, normaliza e concatena. Na hora de combinar, EXPANDE cada par aprovado pelo produto cartesiano das variantes por segmento (clipe base + cada VAR) e por formato (VERTICAL×VERTICAL, QUADRADO×QUADRADO, RETRATO×RETRATO — cada formato reportado pelo descobrir_cortes.py), nunca cruzando formatos. Ex.: GANCHO com base+VAR1 e DESENV só base → 2 peças por formato. Use quando o usuário pedir "combina os cortes", "cruza gancho × desenvolvimento", "monta os anúncios", "gera as combinações", "monta as VSLs". Saída em 04_COMBINADOS (vertical 1080×1920, quadrado 1080×1080, retrato 1080×1350). Requer ffmpeg e WhisperX (faz bootstrap).
---

# Combinador de Vídeo (cadeia de segmentos)

Você combina segmentos de roteiro **já prontos** — clipes legendados (`_LEGENDADO`) e ganchos variados (`_VAR<n>`) que chegam de `03_PREPARADOS` — concatenando um de cada segmento numa **cadeia ordenada** para gerar peças novas (anúncios curtos, VSLs longas), **sem re-legendar**.

Na linha de produção, a entrada é a pasta **`03_PREPARADOS`** (flat): ganchos e desenvolvimentos prontos, soltos, distinguidos pelo rótulo no nome. A saída vai pra pasta-irmã **`04_COMBINADOS`**. Os nomes são livres e os segmentos podem ser dois ou mais — uma VSL pode ter `LEAD`, `HISTORIA`, `OFERTA`, `FECHAMENTO`. Não trave em nome nenhum.

**Quem dirige o esquema é o usuário.** Ele decide, na execução: quais segmentos entram, em que ordem se concatenam, quais **variam** (cruzam, gerando combinações) e quais ficam **fixos/nativos** (acompanham a peça de origem, sem cruzar).

## Conceitos

- **Segmento** — um grupo de cortes da mesma sessão (GANCHOS, DESENVOLVIMENTOS, OFERTA...). Nome livre. Pode ser uma **subpasta** ou um grupo de cortes **soltos na mesma pasta**, identificados pelo rótulo no nome do arquivo.
- **Cadeia** — a ordem em que os segmentos se concatenam. Ex.: gancho → desenvolvimento → CTA. Definida/confirmada pelo usuário; **não se inverte**.
- **Código nativo** — o código no nome do corte (ex.: VAV19). Cortes de segmentos diferentes com o **mesmo código** vieram do **mesmo vídeo de origem** → são a peça nativa daquele vídeo.
- **Eixo que varia × segmento fixo:**
  - **Varia** — todos os cortes daquele segmento entram no cruzamento.
  - **Fixo (nativo)** — o corte daquele segmento é o que tem o **mesmo código** da peça base; não cruza, acompanha. Ex.: "varia gancho × desenvolvimento, mas a OFERTA é a nativa de cada vídeo".

## Variantes por formato e VAR (o modelo de dados)

O `descobrir_cortes.py` agrupa, por segmento+código, **todas as variantes do mesmo corte** — porque o áudio/texto é idêntico entre elas. Cada corte vira:

```
GANCHO / VAV19:
  VERTICAL: { base: <path>, vars: {1: <path>, 2: <path>} }
  QUADRADO: { base: <path>, vars: {1: <path>} }
  RETRATO:  { base: <path>, vars: {} }
```

Nem o formato (`_VERTICAL`/`_QUADRADO`/`_RETRATO`) nem a variação (`_VAR<n>`) é um corte retórico novo — são variantes do mesmo corte. Os formatos de feed recortados são o quadrado (1:1, `_QUADRADO`) e o retrato (4:5, 1080×1350, `_RETRATO`); o vertical (9:16) é o canônico. Daí duas regras:

- **A matriz é julgada UMA vez**, sobre o `VERTICAL` `base` (não-VAR) de cada segmento+código. Vale pra todos os formatos e VARs.
- **A expansão acontece só ao combinar** (produto cartesiano formato × VAR por segmento) — ver Fase 6. **Nunca cruza formato** (vertical só com vertical, quadrado só com quadrado, retrato só com retrato). Itere sobre os formatos que o `descobrir_cortes.py` reportar — não assuma um conjunto fixo. Se um formato falta em algum segmento da cadeia, pula esse formato e avisa.

## Princípio crítico de julgamento (não esquecer)

Case pelo que a peça anterior **PROMETE** × o **tipo de abertura** da peça seguinte — **NÃO pela forma gramatical.** Um gancho que promete "vou te mostrar a vida dos meus alunos" casa com um desenvolvimento que abre com depoimento de aluno, mesmo sem ser pergunta. (Erro real de uma sessão: reprovar gancho+depoimento por regra gramatical cega.)

Com mais de dois segmentos, julgue **par-a-par cada transição vizinha que vai variar** (gancho→desenvolvimento, depois desenvolvimento→CTA). A cadeia é fluida quando toda transição variável é fluida. Transições para um segmento fixo nativo não precisam de julgamento (já vieram juntas do mesmo vídeo).

## Fluxo de execução

### Fase 0 — Bootstrap
`python3 scripts/bootstrap.py --check-only`. Garante ffmpeg + WhisperX. Se o modelo não estiver em cache, avise o download de ~1.5GB na 1ª transcrição.

### Fase 1 — Descobrir os segmentos
`python3 scripts/descobrir_cortes.py "<03_PREPARADOS>"`. Na linha de produção a entrada é `03_PREPARADOS` no modo **mesma pasta** (flat): clipes soltos distinguidos pelo **rótulo no nome** (GANCHO, DESENVOLVIMENTO...) + **código** (VAV19, 28...). O script agrupa por rótulo, extrai o código e, por código, agrupa as variantes por formato e VAR (ver "Variantes por formato e VAR"). O layout de subpastas continua suportado (`modo: subpastas`) pra projetos antigos.

Se os rótulos **não** são os conhecidos (gancho, desenvolvimento, cta, lead, historia, oferta, fechamento, prova), declare-os: `--mesma-pasta "<03_PREPARADOS>" --rotulos LEAD OFERTA FECHAMENTO`. Arquivos sem rótulo reconhecido voltam em `sem_rotulo` — mostre-os ao usuário.

Mostre ao usuário os segmentos achados (nome, códigos, e por código os formatos/VARs disponíveis) e o modo detectado.

### Fase 2 — Definir o esquema de combinação (DIRIGIDO PELO USUÁRIO)
**Pergunte explicitamente** — não assuma. Confirme:
1. **Quais segmentos** entram na peça.
2. **A ordem** da cadeia (concatenação). Sugira a ordem retórica, mas confirme.
3. **Quais variam e quais ficam fixos (nativos).** Ex.: "varia GANCHOS × DESENVOLVIMENTOS; OFERTA fixa na nativa de cada vídeo".

Se o usuário não quiser usar a auto-descoberta, ele pode apontar a ordem:
- `python3 scripts/descobrir_cortes.py "<projeto>" --mesma-pasta "<03_PREPARADOS>" --rotulos GANCHO DESENVOLVIMENTO OFERTA` (a ordem dos `--rotulos` orienta a ordem da cadeia)

A combinação mais usual é só **gancho × desenvolvimento** — mas é o usuário que determina, sempre.

As peças de `03_PREPARADOS` já chegam **prontas** (legendadas e/ou variadas, normalizadas pelo otimizador lá atrás). O combinador **não re-legenda**: só concatena. O nome carrega rótulo + código + `_OTIMIZADO[_LEGENDADO][_VAR<n>]` + formato no fim — o código (VAV19) é extraído e os tokens de processo/formato/VAR não atrapalham o casamento nativo.

### Fase 3 — Obter o texto dos representantes que serão julgados (sidecar .md → senão transcreve)
A matriz é julgada **só sobre o VERTICAL base (não-VAR)** de cada segmento+código (`formatos.VERTICAL.base`) — o áudio/texto é o mesmo entre formatos e VARs. Só os segmentos que **variam** precisam do texto (os fixos nativos não se julgam). Para cada representante, **primeiro cheque o sidecar** `<corte_sem_ext>.md` ao lado dele:

- **Se o `.md` existe** → leia o texto dele. Não transcreva.
- **Se falta** → transcreva e **grave o `.md`** ao lado do corte (assim a próxima combinação reusa):
```bash
python3 scripts/transcrever.py "<vertical_base>" --whisperx-bin <do bootstrap> \
    --cache-dir "<pasta_projeto>/.transcricao/wx_out"
python3 scripts/sidecar_corte.py --json "<json_da_transcrição>" \
    --rotulo <SEGMENTO_EM_MAIÚSCULAS> --out "<corte_sem_ext>.md"
```
O rótulo é o do segmento (GANCHO, DESENVOLVIMENTO...). Para a matriz importa só o texto. A transcrição reusa cache (chave nome+tamanho+mtime). **Não transcreva os clipes `_VAR<n>` nem os `_QUADRADO`** — a matriz já vale pra eles.

### Fase 4 — Analisar e propor a matriz (só verticais não-VAR)
Classifique cada representante (vertical base) dos segmentos que variam:
- O que ele **promete** / qual continuação pede (se for o lado que abre a transição).
- O **tipo de abertura** — dor, revelação, contestação, prova social/depoimento (se for o lado que recebe).

Julgue **par-a-par** cada transição variável. Monte a matriz justificada: ✅ (fluido) / ⚠️ (limítrofe, com ressalva escrita) / ❌ (não casa), **com o porquê de cada célula**. Para cadeias de 3+ que variam em mais de uma transição, mostre a matriz de cada transição. Inclua sempre os **pares nativos** (mesma origem) como combinações válidas.

A matriz é sobre **códigos** (GANCHO/VAV19 × DESENV/VAV57), não sobre formatos/VARs — esses são expandidos depois. Conte quantas peças a expansão vai gerar (pares aprovados × formatos comuns × produto das variantes por segmento) e mostre esse número.

### Fase 5 — Salvar a MATRIZ.md ANTES de gerar (passo obrigatório)
Antes de qualquer vídeo, **escreva `04_COMBINADOS/MATRIZ.md`** com:
- o esquema (segmentos, ordem, o que varia × o que é fixo);
- a matriz ✅/⚠️/❌ justificada (uma tabela por transição variável);
- a **contagem de peças** que serão geradas, já com as expansões (formato × VAR por segmento), listando os nomes de arquivo previstos.

Crie a pasta `04_COMBINADOS` se não existir e grave o `.md` lá. Então diga: "Matriz salva em 04_COMBINADOS/MATRIZ.md. Nada de vídeo foi gerado ainda. Confirma este esquema e esta matriz?" O usuário pode forçar ⚠️/❌, cortar ✅, ou pedir ajustes — reescreva a MATRIZ.md e só então prossiga.

### Fase 6 — Config de saída
Pergunte, oferecendo o default entre colchetes:
- **[Full HD vertical 1080×1920, 30fps, HEVC/x265 CRF20, AAC 48k stereo, .mp4]** ← padrão (quadrado 1080×1080, retrato 1080×1350).
- Alternativas: **4K** (2160×3840), **MOV**, **resolução nativa** (a maior entre os cortes da cadeia, sem rebaixar), **H.264/x264**.

### Fase 7 — Expandir, normalizar e montar
A matriz aprovada é sobre **códigos**. Aqui ela vira peças concretas pela **expansão cartesiana**. Para cada par aprovado (segA/codX × segB/codY na ordem da cadeia):

1. **Para cada formato F reportado pelo `descobrir_cortes.py`** (VERTICAL, QUADRADO, RETRATO — o conjunto é dinâmico, não fixo) em que **todos** os segmentos da cadeia têm clipe (`formatos[F]` com `base` ou `vars`):
2. **Produto cartesiano das variantes por segmento.** Para cada segmento, o conjunto de variantes é `{base} ∪ {cada VAR}` daquele formato. Combine uma variante de cada segmento — todas as combinações.
   - Ex.: GANCHO/VAV19 tem `base`+`VAR1` em VERTICAL; DESENV/VAV57 só `base` → **2 peças verticais**: `GANCHO_VAV19__DESENV_VAV57` (base×base) e `GANCHO_VAV19_VAR1__DESENV_VAV57` (VAR1×base).
   - Se um segmento tem `base`+`VAR1`+`VAR2` e o outro `base`+`VAR1` → 3×2 = 6 peças naquele formato.
3. **Nunca cruze formato** (vertical só com vertical). Se F falta em algum segmento da cadeia, pule F e avise.

Para cada peça (uma escolha de variante por segmento, num formato):
- **Normalize** cada corte que ainda não bate o alvo (rede de segurança; as peças de `03_PREPARADOS` já costumam vir no alvo — cheque specs com ffprobe e pule quem bate). A altura do alvo é **por formato**: vertical 1920, quadrado 1080, retrato 1350 (largura 1080 sempre). Como as peças já vêm reenquadradas do otimizado, o normalize aqui não deve reescalar — só reencoda specs de áudio/fps se destoarem.
```bash
# vertical (ajuste --altura ao formato da peça: 1920 vertical / 1080 quadrado / 1350 retrato):
python3 scripts/normalizar.py "<corte>" --out "<tmp>/<corte>.mp4" \
    --largura 1080 --altura 1920 --fps 30 --vcodec libx265 --crf 20 \
    --sample-rate 48000 --canais 2
```
- **Nivele a loudness da cadeia** (tira o degrau na emenda; atenuação ao mais baixo, nunca sobe). A loudness final (−14 LUFS) é da `invisible-trilha-aplicador`, não aqui.
```bash
python3 scripts/nivelar.py "<seg1_norm>" "<seg2_norm>" "<segN_norm>" --out-dir "<tmp>"
```
- **Concatene** na ordem da cadeia, com as versões niveladas. Para a peça **VERTICAL base×base×…** (a representante), passe os **sidecars `.md` dos cortes originais** pra gerar o roteiro da combinação; para as demais peças (quadrado e qualquer VAR), **não** passe `--sidecars` (um `.md` só por combinação, o da vertical base — mesmo áudio/texto):
```bash
# peça vertical representante (gera o .md):
python3 scripts/combinar.py "<seg1_niv>" "<seg2_niv>" "<segN_niv>" \
    --out "<projeto>/04_COMBINADOS/<nome_da_peça>_VERTICAL.mp4" \
    --sidecars "<seg1_orig>.md" "<seg2_orig>.md" "<segN_orig>.md" \
    --out-md "<projeto>/04_COMBINADOS/<nome_da_peça>_VERTICAL.md"
# demais peças (quadrado, VARs): sem --sidecars
python3 scripts/combinar.py "<…>" --out "<projeto>/04_COMBINADOS/<nome_da_peça>_QUADRADO.mp4"
```
O `.md` junta as seções em sequência, **sem tempos** — a marcação por tempo já foi feita na legendagem dos segmentos. Se um corte não tiver `.md`, vai em `sidecars_faltando` e segue.

### Fase 8 — Resumo
Liste as peças geradas em `04_COMBINADOS/`, quantas e por qual esquema (e a expansão: nº de pares × formatos × variantes), e aponte 1–2 decisões representativas da matriz (de preferência uma ⚠️). Aponte qualquer formato pulado por falta de variante.

## Pontos de confirmação
1. Segmentos descobertos. 2. **Esquema** (quais, ordem, varia×fixo). 3. **MATRIZ.md salva e aprovada**. 4. Config de saída. 5. Resumo final.

## Nomenclatura
- Pasta: `04_COMBINADOS/` (pasta-irmã, etapa da linha). A matriz vai em `04_COMBINADOS/MATRIZ.md`.
- Arquivo: os **rótulos dos segmentos com códigos (e VAR quando houver), na ordem da cadeia**, separados por `__`, com o **token de formato sempre no fim**. O `_VAR<n>` cola no segmento que ele varia:
  - base × base: `GANCHO_VAV19__DESENV_VAV57_VERTICAL.mp4` (e `_QUADRADO.mp4`)
  - VAR no gancho: `GANCHO_VAV19_VAR1__DESENV_VAV57_VERTICAL.mp4`
  - VAR no desenvolvimento: `GANCHO_VAV19__DESENV_VAV57_VAR1_VERTICAL.mp4`
  - três segmentos: `GANCHO_VAV19__DESENV_VAV57__OFERTA_VAV19_VERTICAL.mp4`
  - O `.md` é só o da peça vertical base (não há `.md` por formato nem por VAR).

## Anti-padrões (não faça)
- Travar em GANCHOS/DESENVOLVIMENTOS — os segmentos são de nome livre e podem ser 2 ou mais.
- Assumir que os cortes estão em subpastas — podem estar soltos na mesma pasta, separados pelo rótulo no nome. Confira o `modo` na saída do descobridor.
- Decidir o esquema sozinho — quem diz o que varia, o que é fixo e a ordem é o **usuário**.
- Inverter a ordem da cadeia.
- Reprovar por **forma gramatical** (a promessa é que manda).
- Concatenar specs mistas (quebra o `-c copy`) — mas também não re-normalizar cortes que já chegaram no alvo da otimizadora: cheque specs antes e pule quem já bate.
- Gerar vídeo antes de salvar a `MATRIZ.md` e ter a aprovação.
- Re-legendar as peças — elas já chegam prontas de `03_PREPARADOS`. O combinador só concatena.
- Transcrever segmentos fixos nativos, clipes `_VAR<n>` ou `_QUADRADO` — a matriz é só sobre o vertical base não-VAR.
- Tratar `_QUADRADO` ou `_VAR<n>` como corte retórico novo — são variantes do mesmo corte (mesmo áudio). Não duplicam a matriz; expandem só na hora de combinar.
- Re-julgar o encaixe por formato/VAR — é o mesmo áudio; julga uma vez, vale pra todos.
- Cruzar formato no concat (vertical com quadrado) — pareie vertical-com-vertical, quadrado-com-quadrado.
- Gerar `.md` por formato ou por VAR — um `.md` só por combinação (o da vertical base).
- Rebaixar resolução quando o usuário pediu "nativa".
- **Pular o nivelamento** quando a cadeia mistura cortes de origens diferentes — é o que tira o degrau de volume na emenda. (Cadeia de um corte só não precisa.)
- **Nivelar pra cima.** O nivelamento é sempre por atenuação ao piso da cadeia; subir trecho baixo clipa/esmaga. A loudness final é da trilha-aplicador.

## Referência
O método de julgamento (par-a-par, promessa × abertura), o modelo de segmentos N-lados e as razões técnicas (normalizar antes de concatenar, specs do alvo) estão em `referencia/METODO.md`.
