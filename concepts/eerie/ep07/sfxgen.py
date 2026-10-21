# EP06 (Myers) sound effects (ElevenLabs sound generation). python3 sfxgen.py outdir
import json, os, sys, urllib.request
out = sys.argv[1]; key = os.environ['ELEVENLABS_JC_API_KEY']
REQ = {
 'pen': ('a ballpoint pen writing quickly on paper on a clipboard, soft scratching, quiet, close', 1.6),
 'underline': ('a single slow pen stroke underlining a word on paper, one soft scratch, quiet', 0.8),
 'tick': ('a wall clock ticking slowly in a silent office room, soft, quiet', 4.0),
 'acoff': ('an office air conditioner humming and then switching off, the hum stops, quiet', 2.0),
 'paper': ('sheets of paper being folded and then sliding across a wooden floor, soft rustle, quiet', 2.0),
 'chair': ('an office chair creaking softly as someone shifts, quiet', 1.0),
 'pens': ('three pens being placed down on a wooden desk, soft clicks, quiet', 1.0),
 'standup': ('three office chairs rolling back as people stand up, soft, quiet', 1.2),
}
for k, (p, d) in REQ.items():
    f = os.path.join(out, k + '.mp3')
    if os.path.exists(f): continue
    body = {'text': p, 'duration_seconds': d, 'prompt_influence': 0.6}
    req = urllib.request.Request('https://api.elevenlabs.io/v1/sound-generation', data=json.dumps(body).encode(), headers={'xi-api-key': key, 'Content-Type': 'application/json'})
    open(f, 'wb').write(urllib.request.urlopen(req).read()); print(k, 'ok')
