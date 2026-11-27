#!/bin/bash
# render completo (REALISTA=1, PASSO=2, 2 processos) dentro da trava de CPU
cd /home/user/Tutoriais
P=tiktok-geopolitica/producao/2026-11-27_refinaria-na-mira
flock /tmp/render.lock bash -c "echo INICIO \$(date) > $P/render_estado.txt; REALISTA=1 PASSO=2 blender -b --factory-startup -P tiktok-geopolitica/motor/cena_refinaria.py -- $P range 1,1340 > $P/render_a.log 2>&1 & REALISTA=1 PASSO=2 blender -b --factory-startup -P tiktok-geopolitica/motor/cena_refinaria.py -- $P range 1341,2682 > $P/render_b.log 2>&1 & wait; echo FIM \$(date) >> $P/render_estado.txt"
