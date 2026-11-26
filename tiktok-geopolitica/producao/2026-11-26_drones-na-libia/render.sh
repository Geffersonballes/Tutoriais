#!/bin/bash
# render completo (REALISTA=1, PASSO=2, 2 processos) dentro da trava de CPU; faixas pela duração real (2692 quadros)
cd /home/user/Tutoriais
P=tiktok-geopolitica/producao/2026-11-26_drones-na-libia
flock /tmp/render.lock bash -c "echo INICIO \$(date) > $P/render_estado.txt; REALISTA=1 PASSO=2 blender -b --factory-startup -P tiktok-geopolitica/motor/cena_libia.py -- $P range 1,1346 > $P/render_a.log 2>&1 & REALISTA=1 PASSO=2 blender -b --factory-startup -P tiktok-geopolitica/motor/cena_libia.py -- $P range 1347,2692 > $P/render_b.log 2>&1 & wait; echo FIM \$(date) >> $P/render_estado.txt"
