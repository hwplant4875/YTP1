# Instruction 444 EP01 overlay graphics (transparent 1920x1080 PNGs)
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
HERE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(HERE, 'YouTubeSans-Black.otf')
W, H = 1920, 1080
RED = (225, 22, 30, 255); WHITE = (245, 242, 236, 255); BONE = (230, 222, 205, 255)

def f(sz): return ImageFont.truetype(FONT, sz)

def shadow_text(im, xy, txt, font, fill, anchor='mm', blur=10, alpha=200, stroke=0):
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(sh)
    d.text((xy[0] + 4, xy[1] + 6), txt, font=font, fill=(0, 0, 0, alpha), anchor=anchor, stroke_width=stroke + 6, stroke_fill=(0, 0, 0, alpha))
    sh = sh.filter(ImageFilter.GaussianBlur(blur)); im.alpha_composite(sh)
    ImageDraw.Draw(im).text(xy, txt, font=font, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=(0, 0, 0, 255))

def word_tag(word, out):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    shadow_text(im, (W // 2, H // 2), word.upper(), f(170), WHITE, stroke=5)
    im.save(out)

def film_label(text, out):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    shadow_text(im, (W - 70, 70), text.upper(), f(38), BONE, anchor='ra', blur=6, alpha=170, stroke=2)
    im.save(out)

def rank_card(num, title, year, out):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    g = Image.new('L', (W, H), 0); dg = ImageDraw.Draw(g)
    dg.rectangle([0, 0, 900, H], fill=170); g = g.filter(ImageFilter.GaussianBlur(160))
    im.paste((0, 0, 0, 255), (0, 0), g)
    shadow_text(im, (130, 560), f'#{num}', f(380), RED, anchor='ls')
    shadow_text(im, (140, 680), title.upper(), f(92), WHITE, anchor='ls')
    shadow_text(im, (144, 760), str(year), f(64), BONE, anchor='ls')
    im.save(out)

def odds(pct, out, frac=None):
    col = (60, 200, 90, 255) if pct >= 60 else (240, 190, 40, 255) if pct >= 30 else RED
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    x0, y0, bw, bh = 110, H - 250, 760, 46
    pnl = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dp = ImageDraw.Draw(pnl)
    dp.rounded_rectangle([x0 - 40, y0 - 110, x0 + bw + 40, y0 + bh + 50], 26, fill=(0, 0, 0, 185))
    im.alpha_composite(pnl); d = ImageDraw.Draw(im)
    d.text((x0, y0 - 30), 'SURVIVAL RATE', font=f(54), fill=WHITE, anchor='ls')
    d.text((x0 + bw, y0 - 22), f'{pct:g}%', font=f(96), fill=col, anchor='rs')
    d.rounded_rectangle([x0, y0, x0 + bw, y0 + bh], 23, outline=(255, 255, 255, 140), width=4)
    v = pct if frac is None else frac
    fw = max(bh, bw * v / 100)
    d.rounded_rectangle([x0, y0, x0 + fw, y0 + bh], 23, fill=col)
    im.save(out)

def instruction(text, out):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    fn = f(130)
    while d.textlength(text.upper(), font=fn) > W - 260: fn = f(fn.size - 6)
    shadow_text(im, (W // 2, H // 2 - 95), 'INSTRUCTION', f(56), RED, stroke=3)
    shadow_text(im, (W // 2, H // 2 + 20), text.upper(), fn, WHITE, stroke=7)
    im.save(out)

def center_title(lines, out, big=150, color=WHITE):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    y = H // 2 - (len(lines) - 1) * big * 0.55
    for ln in lines:
        c = RED if ln.startswith('!') else color
        shadow_text(im, (W // 2, int(y)), ln.lstrip('!'), f(big), c); y += big * 1.1
    im.save(out)
