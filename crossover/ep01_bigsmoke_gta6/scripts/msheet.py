import sys, glob, cv2, numpy as np
# usage: msheet.py out.jpg dir1 dir2 ... ; 6 frames per dir on magenta
outs=[]
for d in sys.argv[2:]:
    fs=sorted(glob.glob(d+'/f_*.png'))
    idx=np.linspace(0,len(fs)-1,6).astype(int)
    row=[]
    for i in idx:
        im=cv2.imread(fs[i],cv2.IMREAD_UNCHANGED).astype(np.float32)
        a=im[:,:,3:4]/255.
        bg=np.zeros_like(im[:,:,:3]); bg[:]=(255,0,255)
        c=(im[:,:,:3]*a+bg*(1-a)).astype(np.uint8)
        h=240; w=int(c.shape[1]*h/c.shape[0])
        c=cv2.resize(c,(w,h))
        cv2.putText(c,f"{d.split('/')[-1]} {i}",(5,20),0,0.6,(255,255,255),2)
        row.append(c)
    W=max(r.shape[1] for r in row)
    row=[cv2.copyMakeBorder(r,0,0,0,W-r.shape[1],cv2.BORDER_CONSTANT) for r in row]
    outs.append(np.hstack(row))
W=max(o.shape[1] for o in outs)
outs=[cv2.copyMakeBorder(o,0,0,0,W-o.shape[1],cv2.BORDER_CONSTANT) for o in outs]
cv2.imwrite(sys.argv[1],np.vstack(outs),[cv2.IMWRITE_JPEG_QUALITY,80])
