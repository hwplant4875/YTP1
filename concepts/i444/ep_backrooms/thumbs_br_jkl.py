# Backrooms thumbnails J/K/L (owner 11/8: "기존 잘나가는 유튜브 비디오 썸네일들 처럼 해"). What the top Backrooms / horror-survival videos do
# (ScreenCrush, Film Theory, Wendigoon, penguinz0 ...): ONE big emotional face that fills half the frame, a clean simple background (the
# yellow Backrooms) pushed back with a little blur and shade so the face pops, and 1-3 huge words with a heavy black outline. Nothing else.
# Here: a sharp subject cutout (birefnet-portrait) over a clean empty Backrooms plate, natural film colour, text at the bottom centre,
# bottom-right kept clear for the duration badge.
# usage: python thumbs_br_jkl.py <film.mkv> <stills_dir> <work_dir> <out_dir>
import os, sys, subprocess, io
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from gfx_br import f
FILM, SD, WD, OD = sys.argv[1:5]; os.makedirs(WD, exist_ok=True); W, H = 1280, 720
def frame(t):
    png = subprocess.check_output(['ffmpeg', '-v', 'error', '-ss', str(t), '-i', FILM, '-frames:v', '1', '-f', 'image2pipe', '-vcodec', 'png', '-'])
    return Image.open(io.BytesIO(png)).convert('RGB')
def cut(name, im):
    p = os.path.join(WD, name + '_cut.png')
    if not os.path.exists(p):
        from rembg import remove, new_session
        remove(im, session=new_session('birefnet-portrait'), post_process_mask=True).save(p)
    c = Image.open(p).convert('RGBA'); a = c.getchannel('A').filter(ImageFilter.GaussianBlur(1.2)); c.putalpha(a); return c.crop(c.getbbox())
def fill(im, cx=0.5, cy=0.5, zoom=1.0):
    sw, sh = im.size; cw = min(sw, sh * 16 / 9) / zoom; ch = cw * 9 / 16
    x0 = min(max(0, cx * sw - cw / 2), sw - cw); y0 = min(max(0, cy * sh - ch / 2), sh - ch)
    return im.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((W, H), Image.LANCZOS)
def plate(t, cx=0.5, cy=0.5, zoom=1.0, blur=2.5, dim=0.88):
    p = fill(frame(t), cx, cy, zoom).filter(ImageFilter.GaussianBlur(blur))
    return ImageEnhance.Brightness(ImageEnhance.Contrast(p).enhance(1.05)).enhance(dim).convert('RGBA')
def put(base, c, cx, top, h, bri=1.05, con=1.08):
    k = h / c.height; c = c.resize((int(c.width * k), int(h)), Image.LANCZOS)
    rgb = ImageEnhance.Contrast(ImageEnhance.Brightness(c.convert('RGB')).enhance(bri)).enhance(con)
    rgb = rgb.filter(ImageFilter.UnsharpMask(radius=2, percent=70, threshold=2))
    c2 = rgb.convert('RGBA'); c2.putalpha(c.getchannel('A'))
    # a soft dark halo behind the subject separates it from the bright yellow (the big channels all do this)
    halo = Image.new('RGBA', base.size, (0, 0, 0, 0)); a = Image.new('L', base.size, 0)
    a.paste(c.getchannel('A').filter(ImageFilter.MaxFilter(15)), (int(cx - c2.width / 2), int(top)))
    halo.putalpha(a.filter(ImageFilter.GaussianBlur(28)).point(lambda v: int(v * 0.55))); base.alpha_composite(halo)
    base.alpha_composite(c2, (int(cx - c2.width / 2), int(top))); return base
def text(base, s, sz=170, col=(255, 255, 255), col2=None, x=W / 2 - 50):
    fnt = f(sz)
    while fnt.getlength(s) > 1000: sz -= 4; fnt = f(sz)
    g = Image.new('L', (W, H), 0); d = ImageDraw.Draw(g)
    for y in range(H): d.line([(0, y), (W, y)], fill=int(max(0, min(170, (y - H * 0.62) / (H * 0.38) * 180))))
    base.alpha_composite(Image.merge('RGBA', [Image.new('L', (W, H), 0)] * 3 + [g]))
    y = H - 56; sh = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).text((x + 8, y + 12), s, font=fnt, fill=(0, 0, 0, 240), anchor='ms', stroke_width=24, stroke_fill=(0, 0, 0, 240))
    base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
    ImageDraw.Draw(base).text((x, y), s, font=fnt, fill=col + (255,), anchor='ms', stroke_width=14, stroke_fill=(0, 0, 0, 255))
    if col2:   # first word in a second colour
        w0 = s.split()[0]; x0 = x - fnt.getlength(s) / 2
        ImageDraw.Draw(base).text((x0, y), w0, font=fnt, fill=col2 + (255,), anchor='ls', stroke_width=14, stroke_fill=(0, 0, 0, 255))
    return base
RED, YEL = (255, 40, 40), (255, 214, 40)
# J: Mary's terrified face, huge, on the right; the endless yellow rooms behind; TRAPPED
mary = Image.open(os.path.join(SD, 'haGqDEzUK9inbfy7sCxmZ0MJMZc.jpg')).convert('RGB')
jm = cut('j_mary', mary); jh = 820; jw = jm.width * jh / jm.height
j = plate(1749.3, 0.4, 0.55, 1.0); j = put(j, jm, W - jw / 2, -40, jh)   # flush right: the still's own edge becomes the frame edge
j = text(j, 'TRAPPED', 190, RED, x=W / 2 - 160); j.convert('RGB').save(os.path.join(OD, 'backrooms_thumb_j.jpg'), quality=95)
# K: Captain Clark big and centred, looming over the camera in the yellow rooms; 2% SURVIVE
cap = Image.open(os.path.join(WD, '..', 'thumbs_ghi', 'capseq', 'f12.png')).convert('RGB')
k = plate(1744.75, 0.5, 0.5, 1.05); k = put(k, cut('k_cap', cap), 620, 20, 820, bri=1.08)
k = text(k, '2% SURVIVE', 175, (255, 255, 255), RED); k.convert('RGB').save(os.path.join(OD, 'backrooms_thumb_k.jpg'), quality=95)
# L: Clark's face close, looking up, scared, on the left; the lit yellow hall behind; DON'T GO IN
clark = frame(1566.5)
l = plate(1790.0, 0.75, 0.5, 1.1); l = put(l, cut('l_clark', clark), 440, 30, 760)
l = text(l, "DON'T GO IN", 170, (255, 255, 255), RED); l.convert('RGB').save(os.path.join(OD, 'backrooms_thumb_l.jpg'), quality=95)
print('ok')
