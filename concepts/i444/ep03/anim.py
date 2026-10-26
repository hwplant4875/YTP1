# EP03 v2 animated overlays, rendered as PNG frame sequences (30 fps) that render_v2.py overlays on the edit:
#  stat_card     right-hand panel: tile + name, 4 stat bars filling one by one, then the survival % stamps as it is spoken
#  thermo_beat   full-screen survival thermometer: the blood level drains to the new %, a Ghostface mask stabs in at that mark
#  thermo_final  outro: all 16 masks pinned in ranking order, two highlights, then dims under the closing titles
#  board_beat    TierMaker-style board (user 10/26: the TierMaker template look, no coloured rings, no numbers on tiles, names kept):
#                the new face flies in and slams into its tier row
#  board_final   outro: the full board fills up in ranking order, two highlights, then dims
# Each function writes <out>/%04d.png and returns (frame_count, x, y); frames stop at the last change (the renderer holds it).
import os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(HERE, '..', 'ep01', 'YouTubeSans-Black.otf')
W, H = 1920, 1080
TIERS = [("YOU'RE DEAD", (214, 32, 39), 25), ('PROBABLY DEAD', (240, 112, 24), 40), ('COIN FLIP', (246, 196, 30), 55),
         ("YOU'LL LIVE", (60, 190, 90), 75), ('EASY', (52, 140, 235), 101)]
# TierMaker template: pastel row labels top -> bottom, near-black board, black row lines, plain Arial-like type in dark ink
TM_COL = [(255, 127, 127), (255, 191, 127), (255, 223, 127), (255, 255, 127), (191, 255, 127), (127, 255, 127)]
TM_BOARD, TM_LINE, TM_INK, TM_PAGE = (26, 26, 23), (0, 0, 0), (24, 24, 22), (10, 10, 10)
LETTERS = None                                   # [(letter, phrase), ...] once set_tiers() runs
def set_tiers(rows):
    """rows = [[letter, phrase, max_pct], ...] top (deadliest) -> bottom; switches every graphic to the TierMaker colours"""
    global TIERS, LETTERS
    TIERS = [((l + '  ' + ph.upper()) if ph else l, TM_COL[i], mx) for i, (l, ph, mx) in enumerate(rows)]
    LETTERS = [(l, ph) for l, ph, mx in rows]
WHITE, BONE, RED = (245, 242, 236), (200, 192, 178), (225, 30, 38)
_SANS = {}
def sans(sz, bold=False):
    """Arial (Windows laptop) or its metric twin Liberation Sans (server)"""
    k = (sz, bold)
    if k not in _SANS:
        for p in ([r'C:\Windows\Fonts\arialbd.ttf', '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'] if bold else
                  [r'C:\Windows\Fonts\arial.ttf', '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf']):
            if os.path.exists(p): _SANS[k] = ImageFont.truetype(p, sz); break
        else: _SANS[k] = ImageFont.truetype(os.path.join(HERE, '..', 'ep01', 'YouTubeSans-Black.otf'), sz)
    return _SANS[k]
_F = {}
def f(sz):
    if sz not in _F: _F[sz] = ImageFont.truetype(FONT, sz)
    return _F[sz]
def tier(p): return next(i for i, t in enumerate(TIERS) if p <= t[2])
def col(p): return TIERS[tier(p)][1]
def ease(x): x = min(1.0, max(0.0, x)); return 1 - (1 - x) ** 3
def text(d, xy, s, sz, fill, anchor='mm', stroke=0, sf=(0, 0, 0)):
    d.text(xy, s, font=f(sz), fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=sf)
_IMG = {}
def img(p):
    if p not in _IMG: _IMG[p] = Image.open(p).convert('RGBA')
    return _IMG[p]
def tile(p, size, ring=None, flash=0.0):
    t = img(p).resize((size, size), Image.LANCZOS)
    if flash > 0: t = Image.blend(t, Image.new('RGBA', t.size, (255, 255, 255, 255)), min(1, flash))
    if ring:
        b = max(4, size // 28); o = Image.new('RGBA', (size + 2 * b, size + 2 * b), ring + (255,)); o.paste(t, (b, b)); t = o
    return t
MASK = os.path.join(HERE, 'graphics', 'mask_icon.png')
_M = {}
def mask(h, rot=0):
    k = (h, round(rot))
    if k not in _M:
        m = img(MASK); m = m.resize((max(1, m.size[0] * h // m.size[1]), h), Image.LANCZOS)
        _M[k] = m.rotate(rot, Image.BICUBIC, expand=True) if rot else m
    return _M[k]
def with_shadow(base, layer, xy, off=(0, 8), blur=8, alpha=190):
    a = layer.getchannel('A').filter(ImageFilter.GaussianBlur(blur)).point(lambda v: v * alpha // 255)
    s = Image.new('RGBA', layer.size, (0, 0, 0, 255)); s.putalpha(a)
    base.alpha_composite(s, (int(xy[0] + off[0]), int(xy[1] + off[1]))); base.alpha_composite(layer, (int(xy[0]), int(xy[1])))
def save(im, out, i): im.save(os.path.join(out, f'{i:04d}.png'), compress_level=1)

# ------------------------------------------------------------------ stat card
PX, PY, PW, PH = 1030, 150, 840, 800        # panel box in the frame (keeps x >= 1000, y 140..980)
def stat_card(out, name, tile_png, stats, pct, dur, t_pct, fps=30, reveal=None, film=''):
    os.makedirs(out, exist_ok=True)
    num = isinstance(pct, (int, float)); c = col(pct) if num else RED
    keys = list(stats)
    # bar start times: given (rules demo) or staggered, squeezed so all four are full before the % lands
    if reveal: starts = list(reveal)
    else:
        last = max(0.9, min(1.7, t_pct - 0.55)); starts = [0.32 + i * (last - 0.32) / 3 for i in range(4)]
    FILL = 0.36
    end = max(t_pct + 0.75, starts[-1] + FILL + 0.1)
    n = int(math.ceil(min(dur, end) * fps)) + 1
    static = Image.new('RGBA', (PW, PH), (0, 0, 0, 0)); d = ImageDraw.Draw(static)
    d.rounded_rectangle([0, 0, PW - 1, PH - 1], 26, fill=(10, 9, 12, 215), outline=(70, 66, 74, 255), width=3)
    d.rounded_rectangle([0, 0, PW - 1, 12], 6, fill=c + (255,))
    t = tile(tile_png, 200, ring=None if LETTERS else c); static.alpha_composite(t, (34, 40))
    nm = name.upper(); sz = 62
    while d.textlength(nm, font=f(sz)) > PW - 300 and sz > 34: sz -= 2
    if d.textlength(nm, font=f(sz)) > PW - 300 and ' ' in nm:      # two lines
        a, b = nm.split(' ', 1); text(d, (276, 100), a, 56, WHITE, 'ls'); text(d, (276, 166), b, 56, WHITE, 'ls')
    else: text(d, (276, 130), nm, sz, WHITE, 'ls')
    if film: text(d, (278, 210), film.upper(), 30, BONE, 'ls')
    BX, BW, BH, Y0, DY = 40, PW - 80, 30, 300, 86
    for i, k in enumerate(keys):
        y = Y0 + i * DY
        text(d, (BX, y), k, 32, BONE, 'ls')
        d.rounded_rectangle([BX, y + 14, BX + BW, y + 14 + BH], 15, fill=(40, 38, 44, 255))
    d.line([(BX, 630), (BX + BW, 630)], fill=(70, 66, 74, 255), width=2)
    text(d, (BX, 694), 'SURVIVAL RATE', 40, WHITE, 'ls')
    for i in range(n):
        tt = i / fps
        fr = Image.new('RGBA', (PW, PH), (0, 0, 0, 0)); fr.alpha_composite(static); d = ImageDraw.Draw(fr)
        for j, k in enumerate(keys):
            y = Y0 + j * DY; v = stats[k]; e = ease((tt - starts[j]) / FILL)
            if e > 0:
                w = max(BH, BW * v / 10 * e)
                d.rounded_rectangle([BX, y + 14, BX + w, y + 14 + BH], 15, fill=(225, 30, 38, 255))
                d.rounded_rectangle([BX + 4, y + 17, BX + w - 4, y + 22], 3, fill=(255, 120, 120, 120))
            shown = int(round(v * e)) if e > 0 else 0
            text(d, (BX + BW, y), f'{shown}/10' if e > 0 else '', 40, WHITE, 'rs')
        if tt >= t_pct - 0.02:
            k2 = (tt - t_pct) / 0.2
            if num:
                val = int(round(pct * ease(k2))) if k2 < 1 else pct; s = f'{val}%'
            else: s = '??'
            sc = 1.0 + 0.2 * (1 - ease((tt - t_pct - 0.2) / 0.16)) if k2 >= 1 else 1.2
            lay = Image.new('RGBA', (520, 230), (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
            text(dl, (500, 190), s, 160, c, 'rs', stroke=6)
            if sc != 1.0:
                lay = lay.resize((int(520 * sc), int(230 * sc)), Image.BICUBIC)
            fr.alpha_composite(lay, (int(PW - 40 - 500 * sc), int(772 - 190 * sc)))
            if num and tt >= t_pct + 0.36:
                a = int(255 * ease((tt - t_pct - 0.36) / 0.2)); nm2 = TIERS[tier(pct)][0]
                tl = Image.new('RGBA', (PW, PH), (0, 0, 0, 0)); dt = ImageDraw.Draw(tl)
                w2 = dt.textlength(nm2, font=f(34)) + 40
                dt.rounded_rectangle([BX, 716, BX + w2, 768], 12, fill=c + (a,))
                text(dt, (BX + 20, 754), nm2, 34, (15, 12, 12, a) if (LETTERS or tier(pct) == 2) else (255, 255, 255, a), 'ls')
                fr.alpha_composite(tl)
        # slide in: 0.28 s from +140 px with alpha
        k3 = ease(tt / 0.28)
        if k3 < 1:
            sh = Image.new('RGBA', (PW, PH), (0, 0, 0, 0)); sh.alpha_composite(fr, (int(140 * (1 - k3)), 0))
            sh.putalpha(sh.getchannel('A').point(lambda v: int(v * k3))); fr = sh
        save(fr, out, i)
    return n, PX, PY

# ------------------------------------------------------------------ survival thermometer
TX, T100, T0 = 960, 172, 958
def ypct(p): return T0 - (T0 - T100) * p / 100
def _bg():
    rng = np.random.default_rng(3)
    y, x = np.mgrid[0:H, 0:W]; r = np.hypot((x - W / 2) / W, (y - H / 2) / H)
    a = np.clip(18 - 14 * r + rng.normal(0, 3.0, (H, W)), 0, 255)
    return Image.fromarray(np.stack([a * 1.15, a * 0.9, a * 0.95], -1).clip(0, 255).astype(np.uint8)).convert('RGBA')
_BG = None
def bg():
    global _BG
    if _BG is None: _BG = _bg()
    return _BG.copy()
def _tube(im, level):
    d = ImageDraw.Draw(im); tw = 74; x0, x1 = TX - tw // 2, TX + tw // 2
    text(d, (W // 2, 50), 'GHOSTFACE SURVIVAL METER', 48, (235, 235, 235))
    lx = W // 2 - 520
    for name, c, hi in TIERS:
        d.rounded_rectangle([lx, 92, lx + 22, 114], 5, fill=c); text(d, (lx + 32, 103), name, 24, c, 'lm'); lx += 44 + int(d.textlength(name, font=f(24)))
    d.rounded_rectangle([x0 - 10, T100 - 40, x1 + 10, T0 + 30], 46, fill=(38, 36, 42), outline=(120, 120, 130), width=4)
    d.ellipse([TX - 78, T0 - 20, TX + 78, T0 + 136], fill=(38, 36, 42), outline=(120, 120, 130), width=4)
    for i, (name, c, hi) in enumerate(TIERS):
        lo = 0 if i == 0 else TIERS[i - 1][2]
        d.rectangle([x0 + 6, ypct(min(hi, 100)), x1 - 6, ypct(lo)], fill=tuple(int(v * 0.42) for v in c))
    if level is not None:
        yl = ypct(level)
        d.rectangle([x0 + 6, yl, x1 - 6, T0 + 40], fill=(178, 8, 18))
        d.ellipse([x0 + 6, yl - 9, x1 - 6, yl + 9], fill=(228, 44, 52))
    d.ellipse([TX - 62, T0 - 4, TX + 62, T0 + 120], fill=(178, 8, 18))
    d.line([(x0 + 14, T100 - 20), (x0 + 14, T0)], fill=(205, 205, 215), width=4)
    for p in range(0, 101, 10):
        y = ypct(p); d.line([(x0 - 26, y), (x0 - 8, y)], fill=(200, 200, 200), width=3)
        text(d, (x0 - 34, y), f'{p}', 26, (200, 200, 200), 'rm')
def _layout(placed):
    """callout positions for every placed killer: alternate sides in % order, pushed apart, kept in frame"""
    order = sorted(placed, key=lambda r: r['pct'])
    side = {r['key']: (-1 if i % 2 == 0 else 1) for i, r in enumerate(order)}
    pos = {}
    for s in (-1, 1):
        rows = [r for r in order if side[r['key']] == s][::-1]
        ys = [ypct(r['pct']) for r in rows]; gap = 110
        for i in range(1, len(ys)): ys[i] = max(ys[i], ys[i - 1] + gap)
        over = ys[-1] - 1022 if ys else 0
        if over > 0: ys = [y - over for y in ys]
        for i in range(len(ys) - 2, -1, -1): ys[i] = min(ys[i], ys[i + 1] - gap)
        for r, y in zip(rows, ys): pos[r['key']] = (s, y)
    return pos
def _callout(im, r, s, y, alpha=1.0, glow=0.0):
    p = r['pct']; c = col(p); py = ypct(p)
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    bx = TX + s * 420; mx = TX + s * 62
    d.line([(mx + s * 26, py), (bx - s * 30, py), (bx, y)] if abs(y - py) > 2 else [(mx + s * 26, py), (bx, y)], fill=c, width=4)
    t = tile(r['tile'], 88, ring=c, flash=glow * 0.35)
    tx = bx if s > 0 else bx - t.size[0]
    lay.alpha_composite(t, (int(tx), int(y - t.size[1] / 2)))
    nm = r['short']; ax = 'lm' if s > 0 else 'rm'; nx = bx + s * 112
    text(d, (nx, y - 18), nm, 34, WHITE, ax); text(d, (nx, y + 24), f'{p}%', 40, c, ax, stroke=3)
    if glow > 0:
        g = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dg = ImageDraw.Draw(g)
        tw = max(d.textlength(nm, font=f(34)), d.textlength(f'{p}%', font=f(40)))
        x0, x1 = (tx - 16, nx + tw + 18) if s > 0 else (nx - tw - 18, tx + t.size[0] + 16)
        dg.rounded_rectangle([x0, y - 62, x1, y + 62], 20, outline=c + (int(255 * glow),), width=6)
        lay.alpha_composite(g.filter(ImageFilter.GaussianBlur(2)))
    if alpha < 1: lay.putalpha(lay.getchannel('A').point(lambda v: int(v * alpha)))
    im.alpha_composite(lay)
def _pins(im, placed, pos, skip=None, pop=None):
    for r in sorted(placed, key=lambda r: r['pct']):
        if r['key'] == skip: continue
        s = pos[r['key']][0]; sc = 1.0
        if pop and r['key'] in pop: sc = pop[r['key']]
        if sc <= 0: continue
        m = mask(max(8, int(48 * sc)), rot=-14 * s)
        with_shadow(im, m, (TX + s * 40 - m.size[0] / 2, ypct(r['pct']) - m.size[1] * 0.55), (0, 5), 5, 200)
def thermo_beat(out, placed, new, dur=1.2, fps=30, level_from=None):
    os.makedirs(out, exist_ok=True)
    allp = placed + [new]; pos = _layout(allp)
    p = new['pct']; c = col(p); py = ypct(p)
    lf = level_from if level_from is not None else (placed[-1]['pct'] if placed else 100)
    T_HIT = 0.5
    base_cache = {}
    n = int(round(dur * fps))
    for i in range(n):
        tt = i / fps
        lvl = lf + (p - lf) * ease(tt / 0.48)
        im = bg(); _tube(im, lvl)
        co = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        for r in placed:   # dimmed history; skip the ones the new callout panel would half cover
            s_, y_ = pos[r['key']]
            if not (s_ > 0 and abs(y_ - py) < 210): _callout(co, r, s_, y_)
        co.putalpha(co.getchannel('A').point(lambda v: v * 30 // 100)); im.alpha_composite(co)
        _pins(im, placed, pos)
        # the new mask: flies in from the top right, spinning down, and stabs into the mark at T_HIT
        k = ease(tt / T_HIT)
        h = int(420 - 190 * k); rot = 34 - 24 * k
        x = TX + 14 + (720 * (1 - k)); y = py - h * 0.80 - 520 * (1 - k)
        if tt >= T_HIT:
            fl = max(0.0, 1 - (tt - T_HIT) / 0.22)
            if fl > 0:
                g = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dg = ImageDraw.Draw(g)
                for rr, a in ((170, 60), (120, 110), (70, 180)):
                    dg.ellipse([TX - rr, py - rr * 0.55, TX + rr, py + rr * 0.55], fill=(255, 255, 255, int(a * fl)))
                im.alpha_composite(g.filter(ImageFilter.GaussianBlur(14)))
        m = mask(h, rot=rot); with_shadow(im, m, (x - m.size[0] / 2, y), (0, 18), 18, 230)
        if tt >= T_HIT - 0.02:
            d = ImageDraw.Draw(im); kk = ease((tt - T_HIT) / 0.18)
            d.line([(TX + 40, py), (TX + 40 + 260 * kk, py)], fill=c, width=8)
            d.polygon([(TX + 46, py), (TX + 76, py - 14), (TX + 76, py + 14)], fill=c)
            if tt >= T_HIT + 0.04:
                k4 = ease((tt - T_HIT - 0.04) / 0.16); sc = 0.86 + 0.14 * k4
                pn = Image.new('RGBA', (1600 - 296 + 300, 320), (0, 0, 0, 0)); dp = ImageDraw.Draw(pn)
                dp.rounded_rectangle([0, 10, 594, 310], 24, fill=(8, 6, 8, 235), outline=c, width=5)
                t = tile(new['tile'], 250, ring=c); pn.alpha_composite(t, (24, 160 - t.size[1] // 2))
                text(dp, (314, 98), new['short'], 64 if len(new['short']) <= 8 else 52, WHITE, 'lm', stroke=5)
                text(dp, (314, 210), f'{p}%', 130, c, 'lm', stroke=8)
                pn = pn.crop((0, 0, 600, 320))
                if sc < 1: pn = pn.resize((int(600 * sc), int(320 * sc)), Image.BICUBIC)
                pn.putalpha(pn.getchannel('A').point(lambda v: int(v * k4)))
                im.alpha_composite(pn, (int(TX + 296 + (600 - pn.size[0]) / 2), int(py - pn.size[1] / 2)))
        # impact shake: 6 px, decays over 0.15 s
        if T_HIT <= tt < T_HIT + 0.15:
            a = 6 * (1 - (tt - T_HIT) / 0.15); dx = int(a * math.sin(tt * 90)); dy = int(a * math.cos(tt * 77))
            sh = bg(); sh.alpha_composite(im, (dx, dy)); im = sh
        if tt < 0.07:  # cut in on a short white flash
            im = Image.blend(im, Image.new('RGBA', (W, H), (255, 255, 255, 255)), 0.35 * (1 - tt / 0.07))
        save(im.convert('RGB'), out, i)
    return n, 0, 0
def thermo_final(out, placed, dur, fps=30, t_build=(0.25, 1.9), highlights=(), t_dim=None):
    os.makedirs(out, exist_ok=True)
    pos = _layout(placed); order = list(placed)              # ranking order #16 -> #1
    t0, t1 = t_build; step = (t1 - t0) / max(1, len(order))
    last = max([t1 + 0.4] + [h[0] + 0.9 for h in highlights] + ([t_dim + 0.4] if t_dim else []))
    n = int(math.ceil(min(dur, last) * fps))
    for i in range(n):
        tt = i / fps
        shown = [r for j, r in enumerate(order) if tt >= t0 + j * step]
        lvl = shown[-1]['pct'] if shown else 100
        im = bg(); _tube(im, lvl)
        pop = {}
        for j, r in enumerate(order):
            k = (tt - (t0 + j * step)) / 0.14
            pop[r['key']] = 0 if k < 0 else (1.35 - 0.35 * ease(k) if k < 1 else 1.0)
        for j, r in enumerate(order):
            if pop[r['key']] <= 0: continue
            glow = 0.0
            for th, key in highlights:
                if key == r['key'] and th <= tt < th + 1.2: glow = math.sin(math.pi * (tt - th) / 1.2)
            _callout(im, r, *pos[r['key']], alpha=min(1, pop[r['key']]), glow=glow)
        _pins(im, order, pos, pop={k: v for k, v in pop.items()})
        if t_dim is not None and tt >= t_dim:
            im = Image.blend(im, Image.new('RGBA', (W, H), (0, 0, 0, 255)), 0.55 * ease((tt - t_dim) / 0.35))
        save(im.convert('RGB'), out, i)
    return n, 0, 0

# ------------------------------------------------------------------ TierMaker-style board
LW = 300                                # label column width
def geom():
    """row pitch / square tile size (edge to edge, 2 px black row lines) / board origin for the current number of tiers"""
    nr = len(TIERS); rh = min(196, (H - 40) // nr); ts = rh - 2
    bxw = LW + 7 * ts + 2                   # 7 tile slots wide like the template
    return nr, rh, ts, (W - bxw) // 2, (H - nr * rh) // 2, bxw
def _label_cell(i, flash=0.0):
    nr, RH, TS, BX0, BY0, BXW = geom(); c = TM_COL[i]
    if flash > 0: c = tuple(int(v + (255 - v) * flash) for v in c)
    cell = Image.new('RGBA', (LW, TS), c + (255,)); d = ImageDraw.Draw(cell)
    l, ph = LETTERS[i] if LETTERS else (TIERS[i][0], '')
    if ph:
        d.text((LW / 2, TS * 0.40), l, font=sans(TS * 104 // 194), fill=TM_INK, anchor='mm')
        sz = min(38, TS * 40 // 194)
        while d.textlength(ph, font=sans(sz)) > LW - 24 and sz > 20: sz -= 1
        d.text((LW / 2, TS * 0.80), ph, font=sans(sz), fill=TM_INK, anchor='mm')
    else:
        sz = 104 if len(l) <= 2 else 34
        d.text((LW / 2, TS / 2), l, font=sans(sz), fill=TM_INK, anchor='mm')
    return cell
_FACE = {}
def face(r, size=None):
    """square face tile with the name on a dark strip at the bottom (no ring, no number)"""
    TS = geom()[2]; size = size or TS
    k = (r['tile'], r['short'], size)
    if k not in _FACE:
        t = img(r['tile']).resize((size, size), Image.LANCZOS).copy(); d = ImageDraw.Draw(t)
        sh = max(30, size * 40 // TS); d.rectangle([0, size - sh, size, size], fill=(0, 0, 0, 165))
        nm = r['short']; sz = max(14, size * 29 // TS)
        while d.textlength(nm, font=sans(sz, True)) > size - 6 and sz > 12: sz -= 1
        d.text((size / 2, size - sh / 2), nm, font=sans(sz, True), fill=(255, 255, 255), anchor='mm')
        _FACE[k] = t
    return _FACE[k]
def _row_of(p): return tier(p)
def slots(placed):
    """(x, y) of each placed key: rows by tier, left to right in reveal order"""
    nr, RH, TS, BX0, BY0, BXW = geom(); cnt = [0] * nr; pos = {}
    for r in placed:
        i = _row_of(r['pct']); pos[r['key']] = (BX0 + LW + 2 + cnt[i] * TS, BY0 + i * RH + 1); cnt[i] += 1
    return pos
def board_bg(flash_row=None, flash=0.0):
    nr, RH, TS, BX0, BY0, BXW = geom()
    im = Image.new('RGBA', (W, H), TM_PAGE + (255,)); d = ImageDraw.Draw(im)
    d.rectangle([BX0, BY0, BX0 + BXW, BY0 + nr * RH], fill=TM_LINE)
    for i in range(nr):
        y = BY0 + i * RH + 1
        d.rectangle([BX0 + LW + 2, y, BX0 + BXW - 1, y + TS - 1], fill=TM_BOARD)
        im.alpha_composite(_label_cell(i, flash if i == flash_row else 0.0), (BX0 + 1, y))
    return im
def board_beat(out, placed, new, dur=1.2, fps=30):
    os.makedirs(out, exist_ok=True); TS = geom()[2]
    pos = slots(placed + [new]); row = _row_of(new['pct']); tx, ty = pos[new['key']]
    base = board_bg()
    for r in placed: base.alpha_composite(face(r), pos[r['key']])
    T_HIT, T_IN = 0.5, 0.1
    n = int(round(min(dur, T_HIT + 0.45) * fps)) + 1
    sx, sy, s0 = 1340, 470, 2.3                       # starts big at the right, then slams down into its slot
    for i in range(n):
        tt = i / fps
        if tt < T_HIT:
            im = base.copy()
            k = max(0.0, (tt - T_IN) / (T_HIT - T_IN)); k = k * k        # accelerate into the hit
            sc = s0 + (1 - s0) * k; sz = int(TS * sc)
            cx = sx + (tx + TS / 2 - sx) * k; cy = sy + (ty + TS / 2 - sy) * k
            t = face(new, sz).rotate(-8 * (1 - k), Image.BICUBIC, expand=True)
            if tt < T_IN: t.putalpha(t.getchannel('A').point(lambda v: int(v * tt / T_IN)))
            with_shadow(im, t, (cx - t.size[0] / 2, cy - t.size[1] / 2), (0, int(10 + 30 * (1 - k))), 14, 200)
        else:
            u = tt - T_HIT
            im = board_bg(row, 0.55 * max(0.0, 1 - u / 0.3))
            for r in placed: im.alpha_composite(face(r), pos[r['key']])
            sc = 1 + 0.12 * max(0.0, 1 - u / 0.15); sz = int(TS * sc)
            t = face(new, sz)
            fl = max(0.0, 1 - u / 0.2)
            if fl > 0: t = Image.blend(t, Image.new('RGBA', t.size, (255, 255, 255, 255)), 0.75 * fl)
            im.alpha_composite(t, (int(tx + TS / 2 - sz / 2), int(ty + TS / 2 - sz / 2)))
            if u < 0.12:                                  # impact shake
                a = 5 * (1 - u / 0.12); sh = Image.new('RGBA', (W, H), TM_PAGE + (255,))
                sh.alpha_composite(im, (int(a * math.sin(tt * 90)), int(a * math.cos(tt * 77)))); im = sh
        if tt < 0.07: im = Image.blend(im, Image.new('RGBA', (W, H), (255, 255, 255, 255)), 0.35 * (1 - tt / 0.07))
        save(im.convert('RGB'), out, i)
    return n, 0, 0
def board_final(out, placed, dur, fps=30, t_build=(0.25, 1.9), highlights=(), t_dim=None):
    os.makedirs(out, exist_ok=True); TS = geom()[2]
    pos = slots(placed); t0, t1 = t_build; step = (t1 - t0) / max(1, len(placed))
    last = max([t1 + 0.4] + [h[0] + 1.3 for h in highlights] + ([t_dim + 0.4] if t_dim else []))
    n = int(math.ceil(min(dur, last) * fps)); base = board_bg()
    for i in range(n):
        tt = i / fps; im = base.copy(); top = []
        hl = {k: math.sin(math.pi * (tt - th) / 1.2) for th, k in highlights if th <= tt < th + 1.2}
        dim = max(hl.values()) if hl else 0.0
        for j, r in enumerate(placed):
            k = (tt - (t0 + j * step)) / 0.14
            if k < 0: continue
            sc = 1.35 - 0.35 * ease(k) if k < 1 else 1.0
            if r['key'] in hl: top.append((r, 1 + 0.28 * hl[r['key']])); continue
            t = face(r, int(TS * sc))
            if dim > 0: t = Image.blend(t, Image.new('RGBA', t.size, (0, 0, 0, 255)), 0.5 * dim)
            x, y = pos[r['key']]; im.alpha_composite(t, (int(x + TS / 2 - t.size[0] / 2), int(y + TS / 2 - t.size[1] / 2)))
        for r, sc in top:                                 # highlighted face grows above its neighbours
            t = face(r, int(TS * sc)); x, y = pos[r['key']]
            x = min(max(x + TS / 2 - t.size[0] / 2, 0), W - t.size[0]); y = min(max(y + TS / 2 - t.size[1] / 2, 0), H - t.size[1])
            with_shadow(im, t, (x, y), (0, 10), 16, 220)
        if t_dim is not None and tt >= t_dim:
            im = Image.blend(im, Image.new('RGBA', (W, H), (0, 0, 0, 255)), 0.55 * ease((tt - t_dim) / 0.35))
        save(im.convert('RGB'), out, i)
    return n, 0, 0
