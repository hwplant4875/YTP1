# EP07 Pinhead thumbnails D/E/F (owner 11/05 23:43 KST: "썸네일 3개 더 만들어볼래? 기존꺼는 냅두고. 새로."), horror-ranked-thumbnail skill.
# Same layout and rules as thumbs.py (A/B/C): 1280x720, three panels 427/426/427 with black gutters, left GREEN / middle YELLOW /
# right RED %, YouTube Sans Black 182 with stroke and shadow, a dark gradient under the numbers, every face centred with the same
# face size and one shared eye line. New for D/E/F: a different film trio in each thumbnail (no two films that already share an
# A/B/C thumbnail) and no source image that A/B/C use. Sources are official TMDB stills (backdrops) saved outside the repo.
# usage: python3 thumbs_def.py <tmdb_dir> [out_dir] [--marks]   (--marks: eye line / centre / mouth guides for checking)
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
FACE, EYE = 135, 215                                     # eye-to-mouth distance in output px, eye line y (same as A/B/C)
def grade(im, bright=1.0, contrast=1.18, sat=0.95):
    im = ImageEnhance.Brightness(im).enhance(bright); im = ImageEnhance.Contrast(im).enhance(contrast)
    return ImageEnhance.Color(im).enhance(sat)
def panel(sp, pw):
    """(cx, cy) = nose x / eye line in source px, em = eye-to-mouth distance in source px -> FACE px, eyes at EYE"""
    im = grade(Image.open(os.path.join(SRC, sp['file'])).convert('RGB'), sp.get('bright', 1.0), sp.get('contrast', 1.18), sp.get('sat', 0.95))
    if sp.get('sharp'): im = im.filter(ImageFilter.UnsharpMask(2, sp['sharp'], 2))   # a still that gets enlarged a little
    s = FACE / sp['em']
    big = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    cx, cy = sp['cx'] * s, sp['cy'] * s; ox, oy = round(pw / 2 - cx), round(EYE - cy)
    # background where a close-up still does not reach the panel edge: the still's own edge pixels carried outwards and blurred,
    # so a black backdrop just continues as black under the % (no zoomed, lighter copy of the face showing as a band)
    pl, pt = max(0, ox), max(0, oy); pr, pb = max(0, pw - ox - big.width), max(0, H - oy - big.height)
    ext = Image.fromarray(np.pad(np.asarray(big), ((pt, pb), (pl, pr), (0, 0)), mode='edge')).filter(ImageFilter.GaussianBlur(25))
    p = ImageEnhance.Brightness(ext).enhance(0.85).crop((pl - ox, pt - oy, pl - ox + pw, pt - oy + H)).convert('RGBA')
    m = Image.new('L', big.size, 0); ImageDraw.Draw(m).rectangle([30, 30, big.width - 30, big.height - 30], fill=255); m = m.filter(ImageFilter.GaussianBlur(18))
    short = dict(left=int(ox), top=int(oy), right=int(pw - (ox + big.width)), bottom=int(H - 100 - (oy + big.height)))
    if any(v > 0 for v in short.values()): print('  WARN source does not fill the panel', sp['file'][:30], {k_: v for k_, v in short.items() if v > 0})
    p.paste(big, (ox, oy), m)
    v = np.linspace(0, 1, H)[:, None]; a = (np.clip((v - 0.5) / 0.32, 0, 1) ** 1.2 * 235).astype(np.uint8)   # dark bottom under the %
    p.alpha_composite(Image.merge('RGBA', [Image.new('L', (pw, H), 0)] * 3 + [Image.fromarray(np.repeat(a, pw, 1), 'L')]))
    if MARKS:
        d = ImageDraw.Draw(p); d.line([(0, EYE), (pw, EYE)], fill=(0, 255, 255, 255)); d.line([(0, EYE + FACE), (pw, EYE + FACE)], fill=(255, 0, 255, 255))
        d.line([(pw / 2, 0), (pw / 2, H)], fill=(0, 255, 255, 255))
    return p
def three(specs, name, num_y=205):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 255)); x = 0
    for sp, pw in zip(specs, PW): im.alpha_composite(panel(sp, pw), (x, 0)); x += pw
    d = ImageDraw.Draw(im); x = 0
    for k_ in (1, 2): gx = sum(PW[:k_]); d.rectangle([gx - 3, 0, gx + 3, H], fill=(0, 0, 0, 255))
    for sp, pw in zip(specs, PW): shadow_text(im, (x + pw // 2, H - num_y), sp['pct'], f(182), sp['col'], stroke=8); x += pw
    im.convert('RGB').save(os.path.join(OUT, name), quality=92); print(name)
def F(file, cx, cy, em, pct, col, bright=1.1, **kw): return dict(file=file, cx=cx, cy=cy, em=em, pct=pct, col=col, bright=bright, **kw)
os.makedirs(OUT, exist_ok=True)
# A = Revelations / Hellseeker / Judgment, B = 1987 / Priest / Inferno, C = Hellbound / Bloodline / Hell on Earth.
# D/E/F pair the films differently, so no two films sit together twice across A-F.
D = [F('hellbound_b8_6baZrjbHXH5OUeKAlg0jplH6ZmB.jpg', 1275, 308, 172, '85%', GREEN, 1.05),    # Hellbound #11, official still (Pinhead beside the Female Cenobite)
     F('hellseeker_b8_dC19cAd8xx0G7EydsT7XaA8nVNJ.jpg', 1185, 690, 315, '45%', YEL, 1.0),      # Hellseeker #8, official still (black backdrop)
     F('hellworld_b15_JK1C1lZbzuhXrtvm4VFXJ1SexU.jpg', 1240, 577, 300, '20%', RED, 1.1)]       # Hellworld #5, official still (behind chains)
E = [F('revelations_b1_qv5zpQSx8naAm8C59DGVLMdZxbp.jpg', 2020, 892, 364, '70%', GREEN, 1.1),  # Revelations #10, 4K still
     F('priest2022_b19_kS6Cl5nX5kLmFYcAifxzUh6ySCE.jpg', 1540, 670, 285, '35%', YEL, 1.6),    # the Priest, 2022 #7, looking down at you (B uses a front-on Priest)
     F('hellonearth_b25_rzGCtmicZ3fxmNwljo6192iuds.jpg', 1125, 440, 170, '5%', RED, 1.05, sat=0.3)]  # Hell on Earth #1, screaming (very yellow, so desaturated)
FF = [F('h1987_b36_jGEpNZZTNFG5YJIZlALMjazERNH.jpg', 695, 372, 190, '55%', GREEN, 1.05),     # Hellraiser 1987 #9, light beams
      F('bloodline_b12_aXl2YmJuMESCMWYcZcojTfnMy5q.jpg', 800, 408, 192, '25%', YEL, 1.1),     # Bloodline #6
      F('judgment_b12_8pDFS4hhbn7Fje8QqgIJSu84eZo.jpg', 1870, 750, 330, '10%', RED, 1.1)]     # Judgment #3, 4K still
for specs, name in ((D, 'pinhead_thumb_d.jpg'), (E, 'pinhead_thumb_e.jpg'), (FF, 'pinhead_thumb_f.jpg')): three(specs, name)
# G/H (owner 11/06 00:10 KST after seeing C: "저런 썸네일이 필요해. 다시 2개만 더 퀄리티 좋게", "오른쪽은 무조건 5%", retouching allowed):
# C-style punch, i.e. vivid colour per panel, bright high-contrast faces, and Hell on Earth 5% always on the right. Numbers sit 45 px
# lower, like the C2 variant he asked for at the same time. G and H share no photo; H keeps C's skyline 5% panel (no other
# official Hell on Earth still is sharp enough at this face size, and b25 is in G).
G = [F('h1987_b10_bxmIpsvBsCDWFXY3Cmr37FYDlA7.jpg', 1010, 372, 245, '55%', GREEN, 1.05, contrast=1.25, sat=1.25),   # 1987 #9, blue fog and chains
     F('hellseeker_b1_2pGRnOQ6gcDm1MW8qjbVjwJFupF.jpg', 1790, 1118, 340, '45%', YEL, 1.25, contrast=1.2, sat=1.1),   # Hellseeker #8, red key art
     F('hellonearth_b25_rzGCtmicZ3fxmNwljo6192iuds.jpg', 1105, 425, 155, '5%', RED, 1.0, contrast=1.2, sat=1.1)]    # Hell on Earth #1, screaming
HH = [F('revelations_b18_7oeGa7JEE6NfHsbPrpWk5OInQo5.jpg', 980, 412, 200, '70%', GREEN, 1.25, contrast=1.3, sat=1.25),  # Revelations #10, blue chains
      F('priest2022_b11_qoDbQW14RYP8Agzl1IpVCWIEGTn.jpg', 1493, 730, 325, '35%', YEL, 1.2, contrast=1.25, sat=1.4),  # the Priest, 2022 #7
       F('o_xjeoa7KjnUMQzJXGunHmgMjhHmP.jpg', 2556, 802, 405, '5%', RED, 1.05, contrast=1.22, sat=1.15)]   # Hell on Earth #1, C's skyline art (the owner's favourite 5% panel)
for specs, name in ((G, 'pinhead_thumb_g.jpg'), (HH, 'pinhead_thumb_h.jpg')): three(specs, name, num_y=160)
