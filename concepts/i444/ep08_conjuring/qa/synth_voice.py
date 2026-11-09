# A SYNTHETIC test take for every section (shaped noise at Adam's pace, never real audio or a real voice) plus its character
# alignment and words.json, so build_edl.py can show every shot's speed before the real voice exists.
# Pace: 0.050 s per character, +0.32 s after . ? !, +0.12 s after a comma (calibrated to Adam's 16.9 chars/s in EP04).
# usage: python qa/synth_voice.py [out_folder=voice_synth] [script=script_v1_1.md] [sec_per_char=0.050]
#        then: set VOICE=voice_synth  (Windows) / VOICE=voice_synth (bash), python build_edl.py, python qa/dupes.py
# The out folder is git-ignored: never commit it, and never point VOICE at it for a real render.
import json, re, sys, os, subprocess
import numpy as np
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
OUT = D + (sys.argv[1] if len(sys.argv) > 1 else 'voice_synth').strip('/\\') + '/'
SCRIPT = sys.argv[2] if len(sys.argv) > 2 else 'script_v1_1.md'
CPS = float(sys.argv[3]) if len(sys.argv) > 3 else 0.050
SR = 44100
os.makedirs(OUT, exist_ok=True)
src = open(D + SCRIPT, encoding='utf-8').read()
TXT = {m.group(1): m.group(2).strip() for m in re.finditer(r'^## (s\d\d)[^\n]*\n(.+?)(?=\n## |\Z)', src, re.S | re.M)}
assert len(TXT) == 12, sorted(TXT)
W = {}
for k, txt in sorted(TXT.items()):
    t = 0.05; ch, st, en = [], [], []
    for c in txt:
        ch.append(c); st.append(round(t, 4)); en.append(round(t + CPS, 4)); t += CPS
        if c in '.?!': t += 0.32
        elif c == ',': t += 0.12
    L = t + 0.25
    x = np.zeros(int(L * SR), np.float32); rng = np.random.default_rng(1)
    words, cur = [], None
    for c, s, e in zip(ch, st, en):
        if c.isspace():
            if cur: words.append(cur); cur = None
        else: cur = [s, e, c] if cur is None else [cur[0], e, cur[2] + c]
    if cur: words.append(cur)
    for s, e, w in words:
        a, b = int(s * SR), int(e * SR); x[a:b] = 0.25 * rng.standard_normal(b - a) * np.sin(np.linspace(0, np.pi, b - a))
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 's16le', '-ar', str(SR), '-ac', '1', '-i', '-', '-c:a', 'libmp3lame', '-b:a', '64k',
                    OUT + f'{k}.mp3'], input=(x * 32767).astype(np.int16).tobytes(), check=True)
    json.dump({'characters': ch, 'character_start_times_seconds': st, 'character_end_times_seconds': en}, open(OUT + f'{k}.json', 'w'))
    W[k] = [[round(a, 3), round(b, 3), w] for a, b, w in words]
    print(k, round(L, 2), 's', len(words), 'words')
json.dump(W, open(OUT + 'words.json', 'w'))
print('synthetic takes in', OUT, '(test only; set VOICE to this folder for build_edl.py and the QA scripts)')
