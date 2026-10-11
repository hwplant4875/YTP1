"""Download AWS terrarium elevation tiles covering France and neighbours (zoom 8) into a cache dir."""
import math, os, sys, concurrent.futures as cf, urllib.request
Z = 8
LON0, LON1, LAT0, LAT1 = -6.5, 11.0, 40.6, 52.0
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
def tx(lon): return (lon + 180) / 360 * 2 ** Z
def ty(lat): r = math.radians(lat); return (1 - math.log(math.tan(r) + 1 / math.cos(r)) / math.pi) / 2 * 2 ** Z
jobs = [(x, y) for x in range(int(tx(LON0)), int(tx(LON1)) + 1) for y in range(int(ty(LAT1)), int(ty(LAT0)) + 1)]
def get(xy):
    x, y = xy; p = f"{out}/{Z}_{x}_{y}.png"
    if not os.path.exists(p):
        urllib.request.urlretrieve(f"https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{Z}/{x}/{y}.png", p)
    return p
with cf.ThreadPoolExecutor(16) as ex: print(len(list(ex.map(get, jobs))), "tiles")
