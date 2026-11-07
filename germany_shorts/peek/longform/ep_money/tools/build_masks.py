"""Rasterize Natural Earth land polygons (public domain) into equirectangular
land masks for the iso globe.  Usage: python3 -I build_masks.py <ne_dir> <out_dir>
Writes land_global.png (8192x4096) and land_ne.png (NE United States, 0.004 deg/px)."""
import json, sys
from PIL import Image, ImageDraw

ne_dir, out_dir = sys.argv[1], sys.argv[2]

def rings(path):
    gj = json.load(open(path))
    for f in gj["features"]:
        g = f["geometry"]
        polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        for poly in polys:
            yield poly

def raster(land_path, lake_path, lon0, lon1, lat0, lat1, W, H, ss=2):
    w, h = W * ss, H * ss
    im = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(im)
    sx, sy = w / (lon1 - lon0), h / (lat1 - lat0)
    def pts(ring):
        return [((lo - lon0) * sx, (lat1 - la) * sy) for lo, la in ring]
    def inside(ring):
        xs = [p[0] for p in ring]; ys = [p[1] for p in ring]
        return not (max(xs) < lon0 or min(xs) > lon1 or max(ys) < lat0 or min(ys) > lat1)
    for poly in rings(land_path):
        if not inside(poly[0]):
            continue
        d.polygon(pts(poly[0]), fill=255)
        for hole in poly[1:]:
            d.polygon(pts(hole), fill=0)
    if lake_path:
        for poly in rings(lake_path):
            if inside(poly[0]):
                d.polygon(pts(poly[0]), fill=0)
    return im.resize((W, H), Image.Resampling.BOX)

g = raster(f"{ne_dir}/ne_10m_land.geojson", f"{ne_dir}/ne_50m_lakes.geojson", -180, 180, -90, 90, 8192, 4096)
g.save(f"{out_dir}/land_global.png", optimize=True)
r = raster(f"{ne_dir}/ne_10m_land.geojson", f"{ne_dir}/ne_50m_lakes.geojson", -82, -62, 32, 50, 5000, 4500)
r.save(f"{out_dir}/land_ne.png", optimize=True)
print("ok", g.size, r.size)
