# EP08 Conjuring thumbnails: the owner-approved 3-panel % format (Backrooms A, 11/9 "A는 너무 훌륭해"), same code as
# ../ep_backrooms/thumbs_3panel.py. Official TMDB backdrops only (never committed; they live in the scratchpad SD folder).
# Colour by position: left green (highest survival), middle yellow, right red (lowest; Valak's lowest in the video is 5%).
# panel spec: (file, face centre x, face centre y, crop height as a fraction of the source height, brightness, label)
#   the face centre is placed at 40% of the panel height; the dark gradient covers the lower half under the number.
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'ep01'))
from gfx import f
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
SD = os.environ.get('SD', '/tmp/claude-0/-home-user-YTP1/bb3b993e-7de0-5d78-af5e-c29db5ac82a5/scratchpad/ep08_conj/tmdb/orig/')
OUT = os.environ.get('OUT', '/mnt/project-files/instruction444/ep08_conjuring/')
W, H = 1280, 720; PW = [427, 426, 427]; COL = [(70, 215, 95), (250, 200, 40), (235, 30, 38)]
def panel(fn, cx, cy, chf, pw, b=1.05):
    im = Image.open(SD + fn).convert('RGB'); sw, sh = im.size; ch = chf * sh; cw = ch * pw / H
    x0 = min(max(0, cx * sw - cw / 2), sw - cw); y0 = min(max(0, cy * sh - ch * 0.4), sh - ch)
    p = im.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((pw, H), Image.LANCZOS)
    p = ImageEnhance.Brightness(p).enhance(b); p = ImageEnhance.Contrast(p).enhance(1.12)
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
    im.save(OUT + out, quality=93); return OUT + out
ACH = 'ach_52SGN8vYEUbVKBPrvCgzEfT2daN.jpg'      # Annabelle Comes Home: the doll in the glass case (Daniela outside the crop)
JANET = 'c2_4qcGLQbUtIQCZXmppZodlfHvhJ6.jpg'     # The Conjuring 2: possessed Janet, white eyes
VALAK = 'n1_s9tI8lGQpmWRNsh7aSrPfMQjGQv.jpg'     # The Nun: Valak key art face
A14 = 'a14_2gKX53lskaCYk9ycXmaDJKqWiy.jpg'       # Annabelle (2014): close-up with blood tears
LR_SPIRIT = 'lr_xt9Eyld0tgafiq6Jz1o10nqeKpP.jpg'  # Last Rites: the grinning old woman, one of the spirits the mirror demon controls
VALAK_FULL = 'n1_oSl0mMggtRfnNzJKRmFZc1sNqvI.jpg'  # The Nun: Valak standing
CREATION = 'cr_cooMlxcgNDWpXzXERFepJrMXQhq.jpg'  # Annabelle: Creation: the doll in the closet
ISLA = 'dm_ifZ0fkOlLIdvNeKWG5LUxyMQzOK.jpg'       # The Devil Made Me Do It: Isla, the Occultist
VALAK_N2 = 'n2_vO2925ghThGfYSzaBJBfxmUqd1M.jpg'  # The Nun II: Valak behind the lattice, glowing eyes
if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    a = build([(ACH, 0.372, 0.488, 0.52, 1.12, '95%'), (JANET, 0.255, 0.524, 0.76, 1.10, '55%'), (VALAK, 0.50, 0.431, 0.627, 1.15, '5%')], 'conjuring_thumb_a.jpg')
    b = build([(A14, 0.50, 0.40, 1.0, 1.10, '80%'), (LR_SPIRIT, 0.50, 0.524, 0.76, 1.50, '45%'), (VALAK_FULL, 0.70, 0.254, 0.36, 1.20, '5%')], 'conjuring_thumb_b.jpg')
    c = build([(CREATION, 0.69, 0.415, 0.40, 1.10, '40%'), (ISLA, 0.60, 0.412, 0.78, 1.50, '30%'), (VALAK_N2, 0.655, 0.533, 0.46, 1.45, '5%')], 'conjuring_thumb_c.jpg')
    s = Image.new('RGB', (1940, 1310), (24, 24, 24))
    for i, p in enumerate([a, b, c]): s.paste(Image.open(p).resize((640, 360)), (i * 650, 0))
    for i, p in enumerate([a, b]): s.paste(Image.open(p).resize((960, 540)), (i * 970, 380))
    s.paste(Image.open(c).resize((640, 360)), (650, 940))
    s.save(OUT + 'conjuring_thumbs_sheet.jpg', quality=88); print('ok')
