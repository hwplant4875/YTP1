#!/usr/bin/env bash
# Low-quality one-take intro test (EEVEE 854x480), compressed timelapse pacing, then H.264.
#   bash render_intro.sh [samples=8]
SMP="${1:-8}"; STEP="${2:-1}"; FPS=$((30 / STEP)); LITE="${3:-}"   # bash render_intro.sh 2 3 --intro-lite  = 10 fps quick preview
HERE="$(cd "$(dirname "$0")" && pwd)"; OUT="E:/YTP2/3D Timelapse/renders/intro_test"
rm -rf "$OUT"; mkdir -p "$OUT"
LOCK="/e/YTP2/3D Timelapse/.gpu_lock"
until mkdir "$LOCK" 2>/dev/null; do sleep 5; done
trap 'rmdir "$LOCK" 2>/dev/null' EXIT
B="/c/All The Programs/Blender/blender.exe"
P=seq_colossal,flight,cast845,states845,colossal_asset,seq_colossal
# part 1: tree -> swoosh to plaza -> head -> orbit -> wind-up (gate intact); 30 fps, 1 seq frame per video frame
SEQ_F=1100 COL_SHOW=1 AOT_STATE=intact AOT_EVENT=intact AOT_PLUGINS=$P "$B" -b -P "$HERE/aot/scene.py" -P "$HERE/aot/render_intro.py" -- \
  --cam seq --engine EEVEE --res 854x480 --samples $SMP --intro-out "$OUT" --intro-from 840 --intro-to 1169 --intro-step $STEP --intro-speed 840:1 $LITE --intro-samples $SMP 2>&1 \
  | grep -E "\[intro\]|Traceback|Error" | tail -3
N=$(ls "$OUT" | wc -l)
# part 2: impact onwards (gate kicked in, blocks landed)
SEQ_F=1230 COL_SHOW=1 AOT_STATE=kicked AOT_ARC_T=1 AOT_PLUGINS=$P "$B" -b -P "$HERE/aot/scene.py" -P "$HERE/aot/render_intro.py" -- \
  --cam seq --engine EEVEE --res 854x480 --samples $SMP --intro-out "$OUT" --intro-from 1170 --intro-to 1360 --intro-step $STEP --intro-speed 840:1 $LITE --intro-samples $SMP --intro-index0 $N 2>&1 \
  | grep -E "\[intro\]|Traceback|Error" | tail -3
ffmpeg -hide_banner -loglevel error -y -framerate $FPS -i "$OUT/intro_%05d.png" -c:v libx264 -crf 26 -pix_fmt yuv420p "E:/YTP2/3D Timelapse/renders/intro_test_480p.mp4"
ls -la "E:/YTP2/3D Timelapse/renders/intro_test_480p.mp4"
