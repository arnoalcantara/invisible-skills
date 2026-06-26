# CLAUDE.md — plugin `invisible-radar`

Instruções para qualquer instância de Claude que trabalhe neste plugin. Leia antes de editar.

## O que é

Radar de referências da Invisible: skills que **coletam** material de referência de fontes públicas (vídeos, anúncios, virais) e o preparam para estudo e criação de copy. É a ponta de **coleta** da esteira — o material que estas skills produzem alimenta as skills de **copy** (ex.: `invisible-copy` / `invisible-carrossel`).

Skills atuais:
- **`invisible-video-to-text`** — vídeo (link IG/TikTok/YouTube ou arquivo) → `material.md` unificado (fala transcrita + texto na tela).

## Arquitetura

- **Skill fina, lógica nos scripts.** O `SKILL.md` orquestra e conduz o usuário; os `scripts/*.py` fazem o trabalho pesado (baixar, transcrever, extrair frames). Cada script imprime **JSON** e para.
- **A interpretação visual é do AGENTE, não de script.** A leitura do texto na tela (caixinha, título, legenda) é feita pelo agente lendo os frames — não por OCR. O script só extrai os frames. (Ver `referencia/METODO.md`.)
- **Ambiente central, não por projeto.** As dependências pesadas (WhisperX, yt-dlp) vivem num venv central único `~/.invisible-radar/venv`, montado pelo `bootstrap.py`, reusado por todas as skills do radar. Se já houver um WhisperX de outra skill Invisible (`~/.invisible-video/wxenv`), as skills o reaproveitam.

## Relação com o "Radar de Referências" local (MCPs em TypeScript)

Existe, fora do repo, um projeto `Radar de Referências` (em `04_Playground/`) com MCPs em TS que fazem coleta **em massa** (Meta Ad Library, virais por produtor). Este plugin **não depende** dele: as skills aqui são autocontidas (Python + CLI), instaláveis via marketplace, para o caso **pontual** (1 vídeo → material). Os dois coexistem; o TS é para volume, a skill é para o caso unitário.

## Os scripts (invisible-video-to-text)

- `bootstrap.py` — detecta/instala ffmpeg, yt-dlp, WhisperX; monta o venv central; imprime JSON com `pronto`, `yt_dlp_bin`, `whisperx_bin`.
- `baixar.py` — yt-dlp: link → `<slug>.mp4` (IG tenta cookies do Chrome/Safari; TikTok/YouTube direto).
- `transcrever.py` — ffmpeg extrai áudio + WhisperX (pt, `--no_align`, só texto) → `.txt`.
- `extrair_frames.py` — ffmpeg extrai frames (densos no início, esparsos no resto) para o agente ler.

## Convenções

- **Idioma:** PT-BR no conteúdo; código e nomes de script em português (snake_case).
- **Prefixo:** toda skill com `invisible-` no `name` do frontmatter.
- **Saídas do usuário** (vídeo, material.md) ficam na pasta de trabalho do usuário, **não versionadas** no repo.
- **Scripts:** Python stdlib + ferramentas CLI (ffmpeg, yt-dlp, whisperx). `from __future__ import annotations` no topo se usar anotações PEP 604 (o python3 do sistema pode ser < 3.10).

## Versionamento (semver)

A versão vive em `.claude-plugin/plugin.json`. Bump a cada mudança que vai para a main: **patch** (correção), **minor** (skill/recurso novo), **major** (quebra). Esquecer o bump deixa os instaladores presos na versão antiga.

## Fluxo de trabalho (Git)

Nunca direto na `main`. Worktree + branch → testar local → aprovar → merge. Push só quando o usuário pedir. Ao adicionar o plugin/skill, registrar no `.claude-plugin/marketplace.json` da raiz do repo.
