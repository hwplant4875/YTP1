#!/usr/bin/env bash
# g1 "Opening + Shiganshina fall" (SCENE_BIBLE_v2 B.g1, 32.0 s, kick 11.0) = aot/render_g1.py, one time base.
# The scene is built once per Blender invocation; every frame is a pure function of its g1 time, so the 32 s can be
# split into windows (each invocation <= 20 min wall) that write into the same frame folder.
#   bash render_g1.sh                                   preview: 854x480, 15 fps, Eevee + toon, windows from PARTS
#   PARTS="0-8,8-16,16-24,24-32" STEP=2 bash render_g1.sh   windows / every 2nd frame (frame repeat)
#   TIMES="2.0,4.5,7.0,11.1,14,22,27" bash render_g1.sh   stills only (g1_tSS.ss.png in OUT/stills)
#   ENCODE_ONLY=1 bash render_g1.sh                     re-encode mp4 + contact sheet from the frames
#   NO_ENCODE=1 OUT=... PARTS=12-12.8 bash render_g1.sh  frames only (timing tests)
# VIDEO CLOCK (owner 10/27 07:34): VCLOCK=1 -> frames on the video clock (segtime.TMAP["g1"], G1_PLAN), PARTS / TIMES in VIDEO
# seconds, default OUTR renders/g1_v3.  Previews 480p at FPS=15 (default); the final render is FPS=30 (same command).
#   VCLOCK=1 bash render_g1.sh                          whole g1 (~17.9 s) in two Blender runs
#   VCLOCK=1 TIMES="5.5,7.5,11.2" bash render_g1.sh     stills at video seconds
HERE="$(cd "$(dirname "$0")" && pwd)"
FPS="${FPS:-15}"; STEP="${STEP:-1}"; SMP="${SMP:-8}"; RES="${RES:-854x480}"
if [ -n "$VCLOCK" ]; then
  VD=$(cd "$HERE/aot" && python -c "import segtime; print(round(segtime.vdur('g1'), 4))")
  PARTS="${PARTS:-0-9.5,9.5-$VD}"; VCARG="--vclock"; OUTR="${OUTR:-E:/YTP2/3D Timelapse/renders/g1_v3}"
fi
PARTS="${PARTS:-0-8,8-16,16-24,24-32}"
OUTR="${OUTR:-E:/YTP2/3D Timelapse/renders/g1}"; OUT="${OUT:-$OUTR/frames}"
MP4="$OUTR/g1_preview.mp4"; SHEET="$OUTR/g1_sheet.jpg"
BL="/c/All The Programs/Blender/blender.exe"
LOCK="/e/YTP2/3D Timelapse/.gpu_lock"
mkdir -p "$OUT" "$OUTR/stills"
P=seq_colossal,seq_carla,flight,cast845,g1_set,states845,colossal_asset,world,seq_colossal,seq_carla
run_blender() {   # $@ = extra render_g1.py args
  until mkdir "$LOCK" 2>/dev/null; do sleep 5; done
  trap 'rmdir "$LOCK" 2>/dev/null' EXIT
  FL_FIELD=1 FL_KIDS_MODE=seated FL_NOKIDS= FL_NOGRASS= TREE_DENS=0.006 SEQ_F=1300 \
  COL_SHOW=1 COL_H=${COL_H:-61.5} COL_HEAD=${COL_HEAD:-1.3} COL_BACK=${COL_BACK:-12} COL_DX=${COL_DX:--7} COL_HAND_S=${COL_HAND_S:-1.5} COL_RISE_DROP=${COL_RISE_DROP:-11} \
  AOT_STATE=kicked AOT_ARC_T=1 AOT_EVENT=intact AOT_YEAGER_XY=-165,-585 \
  CARLA_PERFRAME=1 CARLA_NOKIDS=1 CARLA_NOGORE=1 CARLA_H=1.6 CARLA_TITAN_H=${CARLA_TITAN_H:-13} CARLA_F=2200 \
  SWARM_TITANS=${SWARM_TITANS:-36} SWARM_FAN=${SWARM_FAN:-0.95,60} SWARM_TEND=36 FPS=$FPS \
  AOT_PLUGINS=$P "$BL" -b -P "$HERE/aot/scene.py" -P "$HERE/aot/render_g1.py" -- \
    --cam seq --engine BLENDER_EEVEE --res $RES --samples $SMP --g1-out "$1" --fps $FPS --g1-samples $SMP $VCARG "${@:2}" 2>&1 \
    | grep -E "\[g1\]|\[g1_set\]|\[states845\]|\[swarm845\]|\[colossal_asset\]|\[seq_carla\] (per|house)|Traceback|Error|line [0-9]+"
  rmdir "$LOCK" 2>/dev/null; trap - EXIT
  sleep "${GPU_GAP:-10}"                      # leave the GPU to the other renders for a moment between windows
}
if [ -n "$TIMES" ]; then
  run_blender "$OUTR/stills" --times "$TIMES"
  exit 0
fi
if [ -z "$ENCODE_ONLY" ]; then
  IFS=',' read -ra WINS <<< "$PARTS"
  for w in "${WINS[@]}"; do
    a="${w%-*}"; b="${w#*-}"
    echo "[render_g1.sh] window $a-$b s (step $STEP) $(date +%T)"
    run_blender "$OUT" --t0 "$a" --t1 "$b" --step "$STEP"
  done
fi
[ -n "$NO_ENCODE" ] && exit 0
ffmpeg -hide_banner -loglevel error -y -framerate $FPS -i "$OUT/g1_%05d.png" -c:v libx264 -crf 26 -pix_fmt yuv420p "$MP4"
NF=$(ls "$OUT"/g1_*.png | wc -l); ROWS=$(( (NF * 2 / ${FPS%.*} + 6) / 6 ))
ffmpeg -hide_banner -loglevel error -y -i "$MP4" -vf "fps=2,scale=320:-1,tile=6x$ROWS" -frames:v 1 -q:v 5 "$SHEET"
ls -la "$MP4" "$SHEET"
