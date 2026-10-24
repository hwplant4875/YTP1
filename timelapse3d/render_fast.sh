#!/usr/bin/env bash
# Fast-paced 13 s opening test (aot/render_fast.py): Cycles GPU 854x480 (EEVEE crashed on this scene), 24 fps, H.264.
#   bash render_fast.sh [samples=8]
SMP="${1:-8}"
HERE="$(cd "$(dirname "$0")" && pwd)"; OUT="E:/YTP2/3D Timelapse/renders/fast_test"
rm -rf "$OUT"; mkdir -p "$OUT"
LOCK="/e/YTP2/3D Timelapse/.gpu_lock"
until mkdir "$LOCK" 2>/dev/null; do sleep 5; done
trap 'rmdir "$LOCK" 2>/dev/null' EXIT
BL="/c/All The Programs/Blender/blender.exe"
P=seq_colossal,flight,cast845,states845,colossal_asset,seq_colossal
run() {  # t0 t1 state arc
  local N; N=$(ls "$OUT" | wc -l)
  TREE_DENS=0.006 SEQ_F=1300 COL_SHOW=1 AOT_STATE=$3 AOT_ARC_T=$4 AOT_EVENT=intact AOT_PLUGINS=$P "$BL" -b -P "$HERE/aot/scene.py" -P "$HERE/aot/render_fast.py" -- \
    --cam seq --engine CYCLES --res 854x480 --samples $SMP --fast-out "$OUT" --t0 $1 --t1 $2 --fast-samples $SMP --index0 $N 2>&1 \
    | grep -E "\[fast\]|Traceback|Error" | tail -2
}
run 0.0 11.0 intact 1
run 11.0 11.125 kicked 0.15
run 11.125 11.292 kicked 0.35
run 11.292 11.5 kicked 0.6
run 11.5 11.75 kicked 0.85
run 11.75 13.0 kicked 1
ffmpeg -hide_banner -loglevel error -y -framerate 24 -i "$OUT/fast_%05d.png" -c:v libx264 -crf 26 -pix_fmt yuv420p "E:/YTP2/3D Timelapse/renders/intro_fast_480p.mp4"
ls -la "E:/YTP2/3D Timelapse/renders/intro_fast_480p.mp4"
