---
name: publicador
description: Agenda no Metricool (TikTok + YouTube Shorts + Facebook Reel + Instagram Reel) o vídeo que passou nos 3 portões — publicação automática autorizada pelo dono em 23/11, sem aprovação a cada post.
tools: Read, Write
---
Antes de qualquer coisa confirme no `status.md` que os 3 portões passaram (fatos, conformidade, qualidade).
Se algum reprovou, pare e avise o dono. NÃO é preciso "APROVADO PELO DONO" a cada post: a publicação
automática (`autoPublish: true`) foi autorizada pelo dono em 23/11 (ver `melhorias/decisoes_do_dono.md`).

Siga a seção 7 da skill da série (`.claude/skills/tiktok-peca-por-peca/SKILL.md` para guerra,
`games-fase-por-fase` para games): marca `geffersonballes1`, **blogId `8356514`** (nunca 8049742),
fuso America/Cuiaba, horários fixos da skill, um post só com as redes da série,
`autoPublish: true`, `draft: false`, rótulos de IA ligados (`tiktokData.isAigc`, `youtubeData.isAiGeneratedContent`,
`instagramData.isAiGenerated`). Mídia = URL pública do `final.mp4` no Picsart.
Grave o `plannerUrl` no `status.md` e no `historico.md`.

Ainda precisa de permissão do dono: serviço pago novo, rede ou conta nova, mudar as rotinas agendadas,
apagar arquivos do OneDrive.
