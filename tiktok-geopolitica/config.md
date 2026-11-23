# Configuração da série

| Item | Valor | Status |
|---|---|---|
| Nome da série | Peça por Peça (provisório) | definir |
| TikTok para publicar | Metricool, marca `ballestech` (blogId 8049742), TikTok pessoal `geffersonballes1` | ✅ conectado |
| TikTok para métricas | Windsor `tiktok_organic`, conta "Gefferson Balles" | conectado (só leitura) |
| Fuso | America/Cuiaba | ok |
| Voz (ElevenLabs) | Fernando Will Narração & Storytelling — `SWnJtSNPFBZm03EETsy1`, modelo `eleven_multilingual_v2` | ✅ |
| Visual | Estilo B: ilustrações 3D realistas em miniatura (ElevenLabs gpt-image-2.5-sunburst, 9:16 2K, referência `assets/estilo/referencia_B.png`) animadas por `motor/ilustrado.py` | ✅ aprovado |
| Plano B visual | Blender 4.2 LTS low-poly (`motor/lowpoly.py`) | reserva |
| Custo por vídeo | ~16 imagens × 518 + voz ~2.200 ≈ 10.500 créditos ElevenLabs (≈ US$ 1,05) | estimativa |
| Fonte | Montserrat (OFL), em `assets/fonts/` | ✅ |
| CTA padrão | GENERAL / RECRUTA | ok |
| Frequência | 3 vídeos/dia — produções automáticas às 07:45, 14:20 e 17:50 (Cuiabá) | ✅ aprovado |
| Publicação | Metricool `createScheduledPost` com `autoPublish: false`: o dono confirma cada post no app do Metricool | ✅ aprovado |
