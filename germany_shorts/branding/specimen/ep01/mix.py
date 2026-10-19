import json, subprocess, numpy as np
SR=48000
def load(f):
    r=subprocess.run(['ffmpeg','-v','error','-i',f,'-f','f32le','-ac','2','-ar',str(SR),'-'],capture_output=True,check=True).stdout
    return np.frombuffer(r,dtype=np.float32).reshape(-1,2).copy()
P=json.load(open('mixplan.json')); N=int((P['total']+0.2)*SR)
vo=np.zeros((N,2),np.float32); sf=np.zeros((N,2),np.float32); mu=np.zeros((N,2),np.float32)
def put(buf,a,t,v):
    i=int(t*SR); a=a[:max(0,N-i)]; buf[i:i+len(a)]+=a*v
speech=np.zeros(N,np.float32)
for f,t,d in P['voice']:
    a=load(f); put(vo,a,t,1.0); speech[int(t*SR):int((t+d)*SR)]=1
for f,t,v in P['ev']: put(sf,load(f),t,v)
A=load('mus/mA.mp3'); B=load('mus/mB.mp3')
# lift the very quiet intro of A
g=np.ones(len(A),np.float32); n1=int(8*SR); n2=int(16*SR); g[:n1]=4.0; g[n1:n2]=np.linspace(4.0,1.0,n2-n1); A=A*g[:,None]
put(mu,A,0,1.0); put(mu,B,P['total']-len(B)/SR,1.0)
# duck: smooth speech mask (0.4 s ramps)
k=int(0.4*SR); c=np.concatenate([[0],np.cumsum(speech,dtype=np.float64)]); idx=np.arange(N); lo=np.clip(idx-k//2,0,N); hi=np.clip(idx+k//2,0,N); sm=((c[hi]-c[lo])/k).astype(np.float32); env=0.42-0.27*np.clip(sm*1.6,0,1)
mix=vo+sf+mu*env[:,None]
# final fade
fo=int(2.5*SR); mix[-fo:]*=np.linspace(1,0,fo)[:,None]
mix.astype(np.float32).tofile('out/mix.f32')
subprocess.run(['ffmpeg','-y','-v','error','-f','f32le','-ar',str(SR),'-ac','2','-i','out/mix.f32','-af','loudnorm=I=-14:TP=-1.5:LRA=11','-ar',str(SR),'out/mix.wav'],check=True)
print('ok', N/SR)
