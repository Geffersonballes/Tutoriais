---
name: landing-completa-balles-tech
description: 'Roda o fluxo completo de qualidade (criar, criticar, revisar, corrigir, entregar prévia) para a landing page da Balles Tech Energia ou para uma página de campanha de energia solar. Use quando o pedido for "faz/refaz a landing da Balles Tech completa", "página de campanha para produtor rural/comércio/bateria", "/landing-completa-balles-tech" ou quando quiser que a página passe por crítico e revisor antes de mostrar. Para uma edição pequena (trocar um texto), use direto a skill landing-balles-tech.'
---

# Landing completa — Balles Tech

Fluxo em 5 etapas, com **agentes separados** para criar, criticar e revisar. Quem escreveu a página tende a defendê-la; um crítico com contexto limpo acha mais problemas. Argumento do usuário (`$ARGUMENTS`): o tema da página (ex.: "produtor rural", "bateria", "principal").

Skills de base (carregue antes de começar): `landing-balles-tech` (manda em fatos, paleta, estrutura e regras de texto), `landing-page-premium`, `copy-diagnose`, `copy-proof-check`, `web-review`.

## Etapa 0 — Briefing (1 minuto)

Escreva 5 linhas e mostre ao usuário só se algo estiver ambíguo: tema/público, qual tipo de imóvel pré-selecionar no simulador, bateria ligada ou não, mensagem de WhatsApp de origem (`data-msg`), o que será cortado do template. Dado que não está na skill `landing-balles-tech` (financiamento, prazos, marcas, depoimentos) **pergunte; não invente**.

## Etapa 1 — Criar (você, agente principal)

1. Parta de `assets/template.html` da skill `landing-balles-tech` (ou do `index.html` do repositório `geffersonballes/ballestech-landing-page` para a página principal). Trabalhe em branch de desenvolvimento.
2. Aplique o tema: título, subtítulo, fotos, `data-msg` de cada botão, pré-seleção do simulador. Página de campanha é **mais curta** que a principal.
3. Rode `node scripts/verificar.js` da skill base, se aplicável, e tire prints em 375px e 1366px (Playwright, `deviceScaleFactor: 1`) numa pasta do scratchpad.

## Etapa 2 — Crítico de copy (subagente, somente leitura)

Dispare um subagente `general-purpose` com este prompt (preencha `<...>`):

> Você é crítico de copy. NÃO edite arquivos. Leia `<caminho do HTML>` e as regras em `landing-balles-tech/SKILL.md`. Use o método da skill `copy-diagnose` e `copy-proof-check`. Objetivo da página: gerar conversa no WhatsApp com lead qualificado (sabe o valor da conta e o tipo de imóvel). Verifique e liste, citando o trecho exato: (1) promessas sem base — "conta zerada" é proibido, o limite é "até 95%"; (2) número de simulação sem a palavra "estimativa"; (3) fatos fora da lista (projetos, garantia, retorno, endereço, telefone) ou depoimento sem nome e cidade reais; (4) frases com adjetivo vazio ou foco em tecnologia em vez de economia e tranquilidade; (5) botão de WhatsApp sem `data-msg` própria; (6) mais de uma ação competindo com o CTA na mesma dobra. Devolva uma lista priorizada: `GRAVE | MÉDIO | LEVE`, trecho, problema, correção sugerida. Máx. 15 itens.

## Etapa 3 — Revisor visual e técnico (subagente, somente leitura)

Dispare um segundo subagente, **em paralelo** com a etapa 2:

> Você é revisor de design e qualidade. NÃO edite arquivos. Sirva a pasta com `python3 -m http.server` e use Playwright (já instalado, `require('playwright')`) em 375px e 1366px. Confira e **olhe os prints**: (1) console sem erros; (2) sem rolagem horizontal (`scrollWidth` = largura); (3) altura da página no celular — a principal tem ~5.300px; se passar de ~6.500px, avise; campanha deve ser menor; (4) amarelo `#FFC21A` só em botões de ação, controle do simulador e números de economia — nunca em texto sobre fundo claro; (5) contraste AA, botões ≥ 48px; (6) simulador responde e o botão abre o WhatsApp `556596401269` com valor e tipo escritos; (7) diagrama "um dia na sua casa" legível no celular; (8) imagens com `alt`, `lang="pt-BR"`, `prefers-reduced-motion` respeitado; (9) com a skill `web-review`: cara de "página genérica de IA"? Devolva lista `GRAVE | MÉDIO | LEVE` com o que viu, onde e como corrigir.

## Etapa 4 — Corrigir

Junte as duas listas, aplique **todos os GRAVE e MÉDIO** e os LEVE baratos. Para cada item recusado, anote o motivo. Rode de novo os prints e `verificar.js`. Se sobrou algum GRAVE, repita as etapas 2 e 3 **uma única vez** (no máximo 2 rodadas; depois, entregue com os pontos abertos listados).

## Etapa 5 — Entrega

1. Gere a prévia: `python3 scripts/gerar_previa.py <pasta-do-site> <saida>.html` (da skill base) e entregue o arquivo.
2. Commit e push **só na branch de desenvolvimento**. Passar para a `main`/publicar na Hostinger só depois que o dono aprovar a prévia.
3. Responda em português simples, sem jargão: o que mudou, o que o crítico e o revisor acharam (resumido), o que foi corrigido, o que ficou aberto e o que você precisa dele. Anexe os prints.

## Nunca

Inventar depoimento, número ou prazo; prometer conta zerada; mexer em DNS de e-mail (MX, SPF, DKIM, autodiscover) ou nos subdomínios que não são do site; publicar sem aprovação; apagar algo sem um "sim".
