# Método — Aplicador de Trilha com normalização de loudness

Documenta o porquê das escolhas. Os números foram calibrados numa sessão real (lote VAV19
do Laboratório de Skills de Vídeo e Edição: 24 vídeos legendados + 8 trilhas).

## Por que LUFS e não porcentagem

Volume de trilha controlado em "%" é ganho **relativo**: `volume=0.08` multiplica o sinal
existente. Mas cada trilha vem masterizada num nível diferente. Medição real das 8 trilhas
do acervo (loudness integrado, `ebur128`):

```
-7.3 LUFS   Captain Joz - Stunts Cheer      (mais alta)
-9.2 LUFS   Ariel Shalom - Dream Loop
-11.0 LUFS  Lalinea - WALAKATA
-11.6 LUFS  Aves - Joy Ride
-14.9 LUFS  Damon Power - Grief
-15.1 LUFS  Roie Shpigler - Daydreaming
-15.6 LUFS  Tommy H Brandon - Landscapes from a Train
-16.3 LUFS  idokay - I Was All Alone         (mais baixa)
```

~9 dB entre a mais alta e a mais baixa — quase o dobro de volume percebido. "8% de volume"
aplicado em todas soaria alto na Stunts Cheer e sumido na I Was All Alone.

**Loudness (LUFS) é absoluto.** Normalizando cada trilha para o mesmo alvo em LUFS, todas
entram com a mesma presença, independentemente de como foram masterizadas. Prova: levando a
trilha mais alta (-7.3) e a mais baixa (-16.3) ao mesmo -37 LUFS, recebem ganhos bem
diferentes (-29.7 dB vs -20.7 dB) mas soam igualmente presentes ao fundo.

## Os dois alvos

- **Fala → -14 LUFS.** Padrão de loudness de Reels/social. A fala dos 24 vídeos variava de
  -17.1 a -13.3 LUFS (~3.8 dB); normalizada, todos os finais bateram -14.x LUFS.
- **Trilha → -37 LUFS.** Calibrado de ouvido. Equivale a ~23 dB abaixo da fala — fundo
  presente sem competir com a voz. O ponto de partida foi "8% da Daydreaming" (que está em
  -15.1 LUFS): `-15.1 + 20·log10(0.08) = -15.1 - 21.9 ≈ -37 LUFS`. Daí o alvo virou
  absoluto e consistente.

Controle final é **um número**: `--alvo-trilha`. Sobe para -34 (mais presente), desce para
-40 (mais discreta).

## Ganho linear, não compressão

A normalização da fala usa `volume=NdB` (ganho linear: levanta/abaixa o nível inteiro),
**não** `loudnorm`/compressor. Ganho linear preserva a dinâmica natural da voz. Loudness
agressivo comprime e deixa a fala com som "processado". Para voz de professor, ganho linear
é mais natural e previsível.

## A mixagem

```
[0:a]volume=<g_fala>dB[fala];
[1:a]volume=<g_trilha>dB,afade=t=in:st=0:d=1.5,afade=t=out:st=<dur-1.5>:d=1.5[bg];
[fala][bg]amix=inputs=2:duration=first:normalize=0[aout]
```

- `normalize=0` é **essencial**: o default do `amix` divide cada entrada por N (com 2
  entradas, corta a fala pela metade). Com `normalize=0`, cada camada mantém o ganho que
  definimos.
- `-stream_loop -1` no input da trilha: a trilha loopa para cobrir vídeos mais longos que
  ela (no acervo, a Joy Ride tem 24s e vídeos chegam a 66s). `duration=first` corta no fim
  do vídeo.
- `afade` in/out de 1.5s: a trilha não entra nem corta seco.
- `-c:v copy`: vídeo sem recompressão (zero perda de imagem, rápido). Só o áudio é
  reprocessado (AAC 192k).

## Distribuição das trilhas no lote

Round-robin sobre a lista ordenada de trilhas: vídeo `i` recebe trilha `i % M`. Com 24
vídeos e 8 trilhas, cada trilha entra exatamente 3 vezes. Como vídeos "irmãos" (base e
variação do mesmo par) ficam adjacentes na ordenação, recebem trilhas diferentes.

## Validação (teste de aceitação)

Lote VAV19: 24/24 gerados, cada trilha usada 3×, loudness final -14.1 a -14.3 LUFS em
todas as amostras conferidas, vídeo h264 intacto (`-c:v copy`), áudio AAC estéreo.
