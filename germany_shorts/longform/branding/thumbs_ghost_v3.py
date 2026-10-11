# A/B thumbnail variants (b: provocative red markup on a 3D frame, c: edited archive photo).
# usage: python3 thumbs_ab.py <scratch dir with bg1b.png bg2b.png> <out dir>
import sys, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageEnhance

EP = "/home/user/YTP1/germany_shorts/longform/episodes"
FONT = "/home/user/YTP1/germany_shorts/fonts/YouTubeSans-Black.otf"
W, H = 1280, 720
CREAM, AMBER, RED = (245, 240, 230), (255, 166, 77), (235, 30, 35)
F = lambda s: ImageFont.truetype(FONT, s)

def fit(im):
    im = ImageOps.fit(im.convert("RGB"), (W, H), Image.LANCZOS, centering=(0.5, 0.5)); return im

def shade(im, box, alpha, horizontal=None):
    """dark gradient over part of the frame; horizontal='l'|'r'|'t'|'b' fades toward the inside"""
    m = Image.new("L", (W, H), 0); d = ImageDraw.Draw(m)
    x0, y0, x1, y1 = box
    for i in range(256):
        t = i / 255
        if horizontal == "l": d.line([(x0 + (x1 - x0) * t, y0), (x0 + (x1 - x0) * t, y1)], fill=int(alpha * (1 - t)), width=math.ceil((x1 - x0) / 255) + 1)
        if horizontal == "r": d.line([(x1 - (x1 - x0) * t, y0), (x1 - (x1 - x0) * t, y1)], fill=int(alpha * (1 - t)), width=math.ceil((x1 - x0) / 255) + 1)
        if horizontal == "t": d.line([(x0, y0 + (y1 - y0) * t), (x1, y0 + (y1 - y0) * t)], fill=int(alpha * (1 - t)), width=math.ceil((y1 - y0) / 255) + 1)
        if horizontal == "b": d.line([(x0, y1 - (y1 - y0) * t), (x1, y1 - (y1 - y0) * t)], fill=int(alpha * (1 - t)), width=math.ceil((y1 - y0) / 255) + 1)
    return Image.composite(Image.new("RGB", (W, H), (0, 0, 0)), im, m)

def text(d, xy, s, size, fill, anchor="la", stroke=0, sf=(0, 0, 0)):
    d.text(xy, s, font=F(size), fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=sf)

def glow_layer(im, draw_fn, blur=10, strength=0.9):
    """draw shapes, add a soft dark halo under them so red reads on any background"""
    halo = Image.new("L", (W, H), 0); draw_fn(ImageDraw.Draw(halo), 255, extra=8)
    halo = halo.filter(ImageFilter.GaussianBlur(blur)).point(lambda v: int(v * strength))
    im = Image.composite(Image.new("RGB", (W, H), (0, 0, 0)), im, halo)
    draw_fn(ImageDraw.Draw(im), RED, extra=0); return im

def ring(cx, cy, rx, ry, w=11):
    def fn(d, col, extra=0):
        d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], outline=col, width=w + extra)
    return fn

def arrow(x0, y0, x1, y1, w=16, head=46):
    def fn(d, col, extra=0):
        a = math.atan2(y1 - y0, x1 - x0)
        bx, by = x1 - head * 0.8 * math.cos(a), y1 - head * 0.8 * math.sin(a)
        # slight curve: quadratic through a lifted midpoint
        mx, my = (x0 + bx) / 2 - math.sin(a) * 40, (y0 + by) / 2 + math.cos(a) * -40
        pts = [((1 - t) ** 2 * x0 + 2 * (1 - t) * t * mx + t * t * bx, (1 - t) ** 2 * y0 + 2 * (1 - t) * t * my + t * t * by) for t in [i / 40 for i in range(41)]]
        d.line(pts, fill=col, width=w + extra, joint="curve")
        a2 = math.atan2(by - pts[-4][1], bx - pts[-4][0])
        p = [(x1 + extra * math.cos(a2), y1 + extra * math.sin(a2))]
        for s in (-1, 1): p.append((x1 - (head + extra) * math.cos(a2 + s * 0.5), y1 - (head + extra) * math.sin(a2 + s * 0.5)))
        d.polygon(p, fill=col)
    return fn

def label(im, xy, s, size=34, anchor="la"):
    d = ImageDraw.Draw(im); f = F(size)
    l, t, r, b = d.textbbox(xy, s, font=f, anchor=anchor)
    d.rectangle([l - 12, t - 8, r + 12, b + 8], fill=RED); d.text(xy, s, font=f, fill=(255, 255, 255), anchor=anchor)

# ---- 1b: ghost station, train passing an armed guard

from PIL import ImageEnhance
O="/tmp/claude-0/th/out/"
def boost(im,b=1.25,c=1.15): return ImageEnhance.Contrast(ImageEnhance.Brightness(im).enhance(b)).enhance(c)
# A: 3D ghost platform, text at the bottom
im=boost(fit(Image.open("/tmp/claude-0/th/big_escape_rare_0.3.png")),1.45,1.2)
im=shade(im,(0,H-320,W,H),235,"b")
d=ImageDraw.Draw(im)
text(d,(W//2,H-300),"SEALED",160,AMBER,"ma",10)
text(d,(W//2,H-120),"FOR 28 YEARS",64,CREAM,"ma",7)
im.save(O+"2a.jpg",quality=92)
# B: provocative, train blasting through
im=boost(fit(Image.open("/tmp/claude-0/th/big_intro_passby_0.3.png")),1.1,1.15)
im=shade(im,(0,0,W,260),210,"t")
d=ImageDraw.Draw(im)
text(d,(60,40),"IT NEVER",110,CREAM,"la",9)
text(d,(60,150),"STOPPED",110,AMBER,"la",9)
im=glow_layer(im,ring(800,410,95,70))
im=glow_layer(im,arrow(560,330,690,400))
label(im,(800,520),"EAST BERLIN · 1961-1989",34,"ma")
im.save(O+"2b.jpg",quality=92)
# C: real photo, Rosenthaler Platz ghost station as found in Dec 1989; provocative stamp
src=Image.open("/home/user/YTP1/germany_shorts/longform/episodes/01_ghost_stations/assets/c03.jpg").convert("L")
src=ImageOps.autocontrast(src,cutoff=1)
im=ImageOps.colorize(src,(6,8,10),(255,214,160),mid=(110,92,70)).convert("RGB")
im=boost(fit(im),1.15,1.3)
im=shade(im,(0,H-330,W,H),240,"b")
im=shade(im,(0,0,W,180),160,"t")
d=ImageDraw.Draw(im)
text(d,(56,H-310),"FROZEN",150,AMBER,"la",11)
text(d,(60,H-150),"SINCE 1961",86,CREAM,"la",9)
# red rubber stamp, rotated
st=Image.new("RGBA",(560,170),(0,0,0,0)); sd=ImageDraw.Draw(st)
sd.rounded_rectangle([6,6,554,164],radius=14,outline=RED+(255,),width=12)
sd.text((280,88),"VERBOTEN",font=F(108),fill=RED+(255,),anchor="mm")
st=st.rotate(-12,expand=True,resample=Image.BICUBIC)
sh=Image.new("RGBA",st.size,(0,0,0,0)); sh.paste((0,0,0,200),mask=st.split()[3].filter(ImageFilter.GaussianBlur(8)))
im=im.convert("RGBA"); im.alpha_composite(sh,(W-st.width-30,40)); im.alpha_composite(st,(W-st.width-40,30)); im=im.convert("RGB")
im.save(O+"2c.jpg",quality=92)
