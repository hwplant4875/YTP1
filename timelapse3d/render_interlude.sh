#!/usr/bin/env bash
# INTERLUDE 846-850 (agent B): rise over Trost / Wall Rose -> refugee camps (846) -> 104th training camp (847-850), 20.5 s.
# One Blender session builds the world once (aot/render_interlude.py imports scene.py as a library), then renders
# every frame as a pure function of t (plus hudcam camera dumps).  The HUD (place · year, captions, cadet
# tags) is agent E's hud2.py driven by aot/interlude_timeline.json (aot/interlude_hud.py); raw frames stay in OUT/raw.
#   bash render_interlude.sh                 preview: 15 fps, Cycles 4 spp (night 8) + OptiX denoise, 854x480 -> interlude_preview.mp4
#   FPS=30 SMP=8 RES=1920x1080 bash render_interlude.sh       final frames
#   TIMES="1,4,6,9.5,11.5,15,19.5" bash render_interlude.sh     stills only (int_tSS.ss.png + _hud.jpg)
FPS="${FPS:-15}"; T0="${T0:-0}"; T1="${T1:-20.5}"; SMP="${SMP:-4}"; RES="${RES:-854x480}"
HERE="$(cd "$(dirname "$0")" && pwd)"
OUT="${OUT:-E:/YTP2/3D Timelapse/renders/interlude}"
RAW="$OUT/raw"; [ -n "$TIMES" ] && RAW="$OUT/stills_raw"
[ -z "$TIMES" ] && rm -rf "$RAW"; mkdir -p "$RAW"
LOCK="/e/YTP2/3D Timelapse/.gpu_lock"
until mkdir "$LOCK" 2>/dev/null; do sleep 5; done
trap 'rmdir "$LOCK" 2>/dev/null' EXIT
BL="/c/All The Programs/Blender/blender.exe"
EXTRA=""; [ -n "$TIMES" ] && EXTRA="--times $TIMES"
"$BL" -b -P "$HERE/aot/render_interlude.py" -- --out "$RAW" --t0 $T0 --t1 $T1 --fps $FPS --samples $SMP --res $RES $EXTRA 2>&1 \
  | grep -E "\[int\]|Traceback|Error|error" | grep -v "^Warning"
rmdir "$LOCK" 2>/dev/null; trap - EXIT          # GPU free again: the overlay / encode run on the CPU
if [ -n "$TIMES" ]; then
  python "$HERE/aot/interlude_hud.py" --stills "$RAW" "$OUT/stills"; exit 0
fi
python "$HERE/aot/interlude_hud.py"          # -> OUT/hud/int_%05d.png + OUT/interlude_preview.mp4
ffmpeg -hide_banner -loglevel error -y -framerate $FPS -i "$RAW/int_%05d.png" -c:v libx264 -crf 26 -pix_fmt yuv420p "$OUT/interlude_preview_nohud.mp4"
ls -la "$OUT"/*.mp4
