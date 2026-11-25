# Status — 2026-11-25_inspetores-nucleares (série 1, post 25/11/2026 18:00, só TikTok)
- [x] Pauta: "Como se vigia um programa nuclear" (gancho: Irã, China e Rússia na AIEA em 18/11; mecanismo: urânio → centrífugas → 3–5% → 90% → TNP/AIEA → selos, câmeras, poeira → impasse → satélite na Coreia do Norte)
- [x] Checagem (checagem.md) — aprovada, 2+ fontes por afirmação
- [x] Roteiro cascata + narracao_tts.txt (≈390 palavras, 11 cenas)
- [x] Voz edge-tts pt-BR-AntonioNeural +12% (146,7 s) + palavras/legendas (4 tempos corrigidos à mão nas viradas de cena 1 e 4)
- [x] Cena Blender `motor/cena_nuclear.py` (REALISTA=1) — modelos novos em lowpoly.py: centrífuga (com listra que mostra o giro), cilindro de UF6, usina nuclear (reator + torres de resfriamento), satélite; giro com extrapolação linear (2 chaves por objeto)
- [x] Backlog 10: explosões com emissão 1,2 e laranja mais escuro + bola de fogo
- [x] grafismos.json (capa "90% / SEPARA A USINA / DA BOMBA", 8 rótulos, 24 pílulas, 4 fontes, CTA, trilha "curioso")
- [x] Render completo PASSO=2 (4.563 quadros → 2.282 renderizados, 2 processos, sob flock /tmp/render.lock; 14:41→18:34 UTC, ~3h50 com a fila) → render.sh
- [x] compor.py → final.mp4 (2:32, 1080x1920, 30 fps, −14,1 LUFS) + QC APROVADO (capa "90% / SEPARA A USINA / DA BOMBA" legível, explosões no bunker em 1,3–2,3 s, selo de IA, fontes na tela, CTA completo, "Deixa o like" no fim, sem tela preta). Corrigido no QC: pílula da Coreia do Norte cortada na borda → texto menor
- [ ] Agendamento: sessão principal (Metricool, só TikTok, isAigc) — 18:00
Título sugerido: 90% separa uma usina de uma bomba: como se vigia um programa nuclear
Título curto (TikTok): Como se vigia uma bomba atômica?
