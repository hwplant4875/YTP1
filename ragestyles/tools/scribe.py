"""Transcribe a media file with ElevenLabs Scribe (word timestamps). usage: python3 scribe.py file.mp4 [out.json]"""
import json, os, sys, subprocess, uuid, urllib.request
src = sys.argv[1]; out = sys.argv[2] if len(sys.argv) > 2 else src + '.scribe.json'
wav = f'/tmp/scribe_{uuid.uuid4().hex}.mp3'
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-vn', '-ac', '1', '-b:a', '96k', wav], check=True)
b = uuid.uuid4().hex
body = (f'--{b}\r\nContent-Disposition: form-data; name="model_id"\r\n\r\nscribe_v1\r\n'
        f'--{b}\r\nContent-Disposition: form-data; name="tag_audio_events"\r\n\r\ntrue\r\n'
        f'--{b}\r\nContent-Disposition: form-data; name="file"; filename="a.mp3"\r\nContent-Type: audio/mpeg\r\n\r\n').encode() + open(wav, 'rb').read() + f'\r\n--{b}--\r\n'.encode()
req = urllib.request.Request('https://api.elevenlabs.io/v1/speech-to-text', data=body, method='POST',
    headers={'xi-api-key': os.environ['ELEVENLABS_API_KEY'], 'Content-Type': f'multipart/form-data; boundary={b}'})
d = json.loads(urllib.request.urlopen(req, timeout=600).read()); os.remove(wav)
json.dump(d, open(out, 'w'), indent=1)
for w in d.get('words', []):
    if w.get('type') in ('word', 'audio_event'): print(f"{w['start']:.2f}-{w['end']:.2f} {w['text']}")
