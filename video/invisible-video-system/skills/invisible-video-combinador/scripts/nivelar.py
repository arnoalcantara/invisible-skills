#!/usr/bin/env python3
"""nivelar.py — casa a loudness dos cortes de UMA cadeia, por atenuação pura.

Ao concatenar cortes de origens diferentes (gancho de um vídeo, desenvolvimento
de outro), cada um foi gravado num nível distinto → degrau de volume audível na
emenda. Este passo iguala os trechos ENTRE SI antes do concat.

Método validado (Lote 01 Gurgel, jun/2026):
- Nivela PRA BAIXO: alvo = o corte mais baixo da cadeia. Só atenua, nunca aplica
  ganho positivo. Subir trecho baixo clipa/esmaga (alguns têm true peak já no
  limite, ex. +2.1 dBTP); descer é sempre seguro e preserva a dinâmica (nada de
  compressão — decisão de projeto).
- A loudness final absoluta (-14 LUFS) NÃO é tratada aqui; fica para a
  invisible-trilha-aplicador, no fim da esteira. Aqui só removemos o degrau.
- Mede o LUFS DEPOIS de os cortes estarem no formato comum (o normalizar.py já
  põe tudo em 48k estéreo); medir antes, em sample rates/canais diferentes,
  desloca o nível casado.

Vídeo é copiado (-c:v copy); só o áudio é reescrito com o ganho. As specs não
mudam, então o `combinar.py` segue concatenando por -c copy.

Uso:
    python3 nivelar.py <corte1> <corte2> [<corteN> ...] --out-dir <tmp>
Saída (stdout): JSON {"piso_lufs": x, "cortes": [{entrada, saida, lufs, ganho_db}]}
"""
import argparse
import json
import os
import re
import subprocess
import sys


def medir_lufs(video):
    """Integrated loudness (LUFS) via loudnorm em modo análise (1 passada)."""
    cmd = ["ffmpeg", "-hide_banner", "-nostats", "-i", video,
           "-af", "loudnorm=I=-14:TP=-1.5:print_format=json", "-f", "null", "-"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    txt = proc.stderr + proc.stdout
    m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", txt, re.S)
    if not m:
        raise RuntimeError(f"não consegui medir LUFS de {video}")
    return float(json.loads(m.group(0))["input_i"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cortes", nargs="+", help="cortes da cadeia (já normalizados)")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--aac-bitrate", default="192k")
    args = ap.parse_args()

    cortes = [os.path.abspath(c) for c in args.cortes]
    for c in cortes:
        if not os.path.isfile(c):
            print(json.dumps({"erro": f"corte não existe: {c}"}))
            sys.exit(1)
    os.makedirs(os.path.abspath(args.out_dir), exist_ok=True)

    try:
        medidas = [(c, medir_lufs(c)) for c in cortes]
    except RuntimeError as e:
        print(json.dumps({"erro": str(e)}, ensure_ascii=False))
        sys.exit(1)

    piso = min(l for _, l in medidas)  # o mais baixo da cadeia

    resultados = []
    for c, lufs in medidas:
        ganho = round(piso - lufs, 1)  # <= 0 (atenuação)
        nome = os.path.splitext(os.path.basename(c))[0]
        ext = os.path.splitext(c)[1] or ".mp4"
        saida = os.path.join(os.path.abspath(args.out_dir), f"{nome}_niv{ext}")
        cmd = ["ffmpeg", "-y", "-i", c, "-c:v", "copy",
               "-af", f"volume={ganho}dB",
               "-c:a", "aac", "-ar", "48000", "-ac", "2", "-b:a", args.aac_bitrate,
               saida]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            print(json.dumps({"erro": "ffmpeg falhou ao nivelar",
                              "corte": c, "stderr": proc.stderr[-1200:]},
                             ensure_ascii=False))
            sys.exit(1)
        resultados.append({"entrada": c, "saida": saida,
                           "lufs": round(lufs, 1), "ganho_db": ganho})

    print(json.dumps({"piso_lufs": round(piso, 1), "cortes": resultados},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
