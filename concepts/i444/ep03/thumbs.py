# EP03 thumbnails: A = mask -> Ethan -> Wayne (85/53/22), B = split mask vs Wayne, C = one mask, 16 killers
import sys, math, random
sys.path.insert(0, '../ep01')
from PIL import Image, ImageDraw, ImageFilter
from gfx import f, shadow_text, RED, WHITE
from thumbs_v2_lib import pop
SRC = sys.argv[1]; OUT = sys.argv[2]
W, H = 1280, 720
GREEN = (70, 215, 95, 255); YEL = (250, 200, 40, 255)
def load(n): return Image.open(f'{SRC}/{n}.jpg').convert('RGBA')
def eye_align(n, el, er, mid=(640, 300), dist=260, size=(W, H)):
    im = load(n); k = im.size[0] / 1000; el = (el[0] * k, el[1] * k); er = (er[0] * k, er[1] * k)
    ang = math.atan2(er[1] - el[1], er[0] - el[0]); sc = dist / math.hypot(er[0] - el[0], er[1] - el[1])
    cx, cy = (el[0] + er[0]) / 2, (el[1] + er[1]) / 2; ca, sa = math.cos(ang) / sc, math.sin(ang) / sc
    a, b = ca, -sa; d_, e = sa, ca
    c = cx - a * mid[0] - b * mid[1]; f_ = cy - d_ * mid[0] - e * mid[1]
    return im.transform(size, Image.AFFINE, (a, b, c, d_, e, f_), Image.BICUBIC, fillcolor=(0, 0, 0, 255))
def fade_bottom(im, x0, x1, h=260, a=210):
    g = Image.new('L', (W, H), 0); ImageDraw.Draw(g).rectangle([x0, H - h, x1, H], fill=a); g = g.filter(ImageFilter.GaussianBlur(60))
    im.paste((0, 0, 0, 255), (0, 0), g)
MASK, ETHAN, WAYNE = ('mask', (458, 167), (533, 167)), ('ethan', (397, 155), (575, 155)), ('wayne', (408, 272), (567, 272))
# A: three panels, eyes level, 85% -> 53% -> 22%
im = Image.new('RGBA', (W, H), (0, 0, 0, 255)); pw = W // 3
for k, ((n, el, er), pct, col, dist) in enumerate([(MASK, '85%', GREEN, 110), (ETHAN, '53%', YEL, 175), (WAYNE, '22%', RED, 175)]):
    im.paste(pop(eye_align(n, el, er, (pw // 2, 250), dist, (pw, H))), (k * pw + 2, 0))
    fade_bottom(im, k * pw, (k + 1) * pw)
    shadow_text(im, (k * pw + pw // 2, H - 105), pct, f(170), col, stroke=8)
im.convert('RGB').save(OUT + 'ghostface_a_three.jpg', quality=93)
# B: one face, mask on the left half, the man under it on the right
L = pop(eye_align(*MASK, (640, 300), 210)); R = pop(eye_align(*WAYNE, (640, 300), 260))
m = Image.new('L', (W, H), 0); d = ImageDraw.Draw(m); random.seed(4); pts = [(W // 2, 0)]
for y in range(40, H, 40): pts.append((W // 2 + random.randint(-18, 18), y))
pts.append((W // 2, H)); d.polygon(pts + [(W, H), (W, 0)], fill=255)
im = Image.composite(R, L, m); ImageDraw.Draw(im).line(pts, fill=(0, 0, 0, 255), width=10)
fade_bottom(im, 0, W, 230, 200)
shadow_text(im, (W // 4, H - 100), '85%', f(160), GREEN, stroke=8)
shadow_text(im, (3 * W // 4, H - 100), '22%', f(160), RED, stroke=8)
im.convert('RGB').save(OUT + 'ghostface_b_split.jpg', quality=93)
# C: the mask on the right, 16 KILLERS / 1 MASK on the left
im = pop(eye_align(*MASK, (880, 250), 190), 1.1, 1.0, 1.05)
g = Image.new('L', (W, H), 0); ImageDraw.Draw(g).rectangle([0, 0, 560, H], fill=235); g = g.filter(ImageFilter.GaussianBlur(120)); im.paste((0, 0, 0, 255), (0, 0), g)
shadow_text(im, (300, 215), '16', f(260), RED, stroke=10)
shadow_text(im, (300, 440), 'KILLERS', f(110), WHITE, stroke=8)
shadow_text(im, (300, 575), '1 MASK', f(110), WHITE, stroke=8)
im.convert('RGB').save(OUT + 'ghostface_c_16.jpg', quality=93)
