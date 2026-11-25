# Checagem — Como a sua LIVE chega em milhões de celulares ao mesmo tempo? — APROVADO

Roteiro sem números de audiência, de dinheiro ou de qualidade (nada de "1080p" ou "X segundos"): só o mecanismo,
descrito de forma genérica para plataformas de live (não afirmamos detalhes internos do TikTok que não são públicos).

| Afirmação no roteiro | Fontes | Status |
|---|---|---|
| "Em segundos, alguém do outro lado do país já te vê" (atraso de poucos segundos numa live) | getstream.io — The Building Blocks of Live Streaming Infrastructure https://getstream.io/blog/live-video-infrastructure/ (HLS: latência "longa", de segundos) · Mux — Low latency live streaming guide https://mux.com/articles/low-latency-live-streaming-developers-guide-ll-hls-webrtc-cmaf (HLS padrão: 20–45 s; baixa latência: 2–4 s) | ✅ ("em segundos", sem número exato) |
| O vídeo cru é pesado demais; o celular (app) comprime/codifica antes de enviar | Wowza — Live Video Streaming: How It Works https://www.wowza.com/blog/live-video-streaming-how-it-works ("the video signal needs to be compressed through an encoder"; o encoder pode ser "mobile app") · Akamai — What is live video streaming? https://www.akamai.com/glossary/what-is-live-video-streaming ("The video data is compressed to create smaller files") | ✅ |
| Chega a um servidor de entrada (ingest) | Wowza (acima: "Media servers ingest the stream from the encoder") · getstream.io (acima: "send RTMP to your ingest server") · guias de stream key do TikTok LIVE (servidor RTMP de entrada) https://restream.io/learn/platforms/how-to-find-tiktok-stream-key/ | ✅ |
| Lá vira várias versões (alta, média, baixa) — transcodificação | Akamai (acima: "creates multiple video file versions") · getstream.io (acima: "transcoded into multiple bitrates") · Wowza ("different resolutions ... different bitrates") | ✅ |
| Internet boa recebe a alta; sinal fraco recebe a leve e a live continua (bitrate adaptativo) | Wowza (o player escolhe a versão pela tela e pela banda — ABR) · Wikipedia — Adaptive bitrate streaming https://en.wikipedia.org/wiki/Adaptive_bitrate_streaming (detecta a banda do usuário em tempo real e ajusta a qualidade) | ✅ |
| O celular manda um vídeo só; cópias ficam em servidores perto de quem assiste (CDN); quem assiste puxa do mais perto | Akamai (acima: "accessed from servers that are closest to users") · Wowza (acima: "The servers closest to the viewer are called edge servers") · getstream.io ("scales to millions of viewers because CDNs are designed for this") | ✅ |
| "E o seu celular nem sente" (mais espectadores não aumentam o envio do streamer) | consequência direta das linhas acima: o streamer envia 1 fluxo ao ingest e a distribuição é da CDN (Wowza; getstream.io) | ✅ |
| Mensagens e presentes vão por outro caminho, separado do vídeo, e chegam quase em tempo real | getstream.io ("The data plane runs parallel to media, usually over WebSocket"; "arrive in near-real-time", o vídeo atrasa) · Amazon IVS Chat — "a managed, live-chat feature to go alongside live video streams", API de mensagens por WebSocket https://docs.aws.amazon.com/ivs/latest/ChatUserGuide/what-is.html | ✅ (dito de forma geral; "presentes" = eventos do mesmo canal de dados, como reações) |

Descartado (fonte única ou não pública): endereço exato do servidor RTMP do TikTok; "o comentário pode chegar antes da imagem"
(só getstream.io); qualquer número de latência, de espectadores ou de ganhos do programa de incentivo.

**Conformidade:** nenhum logotipo, tela, ícone ou nome de botão real do TikTok além da expressão genérica "Iniciar LIVE";
interface do celular 100 % própria (botão vermelho genérico). Nenhum rosto real: o mascote original Pixel faz o streamer.
Convite final amigável ("Que tal fazer a sua primeira LIVE?") sem prometer dinheiro, seguidores ou números.
Selo "Conteúdo gerado com IA" na tela (padrão do compor).
