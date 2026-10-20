import json, base64, urllib.request, os
K=os.environ['ELEVENLABS_JC_API_KEY']; V='bIHbv24MWmeRgasZH58o'
for s in json.load(open('spec.json')):
    f=f"audio/h_{s['id']}.mp3"
    if os.path.exists(f): continue
    r=urllib.request.Request(f'https://api.elevenlabs.io/v1/text-to-speech/{V}/with-timestamps',data=json.dumps({'text':s['hook'],'model_id':'eleven_v4'}).encode(),headers={'xi-api-key':K,'Content-Type':'application/json'})
    d=json.load(urllib.request.urlopen(r,timeout=180)); open(f,'wb').write(base64.b64decode(d['audio_base64'])); json.dump(d['alignment'],open(f"audio/h_{s['id']}.json",'w'))
    print(s['id'], d['alignment']['character_end_times_seconds'][-1])
