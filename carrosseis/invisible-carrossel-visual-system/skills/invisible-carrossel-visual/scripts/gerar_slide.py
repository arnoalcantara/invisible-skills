#!/usr/bin/env python3
"""gerar_slide.py — gera UM slide via Higgsfield CLI (gpt_image_2) com COLETA ROBUSTA.

Lição do teste de prova (26/06/2026): o `--wait` do Higgsfield CLI dá HTTP 502 com
frequência NA COLETA do resultado — e o job COBRA mesmo quando o --wait falha. Logo,
NUNCA confiar no --wait. O padrão correto é:

  1. Disparar o job SEM --wait → capturar o job_id imediatamente.
  2. Pollar o resultado por `higgsfield generate get <id> --json` até `completed`.
  3. Se o poll falhar (502 transitório), tentar de novo — o job já está rodando no
     servidor, não re-disparar (re-disparar = pagar de novo).
  4. Ao completar, baixar a `result_url` para o arquivo de saída.

Assim uma imagem que já foi paga nunca se perde por um 502 na coleta.

Valida a proporção do PNG baixado (3:4 ≈ 0.75); se vier diferente, marca como falha
(NUNCA força resize — distorce). Re-render é decisão do agente.

Uso:
    python3 gerar_slide.py \
        --prompt-file <arquivo.txt> \
        --out <slide.png> \
        [--image <ref1.png> --image <ref2.png> ...] \
        [--aspect 3:4] [--quality high] [--resolution 2k] \
        [--timeout 600] [--poll 8]

Saída (stdout): JSON com job_id, status, out, dimensoes, ratio, ok, erro.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.request

UUID_RE = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", re.I)
URL_RE = re.compile(r'https://[^\s"]+\.(?:png|jpg|jpeg|webp)', re.I)


def run(cmd, timeout=120):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def disparar(prompt, images, aspect, quality, resolution):
    """Dispara o job SEM --wait. Retorna job_id (str) ou None."""
    cmd = ["higgsfield", "generate", "create", "gpt_image_2",
           "--prompt", prompt,
           "--aspect_ratio", aspect,
           "--quality", quality,
           "--resolution", resolution,
           "--json"]
    for img in images:
        cmd += ["--image", img]
    r = run(cmd, timeout=120)
    blob = (r.stdout or "") + (r.stderr or "")
    # o id do job é o primeiro UUID do response
    m = UUID_RE.search(blob)
    return m.group(0) if m else None


def coletar(job_id, timeout, poll):
    """Polla `generate get <id>` até completar. Resiliente a 502 transitório."""
    deadline = time.time() + timeout
    ultimo = ""
    while time.time() < deadline:
        r = run(["higgsfield", "generate", "get", job_id, "--json"], timeout=60)
        blob = (r.stdout or "")
        ultimo = blob + (r.stderr or "")
        try:
            data = json.loads(blob)
            obj = data[0] if isinstance(data, list) and data else data
            status = (obj or {}).get("status")
            if status == "completed":
                url = (obj or {}).get("result_url")
                if not url:
                    m = URL_RE.search(blob)
                    url = m.group(0) if m else None
                return url, "completed", ultimo
            if status in ("failed", "canceled"):
                return None, status, ultimo
        except (ValueError, TypeError):
            pass  # 502 ou JSON parcial: tenta de novo
        time.sleep(poll)
    return None, "timeout", ultimo


def baixar(url, out):
    urllib.request.urlretrieve(url, out)


def dimensoes(path):
    try:
        from PIL import Image
        with Image.open(path) as im:
            return im.size
    except Exception:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt-file", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--image", action="append", default=[])
    ap.add_argument("--aspect", default="3:4")
    ap.add_argument("--quality", default="high")
    ap.add_argument("--resolution", default="2k")
    ap.add_argument("--timeout", type=int, default=600)
    ap.add_argument("--poll", type=int, default=8)
    ap.add_argument("--job-id", default=None,
                    help="pular o disparo e só coletar este job (recuperação)")
    args = ap.parse_args()

    out = {"job_id": None, "status": None, "out": args.out,
           "dimensoes": None, "ratio": None, "ok": False, "erro": None}

    prompt = open(args.prompt_file, encoding="utf-8").read()

    # 1. disparar (ou usar job_id existente para recuperação)
    job_id = args.job_id
    if not job_id:
        job_id = disparar(prompt, args.image, args.aspect, args.quality, args.resolution)
        if not job_id:
            out["erro"] = "não consegui capturar o job_id no disparo"
            print(json.dumps(out, ensure_ascii=False, indent=2))
            sys.exit(1)
    out["job_id"] = job_id

    # 2. coletar (resiliente a 502)
    url, status, _log = coletar(job_id, args.timeout, args.poll)
    out["status"] = status
    if not url:
        out["erro"] = f"sem result_url (status={status}). " \
                      f"Recupere depois com: --job-id {job_id}"
        print(json.dumps(out, ensure_ascii=False, indent=2))
        sys.exit(1)

    # 3. baixar
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    baixar(url, args.out)

    # 4. validar proporção
    dim = dimensoes(args.out)
    if dim:
        w, h = dim
        ratio = round(w / h, 3)
        out["dimensoes"] = [w, h]
        out["ratio"] = ratio
        # 3:4 = 0.75. Tolerância pequena; outra proporção = falha de render.
        if abs(ratio - 0.75) > 0.02:
            out["erro"] = f"proporção {ratio} != 3:4 — re-render (NÃO forçar resize)"
            print(json.dumps(out, ensure_ascii=False, indent=2))
            sys.exit(1)

    out["ok"] = True
    print(json.dumps(out, ensure_ascii=False, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
