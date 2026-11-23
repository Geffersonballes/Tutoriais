---
name: engajadamente
description: 'Contexto, decisões e próximos passos do domínio engajadamente.com.br (marca guarda-chuva dos cursos do dono, com um subdomínio ou página por curso) e da estrutura de hospedagem na Hostinger que ele divide com ballestech.com.br. Use sempre que o assunto for engajadamente, o domínio dos cursos, criar ou mover landing pages de cursos (Método Não Erre Mais, Docência Criativa / IA para professores e próximos), comprar ou configurar domínio, plano Premium da Hostinger, DNS dos cursos ou "retomar o que foi feito" nessa frente — mesmo que o usuário escreva "engajada mente", "domínio dos cursos" ou só "aquele domínio novo".'
---

# engajadamente.com.br — domínio dos cursos

Esta skill guarda o que foi decidido e feito até **23/11/2026** para que a próxima conversa retome sem perguntar tudo de novo. Leia inteira antes de agir e, ao terminar qualquer mudança nesta frente, **atualize o "Estado atual" e o "Registro"** abaixo (o dono pediu para manter o histórico).

## A ideia (decidida pelo dono)

- **engajadamente.com.br** = marca principal dos **cursos** do dono. Dentro dele ficam os sites/landing pages de cada curso, como subdomínio (`curso.engajadamente.com.br`) ou página (`engajadamente.com.br/curso`).
- **ballestech.com.br** = continua sendo só o site da **Balles Tech Energia** (energia solar). A landing dela tem skill própria: `landing-balles-tech` (repositório `geffersonballes/ballestech-landing-page`).
- Tudo na **mesma conta Hostinger** do dono, num plano **Premium** (vários sites no mesmo plano).

## Estado atual (23/11/2026)

**Ainda não feito — depende do dono (compras são sempre dele):**
- [ ] Comprar o domínio **engajadamente.com.br**. Em 18/11 estava **disponível** (o `.com` também). `.com.br` exige **CPF ou CNPJ** no registro — o dono decide em qual (o CNPJ da Balles Tech é de outra atividade). Preços vistos na Hostinger: 1 ano R$ 39,99 (renova R$ 64,99/ano); 2 anos R$ 94,98; 3 anos R$ 130,98. O Premium costuma dar **domínio grátis no 1º ano** — recomendação: usar esse benefício no engajadamente.com.br.
- [ ] Contratar o **plano Premium** da Hostinger. Preços vistos em 18/11: 1º ano R$ 119,88 (renova R$ 467,88/ano); 2 anos R$ 239,76; 4 anos R$ 479,52. O dono decidiu pelo Premium (vai hospedar Balles Tech + cursos). **Conferir no checkout quantos sites o Premium permite hoje** (a Hostinger muda esse limite).
- [ ] Opcional: registrar também engajadamente.com (proteção de marca).

**Já existe hoje:**
- Páginas de cursos publicadas no **GitHub Pages** (`geffersonballes.github.io`), como subdomínios do domínio da Balles Tech (CNAME no DNS de ballestech.com.br):
  - `naoerremais.ballestech.com.br` → landing do **Método Não Erre Mais**;
  - `docenciacriativa.ballestech.com.br` → landing **"IA para professores" / Docência Criativa** (Prof. Romário Costa), repositório `Geffersonballes/docencia-criativa-landing`, com skill própria `landing-ia-para-professores`.
- Conta Hostinger do dono, ligada pelo conector Hostinger (ferramentas `mcp__hostinger__*`): domínios **ballestech.com.br**, **ballestech.shop** (domínio grátis antigo), **balleseballes.com.br**, **balleseballes.online**. **Nenhum plano de hospedagem ativo** em 18–23/11.
- DNS de ballestech.com.br (na Hostinger): e-mail Hostinger ativo (MX, SPF, DKIM `hostingermail-a/b/c`, autodiscover, autoconfig, `_dmarc`), verificações do Google (TXT e CNAME `75070616`), `www` → raiz, registro A `@` = `162.241.61.38` (site antigo da Balles na HostGator; o `2.57.91.91` foi removido em 18/11 porque mostrava a página padrão da Hostinger sem SSL), e os CNAMEs dos cursos acima.

## Plano quando o dono comprar domínio + Premium

1. Conferir pelo conector: `domains_portfolio_list` (domínio apareceu?) e `hosting_orders_list` (plano ativo?).
2. Criar o site **engajadamente.com.br** no plano (`hosting_websites_create`) e esperar o setup (`hosting_websites_list-setups`).
3. Definir com o dono a página principal do engajadamente (vitrine dos cursos) — usar a skill `landing-page-premium`/`frontend-design` e o mesmo fluxo de prévia + aprovação usado na Balles Tech.
4. **Levar os cursos para o novo domínio sem quebrar links já divulgados:**
   - Se continuarem no GitHub Pages: criar no DNS do engajadamente.com.br os CNAMEs (`naoerremais` e `docenciacriativa` → `geffersonballes.github.io.`), trocar o domínio personalizado no GitHub Pages de cada repositório (arquivo `CNAME`) e ativar HTTPS.
   - Os endereços antigos `*.ballestech.com.br` só saem do DNS **depois** que os novos estiverem no ar e, se possível, com redirecionamento — links em anúncios, bio e checkout podem apontar para eles. Perguntar ao dono antes de remover (é irreversível para quem tem o link antigo).
   - Atualizar a skill `landing-ia-para-professores` (e a do Não Erre Mais, se houver) com o novo endereço.
5. Para a Balles Tech, no mesmo plano: seguir a skill `landing-balles-tech` (site novo, Git com implantação automática da `main`, trocar o A `@` de ballestech.com.br pelo IP do plano, SSL).

## Regras do dono (valem aqui também)

- **Reversível → fazer direto**: criar site, publicar, ajustar registros DNS de site (anotando o valor antigo), SSL, commits/push em branch.
- **Irreversível → explicar e esperar um "sim"**: apagar site/arquivos/e-mails, remover subdomínio em uso, resetar DNS, cancelar/alterar planos, force-push, apagar branch.
- **Compras e pagamentos sempre ficam com o dono** (a API da Hostinger permite comprar; não usar).
- Nunca mexer nos registros de e-mail dos domínios.
- Responder em português do Brasil, em linguagem simples.

## Ambiente de trabalho

- Ambiente de nuvem **"Tutoriais"**: internet liberada, transcritor de áudio (`transcrever arquivo`) e liberação automática das ferramentas do conector Hostinger instalados pelo script de inicialização.
- Repositórios: `geffersonballes/tutoriais` (onde está esta skill), `geffersonballes/ballestech-landing-page` (Balles Tech, com subagentes `copywriter-balles-tech`, `designer-interacoes`, `conteudo-balles-tech`, `qa-publicacao`).

## Registro

| Data | O que aconteceu |
|---|---|
| 2026-11-18 | Dono decide: engajadamente.com.br será o domínio principal dos cursos, com subdomínios por curso; ballestech.com.br fica só para a Balles Tech. |
| 2026-11-18 | Verificado: engajadamente.com.br e .com disponíveis; .com.br exige CPF/CNPJ. Preços de domínio e do Premium levantados. |
| 2026-11-18 | Dono escolhe o plano Premium da Hostinger (Balles Tech + cursos no mesmo plano). Compra ainda pendente. |
| 2026-11-18 | Identificados os cursos já no ar via GitHub Pages: naoerremais e docenciacriativa (subdomínios de ballestech.com.br). |
| 2026-11-23 | Skill criada para retomar o assunto em outra conversa; conversa original arquivada pelo dono. |
