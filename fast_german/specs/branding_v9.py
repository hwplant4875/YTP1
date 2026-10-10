"""Branding round 9 (2026-10-10, user direction):
- Profile: the road-marking profile (round 5 #3) with wind lines to the left of the words, so they run to the right.
- Banner: a long top-down Autobahn where der / die / das drive like cars (der blue, die red, das green)."""
import os, random, sys
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import common as C
from branding_v4 import W, H, CX, CY, SAFE, WHITE, F, fit
from branding_v5 import asphalt, worn, dashes, YEL
D = "/mnt/project-files/fast_german/branding/final/"
PAINT = (246, 246, 240)


def wind(height, rows, seed, col=PAINT, max_len=170):
    """Speed lines: stacked rounded bars, longest in the middle, pointing at the word on their right."""
    rnd = random.Random(seed)
    im = Image.new("RGBA", (max_len + 20, height))
    d = ImageDraw.Draw(im)
    for i in range(rows):
        y = int((i + 0.5) * height / rows)
        mid = 1 - abs((i + 0.5) / rows - 0.5) * 1.3
        ln = int(max_len * (0.45 + 0.55 * mid) * rnd.uniform(0.85, 1.0))
        t = max(10, height // (rows * 3))
        x1 = max_len + 10 - rnd.randint(0, 14)
        d.rounded_rectangle((x1 - ln, y - t // 2, x1, y + t // 2), t // 2, fill=col + (255,))
    return im


def profile():
    im = asphalt(800, 800, 3)
    t1 = fit("FAST", 400, PAINT).resize((400, 240))
    t2 = fit("GERMAN", 450, PAINT).resize((450, 180))
    dl = dashes(900, 18, 70, 50, YEL)
    gap = 30
    y = (800 - (t1.height + gap + t2.height)) // 2
    im.alpha_composite(worn(dl, 5), (-20, y - 72)); im.alpha_composite(worn(dl, 6), (-80, y + t1.height + gap + t2.height + 54))
    x1, x2 = 800 - t1.width - 110, 800 - t2.width - 80          # words pushed right to leave room for the wind
    w1, w2 = wind(t1.height - 40, 4, 1, max_len=x1 - 40), wind(t2.height - 30, 3, 2, max_len=x2 - 40)
    im.alpha_composite(worn(w1, 11, .1), (x1 - w1.width - 6, y + 20))
    im.alpha_composite(worn(w2, 12, .1), (x2 - w2.width - 6, y + t1.height + gap + 15))
    im.alpha_composite(worn(t1, 1, 0.12), (x1, y))
    im.alpha_composite(worn(t2, 2, 0.12), (x2, y + t1.height + gap))
    return im


def car(word, col, length=430, width=180):
    """Top-down car driving right, the article written on its roof."""
    im = Image.new("RGBA", (length + 40, width + 40))
    d = ImageDraw.Draw(im)
    ox, oy = 20, 20
    dark = tuple(int(c * 0.72) for c in col)
    for wx in (0.2, 0.74):                                   # wheels
        for wy in (-14, width - 20):
            d.rounded_rectangle((ox + length * wx, oy + wy, ox + length * wx + 90, oy + wy + 34), 10, fill=(20, 20, 22, 255))
    d.rounded_rectangle((ox, oy, ox + length, oy + width), int(width * 0.38), fill=col + (255,))
    d.rounded_rectangle((ox + length * 0.22, oy + width * 0.12, ox + length * 0.8, oy + width * 0.88), int(width * 0.2), fill=dark + (255,))
    d.rounded_rectangle((ox + length * 0.66, oy + width * 0.17, ox + length * 0.8, oy + width * 0.83), 22, fill=(150, 200, 235, 255))   # windscreen
    d.rounded_rectangle((ox + length * 0.22, oy + width * 0.2, ox + length * 0.3, oy + width * 0.8), 18, fill=(120, 165, 200, 255))  # rear window
    for hy in (0.12, 0.72):
        d.rounded_rectangle((ox + length - 26, oy + width * hy, ox + length - 4, oy + width * hy + 40), 8, fill=(255, 245, 200, 255))
        d.rounded_rectangle((ox + 4, oy + width * hy, ox + 22, oy + width * hy + 40), 6, fill=(230, 30, 30, 255))
    t = fit(word, int(length * 0.28), WHITE)
    if t.height > width * 0.5:
        t = t.resize((int(t.width * width * 0.5 / t.height), int(width * 0.5)))
    im.alpha_composite(t, (ox + int(length * 0.32), oy + (width - t.height) // 2))
    # headlight beams ahead of the car
    beam = Image.new("RGBA", im.size)
    return im


def trail(length, height, seed):
    rnd = random.Random(seed)
    im = Image.new("RGBA", (length, height))
    d = ImageDraw.Draw(im)
    for i in range(5):
        y = int((i + 0.5) * height / 5)
        ln = int(length * rnd.uniform(0.5, 1.0))
        for x in range(ln):
            a = int(150 * (x / ln) ** 2)
            d.line((length - ln + x, y - 4, length - ln + x, y + 4), fill=(255, 255, 255, a))
    return im


def banner():
    im = Image.new("RGBA", (W, H), (70, 120, 60, 255))
    d = ImageDraw.Draw(im)
    rnd = np.random.default_rng(1)
    grass = np.array(im, float); grass[..., :3] += rnd.normal(0, 8, (H, W, 1))
    im = Image.fromarray(grass.clip(0, 255).astype("uint8"))
    top, bot = 120, H - 120
    road = asphalt(W, bot - top, 9)
    im.alpha_composite(road, (0, top))
    d = ImageDraw.Draw(im)
    d.rectangle((0, top - 18, W, top), fill=(150, 150, 150, 255)); d.rectangle((0, bot, W, bot + 18), fill=(150, 150, 150, 255))  # crash barriers
    for y in (top + 30, bot - 56):
        d.rectangle((0, y, W, y + 26), fill=PAINT + (255,))
    lane = (bot - top) / 4
    for k in (1, 3):
        y = int(top + k * lane)
        im.alpha_composite(worn(dashes(W + 400, 22, 300, 500, PAINT), k), (-150 * k, y - 11))
    y = int(top + 2 * lane)                                     # middle divider broken around the title
    md = worn(dashes(W + 400, 22, 300, 500, PAINT), 2)
    md_mask = Image.new("L", md.size, 255); ImageDraw.Draw(md_mask).rectangle((SAFE[0] + 100 - 40, 0, SAFE[2] + 40 + 100, 22), fill=0)
    md.putalpha(Image.fromarray(np.minimum(np.array(md.split()[3]), np.array(md_mask))))
    im.alpha_composite(md, (-100, y - 11))
    # title painted in the middle, with wind lines
    t = fit("FAST GERMAN", 1180, PAINT).resize((1180, 250))
    w = wind(210, 4, 3, max_len=260)
    tx = CX - (t.width + w.width) // 2 + w.width
    im.alpha_composite(worn(w, 13, .1), (tx - w.width - 10, CY - w.height // 2))
    im.alpha_composite(worn(t, 7, .1), (tx, CY - t.height // 2))
    # traffic: der / die / das cars in the outer lanes and either side of the title
    G = C.GENDER
    cars = [("der", 420, 0), ("die", 1300, 0), ("das", 2200, 0),
            ("das", 800, 3), ("der", 1700, 3),
            ("die", 260, 1), ("der", 2340, 2)]
    for word, x, ln in cars:
        c = car(word, G[word])
        cy = int(top + (ln + 0.5) * lane)
        tr = trail(340, c.height - 50, x)
        im.alpha_composite(tr, (x - c.width // 2 - 330, cy - tr.height // 2))
        sh = Image.new("RGBA", c.size, (0, 0, 0, 0)); sh.putalpha(c.split()[3].point(lambda v: v // 2))
        im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)), (x - c.width // 2 + 10, cy - c.height // 2 + 14))
        im.alpha_composite(c, (x - c.width // 2, cy - c.height // 2))
    return im


if __name__ == "__main__":
    profile().convert("RGB").save(D + "profile_fast_german.png")
    banner().convert("RGB").save(D + "banner_fast_german.png")
    print("ok")
