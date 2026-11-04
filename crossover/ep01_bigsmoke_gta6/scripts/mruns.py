import sys,glob,json,cv2,numpy as np
# usage: mruns.py dir maxx ; prints clean runs (official times)
d=sys.argv[1]; mx=int(sys.argv[2])
meta=json.load(open(d+'/meta.json')); fs=sorted(glob.glob(d+'/f_*.png'))
ok=[]
for f in fs:
    a=cv2.imread(f,cv2.IMREAD_UNCHANGED)[:,:,3]>127
    ys,xs=np.nonzero(a)
    good=len(xs)>0 and xs.max()<mx and not a[:,:3].any() and not a[:3,:].any() and not (a[118:122,:205].sum()>5 or a[:118,205:209].sum()>5)
    ok.append(good)
runs=[];s=None
for i,g in enumerate(ok+[False]):
    if g and s is None: s=i
    if not g and s is not None:
        if i-s>=6: runs.append((s,i-1))
        s=None
print(d,[(a,b,round(meta['t_in']+a/30,2),round(meta['t_in']+(b+1)/30,2),round((b-a+1)/30,2)) for a,b in runs])
