#!/usr/bin/env bash
# Autopilot 10/28: render part 2-3 segment previews one after another (aot/forest/render_part2.sh: TOON 0, GPU lock,
# 854x480, 15 fps, every frame), copy to renders/laptop/<name>_<ver>_*, commit + push.  Specs = seg:ver, e.g.
#   nohup bash render_p2.sh f1:v3 f3:v3 > "E:/YTP2/3D Timelapse/logs/render_p2.log" 2>&1 &
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"; cd "$HERE"
export RES="${RES:-854x480}" STEP="${STEP:-1}" FPS=15 TOON=0
LG="E:/YTP2/3D Timelapse/logs"; RD="E:/YTP2/3D Timelapse/renders/part2"; LAP="$HERE/renders/laptop"
BR=claude/project-thread-4b2beh
declare -A NAME=( [f0]=f0_trost_karanes [f1]=f1_formation_female [f2]=f2_forest_trap [f3]=f3_duel_rescue [s1]=s1_stohess_shift [s2]=s2_stohess_wall )
for spec in "$@"; do
  g=${spec%%:*}; v=${spec#*:}; OUT="$RD/${g}_$v"; nm="${NAME[$g]}_$v"
  echo "[p2] $g -> $nm start $(date +%T)"
  rm -rf "$OUT/frames"
  if SEG=$g OUT="$OUT" bash aot/forest/render_part2.sh > "$LG/p2_${g}_$v.log" 2>&1 && [ -f "$OUT/${g}_preview.mp4" ]; then
    cp "$OUT/${g}_preview.mp4" "$LAP/${nm}_preview.mp4"; cp "$OUT/${g}_sheet.jpg" "$LAP/${nm}_sheet.jpg"
    git add "$LAP/${nm}_preview.mp4" "$LAP/${nm}_sheet.jpg" && git commit -q -m "$nm preview (autopilot QA fixes, 480p, TOON off)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- "$LAP/${nm}_preview.mp4" "$LAP/${nm}_sheet.jpg" \
      && git pull -q --rebase --autostash origin $BR && git push -q origin $BR && echo "[p2] pushed $nm $(date +%T)" \
      || echo "[p2] push FAILED $nm"
  else echo "[p2] $g FAILED $(date +%T) (see $LG/p2_${g}_$v.log)"; fi
done
echo "[p2] ALL DONE $(date +%T)"
