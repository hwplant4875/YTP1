import sys
sys.path.insert(0,'/home/user/YTP1/concepts/i444/ep_backrooms')
from gfx_br import f
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
SD='/tmp/claude-0/-home-user-YTP1/bb3b993e-7de0-5d78-af5e-c29db5ac82a5/scratchpad/tmdb_br/orig/'; OD='/tmp/claude-0/-home-user-YTP1/bb3b993e-7de0-5d78-af5e-c29db5ac82a5/scratchpad/thumbs2/'
W,H=1280,720; RED=(235,30,38); WH=(255,255,255); YEL=(255,214,0)
def crop(n,cx,cy,zoom):
    im=Image.open(SD+f's{n}.jpg').convert('RGB'); sw,sh=im.size; cw=min(sw,sh*16/9)/zoom; ch=cw*9/16
    x0=min(max(0,cx*sw-cw/2),sw-cw); y0=min(max(0,cy*sh-ch/2),sh-ch)
    im=im.crop((int(x0),int(y0),int(x0+cw),int(y0+ch))).resize((W,H),Image.LANCZOS)
    return ImageEnhance.Contrast(im).enhance(1.06)
def fit(t,sz,mx):
    while f(sz).getlength(t)>mx: sz-=4
    return sz
def lines(im, items, stroke=14):
    """items: list of (text, size, colour, (x,y), anchor) or segments [(txt,col),...]"""
    im=im.convert('RGBA'); sh=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(sh)
    def segs(it):
        t,sz,col,(x,y),anc=it
        if isinstance(t,str): return [(t,col,x,y,anc,sz)]
        tot=sum(f(sz).getlength(s) for s,_ in t); xx=x-tot/2 if anc[0]=='m' else x; out=[]
        for s,c in t: out.append((s,c,xx,y,'l'+anc[1],sz)); xx+=f(sz).getlength(s)
        return out
    allsegs=[s for it in items for s in segs(it)]
    for s,c,x,y,a,sz in allsegs: d.text((x+6,y+10),s,font=f(sz),fill=(0,0,0,200),anchor=a,stroke_width=stroke+6,stroke_fill=(0,0,0,200))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10))); d=ImageDraw.Draw(im)
    for s,c,x,y,a,sz in allsegs: d.text((x,y),s,font=f(sz),fill=c,anchor=a,stroke_width=stroke,stroke_fill=(0,0,0))
    return im.convert('RGB')
# J: Mary's terrified face left, COULD YOU / SURVIVE? right
j=crop(0,0.66,0.45,1.35)
j=lines(j,[('COULD YOU',fit('COULD YOU',150,560),WH,(965,270),'mm'),('SURVIVE?',fit('SURVIVE?',170,580),YEL,(965,430),'mm')])
j.save(OD+'backrooms_thumb_j.jpg',quality=93)
# K: Captain-era Clark grinning (s24) left, ONLY 1 / GOT OUT right
k=crop(24,0.60,0.5,1.25)
k=lines(k,[([('ONLY ',WH),('1',RED)],fit('ONLY 1',170,560),None,(965,270),'mm'),('GOT OUT',fit('GOT OUT',160,580),WH,(965,430),'mm')])
k.save(OD+'backrooms_thumb_k.jpg',quality=93)
# L: the endless empty yellow room, giant 2% + SURVIVE
l=crop(14,0.5,0.55,1.0)
l=lines(l,[('2%',330,RED,(640,330),'mm'),('SURVIVE',150,WH,(640,560),'mm')],stroke=16)
l.save(OD+'backrooms_thumb_l.jpg',quality=93)
sheet=Image.new('RGB',(W+W//2+20, H),(30,30,30))
for i,n in enumerate('jkl'):
    t=Image.open(OD+f'backrooms_thumb_{n}.jpg')
    if i==0: sheet.paste(t,(0,0))
