"""Profile (user 2026-10-11): white background, pretzel sitting in an open donut box. Flat illustration."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__)); sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import common as C
D = "/mnt/project-files/fast_german/branding/final/"
S, K = 800, 3            # draw at 3x, downsample for clean edges
PINK, PINK_D, PINK_L, INSIDE = (255, 150, 178), (232, 112, 146), (255, 196, 212), (214, 96, 130)


def P(*pts):
    return [(x * K, y * K) for x, y in pts]


def profile(label=True):
    im = Image.new("RGBA", (S * K, S * K), (255, 255, 255, 255))
    d = ImageDraw.Draw(im)
    # floor shadow
    sh = Image.new("L", im.size, 0)
    ImageDraw.Draw(sh).ellipse(P((110, 655), (690, 715)), fill=80)
    im.paste((0, 0, 0), (0, 0), sh.filter(ImageFilter.GaussianBlur(14 * K)))
    # lid standing open behind the box
    d.polygon(P((175, 330), (625, 330), (600, 110), (200, 110)), fill=PINK)
    d.polygon(P((195, 322), (605, 322), (584, 128), (216, 128)), fill=PINK_L)
    if label:
        f = ImageFont.truetype("/mnt/project-files/fonts/de/BarlowCondensed-ExtraBold.ttf", 78 * K)
        d.text((400 * K, 222 * K), "FAST GERMAN", font=f, fill=(214, 86, 124), anchor="mm")
    # inside: back wall, then the floor seen from above
    d.polygon(P((170, 330), (630, 330), (640, 368), (160, 368)), fill=INSIDE)
    d.polygon(P((160, 368), (640, 368), (684, 570), (116, 570)), fill=(255, 236, 241))
    # pretzel lying in the box, with a soft contact shadow
    pz = C.icon("pretzel", 470 * K // 2).resize((470 * K, 400 * K), Image.LANCZOS)
    ps = Image.new("L", im.size, 0)
    ps.paste(pz.split()[3].point(lambda v: v * 70 // 255), (165 * K, 268 * K))
    im.paste((150, 70, 90), (0, 0), ps.filter(ImageFilter.GaussianBlur(10 * K)))
    im.alpha_composite(pz, (165 * K, 245 * K))
    # low front wall and side walls
    d.polygon(P((116, 570), (684, 570), (664, 665), (136, 665)), fill=PINK)
    d.polygon(P((160, 368), (116, 570), (136, 665), (100, 590), (150, 360)), fill=PINK_D)
    d.polygon(P((640, 368), (684, 570), (664, 665), (700, 590), (650, 360)), fill=PINK_D)
    d.line(P((116, 570), (684, 570)), fill=PINK_L, width=5 * K)
    return im.resize((S, S), Image.LANCZOS)


if __name__ == "__main__":
    profile().convert("RGB").save(D + "profile_box.png")
    profile(False).convert("RGB").save(D + "profile_box_plain.png")
