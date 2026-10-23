#!/usr/bin/env bash
# Serialised Blender render (one GPU job at a time on this laptop).
#   bash render.sh <cam> <out.png> [res=960x540] [samples=32] [extra scene.py args...]
# Env vars (AOT_PLUGINS, LINES, EXPO, ...) pass through. Waits for the lock E:/YTP2/3D Timelapse/.gpu_lock.
CAM="$1"; OUT="$2"; RES="${3:-960x540}"; SMP="${4:-32}"; shift 4 2>/dev/null
LOCK="/e/YTP2/3D Timelapse/.gpu_lock"
until mkdir "$LOCK" 2>/dev/null; do
  # break a stale lock older than 20 minutes
  if [ -n "$(find "$LOCK" -maxdepth 0 -mmin +20 2>/dev/null)" ]; then rmdir "$LOCK"; fi
  sleep 3
done
trap 'rmdir "$LOCK" 2>/dev/null' EXIT
HERE="$(cd "$(dirname "$0")" && pwd)"
timeout 900 "/c/All The Programs/Blender/blender.exe" -b -P "$HERE/aot/scene.py" -- --cam "$CAM" --res "$RES" --samples "$SMP" --out "$OUT" "$@" 2>&1 \
  | grep -vE "DeprecationWarning|use_nodes|HIPEW|^\s*$|Fra:|^Blender|Read prefs" | tail -25
