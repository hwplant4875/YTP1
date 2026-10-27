#!/usr/bin/env bash
# Autopilot 10/28: tagged copies (<dir>/<seg>_tagged.mp4) of the given segment renders.  Specs = seg:render_dir
#   bash tag_all.sh g3:"E:/YTP2/3D Timelapse/renders/g3_flight_v10" f1:".../part2/f1_v4"
cd "$(dirname "$0")"
for spec in "$@"; do
  g=${spec%%:*}; d=${spec#*:}
  [ -f "$d/${g}_tagged.mp4" ] && [ "$d/${g}_tagged.mp4" -nt "$d/${g}_preview.mp4" ] && { echo "[tag_all] $g up to date"; continue; }
  python tag_burn.py "$g" "$d/frames" "$d/${g}_tagged.mp4" || echo "[tag_all] $g FAILED"
done
echo "[tag_all] DONE"
