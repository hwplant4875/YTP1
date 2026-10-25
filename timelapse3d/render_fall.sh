#!/usr/bin/env bash
# Segment 2 "the fall" (aot/render_fall.py) in ONE Blender session: houses collapse (fx845), crowd flees and titans pour
# in (swarm845, timelapse), then the Carla beat (seq_carla per-frame poses). Continues render_fast.sh (video 13.0 s).
#   FPS=15 bash render_fall.sh             preview (FPS<=15 -> FAST_PREVIEW=1: 2 samples + OIDN, short paths) -> fall_preview.mp4
#   bash render_fall.sh                    FPS=30 final (8 samples, full light paths)
#   TIMES="0,3,8,12.5" bash render_fall.sh                   stills only (fall_sSS.ss.png in OUT)
FPS="${FPS:-30}"; S0="${S0:-0}"; S1="${S1:-10.6}"
if [ -z "$FAST_PREVIEW" ]; then [ "${FPS%.*}" -le 15 ] && FAST_PREVIEW=1 || FAST_PREVIEW=0; fi
if [ "$FAST_PREVIEW" = 1 ]; then SAMPLES="${SAMPLES:-2}"; else SAMPLES="${SAMPLES:-8}"; fi
export FAST_PREVIEW
[ "$FAST_PREVIEW" = 1 ] && export AOT_FX_PUFFS="${AOT_FX_PUFFS:-0.6}"
HERE="$(cd "$(dirname "$0")" && pwd)"; OUT="${OUT:-E:/YTP2/3D Timelapse/renders/fall_frames}"
MP4="${MP4:-E:/YTP2/3D Timelapse/renders/fall_preview.mp4}"
[ -z "$TIMES" ] && [ "$S0" = 0 ] && rm -rf "$OUT"; mkdir -p "$OUT"   # S0>0: re-render a tail into the same folder
LOCK="/e/YTP2/3D Timelapse/.gpu_lock"
until mkdir "$LOCK" 2>/dev/null; do sleep 5; done
trap 'rmdir "$LOCK" 2>/dev/null' EXIT
BL="/c/All The Programs/Blender/blender.exe"
P=seq_carla,flight,states845,swarm845,world,seq_carla
EXTRA=""; [ -n "$TIMES" ] && EXTRA="--times $TIMES"
# CARLA_PERFRAME: seq_carla builds once, render_fall poses it per frame; SUN_AZ/EXPO as the opening (render_fast.sh)
CARLA_PERFRAME=1 CARLA_NOKIDS=1 AOT_YEAGER_XY=${AOT_YEAGER_XY:--48,-640} CARLA_F=2330 CARLA_TITAN_H=${CARLA_TITAN_H:-16} SWARM=1 SUN_AZ=-102 EXPO=-1.5 TREE_DENS=0.006 FL_NOKIDS=1 COL_SHOW=0 \
AOT_STATE=kicked AOT_ARC_T=1 AOT_EVENT=intact AOT_PLUGINS=$P \
  "$BL" -b -P "$HERE/aot/scene.py" -P "$HERE/aot/render_fall.py" -- \
  --cam overview --engine ${ENGINE:-EEVEE} --res 854x480 --samples $SAMPLES --fall-out "$OUT" --s0 $S0 --s1 $S1 --fps $FPS \
  --fall-samples $SAMPLES $EXTRA 2>&1 | grep -E "\[fall\]|\[swarm845\]|\[seq_carla\] per|Traceback|Error|line [0-9]+"
[ -n "$TIMES" ] && exit 0
ffmpeg -hide_banner -loglevel error -y -framerate $FPS -i "$OUT/fall_%05d.png" -c:v libx264 -crf 26 -pix_fmt yuv420p "$MP4"
ls -la "$MP4"
