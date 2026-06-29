#!/usr/bin/env python3
"""render_html.py — motor de render HTML->PNG para carrosséis de estilo tipográfico/UI.

Para estilos cuja identidade é tipografia sobre fundo chapado dentro de uma moldura
de UI (ex.: "app de Notas do iOS"), o render correto NÃO é imagem generativa: é
HTML/CSS renderizado em PNG por um navegador headless. Vantagens sobre o motor
Higgsfield para esses estilos: pixel-perfeito, texto sempre correto (zero alucinação),
custo zero por slide, e 100% reproduzível.

Este script é GENÉRICO no texto: a moldura/estética é fixa por ESTILO (um template
embutido), e o conteúdo de cada card vem de um ROTEIRO (JSON). Trocar o texto do
roteiro troca o carrossel; a estética é a do estilo escolhido.

Estilos suportados (template embutido):
  - notes      : mockup do app Notas do iOS (validado à mão, fiel à referência).
  - tweet_card : print de tweet do X (Twitter), sub-modo sólido (fundo branco/preto).

Contrato do ROTEIRO (JSON):
{
  "estilo": "notes" | "tweet_card",
  "ratio": "4x5" | "1x1",                      # default 4x5
  "cards": [ ... ]                             # campos do card dependem do estilo
}

--- Campos do card por estilo ---

ESTILO "notes":
{
  "papel": "capa" | "interno" | "fecho",
  "tema": "dark" | "light",                    # opcional; default por papel
  // CAPA / FECHO:
  "titulo": "texto antes do destaque (pode ter \\n p/ quebra)",
  "destaque": "frase destacada (pode ter \\n)",   # ganha o bloco de seleção + carets
  "cta": "linha pequena opcional (ex.: 'Faça isso aqui 👉')",
  // INTERNO (blocos livres; cada bloco vira um parágrafo da nota):
  "blocos": [
    {"emoji": "❌", "label": "NÃO DIGA:", "texto": "..."},
    {"texto": "parágrafo simples sem label"}
  ]
}

ESTILO "tweet_card" (cabeçalho editável; tweet é layout único, sem papel):
{
  "tema": "dark" | "light",                    # opcional; default light
  "nome": "Arno Alcântara",                    # nome de exibição (bold)
  "handle": "arnoalcantara",                   # @ é adicionado automaticamente
  "avatar": "/caminho/local/foto.jpg",         # opcional; embutida via base64.
                                               #   sem foto -> círculo com a inicial do nome
  "verificado": true,                          # opcional; default true (selo azul do X)
  "data": "16 de fev. de 2018",                # opcional; default ausente
  "texto": "corpo do tweet (\\n\\n separa parágrafos)"
}

Uso:
    python3 render_html.py --roteiro roteiro.json --out-dir ./cards [--chrome "/path/Chrome"]

Saída (stdout): JSON {ok, cards:[{file, papel, ratio, w, h}], erros:[...]}.
Requer: um Chrome/Chromium para o modo headless (auto-detecta no macOS/Linux).
"""
import argparse
import base64
import html as _html
import json
import os
import shutil
import subprocess
import sys
import tempfile


# ----------------------------------------------------------------------------
# Localiza um Chrome/Chromium para render headless.
# ----------------------------------------------------------------------------
def achar_chrome(explicito=None):
    if explicito and os.path.exists(explicito):
        return explicito
    candidatos = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    ]
    for c in candidatos:
        if os.path.exists(c):
            return c
    for nome in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome"):
        p = shutil.which(nome)
        if p:
            return p
    return None


# ----------------------------------------------------------------------------
# ESTILO "notes" — CSS + montagem de HTML (portado do método validado à mão).
# A moldura é idêntica em todo slide; o conteúdo vem do roteiro.
# ----------------------------------------------------------------------------
NOTES_CSS = r"""
* { margin:0; padding:0; box-sizing:border-box; }
html,body { background:#444; }
.card { position:relative; overflow:hidden;
  font-family:-apple-system,"SF Pro Text","SF Pro Display","Helvetica Neue",Helvetica,Arial,sans-serif;
  -webkit-font-smoothing:antialiased; text-rendering:geometricPrecision; }
.card.r45 { width:1080px; height:1350px; }
.card.r11 { width:1080px; height:1080px; }
.card.dark { background:#000; }
.card.light { background:#ececec; }
.dark .title { color:#fff; } .light .title { color:#1c1c1e; }
.dark .cta { color:#fff; } .light .cta { color:#1c1c1e; }

.topbar { position:absolute; top:60px; left:0; right:0; display:flex; align-items:center; justify-content:space-between; padding:0 52px; }
.nav-back { display:flex; align-items:center; gap:4px; font-size:42px; font-weight:400; }
.dark .nav-back { color:#e3b13c; } .light .nav-back { color:#1c1c1e; }
.nav-back .chev { font-size:50px; font-weight:500; line-height:.9; margin-top:-4px; }
.nav-right { display:flex; align-items:center; gap:24px; }
.pill { border-radius:44px; display:flex; align-items:center; gap:40px; padding:20px 38px; }
.dark .pill { background:#1c1c1e; } .light .pill { background:#fff; }
.pill .ic svg { width:42px; height:42px; display:block; }
.dark .pill .ic svg { stroke:#cfcfcf; } .light .pill .ic svg { stroke:#1c1c1e; }
.dark .pill .ic.dots circle { fill:#cfcfcf; } .light .pill .ic.dots circle { fill:#1c1c1e; }
.check { width:84px; height:84px; border-radius:50%; background:#e3b13c; display:flex; align-items:center; justify-content:center; }
.check svg { width:46px; height:46px; }
.backbtn { width:84px; height:84px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:48px; font-weight:500; }
.dark .backbtn { background:#1c1c1e; color:#fff; } .light .backbtn { background:#fff; color:#1c1c1e; }

.body { position:absolute; left:120px; right:120px; text-align:left; }
.body.cover { top:300px; } .body.closer { top:300px; }
.body.inner { top:190px; bottom:190px; display:flex; flex-direction:column; justify-content:center; padding:0 24px; }
.title { font-size:100px; font-weight:400; line-height:1.05; letter-spacing:-2px; }
.body.inner .title { font-size:62px; line-height:1.12; }

.sel { display:inline; font-weight:700; box-decoration-break:clone; -webkit-box-decoration-break:clone; padding:1px 12px; line-height:1.34; }
.dark .sel { background:#42350d; color:#f4e8bc; }
.light .sel { background:#e7cf63; color:#1c1408; }
.selwrap { position:relative; margin-top:12px; display:inline-block; max-width:100%; }

/* carets de seleção do iOS: linha fina vertical amarela + bolinha na ponta */
.caret-start, .caret-end { position:absolute; z-index:6; display:flex; flex-direction:column; align-items:center; }
.caret-start .bar, .caret-end .bar { background:#dcb13e; width:4px; display:block; border-radius:2px; height:calc(1.21em - 3px); }
.caret-start .dot, .caret-end .dot { width:18px; height:18px; border-radius:50%; background:#dcb13e; display:block; }
.caret-start { top:-0.07em; left:-10px; }
.caret-start .dot { margin-bottom:-2px; }
.end-anchor { position:relative; display:inline; }
.caret-end { left:4px; bottom:-0.14em; }
.caret-end .bar { order:1; } .caret-end .dot { order:2; margin-top:-2px; }

.cta { font-size:44px; font-weight:400; }
.body.cover .cta { margin-top:40px; }

.iblock { margin-bottom:50px; font-size:56px; line-height:1.2; font-weight:400; }
.iblock:last-child { margin-bottom:0; }
.ilabel { font-weight:700; }
.dark .iblock { color:#fff; } .light .iblock { color:#1c1c1e; }
.iblock .emoji { margin-right:10px; }

.toolbar { position:absolute; left:60px; right:60px; bottom:90px; border-radius:46px; display:flex; align-items:center; justify-content:space-between; padding:26px 56px; }
.dark .toolbar { background:#1c1c1e; } .light .toolbar { background:#fff; }
.toolbar .ic svg { width:50px; height:50px; display:block; }
.dark .toolbar .ic svg { stroke:#d9d9d9; } .light .toolbar .ic svg { stroke:#1c1c1e; }
.aa { font-size:48px; font-weight:600; font-family:"SF Pro Display",-apple-system,sans-serif; }
.dark .aa { color:#fff; } .light .aa { color:#1c1c1e; }

/* overrides 1:1 (canvas mais curto) */
.r11 .body.cover { top:210px; } .r11 .body.inner { top:200px; bottom:170px; } .r11 .body.closer { top:230px; }
.r11 .title { font-size:88px; letter-spacing:-1.5px; }
.r11 .body.inner .title { font-size:54px; }
.r11 .iblock { font-size:50px; margin-bottom:42px; }
.r11 .cta { font-size:40px; } .r11 .body.cover .cta { margin-top:30px; }
.r11 .toolbar { bottom:64px; }
"""

# SVGs da moldura do app Notas
_IC_UNDO = '<span class="ic"><svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 14 4 9l5-5"/><path d="M4 9h11a6 6 0 0 1 0 12h-1"/></svg></span>'
_IC_SHARE = '<span class="ic"><svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 16V4"/><path d="m7 9 5-5 5 5"/><path d="M5 13v6a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-6"/></svg></span>'
_IC_DOTS = '<span class="ic dots"><svg viewBox="0 0 24 24"><circle cx="5" cy="12" r="2.1"/><circle cx="12" cy="12" r="2.1"/><circle cx="19" cy="12" r="2.1"/></svg></span>'
_IC_CHECK = '<div class="check"><svg viewBox="0 0 24 24" fill="none" stroke="#1c1408" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg></div>'
_TB_AA = '<span class="aa">Aa</span>'
_TB_LIST = '<span class="ic"><svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round"><circle cx="4.5" cy="7" r="1.8" fill="currentColor" stroke="none"/><circle cx="4.5" cy="17" r="1.8"/><path d="M9.5 7h10M9.5 17h10"/></svg></span>'
_TB_TABLE = '<span class="ic"><svg viewBox="0 0 24 24" fill="none" stroke-width="2"><rect x="3.5" y="5" width="17" height="14" rx="1.5"/><path d="M3.5 10.3h17M3.5 14.6h17M9 5v14M15 5v14"/></svg></span>'
_TB_CLIP = '<span class="ic"><svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m20 9-9 9a4.2 4.2 0 0 1-6-6l8.5-8.5a2.8 2.8 0 0 1 4 4l-8 8a1.4 1.4 0 0 1-2-2l7.2-7.2"/></svg></span>'
_TB_PEN = '<span class="ic"><svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M15.5 8.5 9 15l-2.2.7.7-2.2 6.5-6.5a1.1 1.1 0 0 1 1.5 1.5z"/></svg></span>'

# papel -> tema default (capa dark, interno/fecho light) — espelha as refs Notes
_NOTES_TEMA_DEFAULT = {"capa": "dark", "interno": "light", "fecho": "light"}


def _nl2br(s):
    """Escapa HTML e converte \\n em <br>."""
    return "<br>".join(_html.escape(part) for part in str(s).split("\n"))


def _topbar(papel):
    if papel == "capa":
        left = '<div class="nav-back"><span class="chev">‹</span><span>Notas</span></div>'
    else:
        left = '<div class="backbtn">‹</div>'
    return (f'<div class="topbar">{left}<div class="nav-right">'
            f'<div class="pill">{_IC_UNDO}{_IC_SHARE}{_IC_DOTS}</div>{_IC_CHECK}</div></div>')


_TOOLBAR = f'<div class="toolbar">{_TB_AA}{_TB_LIST}{_TB_TABLE}{_TB_CLIP}{_TB_PEN}</div>'


def _sel(destaque):
    """Bloco de seleção + carets (linha fina + bolinha) nas pontas."""
    inner = _nl2br(destaque)
    return ('<span class="caret-start"><span class="dot"></span><span class="bar"></span></span>'
            f'<span class="sel">{inner}'
            '<span class="end-anchor"><span class="caret-end"><span class="bar"></span><span class="dot"></span></span></span>'
            '</span>')


def _body_notes(card):
    papel = card.get("papel", "interno")
    if papel in ("capa", "fecho"):
        parts = []
        if card.get("titulo"):
            parts.append(f'<div class="title">{_nl2br(card["titulo"])}</div>')
        if card.get("destaque"):
            parts.append(f'<div class="selwrap title">{_sel(card["destaque"])}</div>')
        if card.get("cta"):
            parts.append(f'<div class="cta">{_nl2br(card["cta"])}</div>')
        role_cls = "cover" if papel == "capa" else "closer"
        return role_cls, "".join(parts)
    # interno: blocos livres
    blocos = []
    for b in card.get("blocos", []):
        emoji = f'<span class="emoji">{_html.escape(b["emoji"])}</span>' if b.get("emoji") else ""
        label = f'<span class="ilabel">{_html.escape(b["label"])}</span> ' if b.get("label") else ""
        texto = _nl2br(b.get("texto", ""))
        blocos.append(f'<div class="iblock">{emoji}{label}{texto}</div>')
    return "inner", "".join(blocos)


def montar_html_notes(card, ratio):
    papel = card.get("papel", "interno")
    tema = card.get("tema") or _NOTES_TEMA_DEFAULT.get(papel, "light")
    rcls = "r45" if ratio == "4x5" else "r11"
    role_cls, body = _body_notes(card)
    return (f'<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8">'
            f'<style>{NOTES_CSS}</style></head><body>'
            f'<div class="card {tema} {rcls}">{_topbar(papel)}'
            f'<div class="body {role_cls}">{body}</div>{_TOOLBAR}</div></body></html>')


# ----------------------------------------------------------------------------
# ESTILO "tweet_card" — print de tweet do X (Twitter), sub-modo sólido.
# Cabeçalho editável (avatar/nome/selo/handle/data); corpo grande centralizado.
# Cores oficiais do X amostradas das refs. (validado à mão, fiel à referência)
# ----------------------------------------------------------------------------
TWEET_CSS = r"""
* { margin:0; padding:0; box-sizing:border-box; }
html,body { background:#444; }
.card { position:relative; overflow:hidden;
  font-family:-apple-system,"SF Pro Text","SF Pro Display","Helvetica Neue",Helvetica,Arial,sans-serif;
  -webkit-font-smoothing:antialiased; text-rendering:geometricPrecision; }
.card.r45 { width:1080px; height:1350px; }
.card.r11 { width:1080px; height:1080px; }
.card.light { background:#fff; } .card.dark { background:#000; }

.tweet { position:absolute; left:96px; right:96px; top:50%; transform:translateY(-50%); }

.head { display:flex; align-items:center; gap:28px; margin-bottom:44px; }
.avatar { width:124px; height:124px; border-radius:50%; flex:0 0 124px; object-fit:cover;
  display:flex; align-items:center; justify-content:center; font-size:54px; font-weight:600; color:#fff; }
.idcol { display:flex; flex-direction:column; justify-content:center; min-width:0; }
.nameline { display:flex; align-items:center; gap:12px; }
.name { font-size:52px; font-weight:700; letter-spacing:-0.5px; line-height:1.05; }
.light .name { color:#0f1419; } .dark .name { color:#e7e9ea; }
.badge { width:44px; height:44px; flex:0 0 44px; }
.handle { font-size:42px; font-weight:400; margin-top:4px; }
.light .handle { color:#536471; } .dark .handle { color:#71767b; }
.date { font-size:36px; font-weight:400; margin-top:6px; }
.light .date { color:#536471; } .dark .date { color:#71767b; }

.tbody { font-size:74px; font-weight:400; line-height:1.22; letter-spacing:-0.5px; }
.light .tbody { color:#0f1419; } .dark .tbody { color:#fff; }
.tbody p { margin:0; } .tbody p + p { margin-top:0.9em; }

.r11 .tbody { font-size:64px; }
"""

# selo verificado do X (badge azul com check branco)
_X_BADGE = ('<svg class="badge" viewBox="0 0 24 24" aria-label="Verificado">'
            '<path fill="#1d9bf0" d="M22.25 12c0-1.43-.88-2.67-2.19-3.34.46-1.39.2-2.9-.81-3.91s-2.52-1.27-3.91-.81c-.66-1.31-1.91-2.19-3.34-2.19s-2.67.88-3.33 2.19c-1.4-.46-2.91-.2-3.92.81s-1.26 2.52-.8 3.91c-1.31.67-2.2 1.91-2.2 3.34s.89 2.67 2.2 3.34c-.46 1.39-.21 2.9.8 3.91s2.52 1.26 3.91.81c.67 1.31 1.91 2.19 3.34 2.19s2.68-.88 3.34-2.19c1.39.45 2.9.2 3.91-.81s1.27-2.52.81-3.91c1.31-.67 2.19-1.91 2.19-3.34z"/>'
            '<path fill="#fff" d="m9.8 17.3-4.4-4.4 1.6-1.6 2.8 2.8 6.2-6.2 1.6 1.6z"/>'
            '</svg>')

# cor de fundo do avatar de fallback (sem foto), por tema
_TWEET_FALLBACK_BG = {"light": "#536471", "dark": "#3a3b3c"}


def _avatar_tweet(card, tema):
    foto = card.get("avatar")
    if foto and os.path.exists(foto):
        ext = os.path.splitext(foto)[1].lstrip(".").lower() or "png"
        if ext == "jpg":
            ext = "jpeg"
        with open(foto, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        return f'<img class="avatar" src="data:image/{ext};base64,{b64}">'
    nome = (card.get("nome") or "?").strip()
    inicial = nome[0].upper() if nome else "?"
    bg = _TWEET_FALLBACK_BG.get(tema, "#536471")
    return f'<div class="avatar" style="background:{bg}">{_html.escape(inicial)}</div>'


def _body_tweet(texto):
    paras = str(texto).split("\n\n")
    return "".join("<p>" + _nl2br(p) + "</p>" for p in paras)


def montar_html_tweet(card, ratio):
    tema = card.get("tema") or "light"
    rcls = "r45" if ratio == "4x5" else "r11"
    badge = _X_BADGE if card.get("verificado", True) else ""
    date = f'<div class="date">{_html.escape(str(card["data"]))}</div>' if card.get("data") else ""
    head = (f'<div class="head">{_avatar_tweet(card, tema)}'
            f'<div class="idcol"><div class="nameline">'
            f'<span class="name">{_html.escape(card.get("nome",""))}</span>{badge}</div>'
            f'<div class="handle">@{_html.escape(str(card.get("handle","")).lstrip("@"))}</div>{date}</div></div>')
    body = f'<div class="tbody">{_body_tweet(card.get("texto",""))}</div>'
    return (f'<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8">'
            f'<style>{TWEET_CSS}</style></head><body>'
            f'<div class="card {tema} {rcls}"><div class="tweet">{head}{body}</div></div></body></html>')


ESTILOS = {"notes": montar_html_notes, "tweet_card": montar_html_tweet}


# ----------------------------------------------------------------------------
# Render: HTML -> PNG via Chrome headless.
# ----------------------------------------------------------------------------
def render_png(chrome, html_str, out_png, ratio):
    h = 1350 if ratio == "4x5" else 1080
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
        f.write(html_str)
        html_path = f.name
    try:
        cmd = [chrome, "--headless", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
               "--force-device-scale-factor=1", f"--window-size=1080,{h}",
               f"--screenshot={out_png}", f"file://{html_path}"]
        subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    finally:
        os.unlink(html_path)
    return os.path.exists(out_png)


def dimensoes_png(path):
    """Lê width/height de um PNG sem dependências externas (header IHDR)."""
    try:
        with open(path, "rb") as f:
            head = f.read(26)
        if head[:8] != b"\x89PNG\r\n\x1a\n":
            return None, None
        w = int.from_bytes(head[16:20], "big")
        h = int.from_bytes(head[20:24], "big")
        return w, h
    except Exception:
        return None, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--roteiro", required=True, help="JSON do roteiro (ver docstring)")
    ap.add_argument("--out-dir", required=True, help="pasta de saída dos PNGs")
    ap.add_argument("--chrome", default=None, help="caminho do Chrome/Chromium")
    args = ap.parse_args()

    out = {"ok": False, "cards": [], "erros": []}

    chrome = achar_chrome(args.chrome)
    if not chrome:
        out["erros"].append("Chrome/Chromium não encontrado. Instale o Google Chrome "
                            "ou passe --chrome <caminho>.")
        print(json.dumps(out, ensure_ascii=False, indent=2)); sys.exit(1)

    try:
        with open(args.roteiro, encoding="utf-8") as f:
            roteiro = json.load(f)
    except Exception as e:
        out["erros"].append(f"roteiro inválido: {e}")
        print(json.dumps(out, ensure_ascii=False, indent=2)); sys.exit(1)

    estilo = roteiro.get("estilo", "notes")
    if estilo not in ESTILOS:
        out["erros"].append(f"estilo '{estilo}' sem template HTML embutido. Disponíveis: {list(ESTILOS)}")
        print(json.dumps(out, ensure_ascii=False, indent=2)); sys.exit(1)
    montar = ESTILOS[estilo]
    ratio = roteiro.get("ratio", "4x5")
    if ratio not in ("4x5", "1x1"):
        out["erros"].append(f"ratio '{ratio}' inválido (use 4x5 ou 1x1)")
        print(json.dumps(out, ensure_ascii=False, indent=2)); sys.exit(1)

    os.makedirs(args.out_dir, exist_ok=True)
    cards = roteiro.get("cards", [])
    if not cards:
        out["erros"].append("roteiro sem cards")
        print(json.dumps(out, ensure_ascii=False, indent=2)); sys.exit(1)

    esperado = (1080, 1350) if ratio == "4x5" else (1080, 1080)
    for i, card in enumerate(cards, 1):
        html_str = montar(card, ratio)
        fname = f"card-{i:02d}.png"
        fpath = os.path.join(args.out_dir, fname)
        ok = render_png(chrome, html_str, fpath, ratio)
        w, h = dimensoes_png(fpath) if ok else (None, None)
        if not ok or (w, h) != esperado:
            out["erros"].append(f"card {i}: render falhou ou dimensão errada ({w}x{h}, esperado {esperado[0]}x{esperado[1]})")
        out["cards"].append({"file": fname, "papel": card.get("papel", "-"),
                             "ratio": ratio, "w": w, "h": h})

    out["ok"] = not out["erros"]
    print(json.dumps(out, ensure_ascii=False, indent=2))
    sys.exit(0 if out["ok"] else 1)


if __name__ == "__main__":
    main()
