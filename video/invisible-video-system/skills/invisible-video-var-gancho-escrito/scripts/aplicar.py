#!/usr/bin/env python3
"""aplicar.py — gera uma variação VAR<n> (gancho animado em texto) de um ou mais
vídeos combinados, com Remotion. Orquestra detecção de modo, resolução do JSON,
ênfase por gancho e render em lanes paralelas.

O número da variação é do usuário (--var): ele decide se está produzindo a VAR1,
VAR2, VAR3… daquele vídeo, e esse número entra no nome da saída. O tratamento
visual (gancho escrito em tipografia) é o mesmo; VAR<n> é só o rótulo do título.

NÃO transcreve e NÃO escolhe a ênfase: a ênfase é editorial e vem do agente
(via --enfase-map ou --enfase), conforme a SKILL.md instrui.

Dois modos (interruptor por vídeo, auto-detectado pelo nome ou forçado):
  - legendado: vídeo base = `<comb>_LEGENDADO.mp4` (desenvolvimento já tem a
    legenda reels queimada e aprovada). NÃO re-legenda. PREFERIDO.
  - crua:      vídeo base = `<comb>.mp4` (sem legenda). A legenda reels do
    desenvolvimento é desenhada no render (consome o captions do .json).

O JSON da combinação (`<comb>.json`, com `secoes` + `secao` por palavra) é
SEMPRE necessário — só pelo gancho (boundary + palavras + tempos). Resolução:
ao lado do vídeo → pasta-pai → --json-dir → busca recursiva em --buscar-em.

Saída: <out-dir>/<comb>_LEGENDADO_VAR<n>.mp4 (default out-dir = <pasta>/LEGENDADOS).

Uso:
    python3 aplicar.py <video_ou_pasta> [<v2> ...] \
        --var 2                    # variação a estampar no nome (VAR2); default 1
        --enfase-map enfase.json   # {"VAV19": "estudar,lembrar,...", ...}
        [--enfase "p1,p2"]         # fallback global, se um gancho não está no mapa
        [--modo auto|legendado|crua] [--lanes N] [--out-dir <dir>]
        [--json-dir <dir>] [--buscar-em <raiz>] [--projeto-dir <central>]
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import threading

PROJETO_CENTRAL_PADRAO = os.path.expanduser("~/.invisible-video/gancho-escrito-remotion")
EXTS_VIDEO = {".mp4", ".mov", ".mkv", ".webm", ".m4v"}
SUFIXO_LEGENDADO = "_LEGENDADO"


def coletar_videos(alvos):
    videos = []
    for a in alvos:
        a = os.path.abspath(os.path.expanduser(a))
        if os.path.isdir(a):
            for nome in sorted(os.listdir(a)):
                p = os.path.join(a, nome)
                if os.path.isfile(p) and os.path.splitext(nome)[1].lower() in EXTS_VIDEO:
                    if re.search(r"_VAR[^_]+\.mp4$", nome):
                        continue  # não reprocessa saídas (VAR1/VAR2/VAR3…)
                    videos.append(p)
        elif os.path.isfile(a):
            videos.append(a)
        else:
            print(f"aviso: alvo inexistente ignorado: {a}", file=sys.stderr)
    return videos


def stem_combinacao(stem_video):
    """Tira o sufixo _LEGENDADO para chegar ao nome-base da combinação."""
    if stem_video.endswith(SUFIXO_LEGENDADO):
        return stem_video[: -len(SUFIXO_LEGENDADO)]
    return stem_video


def gancho_de(stem_comb):
    """GANCHO_VAV19__DESENVOLVIMENTO_VAV23 -> VAV19 (None se o padrão não bate)."""
    m = re.match(r"GANCHO_([^_]+)__", stem_comb)
    return m.group(1) if m else None


def achar_json(stem_comb, dir_video, json_dir, buscar_em):
    nome = stem_comb + ".json"
    candidatos = [
        os.path.join(dir_video, nome),
        os.path.join(os.path.dirname(dir_video), nome),  # pasta-pai (LEGENDADOS -> COMBINAÇÕES)
    ]
    if json_dir:
        candidatos.append(os.path.join(json_dir, nome))
    for c in candidatos:
        if os.path.isfile(c):
            return c
    if buscar_em and os.path.isdir(buscar_em):
        for raiz, _, arquivos in os.walk(buscar_em):
            if nome in arquivos:
                return os.path.join(raiz, nome)
    return None


def montar_lane(projeto_dir, lane):
    if os.path.exists(os.path.join(lane, "node_modules")):
        return
    os.makedirs(os.path.join(lane, "src"), exist_ok=True)
    os.makedirs(os.path.join(lane, "public"), exist_ok=True)
    for f in ("package.json", "remotion.config.ts", "tsconfig.json"):
        shutil.copyfile(os.path.join(projeto_dir, f), os.path.join(lane, f))
    for f in os.listdir(os.path.join(projeto_dir, "src")):
        shutil.copyfile(os.path.join(projeto_dir, "src", f), os.path.join(lane, "src", f))
    os.symlink(os.path.join(projeto_dir, "node_modules"), os.path.join(lane, "node_modules"))


def processar_um(video, args, enfase_map, lane, preparar_py):
    stem_video = os.path.splitext(os.path.basename(video))[0]
    stem_comb = stem_combinacao(stem_video)
    dir_video = os.path.dirname(video)

    # modo
    if args.modo == "auto":
        legendado = stem_video.endswith(SUFIXO_LEGENDADO)
    else:
        legendado = args.modo == "legendado"

    # json
    json_path = achar_json(stem_comb, dir_video, args.json_dir, args.buscar_em)
    if not json_path:
        return {"video": video, "ok": False, "erro": f"json '{stem_comb}.json' não encontrado "
                "(rode invisible-legenda-arquivos na combinação)."}

    # ênfase do gancho
    gancho = gancho_de(stem_comb)
    enf = enfase_map.get(gancho) if gancho else None
    if enf is None:
        enf = args.enfase or ""

    out_dir = os.path.abspath(os.path.expanduser(args.out_dir)) if args.out_dir \
        else os.path.join(os.path.dirname(dir_video) if legendado else dir_video, "LEGENDADOS")
    # se o vídeo já está em LEGENDADOS, a saída fica na mesma LEGENDADOS
    if os.path.basename(dir_video) == "LEGENDADOS" and not args.out_dir:
        out_dir = dir_video
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{stem_comb}_LEGENDADO_VAR{args.var}.mp4")

    public = os.path.join(lane, "public")
    p = subprocess.run(
        [sys.executable, preparar_py, json_path, "--video", video, "--out-dir", public, "--enfase", enf],
        capture_output=True, text=True,
    )
    if p.returncode != 0:
        return {"video": video, "ok": False, "etapa": "preparar", "erro": p.stderr[-400:]}

    props = json.dumps({"videoJaLegendado": legendado})
    print(f"\n=== VAR{args.var} [{os.path.basename(lane)}] {'(legendado)' if legendado else '(crua)'}: {stem_comb} (gancho {gancho}) ===", flush=True)
    r = subprocess.run(
        ["npx", "remotion", "render", "gancho-escrito", out_path, "--props=" + props],
        cwd=lane,
    )
    if r.returncode != 0:
        return {"video": video, "ok": False, "etapa": "render"}
    return {"video": video, "ok": True, "modo": "legendado" if legendado else "crua",
            "gancho": gancho, "saida": out_path}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("alvos", nargs="+", help="vídeo(s) ou pasta")
    ap.add_argument("--var", default="1",
                    help="número/rótulo da variação a estampar no nome (VAR<isto>): 1, 2, 3… Default 1.")
    ap.add_argument("--enfase-map", default=None, help="JSON {gancho: 'palavras'}")
    ap.add_argument("--enfase", default="", help="fallback global de ênfase")
    ap.add_argument("--modo", default="auto", choices=["auto", "legendado", "crua"])
    ap.add_argument("--lanes", type=int, default=2)
    ap.add_argument("--out-dir", default=None)
    ap.add_argument("--json-dir", default=None)
    ap.add_argument("--buscar-em", default=None, help="raiz p/ busca recursiva do .json")
    ap.add_argument("--projeto-dir", default=PROJETO_CENTRAL_PADRAO)
    args = ap.parse_args()

    projeto_dir = os.path.expanduser(args.projeto_dir)
    if not os.path.exists(os.path.join(projeto_dir, "node_modules")):
        print(json.dumps({"erro": f"projeto Remotion não instalado em {projeto_dir}. Rode bootstrap.py."}, ensure_ascii=False))
        return 1

    enfase_map = {}
    if args.enfase_map:
        enfase_map = json.load(open(os.path.expanduser(args.enfase_map), encoding="utf-8"))

    videos = coletar_videos(args.alvos)
    if not videos:
        print(json.dumps({"erro": "nenhum vídeo encontrado nos alvos."}, ensure_ascii=False))
        return 1

    preparar_py = os.path.join(os.path.dirname(os.path.abspath(__file__)), "preparar.py")
    n_lanes = max(1, min(args.lanes, len(videos)))

    # filas round-robin
    filas = [[] for _ in range(n_lanes)]
    for i, v in enumerate(videos):
        filas[i % n_lanes].append(v)

    resultados, lock = [], threading.Lock()
    lanes_dirs = []

    def trabalhar(idx):
        lane = os.path.join(os.path.dirname(projeto_dir), f"gancho-escrito-lane-{idx}")
        lanes_dirs.append(lane)
        montar_lane(projeto_dir, lane)
        for v in filas[idx]:
            res = processar_um(v, args, enfase_map, lane, preparar_py)
            with lock:
                resultados.append(res)

    threads = [threading.Thread(target=trabalhar, args=(i,)) for i in range(n_lanes)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # limpar lanes (node_modules é symlink — rm é barato)
    for lane in lanes_dirs:
        shutil.rmtree(lane, ignore_errors=True)

    ok = sum(1 for r in resultados if r.get("ok"))
    print(json.dumps({"total": len(resultados), "ok": ok, "lanes": n_lanes,
                      "resultados": resultados}, ensure_ascii=False, indent=2))
    return 0 if ok == len(resultados) else 1


if __name__ == "__main__":
    sys.exit(main())
