#!/usr/bin/env bash
# EP1 CONNECTOR flights (aot/render_bridge.py, agent G): one Blender session per scene, each renders its spans.
# STRICT ONE TAKE (HANDOFF 10/25 09:37): matched-camera seams only (no clouds, no wipes). Every scene loads aot/world.py.
# Spans per scene (master_timeline.SEGMENTS):  shig = C1a   interlude = C2a   march = C2b,C3a
#   bash render_bridge.sh                    all scenes, 15 fps preview, 854x480
#   WORLDS="march" bash render_bridge.sh     only these sessions
#   KEYS_ONLY=1 bash render_bridge.sh        evaluate + cache the segment keys (no rendering)
#   FPS=30 SMP=8 bash render_bridge.sh       final frame rate
#   JS="5,20" WORLDS=march bash render_bridge.sh             only these connector frames (spot checks)
#   STILLS="name:x,y,z:lx,ly,lz:lens;..." WORLDS=march HALVES= bash render_bridge.sh    world stills (WORLD coords)
# Output: E:/YTP2/3D Timelapse/renders/master/bridges/<C#>/br_<j>.png (+ _cam dumps), bridges/keys/*.json,
#         renders/master/world_stills/*.png
FPS="${FPS:-15}"; WORLDS="${WORLDS:-shig interlude march}"
HERE="$(cd "$(dirname "$0")" && pwd)"
BL="/c/All The Programs/Blender/blender.exe"
OUTB="E:/YTP2/3D Timelapse/renders/master/bridges"; mkdir -p "$OUTB"
LOCK="/e/YTP2/3D Timelapse/.gpu_lock"
COMMON="--br-fps $FPS"; [ -n "$KEYS_ONLY" ] && COMMON="$COMMON --br-keys-only"; [ -n "$JS" ] && COMMON="$COMMON --br-js $JS"
FILTER='\[bridge\]|\[world\]|\[int\] built|Traceback|Error|error:|line [0-9]+'
lock()   { until mkdir "$LOCK" 2>/dev/null; do sleep 5; done; trap 'rmdir "$LOCK" 2>/dev/null' EXIT; }
unlock() { rmdir "$LOCK" 2>/dev/null; trap - EXIT; }
half() { if [ "${HALVES+x}" = x ]; then echo "$HALVES"; else echo "$1"; fi; }

for W in $WORLDS; do
  echo "== connector scene $W"
  lock
  case "$W" in
    shig)        # as render_fall2.sh SEG=3 (Armored state, sunset light) + world; C1 timelapses the sun to daylight
      FAST_PREVIEW=1 AOT_FX_PUFFS=0.6 CARLA_ENV_DONE=1 SWARM=1 SUN_AZ=-102 EXPO="${EXPO:--1.5}" TREE_DENS=0.006 \
      FL_NOKIDS=1 COL_SHOW=0 AOT_STATE=armored AOT_ARC_T=1 AOT_EVENT=intact AOT_PLUGINS=flight,states845,swarm845,world \
      "$BL" -b -P "$HERE/aot/scene.py" -P "$HERE/aot/render_bridge.py" -- --cam overview --engine CYCLES --res 854x480 \
        --samples ${SMP:-2} --seg 3 --fall-out "$OUTB/_tmp_shig" --fall-samples ${SMP:-2} --world shig \
        --halves "$(half C1a)" --stills "$STILLS" $COMMON 2>&1 | grep --line-buffered -E "$FILTER|\[fall2\]" ;;
    interlude)   # render_interlude.py as a library (agent B attaches world.py inside build())
      "$BL" -b -P "$HERE/aot/render_bridge.py" -- --world interlude --halves "$(half C2a)" --out "$OUTB/_tmp_interlude" \
        --br-samples ${SMP:-4} --br-engine CYCLES --stills "$STILLS" $COMMON 2>&1 | grep --line-buffered -E "$FILTER" ;;
    march)       # as render_march846.sh: Trost set + world, Eevee 8
      TREE_DENS=${TREE_DENS:-0.003} AOT_SET=trost AOT_PLUGINS="world" \
      "$BL" -b -P "$HERE/aot/scene.py" -P "$HERE/aot/render_bridge.py" -- --year 846 --cam trost_overview \
        --engine ${ENGINE:-EEVEE} --res 854x480 --samples ${SMP:-8} --world march --halves "$(half C2b,C3a)" \
        --br-samples ${SMP:-8} --stills "$STILLS" $COMMON 2>&1 | grep --line-buffered -E "$FILTER|\[march" ;;
    trost)       # Trost scene (render_trost.py up to its loop) + world: no connector span now; seam S8 checks / stills
      TA_PSCALE=${TA_PSCALE:-1} TREE_DENS=${TREE_DENS:-0.005} COL_H=${COL_H:-64} COL_DX=${COL_DX:--7} AOT_SET=trost \
      AOT_PLUGINS=colossal_asset,world \
      "$BL" -b -P "$HERE/aot/scene.py" -P "$HERE/aot/render_bridge.py" -- --year 850 --cam trost_overview \
        --engine BLENDER_EEVEE --res 854x480 --samples ${SMP:-1} --rt-out "$OUTB/_tmp_trost" --rt-samples ${SMP:-1} \
        --world trost --halves "$(half '')" --stills "$STILLS" $COMMON 2>&1 | grep --line-buffered -E "$FILTER" ;;
    base)        # bare scene.py (+ AOT_SET if given) + world: stills only
      AOT_PLUGINS="${PLUG:-flight,world}" \
      "$BL" -b -P "$HERE/aot/scene.py" -P "$HERE/aot/render_bridge.py" -- --cam overview --engine ${ENGINE:-EEVEE} \
        --res 854x480 --samples ${SMP:-8} --world base --stills "$STILLS" $COMMON 2>&1 | grep --line-buffered -E "$FILTER" ;;
  esac
  unlock
done
python "$HERE/aot/master_timeline.py" --fps "$FPS" | sed -n '/SEAMS/,$p'
