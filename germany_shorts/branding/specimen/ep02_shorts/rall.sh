#!/bin/bash
# render + mux one short
s=$1; cd /tmp/claude-0/hbs
T=$(python3 -c "import json;print(json.load(open('plans.json'))['$s']['total'])")
SHORT=$s node render.mjs vert.mjs 60 0 $T out/${s}_v.mp4 >/dev/null && ffmpeg -y -v error -i out/${s}_v.mp4 -i out/${s}.wav -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart out/${s}.mp4 && echo "$s done"
