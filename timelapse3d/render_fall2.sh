#!/usr/bin/env bash
# Shiganshina 845 segments 3-5 (aot/render_fall2.py), one Blender session per state.
#   SEG=3  FPS=15 bash render_fall2.sh     Armored bursts the inner gate, ferries, the vow   -> renders/fall/fall3_preview.mp4
#   SEG=45 FPS=15 bash render_fall2.sh     night pull-up + grey belt (seg 4), Grisha beat (seg 5) -> fall4/fall5_preview.mp4
#   FPS=30 = final (8 samples); FPS<=15 = preview (FAST_PREVIEW: 2 samples + OIDN). TIMES="1,4,9" = stills only.
SEG="${SEG:-3}"; FPS="${FPS:-30}"
if [ -z "$FAST_PREVIEW" ]; then [ "${FPS%.*}" -le 15 ] && FAST_PREVIEW=1 || FAST_PREVIEW=0; fi
if [ "$FAST_PREVIEW" = 1 ]; then SAMPLES="${SAMPLES:-2}"; else SAMPLES="${SAMPLES:-8}"; fi
export FAST_PREVIEW
[ "$FAST_PREVIEW" = 1 ] && export AOT_FX_PUFFS="${AOT_FX_PUFFS:-0.6}"
HERE="$(cd "$(dirname "$0")" && pwd)"; FALL="E:/YTP2/3D Timelapse/renders/fall"
OUT="${OUT:-E:/YTP2/3D Timelapse/renders/fall_frames$SEG}"
[ -z "$TIMES" ] && rm -rf "$OUT"; mkdir -p "$OUT" "$FALL"
if [ "$SEG" = 3 ]; then ST=armored; else ST=night; fi
# segments 4-5 (night): Eevee + no smoke volumes; render_fall2 adds fire / smoke CARDS (smokecards) instead
if [ "$SEG" != 3 ]; then export AOT_NOSMOKE=1; ENGINE="${ENGINE:-EEVEE}"; fi
LOCK="/e/YTP2/3D Timelapse/.gpu_lock"
until mkdir "$LOCK" 2>/dev/null; do sleep 5; done
trap 'rmdir "$LOCK" 2>/dev/null' EXIT
BL="/c/All The Programs/Blender/blender.exe"
EXTRA=""; [ -n "$TIMES" ] && EXTRA="--times $TIMES"
CARLA_ENV_DONE=1 SWARM=1 SUN_AZ=-102 EXPO="${EXPO:--1.3}" TREE_DENS=0.006 FL_NOKIDS=1 COL_SHOW=0 \
AOT_STATE=$ST AOT_ARC_T=1 AOT_EVENT=intact AOT_PLUGINS=flight,states845,swarm845 \
  "$BL" -b -P "$HERE/aot/scene.py" -P "$HERE/aot/render_fall2.py" -- \
  --cam overview --engine ${ENGINE:-CYCLES} --res 854x480 --samples $SAMPLES --seg $SEG --fall-out "$OUT" --fps $FPS \
  --fall-samples $SAMPLES $EXTRA 2>&1 | grep -E "\[fall2\]|\[swarm845\]|Traceback|Error|line [0-9]+"
[ -n "$TIMES" ] && exit 0
enc() { ffmpeg -hide_banner -loglevel error -y -framerate $FPS -i "$1" -c:v libx264 -crf 26 -pix_fmt yuv420p "$2"; ls -la "$2"; }
if [ "$SEG" = 3 ]; then enc "$OUT/fall3_%05d.png" "$FALL/fall3_preview.mp4"
else
  [ -d "$OUT/seg4" ] && enc "$OUT/seg4/fall4_%05d.png" "$FALL/fall4_preview.mp4"
  [ -d "$OUT/seg5" ] && enc "$OUT/seg5/fall5_%05d.png" "$FALL/fall5_preview.mp4"
  cp "$OUT/grisha_glitch_marker.json" "$FALL/" 2>/dev/null
fi
