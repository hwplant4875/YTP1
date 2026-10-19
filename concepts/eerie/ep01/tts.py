# Generate narration per segment with ElevenLabs (with character timestamps).
# python3 tts.py outdir [voice_id]
import json, os, sys, base64, urllib.request
out = sys.argv[1]; voice = sys.argv[2] if len(sys.argv) > 2 else 'nPczCjzI2devNBz1zQrb'
os.makedirs(out, exist_ok=True)
segs = json.load(open(os.path.join(os.path.dirname(__file__), 'segments.json')))
key = os.environ['ELEVENLABS_JC_API_KEY']
for i, s in enumerate(segs):
    mp3 = os.path.join(out, s['id'] + '.mp3')
    if os.path.exists(mp3): continue
    body = {'text': s['text'], 'model_id': 'eleven_multilingual_v2',
            'voice_settings': {'stability': 0.65, 'similarity_boost': 0.8, 'style': 0.0, 'use_speaker_boost': True, 'speed': 0.92},
            'previous_text': segs[i-1]['text'] if i else None,
            'next_text': segs[i+1]['text'] if i + 1 < len(segs) else None}
    req = urllib.request.Request(f'https://api.elevenlabs.io/v1/text-to-speech/{voice}/with-timestamps?output_format=mp3_44100_128',
                                 data=json.dumps(body).encode(), headers={'xi-api-key': key, 'Content-Type': 'application/json'})
    r = json.load(urllib.request.urlopen(req))
    open(mp3, 'wb').write(base64.b64decode(r['audio_base64']))
    json.dump(r['alignment'], open(os.path.join(out, s['id'] + '.json'), 'w'))
    print(s['id'], 'ok')
