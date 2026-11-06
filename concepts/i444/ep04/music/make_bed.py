# EP04 Freddy ambience bed (11/7): ElevenLabs Music music_v2_5 with the JC key, two takes of one prompt, joined A -> B -> A later.
import json, os, sys, urllib.request
K = os.environ['ELEVENLABS_JC_API_KEY']
def sub():
    d = json.load(urllib.request.urlopen(urllib.request.Request('https://api.elevenlabs.io/v1/user/subscription', headers={'xi-api-key': K}), timeout=30))
    return d['character_count']
prompt = ("Instrumental dark nightmare lullaby ambience for a horror documentary narration. A very sparse, slow, slightly detuned music box "
          "playing a few soft scattered notes in a minor key at irregular, far-apart moments, never a full tune and never a steady pulse, over low sustained cello and double bass drones, a soft "
          "warm low industrial hum like a distant boiler room, faint slow steam hiss far in the background, and a quiet dark string pad with "
          "deep reverb. Eerie, dreamlike and unsettling, like a child's bedroom at night that slowly turns into a nightmare. Made to sit "
          "quietly under a narrator for several minutes: same mood and tempo throughout, no build-up, no climax, no ending, no silences. "
          "60 BPM, D minor, wide natural stereo. No drums, no percussion, no beat, no booms, no impacts or hits, no stingers, no risers, "
          "no choir, no vocals, no harsh drones, no shrill high strings, no ticking, no metallic clanks.")
before = sub(); print('credits used before', before, flush=True)
for tag in sys.argv[1:] or ['a', 'b']:
    body = {'prompt': prompt, 'music_length_ms': 180000, 'model_id': 'music_v2_5', 'force_instrumental': True}
    r = urllib.request.Request('https://api.elevenlabs.io/v1/music?output_format=mp3_44100_192', data=json.dumps(body).encode(),
                               headers={'xi-api-key': K, 'Content-Type': 'application/json'})
    try:
        open(f'freddy_bed_{tag}.mp3', 'wb').write(urllib.request.urlopen(r, timeout=900).read())
        json.dump({**body, 'key': 'JC (ELEVENLABS_JC_API_KEY)'}, open(f'freddy_bed_{tag}.json', 'w'), indent=1); print('ok', tag, flush=True)
    except urllib.error.HTTPError as e: print('HTTP', e.code, e.read()[:600])
print('credits used after', sub())
