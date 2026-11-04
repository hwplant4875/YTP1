# EP07 v7: voice_orig/words.json from the ElevenLabs alignment of each full take (exact script words, so shot anchors can be
# written straight from script_v7.md), instead of whisper (whisper misspells names and was ~0.1 s less accurate on onsets:
# mean |error| 0.097 s vs 0.064 s against the audio envelope, measured on the v6 takes). A word that follows a pause is snapped
# to the real speech onset (10 ms RMS envelope > -40 dBFS) when that onset is within 0.25 s. tighten2.py then re-times it.
# usage: python3 al_words.py [secs...]
import json, subprocess, sys
import numpy as np
SR = 16000
ORDER = ['s00', 's01', 's04', 's05', 's06', 's07', 's08', 's09', 's02', 's10', 's03', 's11', 's12', 's13']
def pcm(p): return np.frombuffer(subprocess.check_output(['ffmpeg', '-v', 'error', '-i', p, '-f', 's16le', '-ac', '1', '-ar', str(SR), '-']), np.int16).astype(np.float32) / 32768
def words(al):
    ch, a, b = al['characters'], al['character_start_times_seconds'], al['character_end_times_seconds']
    out, cur = [], None
    for c, s, e in zip(ch, a, b):
        if c.isspace():
            if cur: out.append(cur); cur = None
        else: cur = [s, e, c] if cur is None else [cur[0], e, cur[2] + c]
    if cur: out.append(cur)
    return out
def onsets(x):
    h, w = 160, 320
    db = np.array([20 * np.log10(np.sqrt(np.mean(x[i:i + w] ** 2)) + 1e-9) for i in range(0, len(x) - w, h)])
    ons, q = [], 99
    for i, v in enumerate(db > -40):
        if not v: q += 1
        else:
            if q >= 12: ons.append(i * 0.01)
            q = 0
    return ons
secs = sys.argv[1:] or ORDER
try: W = json.load(open('voice_orig/words.json'))
except FileNotFoundError: W = {}
for s in secs:
    A = words(json.load(open(f'voice_orig/{s}.json'))); ons = onsets(pcm(f'voice_orig/{s}.mp3')); n = 0
    for i, w in enumerate(A):
        if i == 0 or w[0] - A[i - 1][1] > 0.1:
            c = [t for t in ons if abs(t - w[0]) <= 0.25 and (i == 0 or t > A[i - 1][1])]
            if c:
                t = min(c, key=lambda t: abs(t - w[0])); w[0] = round(min(t, w[1] - 0.05), 3); n += 1
    W[s] = [[round(a, 3), round(b, 3), t] for a, b, t in A]
    print(s, len(A), 'words,', n, 'onsets snapped')
json.dump(W, open('voice_orig/words.json', 'w'))
