"""Highlight graphic: dashed 180-degree arc + label, as a transparent 1080x1920 PNG.
usage: python3 arc_png.py out.png cx cy r [label]"""
import math, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont
out, cx, cy, r = sys.argv[1], *map(float, sys.argv[2:5])
label = sys.argv[5] if len(sys.argv) > 5 else '180°'
S = 2  # supersample
img = Image.new('RGBA', (1080 * S, 1920 * S), (0, 0, 0, 0))
d = ImageDraw.Draw(img)
col = (255, 212, 0, 255)
n = 26
for i in range(n):
    if i % 2: continue
    a0, a1 = 180 + 180 * i / n, 180 + 180 * (i + 1) / n
    d.arc([(cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S], a0, a1, fill=col, width=7 * S)
for x in (cx - r, cx + r):
    d.ellipse([(x - 9) * S, (cy - 9) * S, (x + 9) * S, (cy + 9) * S], fill=col)
f = ImageFont.truetype('/home/user/rs_work/fonts/YOUTUBESANSBLACK.OTF', 64 * S)
tw = d.textlength(label, font=f)
d.text(((cx * S) - tw / 2, (cy - r - 92) * S), label, font=f, fill=col)
glow = img.filter(ImageFilter.GaussianBlur(10 * S))
shadow = Image.new('RGBA', img.size, (0, 0, 0, 0)); shadow.paste((0, 0, 0, 170), mask=img.split()[3].filter(ImageFilter.GaussianBlur(4 * S)))
outimg = Image.alpha_composite(Image.alpha_composite(shadow, glow), img).resize((1080, 1920), Image.LANCZOS)
outimg.save(out)
