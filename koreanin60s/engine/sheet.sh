#!/bin/bash
# usage: sheet.sh <builddir>  -> <builddir>/sheet.png, one frame at the end of each scene
D=$1
TS=$(python3 -c "
import json,re
h=open('$D/short.html').read(); d=json.loads(re.search(r'const D=(\{.*?\});const IMG',h,re.S).group(1))
print(','.join(f'{min(s[\"t1\"],d[\"END\"])-0.35:.2f}' for s in d['scenes']))")
NODE_PATH=/opt/node22/lib/node_modules node $(dirname $0)/grab.js $D $TS
cd $D; n=$(echo $TS | tr ',' '\n' | wc -l); ins=""; for t in ${TS//,/ }; do ins="$ins -i t_$t.png"; done
lay=$(python3 -c "print('|'.join(f'{i*1080}_0' for i in range($n)))")
ffmpeg -v error -y $ins -filter_complex "xstack=inputs=$n:layout=$lay,scale=$((n*300)):-1" sheet.png; rm -f t_*.png
