import sys; sys.path.insert(0,'/home/user/YTP1/concepts/i444/ep_backrooms')
from gfx_br import f
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
SD='/tmp/claude-0/-home-user-YTP1/bb3b993e-7de0-5d78-af5e-c29db5ac82a5/scratchpad/tmdb_br/orig/'
W,H=1280,720; PW=[427,426,427]; COL=[(70,215,95),(250,200,40),(235,30,38)]
def panel(fn,cx,cy,chf,pw,b=1.05):
    im=Image.open(SD+fn).convert('RGB'); sw,sh=im.size; ch=chf*sh; cw=ch*pw/H
    x0=min(max(0,cx*sw-cw/2),sw-cw); y0=min(max(0,cy*sh-ch*0.4),sh-ch)
    p=im.crop((int(x0),int(y0),int(x0+cw),int(y0+ch))).resize((pw,H),Image.LANCZOS)
    p=ImageEnhance.Brightness(p).enhance(b); p=ImageEnhance.Contrast(p).enhance(1.12)
    g=Image.new('L',(pw,H),0); d=ImageDraw.Draw(g)
    for y in range(H//2,H): d.line([(0,y),(pw,y)],fill=int(235*((y-H/2)/(H/2))**1.2))
    return Image.composite(Image.new('RGB',(pw,H)),p,g)
def build(specs,out):
    im=Image.new('RGB',(W,H)); x=0
    for (fn,cx,cy,chf,b,pct),pw,c in zip(specs,PW,COL):
        p=panel(fn,cx,cy,chf,pw,b).convert('RGBA'); sh=Image.new('RGBA',(pw,H),(0,0,0,0)); d=ImageDraw.Draw(sh)
        d.text((pw/2+5,H-115+8),pct,font=f(182),fill=(0,0,0,220),anchor='mm',stroke_width=14,stroke_fill=(0,0,0,220))
        p.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)))
        ImageDraw.Draw(p).text((pw/2,H-115),pct,font=f(182),fill=c,anchor='mm',stroke_width=8,stroke_fill=(0,0,0))
        im.paste(p.convert('RGB'),(x,0)); x+=pw
    d=ImageDraw.Draw(im); d.rectangle((426,0,429,H),fill=0); d.rectangle((852,0,855,H),fill=0)
    im.save(out,quality=93)
build([('s24.jpg',0.51,0.50,0.95,1.15,'90%'),('s0.jpg',0.47,0.43,0.62,1.0,'15%'),('bd103.jpg',0.54,0.36,0.95,1.15,'2%')],'backrooms_thumb_p1.jpg')
build([('s5.jpg',0.56,0.70,0.80,1.15,'90%'),('s7.jpg',0.84,0.34,0.70,1.05,'40%'),('bd103.jpg',0.54,0.36,0.95,1.15,'2%')],'backrooms_thumb_p2.jpg')
s=Image.new('RGB',(1280,380),(20,20,20))
for i,n in enumerate(['p1','p2']): s.paste(Image.open(f'backrooms_thumb_{n}.jpg').resize((560,315)),(i*580,0))
for i,n in enumerate(['p1','p2']): s.paste(Image.open(f'backrooms_thumb_{n}.jpg').resize((168,94)),(1160-i*0,10+i*110) if False else (1100,10+i*110))
s.save('psheet.jpg')
