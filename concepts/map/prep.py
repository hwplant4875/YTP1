# Decode terrarium DEMs to float16 grids, build the route polyline with terrain heights.
import json, math, numpy as np
from PIL import Image
L = json.load(open('levels.json'))
LON0, LAT0, EXAG = 3.5, 41.75, 1.5
KX, KZ = 111.32 * math.cos(math.radians(LAT0)), 110.57
mer = lambda lat: math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))
dem = {}
for n, l in L.items():
    a = np.asarray(Image.open(f'data/{n}_dem.png').convert('RGB')).astype(np.float32)
    h = a[..., 0] * 256 + a[..., 1] + a[..., 2] / 256 - 32768
    dem[n] = h
    h.astype(np.float16).tofile(f'data/{n}_dem.f16')
    l['w'], l['h'] = h.shape[1], h.shape[0]
    print(n, h.shape, h.min(), h.max())
json.dump(L, open('data/levels_meta.json', 'w'))

def height(lon, lat):
    for n in ['near', 'alps', 'base']:
        lon0, lat0, lon1, lat1 = L[n]['box']
        if lon0 <= lon <= lon1 and lat0 <= lat <= lat1:
            h = dem[n]; H, W = h.shape
            u = (lon - lon0) / (lon1 - lon0) * (W - 1); v = (mer(lat1) - mer(lat)) / (mer(lat1) - mer(lat0)) * (H - 1)
            i, j = int(v), int(u); fv, fu = v - i, u - j
            i1, j1 = min(i + 1, H - 1), min(j + 1, W - 1)
            return float((h[i, j] * (1 - fu) + h[i, j1] * fu) * (1 - fv) + (h[i1, j] * (1 - fu) + h[i1, j1] * fu) * fv)
    return 0.0

# waypoints: name, lon, lat, label (None = shaping point). Route after the Rhone follows the
# Durance / Guil valleys to the Col de la Traversette (one of the leading candidate passes).
W = [("New Carthage", -0.986, 37.600, "NEW CARTHAGE"), ("", -0.75, 38.30, None), ("", -0.40, 39.45, None),
     ("", -0.27, 39.68, None), ("", 0.05, 40.25, None), ("Ebro", 0.52, 40.81, "EBRO"), ("", 1.25, 41.13, None),
     ("", 2.05, 41.50, None), ("", 2.82, 41.98, None), ("Pyrenees", 2.865, 42.465, "PYRENEES"),
     ("", 2.90, 42.70, None), ("", 3.00, 43.18, None), ("", 3.55, 43.45, None), ("", 4.36, 43.84, None),
     ("Rhone", 4.72, 44.02, "RHÔNE"), ("", 5.05, 43.92, None), ("", 5.55, 43.95, None), ("", 5.94, 44.20, None),
     ("", 6.20, 44.43, None), ("", 6.50, 44.57, None), ("", 6.64, 44.66, None), ("", 6.80, 44.72, None),
     ("", 6.92, 44.765, None), ("", 6.99, 44.745, None),
     ("Traversette", 7.0617, 44.6997, "COL DE LA TRAVERSETTE"), ("", 7.12, 44.705, None), ("", 7.16, 44.70, None),
     ("", 7.29, 44.68, None), ("", 7.49, 44.645, None), ("", 7.60, 44.85, None), ("Taurini", 7.686, 45.07, "TAURINI · TURIN")]
pts, cum, marks = [], [0.0], []
# densify each segment with a smooth Catmull-Rom curve, sampled every ~0.25 km
ll = np.array([(w[1], w[2]) for w in W])
def cr(p0, p1, p2, p3, t):
    return 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3)
for k in range(len(W) - 1):
    p0, p1, p2, p3 = ll[max(k - 1, 0)], ll[k], ll[k + 1], ll[min(k + 2, len(W) - 1)]
    segkm = math.hypot((p2[0] - p1[0]) * KX, (p2[1] - p1[1]) * KZ)
    n = max(4, int(segkm / 0.25))
    if W[k][3]: marks.append((W[k][0], W[k][3], len(pts)))
    for i in range(n):
        lon, lat = cr(p0, p1, p2, p3, i / n)
        pts.append((lon, lat))
pts.append(tuple(ll[-1])); marks.append((W[-1][0], W[-1][3], len(pts) - 1))
xyz = []
for lon, lat in pts:
    h = max(height(lon, lat), 0.0)
    xyz.append(((lon - LON0) * KX, h / 1000 * EXAG, -(lat - LAT0) * KZ))
xyz = np.array(xyz)
d = np.r_[0, np.cumsum(np.linalg.norm(np.diff(xyz[:, [0, 2]], axis=0), axis=1))]
elev = [max(height(lon, lat), 0) for lon, lat in pts]
print('route km (2D)', d[-1], 'points', len(xyz))
json.dump({'LON0': LON0, 'LAT0': LAT0, 'EXAG': EXAG, 'KX': KX, 'KZ': KZ,
           'xyz': np.round(xyz, 4).tolist(), 'frac': np.round(d / d[-1], 6).tolist(), 'elev': np.round(elev).tolist(),
           'marks': [{'id': m[0], 'label': m[1], 'i': m[2], 'frac': float(d[m[2]] / d[-1])} for m in marks]},
          open('data/route.json', 'w'))
for m in marks: print(m, round(d[m[2]] / d[-1], 4), round(elev[m[2]]))
