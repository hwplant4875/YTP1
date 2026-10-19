import json, os, sys, urllib.request
out, tag = sys.argv[1], sys.argv[2]
G=["kids science show","curious and playful","light airy flutes and pizzicato strings","bright marimba","soft fluttery shaker","light electronic beat","bouncy bass","sense of wonder","instrumental","sits under narration, not busy","clean modern mix","120 bpm"]
N=["vocals","singing","lyrics","horror","scary","aggressive","heavy distortion","dubstep","loud lead melody","harsh drone","hard panned"]
S={'A':[("Flutter intro",["plucky marimba motif","flute flutters","soft kick","curious"],["slow fade in"],25000),("Explore",["bouncy groove","pizzicato","claps","playful"],["loud"],70000),("Discovery",["glockenspiel sparkles","warm bass","forward motion"],["sad"],60000),("Zoom",["slightly bigger drums","fast and fun"],["epic orchestra"],50000)],
   'B':[("Gentle night",["soft music box","warm pads","calm but curious"],["sad","slow fade in"],40000),("Travel",["bouncy groove returns","flute melody","adventurous"],["loud"],70000),("Nest",["warm pizzicato","glockenspiel","cozy"],["sad"],45000),("Finale",["bright full groove","happy ending"],["epic orchestra"],40000)]}[tag]
plan={"positive_global_styles":G,"negative_global_styles":N,"sections":[{"section_name":a,"positive_local_styles":b,"negative_local_styles":c,"duration_ms":d,"lines":[]} for a,b,c,d in S]}
body={"composition_plan":plan,"model_id":"music_v1"}
json.dump(body,open(out.replace('.mp3','.json'),'w'))
req=urllib.request.Request("https://api.elevenlabs.io/v1/music?output_format=mp3_44100_192",json.dumps(body).encode(),{"xi-api-key":os.environ["ELEVENLABS_JC_API_KEY"],"Content-Type":"application/json"})
try: open(out,"wb").write(urllib.request.urlopen(req,timeout=900).read()); print("ok",out)
except urllib.error.HTTPError as e: print("ERR",e.code,e.read()[:400])
