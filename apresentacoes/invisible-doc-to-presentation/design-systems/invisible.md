# Design System: Invisible (Brand System)

Sistema visual das apresentações da Invisible, derivado do **Brand System Invisible**. Editorial, sofisticado, flat. Funis perpétuos, B2B. Craft invisível: produção refinada, sem ostentação.

---

## Princípios da marca

- **Sem gradientes em fundos.** A planura é um atributo de marca.
- **Cantos retos** (border-radius 0). No máximo 2–4px em micro-elementos.
- **Sem sombras decorativas.** Profundidade vem de sobreposição de camadas.
- **Whitespace generoso** — sensibilidade de jornal editorial.
- **Coral é acento singular**, nunca decorativo: numeração, barras, destaques pontuais.
- **Emoji: nunca.** A marca comunica por tipografia, imagem e logo.
- **Tom:** confiante e assertivo — afirmações, não promessas. Headlines em sentence case com ponto final.

---

## Paleta de Cores

| Variável | Hex | Uso |
|---|---|---|
| `--black` | `#000000` | Fundo de capa, citação e fechamento; títulos fortes |
| `--near-black` | `#111111` | Superfícies escuras, títulos em fundo claro |
| `--coral` | `#E85043` | Acento editorial — numeração, barras, destaques, CTAs |
| `--white` | `#FFFFFF` | Fundo claro principal, texto invertido |
| `--off-white` | `#F5F4F0` | Fundo "papel" — slides de seção/diagrama, linhas de tabela |
| `--light-gray` | `#E8E5DE` | Divisores e bordas sutis |
| `--silver` | `#C0C0C0` | Texto mudo em fundo escuro |
| `--text-sec` | `#666666` | Texto secundário em fundo claro |
| `--text` | `#1A1A1A` | Corpo de texto em fundo claro |

---

## Tipografia (sistema dual + wordmark)

Importar do Google Fonts. Substitutos das fontes licenciadas da marca.

| Papel | Fonte | Token | Uso |
|---|---|---|---|
| Display serif | `Playfair Display` | `--display` | Títulos, números-destaque, citações, capa |
| UI sans | `Space Grotesk` | `--ui` | Labels, wordmark, kickers, dados |
| Body sans | `DM Sans` | `--body` | Corpo de texto, bullets, legendas |

- **Capa / display:** Playfair 900, 60–66px, letter-spacing −0.02em.
- **Títulos de slide (h2):** Playfair 700, 40–54px.
- **Número-destaque:** Playfair 900, 96–104px, cor coral.
- **Citação:** Playfair italic 400, 36–40px.
- **Labels/kickers:** Space Grotesk 600, 13px, uppercase, letter-spacing 0.18em, cor coral.
- **Corpo:** DM Sans 400, 19–21px, line-height 1.55–1.7.

---

## Layout de Slides

Proporção **16:9** (1280 × 720px). O JS aplica `transform: scale()` para caber na tela.

### Tipos de slide disponíveis

| Tipo | Classe | Característica |
|---|---|---|
| Capa | `s-capa` | Fundo preto, label coral, título display serif, assinatura |
| Título de seção / tese | `s-titulo` | Off-white, barra coral à esquerda, frase declarativa única |
| Conteúdo | `s-conteudo` | Branco, label coral, h2 serif, bullets com traço coral |
| Número-destaque | `s-num` | Bloco preto à esquerda com número coral gigante; texto à direita |
| Retrato | `s-retrato` | Texto à esquerda sobre faixa escura, foto editorial dessaturada à direita |
| Citação | `s-citacao` | Fundo preto, aspa coral, citação italic, autor em coral |
| Diagrama | `s-diagrama` | Off-white, fluxo (`flow`) ou funil (`funnel`) com setas coral |
| Tabela | `s-tabela` | Header preto, linha de destaque em off-white/coral |
| Dois colunas | `s-duo` | Coluna preta (número/conceito) + coluna branca (detalhe) |
| Fechamento | `s-fechamento` | Fundo preto, frase grande, assinatura, barra coral |

Cada slide leva, ao final, `<div class="slide-num">N / T</div>` e `<div class="logo-invisible">Invisible</div>`. Slides de fundo **claro** recebem também a classe `light` (ajusta a cor de numeração/logo).

---

## Template HTML Base

Use como estrutura raiz. Substitua `{{TITULO_APRESENTACAO}}`, insira os slides em `#presentation` e preencha o array `notes` (uma string por slide, mesma ordem). Primeiro slide com classe `active`.

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{TITULO_APRESENTACAO}}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400&family=Space+Grotesk:wght@400;500;600;700&family=DM+Sans:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  *,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
  :root{
    --black:#000000; --near-black:#111111; --coral:#E85043;
    --white:#FFFFFF; --off-white:#F5F4F0; --light-gray:#E8E5DE;
    --mid-gray:#999999; --silver:#C0C0C0; --text:#1A1A1A; --text-sec:#666666;
    --display:'Playfair Display',serif; --ui:'Space Grotesk',sans-serif; --body:'DM Sans',sans-serif;
    --w:1280px; --h:720px;
  }
  body{background:#0a0a0a;font-family:var(--body);display:flex;flex-direction:column;align-items:center;min-height:100vh;overflow:hidden;}
  #presentation{position:relative;width:100vw;height:100vh;display:flex;align-items:center;justify-content:center;}
  .slide{display:none;width:var(--w);height:var(--h);position:relative;overflow:hidden;transform-origin:center center;flex-direction:column;}
  .slide.active{display:flex;}

  .label{font-family:var(--ui);font-size:13px;font-weight:600;letter-spacing:.18em;text-transform:uppercase;color:var(--coral);}
  .coral-bar{width:54px;height:4px;background:var(--coral);}

  .logo-invisible{position:absolute;bottom:30px;right:44px;font-family:var(--ui);font-size:12px;font-weight:700;letter-spacing:.22em;text-transform:uppercase;color:rgba(255,255,255,.28);}
  .slide-num{position:absolute;bottom:30px;left:44px;font-family:var(--ui);font-size:11px;font-weight:500;letter-spacing:.12em;color:rgba(255,255,255,.28);}
  .light .logo-invisible,.light .slide-num{color:rgba(0,0,0,.28);}

  /* CAPA */
  .s-capa{background:var(--black);justify-content:center;padding:0 110px;}
  .s-capa .label{margin-bottom:46px;}
  .s-capa h1{font-family:var(--display);font-weight:900;font-size:62px;line-height:1.12;letter-spacing:-.02em;color:var(--white);max-width:920px;}
  .s-capa h1 em{font-style:italic;color:var(--silver);font-weight:400;}
  .s-capa .sign{margin-top:54px;font-family:var(--ui);font-size:16px;font-weight:600;letter-spacing:.04em;color:var(--white);}
  .s-capa .sign span{color:var(--coral);}

  /* TITULO / tese */
  .s-titulo{background:var(--off-white);justify-content:center;padding:0 110px;}
  .s-titulo .coral-bar{margin-bottom:40px;}
  .s-titulo h2{font-family:var(--display);font-weight:700;font-size:54px;line-height:1.18;letter-spacing:-.02em;color:var(--near-black);max-width:900px;}
  .s-titulo h2 b{color:var(--coral);font-weight:700;}

  /* NUMERO DESTAQUE */
  .s-num{background:var(--white);flex-direction:row;align-items:stretch;}
  .s-num .left{width:46%;background:var(--black);display:flex;flex-direction:column;justify-content:center;padding:0 56px;}
  .s-num .big{font-family:var(--display);font-weight:900;font-size:104px;line-height:.94;letter-spacing:-.03em;color:var(--coral);white-space:nowrap;}
  .s-num .ulabel{font-family:var(--ui);font-size:14px;font-weight:600;letter-spacing:.16em;text-transform:uppercase;color:var(--silver);margin-top:26px;max-width:340px;line-height:1.5;}
  .s-num .right{width:54%;display:flex;flex-direction:column;justify-content:center;padding:0 80px;}
  .s-num .right p{font-size:21px;line-height:1.7;color:var(--text);}
  .s-num .right p .hl{color:var(--coral);font-weight:600;}
  .s-num .sub{margin-top:24px;font-family:var(--ui);font-size:15px;color:var(--text-sec);}

  /* CONTEUDO */
  .s-conteudo{background:var(--white);justify-content:center;padding:0 110px;}
  .s-conteudo .label{margin-bottom:18px;}
  .s-conteudo h2{font-family:var(--display);font-weight:700;font-size:42px;line-height:1.15;letter-spacing:-.02em;color:var(--near-black);margin-bottom:38px;max-width:920px;}
  .s-conteudo ul{list-style:none;max-width:960px;}
  .s-conteudo li{position:relative;padding:13px 0 13px 34px;font-size:20px;line-height:1.55;color:var(--text);border-top:1px solid var(--light-gray);}
  .s-conteudo li:first-child{border-top:none;}
  .s-conteudo li::before{content:'';position:absolute;left:0;top:23px;width:16px;height:3px;background:var(--coral);}
  .s-conteudo li b{font-weight:600;}

  /* RETRATO */
  .s-retrato{background:var(--black);flex-direction:row;align-items:stretch;}
  .s-retrato .txt{width:50%;display:flex;flex-direction:column;justify-content:center;padding:0 70px;z-index:2;}
  .s-retrato .label{margin-bottom:30px;line-height:1.6;max-width:340px;}
  .s-retrato .txt p{font-family:var(--display);font-weight:400;font-size:30px;line-height:1.4;color:var(--white);}
  .s-retrato .txt p b{color:var(--coral);font-weight:700;font-style:normal;}
  .s-retrato .photo{width:50%;background-image:url('{{URL_DA_FOTO}}');background-size:cover;background-position:center 20%;filter:grayscale(.5) contrast(1.04);position:relative;}
  .s-retrato .photo::after{content:'';position:absolute;inset:0;background:linear-gradient(90deg,rgba(0,0,0,.92) 0%,rgba(0,0,0,.35) 30%,rgba(0,0,0,0) 60%);}

  /* CITACAO */
  .s-citacao{background:var(--black);justify-content:center;align-items:center;text-align:center;padding:0 130px;}
  .s-citacao .mark{font-family:var(--display);font-size:90px;line-height:0;color:var(--coral);margin-bottom:50px;height:30px;}
  .s-citacao blockquote{font-family:var(--display);font-style:italic;font-weight:400;font-size:38px;line-height:1.45;color:var(--white);max-width:920px;}
  .s-citacao .author{margin-top:44px;font-family:var(--ui);font-size:14px;font-weight:600;letter-spacing:.16em;text-transform:uppercase;color:var(--coral);}

  /* DIAGRAMA */
  .s-diagrama{background:var(--off-white);justify-content:center;padding:0 90px;}
  .s-diagrama .label{margin-bottom:46px;}
  .flow{display:flex;align-items:stretch;gap:0;width:100%;}
  .flow .step{flex:1;background:var(--white);border:1px solid var(--light-gray);padding:38px 30px;display:flex;flex-direction:column;justify-content:center;min-height:230px;}
  .flow .step.dark{background:var(--black);border-color:var(--black);}
  .flow .step .k{font-family:var(--ui);font-size:13px;font-weight:600;letter-spacing:.12em;text-transform:uppercase;color:var(--coral);margin-bottom:16px;}
  .flow .step .v{font-family:var(--display);font-weight:700;font-size:30px;line-height:1.15;color:var(--near-black);}
  .flow .step.dark .v{color:var(--white);}
  .flow .step .d{margin-top:14px;font-size:16px;line-height:1.5;color:var(--text-sec);}
  .flow .step.dark .d{color:var(--silver);}
  .flow .arrow{display:flex;align-items:center;justify-content:center;padding:0 20px;font-size:34px;color:var(--coral);font-family:var(--ui);font-weight:700;}
  .funnel{display:flex;flex-direction:column;align-items:center;gap:16px;width:100%;}
  .funnel .tier{display:flex;align-items:center;justify-content:space-between;background:var(--white);border:1px solid var(--light-gray);padding:24px 40px;}
  .funnel .tier.t1{width:92%;} .funnel .tier.t2{width:74%;} .funnel .tier.t3{width:56%;background:var(--black);border-color:var(--black);}
  .funnel .tier .name{font-family:var(--ui);font-size:18px;font-weight:600;color:var(--near-black);}
  .funnel .tier.t3 .name{color:var(--white);}
  .funnel .tier .price{font-family:var(--display);font-weight:700;font-size:26px;color:var(--coral);}
  .funnel .down{color:var(--coral);font-size:22px;font-family:var(--ui);font-weight:700;}

  /* TABELA */
  .s-tabela{background:var(--white);justify-content:center;padding:0 100px;}
  .s-tabela h2{font-family:var(--display);font-weight:700;font-size:40px;letter-spacing:-.02em;color:var(--near-black);margin-bottom:34px;}
  .s-tabela table{width:100%;border-collapse:collapse;}
  .s-tabela th{background:var(--black);color:var(--white);font-family:var(--ui);font-size:13px;font-weight:600;text-transform:uppercase;letter-spacing:.1em;padding:18px 26px;text-align:left;}
  .s-tabela td{padding:20px 26px;font-size:19px;color:var(--text);border-bottom:1px solid var(--light-gray);}
  .s-tabela tr.hl td{background:var(--off-white);font-weight:600;color:var(--near-black);}
  .s-tabela tr.hl td:last-child{color:var(--coral);}
  .s-tabela td:last-child{font-family:var(--ui);font-weight:600;white-space:nowrap;}

  /* DOIS COLUNAS */
  .s-duo{flex-direction:row;align-items:stretch;background:var(--white);}
  .s-duo .col-l{width:42%;background:var(--black);display:flex;flex-direction:column;justify-content:center;padding:0 60px;}
  .s-duo .col-l .big{font-family:var(--display);font-weight:900;font-size:84px;line-height:.95;letter-spacing:-.02em;color:var(--coral);}
  .s-duo .col-l p{margin-top:24px;font-size:18px;line-height:1.55;color:var(--silver);}
  .s-duo .col-r{width:58%;display:flex;flex-direction:column;justify-content:center;padding:0 64px;}
  .s-duo .blk{margin-bottom:30px;}
  .s-duo .blk:last-child{margin-bottom:0;}
  .s-duo .blk .h{font-family:var(--ui);font-size:13px;font-weight:600;letter-spacing:.12em;text-transform:uppercase;color:var(--coral);margin-bottom:14px;}
  .s-duo .blk ul{list-style:none;}
  .s-duo .blk li{position:relative;padding:6px 0 6px 26px;font-size:18px;line-height:1.4;color:var(--text);}
  .s-duo .blk li::before{content:'';position:absolute;left:0;top:15px;width:12px;height:3px;background:var(--coral);}

  /* FECHAMENTO */
  .s-fechamento{background:var(--black);justify-content:center;align-items:center;text-align:center;padding:0 100px;}
  .s-fechamento h2{font-family:var(--display);font-weight:900;font-size:66px;line-height:1.12;letter-spacing:-.02em;color:var(--white);max-width:880px;}
  .s-fechamento .sign{margin-top:40px;font-family:var(--ui);font-size:17px;font-weight:600;letter-spacing:.05em;color:var(--silver);}
  .s-fechamento .sign span{color:var(--coral);}
  .s-fechamento .coral-bar{margin:44px auto 0;}

  /* UI chrome */
  #notes-bar{position:fixed;bottom:0;left:0;right:0;background:rgba(0,0,0,.92);color:#bbb;font-family:var(--body);font-size:14px;line-height:1.5;padding:14px 28px;display:none;z-index:100;border-top:1px solid #2a2a2a;}
  #notes-bar.visible{display:block;}
  #notes-bar strong{color:var(--coral);font-family:var(--ui);letter-spacing:.06em;text-transform:uppercase;font-size:12px;}
  #controls{position:fixed;top:14px;right:18px;display:flex;gap:8px;z-index:100;}
  #controls button{background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.18);color:#fff;font-family:var(--ui);font-size:12px;padding:7px 13px;cursor:pointer;}
  #controls button:hover{background:rgba(255,255,255,.18);}
  #controls #slide-counter{color:rgba(255,255,255,.5);font-family:var(--ui);font-size:12px;padding:7px 4px;}
  #progress{position:fixed;bottom:0;left:0;height:3px;background:var(--coral);transition:width .25s ease;z-index:99;}
</style>
</head>
<body>
<div id="presentation">
  <!-- Insira os slides aqui. Veja exemplos de cada tipo abaixo. -->
</div>

<div id="notes-bar"><strong>Notas</strong>&nbsp;&nbsp;<span id="notes-text"></span></div>
<div id="controls">
  <button onclick="toggleNotes()">Notas [N]</button>
  <button onclick="toggleFullscreen()">Tela cheia [F]</button>
  <span id="slide-counter"></span>
</div>
<div id="progress"></div>

<script>
  let current=0;
  const slides=document.querySelectorAll('.slide');
  const total=slides.length;
  const notes=[/* uma string por slide, na mesma ordem */];
  function goTo(n){
    slides[current].classList.remove('active');
    current=Math.max(0,Math.min(n,total-1));
    slides[current].classList.add('active');
    document.getElementById('notes-text').textContent=notes[current]||'—';
    document.getElementById('slide-counter').textContent=`${current+1} / ${total}`;
    document.getElementById('progress').style.width=`${((current+1)/total)*100}%`;
  }
  document.addEventListener('keydown',e=>{
    if(e.key==='ArrowRight'||e.key==='ArrowDown'||e.key===' ')goTo(current+1);
    if(e.key==='ArrowLeft'||e.key==='ArrowUp')goTo(current-1);
    if(e.key==='n'||e.key==='N')toggleNotes();
    if(e.key==='f'||e.key==='F')toggleFullscreen();
  });
  function scaleSlides(){
    const s=Math.min(window.innerWidth/1280,window.innerHeight/720);
    slides.forEach(sl=>sl.style.transform=`scale(${s})`);
  }
  window.addEventListener('resize',scaleSlides);
  function toggleNotes(){document.getElementById('notes-bar').classList.toggle('visible');}
  function toggleFullscreen(){if(!document.fullscreenElement){document.documentElement.requestFullscreen();}else{document.exitFullscreen();}}
  scaleSlides();goTo(0);
</script>
</body>
</html>
```

---

## Exemplos de cada tipo de slide

```html
<!-- CAPA (primeiro slide: classe active) -->
<div class="slide s-capa active">
  <div class="label">Proposta de Parceria</div>
  <h1>Uma frase de abertura forte.<br><em>Com uma segunda linha em itálico.</em></h1>
  <div class="sign">Cliente <span>×</span> Invisible · 2026</div>
  <div class="slide-num">01 / 12</div><div class="logo-invisible">Invisible</div>
</div>

<!-- TÍTULO / TESE (fundo claro → classe light) -->
<div class="slide s-titulo light">
  <div class="coral-bar"></div>
  <h2>Uma afirmação declarativa — <b>com o destaque em coral.</b></h2>
  <div class="slide-num">02 / 12</div><div class="logo-invisible">Invisible</div>
</div>

<!-- NÚMERO-DESTAQUE -->
<div class="slide s-num light">
  <div class="left"><div class="big">635 mil</div><div class="ulabel">Rótulo do número</div></div>
  <div class="right">
    <p>Frase de contexto com um <span class="hl">trecho em destaque</span>.</p>
    <div class="sub">Fonte: citar sempre a origem do dado.</div>
  </div>
  <div class="slide-num">03 / 12</div><div class="logo-invisible">Invisible</div>
</div>

<!-- CONTEÚDO -->
<div class="slide s-conteudo light">
  <div class="label">Kicker da seção</div>
  <h2>Título do slide.</h2>
  <ul>
    <li>Primeiro ponto com <b>palavra-chave</b>.</li>
    <li>Segundo ponto que expande ou contrasta.</li>
    <li>Terceiro ponto conclusivo.</li>
  </ul>
  <div class="slide-num">04 / 12</div><div class="logo-invisible">Invisible</div>
</div>

<!-- RETRATO (trocar {{URL_DA_FOTO}} no CSS .s-retrato .photo) -->
<div class="slide s-retrato">
  <div class="txt">
    <div class="label">Kicker sobre a pessoa</div>
    <p>Frase editorial com <b>destaque coral</b> sobre o protagonista.</p>
  </div>
  <div class="photo"></div>
  <div class="slide-num">05 / 12</div><div class="logo-invisible">Invisible</div>
</div>

<!-- CITAÇÃO -->
<div class="slide s-citacao">
  <div class="mark">&ldquo;</div>
  <blockquote>A citação que ancora a marca ou a tese.</blockquote>
  <div class="author">Nome do Autor</div>
  <div class="slide-num">06 / 12</div><div class="logo-invisible">Invisible</div>
</div>

<!-- DIAGRAMA: fluxo -->
<div class="slide s-diagrama light">
  <div class="label">Título do fluxo</div>
  <div class="flow">
    <div class="step"><div class="k">Etapa 1</div><div class="v">Marco inicial</div><div class="d">Detalhe curto.</div></div>
    <div class="arrow">→</div>
    <div class="step"><div class="k">Etapa 2</div><div class="v">Transição</div><div class="d">Detalhe curto.</div></div>
    <div class="arrow">→</div>
    <div class="step dark"><div class="k">Etapa 3</div><div class="v">Resultado</div><div class="d">Detalhe curto.</div></div>
  </div>
  <div class="slide-num">07 / 12</div><div class="logo-invisible">Invisible</div>
</div>

<!-- DIAGRAMA: funil -->
<div class="slide s-diagrama light">
  <div class="label">Título do funil</div>
  <div class="funnel">
    <div class="tier t1"><span class="name">Front-end</span><span class="price">R$ 500</span></div>
    <div class="down">↓</div>
    <div class="tier t2"><span class="name">Intermediário</span><span class="price">R$ 1.500–2.000</span></div>
    <div class="down">↓</div>
    <div class="tier t3"><span class="name">High ticket</span><span class="price">R$ 30 mil</span></div>
  </div>
  <div class="slide-num">08 / 12</div><div class="logo-invisible">Invisible</div>
</div>

<!-- TABELA (linha de destaque: classe hl) -->
<div class="slide s-tabela light">
  <h2>Título da tabela.</h2>
  <table>
    <thead><tr><th>Coluna A</th><th>Coluna B</th><th>Valor</th></tr></thead>
    <tbody>
      <tr><td>Linha 1</td><td>Descrição</td><td>R$ 10 mil</td></tr>
      <tr class="hl"><td>Linha destacada</td><td>Descrição</td><td>R$ 30–35 mil</td></tr>
    </tbody>
  </table>
  <div class="slide-num">09 / 12</div><div class="logo-invisible">Invisible</div>
</div>

<!-- DOIS COLUNAS -->
<div class="slide s-duo">
  <div class="col-l"><div class="big">50/50</div><p>Conceito-âncora explicado em uma frase.</p></div>
  <div class="col-r">
    <div class="blk"><div class="h">Bloco 1</div><ul><li>Item</li><li>Item</li></ul></div>
    <div class="blk"><div class="h">Bloco 2</div><ul><li>Item</li><li>Item</li></ul></div>
  </div>
  <div class="slide-num">10 / 12</div><div class="logo-invisible">Invisible</div>
</div>

<!-- FECHAMENTO -->
<div class="slide s-fechamento">
  <h2>Frase de fechamento / CTA.</h2>
  <div class="sign">Cliente <span>×</span> Invisible</div>
  <div class="coral-bar"></div>
  <div class="slide-num">12 / 12</div><div class="logo-invisible">Invisible</div>
</div>
```

---

## Checklist ao gerar o HTML

1. Copie o template base e substitua `{{TITULO_APRESENTACAO}}`.
2. Insira um `<div class="slide s-...">` por slide aprovado no storyboard; o primeiro recebe `active`.
3. Slides de fundo claro recebem também a classe `light`.
4. Preencha o array `notes` — uma string por slide, na mesma ordem.
5. Todo slide tem `slide-num` (`N / T`) e `logo-invisible` (`Invisible`).
6. Dados pesquisados aparecem com a fonte (em `.sub` no número-destaque, ou rodapé).
7. Em retrato, troque `{{URL_DA_FOTO}}`; ofereça embutir em base64 para uso offline.
8. Sem gradientes de fundo, sem cantos arredondados, sem sombras decorativas, sem emoji.
