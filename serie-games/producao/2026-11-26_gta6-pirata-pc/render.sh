#!/bin/bash
# render completo em 2 metades dentro da trava de CPU (PASSO=2, 8 amostras)
# Retomada: se houver frames, renderiza só os que faltam (RETOMAR=1 bash render.sh)
cd /home/user/Tutoriais
P=serie-games/producao/2026-11-26_gta6-pirata-pc
C=tiktok-geopolitica/motor/cena_gta6_pirata_pc.py
echo NA_FILA $(date) >> $P/render_estado.txt
flock /tmp/render.lock bash -c "echo INICIO \$(date) >> $P/render_estado.txt; PASSO=2 AMOSTRAS=8 blender -b --factory-startup -P $C -- $P range 1,1132 > $P/render_a.log 2>&1 & PASSO=2 AMOSTRAS=8 blender -b --factory-startup -P $C -- $P range 1133,2264 > $P/render_b.log 2>&1 & wait; echo FIM \$(date) >> $P/render_estado.txt"
