# Landing "entrar no grupo" (template)

Dois arquivos: `index.html` (layout, igual para todos os clientes) e `config.js` (tudo que muda por cliente).
Página de ~19 KB, sem fontes externas nem bibliotecas: abre rápido no 4G.

## Novo cliente
1. Copie a pasta `landing/`.
2. No `index.html`, troque **só as 8 linhas do topo** (título, descrição, endereço e `og.jpg`): quem gera a prévia do link no WhatsApp ou no Instagram não roda JavaScript.
   Gere um `og.jpg` de 1200×630 com a logo.
3. Em `config.js`, troque: `marca` (nome, logo, iniciais, Instagram), `cores`, `grupos`, `pixelId` e `textos`.
4. Coloque o arquivo da logo na mesma pasta (ex.: `logo.png`, quadrado, até 512 px, até 60 KB).
5. Abra o `index.html` no navegador para conferir e envie para a hospedagem.

## Rodízio de grupos
A página usa o **primeiro grupo da lista com `cheio: false`**. Quando um grupo encher (perto de 1.024 pessoas),
mude `cheio` para `true` e acrescente o próximo grupo. Se todos estiverem cheios, o botão vira um aviso.

## Medição
- **Pixel da Meta:** cole o número em `pixelId`. A página envia `PageView` ao abrir e `Lead` + `EntrarNoGrupo`
  no clique do botão (com o grupo, o botão clicado e as UTMs). Sem `pixelId`, nada de rastreio é carregado.
- **UTMs** (o convite do WhatsApp não guarda UTM, então a origem é medida na landing):

Padrão combinado com a sessão do Instagram (`../instagram/PLANO-IG.md`):

| Origem | Link |
|---|---|
| Bio do Instagram | `https://DOMINIO/?utm_source=instagram&utm_medium=bio&utm_campaign=perfil` |
| Story (link manual) | `https://DOMINIO/?utm_source=instagram&utm_medium=story&utm_campaign=aaaa-mm-dd` (ou o tema) |
| Anúncio | `https://DOMINIO/?utm_source=instagram&utm_medium=paid_social&utm_campaign=encher-grupo-nov26` |
| Aviso de grupo cheio | `https://DOMINIO/?utm_source=whatsapp&utm_medium=grupo_cheio&utm_campaign=rodizio` |

## Visual (versão 3D, pedida pelo cliente #1)
Fundo com piso em grade em perspectiva, anéis girando em volta da logo, cartões de vidro que inclinam com o mouse, botão com brilho correndo e entrada das seções em 3D.
Feito **só com CSS** (sem three.js), então a página continua leve. Tudo desliga com "reduzir movimento". No título, o trecho entre `[colchetes]` em `config.js` fica dourado.

## Antes de divulgar (parecer da conformidade, 25/11/2026)
- Link real do grupo em `grupos`.
- "Shopee" não pode aparecer como título nem como nome. Só serve para descrever a origem, junto com "não somos a Shopee".
- **Pixel:** só depois de um banner de consentimento (o Pixel carrega só após "Aceitar") **e** de `privacidade.html`, com o responsável (nome, CPF ou CNPJ, e-mail). Um advogado deve revisar.
- Anúncios: só pela conta do Instagram cadastrada no Programa de Afiliados da Shopee. Nunca no Google.

## Regras de conteúdo
Sem urgência falsa, sem números inventados, transparência de afiliado e aviso antigolpe. A seção de prints
só aparece quando houver prints **reais** em `prints`.
