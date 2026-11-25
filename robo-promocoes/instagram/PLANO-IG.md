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

## Atualização 25/11/2026 (tarde)
- Pela sessão principal: o dono já **criou o Instagram e a Página do Facebook**. Ainda faltam o @, a conta profissional e o vínculo.
- A capa v2 do Facebook já usa a logo oficial (preto e dourado), que está em `marca/logo.webp`.
- Metricool (consulta só de leitura): há 3 marcas na conta (ballestech, geffersonballes1, laycmballes) e **nenhuma é do
  Achadinhos**. No IG-2, criar uma **marca nova** "Achadinhos da Lay" e conectar o IG e a Página. Antes, conferir se o plano
  do Metricool permite mais uma marca.

- ✅ **IG-1 concluído (confirmado pelo dono):** **@achadinhosdalay40** (o @ sem número já existia), conta profissional; Página do Facebook **vinculada** (confirmado pelo dono).
  Agora: **IG-2** (marca nova no Metricool).

- IG-2 (Metricool), conferido pela API: **achadinhosdalay40 entrou na marca existente "laycmballes"** (id 8357037) e
  substituiu o @os_discipulados. Nenhuma marca nova apareceu. A mesma marca tem o TikTok laycmballes, o YouTube da Lay e uma
  Página do FB (id 1369610699580001; conferir se é a Achadinhos). Aguardando o dono decidir: manter assim ou separar.

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
Facebook e TikTok: o mesmo padrão, mas com `utm_source=facebook` ou `utm_source=tiktok`.
Se a sessão da landing definir outro padrão, prevalece o dela; atualizar esta tabela.

## Marca (rascunho da sessão principal, 25/11, ainda não aprovado pelo dono)
`marca/bios.md` (bios de IG, FB e TikTok, todas levando à landing) e `marca/capa-facebook-1640x624.png`. As cores são provisórias.
A bio do IG não tem espaço para avisar que os links são de afiliado. Por isso o aviso fica no destaque "Dúvidas" e na landing.
