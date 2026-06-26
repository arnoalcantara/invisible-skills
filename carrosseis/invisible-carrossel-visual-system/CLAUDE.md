# invisible-carrossel-visual — plugin

## O que é

O **sistema visual de carrossel** da Invisible. É o lado VISUAL da produção de carrossel: recebe o roteiro pronto (texto card a card) e o **veste** numa linguagem visual decodificada de referências, gerando os cards finais como PNGs.

Complementa o lado COPY (`invisible-carrossel`, no plugin `invisible-copy`): aquele escreve o texto fiel à fonte; este o renderiza. Fronteira limpa — quem escreve não renderiza; quem renderiza não inventa texto.

## Skills

| Skill | Função |
|---|---|
| `invisible-carrossel-visual` | Produtor visual: roteiro pronto + pasta de referências → cards PNG. Decodifica refs por visão (congela em `_ESTILO.md`), veste o texto por papel de slide, gera via GPT Image 2 (Higgsfield CLI). |

## Princípios de arquitetura

- **Identidade visual = referências.** Não há cadastro de estética por marca. O visual sai 100% das imagens da pasta, decodificadas por visão e congeladas num `_ESTILO.md` por pasta (briefing reutilizável).
- **Papel do slide.** Capa, interno e fecho têm repertórios próprios no `_ESTILO.md`. Interno nunca é tratado como capa.
- **Texto dentro da imagem.** GPT Image 2 desenha fundo + texto integrados. Verificação pós-render (visão) garante texto correto.
- **Coleta robusta.** O `--wait` do Higgsfield dá 502 na coleta e cobra mesmo falhando. Os scripts disparam o job e recuperam por id; nunca re-disparam um job que pode estar rodando.
- **Motor central.** Higgsfield CLI instalado na máquina (npm), não por lote. `bootstrap.py` confirma login e reporta créditos.

## Estilos recorrentes

Cada estilo de carrossel vive como uma **pasta de referências** com um `_ESTILO.md` congelado. O usuário aponta a pasta; a skill lê o briefing pronto. Trocar de estilo = trocar de pasta.

## Roadmap

- **v0.1.0:** produtor visual com motor Higgsfield (texto-na-imagem).
- **Fase 2 — Canva como motor 2:** para estilos UI-mockup/tipográficos (ex.: app de Notas), um template com molduras vazias + injeção de texto via Canva MCP sai mais barato e o texto nunca erra. O Higgsfield fica para estilos com imagem gerada.
- **Modo notícia:** vocação herdada do sistema de referência (Human Academy) — pesquisa pauta por nicho, gera texto (ou delega à `invisible-carrossel`) e veste no visual.

## Convenções

- Fluxo de código: worktree + branch, nunca direto na `main`.
- Documentação em português; código e variáveis em inglês.
- Convenção Invisible: skills com prefixo `invisible-`.
