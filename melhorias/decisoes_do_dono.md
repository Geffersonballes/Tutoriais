# Decisões do dono (o melhoria-continua NÃO muda sem pedir)
- Voz: GUERRA = edge-tts Antonio (grátis). GAMES = voz clonada do dono no ElevenLabs (decisão de 25/11, plano Creator).
- Redes: YouTube Shorts SÓ para games (série 2); TikTok recebe as duas séries por enquanto, para coletar métricas (decisão 23/11). Instagram: não, por enquanto.
- Publicação automática (autoPublish true) autorizada.
- Proporção: 3 vídeos de games + 2 de geopolítica por dia.
- Visual: série 1 estilo B (maquete), série 2 estilo C (cartoon, mascote Pixel).
- Cortes de vídeos de terceiros (ex.: GTA 6 do YouTube): não fazer agora.
- Selo "Conteúdo gerado com IA" na tela: SIM, sempre (24/11), além da declaração de IA nas plataformas (isAigc / isAiGeneratedContent).
- **Pedido de like no final de todo vídeo** (24/11): depois da narração, a voz Antonio diz "Gostou do conteúdo? Então deixa o seu like!" e a tela mostra GOSTOU DO CONTEÚDO? / DEIXA O LIKE. Automático no compor.py (`"curtir": false` no grafismos.json desliga).
- **Áudio com trilha e efeitos** (24/11): o dono pediu mais vida no áudio. Padrão agora: voz tratada + trilha original por clima + efeitos + ducking (motor/audio.py). Tudo documentado em produto/MANUAL_DA_AUTOMACAO.md, que é a base para vender a automação.
- **Áudio novo aprovado** (24/11): "o áudio ficou bom, pode seguir assim" — manter trilha -16 dB, efeitos x0,3, voz tratada.
- **Nome do canal: Peça por Peça** (25/11): o perfil do TikTok passa a se chamar Peça por Peça. A marca no fim de TODOS os vídeos (as duas séries) é PEÇA POR PEÇA — fixo no compor.py (`marca_canal` no grafismos.json troca, para outras contas). "Fase por Fase" continua só como nome interno da série de games.
- **Voz dos games = voz do dono** (25/11): o dono assinou o ElevenLabs Creator e aprovou a própria voz clonada (voice_id Dt3IFiwrxXdZMMFz4Ai0, modelo eleven_v4, etiquetas de emoção). Guerra continua com Antonio.

- **25/11** — Metricool: publicar pela marca nova `geffersonballes1` (blogId 8356514), não mais pela `ballestech`. Facebook (Reels) recebe games E guerra. Guerra = TikTok + Facebook; games = TikTok + YouTube + Facebook.
- 25/11: visual 3D dos games no **nível 2** (contorno de desenho, luz de contorno, cor viva, fundo desfocado) — padrão no cartoon.py.
- 25/11: **Fase do produto → usar o Superpowers (github.com/obra/superpowers).** Quando começarmos a fase de transformar a automação em produto (replicar para outras contas), o Claude deve, SEM esperar novo pedido: (1) ler o conteúdo do pacote antes (código de terceiros); (2) instalá-lo no próprio repositório (.claude/settings.json, para carregar em toda sessão da nuvem — não "global no dispositivo"); (3) conduzir o desenvolvimento pelo fluxo dele: /brainstorming → /writing-plans → /subagent-driven-development (+ /dispatching-parallel-agents quando der), testando antes de entregar. NÃO usar na produção diária dos vídeos (só gasta uso). Avisar o dono que execuções longas consomem o limite de uso.
