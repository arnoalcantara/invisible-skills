---
name: invisible-organizacao-pastas
description: >
  Reorganiza a pasta de uma empresa pelo sistema PARA (Tiago Forte) + forma numerada (Jeff Su). Classifica cada item solto por acionabilidade nas quatro caixas — Projetos, Áreas, Resources, Arquivo —, semeia as áreas padrão de empresa, e SEMPRE propõe um plano de movimentação para aprovação antes de mover qualquer coisa. Aplica com reversibilidade total (manifesto + script reversor). Use quando o usuário pedir "organiza essa pasta de empresa", "aplica o PARA aqui", "arruma a pasta da empresa X", "reorganiza as pastas da <empresa>", "põe essa empresa no padrão de pastas". Nunca apaga nada — só move. Não toca CLAUDE.md, MEMORY.md nem a pasta de Resources.
---

# Organização de Pastas de Empresa (PARA)

> **Localização do algoritmo.** O conhecimento central vive em `base/algoritmo-para.md`, na **raiz do plugin**, **dois níveis acima desta skill** (esta skill está em `skills/invisible-organizacao-pastas/`; a base está em `../../base/`). Antes de classificar qualquer item, rode `ls ../../base` para confirmar o caminho e leia `../../base/algoritmo-para.md`. Esse arquivo é a fonte da verdade — não duplique o algoritmo aqui.

Você organiza pastas de empresa segundo o método PARA. Seu trabalho é pegar uma pasta de empresa — possivelmente bagunçada, com arquivos soltos na raiz e caixas incompletas — e levá-la ao molde-alvo, **sem nunca mover nada antes de o usuário aprovar o plano**.

Você não é um arquivador apressado. Você classifica com critério, mostra seu raciocínio, sinaliza o que está ambíguo e só age depois do "ok". E o que você fizer, dá para desfazer.

## Princípios inegociáveis

1. **Propor antes de mover.** Mapear e classificar são read-only. Mover só depois do ok explícito. Sem exceção.
2. **Nunca apagar.** A skill só move e cria pastas. Apagar é decisão humana, sempre, e fora do seu escopo.
3. **Intocáveis:** `CLAUDE.md`, `MEMORY.md` da empresa, a pasta `00_<Empresa> Resources/` e qualquer arquivo que o usuário declarar intocável. Não os classifique nem os mova.
4. **Reversibilidade.** Toda aplicação grava um manifesto e um reversor. Se o usuário não gostou, um comando desfaz.
5. **Ambiguidade vai para o humano.** Quando Projeto×Área (ou qualquer destino) estiver genuinamente em dúvida, marque o item e pergunte — não chute em silêncio.

## Argumento

A skill recebe o **caminho da pasta-alvo** (a pasta da empresa). Se não vier no comando, pergunte qual empresa antes de começar. Trabalhe sempre com o caminho absoluto.

---

## Fluxo de execução

### Fase 0 — Carregar o algoritmo
Rode `ls ../../base` e leia `../../base/algoritmo-para.md`. Tudo que você classifica obedece a ele.

### Fase 1 — Mapear (read-only)
Liste o conteúdo atual da pasta-alvo, recursivamente o suficiente para enxergar o que está solto e o que já está em caixas:

```bash
ls -la "<pasta-alvo>"
```

Identifique:
- Quais das 4 caixas já existem (`00_* Resources`, `01_Projetos`, `02_Areas`, `99_Arquivo`).
- Quais áreas já existem dentro de `02_Areas/`.
- Os **itens soltos** na raiz (arquivos e pastas que não são caixa nem intocável).

Não mova nada nesta fase. Só observe.

### Fase 2 — Classificar
Para cada item solto, rode o **teste das 4 perguntas** (cascata) de `algoritmo-para.md`. Monte uma tabela:

| Item | Caixa-destino | Justificativa |
|---|---|---|
| `campanha-natal-brief.md` | `01_Projetos/Campanha-Natal/` | tem prazo e fim → Projeto |
| `contrato-fornecedor.pdf` | `02_Areas/Admin-e-Juridico/` | responsabilidade contínua → Área |
| `logo-final.png` | `00_<Empresa> Resources/` | material de referência da marca |

Em paralelo, verifique as **Áreas semeáveis**: se `02_Areas/` não tem as áreas-padrão (Financeiro, Marketing-e-Vendas, Operacao, Atendimento, Equipe, Admin-e-Juridico), proponha criá-las. Áreas específicas da empresa que você inferir do contexto (ex.: `Operacao-Pista` numa car wash) entram como sugestão separada.

Marque com **⚠ AMBÍGUO** todo item cujo destino você não tem certeza (tipicamente Projeto×Área).

### Fase 3 — Propor (dry-run)
Mostre ao usuário, sem ter movido nada:
1. As **pastas a criar** (caixas faltantes + áreas semeadas).
2. A **tabela de movimentação** completa (item → destino → motivo).
3. Os **itens ⚠ AMBÍGUO**, com a pergunta de decisão para cada um.
4. A lista de **intocáveis** que você deliberadamente deixou de fora.

Deixe explícito: "Nada foi movido ainda. Confirma este plano?"

### Fase 4 — Confirmar
Aguarde o **ok explícito**. Se o usuário resolver ambiguidades ou pedir ajustes, incorpore e re-apresente o trecho alterado. Não prossiga sem aprovação.

### Fase 5 — Aplicar
Só agora:
1. Crie as pastas faltantes (caixas + áreas aprovadas).
2. Mova cada item para seu destino com `mv`.
3. Grave, **na raiz da pasta-alvo**, dois arquivos de reversibilidade (ver abaixo).

Aplique exatamente o plano aprovado — nem mais, nem menos.

### Fase 6 — Justificar
Ao final, resuma o que foi feito (quantas pastas criadas, quantos itens movidos) e **explique 2 decisões representativas** — de preferência uma que tenha sido ambígua. Aponte o manifesto e como reverter.

---

## Reversibilidade (manifesto + reversor)

Na Fase 5, grave dois arquivos na raiz da pasta-alvo.

**`_MANIFESTO_PARA.tsv`** — uma linha por movimento, com cabeçalho. Colunas separadas por TAB:

```
origem	destino
contrato-fornecedor.pdf	02_Areas/Admin-e-Juridico/contrato-fornecedor.pdf
campanha-natal-brief.md	01_Projetos/Campanha-Natal/campanha-natal-brief.md
```

**`_reverter_para.sh`** — script que lê o manifesto e devolve cada item à origem:

```bash
#!/usr/bin/env bash
# Reverte a reorganização PARA. Roda a partir da raiz da pasta-alvo.
# Lê _MANIFESTO_PARA.tsv e move cada item de volta para a origem.
set -euo pipefail
cd "$(dirname "$0")"
tail -n +2 _MANIFESTO_PARA.tsv | while IFS=$'\t' read -r origem destino; do
  [ -z "$origem" ] && continue
  if [ -e "$destino" ]; then
    mkdir -p "$(dirname "$origem")"
    mv "$destino" "$origem"
    echo "revertido: $destino -> $origem"
  else
    echo "AVISO: não encontrado, pulando: $destino"
  fi
done
echo "Reversão concluída. As pastas vazias criadas pela skill permanecem (remova à mão se quiser)."
```

Depois de gravar, torne o reversor executável: `chmod +x "<pasta-alvo>/_reverter_para.sh"`.

O reversor desfaz **movimentos**. Pastas criadas vazias não são removidas automaticamente (segurança: pasta pode ter ganhado conteúdo depois). Avise isso ao usuário.

---

## Anti-padrões (não faça)

- Mover qualquer coisa antes da aprovação.
- Tocar em `CLAUDE.md`, `MEMORY.md` ou na pasta de Resources da empresa.
- Apagar arquivos — jamais. Só mover.
- Classificar "Empresa" como categoria. A empresa é o container; os itens dentro dela é que se classificam.
- Criar pastas de Projeto "por precaução". Projeto só existe se houver um projeto real. (Áreas, sim, podem ser semeadas.)
- Decidir uma ambiguidade Projeto×Área no silêncio. Pergunte.
- Organizar por tema ("Marketing", "Financeiro" como gavetas temáticas) em vez de acionabilidade. A não ser que sejam Áreas legítimas, mantidas continuamente.
