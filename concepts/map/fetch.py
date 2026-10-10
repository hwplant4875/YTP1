# Fetch and stitch Web-Mercator tiles (Sentinel-2 cloudless 2016 imagery, AWS terrarium elevation) for a lon/lat box.
import math, os, sys, io, json, concurrent.futures as cf, urllib.request
from PIL import Image
IMG = 'https://tiles.maps.eox.at/wmts/1.0.0/s2cloudless_3857/default/g/{z}/{y}/{x}.jpg'
DEM = 'https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png'
def tx(lon, z): return (lon + 180) / 360 * 2**z
def ty(lat, z): r = math.radians(lat); return (1 - math.log(math.tan(r) + 1 / math.cos(r)) / math.pi) / 2 * 2**z
def get(url):
    for i in range(5):
        try: return urllib.request.urlopen(url, timeout=30).read()
        except Exception as e: err = e
    raise err
def stitch(tpl, z, box, out, ts=256):
    lon0, lat0, lon1, lat1 = box
    x0, x1 = int(tx(lon0, z)), int(tx(lon1, z)); y0, y1 = int(ty(lat1, z)), int(ty(lat0, z))
    im = Image.new('RGB', ((x1 - x0 + 1) * ts, (y1 - y0 + 1) * ts))
    jobs = [(x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)]
    with cf.ThreadPoolExecutor(16) as ex:
        for (x, y), b in zip(jobs, ex.map(lambda j: get(tpl.format(z=z, x=j[0], y=j[1])), jobs)):
            im.paste(Image.open(io.BytesIO(b)).convert('RGB'), ((x - x0) * ts, (y - y0) * ts))
    # crop exactly to box
    px = lambda lon: (tx(lon, z) - x0) * ts; py = lambda lat: (ty(lat, z) - y0) * ts
    im = im.crop((round(px(lon0)), round(py(lat1)), round(px(lon1)), round(py(lat0))))
    im.save(out, quality=92) if out.endswith('.jpg') else im.save(out)
    print(out, im.size, len(jobs), 'tiles')
levels = json.load(open('levels.json'))
for name, L in levels.items():
    stitch(IMG, L['img'], L['box'], f'data/{name}_img.jpg')
    stitch(DEM, L['dem'], L['box'], f'data/{name}_dem.png')
