# EP08 Conjuring music bed (11/9 KST): real free Mixkit tracks only, never generated music (owner rule 11/7, all channels). The mp3s are
# third-party music, so they are never committed: this script downloads them into the work folder and builds the bed there.
# Tracks (Mixkit Stock Music Free License, free for YouTube, no attribution needed), all already used on this channel and accepted by the
# owner (EP04 Freddy, which he picked over the generated bed, and the Backrooms special): 671 Piano Horror (Francisco Alvear),
# 188 Echoes (Andrew Ev), 633 Xanthos (Eugenio Mininni), 540 Nield Grohm Hanging 3. No drums, no steady pulse or ticking, real stereo.
# Checked 11/9 and left out: 612 Selpan (regular hits from 1:15), 565 Fallen (clicks throughout), 625 Fragments of Bangkok (mono),
# 615 Tapis (channels out of phase).
# Bed: Piano Horror 0-108 s -> Echoes 38-214 s -> Xanthos 8-285 s -> Hanging 3 0-250 s, each levelled to -16 LUFS, 8 s equal-power
# crossfades, high-pass 30 Hz, low shelf -2 dB at 110 Hz, high shelf -4 dB at 3 kHz, 1.5 s fade in, 8 s fade out. About 13 min, so the
# renderer never loops it; render_cj.py levels it to -39 LUFS and ducks it under the film lines.
# usage: python music/make_bed.py <work_dir> <out.mp3>
#   laptop: python music\make_bed.py "<EP08 folder>\1_work\music" "<EP08 folder>\1_work\music\conjuring_bed.mp3"
import os, re, subprocess, sys, urllib.request
D = sys.argv[1]; OUT = sys.argv[2]
os.makedirs(D, exist_ok=True)
SEG = [('671', 0, 108.0), ('188', 38.0, 214.0), ('633', 8.0, 285.0), ('540', 0, 250.0)]
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
fc = '[0][1]acrossfade=d=8:c1=qsin:c2=qsin[x];[x][2]acrossfade=d=8:c1=qsin:c2=qsin[y];[y][3]acrossfade=d=8:c1=qsin:c2=qsin[w];' \
     '[w]highpass=f=30,lowshelf=f=110:g=-2,highshelf=f=3000:g=-4[z]'
tmp = os.path.join(D, 'bed_tmp.wav')
subprocess.run(['ffmpeg', '-v', 'error', '-y'] + sum([['-i', p] for p in parts], []) + ['-filter_complex', fc, '-map', '[z]', tmp], check=True)
dur = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', tmp]))
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-af', f'afade=t=in:d=1.5,afade=t=out:st={dur - 8:.2f}:d=8', '-c:a', 'libmp3lame', '-b:a', '256k', OUT], check=True)
print('bed', OUT, round(dur, 1), 's', f'{lufs(["-i", OUT]):.1f} LUFS')
