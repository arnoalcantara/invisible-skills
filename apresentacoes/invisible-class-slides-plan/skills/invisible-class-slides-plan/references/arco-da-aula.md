# O arco da aula e o processo de duas passadas

> **Propósito.** Antes de escolher tipos de slide, monte a **arquitetura** da aula. Um slide é uma frase dentro de um argumento; sem o argumento, viram frases soltas. Este módulo define o arco, a consciência posicional de cada slide e o processo de duas passadas que é o núcleo do motor.
> **Lugar na cadeia:** segunda camada (filosofia → **arco** → tipologia → produção visual). Leia na Passada 1.

---

## O arco canônico

Esqueleto default, adaptável ao conteúdo. Sete funções, na ordem natural de uma aula:

1. **Fisgar** — abrir uma lacuna, tensão ou pergunta. O aluno precisa *querer* a resposta antes de recebê-la. Sem desejo de saber, o resto é ruído.
2. **Orientar** — objetivos + mapa. Onde vamos, por quê, e como o caminho se organiza. (Pré-treino de estrutura: a lei 9 em escala de aula.)
3. **Ativar** — puxar o que o aluno já sabe. O conhecimento novo gruda no antigo; sem âncora, escorrega.
4. **Desenvolver** — o corpo, em **blocos**. Cada bloco tem seu próprio mini-arco: *apresenta → mostra → checa*. É aqui que mora a maior parte dos slides.
5. **Processar** — atividade ativa **espalhada**, não só no fim (lei 12). Prever, comparar, resolver, recuperar da memória.
6. **Consolidar** — síntese, takeaway, antecipação do erro comum. Amarra o que foi construído.
7. **Fechar** — fechar o arco aberto no Fisgar e abrir ponte para a próxima aula.

### O padrão rítmico que se repete em escalas
**Tensão → resolução → consolidação.** Vale para a aula inteira (fisga, desenvolve, consolida) e para *cada bloco* dentro do Desenvolver (levanta a pergunta, mostra a resposta, fixa). É o batimento da aula. Gagné (eventos de instrução), 5E (engage-explore-explain-elaborate-evaluate) e Rosenshine (prática guiada) são variações do mesmo padrão — **não dogmatize um modelo; capture o padrão.**

### Adaptação
O arco é default, não camisa de força. Uma aula de revisão pode ter Fisgar curtíssimo e Processar longo; uma aula introdutória investe pesado em Ativar e Orientar. Ajuste as proporções ao conteúdo e ao público — mas raramente pule o Fisgar e o Fechar, que são o que dá unidade.

---

## Consciência posicional

Cada slide responde três perguntas. É assim que se decidem transições, sinais de "você está aqui", predições e ganchos:

- **De onde venho?** — o que o slide anterior estabeleceu e que este assume como dado.
- **Que trabalho faço?** — minha função na tipologia (apresento? comparo? checo? consolido?).
- **Pra onde aponto?** — o que preparo no próximo slide; que gancho deixo aberto.

Um slide que não sabe responder isso é um slide órfão — provavelmente deveria ser fundido, cortado, ou ter uma transição explícita. Preencha esse campo no plano de **todo** slide.

---

## O processo de duas passadas (núcleo do motor)

A separação entre arquitetar e instanciar é o que impede o deck de virar lista. **Nunca colapse as duas passadas.**

### Passada 1 — Arquitetura → o PLANO (Output 1)
Trabalho de *designer instrucional*, não de diagramador:
1. Ler o conteúdo **todo** (no Modo Transcrição) ou pesquisar e desenvolver (no Modo Esboço).
2. No Modo Transcrição: montar o **mapa de proveniência** (ver [proveniencia.md](proveniencia.md)) — classificar cada unidade de ideia antes de decidir o que vira slide.
3. Segmentar em **blocos** e atribuir a cada um sua **função no arco**.
4. Decidir a **sequência de tipos**: para cada slide, qual família/tipo da [tipologia.md](tipologia.md), escolhido pela *função didática*.
5. Definir ritmo, densidade, **respiros**, pontos de **build** e de **processamento ativo**.
6. Resolver a **consciência posicional** de cada slide.

O resultado é o storyboard slide-a-slide — o **PLANO**, que o usuário aprova. É a fonte da verdade.

### Passada 2 — Instanciação (dentro do plano)
Acontece na própria Passada 1, ao escrever cada bloco do plano: abrir a **ficha** do tipo, aplicar as **13 leis**, fixar o conteúdo concreto e **declarar** a intenção visual no campo `Visual:`. O resultado é o plano completo no contrato `slides-plan` v1 ([slides-plan-spec.md](slides-plan-spec.md)). O **render em HTML** é um passo posterior, feito por outro plugin (`invisible-slides-plan-visual`) a partir do plano aprovado — não acontece aqui.

> **Por que separar.** Na Passada 1 você pensa na aula como um todo — o fio, o ritmo, os respiros. Na Passada 2 você pensa em cada slide como um artefato. Misturar as duas leva a otimizar slides lindos que não formam uma aula. Sem a Passada 1, o deck vira lista; com ela, ganha espinha (lei 13).

---

## Como a IA deve usar este documento

- Comece a Passada 1 esboçando o arco em alto nível (quantos blocos, que função cada um) **antes** de pensar em slides individuais.
- Use o padrão tensão→resolução→consolidação como teste: cada bloco levanta algo, resolve e fixa? Se um bloco só "informa" sem tensão nem fixação, provavelmente está plano demais — adicione um Fisgar local ou um ponto de processamento.
- Preencha a consciência posicional de todo slide no plano. Slides órfãos são sinal de arquitetura frouxa.

---

## Cruzamento com os outros módulos

- [filosofia.md](filosofia.md) — as leis 12 (processamento ativo) e 13 (espinha narrativa) vivem aqui.
- [tipologia.md](tipologia.md) — a sequência de tipos da Passada 1 sai da tipologia, escolhida por função.
- [proveniencia.md](proveniencia.md) — o mapa de proveniência é uma sub-etapa da Passada 1 no Modo Transcrição.
- [slides-plan-spec.md](slides-plan-spec.md) — o formato em que a Passada 1 escreve o plano (o output desta skill); o render derivado é responsabilidade do `invisible-slides-plan-visual`.
