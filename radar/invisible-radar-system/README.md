# invisible-radar

Radar de referências da **Invisible**. Skills que coletam material de referência de fontes públicas e o preparam para estudo e criação de copy. É a ponta de **coleta** da esteira: o material gerado aqui alimenta as skills de copy (`invisible-copy` / `invisible-carrossel`).

---

## Skills

### `invisible-video-to-text`

Transforma um vídeo num **material de trabalho** unificado para copy. Faz duas leituras complementares:

- **Transcreve a fala** (WhisperX, pt) — o conteúdo: tese, mecanismo, pilares.
- **Lê o texto na tela** — a caixinha de pergunta do Instagram, a legenda queimada, o título do YouTube — interpretando frames com **visão** (não OCR). É o contexto: a dor, o gatilho, o público.

Junta tudo num só `material-<slug>.md`, com blocos rotulados:

```
material-<slug>.md
├── 1. TEXTO NA TELA   → o gatilho/contexto (caixinha, legenda, título)
├── 2. FALA TRANSCRITA → o conteúdo (tese, mecanismo)
└── 3. NOTAS DE CONTEXTO → relação entre eles, cenário, voz≠ideia
```

**Fontes:** Instagram, TikTok, YouTube (via yt-dlp) ou um arquivo de vídeo local.

**Uso:** "transcreve esse vídeo", "baixa esse reels e vira material pra carrossel", "pega esse vídeo do YouTube e me dá o material".

---

## Como funciona (visão geral)

```
link (IG/TikTok/YouTube) ou arquivo
        │
        ▼
   [bootstrap]  ffmpeg · yt-dlp · whisperx (venv central ~/.invisible-radar/)
        │
        ▼
   [baixar]     yt-dlp → <slug>.mp4
        │
        ├──────────────┐
        ▼              ▼
   [transcrever]   [extrair_frames]
   fala (pt)       frames densos no início
        │              │
        │              ▼
        │         AGENTE lê o texto na tela (visão)
        ▼              │
        └──────┬───────┘
               ▼
        material-<slug>.md  (unificado, rotulado)
               │
               ▼
        alimenta invisible-carrossel / invisible-copy
```

A skill é fina: orquestra e conduz; a lógica está nos `scripts/*.py`. A leitura visual é do **agente**, não de OCR.

---

## Estrutura

```
radar/invisible-radar-system/
├── .claude-plugin/plugin.json
├── CLAUDE.md
├── README.md
└── skills/
    └── invisible-video-to-text/
        ├── SKILL.md
        ├── scripts/
        │   ├── bootstrap.py        # ffmpeg + yt-dlp + whisperx, venv central
        │   ├── baixar.py           # yt-dlp: link → mp4
        │   ├── transcrever.py      # ffmpeg + whisperx (pt, só texto)
        │   └── extrair_frames.py   # ffmpeg: frames p/ o agente ler
        └── referencia/
            └── METODO.md           # por que visão e não OCR; amostragem de frames
```

---

## Dependências

- **ffmpeg / ffprobe** (Homebrew)
- **yt-dlp** (instalado no venv central pelo bootstrap, ou do sistema)
- **WhisperX** (venv central `~/.invisible-radar/venv`, ou reaproveita `~/.invisible-video/wxenv` se já existir)

O `bootstrap.py` monta tudo de forma idempotente. O modelo de transcrição (~1.5GB) é baixado pelo WhisperX na 1ª transcrição, se não estiver em cache.

---

## Instalação (plugin do Claude Code)

```bash
/plugin marketplace add arnoalcantara/skills
/plugin install invisible-radar@arno-skills
```

As saídas (vídeo, `material.md`) vão para a pasta onde você roda o Claude — não são versionadas.
