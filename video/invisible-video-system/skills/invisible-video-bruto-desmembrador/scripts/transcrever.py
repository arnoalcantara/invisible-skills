#!/usr/bin/env python3
"""transcrever.py — transcreve uma bruta com WhisperX, com cache por vídeo.

Extrai áudio mono 16k, roda WhisperX (large-v3 + alinhamento forçado pt) e
guarda o JSON com timestamp por palavra. A chave de cache é nome+tamanho+mtime
do vídeo; em re-execução com o mesmo arquivo, reusa o JSON e não re-transcreve.

WhisperX é obrigatório: dá timestamp MEDIDO por palavra (wav2vec2), não
interpolado. whisper.cpp com -ml 1 foi descartado (ver referencia/METODO.md):
interpolava e errava a borda em segundos.

Uso:
    python3 transcrever.py <video> --venv <.wxenv> --cache-dir <.transcricao/wx_out> \
        [--model large-v3] [--lang pt]

Saída (stdout): JSON {"json_path": "...", "cacheado": bool}
O JSON do WhisperX fica em <cache-dir>/<chave>.json com segments[].words[].
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile


def chave_cache(video):
    st = os.stat(video)
    base = os.path.basename(video)
    bruto = f"{base}|{st.st_size}|{int(st.st_mtime)}"
    h = hashlib.sha1(bruto.encode("utf-8")).hexdigest()[:12]
    nome = os.path.splitext(base)[0]
    return f"{nome}.{h}"


def extrair_audio(video, wav):
    cmd = [
        "ffmpeg", "-y", "-i", video,
        "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le",
        wav,
    ]
    subprocess.run(cmd, check=True, capture_output=True)


def resolver_bin(whisperx_bin, venv):
    """Decide qual whisperx chamar.

    Prioridade: --whisperx-bin explícito → venv (central) → whisperx do PATH.
    O bootstrap já resolve isso e passa o caminho em whisperx_bin; aqui é só o
    fallback para quem chamar o script direto.
    """
    if whisperx_bin and os.path.exists(whisperx_bin):
        return whisperx_bin
    if venv:
        cand = os.path.join(venv, "bin", "whisperx")
        if os.path.exists(cand):
            return cand
    return "whisperx"  # confia no PATH


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--whisperx-bin", help="caminho do binário whisperx (do bootstrap)")
    ap.add_argument("--venv", help="venv central com whisperx (fallback)")
    ap.add_argument("--cache-dir", required=True)
    ap.add_argument("--model", default="large-v3")
    ap.add_argument("--lang", default="pt")
    args = ap.parse_args()

    video = os.path.abspath(args.video)
    if not os.path.isfile(video):
        print(json.dumps({"erro": f"vídeo não existe: {video}"}))
        sys.exit(1)

    os.makedirs(args.cache_dir, exist_ok=True)
    chave = chave_cache(video)
    json_path = os.path.join(args.cache_dir, f"{chave}.json")

    if os.path.isfile(json_path) and os.path.getsize(json_path) > 0:
        # valida que é JSON com segments
        try:
            with open(json_path, encoding="utf-8") as f:
                data = json.load(f)
            if "segments" in data:
                print(json.dumps({"json_path": json_path, "cacheado": True}, ensure_ascii=False))
                return
        except (OSError, json.JSONDecodeError):
            pass  # cache inválido, re-transcreve

    with tempfile.TemporaryDirectory() as tmp:
        wav = os.path.join(tmp, "audio.wav")
        extrair_audio(video, wav)

        # WhisperX escreve <nome_do_wav>.json no --output_dir
        cmd = [
            resolver_bin(args.whisperx_bin, args.venv), wav,
            "--model", args.model,
            "--language", args.lang,
            "--device", "cpu",
            "--compute_type", "int8",
            "--output_format", "json",
            "--output_dir", tmp,
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            print(json.dumps({"erro": "whisperx falhou", "stderr": proc.stderr[-2000:]}, ensure_ascii=False))
            sys.exit(1)

        # acha o json gerado
        gerado = None
        for f in os.listdir(tmp):
            if f.endswith(".json"):
                gerado = os.path.join(tmp, f)
                break
        if gerado is None:
            print(json.dumps({"erro": "whisperx não gerou JSON", "stdout": proc.stdout[-1000:]}))
            sys.exit(1)

        with open(gerado, encoding="utf-8") as f:
            data = json.load(f)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)

    print(json.dumps({"json_path": json_path, "cacheado": False}, ensure_ascii=False))


if __name__ == "__main__":
    main()
