# Robô de Promoções no WhatsApp: plano e contexto

Documento de passagem entre sessões do Claude Code. A nova sessão deve ler
este arquivo primeiro e seguir os passos com o usuário, um de cada vez.

## O que o usuário quer

> **Isto vai virar um produto vendido.** Tudo o que for aprendido na montagem do cliente #1
> fica registrado em [MANUAL-DE-REPLICACAO.md](MANUAL-DE-REPLICACAO.md), incluindo o diário
> e o status atual. Leia esse arquivo também e atualize-o a cada passo.

Replicar o modelo dos grupos de "achadinhos" (ex.: "PROMOS DA BECO #37"):

1. Anúncio ou story no Instagram com o link de entrada no grupo de WhatsApp.
2. Grupos em que só os admins postam. Quando um enche (~1.024 pessoas), abre-se outro.
3. **Um robô que encontra promoções sozinho** (Shopee, Amazon, Mercado Livre),
   gera o link de afiliado do usuário e posta foto + texto nos grupos o tempo todo.
4. Opcional: uma planilha com produtos escolhidos à mão, que o robô também posta.

Formato da mensagem (do print de referência):

```
É melhor ter e não precisar, do que precisar e não ter! ❤️🩺

🛍️ Monitor digital de pressão arterial de braço ...

de ~R$ 120,91~
💥 por *R$ 36,21*

🛍️ Compre aqui: https://shopee.promo/s/XXXX
```

## Decisão: script, não skill

- **Script/serviço (é o que vamos fazer).** O robô precisa rodar 24h sozinho, num
  servidor, sem ninguém abrir o Claude. Isso é um programa rodando em loop.
- **Skill (opcional, depois).** Uma skill só roda quando o usuário chama o Claude.
  Pode servir mais tarde para tarefas pontuais, por exemplo "adicione este produto à fila",
  "mude o desconto mínimo para 50%" ou "me mostre o que mais teve clique na semana".

## Arquitetura

```
[VPS 24h]
  ├─ Evolution API (Docker): conecta o número do robô via QR Code e envia para os grupos
  ├─ robo-ofertas (Node.js ou Python), a cada 10–20 min:
  │    1. busca ofertas (começar só pela Shopee Affiliate Open API)
  │    2. filtra: desconto mínimo, faixa de preço, categoria, nota, vendas
  │    3. descarta repetidos (histórico em SQLite)
  │    4. gera link curto de afiliado + frase de efeito (IA opcional)
  │    5. envia imagem + legenda para cada grupo configurado
  │    6. registra no Google Sheets (histórico / fila manual)
  └─ agendamento: só posta entre 8h e 23h, com intervalo entre posts
```

## Passo a passo (fazer um de cada vez com o usuário)

1. **Pré-requisitos** (o usuário levanta):
   - Conta aprovada no programa de afiliados da Shopee + App ID e Secret da Open API
     (pedir pela ferramenta `request_credential`, nunca colar no chat).
   - VPS (Hostinger VPS ou outra; hospedagem de site comum não serve).
   - Chip/número separado só para o robô, com WhatsApp instalado.
   - Grupo(s) criados pelo usuário, com o número do robô como admin.
2. **Confirmar a documentação atual** da Shopee Affiliate Open API (endpoint
   GraphQL, assinatura, consultas de ofertas e geração de link curto) antes de codar.
3. **Escrever o robô** nesta pasta (`robo-promocoes/`): código, `.env.example`,
   `docker-compose.yml` (Evolution API + robô) e README de instalação.
4. **Modo teste:** rodar sem enviar nada (só imprime as mensagens) e o usuário aprova o formato.
5. **Subir na VPS:** instalar o Docker, subir o compose e ler o QR Code com o chip do robô.
6. **Teste real** num grupo só com o usuário. Depois liberar para os grupos públicos.
7. **Depois:** Amazon e Mercado Livre, frase por IA, planilha de fila manual,
   e uma skill para comandos do dia a dia.

## Cuidados

- Evolution API/Baileys não é a API oficial do WhatsApp: há risco de banimento. Usar um chip
  separado, intervalos entre posts, horário comercial e postar só nos grupos do usuário.
- Preço e estoque mudam: checar a oferta na hora de postar e manter o aviso
  "Promoção sujeita a alteração".
- Nunca commitar chaves (`.env` fica no `.gitignore`).
