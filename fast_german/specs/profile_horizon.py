"""Profile (2026-10-11, user): an Autobahn running to the horizon, 'Fast / German' above it with a black stroke."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from branding_v4 import FD
D = "/mnt/project-files/fast_german/branding/final/"
S = 800
HZ = 530                       # horizon line
VP = (S // 2, HZ)              # vanishing point
LINE = (245, 245, 240)


def sky():
    y = np.linspace(0, 1, HZ)[:, None, None]
    top, mid, low = np.array([24, 52, 110]), np.array([70, 110, 190]), np.array([255, 178, 90])
    c = np.where(y < 0.6, top + (mid - top) * (y / 0.6), mid + (low - mid) * ((y - 0.6) / 0.4))
    return np.repeat(c, S, axis=1)


def screen_y(z):
    """Depth z (metres ahead) → screen row; camera ~1.6 m high."""
    return HZ + 260.0 * 8 / (z + 8) * 1.4 - 0 if False else HZ + (S - HZ) * 6.0 / (z + 6.0)


def screen_x(xm, z):
    """Lateral offset xm (metres from road centre) at depth z → screen column."""
    return VP[0] + xm * (S - HZ) * 6.0 / (z + 6.0) / 3.2


def quad(d, x0, x1, z0, z1, fill):
    d.polygon([(screen_x(x0, z0), screen_y(z0)), (screen_x(x1, z0), screen_y(z0)),
               (screen_x(x1, z1), screen_y(z1)), (screen_x(x0, z1), screen_y(z1))], fill=fill)


def scene():
    im = Image.new("RGB", (S, S))
    im.paste(Image.fromarray(sky().astype("uint8")), (0, 0))
    # sun glow on the horizon (sky only), then the flat dusk ground
    glow = Image.new("RGBA", (S, S)); gd = ImageDraw.Draw(glow)
    gd.ellipse((VP[0] - 150, HZ - 110, VP[0] + 150, HZ + 110), fill=(255, 225, 160, 150))
    im = Image.alpha_composite(im.convert("RGBA"), glow.filter(ImageFilter.GaussianBlur(45))).convert("RGB")
    d = ImageDraw.Draw(im)
    d.rectangle((0, HZ, S, S), fill=(52, 58, 56))
    far, near = 4000, -5.9
    half = 9.0                                                                  # 2 lanes each way + shoulders ≈ 18 m
    quad(d, -half - 1.2, half + 1.2, near, far, (110, 112, 116))                # concrete verge
    quad(d, -half, half, near, far, (46, 48, 54))                               # asphalt
    quad(d, -0.3, 0.3, near, far, (150, 152, 158))                              # central guard-rail
    for xm in (-half + 0.6, half - 0.9):                                        # outer edge lines
        quad(d, xm, xm + 0.3, near, far, LINE)
    for xm in (-0.9, 0.6):                                                      # inner edge lines
        quad(d, xm, xm + 0.3, near, far, LINE)
    for xm in (-4.6, 4.45):                                                     # lane dashes: 6 m line, 12 m gap
        z = near
        while z < 600:
            quad(d, xm, xm + 0.15 + 0.1, z, z + 6, LINE); z += 18
    return im


def outlined_text(txt, size, fill, stroke):
    f = ImageFont.truetype(f"{FD}/BarlowCondensed-Black.ttf", size)
    l, t, r, b = f.getbbox(txt, stroke_width=stroke)
    im = Image.new("RGBA", (r - l + 20, b - t + 20))
    ImageDraw.Draw(im).text((10 - l, 10 - t), txt, font=f, fill=fill + (255,), stroke_width=stroke, stroke_fill=(0, 0, 0, 255))
    return im.crop(im.getbbox())


def profile():
    im = scene().convert("RGBA")
    t1 = outlined_text("Fast", 240, (255, 255, 255), 13)
    t2 = outlined_text("German", 175, (255, 214, 0), 11)
    y = 105
    for t in (t1, t2):
        sh = Image.new("RGBA", (t.width + 60, t.height + 60), (0, 0, 0, 0))
        a = Image.new("L", sh.size, 0); a.paste(t.split()[3].point(lambda v: v // 2), (30, 30)); sh.putalpha(a)
        im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)), ((S - t.width) // 2 + 6 - 30, y + 10 - 30))
        im.alpha_composite(t, ((S - t.width) // 2, y))
        y += t.height - 6
    return im


if __name__ == "__main__":
    im = profile()
    im.convert("RGB").save(D + "profile_fast_german.png")
    m = Image.new("L", (S, S), 0); ImageDraw.Draw(m).ellipse((0, 0, S - 1, S - 1), fill=255)
    sheet = Image.new("RGB", (420, 230), "white")
    for s, (x, y) in ((176, (20, 20)), (88, (220, 20)), (40, (220, 130))):
        sheet.paste(im.convert("RGB").resize((s, s), Image.LANCZOS), (x, y), m.resize((s, s)))
    sheet.save(D + "profile_sizes.png")
    print("ok")
