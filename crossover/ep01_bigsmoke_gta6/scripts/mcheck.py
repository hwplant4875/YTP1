import sys,glob,json,cv2,numpy as np
# per-frame: bbox of alpha>0.5 and touches: L(x<=1) R(x>=rw-2) T(y<=1) W(watermark box edge) 
for d in sys.argv[1:]:
    meta=json.load(open(d+'/meta.json')); x0,y0,x1,y1=meta['roi']; rw,rh=x1-x0,y1-y0
    fs=sorted(glob.glob(d+'/f_*.png')); out=[]
    for i,f in enumerate(fs):
        a=cv2.imread(f,cv2.IMREAD_UNCHANGED)[:,:,3]>127
        ys,xs=np.nonzero(a)
        if len(xs)==0: out.append(f'{i}:empty'); continue
        fl=''
        if a[:,:3].any(): fl+='L'
        if a[:,-12:].sum()>30: fl+='R'
        if a[:3,:].any(): fl+='T'
        # watermark box edges (box 0..205 x 0..118 in roi coords) 
        if a[118:122,:205].sum()>5 or a[:118,205:209].sum()>5: fl+='W'
        out.append(f'{i}:{xs.min()}-{xs.max()}{fl}')
    print(d, meta['t_in'], ' '.join(out[::6]))
