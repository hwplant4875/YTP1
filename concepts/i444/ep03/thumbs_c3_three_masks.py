# EP03 thumbnail C3, family three_masks: thumb_c()'s layout (thumbs_v2.py) with three Ghostface MASKS instead of
# the unmasked killers, so nothing spoils who the killers are.
#   99% (Jason Carvey, Scream VI opening): clean white mask in the subway       smallest, a little dimmer
#   53% (Ethan Landry, Scream VI):          the aged, cracked shrine mask       reference size
#   10% (Roman Bridger, Scream 3 finale):   the old-style mask, head cocked     biggest, brightest (size rises as survival falls)
# Same as C: 1280x720, panels 427/426/427 with thin black gutters, f(182) % at the same spots and colours,
# one shared dark-teal grade, one shared eye line (centre of the two eye holes), duration-badge corner kept black.
# Source stills are official studio stills (TMDB) in the scratchpad; never committed.
# Run with the rembg venv (needs rembg + scipy):
#   <scratchpad>/rbenv/bin/python -I thumbs_c3_three_masks.py [MASKS_DIR] [OUT_DIR] [CACHE_DIR]
import os, sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'ep01'))
from gfx import f, shadow_text, RED                 # same font + text helper as thumbs_v2.py
from thumbs_v2_lib import pop

SCR = '/tmp/claude-0/-home-user-YTP1/bb3b993e-7de0-5d78-af5e-c29db5ac82a5/scratchpad'
MASKS = sys.argv[1] if len(sys.argv) > 1 else SCR + '/gft/masks'          # TMDB stills (never in the repo)
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, 'upload')
CACHE = sys.argv[3] if len(sys.argv) > 3 else SCR + '/v2work/thumbs_c3'   # rembg matte cache (never in the repo)
NAME = 'ghostface_v2_c3_three_masks.jpg'
W, H = 1280, 720
GREEN = (70, 215, 95, 255); YEL = (250, 200, 40, 255)
PW = [427, 426, 427]
EYE_Y = 166          # shared eye line (C's faces sit at 238; masks are taller, so the line is higher and every chin clears the %)
D2C = 282            # eye-line -> chin in output px at size 1.0 (each spec scales it with 'size')
FEATHER = 70
LUMA = np.array([0.299, 0.587, 0.114], np.float32)
os.makedirs(OUT, exist_ok=True); os.makedirs(CACHE, exist_ok=True)


# ---------------------------------------------------------------- helpers (same as thumbs_v2.py)
def affine(im, src_pt, dst_pt, scale, size, angle=0.0, fill=(0, 0, 0, 255)):
    """Map src_pt -> dst_pt, scaled by `scale`, rotated by `angle` (radians, clockwise) about that point."""
    ca, sa = math.cos(angle) / scale, math.sin(angle) / scale
    a, b, d, e = ca, -sa, sa, ca
    c = src_pt[0] - a * dst_pt[0] - b * dst_pt[1]
    f_ = src_pt[1] - d * dst_pt[0] - e * dst_pt[1]
    return im.transform(size, Image.AFFINE, (a, b, c, d, e, f_), Image.BICUBIC, fillcolor=fill)


def darken(im, mask_l):
    im.paste((0, 0, 0, 255), (0, 0), mask_l)


def vgrad(y0, y1, a0, a1, size=(W, H)):
    y = np.arange(size[1], dtype=np.float32)
    t = np.clip((y - y0) / (y1 - y0), 0, 1); t = t * t * (3 - 2 * t)
    col = (a0 + (a1 - a0) * t).astype(np.uint8)
    return Image.fromarray(np.repeat(col[:, None], size[0], 1), 'L')


def teal_grade(p, desat=0.72, shadow=(-0.045, 0.015, 0.035), high=(0.02, 0.005, -0.02)):
    a = arr(p)
    L = (a @ LUMA)[..., None]
    a = L + (a - L) * desat
    a = a + (1 - L) ** 2 * np.array(shadow, np.float32) + L ** 2 * np.array(high, np.float32)
    return img(a)


def arr(p): return np.asarray(p.convert('RGB')).astype(np.float32) / 255
def img(a): return Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8), 'RGB').convert('RGBA')


# ---------------------------------------------------------------- mask-specific steps
def neutralise(a, amount):
    """Partial grey-world white balance, so the green subway, the olive room and the warm projector light
    all enter the shared teal grade from about the same neutral place."""
    m = a.reshape(-1, 3).mean(0)
    return np.clip(a * (1 + (m.mean() / np.maximum(m, 1e-3) - 1) * amount), 0, 1)


def despeckle(a, thr=0.05):
    """Remove dust specks in a dark room (isolated 1-2 px highlights on the robe/wall), keep everything larger."""
    L = a @ LUMA
    top = L - ndimage.grey_opening(L, size=(4, 4))
    spot = ndimage.binary_dilation((top > thr) & (ndimage.median_filter(L, 7) < 0.30), iterations=1)
    med = np.stack([ndimage.median_filter(a[..., c], 7) for c in range(3)], -1)
    return np.where(spot[..., None], med, a)


def rembg_matte(path):
    """isnet-general-use figure matte, cached (sources wider than 1920 are matted at 1920 and scaled back)."""
    p = os.path.join(CACHE, os.path.basename(path).split('.')[0][:6] + '_matte.png')
    if not os.path.exists(p):
        from rembg import remove, new_session
        im = Image.open(path).convert('RGB'); full = im.size
        if im.size[0] > 1920: im = im.resize((1920, round(1920 * im.size[1] / im.size[0])), Image.LANCZOS)
        remove(im, session=new_session('isnet-general-use'), only_mask=True).resize(full, Image.BILINEAR).save(p)
    return Image.open(p).convert('L')


def guided(I, r, eps):
    """Self-guided filter (He et al.): smooths flat plastic, keeps the eye-hole and hood edges."""
    box = lambda x: ndimage.uniform_filter(x, 2 * r + 1)
    m = box(I); v = box(I * I) - m * m
    k = v / (v + eps)
    return box(k) * I + box(m - k * m)


def clean_mask(a, prot, amt):
    """Scream 3's 4K transfer is grainy with colour noise and red-brown eye holes. On the mask only:
    3px median + edge-preserving (guided) smoothing on luma, blurred + reduced chroma, and the dark eye/nose
    holes pushed to neutral black. Runs before the levelling, so the grain is not lifted with the whites."""
    Y = a @ LUMA; C = a - Y[..., None]
    Y2 = guided(ndimage.median_filter(Y, 3), 3, 0.0025)
    C2 = np.stack([ndimage.gaussian_filter(C[..., c], 2.0) for c in range(3)], -1) * (1 - amt)
    hole = np.clip((0.20 - ndimage.gaussian_filter(Y2, 1.0)) / 0.10, 0, 1)        # holes are < ~0.12 here, the cheek shadow > 0.16
    Y2 = Y2 * (1 - 0.6 * hole); C2 = C2 * (1 - hole[..., None])
    Y2 = Y2 + 0.30 * (Y2 - ndimage.gaussian_filter(Y2, 1.2))                     # gentle luma-only sharpen (replaces the old unsharp pass)
    w = prot[..., None]
    return np.clip(a * (1 - w) + (Y2[..., None] + C2) * w, 0, 1)


def mask_level(a, box, target, pct=97, max_gain=1.9):
    """Bring the mask's highlights (pct-th percentile of luma inside `box`) to `target`, on a highlight-weighted
    curve so the black robe is not lifted into grey."""
    L = a @ LUMA
    x0, y0, x1, y1 = [int(v) for v in box]
    hi = np.percentile(L[max(y0, 0):y1, max(x0, 0):x1], pct)
    g = float(np.clip(target / max(hi, 1e-3), 1 / max_gain, max_gain))
    w = np.clip(ndimage.gaussian_filter(L, 3) / max(hi, 1e-3), 0, 1)[..., None] ** 0.7
    return np.clip(a * (1 + (g - 1) * w), 0, 1), g, hi


def shoulder(a, knee=0.80, top=0.92):
    """Soft highlight roll-off: nothing on the mask clips (the brightest white tops out at ~235)."""
    L = a @ LUMA
    k = top - knee
    L2 = np.where(L > knee, knee + k * (1 - np.exp(-(L - knee) / k)), L)
    return np.clip(a * (L2 / np.maximum(L, 1e-4))[..., None], 0, 1)


def burn(a, region, amount, feather, ramp=None, keep=None):
    """Darken a panel-space box (x0, y0, x1, y1) by `amount`, edges feathered; ramp='lr' fades it out left -> right;
    `keep` (0..1 per px) shields the mask itself."""
    m = np.zeros(a.shape[:2], np.float32)
    x0, y0, x1, y1 = region
    m[max(y0, 0):y1, max(x0, 0):x1] = 1
    if ramp == 'lr':
        t = np.clip((np.arange(a.shape[1]) - x0) / max(x1 - x0, 1), 0, 1)
        m *= (1 - t * t * (3 - 2 * t))[None, :]
    m = ndimage.gaussian_filter(m, feather) if feather else m
    if keep is not None: m = m * (1 - keep)
    return a * (1 - amount * m)[..., None]


# ---------------------------------------------------------------- the three stills
# el/er = centres of the two eye holes (source px), chin = bottom of the mask's chin, rot = how much of the eye-line tilt to level
# (rot > 1 also takes out part of the head's cock), size = mask size relative to D2C.
# The 10% mask's protect polygon traces the mask (with a hood margin) and stops at the jaw: everything outside it
# (robe, the grey shoulder under the chin, the bright projection behind) is treated as set and dimmed.
FINALE_MASK = [(1790, 110), (1900, 105), (2010, 160), (2030, 400), (2010, 560), (1900, 680), (1800, 800), (1760, 850), (1722, 874),
               (1698, 874), (1688, 845), (1670, 826), (1662, 700), (1640, 520), (1600, 470), (1595, 330), (1660, 230), (1720, 150)]
SPECS = [
    # Scream VI subway, ~1.04x: 0.9 size and a lower white target so the 'safe' 99% is the smallest, quietest mask
    dict(path='3dhqnLluOzBZM1udggS5WgUxjxL.jpg', el=(634, 225), er=(740, 224), chin=(701, 467), rot=1.0, size=0.90, nudge=0,
         pct='99%', col=GREEN, wb=0.55, target=0.75, sharpen=30, matte='rembg', bg_keep=0.80, bg_desat=0.45,
         burns=[((0, 0, 60, 360), 0.5, 18, None),                           # warm red/beige subway corner, top left
                ((70, 385, 140, 425), 0.7, 8, None)]),                       # a grey glint on the robe, lower left
    # Scream VI shrine, 0.39x (LANCZOS, light unsharp)
    dict(path='6SoQGZAfH560XBbEDOxowglqPx0.jpg', el=(1768, 596), er=(2028, 592), chin=(1916, 1310), rot=1.0, size=1.0, nudge=0,
         pct='53%', col=YEL, wb=0.45, target=0.76, sharpen=25, despeckle=True),   # aged cracked mask (keeps a little bone colour)
    # Scream 3 finale, 0.55x; rot 1.5 straightens about half of the cocked head (eye holes still level within +-3 px)
    dict(path='7AOvUIJVfpRa7xkiuGFWKGr7XfA.jpg', el=(1718, 320), er=(1862, 335), chin=(1705, 870), rot=1.5, size=1.07, nudge=18,
         pct='10%', col=RED, wb=0.7, target=0.84, denoise=0.6, feather=28,      # denoise = chroma cut; the still's top edge is in the black hood: short feather
         protect=[FINALE_MASK], bg_keep=0.36, bg_desat=0.6,
         burns=[((0, 0, 120, 470), 0.5, 10, 'lr'),                           # pale projection band along the left gutter
                ((-20, 430, 447, 740), 0.8, 14, None, 'bg')]),               # grey shoulder/vest under the chin, under the number, badge corner
]


def mask_panel(sp, pw):
    src = Image.open(os.path.join(MASKS, sp['path'])).convert('RGB')
    (x0, y0), (x1, y1) = sp['el'], sp['er']
    ang = math.atan2(y1 - y0, x1 - x0) * sp['rot']
    mid = ((x0 + x1) / 2, (y0 + y1) / 2)
    scale = D2C * sp['size'] / math.hypot(sp['chin'][0] - mid[0], sp['chin'][1] - mid[1])
    dst = (pw / 2 + sp['nudge'], EYE_Y)
    # downscales go through a proper LANCZOS resize first (PIL's affine does not prefilter, which kept the film grain crunchy)
    pre = min(scale, 1.0)
    im = src.resize((round(src.size[0] * pre), round(src.size[1] * pre)), Image.LANCZOS) if pre < 1 else src
    k = im.size[0] / src.size[0]; m_ = (mid[0] * k, mid[1] * k); s = scale / k
    p = affine(im.convert('RGBA'), m_, dst, s, (pw, H), ang)
    valid = Image.new('L', im.size, 0); ImageDraw.Draw(valid).rectangle([0, 2, im.size[0], im.size[1] - 2], fill=255)
    v = affine(valid.convert('RGBA'), m_, dst, s, (pw, H), ang, fill=(0, 0, 0, 0)).getchannel('R')
    t = np.clip(ndimage.distance_transform_edt(np.asarray(v) > 127) / sp.get('feather', FEATHER), 0, 1)
    v = Image.fromarray((t * t * (3 - 2 * t) * 255).astype(np.uint8), 'L')
    # where the figure is (1) vs the set behind it (0), in panel px
    prot = None
    if 'protect' in sp:
        pm = Image.new('L', src.size, 0); dr = ImageDraw.Draw(pm)
        for poly in sp['protect']: dr.polygon(poly, fill=255)
    elif sp.get('matte') == 'rembg':
        pm = rembg_matte(os.path.join(MASKS, sp['path']))
    else:
        pm = None
    if pm is not None:
        pm = pm.resize(im.size, Image.BILINEAR)
        pm = affine(pm.convert('RGBA'), m_, dst, s, (pw, H), ang, fill=(0, 0, 0, 0)).getchannel('R')
        prot = np.asarray(pm.filter(ImageFilter.GaussianBlur(10))).astype(np.float32) / 255
    if s > 1.0: p = p.filter(ImageFilter.UnsharpMask(1.6, sp.get('sharpen', 40), 2))     # 99%: the only upscale (~1.04x)
    elif sp.get('sharpen'): p = p.filter(ImageFilter.UnsharpMask(1.4, sp['sharpen'], 2))
    a = arr(p)
    if sp.get('denoise'): a = clean_mask(a, prot, sp['denoise'])
    if sp.get('despeckle'): a = despeckle(a)
    a = neutralise(a, sp.get('wb', 0.6))
    if prot is not None:                          # dim + desaturate the set, not the figure
        L = (a @ LUMA)[..., None]; bg = (1 - prot)[..., None]
        a = a + (L - a) * sp.get('bg_desat', 0) * bg
        a = a * (1 - (1 - sp.get('bg_keep', 1.0)) * bg)
    half = 0.55 * D2C * sp['size']                # highlight levelling box: eye line to chin, about +-1.1 eye spacings
    a, g, hi = mask_level(a, (dst[0] - half, EYE_Y - 0.45 * D2C * sp['size'], dst[0] + half, EYE_Y + D2C * sp['size']), sp['target'])
    p = teal_grade(pop(img(a), 1.12, 1.04, 1.08))
    a = shoulder(arr(p), sp.get('hi_knee', 0.80))
    for b in sp.get('burns', []):
        a = burn(a, *b[:4], keep=prot if b[4:] == ('bg',) else None)
    out = Image.new('RGBA', (pw, H), (0, 0, 0, 255)); out.paste(img(a), (0, 0), v)
    vig = Image.new('L', (pw, H), 0)
    ImageDraw.Draw(vig).ellipse([dst[0] - pw * 0.62, EYE_Y - 300, dst[0] + pw * 0.62, EYE_Y + 440], fill=255)
    darken(out, Image.eval(vig.filter(ImageFilter.GaussianBlur(70)), lambda v_: int((255 - v_) * 0.55)))
    chin = (sp['chin'][0] - mid[0], sp['chin'][1] - mid[1])
    chin_y = EYE_Y + scale * (-math.sin(ang) * chin[0] + math.cos(ang) * chin[1])
    print('  %-34s scale %.3f  rot %.1f deg  chin y %.0f  mask hi %.2f -> gain %.2f' % (sp['path'], scale, math.degrees(ang), chin_y, hi, g))
    return out


def thumb_c3():
    im = Image.new('RGBA', (W, H), (0, 0, 0, 255)); x = 0
    for sp, pw in zip(SPECS, PW):
        im.paste(mask_panel(sp, pw), (x, 0)); x += pw
    darken(im, vgrad(372, 575, 0, 225))                                  # floor for the numbers (starts below C's so the chins stay pale)
    d = ImageDraw.Draw(im)
    for k in (1, 2):                                                     # thin black gutters
        gx = sum(PW[:k]); d.rectangle([gx - 3, 0, gx + 3, H], fill=(0, 0, 0, 255))
    x = 0
    for sp, pw in zip(SPECS, PW):                                        # identical to thumb_c(): bottoms at y~618, clear of the duration badge
        shadow_text(im, (x + pw // 2, H - 178), sp['pct'], f(182), sp['col'], stroke=8); x += pw
    path = os.path.join(OUT, NAME)
    im.convert('RGB').save(path, quality=93); print('wrote', path)


if __name__ == '__main__':
    thumb_c3()
