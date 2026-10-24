#!/usr/bin/env bash
# Preview frames of the hill -> inner gate -> Colossal -> kick sequence (aot/seq_colossal.py).
#   bash seq_preview.sh "<frames>" [res=480x270] [samples=12] [outdir]
FR="$1"; RES="${2:-480x270}"; SMP="${3:-12}"; OUT="${4:-E:/YTP2/3D Timelapse/renders/seq}"
HERE="$(cd "$(dirname "$0")" && pwd)"; mkdir -p "$OUT"
for f in $FR; do
  SEQ_F=$f AOT_PLUGINS=seq_colossal,flight,cast845,states845,colossal_asset,seq_colossal \
    bash "$HERE/render.sh" seq "$OUT/seq_f$(printf %04d $f).png" "$RES" "$SMP" | grep -E "Saved|Error|Traceback|failed" | tail -3
done
