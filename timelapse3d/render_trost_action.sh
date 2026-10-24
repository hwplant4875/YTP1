#!/usr/bin/env bash
# Trost action layer test preview (aot/trost_action.py) on the Shiganshina stand-in, ONE Blender session, Cycles GPU.
#   bash render_trost_action.sh                       all shots, 15 fps, 854x480 -> renders/trost_action/trost_action_preview.mp4
#   STILLS="eaten:0.7,cannon:0.5" bash render_trost_action.sh    stills only (shot:fraction), written into OUT
#   SHOTS="lift,cannon" SPEED=0.5 bash render_trost_action.sh    a subset, shorter
FPS="${FPS:-15}"; SMP="${SMP:-2}"
HERE="$(cd "$(dirname "$0")" && pwd)"
OUT="${OUT:-E:/YTP2/3D Timelapse/renders/trost_action}"
FR="$OUT/frames"; mkdir -p "$OUT"
[ -z "$STILLS" ] && rm -rf "$FR"; mkdir -p "$FR"
EXTRA=""
[ -n "$STILLS" ] && EXTRA="$EXTRA --stills $STILLS" && FR="$OUT"
[ -n "$SHOTS" ] && EXTRA="$EXTRA --shots $SHOTS"
LOCK="/e/YTP2/3D Timelapse/.gpu_lock"
until mkdir "$LOCK" 2>/dev/null; do sleep 5; done
trap 'rmdir "$LOCK" 2>/dev/null' EXIT
BL="/c/All The Programs/Blender/blender.exe"
"$BL" -b -P "$HERE/aot/scene.py" -P "$HERE/aot/render_trost_action.py" -- \
  --year 850 --cam overview --engine ${ENGINE:-CYCLES} --res 854x480 --samples $SMP \
  --ta-out "$FR" --fps $FPS --ta-samples $SMP --speed "${SPEED:-1.0}" $EXTRA 2>&1 \
  | grep -E "\[ta\]|\[trost_action\]|Traceback|Error|error:|line [0-9]+"
rmdir "$LOCK" 2>/dev/null
[ -n "$STILLS" ] && exit 0
ffmpeg -hide_banner -loglevel error -y -framerate $FPS -i "$FR/ta_%05d.png" -c:v libx264 -crf 26 -pix_fmt yuv420p "$OUT/trost_action_preview.mp4"
ls -la "$OUT/trost_action_preview.mp4"
