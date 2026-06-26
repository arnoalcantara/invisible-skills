# Método — Produtor Visual de Carrossel

Referência técnica do método de render. Lido pelo agente quando precisa de detalhe; a orquestração está na `SKILL.md`.

---

## 1. Por que texto DENTRO da imagem (e não fundo + texto por cima)

O GPT Image 2 renderiza tipografia legível dentro da imagem. Para estilos onde o card é **tipografia sobre fundo** (ex.: mockup de app de Notas), o modelo desenha fundo e texto integrados, vestidos na referência. Validado em prova real: textos longos em português, zero erro de ortografia.

A verificação pós-render (abrir o PNG com visão e conferir o texto) é o que torna isso seguro: se o texto sai errado, é falha de render → re-gera.

> Alternativa para estilos puramente tipográficos/UI-mockup: **Canva** (template com molduras vazias + injeção de texto via MCP) sai mais barato e o texto nunca erra, porque é texto de verdade. Fica como motor 2 (não implementado nesta v1). O Higgsfield brilha quando o estilo precisa de **imagem gerada** (foto, cena, arte).

## 2. O `_ESTILO.md` — briefing visual congelado por pasta

Cada pasta de referências de um estilo recorrente ganha um `_ESTILO.md` ao lado das imagens. É o briefing decodificado **uma vez** por visão, congelado como contrato. A skill lê esse arquivo em vez de re-analisar as imagens a cada carrossel: mais rápido, mais barato, e **idêntico toda vez** (consistência do feed).

Seções que um `_ESTILO.md` bem-feito tem:
- **Conceito** (o que o estilo imita / é).
- **Moldura / elementos fixos** (detail signature em todos os slides).
- **Modos de fundo** (dark/light + cores exatas).
- **Tipografia travada** (fonte, pesos, caixa — copiada verbatim no prompt).
- **Accent** (como o destaque é feito, com precisão — ex.: bloco de seleção vs. pincel).
- **Papel do slide** (repertório de capa / interno / fecho — a parte que evita interno-com-cara-de-capa).
- **Anti-estética** (o que nunca fazer).
- **Bloco de injeção** pronto para colar no prompt.

O `_ESTILO.md` é editável à mão: é a fonte da verdade do estilo. Para ajustar, edite o arquivo ou troque as refs e re-decodifique.

## 3. Coleta robusta — o problema do 502

O `higgsfield generate create ... --wait` dá **HTTP 502 com frequência na coleta** do resultado, e o job **cobra mesmo quando o --wait falha**. Por isso o `gerar_slide.py`:

1. Dispara o job **sem** `--wait` → captura o `job_id` na hora.
2. Polla `higgsfield generate get <job_id> --json` até `completed` (resiliente a 502 transitório: erro na coleta não significa erro na geração).
3. Baixa a `result_url` ao completar.

Se tudo falhar, o job pode ter rodado mesmo assim. Recupere com:
```bash
higgsfield generate list --image --size 12 --json   # ache o job_id pela timestamp/url
python3 scripts/gerar_slide.py --job-id <id> --out card.png --prompt-file x.txt
```
**Nunca re-dispare um job que pode estar rodando** — re-disparar = pagar de novo.

## 4. Formato e proporção

A Higgsfield CLI (`gpt_image_2`) aceita `--aspect_ratio` em `1:1,4:3,3:4,16:9,9:16,3:2,2:3`. **Não aceita 4:5.** Usa-se **3:4** (que é também a proporção da grade de perfil do Instagram — a capa sobrevive bem ao corte da grade). A saída vem em alta resolução (ex.: 1744×2336); entrega-se o PNG como veio, sem forçar resize.

Validação: ratio ≈ 0.75. Outra proporção = falha de render (re-gera, nunca força resize, que distorce).

## 5. Referências no prompt

- **Capa:** 1–2 imagens da pasta como `--image` (ancora fonte e estética).
- **Internos:** **a capa já gerada + uma ref** como `--image`. A capa dá a direção final; a ref dá repertório. Isso mantém os slides coerentes sem depender do slide anterior.

## 6. Créditos

Cada slide consome créditos do Higgsfield. Um carrossel de ~9 slides + re-renders soma. O `bootstrap.py` reporta os créditos restantes; a skill avisa o usuário antes de gerar em lote. Iterar pouco antes do render real; provar UM card (a capa) antes do lote.
