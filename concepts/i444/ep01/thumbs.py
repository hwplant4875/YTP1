# EP01 thumbnails (1280x720) from HD stills
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import sys
sys.path.insert(0, '.')
from gfx import f, shadow_text, RED, WHITE
OUT = '/mnt/project-files/instruction444/ep01_myers_ranked/thumbs/'
def still(n): return Image.open('stills/' + n).convert('RGBA')
def crop(im, box, size): return im.crop(box).resize(size, Image.LANCZOS)
def pop(im, c=1.25, b=1.15): return ImageEnhance.Brightness(ImageEnhance.Contrast(im).enhance(c)).enhance(b)
W, H = 1280, 720
GREEN = (60, 200, 90, 255); YEL = (240, 190, 40, 255)

# t1: Michael walking out of the fire + giant 1%
im = pop(crop(still('kills_firefighters_90_b.jpg'), (120, 140, 1460, 894), (W, H)), 1.2, 1.25)
g = Image.new('L', (W, H), 0); ImageDraw.Draw(g).rectangle([0, 0, 520, H], fill=230); g = g.filter(ImageFilter.GaussianBlur(120))
im.paste((0, 0, 0, 255), (0, 0), g)
shadow_text(im, (60, 470), '1%', f(300), RED, anchor='ls', stroke=6)
shadow_text(im, (70, 560), 'SURVIVAL RATE', f(64), WHITE, anchor='ls', stroke=3)
im.convert('RGB').save(OUT + 'myers_t1_fire.jpg', quality=92)

# t2: four Michaels, survival rate falling
src = [('1978_every_scene_548.8_b.jpg', (1420, 160, 1820, 1050), '41%', YEL),
       ('rz_2007_trailer_54_b.jpg', (590, 200, 990, 1080), '28%', RED),
       ('curse_tommy_defeats_michael_hd_36_b.jpg', (520, 60, 1300, 1080), '5%', RED),
       ('kills_firefighters_90_b.jpg', (520, 300, 980, 1000), '1%', RED)]
im = Image.new('RGBA', (W, H), (0, 0, 0, 255)); cw = W // 4
for k, (n, box, pct, col) in enumerate(src):
    p = pop(crop(still(n), box, (cw - 6, H)), 1.3, 1.3 if k > 1 else 1.9); im.paste(p, (k * cw + 3, 0))
    shadow_text(im, (k * cw + cw // 2, H - 90), pct, f(130), col, stroke=6)
im.convert('RGB').save(OUT + 'myers_t2_lineup.jpg', quality=92)

# t3: giant mask close-up + one red word
im = pop(crop(still('curse_tommy_defeats_michael_hd_36_b.jpg'), (420, 60, 1880, 881), (W, H)), 1.15, 1.1)
g = Image.new('L', (W, H), 0); ImageDraw.Draw(g).rectangle([0, 0, 470, H], fill=235); g = g.filter(ImageFilter.GaussianBlur(110))
im.paste((0, 0, 0, 255), (0, 0), g)
shadow_text(im, (50, 330), 'KILL', f(190), WHITE, anchor='ls', stroke=6)
shadow_text(im, (50, 520), 'HIM?', f(190), RED, anchor='ls', stroke=6)
im.convert('RGB').save(OUT + 'myers_t3_mask.jpg', quality=92)
