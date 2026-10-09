#!/bin/bash
# usage: peek.sh video.mp4 out.jpg [fps] [cols] — contact sheet with timestamps
f=$1; o=$2; fps=${3:-1}; cols=${4:-8}
ffmpeg -loglevel error -y -i "$f" -vf "fps=$fps,scale=240:-1,drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:text='%{pts\:hms}':x=4:y=4:fontsize=16:fontcolor=yellow:box=1:boxcolor=black@0.6,tile=${cols}x8" -frames:v 1 "$o"
