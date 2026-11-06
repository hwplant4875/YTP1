# EP04 copy of EP07 verify_v7.py (script_v3.md, playback order s00..s11).
# EP07 v7 voice QA: (1) whisper transcript of every final voice/<sec>.mp3 against the script_v7.md text (numbers normalised to
# words), (2) longest pause inside each take (10 ms RMS envelope < -44 dBFS), (3) loudness per take (EBU R128 integrated),
# so no take is noticeably louder or quieter than the others. usage: <whisper venv python> verify_v7.py
import json, os, re, subprocess, difflib
import numpy as np
from faster_whisper import WhisperModel
ORDER = ['s00', 's01', 's02', 's03', 's04', 's05', 's06', 's07', 's08', 's09', 's10', 's11']
src = open(os.environ.get('SCRIPT', 'script_v3.md'), encoding='utf-8').read().split('## Shot slots')[0]
TXT = {m.group(1): m.group(2).strip() for m in re.finditer(r'^## (s\d\d)[^\n]*\n(.+?)(?=\n## |\Z)', src, re.S | re.M)}
ONES = 'zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen'.split()
TENS = 'x x twenty thirty forty fifty sixty seventy eighty ninety'.split()
def two(n): return [ONES[n]] if n < 20 else [TENS[n // 10]] + ([ONES[n % 10]] if n % 10 else [])
def num(n):
    if n < 100: return two(n)
    if 1000 < n < 2100 or 2100 <= n < 2200:     # years: 1996 -> nineteen ninety six, 2022 -> twenty twenty two, 2127 -> twenty one twenty seven
        hi, lo = divmod(n, 100)
        return two(hi) + (['hundred'] if lo == 0 else (['oh'] + two(lo) if lo < 10 else two(lo)))
    if n < 1000: return [ONES[n // 100], 'hundred'] + (two(n % 100) if n % 100 else [])
    return [str(n)]
def norm(t):
    out = []
    for tok in re.sub(r'(\d),(\d)', r'\1\2', t.lower()).replace('-', ' ').replace('%', ' percent').split():
        tok = re.sub(r"[^a-z0-9']", '', tok)
        if not tok: continue
        out += num(int(tok)) if tok.isdigit() else [tok]
    return out
def pcm(p): return np.frombuffer(subprocess.check_output(['ffmpeg', '-v', 'error', '-i', p, '-f', 's16le', '-ac', '1', '-ar', '16000', '-']), np.int16).astype(np.float32) / 32768
def lufs(p):
    e = subprocess.run(['ffmpeg', '-v', 'info', '-i', p, '-af', 'ebur128', '-f', 'null', '-'], capture_output=True, text=True).stderr
    return float(re.findall(r'I:\s+(-?[\d.]+) LUFS', e)[-1])
m = WhisperModel('small.en', device='cpu', compute_type='int8')
bad, L = 0, {}
for s in ORDER:
    x = pcm(f'voice/{s}.mp3')
    segs, _ = m.transcribe(x, word_timestamps=True, language='en', condition_on_previous_text=False)
    heard = norm(' '.join(w.word for g in segs for w in g.words)); want = norm(TXT[s])
    diff = [d for d in difflib.ndiff(want, heard) if d[0] in '+-']
    h, w = 160, 480
    db = np.array([20 * np.log10(np.sqrt(np.mean(x[i:i + w] ** 2)) + 1e-9) for i in range(0, len(x) - w, h)])
    runs, i, sp = [], 0, db > -44
    while i < len(sp):
        if not sp[i]:
            j = i
            while j < len(sp) and not sp[j]: j += 1
            if i > 0 and j < len(sp): runs.append((j - i) * 0.01)
            i = j
        else: i += 1
    L[s] = lufs(f'voice/{s}.mp3')
    if diff: bad += 1
    print(f"{s} {len(x)/16000:6.2f}s  words {'SAME' if not diff else 'DIFF'} ({len(want)}/{len(heard)})  max pause {max(runs or [0]):.2f}s  {L[s]:.1f} LUFS")
    if diff: print('    ', ' '.join(diff))
med = float(np.median(list(L.values())))
print('sections with word differences:', bad, '| loudness median %.1f LUFS, outliers >1.5 LU:' % med, {k: v for k, v in L.items() if abs(v - med) > 1.5} or 'none')
