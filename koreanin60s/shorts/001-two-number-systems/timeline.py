import json, subprocess
seq=[("h1",.25),("h2",.08),("n0",.35),("n1a",.12),("n1b",.35),("n1c",.35),("s0",.55),("s1a",.12),("s1b",.22),("s1c",.22),
("c0",.45),("c1",.25),("c2",.08),("c3",.35),("c4",.08),("c5",.4),("c6",.45),("a0",.5),("a1",.1),("a2",.45),("a3",.15),("r0",.65),("r1",.3),("e0",.4)]
def dur(k): return float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f"vo/{k}.wav"]))
t=0; T={}
for k,g in seq:
    t+=g; d=dur(k); T[k]=[round(t,3),round(t+d,3)]; t+=d
T["END"]=round(t+1.6,3)
json.dump(T,open("timeline.json","w"),indent=1); print(T["END"])
