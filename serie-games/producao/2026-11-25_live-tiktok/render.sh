#!/bin/bash
# render completo em 2 processos (metades), PASSO=2 AMOSTRAS=8 — rodar dentro de flock /tmp/render.lock
cd /home/user/Tutoriais
P=serie-games/producao/2026-11-25_live-tiktok
PASSO=2 AMOSTRAS=8 blender -b --factory-startup -P tiktok-geopolitica/motor/cena_live.py -- $P range 1,882 > $P/render_a.log 2>&1 &
PASSO=2 AMOSTRAS=8 blender -b --factory-startup -P tiktok-geopolitica/motor/cena_live.py -- $P range 883,1766 > $P/render_b.log 2>&1 &
wait
echo FIM > $P/render_fim.txt
