# invisible-class-slides

Skill da Invisible que transforma **transcrição, roteiro ou esboço de aula** numa **apresentação didática para o professor projetar ao vivo numa turma**. Não é deck de vendas — é didática pura, regida pela ciência da aprendizagem (carga cognitiva de Sweller, multimídia de Mayer, asserção-evidência de Alley).

## Como funciona (visão geral)

A skill é um **designer instrucional**: não joga o texto da aula em bullets, transforma um argumento linear num argumento visual estruturado que respeita a memória de trabalho do aluno. Entrega dois artefatos, nesta ordem:

```
arranque → define os 2 dials (fidelidade + visual) + contexto + design system
  → [Transcrição/Roteiro] lê a aula inteira → mapa de proveniência
     [Esboço/Ideia]        pesquisa e desenvolve a aula
  → PASSADA 1: arco da aula + sequência de tipos de slide = PLANO  ◀── Output 1
  → APROVAÇÃO do usuário  (portão obrigatório)
  → PASSADA 2: instancia cada slide (ficha do tipo + 13 leis)
  → RENDER em HTML auto-contido  ◀── Output 2
```

- **Output 1 — Plano (storyboard):** a arquitetura da aula slide-a-slide. Fonte da verdade. Aprovado antes de qualquer render.
- **Output 2 — HTML:** apresentação auto-contida, navegação por teclado, builds (revelação progressiva), notas do professor, tela cheia. Linda de projetar.

## Estrutura do plugin

```
invisible-class-slides/
├── .claude-plugin/plugin.json
├── README.md
├── CLAUDE.md
├── design-systems/
│   └── invisible.md                 # design system padrão (extensível: 1 .md por tema/curso)
└── skills/invisible-class-slides/
    ├── SKILL.md                     # orquestrador fino (dials, 2 passadas, 2 outputs)
    └── references/
        ├── filosofia.md             # princípio-mestre + as 13 leis
        ├── arco-da-aula.md          # arco da aula + processo de 2 passadas
        ├── tipologia.md             # 8 famílias, ~47 tipos de slide (TOC + links)
        ├── fichas/                  # uma ficha executável por tipo
        ├── producao-visual.md       # roteamento de imagem, 4 modos, geração agnóstica
        ├── proveniencia.md          # contrato de fidelidade à aula do professor
        └── outputs.md               # plano → aprovação → HTML
```

## Como usar

Peça, em qualquer variação: "transforma essa transcrição em slides de aula", "monta a apresentação dessa aula", "gera slides didáticos a partir desse roteiro", "cria uma aula sobre X em slides".

A skill pergunta no arranque: a **fonte** (arquivo, texto colado, link), o **modo de fidelidade** (a aula já existe vs. é só um esboço), o **modo visual** (sem imagem / stock / geração), o **design system** e o **contexto do curso**. Depois entrega o plano para você aprovar e só então renderiza.

### Onde os outputs são salvos

```
class-slides/[nome-slug]/
  [nome-slug]_plano.md      # o storyboard aprovável
  [nome-slug].html          # a apresentação
```

`class-slides/` é criada no diretório de trabalho atual. Os outputs **não** são versionados no plugin — pertencem ao seu trabalho.

## Como adicionar um design system

Cada curso pode ter o seu tema visual. Para adicionar um:

1. Crie um `.md` em `design-systems/` (ex.: `bem-grandes.md`), seguindo o formato do `invisible.md`: paleta, tipografia, fundamentos, tabela de tipos de slide → classe CSS, **template HTML completo com o player** e instruções de uso.
2. Pronto. A skill descobre o novo design system sozinha (`ls ../../design-systems/`) e o oferece na escolha. Não é preciso editar o SKILL.md.

O padrão é o **Invisible** (modo escuro editorial, com piso de legibilidade de sala).

## Geração de imagem (portátil)

A skill faz design em HTML/CSS/SVG por conta própria (Modo 0, o default) e pode usar stock grátis (Modo 1). Para geração de imagem por IA (Modos 2/3), ela **detecta em tempo de execução** se há um gerador conectado via MCP; se não houver, avisa e segue em Modo 0/1. Não depende de nenhum servidor específico instalado — funciona em qualquer máquina.

## Instalação (plugin do Claude Code)

```
/plugin marketplace add arnoalcantara/invisible-skills
/plugin install invisible-class-slides@invisible-skills
```

## Escopo (v1)

- **Foco:** projeção ao vivo (professor presente). Modo autoestudo é roadmap.
- **Output:** HTML. Export para PowerPoint/Canva é roadmap (sempre a partir do plano, nunca convertendo o HTML).
