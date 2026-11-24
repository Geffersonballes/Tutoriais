# Economia de contexto (regra das produções automáticas)

A conversa principal só coordena. Todo o trabalho pesado (pesquisa, roteiro, Blender, prévias, folhas de
contato, QC) roda num SUBAGENTE, cujo texto e imagens não entram no contexto da conversa principal.

Na conversa principal, a tarefa agendada faz só:
1. `Agent` (subagent_type `general-purpose`, run_in_background false) com o pedido de produção da série
   (skill `tiktok-peca-por-peca` ou `games-fase-por-fase`), terminando no `final.mp4` aprovado no QC,
   `legenda_post.txt`, título do YouTube, checagem e commit/push dos arquivos.
   O subagente devolve NO MÁXIMO 10 linhas: pasta, tema, título, duração, LUFS, pendências.
2. Upload Picsart (curl) + `createScheduledPost` no Metricool + linha no historico.md + commit/push.
3. Aviso curto ao dono (≤ 6 linhas). Não abrir imagens nem logs grandes aqui.
