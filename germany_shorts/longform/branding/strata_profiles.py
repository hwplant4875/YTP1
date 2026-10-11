from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
MF="/tmp/claude-0/strata/Montserrat-VF.ttf"
def F(size,w=900):
    f=ImageFont.truetype(MF,size); f.set_variation_by_axes([w]); return f
AMBER=(255,170,80); CREAM=(240,236,228); BG=(10,10,12)
P=800
def glow(im,mask,col,r=30,a=0.6):
    g=Image.new("RGB",im.size,col); m=mask.filter(ImageFilter.GaussianBlur(r)).point(lambda v:int(v*a))
    return Image.composite(g,im,m)
# A: big S sliced into strata, one amber slice
S=Image.new("L",(P,P),0); d=ImageDraw.Draw(S); d.text((P//2,P//2+10),"S",font=F(640,900),fill=255,anchor="mm")
bands=Image.new("RGB",(P,P)); bd=ImageDraw.Draw(bands)
ys=[0,250,345,420,455,560,P]; cols=[(225,222,215),(170,168,164),(120,118,116),AMBER,(80,79,78),(55,55,56)]
for (a,b),c in zip(zip(ys,ys[1:]),cols): bd.rectangle([0,a,P,b],fill=c)
gaps=Image.new("L",(P,P),255); gd=ImageDraw.Draw(gaps)
for y in ys[1:-1]: gd.rectangle([0,y-5,P,y+5],fill=0)
m=ImageChops.multiply(S,gaps)
im=Image.new("RGB",(P,P),BG)
am=Image.new("L",(P,P),0); ImageDraw.Draw(am).rectangle([0,420,P,455],fill=255); am=ImageChops.multiply(am,S)
im=glow(im,am,AMBER,40,0.9)
im.paste(bands,(0,0),m); im.save("p2_A_S_layers.png")
# B: cross-section icon: ground surface, layers, glowing tunnel arch underneath
im=Image.new("RGB",(P,P),BG); d=ImageDraw.Draw(im)
d.rectangle([0,0,P,300],fill=(22,24,30))
d.rectangle([0,300,P,312],fill=CREAM)                 # street level
layers=[(312,400,(70,64,58)),(400,470,(56,51,47)),(470,800,(40,37,35))]
for a,b,c in layers: d.rectangle([0,a,P,b],fill=c)
for y in (400,470): d.line([0,y,P,y],fill=(25,24,23),width=6)
# tunnel arch
tm=Image.new("L",(P,P),0); td=ImageDraw.Draw(tm); td.rounded_rectangle([170,500,630,700],radius=120,fill=255); td.rectangle([170,600,630,700],fill=255)
im=glow(im,tm,AMBER,45,0.85); im.paste(Image.new("RGB",(P,P),(255,190,110)),(0,0),tm)
d=ImageDraw.Draw(im); d.rectangle([170,668,630,700],fill=(40,30,22))
for x in range(200,620,48): d.rectangle([x,676,x+26,684],fill=(90,70,50))
d.text((P//2,165),"STRATA",font=F(118,800),fill=CREAM,anchor="mm")
im.save("p2_B_crosssection.png")
# C: clean letter S on black + amber layer line through it
im=Image.new("RGB",(P,P),BG); S=Image.new("L",(P,P),0); ImageDraw.Draw(S).text((P//2,P//2+10),"S",font=F(600,900),fill=255,anchor="mm")
im.paste(Image.new("RGB",(P,P),CREAM),(0,0),S)
cut=Image.new("L",(P,P),0); ImageDraw.Draw(cut).rectangle([0,402,P,432],fill=255)
im.paste(Image.new("RGB",(P,P),BG),(0,0),cut)
line=Image.new("L",(P,P),0); ImageDraw.Draw(line).rectangle([90,410,710,424],fill=255)
im=glow(im,line,AMBER,30,0.9); im.paste(Image.new("RGB",(P,P),AMBER),(0,0),line)
im.save("p2_C_S_cut.png")
