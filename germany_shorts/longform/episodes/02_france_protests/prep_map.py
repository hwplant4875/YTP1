"""Bake the data for scenes/france_map.js.

inputs (argv[1] = folder holding the downloads):
  tiles/8_x_y.png                      AWS terrain tiles (terrarium encoding), from fetch_tiles.py
  ne_10m_admin_0_countries.geojson     Natural Earth (public domain): coastline of France + neighbours
  ne_10m_admin_0_boundary_lines_land   Natural Earth: land borders
  ne_10m_rivers_lake_centerlines       Natural Earth: main rivers
  fr_regions.geojson                   gregoiredavid/france-geojson (IGN/INSEE derived, Licence Ouverte): 13 regions
  lycees.csv                           data.education.gouv.fr annuaire (Licence Ouverte): every lycée with lat/lon
outputs (episodes/02_france_protests/map/):
  height.bin   Float32 grid GW x GH of surface heights in scene units (row 0 = north)
  color.jpg    baked hillshade albedo
  lines.json   draped polylines [x,y,z,...] (coast, border, regions, neighbours, rivers)
  places.json  cities (ignite day, 6 Oct police count), lycées (x,z, ignite day, red/orange flag), spread timeline
Projection: x = (lon-LON_C)*cos(LAT_C)*K, z = -(lat-LAT_C)*K, K = 11.132 units per degree (1 unit = 10 km).
"""
import json, math, sys, os, glob, csv, random
import numpy as np
from PIL import Image, ImageFilter, ImageDraw
from shapely.geometry import shape, mapping, box, LineString, MultiLineString, Point
from shapely.ops import unary_union, linemerge

SRC = sys.argv[1]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'map')
os.makedirs(OUT, exist_ok=True)
LON0, LON1, LAT0, LAT1 = -6.5, 11.0, 40.6, 52.0
LON_C, LAT_C, K = 2.5, 46.3, 11.132
CL = math.cos(math.radians(LAT_C))
def P(lon, lat): return ((lon - LON_C) * CL * K, -(lat - LAT_C) * K)
W_U, H_U = (LON1 - LON0) * CL * K, (LAT1 - LAT0) * K
X0, Z0 = P(LON0, LAT1)            # north-west corner

# ------------------------------------------------------------ elevation, resampled to an equirectangular grid
Z = 8
def tx(lon): return (lon + 180) / 360 * 2 ** Z
def ty(lat): r = np.radians(lat); return (1 - np.log(np.tan(r) + 1 / np.cos(r)) / np.pi) / 2 * 2 ** Z
xs = range(int(tx(LON0)), int(tx(LON1)) + 1); ys = range(int(ty(LAT1)), int(ty(LAT0)) + 1)
mos = np.zeros((len(ys) * 256, len(xs) * 256), np.float32)
for j, y in enumerate(ys):
    for i, x in enumerate(xs):
        a = np.asarray(Image.open(f'{SRC}/tiles/{Z}_{x}_{y}.png').convert('RGB'), np.float32)
        mos[j * 256:(j + 1) * 256, i * 256:(i + 1) * 256] = a[..., 0] * 256 + a[..., 1] + a[..., 2] / 256 - 32768
def sample(lon, lat):
    px = (tx(lon) - xs[0]) * 256 - 0.5; py = (ty(lat) - ys[0]) * 256 - 0.5
    x0 = np.clip(np.floor(px).astype(int), 0, mos.shape[1] - 2); y0 = np.clip(np.floor(py).astype(int), 0, mos.shape[0] - 2)
    fx = px - x0; fy = py - y0
    return (mos[y0, x0] * (1 - fx) * (1 - fy) + mos[y0, x0 + 1] * fx * (1 - fy) + mos[y0 + 1, x0] * (1 - fx) * fy + mos[y0 + 1, x0 + 1] * fx * fy)

TW = 4096; TH = int(round(TW * H_U / W_U))
lon = np.linspace(LON0, LON1, TW)[None, :].repeat(TH, 0)
lat = np.linspace(LAT1, LAT0, TH)[:, None].repeat(TW, 1)
elev = sample(lon, lat)
print('tex', TW, TH, 'elev', elev.min(), elev.max())

# ------------------------------------------------------------ vector data
countries = {f['properties']['ADM0_A3']: shape(f['geometry']).buffer(0) for f in json.load(open(f'{SRC}/ne_10m_admin_0_countries.geojson'))['features']}
bb = box(LON0, LAT0, LON1, LAT1)
land = unary_union([g.intersection(bb) for g in countries.values() if g.intersects(bb)])
france = countries['FRA'].intersection(box(-6, 41, 10, 52)).buffer(0)    # metropolitan France + Corsica
def to_px(g):
    """yield pixel rings of a polygon geometry"""
    polys = [g] if g.geom_type == 'Polygon' else list(g.geoms)
    for p in polys:
        for ring in [p.exterior, *p.interiors]:
            c = np.asarray(ring.coords)
            yield [((x - LON0) / (LON1 - LON0) * TW, (LAT1 - y) / (LAT1 - LAT0) * TH) for x, y in c], ring is p.exterior
def mask_of(g, scale=1):
    im = Image.new('L', (TW * scale, TH * scale), 0); d = ImageDraw.Draw(im)
    polys = [g] if g.geom_type == 'Polygon' else [q for q in g.geoms if q.geom_type == 'Polygon']
    for p in polys:
        d.polygon([(x * scale, y * scale) for x, y in next(to_px(p))[0]], fill=255)
        for ring in p.interiors:
            c = np.asarray(ring.coords)
            d.polygon([((x - LON0) / (LON1 - LON0) * TW * scale, (LAT1 - y) / (LAT1 - LAT0) * TH * scale) for x, y in c], fill=0)
    return np.asarray(im.resize((TW, TH), Image.LANCZOS) if scale > 1 else im, np.float32) / 255
land_m = mask_of(land, 2); fr_m = mask_of(france, 2)
print('masks done')

# ------------------------------------------------------------ height field (scene units)
EXAG = 7.0                      # vertical exaggeration
SLAB_FR, SLAB_NB = 0.42, 0.16   # France stands proud of its neighbours, neighbours stand above the sea
def blur(a, r):
    im = Image.fromarray(np.clip(a * 255, 0, 255).astype(np.uint8)); return np.asarray(im.filter(ImageFilter.GaussianBlur(r)), np.float32) / 255
land_soft = blur(land_m, 2.2); fr_soft = blur(fr_m, 2.2)
h_land = np.maximum(elev, 0) / 10000 * EXAG
h = land_soft * SLAB_NB + fr_soft * (SLAB_FR - SLAB_NB) + h_land * np.clip(land_m * 1.0, 0, 1) * land_soft
h_sea = np.clip(elev, -3000, 0) / 10000 * 0.6    # a whisper of continental shelf
h = h + (1 - land_soft) * h_sea - 0.02
GW, GH = 900, int(round(900 * H_U / W_U))
hg = np.asarray(Image.fromarray(h.astype(np.float32), 'F').resize((GW, GH), Image.BILINEAR), np.float32)
hg.astype('<f4').tofile(f'{OUT}/height.bin')
print('grid', GW, GH)

# ------------------------------------------------------------ baked albedo + hillshade
es = elev.copy()
for _ in range(2): es = (es + np.roll(es, 1, 0) + np.roll(es, -1, 0) + np.roll(es, 1, 1) + np.roll(es, -1, 1)) / 5
gy, gx = np.gradient(es * EXAG * 1.0)
px_m = W_U * 10000 / TW            # metres per texel (horizontal)
nx, nz = -gx / px_m, -gy / px_m
nrm = np.sqrt(nx * nx + nz * nz + 1)
def shade(az, alt):
    a, b = math.radians(az), math.radians(alt)
    lx, ly, lz = math.sin(a) * math.cos(b), math.sin(b), -math.cos(a) * math.cos(b)
    return np.clip((nx * lx + ly + (-nz) * lz) / nrm, 0, 1)
hs = 0.55 * shade(315, 38) + 0.25 * shade(260, 50) + 0.2 * shade(20, 60)
hs = hs / hs[land_m > 0.5].mean()
rng = np.random.default_rng(3)
noise = np.asarray(Image.fromarray((rng.random((TH // 4, TW // 4)) * 255).astype(np.uint8)).resize((TW, TH), Image.BICUBIC), np.float32) / 255
alt = np.clip(np.maximum(elev, 0) / 2500, 0, 1)
fr_col = np.array([66, 60, 52], np.float32); nb_col = np.array([34, 33, 32], np.float32); hi = np.array([128, 118, 102], np.float32)
landc = (fr_col[None, None] * fr_m[..., None] + nb_col[None, None] * (1 - fr_m[..., None]))
landc = landc * (1 + alt[..., None] * 0.9 * (0.4 + 0.6 * fr_m[..., None]))
landc = landc * np.clip(hs, 0.25, 1.9)[..., None] * (0.93 + 0.14 * noise[..., None])
depth = np.clip(-elev / 3000, 0, 1)
sea = np.array([15, 17, 20], np.float32)[None, None] * (1 - 0.45 * depth[..., None])
# faint contour of the shelf edge
shelf = np.exp(-((elev + 200) / 60) ** 2) * (1 - land_m)
sea = sea + shelf[..., None] * np.array([6, 6, 6], np.float32)
col = landc * land_soft[..., None] + sea * (1 - land_soft[..., None])
# thin bright rim just inside the French coast (catches light like a bevel)
rim = np.clip(fr_soft - blur(fr_m, 6), 0, 1) * 1.6
col = col + rim[..., None] * hi[None, None] * 0.25
Image.fromarray(np.clip(col, 0, 255).astype(np.uint8)).save(f'{OUT}/color.jpg', quality=92)
print('color done')

# ------------------------------------------------------------ draped polylines
def height_at(x, z):
    u = (x - X0) / W_U * (GW - 1); v = (z - Z0) / H_U * (GH - 1)
    i = min(max(int(u), 0), GW - 2); j = min(max(int(v), 0), GH - 2); fu, fv = u - i, v - j
    return float(hg[j, i] * (1 - fu) * (1 - fv) + hg[j, i + 1] * fu * (1 - fv) + hg[j + 1, i] * (1 - fu) * fv + hg[j + 1, i + 1] * fu * fv)
def drape(coords, lift=0.03, step=0.25):
    pts = [P(*c[:2]) for c in coords]; out = []
    for (x0, z0), (x1, z1) in zip(pts[:-1], pts[1:]):
        n = max(1, int(math.hypot(x1 - x0, z1 - z0) / step))
        for k in range(n):
            x, z = x0 + (x1 - x0) * k / n, z0 + (z1 - z0) * k / n
            out += [round(x, 3), round(height_at(x, z) + lift, 3), round(z, 3)]
    x, z = pts[-1]; out += [round(x, 3), round(height_at(x, z) + lift, 3), round(z, 3)]
    return out
def lines_of(g):
    if g.is_empty: return []
    if g.geom_type == 'LineString': return [list(g.coords)]
    if g.geom_type in ('MultiLineString', 'GeometryCollection'): return [c for q in g.geoms for c in lines_of(q)]
    if g.geom_type in ('Polygon', 'MultiPolygon'): return lines_of(g.boundary)
    return []
L = {}
coast_fr = france.boundary.difference(unary_union([countries[c] for c in ('ESP', 'ITA', 'CHE', 'DEU', 'BEL', 'LUX', 'AND', 'MCO')]).buffer(0.01))
L['coast'] = [drape(c) for c in lines_of(coast_fr.simplify(0.004)) if len(c) > 2]
land_border = france.boundary.intersection(unary_union([countries[c] for c in ('ESP', 'ITA', 'CHE', 'DEU', 'BEL', 'LUX', 'AND', 'MCO')]).buffer(0.01))
L['border'] = [drape(c) for c in lines_of(land_border.simplify(0.004)) if len(c) > 1]
regions = [shape(f['geometry']).buffer(0) for f in json.load(open(f'{SRC}/fr_regions.geojson'))['features']]
inner = linemerge(lines_of(unary_union([r.boundary for r in regions]).difference(france.boundary.buffer(0.06))))
L['regions'] = [drape(c, 0.02) for c in lines_of(inner.simplify(0.01)) if len(c) > 1]
depts = [shape(f['geometry']).buffer(0) for f in json.load(open(f'{SRC}/fr_depts.geojson'))['features']]
dinner = linemerge(lines_of(unary_union([d.boundary for d in depts]).difference(france.boundary.buffer(0.04)).difference(inner.buffer(0.01))))
L['depts'] = [drape(c, 0.02) for c in lines_of(dinner.simplify(0.005)) if len(c) > 1]
nb = []
for f in json.load(open(f'{SRC}/ne_10m_admin_0_boundary_lines_land.geojson'))['features']:
    g = shape(f['geometry']).intersection(bb)
    if g.is_empty or g.distance(france) < 0.02 and g.difference(france.boundary.buffer(0.05)).is_empty: continue
    g = g.difference(france.buffer(0.04))
    nb += [drape(c, 0.02) for c in lines_of(g.simplify(0.01)) if len(c) > 1]
L['neighbours'] = nb
riv = []
KEEP = {'Seine', 'Loire', 'Rhône', 'Rhne', 'Garonne', 'Dordogne', 'Marne', 'Saône', 'Sane', 'Rhin', 'Rhine', 'Mosel', 'Yonne', 'Doubs', 'Durance', 'Vienne', 'Tarn'}
for f in json.load(open(f'{SRC}/ne_10m_rivers_lake_centerlines.geojson'))['features']:
    if not f['geometry'] or f['properties'].get('name') not in KEEP: continue
    g = shape(f['geometry']).intersection(france.buffer(-0.02))
    riv += [drape(c, 0.015, 0.2) for c in lines_of(g) if len(c) > 1]
L['rivers'] = riv
json.dump(L, open(f'{OUT}/lines.json', 'w'), separators=(',', ':'))
print({k: len(v) for k, v in L.items()})

# ------------------------------------------------------------ places
# day 0 = 18 Sept 2026 (first blockade at Saint-Exupéry, Créteil). Dates per research.md section 1.2 / 2.2;
# cities without a dated first action are put at day 13 (1 Oct, "nationwide" in the ministry count).
D = lambda d, m=9: (d - 18) if m == 9 else (11.5 + d)        # Oct d -> 12.5 + (d-1): mid-day so the 1 Oct flood can land on it
CITIES = [  # name, lat, lon, ignite day, 6 Oct police count (None = not published), label?, weight for the spread pulse
    ('Créteil', 48.790, 2.456, 0, None, 1, 1.0),
    ('Saint-Denis', 48.936, 2.357, D(24), None, 1, 0.7), ('Sarcelles', 48.997, 2.378, D(24), None, 0, 0.5),
    ('La Courneuve', 48.928, 2.396, D(24), None, 0, 0.5), ('Stains', 48.950, 2.383, D(25), None, 0, 0.45),
    ('Gonesse', 48.986, 2.449, D(25), None, 0, 0.45), ('Saint-Ouen', 48.912, 2.334, D(25), None, 0, 0.45),
    ('Rosny-sous-Bois', 48.874, 2.486, D(25), None, 0, 0.45),
    ('Paris', 48.857, 2.352, D(25), 56000, 1, 1.0),
    ('Saint-Ouen-l\'Aumône', 49.044, 2.111, D(28), None, 0, 0.4), ('Meaux', 48.960, 2.879, D(28), None, 0, 0.4),
    ('Marseille', 43.297, 5.370, D(28), 4800, 1, 0.9), ('Lille', 50.629, 3.057, D(28), 5800, 1, 0.8),
    ('Lyon', 45.764, 4.836, D(28), 20000, 1, 0.95), ('Toulon', 43.124, 5.928, D(28), None, 0, 0.5),
    ('Nice', 43.710, 7.262, D(28), None, 1, 0.55),
    ('Roubaix', 50.694, 3.175, D(30), None, 0, 0.45), ('Tours', 47.394, 0.685, D(30), None, 0, 0.5),
    ('Grenoble', 45.188, 5.724, D(30), None, 0, 0.5),
    ('Rennes', 48.117, -1.678, D(1, 10), 3900, 1, 0.7), ('Nantes', 47.218, -1.554, D(1, 10), None, 1, 0.75),
    ('Toulouse', 43.605, 1.444, D(1, 10), 13500, 1, 0.85), ('Aix-en-Provence', 43.530, 5.447, D(1, 10), 1300, 0, 0.45),
    ('Saint-Étienne', 45.440, 4.387, D(1, 10), None, 0, 0.45), ('Brest', 48.390, -4.486, D(1, 10), None, 0, 0.5),
    ('Saint-Brieuc', 48.514, -2.765, D(1, 10), None, 0, 0.35), ('Rouen', 49.443, 1.100, D(1, 10), None, 0, 0.55),
    ('Besançon', 47.238, 6.024, D(1, 10), None, 0, 0.5), ('Metz', 49.119, 6.176, D(1, 10), None, 0, 0.45),
    ('Strasbourg', 48.573, 7.752, D(1, 10), None, 1, 0.55), ('Perpignan', 42.689, 2.895, D(1, 10), None, 0, 0.45),
    ('Bordeaux', 44.838, -0.579, D(1, 10), 9000, 1, 0.75), ('Évreux', 49.024, 1.151, D(2, 10), None, 0, 0.35),
    ('Belfort', 47.638, 6.863, D(2, 10), None, 0, 0.35), ('Nîmes', 43.837, 4.360, D(1, 10), None, 0, 0.4),
    ('Avignon', 43.949, 4.806, D(1, 10), None, 0, 0.4), ('Montpellier', 43.611, 3.877, D(1, 10), None, 0, 0.5),
    ('Annecy', 45.899, 6.129, D(1, 10), None, 0, 0.35), ('Amiens', 49.894, 2.296, D(1, 10), None, 0, 0.45),
    ('Le Havre', 49.494, 0.108, D(1, 10), None, 0, 0.4), ('Manosque', 43.828, 5.786, D(1, 10), None, 0, 0.3),
    ('Nancy', 48.692, 6.184, D(1, 10), None, 0, 0.4), ('Lens', 50.432, 2.833, D(1, 10), None, 0, 0.35),
    ('Ajaccio', 41.919, 8.739, D(6, 10), None, 0, 0.3), ('Bastia', 42.697, 9.450, D(6, 10), None, 0, 0.3),
]
cities = []
for n, la, lo, day, pol, lab, w in CITIES:
    x, z = P(lo, la); cities.append(dict(name=n, lat=la, lon=lo, x=round(x, 3), z=round(z, 3), y=round(height_at(x, z), 3), day=day, police6oct=pol, label=lab, w=w))

# lycées from the national directory. Ignite order: day of the nearest dated city within 45 km (+ jitter, later the
# further out), otherwise day 12-13 (the 1 Oct flood). The first N(day) of that order are lit; N follows the
# Interior Ministry national series (section 2.1). Approximation of WHERE, exact on HOW MANY.
rows = [r for r in csv.DictReader(open(f'{SRC}/lycees.csv', encoding='utf-8-sig'), delimiter=';') if r['latitude'] and r['longitude']]
rows = [r for r in rows if LON0 < float(r['longitude']) < LON1 and LAT0 < float(r['latitude']) < LAT1 and france.contains(Point(float(r['longitude']), float(r['latitude'])))]
rnd = random.Random(11)
ly = []
for r in rows:
    la, lo = float(r['latitude']), float(r['longitude'])
    best = None
    for c in cities:
        dkm = math.hypot((lo - c['lon']) * CL * 111.32, (la - c['lat']) * 111.32)
        if dkm < 45 and c['day'] < 11:
            d = c['day'] + dkm / 45 * (2.0 if c['day'] < 6 else 1.2) + rnd.random() * 0.8
            best = d if best is None else min(best, d)
    if best is None: best = 11.2 + rnd.random() * 1.8
    x, z = P(lo, la)
    ly.append(dict(x=round(x, 3), z=round(z, 3), y=round(height_at(x, z), 3), d=round(best, 3), pub=r['statut_public_prive'] == 'Public', ac=r['libelle_academie']))
ly.sort(key=lambda q: q['d'])
SERIES = [(0, 1), (6, 20), (7, 60), (10, 180), (11, 338), (12, 356), (13, 1027)]   # day 13 = end of 1 Oct   # (day, lycées affected)
def n_at(day):
    for (d0, n0), (d1, n1) in zip(SERIES[:-1], SERIES[1:]):
        if day <= d1: return n0 + (n1 - n0) * max(0, (day - d0)) / (d1 - d0)
    return SERIES[-1][1]
# Fill each step of the national series with lycées whose candidate day falls inside it (random pick among the
# eligible, so dense areas fill faster but the flood on 1 Oct lands all over the country).
# rank = position in the ignite order; the scene lights lycée i once n_at(day) > i
order, taken = [], set()
crei = min(range(len(ly)), key=lambda i: math.hypot(ly[i]['x'] - P(2.456, 48.790)[0], ly[i]['z'] - P(2.456, 48.790)[1]))
order.append(crei); taken.add(crei)
for (d0, n0), (d1, n1) in zip(SERIES[:-1], SERIES[1:]):
    elig = [i for i, q in enumerate(ly) if i not in taken and q['d'] <= d1]
    rnd.shuffle(elig)
    pick = sorted(elig[:n1 - n0], key=lambda i: ly[i]['d'])
    order += pick; taken.update(pick)
rest = [i for i in range(len(ly)) if i not in taken]
order += rest
ly = [ly[i] for i in order]
for i, q in enumerate(ly): q['rank'] = i
# red / orange: 114 + 400 public lycées, weighted toward the academies with the worst SNES-FSU shortage figures
# (Versailles 70%, Toulouse 66.7%, Nantes 61.7%, Créteil 61.1%). ILLUSTRATIVE: the ministry has not published the list.
WEIGHT = {'Versailles': 3.0, 'Créteil': 3.0, 'Toulouse': 2.2, 'Nantes': 2.0, 'Paris': 1.2, 'Aix-Marseille': 1.6, 'Lille': 1.6, 'Lyon': 1.3}
pub = [q for q in ly if q['pub']]
def wsample(pool, k, pw):
    keyed = sorted(pool, key=lambda q: -rnd.random() ** (1 / (WEIGHT.get(q['ac'], 1.0) ** pw)))
    return keyed[:k]
red = wsample(pub, 114, 2.0)
rest = [q for q in pub if q not in red]
orange = wsample(rest, 400, 1.0)
for q in ly: q['ro'] = 0
for q in red: q['ro'] = 2
for q in orange: q['ro'] = 1
cre = next(c for c in cities if c['name'] == 'Créteil')
places = dict(grid=[GW, GH], extent=[X0, Z0, W_U, H_U], cities=cities, series=SERIES,
              lycees=[[q['x'], q['y'], q['z'], q['rank'], q['ro']] for q in ly[:1027]] + [[q['x'], q['y'], q['z'], -1, q['ro']] for q in ly[1027:] if q['ro']],
              all_lycees=[[q['x'], q['y'], q['z']] for q in ly], creteil=[cre['x'], cre['y'], cre['z']])
json.dump(places, open(f'{OUT}/places.json', 'w'), separators=(',', ':'), ensure_ascii=False)
print('lycées', len(ly), 'public', len(pub), 'red', len(red), 'orange', len(orange), 'in flood', min(1027, len(ly)))
