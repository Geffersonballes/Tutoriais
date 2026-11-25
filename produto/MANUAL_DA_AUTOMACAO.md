# Manual da automação de vídeos curtos (base do produto)

Objetivo: replicar para qualquer conta/nicho a máquina que já roda nas séries "Peça por Peça" (geopolítica) e
"Fase por Fase" (games). Cada aprendizado novo entra aqui na seção **Aprendizados** com data.
Tudo usa ferramentas gratuitas e conteúdo 100% próprio (sem música, arte ou personagem de terceiros) — requisito para vender.

## 1. Linha de produção (um vídeo)
1. **Radar** — agente caça tendências/notícias (`cacador-de-tendencias`, `cacador-de-noticias`).
2. **Pauta** — maior nota, sem repetir o `historico.md`.
3. **Checagem** — 2 fontes por afirmação (`verificador-de-fatos`).
4. **Roteiro** — 60–80 s (games) ou 2–2,5 min (geo), gancho nos 3 primeiros segundos.
5. **Voz** — edge-tts `pt-BR-AntonioNeural --rate=+12%` (grátis). Tempos por palavra com faster-whisper.
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
- **24/11** — Áudio: trilha por clima + efeitos + voz tratada dão "vida" sem custo. A trilha precisa ficar
  ~13 dB abaixo da voz; efeitos a −24 LUFS (mais alto compete com a fala).
- **24/11** — Pedido de like falado + na tela no último segundo (voz Antonio + DEIXA O LIKE).
- **24/11** — Subagentes têm limite semanal de uso: o agendamento precisa de plano B (produzir na sessão principal).
- **24/11** — Reinício da máquina mata renders: sempre conferir quadros faltantes e retomar só os intervalos vazios.
- **23/11** — YouTube do canal gamer: games 1,1 mil views vs geo 2–3 → geo só no TikTok.
- **23/11** — Capa com título grande no início (1,3 s) e cover em 600 ms no YouTube.
