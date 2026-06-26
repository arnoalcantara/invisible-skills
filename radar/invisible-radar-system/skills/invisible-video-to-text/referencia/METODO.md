# Método — invisible-video-to-text

Notas de método e as decisões que orientam a skill. Não é lido em runtime; é
documentação para quem evolui a skill.

## Por que duas leituras (fala + texto na tela)

Um vídeo de referência carrega duas informações distintas, e jogar fora qualquer
uma empobrece o material:

- **A fala** é o conteúdo — a tese, o mecanismo, os pilares. Quem só transcreve
  isso perde o enquadramento.
- **O texto na tela** é o contexto. No Instagram, a **caixinha de pergunta** é
  literalmente o gatilho do vídeo: a dor de uma seguidora que a pessoa responde.
  Sem a caixinha, a fala fica solta ("ele respondendo o quê?"). A **legenda
  queimada** costuma definir o público ("Aprendam, esposas").

Para a skill de copy, isso vira ouro: a caixinha dá a **dor dominante** e o
**público**; a fala dá o **conteúdo**. O carrossel nasce do par.

## Por que o AGENTE lê os frames, e não OCR

Testado à mão na sessão que originou a skill: pedir ao modelo com visão para ler
os frames superou OCR em tudo que importa.

- **OCR (Tesseract/cv2)** lê caracteres, mas não entende **layout**: não separa a
  caixinha do título da legenda, erra em fonte estilizada/sobreposta a imagem, e
  não lê **contexto de cenário** (um crucifixo ao fundo, um ambiente profissional).
- **O agente com visão** entende que aquilo é uma caixinha de pergunta do
  Instagram (com título = handle + corpo = pergunta), distingue a legenda
  queimada, lê o título do YouTube, e ainda capta o cenário relevante para a voz.

Por isso o `extrair_frames.py` só **extrai** os frames; a interpretação é do
agente. O OCR ficaria como muleta que o agente teria que revisar de qualquer
jeito — então não vale a dependência.

## Amostragem de frames: densa no início, esparsa no resto

O texto que mais importa (caixinha, título) aparece **cedo** e costuma ficar
**fixo**. Então `extrair_frames.py` amostra denso nos primeiros segundos
(0,1,2,3,5,8s) e esparso no resto (alguns pontos distribuídos até o fim). Isso
pega o texto inicial **e** flagra legendas que mudam no meio/fim, sem extrair
dezenas de frames à toa. Default: até 10 frames.

## Transcrição: só texto, --no_align

A skill usa WhisperX com `--no_align`: aqui não há legenda de vídeo para
sincronizar, então **timestamp por palavra é desnecessário**. `--no_align` é mais
rápido e dispensa o modelo de alinhamento. (Contraste com a esteira de vídeo, que
precisa do timestamp por palavra para legenda karaokê — lá o align é obrigatório.)

A limpeza do texto (corrigir erros de reconhecimento) é do **agente**, não do
script: o script entrega a transcrição crua; o agente corrige preservando sentido
e tom. WhisperX erra em fala coloquial, palavrão, nomes próprios — e o julgamento
do que é erro vs. estilo é editorial, não mecânico.

## Ambiente central, não por projeto

WhisperX (torch + numpy) é pesado; yt-dlp é melhor isolado. Tudo vai num venv
central único (`~/.invisible-radar/venv`), reusado por qualquer skill do radar.
O `bootstrap.py` resolve, em ordem: PATH do sistema → venv central → instala.
Se já houver um WhisperX de outra skill Invisible (`~/.invisible-video/wxenv`), o
`transcrever.py` o reaproveita — não duplica os GB.

## Entregável: um arquivo só

O material vai num **único** `material-<slug>.md` rotulado. A tentação de separar
em "transcrição.md" + "texto-na-tela.md" foi testada e descartada na sessão de
origem: força a skill de copy a abrir dois arquivos e adivinhar a relação entre
eles. Um arquivo auto-explicativo, com blocos rotulados (texto na tela = gatilho;
fala = conteúdo; notas = relação), é o contrato limpo com a skill de copy.

## Generalização: vídeo, não "reels"

A skill nasceu de um reels do Instagram, mas o processo é genérico: **vídeo →
texto**. yt-dlp baixa IG, TikTok e YouTube; a leitura de frames se adapta ao
layout de cada plataforma (caixinha no IG, título no YouTube, stickers no TikTok).
Por isso o nome é `invisible-video-to-text`, não "reels".
