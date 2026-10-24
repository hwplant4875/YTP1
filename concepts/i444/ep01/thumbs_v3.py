# EP01 thumbnail A v3: three Michaels with the same head size and eye line, 90% -> 62% -> 1%
import sys
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, '.')
from gfx import f, shadow_text, RED
from thumbs_v2_lib import pop
SRC = sys.argv[1]; OUT = sys.argv[2]
W, H = 1280, 720; pw = W // 3
GREEN = (70, 215, 95, 255); YEL = (250, 200, 40, 255)
EYE_Y, MASK_W = 250, 390
def head(n, cx, ey, mask_w):
    # scale so the mask is MASK_W wide, put its centre at the panel middle and its eye line at EYE_Y
    im = Image.open(f'{SRC}/{n}.jpg').convert('RGBA'); s = MASK_W / mask_w
    im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    # feather the photo edges so a still smaller than the panel fades into black
    m = Image.new('L', im.size, 0); ImageDraw.Draw(m).rectangle([40, 40, im.width - 40, im.height - 40], fill=255)
    im.putalpha(m.filter(ImageFilter.GaussianBlur(30)))
    p = Image.new('RGBA', (pw - 4, H), (0, 0, 0, 255)); p.alpha_composite(im, (int((pw - 4) / 2 - cx * s), int(EYE_Y - ey * s)))
    return p
panels = [('eBK1p5HNdt24h1guJTtrivOZCXg', 1860, 626, 1900, '90%', GREEN),
          ('aPTYPRVECq2spuLze93hTYSAeIF', 2669, 503, 650, '62%', YEL),
          ('fuuZFPc8x6gQ8mLGoBp9vrmcQMT', 1056, 526, 460, '1%', RED)]
im = Image.new('RGBA', (W, H), (0, 0, 0, 255))
for k, (n, cx, ey, mw, pct, col) in enumerate(panels):
    im.paste(pop(head(n, cx, ey, mw)), (k * pw + 2 + (1 if k == 2 else 0), 0))
    g = Image.new('L', (W, H), 0); ImageDraw.Draw(g).rectangle([k * pw, H - 250, (k + 1) * pw, H], fill=200); g = g.filter(ImageFilter.GaussianBlur(60))
    im.paste((0, 0, 0, 255), (0, 0), g)
    shadow_text(im, (k * pw + pw // 2, H - 105), pct, f(170), col, stroke=8)
im.convert('RGB').save(OUT + 'myers_v3_a_three.jpg', quality=93)
