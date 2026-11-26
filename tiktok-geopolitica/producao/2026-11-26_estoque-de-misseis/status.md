# Status — 2026-11-26_estoque-de-misseis (série 1 "Peça por Peça", guerra)
- [x] Pauta: "Por que os mísseis acabam?" — gancho: Patriots já pagos parados em Washington (FT 24/11; Kyiv Post/VOA 25–26/11) + 850 Tomahawks em 1 mês na guerra com o Irã; mecanismo: estoque → linha de produção → buraco → prazo de validade → fila → guerra das fábricas. Não repete temas do historico.md.
- [x] Checagem (checagem.md) — aprovada, 2 fontes por afirmação; revisão de conformidade aprovada
- [x] Roteiro cascata + narracao_tts.txt (222 palavras, 7 elos + parabéns + CTA)
- [x] Voz edge-tts pt-BR-AntonioNeural +12% (84,8 s) + palavras/legendas (1 tempo corrigido à mão: "Se" do CTA)
- [x] Cena Blender `motor/cena_misseis.py` (REALISTA=1) — modelos novos em lowpoly.py: Tomahawk detalhado (asas, aletas em X, faixa, bocal), contêiner de míssil, lançador tipo Patriot (4 tubos, estabilizadores)
- [x] grafismos.json (capa "850 MÍSSEIS / EM UM MÊS. / POR QUE ACABAM?", 6 rótulos, 18 pílulas, 6 fontes, CTA, trilha "tenso")
- [x] Render PASSO=2 (2.708 quadros → 1.354 renderizados, 2 processos, flock; 10:31→11:41 UTC) → render.sh
- [x] compor.py → final.mp4 (1:30, 1080x1920, 30 fps, −14,3 LUFS) + capa.jpg. QC APROVADO: capa legível em 270 px, lançamentos de Tomahawk no 1º segundo, legenda sincronizada, selo de IA, fontes na tela, CTA completo, "Deixa o like" no fim, sem tela preta (qc_sheet.jpg)
- [ ] Agendamento: sessão que chamou (Metricool/Kwai/historico)
Título curto: Por que os mísseis acabam?
