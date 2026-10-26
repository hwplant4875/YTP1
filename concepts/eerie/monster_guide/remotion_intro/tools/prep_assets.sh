#!/usr/bin/env bash
# Pre-processes audio that Remotion cannot EQ itself, and makes the film-grain tiles.
# Remotion then layers these with <Audio volume={curve}> inside <Sequence>s.
set -euo pipefail
cd "$(dirname "$0")/.."
A=public/audio; M=public/mix
# music bed: steady section 6-16 s, gentle high-shelf cut above 3 kHz, STEREO kept (no -ac)
ffmpeg -v error -y -ss 6 -t 10 -i $A/music_pizz.mp3 -af "highshelf=f=3000:g=-6:t=s:w=0.7,lowpass=f=9000" -c:a pcm_s16le $M/music_bed.wav
# creak and room tone are recorded very low: lift them, keep highs soft
ffmpeg -v error -y -i $A/creak.mp3 -af "volume=24dB,highshelf=f=5000:g=-4,alimiter=limit=0.7" -c:a pcm_s16le $M/creak.wav
ffmpeg -v error -y -t 8 -i $A/roomtone.mp3 -af "volume=26dB,lowpass=f=6000" -c:a pcm_s16le $M/roomtone.wav
# soften the top end of the bright one-shots ("no harsh highs")
for s in chime whoosh riser; do ffmpeg -v error -y -i $A/$s.mp3 -af "highshelf=f=4500:g=-6,lowpass=f=11000" -c:a pcm_s16le $M/$s.wav; done
for s in hit thud; do ffmpeg -v error -y -i $A/$s.wav -af "highshelf=f=4500:g=-5" -c:a pcm_s16le $M/$s.wav; done
ffmpeg -v error -y -i $A/heartbeat.mp3 -af "lowpass=f=3000" -c:a pcm_s16le $M/heartbeat.wav
# grain tiles (deterministic seeds)
python3 - <<'PY'
import numpy as np
from PIL import Image
for k in range(3):
    rng = np.random.default_rng(1000 + k)
    g = np.clip(128 + rng.normal(0, 46, (512, 512)), 0, 255).astype(np.uint8)
    Image.fromarray(g, 'L').save(f'public/fx/grain{k}.png')
PY
echo done
