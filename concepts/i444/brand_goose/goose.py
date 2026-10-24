from PIL import Image, ImageDraw
import math, random
S=4; N=800*S
def bz(p0,c1,c2,p1,n=30):
    return [((1-t)**3*p0[0]+3*(1-t)**2*t*c1[0]+3*(1-t)*t*t*c2[0]+t**3*p1[0],(1-t)**3*p0[1]+3*(1-t)**2*t*c1[1]+3*(1-t)*t*t*c2[1]+t**3*p1[1]) for t in [i/n for i in range(n+1)]]
def sc(p,k=1.15,dx=-40,dy=40): return [((x-400)*k+400+dx)*S for x,y in p], None
def T(p,k=1.15,dx=-60,dy=60): return [(((x-400)*k+400+dx)*S,((y-400)*k+400+dy)*S) for x,y in p]
UP=bz((712,292),(700,262),(630,238),(560,226))+bz((560,236),(540,190),(480,165),(430,185))
BACK=bz((430,185),(380,205),(370,260),(380,320))+bz((380,320),(395,420),(330,520),(260,620))+bz((260,620),(225,680),(205,740),(200,800),12)
FRONT=bz((470,800),(430,700),(470,560),(500,450))+bz((500,450),(525,380),(520,340),(560,320))
LOW=bz((560,320),(620,330),(680,322),(712,292))
P=UP+BACK+[(470,800)]+FRONT+LOW
def inside(poly,x,y):
    c=False; j=len(poly)-1
    for i in range(len(poly)):
        xi,yi=poly[i]; xj,yj=poly[j]
        if (yi>y)!=(yj>y) and x<(xj-xi)*(y-yi)/(yj-yi)+xi: c=not c
        j=i
    return c
def make(bg,fg,name):
    im=Image.new('RGB',(N,N),bg); d=ImageDraw.Draw(im); poly=T(P); d.polygon(poly,fill=fg)
    # bumps on the outline: little raised domes along the back of the head and neck
    for i in range(4,len(BACK)-6,3):
        x,y=T([BACK[i]])[0]; r=(9+3*math.sin(i))*S*1.15; d.ellipse([x-r,y-r,x+r,y+r],fill=fg)
    for i in range(2,len(FRONT)-8,3):
        x,y=T([FRONT[i]])[0]; r=8*S*1.15; d.ellipse([x-r,y-r,x+r,y+r],fill=fg)
    # goosebumps on the skin: small rings (background colour) scattered over head and neck
    random.seed(7); pts=[]
    while len(pts)<70:
        x=random.uniform(220,560); y=random.uniform(190,790)
        if not inside(P,x,y) or math.hypot(x-505,y-228)<45 or (x>540 and y<330): continue
        if any(math.hypot(x-a,y-b)<30 for a,b in pts): continue
        # stay off the edges
        if not all(inside(P,x+dx,y+dy) for dx,dy in [(14,0),(-14,0),(0,14),(0,-14)]): continue
        pts.append((x,y))
    for x,y in pts:
        (X,Y),=T([(x,y)]); r=random.uniform(5,8)*S*1.15
        d.ellipse([X-r,Y-r,X+r,Y+r],outline=bg,width=int(2.6*S))
    # mouth line + angry almond eye (cut-outs)
    m=bz((562,282),(610,290),(660,296),(704,292),24)
    d.line(T(m),fill=bg,width=int(5*S))
    for i in range(1,len(m)-3,2):
        (x0,y0),(x1,y1)=m[i],m[i+2]; xm=(x0+x1)/2
        d.polygon(T([(x0,y0),(xm,y0+9),(x1,y1)]),fill=bg)
    cx,cy,L,Tt,a=505,226,24,10,math.radians(20)
    xs=[-L+2*L*i/30 for i in range(31)]
    loc=[(x,-Tt*(1-(x/L)**2)) for x in xs]+[(x,0.7*Tt*(1-(x/L)**2)) for x in reversed(xs)]
    d.polygon(T([(cx+x*math.cos(a)-y*math.sin(a), cy+x*math.sin(a)+y*math.cos(a)) for x,y in loc]),fill=bg)
    im=im.resize((800,800),Image.LANCZOS); im.save(f'goose/{name}.png')
    pv=Image.new('RGB',(560,200),(255,255,255)); x=10
    for sz in (176,88,40):
        m=Image.new('L',(sz*4,sz*4),0); ImageDraw.Draw(m).ellipse([0,0,sz*4-1,sz*4-1],fill=255); m=m.resize((sz,sz),Image.LANCZOS)
        pv.paste(im.resize((sz,sz),Image.LANCZOS),(x,100-sz//2),m); x+=sz+30
    return pv
names=['goose_A_black_white','goose_B_red_black','goose_C_white_black']
pv=[make((10,10,12),(240,236,228),names[0]),make((176,0,16),(10,10,12),names[1]),make((240,236,228),(10,10,12),names[2])]
G=Image.new('RGB',(1220,1000),'white')
for i,n in enumerate(names): G.paste(Image.open(f'goose/{n}.png').resize((400,400)),(i*410,0))
for i,p in enumerate(pv): G.paste(p,(0,400+i*200))
G.save('goose/goose_options.png')
