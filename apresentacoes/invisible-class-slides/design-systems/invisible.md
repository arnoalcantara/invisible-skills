# Design System: INVISIBLE — Didático (aula ao vivo)

> A identidade Invisible aplicada a **slides de aula projetados ao vivo**. Mantém o craft editorial escuro da marca, mas eleva o **piso de legibilidade** (lei 11): tipografia maior, contraste alto, um acento só. Os tipos de slide aqui correspondem à tipologia didática da skill, não a um deck de vendas.
> Versão: junho 2026.

---

## Princípio visual

O design serve às 13 leis da skill ([../skills/invisible-class-slides/references/filosofia.md](../skills/invisible-class-slides/references/filosofia.md)), nesta ordem de prioridade:

- **Legível do fundo da sala** (lei 11): corpo nunca abaixo de ~24px na escala 1280×720; títulos grandes; contraste alto.
- **Um ponto focal** (lei 4): hierarquia explícita por tamanho/cor/posição.
- **Espaço em branco é estrutura** (lei 10): respiro generoso; nada de tela cheia de texto.
- **Acento único** (coral) reservado para o que importa — nunca decorativo (lei 3).
- **Revelação progressiva nativa** (lei 8): o player suporta `fragment` para builds passo a passo.

**Modo padrão:** escuro (expressão nativa da marca). Para salas muito claras, troque `--near-black` por um fundo claro e inverta os tokens de texto — o sistema é montado em variáveis para isso.

---

## Paleta de cores

```css
/* Fundos */
--black:          #000000;   /* capas, fechamento, citação */
--near-black:     #111111;   /* fundo padrão de slide */
--surface-1:      #1C1C1C;   /* caixas, cards */
--surface-2:      #252525;   /* segundo nível */

/* Bordas */
--border:         #333333;
--border-subtle:  #2A2A2A;

/* Texto */
--white:          #FFFFFF;   /* texto primário / asserções */
--silver:         #D2D2D2;   /* texto secundário (mais claro que o brand p/ legibilidade de sala) */
--muted:          #8A8A8A;   /* labels, terciário */

/* Acento */
--coral:          #E85043;   /* único acento — ênfase, destaque, "certo" */
--coral-dim:      #6E2A24;   /* acento esmaecido p/ estados/contraste */
```

**Regras de cor:**
- Sem gradientes em fundos; profundidade por camadas (`#111` → `#1C1C1C` → `#252525`), não por sombra.
- Coral só em ênfase singular (a asserção-chave, o passo crítico, o "certo" de um erro comum).
- Distinções de conteúdo (certo/errado, A/B) **nunca** dependem só de cor — use também posição, rótulo ou forma (acessibilidade).

---

## Tipografia

```css
--font-display:  'Playfair Display', Georgia, serif;      /* asserções de capa, citações, número grande */
--font-ui:       'DM Sans', system-ui, sans-serif;        /* corpo, listas, rótulos de conteúdo */
--font-label:    'Space Grotesk', system-ui, sans-serif;  /* labels, títulos-asserção, UI */
```

**Import (Google Fonts):**
```
https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,900;1,400;1,700&family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,700&family=Space+Grotesk:wght@500;700&display=swap
```

**Usos e tamanhos (escala 1280×720):**
- *Título-asserção do slide:* `Space Grotesk` 700, 34–40px. É a frase que afirma a ideia (lei 2) — sempre presente.
- *Corpo / itens:* `DM Sans` 400–500, **24–28px** (piso de legibilidade).
- *Número grande / display:* `Playfair Display` 900, 96–140px.
- *Citação:* `Playfair Display` italic, 34–40px.
- *Label / tag:* `Space Grotesk` 700, 12–13px, uppercase, letter-spacing 0.14em, cor coral ou muted.

---

## Fundamentos visuais

- **Border radius:** 0px (flat). Máx. 2px.
- **Sombras:** nenhuma.
- **Espaçamento:** generoso. Margens internas de slide 56–80px.
- **Alinhamento:** esquerda ou centralizado. Nunca justificado.
- **Animações:** fades de opacidade, 150–200ms ease-out. Builds entram suaves; sem bounce.
- **Emojis / ícones decorativos:** nunca. Ícones só funcionais e geométricos.

---

## Tipos de slide → tipologia didática

Cada tipo da tipologia mapeia para uma classe CSS. Tipos parentes compartilham classe (um molde serve vários).

| Classe CSS | Tipos da tipologia que atende |
|---|---|
| `.slide-cover` | abertura-titulo |
| `.slide-assert` | asseracao-evidencia (padrão), definicao, declaracao-soco, exemplo-caso, analogia-metafora |
| `.slide-list` | objetivos, roteiro-agenda, sintese, recursos-referencias, takeaway (variante) |
| `.slide-two-col` | comparacao-lado-a-lado, trade-off-pros-contras, antes-depois, venn-sobreposicao |
| `.slide-diagram` | passo-a-passo, causa-efeito, ciclo-loop, arvore-de-decisao, taxonomia-hierarquia, anatomia-diagrama-rotulado, progressao-jornada |
| `.slide-timeline` | linha-do-tempo, espectro-continuum |
| `.slide-number` | numero-grande, destaque-sobre-dado |
| `.slide-chart` | grafico, infografico (chart real em SVG/código) |
| `.slide-image` | imagem-tela-cheia, imagem-texto, exemplo-anotado |
| `.slide-prompt` | pergunta-provocacao, predicao, enquete, problema-para-resolver, preencher-lacuna, pense-converse-compartilhe, verificacao-entendimento |
| `.slide-quote` | citacao-autoridade |
| `.slide-divider` | divisor-secao, voce-esta-aqui, ponte-transicao, ativacao-conhecimento-previo, erro-comum (variante), mnemonico |
| `.slide-closing` | fechamento da aula |

> A skill escolhe o **tipo** pela tipologia; aqui ela encontra a **classe** para renderizar. Se um tipo precisar de layout que nenhuma classe cobre bem, componha com utilitários (`.label`, `.assert-title`, `.fragment`) mantendo as regras acima.

---

## Revelação progressiva (builds)

Qualquer elemento com a classe `fragment` começa invisível e é revelado um a um pelas setas, **antes** de avançar para o próximo slide. É como as leis 8 e 12 (predição, passo a passo, revelar resposta) vivem no HTML.

```html
<li class="fragment">Revelado no segundo avanço</li>
<div class="fragment">Revelado no terceiro avanço</div>
```

---

## Template HTML base

Use como estrutura raiz. Preencha os slides em `<div id="stage">`. O player já tem navegação por teclado, **builds por fragment**, notas do professor, fullscreen e escala responsiva.

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{TITULO_AULA}}</title>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,900;1,400;1,700&family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,700&family=Space+Grotesk:wght@500;700&display=swap" rel="stylesheet">
<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
:root {
  --black:#000; --near-black:#111; --surface-1:#1C1C1C; --surface-2:#252525;
  --border:#333; --border-subtle:#2A2A2A;
  --white:#FFF; --silver:#D2D2D2; --muted:#8A8A8A;
  --coral:#E85043; --coral-dim:#6E2A24;
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

/* Utilities */
.label { font-family:var(--font-label); font-size:13px; font-weight:700; letter-spacing:0.14em; text-transform:uppercase; color:var(--coral); }
.label-muted { font-family:var(--font-label); font-size:13px; font-weight:500; letter-spacing:0.14em; text-transform:uppercase; color:var(--muted); }
.assert-title { font-family:var(--font-label); font-size:38px; font-weight:700; line-height:1.15; letter-spacing:-0.01em; color:var(--white); }
.wordmark { position:absolute; bottom:26px; right:38px; font-family:var(--font-label); font-size:11px; font-weight:700; letter-spacing:0.16em; text-transform:uppercase; color:rgba(255,255,255,0.08); user-select:none; }
.slide-num { position:absolute; bottom:26px; left:38px; font-family:var(--font-label); font-size:11px; font-weight:500; letter-spacing:0.1em; color:rgba(255,255,255,0.22); }
.coral { color:var(--coral); }

/* Cover */
.slide-cover { background:var(--black); flex-direction:column; justify-content:flex-end; padding:80px 96px 92px; }
.slide-cover .pre { margin-bottom:28px; }
.slide-cover h1 { font-family:var(--font-display); font-size:76px; font-weight:900; line-height:1.02; letter-spacing:-0.03em; margin-bottom:24px; }
.slide-cover .hook { font-family:var(--font-ui); font-size:26px; font-weight:400; color:var(--silver); }

/* Assert + evidence (workhorse) */
.slide-assert { flex-direction:column; padding:64px 80px; }
.slide-assert .top { margin-bottom:36px; }
.slide-assert .evidence { flex:1; display:flex; flex-direction:column; justify-content:center; gap:18px; }
.slide-assert .evidence p { font-family:var(--font-ui); font-size:26px; line-height:1.5; color:var(--silver); max-width:1000px; }
.slide-assert .evidence strong { color:var(--white); font-weight:600; }

/* List (objetivos, roteiro, síntese) */
.slide-list { flex-direction:column; padding:64px 80px; }
.slide-list .top { margin-bottom:36px; }
.slide-list ul { list-style:none; display:flex; flex-direction:column; gap:18px; }
.slide-list li { font-family:var(--font-ui); font-size:26px; color:var(--silver); line-height:1.4; padding-left:26px; position:relative; }
.slide-list li::before { content:''; position:absolute; left:0; top:14px; width:11px; height:2px; background:var(--coral); }
.slide-list li strong { color:var(--white); font-weight:600; }

/* Two columns (comparação, trade-off, antes/depois) */
.slide-two-col { flex-direction:column; padding:56px 72px; }
.slide-two-col .top { margin-bottom:32px; }
.slide-two-col .cols { flex:1; display:flex; gap:0; }
.slide-two-col .col { flex:1; padding:8px 40px; display:flex; flex-direction:column; gap:16px; border-right:1px solid var(--border-subtle); }
.slide-two-col .col:last-child { border-right:none; }
.slide-two-col .col h3 { font-family:var(--font-label); font-size:15px; font-weight:700; letter-spacing:0.1em; text-transform:uppercase; color:var(--muted); }
.slide-two-col .col .row { font-family:var(--font-ui); font-size:23px; color:var(--silver); line-height:1.4; }
.slide-two-col .col .row strong { color:var(--white); font-weight:600; }

/* Diagram / flow (passo a passo, causa-efeito, anatomia, etc.) */
.slide-diagram { flex-direction:column; padding:56px 72px; }
.slide-diagram .top { margin-bottom:40px; }
.slide-diagram .flow { display:flex; align-items:stretch; gap:0; flex:1; }
.slide-diagram .fbox { background:var(--surface-1); border:1px solid var(--border); flex:1; display:flex; flex-direction:column; padding:26px 24px; gap:10px; }
.slide-diagram .fbox .fn { font-family:var(--font-display); font-size:40px; font-weight:900; color:rgba(255,255,255,0.1); line-height:1; }
.slide-diagram .fbox .ftitle { font-family:var(--font-label); font-size:20px; font-weight:700; color:var(--white); }
.slide-diagram .fbox .fsub { font-family:var(--font-ui); font-size:18px; color:var(--silver); line-height:1.45; }
.slide-diagram .arrow { width:44px; flex-shrink:0; display:flex; align-items:center; justify-content:center; color:var(--border); font-size:22px; }

/* Timeline / spectrum */
.slide-timeline { flex-direction:column; padding:64px 80px; }
.slide-timeline .top { margin-bottom:48px; }
.slide-timeline .axis { flex:1; display:flex; align-items:center; }
.slide-timeline .track { width:100%; height:2px; background:var(--border); position:relative; display:flex; justify-content:space-between; }
.slide-timeline .mark { position:relative; top:-7px; display:flex; flex-direction:column; align-items:center; gap:10px; }
.slide-timeline .dot { width:14px; height:14px; border-radius:50%; background:var(--coral); }
.slide-timeline .mark .date { font-family:var(--font-label); font-size:18px; font-weight:700; color:var(--white); }
.slide-timeline .mark .ev { font-family:var(--font-ui); font-size:17px; color:var(--silver); max-width:170px; text-align:center; }

/* Number / highlight */
.slide-number { flex-direction:row; }
.slide-number .num-left { width:480px; flex-shrink:0; background:var(--black); display:flex; flex-direction:column; justify-content:center; padding:72px 60px; border-right:1px solid var(--border-subtle); }
.slide-number .big { font-family:var(--font-display); font-size:132px; font-weight:900; line-height:1; letter-spacing:-0.04em; color:var(--coral); }
.slide-number .unit { font-family:var(--font-ui); font-size:22px; color:var(--silver); margin-top:12px; }
.slide-number .num-right { flex:1; display:flex; flex-direction:column; justify-content:center; padding:64px 64px; gap:20px; }
.slide-number .num-right .assert-title { font-size:34px; }

/* Chart (real chart in SVG/code goes inside .chart-area) */
.slide-chart { flex-direction:column; padding:56px 72px; }
.slide-chart .top { margin-bottom:28px; }
.slide-chart .chart-area { flex:1; display:flex; align-items:center; justify-content:center; }

/* Image */
.slide-image { padding:0; }
.slide-image img, .slide-image .imgfill { width:100%; height:100%; object-fit:cover; }
.slide-image .overlay { position:absolute; left:0; bottom:0; right:0; padding:56px 72px; background:linear-gradient(to top, rgba(0,0,0,0.85), transparent); }
.slide-image.split { display:flex; }
.slide-image.split .imghalf { width:50%; height:100%; }
.slide-image.split .txthalf { width:50%; padding:64px 56px; display:flex; flex-direction:column; justify-content:center; background:var(--near-black); }

/* Prompt (active processing) */
.slide-prompt { background:var(--black); flex-direction:column; justify-content:center; align-items:flex-start; padding:80px 96px; }
.slide-prompt .label { margin-bottom:28px; }
.slide-prompt .q { font-family:var(--font-display); font-size:48px; font-weight:700; line-height:1.2; color:var(--white); max-width:980px; }
.slide-prompt .options { margin-top:36px; display:flex; flex-direction:column; gap:14px; }
.slide-prompt .opt { font-family:var(--font-ui); font-size:24px; color:var(--silver); }

/* Quote */
.slide-quote { background:var(--black); flex-direction:column; justify-content:center; align-items:flex-start; padding:80px 96px; }
.slide-quote blockquote { font-family:var(--font-display); font-size:40px; font-weight:400; font-style:italic; color:var(--white); line-height:1.4; max-width:920px; margin-bottom:28px; }
.slide-quote .author { font-family:var(--font-label); font-size:15px; font-weight:700; letter-spacing:0.12em; text-transform:uppercase; color:var(--coral); }

/* Divider / transition / you-are-here / common-error / mnemonic */
.slide-divider { background:var(--surface-1); flex-direction:column; justify-content:center; align-items:flex-start; padding:80px 96px; }
.slide-divider .kicker { font-family:var(--font-label); font-size:15px; font-weight:700; letter-spacing:0.16em; text-transform:uppercase; color:var(--coral); margin-bottom:20px; }
.slide-divider h2 { font-family:var(--font-display); font-size:54px; font-weight:900; line-height:1.08; color:var(--white); max-width:980px; }

/* Closing */
.slide-closing { background:var(--black); flex-direction:column; justify-content:center; align-items:flex-start; padding:80px 96px; }
.slide-closing blockquote { font-family:var(--font-display); font-size:40px; font-style:italic; color:var(--white); line-height:1.4; max-width:900px; margin-bottom:28px; }
.slide-closing .next { border-top:1px solid var(--border); padding-top:28px; margin-top:32px; }
.slide-closing .next .next-label { font-family:var(--font-label); font-size:13px; font-weight:700; letter-spacing:0.16em; text-transform:uppercase; color:var(--muted); margin-bottom:8px; }
.slide-closing .next .next-val { font-family:var(--font-label); font-size:20px; font-weight:700; color:var(--white); }

/* Player */
#notes-bar { position:fixed; bottom:0; left:0; right:0; background:rgba(0,0,0,0.96); color:var(--silver); font-size:16px; font-family:var(--font-ui); line-height:1.5; padding:16px 28px; display:none; z-index:100; border-top:1px solid var(--border-subtle); }
#notes-bar.visible { display:block; }
#notes-bar strong { color:var(--coral); font-weight:600; }
#controls { position:fixed; top:14px; right:20px; display:flex; gap:8px; z-index:100; align-items:center; }
#controls button { background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.1); color:rgba(255,255,255,0.5); font-size:11px; font-family:var(--font-label); font-weight:500; letter-spacing:0.1em; text-transform:uppercase; padding:6px 12px; cursor:pointer; }
#controls button:hover { background:rgba(255,255,255,0.1); color:#fff; }
#counter { color:rgba(255,255,255,0.3); font-size:12px; font-family:var(--font-label); }
#progress { position:fixed; top:0; left:0; height:3px; background:var(--coral); transition:width 0.25s ease-out; z-index:200; }
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
  if (current < total-1) { current++; frag = fragsOf(slides[current]).length && 0; frag = 0; render(); }
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
2. **Substitua `{{TITULO_AULA}}`** pelo título real.
3. **Insira os slides em `<div id="stage">`**, mapeando o **tipo da tipologia** para a **classe CSS** (tabela acima). O título de todo slide de conteúdo é um **`.assert-title` em frase completa** (lei 2).
4. **Primeiro slide com classe `active`.**
5. **Builds:** marque com `class="fragment"` os elementos que devem ser revelados passo a passo (passos de um processo, opções de uma pergunta, resposta de um quiz, linhas de uma comparação). As setas revelam um a um antes de trocar de slide. Use builds onde a ficha do tipo recomenda.
6. **Preencha o array `notes`** — uma string por slide, na ordem. As notas carregam o que a voz do professor diz (lei 6): o difícil de mostrar, não o que está na tela.
7. **Cada slide termina com:**
   ```html
   <div class="slide-num">N / T</div>
   <div class="wordmark">INVISIBLE</div>
   ```
8. **Gráficos** (`.slide-chart`): renderize o chart **de verdade** em SVG/HTML dentro de `.chart-area` — nunca uma imagem de gráfico gerada (a regra de ouro da produção visual).
9. Sem emojis, sem ícones decorativos, sem gradiente (exceto o overlay de imagem), sem border-radius > 2px.

### Exemplo — Asserção + evidência (workhorse), com build
```html
<div class="slide slide-assert active">
  <div class="top"><div class="label">Pressão atmosférica</div>
    <div class="assert-title">A pressão do ar cai conforme a altitude sobe.</div></div>
  <div class="evidence">
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
    <div class="opt fragment">a) Sobe mais alta</div>
    <div class="opt fragment">b) Apaga</div>
    <div class="opt fragment">c) Vira uma esfera</div>
  </div>
  <div class="slide-num">9 / 18</div><div class="wordmark">INVISIBLE</div>
</div>
```
