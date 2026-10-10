"""Render a title (text + colour emoji) to a transparent 1080-wide PNG strip.
usage: python3 title_png.py out.png "text with emoji 💀" [font.ttf] [max_size] [color]
Text is drawn with the given font; emoji characters with Noto Color Emoji, scaled to the text size.
Wraps to two lines when one line would be wider than 960 px."""
import sys, unicodedata
from PIL import Image, ImageDraw, ImageFont, ImageFilter

EMOJI = '/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf'
W, MAXW = 1080, 960


def is_emoji(ch):
    return ord(ch) >= 0x2190 and (unicodedata.category(ch) == 'So' or ord(ch) >= 0x1F000) or ch in '️‍'


def runs(text):
    out = []
    for ch in text:
        e = is_emoji(ch)
        if out and out[-1][0] == e:
            out[-1][1] += ch
        else:
            out.append([e, ch])
    return out


def measure(line, font, size):
    w = 0
    for e, s in runs(line):
        if e:
            w += int(size * 1.15) * len([c for c in s if c not in '️‍'])
        else:
            w += font.getlength(s)
    return w


def render_line(img, line, font, size, y, color):
    d = ImageDraw.Draw(img)
    x = (W - measure(line, font, size)) / 2
    efont = ImageFont.truetype(EMOJI, 109)
    asc = font.getmetrics()[0]
    for e, s in runs(line):
        if e:
            for c in s:
                if c in '️‍':
                    continue
                g = Image.new('RGBA', (136, 128), (0, 0, 0, 0))
                ImageDraw.Draw(g).text((0, 0), c, font=efont, embedded_color=True)
                g = g.crop(g.getbbox() or (0, 0, 1, 1))
                es = int(size * 1.05)
                g = g.resize((es, int(es * g.height / g.width)), Image.LANCZOS)
                img.alpha_composite(g, (int(x + size * .1), int(y + asc - es * .92)))
                x += int(size * 1.15)
        else:
            d.text((x, y), s, font=font, fill=color)
            x += font.getlength(s)


def main(out, text, fontfile='/home/user/rs_work/fonts/TikTokSans-Black.ttf', max_size=84, color='#ffffff', box=''):
    """box='#ffffff:200' draws the title centred on a solid full-width box of that height."""
    max_size = int(max_size)
    size = max_size
    font = ImageFont.truetype(fontfile, size)
    lines = [text]
    # prefer one line: shrink down to 80% before wrapping
    while measure(text, font, size) > MAXW and size > max_size * 0.8:
        size -= 2
        font = ImageFont.truetype(fontfile, size)
    if measure(text, font, size) > MAXW:
        size = max_size
        font = ImageFont.truetype(fontfile, size)
        words = text.split(' ')
        best = min(range(1, len(words)), key=lambda k: max(measure(' '.join(words[:k]), font, size), measure(' '.join(words[k:]), font, size)))
        lines = [' '.join(words[:best]), ' '.join(words[best:])]
        while max(measure(l, font, size) for l in lines) > MAXW:
            size -= 2
            font = ImageFont.truetype(fontfile, size)
    lh = int(size * 1.18)
    if box:
        bcol, bh = box.split(':')
        img = Image.new('RGBA', (W, int(bh)), bcol)
        top = (int(bh) - lh * len(lines)) / 2 + size * .04
    else:
        img = Image.new('RGBA', (W, lh * len(lines) + 40), (0, 0, 0, 0))
        top = 10
    for i, l in enumerate(lines):
        render_line(img, l, font, size, top + i * lh, color)
    img.save(out)
    print(out, img.size, size)


def caption(out, parts, fontfile, size=100, stroke=9, maxw=1000):
    """Name caption: parts = [(text, colour), ...] on one line, thick black outline, transparent 1080-wide strip."""
    text = ''.join(t for t, _ in parts)

    def length(t, font, size):
        # some fonts (Gmarket Sans web build) have no space glyph: advance spaces by hand
        if font.getmask(' ').getbbox() is None:
            return font.getlength(t)
        return sum(font.getlength(w) for w in t.split(' ')) + t.count(' ') * size * 0.28

    font = ImageFont.truetype(fontfile, size)
    while length(text, font, size) > maxw - 2 * stroke:
        size -= 2
        font = ImageFont.truetype(fontfile, size)
    img = Image.new('RGBA', (W, int(size * 1.3) + 2 * stroke), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    x = (W - length(text, font, size)) / 2
    for t, c in parts:
        for j, w in enumerate(t.split(' ')):
            if j:
                x += length(' ', font, size)
            if w:
                d.text((x, stroke), w, font=font, fill=c, stroke_width=stroke, stroke_fill='#000000')
                x += font.getlength(w)
    img.save(out)
    return img.size


if __name__ == '__main__':
    main(*sys.argv[1:])
