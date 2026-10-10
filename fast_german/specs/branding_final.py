"""Final profile picture (2026-10-10, user pick): pretzel on the German flag (black / red / gold bands)."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from PIL import Image, ImageDraw
from branding_profiles import pretzel, shadowed
OUT = "/mnt/project-files/fast_german/branding/final"
os.makedirs(OUT, exist_ok=True)
FLAG = ((0, 0, 0), (221, 0, 0), (255, 206, 0))


def make(name, size=600):
    im = Image.new("RGBA", (800, 800))
    d = ImageDraw.Draw(im)
    for i, c in enumerate(FLAG):
        d.rectangle((0, i * 800 // 3, 800, (i + 1) * 800 // 3), fill=c + (255,))
    p = shadowed(pretzel(size, sticker=True), 12, 20, 110)
    im.alpha_composite(p, ((800 - p.width) // 2, (800 - p.height) // 2 + 10))
    im.convert("RGB").save(os.path.join(OUT, name))
    return im


im = make("profile_flag_pretzel.png")
sheet = Image.new("RGB", (420, 230), (255, 255, 255))
m = Image.new("L", (800, 800), 0)
ImageDraw.Draw(m).ellipse((0, 0, 799, 799), fill=255)
for s, (x, y) in ((176, (20, 20)), (88, (220, 20)), (40, (220, 130))):
    sheet.paste(im.convert("RGB").resize((s, s), Image.LANCZOS), (x, y), m.resize((s, s), Image.LANCZOS))
sheet.save(os.path.join(OUT, "preview_sizes.png"))
print("ok")
