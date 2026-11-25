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
| 6 | **Nome do grupo e logo** (foto do grupo e do Instagram) | cliente | Cliente #1: "Achadinhos da Lay". |
| 7 | **Grupo(s)** com o robô como admin e "só admins enviam" | cliente | Começar com um grupo de teste. |

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
- **Confirmado no cliente #1:** depois de completar as Informações de Pagamento, o botão
  "Aplicar" fica clicável. Clicar, preencher e enviar o pedido. Depois é aguardar a aprovação.
  (Se não liberar, pedir pelo link "entre em contato com a gente".)
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
- Hostinger: **KVM 1** basta para um cliente. **KVM 2** para o plano gerenciado (vários clientes na mesma VPS).
- Preços vistos em 25/11/2026 (site em dólar, promoção de 24 meses): KVM 1 US$ 6,49/mês (1 vCPU, 4 GB,
  50 GB), renova a US$ 11,99; KVM 2 US$ 8,79/mês (2 vCPU, 8 GB, 100 GB), renova a US$ 14,99;
  KVM 4 US$ 12,99; KVM 8 US$ 25,99. Garantia de 30 dias. Dica: comprar pelo site em reais
  (hostinger.com.br) para evitar IOF e variação do dólar no cartão.
- Sistema: **Ubuntu 24.04** sem painel (ou o modelo "Ubuntu + Docker"). Região: Brasil, se tiver.
- Hospedagem de site comum **não serve** (o robô precisa rodar 24h).

### Depois de contratar
- Tela final da Hostinger: "Bom trabalho, você está pronto 🎉" com **Painel VPS** e o comando `ssh root@<IP>`.
- O Claude confere a VPS pelo **conector Hostinger** (plano, sistema, estado, IP), sem pedir senha.
- Para cliente leigo, usar o **Terminal do navegador** do painel da VPS na Hostinger (não precisa instalar SSH).
- Instalar o Docker: `curl -fsSL https://get.docker.com | sh` e conferir com `docker --version`
  (cliente #1: Docker 29.1.1, instalou sem erro pelo Terminal do navegador).
- Baixar o robô na VPS (o repositório é público, não precisa de senha):
  `cd /opt && git clone --depth 1 -b <branch> https://github.com/Geffersonballes/Tutoriais.git tutoriais`
  e trabalhar em `/opt/tutoriais/robo-promocoes` (o `.env` e `dados/` não vão para o Git, então `git pull` atualiza sem apagar nada).
- `ls` não mostra o `.env.example` (arquivos que começam com ponto ficam ocultos). Isso é normal.
- Criar o `.env` e gerar senhas aleatórias **na própria VPS** (ninguém precisa digitar nem ver a senha):
  `cp .env.example .env && sed -i "s|^EVOLUTION_API_KEY=.*|EVOLUTION_API_KEY=$(openssl rand -hex 24)|; s|^POSTGRES_PASSWORD=.*|POSTGRES_PASSWORD=$(openssl rand -hex 24)|" .env`
  e depois `docker compose up -d postgres evolution` e `docker compose ps`.
- Conectar o chip **sem túnel SSH**: `git pull && bash conectar-whatsapp.sh` mostra o QR Code no próprio
  Terminal do navegador (se o QR sair deformado: `bash conectar-whatsapp.sh 55DDNUMERO` dá um código de 8 letras).
- Visto no cliente #1 (v2.3.7): o **QR Code funciona** (aparece também em `docker compose logs -f --tail 0 evolution`),
  mas o código de 8 letras veio `null` quando a instância tinha sido criada sem número. O script agora recria a
  instância com o número nesse modo. **Preferir o QR Code.** Não mandar print de QR para ninguém.
- Definir o grupo: `sed -i 's|^GRUPOS=.*|GRUPOS=<id>@g.us|' .env` e conferir com `grep ^GRUPOS= .env`.
  O robô **só** posta nos IDs de `GRUPOS`; os outros grupos do número são ignorados.
- Testar o envio antes da Shopee aprovar: `docker compose run --rm robo python -m robo enviar-teste`
  (manda 1 mensagem marcada como TESTE, com produto de exemplo).
- Evolution API: imagem `evoapicloud/evolution-api:v2.3.7` (conferida no Docker Hub em 25/11/2026).
- ⚠️ Produto: o repositório hoje é **público**. Antes de vender, mover o código do robô para um repositório **privado**
  e usar uma deploy key só de leitura na VPS de cada cliente.

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

## 7. Agentes de apoio (`.claude/agents/promo-*.md`)

| Agente | Para quê |
|---|---|
| `promo-coordenador` | Diz em que passo estamos e chama os outros |
| `promo-desenvolvedor` | Código do robô |
| `promo-instalador-vps` | VPS, Docker, Evolution API, QR Code, logs |
| `promo-curador-de-ofertas` | Filtros, nichos, palavras-chave, ritmo |
| `promo-redator` | Frases de efeito, boas-vindas, regras do grupo |
| `promo-divulgacao-instagram` | Stories, reels, anúncios para encher os grupos |
| `promo-conformidade` | Riscos (afiliados, WhatsApp, CDC, LGPD, Meta); tem veto |
| `promo-onboarding-cliente` | Coloca cada cliente novo no ar (`clientes/<apelido>/status.md`) |
| `promo-documentador` | Mantém este manual e o diário atualizados |

## 8. Ideias para o produto (decidir depois)

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
| 25/11/2026 | Informações de Pagamento completadas → botão "Aplicar" liberou → **pedido de acesso à Open API enviado**. Aguardando a Shopee. |
| 25/11/2026 | **VPS contratada:** Hostinger KVM 2 (2 vCPU, 8 GB, 100 GB), Ubuntu 24.04 LTS, estado "running". Conferida pelo conector Hostinger (`vps_virtual-machines_list`), sem precisar de senha. Firewall da Hostinger ainda não configurado. |
| 25/11/2026 | Docker 29.1.1 instalado na VPS. |
| 25/11/2026 | Robô baixado na VPS em `/opt/tutoriais/robo-promocoes` (git clone sem erro). |
| 25/11/2026 | **Marca:** grupo "Achadinhos da Lay"; logo já pronta. **Chip do robô pronto** com WhatsApp. |
| 25/11/2026 | `postgres` e `evolution` subiram (Up) na primeira tentativa. Criado `conectar-whatsapp.sh`. |
| 25/11/2026 | ✅ **Chip do robô conectado** à Evolution API pelo QR Code (o código de 8 letras veio vazio; ver §3). |
| 25/11/2026 | Lista de grupos OK. Grupo **Achadinhos da Lay** = `120363432803335927@g.us`. ⚠️ O número do robô **não é um chip novo**: está em vários outros grupos (família, escola, outros grupos de ofertas). Recomendado para os próximos clientes: chip exclusivo. |
| 25/11/2026 | ✅ `enviar-teste` rodou sem erro ("Teste enviado para ...@g.us"). O horário do log sai no fuso de Cuiabá (`FUSO`). |
| 25/11/2026 | Criados 9 agentes de apoio `promo-*` (ver §7). |
| — | **Próximo:** enquanto a Shopee analisa: contratar a VPS → chip e grupo de teste. Anotar quantos dias a aprovação levou. |
