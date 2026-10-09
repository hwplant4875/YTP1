"""ORBIS wordmark (Playfair Display, orbit crescent inside the O), profile pictures and banner.
usage: python3 orbis_wordmark.py OUT_DIR"""
import sys, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "..", "..", "fonts")
NAVY, CREAM, MUTED = (11, 17, 30), (228, 220, 208), (150, 158, 172)
SS = 4  # supersampling


def bg(w, h, seed=1):
    y, x = np.mgrid[0:h, 0:w]
    r = np.clip(np.hypot((x - w / 2) / w, (y - h * 0.45) / h) * 1.6, 0, 1)[..., None]
    a = np.array((16, 24, 40)) * (1 - r) + np.array((7, 11, 20)) * r
    a = a + np.random.default_rng(seed).normal(0, 2.2, (h, w, 1))
    return Image.fromarray(np.clip(a, 0, 255).astype("uint8"))


def wordmark(size, tracking=0.06, font="PlayfairDisplay-SemiBold.ttf", letters="ORBIS"):
    """returns an L mask of 'ORBIS' (cap height ~ size*0.7) with the crescent in the O"""
    f = ImageFont.truetype(os.path.join(FONTS, font), size * SS)
    tr = int(size * SS * tracking)
    widths = [f.getbbox(c)[2] - f.getbbox(c)[0] for c in letters]
    W = sum(widths) + tr * (len(letters) - 1) + size * SS
    H = int(size * SS * 1.4)
    m = Image.new("L", (W, H)); d = ImageDraw.Draw(m)
    x = size * SS // 2; boxes = []
    for c, w in zip(letters, widths):
        bb = f.getbbox(c); d.text((x - bb[0], 0), c, font=f, fill=255)
        boxes.append((x, bb[1], x + w, bb[3])); x += w + tr
    # crescent: inside the O counter, a thin moon-shaped arc on the lower left (an orbit catching light)
    x0, y0, x1, y1 = boxes[0]
    fill = m.copy()
    ImageDraw.floodfill(fill, ((x0 + x1) // 2, (y0 + y1) // 2), 128)
    counter = Image.fromarray(((np.asarray(fill) == 128) * 255).astype("uint8"))
    cw = x1 - x0
    gap = max(3, int(cw * 0.06)) | 1
    # erode the counter (blur + high threshold) to keep a gap from the stroke
    inner = counter.filter(ImageFilter.BoxBlur(gap)).point(lambda v: 255 if v > 250 else 0)
    dx, dy = int(cw * 0.065), -int((y1 - y0) * 0.035)
    shifted = Image.new("L", m.size); shifted.paste(inner, (dx, dy))
    cres = Image.fromarray(np.clip(np.asarray(inner).astype(int) - np.asarray(shifted), 0, 255).astype("uint8"))
    m = Image.fromarray(np.maximum(np.asarray(m), np.asarray(cres)))
    m = m.crop(m.getbbox())
    return m.resize((m.width // SS, m.height // SS), Image.LANCZOS)


def stamp(img, mask, cx, cy, color, glow=0):
    x, y = int(cx - mask.width / 2), int(cy - mask.height / 2)
    if glow:
        g = Image.new("L", img.size); g.paste(mask, (x, y)); g = g.filter(ImageFilter.GaussianBlur(glow))
        img.paste(Image.new("RGB", img.size, (60, 70, 90)), (0, 0), g.point(lambda v: v * 0.35))
    img.paste(Image.new("RGB", mask.size, color), (x, y), mask)


def tracked(img, text, cx, y, size, color, sp):
    f = ImageFont.truetype(os.path.join(FONTS, "YouTubeSans-Black.otf"), size); d = ImageDraw.Draw(img)
    w = sum(d.textlength(c, font=f) + sp for c in text) - sp; x = cx - w / 2
    for c in text:
        d.text((x, y), c, font=f, fill=color); x += d.textlength(c, font=f) + sp


def main(out):
    os.makedirs(out, exist_ok=True)
    # profile A: full wordmark, sized to sit inside YouTube's circle crop
    p = bg(1600, 1600); wm = wordmark(330)
    s = 1040 / wm.width; wm = wm.resize((int(wm.width * s), int(wm.height * s)), Image.LANCZOS)
    stamp(p, wm, 800, 800, CREAM, glow=30); p.save(os.path.join(out, "profile_orbis_wordmark.png"))
    # profile B: the O alone as a monogram
    p = bg(1600, 1600, 2); om = wordmark(900, letters="O")
    s = 900 / om.height; om = om.resize((int(om.width * s), int(om.height * s)), Image.LANCZOS)
    stamp(p, om, 800, 800, CREAM, glow=40); p.save(os.path.join(out, "profile_orbis_O.png"))
    # banner 2560x1440, safe band y 508..931
    b = bg(2560, 1440, 3); d = ImageDraw.Draw(b)
    for k, r in enumerate((620, 700, 780)):            # faint orbit lines through the band
        d.ellipse((1280 - r * 2.4, 720 - r * 0.42, 1280 + r * 2.4, 720 + r * 0.42), outline=(30 + k * 4, 40 + k * 4, 58 + k * 5), width=2)
    wm = wordmark(200); stamp(b, wm, 1280, 690, CREAM, glow=24)
    tracked(b, "HIDDEN EUROPE, CUT OPEN IN 3D", 1280, 800, 30, MUTED, 9)
    b.save(os.path.join(out, "banner_orbis_2560x1440.jpg"), quality=94)
    b.crop((0, 508, 2560, 931)).resize((1600, 264)).save(os.path.join(out, "banner_orbis_desktop_view.jpg"), quality=90)


if __name__ == "__main__":
    main(sys.argv[1])
