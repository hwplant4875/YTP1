#!/usr/bin/env bash
# FINAL RENDER QUEUE (prepared by the autopilot 10/28, NOT run: the owner approves the final render on Saturday).
# Renders every segment at the approved state (the versions in full_onetake_v11) at FINAL quality, then burns the name tags
# and concatenates the 3-part one take.  Detached + resumable (each segment script skips frames already on disk):
#   nohup bash render_final_queue.sh > "E:/YTP2/3D Timelapse/logs/final_queue.log" 2>&1 &
# Settings: 1920x1080, 30 fps, every frame (STEP=1), TOON 0, Eevee samples SMP (default 16).  Output: renders/final/<seg>/.
# RISKS (read first):
#  * GTX 1060 driver timeout in the FOREST (f2, f3): 1080p costs ~4.5x the GPU time of 480p per frame. The 480p fix was a
#    camera far clip (seg_f2 350 m, seg_f3 600/350 m) + ForestDim tint. At 1080p frames may again exceed the Windows TDR
#    (2 s) -> Blender dies silently and render_part2 fills gaps with duplicate frames. After f2 / f3 check
#      md5sum renders/final/f3/frames/f_*.png | awk '{print $1}' | sort -u | wc -l     (must equal the frame count)
#    If short: F_CLIP=250 for f2, lower seg_f3 clip, or render f2/f3 at SMP=4, or (owner decision) raise TdrDelay.
#  * Time estimate (480p preview ~1.2 s/frame): 1080p ~5-6 s/frame x 30 fps x 390 s ~ 11 700 frames ~ 18-20 h of GPU.
#  * The tags are burnt from frames/_cam (tag_burn.py --size 1920x1080); g1 uses the screen-anchored COLOSSAL TITAN tag.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"; cd "$HERE"
FR="E:/YTP2/3D Timelapse/renders/final"; mkdir -p "$FR"
export TOON=0 FPS=30 STEP=1 RES=1920x1080 SMP="${SMP:-16}"
for g in g1 g2 g3 g4 g5 g6 g7 g8; do
  echo "[final] $g start $(date +%T)"
  if [ "$g" = g1 ]; then VCLOCK=1 OUTR="$FR/g1" bash render_g1.sh > "$FR/$g.log" 2>&1
  else VCLOCK=1 SEG=$g OUT="$FR/$g" bash render_seg.sh > "$FR/$g.log" 2>&1; fi
  python tag_burn.py $g "$FR/$g/frames" "$FR/$g/${g}_tagged.mp4" --size 1920x1080 --fps 30 >> "$FR/$g.log" 2>&1
done
for g in f0 f1 f2 f3 s1 s2; do
  echo "[final] $g start $(date +%T)"
  SEG=$g OUT="$FR/$g" bash aot/forest/render_part2.sh > "$FR/$g.log" 2>&1
  python tag_burn.py $g "$FR/$g/frames" "$FR/$g/${g}_tagged.mp4" --size 1920x1080 --fps 30 >> "$FR/$g.log" 2>&1
done
# NOTE concat_master.sh / the part 2 concat scale to 854x480 for previews: for the final, concat the *_tagged.mp4 files at
# 1920x1080 / 30 fps (same filter graph with scale=1920:1080,fps=30 and the 0.6 s g2|g3 dissolve), CRF 18.
echo "[final] segments DONE $(date +%T) - concat next (see note above)"
