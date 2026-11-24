# Configuração da série

| Item | Valor | Status |
|---|---|---|
| Nome da série | Peça por Peça (provisório) | definir |
| TikTok para publicar | Metricool, marca `ballestech` (blogId 8049742), TikTok pessoal `geffersonballes1` | ✅ conectado |
| YouTube Shorts | ❌ desde 24/11 — a série de guerra sai só no TikTok; o YouTube do canal ficou só para games (decisão do dono, 23/11) | ✅ decidido |
| Horários dos posts | 10:00 (produção da manhã), 18:00 (da tarde), 13:00 do dia seguinte (da noite) | ✅ aprovado |
| TikTok para métricas | Windsor `tiktok_organic`, conta "Gefferson Balles" | conectado (só leitura) |
| Fuso | America/Cuiaba | ok |
| Voz | **pt-BR-AntonioNeural** (Microsoft, via edge-tts, gratuita), `--rate=+12%` | ✅ escolhida pelo dono |
| ElevenLabs | Plano gratuito — **não usar** na rotina (decisão do dono) | — |
| Visual | Estilo B: ilustrações 3D realistas em miniatura (ElevenLabs gpt-image-2.5-sunburst, 9:16 2K, referência `assets/estilo/referencia_B.png`) animadas por `motor/ilustrado.py` | ✅ aprovado |
| Plano B visual | Blender 4.2 LTS low-poly (`motor/lowpoly.py`) | reserva |
| Custo por vídeo | ~16 imagens × 518 + voz ~2.200 ≈ 10.500 créditos ElevenLabs (≈ US$ 1,05) | estimativa |
| Fonte | Montserrat (OFL), em `assets/fonts/` | ✅ |
| CTA padrão | GENERAL / RECRUTA | ok |
| Frequência | 2 vídeos/dia (desde 24/11; a série 2 de games ficou com 3) — produções às 06:20 (post 10:00) e 14:20 (post 18:00) | ✅ aprovado |
| Publicação | Metricool `createScheduledPost` com **`autoPublish: true`** — publicação 100 % automática no TikTok e no YouTube, autorizada pelo dono em 23/11/2026 | ✅ aprovado |
