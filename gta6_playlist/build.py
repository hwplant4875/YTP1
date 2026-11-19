import sys, json, os, glob, subprocess
sys.argv=[sys.argv[0]]
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import intro as I
W,H=I.W,I.H
TR=[
(4,'RHYNO','Travis Scott','music/album-background-desktop',(255,70,190)),
(2,"That's It",'Yung Lean, Future & Metro Boomin','shots/Jason_Duval_11',(90,150,255)),
(3,'Ahh Yea','Playboi Carti','shots/Jason_Duval_10',(60,230,200)),
(18,'TF?','Don Toliver','shots/Lucia_Caminos_11',(150,110,255)),
(15,"Let's Rock",'Kodak Black & Don Toliver','shots/Vice_City_25',(255,80,160)),
(14,'Count Up','Gunna','shots/Vice_City_18',(255,90,220)),
(16,'Wake Up Flex','Young Thug','shots/Boobie_Ike_03',(255,110,170)),
(19,"Don't Chart",'Cardi B','shots/Real_Dimez_04',(200,90,255)),
(20,'GMA','JT','shots/Real_Dimez_02',(255,100,150)),
(17,'IKYFL','Tee Grizzley','shots/Vice_City_12',(80,200,220)),
(12,'Dance with Me','A Boogie wit da Hoodie ft. Elkan','shots/DreQuan_Priest_03',(190,120,255)),
(13,'Bigger','Burna Boy','music/afrobank-background',(255,160,50)),
(11,'Macacoa 2000','Rauw Alejandro','music/cocoteo-background',(255,120,200)),
(9,'X','Jhayco','shots/Vice_City_13',(90,255,170)),
(10,'Suzuki','Fuerza Regida','shots/Mount_Kalaga_National_Park_01',(255,190,110)),
(26,'Sandunguea','Arca','shots/Vice_City_07',(255,70,230)),
(5,'Sexy Magic','CA7RIEL & Paco Amoroso, PinkPantheress, Fred again.., Étienne de Crécy','shots/Leonida_Keys_05',(70,210,255)),
(7,'Go Easy','Dua Lipa','shots/Lucia_Caminos_02',(255,120,150)),
(21,'Power Trip','JENNIE','shots/Lucia_Caminos_10',(220,110,255)),
(23,'Fast Emotion','Zara Larsson','shots/Jason_and_Lucia_09',(120,200,255)),
(24,'Sweet Like Candy','Camila Cabello','shots/Cal_Hampton_03',(255,130,200)),
(22,'Blood in Your Eyes','Tove Lo','shots/Port_Gellhorn_04',(255,70,90)),
(25,'Only One','Fcukers','shots/Jason_and_Lucia_14',(110,120,255)),
(27,'Trdwfe','Rina Sawayama','shots/Lucia_Caminos_06',(255,90,140)),
(28,'All Again','Rose Gray','shots/Vice_City_27',(200,130,255)),
(1,'Starting from Zero','Justice ft. Michael McDonald','shots/Vice_City_01',(255,170,120)),
(6,'Flower in a Hurricane','Justice ft. Tame Impala, SZA, King Gizzard & the Lizard Wizard','shots/Jason_and_Lucia_13',(255,180,110)),
(33,'Stone Kold Krazy Luuv','Jesse Johnson & Dâm-Funk','shots/VINTAGE_VICE_CITY_PACK_VAPID_STANIER_01',(255,200,80)),
(8,'Last Thing You Need','Morgan Wallen','music/country-background',(255,170,60)),
(32,'Bright Lights, Big City','Keith Richards','shots/Vice_City_11',(255,160,90)),
(30,'Largate','Kali Uchis & Helado Negro','shots/Leonida_Keys_01',(90,220,230)),
(31,'No Me Busques','Omar Apollo','shots/Port_Gellhorn_06',(255,150,90)),
(29,'Crazy for You','Lana Del Rey','shots/Jason_and_Lucia_16',(255,190,100)),
(34,'Overtown Lights','Stanley Clarke, Yussef Dayes & Robert Glasper','shots/Vice_City_08',(140,150,255)),
]
assert sorted(t[0] for t in TR)==list(range(1,35))
OUT='/tmp/gta/out'; os.makedirs(OUT,exist_ok=True)
D=None; meta=[]
for i,(alb,title,artist,bg,glow) in enumerate(TR,1):
    bgim,fg,D,TT,ds=I.build(I.G(bg),title,artist,glow)
    fr=fg.convert('RGBA'); fr.alpha_composite(I.disc_frame(D,ds,0),(W//2-ds//2,H//2-ds//2)); fr.alpha_composite(TT)
    fr.convert('RGB').save(f'{OUT}/base_{i:02d}.jpg',quality=95,subsampling=0)
    meta.append(dict(pos=i,album_no=alb,title=title,artist=artist,base=f'base_{i:02d}.jpg'))
    print(i,title,flush=True)
# label png (2x, 436) 
S2=D.size[0]; lab=436; cx_,cy_=600,613
L=D.crop((cx_-lab//2,cy_-lab//2,cx_+lab//2,cy_+lab//2)).convert('RGBA')
m=Image.new('L',(lab,lab),0); ImageDraw.Draw(m).ellipse((3,3,lab-4,lab-4),fill=255); m=m.filter(ImageFilter.GaussianBlur(1.5)); L.putalpha(m); L.save(f'{OUT}/label_436.png')
json.dump(dict(order=meta,label=dict(file='label_436.png',scale_to=218,x=851,y=437,deg_per_sec=45,angle_at_t0_offset=-2.1),intro=dict(file='intro_4s.mp4',seconds=4.0)),open(f'{OUT}/order.json','w'),ensure_ascii=False,indent=1)
