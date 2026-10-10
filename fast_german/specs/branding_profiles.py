"""Profile picture round 2 (2026-10-10). Strategy: one shape, read at 48 px. A big pretzel (the channel's mascot
object) fills the circle, on one flat high-contrast color; no small dots or text. 'Fast' is carried by speed lines."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
from PIL import Image, ImageDraw, ImageFilter
import common as C
from short import shadowed
OUT = "/mnt/project-files/fast_german/branding/round2"
os.makedirs(OUT, exist_ok=True)
NAVY, RED, INK = (20, 27, 45), (214, 52, 58), C.INK


def outlined(im, width, col):
    """White sticker outline around an RGBA icon, so it pops on any background."""
    a = im.split()[3].filter(ImageFilter.MaxFilter(width * 2 + 1))
    base = Image.new("RGBA", im.size, col + (0,))
    base.putalpha(a)
    base.alpha_composite(im)
    return base


def pretzel(size, sticker=False):
    p = C.icon("pretzel", size)
    pad = Image.new("RGBA", (size + 60, size + 60), (0, 0, 0, 0))
    pad.alpha_composite(p, (30, 30))
    return outlined(pad, 16, (255, 255, 255)) if sticker else pad


def make(name, bg, sticker=False, speed=None, size=600, dx=0):
    im = Image.new("RGBA", (800, 800), bg + (255,))
    d = ImageDraw.Draw(im)
    if speed:
        for y, x0, ln in ((300, 40, 170), (400, 10, 210), (500, 50, 160)):
            d.rounded_rectangle((x0, y - 16, x0 + ln, y + 16), 16, fill=speed + (255,))
    p = shadowed(pretzel(size, sticker), 12, 20, 90)
    im.alpha_composite(p, ((800 - p.width) // 2 + dx, (800 - p.height) // 2 + 10))
    im.convert("RGB").save(os.path.join(OUT, name))
    return im


A = make("A_navy_pretzel.png", NAVY, size=620)                                   # calm, matches the sleep videos
B = make("B_red_sticker.png", RED, sticker=True, size=600)                       # loudest, stands out in a feed
C2 = make("C_yellow_fast.png", C.YELLOW, sticker=True, speed=INK, size=560, dx=60)  # 'fast': speed lines

# preview: how each looks as a round avatar at 176 px (channel page), 88 px and 40 px (comments/feed)
sheet = Image.new("RGB", (3 * 360, 330), (255, 255, 255))
for i, im in enumerate((A, B, C2)):
    m = Image.new("L", (800, 800), 0)
    ImageDraw.Draw(m).ellipse((0, 0, 799, 799), fill=255)
    x = i * 360 + 20
    for s, (ox, oy) in ((176, (0, 20)), (88, (200, 20)), (40, (200, 130))):
        r = im.convert("RGB").resize((s, s), Image.LANCZOS)
        sheet.paste(r, (x + ox, oy), m.resize((s, s), Image.LANCZOS))
    ImageDraw.Draw(sheet).text((x + 60, 230), "ABC"[i], fill=(0, 0, 0))
sheet.save(os.path.join(OUT, "preview_sizes.png"))
print("ok")
