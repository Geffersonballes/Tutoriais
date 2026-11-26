#!/bin/bash
# Aplica o ANTI-BORDA (vinheta suave + grão leve) num vídeo já pronto, para reposts/vídeos antigos.
# Uso: anti_borda_video.sh entrada.mp4 saida.mp4   (o compor.py já faz isso nos vídeos novos)
set -e
ffmpeg -v error -y -i "$1" -vf "vignette=a=PI/4.5,noise=alls=4:allf=u" -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p -profile:v high -c:a copy -movflags +faststart "$2"
