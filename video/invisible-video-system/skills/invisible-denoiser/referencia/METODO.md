# Método — invisible-denoiser

## O que foi testado (Lote 01 Gurgel, jun/2026)

Material: `DME__VAV19__VERTICAL__BRUTA.mp4`. Perfil medido: piso de ruído **−54 dB** (limpo), **−17.9 LUFS**, true peak **−0.3 dBFS**.

A hipótese inicial era uma cadeia de "voz de podcast": highpass → denoise → gate → EQ de corpo/presença → compressão → loudness. Testada em modos "leve" e "forte" e **reprovada de ouvido pelo Arno**: em gravação já limpa, EQ + compressão deixam a voz "forte, aberta", artificial. Ele preferiu o original.

**Conclusão:** material limpo não pede tratamento pesado. O único elemento que agregou foi o **denoise**. A skill encolheu pra isso.

## O que ficou

- Filtro **`afftdn`** (FFT denoiser embutido no ffmpeg, sem dependência externa).
- Níveis por `nr` (redução em dB): leve=6, medio=12, **forte=21 (padrão)**.
- Em fonte limpa a diferença entre níveis é pequena; forte foi o default escolhido.
- `arnndn` (denoise neural, exige modelo `.rnnn`) ficou **fora** — a gravação do Gurgel é limpa e o `afftdn` resolveu. Reavaliar só se aparecer material com ruído de fundo pesado (ventilador, rua, sala).

## Decisões de comportamento (Arno)

- **In-place, mesmo nome.** Processa num temp e substitui o original no mesmo nome (`os.replace(tmp, arquivo)`). Sem sufixo, sem marca: o limpo ocupa o lugar do antigo, o nome de quem vem da esteira fica intacto. Consequência aceita: sem marca, não há idempotência por nome — rodar de novo reaplica o filtro (decisão do Arno: a skill faz o serviço e só avisa no fim, não muda o nome).
- **Independente.** Roda em qualquer ponto da esteira, não numa posição fixa.
- `-c:v copy`: vídeo intocado, só o áudio é reprocessado.
- Recusa rodar nas `BRUTAS/` sem `--forcar` (fonte de verdade).

## Fronteira com o resto da esteira

- **Loudness / nivelamento de volume** não é aqui — o degrau de volume entre trechos de uma combinação é resolvido no `invisible-video-combinador` (nivelamento por atenuação), e a loudness final (−14 LUFS) é da `invisible-trilha-aplicador`.
- **Timbre** (EQ, compressão) — fora de escopo por decisão validada.
