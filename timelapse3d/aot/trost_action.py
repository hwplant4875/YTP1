"""850 Trost: the action layer (titans flood, cadet squads on ODM, Eren eaten, Mikasa falls, the rogue Attack Titan,
Armin's supply-HQ lift plan, Eren out of the nape, the cannonball and the half-shift skeleton, Armin's salute,
the boulder operation with red / yellow flares, Levi's entrance, the pyres and Marco).  A pure function of time.

Positions come from a SITE dict (agent C's Trost set, or the Shiganshina stand-in in render_trost_action.py), so the
integration is a parameter swap:
    site = dict(
        gate=(x, y),            breached south gate at the wall line (titans enter here; the boulder seals it)
        inward=(dx, dy),        unit vector from the gate into the district
        wall_z=50.0,            wall top height above the gate ground
        hq=(x, y), hq_size=(w, d, h), hq_roof=[objects hidden for the cutaway],   supply HQ
        boulder=(x, y),         the boulder's resting place
        roofs=np.array(N, 3),   rooftop perch points (x, y, z) for the squads
        ground=fn(x, y)->z, walkable=fn(x, y)->bool (streets, plazas, the gate passage, outside the gate),
        bounds=(x0, x1, y0, y1),
        pyre=(x, y),            dusk pyres square
        fall_pt=(x, y)          optional: street where Mikasa falls (default: auto between the gate and the HQ)
        wall_pts=[(x, y, z)]    optional wall-top points near the gate (Garrison, lure squads, yellow flare)
    )

API (t = seconds after the Colossal's kick on Trost's south gate, the same clock as swarm845):
    import trost_action as TA
    TA.setup(site, seed=850, light=False)     # once per Blender session (~20-40 s: nav grid, tracks, meshes)
    TA.update(t)                              # every frame; same t -> same picture
    TA.BEATS                                  # beat name -> (t0, t1) windows for the edit / the flight
    TA.hero_pos(name, t)                      # eren mikasa armin jean marco connie levi rico ... "attack" "boulder"
    TA.STATE                                  # internals (squads, titans, flares, attack titan, objects)
Reused systems: swarm845 (titan geometry / rig / palettes, nav-grid Dijkstra), attack_titan (the Attack Titan, poses,
shift FX, boulder), odm (squads), flares (flares and puff fields).
"""
import math, os, random, time
import numpy as np
import bpy
from mathutils import Vector

import aotlib as L
import swarm845 as SW
import attack_titan as AT
import odm
import flares as FX

STATE = {}
DT = 0.2
PS = float(os.environ.get("TA_PSCALE", "1.0"))           # user rule: every human at TRUE scale (1.0)
KEY = float(os.environ.get("TA_KEY_SCALE", "1.2"))             # key titans: bearded, the HQ seven, Levi's two, flood leaders
EREN_ACCENT = (0.04, 0.80, 0.32)                                 # emerald collar + hem (emissive), Eren's unique cue
EREN_CLOAK = (0.13, 0.19, 0.07)                                  # green-tinted brown cloak

BEATS = {
    "evacuation":   (2.0, 22.0),    # crowd jammed at the inner gate behind the cargo wagon; Mikasa; the crowd floods out
    "flood":        (2.0, 16.0),    # titans pour through the gate, squads deploy over the rooftops
    "eren_eaten":   (7.5, 14.0),    # squad 34: Thomas grabbed, Eren's leg bitten, Armin grabbed, Eren swallowed
    "squad_wiped":  (14.5, 17.5),   # a big titan sweeps a squad off a roof
    "hq_despair":   (17.0, 21.0),   # titans crowd the supply HQ; cadets stranded on the roofs around it
    "mikasa_falls": (21.0, 26.5),   # Mikasa's dash, out of gas, falls into a street; a titan closes in
    "attack_titan": (26.5, 44.0),   # the rogue titan appears (lightning) and kills titans on its way to the HQ
    "bell_tower":   (27.5, 35.0),   # the rogue titan appears by the church and slams a titan down at the bell tower's foot
    "hq_dash":      (42.0, 46.0),   # the cadets fly into the HQ while the rogue titan keeps the titans busy
    "lift_plan":    (46.0, 54.0),   # cutaway: lift with a ring of rifles, eye volley, seven blades on seven napes
    "at_collapse":  (53.0, 56.5),
    "emerge":       (56.5, 59.0),   # Eren out of the nape (quick), Mikasa pulls him free
    "cannon":       (59.0, 63.5),   # Garrison ring, the cannon fires, the half-shift skeleton blocks it in steam
    "salute":       (63.5, 68.0),   # Armin steps out of the steam in the Shinzou wo sasageyo salute
    "pyxis":        (68.5, 74.5),   # Pixis on the wall top above the inner gate; deserters turn back
    "boulder_shift": (74.5, 79.0),  # Eren shifts by the boulder, goes berserk: RED flare
    "boulder_stab": (79.0, 82.0),   # Armin's blade in the nape: Eren wakes
    "boulder_carry": (82.0, 99.0),  # lift, the walk to the breach, the elite squad cutting down titans around him
    "boulder_seal": (99.0, 104.0),  # the boulder drops into the gate; YELLOW flare
    "levi":         (104.0, 111.0), # Levi's entrance: a dive and a fast spinning slash, standing on the corpse
    "pyres":        (113.0, 125.0), # dusk pyres
    "marco":        (117.5, 120.5), # Jean finds Marco (hold ~2-3 s)
}
B = {k: v for k, v in BEATS.items()}

def _ss(a, b, x):
    u = min(1.0, max(0.0, (x - a) / (b - a))) if b != a else float(x >= b)
    return u * u * (3 - 2 * u)

def v2(p):
    return np.array([float(p[0]), float(p[1])])

def v3(p):
    return np.array([float(p[0]), float(p[1]), float(p[2])])

# ====================================================================== site helpers
class Site:
    def __init__(self, d):
        self.d = d
        self.gate = v2(d["gate"]); self.inw = v2(d.get("inward", (0, 1))); self.inw /= np.linalg.norm(self.inw)
        self.side = np.array([self.inw[1], -self.inw[0]])
        self.wall_z = float(d.get("wall_z", 50.0))
        self.hq = v2(d["hq"]); self.hq_size = d.get("hq_size", (30.0, 22.0, 12.0))
        self.boulder = v2(d["boulder"])
        self.roofs = np.asarray(d["roofs"], float)
        self.ground = d["ground"]; self.walkable = d["walkable"]
        self.bounds = d["bounds"]
        self.pyre = v2(d["pyre"])
        self.wall_pts = [v3(p) for p in d.get("wall_pts", [])] or [v3((*(self.gate + self.side * s * 30 - self.inw * 2), self.wall_z)) for s in (-1, 1, -2, 2, -3, 3)]
        self.grid = None

    def g(self, p):
        return float(self.ground(float(p[0]), float(p[1])))

    def P(self, xy, dz=0.0):
        return np.array([xy[0], xy[1], self.g(xy) + dz])

    def local(self, a, b):
        """Point at a metres inward from the gate and b metres to the side."""
        return self.gate + self.inw * a + self.side * b

    def roof_near(self, p, used=None, rmin=0.0):
        d = np.hypot(self.roofs[:, 0] - p[0], self.roofs[:, 1] - p[1])
        if used:
            d = d.copy(); d[list(used)] = 1e9
        if rmin > 0:
            d = np.where(d < rmin, 1e9, d)
        i = int(np.argmin(d))
        return i, self.roofs[i]

    def roofs_near(self, p, n, used=None, spread=6.0):
        out = []
        used = set(used or ())
        for _ in range(n):
            d = np.hypot(self.roofs[:, 0] - p[0], self.roofs[:, 1] - p[1])
            for k in used:
                d[k] = 1e9
            i = int(np.argmin(d)); used.add(i); out.append(i)
        return out

    def snap(self, p):
        Gd = self.nav()
        i, j = _nearest(Gd, p[0], p[1])
        return np.array([Gd["xs"][i], Gd["ys"][j]])

    def nav(self):
        if self.grid is None:
            self.grid = build_grid(self)
        return self.grid


# ====================================================================== nav grid (swarm845's Dijkstra on our own grid)
GC = SW.G       # 4 m cells (SW.dijkstra uses this constant)

def build_grid(site):
    x0, x1, y0, y1 = site.bounds
    nx, ny = int((x1 - x0) / GC), int((y1 - y0) / GC)
    xs = x0 + (np.arange(nx) + 0.5) * GC; ys = y0 + (np.arange(ny) + 0.5) * GC
    W = np.zeros((nx, ny), bool)
    for i, x in enumerate(xs):
        for j, y in enumerate(ys):
            W[i, j] = bool(site.walkable(float(x), float(y)))
    cur = W.copy(); clr = W.astype(float)
    for _ in range(4):
        n = cur.copy()
        n[1:, :] &= cur[:-1, :]; n[:-1, :] &= cur[1:, :]; n[:, 1:] &= cur[:, :-1]; n[:, :-1] &= cur[:, 1:]
        n[0, :] = n[-1, :] = n[:, 0] = n[:, -1] = False
        cur = n; clr += cur
    return dict(nx=nx, ny=ny, xs=xs, ys=ys, W=W, clr=clr, x0=x0, y0=y0, cache={})

def _cell(Gd, x, y):
    return (int(min(Gd["nx"] - 1, max(0, (x - Gd["x0"]) // GC))), int(min(Gd["ny"] - 1, max(0, (y - Gd["y0"]) // GC))))

def _nearest(Gd, x, y):
    i, j = _cell(Gd, x, y)
    if Gd["W"][i, j]:
        return i, j
    best = None
    for r in range(1, 30):
        for di in range(-r, r + 1):
            for dj in (-r, r) if abs(di) != r else range(-r, r + 1):
                ii, jj = i + di, j + dj
                if 0 <= ii < Gd["nx"] and 0 <= jj < Gd["ny"] and Gd["W"][ii, jj]:
                    d = di * di + dj * dj
                    if best is None or d < best[0]:
                        best = (d, ii, jj)
        if best:
            return best[1], best[2]
    return i, j

def path(site, a, b, lat=0.0):
    """Walkable polyline from a to b (both (x, y)); returns (P (n, 2), cumulative s)."""
    Gd = site.nav()
    gb = _nearest(Gd, b[0], b[1])
    if gb not in Gd["cache"]:
        Gd["cache"][gb] = SW.dijkstra(Gd, [gb])
    dist = Gd["cache"][gb]
    ia = _nearest(Gd, a[0], a[1])
    if dist[ia[0] * Gd["ny"] + ia[1]] == math.inf:
        P = np.array([a, b], float)
    else:
        cells = SW.descend(Gd, dist, *ia)
        P, _ = SW.make_path(Gd, (float(a[0]), float(a[1])), cells, (float(b[0]), float(b[1])), lat, None)
    seg = np.linalg.norm(np.diff(P, axis=0), axis=1)
    return P, np.concatenate([[0.0], np.cumsum(seg)])


# ====================================================================== titans (thin wrapper over swarm845's figures)
EAT_DUR = SW.EAT_DUR

class Titans:
    """Scripted pure titans: flood paths on the nav grid or explicit keys, plus events (grab, swat, blind, leap,
    death).  Geometry / rig / palettes are swarm845's (SW.titan_geo, SW._mesh); pitch for falls via odm.deform."""
    def __init__(self, site, seed=850):
        self.site = site
        self.rnd = random.Random(seed)
        self.specs, self.legs, self.keys, self.ev, self.show = [], [], [], [], []
        self.idx = {}
        self._cache_t = None

    def add(self, name, H=None, legs=None, keys=None, show=(-1e9, 1e9), **sp):
        r = self.rnd
        if H is None:
            H = 3.0 + 12.0 * r.random() ** 1.25
        H = H * float(sp.pop("scale", 1.0))          # per-titan scale (key titans), baked into the merged mesh at build
        spec = dict(name=name, H=H, g=sp.pop("g", r.uniform(0.8, 1.35)), al=sp.pop("al", r.uniform(0.9, 1.15)),
                    hs=sp.pop("hs", r.uniform(0.9, 1.3)), skin=sp.pop("skin", r.randrange(len(SW.T_SKINS))),
                    hair=sp.pop("hair", r.choice([None, 0, 1, 2, 3])), **sp)
        spec.setdefault("v", (1.6 + 0.33 * H) * r.uniform(0.85, 1.15) * 1.5)
        self.idx[name] = len(self.specs)
        self.specs.append(spec); self.legs.append(legs or []); self.keys.append(keys); self.show.append(show)
        self.ev.append(dict(death=None, grab=[], swat=[], blind=None, leap=None, lean=None, abnormal=sp.get("abnormal", False)))
        return len(self.specs) - 1

    def j(self, name):
        return name if isinstance(name, int) else self.idx[name]

    def leg(self, name, t0, a, b, v=None):
        """Walk from a to b on the streets starting at t0 (queued after the previous leg if it is still walking)."""
        j = self.j(name)
        P, s = path(self.site, a, b, self.rnd.uniform(-1, 1))
        self.legs[j].append([t0, P, s, v or self.specs[j]["v"]])

    def sim(self, t_end):
        K = int(round(t_end / DT)) + 1
        T = np.arange(K) * DT
        nt = len(self.specs)
        TX = np.zeros((K, nt)); TY = np.zeros((K, nt))
        for j in range(nt):
            if self.keys[j] is not None:
                ks = self.keys[j]
                kt = np.array([k[0] for k in ks]); kx = np.array([k[1] for k in ks]); ky = np.array([k[2] for k in ks])
                TX[:, j] = np.interp(T, kt, kx); TY[:, j] = np.interp(T, kt, ky)
                continue
            legs = self.legs[j]
            if not legs:
                continue
            tcur = -1e9
            px, py = np.full(K, legs[0][1][0, 0]), np.full(K, legs[0][1][0, 1])
            for lg in legs:
                t0, P, s, v = lg
                t0 = max(t0, tcur)
                lg[0] = t0
                sk = np.clip(v * (T - t0), 0.0, s[-1])
                m = T >= t0
                px[m] = np.interp(sk[m], s, P[:, 0]); py[m] = np.interp(sk[m], s, P[:, 1])
                tcur = t0 + s[-1] / v
            TX[:, j], TY[:, j] = px, py
        # freeze after death
        for j in range(nt):
            d = self.ev[j]["death"]
            if d:
                k = min(K - 1, int(d[0] / DT))
                TX[k:, j] = TX[k, j]; TY[k:, j] = TY[k, j]
        # yaw from motion (smoothed); explicit face targets override while standing
        TYAW = np.zeros((K, nt))
        for j in range(nt):
            yaw = self.specs[j].get("yaw0", 0.0)
            for k in range(K):
                if k > 0:
                    dx, dy = TX[k, j] - TX[k - 1, j], TY[k, j] - TY[k - 1, j]
                    tgt = None
                    if dx * dx + dy * dy > 1e-5:
                        tgt = math.atan2(-dx, dy)
                    face = self.specs[j].get("face")
                    if face is not None and dx * dx + dy * dy < 1e-3:
                        f = face(T[k]) if callable(face) else face
                        if f is not None:
                            tgt = math.atan2(-(f[0] - TX[k, j]), f[1] - TY[k, j])
                    if tgt is not None:
                        dyaw = (tgt - yaw + math.pi) % math.tau - math.pi
                        yaw += max(-0.35, min(0.35, dyaw))
                TYAW[k, j] = yaw
        TD = np.zeros((K, nt)); TD[1:] = np.cumsum(np.hypot(np.diff(TX, axis=0), np.diff(TY, axis=0)), axis=0)
        gz = np.vectorize(lambda x, y: self.site.g((x, y)))
        TZ = np.zeros((K, nt))
        for j in range(nt):
            sub = np.arange(0, K, 5)
            TZ[:, j] = np.interp(np.arange(K), sub, gz(TX[sub, j], TY[sub, j]))
        self.K, self.T, self.TX, self.TY, self.TZ, self.TYAW, self.TD, self.t_end = K, T, TX, TY, TZ, TYAW, TD, t_end
        self.H = np.array([sp["H"] for sp in self.specs])
        self._cache_t = None
        if not hasattr(self, "RX") or len(self.RX["oid"]) != 4 * nt:
            self._rig_only()

    def _rig_only(self):
        """Hand / mouth / nape / crown rig points (needed for sampling before build())."""
        g = SW.Geo()
        Bp, oid, part, pr, pe, hip = [], [], [], [], [], []
        for j, sp in enumerate(self.specs):
            sx, sh, la, hp, hc, hr = SW.titan_geo(g, j, sp)
            sp.update(sx=sx, sh=sh, la=la, hip=hp, hc=hc, hr=hr)
            for (x, y, z, p, a, b) in [(sx, 0.0, sh - 2 * la, 5, (0, sh), (0, sh - la)), (0.0, hr * 0.9, hc - hr * 0.3, 0, (0, 0), (0, 0)),
                                       (0.0, -hr * 0.9, hc - hr * 1.1, 0, (0, 0), (0, 0)), (0.0, 0.0, hc + hr * 1.05, 0, (0, 0), (0, 0))]:
                Bp.append((x, y, z)); oid.append(j); part.append(p); pr.append(a); pe.append(b); hip.append(hp)
        self.RX = {"B": np.array(Bp, float), "oid": np.array(oid, np.int32), "part": np.array(part, np.int32),
                   "pr": np.array(pr, float), "pe": np.array(pe, float), "hip": np.array(hip, float)}
        self.RX["up"] = np.isin(self.RX["part"], (0, 3, 4, 5, 6)).astype(float)

    def build(self, coll):
        gt = SW.Geo(); tmat = []; rig = []
        hb = len(SW.T_SKINS)
        for j, sp in enumerate(self.specs):
            n0 = len(gt.fc)
            sx, sh, la, hip, hc, hr = SW.titan_geo(gt, j, sp)
            sp.update(sx=sx, sh=sh, la=la, hip=hip, hc=hc, hr=hr)
            if sp.get("beard"):
                gt.box((0, hr * 0.55, hc - hr * 0.75), (hr * 1.2, hr * 0.7, hr * 0.8), 1, j, 0, (0, 0), (0, 0), hip, taper=0.6)
            base = [sp["skin"], hb + (sp["hair"] if sp.get("hair") is not None else 0), hb + len(SW.T_HAIRS)]
            if sp.get("beard") and sp.get("hair") is None:
                base[1] = hb + 1
            tmat += [base[c] for c in gt.fc[n0:]]
            H = sp["H"]
            rig.append([(sx, 0.0, sh - 2 * la, 5, (0, sh), (0, sh - la)),            # right hand
                        (0.0, hr * 0.9, hc - hr * 0.3, 0, (0, 0), (0, 0)),          # mouth
                        (0.0, -hr * 0.9, hc - hr * 1.1, 0, (0, 0), (0, 0)),        # nape
                        (0.0, 0.0, hc + hr * 1.05, 0, (0, 0), (0, 0))])             # crown
        tm = [L.mat(f"TA_tskin{i}", c, 0.65) for i, c in enumerate(SW.T_SKINS)] + [L.mat(f"TA_thair{i}", c, 0.7) for i, c in enumerate(SW.T_HAIRS)] \
            + [L.mat("TA_teeth", (0.85, 0.80, 0.70), 0.5)]
        self.R = gt.finish()
        self.ob = SW._mesh("TrostTitans", self.R, gt.f, tmat, tm, coll)
        nt = len(self.specs)
        Bp, oid, part, pr, pe, hip = [], [], [], [], [], []
        for j, rr in enumerate(rig):
            for (x, y, z, p, a, b) in rr:
                Bp.append((x, y, z)); oid.append(j); part.append(p); pr.append(a); pe.append(b); hip.append(self.specs[j]["hip"])
        self.RX = {"B": np.array(Bp, float), "oid": np.array(oid, np.int32), "part": np.array(part, np.int32),
                   "pr": np.array(pr, float), "pe": np.array(pe, float), "hip": np.array(hip, float)}
        self.RX["up"] = np.isin(self.RX["part"], (0, 3, 4, 5, 6)).astype(float)
        self.H = np.array([sp["H"] for sp in self.specs])
        # steam of the dead (white puffs rising off the body for ~10 s, the body shrinking away)
        self.steam = FX.PuffField("TrostTitanSteam", kind="steam", alpha=0.55)
        rnd = np.random.default_rng(7)
        for j in range(nt):
            d = self.ev[j]["death"]
            if not d:
                continue
            td = d[0]; H = self.H[j]
            n = int(16 + 2.0 * H)
            te = td + 0.6 + rnd.random(n) * 9.0
            k = np.clip((te / DT).astype(int), 0, self.K - 1)
            yaw = self.TYAW[k, j]; dirn = d[1]
            along = rnd.random(n) * H * 0.9
            P = np.stack([self.TX[k, j] - np.sin(yaw) * along * dirn, self.TY[k, j] + np.cos(yaw) * along * dirn,
                          self.TZ[k, j] + 0.25 * H * rnd.random(n)], 1)
            self.steam.add_many(te, P, rnd.normal(0, 0.4, (n, 3)), r0=0.06 * H, r1=(0.16 + 0.1 * rnd.random(n)) * H,
                                life=3.5 + 2.5 * rnd.random(n), rise=1.4 + 0.1 * H)
        self.steam.build(coll)

    # ---------------- per-frame pose (vectorised, cached per t)
    def _lerp(self, A, t):
        tt = min(max(t, 0.0), self.t_end)
        kf = tt / DT; k0 = min(int(kf), self.K - 1); k1 = min(k0 + 1, self.K - 1); f = kf - k0
        return A[k0] * (1 - f) + A[k1] * f, k0, k1

    def poses(self, t):
        if self._cache_t == t:
            return self._cache
        nt = len(self.specs)
        px, k0, k1 = self._lerp(self.TX, t); py, _, _ = self._lerp(self.TY, t); pz, _, _ = self._lerp(self.TZ, t)
        y0, y1 = self.TYAW[k0], self.TYAW[k1]
        f = (min(max(t, 0.0), self.t_end) / DT) - k0
        yaw = y0 + (((y1 - y0) + np.pi) % (2 * np.pi) - np.pi) * f
        td, _, _ = self._lerp(self.TD, t)
        spd = (self.TD[k1] - self.TD[k0]) / DT
        H = self.H
        ph = 2 * np.pi * td / (0.55 * H + 0.5)
        mv = np.clip(spd / 1.0, 0.0, 1.0)
        Ar = np.zeros((nt, 8)); Ae = np.zeros((nt, 8)); lean = np.zeros(nt)
        sw = np.sin(ph) * 0.42 * mv
        Ar[:, 1] = sw; Ar[:, 2] = -sw; Ar[:, 3] = -0.7 * sw; Ar[:, 4] = 0.7 * sw
        Ae[:, 5] = Ae[:, 6] = 0.25 + 0.15 * mv
        lean[:] = -0.06 - 0.06 * mv + 0.03 * np.sin(t * 0.7 + np.arange(nt))
        pos = np.stack([px, py, pz], 1)
        pitch = np.zeros(nt); vis = np.ones(nt)
        for j in range(nt):
            e = self.ev[j]; sp = self.specs[j]
            a, b = self.show[j]
            if not (a <= t < b):
                vis[j] = 0.0; continue
            if e["abnormal"] and mv[j] > 0.2:                       # abnormal run: low lean, arms flung back
                lean[j] = -0.55; Ar[j, 3] = Ar[j, 4] = -1.1 + 0.3 * np.sin(ph[j] * 2); Ar[j, 1] *= 1.6; Ar[j, 2] *= 1.6
            if e["lean"] and t >= e["lean"][0] and mv[j] < 0.3:      # hands on the HQ walls, peering in
                u = _ss(e["lean"][0], e["lean"][0] + 1.5, t)
                Ar[j, 3] = Ar[j, 4] = 1.35 * u + 0.08 * math.sin(t * 1.3 + j); Ae[j, 5] = Ae[j, 6] = 0.4 * u; lean[j] = -0.28 * u
            for tg in e["grab"]:
                ej = t - tg
                if 0 <= ej < EAT_DUR:
                    if ej < 0.7:
                        u = _ss(0, 0.7, ej); aa, bb, l = 0.95 * u, 0.3 * u, -0.6 * u
                    elif ej < 1.0:
                        aa, bb, l = 0.95, 0.3, -0.6
                    elif ej < 2.0:
                        u = _ss(1.0, 2.0, ej); aa, bb, l = 0.95 + 0.09 * u, 0.3 + 2.115 * u, -0.6 + 0.65 * u
                    elif ej < 2.4:
                        aa, bb, l = 1.04, 2.415, 0.05
                    else:
                        u = _ss(2.4, 3.4, ej); aa, bb, l = 1.04 * (1 - u), 2.415 * (1 - u) + 0.25 * u, 0.05 - 0.11 * u
                    Ar[j, 1] = Ar[j, 2] = 0.0; Ar[j, 3] = 0.15 * math.sin(ej * 6)
                    Ar[j, 4] = aa; Ae[j, 5] = bb; lean[j] = l
            for ts in e["swat"]:
                ej = t - ts
                if -0.5 <= ej < 1.6:
                    up = _ss(-0.5, 0.0, ej) * (1 - _ss(0.6, 1.6, ej))
                    Ar[j, 4] = 1.6 * up; Ae[j, 5] = 0.2; lean[j] = -0.35 * up
                    yaw[j] += 1.3 * (_ss(-0.15, 0.35, ej) - 0.5) * up
            if e["leap"] is not None:
                ej = t - e["leap"][0]; dur = e["leap"][1]
                if 0 <= ej < dur:
                    u = ej / dur
                    pos[j, 2] += 4 * e["leap"][2] * u * (1 - u)
                    pitch[j] = -0.5 * math.sin(math.pi * u); Ar[j, 3] = Ar[j, 4] = 1.4; lean[j] = -0.2
            if e["blind"] is not None and t >= e["blind"]:
                u = _ss(e["blind"], e["blind"] + 0.35, t)
                Ar[j, 3] = Ar[j, 4] = 2.55 * u; Ae[j, 5] = Ae[j, 6] = 1.9 * u; lean[j] = -0.15 * u + 0.1 * math.sin(t * 9) * u
            if e["death"] is not None:
                td_, dirn = e["death"]
                if t >= td_ - 0.05:
                    u = _ss(td_, td_ + 0.9, t)
                    pitch[j] = -dirn * (math.pi / 2 - 0.08) * u
                    Ar[j, 3] = Ar[j, 4] = 0.6 + 1.6 * u; Ar[j, 1] = 0.3 * u
                    vis[j] = 1.0 - 0.85 * _ss(td_ + 3.0, td_ + 11.0, t)
                    if t > td_ + 12.0:
                        vis[j] = 0.0
        R = (Ar, Ae, lean, vis, yaw, pos, pitch)
        self._cache_t = t; self._cache = R
        self._rig = odm.deform(self.RX, Ar, Ae, lean, vis, yaw, pos, pitch, None, np.zeros(nt)).reshape(nt, 4, 3)
        return R

    def hand(self, name, t):
        self.poses(t); return self._rig[self.j(name), 0].copy()
    def mouth(self, name, t):
        self.poses(t); return self._rig[self.j(name), 1].copy()
    def nape(self, name, t):
        self.poses(t); return self._rig[self.j(name), 2].copy()
    def crown(self, name, t):
        self.poses(t); return self._rig[self.j(name), 3].copy()
    def pos(self, name, t):
        R = self.poses(t); return R[5][self.j(name)].copy()
    def yaw(self, name, t):
        R = self.poses(t); return float(R[4][self.j(name)])

    def update(self, t, hide_all=False):
        Ar, Ae, lean, vis, yaw, pos, pitch = self.poses(t)
        if hide_all:
            vis = vis * 0
        co = odm.deform(self.R, Ar, Ae, lean, vis, yaw, pos, pitch, None, np.zeros(len(vis)))
        self.ob.data.vertices.foreach_set("co", co.astype(np.float32).ravel()); self.ob.data.update()
        self.steam.update(t)


# ====================================================================== the Attack Titan driver
AT.POSES.setdefault("stride_a", dict(AT.POSES["stand"], feet={"R": (AT.V(1.4, 2.3, 0), -6), "L": (AT.V(-1.4, -1.9, 0), 6)},
                                       hands={"R": (AT.V(0.9, -1.4, -4.4), AT.V(0.4, -1, 0), "sh"), "L": (AT.V(-0.9, 1.9, -4.2), AT.V(-0.4, -1, 0), "sh")}))
AT.POSES.setdefault("stride_b", dict(AT.POSES["stand"], feet={"R": (AT.V(1.4, -1.9, 0), -6), "L": (AT.V(-1.4, 2.3, 0), 6)},
                                       hands={"R": (AT.V(0.9, 1.9, -4.2), AT.V(0.4, -1, 0), "sh"), "L": (AT.V(-0.9, -1.4, -4.4), AT.V(-0.4, -1, 0), "sh")}))

class ATDriver:
    """keys: (t, x, y, yaw or None (= face the motion), pose) - position eases between keys; pose 'walk' alternates the
    stride poses with the distance walked.  lie: (t0, t1) windows lying face down; vis windows; shifts (x, y, t0, dur)."""
    def __init__(self, site):
        self.site = site
        self.keys = []; self.vis = []; self.lie = []; self.shifts = []; self.boulder = None
        self.t = None; self._pose = None

    def key(self, t, xy, pose="stand", yaw=None):
        self.keys.append((t, float(xy[0]), float(xy[1]), yaw, pose)); self.keys.sort(key=lambda k: k[0])

    def state(self, t):
        ks = self.keys
        if t <= ks[0][0]:
            k = ks[0]; return np.array([k[1], k[2]]), k[3] if k[3] is not None else 0.0, k[4], 0.0
        for a, b in zip(ks, ks[1:]):
            if a[0] <= t < b[0]:
                u = _ss(a[0], b[0], t) if b[4] != "walk" else (t - a[0]) / (b[0] - a[0])
                p = np.array([a[1] + (b[1] - a[1]) * u, a[2] + (b[2] - a[2]) * u])
                d = np.array([b[1] - a[1], b[2] - a[2]])
                moving = np.linalg.norm(d) > 1.0
                yaw = b[3] if b[3] is not None else (math.atan2(-d[0], d[1]) if moving else (a[3] or 0.0))
                walked = np.linalg.norm(d) * u
                return p, yaw, (b[4] if b[4] != "walk" or moving else "stand"), walked
        k = ks[-1]
        return np.array([k[1], k[2]]), k[3] if k[3] is not None else 0.0, k[4], 0.0

    def yaw_at(self, t):
        # yaw None keys: hold the last motion heading (search backwards)
        p, yaw, pose, w = self.state(t)
        return yaw

    def build(self):
        self.t = AT.place_attack(float(self.site.gate[0]), float(self.site.gate[1]), 0.0, "stand", name="TrostAttack", eyes=25.0)
        self.objs = [o for o in self.t.coll.all_objects]
        self._last_yaw = 0.0

    def visible(self, t):
        return any(a <= t < b for a, b in self.vis)

    def update(self, t):
        T = self.t
        on = self.visible(t)
        for o in self.objs:
            o.hide_render = o.hide_viewport = not on
        for (x, y, t0, dur) in self.shifts:
            u = (t - t0) / dur
            # lightning column + a short small flash from attack_titan.shift_fx; its volume dome (one big opaque
            # white blob) is never shown: the steam is a column of small cards (STATE fields, see setup)
            fx = AT.shift_fx(x, y, min(max(u, 0.0), 1.0) if 0.0 <= u <= 1.0 else 0.0)
            fx["dome"].hide_render = fx["dome"].hide_viewport = True
            fx["dome_d"].default_value = 0.0
            cs = min(fx["core"].scale[0], 3.5)
            fx["core"].scale = (cs, cs, cs * 1.3)
            fx["core"].hide_render = fx["core"].hide_render or not (0.0 <= u <= 0.3)
        if not on:
            return
        p, yaw, pose, walked = self.state(t)
        if pose == "walk":
            pose = "stride_a" if int(walked / 7.0) % 2 == 0 else "stride_b"
        lying = next(((a, b) for a, b in self.lie if a <= t < b), None)
        if lying:
            pose = "crouch"
        if pose != self._pose:
            T.pose(pose); self._pose = pose
        g = self.site.g(p)
        T.place(p[0], p[1], yaw, z=g)
        if lying:
            u = _ss(lying[0], lying[0] + 0.9, t)
            T.holder.rotation_euler = (1.45 * u, 0.0, yaw + math.pi)
            T.holder.location.z = g - 0.8 * u
            bpy.context.view_layer.update()
        self.cur = (p, yaw)

    def nape(self, t):
        """World nape point (pure: from the keys, not the posed rig)."""
        p, yaw, pose, _ = self.state(t)
        fwd = np.array([-math.sin(yaw), math.cos(yaw)])
        lying = next(((a, b) for a, b in self.lie if a <= t < b), None)
        g = self.site.g(p)
        if lying:
            u = _ss(lying[0], lying[0] + 0.9, t)
            h = 12.2
            q = p + fwd * (h * math.sin(1.45 * u) - 1.2 * math.cos(1.45 * u))
            return np.array([q[0], q[1], g + h * math.cos(1.45 * u) + 1.8])
        q = p - fwd * 1.0
        return np.array([q[0], q[1], g + (12.6 if pose not in ("crouch",) else 8.6)])


# ====================================================================== static props: skeleton, cannon, pyres, lift
def _bm_obj(name, bm, mats, coll):
    return L.obj_from_bm(name, bm, mats, coll)

def build_skeleton(coll):
    """Eren's half-shift (S1E5): a titan ribcage + spine + skull and one raised arm blocking the cannonball, in steam.
    Local frame: +y faces the cannon, origin on the ground at the trio."""
    import bmesh
    bm = bmesh.new()
    bone = L.mat("TA_bone", (0.88, 0.82, 0.68), 0.6)
    flesh = L.mat("TA_flesh", (0.55, 0.10, 0.07), 0.6)
    L.cyl(bm, (0, -2.8, 0), (0, -2.6, 10.5), 0.6, 0.5, seg=8)           # spine
    for k in range(7):
        z = 3.6 + k * 0.95
        r = 3.4 - abs(k - 3) * 0.28
        for s in (-1, 1):
            pts = []
            for q in range(9):
                a = q / 8 * math.pi * 0.95
                pts.append((s * math.sin(a) * r, -2.6 - math.cos(a) * r * 0.2 + (1 - math.cos(a)) * 2.6, z - 0.35 * math.sin(a)))
            for a, b in zip(pts, pts[1:]):
                L.cyl(bm, a, b, 0.22, 0.2, seg=6)
    L.cyl(bm, (-3, -2.4, 9.6), (3, -2.4, 9.6), 0.35, 0.35, seg=6)        # collarbones
    sk = bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=8, radius=1.5)
    for v in sk["verts"]:
        v.co = Vector((v.co.x, v.co.y * 1.15 - 2.0, v.co.z * 1.1 + 12.0))
    # raised right arm (the shield): bone + red muscle strands
    sh, el, hd = Vector((3.0, -2.3, 9.4)), Vector((5.6, 1.5, 9.8)), Vector((2.0, 4.8, 7.6))
    L.cyl(bm, sh, el, 0.5, 0.42, seg=8); L.cyl(bm, el, hd, 0.42, 0.36, seg=8)
    hand = bmesh.ops.create_icosphere(bm, subdivisions=1, radius=1.2)
    for v in hand["verts"]:
        v.co += hd
    for f in bm.faces:
        f.material_index = 0
    n0 = len(bm.faces)
    for off in (Vector((0.5, 0.3, 0.4)), Vector((-0.4, 0.2, -0.3)), Vector((0.1, -0.5, 0.5))):
        L.cyl(bm, sh + off, el + off * 0.7, 0.32, 0.25, seg=6, mi=1); L.cyl(bm, el + off * 0.7, hd + off * 0.4, 0.25, 0.2, seg=6, mi=1)
    # left arm hanging + pelvis stub
    L.cyl(bm, (-3.0, -2.3, 9.4), (-4.4, -1.0, 4.8), 0.45, 0.4, seg=8)
    L.cyl(bm, (-4.4, -1.0, 4.8), (-3.6, 0.8, 1.2), 0.4, 0.35, seg=8)
    L.cyl(bm, (-1.8, -2.6, 0.6), (1.8, -2.6, 0.6), 0.7, 0.7, seg=8)
    ob = _bm_obj("TA_HalfShift", bm, [bone, flesh], coll)
    ob.hide_render = True
    return ob

def build_cannon(coll):
    import bmesh
    bm = bmesh.new()
    iron = L.mat("TA_iron", (0.05, 0.05, 0.055), 0.4); wood = L.mat("TA_cwood", (0.25, 0.12, 0.05), 0.8)
    L.cyl(bm, (0, -1.6, 1.25), (0, 1.9, 1.35), 0.42, 0.3, seg=12, mi=0)
    L.box(bm, (0, -0.4, 0.7), (1.3, 2.6, 0.6), mi=1)
    for s in (-1, 1):
        L.cyl(bm, (s * 0.85, 0.3, 0.75), (s * 1.05, 0.3, 0.75), 0.75, 0.75, seg=14, mi=1)
    ob = _bm_obj("TA_Cannon", bm, [iron, wood], coll)
    bs = bmesh.new(); bmesh.ops.create_icosphere(bs, subdivisions=2, radius=0.55)
    ball = _bm_obj("TA_Cannonball", bs, [iron], coll)
    fm, fs = FX.emit_mat("TA_Muzzle", (1.0, 0.55, 0.15), 60.0)
    bf = bmesh.new(); bmesh.ops.create_icosphere(bf, subdivisions=2, radius=1.0)
    flash = _bm_obj("TA_MuzzleFlash", bf, [fm], coll); flash.visible_shadow = False
    return ob, ball, flash

def build_pyre(coll, name, seed):
    import bmesh
    rnd = random.Random(seed)
    bm = bmesh.new()
    logs = L.mat("TA_logs", (0.18, 0.09, 0.04), 0.9); cloth = L.mat("TA_shroud", (0.86, 0.84, 0.78), 0.9)
    for k in range(5):
        a = (k % 2) * math.pi / 2
        for q in range(-2, 3):
            c = (math.cos(a) * 0 - math.sin(a) * q * 1.1, math.sin(a) * 0 + math.cos(a) * q * 1.1, 0.35 + k * 0.6)
            L.box(bm, c, (7.0 if a == 0 else 0.6, 0.6 if a == 0 else 7.0, 0.55), mi=0)
    for q in range(3):
        L.box(bm, (rnd.uniform(-1, 1), -1.8 + q * 1.8, 3.5), (2.0, 0.7, 0.55), mi=1)
    ob = _bm_obj(name, bm, [logs, cloth], coll)
    fm, _ = FX.emit_mat("TA_Fire", (1.0, 0.42, 0.08), 18.0)
    fm2, _ = FX.emit_mat("TA_FireCore", (1.0, 0.8, 0.3), 25.0)
    flames = []
    for k in range(7):
        bf = bmesh.new()
        bmesh.ops.create_cone(bf, cap_ends=True, segments=7, radius1=1.0, radius2=0.0, depth=1.0)
        for v in bf.verts:
            v.co.z += 0.5
        fo = _bm_obj(f"{name}_Flame{k}", bf, [fm if k % 3 else fm2], coll); fo.visible_shadow = False
        fo.location = (ob.location.x + rnd.uniform(-2.2, 2.2), rnd.uniform(-2.2, 2.2), 3.2)
        flames.append((fo, rnd.uniform(0, 9), rnd.uniform(1.6, 2.6), rnd.uniform(4.0, 7.5)))
    ld = bpy.data.lights.new(name + "_Light", "POINT"); ld.color = (1.0, 0.5, 0.18); ld.energy = 0.0; ld.shadow_soft_size = 2.0
    lo = bpy.data.objects.new(name + "_Light", ld); coll.objects.link(lo)
    return ob, flames, lo

def build_lift(coll):
    import bmesh
    bm = bmesh.new()
    wood = L.mat("TA_liftwood", (0.30, 0.17, 0.08), 0.85)
    L.box(bm, (0, 0, 0), (6.5, 6.5, 0.4), mi=0)
    for s in (-1, 1):
        for q in (-1, 1):
            L.cyl(bm, (s * 3.0, q * 3.0, 0), (s * 3.0, q * 3.0, 30), 0.06, 0.06, seg=4, mi=0)
    return _bm_obj("TA_Lift", bm, [wood], coll)


# ====================================================================== choreography
def _roof_path(site, start_xy, goal_xy, n_max, used, rnd, step=(14.0, 34.0)):
    """Greedy chain of perches from the roof nearest start toward the goal."""
    i, r = site.roof_near(start_xy, used)
    used.add(i)
    out = [r]
    for _ in range(n_max):
        cur = out[-1]
        to = np.asarray(goal_xy) - cur[:2]
        dg = np.linalg.norm(to)
        if dg < step[0]:
            break
        d = site.roofs[:, :2] - cur[:2]
        dist = np.hypot(d[:, 0], d[:, 1])
        prog = (d @ (to / dg))
        ok = (dist > step[0]) & (dist < step[1]) & (prog > 0.5 * dist)
        for u in used:
            ok[u] = False
        if not ok.any():
            break
        score = np.where(ok, prog + np.array([rnd.uniform(0, 8) for _ in range(len(prog))]), -1e9)
        k = int(np.argmax(score)); used.add(k); out.append(site.roofs[k])
    return out


def choreograph(site, seed=850):
    rnd = random.Random(seed)
    S = site
    gate, inw, side = S.gate, S.inw, S.side
    TT = Titans(S, seed)
    SQ = odm.Squads("TrostSquads", pscale=PS)
    ATD = ATDriver(S)
    FL = FX.FlareSet("TrostFlares")
    out_pt = gate - inw * 45.0
    hq = S.hq
    dir_hq = (hq - gate) / np.linalg.norm(hq - gate)
    perp_hq = np.array([dir_hq[1], -dir_hq[0]])

    # ------------------------------------------------ flood titans
    Gd = S.nav()
    cand = [(Gd["xs"][i], Gd["ys"][j]) for i in range(Gd["nx"]) for j in range(Gd["ny"]) if Gd["W"][i, j]]
    cand = np.array(cand)
    rel = (cand - gate) @ inw
    hubs_ok = cand[(rel > 50) & (rel < 330) & (np.hypot(cand[:, 0] - hq[0], cand[:, 1] - hq[1]) > 45)]
    nflood = int(os.environ.get("TA_FLOOD", "29"))      # pours through the hole ~2-18 s
    for k in range(nflood):
        ab = k in (5, 13, 21)
        name = f"f{k}"
        TT.add(name, H=(7.0 if ab else None), abnormal=ab, show=(1.5, 1e9), scale=KEY if k < 3 else 1.0)
        if ab:
            TT.specs[-1]["v"] *= 1.9
        hub = hubs_ok[rnd.randrange(len(hubs_ok))]
        t_in = 2.0 + 0.55 * k + rnd.uniform(-0.3, 0.3)
        TT.leg(name, t_in, out_pt + side * rnd.uniform(-12, 12), hub)
    # titans crowding the supply HQ (already deep in the district when the camera gets there)
    ring = []
    for k in range(9):
        a = k / 9 * math.tau + rnd.uniform(-0.2, 0.2)
        w, d_ = S.hq_size[0], S.hq_size[1]
        rr = 0.5 * max(w, d_) + rnd.uniform(5, 9)
        tgt = hq + np.array([math.cos(a), math.sin(a)]) * rr
        name = f"hq{k}"
        TT.add(name, H=rnd.uniform(6, 14), show=(11.0, 1e9), face=tuple(hq))
        start = hq - dir_hq * rnd.uniform(70, 110) + perp_hq * rnd.uniform(-40, 40)
        TT.leg(name, 11.0, start, tgt)
        TT.ev[-1]["lean"] = (rnd.uniform(15.5, 18.0),)
        ring.append(name)

    # ------------------------------------------------ squads deploy (T 3-14), fall back to the HQ roofs (T 14-20)
    used = set()
    front = gate + inw * 110
    names_hair = ["brown", "black", "ash", "blond", "dark", "auburn", "jean", "brown", "dark", "black"]
    nsq = int(os.environ.get("TA_SQUADS", "8"))
    for q in range(nsq):
        start = hq + perp_hq * rnd.uniform(-60, 60) - dir_hq * rnd.uniform(0, 30)
        goal = front + side * (q - (nsq - 1) / 2) * 28 + inw * rnd.uniform(-10, 25)
        for m in range(4):
            f = SQ.flyer(f"s{q}_{m}", "cadet", names_hair[(q * 4 + m) % len(names_hair)])
            route = _roof_path(S, start + rnd.uniform(-6, 6) * side, goal, 9, used, rnd)
            t0 = 3.0 + q * 0.6 + m * 0.25
            t1 = odm.roof_route(f, t0, route, speed=24.0, wait=(0.15, 0.9), rnd=rnd)
            # fall back toward the HQ roofs after the front collapses
            back = _roof_path(S, route[-1][:2], hq + rnd.uniform(-25, 25) * perp_hq, 9, used, rnd)
            if t1 < 15.0:
                f.stand(t1, 15.0 + rnd.uniform(0, 1.5), route[-1], odm.yaw_of(np.append(-inw, 0)))
            tb = odm.roof_route(f, f.t_end(), [route[-1]] + back[1:], speed=24.0, wait=(0.1, 0.5), rnd=rnd)
            f.stand(tb, 70.0, back[-1], odm.yaw_of(np.append(hq - back[-1][:2], 0)))
    # Garrison on the wall top by the gate
    for k, wp in enumerate(S.wall_pts[:8]):
        f = SQ.flyer(f"g{k}", "garrison", rnd.choice(["dark", "brown", "grey"]), rifle=True)
        f.stand(0.0, 74.0, wp, odm.yaw_of(np.append(-inw, 0)), "rifle")

    # ------------------------------------------------ squad 34: Thomas grabbed, Eren's leg, Armin, Eren swallowed
    e_roof_i, e_roof = S.roof_near(gate + inw * 165 + side * 30, used); used.add(e_roof_i)
    a_roof_i, a_roof = S.roof_near(e_roof[:2] + side * 14, used); used.add(a_roof_i)
    eren = SQ.flyer("eren", "cadet", "brown", accent=EREN_ACCENT, cloak=EREN_CLOAK)
    armin = SQ.flyer("armin", "cadet", "blond", H=1.63)
    thomas = SQ.flyer("thomas", "cadet", "ash")
    mina = SQ.flyer("mina", "cadet", "black")
    s34_start = [S.roof_near(e_roof[:2] + inw * k + side * s, used) for k, s in ((95, 0), (80, 10), (70, -8), (88, -14))]
    for (_i, _r) in s34_start:
        used.add(_i)
    # titan that grabs Thomas: stands in a street beside the route
    th_spot = S.snap(e_roof[:2] + inw * 40 + side * 18)
    TT.add("thomas_t", H=11.0, keys=[(0, *(th_spot - inw * 90)), (6.0, *(th_spot - inw * 25)), (8.0, *th_spot), (60, *th_spot)], show=(3.0, 1e9))
    TT.ev[-1]["grab"].append(8.6)
    # the abnormal that leaps and bites off Eren's leg
    ab_spot = S.snap(e_roof[:2] + inw * 12 + side * 6)
    TT.add("biter", H=7.5, keys=[(0, *(ab_spot - inw * 100)), (7.6, *(ab_spot - inw * 6)), (9.2, *ab_spot), (60, *ab_spot)],
           show=(4.0, 1e9), abnormal=True, skin=4, hair=0)
    TT.ev[-1]["leap"] = (9.0, 1.4, 9.0)
    # the bearded titan that swallows Eren
    bd_spot = S.snap(a_roof[:2] + side * 10 - inw * 4)
    TT.add("bearded", H=13.5, g=1.05, hs=1.1, beard=True, hair=1, scale=KEY,
           keys=[(0, *(bd_spot + side * 80)), (9.5, *(bd_spot + side * 12)), (11.0, *bd_spot), (80, *bd_spot)], show=(4.0, 1e9),
           face=tuple(a_roof[:2]))
    TG = 10.6                                            # bearded grab: hand on Armin at TG+0.7, at the mouth by TG+2.0
    TT.ev[-1]["grab"].append(TG)
    # flights
    for f, (_i, r0) in zip((eren, armin, thomas, mina), s34_start):
        f.stand(3.0, 6.8, r0, odm.yaw_of(np.append(inw, 0)))
    mid = S.roof_near(e_roof[:2] + inw * 35, used)[1]
    eren.hop(6.8, 8.1, s34_start[0][1], mid).stand(8.1, 8.75, mid, odm.yaw_of(np.append(inw, 0)))
    leg_pt = v3(mid) + np.array([*(inw * 18 + side * 4), 6.0])
    eren.hop(8.75, 9.55, mid, leg_pt, apex=2.0)
    eren.fall(9.55, 10.45, leg_pt, e_roof, spin=0.6)
    eren.stand(10.45, 12.0, e_roof, odm.yaw_of(np.append(-side, 0)), "lie")
    thomas.hop(6.9, 8.2, s34_start[2][1], v3(S.P(th_spot, 11.5)) - np.append(inw * 4, 0), apex=4.0)
    thomas.follow(8.6 + 0.85, 8.6 + 2.35, lambda t: TT.hand("thomas_t", t) - np.array([0, 0, 1.6]), pose="flail")
    thomas.gone(8.6 + 2.35)
    mina.hop(7.0, 8.6, s34_start[3][1], S.roof_near(a_roof[:2] - side * 20, used)[1]).stand(8.6, 60.0, mina.end_pos(), 0.0, "kneel")
    # Armin: perched -> grabbed (hand) -> lifted to the mouth -> thrown out by Eren -> back on the roof
    armin.hop(6.9, 8.4, s34_start[1][1], a_roof).stand(8.4, TG + 0.7, a_roof, odm.yaw_of(np.append(side, 0)), "kneel")
    armin.follow(TG + 0.7, TG + 2.05, lambda t: TT.hand("bearded", t) - np.array([0, 0, 1.4]), pose="flail")
    armin.fall(TG + 2.15, TG + 2.95, np.zeros(3), a_roof, spin=1.0)    # start point patched after the sim (the mouth)
    armin.stand(TG + 2.95, 20.0, a_roof, odm.yaw_of(np.append(side, 0)), "kneel")
    # Eren: scrambles into the mouth (12.0-12.5), shoves Armin out, swallowed at 13.45
    eren.follow(12.0, 13.45, lambda t: (v3(e_roof) * (1 - _ss(12.0, 12.5, t)) + TT.mouth("bearded", t) * _ss(12.0, 12.5, t))
                - np.array([0, 0, 1.2]), pose="flail",
                vis_fn=lambda t: 1.0 - 0.9 * _ss(13.0, 13.45, t))
    eren.gone(13.45)

    # ------------------------------------------------ a squad wiped off a roof (T 15.6)
    w_i, w_roof = S.roof_near(gate + inw * 140 - side * 70, used); used.add(w_i)
    sw_spot = S.snap(w_roof[:2] + side * 12)
    TT.add("swatter", H=14.5, g=0.7, al=1.25, hs=0.8, skin=6, hair=None,
           keys=[(0, *(sw_spot - inw * 80)), (12.5, *(sw_spot - inw * 14)), (14.6, *sw_spot), (80, *sw_spot)], show=(3.0, 1e9),
           face=tuple(w_roof[:2]))
    TT.ev[-1]["swat"].append(15.6)
    TT.ev[-1]["grab"].append(16.2)
    for m in range(3):
        f = SQ.flyer(f"w{m}", "cadet", ["dark", "brown", "ash"][m])
        p = v3(w_roof) + np.array([*(side * (m - 1) * 1.6), 0])
        st = S.roof_near(w_roof[:2] - inw * 60, used); used.add(st[0])
        f.stand(4.0, 9.0, st[1], 0.0).hop(9.0 + m * 0.2, 10.6 + m * 0.2, st[1], p)
        f.stand(10.6 + m * 0.2, 15.65, p, odm.yaw_of(np.append(-side, 0)), "stand")
        if m < 2:
            land = S.P(w_roof[:2] - side * (14 + 6 * m) + inw * (m * 5 - 3))
            f.fall(15.65, 16.6 + 0.2 * m, p, land, spin=1.2).gone(19.0)
        else:
            f.stand(15.65, 16.9, p, 0.0, "kneel")
            f.follow(16.9, 18.6, lambda t: TT.hand("swatter", t) - np.array([0, 0, 1.6]), pose="flail").gone(18.6)

    # ------------------------------------------------ Mikasa's dash, out of gas, falls (T 21-26)
    M = S.d.get("fall_pt")
    tower = v2(S.d["bell_tower"]) if "bell_tower" in S.d else None
    if M is None and tower is not None:              # Mikasa falls by the church: the rogue titan's first kills are at the tower
        th = (hq - tower) / np.linalg.norm(hq - tower)
        M = tower + th * 55.0
    M = S.snap(v2(M) if M is not None else hq - dir_hq * 85 + perp_hq * 30)
    mikasa = SQ.flyer("mikasa", "cadet", "black", scarf=True)
    connie = SQ.flyer("connie", "cadet", "grey", H=1.58)
    m_start = S.roof_near(hq + dir_hq * 30 + perp_hq * 25, used); used.add(m_start[0])
    mikasa.stand(17.0, 21.0, m_start[1], odm.yaw_of(np.append(-dir_hq, 0)))
    m_route = _roof_path(S, m_start[1][:2], M + dir_hq * 18, 6, used, rnd, step=(18, 40))
    tm = odm.roof_route(mikasa, 21.0, m_route, speed=34.0, wait=(0.05, 0.12), rnd=rnd)
    lastp = v3(m_route[-1])
    air = lastp + np.array([*(-dir_hq * 10), 7.0])
    mikasa.hop(tm, tm + 0.55, lastp, air, apex=2.0, gas=0.45)
    m_land = S.P(M)
    mikasa.fall(tm + 0.55, tm + 1.4, air, m_land, spin=0.7)
    t_mland = tm + 1.4
    mikasa.stand(t_mland, t_mland + 0.5, m_land, odm.yaw_of(np.append(-dir_hq, 0)), "lie")
    mikasa.stand(t_mland + 0.5, 30.0, m_land, odm.yaw_of(np.append(-dir_hq, 0)), "kneel")
    connie.stand(17.0, 21.3, S.roof_near(m_start[1][:2] + perp_hq * 8, used)[1], 0.0)
    odm.roof_route(connie, 21.3, [connie.end_pos()] + [v3(r) for r in m_route[1:]], speed=30.0, wait=(0.05, 0.2), rnd=rnd)
    connie.stand(connie.t_end(), 60.0, connie.end_pos(), odm.yaw_of(np.append(-dir_hq, 0)), "crouch")

    # ------------------------------------------------ the rogue Attack Titan (T 26.5-56)
    A0 = S.snap(M - dir_hq * 32 + perp_hq * 16)
    v0_from, v0_to = S.snap(M - dir_hq * 55 - perp_hq * 10), S.snap(M - dir_hq * 9)
    TT.add("v0", H=9.0, keys=[(0, *v0_from), (24.0, *v0_from), (28.2, *v0_to), (90, *v0_to)], show=(20.0, 1e9), face=tuple(M))
    TT.ev[-1]["death"] = (28.55, -1)                     # punched: falls backward
    ATD.vis.append((26.9, 61.0))
    ATD.shifts.append((float(A0[0]), float(A0[1]), 26.4, 1.5))
    ATD.key(26.9, A0, "crouch", odm.yaw_of(np.append(v0_to - A0, 0)))
    ATD.key(27.6, A0, "roar", odm.yaw_of(np.append(v0_to - A0, 0)))
    pv = v0_to - (v0_to - A0) / np.linalg.norm(v0_to - A0) * 7.5
    ATD.key(28.1, pv, "walk"); ATD.key(28.5, pv, "punch", odm.yaw_of(np.append(v0_to - pv, 0))); ATD.key(29.3, pv, "roar")
    route_end = hq - dir_hq * 40
    tk = [31.5, 34.0, 36.5, 39.0, 41.5]
    cur = pv
    for k, t_k in enumerate(tk):
        fr = (0.04, 0.12, 0.42, 0.7, 0.95)[k] if tower is not None else (k + 1) / len(tk)
        P_k = S.snap(M + (route_end - M) * fr + perp_hq * (12 if k % 2 else -12))
        if tower is not None and k == 0:             # the first kill is slammed down at the foot of the bell tower
            P_k = S.snap(tower + (M - tower) / np.linalg.norm(M - tower) * 12.0)
        come = S.snap(P_k + dir_hq * 35 + perp_hq * rnd.uniform(-20, 20))
        nm = f"v{k + 1}"
        TT.add(nm, H=rnd.uniform(7, 13), keys=[(0, *come), (t_k - 4.0, *come), (t_k - 0.2, *P_k), (90, *P_k)], show=(20.0, 1e9))
        TT.ev[-1]["death"] = (t_k + 0.05, -1 if k % 2 else 1)
        app = P_k - (P_k - cur) / max(1e-3, np.linalg.norm(P_k - cur)) * 7.5
        ATD.key(t_k - 0.45, app, "walk")
        ATD.key(t_k - 0.05, app, "punch", odm.yaw_of(np.append(P_k - app, 0)))
        ATD.key(t_k + 0.6, app, "roar" if k in (1, 4) else "stand", odm.yaw_of(np.append(P_k - app, 0)))
        cur = app
    # three of the HQ crowd fall to him while the cadets get in
    kills = [(ring[0], 45.0), (ring[1], 48.5), (ring[2], 52.0)]
    for nm, t_k in kills:
        TT.ev[TT.j(nm)]["death"] = (t_k + 0.05, 1)
    ATD._pending_kills = kills
    # collapse at the last kill spot (keys finished after the sim, see setup)

    # ------------------------------------------------ the lift plan inside the HQ (T 42-54)
    w, d_, h = S.hq_size
    floor = S.g(hq)
    lift7 = []
    for k in range(7):
        a = k / 7 * math.tau + 0.3
        spots = S.d.get("hq_titan_spots")
        p = v2(spots[k]) if spots else hq + np.array([math.cos(a) * w * 0.3, math.sin(a) * d_ * 0.3])
        nm = f"in{k}"
        TT.add(nm, H=rnd.uniform(3.4, 5.0), keys=[(0, *p), (90, *p)], show=(14.0, 70.0), face=tuple(hq), scale=KEY)
        TT.ev[-1]["blind"] = 49.65
        TT.ev[-1]["death"] = (51.05 + 0.04 * k, 1 if k % 2 else -1)
        lift7.append(nm)
    sc_in = 1.0                                   # true scale (was 0.55 of a 2x figure)
    riflemen = []
    for k in range(9):
        a = k / 9 * math.tau
        f = SQ.flyer(f"r{k}", "cadet", rnd.choice(["brown", "dark", "ash", "black"]), rifle=True, scale=sc_in)
        riflemen.append((f, a))
    jean = SQ.flyer("jean", "cadet", "jean", scale=sc_in)
    marco = SQ.flyer("marco", "cadet", "dark", scale=sc_in)
    droppers = [SQ.flyer(n, "cadet", hcol, scale=sc_in, scarf=(n == "mikasa_in"))
                for n, hcol in (("d0", "brown"), ("d1", "ash"), ("d2", "blond"), ("d3", "dark"), ("d4", "auburn"), ("d5", "black"), ("d6", "grey"))]
    lift_z0, lift_z1 = floor + h - 2.0, floor + 3.0
    def lift_z(t):
        return lift_z0 + (lift_z1 - lift_z0) * _ss(46.3, 49.2, t)
    for f, a in riflemen:
        off = np.array([math.cos(a) * 2.4, math.sin(a) * 2.4])
        f.follow(44.0, 56.0, (lambda off: lambda t: np.array([hq[0] + off[0], hq[1] + off[1], lift_z(t) + 0.2]))(off),
                 yaw_fn=(lambda a: lambda t: a - math.pi / 2)(a), pose="rifle")
        f.gone(56.0)
    for k, f in enumerate(droppers):
        f.seg.append(("pending_dive", 44.0, 56.0, lift7[k]))
    jean.follow(44.0, 56.0, lambda t: np.array([hq[0] + 0.6, hq[1] - 0.6, lift_z(t) + 0.2]), yaw_fn=lambda t: 0.4, pose="stand").gone(56.0)
    marco.follow(44.0, 56.0, lambda t: np.array([hq[0] - 0.6, hq[1] + 0.6, lift_z(t) + 0.2]), yaw_fn=lambda t: 2.5, pose="stand").gone(56.0)
    # the cadets' dash into the HQ (T 42-46): the HQ-roof perchers hop to the HQ roof and vanish inside
    for f in SQ.flyers:
        if f.name.startswith("s") and "_" in f.name and int(f.name.split("_")[1]) < 2:
            p = f.end_pos()
            tgt = v3((hq[0] + rnd.uniform(-w / 3, w / 3), hq[1] + rnd.uniform(-d_ / 3, d_ / 3), floor + h + 0.5))
            t0 = 42.0 + rnd.uniform(0, 2.5)
            f.seg = [s for s in f.seg if s[1] < t0]
            last = f.seg[-1]
            f.seg[-1] = (last[0], last[1], min(last[2], t0), *last[3:])
            f.hop(t0, t0 + 1.1, p, tgt).gone(t0 + 1.3)

    # ------------------------------------------------ flares
    FL_specs = []
    return dict(TT=TT, SQ=SQ, ATD=ATD, FL=FL, M=M, A0=A0, ring=ring, lift7=lift7, droppers=droppers, riflemen=riflemen,
                e_roof=e_roof, a_roof=a_roof, used=used, rnd=rnd, dir_hq=dir_hq, perp_hq=perp_hq, route_end=route_end,
                armin=armin)


def finish_choreography(C, site):
    """Second pass, after the titan sim: things that need titan positions (dive targets, AT approach keys, the
    collapse / emerge / cannon / salute / boulder / Levi / pyres)."""
    S = site; TT, SQ, ATD, FL, rnd = C["TT"], C["SQ"], C["ATD"], C["FL"], C["rnd"]
    gate, inw, side, hq = S.gate, S.inw, S.side, S.hq
    used = C["used"]
    w, d_, h = S.hq_size
    floor = S.g(hq)
    # Armin thrown out of the mouth: patch the fall's start point
    arm = C["armin"]
    for k, s in enumerate(arm.seg):
        if s[0] == "fall" and s[1] > 12.0 and s[1] < 13.5:
            arm.seg[k] = ("fall", s[1], s[2], TT.mouth("bearded", s[1]) - np.array([0, 0, 1.0]), s[4], s[5])
    # droppers: rafters above each lift titan, dive on the nape at 50.4, ride it down
    for k, f in enumerate(C["droppers"]):
        s = f.seg.pop()
        tgt = s[3]
        p = TT.pos(tgt, 48.0)
        raft = np.array([p[0], p[1], floor + h - 1.2])
        f.stand(44.0, 50.35 + 0.04 * k, raft, rnd.uniform(0, 6.28), "crouch")
        f.dive(50.35 + 0.04 * k, 51.0 + 0.04 * k, raft, (lambda tgt: lambda t: TT.nape(tgt, t) + np.array([0, 0, 0.1]))(tgt))
        f.follow(51.0 + 0.04 * k, 56.0, (lambda tgt: lambda t: TT.nape(tgt, min(t, 52.5)) + np.array([0, 0, 0.1]))(tgt), pose="crouch")
        f.gone(56.0)
    # AT approach keys for the HQ crowd kills, then the collapse
    cur = np.array(ATD.keys[-1][1:3])
    for nm, t_k in ATD._pending_kills:
        P_k = TT.pos(nm, t_k)[:2]
        out = (P_k - hq) / max(1e-3, np.linalg.norm(P_k - hq))      # strike from the street side, never through the HQ
        app = P_k + out * 8.5
        # walk around the HQ on an arc outside it (never through the building)
        Rr = 0.5 * max(w, d_) + 16.0
        a0 = math.atan2(cur[1] - hq[1], cur[0] - hq[0]); a1 = math.atan2(app[1] - hq[1], app[0] - hq[0])
        da = (a1 - a0 + math.pi) % math.tau - math.pi
        nst = max(1, int(abs(da) / 0.35))
        t_s = ATD.keys[-1][0]
        for q in range(1, nst):
            aq = a0 + da * q / nst
            ATD.key(t_s + (t_k - 1.6 - t_s) * q / nst, hq + Rr * np.array([math.cos(aq), math.sin(aq)]), "walk")
        ATD.key(t_k - 1.6, app, "walk")
        ATD.key(t_k - 0.05, app, "punch", odm.yaw_of(np.append(P_k - app, 0)))
        ATD.key(t_k + 0.7, app, "stand", odm.yaw_of(np.append(P_k - app, 0)))
        cur = app
    C_pt = cur
    yawC = ATD.keys[-1][3]
    ATD.key(54.0, C_pt, "crouch", yawC)
    ATD.lie.append((54.6, 61.0))
    fwd = np.array([-math.sin(yawC), math.cos(yawC)])
    sideC = np.array([math.cos(yawC), math.sin(yawC)])
    # emerge: Eren rises out of the nape; Mikasa flies to him; Armin follows
    eren2 = SQ.flyer("eren_nape", "cadet", "brown", accent=EREN_ACCENT, cloak=EREN_CLOAK)
    eren2.follow(56.4, 58.0, lambda t: ATD.nape(t) + np.array([0, 0, -1.6 + 1.9 * _ss(56.4, 57.6, t)]), pose="flail",
                 vis_fn=lambda t: 1.0)
    mk = SQ.by_name["mikasa"]; cn = SQ.by_name["connie"]
    mk.seg = [s for s in mk.seg if s[1] < 30.0]
    mk.seg[-1] = (*mk.seg[-1][:2], 30.0, *mk.seg[-1][3:])
    mroof = S.roof_near(C_pt + sideC * 20, used); used.add(mroof[0])
    mk.hop(30.0, 31.2, mk.end_pos(), mroof[1]).stand(31.2, 56.2, mroof[1], 0.0, "crouch")
    mk.hop(56.2, 57.3, mroof[1], ATD.nape(57.3)).stand(57.3, 58.0, ATD.nape(57.3), 0.0, "carry")
    # site key cannon_square: the Garrison corners the trio in an open square (a time cut after the emerge)
    jump = "cannon_square" in S.d
    Q = S.snap(v2(S.d["cannon_square"])) if jump else S.snap(C_pt + sideC * 13 - fwd * 3)
    Qp = S.P(Q)
    to_q = lambda t, a: None
    if jump:   # hold on the corpse, then cut: the trio is already in the square
        eren2.stand(58.0, 58.6, ATD.nape(58.0), 0.0, "kneel")
    else:
        eren2.walk(58.0, 58.9, ATD.nape(58.0), Qp + np.append(-sideC * 0.9, 0), pose="flail")
    eren2.stand(58.9, 68.0, Qp + np.append(-sideC * 0.9, 0), 0.0, "kneel")
    if jump:
        mk.stand(58.0, 58.6, ATD.nape(58.0), 0.0, "carry")
    else:
        mk.walk(58.0, 58.9, ATD.nape(58.0), Qp + np.append(sideC * 0.9, 0), pose="run")
    armin2 = SQ.flyer("armin2", "cadet", "blond", H=1.63)
    ar_roof = S.roof_near(C_pt - sideC * 22, used); used.add(ar_roof[0])
    if jump:
        armin2.stand(52.0, 57.6, ar_roof[1], 0.0, "stand").hop(57.6, 58.5, ar_roof[1], ATD.nape(58.5) + np.array([*(sideC * 2.0), 0]))
    else:
        armin2.stand(52.0, 57.6, ar_roof[1], 0.0, "stand").hop(57.6, 58.8, ar_roof[1], Qp + np.append(fwd * 0.9, 0))
    # Garrison ring + the cannon
    cdir = np.array([math.cos(1.1), math.sin(1.1)])
    cannon_xy = S.snap(Q + cdir * 34)
    cdir = (Q - cannon_xy) / np.linalg.norm(Q - cannon_xy)
    yaw_c = odm.yaw_of(np.append(cdir, 0))
    mk.stand(58.9, 68.0, Qp + np.append(sideC * 0.9, 0), yaw_c + math.pi, "crouch")
    armin2.stand(58.8, 63.9, Qp + np.append(fwd * 0.9, 0), yaw_c + math.pi, "crouch")
    ring_n = 18
    for k in range(ring_n):
        a = k / ring_n * math.tau
        p_out = Q + np.array([math.cos(a), math.sin(a)]) * 42
        p_in = Q + np.array([math.cos(a), math.sin(a)]) * (22 + 3 * (k % 2))
        f = SQ.flyer(f"gr{k}", "garrison", rnd.choice(["dark", "brown", "grey", "ash"]), rifle=True)
        yaw_in = odm.yaw_of(np.append(Q - p_in, 0))
        f.walk(58.6 + rnd.uniform(0, 0.6), 60.4, S.P(p_out), S.P(p_in), "run")
        f.stand(60.4, 68.0, S.P(p_in), yaw_in, "rifle")
    kitz = SQ.flyer("kitz", "garrison", "bald", H=1.8)
    kitz.walk(59.0, 60.6, S.P(cannon_xy + cdir * -12 + np.array([cdir[1], -cdir[0]]) * 4), S.P(cannon_xy - cdir * 4 + np.array([cdir[1], -cdir[0]]) * 3))
    kitz.stand(60.6, 68.0, kitz.end_pos(), yaw_c, "wave")
    # Armin's salute: out of the steam toward the guns
    sal = Qp + np.append(cdir * 6.5, 0)
    armin2.walk(63.9, 64.8, Qp + np.append(fwd * 0.9, 0), sal, "run")
    armin2.stand(64.8, 70.0, sal, yaw_c + math.pi, "salute")

    # ------------------------------------------------ boulder operation (T 74.5-104)
    Bxy = S.boulder
    shift_pt = S.snap(Bxy - side * 12 + inw * 14)
    seal = gate + inw * 7.0
    yaw_b = odm.yaw_of(np.append(Bxy - shift_pt, 0))
    ATD.vis.append((75.2, 140.0))
    ATD.shifts.append((float(shift_pt[0]), float(shift_pt[1]), 74.7, 1.5))
    ATD.key(75.2, shift_pt, "roar", yaw_b)
    ATD.key(77.3, shift_pt, "roar", yaw_b)
    ATD.key(77.9, shift_pt, "punch", yaw_b + 0.6)          # berserk: swings at Mikasa
    ATD.key(78.8, shift_pt, "stand", yaw_b + 0.4)
    near_b = Bxy - (Bxy - shift_pt) / np.linalg.norm(Bxy - shift_pt) * 7.0
    ATD.key(82.0, near_b, "walk")
    ATD.key(83.4, near_b, "crouch", yaw_b)
    to_gate = (seal - near_b) / np.linalg.norm(seal - near_b)
    yaw_g = odm.yaw_of(np.append(to_gate, 0))
    ATD.key(84.4, near_b, "carry", yaw_g)
    stop = seal - to_gate * 9.0
    ATD.key(98.6, stop, "walk")
    ATD.key(99.1, stop, "carry", yaw_g)
    ATD.key(100.6, stop, "crouch", yaw_g)
    ATD.key(140.0, stop, "crouch", yaw_g)
    ATD.carry = (83.4, 84.4, 100.0, 101.4, near_b, seal)
    # Mikasa dodges the punch; Armin's stab and ride on the nape
    mk3 = SQ.flyer("mikasa_b", "cadet", "black", scarf=True)
    r1 = S.roof_near(shift_pt + side * 22, used); used.add(r1[0])
    r2 = S.roof_near(shift_pt - side * 24 + inw * 10, used); used.add(r2[0])
    mk3.stand(74.0, 77.4, r1[1], 0.0).hop(77.4, 78.6, r1[1], r2[1], apex=12).stand(78.6, 84.0, r2[1], 0.0, "crouch")
    ar3 = SQ.flyer("armin_b", "cadet", "blond", H=1.63)
    r3 = S.roof_near(shift_pt + inw * 25, used); used.add(r3[0])
    ar3.stand(74.0, 79.2, r3[1], 0.0, "kneel").hop(79.2, 80.3, r3[1], ATD.nape(80.3))
    ar3.follow(80.3, 104.0, lambda t: ATD.nape(t) + np.array([0, 0, 0.2]), pose="crouch")
    mk3.hop(84.0, 85.2, r2[1], S.roof_near(near_b + to_gate * 40 + side * 20, used)[1])
    # elite squad (Ian, Rico, Mitabi + 3) escorting, killing titans that close in
    elite = [SQ.flyer(n, "garrison", hc, scarf=False) for n, hc in (("ian", "dark"), ("rico", "grey"), ("mitabi", "brown"),
                                                                     ("e3", "ash"), ("e4", "dark"), ("e5", "auburn"))]
    def at_xy(t):
        return ATD.state(t)[0]
    for k, f in enumerate(elite):
        sgn = 1 if k % 2 else -1
        t = 82.0
        p = S.roof_near(near_b + side * sgn * (20 + 6 * k), used)[1]; f.stand(74.0, 82.0 + 0.3 * k, p, 0.0)
        t = 82.0 + 0.3 * k
        while t < 97.0:
            q_xy = at_xy(t + 2.2) + to_gate * (8 + 4 * k) + side * sgn * (16 + 5 * (k // 2))
            i_r, q = S.roof_near(q_xy)
            f.hop(t, t + 1.2, p, q)
            f.stand(t + 1.2, t + 2.2, q, yaw_g, "crouch")
            p = q; t += 2.2
        f.stand(t, 104.0, p, yaw_g, "stand")
    # titans closing in on the carry, cut down by the elite squad (dives on the napes)
    esc_t = (88.0, 92.5, 96.0)
    for k, t_d in enumerate(esc_t):
        tgt = at_xy(t_d) + side * (22 if k % 2 else -22) + to_gate * 10
        tgt = S.snap(tgt); frm = S.snap(tgt + side * (40 if k % 2 else -40) - to_gate * 20)
        TT.add(f"esc{k}", H=rnd.uniform(8, 13), keys=[(0, *frm), (t_d - 6.0, *frm), (t_d - 0.3, *tgt), (200, *tgt)], show=(70.0, 1e9))
        TT.ev[-1]["death"] = (t_d + 0.05, 1)
    TT.sim(140.0)                         # the new titans must exist before their napes are sampled
    for k, t_d in enumerate(esc_t):
        nm = f"esc{k}"
        f = elite[k]
        # replace the hop that covers t_d with a dive onto this titan's nape
        f.seg = [s for s in f.seg if s[2] <= t_d - 0.8]
        p0 = f.end_pos()
        f.dive(t_d - 0.8, t_d, p0 + np.array([0, 0, 6.0]), (lambda nm: lambda t: TT.nape(nm, t))(nm))
        r_next = S.roof_near(at_xy(t_d + 2) + side * (18 if k % 2 else -18))[1]
        f.hop(t_d, t_d + 1.4, TT.nape(nm, t_d), r_next).stand(t_d + 1.4, 104.0, r_next, yaw_g, "crouch")
    # lure squads on the wall top by the gate
    # flares: red on the failure, yellow on success
    red_from = S.roof_near(shift_pt + side * 28 - inw * 10)[1]
    FL.add(77.0, red_from + np.array([0, 0, 2.0]), "red", up=110.0, seed=1)
    FL.add(77.15, red_from + np.array([3, 2, 2.0]), "red", up=95.0, seed=2)
    rico_wall = min(S.wall_pts, key=lambda p: np.linalg.norm(p[:2] - gate))
    FL.add(102.6, rico_wall + np.array([0, 0, 2.0]), "yellow", up=125.0, seed=3, width=1.2)
    FL.add(102.9, rico_wall + np.array([*(side * 8), 2.0]), "yellow", up=105.0, seed=4)
    # green / black: the morning advance (direction) and an abnormal sighting, early in the flood
    FL.add(3.2, S.wall_pts[min(4, len(S.wall_pts) - 1)] + np.array([0, 0, 2.0]), "black", up=100.0, seed=5, life=10.0)   # away from the gate hole
    FL.add(5.0, S.wall_pts[min(5, len(S.wall_pts) - 1)] + np.array([0, 0, 2.0]), "green", up=90.0, seed=6, life=10.0)
    rico = SQ.by_name["rico"]
    rico.seg = [s for s in rico.seg if s[2] <= 100.0]
    rico.hop(100.0, 101.8, rico.end_pos(), rico_wall).stand(101.8, 112.0, rico_wall, odm.yaw_of(np.append(inw, 0)), "wave")

    # ------------------------------------------------ Levi's entrance (T 104-111)
    l1_to = S.snap(stop + to_gate * -26 + side * 6)
    l2_to = S.snap(stop + to_gate * -20 - side * 12)
    for nm, to, td_, dirn in (("lv1", l1_to, 107.75, 1), ("lv2", l2_to, 106.6, -1)):
        frm = S.snap(to - to_gate * 60)
        TT.add(nm, H=rnd.uniform(9, 12), keys=[(0, *frm), (101.0, *frm), (td_ - 0.2, *to), (200, *to)], show=(98.0, 1e9), scale=KEY)
        TT.ev[-1]["death"] = (td_ + 0.05, dirn)
    levi = SQ.flyer("levi", "scout", "black", H=1.6, cravat=True)
    lw = min(S.wall_pts, key=lambda p: np.linalg.norm(p[:2] - (gate + side * 25)))
    levi.stand(103.0, 105.4, lw, odm.yaw_of(np.append(inw, 0)))
    levi.dive(105.4, 106.6, lw + np.array([0, 0, 2.0]), lambda t: TT.nape("lv2", t))
    levi.spin(106.6, 107.75, lambda t: TT.nape("lv1", t), 6.0, 2.5, 0.2, turns=2.5)
    levi.follow(107.75, 112.0, lambda t: TT.crown("lv1", min(t, 109.0)) + np.array([0, 0, 0.1]), yaw_fn=lambda t: 0.0, pose="stand")
    # Armin pulls Eren from the nape; Mikasa joins
    eren3 = SQ.flyer("eren_b", "cadet", "brown", accent=EREN_ACCENT, cloak=EREN_CLOAK)
    eren3.follow(102.8, 104.6, lambda t: ATD.nape(t) + np.array([0, 0, -1.2 + 1.2 * _ss(102.8, 104.2, t)]), pose="flail")
    eren3.stand(104.6, 112.0, eren3.end_pos(), 0.0, "lie")
    ar3.seg = [s for s in ar3.seg if s[1] < 104.0]
    ar3.stand(104.0, 112.0, ATD.nape(104.0) + np.array([*(side * 1.2), 0]), 0.0, "kneel")
    mk3.seg = [s for s in mk3.seg if s[1] < 100.0]
    mk3.hop(102.4, 103.6, mk3.end_pos(), ATD.nape(103.6) - np.array([*(side * 1.2), 0])).stand(103.6, 112.0, ATD.nape(103.6) - np.array([*(side * 1.2), 0]), 0.0, "crouch")

    # ------------------------------------------------ pyres and Marco (T 113-125)
    P0 = S.pyre
    pyre_pts = [S.snap(P0 + side * k * 11) for k in (-1, 0, 1)]
    mourners = []
    for k in range(18):
        a = rnd.uniform(0, math.tau); r = rnd.uniform(9, 16)
        pp = P0 + np.array([math.cos(a), math.sin(a)]) * r
        f = SQ.flyer(f"m{k}", rnd.choice(["cadet", "cadet", "garrison"]), rnd.choice(["brown", "dark", "ash", "black", "blond"]))
        f.stand(112.5, 130.0, S.P(pp), odm.yaw_of(np.append(P0 - pp, 0)), rnd.choice(["stand", "stand", "kneel"]))
    for k in range(8):                       # shrouded bodies waiting by the pyres
        pp = P0 - inw * 9 + side * (k - 3.5) * 2.4
        f = SQ.flyer(f"body{k}", "cadet", "brown")
        f.stand(112.5, 130.0, S.P(pp), odm.yaw_of(np.append(inw, 0)), "lie")
    mpos = S.snap(P0 + inw * 34 + side * 26)
    marco2 = SQ.flyer("marco_dead", "cadet", "dark")
    marco2.stand(112.5, 130.0, S.P(mpos), 0.4, "lie")
    jean2 = SQ.flyer("jean_dusk", "cadet", "jean")
    jfrom = S.snap(mpos - inw * 24 + side * 6)
    jean2.walk(114.5, 117.4, S.P(jfrom), S.P(mpos + side * 1.6 - inw * 0.8), "run")
    jean2.stand(117.4, 130.0, S.P(mpos + side * 1.6 - inw * 0.8), odm.yaw_of(np.append(mpos - (mpos + side * 1.6), 0)), "stand")
    C.update(pyre_pts=pyre_pts, Q=Q, cannon_xy=cannon_xy, cdir=cdir, C_pt=C_pt, shift_pt=shift_pt, seal=seal, stop=stop, mpos=mpos)


# ====================================================================== setup / update
def setup(site_dict, seed=850, light=False, coll_name="TrostAction"):
    t0 = time.time()
    site = Site(site_dict)
    coll = bpy.data.collections.get(coll_name) or L.new_coll(coll_name)
    C = choreograph(site, seed)
    TT = C["TT"]
    TT.sim(140.0)
    finish_choreography(C, site)
    EV = None
    if "inner_gate" in site.d:
        EV = Evac(site, n=int(os.environ.get("TA_EVAC", "650")))
        EV.plan()
        evac_flyers(C["SQ"], site, EV, C["used"])
        pyxis_flyers(C["SQ"], site, C["rnd"])
    TT.sim(140.0)                     # late titans (escort / Levi) added in the second pass
    TT._cache_t = None
    TT.build(coll)
    C["SQ"].build(coll)
    C["ATD"].build()
    C["FL"].build(coll)
    # props
    skel = build_skeleton(coll)
    cannon, ball, flash = build_cannon(coll)
    lift = build_lift(coll)
    boulder = site.d.get("boulder_obj") or AT.make_boulder((0, 0, -500), float(site.d.get("boulder_r", 6.0)), name="TA_Boulder")
    if EV is not None:
        EV.build(coll)
    pyres = [build_pyre(coll, f"TA_Pyre{k}", k) for k in range(3)]
    for (ob, flames, lo), p in zip(pyres, C["pyre_pts"]):
        z = site.g(p)
        ob.location = (p[0], p[1], z)
        for fo, *_ in flames:
            fo.location = (p[0] + fo.location.x, p[1] + fo.location.y, z + 3.2)
        lo.location = (p[0], p[1], z + 6.0)
    fm, fs = FX.emit_mat("TA_Muzzle2", (1.0, 0.75, 0.3), 40.0)
    import bmesh
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=0.35)
    rflash = []
    for k in range(9):
        o = L.obj_from_bm(f"TA_RifleFlash{k}", bm.copy(), [fm], coll); o.visible_shadow = False; rflash.append(o)
    bm.free()
    # smoke / steam fields for the props
    cs = FX.PuffField("TA_CannonSmoke", kind="smoke", color=(0.62, 0.61, 0.58), alpha=0.7)
    hs = FX.PuffField("TA_ShiftSteam", kind="steam", alpha=0.55)
    ps = FX.PuffField("TA_PyreSmoke", kind="smoke", color=(0.30, 0.25, 0.20), alpha=0.6)
    pf = FX.PuffField("TA_PyreFire", kind="fire", color=(1.0, 0.45, 0.1), alpha=0.9, grow=1.0)
    rs = FX.PuffField("TA_RifleSmoke", kind="smoke", color=(0.8, 0.8, 0.77), alpha=0.6)
    rnd = np.random.default_rng(11)
    Q = C["Q"]; cxy = C["cannon_xy"]; cdir = C["cdir"]
    muzzle = np.array([cxy[0] + cdir[0] * 2.2, cxy[1] + cdir[1] * 2.2, site.g(cxy) + 1.35])
    n = 40
    cs.add_many(62.0 + rnd.random(n) * 0.35, muzzle + rnd.normal(0, 0.8, (n, 3)), np.column_stack([cdir[0] * 6 + rnd.normal(0, 2, n), cdir[1] * 6 + rnd.normal(0, 2, n), rnd.random(n) * 1.5]),
                r0=0.8, r1=4.5, life=6.0 + 3 * rnd.random(n), rise=0.6)
    Qz = site.g(Q)
    n = 170
    hs.add_many(62.3 + rnd.random(n) ** 2 * 1.4, np.column_stack([Q[0] + rnd.normal(0, 4, n), Q[1] + rnd.normal(0, 4, n), Qz + rnd.random(n) * 10]),
                rnd.normal(0, 1.6, (n, 3)), r0=0.4, r1=1.8, life=1.2 + 1.0 * rnd.random(n), rise=4.0, alpha=0.35)
    # steam off the Attack Titan's collapsed body + at both shifts
    nape = C["ATD"].nape
    n = 45
    te = 55.0 + rnd.random(n) * 7.0
    P = np.array([nape(t) for t in te]) + rnd.normal(0, 3.0, (n, 3))
    hs.add_many(te, P, rnd.normal(0, 1.0, (n, 3)), r0=0.6, r1=2.8, life=3.0, rise=3.0)
    te = 101.0 + rnd.random(n) * 10.0
    P = np.array([nape(t) for t in te]) + rnd.normal(0, 3.0, (n, 3))
    hs.add_many(te, P, rnd.normal(0, 1.0, (n, 3)), r0=0.6, r1=2.8, life=3.0, rise=3.0)
    # shift steam: after the lightning, a rising column of many small semi-transparent cards that clears fast
    for (sx, sy, st0, sdur) in C["ATD"].shifts:
        z = site.g((sx, sy)); n = 220
        te = st0 + 0.15 + rnd.random(n) ** 1.5 * 1.8
        ang = rnd.random(n) * 6.283; rr = 2.0 + rnd.random(n) * 5.0
        hs.add_many(te, np.column_stack([sx + np.cos(ang) * rr, sy + np.sin(ang) * rr, z + 1.0 + rnd.random(n) * 14.0]),
                    np.column_stack([np.cos(ang) * 1.5, np.sin(ang) * 1.5, 2.0 + rnd.random(n) * 4.0]),
                    r0=0.5, r1=2.0, life=0.9 + 0.9 * rnd.random(n), rise=5.0, alpha=0.3)
    for p in C["pyre_pts"]:
        z = site.g(p)
        n = 320
        te = 112.0 + rnd.random(n) * 14.0
        ps.add_many(te, np.column_stack([p[0] + rnd.normal(0, 1.2, n), p[1] + rnd.normal(0, 1.2, n), z + 5 + rnd.random(n)]),
                    np.column_stack([1.6 + rnd.normal(0, 0.4, n), 0.6 + rnd.normal(0, 0.4, n), np.zeros(n)]), r0=1.0, r1=5.0, life=7.0, rise=5.0)
        te = np.arange(112.0, 126.0, 0.025); n = len(te)
        pf.add_many(te, np.column_stack([p[0] + rnd.normal(0, 1.4, n), p[1] + rnd.normal(0, 1.4, n), z + 3.0 + rnd.random(n)]),
                    rnd.normal(0, 0.3, (n, 3)), r0=1.5, r1=0.7, life=0.55 + 0.3 * rnd.random(n), rise=4.5, fade_in=0.05)
    for k, (f, a) in enumerate(C["riflemen"]):
        st = f.state(49.6)
        tip = st["pos"] + np.array([math.cos(a) * 1.3, math.sin(a) * 1.3, 1.0])
        rs.add_many(49.6 + rnd.random(6) * 0.2, tip + rnd.normal(0, 0.2, (6, 3)), np.column_stack([np.full(6, math.cos(a) * 2), np.full(6, math.sin(a) * 2), np.zeros(6)]),
                    r0=0.12, r1=0.6, life=2.0, rise=0.3)
    for f_ in (cs, hs, ps, pf, rs):
        f_.build(coll)
    STATE.clear()
    STATE.update(site=site, C=C, coll=coll, TT=TT, SQ=C["SQ"], ATD=C["ATD"], FL=C["FL"], skel=skel, cannon=cannon, ball=ball,
                 flash=flash, lift=lift, boulder=boulder, pyres=pyres, rflash=rflash, fields=(cs, hs, ps, pf, rs), muzzle=muzzle,
                 light=light, light0=None, timings=time.time() - t0, EV=EV, cut_state=None)
    if light:
        _light_capture()
    # static placements
    yaw_c = odm.yaw_of(np.append(cdir, 0))
    cannon.location = (cxy[0], cxy[1], site.g(cxy)); cannon.rotation_euler = (0, 0, yaw_c)
    skel.location = (Q[0], Q[1], Qz); skel.rotation_euler = (0, 0, yaw_c + math.pi)
    lift.location = (site.hq[0], site.hq[1], -500)
    update(0.0)
    print(f"[trost_action] titans {len(TT.specs)} flyers {len(C['SQ'].flyers)} gas puffs {C['SQ'].gas.n} setup {time.time() - t0:.1f}s")
    return STATE

def _light_capture():
    w = bpy.context.scene.world
    bg = [(n, tuple(n.inputs[0].default_value), n.inputs[1].default_value) for n in (w.node_tree.nodes if w and w.use_nodes else []) if n.type == "BACKGROUND"]
    suns = [(o.data, tuple(o.data.color), o.data.energy) for o in bpy.data.objects if o.type == "LIGHT" and o.data.type == "SUN"]
    STATE["light0"] = (bg, suns)

def dusk(amount):
    """0 = day as built, 1 = the pyres' dusk (warm low sun, dim sky)."""
    if not STATE.get("light0"):
        _light_capture()
    bg, suns = STATE["light0"]
    for n, c, s in bg:
        n.inputs[1].default_value = s * (1 - 0.6 * amount)
    for d, c, e in suns:
        d.energy = e * (1 - 0.55 * amount)
        d.color = tuple(c[i] * (1 - amount) + (1.0, 0.55, 0.3)[i] * amount for i in range(3))

def update_boulder(t):
    S = STATE; site, ATD = S['site'], S['ATD']
    b = S["boulder"]; r = float(site.d.get("boulder_r", 6.0))
    bx, by = site.boulder
    rest = Vector((bx, by, site.g(site.boulder) + r * 0.8))
    if hasattr(ATD, "carry") and ATD.visible(t) and t >= ATD.carry[0]:
        tl0, tl1, td0, td1, near_b, seal = ATD.carry
        anchor = AT.boulder_anchor(ATD.t, r)
        if t < tl1:
            u = _ss(tl0, tl1, t); b.location = rest.lerp(anchor, u)
        elif t < td0:
            b.location = anchor
        else:
            sp = Vector((seal[0], seal[1], site.g(seal) + r * 0.8))
            u = _ss(td0, td1, t)
            b.location = AT.boulder_anchor(ATD.t, r).lerp(sp, u) if u < 1 else sp
    elif t >= 101.4:
        seal = ATD.carry[5]; b.location = Vector((seal[0], seal[1], site.g(seal) + r * 0.8))
    else:
        b.location = rest
    if site.d.get("boulder_origin") == "bottom":       # the set's boulder has its origin at the bottom centre
        b.location = b.location - Vector((0, 0, r * 0.8))

def update(t):
    S = STATE
    if not S:
        return
    t = float(t)
    site, C = S["site"], S["C"]
    TT, SQ, ATD, FL = S["TT"], S["SQ"], S["ATD"], S["FL"]
    TT.update(t, hide_all=t > 112.5)
    ATD.update(t)
    SQ.update(t)
    FL.update(t)
    for pf in S["fields"]:
        pf.update(t)
    # HQ cutaway
    cut = 45.0 <= t < 55.5
    for o in site.d.get("hq_roof", []) or []:
        o.hide_render = o.hide_viewport = cut
    if site.d.get("hq_cutaway_fn") and S.get("cut_state") != cut:
        site.d["hq_cutaway_fn"](cut); S["cut_state"] = cut
    if S.get("EV") is not None:
        S["EV"].update(t)
    # lift
    floor = site.g(site.hq); w, d_, h = site.hq_size
    lz = (floor + h - 2.0) + ((floor + 3.0) - (floor + h - 2.0)) * _ss(46.3, 49.2, t)
    S["lift"].location = (site.hq[0], site.hq[1], lz if 44.0 <= t < 56.0 else -500)
    for k, (o, (f, a)) in enumerate(zip(S["rflash"], C["riflemen"])):
        on = 49.6 + 0.02 * k <= t < 49.75 + 0.02 * k
        o.hide_render = o.hide_viewport = not on
        if on:
            st = f.state(t)
            o.location = tuple(st["pos"] + np.array([math.cos(a) * 1.4, math.sin(a) * 1.4, 1.0]))
    update_boulder(t)
    # cannon: recoil, flash, ball, skeleton
    yaw_c = S["cannon"].rotation_euler.z
    cdir = C["cdir"]; cxy = C["cannon_xy"]
    show_c = 59.0 <= t < 70.0
    S["cannon"].hide_render = not show_c
    rec = 0.9 * _ss(62.0, 62.05, t) * (1 - _ss(62.3, 63.5, t))
    S["cannon"].location = (cxy[0] - cdir[0] * rec, cxy[1] - cdir[1] * rec, site.g(cxy))
    fl = S["flash"]
    on = 62.0 <= t < 62.18
    fl.hide_render = fl.hide_viewport = not on
    if on:
        u = (t - 62.0) / 0.18
        s = 1.0 + 2.8 * math.sin(math.pi * u)
        fl.location = tuple(S["muzzle"] + np.append(cdir * (1.0 + 2.0 * u), 0)); fl.scale = (s * 1.4, s * 1.4, s)
    ball = S["ball"]
    Q = C["Q"]; Qz = site.g(Q)
    hit = np.array([Q[0] + cdir[0] * -5.0, Q[1] + cdir[1] * -5.0, Qz + 7.8])
    hit = np.array([Q[0] - cdir[0] * -5.0, Q[1] - cdir[1] * -5.0, Qz + 7.8])      # on the raised arm, cannon side
    if 62.0 <= t < 62.35:
        u = (t - 62.0) / 0.35
        ball.location = tuple(S["muzzle"] + (hit - S["muzzle"]) * u); ball.hide_render = False
    elif 62.35 <= t < 63.4:
        u = (t - 62.35)
        p = hit + np.array([cdir[0] * 3 * u, cdir[1] * 3 * u, 4.0 * u - 0.5 * 9.81 * u * u])
        p[2] = max(p[2], Qz + 0.55)
        ball.location = tuple(p); ball.hide_render = False
    elif 63.4 <= t < 70.0:
        p = hit + np.array([cdir[0] * 3.15, cdir[1] * 3.15, 0]); p[2] = Qz + 0.55
        ball.location = tuple(p); ball.hide_render = False
    else:
        ball.hide_render = True
    sk = S["skel"]
    if 62.05 <= t < 66.5:
        u = _ss(62.05, 62.32, t)
        s = max(0.02, u * (1 + 0.12 * math.sin(math.pi * min(1, (t - 62.05) / 0.45))))
        fade = 1 - _ss(64.5, 66.5, t)
        sk.scale = (s, s, s * max(0.02, fade)); sk.hide_render = False
    else:
        sk.hide_render = True
    # pyres
    for (ob, flames, lo) in S["pyres"]:
        on = t >= 112.5
        ob.hide_render = not on
        lo.data.energy = 4000.0 * (0.85 + 0.15 * math.sin(t * 11)) if on else 0.0
        for fo, ph, r0, h0 in flames:
            fo.hide_render = True          # fire is drawn with emissive cards now
            continue
            if on:
                k = 1 + 0.25 * math.sin(t * 13 + ph) + 0.15 * math.sin(t * 29 + 2 * ph)
                fo.scale = (r0 * (0.9 + 0.1 * k), r0 * (0.9 + 0.1 * k), h0 * k)
    if S["light"]:
        dusk(_ss(111.0, 114.0, t))

def hero_pos(name, t):
    S = STATE
    if name == "attack":
        p, yaw, pose, _ = S["ATD"].state(t); return np.array([p[0], p[1], S["site"].g(p) + 15.0])
    if name == "boulder":
        update_boulder(t); return np.array(S["boulder"].location)
    SQ = S["SQ"]
    alias = {"eren": [("eren", 0, 14), ("eren_nape", 56, 70), ("eren_b", 102, 130)],
             "mikasa": [("mikasa_gate", 0, 16.9), ("mikasa", 16.9, 74), ("mikasa_b", 74, 130)], "armin": [("armin", 0, 50), ("armin2", 50, 74), ("armin_b", 74, 130)],
             "jean": [("jean", 0, 60), ("jean_dusk", 110, 130)], "marco": [("marco", 0, 60), ("marco_dead", 110, 130)]}
    for nm, a, b in alias.get(name, [(name, -1e9, 1e9)]):
        if a <= t < b and nm in SQ.by_name:
            return SQ.pos(nm, t)
    return None

def info():
    S = STATE
    return dict(titans=len(S["TT"].specs), flyers=len(S["SQ"].flyers), setup_s=S["timings"])


# ====================================================================== the Trost evacuation (crowd flow at the inner gate)
class Evac:
    """Civilians stream to the inner gate, jam behind the stuck cargo wagon, Mikasa drops in, the merchant backs off,
    the wagon is hauled through and the crowd floods out at a fixed throughput.  Pure function of t (0.2 s grid).
    Figures: swarm845's minimal civilians (person_geo + its palettes), drawn at `ps` x life size."""
    T0, T_MIK, T_PULL0, T_PULL1, T_END = 1.0, 10.6, 11.6, 13.4, 46.0
    RATE = 22.0                 # people through the gate per second once it is clear (a flood)

    def __init__(self, site, n=420, seed=846, ps=1.0):
        self.site, self.n, self.ps = site, n, ps
        self.rnd = np.random.default_rng(seed)
        G = v2(site.d["inner_gate"]); out = v2(site.d.get("inner_out", (0, 1))); out = out / np.linalg.norm(out)
        self.G, self.out, self.side = G, out, np.array([out[1], -out[0]])
        self.front = G - out * 6.0                     # the wagon's back face

    def plan(self):
        S, rnd, G, out, side = self.site, self.rnd, self.G, self.out, self.side
        front = self.front
        sp = 1.05
        pts = []                                       # jam slots: hex packing in a funnel, ranked by distance
        for i in range(-40, 41):
            for j in range(0, 60):
                p = front + side * (i * sp + (j % 2) * sp / 2) - out * (j * sp * 0.87 + 1.5)
                if abs(i * sp) > 6 + j * sp * 1.6:
                    continue
                if S.walkable(float(p[0]), float(p[1])):
                    pts.append((float(np.linalg.norm(p - front)), p))
        pts.sort(key=lambda q: q[0])
        J = np.array([p for _, p in pts[:self.n]])
        n = self.n = len(J)
        Gd = S.nav()
        cand = np.array([(Gd["xs"][i], Gd["ys"][j]) for i in range(Gd["nx"]) for j in range(Gd["ny"]) if Gd["W"][i, j]])
        rel = (cand - G) @ (-out)
        dd = np.hypot(*(cand - G).T)
        cand = cand[(rel > 30) & (dd > 50) & (dd < 230)]
        K = int(round(self.T_END / DT)) + 1
        T = np.arange(K) * DT
        PX = np.zeros((K, n)); PY = np.zeros((K, n))
        t_arr = np.zeros(n)
        exit_pts = G + out * rnd.uniform(25, 120, n)[:, None] + side * (rnd.normal(0, 1, n) * rnd.uniform(4, 40, n))[:, None]
        polys = []
        goal = front - out * 1.0
        for k in range(n):
            s0 = cand[rnd.integers(len(cand))]
            P, s = path(S, s0, goal)
            dJ = np.linalg.norm(J[k] - front)
            dist_g = np.linalg.norm(P - front, axis=1)
            near = dist_g < dJ + 3.0
            cut = int(np.argmax(near)) if near.any() else len(P) - 1
            Q = np.vstack([P[:max(cut, 1)], J[k]])
            sq = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(Q, axis=0), axis=1))])
            v = rnd.uniform(3.2, 5.2)
            t0 = self.T0 + rnd.random() * 4.5 + (0.0 if k < n * 0.7 else rnd.random() * 5)
            t_arr[k] = t0 + sq[-1] / v
            polys.append((Q, sq, v, t0))
        t_gate = self.T_PULL1 + 0.3 + np.arange(n) / self.RATE
        vf = 3.4
        for k in range(n):
            Q, sq, v, t0 = polys[k]
            dJ = np.linalg.norm(J[k] - front)
            t_go = max(t_gate[k] - dJ / vf, t_arr[k], self.T_PULL1)
            F = np.vstack([J[k], front + side * rnd.uniform(-1.5, 1.5), G + side * rnd.uniform(-2.5, 2.5), G + out * 10, exit_pts[k]])
            sf = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(F, axis=0), axis=1))])
            sk = np.clip(v * (T - t0), 0, sq[-1])
            px = np.interp(sk, sq, Q[:, 0]); py = np.interp(sk, sq, Q[:, 1])
            wait = (T > t_arr[k]) & (T < t_go)
            jit = 0.25 * np.sin(T * 1.7 + k) * wait
            px = px + side[0] * jit; py = py + side[1] * jit
            m = T >= t_go
            skf = np.clip(vf * (T[m] - t_go), 0, sf[-1])
            px[m] = np.interp(skf, sf, F[:, 0]); py[m] = np.interp(skf, sf, F[:, 1])
            PX[:, k], PY[:, k] = px, py
        self.T, self.K, self.PX, self.PY = T, K, PX, PY
        PD = np.zeros((K, n)); PD[1:] = np.cumsum(np.hypot(np.diff(PX, axis=0), np.diff(PY, axis=0)), axis=0)
        face_gate = math.atan2(-out[0], out[1])
        YAW = np.zeros((K, n)); yaw = np.full(n, face_gate)
        for k in range(K):
            if k:
                dx, dy = PX[k] - PX[k - 1], PY[k] - PY[k - 1]
                mv = dx * dx + dy * dy > 0.004
                tgt = np.where(mv, np.arctan2(-dx, dy), face_gate)
                d = (tgt - yaw + np.pi) % (2 * np.pi) - np.pi
                yaw = yaw + np.clip(d, -0.6, 0.6)
            YAW[k] = yaw
        self.PD, self.YAW = PD, YAW
        self.Z = S.g(front)

    def build(self, coll):
        rnd = random.Random(7)
        g = SW.Geo(); fm = []
        n = self.n
        hg = np.array([rnd.uniform(1.5, 1.9) if rnd.random() > 0.12 else rnd.uniform(1.0, 1.3) for _ in range(n)])
        for i in range(n):
            n0 = len(g.fc)
            SW.person_geo(g, i, hg[i], rnd.random() < 0.35, rnd)
            base = [rnd.randrange(len(SW.SHIRTS)), len(SW.SHIRTS) + rnd.randrange(len(SW.PANTS)),
                    len(SW.SHIRTS) + len(SW.PANTS) + rnd.randrange(len(SW.SKINS)),
                    len(SW.SHIRTS) + len(SW.PANTS) + len(SW.SKINS) + rnd.choice([0, 0, 1, 1, 1, 2, 3, 4])]
            fm += [base[c] for c in g.fc[n0:]]
        mats = [L.mat(f"SW_shirt{i}", c, 0.75) for i, c in enumerate(SW.SHIRTS)] + [L.mat(f"SW_pants{i}", c, 0.85) for i, c in enumerate(SW.PANTS)] \
            + [L.mat(f"SW_skin{i}", c, 0.6) for i, c in enumerate(SW.SKINS)] + [L.mat(f"SW_hair{i}", c, 0.7) for i, c in enumerate(SW.HAIRS)]
        self.R = g.finish(); self.hg = hg
        self.ob = SW._mesh("TrostEvacCrowd", self.R, g.f, fm, mats, coll)
        wo = self.site.d.get("wagon_obj")            # the set's wagon (trost.py) if present, else a stand-in
        if wo is None:
            import bmesh
            bm = bmesh.new()
            L.box(bm, (0, 0, 1.6), (13.0, 4.6, 0.5), mi=0); L.box(bm, (0, 0, 3.6), (12.4, 4.4, 3.6), mi=1)
            L.cyl(bm, (-6.2, 0, 5.4), (6.2, 0, 5.4), 2.2, seg=10, mi=1)
            for sx in (-4.6, 4.6):
                for sy in (-2.5, 2.5):
                    L.cyl(bm, (sx, sy - 0.25, 1.15), (sx, sy + 0.25, 1.15), 1.15, seg=12, mi=2)
            wo = L.obj_from_bm("TA_CargoWagon", bm, [L.mat("TA_wagonwood", (0.30, 0.17, 0.08), 0.85), L.mat("TA_tarp", (0.55, 0.48, 0.34), 0.9),
                                                     L.mat("TA_wiron", (0.06, 0.06, 0.06), 0.4)], coll)
        wo.hide_render = wo.hide_viewport = False
        self.wagon = wo
        self.w0 = self.G - self.out * 6.5
        self.wyaw0 = math.atan2(self.side[1], self.side[0]) + math.radians(4)

    def wagon_state(self, t):
        u1 = _ss(self.T_PULL0, self.T_PULL0 + 0.8, t)                 # swing it lengthwise
        u2 = _ss(self.T_PULL0 + 0.6, self.T_PULL1 + 0.8, t)           # haul it through and aside
        p = self.w0 + self.out * 26 * u2 + self.side * 10 * _ss(self.T_PULL1, self.T_PULL1 + 1.5, t)
        return p, self.wyaw0 + (math.pi / 2 - math.radians(4)) * u1

    def update(self, t):
        on = 0.0 <= t < self.T_END + 6
        self.ob.hide_render = self.ob.hide_viewport = not on
        p, yaw = self.wagon_state(t)
        self.wagon.location = (p[0], p[1], self.site.g(p)); self.wagon.rotation_euler = (0, 0, yaw)
        if not on:
            return
        tt = min(max(t, 0.0), self.T_END)
        kf = tt / DT; k0 = min(int(kf), self.K - 1); k1 = min(k0 + 1, self.K - 1); f = kf - k0
        n = self.n
        pos = np.zeros((n, 3))
        pos[:, 0] = self.PX[k0] * (1 - f) + self.PX[k1] * f; pos[:, 1] = self.PY[k0] * (1 - f) + self.PY[k1] * f
        pos[:, 2] = self.Z
        yaw = self.YAW[k0] + (((self.YAW[k1] - self.YAW[k0]) + np.pi) % (2 * np.pi) - np.pi) * f
        pd = self.PD[k0] * (1 - f) + self.PD[k1] * f
        spd = (self.PD[k1] - self.PD[k0]) / DT
        pm = np.clip(spd / 1.6, 0, 1)
        ph = 2 * np.pi * pd / (1.5 * self.hg)
        Ar = np.zeros((n, 7)); Ae = np.zeros((n, 7))
        s = np.sin(ph) * 0.75 * pm
        Ar[:, 1] = s; Ar[:, 2] = -s; Ar[:, 3] = -0.8 * s; Ar[:, 4] = 0.8 * s
        jam = pm < 0.1
        Ar[jam, 3] = Ar[jam, 4] = 0.3 + 0.35 * np.sin(t * 3 + np.arange(n)[jam])      # arms up in the jam
        lean = -0.2 * pm
        vis = np.full(n, self.ps)
        rel = pos[:, :2] - self.G
        vis[(np.linalg.norm(rel, axis=1) > 150) & (rel @ self.out > 0)] = 0.0       # gone over the fields
        co = SW._deform(self.R, Ar, Ae, lean, vis, yaw, pos)
        self.ob.data.vertices.foreach_set("co", co.astype(np.float32).ravel()); self.ob.data.update()


def evac_flyers(SQ, site, EV, used):
    """Mikasa drops in front of the merchant (Dimo Reeves), who backs off; then she leaves for the front."""
    G, out, side = EV.G, EV.out, EV.side
    mk = SQ.flyer("mikasa_gate", "cadet", "black", scarf=True)
    i, r0 = site.roof_near(G - out * 45 + side * 25, used); used.add(i)
    land = site.P(EV.front - out * 3.0)
    mk.stand(6.0, EV.T_MIK - 1.1, r0, 0.0).hop(EV.T_MIK - 1.1, EV.T_MIK, r0, land, apex=6.0)
    mk.stand(EV.T_MIK, 14.5, land, odm.yaw_of(np.append(out, 0)), "crouch")
    i2, r1 = site.roof_near(G - out * 90, used); used.add(i2)
    mk.hop(14.5, 15.6, land, r1).gone(16.9)
    dimo = SQ.flyer("dimo", "garrison", "grey", H=1.75)
    p0 = site.P(EV.front - out * 0.5 + side * 2.0)
    dimo.stand(2.0, EV.T_MIK + 0.3, p0, odm.yaw_of(np.append(-out, 0)), "wave")
    p1 = site.P(EV.front - out * 4.5 + side * 6.5)
    dimo.walk(EV.T_MIK + 0.3, EV.T_MIK + 1.4, p0, p1, "run").stand(EV.T_MIK + 1.4, 30.0, p1, odm.yaw_of(np.append(-side, 0)), "stand")
    return mk, dimo


def pyxis_flyers(SQ, site, rnd):
    """Pixis on the wall top above the inner gate (bald, white moustache, Garrison cloak), the ranks below, and the
    deserters who walk off toward the gate, stop at the speech and turn back."""
    out = v2(site.d.get("inner_out", (0, 1))); out = out / np.linalg.norm(out); side = np.array([out[1], -out[0]])
    G = v2(site.d["inner_gate"])
    P = v3(site.d.get("pyxis_pt", (G[0] - out[0] * 2, G[1] - out[1] * 2, site.wall_z)))
    T0, T1 = BEATS["pyxis"]
    face = odm.yaw_of(np.append(-out, 0))
    px = SQ.flyer("pyxis", "garrison", "bald", moustache=True)
    px.stand(T0 - 2.0, T0 + 1.0, P, face, "stand").stand(T0 + 1.0, T1 + 4, P, face, "wave")
    for k, s in enumerate((-1, 1)):
        SQ.flyer(f"aide{k}", "garrison", "dark").stand(T0 - 2.0, T1 + 4, P + np.array([*(side * s * 2.2 + out * 0.8), 0]), face, "salute")
    base = G - out * 30
    for k in range(36):
        r, c = divmod(k, 9)
        p = base + side * (c - 4) * 2.6 - out * r * 2.8
        f = SQ.flyer(f"rank{k}", rnd.choice(["garrison", "garrison", "cadet"]), rnd.choice(["dark", "brown", "ash", "black", "blond"]))
        f.stand(T0 - 2.0, T1 + 4, site.P(p), odm.yaw_of(np.append(out, 0)), "salute" if k % 3 == 0 else "stand")
    for k in range(14):
        p0 = base + side * rnd.uniform(-14, 14) - out * rnd.uniform(2, 10)
        p_away = G - out * 8 + side * rnd.uniform(-5, 5)
        p_mid = p0 + (p_away - p0) * 0.85
        p_back = base + side * rnd.uniform(-12, 12) - out * (12 + rnd.uniform(0, 6))
        f = SQ.flyer(f"deserter{k}", rnd.choice(["garrison", "cadet"]), rnd.choice(["dark", "brown", "ash", "auburn"]))
        tA = T0 + rnd.uniform(0, 0.6)
        f.walk(tA, tA + 2.4, site.P(p0), site.P(p_mid), "run")
        f.stand(tA + 2.4, tA + 3.2, site.P(p_mid), face, "stand")
        f.walk(tA + 3.2, tA + 5.6, site.P(p_mid), site.P(p_back), "run")
        f.stand(tA + 5.6, T1 + 4, site.P(p_back), odm.yaw_of(np.append(out, 0)), "stand")


# ====================================================================== site adapters
def roofs_from_scatter(town="Town", variants="HouseVariants", margin_fn=None, ground=None):
    """Roof-ridge perches (x, y, z) read back from scene.py's / trost.py's GN house scatter."""
    ob = bpy.data.objects.get(town)
    if ob is None:
        return np.zeros((0, 3))
    me = ob.data
    n = len(me.vertices)
    co = np.zeros(n * 3); me.vertices.foreach_get("co", co); co = co.reshape(n, 3)
    var = np.zeros(n, np.int32); me.attributes["variant"].data.foreach_get("value", var)
    scl = np.zeros(n * 3); me.attributes["scl"].data.foreach_get("vector", scl); scl = scl.reshape(n, 3)[:, 0]
    tops = {}
    for k, o in enumerate(bpy.data.collections[variants].objects):
        if o.type == "MESH":
            digits = "".join(ch for ch in o.name if ch.isdigit())
            tops[int(digits) if digits else k] = max(v.co.z for v in o.data.vertices)
    out = []
    for i in range(n):
        x, y = co[i, 0], co[i, 1]
        if margin_fn and not margin_fn(x, y):
            continue
        z0 = ground(x, y) if ground else L.height(x, y)
        out.append((x, y, z0 + tops.get(int(var[i]), 14.0) * scl[i] - 0.2))
    return np.array(out)

def site_from_trost(T=None):
    """Fill the site dict from agent C's trost.py (after the set is built, i.e. from a render script):
        site = TA.site_from_trost(); TA.setup(site)"""
    import sys
    T = T or sys.modules.get("trost")
    hq = T.SUPPLY_HQ
    w, d_ = hq["size"]; h = hq.get("store_z", (0, 10))[1] + 1.5
    av = getattr(T, "AVENUE", None)
    inw = np.array(av[1], float) - np.array(av[0], float) if av else np.array([0.0, 1.0])
    gz = lambda x, y: T.ground_z(x, y) + (0.12 if T.in_district(x, y, 0.0) else 0.0)
    in_hq = getattr(T, "_in_hq", lambda x, y, p: False)
    roofs = roofs_from_scatter(ground=T.ground_z, margin_fn=lambda x, y: T.in_district(x, y, 20) and not in_hq(x, y, 4))
    wall_pts = [(T.R * math.sin(a), -T.S - T.R * math.cos(a), L.WALL_H + 0.3) for a in (-0.06, 0.06, -0.1, 0.1, -0.14, 0.14, -0.18, 0.18)]
    bt = T.BELL_TOWER
    return dict(gate=T.OUTER_GATE, inward=tuple(inw / np.linalg.norm(inw)), wall_z=L.WALL_H,
                hq=hq["center"], hq_size=(w, d_, h), hq_roof=[], hq_cutaway_fn=getattr(T, "set_hq_cutaway", None),
                hq_titan_spots=hq.get("titan_spots"),
                boulder=T.BOULDER[:2], boulder_obj=bpy.data.objects.get("TrostBoulder"), boulder_r=max(T.BOULDER_SIZE) / 2.3,
                boulder_origin="bottom", roofs=roofs, ground=gz, walkable=T.walkable,
                bounds=(-T.W, T.W, T.OUTER_GATE[1] - 140.0, 140.0), pyre=T.PLAZA[:2], wall_pts=wall_pts,
                inner_gate=T.INNER_GATE, inner_out=(0.0, 1.0), pyxis_pt=T.WALLTOP_SPEECH,
                bell_tower=bt["xy"], bell_tower_top=bt.get("top_z", 64.0),
                wagon_obj=bpy.data.objects.get("TrostCargoWagon"),
                cannon_square=(T.INNER_GATE[0], -40.0))   # canon: the Garrison corners the trio near the wall
