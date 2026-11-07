"""Compose a YouTube thumbnail (1280x720 JPEG) from a video still plus big key text.

usage: python3 tools/thumb.py <still.png> <out.jpg> "<LINE 1|[HIGHLIGHT] LINE 2>" \
           [--zoom 1.0] [--cx 0.5] [--cy 0.5] [--x 0.5] [--y 0.5] [--size 150] [--align center]
Text style = the video's bigText: YouTube Sans Black, white, black stroke, soft shadow,
one highlight colour for [bracketed] words. No boxes, no pills.
"""
import argparse, re
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FONT = '/home/user/YTP1/germany_shorts/fonts/YouTubeSans-Black.otf'
HL = (255, 210, 63)
INK = (20, 16, 24)
W, H = 1280, 720


def parts(line):
    return [(m.group(1), HL) if m.group(1) is not None else (m.group(2), (255, 255, 255))
            for m in re.finditer(r'\[([^\]]*)\]|([^\[]+)', line)]


def layout(d, fonts, lines, a):
    """yield (x, y, text, colour, font) for every run of every line"""
    top = a.y * H - sum(f.size * 1.02 for f in fonts) / 2
    for line, font in zip(lines, fonts):
        ps = parts(line)
        ws = [d.textlength(t, font=font) for t, _ in ps]
        tw = sum(ws)
        x = a.x * W - (tw / 2 if a.align == 'center' else (tw if a.align == 'right' else 0))
        for (t, col), w in zip(ps, ws):
            yield x, top, t, col, font
            x += w
        top += font.size * 1.02


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('still'); ap.add_argument('out'); ap.add_argument('text')
    ap.add_argument('--zoom', type=float, default=1.0)
    ap.add_argument('--cx', type=float, default=0.5); ap.add_argument('--cy', type=float, default=0.5)
    ap.add_argument('--x', type=float, default=0.5); ap.add_argument('--y', type=float, default=0.5)
    ap.add_argument('--size', default='150', help='one size, or one per line: 92,120')
    ap.add_argument('--align', default='center')
    a = ap.parse_args()

    im = Image.open(a.still).convert('RGB')
    sw, sh = im.size
    cw, ch = sw / a.zoom, sh / a.zoom
    x0 = min(max(a.cx * sw - cw / 2, 0), sw - cw)
    y0 = min(max(a.cy * sh - ch / 2, 0), sh - ch)
    im = im.crop((round(x0), round(y0), round(x0 + cw), round(y0 + ch))).resize((W, H), Image.LANCZOS)

    lines = a.text.split('|')
    sizes = [int(v) for v in a.size.split(',')]
    sizes += [sizes[-1]] * (len(lines) - len(sizes))
    fonts = [ImageFont.truetype(FONT, v) for v in sizes]
    # soft shadow first (offset, blurred), then the stroked text on top
    mask = Image.new('L', (W, H), 0)
    md = ImageDraw.Draw(mask)
    for x, y, t, _, f in layout(md, fonts, lines, a):
        md.text((x + f.size * 0.03, y + f.size * 0.06), t, font=f, fill=120,
                stroke_width=max(2, round(f.size * 0.08)), stroke_fill=120)
    mask = mask.filter(ImageFilter.GaussianBlur(max(sizes) * 0.04))
    im = Image.composite(Image.new('RGB', (W, H), INK), im, mask)
    d = ImageDraw.Draw(im)
    for x, y, t, col, f in layout(d, fonts, lines, a):
        d.text((x, y), t, font=f, fill=col, stroke_width=max(2, round(f.size * 0.08)), stroke_fill=INK)
    im.save(a.out, quality=92, optimize=True)
    print(a.out)


if __name__ == '__main__':
    main()
