#!/usr/bin/env python3
"""preparar.py — prepara os insumos do Remotion para a variação de gancho escrito
(gancho animado em texto). O número VAR<n> não importa aqui: os insumos são os
mesmos; o rótulo da variação só entra no nome da saída, lá no aplicar.py.

A partir do `.json` WhisperX de uma combinação (com `secoes` no topo e `secao`
por palavra), gera dentro de `public/`:

  - video.mp4      cópia da combinação (fonte do áudio + imagem do desenvolvimento)
  - captions.json  Caption[] só do DESENVOLVIMENTO (legenda reels, igual ao pipeline)
  - hook.json      { boundaryMs, sentences:[{startMs,endMs,words:[{text,startMs,endMs,emphasis}]}] }

A marcação de ênfase é editorial: passa-se `--enfase "palavra,palavra,..."`
(as formas batidas por texto normalizado crescem na animação).

Uso:
    python3 preparar.py <combinacao.json> [--video <mp4>] [--out-dir public]
        [--enfase "estudar,lembrar,leio,excelente,mudou,vida,alunos"]
"""
import argparse
import json
import os
import re
import shutil
import unicodedata

FIM_DE_FRASE = (".", "?", "!", "…")


def normalizar(t: str) -> str:
    """lower + sem acento + só alfanumérico — para casar ênfase por texto."""
    t = unicodedata.normalize("NFKD", t)
    t = "".join(c for c in t if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]", "", t.lower())


def palavras_da_secao(wx, secao):
    """Achata as palavras de uma seção, na ordem, preenchendo timestamps vazios
    pela vizinhança (mesma lógica do convert_captions.mjs)."""
    flat = []
    for seg in wx.get("segments", []):
        for w in seg.get("words", []):
            if w.get("secao") != secao:
                continue
            flat.append({
                "word": (w.get("word") or "").strip(),
                "start": w["start"] if isinstance(w.get("start"), (int, float)) else None,
                "end": w["end"] if isinstance(w.get("end"), (int, float)) else None,
                "score": w["score"] if isinstance(w.get("score"), (int, float)) else None,
            })
    for i, w in enumerate(flat):
        if w["start"] is None:
            prev = flat[i - 1] if i > 0 else None
            w["start"] = prev["end"] if prev and prev["end"] is not None else (w["end"] or 0.0)
        if w["end"] is None:
            nxt = flat[i + 1] if i + 1 < len(flat) else None
            w["end"] = nxt["start"] if nxt and nxt["start"] is not None else w["start"] + 0.12
        if w["end"] < w["start"]:
            w["end"] = w["start"] + 0.08
    return flat


def gerar_captions(flat):
    """Caption[] no formato @remotion/captions (uma por palavra)."""
    return [{
        "text": " " + w["word"],
        "startMs": round(w["start"] * 1000),
        "endMs": round(w["end"] * 1000),
        "timestampMs": round((w["start"] + w["end"]) / 2 * 1000),
        "confidence": w["score"],
    } for w in flat]


def agrupar_em_frases(flat, enfase_set):
    """Agrupa palavras do gancho em frases pela pontuação final da própria
    palavra. Marca emphasis quando a forma normalizada está no conjunto."""
    frases, atual = [], []
    for w in flat:
        token = {
            "text": w["word"],
            "startMs": round(w["start"] * 1000),
            "endMs": round(w["end"] * 1000),
            "emphasis": normalizar(w["word"]) in enfase_set,
        }
        atual.append(token)
        if w["word"].rstrip().endswith(FIM_DE_FRASE):
            frases.append(atual)
            atual = []
    if atual:
        frases.append(atual)
    return [{
        "startMs": fr[0]["startMs"],
        "endMs": fr[-1]["endMs"],
        "words": fr,
    } for fr in frases]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("json", help="combinacao.json (WhisperX + secoes)")
    ap.add_argument("--video", default=None, help="mp4 da combinação; default: <json sem ext>.mp4")
    ap.add_argument("--out-dir", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "public"))
    ap.add_argument("--enfase", default="", help="palavras de ênfase, separadas por vírgula")
    args = ap.parse_args()

    json_path = os.path.abspath(os.path.expanduser(args.json))
    wx = json.load(open(json_path, encoding="utf-8"))
    out_dir = os.path.abspath(os.path.expanduser(args.out_dir))
    os.makedirs(out_dir, exist_ok=True)

    # boundary: fim do gancho = início do desenvolvimento
    secoes = {s["nome"]: s for s in wx.get("secoes", [])}
    if "gancho" not in secoes:
        raise SystemExit("erro: combinação sem seção 'gancho' no .json")
    boundary_ms = round(secoes["gancho"]["end"] * 1000)

    enfase_set = {normalizar(p) for p in args.enfase.split(",") if p.strip()}

    # desenvolvimento -> captions.json
    dev = palavras_da_secao(wx, "desenvolvimento")
    captions = gerar_captions(dev)
    json.dump(captions, open(os.path.join(out_dir, "captions.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)

    # gancho -> hook.json (por frase, com ênfase)
    gancho = palavras_da_secao(wx, "gancho")
    frases = agrupar_em_frases(gancho, enfase_set)
    hook = {"boundaryMs": boundary_ms, "sentences": frases}
    json.dump(hook, open(os.path.join(out_dir, "hook.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)

    # vídeo -> public/video.mp4
    video = os.path.abspath(os.path.expanduser(args.video)) if args.video \
        else os.path.splitext(json_path)[0] + ".mp4"
    if not os.path.isfile(video):
        raise SystemExit(f"erro: vídeo não encontrado: {video}")
    shutil.copyfile(video, os.path.join(out_dir, "video.mp4"))

    print(json.dumps({
        "boundaryMs": boundary_ms,
        "frases_gancho": len(frases),
        "palavras_gancho": len(gancho),
        "palavras_desenvolvimento": len(dev),
        "enfases_marcadas": sum(1 for fr in frases for w in fr["words"] if w["emphasis"]),
        "video": video,
        "out_dir": out_dir,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
