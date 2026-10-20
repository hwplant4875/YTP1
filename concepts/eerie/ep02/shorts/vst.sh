#!/bin/bash
# vst.sh spec.json full_tl.json outname t1,t2,...  -> vertical stills of a Short, tiled 6 per row to outname.jpg
D=$(cd "$(dirname "$0")/.." && pwd); S=$D/src; O=${TMPDIR:-/tmp}/vst_$(basename $3)
cat $S/eng_head.js $S/eng_props.js $S/eng_misc.js $S/eng2_common.js $S/eng2_props.js $S/eng2_scenes.js $S/eng_tail.js | sed -e 's/^  glitch(t, f);$//' -e 's/^  interfere(t, f, disturbance(t));$//' -e 's/^  caption(t, seg);$//' -e 's/^  ctx.globalAlpha = 0.07; ctx.drawImage(grainC.*$//' -e 's/^  ctx.fillStyle = bg; ctx.fillRect(0, by - 80, W, 160);$//' -e 's/^  ctx.fillStyle = vig; ctx.fillRect(0, 0, W, H);$//' > $D/engine_v.js
python3 $D/shorts/build.py $1 $2 $3_tl.json > /dev/null || exit 1
[ -z "$4" ] && exit 0
mkdir -p $O && find $O -name '*.jpg' -delete
cd $D && SH=$3_tl.json node render_v.mjs $2 stills $O $4 2>&1 | grep -v '^$' | tail -3
n=$(ls $O/*.jpg | wc -l); c=6
ffmpeg -y -loglevel error -pattern_type glob -i "$O/*.jpg" -vf "scale=270:480,tile=${c}x$(( (n+c-1)/c ))" -frames:v 1 $3.jpg && echo $3.jpg
