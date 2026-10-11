"""Mock-up (user 2026-10-11): what the v2 shorts look like with Autobahn graphics instead of the night sky.
Asphalt background with lane markings, blue motorway signs for the English meaning, German words as road paint."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__)); sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
from PIL import Image, ImageDraw, ImageFilter
import short_v2 as V
import common as C
from branding_v5 import asphalt, worn, blue_sign, shield
W, H = 1080, 1920
OUT = "/mnt/project-files/fast_german/preview/autobahn_mock/"
os.makedirs(OUT, exist_ok=True)
PAINT = (240, 240, 232)


def road():
    bg = asphalt(W, H, 4)
    d = ImageDraw.Draw(bg)
    for x in (46, W - 46):                                   # solid edge lines
        d.rectangle((x - 8, 0, x + 8, H), fill=PAINT + (255,))
    for y in range(-60, H, 300):                              # centre lane dashes, kept clear of the content
        if y + 100 < 110 or y > 1500:
            d.rectangle((W // 2 - 8, y, W // 2 + 8, y + 100), fill=PAINT + (150,))
    sign = blue_sign(560, 120)
    t = V.text_im("FAST GERMAN", V.de_font(76), (255, 255, 255))
    sign.alpha_composite(t, ((sign.width - t.width) // 2, (sign.height - t.height) // 2))
    sh = shield(96, "A1")
    bg.alpha_composite(V.shadow(sign, 14, 120, 8), ((W - sign.width) // 2 - 28 - 60, 150 - 28))
    bg.alpha_composite(V.shadow(sh, 14, 120, 8), ((W + sign.width) // 2 + 30 - 28 - 60, 162 - 28))
    return bg


def paint_word(de, article=None, size=200, max_w=W - 2 * V.MX):
    lead = (article + " ") if article else ""
    f = V.fit(lead + de, V.de_font, max_w, size)
    l, t, r, b = f.getbbox(lead + de)
    im = Image.new("RGBA", (r - l + 8, b - t + 8))
    d = ImageDraw.Draw(im)
    if lead:
        d.text((4 - l, 4 - t), lead, font=f, fill=V.lighten(C.GENDER[article], 0.1) + (255,))
    d.text((4 - l + f.getlength(lead), 4 - t), de, font=f,
           fill=(V.lighten(C.GENDER[article], 0.1) if article else PAINT) + (255,))
    return worn(im, 3, 0.12)


def meaning_sign(en, w=None, size=70):
    f = V.fit(en, V.ui_font, (w or 900) - 80, size)
    t = V.text_im(en, f, (255, 255, 255))
    s = blue_sign(w or t.width + 90, t.height + 60)
    s.alpha_composite(t, ((s.width - t.width) // 2, (s.height - t.height) // 2))
    return s


def put(bg, im, cx, cy):
    bg.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))


def row(bg, el, y, s=250):
    th = V.thumb(el, s)
    frame = Image.new("RGBA", (s + 16, s + 16)); ImageDraw.Draw(frame).rounded_rectangle((0, 0, s + 15, s + 15), 40, fill=(255, 255, 255, 255))
    frame.alpha_composite(th, (8, 8))
    bg.alpha_composite(V.shadow(frame, 16, 140, 8), (V.MX - 32, y - (s + 16) // 2 - 32))
    tx = V.MX + s + 50
    w = paint_word(el["de"], el.get("article"), 150, W - V.MX - tx)
    bg.alpha_composite(w, (tx, y - s // 2 + 6))
    if el.get("en"):
        m = meaning_sign(el["en"], size=58)
        bg.alpha_composite(V.shadow(m, 12, 120, 6), (tx - 24, y + s // 2 - m.height - 4 - 24))


def frame_hook():
    bg = road()
    card = V.photo_card("tor_3.jpg", 900, 680)[0].resize((900, 680))
    c = Image.new("RGBA", (920, 700)); ImageDraw.Draw(c).rounded_rectangle((0, 0, 919, 699), 40, fill=(255, 255, 255, 255))
    c.alpha_composite(V.rounded(card, 32), (10, 10))
    put(bg, V.shadow(c, 26, 150, 14), W / 2, 690)
    put(bg, paint_word("Torschlusspanik", size=210), W / 2, 1210)
    put(bg, V.shadow(meaning_sign("panic before the gate closes", 900, 64), 14, 130, 8), W / 2, 1390)
    return bg


def frame_rows(gender=False):
    bg = road()
    rows = [dict(photo="tor_1.jpg", de="Tor", en="gate", article="das"),
            dict(photo="lock_1.jpg", focus=(0.62, 0.5), de="Schluss", en="closing", article="der"),
            dict(icon="face-screaming-in-fear", de="Panik", en="panic", article="die")]
    for i, r in enumerate(rows):
        if not gender:
            r.pop("article")
        else:
            r.pop("en")
        row(bg, r, (560 if not gender else 520) + i * (340 if not gender else 300))
    if gender:
        put(bg, paint_word("Torschlusspanik", "die", 150), W / 2, 1420)
    return bg


if __name__ == "__main__":
    fr = [frame_hook(), frame_rows(), frame_rows(True)]
    for i, f in enumerate(fr):
        f.convert("RGB").save(OUT + f"mock_{i + 1}.png")
    sheet = Image.new("RGB", (3 * 540 + 40, 960 + 20), (20, 20, 20))
    for i, f in enumerate(fr):
        sheet.paste(f.convert("RGB").resize((540, 960), Image.LANCZOS), (10 + i * 550, 10))
    sheet.save(OUT + "autobahn_shorts_mock.png")
