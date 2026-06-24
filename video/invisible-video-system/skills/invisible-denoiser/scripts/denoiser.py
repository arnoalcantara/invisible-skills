#!/usr/bin/env python3
"""denoiser.py — reduz ruído do áudio com afftdn, IN-PLACE.

Não gera arquivo novo nem muda o nome: processa e **substitui o original no mesmo
nome**. O vídeo é copiado sem recompressão (`-c:v copy`); só o áudio é reprocessado.
Aceita um arquivo único OU uma pasta inteira (lote).

Como o nome não muda, NÃO há marca de "já tratado": rodar de novo aplica o denoiser
outra vez sobre o já-limpo (em fonte limpa o efeito de uma 2ª passada é pequeno, mas
não é à toa). Rode uma vez por arquivo; é o chamador que controla a ordem.

Níveis (nr = redução de ruído em dB do afftdn):
    leve = 6, medio = 12, forte = 21 (padrão, validado de ouvido no Lote 01).

Em gravação já limpa a diferença entre níveis é pequena. Tratamento de timbre
(EQ, compressão) NÃO entra aqui — foi testado e reprovado: em fonte limpa soa
artificial. Esta skill só limpa ruído, sem mexer em timbre nem dinâmica.

NÃO rodar nas BRUTAS (fonte de verdade, irreproduzível): como substitui o
original, a skill recusa por padrão quando o alvo está numa pasta BRUTAS. Use
--forcar se for intencional (e você tiver cópia).

Uso:
    python3 denoiser.py <arquivo|pasta> [--nivel forte|medio|leve] [--nr N] [--forcar]
Saída (stdout): JSON {"nr": N, "saidas": [...]} ou {"erro": ...}
"""
import argparse
import json
import os
import subprocess
import sys

VIDEO_EXT = {".mp4", ".mov", ".mkv", ".m4v", ".webm"}
AUDIO_EXT = {".wav", ".m4a", ".aac", ".mp3", ".flac", ".ogg"}
NIVEIS = {"leve": 6, "medio": 12, "forte": 21}


def coletar(caminho):
    """Um arquivo → [arquivo]. Uma pasta → toda a mídia da pasta."""
    if os.path.isfile(caminho):
        return [os.path.abspath(caminho)]
    alvos = []
    for entry in sorted(os.listdir(caminho)):
        p = os.path.join(caminho, entry)
        ext = os.path.splitext(entry)[1].lower()
        if (os.path.isfile(p) and not entry.startswith(".")
                and (ext in VIDEO_EXT or ext in AUDIO_EXT)):
            alvos.append(os.path.abspath(p))
    return alvos


def em_brutas(arquivo):
    partes = [p.upper() for p in os.path.abspath(arquivo).split(os.sep)]
    return "BRUTAS" in partes


def denoise_um(arquivo, nr, bitrate):
    raiz, ext = os.path.splitext(arquivo)
    ext_l = ext.lower()
    tmp = f"{raiz}.denoiser_tmp{ext}"
    af = f"afftdn=nr={nr}"
    if ext_l in VIDEO_EXT:
        cmd = ["ffmpeg", "-y", "-i", arquivo, "-af", af,
               "-c:v", "copy", "-c:a", "aac", "-b:a", bitrate, tmp]
    else:
        cmd = ["ffmpeg", "-y", "-i", arquivo, "-af", af, tmp]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise RuntimeError(proc.stderr[-1200:])
    os.replace(tmp, arquivo)        # temp → mesmo nome: o original vira a versão limpa
    return arquivo


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("entrada", help="arquivo de mídia OU pasta (lote)")
    ap.add_argument("--nivel", choices=list(NIVEIS), default="forte")
    ap.add_argument("--nr", type=int, help="redução em dB (sobrepõe --nivel)")
    ap.add_argument("--aac-bitrate", default="192k")
    ap.add_argument("--forcar", action="store_true",
                    help="permite rodar em BRUTAS (substitui a fonte de verdade)")
    args = ap.parse_args()

    if not os.path.exists(args.entrada):
        print(json.dumps({"erro": f"não existe: {args.entrada}"}, ensure_ascii=False))
        sys.exit(1)

    nr = args.nr if args.nr is not None else NIVEIS[args.nivel]
    alvos = coletar(args.entrada)
    if not alvos:
        print(json.dumps({"erro": "nenhuma mídia encontrada"}, ensure_ascii=False))
        sys.exit(1)

    if not args.forcar:
        protegidos = [a for a in alvos if em_brutas(a)]
        if protegidos:
            print(json.dumps({
                "erro": "alvo em BRUTAS (fonte de verdade). Use --forcar se for intencional.",
                "arquivos": protegidos}, ensure_ascii=False))
            sys.exit(2)

    saidas = []
    for a in alvos:
        try:
            saidas.append(denoise_um(a, nr, args.aac_bitrate))
        except RuntimeError as e:
            print(json.dumps({"erro": "ffmpeg falhou", "arquivo": a, "stderr": str(e)},
                             ensure_ascii=False))
            sys.exit(1)

    print(json.dumps({"nr": nr, "saidas": saidas}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
