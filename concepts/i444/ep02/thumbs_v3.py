# EP02 thumbnails v3: A = three Jasons with clear faces, B = split face 90% vs 1%, C = low-battery 1%
import sys
sys.path.insert(0, '../ep01')
from PIL import Image, ImageDraw, ImageFilter
from gfx import f, shadow_text, RED, WHITE
from thumbs_v2_lib import fit, pop
SRC = sys.argv[1]; OUT = sys.argv[2]
W, H = 1280, 720
GREEN = (70, 215, 95, 255); YEL = (250, 200, 40, 255)
def load(n, rot=0):
    im = Image.open(f'{SRC}/{n}.jpg').convert('RGBA')
    return im.rotate(rot, Image.BICUBIC, expand=False) if rot else im
SACK, P4, UBER, P6 = '3g3VSYTiHe8CqkPlbBdlgCFuLZv', 'woOziiDRI1B5Iou3tsNmM05cOau', 'owtvWUhOKGR3GQFiHTtnANMQDhy', '2YEaMi8zXTfMop76zrJs5gxnsMP'
def fade_bottom(im, x0, x1, h=260, a=210):
    g = Image.new('L', (W, H), 0); ImageDraw.Draw(g).rectangle([x0, H - h, x1, H], fill=a); g = g.filter(ImageFilter.GaussianBlur(60))
    im.paste((0, 0, 0, 255), (0, 0), g)

import math
def eye_align(n, el, er, mid=(640, 300), dist=260, size=(W, H)):
    # place a face so its eyes (orig px, scaled-1000 coords x k) sit level at mid, dist apart
    im = load(n); k = im.size[0] / 1000; el = (el[0] * k, el[1] * k); er = (er[0] * k, er[1] * k)
    ang = math.atan2(er[1] - el[1], er[0] - el[0]); sc = dist / math.hypot(er[0] - el[0], er[1] - el[1])
    cx, cy = (el[0] + er[0]) / 2, (el[1] + er[1]) / 2; ca, sa = math.cos(ang) / sc, math.sin(ang) / sc
    # output (x, y) -> input: rotate by ang, scale 1/sc, about eye mid
    a, b = ca, -sa; d_, e = sa, ca
    c = cx - a * mid[0] - b * mid[1]; f_ = cy - d_ * mid[0] - e * mid[1]
    return im.transform(size, Image.AFFINE, (a, b, c, d_, e, f_), Image.BICUBIC, fillcolor=(0, 0, 0, 255))

# A: three Jasons, faces centred and clear, 90% -> 60% -> 1%
im = Image.new('RGBA', (W, H), (0, 0, 0, 255)); pw = W // 3
cols = [(fit(load('5SJyE25gsRGa7edJSAKwd7ATkxd'), 0.6, 0.45, pw, H, 1.0), '90%', GREEN),
        (eye_align(P4, (466, 270), (560, 270), (pw // 2, 260), 120, (pw, H)), '60%', YEL),
        (eye_align(UBER, (455, 156), (545, 156), (pw // 2, 200), 120, (pw, H)), '1%', RED)]
for k, (p, pct, col) in enumerate(cols):
    im.paste(pop(p), (k * pw + 2 + (1 if k == 2 else 0), 0))
    fade_bottom(im, k * pw, (k + 1) * pw)
    shadow_text(im, (k * pw + pw // 2, H - 105), pct, f(170), col, stroke=8)
im.convert('RGB').save(OUT + 'jason_v3_a_three.jpg', quality=93)

# B: one face, two Jasons: left half classic mask (60%), right half Uber Jason (1%), eyes aligned, torn seam
L = pop(eye_align('UEKIznTOOoV3Ko7jg51VoOkFAl', (405, 250), (565, 245))); R = pop(eye_align(UBER, (455, 155), (545, 158)))
m = Image.new('L', (W, H), 0); d = ImageDraw.Draw(m)
import random; random.seed(4); pts = [(W // 2, 0)]
for y in range(40, H, 40): pts.append((W // 2 + random.randint(-18, 18), y))
pts.append((W // 2, H)); d.polygon(pts + [(W, H), (W, 0)], fill=255)
im = Image.composite(R, L, m)
ImageDraw.Draw(im).line(pts, fill=(0, 0, 0, 255), width=10)
fade_bottom(im, 0, W, 230, 200)
shadow_text(im, (W // 4, H - 100), '60%', f(160), YEL, stroke=8)
shadow_text(im, (3 * W // 4, H - 100), '1%', f(160), RED, stroke=8)
im.convert('RGB').save(OUT + 'jason_v3_b_split.jpg', quality=93)

# C: Uber Jason + a dying battery: SURVIVAL 1%
im = pop(eye_align(UBER, (455, 155), (545, 158), (860, 250), 200), 1.1, 1.0, 1.05)
g = Image.new('L', (W, H), 0); ImageDraw.Draw(g).rectangle([0, 0, 560, H], fill=235); g = g.filter(ImageFilter.GaussianBlur(120)); im.paste((0, 0, 0, 255), (0, 0), g)
d = ImageDraw.Draw(im); bx, by, bw, bh = 70, 170, 420, 210
sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle([bx - 6, by - 6, bx + bw + 46, by + bh + 6], 36, fill=(0, 0, 0, 220))
im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14))); d = ImageDraw.Draw(im)
d.rounded_rectangle([bx, by, bx + bw, by + bh], 30, outline=WHITE, width=16)
d.rounded_rectangle([bx + bw + 8, by + bh // 2 - 40, bx + bw + 36, by + bh // 2 + 40], 10, fill=WHITE)
d.rounded_rectangle([bx + 30, by + 30, bx + 58, by + bh - 30], 8, fill=RED)
shadow_text(im, (bx + bw // 2 + 30, by + bh // 2 + 4), '1%', f(130), RED, stroke=6)
shadow_text(im, (bx + 6, by + bh + 120), 'SURVIVAL', f(104), WHITE, anchor='ls', stroke=5)
im.convert('RGB').save(OUT + 'jason_v3_c_battery.jpg', quality=93)
print('ok')
