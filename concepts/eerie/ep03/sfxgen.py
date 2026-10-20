# EP03 sound effects (ElevenLabs sound generation). python3 sfxgen.py outdir
import json, os, sys, urllib.request
out = sys.argv[1]; key = os.environ['ELEVENLABS_JC_API_KEY']
REQ = {
 'tap': ('a bathroom sink tap running gently, water pouring into a ceramic basin, close, quiet, steady', 3.0),
 'tapoff': ('a bathroom tap being turned off, last drops into a sink, quiet', 1.0),
 'fog': ('a soft cold breathy hiss, like frost forming on glass, very quiet, airy', 2.0),
 'squeak': ('a fingertip slowly squeaking across a wet foggy bathroom mirror, drawing a line, close, quiet', 1.6),
 'glasstap': ('a single soft tap of a fingernail on a bathroom mirror, close, quiet', 0.5),
 'ripple': ('a cold liquid glassy ripple, like a hand pushing through the surface of water made of glass, eerie, soft', 1.6),
 'grab': ('a sudden cold grip on skin, a short damp slap and fabric rustle, quiet', 0.6),
 'crack': ('a bathroom mirror cracking, soft muffled glass crack and small tinkle, not loud', 1.2),
 'towel': ('a towel thrown over a mirror, soft cloth whoosh and flop, quiet', 0.8),
 'thumps': ('slow muffled thumps and scratches from behind a wall, distant, struggling, quiet', 4.0),
 'hum': ('a low quiet fluorescent bathroom light hum, steady, soft', 4.0),
 'drip': ('a single water drop falling into a sink, quiet, close', 0.6),
}
for k, (p, d) in REQ.items():
    f = os.path.join(out, k + '.mp3')
    if os.path.exists(f): continue
    body = {'text': p, 'duration_seconds': d, 'prompt_influence': 0.6}
    req = urllib.request.Request('https://api.elevenlabs.io/v1/sound-generation', data=json.dumps(body).encode(), headers={'xi-api-key': key, 'Content-Type': 'application/json'})
    open(f, 'wb').write(urllib.request.urlopen(req).read()); print(k, 'ok')
