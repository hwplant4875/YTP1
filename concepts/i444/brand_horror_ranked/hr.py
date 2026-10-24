from PIL import Image, ImageDraw, ImageFont
import math, sys
S=4; F='fonts/'
BLK=(10,10,12); RED=(190,0,18); WHT=(240,236,228)
def font(n,s): return ImageFont.truetype(F+n,s)
def tomb(d,x,y,w,h,col):
    r=w/2; d.rectangle([x-r,y-h+r,x+r,y],fill=col); d.pieslice([x-r,y-h,x+r,y-h+2*r],180,360,fill=col)
def drips(d,x0,x1,y,col,seed,scale=1.0):
    import random; R=random.Random(seed); x=x0
    while x<x1:
        w=R.uniform(10,22)*scale; L=R.uniform(10,70)*scale
        if R.random()<0.55:
            d.rectangle([x,y-2,x+w,y+L],fill=col); d.ellipse([x-w*0.15,y+L-w*0.6,x+w*1.15,y+L+w*0.6],fill=col)
        x+=w+R.uniform(4,20)*scale
def ctext(d,cx,cy,t,f,col): b=d.textbbox((0,0),t,font=f); d.text((cx-(b[0]+b[2])/2,cy-(b[1]+b[3])/2),t,font=f,fill=col)
def pfp(kind,bg,fg,acc):
    N=800*S; im=Image.new('RGB',(N,N),bg); d=ImageDraw.Draw(im)
    if kind=='tombs':
        base=600*S; ws=170*S
        for x,h,n,c in [(215,300,'2',fg),(585,260,'3',fg),(400,420,'1',acc)]:
            tomb(d,x*S,base,ws,h*S,c); ctext(d,x*S,base-h*S*0.52,n,font('Anton.ttf',int((150 if n=='1' else 110)*S)),bg)
        d.rectangle([90*S,base,710*S,base+26*S],fill=fg)
        drips(d,330*S,470*S,base-420*S+70*S,acc,3,S*0.6) if False else None
    elif kind=='one':
        f=font('Anton.ttf',470*S); ctext(d,400*S,410*S,'1',f,fg)
        b=d.textbbox((0,0),'1',font=f); bw=b[2]-b[0]; bh=b[3]-b[1]
        px=im.load(); ys=[y for y in range(0,N,S) if any(px[x,y]==fg for x in range(0,N,S))]; y1=max(ys)
        xs=[x for x in range(N) if px[x,y1-S]==fg]
        drips(d,min(xs)+2*S,max(xs)-6*S,y1-2*S,fg,4,S*1.0)
        ctext(d,400*S,110*S,'HORROR RANKED',font('Anton.ttf',60*S),acc)
    elif kind=='hr':
        f=font('Anton.ttf',430*S); ctext(d,400*S,370*S,'HR',f,fg)
        d.rectangle([150*S,560*S,650*S,590*S],fill=acc); drips(d,160*S,640*S,585*S,acc,9,S*1.3)
    im=im.resize((800,800),Image.LANCZOS); return im
def previews(im):
    pv=Image.new('RGB',(560,200),(255,255,255)); x=10
    for sz in (176,88,40):
        m=Image.new('L',(sz*4,sz*4),0); ImageDraw.Draw(m).ellipse([0,0,sz*4-1,sz*4-1],fill=255); m=m.resize((sz,sz),Image.LANCZOS)
        pv.paste(im.resize((sz,sz),Image.LANCZOS),(x,100-sz//2),m); x+=sz+30
    return pv
opts=[('hr_A_tombstones',pfp('tombs',BLK,WHT,RED)),('hr_B_bloody_one',pfp('one',BLK,RED,WHT)),('hr_C_monogram',pfp('hr',BLK,WHT,RED))]
G=Image.new('RGB',(1220,1000),'white')
for i,(n,im) in enumerate(opts): im.save(f'out/{n}.png'); G.paste(im.resize((400,400)),(i*410,0)); G.paste(previews(im),(0,400+i*200))
G.save('out/hr_options.png')
# banner 2560x1440, safe 1546x423 centred
B=Image.new('RGB',(2560*2,1440*2),BLK); d=ImageDraw.Draw(B); s=2
cx,cy=1280*s,720*s
ctext(d,cx,cy-40*s,'HORROR RANKED',font('Anton.ttf',190*s),WHT)
d.rectangle([cx-640*s,cy+75*s,cx+640*s,cy+88*s],fill=RED); drips(d,cx-630*s,cx+630*s,cy+86*s,RED,11,s*0.9)
ctext(d,cx,cy+215*s,'EVERY HORROR VILLAIN, RANKED BY HOW HARD THEY ARE TO SURVIVE',font('Anton.ttf',40*s),(170,165,160))
for x,h,c in [(cx-1000*s,260,WHT),(cx+1000*s,220,WHT)]: pass
B=B.resize((2560,1440),Image.LANCZOS); B.save('out/banner_horror_ranked.png')
