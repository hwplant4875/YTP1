from PIL import Image, ImageDraw, ImageFont
BLK=(10,10,12); WHT=(240,236,228); RED=(190,0,18); s=2; W,H=2560*s,1440*s
F=lambda n:ImageFont.truetype('fonts/Anton.ttf',n*s)
def new(): B=Image.new('RGB',(W,H),BLK); return B,ImageDraw.Draw(B)
# stacked
B,d=new(); f1,f2=F(170),F(110); cx,cy=W//2,H//2
b1=d.textbbox((0,0),'BLACK SWAN',font=f1); b2=d.textbbox((0,0),'HORROR',font=f2)
h1=b1[3]-b1[1]; h2=b2[3]-b2[1]; gap=36*s; top=cy-(h1+gap+h2)//2
d.text((cx-(b1[0]+b1[2])/2,top-b1[1]),'BLACK SWAN',font=f1,fill=WHT)
d.text((cx-(b2[0]+b2[2])/2,top+h1+gap-b2[1]),'HORROR',font=f2,fill=RED)
B.resize((2560,1440),Image.LANCZOS).save('out/banner_blackswan_C_stacked.png')
# one line
B,d=new(); f=F(160); t1='BLACK SWAN '; t2='HORROR'
w1=d.textlength(t1,font=f); w2=d.textlength(t2,font=f); x=cx-(w1+w2)/2; b=d.textbbox((0,0),t1+t2,font=f); y=cy-(b[1]+b[3])/2
d.text((x,y),t1,font=f,fill=WHT); d.text((x+w1,y),t2,font=f,fill=RED)
B.resize((2560,1440),Image.LANCZOS).save('out/banner_blackswan_D_oneline.png')
