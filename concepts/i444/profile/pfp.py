from PIL import Image, ImageDraw, ImageFilter
import math
S=4; N=800*S
def skull(d, bone, hole, cx=N//2, cy=int(N*0.47), sc=1.0, red=None, grin=None):
    u=N/800*sc; grin=grin or hole
    d.ellipse([cx-215*u, cy-250*u, cx+215*u, cy+150*u], fill=bone)
    d.rounded_rectangle([cx-172*u, cy+20*u, cx+172*u, cy+240*u], radius=85*u, fill=bone)
    for sgn in (-1,1):
        ex=cx+sgn*95*u; ey=cy-10*u; w=72*u
        pts=[(ex+sgn*w,ey-48*u),(ex-sgn*w,ey+2*u),(ex-sgn*(w-18*u),ey+52*u),(ex+sgn*(w-14*u),ey+44*u)]
        d.polygon(pts, fill=hole)
        if red: d.ellipse([ex-sgn*8*u-10*u, ey+14*u, ex-sgn*8*u+10*u, ey+34*u], fill=red)
    d.polygon([(cx,cy+62*u),(cx-24*u,cy+108*u),(cx+24*u,cy+108*u)], fill=hole)
    gy=cy+150*u; W=158*u
    up=lambda x: gy-52*u+58*u*(1-(x/W)**2)
    lo=lambda x: gy-52*u+128*u*(1-(x/W)**2)
    xs=[ -W+W*2*i/200 for i in range(201)]
    d.polygon([(cx+x,up(x)) for x in xs]+[(cx+x,lo(x)) for x in reversed(xs)], fill=grin)
    for k in range(-5,6):
        x=k*26*u
        if abs(x)<W-12*u: d.line([(cx+x,up(x)-2*u),(cx+x,lo(x)+2*u)], fill=bone, width=int(7*u))
def make(name,bg,bone,hole,red=None,glow=None,grin=None):
    im=Image.new('RGB',(N,N),bg)
    if glow:
        g=Image.new('RGB',(N,N),bg); gd=ImageDraw.Draw(g); gd.ellipse([N*0.12,N*0.1,N*0.88,N*0.86],fill=glow); g=g.filter(ImageFilter.GaussianBlur(N*0.08)); im=g
    d=ImageDraw.Draw(im); skull(d,bone,hole,red=red,grin=grin)
    im=im.resize((800,800),Image.LANCZOS); im.save(f'pfp/{name}.png')
    # circle preview at 3 sizes
    pv=Image.new('RGB',(560,200),(255,255,255)); x=10
    for sz in (176,88,40):
        m=Image.new('L',(sz*4,sz*4),0); ImageDraw.Draw(m).ellipse([0,0,sz*4-1,sz*4-1],fill=255); m=m.resize((sz,sz),Image.LANCZOS)
        pv.paste(im.resize((sz,sz),Image.LANCZOS),(x,100-sz//2),m); x+=sz+30
    pv.save(f'pfp/{name}_preview.png')
make('A_red_grin',(176,0,16),(245,240,232),(18,6,8))
make('B_black_redeyes',(8,8,10),(245,242,236),(8,8,10),red=(230,20,30),glow=(60,0,6))
make('C_black_redgrin',(10,10,12),(240,236,228),(10,10,12),grin=(200,0,20))
