#!/bin/bash
# render completo em 2 metades dentro da trava de CPU, depois monta o final.mp4
cd /home/user/Tutoriais
P=serie-games/producao/2026-11-26_matchmaking
echo NA_FILA $(date) > $P/render_estado.txt
flock /tmp/render.lock bash -c "echo INICIO \$(date) >> $P/render_estado.txt; PASSO=2 AMOSTRAS=8 blender -b --factory-startup -P tiktok-geopolitica/motor/cena_matchmaking.py -- $P range 1,1124 > $P/render_a.log 2>&1 & PASSO=2 AMOSTRAS=8 blender -b --factory-startup -P tiktok-geopolitica/motor/cena_matchmaking.py -- $P range 1125,2248 > $P/render_b.log 2>&1 & wait; echo FIM \$(date) >> $P/render_estado.txt"
