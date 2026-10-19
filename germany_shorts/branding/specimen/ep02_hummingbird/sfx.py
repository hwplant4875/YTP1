import json, os, urllib.request, concurrent.futures as cf
K=os.environ['ELEVENLABS_JC_API_KEY']
J={'hum':('close-up hummingbird wings humming buzz, soft, steady, no birdsong',3.0),
   'chirp':('single loud sharp metallic chirp squeak of an Anna\'s hummingbird dive, short',1.0),
   'heart':('very fast tiny heartbeat thumping, soft, clean',3.0),
   'lick':('tiny quick wet licking slurps, cartoon, soft',1.5),
   'zzz':('gentle cartoon snore, soft and cute',2.0)}
def go(k):
    txt,d=J[k]
    r=urllib.request.Request('https://api.elevenlabs.io/v1/sound-generation',data=json.dumps({'text':txt,'duration_seconds':d,'prompt_influence':0.6}).encode(),headers={'xi-api-key':K,'Content-Type':'application/json'})
    try: open(f'mus/sfx_{k}.mp3','wb').write(urllib.request.urlopen(r,timeout=120).read()); return k,'ok'
    except Exception as e: return k,str(e)
with cf.ThreadPoolExecutor(5) as ex:
    for r in ex.map(go,J): print(*r)
