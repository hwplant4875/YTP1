import os,json,urllib.request,sys
k=os.environ["ELEVENLABS_JC_API_KEY"]
mode=sys.argv[2]
G=["hard techno","German rave","Berlin warehouse club","145 bpm","pounding four-on-the-floor kick","acid bassline","deep husky raspy gravelly male lead vocal with a Bavarian accent shouting German","a club crowd gang vocal shouts the English answer in brackets","vocals all the way through","fast call and response"]
P=[("Ich bin!","I am!"),("Du bist!","You are!"),("Er ist!","He is!"),("Sie ist!","She is!"),("Es ist!","It is!"),("Wir sind!","We are!"),("Ihr seid!","You all are!"),("Sie sind!","They are!")]
if mode=="A":
    secs=[]
    for i in range(4):
        a,b=P[2*i],P[2*i+1]
        st=(["vocals start on the very first beat"] if i==0 else [])+["lead shouts the German, crowd answers the English in brackets"]
        secs.append({"section_name":f"Part {i+1}","positive_local_styles":st,"negative_local_styles":["instrumental break"],"duration_ms":8000,
                     "lines":[f"{a[0]} ({a[1]})",f"{a[0]} ({a[1]})",f"{b[0]} ({b[1]})",f"{b[0]} ({b[1]})"]})
else:
    secs=[]
    for i in range(4):
        a,b=P[2*i],P[2*i+1]
        st=(["vocals start on the very first beat"] if i==0 else [])+["German shout, English crowd answer"]
        secs.append({"section_name":f"Part {i+1}","positive_local_styles":st,"negative_local_styles":["instrumental break"],"duration_ms":7000,
                     "lines":[f"{a[0]} {a[1]}",f"{b[0]} {b[1]}"]})
body={"composition_plan":{"positive_global_styles":G,"negative_global_styles":["pop ballad","soft","instrumental intro","mumbling","translating English into German"],"sections":secs},"model_id":"music_v1"}
req=urllib.request.Request("https://api.elevenlabs.io/v1/music?output_format=mp3_44100_128",data=json.dumps(body).encode(),headers={"xi-api-key":k,"Content-Type":"application/json"})
open(sys.argv[1],"wb").write(urllib.request.urlopen(req,timeout=300).read())
