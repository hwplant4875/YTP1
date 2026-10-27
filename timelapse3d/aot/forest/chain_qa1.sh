#!/usr/bin/env bash
# QA batch 1 re-render chain (10/27 late): only the segments changed by the QA_batch1_1027.md fixes, 480p/360p 15 fps previews,
# GPU lock inside the render scripts.  Part 1: g1 v6, g3 v7, g4 v5 (camp104), g8 v4 -> master_onetake_v2 re-concat.
# Part 2-3: f1 v2, f3 v2, s1 v2, s2 v2 -> part2_3_onetake_v2 (latest version of each segment).  Every preview is committed
# and pushed as it lands.  Run detached:
#   nohup bash aot/forest/chain_qa1.sh > "E:/YTP2/3D Timelapse/logs/chain_qa1.log" 2>&1 &
cd "$(dirname "$0")/../.."
REPO="$(pwd)"; LAP="$REPO/renders/laptop"; LG="/e/YTP2/3D Timelapse/logs"; RD="E:/YTP2/3D Timelapse/renders/part2"
BR=claude/project-thread-4b2beh
push() {   # $1 = commit message, rest = files
  local msg="$1"; shift
  git add "$@" && git commit -q -m "$msg

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" && git pull -q --rebase --autostash origin $BR && git push -q origin $BR \
    && echo "[chain] pushed: $msg $(date +%H:%M)" || echo "[chain] push FAILED: $msg"
}
echo "[chain] start $(date +%H:%M)"
for spec in g1:g1_fall_v6 g3:g3_flight_v7 g4:g4_trost850_v5 g8:g8_boulder_v4; do
  g=${spec%%:*}; lab=${spec#*:}
  ONLY="$g" NOMASTER=1 bash render_queue_master_v2.sh >> "$LG/queue_qa1.log" 2>&1
  if [ -f "$LAP/${lab}_preview.mp4" ]; then push "$lab preview (QA batch1 fixes, TOON off)" "$LAP/${lab}_preview.mp4" "$LAP/${lab}_sheet.jpg"
  else echo "[chain] $lab FAILED (see $LG/$lab.log)"; fi
done
ONLY="none" bash render_queue_master_v2.sh >> "$LG/queue_qa1.log" 2>&1        # master concat only (all labels exist)
[ -f "$LAP/master_onetake_v2_preview.mp4" ] && push "master_onetake_v2 re-concat (g1 v6, g3 v7, g4 v5, g8 v4)" \
  "$LAP/master_onetake_v2_preview.mp4" "$LAP/master_onetake_v2_sheet.jpg"
SEGS="f1 f3 s1 s2" VER=v2 PUSH=0 bash aot/forest/queue_part2.sh >> "$LG/queue_qa1.log" 2>&1
declare -A NAME=( [f0]=f0_trost_karanes [f1]=f1_formation_female [f2]=f2_forest_trap [f3]=f3_duel_rescue [s1]=s1_stohess_shift [s2]=s2_stohess_wall )
for g in f1 f3 s1 s2; do
  f="$LAP/${NAME[$g]}_v2_preview.mp4"
  [ -f "$f" ] && push "${NAME[$g]} v2 preview (QA batch1 fixes, TOON off)" "$f" "${f%_preview.mp4}_sheet.jpg" || echo "[chain] $g v2 missing"
done
# part 2-3 one-take v2: newest preview of each segment
T="$RD/onetake_v2"; mkdir -p "$T"; : > "$T/list.txt"
for g in f0 f1 f2 f3 s1 s2; do
  p=""; for v in v2 v1; do [ -f "$RD/${g}_$v/${g}_preview.mp4" ] && { p="$RD/${g}_$v/${g}_preview.mp4"; break; }; done
  [ -n "$p" ] && echo "file '$p'" >> "$T/list.txt" || echo "[chain] part2 concat: $g missing"
done
ffmpeg -hide_banner -loglevel error -y -f concat -safe 0 -i "$T/list.txt" -c:v libx264 -crf 28 -r 15 -pix_fmt yuv420p "$LAP/part2_3_onetake_v2_preview.mp4"
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$LAP/part2_3_onetake_v2_preview.mp4")
ROWS=$(python -c "import math; print(math.ceil($D / 5 / 8))")
ffmpeg -hide_banner -loglevel error -y -i "$LAP/part2_3_onetake_v2_preview.mp4" -vf "fps=1/5,scale=240:-1,tile=8x$ROWS" -frames:v 1 -q:v 5 "$LAP/part2_3_onetake_v2_sheet.jpg"
push "part2_3_onetake_v2 concat (f1 v2, f3 v2, s1 v2, s2 v2 + f0/f2 v1), ${D}s" "$LAP/part2_3_onetake_v2_preview.mp4" "$LAP/part2_3_onetake_v2_sheet.jpg"
echo "[chain] DONE $(date +%H:%M)"
