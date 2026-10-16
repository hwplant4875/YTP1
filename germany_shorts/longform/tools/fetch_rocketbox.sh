#!/bin/bash
# Fetch one Microsoft Rocketbox avatar (MIT) and convert it for lib_human.js.
# usage: tools/fetch_rocketbox.sh Adults/Male_Adult_08     (run from germany_shorts/longform)
set -e
d=$1; n=${d#*/}; R=https://raw.githubusercontent.com/microsoft/Microsoft-Rocketbox/master/Assets/Avatars/$d
A=assets/rocketbox/$n; mkdir -p $A; T=$(mktemp -d)
curl -sf -o $A/${n}_facial.fbx $R/Export/${n}_facial.fbx
P=$(strings $A/${n}_facial.fbx | grep -ioE '[a-z0-9_]+_head_color\.tga' | head -1); P=${P%_head_color.tga}
g(){ curl -sf -o $T/t.tga $R/Textures/${P}_$1.tga; }
for f in body_color head_color; do g $f; convert $T/t.tga -quality 90 $A/${P}_$f.jpg; done
for f in body_normal head_normal; do g $f; convert $T/t.tga -resize 1024x1024 -quality 92 $A/${P}_$f.jpg; done
for p in body head; do g ${p}_specular; convert $T/t.tga -resize 1024x1024 -colorspace gray -negate -quality 88 $A/${P}_${p}_rough.jpg; done
g opacity_color; convert $T/t.tga -resize 1024x1024 $A/${P}_opacity_color.png
rm -rf $T; echo "$n tex=$P"; du -sh $A
