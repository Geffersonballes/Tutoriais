#!/bin/bash
# render completo (REALISTA=1, PASSO=2, 2 processos) dentro da trava de CPU, depois monta o final.mp4
cd /home/user/Tutoriais
P=tiktok-geopolitica/producao/2026-11-25_inspetores-nucleares
flock /tmp/render.lock bash -c "echo INICIO \$(date) > $P/render_estado.txt; REALISTA=1 PASSO=2 blender -b --factory-startup -P tiktok-geopolitica/motor/cena_nuclear.py -- $P range 1,2376 > $P/render_a.log 2>&1 & REALISTA=1 PASSO=2 blender -b --factory-startup -P tiktok-geopolitica/motor/cena_nuclear.py -- $P range 2377,4752 > $P/render_b.log 2>&1 & wait; echo FIM \$(date) >> $P/render_estado.txt"
python3 tiktok-geopolitica/motor/compor.py $P $P/grafismos.json > $P/compor.log 2>&1 && echo COMPOSTO $(date) >> $P/render_estado.txt || echo ERRO_COMPOR $(date) >> $P/render_estado.txt
