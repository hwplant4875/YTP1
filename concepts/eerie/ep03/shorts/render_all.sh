#!/bin/bash
# render_all.sh full_tl.json voicedir sfxdir outdir s1 s2 ...  -> outdir/<name>.mp4 (60 fps, mixed)
D=$(cd "$(dirname "$0")/.." && pwd); TL=$1; V=$2; X=$3; O=$4; shift 4
MUSIC=/mnt/project-files/eerie_rules/ep01_cat_knocks/music_options/pizzicato_v3/B_original_center.mp3
for n in $@; do
  bash $D/shorts/vst.sh $D/shorts/$n.json $TL $O/$n || exit 1
  T=$(python3 -c "import json;print(json.load(open('$O/${n}_tl.json'))['total'])")
  cd $D && SH=$O/${n}_tl.json FPS=60 node render_v.mjs $TL clip $O/${n}_video.mp4 0 $T 4 2>&1 | tail -1
  python3 $D/mix_short.py $O/${n}_tl.json $V $X $MUSIC $O/${n}_mix.wav 0.55 > /dev/null || exit 1
  ffmpeg -y -loglevel error -i $O/${n}_video.mp4 -i $O/${n}_mix.wav -c:v copy -c:a aac -b:a 192k -shortest $O/$n.mp4 && rm $O/${n}_video.mp4 && echo "DONE $n $T"
done
