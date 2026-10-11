"""STRATA profile, flat 2D: the Playfair S sliced into strata that slip apart, one glowing amber seam.
Writes A (stepped stone tones, like the 3D mark) and B (one cream tone) at 800x800."""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(HERE, "..", "scenes", "data", "fonts", "PlayfairDisplay-Bold.ttf")
OUT = "/mnt/project-files/plans/fineprint/branding/strata"
S = 3200                       # supersampled canvas
BG = (9, 9, 11)
AMBER = (255, 166, 74)
# fractions of the letter height from the top: [from, to, tone (None = seam), slip as a fraction of letter height]
CUTS = [(0.00, 0.335, 0, -0.035), (0.335, 0.505, 1, 0.0), (0.505, 0.55, None, 0.0), (0.545, 0.76, 2, 0.035), (0.76, 1.0, 3, 0.06)]
GAP = 0.022


def letter_mask(height):
    f = ImageFont.truetype(FONT, int(height * 1.45))
    bb = f.getbbox("S")
    m = Image.new("L", (bb[2] - bb[0] + 4, bb[3] - bb[1] + 4), 0)
    ImageDraw.Draw(m).text((2 - bb[0], 2 - bb[1]), "S", font=f, fill=255)
    return m


def build(tones, name):
    img = Image.new("RGB", (S, S), BG)
    # faint radial warmth behind the mark
    halo = Image.new("L", (S, S), 0)
    ImageDraw.Draw(halo).ellipse((S * 0.22, S * 0.22, S * 0.78, S * 0.78), fill=40)
    halo = halo.filter(ImageFilter.GaussianBlur(S * 0.09))
    img = Image.composite(Image.new("RGB", (S, S), (40, 26, 14)), img, halo)

    m = letter_mask(int(S * 0.58))
    w, h = m.size
    ox, oy = (S - w) // 2, (S - h) // 2
    glow = Image.new("L", (S, S), 0)
    for a, b, tone, slip in CUTS:
        top = int(a * h + (GAP * h / 2 if a > 0 else 0))
        bot = int(b * h - (GAP * h / 2 if b < 1 else 0))
        if tone is None:   # the seam: a thin amber bar across the full letter width, not clipped to the glyph
            band = m.crop((0, top, w, bot)).point(lambda v: 255 if v > 0 else 0)
            bar = Image.new("L", (w, bot - top), 0)
            ImageDraw.Draw(bar).rectangle((int(w * 0.30), 0, int(w * 0.80), bot - top), fill=255)
            band = bar
            img.paste(Image.new("RGB", band.size, AMBER), (ox, oy + top), band)
            glow.paste(band, (ox, oy + top))
            continue
        band = m.crop((0, top, w, bot))
        dx = int(slip * h)
        img.paste(Image.new("RGB", band.size, tones[tone]), (ox + dx, oy + top), band)
    # amber bloom around the seam
    g = glow.filter(ImageFilter.GaussianBlur(S * 0.03)).point(lambda v: min(255, v * 3))
    img = Image.composite(Image.new("RGB", (S, S), AMBER), img, g.point(lambda v: int(v * 0.7)))
    img.paste(Image.new("RGB", (S, S), (255, 214, 160)), (0, 0), glow.filter(ImageFilter.GaussianBlur(3)).point(lambda v: v * 0.6))
    img = img.resize((800, 800), Image.LANCZOS)
    img.save(os.path.join(OUT, name))
    # circle preview, as YouTube crops it
    c = Image.new("L", (800, 800), 0); ImageDraw.Draw(c).ellipse((0, 0, 799, 799), fill=255)
    prev = Image.new("RGB", (800, 800), (255, 255, 255)); prev.paste(img, (0, 0), c)
    return prev


a = build([(236, 230, 219), (214, 206, 192), (186, 177, 163), (158, 149, 136)], "profile_strata_2d_A.png")
b = build([(232, 226, 214)] * 4, "profile_strata_2d_B.png")
sheet = Image.new("RGB", (1700, 860), (255, 255, 255)); sheet.paste(a, (30, 30)); sheet.paste(b, (870, 30))
sheet.save("/tmp/claude-0/sc/p2d.jpg")
