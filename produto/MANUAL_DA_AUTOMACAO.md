# Manual da automação de vídeos curtos (base do produto)

Objetivo: replicar para qualquer conta/nicho a máquina que já roda nas séries "Peça por Peça" (geopolítica) e
"Fase por Fase" (games). Cada aprendizado novo entra aqui na seção **Aprendizados** com data.
Tudo usa ferramentas gratuitas e conteúdo 100% próprio (sem música, arte ou personagem de terceiros) — requisito para vender.

## 1. Linha de produção (um vídeo)
1. **Radar** — agente caça tendências/notícias (`cacador-de-tendencias`, `cacador-de-noticias`).
2. **Pauta** — maior nota, sem repetir o `historico.md`.
3. **Checagem** — 2 fontes por afirmação (`verificador-de-fatos`).
4. **Roteiro** — 60–80 s (games) ou 2–2,5 min (geo), gancho nos 3 primeiros segundos.
5. **Voz** — games: voz clonada do dono no ElevenLabs (eleven_v4, com emoção); geo: edge-tts `pt-BR-AntonioNeural --rate=+12%` (grátis). Tempos por palavra com faster-whisper.
6. **Cena 3D** — Blender headless (estilo B miniatura realista ou C cartoon com mascote próprio). PASSO=2, 2 processos.
7. **Composição** — `motor/compor.py`: capa, legenda palavra a palavra, rótulos, pílulas, fontes, CTA, selo de IA,
   **pedido de like** e **áudio completo** (ver seção 2).
8. **QC** — checklist (capa legível em 270 px, gancho, legenda, áudio, selo de IA, like no final).
9. **Publicação** — link público (Picsart) → Metricool `autoPublish`, `isAigc`/`isAiGeneratedContent` = true,
   hashtags de alcance + nicho, capa em 600 ms. Publica assim que fica pronto, ≥ 1h30 entre posts.

## 2. Áudio (motor/audio.py) — padrão desde 24/11
- **Voz tratada**: passa-alta 75 Hz, −2,5 dB em 220 Hz (tira o embolado), +3 dB em 3,2 kHz (presença),
  +1,5 dB em 9 kHz (ar), de-esser e compressor 3:1. Cadeia em `VOZ_FILTRO`.
- **Trilha original por clima**, sintetizada em código (sem licença de terceiros):
  | clima | uso | bpm | caráter |
  |---|---|---|---|
  | curioso | games / "como funciona" | 100 | maior, arpejo leve, batida lo-fi |
  | divertido | meme, assunto leve | 116 | maior, palmas, baixo saltado |
  | tenso | guerra / geopolítica | 88 | menor, tambor grave, baixo pulsando, sem melodia |
  | epico | revelação, números grandes | 120 | menor, bumbo forte, arpejo |
  Escolha em `grafismos.json`: `"trilha": {"clima": "tenso", "volume": -16}`; padrão = curioso (games) / tenso (geo).
- **Estrutura que acompanha a narrativa**: trilha abafada durante a capa → *impacto* + batida entra quando a capa sai
  → bateria some 1 tempo antes de cada novo bloco (respiro) → *whoosh* em cada corte → *bloop* em cada rótulo
  → *riser* subindo até o CTA → batida para e toca um *ding* no "Deixa o like".
- **Ducking**: a trilha abaixa sozinha quando a voz fala (sidechain 6:1), ~13 dB abaixo da voz.
- **Master**: loudnorm −14 LUFS, pico −1,5 dBTP (padrão TikTok/YouTube).

## 3. Regras fixas do dono (replicar como padrão do produto)
Ver `melhorias/decisoes_do_dono.md`. Principais: rótulo de IA sempre; pedido de like no fim; nada de ElevenLabs
ou serviço pago sem aprovação; nada de cortes de vídeos de terceiros; YouTube só para o nicho que performa lá.

## 4. Para clonar para uma conta nova (roteiro do produto)
1. Copiar `motor/`, `.claude/agents/`, a skill da série e `hashtags.md`.
2. Criar `config.md` da série (nicho, horários, redes, estilo visual, mascote próprio).
3. Conectar a marca no Metricool e trocar o `blogId`.
4. Criar os agendamentos (produção → post) e o relatório/melhoria semanal.
5. Rodar 1 vídeo de teste com QC manual antes de ligar o automático.

## Aprendizados (mais recente primeiro)
- **25/11** — Voz clonada do dono no ElevenLabs (eleven_v4 + etiquetas como [surprised], [curious], [dramatically]) dá emoção que a voz grátis não tem. Custo ~1.200 créditos por vídeo de 65 s; voz clonada custa ~2x a de biblioteca. Plano Creator cobre 3 vídeos/dia. Para clientes: cada conta pode clonar a voz do dono do perfil.
- **25/11** — Whisper com `initial_prompt` = roteiro inteiro pode "alucinar" o começo e perder as primeiras frases (vídeo dos NPCs: 32 palavras sem casar). Se `alinhar.py` mostrar muitas "não casadas", rode de novo com um prompt curto (só nomes próprios) e `condition_on_previous_text=False`.
- **25/11** — Vários agentes ao mesmo tempo dividem a mesma pasta temporária: todo arquivo temporário leva o slug do vídeo no nome (ex.: `npcs_f1.jpg`), senão um agente sobrescreve a prévia do outro.
- **25/11** — Pedestre articulado reutilizável (`pedestre()`, `andar()`, `ir()`, `passeio()` em `cena_gta_npcs.py`): tipos de corpo por escala (`h`, `w`) sem deformar a cabeça; serve para multidões e para qualquer vídeo com "gente andando".
- **25/11** — Cena noturna que funciona: em vez de escurecer tudo, trocar o céu por um HDRI de pôr do sol, baixar o sol e acender janelas emissivas por bairro (`cena_rede.py`); a luz apagando vira o gancho. Cor animada no modo realista: gravar só o canal da curva (bug corrigido em `lowpoly.py`).
- **25/11** — Marca única do canal no fim dos vídeos (`marca_canal`), igual ao nome do perfil: reforça o nome e facilita clonar para outra conta.
- **24/11** — Áudio APROVADO pelo dono ("ficou bom, pode seguir assim"): trilha por clima + efeitos + voz tratada dão "vida" sem custo. A trilha precisa ficar
  ~13 dB abaixo da voz; efeitos a −24 LUFS (mais alto compete com a fala).
- **24/11** — Pedido de like falado + na tela no último segundo (voz Antonio + DEIXA O LIKE).
- **24/11** — Subagentes têm limite semanal de uso: o agendamento precisa de plano B (produzir na sessão principal).
- **24/11** — Reinício da máquina mata renders: sempre conferir quadros faltantes e retomar só os intervalos vazios.
- **23/11** — YouTube do canal gamer: games 1,1 mil views vs geo 2–3 → geo só no TikTok.
- **23/11** — Capa com título grande no início (1,3 s) e cover em 600 ms no YouTube.

- **25/11** — Uma marca do Metricool = um conjunto de perfis de um cliente/projeto. Ao abrir marca nova para as mesmas contas, pare de agendar na antiga (mesmo TikTok/YouTube nas duas = post duplicado). Facebook entra como `facebookData.type = "REEL"`.

### Visual 3D "nível 2" (25/11)
- Testamos 3 níveis num quadro do vídeo do GTA (comparação em `tiktok-geopolitica/motor/testes_visual/comparacao_visual.jpg`). O dono escolheu o nível 2: contorno de desenho + luz de contorno + cor viva + fundo desfocado. Virou padrão em `cartoon.py` (`visual_nivel2`).
- Aprendizado: o contorno por casca invertida deixa os objetos granulados se a casca projetar sombra. Use material de emissão pura com `use_backface_culling_shadow` e `use_transparent_shadow` ligados. Com isso o custo cai de 2,5× para ~1,5×.
- Resolução 720x1280 (nível 3) custa ~5× e não cabe em 5 vídeos/dia num servidor sem GPU.

### Ao iniciar a fase do produto (decisão do dono, 25/11)
Primeiro passo automático: revisar e instalar no repositório o pacote de habilidades **Superpowers** (github.com/obra/superpowers) e desenvolver o produto pelo fluxo dele: brainstorming → plano → subagentes (em paralelo quando possível) → testes. Detalhes em `melhorias/decisoes_do_dono.md`. Não usar esse fluxo na produção diária dos vídeos.

### Kwai (25/11)
O Kwai não tem API de publicação. Solução: uma lista no OneDrive com link de download (Picsart) e legenda adaptada (#kwai #kwaibrasil), que o dono posta pelo app. Limites de upload: 1 MB no conector M365 e 10 MB no Google Drive. Detalhes em kwai/LEIA.md.

### Instagram (25/11)
Conta @pecaporpeca95 (profissional, ligada à página do Facebook) na marca 8356514. Reels com isAiGenerated true. Instagram exige conta profissional + página do Facebook para o Metricool publicar sozinho.
