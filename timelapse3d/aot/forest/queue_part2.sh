#!/usr/bin/env bash
# PART 2-3 FULL RENDER QUEUE (prepared 10/27, NOT started): f0 f1 f2 f3 s1 s2 in order, one after another, each through
# aot/forest/render_part2.sh (TOON=0, GPU lock, 640x360, 15 fps, STEP=2), then the part 2-3 one-take concat, then a
# version-labelled copy + push to renders/laptop/.
#   bash aot/forest/queue_part2.sh                     whole queue (detach it: nohup bash aot/forest/queue_part2.sh &)
#   SEGS="f2 f3" bash aot/forest/queue_part2.sh        a subset (the concat uses whatever previews exist)
#   VER=v2 ...                                          version label for renders/laptop (default v1);  PUSH=0 skips git
# Logs: E:/YTP2/3D Timelapse/logs/p2q_<seg>.log ; queue log p2q_queue.log.  A failed segment is logged and skipped.
cd "$(dirname "$0")/../.."
REPO="$(pwd)"
SEGS="${SEGS:-f0 f1 f2 f3 s1 s2}"
VER="${VER:-v1}"; PUSH="${PUSH:-1}"
export RES="${RES:-640x360}" STEP="${STEP:-2}" FPS="${FPS:-15}" TOON=0
LG="E:/YTP2/3D Timelapse/logs"; RD="E:/YTP2/3D Timelapse/renders/part2"
LAP="$REPO/renders/laptop"; mkdir -p "$LAP" "$RD"
declare -A NAME=( [f0]=f0_trost_karanes [f1]=f1_formation_female [f2]=f2_forest_trap [f3]=f3_duel_rescue [s1]=s1_stohess_shift [s2]=s2_stohess_wall )
say() { echo "[queue] $* $(date +%H:%M:%S)" | tee -a "$LG/p2q_queue.log"; }

for g in $SEGS; do
  say "$g start"
  OUT="$RD/${g}_$VER"
  if SEG=$g OUT="$OUT" bash aot/forest/render_part2.sh > "$LG/p2q_$g.log" 2>&1 && [ -f "$OUT/${g}_preview.mp4" ]; then
    cp "$OUT/${g}_preview.mp4" "$LAP/${NAME[$g]}_${VER}_preview.mp4"
    cp "$OUT/${g}_sheet.jpg" "$LAP/${NAME[$g]}_${VER}_sheet.jpg"
    say "$g DONE"
    if [ "$PUSH" = 1 ]; then
      git add "$LAP/${NAME[$g]}_${VER}_preview.mp4" "$LAP/${NAME[$g]}_${VER}_sheet.jpg" && \
      git commit -q -m "${NAME[$g]} $VER preview (part 2-3, TOON off)" && \
      git pull -q --rebase --autostash && git push -q && say "$g pushed"
    fi
  else
    say "$g FAILED (see p2q_$g.log)"
  fi
done

# one-take concat of every segment preview present, in order
LIST="$RD/concat_$VER.txt"; : > "$LIST"
for g in f0 f1 f2 f3 s1 s2; do
  [ -f "$RD/${g}_$VER/${g}_preview.mp4" ] && echo "file '$RD/${g}_$VER/${g}_preview.mp4'" >> "$LIST"
done
if [ -s "$LIST" ]; then
  ffmpeg -hide_banner -loglevel error -y -f concat -safe 0 -i "$LIST" -c copy "$RD/part2_3_onetake_$VER.mp4" && \
  cp "$RD/part2_3_onetake_$VER.mp4" "$LAP/part2_3_onetake_${VER}_preview.mp4" && say "concat DONE ($(wc -l < "$LIST") segments)"
  if [ "$PUSH" = 1 ] && [ -f "$LAP/part2_3_onetake_${VER}_preview.mp4" ]; then
    git add "$LAP/part2_3_onetake_${VER}_preview.mp4" && git commit -q -m "part 2-3 one-take $VER preview (concat)" && \
    git pull -q --rebase --autostash && git push -q && say "concat pushed"
  fi
fi
say "queue finished"
