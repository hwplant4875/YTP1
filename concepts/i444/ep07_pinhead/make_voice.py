# EP04 narration: one eleven_v4 take per section from script_v1.md (Adam), with-timestamps alignment.
# Writes voice/<seg>.mp3 + .json (same alignment format as EP03 voice_v3/). Skips sections already generated.
import json, os, re, base64, urllib.request
K = os.environ['ELEVENLABS_JC_API_KEY']; OUT = 'voice/'; os.makedirs(OUT, exist_ok=True)
src = open('script_v1.md').read().split('## Fact notes')[0]
SEC = [(m.group(1), m.group(2).strip()) for m in re.finditer(r'^## (s\d\d)[^\n]*\n(.+?)(?=\n## |\Z)', src, re.S | re.M)]
prev = ''
for i, (name, text) in enumerate(SEC):
    if not os.path.exists(OUT + name + '.mp3'):
        body = {'text': text, 'model_id': 'eleven_v4'}
        if prev: body['previous_text'] = prev[-400:]
        if i + 1 < len(SEC): body['next_text'] = SEC[i + 1][1][:300]
        r = urllib.request.Request('https://api.elevenlabs.io/v1/text-to-speech/s3TPKV1kjDlVtZbl4Ksh/with-timestamps',
                                   data=json.dumps(body).encode(), headers={'xi-api-key': K, 'Content-Type': 'application/json'})
        d = json.load(urllib.request.urlopen(r, timeout=300))
        open(OUT + name + '.mp3', 'wb').write(base64.b64decode(d['audio_base64'])); json.dump(d['alignment'], open(OUT + name + '.json', 'w'))
        print(name, round(d['alignment']['character_end_times_seconds'][-1], 2), flush=True)
    prev = text
