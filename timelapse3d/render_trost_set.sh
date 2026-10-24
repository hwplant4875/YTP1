#!/usr/bin/env bash
# Trost district set (aot/trost.py): sky-view stills in ONE Blender session (scene built once, cameras looped).
#   bash render_trost_set.sh [samples]                 all CAMS of trost.py, 854x480 Cycles GPU (default 4 samples + denoise)
#   CAMS=trost_hq_cut,trost_boulder bash render_trost_set.sh 8
#   RES=1280x720 OUT=/some/dir bash render_trost_set.sh
SMP="${1:-4}"; RES="${RES:-854x480}"
HERE="$(cd "$(dirname "$0")" && pwd)"; OUT="${OUT:-E:/YTP2/3D Timelapse/renders/trost_set}"
mkdir -p "$OUT"
CAMARG=""; [ -n "$CAMS" ] && CAMARG="--cams $CAMS"
LOCK="/e/YTP2/3D Timelapse/.gpu_lock"
until mkdir "$LOCK" 2>/dev/null; do sleep 5; done
trap 'rmdir "$LOCK" 2>/dev/null' EXIT
BL="/c/All The Programs/Blender/blender.exe"
TREE_DENS=${TREE_DENS:-0.006} AOT_SET=trost AOT_PLUGINS="${AOT_PLUGINS:-}" \
  "$BL" -b -P "$HERE/aot/scene.py" -P "$HERE/aot/trost.py" -- \
  --cam trost_overview --engine ${ENGINE:-CYCLES} --res $RES --samples $SMP --stills "$OUT" $CAMARG 2>&1 \
  | grep -E "\[trost\]|\[plugin|Traceback|Error|error:"
ls -la "$OUT"
