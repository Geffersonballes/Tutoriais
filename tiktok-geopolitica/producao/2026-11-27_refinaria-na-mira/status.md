# Status — 2026-11-27_refinaria-na-mira (série 1 "Peça por Peça", guerra)
- [x] Pauta: sem pauta pendente em `pautas_do_dono.md`; radar (notícias de 26–27/11): projétil atinge a refinaria da Aramco em Jazan (Arábia Saudita), incêndio, 1 morto, parada parcial; coalizão culpa os houthis. Mecanismo: o caminho do petróleo e por que a refinaria é o ponto fraco. Fora do histórico e do tema de hoje cedo (Ebola).
- [x] Checagem (checagem.md) — APROVADA, 11 afirmações com 2 fontes (Arab News, Bloomberg/Rigzone, Gulf News, Khaleej Times, EIA, CRS, Enerdata); conformidade APROVADA
- [x] Roteiro cascata + narracao_tts.txt (207 palavras, 7 elos + parabéns + CTA GENERAL/RECRUTA)
- [x] Voz edge-tts pt-BR-AntonioNeural +12% (84,0 s) + palavras/legendas
- [x] Cena Blender `motor/cena_refinaria.py` (REALISTA=1). Modelos novos em lowpoly.py: `torre_destilacao`, `tanque_armazenamento`, `cavalo_de_pau`, `caminhao_tanque`, `coluna_fumaca` (backlog Ebola: fumaça menos "contas"). Mar com ondas (`mar_ondulado`).
- [x] grafismos.json (capa "400 MIL BARRIS / POR DIA / NA MIRA", 7 rótulos, 21 pílulas, 4 fontes, CTA, trilha "tenso")
- [x] Render PASSO=2 (2.682 quadros → 1.341 renderizados, 2 processos, flock; 18:30→19:52 UTC, ~7 s/quadro por processo) → render.sh
- [x] compor.py → final.mp4 (89,6 s; 1080x1920, 30 fps, −14,2 LUFS, pico −1,5 dBTP) + capa.jpg. QC APROVADO (qc_sheet.jpg): capa legível em 270 px, gancho com impacto/explosão na refinaria nos 3 primeiros s, legenda sincronizada (400 mil, 2019, 5,7), rótulos e pílulas sem tapar o objeto, fontes na tela, selo de IA, CTA GENERAL/RECRUTA completo, "Deixa o like" no fim, sem tela preta
- [ ] Agendamento/Kwai/histórico: NÃO feito nesta sessão (pedido) — fica com a sessão que chamou
