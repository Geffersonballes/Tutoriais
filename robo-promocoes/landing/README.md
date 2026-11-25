# Landing "entrar no grupo" (template)

Dois arquivos: `index.html` (layout, igual para todos os clientes) e `config.js` (tudo que muda por cliente).
Página de ~19 KB, sem fontes externas nem bibliotecas: abre rápido no 4G.

## Novo cliente
1. Copie a pasta `landing/`.
2. Em `config.js`, troque: `marca` (nome, logo, iniciais, Instagram), `cores`, `grupos`, `pixelId` e `textos`.
3. Coloque o arquivo da logo na mesma pasta (ex.: `logo.png`, quadrado, até 512 px, até 60 KB).
4. Abra o `index.html` no navegador para conferir e envie para a hospedagem.

## Rodízio de grupos
A página usa o **primeiro grupo da lista com `cheio: false`**. Quando um grupo encher (perto de 1.024 pessoas),
mude `cheio` para `true` e acrescente o próximo grupo. Se todos estiverem cheios, o botão vira um aviso.

## Medição
- **Pixel da Meta:** cole o número em `pixelId`. A página envia `PageView` ao abrir e `Lead` + `EntrarNoGrupo`
  no clique do botão (com o grupo, o botão clicado e as UTMs). Sem `pixelId`, nada de rastreio é carregado.
- **UTMs** (o convite do WhatsApp não guarda UTM, então a origem é medida na landing):

| Origem | Link |
|---|---|
| Bio do Instagram | `https://DOMINIO/?utm_source=instagram&utm_medium=bio` |
| Story | `https://DOMINIO/?utm_source=instagram&utm_medium=story` |
| Post/reels | `https://DOMINIO/?utm_source=instagram&utm_medium=post` |
| Anúncio | `https://DOMINIO/?utm_source=instagram&utm_medium=anuncio&utm_campaign=NOME` |
| Grupo cheio (aviso) | `https://DOMINIO/?utm_source=whatsapp&utm_medium=grupo_cheio` |

## Regras de conteúdo
Sem urgência falsa, sem números inventados, transparência de afiliado e aviso antigolpe. A seção de prints
só aparece quando houver prints **reais** em `prints`.
