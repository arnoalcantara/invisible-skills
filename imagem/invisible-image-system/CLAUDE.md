# CLAUDE.md — invisible-image-system

Este arquivo orienta qualquer instância de Claude que trabalhe neste repositório.

## O que é este sistema

Agente de geração de imagem da Invisible. Opera como **Diretor de Fotografia cinematográfico**: interpreta qualquer pedido (frase, palavra, referência visual) e produz uma imagem via Higgsfield CLI usando o formato de prompt **Nano Banana 2**.

A skill é autônoma: decide câmera, lente, luz e post sem pedir ao usuário — pergunta apenas o que é operacionalmente necessário (aspect ratio, resolução).

## Estrutura

```
invisible-image-system/
├── .claude-plugin/
│   └── plugin.json        # manifesto do plugin (bumpar versão ao publicar)
├── skills/
│   └── invisible-image/
│       └── SKILL.md       # agente principal
├── CLAUDE.md              # este arquivo
└── README.md              # visão do sistema para humanos
```

## Fluxo de trabalho (Git)

1. Edite `skills/invisible-image/SKILL.md` conforme o pedido.
2. **Suba a versão em `.claude-plugin/plugin.json`** a cada mudança publicada — sem bump, o marketplace não entrega a atualização.
3. Commit seguindo o padrão:
   - `feat: ...` novo comportamento ou regra
   - `fix: ...` correção
   - `docs: ...` README/CLAUDE sem mexer na skill
   - `chore: ...` bump de versão, estrutura
4. Push apenas quando o usuário pedir.

## Versionamento (semver)

- **patch** (1.0.0 → 1.0.1): correção de prompt, ajuste de lente/stock.
- **minor** (1.0.0 → 1.1.0): nova câmera, novo look, nova seção.
- **major** (1.0.0 → 2.0.0): mudança incompatível no fluxo ou no formato do prompt.

## Nunca faça

- Copiar conteúdo da SKILL.md para outro arquivo (mantém único ponto de verdade).
- Fazer push sem bumpar a versão quando houver mudança na skill.
