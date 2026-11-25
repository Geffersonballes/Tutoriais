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

## Estilo visual C — cartoon 3D com o mascote Pixel (desde 23/11)
- Use `tiktok-geopolitica/motor/cartoon.py`: `pixel()` (mascote ORIGINAL: moletom laranja, fone verde-limão,
  cabelo escuro; gestos `acenar`, `apontar`, `comemorar`, `pensar`, `espanto`, `respirar`) e `modo_cartoon()`
  no lugar de `modo_realista()` (céu em degradê, cores vivas, quinas arredondadas, sem desfoque).
  Exemplo mínimo: `motor/exemplo_cartoon.py`; referência: `assets/estilo/referencia_C_pixel.jpg`.
- Linguagem de câmera do formato "Como funciona": o Pixel em primeiro plano reage/explica em cada bloco
  (gesto no verbo principal), cenas FECHADAS (quarto gamer, servidor, estádio, mapa em miniatura) e cortes a
  cada bloco. Mostre o mecanismo em objetos simples e coloridos.
- `samples=8`, 540×960, PASSO=2, 2 processos (~7 s/quadro).
- Proibido copiar personagem, nome ou cenário de outros canais (ex.: o canal de referência tem um mascote
  próprio de camiseta amarela e boné — o Pixel NÃO pode se parecer com ele) e de jogos.

## Pautas: todos os jogos
Não só GTA: CS2, PUBG, Free Fire, Valorant, LoL, Minecraft, Roblox, Fortnite, EA FC, consoles, PC gamer.
Formato que mais rende no nicho: "Como ___ funciona?" (ex.: "Como o servidor sabe que seu tiro acertou?",
"Como a zona do battle royale decide onde fechar?", "Como o anti-cheat pega trapaceiro?", "Por que dá lag?",
"Como o matchmaking escolhe seu time?"). Notícia quente (lançamento, recorde) entra quando o radar der nota alta.

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

**Hashtags:** siga `tiktok-geopolitica/hashtags.md` (6 de alcance #fyp #foryou #paravoce #viral #tiktokbrasil #shorts + #games #gamer #gamesnotiktok #curiosidades + tema + #aprendanotiktok).

**Melhoria contínua (todo vídeo):** antes de montar a cena, pegue 1 item "aberto" de `melhorias/backlog.md`
que caiba no vídeo e implemente; no QC, anote no backlog todo defeito que não deu para corrigir agora.

**Capa no YouTube (canal verificado em 23/11):** no `createScheduledPost`, envie `"videoCoverMilliseconds": 600` no info (quadro com o título grande da capa). O TikTok pessoal ignora esse campo e usa o 1º quadro, que já é a capa.

## Pedido de like (obrigatório, decisão do dono 24/11)
O compor.py acrescenta sozinho, depois da narração, a fala "Gostou do conteúdo? Então deixa o seu like!" (Antonio) e a tela GOSTOU DO CONTEÚDO? / DEIXA O LIKE. Não desligue. No QC, confira que aparece no fim.

## Áudio (obrigatório desde 24/11)
O compor.py gera voz tratada + trilha original + efeitos (motor/audio.py). Escolha o clima no grafismos.json ("trilha": {"clima": "curioso|tenso|epico|divertido"}) conforme a emoção do tema. Todo aprendizado novo vai para produto/MANUAL_DA_AUTOMACAO.md.

## VOZ (decisão do dono, 25/11) — substitui qualquer regra antiga de "nunca ElevenLabs" nesta série
A narração dos vídeos de GAMES é a **voz clonada do dono** no ElevenLabs (plano Creator, pago pelo dono).
1. `mcp__ElevenLabs__creative_generate_speech` (carregar via ToolSearch): `model_id` "eleven_v4", `voice_id` "Dt3IFiwrxXdZMMFz4Ai0", `generations_count` 1. Nunca repita a chamada para "tentar de novo" (cada uma cobra).
2. Prompt = narracao_tts.txt com etiquetas de emoção em inglês entre colchetes, com moderação: [surprised] no gancho, [curious] nas perguntas, [excited] nas revelações, [dramatically] no ponto alto, [mischievously] em viradas. Números por extenso como no roteiro.
3. `creative_get_flow_run_status` até all_completed → `curl` do content_url → narracao.mp3 → palavras.py + alinhar.py.
4. O "Gostou do conteúdo? Deixa o seu like!" já está gravado na voz do dono em produto/vozes/curtir_gefferson.mp3 e o compor.py usa sozinho. Não gere com edge-tts.
5. Orçamento: ~1.200 créditos por vídeo de games; o plano tem ~124 mil/mês (cabem os 3 vídeos/dia). Se a conta acusar falta de crédito, use Antonio (edge-tts) e avise o dono.

**MARCA E REDES (decisão do dono, 25/11 — vale acima do que estiver escrito antes):** agende na marca nova do Metricool `geffersonballes1`, **blogId `8356514`** (fuso America/Cuiaba). Não use mais a `ballestech` (8049742) — ela tem o mesmo TikTok e YouTube, e agendar nas duas duplicaria o post. Todo vídeo vai também para o **Facebook como Reel** (página Peça por Peça): acrescente `{"network":"facebook"}` em `providers` e `"facebookData": {"type": "REEL", "title": "<título curto>"}`. Guerra = TikTok + Facebook; games = TikTok + YouTube + Facebook.

## VISUAL NÍVEL 2 (decisão do dono, 25/11)
O `modo_cartoon()` do cartoon.py já aplica sozinho o "nível 2": luz de contorno por trás, brilho suave + cor mais viva no compositor, contorno escuro de desenho em tudo (casca invertida com emissão pura e sem sombra) e fundo levemente desfocado no alvo da câmera. Custo: ~1,5× o tempo de render (≈30 s por quadro em vez de ≈20 s; um vídeo de 60 s leva ~3 h). Não desligue. `VISUAL=0` volta ao visual antigo só para depuração. Objetos criados DEPOIS de `modo_cartoon()` ficam sem contorno — chame-o no fim da cena, como hoje.

## KWAI (25/11)
Depois de agendar no Metricool, acrescente o vídeo à lista do Kwai no OneDrive, seguindo kwai/LEIA.md.
