import json, base64, urllib.request, os, sys, concurrent.futures as cf
K=os.environ['ELEVENLABS_JC_API_KEY']; V='bIHbv24MWmeRgasZH58o'
sc=json.load(open('audio/scenes.json'))
def go(s):
    if os.path.exists(f"audio/v_{s['id']}.mp3") and '--force' not in sys.argv: return s['id'],'cached'
    for k in range(4):
        try:
            r=urllib.request.Request(f'https://api.elevenlabs.io/v1/text-to-speech/{V}/with-timestamps',data=json.dumps({'text':s['text'],'model_id':'eleven_v4'}).encode(),headers={'xi-api-key':K,'Content-Type':'application/json'})
            d=json.load(urllib.request.urlopen(r,timeout=180))
            open(f"audio/v_{s['id']}.mp3",'wb').write(base64.b64decode(d['audio_base64'])); json.dump(d['alignment'],open(f"audio/a_{s['id']}.json",'w')); return s['id'],'ok'
        except Exception as e: err=str(e)
    return s['id'],'FAIL '+err
with cf.ThreadPoolExecutor(4) as ex:
    for r in ex.map(go,sc): print(*r)
