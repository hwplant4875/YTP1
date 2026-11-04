"""usage: python3 -I scripts/mix.py audio_events.py out.wav"""
import sys, subprocess, json, importlib.util, numpy as np
SR=48000
spec=importlib.util.spec_from_file_location('a',sys.argv[1]); A=importlib.util.module_from_spec(spec); spec.loader.exec_module(A)
def load(f,a,b,flt):
    af=f'atrim=0:{b-a:.4f}'+(','+flt if flt else '')
    raw=subprocess.run(['ffmpeg','-loglevel','error','-ss',f'{a:.4f}','-t',f'{b-a+0.05:.4f}','-i',f,'-af',af,'-ac','2','-ar',str(SR),'-f','f32le','-'],capture_output=True,check=True).stdout
    return np.frombuffer(raw,np.float32).reshape(-1,2).copy()
def lufs(x):
    # BS.1770 approx: K-weighting via ffmpeg ebur128 is heavy; use simple gated RMS with K-ish weighting from ffmpeg
    p=subprocess.run(['ffmpeg','-hide_banner','-f','f32le','-ar',str(SR),'-ac','2','-i','-','-af','loudnorm=print_format=json','-f','null','-'],input=x.astype(np.float32).tobytes(),capture_output=True)
    t=p.stderr.decode(); j=json.loads(t[t.rfind('{'):t.rfind('}')+1]); return float(j['input_i'])
mix=np.zeros((int(A.TOTAL*SR)+SR,2),np.float32); log=[]
for name,f,a,b,tp,target,fi,fo,flt in A.EVENTS:
    x=load(f,a,b,flt)
    L=lufs(x) if len(x)>SR*0.4 else None
    g=10**((target-L)/20) if L is not None and L>-70 else 1.0
    x=x*g
    n=len(x); fin=int(fi*SR); fout=int(fo*SR)
    if fin>0: x[:fin]*=np.linspace(0,1,fin)[:,None]
    if fout>0: x[-fout:]*=np.linspace(1,0,fout)[:,None]
    i0=int(round(tp*SR)); mix[i0:i0+n]+=x[:max(0,len(mix)-i0)]
    log.append((name,round(L,1) if L else None,round(20*np.log10(g),1),tp,round(tp+n/SR,2)))
mix=mix[:int(A.TOTAL*SR)]
for l in log: print(l)
tmp=sys.argv[2]+'.pre.f32'
mix.astype(np.float32).tofile(tmp)
# final loudness -14 LUFS, TP -1.5 (two-pass)
p=subprocess.run(['ffmpeg','-hide_banner','-f','f32le','-ar',str(SR),'-ac','2','-i',tmp,'-af','loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json','-f','null','-'],capture_output=True)
t=p.stderr.decode(); j=json.loads(t[t.rfind('{'):t.rfind('}')+1])
af=f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true"
subprocess.run(['ffmpeg','-loglevel','error','-y','-f','f32le','-ar',str(SR),'-ac','2','-i',tmp,'-af',af,'-ar',str(SR),'-c:a','pcm_s16le',sys.argv[2]],check=True)
print('pre-mix I',j['input_i'],'TP',j['input_tp'])
