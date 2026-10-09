"""ElevenLabs TTS with word timings. usage: python3 tts.py lines.json outdir
lines.json: {"voice": "...", "model": "eleven_multilingual_v2", "settings": {...}, "lines": {"l1": "text", ...}}
Writes outdir/<id>.mp3 and outdir/<id>.json ({"words": [{"w","s","e"}], "dur"}). Cached: skips existing ids with same text."""
import base64, json, os, sys, urllib.request
spec = json.load(open(sys.argv[1])); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
key = os.environ['ELEVENLABS_API_KEY']
for lid, text in spec['lines'].items():
    jp = f'{out}/{lid}.json'
    if os.path.exists(jp) and json.load(open(jp)).get('text') == text and spec['voice'] == json.load(open(jp)).get('voice'): continue
    body = {'text': text, 'model_id': spec.get('model', 'eleven_multilingual_v2'),
            'voice_settings': spec.get('settings', {'stability': .4, 'similarity_boost': .8, 'style': .45, 'use_speaker_boost': True})}
    req = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{spec['voice']}/with-timestamps?output_format=mp3_44100_192",
        data=json.dumps(body).encode(), headers={'xi-api-key': key, 'Content-Type': 'application/json'}, method='POST')
    d = json.loads(urllib.request.urlopen(req, timeout=180).read())
    open(f'{out}/{lid}.mp3', 'wb').write(base64.b64decode(d['audio_base64']))
    al = d['alignment']; words, cur = [], None
    for ch, s, e in zip(al['characters'], al['character_start_times_seconds'], al['character_end_times_seconds']):
        if ch.isspace():
            if cur: words.append(cur); cur = None
            continue
        if cur is None: cur = {'w': ch, 's': s, 'e': e}
        else: cur['w'] += ch; cur['e'] = e
    if cur: words.append(cur)
    json.dump({'text': text, 'voice': spec['voice'], 'words': words, 'dur': al['character_end_times_seconds'][-1]}, open(jp, 'w'), indent=1)
    print(lid, round(al['character_end_times_seconds'][-1], 2), 's')
