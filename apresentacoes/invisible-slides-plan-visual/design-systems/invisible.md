<!-- base: invisible-doc-to-presentation/design-systems/invisible.md (jun/2026) — inteligência visual oficial adotada integralmente (paleta, tipografia, escala, classes s-*, player). Estendido com: player com fragments (builds) + 5 layouts didáticos (s-timeline, s-chart, s-image, s-prompt, s-divider) na MESMA escala e linguagem. NÃO alterar a lógica visual oficial; só acrescentar. Sincronizar manualmente em mudança de marca. -->

# Design System: Invisible (Brand System) — Renderizador de slides

Sistema visual das apresentações da Invisible, derivado do **Brand System Invisible**. Editorial, sofisticado, flat. Funis perpétuos, B2B. Craft invisível: produção refinada, sem ostentação.

> Este é o design system da `invisible-doc-to-presentation` (a inteligência visual aprovada), adotado **integralmente** e estendido para a aula: suporte a **builds** (revelação progressiva via `fragment`) e 5 tipos de slide didáticos extras (`s-timeline`, `s-chart`, `s-image`, `s-prompt`, `s-divider`), desenhados na mesma escala e linguagem `s-`. O sistema é **misto**: cada tipo de slide decide se o fundo é escuro (capa, citação, número, fechamento) ou claro (título, conteúdo, diagrama, tabela). Fundo claro recebe a classe `light` (ajusta numeração/logo).

---

## Princípios da marca

- **Sem gradientes em fundos.** A planura é um atributo de marca. (Exceção: overlay de imagem.)
- **Cantos retos** (border-radius 0). No máximo 2–4px em micro-elementos.
- **Sem sombras decorativas.** Profundidade vem de sobreposição de camadas.
- **Whitespace generoso** — sensibilidade de jornal editorial.
- **Coral é acento singular**, nunca decorativo: numeração, barras, destaques pontuais.
- **Emoji: nunca.** A marca comunica por tipografia, imagem e logo.
- **Tom:** confiante e assertivo — afirmações, não promessas. Headlines em sentence case com ponto final.
- **Revelação progressiva nativa.** O player suporta `fragment` para builds passo a passo (uso na aula).

---

## Paleta de Cores

| Variável | Hex | Uso |
|---|---|---|
| `--black` | `#000000` | Fundo de capa, citação, prompt e fechamento; títulos fortes |
| `--near-black` | `#111111` | Superfícies escuras, títulos em fundo claro |
| `--coral` | `#E85043` | Acento editorial — numeração, barras, destaques, CTAs, "certo" |
| `--white` | `#FFFFFF` | Fundo claro principal, texto invertido |
| `--off-white` | `#F5F4F0` | Fundo "papel" — slides de seção/diagrama, linhas de tabela |
| `--light-gray` | `#E8E5DE` | Divisores e bordas sutis |
| `--silver` | `#C0C0C0` | Texto mudo em fundo escuro |
| `--text-sec` | `#666666` | Texto secundário em fundo claro |
| `--text` | `#1A1A1A` | Corpo de texto em fundo claro |

**Regra de cor:** distinções de conteúdo (certo/errado, A/B) nunca dependem só de cor — use também posição, rótulo ou forma (acessibilidade).

---

## Tipografia (sistema dual + wordmark)

Importar do Google Fonts. Substitutos das fontes licenciadas da marca.

| Papel | Fonte | Token | Uso |
|---|---|---|---|
| Display serif | `Playfair Display` | `--display` | Títulos, números-destaque, citações, capa, divisor, prompt |
| UI sans | `Space Grotesk` | `--ui` | Labels, wordmark, kickers, dados, títulos de conteúdo (h2) |
| Body sans | `DM Sans` | `--body` | Corpo de texto, bullets, legendas |

- **Capa / display:** Playfair 900, 60–66px, letter-spacing −0.02em.
- **Títulos de slide (h2):** Playfair 700, 40–54px (capa/tese/tabela). Asserção de conteúdo: Space Grotesk 700, 28–42px.
- **Número-destaque:** Playfair 900, 96–104px, cor coral.
- **Citação:** Playfair italic 400, 36–40px.
- **Divisor:** Playfair 900, 40px. **Prompt (pergunta):** Playfair 700, 32px.
- **Labels/kickers:** Space Grotesk 600, 13px, uppercase, letter-spacing 0.18em, cor coral.
- **Corpo:** DM Sans 400, 19–21px, line-height 1.55–1.7.

> **Nunca inflar.** Inflar a tipografia foi o erro da versão antiga. O que dá sofisticação é o espaço, não o tamanho.

---

## Layout de Slides

Proporção **16:9** (1280 × 720px). O JS aplica `transform: scale()` para caber na tela.

### Tipos de slide disponíveis

| Tipo | Classe | Característica | Fundo |
|---|---|---|---|
| Capa | `s-capa` | Label coral, título display serif, assinatura | escuro |
| Título de seção / tese | `s-titulo` | Barra coral à esquerda, frase declarativa única | claro |
| Conteúdo | `s-conteudo` | Label coral, h2, bullets com traço coral; **workhorse** | claro |
| Número-destaque | `s-num` | Bloco preto à esquerda com número coral gigante; texto à direita | misto |
| Retrato | `s-retrato` | Texto sobre faixa escura, foto editorial dessaturada | escuro |
| Citação | `s-citacao` | Aspa coral, citação italic, autor em coral | escuro |
| Diagrama | `s-diagrama` | Fluxo (`flow`) ou funil (`funnel`) com setas coral | claro |
| Tabela | `s-tabela` | Header preto, linha de destaque em off-white/coral | claro |
| Dois colunas | `s-duo` | Coluna preta (conceito) + coluna branca (detalhe) | misto |
| Fechamento | `s-fechamento` | Frase grande, assinatura, barra coral | escuro |
| **Linha do tempo / espectro** | `s-timeline` | Eixo horizontal, marcos com ponto coral | claro |
| **Gráfico / infográfico** | `s-chart` | Chart **real** em SVG/código (nunca imagem) | claro |
| **Imagem** | `s-image` | Tela cheia (com `overlay`) ou `split` (imagem + texto) | escuro |
| **Pergunta / processamento ativo** | `s-prompt` | Pergunta em destaque, opções tipicamente `fragment` | escuro |
| **Divisor / ponte / erro comum / você-está-aqui** | `s-divider` | Kicker coral, frase de seção display | claro |

Cada slide leva, ao final, `<div class="slide-num">N / T</div>` e `<div class="logo-invisible">Invisible</div>`. Slides de fundo **claro** recebem também a classe `light` (ajusta a cor de numeração/logo).

---

## Revelação progressiva (builds)

Qualquer elemento com a classe `fragment` começa invisível e é revelado um a um pelas setas, **antes** de avançar para o próximo slide. Slides **sem** `fragment` se comportam como um player simples (uma seta = um slide) — um storyboard sem builds (ex.: da `invisible-doc-to-presentation`) renderiza sem regressão.

```html
<li class="fragment">Revelado no segundo avanço</li>
<div class="fragment">Revelado no terceiro avanço</div>
```

---

## Template HTML Base

Use como estrutura raiz. Substitua `{{TITULO_APRESENTACAO}}`, insira os slides em `#presentation` e preencha o array `notes` (uma string por slide, mesma ordem). Primeiro slide com classe `active`. O player já tem navegação por teclado, **builds por fragment**, notas (N), fullscreen (F), contador, barra de progresso e escala responsiva.

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
  .fragment{opacity:0;transition:opacity .18s ease-out;}
  .fragment.shown{opacity:1;}

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
  /* corpo em prosa (evidência da asserção) */
  .s-conteudo .body{max-width:920px;}
  .s-conteudo .body p{font-size:20px;line-height:1.7;color:var(--text);margin-bottom:16px;}
  .s-conteudo .body p:last-child{margin-bottom:0;}
  .s-conteudo .body b{font-weight:600;color:var(--near-black);}

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

  /* ════ EXTENSÕES DIDÁTICAS (mesma escala e linguagem s-) ════ */

  /* TIMELINE / espectro */
  .s-timeline{background:var(--off-white);justify-content:center;padding:0 90px;}
  .s-timeline .label{margin-bottom:54px;}
  .s-timeline .axis{display:flex;align-items:center;}
  .s-timeline .track{width:100%;height:2px;background:var(--light-gray);position:relative;display:flex;justify-content:space-between;}
  .s-timeline .mark{position:relative;top:-6px;display:flex;flex-direction:column;align-items:center;gap:14px;}
  .s-timeline .dot{width:12px;height:12px;border-radius:50%;background:var(--coral);}
  .s-timeline .mark .date{font-family:var(--ui);font-size:15px;font-weight:600;letter-spacing:.04em;color:var(--near-black);}
  .s-timeline .mark .ev{font-family:var(--body);font-size:14px;color:var(--text-sec);max-width:170px;text-align:center;line-height:1.5;}

  /* CHART (chart real em SVG/código dentro de .chart-area) */
  .s-chart{background:var(--white);justify-content:center;padding:0 90px;}
  .s-chart h2{font-family:var(--display);font-weight:700;font-size:38px;letter-spacing:-.02em;color:var(--near-black);margin-bottom:30px;}
  .s-chart .chart-area{flex:1;display:flex;align-items:center;justify-content:center;max-height:480px;}
  .s-chart .chart-area text{font-family:var(--body);}
  .s-chart .src{margin-top:20px;font-family:var(--ui);font-size:13px;color:var(--text-sec);}

  /* IMAGEM */
  .s-image{padding:0;background:var(--black);}
  .s-image img,.s-image .imgfill{width:100%;height:100%;object-fit:cover;}
  .s-image .overlay{position:absolute;left:0;bottom:0;right:0;padding:56px 80px;background:linear-gradient(to top,rgba(0,0,0,.9),transparent);}
  .s-image .overlay .label{margin-bottom:14px;}
  .s-image .overlay h2{font-family:var(--display);font-weight:700;font-size:40px;line-height:1.15;color:var(--white);}
  .s-image .overlay .cap{font-family:var(--body);font-size:16px;color:var(--silver);margin-top:10px;line-height:1.5;}
  .s-image.split{flex-direction:row;}
  .s-image.split .imghalf{width:50%;height:100%;background-size:cover;background-position:center;}
  .s-image.split .txthalf{width:50%;padding:0 64px;display:flex;flex-direction:column;justify-content:center;gap:18px;background:var(--white);}
  .s-image.split .txthalf .label{color:var(--coral);}
  .s-image.split .txthalf h2{font-family:var(--display);font-weight:700;font-size:34px;line-height:1.2;color:var(--near-black);}
  .s-image.split .txthalf p{font-family:var(--body);font-size:18px;line-height:1.65;color:var(--text);}

  /* PROMPT (processamento ativo) */
  .s-prompt{background:var(--black);justify-content:center;padding:0 110px;}
  .s-prompt .label{margin-bottom:32px;}
  .s-prompt .q{font-family:var(--display);font-weight:700;font-size:42px;line-height:1.25;letter-spacing:-.01em;color:var(--white);max-width:940px;}
  .s-prompt .options{margin-top:44px;display:flex;flex-direction:column;gap:14px;}
  .s-prompt .opt{font-family:var(--body);font-size:20px;color:var(--silver);padding-left:26px;position:relative;}
  .s-prompt .opt::before{content:'';position:absolute;left:0;top:13px;width:14px;height:3px;background:var(--coral);}
  .s-prompt .opt b{color:var(--white);font-weight:600;}

  /* DIVISOR / ponte / erro comum / você-está-aqui */
  .s-divider{background:var(--off-white);justify-content:center;padding:0 110px;}
  .s-divider .kicker{font-family:var(--ui);font-size:13px;font-weight:600;letter-spacing:.18em;text-transform:uppercase;color:var(--coral);margin-bottom:26px;}
  .s-divider h2{font-family:var(--display);font-weight:900;font-size:52px;line-height:1.1;letter-spacing:-.02em;color:var(--near-black);max-width:920px;}
  .s-divider .sub{font-family:var(--body);font-size:19px;color:var(--text-sec);margin-top:24px;max-width:780px;line-height:1.6;}

  /* UI chrome */
  #notes-bar{position:fixed;bottom:0;left:0;right:0;background:rgba(0,0,0,.92);color:#bbb;font-family:var(--body);font-size:14px;line-height:1.5;padding:14px 28px;display:none;z-index:100;border-top:1px solid #2a2a2a;}
  #notes-bar.visible{display:block;}
  #notes-bar strong{color:var(--coral);font-family:var(--ui);letter-spacing:.06em;text-transform:uppercase;font-size:12px;}
  #controls{position:fixed;top:14px;right:18px;display:flex;gap:8px;z-index:100;align-items:center;}
  #controls button{background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.18);color:#fff;font-family:var(--ui);font-size:12px;padding:7px 13px;cursor:pointer;}
  #controls button:hover{background:rgba(255,255,255,.18);}
  #controls #slide-counter{color:rgba(255,255,255,.5);font-family:var(--ui);font-size:12px;padding:7px 4px;}
  #progress{position:fixed;bottom:0;left:0;height:3px;background:var(--coral);transition:width .25s ease;z-index:99;}
</style>
</head>
<body>
<div id="presentation">
  <!-- Insira os slides aqui. Primeiro slide com classe "active". -->
  <!-- Cada slide termina com: <div class="slide-num">N / T</div><div class="logo-invisible">Invisible</div> -->
  <!-- Builds: qualquer elemento com class="fragment" é revelado um a um pelas setas. -->
</div>

<div id="notes-bar"><strong>Notas</strong>&nbsp;&nbsp;<span id="notes-text"></span></div>
<div id="controls">
  <button onclick="toggleNotes()">Notas [N]</button>
  <button onclick="toggleFullscreen()">Tela cheia [F]</button>
  <span id="slide-counter"></span>
</div>
<div id="progress"></div>

<script>
  // notes = uma string por slide, na mesma ordem dos slides
  const notes=[/* PREENCHER */];

  let current=0, frag=0;
  const slides=Array.from(document.querySelectorAll('.slide'));
  const total=slides.length;
  const fragsOf=s=>Array.from(s.querySelectorAll('.fragment'));

  function render(){
    slides.forEach((s,i)=>s.classList.toggle('active',i===current));
    const f=fragsOf(slides[current]);
    f.forEach((el,i)=>el.classList.toggle('shown',i<frag));
    document.getElementById('notes-text').textContent=notes[current]||'—';
    document.getElementById('slide-counter').textContent=`${current+1} / ${total}`;
    document.getElementById('progress').style.width=`${((current+1)/total)*100}%`;
  }
  function next(){
    const f=fragsOf(slides[current]);
    if(frag<f.length){frag++;render();return;}
    if(current<total-1){current++;frag=0;render();}
  }
  function prev(){
    if(frag>0){frag--;render();return;}
    if(current>0){current--;frag=fragsOf(slides[current]).length;render();}
  }
  function goTo(n){current=Math.max(0,Math.min(n,total-1));frag=0;render();}

  document.addEventListener('keydown',e=>{
    if(['ArrowRight','ArrowDown',' '].includes(e.key)){e.preventDefault();next();}
    if(['ArrowLeft','ArrowUp'].includes(e.key)){e.preventDefault();prev();}
    if(e.key==='n'||e.key==='N')toggleNotes();
    if(e.key==='f'||e.key==='F')toggleFullscreen();
    if(e.key==='Home')goTo(0);
    if(e.key==='End')goTo(total-1);
  });
  function scaleSlides(){
    const s=Math.min(window.innerWidth/1280,window.innerHeight/720);
    slides.forEach(sl=>sl.style.transform=`scale(${s})`);
  }
  window.addEventListener('resize',scaleSlides);
  function toggleNotes(){document.getElementById('notes-bar').classList.toggle('visible');}
  function toggleFullscreen(){if(!document.fullscreenElement){document.documentElement.requestFullscreen();}else{document.exitFullscreen();}}
  scaleSlides();render();
</script>
</body>
</html>
```

---

## Exemplos de cada tipo de slide

```html
<!-- CAPA (primeiro slide: classe active) -->
<div class="slide s-capa active">
  <div class="label">Aula 03 · Termodinâmica</div>
  <h1>Por que a água ferve mais rápido na montanha.<br><em>Uma questão de pressão.</em></h1>
  <div class="sign">Curso de Física <span>·</span> Invisible</div>
  <div class="slide-num">01 / 18</div><div class="logo-invisible">Invisible</div>
</div>

<!-- TÍTULO / TESE (fundo claro → classe light) -->
<div class="slide s-titulo light">
  <div class="coral-bar"></div>
  <h2>A pressão do ar cai conforme a altitude <b>sobe.</b></h2>
  <div class="slide-num">02 / 18</div><div class="logo-invisible">Invisible</div>
</div>

<!-- CONTEÚDO (workhorse): lista com build -->
<div class="slide s-conteudo light">
  <div class="label">Pressão atmosférica</div>
  <h2>O ar tem peso — e o peso diminui com a altura.</h2>
  <ul>
    <li class="fragment">Ao nível do mar, a coluna inteira de ar pesa sobre você: <b>~1 atm</b>.</li>
    <li class="fragment">A 5.500 m, metade da atmosfera ficou abaixo — a pressão cai pela <b>metade</b>.</li>
    <li class="fragment">Menos pressão sobre o líquido = ebulição em <b>temperatura menor</b>.</li>
  </ul>
  <div class="slide-num">04 / 18</div><div class="logo-invisible">Invisible</div>
</div>

<!-- CONTEÚDO em prosa (evidência da asserção) -->
<div class="slide s-conteudo light">
  <div class="label">Definição</div>
  <h2>O que é pressão atmosférica.</h2>
  <div class="body">
    <p class="fragment">É a <b>força por área</b> exercida pelo peso do ar sobre tudo na superfície.</p>
    <p class="fragment">Medimos em atmosferas (atm) ou em milímetros de mercúrio (mmHg).</p>
  </div>
  <div class="slide-num">05 / 18</div><div class="logo-invisible">Invisible</div>
</div>

<!-- NÚMERO-DESTAQUE -->
<div class="slide s-num light">
  <div class="left"><div class="big">−50%</div><div class="ulabel">Queda da pressão a 5.500 m de altitude</div></div>
  <div class="right">
    <p>A cada ~5,5 km de altitude, a pressão atmosférica cai <span class="hl">pela metade</span>.</p>
    <div class="sub">Fonte: citar sempre a origem do dado.</div>
  </div>
  <div class="slide-num">06 / 18</div><div class="logo-invisible">Invisible</div>
</div>

<!-- DOIS COLUNAS (comparação) -->
<div class="slide s-duo">
  <div class="col-l"><div class="big">vs</div><p>Nível do mar contra alta montanha.</p></div>
  <div class="col-r">
    <div class="blk"><div class="h">Nível do mar</div><ul><li>1 atm</li><li>Água ferve a 100 °C</li></ul></div>
    <div class="blk"><div class="h">5.500 m</div><ul><li>0,5 atm</li><li>Água ferve a ~83 °C</li></ul></div>
  </div>
  <div class="slide-num">07 / 18</div><div class="logo-invisible">Invisible</div>
</div>

<!-- DIAGRAMA: fluxo -->
<div class="slide s-diagrama light">
  <div class="label">Cadeia causal</div>
  <div class="flow">
    <div class="step"><div class="k">Sobe</div><div class="v">Altitude</div><div class="d">Você ganha altura.</div></div>
    <div class="arrow">→</div>
    <div class="step"><div class="k">Cai</div><div class="v">Pressão</div><div class="d">Menos ar acima.</div></div>
    <div class="arrow">→</div>
    <div class="step dark"><div class="k">Cai</div><div class="v">Ponto de ebulição</div><div class="d">Ferve antes dos 100 °C.</div></div>
  </div>
  <div class="slide-num">08 / 18</div><div class="logo-invisible">Invisible</div>
</div>

<!-- PERGUNTA / PROCESSAMENTO ATIVO (opções como fragment) -->
<div class="slide s-prompt">
  <div class="label">Preveja</div>
  <div class="q">O que acontece com a chama de uma vela num elevador em queda livre?</div>
  <div class="options">
    <div class="opt fragment">Sobe mais alta</div>
    <div class="opt fragment">Apaga</div>
    <div class="opt fragment">Vira uma <b>esfera</b></div>
  </div>
  <div class="slide-num">09 / 18</div><div class="logo-invisible">Invisible</div>
</div>

<!-- DIVISOR / ponte de seção -->
<div class="slide s-divider light">
  <div class="kicker">Parte 2</div>
  <h2>O que a pressão faz com a temperatura de ebulição.</h2>
  <div class="sub">Entendida a pressão, vamos ligar os dois fenômenos.</div>
  <div class="slide-num">10 / 18</div><div class="logo-invisible">Invisible</div>
</div>

<!-- TIMELINE / espectro -->
<div class="slide s-timeline light">
  <div class="label">Evolução do conceito</div>
  <div class="axis">
    <div class="track">
      <div class="mark"><div class="dot"></div><div class="date">1643</div><div class="ev">Torricelli inventa o barômetro.</div></div>
      <div class="mark"><div class="dot"></div><div class="date">1648</div><div class="ev">Pascal mede a pressão numa montanha.</div></div>
      <div class="mark"><div class="dot"></div><div class="date">Hoje</div><div class="ev">Base da meteorologia moderna.</div></div>
    </div>
  </div>
  <div class="slide-num">11 / 18</div><div class="logo-invisible">Invisible</div>
</div>

<!-- GRÁFICO (chart REAL em SVG; nunca imagem) -->
<div class="slide s-chart light">
  <h2>Ponto de ebulição × altitude.</h2>
  <div class="chart-area">
    <!-- SVG com os dados literais do plano; barras/linha desenhadas em código -->
    <svg viewBox="0 0 900 420" width="900" height="420" role="img" aria-label="Ponto de ebulição cai com a altitude">
      <!-- eixos, pontos e linha aqui, com os números do Conteúdo -->
    </svg>
  </div>
  <div class="src">Fonte: citar a origem do dado.</div>
  <div class="slide-num">12 / 18</div><div class="logo-invisible">Invisible</div>
</div>

<!-- IMAGEM tela cheia (com overlay) -->
<div class="slide s-image">
  <div class="imgfill" style="background-image:url('{{URL}}');background-size:cover;background-position:center;"></div>
  <div class="overlay">
    <div class="label">No campo</div>
    <h2>Cozinhar a 4.000 m leva mais tempo.</h2>
    <div class="cap">A água ferve mais frio — e cozinha mais devagar.</div>
  </div>
  <div class="slide-num">13 / 18</div><div class="logo-invisible">Invisible</div>
</div>

<!-- IMAGEM split (imagem + texto) -->
<div class="slide s-image split">
  <div class="imghalf" style="background-image:url('{{URL}}');"></div>
  <div class="txthalf">
    <div class="label">Exemplo anotado</div>
    <h2>O barômetro de Torricelli.</h2>
    <p>O peso do ar empurra o mercúrio coluna acima até equilibrar.</p>
  </div>
  <div class="slide-num">14 / 18</div><div class="logo-invisible">Invisible</div>
</div>

<!-- CITAÇÃO -->
<div class="slide s-citacao">
  <div class="mark">&ldquo;</div>
  <blockquote>Vivemos no fundo de um oceano de ar.</blockquote>
  <div class="author">Evangelista Torricelli</div>
  <div class="slide-num">15 / 18</div><div class="logo-invisible">Invisible</div>
</div>

<!-- TABELA (linha de destaque: classe hl) -->
<div class="slide s-tabela light">
  <h2>Pressão e ebulição por altitude.</h2>
  <table>
    <thead><tr><th>Local</th><th>Altitude</th><th>Ferve a</th></tr></thead>
    <tbody>
      <tr><td>Praia</td><td>0 m</td><td>100 °C</td></tr>
      <tr class="hl"><td>La Paz</td><td>3.640 m</td><td>~88 °C</td></tr>
    </tbody>
  </table>
  <div class="slide-num">16 / 18</div><div class="logo-invisible">Invisible</div>
</div>

<!-- FECHAMENTO -->
<div class="slide s-fechamento">
  <h2>Menos ar acima, menos calor para ferver.</h2>
  <div class="sign">Próxima aula <span>·</span> Calorimetria</div>
  <div class="coral-bar"></div>
  <div class="slide-num">18 / 18</div><div class="logo-invisible">Invisible</div>
</div>
```

---

## Checklist ao gerar o HTML

1. Copie o template base e substitua `{{TITULO_APRESENTACAO}}`.
2. Insira um `<div class="slide s-...">` por slide do plano, mapeando o **tipo** para a **classe** ([tipo-layout-map.md](../skills/invisible-slides-plan-visual/references/tipo-layout-map.md)); o primeiro recebe `active`.
3. Slides de fundo **claro** recebem também a classe `light`.
4. **Builds:** marque com `class="fragment"` os elementos que o campo `Build:` do plano manda revelar passo a passo. As setas revelam um a um antes de trocar de slide.
5. Preencha o array `notes` — uma string por slide, na mesma ordem (campo `Notas do professor:`).
6. Todo slide tem `slide-num` (`N / T`) e `logo-invisible` (`Invisible`).
7. **Gráficos** (`s-chart`): renderize o chart **de verdade** em SVG/HTML dentro de `.chart-area` — nunca uma imagem de gráfico. Dados literais do `Conteúdo:`.
8. Dados pesquisados aparecem com a fonte (em `.sub`, `.src` ou rodapé).
9. Em retrato/imagem, troque `{{URL_DA_FOTO}}`/`{{URL}}`; ofereça embutir em base64 para uso offline.
10. **Escala refinada sempre** — não infle as fontes além desta folha. Sem gradientes de fundo (exceto overlay de imagem), sem cantos arredondados, sem sombras decorativas, sem emoji.
