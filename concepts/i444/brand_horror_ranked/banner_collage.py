from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import glob, sys
sys.path.insert(0,'hr'); 
H='collage/hi/'; FN='hr/fonts/Anton.ttf'
def src(p): return Image.open(glob.glob(H+p+'*')[0]).convert('RGB')
def tile(p,w,h,fx,fy,z=1.0):
    im=src(p); W,Hh=im.size; s=max(w/W,h/Hh)*z; im=im.resize((int(W*s),int(Hh*s)),Image.LANCZOS)
    x=min(max(int(fx*im.width-w/2),0),im.width-w); y=min(max(int(fy*im.height-h/2),0),im.height-h)
    t=im.crop((x,y,x+w,y+h)); t=ImageEnhance.Color(t).enhance(0.8); return ImageEnhance.Brightness(t).enhance(0.85)
W,HH=2560,1440; B=Image.new('RGB',(W,HH),(10,10,12)); g=6
rows=[(0,480,[('10585_5cP',.6,.4,1.3),('9003_bxm',.5,.35,1.3),('30497',.72,.45,1.4),('176',.45,.4,1.2),('565_cAk3',.55,.5,1.3)]),
      (480,480,None),
      (960,480,[('9552',.62,.55,1.3),('10225_hNzp',.55,.4,1.3),('377_f5yD',.6,.45,1.4),('4232_vh7n',.5,.4,1.6),('346364_7gg3',.42,.45,1.4)])]
for y,h,items in rows:
    if items:
        w=W//5
        for i,(p,fx,fy,z) in enumerate(items): B.paste(tile(p,w-g,h-g,fx,fy,z),(i*w+g//2,y+g//2))
# middle row: 2 villains | centre | 2 villains
mid=[(0,427,('10225_qdQ',.33,.35,1.5)),(427,426,('948',.42,.38,1.5)),(1707,426,('346364_aliC',.72,.38,1.5)),(2133,427,('377_x2Um',.38,.45,1.5))]
for x,w,(p,fx,fy,z) in mid: B.paste(tile(p,w-g,480-g,fx,fy,z),(x+g//2,480+g//2))
# darken top/bottom rows a little more (TV-only area), and the centre zone
dark=Image.new('L',(W,HH),0); d=ImageDraw.Draw(dark)
d.rectangle([0,0,W,480],fill=90); d.rectangle([0,960,W,HH],fill=90)
B=Image.composite(Image.new('RGB',(W,HH),(10,10,12)),B,dark)
# centre glow-free black panel with soft edge
m=Image.new('L',(W,HH),0); ImageDraw.Draw(m).rectangle([860,300,1700,1140],fill=255); m=m.filter(ImageFilter.GaussianBlur(70))
B=Image.composite(Image.new('RGB',(W,HH),(10,10,12)),B,m)
d=ImageDraw.Draw(B); f=ImageFont.truetype(FN,190)
t='HORROR RANKED'; b=d.textbbox((0,0),t,font=f); x=(W-(b[2]-b[0]))//2-b[0]; y=640-b[1]
sh=Image.new('L',(W,HH),0); ImageDraw.Draw(sh).text((x,y+6),t,font=f,fill=255); sh=sh.filter(ImageFilter.GaussianBlur(18))
B=Image.composite(Image.new('RGB',(W,HH),(0,0,0)),B,sh); d=ImageDraw.Draw(B)
d.text((x,y),t,font=f,fill=(240,236,228))
bb=d.textbbox((x,y),t,font=f); ly=bb[3]+26
d.rectangle([bb[0],ly,bb[2],ly+12],fill=(190,0,18))
import random; R=random.Random(11); xx=bb[0]+8
while xx<bb[2]-20:
    w=R.uniform(8,16); L=R.uniform(8,48)
    if R.random()<.5: d.rectangle([xx,ly+10,xx+w,ly+10+L],fill=(190,0,18)); d.ellipse([xx-2,ly+10+L-w*.6,xx+w+2,ly+10+L+w*.6],fill=(190,0,18))
    xx+=w+R.uniform(6,28)
B.save('collage/banner_horror_ranked_collage.png')
C=B.copy(); ImageDraw.Draw(C).rectangle([507,508,2053,931],outline=(0,255,0),width=3); C.resize((1280,720)).save('collage/check.png')
