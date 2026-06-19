# CLAUDE.md — plugin `invisible-video-system`

Orienta qualquer instância de Claude que trabalhe neste plugin. Leia antes de editar.

## O que é

O sistema de vídeo da Invisible. Hoje tem uma skill: **`invisible-video-bruto-desmembrador`**,
que corta vídeos brutos em um vídeo por seção do roteiro. O nome do plugin é genérico
de propósito — é onde futuras skills de vídeo entram (legendagem, montagem, export).

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
