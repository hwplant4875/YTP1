#!/usr/bin/env bash
# Preview frames of the Carla sequence (aot/seq_carla.py: S12-S14 Carla / Hannes / Smiling Titan, S18 ferries + oath).
#   bash carla_preview.sh "<frames>" [res=640x360] [samples=16] [outdir]
# Frames continue seq_colossal's numbering: 2100-2190 fly-in, S12 2190-2340, S13 2340-2460, S14 2460-2650, S18 2650-2890.
FR="$1"; RES="${2:-640x360}"; SMP="${3:-16}"; OUT="${4:-E:/YTP2/3D Timelapse/renders/seq_carla}"
HERE="$(cd "$(dirname "$0")" && pwd)"; mkdir -p "$OUT"
for f in $FR; do
  CARLA_F=$f AOT_PLUGINS=seq_carla,flight,cast845,states845,seq_carla \
    bash "$HERE/render.sh" carla "$OUT/carla_f$(printf %04d $f).png" "$RES" "$SMP" | grep -E "seq_carla|Saved|Error|Traceback|failed|line [0-9]" | tail -12
done
