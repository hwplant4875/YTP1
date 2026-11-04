"""Map Lights pilot short: "Who brings the presents in your country?" (Europe).
usage: python3 -I maplights_pilot.py <ne50.geojson> <out.mp4> <music.mp3> <still_dir> [debug|stills]
"""
import json, math, sys, subprocess, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

geo_path, out_mp4, audio_path, still_dir = sys.argv[1:5]
MODE = sys.argv[5] if len(sys.argv) > 5 else ''
W, H, FPS, DUR, SS = 1080, 1920, 30, 13.5, 2
FONT = '/mnt/project-files/fonts/YOUTUBESANSBLACK.OTF'

# ---------- projection (Lambert azimuthal equal-area) ----------
lon0, lat0 = math.radians(17.0), math.radians(53.0)
def proj(lon, lat):
    l, p = math.radians(lon), math.radians(lat)
    c = math.sin(lat0) * math.sin(p) + math.cos(lat0) * math.cos(p) * math.cos(l - lon0)
    k = math.sqrt(2 / (1 + c))
    return (k * math.cos(p) * math.sin(l - lon0),
            k * (math.cos(lat0) * math.sin(p) - math.sin(lat0) * math.cos(p) * math.cos(l - lon0)))

BOX = (70, 500, 960, 1200)
core = [(-24.5, 63.5), (-9.5, 36.5), (34.5, 34.6), (46, 40.5), (31, 70.8), (-22, 66.5)]
pp = [proj(*q) for q in core]
minx, maxx = min(p[0] for p in pp), max(p[0] for p in pp)
miny, maxy = min(p[1] for p in pp), max(p[1] for p in pp)
sc = min((BOX[2] - BOX[0]) / (maxx - minx), (BOX[3] - BOX[1]) / (maxy - miny))
cx, cy = (BOX[0] + BOX[2]) / 2, (BOX[1] + BOX[3]) / 2
mx, my = (minx + maxx) / 2, (miny + maxy) / 2
def px(lon, lat):
    x, y = proj(lon, lat)
    return ((cx + (x - mx) * sc) * SS, (cy - (y - my) * sc) * SS)

GROUPS = [
    ('santa', 'Santa / Father Christmas', (255, 78, 96),
     ['GBR', 'IRL', 'FRA', 'PRT', 'ITA', 'ROU', 'MDA', 'BGR', 'LTU', 'LVA', 'EST', 'DNK', 'NOR', 'SWE',
      'FIN', 'MLT', 'SVN', 'HRV', 'POL', 'AND', 'MCO', 'SMR', 'VAT']),
    ('christkind', 'Christkind (Baby Jesus)', (255, 198, 64), ['AUT', 'CHE', 'LIE', 'CZE', 'SVK', 'HUN']),
    ('germany', 'Germany: Santa + Christkind', None, ['DEU']),
    ('nicholas', 'St. Nicholas (Dec 6)', (182, 126, 255), ['NLD', 'BEL', 'LUX', 'UKR']),
    ('frost', 'Grandfather Frost (New Year)', (104, 206, 255),
     ['RUS', 'BLR', 'SRB', 'MNE', 'MKD', 'BIH', 'ALB', 'KOS', 'TUR', 'GEO', 'ARM', 'AZE', 'KAZ']),
    ('kings', 'Three Kings (Jan 6)', (64, 216, 124), ['ESP']),
    ('basil', 'St. Basil (Jan 1)', (255, 142, 70), ['GRC', 'CYP']),
    ('yule', '13 Yule Lads', (242, 242, 236), ['ISL']),
]
T0 = [1.0 + 1.12 * i for i in range(len(GROUPS))]

# ---------- geometry ----------
feats = json.load(open(geo_path, encoding='utf-8'))['features']
def rings(geom):
    if geom['type'] == 'Polygon':
        yield geom['coordinates']
    elif geom['type'] == 'MultiPolygon':
        for poly in geom['coordinates']:
            yield poly
def in_view(poly):
    lons = [p[0] for p in poly[0]]; lats = [p[1] for p in poly[0]]
    return max(lons) > -40 and min(lons) < 75 and max(lats) > 25 and min(lats) < 82
def draw_mask(draw, geom, val=255):
    for poly in rings(geom):
        if not in_view(poly):
            continue
        ext = [px(*p) for p in poly[0]]
        if len(ext) > 2:
            draw.polygon(ext, fill=val)
        for hole in poly[1:]:
            hp = [px(*p) for p in hole]
            if len(hp) > 2:
                draw.polygon(hp, fill=0)
by_code = {}
for f in feats:
    by_code.setdefault(f['properties']['ADM0_A3'], []).append(f['geometry'])

def down(img):
    return img.resize((W, H), Image.LANCZOS)

# base land + borders
land = Image.new('L', (W * SS, H * SS), 0); dl = ImageDraw.Draw(land)
bord = Image.new('L', (W * SS, H * SS), 0); db = ImageDraw.Draw(bord)
for f in feats:
    g = f['geometry']
    draw_mask(dl, g)
    for poly in rings(g):
        if not in_view(poly):
            continue
        ext = [px(*p) for p in poly[0]]
        if len(ext) > 2:
            db.line(ext + [ext[0]], fill=255, width=3, joint='curve')
land, bord = down(land), down(bord)

# ---------- background ----------
yy = np.linspace(0, 1, H)[:, None]
top, bot = np.array([7, 14, 38]), np.array([13, 24, 58])
bg = (top + (bot - top) * yy)[:, :, None].transpose(0, 2, 1) * np.ones((1, W, 1))
gy, gx = np.mgrid[0:H, 0:W]
rad = np.exp(-(((gx - 520) / 520.0) ** 2 + ((gy - 820) / 520.0) ** 2))
bg = bg + rad[:, :, None] * np.array([14, 22, 46])
bg = Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8), 'RGB').convert('RGBA')
FADE = (np.clip((gy - 380) / 130.0, 0, 1) * np.clip((1245 - gy) / 55.0, 0, 1)).astype(np.float32)
def faded(mask_img, k=1.0):
    return Image.fromarray(np.clip(np.array(mask_img, np.float32) * FADE * k, 0, 255).astype(np.uint8), 'L')
sea_land = Image.new('RGBA', (W, H), (26, 38, 82, 0)); sea_land.putalpha(faded(land))
borders = Image.new('RGBA', (W, H), (8, 14, 34, 0)); borders.putalpha(faded(bord, 0.85))
base = Image.alpha_composite(bg, sea_land)

# ---------- group layers (cropped to bbox) ----------
def stripes(mask, c1, c2, wpx=16):
    a = np.zeros((H, W, 4), np.uint8)
    band = ((gx + gy) // wpx) % 2 == 0
    a[band] = c1 + (255,); a[~band] = c2 + (255,)
    im = Image.fromarray(a, 'RGBA'); im.putalpha(mask); return im
layers = []
for gi, (key, label, col, codes) in enumerate(GROUPS):
    m = Image.new('L', (W * SS, H * SS), 0); dm = ImageDraw.Draw(m)
    for c in codes:
        for g in by_code.get(c, []):
            draw_mask(dm, g)
    m = faded(down(m))
    if col is None:
        fill = stripes(m, GROUPS[0][2], GROUPS[1][2])
        gcol = (255, 150, 90)
    else:
        fill = Image.new('RGBA', (W, H), col + (0,)); fill.putalpha(m)
        gcol = col
    glow_a = m.filter(ImageFilter.GaussianBlur(14))
    glow = Image.new('RGBA', (W, H), gcol + (0,)); glow.putalpha(glow_a.point(lambda v: min(255, int(v * 1.6))))
    bb = glow.getbbox() or (0, 0, 1, 1)
    layers.append(dict(key=key, bb=bb, fill=np.array(fill.crop(bb)), glow=np.array(glow.crop(bb)),
                       phase=random.Random(gi).random()))

# ---------- text ----------
def font(sz): return ImageFont.truetype(FONT, sz)
def fit(text, maxw, start):
    s = start
    while font(s).getlength(text) > maxw and s > 10:
        s -= 1
    return font(s)
def text_layer(lines, centers, maxw, start, fill=(255, 255, 255), glow=(255, 214, 120), shadow=True):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    f = min((fit(t, maxw, start) for t in lines), key=lambda ff: ff.size)
    for t, (x, y) in zip(lines, centers):
        d.text((x, y), t, font=f, fill=fill + (255,), anchor='mm')
    a = im.split()[3]
    out = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    if shadow:
        sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); sh.putalpha(a.filter(ImageFilter.GaussianBlur(10)).point(lambda v: int(v * 0.8)))
        out = Image.alpha_composite(out, sh)
    if glow:
        gl = Image.new('RGBA', (W, H), glow + (0,)); gl.putalpha(a.filter(ImageFilter.GaussianBlur(18)).point(lambda v: int(v * 0.45)))
        out = Image.alpha_composite(out, gl)
    return Image.alpha_composite(out, im)
title = text_layer(['Who brings the presents', 'in your country?'], [(540, 352), (540, 440)], 930, 84)
kicker = text_layer(['EUROPE  ·  CHRISTMAS 2026'], [(540, 272)], 700, 36, fill=(255, 211, 107), glow=None)
cta = text_layer(['COMMENT YOUR COUNTRY'], [(540, 272)], 760, 44, fill=(255, 211, 107), glow=(255, 211, 107))
CTA_ARR, KICK_ARR = np.array(cta), np.array(kicker)

# legend items: 2 columns x 4 rows, column-major in reveal order
LX, LY, ROWH, COLW = [84, 496], 1282, 62, 404
LEG_FONT = min((fit(g[1], COLW - 44, 34) for g in GROUPS), key=lambda ff: ff.size)
legend = []
for i, (key, label, col, codes) in enumerate(GROUPS):
    x, y = LX[i // 4], LY + (i % 4) * ROWH
    im = Image.new('RGBA', (COLW + 40, 60), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if col is None:
        d.pieslice((4, 14, 32, 42), 135, 315, fill=GROUPS[0][2] + (255,))
        d.pieslice((4, 14, 32, 42), -45, 135, fill=GROUPS[1][2] + (255,))
    else:
        d.ellipse((4, 14, 32, 42), fill=col + (255,))
    d.text((44, 29), label, font=LEG_FONT, fill=(255, 255, 255, 255), anchor='lm')
    legend.append((im, x, y - 30))

# ---------- snow ----------
rng = random.Random(7)
flakes = [dict(x=rng.uniform(0, W), y=rng.uniform(0, H), v=rng.uniform(35, 85), r=rng.uniform(1.6, 4.2),
               a=rng.uniform(0.25, 0.7), ph=rng.uniform(0, 6.28)) for _ in range(85)]

def ease(u): return 1 - (1 - max(0.0, min(1.0, u))) ** 3
def scaled(arr, k):
    out = arr.copy(); out[:, :, 3] = np.clip(arr[:, :, 3].astype(np.float32) * k, 0, 255).astype(np.uint8)
    return Image.fromarray(out, 'RGBA')

PRE = 0.40
def frame(t):
    im = base.copy()
    for L, t0 in zip(layers, T0):
        f = ease((t - t0) / 0.4)
        flash = math.exp(-((t - t0 - 0.22) / 0.2) ** 2)
        tw = 1 + 0.07 * math.sin(2 * math.pi * (0.6 * t + L['phase'])) if t > t0 + 0.6 else 1.0
        im.alpha_composite(scaled(L['glow'], min(1.0, (0.22 + 0.6 * f + 0.5 * flash) * tw)), dest=L['bb'][:2])
        im.alpha_composite(scaled(L['fill'], min(1.0, (PRE + (0.95 - PRE) * f) * tw)), dest=L['bb'][:2])
    im.alpha_composite(borders)
    sn = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ds = ImageDraw.Draw(sn)
    for fl in flakes:
        y = (fl['y'] + fl['v'] * t) % H; x = fl['x'] + 14 * math.sin(fl['ph'] + t * 0.9)
        ds.ellipse((x - fl['r'], y - fl['r'], x + fl['r'], y + fl['r']), fill=(255, 255, 255, int(255 * fl['a'])))
    im.alpha_composite(sn)
    im.alpha_composite(title)
    k = ease((t - 10.6) / 0.35)
    if k < 1:
        im.alpha_composite(scaled(KICK_ARR, 1 - k))
    if k > 0:
        im.alpha_composite(scaled(CTA_ARR, k))
    for (lim, x, y), t0 in zip(legend, T0):
        f = ease((t - t0) / 0.3)
        pop = 1 + 0.10 * math.exp(-((t - t0 - 0.15) / 0.15) ** 2)
        li = lim if pop < 1.001 else lim.resize((int(lim.width * pop), int(lim.height * pop)), Image.BILINEAR)
        dy = (li.height - lim.height) // 2
        im.alpha_composite(scaled(np.array(li), 0.5 + 0.5 * f), dest=(x, y - dy))
    return im

def debug_boxes(im):
    d = ImageDraw.Draw(im)
    d.rectangle((900, 1035, W, H), outline=(255, 0, 0, 255), width=3)
    d.rectangle((0, 1540, W, H), outline=(255, 0, 0, 255), width=3)
    d.line((50, 0, 50, H), fill=(255, 0, 0, 255), width=2); d.line((W - 50, 0, W - 50, H), fill=(255, 0, 0, 255), width=2)
    return im

if MODE in ('debug', 'stills'):
    for t in (0.0, 4.0, 12.5):
        im = frame(t)
        if MODE == 'debug':
            im = debug_boxes(im)
        im.convert('RGB').save(f'{still_dir}/pilot_t{t:04.1f}.jpg', quality=90)
    sys.exit(0)

N = int(DUR * FPS)
ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
                       '-i', '-', '-ss', '0', '-t', str(DUR), '-i', audio_path,
                       '-af', f'afade=t=in:d=0.3,afade=t=out:st={DUR - 1.6}:d=1.6,highshelf=f=3000:g=-3,loudnorm=I=-20:TP=-2:LRA=7',
                       '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p',
                       '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-shortest', '-movflags', '+faststart', out_mp4], stdin=subprocess.PIPE)
for i in range(N):
    ff.stdin.write(frame(i / FPS).convert('RGB').tobytes())
ff.stdin.close(); ff.wait()
print('done', out_mp4)
