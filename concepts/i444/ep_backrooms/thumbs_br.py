# Backrooms special thumbnails (11/7 KST): single scenes, not the three-panel ranking layout (this episode must look different).
# Official TMDB stills of Backrooms (2026, TMDB 1083381), downloaded into a scratch folder and never committed:
#   A  Captain Clark's face, Mary's hand on it (qH4e3SQFkgrr7doxm7FZF61gUUO) + a huge red 2%  (the lowest survival in the video)
#   B  Clark walking down the endless yellow corridor, a tiny figure at the far end (xG05IQIP5Hy16xff6DptYphyMHE) + 1 OF 5
#   C  Mary pressed against the yellow wall (haGqDEzUK9inbfy7sCxmZ0MJMZc) + HOW LONG?
# Text: YouTube Sans Black, black stroke, soft shadow, a dark gradient under the text so it pops (channel rule).
# usage: python thumbs_br.py <stills_dir> <out_dir>
import os, sys, urllib.request
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from gfx_br import f, WHITE, RED
SD, OD = sys.argv[1], sys.argv[2]; os.makedirs(SD, exist_ok=True); os.makedirs(OD, exist_ok=True)
W, H = 1280, 720
IDS = {'a': 'qH4e3SQFkgrr7doxm7FZF61gUUO', 'b': 'xG05IQIP5Hy16xff6DptYphyMHE', 'c': 'haGqDEzUK9inbfy7sCxmZ0MJMZc'}
def still(k):
    p = os.path.join(SD, IDS[k] + '.jpg')
    if not os.path.exists(p):
        req = urllib.request.Request(f'https://image.tmdb.org/t/p/original/{IDS[k]}.jpg', headers={'User-Agent': 'Mozilla/5.0'})
        open(p, 'wb').write(urllib.request.urlopen(req, timeout=60).read())
    return Image.open(p).convert('RGB')
def fill(im, cx=0.5, cy=0.5, zoom=1.0):
    """crop to 16:9 around (cx, cy) (fractions of the source), zoom > 1 crops tighter, then scale to 1280x720"""
    sw, sh = im.size; cw = min(sw, sh * 16 / 9) / zoom; ch = cw * 9 / 16
    x0 = min(max(0, cx * sw - cw / 2), sw - cw); y0 = min(max(0, cy * sh - ch / 2), sh - ch)
    return im.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((W, H), Image.LANCZOS)
def grade(im, b=1.0, c=1.12, s=1.05):
    im = ImageEnhance.Brightness(im).enhance(b); im = ImageEnhance.Contrast(im).enhance(c); return ImageEnhance.Color(im).enhance(s)
def shade(im, box, alpha=200, blur=90):
    m = Image.new('L', (W, H), 0); ImageDraw.Draw(m).ellipse(box, fill=alpha); m = m.filter(ImageFilter.GaussianBlur(blur))
    return Image.composite(Image.new('RGB', (W, H), (0, 0, 0)), im, m)
def text(im, xy, s, sz, fill, anchor='mm', stroke=10):
    im = im.convert('RGBA'); sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(sh)
    d.text((xy[0] + 6, xy[1] + 9), s, font=f(sz), fill=(0, 0, 0, 220), anchor=anchor, stroke_width=stroke + 8, stroke_fill=(0, 0, 0, 220))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(12)))
    ImageDraw.Draw(im).text(xy, s, font=f(sz), fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=(0, 0, 0, 255))
    return im.convert('RGB')
# A: Captain Clark, the face on the left two thirds, 2% on the right
a = grade(fill(still('a'), cx=0.42, cy=0.45, zoom=1.0), b=1.08, c=1.15)
a = shade(a, (760, 120, 1500, 860), 215)
a = text(a, (1035, 380), '2%', 300, RED, stroke=12)
a.save(os.path.join(OD, 'backrooms_thumb_a.jpg'), quality=92)
# B: the endless corridor, 1 OF 5 across the ceiling
b = grade(fill(still('b'), cx=0.5, cy=0.5, zoom=1.0), b=1.0, c=1.15, s=1.1)
b = shade(b, (170, -260, 1110, 330), 190)
im = b.convert('RGBA'); d = ImageDraw.Draw(im); sz = 190; s1, s2 = '1 ', 'OF 5'; w1, w2 = f(sz).getlength(s1), f(sz).getlength(s2)
x0 = W / 2 - (w1 + w2) / 2
b = text(im.convert('RGB'), (x0, 135), s1, sz, RED, anchor='lm'); b = text(b, (x0 + w1, 135), s2, sz, WHITE, anchor='lm')
b.save(os.path.join(OD, 'backrooms_thumb_b.jpg'), quality=92)
# C: Mary against the wall on the right, HOW LONG? over the empty yellow wall on the left
c = grade(fill(still('c'), cx=0.55, cy=0.5, zoom=1.0), b=1.0, c=1.12)
c = shade(c, (-200, 130, 860, 620), 170)
c = text(c, (360, 300), 'HOW', 190, WHITE, stroke=11); c = text(c, (360, 470), 'LONG?', 190, WHITE, stroke=11)
c.save(os.path.join(OD, 'backrooms_thumb_c.jpg'), quality=92)
print('ok', OD)
