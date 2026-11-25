# Longo 1 — Como funciona a guerra moderna (prévia, 25/11)

Status: **prévia enviada ao dono, aguardando aprovação do formato** (folha.jpg + trecho de 30 s). Não publicar antes disso.

- Formato: 1920x1080. O Short fica no centro (608x1080), sobre o próprio vídeo desfocado e escurecido. Painel esquerdo: "PEÇA N" e o tema. Painel direito: título da série e cinco pontos de progresso. Selo de IA no canto.
- Duração: 11:08. Áudio a −14,3 LUFS.
- Fontes: os final.mp4 baixados das URLs do Metricool (static.metricool.com/planner/202611/…), porque o git ignora os .mp4.
- Voz do dono (ElevenLabs eleven_v4, 1 geração cada): abertura de 16,4 s e fecho de 10,7 s ("se inscreve para a próxima peça").
- A rede elétrica foi cortada em 123,4 s para tirar o pedido de like repetido. O dos inspetores ainda tem o like no final (dá para cortar em ~150 s na versão final).
- Ajustes para a versão final: quebrar "A rede elétrica" como "A rede / elétrica" no painel; cortar o like do vídeo nuclear.
- Para montar: `python3 cards.py && bash montar.sh` (tudo no ffmpeg, cerca de 10 min em 4 CPUs).

## Capítulos (para a descrição)
00:00 As cinco peças da guerra moderna
00:20 Peça 1 — Por que todo mundo mira nas pontes
01:36 Peça 2 — A rede elétrica como alvo
03:41 Peça 3 — A defesa antiaérea (míssil de 4 milhões x drone de 35 mil)
06:14 Peça 4 — O Estreito de Ormuz
08:21 Peça 5 — Como se vigia uma bomba atômica
10:55 Próxima peça
