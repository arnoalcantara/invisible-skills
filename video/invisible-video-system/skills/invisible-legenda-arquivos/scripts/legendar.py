#!/usr/bin/env python3
"""legendar.py — gera a transcrição com timestamp por palavra (.json) para um vídeo
ou uma pasta inteira de vídeos, salvando AO LADO da origem com o MESMO nome do vídeo.

Regra de nome e pasta (fixa): para `<pasta>/CORTE.mp4` sai `<pasta>/CORTE.json`.
O vídeo nunca é tocado; só nasce o arquivo irmão.

Por que JSON (e só JSON): traz `segments[].words[]` — cada palavra com start/end medido
por wav2vec2, não interpolado. É a fonte pra animação palavra-a-palavra no Remotion,
consumida pela invisible-legendas-aplicador. É o único formato que o pipeline precisa.

Método (robusto, igual ao resto do sistema): extrai áudio mono 16k com ffmpeg e roda
o WhisperX sobre o WAV — não sobre o vídeo. Isso evita o caminho de decode de vídeo do
torchcodec (que cospe avisos de dylib) e é mais previsível entre máquinas. O WhisperX
gera o JSON num diretório temporário; daqui movemos pro lado do vídeo, com o nome da origem.

Resumível: por padrão pula um vídeo cujo `.json` já existe. `--forcar` re-transcreve e
sobrescreve.

Uso:
    python3 legendar.py <arquivo_ou_pasta> \
        [--whisperx-bin <bin do bootstrap>] [--venv <~/.invisible-video/wxenv>] \
        [--lang pt] [--model large-v3] [--forcar]

Saída (stdout): JSON com um relatório por vídeo (gerado | pulado | erro) + resumo.
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile

try:
    from marcar_secoes import marcar_secoes_no_json
except ImportError:  # módulo irmão; garante o dir do script no path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from marcar_secoes import marcar_secoes_no_json

EXTS_VIDEO = {".mp4", ".mov", ".mkv", ".m4v", ".webm", ".avi", ".mpg", ".mpeg", ".wmv", ".flv"}


def resolver_bin(whisperx_bin, venv):
    """whisperx a chamar: --whisperx-bin explícito → venv central → PATH."""
    if whisperx_bin and os.path.exists(whisperx_bin):
        return whisperx_bin
    if venv:
        cand = os.path.join(venv, "bin", "whisperx")
        if os.path.exists(cand):
            return cand
    return "whisperx"  # confia no PATH


def listar_videos(alvo):
    """Um arquivo → [arquivo]. Uma pasta → vídeos diretos nela (sem recursão), ordenados."""
    if os.path.isfile(alvo):
        return [os.path.abspath(alvo)]
    if os.path.isdir(alvo):
        vids = [
            os.path.join(alvo, f)
            for f in sorted(os.listdir(alvo))
            if os.path.splitext(f)[1].lower() in EXTS_VIDEO
            and not f.startswith(".")
        ]
        return [os.path.abspath(v) for v in vids]
    return []


def extrair_audio(video, wav):
    cmd = [
        "ffmpeg", "-y", "-i", video,
        "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le",
        wav,
    ]
    subprocess.run(cmd, check=True, capture_output=True)


def alvo_json(video):
    """Caminho de saída irmão do vídeo: mesmo nome, extensão .json."""
    return os.path.splitext(video)[0] + ".json"


def ja_pronto(video):
    """True se o .json já existe e não está vazio."""
    p = alvo_json(video)
    return os.path.isfile(p) and os.path.getsize(p) > 0


def legendar_um(video, wx_bin, lang, model):
    """Gera o .json para um vídeo. Retorna dict de relatório."""
    destino = alvo_json(video)
    with tempfile.TemporaryDirectory() as tmp:
        wav = os.path.join(tmp, "audio.wav")
        try:
            extrair_audio(video, wav)
        except subprocess.CalledProcessError as e:
            return {"video": os.path.basename(video), "status": "erro",
                    "etapa": "extrair_audio", "stderr": (e.stderr or b"")[-800:].decode("utf-8", "ignore")}

        # WhisperX gera só o JSON (transcrição + alinhamento por palavra), nomeado pelo
        # basename do WAV no diretório temporário. Movemos pro lado do vídeo.
        cmd = [
            wx_bin, wav,
            "--model", model,
            "--language", lang,
            "--device", "cpu",
            "--compute_type", "int8",
            "--output_format", "json",
            "--output_dir", tmp,
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            return {"video": os.path.basename(video), "status": "erro",
                    "etapa": "whisperx", "stderr": proc.stderr[-1500:]}

        wav_base = os.path.splitext(os.path.basename(wav))[0]
        origem = os.path.join(tmp, f"{wav_base}.json")
        if not (os.path.isfile(origem) and os.path.getsize(origem) > 0):
            return {"video": os.path.basename(video), "status": "erro",
                    "etapa": "saida_json", "detalhe": "WhisperX não gerou json"}
        os.replace(origem, destino)  # sobrescreve em --forcar

    # sidecar de roteiro: se há <video>.md ao lado, marca cada palavra do JSON
    # com a seção (gancho/desenvolvimento...) casando o texto contra a
    # transcrição — tempo medido sobre o vídeo atual, robusto a edição.
    secoes_rel = None
    md_lado = os.path.splitext(video)[0] + ".md"
    if os.path.isfile(md_lado):
        try:
            with open(destino, encoding="utf-8") as f:
                data = json.load(f)
            secoes_rel = marcar_secoes_no_json(data, md_lado)
            if secoes_rel.get("marcado"):
                with open(destino, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False)
        except (OSError, json.JSONDecodeError) as e:
            secoes_rel = {"marcado": False, "erro": str(e)}

    rep = {"video": os.path.basename(video), "status": "gerado",
           "saida": os.path.basename(destino)}
    if secoes_rel is not None:
        rep["secoes"] = secoes_rel
    return rep


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("alvo", help="arquivo de vídeo OU pasta com vídeos")
    ap.add_argument("--whisperx-bin", help="caminho do binário whisperx (do bootstrap)")
    ap.add_argument("--venv", help="venv central com whisperx (fallback)")
    ap.add_argument("--lang", default="pt")
    ap.add_argument("--model", default="large-v3")
    ap.add_argument("--forcar", action="store_true",
                    help="re-transcreve e sobrescreve mesmo se o .json já existir")
    args = ap.parse_args()

    alvo = os.path.abspath(os.path.expanduser(args.alvo))
    videos = listar_videos(alvo)
    if not videos:
        print(json.dumps({"erro": f"nenhum vídeo encontrado em: {alvo}"}, ensure_ascii=False))
        sys.exit(1)

    wx_bin = resolver_bin(args.whisperx_bin, args.venv)

    relatorios = []
    n_gerados = n_pulados = n_erros = 0
    for v in videos:
        if not args.forcar and ja_pronto(v):
            relatorios.append({"video": os.path.basename(v), "status": "pulado",
                               "motivo": "json já existe"})
            n_pulados += 1
            continue
        rep = legendar_um(v, wx_bin, args.lang, args.model)
        relatorios.append(rep)
        if rep["status"] == "gerado":
            n_gerados += 1
        else:
            n_erros += 1
        # progresso incremental no stderr (não polui o JSON do stdout)
        print(f"[{rep['status']}] {rep['video']}", file=sys.stderr)

    saida = {
        "alvo": alvo,
        "modo": "arquivo" if os.path.isfile(alvo) else "pasta",
        "total": len(videos),
        "gerados": n_gerados,
        "pulados": n_pulados,
        "erros": n_erros,
        "relatorios": relatorios,
    }
    print(json.dumps(saida, ensure_ascii=False, indent=2))
    sys.exit(0 if n_erros == 0 else 2)


if __name__ == "__main__":
    main()
