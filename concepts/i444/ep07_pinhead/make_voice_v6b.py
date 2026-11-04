# EP07 v6b (owner 11/04 21:00 KST: "isn't a 55% start too low?"). Every earlier episode started at 80-99%, so the five safest
# entries move up and the ladder passes every tier once: Hellbound 85 Easy, Revelations 70 Don't Worry, 1987 55 Close Call,
# Hellseeker 45 Better Run, 2022 35 Almost Dead. Bloodline..Hell on Earth and the playback order are unchanged.
# Only the last sentence ("Survival rate: ...") of s04-s08 is re-voiced (Adam / eleven_v4 / with-timestamps, previous_text =
# the rest of the section, next_text = the next section in playback order). It is joined to the untouched v6 take at the
# quietest 20 ms inside the pause before "Survival rate", level-matched to the old last sentence, and the alignment is rebuilt.
# The v6 raw takes are kept in voice_orig/v6/. Also rewrites the five headings + last sentences in script_v1.md and the pct
# values in stats.json.
# Then: w3.py s04 s05 s06 s07 s08 (whisper) -> python3 tighten2.py -> verify_voice.py
# usage: python3 make_voice_v6b.py [--dry]
import json, os, re, sys, base64, shutil, subprocess, urllib.request
import numpy as np
DRY = '--dry' in sys.argv
K = os.environ.get('ELEVENLABS_JC_API_KEY', '')
VOICE = 's3TPKV1kjDlVtZbl4Ksh'   # Adam
NEW = {'s04': (85, 'eighty-five'), 's05': (70, 'seventy'), 's06': (55, 'fifty-five'), 's07': (45, 'forty-five'),
       's08': (35, 'thirty-five')}
TIERS = [('Slaughtered', 25), ('Almost Dead', 40), ('Better Run', 50), ('Close Call', 60), ("Don't Worry", 80), ('Easy', 101)]
def tier(p): return next(n for n, t in TIERS if p <= t)          # same rule as ep03/anim.py tier()
SR = 44100

# 1. script text
md = open('script_v1.md', encoding='utf-8').read()
body, facts = md.split('## Fact notes', 1)
for k, (p, w) in NEW.items():
    body, n = re.subn(rf'^(## {k} [^\n]*?), \d+%, [^\n]+$', lambda m: f'{m.group(1)}, {p}%, {tier(p)}', body, flags=re.M)
    assert n == 1, k
    m = re.search(rf'^## {k}[^\n]*\n(.+?)(?=\n## |\Z)', body, re.S | re.M)
    blk = m.group(1); j = blk.rfind('Survival rate:')
    blk2 = blk[:j] + re.sub(r'^Survival rate: [a-z-]+ percent\.', f'Survival rate: {w} percent.', blk[j:])
    assert blk2 != blk, k
    body = body[:m.start(1)] + blk2 + body[m.end(1):]
SEC = [(m.group(1), m.group(2).strip()) for m in re.finditer(r'^## (s\d\d)[^\n]*\n(.+?)(?=\n## |\Z)', body, re.S | re.M)]
TXT = dict(SEC); ORDER = [k for k, _ in SEC]
for k in NEW: print(k, '|', re.search(rf'^## {k}[^\n]*', body, re.M).group(0), '|', TXT[k][TXT[k].rfind('Survival'):])

def pcm(p):
    return np.frombuffer(subprocess.check_output(['ffmpeg', '-v', 'error', '-i', p, '-f', 's16le', '-ac', '1', '-ar', str(SR), '-']),
                         np.int16).astype(np.float32) / 32768
def srms(v): f = v[np.abs(v) > 0.01]; return np.sqrt(np.mean(f ** 2)) if len(f) else 1
def tts(text, prev, nxt):
    body = {'text': text, 'model_id': 'eleven_v4', 'previous_text': prev, 'next_text': nxt}
    r = urllib.request.Request(f'https://api.elevenlabs.io/v1/text-to-speech/{VOICE}/with-timestamps', data=json.dumps(body).encode(),
                               headers={'xi-api-key': K, 'Content-Type': 'application/json'})
    d = json.load(urllib.request.urlopen(r, timeout=300))
    return base64.b64decode(d['audio_base64']), d['alignment']

chars = sum(len(TXT[k][TXT[k].rfind('Survival rate'):]) for k in NEW)
print('characters to voice:', chars)
if not DRY:
    open('script_v1.md', 'w', encoding='utf-8').write(body + '## Fact notes' + facts)
    st = json.load(open('stats.json'))
    for e in st['entries']:
        if e['sec'] in NEW: e['pct'] = NEW[e['sec']][0]
    json.dump(st, open('stats.json', 'w'), indent=1)
    os.makedirs('voice_orig/v6', exist_ok=True)

# 2. voice
for k in NEW:
    src = f'voice_orig/v6/{k}' if os.path.exists(f'voice_orig/v6/{k}.mp3') else f'voice_orig/{k}'
    if not DRY and src == f'voice_orig/{k}':
        for ext in ('mp3', 'json'): shutil.copy(f'voice_orig/{k}.{ext}', f'voice_orig/v6/{k}.{ext}')
        src = f'voice_orig/v6/{k}'
    old = json.load(open(src + '.json')); s = ''.join(old['characters'])
    j = s.rfind('Survival rate'); i = j - 1
    while s[i] == ' ': i -= 1                                      # i = the full stop before "Survival rate"
    txt = TXT[k]; jt = txt.rfind('Survival rate')
    before, last = txt[:jt].strip(), txt[jt:].strip()
    assert ' '.join(s[:i + 1].split()) == ' '.join(before.split()), (k, s[:i + 1][-80:], before[-80:])
    t0, t1 = old['character_end_times_seconds'][i], old['character_start_times_seconds'][j]
    x = pcm(src + '.mp3'); w = int(0.02 * SR)
    a, b = int(max(0, t0 - 0.03) * SR), int((t1 + 0.03) * SR)
    rms = [np.sqrt(np.mean(x[n:n + w] ** 2)) for n in range(a, max(a + 1, b - w), w // 2)]
    cut = (a + int(np.argmin(rms)) * (w // 2) + w // 2) / SR
    nxt = TXT[ORDER[ORDER.index(k) + 1]][:300]
    print(k, f'pause {t0:.2f}-{t1:.2f} s, cut at {cut:.3f} s, old last sentence: "{s[j:]}" -> "{last}"', flush=True)
    if DRY: continue
    audio, al = tts(last, before[-400:], nxt)
    tmp = f'voice_orig/v6/{k}_last.mp3'; open(tmp, 'wb').write(audio); json.dump(al, open(tmp[:-4] + '.json', 'w'))
    y = pcm(tmp); d1 = len(y) / SR
    g = srms(x[int(t1 * SR):]) / srms(y)                           # match the old last sentence's speech level
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-t', f'{cut:.3f}', '-i', src + '.mp3', '-i', tmp, '-filter_complex',
                    f'[0:a]aresample={SR},afade=t=out:st={max(0, cut - 0.012):.3f}:d=0.012[a];'
                    f'[1:a]aresample={SR},volume={g:.3f},afade=t=in:st=0:d=0.012[b];[a][b]concat=n=2:v=0:a=1',
                    '-ac', '1', '-b:a', '192k', f'voice_orig/{k}.mp3'], check=True)
    al2 = {'characters': old['characters'][:i + 1] + [' '] + list(al['characters']),
           'character_start_times_seconds': old['character_start_times_seconds'][:i + 1] + [cut] + [t + cut for t in al['character_start_times_seconds']],
           'character_end_times_seconds': old['character_end_times_seconds'][:i + 1] + [cut] + [t + cut for t in al['character_end_times_seconds']]}
    json.dump(al2, open(f'voice_orig/{k}.json', 'w'))
    print(k, f'new last sentence {d1:.2f} s, gain {g:.2f}, take now {cut + d1:.2f} s', flush=True)
