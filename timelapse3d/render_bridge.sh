#!/usr/bin/env bash
# EP1 bridge flights (aot/render_bridge.py, agent G): one Blender session per WORLD, each renders its bridge halves.
#   bash render_bridge.sh                    all worlds (interlude, march, trost, shig), 15 fps preview, 854x480
#   WORLDS="interlude march" bash render_bridge.sh          only these sessions
#   KEYS_ONLY=1 bash render_bridge.sh        evaluate + cache the segment keys (no rendering; still loads each world)
#   FPS=30 SMP=8 bash render_bridge.sh       final frame rate
#   JS="5,20" WORLDS=march bash render_bridge.sh             only these bridge frames (spot checks)
# Halves per world (master_timeline.SEGMENTS): interlude = B1b B2a B3b B4a, march = B2b B3a, trost = B4b, shig = B1a.
# Output: E:/YTP2/3D Timelapse/renders/master/bridges/<B#>/br_<j>.png (+ _cam dumps) and bridges/keys/*.json.
FPS="${FPS:-15}"; WORLDS="${WORLDS:-interlude march trost shig}"
HERE="$(cd "$(dirname "$0")" && pwd)"
BL="/c/All The Programs/Blender/blender.exe"
OUTB="E:/YTP2/3D Timelapse/renders/master/bridges"; mkdir -p "$OUTB"
LOCK="/e/YTP2/3D Timelapse/.gpu_lock"
COMMON="--br-fps $FPS"; [ -n "$KEYS_ONLY" ] && COMMON="$COMMON --br-keys-only"; [ -n "$JS" ] && COMMON="$COMMON --br-js $JS"
FILTER='\[bridge\]|\[int\] built|Traceback|Error|error:|line [0-9]+'
lock()   { until mkdir "$LOCK" 2>/dev/null; do sleep 5; done; trap 'rmdir "$LOCK" 2>/dev/null' EXIT; }
unlock() { rmdir "$LOCK" 2>/dev/null; trap - EXIT; }

for W in $WORLDS; do
  echo "== bridge world $W"
  lock
  case "$W" in
    interlude)   # render_interlude.py as a library (no scene.py): Cycles 4 spp + OptiX as agent B's preview
      "$BL" -b -P "$HERE/aot/render_bridge.py" -- --world interlude --halves B1b,B2a,B3b,B4a --out "$OUTB/_tmp_interlude" \
        --br-samples ${SMP:-4} --br-engine CYCLES $COMMON 2>&1 | grep --line-buffered -E "$FILTER" ;;
    march)       # as render_march846.sh: Trost set, Eevee 8
      TREE_DENS=${TREE_DENS:-0.003} AOT_SET=trost AOT_PLUGINS="" \
      "$BL" -b -P "$HERE/aot/scene.py" -P "$HERE/aot/render_bridge.py" -- --year 846 --cam trost_overview \
        --engine ${ENGINE:-EEVEE} --res 854x480 --samples ${SMP:-8} --world march --halves B2b,B3a --br-samples ${SMP:-8} \
        $COMMON 2>&1 | grep --line-buffered -E "$FILTER|\[march" ;;
    trost)       # as render_trost.sh (Eevee, 1 sample): render_trost.py runs up to its render loop
      TA_PSCALE=${TA_PSCALE:-2.5} TREE_DENS=${TREE_DENS:-0.005} COL_H=${COL_H:-64} COL_DX=${COL_DX:--7} AOT_SET=trost \
      AOT_PLUGINS=colossal_asset \
      "$BL" -b -P "$HERE/aot/scene.py" -P "$HERE/aot/render_bridge.py" -- --year 850 --cam trost_overview \
        --engine BLENDER_EEVEE --res 854x480 --samples ${SMP:-1} --rt-out "$OUTB/_tmp_trost" --rt-samples ${SMP:-1} \
        --world trost --halves B4b $COMMON 2>&1 | grep --line-buffered -E "$FILTER" ;;
    shig)        # as render_fall2.sh SEG=45 FALL2_ONLY=5 (night state, no smoke volumes): render_fall2.py up to main
      FAST_PREVIEW=1 AOT_FX_PUFFS=0.6 AOT_NOSMOKE=1 CARLA_ENV_DONE=1 SWARM=1 SUN_AZ=-102 EXPO="${EXPO:--1.3}" TREE_DENS=0.006 \
      FL_NOKIDS=1 COL_SHOW=0 AOT_STATE=night AOT_ARC_T=1 AOT_EVENT=intact AOT_PLUGINS=flight,states845,swarm845 \
      "$BL" -b -P "$HERE/aot/scene.py" -P "$HERE/aot/render_bridge.py" -- --cam overview --engine CYCLES --res 854x480 \
        --samples ${SMP:-2} --seg 45 --fall-out "$OUTB/_tmp_shig" --fall-samples ${SMP:-2} --world shig --halves B1a \
        $COMMON 2>&1 | grep --line-buffered -E "$FILTER|\[fall2\]" ;;
  esac
  unlock
done
python "$HERE/aot/master_timeline.py" --fps "$FPS" | sed -n '/BRIDGES/,$p'
