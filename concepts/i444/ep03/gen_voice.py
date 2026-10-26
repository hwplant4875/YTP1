# generate Adam narration per segment with timestamps (eleven_v4), previous_text for continuity
import json, os, base64, urllib.request
K = os.environ['ELEVENLABS_JC_API_KEY']; S = json.load(open('segments.json'))
prev = ''
for k, t in S.items():
    if os.path.exists(f'voice/{k}.mp3'): prev = t; continue
    body = json.dumps({'text': t, 'model_id': 'eleven_v4', 'previous_text': prev[-400:]}).encode()
    r = urllib.request.Request('https://api.elevenlabs.io/v1/text-to-speech/s3TPKV1kjDlVtZbl4Ksh/with-timestamps', data=body,
                               headers={'xi-api-key': K, 'Content-Type': 'application/json'})
    d = json.load(urllib.request.urlopen(r, timeout=300))
    open(f'voice/{k}.mp3', 'wb').write(base64.b64decode(d['audio_base64'])); json.dump(d['alignment'], open(f'voice/{k}.json', 'w'))
    prev = t; print(k, round(d['alignment']['character_end_times_seconds'][-1], 1), flush=True)
