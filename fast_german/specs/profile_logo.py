"""Profile (2026-10-11, user): text only, clean like a brand logo. DIN-style Barlow Condensed, flat colours.
A: asphalt background (matches the banner), white 'Fast' + Autobahn-sign yellow 'German'. B: yellow background, black type."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from PIL import Image, ImageDraw, ImageFont
from branding_v4 import FD
D = "/mnt/project-files/fast_german/branding/final/"
S = 800


def word(txt, width, fill):
    f = ImageFont.truetype(f"{FD}/BarlowCondensed-Black.ttf", 400)
    im = Image.new("RGBA", (int(f.getlength(txt)) + 80, 600))
    ImageDraw.Draw(im).text((40, 40), txt, font=f, fill=fill + (255,))
    im = im.crop(im.getbbox())
    return im.resize((width, int(im.height * width / im.width)), Image.LANCZOS)


def logo(bg, c1, c2, name):
    im = Image.new("RGBA", (S, S), bg + (255,))
    t1, t2 = word("Fast", 440, c1), word("German", 580, c2)
    gap = 26
    y = (S - (t1.height + gap + t2.height)) // 2
    im.alpha_composite(t1, ((S - t2.width) // 2, y))                 # left-aligned with 'German'
    im.alpha_composite(t2, ((S - t2.width) // 2, y + t1.height + gap))
    im.convert("RGB").save(D + name)
    return im


if __name__ == "__main__":
    A = logo((34, 36, 40), (255, 255, 255), (255, 204, 0), "profile_logo_A_dark.png")
    B = logo((255, 204, 0), (20, 20, 22), (20, 20, 22), "profile_logo_B_yellow.png")
    m = Image.new("L", (S, S), 0); ImageDraw.Draw(m).ellipse((0, 0, S - 1, S - 1), fill=255)
    sheet = Image.new("RGB", (760, 230), "white")
    for i, im in enumerate((A, B)):
        for s, (x, y) in ((176, (20, 20)), (88, (220, 20)), (40, (220, 130))):
            sheet.paste(im.convert("RGB").resize((s, s), Image.LANCZOS), (x + i * 380, y), m.resize((s, s)))
    sheet.save(D + "profile_logo_sizes.png")
    print("ok")
