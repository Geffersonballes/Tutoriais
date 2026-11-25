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
    tituloPagina: "Achadinhos da Lay | Grupo de ofertas no WhatsApp",
    descricao: "Grupo gratuito no WhatsApp com achadinhos garimpados na Shopee para casa, beleza, criançada e utilidades. Grupo independente, com links de afiliado.",
    selo: "Grupo gratuito no WhatsApp",
    titulo: "Achadinhos para casa, beleza e criançada [direto no seu WhatsApp]", // o trecho entre [ ] fica dourado
    subtitulo: "Ofertas garimpadas na Shopee, com preço e link de afiliado. Grupo independente: não somos a Shopee.",
    botao: "Entrar no grupo de ofertas",
    abaixoDoBotao: "Grátis · só admins postam · você sai quando quiser",
    todosCheios: "Os grupos estão cheios. Um novo grupo abre em breve!",
    nicho: "casa, beleza, criançada e utilidades",
  },

  // Prints de ofertas reais (ex.: ["prints/oferta1.jpg"]). Vazio = a seção não aparece.
  prints: [],
};
