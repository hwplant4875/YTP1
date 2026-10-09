"""Raster the world land map (equirectangular, lat 82..-56) for the ORBIS banner slab top.
usage: python3 world_map_texture.py land_rings.json out.png"""
import json, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

LAT0, LAT1, LON0 = 82, -45, -180
W = 4096; H = round(W * (LAT0 - LAT1) / 360); SS = 2
w, h = W * SS, H * SS
P = lambda lo, la: ((lo - LON0) / 360 * w, (LAT0 - la) / (LAT0 - LAT1) * h)
area = lambda r: sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(r, r[1:] + r[:1])) / 2

rings = json.load(open(sys.argv[1]))
outer = max(rings, key=lambda r: abs(area(r)))
sign = 1 if area(outer) > 0 else -1
land = Image.new("L", (w, h)); d = ImageDraw.Draw(land)
for fill_outer in (True, False):
    for r in rings:
        if len(r) < 3 or (area(r) * sign > 0) != fill_outer: continue
        lons = [r[0][0]]
        for (a, _), (b, _) in zip(r, r[1:]):            # unwrap rings that cross the antimeridian
            step = b - a; step -= 360 * round(step / 360); lons.append(lons[-1] + step)
        for off in ((0,) if max(lons) - min(lons) < 300 and min(lons) >= -180 and max(lons) <= 180 else (-360, 0, 360)):
            d.polygon([P(lo + off, la) for lo, (_, la) in zip(lons, r)], fill=255 if fill_outer else 0)
land = land.resize((W, H), Image.LANCZOS)

rng = np.random.default_rng(5)
y = np.linspace(0, 1, H)[:, None, None]
ocean = np.array((13, 26, 44)) * (1 - y) + np.array((8, 17, 30)) * y + np.zeros((H, W, 3))
img = Image.fromarray(ocean.astype("uint8"))
g = ImageDraw.Draw(img)
for lon in range(-180, 181, 15):
    x = (lon - LON0) / 360 * W; g.line([(x, 0), (x, H)], fill=(30, 44, 64), width=1)
for lat in range(-45, 76, 15):
    yy = (LAT0 - lat) / (LAT0 - LAT1) * H; g.line([(0, yy), (W, yy)], fill=(30, 44, 64), width=1)
# drop shadow under land
sh = land.filter(ImageFilter.GaussianBlur(6)); sh = Image.fromarray((np.asarray(sh) * 0.5).astype("uint8"))
img.paste((0, 0, 0), (0, 3), sh)
# land: sandstone with grain and soft relief shading
lc = np.array((216, 204, 182), float) + rng.normal(0, 7, (H, W, 1))
relief = np.asarray(land.filter(ImageFilter.GaussianBlur(10))).astype(float) / 255
lc *= (0.9 + 0.1 * relief)[..., None]
landimg = Image.fromarray(np.clip(lc, 0, 255).astype("uint8"))
img.paste(landimg, (0, 0), land)
# coastline highlight
edge = land.filter(ImageFilter.FIND_EDGES).filter(ImageFilter.GaussianBlur(0.6))
img.paste((255, 246, 228), (0, 0), Image.fromarray((np.asarray(edge) * 0.6).astype("uint8")))
# warm glows at the hidden places
glow = Image.new("RGB", (W, H)); gd = ImageDraw.Draw(glow)
for lo, la in [(13.4, 52.5), (2.35, 48.85), (-0.12, 51.5), (12.5, 41.9), (30.1, 51.4), (8.2, 46.7), (28.97, 41.0)]:
    x, yy = (lo - LON0) / 360 * W, (LAT0 - la) / (LAT0 - LAT1) * H
    gd.ellipse((x - 5, yy - 5, x + 5, yy + 5), fill=(255, 200, 120))
glow = Image.fromarray(np.clip(np.asarray(glow.filter(ImageFilter.GaussianBlur(9))).astype(float) * 3 + np.asarray(glow) * 1.0, 0, 255).astype("uint8"))
img = Image.fromarray(np.clip(np.asarray(img).astype(int) + np.asarray(glow), 0, 255).astype("uint8"))
img.save(sys.argv[2])
