#!/usr/bin/env python3
"""Motor de inserção de B-roll — ffmpeg puro, determinístico, roda em qualquer máquina.

Insere N coberturas de B-roll num vídeo-alvo por SUBSTITUIÇÃO DE VÍDEO, mantendo o
ÁUDIO ORIGINAL 100% intacto (nunca cortado, deslocado ou reprocessado). Cada B-roll
é reconciliado para a grade EXATA do alvo (resolução/fps/codec/pix_fmt) antes de entrar.

Recebe o alvo + um JSON de pontos. Cada ponto:
    {"entrada": 1.937, "broll": "/caminho/broll.mp4", "ate_fim": false}
- entrada: segundo onde a cobertura começa (âncora na fala).
- broll:   caminho do .mp4 do B-roll (já gerado; pode ser qualquer duração/grade).
- ate_fim: se true, estica o B-roll (clone do último frame) até o fim do alvo.
           Só faz sentido no ÚLTIMO ponto. Se false, usa a duração natural do B-roll
           (aparada em --cobertura, default 2.0s).

Os pontos NÃO podem se sobrepor: cada cobertura ocupa [entrada, entrada+dur]. O script
valida e recusa sobreposição.

Saída: <base>_BROLL_<resto>.mp4 na mesma pasta (o token _BROLL entra logo após a
seção/base, antes de _OTIMIZADO/_VERTICAL — configurável via --sufixo-pos).

Uso:
    python3 inserir.py ALVO.mp4 --pontos pontos.json [--cobertura 2.0] [--out saida.mp4]

Sem --out, o nome é derivado inserindo _BROLL no lugar certo.
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile

FFMPEG = os.environ.get("FFMPEG_BIN", "ffmpeg")
FFPROBE = os.environ.get("FFPROBE_BIN", "ffprobe")


def run(cmd, quiet=True):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        sys.stderr.write("FALHOU: " + " ".join(cmd) + "\n")
        sys.stderr.write(p.stderr[-2000:] + "\n")
        raise SystemExit(1)
    return p.stdout


def probe(path):
    """Specs de vídeo do alvo: largura, altura, fps (num), codec, pix_fmt, duração."""
    out = run([
        FFPROBE, "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=width,height,r_frame_rate,codec_name,pix_fmt",
        "-show_entries", "format=duration",
        "-of", "json", path,
    ])
    d = json.loads(out)
    st = d["streams"][0]
    num, den = st["r_frame_rate"].split("/")
    fps = round(float(num) / float(den))
    return {
        "w": int(st["width"]),
        "h": int(st["height"]),
        "fps": fps,
        "codec": st["codec_name"],
        "pix_fmt": st.get("pix_fmt", "yuv420p"),
        "dur": float(d["format"]["duration"]),
    }


def tem_audio(path):
    out = run([
        FFPROBE, "-v", "error", "-select_streams", "a:0",
        "-show_entries", "stream=codec_name", "-of", "json", path,
    ])
    return bool(json.loads(out).get("streams"))


def venc_args(codec):
    """Args de encoder de vídeo casando o codec do alvo (hevc/libx265 ou h264/libx264)."""
    if codec in ("hevc", "h265"):
        return ["-c:v", "libx265", "-x265-params", "log-level=error"]
    return ["-c:v", "libx264", "-preset", "medium"]


def prep_broll(broll, tmp, idx, alvo, cobertura, ate_fim):
    """Reconcilia um B-roll para a grade do alvo. Retorna caminho do mp4 preparado."""
    w, h, fps, pix = alvo["w"], alvo["h"], alvo["fps"], alvo["pix_fmt"]
    out = os.path.join(tmp, f"broll_{idx}.mp4")
    # scale para altura do alvo mantendo cobertura de largura, depois crop central exato.
    # (o i2v costuma sair um pouco mais largo, ex. 1088 vs 1080 — crop resolve)
    vf = f"scale=-2:{h},crop={w}:{h},fps={fps},setsar=1"
    if ate_fim:
        # estica clonando o último frame; o -t final define a duração exata
        vf += ",tpad=stop_mode=clone:stop_duration=3600"
    cmd = [FFMPEG, "-y", "-i", broll, "-an", "-t", f"{cobertura:.4f}",
           "-vf", vf, *venc_args(alvo["codec"]), "-pix_fmt", pix, out]
    run(cmd)
    return out


def cut_video(alvo_path, tmp, idx, ss, to, alvo):
    """Recorta um pedaço de VÍDEO do alvo (sem áudio), na grade do alvo."""
    out = os.path.join(tmp, f"seg_{idx}.mp4")
    cmd = [FFMPEG, "-y", "-i", alvo_path, "-an", "-ss", f"{ss:.4f}", "-to", f"{to:.4f}",
           "-vf", f"fps={alvo['fps']},setsar=1", *venc_args(alvo["codec"]),
           "-pix_fmt", alvo["pix_fmt"], out]
    run(cmd)
    return out


def derivar_saida(alvo_path, sufixo_pos):
    """Insere _BROLL no nome. sufixo_pos: token ANTES do qual _BROLL entra (ex.: OTIMIZADO)."""
    d = os.path.dirname(alvo_path)
    base = os.path.basename(alvo_path)
    nome, ext = os.path.splitext(base)
    partes = nome.split("_")
    if sufixo_pos and sufixo_pos in partes:
        i = partes.index(sufixo_pos)
        partes.insert(i, "BROLL")
    else:
        # fallback: _BROLL logo antes do último token (formato)
        partes.insert(len(partes) - 1, "BROLL")
    return os.path.join(d, "_".join(partes) + ext)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("alvo")
    ap.add_argument("--pontos", required=True, help="JSON: [{entrada, broll, ate_fim}]")
    ap.add_argument("--cobertura", type=float, default=2.0,
                    help="Duração de cada cobertura em segundos (default 2.0)")
    ap.add_argument("--out", default=None)
    ap.add_argument("--sufixo-pos", default="OTIMIZADO",
                    help="Token antes do qual _BROLL entra no nome (default OTIMIZADO)")
    args = ap.parse_args()

    if not os.path.exists(args.alvo):
        sys.stderr.write(f"Alvo não existe: {args.alvo}\n")
        return 1
    with open(args.pontos, encoding="utf-8") as f:
        pontos = json.load(f)
    if not pontos:
        sys.stderr.write("Nenhum ponto de B-roll.\n")
        return 1

    alvo = probe(args.alvo)
    if not tem_audio(args.alvo):
        sys.stderr.write("Alvo sem áudio — esta skill preserva o áudio original; abortando.\n")
        return 1

    # ordena por entrada e calcula a janela [entrada, fim] de cada cobertura
    pontos = sorted(pontos, key=lambda p: float(p["entrada"]))
    janelas = []
    for i, p in enumerate(pontos):
        ent = float(p["entrada"])
        ate_fim = bool(p.get("ate_fim", False))
        fim = alvo["dur"] if ate_fim else min(ent + args.cobertura, alvo["dur"])
        if ent < 0 or ent >= alvo["dur"]:
            sys.stderr.write(f"Ponto {i} fora do vídeo (entrada={ent}, dur={alvo['dur']:.2f}).\n")
            return 1
        if not os.path.exists(p["broll"]):
            sys.stderr.write(f"B-roll não existe: {p['broll']}\n")
            return 1
        janelas.append({"ent": ent, "fim": fim, "broll": p["broll"], "ate_fim": ate_fim})

    # valida sobreposição
    for a, b in zip(janelas, janelas[1:]):
        if b["ent"] < a["fim"] - 1e-3:
            sys.stderr.write(
                f"Sobreposição: cobertura em {a['ent']:.2f}-{a['fim']:.2f} colide "
                f"com a de {b['ent']:.2f}.\n")
            return 1

    out_path = args.out or derivar_saida(args.alvo, args.sufixo_pos)

    with tempfile.TemporaryDirectory() as tmp:
        # monta a timeline de VÍDEO: [alvo 0->ent1][broll1][alvo fim1->ent2][broll2]...
        # ...[alvo fimN->fim] (a menos que o último seja ate_fim)
        pecas = []
        cursor = 0.0
        for i, j in enumerate(janelas):
            # pedaço do alvo antes desta cobertura
            if j["ent"] > cursor + 1e-3:
                pecas.append(cut_video(args.alvo, tmp, f"a{i}", cursor, j["ent"], alvo))
            # duração desta cobertura
            dur = j["fim"] - j["ent"]
            pecas.append(prep_broll(j["broll"], tmp, i, alvo, dur, j["ate_fim"]))
            cursor = j["fim"]
        # rabo do alvo depois da última cobertura
        if cursor < alvo["dur"] - 1e-3:
            pecas.append(cut_video(args.alvo, tmp, "z", cursor, alvo["dur"], alvo))

        # concat só vídeo — CAMINHOS ABSOLUTOS (ffmpeg resolve relativo à lista, não ao cwd)
        lista = os.path.join(tmp, "concat.txt")
        with open(lista, "w", encoding="utf-8") as f:
            for pc in pecas:
                f.write(f"file '{os.path.abspath(pc)}'\n")
        video_montado = os.path.join(tmp, "video_montado.mp4")
        run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", lista, "-c", "copy", video_montado])

        # remux: vídeo montado + ÁUDIO ORIGINAL inteiro do alvo (nunca reprocessado)
        run([FFMPEG, "-y", "-i", video_montado, "-i", args.alvo,
             "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "copy",
             "-shortest", out_path])

    # verificação
    final = probe(out_path)
    rel = {
        "saida": out_path,
        "grade": f"{final['w']}x{final['h']} {final['fps']}fps {final['codec']}",
        "dur_final": round(final["dur"], 3),
        "dur_alvo": round(alvo["dur"], 3),
        "coberturas": [
            {"entrada": round(j["ent"], 3), "fim": round(j["fim"], 3),
             "ate_fim": j["ate_fim"], "broll": os.path.basename(j["broll"])}
            for j in janelas
        ],
        "ok": abs(final["dur"] - alvo["dur"]) < 0.15
              and (final["w"], final["h"], final["fps"]) == (alvo["w"], alvo["h"], alvo["fps"]),
    }
    print(json.dumps(rel, ensure_ascii=False, indent=2))
    return 0 if rel["ok"] else 2


if __name__ == "__main__":
    sys.exit(main())
