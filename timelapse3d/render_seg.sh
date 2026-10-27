#!/usr/bin/env bash
# GENERIC TROST SEGMENT RENDER (aot/render_seg.py + aot/seg_<SEG>.py on the aot/trost.py set), 854x480, 15 fps, Eevee, toon.
#   SEG=g8 bash render_seg.sh                     whole segment: windows of WINLEN s, one Blender run each, then encode
#   SEG=g8 WIN=0,25 bash render_seg.sh            one window only (frames kept; add ENCODE=1 to encode afterwards)
#   SEG=g8 STILLS="12,30" bash render_seg.sh      stills (local seconds) into $OUT/stills
#   SEG=g8 ENCODE_ONLY=1 bash render_seg.sh       frame repeat + mp4 + 2 fps contact sheet from the frames already rendered
#   SEG=g8 CHECK=1 bash render_seg.sh             build, camchan.check + the module's check(), no render (no GPU lock)
#   SEG=g8 DRY=1 bash render_seg.sh               build, checks, a few timed update() calls, no render
# Env: STEP (render every Nth frame, default 2; frames are repeated before the encode), WINLEN (s per Blender run, default 25),
#      FPS (15), SMP (Eevee TAA samples, 1), ENGINE (BLENDER_EEVEE), OUT (default renders/<SEG>), DUR (default from segtime).
SEG="${SEG:?set SEG=g8 (etc.)}"
# VIDEO CLOCK v3 (owner 10/27: 2x speed, 30 fps): VCLOCK=1 -> FPS 30, DUR = segtime.vdur(SEG), WIN/STILLS in VIDEO seconds,
# segment evaluated at segtime.seg_t (see aot/segtime.py).  Default OUT for VCLOCK is renders/<SEG>_v3.
if [ -n "$VCLOCK" ]; then FPS="${FPS:-30}"; VCARG="--vclock"; OUT="${OUT:-E:/YTP2/3D Timelapse/renders/${SEG}_v3}"; fi
FPS="${FPS:-15}"; SMP="${SMP:-1}"; STEP="${STEP:-2}"; WINLEN="${WINLEN:-25}"
HERE="$(cd "$(dirname "$0")" && pwd)"
OUT="${OUT:-E:/YTP2/3D Timelapse/renders/$SEG}"
FR="$OUT/frames"; mkdir -p "$FR"
BL="/c/All The Programs/Blender/blender.exe"
LOCK="/e/YTP2/3D Timelapse/.gpu_lock"
if [ -n "$VCLOCK" ]; then DUR="${DUR:-$(cd "$HERE/aot" && python -c "import segtime; print(segtime.vdur('$SEG'))")}"
else DUR="${DUR:-$(cd "$HERE/aot" && python -c "import segtime; print(segtime.DUR['$SEG'])")}"; fi
# OPT-IN Shiganshina set (frame W; g2 agent 10/27): SEG_SET=shiganshina (the default for SEG=g2) builds scene.py's own
# Shiganshina 845 with g1's plug-ins + env (AOT_STATE=kicked, Colossal hidden) instead of AOT_SET=trost, and render_seg.py
# runs with SEG_FRAME=W (identity frame, scene.py ground).  Trost segments are unchanged.
SEG_SETVAR=trost; SEG_YEAR="${SEG_YEAR:-850}"
[ "$SEG" = g2 ] && SEG_SET="${SEG_SET:-shiganshina}"
if [ "$SEG_SET" = shiganshina ]; then
  export SEG_FRAME=W FL_FIELD=1 FL_KIDS_MODE=seated FL_NOKIDS= FL_NOGRASS= TREE_DENS=0.006 SEQ_F=1300 COL_SHOW=0 \
    AOT_STATE=kicked AOT_ARC_T=1 AOT_EVENT=intact AOT_YEAGER_XY=-165,-585 CARLA_PERFRAME=1 CARLA_NOKIDS=1 CARLA_NOGORE=1 \
    CARLA_H=1.6 CARLA_TITAN_H=13 CARLA_F=2200 SWARM_TITANS="${SWARM_TITANS:-36}" SWARM_FAN="${SWARM_FAN:-0.95,60}" \
    SWARM_TEND="${SWARM_TEND:-90}" FPS="$FPS"
  SEG_SETVAR=""; SEG_YEAR=845
  SEG_PLUGINS="${SEG_PLUGINS:-seq_colossal,seq_carla,flight,cast845,g1_set,states845,world,seq_colossal,seq_carla}"
  SEG_CAM="${SEG_CAM:-seq}"
fi

run_blender() {   # $1 = output dir (may contain spaces), $2 = extra args, $3 = nolock; GPU lock only while Blender runs
  local SOUT="$1" NOLOCK="$3"
  if [ -z "$NOLOCK" ]; then
    until mkdir "$LOCK" 2>/dev/null; do sleep 5; done
    trap 'rmdir "$LOCK" 2>/dev/null' EXIT
  fi
  AOT_SET=$SEG_SETVAR AOT_PLUGINS=${SEG_PLUGINS:-world} TA_PSCALE=1.0 \
    "$BL" -b -P "$HERE/aot/scene.py" -P "$HERE/aot/render_seg.py" -- \
    --year $SEG_YEAR --cam ${SEG_CAM:-gate} --engine ${ENGINE:-BLENDER_EEVEE} --res 854x480 --samples $SMP \
    --seg "$SEG" --seg-out "$SOUT" --fps $FPS --seg-samples $SMP $VCARG $2 2>&1 \
    | grep --line-buffered -E "\[seg|\[g[0-9]|\[trost\]|\[plugin|Traceback|Error|error:|line [0-9]+|FLAG|peak|  -|camera|t [0-9]"
  if [ -z "$NOLOCK" ]; then rmdir "$LOCK" 2>/dev/null; trap - EXIT; fi
}

if [ -n "$CHECK" ]; then run_blender "$OUT/check" "--check" nolock; exit 0; fi
if [ -n "$DRY" ]; then run_blender "$OUT/check" "--dry" nolock; exit 0; fi
if [ -n "$STILLS" ]; then run_blender "$OUT/stills" "--stills $STILLS"; ls "$OUT/stills" | tail -20; exit 0; fi

if [ -z "$ENCODE_ONLY" ]; then
  if [ -n "$WIN" ]; then
    run_blender "$FR" "--t0 ${WIN%,*} --t1 ${WIN#*,} --step $STEP"
    [ -z "$ENCODE" ] && exit 0
  else
    A=0
    while python -c "import sys; sys.exit(0 if $A < $DUR - 1e-6 else 1)"; do
      Bw=$(python -c "print(min($A + $WINLEN, $DUR))")
      for TRY in 1 2 3; do                       # Blender may die mid-window: resume (frames on disk are skipped)
        run_blender "$FR" "--t0 $A --t1 $Bw --step $STEP"
        [ -f "$FR/_done_${A}_${Bw}" ] && break
        python - "$FR" "$A" "$Bw" <<'PY' && break
import os, sys, glob
d, a, b = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
fs = glob.glob(os.path.join(d, "_done_*"))
ok = any(abs(float(f.split("_")[-2]) - a) < 1e-6 and abs(float(f.split("_")[-1]) - b) < 1e-6 for f in fs)
sys.exit(0 if ok else 1)
PY
        echo "[seg] blender exited early in window $A-$Bw (try $TRY), resuming"
      done
      A=$Bw
    done
  fi
fi

# ---- frame repeat (STEP > 1 leaves gaps), mp4, 2 fps contact sheet
python - "$FR" "$DUR" "$FPS" <<'PY'
import os, sys, shutil
d, dur, fps = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
n = int(round(dur * fps))
last = None
for f in range(n):
    p = os.path.join(d, f"f_{f:05d}.png")
    if os.path.exists(p) and os.path.getsize(p) > 0 and not os.path.islink(p):
        last = p
    elif last is not None:
        shutil.copyfile(last, p)
missing = [f for f in range(n) if not os.path.exists(os.path.join(d, f"f_{f:05d}.png"))]
print(f"[seg] frames 0..{n - 1}: {len(missing)} missing" + (f" (first {missing[:5]})" if missing else ""))
PY
ffmpeg -hide_banner -loglevel error -y -framerate $FPS -start_number 0 -i "$FR/f_%05d.png" -c:v libx264 -crf 26 -pix_fmt yuv420p "$OUT/${SEG}_preview.mp4"
ROWS=$(python -c "import math; print(math.ceil($DUR * 2 / 6))")
ffmpeg -hide_banner -loglevel error -y -i "$OUT/${SEG}_preview.mp4" -vf "fps=2,scale=320:-1,tile=6x$ROWS" -frames:v 1 -q:v 6 "$OUT/${SEG}_sheet.jpg"
ls -la "$OUT/${SEG}_preview.mp4" "$OUT/${SEG}_sheet.jpg"
