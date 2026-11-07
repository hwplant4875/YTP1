"""Louder chart thumbnail: real Nov 4-5 bars (Yahoo Finance) merged into 15-minute candles, a red-lit cliff,
a giant red claim. usage: python3 tools/thumb_crash.py <SYM_i> <out.jpg> "<BIG>" "<SUB>" "<TAG>" [agg=3]"""
import json, sys, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
FONT = '/home/user/YTP1/germany_shorts/fonts/YouTubeSans-Black.otf'
K = 2; W, H = 1280 * K, 720 * K
BG, UP, DN = (8, 9, 12), (30, 210, 140), (255, 48, 72)
f = lambda s: ImageFont.truetype(FONT, int(s * K))

def bars(key, agg):
    days = os.environ.get('DAYS', '2026-11-04,2026-11-05').split(',')
    rows = [r for r in json.load(open(os.path.join(HERE, '..', 'data', 'prices.json')))[key] if r[0][:10] in days]
    out = []
    for day in days:
        d = [r for r in rows if r[0].startswith(day)]
        for i in range(0, len(d), agg):
            g = d[i:i + agg]; out.append((g[0][0], g[0][1], max(x[2] for x in g), min(x[3] for x in g), g[-1][4]))
    return out

def main():
    key, out, big, sub, tag = sys.argv[1:6]; agg = int(sys.argv[6]) if len(sys.argv) > 6 else 3
    rows = bars(key, agg); n = len(rows)
    split = next(i for i, r in enumerate(rows) if r[0].startswith('2026-11-05'))
    x0, x1, y0, y1 = (40 if os.environ.get('WIDE') else 330) * K, 1250 * K, (50 if os.environ.get('WIDE') else 40) * K, ((440 if sys.argv[4].strip() else 540) if os.environ.get('WIDE') else 700) * K          # chart sits right; claim lives on the left
    hi = max(r[2] for r in rows); lo = min(r[3] for r in rows); p = (hi - lo) * 0.04; hi += p; lo -= p
    Y = lambda v: y0 + (hi - v) / (hi - lo) * (y1 - y0)
    dx = (x1 - x0) / n
    # background: near-black with a red light rising from the bottom right (where it crashed)
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.hypot((xx - W * 0.8) / W, (yy - H * 1.05) / H)
    red = np.clip(1 - r / 0.75, 0, 1) ** 2 * (0.0 if os.environ.get('NOGLOW') else 1.0)   # owner 11/8: no glow
    bg = np.stack([BG[0] + 120 * red, BG[1] + 8 * red, BG[2] + 18 * red], -1)
    im = Image.fromarray(bg.clip(0, 255).astype('uint8')); d = ImageDraw.Draw(im)
    for i in range(1, 7): d.line([(0, y0 + i * (y1 - y0) / 7), (W, y0 + i * (y1 - y0) / 7)], fill=(30, 32, 40), width=K)
    # glow of the crash candles
    glow = Image.new('RGB', (W, H)); gd = ImageDraw.Draw(glow)
    for i, (t, o, h, l, c) in enumerate(rows):
        if i >= split and c < o: cx = x0 + (i + 0.5) * dx; gd.rectangle([cx - dx, Y(o), cx + dx, Y(c)], fill=(255, 30, 50))
    g = np.asarray(glow.filter(ImageFilter.GaussianBlur(26 * K)), dtype='float32') * (0.0 if os.environ.get('NOGLOW') else 0.9)
    im = Image.fromarray(np.clip(np.asarray(im, dtype='float32') + g, 0, 255).astype('uint8')); d = ImageDraw.Draw(im)
    # Wednesday close line
    wc = rows[split - 1][4]
    for x in range(int(x0), int(x1), 18 * K): d.line([(x, Y(wc)), (x + 9 * K, Y(wc))], fill=(150, 156, 170), width=2 * K)
    for i, (t, o, h, l, c) in enumerate(rows):
        cx = x0 + (i + 0.5) * dx; col = UP if c >= o else DN
        d.line([(cx, Y(h)), (cx, Y(l))], fill=col, width=max(3, int(dx * 0.16)))
        a, b = sorted([Y(o), Y(c)]); d.rectangle([cx - dx * 0.38, a, cx + dx * 0.38, max(b, a + 3 * K)], fill=col)
    # last price
    last = rows[-1][4]; d.line([(x0, Y(last)), (W, Y(last))], fill=DN, width=2 * K)
    # the claim, left, huge
    def txt(s, x, y, size, col, stroke=(0, 0, 0), sw=0.11, anchor='ls'):
        ft = f(size)
        sh = Image.new('L', (W, H)); ImageDraw.Draw(sh).text((x + 8 * K, y + 12 * K), s, font=ft, fill=255, anchor=anchor, stroke_width=int(size * sw * K))
        im.paste((0, 0, 0), (0, 0), sh.filter(ImageFilter.GaussianBlur(10 * K)).point(lambda v: int(v * 0.8)))
        ImageDraw.Draw(im).text((x, y), s, font=ft, fill=col, anchor=anchor, stroke_width=int(size * sw * K), stroke_fill=stroke)
    if os.environ.get('WIDE'):
        # one full-width number across the top, the hook line at the bottom left
        size = 200
        while ImageDraw.Draw(im).textlength(big, font=f(size)) > 1220 * K: size -= 2
        # owner 11/8: all text at the bottom; WHITE=1 -> white number with a red stroke
        if tag.strip(): txt(tag, 34 * K, 70 * K, 56, (255, 255, 255))
        white = os.environ.get('WHITE')
        txt(big, 640 * K, (575 if sub.strip() else 680) * K, size, (255, 255, 255) if white else DN, stroke=DN if white else (255, 255, 255), sw=0.09 if white else 0.06, anchor='ms')
        if sub.strip(): txt(sub, 640 * K, 698 * K, 104, (255, 214, 0), anchor='ms')
        im.resize((1280, 720), Image.LANCZOS).save(out, quality=94); print(out); return
    txt(tag, 44 * K, 120 * K, 64, (255, 255, 255))
    lines = big.split('|')
    y = 300 * K
    for i, s in enumerate(lines):
        size = 210 if i == 0 else 175
        txt(s, 40 * K, y, size, DN if i == 0 else (255, 255, 255), stroke=(255, 255, 255) if i == 0 else (0, 0, 0), sw=0.05 if i == 0 else 0.11)
        y += int(size * 0.95 * K)
    txt(sub, 46 * K, y + 10 * K, 104, (255, 214, 0))
    im.resize((1280, 720), Image.LANCZOS).save(out, quality=94); print(out)

main()
