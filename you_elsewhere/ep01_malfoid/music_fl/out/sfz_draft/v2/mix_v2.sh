#!/bin/bash
# v2 mix: felt-soft piano (softer layers, highs rolled off ~5 kHz, gentle transient taming), long warm hall clearly audible.
cd "$(dirname "$0")"
FC="[0:a]highpass=f=40,lowpass=f=5000,lowpass=f=6500,highshelf=f=2800:g=-2.5,equalizer=f=230:t=q:w=0.9:g=1.5,volume=22dB,acompressor=threshold=-24dB:ratio=2.2:attack=1.5:release=180:knee=6[p];
[1:a]pan=mono|c0=0.5*c0+0.5*c1,highpass=f=34,lowpass=f=1800,equalizer=f=90:t=q:w=1:g=1.5,volume=9dB,pan=stereo|c0=c0|c1=c0[b];
[2:a]highshelf=f=5000:g=-6,lowpass=f=8000,volume=15dB,pan=stereo|c0=0.85*c0+0.15*c1|c1=c1[d];
[p][b][d]amix=inputs=3:normalize=0:duration=longest,asplit[dry][send];
[send]adelay=25|25,highpass=f=180,lowpass=f=4500[sendf];
[sendf][3:a]afir=dry=10:wet=10:length=1,volume=-7dB[wet];
[dry][wet]amix=inputs=2:normalize=0:duration=longest,afade=t=out:st=150:d=6"
ffmpeg -y -loglevel error -i piano.wav -i bass.wav -i drums.wav -i ir_hall_warm.wav -filter_complex "$FC" -ar 44100 -c:a pcm_f32le premaster.wav
G=$(ffmpeg -hide_banner -i premaster.wav -af loudnorm=I=-17:TP=-1.5:print_format=summary -f null - 2>&1 | awk '/Input Integrated/{i=$3} /Input True Peak/{tp=$4} END{g=-17-i; if (tp+g>-1.5) g=-1.5-tp; print g}')
echo "gain $G dB"
ffmpeg -y -loglevel error -i premaster.wav -af "volume=${G}dB" -ar 44100 -c:a pcm_s24le hedwig_trio_sfz_v2.wav
ffmpeg -y -loglevel error -i hedwig_trio_sfz_v2.wav -c:a libmp3lame -b:a 320k hedwig_trio_sfz_v2.mp3
ffmpeg -hide_banner -i hedwig_trio_sfz_v2.wav -af ebur128=peak=true -f null - 2>&1 | grep -E "I:|Peak:" | tail -2
