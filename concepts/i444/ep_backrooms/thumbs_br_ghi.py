# Backrooms thumbnails G/H/I (owner 11/8: "싹다 별로다" for A-F; "노력이 들어갔다는걸 보여주고 싶어"): layered composites from the owner's film
# file (never committed): rembg cutouts with feathered edges, a matched light wrap / glow, film grain on top so the layers sit together,
# the film's natural colour (light contrast lift only), one big plain-English line at the bottom centre clear of the duration badge.
# step 1: python thumbs_br_ghi.py cut <film> <work_dir>        -> frames + cutouts (inspect them)
# step 2: python thumbs_br_ghi.py build <film> <work_dir> <out_dir>
import os, sys, subprocess, io, random
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageChops
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from gfx_br import f
MODE, FILM, WD = sys.argv[1], sys.argv[2], sys.argv[3]; os.makedirs(WD, exist_ok=True)
W, H = 1280, 720
FR = {  # film times
    'corridor': 1749.30, 'rooms': 1744.75, 'room_wide': 1790.00,
    'cap_store': 5571.85, 'cap_full': 5567.20, 'mary_run': 5312.00, 'mary_full': 5310.30,
    'kat_bobby': 3141.65, 'hazmat': 5717.00, 'clark_walk': 1790.00, 'store_wall': 1514.20, 'clark_face': 1566.50}
def frame(t):
    png = subprocess.check_output(['ffmpeg', '-v', 'error', '-ss', str(t), '-i', FILM, '-frames:v', '1', '-f', 'image2pipe', '-vcodec', 'png', '-'])
    return Image.open(io.BytesIO(png)).convert('RGB')
if MODE == 'cut':
    from rembg import remove, new_session
    s = new_session('birefnet-portrait')   # isnet-general-use lost Captain Clark's yellow costume against the yellow store
    for k, t in FR.items():
        im = frame(t)
        if k == 'cap_store':   # seeking this HEVC file lands a few frames off here: use the frame taken from a 12-fps run from 5571.0 (frame 12)
            seq = os.path.join(WD, 'capseq', 'f12.png')
            if os.path.exists(seq): im = Image.open(seq).convert('RGB')
        if k == 'hazmat': im = im.crop((0, 380, 520, im.height))   # the small yellow hazmat man, full body, at the left
        im.save(os.path.join(WD, f'{k}.png'))
        if k not in ('corridor', 'rooms', 'room_wide', 'store_wall'):
            remove(im, session=s, post_process_mask=True).save(os.path.join(WD, f'{k}_cut.png'))
        print(k)
    sys.exit()
OD = sys.argv[4]
def load(k): return Image.open(os.path.join(WD, k + '.png')).convert('RGBA')
def fill(im, cx=0.5, cy=0.5, zoom=1.0):
    sw, sh = im.size; cw = min(sw, sh * 16 / 9) / zoom; ch = cw * 9 / 16
    x0 = min(max(0, cx * sw - cw / 2), sw - cw); y0 = min(max(0, cy * sh - ch / 2), sh - ch)
    return im.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((W, H), Image.LANCZOS)
def lift(im, con=1.08, bri=1.03):
    m = im.convert('RGB'); m = ImageEnhance.Contrast(m).enhance(con); return ImageEnhance.Brightness(m).enhance(bri)
def fill_holes(a):   # rembg sometimes leaves holes inside a body (a door knob, a belt); fill only fully enclosed holes
    from scipy.ndimage import binary_fill_holes, label
    m = np.asarray(a) > 128; holes = binary_fill_holes(m) & ~m; lab, n = label(holes)
    arr = np.asarray(a).copy()
    for i in range(1, n + 1):   # only small holes (a real gap between an arm and the body stays open)
        r = lab == i
        if r.sum() < 0.002 * m.size: arr[r] = 255
    return Image.fromarray(arr)
def cutout(k, box=None, feather=2.0, grow=0):
    c = load(k + '_cut')
    if box: c = c.crop(box)
    a = fill_holes(c.getchannel('A'))
    if grow < 0: a = a.filter(ImageFilter.MinFilter(1 - 2 * grow if (1 - 2 * grow) % 2 else 3))
    a = a.filter(ImageFilter.GaussianBlur(feather)); c.putalpha(a); return c.crop(c.getbbox())
def place(base, c, x, y, h, light=1.0, warm=0.0, wrap=None):
    """paste cutout c with its bottom-centre at (x, y), scaled to height h; light = brightness match, warm = yellow tint (Backrooms
    light), wrap = (r, g, b) light-wrap colour bleeding around the edge"""
    k = h / c.height; c = c.resize((max(1, int(c.width * k)), int(h)), Image.LANCZOS)
    rgb = ImageEnhance.Brightness(c.convert('RGB')).enhance(light)
    if warm:
        r, g, b = rgb.split(); rgb = Image.merge('RGB', (r.point(lambda v: min(255, int(v * (1 + warm * 0.5)))),
                                                          g.point(lambda v: min(255, int(v * (1 + warm * 0.4)))), b.point(lambda v: int(v * (1 - warm)))))
    c2 = rgb.convert('RGBA'); c2.putalpha(c.getchannel('A'))
    px, py = int(x - c2.width / 2), int(y - c2.height)
    if wrap:
        edge = ImageChops.subtract(c.getchannel('A'), c.getchannel('A').filter(ImageFilter.MinFilter(9))).filter(ImageFilter.GaussianBlur(6))
        wl = Image.new('RGBA', c2.size, wrap + (0,)); wl.putalpha(edge.point(lambda v: int(v * 0.55))); c2.alpha_composite(wl)
    base.alpha_composite(c2, (px, py)); return base
def shadow(base, x, y, w, alpha=120):
    m = Image.new('L', (W, H), 0); ImageDraw.Draw(m).ellipse((x - w / 2, y - w * 0.07, x + w / 2, y + w * 0.07), fill=alpha)
    base.alpha_composite(Image.merge('RGBA', [Image.new('L', (W, H), 0)] * 3 + [m.filter(ImageFilter.GaussianBlur(14))]))
def glow(base, box, col, alpha=150, blur=60):
    m = Image.new('L', (W, H), 0); ImageDraw.Draw(m).ellipse(box, fill=alpha)
    g = Image.new('RGBA', (W, H), col + (0,)); g.putalpha(m.filter(ImageFilter.GaussianBlur(blur))); base.alpha_composite(g)
def grain(base, amt=7, seed=3):
    rnd = np.random.default_rng(seed); n = rnd.normal(0, amt, (H, W, 1)).repeat(3, 2)
    a = np.asarray(base.convert('RGB')).astype(np.float32) + n; return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA')
def vignette(base, s=0.35):
    m = Image.new('L', (W, H), 0); ImageDraw.Draw(m).ellipse((-W * 0.2, -H * 0.25, W * 1.2, H * 1.25), fill=255)
    m = m.filter(ImageFilter.GaussianBlur(150)); dark = ImageEnhance.Brightness(base.convert('RGB')).enhance(1 - s).convert('RGBA')
    return Image.composite(base, dark, m)
def bottom_text(base, s, sz=150, col=(255, 255, 255)):
    fnt = f(sz)
    while fnt.getlength(s) > 1020: sz -= 4; fnt = f(sz)
    g = Image.new('L', (W, H), 0); d = ImageDraw.Draw(g)
    for y in range(H): d.line([(0, y), (W, y)], fill=int(max(0, min(200, (y - H * 0.55) / (H * 0.45) * 220))))
    base.alpha_composite(Image.merge('RGBA', [Image.new('L', (W, H), 0)] * 3 + [g]))
    y = H - 58; sh = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).text((W / 2 - 40 + 7, y + 10), s, font=fnt, fill=(0, 0, 0, 230), anchor='ms', stroke_width=20, stroke_fill=(0, 0, 0, 230))
    base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
    ImageDraw.Draw(base).text((W / 2 - 40, y), s, font=fnt, fill=col + (255,), anchor='ms', stroke_width=12, stroke_fill=(0, 0, 0, 255))
    return base
# ---- G: Captain Clark huge behind an endless yellow room, tiny Mary running toward us ----
g = lift(fill(load('corridor'), 0.5, 0.55, 1.05)).convert('RGBA')
glow(g, (300, -80, 980, 300), (255, 245, 200), 120, 90)                       # the fluorescent ceiling
cap = cutout('cap_store'); g = place(g, cap, 800, 735, 700, light=0.9, warm=0.08, wrap=(255, 240, 190))
dark = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(dark).rectangle((0, 0, W, H), fill=(0, 0, 0, 30)); g.alpha_composite(dark)
mary = cutout('mary_full'); shadow(g, 360, 592, 110); g = place(g, mary, 360, 596, 230, light=1.05, warm=0.06, wrap=(255, 240, 190))
g = bottom_text(vignette(grain(g, 6), 0.3), '2% SURVIVE', 150)
g.convert('RGB').save(os.path.join(OD, 'backrooms_thumb_g.jpg'), quality=95)
# ---- H: the dark store wall torn open, the yellow Backrooms glowing through the tear, Clark in the dark looking in ----
wall = lift(fill(load('store_wall'), 0.5, 0.5, 1.0), 1.1, 1.25).convert('RGBA')
inside = lift(fill(load('rooms'), 0.5, 0.5, 1.15), 1.05, 1.1).convert('RGBA')
rnd = random.Random(7); pts_l, pts_r = [], []
for i in range(13):
    y = -40 + i * 66; c = 690 + 80 * np.sin(i * 0.9); wdt = 170 + 70 * np.sin(i * 1.7 + 1)
    pts_l.append((c - wdt / 2 + rnd.uniform(-28, 28), y)); pts_r.append((c + wdt / 2 + rnd.uniform(-28, 28), y))
tear = Image.new('L', (W, H), 0); ImageDraw.Draw(tear).polygon(pts_l + pts_r[::-1], fill=255); tear = tear.filter(ImageFilter.GaussianBlur(2))
h = wall.copy(); glow(h, (420, -100, 980, 820), (255, 230, 150), 200, 110)       # the slit's light spilling on the wall
h.paste(inside, (0, 0), tear)
rim = ImageChops.subtract(tear.filter(ImageFilter.MaxFilter(15)), tear).filter(ImageFilter.GaussianBlur(4))
rl = Image.new('RGBA', (W, H), (255, 236, 170, 0)); rl.putalpha(rim.point(lambda v: min(255, int(v * 1.2)))); h.alpha_composite(rl)
clark = cutout('clark_face'); h = place(h, clark, 330, 760, 700, light=0.75, warm=0.18, wrap=(255, 225, 140))
h = bottom_text(vignette(grain(h, 7), 0.3), 'LEAVE IT ALONE', 140)
h.convert('RGB').save(os.path.join(OD, 'backrooms_thumb_h.jpg'), quality=95)
# ---- I: five people walking into the yellow room, four fading to static, one (Mary) solid ----
i_ = lift(fill(load('rooms'), 0.5, 0.5, 1.05)).convert('RGBA')   # an empty room (no one in the plate)
ppl = [('hazmat', None, 0.30), ('clark_walk', None, 0.40), ('kat_bobby', None, 0.48), ('mary_full', None, 1.0)]   # Naren (hazmat), Clark, Kat + Bobby fading; Mary solid
xs = [190, 400, 700, 1060]
for (k, side, op), x in zip(ppl, xs):
    c = load(k + '_cut'); bb = c.getbbox(); c = c.crop(bb)
    if side: c = c.crop((0, 0, c.width // 2, c.height)) if side == 'L' else c.crop((c.width // 2, 0, c.width, c.height))
    c = c.crop(c.getbbox()); a = fill_holes(c.getchannel('A')).filter(ImageFilter.GaussianBlur(1.5)); c.putalpha(a)
    hgt = 390 if op == 1.0 else (330 if k != 'kat_bobby' else 350)
    if op < 1.0:   # fading / breaking into static
        st = Image.fromarray(np.random.default_rng(int(x)).integers(0, 255, (c.height, c.width), dtype=np.uint8)).convert('RGB')
        mix = Image.blend(c.convert('RGB'), st, 0.35); c2 = mix.convert('RGBA')
        rows = Image.new('L', c.size, 255); dr = ImageDraw.Draw(rows)
        for yy in range(0, c.height, 6): dr.line([(0, yy), (c.width, yy)], fill=int(255 * op * 0.6))
        c2.putalpha(ImageChops.multiply(a, rows.point(lambda v: int(min(255, v * op * 1.6))))); c = c2
    shadow(i_, x, 600, 110, 90 if op == 1.0 else 40)
    i_ = place(i_, c, x, 604, hgt, light=1.0, warm=0.06, wrap=(255, 240, 190) if op == 1.0 else None)
i_ = bottom_text(vignette(grain(i_, 6), 0.28), '1 OF 5 GOT OUT', 140)
i_.convert('RGB').save(os.path.join(OD, 'backrooms_thumb_i.jpg'), quality=95)
print('ok')
