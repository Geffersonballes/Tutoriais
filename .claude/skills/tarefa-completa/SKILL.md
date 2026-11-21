---
name: tarefa-completa
description: 'Fluxo de qualidade para qualquer tarefa complexa ou de várias etapas que não seja só uma landing page: sistema ou automação de vendas, site com várias páginas, fluxo de WhatsApp/CRM, relatório, conteúdo em lote, refatoração, pesquisa com entrega. Planeja, divide em subagentes quando compensa, faz um crítico independente revisar, corrige e entrega com verificação. Use quando o usuário disser "tarefa completa", "faz isso direito", "com revisão", "é grande/complexo", ou quando o pedido tiver várias partes e risco de erro. Para landing page use landing-completa-balles-tech, landing-completa-professores ou landing-completa-nova.'
---

# Tarefa completa

Padrão: **planejar → executar → criticar (agente independente) → corrigir → entregar verificado.** Quem fez tende a defender o próprio trabalho; um agente com contexto limpo acha mais problemas. Argumento (`$ARGUMENTS`): a tarefa.

## Quando NÃO usar o fluxo inteiro

Tarefa pequena (trocar um texto, uma pergunta, um ajuste de uma linha): faça direto. Subagentes custam tokens; só valem quando há risco de erro ou partes independentes.

## 1. Planejar (você, sem subagente)

Escreva em poucas linhas: **objetivo**, **critérios de pronto** (verificáveis: "teste X passa", "página abre em 375px sem rolar para o lado"), **partes** e quais são independentes. Pergunte ao usuário só o que muda o rumo e não tem padrão razoável; o resto, decida e avise. Dado que falta nunca é inventado: fica marcado `[PREENCHER]` ou vira pergunta.

## 2. Executar

- Partes **dependentes** ou pequenas: faça você mesmo, em sequência.
- Partes **independentes** e grandes (ex.: 5 variações, pesquisar vários concorrentes, vários arquivos sem relação): um subagente por parte, em paralelo, cada um com prompt completo e autossuficiente (objetivo, arquivos, regras, formato da resposta). Pesquisa e busca: `Explore`/`general-purpose`.
- Use as skills que já existem para o assunto (landing, copy, follow-ups de vendas solares, planilhas, documentos…) em vez de reinventar.

## 3. Criticar (subagente independente, somente leitura)

Dispare **um** subagente que não participou da execução:

> Você é revisor independente. NÃO edite nada. Objetivo: `<objetivo>`. Critérios de pronto: `<lista>`. Examine `<arquivos/saída>`. Procure: erro de fato ou invenção (dado sem fonte), critério não cumprido, caso de borda, regressão, algo irreversível ou que mexe fora do escopo, risco de segurança ou de privacidade. **Rode** testes/verificações quando existirem e reporte o resultado literal; para algo visual, abra e olhe os prints. Devolva `GRAVE | MÉDIO | LEVE`, onde, evidência, correção sugerida. Máx. 15 itens.

Se a tarefa tem duas frentes distintas (ex.: conteúdo e técnica), dispare dois críticos em paralelo.

## 4. Corrigir

Aplique GRAVE e MÉDIO e os LEVE baratos; anote o motivo de cada recusado. Rode de novo as verificações. Se sobrou GRAVE, **uma** segunda rodada de crítica; depois pare e entregue listando os pontos abertos (máx. 2 rodadas, para não gastar tokens em círculo).

## 5. Entregar

Resposta em português simples, sem jargão: o que foi feito, o que o crítico achou e o que mudou por causa disso, **como foi verificado** (comando/resultado/prints) e o que ficou aberto ou depende do usuário. Diga com franqueza o que não foi testado. Entregáveis em arquivo na pasta de trabalho; commit e push só na branch de desenvolvimento.

## Regras de autonomia (as do dono)

- **Reversível → faça direto:** editar, criar, testar, commit/push em branch, gerar prévia.
- **Irreversível ou externo → explique e espere um "sim":** apagar arquivos, site, e-mails ou branches; force-push; mexer em DNS de e-mail; publicar em produção; enviar mensagem ou e-mail a cliente; **qualquer compra ou pagamento**.
- Dados de clientes/leads são privados: não vão para serviços externos nem para o repositório.
