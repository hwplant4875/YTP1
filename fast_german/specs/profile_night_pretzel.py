"""Profile (2026-10-11, user idea): a pretzel in the middle of a starry night sky.
A: the pretzel glows like a moon. B: the pretzel drawn as a constellation of stars."""
import math, os, random, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import common as C
D = "/mnt/project-files/fast_german/branding/final/"
S = 800


def sky(seed=1):
    yy, xx = np.mgrid[0:S, 0:S] / S
    r = np.sqrt((xx - .5) ** 2 + (yy - .55) ** 2)
    top, mid = np.array([8, 12, 34]), np.array([34, 40, 96])
    c = mid[None, None] * (1 - r[..., None] * 1.4).clip(0, 1) + top[None, None] * (r[..., None] * 1.4).clip(0, 1)
    im = Image.fromarray(c.clip(0, 255).astype("uint8")).convert("RGBA")
    rnd = random.Random(seed)
    stars = Image.new("RGBA", (S, S)); d = ImageDraw.Draw(stars)
    for _ in range(170):
        x, y = rnd.uniform(0, S), rnd.uniform(0, S)
        rr = rnd.choice((1, 1, 1.4, 1.8, 2.4))
        a = rnd.randint(110, 255)
        d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=(255, 250, 235, a))
    for _ in range(9):                                            # a few sparkles
        x, y, L = rnd.uniform(40, S - 40), rnd.uniform(40, S - 40), rnd.uniform(10, 18)
        d.line((x - L, y, x + L, y), fill=(255, 250, 230, 220), width=2); d.line((x, y - L, x, y + L), fill=(255, 250, 230, 220), width=2)
    im.alpha_composite(stars.filter(ImageFilter.GaussianBlur(0.6)))
    im.alpha_composite(stars)
    return im


def glow_behind(im, alpha_src, pos, col, blur, strength):
    g = Image.new("RGBA", (S, S))
    a = Image.new("L", (S, S), 0); a.paste(alpha_src, pos)
    g.paste(Image.new("RGBA", (S, S), col + (255,)), (0, 0), a.point(lambda v: int(v * strength)))
    im.alpha_composite(g.filter(ImageFilter.GaussianBlur(blur)))


def fill_small_holes(mask, max_area):
    """Fill enclosed gaps smaller than max_area px (outside = whatever floods from the corner)."""
    inv = Image.fromarray(np.where(np.array(mask) > 127, 0, 200).astype("uint8"))
    ImageDraw.floodfill(inv, (0, 0), 1)
    out = np.array(mask).copy()
    for _ in range(50):
        arr = np.array(inv)
        idx = np.argwhere(arr == 200)
        if not len(idx):
            break
        y, x = map(int, idx[0])
        ImageDraw.floodfill(inv, (x, y), 50)
        region = np.array(inv) == 50
        if region.sum() < max_area:
            out[region] = 255
        inv = Image.fromarray(np.where(region, 2, np.array(inv)).astype("uint8"))
    return Image.fromarray(out)


def profile_a():
    im = sky()
    raw = C.icon("pretzel", 470)
    p = Image.new("RGBA", (raw.width + 60, raw.height + 60)); p.alpha_composite(raw, (30, 30))
    a = p.split()[3].filter(ImageFilter.MinFilter(9)).filter(ImageFilter.MaxFilter(37))   # white sticker stroke; the min-filter drops stray crumbs
    a = a.filter(ImageFilter.GaussianBlur(4)).point(lambda v: 255 if v > 110 else 0).filter(ImageFilter.GaussianBlur(1))
    a = fill_small_holes(a.filter(ImageFilter.MaxFilter(21)).filter(ImageFilter.MinFilter(21)), 4000)
    st = Image.new("RGBA", p.size, (255, 255, 255, 0)); st.putalpha(a); st.alpha_composite(p); p = st
    pos = ((S - p.width) // 2, (S - p.height) // 2 + 10)
    glow_behind(im, p.split()[3], pos, (255, 200, 120), 22, 0.85)
    glow_behind(im, p.split()[3], pos, (255, 230, 170), 8, 0.6)
    im.alpha_composite(p, pos)
    return im


def profile_b():
    """Constellation: star points along a pretzel outline, joined by thin lines."""
    im = sky(2)
    # pretzel path: two loops + crossed arms (parametric), centred
    pts = []
    for t in np.linspace(0, 2 * math.pi, 22, endpoint=False):
        x = math.sin(t) * (1 + 0.15 * math.cos(2 * t))
        y = -0.55 * math.cos(2 * t) + 0.25 * math.cos(t)
        pts.append((S / 2 + x * 230, S / 2 + y * 260 + 10))
    lines = Image.new("RGBA", (S, S)); d = ImageDraw.Draw(lines)
    for a, b in zip(pts, pts[1:] + pts[:1]):
        d.line((a, b), fill=(255, 230, 180, 150), width=3)
    im.alpha_composite(lines.filter(ImageFilter.GaussianBlur(4))); im.alpha_composite(lines)
    st = Image.new("RGBA", (S, S)); d = ImageDraw.Draw(st)
    for i, (x, y) in enumerate(pts):
        r = 9 if i % 3 == 0 else 6
        d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 244, 214, 255))
    im.alpha_composite(st.filter(ImageFilter.GaussianBlur(8))); im.alpha_composite(st)
    return im


if __name__ == "__main__":
    A, B = profile_a(), profile_b()
    A.convert("RGB").save(D + "profile_night_A_glow.png"); B.convert("RGB").save(D + "profile_night_B_stars.png")
    m = Image.new("L", (S, S), 0); ImageDraw.Draw(m).ellipse((0, 0, S - 1, S - 1), fill=255)
    sheet = Image.new("RGB", (760, 230), "white")
    for i, im in enumerate((A, B)):
        for s, (x, y) in ((176, (20, 20)), (88, (220, 20)), (40, (220, 130))):
            sheet.paste(im.convert("RGB").resize((s, s), Image.LANCZOS), (x + i * 380, y), m.resize((s, s)))
    sheet.save(D + "profile_night_sizes.png")
    print("ok")
