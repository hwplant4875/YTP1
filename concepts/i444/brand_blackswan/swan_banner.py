from PIL import Image, ImageDraw, ImageFont, ImageOps
import sys
src=Image.open(sys.argv[1]).convert('L')
mask=src.point(lambda v:255 if v<128 else 0); mask=mask.crop(mask.getbbox())
BLK=(10,10,12); WHT=(240,236,228); RED=(190,0,18); GRY=(150,146,140)
def banner(swan_col,name):
    s=2; W,H=2560*s,1440*s; B=Image.new('RGB',(W,H),BLK); d=ImageDraw.Draw(B)
    sh=380*s; m=mask.resize((int(mask.width*sh/mask.height),sh),Image.LANCZOS)
    f1=ImageFont.truetype('fonts/Anton.ttf',150*s); f2=ImageFont.truetype('fonts/Anton.ttf',34*s)
    t1='BLACK SWAN'; t2='HORROR'
    w1=d.textbbox((0,0),t1,font=f1)[2]; gap=60*s; tot=m.width+gap+w1
    x0=(W-tot)//2; cy=H//2
    B.paste(Image.new('RGB',m.size,swan_col),(x0,cy-sh//2),m)
    tx=x0+m.width+gap
    b=d.textbbox((0,0),t1,font=f1); d.text((tx,cy-20*s-b[3]),t1,font=f1,fill=WHT)
    f3=ImageFont.truetype('fonts/Anton.ttf',96*s); d.text((tx,cy-5*s),t2,font=f3,fill=RED)
    hb=d.textbbox((tx,cy-5*s),t2,font=f3)
    d.text((hb[2]+30*s,hb[1]+(hb[3]-hb[1])/2-17*s),'EVERY HORROR VILLAIN, RANKED',font=f2,fill=GRY)
    B=B.resize((2560,1440),Image.LANCZOS); B.save(f'out/{name}.png')
    # safe-area check overlay
    C=B.copy(); ImageDraw.Draw(C).rectangle([507,508,2053,931],outline=(0,255,0),width=3); C.save(f'out/{name}_safecheck.png')
banner(WHT,'banner_blackswan_A_white')
banner(RED,'banner_blackswan_B_red')
