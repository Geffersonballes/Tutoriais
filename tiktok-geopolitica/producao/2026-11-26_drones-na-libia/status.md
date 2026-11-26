# Status — 2026-11-26_drones-na-libia (série 1 "Peça por Peça", guerra)
- [x] Pauta: "Como a guerra da Ucrânia chegou à África?" — gancho: drones navais ucranianos atingem a corveta russa Merkury em Benghazi (22/11) + reações de 24–26/11 (LNA promete retaliar, Itália critica, Kiev defende). Mecanismo: drone naval → porto amigo → alcance → efeito colateral → diplomacia → novo front.
- [x] Checagem (checagem.md) — aprovada, 2 fontes; conformidade aprovada
- [x] Roteiro + narracao_tts.txt (223 palavras, 9 parágrafos: gancho, 6 elos, parabéns, CTA)
- [x] Voz edge-tts pt-BR-AntonioNeural +12% (84,2 s) + palavras/legendas (1 tempo corrigido à mão: "Se" do CTA 77,90→78,76)
- [x] Cena Blender `motor/cena_libia.py` (REALISTA=1), palcos PORTO (Benghazi em miniatura) e MAPA (Mediterrâneo + Mar Negro). Modelos novos em lowpoly.py: `drone_naval()` (casco em cunha, antena, câmera, jato), `corveta()` (proa em cunha, 3 níveis, células de mísseis, radar, convoo) e `mar_ondulado()` (backlog 4/32: mar com ondas animadas)
- [x] grafismos.json (capa "7 DRONES. / UM NAVIO RUSSO. / NA ÁFRICA?", 6 rótulos, 21 pílulas, 6 fontes, CTA ALMIRANTE/MARUJO, trilha "tenso")
- [x] Render PASSO=2 (2.692 quadros → 1.346 renderizados, 2 processos, flock; 18:34→19:51 UTC) → render.sh
- [x] compor.py → final.mp4 (1:29,9, 1080x1920, 30 fps, −14,2 LUFS) + capa.jpg. QC APROVADO: capa legível em 270 px, drones atingindo a corveta com explosão aos 1–3 s, legenda sincronizada a 63 %, selo de IA, fontes na tela, CTA ALMIRANTE/MARUJO completo, "Deixa o like" no fim, sem tela preta (qc_sheet.jpg)
- [ ] Agendamento: sessão que chamou (Metricool/Kwai/historico)
Título curto: Como a guerra da Ucrânia chegou à África?
