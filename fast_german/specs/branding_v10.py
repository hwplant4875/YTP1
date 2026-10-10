"""Branding round 10 (2026-10-10): speed without drawn lines. Like a panning photo: the road (asphalt grain,
lane dashes) is motion-blurred sideways, the painted words stay sharp, lean forward a little and leave a soft
smear behind them. Same treatment on the banner's der/die/das cars."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from branding_v4 import W, H, CX, CY, SAFE, fit
from branding_v5 import asphalt, worn, dashes, YEL
import branding_v9 as V9
D = "/mnt/project-files/fast_german/branding/final/"
PAINT = V9.PAINT


def hblur(im, r):
    """Horizontal box blur of radius r (motion blur along the road)."""
    a = np.array(im, float)
    pad = np.pad(a, ((0, 0), (r, r), (0, 0)), mode="edge")
    c = np.cumsum(pad, axis=1)
    c = np.concatenate([np.zeros_like(c[:, :1]), c], axis=1)
    out = (c[:, 2 * r + 1:] - c[:, :-2 * r - 1]) / (2 * r + 1)
    return Image.fromarray(out[:, :a.shape[1]].clip(0, 255).astype("uint8"), im.mode)


def lean(im, k=0.12):
    w, h = im.size
    return im.transform((w + int(h * k), h), Image.AFFINE, (1, k, -h * k, 0, 1, 0), Image.BICUBIC)


def smear(layer, length, strength=0.07, steps=36):
    out = Image.new("RGBA", layer.size)
    for i in range(steps, 0, -1):
        k = i / steps
        g = layer.copy(); g.putalpha(g.split()[3].point(lambda v: int(v * strength * (1 - k) ** 1.5)))
        out.alpha_composite(g, (-int(length * k), 0))
    return hblur(out, 6)


def profile():
    S = 800
    bg = asphalt(S, S, 3)
    dl = dashes(1000, 18, 70, 50, YEL)
    t1 = lean(fit("FAST", 420, PAINT).resize((420, 240)))
    t2 = lean(fit("GERMAN", 470, PAINT).resize((470, 180)))
    gap = 30
    y = (S - (t1.height + gap + t2.height)) // 2
    bg.alpha_composite(worn(dl, 5), (-40, y - 72)); bg.alpha_composite(worn(dl, 6), (-100, y + t1.height + gap + t2.height + 54))
    bg = hblur(bg.convert("RGB"), 28).convert("RGBA")              # the road rushes past
    layer = Image.new("RGBA", (S, S))
    layer.alpha_composite(worn(t1, 1, 0.12), ((S - t1.width) // 2 + 25, y))
    layer.alpha_composite(worn(t2, 2, 0.12), ((S - t2.width) // 2 + 25, y + t1.height + gap))
    bg.alpha_composite(smear(layer, 170))
    bg.alpha_composite(layer)
    return bg


def banner():
    G = V9.C.GENDER
    top, bot = 120, H - 120
    lane = (bot - top) / 4
    # road and markings, then blur them sideways
    im = Image.new("RGBA", (W, H), (70, 120, 60, 255))
    rnd = np.random.default_rng(1)
    g = np.array(im, float); g[..., :3] += rnd.normal(0, 8, (H, W, 1)); im = Image.fromarray(g.clip(0, 255).astype("uint8"))
    im.alpha_composite(asphalt(W, bot - top, 9), (0, top))
    d = ImageDraw.Draw(im)
    d.rectangle((0, top - 18, W, top), fill=(150, 150, 150, 255)); d.rectangle((0, bot, W, bot + 18), fill=(150, 150, 150, 255))
    for yy in (top + 30, bot - 56):
        d.rectangle((0, yy, W, yy + 26), fill=PAINT + (255,))
    for k in (1, 2, 3):
        yy = int(top + k * lane)
        im.alpha_composite(worn(dashes(W + 400, 22, 300, 500, PAINT), k), (-150 * k, yy - 11))
    im = hblur(im.convert("RGB"), 40).convert("RGBA")
    # cars: sharp, with a soft smear behind
    cars = [("der", 420, 0), ("die", 1300, 0), ("das", 2200, 0), ("das", 800, 3), ("der", 1700, 3), ("die", 260, 1), ("der", 2340, 2)]
    layer = Image.new("RGBA", (W, H))
    shadows = Image.new("RGBA", (W, H))
    for word, x, ln in cars:
        c = V9.car(word, G[word])
        cy = int(top + (ln + 0.5) * lane)
        sh = Image.new("RGBA", c.size); sh.putalpha(c.split()[3].point(lambda v: v // 2))
        shadows.alpha_composite(sh, (x - c.width // 2 + 10, cy - c.height // 2 + 14))
        layer.alpha_composite(c, (x - c.width // 2, cy - c.height // 2))
    im.alpha_composite(shadows.filter(ImageFilter.GaussianBlur(10)))
    im.alpha_composite(smear(layer, 300, 0.09))
    im.alpha_composite(layer)
    # title painted in the middle: a road marking, so it moves with the road but stays readable
    t = lean(fit("FAST GERMAN", 1250, PAINT).resize((1250, 260)))
    tl = Image.new("RGBA", (W, H)); tl.alpha_composite(worn(t, 7, .1), (CX - t.width // 2 + 20, CY - t.height // 2))
    clear = Image.new("RGBA", (W, H)); ImageDraw.Draw(clear).rectangle((SAFE[0], CY - 150, SAFE[2], CY + 150), fill=(0, 0, 0, 0))
    im.alpha_composite(smear(tl, 260, 0.06))
    im.alpha_composite(tl)
    return im


if __name__ == "__main__":
    profile().convert("RGB").save(D + "profile_fast_german.png")
    banner().convert("RGB").save(D + "banner_fast_german.png")
    print("ok")


WORDS = ["Der", "Die", "Das", "Ich", "Du", "Wie", "Wo", "Was", "Ja", "Nein", "Hallo", "Danke", "Wer", "Warum", "Bitte", "Tschüss"]


def word_colour(w):
    G = V9.C.GENDER
    return {"Der": G["der"], "Die": G["die"], "Das": G["das"]}.get(w, PAINT)


def banner_words():
    """Words drive on a two-way highway with a yellow centre line; the two middle lanes sit inside the mobile crop."""
    LANE = 200
    lanes_top = [CY - LANE * k for k in (1, 2, 3)]            # top edges of the lanes above the centre line
    lanes_bot = [CY + LANE * k for k in (0, 1, 2)]            # top edges of the lanes below
    top, bot = CY - 3 * LANE, CY + 3 * LANE
    im = Image.new("RGBA", (W, H), (64, 112, 56, 255))
    rnd = np.random.default_rng(1)
    g = np.array(im, float); g[..., :3] += rnd.normal(0, 8, (H, W, 1)); im = Image.fromarray(g.clip(0, 255).astype("uint8"))
    im.alpha_composite(asphalt(W, bot - top, 9), (0, top))
    d = ImageDraw.Draw(im)
    d.rectangle((0, top - 16, W, top), fill=(150, 150, 150, 255)); d.rectangle((0, bot, W, bot + 16), fill=(150, 150, 150, 255))
    for yy in (top + 18, bot - 40):
        d.rectangle((0, yy, W, yy + 22), fill=PAINT + (255,))
    d.rectangle((0, CY - 20, W, CY - 6), fill=YEL + (255,)); d.rectangle((0, CY + 6, W, CY + 20), fill=YEL + (255,))  # centre line
    for yy in (CY - LANE, CY - 2 * LANE, CY + LANE, CY + 2 * LANE):
        im.alpha_composite(worn(dashes(W + 400, 18, 280, 420, PAINT), yy), (-int(yy) % 400, yy - 9))
    im = hblur(im.convert("RGB"), 40).convert("RGBA")
    # traffic: every lane drives to the right (forward = learning fast); bigger words in the two mobile lanes
    r = np.random.default_rng(4)
    layer = Image.new("RGBA", (W, H))
    order = list(WORDS)
    def put(w, x, y0, h, seed):
        t = lean(fit(w, 1000, word_colour(w)))
        t = t.resize((int(t.width * h / t.height), h))
        layer.alpha_composite(worn(t, seed, .08), (int(x), y0 + (LANE - h) // 2))
        return t.width

    def row(words, y0, h, x0, x1, seed):
        """Spread whole words evenly between x0 and x1 (used to fill the mobile crop exactly)."""
        widths = [lean(fit(w, 1000, PAINT)).size for w in words]
        widths = [int(ww * h / hh) for ww, hh in widths]
        gap = (x1 - x0 - sum(widths)) / len(words)
        x = x0 + gap * 0.75
        for k, w in enumerate(words):
            put(w, x, y0, h, seed + k); x += widths[k] + gap

    # mobile lanes: the two lanes either side of the centre line, whole words inside the crop
    row(["Der", "Die", "Das"], CY - LANE, 150, SAFE[0], SAFE[2], 10)
    row(["Ich", "Wie", "Was"], CY, 150, SAFE[0], SAFE[2], 20)
    # same lanes continue outside the crop on desktop / TV
    row(["Hallo"], CY - LANE, 150, 0, SAFE[0] - 40, 30); row(["Danke"], CY - LANE, 150, SAFE[2] + 40, W, 31)
    row(["Ja"], CY, 150, 0, SAFE[0] - 40, 32); row(["Nein"], CY, 150, SAFE[2] + 40, W, 33)
    # outer lanes: lighter traffic
    row(["Wer", "Du", "Warum"], CY - 2 * LANE, 120, 0, W, 40)
    row(["Tschüss", "Wo", "Bitte"], CY + LANE, 120, -200, W, 50)
    row(["Die", "Wie", "Das"], CY - 3 * LANE, 105, 200, W, 60)
    row(["Was", "Ich", "Danke"], CY + 2 * LANE, 105, -100, W - 200, 70)
    im.alpha_composite(smear(layer, 320, 0.08))
    im.alpha_composite(layer)
    return im


if __name__ == "__main__":
    banner_words().convert("RGB").save(D + "banner_fast_german.png")
    print("banner ok")
