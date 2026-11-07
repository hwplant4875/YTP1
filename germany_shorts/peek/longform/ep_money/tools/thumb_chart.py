"""Thumbnail from the real Nov 4-5 5-minute bars (Yahoo Finance), drawn like a trading app.
usage: python3 tools/thumb_chart.py <SYM_i key> <out.jpg> "<LINE1>" "<LINE2>" [--logo path.png]"""
import json, sys, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
FONT = '/home/user/YTP1/germany_shorts/fonts/YouTubeSans-Black.otf'
K = 2; W, H = 1280 * K, 720 * K
BG, GRID, UP, DN = (11, 14, 17), (34, 38, 46), (38, 196, 133), (246, 70, 93)

def main():
    key, out, l1, l2 = sys.argv[1:5]; label = sys.argv[5] if len(sys.argv) > 5 else ''
    rows = [r for r in json.load(open(os.path.join(HERE, '..', 'data', 'prices.json')))[key] if '2026-11-04' <= r[0] < '2026-11-06']
    im = Image.new('RGB', (W, H), BG); d = ImageDraw.Draw(im)
    x0, x1, y0, y1 = 40 * K, 1100 * K, 80 * K, 690 * K
    hi = max(r[2] for r in rows); lo = min(r[3] for r in rows); pad = (hi - lo) * 0.06; hi += pad; lo -= pad
    Y = lambda p: y0 + (hi - p) / (hi - lo) * (y1 - y0)
    for i in range(1, 6): d.line([(x0, y0 + i * (y1 - y0) / 6), (x1, y0 + i * (y1 - y0) / 6)], fill=GRID, width=K)
    n = len(rows); dx = (x1 - x0) / n
    split = next(i for i, r in enumerate(rows) if r[0].startswith('2026-11-05'))
    d.line([(x0 + split * dx, y0), (x0 + split * dx, y1)], fill=(60, 66, 78), width=K)
    # red glow under the crash day
    glow = Image.new('RGB', (W, H), (0, 0, 0)); gd = ImageDraw.Draw(glow)
    for i, r in enumerate(rows[split:], split):
        cx = x0 + (i + 0.5) * dx; gd.line([(cx, Y(r[2])), (cx, Y(r[3]))], fill=(140, 20, 35), width=int(dx * 2.5))
    im = Image.composite(Image.blend(im, glow.filter(ImageFilter.GaussianBlur(40 * K)), 0.0), im, Image.new('L', (W, H), 255))
    im = Image.fromarray(__import__('numpy').clip(__import__('numpy').asarray(im, dtype='int16') + __import__('numpy').asarray(glow.filter(ImageFilter.GaussianBlur(30 * K)), dtype='int16'), 0, 255).astype('uint8'))
    d = ImageDraw.Draw(im)
    for i, (t, o, h, l, c, v) in enumerate(rows):
        cx = x0 + (i + 0.5) * dx; col = UP if c >= o else DN
        d.line([(cx, Y(h)), (cx, Y(l))], fill=col, width=max(2, int(dx * 0.18)))
        a, b = sorted([Y(o), Y(c)]); d.rectangle([cx - dx * 0.36, a, cx + dx * 0.36, max(b, a + 2 * K)], fill=col)
    # last price line + tag on the right
    last = rows[-1][4]; ly = Y(last)
    for xx in range(int(x0), int(x1), 14 * K): d.line([(xx, ly), (xx + 7 * K, ly)], fill=DN, width=2 * K)
    f = lambda s: ImageFont.truetype(FONT, s * K)
    tag = f'{last:,.2f}'; tw = d.textlength(tag, font=f(30))
    d.rectangle([x1 + 6 * K, ly - 22 * K, x1 + 16 * K + tw, ly + 22 * K], fill=DN)
    d.text((x1 + 11 * K, ly), tag, font=f(30), fill=(255, 255, 255), anchor='lm')
    # day labels
    for i, s in ((0, 'WED NOV 4'), (split, 'THU NOV 5')):
        d.text((x0 + i * dx + 14 * K, y0 + 30 * K), s, font=f(26), fill=(120, 128, 140), anchor='ls')
    if label: d.text((x0 + 4 * K, 30 * K), label, font=f(40), fill=(230, 233, 238), anchor='lt')
    # big claim, bottom-left over the old highs? top-left area is where price was highest; put text left-middle
    def big(s, x, y, size, col):
        ft = f(size); d.text((x + 6 * K, y + 8 * K), s, font=ft, fill=(0, 0, 0), anchor='ls', stroke_width=int(size * 0.12 * K), stroke_fill=(0, 0, 0))
        d.text((x, y), s, font=ft, fill=col, anchor='ls', stroke_width=int(size * 0.1 * K), stroke_fill=(0, 0, 0))
    big(l1, 52 * K, 560 * K, 150, (255, 255, 255))
    big(l2, 56 * K, 670 * K, 104, (255, 210, 63))
    if len(sys.argv) > 6:
        lg = Image.open(sys.argv[6]).convert('RGBA'); s = 70 * K / lg.height; lg = lg.resize((int(lg.width * s), int(lg.height * s)))
        im.paste(lg, (int(x1 - lg.width), 22 * K), lg)
    im.resize((1280, 720), Image.LANCZOS).save(out, quality=93)
    print(out)

main()
