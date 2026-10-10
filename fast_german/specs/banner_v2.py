"""Banner redesign (2026-10-10): three full-bleed concepts matching the text-logo profiles (round3 A/B/C), no flag.
Mobile safe area 1546x423 holds only pretzel | 'Fast German' | beer; the rest of 2560x1440 is filled for desktop/TV."""
import math, os, random, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
sys.path.insert(0, os.path.dirname(__file__))
from PIL import Image, ImageDraw
import common as C
from short import text_img, shadowed, font
from PIL import ImageFilter


def outlined(im, width, col):
    a = im.split()[3].filter(ImageFilter.MaxFilter(width * 2 + 1))
    base = Image.new("RGBA", im.size, col + (0,))
    base.putalpha(a)
    base.alpha_composite(im)
    return base


def skew(im, k=0.18):
    w, h = im.size
    return im.transform((w + int(h * k), h), Image.AFFINE, (1, k, -h * k, 0, 1, 0), Image.BICUBIC)
OUT = "/mnt/project-files/fast_german/branding/banner_v2"
os.makedirs(OUT, exist_ok=True)
W, H = 2560, 1440
CX, CY = W // 2, H // 2
SAFE = (CX - 773, CY - 211, CX + 773, CY + 211)
BLACK, FRED, GOLD = (18, 18, 20), (221, 0, 0), (255, 206, 0)
BLUE, RED, GREEN = C.GENDER["der"], C.GENDER["die"], C.GENDER["das"]
WORDS = ["Hallo!", "Danke!", "Prost!", "Tschüss!", "Genau!", "Lecker!", "Bitte!", "Na und?", "Krass!", "Jawohl!",
         "der Hund", "die Katze", "das Bier", "die Brezel", "der Apfel", "das Brot", "Wunderbar!", "Doch!"]
ICONS = ["pretzel", "beer-mug", "bread", "hot-dog", "castle", "soccer-ball", "high-speed-train", "automobile",
         "hot-beverage", "shortcake", "snow-capped-mountain", "books", "bicycle", "cheese-wedge", "evergreen-tree",
         "musical-notes", "light-bulb"]


def ic(name, s, sticker=True):
    try:
        im = C.icon(name, s)
    except Exception:
        return None
    if sticker:
        pad = Image.new("RGBA", (s + 40, s + 40))
        pad.alpha_composite(im, (20, 20))
        im = outlined(pad, max(6, s // 28), (255, 255, 255))
    return im


def tight(im):
    """Crop transparent padding so layout uses the visible width."""
    return im.crop(im.split()[3].point(lambda a: 255 if a > 8 else 0).getbbox())


def in_safe(x, y, w, h, m=40):
    return not (x + w < SAFE[0] - m or x > SAFE[2] + m or y + h < SAFE[1] - m or y > SAFE[3] + m)


def center(im, fill, stroke=None, italic=False, offset_shadow=None, icon_size=190, size=155):
    """'Fast German' on one line with the pretzel and beer either side, all inside the mobile safe area."""
    t = text_img("Fast German", font(size, "Bold"), fill + (255,), stroke=14 if stroke else 0,
                 stroke_fill=(stroke + (255,)) if stroke else None)
    if italic:
        t = skew(t)
    t = tight(t)
    pz, beer = (tight(shadowed(ic(n, icon_size), 8, 14, 80)) for n in ("pretzel", "beer-mug"))
    gap = 45
    total = pz.width + gap + t.width + gap + beer.width
    assert total < SAFE[2] - SAFE[0] - 40, total
    x = CX - total // 2
    im.alpha_composite(pz, (x, CY - pz.height // 2 + 6))
    x += pz.width + gap
    if offset_shadow:
        sh = Image.new("RGBA", t.size, offset_shadow + (255,))
        sh.putalpha(t.split()[3])
        im.alpha_composite(sh, (x + 10, CY - t.height // 2 + 10))
        im.alpha_composite(t, (x, CY - t.height // 2))
    else:
        im.alpha_composite(shadowed(t, 8, 12, 80), (x, CY - t.height // 2))
    x += t.width + gap
    im.alpha_composite(beer, (x, CY - beer.height // 2 + 6))


def chip(word, col, s=58):
    t = text_img(word, font(s, "Bold"), (255, 255, 255, 255))
    im = Image.new("RGBA", (t.width + 40, t.height + 10))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, im.width - 1, im.height - 1), im.height // 2, fill=col + (255,))
    im.alpha_composite(t, (20, 5))
    return im


def scatter(im, items, seed, tries=3000, margin=30):
    """Place images at random spots outside the safe area without overlapping each other."""
    rnd, boxes = random.Random(seed), []
    for it in items:
        r = shadowed(it.rotate(rnd.uniform(-12, 12), expand=True, resample=Image.BICUBIC), 6, 10, 60)
        for _ in range(tries):
            x, y = rnd.randint(-60, W - r.width + 60), rnd.randint(-60, H - r.height + 60)
            if in_safe(x, y, r.width, r.height):
                continue
            if any(x < b[2] + margin and x + r.width > b[0] - margin and y < b[3] + margin and y + r.height > b[1] - margin
                   for b in boxes):
                continue
            boxes.append((x, y, x + r.width, y + r.height))
            im.alpha_composite(r, (x, y))
            break


def speed_yellow():
    """A (matches profile A): yellow, black italic name with speed lines, German-life stickers around."""
    im = Image.new("RGBA", (W, H), C.YELLOW + (255,))
    d = ImageDraw.Draw(im)
    for k in range(-H, W, 110):
        d.line((k, 0, k + H, H), fill=(255, 212, 88, 255), width=40)
    items = [x for x in (ic(n, random.Random(i).choice((190, 220, 250))) for i, n in enumerate(ICONS * 2)) if x]
    scatter(im, items, 7)
    center(im, BLACK, italic=True)
    return im


def chips_black():
    """B (matches profile B): black, yellow+white name, colorful der/die/das word chips around."""
    im = Image.new("RGBA", (W, H), BLACK + (255,))
    d = ImageDraw.Draw(im)
    for y in range(0, H, 40):
        for x in range((y // 40 % 2) * 20, W, 40):
            d.ellipse((x - 2, y - 2, x + 2, y + 2), fill=(255, 255, 255, 22))
    cols = [BLUE, RED, GREEN, (245, 160, 40)]
    words = WORDS + ["Kartoffel", "Fernweh", "Feierabend", "Ohrwurm", "Schmetterling", "Kummerspeck", "Gemütlichkeit",
                     "die Glühbirne", "der Handschuh", "Zeitgeist", "Quatsch!", "Ach so!"]
    scatter(im, [chip(w, cols[i % 4], s=random.Random(i).choice((56, 66, 78))) for i, w in enumerate(words)], 3, margin=24)
    # two-tone title: draw "Fast" yellow and "German" white by composing two images
    t1 = text_img("Fast ", font(155, "Bold"), C.YELLOW + (255,))
    t2 = text_img("German", font(155, "Bold"), (255, 255, 255, 255))
    t = Image.new("RGBA", (t1.width + t2.width - 40, max(t1.height, t2.height)))
    t.alpha_composite(t1, (0, 0)); t.alpha_composite(t2, (t1.width - 40, 0))
    _place_custom(im, tight(t))
    return im


def _place_custom(im, t, icon_size=190, gap=45):
    pz, beer = (tight(shadowed(ic(n, icon_size), 8, 14, 80)) for n in ("pretzel", "beer-mug"))
    total = pz.width + gap + t.width + gap + beer.width
    assert total < SAFE[2] - SAFE[0] - 40, total
    x = CX - total // 2
    im.alpha_composite(pz, (x, CY - pz.height // 2 + 6)); x += pz.width + gap
    im.alpha_composite(shadowed(t, 8, 12, 90), (x, CY - t.height // 2)); x += t.width + gap
    im.alpha_composite(beer, (x, CY - beer.height // 2 + 6))


def words_red():
    """C (matches profile C): red, white name with a hard dark-red shadow, faint German words as texture."""
    im = Image.new("RGBA", (W, H), (214, 52, 58, 255))
    rnd = random.Random(11)
    words = WORDS + ["Kartoffel", "Schmetterling", "Handschuh", "Kummerspeck", "Glühbirne", "Torschlusspanik",
                     "Fernweh", "Feierabend", "Gemütlichkeit", "Ohrwurm", "Zeitgeist", "Wanderlust"]
    boxes = []
    for i in range(500):
        s = rnd.choice((60, 76, 96, 120, 150))
        t = text_img(words[i % len(words)], font(s, "Bold"), (255, 255, 255, rnd.choice((40, 60, 90))))
        for _ in range(40):
            x, y = rnd.randint(-80, W - t.width + 80), rnd.randint(-40, H - t.height + 40)
            if in_safe(x, y, t.width, t.height, 50):
                continue
            if any(x < b[2] + 16 and x + t.width > b[0] - 16 and y < b[3] - 10 and y + t.height > b[1] + 10 for b in boxes):
                continue
            boxes.append((x, y, x + t.width, y + t.height))
            im.alpha_composite(t, (x, y))
            break
    center(im, (255, 255, 255), offset_shadow=(120, 20, 28))
    return im


def previews(name, im):
    im.convert("RGB").save(os.path.join(OUT, name + ".png"))
    pv = im.copy()
    ImageDraw.Draw(pv).rectangle(SAFE, outline=(0, 255, 120, 255), width=8)
    mob = im.crop(SAFE).resize((773, 211))
    sheet = Image.new("RGB", (1280, 720 + 40 + 211), (255, 255, 255))
    sheet.paste(pv.convert("RGB").resize((1280, 720)), (0, 0))
    sheet.paste(mob.convert("RGB"), ((1280 - 773) // 2, 760))
    sheet.save(os.path.join(OUT, name + "_preview.jpg"), quality=88)


if __name__ == "__main__":
    for n, f in (("A_yellow_speed", speed_yellow), ("B_black_chips", chips_black), ("C_red_words", words_red)):
        previews(n, f())
        print(n, flush=True)
