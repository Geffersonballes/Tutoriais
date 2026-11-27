#!/bin/bash
# re-render do bloco 2 (Pixel mais longe da câmera, dissipador desce em "leva"); quadros 561–929, retomável
cd /home/user/Tutoriais
P=serie-games/producao/2026-11-27_gta6-consoles
C=tiktok-geopolitica/motor/cena_gta6_consoles.py
echo NA_FILA refazer_bloco2 $(date) >> $P/render_estado.txt
flock /tmp/render.lock bash -c "echo INICIO refazer_bloco2 \$(date) >> $P/render_estado.txt; PASSO=2 AMOSTRAS=8 blender -b --factory-startup -P $C -- $P range 561,745 > $P/render_a.log 2>&1 & PASSO=2 AMOSTRAS=8 blender -b --factory-startup -P $C -- $P range 747,929 > $P/render_b.log 2>&1 & wait; echo FIM refazer_bloco2 \$(date) >> $P/render_estado.txt"
