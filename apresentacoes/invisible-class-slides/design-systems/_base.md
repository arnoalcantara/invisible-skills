# Base de composição — máquina compartilhada (partial)

> **Não é um design system selecionável.** O prefixo `_` marca isto como um *partial*: a skill **não** o oferece como brand no arranque (Fase 0 ignora arquivos `_…`). É a **camada de composição** — a estrutura, o layout e o player — herdada por **todos** os brands.
>
> **Divisão de responsabilidade.** Aqui mora *como o slide se monta* (layouts, densidade, hierarquia, grid, primitivos, player) — escrito **só com variáveis** (`var(--…)`), sem nenhuma cor ou fonte literal. Um brand (`invisible.md` e futuros) é só o **skin**: define os tokens (`:root`) e o tratamento. Brand novo = redefinir tokens, herdar toda esta composição.
>
> **O ofício** que decide *quando* usar cada layout, variante e primitivo vive em [../skills/invisible-class-slides/references/composicao-visual.md](../skills/invisible-class-slides/references/composicao-visual.md). Esta base é o ferramental; a reference é a mão.
>
> Versão: junho 2026.

---

## Contrato de tokens (o que todo brand precisa definir)

O brand fornece um bloco `:root` com **todos** estes tokens. A base referencia só `var(--…)` — se um token faltar, o fallback declarado aqui no `:root` da base entra (e o visual degrada com elegância, não quebra).

**Obrigatórios (o skin de fato):**

```
/* Fundos — do mais escuro ao mais claro (profundidade por camadas) */
--bg-0     /* capa, citação, fechamento (mais escuro) */
--bg-1     /* fundo padrão de slide */
--surface-1, --surface-2   /* caixas, cards */

/* Bordas */
--border, --border-subtle

/* Texto — primário ao terciário */
--ink-1    /* texto primário / asserções */
--ink-2    /* texto secundário */
--ink-3    /* labels, terciário */

/* Acento — um só */
--accent, --accent-dim

/* Fontes */
--font-display   /* asserções-herói, citações, número grande */
--font-ui        /* corpo, listas */
--font-label     /* labels, títulos-asserção, UI */
--font-link      /* a tag <link> do Google Fonts (ou @font-face) */

/* Wordmark — texto da marca no rodapé do slide */
--wordmark-text  /* via conteúdo; o brand informa a string */
```

**Estruturais (já têm default nesta base; o brand sobrescreve só se quiser outro ritmo):**

```
/* Escala de espaçamento — 8-pt, o vocabulário do grid */
--s-1:8px;  --s-2:12px; --s-3:16px; --s-4:24px;
--s-5:32px; --s-6:48px; --s-7:64px; --s-8:80px;

/* Padding-padrão do slide e raio */
--pad-slide: var(--s-7) var(--s-8);
--radius: 0px;            /* flat; máx. 2px */
```

> **Regra dura:** a base nunca cita `#E85043`, `Playfair`, `coral`. Só `var(--accent)`, `var(--font-display)`. É isso que torna a composição portável.

---

## Como a skill monta o HTML (render)

O HTML final é **um arquivo auto-contido** = **base + skin**, montado assim:

1. Pegue o **esqueleto** desta base (abaixo).
2. No `<head>`, injete o `{{FONT_LINKS}}` e o bloco `:root { … }` **do brand escolhido** (os tokens). Eles entram **depois** do `:root` de defaults da base — assim o brand vence no cascade.
3. Mantenha **todo o CSS estrutural** desta base como está (ele só usa `var(--…)`).
4. Insira os slides em `<div id="stage">`, mapeando o **tipo da tipologia** para a **classe** (a tabela tipo→classe vive no brand).
5. Preencha o array `notes` (uma string por slide).
6. A base não vira dependência externa: o conteúdo dela é **inlinado** no arquivo final.

---

## Builds (revelação progressiva — lei 8)

Qualquer elemento com `class="fragment"` começa invisível e é revelado um a um pelas setas, **antes** de avançar para o próximo slide.

```html
<li class="fragment">Revelado no segundo avanço</li>
```

---

## Esqueleto + CSS estrutural + player

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{TITULO_AULA}}</title>
{{FONT_LINKS}}
<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

/* === DEFAULTS DA BASE (o brand sobrescreve com seu :root logo abaixo) === */
:root {
  --s-1:8px; --s-2:12px; --s-3:16px; --s-4:24px; --s-5:32px; --s-6:48px; --s-7:64px; --s-8:80px;
  --pad-slide: var(--s-7) var(--s-8);
  --radius: 0px;
}

{{ROOT_TOKENS}}  /* <-- bloco :root do brand: paleta, fontes, escala (opcional) */

/* ===================== ESTRUTURA (portável, só var()) ===================== */
body { background:#0a0a0a; display:flex; align-items:center; justify-content:center; min-height:100vh; overflow:hidden; font-family:var(--font-ui); }
#stage { position:fixed; width:1280px; height:720px; transform-origin:center center; }
.slide { display:none; position:absolute; inset:0; width:1280px; height:720px; background:var(--bg-1); color:var(--ink-1); overflow:hidden; padding:var(--pad-slide); }
.slide.active { display:flex; flex-direction:column; }
.fragment { opacity:0; transition:opacity .18s ease-out; }
.fragment.shown { opacity:1; }

/* --- Utilitários de texto --- */
.label { font-family:var(--font-label); font-size:13px; font-weight:700; letter-spacing:0.14em; text-transform:uppercase; color:var(--accent); }
.label-muted { font-family:var(--font-label); font-size:13px; font-weight:500; letter-spacing:0.14em; text-transform:uppercase; color:var(--ink-3); }
.assert-title { font-family:var(--font-label); font-size:38px; font-weight:700; line-height:1.15; letter-spacing:-0.01em; color:var(--ink-1); }
.assert-title.tight { font-size:clamp(30px,3vw,34px); line-height:1.2; max-width:22ch; }   /* asserção curta: 1–2 linhas, sem competir com o corpo */
.accent { color:var(--accent); }
/* Ênfase sem caixa: liderar com tipografia em vez de moldura. Use dentro de .evidence / .slide-list,
   ou como bloco esparso. A palavra-chave vira acento com <span class="accent"> (um só ponto de cor). */
.emphasis { font-family:var(--font-display); font-weight:900; font-size:clamp(34px,4.4vw,52px); line-height:1.12; letter-spacing:-0.02em; color:var(--ink-1); max-width:20ch; }
.wordmark { position:absolute; bottom:26px; right:38px; font-family:var(--font-label); font-size:11px; font-weight:700; letter-spacing:0.16em; text-transform:uppercase; color:rgba(255,255,255,0.08); user-select:none; }
.slide-num { position:absolute; bottom:26px; left:38px; font-family:var(--font-label); font-size:11px; font-weight:500; letter-spacing:0.1em; color:rgba(255,255,255,0.22); }

/* --- Primitivos estruturais (preencher o quadro COM FUNÇÃO, nunca ornamento) --- */
.accent-bar { width:48px; height:4px; background:var(--accent); flex-shrink:0; }
.accent-bar.tall { width:4px; height:auto; align-self:stretch; }
.rule { height:1px; background:var(--border-subtle); width:100%; }
.kicker-band { display:flex; align-items:center; gap:var(--s-3); }
.index-numeral { font-family:var(--font-display); font-weight:900; font-size:clamp(96px,16vw,180px); line-height:0.8; color:var(--accent-dim); letter-spacing:-0.04em; }

/* ===================== LAYOUTS DE SLIDE ===================== */

/* --- Cover --- */
.slide-cover { background:var(--bg-0); justify-content:flex-end; padding:80px 96px 92px; }
.slide-cover .pre { margin-bottom:28px; }
.slide-cover h1 { font-family:var(--font-display); font-size:76px; font-weight:900; line-height:1.02; letter-spacing:-0.03em; margin-bottom:24px; }
.slide-cover .hook { font-family:var(--font-ui); font-size:26px; font-weight:400; color:var(--ink-2); max-width:1000px; }

/* --- Assert + evidência (workhorse) ---
   default: top-anchored (título em cima, evidência preenche abaixo, alinhada ao topo).
   .center: evidência centrada no vertical (use só quando a evidência é 1 bloco visual dominante).
   .hero:   asserção-herói que É o slide (declaração-soco, slide esparso). */
.slide-assert .top { margin-bottom:var(--s-5); }
.slide-assert .evidence { flex:1; display:flex; flex-direction:column; justify-content:flex-start; gap:var(--s-4); min-height:0; }
.slide-assert.center .evidence { justify-content:center; }
.slide-assert .evidence p { font-family:var(--font-ui); font-size:26px; line-height:1.5; color:var(--ink-2); max-width:1000px; }
.slide-assert .evidence p.lead { font-size:30px; color:var(--ink-1); }   /* linha primária da evidência */
.slide-assert .evidence strong { color:var(--ink-1); font-weight:600; }
/* asserção-herói: enche o quadro escalando o foco, em vez de centralizar texto magro */
.slide-assert.hero { justify-content:center; gap:var(--s-5); }
.slide-assert.hero .assert-lead { font-family:var(--font-display); font-size:clamp(48px,6.2vw,76px); font-weight:900; line-height:1.06; letter-spacing:-0.02em; color:var(--ink-1); max-width:18ch; }
.slide-assert.hero .sub { font-family:var(--font-ui); font-size:26px; color:var(--ink-2); max-width:760px; }
/* numbered: numeral grande como âncora posicional (top-left), dá segundo registro à frase esparsa */
.slide-assert.numbered .top { display:flex; align-items:flex-start; gap:var(--s-5); }
.slide-assert.numbered .top .index-numeral { font-size:clamp(64px,8vw,104px); flex-shrink:0; }
.slide-assert.numbered .top .top-text { display:flex; flex-direction:column; gap:var(--s-2); padding-top:var(--s-2); }

/* --- List (objetivos, roteiro, síntese, takeaway) ---
   gap deriva da escala; .lead (poucos itens, grandes) preenche o quadro; .dense aperta.
   .li-sub = linha secundária sob um item (sub-hierarquia). */
.slide-list .top { margin-bottom:var(--s-5); }
.slide-list ul { list-style:none; flex:1; display:flex; flex-direction:column; justify-content:flex-start; gap:var(--s-4); min-height:0; }
.slide-list.center ul { justify-content:center; }
.slide-list li { font-family:var(--font-ui); font-size:26px; color:var(--ink-2); line-height:1.4; padding-left:26px; position:relative; }
.slide-list li::before { content:''; position:absolute; left:0; top:14px; width:11px; height:2px; background:var(--accent); }
.slide-list li strong { color:var(--ink-1); font-weight:600; }
.slide-list li .li-sub { display:block; font-size:20px; color:var(--ink-3); line-height:1.4; margin-top:6px; }
.slide-list.lead ul { gap:var(--s-5); }
.slide-list.lead li { font-size:34px; color:var(--ink-1); }
.slide-list.dense ul { gap:var(--s-3); }
.slide-list.dense li { font-size:23px; }

/* --- Two columns (comparação, trade-off, antes/depois, venn) ---
   respiro vertical real; header de coluna com presença; agrupamento por .row-group;
   .row.primary destaca a linha-chave; .verdict é o rodapé de veredito de uma coluna. */
.slide-two-col .top { margin-bottom:var(--s-4); }
.slide-two-col .cols { flex:1; display:flex; gap:0; min-height:0; }
.slide-two-col .col { flex:1; padding:var(--s-4) var(--s-6); display:flex; flex-direction:column; justify-content:center; gap:var(--s-3); border-right:1px solid var(--border-subtle); }
.slide-two-col .col:last-child { border-right:none; }
.slide-two-col .col h3 { font-family:var(--font-label); font-size:18px; font-weight:700; letter-spacing:0.08em; text-transform:uppercase; color:var(--ink-2); margin-bottom:var(--s-2); }
.slide-two-col .col .row { font-family:var(--font-ui); font-size:23px; color:var(--ink-2); line-height:1.4; }
.slide-two-col .col .row.primary { font-size:26px; color:var(--ink-1); font-weight:600; }
.slide-two-col .col .row strong { color:var(--ink-1); font-weight:600; }
.slide-two-col .col .row-group { display:flex; flex-direction:column; gap:6px; }
.slide-two-col .col .verdict { margin-top:auto; padding-top:var(--s-3); border-top:1px solid var(--border-subtle); font-family:var(--font-label); font-size:16px; text-transform:uppercase; letter-spacing:0.08em; color:var(--accent); }

/* --- Diagram / flow (passo a passo, causa-efeito, anatomia, taxonomia, ciclo) ---
   row (até 4 caixas) com setas, OU .grid (5-6 caixas → 3x2 / 2x2) sem setas.
   .fbox tem padding real; .fbox.critical destaca o passo-chave;
   .fn vira índice ESTRUTURAL legível (peso e foco), não fundo a 10%. */
.slide-diagram .top { margin-bottom:var(--s-5); }
.slide-diagram .flow { display:flex; align-items:stretch; gap:var(--s-3); flex:1; min-height:0; }
.slide-diagram .flow.grid { display:grid; grid-template-columns:repeat(3,1fr); grid-auto-rows:1fr; gap:var(--s-3); align-items:stretch; }
.slide-diagram .flow.grid.cols-2 { grid-template-columns:repeat(2,1fr); }
.slide-diagram .fbox { background:var(--surface-1); border:1px solid var(--border); border-radius:var(--radius); flex:1; display:flex; flex-direction:column; padding:var(--s-5) var(--s-4); gap:var(--s-2); }
.slide-diagram .fbox.critical { border-color:var(--accent); background:var(--surface-2); }
/* Tratamentos de caixa — escolha um por função (varie entre slides; a borda-padrão não é default por inércia) */
.slide-diagram .fbox.fill { border:none; background:var(--surface-1); }                                    /* preenchida, sem borda */
.slide-diagram .fbox.hairline { border:1px solid var(--border-subtle); background:transparent; }            /* só linha fina */
.slide-diagram .fbox.edge { border:none; background:transparent; border-left:3px solid var(--accent); padding-left:var(--s-4); }   /* uma aresta de acento */
.slide-diagram .fbox .fn { font-family:var(--font-display); font-size:44px; font-weight:900; color:var(--accent-dim); line-height:1; }
.slide-diagram .fbox.critical .fn { color:var(--accent); }
.slide-diagram .fbox .ftitle { font-family:var(--font-label); font-size:21px; font-weight:700; color:var(--ink-1); line-height:1.2; }
.slide-diagram .fbox .fsub { font-family:var(--font-ui); font-size:18px; color:var(--ink-2); line-height:1.45; }
.slide-diagram .arrow { width:40px; flex-shrink:0; display:flex; align-items:center; justify-content:center; color:var(--border); font-size:22px; }

/* --- flow.chain: cadeia causal (causa-efeito) ---
   .cnode SEM borda (palavra-chave sobre um tick de acento), ligados por .carrow (linha+seta em --accent-dim).
   .cnode.turn marca o elo de virada; .carrow-label nomeia o nexo; .chain.vertical para cadeias longas/builds. */
.slide-diagram .flow.chain { align-items:center; gap:0; }
.slide-diagram .flow.chain .cnode { flex:1; display:flex; flex-direction:column; gap:var(--s-2); padding:0 var(--s-3); border:none; background:transparent; min-width:0; }
.slide-diagram .flow.chain .cnode::before { content:''; display:block; width:28px; height:3px; background:var(--accent-dim); margin-bottom:var(--s-2); }
.slide-diagram .flow.chain .cnode.turn::before { background:var(--accent); }
.slide-diagram .flow.chain .cnode .clabel { font-family:var(--font-label); font-size:22px; font-weight:700; color:var(--ink-1); line-height:1.2; }
.slide-diagram .flow.chain .cnode.turn .clabel { color:var(--accent); }
.slide-diagram .flow.chain .cnode .csub { font-family:var(--font-ui); font-size:17px; color:var(--ink-2); line-height:1.4; }
.slide-diagram .flow.chain .carrow { flex-shrink:0; width:52px; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:6px; color:var(--accent-dim); }
.slide-diagram .flow.chain .carrow svg { width:48px; height:14px; display:block; }
.slide-diagram .flow.chain .carrow .carrow-label { font-family:var(--font-label); font-size:11px; font-weight:500; letter-spacing:0.08em; text-transform:uppercase; color:var(--ink-3); text-align:center; line-height:1.2; max-width:84px; }
.slide-diagram .flow.chain.vertical { flex-direction:column; align-items:stretch; justify-content:center; }
.slide-diagram .flow.chain.vertical .cnode { flex:none; padding:var(--s-2) 0; }
.slide-diagram .flow.chain.vertical .carrow { width:100%; height:34px; flex-direction:row; gap:var(--s-3); }
.slide-diagram .flow.chain.vertical .carrow svg { transform:rotate(90deg); }

/* --- flow.cycle: processo que retorna ao início (ciclo-loop) ---
   3–6 .cnode posicionados num anel (.pos-1..6) sobre um caminho circular SVG (.cycle-svg) em --accent-dim.
   Para 3 nós use pos-1/3/5; para 4 use pos-1/2/4/5; para 6 use todos. */
.slide-diagram .flow.cycle { position:relative; display:block; flex:1; min-height:0; }
.slide-diagram .flow.cycle .cycle-svg { position:absolute; inset:0; width:100%; height:100%; color:var(--accent-dim); pointer-events:none; }
.slide-diagram .flow.cycle .cnode { position:absolute; transform:translate(-50%,-50%); display:flex; flex-direction:column; align-items:center; gap:4px; text-align:center; max-width:210px; border:none; background:var(--bg-1); padding:var(--s-2) var(--s-3); }
.slide-diagram .flow.cycle .cnode .clabel { font-family:var(--font-label); font-size:19px; font-weight:700; color:var(--ink-1); line-height:1.2; }
.slide-diagram .flow.cycle .cnode .csub { font-family:var(--font-ui); font-size:15px; color:var(--ink-2); line-height:1.35; }
.slide-diagram .flow.cycle .cnode.turn .clabel { color:var(--accent); }
.slide-diagram .flow.cycle .cnode.pos-1 { top:9%;  left:50%; }
.slide-diagram .flow.cycle .cnode.pos-2 { top:30%; left:88%; }
.slide-diagram .flow.cycle .cnode.pos-3 { top:72%; left:84%; }
.slide-diagram .flow.cycle .cnode.pos-4 { top:91%; left:50%; }
.slide-diagram .flow.cycle .cnode.pos-5 { top:72%; left:16%; }
.slide-diagram .flow.cycle .cnode.pos-6 { top:30%; left:12%; }

/* --- flow.tree: raiz + ramos (taxonomia-hierarquia, arvore-de-decisao) ---
   .troot no topo, .tconnect (haste), .tbranches (ramos lado a lado ligados por uma régua).
   .tree.decision usa .branch-label para rotular ramos (sim/não). */
.slide-diagram .flow.tree { flex-direction:column; align-items:center; justify-content:center; gap:0; }
.slide-diagram .flow.tree .troot { display:flex; flex-direction:column; align-items:center; gap:4px; padding:var(--s-3) var(--s-5); background:var(--surface-1); border-left:3px solid var(--accent); }
.slide-diagram .flow.tree .troot .clabel { font-family:var(--font-label); font-size:21px; font-weight:700; color:var(--ink-1); }
.slide-diagram .flow.tree .tconnect { width:2px; height:var(--s-5); background:var(--border); }
.slide-diagram .flow.tree .tbranches { display:flex; gap:var(--s-5); align-items:flex-start; justify-content:center; position:relative; padding-top:var(--s-4); }
.slide-diagram .flow.tree .tbranches::before { content:''; position:absolute; top:0; left:20%; right:20%; height:2px; background:var(--border); }
.slide-diagram .flow.tree .tbranch { display:flex; flex-direction:column; align-items:center; gap:var(--s-2); flex:1; max-width:280px; position:relative; }
.slide-diagram .flow.tree .tbranch::before { content:''; width:2px; height:var(--s-4); background:var(--border); }
.slide-diagram .flow.tree .tbranch .branch-label { font-family:var(--font-label); font-size:12px; font-weight:700; letter-spacing:0.1em; text-transform:uppercase; color:var(--accent); }
.slide-diagram .flow.tree .tnode { display:flex; flex-direction:column; gap:4px; padding:var(--s-3) var(--s-4); border:1px solid var(--border-subtle); width:100%; }
.slide-diagram .flow.tree .tnode .clabel { font-family:var(--font-label); font-size:19px; font-weight:700; color:var(--ink-1); line-height:1.2; }
.slide-diagram .flow.tree .tnode .csub { font-family:var(--font-ui); font-size:16px; color:var(--ink-2); line-height:1.4; }

/* --- Timeline / spectrum --- */
.slide-timeline .top { margin-bottom:var(--s-6); }
.slide-timeline .axis { flex:1; display:flex; align-items:center; }
.slide-timeline .track { width:100%; height:2px; background:var(--border); position:relative; display:flex; justify-content:space-between; }
.slide-timeline .mark { position:relative; top:-7px; display:flex; flex-direction:column; align-items:center; gap:10px; }
.slide-timeline .dot { width:14px; height:14px; border-radius:50%; background:var(--accent); }
.slide-timeline .mark .date { font-family:var(--font-label); font-size:18px; font-weight:700; color:var(--ink-1); }
.slide-timeline .mark .ev { font-family:var(--font-ui); font-size:17px; color:var(--ink-2); max-width:170px; text-align:center; }

/* --- Number / highlight --- */
.slide-number { flex-direction:row; padding:0; }
.slide-number .num-left { width:480px; flex-shrink:0; background:var(--bg-0); display:flex; flex-direction:column; justify-content:center; padding:72px 60px; border-right:1px solid var(--border-subtle); }
.slide-number .big { font-family:var(--font-display); font-size:132px; font-weight:900; line-height:1; letter-spacing:-0.04em; color:var(--accent); }
.slide-number .unit { font-family:var(--font-ui); font-size:22px; color:var(--ink-2); margin-top:12px; }
.slide-number .num-right { flex:1; display:flex; flex-direction:column; justify-content:center; padding:64px; gap:20px; }
.slide-number .num-right .assert-title { font-size:34px; }

/* --- Contrast (erro-comum, antes-depois) — equívoco vs. correto, ASSIMÉTRICO (não espelhado) ---
   .side.wrong é hairline/esmaecida; .side.right carrega o acento numa aresta + texto pleno.
   Distinção por rótulo + posição + aresta, nunca só cor. .contrast.stack empilha (build erro→correto). */
.slide-contrast .top { margin-bottom:var(--s-5); }
.slide-contrast .sides { flex:1; display:flex; gap:var(--s-5); min-height:0; }
.slide-contrast .side { flex:1; display:flex; flex-direction:column; justify-content:center; gap:var(--s-3); padding:var(--s-5); }
.slide-contrast .side .side-label { font-family:var(--font-label); font-size:14px; font-weight:700; letter-spacing:0.12em; text-transform:uppercase; }
.slide-contrast .side .side-body { font-family:var(--font-ui); font-size:24px; line-height:1.45; }
.slide-contrast .side.wrong { background:transparent; border:1px solid var(--border-subtle); }
.slide-contrast .side.wrong .side-label { color:var(--ink-3); }
.slide-contrast .side.wrong .side-body { color:var(--ink-3); }
.slide-contrast .side.right { background:var(--surface-1); border-left:3px solid var(--accent); }
.slide-contrast .side.right .side-label { color:var(--accent); }
.slide-contrast .side.right .side-body { color:var(--ink-1); }
.slide-contrast.stack .sides { flex-direction:column; gap:var(--s-4); }

/* --- Parallel (paralelo-textos) — dois textos correspondentes + conector de cumprimento ---
   .ptext SEM borda (lê como passagem, display itálico); o .connector central carrega o acento UMA vez. */
.slide-parallel .top { margin-bottom:var(--s-5); }
.slide-parallel .pair { flex:1; display:flex; flex-direction:column; justify-content:center; gap:var(--s-4); min-height:0; }
.slide-parallel .ptext { font-family:var(--font-display); font-size:clamp(24px,2.8vw,32px); font-style:italic; line-height:1.4; color:var(--ink-1); max-width:62ch; }
.slide-parallel .ptext .pref { display:block; font-family:var(--font-label); font-size:13px; font-style:normal; font-weight:700; letter-spacing:0.12em; text-transform:uppercase; color:var(--ink-3); margin-bottom:var(--s-1); }
.slide-parallel .connector { display:flex; align-items:center; gap:var(--s-3); }
.slide-parallel .connector .c-rule { height:1px; background:var(--accent-dim); flex:1; }
.slide-parallel .connector .connector-label { font-family:var(--font-label); font-size:13px; font-weight:700; letter-spacing:0.14em; text-transform:uppercase; color:var(--accent); white-space:nowrap; }
.slide-parallel .connector .c-glyph { width:10px; height:10px; border:2px solid var(--accent); transform:rotate(45deg); flex-shrink:0; }

/* --- Rail — split assimétrico genérico (a moldura que o ofício §6 prega) ---
   .rail-aside (~38%, --bg-0, âncora: numeral/label/assert curta) + .rail-main (evidência). .slide-rail.right inverte. */
.slide-rail { flex-direction:row; padding:0; }
.slide-rail .rail-aside { width:38%; flex-shrink:0; background:var(--bg-0); display:flex; flex-direction:column; justify-content:center; gap:var(--s-3); padding:var(--s-7) var(--s-6); border-right:1px solid var(--border-subtle); }
.slide-rail .rail-main { flex:1; display:flex; flex-direction:column; justify-content:center; gap:var(--s-4); padding:var(--s-7); min-width:0; }
.slide-rail.right { flex-direction:row-reverse; }
.slide-rail.right .rail-aside { border-right:none; border-left:1px solid var(--border-subtle); }

/* --- Chart (chart REAL em SVG/código dentro de .chart-area) --- */
.slide-chart .top { margin-bottom:var(--s-4); }
.slide-chart .chart-area { flex:1; display:flex; align-items:center; justify-content:center; min-height:0; }

/* --- Image --- */
.slide-image { padding:0; }
.slide-image img, .slide-image .imgfill { width:100%; height:100%; object-fit:cover; }
.slide-image .overlay { position:absolute; left:0; bottom:0; right:0; padding:56px 72px; background:linear-gradient(to top, rgba(0,0,0,0.85), transparent); }
.slide-image.split { flex-direction:row; }
.slide-image.split .imghalf { width:50%; height:100%; }
.slide-image.split .txthalf { width:50%; padding:64px 56px; display:flex; flex-direction:column; justify-content:center; background:var(--bg-1); }

/* --- Prompt (processamento ativo) --- */
.slide-prompt { background:var(--bg-0); justify-content:center; align-items:flex-start; padding:80px 96px; }
.slide-prompt .label { margin-bottom:28px; }
.slide-prompt .q { font-family:var(--font-display); font-size:48px; font-weight:700; line-height:1.2; color:var(--ink-1); max-width:980px; }
.slide-prompt .options { margin-top:36px; display:flex; flex-direction:column; gap:14px; }
.slide-prompt .opt { font-family:var(--font-ui); font-size:24px; color:var(--ink-2); }

/* --- Quote --- */
.slide-quote { background:var(--bg-0); justify-content:center; align-items:flex-start; padding:80px 96px; gap:var(--s-5); }
.slide-quote blockquote { font-family:var(--font-display); font-size:40px; font-weight:400; font-style:italic; color:var(--ink-1); line-height:1.4; max-width:920px; }
.slide-quote .author { font-family:var(--font-label); font-size:15px; font-weight:700; letter-spacing:0.12em; text-transform:uppercase; color:var(--accent); }

/* --- Divider / transition / you-are-here / common-error / mnemonic --- */
.slide-divider { background:var(--surface-1); justify-content:center; align-items:flex-start; padding:80px 96px; gap:var(--s-4); }
.slide-divider .kicker { font-family:var(--font-label); font-size:15px; font-weight:700; letter-spacing:0.16em; text-transform:uppercase; color:var(--accent); }
.slide-divider h2 { font-family:var(--font-display); font-size:54px; font-weight:900; line-height:1.08; color:var(--ink-1); max-width:980px; }

/* --- Closing --- */
.slide-closing { background:var(--bg-0); justify-content:center; align-items:flex-start; padding:80px 96px; gap:var(--s-4); }
.slide-closing blockquote { font-family:var(--font-display); font-size:40px; font-style:italic; color:var(--ink-1); line-height:1.4; max-width:900px; }
.slide-closing .next { border-top:1px solid var(--border); padding-top:28px; margin-top:8px; }
.slide-closing .next .next-label { font-family:var(--font-label); font-size:13px; font-weight:700; letter-spacing:0.16em; text-transform:uppercase; color:var(--ink-3); margin-bottom:8px; }
.slide-closing .next .next-val { font-family:var(--font-label); font-size:20px; font-weight:700; color:var(--ink-1); }

/* ===================== PLAYER ===================== */
#notes-bar { position:fixed; bottom:0; left:0; right:0; background:rgba(0,0,0,0.96); color:var(--ink-2); font-size:16px; font-family:var(--font-ui); line-height:1.5; padding:16px 28px; display:none; z-index:100; border-top:1px solid var(--border-subtle); }
#notes-bar.visible { display:block; }
#notes-bar strong { color:var(--accent); font-weight:600; }
#controls { position:fixed; top:14px; right:20px; display:flex; gap:8px; z-index:100; align-items:center; }
#controls button { background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.1); color:rgba(255,255,255,0.5); font-size:11px; font-family:var(--font-label); font-weight:500; letter-spacing:0.1em; text-transform:uppercase; padding:6px 12px; cursor:pointer; }
#controls button:hover { background:rgba(255,255,255,0.1); color:#fff; }
#counter { color:rgba(255,255,255,0.3); font-size:12px; font-family:var(--font-label); }
#progress { position:fixed; top:0; left:0; height:3px; background:var(--accent); transition:width 0.25s ease-out; z-index:200; }
</style>
</head>
<body>
<div id="stage">
  <!-- SLIDES AQUI. Primeiro slide com classe "active". -->
  <!-- Cada slide termina com: <div class="slide-num">N / T</div><div class="wordmark">{{WORDMARK}}</div> -->
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

## Instruções de uso (estruturais — valem para qualquer brand)

1. **Monte base + skin** conforme "Como a skill monta o HTML".
2. **Substitua `{{TITULO_AULA}}`** pelo título real e **`{{WORDMARK}}`** pela string da marca (vem do brand).
3. **Insira os slides em `<div id="stage">`**, mapeando o **tipo da tipologia** para a **classe CSS** (tabela tipo→classe no brand). Todo slide de conteúdo tem um **`.assert-title` em frase completa** (lei 2).
4. **Primeiro slide com classe `active`.**
5. **Builds:** marque com `class="fragment"` o que deve ser revelado passo a passo (passos de um processo, opções de pergunta, resposta de quiz, linhas de comparação). Use onde a ficha do tipo recomenda.
6. **Preencha o array `notes`** — uma string por slide, na ordem. As notas carregam o que a voz do professor diz (lei 6): o difícil de mostrar.
7. **Cada slide termina com** `<div class="slide-num">N / T</div><div class="wordmark">{{WORDMARK}}</div>`.
8. **Gráficos** (`.slide-chart`): renderize o chart **de verdade** em SVG/HTML dentro de `.chart-area` — nunca uma imagem de gráfico gerada.
9. **Composição:** a escolha de layout, variante (`.hero`, `.center`, `.numbered`, `.tight`, `.lead`, `.dense`, `.grid`, `.critical`, `.verdict`, `.chain`, `.cycle`, `.tree`, `.stack`, `.fill`, `.hairline`, `.edge`) e primitivo (`.accent-bar`, `.index-numeral`, `.emphasis`, `.rule`) segue [composicao-visual.md](../skills/invisible-class-slides/references/composicao-visual.md). Sem emojis, sem ícones decorativos, sem gradiente (exceto o overlay de imagem), sem border-radius acima do `--radius` do brand.
10. **Sem inline, sem classe improvisada.** Se um tratamento não existe no ferramental, ele é **adicionado a esta base** — nunca a um `style=`. Se você se pegar escrevendo `<p style="…">` ou inventando uma classe nova com CSS próprio, pare: o componente certo já está acima, ou deve ser criado aqui. É onde a consistência e o gosto morrem. As setas/glifos de `chain`/`cycle`/`tree` são SVG com `stroke="currentColor"` (a cor vem da classe, não de `style=`).

### Exemplo — Asserção + evidência (workhorse), top-anchored, com build
```html
<div class="slide slide-assert active">
  <div class="top"><div class="label">Pressão atmosférica</div>
    <div class="assert-title">A pressão do ar cai conforme a altitude sobe.</div></div>
  <div class="evidence">
    <p class="lead fragment">Ao nível do mar, a coluna de ar inteira pesa sobre você: <strong>~1 atm</strong>.</p>
    <p class="fragment">A 5.500 m, metade da atmosfera ficou abaixo — a pressão cai pela <strong>metade</strong>.</p>
  </div>
  <div class="slide-num">4 / 18</div><div class="wordmark">{{WORDMARK}}</div>
</div>
```

### Exemplo — Asserção-herói (declaração-soco / slide esparso enche o quadro pelo foco)
```html
<div class="slide slide-assert hero">
  <div class="accent-bar"></div>
  <div class="assert-lead">A Jerusalém desce. Ela não é construída.</div>
  <div class="sub">A salvação não nasce de baixo para cima. É dom, não conquista.</div>
  <div class="slide-num">6 / 35</div><div class="wordmark">{{WORDMARK}}</div>
</div>
```

### Exemplo — Diagrama de 6 passos em grid 3×2 (em vez de 6 caixas espremidas numa linha)
```html
<div class="slide slide-diagram">
  <div class="top"><div class="label">Processo</div>
    <div class="assert-title">O ciclo da água tem seis etapas encadeadas.</div></div>
  <div class="flow grid">
    <div class="fbox"><div class="fn">1</div><div class="ftitle">Evaporação</div><div class="fsub">O sol aquece a superfície.</div></div>
    <div class="fbox"><div class="fn">2</div><div class="ftitle">Condensação</div><div class="fsub">Vapor vira nuvem.</div></div>
    <div class="fbox critical"><div class="fn">3</div><div class="ftitle">Precipitação</div><div class="fsub">A etapa que define o clima.</div></div>
    <div class="fbox"><div class="fn">4</div><div class="ftitle">Infiltração</div><div class="fsub">A água penetra o solo.</div></div>
    <div class="fbox"><div class="fn">5</div><div class="ftitle">Escoamento</div><div class="fsub">Rios levam ao mar.</div></div>
    <div class="fbox"><div class="fn">6</div><div class="ftitle">Retorno</div><div class="fsub">O ciclo recomeça.</div></div>
  </div>
  <div class="slide-num">12 / 18</div><div class="wordmark">{{WORDMARK}}</div>
</div>
```

### Exemplo — Contraste (erro-comum / antes-depois): equívoco vs. correto, assimétrico
```html
<div class="slide slide-contrast">
  <div class="top"><div class="label">Equívoco comum</div>
    <div class="assert-title tight">Fé não é o oposto de razão.</div></div>
  <div class="sides">
    <div class="side wrong">
      <div class="side-label">O que se pensa</div>
      <div class="side-body">Crer é desligar o juízo: aceitar sem evidência, contra a inteligência.</div>
    </div>
    <div class="side right fragment">
      <div class="side-label">O que é</div>
      <div class="side-body">A fé <strong>pressupõe</strong> a razão e a leva além do que ela alcança sozinha — não a contradiz.</div>
    </div>
  </div>
  <div class="slide-num">9 / 22</div><div class="wordmark">{{WORDMARK}}</div>
</div>
```

### Exemplo — Textos paralelos (paralelo-textos): correspondência ligada por um conector
```html
<div class="slide slide-parallel">
  <div class="top"><div class="label">Promessa e cumprimento</div>
    <div class="assert-title tight">O que Isaías anuncia, o Apocalipse consuma.</div></div>
  <div class="pair">
    <p class="ptext"><span class="pref">Isaías 65,17</span>"Eis que vou criar novos céus e nova terra."</p>
    <div class="connector"><span class="c-glyph"></span><span class="connector-label">Cumpre-se em</span><span class="c-rule"></span></div>
    <p class="ptext"><span class="pref">Apocalipse 21,1</span>"Vi então um novo céu e uma nova terra."</p>
  </div>
  <div class="slide-num">14 / 22</div><div class="wordmark">{{WORDMARK}}</div>
</div>
```

### Exemplo — Cadeia causal (causa-efeito): nós sem caixa, ligados por setas SVG
```html
<div class="slide slide-diagram">
  <div class="top"><div class="label">Mecanismo</div>
    <div class="assert-title">O pecado fecha o homem em si e seca a caridade.</div></div>
  <div class="flow chain">
    <div class="cnode"><div class="clabel">Soberba</div><div class="csub">O eu vira o centro.</div></div>
    <div class="carrow">
      <svg viewBox="0 0 48 14" fill="none" stroke="currentColor" stroke-width="2"><line x1="0" y1="7" x2="42" y2="7"/><polyline points="36,2 44,7 36,12"/></svg>
      <span class="carrow-label">fecha em</span>
    </div>
    <div class="cnode turn"><div class="clabel">Isolamento</div><div class="csub">O outro vira ameaça.</div></div>
    <div class="carrow">
      <svg viewBox="0 0 48 14" fill="none" stroke="currentColor" stroke-width="2"><line x1="0" y1="7" x2="42" y2="7"/><polyline points="36,2 44,7 36,12"/></svg>
      <span class="carrow-label">seca</span>
    </div>
    <div class="cnode"><div class="clabel">Caridade</div><div class="csub">Sem o outro, não há amor.</div></div>
  </div>
  <div class="slide-num">11 / 22</div><div class="wordmark">{{WORDMARK}}</div>
</div>
```

### Exemplo — Ciclo (ciclo-loop): 4 nós num anel sobre caminho circular SVG
```html
<div class="slide slide-diagram">
  <div class="top"><div class="label">Vida sacramental</div>
    <div class="assert-title">A graça é um ciclo que se realimenta, não uma linha.</div></div>
  <div class="flow cycle">
    <svg class="cycle-svg" viewBox="0 0 100 100" fill="none" stroke="currentColor" stroke-width="0.8" preserveAspectRatio="none">
      <path d="M50 14 A36 36 0 1 1 49.9 14" stroke-dasharray="2 2"/>
      <polyline points="46,16 50,12 54,16"/>
    </svg>
    <div class="cnode pos-1"><div class="clabel">Graça</div><div class="csub">Deus dá o primeiro passo.</div></div>
    <div class="cnode pos-2"><div class="clabel">Conversão</div><div class="csub">O coração responde.</div></div>
    <div class="cnode pos-4"><div class="clabel">Caridade</div><div class="csub">O amor transborda em obra.</div></div>
    <div class="cnode pos-5"><div class="clabel">Abertura</div><div class="csub">A obra dispõe a mais graça.</div></div>
  </div>
  <div class="slide-num">18 / 22</div><div class="wordmark">{{WORDMARK}}</div>
</div>
```

### Exemplo — Árvore de decisão (taxonomia/árvore): raiz + ramos rotulados
```html
<div class="slide slide-diagram">
  <div class="top"><div class="label">Discernimento</div>
    <div class="assert-title tight">A consolação tem origem — e ela se testa.</div></div>
  <div class="flow tree decision">
    <div class="troot"><div class="clabel">Moção interior</div></div>
    <div class="tconnect"></div>
    <div class="tbranches">
      <div class="tbranch">
        <div class="branch-label">Leva a Deus</div>
        <div class="tnode"><div class="clabel">Consolação</div><div class="csub">Cresce em fé, paz, humildade.</div></div>
      </div>
      <div class="tbranch">
        <div class="branch-label">Afasta de Deus</div>
        <div class="tnode"><div class="clabel">Engano</div><div class="csub">Termina em inquietação e orgulho.</div></div>
      </div>
    </div>
  </div>
  <div class="slide-num">20 / 22</div><div class="wordmark">{{WORDMARK}}</div>
</div>
```

### Exemplo — Rail (split assimétrico) com numeral de seção como âncora
```html
<div class="slide slide-rail">
  <div class="rail-aside">
    <div class="label-muted">Parte II</div>
    <div class="index-numeral">02</div>
    <div class="assert-title tight">A nova criação</div>
  </div>
  <div class="rail-main">
    <div class="emphasis">O fim não é fuga do mundo, mas sua <span class="accent">transfiguração</span>.</div>
  </div>
  <div class="slide-num">13 / 22</div><div class="wordmark">{{WORDMARK}}</div>
</div>
```

### Exemplo — Asserção-herói liderada por tipografia (`.emphasis`), sem caixa
```html
<div class="slide slide-assert hero">
  <div class="accent-bar"></div>
  <div class="emphasis">Deus não conserta o velho. Ele faz <span class="accent">novas todas as coisas</span>.</div>
  <div class="sub">A redenção é criação, não reparo.</div>
  <div class="slide-num">21 / 22</div><div class="wordmark">{{WORDMARK}}</div>
</div>
```

### Exemplo — Caixas com tratamento variado (`.fill` / `.hairline` / `.edge`) em vez de borda-padrão
```html
<div class="slide slide-diagram">
  <div class="top"><div class="label">Três sentidos</div>
    <div class="assert-title">A Escritura se lê em mais de um nível.</div></div>
  <div class="flow grid cols-2">
    <div class="fbox fill"><div class="ftitle">Literal</div><div class="fsub">O que o texto diz de fato.</div></div>
    <div class="fbox hairline"><div class="ftitle">Alegórico</div><div class="fsub">O que aponta em Cristo.</div></div>
    <div class="fbox hairline"><div class="ftitle">Moral</div><div class="fsub">O que pede da conduta.</div></div>
    <div class="fbox edge"><div class="ftitle">Anagógico</div><div class="fsub">O que antecipa do fim.</div></div>
  </div>
  <div class="slide-num">7 / 22</div><div class="wordmark">{{WORDMARK}}</div>
</div>
```
