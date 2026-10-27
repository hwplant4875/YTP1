#!/usr/bin/env bash
# PART 2-3 composition check: 2 stills per segment at 480x270 (GPU lock respected by render_part2.sh). Log per segment.
cd "$(dirname "$0")/../.."
LG="E:/YTP2/3D Timelapse/logs"
for spec in "f0:6,12" "f1:21,30" "f2:8,18.5" "f3:22.5,44.8" "s1:18,26" "s2:23,40"; do
  SEG="${spec%%:*}"; ST="${spec#*:}"
  SEG=$SEG STILLS="$ST" RES=480x270 bash aot/forest/render_part2.sh > "$LG/p2_stills270_$SEG.log" 2>&1
done
echo done > "$LG/p2_stills270_DONE"
