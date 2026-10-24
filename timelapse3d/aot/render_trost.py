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
# (T0, T1, video seconds): SET PIECES at ~1x (scaled by SET_K), quick TRANSITIONS (swoops) between them
SET_K = float(os.environ.get("RT_SET_K", "1.25"))
_SP = [  # (T0, T1, dv, is_set_piece)
    (0, 2, 2.0, 0), (2, 6, 3.0, 1),                 # breach aftermath, FLOOD through the gate hole
    (6, 7.6, 0.8, 0), (7.6, 12.4, 4.5, 1),          # swoop -> squad 34: Eren eaten
    (12.4, 13.2, 1.5, 0), (13.2, 16, 3.5, 1),       # swoop -> inner gate: Mikasa clears the wagon, the crowd floods out
    (16, 17.5, 1.2, 0), (17.5, 21, 3.0, 1),         # swoop -> supply HQ: titans around it, cadets stranded
    (21, 22.5, 0.8, 0), (22.5, 26.5, 3.5, 1),       # Mikasa falls into the street
    (26.5, 30, 3.5, 1), (30, 44, 7.0, 1),           # the rogue titan appears and kills titans
    (44, 46, 1.5, 0), (46, 54, 7.5, 1),             # HQ dash -> lift plan (cutaway)
    (54, 56.5, 1.5, 0), (56.5, 59, 2.5, 1),         # Eren out of the nape
    (59, 61.5, 1.2, 0), (61.5, 63.5, 2.5, 1),       # the cannon and the half-shift
    (63.5, 66, 2.0, 1),                             # Armin's salute (overlay hold 2.5 s after SET_K)
    (66, 68.5, 1.0, 0), (68.5, 71.5, 2.4, 1),       # swoop -> Pyxis on the wall (hold 3 s)
    (71.5, 74.5, 1.0, 0), (74.5, 79, 3.5, 1),       # swoop -> boulder: Eren shifts, red flare
    (79, 82, 2.5, 1), (82, 99, 11.0, 1),            # Armin's stab, the carry
    (99, 104, 4.0, 1), (104, 111, 5.5, 1),          # the seal + yellow flare, Levi
    (111, 113, 1.0, 0), (113, 117.5, 3.0, 1),       # swoop -> dusk pyres
    (117.5, 120.5, 2.0, 1), (120.5, 125, 3.0, 1)]   # Marco (hold 2.5 s), pull away
SEGS = [(a, b, dv * (SET_K if sp else 1.0)) for a, b, dv, sp in _SP]
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
    """Set pieces: one clear subject per beat in an open space, camera 35-80 m on a steep oblique (low, 15-45 m up,
    for wall top / squares / streets); between set pieces a quick rise-and-swoop (a high midpoint key is inserted
    when the hop is long)."""
    S = TA.STATE; C = S["C"]; st = S["site"]
    hq = st.hq
    M, A0, Q, cxy, Cp = C["M"], C["A0"], C["Q"], C["cannon_xy"], C["C_pt"]
    er, ar = C["e_roof"], C["a_roof"]
    stop, mp, sp_ = C["stop"], C["mpos"], C["shift_pt"]
    at = lambda t: np.array(S["ATD"].state(t)[0][:2])
    K = []
    def k(v, loc, tgt, lens, piece=True):
        K.append((float(v), Vector(loc), Vector(tgt), float(lens), piece))
    def kt(T, loc, tgt, lens):
        k(Vmap(T), loc, tgt, lens)
    def rel(c, dx, dy, z):
        return (float(c[0]) + dx, float(c[1]) + dy, float(z))
    ex, ey = EREN_WALL
    igx, igy = TR.INNER_GATE
    # ---- intro (video time): dawn over the town, the wall top, the Colossal, the kick
    k(0.0, (-250, -420, 170), (-40, -790, 25), 28)
    k(3.6, (-120, -720, 110), (ex, ey, 45), 34)
    k(7.2, (ex - 18, ey + 44, 82), (ex, ey, L.WALL_H + 0.8), 58)
    k(9.0, (ex - 12, ey + 52, 82), (ex + 6, ey - 8, L.WALL_H + 5), 46)
    k(11.4, (ex + 4, ey + 80, 78), (-14, GY - 14, 56), 34)
    k(13.6, (50, GY + 130, 95), (0, GY + 12, 20), 32)
    # ---- FLOOD: street level on the avenue, looking into the gate hole as the titans pour in
    kt(2.2, (38, GY + 125, 48), (0, GY + 18, 6), 30)
    kt(5.8, (34, GY + 140, 44), (-4, GY + 40, 6), 30)
    # ---- Eren eaten: squad 34's roofs, steep oblique ~55 m
    e = (er[:2] + ar[:2]) / 2
    kt(7.8, rel(e, -42, -30, er[2] + 34), rel(e, 0, 4, er[2] - 4), 36)
    kt(12.2, rel(e, -36, -22, er[2] + 30), rel(e, 0, 2, er[2] - 5), 40)
    # ---- inner gate: the wagon jam released, crowd floods out (camera south-east of the gate, low)
    kt(13.4, (igx + 48, igy - 62, 34), (igx, igy - 10, 4), 30)
    kt(15.8, (igx + 40, igy - 52, 30), (igx, igy + 6, 4), 30)
    # ---- HQ despair: from the yard side, titans ringing the building
    kt(17.7, rel(hq, -45, -80, 78), rel(hq, 0, -4, 4), 30)
    kt(20.8, rel(hq, -38, -70, 72), rel(hq, 4, 0, 4), 30)
    # ---- Mikasa falls into the street at M
    kt(22.7, rel(M, -16, 26, 58), rel(M, 0, 0, 1), 44)
    kt(26.3, rel(M, -14, 22, 54), rel(M, 2, -4, 2), 46)
    # ---- the rogue titan appears beside her and fights its way north
    kt(28.0, rel(A0, -30, 40, 66), rel(A0, 0, 0, 7), 30)
    for T in (32.0, 37.0, 42.0):
        a = at(T)
        kt(T, rel(a, -38, -40, 72), rel(a, 0, 0, 6), 30)
    # ---- lift plan: steep over the cutaway
    kt(46.4, rel(hq, -22, -14, 58), rel(hq, 0, 0, 1), 30)
    kt(53.6, rel(hq, -18, -10, 50), rel(hq, 0, 0, 1), 30)
    # ---- Eren out of the nape, the cannon and the half-shift, Armin's salute
    kt(56.7, rel(Cp, -16, 30, 58), rel(Cp, 0, 0, 3), 32)
    kt(58.8, rel(Cp, -14, 30, 54), rel(Q, 0, 0, 2), 34)
    cd = C["cdir"]; perp = np.array([cd[1], -cd[0]])
    mid = (Q + cxy) / 2
    kt(61.7, rel(mid, -6, 46, 50), rel(mid, 0, 0, 4), 32)
    kt(63.4, rel(mid, -4, 42, 46), rel(Q, 0, 0, 5), 34)
    kt(63.8, rel(Q, -8, 34, 50), rel(Q, 0, 0, 2), 46)
    kt(65.9, rel(Q, -6, 30, 47), rel(Q, 0, 0, 2), 52)
    # ---- Pyxis on the wall top above the inner gate (camera level with the wall walk, Trost side)
    sx, sy, sz = TR.WALLTOP_SPEECH
    kt(68.6, (sx + 30, sy - 40, sz + 14), (sx, sy, sz + 1), 55)
    kt(71.4, (sx + 26, sy - 36, sz + 12), (sx, sy, sz + 1), 62)
    # ---- boulder: shift by the rock (red flare), the stab, the carry down the avenue, the seal (yellow flare)
    kt(74.7, rel(sp_, 46, 40, 40), rel(sp_, 0, 0, 8), 32)
    kt(81.8, rel(sp_, 38, 34, 36), rel(sp_, 0, 0, 10), 34)
    for T in (86.0, 91.0, 96.0):
        a = at(T)
        kt(T, rel(a, 60, 40, 58), rel(a, 0, -20, 10), 30)
    kt(99.5, (45, GY + 70, 48), (0, GY + 6, 12), 30)
    kt(103.8, (40, GY + 62, 44), (0, GY + 4, 10), 30)
    # ---- Levi's entrance
    kt(104.5, rel(stop, 42, 46, 34), rel(stop, 0, 16, 8), 32)
    kt(110.8, rel(stop, 36, 40, 30), rel(stop, 0, 20, 4), 34)
    # ---- dusk pyres and Marco
    pc = np.array(TR.PLAZA[:2])
    kt(113.3, rel(pc, 60, -55, 50), rel(pc, 0, 0, 2), 30)
    kt(117.3, rel(mp, 20, -18, 22), rel(mp, 0, 0, 0), 38)
    kt(120.4, rel(mp, 17, -15, 19), rel(mp, 0, 0, 0), 44)
    kt(124.9, rel(pc, 140, -150, 140), rel(pc, 0, 10, 0), 28)
    K.sort(key=lambda e: e[0])
    out = []
    for e in K:
        if out and e[0] - out[-1][0] < 0.25:
            continue
        if out:                                            # rise-and-swoop between distant set pieces
            p_, q_ = out[-1], e
            d = (q_[1] - p_[1]).length
            if d > 160 and q_[0] - p_[0] > 0.5:
                lm = (p_[1] + q_[1]) / 2; lm.z = max(p_[1].z, q_[1].z) + min(140.0, 0.22 * d)
                out.append(((p_[0] + q_[0]) / 2, lm, (p_[2] + q_[2]) / 2, (p_[3] + q_[3]) / 2, False))
        out.append(e)
    return out

_CAM = {}
def cam_at(v):
    if not _CAM:
        ks = cam_keys(); T = [e[0] for e in ks]
        lnl = [math.log(e[3]) for e in ks]
        _CAM.update(loc=Channel(T, [e[1] for e in ks]), tgt=Channel(T, [e[2] for e in ks]), T=T, lnl=lnl, ml=_pchip_m0(T, lnl))
        for e in ks:
            print(f"[trost] key v={e[0]:.2f} T={Tmap(e[0]):.2f} loc={tuple(round(c) for c in e[1])} lens={e[3]:.0f}" + ('' if e[4] else ' swoop'))
        print("[trost] camera keys:", len(ks))
    loc, tgt = _CAM["loc"].at(v), _CAM["tgt"].at(v)
    lens = math.exp(_pchip(_CAM["T"], _CAM["lnl"], _CAM["ml"], v))
    if v < 17.0:                                   # never behind the Colossal: stay north of the outer wall
        loc.y = max(loc.y, GY + 25)
    loc.z = max(loc.z, L.height(loc.x, loc.y) + 14)
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
    night = 0.55 * (1 - ss(0.2, 3.6, v))
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
    # readable sky views: real sun shadows (bigger shadow pool, full resolution, soft), screen-space AO (fast GI)
    for k_, v_ in (("use_shadows", True), ("shadow_pool_size", "1024"), ("shadow_resolution_scale", 1.0),
                   ("shadow_ray_count", 1), ("shadow_step_count", 6), ("use_raytracing", True), ("ray_tracing_method", "SCREEN"),
                   ("use_fast_gi", True), ("fast_gi_method", "AMBIENT_OCCLUSION_ONLY"), ("fast_gi_distance", 6.0),
                   ("fast_gi_quality", 0.25), ("fast_gi_resolution", "4")):
        try:
            setattr(ev, k_, v_)
        except Exception as ex_:
            print("[trost] eevee setting", k_, "failed:", ex_)
    for o in bpy.data.objects:
        if o.type == "LIGHT" and o.data.type == "SUN":
            d = o.data
            for k_, v_ in (("use_shadow", True), ("angle", math.radians(1.2)), ("shadow_maximum_resolution", 0.02),
                           ("use_shadow_jitter", False), ("shadow_filter_radius", 1.5)):
                try:
                    setattr(d, k_, v_)
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

def hero_pop():
    """Subtle emission boost so the hero colour cues pop against the roofs: Mikasa's scarf, Armin's blond hair,
    the Scouts' green cloaks (Levi)."""
    for name, col, strength in (("ODM_scarf", (0.9, 0.05, 0.04), 1.2), ("ODM_hair_blond", (0.95, 0.75, 0.3), 0.6),
                                ("ODM_cloak_scout", (0.1, 0.45, 0.15), 0.5)):
        m = bpy.data.materials.get(name)
        if not m or not m.use_nodes:
            continue
        bs = m.node_tree.nodes.get("Principled BSDF")
        if bs:
            bs.inputs["Emission Color"].default_value = (*col, 1)
            bs.inputs["Emission Strength"].default_value = strength
hero_pop()
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

if B.dry and os.environ.get("RT_PROBE"):
    C = TA.STATE["C"]
    print("[trost] probe C:", {k: (np.round(np.asarray(v, float), 1).tolist() if isinstance(v, (tuple, list, np.ndarray)) and np.asarray(v).dtype != object and np.asarray(v).size <= 6 else type(v).__name__) for k, v in C.items()})
    for nm in ("eren", "armin", "thomas", "mikasa", "jean", "marco", "connie", "levi", "pyxis", "attack", "boulder", "w1", "w1_0"):
        row = []
        for T in (2, 5, 8, 10, 12, 14, 15.5, 17, 19, 21, 23, 25, 27, 30, 35, 40, 45, 48, 52, 57, 62, 65, 70, 76, 80, 85, 92, 100, 103, 106, 110, 116, 119):
            try:
                p_ = TA.hero_pos(nm, T)
            except Exception:
                p_ = None
            row.append(None if p_ is None else (T, *[int(round(float(c))) for c in p_]))
        print("[trost] hero", nm, [r for r in row if r])
    for k, v in sorted(TA.BEATS.items(), key=lambda e: e[1]):
        print("[trost] beat", k, v)
    sys.exit(0)
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
