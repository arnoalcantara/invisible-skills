# Índice de Perfis de Produto

> **Propósito.** Catálogo dos perfis de produto que vivem nesta pasta (`base/produtos/`).
> Leia este índice **antes** de abrir os arquivos: ele diz quais produtos têm perfil salvo e quando
> usar cada um, para a IA oferecer sem precisar abrir tudo. Depois de escolher, abra o perfil e use-o
> como Briefing + Arquivo de Voz daquele produto.

Um **perfil de produto** é um pacote completo de conhecimento de um produto recorrente: oferta,
mecanismo, promessa, avatar, dores, desejos, reencadre, voz da marca e padrões de criativo já
validados. **Um perfil substitui o par Briefing + Arquivo de Voz** — quando o usuário escolhe um
perfil, o copywriter não pede briefing, lê o perfil como fonte de estratégia E de voz.

É diferente das outras camadas da base:
- **Modelos (`base/copy/modelos/`)** são movimentos de persuasão de um *produtor*, agnósticos de produto, reproduzidos com fidelidade máxima e **sem** filtro de verdade/dignidade.
- **Um perfil de produto** é o *produto inteiro* — conhecimento real, com o filtro de verdade/dignidade **ativo**. Não é um movimento de copy, é o briefing-de-produto pronto.

---

## Como a IA deve usar os perfis

1. **O perfil é o Briefing e o Arquivo de Voz.** Não recalcule estratégia, não peça briefing quando um perfil foi escolhido. Avatar, dores, mecanismo, promessa, objeções e voz saem do perfil.
2. **Filtro de verdade/dignidade ativo.** Diferente dos modelos, o perfil passa pelo corte normal do sistema.
3. **Craft por cima.** Os módulos de `base/copy/` e `base/formatos/` continuam montando a peça; o perfil diz o quê, o craft diz como.
4. **Escolha pelo produto.** Selecione o perfil cujo produto casa com o pedido. Se nenhum casa, siga o fluxo normal (Briefing + Voz).

---

## Catálogo

### `desafio-memorize-escrita.md` — Desafio Memorize com a Escrita (DME)

| Quando usar |
|---|
| Qualquer pedido de copy para o **Desafio Memorize com a Escrita** — anúncio/Reels, banco de ganchos, variação de criativo, e-mail, carrossel. Desafio de 3 dias, técnicas de escrita para memorização, público adulto que estuda por conta própria e "esquece o que estuda". Traz avatar, voz, mecanismo, 11 tipos de gancho validados, estrutura de roteiro e CTAs testados. Foco em anúncio de vídeo, mas serve qualquer formato. |

---

## Manutenção do índice (rotina determinada)

Quando o Arno disser **"criei um perfil de produto novo"** (ou pedir para indexar):

1. **Localize o arquivo novo:** `ls base/produtos/` e identifique o `.md` que ainda não está no Catálogo.
2. **Leia o arquivo** e extraia: o **nome do produto** e a linha de **quando usar** (a partir do Propósito e da Seção 0 do perfil).
3. **Acrescente uma seção no Catálogo** seguindo o formato das existentes. Não reescreva as entradas já existentes — só adicione a nova.
4. **Confira a convenção de nome:** kebab-case, sem espaço, descritivo do produto (`desafio-memorize-escrita.md`).
5. **Suba a versão** em `.claude-plugin/plugin.json` (bump **minor** — perfil novo é recurso compatível) e **commite** (`feat(base): adiciona perfil de produto [nome]`).

---

## Cruzamento com os outros módulos

- `base/copy/macroestrutura.md`, `base/copy/angulos.md`, `base/copy/estruturas-de-copy.md`, `base/copy/figuras-de-retorica.md`, `base/copy/portugues-natural.md` — o craft que monta a peça por cima do perfil.
- `base/formatos/[formato].md` — regras do canal pedido; o perfil adapta sua voz a elas.
- `base/copy/modelos/indice-modelos.md` — camada distinta (movimento de produtor, não produto). Um perfil pode usar um modelo da biblioteca se o usuário pedir, mas são coisas diferentes.
