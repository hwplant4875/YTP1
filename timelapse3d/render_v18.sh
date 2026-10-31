#!/usr/bin/env bash
# v18 LAST PREVIEW (FEEDBACK_v17): re-render the changed part-1 segments, re-burn every segment's captions, concat g1-g8.
#   nohup bash render_v18.sh > "E:/YTP2/3D Timelapse/logs/render_v18.log" 2>&1 &
HERE="$(cd "$(dirname "$0")" && pwd)"; cd "$HERE"
bash render_one.sh g1:g1_fall_v10 g3:g3_flight_v15 g5:g5_trost_v14 g6:g6_hq_v11 g8:g8_boulder_v10
R="E:/YTP2/3D Timelapse/renders"
rm -f "$R"/g2_armored_v9/g2_tagged.mp4 "$R"/g4_trost850_v9/g4_tagged.mp4 "$R"/g7_basin_v7/g7_tagged.mp4
python assemble_v18.py --wait
echo "[v18] ALL DONE $(date +%T)"
