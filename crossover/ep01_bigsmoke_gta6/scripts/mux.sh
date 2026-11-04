#!/bin/bash
# mux.sh video.mp4 audio.wav out.mp4
ffmpeg -loglevel error -y -i "$1" -i "$2" -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart "$3"
