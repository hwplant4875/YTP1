"""STRATA profile v3: an extremely right-angled S (a mirrored Hangul ㄹ), built from strata bars, one amber seam.
Writes variants A/B/C at 800x800 plus a size-check sheet."""
import os
from PIL import Image, ImageDraw, ImageFilter

OUT = "/mnt/project-files/plans/fineprint/branding/strata"
S = 3200
BG = (10, 10, 12)
CREAM = (236, 230, 218)
AMBER = (255, 166, 74)


def geom(w=0.50, h=0.56, t=0.135):
    W, H, T = w * S, h * S, t * S
    g = (H - 3 * T) / 2
    x0, y0 = (S - W) / 2, (S - H) / 2
    x1 = x0 + W
    ym = y0 + T + g                 # top of middle bar
    yb = ym + T + g                 # top of bottom bar
    return dict(W=W, H=H, T=T, g=g, x0=x0, y0=y0, x1=x1, ym=ym, yb=yb)


def glow(img, mask, col, radius, amount):
    gm = mask.filter(ImageFilter.GaussianBlur(radius)).point(lambda v: int(min(255, v * amount)))
    return Image.composite(Image.new("RGB", img.size, col), img, gm)


def base():
    img = Image.new("RGB", (S, S), BG)
    halo = Image.new("L", (S, S), 0)
    ImageDraw.Draw(halo).ellipse((S * 0.2, S * 0.2, S * 0.8, S * 0.8), fill=36)
    return Image.composite(Image.new("RGB", (S, S), (44, 28, 14)), img, halo.filter(ImageFilter.GaussianBlur(S * 0.1)))


def variant_a():
    """solid right-angled S, cream, middle bar amber (the glowing stratum)"""
    k = geom(); img = base(); m = Image.new("L", (S, S), 0); a = Image.new("L", (S, S), 0)
    d, da = ImageDraw.Draw(m), ImageDraw.Draw(a)
    x0, x1, y0, ym, yb, T = k["x0"], k["x1"], k["y0"], k["ym"], k["yb"], k["T"]
    d.rectangle((x0, y0, x1, y0 + T), fill=255)                 # top bar
    d.rectangle((x0, y0, x0 + T, ym), fill=255)                 # left upright
    d.rectangle((x1 - T, ym + T, x1, yb + T), fill=255)         # right upright
    d.rectangle((x0, yb, x1, yb + T), fill=255)                 # bottom bar
    da.rectangle((x0, ym, x1, ym + T), fill=255)                # full middle bar = the amber stratum
    img.paste(Image.new("RGB", (S, S), CREAM), (0, 0), m)
    img = glow(img, a, AMBER, S * 0.03, 0.9)
    img.paste(Image.new("RGB", (S, S), AMBER), (0, 0), a)
    return img


def variant_b():
    """the S as stacked strata: every bar split into thin layers, cream tones stepping down, amber middle layer"""
    k = geom(); img = base()
    x0, x1, y0, ym, yb, T = k["x0"], k["x1"], k["y0"], k["ym"], k["yb"], k["T"]
    m = Image.new("L", (S, S), 0); d = ImageDraw.Draw(m)
    d.rectangle((x0, y0, x1, y0 + T), fill=255); d.rectangle((x0, y0, x0 + T, ym + T), fill=255)
    d.rectangle((x0, ym, x1, ym + T), fill=255)
    d.rectangle((x1 - T, ym, x1, yb + T), fill=255); d.rectangle((x0, yb, x1, yb + T), fill=255)
    n, gap = 9, S * 0.012                                       # horizontal strata through the whole letter
    top, bot = y0, yb + T
    band = (bot - top) / n
    am = Image.new("L", (S, S), 0)
    for i in range(n):
        a, b = top + i * band + (gap / 2 if i else 0), top + (i + 1) * band - (gap / 2 if i < n - 1 else 0)
        stripe = Image.new("L", (S, S), 0); ImageDraw.Draw(stripe).rectangle((0, a, S, b), fill=255)
        part = Image.composite(m, Image.new("L", (S, S), 0), stripe)
        if i == n // 2:
            am = part; col = AMBER
        else:
            v = 238 - abs(i - n // 2) * 14
            col = (v, v - 6, v - 16)
        img.paste(Image.new("RGB", (S, S), col), (0, 0), part)
    img = glow(img, am, AMBER, S * 0.03, 0.8)
    img.paste(Image.new("RGB", (S, S), AMBER), (0, 0), am)
    return img


def variant_c():
    """right-angled S cut into three slabs along its bars; the slabs slip like a fault, amber light in the cuts"""
    k = geom(); img = base()
    x0, x1, y0, ym, yb, T, g = k["x0"], k["x1"], k["y0"], k["ym"], k["yb"], k["T"], k["g"]
    cut = S * 0.014; slip = S * 0.022
    slabs = [  # (rects, dx)
        ([(x0, y0, x1, y0 + T), (x0, y0 + T, x0 + T, ym - cut / 2)], -slip),
        ([(x0, ym + cut / 2, x1, ym + T - cut / 2)], 0),
        ([(x1 - T, ym + T + cut / 2, x1, yb), (x0, yb, x1, yb + T)], slip),
    ]
    seams = Image.new("L", (S, S), 0); ds = ImageDraw.Draw(seams)
    ds.rectangle((x0 - slip, ym - cut / 2, x1 - slip * 0.2, ym + cut / 2), fill=255)
    ds.rectangle((x0 + slip * 0.2, ym + T - cut / 2, x1 + slip, ym + T + cut / 2), fill=255)
    img = glow(img, seams, AMBER, S * 0.02, 1.0)
    img.paste(Image.new("RGB", (S, S), AMBER), (0, 0), seams)
    for rects, dx in slabs:
        m = Image.new("L", (S, S), 0); d = ImageDraw.Draw(m)
        for r in rects:
            d.rectangle((r[0] + dx, r[1], r[2] + dx, r[3]), fill=255)
        img.paste(Image.new("RGB", (S, S), CREAM), (0, 0), m)
    return img


def circle(im, size):
    im = im.resize((size, size), Image.LANCZOS)
    c = Image.new("L", (size, size), 0); ImageDraw.Draw(c).ellipse((0, 0, size - 1, size - 1), fill=255)
    out = Image.new("RGB", (size, size), (255, 255, 255)); out.paste(im, (0, 0), c); return out


sheet = Image.new("RGB", (3 * 520 + 40, 520 + 160), (255, 255, 255))
for i, (name, fn) in enumerate([("A", variant_a), ("B", variant_b), ("C", variant_c)]):
    im = fn()
    im.resize((800, 800), Image.LANCZOS).save(os.path.join(OUT, f"profile_strata_sq_{name}.png"))
    sheet.paste(circle(im, 480), (20 + i * 520, 20))
    for j, sz in enumerate([88, 48, 32]):          # how it reads in comments / sidebar
        sheet.paste(circle(im, sz), (20 + i * 520 + j * 110, 520))
sheet.save(os.path.join(OUT, "profile_strata_sq_compare.jpg"), quality=92)
