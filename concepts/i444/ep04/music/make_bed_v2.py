# EP04 Freddy music bed v2 (11/7 KST): real free tracks from Mixkit instead of generated music. The owner's 11/7 rule for every
# channel: never generate or assemble BGM ourselves, download fitting ready-made free tracks (Mixkit). The mp3s are third-party
# music, so they are never committed; this script downloads them into the work folder and builds the bed there.
# Tracks (Mixkit Stock Music Free License, free for YouTube videos, no attribution needed):
#   671 Piano Horror (Francisco Alvear), 188 Echoes (Andrew Ev), 633 Xanthos (Eugenio Mininni). Picked from Mixkit's horror,
#   creepy and scary pages for no drums, no steady pulse or ticking, dark tone (spectral centroid 490-680 Hz), real stereo.
# Bed: Piano Horror 0-108 s -> Echoes 38-214 s -> Xanthos 0-200 s, each cut before its own fade-out so the joins never dip,
# each levelled to -16 LUFS, 8 s equal-power crossfades, then high-pass 30 Hz, low shelf -2 dB at 110 Hz, high shelf -4 dB at
# 3 kHz, 1.5 s fade in, 8 s fade out. Result 7:48 (468 s), about -16.6 LUFS, stereo; the renderer levels it to -39 LUFS.
# usage: python make_bed_v2.py <work_dir> <out.mp3>
#   laptop: python music\make_bed_v2.py "E:\YTP2\Horror Ranked\EP04 Freddy Krueger\1_work\music" "E:\YTP2\Horror Ranked\EP04 Freddy Krueger\1_work\music\freddy_bed_v2.mp3"
import os, re, subprocess, sys, urllib.request
D = sys.argv[1]; OUT = sys.argv[2]
os.makedirs(D, exist_ok=True)
SEG = [('671', 0, 108.0), ('188', 38.0, 214.0), ('633', 0, 200.0)]
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
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-af', f'afade=t=in:d=1.5,afade=t=out:st={dur - 8:.2f}:d=8', '-c:a', 'libmp3lame', '-b:a', '256k', OUT], check=True)
print('bed', OUT, round(dur, 1), 's', f'{lufs(["-i", OUT]):.1f} LUFS')
