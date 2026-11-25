---
name: tiktok-peca-por-peca
description: Rotina diária da série "Peça por Peça" no TikTok pessoal (geffersonballes1) — vídeos 3D low-poly de 2 a 2,5 min sobre guerras, conflitos e política mundial, no formato cascata "Se você… Então você… Esse é o… Mas…". Use para produzir e agendar o vídeo do dia (meta de 3 por dia), retomar uma produção parada, ou quando o usuário pedir um novo vídeo da série.
---

# Série "Peça por Peça" — rotina de produção

Leia antes de começar: `tiktok-geopolitica/01_analise_video_referencia.md` (o formato),
`tiktok-geopolitica/03_pipeline.md` (agentes e portões), `tiktok-geopolitica/config.md` (contas, voz, IDs)
e o vídeo-modelo já pronto: `tiktok-geopolitica/producao/2026-11-23_defesa-antiaerea/`.

**Meta:** 3 vídeos por dia, cada um produzido numa sessão própria. Uma execução da skill = 1 vídeo.
Se já houver 3 vídeos agendados para hoje no Metricool (`getScheduledPosts`), produza para amanhã.

## 0. Preparar a máquina (≈ 3 min)
```bash
bash tiktok-geopolitica/motor/instalar.sh
```
Blender 4.2 (EEVEE em CPU), Mesa EGL, faster-whisper, edge-tts, Pillow, ffmpeg.

## 1. Pauta (agentes `cacador-de-noticias` → `editor-de-pauta`)
- Rode o `cacador-de-noticias` (ele dispara os 3 subagentes de notícias em paralelo) e grave
  `tiktok-geopolitica/noticias/AAAA-MM-DD_radar.md`. Se o radar de hoje já existir, reaproveite.
- Leia `tiktok-geopolitica/historico.md` e **não repita** tema dos últimos 14 dias.
- Prefira explicar um MECANISMO puxado pela notícia (ex.: "Por que o Estreito de Ormuz pode parar o mundo",
  "Você montou um cessar-fogo", "Por que destruir uma ponte muda uma guerra"). Notícia do dia só no gancho.
- Variedade nos 3 vídeos do dia: no máximo 1 sobre o mesmo conflito.

## 2. Checagem e roteiro (`verificador-de-fatos` ⛔, `roteirista`, `critico-de-retencao`, `revisor-de-portugues`)
- Cada número/data com 2 fontes; grave `producao/<pasta>/checagem.md`. Reprovado → volte ao passo 1.
- Roteiro: gancho com número em ≤ 4 s; 8–11 elos; 330–420 palavras (2:00–2:30); final
  "Parabéns. Você construiu/montou ___." + CTA binário (GENERAL/RECRUTA, DIPLOMATA/ESTAGIÁRIO…).
- Tom neutro: atribua posições ("Moscou diz…", "Kiev afirma…"). Nada de torcer por um lado.
- Grave `producao/<pasta>/narracao_tts.txt` — UM parágrafo por cena (o motor usa as quebras de linha
  como divisão de cenas). Números por extenso, siglas soletradas ("I-F-F").
- `revisor-de-conformidade` ⛔ aprova antes de gastar créditos de voz.

Pasta: `tiktok-geopolitica/producao/AAAA-MM-DD_<slug>/` com um `status.md` atualizado a cada etapa.

## 3. Narração (`narrador`) — voz gratuita Microsoft "Antonio"
Voz oficial da série: **pt-BR-AntonioNeural** (edge-tts, gratuita e sem limite). Não use ElevenLabs.
```bash
edge-tts --voice pt-BR-AntonioNeural --rate=+12% --file $P/narracao_tts.txt --write-media $P/narracao.mp3
```
```bash
ffmpeg -v error -y -i $P/narracao.mp3 -ac 1 -ar 16000 /tmp/narr.wav
python3 tiktok-geopolitica/motor/palavras.py /tmp/narr.wav $P/palavras.json $P/narracao_tts.txt
python3 tiktok-geopolitica/motor/alinhar.py $P      # -> legendas.json + tempos de cada cena
```

## 4. Animação 3D no Blender (`diretor-de-arte`) — ESTILO "B" EM VÍDEO
Decisão do dono: **tudo em vídeo animado no Blender**, sem ElevenLabs. Visual-alvo = estilo B (3D realista em
miniatura: tilt-shift, céu real, sol dourado, quinas arredondadas, prédios com janelas). Referência visual:
`tiktok-geopolitica/assets/estilo/referencia_B.png`. O modo `REALISTA=1` liga isso (`modo_realista()` em `lowpoly.py`:
EEVEE, céu HDRI CC0 da Poly Haven, materiais PBR, janelas, grama com textura, desfoque tilt-shift focado no `alvo`).

1. Copie `motor/cena_defesa.py` para `motor/cena_<slug>.py` e reescreva as cenas usando `motor/lowpoly.py`.
   Sincronize tudo com `T(cena, "palavra")`. Mantenha o bloco `if os.environ.get("REALISTA")` no fim.
   **A cada vídeo, melhore 1 ou 2 modelos** em `lowpoly.py` (mais detalhe nos caminhões, navios, tanques, aviões,
   sacos de areia, caixas de munição) — o visual deve se aproximar da referência B vídeo após vídeo.
2. Prévia (meia resolução, ~4 s por quadro) e conferência com Read:
```bash
REALISTA=1 blender -b --factory-startup -P tiktok-geopolitica/motor/cena_<slug>.py -- $P preview 3,15,40,80
```
3. Render final a 15 quadros/s (o compor duplica para 30 fps), em 2 processos, em segundo plano (~1h30):
```bash
N=$(REALISTA=1 blender -b --factory-startup -P tiktok-geopolitica/motor/cena_<slug>.py -- $P | grep FRAMES | cut -d' ' -f2)
H=$(( (N/2/2)*2 + 1 ))
REALISTA=1 PASSO=2 nohup blender -b --factory-startup -P .../cena_<slug>.py -- $P range 1,$((H-1)) > $P/render_a.log 2>&1 &
REALISTA=1 PASSO=2 nohup blender -b --factory-startup -P .../cena_<slug>.py -- $P range $H,$N > $P/render_b.log 2>&1 &
```
   Espere com um comando em segundo plano que termina quando o Blender acabar (você é avisado).

**Alternativa só para cenas-chave:** imagens de IA do Canva (`generate-image`) animadas com `motor/ilustrado.py`,
se o limite de IA do Canva permitir. Nunca use ElevenLabs.

## 5. Composição (`editor-de-video`)
Escreva `producao/<pasta>/grafismos.json` (rótulos amarelos, pílulas vermelhas/azuis, fontes, CTA) no
modelo do vídeo 01 e rode:
```bash
python3 tiktok-geopolitica/motor/compor.py $P $P/grafismos.json 5,30,60   # prévia
python3 tiktok-geopolitica/motor/compor.py $P $P/grafismos.json           # final.mp4 + capa.jpg
```
**Capa obrigatória** em `grafismos.json`: `"capa": {"linhas": ["33 KM DE MAR", "QUE PODEM", "PARAR O MUNDO"],
"destaque": [0], "dur": 1.3}` — 2 a 4 linhas, no máximo ~6 palavras no total, curiosa e verdadeira (sem
promessa que o vídeo não cumpre). Ela aparece grande no meio no 1º 1,3 s e vira a capa da grade do perfil
(o TikTok pessoal usa o 1º quadro). A narração do gancho continua por baixo.

## 6. Controle de qualidade (`controle-de-qualidade` ⛔)
Folha de contato 1 fps do `final.mp4`, conferir: legenda sincronizada e sem erro, nada cortado na área segura
(fora dos 15 % inferiores e da coluna de botões à direita), sem tela preta, duração 1:50–2:50, áudio −14 LUFS. Mais o **checklist do post**:
- [ ] **Capa:** o 1º quadro (`capa.jpg`) mostra o título grande, legível no tamanho da grade (olhe em 270 px).
- [ ] **Gancho:** a cena mais forte (explosão, ameaça, número chocante) aparece nos 3 primeiros segundos.
- [ ] **Título:** curto, curioso e verdadeiro; o vídeo responde à pergunta da capa.
- [ ] **Legenda:** sem erro e sem tapar o objeto principal da cena (rótulos e pílulas acima, legenda a 63 % da altura).
- [ ] **Começo e fim:** não começa nem termina no meio de uma frase; o CTA aparece completo.
- [ ] **Crédito/fonte:** número na tela tem fonte; selo "Conteúdo gerado com IA" visível na tela (decisão do dono 24/11) + isAigc / isAiGeneratedContent no post.

## 7. Entrega e agendamento (`publicador`)
1. Gere um link público do `final.mp4` pelo Picsart (aceita até 100 MB; o Google Drive daqui só aceita 10 MB):
   chame `picsart_upload_local_files` com o nome e o tamanho do arquivo e rode o `curl` devolvido, trocando `{path}`
   pelo caminho do vídeo. O link (`response.url`) é temporário, mas o Metricool copia o vídeo para o servidor dele
   no agendamento, então basta usá-lo logo em seguida.
2. Envie o vídeo ao usuário (SendUserFile) com a legenda do post.
3. Agende no Metricool **um post só para TikTok + YouTube Shorts** (marca `ballestech`, blogId `8049742`,
   fuso `America/Cuiaba`; TikTok `geffersonballes1`, YouTube canal `UCfamwKNkLBtNjhjZLPQdDfg`).
   **Horários fixos aprovados pelo dono** (melhores das duas redes segundo o Metricool):
   | Produção | Post |
   |---|---|
   | manhã (06:20; render leva ~2h20) | **10:00** do mesmo dia |
   | tarde (14:20) | **18:00** do mesmo dia |
   | noite (17:50) | agora é da série 2 (games), post 13:00 do dia seguinte — ver skill games-fase-por-fase |
   Se o horário já passou ou está ocupado, use o próximo livre entre 10:00, 13:00, 16:00 e 18:00 (mínimo 3 h entre posts).
   - `providers: [{"network":"tiktok"},{"network":"youtube"}]`, **`autoPublish: true`** (publicação automática
     autorizada pelo dono em 23/11/2026 — com `false` o TikTok fica parado na caixa de entrada do app).
     Por isso os portões (fatos, conformidade, qualidade) são obrigatórios: se algum reprovar, NÃO agende.
   - `tiktokData`: `isAigc: true`, `privacyOption: PUBLIC_TO_EVERYONE`, comentários/dueto/stitch liberados, `title` = tema.
   - `youtubeData`: `{"title": "<tema> #shorts" (≤ 100 caracteres), "type": "short", "privacy": "public",
     "category": "EDUCATION", "madeForKids": false, "isAiGeneratedContent": true, "tags": [5–8 termos do tema]}`.
   - Legenda (`text`, vale como descrição no YouTube): ≤ 150 caracteres + 5–7 hashtags
     (#geopolitica #guerra #noticias #historia #aprendanotiktok + 2 do tema).
4. Registre em `tiktok-geopolitica/historico.md`: data, tema, link do Metricool, horário.
5. Faça commit e push dos arquivos da produção (frames, preview e final.mp4 ficam fora do git).

## 8. Desempenho (`analista-de-desempenho`, 1× por dia)
Windsor `tiktok_organic` (conta "Gefferson Balles"): views, retenção, comentários, seguidores dos vídeos de
48 h e 7 dias atrás → `tiktok-geopolitica/aprendizados.md`. Leia esse arquivo antes de escolher a próxima pauta.

**Hashtags:** siga `tiktok-geopolitica/hashtags.md` (6 de alcance #fyp #foryou #paravoce #viral #tiktokbrasil #shorts + nicho + tema + #aprendanotiktok).

**Melhoria contínua (todo vídeo):** antes de montar a cena, pegue 1 item "aberto" de `melhorias/backlog.md`
que caiba no vídeo e implemente; no QC, anote no backlog todo defeito que não deu para corrigir agora.

**Capa no YouTube (canal verificado em 23/11):** no `createScheduledPost`, envie `"videoCoverMilliseconds": 600` no info (quadro com o título grande da capa). O TikTok pessoal ignora esse campo e usa o 1º quadro, que já é a capa.

**REDES (decisão do dono, 23/11):** a série de guerra/geopolítica vai SÓ para o TikTok — `providers: [{"network":"tiktok"}]`, sem youtubeData. O YouTube Shorts do canal (público gamer) fica só para a série de games.

## Pedido de like (obrigatório, decisão do dono 24/11)
O compor.py acrescenta sozinho, depois da narração, a fala "Gostou do conteúdo? Então deixa o seu like!" (Antonio) e a tela GOSTOU DO CONTEÚDO? / DEIXA O LIKE. Não desligue. No QC, confira que aparece no fim.

## Áudio (obrigatório desde 24/11)
O compor.py gera voz tratada + trilha original + efeitos (motor/audio.py). Escolha o clima no grafismos.json ("trilha": {"clima": "curioso|tenso|epico|divertido"}) conforme a emoção do tema. Todo aprendizado novo vai para produto/MANUAL_DA_AUTOMACAO.md.

**MARCA E REDES (decisão do dono, 25/11 — vale acima do que estiver escrito antes):** agende na marca nova do Metricool `geffersonballes1`, **blogId `8356514`** (fuso America/Cuiaba). Não use mais a `ballestech` (8049742) — ela tem o mesmo TikTok e YouTube, e agendar nas duas duplicaria o post. Todo vídeo vai também para o **Facebook como Reel** (página Peça por Peça): acrescente `{"network":"facebook"}` em `providers` e `"facebookData": {"type": "REEL", "title": "<título curto>"}`. Guerra = TikTok + Facebook; games = TikTok + YouTube + Facebook.

## KWAI (25/11)
Depois de agendar no Metricool, acrescente o vídeo à lista do Kwai no OneDrive, seguindo kwai/LEIA.md.

## INSTAGRAM (25/11)
Todo post na marca 8356514 inclui também {"network":"instagram"} (@pecaporpeca95) com "instagramData": {"type":"REEL","showReelOnFeed":true,"isAiGenerated":true}.
