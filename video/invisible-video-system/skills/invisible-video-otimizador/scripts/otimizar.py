#!/usr/bin/env python3
"""otimizar.py — remove silêncios internos de um vídeo sem comer palavra.

Critério validado em sessão real (ver referencia/METODO.md):
  - silêncio = trecho ≥ 0.3s abaixo de -35dB (silencedetect; `d` é a duração
    MÍNIMA pra contar como silêncio — pausas menores ficam intactas).
    -35dB e não -30: a -30 a palavra final dita baixo (decrescendo do professor)
    caía como silêncio e era cortada. -35 trata fala fraca como fala.
  - respiro ASSIMÉTRICO: 0.10s na entrada (após silence_end), 0.25s na saída
    (após silence_start). Início de palavra tem ataque alto (0.1 basta); fim
    decai suave — cauda baixa de "S"/vogal átona — precisa 0.25 pra não comer.
    Respiro simétrico come consoante final: NÃO usar.
  - só silêncios INTERNOS: começo e fim do vídeo ficam intactos.

Constrói os segmentos a MANTER (complemento dos silêncios, com respiros), e os
recorta+concatena ao frame exato via filter_complex (trim/atrim + setpts/asetpts
+ concat). Reencode HEVC preservando specs do original.

Aceita um ARQUIVO ou uma PASTA (lote: otimiza todos os vídeos da pasta).

Descarte de takes (opcional): com --descartar "ini-fim,ini-fim,...", os intervalos
indicados (tomadas repetidas/ruins, vindas do selecionar_takes.py) são REMOVIDOS do
vídeo no mesmo reencode do corte de silêncio. Quem decide os intervalos é a SKILL
(transcreve com WhisperX → selecionar_takes.py → última take vence); aqui só se
aplica o recorte. Só faz sentido pra um ARQUIVO único (cada vídeo tem seus próprios
intervalos), não pra lote.

Normaliza no mesmo passo (opcional): com --normalizar, o corte de silêncio e a
padronização de formato (resolução/fps/códec/áudio) viram um reencode único —
saída pronta pra concatenar. Sem --normalizar, preserva as specs do original.

Uso:
    python3 otimizar.py <arquivo_ou_pasta> [--out-dir <dir>]
        [--modo-silencio conservador|justo]  # -35dB/0.3s ou -33dB/0.15s
        [--silence-noise -35dB] [--silence-min 0.3]   # sobrepõem o --modo-silencio
        [--modo-respiro conservador|justo]   # respiro 0.10/0.25 ou 0.05/0.18
        [--respiro-entrada 0.10] [--respiro-saida 0.25]   # sobrepõem o --modo-respiro
        [--descartar "12.30-18.90,40.10-45.00"]
        [--crf 20] [--preset medium]
        [--normalizar --largura 1080 --altura 1920 --fps 30
         --vcodec libx265 --container mp4 --sample-rate 48000 --canais 2]

Saída (stdout): JSON {"resultados": [{origem, saida, silencios, segmentos, verificacao}]}
"""
import argparse
import json
import os
import re
import subprocess
import sys

VIDEO_EXT = {".mp4", ".mov", ".mkv", ".m4v", ".avi", ".webm"}

# DOIS eixos de modo, INDEPENDENTES (não se acoplam):
#
# 1) Respiro = margem deixada nas bordas da fala (entrada/saída em segundos).
#    conservador: o critério validado em sessão real — preserva mais cauda/ataque.
#    justo: margem menor nas duas pontas (ritmo mais seco).
#    Ambos assimétricos (saída > entrada): o fim da palavra decai suave e precisa
#    de mais margem que o início, que tem ataque alto.
MODOS_RESPIRO = {
    "conservador": {"entrada": 0.10, "saida": 0.25},
    "justo": {"entrada": 0.05, "saida": 0.18},
}
# 2) Silêncio = o que conta como silêncio cortável (limiar de nível + duração mín).
#    conservador: -35dB / 0.3s — fala fraca (decrescendo final) ainda é tratada
#    como fala; só pausa de 0.3s+ é cortada.
#    justo: -33dB / 0.15s — limiar mais alto pega mais coisa como silêncio e a
#    duração menor corta pausas mais curtas. Mais agressivo.
MODOS_SILENCIO = {
    "conservador": {"noise": "-35dB", "min": 0.3},
    "justo": {"noise": "-33dB", "min": 0.15},
}

RE_START = re.compile(r"silence_start:\s*([\d.]+)")
RE_END = re.compile(r"silence_end:\s*([\d.]+)")

# nome de saída: descarta SÓ os tokens de ruído de processamento (BRUTA, VERTICAL,
# RAW...) e mantém TODO o resto na ordem original — tipo (GANCHO/DESENVOLVIMENTO),
# código (VAV23), prefixo (DME), o que houver. Nada de identificação se perde; só
# as palavras de processo somem. Separadores viram underscore único.
RUIDO_NOME = {"BRUTA", "BRUTO", "BRUTAS", "BRUTOS",
              "OTIMIZADO", "OTIMIZADA", "RAW", "FINAL",
              "VERTICAL", "HORIZONTAL"}


def nome_saida_base(nome):
    """Limpa o nome original mantendo toda a identificação.

    Descarta apenas tokens de RUÍDO (BRUTA, VERTICAL, RAW, FINAL, OTIMIZADO...) e
    preserva o resto na ordem em que aparece — tipo, código, prefixo, número.
    'DME__VAV23__VERTICAL__BRUTA__DESENVOLVIMENTO' vira
    'DME_VAV23_DESENVOLVIMENTO' (o tipo NUNCA se perde). Se sobrar nada (nome só
    de ruído), devolve o nome original. Capitalização preservada.
    """
    tokens = [t for t in re.split(r"[_\-.\s]+", nome) if t]
    uteis = [t for t in tokens if t.upper() not in RUIDO_NOME]
    return "_".join(uteis) if uteis else nome


def ffprobe_specs(video):
    def probe(stream, entries):
        cmd = ["ffprobe", "-v", "error", "-select_streams", stream,
               "-show_entries", entries, "-of", "json", video]
        out = subprocess.run(cmd, capture_output=True, text=True).stdout
        try:
            return json.loads(out).get("streams", [])
        except json.JSONDecodeError:
            return []

    v = probe("v:0", "stream=codec_name,pix_fmt,r_frame_rate")
    a = probe("a:0", "stream=codec_name,sample_rate,channels")
    fmt_cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration",
               "-of", "json", video]
    try:
        dur = float(json.loads(
            subprocess.run(fmt_cmd, capture_output=True, text=True).stdout
        )["format"]["duration"])
    except (json.JSONDecodeError, KeyError, ValueError):
        dur = None
    vs = v[0] if v else {}
    as_ = a[0] if a else {}
    return {
        "vcodec": vs.get("codec_name", "hevc"),
        "pix_fmt": vs.get("pix_fmt", "yuv420p"),
        "fps": vs.get("r_frame_rate", "30"),
        "acodec": as_.get("codec_name", "aac"),
        "sample_rate": as_.get("sample_rate", "48000"),
        "channels": int(as_.get("channels", 2) or 2),
        "duracao": dur,
    }


def encoder_para_codec(codec):
    mapa = {"hevc": "libx265", "h265": "libx265", "h264": "libx264", "avc": "libx264"}
    return mapa.get(codec, "libx265")


def detectar_silencios(video, noise, dur_min):
    """Roda silencedetect e devolve lista de (inicio, fim) de cada silêncio."""
    cmd = ["ffmpeg", "-i", video, "-af",
           f"silencedetect=noise={noise}:d={dur_min}", "-f", "null", "-"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    log = proc.stderr
    silencios = []
    inicio = None
    for linha in log.splitlines():
        ms = RE_START.search(linha)
        me = RE_END.search(linha)
        if ms:
            inicio = float(ms.group(1))
        if me and inicio is not None:
            silencios.append((inicio, float(me.group(1))))
            inicio = None
    # silêncio que vai até o fim sem silence_end: ignorado (não é interno)
    return silencios


def segmentos_a_manter(silencios, duracao, resp_in, resp_out):
    """Complemento dos silêncios = trechos com fala. Aplica respiro assimétrico.

    Para cada silêncio (s_ini, s_fim):
      - o trecho de fala ANTES dele termina em s_ini + resp_out (cauda preservada)
      - o trecho de fala DEPOIS dele começa em s_fim - resp_in (ataque preservado)
    Começo (0) e fim (duracao) ficam intactos.
    """
    if not silencios:
        return [(0.0, duracao)]

    segmentos = []
    cursor = 0.0
    for (s_ini, s_fim) in silencios:
        fim_fala = min(s_ini + resp_out, duracao)
        if fim_fala > cursor:
            segmentos.append((cursor, fim_fala))
        cursor = max(s_fim - resp_in, fim_fala)
    if cursor < duracao:
        segmentos.append((cursor, duracao))
    # remove segmentos degenerados
    return [(a, b) for (a, b) in segmentos if b - a > 0.01]


def subtrair_descartes(segmentos, descartar):
    """Remove dos segmentos a manter os intervalos de takes descartadas.

    `descartar` é uma lista de (ini, fim) de tomadas ruins/repetidas. Cada um
    pode partir um segmento de fala em dois (descarte no meio), encurtá-lo (na
    ponta) ou eliminá-lo (descarte cobre o segmento inteiro). Roda o corte de
    take no MESMO passo do corte de silêncio — sem reencode extra.
    """
    if not descartar:
        return segmentos
    descartar = sorted(descartar)
    resultado = []
    for (a, b) in segmentos:
        pedacos = [(a, b)]
        for (d_ini, d_fim) in descartar:
            novos = []
            for (s, e) in pedacos:
                # sem sobreposição: pedaço intacto
                if d_fim <= s or d_ini >= e:
                    novos.append((s, e))
                    continue
                # sobra antes do descarte
                if d_ini > s:
                    novos.append((s, min(d_ini, e)))
                # sobra depois do descarte
                if d_fim < e:
                    novos.append((max(d_fim, s), e))
            pedacos = novos
        resultado.extend(pedacos)
    return [(a, b) for (a, b) in resultado if b - a > 0.01]


def montar_filter_complex(segmentos, alvo=None):
    """Gera filter_complex que recorta cada segmento (v+a) e concatena.

    Se `alvo` (dict com largura/altura) vier, NORMALIZA cada segmento de vídeo
    no mesmo passo: scale preservando proporção + pad (barras) + setsar=1. Assim
    o corte de silêncio e a normalização viram um reencode único — sem segunda
    geração de reencode. Sem `alvo`, preserva as specs do original.
    """
    norm = ""
    if alvo:
        W, H = alvo["largura"], alvo["altura"]
        norm = (f",scale={W}:{H}:force_original_aspect_ratio=decrease,"
                f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,setsar=1")
    partes = []
    labels = []
    for i, (a, b) in enumerate(segmentos):
        partes.append(
            f"[0:v]trim=start={a:.3f}:end={b:.3f},setpts=PTS-STARTPTS{norm}[v{i}];")
        partes.append(
            f"[0:a]atrim=start={a:.3f}:end={b:.3f},asetpts=PTS-STARTPTS[a{i}];")
        labels.append(f"[v{i}][a{i}]")
    n = len(segmentos)
    concat = "".join(labels) + f"concat=n={n}:v=1:a=1[vout][aout]"
    return "".join(partes) + concat


def otimizar_um(video, out_dir, noise, dur_min, resp_in, resp_out, crf, preset,
                alvo=None, descartar=None):
    descartar = descartar or []
    specs = ffprobe_specs(video)
    if specs["duracao"] is None:
        return {"origem": video, "erro": "não consegui ler a duração (ffprobe)"}

    silencios = detectar_silencios(video, noise, dur_min)
    segmentos = segmentos_a_manter(silencios, specs["duracao"], resp_in, resp_out)
    # corte de takes no mesmo passo: remove os intervalos descartados da fala.
    segmentos = subtrair_descartes(segmentos, descartar)

    nome = os.path.splitext(os.path.basename(video))[0]
    base = nome_saida_base(nome)  # TIPO_ID, sem ruído (BRUTA etc.)
    # com normalização, o container/ext vem do alvo; senão, preserva o original.
    ext = ("." + alvo["container"]) if alvo else (os.path.splitext(video)[1] or ".mp4")
    os.makedirs(out_dir, exist_ok=True)
    # o token de formato é SEMPRE o último (contrato da linha de produção): o
    # vídeo otimizado é o vertical, então sai com _OTIMIZADO_VERTICAL. A variante
    # quadrada (quadrado.py) troca _VERTICAL por _QUADRADO depois.
    saida = os.path.join(out_dir, f"{base}_OTIMIZADO_VERTICAL{ext}")

    if len(segmentos) <= 1 and not silencios and not descartar:
        # nada a cortar — ainda assim entrega cópia reencodada? Não: só avisa.
        return {"origem": video, "saida": None,
                "silencios": [], "segmentos": len(segmentos),
                "aviso": "nenhum silêncio interno ≥%.2fs detectado; nada a otimizar"
                         % dur_min}

    fc = montar_filter_complex(segmentos, alvo)
    # com alvo, o códec/fps/áudio são os do alvo; sem alvo, preserva o original.
    if alvo:
        venc = alvo["vcodec"]
        fps = str(alvo["fps"])
        ar = str(alvo["sample_rate"])
        ac = str(alvo["canais"])
    else:
        venc = encoder_para_codec(specs["vcodec"])
        fps = specs["fps"]
        ar = str(specs["sample_rate"])
        ac = str(specs["channels"])

    cmd = [
        "ffmpeg", "-y", "-i", video,
        "-filter_complex", fc, "-map", "[vout]", "-map", "[aout]",
        "-c:v", venc, "-crf", str(crf), "-preset", preset,
        "-pix_fmt", "yuv420p" if alvo else specs["pix_fmt"], "-r", fps,
    ]
    if venc == "libx265":
        cmd += ["-tag:v", "hvc1"]
    cmd += ["-c:a", "aac", "-ar", ar, "-ac", ac, saida]

    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        return {"origem": video, "erro": "ffmpeg falhou",
                "stderr": proc.stderr[-1500:]}

    # sidecar de roteiro: se houver <video>.md ao lado da entrada, propaga p/ a
    # saída casando o nome _OTIMIZADO. Não transcreve — só carrega adiante.
    sidecar_propagado = False
    md_entrada = os.path.splitext(video)[0] + ".md"
    if os.path.isfile(md_entrada):
        # o .md sai SEM token de formato (<base>_OTIMIZADO.md): um sidecar serve
        # vertical e quadrado do mesmo segmento (mesmo áudio/texto).
        md_saida = os.path.join(out_dir, f"{base}_OTIMIZADO.md")
        with open(md_entrada, encoding="utf-8") as f:
            conteudo_md = f.read()
        with open(md_saida, "w", encoding="utf-8") as f:
            f.write(conteudo_md)
        sidecar_propagado = True

    # verificação: silencedetect no resultado. Não pode sobrar silêncio >dur_min.
    # Pausas ~0.35–0.49 são o respiro preservado (silencedetect mede do
    # cruzamento de limiar, não da última sílaba) — esperado.
    residuais = detectar_silencios(saida, noise, dur_min)
    return {
        "origem": video,
        "saida": saida,
        "nome_saida": os.path.basename(saida),
        "silencios": len(silencios),
        "segmentos": len(segmentos),
        "takes_descartadas": len(descartar),
        "normalizado": bool(alvo),
        "sidecar_propagado": sidecar_propagado,
        "verificacao": {
            "silencios_residuais": len(residuais),
            "ok": len(residuais) == 0,
            "nota": "residuais>0 só é problema se forem pausas longas reais; "
                    "respiros ~0.35-0.49s não disparam em d=%.2f" % dur_min,
        },
    }


def coletar_videos(caminho):
    if os.path.isfile(caminho):
        return [caminho]
    vids = []
    for entry in sorted(os.listdir(caminho)):
        p = os.path.join(caminho, entry)
        if (os.path.isfile(p) and not entry.startswith(".")
                and os.path.splitext(entry)[1].lower() in VIDEO_EXT
                and "OTIMIZADO" not in entry.upper()):
            vids.append(p)
    return vids


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("entrada", help="arquivo de vídeo OU pasta (lote)")
    ap.add_argument("--out-dir", help="pasta de saída (padrão: OTIMIZADOS/ ao lado)")
    ap.add_argument("--modo-silencio", choices=list(MODOS_SILENCIO),
                    default="conservador",
                    help="o que conta como silêncio: conservador (-35dB/0.3s, "
                         "validado) ou justo (-33dB/0.15s, mais agressivo)")
    # se passados, sobrepõem o preset do --modo-silencio.
    ap.add_argument("--silence-noise", default=None)
    ap.add_argument("--silence-min", type=float, default=None)
    ap.add_argument("--modo-respiro", choices=list(MODOS_RESPIRO),
                    default="conservador",
                    help="margem nas bordas: conservador (0.10/0.25, validado) "
                         "ou justo (0.05/0.18, corte mais apertado)")
    # se passados, sobrepõem o preset do --modo-respiro (ponta a ponta, em segundos).
    ap.add_argument("--respiro-entrada", type=float, default=None)
    ap.add_argument("--respiro-saida", type=float, default=None)
    ap.add_argument("--descartar", default="",
                    help='intervalos de takes a remover: "ini-fim,ini-fim" (segundos). '
                         "Só para arquivo único.")
    ap.add_argument("--crf", type=int, default=20)
    ap.add_argument("--preset", default="medium")
    # Normalização (opcional). Se QUALQUER uma destas vier, a otimizadora
    # normaliza no mesmo reencode. Sem elas, preserva as specs do original.
    ap.add_argument("--normalizar", action="store_true",
                    help="normaliza para o alvo (default FHD vertical) no mesmo passo")
    ap.add_argument("--largura", type=int, default=1080)
    ap.add_argument("--altura", type=int, default=1920)
    ap.add_argument("--fps", default="30")
    ap.add_argument("--vcodec", default="libx265",
                    help="libx265 (HEVC) ou libx264 (H.264)")
    ap.add_argument("--container", default="mp4", help="mp4 ou mov")
    ap.add_argument("--sample-rate", default="48000")
    ap.add_argument("--canais", type=int, default=2)
    args = ap.parse_args()

    # respiro: o --modo-respiro define o preset; --respiro-* sobrepõe ponta a ponta.
    resp_in = args.respiro_entrada if args.respiro_entrada is not None \
        else MODOS_RESPIRO[args.modo_respiro]["entrada"]
    resp_out = args.respiro_saida if args.respiro_saida is not None \
        else MODOS_RESPIRO[args.modo_respiro]["saida"]
    # silêncio: o --modo-silencio define o preset; --silence-* sobrepõe cada um.
    noise = args.silence_noise if args.silence_noise is not None \
        else MODOS_SILENCIO[args.modo_silencio]["noise"]
    smin = args.silence_min if args.silence_min is not None \
        else MODOS_SILENCIO[args.modo_silencio]["min"]

    # parse de --descartar "ini-fim,ini-fim"
    descartar = []
    if args.descartar.strip():
        for par in args.descartar.split(","):
            par = par.strip()
            if not par:
                continue
            try:
                ini, fim = par.split("-")
                descartar.append((float(ini), float(fim)))
            except ValueError:
                print(json.dumps({"erro": f"intervalo inválido em --descartar: '{par}' "
                                          "(esperado ini-fim, ex.: 12.3-18.9)"}))
                sys.exit(1)

    alvo = None
    if args.normalizar:
        alvo = {
            "largura": args.largura, "altura": args.altura, "fps": args.fps,
            "vcodec": args.vcodec, "container": args.container,
            "sample_rate": args.sample_rate, "canais": args.canais,
        }

    entrada = os.path.abspath(args.entrada)
    if not os.path.exists(entrada):
        print(json.dumps({"erro": f"não existe: {entrada}"}))
        sys.exit(1)

    videos = coletar_videos(entrada)
    if not videos:
        print(json.dumps({"erro": "nenhum vídeo encontrado"}))
        sys.exit(1)

    # descartes de take só fazem sentido para um arquivo único — cada vídeo tem
    # seus próprios intervalos. Em lote, ignoramos e avisamos.
    aviso_lote = None
    if descartar and len(videos) > 1:
        aviso_lote = ("--descartar ignorado: vale só para arquivo único, não lote "
                      "(cada vídeo tem seus próprios intervalos de take)")
        descartar = []

    # pasta-irmã da entrada: 02_OTIMIZADOS é etapa da linha de produção, irmã de
    # 01_Brutas (fonte) e não subpasta da entrada.
    base = entrada if os.path.isdir(entrada) else os.path.dirname(entrada)
    base = os.path.dirname(os.path.abspath(base.rstrip("/"))) \
        if os.path.basename(os.path.abspath(base.rstrip("/"))).upper().startswith("01_") \
        else os.path.abspath(base)
    out_dir = os.path.abspath(args.out_dir) if args.out_dir \
        else os.path.join(base, "02_OTIMIZADOS")

    resultados = []
    for v in videos:
        resultados.append(otimizar_um(
            v, out_dir, noise, smin,
            resp_in, resp_out, args.crf, args.preset,
            alvo, descartar))

    saida_json = {"out_dir": out_dir, "resultados": resultados, "alvo": alvo,
                  "modo_respiro": args.modo_respiro,
                  "respiros": {"entrada": resp_in, "saida": resp_out},
                  "modo_silencio": args.modo_silencio,
                  "silencio": {"noise": noise, "min": smin}}
    if aviso_lote:
        saida_json["aviso"] = aviso_lote
    print(json.dumps(saida_json, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
