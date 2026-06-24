#!/usr/bin/env python3
"""aplicar.py — gera uma variação VAR<n> (gancho animado em texto) de um ou mais
vídeos combinados, com Remotion. Orquestra detecção de modo, resolução do JSON,
ênfase por gancho e render em lanes paralelas.

O número da variação é do usuário (--var): ele decide se está produzindo a VAR1,
VAR2, VAR3… daquele vídeo, e esse número entra no nome da saída. O tratamento
visual (gancho escrito em tipografia) é o mesmo; VAR<n> é só o rótulo do título.

NÃO transcreve e NÃO escolhe a ênfase: a ênfase é editorial e vem do agente
(via --enfase-map ou --enfase), conforme a SKILL.md instrui.

Dois ALVOS (--alvo):
  - combinacao (default): varia o gancho DENTRO de uma combinação; o
    desenvolvimento aparece no boundary. Modo de legenda (interruptor por vídeo,
    auto/legendado/crua) decide se re-desenha a legenda do desenvolvimento.
  - segmento: o clipe INTEIRO é um gancho isolado (já otimizado). A tipografia
    cobre o clipe todo; não há desenvolvimento nem karaokê. O gancho variado é
    final por si — vai direto pra 03_PREPARADOS. Entrada típica: os clipes de
    gancho de 02_OTIMIZADOS (vertical e quadrado).

O JSON (`segments[].words[]`; no alvo combinacao também `secoes`/`secao`) é
SEMPRE necessário pelo gancho. É nomeado pela BASE (sem formato/VAR) — a skill o
acha removendo o token de formato/VAR do nome do clipe e procurando o irmão.

Saída: <out-dir>/<id>_OTIMIZADO_VAR<n>_VERTICAL.mp4 — o _VAR<n> entra ANTES do
token de formato (formato sempre o último token). Default out-dir = pasta-irmã
03_PREPARADOS.

Uso:
    python3 aplicar.py <video_ou_pasta> [<v2> ...] \
        --alvo segmento|combinacao # default combinacao
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

# token de formato é sempre o último; o .json é nomeado pela base (sem formato/VAR).
RE_FORMATO = re.compile(r"(?i)_(VERTICAL|QUADRADO|HORIZONTAL)$")
RE_VAR = re.compile(r"(?i)_VAR\d+")


def formato_de(stem):
    """Token de formato final (_VERTICAL/_QUADRADO/...), ou '' se não houver."""
    m = RE_FORMATO.search(stem)
    return m.group(0) if m else ""


def base_sem_formato_var(stem):
    """Remove o token de formato (final) e qualquer _VAR<n>."""
    return RE_VAR.sub("", RE_FORMATO.sub("", stem))


def coletar_videos(alvos):
    videos = []
    for a in alvos:
        a = os.path.abspath(os.path.expanduser(a))
        if os.path.isdir(a):
            for nome in sorted(os.listdir(a)):
                p = os.path.join(a, nome)
                if os.path.isfile(p) and os.path.splitext(nome)[1].lower() in EXTS_VIDEO:
                    if RE_VAR.search(os.path.splitext(nome)[0]):
                        continue  # não reprocessa saídas (VAR1/VAR2/VAR3…)
                    videos.append(p)
        elif os.path.isfile(a):
            videos.append(a)
        else:
            print(f"aviso: alvo inexistente ignorado: {a}", file=sys.stderr)
    return videos


def stem_combinacao(stem_video):
    """Tira o sufixo _LEGENDADO (alvo combinacao) para chegar ao nome-base.

    Cuidado: o _LEGENDADO vem ANTES do token de formato (..._LEGENDADO_VERTICAL),
    então removemos o _LEGENDADO preservando o formato no fim."""
    fmt = formato_de(stem_video)
    miolo = stem_video[: -len(fmt)] if fmt else stem_video
    if miolo.endswith(SUFIXO_LEGENDADO):
        miolo = miolo[: -len(SUFIXO_LEGENDADO)]
    return miolo + fmt


def gancho_de(stem_comb):
    """GANCHO_VAV19__DESENVOLVIMENTO_VAV23 -> VAV19. No alvo segmento, GANCHO_VAV19
    (ou <prefixo>_VAV19...) -> VAV19. Casa o primeiro código alfanumérico."""
    m = re.match(r"(?i)GANCHO_([^_]+)__", stem_comb)
    if m:
        return m.group(1)
    m = re.search(r"([A-Z]{2,6}\d{1,5})", stem_comb)
    return m.group(1) if m else None


def achar_json(stem_comb, dir_video, json_dir, buscar_em):
    # o .json é nomeado pela base (sem formato/VAR).
    nome = base_sem_formato_var(stem_comb) + ".json"
    candidatos = [
        os.path.join(dir_video, nome),
        os.path.join(os.path.dirname(dir_video), nome),  # pasta-pai
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
    dir_video = os.path.dirname(video)
    segmento = args.alvo == "segmento"

    if segmento:
        # o clipe inteiro é gancho; o stem-base é o próprio nome do clipe.
        stem_comb = stem_video
        # gancho variado é final por si: sem captions de desenvolvimento.
        legendado = True
    else:
        stem_comb = stem_combinacao(stem_video)
        if args.modo == "auto":
            # _LEGENDADO vem antes do formato: ..._LEGENDADO_VERTICAL
            legendado = bool(re.search(r"(?i)_LEGENDADO(_(VERTICAL|QUADRADO|HORIZONTAL))?$", stem_video))
        else:
            legendado = args.modo == "legendado"

    # json (nomeado pela base, sem formato/VAR)
    json_path = achar_json(stem_comb, dir_video, args.json_dir, args.buscar_em)
    if not json_path:
        base = base_sem_formato_var(stem_comb)
        return {"video": video, "ok": False, "erro": f"json '{base}.json' não encontrado "
                "(rode invisible-legenda-arquivos no segmento/combinação)."}

    # ênfase do gancho
    gancho = gancho_de(stem_comb)
    enf = enfase_map.get(gancho) if gancho else None
    if enf is None:
        enf = args.enfase or ""

    # saída na pasta-irmã 03_PREPARADOS (etapa da linha), não numa subpasta.
    if args.out_dir:
        out_dir = os.path.abspath(os.path.expanduser(args.out_dir))
    else:
        out_dir = os.path.join(os.path.dirname(dir_video.rstrip("/")), "03_PREPARADOS")
    os.makedirs(out_dir, exist_ok=True)

    # nome: _VAR<n> ANTES do token de formato (formato sempre o último token).
    fmt = formato_de(stem_comb)
    miolo = stem_comb[: -len(fmt)] if fmt else stem_comb
    out_path = os.path.join(out_dir, f"{miolo}_VAR{args.var}{fmt}.mp4")

    public = os.path.join(lane, "public")
    cmd_prep = [sys.executable, preparar_py, json_path, "--video", video,
                "--out-dir", public, "--enfase", enf, "--alvo", args.alvo]
    p = subprocess.run(cmd_prep, capture_output=True, text=True)
    if p.returncode != 0:
        return {"video": video, "ok": False, "etapa": "preparar", "erro": p.stderr[-400:]}

    props = json.dumps({"videoJaLegendado": legendado})
    rotulo = "segmento" if segmento else ("legendado" if legendado else "crua")
    print(f"\n=== VAR{args.var} [{os.path.basename(lane)}] ({rotulo}): {stem_comb} (gancho {gancho}) ===", flush=True)
    r = subprocess.run(
        ["npx", "remotion", "render", "gancho-escrito", out_path, "--props=" + props],
        cwd=lane,
    )
    if r.returncode != 0:
        return {"video": video, "ok": False, "etapa": "render"}
    return {"video": video, "ok": True, "alvo": args.alvo,
            "modo": rotulo, "gancho": gancho, "saida": out_path}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("alvos", nargs="+", help="vídeo(s) ou pasta")
    ap.add_argument("--alvo", default="combinacao", choices=["combinacao", "segmento"],
                    help="combinacao (default): gancho dentro de uma combinação. "
                         "segmento: o clipe inteiro é gancho (corte isolado já otimizado).")
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
