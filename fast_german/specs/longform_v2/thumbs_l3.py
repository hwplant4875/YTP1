"""A/B thumbnails for L3 (1280x720), v3 (user 2026-10-12: sunset 3D road scrapped; use the video's top-down asphalt with
the white lane line dead centre). Benchmarks (top German-lesson videos, 5-13M views): one character + speech bubble,
a huge level/number, 2-4 words in heavy type, bilingual pairs (Hello | Hallo), saturated colour blocks.
1a 3D character + "Hallo!" bubble + big 50 · 1b provocative Hallo ✗ vs Servus ✓ · 1c real photo card."""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "lib"))
import road_loop as RL, short_v2 as S
S.use_road_theme()
OUT = "/mnt/project-files/fast_german/upload/L3_greetings/"
E3 = "/mnt/project-files/fast_german/cache/emoji3d/"          # Microsoft Fluent 3D emoji (MIT)
W, H = 1280, 720
Y, WH, RED, GREEN, INK = (255, 204, 0), (255, 255, 255), (235, 45, 50), (40, 190, 80), (20, 20, 22)


def asphalt():
    """The video's background: plain top-down asphalt, dashed white centre line on x = W/2."""
    tex = RL.strip(W, H, tracks=False)[:H, :W]
    im = Image.fromarray(tex.astype(np.uint8)).convert("RGBA")
    v = Image.new("L", (W, H), 0)
    ImageDraw.Draw(v).ellipse((-200, -160, W + 200, H + 160), fill=255)
    dark = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dark.putalpha(Image.eval(v.filter(ImageFilter.GaussianBlur(110)), lambda a: int((255 - a) * 0.55)))
    im.alpha_composite(dark)
    return im


def e3(name, s):
    return S.shadow(Image.open(E3 + name + ".png").convert("RGBA").resize((s, s), Image.LANCZOS), 26, 190, 16)


def word(t, size, col=WH, stroke=14):
    return S.shadow(S.text_im(t, S.de_font(size), col, stroke=stroke, sfill=INK), 18, 200, 12)


def put(im, el, x, y, anchor="mm"):
    dx = {"l": 0, "m": el.width // 2, "r": el.width}[anchor[0]]
    dy = {"t": 0, "m": el.height // 2, "b": el.height}[anchor[1]]
    im.alpha_composite(el, (int(x - dx), int(y - dy)))


def bubble(text, size, fill=WH, col=INK, tail="bl"):
    t = S.text_im(text, S.de_font(size), col, stroke=0)
    w, h = t.width + 90, t.height + 60
    b = Image.new("RGBA", (w + 60, h + 60))
    d = ImageDraw.Draw(b)
    d.rounded_rectangle((0, 0, w, h), 44, fill=fill + (255,), outline=INK + (255,), width=8)
    tx = 70 if tail == "bl" else w - 70
    d.polygon([(tx - 30, h - 8), (tx + 30, h - 8), (tx - 50 if tail == "bl" else tx + 50, h + 55)], fill=fill + (255,), outline=INK + (255,))
    d.rectangle((tx - 24, h - 14, tx + 24, h - 4), fill=fill + (255,))
    b.alpha_composite(t, (45, 30))
    return S.shadow(b, 18, 170, 10)


def pill(text, size, fill, col=INK):
    t = S.text_im(text, S.de_font(size), col, stroke=0)
    b = Image.new("RGBA", (t.width + 60, t.height + 30))
    ImageDraw.Draw(b).rounded_rectangle((0, 0, b.width - 1, b.height - 1), b.height // 2, fill=fill + (255,), outline=INK + (255,), width=6)
    b.alpha_composite(t, (30, 15))
    return S.shadow(b, 16, 170, 10)


def brand(im, x=70, y=62):
    put(im, e3("pretzel", 100), x, y)


def flag(w):
    """German flag (Noto region-flags, public domain): clean rounded card with a thin white rim."""
    h = int(w * 0.6)
    f = S.rounded(Image.open(E3 + "flag_de.png").convert("RGBA").resize((w, h), Image.LANCZOS), 22)
    card = Image.new("RGBA", (w + 16, h + 16))
    ImageDraw.Draw(card).rounded_rectangle((0, 0, w + 15, h + 15), 28, fill=WH + (255,))
    card.alpha_composite(f, (8, 8))
    return S.shadow(card, 22, 190, 14)


TITLE = [("50", 230, Y), ("Useful", 130, WH), ("German", 130, WH), ("Phrases", 130, WH)]


def title(im, cx, top, max_w=580):
    y = top
    for t, sz, col in TITLE:
        w = word(t, sz, col)
        while w.width > max_w:
            sz -= 6; w = word(t, sz, col)
        put(im, w, cx, y, "mt")
        y += w.height - 48


# 1a: waving hand + flag on the left lane, "50 Useful German Phrases" on the right
im = asphalt()
put(im, flag(420), 320, 250)
put(im, e3("wave", 300), 330, 540)
title(im, 960, 10)
im.convert("RGB").save(OUT + "1a.jpg", quality=93)

# 1b: super minimal: flag left, title right, nothing else
im = asphalt()
put(im, flag(480), 320, 360)
title(im, 960, 10)
im.convert("RGB").save(OUT + "1b.jpg", quality=93)

# 1c: real photo (Brandenburg Gate by day; Wolfgang Staudt, CC BY 2.0, credited in the description)
im = asphalt()
ph = S.rounded(S.cover("/mnt/project-files/fast_german/cache/photos/brandenburg_day.jpg", 540, 500, (0.5, 0.5)).convert("RGBA"), 26)
card = Image.new("RGBA", (570, 530))
ImageDraw.Draw(card).rounded_rectangle((0, 0, 569, 529), 34, fill=WH + (255,))
card.alpha_composite(ph, (15, 15))
put(im, S.shadow(card.rotate(4, expand=True, resample=Image.BICUBIC), 26, 200, 16), 320, 380)
put(im, flag(200), 520, 600)
title(im, 960, 10)
im.convert("RGB").save(OUT + "1c.jpg", quality=93)
