"""Channel branding for Fast German: profile pictures (800x800) and banner (2560x1440, safe area 1546x423)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
from PIL import Image, ImageDraw
import common as C
from short import text_img, shadowed, font, ui_font
OUT = "/mnt/project-files/fast_german/branding"
os.makedirs(OUT, exist_ok=True)
BLUE, RED, GREEN = C.GENDER["der"], C.GENDER["die"], C.GENDER["das"]


def profile_a():
    """Pretzel on navy (the sleep-video color) with der/die/das dots; everything inside the circular crop."""
    im = Image.new("RGBA", (800, 800), (20, 27, 45, 255))
    p = shadowed(C.icon("pretzel", 500), 10, 18, 90)
    im.alpha_composite(p, ((800 - p.width) // 2, 105))
    d = ImageDraw.Draw(im)
    for i, col in enumerate((BLUE, RED, GREEN)):
        x = 400 + (i - 1) * 95
        d.ellipse((x - 32, 600, x + 32, 664), fill=col + (255,))
    im.convert("RGB").save(os.path.join(OUT, "profile_a_pretzel.png"))


def profile_b():
    """'FG' monogram, letters in der/die colors, das-green dot, on cream."""
    im = Image.new("RGBA", (800, 800), C.CREAM + (255,))
    f = font(430, "Bold")
    F = text_img("F", f, BLUE + (255,), stroke=14, stroke_fill=C.INK + (255,))
    G = text_img("G", f, RED + (255,), stroke=14, stroke_fill=C.INK + (255,))
    x = (800 - (F.width + G.width - 40 + 70)) // 2  # F, G and the green dot, centered for the round crop
    im.alpha_composite(shadowed(F, 8, 12, 70), (x, 150))
    im.alpha_composite(shadowed(G, 8, 12, 70), (x + F.width - 40, 150))
    d = ImageDraw.Draw(im)
    gx = x + F.width - 40 + G.width - 10
    d.ellipse((gx - 10, 470, gx + 66, 546), fill=GREEN + (255,), outline=C.INK + (255,), width=10)
    im.convert("RGB").save(os.path.join(OUT, "profile_b_monogram.png"))


def banner():
    W, H = 2560, 1440
    im = Image.new("RGBA", (W, H), C.CREAM + (255,))
    d = ImageDraw.Draw(im)
    # subtle dot pattern like the videos
    for y in range(0, H, 48):
        for x in range((y // 48 % 2) * 24, W, 48):
            d.ellipse((x - 3, y - 3, x + 3, y + 3), fill=(236, 222, 196, 255))
    # der/die/das stripe at the bottom of the safe area
    cx, cy = W // 2, H // 2
    title = text_img("FAST GERMAN", font(190, "Bold"), C.YELLOW + (255,), stroke=16, stroke_fill=C.INK + (255,))
    im.alpha_composite(shadowed(title, 10, 14, 80), (cx - title.width // 2, cy - 200))
    x = cx - 390
    for word, col in (("der", BLUE), ("die", RED), ("das", GREEN)):
        t = text_img(word, font(96, "Bold"), col + (255,), stroke=8, stroke_fill=(255, 255, 255, 255))
        im.alpha_composite(t, (x + (260 - t.width) // 2, cy - 5))
        x += 260
    tag = text_img("Learn German fast. New shorts every day.", ui_font(44), C.INK + (255,))
    im.alpha_composite(tag, (cx - tag.width // 2, cy + 125))
    # icons outside the safe area (visible on desktop and TV)
    for name, x, y, s in (("pretzel", 260, 380, 300), ("hot-beverage", 620, 1120, 240), ("crescent-moon", 2040, 330, 280),
                          ("beer-mug", 2250, 880, 240), ("bread", 300, 1000, 220), ("light-bulb", 1960, 1130, 200)):
        im.alpha_composite(shadowed(C.icon(name, s), 8, 14, 60), (x - s // 2, y - s // 2))
    im.convert("RGB").save(os.path.join(OUT, "banner_2560x1440.png"))
    # preview with the mobile safe area outlined
    pv = im.copy()
    ImageDraw.Draw(pv).rectangle((cx - 773, cy - 211, cx + 773, cy + 211), outline=(229, 72, 77, 255), width=6)
    pv.convert("RGB").resize((1280, 720)).save(os.path.join(OUT, "banner_preview_safe_area.png"))


profile_a()
profile_b()
banner()
print("ok")
