#!/usr/bin/env bash
# Autopilot 10/28: part 1 master concat with a 0.6 s dissolve at the g2|g3 seam only (g2's canal/river set and g3's world
# river differ, the camera seam itself matches).  Inputs in order g1..g8 (854x480 / 15 fps after scaling).
#   bash concat_master.sh OUT.mp4 g1.mp4 g2.mp4 g3.mp4 ... g8.mp4
out="$1"; shift
args=(); fc=""; n=0
for f in "$@"; do args+=(-i "$f"); fc="$fc[$n:v]scale=854:480,fps=15,setsar=1,format=yuv420p[v$n];"; n=$((n+1)); done
d2=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$2")
off=$(python -c "print(round($d2 - 0.6, 3))")
fc="$fc[v1][v2]xfade=transition=fade:duration=0.6:offset=$off[x12];[v0][x12]"
for i in $(seq 3 $((n-1))); do fc="$fc[v$i]"; done
fc="${fc}concat=n=$((n-1)):v=1:a=0[o]"
ffmpeg -hide_banner -loglevel error -y "${args[@]}" -filter_complex "$fc" -map "[o]" -c:v libx264 -crf 28 -pix_fmt yuv420p "$out"
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$out"); ROWS=$(python -c "import math; print(math.ceil($D / 5 / 10))")
ffmpeg -hide_banner -loglevel error -y -i "$out" -vf "fps=1/5,scale=192:-1,tile=10x$ROWS" -frames:v 1 -q:v 5 "${out%_preview.mp4}_sheet.jpg"
echo "$out $D"
