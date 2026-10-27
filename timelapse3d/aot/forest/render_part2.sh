#!/usr/bin/env bash
# PART 2-3 SEGMENT RENDER (seg_f*.py forest, seg_s*.py Stohess) on aot/render_seg.py, 640x360, 15 fps, Eevee, TOON off.
#   SEG=f1 bash aot/forest/render_part2.sh                 whole segment (windows of WINLEN s), encode + 2 fps contact sheet
#   SEG=f1 STILLS="2,10" bash aot/forest/render_part2.sh   stills (seconds) into $OUT/stills
#   SEG=f1 ENCODE_ONLY=1 ...                               encode from frames on disk;  CHECK=1 / DRY=1 no render, no lock
# Sets: f0 = Trost set (AOT_SET=trost, frame M, the part 1 end) ; f1.. = forest.fset (frame W) ; s* = stohess.sset (frame W).
# Segment time = video time (no VCLOCK; each module's DUR is already in video seconds).  GPU lock as render_seg.sh.
SEG="${SEG:?set SEG=f1 (etc.)}"
FPS="${FPS:-15}"; SMP="${SMP:-1}"; STEP="${STEP:-2}"; WINLEN="${WINLEN:-20}"; RES="${RES:-640x360}"
export TOON="${TOON:-0}"
HERE="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="${OUT:-E:/YTP2/3D Timelapse/renders/part2/$SEG}"
FR="$OUT/frames"; mkdir -p "$FR"
BL="/c/All The Programs/Blender/blender.exe"
LOCK="/e/YTP2/3D Timelapse/.gpu_lock"
DUR="${DUR:-$(cd "$HERE/aot" && python -c "import seg_$SEG as m; print(m.DUR)")}"
case "$SEG" in
  f0) SETV=trost; export SEG_FRAME=M; PLUG=world; CAMN=gate ;;
  s*) SETV=stohess.sset; export SEG_FRAME=W AOT_WORLD_FRAME=shig; PLUG=""; CAMN=s_overview ;;
  *)  SETV=forest.fset; export SEG_FRAME=W AOT_WORLD_FRAME=shig; PLUG=""; CAMN=f_overview ;;
esac

run_blender() {   # $1 = output dir, $2 = extra args, $3 = nolock
  local SOUT="$1" NOLOCK="$3"
  if [ -z "$NOLOCK" ]; then
    until mkdir "$LOCK" 2>/dev/null; do sleep 5; done
    trap 'rmdir "$LOCK" 2>/dev/null' EXIT
  fi
  AOT_SET=$SETV AOT_PLUGINS=$PLUG TA_PSCALE=1.0 FPS=$FPS \
    "$BL" -b -P "$HERE/aot/scene.py" -P "$HERE/aot/render_seg.py" -- \
    --year 850 --cam $CAMN --engine ${ENGINE:-BLENDER_EEVEE} --res $RES --samples $SMP \
    --seg "$SEG" --seg-out "$SOUT" --fps $FPS --seg-samples $SMP $2 2>&1 \
    | grep --line-buffered -E "\[seg|\[f[0-9]|\[s[0-9]|\[forest|\[stohess|\[trost\]|\[world|\[plugin|Traceback|Error|error:|line [0-9]+|FLAG|peak"
  if [ -z "$NOLOCK" ]; then rmdir "$LOCK" 2>/dev/null; trap - EXIT; fi
}

if [ -n "$CHECK" ]; then run_blender "$OUT/check" "--check" nolock; exit 0; fi
if [ -n "$DRY" ]; then run_blender "$OUT/check" "--dry" nolock; exit 0; fi
if [ -n "$STILLS" ]; then run_blender "$OUT/stills" "--stills $STILLS"; ls "$OUT/stills" | tail -20; exit 0; fi

if [ -z "$ENCODE_ONLY" ]; then
  A=0
  while python -c "import sys; sys.exit(0 if $A < $DUR - 1e-6 else 1)"; do
    Bw=$(python -c "print(min($A + $WINLEN, $DUR))")
    for TRY in 1 2 3; do
      run_blender "$FR" "--t0 $A --t1 $Bw --step $STEP"
      ls "$FR" | grep -q "^_done_${A}_" && break
      echo "[seg] blender exited early in window $A-$Bw (try $TRY), resuming"
    done
    A=$Bw
  done
fi

python - "$FR" "$DUR" "$FPS" <<'PY'
import os, sys, shutil
d, dur, fps = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
n = int(round(dur * fps)); last = None
for f in range(n):
    p = os.path.join(d, f"f_{f:05d}.png")
    if os.path.exists(p) and os.path.getsize(p) > 0:
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
