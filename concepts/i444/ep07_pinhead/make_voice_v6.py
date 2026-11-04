# EP07 v6 re-voice (owner 11/04 evening: full story re-check, factcheck_v6.md).
# Adam / eleven_v4 / with-timestamps, previous_text + next_text taken from the NEW playback order in script_v1.md.
# FULL sections get a new take. PART sections only re-voice their first sentence; the new sentence is joined to the untouched
# rest of the v5 take at the quietest 20 ms inside the pause after the old first sentence, and the alignment is rebuilt.
# The old raw takes are kept in voice_orig/v5/.
# Then: python3 words_v6.py (whisper) -> python3 tighten2.py -> check.
# usage: python3 make_voice_v6.py [--dry]
import json, os, re, sys, base64, shutil, subprocess, urllib.request
import numpy as np
DRY = '--dry' in sys.argv
K = os.environ.get('ELEVENLABS_JC_API_KEY', '')
VOICE = 's3TPKV1kjDlVtZbl4Ksh'   # Adam
src = open('script_v1.md', encoding='utf-8').read().split('## Fact notes')[0]
SEC = [(m.group(1), m.group(2).strip()) for m in re.finditer(r'^## (s\d\d)[^\n]*\n(.+?)(?=\n## |\Z)', src, re.S | re.M)]
TXT = dict(SEC); ORDER = [k for k, _ in SEC]
FULL = ['s04', 's05', 's07', 's08', 's09', 's02', 's03', 's12']
PART = ['s06', 's10', 's13']
os.makedirs('voice_orig/v5', exist_ok=True)
def first_sentence(t): return t[:t.index('.') + 1]
def ctx(k):
    i = ORDER.index(k)
    return (TXT[ORDER[i - 1]][-400:] if i > 0 else ''), (TXT[ORDER[i + 1]][:300] if i + 1 < len(ORDER) else '')
def tts(text, prev, nxt):
    body = {'text': text, 'model_id': 'eleven_v4'}
    if prev: body['previous_text'] = prev
    if nxt: body['next_text'] = nxt
    r = urllib.request.Request(f'https://api.elevenlabs.io/v1/text-to-speech/{VOICE}/with-timestamps', data=json.dumps(body).encode(),
                               headers={'xi-api-key': K, 'Content-Type': 'application/json'})
    d = json.load(urllib.request.urlopen(r, timeout=300))
    return base64.b64decode(d['audio_base64']), d['alignment']
def pcm(p, sr=44100):
    return np.frombuffer(subprocess.check_output(['ffmpeg', '-v', 'error', '-i', p, '-f', 's16le', '-ac', '1', '-ar', str(sr), '-']), np.int16).astype(np.float32) / 32768
def backup(k):
    for ext in ('mp3', 'json'):
        a, b = f'voice_orig/{k}.{ext}', f'voice_orig/v5/{k}.{ext}'
        if not os.path.exists(b): shutil.copy(a, b)
chars = 0
for k in FULL: chars += len(TXT[k])
for k in PART: chars += len(first_sentence(TXT[k]))
print('characters to voice:', chars, '(~%d credits at 0.44/char)' % (chars * 0.44))
if DRY:
    for k in FULL: print('FULL', k, TXT[k][:70], '...')
    for k in PART: print('PART', k, first_sentence(TXT[k]))
    sys.exit()
for k in FULL:
    backup(k); prev, nxt = ctx(k)
    audio, al = tts(TXT[k], prev, nxt)
    open(f'voice_orig/{k}.mp3', 'wb').write(audio); json.dump(al, open(f'voice_orig/{k}.json', 'w'))
    print(k, 'full', round(al['character_end_times_seconds'][-1], 2), flush=True)
for k in PART:
    backup(k); prev, _ = ctx(k)
    new1 = first_sentence(TXT[k]); rest_new = TXT[k][len(new1):].strip()
    audio, al = tts(new1, prev, rest_new[:300])
    tmp = f'voice_orig/v5/{k}_first.mp3'; open(tmp, 'wb').write(audio); json.dump(al, open(tmp[:-4] + '.json', 'w'))
    old = json.load(open(f'voice_orig/v5/{k}.json')); s = ''.join(old['characters'])
    i = s.index('.')                       # end of the old first sentence
    j = i + 1
    while s[j] == ' ': j += 1              # first char of the old remainder
    assert s[j:].strip() == rest_new, (k, s[j:j + 60], rest_new[:60])
    t0, t1 = old['character_end_times_seconds'][i], old['character_start_times_seconds'][j]
    x = pcm(f'voice_orig/v5/{k}.mp3'); sr = 44100; w = int(0.02 * sr)
    a, b = int(max(0, t0 - 0.03) * sr), int((t1 + 0.03) * sr)
    rms = [np.sqrt(np.mean(x[n:n + w] ** 2)) for n in range(a, max(a + 1, b - w), w // 2)]
    cut = (a + int(np.argmin(rms)) * (w // 2) + w // 2) / sr          # seconds into the old take
    y = pcm(tmp); d1 = len(y) / sr
    # level match on speech (RMS above -40 dBFS)
    def srms(v): f = v[np.abs(v) > 0.01]; return np.sqrt(np.mean(f ** 2)) if len(f) else 1
    g = srms(x) / srms(y)
    out = f'voice_orig/{k}.mp3'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-ss', f'{cut:.3f}', '-i', f'voice_orig/v5/{k}.mp3', '-filter_complex',
                    f'[0:a]aresample=44100,volume={g:.3f},afade=t=out:st={max(0, d1 - 0.012):.3f}:d=0.012[a];'
                    f'[1:a]aresample=44100,afade=t=in:st=0:d=0.012[b];[a][b]concat=n=2:v=0:a=1', '-ac', '1', '-b:a', '192k', out], check=True)
    sh = d1 - cut
    al2 = {'characters': list(al['characters']) + [' '] + old['characters'][j:],
           'character_start_times_seconds': list(al['character_start_times_seconds']) + [d1] + [t + sh for t in old['character_start_times_seconds'][j:]],
           'character_end_times_seconds': list(al['character_end_times_seconds']) + [d1] + [t + sh for t in old['character_end_times_seconds'][j:]]}
    json.dump(al2, open(f'voice_orig/{k}.json', 'w'))
    print(k, 'part', round(d1, 2), 's new first sentence, joined at', round(cut, 3), 's of the old take, gain', round(g, 2), flush=True)
