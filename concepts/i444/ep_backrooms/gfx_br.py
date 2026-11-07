# Backrooms special overlay graphics (1920x1080 RGBA PNGs), YouTube Sans Black, white with a black stroke and a soft shadow.
# No boxes, pills, bars or gauges: plain big text, with a soft blurred darkening behind it where the film's yellow walls would
# eat the white (the same idea as the thumbnails' shadow under the numbers).
#   cap     cold-open caption, centre, f(170) (EP01-EP04 word_tag look, shrunk to 1760 px or split over two lines)
#   corner  top-right SURVIVAL RATE + the number in its colour (green >= 70, yellow >= 40, red below)
#   drop    animated: the new number lands big in the centre with the stamp, then flies into the corner (PNG frames)
#   choice  TURN BACK / KEEP GOING, state 0 = both white, state 1 = TURN BACK dimmed, KEEP GOING red and bigger
#   place   stage name, top-left
#   sub     film-line subtitle, bottom centre
#   date    tape date, centre (JUNE 19, 1990)
#   final   1 OF 5 (the 1 in red)
import os, sys, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(HERE, '..', 'ep01', 'YouTubeSans-Black.otf')
W, H = 1920, 1080
WHITE = (245, 242, 236, 255); DIM = (170, 168, 162, 255)
GREEN = (70, 215, 95, 255); YELLOW = (250, 200, 40, 255); RED = (235, 30, 38, 255)
def f(sz): return ImageFont.truetype(FONT, sz)
def col(p):  # v3: a word value (SURVIVED / TRAPPED..?) is green for SURVIVED, red otherwise
    if isinstance(p, str): return GREEN if p.upper().startswith('SURVIV') else RED
    return GREEN if p >= 70 else YELLOW if p >= 40 else RED
def pstr(p): return p if isinstance(p, str) else f'{p}%'
def num_size(p, base, maxw):  # the number's font size, shrunk so a word value fits the width
    s = pstr(p); sz = base
    while f(sz).getlength(s) > maxw and sz > 40: sz -= 2
    return sz
def blank(): return Image.new('RGBA', (W, H), (0, 0, 0, 0))
def glow(im, box, alpha=135, blur=70):
    """soft dark ellipse behind text (no hard edge anywhere), box = (x0, y0, x1, y1)"""
    m = Image.new('L', (W, H), 0); ImageDraw.Draw(m).ellipse(box, fill=alpha); m = m.filter(ImageFilter.GaussianBlur(blur))
    im.alpha_composite(Image.composite(Image.new('RGBA', (W, H), (0, 0, 0, 255)), Image.new('RGBA', (W, H), (0, 0, 0, 0)), m))
def text(im, xy, txt, font, fill, anchor='mm', stroke=5, blur=10, alpha=200):
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(sh)
    d.text((xy[0] + 4, xy[1] + 6), txt, font=font, fill=(0, 0, 0, alpha), anchor=anchor, stroke_width=stroke + 6, stroke_fill=(0, 0, 0, alpha))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(blur)))
    ImageDraw.Draw(im).text(xy, txt, font=font, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=(0, 0, 0, 255))
def cap(word, out):
    im = blank(); w = word.upper(); sz = 170
    while f(sz).getlength(w) > 1760 and sz > 120: sz -= 5
    if f(sz).getlength(w) <= 1760: text(im, (960, 540), w, f(sz), WHITE)
    else:
        ws = w.split(); k = min(range(1, len(ws)), key=lambda i: abs(len(' '.join(ws[:i])) - len(' '.join(ws[i:]))))
        text(im, (960, 455), ' '.join(ws[:k]), f(170), WHITE); text(im, (960, 635), ' '.join(ws[k:]), f(170), WHITE)
    im.save(out)
# corner layout (the drop animation ends exactly on it)
CX, CY_LABEL, CY_NUM, C_LABEL, C_NUM = 1856, 50, 218, 48, 132
def corner_img(p, label_alpha=1.0, num=True):
    im = blank(); glow(im, (1440, -60, 1990, 330))
    if label_alpha > 0:
        lab = blank(); text(lab, (CX, CY_LABEL), 'SURVIVAL RATE', f(C_LABEL), WHITE, anchor='ra', stroke=3, blur=6, alpha=170)
        if label_alpha < 1: lab.putalpha(lab.getchannel('A').point(lambda v: int(v * label_alpha)))
        im.alpha_composite(lab)
    if num: text(im, (CX, CY_NUM), pstr(p), f(num_size(p, C_NUM, 470)), col(p), anchor='rs', stroke=5, blur=8)
    return im
def corner(p, out): corner_img(p).save(out)
def ease(x): x = min(1, max(0, x)); return x * x * (3 - 2 * x)
DROP_Y = 790   # v3 (owner 11/7): the big number lands in the lower third, off the faces
def drop(out_dir, p, dur, fps=30, hold=1.0, prev=None):
    """big number punches in at the centre (0.14 s), holds, then flies into the corner (0.38 s) and the label fades in;
    returns (n_frames, 0, 0); the frames after the move repeat the finished corner"""
    os.makedirs(out_dir, exist_ok=True)
    s = pstr(p); BIG = num_size(p, 330, 1300)
    spr = Image.new('RGBA', (1400, 520), (0, 0, 0, 0)); text(spr, (700, 260), s, f(BIG), col(p), stroke=10, blur=14, alpha=210)
    bb = spr.getchannel('A').point(lambda v: 255 if v > 200 else 0).getbbox()   # the glyphs (shadow excluded)
    gx0, gy0, gx1, gy1 = bb
    # corner glyph box for the same string at C_NUM: right edge CX, baseline CY_NUM
    fc = f(num_size(p, C_NUM, 470)); cb = fc.getbbox(s, anchor='rs', stroke_width=5)
    k_end = (cb[2] - cb[0]) / (gx1 - gx0)
    end_x1, end_y1 = CX + cb[2], CY_NUM + cb[3]
    n = max(1, round(dur * fps)); t_in, t_mv = 0.14, 0.38
    for i in range(n):
        t = i / fps; im = corner_img(prev) if prev is not None else blank()   # v3: the old value stays in the corner until the new one lands
        if t >= hold + t_mv:
            im = corner_img(p)
        else:
            if t < t_in: k = 1.35 - 0.35 * ease(t / t_in); a = ease(t / t_in); cx, cy, kk = 960, DROP_Y, k
            elif t < hold: a = 1; cx, cy, kk = 960, DROP_Y, 1.0
            else:
                u = ease((t - hold) / t_mv); a = 1
                # glyph box centre moves from the screen centre to the corner glyph box centre
                ex = end_x1 - (gx1 - gx0) * k_end / 2; ey = end_y1 - (gy1 - gy0) * k_end / 2
                cx, cy, kk = 960 + (ex - 960) * u, DROP_Y + (ey - DROP_Y) * u, 1 + (k_end - 1) * u
                im = corner_img(p, label_alpha=1.0, num=False)   # v3: the label never fades; only the number swaps
            sw, sh = max(1, int(spr.width * kk)), max(1, int(spr.height * kk))
            sp = spr.resize((sw, sh), Image.LANCZOS)
            if a < 1: sp.putalpha(sp.getchannel('A').point(lambda v: int(v * a)))
            # place so that the glyph box centre lands on (cx, cy)
            gcx, gcy = (gx0 + gx1) / 2 * kk, (gy0 + gy1) / 2 * kk
            _paste(im, sp, cx - gcx, cy - gcy)
        im.save(os.path.join(out_dir, f'{i + 1:04d}.png'))
    return n, 0, 0
def _paste(im, sp, x, y):
    x, y = int(round(x)), int(round(y)); l = Image.new('RGBA', (W, H), (0, 0, 0, 0)); l.paste(sp, (x, y), sp); im.alpha_composite(l)
def choice(state, out):
    im = blank(); glow(im, (260, 360, 860, 720), 120); glow(im, (1060, 360, 1660, 720), 120)
    if state == 0:
        text(im, (560, 540), 'TURN BACK', f(118), WHITE, stroke=6); text(im, (1360, 540), 'KEEP GOING', f(118), WHITE, stroke=6)
    else:
        text(im, (560, 540), 'TURN BACK', f(104), DIM, stroke=5, alpha=120); text(im, (1360, 540), 'KEEP GOING', f(140), RED, stroke=7)
    im.save(out)
def place(name, out):
    im = blank(); fn = f(84); w = fn.getlength(name.upper())
    glow(im, (-120, -80, int(w) + 260, 250), 125)
    text(im, (72, 46), name.upper(), fn, WHITE, anchor='la', stroke=5, blur=8)
    im.save(out)
def sub(line, out):
    im = blank(); fn = f(72)
    while fn.getlength(line) > 1700: fn = f(fn.size - 4)
    text(im, (960, 1000), line, fn, WHITE, anchor='ms', stroke=5, blur=8, alpha=220)
    im.save(out)
def date(lines, out):
    """lines: ['JUNE 19, 1990'] or ['JUNE 29, 1990', '10 DAYS LATER']; a line starting with '!' is red"""
    im = blank(); big = 150; y = 540 - (len(lines) - 1) * big * 0.55
    glow(im, (360, int(y - 190), 1560, int(y + big * 1.1 * (len(lines) - 1) + 190)), 120)
    for ln in lines:
        text(im, (960, int(y)), ln.lstrip('!'), f(big), RED if ln.startswith('!') else WHITE, stroke=6); y += big * 1.1
    im.save(out)
def final(out):
    im = blank(); glow(im, (330, 300, 1590, 780), 140)
    fn = f(300); a, b = '1 ', 'OF 5'; wa, wb = fn.getlength(a), fn.getlength(b); x0 = 960 - (wa + wb) / 2
    text(im, (x0, 540), a, fn, RED, anchor='lm', stroke=10, blur=14); text(im, (x0 + wa, 540), b, fn, WHITE, anchor='lm', stroke=10, blur=14)
    im.save(out)
if __name__ == '__main__':   # style test: python gfx_br.py <out_dir>
    o = sys.argv[1]; os.makedirs(o, exist_ok=True)
    cap('Five people', f'{o}/cap.png'); corner(70, f'{o}/corner70.png'); corner(40, f'{o}/corner40.png'); corner(5, f'{o}/corner5.png')
    choice(0, f'{o}/choice0.png'); choice(1, f'{o}/choice1.png'); place('The Laundry Room', f'{o}/place.png')
    sub("There's someone down there!", f'{o}/sub.png'); date(['JUNE 19, 1990'], f'{o}/date.png'); final(f'{o}/final.png')
    print(drop(f'{o}/drop', 40, 1.7))
