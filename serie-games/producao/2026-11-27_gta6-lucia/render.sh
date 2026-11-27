#!/bin/bash
# render completo em 2 metades dentro da trava de CPU (PASSO=2, 8 amostras)
# Retomada: se a máquina reiniciar, rode de novo (bash render.sh): o Blender pula quadros que já existem
cd /home/user/Tutoriais
P=serie-games/producao/2026-11-27_gta6-lucia
C=tiktok-geopolitica/motor/cena_gta6_lucia.py
echo NA_FILA $(date) >> $P/render_estado.txt
flock /tmp/render.lock bash -c "echo INICIO \$(date) >> $P/render_estado.txt; PASSO=2 AMOSTRAS=8 blender -b --factory-startup -P $C -- $P range 1,1130 > $P/render_a.log 2>&1 & PASSO=2 AMOSTRAS=8 blender -b --factory-startup -P $C -- $P range 1131,2260 > $P/render_b.log 2>&1 & wait; echo FIM \$(date) >> $P/render_estado.txt"
