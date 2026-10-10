"""Red pointer arrow (shorts style) as a transparent 1080x1920 PNG.
usage: python3 arrow_png.py out.png tail_x tail_y tip_x tip_y [shaft_px]"""
import math, sys
from PIL import Image, ImageDraw, ImageFilter
out, tx, ty, px, py = sys.argv[1], *map(float, sys.argv[2:6])
sw = float(sys.argv[6]) if len(sys.argv) > 6 else 22
S = 3
img = Image.new('RGBA', (1080 * S, 1920 * S), (0, 0, 0, 0))
d = ImageDraw.Draw(img)
ang = math.atan2(py - ty, px - tx)
ux, uy = math.cos(ang), math.sin(ang)
nx, ny = -uy, ux
head_l, head_w = sw * 3.6, sw * 2.6
bx, by = px - ux * head_l, py - uy * head_l
col = (232, 30, 36, 255)
# shaft tapers slightly toward the tail, like a hand-drawn marker arrow
shaft = [(tx + nx * sw * .38, ty + ny * sw * .38), (bx + nx * sw * .55, by + ny * sw * .55),
         (bx - nx * sw * .55, by - ny * sw * .55), (tx - nx * sw * .38, ty - ny * sw * .38)]
head = [(px, py), (bx + nx * head_w, by + ny * head_w), (bx + ux * sw * .6, by + uy * sw * .6), (bx - nx * head_w, by - ny * head_w)]
for poly in (shaft, head):
    d.polygon([(x * S, y * S) for x, y in poly], fill=col)
d.ellipse([(tx - sw * .38) * S, (ty - sw * .38) * S, (tx + sw * .38) * S, (ty + sw * .38) * S], fill=col)
shadow = Image.new('RGBA', img.size, (0, 0, 0, 0))
shadow.paste((0, 0, 0, 110), mask=img.split()[3].filter(ImageFilter.GaussianBlur(5 * S)))
shadow = shadow.transform(img.size, Image.AFFINE, (1, 0, -3 * S, 0, 1, -4 * S))
Image.alpha_composite(shadow, img).resize((1080, 1920), Image.LANCZOS).save(out)
