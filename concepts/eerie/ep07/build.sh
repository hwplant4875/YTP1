#!/bin/bash
# Build engine.js from src/ (order matters), syntax-check it, and optionally render a contact sheet of stills.
# ./build.sh                       -> engine.js (+ engine_th.js for the thumbnail scenes)
# ./build.sh timeline.json name t1,t2,...   -> also renders stills to /tmp/st_name and tiles them to name.jpg (3 per row)
D=$(cd "$(dirname "$0")" && pwd); S=$D/src
cat $S/eng_head.js $S/eng_props.js $S/eng_misc.js $S/eng2_common.js $S/eng2_props.js $S/eng2_scenes.js $S/eng_tail.js > $D/engine.js || exit 1
cat $S/eng_head.js $S/eng_props.js $S/eng_misc.js $S/eng2_common.js $S/eng2_props.js $S/eng2_scenes.js $D/thumb_scene.js $S/eng_tail.js > $D/engine_th.js
node -e "new Function(require('fs').readFileSync('$D/engine.js','utf8'))" || exit 1
[ -z "$3" ] && exit 0
O=${TMPDIR:-/tmp}/st_$2; mkdir -p $O && find $O -name '*.jpg' -delete
cd $D && node render.mjs $1 stills $O $3 2>&1 | grep -v '^$' | tail -3
n=$(ls $O/*.jpg | wc -l); c=3; [ $n -le 4 ] && c=2
ffmpeg -y -loglevel error -pattern_type glob -i "$O/*.jpg" -vf "scale=640:360,tile=${c}x$(( (n+c-1)/c ))" -frames:v 1 $2.jpg && echo $2.jpg
