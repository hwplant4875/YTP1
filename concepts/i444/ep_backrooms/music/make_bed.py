# Backrooms special music bed (11/7 KST): ready-made free tracks from Mixkit (owner's 11/7 rule: never generate or compose BGM).
# The mp3s are third-party music, so they are never committed; this script downloads them into the work folder and builds the bed.
# Tracks (Mixkit Stock Music Free License, free for YouTube videos, no attribution needed), picked from Mixkit's scary, mysterious,
# dark, eerie, creepy and tension pages (133 tracks, 16 analysed) for no drums (percussive share < 0.07), no steady pulse (onset
# periodicity < 0.36), dark tone (centroid 640-880 Hz) and real stereo (L/R correlation 0.16-0.66):
#   588 Feedback Dreams  - slow analogue-synth chords that swell and hang (the liminal, 90s-video feel)      cold open to THE SLIT
#   633 Xanthos          - dense, dark ambient drone, no beat                                                  THE MAP to YOUR OLD HOME
#   540 Nield Grohm Hanging 3 - busier low texture with a long natural fade at the end                         dining room to the end
# Bed: 588 12-138 s -> 633 8-285 s -> 540 0-250 s, each cut before its own fade-out except the last, levelled to -16 LUFS, 8 s
# equal-power crossfades, then high-pass 30 Hz, low shelf -2 dB at 110 Hz, high shelf -4 dB at 3 kHz, 1.5 s fade in. About 10:37,
# longer than the episode (~9:55); render_br.py levels it to -39 LUFS, ducks it under the film lines and fades it at the end.
# usage: python music/make_bed.py <work_dir> <out.mp3>
#   laptop: python music\make_bed.py "E:\YTP2\Horror Ranked\EP08 Backrooms\1_work\music" "E:\YTP2\Horror Ranked\EP08 Backrooms\1_work\music\backrooms_bed_v1.mp3"
import os, re, subprocess, sys, urllib.request
D = sys.argv[1]; OUT = sys.argv[2]
os.makedirs(D, exist_ok=True)
SEG = [('588', 12.0, 138.0), ('633', 8.0, 285.0), ('540', 0.0, 250.0)]
for tid, _, _ in SEG:
    p = os.path.join(D, f'mixkit_{tid}.mp3')
    if not os.path.exists(p) or os.path.getsize(p) < 100000:
        req = urllib.request.Request(f'https://assets.mixkit.co/music/{tid}/{tid}.mp3', headers={'User-Agent': 'Mozilla/5.0'})
        open(p, 'wb').write(urllib.request.urlopen(req, timeout=60).read()); print('downloaded', p)
def lufs(args):
    o = subprocess.run(['ffmpeg', '-v', 'info', '-nostats'] + args + ['-af', 'ebur128', '-f', 'null', '-'], capture_output=True, text=True).stderr
    return float(re.findall(r'I:\s+(-?[\d.]+) LUFS', o)[-1])
parts = []
for i, (tid, a, b) in enumerate(SEG):
    src = os.path.join(D, f'mixkit_{tid}.mp3'); L = lufs(['-ss', str(a), '-to', str(b), '-i', src]); g = -16.0 - L
    w = os.path.join(D, f'seg{i}.wav')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(a), '-to', str(b), '-i', src, '-af', f'volume={g:.2f}dB', '-ar', '44100', '-ac', '2', w], check=True)
    parts.append(w); print(tid, a, b, f'{L:.1f} LUFS -> gain {g:+.1f} dB')
fc = '[0][1]acrossfade=d=8:c1=qsin:c2=qsin[x];[x][2]acrossfade=d=8:c1=qsin:c2=qsin[y];' \
     '[y]highpass=f=30,lowshelf=f=110:g=-2,highshelf=f=3000:g=-4[z]'
tmp = os.path.join(D, 'bed_tmp.wav')
subprocess.run(['ffmpeg', '-v', 'error', '-y'] + sum([['-i', p] for p in parts], []) + ['-filter_complex', fc, '-map', '[z]', tmp], check=True)
dur = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', tmp]))
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-af', 'afade=t=in:d=1.5', '-c:a', 'libmp3lame', '-b:a', '256k', OUT], check=True)
print('bed', OUT, round(dur, 1), 's', f'{lufs(["-i", OUT]):.1f} LUFS')
