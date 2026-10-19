from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math
S=4
F="/home/user/YTP1/germany_shorts/fonts/"
DREAM=(255,196,61)      # 꿈색 #FFC43D
DREAM_D=(236,160,40)
INK=(43,30,58)
WHITE=(255,252,245)
def fnt(n,s): return ImageFont.truetype(F+n,int(s*S))

def tile_bg(w,h,seed=0):
    im=Image.new("RGB",(w*S,h*S)); d=ImageDraw.Draw(im)
    top=(34,28,62); bot=(86,62,104)
    for y in range(h*S):
        t=y/(h*S); d.line([(0,y),(w*S,y)],fill=tuple(int(top[i]+(bot[i]-top[i])*t) for i in range(3)))
    # soft glow behind character
    g=Image.new("L",im.size,0); gd=ImageDraw.Draw(g)
    cx,cy=w*S//2,int(h*S*0.48)
    for r in range(int(w*S*0.42),0,-6*S): gd.ellipse([cx-r,cy-r,cx+r,cy+r],fill=int(120*(1-r/(w*S*0.42))**1.5))
    im=Image.composite(Image.new("RGB",im.size,(255,190,90)),im,g.point(lambda v:int(v*0.45)))
    return im

def limb(d,a,b,w,col=DREAM):
    d.line([a,b],fill=col,width=w); r=w//2
    for p in (a,b): d.ellipse([p[0]-r,p[1]-r,p[0]+r,p[1]+r],fill=col)

def eyes(d,cx,cy,r,kind="round",col=INK):
    ex=r*0.34
    for sx in (-1,1):
        x=cx+sx*ex
        if kind=="round":
            d.ellipse([x-r*0.13,cy-r*0.17,x+r*0.13,cy+r*0.17],fill=col)
        elif kind=="sleepy":
            d.chord([x-r*0.16,cy-r*0.16,x+r*0.16,cy+r*0.16],start=0,end=180,fill=col)
        elif kind=="closed":
            d.arc([x-r*0.15,cy-r*0.12,x+r*0.15,cy+r*0.14],start=200,end=340,fill=col,width=int(r*0.07))
        elif kind=="wide":
            d.ellipse([x-r*0.17,cy-r*0.2,x+r*0.17,cy+r*0.2],fill=col)
            d.ellipse([x-r*0.06+r*0.04,cy-r*0.12,x+r*0.06+r*0.04,cy-r*0.0],fill=WHITE if col==INK else INK)

def mouth(d,cx,cy,r,kind="smile",col=INK):
    if kind=="smile": d.arc([cx-r*0.24,cy-r*0.12,cx+r*0.24,cy+r*0.22],start=15,end=165,fill=col,width=int(r*0.075))
    elif kind=="o": d.ellipse([cx-r*0.08,cy,cx+r*0.08,cy+r*0.16],fill=col)
    elif kind=="grin": d.chord([cx-r*0.24,cy-r*0.1,cx+r*0.24,cy+r*0.26],start=0,end=180,fill=col)

def stick_body(d,cx,hy,r,col=DREAM,shirt=None,pose="stand"):
    s=r/80
    neck=hy+r*0.95
    hip=neck+130*s
    tw=int(16*s)
    if shirt:
        d.rounded_rectangle([cx-38*s,neck-6*s,cx+38*s,hip+10*s],radius=int(30*s),fill=shirt)
    else:
        limb(d,(cx,neck),(cx,hip),int(20*s),col)
    if pose=="wave":
        limb(d,(cx-30*s,neck+20*s),(cx-70*s,neck+95*s),tw,col)
        limb(d,(cx+30*s,neck+20*s),(cx+85*s,neck-50*s),tw,col)
    else:
        limb(d,(cx-30*s,neck+20*s),(cx-60*s,neck+110*s),tw,col)
        limb(d,(cx+30*s,neck+20*s),(cx+60*s,neck+110*s),tw,col)
    limb(d,(cx-16*s,hip),(cx-26*s,hip+125*s),tw,col)
    limb(d,(cx+16*s,hip),(cx+26*s,hip+125*s),tw,col)

def head(d,cx,cy,r,col=DREAM): d.ellipse([cx-r,cy-r,cx+r,cy+r],fill=col)

def cloud(d,cx,cy,r,col):
    for dx,dy,rr in [(-0.55,0.15,0.55),(0.55,0.15,0.55),(0,-0.2,0.7),(-0.25,0.35,0.5),(0.25,0.35,0.5)]:
        d.ellipse([cx+dx*r-rr*r,cy+dy*r-rr*r,cx+dx*r+rr*r,cy+dy*r+rr*r],fill=col)

# ---- designs ----
def d1(im,cx,cy):  # Sunny: pure dream stickman
    d=ImageDraw.Draw(im); r=80*S; stick_body(d,cx,cy,r); head(d,cx,cy,r)
    eyes(d,cx,cy-r*0.02,r,"round"); mouth(d,cx,cy+r*0.22,r)
def d2(im,cx,cy):  # Nightcap
    d=ImageDraw.Draw(im); r=80*S; stick_body(d,cx,cy,r); head(d,cx,cy,r)
    cap=(108,124,232)
    d.polygon([(cx-r*1.02,cy-r*0.25),(cx+r*1.0,cy-r*0.35),(cx+r*1.45,cy+r*0.15)],fill=cap)
    d.pieslice([cx-r*1.02,cy-r*1.05,cx+r*1.0,cy+r*0.45],start=180,end=360,fill=cap)
    d.polygon([(cx-r*0.2,cy-r*1.0),(cx+r*0.95,cy-r*0.4),(cx+r*1.5,cy+r*0.3),(cx+r*1.25,cy+r*0.35),(cx+r*0.6,cy-r*0.3)],fill=cap)
    d.rounded_rectangle([cx-r*1.05,cy-r*0.38,cx+r*1.05,cy-r*0.18],radius=int(r*0.1),fill=WHITE)
    d.ellipse([cx+r*1.25,cy+r*0.2,cx+r*1.6,cy+r*0.55],fill=WHITE)
    eyes(d,cx,cy+r*0.12,r,"sleepy"); mouth(d,cx,cy+r*0.42,r)
def d3(im,cx,cy):  # Cloud head
    d=ImageDraw.Draw(im); r=78*S; stick_body(d,cx,cy+r*0.1,r); cloud(d,cx,cy,r*1.05,DREAM)
    eyes(d,cx,cy+r*0.1,r,"round"); mouth(d,cx,cy+r*0.35,r)
def d4(im,cx,cy):  # Dream bubble halo: little cloud floating above
    d=ImageDraw.Draw(im); r=80*S; stick_body(d,cx,cy,r); head(d,cx,cy,r)
    cloud(d,cx+r*0.55,cy-r*1.55,r*0.42,WHITE)
    for i,(dx,dy,rr) in enumerate([(0.32,-1.08,0.09),(0.18,-0.92,0.06)]):
        d.ellipse([cx+dx*r-rr*r,cy+dy*r-rr*r,cx+dx*r+rr*r,cy+dy*r+rr*r],fill=WHITE)
    eyes(d,cx,cy,r,"closed"); mouth(d,cx,cy+r*0.25,r,"smile")
def d5(im,cx,cy):  # White eyes + white mouth on dream body with dark outline (Ifverse-like inversion)
    d=ImageDraw.Draw(im); r=80*S
    stick_body(d,cx,cy,r,col=DREAM)
    d.ellipse([cx-r-6*S,cy-r-6*S,cx+r+6*S,cy+r+6*S],fill=INK); head(d,cx,cy,r)
    # big white eye shapes with dark pupils
    for sx in (-1,1):
        x=cx+sx*r*0.33
        d.ellipse([x-r*0.22,cy-r*0.28,x+r*0.22,cy+r*0.16],fill=WHITE)
        d.ellipse([x-r*0.09+sx*r*0.03,cy-r*0.12,x+r*0.09+sx*r*0.03,cy+r*0.06],fill=INK)
    d.chord([cx-r*0.28,cy+r*0.15,cx+r*0.28,cy+r*0.55],start=0,end=180,fill=WHITE)
def d6(im,cx,cy):  # Star hoodie (sleepy onesie with star tip)
    d=ImageDraw.Draw(im); r=80*S; hood=(255,248,232)
    stick_body(d,cx,cy,r,col=DREAM,shirt=hood)
    d.ellipse([cx-r*1.18,cy-r*1.15,cx+r*1.18,cy+r*1.1],fill=hood)
    # star on hood tip
    pts=[]; sx,sy,R=cx+r*0.95,cy-r*1.05,r*0.32
    for k in range(10):
        a=-math.pi/2+k*math.pi/5; rr=R if k%2==0 else R*0.45; pts.append((sx+rr*math.cos(a),sy+rr*math.sin(a)))
    d.polygon(pts,fill=DREAM)
    head(d,cx,cy+r*0.05,r*0.86)
    eyes(d,cx,cy+r*0.05,r*0.86,"round"); mouth(d,cx,cy+r*0.28,r*0.86)
def d7(im,cx,cy):  # Bean/pillow body, no limbs above, tiny legs
    d=ImageDraw.Draw(im); r=80*S
    limb(d,(cx-28*S,cy+180*S),(cx-30*S,cy+250*S),int(16*S)); limb(d,(cx+28*S,cy+180*S),(cx+30*S,cy+250*S),int(16*S))
    d.rounded_rectangle([cx-r*1.1,cy-r*1.1,cx+r*1.1,cy+r*2.4],radius=int(r*1.1),fill=DREAM)
    limb(d,(cx-r*1.05,cy+r*0.9),(cx-r*1.5,cy+r*1.5),int(16*S)); limb(d,(cx+r*1.05,cy+r*0.9),(cx+r*1.5,cy+r*1.5),int(16*S))
    eyes(d,cx,cy,r,"sleepy"); mouth(d,cx,cy+r*0.3,r,"o")
    # Zz
    d.text((cx+r*1.1,cy-r*1.4),"z",font=fnt("YouTubeSans-Black.otf",34),fill=WHITE,anchor="mm")
    d.text((cx+r*1.45,cy-r*1.8),"Z",font=fnt("YouTubeSans-Black.otf",50),fill=WHITE,anchor="mm")
def d8(im,cx,cy):  # Sprout/petal: spring flower cowlick
    d=ImageDraw.Draw(im); r=80*S; stick_body(d,cx,cy,r); head(d,cx,cy,r)
    # little flower on top
    fx,fy=cx+r*0.15,cy-r*1.25
    d.line([(cx+r*0.05,cy-r*0.92),(fx,fy)],fill=(120,190,90),width=int(10*S))
    for k in range(5):
        a=k*2*math.pi/5; px,py=fx+r*0.22*math.cos(a),fy+r*0.22*math.sin(a)
        d.ellipse([px-r*0.17,py-r*0.17,px+r*0.17,py+r*0.17],fill=WHITE)
    d.ellipse([fx-r*0.13,fy-r*0.13,fx+r*0.13,fy+r*0.13],fill=(255,150,60))
    eyes(d,cx,cy,r,"wide"); mouth(d,cx,cy+r*0.28,r,"smile")

designs=[("1","SUNNY","꿈색 막대인간, 군더더기 0",d1),("2","NIGHTCAP","잠옷 모자, 졸린 눈",d2),
         ("3","CLOUDY","구름 모양 머리",d3),("4","BUBBLE","머리 위 꿈 구름",d4),
         ("5","BIG EYES","흰 눈·흰 입 (Ifverse식)",d5),("6","STAR HOOD","별 달린 흰 후드",d6),
         ("7","PILLOW","베개 모양 몸통 + Zz",d7),("8","BLOOM","머리에 봄꽃 한 송이",d8)]
TW,TH=480,600
sheet=Image.new("RGB",(TW*4*S,(TH*2+90)*S),(20,16,34))
kf=ImageFont.truetype(F+"Pretendard-ExtraBold.otf",int(22*S))
for i,(n,name,desc,fn) in enumerate(designs):
    t=tile_bg(TW,TH); fn(t,TW*S//2,int(TH*S*0.33))
    d=ImageDraw.Draw(t)
    d.text((TW*S//2,int(TH*0.88*S)),f"{n}. {name}",font=fnt("YouTubeSans-Black.otf",40),fill=WHITE,anchor="mm",stroke_width=3*S,stroke_fill=INK)
    d.text((TW*S//2,int(TH*0.95*S)),desc,font=kf,fill=DREAM,anchor="mm")
    sheet.paste(t,((i%4)*TW*S,(i//4)*TH*S))
d=ImageDraw.Draw(sheet)
d.text((TW*2*S,(TH*2+45)*S),"DAYDREAMER 마스코트 시안  ·  꿈색 #FFC43D",font=ImageFont.truetype(F+"Pretendard-ExtraBold.otf",int(36*S)),fill=DREAM,anchor="mm")
sheet=sheet.resize((TW*4,TH*2+90),Image.LANCZOS); sheet.save("mascots_sheet.jpg",quality=92)

# thumbnail-size test: each mascot in a 1280x720 thumb, shown at 246x138 (mobile suggested size)
strip=Image.new("RGB",(4*262+16,2*156+16),(15,15,15))
for i,(n,name,desc,fn) in enumerate(designs):
    t=tile_bg(1280,720); fn(t,int(1280*0.28*S),int(720*0.30*S))
    d=ImageDraw.Draw(t)
    d.text((int(1280*0.70*S),int(720*0.40*S)),"10x",font=fnt("YouTubeSans-Black.otf",200),fill=DREAM,anchor="mm",stroke_width=9*S,stroke_fill=INK)
    d.text((int(1280*0.70*S),int(720*0.66*S)),"FASTER?",font=fnt("YouTubeSans-Black.otf",104),fill=WHITE,anchor="mm",stroke_width=7*S,stroke_fill=INK)
    d.text((int(60*S),int(60*S)),n,font=fnt("YouTubeSans-Black.otf",70),fill=WHITE,anchor="mm")
    t=t.resize((246,138),Image.LANCZOS)
    strip.paste(t,(16+(i%4)*262,16+(i//4)*156))
strip.save("thumb_size_test.jpg",quality=92)
