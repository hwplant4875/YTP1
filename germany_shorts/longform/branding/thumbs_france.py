# STRATA long-form 2 (France 2026 lycée protests): A/B/C thumbnails, 1280x720.
#   2a: 3D map frame (map_tour render) with the country lit up, "1 SCHOOL -> 1,000"
#   2b: provocative: real photo (Perpignan, police vs. pupils with the tricolour), red ring + arrow
#   2c: edited real photo: "NES POUR BRILLER PAS POUR ETRE NEGLIGES" banner (Paris, 6 Oct)
# usage: python3 thumbs_france.py <out dir>
import sys, os, glob, math, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageEnhance

EP = "/home/user/YTP1/germany_shorts/longform/episodes/02_france_protests"
FONT = "/home/user/YTP1/germany_shorts/fonts/YouTubeSans-Black.otf"
OUT = sys.argv[1] if len(sys.argv) > 1 else "."
W, H = 1280, 720
WHITE, BLUE, RED = (255, 255, 255), (38, 110, 255), (239, 35, 50)
F = lambda s: ImageFont.truetype(FONT, s)


def fit(im, centering=(0.5, 0.5)):
    return ImageOps.fit(im.convert("RGB"), (W, H), Image.LANCZOS, centering=centering)


def shade(im, box, alpha, side):
    """dark gradient over box, strongest at `side` ('l','r','t','b'), fading inward"""
    m = Image.new("L", (W, H), 0); d = ImageDraw.Draw(m)
    x0, y0, x1, y1 = box
    n = (x1 - x0) if side in "lr" else (y1 - y0)
    for i in range(n):
        v = int(alpha * (1 - i / n) ** 1.3)
        if side == "l": d.line([(x0 + i, y0), (x0 + i, y1)], fill=v)
        if side == "r": d.line([(x1 - i, y0), (x1 - i, y1)], fill=v)
        if side == "t": d.line([(x0, y0 + i), (x1, y0 + i)], fill=v)
        if side == "b": d.line([(x0, y1 - i), (x1, y1 - i)], fill=v)
    return Image.composite(Image.new("RGB", (W, H), (0, 0, 0)), im, m)


def text(im, xy, s, size, fill, anchor="la", stroke=10, shadow=True):
    if shadow:  # soft drop shadow so the black stroke separates from busy backgrounds
        sh = Image.new("L", (W, H), 0)
        ImageDraw.Draw(sh).text((xy[0] + 6, xy[1] + 8), s, font=F(size), fill=200, anchor=anchor, stroke_width=stroke + 4)
        im = Image.composite(Image.new("RGB", (W, H), (0, 0, 0)), im, sh.filter(ImageFilter.GaussianBlur(10)))
    ImageDraw.Draw(im).text(xy, s, font=F(size), fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=(0, 0, 0))
    return im


def glow_layer(im, draw_fn, blur=10, strength=0.9):
    halo = Image.new("L", (W, H), 0); draw_fn(ImageDraw.Draw(halo), 255, extra=10)
    halo = halo.filter(ImageFilter.GaussianBlur(blur)).point(lambda v: int(v * strength))
    im = Image.composite(Image.new("RGB", (W, H), (0, 0, 0)), im, halo)
    draw_fn(ImageDraw.Draw(im), RED, extra=0); return im


def ring(cx, cy, rx, ry, w=12):
    def fn(d, col, extra=0):
        d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], outline=col, width=w + extra)
    return fn


def arrow(x0, y0, x1, y1, w=18, head=50, bend=40):
    """curved arrow; the shaft is stamped with discs so it stays smooth at any width"""
    def fn(d, col, extra=0):
        a = math.atan2(y1 - y0, x1 - x0)
        bx, by = x1 - head * 0.7 * math.cos(a), y1 - head * 0.7 * math.sin(a)
        mx, my = (x0 + bx) / 2 - math.sin(a) * bend, (y0 + by) / 2 + math.cos(a) * bend
        pts = [((1 - t) ** 2 * x0 + 2 * (1 - t) * t * mx + t * t * bx, (1 - t) ** 2 * y0 + 2 * (1 - t) * t * my + t * t * by)
               for t in [i / 120 for i in range(121)]]
        r = (w + extra) / 2
        for x, y in pts: d.ellipse([x - r, y - r, x + r, y + r], fill=col)
        a2 = math.atan2(by - pts[-6][1], bx - pts[-6][0])
        tip = (bx + (head * 0.7 + extra) * math.cos(a2), by + (head * 0.7 + extra) * math.sin(a2))
        p = [tip]
        for s in (-1, 1): p.append((tip[0] - (head + 2 * extra) * math.cos(a2 + s * 0.55), tip[1] - (head + 2 * extra) * math.sin(a2 + s * 0.55)))
        d.polygon(p, fill=col)
    return fn


def tricolour(im, x, y, w=150, h=14):
    d = ImageDraw.Draw(im)
    d.rectangle([x - 3, y - 3, x + w + 3, y + h + 3], fill=(0, 0, 0))
    for i, c in enumerate([(0, 85, 164), WHITE, RED]):
        d.rectangle([x + i * w // 3, y, x + (i + 1) * w // 3, y + h], fill=c)


def boost(im, b=1.0, c=1.0, s=1.0):
    return ImageEnhance.Color(ImageEnhance.Contrast(ImageEnhance.Brightness(im).enhance(b)).enhance(c)).enhance(s)


os.makedirs(OUT, exist_ok=True)

# ---- 2a: 3D map, France lit up (frame 9 s of the recoloured map_tour render)
frame = os.path.join(OUT, "_map_tour_9s.png")
src = glob.glob(f"{EP}/cache/3d_france_map_tour*.mp4")[0]
subprocess.run(["ffmpeg", "-v", "0", "-y", "-ss", "9", "-i", src, "-frames:v", "1", frame], check=True)
im = Image.open(frame).convert("RGB").resize((1460, 821), Image.LANCZOS).crop((40, 40, 40 + W, 40 + H))
# cool night grade: shadows pushed to navy, lights stay white
r, g, b = im.split()
im = Image.merge("RGB", (r.point(lambda v: int(v * 0.86)), g.point(lambda v: int(v * 0.93)), b.point(lambda v: min(255, int(v * 1.12 + 10)))))
im = boost(im, 1.25, 1.2)
# red origin glow on Paris / Creteil, where it started
glow = Image.new("L", (W, H), 0); ImageDraw.Draw(glow).ellipse([680 - 70, 160 - 70, 680 + 70, 160 + 70], fill=255)
im = Image.composite(Image.new("RGB", (W, H), RED), im, glow.filter(ImageFilter.GaussianBlur(38)).point(lambda v: int(v * 0.75)))
im = shade(im, (0, 0, 640, H), 245, "l")
im = text(im, (52, 70), "1 SCHOOL", 118, WHITE, stroke=10)
im = glow_layer(im, arrow(150, 215, 175, 395, w=22, head=62, bend=30))
im = text(im, (40, 395), "1,000", 250, RED, stroke=13)
tricolour(im, 300, 680, 210, 16)
im.save(f"{OUT}/2a.jpg", quality=92)
os.remove(frame)

# ---- 2b: provocative: riot police facing pupils carrying the tricolour (Perpignan, 2 Oct)
p = f"{EP}/sources/photos/best/Journée_de_mobilisation_des_lycéens_à_Perpignan_14.jpg"
im = Image.open(p).convert("RGB")
im = im.crop((0, 0, im.width, im.height))  # full frame, 16:9 already
im = boost(fit(im, (0.5, 0.6)), 1.0, 1.15, 1.1)
im = shade(im, (0, 0, W, 300), 235, "t")
im = text(im, (W // 2, 22), "POLICE vs. TEENS", 130, WHITE, "ma", 11)
ImageDraw.Draw(im)
# ring the pupils with the flag, arrow from the riot officer toward them
im = glow_layer(im, ring(690, 420, 175, 150, w=13))
im = glow_layer(im, arrow(330, 530, 505, 455, w=22, head=60, bend=-35))
im.save(f"{OUT}/2b.jpg", quality=92)

# ---- 2c: edited real photo: the "born to shine, not to be neglected" banner (Paris, 6 Oct)
p = f"{EP}/sources/photos/best/Manifestation_lycéenne_du_6_octobre_2026_à_Paris_63.jpg"
im = Image.open(p).convert("RGB")
w0, h0 = im.size
x0 = 0; cw = w0; ch = int(cw * 9 / 16); y0 = int(h0 * 0.10)  # keep the whole banner, NEGLIGES included
im = im.crop((x0, y0, x0 + cw, y0 + ch))
im = boost(fit(im), 1.02, 1.2, 1.15)
im = shade(im, (600, 0, W, H), 235, "r")
im = text(im, (W - 36, 120), "SO THEY", 104, WHITE, "ra", 10)
im = text(im, (W - 36, 240), "REVOLTED", 116, BLUE, "ra", 12)
d = ImageDraw.Draw(im)
for i, line in enumerate(['"BORN TO SHINE,', 'NOT TO BE NEGLECTED"']):
    im = text(im, (W - 40, 410 + i * 54), line, 42, WHITE, "ra", 6, shadow=False)
tricolour(im, W - 250, 540, 210, 18)
im.save(f"{OUT}/2c.jpg", quality=92)

# ---- compare sheet
ims = [Image.open(f"{OUT}/2{k}.jpg") for k in "abc"]
sheet = Image.new("RGB", (3 * 426 + 4 * 10, 240 + 20 + 40), (24, 24, 24)); d = ImageDraw.Draw(sheet)
for i, t in enumerate(ims):
    sheet.paste(t.resize((426, 240), Image.LANCZOS), (10 + i * 436, 10))
    d.text((10 + i * 436 + 213, 262), "2" + "abc"[i], font=F(28), fill=WHITE, anchor="ma")
sheet.save(f"{OUT}/2_compare.jpg", quality=88)
for k in "abc": print(k, os.path.getsize(f"{OUT}/2{k}.jpg") // 1024, "KB")
