#!/usr/bin/env bash
# MASTER v2 BATCH RENDER QUEUE (owner 11:19 / 20:40: edit first, render everything later in ONE queue).  Prepared, NOT run.
# Renders the part-1 segments one after another (480p 15 fps previews, video clock, TOON off, GPU lock inside the render
# scripts), copies each preview + 2 fps sheet to renders/laptop/ with its version label, then concatenates master v2.
#   bash render_queue_master_v2.sh                 everything still missing (segments whose laptop preview exists are skipped)
#   FORCE=1 bash render_queue_master_v2.sh         re-render every segment
#   ONLY="g3 g5" bash render_queue_master_v2.sh    just these segments (+ the master concat)
#   NOMASTER=1 ...                                 skip the master concat
# Start it DETACHED so it survives the session:  nohup bash render_queue_master_v2.sh > "E:/YTP2/3D Timelapse/logs/queue_master_v2.log" 2>&1 &
# Per-segment logs: E:/YTP2/3D Timelapse/logs/<label>.log.  After it finishes: git add renders/laptop/<labels>* + push.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
RD="E:/YTP2/3D Timelapse/renders"; LG="/e/YTP2/3D Timelapse/logs"; LAP="$HERE/renders/laptop"
mkdir -p "$LG"
export TOON=0
# segment : version label (bump the label when the segment's code changes again)
SEGS="g1:g1_fall_v5 g2:g2_armored_v5 g3:g3_flight_v6 g4:g4_trost850_v4 g5:g5_trost_v4 g6:g6_hq_v4 g7:g7_basin_v3 g8:g8_boulder_v3"
want() { [ -z "${ONLY:-}" ] && return 0; case " $ONLY " in *" $1 "*) return 0;; esac; return 1; }
cd "$HERE"
for spec in $SEGS; do
  g=${spec%%:*}; lab=${spec#*:}
  want "$g" || continue
  if [ -z "${FORCE:-}" ] && [ -f "$LAP/${lab}_preview.mp4" ]; then echo "[queue] $g skip ($lab exists)"; continue; fi
  echo "[queue] $g -> $lab start $(date +%T)"
  if [ "$g" = g1 ]; then
    rm -rf "$RD/$lab/frames"
    VCLOCK=1 OUTR="$RD/$lab" bash render_g1.sh > "$LG/$lab.log" 2>&1
    src_mp4="$RD/$lab/g1_preview.mp4"; src_jpg="$RD/$lab/g1_sheet.jpg"
  else
    rm -rf "$RD/$lab/frames"
    VCLOCK=1 SEG=$g OUT="$RD/$lab" bash render_seg.sh > "$LG/$lab.log" 2>&1
    src_mp4="$RD/$lab/${g}_preview.mp4"; src_jpg="$RD/$lab/${g}_sheet.jpg"
  fi
  if cp "$src_mp4" "$LAP/${lab}_preview.mp4" && cp "$src_jpg" "$LAP/${lab}_sheet.jpg"; then echo "[queue] $g DONE $(date +%T)"
  else echo "[queue] $g FAILED $(date +%T) (see $LG/$lab.log)"; fi
done
[ -n "${NOMASTER:-}" ] && { echo "[queue] ALL DONE (no master)"; exit 0; }
# ---- master one-take v2 preview: concat of the 8 previews (no HUD overlay), sheet = 1 frame / 5 s
T="$RD/master_v2"; mkdir -p "$T"; : > "$T/list.txt"
for spec in $SEGS; do
  lab=${spec#*:}
  [ -f "$LAP/${lab}_preview.mp4" ] || { echo "[queue] master: MISSING $lab"; exit 1; }
  echo "file '$(cygpath -m "$LAP/${lab}_preview.mp4")'" >> "$T/list.txt"
done
ffmpeg -hide_banner -loglevel error -y -f concat -safe 0 -i "$T/list.txt" -c:v libx264 -crf 28 -r 15 -pix_fmt yuv420p "$LAP/master_onetake_v2_preview.mp4"
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$LAP/master_onetake_v2_preview.mp4")
ROWS=$(python -c "import math; print(math.ceil($D / 5 / 8))")
ffmpeg -hide_banner -loglevel error -y -i "$LAP/master_onetake_v2_preview.mp4" -vf "fps=1/5,scale=240:-1,tile=8x$ROWS" -frames:v 1 -q:v 5 "$LAP/master_onetake_v2_sheet.jpg"
echo "[queue] master v2 ${D}s -> $LAP/master_onetake_v2_preview.mp4 + _sheet.jpg"
echo "[queue] ALL DONE"
