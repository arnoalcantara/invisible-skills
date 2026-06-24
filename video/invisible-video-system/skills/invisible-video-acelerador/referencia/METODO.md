# Método — invisible-video-acelerador

## Problema

Acelerar um vídeo parece trivial, mas tem duas armadilhas:

1. **O áudio.** Acelerar o áudio mexendo no sample rate (o jeito ingênuo) sobe o
   tom junto — a voz vira desenho animado. Errado para talking-head.
2. **O fps.** `setpts` re-cronometra os frames. Se você não fixa o fps de saída,
   a taxa efetiva sobe (30fps a 2x viram ~60fps VFR), inflando o arquivo e
   confundindo players.

## Solução

### Vídeo: `setpts=PTS/FATOR` + `-r <fps_da_fonte>`

`setpts=PTS/FATOR` divide os timestamps de apresentação pelo fator — o vídeo
toca mais rápido. Forçando a saída no **mesmo fps da fonte** (`-r`, lido por
ffprobe `avg_frame_rate`), o ffmpeg descarta frames uniformemente para caber na
duração menor. Resultado: vídeo mais curto, fluido, no fps de sempre.

Acelerar **exige reencode** (não dá `-c:v copy`: os frames mudam de timestamp e
muitos são descartados). Reencodamos em H.264 yuv420p, CRF 18 (qualidade alta,
visualmente transparente), preset `medium`. H.264 é o que o resto da esteira
usa (otimizador, finalizados) — saída consistente e compatível com social.

### Áudio: `atempo=FATOR`

`atempo` muda só o andamento, **preservando o tom** da voz. Range válido por
filtro: `[0.5, 2.0]`. Os três fatores oferecidos (1.2, 1.5, 2.0) cabem todos —
um único `atempo` resolve, sem encadear. (Para fatores >2x seria preciso
encadear: `atempo=2.0,atempo=1.5` etc. — fora do escopo desta skill.)

Vídeo sem trilha de áudio: o script detecta (ffprobe) e sai com `-an`.

## Decisões travadas

- **Três fatores só: 1.2 / 1.5 / 2.** Cobrem o uso real (encurtar um pouco,
  bastante, ou pela metade) e cabem num só `atempo`. Sem default — o usuário
  escolhe a cada execução.
- **Grava ao lado, original intacto.** Diferente do denoiser (que é in-place e
  remove o original), aqui o original fica: você quer comparar o ritmo e talvez
  manter as duas velocidades.
- **Fator no nome** (`_ACELERADO_12X/15X/2X`). Acelerar o mesmo arquivo em
  fatores diferentes não pode colidir.
- **Sufixo composto** (`_ACELERADO_<FATOR>`, não só `_<FATOR>`): marca a etapa e
  o parâmetro, legível na esteira.

## Verificação

- Duração da saída ≈ duração da fonte ÷ fator (2x → metade).
- fps da saída == fps da fonte.
- Áudio presente, em sincronia, sem alteração de tom (ouvido).
