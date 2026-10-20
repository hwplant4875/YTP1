# audio for one short: hook VO + long-form VO slices, long-form SFX remapped, hook SFX, ducked music bed, loudnorm -14
import json, subprocess, sys, numpy as np
SR=48000; sid=sys.argv[1]; SP='/tmp/claude-0/hb2/'
def load(f):
    r=subprocess.run(['ffmpeg','-v','error','-i',f,'-f','f32le','-ac','2','-ar',str(SR),'-'],capture_output=True,check=True).stdout
    return np.frombuffer(r,dtype=np.float32).reshape(-1,2).copy()
P=json.load(open('/tmp/claude-0/hbs/plans.json'))[sid]; M=json.load(open(SP+'mixplan.json')); N=int((P['total']+0.05)*SR)
vo=np.zeros((N,2),np.float32); sf=np.zeros((N,2),np.float32); speech=np.zeros(N,np.float32)
def put(buf,a,t,v):
    i=int(t*SR); a=a[:max(0,N-i)]; buf[i:i+len(a)]+=a*v
for p in P['parts']:
    f,T,off,d=p['vo']; a=load(f)[int(off*SR):int((off+d)*SR)]
    fl=int(0.04*SR); a[-fl:]*=np.linspace(1,0,fl)[:,None]; put(vo,a,T,1.0); speech[int(T*SR):int((T+d)*SR)]=1
    if p['kind']=='clip':
        g0=p['gstart']
        for f2,g,v in M['ev']:
            l=g-g0-p['t0']  # event time inside this clip part
            if 0.2<=l<p['len']-0.2: put(sf,load(SP+f2),p['T0']+l,v)
for p in P['parts'][1:]: put(sf,load(SP+'mus/sfx_whoosh.mp3'),p['T0']-0.25,0.2)
H=json.load(open(f'/tmp/claude-0/hbs/audio/h_{sid}.json')); hs=''.join(H['characters'])
def hat(ph): return 0.05+H['character_start_times_seconds'][hs.index(ph)]
HK={'b01':[('sfx_heart',0.0,0.3),('sfx_pop','huge',0.35)],'b02':[('sfx_sleepy0','shuts',0.3)],'b03':[('sfx_whoosh',0.0,0.2),('sfx_lick','tongue',0.35)],
    'b04':[('sfx_whoosh',0.0,0.25),('sfx_pop','shoulder',0.35)],'b05':[('sfx_ding','red throat',0.25),('sfx_pop','no red',0.35)],'b06':[('sfx_hum',0.0,0.25),('sfx_pop','three-gram',0.3)],
    'b07':[('sfx_chirp',0.0,0.25),('sfx_ding','spider',0.25)],'b08':[('sfx_hum',0.0,0.25),('sfx_pop','get',0.35)],'b09':[('sfx_chirp',0.0,0.25),('sfx_pop','walk',0.35),('sfx_whoosh','feet',0.2)]}
for f2,w,v in HK.get(sid,[]): put(sf,load(SP+f'mus/{f2}.mp3'),w if isinstance(w,float) else hat(w)-0.05,v)
O=json.load(open(f'/tmp/claude-0/hbs/audio/o_{sid}.json')); os_=''.join(O['characters']); SPEC={x['id']:x for x in json.load(open('/tmp/claude-0/hbs/spec.json'))}
po=P['parts'][-1]['T0']+0.15; qs=po+O['character_start_times_seconds'][os_.index(SPEC[sid]['oqs'])]
put(sf,load(SP+'mus/sfx_pop.mp3'),po+0.05,0.3); put(sf,load(SP+'mus/sfx_ding.mp3'),qs-0.1,0.22)
mus={'b01':('mA',40),'b02':('mB',30),'b03':('mA',90),'b04':('mB',70),'b05':('mA',140),'b06':('mB',110),'b07':('mA',20),'b08':('mB',150),'b09':('mA',170)}.get(sid,('mA',60))
mu=load(SP+f'mus/{mus[0]}.mp3')[int(mus[1]*SR):][:N]; fi=int(0.3*SR); mu[:fi]*=np.linspace(0.3,1,fi)[:,None]; mu=np.pad(mu,((0,N-len(mu)),(0,0)))
k=int(0.4*SR); c=np.concatenate([[0],np.cumsum(speech,dtype=np.float64)]); idx=np.arange(N); lo=np.clip(idx-k//2,0,N); hi=np.clip(idx+k//2,0,N)
env=0.42-0.27*np.clip(((c[hi]-c[lo])/k)*1.6,0,1)
mix=vo+sf*0.8+mu*env[:,None]; fo=int(0.6*SR); mix[-fo:]*=np.linspace(1,0,fo)[:,None]
raw=f'/tmp/claude-0/hbs/out/{sid}.f32'; mix.astype(np.float32).tofile(raw)
subprocess.run(['ffmpeg','-y','-v','error','-f','f32le','-ar',str(SR),'-ac','2','-i',raw,'-af','loudnorm=I=-14:TP=-1.5:LRA=11','-ar',str(SR),f'/tmp/claude-0/hbs/out/{sid}.wav'],check=True)
print(sid,'ok',round(N/SR,2))
