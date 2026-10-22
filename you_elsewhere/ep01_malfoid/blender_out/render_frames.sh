#!/bin/bash
# re-launch Blender until all 1200 PNG frames exist (placeholders of crashed frames are removed first)
cd /c/Users/hw549/Downloads/YTP1/YouElsewhere/ep01_malfoid
for i in 1 2 3 4 5 6 7 8; do
  find frames_v3 -name "*.png" -size 0 -delete 2>/dev/null
  n=$(ls frames_v3/*.png 2>/dev/null | wc -l)
  echo "attempt $i, frames present: $n"
  [ "$n" -ge 1200 ] && break
  "/c/All The Programs/Blender/blender.exe" -b --factory-startup -P malfoid_blender.py -- "C:/Users/hw549/Downloads/YTP1/ye_wt/you_elsewhere/ep01_malfoid/assets" "C:/Users/hw549/Downloads/YTP1/YouElsewhere/ep01_malfoid" frames >> render_log_v2.txt 2>&1
done
ls frames_v3/*.png | wc -l
