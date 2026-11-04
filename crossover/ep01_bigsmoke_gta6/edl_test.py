# EP01 test cut v1 (~28.8 s). Official timelines; see hd/offsets.json
import json,cv2,numpy as np
H_=1080
def meas(d,t,dur=0.0,rate=1.0):
    m=json.load(open(f'mattes/{d}/meta.json')); i0=int(round((t-m['t_in'])*30)); i1=i0+int(dur*30*rate)
    rh=m['roi'][3]-m['roi'][1]; yts=[]; hxs=[]; hws=[]
    for i in range(i0,max(i0,i1)+1,3):
        i=min(i,m['n']-1)
        a=cv2.imread(f'mattes/{d}/f_{i:05d}.png',cv2.IMREAD_UNCHANGED)[:,:,3]>127
        ys,xs=np.nonzero(a); yt=ys.min(); band=a[yt:yt+70]; bx=np.nonzero(band.any(0))[0]
        yts.append(yt); hxs.append(bx.mean()); hws.append(bx.max()-bx.min())
    return float(np.mean(hxs)), int(min(yts)), float(np.median(hws)), rh
def place(d,t,headx=0.42,top=110,hat=205,smax=1.85,dur=0.0,rate=1.0):
    hx,yt,hw,rh=meas(d,t,dur,rate)
    s=max(hat/hw,(H_+4-top)/(rh-yt)); s=min(s,smax)
    ox=headx*1920-hx*s; oy=H_+4-rh*s   # bottom of roi just below canvas
    return dict(s=round(s,3),ox=round(ox),oy=round(oy))
STORE=dict(key='E_b',t=706.4,still=True,cx=0.76,cy=0.52,blur=5.0)
HOUSE=dict(key='E_a',t=274.3,still=True,cx=0.75,cy=0.55,blur=4.0)
GR=dict(match=(0.40,0.20,0.20),ref='around',lightwrap=0.35,grain=3.2,sharpen=0.55,erode=1,soft=0.9,sat=1.06)
def comp(id,dur,bg,z,d,t,rate=1.0,pl=None,shake=None,grade=None):
    b=dict(bg); b['zoom']=z
    fg=dict(matte=f'mattes/{d}',t=t,rate=rate); fg.update(pl or place(d,t))
    s=dict(id=id,type='comp',dur=dur,bg=b,fg=fg,grade=dict(GR,**(grade or {})))
    if shake: s['shake']=shake
    return s
def plate(id,dur,key,t,z=(1.0,1.03),cx=0.5,cy=0.5,**kw):
    return dict(id=id,type='plate',dur=dur,key=key,t=t,zoom=z,cx=cx,cy=cy,**kw)
BAT=dict(s=1.6,ox=-6,oy=1084-int(720*1.6))
SHOTS=[
 plate('C1',2.20,'E_a',272.05,z=(1.10,1.16),cx=0.45,cy=0.56),
 comp('C2',2.20,HOUSE,(2.0,2.06),'M_bat',392.9,rate=0.75,pl=BAT,shake=dict(start=0.0,dur=0.45,amp=10)),
 plate('C3',0.85,'E_a',305.05,z=(1.0,1.04)),
 comp('C4',1.55,HOUSE,(2.08,2.12),'M_bat',394.75,pl=BAT),
 plate('C5',2.45,'E_a',316.30,z=(1.0,1.07)),
 plate('S1',1.95,'T1',76.60,z=(1.0,1.02)),
 plate('S2',0.95,'E_b',715.45,z=(1.0,1.03)),
 comp('S3',0.95,STORE,(2.0,2.03),'W_F',420.05,pl=place('W_F',420.05,headx=0.42,dur=0.95)),
 comp('S4',1.95,STORE,(2.0,2.05),'M_A',405.6,pl=place('M_A',405.6,headx=0.40,dur=1.95)),
 plate('S5',0.80,'E_b',720.85),
 comp('S6',1.50,STORE,(2.02,2.06),'W_B1',410.7,pl=place('W_B1',410.7,headx=0.43,dur=1.50)),
 plate('S7',2.15,'E_b',713.0,z=(1.0,1.04)),
 comp('S8',1.00,STORE,(2.0,2.03),'W_D',430.4,pl=place('W_D',430.4,headx=0.41,dur=1.00)),
 plate('S9',0.62,'E_b',721.85),
 comp('S10',1.15,STORE,(2.04,2.07),'W_P',402.47,pl=place('W_P',402.47,headx=0.42,dur=1.15)),
 plate('S11',1.13,'E_b',710.0,z=(1.15,1.18),cx=0.43,cy=0.55),
 plate('S12',0.55,'E_b',723.87),
 comp('S13',0.57,STORE,(2.01,2.03),'W_B1',412.6,pl=place('W_B1',412.6,headx=0.44,dur=0.57)),
 plate('S14',0.60,'E_b',720.05),
 comp('S15',0.60,STORE,(2.0,2.02),'M_A',407.55,pl=place('M_A',407.55,headx=0.40,dur=0.60)),
 plate('S16',0.67,'E_b',716.40),
 comp('S17',1.43,STORE,(2.0,2.05),'W_F',418.6,pl=place('W_F',418.6,headx=0.42,dur=1.43)),
 plate('S18',1.10,'E_b',722.58,z=(1.0,1.05)),
]
