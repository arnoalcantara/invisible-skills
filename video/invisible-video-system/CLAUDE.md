# CLAUDE.md — plugin `invisible-video-system`

Orienta qualquer instância de Claude que trabalhe neste plugin. Leia antes de editar.

## O que é

O sistema de vídeo da Invisible. Três skills, encadeáveis na mesma pasta de projeto:

- **`invisible-video-bruto-desmembrador`** — corta brutos em um vídeo por seção do roteiro.
- **`invisible-video-combinador`** — cruza ganchos × desenvolvimentos por encaixe retórico
  e gera anúncios combinados (consome as saídas do desmembrador).
- **`invisible-video-otimizador`** — escolhe a melhor take quando há várias tentativas
  da mesma fala (transcrição WhisperX, última take vence), remove silêncios internos sem
  comer palavra e, opcionalmente, normaliza o formato no mesmo reencode (corte pronto pra
  concatenar).

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
- `normalizar.py` — normaliza um corte para o alvo (`scale+pad+setsar=1` + fps + aformat).
  **Rede de segurança:** o ideal é os cortes já chegarem normalizados da otimizadora;
  este script só entra quando algum corte ainda tem specs divergentes do alvo.
- `combinar.py` — concat `-c copy` de gancho+desenvolvimento já normalizados.

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

**Por que cópias e não scripts compartilhados:** decisão de manter cada skill autocontida.
Ao corrigir um bug em `bootstrap.py`/`transcrever.py`, replicar nas três cópias (agora as
três têm `transcrever.py`).

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
