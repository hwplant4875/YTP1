# A/B thumbnail variants (b: provocative red markup on a 3D frame, c: edited archive photo).
# usage: python3 thumbs_ab.py <scratch dir with bg1b.png bg2b.png> <out dir>
import sys, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageEnhance
SRC, OUT = sys.argv[1], sys.argv[2]
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
im = fit(Image.open(f"{SRC}/bg1b.png"))
im = ImageEnhance.Brightness(im).enhance(1.15)
im = Image.new("RGB", (W, H)); im.paste(src := fit(Image.open(f"{SRC}/bg1b.png")).crop((0, 140, W, H)), (0, 0))
im = ImageEnhance.Brightness(im).enhance(1.15)
im = shade(im, (0, 380, W, H), 255, "b"); im = shade(im, (0, 0, W, 130), 200, "t")
d = ImageDraw.Draw(im)
text(d, (W // 2, 455), "TRAINS", 120, CREAM, "ma")
text(d, (W // 2, 575), "NEVER STOPPED", 118, RED, "ma")
for fn in (ring(572, 265, 62, 92), arrow(760, 120, 640, 205)):
    im = glow_layer(im, fn)
label(im, (775, 105), "ARMED GUARD", 36, "lm")
label(im, (40, 60), "WEST BERLIN TRAIN", 36)
im = glow_layer(im, arrow(150, 105, 120, 215))
im.save(f"{OUT}/1b.jpg", quality=93)

# ---- 1c: Rosenthaler Platz ghost station, photographed just before reopening (Dec 1989)
ph = Image.open(f"{EP}/01_ghost_stations/assets/c03.jpg").convert("L")
ph = ImageOps.autocontrast(ph, cutoff=1)
ph = ImageOps.colorize(ph, (8, 10, 14), (236, 230, 214), mid=(110, 104, 94))
im = ImageOps.fit(ph, (W, H), Image.LANCZOS, centering=(0.5, 0.15))
im = ImageEnhance.Contrast(im).enhance(1.1)
im = shade(im, (0, 330, W, H), 245, "b"); im = shade(im, (0, 0, W, 200), 120, "t")
d = ImageDraw.Draw(im)
text(d, (60, 455), "SEALED FOR", 92, CREAM)
text(d, (52, 545), "28 YEARS", 160, AMBER)
im.save(f"{OUT}/1c.jpg", quality=93)

# ---- 2b: the NBC camera filming inside the tunnel
im = fit(Image.open(f"{SRC}/bg2b.png"))
im = shade(im, (700, 0, W, H), 230, "r")
d = ImageDraw.Draw(im)
text(d, (1245, 60), "TV PAID", 112, CREAM, "ra")
text(d, (1245, 175), "FOR THIS", 112, CREAM, "ra")
text(d, (1245, 290), "TUNNEL", 112, RED, "ra")
for fn in (ring(637, 285, 95, 120), arrow(1000, 575, 735, 380)):
    im = glow_layer(im, fn)
label(im, (1240, 600), "NBC, 1962", 40, "ra")
im.save(f"{OUT}/2b.jpg", quality=93)

# ---- 2c: Bernauer Str./Gartenstraße, June 1962, with the tunnel drawn underneath
ph = Image.open(f"{EP}/02_tunnel29/assets/t09.jpg").convert("L")
ph = ImageOps.autocontrast(ph, cutoff=2)
ph = ImageOps.colorize(ph, (6, 8, 12), (225, 220, 205), mid=(96, 92, 86))
GY = 545                                        # street level in the thumbnail
ph = ph.resize((W, round(ph.height * W / ph.width)), Image.LANCZOS)   # 1280 x 892
im = Image.new("RGB", (W, H)); im.paste(ph.crop((0, 170, W, 170 + GY)), (0, 0))
im = shade(im, (0, 0, W, 300), 170, "t")
# soil cut below the street: strata, then a glowing tunnel
import numpy as np, random
random.seed(3)
soil = Image.new("RGB", (W, H - GY)); sd = ImageDraw.Draw(soil)
for y in range(H - GY): t = y / (H - GY); sd.line([(0, y), (W, y)], fill=(int(70 - 40 * t), int(52 - 30 * t), int(36 - 20 * t)))
for _ in range(5000): x, y = random.randrange(W), random.randrange(H - GY); c = random.choice([(20, 14, 10), (110, 88, 62)]); sd.point((x, y), fill=c)
for k in range(3): yy = 30 + k * 45; sd.line([(0, yy), (W, yy + random.randint(-6, 6))], fill=(30, 22, 16), width=2)
im.paste(soil, (0, GY))
d = ImageDraw.Draw(im); d.line([(0, GY), (W, GY)], fill=(15, 12, 10), width=4)
ty = GY + 100
glow = Image.new("RGB", (W, H)); g = ImageDraw.Draw(glow)
g.rectangle([0, ty - 18, W, ty + 18], fill=(70, 38, 10))
for x in range(30, W, 110): g.ellipse([x - 8, ty - 8, x + 8, ty + 8], fill=AMBER)
glow = np.asarray(glow, dtype="int16") + np.asarray(glow.filter(ImageFilter.GaussianBlur(16)), dtype="int16") * 2
im = Image.fromarray(np.clip(np.asarray(im, dtype="int16") + glow, 0, 255).astype("uint8"))
d = ImageDraw.Draw(im)
text(d, (50, 30), "THEY DUG", 112, CREAM, stroke=3, sf=(20, 20, 20))
text(d, (50, 145), "UNDER THIS", 112, AMBER, stroke=3, sf=(20, 20, 20))
label(im, (W - 40, ty + 60), "TUNNEL 29 · 1962", 32, "rm")
im.save(f"{OUT}/2c.jpg", quality=93)
