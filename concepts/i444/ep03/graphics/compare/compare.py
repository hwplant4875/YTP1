# EP03 v2 comparison mockups: survival-outcome tier board vs survival thermometer (Ghostface masks pinned at each %)
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
FONT = '/home/user/YTP1/concepts/i444/ep01/YouTubeSans-Black.otf'
def f(sz): return ImageFont.truetype(FONT, sz)
W, H = 1920, 1080
K = [('carvey', 'CARVEY', 99), ('karl', 'KARL', 75), ('mrs_loomis', 'MRS. LOOMIS', 68), ('charlie', 'CHARLIE', 60),
     ('quinn', 'QUINN', 56), ('ethan', 'ETHAN', 53), ('marco', 'MARCO', 50), ('richie', 'RICHIE', 45), ('jessica', 'JESSICA', 43),
     ('stu', 'STU', 40), ('mickey', 'MICKEY', 36), ('amber', 'AMBER', 30), ('billy', 'BILLY', 25), ('wayne', 'WAYNE', 22),
     ('jill', 'JILL', 18), ('roman', 'ROMAN', 15)]                       # ranking order #16 -> #1
TIERS = [("YOU'RE DEAD", (214, 32, 39), 25), ('PROBABLY DEAD', (240, 112, 24), 40), ('COIN FLIP', (246, 196, 30), 55),
         ("YOU'LL LIVE", (60, 190, 90), 75), ('EASY', (52, 140, 235), 101)]
def tier(p): return next(i for i, t in enumerate(TIERS) if p <= t[2])
def col(p): return TIERS[tier(p)][1]
TILE = {k: Image.open(f'tiles/{k}.png').convert('RGB') for k, _, _ in K}
MASK = Image.open('mask_icon.png')

def background():
    rng = np.random.default_rng(3)
    y, x = np.mgrid[0:H, 0:W]; r = np.hypot((x - W / 2) / W, (y - H / 2) / H)
    base = 18 - 14 * r; n = rng.normal(0, 3.0, (H, W))
    a = np.clip(base + n, 0, 255)
    im = np.stack([a * 1.15, a * 0.9, a * 0.95], -1)
    return Image.fromarray(im.clip(0, 255).astype(np.uint8)).convert('RGBA')

def text(d, xy, s, sz, fill, anchor='mm', stroke=0, sf=(0, 0, 0)):
    d.text(xy, s, font=f(sz), fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=sf)

def tile(k, size, ring=None, flash=0.0):
    t = TILE[k].resize((size, size), Image.LANCZOS).convert('RGBA')
    if flash: t = Image.blend(t, Image.new('RGBA', t.size, (255, 255, 255, 255)), flash)
    if ring:
        b = max(4, size // 28); out = Image.new('RGBA', (size + 2 * b, size + 2 * b), ring + (255,)); out.paste(t, (b, b)); t = out
    return t

def mask(h, rot=0):
    m = MASK.resize((MASK.size[0] * h // MASK.size[1], h), Image.LANCZOS)
    return m.rotate(rot, Image.BICUBIC, expand=True) if rot else m

def shadow(im, layer, off=(0, 10), blur=14, alpha=170):
    a = layer.getchannel('A').filter(ImageFilter.GaussianBlur(blur)).point(lambda v: v * alpha // 255)
    s = Image.new('RGBA', layer.size, (0, 0, 0, 255)); s.putalpha(a)
    im.alpha_composite(s, off); im.alpha_composite(layer)

# ------------------------------------------------------------------ A: survival-outcome tier board
def board(placed, new=None, out='a.png'):
    im = background(); d = ImageDraw.Draw(im)
    text(d, (W // 2, 62), 'GHOSTFACE SURVIVAL RANKING', 50, (235, 235, 235), stroke=0)
    top, rh, gap = 112, 182, 10
    rows = {i: [] for i in range(5)}
    for k, n, p in placed: rows[tier(p)].append((k, n, p))
    hot = tier(new[2]) if new else None
    for i, (name, c, hi) in enumerate(TIERS):
        y = top + i * (rh + gap)
        lo = 0 if i == 0 else TIERS[i - 1][2] + 1
        rng = f'{lo}-{min(hi, 100)}%'
        glow = (i == hot)
        d.rounded_rectangle([50, y, 410, y + rh], 14, fill=c)
        text(d, (230, y + rh // 2 - 14), name, 46 if len(name) < 12 else 40, (255, 255, 255), stroke=4, sf=(0, 0, 0))
        text(d, (230, y + rh // 2 + 38), rng, 30, (20, 20, 20))
        d.rounded_rectangle([422, y, 1870, y + rh], 14, fill=(30, 28, 32), outline=c if glow else (58, 54, 60), width=6 if glow else 2)
        for j, (k, n, p) in enumerate(rows[i]):
            x = 446 + j * 236
            t = tile(k, 132, ring=c); im.alpha_composite(t, (x, y + 10))
            text(d, (x + t.size[0] // 2, y + 166), n, 26, (240, 240, 240))
            d.rounded_rectangle([x + t.size[0] - 70, y + 8, x + t.size[0] + 8, y + 46], 10, fill=c)
            text(d, (x + t.size[0] - 31, y + 27), f'{p}%', 26, (255, 255, 255) if tier(p) != 2 else (20, 20, 20))
    if new:
        k, n, p = new; i = tier(p); y = top + i * (rh + gap); j = len(rows[i])
        sx, sy = 446 + j * 236, y + 10
        # the new tile mid-slam: big, flashing, flying in from the centre toward its slot
        dim = Image.new('RGBA', (W, H), (0, 0, 0, 120)); im.alpha_composite(dim)
        d = ImageDraw.Draw(im); d.rounded_rectangle([422, y, 1870, y + rh], 14, outline=col(p), width=6)
        big = tile(k, 330, ring=col(p), flash=0.12)
        cx, cy = 1560, 430
        streak = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ds = ImageDraw.Draw(streak)
        for s in range(14):
            o = (s - 7) * 22
            ds.line([(cx - 120, cy + o), (sx + 140, sy + 66 + o // 4)], fill=(255, 255, 255, 16), width=8)
        im.alpha_composite(streak.filter(ImageFilter.GaussianBlur(6)))
        ghost = Image.new('RGBA', (144, 144), col(p) + (90,)); im.alpha_composite(ghost, (sx - 6, sy - 6))
        shadow(im, _place(big, (cx - big.size[0] // 2, cy - big.size[1] // 2)), (0, 16), 22, 200)
        d = ImageDraw.Draw(im)
        text(d, (cx, cy + 222), 'MICKEY ALTIERI' if k == 'mickey' else n, 58, (255, 255, 255), stroke=6)
        text(d, (cx, cy + 315), f'{p}%', 120, col(p), stroke=8)
    im.convert('RGB').save(out, quality=93)

def _place(layer, xy):
    c = Image.new('RGBA', (W, H), (0, 0, 0, 0)); c.alpha_composite(layer, xy); return c

# ------------------------------------------------------------------ B: survival thermometer with masks pinned at each %
TX, T100, T0 = 960, 172, 958          # tube centre x, y at 100 %, y at 0 %
def ypct(p): return T0 - (T0 - T100) * p / 100

def tube(im, level=None):
    d = ImageDraw.Draw(im)
    tw = 74; x0, x1 = TX - tw // 2, TX + tw // 2
    # glass back
    d.rounded_rectangle([x0 - 10, T100 - 40, x1 + 10, T0 + 30], 46, fill=(38, 36, 42), outline=(120, 120, 130), width=4)
    d.ellipse([TX - 78, T0 - 20, TX + 78, T0 + 136], fill=(38, 36, 42), outline=(120, 120, 130), width=4)
    # zone colours along the scale (faint) + liquid
    for i, (name, c, hi) in enumerate(TIERS):
        lo = 0 if i == 0 else TIERS[i - 1][2]
        ya, yb = ypct(min(hi, 100)), ypct(lo)
        d.rectangle([x0 + 6, ya, x1 - 6, yb], fill=tuple(int(v * 0.5) for v in c))
    if level is not None:
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
        dl.rectangle([x0 + 6, ypct(level), x1 - 6, T0 + 40], fill=(178, 8, 18, 255))
        dl.ellipse([TX - 62, T0 - 4, TX + 62, T0 + 120], fill=(178, 8, 18, 255))
        dl.ellipse([x0 + 6, ypct(level) - 9, x1 - 6, ypct(level) + 9], fill=(225, 40, 48, 255))
        im.alpha_composite(lay)
    else:
        d.ellipse([TX - 62, T0 - 4, TX + 62, T0 + 120], fill=(150, 10, 18))
    d = ImageDraw.Draw(im)
    d.line([(x0 + 14, T100 - 20), (x0 + 14, T0)], fill=(255, 255, 255, 60), width=6)       # glass highlight
    for p in range(0, 101, 10):
        y = ypct(p); d.line([(x0 - 26, y), (x0 - 8, y)], fill=(200, 200, 200), width=3)
        text(d, (x0 - 34, y), f'{p}', 26, (200, 200, 200), anchor='rm')
    return d

def thermo(placed, new=None, level=None, out='b.png'):
    im = background(); d = ImageDraw.Draw(im)
    text(d, (W // 2, 50), 'GHOSTFACE SURVIVAL METER', 48, (235, 235, 235))
    lx = W // 2 - 520
    for name, c, hi in TIERS:
        d.rounded_rectangle([lx, 92, lx + 22, 114], 5, fill=c); text(d, (lx + 32, 103), name, 24, c, anchor='lm'); lx += 44 + int(d.textlength(name, font=f(24)))
    d = tube(im, level)
    callouts = Image.new('RGBA', (W, H), (0, 0, 0, 0)); im_main = im; im = callouts; d = ImageDraw.Draw(im)
    order = sorted(placed, key=lambda r: r[2])
    side = {k: (-1 if i % 2 == 0 else 1) for i, (k, _, _) in enumerate(order)}
    # callout positions: start at the pin height, push apart to a minimum gap, keep inside the frame
    for s in (-1, 1):
        rows = [r for r in order if side[r[0]] == s][::-1]            # top (high %) first
        ys = [ypct(p) for _, _, p in rows]; gap = 110
        for i in range(1, len(ys)): ys[i] = max(ys[i], ys[i - 1] + gap)
        over = ys[-1] - 1022 if ys else 0
        if over > 0: ys = [y - over for y in ys]
        for i in range(len(ys) - 2, -1, -1): ys[i] = min(ys[i], ys[i + 1] - gap)
        for (k, n, p), y in zip(rows, ys):
            c = col(p); py = ypct(p)
            mx = TX + s * 62
            bx = TX + s * 420 if s > 0 else TX - 420           # callout inner edge
            d.line([(mx + s * 26, py), (bx - s * 30, py), (bx, y)] if abs(y - py) > 2 else [(mx + s * 26, py), (bx, y)], fill=c, width=4)
            t = tile(k, 88, ring=c)
            if s > 0:
                im.alpha_composite(t, (bx, int(y - t.size[1] / 2)))
                text(d, (bx + 112, y - 18), n, 34, (240, 240, 240), anchor='lm')
                text(d, (bx + 112, y + 24), f'{p}%', 40, c, anchor='lm', stroke=3)
            else:
                im.alpha_composite(t, (bx - t.size[0], int(y - t.size[1] / 2)))
                text(d, (bx - 112, y - 18), n, 34, (240, 240, 240), anchor='rm')
                text(d, (bx - 112, y + 24), f'{p}%', 40, c, anchor='rm', stroke=3)
    im = im_main
    if new: callouts.putalpha(callouts.getchannel('A').point(lambda v: v * 30 // 100))
    im.alpha_composite(callouts); d = ImageDraw.Draw(im)
    # masks stuck into the gauge at the exact %, alternating sides of the tube (drawn last so they sit on the glass)
    for k, n, p in order:
        m = mask(48, rot=-14 * side[k]); x = TX + side[k] * 40 - m.size[0] // 2; y = int(ypct(p) - m.size[1] * 0.55)
        shadow(im, _place(m, (x, y)), (0, 5), 5, 200)
    if new:
        k, n, p = new; c = col(p); py = ypct(p); d = ImageDraw.Draw(im)
        # flash ring where the mask hits
        fl = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dfl = ImageDraw.Draw(fl)
        for r, a in ((150, 50), (110, 90), (70, 150)): dfl.ellipse([TX - r, py - r * 0.55, TX + r, py + r * 0.55], fill=(255, 255, 255, a))
        im.alpha_composite(fl.filter(ImageFilter.GaussianBlur(14)))
        m = mask(230, rot=10); shadow(im, _place(m, (TX - m.size[0] // 2 + 14, int(py - m.size[1] * 0.80))), (0, 18), 18, 230)
        d = ImageDraw.Draw(im)
        d.line([(TX + 40, py), (TX + 300, py)], fill=c, width=8)
        d.polygon([(TX + 46, py), (TX + 76, py - 14), (TX + 76, py + 14)], fill=c)
        pnl = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(pnl).rounded_rectangle([TX + 296, py - 150, 1890, py + 150], 24, fill=(8, 6, 8, 235), outline=c, width=5)
        im.alpha_composite(pnl); d = ImageDraw.Draw(im)
        t = tile(k, 250, ring=c); im.alpha_composite(t, (TX + 320, int(py - t.size[1] / 2)))
        text(d, (TX + 610, py - 62), n, 64, (255, 255, 255), anchor='lm', stroke=5)
        text(d, (TX + 610, py + 50), f'{p}%', 130, c, anchor='lm', stroke=8)
    im.convert('RGB').save(out, quality=93)

ALL = K
board(ALL, out='A1_tierboard_full.jpg')
upto6 = K[:10]                      # #16..#7 already ranked when Mickey (#6) lands
board(upto6, new=K[10], out='A2_tierboard_mickey.jpg')
thermo(ALL, out='B1_thermometer_full.jpg')
thermo(upto6, new=K[10], level=36, out='B2_thermometer_mickey.jpg')
print('ok')
