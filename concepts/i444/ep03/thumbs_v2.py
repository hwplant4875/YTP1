# EP03 thumbnails v2 ("Every Ghostface Ranked by Your Chance of Surviving Them")
#   a = mask centred + big "16 KILLERS" at the bottom
#   b = "WHO'S #1?" at the top, the mask cut out (rembg) and laid over the letters
#   c = three faces, eyes level: Carvey 99% / Ethan 53% / Roman 15% (the 99% is a person, not the mask, so it can't read as 'Ghostface is easy')
# Run with the rembg venv (needs rembg + scipy):
#   <scratchpad>/rbenv/bin/python thumbs_v2.py [GFT_SRC_DIR] [OUT_DIR] [CACHE_DIR]
import os, sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'ep01'))
from gfx import f, shadow_text, RED, WHITE
from thumbs_v2_lib import pop

SCR = '/tmp/claude-0/-home-user-YTP1/bb3b993e-7de0-5d78-af5e-c29db5ac82a5/scratchpad'
GFT = sys.argv[1] if len(sys.argv) > 1 else SCR + '/gft/src'          # official Scream VI key art / posters
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, 'upload')
CACHE = sys.argv[3] if len(sys.argv) > 3 else SCR + '/v2work/thumbs3'  # rembg alpha cache (never in the repo)
FACES = os.path.join(HERE, 'faces')
ANTON = SCR + '/hr/fonts/Anton.ttf'
W, H = 1280, 720
GREEN = (70, 215, 95, 255); YEL = (250, 200, 40, 255)
os.makedirs(OUT, exist_ok=True); os.makedirs(CACHE, exist_ok=True)


def anton(sz): return ImageFont.truetype(ANTON, sz)


def save(im, name):
    im.convert('RGB').save(os.path.join(OUT, name), quality=93)
    print('wrote', os.path.join(OUT, name))


def affine(im, src_pt, dst_pt, scale, size, angle=0.0, fill=(0, 0, 0, 255)):
    """Map src_pt -> dst_pt, scaled by `scale`, rotated by `angle` (radians, clockwise) about that point."""
    ca, sa = math.cos(angle) / scale, math.sin(angle) / scale
    a, b, d, e = ca, -sa, sa, ca
    c = src_pt[0] - a * dst_pt[0] - b * dst_pt[1]
    f_ = src_pt[1] - d * dst_pt[0] - e * dst_pt[1]
    return im.transform(size, Image.AFFINE, (a, b, c, d, e, f_), Image.BICUBIC, fillcolor=fill)


def segments_text(im, cx, base, parts, font, stroke, blur=12, alpha=220, shadow=True):
    """Draw [(text, colour), ...] as one centred line on baseline `base`, black stroke + soft drop shadow."""
    d = ImageDraw.Draw(im)
    widths = [d.textlength(t, font=font) for t, _ in parts]
    x = cx - sum(widths) / 2
    if shadow:
        sh = Image.new('RGBA', im.size, (0, 0, 0, 0)); ds = ImageDraw.Draw(sh); xx = x
        for (t, _), w in zip(parts, widths):
            ds.text((xx + 5, base + 8), t, font=font, fill=(0, 0, 0, alpha), anchor='ls', stroke_width=stroke + 8, stroke_fill=(0, 0, 0, alpha)); xx += w
        im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(blur)))
    d = ImageDraw.Draw(im)
    for (t, col), w in zip(parts, widths):
        d.text((x, base), t, font=font, fill=col, anchor='ls', stroke_width=stroke, stroke_fill=(0, 0, 0, 255)); x += w


def darken(im, mask_l):
    im.paste((0, 0, 0, 255), (0, 0), mask_l)


def vgrad(y0, y1, a0, a1, size=(W, H)):
    """Vertical alpha ramp: a0 at y0 -> a1 at y1 (smoothstep), held outside."""
    y = np.arange(size[1], dtype=np.float32)
    t = np.clip((y - y0) / (y1 - y0), 0, 1); t = t * t * (3 - 2 * t)
    col = (a0 + (a1 - a0) * t).astype(np.uint8)
    return Image.fromarray(np.repeat(col[:, None], size[0], 1), 'L')


# ---------------------------------------------------------------- the mask key art
MASK_SRC = os.path.join(GFT, 'mask.jpg')            # 1920x1080, mask centre ~ (975, 480)
mask_rgb = Image.open(MASK_SRC).convert('RGBA')


def figure_alpha():
    """rembg (isnet-general-use) matte of hood + mask + shoulders, eye/mouth holes filled, stray bits removed."""
    p = os.path.join(CACHE, 'mask_rembg_isnet.png')
    if not os.path.exists(p):
        from rembg import remove, new_session
        remove(Image.open(MASK_SRC).convert('RGB'), session=new_session('isnet-general-use'), only_mask=True).save(p)
    a = np.asarray(Image.open(p).convert('L')).astype(np.float32) / 255
    lab, n = ndimage.label(a > 0.5)
    keep = lab == (np.argmax(np.bincount(lab.ravel())[1:]) + 1)       # biggest blob = the figure
    solid = ndimage.binary_fill_holes(keep)
    return np.where(solid & ~keep, 1.0, a * keep)                       # holes (eyes, mouth) -> opaque


def face_alpha(fig, y_max=470):
    """Just the white mask (the face) above y_max, eye/nose holes filled: the occluder that sits over the type."""
    lum = np.asarray(mask_rgb.convert('L').filter(ImageFilter.GaussianBlur(2.5))).astype(np.float32)
    m = (lum > 11) & (fig > 0.5)
    m[:, :720] = False; m[:, 1240:] = False; m[y_max:] = False           # mask lives in x 760..1190; below y_max the knife joins it
    lab, n = ndimage.label(m)
    m = ndimage.binary_fill_holes(lab == lab[200, 975])                   # the blob through the nose bridge
    m = ndimage.gaussian_filter(ndimage.binary_opening(m, iterations=3).astype(np.float32), 5) > 0.5   # smooth the rim
    # the brow follows the hood's shadow line and comes out lumpy: round it into a clean dome (x 830..1130, above y 260)
    top = np.argmax(m, 0).astype(np.float32); ts = ndimage.gaussian_filter1d(top, 10, mode='nearest')
    yy = np.arange(m.shape[0])[:, None]; dome = slice(830, 1131)
    m[:260, dome] = yy[:260] >= ts[None, dome]
    return Image.fromarray((m * 255).astype(np.uint8), 'L').filter(ImageFilter.GaussianBlur(1.0))   # ~1px feather at output size


def lift_brow(im, fa, reach=85, target=0.45, max_gain=2.6):
    """Brighten the hood-shadowed top ~`reach` px of the mask so the edge that crosses the letters reads as pale mask, not a dark smudge.
    Gain comes from blurred luminance (texture kept) and only lifts what is darker than `target`."""
    a = np.asarray(fa) > 127; has = a.any(0); top = np.argmax(a, 0)
    yy = np.arange(im.size[1], dtype=np.float32)[:, None]
    ramp = np.clip(1 - (yy - top[None, :]) / reach, 0, 1) * (yy >= top[None, :]) * has[None, :]
    ramp = ndimage.gaussian_filter(ramp.astype(np.float32), 4)
    rgb = np.asarray(im.convert('RGB')).astype(np.float32) / 255
    L = ndimage.gaussian_filter(rgb @ np.array([0.299, 0.587, 0.114], np.float32), 6)
    gain = 1 + (np.clip(target / np.maximum(L, 0.02), 1, max_gain) - 1) * ramp
    rgb = rgb * gain[..., None]
    lum = (rgb @ np.array([0.299, 0.587, 0.114], np.float32))[..., None]
    rgb = rgb + (lum - rgb) * (0.55 * ramp[..., None])                   # the lifted shadow is hood-blue: pull it back to the mask's grey
    out = Image.fromarray((np.clip(rgb, 0, 1) * 255 + 0.5).astype(np.uint8), 'RGB').convert('RGBA')
    out.putalpha(im.getchannel('A')); return out


# ================================================================= A: mask + 16 KILLERS
def thumb_a(font=None, base=H - 32, name='ghostface_v2_a_mask_text.jpg'):
    s = 0.68                                                             # whole mask (brow to chin) in the top 3/4
    im = affine(mask_rgb, (975, 0), (W / 2, -45), s, (W, H))
    im = pop(im, 1.12, 1.0, 1.05)
    darken(im, vgrad(395, 640, 0, 235))                               # soft dark floor for the type
    side = Image.new('L', (W, H), 0); ImageDraw.Draw(side).ellipse([-420, -200, W + 420, H + 260], fill=255)
    darken(im, Image.eval(side.filter(ImageFilter.GaussianBlur(140)), lambda v: int((255 - v) * 0.55)))
    # f(200), centred 70px left: the S (stroke incl.) ends at x~1106, clear of YouTube's duration badge (~x1110-1252 / y621-692).
    # Do not raise the baseline instead: that pushes the type into the mask's mouth.
    segments_text(im, W / 2 - 70, base, [('16 ', RED), ('KILLERS', WHITE)], font or f(200), stroke=9)
    save(im, name)


# ================================================================= B: WHO'S #1? behind the mask
def thumb_b():
    fig = figure_alpha(); face = face_alpha(fig)
    s = W / 1920 * 1.08; top = 87                                        # figure 8% bigger than a full-width fit; source y=0 lands at output y=87
                                                                         # (brow at y~150 covers ~1/3 of O'S; mouth bottom at y~706 stays in frame)
    bg = affine(mask_rgb, (975, 0), (W / 2, top), s, (W, H))
    bg = pop(bg, 1.12, 1.0, 1.05); lit = bg.copy()
    darken(bg, vgrad(top - 6, top + 250, 255, 0))                        # night sky fades to black at the top (hides the still's top edge)
    darken(bg, vgrad(560, H, 0, 150))
    # type
    txt = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    font = ImageFont.truetype(os.path.join(HERE, '..', 'ep01', 'YouTubeSans-Black.otf'), 238)
    segments_text(txt, W / 2, 210, [("WHO'S ", WHITE), ('#1', RED), ('?', WHITE)], font, stroke=9)   # raised 16px with the bigger figure
    im = bg.copy(); im.alpha_composite(txt)
    # the mask itself, cut out, laid back over the letters (+ a contact shadow on the type)
    fa = affine(face.convert('RGBA'), (975, 0), (W / 2, top), s, (W, H), fill=(0, 0, 0, 0)).getchannel('R')
    shadow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    shadow.putalpha(Image.eval(fa.filter(ImageFilter.GaussianBlur(10)), lambda v: int(v * 0.85)))
    sh_mask = Image.new('L', (W, H), 0); sh_mask.paste(txt.getchannel('A'))
    sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); sh.paste(shadow, (6, 10))
    sh.putalpha(Image.fromarray(np.minimum(np.asarray(sh.getchannel('A')), np.asarray(sh_mask)), 'L'))
    im.alpha_composite(sh)
    face_layer = lift_brow(lit, fa); face_layer.putalpha(fa)            # the mask keeps its own light, brow lifted
    im.alpha_composite(face_layer)
    save(im, 'ghostface_v2_b_text_behind.jpg')


# ================================================================= C: three faces, eyes level
PW = [427, 426, 427]
EYE_Y = 238
FEATHER = 70
# Roman: Scream 3 reveal frame (black robe, glaring), 1221x793, from scream.fandom.com File:Roman-Bridger-008.png.
# Kept in the scratchpad like the key art (not committed); scale ~1.0, so no upscale.
ROMAN = SCR + '/v2work/thumbs4/roman/roman_s3_reveal.png'
FACE_SPECS = [
    # file, left/right eye (source px), valid rows of the still (letterbox), scale, x nudge, how much to level the eyes, pct, colour, brightness lift
    dict(path=os.path.join(FACES, 'carvey.jpg'), el=(855, 364), er=(1012, 337), rows=(140, 940), scale=0.82, nudge=-10, rot=0.6, pct='99%', col=GREEN, lift=1.16),
    dict(path=os.path.join(GFT, 'ethan.jpg'), el=(1615, 615), er=(2190, 625), rows=(0, 2160), scale=0.285, nudge=0, rot=1.0, pct='53%', col=YEL),
    dict(path=ROMAN, el=(492, 307), er=(624, 305), rows=(0, 793), scale=0.99, nudge=0, rot=1.0, pct='15%', col=RED, lift=1.08),
]


def teal_grade(p, desat=0.72, shadow=(-0.045, 0.015, 0.035), high=(0.02, 0.005, -0.02)):
    """One shared dark-teal grade for all three panels (pulls the orange/blue/brown sources into one look)."""
    a = np.asarray(p.convert('RGB')).astype(np.float32) / 255
    L = (a @ np.array([0.299, 0.587, 0.114], np.float32))[..., None]
    a = L + (a - L) * desat
    a = a + (1 - L) ** 2 * np.array(shadow, np.float32) + L ** 2 * np.array(high, np.float32)
    out = Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8), 'RGB').convert('RGBA')
    out.putalpha(p.getchannel('A')); return out


def face_panel(sp, pw):
    im = Image.open(sp['path']).convert('RGBA')
    (x0, y0), (x1, y1) = sp['el'], sp['er']
    ang = math.atan2(y1 - y0, x1 - x0) * sp['rot']
    mid = ((x0 + x1) / 2, (y0 + y1) / 2)
    dst = (pw / 2 + sp['nudge'], EYE_Y)
    p = affine(im, mid, dst, sp['scale'], (pw, H), ang)
    valid = Image.new('L', im.size, 0); ImageDraw.Draw(valid).rectangle([0, sp['rows'][0] + 2, im.size[0], sp['rows'][1] - 2], fill=255)
    v = affine(valid.convert('RGBA'), mid, dst, sp['scale'], (pw, H), ang, fill=(0, 0, 0, 0)).getchannel('R')
    t = np.clip(ndimage.distance_transform_edt(np.asarray(v) > 127) / FEATHER, 0, 1)   # 0 where the still runs out -> 1 FEATHER px inside
    v = Image.fromarray((t * t * (3 - 2 * t) * 255).astype(np.uint8), 'L')
    if sp['scale'] > 1.2: p = p.filter(ImageFilter.UnsharpMask(2.2, 70, 2))
    p = teal_grade(pop(p, 1.12, 1.04 * sp.get('lift', 1.0), 1.08))
    out = Image.new('RGBA', (pw, H), (0, 0, 0, 255)); out.paste(p, (0, 0), v)
    vig = Image.new('L', (pw, H), 0)
    ImageDraw.Draw(vig).ellipse([dst[0] - pw * 0.62, EYE_Y - 300, dst[0] + pw * 0.62, EYE_Y + 420], fill=255)
    darken(out, Image.eval(vig.filter(ImageFilter.GaussianBlur(70)), lambda v_: int((255 - v_) * 0.6)))
    return out


def thumb_c():
    im = Image.new('RGBA', (W, H), (0, 0, 0, 255)); x = 0
    for sp, pw in zip(FACE_SPECS, PW):
        im.paste(face_panel(sp, pw), (x, 0)); x += pw
    darken(im, vgrad(352, 567, 0, 225))                               # floor for the numbers (raised with them)
    d = ImageDraw.Draw(im)
    for k in (1, 2):                                                     # thin black gutters
        gx = sum(PW[:k]); d.rectangle([gx - 3, 0, gx + 3, H], fill=(0, 0, 0, 255))
    x = 0
    for sp, pw in zip(FACE_SPECS, PW):                                   # bottoms (stroke incl.) at y~618: '15%' clears the duration badge (y621+)
        shadow_text(im, (x + pw // 2, H - 178), sp['pct'], f(182), sp['col'], stroke=8); x += pw
    save(im, 'ghostface_v2_c_extremes.jpg')


if __name__ == '__main__':
    which = os.environ.get('ONLY', 'abc')
    if 'a' in which: thumb_a()
    if 'b' in which: thumb_b()
    if 'c' in which: thumb_c()
