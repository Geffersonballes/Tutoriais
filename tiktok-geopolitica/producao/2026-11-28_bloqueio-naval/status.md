# Status — 2026-11-28_bloqueio-naval (série 1 "Peça por Peça", guerra)
- [x] Pauta: sem pauta pendente; notícia de 26–28/11 (Pacific Archer atingido ao furar o bloqueio dos EUA aos portos do Irã; 158 desviados, 6 inutilizados). Mecanismo: como funciona um bloqueio naval.
- [x] Checagem (checagem.md) — APROVADA, 11 afirmações com 2 fontes; conformidade APROVADA
- [x] Roteiro cascata + narracao_tts.txt (209 palavras, 7 elos + parabéns + CTA GENERAL/RECRUTA)
- [x] Voz edge-tts pt-BR-AntonioNeural +12% (84,3 s) + palavras/legendas (seg. 5/6 corrigidos à mão: Whisper pulou "A tripulação saiu ilesa")
- [x] Cena Blender `motor/cena_bloqueio.py` (REALISTA=1), palco único: costa com porto, linha de corvetas, mar com ondas (`mar_ondulado`, backlog do mar liso dos mísseis), fumaça com `coluna_fumaca` (backlog Moldávia). Modelos novos em lowpoly.py: `graneleiro` (porões, guindastes de convés, castelo com janelas) e `guindaste_porto`. Câmera: chaves novas agora sempre BEZIER (antes herdavam o CONSTANT do `corte`)
- [x] grafismos.json (capa "158 NAVIOS / MANDADOS / DE VOLTA", 7 rótulos, 22 pílulas, 4 fontes, CTA, trilha "tenso"); prévia do compor OK
- [x] titulo.txt, legenda_post.txt, kwai_produto.txt
- [ ] Render: fila do PC do dono (render_fila/pendente/2026-11-28_bloqueio-naval.json); plano B nuvem PASSO=2
