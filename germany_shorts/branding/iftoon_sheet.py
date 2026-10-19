from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
import math, random
S=2
F="/home/user/YTP1/germany_shorts/fonts/"
BLK=(22,16,28); DREAM=(255,205,60); DSH=(240,158,40); WHITE=(255,255,255)
CAP=(96,120,240); CAPSH=(66,84,200); CREAM=(255,246,228); CREAMSH=(226,206,180)
def fnt(n,s): return ImageFont.truetype(F+n,int(s*S))
def M(W,H): return Image.new("L",(W,H),0)
def caps(m,a,b,w):
    d=ImageDraw.Draw(m); d.line([a,b],fill=255,width=int(w)); r=w/2
    for p in (a,b): d.ellipse([p[0]-r,p[1]-r,p[0]+r,p[1]+r],fill=255)
def cel(im,mask,base,shade,ow,light=(-1,-1),k=0.13):
    W,H=im.size; bb=mask.getbbox(); sz=max(bb[2]-bb[0],bb[3]-bb[1])
    o=mask.filter(ImageFilter.MaxFilter(int(ow)|1))
    im.paste(Image.new("RGB",(W,H),BLK),(0,0),o)
    im.paste(Image.new("RGB",(W,H),base),(0,0),mask)
    dx,dy=int(light[0]*sz*k),int(light[1]*sz*k)
    sh=ImageChops.subtract(mask,ImageChops.offset(mask,dx,dy))
    im.paste(Image.new("RGB",(W,H),shade),(0,0),sh)
def halftone_bg(W,H,c1,c2,step=14):
    im=Image.new("RGB",(W,H),c1); d=ImageDraw.Draw(im)
    for y in range(0,H,step*S):
        for x in range(0,W,step*S):
            t=((x/W)*0.6+(1-y/H)*0.4); r=step*S*0.42*t
            ox=(step*S//2) if (y//(step*S))%2 else 0
            d.ellipse([x+ox-r,y-r,x+ox+r,y+r],fill=c2)
    return im
def panel_border(im,w=10):
    d=ImageDraw.Draw(im); W,H=im.size; d.rectangle([0,0,W-1,H-1],outline=BLK,width=w*S)

def toon(im,cx,base,r,cap=False,mood="happy",pose="wave"):
    W,H=im.size; hy=base-r*3.9; neck=hy+r*0.9; hip=neck+r*1.3; lw=r*0.28; ow=r*0.12
    body=M(W,H); ImageDraw.Draw(body).rounded_rectangle([cx-r*0.36,neck-r*0.1,cx+r*0.36,hip+r*0.2],radius=int(r*0.36),fill=255)
    if pose=="run":
        caps(body,(cx-r*0.15,hip),(cx-r*0.7,base-r*0.3),lw); caps(body,(cx+r*0.15,hip),(cx+r*0.55,hip+r*0.6),lw); caps(body,(cx+r*0.55,hip+r*0.6),(cx+r*0.25,base-r*0.15),lw)
    else:
        caps(body,(cx-r*0.17,hip),(cx-r*0.24,base-r*0.15),lw); caps(body,(cx+r*0.17,hip),(cx+r*0.24,base-r*0.15),lw)
        ImageDraw.Draw(body).ellipse([cx-r*0.52,base-r*0.3,cx-r*0.04,base],fill=255); ImageDraw.Draw(body).ellipse([cx+r*0.04,base-r*0.3,cx+r*0.52,base],fill=255)
    sh=neck+r*0.25
    if pose=="wave": caps(body,(cx-r*0.3,sh),(cx-r*0.7,sh+r*0.9),lw); caps(body,(cx+r*0.3,sh),(cx+r*1.4,sh-r*0.45),lw)
    elif pose=="shock": caps(body,(cx-r*0.3,sh),(cx-r*1.2,sh-r*0.7),lw); caps(body,(cx+r*0.3,sh),(cx+r*1.2,sh-r*0.7),lw)
    elif pose=="run": caps(body,(cx-r*0.3,sh),(cx-r*1.0,sh+r*0.3),lw); caps(body,(cx+r*0.3,sh),(cx+r*0.9,sh-r*0.4),lw)
    else: caps(body,(cx-r*0.3,sh),(cx-r*0.7,sh+r*0.9),lw); caps(body,(cx+r*0.3,sh),(cx+r*0.7,sh+r*0.9),lw)
    cel(im,body,DREAM,DSH,ow)
    head=M(W,H); ImageDraw.Draw(head).ellipse([cx-r,hy-r*0.95,cx+r,hy+r*0.95],fill=255)
    cel(im,head,DREAM,DSH,ow,k=0.12)
    d=ImageDraw.Draw(im)
    # face (manga style): big oval eyes with two highlights, small blush hatch
    ey=hy+r*0.02; ex=r*0.34
    for s in (-1,1):
        x=cx+s*ex
        if mood=="sleepy": d.arc([x-r*0.15,ey-r*0.12,x+r*0.15,ey+r*0.14],start=20,end=160,fill=BLK,width=int(r*0.08))
        elif mood=="shock":
            d.ellipse([x-r*0.17,ey-r*0.22,x+r*0.17,ey+r*0.22],fill=WHITE,outline=BLK,width=int(r*0.06)); d.ellipse([x-r*0.05,ey-r*0.05,x+r*0.05,ey+r*0.05],fill=BLK)
        else:
            d.ellipse([x-r*0.13,ey-r*0.19,x+r*0.13,ey+r*0.19],fill=BLK)
            d.ellipse([x-r*0.07+r*0.03,ey-r*0.14,x+r*0.03+r*0.05,ey-r*0.03],fill=WHITE)
            d.ellipse([x-r*0.06,ey+r*0.06,x-r*0.01,ey+r*0.11],fill=WHITE)
        for k in range(3): d.line([cx+s*r*0.6-r*0.12+k*r*0.08,hy+r*0.3,cx+s*r*0.6-r*0.06+k*r*0.08,hy+r*0.2],fill=(232,96,80),width=int(r*0.035))
    my=hy+r*0.4
    if mood=="shock": d.ellipse([cx-r*0.13,my-r*0.1,cx+r*0.13,my+r*0.22],fill=BLK)
    elif mood=="sleepy": d.ellipse([cx-r*0.05,my,cx+r*0.05,my+r*0.08],fill=BLK)
    else:
        d.chord([cx-r*0.22,my-r*0.14,cx+r*0.22,my+r*0.22],start=0,end=180,fill=BLK); d.chord([cx-r*0.11,my+r*0.03,cx+r*0.11,my+r*0.2],start=0,end=180,fill=(240,100,100))
    if cap:
        c=M(W,H); dc=ImageDraw.Draw(c)
        dc.chord([cx-r*1.02,hy-r*1.12,cx+r*1.02,hy+r*0.5],start=180,end=360,fill=255)
        P=[(cx-r*0.1,hy-r*0.8),(cx+r*0.55,hy-r*1.75),(cx+r*1.25,hy-r*1.0),(cx+r*1.35,hy-r*0.35)]
        for i in range(61):
            t=i/60; u=1-t
            x=u**3*P[0][0]+3*u*u*t*P[1][0]+3*u*t*t*P[2][0]+t**3*P[3][0]; y=u**3*P[0][1]+3*u*u*t*P[1][1]+3*u*t*t*P[2][1]+t**3*P[3][1]
            rr=r*(0.62*(1-t)**1.1+0.07); dc.ellipse([x-rr,y-rr,x+rr,y+rr],fill=255)
        ImageDraw.Draw(c).rectangle([0,hy-r*0.2,cx+r*0.95,H],fill=0)
        cel(im,c,CAP,CAPSH,ow,light=(-1,-1))
        b=M(W,H); ImageDraw.Draw(b).rounded_rectangle([cx-r*1.08,hy-r*0.44,cx+r*1.08,hy-r*0.12],radius=int(r*0.15),fill=255); cel(im,b,CREAM,CREAMSH,ow)
        px,py=P[3]; p=M(W,H); ImageDraw.Draw(p).ellipse([px-r*0.25,py-r*0.25,px+r*0.25,py+r*0.25],fill=255); cel(im,p,CREAM,CREAMSH,ow)

def burst(im,cx,cy,R,text,fill=(255,70,70),tcol=WHITE,n=14,size=60):
    d=ImageDraw.Draw(im); pts=[]; random.seed(int(cx))
    for i in range(n*2):
        a=i*math.pi/n; rr=R*(1 if i%2==0 else 0.62)*random.uniform(0.9,1.08); pts.append((cx+rr*math.cos(a),cy+rr*0.8*math.sin(a)))
    d.polygon(pts,fill=fill,outline=BLK,width=int(6*S))
    d.text((cx,cy),text,font=fnt("YouTubeSans-Black.otf",size),fill=tcol,anchor="mm",stroke_width=int(5*S),stroke_fill=BLK)
def speedlines(im,cx,cy,n=60,inner=0.3,col=BLK):
    W,H=im.size; d=ImageDraw.Draw(im); random.seed(3)
    for i in range(n):
        a=random.uniform(0,2*math.pi); r0=random.uniform(inner,inner+0.1)*W; r1=W*1.2; w=random.uniform(2,7)*S
        d.polygon([(cx+r0*math.cos(a),cy+r0*math.sin(a)),(cx+r1*math.cos(a-0.012),cy+r1*math.sin(a-0.012)),(cx+r1*math.cos(a+0.012),cy+r1*math.sin(a+0.012))],fill=col)
def motion(im,x0,y0,n=5,length=180):
    d=ImageDraw.Draw(im)
    for i in range(n): y=y0+i*28*S; d.line([x0-length*S*(0.6+0.4*(i%2)),y,x0,y],fill=BLK,width=int(6*S))
def sweat(im,x,y,r):
    d=ImageDraw.Draw(im); d.polygon([(x,y-r*1.6),(x-r,y),(x+r,y)],fill=(150,210,255),outline=BLK); d.ellipse([x-r,y-r,x+r,y+r],fill=(150,210,255),outline=BLK,width=int(3*S))
def bubble(im,x,y,w,h,text,size=44):
    d=ImageDraw.Draw(im); d.rounded_rectangle([x-w/2,y-h/2,x+w/2,y+h/2],radius=int(h/2),fill=WHITE,outline=BLK,width=int(5*S))
    d.polygon([(x-w*0.12,y+h/2-3*S),(x-w*0.3,y+h*0.95),(x+w*0.02,y+h/2-3*S)],fill=WHITE,outline=BLK,width=int(5*S)); d.line([(x-w*0.12+6*S,y+h/2-3*S),(x+w*0.02-6*S,y+h/2-3*S)],fill=WHITE,width=int(8*S))
    d.text((x,y),text,font=fnt("YouTubeSans-Black.otf",size),fill=BLK,anchor="mm")

BG1=(255,236,170); BG1d=(255,214,110); BG2=(176,214,255); BG2d=(130,180,245)
def hero(cap):
    W,H=900*S,1100*S; im=halftone_bg(W,H,BG1 if not cap else BG2,BG1d if not cap else BG2d)
    toon(im,W//2,int(H*0.93),int(150*S),cap=cap,mood="happy",pose="wave")
    bubble(im,int(W*0.28),int(H*0.12),int(330*S),int(110*S),"WHAT IF...?",52)
    panel_border(im); return im
def fx_panels():
    out=[]
    W,H=600*S,600*S
    a=halftone_bg(W,H,(255,250,235),(255,200,120)); burst(a,W*0.5,H*0.32,230*S,"WHAT IF?!",size=70); toon(a,W*0.5,int(H*1.02),int(62*S),cap=True,mood="shock",pose="shock"); panel_border(a); out.append(("말풍선 폭발","WHAT IF?!",a))
    b=Image.new("RGB",(W,H),(255,255,255)); speedlines(b,W*0.5,H*0.52,90,0.22); toon(b,W*0.5,int(H*0.95),int(70*S),cap=True,mood="shock",pose="shock")
    d=ImageDraw.Draw(b); d.text((W*0.5,H*0.1),"!!",font=fnt("YouTubeSans-Black.otf",90),fill=(255,70,70),anchor="mm",stroke_width=5*S,stroke_fill=BLK); sweat(b,W*0.68,H*0.3,14*S); panel_border(b); out.append(("집중선 + 충격","",b))
    c=halftone_bg(W,H,(200,235,255),(150,205,250)); toon(c,W*0.58,int(H*0.95),int(68*S),cap=True,mood="happy",pose="run"); motion(c,int(W*0.36),int(H*0.45),5,170)
    d=ImageDraw.Draw(c); d.text((W*0.5,H*0.12),"ZOOM!",font=fnt("YouTubeSans-Black.otf",80),fill=DREAM,anchor="mm",stroke_width=6*S,stroke_fill=BLK); panel_border(c); out.append(("속도선 + 효과음","",c))
    e=halftone_bg(W,H,(60,46,92),(96,78,140)); toon(e,W*0.5,int(H*0.95),int(70*S),cap=True,mood="sleepy",pose="stand")
    d=ImageDraw.Draw(e)
    for i,(x,y,s) in enumerate([(0.68,0.26,40),(0.76,0.17,56),(0.86,0.07,74)]): d.text((W*x,H*y),"Z",font=fnt("YouTubeSans-Black.otf",s),fill=WHITE,anchor="mm",stroke_width=4*S,stroke_fill=BLK)
    for k in range(6):
        sx,sy=random.uniform(0.1,0.4)*W,random.uniform(0.08,0.4)*H; R=random.uniform(8,16)*S
        d.polygon([(sx,sy-R),(sx+R*0.3,sy-R*0.3),(sx+R,sy),(sx+R*0.3,sy+R*0.3),(sx,sy+R),(sx-R*0.3,sy+R*0.3),(sx-R,sy),(sx-R*0.3,sy-R*0.3)],fill=DREAM,outline=BLK)
    panel_border(e); out.append(("꿈나라 Zzz","",e))
    return out
def thumb(cap):
    W,H=1280*S,720*S; im=Image.new("RGB",(W,H),(255,255,255)); speedlines(im,W*0.3,H*0.45,110,0.12,col=(255,214,110))
    toon(im,int(W*0.3),int(H*1.05),int(118*S),cap=cap,mood="shock",pose="shock")
    d=ImageDraw.Draw(im)
    d.text((W*0.72,H*0.36),"10x",font=fnt("YouTubeSans-Black.otf",200),fill=DREAM,anchor="mm",stroke_width=10*S,stroke_fill=BLK)
    d.text((W*0.72,H*0.64),"FASTER?",font=fnt("YouTubeSans-Black.otf",110),fill=(255,80,80),anchor="mm",stroke_width=8*S,stroke_fill=BLK)
    panel_border(im,8); return im

A=hero(False); B=hero(True); fx=fx_panels(); TA=thumb(False); TB=thumb(True)
# sheet
W=1920; sheet=Image.new("RGB",(W,2330),(24,20,34)); d=ImageDraw.Draw(sheet)
d.text((W//2,50),"IF TOON 캐릭터 · 만화 이펙트 시안",font=ImageFont.truetype(F+"Pretendard-Black.otf",52),fill=(255,205,60),anchor="mm")
a=A.resize((900,1100),Image.LANCZOS); b=B.resize((900,1100),Image.LANCZOS)
sheet.paste(a,(40,100)); sheet.paste(b,(980,100))
lf=ImageFont.truetype(F+"Pretendard-ExtraBold.otf",40)
d.text((490,1235),"A. 기본",font=lf,fill="white",anchor="mm"); d.text((1430,1235),"B. 나이트캡",font=lf,fill="white",anchor="mm")
for i,(t,_,p) in enumerate(fx):
    x=40+i*470; sheet.paste(p.resize((430,430),Image.LANCZOS),(x,1280)); d.text((x+215,1740),t,font=ImageFont.truetype(F+"Pretendard-ExtraBold.otf",32),fill="white",anchor="mm")
ta=TA.resize((900,506),Image.LANCZOS); tb=TB.resize((900,506),Image.LANCZOS); sheet.paste(ta,(40,1790)); sheet.paste(tb,(980,1790))
sheet.save("iftoon_sheet_v1.jpg",quality=90); sheet.resize((960,1165)).save("pv.jpg")
A.resize((900,1100)).save("hero_A.png"); B.resize((900,1100)).save("hero_B.png"); TA.resize((1280,720)).save("thumb_A.png"); TB.resize((1280,720)).save("thumb_B.png")
