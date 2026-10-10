"""1280x720 thumbnails for the long-form videos."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
from PIL import Image, ImageDraw
import common as C
from short import text_img, shadowed, font
from longform import bg_image, DARK, LIGHT, pill
OUT = os.path.join(os.path.dirname(__file__), "..", "out")

def big(t, size, col, stroke=12, sc=(28, 28, 30)):
    return shadowed(text_img(t, font(size, "Bold"), col + (255,), stroke=stroke, stroke_fill=sc + (255,)), 8, 12, 90)

def make(name, theme, lines, icons, tag=None):
    im = bg_image(theme).resize((1280, 720))
    im.alpha_composite(pill("FAST GERMAN", C.YELLOW, C.INK, size=30, icon="pretzel"), (36, 30))
    y = 150
    for t, size, col in lines:
        b = big(t, size, col)
        im.alpha_composite(b, (40, y))
        y += b.height - 30
    x = 1280 - 40
    for ic, s, yy in icons:
        i = shadowed(C.icon(ic, s), 10, 16, 90)
        im.alpha_composite(i, (x - i.width, yy))
        x -= i.width - 80
    if tag:
        p = pill(tag, (255, 255, 255), C.INK, size=34)
        im.alpha_composite(p, (46, 720 - p.height - 36))
    im.convert("RGB").save(os.path.join(OUT, name), quality=92)

make("thumb_L1.jpg", DARK, [("8 HOURS", 130, C.YELLOW), ("German words", 96, (255, 255, 255)), ("while you sleep", 74, (255, 255, 255))],
     [("crescent-moon", 330, 150), ("sleeping-face", 210, 440)], tag="350 beginner words · said slowly")
make("thumb_L2.jpg", LIGHT, [("GERMAN A1", 130, C.YELLOW), ("in 25 MIN", 130, (255, 255, 255))],
     [("rocket", 360, 200)], tag="No boring grammar")
make("thumb_L3.jpg", LIGHT, [("KITCHEN", 140, C.YELLOW), ("in German", 100, (255, 255, 255))],
     [("cooking", 400, 170)], tag="Picture dictionary · der die das colors")


def l1_variants():
    """A/B test variants for the 8 h sleep video (user rule: 3 thumbnails per video, a/b/c)."""
    # b: provocative, red circle and arrow
    im = Image.open(os.path.join(OUT, "thumb_L1.jpg")).convert("RGBA")
    d = ImageDraw.Draw(im)
    d.ellipse((50, 170, 640, 320), outline=(229, 45, 50, 255), width=10)
    d.line((900, 230, 690, 245), fill=(229, 45, 50, 255), width=16)
    d.polygon([(650, 248), (700, 215), (705, 275)], fill=(229, 45, 50, 255))
    im.convert("RGB").save(os.path.join(OUT, "thumb_L1b.jpg"), quality=92)
    # c: question hook, moon left
    im = bg_image(DARK).resize((1280, 720))
    im.alpha_composite(pill("FAST GERMAN", C.YELLOW, C.INK, size=30, icon="pretzel"), (36, 30))
    moon = shadowed(C.icon("crescent-moon", 380), 10, 16, 90)
    im.alpha_composite(moon, (40, 200))
    y = 190
    for t, size, col in [("Fall asleep", 104, (255, 255, 255)), ("learning", 104, (255, 255, 255)),
                         ("GERMAN", 132, C.YELLOW)]:
        b = big(t, size, col)
        im.alpha_composite(b, (1280 - b.width - 40, y))
        y += b.height - 34
    im.convert("RGB").save(os.path.join(OUT, "thumb_L1c.jpg"), quality=92)


l1_variants()
