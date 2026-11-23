Você vai montar e operar, nesta conta, uma rotina automática de vídeos curtos para TikTok e YouTube Shorts
chamada **"Peça por Peça"**: vídeos de ~2 min 30 s, verticais (1080×1920), em português do Brasil, sobre **guerras,
conflitos e política mundial**, no formato de explicação em cascata. Tudo com ferramentas **gratuitas**:
Blender (animação 3D), voz neural da Microsoft "Antonio" (edge-tts), Whisper (legendas), ffmpeg (montagem)
e o conector **Metricool** (agendamento no TikTok e no YouTube). Trabalhe em português comigo.

Comece agora pela PARTE 1 e só me pergunte o que for decisão minha.

---------------------------------------------------------------------------------------------------
PARTE 1 — DE ONDE VEM O CÓDIGO
---------------------------------------------------------------------------------------------------
Este sistema já existe pronto no repositório GitHub **Geffersonballes/Tutoriais**, na branch
**claude/nifty-noether-jtt32a** (pastas `tiktok-geopolitica/` e `.claude/`). Tente anexá-lo à sessão
(ferramenta add_repo, owner "Geffersonballes", repo "Tutoriais") e copie para o seu repositório:
- `.claude/agents/` (18 agentes) e `.claude/skills/tiktok-peca-por-peca/SKILL.md` (a rotina)
- `tiktok-geopolitica/` inteira (motor de vídeo, fontes, céus HDRI, documentação, vídeo-modelo)
Se conseguir, leia `tiktok-geopolitica/motor/README.md` e o SKILL.md e pule para a PARTE 4.
Se NÃO tiver acesso, reconstrua tudo pelas PARTES 2 e 3 abaixo.

---------------------------------------------------------------------------------------------------
PARTE 2 — PREPARAR A MÁQUINA (rode e salve como script de configuração do ambiente)
---------------------------------------------------------------------------------------------------
Crie `tiktok-geopolitica/motor/instalar.sh` (idempotente), rode, e proponha salvá-lo no script de
configuração do ambiente da nuvem (assim toda sessão nova já começa pronta):

```bash
#!/usr/bin/env bash
set -e
if ! command -v blender >/dev/null 2>&1; then
  cd /opt && curl -sSfL -o blender.tar.xz https://download.blender.org/release/Blender4.2/blender-4.2.3-linux-x64.tar.xz
  tar xf blender.tar.xz && rm blender.tar.xz && ln -sf /opt/blender-4.2.3-linux-x64/blender /usr/local/bin/blender
fi
if [ ! -e /usr/lib/x86_64-linux-gnu/libEGL.so.1 ]; then
  apt-get update -q >/dev/null && apt-get install -y -q libegl1 libgl1 libegl-mesa0 libgl1-mesa-dri >/dev/null
fi
python3 -c "import faster_whisper" 2>/dev/null || pip install -q faster-whisper pillow
python3 -c "import edge_tts" 2>/dev/null || pip install -q edge-tts
# o proxy da nuvem usa certificado próprio: o edge-tts precisa confiar nele
if [ -f /root/.ccr/ca-bundle.crt ]; then C=$(python3 -m certifi); grep -q ccr-proxy-added "$C" || { echo "# ccr-proxy-added" >> "$C"; cat /root/.ccr/ca-bundle.crt >> "$C"; }; fi
command -v ffmpeg >/dev/null || (apt-get update -q >/dev/null && apt-get install -y -q ffmpeg >/dev/null)
blender --version | head -1
```
Notas técnicas comprovadas:
- Não há GPU: o Blender renderiza na CPU. Use `blender -b --factory-startup -P script.py -- args`.
- faster-whisper: carregue o WAV com numpy (wave + np.int16/32768) e passe o array — o `av` do container
  falha ao abrir arquivos direto.
- Voz: `edge-tts --voice pt-BR-AntonioNeural --rate=+12% --file narracao_tts.txt --write-media narracao.mp3`
  (gratuito, sem chave, sem limite).
- Fonte das legendas: Montserrat (licença OFL), baixada de
  https://raw.githubusercontent.com/google/fonts/main/ofl/montserrat/ (arquivos `Montserrat[wght].ttf` e
  `Montserrat-Italic[wght].ttf`); escolha o peso com `font.set_variation_by_axes([800])`.
- Céu: HDRI CC0 da Poly Haven (API `https://api.polyhaven.com/files/kloofendal_48d_partly_cloudy_puresky`,
  arquivo 2k .hdr).

---------------------------------------------------------------------------------------------------
PARTE 3 — RECONSTRUIR (só se não tiver acesso ao repositório)
---------------------------------------------------------------------------------------------------
3.1 O FORMATO DO VÍDEO (copie a estrutura, nunca a marca de outro canal)
- Narração em **cascata**, 8 a 12 elos de 8–15 s: "Se você [faz o óbvio]… [problema]. Então você [solução].
  Esse é o [NOME TÉCNICO]. Mas [novo problema]…" — o "Mas" no fim de cada elo prende o espectador.
- Gancho com número nos primeiros 4 s. Final: "Parabéns. Você construiu ___." + CTA binário de comentário
  ("Se você já sabia, comente GENERAL. Se não sabia, comente RECRUTA.").
- 330–420 palavras (~3 palavras/s). Tom neutro: atribuir posições ("Moscou diz…", "Kiev afirma…").
- Visual: 3D estilizado "maquete" (tilt-shift, céu real, sol dourado, quinas arredondadas, prédios com
  janelas). Câmera sempre em movimento, corte seco só entre elos. Ameaça = vermelho, defesa = amarelo.
  Peça nova "nasce" crescendo; conceito revelado fica amarelo por ~1 s.
- Grafismos por cima: legenda **uma palavra por vez** no centro (65 % da altura), Montserrat ExtraBold branca
  com contorno preto (palavras do NOME TÉCNICO em amarelo); **rótulo amarelo grande** com o nome do conceito;
  **pílulas** brancas arredondadas com bolinha vermelha (problema) ou azul (dado); selo "Conteúdo gerado com IA";
  cartão final com o CTA. Áudio: narração em −14 LUFS + "whoosh" (ruído rosa filtrado) nos cortes.

3.2 MOTOR DE VÍDEO — crie em `tiktok-geopolitica/motor/`:
- `palavras.py` — Whisper "small" com `word_timestamps=True`, `initial_prompt` = texto do roteiro → palavras.json.
- `alinhar.py` — alinha as palavras do roteiro (narracao_tts.txt, UM parágrafo por elo) com as do Whisper
  (difflib.SequenceMatcher sobre palavras normalizadas sem acento; mapear "4"→"quatro", "cem"/"sem" etc.;
  interpolar as que não casarem) → legendas.json `[{w, s, e, seg}]` (seg = índice do elo/cena).
- `lowpoly.py` — biblioteca para o Blender, tudo por código (bmesh): caixa, cilindro, esfera, anel; modelos
  prédio, árvore, nuvem, míssil (frente = +Y), drone (asa delta), avião (com radome opcional), radar
  (base + prato giratório), caminhão (com tubos de lançamento), canhão, torre de laser, boneco; helpers de
  animação: `visivel(ob, ini, fim)` (hide_render com chaves), `pop()` (nasce crescendo), `caminho(ob, t0, t1, fn)`
  (chaves densas + orientação pelo movimento), `explosao()` (partículas), `rastro()` (bolinhas de fumaça),
  `destacar(material, t, cor)` (pisca amarelo). E `modo_realista()`: EEVEE (`BLENDER_EEVEE_NEXT`), 4 amostras,
  540×960, AgX "Punchy", materiais Principled com a cor convertida de sRGB para linear, fachadas com janelas
  (Brick Texture em coordenadas de objeto, só nas faces verticais), grama com Noise + ColorRamp, modificador
  Bevel nas caixas, céu HDRI, sol quente (1.0, 0.80, 0.58) energia 4,5, profundidade de campo (f/0.35) focada
  no alvo da câmera = efeito maquete.
- `cena_<tema>.py` — a decupagem de UM vídeo em código: monta o cenário, anima cada elo sincronizado por
  `T(elo, "palavra")` lido do legendas.json (nunca tempos fixos), câmera com TRACK_TO num vazio "alvo" e
  corte seco no início de cada elo. Modos: `preview t1,t2,...` (stills em meia resolução) e `range a,b`
  (render). Variáveis: `REALISTA=1` liga o modo_realista; `PASSO=2` renderiza 1 quadro a cada 2 (15 qps).
- `compor.py` — lê frames/ (repete o último quadro disponível quando foi renderizado com passo), redimensiona
  para 1080×1920, desenha com Pillow a legenda palavra a palavra (efeito pop), rótulos, pílulas, fontes, CTA e
  selo, mixa o áudio (narração + whooshes, loudnorm −14 LUFS) e gera `final.mp4` (H.264 CRF 19, AAC 192k,
  +faststart) e `capa.jpg`. Lê `grafismos.json`: `{rotulos:[{texto, de, ate}], pilulas:[{texto, ponto, de, ate, y}],
  fontes:[...], cta:{...}}`, com tempos no formato `[elo, "palavra", n, deslocamento]`.
- Render: ~3,6 s por quadro no modo realista; vídeo de 2:30 a 15 qps ≈ 2.270 quadros em 2 processos Blender
  paralelos ≈ 1h30. Rode em segundo plano e espere a notificação.

3.3 AGENTES — crie em `.claude/agents/` (um .md cada, com frontmatter name/description/tools):
supervisor-geral (orquestra e aplica os portões) · cacador-de-noticias (dispara em paralelo:
noticias-agencias-globais, noticias-regionais, noticias-brasil) · tradutor-de-fontes · editor-de-pauta ·
verificador-de-fatos (VETO; 2 fontes por número) · roteirista · critico-de-retencao · revisor-de-portugues
(copy: narração para TTS com números por extenso + legenda do post) · revisor-de-conformidade (VETO;
diretrizes do TikTok, sem violência gráfica, rótulo de IA) · diretor-de-arte · narrador (edge-tts Antonio) ·
editor-de-video · controle-de-qualidade (VETO; folha de contato 1 quadro/3 s, sincronia, área segura, LUFS) ·
publicador (Metricool) · analista-de-desempenho (métricas 48 h e 7 dias → aprendizados.md).

3.4 SKILL — crie `.claude/skills/tiktok-peca-por-peca/SKILL.md` com a rotina de 1 vídeo por execução:
instalar → notícias do dia → pauta (sem repetir os últimos 14 dias do `historico.md` nem o mesmo conflito no
dia) → checagem → roteiro → crítica → revisão de português → conformidade → narração Antonio → palavras e
alinhamento → cena Blender (prévia, depois render REALISTA=1 PASSO=2) → grafismos e composição → controle de
qualidade → link público → agendamento → histórico, commit e push. A cada vídeo, melhore 1 ou 2 modelos 3D.

---------------------------------------------------------------------------------------------------
PARTE 4 — PUBLICAÇÃO COM O CONECTOR METRICOOL
---------------------------------------------------------------------------------------------------
1. Chame `getBrandSettings` e me mostre as marcas e redes conectadas. Pergunte em qual perfil de TikTok e
   canal de YouTube devo publicar (se faltar, eu conecto no Metricool) e anote blogId, fuso e redes em
   `tiktok-geopolitica/config.md`.
2. Link público do vídeo: o Metricool só aceita URL pública. Use o Picsart (`picsart_upload_local_files`
   devolve um comando curl; o link vale pouco tempo, mas o Metricool copia o arquivo no agendamento).
   O upload pelo Google Drive daqui é limitado a 10 MB — não serve para vídeo.
3. UM post para as duas redes com `createScheduledPost`:
   `providers: [{"network":"tiktok"},{"network":"youtube"}]`, `autoPublish: false` (eu confirmo cada
   publicação no app do Metricool), `tiktokData: {privacyOption: "PUBLIC_TO_EVERYONE", isAigc: true,
   title: <tema>}`, `youtubeData: {title: "<tema> #shorts", type: "short", privacy: "public",
   category: "EDUCATION", madeForKids: false, isAiGeneratedContent: true, tags: [...]}`,
   `text` = legenda (≤ 150 caracteres + 5–7 hashtags).
4. Horários (Cuiabá; confirme com `getBestTimeToPostByNetwork`): produção das 07:45 → post 10:00;
   produção das 14:20 → post 18:00; produção das 17:50 → post 13:00 do dia seguinte. Mínimo 3 h entre posts.
5. Métricas (opcional): conector Windsor.ai, fonte `tiktok_organic` (só leitura).

---------------------------------------------------------------------------------------------------
PARTE 5 — AUTOMAÇÃO E REGRAS
---------------------------------------------------------------------------------------------------
- Faça primeiro UM vídeo completo e me mande o final.mp4 para eu aprovar antes de agendar.
- Depois de aprovado, crie 3 tarefas agendadas diárias (07:45, 14:20 e 17:50, fuso America/Cuiaba) que
  disparam NESTA conversa (é ela que tem os conectores), cada uma pedindo "produza e agende 1 vídeo seguindo
  a skill tiktok-peca-por-peca".
- Nunca publique sem os portões (fatos, conformidade, qualidade) e sem a minha confirmação no app.
- Proibido: rostos de líderes reais, sangue, vítimas, imagens realistas que pareçam registro real de ataque,
  torcer por um lado, cópia de marca/personagem de outros canais, fatos sem 2 fontes.
- Não use serviços pagos (ElevenLabs etc.) sem eu pedir: a voz é a do Antonio e o visual sai do Blender.
- Arquivos pesados (frames, prévias, .mp4) ficam fora do git (.gitignore).
