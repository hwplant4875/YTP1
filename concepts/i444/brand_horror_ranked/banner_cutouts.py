from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
W,H=2560,1440
B=Image.new('RGB',(W,H),(8,6,8))
# dark red fog glow behind the lineup
g=Image.new('L',(W,H),0); ImageDraw.Draw(g).ellipse([300,300,2260,1500],fill=255); g=g.filter(ImageFilter.GaussianBlur(220))
B=Image.composite(Image.new('RGB',(W,H),(70,0,8)),B,g)
def put(name,fx,fy,fh,X,Y,FH,bright=1.0,crop=None):
    global B
    im=Image.open('cut2/'+name+'.png').convert('RGBA')
    if crop: im=im.crop(crop); im=im.crop(im.getbbox())
    sc=FH/(fh*im.height); im=im.resize((int(im.width*sc),int(im.height*sc)),Image.LANCZOS)
    if bright!=1.0:
        a=im.getchannel('A'); im=ImageEnhance.Brightness(im.convert('RGB')).enhance(bright).convert('RGBA'); im.putalpha(a)
    if name in FADE:
        a=im.getchannel('A'); g=Image.new('L',im.size,255); dd=ImageDraw.Draw(g); h0=int(im.height*0.7)
        for y in range(h0,im.height): dd.line([(0,y),(im.width,y)],fill=int(255*(1-(y-h0)/(im.height-h0))))
        from PIL import ImageChops; im.putalpha(ImageChops.multiply(a,g))
    B.paste(im,(int(X-fx*im.width),int(Y-fy*im.height)),im)
FADE={'10225_qdQ','9003_bxm','346364_rAQc','10585_2wU0'}
BK,FR=610,790
L=[ # back row
 ('9003_bxm',.45,.42,.6,600,BK,330,.8,(0,0,900,10000)),
 ('565_cAk3',.5,.11,.2,1180,BK,170,.75,None),
 ('346364_rAQc',.42,.42,.45,1760,BK,190,.8,None),
 ('934433_AlPm',.55,.08,.12,2330,BK,180,.9,None),
 # front row
 ('377_paBQ',.33,.12,.1,300,FR+20,120,1.1,None),
 ('10225_qdQ',.43,.25,.4,890,FR,220,1.0,None),
 ('948_6Io0',.5,.14,.18,1470,FR,220,1.0,None),
 ('10585_2wU0',.6,.3,.3,2050,FR,220,1.05,None),
]
for a in L: put(*a)
# bottom fade to black
f=Image.new('L',(W,H),0); d=ImageDraw.Draw(f)
for y in range(1150,H): d.line([(0,y),(W,y)],fill=int(255*min(1,(y-1150)/290)))
B=Image.composite(Image.new('RGB',(W,H),(8,6,8)),B,f)
B.save('banner_horror_ranked_cutouts.png')
C=B.copy(); ImageDraw.Draw(C).rectangle([507,508,2053,931],outline=(0,255,0),width=3); C.resize((1280,720)).save('check2.png')
