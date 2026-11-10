# The ENTIRE Story of The Exorcist: voice QA for the raw paragraph takes in voice_orig/ (same checks as
# ep08_conjuring/verify.py): (1) faster-whisper small.en transcript of every take against its paragraph text
# (numbers and years normalised to words), (2) longest pause inside each take (10 ms RMS envelope < -44 dBFS),
# (3) EBU R128 loudness per take, outliers > 1.5 LU from the median. Writes qa/voice_check.json and prints the
# ids to re-voice (python3 make_voice.py ELEVENLABS_JC_API_KEY --only <ids>), plus the total narration length.
# usage: python3 check_voice.py [--no-whisper]
import difflib, json, os, re, subprocess, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
P = json.load(open(os.path.join(HERE, 'paragraphs.json')))
ONES = 'zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen'.split()
TENS = 'x x twenty thirty forty fifty sixty seventy eighty ninety'.split()


def two(n): return [ONES[n]] if n < 20 else [TENS[n // 10]] + ([ONES[n % 10]] if n % 10 else [])


def num(n):
    if n < 100: return two(n)
    if 1000 < n < 2200:   # years: 1973 -> nineteen seventy three, 2027 -> twenty twenty seven, 1900 -> nineteen hundred
        hi, lo = divmod(n, 100)
        return two(hi) + (['hundred'] if lo == 0 else (['oh'] + two(lo) if lo < 10 else two(lo)))
    if n < 1000: return [ONES[n // 100], 'hundred'] + (two(n % 100) if n % 100 else [])
    return [str(n)]


def norm(t):
    out = []
    t = re.sub(r'(\d),(\d)', r'\1\2', t.lower()).replace('-', ' ').replace('%', ' percent')
    t = t.replace('1890s', 'eighteen nineties')
    for tok in t.split():
        tok = re.sub(r"[^a-z0-9']", '', tok)
        if tok:
            out += num(int(tok)) if tok.isdigit() else [tok]
    return out


def pcm(p):
    return np.frombuffer(subprocess.check_output(['ffmpeg', '-v', 'error', '-i', p, '-f', 's16le', '-ac', '1', '-ar', '16000', '-']),
                         np.int16).astype(np.float32) / 32768


def lufs(p):
    e = subprocess.run(['ffmpeg', '-v', 'info', '-i', p, '-af', 'ebur128', '-f', 'null', '-'], capture_output=True, text=True).stderr
    return float(re.findall(r'I:\s+(-?[\d.]+) LUFS', e)[-1])


def max_pause(x):
    h, w = 160, 480
    sp = np.array([20 * np.log10(np.sqrt(np.mean(x[i:i + w] ** 2)) + 1e-9) for i in range(0, len(x) - w, h)]) > -44
    best, i = 0.0, 0
    while i < len(sp):
        if sp[i]:
            i += 1
            continue
        j = i
        while j < len(sp) and not sp[j]:
            j += 1
        if i > 0 and j < len(sp):
            best = max(best, (j - i) * 0.01)
        i = j
    return best


def main():
    use_whisper = '--no-whisper' not in sys.argv
    if use_whisper:
        from faster_whisper import WhisperModel
        m = WhisperModel('small.en', device='cpu', compute_type='int8')
    rows, total = [], 0.0
    for p in P:
        f = os.path.join(HERE, 'voice_orig', p['id'] + '.mp3')
        if not os.path.exists(f):
            rows.append({'id': p['id'], 'missing': True})
            print(p['id'], 'MISSING')
            continue
        x = pcm(f)
        r = {'id': p['id'], 'secs': round(len(x) / 16000, 2), 'max_pause': round(max_pause(x), 2), 'lufs': lufs(f)}
        total += r['secs']
        if use_whisper:
            segs, _ = m.transcribe(x, word_timestamps=True, language='en', condition_on_previous_text=False)
            heard, want = norm(' '.join(w.word for g in segs for w in g.words)), norm(p['text'])
            r['diff'] = [d for d in difflib.ndiff(want, heard) if d[0] in '+-']
            r['match'] = round(difflib.SequenceMatcher(None, want, heard).ratio(), 3)
        rows.append(r)
        print(f"{p['id']} {r['secs']:6.2f}s  max pause {r['max_pause']:.2f}s  {r['lufs']:.1f} LUFS"
              + (f"  match {r['match']}" if use_whisper else ''), flush=True)
        if use_whisper and r['diff']:
            print('     ', ' '.join(r['diff']))
    have = [r for r in rows if not r.get('missing')]
    med = float(np.median([r['lufs'] for r in have])) if have else 0.0
    redo = sorted({r['id'] for r in have if r['max_pause'] > 1.2 or abs(r['lufs'] - med) > 1.5
                   or (use_whisper and r['match'] < 0.97)})
    missing = [r['id'] for r in rows if r.get('missing')]
    os.makedirs(os.path.join(HERE, 'qa'), exist_ok=True)
    json.dump({'rows': rows, 'median_lufs': med, 'total_secs': round(total, 1), 'redo': redo, 'missing': missing},
              open(os.path.join(HERE, 'qa', 'voice_check.json'), 'w'), indent=1)
    print(f'total narration {total / 60:.1f} min | median {med:.1f} LUFS | missing {missing or "none"}')
    print('re-voice candidates (pause > 1.2 s, loudness > 1.5 LU off, whisper match < 0.97; names can trip whisper, read the diff first):',
          ','.join(redo) or 'none')


if __name__ == '__main__':
    main()
