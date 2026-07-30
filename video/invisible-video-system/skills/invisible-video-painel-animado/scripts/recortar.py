#!/usr/bin/env python3
"""Recorta o fundo de um personagem gerado no GPT Image -> alpha real.

O GPT Image 2 NÃO entrega transparência no download (vem RGB opaco, fundo branco),
mesmo que o preview do Artlist mostre xadrez. Este script roda o rembg (u2net) e
devolve um PNG RGBA com fundo removido. Roda na venv rembg do bootstrap.

Uso:
    <rembgenv>/bin/python recortar.py entrada.png saida_ALPHA.png

Valida o alpha e imprime um JSON com o resultado (mode, alpha extrema, bbox).
Sai !=0 se o alpha não ficou transparente (fundo não removido).
"""
import json
import sys


def main():
    if len(sys.argv) < 3:
        sys.stderr.write("uso: recortar.py entrada.png saida_ALPHA.png\n")
        return 2
    entrada, saida = sys.argv[1], sys.argv[2]
    try:
        from rembg import remove
        from PIL import Image
    except ImportError as e:
        sys.stderr.write(f"Dependência ausente ({e}). Rode o bootstrap para criar a venv rembg.\n")
        return 3

    im = Image.open(entrada)
    res = remove(im)  # RGBA com fundo removido
    if res.mode != "RGBA":
        res = res.convert("RGBA")
    res.save(saida)

    a = res.getchannel("A")
    mn, mx = a.getextrema()
    rel = {
        "saida": saida,
        "mode": res.mode,
        "alpha_min": mn,
        "alpha_max": mx,
        "transparente": mn == 0,
        "bbox": res.getbbox(),
    }
    print(json.dumps(rel, ensure_ascii=False))
    return 0 if mn == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
