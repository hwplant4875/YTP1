"""Profile round 11 (2026-10-10): words stay crisp. A: motion smear only behind the first letters (F, G).
B: cartoon speed — tapered whoosh strokes and dust puffs trailing the words."""
import os, sys, random
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from branding_v4 import fit
from branding_v5 import asphalt, worn, dashes, YEL
from branding_v10 import hblur, lean, smear, PAINT
D = "/mnt/project-files/fast_german/branding/final/"
S = 800


def base(blur=True):
    bg = asphalt(S, S, 3)
    t1 = lean(fit("FAST", 420, PAINT).resize((420, 240)))
    t2 = lean(fit("GERMAN", 470, PAINT).resize((470, 180)))
    gap = 30
    y = (S - (t1.height + gap + t2.height)) // 2
    dl = dashes(1000, 18, 70, 50, YEL)
    bg.alpha_composite(worn(dl, 5), (-40, y - 72)); bg.alpha_composite(worn(dl, 6), (-100, y + t1.height + gap + t2.height + 54))
    if blur:
        bg = hblur(bg.convert("RGB"), 22).convert("RGBA")
    p1 = ((S - t1.width) // 2 + 40, y)
    p2 = ((S - t2.width) // 2 + 40, y + t1.height + gap)
    return bg, (worn(t1, 1, .12), p1, 0.27), (worn(t2, 2, .12), p2, 0.19)   # (word, pos, first-letter share)


def first_letter(word, pos, share):
    """Layer holding only the leading letter of a word, at its place on the canvas."""
    lay = Image.new("RGBA", (S, S))
    cut = word.crop((0, 0, int(word.width * share), word.height))
    lay.alpha_composite(cut, pos)
    return lay


def profile_a():
    bg, *words = base()
    for w, pos, share in words:
        bg.alpha_composite(smear(first_letter(w, pos, share), 210, 0.10))
    for w, pos, _ in words:
        bg.alpha_composite(w, pos)
    return bg


def whoosh(length, thick, col=PAINT):
    """Comic speed stroke: thin tail on the left, fat rounded head on the right."""
    im = Image.new("RGBA", (length, thick * 2))
    d = ImageDraw.Draw(im)
    pts = [(0, thick)] + [(x, thick - thick * (x / length) ** 0.8 / 2) for x in range(0, length, 4)] + \
          [(length - thick // 2, thick // 2), (length, thick)] + \
          [(x, thick + thick * (x / length) ** 0.8 / 2) for x in range(length, 0, -4)]
    d.polygon(pts, fill=col + (255,))
    d.ellipse((length - thick, thick // 2, length, thick * 3 // 2), fill=col + (255,))
    return im


def puff(r, seed):
    rnd = random.Random(seed)
    im = Image.new("RGBA", (r * 4, r * 3))
    d = ImageDraw.Draw(im)
    for _ in range(5):
        rr = rnd.randint(r // 2, r)
        x, y = rnd.randint(r, r * 3 - rr), rnd.randint(r // 2, r * 2)
        d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=(225, 225, 220, 255), outline=(30, 30, 32, 255), width=5)
    return im


def profile_b():
    bg, *words = base(blur=False)
    for k, (w, (x, y), share) in enumerate(words):
        h = w.height
        for j, (fy, ln, th) in enumerate(((0.25, 150, 16), (0.52, 200, 20), (0.78, 130, 14))):
            s = whoosh(ln, th)
            bg.alpha_composite(worn(s, 30 + 3 * k + j, .05), (x - ln - 18 + j * 6, y + int(h * fy) - th))
        p = puff(34, k)
        bg.alpha_composite(p, (x - p.width + 30, y + h - p.height + 18))
    for w, pos, _ in words:
        bg.alpha_composite(w, pos)
    return bg


if __name__ == "__main__":
    profile_a().convert("RGB").save(D + "profile_A_letter_trail.png")
    profile_b().convert("RGB").save(D + "profile_B_cartoon.png")
    print("ok")
