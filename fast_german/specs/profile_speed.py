"""Profile round 7 (2026-10-10): road-marking profile, now with a feeling of speed (user ask)."""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from branding_v4 import fit, streaks, round_preview
from branding_v5 import worn, dashes, YEL
from banner_road import asphalt, PAINT, lane_arrow
import branding_v4
OUT = "/mnt/project-files/fast_german/branding/round7"
os.makedirs(OUT, exist_ok=True)
branding_v4.OUT = OUT
S = 800


def shear(im, k=0.22):
    w, h = im.size
    return im.transform((w + int(h * k), h), Image.AFFINE, (1, k, -h * k, 0, 1, 0), Image.BICUBIC)


def words(col=PAINT, w1=440, w2=520):
    t1 = shear(fit("FAST", w1, col).resize((w1, 240)))
    t2 = shear(fit("GERMAN", w2, col).resize((w2, 180)))
    return t1, t2


def ghosts(el, n=5, step=26, fade=0.45):
    """Motion trail: fading copies of the element stepping back to the left."""
    out = Image.new("RGBA", (el.width + n * step, el.height))
    for i in range(n, 0, -1):
        g = el.copy(); g.putalpha(g.split()[3].point(lambda v: int(v * fade ** i)))
        out.alpha_composite(g.filter(ImageFilter.BoxBlur(3)), ((n - i) * step, 0))
    out.alpha_composite(el, (n * step, 0))
    return out


def place(im, t1, t2, dx=0, gap=18):
    y = (S - (t1.height + gap + t2.height)) // 2
    im.alpha_composite(t1, ((S - t1.width) // 2 + dx, y))
    im.alpha_composite(t2, ((S - t2.width) // 2 + dx, y + t1.height + gap))
    return y


def p1():
    """Day asphalt, forward-leaning paint, white speed streaks and a yellow dashed line racing past."""
    im = asphalt(S, S, seed=5)
    im.alpha_composite(worn(dashes(S + 200, 16, 90, 60, YEL), 3), (-100, 150))
    im.alpha_composite(worn(dashes(S + 200, 16, 90, 60, YEL), 4), (-40, 640))
    im.alpha_composite(streaks((S, S), [(255, 255, 255)], 22, 6, 200, 600, (5, 12), (150, 420), 2), (-120, 0))
    t1, t2 = words()
    place(im, worn(t1, 1, .08), worn(t2, 2, .08), dx=20)
    return im


def p2():
    """Night: red tail-light and white head-light streaks through the frame, glowing paint."""
    im = asphalt(S, S, base=(22, 24, 30), seed=6, night=True)
    im.alpha_composite(streaks((S, S), [(255, 60, 50)], 26, 1, 0, S, (4, 10), (200, 700), 2))
    im.alpha_composite(streaks((S, S), [(255, 236, 200)], 22, 2, 0, S, (4, 10), (200, 700), 2))
    t1, t2 = words((250, 250, 240))
    layer = Image.new("RGBA", (S, S))
    place(layer, t1, t2, dx=20)
    im.alpha_composite(layer.filter(ImageFilter.GaussianBlur(12))); im.alpha_composite(layer)
    return im


def p3():
    """Motion trail: the letters leave ghost copies behind them, like a long exposure."""
    im = asphalt(S, S, seed=7)
    t1, t2 = words(w1=400, w2=470)
    g1, g2 = ghosts(worn(t1, 1, .06)), ghosts(worn(t2, 2, .06))
    place(im, g1, g2, dx=-10)
    return im


if __name__ == "__main__":
    P = [p1(), p2(), p3()]
    for k, p in zip("123", P):
        p.convert("RGB").save(os.path.join(OUT, f"profile_{k}.png"))
    round_preview(P, "profile_sizes.png")
    print("ok")


def smear(layer, length=260, steps=40):
    """Directional motion blur to the left: the letters leave a long smeared trail behind them."""
    out = Image.new("RGBA", layer.size)
    for i in range(steps, 0, -1):
        k = i / steps
        g = layer.copy(); g.putalpha(g.split()[3].point(lambda v: int(v * 0.10 * (1 - k) ** 1.2)))
        out.alpha_composite(g, (-int(length * k), 0))
    return out


def final():
    """Round 8: night Autobahn, forward-leaning paint with a long motion smear and light streaks."""
    im = asphalt(S, S, base=(20, 22, 28), seed=8, night=True)
    im.alpha_composite(streaks((S, S), [(255, 60, 50)], 30, 11, 0, S, (4, 9), (250, 800), 2))
    im.alpha_composite(streaks((S, S), [(255, 236, 200)], 26, 12, 0, S, (4, 9), (250, 800), 2))
    t1, t2 = words((250, 250, 240), w1=430, w2=500)
    layer = Image.new("RGBA", (S, S))
    place(layer, t1, t2, dx=40)
    im.alpha_composite(smear(layer, 300))
    im.alpha_composite(layer.filter(ImageFilter.GaussianBlur(10)))
    im.alpha_composite(layer)
    return im
