"""Render an EDL (python module with SHOTS list) to video frames -> ffmpeg.
usage: python3 -I scripts/render.py edl_module_path out.mp4 [--only S3,S4] [--preview]"""
import json, subprocess, sys, os, math, importlib.util, time
import numpy as np, cv2
W,H,FPS=1920,1080,30
O=json.load(open('hd/offsets.json'))
def srcinfo(key):
    f='hd/'+O[key]['file']
    w,h=map(int,subprocess.run(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height','-of','csv=p=0',f],capture_output=True,text=True).stdout.strip().split(','))
    return f,w,h
def decode(key,t,dur,scale=None):
    """yield RGB frames (full source res unless scale=(w,h)) for official time t..t+dur at 30fps"""
    f,w,h=srcinfo(key); ft=t-O[key]['offset']
    vf='fps=30'
    ow,oh=w,h
    if scale: vf+=f',scale={scale[0]}:{scale[1]}:flags=lanczos'; ow,oh=scale
    n=int(round(dur*FPS))
    p=subprocess.Popen(['ffmpeg','-loglevel','quiet','-ss',f'{ft:.3f}','-i',f,'-t',f'{dur+0.5:.3f}','-vf',vf,'-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
    last=None
    for i in range(n):
        b=p.stdout.read(ow*oh*3)
        if len(b)<ow*oh*3:
            if last is None: raise RuntimeError(f'no frames {key}@{t}')
            yield last; continue
        last=np.frombuffer(b,np.uint8).reshape(oh,ow,3); yield last
    p.kill()
def still(key,t):
    return next(decode(key,t,1/FPS))
def zoomcrop(img,cx,cy,z):
    """crop a 16:9 window of size (w/z) centered at normalized (cx,cy), clamp inside, resize to W,H"""
    h,w=img.shape[:2]
    cw=w/z; ch=cw*9/16
    if ch>h: ch=h; cw=ch*16/9
    x0=min(max(cx*w-cw/2,0),w-cw); y0=min(max(cy*h-ch/2,0),h-ch)
    M=np.array([[W/cw,0,-x0*W/cw],[0,H/ch,-y0*H/ch]],np.float32)
    return cv2.warpAffine(img,M,(W,H),flags=cv2.INTER_LANCZOS4 if W/cw>1 else cv2.INTER_AREA,borderMode=cv2.BORDER_REFLECT)
def ease(x): return 0.5-0.5*math.cos(math.pi*min(max(x,0),1))
def lab_stats(img,mask=None):
    lab=cv2.cvtColor(img.astype(np.float32)/255.,cv2.COLOR_RGB2LAB)
    if mask is not None: px=lab[mask]
    else: px=lab.reshape(-1,3)
    return px.mean(0),px.std(0)+1e-3
def apply_match(fg,mf,sf,mb,sb,k):
    lab=cv2.cvtColor(fg.astype(np.float32)/255.,cv2.COLOR_RGB2LAB)
    k=np.array(k,np.float32)
    scale=1+k*(sb/sf-1); shift=k*(mb-mf)
    lab=(lab-mf)*scale+mf+shift
    out=cv2.cvtColor(lab,cv2.COLOR_LAB2RGB)*255.
    return np.clip(out,0,255)
def load_matte(d,idx):
    meta=json.load(open(d+'/meta.json'))
    idx=min(max(idx,0),meta['n']-1)
    im=cv2.imread(f'{d}/f_{idx:05d}.png',cv2.IMREAD_UNCHANGED)
    im=cv2.cvtColor(im,cv2.COLOR_BGRA2RGBA)
    return im[...,:3].astype(np.float32),im[...,3].astype(np.float32)/255.,meta
def render_comp(s):
    n=int(round(s['dur']*FPS))
    bgs=s['bg']; fgs=s['fg']
    # background
    if bgs.get('still',True):
        bimg=still(bgs['key'],bgs['t']).astype(np.float32)
        bframes=None
    else:
        bframes=decode(bgs['key'],bgs['t'],s['dur'])
    meta=json.load(open(fgs['matte']+'/meta.json'))
    i0=int(round((fgs['t']-meta['t_in'])*FPS))
    rate=fgs.get('rate',1.0)
    # placement: roi height -> fh*H, center x fx*W, bottom fy*H
    rx0,ry0,rx1,ry1=meta['roi']; rw,rh=rx1-rx0,ry1-ry0
    sc=fgs['fh']*H/rh if 'fh' in fgs else 1.0
    if fgs.get('crop'):  # sub-crop of roi in roi px (x0,y0,x1,y1) to use; placement refers to roi still
        pass
    if 's' in fgs: sc=fgs['s']
    fw,fh_=int(round(rw*sc)),int(round(rh*sc))
    if 'ox' in fgs: ox,oy=int(round(fgs['ox'])),int(round(fgs['oy']))
    else: ox=int(round(fgs['fx']*W-fw/2)); oy=int(round(fgs['fy']*H-fh_))
    flip=fgs.get('flip',False)
    g=s.get('grade',{})
    stats=None
    rng=np.random.default_rng(7)
    for i in range(n):
        tt=i/FPS
        if bframes is not None: bimg=next(bframes).astype(np.float32)
        z0,z1=bgs.get('zoom',(1.0,1.0)); z=z0+(z1-z0)*ease(i/max(n-1,1))
        bg=zoomcrop(bimg,bgs.get('cx',0.5),bgs.get('cy',0.5),z).astype(np.float32)
        if bgs.get('blur',0)>0: bg=cv2.GaussianBlur(bg,(0,0),bgs['blur'])
        if 'bg_gain' in g: bg=bg*g['bg_gain']
        fidx=i0+int(math.floor(i*rate))
        if fgs.get('hold') is not None and i*rate>=fgs['hold']*FPS: fidx=i0+int(fgs['hold']*FPS)
        frgb,fa,_=load_matte(fgs['matte'],fidx)
        if flip: frgb=frgb[:,::-1]; fa=fa[:,::-1]
        interp=cv2.INTER_CUBIC if sc>1 else cv2.INTER_AREA
        frgb=cv2.resize(frgb,(fw,fh_),interpolation=interp); fa=cv2.resize(fa,(fw,fh_),interpolation=cv2.INTER_LINEAR)
        shp=g.get('sharpen',0.0)
        if shp>0:
            bl=cv2.GaussianBlur(frgb,(0,0),g.get('sharpen_sigma',1.4)); frgb=np.clip(frgb+(frgb-bl)*shp,0,255)
        # alpha refine
        er=g.get('erode',1)
        if er>0: fa=cv2.erode(fa,np.ones((2*er+1,2*er+1),np.uint8))
        fa=cv2.GaussianBlur(fa,(0,0),g.get('soft',0.9))
        # paste into full canvas
        F=np.zeros((H,W,3),np.float32); A=np.zeros((H,W),np.float32)
        x0,y0=max(ox,0),max(oy,0); x1,y1=min(ox+fw,W),min(oy+fh_,H)
        if x1>x0 and y1>y0:
            F[y0:y1,x0:x1]=frgb[y0-oy:y1-oy,x0-ox:x1-ox]; A[y0:y1,x0:x1]=fa[y0-oy:y1-oy,x0-ox:x1-ox]
        if stats is None:
            m=A>0.6
            mf,sf=lab_stats(F,m)
            ref=g.get('ref','around')
            if ref=='around':
                ring=cv2.dilate((A>0.05).astype(np.uint8),np.ones((151,151),np.uint8)).astype(bool)
                mb,sb=lab_stats(bg,ring)
            else: mb,sb=lab_stats(bg)
            stats=(mf,sf,mb,sb)
        k=g.get('match',(0.45,0.35,0.35))
        F=apply_match(F,*stats,k)
        if 'exposure' in g: F=F*g['exposure']
        if 'sat' in g:
            gray=F.mean(2,keepdims=True); F=gray+(F-gray)*g['sat']
        if 'tint' in g: F=F*np.array(g['tint'],np.float32)
        # light wrap
        lw=g.get('lightwrap',0.45)
        if lw>0:
            bgb=cv2.GaussianBlur(bg,(0,0),20)
            inner=A*(1-cv2.GaussianBlur(A,(0,0),7))
            inner=np.clip(inner*2.2,0,1)[...,None]*lw
            F=F*(1-inner)+bgb*inner
        # contact shadow / vignette behind fg (optional)
        if g.get('shadow',0)>0:
            sh=cv2.GaussianBlur(A,(0,0),35)*g['shadow']
            bg=bg*(1-sh[...,None])
        out=F*A[...,None]+bg*(1-A[...,None])
        # fg defocus to match? optional sharpen fg
        # grain
        gr=g.get('grain',3.0)
        if gr>0: out=out+rng.normal(0,gr,(H,W,1)).astype(np.float32)
        # shake
        sk=s.get('shake')
        if sk and sk['start']<=tt<sk['start']+sk['dur']:
            a=sk['amp']*(1-(tt-sk['start'])/sk['dur'])
            dx,dy=rng.uniform(-a,a),rng.uniform(-a,a)
            M=np.array([[1.04,0,dx-0.02*W],[0,1.04,dy-0.02*H]],np.float32)
            out=cv2.warpAffine(out,M,(W,H),borderMode=cv2.BORDER_REFLECT)
        yield np.clip(out,0,255).astype(np.uint8)
def render_plate(s):
    n=int(round(s['dur']*FPS))
    z0,z1=s.get('zoom',(1.0,1.0)); cx,cy=s.get('cx',0.5),s.get('cy',0.5)
    rate=s.get('rate',1.0)
    if s.get('freeze') is not None:
        img=still(s['key'],s['freeze']).astype(np.float32)
        frames=(img for _ in range(n))
    elif rate!=1.0:
        allf=list(decode(s['key'],s['t'],s['dur']*rate+0.1))
        frames=(allf[min(int(i*rate),len(allf)-1)] for i in range(n))
    else:
        frames=decode(s['key'],s['t'],s['dur'])
    rng=np.random.default_rng(3)
    for i,fr in enumerate(frames):
        z=z0+(z1-z0)*ease(i/max(n-1,1))
        out=zoomcrop(np.asarray(fr),cx,cy,z).astype(np.float32)
        if s.get('gain'): out=out*s['gain']
        sk=s.get('shake')
        tt=i/FPS
        if sk and sk['start']<=tt<sk['start']+sk['dur']:
            a=sk['amp']*(1-(tt-sk['start'])/sk['dur'])
            dx,dy=rng.uniform(-a,a),rng.uniform(-a,a)
            M=np.array([[1.04,0,dx-0.02*W],[0,1.04,dy-0.02*H]],np.float32)
            out=cv2.warpAffine(out,M,(W,H),borderMode=cv2.BORDER_REFLECT)
        yield np.clip(out,0,255).astype(np.uint8)
def main():
    path=sys.argv[1]; out=sys.argv[2]
    spec=importlib.util.spec_from_file_location('edl',path); edl=importlib.util.module_from_spec(spec); spec.loader.exec_module(edl)
    only=None
    for a in sys.argv[3:]:
        if a.startswith('--only='): only=set(a.split('=')[1].split(','))
    shots=[s for s in edl.SHOTS if (only is None or s['id'] in only)]
    if '--stills' in sys.argv:
        os.makedirs(out,exist_ok=True)
        for s in shots:
            dur=s['dur']; s2=dict(s); 
            gen=render_comp(s2) if s['type']=='comp' else render_plate(s2)
            n=int(round(dur*FPS)); pick={0,n//2,n-1}
            for i,fr in enumerate(gen):
                if i in pick: cv2.imwrite(f"{out}/{s['id']}_{i:03d}.jpg",cv2.cvtColor(fr,cv2.COLOR_RGB2BGR),[cv2.IMWRITE_JPEG_QUALITY,88])
            print('still',s['id'],flush=True)
        return
    enc=subprocess.Popen(['ffmpeg','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-c:v','libx264','-preset','medium','-crf','15','-pix_fmt','yuv420p','-movflags','+faststart',out],stdin=subprocess.PIPE)
    total=0; t=time.time(); marks=[]
    for s in shots:
        gen=render_comp(s) if s['type']=='comp' else render_plate(s)
        c=0
        for fr in gen:
            enc.stdin.write(fr.tobytes()); c+=1
        marks.append((s['id'],round(total/FPS,3),c)); total+=c
        print(s['id'],c,'frames',round(time.time()-t,1),'s',flush=True)
    enc.stdin.close(); enc.wait()
    json.dump(marks,open(out+'.marks.json','w'))
    print('done',total,'frames',round(total/FPS,2),'s')
if __name__=='__main__': main()
