import subprocess, json, sys, numpy as np
from numpy.fft import rfft, irfft
SR=8000
def pcm(path, ss=None, t=None):
    cmd=['ffmpeg','-loglevel','error']
    if ss is not None: cmd+=['-ss',str(max(0,ss))]
    cmd+=['-i',path]
    if t is not None: cmd+=['-t',str(t)]
    cmd+=['-vn','-ac','1','-ar',str(SR),'-f','s16le','-']
    return np.frombuffer(subprocess.run(cmd,capture_output=True).stdout,np.int16).astype(np.float32)
def find(seg, ref):
    n=1<<int(np.ceil(np.log2(len(ref)+len(seg))))
    c=irfft(rfft(ref,n)*np.conj(rfft(seg,n)),n)[:len(ref)-len(seg)]
    k=int(np.argmax(c))
    nc=c[k]/(np.linalg.norm(seg)*np.linalg.norm(ref[k:k+len(seg)])+1e-9)
    return k/SR, nc
# name: (hd file, 360p ref, requested start)
jobs={'E_a':('E_a.mkv','tJbzMqJGH4k.mp4',250),'E_b':('E_b.mkv','tJbzMqJGH4k.mp4',690),'E_c':('E_c.mkv','tJbzMqJGH4k.mp4',780),
 'E_d':('E_d.mkv','tJbzMqJGH4k.mp4',1525),'E_g':('E_g.mkv','tJbzMqJGH4k.mp4',571),
 'BG_a':('BG_a.mkv','OpTizzox2Qo.mp4',280),'BG_b':('BG_b.mkv','OpTizzox2Qo.mp4',380),
 'EL_a':('EL_a.mkv','H5lj23EUR9U.mp4',585),'EL_b':('EL_b.mkv','H5lj23EUR9U.mp4',760),
 'T1':('QdBZY2fkU-0.mkv','QdBZY2fkU-0.mp4',0),'T2':('VQRLujxTm3c.mkv','VQRLujxTm3c.mp4',0),'L':('rz1B4B2yBZY.mkv','rz1B4B2yBZY.mp4',0),
 'DT':('E1aTlYlfzRk.mkv','E1aTlYlfzRk.mp4',0),'TR':('cF3GK_sfPVM.mkv','cF3GK_sfPVM.mp4',0)}
out={}
for k,(hdf,ref,st) in jobs.items():
    res=[]
    for probe in [6,16]:
        seg=pcm('hd/'+hdf,probe,8)
        r0=st+probe-20
        ref_a=pcm('src/'+ref,r0,40)
        off,nc=find(seg,ref_a)
        official=max(0,r0)+off   # official time of hd t=probe
        res.append((round(official-probe,3),round(nc,3)))
    out[k]={'file':hdf,'offset':res[0][0],'check':res}
    print(k,res,flush=True)
json.dump(out,open('hd/offsets.json','w'),indent=1)
