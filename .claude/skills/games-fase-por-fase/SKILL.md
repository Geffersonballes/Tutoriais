---
name: games-fase-por-fase
description: Rotina da série 2 "Fase por Fase" no TikTok geffersonballes1 + YouTube Shorts — vídeos 3D de 60 a 80 s sobre games (e outro assunto só se estiver mais quente), escolhidos pelo que está com mais engajamento. Use para produzir e agendar um vídeo da série 2 ou quando o usuário pedir um vídeo de games/tendência.
---
# Série 2 — Fase por Fase

Mesmo pipeline da skill `tiktok-peca-por-peca` (leia-a: máquina, narração, Blender, composição, QC,
Picsart, Metricool), com estas diferenças. Configuração em `serie-games/config.md`.

## 1. Pauta — `cacador-de-tendencias`
Rode o agente (ele dispara `tendencias-games`, `tendencias-plataformas` e `analista-de-desempenho`).
Escolha a pauta de maior nota que ainda não está em `serie-games/historico.md`. Prefira ângulos de
mecanismo: custo, tecnologia, economia, bastidores, recordes ("Por que GTA 6 custou tanto?",
"Como um jogo chega a 99 de nota?"). Evite spoiler de história (se inevitável, aviso na capa).

## 2. Checagem e roteiro
`verificador-de-fatos` ⛔ (2 fontes por número; o que for de fonte única vira "segundo X" ou sai),
`roteirista` com 6–8 blocos, 150–200 palavras (60–80 s), `critico-de-retencao`, `revisor-de-portugues`,
`revisor-de-conformidade` ⛔ com as regras de games: sem arte/personagem/logotipo de jogo, sem gameplay,
sem incentivo a pirataria ou builds vazadas, sem apostas/loot box como promoção.

## 3–6. Narração, cena, composição, QC
Igual à série 1, pasta `serie-games/producao/AAAA-MM-DD_slug/`. Cena em
`tiktok-geopolitica/motor/cena_<slug>.py` usando `lowpoly.py` (cidade, carros, prédios, moedas, setas,
servidores, consoles genéricos sem marca). `REALISTA=1 PASSO=2`, 2 processos.
`grafismos.json` sempre com `"capa"` (título grande nos 1,3 s iniciais) e CTA do config.

## 7. Publicação
UM post no Metricool (blogId 8049742, America/Cuiaba), providers tiktok + youtube, horário do config
(15:30 ou 21:30; se já passou, o próximo livre com ≥ 2 h de distância de qualquer post da série 1),
autoPublish true, `tiktokData.isAigc` true, `youtubeData {type short, category GAMING, madeForKids false,
isAiGeneratedContent true, title "<título> #shorts"}`. Registre em `serie-games/historico.md`,
commit e push. Avise em português: tema, horário, link do Metricool e pendências.
