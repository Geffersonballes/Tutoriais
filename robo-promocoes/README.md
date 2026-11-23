# Robô de Promoções (Shopee → WhatsApp)

Busca ofertas na Shopee Affiliate Open API, filtra (desconto, preço, nota, vendas),
gera o seu link curto de afiliado e posta foto + texto nos seus grupos de WhatsApp
pela Evolution API. Contexto e decisões: [PLANO.md](PLANO.md).

## Formato da mensagem

```
É melhor ter e não precisar, do que precisar e não ter! ❤️

🛍️ Monitor Digital de Pressão Arterial de Braço

de ~R$ 120,70~
💥 por *R$ 36,21*

🛍️ Compre aqui: https://s.shopee.com.br/XXXX

_Promoção sujeita a alteração de preço e estoque._
```

## Comandos

| Comando | O que faz |
|---|---|
| `python -m robo teste --exemplo` | Mostra mensagens com produtos de exemplo (sem chave nenhuma) |
| `python -m robo teste` | Busca de verdade na Shopee e **só imprime** (não envia nada) |
| `python -m robo grupos` | Lista os grupos do número do robô, com o ID de cada um |
| `python -m robo rodar` | Produção: posta em loop nos `GRUPOS`, das 8h às 23h |

## Instalação na VPS (Passo 5)

1. VPS Ubuntu com Docker: `curl -fsSL https://get.docker.com | sh`
2. Copie esta pasta para a VPS, depois `cp .env.example .env` e preencha.
3. `docker compose up -d postgres evolution`
4. No seu computador, abra um túnel: `ssh -L 8080:localhost:8080 usuario@IP_DA_VPS`
   e acesse `http://localhost:8080/manager` (senha = `EVOLUTION_API_KEY`).
   Crie a instância `robo` e leia o QR Code com o WhatsApp do **chip do robô**.
5. `docker compose run --rm robo python -m robo grupos` → copie os IDs `...@g.us` para `GRUPOS`.
6. `docker compose run --rm robo python -m robo teste` → confira as mensagens.
7. `docker compose up -d robo` e acompanhe com `docker compose logs -f robo`.

## Cuidados

- Evolution API não é a API oficial do WhatsApp: use um chip só para o robô,
  poste apenas nos seus grupos e mantenha os intervalos.
- O `.env` tem suas chaves e não vai para o Git.
