"""HUD overlay for the 3D timelapse frames (place, year, Eren's age, chapter title, caption, place labels).

python3 hud.py in.png out.png --labels lab.json --font A --place "SHIGANSHINA DISTRICT" --year 845 --age 10 \
    --title "A Long Dream" --caption "..." --show "WALL MARIA,SHIGANSHINA DISTRICT"
"""
import argparse, json, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
F = lambda n: os.path.join(HERE, "fonts", n)
FONTS = {  # title font, title weight, body font, body weight
    "A": (F("GrenzeGotisch-VF.ttf"), 800, F("GrenzeGotisch-VF.ttf"), 450),
    "B": (F("PirataOne-Regular.ttf"), None, F("GrenzeGotisch-VF.ttf"), 450),
    "C": (F("UnifrakturCook-Bold.ttf"), None, F("GrenzeGotisch-VF.ttf"), 450),
}

def font(path, size, wght=None):
    f = ImageFont.truetype(path, size)
    if wght is not None:
        try:
            f.set_variation_by_axes([wght])
        except Exception:
            pass
    return f

def shadow_text(base, xy, text, fnt, anchor, fill=(255, 255, 255, 255), blur=None, spacing=0):
    W, H = base.size
    blur = blur or max(2, H // 300)
    sh = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).text((xy[0], xy[1] + blur // 2), text, font=fnt, anchor=anchor, fill=(0, 0, 0, 170))
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    base.alpha_composite(sh)
    ImageDraw.Draw(base).text(xy, text, font=fnt, anchor=anchor, fill=fill)

def draw(img, a):
    W, H = img.size
    s = H / 1080
    tf, tw, bf, bw = FONTS[a.font]
    base = img.convert("RGBA")
    m = int(48 * s)
    # top-left: place
    shadow_text(base, (m, m), a.place, font(bf, int(40 * s), 600), "la")
    # top-right: year + Eren's age
    shadow_text(base, (W - m, m - int(8 * s)), f"Year {a.year}", font(tf, int(78 * s), tw), "ra")
    if a.age:
        shadow_text(base, (W - m, m + int(84 * s)), f"Eren, age {a.age}", font(bf, int(36 * s), bw), "ra")
    # bottom: title + rule + caption
    cy = H - int(150 * s)
    shadow_text(base, (W // 2, cy), a.title, font(tf, int(96 * s), tw), "ms")
    d = ImageDraw.Draw(base)
    rw = int(150 * s)
    d.line([(W // 2 - rw, cy + int(20 * s)), (W // 2 + rw, cy + int(20 * s))], fill=(255, 255, 255, 200), width=max(1, int(2 * s)))
    shadow_text(base, (W // 2, cy + int(70 * s)), a.caption, font(bf, int(42 * s), bw), "ms")
    # place labels with leader lines
    if a.labels and a.show:
        lab = json.load(open(a.labels))
        lf = font(bf, int(34 * s), 650)
        for name in a.show.split(","):
            if name not in lab:
                continue
            u, v = lab[name]
            x, y = int(u * W), int((1 - v) * H)
            top = y - int(110 * s)
            d.line([(x, y), (x, top + int(8 * s))], fill=(255, 255, 255, 230), width=max(1, int(2 * s)))
            d.ellipse([x - int(5 * s), y - int(5 * s), x + int(5 * s), y + int(5 * s)], fill=(255, 255, 255, 255))
            shadow_text(base, (x, top), name, lf, "ms")
    return base.convert("RGB")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("inp"); ap.add_argument("out")
    for k in ("labels", "place", "year", "age", "title", "caption", "show"):
        ap.add_argument("--" + k, default="")
    ap.add_argument("--font", default="A")
    a = ap.parse_args()
    draw(Image.open(a.inp), a).save(a.out, quality=92)
