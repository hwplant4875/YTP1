# You, Elsewhere channel profile picture (dark academia / study music), 800x800, readable in YouTube's circle crop.
# Variants: a) "You, / Elsewhere" two-line script on deep ink-green   b) "Ye" monogram + small serif name, ink-green
#           c) two-line script in ink on warm parchment
# Also writes a QA sheet with the circle crop at 160, 98 and 40 px.
# usage: python make_profile.py <out_dir>
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
FONTS = r'C:\Users\hw549\AppData\Local\Microsoft\Windows\Fonts'
ALLURA, VIBES = os.path.join(FONTS, 'Allura-Regular.ttf'), os.path.join(FONTS, 'GreatVibes-Regular.ttf')
CORM = r'C:\Users\hw549\Downloads\YTP1\_fonts_dl\cormorant\CormorantGaramond.ttf'
S = 2400                                         # draw at 3x, downsample to 800
GOLD, CREAM, INK = (226, 196, 140), (246, 238, 224), (34, 30, 26)

def background(c_in, c_out, grain=5, seed=1):
    yy, xx = np.mgrid[0:S, 0:S] / S - 0.5
    r = np.sqrt(xx ** 2 + yy ** 2) / 0.71
    a = np.array(c_in, np.float32); b = np.array(c_out, np.float32)
    img = a + (b - a) * (r[..., None] ** 1.4)
    img += np.random.default_rng(seed).normal(0, grain, (S, S, 1))          # paper / film grain
    return Image.fromarray(img.clip(0, 255).astype(np.uint8))

def text_mask(lines):
    """lines: (text, font path, size, y centre, tracking, variation) -> L mask, horizontally centred."""
    m = Image.new('L', (S, S), 0); d = ImageDraw.Draw(m)
    for text, path, size, cy, track, var in lines:
        f = ImageFont.truetype(path, size)
        if var: f.set_variation_by_name(var)
        ws = [d.textlength(ch, font=f) for ch in text]; x = (S - sum(ws) - track * (len(text) - 1)) / 2
        bb = d.textbbox((0, 0), text, font=f); y = cy - (bb[1] + bb[3]) / 2
        for ch, w in zip(text, ws): d.text((x, y), ch, font=f, fill=255); x += w + track
    return m

def ring(r_frac, width, alpha=255):
    m = Image.new('L', (S, S), 0); d = ImageDraw.Draw(m); r = S * r_frac
    d.ellipse([S / 2 - r, S / 2 - r, S / 2 + r, S / 2 + r], outline=alpha, width=width)
    return m

def comp(bg, mask, colour, glow=None, shadow=True):
    if shadow:
        bg = Image.composite(Image.new('RGB', bg.size, (0, 0, 0)), bg, mask.filter(ImageFilter.GaussianBlur(18)).point(lambda v: int(v * 0.55)))
    if glow:
        bg = Image.composite(Image.new('RGB', bg.size, glow), bg, mask.filter(ImageFilter.GaussianBlur(40)).point(lambda v: int(v * 0.3)))
    return Image.composite(Image.new('RGB', bg.size, colour), bg, mask)

def variant_a():
    bg = background((30, 52, 42), (8, 16, 13))
    bg = comp(bg, ring(0.445, 6, 150), GOLD, shadow=False)
    bg = comp(bg, ring(0.425, 3, 110), GOLD, shadow=False)
    return comp(bg, text_mask([('You,', ALLURA, 700, S * 0.39, 0, None), ('Elsewhere', ALLURA, 500, S * 0.61, 0, None)]), CREAM, (255, 214, 150))

def variant_b():
    bg = background((30, 52, 42), (8, 16, 13), seed=2)
    bg = comp(bg, ring(0.445, 6, 150), GOLD, shadow=False)
    bg = comp(bg, text_mask([('Ye', VIBES, 1150, S * 0.43, 0, None)]), CREAM, (255, 214, 150))
    return comp(bg, text_mask([('YOU, ELSEWHERE', CORM, 130, S * 0.80, 36, 'SemiBold')]), GOLD)

def variant_c():
    bg = background((240, 228, 204), (196, 172, 134), grain=6, seed=3)
    bg = comp(bg, ring(0.445, 6, 170), (120, 92, 52), shadow=False)
    return comp(bg, text_mask([('You,', ALLURA, 700, S * 0.39, 0, None), ('Elsewhere', ALLURA, 500, S * 0.61, 0, None)]), INK, shadow=False)

sheet = Image.new('RGB', (3 * 520, 520), (24, 24, 24)); sd = ImageDraw.Draw(sheet)
for k, (name, fn) in enumerate([('a', variant_a), ('b', variant_b), ('c', variant_c)]):
    im = fn().resize((800, 800), Image.LANCZOS)
    im.save(os.path.join(OUT, f'profile_{name}_800.png'))
    circ = Image.new('L', (800, 800), 0); ImageDraw.Draw(circ).ellipse([0, 0, 799, 799], fill=255)
    x0 = k * 520 + 20
    for size, (x, y) in ((300, (x0, 20)), (98, (x0 + 320, 40)), (40, (x0 + 320, 160))):
        sheet.paste(im.resize((size, size), Image.LANCZOS), (x, y), circ.resize((size, size), Image.LANCZOS))
    sd.text((x0, 340), f'variant {name}: 300 / 98 / 40 px circle', fill=(200, 200, 200))
sheet.save(os.path.join(OUT, 'profile_qa_sheet.png'))
print('done', OUT)

# ------------------------------------------------------------------ v2 (owner 10/26): monogram look, "You" centred high,
# "Elsewhere" bent underneath like a boat / a smile, its ends curling up around "You"
import cv2

def smile(mask, radius, mid_y):
    """Polar-warp a straight text mask onto the bottom of a circle (a smile): the text's centre stays at mid_y,
    letters rotate to follow the arc with their tops toward the centre, so the script joins stay intact."""
    a = np.asarray(mask); ys, xs = np.nonzero(a > 0)
    tx = (xs.min() + xs.max()) / 2; base = mid_y                     # ink-centred horizontally
    cx, cy = S / 2, mid_y - radius                                  # circle centre above the text
    gx, gy = np.meshgrid(np.arange(S, dtype=np.float32), np.arange(S, dtype=np.float32))
    r = np.hypot(gx - cx, gy - cy); th = np.arctan2(cx - gx, gy - cy)  # 0 straight down, + to the left
    src_x = (tx - th * radius).astype(np.float32); src_y = (base + (r - radius)).astype(np.float32)
    shift_y = (ys.min() + ys.max()) / 2 - base                       # keep the ink centre on the arc
    out = cv2.remap(a, src_x, src_y + np.float32(shift_y), cv2.INTER_CUBIC)
    return Image.fromarray(out)

def variant_smile(name, you_font, you_size, you_y, else_size, else_y, radius, else_col):
    bg = background((30, 52, 42), (8, 16, 13), seed=4)
    bg = comp(bg, ring(0.445, 6, 150), GOLD, shadow=False)
    bg = comp(bg, text_mask([('You', you_font, you_size, you_y, 0, None)]), CREAM, (255, 214, 150))
    m = smile(text_mask([('Elsewhere', ALLURA, else_size, S / 2, 0, None)]), radius, else_y)
    return comp(bg, m, else_col, (255, 214, 150))

SMILES = {
    's1': lambda: variant_smile('s1', VIBES, 820, S * 0.39, 400, S * 0.745, S * 0.34, CREAM),
    's2': lambda: variant_smile('s2', VIBES, 820, S * 0.39, 400, S * 0.745, S * 0.34, GOLD),
    's3': lambda: variant_smile('s3', VIBES, 860, S * 0.40, 380, S * 0.75, S * 0.27, GOLD),
}
sheet = Image.new('RGB', (3 * 520, 360), (24, 24, 24)); sd = ImageDraw.Draw(sheet)
for k, (name, fn) in enumerate(SMILES.items()):
    im = fn().resize((800, 800), Image.LANCZOS); im.save(os.path.join(OUT, f'profile_{name}_800.png'))
    circ = Image.new('L', (800, 800), 0); ImageDraw.Draw(circ).ellipse([0, 0, 799, 799], fill=255)
    x0 = k * 520 + 20
    for size, (x, y) in ((300, (x0, 20)), (98, (x0 + 320, 40)), (40, (x0 + 320, 160))):
        sheet.paste(im.resize((size, size), Image.LANCZOS), (x, y), circ.resize((size, size), Image.LANCZOS))
    sd.text((x0, 335), f'{name}: 300 / 98 / 40 px circle', fill=(200, 200, 200))
sheet.save(os.path.join(OUT, 'profile_smile_qa_sheet.png'))
