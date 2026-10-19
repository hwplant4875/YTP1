import os,json,urllib.request,sys
k=os.environ["ELEVENLABS_JC_API_KEY"]
mode=sys.argv[2]
BAR=60/140*4*1000
G=["hard techno","German rave","Berlin warehouse club","exactly 140 bpm, strict tempo","pounding four-on-the-floor kick","acid bassline",
   "deep husky raspy gravelly male vocal with a Bavarian accent","rhythmic shouted chant locked to the beat",
   "every lyric line sung with the exact same rhythm and the same melody, one line per bar","German words then English words in the same line",
   "vocals all the way through"]
P=[("Ich bin!","I am!"),("Du bist!","You are!"),("Er ist!","He is!"),("Sie ist!","She is!"),("Es ist!","It is!"),("Wir sind!","We are!"),("Ihr seid!","You all are!"),("Sie sind!","They are!")]
NEG=["pop ballad","soft","instrumental intro","instrumental break","mumbling","rubato","free timing","syncopated vocals","translating English into German"]
secs=[]
if mode=="X":
    for i,(de,en) in enumerate(P):
        st=(["vocals start on the very first beat"] if i==0 else [])+["same chant rhythm as before"]
        secs.append({"section_name":f"Part {i+1}","positive_local_styles":st,"negative_local_styles":[],"duration_ms":int(2*BAR),"lines":[f"{de} {en}"]*2})
else:
    for i in range(4):
        a,b=P[2*i],P[2*i+1]
        st=(["vocals start on the very first beat"] if i==0 else [])+["same chant rhythm as before"]
        secs.append({"section_name":f"Part {i+1}","positive_local_styles":st,"negative_local_styles":[],"duration_ms":int(4*BAR),
                     "lines":[f"{a[0]} {a[1]}",f"{a[0]} {a[1]}",f"{b[0]} {b[1]}",f"{b[0]} {b[1]}"]})
body={"composition_plan":{"positive_global_styles":G,"negative_global_styles":NEG,"sections":secs},"model_id":"music_v1"}
req=urllib.request.Request("https://api.elevenlabs.io/v1/music?output_format=mp3_44100_128",data=json.dumps(body).encode(),headers={"xi-api-key":k,"Content-Type":"application/json"})
open(sys.argv[1],"wb").write(urllib.request.urlopen(req,timeout=300).read())
