"""Branding round 4 (2026-10-10). Brief from 영맨: you should *feel* 'learn fast' at a glance, and the type should
look German, not rounded. Type: Barlow Condensed (DIN 1451-style, OFL). Three sets, each a profile + banner:
A Autobahn sign, B speed streaks, C fast-forward chevrons."""
import os, random
from PIL import Image, ImageDraw, ImageFilter, ImageFont
FD = "/mnt/project-files/fonts/de"
OUT = "/mnt/project-files/fast_german/branding/round4"
os.makedirs(OUT, exist_ok=True)
W, H = 2560, 1440
CX, CY = W // 2, H // 2
SAFE = (CX - 773, CY - 211, CX + 773, CY + 211)
BLUE, WHITE, BLACK, YEL, RED = (0, 84, 166), (255, 255, 255), (16, 16, 18), (255, 204, 0), (226, 35, 26)


def F(size, style="Black"):
    return ImageFont.truetype(f"{FD}/BarlowCondensed-{style}.ttf", size)


def text(t, size, fill, style="Black", track=0):
    """Tightly cropped RGBA text, optional letter tracking."""
    f = F(size, style)
    w = sum(f.getlength(c) for c in t) + track * (len(t) - 1) + size
    im = Image.new("RGBA", (int(w), int(size * 1.5)))
    d, x = ImageDraw.Draw(im), size // 2
    for c in t:
        d.text((x, size // 4), c, font=f, fill=fill + (255,))
        x += f.getlength(c) + track
    return im.crop(im.getbbox())


def fit(t, width, fill, style="Black", track=0):
    """Text scaled so its visible width equals `width`."""
    probe = text(t, 400, fill, style, track)
    return text(t, int(400 * width / probe.width), fill, style, int(track * width / probe.width))


def shadow(im, off=10, blur=16, a=110):
    pad = blur * 3
    out = Image.new("RGBA", (im.width + pad * 2 + off, im.height + pad * 2 + off))
    sh = Image.new("RGBA", im.size, (0, 0, 0, a))
    sh.putalpha(im.split()[3].point(lambda v: v * a // 255))
    out.alpha_composite(sh, (pad + off, pad + off))
    out = out.filter(ImageFilter.GaussianBlur(blur))
    out.alpha_composite(im, (pad, pad))
    return out, pad


def scale_to(im, width):
    return im.resize((width, int(im.height * width / im.width)), Image.LANCZOS) if im.width > width else im


def paste_c(im, el, cx, cy, sh=True):
    if sh:
        s, pad = shadow(el)
        im.alpha_composite(s, (cx - el.width // 2 - pad, cy - el.height // 2 - pad))
    else:
        im.alpha_composite(el, (cx - el.width // 2, cy - el.height // 2))


def streaks(size, cols, n, seed, ymin=0, ymax=None, thick=(4, 22), length=(200, 1400), blur=6):
    """Horizontal motion streaks, sharp head on the right, fading tail to the left."""
    w, h = size
    ymax = ymax or h
    layer = Image.new("RGBA", size)
    rnd = random.Random(seed)
    for _ in range(n):
        y, t, ln = rnd.randint(ymin, ymax), rnd.randint(*thick), rnd.randint(*length)
        x1 = rnd.randint(-200, w + 200)
        col = rnd.choice(cols)
        grad = Image.new("RGBA", (ln, t))
        gd = ImageDraw.Draw(grad)
        for i in range(ln):
            gd.line((i, 0, i, t), fill=col + (int(255 * (i / ln) ** 1.6),))
        m = Image.new("L", (ln, t), 0)
        ImageDraw.Draw(m).rounded_rectangle((0, 0, ln - 1, t - 1), t // 2, fill=255)
        a = Image.composite(grad.split()[3], m, m)
        grad.putalpha(Image.fromarray(__import__("numpy").minimum(__import__("numpy").array(a), __import__("numpy").array(m))))
        layer.alpha_composite(grad, (x1 - ln, y - t // 2)) if x1 - ln > -ln else None
    if blur:
        layer = layer.filter(ImageFilter.BoxBlur(blur))
    return layer


def round_preview(profiles, name):
    sheet = Image.new("RGB", (len(profiles) * 360, 300), (255, 255, 255))
    m = Image.new("L", (800, 800), 0)
    ImageDraw.Draw(m).ellipse((0, 0, 799, 799), fill=255)
    for i, im in enumerate(profiles):
        x = i * 360 + 20
        for s, (ox, oy) in ((176, (0, 20)), (88, (200, 20)), (40, (200, 130))):
            sheet.paste(im.convert("RGB").resize((s, s), Image.LANCZOS), (x + ox, oy), m.resize((s, s), Image.LANCZOS))
        ImageDraw.Draw(sheet).text((x + 80, 220), "ABC"[i], fill=(0, 0, 0))
    sheet.save(os.path.join(OUT, name))


def banner_preview(im, name):
    im.convert("RGB").save(os.path.join(OUT, name + ".png"))
    pv = im.copy()
    ImageDraw.Draw(pv).rectangle(SAFE, outline=(0, 255, 120, 255), width=8)
    sheet = Image.new("RGB", (1280, 720 + 40 + 211), (255, 255, 255))
    sheet.paste(pv.convert("RGB").resize((1280, 720)), (0, 0))
    sheet.paste(im.crop(SAFE).convert("RGB").resize((773, 211)), ((1280 - 773) // 2, 760))
    sheet.save(os.path.join(OUT, name + "_preview.jpg"), quality=88)


# ---------- A: Autobahn sign ----------
def sign(w, h, label_top, label_bot, arrow=True):
    """Blue German motorway sign: white inner border, DIN type, a white arrow pointing ahead/right."""
    im = Image.new("RGBA", (w, h))
    d = ImageDraw.Draw(im)
    r = int(min(w, h) * 0.09)
    d.rounded_rectangle((0, 0, w - 1, h - 1), r, fill=BLUE + (255,))
    b = int(min(w, h) * 0.035)
    d.rounded_rectangle((b, b, w - 1 - b, h - 1 - b), r - b // 2, outline=WHITE + (255,), width=max(6, b // 2))
    return im


def profile_A():
    im = Image.new("RGBA", (800, 800), BLUE + (255,))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((125, 125, 675, 675), 56, outline=WHITE + (255,), width=16)
    t1, t2 = fit("FAST", 400, WHITE), fit("GERMAN", 400, WHITE)
    arrow = Image.new("RGBA", (400, 70))
    ad = ImageDraw.Draw(arrow)
    ad.rectangle((0, 25, 330, 45), fill=WHITE + (255,))
    ad.polygon([(320, 0), (400, 35), (320, 70)], fill=WHITE + (255,))
    total = t1.height + 28 + t2.height + 34 + arrow.height
    y = (800 - total) // 2
    for el, gap in ((t1, 28), (t2, 34), (arrow, 0)):
        im.alpha_composite(el, ((800 - el.width) // 2, y)); y += el.height + gap
    return im


def banner_A():
    # night Autobahn: dark gradient sky, tail-light (red) and head-light (white/amber) streaks
    im = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(im)
    for y in range(H):
        k = y / H
        d.line((0, y, W, y), fill=(int(8 + 14 * k), int(14 + 20 * k), int(30 + 40 * k), 255))
    im.alpha_composite(streaks((W, H), [(255, 60, 50), (255, 40, 40)], 130, 1, 0, H, (4, 14), (300, 1600), 3))
    im.alpha_composite(streaks((W, H), [(255, 240, 210), (255, 190, 90)], 110, 2, 0, H, (3, 12), (300, 1800), 3))
    glow = im.filter(ImageFilter.GaussianBlur(18))
    im = Image.blend(im, glow, 0.35)
    # darken behind the sign so it stands
    s = sign(1400, 380, "", "")
    t = fit("Fast German", 1000, WHITE, "Bold")
    s.alpha_composite(t, (70, (380 - t.height) // 2 - 4))
    ar = Image.new("RGBA", (190, 150))
    ad = ImageDraw.Draw(ar)
    ad.rectangle((0, 52, 110, 98), fill=WHITE + (255,))
    ad.polygon([(100, 0), (190, 75), (100, 150)], fill=WHITE + (255,))
    s.alpha_composite(ar, (1400 - 70 - 190, (380 - 150) // 2))
    paste_c(im, s, CX, CY)
    return im


# ---------- B: speed streaks ----------
def profile_B():
    im = Image.new("RGBA", (800, 800), BLACK + (255,))
    t1, t2 = fit("FAST", 560, YEL, "BlackItalic"), fit("GERMAN", 560, WHITE, "BlackItalic")
    total = t1.height + 30 + t2.height
    y0 = (800 - total) // 2
    im.alpha_composite(streaks((800, 800), [YEL], 14, 4, y0 + 20, y0 + t1.height - 20, (10, 24), (120, 300), 0), (-150, 0))
    im.alpha_composite(t1, ((800 - t1.width) // 2 + 30, y0))
    im.alpha_composite(t2, ((800 - t2.width) // 2 + 10, y0 + t1.height + 30))
    return im


def banner_B():
    im = Image.new("RGBA", (W, H), BLACK + (255,))
    im.alpha_composite(streaks((W, H), [(60, 60, 64), (90, 90, 96)], 160, 5, 0, H, (6, 20), (300, 1400), 2))
    im.alpha_composite(streaks((W, H), [YEL], 40, 6, 0, H, (6, 18), (300, 1200), 2))
    t1, t2 = fit("Fast", 560, YEL, "BlackItalic"), fit("German", 880, WHITE, "BlackItalic")
    row = Image.new("RGBA", (t1.width + 50 + t2.width, max(t1.height, t2.height)))
    row.alpha_composite(t1, (0, row.height - t1.height)); row.alpha_composite(t2, (t1.width + 50, row.height - t2.height))
    lead = streaks((900, row.height), [YEL, WHITE], 16, 7, 30, row.height - 30, (10, 26), (250, 800), 0)
    row = scale_to(row, 1380)
    lead = lead.resize((900, row.height))
    im.alpha_composite(lead, (CX - row.width // 2 - 900 + 40, CY - row.height // 2))
    paste_c(im, row, CX, CY)
    return im


# ---------- C: fast-forward chevrons ----------
def chevrons(h, n, col, gap=0.55, thick=0.36):
    w = int(h * (0.5 + gap * (n - 1)) + h * thick)
    im = Image.new("RGBA", (w, h))
    d = ImageDraw.Draw(im)
    for i in range(n):
        x = int(i * h * gap)
        t = int(h * thick)
        d.polygon([(x, 0), (x + t, 0), (x + t + h // 2, h // 2), (x + t, h), (x, h), (x + h // 2, h // 2)], fill=col + (255,))
    return im


def profile_C():
    im = Image.new("RGBA", (800, 800), RED + (255,))
    ch = chevrons(170, 2, WHITE)
    t1, t2 = fit("FAST", 420, WHITE), fit("GERMAN", 560, WHITE)
    row_w = ch.width + 30 + t1.width
    y = (800 - (t1.height + 34 + t2.height)) // 2
    x = (800 - row_w) // 2
    im.alpha_composite(ch, (x, y + (t1.height - ch.height) // 2)); im.alpha_composite(t1, (x + ch.width + 30, y))
    im.alpha_composite(t2, ((800 - t2.width) // 2, y + t1.height + 34))
    return im


def banner_C():
    im = Image.new("RGBA", (W, H), RED + (255,))
    # rows of faint chevrons racing to the right, filling the canvas
    rnd = random.Random(9)
    for y in range(-60, H, 150):
        x = rnd.randint(-300, 0)
        while x < W:
            ch = chevrons(110, 3, (255, 255, 255))
            ch.putalpha(ch.split()[3].point(lambda v: v * rnd.choice((22, 32, 44)) // 255))
            im.alpha_composite(ch, (x, y)); x += ch.width + rnd.randint(120, 380)
    ch = chevrons(260, 3, WHITE)
    t = fit("Fast German", 1020, WHITE)
    row = Image.new("RGBA", (ch.width + 60 + t.width, max(ch.height, t.height)))
    row.alpha_composite(ch, (0, (row.height - ch.height) // 2)); row.alpha_composite(t, (ch.width + 60, (row.height - t.height) // 2))
    paste_c(im, scale_to(row, 1400), CX, CY)
    return im


if __name__ == "__main__":
    P = [profile_A(), profile_B(), profile_C()]
    for k, p in zip("ABC", P):
        p.convert("RGB").save(os.path.join(OUT, f"profile_{k}.png"))
    round_preview(P, "profile_sizes.png")
    for k, f in zip("ABC", (banner_A, banner_B, banner_C)):
        banner_preview(f(), f"banner_{k}")
        print(k, flush=True)
