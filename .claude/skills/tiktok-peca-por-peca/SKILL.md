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

## 3. Narração (`narrador`)
ElevenLabs `creative_generate_speech`, voz **Fernando Will** `SWnJtSNPFBZm03EETsy1`, modelo
`eleven_multilingual_v2`, `generations_count: 1` (nunca repita a chamada: cobra de novo). Baixe para `narracao.mp3`.
```bash
ffmpeg -v error -y -i $P/narracao.mp3 -ac 1 -ar 16000 /tmp/narr.wav
python3 tiktok-geopolitica/motor/palavras.py /tmp/narr.wav $P/palavras.json $P/narracao_tts.txt
python3 tiktok-geopolitica/motor/alinhar.py $P      # -> legendas.json + tempos de cada cena
```

## 4. Cenas 3D (`diretor-de-arte`)
- Copie `motor/cena_defesa.py` para `motor/cena_<slug>.py` e reescreva as cenas. Use SÓ a biblioteca
  `motor/lowpoly.py` (cidade, mísseis, drones, aviões, radar, caminhões, navios = caixas/cilindros, bonecos,
  explosões, fumaça, anéis). Se precisar de um modelo novo (navio, tanque, mapa, bandeira genérica), crie a
  função em `lowpoly.py` para reaproveitar nos próximos vídeos.
- Sincronize tudo com `T(cena, "palavra")` — nunca tempos fixos.
- Regras visuais: corte seco só entre cenas; câmera sempre se movendo; objeto novo nasce com `pop`;
  conceito revelado fica amarelo com `destacar`; ameaça = vermelho, defesa = amarelo; objetos GRANDES no quadro
  (mísseis já têm escala ×2,4; drones ≥ 2,4; aviões ≥ 2).
- **Proibido:** rostos de líderes reais, bandeiras usadas de forma ofensiva, sangue, corpos, vítimas,
  imagens realistas de guerra. Tudo estilizado.
- Prévia antes do render completo (confira a folha de contato com Read):
```bash
blender -b --factory-startup -P tiktok-geopolitica/motor/cena_<slug>.py -- $P preview 2,10,20,30,...
```
- Render completo em 4 processos (≈ 25 min para 2:30). Rode em segundo plano e espere a notificação:
```bash
N=$(blender -b --factory-startup -P tiktok-geopolitica/motor/cena_<slug>.py -- $P | grep FRAMES | cut -d' ' -f2)
# divida 1..N em 4 faixas e lance:  blender ... -- $P range a,b  (uma por processo, com nohup)
```

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
1. Suba `final.mp4` para o Google Drive (`create_file` com referência de arquivo `sha256:<hash>:<caminho>`,
   `contentMimeType: video/mp4`, `disableConversionToGoogleType: true`) e também para o OneDrive em
   `Área de Trabalho/Editor de vídeo/Peça por Peça/` (pasta autorizada no CLAUDE.md).
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
