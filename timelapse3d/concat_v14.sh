#!/usr/bin/env bash
# v14 (FEEDBACK_v13 §1 "NO transition effect: one natural continuous take"): plain concat of segment previews (every input
# scaled to 854x480 / 15 fps), + 1 frame per 5 s contact sheet.   bash concat_v14.sh OUT.mp4 in1.mp4 in2.mp4 ...
out="$1"; shift
args=(); fc=""; n=0
for f in "$@"; do args+=(-i "$f"); fc="$fc[$n:v]scale=854:480,fps=15,setsar=1,format=yuv420p[v$n];"; n=$((n+1)); done
for i in $(seq 0 $((n-1))); do fc="$fc[v$i]"; done
fc="${fc}concat=n=$n:v=1:a=0[o]"
ffmpeg -hide_banner -loglevel error -y "${args[@]}" -filter_complex "$fc" -map "[o]" -c:v libx264 -crf 30 -pix_fmt yuv420p "$out"
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$out"); ROWS=$(python -c "import math; print(math.ceil($D / 5 / 10))")
ffmpeg -hide_banner -loglevel error -y -i "$out" -vf "fps=1/5,scale=192:-1,tile=10x$ROWS" -frames:v 1 -q:v 5 "${out%_preview.mp4}_sheet.jpg"
echo "$out $D"
