#!/usr/bin/env bash
# v17 batch (FEEDBACK_v15): part-1 segments (render_one.sh), then part-2 (render_v15.sh), then assemble_v17.py.
#   nohup bash render_v17.sh > "E:/YTP2/3D Timelapse/logs/render_v17.log" 2>&1 &
HERE="$(cd "$(dirname "$0")" && pwd)"; cd "$HERE"
bash render_one.sh g2:g2_armored_v9 g3:g3_flight_v14 g5:g5_trost_v13 g6:g6_hq_v10 g7:g7_basin_v7 g8:g8_boulder_v9
NO_ASSEMBLE=1 bash render_v15.sh f1:v13 f2:v11 f3v17:v1
python assemble_v17.py --wait
echo "[v17] ALL DONE $(date +%T)"
