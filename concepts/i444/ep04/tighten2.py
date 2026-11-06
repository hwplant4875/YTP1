# EP04 copy of EP07 tighten2.py.
# EP07 v4 (owner 11/04: "remove the silence between voice lines, natural, no stops"; MAX quality pass). Breath-aware version of
# tighten.py: pauses are found on a 10 ms RMS envelope (speech = louder than THR dBFS), so quiet breaths count as pause too
# (silencedetect is peak-based and missed them, leaving 0.6-1.0 s gaps). Every pause inside a take becomes KEEP_A s of the
# word's tail + KEEP_B s before the next word (keeps the start of the in-breath, so it still sounds human), head 0.03 s,
# tail 0.15 s. Reads the untouched takes in voice_orig/, writes voice/ (mp3, alignment json, words.json re-timed with the
# same cut map, exactly like tighten.py), so every cut / caption / card anchor follows the new timing.
import json, os, subprocess
import numpy as np
THR, MINP, KEEP_A, KEEP_B, HEAD, TAIL, FADE, HOP = -44.0, 0.32, 0.10, 0.20, 0.03, 0.15, 0.008, 0.01
W = json.load(open('voice_orig/words.json'))
def pcm(p): return np.frombuffer(subprocess.check_output(['ffmpeg', '-v', 'error', '-i', p, '-f', 's16le', '-ac', '1', '-ar', '16000', '-']), np.int16).astype(np.float32) / 32768
def speech_mask(x, sr=16000):
    h, w = int(HOP * sr), int(0.03 * sr)
    db = np.array([20 * np.log10(np.sqrt(np.mean(x[i:i + w] ** 2)) + 1e-9) for i in range(0, max(1, len(x) - w), h)])
    sp = db > THR
    # drop isolated blips (clicks, breath peaks) shorter than 50 ms
    i = 0
    while i < len(sp):
        if sp[i]:
            j = i
            while j < len(sp) and sp[j]: j += 1
            if j - i < 5 and i > 0 and j < len(sp): sp[i:j] = False
            i = j
        else: i += 1
    return sp
def pauses(sp):
    out, i = [], 0
    while i < len(sp):
        if not sp[i]:
            j = i
            while j < len(sp) and not sp[j]: j += 1
            out.append((i * HOP, j * HOP)); i = j
        else: i += 1
    return out
def dur(p): return float(subprocess.check_output(['ffprobe', '-v', '0', '-show_entries', 'format=duration', '-of', 'csv=p=0', p]))
report = {}
for seg in sorted(W):
    src = f'voice_orig/{seg}.mp3'; D = dur(src); sp = speech_mask(pcm(src)); P = pauses(sp)
    cuts = []
    for a, b in P:
        if a <= 0.0: cuts.append((0.0, max(0.0, b - HEAD)))
        elif b >= D - 0.05: cuts.append((min(D, a + TAIL), D))
        elif b - a >= MINP and b - a > KEEP_A + KEEP_B: cuts.append((a + KEEP_A, b - KEEP_B))
    keep, t = [], 0.0
    for a, b in cuts:
        if a > t: keep.append((t, a))
        t = max(t, b)
    if t < D: keep.append((t, D))
    def mp(x):
        out = 0.0
        for a, b in keep:
            if x <= a: return out
            if x <= b: return out + x - a
            out += b - a
        return out
    parts = ''.join(f"[0:a]atrim={a:.4f}:{b:.4f},asetpts=PTS-STARTPTS,afade=t=in:d={FADE},afade=t=out:st={max(0, b - a - FADE):.4f}:d={FADE}[k{i}];"
                    for i, (a, b) in enumerate(keep))
    fc = parts + ''.join(f'[k{i}]' for i in range(len(keep))) + f'concat=n={len(keep)}:v=0:a=1[o]'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-filter_complex', fc, '-map', '[o]', '-c:a', 'libmp3lame', '-b:a', '192k', f'voice/{seg}.mp3'], check=True)
    al = json.load(open(f'voice_orig/{seg}.json'))
    for k in ('character_start_times_seconds', 'character_end_times_seconds'): al[k] = [round(mp(x), 4) for x in al[k]]
    json.dump(al, open(f'voice/{seg}.json', 'w'))
    W[seg] = [[round(mp(a), 3), round(mp(b), 3), w] for a, b, w in W[seg]]
    report[seg] = (round(D, 2), round(sum(b - a for a, b in keep), 2), len(cuts))
    print(seg, D.__round__(2), '->', report[seg][1], len(cuts), 'cuts', flush=True)
json.dump(W, open('voice/words.json', 'w'))
