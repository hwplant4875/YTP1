# EP03 thumbnail C2 ("two masks"): thumb C's winning format with Ghostface masks in place of two killers' faces (no spoilers).
#   99% = Jason Carvey's face, exactly as in thumb C (thumbs_v2.py) / 53% = Scream VI mask (Ethan's film) / 10% = Scream 3 mask (Roman's film)
#   Same 1280x720, three panels, black gutters, % numbers, dark-teal grade, shared eye line (for a mask: its two eye-hole centres).
#   The 10% mask is the biggest and brightest of the three, so the threat climbs left to right.
# Run with the rembg venv (needs rembg + scipy):
#   <scratchpad>/rbenv/bin/python thumbs_c2_two_masks.py [MASK_DIR] [OUT_DIR] [CACHE_DIR]
# The stills are official studio stills (TMDB); they stay in the scratchpad and are never committed.
import os, sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'ep01'))
from gfx import f, shadow_text, RED
from thumbs_v2_lib import pop

SCR = '/tmp/claude-0/-home-user-YTP1/bb3b993e-7de0-5d78-af5e-c29db5ac82a5/scratchpad'
MASKS = sys.argv[1] if len(sys.argv) > 1 else SCR + '/gft/masks'          # Scream VI / Scream 3 stills
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, 'upload')
CACHE = sys.argv[3] if len(sys.argv) > 3 else SCR + '/v2work/thumbs3'     # rembg matte cache (never in the repo)
FACES = os.path.join(HERE, 'faces')
NAME = 'ghostface_v2_c2_two_masks.jpg'
W, H = 1280, 720
PW = [427, 426, 427]
EYE_Y = 238
FEATHER = 70
GREEN = (70, 215, 95, 255); YEL = (250, 200, 40, 255)
LUMA = np.array([0.299, 0.587, 0.114], np.float32)
os.makedirs(OUT, exist_ok=True); os.makedirs(CACHE, exist_ok=True)


# ---------------------------------------------------------------- helpers (copied from thumbs_v2.py so this file runs on its own)
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
    """Vertical alpha ramp: a0 at y0 -> a1 at y1 (smoothstep), held outside."""
    y = np.arange(size[1], dtype=np.float32)
    t = np.clip((y - y0) / (y1 - y0), 0, 1); t = t * t * (3 - 2 * t)
    col = (a0 + (a1 - a0) * t).astype(np.uint8)
    return Image.fromarray(np.repeat(col[:, None], size[0], 1), 'L')


def teal_grade(p, desat=0.72, shadow=(-0.045, 0.015, 0.035), high=(0.02, 0.005, -0.02)):
    """One shared dark-teal grade for all three panels."""
    a = np.asarray(p.convert('RGB')).astype(np.float32) / 255
    L = (a @ LUMA)[..., None]
    a = L + (a - L) * desat
    a = a + (1 - L) ** 2 * np.array(shadow, np.float32) + L ** 2 * np.array(high, np.float32)
    out = Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8), 'RGB').convert('RGBA')
    out.putalpha(p.getchannel('A')); return out


def edge_feather(v):
    """0 where the still runs out -> 1 FEATHER px inside (smoothstep)."""
    t = np.clip(ndimage.distance_transform_edt(np.asarray(v) > 127) / FEATHER, 0, 1)
    return Image.fromarray((t * t * (3 - 2 * t) * 255).astype(np.uint8), 'L')


def vignette(out, dst, pw):
    vig = Image.new('L', (pw, H), 0)
    ImageDraw.Draw(vig).ellipse([dst[0] - pw * 0.62, EYE_Y - 300, dst[0] + pw * 0.62, EYE_Y + 420], fill=255)
    darken(out, Image.eval(vig.filter(ImageFilter.GaussianBlur(70)), lambda v_: int((255 - v_) * 0.6)))


def rgb_f(im): return np.asarray(im.convert('RGB')).astype(np.float32) / 255


def from_f(a, alpha=None):
    out = Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8), 'RGB').convert('RGBA')
    if alpha is not None: out.putalpha(alpha)
    return out


def smooth(t): t = np.clip(t, 0, 1); return t * t * (3 - 2 * t)


def tone_lift(a, g):
    """Soft-knee lift (x*g / (1 + x*(g-1))): dark stills open up, highlights do not clip."""
    return a * g / (1 + a * (g - 1))


# ---------------------------------------------------------------- 99%: Carvey, = thumbs_v2.FACE_SPECS[0] + face_panel()
CARVEY = dict(path=os.path.join(FACES, 'carvey.jpg'), el=(855, 364), er=(1012, 337), rows=(140, 940),
              scale=0.82, nudge=-10, rot=0.6, pct='99%', col=GREEN, lift=1.16)


def face_panel(sp, pw):
    im = Image.open(sp['path']).convert('RGBA')
    (x0, y0), (x1, y1) = sp['el'], sp['er']
    ang = math.atan2(y1 - y0, x1 - x0) * sp['rot']
    mid = ((x0 + x1) / 2, (y0 + y1) / 2)
    dst = (pw / 2 + sp['nudge'], EYE_Y)
    p = affine(im, mid, dst, sp['scale'], (pw, H), ang)
    valid = Image.new('L', im.size, 0); ImageDraw.Draw(valid).rectangle([0, sp['rows'][0] + 2, im.size[0], sp['rows'][1] - 2], fill=255)
    v = edge_feather(affine(valid.convert('RGBA'), mid, dst, sp['scale'], (pw, H), ang, fill=(0, 0, 0, 0)).getchannel('R'))
    if sp['scale'] > 1.2: p = p.filter(ImageFilter.UnsharpMask(2.2, 70, 2))
    p = teal_grade(pop(p, 1.12, 1.04 * sp.get('lift', 1.0), 1.08))
    out = Image.new('RGBA', (pw, H), (0, 0, 0, 255)); out.paste(p, (0, 0), v)
    vignette(out, dst, pw)
    return out


# ---------------------------------------------------------------- 53% / 10%: masks
# el/er = eye-hole centres, mouth = chin rim y (source px); scale = output px per source px (both are downscales).
MASK_SPECS = [
    # Scream VI: weathered, cracked mask, front-on, black hood on an olive wall (3840x2160). Chin rim at y~476, just above the digits.
    dict(path='6SoQGZAfH560XBbEDOxowglqPx0.jpg', el=(1765, 608), er=(2022, 592), mouth=1285, scale=0.348,
         gain=2.1, wb=0.7, despeckle=True, pct='53%', col=YEL),
    # Scream 3 (2551x1435): hooded, near front-on, blue-lit window behind the hood's right side.
    # Biggest and brightest mask (eye holes ~97px apart vs ~90 for 53%). With the eye line level with the others,
    # the chin rim tucks behind the top of the '10' and the long scream mouth shows down to it.
    dict(path='ckIUnXuWSHAc98QcwsmMShQvGNi.jpg', el=(1125, 470), er=(1243, 466), mouth=800, scale=0.82,
         gain=2.3, wb=1.0, pct='10%', col=RED,
         matte='ckiu_rembg_isnet.png',                 # rembg figure matte (hood + mask + robe) for the set work below
         white=1.55,                                   # mask whites: soft-knee lift through the face matte (p95 ~129 -> ~175)
         hood=2.2,                                     # hood fabric gain on the window side, so the robe reads as cloth
         chroma=1.5,                                   # chroma blur (px): film-grain colour speckle on the lifted hood
         warm=(3, 0, -3),                              # a touch warmer, towards Carvey's panel
         bg=dict(blur=10, keep=0.55, desat=0.8),       # window specks -> soft, grey, dim backlight
         rim=dict(lum=20, width=15, y=(0, 430))),      # cool rim (+20 luma, ~15px) inside the hood outline, window side
]


def neutral_wb(a, sp, amount):
    """Pull the lit mask surface (between the eye holes and the chin) to neutral grey, so both masks enter the grade alike."""
    (x0, y0), (x1, y1) = sp['el'], sp['er']
    s = math.hypot(x1 - x0, y1 - y0); cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    box = a[int(cy - 1.2 * s):int(sp['mouth']), int(cx - 1.1 * s):int(cx + 1.1 * s)].reshape(-1, 3)
    L = box @ LUMA
    m = box[L > np.percentile(L, 60)].mean(0)
    return a * (1 + (m.mean() / m - 1) * amount)


def figure_matte(sp, path):
    """rembg (isnet-general-use) matte of hood + mask + robe, cached outside the repo."""
    p = os.path.join(CACHE, sp['matte'])
    if not os.path.exists(p):
        from rembg import remove, new_session
        im = Image.open(path).convert('RGB'); full = im.size
        if im.size[0] > 1920: im = im.resize((1920, round(1920 * im.size[1] / im.size[0])), Image.LANCZOS)
        remove(im, session=new_session('isnet-general-use'), only_mask=True).resize(full, Image.BILINEAR).save(p)
    return Image.open(p).convert('L')


def face_matte(a, dst, s_eye):
    """The white mask itself in panel px (lit and shadow side): clearly brighter than the hood, joined to the nose,
    eye holes and mouth filled, ~2px feather."""
    L = ndimage.gaussian_filter(a @ LUMA, 2)
    box = np.zeros(L.shape, bool)
    box[int(dst[1] - 1.6 * s_eye):int(dst[1] + 3.4 * s_eye), int(dst[0] - 1.3 * s_eye):int(dst[0] + 1.3 * s_eye)] = True
    m = ndimage.binary_opening((L > 0.09) & box, iterations=2)
    lab, _ = ndimage.label(m)
    m = lab == lab[int(dst[1] + 0.45 * s_eye), int(dst[0])]                  # the blob through the nose
    m = ndimage.binary_fill_holes(ndimage.binary_closing(m, iterations=3))
    return ndimage.gaussian_filter(ndimage.binary_dilation(m).astype(np.float32), 2)


def treat_set(a, fig, fm, sp, dst, s_eye):
    """Before the grade: a brighter, neutral mask; the hood's fabric opened up on the window side;
    the blue window specks behind the hood defocused, greyed and dimmed into a soft backlight."""
    yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]].astype(np.float32)
    # mask whites up (soft knee, nothing clips) and its blue cast to neutral grey, through the face matte only
    lifted = tone_lift(a, sp['white'])
    ll = (lifted @ LUMA)[..., None]
    a = a + (ll + (lifted - ll) * 0.35 - a) * fm[..., None]
    # hood fabric right of the mask: texture lifted (a gain, not a flat veil) so the robe does not sink into the black
    w = fig * (1 - fm) * smooth((xx - dst[0] - 0.4 * s_eye) / (1.2 * s_eye)) * smooth((yy - 60) / 80) * smooth((470 - yy) / 120)
    a = a * (1 + (sp['hood'] - 1) * w[..., None])
    # background (outside the figure matte): defocus, grey, dim
    bgw = np.clip(1 - fig, 0, 1); b = sp['bg']
    blur = np.stack([ndimage.gaussian_filter(a[..., c] * bgw, b['blur']) for c in range(3)], -1)
    soft = blur / np.maximum(ndimage.gaussian_filter(bgw, b['blur'])[..., None], 1e-3)   # normalised: the hood does not bleed in
    sl = (soft @ LUMA)[..., None]
    soft = (sl + (soft - sl) * (1 - b['desat'])) * b['keep']
    a = a + (soft - a) * bgw[..., None]
    return np.clip(a, 0, 1)


def add_rim(out, fig, fm, sp, dst, s_eye):
    """After the grade: a faint cool rim just inside the hood's outline on the window side."""
    r = sp['rim']
    inside = ndimage.distance_transform_edt(fig > 0.5)                       # the panel's own edges do not count as outline
    band = ndimage.gaussian_filter(np.exp(-(inside / r['width']) ** 2) * (fig > 0.5), 2)
    yy, xx = np.mgrid[0:fig.shape[0], 0:fig.shape[1]].astype(np.float32)
    w = band * smooth((xx - dst[0]) / (1.2 * s_eye)) * smooth((yy - r['y'][0]) / 30) * smooth((r['y'][1] - yy) / 60) * (1 - fm)
    return from_f(rgb_f(out) + w[..., None] * r['lum'] / 255 * np.array([0.85, 1.0, 1.2], np.float32))


def mask_panel(sp, pw):
    path = os.path.join(MASKS, sp['path'])
    src = Image.open(path).convert('RGB'); full_w = src.size[0]
    src = Image.fromarray(np.clip(neutral_wb(np.asarray(src).astype(np.float32), sp, sp['wb']), 0, 255).astype(np.uint8), 'RGB')
    (x0, y0), (x1, y1) = sp['el'], sp['er']
    ang = math.atan2(y1 - y0, x1 - x0)                                        # eye holes fully level
    mid = ((x0 + x1) / 2, (y0 + y1) / 2)
    scale = sp['scale']
    # pre-shrink with LANCZOS (PIL's affine does not antialias when reducing), then the affine runs at ~1:1
    src = src.resize((round(src.size[0] * scale), round(src.size[1] * scale)), Image.LANCZOS)
    if sp.get('despeckle'):                                                   # white dust specks on the VI hood
        q = np.asarray(src).astype(np.int16); med = np.asarray(src.filter(ImageFilter.MedianFilter(5))).astype(np.int16)
        spot = ndimage.binary_dilation(((q.mean(2) - med.mean(2)) > 18) & (med.mean(2) < 40), iterations=1)
        q[spot] = med[spot]; src = Image.fromarray(q.astype(np.uint8), 'RGB')
    k = src.size[0] / full_w
    mid_p, s_aff = (mid[0] * k, mid[1] * k), scale / k
    dst = (pw / 2, EYE_Y)
    p = affine(src.convert('RGBA'), mid_p, dst, s_aff, (pw, H), ang)
    valid = Image.new('L', src.size, 0); ImageDraw.Draw(valid).rectangle([0, 2, src.size[0] - 3, src.size[1] - 3], fill=255)
    v = edge_feather(affine(valid.convert('RGBA'), mid_p, dst, s_aff, (pw, H), ang, fill=(0, 0, 0, 0)).getchannel('R'))
    p = p.filter(ImageFilter.UnsharpMask(1.2, 45, 2))                         # crisp mask rim for phone size
    a = tone_lift(rgb_f(p), sp['gain'])
    if sp.get('chroma'):
        L = (a @ LUMA)[..., None]
        a = L + np.stack([ndimage.gaussian_filter((a - L)[..., c], sp['chroma']) for c in range(3)], -1)
    s_eye = math.hypot(x1 - x0, y1 - y0) * scale
    if sp.get('matte'):
        fig = figure_matte(sp, path).resize(src.size, Image.BILINEAR)
        fig = np.asarray(affine(fig.convert('RGBA'), mid_p, dst, s_aff, (pw, H), ang, fill=(0, 0, 0, 0)).getchannel('R')).astype(np.float32) / 255
        fm = face_matte(a, dst, s_eye)
        a = treat_set(a, fig, fm, sp, dst, s_eye)
    p = teal_grade(pop(from_f(a), 1.12, 1.04, 1.08))                         # same pop + grade as the face panels
    if sp.get('warm'):                                                        # blacks stay black
        q = rgb_f(p)
        p = from_f(q + np.array(sp['warm'], np.float32) / 255 * np.clip((q @ LUMA) / 0.2, 0, 1)[..., None], p.getchannel('A'))
    out = Image.new('RGBA', (pw, H), (0, 0, 0, 255)); out.paste(p, (0, 0), v)
    vignette(out, dst, pw)
    if sp.get('rim'):
        out = add_rim(out, fig, fm, sp, dst, s_eye)
    print(f"  {sp['pct']}: scale {scale}, eye holes {s_eye:.1f}px apart, chin rim y~{EYE_Y + (sp['mouth'] - mid[1]) * scale:.0f}")
    return out


# ---------------------------------------------------------------- compose (as thumb_c)
def thumb_c2():
    panels = [face_panel(CARVEY, PW[0])] + [mask_panel(sp, pw) for sp, pw in zip(MASK_SPECS, PW[1:])]
    im = Image.new('RGBA', (W, H), (0, 0, 0, 255)); x = 0
    for p, pw in zip(panels, PW):
        im.paste(p, (x, 0)); x += pw
    darken(im, vgrad(352, 567, 0, 225))                                       # floor for the numbers
    d = ImageDraw.Draw(im)
    for k in (1, 2):                                                          # thin black gutters
        gx = sum(PW[:k]); d.rectangle([gx - 3, 0, gx + 3, H], fill=(0, 0, 0, 255))
    x = 0
    for (pct, col), pw in zip([(CARVEY['pct'], CARVEY['col'])] + [(s['pct'], s['col']) for s in MASK_SPECS], PW):
        shadow_text(im, (x + pw // 2, H - 178), pct, f(182), col, stroke=8); x += pw   # '10%' clears the duration badge (y621+)
    im.convert('RGB').save(os.path.join(OUT, NAME), quality=93)
    print('wrote', os.path.join(OUT, NAME))


if __name__ == '__main__':
    thumb_c2()
