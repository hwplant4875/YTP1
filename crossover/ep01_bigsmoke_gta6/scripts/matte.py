"""Matte a character out of an HD source range.
usage: python3 -I matte.py JOB.json
JOB: {"key":"BG_b","t_in":392.0,"t_out":394.4,"roi":[x0,y0,x1,y1],"zero":[[x0,y0,x1,y1],...],
      "seed":[x0,y0,x1,y1], "model":"rvm"|"birefnet", "out":"mattes/M2", "dsr":0.5}
Writes out/f_00000.png (RGBA, roi-sized), one per source frame, and meta.json (fps, t_in, n)."""
import json, subprocess, sys, os, time
import numpy as np, cv2
O=json.load(open('hd/offsets.json'))
job=json.load(open(sys.argv[1]))
src='hd/'+O[job['key']]['file']; off=O[job['key']]['offset']
os.makedirs(job['out'],exist_ok=True)
w,h=map(int,subprocess.run(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height','-of','csv=p=0',src],capture_output=True,text=True).stdout.strip().split(','))
fps=30.0
t0=job['t_in']-off; dur=job['t_out']-job['t_in']
cmd=['ffmpeg','-loglevel','error','-ss',f'{t0:.3f}','-i',src,'-t',f'{dur:.3f}','-vf','fps=30','-f','rawvideo','-pix_fmt','rgb24','-']
p=subprocess.Popen(cmd,stdout=subprocess.PIPE)
x0,y0,x1,y1=job['roi']; rw,rh=x1-x0,y1-y0
model=job.get('model','rvm')
import onnxruntime as ort
so=ort.SessionOptions(); so.intra_op_num_threads=int(os.environ.get('NT','4'))
if model=='rvm':
    sess=ort.InferenceSession('models/rvm_mobilenetv3_fp32.onnx',so,providers=['CPUExecutionProvider'])
    rec=[np.zeros([1,1,1,1],np.float32)]*4
    dsr=np.array([job.get('dsr',0.5)],np.float32)
else:
    sess=ort.InferenceSession('/root/.rembg/models/birefnet-general-lite/birefnet-general-lite.onnx',so,providers=['CPUExecutionProvider'])
mean=np.array([0.485,0.456,0.406],np.float32); std=np.array([0.229,0.224,0.225],np.float32)
def post(a):
    a=a.astype(np.float32)
    for zx0,zy0,zx1,zy1 in job.get('zero',[]):
        a[max(0,zy0-y0):max(0,zy1-y0), max(0,zx0-x0):max(0,zx1-x0)]=0
    if 'seed' in job:
        sx0,sy0,sx1,sy1=job['seed']
        m=(a>0.3).astype(np.uint8)
        n,lab=cv2.connectedComponents(m)
        keep=np.zeros_like(m)
        seedlab=set(np.unique(lab[sy0-y0:sy1-y0, sx0-x0:sx1-x0]))-{0}
        for l in seedlab: keep|=(lab==l).astype(np.uint8)
        keep=cv2.dilate(keep,np.ones((9,9),np.uint8))
        a=a*keep
    return np.clip(a,0,1)
i=0; t=time.time()
while True:
    buf=p.stdout.read(w*h*3)
    if len(buf)<w*h*3: break
    fr=np.frombuffer(buf,np.uint8).reshape(h,w,3)[y0:y1,x0:x1]
    if model=='rvm':
        x=(fr.astype(np.float32)/255.).transpose(2,0,1)[None]
        fgr,pha,*rec=sess.run(None,{'src':x,'r1i':rec[0],'r2i':rec[1],'r3i':rec[2],'r4i':rec[3],'downsample_ratio':dsr})
        a=pha[0,0]
    else:
        x=cv2.resize(fr,(1024,1024),interpolation=cv2.INTER_AREA).astype(np.float32)/255.
        x=((x-mean)/std).transpose(2,0,1)[None].astype(np.float32)
        o=sess.run(None,{'input_image':x})[0][0,0]
        o=1/(1+np.exp(-o)) if (o.min()<0 or o.max()>1) else o
        a=cv2.resize(o,(rw,rh),interpolation=cv2.INTER_CUBIC)
    a=post(a)
    rgba=np.dstack([fr,(a*255+0.5).astype(np.uint8)])
    cv2.imwrite(f"{job['out']}/f_{i:05d}.png",cv2.cvtColor(rgba,cv2.COLOR_RGBA2BGRA))
    i+=1
    if i%30==0: print(job['out'],i,'frames',round((time.time()-t)/i,2),'s/f',flush=True)
json.dump({'fps':fps,'t_in':job['t_in'],'n':i,'roi':job['roi'],'key':job['key']},open(job['out']+'/meta.json','w'))
print('done',job['out'],i,round(time.time()-t,1),'s')
