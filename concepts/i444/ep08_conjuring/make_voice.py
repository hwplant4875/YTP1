# EP08 Conjuring voice, copied from EP04 make_voice_v3.py (one full take per section, Adam, eleven_v4, with-timestamps). Run only after the owner OKs the script.
# Adam / eleven_v4 / with-timestamps, previous_text and next_text from the neighbouring sections in playback order. No splicing.
# EP07 v7 voice (owner 11/05 00:59 KST: new script, keep only the intro; v6b had an audible "sur survival rate" splice).
# Every section of script_v7.md is voiced as ONE full take: Adam / eleven_v4 / with-timestamps, previous_text and next_text
# taken from the neighbouring sections in playback order. No splicing anywhere. The v6 raw takes are kept in voice_orig/prev/.
# Then: w3.py <all sections> (whisper) -> python3 tighten2.py -> verify_voice.py + glitch check.
# usage: python3 make_voice_v7.py KEY_ENV_NAME [--dry] [--only s04,s05]
import json, os, re, sys, base64, shutil, urllib.request
DRY = '--dry' in sys.argv
KEYNAME = sys.argv[1]
ONLY = sys.argv[sys.argv.index('--only') + 1].split(',') if '--only' in sys.argv else None
K = os.environ.get(KEYNAME, '')
VOICE = 's3TPKV1kjDlVtZbl4Ksh'   # Adam
src = open(os.environ.get('SCRIPT', 'script_v1.md'), encoding='utf-8').read().split('## Shot slots')[0]
TXT = {m.group(1): m.group(2).strip() for m in re.finditer(r'^## (s\d\d)[^\n]*\n(.+?)(?=\n## |\Z)', src, re.S | re.M)}
ORDER = ['s00', 's01', 's02', 's03', 's04', 's05', 's06', 's07', 's08', 's09', 's10', 's11']
assert sorted(TXT) == sorted(ORDER), sorted(TXT)
todo = ONLY or ORDER
chars = sum(len(TXT[k]) for k in todo)
print('sections', len(todo), 'characters', chars)
if DRY:
    for k in todo: print(k, len(TXT[k]), TXT[k][:80], '...')
    sys.exit()
os.makedirs('voice_orig/prev', exist_ok=True)
for k in todo:
    for ext in ('mp3', 'json'):
        a, b = f'voice_orig/{k}.{ext}', f'voice_orig/prev/{k}.{ext}'
        if os.path.exists(a) and not os.path.exists(b): shutil.copy(a, b)
    i = ORDER.index(k)
    body = {'text': TXT[k], 'model_id': 'eleven_v4'}
    if i > 0: body['previous_text'] = TXT[ORDER[i - 1]][-400:]
    if i + 1 < len(ORDER): body['next_text'] = TXT[ORDER[i + 1]][:300]
    r = urllib.request.Request(f'https://api.elevenlabs.io/v1/text-to-speech/{VOICE}/with-timestamps', data=json.dumps(body).encode(),
                               headers={'xi-api-key': K, 'Content-Type': 'application/json'})
    d = json.load(urllib.request.urlopen(r, timeout=300))
    open(f'voice_orig/{k}.mp3', 'wb').write(base64.b64decode(d['audio_base64']))
    json.dump(d['alignment'], open(f'voice_orig/{k}.json', 'w'))
    print(k, round(d['alignment']['character_end_times_seconds'][-1], 2), 's', flush=True)
