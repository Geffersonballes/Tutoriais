# Status — 2026-11-26_tnp-israel (série 1 "Peça por Peça", guerra) — RESPOSTA AO COMENTÁRIO
- [x] Pauta: nº 1 de `pautas_do_dono.md` ("Por que Israel não está no tratado nuclear?"); caçador de notícias pulado (pedido do dono). Balão "Israel não faz parte do TNP, por quê?" sem nome/foto/@.
- [x] Checagem (checagem.md) — APROVADA, 11 afirmações com 2 fontes (UNODA, AIEA, SIPRI, ACA); conformidade APROVADA (tom neutro, sem prever/incentivar ataque, sem bandeiras reais)
- [x] Roteiro cascata + narracao_tts.txt (199 palavras, 6 elos + parabéns + "manda nos comentários a próxima pergunta")
- [x] Voz edge-tts pt-BR-AntonioNeural +12% (84,5 s) + palavras/legendas (3 tempos corrigidos à mão: "Inspetores", "E" da cena 5, "Teerã")
- [x] Cena Blender `motor/cena_tnp.py` (REALISTA=1), reaproveitando centrífugas, usina, agência, van e inspetores do vídeo nuclear de 25/11. Modelos novos em lowpoly.py: `bandeira` (mastro + pano ondulado, sem país real) e `documento` (tratado no púlpito com selo). compor.py: novo `"comentario"` (balão de comentário) e CTA de 1 linha (t2a vazio).
- [x] grafismos.json (capa "ISRAEL FORA / DO TRATADO / NUCLEAR?", 6 rótulos, 19 pílulas, 7 fontes, CTA, trilha "curioso")
- [x] Render PASSO=2 (2.691 quadros → 1.346 renderizados, 2 processos, flock; 21:59→23:31 UTC, ~7,4 s/quadro, AMOSTRAS=4) → render.sh
- [x] compor.py → final.mp4 (89,9 s após cortar 0,2 s de silêncio final; 1080x1920, 30 fps, −14,0 LUFS) + capa.jpg. QC APROVADO (qc_sheet.jpg): capa legível em 270 px, balão do comentário 1,3–7,6 s, legenda sincronizada, rótulos/pílulas acima da legenda, fontes na tela, selo de IA, CTA "manda nos comentários a próxima pergunta" completo, "Deixa o like" no fim, sem tela preta
- [ ] Agendamento: NÃO feito nesta sessão (pedido do dono) — sessão que chamou (Metricool/Kwai/historico/pautas)
