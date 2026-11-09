# Backrooms three-panel % thumbnails B and C (channel format, same build as thumbs_3panel.py's variant A: panels 427/426/427, numbers
# low at H-115 on a dark shadow, green / yellow / red, natural colour with a light lift). Faces are sharp frames from the owner's film file
# (never committed), different from A (TMDB stills s24 / s0 / bd103) and from each other.
#   B  Clark in the yellow room (film 1566.5) 90% | Kat, scared, on Bobby's camcorder (2769.4) 15% | Captain Clark's face, tight (sharpest frame of the store shot; C uses a wider frame of it) 2%  (the 5259 neck shot showed the bite)
#   C  Clark tired in his store (d_clark_discovers 24.0) 90% | Mary at Async (6125.0) 40% | Captain Clark in full costume (5571.9) 2%
# usage: python thumbs_3panel_bc.py <frames_dir (f_<t>.png)> <out_dir>
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from gfx_br import f
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
SD, OD = sys.argv[1], sys.argv[2]
W, H = 1280, 720; PW = [427, 426, 427]; COL = [(70, 215, 95), (250, 200, 40), (235, 30, 38)]
def panel(fn, cx, cy, chf, pw, b=1.05):
    im = Image.open(os.path.join(SD, fn)).convert('RGB'); sw, sh = im.size; ch = chf * sh; cw = ch * pw / H
    x0 = min(max(0, cx * sw - cw / 2), sw - cw); y0 = min(max(0, cy * sh - ch * 0.30), sh - ch)   # cy = the eye line in the source: eyes land ~30% from the top (owner 11/9: B/C faces sat too low)
    p = im.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((pw, H), Image.LANCZOS)
    p = ImageEnhance.Brightness(p).enhance(b); p = ImageEnhance.Contrast(p).enhance(1.12)
    p = p.filter(ImageFilter.UnsharpMask(radius=2, percent=60, threshold=2))
    g = Image.new('L', (pw, H), 0); d = ImageDraw.Draw(g)
    for y in range(H // 2, H): d.line([(0, y), (pw, y)], fill=int(235 * ((y - H / 2) / (H / 2)) ** 1.2))
    return Image.composite(Image.new('RGB', (pw, H)), p, g)
def build(specs, out):
    im = Image.new('RGB', (W, H)); x = 0
    for (fn, cx, cy, chf, b, pct), pw, c in zip(specs, PW, COL):
        p = panel(fn, cx, cy, chf, pw, b).convert('RGBA'); sh = Image.new('RGBA', (pw, H), (0, 0, 0, 0)); d = ImageDraw.Draw(sh)
        d.text((pw / 2 + 5, H - 115 + 8), pct, font=f(182), fill=(0, 0, 0, 220), anchor='mm', stroke_width=14, stroke_fill=(0, 0, 0, 220))
        p.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)))
        ImageDraw.Draw(p).text((pw / 2, H - 115), pct, font=f(182), fill=c, anchor='mm', stroke_width=8, stroke_fill=(0, 0, 0))
        im.paste(p.convert('RGB'), (x, 0)); x += pw
    d = ImageDraw.Draw(im); d.rectangle((426, 0, 429, H), fill=0); d.rectangle((852, 0, 855, H), fill=0)
    im.save(os.path.join(OD, out), quality=93)
# (file, centre x, eye-line y, crop height as a fraction of the frame, brightness, number)
build([('f_1566.5.png', 0.56, 0.32, 0.50, 1.05, '90%'), ('f_2769.4.png', 0.555, 0.16, 0.70, 1.08, '15%'),
       ('f_cap11.png', 0.498, 0.366, 0.30, 1.12, '2%')], 'backrooms_thumb_3p_b.jpg')
build([('f_clark_store.png', 0.50, 0.41, 0.55, 1.15, '90%'), ('f_6125.0.png', 0.48, 0.44, 0.50, 1.05, '40%'),
       ('f_cap12.png', 0.49, 0.384, 0.40, 1.12, '2%')], 'backrooms_thumb_3p_c.jpg')
print('ok')