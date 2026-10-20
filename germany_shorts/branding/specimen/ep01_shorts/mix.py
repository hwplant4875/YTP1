# audio for one short: hook VO + long-form VO slices, long-form SFX remapped, hook SFX, ducked music bed, loudnorm -14
import json, subprocess, sys, numpy as np
SR=48000; sid=sys.argv[1]; SP='/tmp/claude-0/sp2/'
def load(f):
    r=subprocess.run(['ffmpeg','-v','error','-i',f,'-f','f32le','-ac','2','-ar',str(SR),'-'],capture_output=True,check=True).stdout
    return np.frombuffer(r,dtype=np.float32).reshape(-1,2).copy()
P=json.load(open('/tmp/claude-0/shs/plans.json'))[sid]; M=json.load(open(SP+'mixplan.json')); N=int((P['total']+0.05)*SR)
vo=np.zeros((N,2),np.float32); sf=np.zeros((N,2),np.float32); speech=np.zeros(N,np.float32)
def put(buf,a,t,v):
    i=int(t*SR); a=a[:max(0,N-i)]; buf[i:i+len(a)]+=a*v
for p in P['parts']:
    f,T,off,d=p['vo']; a=load(f)[int(off*SR):int((off+d)*SR)]
    fl=int(0.04*SR); a[-fl:]*=np.linspace(1,0,fl)[:,None]; put(vo,a,T,1.0); speech[int(T*SR):int((T+d)*SR)]=1
    if p['kind']=='clip':
        g0=p['gstart']
        for f2,g,v in M['ev']:
            if g0+0.2<=g<g0+p['len']-0.2: put(sf,load(SP+f2),p['T0']+g-g0,v)
for p in P['parts'][1:]: put(sf,load(SP+'mus/sfx_whoosh.mp3'),p['T0']-0.25,0.2)
H=json.load(open(f'/tmp/claude-0/shs/audio/h_{sid}.json')); hs=''.join(H['characters'])
def hat(ph): return 0.05+H['character_start_times_seconds'][hs.index(ph)]
HK={'s01':[('sfx_whoosh',0.0,0.25),('sfx_ding','zero',0.3)],'s02':[('sfx_pop','loses',0.4)],'s03':[('sfx_whoosh',0.0,0.25),('sfx_pop',1.6,0.35)],
    's04':[('sfx_bubbles',0.0,0.25)],'s05':[('sfx_pop','bite',0.5)],'s06':[('sfx_splash',0.75,0.45)],'s07':[('sfx_pop','electricity',0.4)],'s08':[('sfx_whoosh','roll',0.25)],
    's09':[('sfx_bubbles',0.0,0.25)],'s10':[('sfx_pop','stops',0.4)],'s11':[('sfx_whoosh',0.0,0.2)],'s12':[('sfx_pop','trees',0.35)],'s13':[('sfx_whoosh',0.0,0.25)],'s14':[('sfx_ding','twenty',0.3)]}
for f2,w,v in HK.get(sid,[]): put(sf,load(SP+f'mus/{f2}.mp3'),w if isinstance(w,float) else hat(w)-0.05,v)
mus={'s01':('mA',60),'s02':('mB',20),'s03':('mA',100),'s04':('mB',70),'s05':('mA',140),'s06':('mB',120),'s07':('mA',30),'s08':('mB',160),'s09':('mA',180),'s10':('mB',45),'s11':('mA',15),'s12':('mB',95),'s13':('mA',120),'s14':('mB',185)}.get(sid,('mA',60))
mu=load(SP+f'mus/{mus[0]}.mp3')[int(mus[1]*SR):][:N]; fi=int(0.3*SR); mu[:fi]*=np.linspace(0.3,1,fi)[:,None]; mu=np.pad(mu,((0,N-len(mu)),(0,0)))
k=int(0.4*SR); c=np.concatenate([[0],np.cumsum(speech,dtype=np.float64)]); idx=np.arange(N); lo=np.clip(idx-k//2,0,N); hi=np.clip(idx+k//2,0,N)
env=0.42-0.27*np.clip(((c[hi]-c[lo])/k)*1.6,0,1)
mix=vo+sf*0.8+mu*env[:,None]; fo=int(0.6*SR); mix[-fo:]*=np.linspace(1,0,fo)[:,None]
raw=f'/tmp/claude-0/shs/out/{sid}.f32'; mix.astype(np.float32).tofile(raw)
subprocess.run(['ffmpeg','-y','-v','error','-f','f32le','-ar',str(SR),'-ac','2','-i',raw,'-af','loudnorm=I=-14:TP=-1.5:LRA=11','-ar',str(SR),f'/tmp/claude-0/shs/out/{sid}.wav'],check=True)
print(sid,'ok',round(N/SR,2))
