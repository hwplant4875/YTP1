# EP3 thumbnail: owner's AI still, slightly darkened (stronger soft darkening behind the centre), centred title.
# Fonts: Allura (channel script) + Cormorant Garamond (serif, Google Fonts) in the channel's warm off-white.
# text block sits a little below the centre so the face stays clear
# usage: python make_thumb.py <source.png> <out_dir> <variant>
import sys, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import numpy as np

src, out_dir, variant = sys.argv[1], sys.argv[2], sys.argv[3]
HERE = os.path.dirname(os.path.abspath(__file__))
ALLURA = os.path.join(HERE, '..', '..', 'ep01_malfoid', 'assets', 'Allura.ttf')
CORM = r'C:\Users\hw549\Downloads\YTP1\_fonts_dl\cormorant\CormorantGaramond.ttf'
W, H = 1920, 1080
COL = (246, 238, 224)

img = Image.open(src).convert('RGB').resize((W, H), Image.LANCZOS)
img = ImageEnhance.Brightness(img).enhance(0.80)                       # slightly darker overall
yy, xx = np.mgrid[0:H, 0:W]
band = np.exp(-(((xx - W / 2) / (W * 0.36)) ** 2 + ((yy - H * 0.59) / (H * 0.24)) ** 2))
arr = np.asarray(img).astype(np.float32) * (1 - 0.38 * band[..., None])  # extra soft darkening behind the text
img = Image.fromarray(arr.clip(0, 255).astype(np.uint8))

LINES = {   # (text, font, size, tracking px, y centre)
    'a': [('A QUIET HOUR IN THE LIBRARY', 'corm', 50, 9, 492), ('with Malfoid', 'allura', 200, 0, 635),
          ("jazz piano  ·  Hedwig's Theme", 'corm_i', 44, 2, 790)],
    'b': [('THE LIBRARY', 'corm', 64, 16, 500), ('with Malfoid', 'allura', 210, 0, 645),
          ('jazz piano for reading & study', 'corm_i', 44, 2, 802)],
}[variant]

def font(kind, size):
    if kind == 'allura': return ImageFont.truetype(ALLURA, size)
    f = ImageFont.truetype(CORM, size); f.set_variation_by_name('SemiBold' if kind == 'corm' else 'Medium')
    return f

def draw_line(d, text, f, track, cy):
    widths = [d.textlength(c, font=f) for c in text]
    total = sum(widths) + track * (len(text) - 1)
    x = (W - total) / 2
    asc, desc = f.getmetrics(); y = cy - (asc + desc) / 2
    for c, w in zip(text, widths):
        d.text((x, y), c, font=f, fill=255); x += w + track

text_mask = Image.new('L', (W, H), 0); d = ImageDraw.Draw(text_mask)
for text, kind, size, track, cy in LINES:
    draw_line(d, text, font(kind, size), track, cy)
# thin divider under the script line
dv = Image.new('L', (W, H), 0); ImageDraw.Draw(dv).line([(W / 2 - 150, LINES[2][4] - 46), (W / 2 + 150, LINES[2][4] - 46)], fill=170, width=2)
text_mask = Image.fromarray(np.maximum(np.asarray(text_mask), np.asarray(dv)))

shadow = text_mask.filter(ImageFilter.GaussianBlur(10)).point(lambda v: int(v * 0.75))
glow = text_mask.filter(ImageFilter.GaussianBlur(22)).point(lambda v: int(v * 0.35))
img = Image.composite(Image.new('RGB', (W, H), (12, 9, 6)), img, shadow)
img = Image.composite(Image.new('RGB', (W, H), (255, 214, 150)), img, glow)   # faint warm candle glow
img = Image.composite(Image.new('RGB', (W, H), COL), img, text_mask)

os.makedirs(out_dir, exist_ok=True)
png = os.path.join(out_dir, f'ep03_thumbnail_{variant}_1920x1080.png'); img.save(png)
jpg = os.path.join(out_dir, f'ep03_thumbnail_{variant}_1280x720.jpg'); img.resize((1280, 720), Image.LANCZOS).save(jpg, quality=92)
print(png, jpg)
