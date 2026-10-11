from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps
MF="/tmp/claude-0/strata/Montserrat-VF.ttf"
def F(size,w=800):
    f=ImageFont.truetype(MF,size); f.set_variation_by_axes([w]); return f
AMBER=(255,170,80); CREAM=(240,236,228)
def track(d,xy,s,f,fill,sp,anchor="mm"):
    ws=[d.textlength(c,font=f) for c in s]; tot=sum(ws)+sp*(len(s)-1)
    x=xy[0]-tot/2 if anchor=="mm" else xy[0]
    for c,w in zip(s,ws):
        d.text((x,xy[1]),c,font=f,fill=fill,anchor="lm"); x+=w+sp
    return tot
def mark(size):
    """core-sample mark: circle cut into strata bands, one glowing amber layer"""
    S=size*4; im=Image.new("RGBA",(S,S),(0,0,0,0)); d=ImageDraw.Draw(im)
    bands=[(0.00,0.30,(58,58,62)),(0.30,0.47,(44,44,48)),(0.47,0.545,AMBER),(0.545,0.70,(30,30,34)),(0.70,1.0,(20,20,23))]
    for a,b,c in bands: d.rectangle([0,int(a*S),S,int(b*S)],fill=c+(255,))
    # thin separators
    for a,b,c in bands: d.line([0,int(a*S),S,int(a*S)],fill=(10,10,12,255),width=S//160)
    m=Image.new("L",(S,S),0); ImageDraw.Draw(m).ellipse([0,0,S-1,S-1],fill=255)
    im.putalpha(m)
    return im.resize((size,size),Image.LANCZOS)
# profile 800x800
P=800; pr=Image.new("RGB",(P,P),(8,8,10))
g=Image.new("RGBA",(P,P),(0,0,0,0)); gd=ImageDraw.Draw(g)
gd.rectangle([150,int(150+0.47*500),650,int(150+0.545*500)],fill=AMBER+(160,)); g=g.filter(ImageFilter.GaussianBlur(40))
pr.paste(g,(0,0),g)
mk=mark(500); pr.paste(mk,(150,150),mk)
pr.save("profile_strata.png")
# profile variant with wordmark below mark
pr2=Image.new("RGB",(P,P),(8,8,10)); m2=mark(380); pr2.paste(g.resize((P,P)),(0,-60),g); pr2.paste(m2,(210,150),m2)
d=ImageDraw.Draw(pr2); track(d,(400,640),"STRATA",F(92,800),CREAM,14)
pr2.save("profile_strata_word.png")
# banner 2560x1440
bg=Image.open("cs_stack_0.5.png").convert("RGB")
bg=bg.resize((2880,1620),Image.LANCZOS).crop((160,60,160+2560,60+1440))
bg=ImageEnhance.Brightness(bg).enhance(0.75)
B=bg.copy(); ov=Image.new("RGBA",B.size,(0,0,0,0)); od=ImageDraw.Draw(ov)
od.rectangle([0,500,2560,940],fill=(0,0,0,150)); ov=ov.filter(ImageFilter.GaussianBlur(60)); B.paste(ov,(0,0),ov)
d=ImageDraw.Draw(B)
mk=mark(210); B.paste(mk,(1280-560,615),mk)
f=F(170,800); tw=track(d,(1280+130,720),"STRATA",f,CREAM,26)
track(d,(1280,880),"THE HIDDEN WORLD, CUT OPEN IN 3D",F(44,600),AMBER,10)
B.save("banner_strata_2560x1440.jpg",quality=92)
# safe-area preview (TV/desktop/mobile guides)
pv=B.resize((1280,720)); pd=ImageDraw.Draw(pv); pd.rectangle([(1280-773)//2,(720-212)//2,(1280+773)//2,(720+212)//2],outline=(0,255,0),width=2)
pv.save("banner_preview.jpg")
