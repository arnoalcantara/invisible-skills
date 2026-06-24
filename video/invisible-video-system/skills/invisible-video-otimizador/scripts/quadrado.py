#!/usr/bin/env python3
"""quadrado.py — gera a versão QUADRADA (1:1) de vídeos verticais otimizados.

Roda DEPOIS do otimizar.py, sobre a pasta OTIMIZADOS/ (ou um arquivo). Para cada
`_OTIMIZADO`, recorta um quadrado de largura cheia e o salva como `_QUADRADO` ao
lado — o vertical e o quadrado convivem na mesma pasta e seguem em paralelo pela
esteira.

POR QUE AQUI (e não na combinação): o enquadramento vertical→quadrado é uma
decisão POR BRUTA (onde fica o rosto dentro do 1:1). Resolvida uma vez no
otimizado, propaga idêntica a todas as combinações. Se ficasse pro combinador,
cada par gancho+desenvolvimento exigiria reenquadrar de novo.

COMO A ÂNCORA É DECIDIDA — face detection (YuNet) ancorada nos OLHOS:
  - O quadrado tem lado = LARGURA do vídeo (largura cheia, descarta altura). A
    folga vertical é H - W; a âncora `y` ∈ [0, H-W] é o que se decide.
  - Detector YuNet (cv2.FaceDetectorYN, modelo ~230KB em referencia/modelos/, sem
    torch). Além da caixa, ele devolve 5 pontos faciais — e a âncora usa os OLHOS,
    não o centro da caixa. POR QUÊ: o Haar (testado antes) centra a caixa no rosto
    inteiro e a barba branca grande puxa o centro pra baixo (pro queixo), cortando
    a coroa da cabeça no crop. Os olhos são um ponto estável, imune à barba.
  - Amostra ~8 frames, pega a MEDIANA do y dos olhos (câmera estática → quase não
    andam) e coloca os olhos em ~30% da altura do quadrado (terço superior, com
    respiro pra coroa): y = clamp(olhos_y - 0.30*W, 0, H-W). Default 0.30 cravado
    de ouvido pelo Arno (olhos mais altos) sobre o material do Lote 01.
  - Detecções implausíveis (olhos fora de [0.15, 0.75]·H) são descartadas. Sem
    rosto plausível (mão na frente, cabeça virada): fallback âncora alta segura
    y = 0.15*(H-W).
  - --ancora <fração> sobrepõe a detecção (0=topo, 0.5=centro, 1=base). É o que a
    SKILL usa quando o Arno NUDGA um corte na folha de contato.

FOLHA DE CONTATO: com --contato, monta um PNG (grade de miniaturas, uma por
quadrado, com o nome embaixo) pra aprovação em bloco — o auto acerta a maioria e
o Arno cutuca só os outliers (o Haar chuta feio de vez em quando).

Uso (rodar com o PYTHON DA VENV que tem cv2 — ver bootstrap.py):
    ~/.invisible-video/wxenv/bin/python quadrado.py <arquivo_ou_pasta> \
        [--out-dir <dir>] [--target-frac 0.45] [--ancora <fração>] \
        [--crf 20] [--preset medium] [--contato] [--frames 8]

Saída (stdout): JSON {"resultados": [{origem, saida, ancora_y, folga, rosto, fonte}]}
"""
import argparse
import json
import os
import re
import subprocess
import sys

try:
    import cv2
except ImportError:
    print(json.dumps({
        "erro": "cv2 (opencv) não encontrado. Rode o bootstrap.py do otimizador "
                "para instalar opencv-python-headless na venv central, e invoque "
                "este script com o python dessa venv (~/.invisible-video/wxenv/bin/python)."
    }, ensure_ascii=False))
    sys.exit(3)

VIDEO_EXT = {".mp4", ".mov", ".mkv", ".m4v", ".avi", ".webm"}
EYE_FRAC_PADRAO = 0.30      # onde a linha dos OLHOS cai dentro do quadrado
FALLBACK_FRAC = 0.15        # âncora alta segura quando não detecta rosto

MODELO_YUNET = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "referencia", "modelos", "face_detection_yunet_2023mar.onnx")


def _detector(w, h):
    """YuNet configurado pro tamanho do frame. score_threshold alto corta lixo."""
    return cv2.FaceDetectorYN.create(
        MODELO_YUNET, "", (w, h), score_threshold=0.6, nms_threshold=0.3, top_k=50)


def ffprobe_wh_dur(video):
    def run(args):
        return subprocess.run(args, capture_output=True, text=True).stdout.strip()
    wh = run(["ffprobe", "-v", "error", "-select_streams", "v:0",
              "-show_entries", "stream=width,height", "-of", "csv=p=0", video])
    dur = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
               "-of", "csv=p=0", video])
    try:
        w, h = (int(float(x)) for x in wh.split(","))
    except (ValueError, IndexError):
        return None, None, None
    try:
        d = float(dur)
    except ValueError:
        d = None
    return w, h, d


def codec_de(video):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=codec_name", "-of", "csv=p=0", video],
        capture_output=True, text=True).stdout.strip()
    return out or "hevc"


def encoder_para(codec):
    return {"hevc": "libx265", "h265": "libx265",
            "h264": "libx264", "avc": "libx264"}.get(codec, "libx265")


def _frame(video, t):
    """Extrai 1 frame em t segundos e devolve como imagem cv2 (ou None)."""
    tmp = os.path.join("/tmp", f"_quad_frame_{os.getpid()}.png")
    r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}",
                        "-i", video, "-frames:v", "1", tmp],
                       capture_output=True, text=True)
    if r.returncode != 0 or not os.path.isfile(tmp):
        return None
    img = cv2.imread(tmp)
    try:
        os.remove(tmp)
    except OSError:
        pass
    return img


def detectar_ancora(video, w, h, dur, eye_frac, n_frames):
    """Acha y pela mediana do y dos OLHOS (YuNet). Devolve (y, info)."""
    folga = h - w
    if folga <= 0:
        return 0, {"fonte": "ja_quadrado_ou_horizontal"}
    if not dur:
        return round(FALLBACK_FRAC * folga), {"fonte": "fallback_sem_duracao"}

    import statistics
    det = _detector(w, h)
    olhos = []
    for i in range(1, n_frames + 1):
        img = _frame(video, dur * i / (n_frames + 1))
        if img is None:
            continue
        det.setInputSize((img.shape[1], img.shape[0]))
        ok, faces = det.detect(img)
        if faces is None or len(faces) == 0:
            continue
        # YuNet: [x,y,w,h, olhoD(x,y), olhoE(x,y), nariz, bocaD, bocaE, score]
        f = max(faces, key=lambda r: r[-1])         # melhor score
        ey = (float(f[5]) + float(f[7])) / 2.0      # média dos dois olhos (y)
        if 0.15 * h <= ey <= 0.75 * h:              # plausibilidade
            olhos.append(ey)

    if not olhos:
        return round(FALLBACK_FRAC * folga), {
            "fonte": "fallback_sem_rosto", "deteccoes": 0}

    ey = statistics.median(olhos)
    y = round(ey - eye_frac * w)
    y = max(0, min(folga, y))
    return y, {"fonte": "olhos_yunet", "deteccoes": len(olhos),
               "olhos_y": round(ey)}


def gerar_quadrado(video, out_dir, target_frac, ancora_fixa, crf, preset,
                   n_frames):
    w, h, dur = ffprobe_wh_dur(video)
    if w is None:
        return {"origem": video, "erro": "não consegui ler dimensões (ffprobe)"}
    if w == h:
        return {"origem": video, "saida": None,
                "aviso": "vídeo já é quadrado; nada a fazer"}
    if w > h:
        return {"origem": video, "saida": None,
                "aviso": "vídeo é horizontal (W>H); crop quadrado vertical não se aplica"}

    folga = h - w
    if ancora_fixa is not None:
        y = max(0, min(folga, round(ancora_fixa * folga)))
        info = {"fonte": "ancora_manual", "fracao": ancora_fixa}
    else:
        y, info = detectar_ancora(video, w, h, dur, target_frac, n_frames)

    raiz, ext = os.path.splitext(os.path.basename(video))
    os.makedirs(out_dir, exist_ok=True)
    # o token de formato é SEMPRE o último: a entrada é <id>_OTIMIZADO_VERTICAL,
    # então SUBSTITUI o _VERTICAL final por _QUADRADO (não anexa). Se não houver
    # _VERTICAL no fim (entrada avulsa), anexa _QUADRADO como fallback.
    if re.search(r"(?i)_VERTICAL$", raiz):
        nome_q = re.sub(r"(?i)_VERTICAL$", "_QUADRADO", raiz)
    else:
        nome_q = f"{raiz}_QUADRADO"
    saida = os.path.join(out_dir, f"{nome_q}{ext}")

    venc = encoder_para(codec_de(video))
    # lado = largura cheia; recorta só a altura. Áudio idêntico ao vertical (copy).
    cmd = ["ffmpeg", "-y", "-i", video,
           "-vf", f"crop={w}:{w}:0:{y}",
           "-c:v", venc, "-crf", str(crf), "-preset", preset,
           "-pix_fmt", "yuv420p"]
    if venc == "libx265":
        cmd += ["-tag:v", "hvc1"]
    cmd += ["-c:a", "copy", saida]

    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        return {"origem": video, "erro": "ffmpeg falhou (crop)",
                "stderr": proc.stderr[-1200:]}

    # NÃO propaga sidecar .md pro quadrado: o roteiro é o MESMO da vertical (mesmo
    # áudio). Um .md só por corte (o do vertical) — sem duplicata _QUADRADO.md.

    return {"origem": video, "saida": saida,
            "nome_saida": os.path.basename(saida),
            "dim_origem": f"{w}x{h}", "dim_saida": f"{w}x{w}",
            "ancora_y": y, "folga": folga,
            "ancora_frac": round(y / folga, 3) if folga else 0,
            "rosto": info}


def montar_contato(resultados, out_dir, cols=3, thumb=320):
    """Folha de contato: grade de miniaturas (1 por quadrado) com o nome embaixo."""
    quadros = [r for r in resultados if r.get("saida")]
    if not quadros:
        return None
    import math
    rows = math.ceil(len(quadros) / cols)
    legenda = 28
    cellw, cellh = thumb, thumb + legenda
    import numpy as np
    canvas = np.full((rows * cellh, cols * cellw, 3), 30, dtype=np.uint8)

    for idx, r in enumerate(quadros):
        w, h, dur = ffprobe_wh_dur(r["saida"])
        img = _frame(r["saida"], (dur or 0) / 2.0)
        if img is None:
            continue
        img = cv2.resize(img, (thumb, thumb))
        ri, ci = divmod(idx, cols)
        y0, x0 = ri * cellh, ci * cellw
        canvas[y0:y0 + thumb, x0:x0 + thumb] = img
        nome = r["nome_saida"]
        if len(nome) > 34:
            nome = nome[:31] + "..."
        cv2.putText(canvas, nome, (x0 + 6, y0 + thumb + 19),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (220, 220, 220), 1,
                    cv2.LINE_AA)
    destino = os.path.join(out_dir, "_CONTATO_QUADRADO.png")
    cv2.imwrite(destino, canvas)
    return destino


def coletar(caminho):
    if os.path.isfile(caminho):
        return [caminho]
    vids = []
    for entry in sorted(os.listdir(caminho)):
        p = os.path.join(caminho, entry)
        up = entry.upper()
        if (os.path.isfile(p) and not entry.startswith(".")
                and os.path.splitext(entry)[1].lower() in VIDEO_EXT
                and "QUADRADO" not in up):
            vids.append(p)
    return vids


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("entrada", help="arquivo _OTIMIZADO OU pasta (lote, ex. OTIMIZADOS/)")
    ap.add_argument("--out-dir", help="saída (padrão: mesma pasta da entrada)")
    ap.add_argument("--target-frac", type=float, default=EYE_FRAC_PADRAO,
                    help="onde a linha dos olhos cai no quadrado (0=topo, 1=base)")
    ap.add_argument("--ancora", type=float, default=None,
                    help="sobrepõe a detecção: fração da folga (0=topo,0.5=centro,1=base). "
                         "Use pra NUDGAR um corte específico.")
    ap.add_argument("--frames", type=int, default=8,
                    help="quantos frames amostrar na detecção de rosto")
    ap.add_argument("--crf", type=int, default=20)
    ap.add_argument("--preset", default="medium")
    ap.add_argument("--contato", action="store_true",
                    help="gera a folha de contato (_CONTATO_QUADRADO.png) pra aprovação")
    args = ap.parse_args()

    entrada = os.path.abspath(args.entrada)
    if not os.path.exists(entrada):
        print(json.dumps({"erro": f"não existe: {entrada}"}, ensure_ascii=False))
        sys.exit(1)

    videos = coletar(entrada)
    if not videos:
        print(json.dumps({"erro": "nenhum vídeo (não-quadrado) encontrado"},
                         ensure_ascii=False))
        sys.exit(1)

    base = entrada if os.path.isdir(entrada) else os.path.dirname(entrada)
    out_dir = os.path.abspath(args.out_dir) if args.out_dir else base

    resultados = [
        gerar_quadrado(v, out_dir, args.target_frac, args.ancora,
                       args.crf, args.preset, args.frames)
        for v in videos
    ]

    contato = None
    if args.contato:
        contato = montar_contato(resultados, out_dir)

    print(json.dumps({"out_dir": out_dir, "resultados": resultados,
                      "folha_contato": contato,
                      "target_frac": args.target_frac,
                      "ancora_manual": args.ancora},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
