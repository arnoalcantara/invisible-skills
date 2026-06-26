# invisible-carrossel-visual

Sistema visual de carrossel da Invisible. Transforma um **roteiro pronto** (texto card a card) numa peça visual: os cards renderizados como PNGs, vestidos numa linguagem visual decodificada de **referências**.

É o lado VISUAL do carrossel. O lado COPY é a skill `invisible-carrossel` (plugin `invisible-copy`), que escreve o texto fiel à fonte. Aqui, esse texto é renderizado.

## Skills

### `invisible-estilo-decoder`

Aponte uma **pasta de referências visuais** (imagens de inspiração de um estilo) e a skill as lê por **visão** (decompondo grids) e congela o sistema visual num arquivo **`[NomeDaPasta]_ESTILO.md`** salvo na própria pasta. Esse briefing é o contrato que o produtor visual lê em vez de re-analisar as imagens a cada carrossel — mais barato, mais rápido e idêntico toda vez. Não gera imagem; só o contrato.

```
> decodifica o estilo dessas referências: <pasta>
```

O `[Pasta]_ESTILO.md` é editável à mão: é a fonte da verdade do estilo.

### `invisible-carrossel-visual`

Recebe dois insumos:
1. **Roteiro pronto** — um `.md` com o texto card a card (saída da `invisible-carrossel`).
2. **Pasta de referências visuais** — imagens de inspiração de um estilo de carrossel.

E entrega os **cards renderizados** (PNG, 3:4), com o texto dentro da imagem, na estética das referências.

**Como funciona:**
- Decodifica as referências por **visão** (fonte, paleta, registro tonal, moldura, detail signature; decompõe grids) e congela o resultado num `_ESTILO.md` na própria pasta. Da próxima vez, lê o briefing congelado em vez de re-analisar.
- Veste o texto na linguagem decodificada, respeitando o **papel** de cada slide (capa / interno / fecho).
- Gera via **GPT Image 2 (Higgsfield CLI)**, com o texto renderizado dentro da imagem.
- Prova UM card (a capa) antes do lote; verifica cada slide por visão pós-render.

**Coleta robusta:** dispara o job e recupera por id; nunca confia no `--wait` do Higgsfield (que dá 502 na coleta e cobra mesmo falhando).

## Requisitos

- **Higgsfield CLI** instalado e logado:
  ```bash
  npm install -g @higgsfield/cli
  higgsfield auth login
  higgsfield account status
  ```
- Uma **pasta de referências visuais** (com ou sem `_ESTILO.md`).

A skill faz bootstrap (`scripts/bootstrap.py`) e reporta os créditos antes de gerar.

## Uso

```
> renderiza esse carrossel: <roteiro.md>, usando as referências em <pasta>
```

A skill decodifica/lê o estilo, mostra o plano, gera a capa para aprovação, e então o lote.

## Roadmap

- **v0.1.0:** motor Higgsfield (texto-na-imagem).
- **Fase 2:** Canva como motor 2 para estilos UI-mockup/tipográficos (mais barato, texto nunca erra).
- **Modo notícia:** pesquisa pauta por nicho e gera o carrossel ponta a ponta.
