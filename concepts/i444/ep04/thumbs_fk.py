# EP04 Freddy Krueger thumbnails A/B/C (horror-ranked-thumbnail skill, the EP07 "C" look the owner asked for on 11/06:
# "저런 썸네일이 필요해", "오른쪽은 무조건 5%", numbers low like C3). 1280x720, three panels 427/426/427 with black gutters,
# left GREEN / middle YELLOW / right RED %, YouTube Sans Black 182 with stroke and shadow, a dark gradient under the numbers.
# Every face is centred, with the same face size and one shared eye line inside a thumbnail. The right panel is always
# The Dream Master (5%, the lowest rate in the video), with a different Dream Master photo in each thumbnail. Each panel's
# face comes from the film whose % it shows. Sources are official TMDB stills, posters and promo photos, saved outside the
# repo (never committed); only the face region is used.
# usage: python3 thumbs_fk.py <tmdb_dir> [out_dir] [--marks]   (--marks: eye line / mouth line / centre guides)
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'ep01'))
from gfx import f, shadow_text
SRC = sys.argv[1]; OUT = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else os.path.join(HERE, 'upload')
MARKS = '--marks' in sys.argv
W, H = 1280, 720; PW = [427, 426, 427]
GREEN = (70, 215, 95, 255); YEL = (250, 200, 40, 255); RED = (235, 30, 38, 255)
NUM_Y = 115                                               # number centre above the bottom (EP07 C3, the owner's pick)
def grade(im, bright=1.0, contrast=1.2, sat=1.15):
    im = ImageEnhance.Brightness(im).enhance(bright); im = ImageEnhance.Contrast(im).enhance(contrast)
    return ImageEnhance.Color(im).enhance(sat)
def panel(sp, pw, FACE, EYE):
    """(cx, cy) = face centre x / eye line in source px, em = eye-to-mouth distance in source px -> FACE px, eyes at EYE"""
    im = grade(Image.open(os.path.join(SRC, sp['file'])).convert('RGB'), sp['bright'], sp['contrast'], sp['sat'])
    x0, y0 = 0, 0
    if sp.get('crop'):                                   # keep a poster's title lettering out of the panel (the photo part only)
        im = im.crop(sp['crop']); x0, y0 = sp['crop'][:2]
    if sp.get('sharp'): im = im.filter(ImageFilter.UnsharpMask(2, sp['sharp'], 2))
    s = FACE / sp['em']
    big = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    cx, cy = (sp['cx'] - x0) * s, (sp['cy'] - y0) * s; ox, oy = round(pw / 2 - cx), round(EYE - cy)
    # where the photo does not reach the panel edge, its own edge pixels carry on outwards, blurred (no lighter zoomed copy)
    pl, pt = max(0, ox), max(0, oy); pr, pb = max(0, pw - ox - big.width), max(0, H - oy - big.height)
    ext = Image.fromarray(np.pad(np.asarray(big), ((pt, pb), (pl, pr), (0, 0)), mode='edge')).filter(ImageFilter.GaussianBlur(25))
    p = ImageEnhance.Brightness(ext).enhance(0.85).crop((pl - ox, pt - oy, pl - ox + pw, pt - oy + H)).convert('RGBA')
    m = Image.new('L', big.size, 0); ImageDraw.Draw(m).rectangle([30, 30, big.width - 30, big.height - 30], fill=255); m = m.filter(ImageFilter.GaussianBlur(18))
    short = dict(left=int(ox), top=int(oy), right=int(pw - (ox + big.width)), bottom=int(H - 100 - (oy + big.height)))
    if any(v > 0 for v in short.values()): print('  WARN source does not fill the panel', sp['file'][:30], {k_: v for k_, v in short.items() if v > 0})
    if s > 1.05: print(f'  NOTE {sp["file"][:30]} enlarged {s:.2f}x')
    p.paste(big, (ox, oy), m)
    v = np.linspace(0, 1, H)[:, None]; a = (np.clip((v - 0.5) / 0.32, 0, 1) ** 1.2 * 235).astype(np.uint8)   # dark bottom under the %
    p.alpha_composite(Image.merge('RGBA', [Image.new('L', (pw, H), 0)] * 3 + [Image.fromarray(np.repeat(a, pw, 1), 'L')]))
    if MARKS:
        d = ImageDraw.Draw(p); d.line([(0, EYE), (pw, EYE)], fill=(0, 255, 255, 255)); d.line([(0, EYE + FACE), (pw, EYE + FACE)], fill=(255, 0, 255, 255))
        d.line([(pw / 2, 0), (pw / 2, H)], fill=(0, 255, 255, 255))
    return p
def three(specs, name, FACE, EYE):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 255)); x = 0
    for sp, pw in zip(specs, PW): im.alpha_composite(panel(sp, pw, FACE, EYE), (x, 0)); x += pw
    d = ImageDraw.Draw(im); x = 0
    for k_ in (1, 2): gx = sum(PW[:k_]); d.rectangle([gx - 3, 0, gx + 3, H], fill=(0, 0, 0, 255))
    for sp, pw in zip(specs, PW): shadow_text(im, (x + pw // 2, H - NUM_Y), sp['pct'], f(182), sp['col'], stroke=8); x += pw
    im.convert('RGB').save(os.path.join(OUT, name), quality=92); print(name)
def F(file, cx, cy, em, pct, col, bright=1.1, contrast=1.2, sat=1.15, **kw):
    return dict(file=file, cx=cx, cy=cy, em=em, pct=pct, col=col, bright=bright, contrast=contrast, sat=sat, **kw)
os.makedirs(OUT, exist_ok=True)
# TMDB files are saved as <key>_<b|p><index>_<tmdb path>.jpg (b = backdrop/still, p = poster/key art); the key is the film:
# fj Freddy vs. Jason 95%, n2 Freddy's Revenge 65%, n5 The Dream Child 55%, n6 Freddy's Dead 45%, n7 New Nightmare 30%,
# n1 the 1984 original 22%, n4 The Dream Master 5%. No photo is used twice across A/B/C.
A = [F('fj_b3_8K2w1hG34VAuaFYKDS0SU1Lb0Br.jpg', 1470, 840, 345, '95%', GREEN, 1.05),            # Freddy vs. Jason, 4K still, glove up
     F('n1_p11_6soYjMYxvCezyr5sf57sVERdgIP.jpg', 1030, 815, 245, '22%', YEL, 0.95, 1.05, 1.0, crop=(0, 0, 2000, 1425)),  # 1984 original, promo photo on red smoke (title below 1430 left out)
     F('n4_b25_lvjTM5UntOCPUnoFN5dsaeGCYDW.jpg', 1860, 472, 418, '5%', RED, 1.15)]             # The Dream Master, bulging eyes (lab)
B = [F('n2_p43_hy2sjWo1x5MwnuCBj3560GjCmxJ.jpg', 880, 606, 224, '65%', GREEN, 1.0, 1.1, 1.05),  # Freddy's Revenge, promo photo (black hat, glow)
     F('n6_b12_aOnlEAMZN9ABPAWOQggaOVdw5xt.jpg', 730, 355, 215, '45%', YEL, 1.0, 1.2, 1.1),     # Freddy's Dead, laughing
     F('n4_b36_i3pL435lhF1A7PGJvyPUpAesRfb.jpg', 1110, 555, 245, '5%', RED, 1.1, 1.2, 1.1)]     # The Dream Master, glove raised
C = [F('n5_p6_5moXMrlntjZNxPlIh49H71dOTYk.jpg', 860, 687, 393, '55%', GREEN, 1.1, 1.15, 1.1),   # The Dream Child, key art (red)
     F('n7_b24_pnTYzs0z7GJGD2E888n6lFe8PWh.jpg', 1165, 475, 160, '30%', YEL, 1.2, 1.25, 1.2),   # New Nightmare, hospital
     F('n4_p30_iIGbJauwmps49XPZpXbvqbFWJ0l.jpg', 382, 311, 194, '5%', RED, 1.1, 1.15, 1.1, crop=(0, 0, 662, 1525))]  # The Dream Master, Crave Inn diner (title from x 667 left out)
# face size / eye line per thumbnail: A's Dream Master photo is cut at the top of the hat, so A sits a little higher and closer
for specs, name, face, eye in ((A, 'freddy_thumb_a.jpg', 150, 215), (B, 'freddy_thumb_b.jpg', 140, 235), (C, 'freddy_thumb_c.jpg', 140, 235)):
    three(specs, name, face, eye)
