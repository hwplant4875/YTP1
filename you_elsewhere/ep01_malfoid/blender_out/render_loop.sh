#!/bin/bash
# re-launch Blender until all 1200 PNG frames exist (placeholders of crashed frames are removed first)
cd /c/Users/hw549/Downloads/YTP1/YouElsewhere/ep01_malfoid
for i in 1 2 3 4 5 6 7 8; do
  find frames_loop -name "*.png" -size 0 -delete 2>/dev/null
  n=$(ls frames_loop/*.png 2>/dev/null | wc -l)
  echo "attempt $i, frames present: $n"
  [ "$n" -ge 660 ] && break
  "/c/All The Programs/Blender/blender.exe" -b --factory-startup -P malfoid_blender.py -- "C:/Users/hw549/Downloads/YTP1/ye_wt/you_elsewhere/ep01_malfoid/assets" "C:/Users/hw549/Downloads/YTP1/YouElsewhere/ep01_malfoid" loop >> render_log_loop.txt 2>&1
done
ls frames_loop/*.png | wc -l
