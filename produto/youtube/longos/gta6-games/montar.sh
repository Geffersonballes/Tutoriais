set -e
ENC="-c:v libx264 -preset veryfast -crf 24 -pix_fmt yuv420p -r 30 -c:a aac -b:a 192k -ar 48000 -ac 2"
FR="[0:v]fps=30,split[a][b];[a]scale=1920:-2,crop=1920:1080,boxblur=25:2,eq=brightness=-0.28:saturation=0.7[bg];[b]scale=608:1080[fg];[bg][fg]overlay=656:0[m];[m][1:v]overlay=0:0"
seg(){ # src start dur lat out
  ffmpeg -nostdin -y -v error -ss $2 -t $3 -i $1 -i $4 -filter_complex "$FR[v];[0:a]loudnorm=I=-14:TP=-1.5,aresample=48000[a]" -map "[v]" -map "[a]" $ENC $5; }
card(){ # png dur out
  ffmpeg -nostdin -y -v error -loop 1 -t $2 -i $1 -f lavfi -t $2 -i anullsrc=r=48000:cl=stereo -filter_complex "[0:v]scale=1920:1080,zoompan=z='1+0.0008*on':d=1:s=1920x1080:fps=30,fade=in:0:8,fade=out:st=$(echo "$2-0.3"|bc):d=0.3[v]" -map "[v]" -map 1:a $ENC -shortest $3; }
# intro
i=0; for s in "npcs 20" "fps 30" "twitch 30" "cs2 25" "anti 30"; do set -- $s
 ffmpeg -nostdin -y -v error -ss $2 -t 3.25 -i $1.mp4 -i lat$i.png -f lavfi -t 3.25 -i anullsrc=r=48000:cl=stereo -filter_complex "$FR[v]" -map "[v]" -map 2:a $ENC i$i.mp4; i=$((i+1)); done
printf "file i%d.mp4\n" 0 1 2 3 4 > li.txt; ffmpeg -nostdin -y -v error -f concat -i li.txt -c copy introv.mp4
ffmpeg -nostdin -y -v error -i introv.mp4 -i intro.mp3 -filter_complex "[1:a]loudnorm=I=-14:TP=-1.5,aresample=48000,apad[a]" -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -ar 48000 -ac 2 -shortest s00.mp4
card titulo.png 2.5 s01.mp4
L="s00.mp4 s01.mp4"; n=0
while read f dur; do card card$n.png 2.2 c$n.mp4; seg $f.mp4 0 $dur lat$n.png p$n.mp4; L="$L c$n.mp4 p$n.mp4"; n=$((n+1)); done < segs.txt
ffmpeg -nostdin -y -v error -loop 1 -t 12.5 -i fim.png -i outro.mp3 -filter_complex "[0:v]scale=1920:1080,fps=30,fade=in:0:8[v];[1:a]loudnorm=I=-14:TP=-1.5,aresample=48000,apad[a]" -map "[v]" -map "[a]" $ENC -t 12.5 s99.mp4
L="$L s99.mp4"; printf "file %s\n" $L > lista.txt
ffmpeg -nostdin -y -v error -f concat -i lista.txt -c copy longo.mp4
ffprobe -v error -show_entries format=duration -of csv=p=0 longo.mp4
