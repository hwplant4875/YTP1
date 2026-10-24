import sys; sys.path.insert(0,'raven')
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import importlib.util
spec=importlib.util.spec_from_file_location('rv','raven/raven.py'); 
src=open('raven/raven.py').read(); src=src[:src.index('pvs=[]')]; ns={}; exec(src,ns)
W,H=2560,1440; F='/mnt/attach/project-files/fonts/YouTubeSans-Black.otf'
im=Image.new('RGB',(W,H),(8,8,10))
# red glow band behind the safe area
g=Image.new('L',(W,H),0); ImageDraw.Draw(g).ellipse([W/2-1100,H/2-330,W/2+1100,H/2+330],fill=150); g=g.filter(ImageFilter.GaussianBlur(160)); im.paste((150,0,12),(0,0),g)
# raven head (from the profile art) on the left of the safe area
N=ns['N']; r=Image.new('RGB',(N,N),(0,0,0)); m=Image.new('L',(N,N),0)
ns['raven'](r,eye=(255,40,40),beak=(120,0,10)); 
mk=Image.new('RGB',(N,N),(0,0,0)); ns['raven'](mk,body=(255,255,255),eye=(255,255,255),beak=(255,255,255)); m=mk.convert('L').point(lambda v:255 if v>20 else 0)
sz=500; r=r.resize((sz,sz),Image.LANCZOS); m=m.resize((sz,sz),Image.LANCZOS)
fade=Image.linear_gradient('L').resize((sz,sz)).point(lambda v: 255 if v<150 else max(0,255-(v-150)*2.4))
from PIL import ImageChops
m=ImageChops.multiply(m,fade)
im.paste(r,(W//2-730,H//2-sz//2+40),m)
d=ImageDraw.Draw(im)
f1=ImageFont.truetype(F,160); f2=ImageFont.truetype(F,46)
x=W//2-230
d.text((x,H//2-30),'NEVERMORE',font=f1,fill=(242,238,230),anchor='ls')
d.rectangle([x+6,H//2+10,x+150,H//2+18],fill=(200,0,20))
d.text((x+4,H//2+100),'WOULD YOU SURVIVE THE HORROR MOVIE?',font=f2,fill=(200,0,20),anchor='ls')
im.save('raven/banner_nevermore.png')
# safe-area check: draw guides on a copy
c=im.copy(); dc=ImageDraw.Draw(c); dc.rectangle([(W-1546)//2,(H-423)//2,(W+1546)//2,(H+423)//2],outline=(0,255,0),width=4); dc.rectangle([(W-2560)//2,(H-423)//2,(W+2560)//2,(H+423)//2],outline=(255,255,0),width=2)
c.resize((1280,720)).save('raven/banner_check.png')
