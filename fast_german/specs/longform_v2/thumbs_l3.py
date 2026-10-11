"""A/B thumbnails for L3 (1280x720): 1a clean 3D-style emoji, 1b provocative (red circle + arrow), 1c real photo."""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "lib"))
import common as C, road_loop as RL, short_v2 as S
S.use_road_theme()
OUT = "/mnt/project-files/fast_german/upload/L3_greetings/"
W, H = 1280, 720
Y, WH, RED = (255, 204, 0), (250, 250, 246), (229, 45, 50)


def road():
    tex = np.roll(RL.strip(W, H, tracks=False)[:H, :W], 590, axis=1)   # lane line to the right edge, away from the text
    return Image.fromarray(tex.astype(np.uint8)).convert("RGBA")


def word(t, size, col=WH):
    return S.shadow(S.text_im(t, S.de_font(size), col, stroke=12), 18, 150, 10)


def emoji(name, s):
    return S.shadow(C.icon(name, s), 24, 150, 14)


def put(im, el, x, y, anchor="mm"):
    dx = {"l": 0, "m": el.width // 2, "r": el.width}[anchor[0]]
    dy = {"t": 0, "m": el.height // 2, "b": el.height}[anchor[1]]
    im.alpha_composite(el, (int(x - dx), int(y - dy)))


def pretzel(im):
    put(im, S.shadow(C.icon("pretzel", 120), 12, 140, 6), 85, 75)


# 1a: big waving hand + "50 German phrases" + three greetings as chips
im = road()
put(im, emoji("waving-hand-default", 430), 1010, 380)
put(im, word("50", 260, Y), 70, 250, "lm")
put(im, word("German", 150), 70, 420, "lm")
put(im, word("phrases", 150), 70, 560, "lm")
pretzel(im)
im.convert("RGB").save(OUT + "1a.jpg", quality=92)

# 1b: "Stop saying only HALLO" with the red circle around Hallo and an arrow to the alternatives
im = road()
put(im, word("STOP saying", 110), 660, 110)
put(im, word("only", 90, Y), 660, 215)
put(im, word("Hallo", 210), 380, 400)
d = ImageDraw.Draw(im)
d.ellipse((120, 290, 650, 520), outline=RED + (255,), width=14)
for i, (t, yy) in enumerate([("Moin", 330), ("Servus", 450), ("Na?", 570)]):
    put(im, word(t, 110, Y), 1010, yy)
d.line((680, 420, 820, 420), fill=RED + (255,), width=18)
d.polygon([(860, 420), (810, 385), (810, 455)], fill=RED + (255,))
put(im, emoji("face-with-open-mouth", 150), 230, 610)
pretzel(im)
im.convert("RGB").save(OUT + "1b.jpg", quality=92)

# 1c: real Berlin photo, darkened on the left for the text
ph = S.cover("/mnt/project-files/fast_german/cache/photos/berlin_2.jpg", W, H, (0.6, 0.5)).convert("RGBA")
grad = np.zeros((H, W, 4), np.uint8)
grad[..., 3] = (np.clip(1 - np.linspace(0, 1.4, W), 0, 1) * 200).astype(np.uint8)[None, :]
ph.alpha_composite(Image.fromarray(grad))
put(ph, word("Speak", 150), 60, 210, "lm")
put(ph, word("German", 150), 60, 360, "lm")
put(ph, word("in 10 minutes", 100, Y), 60, 500, "lm")
put(ph, emoji("waving-hand-default", 240), 1090, 560)
pretzel(ph)
ph.convert("RGB").save(OUT + "1c.jpg", quality=92)
