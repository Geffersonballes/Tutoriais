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
    logo: "",
    iniciais: "AL",
    instagram: "", // ex.: "https://instagram.com/achadinhosdalay" (vazio = não aparece)
  },

  // Cores da marca (RASCUNHO: trocar pelas cores da logo quando o dono enviar)
  cores: {
    fundo: "#FFF8EC",
    texto: "#2A1A12",
    destaque: "#F4B23E", // amarelo 💛 dos textos do grupo
    botao: "#0F7A43",    // verde de WhatsApp, escurecido para o texto branco ficar legível
    botaoTexto: "#FFFFFF",
  },

  grupos: [
    // { nome: "Grupo 1", link: "https://chat.whatsapp.com/XXXXXXXX", cheio: false },
    { nome: "Grupo 1", link: "", cheio: false },
  ],

  // Pixel da Meta: cole só o número do Pixel. Vazio = nenhum rastreio é carregado.
  pixelId: "",

  textos: {
    tituloPagina: "Achadinhos da Lay | Grupo de ofertas da Shopee no WhatsApp",
    descricao: "Grupo gratuito no WhatsApp com achadinhos da Shopee para casa, beleza, criançada e utilidades. Só admins postam.",
    selo: "Grupo gratuito no WhatsApp",
    titulo: "Achadinhos da Shopee direto no seu WhatsApp",
    subtitulo: "Ofertas para casa, beleza, criançada e utilidades do dia a dia, com preço e link, num grupo organizado.",
    botao: "Entrar no grupo de ofertas",
    abaixoDoBotao: "Grátis · só admins postam · você sai quando quiser",
    todosCheios: "Os grupos estão cheios. Um novo grupo abre em breve!",
    nicho: "casa, beleza, criançada e utilidades",
  },

  // Prints de ofertas reais (ex.: ["prints/oferta1.jpg"]). Vazio = a seção não aparece.
  prints: [],
};
