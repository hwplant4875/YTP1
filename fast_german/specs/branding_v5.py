"""Branding round 5 (2026-10-10): the user liked the Autobahn idea from round 4. Three takes on it:
1 'A1' Autobahn sign (A1 is both a motorway number and the first CEFR level), 2 the German no-speed-limit sign,
3 'FAST GERMAN' painted on the asphalt like a road marking."""
import os, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from branding_v4 import (W, H, CX, CY, SAFE, BLUE, WHITE, BLACK, YEL, F, text, fit, shadow, paste_c, scale_to,
                         streaks, round_preview, banner_preview)
import branding_v4
OUT = "/mnt/project-files/fast_german/branding/round5"
os.makedirs(OUT, exist_ok=True)
branding_v4.OUT = OUT
ASPHALT = (44, 46, 50)


def night():
    im = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(im)
    for y in range(H):
        k = y / H
        d.line((0, y, W, y), fill=(int(8 + 14 * k), int(14 + 20 * k), int(30 + 40 * k), 255))
    im.alpha_composite(streaks((W, H), [(255, 60, 50), (255, 40, 40)], 130, 1, 0, H, (4, 14), (300, 1600), 3))
    im.alpha_composite(streaks((W, H), [(255, 240, 210), (255, 190, 90)], 110, 2, 0, H, (3, 12), (300, 1800), 3))
    return Image.blend(im, im.filter(ImageFilter.GaussianBlur(18)), 0.35)


def asphalt(w, h, seed=0):
    rnd = np.random.default_rng(seed)
    n = rnd.normal(0, 1, (h, w))
    base = np.array(ASPHALT, float)[None, None, :] + n[..., None] * 9
    im = Image.fromarray(np.clip(base, 0, 255).astype("uint8")).convert("RGBA")
    return im.filter(ImageFilter.GaussianBlur(0.6))


def worn(el, seed=1, amount=0.22):
    """Road-paint wear: knock random speckles out of the alpha."""
    a = np.array(el.split()[3], float)
    rnd = np.random.default_rng(seed)
    holes = rnd.random(a.shape) < amount
    holes = np.array(Image.fromarray((holes * 255).astype("uint8")).filter(ImageFilter.GaussianBlur(1.2))) > 90
    a[holes] *= 0.35
    el = el.copy(); el.putalpha(Image.fromarray(a.astype("uint8")))
    return el


def shield(h, label="A1"):
    """Autobahn route shield: blue, white rim, white number (proportions of the real sign)."""
    w = int(h * 1.45)
    im = Image.new("RGBA", (w, h))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), int(h * 0.22), fill=WHITE + (255,))
    b = int(h * 0.07)
    d.rounded_rectangle((b, b, w - 1 - b, h - 1 - b), int(h * 0.17), fill=BLUE + (255,))
    t = fit(label, int(w * 0.62), WHITE, "Bold")
    if t.height > h * 0.62:
        t = scale_to(t, int(t.width * h * 0.62 / t.height))
    im.alpha_composite(t, ((w - t.width) // 2, (h - t.height) // 2))
    return im


def blue_sign(w, h):
    im = Image.new("RGBA", (w, h))
    d = ImageDraw.Draw(im)
    r = int(min(w, h) * 0.09)
    d.rounded_rectangle((0, 0, w - 1, h - 1), r, fill=BLUE + (255,))
    b = int(min(w, h) * 0.035)
    d.rounded_rectangle((b, b, w - 1 - b, h - 1 - b), r - b // 2, outline=WHITE + (255,), width=max(6, b // 2))
    return im


def arrow(w, h, col=WHITE):
    im = Image.new("RGBA", (w, h))
    d = ImageDraw.Draw(im)
    d.rectangle((0, int(h * 0.35), int(w * 0.58), int(h * 0.65)), fill=col + (255,))
    d.polygon([(int(w * 0.52), 0), (w, h // 2), (int(w * 0.52), h)], fill=col + (255,))
    return im


def nolimit(d_px, rim=True):
    """German 'end of all restrictions' sign: white disc, five thin black diagonal bars."""
    s = d_px * 3
    im = Image.new("RGBA", (s, s))
    dr = ImageDraw.Draw(im)
    dr.ellipse((0, 0, s - 1, s - 1), fill=(120, 120, 124, 255) if rim else WHITE + (255,))
    k = int(s * 0.025)
    dr.ellipse((k, k, s - 1 - k, s - 1 - k), fill=WHITE + (255,))
    bars = Image.new("L", (s, s), 0)
    bd = ImageDraw.Draw(bars)
    for i in range(-2, 3):
        o = i * s * 0.075
        bd.line((s * 0.18 + o, s * 0.82 + o, s * 0.82 + o, s * 0.18 + o), fill=255, width=int(s * 0.03))
    m = Image.new("L", (s, s), 0)
    ImageDraw.Draw(m).ellipse((k * 2, k * 2, s - 1 - k * 2, s - 1 - k * 2), fill=255)
    bars = Image.fromarray(np.minimum(np.array(bars), np.array(m)))
    im.paste(Image.new("RGBA", (s, s), (30, 30, 32, 255)), (0, 0), bars)
    return im.resize((d_px, d_px), Image.LANCZOS)


def halo(el, r):
    """White outline so black type stays readable over the sign's bars."""
    pad = Image.new("RGBA", (el.width + 2 * r, el.height + 2 * r))
    pad.alpha_composite(el, (r, r))
    a = pad.split()[3].filter(ImageFilter.MaxFilter(2 * r + 1))
    out = Image.new("RGBA", pad.size, WHITE + (0,)); out.putalpha(a); out.alpha_composite(pad)
    return out


# ---------- 1: A1 sign ----------
def profile_1():
    im = Image.new("RGBA", (800, 800), BLUE + (255,))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((125, 125, 675, 675), 56, outline=WHITE + (255,), width=16)
    sh = shield(120)
    t1, t2 = fit("FAST", 390, WHITE), fit("GERMAN", 390, WHITE)
    y = (800 - (sh.height + 26 + t1.height + 24 + t2.height)) // 2
    for el, gap in ((sh, 26), (t1, 24), (t2, 0)):
        im.alpha_composite(el, ((800 - el.width) // 2, y)); y += el.height + gap
    return im


def banner_1():
    im = night()
    d = ImageDraw.Draw(im)
    # gantry: two posts and a beam across the top of the safe area
    for x in (CX - 860, CX + 840):
        d.rectangle((x, CY - 260, x + 22, H), fill=(70, 74, 82, 255))
    d.rectangle((CX - 880, CY - 262, CX + 880, CY - 240), fill=(70, 74, 82, 255))
    s = blue_sign(1420, 380)
    sh = shield(170)
    t = fit("Fast German", 760, WHITE, "Bold")
    a = arrow(150, 124)
    x = 60
    s.alpha_composite(sh, (x, (380 - sh.height) // 2)); x += sh.width + 50
    s.alpha_composite(t, (x, (380 - t.height) // 2 - 4))
    s.alpha_composite(a, (1420 - 60 - a.width, (380 - a.height) // 2))
    paste_c(im, s, CX, CY + 10)
    # next exits, desktop only: the levels ahead
    for lab, km, cx in (("A2", "2 km", 250), ("B1", "5 km", W - 250)):
        ss = blue_sign(380, 180)
        sh2 = shield(100, lab)
        kt = fit(km, 130, WHITE, "Bold")
        ss.alpha_composite(sh2, (32, (180 - sh2.height) // 2)); ss.alpha_composite(kt, (380 - 32 - kt.width, (180 - kt.height) // 2))
        paste_c(im, ss, cx, CY + 10)
    return im


# ---------- 2: no speed limit ----------
def profile_2():
    im = Image.new("RGBA", (800, 800), (24, 26, 30, 255))
    im.alpha_composite(nolimit(740), (30, 30))
    t1, t2 = fit("FAST", 470, BLACK), fit("GERMAN", 470, BLACK)
    t1, t2 = (halo(t, 16) for t in (t1, t2))
    y = (800 - (t1.height + 6 + t2.height)) // 2
    im.alpha_composite(t1, ((800 - t1.width) // 2, y)); im.alpha_composite(t2, ((800 - t2.width) // 2, y + t1.height + 6))
    return im


def banner_2():
    im = night()
    sg = nolimit(380)
    t = fit("Fast German", 940, WHITE, "Bold")
    row = Image.new("RGBA", (sg.width + 70 + t.width, max(sg.height, t.height)))
    row.alpha_composite(sg, (0, (row.height - sg.height) // 2)); row.alpha_composite(t, (sg.width + 70, (row.height - t.height) // 2))
    paste_c(im, scale_to(row, 1440), CX, CY)
    return im


# ---------- 3: road marking ----------
def dashes(w, h, dash, gap, col=WHITE):
    im = Image.new("RGBA", (w, h))
    d = ImageDraw.Draw(im)
    for x in range(0, w, dash + gap):
        d.rectangle((x, 0, x + dash, h), fill=col + (255,))
    return im


def profile_3():
    im = asphalt(800, 800, 3)
    t1 = fit("FAST", 420, WHITE).resize((420, 250))
    t2 = fit("GERMAN", 470, WHITE).resize((470, 190))
    dl = dashes(800, 18, 70, 50, YEL)
    y = (800 - (t1.height + 30 + t2.height)) // 2
    im.alpha_composite(worn(dl, 5), (0, y - 70)); im.alpha_composite(worn(dl, 6), (-60, y + t1.height + 30 + t2.height + 52))
    im.alpha_composite(worn(t1, 1, 0.12), ((800 - t1.width) // 2, y))
    im.alpha_composite(worn(t2, 2, 0.12), ((800 - t2.width) // 2, y + t1.height + 30))
    return im


def banner_3():
    im = asphalt(W, H, 4)
    d = ImageDraw.Draw(im)
    # lanes: solid edge lines and dashed lane dividers across the whole width
    for y in (90, H - 110):
        d.rectangle((0, y, W, y + 24), fill=(235, 235, 235, 255))
    for y in (CY - 300, CY + 280):
        im.alpha_composite(worn(dashes(W, 22, 260, 180), y), (0, y))
    im.alpha_composite(streaks((W, H), [(255, 255, 255)], 50, 8, 0, H, (4, 10), (400, 1400), 3))
    t = fit("FAST GERMAN", 1400, WHITE).resize((1400, 300))
    paste_c(im, worn(t, 7, 0.12), CX, CY, sh=False)
    return im


if __name__ == "__main__":
    P = [profile_1(), profile_2(), profile_3()]
    for k, p in zip("123", P):
        p.convert("RGB").save(os.path.join(OUT, f"profile_{k}.png"))
    round_preview(P, "profile_sizes.png")
    for k, f in zip("123", (banner_1, banner_2, banner_3)):
        banner_preview(f(), f"banner_{k}")
        print(k, flush=True)
