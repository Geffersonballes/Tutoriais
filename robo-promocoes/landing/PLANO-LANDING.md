# Landing page do "Achadinhos da Lay": plano e passagem de sessão

Frente **aninhada** ao projeto Robô de Promoções (`robo-promocoes/`). Leia antes: `../PLANO.md`,
`../MANUAL-DE-REPLICACAO.md` (§3.2 referência "Promos da Beco", §3.3 Instagram), `../textos-do-grupo.md`
e `../instagram/PLANO-IG.md`.

## Funil decidido pelo dono (25/11/2026)
Instagram (bio, posts, anúncios) → **landing page** → botão → **grupo de WhatsApp** "Achadinhos da Lay".

## O que a landing precisa fazer
1. Página leve, pensada primeiro para o celular (abre em menos de 2 s no 4G), com a cara da marca (logo do dono)
   e um CTA único e grande: "Entrar no grupo de ofertas" → link de convite do grupo.
2. **Rodízio de grupos:** quando um grupo enche (perto de 1.024), o botão passa a apontar para o próximo. O link do grupo
   atual fica num lugar fácil de trocar (arquivo de configuração ou JSON), sem mexer no layout. No futuro, o robô
   pode atualizar sozinho.
3. Prova e confiança: exemplos de ofertas reais (prints) quando existirem, "só admins postam", "pode silenciar",
   alerta antigolpe, transparência de que os links são de afiliado e LGPD (a página não coleta dados).
4. Medição: Pixel da Meta e evento de clique no botão (para os anúncios do Instagram), além de UTM por origem
   (bio, story, anúncio).
5. Hospedagem: Hostinger (o dono já tem hospedagem e o conector `hostinger`). Domínio ou subdomínio a definir com o
   dono (ex.: um subdomínio de domínio que ele já tenha, ou um domínio novo da marca).
6. **Replicável para o produto:** um template em que, para cada cliente novo, só mudam o nome, a logo, as cores, os links
   e os textos.

## Regras
- Um passo por vez com o dono, em português simples, esperando a confirmação.
- Nada publicado sem a aprovação do dono (mostrar uma prévia antes).
- Sem urgência falsa, sem promessa de ganho, com transparência de afiliado. Passar pelo `promo-critico` e
  pelo `promo-conformidade`.
- Credenciais nunca no chat nem no Git.

## Skills e agentes úteis
Skill `anthropic-skills:landing-page-premium` (HTML único, mobile-first); agentes `promo-copywriter`, `promo-critico`,
`promo-conformidade`, `promo-divulgacao-instagram`, `promo-documentador`.

## Pendências do dono
Domínio/subdomínio, logo em arquivo, cores da marca, link de convite do grupo (só divulgar quando as ofertas
reais estiverem saindo) e o número oficial de atendimento.
