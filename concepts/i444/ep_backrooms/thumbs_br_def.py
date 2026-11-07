# Backrooms thumbnails D/E/F (owner 11/8): frames from the owner's film file (never committed), the film's natural colour with only a light
# contrast/brightness lift, one big text each (YouTube Sans Black, black stroke + shadow, dark gradient under it), bottom-right kept clear.
#   D  the empty yellow Backrooms rooms (film 1749.3)                 + TRAPPED..?   (pure Backrooms space, huge text)
#   E  Captain Clark in full costume, lit, in the copied store (5572.3) + SURVIVED?
#   F  Mary dragged out by the yellow/green hazmat team (5749.5)      + 1 OF 5
# usage: python thumbs_br_def.py <film.mkv> <out_dir>
import os, sys, subprocess, io
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from gfx_br import f
FILM, OD = sys.argv[1], sys.argv[2]; W, H = 1280, 720
RED, WHITE = (255, 36, 36), (255, 255, 255)
def frame(t):
    png = subprocess.check_output(['ffmpeg', '-v', 'error', '-ss', str(t), '-i', FILM, '-frames:v', '1', '-f', 'image2pipe', '-vcodec', 'png', '-'])
    return Image.open(io.BytesIO(png)).convert('RGB')
def fill(im, cx=0.5, cy=0.5, zoom=1.0):
    sw, sh = im.size; cw = min(sw, sh * 16 / 9) / zoom; ch = cw * 9 / 16
    x0 = min(max(0, cx * sw - cw / 2), sw - cw); y0 = min(max(0, cy * sh - ch / 2), sh - ch)
    return im.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((W, H), Image.LANCZOS)
def lift(im, con=1.12, bri=1.06):   # light touch only (owner: keep the film's natural look)
    im = ImageEnhance.Contrast(im).enhance(con); im = ImageEnhance.Brightness(im).enhance(bri)
    return im.filter(ImageFilter.UnsharpMask(radius=1.6, percent=80, threshold=3))
def gradient(im, top, bottom, alpha=170):  # a soft dark band under the text
    m = Image.new('L', (W, H), 0); d = ImageDraw.Draw(m)
    for y in range(H):
        a = 0
        if top <= y <= bottom: a = alpha
        elif y < top: a = max(0, alpha - (top - y) * 2.2)
        else: a = max(0, alpha - (y - bottom) * 2.2)
        d.line([(0, y), (W, y)], fill=int(a))
    return Image.composite(Image.new('RGB', (W, H), (0, 0, 0)), im, m.filter(ImageFilter.GaussianBlur(20)))
def text(im, xy, s, sz, fill, anchor='mm', stroke=13):
    while f(sz).getlength(s) > 1180 and sz > 80: sz -= 4
    im = im.convert('RGBA'); fnt = f(sz)
    sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).text((xy[0] + 8, xy[1] + 12), s, font=fnt, fill=(0, 0, 0, 230), anchor=anchor,
                                                                         stroke_width=stroke + 10, stroke_fill=(0, 0, 0, 230))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(11)))
    ImageDraw.Draw(im).text(xy, s, font=fnt, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=(0, 0, 0, 255))
    return im.convert('RGB')
# D: pure Backrooms, the text huge across the upper half
d = lift(fill(frame(1749.3), 0.5, 0.55, 1.0), 1.1, 1.04); d = gradient(d, 120, 300, 150)
d = text(d, (640, 215), 'TRAPPED..?', 230, RED); d.save(os.path.join(OD, 'backrooms_thumb_d.jpg'), quality=95)
# E: Captain Clark big over Mary, text top-left over the ceiling
e = lift(fill(frame(5572.3), 0.43, 0.42, 1.7), 1.12, 1.06); e = gradient(e, 20, 170, 150)
e = text(e, (640, 100), 'SURVIVED?', 175, WHITE); e.save(os.path.join(OD, 'backrooms_thumb_e.jpg'), quality=95)
# F: Mary pulled out by hazmat, text top-left
g = lift(fill(frame(5749.5), 0.5, 0.5, 1.0), 1.12, 1.08); g = gradient(g, 30, 190, 160)
g = text(g, (370, 115), '1 OF 5', 200, WHITE)
g = text(g, (370 - f(200).getlength('1 OF 5') / 2, 115), '1', 200, RED, anchor='lm')
g.save(os.path.join(OD, 'backrooms_thumb_f.jpg'), quality=95)
print('ok')
