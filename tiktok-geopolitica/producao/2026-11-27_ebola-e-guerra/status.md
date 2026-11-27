# Status — 2026-11-27_ebola-e-guerra (série 1 "Peça por Peça", guerra)
- [x] Pauta: sem pauta pendente em `pautas_do_dono.md`; radar do dia (notícias de 26/11): Ebola no Congo passa de 12 mil casos e combates atrapalham a resposta. Mecanismo: como se cerca um surto e onde a guerra quebra cada peça. Fora do histórico e dos temas de hoje (defesa antiaérea, rede elétrica).
- [x] Checagem (checagem.md) — APROVADA, 12 afirmações com 2 fontes (AP, Reuters, OMS, CDC); conformidade APROVADA
- [x] Roteiro cascata + narracao_tts.txt (214 palavras, 8 elos + parabéns + CTA GENERAL/RECRUTA)
- [x] Voz edge-tts pt-BR-AntonioNeural +12% (83,4 s) + palavras/legendas (3 tempos corrigidos à mão: "Esse" da cena 3, "sem", "Dois")
- [x] Cena Blender `motor/cena_ebola.py` (REALISTA=1). Modelos novos em lowpoly.py: `cabana`, `tenda_medica`, `agente_epi`. compor.py: `subst` com sequências de palavras (backlog TNP).
- [x] grafismos.json (capa "12 MIL CASOS / DE EBOLA / NO MEIO DA GUERRA", 7 rótulos, 18 pílulas, 5 fontes, CTA, trilha "tenso")
- [x] Render PASSO=2 (2.663 quadros → 1.332 renderizados, 2 processos, flock; 10:33→12:24 UTC, ~10 s/quadro por processo) → render.sh
- [x] compor.py (anti_borda automático) → final.mp4 (89,0 s; 1080x1920, 30 fps, −14,2 LUFS, pico −1,4 dBTP) + capa.jpg. QC APROVADO (qc_sheet.jpg): capa legível em 270 px, gancho com casos + explosões no front nos 3 primeiros s, legenda sincronizada (21, 25 km, 80% em bloco), rótulos sem sobrepor pílulas (corrigido: pílulas das cenas 2, 4 e 7 terminam no "Esse/Essa"), fontes na tela, selo de IA, CTA GENERAL/RECRUTA completo, "Deixa o like" no fim, sem tela preta
- [ ] Agendamento: NÃO feito nesta sessão (pedido) — sessão que chamou (Metricool/Kwai/historico)
