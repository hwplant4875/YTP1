#!/usr/bin/env bash
# TROST SEGMENT (aot/render_trost.py on the aot/trost.py set + aot/trost_action.py), ONE Blender session per part.
#   PART=1 bash render_trost.sh          parts: 1 = v 0-36, 2 = v 36-72, 3 = v 72-end (108.2 s)  (15 fps, 854x480)
#   STILLS="8.5,14.2,30" bash render_trost.sh       stills only (video seconds) into OUT
#   DRY=1 bash render_trost.sh           build + print the timeline / camera, no render
# Env: ENGINE (CYCLES|BLENDER_EEVEE), SMP (samples), STEP (render every Nth frame; the encode repeats frames)
FPS="${FPS:-15}"; SMP="${SMP:-1}"; STEP="${STEP:-2}"; PART="${PART:-1}"
HERE="$(cd "$(dirname "$0")" && pwd)"
OUT="${OUT:-E:/YTP2/3D Timelapse/renders/trost}"
case "$PART" in 1) V0=0; V1=36;; 2) V0=36; V1=72;; 3) V0=72; V1=999;; esac
[ -n "$WIN" ] && V0=${WIN%,*} && V1=${WIN#*,}
FR="$OUT/frames_p$PART"; mkdir -p "$OUT"; rm -f "$FR/_done"
EXTRA="--v0 $V0 --v1 $V1 --step $STEP"
if [ -n "$STILLS" ]; then EXTRA="--stills $STILLS"; FR="$OUT"; elif [ -z "$DRY" ] && [ -z "$WIN" ]; then rm -rf "$FR"; mkdir -p "$FR"; fi
[ -n "$DRY" ] && EXTRA="$EXTRA --dry"
LOCK="/e/YTP2/3D Timelapse/.gpu_lock"
until mkdir "$LOCK" 2>/dev/null; do sleep 5; done
trap 'rmdir "$LOCK" 2>/dev/null' EXIT
BL="/c/All The Programs/Blender/blender.exe"
for TRY in 1 2 3; do
TA_PSCALE=${TA_PSCALE:-1.0} SUN_AZ=${SUN_AZ:--102} TA_FLOOD=${TA_FLOOD:-30} TA_FLOOD_GAP=${TA_FLOOD_GAP:-0.22} TREE_DENS=${TREE_DENS:-0.005} COL_H=${COL_H:-64} COL_DX=${COL_DX:--7} AOT_SET=trost AOT_PLUGINS=${RT_PLUGINS:-colossal_asset,world} \
  "$BL" -b -P "$HERE/aot/scene.py" -P "$HERE/aot/render_trost.py" -- \
  --year 850 --cam trost_overview --engine ${ENGINE:-BLENDER_EEVEE} --res 854x480 --samples $SMP \
  --rt-out "$FR" --fps $FPS --rt-samples $SMP $EXTRA 2>&1 \
  | grep --line-buffered -E "\[trost\]|\[trost_action\]|\[plugin|Traceback|Error|error:|line [0-9]+"
[ -n "$STILLS" ] || [ -n "$DRY" ] && break
[ -f "$FR/_done" ] && break
echo "[trost] blender exited early (try $TRY), resuming"
done
rmdir "$LOCK" 2>/dev/null
[ -n "$STILLS" ] || [ -n "$DRY" ] && exit 0
# frames are rt_<global index>; STEP > 1 leaves gaps -> repeat the last rendered frame
python - "$FR" "$STEP" <<'PY'
import os, sys, shutil, glob
d, step = sys.argv[1], int(sys.argv[2])
fs = sorted(glob.glob(os.path.join(d, "rt_*.png")))
if fs and step > 1:
    a, b = int(fs[0][-9:-4]), int(fs[-1][-9:-4]) + step - 1
    last = fs[0]
    for f in range(a, b + 1):
        p = os.path.join(d, f"rt_{f:05d}.png")
        if os.path.exists(p): last = p
        else: shutil.copyfile(last, p)
PY
FIRST=$(ls "$FR" | grep "^rt_" | head -1 | sed 's/rt_0*\([0-9]\)/\1/; s/\.png//'); [ -z "$FIRST" ] && FIRST=0
ffmpeg -hide_banner -loglevel error -y -framerate $FPS -start_number $FIRST -i "$FR/rt_%05d.png" -c:v libx264 -crf 26 -pix_fmt yuv420p "$OUT/trost_part$PART.mp4"
ls -la "$OUT/trost_part$PART.mp4"
