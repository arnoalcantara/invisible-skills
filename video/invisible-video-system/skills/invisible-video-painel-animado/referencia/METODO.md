# MÉTODO — invisible-video-painel-animado

Referência técnica de manutenção. O fluxo operacional está na `SKILL.md`.

## Arquitetura — três metades

1. **Geração do personagem (Artlist, sessão-dependente):** GPT Image 2 gera SÓ o
   personagem ilustrado. Depende do MCP Artlist. Não roda sem o conector.
2. **Composição (Remotion, portável):** o projeto central em
   `~/.invisible-video/painel-animado-remotion` desenha e anima o painel inteiro
   (card, diagrama, texto). Determinístico, roda em qualquer lugar com Node.
3. **Inserção (`inserir.py`, ffmpeg puro):** o MESMO motor da broll-insert. Cutaway:
   recorta só a faixa de vídeo do alvo na janela, reconcilia a grade, remuxa o áudio
   original inteiro. O áudio nunca é tocado.

O recorte (`recortar.py`, rembg) é a ponte entre 1 e 2: transforma o PNG opaco do
GPT Image em PNG com alpha real.

## Por que Remotion e não i2v (o aprendizado central)

Painel didático tem TEXTO legível como ponto central. i2v generativo (Seedance) **reescreve
o texto** ao animar ("ROTA DO SOM" virou "ROTA DOI J" no teste). Além disso, i2v só "treme"
a imagem pronta; não **compõe o quadro** (elementos entrando, montando). Remotion resolve
os dois: texto é `<div>` de verdade (nunca erra) e a animação é declarativa (cada elemento
tem seu timing de entrada). Custo: ~600 créditos (1 imagem) vs ~1350 do caminho i2v.

## O GPT Image não entrega alpha no download (armadilha)

O preview do Artlist mostra xadrez de transparência, mas o PNG **baixado** vem **RGB
opaco** (fundo branco chapado). Validar SEMPRE em disco (`Image.mode`, alpha extrema) —
nunca confiar no preview. Solução: `recortar.py` roda rembg (u2net, offline) sobre o
fundo branco — recorte limpo em ilustração flat. O script sai !=0 se o alpha não ficar
transparente (fundo não removido).

## Templates paramétricos (layout fixo, conteúdo variável)

O projeto Remotion registra 3 composições; cada uma lê `public/props.json` via
`calculateMetadata` (a skill escreve o JSON; a duração vem de `duracaoSeg`). O layout é
fixo; a skill só preenche o conteúdo. Isso torna a skill previsível (sem gerar código
de layout por painel) e reproduzível.

- **FluxoDeNos** — N nós (2–4) encadeados por setas + selos + fecho + personagem.
  Posições e timing calculados a partir de `nos.length`. Foi o template validado.
- **ErroCerto** — card dividido, esquerda (riscada) × direita.
- **ConceitoNomeado** — ícone-conceito grande + explicação em cartão.

Peças compartilhadas em `src/comum.tsx` (paleta, `useEnter` spring, Titulo, No, Seta,
Selo, Icone, Personagem). Ícones nomeados viram SVG no componente `Icone`.

Texto multi-linha usa `\n` no JSON + `whiteSpace: "pre-line"` no componente (sem isso o
`\n` não quebra e o texto vaza a margem — bug pego no teste).

## Ritmo da animação (aprendizado do teste)

Espaçar as entradas pelos 5s inteiros; amontoar no 1º segundo atropela. No FluxoDeNos:
nós entram de 21 em 21 frames a partir do 36; setas se "desenham" via `clip-path`
(18 frames); selos em cascata; personagem sobe por último (frame 120). Spring suave:
`damping 22 / stiffness 70 / mass 1`.

## Inserção — como preserva o áudio

Idêntico à broll-insert: recorta a faixa de VÍDEO do alvo nos pedaços entre coberturas,
reconcilia cada painel para a grade do alvo (crop/fps/codec/pix_fmt), concatena só vídeo
com caminhos ABSOLUTOS, remuxa o áudio original inteiro
(`-map 0:v:0 -map 1:a:0 -c:v copy -c:a copy -shortest`). A skill de painel passa `--out`
com `_ANIMATION`; o `inserir.py` é o mesmo binário reusado.

## IDs de modelo Artlist (verificados 30/07/2026)

| Uso | Modelo | modelId |
|---|---|---|
| Personagem | GPT Image 2 - T2I - High | 2341 |

> Se `generate_image` reclamar do modelId, re-listar com `list_models` (kind image) e
> achar o "GPT Image 2 - T2I - High" pelo displayName. GPT Image (não Nano Banana) porque
> lida melhor com o pedido de fundo isolado — mas o alpha real vem SEMPRE do rembg.

## Teste de aceitação (30/07/2026, Lote 09 / VAV133)

Painel "ROTA DO SOM" (FluxoDeNos), personagem mãe+filho, inserido em 95.4s (fala "rota
do som"), cobertura 5s. Validado frame a frame: fala intacta antes/depois, painel nítido,
composição animando por cima, áudio idêntico. ✅ Aprovado pelo Arno.

## Escopo (o que esta skill NÃO faz)

- Overlay / picture-in-picture (é cutaway).
- Texto gerado por IA (é Remotion).
- Animação por i2v generativo.
- Layout Remotion novo por painel (usa os templates).
- Mexer na esteira de lote (skill avulsa).
- Tocar no áudio.
