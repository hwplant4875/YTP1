# EP02 sound effects (ElevenLabs sound generation). python3 sfxgen.py outdir
import json, os, sys, urllib.request
out = sys.argv[1]; key = os.environ['ELEVENLABS_JC_API_KEY']
REQ = {
 'buzz': ('a smartphone vibrating twice on a wooden nightstand in a quiet bedroom at night, soft muffled buzz, close', 1.6),
 'notif': ('a single soft gentle smartphone message notification ding, warm, quiet, short', 0.8),
 'shutter': ('a single quiet smartphone camera shutter click, close, dry', 0.6),
 'typing': ('soft quick taps on a smartphone touchscreen keyboard, about eight taps, quiet, close', 1.2),
 'send': ('a soft short upward swoosh of a sent chat message, gentle, quiet', 0.6),
 'flash': ('a camera flash charging whine and a sharp soft pop of a flash bulb, short', 0.8),
 'poweroff': ('a smartphone powering down, soft low descending electronic tone, short', 1.0),
 'poweron': ('a smartphone booting up by itself, soft gentle rising startup chime, quiet', 1.4),
}
for k, (p, d) in REQ.items():
    f = os.path.join(out, k + '.mp3')
    if os.path.exists(f): continue
    body = {'text': p, 'duration_seconds': d, 'prompt_influence': 0.6}
    req = urllib.request.Request('https://api.elevenlabs.io/v1/sound-generation', data=json.dumps(body).encode(), headers={'xi-api-key': key, 'Content-Type': 'application/json'})
    open(f, 'wb').write(urllib.request.urlopen(req).read()); print(k, 'ok')
