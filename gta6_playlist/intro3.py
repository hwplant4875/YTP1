import sys, glob, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
sys.path.insert(0,'/tmp/gta/st')
W,H=1920,1080; FPS=30
F='/tmp/gta/fonts/'; S='/tmp/gta/img/'
def G(p): return sorted(glob.glob(S+p+'*'))[0]
def ease(t): t=max(0,min(1,t)); return t*t*(3-2*t)
def disc_img(size):
    im=Image.open('/tmp/gta/st/disc_x4.png').convert('RGB'); cx,cy,r=912,910,846
    im=im.crop((cx-r,cy-r,cx+r,cy+r)).resize((size*2,size*2),Image.LANCZOS)
    return im
def build(bgpath,title,artist,glow,blur=7,dsize=600):
    bg=Image.open(bgpath).convert('RGB'); w,h=bg.size; s=max(W/w,H/h)*1.06
    bg=bg.resize((int(w*s),int(h*s)),Image.LANCZOS); x=(bg.width-W)//2; y=(bg.height-H)//2
    bg=bg.crop((x,y,x+W,y+H)).filter(ImageFilter.GaussianBlur(blur)); bg=Image.eval(bg,lambda v:int(v*0.80))
    yy,xx=np.mgrid[0:H,0:W]; d=np.sqrt(((xx-W/2)/(W/2))**2+((yy-H/2)/(H/2))**2)
    v=np.clip(1-0.38*np.clip(d-0.55,0,1)/0.85,0,1)[...,None]
    bg=Image.fromarray((np.asarray(bg)*v).astype('uint8'))
    cx,cy=W//2,H//2
    base=Image.new('L',(W,H),0); ImageDraw.Draw(base).ellipse((cx-dsize//2,cy-dsize//2,cx+dsize//2,cy+dsize//2),fill=255)
    stroke=base.filter(ImageFilter.MaxFilter(15)).filter(ImageFilter.GaussianBlur(1))
    def lay(mask,col,k):
        return Image.composite(Image.new('RGB',(W,H),col),Image.new('RGB',(W,H),0),mask.point(lambda p:int(min(255,p*k))))
    g=ImageChops.screen(ImageChops.screen(lay(stroke.filter(ImageFilter.GaussianBlur(70)),glow,1.5),lay(stroke.filter(ImageFilter.GaussianBlur(22)),glow,1.3)),lay(stroke.filter(ImageFilter.GaussianBlur(7)),(255,255,255),0.9))
    fg=ImageChops.screen(bg,g); fg.paste((255,255,255),mask=stroke)
    D=disc_img(dsize)  # 2x
    T=Image.new('RGBA',(W,H),(0,0,0,0)); dr=ImageDraw.Draw(T)
    f1=ImageFont.truetype(F+'MrDafoe-Regular.ttf',54); YS='/mnt/attach/project-files/fonts/YouTubeSans-Black.otf'
    f2=ImageFont.truetype(YS,76); f3=ImageFont.truetype(YS,40); R=W-90; yb=H-80
    def rt(txt,f,y,fill,sw):
        w_=dr.textlength(txt,font=f); dr.text((R-w_,y),txt,font=f,fill=fill,stroke_width=sw,stroke_fill=(0,0,0,255))
    rt(artist,f3,yb-44,(235,235,235,255),4); rt(title,f2,yb-132,(255,255,255,255),6); rt('Now Playing',f1,yb-198,glow+(255,),4)
    sh=T.split()[3].filter(ImageFilter.GaussianBlur(8)).point(lambda p:int(p*0.6))
    TT=Image.new('RGBA',(W,H),(0,0,0,0)); TT.paste((0,0,0,255),mask=sh); TT.alpha_composite(T)
    return bg,fg,D,TT,dsize
def disc_frame(D,dsize,ang):
    S2=D.size[0]; k=S2/1200; lab=int(436*k)
    cx_,cy_=int(600*k),int(613*k); box=(cx_-lab//2,cy_-lab//2,cx_+lab//2,cy_+lab//2)
    L=D.crop(box).rotate(-ang,Image.BICUBIC)
    m=Image.new('L',(lab,lab),0); ImageDraw.Draw(m).ellipse((3,3,lab-4,lab-4),fill=255); m=m.filter(ImageFilter.GaussianBlur(1.5))
    d=D.copy(); d.paste(L,box[:2],m)
    d=d.resize((dsize,dsize),Image.LANCZOS)
    mm=Image.new('L',(dsize*2,dsize*2),0); ImageDraw.Draw(mm).ellipse((2,2,dsize*2-3,dsize*2-3),fill=255); d.putalpha(mm.resize((dsize,dsize),Image.LANCZOS)); return d
def logo(hh):
    im=Image.open(sorted(glob.glob(S+'logo/poster_logo.0m-*'))[0]).convert('RGBA'); im=im.crop(im.getbbox())
    return im.resize((int(im.width*hh/im.height),hh),Image.LANCZOS)
def quote(txt,size=58,col=(236,217,160),font='PlayfairDisplay-Italic[wght].ttf'):
    f=ImageFont.truetype(F+font,size)
    try: f.set_variation_by_axes([500])
    except Exception as e: pass
    T=Image.new('RGBA',(W,260),(0,0,0,0)); dr=ImageDraw.Draw(T); w_=dr.textlength(txt,font=f)
    dr.text(((W-w_)/2,130),txt,anchor='ls',font=f,fill=col+(255,))
    sh=T.split()[3].filter(ImageFilter.GaussianBlur(7)).point(lambda p:int(min(255,p*0.9)))
    O=Image.new('RGBA',(W,260),(0,0,0,0)); O.paste((0,0,0,255),mask=sh); O.alpha_composite(T); return O
def fade(layer,a):
    if a>=1: return layer
    l=layer.copy(); l.putalpha(layer.split()[3].point(lambda p:int(p*a))); return l
if __name__=='__main__':
    out=sys.argv[1]; dur=float(sys.argv[2]) if len(sys.argv)>2 else 11
    bg,fg,D,TT,ds=build(G('music/album-background-desktop'),'RHYNO','Travis Scott',(255,70,190))
    LG=logo(540); fn=sys.argv[3]; fs=int(sys.argv[4]); Q=quote('\u201cHere\u2019s the Mix you ordered, kind sir\u201d',fs,font=fn)
    # logo soft shadow
    ls=Image.new('RGBA',(LG.width+160,LG.height+160),(0,0,0,0)); ls.paste((0,0,0,255),(80,80),LG.split()[3]); ls=ls.filter(ImageFilter.GaussianBlur(30)); ls.putalpha(ls.split()[3].point(lambda p:int(p*0.7)))
    dark=Image.eval(bg,lambda v:int(v*0.42))
    p=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-c:v','libx264','-crf','18','-preset','medium','-pix_fmt','yuv420p',out],stdin=subprocess.PIPE)
    for i in range(int(dur*FPS)):
        t=i/FPS
        m=ease((t-2.1)/1.3)          # 0 intro -> 1 main
        la=1-ease((t-2.0)/0.8)       # logo alpha (full at frame 0)
        qa=ease((t-0.15)/0.6)*(1-ease((t-2.0)/0.8))
        fr=Image.blend(dark,fg,m).convert('RGBA')
        if m>0:
            fr.alpha_composite(fade(disc_frame(D,ds,(t-2.1)*45),m),(W//2-ds//2,H//2-ds//2))
            fr.alpha_composite(fade(TT,m))
        if m<1 and m>0:
            pass
        if la>0:
            sc=1.0+0.03*t/3
            l2=LG.resize((int(LG.width*sc),int(LG.height*sc)),Image.BICUBIC)
            fr.alpha_composite(fade(ls,la),(W//2-ls.width//2,H//2-ls.height//2+12))
            fr.alpha_composite(fade(l2,la),(W//2-l2.width//2,H//2-l2.height//2))
        if False: fr.alpha_composite(fade(Q,qa),(0,H-390))
        p.stdin.write(fr.convert('RGB').tobytes())
        if i in (0,36,66,90): fr.convert('RGB').save(out[:-4]+'_%03d.jpg'%i,quality=88)
    p.stdin.close(); p.wait()
