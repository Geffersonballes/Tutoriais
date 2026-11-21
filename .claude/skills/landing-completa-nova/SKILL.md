---
name: landing-completa-nova
description: 'Roda o fluxo completo de qualidade (criar, criticar, revisar, corrigir, entregar) para QUALQUER outra landing page ou página de vendas nova que não seja a da Balles Tech nem a de professores — outro curso, produto, serviço ou oferta. Use em "faz uma landing para X completa", "/landing-completa-nova", "cria a página de vendas de Y e revisa antes de me mostrar".'
---

# Landing completa — página nova

Fluxo em 5 etapas com **agentes separados** para criar, criticar e revisar. Argumento (`$ARGUMENTS`): o produto/oferta. Skills de base (carregue antes): `landing-page-premium` (design, animação, estrutura técnica), `landing-page-copy`/`copywriting-kit:landing-page-copy`, `copy-diagnose`, `copy-proof-check`, `web-review`. Se for curso para professores, use `landing-completa-professores`; se for Balles Tech, `landing-completa-balles-tech`.

## Etapa 0 — Briefing (pergunte o que faltar, não invente)

Reúna: produto e promessa, público, preço e forma de pagamento, link do CTA (checkout/WhatsApp), quem entrega (nome, credenciais, foto real), prova real disponível (depoimentos com nome, números verificáveis) e referências visuais. Dado ausente vira `[PREENCHER]` visível. Escreva a **direção de arte em 5 linhas** (público/sensação, paleta, fontes, estilo de imagem, elemento-assinatura) conforme `landing-page-premium`.

## Etapa 1 — Criar (você, agente principal)

Esqueleto com todas as dobras e copy real (sem lorem ipsum), depois visual, depois animações. Arquivo único `.html`, mobile first (375px), CTA em constante fácil de trocar, SEO básico, `prefers-reduced-motion`. Capture prints em 375px e 1366px (Playwright).

## Etapa 2 — Crítico de copy (subagente, somente leitura)

> Você é crítico de copy. NÃO edite arquivos. Leia `<caminho do HTML>` e o briefing `<resumo>`. Use `copy-diagnose` e `copy-proof-check`, com o briefing como única evidência. Cite o trecho exato e liste: (1) promessas ou números sem base no briefing; (2) depoimentos, logos ou selos não fornecidos; (3) urgência/escassez sem data ou estoque real; (4) frases genéricas ("solução inovadora") e ordem das dobras (promessa → dor → virada → prova → oferta → objeções → CTA); (5) mais de uma ação competindo com o CTA principal por dobra; (6) CTA fraco ("Enviar"). Devolva `GRAVE | MÉDIO | LEVE`, trecho, problema, correção. Máx. 15 itens.

## Etapa 3 — Revisor visual e técnico (subagente, somente leitura, em paralelo)

> Você é revisor. NÃO edite arquivos. Sirva a pasta e use Playwright em 375px e 1366px; **olhe os prints**. Confira: console sem erros; sem rolagem horizontal; contraste AA e CTA como elemento de maior contraste; botões ≥ 48px; consistência (raios, sombras, espaçamentos por variáveis CSS); imagens com `alt` e `loading="lazy"` fora do hero; peso da página para 4G; com `web-review`: aparência genérica de IA, hierarquia, estados vazios. Devolva `GRAVE | MÉDIO | LEVE` com onde e como corrigir.

## Etapa 4 — Corrigir

Aplique GRAVE e MÉDIO e os LEVE baratos; refaça os prints. Se sobrar GRAVE, repita 2 e 3 uma vez (máx. 2 rodadas); depois entregue com os pontos abertos listados.

## Etapa 5 — Entrega

Entregue o HTML (e publique como Artifact só se fizer sentido para o usuário ver), os prints e um resumo em português simples: o que foi feito, o que crítico e revisor acharam, o que foi corrigido, o que ficou `[PREENCHER]`. Commit e push só na branch de desenvolvimento; publicar no domínio só com o "sim" do usuário.

## Nunca

Inventar depoimentos, números de alunos ou resultados; usar logos/marcas de terceiros sem autorização; deixar mais de uma ação competindo com o CTA.
