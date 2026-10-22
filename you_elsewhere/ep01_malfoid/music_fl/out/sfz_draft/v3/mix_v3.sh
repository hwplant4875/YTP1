#!/bin/bash
# Mix the three sfizz stems: warm piano, bass under it, drums ~13 dB below piano, convolution "Chamber Warm" send.
cd "$(dirname "$0")"
FC="[0:a]highpass=f=40,equalizer=f=220:t=q:w=0.9:g=1.5,equalizer=f=3200:t=q:w=1.2:g=-1.5,highshelf=f=6000:g=-3,volume=16dB[p];
[1:a]pan=mono|c0=0.5*c0+0.5*c1,highpass=f=34,lowpass=f=2600,equalizer=f=90:t=q:w=1:g=1.5,volume=7dB,pan=stereo|c0=c0|c1=c0[b];
[2:a]highshelf=f=6000:g=-4,lowpass=f=9500,volume=13dB,pan=stereo|c0=0.85*c0+0.15*c1|c1=c1[d];
[p][b][d]amix=inputs=3:normalize=0:duration=longest,asplit[dry][send];
[send]highpass=f=220,lowpass=f=5500[sendf];
[sendf][3:a]afir=dry=10:wet=10:length=1,volume=-11dB[wet];
[dry][wet]amix=inputs=2:normalize=0:duration=longest,lowpass=f=14000,afade=t=out:st=$(python -c "import subprocess;d=float(subprocess.run([\"ffprobe\",\"-v\",\"error\",\"-show_entries\",\"format=duration\",\"-of\",\"csv=p=0\",\"piano.wav\"],capture_output=True,text=True).stdout);print(round(d-4,2))"):d=4"
ffmpeg -y -loglevel error -i piano.wav -i bass.wav -i drums.wav -i ir_chamber_warm.wav -filter_complex "$FC" -ar 44100 -c:a pcm_f32le premaster.wav
G=$(ffmpeg -hide_banner -i premaster.wav -af loudnorm=I=-16:TP=-1.5:print_format=summary -f null - 2>&1 | awk '/Input Integrated/{i=$3} /Input True Peak/{tp=$4} END{g=-16-i; if (tp+g>-1.5) g=-1.5-tp; print g}')
echo "gain $G dB"
ffmpeg -y -loglevel error -i premaster.wav -af "volume=${G}dB" -ar 44100 -c:a pcm_s24le hedwig_trio_sfz_v3.wav
ffmpeg -y -loglevel error -i hedwig_trio_sfz_v3.wav -c:a libmp3lame -b:a 320k hedwig_trio_sfz_v3.mp3
ffmpeg -hide_banner -i hedwig_trio_sfz_v3.wav -af ebur128=peak=true -f null - 2>&1 | grep -E "I:|Peak:" | tail -2
