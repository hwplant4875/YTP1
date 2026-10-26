#!/usr/bin/env bash
# 846 "retake Wall Maria" march (aot/march846.py + aot/render_march846.py) on the Trost set, ONE Blender session.
#   bash render_march846.sh                       preview: 854x480, 15 fps, Eevee -> renders/march846/march846_preview.mp4
#   TIMES="0,4,8,11,14,17.9" bash render_march846.sh    stills only (march_tSS.ss.png in OUT)
#   FPS=30 RES=1280x720 ENGINE=CYCLES SMP=16 bash render_march846.sh   final-ish
#   MARCH_PLUGINS=world,toon TOON=1   (agent G: world layer on by default for the one-take seams; toon opt-in)
#   MARCH_N=60000 MARCH_TITANS=420 MARCH_WAGONS=1600 (agent counts), SET=march846 = placeholder wall instead of Trost
FPS="${FPS:-15}"; RES="${RES:-854x480}"; ENGINE="${ENGINE:-EEVEE}"; SMP="${SMP:-8}"
T0="${T0:-0}"; T1="${T1:-18}"; SET="${SET:-trost}"
HERE="$(cd "$(dirname "$0")" && pwd)"
OUT="${OUT:-E:/YTP2/3D Timelapse/renders/march846}"
FR="$OUT/frames"; [ -n "$TIMES" ] && FR="$OUT"
mkdir -p "$OUT"; [ -z "$TIMES" ] && rm -rf "$FR"; mkdir -p "$FR"
EXTRA=""; [ -n "$TIMES" ] && EXTRA="--times $TIMES"
LOCK="/e/YTP2/3D Timelapse/.gpu_lock"
until mkdir "$LOCK" 2>/dev/null; do sleep 5; done
trap 'rmdir "$LOCK" 2>/dev/null' EXIT
BL="/c/All The Programs/Blender/blender.exe"
TREE_DENS=${TREE_DENS:-0.003} AOT_SET=$SET AOT_PLUGINS="${MARCH_PLUGINS:-world}" \
  "$BL" -b -P "$HERE/aot/scene.py" -P "$HERE/aot/render_march846.py" -- \
  --year 846 --cam trost_overview --engine $ENGINE --res $RES --samples $SMP \
  --m-out "$FR" --fps $FPS --t0 $T0 --t1 $T1 --m-samples $SMP $EXTRA 2>&1 \
  | grep -E "\[march|\[trost\]|\[plugin|Traceback|Error|error:|line [0-9]+"
rmdir "$LOCK" 2>/dev/null
[ -n "$TIMES" ] && exit 0
ffmpeg -hide_banner -loglevel error -y -framerate $FPS -i "$FR/march_%05d.png" -c:v libx264 -crf 26 -pix_fmt yuv420p "$OUT/march846_preview.mp4"
cp "$FR/march846_alive.json" "$OUT/" 2>/dev/null
ls -la "$OUT/march846_preview.mp4"
