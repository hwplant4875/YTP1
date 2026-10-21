# EP06 (Myers) sound effects (ElevenLabs sound generation). python3 sfxgen.py outdir
import json, os, sys, urllib.request
out = sys.argv[1]; key = os.environ['ELEVENLABS_JC_API_KEY']
REQ = {
 'street': ('quiet suburban street on Halloween night, distant children laughing, leaves rustling in a light wind, far away, soft', 6.0),
 'steps': ('slow heavy footsteps on a wooden hallway floor, four steps, unhurried, muffled, quiet', 3.0),
 'dooropen': ('an interior wooden door slowly opening with a soft creak, quiet', 1.6),
 'curtain': ('curtains quickly pulled shut on a metal rail, soft swish, quiet', 0.8),
 'slats': ('a slatted wooden closet door gently rattling, very soft, quiet', 1.0),
 'shots': ('six muffled gunshots in quick succession heard from inside a house, dull and soft, low-passed, not loud', 2.5),
 'fall': ('a heavy body falling from a balcony and landing on grass with a dull soft thud, quiet', 1.2),
 'car': ('a car engine starting and driving away on a quiet street at night, muffled from inside the car, soft', 3.0),
 'clap': ('a few neighbours clapping slowly on their porches outdoors at night, scattered, distant, soft', 2.5),
 'situp': ('cloth rustling and a wooden floor creaking as someone slowly sits up from lying down, quiet', 2.0),
 'knifeset': ('a kitchen knife gently slid back into a wooden knife block, soft click, quiet', 0.8),
}
for k, (p, d) in REQ.items():
    f = os.path.join(out, k + '.mp3')
    if os.path.exists(f): continue
    body = {'text': p, 'duration_seconds': d, 'prompt_influence': 0.6}
    req = urllib.request.Request('https://api.elevenlabs.io/v1/sound-generation', data=json.dumps(body).encode(), headers={'xi-api-key': key, 'Content-Type': 'application/json'})
    open(f, 'wb').write(urllib.request.urlopen(req).read()); print(k, 'ok')
