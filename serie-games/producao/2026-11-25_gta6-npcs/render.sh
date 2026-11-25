#!/bin/bash
# render completo em 2 processos (metades), dentro da trava de CPU compartilhada
cd /home/user/Tutoriais
flock /tmp/render.lock bash -c 'echo INICIO $(date) > serie-games/producao/2026-11-25_gta6-npcs/render_estado.txt; PASSO=2 AMOSTRAS=8 blender -b --factory-startup -P tiktok-geopolitica/motor/cena_gta_npcs.py -- serie-games/producao/2026-11-25_gta6-npcs range 1,1055 > serie-games/producao/2026-11-25_gta6-npcs/render_a.log 2>&1 & PASSO=2 AMOSTRAS=8 blender -b --factory-startup -P tiktok-geopolitica/motor/cena_gta_npcs.py -- serie-games/producao/2026-11-25_gta6-npcs range 1057,2110 > serie-games/producao/2026-11-25_gta6-npcs/render_b.log 2>&1 & wait; echo FIM $(date) >> serie-games/producao/2026-11-25_gta6-npcs/render_estado.txt'
