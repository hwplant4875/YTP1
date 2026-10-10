"""Banner round 6 (2026-10-10): the user picked the road-marking profile; the banner gets three richer takes on
'FAST GERMAN painted on the Autobahn': 1 day, top-down; 2 night, top-down with headlights; 3 driver's-eye perspective."""
import os, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from branding_v4 import W, H, CX, CY, SAFE, WHITE, YEL, fit, streaks, banner_preview
from branding_v5 import worn, dashes
import branding_v4
OUT = "/mnt/project-files/fast_german/branding/round6"
os.makedirs(OUT, exist_ok=True)
branding_v4.OUT = OUT
PAINT = (238, 238, 232)


def asphalt(w, h, base=(52, 54, 58), seed=0, night=False):
    rnd = np.random.default_rng(seed)
    n = rnd.normal(0, 1, (h, w)) * (6 if night else 10)
    big = np.array(Image.fromarray(((rnd.random((h // 60 + 2, w // 60 + 2))) * 255).astype("uint8"))
                   .resize((w, h), Image.BICUBIC), float) / 255 - 0.5
    img = np.array(base, float)[None, None, :] + (n + big * 14)[..., None]
    # tyre tracks: two darker bands per lane
    for y0 in (190, 470, 960, 1240):
        img[y0:y0 + 90] *= 0.9
    return Image.fromarray(np.clip(img, 0, 255).astype("uint8")).convert("RGBA")


def lane_arrow(w, h, col=PAINT):
    im = Image.new("RGBA", (w, h))
    d = ImageDraw.Draw(im)
    d.rectangle((0, int(h * .38), int(w * .7), int(h * .62)), fill=col + (255,))
    d.polygon([(int(w * .62), 0), (w, h // 2), (int(w * .62), h)], fill=col + (255,))
    return im


def markings(im, col=PAINT, glow=False):
    d = ImageDraw.Draw(im)
    for y in (70, H - 100):                                   # solid edge lines
        d.rectangle((0, y, W, y + 30), fill=col + (255,))
    for y in (CY - 330, CY + 300):                           # dashed lane lines (Autobahn: 6 m dash, 12 m gap)
        im.alpha_composite(worn(dashes(W, 26, 300, 600, col), y), (-120 if y < CY else 180, y))
    for x, y in ((260, 300), (2060, 300), (700, 1130), (1700, 1130)):   # lane arrows, outside the safe area
        im.alpha_composite(worn(lane_arrow(330, 120, col), x + y), (x, y - 60))
    if glow:
        g = im.filter(ImageFilter.GaussianBlur(14))
        im.alpha_composite(Image.blend(Image.new("RGBA", im.size), g, 0.0))


def title(col=PAINT, width=1340, height=310):
    t = fit("FAST GERMAN", width, col).resize((width, height))
    w, h = t.size                                   # lean forward, like the profile
    t = t.transform((w + int(h * .22), h), Image.AFFINE, (1, .22, -h * .22, 0, 1, 0), Image.BICUBIC)
    return worn(t, 7, 0.1)


def day():
    im = asphalt(W, H, seed=1)
    markings(im)
    im.alpha_composite(streaks((W, H), [(255, 255, 255)], 40, 8, 0, H, (3, 8), (400, 1500), 3))
    t = title()
    sh = Image.new("RGBA", t.size, (0, 0, 0, 0)); sh.putalpha(t.split()[3].point(lambda v: v // 4))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(3)), (CX - t.width // 2 + 4, CY - t.height // 2 + 6))
    im.alpha_composite(t, (CX - t.width // 2, CY - t.height // 2))
    return vignette(im, 0.35)


def night():
    im = asphalt(W, H, base=(22, 24, 30), seed=2, night=True)
    paint = Image.new("RGBA", (W, H))
    markings(paint, (250, 250, 240))
    t = title((250, 250, 240))
    paint.alpha_composite(t, (CX - t.width // 2, CY - t.height // 2))
    # headlight pool from the left lights the paint: brighter near the centre band
    yy, xx = np.mgrid[0:H, 0:W]
    light = np.exp(-((yy - CY) / 520.0) ** 2) * (0.45 + 0.55 * np.clip(xx / W * 1.4, 0, 1))
    a = np.array(paint.split()[3], float) * (0.35 + 0.65 * light)
    paint.putalpha(Image.fromarray(a.astype("uint8")))
    glow = paint.filter(ImageFilter.GaussianBlur(10))
    im.alpha_composite(glow); im.alpha_composite(paint)
    im.alpha_composite(streaks((W, H), [(255, 60, 50)], 45, 1, 0, H, (4, 12), (500, 1700), 3))
    im.alpha_composite(streaks((W, H), [(255, 236, 200)], 45, 2, 0, H, (4, 12), (500, 1700), 3))
    return vignette(im, 0.5)


def perspective():
    """Driver's view: dusk sky, Autobahn running to the horizon, text painted on the road and foreshortened."""
    hz = 470
    im = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(im)
    for y in range(hz):
        k = y / hz
        d.line((0, y, W, y), fill=(int(255 - 120 * (1 - k)), int(150 - 60 * (1 - k)), int(90 + 40 * (1 - k)), 255))
    # flat road texture, then warp it into perspective
    road = asphalt(W, 2400, seed=3)
    rd = ImageDraw.Draw(road)
    for x in (300, W - 330):
        rd.rectangle((x, 0, x + 30, 2400), fill=PAINT + (255,))
    for x in (W // 3, 2 * W // 3):
        for y in range(0, 2400, 420):
            rd.rectangle((x - 13, y, x + 13, y + 220), fill=PAINT + (255,))
    t = fit("FAST GERMAN", 1500, PAINT).resize((1500, 900))   # road text is drawn tall so it reads foreshortened
    road.alpha_composite(worn(t, 7, 0.08), ((W - 1500) // 2, 1180))
    # perspective: road rows y_src in [0,2400] map to screen rows [hz, H]; width shrinks toward the horizon
    out = np.zeros((H, W, 4), np.uint8)
    src = np.array(road)
    for y in range(hz + 1, H):
        z = (y - hz) / (H - hz)                     # 0 at horizon, 1 at bottom
        sy = int(np.clip(2400 * (1 - (0.06 / (z + 0.06) - 0.06 / 1.06) / (1 - 0.06 / 1.06)), 0, 2399))
        half = int(W * (0.04 + 0.96 * z) * 1.2)
        xs = np.linspace(0, W - 1, 2 * half).astype(int)
        x0 = CX - half
        lo, hi = max(0, x0), min(W, x0 + 2 * half)
        out[y, lo:hi] = src[sy, xs[lo - x0:hi - x0]]
    roadim = Image.fromarray(out)
    im.alpha_composite(roadim)
    im = Image.alpha_composite(Image.new("RGBA", (W, H), (60, 70, 90, 255)), im)
    return vignette(im, 0.3)


def vignette(im, s):
    yy, xx = np.mgrid[0:H, 0:W]
    v = 1 - s * (((xx - CX) / CX) ** 2 + ((yy - CY) / CY) ** 2) / 2
    a = (np.array(im.convert("RGB"), float) * v[..., None]).clip(0, 255).astype("uint8")
    return Image.fromarray(a).convert("RGBA")


if __name__ == "__main__":
    for k, f in (("1_day", day), ("2_night", night)):
        banner_preview(f(), "banner_" + k)
        print(k, flush=True)
