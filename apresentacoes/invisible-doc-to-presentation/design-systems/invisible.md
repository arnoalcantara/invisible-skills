# Design System: INVISIBLE — Brand System
> Agência de marketing sofisticada. Craft invisível que eleva marcas sem se mostrar.
> Versão: maio 2026.

---

## Identidade Visual

**Filosofia:** craft invisível — o trabalho da agência some dentro do resultado do cliente. Sofisticação sem ostentação.

**Modo padrão:** escuro. O modo escuro é uma expressão nativa da marca, não alternativa secundária.

---

## Paleta de Cores

```css
/* Fundos */
--black:          #000000;   /* capas, fechamento */
--near-black:     #111111;   /* fundo padrão de slides */
--surface-1:      #1C1C1C;   /* cards sobre fundo escuro */
--surface-2:      #252525;   /* segundo nível de profundidade */
--surface-3:      #2E2E2E;   /* terceiro nível */

/* Bordas */
--border:         #333333;
--border-subtle:  #2A2A2A;

/* Texto */
--white:          #FFFFFF;   /* texto primário */
--silver:         #C0C0C0;   /* texto secundário */
--muted:          #888888;   /* texto terciário */
--dim:            #666666;   /* texto mudo */

/* Acento */
--coral:          #E85043;   /* único acento — usar com parcimônia */
```

**Regras de cor:**
- Sem gradientes em fundos — a planura é intencional
- Profundidade por sobreposição de camadas (`#111111` → `#1C1C1C` → `#252525`), não por sombras
- Coral `#E85043` é reservado para momentos de ênfase singular — nunca decorativo
- Sem sombras em modo escuro

---

## Tipografia

```css
--font-display:  'Playfair Display', Georgia, serif;   /* display, headlines editoriais, citações */
--font-ui:       'DM Sans', system-ui, sans-serif;     /* body, corpo, listas */
--font-label:    'Space Grotesk', system-ui, sans-serif; /* labels, UI, wordmark */
```

**Google Fonts import:**
```
https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,900;1,400;1,700&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500&family=Space+Grotesk:wght@500;700;900&display=swap
```

**Usos:**
- Títulos de seção e headlines editoriais: `Playfair Display` 700–900
- Citações e momentos dramáticos: `Playfair Display` italic
- Labels, tags, wordmark, UI estrutural: `Space Grotesk` 700–900, uppercase, letter-spacing 0.12–0.18em
- Corpo de texto, bullets, parágrafos: `DM Sans` 300–400

---

## Fundamentos Visuais

- **Border radius:** 0px (flat). Máximo 2px.
- **Sombras:** nenhuma em modo escuro.
- **Espaçamento:** generoso — whitespace é elemento de design.
- **Alinhamento:** esquerda ou centralizado. Nunca justificado.
- **Animações:** mínimas. Fades de opacidade. 150–200ms ease-out. Sem bounce.
- **Botões:** flat rectangles, 0px radius, sem sombra.
- **Emojis / ícones decorativos:** nunca.

---

## Tipos de Slide Disponíveis

| Tipo | Classe CSS | Uso |
|---|---|---|
| Capa | `.slide-cover` | Abertura. Fundo `#000000`. Playfair Display 900 enorme. Label coral. |
| Conteúdo | `.slide-content` | Texto + bullets. Fundo `#111111`. Cards em `#1C1C1C`. |
| Dois colunas | `.slide-two-col` | Contraste ou comparação. Divisor `#333`. |
| Tabela | `.slide-table-layout` | Dados. Header com label; linhas separadas por `#2A2A2A`. |
| Número destaque | `.slide-number` | Métrica de impacto. Número em Playfair + coral. |
| Diagrama / fluxo | `.slide-diagram` | Processo sequencial. Caixas em `#1C1C1C`, setas `#333`. |
| Citação | `.slide-quote` | Quote em Playfair italic. Fundo `#000000`. Atribuição em coral. |
| Fechamento | `.slide-closing` | Capa final. Fundo `#000000`. Quote + próximo passo. |

---

## Template HTML Base

Use este template como estrutura raiz de toda apresentação com o design system Invisible. Preencha os slides dentro de `<div id="stage">`. O player já tem navegação por teclado, notas do apresentador, fullscreen e escala responsiva.

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{TITULO_APRESENTACAO}}</title>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,900;1,400;1,700&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500&family=Space+Grotesk:wght@500;700;900&display=swap" rel="stylesheet">
<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
:root {
  --black: #000000; --near-black: #111111;
  --surface-1: #1C1C1C; --surface-2: #252525; --surface-3: #2E2E2E;
  --border: #333333; --border-subtle: #2A2A2A;
  --white: #FFFFFF; --silver: #C0C0C0; --muted: #888888; --dim: #666666;
  --coral: #E85043;
  --font-display: 'Playfair Display', Georgia, serif;
  --font-ui: 'DM Sans', system-ui, sans-serif;
  --font-label: 'Space Grotesk', system-ui, sans-serif;
}
body { background: #0a0a0a; display: flex; align-items: center; justify-content: center; min-height: 100vh; overflow: hidden; font-family: var(--font-ui); }
#stage { position: fixed; width: 1280px; height: 720px; transform-origin: center center; }
.slide { display: none; position: absolute; inset: 0; width: 1280px; height: 720px; background: var(--near-black); color: var(--white); overflow: hidden; }
.slide.active { display: flex; }

/* ── Utilities ── */
.label { font-family: var(--font-label); font-size: 11px; font-weight: 700; letter-spacing: 0.18em; text-transform: uppercase; color: var(--coral); }
.label-muted { font-family: var(--font-label); font-size: 11px; font-weight: 500; letter-spacing: 0.18em; text-transform: uppercase; color: var(--muted); }
.wordmark { position: absolute; bottom: 28px; right: 40px; font-family: var(--font-label); font-size: 10px; font-weight: 900; letter-spacing: 0.18em; text-transform: uppercase; color: rgba(255,255,255,0.07); user-select: none; }
.slide-num { position: absolute; bottom: 28px; left: 40px; font-family: var(--font-label); font-size: 10px; font-weight: 500; letter-spacing: 0.12em; color: rgba(255,255,255,0.18); }

/* ── Cover ── */
.slide-cover { background: var(--black); flex-direction: column; justify-content: flex-end; padding: 80px 100px 88px; }
.slide-cover .pre { margin-bottom: 32px; }
.slide-cover h1 { font-family: var(--font-display); font-size: 80px; font-weight: 900; line-height: 1.0; letter-spacing: -0.03em; color: var(--white); margin-bottom: 28px; }
.slide-cover .sub { font-family: var(--font-ui); font-size: 18px; font-weight: 300; color: var(--silver); letter-spacing: 0.02em; }

/* ── Content (generic) ── */
.slide-content { flex-direction: column; padding: 56px 80px; }
.slide-content .slide-top { margin-bottom: 40px; }
.slide-content .slide-top h2 { font-family: var(--font-label); font-size: 28px; font-weight: 700; color: var(--white); margin-top: 12px; }
.slide-content ul { list-style: none; display: flex; flex-direction: column; gap: 14px; }
.slide-content li { font-family: var(--font-ui); font-size: 18px; color: var(--silver); line-height: 1.55; padding-left: 20px; position: relative; }
.slide-content li::before { content: ''; position: absolute; left: 0; top: 11px; width: 8px; height: 1px; background: var(--coral); }
.slide-content li strong { color: var(--white); font-weight: 500; }

/* ── Cards grid (use inside .slide-content) ── */
.card-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; flex: 1; }
.card { background: var(--surface-1); border: 1px solid var(--border-subtle); padding: 28px 32px; display: flex; flex-direction: column; gap: 8px; }
.card .card-tag { font-family: var(--font-label); font-size: 10px; font-weight: 700; letter-spacing: 0.18em; text-transform: uppercase; color: var(--coral); }
.card .card-name { font-family: var(--font-label); font-size: 20px; font-weight: 700; color: var(--white); letter-spacing: -0.01em; }
.card .card-desc { font-family: var(--font-ui); font-size: 14px; font-weight: 400; color: var(--silver); line-height: 1.5; }

/* ── Two columns ── */
.slide-two-col { flex-direction: row; }
.slide-two-col .col { flex: 1; display: flex; flex-direction: column; justify-content: center; padding: 64px 56px; border-right: 1px solid var(--border-subtle); }
.slide-two-col .col:last-child { border-right: none; background: var(--surface-1); }
.slide-two-col .col h3 { font-family: var(--font-label); font-size: 13px; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; color: var(--muted); margin-bottom: 20px; }
.slide-two-col .col ul { list-style: none; display: flex; flex-direction: column; gap: 12px; }
.slide-two-col .col li { font-family: var(--font-ui); font-size: 16px; color: var(--silver); line-height: 1.55; padding-left: 18px; position: relative; }
.slide-two-col .col li::before { content: ''; position: absolute; left: 0; top: 10px; width: 7px; height: 1px; background: var(--coral); }
.slide-two-col .col li strong { color: var(--white); font-weight: 500; }

/* ── Table ── */
.slide-table-layout { flex-direction: column; padding: 56px 80px; }
.slide-table-layout .slide-top { margin-bottom: 36px; }
.slide-table-layout .slide-top h2 { font-family: var(--font-label); font-size: 28px; font-weight: 700; color: var(--white); margin-top: 12px; }
.slide-table-layout table { width: 100%; border-collapse: collapse; }
.slide-table-layout thead tr { border-bottom: 1px solid var(--border); }
.slide-table-layout thead th { font-family: var(--font-label); font-size: 10px; font-weight: 700; letter-spacing: 0.18em; text-transform: uppercase; color: var(--muted); padding: 0 0 14px; text-align: left; }
.slide-table-layout thead th:not(:first-child) { padding-left: 24px; }
.slide-table-layout tbody tr { border-bottom: 1px solid var(--border-subtle); }
.slide-table-layout tbody td { font-family: var(--font-ui); font-size: 15px; color: var(--silver); padding: 13px 0; line-height: 1.4; }
.slide-table-layout tbody td:not(:first-child) { padding-left: 24px; }
.slide-table-layout tbody td strong { color: var(--white); font-weight: 500; }
.slide-table-layout tbody td .coral { color: var(--coral); font-weight: 500; }
.slide-table-layout tbody tr.highlight td { color: var(--white); }
.slide-table-layout tbody tr.highlight td:first-child { color: var(--coral); }

/* ── Number highlight ── */
.slide-number { flex-direction: row; }
.slide-number .num-left { width: 420px; flex-shrink: 0; background: var(--black); display: flex; flex-direction: column; justify-content: center; align-items: flex-start; padding: 72px 64px; border-right: 1px solid var(--border-subtle); }
.slide-number .num-left .big { font-family: var(--font-display); font-size: 112px; font-weight: 900; line-height: 1; letter-spacing: -0.04em; color: var(--coral); }
.slide-number .num-left .unit { font-family: var(--font-ui); font-size: 14px; font-weight: 300; color: var(--silver); margin-top: 8px; line-height: 1.4; max-width: 180px; }
.slide-number .num-right { flex: 1; display: flex; flex-direction: column; padding: 64px 72px; justify-content: center; gap: 24px; }
.slide-number .num-right h2 { font-family: var(--font-label); font-size: 28px; font-weight: 700; color: var(--white); letter-spacing: -0.02em; }

/* ── Diagram / flow ── */
.slide-diagram { flex-direction: column; padding: 64px 80px; }
.slide-diagram .slide-top { margin-bottom: 48px; }
.slide-diagram .slide-top h2 { font-family: var(--font-label); font-size: 28px; font-weight: 700; color: var(--white); margin-top: 12px; }
.slide-diagram .flow { display: flex; align-items: stretch; gap: 0; flex: 1; }
.slide-diagram .fbox { background: var(--surface-1); border: 1px solid var(--border); flex: 1; display: flex; flex-direction: column; padding: 28px 24px; gap: 10px; }
.slide-diagram .fbox .fn { font-family: var(--font-display); font-size: 36px; font-weight: 900; color: rgba(255,255,255,0.08); line-height: 1; }
.slide-diagram .fbox .ftitle { font-family: var(--font-label); font-size: 16px; font-weight: 700; color: var(--white); letter-spacing: -0.01em; }
.slide-diagram .fbox .fsub { font-family: var(--font-ui); font-size: 13px; color: var(--silver); line-height: 1.5; }
.slide-diagram .fbox .fdetail { font-family: var(--font-label); font-size: 11px; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; color: var(--coral); margin-top: auto; }
.slide-diagram .arrow { width: 40px; flex-shrink: 0; display: flex; align-items: center; justify-content: center; color: var(--border); font-size: 18px; }

/* ── Quote / Closing ── */
.slide-quote, .slide-closing { background: var(--black); flex-direction: column; justify-content: center; align-items: flex-start; padding: 80px 100px; }
.slide-quote blockquote, .slide-closing blockquote { font-family: var(--font-display); font-size: 34px; font-weight: 400; font-style: italic; color: var(--white); line-height: 1.45; max-width: 840px; margin-bottom: 28px; }
.slide-quote .author, .slide-closing .author { font-family: var(--font-label); font-size: 12px; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; color: var(--muted); }
.slide-closing .next { border-top: 1px solid var(--border); padding-top: 32px; margin-top: 40px; }
.slide-closing .next .next-label { font-family: var(--font-label); font-size: 10px; font-weight: 700; letter-spacing: 0.18em; text-transform: uppercase; color: var(--muted); margin-bottom: 8px; }
.slide-closing .next .next-val { font-family: var(--font-label); font-size: 16px; font-weight: 700; color: var(--white); }

/* ── Player controls ── */
#notes-bar { position: fixed; bottom: 0; left: 0; right: 0; background: rgba(0,0,0,0.95); color: var(--silver); font-size: 13px; font-family: var(--font-ui); padding: 12px 24px; display: none; z-index: 100; border-top: 1px solid var(--border-subtle); }
#notes-bar.visible { display: block; }
#notes-bar strong { color: var(--coral); font-weight: 500; }
#controls { position: fixed; top: 14px; right: 20px; display: flex; gap: 8px; z-index: 100; align-items: center; }
#controls button { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); color: rgba(255,255,255,0.4); font-size: 11px; font-family: var(--font-label); font-weight: 500; letter-spacing: 0.1em; text-transform: uppercase; padding: 6px 12px; cursor: pointer; }
#controls button:hover { background: rgba(255,255,255,0.1); color: white; }
#counter { color: rgba(255,255,255,0.25); font-size: 11px; font-family: var(--font-label); }
#progress { position: fixed; top: 0; left: 0; height: 2px; background: var(--coral); transition: width 0.25s ease-out; z-index: 200; }
</style>
</head>
<body>
<div id="stage">
  <!-- SLIDES AQUI — cada slide: <div class="slide [tipo]" id="sN"> ... </div> -->
  <!-- Primeiro slide deve ter classe "active" -->
  <!-- Cada slide termina com: <div class="slide-num">N / T</div><div class="wordmark">INVISIBLE</div> -->
</div>

<div id="notes-bar"><strong>Notas&nbsp;·&nbsp;</strong><span id="notes-text"></span></div>
<div id="controls">
  <button onclick="toggleNotes()">N · Notas</button>
  <button onclick="toggleFullscreen()">F · Fullscreen</button>
  <span id="counter"></span>
</div>
<div id="progress"></div>

<script>
// notes = array de strings, uma por slide, na ordem dos slides
const notes = [/* PREENCHER */];

let current = 0;
const slides = document.querySelectorAll('.slide');
const total = slides.length;

function goTo(n) {
  slides[current].classList.remove('active');
  current = Math.max(0, Math.min(n, total - 1));
  slides[current].classList.add('active');
  document.getElementById('notes-text').textContent = notes[current] || '';
  document.getElementById('counter').textContent = (current + 1) + ' / ' + total;
  document.getElementById('progress').style.width = ((current + 1) / total * 100) + '%';
}

document.addEventListener('keydown', e => {
  if (['ArrowRight','ArrowDown',' '].includes(e.key)) { e.preventDefault(); goTo(current + 1); }
  if (['ArrowLeft','ArrowUp'].includes(e.key)) { e.preventDefault(); goTo(current - 1); }
  if (e.key === 'n' || e.key === 'N') toggleNotes();
  if (e.key === 'f' || e.key === 'F') toggleFullscreen();
  if (e.key === 'Home') goTo(0);
  if (e.key === 'End') goTo(total - 1);
});

function scaleStage() {
  const stage = document.getElementById('stage');
  const scale = Math.min(window.innerWidth / 1280, window.innerHeight / 720);
  stage.style.transform = 'scale(' + scale + ')';
  stage.style.left = ((window.innerWidth - 1280) / 2) + 'px';
  stage.style.top = ((window.innerHeight - 720) / 2) + 'px';
}

function toggleNotes() { document.getElementById('notes-bar').classList.toggle('visible'); }
function toggleFullscreen() {
  if (!document.fullscreenElement) document.documentElement.requestFullscreen();
  else document.exitFullscreen();
}

window.addEventListener('resize', scaleStage);
scaleStage();
goTo(0);
</script>
</body>
</html>
```

---

## Instruções para o Claude ao usar este template

1. **Copie o template HTML completo** acima como base.
2. **Substitua `{{TITULO_APRESENTACAO}}`** pelo título real.
3. **Insira os slides dentro de `<div id="stage">`** usando as classes CSS dos tipos acima.
4. **O primeiro slide deve ter a classe `active`.**
5. **Preencha o array `notes`** no JavaScript com as notas do apresentador — uma string por slide, mesma ordem.
6. **Cada slide termina com:**
   ```html
   <div class="slide-num">N / T</div>
   <div class="wordmark">INVISIBLE</div>
   ```
7. **Convenções de conteúdo:**
   - Títulos de slide: `<h2>` dentro de `.slide-top`, em `Space Grotesk` via classe `.slide-[tipo]`
   - Labels de seção: `<div class="label">TEXTO</div>` antes do `<h2>`
   - Destaques em coral: `<span style="color:var(--coral)">...</span>` ou `<strong>` quando apropriado
   - Elementos em `Playfair Display`: use apenas em slides de capa, citação, fechamento e número destaque
   - Sem emojis, sem ícones decorativos, sem gradientes, sem border-radius > 2px

### Exemplo — Slide de conteúdo com bullets:
```html
<div class="slide slide-content active">
  <div class="slide-top">
    <div class="label">Seção</div>
    <h2>Título do slide.</h2>
  </div>
  <ul>
    <li>Primeiro ponto com informação concreta e <strong>destaque em branco</strong></li>
    <li>Segundo ponto que expande ou contrasta</li>
    <li>Terceiro ponto conclusivo</li>
  </ul>
  <div class="slide-num">1 / 10</div>
  <div class="wordmark">INVISIBLE</div>
</div>
```

### Exemplo — Slide de capa:
```html
<div class="slide slide-cover active">
  <div class="pre label">Label da apresentação</div>
  <h1>Título Principal<br>da Apresentação.</h1>
  <div class="sub">Subtítulo ou data · contexto</div>
  <div class="slide-num">1 / 10</div>
  <div class="wordmark">INVISIBLE</div>
</div>
```

### Exemplo — Slide de fechamento com citação:
```html
<div class="slide slide-closing">
  <blockquote>"A frase de impacto que resume<br>o espírito da reunião ou projeto."</blockquote>
  <div class="author">Nome · Contexto</div>
  <div class="next">
    <div class="next-label">Próximo passo</div>
    <div class="next-val">Reunião Dia 2 · Data · Hora</div>
  </div>
  <div class="slide-num">10 / 10</div>
  <div class="wordmark">INVISIBLE</div>
</div>
```
