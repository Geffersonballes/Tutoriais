#!/bin/bash
# render completo em 2 metades dentro da trava de CPU, depois monta o final.mp4
cd /home/user/Tutoriais
P=serie-games/producao/2026-11-25_gta6-npcs
flock /tmp/render.lock bash -c "echo INICIO \$(date) > $P/render_estado.txt; PASSO=2 AMOSTRAS=8 blender -b --factory-startup -P tiktok-geopolitica/motor/cena_gta_npcs.py -- $P range 1,941 > $P/render_a.log 2>&1 & PASSO=2 AMOSTRAS=8 blender -b --factory-startup -P tiktok-geopolitica/motor/cena_gta_npcs.py -- $P range 943,1883 > $P/render_b.log 2>&1 & wait; echo FIM \$(date) >> $P/render_estado.txt"
python3 tiktok-geopolitica/motor/compor.py $P $P/grafismos.json > $P/compor.log 2>&1 && echo COMPOSTO $(date) >> $P/render_estado.txt
