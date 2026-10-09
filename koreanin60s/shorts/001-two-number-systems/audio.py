import json, numpy as np, wave, subprocess
SR=48000; T=json.load(open("timeline.json")); S=lambda k:T[k][0]; E=lambda k:T[k][1]
N=int((T["END"]+0.3)*SR); rng=np.random.default_rng(1)
def env(n,a=.003,d=.2):
    t=np.arange(n)/SR; e=np.exp(-t/d); k=int(a*SR); e[:k]*=np.linspace(0,1,k); return e
def pop():
    n=int(.12*SR); t=np.arange(n)/SR; f=np.linspace(900,300,n); x=np.sin(2*np.pi*np.cumsum(f)/SR)*env(n,.001,.035); return x*.55
def whoosh():
    n=int(.45*SR); x=rng.standard_normal(n); 
    # moving bandpass via simple one-pole lowpass with sweeping coeff
    y=np.zeros(n); a=np.linspace(.02,.35,n); a=np.concatenate([a[:n//2],a[n//2:][::-1]]) if False else a
    s=0
    for i in range(n): s+=a[i]*(x[i]-s); y[i]=s
    y=y-np.convolve(y,np.ones(40)/40,'same'); w=np.sin(np.linspace(0,np.pi,n))**2; return y*w*1.4
def ding():
    n=int(1.0*SR); t=np.arange(n)/SR; x=sum(np.sin(2*np.pi*f*t)*g for f,g in [(1568,1),(2349,.45),(3136,.25)])*env(n,.002,.28); return x*.28
def thud():
    n=int(.35*SR); t=np.arange(n)/SR; f=np.linspace(140,45,n); x=np.sin(2*np.pi*np.cumsum(f)/SR)*env(n,.001,.12); x+=rng.standard_normal(n)*env(n,.001,.02)*.3; return x*.9
def tick():
    n=int(.03*SR); x=rng.standard_normal(n)*env(n,.0005,.004); return x*.35
def boing():
    n=int(.4*SR); t=np.arange(n)/SR; f=320+180*np.sin(2*np.pi*9*t)*np.exp(-t*6); x=np.sin(2*np.pi*np.cumsum(f)/SR)*env(n,.002,.15); return x*.35
def sparkle():
    out=np.zeros(int(.8*SR))
    for i,f in enumerate([2093,2637,3136,4186]):
        n=int(.5*SR); t=np.arange(n)/SR; x=np.sin(2*np.pi*f*t)*env(n,.001,.12)*.18; o=int(i*.07*SR); out[o:o+n]+=x
    return out
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
while t<S('c0')+1.8: put(tick(),t); t+=.09
# music: 100bpm C G Am F
bpm=100; beat=60/bpm; mus=np.zeros(N)
chords=[[261.6,329.6,392.0],[196.0,246.9,293.7],[220.0,261.6,329.6],[174.6,220.0,261.6]]
def pluck(f,dur=.5,g=.12):
    n=int(dur*SR); t=np.arange(n)/SR; x=(np.sin(2*np.pi*f*t)+.3*np.sin(2*np.pi*2*f*t)+.1*np.sin(2*np.pi*3*f*t))*env(n,.004,.18); return x*g
def kick():
    n=int(.25*SR); t=np.arange(n)/SR; f=np.linspace(110,40,n); return np.sin(2*np.pi*np.cumsum(f)/SR)*env(n,.001,.09)*.5
def hat():
    n=int(.05*SR); x=rng.standard_normal(n); x=np.diff(np.concatenate([[0],x]))*env(n,.0005,.012); return x*.12
b=0; t=0.0
while t<T["END"]:
    c=chords[(b//4)%4]
    arp=[c[0],c[1],c[2],c[1]*2]
    for k in range(2):
        tt=t+k*beat/2; i=int(tt*SR); x=pluck(arp[(b*2+k)%4]*(2 if k else 1)); j=min(N,i+len(x)); mus[i:j]+=x[:j-i]
    if b%4==0:
        for f in c:
            n=int(4*beat*SR); tt=np.arange(n)/SR; pad=np.sin(2*np.pi*f/2*tt)*.035*np.minimum(1,tt/.4)*np.exp(-tt/3); i=int(t*SR); j=min(N,i+n); mus[i:j]+=pad[:j-i]
    if b%2==0: x=kick(); i=int(t*SR); j=min(N,i+len(x)); mus[i:j]+=x[:j-i]
    x=hat(); i=int((t+beat/2)*SR); j=min(N,i+len(x)); mus[i:j]+=x[:j-i]
    b+=1; t+=beat
fade=np.ones(N); k=int(1.2*SR); fade[-k:]=np.linspace(1,0,k); mus*=fade
def w(name,x):
    x=np.clip(x,-1,1); s=(np.stack([x,x],1)*32767).astype(np.int16)
    with wave.open(name,"wb") as f: f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR); f.writeframes(s.tobytes())
w("sfx.wav",sfx*.7); w("music.wav",mus*.8)
# VO track
keys=[k for k in T if k!="END"]
inp=[]; flt=[]
for i,k in enumerate(keys):
    inp+=["-i",f"vo/{k}.wav"]; d=int(S(k)*1000); flt.append(f"[{i}]adelay={d}|{d}[v{i}]")
flt.append("".join(f"[v{i}]" for i in range(len(keys)))+f"amix=inputs={len(keys)}:normalize=0,apad=whole_dur={T['END']+.3}[vo]")
subprocess.run(["ffmpeg","-v","error","-y",*inp,"-filter_complex",";".join(flt),"-map","[vo]","-ar","48000","-ac","2","vo.wav"],check=True)
subprocess.run(["ffmpeg","-v","error","-y","-i","vo.wav","-i","music.wav","-i","sfx.wav","-filter_complex",
 "[0]asplit[vo][sc];[1]volume=0.55[m];[m][sc]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=300[md];[vo]volume=1.0[v];[v][md][2]amix=inputs=3:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=9[out]",
 "-map","[out]","-ar","48000","-ac","2","mix.wav"],check=True)
print("ok")
