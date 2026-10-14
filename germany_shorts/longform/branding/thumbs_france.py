# STRATA long-form 2 (France 2026 lycée protests): A/B/C thumbnails, 1280x720.
# Rebuilt after a benchmark of Neo, Vox, Johnny Harris, Wendover, PolyMatter, RealLifeLore,
# Economics Explained, VICE News and DW (see upload/2_france_protests/benchmark.md):
# one real photo carries the thumbnail, 0-3 words, one accent colour, no flag stripes.
#   2a  provocative (v3): two lycéens in smoke around a smouldering bin, "TEEN REVOLT" (REVOLT red).
#       (v2 was the Paris crowd + barricade with "1,000 SCHOOLS"; the user found it not provocative enough.)
#   2b  provocative: Perpignan, 2 Oct: riot police in green tear gas facing masked pupils with
#       raised hands. Hand-drawn red ring on the pupils, "POLICE vs. TEENS" (Wendover/VICE style).
#   2c  real photo, different angle: Lycée Jacques-Decour, Paris: the school door walled off with
#       wheelie bins, pupils sitting on them. A cardboard placard: "WE SHUT IT DOWN".
# Photos: Wikimedia Commons (Camille Hestaux CC0, Aurelio Cárdenas CC BY 4.0, Wyslijp16 CC BY 4.0).
# usage: python3 thumbs_france.py <out dir>
import sys, os, math, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageEnhance, ImageChops

EP = "/home/user/YTP1/germany_shorts/longform/episodes/02_france_protests"
RAW = f"{EP}/sources/photos/raw"
FD = "/home/user/YTP1/germany_shorts/fonts"
ANTON = f"{FD}/Anton-Regular.ttf"                     # condensed headline (OFL)
MARKER = f"{FD}/PermanentMarker-Regular.ttf"          # placard handwriting (Apache 2.0)
CLEAN = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
OUT = sys.argv[1] if len(sys.argv) > 1 else "."
W, H = 1280, 720
WHITE, RED = (255, 255, 255), (232, 30, 40)
F = lambda path, s: ImageFont.truetype(path, s)


def load(name):
    return ImageOps.exif_transpose(Image.open(f"{RAW}/{name}")).convert("RGB")


def crop16(im, x0, y0, w):
    """crop a 16:9 window (x0, y0, width w in source px) and scale to 1280x720"""
    h = round(w * 9 / 16)
    return im.crop((x0, y0, x0 + w, y0 + h)).resize((W, H), Image.LANCZOS)


def grade(im, b=1.0, c=1.0, s=1.0, sharp=0):
    im = ImageEnhance.Color(ImageEnhance.Contrast(ImageEnhance.Brightness(im).enhance(b)).enhance(c)).enhance(s)
    return im.filter(ImageFilter.UnsharpMask(2, sharp, 2)) if sharp else im


def vignette(im, strength=0.45, power=2.2):
    m = Image.new("L", (W, H)); px = m.load()
    for y in range(0, H, 4):
        for x in range(0, W, 4):
            d = math.hypot((x - W / 2) / (W / 2), (y - H / 2) / (H / 2)) / math.sqrt(2)
            v = int(255 * strength * min(1, d ** power * 1.6))
            for dy in range(4):
                for dx in range(4): px[x + dx, y + dy] = v
    return Image.composite(Image.new("RGB", (W, H)), im, m.filter(ImageFilter.GaussianBlur(30)))


def gradient(im, side, size, alpha):
    """darken from one edge, fading inward ('t','b','l','r')"""
    m = Image.new("L", (W, H), 0); d = ImageDraw.Draw(m)
    for i in range(size):
        v = int(alpha * (1 - i / size) ** 1.6)
        if side == "t": d.line([(0, i), (W, i)], fill=v)
        if side == "b": d.line([(0, H - 1 - i), (W, H - 1 - i)], fill=v)
        if side == "l": d.line([(i, 0), (i, H)], fill=v)
        if side == "r": d.line([(W - 1 - i, 0), (W - 1 - i, H)], fill=v)
    return Image.composite(Image.new("RGB", (W, H)), im, m)


def soft_text(im, xy, s, font, fill=WHITE, anchor="la", shadow=170, blur=14, off=(0, 6), stroke=0):
    """text with a soft drop shadow only (no hard outline): the clean Neo/DW look"""
    sh = Image.new("L", (W, H), 0)
    ImageDraw.Draw(sh).text((xy[0] + off[0], xy[1] + off[1]), s, font=font, fill=shadow, anchor=anchor,
                            stroke_width=stroke + 6)
    im = Image.composite(Image.new("RGB", (W, H)), im, sh.filter(ImageFilter.GaussianBlur(blur)))
    ImageDraw.Draw(im).text(xy, s, font=font, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=(0, 0, 0))
    return im


def hand_ring(im, cx, cy, rx, ry, col=RED, w=11, turns=1.12, seed=3, tilt=-0.18):
    """marker-drawn ellipse: slightly over-rotated, wobbly, uneven pressure, with a dark halo"""
    rnd = random.Random(seed)
    ph = [rnd.uniform(0, 6.28) for _ in range(3)]
    pts = []
    n = 260
    for i in range(n + 1):
        t = i / n * turns * 2 * math.pi + 2.2
        wob = 1 + 0.035 * math.sin(3 * t + ph[0]) + 0.025 * math.sin(5 * t + ph[1])
        grow = 1 + 0.06 * i / n                       # second pass drifts outward, like a real stroke
        x, y = rx * wob * grow * math.cos(t), ry * wob * grow * math.sin(t)
        pts.append((cx + x * math.cos(tilt) - y * math.sin(tilt), cy + x * math.sin(tilt) + y * math.cos(tilt)))
    halo = Image.new("L", (W, H), 0); dh = ImageDraw.Draw(halo)
    for x, y in pts: dh.ellipse([x - w, y - w, x + w, y + w], fill=150)
    im = Image.composite(Image.new("RGB", (W, H)), im, halo.filter(ImageFilter.GaussianBlur(9)))
    d = ImageDraw.Draw(im)
    for i, (x, y) in enumerate(pts):
        r = w / 2 * (0.75 + 0.35 * math.sin(i / n * math.pi))   # thin start/end, full in the middle
        d.ellipse([x - r, y - r, x + r, y + r], fill=col)
    return im


def placard(lines, size, w, h, angle, seed=7):
    """a hand-lettered cardboard sign: corrugated brown board, torn edges, black marker, red underline"""
    rnd = random.Random(seed)
    pad = 40
    board = Image.new("RGBA", (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
    base = Image.new("RGB", (w, h), (196, 158, 108))
    # flute stripes + paper grain
    d = ImageDraw.Draw(base)
    for x in range(0, w, 9):
        d.line([(x, 0), (x, h)], fill=(188, 150, 101), width=3)
    noise = Image.effect_noise((w, h), 22).convert("L")
    base = Image.composite(Image.new("RGB", (w, h), (150, 112, 68)), base, noise.point(lambda v: int(max(0, v - 120) * 0.9)))
    base = ImageEnhance.Brightness(base).enhance(1.04)
    # torn outline
    poly = []
    for i in range(41): poly.append((i / 40 * w, rnd.uniform(0, 9)))
    for i in range(1, 24): poly.append((w - rnd.uniform(0, 9), i / 24 * h))
    for i in range(40, -1, -1): poly.append((i / 40 * w, h - rnd.uniform(0, 9)))
    for i in range(23, 0, -1): poly.append((rnd.uniform(0, 9), i / 24 * h))
    mask = Image.new("L", (w, h), 0); ImageDraw.Draw(mask).polygon(poly, fill=255)
    card = Image.new("RGBA", (w, h)); card.paste(base, (0, 0), mask)
    # marker text, centred line by line, each line nudged a little like handwriting
    dc = ImageDraw.Draw(card)
    font = F(MARKER, size)
    lh = size * 1.08
    y = h / 2 - lh * len(lines) / 2 + lh / 2 + 4
    for i, s in enumerate(lines):
        dc.text((w / 2 + rnd.uniform(-10, 10), y), s, font=font, fill=(18, 16, 16), anchor="mm")
        if i == len(lines) - 1:   # red marker underline under the last line
            tw = dc.textlength(s, font=font)
            x0, x1 = w / 2 - tw / 2 - 6, w / 2 + tw / 2 + 6
            yy = y + size * 0.55
            for k in range(60):
                t = k / 59
                xx = x0 + (x1 - x0) * t; yv = yy + 6 * math.sin(t * 3.2) - 4 * t
                dc.ellipse([xx - 7, yv - 6, xx + 7, yv + 6], fill=(205, 28, 36))
        y += lh
    board.paste(card, (pad, pad), card)
    board = board.rotate(angle, resample=Image.BICUBIC, expand=True)
    shadow = Image.new("RGBA", board.size, (0, 0, 0, 0))
    shadow.putalpha(board.getchannel("A").point(lambda v: int(v * 0.65)).filter(ImageFilter.GaussianBlur(14)))
    return board, shadow


def paste_rgba(im, layer, shadow, x, y, sh_off=(10, 16)):
    im = im.convert("RGBA")
    blk = Image.new("RGBA", shadow.size, (0, 0, 0, 255)); blk.putalpha(shadow.getchannel("A"))
    im.alpha_composite(blk, (x + sh_off[0], y + sh_off[1]))
    im.alpha_composite(layer, (x, y))
    return im.convert("RGB")


os.makedirs(OUT, exist_ok=True)

# ---- 2a (v3, provocative): two lycéens in a cloud of smoke around a smouldering wheelie bin
# (29 Sep, Camille Hestaux, CC0). Two words: "TEEN" white, "REVOLT" red (Wendover "RIOT" pattern).
im = load("Deux_lycéens_tentent_d_éteindre_une_poubelle.jpg")                          # 1920x2880 portrait
im = crop16(im, 0, 880, 1920)
im = grade(im, 0.98, 1.22, 1.08, sharp=80)
im = vignette(im, 0.5)
im = gradient(im, "t", 300, 215)
f = F(ANTON, 160)
tw = ImageDraw.Draw(im).textlength("TEEN REVOLT", font=f)
x0 = (W - tw) / 2
im = soft_text(im, (x0, 4), "TEEN", f, shadow=230, blur=12, off=(0, 6), stroke=3)
im = soft_text(im, (x0 + ImageDraw.Draw(im).textlength("TEEN ", font=f), 4), "REVOLT", f, fill=RED,
               shadow=230, blur=12, off=(0, 6), stroke=3)
im.save(f"{OUT}/2a.jpg", quality=92)

# ---- 2b: provocative. Riot police in green tear gas facing masked pupils with raised hands.
im = load("Journée_de_mobilisation_des_lycéens_à_Perpignan_05.jpg")                     # 3840x2163
im = crop16(im, 180, 40, 3540)
im = grade(im, 1.0, 1.18, 1.12, sharp=70)
im = vignette(im, 0.42)
im = gradient(im, "t", 260, 170)
im = hand_ring(im, 832, 392, 162, 196, w=12, tilt=-0.06)
f = F(ANTON, 132)
im = soft_text(im, (W // 2, 16), "POLICE vs. TEENS", f, anchor="ma", shadow=220, blur=12, off=(0, 5), stroke=3)
im.save(f"{OUT}/2b.jpg", quality=92)

# ---- 2c: the school door walled off with wheelie bins, pupils sitting on top.
im = load("2026_high_school_student_movement_and_blockades_at_Lycée_Jacques-Decour_in_Paris_03.jpg")  # 3840x2560
im = crop16(im, 420, 872, 3000)
im = grade(im, 1.0, 1.14, 1.1, sharp=60)
im = vignette(im, 0.38)
board, shadow = placard(["WE SHUT", "IT DOWN"], 100, 560, 310, 4, seed=11)
im = paste_rgba(im, board, shadow, 20, 6)
im.save(f"{OUT}/2c.jpg", quality=92)

# ---- compare sheet
ims = [Image.open(f"{OUT}/2{k}.jpg") for k in "abc"]
sheet = Image.new("RGB", (3 * 426 + 4 * 10, 240 + 20 + 40), (24, 24, 24)); d = ImageDraw.Draw(sheet)
for i, t in enumerate(ims):
    sheet.paste(t.resize((426, 240), Image.LANCZOS), (10 + i * 436, 10))
    d.text((10 + i * 436 + 213, 262), "2" + "abc"[i], font=F(CLEAN, 28), fill=WHITE, anchor="ma")
sheet.save(f"{OUT}/2_compare.jpg", quality=88)
for k in "abc": print(k, os.path.getsize(f"{OUT}/2{k}.jpg") // 1024, "KB")
