# Status — 2026-11-28_moldavia-drones (série 1 "Peça por Peça", guerra)
- [x] Pauta: sem pauta pendente em `pautas_do_dono.md`; radar (notícias de 17–27/11): sete drones no espaço aéreo da Moldávia em 17/11, um sobre Chișinău, cinco caídos, espaço aéreo fechado; Sandu volta ao tema na Assembleia Parlamentar da OTAN (23/11). Mecanismo: como a guerra transborda para um vizinho neutro. Fora do histórico (Ebola, refinaria de Jazan etc.).
- [x] Checagem (checagem.md) — APROVADA, 11 afirmações com 2 fontes (Reuters, IBTimes, Euronews, Radio Moldova, Constituição/Tribunal Constitucional, Carnegie); conformidade APROVADA
- [x] Roteiro cascata + narracao_tts.txt (222 palavras, 7 elos + parabéns + CTA GENERAL/RECRUTA)
- [x] Voz edge-tts pt-BR-AntonioNeural +12% (84,2 s) + palavras/legendas
- [x] Cena Blender `motor/cena_moldavia.py` (REALISTA=1). Modelos novos em lowpoly.py: `drone_delta` (asa delta com derivas e hélice girando), `casa_vila` (telhado de duas águas, porta, janelas), `prisma_ll` + `texto3d` (mapa com contornos reais e nomes 3D — backlog do mapa abstrato da Líbia)
- [x] grafismos.json (capa "7 DRONES / NUM PAÍS / FORA DA GUERRA", 7 rótulos, 21 pílulas, 4 fontes, CTA, trilha "tenso")
- [x] Render PASSO=2 (2.690 quadros → 1.345 renderizados, 2 processos, flock; 10:31→11:30 UTC) → render.sh
- [x] compor.py → final.mp4 (89,9 s; 1080x1920, 30 fps, −14,1 LUFS, pico −1,5 dBTP) + capa.jpg. QC APROVADO (qc_sheet.jpg): capa legível em 270 px, gancho com enxame de 7 drones sobre a cidade nos 3 primeiros s, legenda sincronizada (1994, 17), rótulos/pílulas sem tapar o objeto, fontes na tela, selo de IA, CTA GENERAL/RECRUTA completo, "Deixa o like" no fim, sem tela preta. Defeitos menores anotados no backlog
- [ ] Agendamento/Kwai/histórico: NÃO feito nesta sessão (pedido) — fica com a sessão que chamou
