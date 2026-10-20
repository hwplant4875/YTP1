#!/bin/bash
# vst.sh short name t1,t2,...  -> vertical stills tiled to $SS/name.jpg
E=/tmp/claude-0/-home-user-YTP1/db7b424d-ffe5-5abf-bc8b-b81061ddb974/scratchpad/eerie/ep01
SS=/tmp/claude-0/-home-user-YTP1/db7b424d-ffe5-5abf-bc8b-b81061ddb974/scratchpad/eerie/shorts
D=/home/user/YTP1/concepts/eerie/ep01
cd $E && cat eng_head.js eng_props.js eng_misc.js eng_scenes.js eng_tail.js | sed -e 's/^  glitch(t, f);$//' -e 's/^  interfere(t, f, disturbance(t));$//' -e 's/^  caption(t, seg);$//' -e 's/^  ctx.globalAlpha = 0.07; ctx.drawImage(grainC.*$//' -e 's/^  ctx.fillStyle = bg; ctx.fillRect(0, by - 80, W, 160);$//' -e 's/^  ctx.fillStyle = vig; ctx.fillRect(0, 0, W, H);$//' > $D/engine_v.js
cp $SS/short_v.js $D/short_v.js
python3 $SS/build.py $SS/$1.json $E/tl10.json $SS/$1_tl.json >/dev/null
mkdir -p $SS/st_$2 && find $SS/st_$2 -name '*.jpg' -delete
cd $D && SH=$SS/$1_tl.json node render_v.mjs $E/tl10.json stills $SS/st_$2 $3 2>&1 | grep -v '^$' | tail -3
n=$(ls $SS/st_$2/*.jpg | wc -l); c=6
ffmpeg -y -loglevel error -pattern_type glob -i "$SS/st_$2/*.jpg" -vf "scale=270:480,tile=${c}x$(( (n+c-1)/c ))" -frames:v 1 $SS/$2.jpg && echo $SS/$2.jpg
