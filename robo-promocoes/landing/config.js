/*
 * CONFIGURAÇÃO DA LANDING — é o ÚNICO arquivo que muda de um cliente para outro.
 * O index.html não precisa ser tocado.
 *
 * Rodízio de grupos: a página manda a pessoa para o PRIMEIRO grupo da lista com `cheio: false`.
 * Quando um grupo encher, troque `cheio` para true (ou acrescente o grupo novo no fim da lista).
 * Se todos estiverem cheios, o botão mostra o aviso `textos.todosCheios`.
 */
window.LANDING = {
  marca: {
    nome: "Achadinhos da Lay",
    // Caminho da logo (ex.: "logo.png"). Vazio = mostra as iniciais no lugar da logo.
    logo: "logo.webp",
    iniciais: "AL",
    instagram: "", // ex.: "https://instagram.com/achadinhosdalay" (vazio = não aparece)
  },

    cores: {
    // Tiradas da logo (preto + dourado). O botão é a cor de maior contraste da página.
    fundo: "#0B0B0B",
    texto: "#FFF6DD",
    destaque: "#FFC21A",
    botao: "#FFC21A",
    botaoTexto: "#111111",
  },

  grupos: [
    // { nome: "Grupo 1", link: "https://chat.whatsapp.com/XXXXXXXX", cheio: false },
    { nome: "Grupo 1", link: "", cheio: false },
  ],

  // Pixel da Meta: cole só o número do Pixel. Vazio = nenhum rastreio é carregado.
  pixelId: "",

  textos: {
    tituloPagina: "Achadinhos da Lay | Pare de caçar promoção, ela chega até você",
    descricao: "Grupo gratuito no WhatsApp com ofertas com desconto selecionadas todo dia. Grupo independente, com links de afiliado.",
    selo: "Grupo gratuito no WhatsApp",
    titulo: "Pare de caçar promoção. [Ela chega até você.]", // o trecho entre [ ] fica dourado
    subtitulo: "Ofertas com desconto escolhidas a dedo todo dia, direto no seu WhatsApp.",
    // 3 frases curtas de impacto (aparecem como selos embaixo do título)
    destaques: ["🔥 Ofertas novas todo dia", "🏷️ Desconto + link direto", "🔒 Ninguém chama no privado"],
    botao: "Quero entrar no grupo",
    abaixoDoBotao: "Só admins postam · silencie ou saia quando quiser",
    // linha pequena do rodapé (transparência obrigatória: afiliado + independência + preço + golpe)
    aviso: "Ofertas da Shopee divulgadas com links de afiliado: podemos receber comissão, sem custo extra para você. Grupo independente, não somos a Shopee. Preços e estoque podem mudar. ⚠️ A equipe nunca pede Pix nem chama no privado.",
    todosCheios: "Os grupos estão cheios. Um novo grupo abre em breve!",
  },

};
