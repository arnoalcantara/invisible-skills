#!/usr/bin/env python3
"""descobrir_cortes.py — descobre os SEGMENTOS de um projeto (N segmentos, nomes livres).

Uma "peça" final é a concatenação ordenada de um corte de cada segmento escolhido:
gancho → desenvolvimento → CTA, ou para uma VSL lead → história → oferta →
fechamento, ou qualquer cadeia que o usuário montar.

Um segmento é um grupo de cortes. Os cortes podem estar organizados de DOIS jeitos,
e a skill cobre os dois (mais o explícito):

  A) SUBPASTAS — cada segmento é uma subpasta (GANCHOS/, DESENVOLVIMENTOS/...).
  B) MESMA PASTA — todos os cortes soltos numa pasta só, distinguidos pelo NOME:
     o nome sempre carrega o RÓTULO da sessão (GANCHO, DESENVOLVIMENTO...) e o
     CÓDIGO/número (19, VAV19...), em qualquer ordem. Ex.: VAV19_GANCHO.mp4,
     DESENVOLVIMENTO_VAV19.mov, gancho-28.mp4.

A skill NÃO trava em GANCHOS/DESENVOLVIMENTOS. O rótulo é detectado por
palavra-chave conhecida (PADROES_CONHECIDOS) ou por rótulos que o usuário declarar
em --rotulos. O CÓDIGO é extraído à parte e serve para (a) nomenclatura de saída e
(b) casar os pares NATIVOS — cortes de segmentos diferentes com o mesmo código
vieram do mesmo vídeo de origem.

Modos:
  - auto:  varre <projeto>. Se houver subpastas com vídeo → modo A. Senão, se
           houver vídeos soltos → modo B (agrupa por rótulo no nome).
  - --segmentos d1 d2 ...     → modo A explícito, na ordem dada (ordem de concat).
  - --mesma-pasta <pasta>     → força o modo B numa pasta específica.
  - --rotulos GANCHO DESENV...→ rótulos extras/ordem para o modo B (nomes livres).

Uso:
    python3 descobrir_cortes.py <pasta_projeto>
        [--segmentos <dir1> <dir2> ...]
        [--mesma-pasta <pasta>] [--rotulos <ROT1> <ROT2> ...]

Saída (stdout): JSON
    {
      "projeto": "...", "modo": "subpastas|mesma_pasta",
      "segmentos": [
        {"nome": "GANCHO", "dir": "...", "padrao_conhecido": "gancho",
         "cortes": [{"codigo": "VAV19",
                     "formatos": {
                       "VERTICAL": {"base": "<path|null>", "vars": {"1": "<path>"}},
                       "QUADRADO": {"base": "<path|null>", "vars": {}}}}]},
        ...
      ],
      "subpastas_ignoradas": [...],
      "sem_rotulo": [...]   # (modo B) arquivos cujo rótulo não foi reconhecido
    }
Nem o formato (_VERTICAL/_QUADRADO) nem a variação (_VAR<n>) viram corte novo: são
variantes do MESMO corte (mesmo código, mesmo áudio/texto). A matriz retórica é
julgada UMA vez (no VERTICAL base) e a expansão formato×VAR acontece só ao combinar.
A ORDEM da lista "segmentos" é a ordem de concatenação proposta.

Na linha de produção, o combinador lê a pasta 03_PREPARADOS no modo MESMA PASTA
(ganchos e desenvolvimentos prontos, soltos, identificados pelo rótulo no nome).
"""
import argparse
import json
import os
import re
import sys

VIDEO_EXT = {".mp4", ".mov", ".mkv", ".m4v", ".avi", ".webm"}

# rótulos-padrão conhecidos -> forma singular (só para SUGERIR; não restringe).
PADROES_CONHECIDOS = {
    "GANCHO": "gancho", "GANCHOS": "gancho",
    "DESENVOLVIMENTO": "desenvolvimento", "DESENVOLVIMENTOS": "desenvolvimento",
    "CTA": "cta", "CTAS": "cta",
    "LEAD": "lead", "LEADS": "lead",
    "HISTORIA": "historia", "HISTORIAS": "historia",
    "OFERTA": "oferta", "OFERTAS": "oferta",
    "FECHAMENTO": "fechamento", "FECHAMENTOS": "fechamento",
    "PROVA": "prova", "PROVAS": "prova",
}

ORDEM_RETORICA = ["gancho", "lead", "desenvolvimento", "historia",
                  "prova", "oferta", "cta", "fechamento"]

RE_CODIGO = re.compile(r"[A-Z]{2,5}\d{1,4}", re.IGNORECASE)
# número solto (ex.: "28") como código alternativo, quando não há VAVxx.
# Delimitado por não-dígito (ou pontas), tolerando _ - . como separador — \b
# falha entre "_" e dígito porque "_" conta como caractere de palavra.
RE_NUM = re.compile(r"(?<!\d)(\d{1,4})(?!\d)")
# sufixos de processamento que não são rótulo de segmento.
RUIDO = {"OTIMIZADO", "VERTICAL", "HORIZONTAL", "FINAL", "RAW", "QUADRADO", "LEGENDADO"}

RE_VAR = re.compile(r"(?i)VAR(\d+)")


def formato_de(base):
    """Token de formato do corte: 'QUADRADO', 'VERTICAL' ou 'VERTICAL' (default).

    O contrato da linha põe o formato como último token. Na ausência de token,
    assume VERTICAL (o formato canônico)."""
    toks = [t.upper() for t in tokens(base)]
    if "QUADRADO" in toks:
        return "QUADRADO"
    return "VERTICAL"


def var_de(base):
    """Número da variação (_VAR<n>) ou None se for o corte base."""
    m = RE_VAR.search(base)
    return int(m.group(1)) if m else None


def parear_variantes(crus):
    """Agrupa as variantes de cada corte por código e por formato.

    `crus` é uma lista de dicts {codigo, arquivo, formato, var} na ordem de
    descoberta. Nem o formato nem a variação são cortes retóricos novos: são
    variantes do MESMO corte (mesmo código, mesmo áudio/texto). Casa por código e
    expõe, por formato, o clipe base e o dicionário de VARs:

        {"codigo": "VAV19",
         "formatos": {
            "VERTICAL": {"base": <path|None>, "vars": {1: <path>, 2: <path>}},
            "QUADRADO": {"base": <path|None>, "vars": {1: <path>}}}}

    A matriz retórica é julgada UMA vez (no VERTICAL base) e vale pra todas as
    variantes; a expansão (formato × VAR) acontece só na hora de combinar.
    """
    porcodigo = {}
    ordem = []
    for c in crus:
        cod = c["codigo"]
        if cod not in porcodigo:
            porcodigo[cod] = {}
            ordem.append(cod)
        fmt = c["formato"]
        slot = porcodigo[cod].setdefault(fmt, {"base": None, "vars": {}})
        if c["var"] is None:
            slot["base"] = slot["base"] or c["arquivo"]
        else:
            slot["vars"].setdefault(c["var"], c["arquivo"])
    return [{"codigo": cod, "formatos": porcodigo[cod]} for cod in ordem]


def extrair_codigo(base):
    m = RE_CODIGO.search(base)
    if m:
        return m.group(0).upper()
    m = RE_NUM.search(base)
    return m.group(1) if m else base


def padrao_de(rotulo):
    return PADROES_CONHECIDOS.get(rotulo.upper())


def tokens(base):
    """Quebra o nome em tokens alfabéticos/numéricos, separadores _ - . espaço."""
    return [t for t in re.split(r"[_\-.\s]+", base) if t]


def detectar_rotulo(base, rotulos_validos):
    """Acha o rótulo de segmento no nome do arquivo.

    rotulos_validos: dict UPPER->forma_singular (conhecidos + declarados).
    Procura um token que case com um rótulo válido. Ignora código e ruído.
    Retorna (rotulo_singular, rotulo_exibicao) ou (None, None).
    """
    for t in tokens(base):
        tu = t.upper()
        if tu in RUIDO:
            continue
        if tu in rotulos_validos:
            return rotulos_validos[tu], tu
    return None, None


def listar_cortes_subpasta(pasta):
    crus = []
    if not pasta or not os.path.isdir(pasta):
        return []
    for entry in sorted(os.listdir(pasta)):
        caminho = os.path.join(pasta, entry)
        if not os.path.isfile(caminho) or entry.startswith("."):
            continue
        base, ext = os.path.splitext(entry)
        if ext.lower() not in VIDEO_EXT:
            continue
        crus.append({"codigo": extrair_codigo(base), "arquivo": caminho,
                     "formato": formato_de(base), "var": var_de(base)})
    return parear_variantes(crus)


def montar_segmento_subpasta(caminho_pasta):
    nome = os.path.basename(os.path.normpath(caminho_pasta))
    return {
        "nome": nome,
        "dir": os.path.abspath(caminho_pasta),
        "padrao_conhecido": padrao_de(nome),
        "cortes": listar_cortes_subpasta(caminho_pasta),
    }


def agrupar_mesma_pasta(pasta, rotulos_extra):
    """Modo B: agrupa os vídeos soltos de uma pasta por rótulo detectado no nome."""
    # rótulos válidos = conhecidos + os declarados pelo usuário (nomes livres).
    validos = dict(PADROES_CONHECIDOS)
    ordem_extra = []
    for r in rotulos_extra or []:
        validos[r.upper()] = r.lower()
        ordem_extra.append(r.lower())

    grupos = {}          # singular -> {"exibicao":..., "crus":[...]}
    sem_rotulo = []
    for entry in sorted(os.listdir(pasta)):
        caminho = os.path.join(pasta, entry)
        if not os.path.isfile(caminho) or entry.startswith("."):
            continue
        base, ext = os.path.splitext(entry)
        if ext.lower() not in VIDEO_EXT:
            continue
        singular, exib = detectar_rotulo(base, validos)
        if singular is None:
            sem_rotulo.append(caminho)
            continue
        g = grupos.setdefault(singular, {"exibicao": exib, "crus": []})
        g["crus"].append({"codigo": extrair_codigo(base), "arquivo": caminho,
                          "formato": formato_de(base), "var": var_de(base)})

    segmentos = []
    for singular, g in grupos.items():
        segmentos.append({
            "nome": g["exibicao"],
            "dir": os.path.abspath(pasta),   # todos na mesma pasta
            "padrao_conhecido": singular if singular in PADROES_CONHECIDOS.values()
                                else None,
            "cortes": parear_variantes(g["crus"]),   # variantes por formato/VAR
        })

    # ordena: ordem retórica conhecida primeiro, depois ordem dos --rotulos, depois alfabético
    def chave(seg):
        s = seg["padrao_conhecido"]
        nome_low = seg["nome"].lower()
        if s in ORDEM_RETORICA:
            return (0, ORDEM_RETORICA.index(s), nome_low)
        if nome_low in ordem_extra:
            return (1, ordem_extra.index(nome_low), nome_low)
        return (2, 0, nome_low)
    segmentos.sort(key=chave)
    return segmentos, sem_rotulo


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("projeto")
    ap.add_argument("--segmentos", nargs="+",
                    help="modo SUBPASTAS explícito: lista ORDENADA de pastas")
    ap.add_argument("--mesma-pasta",
                    help="força o modo MESMA PASTA nesta pasta (cortes soltos)")
    ap.add_argument("--rotulos", nargs="+",
                    help="rótulos de segmento extras/ordem para o modo mesma pasta "
                         "(nomes livres; ex.: GANCHO DESENVOLVIMENTO OFERTA)")
    args = ap.parse_args()

    projeto = os.path.abspath(args.projeto)
    if not os.path.isdir(projeto):
        print(json.dumps({"erro": f"pasta não existe: {projeto}"}))
        sys.exit(1)

    # 1) modo mesma-pasta forçado
    if args.mesma_pasta:
        pasta = (args.mesma_pasta if os.path.isabs(args.mesma_pasta)
                 else os.path.join(projeto, args.mesma_pasta))
        if not os.path.isdir(pasta):
            print(json.dumps({"erro": f"--mesma-pasta não é pasta: {pasta}"}))
            sys.exit(1)
        segmentos, sem_rotulo = agrupar_mesma_pasta(pasta, args.rotulos)
        print(json.dumps({"projeto": projeto, "modo": "mesma_pasta",
                          "segmentos": segmentos, "subpastas_ignoradas": [],
                          "sem_rotulo": sem_rotulo}, ensure_ascii=False, indent=2))
        return

    # 2) modo subpastas explícito
    if args.segmentos:
        segmentos = []
        for s in args.segmentos:
            p = s if os.path.isabs(s) else os.path.join(projeto, s)
            if not os.path.isdir(p):
                print(json.dumps({"erro": f"segmento não é pasta: {p}"}))
                sys.exit(1)
            segmentos.append(montar_segmento_subpasta(p))
        print(json.dumps({"projeto": projeto, "modo": "subpastas",
                          "segmentos": segmentos, "subpastas_ignoradas": [],
                          "sem_rotulo": []}, ensure_ascii=False, indent=2))
        return

    # 3) auto: subpastas com vídeo? então modo A. Senão, vídeos soltos → modo B.
    subpastas = []
    ignoradas = []
    tem_video_solto = False
    for entry in sorted(os.listdir(projeto)):
        p = os.path.join(projeto, entry)
        if entry.startswith("."):
            continue
        if os.path.isdir(p):
            seg = montar_segmento_subpasta(p)
            if seg["cortes"]:
                subpastas.append(seg)
            else:
                ignoradas.append(entry)
        elif (os.path.isfile(p)
              and os.path.splitext(entry)[1].lower() in VIDEO_EXT):
            tem_video_solto = True

    if subpastas:
        def chave(seg):
            pk = seg["padrao_conhecido"]
            return (ORDEM_RETORICA.index(pk) if pk in ORDEM_RETORICA else 99,
                    seg["nome"].upper())
        subpastas.sort(key=chave)
        print(json.dumps({"projeto": projeto, "modo": "subpastas",
                          "segmentos": subpastas, "subpastas_ignoradas": ignoradas,
                          "sem_rotulo": []}, ensure_ascii=False, indent=2))
        return

    if tem_video_solto:
        segmentos, sem_rotulo = agrupar_mesma_pasta(projeto, args.rotulos)
        print(json.dumps({"projeto": projeto, "modo": "mesma_pasta",
                          "segmentos": segmentos, "subpastas_ignoradas": ignoradas,
                          "sem_rotulo": sem_rotulo}, ensure_ascii=False, indent=2))
        return

    print(json.dumps({"projeto": projeto, "modo": "vazio", "segmentos": [],
                      "subpastas_ignoradas": ignoradas, "sem_rotulo": []},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
