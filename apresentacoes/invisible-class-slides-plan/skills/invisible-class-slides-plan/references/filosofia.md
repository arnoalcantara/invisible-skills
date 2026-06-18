# Filosofia — o princípio-mestre e as 13 leis

> **Propósito.** Esta é a constituição da skill. Tudo que ela gera obedece ao princípio-mestre e às 13 leis. Leia **antes** de planejar qualquer deck (Passada 1) e tenha as leis à mão ao instanciar cada slide (Passada 2).
> **Lugar na cadeia:** primeira camada, acima de tudo (filosofia → arco → tipologia → produção visual).

---

## Princípio-mestre

A memória de trabalho do aluno é minúscula: **~4 blocos novos por vez, e dura segundos**. Tudo que aparece na tela consome esse orçamento de duas formas — gastando-o para entender **o conteúdo** (bom) ou para decifrar **o slide** (desperdício). Um bom slide didático gasta 100% do orçamento no conteúdo e 0% em si mesmo.

Essa é a régua. Toda decisão de design responde a uma pergunta só: *isto faz o aluno gastar memória entendendo a ideia, ou lutando com o slide?*

### Os três corpos de pesquisa que sustentam isto

- **Teoria da Carga Cognitiva (Sweller).** Três cargas competem pelo mesmo orçamento:
  - *Intrínseca* — a dificuldade inerente ao conteúdo. Não dá pra eliminar; dá pra **sequenciar** (do simples ao complexo, pré-treinar peças antes do todo).
  - *Extrínseca* — a carga imposta pela *forma* (slide confuso, texto que compete com a fala, decoração). É o inimigo. **Eliminar.**
  - *Germânica* — o esforço bom, de construir o esquema mental. Liberar orçamento (cortando a extrínseca) é liberar espaço **para ela**.
- **Teoria Cognitiva da Aprendizagem Multimídia (Mayer).** O aluno tem **dois canais** (visual e verbal), ambos limitados. Daí os princípios: coerência (cortar o irrelevante), sinalização (destacar o que importa), redundância (não ler o texto que está na tela em voz alta), contiguidade espacial (rótulo junto da coisa), segmentação (quebrar em pedaços no ritmo do aluno), pré-treino (vocabulário antes do processo).
- **Asserção-Evidência (Alley, Penn State).** A coluna vertebral estrutural da skill. O título do slide é uma **frase completa que afirma a ideia** ("A pressão cai conforme a altitude sobe"), e embaixo vem a **evidência visual** que sustenta a afirmação — não uma lista de bullets. Bullets descrevem; a evidência *mostra*.

---

## As 13 leis

Toda geração obedece, sempre. São a tradução operacional do princípio-mestre.

1. **Uma ideia por slide.** Duas ideias = dois slides. Se um slide tem mais de uma asserção defensável, quebre.
2. **Título é asserção, não tópico.** A linha de cima diz a *conclusão* ("A pressão cai conforme a altitude sobe"), não o *assunto* ("Pressão e altitude"). O título sozinho deve ensinar algo.
3. **Carga extrínseca mínima.** Cada elemento na tela se justifica ou é cortado. Decoração, logo grande, textura, ícone fofo — fora.
4. **Hierarquia visual explícita.** Um único ponto focal por slide. Tamanho, cor e posição dizem o que ler primeiro, segundo, terceiro. Se tudo grita, nada é ouvido.
5. **Mostrar, não listar.** Um diagrama/imagem que *é* a evidência vence o bullet que a descreve. O bullet é o último recurso, não o primeiro.
6. **Slide não duplica a fala.** A voz carrega o difícil de mostrar; o slide carrega o difícil de dizer. Nunca encha a tela com o texto que o professor vai ler em voz alta (princípio da redundância de Mayer — texto idêntico à fala *atrapalha*).
7. **Rótulo junto da coisa.** Anote o diagrama no próprio ponto, não numa legenda distante (contiguidade espacial). O olho não deve viajar pra cruzar nome e objeto.
8. **Revelação progressiva.** Builds em etapas, no ritmo da explicação. Não despeje o slide pronto se a ideia se constrói em passos.
9. **Pré-treinar vocabulário.** Apresente as peças (termos, símbolos) antes do todo. O aluno não pode aprender o processo e o jargão ao mesmo tempo.
10. **Espaço em branco é estrutura.** O vazio agrupa, separa e hierarquiza. Não é espaço "a preencher" — é elemento de design.
11. **Piso de legibilidade.** Tipografia grande (legível do fundo da sala), alto contraste, sistema de cor e fonte enxuto e consistente. Em projeção ao vivo isto não é estética, é função.
12. **Pontos de processamento ativo.** Momentos de "preveja / compare / lembre / resolva" espalhados, não só no fim. Aprender exige *fazer*, não só receber.
13. **Espinha narrativa.** O deck tem um fio condutor; cada slide avança nele e o aluno sempre sabe onde está. Sem espinha, é uma pilha de slides; com ela, é uma aula.

---

## Foco: projeção ao vivo (v1) e o modo autoestudo (roadmap)

O alvo desta versão é **projeção ao vivo**: o professor está presente e a voz dele carrega parte da carga cognitiva. Isso permite uma tela mais limpa — o slide não precisa explicar sozinho, porque há um narrador humano. **Default e único modo do v1.**

A skill também prevê, como **modo futuro (roadmap)**, uma versão de **autoestudo**: o aluno consome sem narrador, então o slide precisa explicar-se sozinho — mais texto na tela, mais autossuficiência. **Atenção:** vários princípios de Mayer se *invertem* entre os dois modos (o princípio da redundância, por exemplo, vira ao contrário quando não há voz). Por isso o autoestudo não é só "o mesmo deck com mais texto": ele separa uma **camada de projeção** (limpa) de uma **camada de referência** (notas/handout). Implementar isso é trabalho à parte — fica para uma versão posterior. No v1, quando o usuário pedir autoestudo, avise que o foco atual é projeção ao vivo e ofereça gerar o deck ao vivo + notas do professor robustas como aproximação.

---

## Como a IA deve usar este documento

- **Na Passada 1 (arquitetura):** as leis 1, 12 e 13 guiam a *sequência* — uma ideia por slide define quantos slides; processamento ativo define onde entram os respiros; espinha narrativa define o fio.
- **Na Passada 2 (instanciação):** as leis 2–11 guiam *cada slide* — asserção no título, hierarquia, mostrar em vez de listar, builds, legibilidade.
- **Quando algo na tela não passa na régua** ("isto é conteúdo ou é ruído?"), corte. A dúvida resolve sempre a favor de menos.

---

## Cruzamento com os outros módulos

- [arco-da-aula.md](arco-da-aula.md) — as leis 12 e 13 se realizam no arco e na consciência posicional.
- [tipologia.md](tipologia.md) — a lei 5 (mostrar, não listar) é o critério que separa as famílias; cada ficha aplica as leis de carga.
- [producao-visual.md](producao-visual.md) — as leis 3, 4, 7 e 10 governam o que entra (ou não) como imagem.
- [proveniencia.md](proveniencia.md) — a fidelidade ao conteúdo é a contraparte ética das leis de forma.
