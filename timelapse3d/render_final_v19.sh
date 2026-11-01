#!/usr/bin/env bash
# FINAL (owner 11/01 "그렇게 수정하고 최종본 렌더해줘"): the v19 cut (g1-g8, ends on the three walls), no on-screen text
# except the 846 counter, 1920x1080, 30 fps, every frame, TOON 0, Eevee SMP 8.  Resumable (segment scripts skip frames
# already on disk).  Output: renders/final/aot_ep1_final_1080p30.mp4 (+ a 480p copy + sheet, those two pushed).
#   nohup bash render_final_v19.sh > "E:/YTP2/3D Timelapse/logs/final_v19.log" 2>&1 &
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"; cd "$HERE"
FR="E:/YTP2/3D Timelapse/renders/final"; mkdir -p "$FR"
export TOON=0 FPS=30 STEP=1 RES=1920x1080 SMP="${SMP:-8}" TAG_TEXT=counter_only
LIST="$FR/concat_v19.txt"; : > "$LIST"
for g in g1 g2 g3 g4 g5 g6 g7 g8; do
  echo "[final] $g start $(date +%T)"
  if [ "$g" = g1 ]; then VCLOCK=1 OUTR="$FR/g1" bash render_g1.sh > "$FR/$g.log" 2>&1
  else VCLOCK=1 SEG=$g OUT="$FR/$g" bash render_seg.sh > "$FR/$g.log" 2>&1; fi
  python tag_burn.py $g "$FR/$g/frames" "$FR/$g/${g}_final.mp4" --size 1920x1080 --fps 30 >> "$FR/$g.log" 2>&1
  if [ -f "$FR/$g/${g}_final.mp4" ]; then echo "file '$FR/$g/${g}_final.mp4'" >> "$LIST"; echo "[final] $g done $(date +%T)"
  else echo "[final] $g FAILED $(date +%T) (see $FR/$g.log)"; fi
done
OUT="$FR/aot_ep1_final_1080p30.mp4"
ffmpeg -v error -y -f concat -safe 0 -i "$LIST" -vf "scale=1920:1080,fps=30" -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p "$OUT" \
  && echo "[final] 1080p DONE $OUT $(date +%T)"
ffmpeg -v error -y -i "$OUT" -vf scale=854:480 -c:v libx264 -crf 26 -pix_fmt yuv420p "$FR/aot_ep1_final_480p.mp4"
ffmpeg -v error -y -i "$OUT" -vf "fps=1/6,scale=320:-2,tile=6x6" -frames:v 1 "$FR/aot_ep1_final_sheet.jpg"
LAP="$HERE/renders/laptop"; cp "$FR/aot_ep1_final_480p.mp4" "$FR/aot_ep1_final_sheet.jpg" "$LAP/"
git add "$LAP/aot_ep1_final_480p.mp4" "$LAP/aot_ep1_final_sheet.jpg" && git commit -q -m "FINAL aot ep1 (480p copy + sheet of the 1080p30 master)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- "$LAP/aot_ep1_final_480p.mp4" "$LAP/aot_ep1_final_sheet.jpg" \
  && git pull -q --rebase --autostash origin claude/project-thread-4b2beh && git push -q origin claude/project-thread-4b2beh && echo "[final] pushed 480p + sheet"
echo "[final] ALL DONE $(date +%T)"
