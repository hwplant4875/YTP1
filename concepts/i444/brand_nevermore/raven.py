from PIL import Image, ImageDraw, ImageFilter
S=4; N=800*S
def bz(p0,c1,c2,p1,n=24):
    return [((1-t)**3*p0[0]+3*(1-t)**2*t*c1[0]+3*(1-t)*t*t*c2[0]+t**3*p1[0],(1-t)**3*p0[1]+3*(1-t)**2*t*c1[1]+3*(1-t)*t*t*c2[1]+t**3*p1[1]) for t in [i/n for i in range(n+1)]]
P=(bz((725,432),(640,372),(545,312),(470,296))+bz((470,296),(445,240),(405,212),(355,210))+bz((355,210),(285,210),(232,258),(222,330))
   +bz((222,330),(205,450),(175,620),(150,800))
   +[(150,800),(620,800)]+[(590,720),(640,712),(575,668),(618,650),(560,612),(598,590),(540,556),(574,532),(512,500)]
   +bz((512,500),(570,486),(660,460),(725,432)))
def sc(p,dx=0,dy=0,k=1.0): return [((x-400)*k*S+N/2+dx*S,(y-400)*k*S+N/2+dy*S) for x,y in p]
def raven(im,body=(8,8,10),eye=(235,20,30),rim=None,dx=0,dy=40,k=1.0,beak=None):
    d=ImageDraw.Draw(im); pts=sc(P,dx,dy,k)
    if rim:
        g=Image.new('L',im.size,0); ImageDraw.Draw(g).polygon(pts,fill=255); g=g.filter(ImageFilter.MaxFilter(27)).filter(ImageFilter.GaussianBlur(8))
        im.paste(rim,(0,0),g)
    d.polygon(pts,fill=body)
    bl=beak or tuple(min(255,c+40) for c in body)
    d.line(sc(bz((492,410),(580,412),(660,420),(718,431)),dx,dy,k),fill=bl,width=int(5*S*k))
    ex,ey=sc([(420,318)],dx,dy,k)[0]; r=24*S*k
    gl=Image.new('L',im.size,0); ImageDraw.Draw(gl).ellipse([ex-r*2.2,ey-r*2.2,ex+r*2.2,ey+r*2.2],fill=170); gl=gl.filter(ImageFilter.GaussianBlur(r))
    im.paste(eye,(0,0),gl); d=ImageDraw.Draw(im)
    d.ellipse([ex-r,ey-r,ex+r,ey+r],fill=eye); d.ellipse([ex-r*0.35-r*0.25,ey-r*0.6,ex+r*0.35-r*0.25,ey+r*0.1],fill=(255,235,230))
def save(im,name):
    im=im.resize((800,800),Image.LANCZOS); im.save(f'raven/{name}.png')
    pv=Image.new('RGB',(560,200),(255,255,255)); x=10
    for sz in (176,88,40):
        m=Image.new('L',(sz*4,sz*4),0); ImageDraw.Draw(m).ellipse([0,0,sz*4-1,sz*4-1],fill=255); m=m.resize((sz,sz),Image.LANCZOS)
        pv.paste(im.resize((sz,sz),Image.LANCZOS),(x,100-sz//2),m); x+=sz+30
    return pv
pvs=[]
# A: blood red background, black raven, glowing red eye
im=Image.new('RGB',(N,N),(170,0,14)); raven(im,eye=(255,40,40),beak=(120,0,10)); pvs.append(save(im,'raven_A_red'))
# B: black background, red rim light, red eye
im=Image.new('RGB',(N,N),(6,6,8)); raven(im,body=(10,10,12),rim=(200,0,20),beak=(60,60,64)); pvs.append(save(im,'raven_B_black_rim'))
# C: black background, blood moon behind the raven
im=Image.new('RGB',(N,N),(6,6,8)); d=ImageDraw.Draw(im); R=300*S
g=Image.new('L',im.size,0); ImageDraw.Draw(g).ellipse([N/2-R*1.15,N/2-R*1.15-60*S,N/2+R*1.15,N/2+R*1.15-60*S],fill=120); g=g.filter(ImageFilter.GaussianBlur(60*S)); im.paste((150,0,12),(0,0),g)
d=ImageDraw.Draw(im); d.ellipse([N/2-R,N/2-R-60*S,N/2+R,N/2+R-60*S],fill=(185,8,20))
raven(im,body=(8,8,10),eye=(255,255,255),beak=(55,55,58),k=0.92,dy=70); pvs.append(save(im,'raven_C_moon'))
G=Image.new('RGB',(1220,400),'white')
for i,n in enumerate(['raven_A_red','raven_B_black_rim','raven_C_moon']): G.paste(Image.open(f'raven/{n}.png').resize((400,400)),(i*410,0))
G.save('raven/options.png')
P2=Image.new('RGB',(560,600),'white'); [P2.paste(p,(0,i*200)) for i,p in enumerate(pvs)]; P2.save('raven/previews.png')
