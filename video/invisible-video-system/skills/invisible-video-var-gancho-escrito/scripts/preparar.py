#!/usr/bin/env python3
"""preparar.py — prepara os insumos do Remotion para a variação de gancho escrito
(gancho animado em texto). O número VAR<n> não importa aqui: os insumos são os
mesmos; o rótulo da variação só entra no nome da saída, lá no aplicar.py.

Dois alvos (--alvo):
  - combinacao (default): o `.json` tem `secoes` (gancho + desenvolvimento). A
    tipografia cobre só o GANCHO e revela o desenvolvimento no boundary. Gera
    captions.json do desenvolvimento (legenda reels) quando o vídeo é cru.
  - segmento: o clipe INTEIRO é o gancho (um corte de gancho isolado, já otimizado).
    A tipografia cobre o clipe do começo ao fim — boundaryMs = duração do vídeo —
    sem captions de desenvolvimento (não há). Usa a seção `gancho` se marcada, ou
    TODAS as palavras do `.json` como fallback.

A partir do `.json` WhisperX, gera dentro de `public/`:

  - video.mp4      cópia do vídeo (fonte do áudio + imagem)
  - captions.json  Caption[] do desenvolvimento (vazio no alvo segmento)
  - hook.json      { boundaryMs, sentences:[{startMs,endMs,words:[{text,startMs,endMs,emphasis}]}] }

A marcação de ênfase é editorial: passa-se `--enfase "palavra,palavra,..."`
(as formas batidas por texto normalizado crescem na animação).

Uso:
    python3 preparar.py <json> [--video <mp4>] [--out-dir public]
        [--alvo combinacao|segmento]
        [--enfase "estudar,lembrar,leio,excelente,mudou,vida,alunos"]
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import unicodedata

FIM_DE_FRASE = (".", "?", "!", "…")


def duracao_video(video):
    """Duração em segundos via ffprobe (float), ou None."""
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", video],
        capture_output=True, text=True).stdout.strip()
    try:
        return float(out)
    except ValueError:
        return None


def normalizar(t: str) -> str:
    """lower + sem acento + só alfanumérico — para casar ênfase por texto."""
    t = unicodedata.normalize("NFKD", t)
    t = "".join(c for c in t if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]", "", t.lower())


def palavras_da_secao(wx, secao):
    """Achata as palavras de uma seção, na ordem, preenchendo timestamps vazios
    pela vizinhança (mesma lógica do convert_captions.mjs). Se secao=None, pega
    TODAS as palavras (usado no alvo segmento, onde o clipe inteiro é gancho)."""
    flat = []
    for seg in wx.get("segments", []):
        for w in seg.get("words", []):
            if secao is not None and w.get("secao") != secao:
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
    ap.add_argument("json", help="json WhisperX (com secoes no alvo combinacao)")
    ap.add_argument("--video", default=None, help="mp4 de entrada; default: <json sem ext>.mp4")
    ap.add_argument("--out-dir", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "public"))
    ap.add_argument("--alvo", default="combinacao", choices=["combinacao", "segmento"],
                    help="combinacao: gancho dentro de uma combinação (revela o "
                         "desenvolvimento no boundary). segmento: o clipe inteiro é gancho.")
    ap.add_argument("--enfase", default="", help="palavras de ênfase, separadas por vírgula")
    args = ap.parse_args()

    json_path = os.path.abspath(os.path.expanduser(args.json))
    wx = json.load(open(json_path, encoding="utf-8"))
    out_dir = os.path.abspath(os.path.expanduser(args.out_dir))
    os.makedirs(out_dir, exist_ok=True)

    # vídeo -> public/video.mp4 (resolve cedo: o alvo segmento precisa da duração)
    video = os.path.abspath(os.path.expanduser(args.video)) if args.video \
        else os.path.splitext(json_path)[0] + ".mp4"
    if not os.path.isfile(video):
        raise SystemExit(f"erro: vídeo não encontrado: {video}")

    enfase_set = {normalizar(p) for p in args.enfase.split(",") if p.strip()}

    if args.alvo == "segmento":
        # o clipe inteiro é gancho: boundary = duração do vídeo (a tipografia
        # cobre tudo, nunca revela imagem crua). Sem desenvolvimento.
        dur = duracao_video(video)
        if dur is None:
            raise SystemExit(f"erro: não consegui ler a duração de {video} (ffprobe)")
        boundary_ms = round(dur * 1000)
        # usa a seção 'gancho' se o .json estiver marcado; senão, todas as palavras.
        secoes = {s["nome"]: s for s in wx.get("secoes", [])}
        gancho = palavras_da_secao(wx, "gancho" if "gancho" in secoes else None)
        dev = []
    else:
        # combinação: boundary = fim do gancho = início do desenvolvimento.
        secoes = {s["nome"]: s for s in wx.get("secoes", [])}
        if "gancho" not in secoes:
            raise SystemExit("erro: combinação sem seção 'gancho' no .json "
                             "(use --alvo segmento para um corte de gancho isolado)")
        boundary_ms = round(secoes["gancho"]["end"] * 1000)
        gancho = palavras_da_secao(wx, "gancho")
        dev = palavras_da_secao(wx, "desenvolvimento")

    # captions.json (desenvolvimento; vazio no alvo segmento)
    captions = gerar_captions(dev)
    json.dump(captions, open(os.path.join(out_dir, "captions.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)

    # gancho -> hook.json (por frase, com ênfase)
    frases = agrupar_em_frases(gancho, enfase_set)
    hook = {"boundaryMs": boundary_ms, "sentences": frases}
    json.dump(hook, open(os.path.join(out_dir, "hook.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)

    shutil.copyfile(video, os.path.join(out_dir, "video.mp4"))

    print(json.dumps({
        "alvo": args.alvo,
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
