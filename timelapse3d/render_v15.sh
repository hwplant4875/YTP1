#!/usr/bin/env bash
# v15 batch (10/31): changed segments one after another (GPU lock, 854x480, 15 fps, TOON 0), copy to renders/laptop, push;
# then assemble_v15.py (full one-take + sheet + key moments).   nohup bash render_v15.sh f1:v11 s1v15:v1 s2v15:v1 > "E:/YTP2/3D Timelapse/logs/render_v15.log" 2>&1 &
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"; cd "$HERE"
export RES="${RES:-854x480}" STEP="${STEP:-1}" FPS=15 TOON=0
LG="E:/YTP2/3D Timelapse/logs"; RD="E:/YTP2/3D Timelapse/renders/part2"; LAP="$HERE/renders/laptop"
BR=claude/project-thread-4b2beh
declare -A NAME=( [f0]=f0_trost_karanes [f1]=f1_formation_female [f2]=f2_forest_trap [f3]=f3_duel_rescue [s1v15]=s1v15_stohess_sky [s2v15]=s2v15_stohess_cathedral [f3v17]=f3v17_forest_sky )
for spec in "$@"; do
  g=${spec%%:*}; v=${spec#*:}; OUT="$RD/${g}_$v"; nm="${NAME[$g]}_$v"
  echo "[v15] $g -> $nm start $(date +%T)"
  rm -rf "$OUT/frames"
  if SEG=$g OUT="$OUT" bash aot/forest/render_part2.sh > "$LG/v15_${g}_$v.log" 2>&1 && [ -f "$OUT/${g}_preview.mp4" ]; then
    cp "$OUT/${g}_preview.mp4" "$LAP/${nm}_preview.mp4"; cp "$OUT/${g}_sheet.jpg" "$LAP/${nm}_sheet.jpg"
    git add "$LAP/${nm}_preview.mp4" "$LAP/${nm}_sheet.jpg" && git commit -q -m "$nm preview (v15, 480p, TOON off)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- "$LAP/${nm}_preview.mp4" "$LAP/${nm}_sheet.jpg" \
      && git pull -q --rebase --autostash origin $BR && git push -q origin $BR && echo "[v15] pushed $nm $(date +%T)" \
      || echo "[v15] push FAILED $nm"
  else echo "[v15] $g FAILED $(date +%T) (see $LG/v15_${g}_$v.log)"; fi
done
[ -z "${NO_ASSEMBLE:-}" ] && python "${ASSEMBLE:-assemble_v15.py}" --wait
echo "[v15] ALL DONE $(date +%T)"
