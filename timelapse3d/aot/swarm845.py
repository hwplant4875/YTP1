"""Crowd + pure-titan swarm for the fall of Shiganshina (845), built to read from a sky camera (60-250 m).

Minimal, colourful, faceless figures (same spirit as render_fast.py's plaza crowd): a tapered body, a
sphere head (hair-coloured top so it reads from above) and box limbs that swing. Titans are the same
idea scaled up: box legs, a capsule-ish torso, two-segment arms (they can lift a person to the mouth),
skin tones, 3-15 m, plus a few distinctive ones (the Smiling Titan with its grin, a fat short one, a
lanky bald one, an abnormal runner).

EVERYTHING IS A PURE FUNCTION OF TIME.  setup() precomputes the whole story on a 0.2 s grid (paths on a
walkable street grid, boat schedule, titan wandering / grabbing); update(t) only interpolates and
writes vertex positions of two deforming meshes (all people / all titans) + the boat objects.

API (t = seconds after the kick impact, i.e. the moment the outer gate bursts; t < 0 = before it):
    import swarm845 as SW
    SW.setup(n_plaza=500, n_street=320, n_titans=30, seed=845, t_end=150.0)   # once per Blender session
    SW.update(t, pscale=None)          # every frame; same t -> same result; ~15 ms (pscale: people size factor)
    SW.HIDE_TITANS = {"smiling"}       # hide titans by name/index (a hero rig takes over)
    SW.info()                          # dict: counts, eaten, boats, timings
    SW.STATE                           # internals (objects, arrays) if a shot needs to look something up
    SW.titan_pos(name_or_index, t)     # (x, y, z, yaw) of a titan, e.g. "smiling", for camera tracking
Story beats (t): < 0 the crowd (plaza + streets) stands looking south at the outer wall / Colossal;
    0.15-0.6 startle hop; 0.6-4 s people start running (staggered, near-gate first) along the streets
    to the inner gate (north, then they spread out in the field beyond it) or to the three canal ferry
    docks (east canal), where boats (24 seats) fill up and push off north through the water gate, the
    next boat in the queue sliding up; titans walk in through the broken outer gate from ~t=4 s, one
    after another, wander the streets with momentum, drift toward people, grab one (reach, lift to
    the mouth, gone, no gore), then scatter for a while.  After t_end everything freezes.
Plug-in use (scene.py AOT_PLUGINS=swarm845): build(M, year, ctx) runs setup() only when SWARM=1, then
    update(SWARM_T) if SWARM_T is set (single test still).  Test cameras: swarm_plaza, swarm_town,
    swarm_gate, swarm_canal, swarm_igate, swarm_mid.
      SWARM=1 SWARM_T=20 AOT_PLUGINS=swarm845 bash render.sh swarm_town out.png 854x480 8
Env: SWARM_PLAZA, SWARM_STREET, SWARM_TITANS, SWARM_SEED, SWARM_TEND override the setup() defaults.
"""
import math, os, time, heapq, random
import numpy as np
import bpy

import aotlib as L

DT = 0.2
OGX, OGY = L.OUTER_GATE
PXC, PYC, PR = L.PLAZA
CX, CW = L.CX, L.CANAL_W
HEAD_PT = (-7.0, OGY - 16.0)          # where the Colossal's head is: the crowd looks there
G = 4.0                               # nav grid cell (m)
X0, X1, Y0, Y1 = -300.0, 300.0, OGY - 160.0, 140.0
DOCK_Y = (-130.0, -280.0, -430.0)
DOCK_BANK_X = CX - CW / 2 - 4.0       # waiting area centre on the canal road
BOAT_Q_X = CX - 6.5                   # docked / queued boats (west half of the canal)
BOAT_LANE_X = CX + 5.0                # sailing lane (east half)
NB, SEATS = 5, 24
EAT_DUR = 3.4
PEOPLE_SCALE = float(os.environ.get("SWARM_PSCALE", "1.0"))   # >1 exaggerates people for very high shots (render-time only)
HIDE_TITANS = set()          # titan names / indices update() hides (e.g. {"smiling"} when a hero titan replaces it)
STATE = {}

# ---------------------------------------------------------------- palettes (linear RGB)
SHIRTS = [(0.80, 0.07, 0.05), (0.05, 0.18, 0.75), (0.92, 0.68, 0.04), (0.08, 0.48, 0.12), (0.88, 0.88, 0.82),
          (0.92, 0.32, 0.04), (0.42, 0.10, 0.58), (0.03, 0.50, 0.52), (0.88, 0.32, 0.50), (0.30, 0.62, 0.92),
          (0.60, 0.80, 0.10), (0.70, 0.12, 0.25)]
PANTS = [(0.10, 0.06, 0.03), (0.04, 0.05, 0.14), (0.20, 0.20, 0.22), (0.40, 0.30, 0.17)]
SKINS = [(0.80, 0.55, 0.42), (0.70, 0.45, 0.32), (0.55, 0.34, 0.22)]
HAIRS = [(0.02, 0.016, 0.012), (0.12, 0.06, 0.03), (0.55, 0.40, 0.12), (0.45, 0.12, 0.04), (0.50, 0.50, 0.50)]
T_SKINS = [(0.66, 0.30, 0.17), (0.74, 0.33, 0.18), (0.76, 0.38, 0.23), (0.70, 0.32, 0.18), (0.58, 0.17, 0.09),
           (0.76, 0.36, 0.21), (0.66, 0.20, 0.11)]
T_HAIRS = [(0.03, 0.022, 0.018), (0.13, 0.07, 0.035), (0.42, 0.24, 0.09), (0.55, 0.45, 0.20)]
SPECIAL = [  # name, H, girth, arm length, head scale, skin, hair, speed, start rank
    dict(name="smiling", H=13.0, g=0.78, al=1.15, hs=1.0, skin=0, hair=1, v=4.6, grin=True, rank=2),
    dict(name="fat", H=5.0, g=1.75, al=0.85, hs=1.3, skin=1, hair=None, v=2.2, rank=4),
    dict(name="lanky", H=14.5, g=0.68, al=1.25, hs=0.8, skin=6, hair=None, v=5.4, rank=7),
    dict(name="runner", H=7.0, g=0.9, al=1.0, hs=1.15, skin=4, hair=0, v=8.0, rank=11),
]

def _smooth(u):
    u = min(1.0, max(0.0, u)); return u * u * (3 - 2 * u)

# ---------------------------------------------------------------- tiny geometry builder (numpy, per-vertex rig data)
class Geo:
    """Accumulates primitives with per-vertex rig info: object id, part, root pivot (y,z), elbow pivot (y,z)."""
    def __init__(self):
        self.v, self.f, self.fc, self.oid, self.part, self.pr, self.pe, self.hip = [], [], [], [], [], [], [], []

    def _add(self, verts, faces, cats, oid, part, pr, pe, hip):
        b = len(self.v)
        self.v += verts; self.f += [[i + b for i in fa] for fa in faces]; self.fc += cats
        n = len(verts)
        self.oid += [oid] * n; self.part += [part] * n; self.pr += [pr] * n; self.pe += [pe] * n; self.hip += [hip] * n

    def box(self, c, s, cat, oid, part=0, pr=(0, 0), pe=(0, 0), hip=0.0, taper=1.0):
        x, y, z = c; a, b, h = s[0] / 2, s[1] / 2, s[2] / 2
        V = []
        for zz in (-h, h):
            k = taper if zz > 0 else 1.0
            V += [(x - a * k, y - b * k, z + zz), (x + a * k, y - b * k, z + zz), (x + a * k, y + b * k, z + zz), (x - a * k, y + b * k, z + zz)]
        F = [[0, 3, 2, 1], [4, 5, 6, 7], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]]
        self._add(V, F, [cat] * 6, oid, part, pr, pe, hip)

    def cyl(self, cx, cy, z0, z1, r0, r1, seg, cat, oid, part=0, pr=(0, 0), pe=(0, 0), hip=0.0, sy=1.0):
        V = []
        for z, r in ((z0, r0), (z1, r1)):
            V += [(cx + math.cos(2 * math.pi * i / seg) * r, cy + math.sin(2 * math.pi * i / seg) * r * sy, z) for i in range(seg)]
        F = [[i, (i + 1) % seg, seg + (i + 1) % seg, seg + i] for i in range(seg)]
        F += [list(range(seg))[::-1], list(range(seg, 2 * seg))]
        self._add(V, F, [cat] * len(F), oid, part, pr, pe, hip)

    def sphere(self, c, r, seg, rings, cat_lo, cat_hi, split, oid, part=0, hip=0.0, sz=1.0):
        """UV sphere; faces whose centre is above c.z + split*r get cat_hi (hair), else cat_lo."""
        x, y, z = c
        V = [(x, y, z - r * sz)]
        for k in range(1, rings):
            th = math.pi * k / rings
            V += [(x + math.sin(th) * math.cos(2 * math.pi * i / seg) * r, y + math.sin(th) * math.sin(2 * math.pi * i / seg) * r,
                   z - math.cos(th) * r * sz) for i in range(seg)]
        V.append((x, y, z + r * sz))
        top = len(V) - 1
        F = [[0, 1 + (i + 1) % seg, 1 + i] for i in range(seg)]
        for k in range(rings - 2):
            a, b = 1 + k * seg, 1 + (k + 1) * seg
            F += [[a + i, a + (i + 1) % seg, b + (i + 1) % seg, b + i] for i in range(seg)]
        a = 1 + (rings - 2) * seg
        F += [[a + i, a + (i + 1) % seg, top] for i in range(seg)]
        cats = [cat_hi if sum(V[i][2] for i in fa) / len(fa) > z + split * r else cat_lo for fa in F]
        self._add(V, F, cats, oid, part, (0, 0), (0, 0), hip)

    def finish(self):
        R = {"B": np.array(self.v, float), "oid": np.array(self.oid, np.int32), "part": np.array(self.part, np.int32),
             "pr": np.array(self.pr, float), "pe": np.array(self.pe, float), "hip": np.array(self.hip, float)}
        R["up"] = np.isin(R["part"], (0, 3, 4, 5, 6)).astype(float)
        return R

def _rot(y, z, py, pz, c, s):
    dy = y - py; dz = z - pz
    return py + dy * c - dz * s, pz + dy * s + dz * c

def _deform(R, Ar, Ae, lean, vis, yaw, pos):
    """Rig -> world verts. Ar/Ae (nobj, 7) root / elbow angles about local x (+ = hanging limb swings forward),
    lean (nobj) upper body about the hip (- = forward), vis (nobj) scale, yaw (nobj), pos (nobj, 3)."""
    o, p, B = R["oid"], R["part"], R["B"]
    y, z = B[:, 1], B[:, 2]
    ce, se = np.cos(Ae)[o, p], np.sin(Ae)[o, p]
    y, z = _rot(y, z, R["pe"][:, 0], R["pe"][:, 1], ce, se)
    cr, sr = np.cos(Ar)[o, p], np.sin(Ar)[o, p]
    y, z = _rot(y, z, R["pr"][:, 0], R["pr"][:, 1], cr, sr)
    a = lean[o] * R["up"]
    y, z = _rot(y, z, 0.0, R["hip"], np.cos(a), np.sin(a))
    s = vis[o]
    x = B[:, 0] * s; y = y * s; z = z * s
    c, sn = np.cos(yaw)[o], np.sin(yaw)[o]
    out = np.empty((len(B), 3))
    out[:, 0] = c * x - sn * y + pos[o, 0]
    out[:, 1] = sn * x + c * y + pos[o, 1]
    out[:, 2] = z + pos[o, 2]
    return out

def _mesh(name, R, faces, fmat, mats, coll):
    me = bpy.data.meshes.new(name)
    me.from_pydata(R["B"].tolist(), [], faces)
    for m in mats:
        me.materials.append(m)
    me.polygons.foreach_set("material_index", np.asarray(fmat, np.int32))
    me.update()
    ob = bpy.data.objects.new(name, me); coll.objects.link(ob)
    return ob

# ---------------------------------------------------------------- figures
def person_geo(g, i, h, dress, rnd):
    s = h / 1.7
    hip = 0.82 * s
    sh = 1.36 * s
    for side, part in ((-1, 1), (1, 2)):
        g.box((0.09 * s * side, 0, hip / 2), (0.13 * s, 0.15 * s, hip), 1, i, part, (0, hip), (0, 0), hip)
    if dress:
        g.cyl(0, 0, 0.32 * s, 1.42 * s, 0.30 * s, 0.21 * s, 6, 0, i, 0, hip=hip)
    else:
        g.cyl(0, 0, 0.76 * s, 1.42 * s, 0.19 * s, 0.24 * s, 6, 0, i, 0, hip=hip, sy=0.8)
    for side, part in ((-1, 3), (1, 4)):
        g.box((0.30 * s * side, 0, sh - 0.29 * s), (0.09 * s, 0.10 * s, 0.6 * s), 0, i, part, (0, sh), (0, 0), hip)
    g.sphere((0, 0, 1.57 * s), 0.135 * s, 6, 4, 2, 3, -0.05, i, 0, hip, sz=1.1)

def titan_geo(g, j, sp):
    H, gi, al, hs = sp["H"], sp["g"], sp["al"], sp["hs"]
    hip = 0.47 * H; sh = 0.79 * H; la = 0.18 * H * al
    for side, part in ((-1, 1), (1, 2)):
        g.box((0.075 * H * gi * side, 0, hip / 2), (0.10 * H * gi, 0.11 * H * gi, hip), 0, j, part, (0, hip), (0, 0), hip, taper=1.1)
        g.box((0.075 * H * gi * side, 0.025 * H, 0.012 * H), (0.10 * H * gi, 0.16 * H, 0.024 * H), 0, j, part, (0, hip), (0, 0), hip)
    belly = 1.25 if gi > 1.3 else 1.0
    g.cyl(0, 0, 0.44 * H, 0.62 * H, 0.12 * H * gi, 0.14 * H * gi * belly, 8, 0, j, 0, hip=hip, sy=0.75)
    g.cyl(0, 0, 0.62 * H, 0.80 * H, 0.14 * H * gi * belly, 0.13 * H * gi, 8, 0, j, 0, hip=hip, sy=0.7)
    g.cyl(0, 0, 0.79 * H, 0.85 * H, 0.04 * H, 0.04 * H, 6, 0, j, 0, hip=hip)
    hr = 0.075 * H * hs; hc = 0.85 * H + hr * 0.85
    g.sphere((0, 0, hc), hr, 8, 6, 0, 1 if sp.get("hair") is not None else 0, 0.15, j, 0, hip, sz=1.1)
    if sp.get("grin"):
        g.box((0, hr * 0.9, hc - hr * 0.32), (hr * 1.25, hr * 0.25, hr * 0.17), 2, j, 0, (0, 0), (0, 0), hip)
    sx = 0.13 * H * gi + 0.032 * H
    for side, pu, pf in ((-1, 3, 6), (1, 4, 5)):
        g.box((sx * side, 0, sh - la / 2), (0.055 * H, 0.06 * H, la), 0, j, pu, (0, sh), (0, 0), hip)
        g.box((sx * side, 0, sh - la * 1.5), (0.05 * H, 0.055 * H, la), 0, j, pf, (0, sh), (0, sh - la), hip)
    return (sx, sh, la, hip, hc, hr)

# ---------------------------------------------------------------- nav grid
WALK_FN = None               # opt-in override set by configure() (other district sets, e.g. Trost); None = Shiganshina

def configure(walkable=None, bounds=None, gates=None):
    """Opt-in hook for other district sets (default Shiganshina behaviour is unchanged unless this is called):
    walkable=fn(x, y)->bool replaces _walk_people; bounds=(x0, x1, y0, y1) replaces the nav grid extent;
    gates=dict(outer=(x, y)) moves the outer gate used by the titan entry / wander mask."""
    global WALK_FN, X0, X1, Y0, Y1, OGX, OGY
    if walkable is not None:
        WALK_FN = walkable
    if bounds is not None:
        X0, X1, Y0, Y1 = map(float, bounds)
    if gates and "outer" in gates:
        OGX, OGY = map(float, gates["outer"])
    STATE.pop("grid", None)

def _walk_people(x, y):
    if WALK_FN is not None:
        return bool(WALK_FN(x, y))
    if abs(x - CX) < CW / 2 + 2.5:
        return False
    if abs(x - PXC) < 9.5 and abs(y - PYC) < 9.5:          # monument plinth
        return False
    if abs(x) < 5.5 and -14 <= y <= 12:                     # inner gate passage
        return True
    if 8 < y < 125 and abs(x) < 16 + (y - 8) * 0.5:         # field beyond the inner gate
        return True
    if abs(x) < 5.5 and OGY - 12 <= y <= OGY + 12:           # broken outer gate
        return True
    if OGY - 160 < y < OGY - 6 and abs(x) < 26 + (OGY - 6 - y) * 0.6:   # outside the outer gate (titans)
        return True
    return L.in_district(x, y, 7.0) and L.on_road(x, y)

NB8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

def build_grid():
    nx, ny = int((X1 - X0) / G), int((Y1 - Y0) / G)
    xs = X0 + (np.arange(nx) + 0.5) * G; ys = Y0 + (np.arange(ny) + 0.5) * G
    W = np.zeros((nx, ny), bool)
    for i, x in enumerate(xs):
        if WALK_FN is None and abs(x) > 300:
            continue
        for j, y in enumerate(ys):
            W[i, j] = _walk_people(float(x), float(y))
    cur = W.copy(); clr = W.astype(float)
    for _ in range(4):
        n = cur.copy()
        n[1:, :] &= cur[:-1, :]; n[:-1, :] &= cur[1:, :]; n[:, 1:] &= cur[:, :-1]; n[:, :-1] &= cur[:, 1:]
        n[0, :] = n[-1, :] = n[:, 0] = n[:, -1] = False
        cur = n; clr += cur
    Z = np.zeros((nx, ny))
    for i, x in enumerate(xs):
        for j, y in enumerate(ys):
            if W[i, j]:
                Z[i, j] = L.height(float(x), float(y)) + (0.16 if L.in_district(float(x), float(y), 0.0) else 0.05)
    WT = W & (ys[None, :] < -16.0) & (ys[None, :] > OGY - 2.0)     # wandering titans stay inside the district
    return dict(nx=nx, ny=ny, xs=xs, ys=ys, W=W, WT=WT, clr=clr, Z=Z)

def cell(Gd, x, y):
    i = int(min(Gd["nx"] - 1, max(0, (x - X0) // G))); j = int(min(Gd["ny"] - 1, max(0, (y - Y0) // G)))
    return i, j

def nearest_walk(Gd, x, y, mask="W"):
    i, j = cell(Gd, x, y); M = Gd[mask]
    if M[i, j]:
        return i, j
    for r in range(1, 12):
        best = None
        for di in range(-r, r + 1):
            for dj in range(-r, r + 1):
                ii, jj = i + di, j + dj
                if 0 <= ii < Gd["nx"] and 0 <= jj < Gd["ny"] and M[ii, jj]:
                    d = di * di + dj * dj
                    if best is None or d < best[0]:
                        best = (d, ii, jj)
        if best:
            return best[1], best[2]
    return i, j

def dijkstra(Gd, goals):
    nx, ny = Gd["nx"], Gd["ny"]
    W = Gd["W"].ravel().tolist(); C = Gd["clr"].ravel().tolist()
    dist = [math.inf] * (nx * ny)
    h = []
    for (i, j) in goals:
        dist[i * ny + j] = 0.0; h.append((0.0, i * ny + j))
    heapq.heapify(h)
    steps = [(di * ny + dj, di, dj, math.hypot(di, dj) * G) for di, dj in NB8]
    while h:
        d, c = heapq.heappop(h)
        if d > dist[c]:
            continue
        ci, cj = divmod(c, ny)
        for off, di, dj, ln in steps:
            ii, jj = ci + di, cj + dj
            if not (0 <= ii < nx and 0 <= jj < ny):
                continue
            n = c + off
            if not W[n]:
                continue
            nd = d + ln * (1.0 + 1.2 / (0.5 + C[n]))
            if nd < dist[n]:
                dist[n] = nd; heapq.heappush(h, (nd, n))
    return dist

def descend(Gd, dist, i, j):
    ny = Gd["ny"]; nx = Gd["nx"]
    out = [(i, j)]
    c = i * ny + j
    for _ in range(2000):
        if dist[c] == 0:
            break
        ci, cj = divmod(c, ny)
        best, bd = None, dist[c]
        for di, dj in NB8:
            ii, jj = ci + di, cj + dj
            if 0 <= ii < nx and 0 <= jj < ny and dist[ii * ny + jj] < bd:
                bd = dist[ii * ny + jj]; best = ii * ny + jj
        if best is None:
            break
        c = best; out.append(divmod(c, ny))
    return out

def make_path(Gd, start, cells, end, lat, rnd):
    """Cell chain -> smoothed polyline with a per-person lateral lane offset bounded by the street clearance."""
    xs, ys = Gd["xs"], Gd["ys"]
    P = np.array([start] + [(xs[i], ys[j]) for i, j in cells] + [end], float)
    C = np.array([Gd["clr"][cells[0]]] + [Gd["clr"][c] for c in cells] + [Gd["clr"][cells[-1]]], float)
    for _ in range(2):
        if len(P) > 3:
            P[1:-1] = (P[:-2] + P[1:-1] + P[2:]) / 3.0
            C[1:-1] = np.minimum(np.minimum(C[:-2], C[1:-1]), C[2:])
    if len(P) > 3:
        d = np.gradient(P, axis=0); n = np.linalg.norm(d, axis=1, keepdims=True); n[n == 0] = 1
        nrm = np.stack([-d[:, 1], d[:, 0]], 1) / n
        off = np.clip((C * G - 3.0) * 0.55, 0.0, 6.0) * lat
        w = np.ones(len(P)); w[:2] = (0.0, 0.5); w[-2:] = (0.5, 0.0)
        P = P + nrm * (off * w)[:, None]
    seg = np.linalg.norm(np.diff(P, axis=0), axis=1)
    s = np.concatenate([[0.0], np.cumsum(seg)])
    return P, s

# ---------------------------------------------------------------- setup
def setup(n_plaza=None, n_street=None, n_titans=None, seed=None, t_end=None):
    t_start = time.time()
    env = os.environ.get
    n_plaza = int(env("SWARM_PLAZA", n_plaza or 500)); n_street = int(env("SWARM_STREET", n_street or 320))
    n_titans = int(env("SWARM_TITANS", n_titans or 30)); seed = int(env("SWARM_SEED", seed or 845))
    t_end = float(env("SWARM_TEND", t_end or 150.0))
    rnd = random.Random(seed); np.random.seed(seed)
    K = int(round(t_end / DT)) + 1
    T = np.arange(K) * DT
    Gd = build_grid()
    t_grid = time.time() - t_start
    gate_goal = [nearest_walk(Gd, 0.0, 24.0)]
    dist_gate = dijkstra(Gd, gate_goal)
    dock_goal = [nearest_walk(Gd, DOCK_BANK_X, yd) for yd in DOCK_Y]
    dist_dock = [dijkstra(Gd, [g]) for g in dock_goal]
    ny = Gd["ny"]

    # ---- people: start positions
    starts = []
    occ = {}
    def free(x, y, r=1.45):
        gx, gy = int(x // 2), int(y // 2)
        for a in (-1, 0, 1):
            for b in (-1, 0, 1):
                for (ox, oy) in occ.get((gx + a, gy + b), ()):
                    if (ox - x) ** 2 + (oy - y) ** 2 < r * r:
                        return False
        return True
    tries = 0
    while len(starts) < n_plaza and tries < n_plaza * 40:
        tries += 1
        a = rnd.uniform(0, math.tau); r = math.sqrt(rnd.random()) * (PR - 1.5)
        x, y = PXC + math.cos(a) * r, PYC + math.sin(a) * r
        if abs(x - PXC) < 10.5 and abs(y - PYC) < 10.5:
            continue
        if free(x, y):
            starts.append((x, y, 0)); occ.setdefault((int(x // 2), int(y // 2)), []).append((x, y))
    cand = [(i, j) for i in range(Gd["nx"]) for j in range(ny)
            if Gd["W"][i, j] and dist_gate[i * ny + j] < math.inf and Gd["ys"][j] < -20 and Gd["ys"][j] > OGY + 8
            and math.hypot(Gd["xs"][i] - PXC, Gd["ys"][j] - PYC) > PR + 3]
    for (i, j) in rnd.sample(cand, min(n_street, len(cand))):
        starts.append((Gd["xs"][i] + rnd.uniform(-1.6, 1.6), Gd["ys"][j] + rnd.uniform(-1.6, 1.6), 1))
    N = len(starts)

    # ---- people: attributes + paths
    PX = np.zeros((K, N)); PY = np.zeros((K, N)); PZ = np.zeros((K, N)); PS = np.zeros((K, N), np.int8)
    yaw0 = np.zeros(N); hgt = np.zeros(N)
    goal = np.zeros(N, np.int32) - 1             # -1 stay, 0 gate, 1.. dock index + 1
    t_arr = np.full(N, math.inf); spot = np.zeros((N, 2))
    zg = lambda x, y: Gd["Z"][cell(Gd, x, y)]
    t_go = np.zeros(N)
    for i, (x, y, street) in enumerate(starts):
        u = rnd.random()
        h = rnd.uniform(1.0, 1.3) if u < 0.12 else rnd.uniform(1.5, 1.9)
        hgt[i] = h
        v = rnd.uniform(2.0, 2.8) if u < 0.12 else (rnd.uniform(1.4, 2.0) if u > 0.9 else rnd.uniform(2.6, 4.2))
        yaw0[i] = math.atan2(-(HEAD_PT[0] - x), HEAD_PT[1] - y) + rnd.uniform(-0.25, 0.25)
        if street:
            tg = 0.6 + rnd.uniform(0, 2.5) + max(0.0, (y - OGY)) / 300.0
        else:
            tg = 1.0 + rnd.uniform(0, 2.8) + max(0.0, PYC + PR - y) / 40.0
        if rnd.random() < 0.13:                  # frozen in shock / looking for family: the titans' first victims
            tg += rnd.uniform(6.0, 45.0)
        t_go[i] = tg
        ci, cj = nearest_walk(Gd, x, y)
        dg = dist_gate[ci * ny + cj]
        dd = [d[ci * ny + cj] for d in dist_dock]
        kd = int(np.argmin(dd))
        dock = dd[kd] < math.inf and (dd[kd] < 0.45 * dg or (rnd.random() < 0.3 and dd[kd] < 1.3 * dg))
        if dg == math.inf and dd[kd] == math.inf:
            PX[:, i], PY[:, i] = x, y; PZ[:, i] = zg(x, y); continue
        if dock:
            goal[i] = kd + 1
            cells = descend(Gd, dist_dock[kd], ci, cj)
            end = (DOCK_BANK_X + rnd.uniform(-3.5, 3.5), DOCK_Y[kd] + rnd.uniform(-8, 8))
        else:
            goal[i] = 0
            cells = descend(Gd, dist_gate, ci, cj)
            yy = rnd.uniform(28, 115); end = (rnd.uniform(-1, 1) * (12 + (yy - 8) * 0.45), yy)
        P, s = make_path(Gd, (x, y), cells, end, rnd.uniform(-1, 1), rnd)
        sk = np.clip(v * (T - tg), 0.0, s[-1])
        PX[:, i] = np.interp(sk, s, P[:, 0]); PY[:, i] = np.interp(sk, s, P[:, 1])
        t_arr[i] = tg + s[-1] / v; spot[i] = end
    ii = np.clip(((PX - X0) // G).astype(int), 0, Gd["nx"] - 1); jj = np.clip(((PY - Y0) // G).astype(int), 0, ny - 1)
    PZ[:] = Gd["Z"][ii, jj]

    # ---- boats: schedule (fill in arrival order, 24 seats, leave when full or 30 s after the first boarder)
    boats = []           # dict(d, b, dep, D)
    seat = {}            # person -> (boat index, slot, t_board)
    for d in range(len(DOCK_Y)):
        arr = sorted((t_arr[i], i) for i in range(N) if goal[i] == d + 1)
        b, D, seats, last, dep = 0, 0.0, [], 0.0, []
        for ta, i in arr:
            while b < NB:
                tb = max(ta + 0.4, D + 1.0, last + 0.3)
                if seats and tb > seats[0][1] + 30.0:
                    dep.append(seats[0][1] + 30.0); b += 1; D = dep[-1] + 7.0; seats, last = [], D; continue
                seats.append((i, tb)); last = tb
                seat[i] = (len(boats) + b, len(seats) - 1, tb)
                if len(seats) == SEATS:
                    dep.append(tb + 2.5); b += 1; D = dep[-1] + 7.0; seats, last = [], D
                break
        if seats and b < NB:
            dep.append(last + 12.0)
        dep += [math.inf] * (NB - len(dep))
        for k in range(NB):
            boats.append(dict(d=d, b=k, dep=dep[k]))
    nbt = len(boats)
    BX = np.zeros((K, nbt)); BY = np.zeros((K, nbt)); BZ = np.full((K, nbt), 0.13); BYAW = np.zeros((K, nbt))
    def north_x(y):
        tt = max(0.0, (y - 8) / 40.0)
        return math.sin(tt / 5) * 60 * min(1, tt / 6)
    zcache = {}
    for bi, bo in enumerate(boats):
        d, b = bo["d"], bo["b"]; yd = DOCK_Y[d]
        deps = [boats[bi - b + q]["dep"] for q in range(b)]
        for k, t in enumerate(T):
            yq = yd - 15.0 * b + 15.0 * sum(_smooth((t - dj) / 7.0) for dj in deps)
            if t < bo["dep"]:
                x, y = BOAT_Q_X, yq
            else:
                u = t - bo["dep"]; a, vm = 0.5, 3.2; ua = vm / a
                s = 0.5 * a * u * u if u < ua else 0.5 * a * ua * ua + vm * (u - ua)
                y = yd + s; x = BOAT_Q_X + (BOAT_LANE_X - BOAT_Q_X) * _smooth(u / 6.0) + north_x(y)
            BX[k, bi], BY[k, bi] = x, y
            if y > 2:
                ky = int(y // 4)
                if ky not in zcache:
                    zcache[ky] = L.height(CX + north_x(y), y) + 2.15
                BZ[k, bi] = 0.13 + (zcache[ky] - 0.13) * min(1.0, (y - 2) / 12.0)
        dx = np.gradient(BX[:, bi]); dy = np.gradient(BY[:, bi])
        BYAW[:, bi] = np.where(np.hypot(dx, dy) > 1e-4, np.arctan2(-dx, np.maximum(dy, 1e-6)), 0.0)
    slots = [(-1.15 + 1.15 * (q % 3), -4.9 + 1.4 * (q // 3)) for q in range(SEATS)]
    for i, (bi, q, tb) in seat.items():
        sx, sy = slots[q]
        c, s_ = np.cos(BYAW[:, bi]), np.sin(BYAW[:, bi])
        wx = BX[:, bi] + c * sx - s_ * sy; wy = BY[:, bi] + s_ * sx + c * sy; wz = BZ[:, bi] + 0.55
        u = np.clip((T - tb) / 1.2, 0.0, 1.0)
        m = T >= tb
        PX[m, i] = (PX[m, i] * (1 - u[m]) + wx[m] * u[m]); PY[m, i] = PY[m, i] * (1 - u[m]) + wy[m] * u[m]
        PZ[m, i] = PZ[m, i] * (1 - u[m]) + wz[m] * u[m] + np.sin(np.pi * u[m]) * 0.6
        PS[m, i] = 3

    # ---- titans
    specs = []
    sp_by_rank = {s["rank"]: s for s in SPECIAL}
    for j in range(n_titans):
        if j in sp_by_rank:
            sp = dict(sp_by_rank[j])
        else:
            H = 3.0 + 12.0 * rnd.random() ** 1.25
            sp = dict(name=f"t{j}", H=H, g=rnd.uniform(0.8, 1.35), al=rnd.uniform(0.9, 1.15), hs=rnd.uniform(0.9, 1.3),
                      skin=rnd.randrange(len(T_SKINS)), hair=rnd.choice([None, 0, 1, 2, 3]), v=(1.6 + 0.33 * H) * rnd.uniform(0.85, 1.15))
        specs.append(sp)
    nt = len(specs)
    TX = np.zeros((K, nt)); TY = np.zeros((K, nt)); TYAW = np.zeros((K, nt)); TG = np.full((K, nt), -1e9)
    VJ = np.full(N, -1, np.int32); VTG = np.full(N, math.inf); VPOS = np.zeros((N, 3))
    tit = []
    for j, sp in enumerate(specs):
        dj = 4.0 + 4.2 * j + rnd.uniform(-1.5, 1.5)
        x = rnd.uniform(-1, 1) * min(dj * 0.5, 60.0)
        tit.append(dict(x=x, y=OGY - 8 - dj, yaw=0.0, head=(0.0, 1.0), mode="enter", wp=[(0.0, OGY - 8.0), (0.0, OGY + 18.0)],
                        tgt=None, cool=0.0, sated=0.0, tg=-1e9, chase=None))
    WT = Gd["WT"]; nx = Gd["nx"]
    alive = np.ones(N, bool)
    for k, t in enumerate(T):
        px, py = PX[k], PY[k]
        eat_ok = alive & (PS[k] == 0) & (t >= 0.0) & (py < -14.0)
        # people density (16 m bins) for the titans' drift
        if eat_ok.any():
            Dn, _, _ = np.histogram2d(px[eat_ok], py[eat_ok], bins=[int((X1 - X0) / 16), int((Y1 - Y0) / 16)], range=[[X0, X1], [Y0, Y1]])
        else:
            Dn = np.zeros((int((X1 - X0) / 16), int((Y1 - Y0) / 16)))
        for j, ti in enumerate(tit):
            sp = specs[j]; v = sp["v"]
            if t - ti["tg"] < EAT_DUR:
                pass
            elif ti["mode"] == "enter":
                wx, wy = ti["wp"][0]
                dx, dy = wx - ti["x"], wy - ti["y"]; dd = math.hypot(dx, dy)
                if dd < v * DT:
                    ti["wp"].pop(0)
                    if not ti["wp"]:
                        ti["mode"] = "wander"; ti["tgt"] = nearest_walk(Gd, ti["x"], ti["y"], "WT")
                else:
                    ti["x"] += dx / dd * v * DT; ti["y"] += dy / dd * v * DT; ti["head"] = (dx / dd, dy / dd)
            else:
                # grab?
                reach = 1.5 + 0.38 * sp["H"]
                if t >= ti["cool"] and eat_ok.any():
                    ddx = px - ti["x"]; ddy = py - ti["y"]; d2 = np.where(eat_ok, ddx * ddx + ddy * ddy, 1e12)
                    vi = int(np.argmin(d2)); dv = math.sqrt(d2[vi])
                    if dv < reach:
                        ti["tg"] = t; TG[k:, j] = t
                        VJ[vi] = j; VTG[vi] = t; VPOS[vi] = (px[vi], py[vi], PZ[k, vi]); alive[vi] = False; eat_ok[vi] = False
                        ti["yaw_lock"] = math.atan2(-(px[vi] - ti["x"]), py[vi] - ti["y"])
                        ti["cool"] = t + EAT_DUR + rnd.uniform(5, 14); ti["sated"] = t + EAT_DUR + rnd.uniform(5, 12)
                        a = rnd.uniform(0, math.tau); ti["head"] = (math.cos(a), math.sin(a)); ti["chase"] = None
                        TX[k, j], TY[k, j] = ti["x"], ti["y"]
                        continue
                    if dv < 14 + 0.8 * sp["H"] and t >= ti["sated"]:
                        mi, mj = cell(Gd, (px[vi] + ti["x"]) / 2, (py[vi] + ti["y"]) / 2)
                        if WT[mi, mj] and WT[cell(Gd, px[vi], py[vi])]:
                            ti["chase"] = vi
                        else:
                            ti["chase"] = None
                    else:
                        ti["chase"] = None
                if ti["chase"] is not None:
                    vi = ti["chase"]; dx, dy = px[vi] - ti["x"], py[vi] - ti["y"]; dd = math.hypot(dx, dy) + 1e-6
                    st = min(v * 1.3 * DT, max(0.0, dd - reach * 0.6))
                    ti["x"] += dx / dd * st; ti["y"] += dy / dd * st; ti["head"] = (dx / dd, dy / dd)
                    ti["tgt"] = None
                else:
                    if ti["tgt"] is None:
                        ti["tgt"] = nearest_walk(Gd, ti["x"], ti["y"], "WT")
                    gx, gy = Gd["xs"][ti["tgt"][0]], Gd["ys"][ti["tgt"][1]]
                    dx, dy = gx - ti["x"], gy - ti["y"]; dd = math.hypot(dx, dy)
                    if dd <= v * DT:
                        ti["x"], ti["y"] = gx, gy
                        hx, hy = ti["head"]; ci, cj = ti["tgt"]
                        sated = t < ti["sated"]
                        best, bs = None, -1e9
                        lure = None                       # direction to the nearest person (long-range drift)
                        if not sated and eat_ok.any():
                            ddx = px - gx; ddy = py - gy; d2 = np.where(eat_ok, ddx * ddx + ddy * ddy, 1e12)
                            q = int(np.argmin(d2)); dq = math.sqrt(d2[q])
                            if dq < 260:
                                lure = (ddx[q] / (dq + 1e-6), ddy[q] / (dq + 1e-6))
                        opts = [(di, dj) for di, dj in NB8 if 0 <= ci + di < nx and 0 <= cj + dj < ny and WT[ci + di, cj + dj]]
                        for di, dj in opts:
                            ln = math.hypot(di, dj); ux, uy = di / ln, dj / ln
                            cs = ux * hx + uy * hy
                            if cs < -0.8 and len(opts) > 1:
                                continue
                            ax, ay = gx + ux * 28, gy + uy * 28
                            bx_, by_ = int((ax - X0) // 16), int((ay - Y0) // 16)
                            dens = Dn[bx_, by_] if 0 <= bx_ < Dn.shape[0] and 0 <= by_ < Dn.shape[1] else 0.0
                            sc = 1.4 * cs + (0.0 if sated else 2.2 * min(1.0, dens / 4.0)) + rnd.uniform(0, 2.0 if sated else 1.0)
                            if lure:
                                sc += 1.8 * (ux * lure[0] + uy * lure[1])
                            if sc > bs:
                                bs, best = sc, (di, dj)
                        if best:
                            ln = math.hypot(*best)
                            ti["head"] = (best[0] / ln, best[1] / ln)
                            ti["tgt"] = (ci + best[0], cj + best[1])
                    else:
                        ti["x"] += dx / dd * v * DT; ti["y"] += dy / dd * v * DT
                        ti["head"] = (0.8 * ti["head"][0] + 0.2 * dx / dd, 0.8 * ti["head"][1] + 0.2 * dy / dd)
            TX[k, j], TY[k, j] = ti["x"], ti["y"]
    # titan yaw: follow motion (smoothed), locked toward the victim while eating
    for j in range(nt):
        yaw = 0.0
        for k in range(K):
            if k > 0:
                dx, dy = TX[k, j] - TX[k - 1, j], TY[k, j] - TY[k - 1, j]
                if T[k] - TG[k, j] < EAT_DUR:
                    tgt = None
                    vi = np.where((VJ == j) & (np.abs(VTG - TG[k, j]) < 1e-6))[0]
                    if len(vi):
                        q = vi[0]; tgt = math.atan2(-(VPOS[q, 0] - TX[k, j]), VPOS[q, 1] - TY[k, j])
                elif dx * dx + dy * dy > 1e-6:
                    tgt = math.atan2(-dx, dy)
                else:
                    tgt = None
                if tgt is not None:
                    dyaw = (tgt - yaw + math.pi) % math.tau - math.pi
                    yaw += max(-0.45, min(0.45, dyaw))
            TYAW[k, j] = yaw
    # grabbed people: frozen at the grab spot from tg on (update() then hangs them from the hand)
    for i in np.where(VJ >= 0)[0]:
        m = T >= VTG[i]
        PX[m, i], PY[m, i], PZ[m, i] = VPOS[i]
        PS[m, i] = np.where(T[m] < VTG[i] + 2.4, 1, 2)
    # people yaw (smoothed, from motion) + walked distance (ground only)
    PYAW = np.zeros((K, N)); PD = np.zeros((K, N))
    yaw = yaw0.copy(); dist = np.zeros(N)
    for k in range(K):
        if k > 0:
            dx, dy = PX[k] - PX[k - 1], PY[k] - PY[k - 1]
            mv = (dx * dx + dy * dy > 0.0004) & (PS[k] == 0)
            tgt = np.arctan2(-dx, dy)
            dyaw = (tgt - yaw + np.pi) % (2 * np.pi) - np.pi
            yaw = np.where(mv, yaw + np.clip(dyaw, -0.7, 0.7), yaw)
            dist = dist + np.where(PS[k] == 0, np.hypot(dx, dy), 0.0)
        PYAW[k] = yaw; PD[k] = dist
    TD = np.zeros((K, nt)); TD[1:] = np.cumsum(np.hypot(np.diff(TX, axis=0), np.diff(TY, axis=0)), axis=0)
    TZ = np.zeros((K, nt))
    ii = np.clip(((TX - X0) // G).astype(int), 0, nx - 1); jj = np.clip(((TY - Y0) // G).astype(int), 0, ny - 1)
    TZ[:] = np.maximum(Gd["Z"][ii, jj], 0.05)
    t_sim = time.time() - t_start

    # ---- Blender objects
    coll = bpy.data.collections.get("Swarm845") or L.new_coll("Swarm845")
    gp = Geo(); pmat = []
    shirt_i = np.array([rnd.randrange(len(SHIRTS)) for _ in range(N)]); pants_i = np.array([rnd.randrange(len(PANTS)) for _ in range(N)])
    skin_i = np.array([rnd.randrange(len(SKINS)) for _ in range(N)]); hair_i = np.array([rnd.choice([0, 0, 1, 1, 1, 2, 3, 4]) for _ in range(N)])
    for i in range(N):
        n0 = len(gp.fc)
        person_geo(gp, i, hgt[i], rnd.random() < 0.3, rnd)
        base = [shirt_i[i], len(SHIRTS) + pants_i[i], len(SHIRTS) + len(PANTS) + skin_i[i], len(SHIRTS) + len(PANTS) + len(SKINS) + hair_i[i]]
        pmat += [base[c] for c in gp.fc[n0:]]
    mats = [L.mat(f"SW_shirt{i}", c, 0.75) for i, c in enumerate(SHIRTS)] + [L.mat(f"SW_pants{i}", c, 0.85) for i, c in enumerate(PANTS)] \
        + [L.mat(f"SW_skin{i}", c, 0.6) for i, c in enumerate(SKINS)] + [L.mat(f"SW_hair{i}", c, 0.7) for i, c in enumerate(HAIRS)]
    RP = gp.finish()
    pob = _mesh("SwarmPeople", RP, gp.f, pmat, mats, coll)
    gt = Geo(); tmat = []; hands = []
    for j, sp in enumerate(specs):
        n0 = len(gt.fc)
        sx, sh, la, hip, hc, hr = titan_geo(gt, j, sp)
        sp.update(sx=sx, sh=sh, la=la, hip=hip, hc=hc, hr=hr)
        hb = len(T_SKINS)
        base = [sp["skin"], hb + (sp["hair"] if sp.get("hair") is not None else 0), hb + len(T_HAIRS)]
        tmat += [base[c] for c in gt.fc[n0:]]
        hands.append((sx, 0.0, sh - 2 * la, j, sh, sh - la, hip))
    tm = [L.mat(f"SW_tskin{i}", c, 0.65, sss=0.0) for i, c in enumerate(T_SKINS)] + [L.mat(f"SW_thair{i}", c, 0.7) for i, c in enumerate(T_HAIRS)] \
        + [L.mat("SW_teeth", (0.85, 0.80, 0.70), 0.5)]
    RT = gt.finish()
    tob = _mesh("SwarmTitans", RT, gt.f, tmat, tm, coll)
    RH = {"B": np.array([h[:3] for h in hands], float), "oid": np.arange(nt, dtype=np.int32), "part": np.full(nt, 5, np.int32),
          "pr": np.array([(0, h[4]) for h in hands], float), "pe": np.array([(0, h[5]) for h in hands], float),
          "hip": np.array([h[6] for h in hands], float), "up": np.ones(nt)}
    # boats + piers
    from mathutils import Vector
    import bmesh
    wood = L.mat("SW_boat", (0.22, 0.11, 0.05), 0.8); plank = L.mat("SW_plank", (0.36, 0.24, 0.12), 0.85)
    bm = bmesh.new()
    L.box(bm, (0, -0.6, 0.2), (4.2, 11.8, 0.9), taper=(1.0, 1.0))
    L.box(bm, (0, 5.9, 0.25), (2.6, 2.4, 0.8), taper=(0.3, 1.0))
    L.box(bm, (0, -6.4, 0.45), (3.4, 0.6, 0.7))
    for sxx in (-1, 1):
        L.box(bm, (sxx * 2.0, -0.6, 0.75), (0.25, 11.6, 0.35), mi=1)
    bme = bpy.data.meshes.new("SwarmBoat"); bm.to_mesh(bme); bm.free(); bme.materials.append(wood); bme.materials.append(plank)
    bobs = []
    for bi in range(nbt):
        o = bpy.data.objects.new(f"SwarmBoat{bi}", bme); coll.objects.link(o); bobs.append(o)
    bm = bmesh.new()
    for yd in DOCK_Y:
        L.box(bm, (CX - CW / 2 + 1.0, yd, 0.3), (4.0, 18.0, 0.25))
        for q in range(4):
            L.box(bm, (CX - CW / 2 + 2.8, yd - 8 + q * 5.3, 0.1), (0.35, 0.35, 1.6))
    L.obj_from_bm("SwarmPiers", bm, [plank], coll)
    STATE.clear()
    STATE.update(K=K, T=T, N=N, nt=nt, PX=PX.astype(np.float32), PY=PY.astype(np.float32), PZ=PZ.astype(np.float32), PS=PS,
                 PYAW=PYAW.astype(np.float32), PD=PD.astype(np.float32), yaw0=yaw0, hgt=hgt, t_go=t_go,
                 street=np.array([s[2] for s in starts], bool),
                 TX=TX, TY=TY, TZ=TZ, TYAW=TYAW, TD=TD, TG=TG, VJ=VJ, VTG=VTG, VPOS=VPOS,
                 BX=BX, BY=BY, BZ=BZ, BYAW=BYAW, boats=boats, bobs=bobs, specs=specs,
                 RP=RP, RT=RT, RH=RH, pob=pob, tob=tob, grid=Gd, seat=seat, goal=goal,
                 t_end=t_end, timings=dict(grid=t_grid, sim=t_sim - t_grid, total=time.time() - t_start))
    update(0.0)
    print(f"[swarm845] people {N} titans {nt} boats {nbt} eaten {int((VJ >= 0).sum())} seated {len(seat)} "
          f"grid {t_grid:.1f}s sim {t_sim - t_grid:.1f}s total {time.time() - t_start:.1f}s")
    return STATE

# ---------------------------------------------------------------- per-frame
def _lerp_idx(t):
    S = STATE
    tt = min(max(t, 0.0), S["t_end"])
    kf = tt / DT; k0 = min(int(kf), S["K"] - 1); k1 = min(k0 + 1, S["K"] - 1); f = kf - k0
    return k0, k1, f

def _alerp(a, b, f):
    return a + (((b - a) + np.pi) % (2 * np.pi) - np.pi) * f

def update(t, pscale=None):
    """Set every person, titan and boat for time t (seconds after the kick impact). Pure function of t.
    pscale overrides PEOPLE_SCALE for this call (people drawn larger than life for high shots)."""
    global PEOPLE_SCALE
    if pscale is not None:
        PEOPLE_SCALE = float(pscale)
    S = STATE
    if not S:
        return
    t = float(t)
    k0, k1, f = _lerp_idx(t)
    N, nt = S["N"], S["nt"]
    # ---------------- titans
    tvis = t >= 0.0
    S["tob"].hide_render = S["tob"].hide_viewport = not tvis
    tpos = np.stack([S["TX"][k0] * (1 - f) + S["TX"][k1] * f, S["TY"][k0] * (1 - f) + S["TY"][k1] * f,
                     S["TZ"][k0] * (1 - f) + S["TZ"][k1] * f], 1)
    tyaw = _alerp(S["TYAW"][k0], S["TYAW"][k1], f)
    td = S["TD"][k0] * (1 - f) + S["TD"][k1] * f
    tspd = (S["TD"][k1] - S["TD"][k0]) / DT
    H = np.array([sp["H"] for sp in S["specs"]])
    ph = 2 * np.pi * td / (0.55 * H + 0.5)
    mv = np.clip(tspd / 1.0, 0.0, 1.0)
    Ar = np.zeros((nt, 7)); Ae = np.zeros((nt, 7)); lean = np.zeros(nt)
    sw = np.sin(ph) * 0.42 * mv
    Ar[:, 1] = sw; Ar[:, 2] = -sw; Ar[:, 3] = -0.7 * sw; Ar[:, 4] = 0.7 * sw
    Ae[:, 5] = Ae[:, 6] = 0.25 + 0.15 * mv                 # slightly bent elbows: the dopey pure-titan stance
    lean[:] = -0.06 - 0.06 * mv + 0.03 * np.sin(t * 0.7 + np.arange(nt))
    tg = np.where(S["TG"][k1] <= t, S["TG"][k1], S["TG"][k0])
    e = t - tg
    for j in np.where((e >= 0) & (e < EAT_DUR))[0]:
        ej = e[j]
        if ej < 0.7:
            u = _smooth(ej / 0.7); a, b, l = 0.95 * u, 0.3 * u, -0.6 * u
        elif ej < 1.0:
            a, b, l = 0.95, 0.3, -0.6
        elif ej < 2.0:
            u = _smooth(ej - 1.0); a, b, l = 0.95 + 0.09 * u, 0.3 + 2.115 * u, -0.6 + 0.65 * u
        elif ej < 2.4:
            a, b, l = 1.04, 2.415, 0.05
        else:
            u = _smooth(ej - 2.4); a, b, l = 1.04 * (1 - u), 2.415 * (1 - u) + 0.25 * u, 0.05 - 0.11 * u
        Ar[j, 1] = Ar[j, 2] = 0.0; Ar[j, 3] = 0.15 * math.sin(ej * 6)
        Ar[j, 4] = a; Ae[j, 5] = b; lean[j] = l
    Ar[:, 5] = Ar[:, 4]; Ar[:, 6] = Ar[:, 3]
    bob = (0.5 - 0.5 * np.cos(2 * ph)) * 0.025 * H * mv
    tp = tpos.copy(); tp[:, 2] += bob
    tvisv = np.ones(nt)
    for j, sp in enumerate(S["specs"]):
        if j in HIDE_TITANS or sp["name"] in HIDE_TITANS:
            tvisv[j] = 0.0
    co = _deform(S["RT"], Ar, Ae, lean, tvisv, tyaw, tp)
    S["tob"].data.vertices.foreach_set("co", co.astype(np.float32).ravel()); S["tob"].data.update()
    hand = _deform(S["RH"], Ar, Ae, lean, tvisv, tyaw, tp)
    # ---------------- people
    PX, PY, PZ = S["PX"], S["PY"], S["PZ"]
    pos = np.stack([PX[k0] * (1 - f) + PX[k1] * f, PY[k0] * (1 - f) + PY[k1] * f, PZ[k0] * (1 - f) + PZ[k1] * f], 1).astype(float)
    yaw = _alerp(S["PYAW"][k0], S["PYAW"][k1], f).astype(float)
    pd = (S["PD"][k0] * (1 - f) + S["PD"][k1] * f).astype(float)
    spd = (S["PD"][k1] - S["PD"][k0]) / DT
    hg = S["hgt"]
    pm = np.clip(spd / 1.6, 0.0, 1.0)
    pph = 2 * np.pi * pd / (1.5 * hg)
    PAr = np.zeros((N, 7)); PAe = np.zeros((N, 7)); plean = -0.22 * pm
    s = np.sin(pph) * 0.75 * pm
    PAr[:, 1] = s; PAr[:, 2] = -s; PAr[:, 3] = -0.8 * s; PAr[:, 4] = 0.8 * s
    vis = np.full(N, PEOPLE_SCALE)
    pos[:, 2] += (0.5 - 0.5 * np.cos(2 * pph)) * 0.08 * pm
    if t < 0.0:
        yaw = S["yaw0"].copy()
        idle = np.arange(N) * 1.7
        plean = 0.03 * np.sin(t * 0.8 + idle)
        PAr[:, 3] = PAr[:, 4] = 0.05 * np.sin(t * 1.3 + idle)
    else:
        if 0.15 < t < 0.75:
            dly = (np.arange(N) % 7) * 0.02
            u = np.clip((t - 0.15 - dly) / 0.45, 0.0, 1.0) * ~S["street"]
            pos[:, 2] += np.sin(np.pi * u) * 0.28
            PAr[:, 3] += np.sin(np.pi * u) * 2.0; PAr[:, 4] += np.sin(np.pi * u) * 2.0
        wait = (t < S["t_go"]) & (pm < 0.05)
        PAr[wait, 3] = PAr[wait, 4] = 0.4 + 0.3 * np.sin(t * 4 + np.arange(N)[wait])
    held = np.where((S["VJ"] >= 0) & (t >= S["VTG"]))[0]
    for i in held:
        e = t - S["VTG"][i]; j = S["VJ"][i]
        if e >= 2.4:
            vis[i] = 0.0; continue
        PAr[i, 3] = PAr[i, 4] = 2.7 + 0.35 * math.sin(e * 14)
        PAr[i, 1] = 0.5 * math.sin(e * 11); PAr[i, 2] = -PAr[i, 1]; plean[i] = 0.0
        hp = hand[j] - np.array([0, 0, 1.0 * hg[i] / 1.7])
        if e < 0.7:
            pos[i] = S["VPOS"][i]; pos[i, 2] += abs(math.sin(e * 9)) * 0.15
        else:
            u = _smooth((e - 0.7) / 0.3)
            pos[i] = S["VPOS"][i] * (1 - u) + hp * u
            yaw[i] = tyaw[j] + math.pi
        if e > 2.0:
            vis[i] = max(0.0, 1.0 - (e - 2.0) / 0.4) * PEOPLE_SCALE
            m = np.array([0, 0.09 * H[j], 0.0])
            c, sn = math.cos(tyaw[j]), math.sin(tyaw[j])
            mouth = tpos[j] + np.array([-sn * m[1], c * m[1], S["specs"][j]["hc"] - 0.2 * S["specs"][j]["hr"]])
            u = 1.0 - vis[i] / PEOPLE_SCALE
            pos[i] = pos[i] * (1 - u) + mouth * u
    co = _deform(S["RP"], PAr, PAe, plean, vis, yaw, pos)
    S["pob"].data.vertices.foreach_set("co", co.astype(np.float32).ravel()); S["pob"].data.update()
    # ---------------- boats
    for bi, o in enumerate(S["bobs"]):
        o.location = (S["BX"][k0, bi] * (1 - f) + S["BX"][k1, bi] * f, S["BY"][k0, bi] * (1 - f) + S["BY"][k1, bi] * f,
                      S["BZ"][k0, bi] * (1 - f) + S["BZ"][k1, bi] * f + 0.05 * math.sin(t * 1.3 + bi))
        o.rotation_euler = (0.0, 0.015 * math.sin(t * 0.9 + bi * 2), float(_alerp(S["BYAW"][k0, bi], S["BYAW"][k1, bi], f)))

def titan_pos(which, t):
    S = STATE
    j = which if isinstance(which, int) else [sp["name"] for sp in S["specs"]].index(which)
    k0, k1, f = _lerp_idx(t)
    return (S["TX"][k0, j] * (1 - f) + S["TX"][k1, j] * f, S["TY"][k0, j] * (1 - f) + S["TY"][k1, j] * f,
            S["TZ"][k0, j], float(_alerp(S["TYAW"][k0, j], S["TYAW"][k1, j], f)))

def info():
    S = STATE
    return dict(people=S["N"], titans=S["nt"], boats=len(S["bobs"]), eaten=int((S["VJ"] >= 0).sum()), seated=len(S["seat"]),
                departed=sum(1 for b in S["boats"] if b["dep"] < math.inf), timings=S["timings"])

# ---------------------------------------------------------------- plug-in hooks
def build(M, year, ctx):
    if os.environ.get("SWARM", "0") != "1":
        return
    setup()
    if "SWARM_T" in os.environ:
        t0 = time.time(); update(float(os.environ["SWARM_T"]))
        print(f"[swarm845] update({os.environ['SWARM_T']}) {1000 * (time.time() - t0):.1f} ms", info())

CAMS = {
    "swarm_plaza": ((PXC + 25, PYC - 80, 75), (PXC, PYC - 5, 0), 35),
    "swarm_town":  ((70, OGY - 120, 240), (0, -380, 0), 26),
    "swarm_gate":  ((40, OGY + 170, 110), (0, OGY + 40, 0), 32),
    "swarm_canal": ((120, -330, 120), (CX - 10, -250, 0), 32),
    "swarm_igate": ((60, -150, 110), (0, -20, 0), 32),
    "swarm_mid":   ((110, -480, 150), (0, OGY + 60, 0), 30),
}
