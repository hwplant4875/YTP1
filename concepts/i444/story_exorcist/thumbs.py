# START / END two-panel thumbnails (benchmark format: Right Turn "The ENTIRE Story of X") for "The ENTIRE Story of The Exorcist".
# Official images only, from TMDB (SOURCES below = the TMDB file of each name; download https://image.tmdb.org/t/p/original/<file>
# into $ORIG as <name>.jpg). Never commit the source images. Font: Luckiest Guy (Apache 2.0), slanted 0.18 like the benchmark.
# START = the demon's first host (Regan, 1973), END = its latest (the possessed girls of Believer, 2023).
# usage: ORIG=<folder with the sources> FONT=<ttf> python3 -I thumbs.py [variant ...]   -> upload/exorcist_story_thumb_<v>.jpg
# The finished jpgs stay out of git (they are built from studio images); deliver them through the project files.
import sys, os
SOURCES = {
    '9552_posters_39': 'niWzeJeTPXJlHKouGhnoCvhJ3MS.jpg',
    '9552_backdrops_31': 'xBqrGCpub5ULz0BCbInzcNbRE1F.jpg',
    '807172_backdrops_13': 'fmrDLIgB5SdcJ3gCZC5oCx61bXP.jpg',
    '807172_backdrops_6': 'xZkYUCGtIf2RHIY34H4Rpfw6IZC.jpg',
}  # 9552 = The Exorcist (1973, poster 39 = Extended Director's Cut Blu-ray art), 807172 = The Exorcist: Believer (2023)
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
HERE = os.path.dirname(os.path.abspath(__file__))
# font: https://raw.githubusercontent.com/google/fonts/main/apache/luckiestguy/LuckiestGuy-Regular.ttf (not committed)
FONT = os.environ.get('FONT', os.path.join(HERE, 'LuckiestGuy-Regular.ttf'))
ORIG = os.environ.get('ORIG', os.path.join(HERE, 'orig'))
W, H, PW = 1280, 720, 640
YELLOW = (255, 226, 18)
# panel = (image, face centre x, face centre y, face height in px (all in original pixels), brightness, contrast)
V = {
    'A': [('9552_posters_39', 900, 1530, 1060, 1.08, 1.08), ('807172_backdrops_13', 1040, 460, 680, 1.10, 1.06)],
    'B': [('9552_backdrops_31', 790, 500, 360, 1.06, 1.06, 430), ('807172_backdrops_6', 1270, 530, 620, 1.12, 1.06)],
}
FACE_H, FACE_Y = 470, 275


def panel(name, cx, cy, fh, br, ct, target=FACE_H):
    im = Image.open(os.path.join(ORIG, name + '.jpg')).convert('RGB')
    s = target / fh
    w, h = PW / s, H / s
    left = min(max(cx - (PW / 2) / s, 0), im.width - w)
    top = min(max(cy - FACE_Y / s, 0), im.height - h)
    p = im.crop((round(left), round(top), round(left + w), round(top + h))).resize((PW, H), Image.LANCZOS)
    p = ImageEnhance.Contrast(ImageEnhance.Brightness(p).enhance(br)).enhance(ct)
    # dark gradient under the word so it pops
    g = Image.new('L', (PW, H), 0)
    gd = ImageDraw.Draw(g)
    for y in range(430, H):
        gd.line((0, y, PW, y), fill=int(175 * ((y - 430) / (H - 430)) ** 1.3))
    p.paste(Image.new('RGB', (PW, H), 'black'), (0, 0), g)
    return p


def word(canvas, text, cx, cy, fill, size):
    f = ImageFont.truetype(FONT, size)
    pad = 60
    bw, bh = int(f.getlength(text)) + 2 * pad, size + 2 * pad
    layer = Image.new('RGBA', (bw, bh), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.text((pad, pad), text, font=f, fill=fill, stroke_width=11, stroke_fill='black')
    # slant like the comic font in the benchmark
    sh = 0.18
    layer = layer.transform((bw + int(sh * bh), bh), Image.AFFINE, (1, sh, -sh * bh, 0, 1, 0), Image.BICUBIC)
    shadow = Image.new('RGBA', layer.size, (0, 0, 0, 0))
    shadow.putalpha(layer.split()[3].point(lambda a: int(a * 0.75)))
    shadow = shadow.filter(ImageFilter.GaussianBlur(4))
    box = layer.getbbox()
    x = int(cx - (box[0] + box[2]) / 2)
    y = int(cy - (box[1] + box[3]) / 2)
    canvas.alpha_composite(shadow, (x + 7, y + 8))
    canvas.alpha_composite(layer, (x, y))


def tear(canvas):
    # jagged white torn-paper divider down the middle
    import random
    rnd = random.Random(7)
    pts_l, pts_r, y = [], [], 0
    while y <= H + 20:
        j = rnd.uniform(-7, 7)
        pts_l.append((PW - 5 + j, y)); pts_r.append((PW + 5 + j + rnd.uniform(-2, 2), y))
        y += rnd.uniform(14, 26)
    d = ImageDraw.Draw(canvas)
    d.polygon([(x + 4, y) for x, y in pts_l] + [(x + 4, y) for x, y in reversed(pts_r)], fill=(0, 0, 0, 120))
    d.polygon(pts_l + list(reversed(pts_r)), fill=(255, 255, 255, 255))


def build(v):
    c = Image.new('RGBA', (W, H), 'black')
    for i, spec in enumerate(V[v]):
        c.paste(panel(*spec), (i * PW, 0))
    tear(c)
    word(c, 'START', PW // 2, 628, (255, 255, 255), 150)
    word(c, 'END', PW + PW // 2, 628, YELLOW, 150)
    out = os.path.join(HERE, 'upload', f'exorcist_story_thumb_{v.lower()}.jpg')
    c.convert('RGB').save(out, quality=92)
    print(out)


for v in (sys.argv[1:] or V):
    build(v)
