# Backrooms thumbnail C2 (owner 11/8): the original C's crop and text layout (thumbs_br.py: HOW / LONG? on two lines over the empty yellow
# wall on the left, centres (360,300) and (360,470), size 190, white, stroke 11, shadow, a soft dark ellipse behind it, kept light) with the
# film's natural colour (very light contrast/brightness only, no saturation). usage: python thumbs_br_c2.py <stills_dir> <out_dir>
import os, sys
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from gfx_br import f
SD, OD = sys.argv[1], sys.argv[2]; W, H = 1280, 720
im = Image.open(os.path.join(SD, 'haGqDEzUK9inbfy7sCxmZ0MJMZc.jpg')).convert('RGB')
sw, sh = im.size; cw = min(sw, sh * 16 / 9); ch = cw * 9 / 16
x0 = min(max(0, 0.55 * sw - cw / 2), sw - cw); y0 = min(max(0, 0.5 * sh - ch / 2), sh - ch)
im = im.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((W, H), Image.LANCZOS)
im = ImageEnhance.Contrast(im).enhance(1.06); im = ImageEnhance.Brightness(im).enhance(1.03)
im = im.filter(ImageFilter.UnsharpMask(radius=1.4, percent=60, threshold=3))
m = Image.new('L', (W, H), 0); ImageDraw.Draw(m).ellipse((-200, 130, 860, 620), fill=115); m = m.filter(ImageFilter.GaussianBlur(90))
im = Image.composite(Image.new('RGB', (W, H), (0, 0, 0)), im, m)
def text(im, xy, s, sz, fill, stroke=11):
    im = im.convert('RGBA'); sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(sh)
    d.text((xy[0] + 6, xy[1] + 9), s, font=f(sz), fill=(0, 0, 0, 220), anchor='mm', stroke_width=stroke + 8, stroke_fill=(0, 0, 0, 220))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(12)))
    ImageDraw.Draw(im).text(xy, s, font=f(sz), fill=fill, anchor='mm', stroke_width=stroke, stroke_fill=(0, 0, 0, 255))
    return im.convert('RGB')
im = text(im, (360, 300), 'HOW', 190, (255, 255, 255)); im = text(im, (360, 470), 'LONG?', 190, (255, 255, 255))
im.save(os.path.join(OD, 'backrooms_thumb_c2.jpg'), quality=95); print('ok')
