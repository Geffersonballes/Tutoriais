# Manual de replicação: robô de promoções para um novo cliente

Objetivo: tudo o que aprendemos montando o **cliente #1 (o próprio dono)** fica
registrado aqui, para que montar a próxima conta seja só seguir a receita.
Este robô vai virar um **produto vendido** (automação de grupos de achadinhos).

> Regra para o Claude: a cada passo concluído, ou a cada descoberta (tela diferente,
> erro, ajuste), atualize este arquivo e o "Diário do cliente #1" no fim dele.

---

## 1. Checklist do cliente (antes de começar)

| # | Item | Quem faz | Observações |
|---|---|---|---|
| 1 | Conta de **afiliado Shopee** aprovada | cliente | Pelo app Shopee > "Afiliados". Já aprovado se aparece "Sua Performance". |
| 2 | **Informações de pagamento** completas no painel de afiliado | cliente | Sem isso o botão "Aplicar" da Open API fica cinza (ver §2). |
| 3 | **Acesso à Open API** (App ID + Senha/Secret) | cliente pede, Shopee aprova | Pode levar dias. Começar por aqui. |
| 4 | **VPS** | cliente contrata (ou nós, no plano gerenciado) | Specs no §3. |
| 5 | **Chip só para o robô**, com WhatsApp | cliente | Nunca o número pessoal ou da empresa (risco de banimento). |
| 6 | **Grupo(s)** com o robô como admin e "só admins enviam" | cliente | Começar com um grupo de teste. |

Mensagem pronta para mandar ao cliente pelo WhatsApp: ver §6.

## 2. Shopee: como chegar na Open API (telas reais, nov/2026)

- O **app** da Shopee (área de afiliados) **não tem** a opção de API. Só o **site**.
- Caminho: navegador → `affiliate.shopee.com.br` → login → menu **Open API**
  (página "Página Inicial / Open API", seção **"Meu API"**).
  No celular, se não aparecer, ativar "Versão para computador".
- Tela de quem ainda não tem acesso:
  - `AppID: --` / `Senha: --` e botão **"Aplicar"** cinza.
  - Texto: "No momento você não possui acesso à Plataforma de Open API dos
    Afiliados Shopee. Por favor, entre em contato com a gente para pedir acesso".
  - Faixa vermelha no topo: "Por favor, complete suas **Informações de P**[agamento]".
- Hipótese (a confirmar no cliente #1): completar as informações de pagamento libera o
  botão "Aplicar". Se não liberar, pedir pelo link "entre em contato com a gente".
- Texto de justificativa sugerido:
  > Olá! Sou afiliado Shopee e gostaria de solicitar acesso à Open API de Afiliados.
  > Pretendo usar a API para buscar ofertas e gerar links de afiliado automaticamente,
  > que serão divulgados nos meus grupos de promoções no WhatsApp, divulgados pelo
  > Instagram. Obrigado!
- Na tela, o **Secret** se chama **"Senha"**. No `.env`: `SHOPEE_APP_ID` e `SHOPEE_SECRET`.
- Credenciais **nunca** pelo chat nem por WhatsApp: o Claude pede por formulário seguro
  (`request_credential`) ou o próprio cliente cola no `.env` da VPS.

### Detalhes técnicos da API (para o código)
- Endpoint Brasil: `https://open-api.affiliate.shopee.com.br/graphql`
- Header: `Authorization: SHA256 Credential=<AppId>, Timestamp=<ts>, Signature=<sig>`
  com `sig = sha256(AppId + Timestamp + corpoJSON + Secret)` em hex, ts em segundos.
  O corpo assinado tem de ser **exatamente** o texto enviado.
- Busca: `productOfferV2(keyword, sortType, page, limit)`. Link: mutation
  `generateShortLink(input: {originUrl, subIds})`.
- A confirmar na 1ª chamada real: nomes dos campos e se `priceDiscountRate` vem em % ou em fração.

## 3. VPS

- **Não precisa de placa de vídeo.** Roda: Evolution API + Postgres + robô (Python).
- Mínimo: 1 vCPU, 2 GB RAM, 20 GB. **Recomendado: 1–2 vCPU, 4 GB RAM, 40 GB+ NVMe.**
- Hostinger: **KVM 1** basta para um cliente. KVM 2 se for hospedar vários clientes.
- Sistema: **Ubuntu 24.04** sem painel (ou o modelo "Ubuntu + Docker"). Região: Brasil, se tiver.
- Hospedagem de site comum **não serve** (o robô precisa rodar 24h).

## 4. Conectores do Claude

- **Nenhum conector é necessário** para o robô funcionar: ele roda sozinho na VPS e
  fala direto com a Shopee (Open API) e com o WhatsApp (Evolution API).
- Não existe conector da Shopee. Úteis depois: **Hostinger** (gerenciar a VPS) e
  **Google Sheets** (fila manual de produtos e histórico).

## 5. Instalação (resumo; detalhes no README)

1. Docker na VPS → copiar a pasta `robo-promocoes/` → `cp .env.example .env` e preencher.
2. `docker compose up -d postgres evolution` → túnel SSH → `/manager` → criar a instância → ler o QR Code com o chip do robô.
3. `python -m robo grupos` → colocar os IDs em `GRUPOS`.
4. `python -m robo teste` → cliente aprova o formato.
5. `docker compose up -d robo` → teste num grupo só com o cliente → liberar nos grupos públicos.

## 6. Mensagem de pendências para o cliente (copiar e colar no WhatsApp)

```
*📋 PENDÊNCIAS – ROBÔ DE PROMOÇÕES (SHOPEE)*

*1️⃣ Acesso à API da Shopee* _(fazer primeiro, pode levar dias)_
☐ Entrar em affiliate.shopee.com.br (pelo navegador, não pelo app)
☐ Completar as *Informações de Pagamento* (faixa vermelha no topo)
☐ Abrir *Open API* e clicar em *Aplicar* (ou "entre em contato com a gente")
☐ Quando liberar, aparecerão o *AppID* e a *Senha*
⚠️ _Não mandar o AppID nem a Senha por mensagem para ninguém_

*2️⃣ Servidor (VPS)*
☐ Contratar uma VPS (ex.: Hostinger KVM 1, Ubuntu 24.04)
☐ Guardar o IP e a senha root em lugar seguro

*3️⃣ Chip do robô*
☐ Chip novo, só para o robô, com WhatsApp num celular reserva
☐ Usar o número normalmente por alguns dias antes de começar
⚠️ _Não usar o número pessoal nem o da empresa (risco de banimento)_

*4️⃣ Grupo de teste*
☐ Criar um grupo só com você e o número do robô
☐ Tornar o robô *admin* e marcar *só admins enviam mensagens*

*5️⃣ Com tudo pronto*
☐ Avisar para instalarmos, lermos o QR Code e fazermos o teste
```

## 7. Ideias para o produto (decidir depois)

- **Modelo de entrega:**
  (a) VPS do cliente, nós instalamos (cobrança de setup + mensalidade de suporte); ou
  (b) **plano gerenciado**: uma VPS nossa com vários clientes. A Evolution API aceita várias
  instâncias (um número por cliente) e cada cliente roda um container `robo` com o próprio `.env`.
  Uma KVM 2 deve aguentar vários clientes.
- **O que muda por cliente:** `.env` (chaves Shopee, instância, grupos, filtros, horários,
  palavras-chave, frases). O código é o mesmo.
- **A fazer para escalar:** script `novo-cliente.sh` que gera a pasta e o `.env` do cliente;
  painel ou planilha por cliente; comandos do dia a dia via skill do Claude.
- **Termos de uso para o cliente:** a Evolution API não é a API oficial do WhatsApp (risco de
  banimento, por conta do cliente); o cliente usa a **própria** conta de afiliado; preços
  sujeitos a alteração; LGPD dos membros dos grupos.

---

## Diário do cliente #1 (dono)

| Data | O que aconteceu |
|---|---|
| 23/11/2026 | Decidido começar **só pela Shopee**. Rascunho do robô pronto, com modo teste usando produtos de exemplo. |
| 24/11/2026 | Afiliado Shopee já aprovado (app mostra "Sua Performance"). Open API achada no site: sem acesso, botão "Aplicar" cinza, aviso para completar as Informações de Pagamento. |
| 24/11/2026 | Definida a VPS: Hostinger KVM 1, Ubuntu 24.04, sem placa de vídeo. Confirmado que nenhum conector do Claude é necessário. |
| — | **Próximo:** completar o pagamento → pedir a API → contratar a VPS → chip e grupo de teste. |
