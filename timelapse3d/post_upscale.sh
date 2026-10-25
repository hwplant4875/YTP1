#!/usr/bin/env bash
# Optional post step for finals: frames (e.g. 15 fps 720p) -> RIFE x2 (30 fps) -> Real-ESRGAN anime-video x2 -> H.264.
#   bash post_upscale.sh <frames_dir> <out.mp4> [in_fps=15] [scale=2] [crf=18]
# TOOLS defaults to E:/YTP2/3D Timelapse/tools (rife-ncnn-vulkan-20221029-windows, realesrgan); GPU=0 is the NVIDIA card
# (device 1 on the laptop is the Intel iGPU). On Linux/cloud set TOOLS to the ncnn-vulkan Linux builds.
set -e
IN="$1"; OUT="$2"; FPS="${3:-15}"; SC="${4:-2}"; CRF="${5:-18}"
TOOLS="${TOOLS:-E:/YTP2/3D Timelapse/tools}"; GPU="${GPU:-0}"
RIFE="$TOOLS/rife-ncnn-vulkan-20221029-windows"; ESR="$TOOLS/realesrgan"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
mkdir -p "$TMP/rife" "$TMP/esr"
"$RIFE/rife-ncnn-vulkan.exe" -i "$IN" -o "$TMP/rife" -m "$RIFE/rife-v4.6" -g "$GPU"
if [ "$SC" = "1" ]; then SRC="$TMP/rife"; else
  "$ESR/realesrgan-ncnn-vulkan.exe" -i "$TMP/rife" -o "$TMP/esr" -n realesr-animevideov3 -s "$SC" -m "$ESR/models" -g "$GPU"
  SRC="$TMP/esr"; fi
ffmpeg -hide_banner -loglevel error -y -framerate $((FPS * 2)) -i "$SRC/%08d.png" -c:v libx264 -crf "$CRF" -pix_fmt yuv420p "$OUT"
ls -la "$OUT"
