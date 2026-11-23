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
Blender 4.2 (Workbench, sem GPU), Mesa EGL, faster-whisper, Pillow, ffmpeg.

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

## 4. Ilustrações animadas (`diretor-de-arte`) — ESTILO PADRÃO "B"
Visual aprovado pelo dono: **3D realista em miniatura** (tilt-shift, luz suave de fim de tarde, veículos e cidades
detalhados, claramente maquete — nunca parecendo foto real). Referência: `tiktok-geopolitica/assets/estilo/referencia_B.png`
(geração ElevenLabs `lVqhhKVLhbHRz9ZXTCxI`).

1. **Planeje as tomadas**: 14 a 18 imagens por vídeo (1 por cena + 1 extra nas cenas longas, gancho e final).
   Cada tomada = imagem + movimento de câmera + efeitos sincronizados com palavras da narração.
2. **Gere as imagens** (ElevenLabs, ~518 créditos cada em 2K):
   - `creative_create_flow` (nome "Peça por Peça — <slug>") → `creative_add_flow_asset_node` com
     `generation_id: lVqhhKVLhbHRz9ZXTCxI` (referência de estilo).
   - Para cada tomada: `creative_add_flow_node` (`image-generation`, `gpt-image-2.5-sunburst`,
     `model_parameters: {"aspect_ratio": "9:16", "resolution": "2K", "quality": "high"}`, `connect_from: [ref]`).
     Prompt começa SEMPRE com: "Use the reference image ONLY for its visual style: stylized-realistic 3D miniature,
     tilt-shift depth of field, soft global illumination, clean readable shapes. New scene, vertical 9:16 composition:"
     e termina com: "Keep the main action in the middle of the frame; calmer top 20% and bottom 25% (captions).
     No text, no letters, no logos, no flags, no faces of real people, no blood, no victims."
   - `creative_run_flow_nodes` em lotes de até 20, `generations_count: 1` (nunca repita: cobra de novo); acompanhe com
     `creative_get_flow_run_status` e baixe cada `content_url` para `$P/img/NN.png`.
   - Confira as imagens (folha de contato com Read). Só regenere uma imagem se estiver errada de verdade.
3. **Escreva `$P/tomadas.json`** (formato documentado no topo de `motor/ilustrado.py`): `img`, `de` (palavra da
   narração), `mov` (zoom_in, zoom_out, pan_esq, pan_dir, pan_cima, pan_baixo), `foco`, e `efeitos`
   (`aneis` = radar/sinal, `rastro` = míssil/foguete/drone, `explosao`, `seta`, `pulso`, `alvo`).
   Coordenadas em frações da imagem — confira na folha de contato onde está cada objeto.
4. **Gere os quadros**:
```bash
python3 -I tiktok-geopolitica/motor/ilustrado.py $P preview 3,15,40      # prévia
python3 -I tiktok-geopolitica/motor/ilustrado.py $P                      # todos os quadros (~2 min)
```
**Plano B** (se faltar crédito na ElevenLabs): motor 3D low-poly do Blender — copie `motor/cena_defesa.py` para
`motor/cena_<slug>.py`, use `motor/lowpoly.py` e renderize com `blender -b --factory-startup -P ... -- $P range a,b`
em 4 processos (≈ 25 min).

## 5. Composição (`editor-de-video`)
Escreva `producao/<pasta>/grafismos.json` (rótulos amarelos, pílulas vermelhas/azuis, fontes, CTA) no
modelo do vídeo 01 e rode:
```bash
python3 tiktok-geopolitica/motor/compor.py $P $P/grafismos.json 5,30,60   # prévia
python3 tiktok-geopolitica/motor/compor.py $P $P/grafismos.json           # final.mp4 + capa.jpg
```

## 6. Controle de qualidade (`controle-de-qualidade` ⛔)
Folha de contato 1 fps do `final.mp4`, conferir: legenda sincronizada e sem erro, nada cortado na área segura
(fora dos 15 % inferiores e da coluna de botões à direita), sem tela preta, duração 1:50–2:50, áudio −14 LUFS.

## 7. Entrega e agendamento (`publicador`)
1. Gere um link público do `final.mp4` pelo Picsart (aceita até 100 MB; o Google Drive daqui só aceita 10 MB):
   chame `picsart_upload_local_files` com o nome e o tamanho do arquivo e rode o `curl` devolvido, trocando `{path}`
   pelo caminho do vídeo. O link (`response.url`) é temporário, mas o Metricool copia o vídeo para o servidor dele
   no agendamento, então basta usá-lo logo em seguida.
2. Envie o vídeo ao usuário (SendUserFile) com a legenda do post.
3. Agende no Metricool (marca `ballestech`, blogId `8049742`, fuso `America/Cuiaba`, TikTok `geffersonballes1`),
   no melhor horário livre (`getBestTimeToPostByNetwork`), com intervalo mínimo de 4 h entre posts:
   - **Padrão (com aprovação):** `createScheduledPost` com `autoPublish: false` → o dono recebe um aviso no app
     do Metricool e confirma a publicação com 1 toque. Só use `autoPublish: true` se o usuário autorizar
     explicitamente a publicação 100 % automática (registre a autorização em `config.md`).
   - `tiktokData`: `isAigc: true`, `privacyOption: PUBLIC_TO_EVERYONE`, comentários/dueto/stitch liberados.
   - Legenda: ≤ 150 caracteres + 5–7 hashtags (#geopolitica #guerra #noticias #historia #aprendanotiktok + 2 do tema).
4. Registre em `tiktok-geopolitica/historico.md`: data, tema, link do Metricool, horário.
5. Faça commit e push dos arquivos da produção (frames, preview e final.mp4 ficam fora do git).

## 8. Desempenho (`analista-de-desempenho`, 1× por dia)
Windsor `tiktok_organic` (conta "Gefferson Balles"): views, retenção, comentários, seguidores dos vídeos de
48 h e 7 dias atrás → `tiktok-geopolitica/aprendizados.md`. Leia esse arquivo antes de escolher a próxima pauta.
