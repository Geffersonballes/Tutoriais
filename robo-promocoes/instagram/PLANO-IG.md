# Instagram do "Achadinhos da Lay": plano e passagem de sessão

Frente de trabalho **aninhada** ao projeto Robô de Promoções (`robo-promocoes/`).
Leia antes: `../PLANO.md`, `../MANUAL-DE-REPLICACAO.md` (§3.2 referência "Promos da Beco" e §3.3 Instagram)
e `../textos-do-grupo.md`.

## Objetivo
Instagram **novo** do Achadinhos da Lay, com **postagem automática**, servindo de vitrine e funil para o
grupo de WhatsApp. **Atualização:** a bio aponta para a landing page (`../landing/PLANO-LANDING.md`), que leva ao grupo. Faz parte do produto que será vendido a outras contas: registrar
cada aprendizado no manual (§3.3 e no diário).

## Estado em 25/11/2026
- O dono recebeu o **Passo IG-1** e ainda não confirmou: criar a conta com e-mail (sugestão @achadinhosdalay),
  logo como foto, conta profissional (Criador ou Empresa), Página do Facebook vinculada, sem link do grupo na bio por
  enquanto, aquecimento de 1 a 2 semanas com posts manuais.
- O grupo de WhatsApp e o robô já funcionam (formatos aprovados). Aguardando a liberação da Shopee Open API.
- A descrição do grupo está em rascunho (o dono vai alterar). O número oficial de atendimento ainda não foi definido.

## Próximos passos (um por vez, esperando a confirmação do dono)
1. Confirmar o IG-1: @ escolhido, conta profissional e Página do Facebook vinculada.
2. Conectar o IG ao **Metricool** (o dono já usa no TikTok; conector `Metricool_Social_Media_Management`).
   Conferir as marcas existentes (`getBrandSettings`) e se o plano permite outra marca/rede.
3. Plano de aquecimento (2 semanas): bio, destaques, 6 a 9 posts iniciais e o que fazer à mão cada dia.
4. Linha editorial automática (já existe um protótipo de reel: `criativos/2026-11-25_teste-voz-laynner.mp4`, com voz clonada
   "Laynner" no ElevenLabs, eleven_v4 com a tag [animada], ~228 créditos por versão, mais um vídeo 1080x1920 de 12 s montado no ffmpeg; o produto é de exemplo e
   **o dono ainda não avaliou**). Itens: carrossel "Top 5 achadinhos do dia" (imagem gerada a partir das ofertas que o robô postou),
   reels de produto e stories. A API não permite figurinha de link no story, então o link (da landing) fica na bio.
5. Integração com o robô: gerar as artes a partir da tabela `postados` e agendar pelo Metricool, sem urgência falsa e
   com transparência de afiliado.
6. Anúncios para encher o grupo (com o agente `promo-divulgacao-instagram` e o veto do `promo-conformidade`).

## Agentes úteis
`promo-divulgacao-instagram`, `promo-copywriter`, `promo-critico`, `promo-conformidade`, `promo-cacador-de-tendencias`,
`promo-documentador`.

## UTMs combinados com a landing (usar sempre estes)
Base: URL da landing + `?utm_source=instagram&utm_medium=<meio>&utm_campaign=<campanha>`
| Origem | utm_medium | utm_campaign |
|---|---|---|
| Link da bio | `bio` | `perfil` |
| Story (link manual, quando postar à mão) | `story` | `aaaa-mm-dd` ou tema |
| Anúncio | `paid_social` | nome da campanha (ex.: `encher-grupo-nov26`) |
Se a sessão da landing definir outro padrão, prevalece o dela; atualizar esta tabela.
