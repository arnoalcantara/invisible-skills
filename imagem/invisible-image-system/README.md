# invisible-image

Agente de geração de imagem cinematográfica da Invisible.

## O que faz

Recebe qualquer pedido (uma frase, uma palavra, uma imagem de referência) e entrega uma imagem renderizada via Higgsfield CLI. Opera como Diretor de Fotografia: decide câmera, lente, luz, post e grão de filme sozinho. Não explica. Não pergunta sobre estética. Entrega.

Pergunta apenas o que é tecnicamente necessário: aspect ratio e resolução (se não estiverem claros no pedido).

## Como invocar

```
/invisible-image
```

## Motor

Higgsfield CLI + modelo Nano Banana 2, via script Python local.

## Câmeras

- **IMAX MK IV 65mm** — contemplativo, retratos densos, escala, rituais.
- **ARRI Alexa 35** — narrativo, urbano, noturno, dinâmico. (default)

## Formato de prompt

Nano Banana 2 — parágrafos em inglês com headers em CAPS (`CAMERA:`, `LENS:`, `LIGHT:`...). Sem markdown, sem buzzwords, sem citação de diretores. Máximo 1.500 caracteres.
