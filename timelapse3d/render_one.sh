#!/usr/bin/env bash
# Autopilot 10/28: render ONE part-1 segment preview (480p 15 fps, VCLOCK, TOON off, GPU lock inside the render scripts),
# copy preview + sheet to renders/laptop/<label>_*, commit + push.  Specs run in order:
#   nohup bash render_one.sh g1:g1_fall_v7 g3:g3_flight_v8 > "E:/YTP2/3D Timelapse/logs/render_one.log" 2>&1 &
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"; cd "$HERE"
RD="E:/YTP2/3D Timelapse/renders"; LG="/e/YTP2/3D Timelapse/logs"; LAP="$HERE/renders/laptop"
BR=claude/project-thread-4b2beh
export TOON=0
for spec in "$@"; do
  g=${spec%%:*}; lab=${spec#*:}
  echo "[one] $g -> $lab start $(date +%T)"
  rm -rf "$RD/$lab/frames"
  if [ "$g" = g1 ]; then
    VCLOCK=1 OUTR="$RD/$lab" bash render_g1.sh > "$LG/$lab.log" 2>&1
  else
    VCLOCK=1 SEG=$g OUT="$RD/$lab" bash render_seg.sh > "$LG/$lab.log" 2>&1
  fi
  if cp "$RD/$lab/${g}_preview.mp4" "$LAP/${lab}_preview.mp4" && cp "$RD/$lab/${g}_sheet.jpg" "$LAP/${lab}_sheet.jpg"; then
    git add "$LAP/${lab}_preview.mp4" "$LAP/${lab}_sheet.jpg" && git commit -q -m "$lab preview (autopilot QA fixes, TOON off)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- "$LAP/${lab}_preview.mp4" "$LAP/${lab}_sheet.jpg" \
      && git pull -q --rebase --autostash origin $BR && git push -q origin $BR && echo "[one] pushed $lab $(date +%T)" \
      || echo "[one] push FAILED $lab"
  else echo "[one] $g FAILED $(date +%T) (see $LG/$lab.log)"; fi
done
echo "[one] ALL DONE $(date +%T)"
