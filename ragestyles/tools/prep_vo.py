"""Speed up + trim VO lines and rescale word timings. usage: python3 prep_vo.py vo_dir tempo
Writes <id>_f.wav and adds 'fw' (fast words) + 'fdur' to <id>.json."""
import json, glob, os, subprocess, sys
import numpy as np
d, tempo = sys.argv[1], float(sys.argv[2])
for jp in sorted(glob.glob(f'{d}/l*.json')):
    j = json.load(open(jp)); mp = jp[:-5] + '.mp3'; wav = jp[:-5] + '_f.wav'
    a = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', mp, '-af', f'atempo={tempo}', '-f', 'f32le', '-ac', '1', '-ar', '48000', '-'],
                                     capture_output=True, check=True).stdout, np.float32)
    thr = 10 ** (-42 / 20); idx = np.where(np.abs(a) > thr)[0]
    s0 = max(idx[0] - int(.02 * 48000), 0); s1 = min(idx[-1] + int(.08 * 48000), len(a))
    a = a[s0:s1]
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', '48000', '-ac', '1', '-i', '-', wav], input=a.tobytes(), check=True)
    off = s0 / 48000
    j['fw'] = [{'w': w['w'], 's': round(w['s'] / tempo - off, 3), 'e': round(w['e'] / tempo - off, 3)} for w in j['words']]
    j['fdur'] = round(len(a) / 48000, 3)
    json.dump(j, open(jp, 'w'), indent=1); print(os.path.basename(jp), j['fdur'])
