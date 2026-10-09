"""ORBIS minimal world-map banners (2560x1440, no text). The whole map sits inside the 1546x423 area
every device shows. Variants: solid silhouette and dot grid.
usage: python3 minimal_map_banner.py land_rings.json OUT_DIR"""
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

NAVY, CREAM, AMBER = (11, 17, 30), (228, 220, 208), (238, 160, 70)
LAT0, LAT1 = 80, -57
BW, BH = 2560, 1440
MAP_H = 360                                    # map height inside the 423px safe band
MAP_W = round(MAP_H * 360 / (LAT0 - LAT1))
X0, Y0 = (BW - MAP_W) // 2, (BH - MAP_H) // 2
area = lambda r: sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(r, r[1:] + r[:1])) / 2


def land_mask(rings, w, h):
    P = lambda lo, la: ((lo + 180) / 360 * w, (LAT0 - la) / (LAT0 - LAT1) * h)
    sign = 1 if area(max(rings, key=lambda r: abs(area(r)))) > 0 else -1
    m = Image.new("L", (w, h)); d = ImageDraw.Draw(m)
    for outer in (True, False):
        for r in rings:
            if len(r) < 3 or (area(r) * sign > 0) != outer: continue
            lons = [r[0][0]]
            for (a, _), (b, _) in zip(r, r[1:]):
                st = b - a; st -= 360 * round(st / 360); lons.append(lons[-1] + st)
            offs = (0,) if min(lons) >= -180 and max(lons) <= 180 else (-360, 0, 360)
            for off in offs:
                d.polygon([P(lo + off, la) for lo, (_, la) in zip(lons, r)], fill=255 if outer else 0)
    return m


def base():
    y, x = np.mgrid[0:BH, 0:BW]
    r = np.clip(np.hypot((x - BW / 2) / BW, (y - BH / 2) / BH) * 1.5, 0, 1)[..., None]
    a = np.array((14, 21, 36)) * (1 - r) + np.array((8, 12, 22)) * r
    a = a + np.random.default_rng(4).normal(0, 1.6, (BH, BW, 1))
    return Image.fromarray(np.clip(a, 0, 255).astype("uint8"))


def main(src, out):
    rings = json.load(open(src))
    SS = 4
    m = land_mask(rings, MAP_W * SS, MAP_H * SS).resize((MAP_W, MAP_H), Image.LANCZOS)
    # solid silhouette
    img = base(); img.paste(CREAM, (X0, Y0), m)
    img.save(os.path.join(out, "banner_orbis_minimal_solid.jpg"), quality=95)
    # dot grid: one dot per cell where the cell is mostly land; Europe's hidden places in amber
    img = base(); d = ImageDraw.Draw(img)
    cell = 7; rad = 2.1
    a = np.asarray(m).astype(float) / 255
    for cy in range(0, MAP_H - cell + 1, cell):
        for cx in range(0, MAP_W - cell + 1, cell):
            if a[cy:cy + cell, cx:cx + cell].mean() > 0.45:
                x, y = X0 + cx + cell / 2, Y0 + cy + cell / 2
                d.ellipse((x - rad, y - rad, x + rad, y + rad), fill=CREAM)
    P = lambda lo, la: (X0 + (lo + 180) / 360 * MAP_W, Y0 + (LAT0 - la) / (LAT0 - LAT1) * MAP_H)
    for lo, la in [(13.4, 52.5), (2.35, 48.85), (-0.12, 51.5), (12.5, 41.9), (30.1, 51.4), (8.2, 46.7)]:
        x, y = P(lo, la); x = X0 + (round((x - X0) / cell - 0.5) + 0.5) * cell; y = Y0 + (round((y - Y0) / cell - 0.5) + 0.5) * cell
        d.ellipse((x - rad - 0.4, y - rad - 0.4, x + rad + 0.4, y + rad + 0.4), fill=AMBER)
    img.save(os.path.join(out, "banner_orbis_minimal_dots.jpg"), quality=95)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
