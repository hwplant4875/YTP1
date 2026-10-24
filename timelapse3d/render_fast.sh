#!/usr/bin/env bash
# Fast-paced opening (aot/render_fast.py) in ONE Blender session: Cycles GPU 854x480 (EEVEE crashed on this scene), H.264.
# The scene is built once with AOT_STATE=kicked; render_fast calls fx845.update(t - 11) per frame (t < 11 = intact gate),
# so every frame is a pure function of its time and any window / still renders on its own.
#   bash render_fast.sh [samples=8]                 FPS=30 (final) by default, FPS=15 for quick previews
#   T1=15.5 FAST_HOUSE_CAM=12.9 bash render_fast.sh  longer cut incl. the close house-collapse camera (optional)
#   TIMES="0,1.9,4.7,8" bash render_fast.sh 8       stills only, written as fast_tSS.ss.png into OUT
SMP="${1:-8}"; FPS="${FPS:-30}"; T0="${T0:-0.0}"; T1="${T1:-13.0}"
HERE="$(cd "$(dirname "$0")" && pwd)"; OUT="${OUT:-E:/YTP2/3D Timelapse/renders/fast_test}"
[ -z "$TIMES" ] && rm -rf "$OUT"; mkdir -p "$OUT"
LOCK="/e/YTP2/3D Timelapse/.gpu_lock"
until mkdir "$LOCK" 2>/dev/null; do sleep 5; done
trap 'rmdir "$LOCK" 2>/dev/null' EXIT
BL="/c/All The Programs/Blender/blender.exe"
P=seq_colossal,flight,cast845,states845,colossal_asset,seq_colossal
EXTRA=""; [ -n "$TIMES" ] && EXTRA="--times $TIMES"
# FL_FIELD: road / tussocks / trees / bushes on the tree -> gate meadow; FL_KIDS_MODE=seated: Eren dozes and bends forward
FL_FIELD=1 FL_KIDS_MODE=seated TREE_DENS=0.006 SEQ_F=1300 COL_SHOW=1 AOT_STATE=kicked AOT_ARC_T=1 AOT_EVENT=intact AOT_PLUGINS=$P \
  "$BL" -b -P "$HERE/aot/scene.py" -P "$HERE/aot/render_fast.py" -- \
  --cam seq --engine CYCLES --res 854x480 --samples $SMP --fast-out "$OUT" --t0 $T0 --t1 $T1 --fps $FPS --fast-samples $SMP $EXTRA 2>&1 \
  | grep -E "\[fast\]|\[flight\] field|Traceback|Error"
[ -n "$TIMES" ] && exit 0
ffmpeg -hide_banner -loglevel error -y -framerate $FPS -i "$OUT/fast_%05d.png" -c:v libx264 -crf 26 -pix_fmt yuv420p "E:/YTP2/3D Timelapse/renders/intro_fast_480p.mp4"
ls -la "E:/YTP2/3D Timelapse/renders/intro_fast_480p.mp4"
