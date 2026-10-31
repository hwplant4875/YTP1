"""g7 CANNON BASIN, HALF-SHIFT, SALUTE, PYXIS (SCENE_BIBLE_v2 g7, PACE 45.0 s, frame M).
Driven by aot/render_seg.py (SEG=g7 bash render_seg.sh).  Every frame is a pure function of the local time t (0..DUR).

OWNER 15:25 10/26 (binding): the basin is at its ANIME position on Wall Rose's NORTH face (trost.py block 8, mirrored
Y' = 1740 - Y): floor X 340..385 / Y 875..907 (Z -3.6), bank Y 907..919, terrace TT Y 919..927, gun bastion GB Y 875..891
(deck Z 20) with the cannon at (318, 883, 20), bell tower T_K (322, 922), Garrison building GH Y 928..948.  Seen from the
Garrison side (north, looking south at the wall and the trio) the canal, the barred water gate and the boats are on the LEFT.
No decoy corner D (owner 16:53): no titan mass, decoy soldiers or cranes there.

Contents (every time lives in BEATS below; WARP maps video time -> beat time, identity today):
  0-6 transit: the camera crosses the Rose top WEST of the basin from the g6 seam; the trio is already on the floor (Eren
  kneeling, Armin kneeling, Mikasa on guard), 48 Garrison on the plinth / flights / bank / terrace, the turntable gun swings
  40 deg onto them, the captain raises his arm (4.6), the pier-top signaller waves (5.0) - FIRE 6.0 (muzzle star, puff,
  recoil, a dark shell for 0.33 s, no white line) - Eren bites: a black arm sweeps up (6.05) and the half-shift skeleton
  erupts (6.12-6.38: torso from the floor, ribcage over the trio, right forearm curled as a shield) - IMPACT 6.35: orange
  fireball on the forearm, scorch - steam LOTS: burst to r 25 m in 1.2 s, a 12 -> 30 m column to Z 85-95 leaning east, a
  4-6 m blanket on the floor (the Garrison waist-deep) that thins by ~13 s; the Garrison crouch back, the crew reloads -
  Eren is pulled out of the nape (9.2-10.0) - Armin walks out alone, hands up (10.2-11.2) - SALUTE (11.2-14.2, fist on the
  heart) - the captain raises his arm again (13.8), PYXIS catches it (14.6) and walks down to the floor (14.6-16.4) - the
  four walk to the basket and ride it up the north face to the Rose top (16.5-20.4) - time-lapse walk west on the wall top
  (20.8-27.0) - S1 (27-30): Pyxis looks south over Trost, then they turn and sit facing north - to S2 (30-33) while square
  A fills with ~2,000 troops, 6 green banners unroll - SPEECH (33-38): deserters at the back turn round, the fist ripple
  (37.0) - deployment (38-42): the front ranks go up the north face (ODM, 2 short hooks each), the wall top fills - the
  elites leap off south over the roofs toward the Boulder Court (42-45) = seam g7 C15 = g8 K0.
Reused: odm.Squads (hook=True; thin light-grey wires), swarm845 minimal figures (square A / wall-top masses), smokecards
(steam / smoke / dust / fire / glow), trost.py (TrostCannon_K, set_basket).
"""
import math, os, random, sys, time
import numpy as np

try:
    import bpy, bmesh
    from mathutils import Vector, Matrix
except ImportError:                       # pure-python use (camera checks outside Blender)
    bpy = None

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import camchan
import segtime
import camkeys

DUR = segtime.DUR["g7"]                    # 45.0 (PACE / tight)

# ====================================================================== BEATS + WARP (the ONE re-time place)
# BEATS are on the beat clock; WARP maps the video time t (0..45) to it, piecewise linear (identity today), so a re-time is
# an edit of WARP alone.  Camera keys (camkeys.G7) and light keys are on the VIDEO clock.
WARP = [(0.0, 0.0), (DUR, DUR)]

def T_old(t):
    """video time -> beat time."""
    for (a, A), (b, B) in zip(WARP, WARP[1:]):
        if t <= b:
            return A + (B - A) * (max(t, a) - a) / (b - a)
    return t

def T_new(t):
    """beat time -> video time."""
    for (a, A), (b, B) in zip(WARP, WARP[1:]):
        if t <= B:
            return a + (b - a) * (max(t, A) - A) / (B - A)
    return t

BEATS = dict(
    transit=(0.0, 6.0), swing=(1.0, 4.5), captain_arm=(4.6, 6.0), signal=(5.0, 5.9),
    fire=6.0, black_arm=(6.05, 6.28), erupt=(6.12, 6.38), impact=6.35, recoil=(6.0, 7.6), cower=(6.4, 7.8),
    steam_burst=(6.36, 7.6), blanket=(6.5, 11.0), column=(6.4, 18.0), reload=(7.6, 10.6),
    eren_out=(9.2, 10.0), armin_out=(10.2, 11.2), salute=(11.2, 14.2), captain_arm2=(13.8, 14.6),
    pyxis_in=12.4, pyxis_catch=14.6, pyxis_down=(14.6, 16.4), to_basket=(16.5, 17.4), basket=(17.4, 20.4),
    step_off=(20.4, 20.8), walk_west=(20.8, 27.0), s1=(27.0, 30.0), sit=(29.0, 29.8), to_s2=(30.0, 33.0),
    a_fill=(30.0, 33.2), banners=(30.2, 32.0), speech=(33.0, 38.0), deserters=(33.4, 37.0), fist=37.0,
    deploy=(38.0, 42.0), climb=(38.4, 41.2), leap=(42.0, 44.9), skel_gone=(6.9, 7.5))

# ====================================================================== anchors (frame M; bible g7 CORRECTION, trost.py K)
FLOOR_Z = -3.6
EREN0 = (362.0, 888.0)                     # trio on the floor (bible (362, 852) mirrored)
MIKASA0 = (361.5, 890.6)                   # on guard between Eren and the Garrison bank (blades drawn)
ARMIN0 = (364.2, 889.4)
CANNON = (329.0, 887.5, 20.0)              # TrostCannon_K turntable centre on GB; v14 (FEEDBACK_v13 §1): moved LEFT (east, seen
                                           # from the north camera) toward the deck's NE rooftop corner (GB x 308..338, y 875..891)
AIM = 85.0                                 # compass bearing onto the trio (bible 95 deg mirrored)
SKEL_BEARING = 264.0                       # the half-shift torso faces the gun (bible 250 deg, re-aimed at the cannon)
HAND_LOCAL = (0.2, 7.4, 5.4)               # right hand of the curled forearm (local, from the floor at Eren's spot)
CAPTAIN = (361.5, 908.6)                   # on the plinth PL (X 357..367, Y 902..912, top Z -0.6)
ARMIN_SALUTE = (362.0, 899.0)
BASKET = (342.0, 879.0)                    # TrostBasket_K stop on the floor (rides to the Rose top, Z 50)
WALLTOP_Z = 50.05
S1 = (-120.0, 866.6)                       # Pyxis spot 1: south edge just east of the inner gate (talk, looking south)
S2 = (-20.0, 873.6)                        # Pyxis spot 2: north edge (speech), banners X -45..+5
A_SQ = (-20.0, 916.0, 190.0, 30.0)         # Pyxis troops (owner 10/27: no square plate -> one long rank band on the strip)
STRIP = (-190.0, 150.0, 876.0, 946.0)      # owner 10/27: long, wide ivory paving strip along the Rose north face (x0, x1, y0, y1)
B0 = (290.0, 262.0)                        # Boulder Court (the elites leap toward it)

# ====================================================================== camera (camkeys.G7: north-side re-key, owner 15:25)
CAM_KEYS = list(camkeys.G7)
_ck = camkeys.cam("g7")
CAM = camchan.CamPath(**_ck)               # v_in = A2 seam velocity, look_v_in = g6's look-at velocity, look at rest at C15
CAM_LIMITS = dict(speed=110.0, yaw=30.0, hmin=90.0)

# ====================================================================== small helpers (no bpy)
def ss(a, b, x):
    u = min(1.0, max(0.0, (x - a) / (b - a))) if b != a else float(x >= b)
    return u * u * (3 - 2 * u)

def lerp(a, b, u):
    return a + (b - a) * u

def bump(t, a, b, c, d):
    return ss(a, b, t) * (1 - ss(c, d, t))

def yaw_to(dx, dy):
    """odm / swarm heading (radians CCW from +Y) of the direction (dx, dy)."""
    return math.atan2(-dx, dy)

def heading(compass_deg):
    return -math.radians(compass_deg)

def skel_xf(p):
    """Skeleton local (x right, y forward toward the gun, z up from the floor) -> M."""
    b = math.radians(SKEL_BEARING)
    fx, fy = math.sin(b), math.cos(b)              # forward
    rx, ry = math.cos(b), -math.sin(b)             # right
    return (EREN0[0] + rx * p[0] + fx * p[1], EREN0[1] + ry * p[0] + fy * p[1], FLOOR_Z + p[2])

HAND_M = skel_xf(HAND_LOCAL)

def muzzle_M(bearing=AIM, recoil=0.0):
    b = math.radians(bearing)
    f = np.array([math.sin(b), math.cos(b), 0.0])
    return np.array(CANNON) + f * (2.65 - recoil) + np.array([0, 0, 1.05])

def cannon_bearing(t):
    return AIM - 40.0 * (1.0 - ss(*BEATS["swing"], t))

def cannon_recoil(t):
    r0, r1 = BEATS["recoil"]
    return 1.3 * ss(r0, r0 + 0.06, t) * (1.0 - ss(r0 + 0.25, r1, t))

def basket_frac(t):
    return ss(*BEATS["basket"], t)

STATE = {}

def _site():
    return STATE["site"]

def S3(x, y=None, z=0.0):
    """M -> set coords (np array)."""
    if y is None:
        p = x; x, y, z = float(p[0]), float(p[1]), float(p[2]) if len(p) > 2 else 0.0
    return np.array([x, y - segtime.SET_OFF_Y, z])

def SV(x, y=None, z=0.0):
    return Vector(S3(x, y, z))

def G(x, y):
    return _site()["ground_M"](float(x), float(y))

def GP(x, y, dz=0.05):
    """Standing point (set coords) on the ground at M (x, y)."""
    return S3(x, y, G(x, y) + dz)

def WP(x, y):
    """Standing point (set coords) on the Rose wall walk at M (x, y)."""
    return S3(x, y, WALLTOP_Z)

def say(*a):
    print("[g7]", *a, flush=True)

def _coll(name):
    c = bpy.data.collections.get(name)
    return c if c else STATE["L"].new_coll(name)

def hexrgb(h):
    h = h.lstrip("#"); c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c)

def _hide(ob, h):
    if ob is not None and (ob.hide_render != h or ob.hide_viewport != h):
        ob.hide_render = ob.hide_viewport = h

def emit_mat(name, rgb, strength):
    import flares as FX
    return FX.emit_mat(name, rgb, strength)

_RC = {}
def top_z(x, y, zmax=400.0):
    """Highest surface under M (x, y) by a scene ray cast (roofs, wall top, ground); cached."""
    key = (round(x, 1), round(y, 1))
    if key in _RC:
        return _RC[key]
    dg = bpy.context.evaluated_depsgraph_get()
    hit, loc, nrm, idx, ob, mw = bpy.context.scene.ray_cast(dg, SV(x, y, zmax), Vector((0, 0, -1)))
    z = float(loc.z) if hit else G(x, y)
    if hit and ob is not None and (ob.name.startswith("Haze") or ob.name.startswith("Sky")):
        z = G(x, y)
    _RC[key] = z
    return z

def roof_pt(x, y, search=5.0):
    """A standing spot on top of whatever is near M (x, y) (highest of 5 probes), set coords."""
    best = None
    for dx, dy in ((0, 0), (search, 0), (-search, 0), (0, search), (0, -search)):
        z = top_z(x + dx, y + dy)
        if best is None or z > best[2] + 0.5:
            best = (x + dx, y + dy, z)
    return S3(best[0], best[1], best[2] + 0.05)

def anchor_near(p0, p1, dmax=33.0, up=2.5, beyond=3.0):
    """One-hook anchor (set coords) for a hop p0 -> p1: on the far side of the landing (roof ridge / facade), a little
    above it, pulled back toward p0 if it would be more than dmax away (owner: anchors <= 35 m)."""
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    d = p1[:2] - p0[:2]; n = np.linalg.norm(d)
    a = p1 + np.array([*(d / max(n, 1e-6) * beyond), up])
    v = a - p0; L_ = np.linalg.norm(v)
    if L_ > dmax:
        a = p0 + v / L_ * dmax
    return a

# ====================================================================== the half-shift skeleton (procedural, local frame)
def _tube(bm, pts, r, seg=6, mi=0, r1=None):
    """Tube along a polyline (local coords), radius r -> r1."""
    pts = [Vector(p) for p in pts]
    n = len(pts); rings = []
    r1 = r if r1 is None else r1
    for i, p in enumerate(pts):
        t = (pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)]).normalized()
        a = Vector((0, 0, 1)) if abs(t.z) < 0.9 else Vector((1, 0, 0))
        u = t.cross(a).normalized(); v = t.cross(u).normalized()
        rr = r + (r1 - r) * i / max(1, n - 1)
        rings.append([bm.verts.new(p + (u * math.cos(k * math.tau / seg) + v * math.sin(k * math.tau / seg)) * rr) for k in range(seg)])
    for i in range(n - 1):
        for k in range(seg):
            f = bm.faces.new((rings[i][k], rings[i][(k + 1) % seg], rings[i + 1][(k + 1) % seg], rings[i + 1][k]))
            f.material_index = mi
    for ring, flip in ((rings[0], True), (rings[-1], False)):
        f = bm.faces.new(list(reversed(ring)) if flip else ring); f.material_index = mi

def _blob(bm, c, r, mi=0, seg=10, rings=6):
    """Ellipsoid (r = (rx, ry, rz)) at c."""
    m = Matrix.Diagonal((r[0], r[1], r[2], 1.0))
    res = bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=rings, radius=1.0, matrix=Matrix.Translation(c) @ m)
    for f in {f for v in res["verts"] for f in v.link_faces}:
        f.material_index = mi

def _arc(c, rx, ry, a0, a1, z, n=9, dz=0.0):
    return [(c[0] + rx * math.cos(a0 + (a1 - a0) * k / (n - 1)), c[1] + ry * math.sin(a0 + (a1 - a0) * k / (n - 1)),
             z + dz * math.sin(math.pi * k / (n - 1))) for k in range(n)]

def skeleton_bm(dark=False):
    """Torso-only half shift: 10 m from the floor, hunched 30 deg toward the gun, skull 2.2 m, ribcage 6 x 5 m arched over
    the trio, right forearm curled low across the front as a shield, left arm bones lying on the floor.  Materials:
    0 bone (gold-ivory), 1 muscle (dark red), 2 sockets / mouth, 3 teeth.  dark=True: only the right arm (the black arm)."""
    bm = bmesh.new()
    lean = math.radians(30.0)
    def sp(h):                                      # spine point at height h (along the hunched axis)
        return (0.0, -1.6 + math.sin(lean) * h, h * math.cos(lean) - 0.6)
    sh_r, sh_l = (2.9, 2.4, 6.6), (-2.9, 2.4, 6.6)
    elbow = (3.7, 5.6, 3.2); hand = HAND_LOCAL
    if dark:
        _tube(bm, [sh_r, elbow], 0.45, mi=0); _tube(bm, [elbow, hand], 0.40, mi=0, r1=0.3)
        _blob(bm, hand, (0.9, 0.9, 0.7), mi=0, seg=8, rings=5)
        return bm
    # spine (vertebrae as a chain of fat beads) + neck
    for k in range(13):
        h = 0.2 + k * 0.62
        _blob(bm, sp(h), (0.42, 0.42, 0.28), mi=0, seg=8, rings=4)
    _tube(bm, [sp(0.0), sp(8.2)], 0.2, mi=0)
    # ribcage: 7 pairs of curved ribs from the spine round to a sternum in front (6 m wide, 5 m deep)
    for k in range(7):
        h = 2.0 + k * 0.72
        c = sp(h); w = 3.0 - 0.06 * abs(k - 3) ** 1.6; d = 2.6 - 0.05 * abs(k - 3) ** 1.5
        for sx in (-1, 1):
            pts = [(c[0] + sx * w * math.sin(a), c[1] + d * (1 - math.cos(a)), c[2] - 0.9 * math.sin(a * 0.5))
                   for a in np.linspace(0.08, math.pi * 0.93, 9)]
            _tube(bm, pts, 0.17, seg=5, mi=0, r1=0.13)
    s0, s1 = sp(2.0), sp(6.3)
    _tube(bm, [(s0[0], s0[1] + 5.0, s0[2] - 0.7), (s1[0], s1[1] + 4.6, s1[2] - 0.9)], 0.24, mi=0)   # sternum
    # shoulder girdle + muscle on the shoulders / neck
    top = sp(7.6)
    for s_ in (sh_r, sh_l):
        _tube(bm, [top, s_], 0.26, mi=0)
        _blob(bm, s_, (1.1, 1.0, 0.9), mi=1, seg=8, rings=5)
    _tube(bm, [sp(7.0), sp(9.0)], 0.75, mi=1, seg=8)                       # neck muscle
    # skull 2.2 m: cranium, cheek muscle, sockets, jaw, teeth (titans keep faces)
    hc = sp(9.6); sk = (hc[0], hc[1] + 0.9, hc[2] + 0.1)
    _blob(bm, sk, (0.95, 1.15, 1.05), mi=0, seg=12, rings=7)
    for sx in (-1, 1):
        _blob(bm, (sk[0] + sx * 0.75, sk[1] + 0.1, sk[2] - 0.15), (0.35, 0.7, 0.6), mi=1, seg=8, rings=5)
        _blob(bm, (sk[0] + sx * 0.38, sk[1] + 1.0, sk[2] + 0.15), (0.24, 0.12, 0.22), mi=2, seg=8, rings=4)
    _blob(bm, (sk[0], sk[1] + 0.75, sk[2] - 0.75), (0.7, 0.55, 0.32), mi=0, seg=10, rings=5)           # jaw
    _blob(bm, (sk[0], sk[1] + 1.12, sk[2] - 0.45), (0.55, 0.08, 0.13), mi=3, seg=8, rings=4)          # teeth row
    _blob(bm, (sk[0], sk[1] + 1.14, sk[2] - 0.62), (0.5, 0.06, 0.08), mi=2, seg=8, rings=3)           # mouth gap
    # right arm curled as a shield: upper arm with muscle, forearm across the front, hand + finger bones
    _tube(bm, [sh_r, elbow], 0.32, mi=0)
    _tube(bm, [sh_r, ((sh_r[0] + elbow[0]) / 2, (sh_r[1] + elbow[1]) / 2, (sh_r[2] + elbow[2]) / 2)], 0.62, mi=1, seg=8, r1=0.48)
    for dx in (-0.18, 0.18):
        _tube(bm, [elbow, (hand[0] + dx, hand[1], hand[2])], 0.22, seg=5, mi=0)
    _blob(bm, hand, (0.7, 0.8, 0.45), mi=0, seg=8, rings=5)
    for k in range(4):
        a = -0.7 + k * 0.45
        tip = (hand[0] - 1.1 * math.cos(a), hand[1] + 1.0 + 0.4 * math.sin(a), hand[2] - 0.6)
        _tube(bm, [hand, tip], 0.11, seg=4, mi=0)
    # left arm bones lying on the floor
    le = (-4.4, 3.4, 0.35); lh = (-5.2, 7.2, 0.25)
    _tube(bm, [sh_l, le], 0.3, mi=0)
    _tube(bm, [le, lh], 0.22, seg=5, mi=0)
    _blob(bm, lh, (0.7, 0.8, 0.3), mi=0, seg=8, rings=4)
    # pelvis stub sunk in the floor + a few loose rib ends
    _blob(bm, sp(0.0), (1.8, 1.2, 0.6), mi=0, seg=10, rings=5)
    return bm

def build_skeleton(coll):
    L = STATE["L"]
    bone = L.mat("G7_Bone", hexrgb("#e6d3a8"), 0.55)
    musc = L.mat("G7_Muscle", hexrgb("#9a1f24"), 0.6)
    sock = L.mat("G7_Socket", hexrgb("#2a1414"), 0.9)
    teeth = L.mat("G7_Teeth", hexrgb("#f2ead8"), 0.5)
    black = L.mat("G7_BlackArm", hexrgb("#141012"), 0.8)
    root = bpy.data.objects.new("G7_SkelRoot", None); coll.objects.link(root)
    root.location = SV(EREN0[0], EREN0[1], FLOOR_Z)
    root.rotation_euler = (0.0, 0.0, heading(SKEL_BEARING))
    sk = L.obj_from_bm("G7_HalfShift", skeleton_bm(False), [bone, musc, sock, teeth], coll)
    sk.parent = root; sk.location = (0, 0, 0)
    da = L.obj_from_bm("G7_BlackArm", skeleton_bm(True), [black], coll)
    da.parent = root; da.location = (0, 0, 0)
    # scorch patch on the forearm after the impact
    bm = bmesh.new(); _blob(bm, HAND_LOCAL, (1.2, 1.3, 0.55), mi=0, seg=8, rings=5)
    sc = L.obj_from_bm("G7_Scorch", bm, [L.mat("G7_ScorchMat", hexrgb("#2a2420"), 0.95)], coll)
    sc.parent = root; sc.location = (0.0, -0.1, 0.12)
    for o in (sk, da, sc):
        _hide(o, True)
    STATE["skel"] = (root, sk, da, sc)

def update_skeleton(t):
    root, sk, da, sc = STATE["skel"]
    e0, e1 = BEATS["erupt"]
    b0, b1 = BEATS["black_arm"]
    gone = BEATS["skel_gone"]                                                  # owner 10/27: the temporary model goes once
    on = e0 <= t < gone[1]                                                     # the steam thickens (sinks into the blanket)
    _hide(sk, not on)
    if on:
        u = min(1.0, (t - e0) / (e1 - e0))
        back = 1.0 + 0.12 * math.sin(math.pi * u) if u < 1.0 else 1.0            # slight overshoot as it erupts
        z = max(0.03, (1 - (1 - u) ** 3) * back)
        xy = 0.45 + 0.55 * (1 - (1 - u) ** 2)
        settle = 1.0 - 0.95 * ss(gone[0], gone[1], t)                            # sinks away into the steam
        sk.scale = (xy, xy, z * settle)
    show_b = b0 <= t < b1 + 0.05
    _hide(da, not show_b)
    if show_b:
        u = min(1.0, (t - b0) / (b1 - b0))
        da.scale = (1.0, 0.35 + 0.65 * u, 0.4 + 0.6 * u)                         # the arm sweeps up and out
    _hide(sc, t < BEATS["impact"] + 0.08)

# ====================================================================== people (odm figures, hook mode)
GARRISON_HAIRS = ["dark", "brown", "ash", "black", "auburn", "grey", "brown", "dark"]

def build_people(coll):
    import odm
    rnd = random.Random(907)
    SQ = odm.Squads("G7Squads", pscale=1.0, hook=True)
    STATE["SQ"] = SQ
    face_s = yaw_to(0, -1); face_n = yaw_to(0, 1); face_e = yaw_to(1, 0); face_w = yaw_to(-1, 0)
    to_trio = lambda x, y: yaw_to(EREN0[0] - x, EREN0[1] - y)
    fire, impact = BEATS["fire"], BEATS["impact"]
    c0, c1 = BEATS["cower"]
    # ---- the trio
    er = SQ.flyer("eren", "cadet", "brown", gear=False, accent=(0.04, 0.8, 0.32))
    er.stand(0.0, BEATS["black_arm"][0], GP(*EREN0), face_w, "kneel")
    e0, e1 = BEATS["eren_out"]
    ek = (360.4, 893.4)
    n_top = S3(*skel_xf((0.0, 3.0, 9.0))); n_bot = GP(*ek)
    def nape(u):                                    # pulled out of the nape and lowered to the floor beside the ribcage
        p = n_top + (n_bot - n_top) * u
        p[2] += 2.5 * u * (1 - u)
        return p
    er.follow(e0, e1, lambda t: nape(ss(e0, e1, t)), yaw_fn=lambda t: face_n, pose="flail",
              vis_fn=lambda t: 1.0 if t >= e0 else 0.0)
    er.follow(BEATS["black_arm"][0], e0, lambda t: GP(*EREN0), yaw_fn=lambda t: face_w, pose="kneel",
              vis_fn=lambda t: 0.0)                                              # inside the nape until he is pulled out
    STATE["eren_hidden"] = (BEATS["black_arm"][0] + 0.02, e0)                    # inside the nape
    er.stand(e1, BEATS["to_basket"][0], GP(*ek), face_n, "kneel")
    mk = SQ.flyer("mikasa", "cadet", "black", scarf=True)
    mk.stand(0.0, e0 - 0.6, GP(*MIKASA0), face_n, "crouch")
    mk.hop(e0 - 0.6, e0, GP(*MIKASA0), n_top + np.array([-1.2, 0.8, 0.0]), apex=2.0, anchors=[S3(*skel_xf((0.0, 3.4, 9.6)))])
    mk.follow(e0, e1, lambda t: nape(ss(e0, e1, t)) + np.array([-1.2, 0.8, 0.0]), yaw_fn=lambda t: face_n, pose="crouch")
    mk.stand(e1, BEATS["to_basket"][0], GP(ek[0] - 1.2, ek[1] + 0.8), face_n, "stand")
    ar = SQ.flyer("armin", "cadet", "blond", H=1.63)
    a0, a1 = BEATS["armin_out"]; s0, s1 = BEATS["salute"]
    ar.stand(0.0, a0, GP(*ARMIN0), face_n, "kneel")
    ar.walk(a0, a1, GP(*ARMIN0), GP(*ARMIN_SALUTE), "wave")                      # walks out alone, hands up
    ar.stand(a1, s0, GP(*ARMIN_SALUTE), face_n, "wave")
    ar.stand(s0, s1, GP(*ARMIN_SALUTE), face_n, "salute")                         # the heart salute
    ar.stand(s1, BEATS["pyxis_down"][1], GP(*ARMIN_SALUTE), face_n, "stand")
    ar.walk(BEATS["pyxis_down"][1], BEATS["to_basket"][0], GP(*ARMIN_SALUTE), GP(ek[0] + 1.5, ek[1] + 0.5), "run")
    # ---- Pyxis (bald, moustache) + Anka + 2 riflemen: along TT from the west, down the plinth stair, to the trio
    px = SQ.flyer("pyxis", "garrison", "bald", moustache=True, H=1.68)
    ak = SQ.flyer("anka", "garrison", "dark", H=1.62)
    pr = [SQ.flyer(f"prf{k}", "garrison", h, rifle=True) for k, h in enumerate(("brown", "ash"))]
    path = [(314.0, 923.5), (356.0, 922.0), (362.5, 914.5), (362.6, 910.6)]
    pt = [BEATS["pyxis_in"], 13.7, 14.3, BEATS["pyxis_catch"]]
    for k in range(3):
        px.walk(pt[k], pt[k + 1], GP(*path[k]), GP(*path[k + 1]), "run")
    down = [(362.6, 910.6), (369.5, 912.5), (371.0, 906.0), (365.0, 896.5)]
    dt_ = [BEATS["pyxis_catch"], 15.1, 15.7, BEATS["pyxis_down"][1]]
    px.stand(dt_[0], dt_[0] + 0.3, GP(*down[0]), face_s, "wave")                  # catches the captain's raised arm
    for k in range(3):
        px.walk(max(dt_[k], dt_[0] + 0.3), dt_[k + 1], GP(*down[k]), GP(*down[k + 1]), "run")
    px.stand(dt_[-1], BEATS["to_basket"][0], GP(*down[-1]), to_trio(*down[-1]), "stand")
    for k, f in enumerate([ak] + pr):
        off = np.array([(-1.6, 1.2), (1.6, 1.4), (0.0, 2.6)][k])
        pth = [np.array(p) + off for p in path]
        for j in range(3):
            f.walk(pt[j] + 0.25, pt[j + 1] + 0.25, GP(*pth[j]), GP(*pth[j + 1]), "run")
        f.stand(pt[-1] + 0.25, DUR, GP(*pth[-1]), face_s, "rifle" if k else "stand")
    # ---- the four walk to the basket, ride it up, step onto the Rose top, time-lapse walk west, S1, S2
    b0, b1 = BEATS["basket"]
    bz = lambda t: FLOOR_Z + 0.32 + 53.6 * basket_frac(t)
    offs = {"pyxis": (-0.9, -0.9), "eren": (0.9, -0.9), "mikasa": (0.9, 0.9), "armin": (-0.9, 0.9)}
    start = {"pyxis": down[-1], "eren": ek, "mikasa": (ek[0] - 1.2, ek[1] + 0.8), "armin": (ek[0] + 1.5, ek[1] + 0.5)}
    flyers = {"pyxis": px, "eren": er, "mikasa": mk, "armin": ar}
    order = ["pyxis", "eren", "mikasa", "armin"]
    for k, nm in enumerate(order):
        f = flyers[nm]; o = offs[nm]
        bp = (BASKET[0] + o[0], BASKET[1] + o[1])
        f.walk(BEATS["to_basket"][0], b0, GP(*start[nm]), S3(bp[0], bp[1], FLOOR_Z + 0.32), "run")
        f.follow(b0, BEATS["step_off"][0], (lambda bp: lambda t: S3(bp[0], bp[1], bz(t)))(bp), yaw_fn=lambda t: face_n, pose="stand")
        top0 = (340.5 + 1.3 * k, 872.5 - 0.6 * (k % 2))
        f.walk(BEATS["step_off"][0], BEATS["step_off"][1], S3(bp[0], bp[1], bz(b1)), WP(*top0), "run")
        # west along the wall walk (between the rails), Pyxis leading
        w0, w1 = BEATS["walk_west"]
        dest = {"pyxis": (S1[0], S1[1]), "eren": (S1[0] + 2.4, 867.6), "mikasa": (S1[0] + 4.6, 869.0), "armin": (S1[0] + 3.4, 870.4)}[nm]
        f.walk(w0 + 0.12 * k, w1, WP(*top0), WP(*dest), "run")
        s0_, s1_ = BEATS["s1"]
        f.stand(w1, BEATS["sit"][0], WP(*dest), face_s, "stand")                  # looking south over Trost
        f.stand(BEATS["sit"][0], BEATS["sit"][1], WP(*dest), face_n, "stand")     # turn round ...
        f.stand(BEATS["sit"][1], s1_, WP(*dest), face_n, "kneel")                # ... and sit facing north
        d2 = {"pyxis": S2, "eren": (S2[0] + 2.6, S2[1]), "mikasa": (S2[0] + 6.0, 872.0), "armin": (S2[0] + 4.6, 870.6)}[nm]
        f.walk(BEATS["to_s2"][0] + 0.15 * k, BEATS["to_s2"][1], WP(*dest), WP(*d2), "run")
        sp0, sp1 = BEATS["speech"]
        if nm == "pyxis":
            for q in range(5):                                                     # gesturing through the speech
                f.stand(sp0 + q, sp0 + q + 0.55, WP(*d2), face_n, "wave")
                f.stand(sp0 + q + 0.55, sp0 + q + 1.0, WP(*d2), face_n, "stand")
            post = (-20.0, 866.8)                                                  # his post behind the timber railing
            f.walk(sp1, sp1 + 1.2, WP(*d2), WP(*post), "run")
            f.stand(sp1 + 1.2, DUR, WP(*post), face_s, "stand")
        elif nm == "eren":
            f.stand(sp0, BEATS["deploy"][0] + 1.0, WP(*d2), face_n, "stand")      # beside Pyxis for the speech
        else:
            f.stand(sp0, BEATS["deploy"][0] + 1.0, WP(*d2), face_n, "stand")
        if nm != "pyxis":                                                          # Eren, Mikasa, Armin join the elites
            STATE.setdefault("trio_top", {})[nm] = WP(*d2)
    # ---- captain on the plinth: arm up (4.6-6.0), again at 13.8, caught by Pyxis 14.6
    cp = SQ.flyer("captain", "garrison", "dark", moustache=True)
    ca0, ca1 = BEATS["captain_arm"]; cb0, cb1 = BEATS["captain_arm2"]
    cp.stand(0.0, ca0, GP(*CAPTAIN), face_s, "stand").stand(ca0, ca1, GP(*CAPTAIN), face_s, "wave")
    cp.stand(ca1, cb0, GP(*CAPTAIN), face_s, "stand").stand(cb0, cb1 + 0.3, GP(*CAPTAIN), face_s, "wave")
    cp.stand(cb1 + 0.3, DUR, GP(*CAPTAIN), face_s, "stand")
    # ---- the 48 Garrison (6 on PL incl. 2 riflemen kneeling at its front corners; 10 + 10 on the flights; 14 on TT;
    #      5 on the west ledge) + gun crew 4 + the pier-top signaller.  Recoil at the impact: they crouch back.
    spots = []
    spots += [((357.9, 902.9), "rifle"), ((366.1, 902.9), "rifle"), ((359.0, 906.2), "stand"), ((365.0, 906.2), "stand"),
              ((358.6, 910.6), "stand")]
    for k in range(10):                                         # west flight SW (steps down eastward, X 340..348)
        spots.append(((341.2 + (k % 3) * 2.4, 887.0 + k * 1.9), "stand"))
    for k in range(10):                                         # bank SB (Y 907..919): two staggered rows
        x = 343.5 + k * 4.1
        if 355.5 < x < 368.5:
            x += 13.5
        spots.append(((min(x, 383.0), 908.6 + (k % 2) * 2.2), "stand"))
    for k in range(14):                                         # terrace TT (Y 919..927, Z 0)
        spots.append(((326.0 + k * 4.6, 921.2 + (k % 2) * 2.6), "stand"))
    for k in range(5):                                          # the west ledge beside the flight
        spots.append(((336.6 + (k % 2) * 1.6, 893.5 + k * 2.6), "stand"))
    gar = []
    for k, ((x, y), pose) in enumerate(spots):
        f = SQ.flyer(f"gk{k}", "garrison", GARRISON_HAIRS[k % len(GARRISON_HAIRS)], rifle=(pose == "rifle"))
        yw = to_trio(x, y) + rnd.uniform(-0.15, 0.15)
        p = GP(x, y)
        if pose == "rifle":
            f.stand(0.0, DUR, p, yw, "rifle")
        else:
            back = np.array([x - EREN0[0], y - EREN0[1]]); back /= max(np.linalg.norm(back), 1e-6)
            dly = math.hypot(x - EREN0[0], y - EREN0[1]) / 120.0
            p2 = GP(x + back[0] * 0.8, y + back[1] * 0.8)
            f.stand(0.0, c0 + dly, p, yw, pose)
            f.stand(c0 + dly, c1 + dly, p2, yw, "crouch")                             # recoil from the blast / steam
            f.stand(c1 + dly, BEATS["salute"][1], p2, yw, "aim" if k % 4 == 0 else "stand")
            f.stand(BEATS["salute"][1], DUR, p2, yw, "stand")
        gar.append(f)
    crew = [(314.5, 880.0), (314.5, 886.0), (321.5, 879.0), (321.5, 887.0)]
    for k, (x, y) in enumerate(crew):
        f = SQ.flyer(f"crew{k}", "garrison", GARRISON_HAIRS[(k + 3) % 8])
        p = S3(x, y, 20.05); yw = yaw_to(math.sin(math.radians(AIM)), math.cos(math.radians(AIM)))
        f.stand(0.0, BEATS["fire"] - 0.4, p, yw, "stand").stand(BEATS["fire"] - 0.4, BEATS["fire"] + 0.6, p, yw, "crouch")
        r0, r1 = BEATS["reload"]
        f.stand(BEATS["fire"] + 0.6, r0, p, yw, "stand")
        for q in range(3):
            f.stand(r0 + q, r0 + q + 0.5, p, yw, "crouch").stand(r0 + q + 0.5, r0 + q + 1.0, p, yw, "stand")
        f.stand(r1, DUR, p, yw, "stand")
    sg = SQ.flyer("signaller", "garrison", "brown")
    p = S3(335.5, 889.0, 20.05)
    sg.stand(0.0, BEATS["signal"][0], p, face_e, "stand").stand(BEATS["signal"][0], BEATS["signal"][1], p, face_e, "wave")
    sg.stand(BEATS["signal"][1], DUR, p, face_e, "stand")
    # ---- deployment: the front of square A goes up the north face (2 short hooks each, anchors <= 35 m) onto the wall top;
    #      16 elites (Ian's, Rico's, Mitabi's squads + the trio) leap off south over the roofs (42-45)
    climbers = []
    cl0, cl1 = BEATS["climb"]
    for k in range(14):
        x = -58.0 + k * 6.4 + rnd.uniform(-1.0, 1.0)
        f = SQ.flyer(f"cl{k}", "garrison", GARRISON_HAIRS[k % 8])
        a = GP(x, 905.0); b = GP(x, 881.0)
        t0 = cl0 + 0.18 * k
        f.stand(BEATS["a_fill"][1], BEATS["deploy"][0], a, face_s, "stand")
        f.walk(BEATS["deploy"][0], t0, a, b, "run")
        mid = S3(x, 876.4, 26.0); top = WP(x + 0.8, 870.5)
        f.hop(t0, t0 + 1.1, b, mid, apex=3.0, anchors=[S3(x, 875.4, 33.0)])
        f.hop(t0 + 1.1, t0 + 2.1, mid, top, apex=4.0, anchors=[S3(x, 875.4, 51.0)])
        f.stand(t0 + 2.1, DUR, top, face_s, "stand")
        climbers.append(f)
    elites = []
    names = [("ian", "dark"), ("i1", "brown"), ("i2", "ash"), ("i3", "black"), ("rico", "grey"), ("r1", "brown"), ("r2", "dark"),
             ("r3", "auburn"), ("mitabi", "brown"), ("m1", "dark"), ("m2", "ash"), ("m3", "black"), ("e1", "brown")]
    l0, l1 = BEATS["leap"]
    for k, (nm, h) in enumerate(names):
        f = SQ.flyer(nm, "garrison", h)
        x = 8.0 + k * 4.2
        top = WP(x, 868.2)
        f.stand(BEATS["deploy"][0] + 0.5, l0 + 0.12 * k, top, face_s, "stand")
        elites.append((f, x, top))
    for nm in ("eren", "mikasa", "armin"):                       # the trio leaves Pyxis's side and joins them
        f = flyers[nm]
        x = {"eren": 2.0, "mikasa": 4.6, "armin": -0.6}[nm]
        top = WP(x, 868.6)
        f.walk(BEATS["deploy"][0] + 1.0, BEATS["deploy"][0] + 2.2, STATE["trio_top"][nm], top, "run")
        f.stand(BEATS["deploy"][0] + 2.2, l0 + 0.4, top, face_s, "stand")
        elites.append((f, x, top))
    for k, (f, x, top) in enumerate(elites):
        t0 = l0 + 0.12 * k if k < len(names) else l0 + 0.4
        gx = x + (B0[0] - x) * 0.05 + rnd.uniform(-4, 4)
        r1_ = roof_pt(gx, 852.0 - rnd.uniform(0, 3))          # the terraces at the wall foot (hook <= 35 m from the top)
        r2_ = roof_pt(gx + 6.0, 826.0 - rnd.uniform(0, 5))
        f.hop(t0, t0 + 1.05, top, r1_, apex=3.0, anchors=[anchor_near(top, r1_)])
        f.hop(t0 + 1.15, t0 + 2.1, r1_, r2_, apex=4.0, anchors=[anchor_near(r1_, r2_)])
        street = GP(gx + 9.0, 800.0)
        if t0 + 2.2 < DUR - 0.2:
            f.hop(t0 + 2.2, min(DUR - 0.12, t0 + 3.0), r2_, street, apex=3.0, anchors=[anchor_near(r2_, street)])
        f.gone(DUR - 0.1)                                         # down in the streets by the seam (g8 has its own squads)
    SQ.build(coll)
    try:                                                          # thin LIGHT-grey wires, dark hook heads (owner QA 10/27)
        wm = bpy.data.materials.new("G7_ODM_wire_grey"); wm.use_nodes = True
        b_ = wm.node_tree.nodes["Principled BSDF"]; b_.inputs["Base Color"].default_value = (*hexrgb("#b9bcc0"), 1)
        b_.inputs["Roughness"].default_value = 0.6
        SQ.wob.data.materials[0] = wm
        if getattr(SQ, "hob", None) is not None:
            hm = bpy.data.materials.new("G7_ODM_hook"); hm.use_nodes = True
            hm.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*hexrgb("#3a3c40"), 1)
            SQ.hob.data.materials[0] = hm
    except Exception as ex:
        say("wire material failed:", ex)
    say(f"flyers: {len(SQ.flyers)}")

# ====================================================================== farmland north of Rose (coordinator 10/27, ruling E3)
# Strip fields in bands along the north road (the WD_Ground palette of world.py, as round the other towns), dirt roads,
# tree lines along the roads / some field edges, a few copses.  No buildings (E3: only Pyxis's forecourt + the basin).
# A meadow pasture stays round the basin and the canal (X 150..650, Y < 1300) and a glacis along the wall (Y < 905): that
# is all g6's last frames / g7's first ones see north of the wall, so the g6 -> g7 seam stays pixel-exact.
FIELD_PAL = [(0.36, 0.33, 0.14), (0.17, 0.28, 0.06), (0.27, 0.21, 0.11), (0.44, 0.40, 0.18), (0.21, 0.31, 0.08),
             (0.30, 0.33, 0.12), (0.15, 0.25, 0.05), (0.33, 0.26, 0.13)]                       # linear rgb (world.py cols)
FARM_BOX = (-1150.0, 1150.0, 905.0, 1850.0)
ROADS_N = [([(-140, 878), (-148, 1040), (-170, 1290), (-200, 1850)], 4.0),        # the main road north from the inner gate
           ([(-1150, 1385), (-600, 1372), (-172, 1360), (420, 1378), (1150, 1395)], 3.5),   # cross road beyond the canal end
           ([(-20, 946), (-60, 1060), (-150, 1110)], 3.0),                         # strip -> main road
           ([(-160, 1660), (-600, 1610), (-1150, 1590)], 3.0), ([(-180, 1500), (300, 1560), (900, 1600)], 3.0)]

def _seg_d(px, py, P):
    best = 1e9
    for (ax, ay), (bx, by) in zip(P, P[1:]):
        dx, dy = bx - ax, by - ay; l2 = dx * dx + dy * dy
        u = 0.0 if l2 == 0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / l2))
        best = min(best, math.hypot(px - ax - u * dx, py - ay - u * dy))
    return best

def _farm_free(x, y, pad=0.0):
    if y < FARM_BOX[2] + pad or 150.0 - pad < x < 650.0 + pad and y < 1300.0 + pad:
        return False
    if STRIP[0] - pad < x < STRIP[1] + pad and STRIP[2] - pad < y < STRIP[3] + pad:      # the ivory strip (was square A)
        return False
    if abs(x - 400.0) < 25.0 + pad and y < 1340.0:
        return False
    return all(_seg_d(x, y, P) > hw + 2.5 + pad for P, hw in ROADS_N)

def build_strip(coll):
    """Owner 10/27 (Pyxis speech): no square plate - a long, wide ivory paving strip along the wall (STRIP), draped on the
    terrain over the old square A paving; the obelisk fountain of square A is removed."""
    L = STATE["L"]
    hgt = lambda x, y: float(L.height(x, y - segtime.SET_OFF_Y))
    x0, x1, y0, y1 = STRIP
    bm = bmesh.new(); step = 6.0
    nx, ny = int(math.ceil((x1 - x0) / step)), int(math.ceil((y1 - y0) / step))
    V = [[bm.verts.new((x0 + (x1 - x0) * i / nx, y0 + (y1 - y0) * j / ny - segtime.SET_OFF_Y,
                         hgt(x0 + (x1 - x0) * i / nx, y0 + (y1 - y0) * j / ny) + 0.22)) for j in range(ny + 1)] for i in range(nx + 1)]
    for i in range(nx):
        for j in range(ny):
            bm.faces.new((V[i][j], V[i + 1][j], V[i + 1][j + 1], V[i][j + 1])).material_index = (i // 2 + j // 2) % 2
    L.obj_from_bm("G7_IvoryStrip", bm, [L.mat("G7_Ivory", hexrgb("#ebe2cc"), 0.9), L.mat("G7_Ivory2", hexrgb("#e3d9c0"), 0.9)], coll)
    o = bpy.data.objects.get("TrostNorthSquare")
    if o is not None and o.type == "MESH":
        bm = bmesh.new(); bm.from_mesh(o.data); mw = o.matrix_world
        dead = [v for v in bm.verts if math.hypot((mw @ v.co).x + 20.0, (mw @ v.co).y + segtime.SET_OFF_Y - 935.0) < 7.5]
        bmesh.ops.delete(bm, geom=dead, context="VERTS"); bm.to_mesh(o.data); bm.free(); o.data.update()
    say(f"ivory strip {x1 - x0:.0f} x {y1 - y0:.0f} m, fountain removed")

def build_farmland(coll):
    L = STATE["L"]; TR = STATE["TR"]
    rnd = random.Random(1740)
    hgt = lambda x, y: float(L.height(x, y - segtime.SET_OFF_Y))
    mats = [L.mat(f"G7_Field{i}", c, 0.95) for i, c in enumerate(FIELD_PAL)] + [L.mat("G7_Dirt", hexrgb("#8b7558"), 0.95)]
    bm = bmesh.new()
    def patch(x0, x1, y0, y1, mi, dz=0.12, step=8.0):
        """A field draped on the terrain; cells on a road / the forecourt / the pasture are left out (fields hug them)."""
        nx = max(1, int(math.ceil((x1 - x0) / step))); ny = max(1, int(math.ceil((y1 - y0) / step)))
        xs = [x0 + (x1 - x0) * i / nx for i in range(nx + 1)]; ys = [y0 + (y1 - y0) * j / ny for j in range(ny + 1)]
        V = {}
        def v(i, j):
            if (i, j) not in V:
                V[(i, j)] = bm.verts.new((xs[i], ys[j] - segtime.SET_OFF_Y, hgt(xs[i], ys[j]) + dz))
            return V[(i, j)]
        made = 0
        for i in range(nx):
            for j in range(ny):
                if _farm_free((xs[i] + xs[i + 1]) / 2, (ys[j] + ys[j + 1]) / 2, 1.5):
                    bm.faces.new((v(i, j), v(i + 1, j), v(i + 1, j + 1), v(i, j + 1))).material_index = mi; made += 1
        return made
    # fields: bands along Y, strips across X, 1.6 m meadow hedge gaps
    nf = 0; edges = []
    y = FARM_BOX[2]
    while y < FARM_BOX[3]:
        bh = rnd.uniform(110.0, 175.0); x = FARM_BOX[0] + rnd.uniform(0, 40)
        while x < FARM_BOX[1]:
            w = rnd.uniform(32.0, 85.0)
            a0, a1, b0, b1 = x + 0.8, x + w - 0.8, y + 0.8, min(y + bh, FARM_BOX[3]) - 0.8
            if rnd.random() > 0.07:                                         # a few fallow gaps stay meadow
                nf += patch(a0, a1, b0, b1, rnd.randrange(len(FIELD_PAL))) > 0
            x += w
        edges.append(y)
        y += bh
    # roads (dirt ribbons, draped)
    for P, hw in ROADS_N:
        pts = []
        for (ax, ay), (bx, by) in zip(P, P[1:]):
            n = max(1, int(math.hypot(bx - ax, by - ay) / 10.0))
            pts += [(ax + (bx - ax) * k / n, ay + (by - ay) * k / n) for k in range(n)]
        pts.append(P[-1])
        rows = []
        for k, (x, y) in enumerate(pts):
            a = pts[max(k - 1, 0)]; b = pts[min(k + 1, len(pts) - 1)]
            tx, ty = b[0] - a[0], b[1] - a[1]; l = math.hypot(tx, ty) or 1.0
            nx_, ny_ = -ty / l, tx / l
            rows.append([bm.verts.new((x + nx_ * o, y + ny_ * o - segtime.SET_OFF_Y, hgt(x + nx_ * o, y + ny_ * o) + 0.2)) for o in (-hw, hw)])
        for r0, r1 in zip(rows, rows[1:]):
            bm.faces.new((r0[0], r0[1], r1[1], r1[0])).material_index = len(FIELD_PAL)
    ob = L.obj_from_bm("G7_Farmland", bm, mats, coll)
    # trees: lines along the roads, along some field edges, a few copses (the set's yard-tree variants, GN instanced)
    tc = bpy.data.collections.get("TrostYardTreeVariants")
    recs = []
    def tree(x, y, s=None):
        if y < 905.0 or (150.0 < x < 650.0 and y < 1300.0) or (STRIP[0] < x < STRIP[1] and y < STRIP[3] + 3) or (abs(x - 400) < 25 and y < 1340):
            return
        if any(_seg_d(x, y, P) < hw + 1.5 for P, hw in ROADS_N):
            return
        s = s or rnd.uniform(2.0, 3.0)                               # 9-14 m field trees (the yard variants are small)
        recs.append((x, y - segtime.SET_OFF_Y, hgt(x, y), rnd.uniform(0, 6.28), s, s, s * rnd.uniform(0.9, 1.2), rnd.randrange(6)))
    for P, hw in ROADS_N:
        for (ax, ay), (bx, by) in zip(P, P[1:]):
            L_ = math.hypot(bx - ax, by - ay); n = int(L_ / 13.0)
            nx_, ny_ = -(by - ay) / L_, (bx - ax) / L_
            for k in range(n):
                if rnd.random() < 0.3:
                    continue
                u = (k + rnd.uniform(0.2, 0.8)) / n
                for sd in (-1, 1):
                    if rnd.random() < 0.5:
                        tree(ax + (bx - ax) * u + nx_ * sd * (hw + 3.0), ay + (by - ay) * u + ny_ * sd * (hw + 3.0))
    for y in edges[1:]:
        if rnd.random() < 0.55:
            x = FARM_BOX[0]
            while x < FARM_BOX[1]:
                if rnd.random() < 0.6:
                    tree(x, y + rnd.uniform(-1, 1))
                x += rnd.uniform(11.0, 20.0)
    for k in range(16):
        cx, cy = rnd.uniform(-1100, 1100), rnd.uniform(1000, 1820)
        for q in range(rnd.randint(8, 22)):
            tree(cx + rnd.gauss(0, 14), cy + rnd.gauss(0, 10))
    if tc is not None and recs:
        tr = TR._instances("G7_FarmTrees", tc, recs)
    say(f"farmland: {nf} fields, {len(ROADS_N)} roads, {len(recs)} trees")

# ====================================================================== titans inside Trost below the Rose (bible g7 TW, no D)
class _TSite:
    def g(self, p):
        return G(p[0], p[1] + segtime.SET_OFF_Y)

TITANS_E = [   # (H, x, y, drift dx, dy, reach): milling at the inner-gate forecourt E and the AV mouth, faces toward the wall;
               # OWNER 16:53: nothing at the NW pocket D (X < -360); bible: none within 250 m of the basin (all X <= 90)
    (13.0, -160, 836, 3, -2, True), (8.0, -146, 826, -4, 3, True), (11.0, -128, 832, 2, 4, True), (5.5, -112, 840, -3, -2, True),
    (9.5, -168, 812, 5, 3, False), (6.5, -134, 808, -2, 5, False), (12.0, -110, 816, 4, 1, False), (7.0, -152, 798, 1, 4, False),
    (10.0, -92, 826, -5, 2, True), (6.0, -120, 792, 3, 3, False), (14.0, -140, 760, 2, 6, False), (8.5, -128, 720, -3, 7, False),
    (7.5, -62, 842, -4, 2, True), (9.0, -205, 836, 3, 2, True), (6.0, -228, 845, 2, -1, True), (11.5, 40, 840, -3, 2, True),
    (7.0, 72, 846, -2, 1, True), (8.0, -20, 830, 4, 3, True)]

def build_titans(coll):
    import trost_action as TA
    TT = TA.Titans(_TSite(), seed=707)
    STATE["TT"] = TT
    for k, (H, x, y, dx, dy, reach) in enumerate(TITANS_E):
        keys = [(0.0, *S3(x, y)[:2]), (DUR + 1.0, *S3(x + dx, y + dy)[:2])]
        TT.add(f"tw{k}", H=H, keys=keys, show=(-1e9, 1e9))
        TT.specs[-1]["face"] = tuple(S3(x + 0.3 * (-140 - x), 880.0)[:2])        # up at the wall / the inner gate
        if reach:
            TT.ev[-1]["lean"] = (0.5 * (k % 5),)                                   # arms up against the wall face
    TT.sim(DUR + 1.0)
    TT.build(coll)
    say(f"titans: {len(TT.specs)}")

# ====================================================================== masses (swarm845 minimal figures): square A + wall top
def build_masses(coll):
    import swarm845 as SW
    L = STATE["L"]
    rng = np.random.default_rng(935); rnd = random.Random(935)
    cx, cy, w, d = A_SQ
    # coordinator QA 10/27: 8 company blocks in loose ranks (files 1.2 m, ranks 1.5 m) with 4-12 m aisles of pale paving
    # between them and an officer 2.5 m in front of each, so the ~2,000 read as a FORMATION (not gravel); jackets
    # alternate Garrison brown / beige per block
    pts, blk = [], []
    cols_x = [(-108.0 + 23.0 * i, -90.0 + 23.0 * i) for i in range(8)]     # owner 10/27: 8 blocks side by side along the wall
    rows_y = [(902.0, 929.0)]
    for bi, (x0, x1) in enumerate(cols_x):
        for bj, (y0, y1) in enumerate(rows_y):
            b_ = bi + bj
            for y in np.arange(y0, y1 + 0.01, 1.5):
                for x in np.arange(x0, x1 + 0.01, 1.2):
                    pts.append((x + rng.normal(0, 0.07), y + rng.normal(0, 0.07))); blk.append(b_)
            pts.append(((x0 + x1) / 2, y0 - 2.5)); blk.append(100 + b_)          # officer in front (south)
    A = np.array(pts); blk = np.array(blk)
    nA = len(A)
    # wall-top Garrison (packed wall top behind Pyxis) X -80..+60, Y 866..870.5
    wt = []
    for k in range(150):
        x = rng.uniform(-82, 62)
        if abs(x - S2[0]) < 7.0:
            continue
        wt.append((x, rng.uniform(866.0, 870.4)))
    WT = np.array(wt); nW = len(WT)
    n = nA + nW
    g = SW.Geo(); fm = []
    hg = np.clip(rng.normal(1.66, 0.05, n), 1.52, 1.80)
    jacket = [hexrgb(c) for c in ("#7a4f33", "#b0855a", "#5e3b26")]          # Garrison brown / beige blocks, dark officers
    mats = [L.mat(f"G7_jacket{i}", c, 0.8) for i, c in enumerate(jacket)] + \
           [L.mat("G7_trousers", hexrgb("#d2d0cc"), 0.85), L.mat("G7_skin", hexrgb("#d8a888"), 0.6)] + \
           [L.mat(f"G7_hair{i}", hexrgb(c), 0.7) for i, c in enumerate(("#1c1814", "#3a2a1e", "#6a4a2a", "#8a6a3a", "#5a3a28"))]
    for i in range(n):
        n0 = len(g.fc)
        SW.person_geo(g, i, hg[i], False, rnd)
        if i < nA:
            jk = 2 if blk[i] >= 100 else (blk[i] + blk[i] // 2) % 2
        else:
            jk = rnd.randrange(2)
        base = [jk, 3, 4, 5 + rnd.randrange(5)]
        fm += [base[c] for c in g.fc[n0:]]
    R = g.finish()
    ob = SW._mesh("G7_Masses", R, g.f, fm, mats, coll)
    ob.visible_shadow = True
    # timing: A fills front-to-back over a_fill (time-lapse march in from the north), the fist ripple from the front
    f0, f1 = BEATS["a_fill"]
    depth = (A[:, 1] - (cy - d / 2)) / d                              # 0 = front (south, at the wall), 1 = back
    t_arr = f0 + 0.3 + depth * (f1 - f0 - 0.8) + rng.uniform(-0.25, 0.25, nA)
    t_fist = BEATS["fist"] + depth * 0.9 + rng.uniform(0, 0.15, nA)
    des = np.where(depth > 0.88)[0]
    des = rng.choice(des, size=min(14, len(des)), replace=False)      # deserters at the back
    t_wt = BEATS["a_fill"][0] + rng.uniform(0.0, 2.5, nW)
    STATE["mass"] = dict(ob=ob, R=R, A=A, nA=nA, WT=WT, nW=nW, n=n, t_arr=t_arr, t_fist=t_fist, des=des, depth=depth,
                         t_wt=t_wt, phase=rng.uniform(0, math.tau, n))
    say(f"masses: square A {nA} + wall top {nW}")

def update_masses(t):
    import swarm845 as SW
    M_ = STATE["mass"]
    n, nA = M_["n"], M_["nA"]
    pos = np.zeros((n, 3)); yw = np.full(n, math.pi); vis = np.zeros(n); mv = np.zeros(n)
    A = M_["A"]; ta = M_["t_arr"]
    # square A: march in (40 m north of the slot, 1.4 s), stand facing the wall (south)
    u = np.clip((t - ta) / 1.4, 0.0, 1.0)
    vis[:nA] = (t >= ta - 1.4).astype(float)
    pos[:nA, 0] = A[:, 0]
    pos[:nA, 1] = A[:, 1] + 40.0 * (1 - u) ** 1.5
    mv[:nA] = ((u > 0) & (u < 1)).astype(float)
    # deserters: walk off north, stop, turn round, walk back
    d0, d1 = BEATS["deserters"]
    for i in M_["des"]:
        k = (t - d0) / (d1 - d0)
        if 0.0 <= k <= 1.0:
            off = 14.0 * (min(k, 0.45) / 0.45 if k < 0.55 else max(0.0, 1.0 - (k - 0.55) / 0.45))
            pos[i, 1] += off
            yw[i] = 0.0 if k < 0.5 else math.pi
            mv[i] = 0.0 if 0.45 < k < 0.6 else 1.0
    # deployment: the block closes up toward the wall; the front ranks go up the face (fade at the wall foot)
    dp0, dp1 = BEATS["deploy"]
    sh = 14.0 * ss(dp0, dp1, t)
    pos[:nA, 1] -= sh
    gone = (A[:, 1] - sh) < 897.0
    vis[:nA] *= np.where(gone & (t > dp0), 0.0, 1.0)
    mv[:nA] = np.maximum(mv[:nA], float(dp0 < t < dp1))
    pos[:nA, 2] = 0.06
    # wall top: arrive (fade in by scale) from the a_fill start, face north
    W = M_["WT"]; nW = M_["nW"]
    pos[nA:, 0] = W[:, 0]; pos[nA:, 1] = W[:, 1]; pos[nA:, 2] = WALLTOP_Z
    yw[nA:] = 0.0
    vis[nA:] = np.clip((t - M_["t_wt"]) / 0.5, 0.0, 1.0)
    pos[:, 1] -= segtime.SET_OFF_Y
    ph = M_["phase"] + 2 * math.pi * 1.8 * t
    Ar = np.zeros((n, 7)); Ae = np.zeros((n, 7)); lean = np.zeros(n)
    s = np.sin(ph) * 0.6 * mv
    Ar[:, 1] = s; Ar[:, 2] = -s; Ar[:, 3] = -0.7 * s; Ar[:, 4] = 0.7 * s
    lean[:] = -0.12 * mv
    # the fist ripple: right fist to the heart (arm swung forward / up)
    f = np.clip((t - M_["t_fist"]) / 0.35, 0.0, 1.0) * (1.0 - ss(BEATS["deploy"][0] - 0.4, BEATS["deploy"][0] + 0.4, t))
    Ar[:nA, 4] += 1.25 * f
    co = SW._deform(M_["R"], Ar, Ae, lean, vis, yw, pos)
    ob = M_["ob"]
    ob.data.vertices.foreach_set("co", co.astype(np.float32).ravel()); ob.data.update()

# ====================================================================== props: banners, shell, flash lights
def build_props(coll):
    L = STATE["L"]
    green = L.mat("G7_Banner", hexrgb("#2f5d3a"), 0.85)
    pale = L.mat("G7_BannerEmblem", hexrgb("#d8cfb4"), 0.8)
    pole = L.mat("G7_Pole", hexrgb("#4a3427"), 0.8)
    bans = []
    for k in range(6):
        x = -45.0 + k * 10.0
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation((0, 0, -5.0)) @ Matrix.Diagonal((3.2, 0.12, 10.0, 1.0)))
        for f in bm.faces:
            f.material_index = 0
        bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation((0, 0.08, -2.6)) @ Matrix.Diagonal((1.4, 0.06, 1.8, 1.0)))
        for f in bm.faces[6:]:
            f.material_index = 1
        bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation((0, 0, 0.2)) @ Matrix.Diagonal((4.0, 0.2, 0.2, 1.0)))
        for f in bm.faces[12:]:
            f.material_index = 2
        ob = L.obj_from_bm(f"G7_Banner{k}", bm, [green, pale, pole], coll)
        ob.location = SV(x, 876.0, 50.6)                         # just proud of the north-face panels (Y 875.55)
        bans.append(ob)
    STATE["banners"] = bans
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=8, v_segments=5, radius=0.32)
    STATE["shell"] = L.obj_from_bm("G7_Shell", bm, [L.mat("G7_ShellMat", hexrgb("#1a1a1a"), 0.5)], coll)
    _hide(STATE["shell"], True)
    lights = []
    for nm, col in (("G7_MuzzleLight", (1.0, 0.75, 0.4)), ("G7_FireLight", (1.0, 0.55, 0.22))):
        ld = bpy.data.lights.new(nm, "POINT"); ld.color = col; ld.energy = 0.0
        for k_, v_ in (("shadow_soft_size", 2.0), ("use_shadow", False)):   # no shadow: 1-sample Eevee shadows speckle
            try:
                setattr(ld, k_, v_)
            except Exception:
                pass
        lo = bpy.data.objects.new(nm, ld); coll.objects.link(lo)
        lights.append((lo, ld))
    STATE["lights"] = lights
    lights[0][0].location = Vector(S3(muzzle_M()) + np.array([0, 0, 1.5]))
    lights[1][0].location = Vector(S3(HAND_M) + np.array([0, 0, 3.0]))

def update_props(t):
    f0, f1 = BEATS["banners"]
    for k, ob in enumerate(STATE["banners"]):
        u = ss(f0 + 0.2 * k, f1 + 0.2 * k, t)
        _hide(ob, u <= 0.01)
        ob.scale = (1.0, 1.0, max(0.02, u))
    # the shell: muzzle -> impact in 0.33 s, a dark dot (no tracer line)
    sh = STATE["shell"]
    tf, ti = BEATS["fire"] + 0.02, BEATS["impact"]
    on = tf <= t < ti
    _hide(sh, not on)
    if on:
        u = (t - tf) / (ti - tf)
        a = muzzle_M(); b = np.array(HAND_M) + np.array([0.0, 0.0, 0.6])
        p = a + (b - a) * u; p[2] += 2.0 * u * (1 - u)
        sh.location = Vector(S3(p))
    (lm, ldm), (lf, ldf) = STATE["lights"]          # kept at 0: an Eevee point light cuts a hard disc on the wall;
                                                    # the emissive glow / fire cards carry the flashes
    ldm.energy = 0.0 * bump(t, BEATS["fire"] - 0.01, BEATS["fire"] + 0.02, BEATS["fire"] + 0.06, BEATS["fire"] + 0.2)
    ti = BEATS["impact"]
    ldf.energy = 0.0 * bump(t, ti - 0.01, ti + 0.05, ti + 0.25, ti + 1.1)
    # the cannon: turntable swing onto the trio, recoil at the shot
    cn = STATE.get("cannon")
    if cn is not None:
        b = cannon_bearing(t); r = cannon_recoil(t)
        br = math.radians(b)
        cn.location = SV(CANNON[0] - math.sin(br) * r, CANNON[1] - math.cos(br) * r, CANNON[2])
        cn.rotation_euler = (0.0, 0.0, heading(b))
    TR = STATE["TR"]
    if hasattr(TR, "set_basket"):
        TR.set_basket(basket_frac(t))

# ====================================================================== FX cards
def build_cards(coll):
    import smokecards as SC
    rng = np.random.default_rng(77)
    C = SC.SmokeCards("G7Cards")
    W = np.array([2.0, 0.3, 0.0])                                     # wind: the column leans ~10 deg east
    tf, ti = BEATS["fire"], BEATS["impact"]
    mz = S3(muzzle_M())
    # muzzle star (glow) + powder puff
    C.add_many([tf, tf + 0.03], np.tile(mz, (2, 1)), None, r0=2.6, r1=3.4, life=0.14, rise=0.0, kind="glow", alpha=1.0,
               color=hexrgb("#ffc040"), fade_in=0.005)
    b = math.radians(AIM); fw = np.array([math.sin(b), math.cos(b), 0.0])
    n = 14
    C.add_many(tf + rng.random(n) * 0.15, np.tile(mz, (n, 1)) + rng.normal(0, 0.5, (n, 3)),
               fw * rng.uniform(4, 12, (n, 1)) + np.column_stack([rng.normal(0, 1.5, n), rng.normal(0, 1.5, n), rng.uniform(0.5, 2.5, n)]),
               r0=1.0, r1=rng.uniform(3.5, 5.5, n), life=rng.uniform(2.2, 3.4, n), rise=1.2, kind="smoke", alpha=0.6, tau=0.5,
               color=(0.62, 0.58, 0.50))
    # ignition: yellow flicker + dust ring on the floor
    c = S3(EREN0[0], EREN0[1], FLOOR_Z + 0.6)
    C.add_many([BEATS["black_arm"][0], BEATS["black_arm"][0] + 0.07], np.tile(c + np.array([0, 0, 3.0]), (2, 1)), None, r0=4.0, r1=5.0,
               life=0.12, rise=0.0, kind="glow", alpha=0.9, color=hexrgb("#ffe08a"), fade_in=0.005)
    n = 30; a = np.linspace(0, math.tau, n, endpoint=False)
    C.add_many(BEATS["erupt"][0] + rng.random(n) * 0.15, np.tile(c, (n, 1)) + np.column_stack([np.cos(a) * 2, np.sin(a) * 2, np.zeros(n)]),
               np.column_stack([np.cos(a) * 14, np.sin(a) * 14, rng.uniform(0.5, 2, n)]), r0=1.5, r1=rng.uniform(3.5, 5.0, n),
               life=rng.uniform(1.4, 2.0, n), rise=0.5, kind="dust", alpha=0.6, tau=0.4, color=hexrgb("#a89878"))
    # IMPACT fireball on the forearm (orange, r 6-8 m) + flash
    h = S3(HAND_M)
    C.add_many([ti], [h + np.array([0, 0, 1.0])], None, r0=7.0, r1=9.0, life=0.22, rise=0.0, kind="glow", alpha=1.0,
               color=(1.0, 0.72, 0.38), fade_in=0.005)
    n = 26
    C.add_many(ti + rng.random(n) * 0.12, np.tile(h, (n, 1)) + rng.normal(0, 1.2, (n, 3)),
               np.column_stack([rng.normal(0, 6, n), rng.normal(0, 6, n), rng.uniform(1, 7, n)]), r0=2.5, r1=rng.uniform(5.5, 8.0, n),
               life=rng.uniform(0.5, 0.9, n), rise=2.0, kind="fire", alpha=1.0, tau=0.3, color=hexrgb("#ff8a2a"))
    n = 16
    C.add_many(ti + 0.3 + rng.random(n) * 0.5, np.tile(h, (n, 1)) + rng.normal(0, 1.5, (n, 3)),
               np.column_stack([rng.normal(0, 2, n), rng.normal(0, 2, n), rng.uniform(4, 9, n)]), r0=3.0, r1=rng.uniform(6, 9, n),
               life=rng.uniform(2.5, 3.5, n), rise=3.0, kind="smoke", alpha=0.55, tau=0.6, color=(0.20, 0.17, 0.15))
    # steam LOTS: burst to r 25 m in 1.2 s
    sc = S3(*skel_xf((0.0, 1.5, 4.0)))
    n = 140; th = rng.uniform(0, math.tau, n)
    sp = rng.uniform(16, 30, n)
    C.add_many(BEATS["steam_burst"][0] + rng.random(n) * 0.5, np.tile(sc, (n, 1)) + rng.normal(0, 1.5, (n, 3)),
               np.column_stack([np.cos(th) * sp, np.sin(th) * sp, rng.uniform(1, 12, n)]), r0=4.0, r1=rng.uniform(12, 18, n),
               life=rng.uniform(4.5, 7.0, n), rise=2.5, kind="steam", alpha=0.8, tau=0.7)
    # blanket 4-6 m deep on the floor (the Garrison waist-deep), thinning by ~13 s
    b0, b1 = BEATS["blanket"]
    ts = np.arange(b0, b1, 0.04); n = len(ts)
    r = 24.0 * np.sqrt(rng.random(n)); th = rng.uniform(0, math.tau, n)
    P = np.column_stack([EREN0[0] + 1.5 + np.cos(th) * r, EREN0[1] + 6.0 + np.sin(th) * r * 0.85, np.full(n, FLOOR_Z + 1.6)])
    P[:, 1] = np.clip(P[:, 1], 876.0, 921.0)
    P = np.array([S3(*p) for p in P]) + np.column_stack([np.zeros(n), np.zeros(n), rng.uniform(0, 2.0, n)])
    C.add_many(ts, P, np.column_stack([rng.normal(0, 1.5, n), rng.normal(0, 1.5, n), rng.uniform(0.0, 0.6, n)]), r0=6.0,
               r1=rng.uniform(10.0, 14.0, n), life=rng.uniform(3.4, 5.0, n), rise=0.5, kind="steam", alpha=0.6, tau=1.5)
    # the column 12 -> 30 m wide to Z 85-95, leaning east; dense to 11 s, thinning to 18 s, a thin column to the end
    for (a_, b_, dt, al, r1) in ((BEATS["column"][0], 11.0, 0.05, 0.6, (12, 18)), (11.0, BEATS["column"][1], 0.09, 0.42, (12, 17)),
                                 (BEATS["column"][1], DUR, 0.18, 0.28, (9, 13))):
        ts = np.arange(a_, b_, dt); n = len(ts)
        base = sc + np.array([0, 0, 2.0])
        P = np.tile(base, (n, 1)) + np.column_stack([rng.normal(0, 2.5, n), rng.normal(0, 2.5, n), rng.uniform(0, 3, n)])
        V = np.column_stack([rng.normal(0, 0.8, n), rng.normal(0, 0.8, n), rng.uniform(11.5, 14.5, n)]) + W
        C.add_many(ts, P, V, r0=4.5, r1=rng.uniform(*r1, n), life=rng.uniform(6.0, 7.0, n), rise=0.8, kind="steam", alpha=al, tau=0.0)
    # wisps off the bones (pure in t)
    ts = np.arange(BEATS["impact"] + 0.5, DUR, 0.12); n = len(ts)
    pts = [skel_xf((rng.uniform(-3, 3), rng.uniform(-1.5, 4.5), rng.uniform(2.0, 9.0))) for _ in range(n)]
    C.add_many(ts, np.array([S3(*p) for p in pts]), np.column_stack([rng.normal(0, 0.8, n), rng.normal(0, 0.8, n), rng.uniform(2, 4, n)]),
               r0=0.8, r1=rng.uniform(2.5, 4.0, n), life=rng.uniform(1.6, 2.6, n), rise=2.5, kind="steam", alpha=0.4, tau=0.8)
    # ambient: town smoke columns (Trost, south of the wall) + thin steam over the HQ corpses (g6 continuity)
    for k in range(9):
        x, y = rng.uniform(-360, 330), rng.uniform(160, 780)
        base = S3(x, y, top_z(x, y) + 2.0); ts = np.arange(0.0, DUR, 0.5); n = len(ts)
        C.add_many(ts - 14.0, np.tile(base, (n, 1)) + rng.normal(0, 2, (n, 3)),
                   np.column_stack([rng.normal(0, 0.6, n), rng.normal(0, 0.6, n), rng.uniform(8, 11, n)]) + W * 0.5,
                   r0=3.0, r1=rng.uniform(12, 18, n), life=15.0, rise=0.8, kind="smoke", alpha=0.32, tau=4.0, color=(0.30, 0.27, 0.24))
    for (x, y) in ((-178.0, 619.0), (-205.0, 600.0)):
        base = S3(x, y, 2.0); ts = np.arange(0.0, DUR, 0.4); n = len(ts)
        C.add_many(ts - 8.0, np.tile(base, (n, 1)) + rng.normal(0, 1.5, (n, 3)),
                   np.column_stack([rng.normal(0, 0.5, n), rng.normal(0, 0.5, n), rng.uniform(6, 8, n)]) + W * 0.4,
                   r0=1.5, r1=rng.uniform(5, 8, n), life=9.0, rise=1.0, kind="steam", alpha=0.25, tau=3.0)
    C.build(coll)
    STATE["cards"] = C
    say(f"smoke cards: {C.count()}")

# ====================================================================== build / update
def build(site):
    t0 = time.time()
    STATE["site"] = site; STATE["TR"] = site["TR"]; STATE["L"] = site["L"]
    coll = _coll("G7")
    bpy.context.view_layer.update()
    STATE["cannon"] = bpy.data.objects.get("TrostCannon_K")
    if STATE["cannon"] is None:
        say("WARNING: TrostCannon_K missing")
    TR = site["TR"]
    for fn, args in (("set_breach", (True,)), ("set_glow", (0.0,))):           # after the kick (g5); glow ramps g6 0 -> g8 1
        try:
            getattr(TR, fn)(*args)
        except Exception as ex:
            say(fn, "failed:", ex)
    rub = bpy.data.objects.get("OuterGateRubble")                                # g8 flattens the kick's rubble fan (x 0.45)
    if rub is not None:
        rub.scale.z *= 0.45
    try:                                   # g8's own titans at their t = 0 poses (court + gate square): no pop at the seam
        import seg_g8 as S8
        S8.STATE.update(site=site, TR=TR, L=site["L"])
        S8.build_titans(coll)
        STATE["TT8"] = S8.STATE["TT"]
        STATE["TT8"].update(0.0)
    except Exception as ex:
        import traceback; traceback.print_exc()
        say("g8 titans failed:", ex)
    build_farmland(coll)
    build_strip(coll)
    build_skeleton(coll)
    build_titans(coll)
    build_people(coll)
    build_masses(coll)
    build_props(coll)
    build_cards(coll)
    _light_capture()
    say(f"build {time.time() - t0:.1f}s")

def finish():
    pass

def update(tv):
    t = T_old(float(tv))
    update_skeleton(t)
    update_props(t)
    STATE["TT"].update(t)
    STATE["SQ"].update(t)
    try:
        STATE["TR"].set_glow(ss(22.0, 40.0, t))                                 # breach glow: g6 ends at 0, g8 starts at 1
    except Exception:
        pass
    update_masses(t)
    STATE["cards"].update(t, wind=(2.0, 0.3))

# ---------------------------------------------------------------------- light: g6 H8 (warm gold, el 27) -> g8 K0 (el 12, az 255)
# t: sun elevation, compass azimuth, energy, sun rgb, zenith rgb, horizon rgb, world (lighting) strength
# The basin is on the NORTH face: at the g6/g8 azimuth (250-255) the wall would shade the whole floor, so the sun walks on to
# ~268 (grazing the north face from the west, the floor lit) while the camera crosses the wall, then back to g8's 255 / 12
# while the view turns west along the wall top (23-45 s), where the shadows read least.
LIGHT_KEYS = [
    (0.0,  27.0, 250, 2.8, (1.00, 0.84, 0.62), (0.18, 0.31, 0.60), (0.86, 0.76, 0.62), 0.92),   # = g6 69.5
    (6.0,  26.0, 267, 2.9, (1.00, 0.84, 0.61), (0.18, 0.32, 0.61), (0.87, 0.76, 0.61), 0.93),
    (17.0, 23.5, 268, 3.0, (1.00, 0.83, 0.60), (0.19, 0.32, 0.62), (0.89, 0.77, 0.60), 0.95),
    (45.0, 12.0, 255, 3.4, (1.00, 0.80, 0.56), (0.20, 0.35, 0.68), (0.96, 0.78, 0.55), 1.00),   # = g8 0.0
]
GRADE_KEYS = [
    (0.0,  (1.04, 0.98, 0.89), -0.08),          # = g6 69.5
    (45.0, (1.06, 0.98, 0.86), 0.00),           # = g8 0.0
]

def _keyed(K, t):
    if t <= K[0][0]: return K[0], K[0], 0.0
    for a, b in zip(K, K[1:]):
        if a[0] <= t < b[0]:
            return a, b, ss(a[0], b[0], t)
    return K[-1], K[-1], 0.0

def _light_capture():
    sc = bpy.context.scene
    suns = [o for o in bpy.data.objects if o.type == "LIGHT" and o.data.type == "SUN"]
    w = sc.world
    nodes = w.node_tree.nodes if (w and w.use_nodes) else []
    STATE["light0"] = dict(suns=suns, exp0=sc.view_settings.exposure,
                           ramps=[n for n in nodes if n.type == "VALTORGB"], skies=[n for n in nodes if n.type == "TEX_SKY"],
                           bgs=[(n, n.inputs[1].default_value) for n in nodes if n.type == "BACKGROUND"])

def light(tv):
    t = float(tv)                                         # light keys are on the video clock
    a, b, u = _keyed(LIGHT_KEYS, t)
    def mix(i):
        x, y = a[i], b[i]
        if isinstance(x, tuple):
            return tuple(lerp(p, q, u) for p, q in zip(x, y))
        return lerp(x, y, u)
    def sdir(k):
        el, az = math.radians(k[1]), math.radians(k[2])
        return np.array([math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el)])
    d = sdir(a) * (1 - u) + sdir(b) * u; d /= np.linalg.norm(d)
    L0 = STATE["light0"]
    en = mix(3); col = mix(4); zen = mix(5); hor = mix(6); ws = mix(7)
    for o in L0["suns"]:
        o.rotation_euler = Vector(tuple(-d)).to_track_quat("-Z", "Y").to_euler()
        o.data.energy = en; o.data.color = col
    for r in L0["ramps"]:
        el = r.color_ramp.elements
        el[0].color = (*hor, 1); el[-1].color = (*zen, 1)
    for s in L0["skies"]:
        try:
            s.sun_elevation = math.radians(mix(1)); s.sun_rotation = math.atan2(d[1], d[0])
        except Exception:
            pass
    for n, s0 in L0["bgs"]:
        n.inputs[1].default_value = s0 * ws
    ga, gb, gu = _keyed(GRADE_KEYS, t)
    gain = tuple(lerp(p, q, gu) for p, q in zip(ga[1], gb[1])); gex = lerp(ga[2], gb[2], gu)
    vs = bpy.context.scene.view_settings
    vs.exposure = L0["exp0"] + gex
    try:
        vs.use_curve_mapping = True
        cm = vs.curve_mapping
        cm.white_level = tuple(1.0 / max(g, 1e-3) for g in gain)
        cm.black_level = (0.0, 0.0, 0.0)
        cm.update()
    except Exception as ex_:
        if not STATE.get("grade_warned"):
            say("colour grade failed:", ex_); STATE["grade_warned"] = True

def cam_shake(tv):
    """A tiny shake at the impact (0.2 deg, 0.3 s): the fireball is the beat's only bang."""
    u = tv - T_new(BEATS["impact"])
    if u < 0.0 or u > 0.3:
        return 0.0, 0.0
    a = math.radians(0.2) * (1 - u / 0.3) ** 2
    return a * math.sin(u * 2 * math.pi * 13.0), a * 0.6 * math.sin(u * 2 * math.pi * 10.0 + 1.1)

# ====================================================================== HUD trackers (M) + self checks
def _p_set_to_M(p):
    return (float(p[0]), float(p[1]) + segtime.SET_OFF_Y, float(p[2]))

def _sq(name, t0=-1e9, t1=1e9):
    def f(tv):
        t = T_old(tv)
        if not (t0 <= t < t1): return None
        st = STATE["SQ"].state(name, t)
        return _p_set_to_M(st["pos"] + np.array([0, 0, 2.0])) if st["vis"] > 0 else None
    return f

TRACK = {"EREN": _sq("eren", 0.0, 44.0), "MIKASA": _sq("mikasa", 0.0, 44.0), "ARMIN": _sq("armin", 0.0, 44.0),
         "PYXIS": _sq("pyxis", BEATS["pyxis_in"], DUR)}

def check():
    """Basin handedness from the FIRE key (canal on the LEFT), the anchor rule, the seams."""
    c, l, _ = CAM.eval(BEATS["fire"])
    d = np.array(l) - np.array(c); d[2] = 0; d /= np.linalg.norm(d)
    right = np.array([d[1], -d[0], 0.0])
    gate = np.array([402.0, 875.0, 0.0]) - np.array(c)
    say("handedness at FIRE: water gate is on the", "LEFT (ok)" if np.dot(gate, right) < 0 else "RIGHT (WRONG)")
    s_in, s_out = segtime.seam("g6_g7"), segtime.seam("g7_g8")
    for nm, tt, s in (("in", 0.0, s_in), ("out", DUR, s_out)):
        p, lk, ln = CAM.eval(tt)
        say(f"seam {nm}: pos err {np.linalg.norm(np.array(p) - np.array(s['pos'])):.3f} m, look err "
            f"{np.linalg.norm(np.array(lk) - np.array(s['look'])):.3f} m, lens {ln:.2f} vs {s['lens']}")
    v = CAM.vel(DUR - 1e-3); say(f"exit velocity {np.round(v, 2)} vs seam {s_out['vel']}")
    SQ = STATE.get("SQ")
    if SQ is not None:
        worst = 0.0
        for f in SQ.flyers:
            for s in f.seg:
                if s[0] == "hop" and s[7]:
                    worst = max(worst, float(np.linalg.norm(np.asarray(s[7][0]) - s[3])))
        say(f"longest hook (anchor distance from the take-off): {worst:.1f} m (owner <= 35)")

if __name__ == "__main__":
    camchan.check(CAM, 0.0, DUR, limits=dict(name="g7 CAM", **CAM_LIMITS))
