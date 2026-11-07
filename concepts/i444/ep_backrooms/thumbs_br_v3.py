# Backrooms special thumbnails v3 (owner 11/7 21:36 KST: "눈에 잘 띄게, 색감이랑 명암 등 조정해서"). Same three ideas as thumbs_br.py on the
# official TMDB stills (never committed), regraded to read at 168x94: deep blacks, saturated Backrooms yellow, a vignette, sharpening,
# a lit subject, and bigger text with a red/yellow glow. usage: python thumbs_br_v3.py <stills_dir (thumbs_br.py downloads)> <out_dir>
import os, sys
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageChops
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from gfx_br import f
SD, OD = sys.argv[1], sys.argv[2]; os.makedirs(OD, exist_ok=True)
W, H = 1280, 720
RED, YEL, WHITE = (255, 32, 32), (255, 214, 0), (255, 255, 255)
IDS = {'a': 'qH4e3SQFkgrr7doxm7FZF61gUUO', 'b': 'xG05IQIP5Hy16xff6DptYphyMHE', 'c': 'haGqDEzUK9inbfy7sCxmZ0MJMZc'}
def still(k): return Image.open(os.path.join(SD, IDS[k] + '.jpg')).convert('RGB')
def fill(im, cx=0.5, cy=0.5, zoom=1.0):
    sw, sh = im.size; cw = min(sw, sh * 16 / 9) / zoom; ch = cw * 9 / 16
    x0 = min(max(0, cx * sw - cw / 2), sw - cw); y0 = min(max(0, cy * sh - ch / 2), sh - ch)
    return im.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((W, H), Image.LANCZOS)
def curve(im, lift=0.0, gamma=1.0, gain=1.0):
    lut = [min(255, max(0, int(255 * (max(0, i / 255 - lift) / (1 - lift)) ** gamma * gain))) for i in range(256)]
    return im.point(lut * 3)
def grade(im, sat=1.5, con=1.35, bright=1.05, black=0.06, gamma=0.95):
    im = curve(im, lift=black, gamma=gamma)                      # crush the blacks
    im = ImageEnhance.Contrast(im).enhance(con); im = ImageEnhance.Color(im).enhance(sat); im = ImageEnhance.Brightness(im).enhance(bright)
    return im.filter(ImageFilter.UnsharpMask(radius=2.2, percent=140, threshold=2))
def warm(im, amt=0.18):  # push the Backrooms yellow
    r, g, b = im.split(); r = r.point(lambda v: min(255, int(v * (1 + amt * 0.6)))); g = g.point(lambda v: min(255, int(v * (1 + amt * 0.45))))
    b = b.point(lambda v: int(v * (1 - amt))); return Image.merge('RGB', (r, g, b))
def light(im, box, gain=1.35, blur=120):  # lift the subject
    m = Image.new('L', (W, H), 0); ImageDraw.Draw(m).ellipse(box, fill=255); m = m.filter(ImageFilter.GaussianBlur(blur))
    return Image.composite(ImageEnhance.Brightness(im).enhance(gain), im, m)
def vignette(im, strength=0.55):
    m = Image.new('L', (W, H), 0); ImageDraw.Draw(m).ellipse((-W * 0.15, -H * 0.2, W * 1.15, H * 1.2), fill=255)
    m = m.filter(ImageFilter.GaussianBlur(160)); dark = ImageEnhance.Brightness(im).enhance(1 - strength)
    return Image.composite(im, dark, m)
def shade(im, box, alpha=210, blur=90):
    m = Image.new('L', (W, H), 0); ImageDraw.Draw(m).ellipse(box, fill=alpha); m = m.filter(ImageFilter.GaussianBlur(blur))
    return Image.composite(Image.new('RGB', (W, H), (0, 0, 0)), im, m)
def text(im, xy, s, sz, fill, anchor='mm', stroke=12, glow=None):
    im = im.convert('RGBA'); fnt = f(sz)
    if glow:
        g = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(g).text(xy, s, font=fnt, fill=glow + (255,), anchor=anchor, stroke_width=stroke + 18, stroke_fill=glow + (255,))
        im.alpha_composite(g.filter(ImageFilter.GaussianBlur(26)))
    sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).text((xy[0] + 8, xy[1] + 12), s, font=fnt, fill=(0, 0, 0, 235), anchor=anchor,
                                                                         stroke_width=stroke + 10, stroke_fill=(0, 0, 0, 235))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
    ImageDraw.Draw(im).text(xy, s, font=fnt, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=(0, 0, 0, 255))
    return im.convert('RGB')
# A: Captain Clark's face lit and saturated, a huge red 2% with a red glow on the dark right side
a = fill(still('a'), cx=0.40, cy=0.45, zoom=1.08); a = grade(a, sat=1.55, con=1.4, bright=1.08); a = warm(a, 0.12)
a = light(a, (60, 40, 760, 700), 1.3); a = shade(a, (720, 60, 1560, 860), 225); a = vignette(a, 0.5)
a = text(a, (1040, 380), '2%', 340, RED, stroke=14, glow=(170, 0, 0))
a.save(os.path.join(OD, 'backrooms_thumb_a.jpg'), quality=95)
# B: the endless yellow corridor, vivid yellow, the corridor end lit, 1 OF 5 big with a yellow glow
b = fill(still('b'), cx=0.5, cy=0.52, zoom=1.12); b = grade(b, sat=1.75, con=1.38, bright=1.06, black=0.05); b = warm(b, 0.22)
b = light(b, (430, 160, 850, 560), 1.25, 90); b = vignette(b, 0.6); b = shade(b, (260, -160, 1020, 250), 190, 80)
b = text(b, (640, 120), '1 OF 5', 180, WHITE, stroke=12, glow=(0, 0, 0))
im = b.convert('RGBA'); ImageDraw.Draw(im)  # colour the "1" red on top
b = text(im.convert('RGB'), (640 - f(180).getlength('1 OF 5') / 2, 120), '1', 180, RED, anchor='lm', stroke=12)
b.save(os.path.join(OD, 'backrooms_thumb_b.jpg'), quality=95)
# C: Mary against the yellow wall, her face lit, HOW LONG? in white over a deep shadow, yellow glow
c = fill(still('c'), cx=0.62, cy=0.45, zoom=1.05); c = grade(c, sat=1.6, con=1.38, bright=1.05); c = warm(c, 0.2)
c = light(c, (760, 40, 1300, 620), 1.3); c = shade(c, (-200, 60, 760, 760), 215); c = vignette(c, 0.45)
c = text(c, (400, 250), 'HOW', 190, WHITE, stroke=12, glow=(120, 90, 0)); c = text(c, (400, 450), 'LONG?', 190, YEL, stroke=12, glow=(120, 90, 0))
c.save(os.path.join(OD, 'backrooms_thumb_c.jpg'), quality=95)
print('ok', OD)
