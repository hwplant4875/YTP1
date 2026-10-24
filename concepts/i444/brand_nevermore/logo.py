from PIL import Image, ImageDraw
src=open('raven/raven.py').read(); src=src[:src.index('pvs=[]')]; ns={}; exec(src,ns)
N,S,sc,bz,P=ns['N'],ns['S'],ns['sc'],ns['bz'],ns['P']
def logo(bg,fg,name,k=1.45,dx=-171,dy=-14,eye_r=20):
    im=Image.new('RGB',(N,N),bg); d=ImageDraw.Draw(im)
    d.polygon(sc(P,dx,dy,k),fill=fg)
    d.line(sc(bz((492,410),(580,412),(660,420),(718,431)),dx,dy,k),fill=bg,width=int(7*S*k))  # beak split
    import math
    # sharp almond eye, tilted down toward the beak: a cut-out, so still two colours
    cx,cy,L,T,a=418,318,36,16,math.radians(16)
    xs=[-L+2*L*i/30 for i in range(31)]
    loc=[(x,-T*(1-(x/L)**2)) for x in xs]+[(x,0.7*T*(1-(x/L)**2)) for x in reversed(xs)]
    pts=[(cx+x*math.cos(a)-y*math.sin(a), cy+x*math.sin(a)+y*math.cos(a)) for x,y in loc]
    d.polygon(sc(pts,dx,dy,k),fill=bg)
    return ns['save'](im,name)
pv=[logo((176,0,16),(10,10,12),'logo_A_red_black'),
    logo((10,10,12),(176,0,16),'logo_B_black_red'),
    logo((240,236,228),(10,10,12),'logo_C_white_black')]
G=Image.new('RGB',(1220,400),'white')
for i,n in enumerate(['logo_A_red_black','logo_B_black_red','logo_C_white_black']): G.paste(Image.open(f'raven/{n}.png').resize((400,400)),(i*410,0))
G.save('raven/logo_options.png')
P2=Image.new('RGB',(560,600),'white'); [P2.paste(p,(0,i*200)) for i,p in enumerate(pv)]; P2.save('raven/logo_previews.png')
