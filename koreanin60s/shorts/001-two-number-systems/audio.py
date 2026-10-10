import json, numpy as np, wave, subprocess, sys
sys.path.insert(0, "/home/user/YTP1/koreanin60s/engine")
from sound import load, music
SR=48000; T=json.load(open("timeline.json")); S=lambda k:T[k][0]; E=lambda k:T[k][1]
N=int((T["END"]+0.3)*SR)
pop=lambda: load("pop"); whoosh=lambda: load("whoosh"); ding=lambda: load("ding"); thud=lambda: load("stamp"); tick=lambda: load("tick", .35)
boing=pop; sparkle=ding
sfx=np.zeros(N)
def put(x,t,g=1.0):
    i=int(t*SR); j=min(N,i+len(x)); 
    if i<N: sfx[i:j]+=x[:j-i]*g
put(boing(),0.05)
scn=[S('n0')-.2,S('s0')-.2,S('c0')-.2,S('a0')-.25,S('r0')-.25,S('e0')-.25]
for t in scn: put(whoosh(),t-.05,.8)
sp=S('h1')+1.15
pops=[.05,sp,sp+.08,sp+.25,S('n0')+.05,S('n1a')-.04,S('n1b')-.04,S('n1c')-.04,S('s0')+.05,S('s1a')-.04,S('s1b')-.04,S('s1c')-.04,S('c0')+1.7,S('c2')-.05,S('c4')-.05,
 S('a0')+.1,S('a1')-.12,S('r0')+.05,S('r1')-.15,S('e0')+.25,S('e0')+.65]
r0,d0=S('r0'),E('r0')-S('r0'); pops+= [r0+d0*(.35+i*.16) for i in range(3)]
r1,d1=S('r1'),E('r1')-S('r1'); pops+= [r1+d1*(.02+i*.17) for i in range(4)]
for t in pops: put(pop(),t,.8)
for t in [S('h2')+.75,S('c6')+.05]: put(thud(),t)
for t in [S('c5')+.05,S('a3')-.12]: put(ding(),t)
put(sparkle(),S('e0')-.1)
t=S('c0')+.2
put(tick(),t)
mus=music(N)
def w(name,x):
    x=np.clip(x,-1,1); s=(np.stack([x,x],1)*32767).astype(np.int16)
    with wave.open(name,"wb") as f: f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR); f.writeframes(s.tobytes())
w("sfx.wav",sfx*.55); w("music.wav",mus)
# VO track
keys=[k for k in T if k!="END"]
inp=[]; flt=[]
for i,k in enumerate(keys):
    inp+=["-i",f"vo/{k}.wav"]; d=int(S(k)*1000); flt.append(f"[{i}]adelay={d}|{d}[v{i}]")
flt.append("".join(f"[v{i}]" for i in range(len(keys)))+f"amix=inputs={len(keys)}:normalize=0,apad=whole_dur={T['END']+.3}[vo]")
subprocess.run(["ffmpeg","-v","error","-y",*inp,"-filter_complex",";".join(flt),"-map","[vo]","-ar","48000","-ac","2","vo.wav"],check=True)
subprocess.run(["ffmpeg","-v","error","-y","-i","vo.wav","-i","music.wav","-i","sfx.wav","-filter_complex",
 "[0]asplit[vo][sc];[1]volume=0.3[m];[m][sc]sidechaincompress=threshold=0.02:ratio=8:attack=20:release=300[md];[vo]volume=1.0[v];[v][md][2]amix=inputs=3:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=9[out]",
 "-map","[out]","-ar","48000","-ac","2","mix.wav"],check=True)
print("ok")
