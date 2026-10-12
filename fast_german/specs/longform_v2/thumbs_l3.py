"""A/B thumbnails for L3 (1280x720), v2 (user 2026-10-12: v1 rejected; Autobahn centre line must sit in the middle).
1a 3D Autobahn with an overhead motorway sign · 1b provocative (Hallo vs Moin/Servus/Na?, red circle + arrow) · 1c real photo."""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "lib"))
import common as C, short_v2 as S
S.use_road_theme()
OUT = "/mnt/project-files/fast_german/upload/L3_greetings/"
W, H = 1280, 720
Y, WH, RED, GREEN = (255, 204, 0), (255, 255, 255), (230, 40, 45), (52, 199, 89)
SIGN_BLUE = (0, 84, 166)
BAR = "/mnt/project-files/fonts/de/BarlowCondensed-Black.ttf"


def bar(size):
    return ImageFont.truetype(BAR, size)


def road3d(hz=300, sky_top=(18, 40, 92), sky_bot=(255, 150, 70), seed=3):
    """Perspective Autobahn at dusk: vanishing point dead centre, dashed centre line on the vertical midline."""
    rng = np.random.default_rng(seed)
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    img = np.zeros((H, W, 3), np.float32)
    t = np.clip(y / hz, 0, 1)[..., None]
    img[:] = np.array(sky_top) * (1 - t) + np.array(sky_bot) * t
    g = y > hz
    z = 520.0 / np.maximum(y - hz, 1)                      # depth
    xw = (x - W / 2) * z / 100                               # world x in metres-ish
    asph = 58 + rng.normal(0, 7, (H, W))                     # fine grain
    road = np.abs(xw) < 7.5
    col = np.stack([asph * 1.0, asph * 1.0, asph * 1.04], -1)
    # far shoulder: dark grass
    dk = np.clip((y - hz) / (H - hz), 0, 1)
    grass = np.stack([30 + 10 * dk, 44 + 20 * dk, 34 + 6 * dk], -1) + rng.normal(0, 4, (H, W))[..., None]
    base = np.where(road[..., None], col, grass)
    paint = (np.abs(np.abs(xw) - 7.1) < 0.18) | ((np.abs(xw) < 0.16) & ((z * 0.9) % 6 < 3.2))   # edges + centre dashes
    base = np.where(paint[..., None], 235, base)
    fog = np.clip(1 - (y - hz) / 140, 0, 1)[..., None] * 0.75   # haze near the horizon
    base = base * (1 - fog) + np.array(sky_bot) * 0.55 * fog
    img = np.where(g[..., None], base, img)
    sun = np.exp(-(((x - W / 2) / 260) ** 2 + ((y - hz) / 120) ** 2))[..., None]     # glow at the vanishing point
    img = img + sun * np.array([255, 190, 110]) * 0.55
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert("RGBA")
    vig = Image.new("L", (W, H), 0)
    ImageDraw.Draw(vig).ellipse((-300, -250, W + 300, H + 250), fill=255)
    dark = Image.new("RGBA", (W, H), (0, 0, 0, 150))
    dark.putalpha(Image.eval(vig.filter(ImageFilter.GaussianBlur(120)), lambda v: int((255 - v) * 0.7)))
    im.alpha_composite(dark)
    return im


def put(im, el, x, y, anchor="mm"):
    dx = {"l": 0, "m": el.width // 2, "r": el.width}[anchor[0]]
    dy = {"t": 0, "m": el.height // 2, "b": el.height}[anchor[1]]
    im.alpha_composite(el, (int(x - dx), int(y - dy)))


def word(t, size, col=WH, stroke=12):
    return S.shadow(S.text_im(t, S.de_font(size), col, stroke=stroke), 18, 170, 10)


def emoji(name, s):
    return S.shadow(C.icon(name, s), 24, 170, 14)


def sign(lines, w, pad=26, fill=SIGN_BLUE):
    """German motorway sign: blue board, white rim, DIN-style condensed caps."""
    ims = []
    for t, sz, col in lines:
        while bar(sz).getlength(t) > w - 2 * pad - 30:
            sz -= 4
        ims.append(S.text_im(t, bar(sz), col, stroke=0))
    h = sum(i.height for i in ims) + pad * 2 + 10 * (len(ims) - 1)
    b = Image.new("RGBA", (w, h))
    d = ImageDraw.Draw(b)
    d.rounded_rectangle((0, 0, w - 1, h - 1), 26, fill=(255, 255, 255, 255))
    d.rounded_rectangle((9, 9, w - 10, h - 10), 20, fill=fill + (255,))
    yy = pad
    for i in ims:
        b.alpha_composite(i, ((w - i.width) // 2, yy)); yy += i.height + 10
    return S.shadow(b, 24, 190, 16)


def posts(im, x0, x1, top):
    d = ImageDraw.Draw(im)
    for x in (x0, x1):
        d.rectangle((x - 9, top, x + 9, 360), fill=(70, 74, 82, 255))


def pretzel(im, x=78, y=70):
    put(im, S.shadow(C.icon("pretzel", 110), 12, 170, 6), x, y)


# ---------- 1a: 3D Autobahn, overhead sign "50 GERMAN PHRASES", waving hand + "in 10 min" sign
im = road3d()
posts(im, 190, 1090, 200)
sg = sign([("50 GERMAN PHRASES", 170, WH), ("YOU'LL ACTUALLY USE", 70, Y)], 1120)
put(im, sg, W / 2, 175)
put(im, emoji("waving-hand-default", 360), 200, 545)
tag = sign([("in 10 min", 84, (20, 20, 20))], 330, pad=14, fill=Y)
put(im, tag, 1080, 590)

im.convert("RGB").save(OUT + "1a.jpg", quality=93)

# ---------- 1b: provocative. Left lane: Hallo, circled red + "STOP". Right lane: Moin / Servus / Na? with a check
im = road3d(sky_top=(40, 10, 30), sky_bot=(255, 90, 60), seed=5)
put(im, word("STOP saying only", 96), W / 2, 80)
put(im, word("Hallo", 190), 330, 330)
d = ImageDraw.Draw(im)
d.ellipse((70, 215, 590, 450), outline=RED + (255,), width=16)
d.line((80, 440, 580, 225), fill=RED + (255,), width=16)        # struck through
for t, yy in [("Moin!", 250), ("Servus!", 385), ("Na?", 520)]:
    put(im, word(t, 120, Y), 990, yy)
d.line((610, 330, 760, 330), fill=RED + (255,), width=22)
d.polygon([(810, 330), (750, 290), (750, 370)], fill=RED + (255,))
put(im, emoji("face-screaming-in-fear", 210), 330, 590)
put(im, emoji("check-mark-button", 120), 1190, 640)
pretzel(im, 78, 70)
im.convert("RGB").save(OUT + "1b.jpg", quality=93)

# ---------- 1c: real photo, Brandenburg Gate at sunset
ph = S.cover("/mnt/project-files/fast_german/cache/photos/brandenburg_1.jpg", W, H, (0.5, 0.6)).convert("RGBA")
ph = Image.blend(ph, Image.new("RGBA", (W, H), (0, 0, 0, 255)), 0.15)
grad = np.zeros((H, W, 4), np.uint8)
grad[..., 3] = (np.clip(1 - np.linspace(0, 1.3, H), 0, 1) * 170).astype(np.uint8)[:, None]   # dark top for the text
ph.alpha_composite(Image.fromarray(grad))
put(ph, word("Speak German", 150), W / 2, 110)
hl = Image.new("RGBA", (760, 130))
ImageDraw.Draw(hl).rounded_rectangle((0, 0, 759, 129), 24, fill=Y + (255,))
hl.alpha_composite(S.text_im("in 10 minutes", S.de_font(100), (20, 20, 20), stroke=0), (40, 8))
put(ph, S.shadow(hl, 20, 170, 10), W / 2, 265)
put(ph, emoji("waving-hand-default", 260), 1110, 560)
put(ph, word("Hallo!", 120), 210, 600)
pretzel(ph, 70, 60)
ph.convert("RGB").save(OUT + "1c.jpg", quality=93)
