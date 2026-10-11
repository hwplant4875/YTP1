#!/bin/bash
# one render job: job.sh <name>   reads out/batch/<name>/args (dur), race file marble/race_<name>.json, audio out/batch/<name>/audio.wav
cd /home/user/YTP1/concepts
N=$1; D=out/batch/$N
[ -f $D/done ] && exit 0
DUR=$(cat $D/dur)
node render.mjs marble/scene.js $D/video.mp4 --w 1080 --h 1920 --fps 60 --dur $DUR --shot race_$N.json > $D/render.log 2>&1 || { echo fail > $D/failed; exit 1; }
ffmpeg -y -v error -i $D/video.mp4 -i $D/audio.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 256k -shortest -movflags +faststart $D/final.mp4 && touch $D/done
