# EP07 (Weakness v4) sound effects (ElevenLabs sound generation). python3 sfxgen.py outdir
import json, os, sys, urllib.request
out = sys.argv[1]; key = os.environ['ELEVENLABS_JC_API_KEY']
REQ = {
 'squeeze': ('a firm handshake, leather glove creaking as a hand squeezes tighter, soft, close, quiet', 1.4),
 'crack': ('a muffled knuckle crack heard through a closed office door, short, soft, distant, quiet', 0.6),
 'doorbell': ('a soft two-tone apartment doorbell ding dong in a quiet hallway, gentle', 1.6),
 'boxes': ('three small cardboard boxes being picked up, soft cardboard rustle, quiet', 1.2),
 'drop': ('three clipboards dropping onto a carpeted floor, soft muffled thuds, quiet', 0.9),
 'mailpile': ('envelopes sliding through a mail slot and landing on a floor one after another, soft, quiet', 2.0),
}
for k, (p, d) in REQ.items():
    f = os.path.join(out, k + '.mp3')
    if os.path.exists(f): continue
    body = {'text': p, 'duration_seconds': d, 'prompt_influence': 0.6}
    req = urllib.request.Request('https://api.elevenlabs.io/v1/sound-generation', data=json.dumps(body).encode(), headers={'xi-api-key': key, 'Content-Type': 'application/json'})
    open(f, 'wb').write(urllib.request.urlopen(req).read()); print(k, 'ok')
