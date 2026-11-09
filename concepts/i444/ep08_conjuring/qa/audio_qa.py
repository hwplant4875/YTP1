# QA on the render audio (EP08 copy of ../../ep_backrooms/qa/audio_qa.py): integrated loudness + true peak, silences over 1.5 s,
# the level of every film-line insert vs the narration around it, and clicks at insert cuts (sample-to-sample jumps in a 30 ms window).
# usage: python qa/audio_qa.py <render.mp4>
import json, sys, subprocess, re, os
import numpy as np
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
E = json.load(open(D + 'edl.json')); R = sys.argv[1]
o = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', R, '-af', 'ebur128=peak=true,silencedetect=n=-45dB:d=1.5', '-f', 'null', '-'],
                   capture_output=True, text=True).stderr
I = re.findall(r'I:\s+(-?[\d.]+) LUFS', o)[-1]; TP = re.findall(r'Peak:\s+(-?[\d.]+) dBFS', o)[-1]
print(f'integrated {I} LUFS, true peak {TP} dBFS'); sil = re.findall(r'silence_start: ([\d.]+)', o)
print('silences > 1.5 s at', sil or 'none')
x = np.frombuffer(subprocess.check_output(['ffmpeg', '-v', 'error', '-i', R, '-vn', '-ac', '1', '-ar', '48000', '-f', 's16le', '-']), np.int16).astype(np.float32) / 32768
def rms(a, b): s = x[int(a * 48000):int(b * 48000)]; return 20 * np.log10(np.sqrt(np.mean(s ** 2)) + 1e-9)
def click(t):
    s = x[int((t - 0.015) * 48000):int((t + 0.015) * 48000)]; return 20 * np.log10(np.max(np.abs(np.diff(s))) + 1e-9) if len(s) > 2 else -99
t0 = 0.0
for S in E['sections']:
    base = round(t0 * 30) / 30
    for k in S['inserts']:
        a, b = base + k['s0'], base + k['s1']
        line = f"{S['voice']} {k['kind']:6s} {a:7.2f}-{b:7.2f}  rms {rms(a, b):6.1f} dB  (narration before {rms(a - 3, a):6.1f} / after {rms(b, b + 3):6.1f})"
        print(line + f"  jump at cuts {click(a):5.1f} / {click(b):5.1f} dBFS" + (f"  sub: {k['sub']}" if k.get('sub') else ''))
    t0 += S['len']
