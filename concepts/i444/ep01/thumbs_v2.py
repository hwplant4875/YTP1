# EP01 thumbnails v2: sharp official stills (TMDB backdrops), 1280x720
import sys
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
sys.path.insert(0, '.')
from gfx import f, shadow_text, RED, WHITE
SRC = sys.argv[1]; OUT = '/mnt/project-files/instruction444/ep01_myers_ranked/thumbs/'
W, H = 1280, 720
GREEN = (70, 215, 95, 255); YEL = (250, 200, 40, 255)
def load(n): return Image.open(f'{SRC}/{n}.jpg').convert('RGBA')
def fit(im, cx, cy, w, h, zoom=1.0):
    # crop box of aspect w:h centred on (cx, cy) fractions, scaled by zoom (1 = full height)
    iw, ih = im.size; ch = ih / zoom; cw = ch * w / h
    if cw > iw: cw = iw; ch = cw * h / w
    x0 = min(max(cx * iw - cw / 2, 0), iw - cw); y0 = min(max(cy * ih - ch / 2, 0), ih - ch)
    return im.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((w, h), Image.LANCZOS)
def pop(im, c=1.1, b=1.05, s=1.1): return ImageEnhance.Color(ImageEnhance.Brightness(ImageEnhance.Contrast(im).enhance(c)).enhance(b)).enhance(s)
def shade_left(im, width, a=235):
    g = Image.new('L', im.size, 0); ImageDraw.Draw(g).rectangle([0, 0, width, im.size[1]], fill=a); g = g.filter(ImageFilter.GaussianBlur(width * 0.25))
    im.paste((0, 0, 0, 255), (0, 0), g)

# 2a: three Michaels, 90% -> 62% -> 1%
panels = [('eBK1p5HNdt24h1guJTtrivOZCXg', 0.5, 0.5, 1.0, '90%', GREEN),
          ('aPTYPRVECq2spuLze93hTYSAeIF', 0.66, 0.42, 1.5, '62%', YEL),
          ('fuuZFPc8x6gQ8mLGoBp9vrmcQMT', 0.5, 0.45, 1.1, '1%', RED)]
im = Image.new('RGBA', (W, H), (0, 0, 0, 255)); pw = W // 3
for k, (n, cx, cy, z, pct, col) in enumerate(panels):
    im.paste(pop(fit(load(n), cx, cy, pw - 4, H, z)), (k * pw + 2 + (1 if k == 2 else 0), 0))
    g = Image.new('L', (W, H), 0); ImageDraw.Draw(g).rectangle([k * pw, H - 250, (k + 1) * pw, H], fill=200); g = g.filter(ImageFilter.GaussianBlur(60))
    im.paste((0, 0, 0, 255), (0, 0), g)
    shadow_text(im, (k * pw + pw // 2, H - 105), pct, f(170), col, stroke=8)
im.convert('RGB').save(OUT + 'myers_v2_a_three.jpg', quality=93)

# 2b: burnt Kills mask + 1% SURVIVAL RATE
im = pop(fit(load('5P0PtxIneLNMq7m0crF1R9Sjzpv'), 0.62, 0.5, W, H, 1.0), 1.1, 1.05, 1.05)
shade_left(im, 560)
shadow_text(im, (60, 430), '1%', f(330), RED, anchor='ls', stroke=8)
shadow_text(im, (72, 530), 'SURVIVAL RATE', f(70), WHITE, anchor='ls', stroke=4)
im.convert('RGB').save(OUT + 'myers_v2_b_onepercent.jpg', quality=93)

# 2c: Michael with the knife + KILL HIM?
im = pop(fit(load('czRXzKy5YcvoVhRUb8RQsFHUDi1'), 0.62, 0.45, W, H, 1.15), 1.1, 1.1, 1.05)
shade_left(im, 520)
shadow_text(im, (55, 330), 'KILL', f(200), WHITE, anchor='ls', stroke=7)
shadow_text(im, (55, 540), 'HIM?', f(200), RED, anchor='ls', stroke=7)
im.convert('RGB').save(OUT + 'myers_v2_c_killhim.jpg', quality=93)
