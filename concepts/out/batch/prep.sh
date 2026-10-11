#!/bin/bash
# prep.sh <name> <seed>: race json + audio for one batch short, then queue it
set -e
N=$1; S=$2; C=/home/user/YTP1/concepts; D=$C/out/batch/$N; mkdir -p $D
SND=$(python3 -c "import json;print({p['name']:p['sound'] for p in json.load(open('$C/out/batch/plan.json'))}['$N'])")
cd $C/marble && DATA=data/$N.json OUT=./race_$N.json node sim.mjs $S | tail -3
cd $C/audio && RACE=race_$N.json OUT=$D/raw.wav python3 mix.py marble $SND | grep '^duration' | awk '{print $2}' > $D/dur
ffmpeg -y -v error -i $D/raw.wav -af loudnorm=I=-14:TP=-1.5:LRA=11 -ar 48000 $D/audio.wav
echo "$N seed $S sound $SND dur $(cat $D/dur)"
echo $N >> $C/out/batch/queue.txt
