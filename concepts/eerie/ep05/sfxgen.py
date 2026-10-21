# EP04 sound effects (ElevenLabs sound generation). python3 sfxgen.py outdir
import json, os, sys, urllib.request
out = sys.argv[1]; key = os.environ['ELEVENLABS_JC_API_KEY']
REQ = {
 'grab': ('a sudden cold hand gripping an ankle, a short damp slap and fabric rustle, quiet', 0.6),
 'drag': ('a body being dragged quickly across a wooden floor on its back, cloth sliding, soft scrape, ending in silence, quiet', 2.0),
 'binlid': ('a plastic street rubbish bin lid closing, soft thump, outdoors at night, quiet', 0.8),
 'keylock': ('a key turning in a front door lock, a clean click, close, quiet', 0.8),
 'sofa': ('a heavy fabric sofa shifting a few centimetres on a wooden floor, a short low creak and scrape, quiet', 1.0),
 'joint': ('a single dry bony joint cracking, soft knuckle click, eerie, close, quiet', 0.5),
 'scrape': ('long fingers slowly feeling across a wooden floor, soft dry scratching and tapping, eerie, quiet', 3.0),
 'unplug': ('a power plug pulled out of a wall socket, small plastic click, quiet', 0.5),
 'cloth': ('a rolled-up rug and a cotton hoodie being stood up on a wooden floor, soft fabric rustle and thump, quiet', 1.2),
 'chop': ('a kitchen knife chopping down hard through something thin and bony onto a wooden floor, one dull crack and thud, not loud', 0.7),
 'knife': ('a kitchen knife slowly drawn from a wooden knife block, soft metallic slide, quiet', 1.0),
 'servo': ('a small security camera motor turning, soft electric whirr, quiet', 1.2),
}
for k, (p, d) in REQ.items():
    f = os.path.join(out, k + '.mp3')
    if os.path.exists(f): continue
    body = {'text': p, 'duration_seconds': d, 'prompt_influence': 0.6}
    req = urllib.request.Request('https://api.elevenlabs.io/v1/sound-generation', data=json.dumps(body).encode(), headers={'xi-api-key': key, 'Content-Type': 'application/json'})
    open(f, 'wb').write(urllib.request.urlopen(req).read()); print(k, 'ok')
