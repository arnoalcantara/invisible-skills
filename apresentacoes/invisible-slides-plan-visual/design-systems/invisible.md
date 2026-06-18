<!-- base: invisible-doc-to-presentation/design-systems/invisible.md (jun/2026), escala refinada + 5 layouts didáticos (timeline, chart, image, prompt, divider) re-desenhados nessa escala + player com fragments. Sincronizar manualmente em mudanças de marca. -->

# Design System: INVISIBLE — Renderizador de slides

> A identidade Invisible da agência, na escala **editorial refinada** (a mesma da `invisible-doc-to-presentation`, que produz o visual aprovado), estendida para cobrir todos os tipos de slide didáticos e com suporte a **builds** (revelação progressiva). Modo escuro nativo, um acento coral, três fontes. Craft invisível: o slide some no conteúdo.
> Versão: junho 2026.

---

## Princípio visual

Sofisticação sem ostentação. A escala é **refinada, não inflada** — corpo 14–18px, não 24–28px. Hierarquia por contraste e espaço, não por tamanho bruto. Um acento só.

- **Um ponto focal por slide.** Hierarquia explícita por peso/cor/posição.
- **Espaço em branco é estrutura.** Respiro generoso; nada de tela cheia de texto.
- **Acento único** (coral `#E85043`) reservado para o que importa — nunca decorativo.
- **Planura intencional.** Sem gradientes em fundo (exceto overlay de imagem), sem sombras, border-radius 0–2px.
- **Revelação progressiva nativa.** O player suporta `fragment` para builds passo a passo.

**Modo padrão:** escuro (expressão nativa da marca). Para salas/telas muito claras, troque `--near-black` por um fundo claro e inverta os tokens de texto — o sistema é montado em variáveis para isso.

---

## Paleta de cores

```css
/* Fundos */
--black:          #000000;   /* capas, fechamento, citação, prompt */
--near-black:     #111111;   /* fundo padrão de slide */
--surface-1:      #1C1C1C;   /* cards, caixas, divisor */
--surface-2:      #252525;   /* segundo nível */
--surface-3:      #2E2E2E;   /* terceiro nível */

/* Bordas */
--border:         #333333;
--border-subtle:  #2A2A2A;

/* Texto */
--white:          #FFFFFF;   /* texto primário / asserções */
--silver:         #C0C0C0;   /* texto secundário (escala refinada) */
--muted:          #888888;   /* labels, terciário */
--dim:            #666666;   /* texto mudo */

/* Acento */
--coral:          #E85043;   /* único acento — ênfase, destaque, "certo" */
```

**Regras de cor:**
- Sem gradientes em fundos; profundidade por camadas (`#111` → `#1C1C1C` → `#252525`), não por sombra.
- Coral só em ênfase singular (a asserção-chave, o passo crítico, o "certo" de um erro comum).
- Distinções de conteúdo (certo/errado, A/B) **nunca** dependem só de cor — use também posição, rótulo ou forma (acessibilidade).

---

## Tipografia

```css
--font-display:  'Playfair Display', Georgia, serif;      /* capa, citações, número grande, divisor, prompt */
--font-ui:       'DM Sans', system-ui, sans-serif;        /* corpo, listas, rótulos de conteúdo */
--font-label:    'Space Grotesk', system-ui, sans-serif;  /* labels, títulos de seção, UI */
```

**Import (Google Fonts):**
```
https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,900;1,400;1,700&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500&family=Space+Grotesk:wght@500;700;900&display=swap
```

**Usos e tamanhos (escala 1280×720, refinada):**
- *Título de seção / asserção do slide:* `Space Grotesk` 700, **28px** (`<h2>`). É a frase que afirma a ideia.
- *Corpo / itens:* `DM Sans` 300–400, **14–18px**.
- *Capa:* `Playfair Display` 900, 80px.
- *Número grande / display:* `Playfair Display` 900, 112px.
- *Citação:* `Playfair Display` italic, 34px.
- *Divisor:* `Playfair Display` 900, 40px.
- *Prompt (pergunta):* `Playfair Display` 700, 32px.
- *Label / tag:* `Space Grotesk` 700, 10–11px, uppercase, letter-spacing 0.18em, cor coral ou muted.

> **Nunca inflar.** Esta escala é o que distingue o visual aprovado do antigo (que subia o corpo para 24–28px e parecia pesado). Mantenha-a.

---

## Fundamentos visuais

- **Border radius:** 0px (flat). Máx. 2px.
- **Sombras:** nenhuma (exceto o overlay de gradiente em imagem).
- **Espaçamento:** generoso. Margens internas de slide 56–80px.
- **Alinhamento:** esquerda ou centralizado. Nunca justificado.
- **Animações:** fades de opacidade, 150–200ms ease-out. Builds entram suaves; sem bounce.
- **Emojis / ícones decorativos:** nunca. Ícones só funcionais e geométricos.

---

## Tipos de slide → classe CSS

Cada slide do plano traz um campo `Família / Tipo`; o renderizador o mapeia para uma classe CSS. A tabela completa tipo-didático → classe está em [tipo-layout-map.md](../skills/invisible-slides-plan-visual/references/tipo-layout-map.md). Resumo das classes disponíveis:

| Classe CSS | Para |
|---|---|
| `.slide-cover` | abertura/capa |
| `.slide-content` | conteúdo workhorse (asserção+evidência, definição, declaração, objetivos, síntese, takeaway…) |
| `.slide-two-col` | comparação, trade-off, antes/depois, Venn |
| `.slide-diagram` | passo a passo, causa-efeito, ciclo, árvore, taxonomia, anatomia, jornada |
| `.slide-table-layout` | dados/comparações tabulares |
| `.slide-number` | número grande, destaque sobre dado |
| `.slide-quote` | citação/autoridade |
| `.slide-closing` | fechamento da aula |
| `.slide-timeline` | linha do tempo, espectro/continuum |
| `.slide-chart` | gráfico, infográfico (chart real em SVG/código) |
| `.slide-image` | imagem tela-cheia, imagem+texto, exemplo anotado |
| `.slide-prompt` | pergunta, predição, enquete, problema, quiz (processamento ativo) |
| `.slide-divider` | divisor, você-está-aqui, ponte, erro comum, mnemônico |

> Tipo desconhecido → fallback `.slide-content` + comentário HTML `<!-- tipo não mapeado: X -->`. Nunca quebre por causa de um tipo fora do vocabulário.

---

## Revelação progressiva (builds)

Qualquer elemento com a classe `fragment` começa invisível e é revelado um a um pelas setas, **antes** de avançar para o próximo slide.

```html
<li class="fragment">Revelado no segundo avanço</li>
<div class="fragment">Revelado no terceiro avanço</div>
```

Slides **sem** `fragment` se comportam como um player simples (uma seta = um slide), então um storyboard sem builds (ex.: da `invisible-doc-to-presentation`) renderiza sem regressão.

---

## Template HTML base

Use como estrutura raiz. Preencha os slides em `<div id="stage">`. O player já tem navegação por teclado, **builds por fragment**, notas do apresentador, fullscreen e escala responsiva.

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{TITULO}}</title>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,900;1,400;1,700&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500&family=Space+Grotesk:wght@500;700;900&display=swap" rel="stylesheet">
<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
:root {
  --black:#000; --near-black:#111; --surface-1:#1C1C1C; --surface-2:#252525; --surface-3:#2E2E2E;
  --border:#333; --border-subtle:#2A2A2A;
  --white:#FFF; --silver:#C0C0C0; --muted:#888; --dim:#666;
  --coral:#E85043;
  --font-display:'Playfair Display',Georgia,serif;
  --font-ui:'DM Sans',system-ui,sans-serif;
  --font-label:'Space Grotesk',system-ui,sans-serif;
}
body { background:#0a0a0a; display:flex; align-items:center; justify-content:center; min-height:100vh; overflow:hidden; font-family:var(--font-ui); }
#stage { position:fixed; width:1280px; height:720px; transform-origin:center center; }
.slide { display:none; position:absolute; inset:0; width:1280px; height:720px; background:var(--near-black); color:var(--white); overflow:hidden; }
.slide.active { display:flex; }
.fragment { opacity:0; transition:opacity .18s ease-out; }
.fragment.shown { opacity:1; }

/* ── Utilities ── */
.label { font-family:var(--font-label); font-size:11px; font-weight:700; letter-spacing:0.18em; text-transform:uppercase; color:var(--coral); }
.label-muted { font-family:var(--font-label); font-size:11px; font-weight:500; letter-spacing:0.18em; text-transform:uppercase; color:var(--muted); }
.wordmark { position:absolute; bottom:28px; right:40px; font-family:var(--font-label); font-size:10px; font-weight:900; letter-spacing:0.18em; text-transform:uppercase; color:rgba(255,255,255,0.07); user-select:none; }
.slide-num { position:absolute; bottom:28px; left:40px; font-family:var(--font-label); font-size:10px; font-weight:500; letter-spacing:0.12em; color:rgba(255,255,255,0.18); }
.coral { color:var(--coral); }

/* ── Cover ── */
.slide-cover { background:var(--black); flex-direction:column; justify-content:flex-end; padding:80px 100px 88px; }
.slide-cover .pre { margin-bottom:32px; }
.slide-cover h1 { font-family:var(--font-display); font-size:80px; font-weight:900; line-height:1.0; letter-spacing:-0.03em; color:var(--white); margin-bottom:28px; }
.slide-cover .sub { font-family:var(--font-ui); font-size:18px; font-weight:300; color:var(--silver); letter-spacing:0.02em; }

/* ── Content (workhorse: asserção+evidência, definição, declaração, lista, síntese) ── */
.slide-content { flex-direction:column; padding:56px 80px; }
.slide-content .slide-top { margin-bottom:40px; }
.slide-content .slide-top h2 { font-family:var(--font-label); font-size:28px; font-weight:700; color:var(--white); margin-top:12px; line-height:1.2; }
.slide-content ul { list-style:none; display:flex; flex-direction:column; gap:14px; }
.slide-content li { font-family:var(--font-ui); font-size:18px; color:var(--silver); line-height:1.55; padding-left:20px; position:relative; }
.slide-content li::before { content:''; position:absolute; left:0; top:11px; width:8px; height:1px; background:var(--coral); }
.slide-content li strong { color:var(--white); font-weight:500; }
/* corpo em prosa (evidência da asserção) */
.slide-content .body { flex:1; display:flex; flex-direction:column; justify-content:center; gap:16px; }
.slide-content .body p { font-family:var(--font-ui); font-size:18px; line-height:1.6; color:var(--silver); max-width:920px; }
.slide-content .body strong { color:var(--white); font-weight:500; }

/* ── Cards grid (use inside .slide-content) ── */
.card-grid { display:grid; grid-template-columns:1fr 1fr; gap:16px; flex:1; }
.card { background:var(--surface-1); border:1px solid var(--border-subtle); padding:28px 32px; display:flex; flex-direction:column; gap:8px; }
.card .card-tag { font-family:var(--font-label); font-size:10px; font-weight:700; letter-spacing:0.18em; text-transform:uppercase; color:var(--coral); }
.card .card-name { font-family:var(--font-label); font-size:20px; font-weight:700; color:var(--white); letter-spacing:-0.01em; }
.card .card-desc { font-family:var(--font-ui); font-size:14px; font-weight:400; color:var(--silver); line-height:1.5; }

/* ── Two columns ── */
.slide-two-col { flex-direction:row; }
.slide-two-col .col { flex:1; display:flex; flex-direction:column; justify-content:center; padding:64px 56px; border-right:1px solid var(--border-subtle); }
.slide-two-col .col:last-child { border-right:none; background:var(--surface-1); }
.slide-two-col .col h3 { font-family:var(--font-label); font-size:13px; font-weight:700; letter-spacing:0.12em; text-transform:uppercase; color:var(--muted); margin-bottom:20px; }
.slide-two-col .col ul { list-style:none; display:flex; flex-direction:column; gap:12px; }
.slide-two-col .col li { font-family:var(--font-ui); font-size:16px; color:var(--silver); line-height:1.55; padding-left:18px; position:relative; }
.slide-two-col .col li::before { content:''; position:absolute; left:0; top:10px; width:7px; height:1px; background:var(--coral); }
.slide-two-col .col li strong { color:var(--white); font-weight:500; }

/* ── Table ── */
.slide-table-layout { flex-direction:column; padding:56px 80px; }
.slide-table-layout .slide-top { margin-bottom:36px; }
.slide-table-layout .slide-top h2 { font-family:var(--font-label); font-size:28px; font-weight:700; color:var(--white); margin-top:12px; }
.slide-table-layout table { width:100%; border-collapse:collapse; }
.slide-table-layout thead tr { border-bottom:1px solid var(--border); }
.slide-table-layout thead th { font-family:var(--font-label); font-size:10px; font-weight:700; letter-spacing:0.18em; text-transform:uppercase; color:var(--muted); padding:0 0 14px; text-align:left; }
.slide-table-layout thead th:not(:first-child) { padding-left:24px; }
.slide-table-layout tbody tr { border-bottom:1px solid var(--border-subtle); }
.slide-table-layout tbody td { font-family:var(--font-ui); font-size:15px; color:var(--silver); padding:13px 0; line-height:1.4; }
.slide-table-layout tbody td:not(:first-child) { padding-left:24px; }
.slide-table-layout tbody td strong { color:var(--white); font-weight:500; }
.slide-table-layout tbody td .coral { color:var(--coral); font-weight:500; }
.slide-table-layout tbody tr.highlight td { color:var(--white); }
.slide-table-layout tbody tr.highlight td:first-child { color:var(--coral); }

/* ── Number highlight ── */
.slide-number { flex-direction:row; }
.slide-number .num-left { width:420px; flex-shrink:0; background:var(--black); display:flex; flex-direction:column; justify-content:center; align-items:flex-start; padding:72px 64px; border-right:1px solid var(--border-subtle); }
.slide-number .num-left .big { font-family:var(--font-display); font-size:112px; font-weight:900; line-height:1; letter-spacing:-0.04em; color:var(--coral); }
.slide-number .num-left .unit { font-family:var(--font-ui); font-size:14px; font-weight:300; color:var(--silver); margin-top:8px; line-height:1.4; max-width:180px; }
.slide-number .num-right { flex:1; display:flex; flex-direction:column; padding:64px 72px; justify-content:center; gap:24px; }
.slide-number .num-right h2 { font-family:var(--font-label); font-size:28px; font-weight:700; color:var(--white); letter-spacing:-0.02em; line-height:1.25; }

/* ── Diagram / flow ── */
.slide-diagram { flex-direction:column; padding:64px 80px; }
.slide-diagram .slide-top { margin-bottom:48px; }
.slide-diagram .slide-top h2 { font-family:var(--font-label); font-size:28px; font-weight:700; color:var(--white); margin-top:12px; }
.slide-diagram .flow { display:flex; align-items:stretch; gap:0; flex:1; }
.slide-diagram .fbox { background:var(--surface-1); border:1px solid var(--border); flex:1; display:flex; flex-direction:column; padding:28px 24px; gap:10px; }
.slide-diagram .fbox .fn { font-family:var(--font-display); font-size:36px; font-weight:900; color:rgba(255,255,255,0.08); line-height:1; }
.slide-diagram .fbox .ftitle { font-family:var(--font-label); font-size:16px; font-weight:700; color:var(--white); letter-spacing:-0.01em; }
.slide-diagram .fbox .fsub { font-family:var(--font-ui); font-size:13px; color:var(--silver); line-height:1.5; }
.slide-diagram .fbox .fdetail { font-family:var(--font-label); font-size:11px; font-weight:700; letter-spacing:0.12em; text-transform:uppercase; color:var(--coral); margin-top:auto; }
.slide-diagram .arrow { width:40px; flex-shrink:0; display:flex; align-items:center; justify-content:center; color:var(--border); font-size:18px; }

/* ── Timeline / spectrum (refinada) ── */
.slide-timeline { flex-direction:column; padding:56px 80px; }
.slide-timeline .slide-top { margin-bottom:44px; }
.slide-timeline .slide-top h2 { font-family:var(--font-label); font-size:28px; font-weight:700; color:var(--white); margin-top:12px; }
.slide-timeline .axis { flex:1; display:flex; align-items:center; }
.slide-timeline .track { width:100%; height:1px; background:var(--border); position:relative; display:flex; justify-content:space-between; }
.slide-timeline .mark { position:relative; top:-5px; display:flex; flex-direction:column; align-items:center; gap:10px; }
.slide-timeline .dot { width:10px; height:10px; border-radius:50%; background:var(--coral); }
.slide-timeline .mark .date { font-family:var(--font-label); font-size:14px; font-weight:700; color:var(--white); }
.slide-timeline .mark .ev { font-family:var(--font-ui); font-size:13px; color:var(--silver); max-width:160px; text-align:center; line-height:1.5; }

/* ── Chart (chart real em SVG/código dentro de .chart-area) ── */
.slide-chart { flex-direction:column; padding:56px 80px; }
.slide-chart .slide-top { margin-bottom:28px; }
.slide-chart .slide-top h2 { font-family:var(--font-label); font-size:28px; font-weight:700; color:var(--white); margin-top:12px; }
.slide-chart .chart-area { flex:1; display:flex; align-items:center; justify-content:center; }
.slide-chart .chart-area text { font-family:var(--font-ui); }

/* ── Image ── */
.slide-image { padding:0; }
.slide-image img, .slide-image .imgfill { width:100%; height:100%; object-fit:cover; }
.slide-image .overlay { position:absolute; left:0; bottom:0; right:0; padding:56px 80px; background:linear-gradient(to top, rgba(0,0,0,0.88), transparent); }
.slide-image .overlay h2 { font-family:var(--font-label); font-size:28px; font-weight:700; color:var(--white); }
.slide-image .overlay .cap { font-family:var(--font-ui); font-size:15px; color:var(--silver); margin-top:8px; line-height:1.5; }
.slide-image.split { display:flex; }
.slide-image.split .imghalf { width:50%; height:100%; }
.slide-image.split .txthalf { width:50%; padding:56px 56px; display:flex; flex-direction:column; justify-content:center; gap:16px; background:var(--near-black); }
.slide-image.split .txthalf p { font-family:var(--font-ui); font-size:16px; line-height:1.6; color:var(--silver); }

/* ── Prompt (processamento ativo) ── */
.slide-prompt { background:var(--black); flex-direction:column; justify-content:center; align-items:flex-start; padding:72px 100px; }
.slide-prompt .label { margin-bottom:28px; }
.slide-prompt .q { font-family:var(--font-display); font-size:32px; font-weight:700; line-height:1.3; color:var(--white); max-width:920px; }
.slide-prompt .options { margin-top:36px; display:flex; flex-direction:column; gap:12px; }
.slide-prompt .opt { font-family:var(--font-ui); font-size:16px; color:var(--silver); padding-left:20px; position:relative; }
.slide-prompt .opt::before { content:''; position:absolute; left:0; top:11px; width:8px; height:1px; background:var(--coral); }
.slide-prompt .opt strong { color:var(--white); font-weight:500; }

/* ── Quote ── */
.slide-quote { background:var(--black); flex-direction:column; justify-content:center; align-items:flex-start; padding:80px 100px; }
.slide-quote blockquote { font-family:var(--font-display); font-size:34px; font-weight:400; font-style:italic; color:var(--white); line-height:1.45; max-width:840px; margin-bottom:28px; }
.slide-quote .author { font-family:var(--font-label); font-size:12px; font-weight:700; letter-spacing:0.14em; text-transform:uppercase; color:var(--coral); }

/* ── Divider / transition / you-are-here / common-error / mnemonic (refinada) ── */
.slide-divider { background:var(--surface-1); flex-direction:column; justify-content:center; align-items:flex-start; padding:80px 100px; }
.slide-divider .kicker { font-family:var(--font-label); font-size:11px; font-weight:700; letter-spacing:0.18em; text-transform:uppercase; color:var(--coral); margin-bottom:20px; }
.slide-divider h2 { font-family:var(--font-display); font-size:40px; font-weight:900; line-height:1.1; color:var(--white); max-width:920px; }
.slide-divider .sub { font-family:var(--font-ui); font-size:16px; color:var(--silver); margin-top:20px; max-width:760px; line-height:1.6; }

/* ── Closing ── */
.slide-closing { background:var(--black); flex-direction:column; justify-content:center; align-items:flex-start; padding:80px 100px; }
.slide-closing blockquote { font-family:var(--font-display); font-size:34px; font-weight:400; font-style:italic; color:var(--white); line-height:1.45; max-width:840px; margin-bottom:28px; }
.slide-closing .author { font-family:var(--font-label); font-size:12px; font-weight:700; letter-spacing:0.14em; text-transform:uppercase; color:var(--muted); }
.slide-closing .next { border-top:1px solid var(--border); padding-top:32px; margin-top:40px; }
.slide-closing .next .next-label { font-family:var(--font-label); font-size:10px; font-weight:700; letter-spacing:0.18em; text-transform:uppercase; color:var(--muted); margin-bottom:8px; }
.slide-closing .next .next-val { font-family:var(--font-label); font-size:16px; font-weight:700; color:var(--white); }

/* ── Player controls ── */
#notes-bar { position:fixed; bottom:0; left:0; right:0; background:rgba(0,0,0,0.95); color:var(--silver); font-size:13px; font-family:var(--font-ui); line-height:1.5; padding:12px 24px; display:none; z-index:100; border-top:1px solid var(--border-subtle); }
#notes-bar.visible { display:block; }
#notes-bar strong { color:var(--coral); font-weight:500; }
#controls { position:fixed; top:14px; right:20px; display:flex; gap:8px; z-index:100; align-items:center; }
#controls button { background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.1); color:rgba(255,255,255,0.4); font-size:11px; font-family:var(--font-label); font-weight:500; letter-spacing:0.1em; text-transform:uppercase; padding:6px 12px; cursor:pointer; }
#controls button:hover { background:rgba(255,255,255,0.1); color:#fff; }
#counter { color:rgba(255,255,255,0.25); font-size:11px; font-family:var(--font-label); }
#progress { position:fixed; top:0; left:0; height:2px; background:var(--coral); transition:width 0.25s ease-out; z-index:200; }
</style>
</head>
<body>
<div id="stage">
  <!-- SLIDES AQUI. Primeiro slide com classe "active". -->
  <!-- Cada slide termina com: <div class="slide-num">N / T</div><div class="wordmark">INVISIBLE</div> -->
  <!-- Builds: qualquer elemento com class="fragment" é revelado um a um pelas setas. -->
</div>

<div id="notes-bar"><strong>Notas&nbsp;·&nbsp;</strong><span id="notes-text"></span></div>
<div id="controls">
  <button onclick="toggleNotes()">N · Notas</button>
  <button onclick="toggleFullscreen()">F · Tela cheia</button>
  <span id="counter"></span>
</div>
<div id="progress"></div>

<script>
// notes = array de strings, uma por slide, na ordem dos slides
const notes = [/* PREENCHER */];

let current = 0, frag = 0;
const slides = Array.from(document.querySelectorAll('.slide'));
const total = slides.length;
const fragsOf = s => Array.from(s.querySelectorAll('.fragment'));

function render() {
  slides.forEach((s,i) => s.classList.toggle('active', i === current));
  const f = fragsOf(slides[current]);
  f.forEach((el,i) => el.classList.toggle('shown', i < frag));
  document.getElementById('notes-text').textContent = notes[current] || '';
  document.getElementById('counter').textContent = (current+1)+' / '+total;
  document.getElementById('progress').style.width = ((current+1)/total*100)+'%';
}
function next() {
  const f = fragsOf(slides[current]);
  if (frag < f.length) { frag++; render(); return; }
  if (current < total-1) { current++; frag = 0; render(); }
}
function prev() {
  if (frag > 0) { frag--; render(); return; }
  if (current > 0) { current--; frag = fragsOf(slides[current]).length; render(); }
}
function goTo(n){ current = Math.max(0,Math.min(n,total-1)); frag = 0; render(); }

document.addEventListener('keydown', e => {
  if (['ArrowRight','ArrowDown',' '].includes(e.key)) { e.preventDefault(); next(); }
  if (['ArrowLeft','ArrowUp'].includes(e.key)) { e.preventDefault(); prev(); }
  if (e.key==='n'||e.key==='N') toggleNotes();
  if (e.key==='f'||e.key==='F') toggleFullscreen();
  if (e.key==='Home') goTo(0);
  if (e.key==='End') goTo(total-1);
});
function scaleStage(){
  const stage=document.getElementById('stage');
  const scale=Math.min(window.innerWidth/1280, window.innerHeight/720);
  stage.style.transform='scale('+scale+')';
  stage.style.left=((window.innerWidth-1280)/2)+'px';
  stage.style.top=((window.innerHeight-720)/2)+'px';
}
function toggleNotes(){ document.getElementById('notes-bar').classList.toggle('visible'); }
function toggleFullscreen(){ if(!document.fullscreenElement) document.documentElement.requestFullscreen(); else document.exitFullscreen(); }
window.addEventListener('resize', scaleStage);
scaleStage(); render();
</script>
</body>
</html>
```

---

## Instruções para o Claude ao usar este template

1. **Copie o template completo** acima.
2. **Substitua `{{TITULO}}`** pelo título real do plano.
3. **Insira os slides em `<div id="stage">`**, mapeando o **tipo** do plano para a **classe CSS** ([tipo-layout-map.md](../skills/invisible-slides-plan-visual/references/tipo-layout-map.md)). O título de todo slide de conteúdo é uma **frase-asserção** no `<h2>`.
4. **Primeiro slide com classe `active`.**
5. **Builds:** marque com `class="fragment"` os elementos que o campo `Build:` do plano manda revelar passo a passo (passos de um processo, opções de uma pergunta, resposta de um quiz, linhas de uma comparação). As setas revelam um a um antes de trocar de slide.
6. **Preencha o array `notes`** — uma string por slide, na ordem, vinda do campo `Notas do professor:` do plano.
7. **Cada slide termina com:**
   ```html
   <div class="slide-num">N / T</div>
   <div class="wordmark">INVISIBLE</div>
   ```
8. **Gráficos** (`.slide-chart`): renderize o chart **de verdade** em SVG/HTML dentro de `.chart-area` — nunca uma imagem de gráfico gerada (a regra de ouro da produção visual).
9. **Escala refinada sempre.** Não suba os tamanhos de fonte além desta folha. O corpo vive em 14–18px; o que dá sofisticação é o espaço, não o tamanho.
10. Sem emojis, sem ícones decorativos, sem gradiente (exceto o overlay de imagem), sem border-radius > 2px.

### Exemplo — Asserção + evidência (workhorse), com build
```html
<div class="slide slide-content active">
  <div class="slide-top"><div class="label">Pressão atmosférica</div>
    <h2>A pressão do ar cai conforme a altitude sobe.</h2></div>
  <div class="body">
    <p class="fragment">Ao nível do mar, a coluna de ar inteira pesa sobre você: <strong>~1 atm</strong>.</p>
    <p class="fragment">A 5.500 m, metade da atmosfera ficou abaixo — a pressão cai pela <strong>metade</strong>.</p>
  </div>
  <div class="slide-num">4 / 18</div><div class="wordmark">INVISIBLE</div>
</div>
```

### Exemplo — Pergunta / processamento ativo
```html
<div class="slide slide-prompt">
  <div class="label">Preveja</div>
  <div class="q">O que acontece com a chama de uma vela dentro de um elevador em queda livre?</div>
  <div class="options">
    <div class="opt fragment">Sobe mais alta</div>
    <div class="opt fragment">Apaga</div>
    <div class="opt fragment">Vira uma esfera</div>
  </div>
  <div class="slide-num">9 / 18</div><div class="wordmark">INVISIBLE</div>
</div>
```

### Exemplo — Divisor de seção
```html
<div class="slide slide-divider">
  <div class="kicker">Parte 2</div>
  <h2>Por que a água ferve mais rápido na montanha.</h2>
  <div class="sub">Agora que entendemos a pressão, vamos ver o que ela faz com a temperatura de ebulição.</div>
  <div class="slide-num">10 / 18</div><div class="wordmark">INVISIBLE</div>
</div>
```
