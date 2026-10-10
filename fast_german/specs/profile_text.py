"""Profile picture round 3 (2026-10-10): text logo 'Fast German', no pretzel, no flag.
Two stacked words as large as the round crop allows, so it still reads at 40 px."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
from PIL import Image, ImageDraw
import common as C
from short import text_img, shadowed, font
OUT = "/mnt/project-files/fast_german/branding/round3"
os.makedirs(OUT, exist_ok=True)
INK, YEL = (18, 18, 20), C.YELLOW


def skew(im, k=0.18):
    w, h = im.size
    return im.transform((w + int(h * k), h), Image.AFFINE, (1, k, -h * k, 0, 1, 0), Image.BICUBIC)


def word(t, size, fill, stroke=0, sf=None, italic=False):
    im = text_img(t, font(size, "Bold"), fill + (255,), stroke=stroke, stroke_fill=(sf + (255,)) if sf else None)
    return skew(im) if italic else im


def stack(bg, top, bottom, lines=None, offset_shadow=None, name="x.png"):
    im = Image.new("RGBA", (800, 800), bg + (255,))
    d = ImageDraw.Draw(im)
    if lines:
        for y, x0, ln in ((330, 70, 80), (400, 50, 100), (470, 80, 70)):
            d.rounded_rectangle((x0, y - 12, x0 + ln, y + 12), 12, fill=lines + (255,))
    total = top.height + bottom.height - 60
    y = (800 - total) // 2 - 10
    for i, w in enumerate((top, bottom)):
        if offset_shadow:
            sh = Image.new("RGBA", w.size, offset_shadow + (255,))
            sh.putalpha(w.split()[3])
            im.alpha_composite(sh, ((800 - w.width) // 2 + 12, y + 12))
        im.alpha_composite(w, ((800 - w.width) // 2 + (40 if lines else 0), y))
        y += w.height - 60
    im.convert("RGB").save(os.path.join(OUT, name))
    return im


# A: black on yellow, italic with speed lines ("fast")
A = stack(YEL, word("Fast", 250, INK, italic=True), word("German", 165, INK, italic=True), lines=INK, name="A_yellow_italic.png")
# B: yellow + white on black, like the video titles (big yellow word with ink outline)
B = stack(INK, word("Fast", 260, YEL), word("German", 170, (255, 255, 255)), name="B_black_yellow.png")
# C: white sticker letters with hard red offset shadow on red
RED = (214, 52, 58)
C3 = stack(RED, word("Fast", 255, (255, 255, 255)), word("German", 168, (255, 255, 255)), offset_shadow=(120, 20, 28), name="C_red_white.png")

sheet = Image.new("RGB", (3 * 360, 300), (255, 255, 255))
m = Image.new("L", (800, 800), 0)
ImageDraw.Draw(m).ellipse((0, 0, 799, 799), fill=255)
for i, im in enumerate((A, B, C3)):
    x = i * 360 + 20
    for s, (ox, oy) in ((176, (0, 20)), (88, (200, 20)), (40, (200, 130))):
        sheet.paste(im.convert("RGB").resize((s, s), Image.LANCZOS), (x + ox, oy), m.resize((s, s), Image.LANCZOS))
    ImageDraw.Draw(sheet).text((x + 80, 220), "ABC"[i], fill=(0, 0, 0))
sheet.save(os.path.join(OUT, "preview_sizes.png"))
print("ok")
