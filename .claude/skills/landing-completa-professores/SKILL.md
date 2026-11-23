---
name: landing-completa-professores
description: 'Roda o fluxo completo de qualidade (criar, criticar, revisar, corrigir, entregar) para a landing "IA para professores" do curso Docência Criativa (Prof. Romário Costa) ou para uma nova página de vendas para professores. Use em "refaz/atualiza a landing dos professores completa", "revisa a página do Romário com crítico", "/landing-completa-professores". Para trocar só preço ou link, use direto landing-ia-para-professores.'
---

# Landing completa — IA para professores

Fluxo em 5 etapas com **agentes separados** para criar, criticar e revisar. Argumento (`$ARGUMENTS`): o que mudar ("preço e FAQ", "página nova para outro curso", "revisão geral").

Skills de base (carregue antes): `landing-ia-para-professores` (manda no que é específico da página, no `CONFIG` e nos testes), `copy-pagina-vendas-professores`, `landing-page-premium`, `copy-diagnose`, `copy-proof-check`, `web-review`.

## Etapa 0 — Briefing

Se for a página existente: `git pull --ff-only` no repositório `Geffersonballes/docencia-criativa-landing` (use `add_repo` se faltar) e `npm ci` na primeira vez. Se for página nova de outro curso: anote público, promessa, preço, módulos, quem ensina. **O documento do curso é a fonte de verdade** — nada de conteúdo que ele não sustente. O que faltar fica `"[PREENCHER]"`.

## Etapa 1 — Criar (você, agente principal)

Edite com substituições exatas, só no que o pedido manda (`CONFIG`, `FAQ`, `DEMO`…). Comentários do código em português. Rode `npm test` (e `npm run contraste` se mexeu em cor, tamanho ou animação — esperado: "abaixo do mínimo AA: 0"). Capture com `scripts/capturas.js` da skill base (iPhone 11 e desktop 1280).

## Etapa 2 — Crítico de copy e de risco (subagente, somente leitura)

> Você é crítico de copy. NÃO edite arquivos. Leia `index.html` e as "Regras de conteúdo" de `landing-ia-para-professores/SKILL.md`; use `copy-diagnose` e `copy-proof-check`, com o documento do curso (`conteudo/aulas.json`) como evidência. Procure, citando o trecho: (1) benefício, ferramenta, formato ou resultado que o documento do curso não sustenta; (2) depoimento, número de alunos, selo ou estatística sem fonte; (3) urgência sem `dataEncerramento` real; (4) preço "de/por" sem venda anterior (risco CDC art. 37); (5) garantia vendida como vantagem em vez de direito (CDC art. 49, 7 dias); (6) "tudo grátis" sobre ferramentas; (7) IA vendida como substituta do professor — a regra é "a IA rascunha, o professor decide"; (8) tom: acolhedor, de professor para professor, sem jargão e sem vitimizar. Devolva lista `GRAVE | MÉDIO | LEVE`, trecho, problema, correção. Máx. 15 itens.

## Etapa 3 — Revisor de design, acessibilidade e peso (subagente, somente leitura, em paralelo)

> Você é revisor. NÃO edite arquivos. Rode `npm test` e `npm run contraste` e reporte o resultado literal. Abra os prints (celular 360px primeiro) e confira: (1) sem estouro de largura, palavra quebrada no meio ou texto apagado por efeito; (2) letra base 18px, botões ≥ 48px, contraste AA inclusive sobre o fundo animado; (3) teclado, `prefers-reduced-motion`, botões A−/A+; (4) peso do `index.html` ≤ 200 KB e sem pedidos externos (exceto o Meta Pixel quando houver `pixelId`); (5) links externos só checkout e redes do professor, com `target="_blank" rel="noopener"` e aviso "(abre em nova aba)"; (6) `[PREENCHER]` visível ou escondido de forma coerente; (7) com `web-review`: hierarquia, um CTA por dobra, aparência genérica. Antes de sugerir remover seção, consulte `references/historico.md`. Devolva `GRAVE | MÉDIO | LEVE` com onde e como corrigir.

## Etapa 4 — Corrigir

Aplique GRAVE e MÉDIO e os LEVE baratos. **Corrija a página, não o teste** (o teste só muda se a estrutura mudou de propósito). Rode `npm test` e `npm run contraste` de novo e refaça as capturas. Se sobrar GRAVE, repita 2 e 3 uma vez; depois entregue com os pontos abertos listados.

## Etapa 5 — Entrega

1. Commit em português (o título diz o que mudou para quem visita; corpo em tópicos curtos) na branch de desenvolvimento da sessão.
2. `git push origin main` (publica) e `bash .claude/skills/landing-ia-para-professores/scripts/conferir-publicado.sh .` **só se o dono pediu para publicar**; senão, entregue as capturas e espere o "pode publicar".
3. Responda em português simples: o que mudou, o que crítico e revisor acharam, resultado dos testes, divergências com o documento do curso, cuidados legais e o que depende dele.

## Nunca

Colocar o documento do curso (`conteudo/*.docx`) no repositório; inventar depoimento, número, parcelamento ou selo; cronômetro que reinicia; apagar branch, arquivo ou site, mexer em DNS de e-mail ou comprar algo sem "sim".
