# CLAUDE.md — plugin `invisible-video-system`

Orienta qualquer instância de Claude que trabalhe neste plugin. Leia antes de editar.

## O que é

O sistema de vídeo da Invisible. Onze skills, encadeadas numa **linha de produção por pastas
de etapa** (ver "Linha de produção" abaixo). Nove fazem o trabalho da esteira (abaixo); duas
orquestram um lote inteiro por cima dela — `invisible-video-lote-plano` (conversa as
preferências, cria a pasta do lote vazia e grava o `PLAN_LOTE.md`) e
`invisible-video-lote-producao` (maestro que lê o plano e invoca as skills da esteira na ordem,
uma etapa por vez, reconciliando o progresso com as pastas):

- **`invisible-video-bruto-desmembrador`** — corta brutos em um vídeo por seção do roteiro.
- **`invisible-video-otimizador`** — **apara as pontas pela fala** (transcreve a bruta com
  WhisperX e usa a 1ª/última palavra pra cortar ruído antes/depois da fala — o silencedetect
  não vê ruído como cortável), escolhe a melhor take quando há várias tentativas da mesma fala
  (transcrição WhisperX, última take vence), remove silêncios internos sem comer palavra e,
  opcionalmente, normaliza o formato no mesmo reencode. A transcrição da bruta é **efêmera**
  (JSON-1, cache em `.transcricao/`, só pro aparo) — NÃO é a legenda; a legenda é o JSON-2 da
  legenda-arquivos, sobre o otimizado. WhisperX virou dependência obrigatória (o aparo
  transcreve sempre). Entrega o corte vertical como `<id>_OTIMIZADO_VERTICAL` em `02_OTIMIZADOS`;
  gera a variante quadrada (1:1) trocando `_VERTICAL` por `_QUADRADO`, com âncora por detecção de
  rosto (YuNet). O sidecar `.md` sai sem token de formato.
- **`invisible-legenda-arquivos`** — aponta uma pasta (tipicamente `02_OTIMIZADOS`) e gera um
  `.json` (timestamp por palavra) via WhisperX, nomeado pela **base** (sem formato nem VAR) —
  um `.json` serve vertical, quadrado e VARs. Deduplica por base (roda WhisperX uma vez por
  segmento). Lote, resumível, sem tocar no original.
- **`invisible-legendas-aplicador`** — queima legenda animada (karaokê) nos **segmentos
  otimizados** com Remotion, consumindo o `.json` da base (acha pelo strip de formato/VAR).
  Estilos `reels`/`minimal`/`classic` e `capsula` (cápsula branca arredondada por frase, texto
  preto — estilo repost/viral, opt-in via `--estilo capsula`), default por formato. Insere
  `_LEGENDADO` antes do token de formato e grava em `03_PREPARADOS`.
- **`invisible-video-var-gancho-escrito`** — variação de gancho escrito: tipografia animada
  sobre fundo preto sincronizada com a fala, com ênfase. Dois alvos: `--alvo combinacao` (gancho
  dentro de uma combinação) ou `--alvo segmento` (clipe de gancho isolado já otimizado, cobre o
  clipe todo, final por si). Respeita a dimensão real (vertical/quadrado). `VAR<n>` do usuário
  entra no nome antes do formato; saída em `03_PREPARADOS`.
- **`invisible-video-combinador`** — lê `03_PREPARADOS` (flat, peças prontas) e concatena N
  segmentos numa cadeia ordenada **sem re-legendar**. Analisa a matriz só sobre os verticais
  não-VAR, salva a `MATRIZ.md` em `04_COMBINADOS` antes de gerar, nivela a loudness por
  atenuação ao mais baixo (a loudness final fica pra trilha), e expande cada par aprovado pelo
  produto cartesiano de variantes por segmento e por formato (sem cruzar formatos).
- **`invisible-trilha-aplicador`** — põe trilha de fundo preservando a fala, com loudness por
  LUFS (não por %): fala a -14 LUFS, trilha a -37 LUFS; `amix normalize=0`, fade/loop; em lote
  distribui as trilhas. Lê de `04_COMBINADOS` e grava na pasta-**irmã**
  `99_FINALIZADOS/<nome>_FINALIZADO.mp4`. Última etapa da esteira.
- **`invisible-denoiser`** — reduz o ruído de fundo do áudio com `afftdn` (níveis `leve`/`medio`/
  `forte` = nr 6/12/21, padrão forte), sem mexer em timbre nem dinâmica. Trabalha **in-place e
  mantém o nome**: substitui o original no mesmo nome (sem sufixo, sem marca), com o vídeo copiado
  sem recompressão. Só avisa no fim que rodou. Independente — roda em qualquer ponto da esteira.
  Recusa rodar nas `BRUTAS/` sem `--forcar`. (EQ e compressão ficaram de fora: testados e
  reprovados em gravação limpa.)
- **`invisible-video-acelerador`** — acelera um vídeo (ou pasta) por um fator fixo à escolha
  (`1.2x` padrão, `1.5x`, `2x`): vídeo (`setpts`) e áudio (`atempo`) pelo mesmo fator, com o
  **tom da voz preservado** (sem chipmunk). Reencoda em H.264 mantendo resolução e fps da fonte.
  Grava ao lado com `_ACELERADO_<FATOR>` no fim (`12X`/`15X`/`2X`); original intacto. Independente
  — roda em qualquer ponto da esteira; em lote pula o que já tem `_ACELERADO`.

O nome do plugin é genérico de propósito — é onde futuras skills de vídeo entram.

## Linha de produção (pastas de etapa + gramática de nomes)

As skills se acoplam por **pastas de etapa numeradas, irmãs sob a raiz do projeto**, e pelo
**nome do arquivo** — não por flags passadas entre elas. Cada skill grava numa pasta-irmã da
entrada (`os.path.dirname(entrada)/<NN_ETAPA>`); `--out-dir` sobrescreve.

```
01_Brutas → [otimizador] → 02_OTIMIZADOS → [legenda-arquivos: .json]
          → [legendas-aplicador / var-gancho-escrito] → 03_PREPARADOS
          → [combinador] → 04_COMBINADOS → [trilha] → 99_FINALIZADOS
```

**Gramática de nomes (o contrato).** Regra única: o token de **formato** é sempre o **último**;
`_VAR<n>` cola no segmento que ele varia; `_OTIMIZADO`/`_LEGENDADO` marcam o processamento.

| Artefato | Pasta | Nome |
|---|---|---|
| Segmento otimizado vertical | `02_OTIMIZADOS` | `<id>_OTIMIZADO_VERTICAL.mp4` |
| Segmento otimizado quadrado | `02_OTIMIZADOS` | `<id>_OTIMIZADO_QUADRADO.mp4` |
| Sidecar de roteiro | `02_OTIMIZADOS` | `<id>_OTIMIZADO.md` (sem formato) |
| `.json` de timestamps | `02_OTIMIZADOS` | `<id>_OTIMIZADO.json` (sem formato, sem VAR) |
| Gancho variado (tipografia) | `03_PREPARADOS` | `<id>_OTIMIZADO_VAR<n>_VERTICAL.mp4` / `_QUADRADO` |
| Segmento legendado (karaokê) | `03_PREPARADOS` | `<id>_OTIMIZADO_LEGENDADO_VERTICAL.mp4` / `_QUADRADO` |
| Combinação | `04_COMBINADOS` | `GANCHO_VAV19__DESENV_VAV57_VERTICAL.mp4` |
| Matriz | `04_COMBINADOS` | `MATRIZ.md` |
| Finalizado (com trilha) | `99_FINALIZADOS` | `<stem>_FINALIZADO.mp4` |

Um `.json`/`.md` por **base** serve todas as variantes (vertical, quadrado, VARs) — mesmo
áudio/texto. As skills que consomem o `.json` (legendas-aplicador, var-gancho) o acham
removendo o token de formato/VAR do nome do clipe.

## Arquitetura

- **Skill fina, lógica nos scripts.** A `SKILL.md` orquestra e aponta; o trabalho pesado
  vive em `skills/invisible-video-bruto-desmembrador/scripts/` (Python puro, stdlib + ffmpeg
  + WhisperX). Cada script imprime JSON e para — os pontos de confirmação ficam com o agente,
  não enterrados no código.
- **O método é sagrado.** Vive em `skills/.../referencia/METODO.md`. Foi validado em número
  numa sessão real. **Não reintroduzir** o que foi descartado: corte por silêncio puro e
  `whisper.cpp -ml 1` para timestamp (interpola, erra segundos). Timestamp é sempre WhisperX.
- **Preservar specs.** O corte recodifica (não copy-codec) para cortar ao frame exato, mas
  lê e preserva codec/pix_fmt/fps/áudio do bruto com ffprobe.

## Os scripts

Em `skills/invisible-video-bruto-desmembrador/scripts/`:

- `bootstrap.py` — detecta/instala ffmpeg (brew) e WhisperX (PATH do sistema ou venv CENTRAL
  único `~/.invisible-video/wxenv`, Python 3.12, instalado uma vez e reusado — nunca por
  projeto); detecta `modelo_pronto` no cache HF para não avisar download à toa. Idempotente.
- `descobrir_pares.py` — pareia vídeo+roteiro por prefixo de nome, tolerante a sufixos.
- `parse_roteiro.py` — extrai seções e frases-âncora; ignora marcação de palco.
- `transcrever.py` — WhisperX com cache (JSON por vídeo, chave nome+tamanho+mtime).
- `achar_bordas.py` — o coração: âncora fuzzy × tomadas × silêncio → timestamps + respiros.
- `cortar.py` — ffprobe specs + ffmpeg recodifica cada seção, pasta plural.
- `pipeline.py` — atalho que expõe as etapas como subcomandos.

Em `skills/invisible-video-combinador/scripts/`:

- `bootstrap.py`, `transcrever.py` — **cópias** das do desmembrador (cada skill autocontida).
- `descobrir_cortes.py` — lê `03_PREPARADOS` (flat, modo mesma-pasta) agrupando por rótulo
  (GANCHO/DESENVOLVIMENTO...) + código (VAVxx); layout de subpastas ainda suportado. Por
  código, agrupa **todas as variantes** num `formatos: {VERTICAL: {base, vars}, QUADRADO:
  {base, vars}}` — nem formato nem `_VAR<n>` é corte novo. A matriz é julgada só sobre o
  `VERTICAL.base`; a expansão (formato × VAR) é do combinar/agente.
- `normalizar.py` — normaliza um corte para o alvo (`scale+pad+setsar=1` + fps + aformat).
  **Rede de segurança:** o ideal é os cortes já chegarem normalizados da otimizadora;
  este script só entra quando algum corte ainda tem specs divergentes do alvo.
- `nivelar.py` — entre normalizar e combinar: mede o LUFS de cada corte da cadeia
  (`loudnorm print_format=json`), casa todos com o **mais baixo** por `volume` negativo
  (atenuação pura, nunca sobe → nunca clipa, dinâmica intacta) e devolve as versões `_niv`.
  Tira o degrau de volume na emenda. A loudness final (−14) é da trilha-aplicador.
- `combinar.py` — concat `-c copy` de gancho+desenvolvimento já normalizados e nivelados.
- `sidecar_corte.py` — junta os `.md` (sidecar de roteiro) das partes no `.md` da combinação,
  pra a cadeia montada carregar o rótulo+texto de cada seção adiante no pipeline.

Em `skills/invisible-video-otimizador/scripts/`:

- `bootstrap.py`, `transcrever.py` — **cópias** das do desmembrador. O `transcrever.py` é
  usado **sempre** agora: o aparo de pontas transcreve a bruta em toda otimização (além da
  seleção de takes). O JSON da bruta é efêmero (cache do transcrever, não vai pra esteira).
- `selecionar_takes.py` — lê o JSON do WhisperX, quebra a fala em blocos por pausa longa,
  agrupa blocos com texto parecido (`difflib`, transitivo) e marca as takes anteriores pra
  descarte (a última vence). Stdlib puro, sem ffmpeg. Devolve os intervalos `descartar` +
  relatório. Não toca no vídeo.
- `otimizar.py` — **apara as pontas** (transcreve a bruta com WhisperX via `transcrever.py`,
  pega a 1ª/última palavra e clampa os keep-segments à janela da fala, com respiro — corta
  ruído antes/depois; FALHA DURO sem WhisperX), subtrai os intervalos de take descartada (via
  `--descartar`) dos keep-segments, roda silencedetect (preset `--modo-silencio`: conservador -35dB/0.3s ou
  justo -33dB/0.15s) → keep-segments com respiro assimétrico (preset `--modo-respiro`:
  conservador 0.10/0.25 ou justo 0.05/0.18). Os dois eixos são INDEPENDENTES; `--silence-*`
  e `--respiro-*` sobrepõem cada preset →
  filter_complex (trim/atrim+concat, com `scale+pad+setsar` opcional via `--normalizar`)
  → reencode → verifica. Descarte de take, corte de silêncio e normalização no MESMO
  reencode. Aceita arquivo ou pasta (lote); `--descartar` vale só pra arquivo único. Por
  padrão preserva specs; com `--normalizar` padroniza no mesmo passo (a normalização migrou
  do combinador pra cá — fundir tudo num só reencode evita gerações extras). O nome de saída
  é limpo via `nome_saida_base()` + token de formato: **preserva toda a identificação** (tipo,
  código, prefixo, número, na ordem original), descarta tokens de ruído de processo (BRUTA,
  VERTICAL, HORIZONTAL, RAW, FINAL, OTIMIZADO) e acrescenta `_OTIMIZADO_VERTICAL` (formato sempre
  o último token). Ex.: `DME_VAV23_VERTICAL_BRUTA_DESENVOLVIMENTO` → `DME_VAV23_DESENVOLVIMENTO_OTIMIZADO_VERTICAL`.
  Saída na pasta-irmã `02_OTIMIZADOS`. O sidecar `.md` é propagado **sem token de formato**
  (`<id>_OTIMIZADO.md`) — um `.md` serve vertical e quadrado. O lote pula qualquer arquivo com
  `OTIMIZADO` no nome.
- `quadrado.py` — gera a variante quadrada (1:1) de cada `_OTIMIZADO_VERTICAL`: recorta um quadrado de
  largura cheia (`crop=W:W:0:y`, descarta só altura) e salva trocando `_VERTICAL` por `_QUADRADO`
  (formato sempre o último token), na mesma pasta `02_OTIMIZADOS`. A âncora
  vertical `y` é decidida por detecção de rosto YuNet (modelo `.onnx` versionado em
  `referencia/modelos/`, olhos a ~30% da altura, mediana de alguns frames), com fallback de
  âncora alta quando não detecta rosto; `--ancora` faz nudge manual e `--contato` gera folha
  de contato pra conferência. Áudio `-c:a copy`, vídeo reencodado no codec da origem. O
  `bootstrap.py` instala `opencv-python-headless` na venv central pra isso.

Em `skills/invisible-legenda-arquivos/scripts/`:

- `bootstrap.py` — **cópia** da do desmembrador (cada skill autocontida).
- `legendar.py` — extrai áudio mono 16k com ffmpeg e roda WhisperX (`--output_format json`),
  depois move o `.json` pro lado do vídeo nomeado pela **base** (sem token de formato nem VAR):
  `GANCHO_VAV19_OTIMIZADO_VERTICAL.mp4` → `GANCHO_VAV19_OTIMIZADO.json`. **Deduplica por base**:
  em lote, agrupa as variantes (vertical/quadrado/VARs) por base e roda WhisperX UMA vez por
  segmento (representante: o `_VERTICAL` não-VAR) — um `.json` serve todas. Resumível (pula a
  base que já tem `.json`, `--forcar` refaz). Não recodifica nem toca no vídeo. O `.json` traz
  `segments[].words[]` (start/end por palavra). **Só JSON:** o `.srt` foi descartado (v2.0.0).
  Se há um sidecar `<base>_OTIMIZADO.md` ao lado, chama `marcar_secoes.py` pra taggear cada
  palavra com a `secao` (e injetar o bloco `secoes`).
- `marcar_secoes.py` — marca cada palavra do `.json` com a seção do roteiro quando existe um
  `<video>.md` ao lado: acha QUANDO cada seção começa casando o texto do MD contra a
  transcrição por similaridade fuzzy (mesma técnica do `achar_bordas.py` do desmembrador),
  não por tempos pré-gravados — robusto a edição entre combinar e legendar. Sem `.md`, o
  `.json` sai sem `secao`.

Em `skills/invisible-legendas-aplicador/scripts/` (+ `remotion/`):

- `bootstrap.py` — **NÃO é cópia** do desmembrador: aqui o ambiente é Remotion/Node, não
  WhisperX. Detecta node/npm/ffmpeg, sincroniza os fontes do template `../remotion/` para um
  projeto central único (`~/.invisible-video/legendas-remotion`) e roda `npm install` só na
  1ª vez ou quando o `package.json` muda. Idempotente. Reporta `pronto`.
- `convert_captions.mjs` — achata `segments[].words[]` do `.json` (saída da
  `invisible-legenda-arquivos`) em `Caption[]` do `@remotion/captions`, uma Caption por
  palavra; interpola timestamp de palavra sem start/end pra nenhuma "sumir".
- `aplicar.py` — orquestra por vídeo: localiza o `.json` da **base** (strip de formato/VAR no
  nome do clipe; sem ele, para e avisa — **não transcreve**), converte → encena no central →
  `npx remotion render <estilo>` → `03_PREPARADOS/<id>_OTIMIZADO_LEGENDADO_VERTICAL.mp4` (insere
  `_LEGENDADO` ANTES do token de formato; formato sempre o último). Lê os **segmentos otimizados**
  de `02_OTIMIZADOS` (não as combinações); pula clipes `_VAR<n>` no lote (vêm prontos da
  var-gancho). Detecta o formato pela dimensão real (ffprobe): default por formato
  (quadrado→`classic`, vertical→`reels`); no quadrado usa `bottomOffsetSquare`. **`--still <frame>`**:
  em vez do vídeo, grava uma prova `.png` (`<nome>_PROVA.png`) com `remotion still` num caminho
  ABSOLUTO na pasta de trabalho/`--out-dir` — nunca no projeto central. (Toda prova das skills de
  vídeo vai pra pasta de trabalho, acessível ao usuário.)
- `remotion/` — template do render (fontes só; `node_modules` vive no central, não no repo).
  `src/Captions.tsx` guarda os `PRESETS` (ritmo, fonte, cor, posição, modo de destaque) e a
  correção de quebra de linha que impede o texto de vazar a margem (**não reverter** — espaço
  fora do `inline-block`). `Root.tsx` adapta duração/dimensão por vídeo via `parseMedia`. O
  preset `hormozi` existe mas está EXPERIMENTAL (em ajuste — não oferecer como pronto).

Em `skills/invisible-video-var-gancho-escrito/scripts/` (+ `remotion/`):

- `bootstrap.py` — Remotion/Node (como o do aplicador, projeto central próprio
  `~/.invisible-video/gancho-escrito-remotion`). Sincroniza os fontes; `npm install` só na 1ª vez.
- `preparar.py` — gera `public/hook.json` (frases do gancho + `emphasis` + `boundaryMs`) e
  `captions.json`; copia o vídeo p/ `public/video.mp4`. `--alvo combinacao` (default) usa `secoes`
  pra achar o boundary do gancho e captions do desenvolvimento; `--alvo segmento` usa a **duração
  do vídeo** como boundary (clipe inteiro é gancho), captions vazio. O `VAR<n>` não entra aqui.
- `aplicar.py` — orquestra: `--alvo {combinacao,segmento}`, resolve o `.json` da **base** (strip
  de formato/VAR), puxa a ênfase por gancho (`--enfase-map`), render em lanes paralelas. Saída em
  `03_PREPARADOS` com `_VAR<n>` inserido ANTES do token de formato (formato sempre o último);
  `--var <n>` (default `1`) é do usuário. No alvo segmento trata como "já legendado" (sem karaokê).
  Remotion respeita a dimensão real (vertical/quadrado) via `calculateMetadata`. **`--still <frame>`**:
  prova `.png` só do primeiro gancho (`<id>_VAR<n>_PROVA<fmt>.png`), uma lane só, gravada na pasta
  de trabalho/`--out-dir` — nunca no projeto central; é a prova do portão de aprovação.
- `convert_captions.mjs` — cópia da do aplicador (modo crua legenda o desenvolvimento).
- `remotion/src/` — `HookText.tsx` é a animação do gancho (fonte/tamanho/cor/entrada — onde
  estilos futuros entram); `Composition.tsx`/`Root.tsx` montam a composição `gancho-escrito`
  (id interno mantido no rename — não confundir com o nome da skill).

Em `skills/invisible-trilha-aplicador/scripts/`:

- `bootstrap.py` — **NÃO é WhisperX nem Remotion:** só ffmpeg/ffprobe (loudness, mix, reencode
  de áudio). Sem Node, sem venv. Detecta/instala via brew. Reporta `pronto`.
- `aplicar.py` — ffmpeg puro: mede LUFS de fala e trilha (ebur128), calcula o ganho de cada
  uma p/ os alvos (`--alvo-fala -14`, `--alvo-trilha -37`), mixa com `amix normalize=0`, trilha
  com fade in/out e `-stream_loop -1`, `-c:v copy`. Em lote distribui as trilhas em rodízio;
  trilhas medidas uma vez (cache). Lê de `04_COMBINADOS`; saída na pasta-**irmã**
  `99_FINALIZADOS/<nome>_FINALIZADO.mp4`. O método (por que LUFS, calibração do -37) está em
  `referencia/METODO.md`.

Em `skills/invisible-denoiser/scripts/`:

- `bootstrap.py` — **só ffmpeg/ffprobe** (igual ao da trilha; `afftdn` é embutido). Sem Node,
  sem WhisperX, sem modelo.
- `denoiser.py` — ffmpeg puro: `afftdn=nr=<6|12|21>` no áudio, `-c:v copy` no vídeo. **In-place,
  mesmo nome** (temp → `os.replace` sobre o próprio arquivo; sem sufixo, original substituído).
  Arquivo único ou pasta (processa toda a mídia — sem marca no nome, não pula nada). Recusa alvo
  em `BRUTAS/` sem `--forcar`. Sem EQ/compressão (reprovados). Método em `referencia/METODO.md`.

Em `skills/invisible-video-acelerador/scripts/`:

- `bootstrap.py` — **só ffmpeg/ffprobe** (`setpts`/`atempo` são embutidos). Sem Node, sem
  WhisperX, sem modelo.
- `acelerar.py` — ffmpeg: `setpts=PTS/<fator>` no vídeo + `atempo=<fator>` no áudio (preserva o
  tom; os fatores 1.2/1.5/2.0 cabem no range `[0.5,2.0]` do atempo), reencode H.264 forçando o
  `-r` do fps da fonte. Grava ao lado com `_ACELERADO_<FATOR>` (12X/15X/2X); arquivo único ou
  pasta (pula `_ACELERADO`). Um arquivo por execução. Método em `referencia/METODO.md`.

**Por que cópias e não scripts compartilhados:** decisão de manter cada skill autocontida.
Ao corrigir um bug em `bootstrap.py`/`transcrever.py`, replicar em todas as cópias — atenção:
o `bootstrap.py` do `invisible-legendas-aplicador` é o ÚNICO diferente (Remotion, não WhisperX),
não entra nessa replicação. As demais skills têm a sua `bootstrap.py` de WhisperX; a
`invisible-legenda-arquivos` tem só `bootstrap.py`, com lógica própria de WhisperX em `legendar.py`.
O `bootstrap.py` do `invisible-denoiser` também é só ffmpeg (como o da trilha), não WhisperX.

## Convenções

- **Idioma:** PT-BR (nomes de arquivo de script em PT-BR, kebab/snake conforme o tipo).
- **Skill:** prefixo `invisible-` no `name:` do frontmatter (convenção Invisible).
- **Saídas** (os cortes) vão para a pasta do projeto do usuário (GANCHOS/, etc.) — não versionadas.
- **Defaults validados** (respiro 0.15/0.30, crf 18, large-v3/pt) só mudam com motivo.

## Versionamento (semver)

A versão vive em `.claude-plugin/plugin.json`. Bump obrigatório em toda mudança de
comportamento que vai pra `main` — senão o marketplace não entrega nada novo.

- **patch** — bug, ajuste de texto, ajuste de parâmetro.
- **minor** — recurso novo compatível (script novo, etapa nova, skill nova de vídeo).
- **major** — mudança incompatível (renomear/remover skill, mudar contrato de saída).

## Fluxo de trabalho (Git)

Nunca trabalhar direto na `main`: worktree + branch, testar, aprovar, merge. Push só
quando o Arno pedir. Registrar a entrada no `.claude-plugin/marketplace.json` da raiz do repo.
