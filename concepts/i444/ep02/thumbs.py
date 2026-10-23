# EP02 thumbnails: sharp official stills (TMDB backdrops), 1280x720
import sys
sys.path.insert(0, '../ep01')
from PIL import Image, ImageDraw, ImageFilter
from gfx import f, shadow_text, RED, WHITE
from thumbs_v2_lib import fit, pop, shade_left
SRC = sys.argv[1]; OUT = '/mnt/project-files/instruction444/ep02_jason_ranked/thumbs/'
W, H = 1280, 720
GREEN = (70, 215, 95, 255); YEL = (250, 200, 40, 255)
def load(n): return Image.open(f'{SRC}/{n}.jpg').convert('RGBA')

# A: three Jasons, 90% -> 60% -> 1%
panels = [('5SJyE25gsRGa7edJSAKwd7ATkxd', 0.6, 0.45, 1.0, '90%', GREEN),
          ('UEKIznTOOoV3Ko7jg51VoOkFAl', 0.5, 0.45, 1.0, '60%', YEL),
          ('owtvWUhOKGR3GQFiHTtnANMQDhy', 0.58, 0.4, 1.05, '1%', RED)]
im = Image.new('RGBA', (W, H), (0, 0, 0, 255)); pw = W // 3
for k, (n, cx, cy, z, pct, col) in enumerate(panels):
    im.paste(pop(fit(load(n), cx, cy, pw - 4, H, z)), (k * pw + 2 + (1 if k == 2 else 0), 0))
    g = Image.new('L', (W, H), 0); ImageDraw.Draw(g).rectangle([k * pw, H - 250, (k + 1) * pw, H], fill=200); g = g.filter(ImageFilter.GaussianBlur(60))
    im.paste((0, 0, 0, 255), (0, 0), g)
    shadow_text(im, (k * pw + pw // 2, H - 105), pct, f(170), col, stroke=8)
im.convert('RGB').save(OUT + 'jason_a_three.jpg', quality=93)

# B: Uber Jason + 1% SURVIVAL RATE
im = pop(fit(load('owtvWUhOKGR3GQFiHTtnANMQDhy'), 0.6, 0.45, W, H, 1.05), 1.1, 1.05, 1.05)
shade_left(im, 560)
shadow_text(im, (60, 430), '1%', f(330), RED, anchor='ls', stroke=8)
shadow_text(im, (72, 530), 'SURVIVAL RATE', f(70), WHITE, anchor='ls', stroke=4)
im.convert('RGB').save(OUT + 'jason_b_onepercent.jpg', quality=93)

# C: Jason Lives in the woods + KILL HIM?
im = pop(fit(load('2YEaMi8zXTfMop76zrJs5gxnsMP'), 0.45, 0.45, W, H, 1.04), 1.1, 1.1, 1.05)
g = Image.new('L', (W, H), 0); ImageDraw.Draw(g).rectangle([W - 470, 0, W, H], fill=225); g = g.filter(ImageFilter.GaussianBlur(110)); im.paste((0, 0, 0, 255), (0, 0), g)
shadow_text(im, (W - 50, 330), 'KILL', f(200), WHITE, anchor='rs', stroke=7)
shadow_text(im, (W - 50, 540), 'HIM?', f(200), RED, anchor='rs', stroke=7)
im.convert('RGB').save(OUT + 'jason_c_killhim.jpg', quality=93)
