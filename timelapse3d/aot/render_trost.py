"""TROST SEGMENT (EP1 beats 12-20): one continuous sky take on agent C's Trost set (aot/trost.py) with agent D's
action layer (aot/trost_action.py), ~2:35 of video.  Run after scene.py in the same Blender session (render_trost.sh):
    AOT_SET=trost AOT_PLUGINS=colossal_asset blender -b -P aot/scene.py -P aot/render_trost.py -- --cam trost_overview \
        --rt-out DIR [--v0 0 --v1 52] [--fps 15] [--rt-samples 2] [--stills 8.0,13.9] [--step 1]
Every frame is a pure function of its VIDEO time v (camera, Colossal, lightning, breach FX, TA.update(T(v))),
so any window / still renders on its own.

Video timeline (v, seconds):
   0-4     graduation night ends: dawn over Trost, high and descending to the outer wall
   4-9     on Trost's wall top Eren strikes his "I can do this!" pose among the cadet squad doing cannon maintenance
   9.0     lightning behind him, the scene darkens, the camera shakes, the Colossal's head is there at once (rise 9-11.4)
   12-14   wind-up and the KICK at v = 14: the outer gate bursts, blocks arc into the town, dust; the Colossal fades
   14-     trost_action time T = Tmap(v): T = 0 at the kick, D's 125 s action remapped with timelapse speed ramps
           (brisk; holds only for the overlay beats: salute 2.5 s, Pyxis 3 s, Marco 2.5 s).  Ends ~v 144.5.
Camera: one spline through keys in video time (chord-scaled Hermite, re-timed by a monotone arc-length curve so the
speed is C1-smooth: no jumps at keys).  Never south of the outer wall while the Colossal is visible.
"""
import bpy, bmesh, math, os, sys, time, random, argparse
import numpy as np
from mathutils import Vector, noise

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ap = argparse.ArgumentParser(allow_abbrev=False)
ap.add_argument("--rt-out", required=True)
ap.add_argument("--fps", type=float, default=15.0)
ap.add_argument("--v0", type=float, default=0.0)
ap.add_argument("--v1", type=float, default=1e9)
ap.add_argument("--rt-samples", type=int, default=2)
ap.add_argument("--step", type=int, default=1, help="render every Nth frame (the encoder repeats frames)")
ap.add_argument("--stills", default="", help="comma list of video times to render as stills")
ap.add_argument("--dry", action="store_true")
B, _ = ap.parse_known_args(argv)

import aotlib as L
import trost as TR
import trost_action as TA
import people_kit as PK
import smokecards as SC

CA = sys.modules.get("colossal_asset")
GX, GY = TR.OUTER_GATE
STRIKE = Vector((-7.0, GY - 22, 0))
V_LIGHT, V_KICK = 9.0, 14.0

def ss(a, b, x):
    u = min(1.0, max(0.0, (x - a) / (b - a))) if b != a else float(x >= b)
    return u * u * (3 - 2 * u)

def bump(t, a, b, c, d):
    return ss(a, b, t) * (1 - ss(c, d, t))

# ====================================================================== site dict for trost_action
def roofs_from_town():
    ob = bpy.data.objects.get("Town"); me = ob.data
    n = len(me.vertices)
    co = np.zeros(n * 3); me.vertices.foreach_get("co", co); co = co.reshape(n, 3)
    var = np.zeros(n, np.int32); me.attributes["variant"].data.foreach_get("value", var)
    scl = np.zeros(n * 3); me.attributes["scl"].data.foreach_get("vector", scl); scl = scl.reshape(n, 3)[:, 0]
    tops = {}
    for k, o in enumerate(bpy.data.collections["HouseVariants"].objects):
        if o.name.startswith("TH") and o.name[2:].isdigit():
            tops[int(o.name[2:])] = max(v.co.z for v in o.data.vertices)
    out = []
    for i in range(n):
        x, y = co[i, 0], co[i, 1]
        if not TR.in_district(x, y, 20) or y > -40:
            continue
        out.append((x, y, L.height(x, y) + tops.get(int(var[i]), 14.0) * scl[i] - 0.2))
    return np.array(out)

def site():
    hq = TR.SUPPLY_HQ["center"]; w, d = TR.SUPPLY_HQ["size"]; h = 12.0
    roofs = roofs_from_town()
    keep = (np.abs(roofs[:, 0] - hq[0]) > w / 2 + 6) | (np.abs(roofs[:, 1] - hq[1]) > d / 2 + 6)
    roofs = roofs[keep]
    def walk(x, y):
        if abs(x - hq[0]) < w / 2 + 1 and abs(y - hq[1]) < d / 2 + 1:
            return False
        if TR.in_canal(x, y) and not TR.on_road(x, y):
            return False
        return TR.walkable(x, y)
    def ground(x, y):
        g = L.height(x, y)
        return max(g, 0.0) + 0.16 if TR.in_district(x, y, 0.0) else g
    wall_pts = []
    for a in (-0.05, 0.05, -0.09, 0.09, -0.13, 0.13, -0.17, 0.17):
        r = TR.R - 1.0
        wall_pts.append((r * math.sin(a), -TR.S - r * math.cos(a), L.WALL_H + 0.3))
    up = [bpy.data.objects.get(n) for n in TR.HQ_UPPER]
    return dict(gate=(GX, GY), inward=(0.0, 1.0), wall_z=L.WALL_H, hq=hq, hq_size=(w, d, h), hq_roof=[o for o in up if o],
                boulder=(TR.BOULDER[0], TR.BOULDER[1]), roofs=roofs, ground=ground, walkable=walk,
                bounds=(-TR.W, TR.W, GY - 140.0, -8.0), pyre=(TR.INNER_GATE[0] + 10, -42.0), wall_pts=wall_pts,
                # extras for D (optional keys): set landmarks and sizes
                boulder_r=6.5, boulder_size=TR.BOULDER_SIZE, bell=TR.BELL_TOWER["xy"], belfry_c=TR.BELL_TOWER["belfry_c"],
                inner_gate=TR.INNER_GATE, wagon="TrostCargoWagon", pyxis_pt=TR.WALLTOP_SPEECH, plaza=TR.PLAZA[:2],
                evac_route=TR.EVAC_ROUTE, streets=TR.street_polylines())

# ====================================================================== time map v -> T (trost_action clock)
# (T0, T1, video seconds) after the kick; pchip through the cumulative knots -> C1-smooth speed ramps
SEGS = [(0, 2, 2.5), (2, 7.5, 6.0), (7.5, 14, 8.0), (14, 17.5, 3.5), (17.5, 21, 4.5), (21, 26.5, 6.0), (26.5, 44, 15.0),
        (44, 46, 2.5), (46, 54, 10.0), (54, 56.5, 3.0), (56.5, 59, 3.5), (59, 63.5, 5.5), (63.5, 65.5, 2.5), (65.5, 68, 2.0),
        (68, 74.5, 3.0), (74.5, 79, 5.0), (79, 82, 3.5), (82, 99, 16.0), (99, 104, 6.0), (104, 111, 8.0), (111, 113, 2.0),
        (113, 117.5, 5.0), (117.5, 120.5, 2.5), (120.5, 125, 5.0)]
KV = [V_KICK]; KT = [0.0]
for a, b, dv in SEGS:
    KV.append(KV[-1] + dv); KT.append(float(b))
V_END = KV[-1]

def _pchip_m(T, S):
    D = [(S[i + 1] - S[i]) / (T[i + 1] - T[i]) for i in range(len(T) - 1)]
    return [D[0]] + [0.0 if D[i - 1] * D[i] <= 0 else 2 * D[i - 1] * D[i] / (D[i - 1] + D[i]) for i in range(1, len(D))] + [D[-1]]

def _pchip(T, S, m, t):
    t = min(max(t, T[0]), T[-1])
    i = 0
    while i < len(T) - 2 and T[i + 1] <= t:
        i += 1
    h = T[i + 1] - T[i]; s = (t - T[i]) / h
    h00, h10, h01, h11 = 2 * s ** 3 - 3 * s ** 2 + 1, s ** 3 - 2 * s ** 2 + s, -2 * s ** 3 + 3 * s ** 2, s ** 3 - s ** 2
    return h00 * S[i] + h10 * h * m[i] + h01 * S[i + 1] + h11 * h * m[i + 1]

KM = _pchip_m(KV, KT)
def Tmap(v):
    return 0.0 if v <= V_KICK else _pchip(KV, KT, KM, v)

def Vmap(T):
    """Inverse of Tmap (bisection)."""
    lo, hi = V_KICK, V_END
    for _ in range(50):
        mid = (lo + hi) / 2
        if Tmap(mid) < T:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2

# ====================================================================== camera spline (as render_fast)
def _herm(p0, p1, p2, p3, u):
    d01, d12, d23 = (p1 - p0).length, (p2 - p1).length, (p3 - p2).length
    m1 = (p2 - p0) * (d12 / (d01 + d12)) if d01 + d12 > 1e-9 else p2 - p1
    m2 = (p3 - p1) * (d12 / (d12 + d23)) if d12 + d23 > 1e-9 else p2 - p1
    h00, h10, h01, h11 = 2 * u ** 3 - 3 * u ** 2 + 1, u ** 3 - 2 * u ** 2 + u, -2 * u ** 3 + 3 * u ** 2, u ** 3 - u ** 2
    return p1 * h00 + m1 * h10 + p2 * h01 + m2 * h11

def _pchip_m0(T, S):
    D = [(S[i + 1] - S[i]) / (T[i + 1] - T[i]) for i in range(len(T) - 1)]
    return [0.0] + [0.0 if D[i - 1] * D[i] <= 0 else 2 * D[i - 1] * D[i] / (D[i - 1] + D[i]) for i in range(1, len(D))] + [0.0]

class Channel:
    def __init__(self, T, pts):
        self.T, self.P = T, [Vector(p) for p in pts]
        n = len(pts); self.segs = []; S = [0.0]
        for i in range(n - 1):
            q = [self.P[max(0, min(n - 1, j))] for j in (i - 1, i, i + 1, i + 2)]
            acc = [0.0]; prev = q[1]
            for k in range(1, 65):
                p = _herm(*q, k / 64); acc.append(acc[-1] + (p - prev).length + 1e-7); prev = p
            self.segs.append((q, acc)); S.append(S[-1] + acc[-1])
        self.S, self.m = S, _pchip_m0(T, S)
    def at(self, t):
        s = _pchip(self.T, self.S, self.m, t)
        i = 0
        while i < len(self.segs) - 1 and self.S[i + 1] <= s:
            i += 1
        q, acc = self.segs[i]; r = s - self.S[i]
        k = 0
        while k < len(acc) - 2 and acc[k + 1] < r:
            k += 1
        f = min(1.0, max(0.0, (r - acc[k]) / (acc[k + 1] - acc[k])))
        return _herm(*q, (k + f) / 64)

def P3(xy, z):
    return (float(xy[0]), float(xy[1]), float(z))

def cam_keys():
    S = TA.STATE; C = S["C"]; st = S["site"]
    g, inw, side, hq = st.gate, st.inw, st.side, st.hq
    er, ar = C["e_roof"], C["a_roof"]
    M, A0, Q, cxy = C["M"], C["A0"], C["Q"], C["cannon_xy"]
    stop, P0, mp, Cp = C["stop"], st.pyre, C["mpos"], C["C_pt"]
    eye = (er[:2] + ar[:2]) / 2
    at = lambda t: np.array(S["ATD"].state(t)[0][:2])
    K = []
    def k(v, loc, tgt, lens):
        K.append((float(v), Vector(loc), Vector(tgt), float(lens)))
    def kt(T, loc, tgt, lens):
        k(Vmap(T), loc, tgt, lens)
    ex, ey = EREN_WALL
    # ---- intro (video time)
    k(0.0, (-560, 240, 560), (40, -560, 0), 26)
    k(4.0, (-210, -600, 220), (-20, -850, 30), 30)
    k(7.2, (ex - 18, ey + 44, 82), (ex, ey, L.WALL_H + 0.8), 58)
    k(9.0, (ex - 12, ey + 52, 82), (ex + 6, ey - 8, L.WALL_H + 5), 46)
    k(11.4, (ex + 4, ey + 80, 78), (-14, GY - 14, 56), 34)          # Eren small on the wall, the head beyond
    k(13.6, (60, GY + 150, 112), (0, GY + 15, 22), 32)                 # the gate in frame for the kick
    # ---- action (trost_action time)
    kt(2.0, (95, GY + 125, 150), (0, GY + 110, 0), 30)
    kt(6.0, (110, GY + 150, 175), (0, GY + 210, 0), 30)
    kt(7.6, P3(eye - side * 55 - inw * 45, er[2] + 48), P3(eye + inw * 6, er[2] - 4), 34)
    kt(13.7, P3(eye - side * 45 - inw * 30, er[2] + 40), P3(eye, er[2] - 2), 40)
    wr = S["SQ"].pos("w1", 15.0)
    kt(14.9, P3(wr[:2] - inw * 50 + side * 30, wr[2] + 40), P3(wr[:2], wr[2] - 4), 36)
    kt(16.6, P3(wr[:2] - inw * 42 + side * 22, wr[2] + 36), P3(wr[:2], wr[2] - 6), 36)
    # evacuation at the inner gate (D's beat if present, else a placeholder pass over the jammed wagon)
    ev = TA.BEATS.get("evac") or TA.BEATS.get("evacuation")
    igx = TR.INNER_GATE[0]
    if ev:
        kt(17.9, (igx + 90, -190, 140), (igx, -15, 0), 32); kt(19.4, (igx + 75, -165, 120), (igx, 5, 0), 32)
    else:
        kt(18.0, (igx + 90, -190, 150), (igx, -15, 0), 32); kt(19.0, (igx + 80, -175, 140), (igx, -10, 0), 32)
    kt(20.0, P3(hq - inw * 120 + side * 60, 140), P3(hq, 0), 32)
    kt(21.0, P3(hq - inw * 100 + side * 30, 120), P3(hq, 0), 32)
    kt(21.8, P3(M + side * 80 - inw * 20, 90), P3((M + hq) / 2, 0), 30)
    kt(26.2, P3(M + side * 60 - inw * 40, 70), P3(M, 2), 32)
    kt(27.5, P3(A0 + side * 70 - inw * 50, 62), P3(A0, 8), 30)
    bell = [n for n in TA.BEATS if "bell" in n]
    for T in ((31.0, 40.0, 43.0) if bell else (31.0, 35.0, 39.0, 43.0)):
        a = at(T)
        kt(T, P3(a + side * 70 - inw * 50, 78), P3(a, 6), 30)
    if bell:
        b0, b1 = TA.BEATS[bell[0]]
        bx, by = TR.BELL_TOWER["xy"]
        kt((b0 + b1) / 2, (bx + 60, by - 70, 85), (bx, by, 35), 34)
    kt(45.0, P3(hq - inw * 60 + side * 30, 90), P3(hq, 4), 32)
    kt(46.6, P3(hq - inw * 26 + side * 14, 60), P3(hq, 1), 30)
    kt(52.6, P3(hq - inw * 22 + side * 10, 52), P3(hq, 1), 30)
    kt(56.4, P3(Cp + side * 45 - inw * 40, 50), P3(Cp, 4), 32)
    kt(58.8, P3(Cp + side * 38 - inw * 34, 44), P3(Q, 3), 32)
    mid = (Q + cxy) / 2
    perp = np.array([C["cdir"][1], -C["cdir"][0]])
    kt(61.4, P3(mid + perp * 40, 62), P3(mid, 5), 32)
    kt(63.2, P3(mid + perp * 36, 58), P3(Q, 6), 34)
    kt(64.4, P3(Q + perp * 14 - C["cdir"] * 22, 52), P3(Q + C["cdir"] * 5, 2), 34)
    kt(66.6, P3(Q + perp * 12 - C["cdir"] * 18, 46), P3(Q + C["cdir"] * 5, 2), 40)     # salute hold
    px = TA.BEATS.get("pyxis")
    sp = TR.WALLTOP_SPEECH
    p0, p1 = (px if px else (68.5, 74.0))
    kt(p0 + 0.5, (sp[0] + 55, sp[1] - 95, 92), (sp[0], sp[1], sp[2]), 36)
    kt(p1 - 0.5, (sp[0] + 45, sp[1] - 80, 84), (sp[0], sp[1], sp[2]), 40)              # Pyxis hold
    for T in (75.5, 80.0, 84.0, 88.0, 92.0, 96.0, 100.0, 103.5):
        a = at(T)
        kt(T, P3(a + side * 75 + inw * 45, 135), P3(a - inw * 20, 10), 28)
    kt(105.2, P3(stop + inw * 40 + side * 55, 58), P3(stop + inw * 22, 6), 32)
    kt(109.0, P3(stop + inw * 36 + side * 45, 50), P3(stop + inw * 24, 4), 34)
    kt(114.5, P3(P0 - inw * 60 + side * 50, 64), P3(P0 + inw * 8, 0), 30)
    kt(118.0, P3(mp - inw * 42 + side * 30, 60), P3(mp, 0), 40)
    kt(120.4, P3(mp - inw * 38 + side * 27, 56), P3(mp, 0), 42)                         # Marco hold
    kt(124.9, P3(P0 - inw * 140 + side * 90, 150), P3(P0 + inw * 10, 0), 28)            # pull up, dusk
    K.sort(key=lambda e: e[0])
    out = []
    for e in K:
        if out and e[0] - out[-1][0] < 0.4:
            continue
        out.append(e)
    return out

_CAM = {}
def cam_at(v):
    if not _CAM:
        ks = cam_keys(); T = [e[0] for e in ks]
        lnl = [math.log(e[3]) for e in ks]
        _CAM.update(loc=Channel(T, [e[1] for e in ks]), tgt=Channel(T, [e[2] for e in ks]), T=T, lnl=lnl, ml=_pchip_m0(T, lnl))
        print("[trost] camera keys:", len(ks))
    loc, tgt = _CAM["loc"].at(v), _CAM["tgt"].at(v)
    lens = math.exp(_pchip(_CAM["T"], _CAM["lnl"], _CAM["ml"], v))
    if v < 17.0:                                   # never behind the Colossal: stay north of the outer wall
        loc.y = max(loc.y, GY + 25)
    loc.z = max(loc.z, L.height(loc.x, loc.y) + 25)
    if V_KICK <= v < V_KICK + 1.0:
        kk = (V_KICK + 1.0 - v) * 2.5
        loc = loc + Vector((noise.noise(Vector((v * 40, 0, 0))), noise.noise(Vector((0, v * 40, 3))), noise.noise(Vector((5, 1, v * 40))))) * kk
    rot = (tgt - loc).to_track_quat("-Z", "Y").to_euler()
    a = 0.011 * bump(v, V_LIGHT, V_LIGHT + 0.06, V_LIGHT + 0.15, V_LIGHT + 1.1) + 0.006 * bump(v, V_KICK - 0.02, V_KICK + 0.02, V_KICK + 0.1, V_KICK + 1.0)
    if a:
        rot.x += a * noise.noise(Vector((v * 31, 0.5, 7))); rot.z += a * noise.noise(Vector((2.5, v * 29, 1)))
    return loc, rot, lens

# ====================================================================== intro: Eren and the squad on the wall top
EREN_WALL = (-24.0, None)
def _wall_pt(x, inset):
    """Point on the district wall walk at x near the tip; inset > 0 = toward the town side."""
    y = -TR.S - math.sqrt(TR.R ** 2 - x * x)
    n = Vector((-x, -TR.S - y)).normalized()           # toward the round end's centre (inward)
    return (x + n.x * inset, y + n.y * inset)

INTRO = []
def build_intro():
    global EREN_WALL
    ex, ey = _wall_pt(-44.0, 1.8); EREN_WALL = (ex, ey)        # clear of the gatehouse pilasters (|x| 10-17)
    z = L.WALL_H + 0.25
    INTRO.append(PK.person("eren", (ex, ey, z), yaw=0.0, pose="salute"))          # facing the town, Colossal behind
    for k, (pre, dx, ins, yaw, pose) in enumerate((("connie", -6, 1.0, 0.6, "stand"), ("sasha", 5, 1.2, -0.5, "stand"),
                                                  ("cadet:2", -11, -1.5, 1.4, "kneel"), ("cadet:5", 9, -1.0, -1.2, "kneel"),
                                                  ("cadet:1", 14, 1.6, 2.6, "stand"), ("cadet:3", -16, 0.8, -2.8, "stand"))):
        x, y = _wall_pt(-44.0 + dx, ins)
        INTRO.append(PK.person(pre, (x, y, z), yaw=yaw, pose=pose))

def intro_at(v):
    on = v < V_KICK + 0.25                              # the blast sweeps the wall top; the squad launches off (cut)
    for e in INTRO:
        e.hide_render = e.hide_viewport = not on

# ====================================================================== lightning, darkness, dawn
FLICKER = ((V_LIGHT + 0.02, V_LIGHT + 0.10, 0), (V_LIGHT + 0.14, V_LIGHT + 0.19, 1), (V_LIGHT + 0.24, V_LIGHT + 0.35, 0))

def _bolt(name, seed, top=720.0):
    rnd = random.Random(seed)
    bm = bmesh.new()
    def channel(p, n, step, r, spread, depth=0):
        pts = [p]
        for kk in range(n):
            q = pts[-1] + Vector((rnd.uniform(-spread, spread), rnd.uniform(-spread, spread), -step * rnd.uniform(0.7, 1.3)))
            if depth == 0:
                left = n - kk
                q.x += (STRIKE.x - q.x) / max(1, left) * 0.8; q.y += (STRIKE.y - q.y) / max(1, left) * 0.8
            q.z = max(q.z, 0.0); pts.append(q)
        for a, b in zip(pts, pts[1:]):
            L.cyl(bm, a, b, r, r * 0.92, seg=6)
        return pts
    main = channel(Vector((STRIKE.x + rnd.uniform(-60, 60), STRIKE.y - rnd.uniform(20, 80), top)), 34, top / 34, 1.7, 14)
    for kk in range(4):
        st = main[rnd.randrange(4, 22)]
        channel(st.copy(), rnd.randint(5, 10), rnd.uniform(14, 24), 0.8, 18, depth=1)
    m = bpy.data.materials.new(name + "Mat"); m.use_nodes = True
    nt = m.node_tree; nt.nodes.remove(nt.nodes["Principled BSDF"])
    em = nt.nodes.new("ShaderNodeEmission"); em.inputs["Color"].default_value = (1.0, 0.70, 0.22, 1); em.inputs["Strength"].default_value = 40
    nt.links.new(em.outputs[0], nt.nodes["Material Output"].inputs["Surface"])
    ob = L.obj_from_bm(name, bm, [m]); ob.visible_shadow = False; ob.hide_render = True
    return ob

FX = {}
def build_fx():
    FX["bolts"] = [_bolt("RT_Bolt0", 11), _bolt("RT_Bolt1", 23)]
    ld = bpy.data.lights.new("RT_Flash", "POINT"); ld.color = (1.0, 0.75, 0.35); ld.shadow_soft_size = 30; ld.energy = 0
    lo = bpy.data.objects.new("RT_Flash", ld); lo.location = STRIKE + Vector((0, 0, 140)); bpy.context.scene.collection.objects.link(lo)
    FX["flash"] = ld
    w = bpy.context.scene.world
    FX["bg"] = [(n, n.inputs[1].default_value) for n in w.node_tree.nodes if n.type == "BACKGROUND"]
    FX["suns"] = [(o.data, o.data.energy, tuple(o.data.color)) for o in bpy.data.objects if o.type == "LIGHT" and o.data.type == "SUN"]
    FX["exp"] = bpy.context.scene.view_settings.exposure

def light_at(v):
    """Dawn (v 0-4) and the lightning darkening (v 9-10); afterwards trost_action owns the light (dusk at the pyres)."""
    on = [b for a, c, b in FLICKER if a <= v < c]
    for k, ob in enumerate(FX["bolts"]):
        ob.hide_render = not (on and on[0] == k)
    FX["flash"].energy = 6e6 if on else 0.0
    night = 1 - ss(0.3, 4.2, v)
    dk = bump(v, V_LIGHT - 0.15, V_LIGHT, V_LIGHT + 0.35, V_LIGHT + 1.0)
    sc = bpy.context.scene
    sc.view_settings.exposure = FX["exp"] - 1.6 * dk - 1.4 * night + (0.7 if on else 0.0)
    if v >= 16.0:
        return
    f = (1 - 0.72 * dk) * (1 - 0.8 * night)
    for n, b in FX["bg"]:
        n.inputs[1].default_value = b * f
    for d, e, c in FX["suns"]:
        d.energy = e * f
        d.color = tuple(c[i] * (1 - night) + (0.55, 0.65, 1.0)[i] * night for i in range(3))

# ====================================================================== the Colossal (colossal_asset at Trost's gate)
def colossal_at(v):
    show = V_LIGHT <= v < V_KICK + 3.2
    u = min(1.0, max(0.0, (v - V_LIGHT - 0.02) / 2.4)); rise = 1 - (1 - u) ** 3
    if v < 12.0:
        kick = 0.0
    elif v < 13.3:
        kick = -ss(12.0, 13.3, v)
    else:
        kick = -1.0 + 2.0 * ss(13.3, V_KICK, v)
    return show, rise, kick, ss(V_KICK + 1.0, V_KICK + 2.8, v), ss(V_LIGHT + 0.15, V_LIGHT + 0.45, v), ss(V_LIGHT + 1.0, V_LIGHT + 1.7, v)

# ====================================================================== light breach FX at Trost's outer gate
BR = {}
def build_breach():
    rnd = random.Random(850)
    coll = L.new_coll("TrostBreach")
    m = L.mat("BreachStone", (0.42, 0.40, 0.36), 0.9, var=0.15, var_scale=0.4)
    blocks = []
    for i in range(36):
        s = rnd.uniform(1.2, 5.5) if i < 14 else rnd.uniform(0.5, 1.6)
        bm = bmesh.new(); L.box(bm, (0, 0, 0), (s * rnd.uniform(0.8, 1.4), s, s * rnd.uniform(0.6, 1.0)))
        ob = L.obj_from_bm(f"RT_Block{i}", bm, [m], coll); ob.hide_render = True
        p0 = Vector((GX + rnd.uniform(-6, 6), GY + rnd.uniform(-2, 4), rnd.uniform(3, 18)))
        dist = rnd.uniform(40, 260) if i < 14 else rnd.uniform(15, 120)
        ang = rnd.uniform(-0.55, 0.55)
        land = Vector((GX + math.sin(ang) * dist, GY + math.cos(ang) * dist, 0))
        T = 0.9 + dist / 140.0
        blocks.append(dict(ob=ob, p0=p0, land=land, T=T, spin=Vector((rnd.uniform(-5, 5), rnd.uniform(-5, 5), rnd.uniform(-3, 3))), s=s))
    BR["blocks"] = blocks
    cs = SC.SmokeCards("RT_BreachDust")
    n = 140
    te = np.random.default_rng(3)
    t0 = te.random(n) * 1.2
    pos = np.column_stack([GX + te.normal(0, 6, n), GY + 4 + te.random(n) * 10, te.random(n) * 20])
    vel = np.column_stack([te.normal(0, 8, n), 10 + te.random(n) * 28, te.normal(0, 3, n)])
    cs.add_many(t0, pos, vel, r0=3.0, r1=14.0, life=7.0, rise=2.0, kind="dust", alpha=0.7, tau=1.2)
    for b in blocks[:14]:                                  # puffs where the big blocks land
        tl = b["T"]
        p = np.array([[b["land"].x, b["land"].y, 2.0]] * 10) + te.normal(0, 3, (10, 3))
        cs.add_many(tl + te.random(10) * 0.3, p, te.normal(0, 4, (10, 3)), r0=2.0, r1=9.0, life=5.0, rise=1.5, kind="dust", alpha=0.65, tau=0.8)
    cs.build(coll)
    BR["cards"] = cs
    BR["door"] = bpy.data.objects.get("OuterGate_Door")

def breach_at(v):
    t = v - V_KICK
    if BR.get("door"):
        BR["door"].hide_render = t >= 0
    for b in BR["blocks"]:
        ob = b["ob"]
        if t < 0 or t > 40:
            ob.hide_render = True; continue
        ob.hide_render = False
        u = min(1.0, t / b["T"])
        p = b["p0"].lerp(b["land"], u)
        p.z = b["p0"].z * (1 - u) + (b["s"] * 0.4) * u + 4.0 * b["T"] ** 2 * u * (1 - u) * 9.81 / 4
        ob.location = p
        sp = min(t, b["T"])
        ob.rotation_euler = (b["spin"].x * sp, b["spin"].y * sp, b["spin"].z * sp)
    BR["cards"].update(max(-1.0, t))

# ====================================================================== swap D's boulder for the set's boulder mesh
def adopt_boulder():
    b = TA.STATE.get("boulder")
    mine = bpy.data.objects.get("TrostBoulder")
    if b is None or mine is None or b is mine:
        return
    me = TR.boulder_mesh("TrostBoulderCarry", origin="center")
    for v in me.vertices:
        v.co.z -= 0.6                                    # seat matches D's rest height (centre at ground + 0.8 r)
    me.materials.append(mine.data.materials[0])
    b.data = me
    b.rotation_euler.z = math.radians(28)
    mine.hide_render = mine.hide_viewport = True

# ====================================================================== render loop
sc = bpy.context.scene
cam = sc.camera
cam.data.clip_start = 0.5
if sc.render.engine.startswith("BLENDER_EEVEE"):
    sc.eevee.taa_render_samples = max(1, B.rt_samples)
    ev = sc.eevee
    for k_, v_ in (("use_raytracing", False), ("shadow_resolution_scale", 0.5), ("shadow_ray_count", 1), ("shadow_step_count", 4),
                   ("use_shadows", True)):
        try:
            setattr(ev, k_, v_)
        except Exception:
            pass
else:
    cy = sc.cycles
    cy.samples = B.rt_samples; cy.use_adaptive_sampling = True; cy.use_denoising = True
    try:
        cy.denoiser = "OPENIMAGEDENOISE"; cy.denoising_use_gpu = True
    except Exception:
        pass
    cy.max_bounces, cy.diffuse_bounces, cy.glossy_bounces, cy.transmission_bounces = 3, 1, 1, 2
    cy.volume_bounces = 0; cy.volume_step_rate = 6; cy.volume_max_steps = 96; cy.transparent_max_bounces = 16
    sc.render.use_simplify = True; sc.render.simplify_subdivision_render = 0
    cy.texture_limit_render = "1024"
sc.render.use_persistent_data = True
for n in ("Haze",):
    o = bpy.data.objects.get(n)
    if o:
        o.hide_render = True
sc.render.image_settings.file_format = "PNG"
os.makedirs(B.rt_out, exist_ok=True)

t0 = time.time()
TR.set_hq_cutaway(False); TR.set_wagon(True)
hql = bpy.data.objects.get("TrostHQ_Lift")
if hql:
    hql.hide_render = hql.hide_viewport = True            # D's lift (with the rifle ring) replaces the set's platform
SITE = TA.site_from_trost(TR) if hasattr(TA, "site_from_trost") else site()
TA.setup(SITE, light=True)
if not SITE.get("boulder_obj"):
    adopt_boulder()
print(f"[trost] TA setup {time.time() - t0:.1f}s", TA.info(), "beats:", sorted(TA.BEATS))
build_intro(); build_fx(); build_breach()
col_coll = bpy.data.collections.get("ColossalTitan")
print(f"[trost] setup total {time.time() - t0:.1f}s; video length {V_END:.1f}s; colossal {'on' if (CA and CA.STATE) else 'MISSING'}")

def frame_state(v):
    T = Tmap(v)
    TA.update(T)
    light_at(v)
    show, rise, kick, fade, hl, hr = colossal_at(v)
    if col_coll:
        col_coll.hide_render = not show
        if show and CA and CA.STATE:
            CA.set_pose(kick, rise, fade, hand_l=hl, hand_r=hr, steam=ss(V_LIGHT + 0.1, V_LIGHT + 3.0, v))
    intro_at(v)
    breach_at(v)
    loc, rot, lens = cam_at(v)
    cam.location = loc; cam.rotation_euler = rot; cam.data.lens = lens
    return T

if B.dry:
    for v in np.arange(0, V_END, 2.0):
        T = frame_state(float(v)); print(f"[trost] v={v:.1f} T={T:.2f} cam={tuple(round(c) for c in cam.location)}")
    sys.exit(0)

if B.stills:
    jobs = [(float(x), f"still_v{float(x):06.2f}.png") for x in B.stills.split(",") if x.strip()]
else:
    n0 = int(math.ceil(B.v0 * B.fps)); n1 = int(min(B.v1, V_END) * B.fps)
    jobs = [(f / B.fps, f"rt_{f:05d}.png") for f in range(n0, n1) if f % B.step == 0]
tr = time.time()
for i, (v, fn) in enumerate(jobs):
    tu = time.time()
    T = frame_state(v)
    tu = time.time() - tu
    sc.render.filepath = os.path.join(B.rt_out, fn)
    bpy.ops.render.render(write_still=True)
    el = time.time() - tr
    print(f"[trost] {i + 1}/{len(jobs)} v={v:.2f} T={T:.2f} -> {fn} ({el:.0f}s, {el / (i + 1):.2f}s/f, update {tu:.2f}s)", flush=True)
