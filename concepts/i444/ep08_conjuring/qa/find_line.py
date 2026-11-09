# Find a spoken film line in a clip: faster-whisper word timestamps over [t0, t1] of the clip, printed with absolute times, and the
# best match for the wanted words (in = 0.25 s before the first word, dur = line + 0.35 s, ready for an ins(...) in shots.py).
# usage: python qa/find_line.py <clip.mp4> <t0> <t1> "There's someone down there"   [model, default medium.en]
import sys, re, subprocess
import numpy as np
from faster_whisper import WhisperModel
src, t0, t1, want = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
model = sys.argv[5] if len(sys.argv) > 5 else 'medium.en'
x = np.frombuffer(subprocess.check_output(['ffmpeg', '-v', 'error', '-ss', str(t0), '-t', str(t1 - t0), '-i', src, '-vn', '-f', 's16le', '-ac', '1',
                                            '-ar', '16000', '-']), np.int16).astype(np.float32) / 32768
m = WhisperModel(model, device='cpu', compute_type='int8')
segs, _ = m.transcribe(x, word_timestamps=True, language='en', beam_size=5, condition_on_previous_text=False)
ws = [(t0 + w.start, t0 + w.end, w.word.strip()) for g in segs for w in g.words]
for a, b, w in ws: print(f'{a:8.2f} {b:8.2f}  {w}')
def n(s): return re.sub(r"[^a-z']", '', s.lower())
tgt = [n(t) for t in want.split() if n(t)]; best = None
for i in range(len(ws)):
    j, k, hit = i, 0, 0
    while j < len(ws) and k < len(tgt):
        if n(ws[j][2]) == tgt[k]: hit += 1; j += 1; k += 1
        else: break
    if hit and (best is None or hit > best[0]): best = (hit, i, j - 1)
if best:
    h, i, j = best; a, b = ws[i][0], ws[j][1]
    print(f'\nbest: "{" ".join(w for _, _, w in ws[i:j + 1])}" ({h}/{len(tgt)} words)  {a:.2f}-{b:.2f}  ->  in {a - 0.25:.2f}, seconds {b - a + 0.6:.2f}')
else: print('\nnot found; read the words above')
