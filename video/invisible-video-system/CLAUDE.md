# CLAUDE.md — plugin `invisible-video-system`

Orienta qualquer instância de Claude que trabalhe neste plugin. Leia antes de editar.

## O que é

O sistema de vídeo da Invisible. Oito skills, encadeáveis na mesma pasta de projeto:

- **`invisible-video-bruto-desmembrador`** — corta brutos em um vídeo por seção do roteiro.
- **`invisible-video-combinador`** — cruza ganchos × desenvolvimentos por encaixe retórico
  e gera anúncios combinados (consome as saídas do desmembrador). Antes de concatenar, nivela
  a loudness dos cortes da cadeia por atenuação ao mais baixo (nunca sobe, pra não clipar),
  eliminando o degrau de volume na emenda — a loudness final fica pra trilha-aplicador.
- **`invisible-video-otimizador`** — escolhe a melhor take quando há várias tentativas
  da mesma fala (transcrição WhisperX, última take vence), remove silêncios internos sem
  comer palavra e, opcionalmente, normaliza o formato no mesmo reencode (corte pronto pra
  concatenar). Sob demanda, gera também a variante quadrada (1:1, `_QUADRADO`) recortando
  a largura cheia com âncora vertical por detecção de rosto (YuNet).
- **`invisible-legenda-arquivos`** — aponta um vídeo ou uma pasta e gera, ao lado de cada vídeo e
  com o mesmo nome, um `.json` (transcrição com timestamp por palavra, fonte pra animação
  palavra-a-palavra no Remotion) via WhisperX. Só o `.json` — é o que o pipeline consome.
  Lote, resumível, sem tocar no original.
- **`invisible-legendas-aplicador`** — queima legenda animada (karaokê) no vídeo com Remotion,
  consumindo o `.json` da `invisible-legenda-arquivos` (não transcreve). Estilos `reels`/`minimal`/
  `classic`; saída em `LEGENDADOS/<nome>_LEGENDADO.mp4`, sem tocar no original. É a última etapa
  do pipeline de legenda (reencode obrigatório — pixel novo sobre o vídeo).
- **`invisible-video-var-gancho-escrito`** — gera uma variação de gancho escrito: troca a
  imagem do gancho por uma animação de tipografia sobre fundo preto (palavras sincronizadas
  com a fala, por frase, com ênfase), mantendo o áudio; segue com o desenvolvimento. O número
  da variação é do usuário (a skill pergunta qual `VAR<n>` e estampa no nome). Opera sobre o
  `_LEGENDADO.mp4` (não re-legenda) ou a combinação crua; saída `LEGENDADOS/<comb>_LEGENDADO_VAR<n>.mp4`.
- **`invisible-trilha-aplicador`** — põe trilha de fundo preservando a fala, com loudness por
  LUFS (não por %): fala a -14 LUFS (ganho linear), trilha a -37 LUFS (~23 dB abaixo); `amix
  normalize=0`, fade in/out e loop; em lote distribui as trilhas. Vídeo sem recompressão; saída
  `99_FINALIZADOS/<nome>_FINALIZADO.mp4`. Tipicamente a última etapa da esteira.
- **`invisible-denoiser`** — reduz o ruído de fundo do áudio com `afftdn` (níveis `leve`/`medio`/
  `forte` = nr 6/12/21, padrão forte), sem mexer em timbre nem dinâmica. Trabalha **in-place**:
  salva `_DENOISER` no fim do nome e substitui o original, com o vídeo copiado sem recompressão.
  Independente — roda em qualquer ponto da esteira. Recusa rodar nas `BRUTAS/` sem `--forcar`.
  (EQ e compressão ficaram de fora: testados e reprovados em gravação limpa.)

O nome do plugin é genérico de propósito — é onde futuras skills de vídeo entram.

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
- `descobrir_cortes.py` — acha `GANCHOS/` e `DESENVOLVIMENTOS/`, extrai o código (VAVxx).
  Pareia a variante quadrada (`_QUADRADO`) com a vertical de mesmo código numa entrada só
  (`arquivo` + `arquivo_quadrado`); `QUADRADO` entra no set de ruído. Quadrado órfão (sem a
  vertical de mesmo código) vira corte próprio (`orfao_quadrado`), não some.
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

- `bootstrap.py`, `transcrever.py` — **cópias** das do desmembrador. O `transcrever.py`
  só é usado quando há seleção de takes (transcrição WhisperX); o resto da skill é ffmpeg puro.
- `selecionar_takes.py` — lê o JSON do WhisperX, quebra a fala em blocos por pausa longa,
  agrupa blocos com texto parecido (`difflib`, transitivo) e marca as takes anteriores pra
  descarte (a última vence). Stdlib puro, sem ffmpeg. Devolve os intervalos `descartar` +
  relatório. Não toca no vídeo.
- `otimizar.py` — subtrai os intervalos de take descartada (via `--descartar`) dos
  keep-segments, roda silencedetect (preset `--modo-silencio`: conservador -35dB/0.3s ou
  justo -33dB/0.15s) → keep-segments com respiro assimétrico (preset `--modo-respiro`:
  conservador 0.10/0.25 ou justo 0.05/0.18). Os dois eixos são INDEPENDENTES; `--silence-*`
  e `--respiro-*` sobrepõem cada preset →
  filter_complex (trim/atrim+concat, com `scale+pad+setsar` opcional via `--normalizar`)
  → reencode → verifica. Descarte de take, corte de silêncio e normalização no MESMO
  reencode. Aceita arquivo ou pasta (lote); `--descartar` vale só pra arquivo único. Por
  padrão preserva specs; com `--normalizar` padroniza no mesmo passo (a normalização migrou
  do combinador pra cá — fundir tudo num só reencode evita gerações extras). O nome de saída
  é limpo via `nome_saida_base()`: **preserva toda a identificação** (tipo, código, prefixo,
  número, na ordem original) e descarta SÓ tokens de ruído de processo (BRUTA, VERTICAL,
  HORIZONTAL, RAW, FINAL, OTIMIZADO) + `_OTIMIZADO`. Ex.: `DME_VAV23_VERTICAL_BRUTA_DESENVOLVIMENTO`
  → `DME_VAV23_DESENVOLVIMENTO_OTIMIZADO` (o tipo nunca se perde). Separadores repetidos viram
  underscore único. O lote pula qualquer arquivo com `OTIMIZADO` no nome; o combinador lê o
  código mesmo assim (trata `OTIMIZADO` como ruído).
- `quadrado.py` — gera a variante quadrada (1:1) de cada `_OTIMIZADO`: recorta um quadrado de
  largura cheia (`crop=W:W:0:y`, descarta só altura) e salva `_QUADRADO` ao lado. A âncora
  vertical `y` é decidida por detecção de rosto YuNet (modelo `.onnx` versionado em
  `referencia/modelos/`, olhos a ~30% da altura, mediana de alguns frames), com fallback de
  âncora alta quando não detecta rosto; `--ancora` faz nudge manual e `--contato` gera folha
  de contato pra conferência. Áudio `-c:a copy`, vídeo reencodado no codec da origem. O
  `bootstrap.py` instala `opencv-python-headless` na venv central pra isso.

Em `skills/invisible-legenda-arquivos/scripts/`:

- `bootstrap.py` — **cópia** da do desmembrador (cada skill autocontida).
- `legendar.py` — extrai áudio mono 16k com ffmpeg e roda WhisperX UMA vez por vídeo
  (`--output_format json`), depois move o `.json` pro lado do vídeo, renomeado pro nome da
  origem. Regra de saída FIXA: `<pasta>/CORTE.mp4` → `<pasta>/CORTE.json` (mesmo nome, mesma
  pasta, ao lado do original — sem pasta de saída separada). Aceita arquivo único ou pasta
  (lote, vídeos diretos sem recursão); resumível (pula o que já tem o `.json`, `--forcar`
  refaz). Não recodifica nem toca no vídeo — só transcreve. Imprime relatório JSON; progresso
  no stderr. O `.json` traz `segments[].words[]` (start/end por palavra) — é o que o Remotion
  consome pra legenda animada. **Só JSON:** o `.srt` foi descartado (v2.0.0) — o pipeline só
  usa o timestamp por palavra, que só o JSON carrega; gerar SRT era peso morto. Sem `--formatos`.
  Se há um sidecar de roteiro `<video>.md` ao lado, depois de gerar o `.json` chama
  `marcar_secoes.py` pra taggear cada palavra com a `secao` (e injetar o bloco `secoes`).
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
- `aplicar.py` — orquestra por vídeo: localiza o `.json` irmão (sem ele, para e avisa —
  **não transcreve**), converte → encena `public/video.mp4` + `public/captions.json` no
  central → `npx remotion render <estilo>` → `LEGENDADOS/<nome>_LEGENDADO.mp4`. Aceita arquivo
  ou pasta (lote, ignora a própria `LEGENDADOS`). Detecta o formato pela dimensão real do
  vídeo (ffprobe): `--estilo` é opcional e o default sai por formato (quadrado→`classic`,
  vertical→`reels`); no quadrado a posição vertical da legenda usa o `bottomOffsetSquare` do
  preset (Remotion lê width/height reais via `calculateMetadata`).
- `remotion/` — template do render (fontes só; `node_modules` vive no central, não no repo).
  `src/Captions.tsx` guarda os `PRESETS` (ritmo, fonte, cor, posição, modo de destaque) e a
  correção de quebra de linha que impede o texto de vazar a margem (**não reverter** — espaço
  fora do `inline-block`). `Root.tsx` adapta duração/dimensão por vídeo via `parseMedia`. O
  preset `hormozi` existe mas está EXPERIMENTAL (em ajuste — não oferecer como pronto).

Em `skills/invisible-video-var-gancho-escrito/scripts/` (+ `remotion/`):

- `bootstrap.py` — Remotion/Node (como o do aplicador, projeto central próprio
  `~/.invisible-video/gancho-escrito-remotion`). Sincroniza os fontes; `npm install` só na 1ª vez.
- `preparar.py` — do `.json` da combinação (com `secoes`/`secao`) gera `public/hook.json`
  (frases do gancho + `emphasis` + `boundaryMs`) e `captions.json` (só desenvolvimento); copia
  o vídeo base p/ `public/video.mp4`. O número `VAR<n>` NÃO entra aqui — só no nome da saída.
- `aplicar.py` — orquestra: detecta o modo por vídeo (legendado vs crua), resolve o `.json`,
  puxa a ênfase por gancho (`--enfase-map`), render em lanes paralelas. **`--var <n>`** estampa
  a variação no nome (`_LEGENDADO_VAR<n>.mp4`, default `1`); o número é do usuário, não da skill.
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
  trilhas medidas uma vez (cache). Saída `99_FINALIZADOS/<nome>_FINALIZADO.mp4`. O método (por
  que LUFS, calibração do -37) está em `referencia/METODO.md`.

Em `skills/invisible-denoiser/scripts/`:

- `bootstrap.py` — **só ffmpeg/ffprobe** (igual ao da trilha; `afftdn` é embutido). Sem Node,
  sem WhisperX, sem modelo.
- `denoiser.py` — ffmpeg puro: `afftdn=nr=<6|12|21>` no áudio, `-c:v copy` no vídeo. **In-place**
  (temp → `<nome>_DENOISER.ext`, remove o original). Arquivo único ou pasta (pula `_DENOISER`).
  Recusa alvo em `BRUTAS/` sem `--forcar`. Sem EQ/compressão (reprovados). Método em
  `referencia/METODO.md`.

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
