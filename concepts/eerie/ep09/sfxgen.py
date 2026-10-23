# EP09 (dog teeth) sound effects (ElevenLabs sound generation). python3 sfxgen.py outdir
import json, os, sys, urllib.request
out = sys.argv[1]; key = os.environ['ELEVENLABS_JC_API_KEY']
REQ = {
 'growl': ('a large dog growling low and steady, close, deep, menacing but soft, no bark', 2.0),
 'growlman': ('a man imitating a dog growl, low throaty growl, close, quiet room', 1.6),
 'bark': ('one single deep dog bark indoors, soft, slightly distant', 0.8),
 'pant': ('a happy dog panting softly and its tail thumping on a wooden floor, close, quiet', 2.0),
 'clicks': ('small hard teeth falling one by one onto a wooden floor, tiny clicks, quiet', 2.0),
 'fork': ('a fork gently clinking on a ceramic dinner plate, quiet dining room', 1.0),
 'pat': ('two soft pats on a head with a hand, muffled, close, quiet', 0.6),
 'paws': ('dog claws clicking on a wooden floor, trotting toward the camera, quiet', 1.6),
 'pounce': ('a large dog leaping and pinning a person to a carpeted floor, heavy soft thump and fabric, quiet', 1.0),
 'sniff': ('a dog sniffing closely, short quick sniffs, quiet', 1.2),
 'scratchear': ('a dog scratching behind its ear with its back paw, collar tags jingling softly, quiet', 1.4),
 'phonering': ('an old landline phone ringing twice in a quiet room, soft, slightly distant', 2.0),
 'tags': ('dog collar tags jingling softly once, close, quiet', 0.6),
 'whine': ('a dog whining softly once, close, quiet', 1.0),
}
for k, (p, d) in REQ.items():
    f = os.path.join(out, k + '.mp3')
    if os.path.exists(f): continue
    body = {'text': p, 'duration_seconds': d, 'prompt_influence': 0.6}
    req = urllib.request.Request('https://api.elevenlabs.io/v1/sound-generation', data=json.dumps(body).encode(), headers={'xi-api-key': key, 'Content-Type': 'application/json'})
    open(f, 'wb').write(urllib.request.urlopen(req).read()); print(k, 'ok')
