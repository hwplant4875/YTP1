"""g6 SUPPLY HQ, LIFT OPERATION, EREN EMERGES (SCENE_BIBLE_v2 g6, TIGHT 69.5 s, frame M).
Driven by aot/render_seg.py (SEG=g6 bash render_seg.sh).  Every frame is a pure function of the local time t (0..DUR).

Layout (integrator ruling, checked against ref/anime/bible/ep08_000014937.jpg and ref/user/trost_hq_warehouse_wing_ref.png):
keep HK at the WEST end (-250, 640), warehouse wing HW to the EAST (X -234..-136), plaza apron SOUTH of the wing.  Seen
from the plaza (camera south / south-east, looking north-west) the keep is on the LEFT and the wing runs off to the RIGHT,
as in the owner's wing ref; the Attack Titan collapses along the wing base with his legs toward the keep (west), head east.

Contents (bible g6 choreography, tight column; every time lives in BEATS / AT_KEYS / LIGHT_KEYS / camkeys.G6):
  0-6.6 the Attack Titan (AT) walks out of Q2 up the N-S street exactly where g5 left him ((-231, 531), heading 349 deg,
  6 m/s), breaks into a run, punches the street titan ST1 aside (2.6) - F0/F1 climb the keep's south face and step onto the
  tier-1 roof walk, peering into the hall hole - Jean's squad (8) hops from the south roofs to the keep (Jean lands on the
  roof walk 2.6) and crashes the tall hall windows (3.5 / 4.0, glints); the other stranded cadets follow in by ~8 -
  6.8-7.9 the AT roars at the plaza edge - 9.9 leap up the keep face, 10.9 punch, 11.0-11.9 TACKLE: both roof-walk titans
  carried 30 m ESE onto the apron (dust, shake) - Armin / Mikasa / Connie cross from roof R and crash a window, gas thin
  (12.5) - rampage: stomps 12.6 / 13.8, head-off punch 15.85, roar 16.6, uppercut 18.45, slam 24.0 - CUTAWAY 17-19: the 36 m
  bay dithers away (shadow proxy keeps the sun out, warm torch lights inside) - cage down Z 10 -> 2.8 (19.5-22.5), 7
  titans of 3-4 m shuffle into a 4.5 m ring (22.5-27.4) - VOLLEY 27.5 (28 flashes, light spike, powder smoke, titans blinded)
  - 7 cutters drop from the rafters 27.8-28.8, Sasha and Connie miss, Mikasa and Annie finish 30.3 / 30.7 - swarm on the
  plaza 31.2-35.0 (3 biters thrown / stomped), roof returns 33.5-35.5, breakout of 12 through the west arched door 34.0 onto
  the wing roof - the BLOND titan spotted, charged, nape bitten 36.9-37.9 and thrown onto F5 38.9 - roar 40.8-41.8 - lunge 42, face-down fall 42.8,
  skid 10 m east 43.6-45 in a beige dust bow wave - steam white-out 45-48.5 - Eren rises out of the nape 48.5-50.5 - Mikasa
  runs down the slate roof and drops in 50.5-52.4, kneels by him - tableau on the keep roof walk 55.5-59.5 (Mikasa carries
  Eren up; Armin kneels; Jean, Reiner, Bertolt, Annie stand) - exit east to the basin 59.5-69.5 (g6 H8 = g7 C0).
Reused: attack_titan (asset + blended poses, as seg_g5), trost_action.Titans (pure titans, subclassed), odm.Squads (one-hook
ODM people), smokecards (steam / dust / smoke / glow cards), trost.py HQ hooks (set_hq_cutaway, set_hq_lift), toon.
Placeholders built here: G6_* (point lights only).
"""
import math, os, random, sys, time
import numpy as np

try:
    import bpy
    from mathutils import Vector, Matrix
except ImportError:                       # pure-python use (camera / timing checks outside Blender)
    bpy = None

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import camchan
import camkeys
import segtime

DUR = segtime.DUR["g6"]                    # 69.5 (tight)

# ====================================================================== WARP + BEATS (the ONE re-time place)
# BEATS are on the CHOREOGRAPHY clock.  WARP maps the segment's video time t (0..DUR) to that clock, piecewise linear, so a
# re-time is an edit of WARP alone (e.g. [(0, 0), (19.5, 17.0), ...] plays the approach faster).  Camera keys (camkeys.G6),
# light keys and the cam shakes are on the VIDEO clock.  Identity today.
WARP = [(0.0, 0.0), (DUR, DUR)]

def T_old(t):
    """video time -> choreography time."""
    for (a, A), (b, B) in zip(WARP, WARP[1:]):
        if t <= b:
            return A + (B - A) * (max(t, a) - a) / (b - a)
    return t

def T_new(t):
    """choreography time -> video time."""
    for (a, A), (b, B) in zip(WARP, WARP[1:]):
        if t <= B:
            return a + (b - a) * (max(t, A) - A) / (B - A)
    return t

BEATS = dict(
    street_punch=2.6, st1_kill=2.75, climb=(0.8, 7.0), jean_land=2.6, crash=(4.4, 5.0), stragglers=(4.0, 8.0),
    look_roar=(6.9, 7.9), leap=(9.9, 10.7), hq_punch=10.9, tackle=(11.0, 11.9), trio=(4.0, 13.4),
    r1_kill=12.6, r2_kill=13.8, f2_kill=15.85, roar2=(16.5, 17.5), f3_kill=18.45, w1_kill=24.05,
    cut_open=(17.6, 18.8), lift=(19.5, 22.5), ring=(22.5, 27.4), volley=27.5, drop=(27.8, 28.8),
    misses=(28.8, 29.6), finish=(30.3, 30.7), cut_close=(34.0, 35.2), inside_gone=35.6,
    swarm=(31.2, 35.0), biter_kills=(32.6, 33.8, 35.0), breakout=34.0, wing_roof=(35.6, 37.6),
    brd_in=(27.0, 35.6), spot=(35.5, 36.0), charge=(36.0, 36.9), brd_bite=(36.9, 37.9), throw=(37.9, 38.7), brd_hit=38.9,
    brd_kill=38.9, roar3=(40.8, 41.8), lunge=(42.0, 42.8), fall=(42.8, 43.6), skid=(43.6, 45.0), whiteout=(45.0, 48.5),
    eren_rise=(48.5, 50.5), mikasa_run=(50.5, 51.2), mikasa_drop=(51.2, 52.4), hug=52.6,
    tableau=(55.5, 59.5), carry_up=(54.0, 59.3), exit=(59.5, 69.5))

# ====================================================================== anchors (frame M; bible g6 + trost.py block 7)
HQ = (-250.0, 640.0)                       # keep centre; tier 1 X -266..-234, Y 624..656, roof walk Z 28; tier 2 S face Y 634
HOLE = (-251.0, 634.0, 31.0)               # hall hole in tier 2's south face
LIFT_C = (-187.0, 641.0)                   # cage / shaft centre; cage floor Z 10 -> 2.8
CAGE_Z = (10.0, 2.8)
BAY = (-205.0, -169.0, 631.0, 651.0)       # storeroom HS
RAFTERS_X = [-199.0, -193.0, -187.0, -181.0, -175.0]   # tie beams N-S at Z 6.0 (top 6.25)
DOOR = (-208.2, 627.0)                     # the large arched doorway at the bay's west end (breakout)
ROOF_R = (-258.0, 505.0, 25.0)             # g5's end: Armin, Mikasa, Connie on the ridge of roof R
ST1_POS = (-231.0, 563.0)
CC_POS = (-221.5, 514.5); CC_KILL = 66.8 - 70.0      # g5's CC corpse (fight #2 in Q2), killed 3.2 s before g6 starts
EREN_NAPE = (-178.0, 619.0)                # bible: the prone body's nape (trost ANCHORS_M EREN_NAPE)
TERRACE = (-270.0, -230.0, 612.0, 624.0, 2.5)
WALK_Z = 28.0                              # keep tier-1 roof walk
SEAM5 = dict(pos=(-231.0, 531.0), heading=349.0, v=6.0)   # g5 AT_END / AT_END_HEADING / AT_END_V (exact)
WIND = np.array([2.6, 1.2, 0.0])           # = g5 (smoke drift)
STEAM_WARM = (1.0, 0.88, 0.74)             # = g5 v2: counters the blue sky fill on steam cards
SMOKE_SITES = [(-62, 112), (48, 140), (-108, 186), (118, 228), (-28, 262), (-188, 142), (168, 330), (-138, 362), (64, 420),
               (-232, 262), (222, 150), (-84, 560), (-300, 420)]                # = g5 (continue its columns over the seam)
SMOKE_KEEP = (11, 12, 8, 9)                # these 4 keep burning; the other 9 sources die out 15-40 s (bible: 2-4 in g6)

def wing_roof_z(y):
    """Wing HW south roof slope (eave Y 627.4 Z 23.8 -> ridge Y 640 Z 41)."""
    return 23.8 + (min(max(y, 627.4), 640.0) - 627.4) * (17.2 / 12.6)

# ====================================================================== camera (camkeys.G6 = bible keys, pitch <= 45 rework)
CAM_KEYS = list(camkeys.G6)
_ck = camkeys.cam("g6")
CAM = camchan.CamPath(CAM_KEYS, v_in=_ck["v_in"], v_out=_ck["v_out"])
CAM_LIMITS = dict(speed=48.0, yaw=30.0, pitch=(17.0, 45.0), hmin=90.0, hmax=380.0, lens=(27.0, 50.0))
SHAKES = [(11.95, 0.0045, 0.35), (43.65, 0.0052, 0.40)]     # VIDEO clock: (t, amplitude rad <= 0.3 deg, duration)

# ====================================================================== small pure helpers
def ss(a, b, x):
    u = min(1.0, max(0.0, (x - a) / (b - a))) if b != a else float(x >= b)
    return u * u * (3 - 2 * u)

def lerp(a, b, u):
    return a + (b - a) * u

def bump(t, a, b, c, d):
    return ss(a, b, t) * (1 - ss(c, d, t))

def heading_yaw(compass_deg):
    """compass bearing (deg, cw from N) -> yaw (rad, ccw from +Y; attack_titan / odm / trost_action convention)."""
    return -math.radians(compass_deg)

def yaw_to(dx, dy):
    return math.atan2(-dx, dy)

def hvec(compass_deg):
    a = math.radians(compass_deg); return np.array([math.sin(a), math.cos(a)])

# ====================================================================== the Attack Titan (pure keys -> state)
# (t, x, y, compass heading, mode of the segment ENDING at this key)
AT_KEYS = [
    (0.00, -231.0, 531.0, 349, "walk"),        # = g5 AT_END (6 m/s, heading 349)
    (2.60, -232.5, 549.0, 0, "walk_in"),       # Hermite from the g5 tangent into the run
    (3.10, -232.4, 553.0, 2, "punch"),         # ST1 knocked aside into the plaza mouth without stopping
    (6.60, -232.0, 580.0, 0, "run"),
    (6.90, -232.0, 581.0, 343, "stand"),
    (7.90, -232.0, 581.0, 343, "roar"),        # looks up at the HQ (ep08 06:33)
    (8.10, -232.5, 582.0, 335, "stand"),
    (9.90, -244.0, 604.0, 335, "run"),
    (10.70, -249.0, 620.0, 0, "climb"),        # leap up the keep face
    (11.00, -249.0, 620.5, 0, "punch"),        # fist into the roof-walk titans by the hall hole
    (11.90, -226.0, 602.0, 125, "tackle"),     # both carried off ESE onto the apron
    (12.30, -227.0, 602.0, 250, "land"),
    (12.85, -228.5, 602.0, 250, "stomp"),      # R1 (12.6)
    (13.40, -222.5, 600.5, 100, "run"),
    (14.10, -222.0, 600.0, 120, "stomp"),      # R2 (13.8)
    (15.20, -213.0, 601.0, 60, "walk"),
    (16.00, -212.5, 601.5, 55, "punch"),       # F2's head off (15.85)
    (16.50, -212.5, 601.5, 70, "stand"),
    (17.50, -212.5, 601.5, 70, "roar"),        # head thrown back (ep08 10:22)
    (18.20, -197.0, 598.0, 100, "run"),
    (18.80, -196.5, 598.0, 100, "uppercut"),   # F3 (18.45)
    (23.40, -198.0, 599.0, 190, "boxer"),      # faces W1 coming from the SW
    (24.40, -198.5, 598.0, 190, "slam"),       # W1 slammed into the paving (24.05)
    (31.20, -198.0, 600.0, 120, "boxer"),
    (35.50, -198.0, 600.0, 120, "flail"),      # swarmed: 3 biters thrown off / stomped
    (36.00, -198.0, 600.0, 270, "stand"),      # owner 10/27: surrounded, he spots the BLOND titan (Thomas's eater) to the west
    (36.90, -224.0, 600.5, 270, "run"),        # charges madly (~29 m/s)
    (37.90, -225.0, 600.5, 270, "bite"),       # bites its nape
    (38.70, -225.5, 601.0, 320, "throw"),      # and hurls it NW at the last titan standing (F5 at the keep's NW foot)
    (40.80, -205.0, 618.0, 60, "walk"),
    (41.80, -205.0, 618.0, 160, "roar"),       # arms hanging, head back (ep08 19:35.9)
    (42.10, -204.5, 618.5, 90, "stand"),
    (42.80, -201.5, 619.0, 90, "lunge"),
    (43.60, -199.5, 619.0, 90, "fall"),        # face down
    (45.00, -191.5, 619.0, 90, "skid"),        # 10 m east along the wing plinth, legs to the keep
]
AT_STEP = {"run": 10.0, "walk": 7.0, "walk_in": 7.0}
LIN = ("run", "walk", "walk_in", "tackle", "fall", "lunge", "climb")
PRONE = 1.50                                 # rad: face down (holder pitch about the feet)
LIE_DZ = [1.3]                               # body depth when prone (measured at build)
NAPE_OFF = [13.4, 1.2]                       # prone nape: forward from the feet, height (measured at build)

def _at_cum():
    c = [0.0]
    for a, b in zip(AT_KEYS, AT_KEYS[1:]):
        c.append(c[-1] + math.hypot(b[1] - a[1], b[2] - a[2]))
    return c
_AT_CUM = _at_cum()
WALK0 = [0.0]                                # g5's walked distance at its end (stride phase continuity; set at build)

def _walk_in_pos(u):
    a, b = AT_KEYS[0], AT_KEYS[1]
    T = b[0] - a[0]
    p0 = np.array(a[1:3], float); p1 = np.array(b[1:3], float)
    m0 = hvec(SEAM5["heading"]) * SEAM5["v"] * T
    v1 = math.hypot(AT_KEYS[3][1] - b[1], AT_KEYS[3][2] - b[2]) / (AT_KEYS[3][0] - b[0])
    m1 = hvec(0.0) * v1 * T
    h00, h10, h01, h11 = 2 * u ** 3 - 3 * u ** 2 + 1, u ** 3 - 2 * u ** 2 + u, -2 * u ** 3 + 3 * u ** 2, u ** 3 - u ** 2
    return p0 * h00 + m0 * h10 + p1 * h01 + m1 * h11

def at_state(t):
    ks = AT_KEYS
    t = max(t, 0.0)
    if t >= ks[-1][0]:
        return dict(pos=np.array(ks[-1][1:3], float), yaw=heading_yaw(ks[-1][3]), mode="lie", u=1.0, t0=ks[-1][0], t1=1e9,
                    walked=WALK0[0] + _AT_CUM[-1], eyes=0.0)
    for i, (a, b) in enumerate(zip(ks, ks[1:])):
        if a[0] <= t < b[0]:
            break
    mode = b[4]
    u = (t - a[0]) / (b[0] - a[0])
    if mode in LIN:
        ue = u
    elif mode == "skid":
        ue = 1 - (1 - u) ** 2
    else:
        ue = u * u * (3 - 2 * u)
    if mode == "walk_in":
        p = _walk_in_pos(u); d = _walk_in_pos(min(1.0, u + 0.01)) - p
        if u > 0.99:
            d = hvec(b[3])
        yaw = yaw_to(d[0], d[1]) if u > 1e-4 else heading_yaw(SEAM5["heading"])
        walked = _AT_CUM[i] + float(np.linalg.norm(p - np.array(a[1:3])))
    else:
        p = np.array([lerp(a[1], b[1], ue), lerp(a[2], b[2], ue)])
        ya, yb = heading_yaw(a[3]), heading_yaw(b[3])
        dy = (yb - ya + math.pi) % math.tau - math.pi
        yaw = ya + dy * ss(0.0, 0.6 if mode in LIN else 1.0, u)
        walked = _AT_CUM[i] + math.hypot(b[1] - a[1], b[2] - a[2]) * ue
    eyes = 6.0 if mode == "roar" else 0.0            # <= 2 px green (bible owner rule)
    return dict(pos=p, yaw=yaw, mode=mode, u=u, t0=a[0], t1=b[0], walked=WALK0[0] + walked, eyes=eyes)

def at_vel(t, dt=0.05):
    a = at_state(max(0.0, t - dt))["pos"]; b = at_state(t + dt)["pos"]
    return (b - a) / (t + dt - max(0.0, t - dt))

def at_z(t):
    """Holder height above the ground (the leap / punch on the keep face, the tackle fall)."""
    l0, l1 = BEATS["leap"]; k0, k1 = BEATS["tackle"]
    if l0 <= t < l1:
        u = (t - l0) / (l1 - l0); return 15.0 * ss(0, 1, u) + 3.0 * math.sin(math.pi * u)
    if l1 <= t < k0:
        return lerp(15.0, 16.0, (t - l1) / (k0 - l1))
    if k0 <= t < k1:
        u = (t - k0) / (k1 - k0); return 16.0 * (1 - u) + 10.0 * u * (1 - u)
    return 0.0

def at_pitch(t):
    k0, k1 = BEATS["tackle"]
    if k0 <= t < k1:
        return 0.55 * math.sin(math.pi * (t - k0) / (k1 - k0))
    if t < BEATS["lunge"][0]:
        return 0.0
    if t < BEATS["fall"][0]:
        return 0.28 * ss(*BEATS["lunge"], t)
    if t < BEATS["fall"][1]:
        u = (t - BEATS["fall"][0]) / (BEATS["fall"][1] - BEATS["fall"][0])
        return 0.28 + (PRONE - 0.28) * u ** 1.7
    return PRONE

def nape_M(t):
    """Pure prone-nape position (M) once he lies still (the build measures NAPE_OFF from the posed asset)."""
    st = at_state(max(t, BEATS["skid"][1]))
    f = hvec(AT_KEYS[-1][3])
    return np.array([st["pos"][0] + f[0] * NAPE_OFF[0], st["pos"][1] + f[1] * NAPE_OFF[0], NAPE_OFF[1]])

def cage_z(t):
    u = min(1.0, max(0.0, (t - BEATS["lift"][0]) / (BEATS["lift"][1] - BEATS["lift"][0])))
    u = 1 - (1 - u) ** 2                                        # ease-out onto the firing level
    return lerp(CAGE_Z[0], CAGE_Z[1], u)

def cut_frac(t):
    return ss(*BEATS["cut_open"], t) * (1 - ss(*BEATS["cut_close"], t))

# ====================================================================== everything below needs Blender
STATE = {}
PLACEHOLDERS = []

def say(*a):
    print("[seg g6]", *a, flush=True)

def _site():
    return STATE["site"]

def S3(x, y=None, z=0.0):
    """M -> set coords (np array)."""
    if y is None:
        p = x; x, y, z = float(p[0]), float(p[1]), float(p[2]) if len(p) > 2 else 0.0
    return np.array([float(x), float(y) - segtime.SET_OFF_Y, float(z)])

def SV(x, y=None, z=0.0):
    return Vector(S3(x, y, z))

def G(x, y):
    return _site()["ground_M"](float(x), float(y))

def _coll(name):
    c = bpy.data.collections.get(name)
    return c if c else STATE["L"].new_coll(name)

def hexrgb(h):
    h = h.lstrip("#"); c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c)

def _hide(ob, h):
    if ob is not None and (ob.hide_render != h or ob.hide_viewport != h):
        ob.hide_render = ob.hide_viewport = h

_RC = {}
def top_z(x, y, default=None, zmax=400.0):
    key = (round(x, 1), round(y, 1))
    if key in _RC:
        return _RC[key]
    dg = bpy.context.evaluated_depsgraph_get()
    hit, loc, nrm, idx, ob, mw = bpy.context.scene.ray_cast(dg, SV(x, y, zmax), Vector((0, 0, -1)))
    z = float(loc.z) if hit else (default if default is not None else G(x, y))
    if hit and ob is not None and (ob.name.startswith("Haze") or ob.name.startswith("Sky") or ob.name.startswith("TrostHQ_BayShadow")):
        z = default if default is not None else G(x, y)
    _RC[key] = z
    return z

def perch(x, y, search=4.0):
    best = None
    for dx, dy in ((0, 0), (search, 0), (-search, 0), (0, search), (0, -search)):
        z = top_z(x + dx, y + dy)
        if best is None or z > best[2] + 0.5:
            best = (x + dx, y + dy, z)
    return np.array([best[0], best[1], best[2] + 0.05])

def roof_set(x, y, search=4.0):
    q = perch(x, y, search); return S3(q[0], q[1], q[2])

def gnd_set(x, y, dz=0.05):
    return S3(x, y, G(x, y) + dz)

# ====================================================================== Attack Titan (asset) with blended poses
def _V(r, f, z):
    import attack_titan as AT
    return AT.V(r, f, z)

def blend(a, b, u):
    if u <= 0: return a
    if u >= 1: return b
    out = dict(hips=lerp(a["hips"], b["hips"], u), fist=lerp(a.get("fist", 0), b.get("fist", 0), u), jaw=lerp(a.get("jaw", 0), b.get("jaw", 0), u))
    ba = {k[0]: k[1:] for k in a.get("bend", [])}; bb = {k[0]: k[1:] for k in b.get("bend", [])}
    order = [k[0] for k in a.get("bend", [])] + [k[0] for k in b.get("bend", []) if k[0] not in ba]
    out["bend"] = [(n, *[lerp(x, y, u) for x, y in zip(ba.get(n, (0, 0, 0)), bb.get(n, (0, 0, 0)))]) for n in order]
    out["feet"] = {sd: (a["feet"][sd][0].lerp(b["feet"][sd][0], u), lerp(a["feet"][sd][1], b["feet"][sd][1], u)) for sd in ("L", "R")}
    out["knee"] = a.get("knee", _V(0, 1, 0)).lerp(b.get("knee", _V(0, 1, 0)), u)
    hands = {}
    for sd in ("L", "R"):
        pa, qa, ma = a["hands"][sd]; pb, qb, mb = b["hands"][sd]
        if ma != mb:
            pa = _abs_hand(sd, pa, ma); pb = _abs_hand(sd, pb, mb); ma = "abs"
        hands[sd] = (pa.lerp(pb, u), qa.lerp(qb, u), ma)
    out["hands"] = hands
    return out

def _abs_hand(sd, p, mode):
    return p if mode == "abs" else STATE["SH"][sd] + p

BENDS0 = ["spine.001_59", "spine.002_58", "spine.003_57", "spine.004_10", "Head_9"]
def _bends(p1, p2, p3, p4, ph, yaw=(0, 0, 0, 0, 0)):
    return [(n, p, y, 0) for n, p, y in zip(BENDS0, (p1, p2, p3, p4, ph), yaw)]

def make_poses():
    import attack_titan as AT
    V = AT.V
    P = {k: dict(v) for k, v in AT.POSES.items() if k in ("stand", "roar", "punch", "crouch")}
    st = P["stand"]
    P["run"] = dict(st, hips=8.3, bend=_bends(14, 10, 6, 2, -6),
                    hands={"R": (V(1.0, 0.6, -3.6), V(1, -0.6, 0), "sh"), "L": (V(-1.0, 0.6, -3.6), V(-1, -0.6, 0), "sh")}, fist=0.9, jaw=10)
    P["stomp_up"] = dict(st, hips=8.6, bend=_bends(8, 8, 6, 10, 18),
                         feet={"R": (V(1.5, 3.4, 3.6), -10), "L": (V(-1.4, -0.6, 0), 8)}, knee=V(0, 1, 0.3),
                         hands={"R": (V(1.8, -1.2, -3.6), V(1, -0.6, 0), "sh"), "L": (V(-1.8, -1.2, -3.6), V(-1, -0.6, 0), "sh")}, fist=1.0, jaw=26)
    P["stomp_down"] = dict(P["stomp_up"], hips=7.6, bend=_bends(16, 12, 8, 12, 20),
                           feet={"R": (V(1.5, 4.0, 0.2), -10), "L": (V(-1.4, -0.8, 0), 8)}, jaw=30)
    P["boxer"] = dict(st, hips=8.1, bend=_bends(6, 6, 4, 0, 0, (0, -8, -8, 0, 0)),
                      feet={"R": (V(1.8, -1.6, 0), -15), "L": (V(-1.6, 1.8, 0), 12)}, knee=V(0, 1, 0.25),
                      hands={"R": (V(-0.3, 2.0, 0.6), V(1, -0.2, -1), "sh"), "L": (V(0.4, 2.6, 1.0), V(-1, -0.2, -1), "sh")}, fist=1.0, jaw=8)
    P["jab"] = dict(P["boxer"], bend=_bends(10, 8, 6, 0, 0, (0, 12, 10, 0, 0)),
                    hands={"R": (V(-0.4, 5.0, 0.6), V(1, 0, -1), "sh"), "L": (V(0.5, 1.8, 0.4), V(-1, -0.2, -1), "sh")})
    P["jab_l"] = dict(P["boxer"], bend=_bends(10, 8, 6, 0, 0, (0, -12, -10, 0, 0)),
                      hands={"R": (V(-0.3, 1.8, 0.4), V(1, -0.2, -1), "sh"), "L": (V(0.4, 5.0, 0.6), V(-1, 0, -1), "sh")})
    P["slam"] = dict(st, hips=7.6, bend=_bends(22, 16, 8, -2, -6),
                     feet={"R": (V(1.6, -3.0, 0), -10), "L": (V(-1.6, 2.6, 0), 10)}, knee=V(0, 1, 0),
                     hands={"R": (V(-0.6, 5.0, 0.0), V(1, 0, -1), "sh"), "L": (V(0.6, 5.0, 0.0), V(-1, 0, -1), "sh")}, fist=0.4, jaw=24)
    P["slam_up"] = dict(P["slam"], hips=8.6, bend=_bends(-10, -8, -4, -4, -8),
                        hands={"R": (V(-0.4, 1.2, 5.6), V(1, 0, -1), "sh"), "L": (V(0.4, 1.2, 5.6), V(-1, 0, -1), "sh")})
    P["uppercut"] = dict(st, hips=8.4, bend=_bends(-8, -10, -6, -6, -10, (0, 10, 8, 0, 0)),
                         feet={"R": (V(1.7, -2.2, 0), -16), "L": (V(-1.6, 2.4, 0), 10)}, knee=V(0, 1, 0.1),
                         hands={"R": (V(-0.4, 2.4, 5.4), V(1, 0, -1), "sh"), "L": (V(0.6, 1.8, 0.2), V(-1, -0.2, -1), "sh")}, fist=1.0, jaw=18)
    P["climb"] = dict(st, hips=8.6, bend=_bends(12, 10, 6, -6, -14),
                      feet={"R": (V(1.5, 0.9, 2.4), -8), "L": (V(-1.4, 0.4, 0.0), 8)}, knee=V(0, 1, 0.4),
                      hands={"R": (V(0.0, 1.6, 5.4), V(1, -0.3, -0.4), "sh"), "L": (V(0.0, 1.6, 5.4), V(-1, -0.3, -0.4), "sh")}, fist=0.2, jaw=20)
    P["tackle"] = dict(st, hips=7.6, bend=_bends(26, 20, 10, -4, -10),
                       feet={"R": (V(1.5, -2.4, 1.0), -8), "L": (V(-1.5, -1.2, 0.4), 8)}, knee=V(0, 1, 0.2),
                       hands={"R": (V(-1.0, 3.8, -0.4), V(1, 0, -1), "sh"), "L": (V(1.0, 3.8, -0.4), V(-1, 0, -1), "sh")}, fist=0.1, jaw=24)
    P["bite"] = dict(st, hips=6.8, bend=_bends(30, 20, 10, 6, 14),
                     feet={"R": (V(2.0, -1.2, 0), -14), "L": (V(-2.0, 1.4, 0), 14)}, knee=V(0, 1, 0.3),
                     hands={"R": (V(-0.6, 3.6, -1.4), V(1, 0, -1), "sh"), "L": (V(0.6, 3.6, -1.4), V(-1, 0, -1), "sh")}, fist=0.0, jaw=34)
    P["lunge"] = dict(P["run"], hips=7.6, bend=_bends(24, 16, 8, -4, -10),
                      hands={"R": (V(0.4, 3.0, -1.8), V(1, -0.2, -0.6), "sh"), "L": (V(-0.4, 3.0, -1.8), V(-1, -0.2, -0.6), "sh")}, jaw=26)
    P["lie"] = dict(st, hips=8.9, bend=_bends(0, 0, 0, 6, 10),
                    feet={"R": (V(1.3, 0.0, 0), -4), "L": (V(-1.3, -0.4, 0), 4)}, knee=V(0, 1, 0.0),
                    hands={"R": (V(0.9, 1.6, 4.6), V(1, 0.6, 0), "sh"), "L": (V(-0.9, 1.6, 4.6), V(-1, 0.6, 0), "sh")}, fist=0.0, jaw=20)
    return P

def _walk_feet(spec, phase, amp, lift=0.9):
    import attack_titan as AT
    out = dict(spec)
    fr = -amp * math.cos(phase); fl = amp * math.cos(phase)
    lr = lift * max(0.0, math.sin(phase)); ll = lift * max(0.0, -math.sin(phase))
    fe = spec["feet"]
    out["feet"] = {"R": (fe["R"][0] + AT.V(0, fr, lr), fe["R"][1]), "L": (fe["L"][0] + AT.V(0, fl, ll), fe["L"][1])}
    hs = dict(spec["hands"])
    if hs["R"][2] == "sh" and hs["L"][2] == "sh":
        hs = {"R": (hs["R"][0] + AT.V(0, 0.5 * amp * math.cos(phase), 0), hs["R"][1], "sh"),
              "L": (hs["L"][0] + AT.V(0, -0.5 * amp * math.cos(phase), 0), hs["L"][1], "sh")}
        out["hands"] = hs
    return out

def build_attack(coll):
    import attack_titan as AT
    t0 = time.time()
    T = AT.place_attack(0.0, -5000.0, 0.0, "stand", name="G6Attack", eyes=0.0)
    STATE["AT"] = T
    T.holder.matrix_world = Matrix.Identity(4); bpy.context.view_layer.update()
    T.pose("stand", ground=False)
    STATE["SH"] = {"L": T.wpos("upper_arm.L_32").copy(), "R": T.wpos("upper_arm.R_55").copy()}
    STATE["P"] = make_poses()
    STATE["at_objs"] = [o for o in T.coll.all_objects]
    # prone calibration: holder at the origin facing +Y (yaw 0), pitched PRONE about the feet -> body depth + nape offset
    AT.POSES["_g6"] = STATE["P"]["lie"]; T.pose("_g6", ground=False)
    T.holder.location = (0, 0, 0); T.holder.rotation_euler = (PRONE, 0.0, math.pi)
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    zmin = 1e9
    for o in STATE["at_objs"]:
        if o.type != "MESH" or o.hide_render:
            continue
        try:
            oe = o.evaluated_get(dg); me = oe.to_mesh()
            mw = oe.matrix_world
            co = np.zeros(len(me.vertices) * 3); me.vertices.foreach_get("co", co); co = co.reshape(-1, 3)
            if len(co):
                M4 = np.array(mw)
                zs = co @ M4[2, :3] + M4[2, 3]
                zmin = min(zmin, float(zs.min()))
            oe.to_mesh_clear()
        except Exception as ex:
            say("prone calibration skipped", o.name, ex)
    if zmin < 1e8:
        LIE_DZ[0] = -zmin + 0.05
    neck = T.wpos("Head_9")
    NAPE_OFF[0] = float(neck.y); NAPE_OFF[1] = float(neck.z) + LIE_DZ[0] * math.sin(PRONE) + 0.9
    say(f"AT prone calibration: body depth {LIE_DZ[0]:.2f} m, nape {NAPE_OFF[0]:.1f} m forward of the feet at Z {NAPE_OFF[1]:.1f}")
    for o in STATE["at_objs"]:
        _hide(o, True)
    try:                                       # g5's walked distance at its end: the stride phase continues over the seam
        import seg_g5
        WALK0[0] = float(seg_g5.at_state(segtime.DUR["g5"])["walked"])
    except Exception as ex:
        say("g5 stride phase unavailable:", ex)
    say(f"Attack Titan imported {time.time() - t0:.1f}s")

def _pose_attack(t):
    import attack_titan as AT
    T = STATE["AT"]; P = STATE["P"]
    st = at_state(t)
    for o in STATE["at_objs"]:
        _hide(o, False)
    mode, u = st["mode"], st["u"]
    if mode in ("walk", "walk_in"):
        spec = _walk_feet(P["stand"], math.pi * st["walked"] / AT_STEP["walk"], 2.4)
        if mode == "walk_in":
            spec = blend(spec, _walk_feet(P["run"], math.pi * st["walked"] / AT_STEP["walk"], 3.0, lift=1.2), ss(0.3, 1.0, u))
    elif mode == "run":
        spec = _walk_feet(P["run"], math.pi * st["walked"] / AT_STEP["run"], 3.2, lift=1.4)
    elif mode == "punch":
        spec = blend(P["run"], P["punch"], bump(u, 0.0, 0.4, 0.8, 1.0) if st["t1"] < 5 else ss(0.0, 0.5, u))
    elif mode == "stand":
        spec = P["stand"]
    elif mode == "roar":
        spec = blend(P["stand"], P["roar"], bump(t, st["t0"], st["t0"] + 0.3, st["t1"] - 0.25, st["t1"]))
    elif mode == "climb":
        spec = blend(P["run"], P["climb"], ss(0.0, 0.5, u))
    elif mode == "tackle":
        spec = blend(P["punch"], P["tackle"], ss(0.0, 0.3, u))
    elif mode == "land":
        spec = blend(P["crouch"], P["stand"], ss(0.2, 1.0, u))
    elif mode == "stomp":
        ts = BEATS["r1_kill"] if t < 13.2 else BEATS["r2_kill"]
        up = bump(t, ts - 0.35, ts - 0.12, ts + 0.04, ts + 0.25)
        dn = bump(t, ts - 0.08, ts, ts + 0.1, ts + 0.3)
        spec = blend(blend(P["stand"], P["stomp_up"], up), P["stomp_down"], dn)
    elif mode == "uppercut":
        spec = blend(P["run"], P["uppercut"], bump(u, 0.0, 0.45, 0.8, 1.0))
    elif mode == "boxer":
        spec = blend(P["stand"], P["boxer"], ss(st["t0"], st["t0"] + 0.4, t))
        for tb in (21.0, 21.4, 27.9):
            spec = blend(spec, P["jab"], bump(t, tb - 0.1, tb, tb + 0.05, tb + 0.2))
    elif mode == "slam":
        tk = BEATS["w1_kill"]
        spec = blend(blend(P["boxer"], P["slam_up"], bump(t, st["t0"], tk - 0.35, tk - 0.15, tk)), P["slam"], ss(tk - 0.15, tk, t))
    elif mode == "flail":
        spec = P["boxer"]
        for k, tb in enumerate(BEATS["biter_kills"] + (31.8, 34.3)):
            spec = blend(spec, P["jab"] if k % 2 == 0 else P["jab_l"], bump(t, tb - 0.15, tb, tb + 0.08, tb + 0.3))
        ts = BEATS["biter_kills"][2]
        spec = blend(spec, P["stomp_down"], bump(t, ts - 0.1, ts, ts + 0.1, ts + 0.3))
    elif mode == "bite":
        spec = blend(P["run"], P["bite"], ss(st["t0"], st["t0"] + 0.35, t))
    elif mode == "throw":                                           # the bitten titan swung up and hurled (arms up, then through)
        spec = blend(blend(P["bite"], P["uppercut"], ss(0.0, 0.45, u)), P["punch"], ss(0.45, 0.9, u))
    elif mode == "lunge":
        spec = blend(P["stand"], P["lunge"], ss(0.0, 0.6, u))
    elif mode in ("fall", "skid", "lie"):
        spec = blend(P["lunge"], P["lie"], ss(0.0, 0.6, u) if mode == "fall" else 1.0)
    else:
        spec = P["stand"]
    AT.POSES["_g6"] = spec
    T.pose("_g6", ground=False)
    p = st["pos"]
    pitch = at_pitch(t)
    z = G(p[0], p[1]) + at_z(t) + LIE_DZ[0] * math.sin(max(0.0, pitch)) * ss(0.4, 1.0, pitch / PRONE)
    if mode == "run":
        z += 0.35 * abs(math.sin(math.pi * st["walked"] / AT_STEP["run"]))
    T.holder.location = Vector(S3(p[0], p[1], z))
    T.holder.rotation_euler = (pitch, 0.0, st["yaw"] + math.pi)
    T.eyes(st["eyes"])
    if mode == "lie" or (mode == "skid" and u > 0.9):
        STATE["nape_now"] = _nape_from_bone()
    return st

def _nape_from_bone():
    T = STATE["AT"]
    bpy.context.view_layer.update()
    n = T.wpos("Head_9")
    return np.array([n.x, n.y, n.z + 0.9])

# ====================================================================== pure titans (trost_action.Titans + g6 events)
class _TSite:
    def g(self, p):
        return G(float(p[0]), float(p[1]) + segtime.SET_OFF_Y)
    def nav(self):
        return None

class _NoSteam:
    def update(self, t, wind=None):
        pass

def make_titans_class():
    import trost_action as TA
    import swarm845 as SW
    import odm
    L = STATE["L"]

    class Titans6(TA.Titans):
        """trost_action.Titans plus the g6 events (g6 dict per spec): keep (corpse stays, slow shrink), fall (tf, dur, dirn),
        zoff(t) (height above the ground: keep climbers, the roof walk, hurled arcs), climb (t0, t1) arms up against a wall,
        reach (peering / reaching), cling (t0, t1) leaning in and biting, kneel / lying."""
        def poses(self, t):
            if self._cache_t == t:
                return self._cache
            R = super().poses(t)
            Ar, Ae, lean, vis, yaw, pos, pitch = R
            for j, sp in enumerate(self.specs):
                x = sp.get("g6")
                if not x:
                    continue
                a, b = self.show[j]
                if not (a <= t < b):
                    continue
                d = self.ev[j]["death"]
                dead = d is not None and t >= d[0]
                if x.get("keep") and dead:
                    vis[j] = 1.0 - (1.0 - x.get("shrink", 0.88)) * ss(d[0] + 2.0, d[0] + x.get("shrink_t", 40.0), t)
                if x.get("zoff") is not None:
                    pos[j, 2] += x["zoff"](t)
                if x.get("fall") is not None:
                    tf, dur, dirn = x["fall"]
                    if t >= tf:
                        u = ss(tf, tf + dur, t)
                        pf = -dirn * (math.pi / 2 - 0.1) * u
                        if abs(pf) > abs(pitch[j]) or not dead:
                            pitch[j] = pf
                        Ar[j, 3] = Ar[j, 4] = 1.6 * u + 0.2; Ar[j, 1] = 0.3 * u
                if x.get("climb") is not None:
                    c0, c1 = x["climb"]
                    w = bump(t, c0, c0 + 0.3, c1, c1 + 0.4)
                    if w > 0 and not dead:
                        Ar[j, 3] = Ar[j, 4] = (2.7 + 0.25 * math.sin(t * 5 + j)) * w; Ae[j, 5] = Ae[j, 6] = 0.3 * w
                        lean[j] = -0.12 * w; Ar[j, 1] = 0.5 * w * max(0.0, math.sin(t * 5 + j)); Ar[j, 2] = 0.5 * w * max(0.0, -math.sin(t * 5 + j))
                if x.get("reach") is not None and not dead and t >= x["reach"] and (x.get("reach_end") is None or t < x["reach_end"]):
                    u = ss(x["reach"], x["reach"] + 1.0, t)
                    Ar[j, 3] = Ar[j, 4] = (1.6 + 0.2 * math.sin(t * 1.4 + j)) * u; lean[j] = -0.3 * u; Ae[j, 5] = Ae[j, 6] = 0.5 * u
                if x.get("cling") is not None and not dead:
                    c0, c1 = x["cling"]
                    w = bump(t, c0, c0 + 0.3, c1, c1 + 0.2)
                    if w > 0:
                        lean[j] = -0.55 * w; Ar[j, 3] = Ar[j, 4] = (1.5 + 0.3 * math.sin(t * 7 + j)) * w; Ae[j, 5] = Ae[j, 6] = 0.9 * w
                if x.get("lying"):
                    pitch[j] = -(math.pi / 2 - 0.1); Ar[j, 3] = 0.6; Ar[j, 4] = 1.6
            self._rig = odm.deform(self.RX, Ar, Ae, lean, vis, yaw, pos, pitch, None, np.zeros(len(vis))).reshape(len(vis), 4, 3)
            return R

        def build(self, coll):
            gt = SW.Geo(); tmat = []; rig = []
            hb = len(SW.T_SKINS)
            for j, sp in enumerate(self.specs):
                n0 = len(gt.fc)
                sx, sh, la, hip, hc, hr = SW.titan_geo(gt, j, sp)
                sp.update(sx=sx, sh=sh, la=la, hip=hip, hc=hc, hr=hr)
                if sp.get("beard"):
                    gt.box((0, hr * 0.55, hc - hr * 0.75), (hr * 1.2, hr * 0.7, hr * 0.8), 1, j, 0, (0, 0), (0, 0), hip, taper=0.6)
                if sp.get("longhair"):
                    gt.box((0, -hr * 0.35, hc - hr * 1.0), (hr * 2.1, hr * 0.9, hr * 1.8), 1, j, 0, (0, 0), (0, 0), hip, taper=1.1)
                base = [sp["skin"], hb + (sp["hair"] if sp.get("hair") is not None else 0), hb + len(SW.T_HAIRS)]
                if sp.get("beard") and sp.get("hair") is None:
                    base[1] = hb + 1
                tmat += [base[c] for c in gt.fc[n0:]]
                rig.append([(sx, 0.0, sh - 2 * la, 5, (0, sh), (0, sh - la)), (0.0, hr * 0.9, hc - hr * 0.3, 0, (0, 0), (0, 0)),
                            (0.0, -hr * 0.9, hc - hr * 1.1, 0, (0, 0), (0, 0)), (0.0, 0.0, hc + hr * 1.05, 0, (0, 0), (0, 0))])
            tm = [L.mat(f"G6_tskin{i}", c, 0.65) for i, c in enumerate(SW.T_SKINS)] + [L.mat(f"G6_thair{i}", c, 0.7) for i, c in enumerate(SW.T_HAIRS)] \
                + [L.mat("G6_tteeth", (0.85, 0.80, 0.70), 0.5)]
            self.R = gt.finish()
            self.ob = SW._mesh("G6Titans", self.R, gt.f, tmat, tm, coll)
            Bp, oid, part, pr, pe, hipl = [], [], [], [], [], []
            for j, rr in enumerate(rig):
                for (x, y, z, p, a, b) in rr:
                    Bp.append((x, y, z)); oid.append(j); part.append(p); pr.append(a); pe.append(b); hipl.append(self.specs[j]["hip"])
            self.RX = {"B": np.array(Bp, float), "oid": np.array(oid, np.int32), "part": np.array(part, np.int32),
                       "pr": np.array(pr, float), "pe": np.array(pe, float), "hip": np.array(hipl, float)}
            self.RX["up"] = np.isin(self.RX["part"], (0, 3, 4, 5, 6)).astype(float)
            self.H = np.array([sp["H"] for sp in self.specs])
            self.steam = _NoSteam()                 # g6 draws thin steam COLUMNS itself (bible: no opaque blobs)

        def override(self, name, t0, t1, p0, p1):
            """Straight path override (set coords xy) between t0 and t1 after sim (hurls, skids); holds p1 after."""
            j = self.j(name)
            k0, k1 = int(round(t0 / TA.DT)), int(round(t1 / TA.DT))
            for k in range(max(0, k0), self.K):
                u = 1.0 if k >= k1 else ss(k0, k1, k)
                self.TX[k, j] = p0[0] + (p1[0] - p0[0]) * u; self.TY[k, j] = p0[1] + (p1[1] - p0[1]) * u
                self.TZ[k, j] = self.site.g((self.TX[k, j], self.TY[k, j]))
            self._cache_t = None
    return Titans6

# titan rosters (M).  Ring order around the cage: S5, S0, S2, S3, S4, S1, S6 (Mikasa's S0 next to Sasha's S5, Annie's S1
# next to Connie's S6)
RING_ORDER = ["S5", "S0", "S2", "S3", "S4", "S1", "S6"]
RING_R = 4.5
CUTTERS = {"S0": "mikasa", "S1": "annie", "S2": "reiner", "S3": "bertolt", "S4": "jean", "S5": "sasha", "S6": "connie"}
FINISH = {"S5": ("mikasa", BEATS["finish"][0]), "S6": ("annie", BEATS["finish"][1])}

def ring_pos(name):
    k = RING_ORDER.index(name)
    a = math.radians(205.0 + k * 360.0 / 7)
    return (LIFT_C[0] + RING_R * math.cos(a), LIFT_C[1] + RING_R * math.sin(a))

def _arc_z(t0, t1, z0, z1, apex):
    def f(t):
        if t < t0: return z0
        if t >= t1: return z1
        u = (t - t0) / (t1 - t0)
        return z0 * (1 - u) + z1 * u + 4 * apex * u * (1 - u)
    return f

def build_titans(coll):
    Titans6 = make_titans_class()
    TT = Titans6(_TSite(), seed=606)
    STATE["TT"] = TT
    rnd = random.Random(606)
    def add(name, H, keys_M, show=(-1e9, 1e9), g6=None, **sp):
        keys = [(k[0], *S3(k[1], k[2])[:2]) for k in keys_M]
        keys.sort(key=lambda k: k[0])
        if keys[-1][0] < 999:
            keys.append((999.0, keys[-1][1], keys[-1][2]))
        if keys[0][0] > -1:
            keys.insert(0, (-10.0, keys[0][1], keys[0][2]))
        TT.add(name, H=H, keys=keys, show=show, **sp)
        TT.specs[-1]["g6"] = g6 or {}
        return name
    def kill(name, td, dirn=1, keep=True, shrink=0.88, shrink_t=40.0):
        TT.ev[TT.j(name)]["death"] = (td, dirn)
        TT.specs[TT.j(name)].setdefault("g6", {}).update(keep=keep, shrink=shrink, shrink_t=shrink_t)
    def face(name, xy):
        if callable(xy):
            TT.specs[TT.j(name)]["face"] = lambda t, f=xy: (lambda q: (float(q[0]), float(q[1]) - segtime.SET_OFF_Y))(f(t))
        else:
            q = S3(*xy)[:2]; TT.specs[TT.j(name)]["face"] = (float(q[0]), float(q[1]))
    at_xy = lambda t: at_state(t)["pos"]
    # ---- ST1: street titan in the plaza mouth, knocked aside at 2.6 (falls back into the apron)
    add("ST1", 7.0, [(0.0, *ST1_POS)], hair=2)
    face("ST1", (-231, 540)); kill("ST1", BEATS["st1_kill"], -1)
    # ---- F0 / F1: g5's facade titans hq0 / hq1 climb the keep's south face onto the roof walk; tackled off at 11.0
    # v17 (FEEDBACK_v15): Eren pulling these two off the HQ is DELETED (G6_HQ_PAIR=1 restores them)
    k0, k1 = BEATS["tackle"]
    for nm, start, wall_x, land, H, kw, td in (() if not os.environ.get("G6_HQ_PAIR") else (("F0", (-262, 610), -255.5, (-232.0, 600.0), 6.5, dict(longhair=True, hair=1), BEATS["r1_kill"]),
                                               ("F1", (-244, 609), -246.5, (-218.0, 597.0), 6.0, dict(hair=0), BEATS["r2_kill"]))):
        c0, c1 = (0.8, 6.4) if nm == "F0" else (1.4, 6.8)
        keys = [(0.0, *start), (c0, *start), (c0 + 1.2, wall_x, 622.3), (c1, wall_x, 622.3), (c1 + 0.6, wall_x, 629.5),
                (k0 + 0.02, wall_x, 629.5), (k1, *land)]
        zc = lambda t, c0=c0, c1=c1: (2.5 * ss(c0, c0 + 1.2, t) + 23.5 * ss(c0 + 1.2, c1, t) + 2.0 * ss(c1, c1 + 0.6, t)) if t < k0 else \
            _arc_z(k0, k1, WALK_Z, 0.0, 3.0)(t)
        add(nm, H, keys, g6=dict(zoff=zc, climb=(c0 + 1.2, c1 + 0.2), reach=c1 + 0.8, reach_end=k0, fall=(k0 + 0.3, 0.6, -1)), **kw)
        face(nm, (HOLE[0], 645.0))
        kill(nm, td, -1)
    # ---- F2 / F3 (g5 hq2 / hq3): peer at the wing facade, then come at him; head-off punch 15.85, uppercut 18.45
    add("F2", 7.5, [(0.0, -212, 620), (13.3, -212, 620), (15.4, -207, 606.5)], g6=dict(reach=0.0, reach_end=13.2), hair=3)
    face("F2", lambda t: at_xy(t) if t > 13.0 else (-212, 632)); kill("F2", BEATS["f2_kill"], -1)
    add("F3", 6.5, [(0.0, -184, 621), (16.0, -184, 621), (18.1, -191, 598.5)], g6=dict(reach=0.0, reach_end=15.9), hair=None)
    face("F3", lambda t: at_xy(t) if t > 15.8 else (-184, 632)); kill("F3", BEATS["f3_kill"], -1)
    # ---- F5 (g5 hq5): stays at the keep's NW foot, hands on the stones
    add("F5", 7.0, [(0.0, -272, 664)], g6=dict(reach=0.0, fall=(BEATS["brd_hit"] + 0.05, 0.5, 1)), hair=2)
    face("F5", (-268, 652)); kill("F5", BEATS["brd_hit"] + 0.05, 1)                 # flattened by the thrown blond titan
    # ---- W1 (g5 hqw2): wanders in from the SW, slammed into the paving 24.05
    add("W1", 5.5, [(0.0, -206, 588), (20.8, -206, 589), (23.6, -199.5, 591.5)], hair=1)
    face("W1", at_xy); kill("W1", BEATS["w1_kill"], 1)
    # ---- the swarm: B1 (g5 hqw3), B2 (g5 hqw1), B3 (g5 hq4) cling 31.2-35, thrown / stomped
    for nm, keys, H, tk, dirn, kw in (("B1", [(0.0, -120, 610), (22.0, -125, 606), (31.2, -193.0, 602.5)], 4.5, 0, 1, dict(hair=0)),
                                      ("B2", [(0.0, -286, 596), (24.0, -280, 598), (31.3, -203.0, 597.5)], 5.0, 1, 1, dict(hair=None)),
                                      ("B3", [(0.0, -152, 620), (25.0, -152, 620), (31.6, -197.0, 594.5)], 6.0, 2, 1, dict(hair=3))):
        te = BEATS["biter_kills"][tk]
        z = (lambda t, te=te: (_arc_z(te, te + 0.6, 0.0, 0.0, 5.0)(t))) if nm != "B3" else None
        g6 = dict(cling=(BEATS["swarm"][0], te), fall=(te + 0.05, 0.5, 1) if nm != "B3" else None)
        if z is not None:
            g6["zoff"] = z
        if nm in ("B2", "B3"):
            g6.update(reach=0.0, reach_end=26.0 if nm == "B3" else 0.1)
        add(nm, H, keys, g6=g6, **kw)
        face(nm, at_xy); kill(nm, te, dirn)
    # ---- BRD: the BLOND titan (Thomas's eater, owner 10/27) from the west strip: spotted 35.5, nape bitten 36.9-37.9,
    # swung up and thrown NW onto F5 (impact 38.9)
    th0, th1 = BEATS["throw"][0] + 0.3, BEATS["brd_hit"]
    add("BRD", 8.0, [(0.0, -300, 598), (BEATS["brd_in"][0], -300, 598), (BEATS["brd_in"][1], -232.0, 601.0)],
        show=(BEATS["brd_in"][0] - 0.1, 1e9), hair=3, g=1.05, grin=True,
        g6=dict(zoff=_arc_z(th0, th1, 0.0, 0.0, 14.0), fall=(th0, 0.5, 1)))
    face("BRD", at_xy); kill("BRD", BEATS["brd_kill"], 1)
    # ---- CC: g5's crew-cut 12 m titan, slammed into tower T and nape-stamped at g5 66.8 (= g6 -3.2): its corpse stays
    add("CC", 12.0, [(0.0, *CC_POS)], g=0.95, al=1.05, hair=0)
    face("CC", (-246, 499)); kill("CC", CC_KILL, 1, keep=True, shrink=0.85, shrink_t=20.0)
    # ---- W0 (g5 hqw0): drifts off east, out of the late framings
    add("W0", 6.0, [(0.0, -160, 592), (14.0, -140, 584), (34.0, -104, 580)], hair=2)
    # ---- storeroom: exactly 7 titans of 3-4 m, milling, then a 4.5 m ring round the cage (arms reaching), blinded 27.55
    for k, nm in enumerate(["S0", "S1", "S2", "S3", "S4", "S5", "S6"]):
        rx, ry = ring_pos(nm)
        ox, oy = rx - LIFT_C[0], ry - LIFT_C[1]
        sx = min(BAY[1] - 2.8, max(BAY[0] + 3.2, rx + ox * rnd.uniform(0.6, 1.8)))
        sy = min(BAY[3] - 1.8, max(BAY[2] + 1.8, ry + oy * rnd.uniform(0.6, 1.4)))
        mx_, my_ = sx + rnd.uniform(-2, 2), sy + rnd.uniform(-1.5, 1.5)
        mx_ = min(BAY[1] - 2.8, max(BAY[0] + 3.2, mx_)); my_ = min(BAY[3] - 1.8, max(BAY[2] + 1.8, my_))
        r0 = BEATS["ring"][0] + rnd.uniform(0.0, 1.2)
        add(nm, rnd.uniform(3.0, 4.0), [(0.0, sx, sy), (11.0, mx_, my_), (r0, mx_, my_), (BEATS["ring"][1] - rnd.uniform(0, 0.6), rx, ry)],
            g6=dict(reach=BEATS["ring"][0] + 2.0, reach_end=BEATS["volley"]), hair=rnd.choice([None, 0, 1, 2, 3]))
        TT.ev[-1]["blind"] = BEATS["volley"] + 0.05
        if nm in FINISH:
            tgt = CUTTERS[nm]
            miss = MISS_SPOT[nm]
            face(nm, (lambda m: (lambda t: m if t > BEATS["misses"][0] else LIFT_C))(miss))
            kill(nm, FINISH[nm][1], 1, shrink=0.8, shrink_t=20.0)
        else:
            face(nm, LIFT_C)
            kill(nm, BEATS["drop"][1], 1, shrink=0.8, shrink_t=20.0)
    TT.sim(DUR + 1.0)
    TT.override("BRD", th0, th1, S3(-232.0, 601.0)[:2], S3(-268.0, 657.0)[:2])
    TT.override("ST1", BEATS["st1_kill"], BEATS["st1_kill"] + 0.55, S3(*ST1_POS)[:2], S3(-227.0, 574.0)[:2])
    TT.override("F2", BEATS["f2_kill"], BEATS["f2_kill"] + 0.4, S3(-207, 606.5)[:2], S3(-203.5, 609.5)[:2])
    TT.override("F3", BEATS["f3_kill"], BEATS["f3_kill"] + 0.45, S3(-191, 598.5)[:2], S3(-186.0, 597.0)[:2])
    TT.override("B1", BEATS["biter_kills"][0], BEATS["biter_kills"][0] + 0.6, S3(-193.0, 602.5)[:2], S3(-181.0, 604.0)[:2])
    TT.override("B2", BEATS["biter_kills"][1], BEATS["biter_kills"][1] + 0.6, S3(-203.0, 597.5)[:2], S3(-215.0, 589.0)[:2])
    TT.build(coll)
    say(f"titans: {len(TT.specs)}")

# Sasha / Connie miss: they land on the floor beside their titans, which turn on them
MISS_SPOT = {}
def _miss_spots():
    for nm in ("S5", "S6"):
        rx, ry = ring_pos(nm); o = np.array([rx - LIFT_C[0], ry - LIFT_C[1]]) / RING_R
        side = np.array([-o[1], o[0]]) * (1.4 if nm == "S5" else -1.4)
        MISS_SPOT[nm] = (rx + o[0] * 1.6 + side[0], ry + o[1] * 1.6 + side[1])
_miss_spots()

def titan_M(name, t, part="pos"):
    TT = STATE["TT"]
    p = getattr(TT, part)(name, t)
    return np.array([p[0], p[1] + segtime.SET_OFF_Y, p[2]])

# ====================================================================== people: one-hook ODM squads (odm.Squads, hook=True)
HOP_MAX = 34.0                                  # coordinator QA: a hook anchor is never more than 34 m from the soldier
HOOKS = []                                      # (flyer, t0, p0, anchor) for the check

def _anchor(p0, p1, up=3.5, ahead=2.5):
    """A hook anchor near the landing (a wall / roof edge / beam there), pulled in to <= HOP_MAX from the take-off."""
    p0 = np.asarray(p0, float); p1 = np.asarray(p1, float)
    d = p1 - p0; dh = np.array([d[0], d[1], 0.0]); n = np.linalg.norm(dh)
    fwd = dh / n if n > 1e-3 else np.array([0.0, 1.0, 0.0])
    A = p1 + fwd * ahead + np.array([0.0, 0.0, up])
    L_ = np.linalg.norm(A - (p0 + np.array([0, 0, 0.9])))
    if L_ > HOP_MAX:
        A = p0 + np.array([0, 0, 0.9]) + (A - p0 - np.array([0, 0, 0.9])) * (HOP_MAX / L_)
    return A

def hop(f, t0, t1, p0, p1, anchor=None, gas=1.0, apex=None):
    A = np.asarray(anchor, float) if anchor is not None else _anchor(p0, p1)
    HOOKS.append((f.name, t0, np.asarray(p0, float), A))
    f.hop(t0, t1, p0, p1, apex=apex, gas=gas, anchors=[A])
    return f

def fly(f, t, pts, speed=17.0, wait=0.12, anchors=None, gas_last=1.0):
    """Hop through explicit set-coord points (every leg <= ~28 m); returns (t, last point)."""
    prev = np.asarray(pts[0], float)
    for k, q in enumerate(pts[1:]):
        q = np.asarray(q, float)
        d = float(np.linalg.norm(q - prev)); dt = max(0.8, d / speed)
        A = anchors[k] if anchors and k < len(anchors) else None
        hop(f, t, t + dt, prev, q, anchor=A, gas=gas_last if k == len(pts) - 2 else 1.0)
        t += dt
        if k < len(pts) - 2 and wait > 0:
            f.stand(t, t + wait, q, odm_yaw(q - prev), "crouch"); t += wait
        prev = q
    return t, prev

def run(f, t0, p0, p1, v=7.0):
    """On foot across open paving (no hook): returns the arrival time."""
    t1 = t0 + max(0.4, float(np.linalg.norm(np.asarray(p1)[:2] - np.asarray(p0)[:2])) / v)
    f.walk(t0, t1, p0, p1, "run")
    return t1

def odm_yaw(d):
    import odm
    return odm.yaw_of(np.array([d[0], d[1], 0.0]))

def build_people(coll):
    import odm
    rnd = random.Random(660)
    SQ = odm.Squads("G6Squads", pscale=1.0, hook=True)
    STATE["SQ"] = SQ
    TT = STATE["TT"]
    H = 1.65
    yaw_at = lambda a, b: odm_yaw(np.array([b[0] - a[0], b[1] - a[1]]))
    nape = lambda nm: (lambda t: TT.nape(nm, t))
    W_S = S3(-242.5, 634.6, 39.0); W_N = S3(-257.5, 634.6, 39.0)              # the tall leaded hall windows (tier 2, south)
    W_E = [S3(-239.6, 639.0, 33.0), S3(-239.6, 649.0, 33.0)]                  # east face windows
    STATE["windows"] = []
    # ---------------- Jean's squad + the stranded 104th (g5 left 18 round (-196, 576), several on the apron itself): two
    # desperate ODM hops - low over the apron on the keep's parapet, then straight through the hall windows (4.4 / 5.0 ...)
    names = ["jean"] + [f"j{k}" for k in range(7)] + [f"c{k}" for k in range(10)]
    for k, nm in enumerate(names):
        f = SQ.flyer(nm, "cadet", "jean" if nm == "jean" else rnd.choice(["dark", "brown", "ash", "black", "auburn", "blond"]), H=H)
        if nm == "jean":
            x0, y0 = -236.0, 598.0
        else:
            x0, y0 = -214 + rnd.uniform(-16, 16), 586 + rnd.uniform(-7, 7)
        p0 = gnd_set(x0, y0)
        # owner 10/27: they FLY (ODM) desperately straight at the keep and crash the windows - no walking
        win = W_S if k % 3 == 0 else (W_N if k % 3 == 1 else W_E[k % 2])
        tw = BEATS["crash"][k % 2] + 0.12 * k if k < 8 else BEATS["stragglers"][0] + 0.4 * (k - 8) + 1.9
        xr = -262 + 24 * ((k * 5) % 18) / 17.0 + rnd.uniform(-0.5, 0.5)
        mid = S3(xr + rnd.uniform(-2, 2), 611.0 + rnd.uniform(-2, 2), 15.0 + rnd.uniform(-2, 3))     # low over the apron
        t0 = tw - 1.75
        f.stand(0.0, t0, p0, yaw_at((x0, y0), HQ), rnd.choice(["crouch", "stand"]))
        hop(f, t0, t0 + 1.05, p0, mid, anchor=np.array([xr, 624.3 - segtime.SET_OFF_Y, WALK_Z + 1.6]))
        if nm == "jean":
            STATE["jean_land"] = t0 + 1.05
        hop(f, t0 + 1.05, tw + 0.45, mid, win, anchor=win + np.array([0, 0.6, 2.5]))
        f.gone(tw + 0.45)
        STATE["windows"].append((tw + 0.42, win))
    # ---------------- Armin, Mikasa, Connie: from g5's ridge R over two roofs, glide down to the apron, run, hook the
    # parapet, crash a window with the gas running out (~13.4)
    ridge = S3(*ROOF_R)
    trio = [("mikasa_a", "black", dict(scarf=True), ridge + np.array([0.0, 0.0, 0.05]), "kneel"),
            ("armin_a", "blond", dict(H=1.63), ridge + np.array([1.2, -0.6, 0.05]), "stand"),
            ("connie_a", "grey", {}, ridge + np.array([-1.4, 0.8, 0.05]), "stand")]
    for k, (nm, hair, kw, p0, pose) in enumerate(trio):
        kw.setdefault("H", H)
        f = SQ.flyer(nm, "cadet", hair, **kw)
        t0 = BEATS["trio"][0] + 0.25 * k
        f.stand(0.0, t0, p0, heading_yaw(110.0), pose)
        r1 = roof_set(-261 + 2 * k, 529); r2 = roof_set(-263 + 2 * k, 553)
        hop(f, t0, t0 + 1.0, p0, r1); hop(f, t0 + 1.0, t0 + 2.0, r1, r2)
        g0 = S3(-263 + 2 * k, 580.0, 16.0)                       # owner 10/27: glide low over the apron on the wire, no running
        hop(f, t0 + 2.0, t0 + 3.1, r2, g0, anchor=np.array([-263 + 2 * k, 600.0 - segtime.SET_OFF_Y, 24.0]), gas=0.9)
        g1 = S3(-262 + 2 * k, 608.0, 13.0)
        hop(f, t0 + 3.1, t0 + 4.1, g0, g1, anchor=np.array([-262 + 2 * k, 624.3 - segtime.SET_OFF_Y, WALK_Z + 1.6]), gas=0.85)
        t = t0 + 4.1
        rw = S3(-262 + 2 * k, 626.8, WALK_Z + 0.1)
        hop(f, t, t + 0.9, g1, rw, anchor=np.array([-262 + 2 * k, 624.3 - segtime.SET_OFF_Y, WALK_Z + 1.6]), gas=0.8)
        t += 0.9
        tw = max(t + 0.15, BEATS["trio"][1] - 0.45 + 0.1 * k)
        f.stand(t, tw, rw, heading_yaw(0.0), "crouch")
        hop(f, tw, tw + 0.4, rw, W_N + np.array([1.0 * k, 0, 0]), anchor=W_N + np.array([1.0 * k, 0.6, 1.2]), gas=0.5)
        f.gone(tw + 0.4)
        STATE["windows"].append((tw + 0.38, W_N))
    # ---------------- the cage: 28 gunners round the rim (7 per side), rifles out; gone when the roof returns
    def cage_set(t):
        return S3(LIFT_C[0], LIFT_C[1], cage_z(t) + 0.2)
    STATE["muzzles"] = []
    k = 0
    for side, (ox, oy) in enumerate(((0, -1), (1, 0), (0, 1), (-1, 0))):
        for u in np.linspace(-2.1, 2.1, 7):
            off = np.array([ox * 2.05 + (-oy) * u, oy * 2.05 + ox * u, 0.0])
            f = SQ.flyer(f"g{k}", "cadet", rnd.choice(["dark", "brown", "ash", "black", "auburn", "blond", "grey"]), rifle=True, H=H)
            yw = odm_yaw(np.array([ox, oy]))
            f.follow(0.0, BEATS["inside_gone"], (lambda o: (lambda t: cage_set(t) + o))(off), yaw_fn=(lambda y: (lambda t: y))(yw), pose="aim")
            f.gone(BEATS["inside_gone"])
            STATE["muzzles"].append(np.array(S3(LIFT_C[0], LIFT_C[1], CAGE_Z[1] + 0.2)) + off * 1.3 + np.array([0, 0, 1.25]))
            k += 1
    # ---------------- the 7 cutters on the rafters above each titan's back; drop 27.8-28.8; Sasha / Connie miss
    cut = {}
    for nm_t, who in CUTTERS.items():
        hair = dict(mikasa="black", annie="blond", reiner="blond", bertolt="dark", jean="jean", sasha="auburn", connie="grey")[who]
        f = SQ.flyer(who, "cadet", hair, H=(1.53 if who == "annie" else 1.85 if who == "reiner" else 1.92 if who == "bertolt" else H),
                     **(dict(scarf=True) if who == "mikasa" else {}))
        rx, ry = ring_pos(nm_t); o = np.array([rx - LIFT_C[0], ry - LIFT_C[1]]) / RING_R
        bx = min(RAFTERS_X, key=lambda X: abs(X - (rx + o[0] * 1.2)))
        by = min(BAY[3] - 1.2, max(BAY[2] + 1.2, ry + o[1] * 1.4))
        perch_p = S3(bx, by, 6.3)
        d0 = BEATS["drop"][0] + rnd.uniform(0.0, 0.15)
        f.stand(0.0, d0, perch_p, odm_yaw(-o), "crouch")
        if who in ("sasha", "connie"):
            ms = MISS_SPOT["S5" if who == "sasha" else "S6"]
            f.dive(d0, BEATS["drop"][1], perch_p, (lambda q: (lambda t: q))(S3(ms[0], ms[1], 0.15)))
            f.stand(BEATS["drop"][1], BEATS["inside_gone"], S3(ms[0], ms[1], 0.15), odm_yaw(np.array([rx - ms[0], ry - ms[1]])), "crouch")
        else:
            f.dive(d0, BEATS["drop"][1], perch_p, nape(nm_t))
            f.follow(BEATS["drop"][1], BEATS["drop"][1] + 0.6, nape(nm_t), pose="crouch")
            q = TT.nape(nm_t, BEATS["drop"][1] + 0.6)
            q = np.array([q[0], q[1], 0.15])
            f.stand(BEATS["drop"][1] + 0.6, BEATS["inside_gone"], q, odm_yaw(-o), "stand")
        cut[who] = f
        HOOKS.append((who, d0, perch_p, np.asarray(TT.nape(nm_t, BEATS["drop"][1]), float)))
    for nm_t, (who, tk) in FINISH.items():                     # Mikasa and Annie spring onto the two survivors' napes
        f = cut[who]; t0_ = tk - 0.6
        p0 = f.state(t0_ - 0.01)["pos"]
        f.seg = [s for s in f.seg if not (s[0] == "stand" and s[1] >= BEATS["drop"][1] + 0.6)]
        f.stand(BEATS["drop"][1] + 0.6, t0_, p0, 0.0, "stand")
        f.dive(t0_, tk, p0, nape(nm_t))
        HOOKS.append((who, t0_, p0, np.asarray(TT.nape(nm_t, tk), float)))
        q = TT.nape(nm_t, tk + 0.6); q = np.array([q[0], q[1], 0.15])
        f.follow(tk, tk + 0.6, nape(nm_t), pose="crouch").stand(tk + 0.6, BEATS["inside_gone"], q, 0.0, "stand")
        f.gone(BEATS["inside_gone"])
    for who, f in cut.items():
        if who not in ("mikasa", "annie"):
            f.gone(BEATS["inside_gone"])
    # ---------------- breakout: 12 out of the west arched door (34.0), low over the apron, up onto the wing roof
    bo = [("mikasa_b", "black", dict(scarf=True)), ("armin_b", "blond", dict(H=1.63)), ("jean_b", "jean", {}), ("reiner_b", "blond", dict(H=1.85)),
          ("bertolt_b", "dark", dict(H=1.92)), ("annie_b", "blond", dict(H=1.53)), ("sasha_b", "auburn", {}), ("connie_b", "grey", {})] + \
         [(f"b{k}", rnd.choice(["dark", "brown", "ash", "black"]), {}) for k in range(4)]
    STATE["roof_spots"] = {}
    for k, (nm, hair, kw) in enumerate(bo):
        kw.setdefault("H", H)
        f = SQ.flyer(nm, "cadet", hair, **kw)
        t0 = BEATS["breakout"] + 0.14 * k
        d = S3(DOOR[0] + rnd.uniform(-1.2, 1.2), DOOR[1] - 0.5, 0.1)
        a1 = gnd_set(-212 - 0.8 * k, 614 + rnd.uniform(-2, 2))
        rx = -228 + 1.5 * k + rnd.uniform(-0.4, 0.4); ry = 632.0 + rnd.uniform(-1, 1.5)
        rr = S3(rx, ry, wing_roof_z(ry) + 0.05)
        f.stand(t0 - 0.01, t0, d, heading_yaw(200.0), "run")
        f.walk(t0, t0 + 0.9, d, a1, "fly")                       # skims low out of the door (no hook over open paving)
        f.stand(t0 + 0.9, t0 + 1.0, a1, heading_yaw(0.0), "crouch")
        hop(f, t0 + 1.0, t0 + 2.2, a1, rr, anchor=np.array([rx + 1.0, 627.6 - segtime.SET_OFF_Y, 24.2]))
        f.stand(t0 + 2.2, 1e3, rr, heading_yaw(180.0), rnd.choice(["stand", "stand", "crouch"]))
        STATE["roof_spots"][nm] = rr
    # ---------------- Eren: out of the nape (no ODM gear, no jacket), rises 48.5-50.5
    er = SQ.flyer("eren", "cadet", "brown", gear=False, H=1.70, cloak=(0.42, 0.40, 0.29))
    def eren_p(t):
        nz = STATE.get("nape_now")
        p = S3(*nape_M(t)) if nz is None else nz
        return p + np.array([0.0, 0.0, -1.5 + 1.5 * ss(*BEATS["eren_rise"], t)])
    er.follow(BEATS["eren_rise"][0], BEATS["carry_up"][0], eren_p, yaw_fn=lambda t: heading_yaw(90.0), pose="stand")
    # ---------------- Mikasa: down the slate roof, drops in by ODM, kneels by him; carries him up to the keep roof walk
    mk = SQ.by_name["mikasa_b"]
    r0 = STATE["roof_spots"]["mikasa_b"]
    mk.seg = [s for s in mk.seg if not (s[0] == "stand" and s[2] >= 1e3)]
    t_r = BEATS["breakout"] + 2.2
    eave = S3(-190.0, 628.4, 24.0)
    rr2 = S3(-190.0, 631.5, wing_roof_z(631.5) + 0.05)
    mk.seg = [s_ for s_ in mk.seg if not (s_[0] == "stand" and s_[1] == t_r)]
    mk.stand(t_r, 45.5, r0, heading_yaw(180.0), "stand")
    mk.walk(45.5, 48.0, r0, rr2, "run")                           # along the slate roof toward the fallen titan
    mk.stand(48.0, BEATS["mikasa_run"][0], rr2, heading_yaw(160.0), "stand")
    mk.walk(BEATS["mikasa_run"][0], BEATS["mikasa_run"][1], rr2, eave, "run")   # down the slope (ep08 20:21.5)
    nape_rest = STATE["nape_rest"]
    kneel_p = nape_rest + np.array([1.1, -0.9, -0.6])
    hop(mk, BEATS["mikasa_drop"][0], BEATS["mikasa_drop"][1], eave, kneel_p, anchor=nape_rest + np.array([0.0, 0.0, 0.4]), apex=1.5)
    mk.stand(BEATS["mikasa_drop"][1], BEATS["hug"], kneel_p, heading_yaw(270.0), "stand")
    mk.stand(BEATS["hug"], BEATS["carry_up"][0], kneel_p + np.array([-0.5, 0.4, 0.0]), heading_yaw(270.0), "kneel")
    # tableau on the keep roof walk at the south parapet by the SW turret (F08/000031928): Mikasa + Eren, Armin kneeling,
    # Jean, Reiner, Bertolt, Annie standing.  Short hops: nape -> wing eave -> along the eave -> next to the keep -> the
    # spot (hook on the SW turret); every anchor on the wing roof / turret, <= 34 m.
    spot = lambda dx: S3(-259.0 + dx, 626.6, WALK_Z + 0.1)
    roofA = lambda x: S3(x, 631.0, wing_roof_z(631.0))
    c0, c1 = BEATS["carry_up"]
    p_a = kneel_p + np.array([-0.5, 0.4, 0.0])
    e1, e2, e3 = S3(-180.0, 627.6, 24.1), S3(-205.0, 627.6, 24.1), S3(-230.0, 627.6, 24.1)
    tA = c0
    for a_, b_, A_ in ((p_a, e1, roofA(-181.0)), (e1, e2, roofA(-206.0)), (e2, e3, roofA(-231.0)), (e3, spot(0.0), None)):
        dt = max(0.7, float(np.linalg.norm(b_ - a_)) / 20.0)
        hop(mk, tA, tA + dt, a_, b_, anchor=A_); tA += dt
    mk.stand(tA, DUR + 1, spot(0.0), heading_yaw(180.0), "kneel")
    STATE["tableau_t"] = tA
    er.follow(c0, tA, lambda t: SQ.by_name["mikasa_b"].state(t)["pos"] + np.array([0.5, 0.3, 0.2]),
              yaw_fn=lambda t: SQ.by_name["mikasa_b"].state(t)["yaw"], pose="stand")
    er.stand(tA, DUR + 1, spot(0.9), heading_yaw(180.0), "lie")
    for k, (nm, dx, pose) in enumerate((("armin_b", -1.0, "kneel"), ("jean_b", 2.4, "stand"), ("reiner_b", 3.6, "stand"),
                                         ("bertolt_b", 4.8, "stand"), ("annie_b", 6.0, "stand"))):
        f = SQ.by_name[nm]; rr = STATE["roof_spots"][nm]
        f.seg = [s for s in f.seg if not (s[0] == "stand" and s[2] >= 1e3)]
        t0 = c0 + 1.2 + 0.35 * k
        f.stand(BEATS["breakout"] + 2.2, t0, rr, heading_yaw(180.0), "stand")
        e = S3(-229.5 + 0.4 * k, 627.6, 24.1)
        hop(f, t0, t0 + 0.9, rr, e, anchor=roofA(-230.5))
        hop(f, t0 + 1.0, t0 + 2.4, e, spot(dx))
        f.stand(t0 + 2.4, DUR + 1, spot(dx), heading_yaw(180.0), pose)
    SQ.build(coll)
    # coordinator QA (g5 review): the wire is a THIN LIGHT-GREY line (not black), the hook head stays dark
    try:
        wm = bpy.data.materials.new("G6_ODM_wire_grey"); wm.use_nodes = True
        b = wm.node_tree.nodes["Principled BSDF"]; b.inputs["Base Color"].default_value = (*hexrgb("#b9bcc0"), 1)
        b.inputs["Roughness"].default_value = 0.6
        SQ.wob.data.materials[0] = wm
        hm = bpy.data.materials.new("G6_ODM_hook"); hm.use_nodes = True
        hm.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*hexrgb("#3a3c40"), 1)
        SQ.hob.data.materials[0] = hm
    except Exception as ex:
        say("wire material failed:", ex)
    say(f"flyers: {len(SQ.flyers)}")

# ====================================================================== smoke / steam / dust / flashes (smokecards)
def _column(C, rng, ts, base, H, alpha=0.30, rise=5.5, r=(1.0, 5.0), life=(6.0, 9.0), spread=0.08):
    """Thin wavy steam column (bible: 40-80 m ribbon columns per corpse, never an opaque blob)."""
    n = len(ts)
    if n == 0:
        return
    P_ = np.tile(base, (n, 1)) + np.column_stack([rng.normal(0, spread * H, n), rng.normal(0, spread * H, n), rng.uniform(0.3, 1.5, n)])
    V_ = np.column_stack([np.sin(ts * 0.9) * 0.9 + rng.normal(0, 0.4, n), np.cos(ts * 0.7) * 0.9 + rng.normal(0, 0.4, n), rng.uniform(rise * 0.8, rise * 1.2, n)])
    C.add_many(ts, P_, V_, r0=r[0], r1=rng.uniform(r[1] * 0.8, r[1] * 1.2, n), life=rng.uniform(*life, n), rise=1.0, kind="steam", alpha=alpha, tau=0.0)

def build_cards(coll):
    import smokecards as SC
    rng = np.random.default_rng(66)
    C = SC.SmokeCards("G6Cards")
    _am = C.add_many
    def _add_many(te, pos, vel=None, *a, **k):
        if k.get("kind") == "steam":
            c = k.get("color")
            base = np.array([0.92, 0.92, 0.90]) if c is None else np.asarray(c, float)
            k["color"] = base * np.array(STEAM_WARM)
        return _am(te, pos, vel, *a, **k)
    C.add_many = _add_many
    TT = STATE["TT"]
    # ---- town smoke columns continuing g5's 13 (pre-rolled so they stand at t 0); 9 die out 15-40 s
    for k, (x, y) in enumerate(SMOKE_SITES):
        tstop = DUR if k in SMOKE_KEEP else 15.0 + 25.0 * rng.random()
        base = S3(x, y, top_z(x, y) + 1.0)
        lean = WIND * (0.8 + 0.4 * rng.random())
        ts = np.arange(-16.0, tstop, 0.16); n = len(ts)
        C.add_many(ts, base[None, :] + rng.normal(0, 1.2, (n, 3)),
                   np.column_stack([np.sin(ts * 0.9 + k) * 1.2, np.cos(ts * 0.7 + k) * 1.2, rng.uniform(8, 11, n)]) + lean * 0.5,
                   r0=3.0, r1=rng.uniform(7.0, 10.0, n), life=rng.uniform(4.5, 5.5, n), rise=1.0, kind="smoke", alpha=1.0, tau=0.0,
                   color=hexrgb("#33312f"))
        ts = np.arange(-15.5, tstop, 0.14); n = len(ts)
        C.add_many(ts, base[None, :] + np.array([0, 0, 6.0]) + rng.normal(0, 1.5, (n, 3)),
                   np.column_stack([np.sin(ts * 0.8 + k) * 1.6, np.cos(ts * 0.6 + k) * 1.6, rng.uniform(9, 12, n)]) + lean * 0.9,
                   r0=5.0, r1=rng.uniform(13, 19, n), life=rng.uniform(12.0, 15.0, n), rise=1.0, kind="smoke", alpha=0.9, tau=0.0,
                   color=hexrgb("#6e6a64"))
        ts = np.arange(-1.0, tstop, 0.12); n = len(ts)
        C.add_many(ts, base[None, :] + rng.normal(0, 1.2, (n, 3)), np.column_stack([rng.normal(0, 0.5, n), rng.normal(0, 0.5, n), rng.uniform(3, 6, n)]),
                   r0=1.4, r1=rng.uniform(2.2, 3.4, n), life=rng.uniform(0.6, 1.0, n), rise=1.0, kind="fire", alpha=0.9, color=hexrgb("#ff8a2a"))
    # ---- Attack Titan body steam (thin, constant) while he fights; heavier on the roars
    ts = np.arange(0.0, BEATS["fall"][0], 0.11); n = len(ts)
    P_ = []
    for t in ts:
        st = at_state(t); p = st["pos"]
        P_.append(S3(p[0], p[1], G(*p) + at_z(t) + rng.uniform(6, 13)) + np.array([rng.normal(0, 1.5), rng.normal(0, 1.5), 0]))
    C.add_many(ts, np.array(P_), np.column_stack([rng.normal(0, 1, n), rng.normal(0, 1, n), rng.uniform(2, 4, n)]), r0=1.2, r1=rng.uniform(3, 5, n),
               life=rng.uniform(1.6, 2.4, n), rise=3.0, kind="steam", alpha=0.22, tau=0.6)
    # ---- kills: blade glints / impact dust + a short burst, then a thin column to the end
    ext = [("ST1", BEATS["st1_kill"], 0.7), ("F0", BEATS["r1_kill"], 1.0), ("F1", BEATS["r2_kill"], 1.0), ("F2", BEATS["f2_kill"], 1.6),
           ("F3", BEATS["f3_kill"], 1.0), ("W1", BEATS["w1_kill"], 1.0), ("B1", BEATS["biter_kills"][0], 0.7),
           ("B2", BEATS["biter_kills"][1], 0.7), ("B3", BEATS["biter_kills"][2], 0.7), ("BRD", BEATS["brd_kill"], 1.2), ("F5", BEATS["brd_hit"] + 0.05, 1.0)]
    for nm, te, k in ext:
        try:
            TT.j(nm)
        except Exception:
            continue                                            # v17: F0 / F1 removed
        Hh = TT.H[TT.j(nm)]
        p = TT.nape(nm, te - 0.02)
        n = int(18 * k)
        C.add_many(te + rng.random(n) * 0.35, np.tile(p, (n, 1)) + rng.normal(0, 0.8, (n, 3)),
                   np.column_stack([rng.normal(0, 4, n), rng.normal(0, 4, n), rng.uniform(4, 10, n)]), r0=1.0, r1=rng.uniform(3, 5, n) * k,
                   life=rng.uniform(1.6, 2.6, n), rise=3.0, kind="steam", alpha=0.75, tau=0.6)
        q = TT.pos(nm, te + 1.2)
        n = 10
        C.add_many(te + 0.3 + rng.random(n) * 0.4, np.tile(q, (n, 1)) + rng.normal(0, 1.5, (n, 3)),
                   np.column_stack([rng.normal(0, 5, n), rng.normal(0, 5, n), rng.uniform(0, 2, n)]), r0=1.5, r1=rng.uniform(4, 6, n),
                   life=rng.uniform(1.4, 2.2, n), rise=0.5, kind="dust", alpha=0.6, tau=0.5, color=hexrgb("#a89070"))
        ts = np.arange(te + 0.8, DUR, 0.13)
        _column(C, rng, ts, TT.pos(nm, te + 1.5) + np.array([0, 0, 0.5]), Hh, alpha=0.26, rise=5.0 + 0.2 * Hh, r=(1.0, 3.5 + 0.3 * Hh))
    _column(C, rng, np.arange(-6.0, DUR, 0.13), S3(CC_POS[0], CC_POS[1], 1.0), 12.0, alpha=0.26, rise=7.0, r=(1.0, 6.0))   # g5's CC corpse
    # ---- tackle landing (11.9): big beige dust burst + chips from the parapet
    tl = BEATS["tackle"][1]; c = S3(-226.0, 601.0, 1.0); n = 46
    C.add_many(tl + rng.random(n) * 0.4, np.tile(c, (n, 1)) + rng.normal(0, 3.5, (n, 3)) * np.array([1, 1, 0.3]),
               np.column_stack([rng.normal(0, 10, n), rng.normal(0, 10, n), rng.uniform(1, 6, n)]), r0=3.0, r1=rng.uniform(8, 12, n),
               life=rng.uniform(2.6, 4.0, n), rise=1.2, kind="dust", alpha=0.75, tau=0.8, color=hexrgb("#a89070"))
    p = S3(-251.0, 625.0, 29.0); n = 20
    C.add_many(BEATS["hq_punch"] + rng.random(n) * 0.3, np.tile(p, (n, 1)) + rng.normal(0, 1.2, (n, 3)),
               np.column_stack([rng.normal(0, 4, n), rng.uniform(-6, -1, n), rng.uniform(-2, 3, n)]), r0=1.2, r1=rng.uniform(3, 5, n),
               life=rng.uniform(1.6, 2.4, n), rise=-0.5, kind="dust", alpha=0.7, tau=0.6, color=hexrgb("#d6c8a8"))
    for ts_, xy in ((BEATS["r1_kill"], (-231.0, 600.5)), (BEATS["r2_kill"], (-219.0, 597.5)), (BEATS["w1_kill"], (-199.0, 592.0)),
                    (BEATS["biter_kills"][2], (-197.0, 594.5)), (BEATS["street_punch"] + 0.6, (-227.0, 574.0))):
        q = S3(xy[0], xy[1], 1.0); m = 14
        C.add_many(ts_ + rng.random(m) * 0.12, np.tile(q, (m, 1)) + rng.normal(0, 1.2, (m, 3)),
                   np.column_stack([rng.normal(0, 6, m), rng.normal(0, 6, m), rng.uniform(1, 3, m)]), r0=1.5, r1=rng.uniform(4, 6.5, m),
                   life=rng.uniform(1.3, 2.2, m), rise=0.8, kind="dust", alpha=0.65, tau=0.5, color=hexrgb("#a89070"))
    # ---- window crash-ins: tiny falling glints (glass)
    for tw, w in STATE["windows"]:
        m = 8
        C.add_many(tw + rng.random(m) * 0.2, np.tile(w, (m, 1)) + rng.normal(0, 0.6, (m, 3)),
                   np.column_stack([rng.normal(0, 2, m), rng.normal(0, 2, m), rng.uniform(-3, 1, m)]), r0=0.35, r1=0.25, life=0.45, rise=-2.0,
                   kind="glow", alpha=1.0, color=hexrgb("#e8f4ff"), fade_in=0.01)
    # ---- the VOLLEY (27.5): 28 star flashes in one 2-frame burst, then powder smoke drifting up over 4 s, sparks
    tv = BEATS["volley"]
    M_ = np.array(STATE["muzzles"]); n = len(M_)
    C.add_many(np.full(n, tv) + rng.random(n) * 0.03, M_, None, r0=0.9, r1=1.1, life=0.14, rise=0.0, kind="glow", alpha=1.0,
               color=hexrgb("#fff3c0"), fade_in=0.004)
    C.add_many(np.full(n, tv + 0.01), M_, None, r0=2.0, r1=2.4, life=0.12, rise=0.0, kind="glow", alpha=0.7, color=hexrgb("#ffb347"), fade_in=0.004)
    m = 3 * n
    C.add_many(tv + 0.04 + rng.random(m) * 0.3, np.repeat(M_, 3, axis=0) + rng.normal(0, 0.3, (m, 3)),
               np.column_stack([rng.normal(0, 0.8, m), rng.normal(0, 0.8, m), rng.uniform(0.4, 1.2, m)]), r0=0.4, r1=rng.uniform(1.2, 1.8, m),
               life=rng.uniform(3.0, 4.5, m), rise=0.6, kind="smoke", alpha=0.6, tau=0.8, color=hexrgb("#cfcac0"))
    m = 40
    C.add_many(tv + rng.random(m) * 0.4, np.repeat(M_, 2, axis=0)[:m] + rng.normal(0, 0.4, (m, 3)),
               np.column_stack([rng.normal(0, 3, m), rng.normal(0, 3, m), rng.uniform(0, 3, m)]), r0=0.12, r1=0.08, life=0.5, rise=-3.0,
               kind="glow", alpha=1.0, color=hexrgb("#ffc860"), fade_in=0.01)
    # ---- storeroom cuts: blade streaks + steam rising out of the open bay (columns end as the roof returns)
    cuts = [(nm, BEATS["drop"][1]) for nm in ("S0", "S1", "S2", "S3", "S4")] + [(nm, FINISH[nm][1]) for nm in FINISH]
    for nm, te in cuts:
        p = TT.nape(nm, te - 0.02)
        C.add_many(te + np.array([0.0, 0.05]), np.tile(p, (2, 1)), None, r0=0.7, r1=0.8, life=0.16, rise=0.0, kind="glow", alpha=1.0,
                   color=hexrgb("#cfe8ff"), dirs=np.array([[1.0, 0.4, 0.6], [1.0, -0.5, 0.3]]), stretch=4.0, fade_in=0.01)
        C.add_many(te + 0.1 + rng.random(8) * 0.4, np.tile(p, (8, 1)) + rng.normal(0, 0.4, (8, 3)),
                   np.column_stack([rng.normal(0, 1, 8), rng.normal(0, 1, 8), rng.uniform(2, 4, 8)]), r0=0.5, r1=1.6, life=1.8, rise=2.5,
                   kind="steam", alpha=0.7, tau=0.5)
        _column(C, rng, np.arange(te + 0.5, BEATS["cut_close"][0] - 0.5, 0.15), TT.pos(nm, te + 1.0), 3.5, alpha=0.3, rise=5.0, r=(0.6, 2.6),
                life=(3.0, 5.0))
    # nape cuts outside (glints only, the AT kills have no blades) - none
    # ---- the breakout: a dust puff at the west door (17:34.1)
    q = S3(DOOR[0], DOOR[1] - 2.0, 1.5); n = 22
    C.add_many(BEATS["breakout"] + rng.random(n) * 0.6, np.tile(q, (n, 1)) + rng.normal(0, 1.0, (n, 3)),
               np.column_stack([rng.normal(0, 2, n), rng.uniform(-7, -2, n), rng.uniform(0, 2, n)]), r0=1.2, r1=rng.uniform(3, 5, n),
               life=rng.uniform(1.5, 2.5, n), rise=0.6, kind="dust", alpha=0.65, tau=0.6, color=hexrgb("#a89070"))
    # ---- the collapse: beige dust bow wave along the skid (owner wing ref), steam white-out, then 6-8 columns + embers
    s0, s1 = BEATS["skid"]
    ts = np.arange(BEATS["fall"][1] - 0.05, s1 + 0.2, 0.025); n = len(ts)
    P_ = np.array([S3(at_state(t)["pos"][0] + NAPE_OFF[0] + 1.5, 619.0, 0.0) for t in ts]) + np.column_stack(
        [rng.normal(0, 2.0, n), rng.normal(0, 4.0, n), rng.uniform(0.5, 4, n)])
    C.add_many(ts, P_, np.column_stack([rng.uniform(4, 12, n), rng.normal(0, 7, n), rng.uniform(1, 6, n)]), r0=3.0, r1=rng.uniform(8, 14, n),
               life=rng.uniform(3.0, 4.6, n), rise=1.0, kind="dust", alpha=0.9, tau=0.9, color=hexrgb("#9c8466"))
    ts = np.arange(s0, s1 + 0.4, 0.02); n = len(ts)
    P_ = np.array([S3(at_state(t)["pos"][0] + rng.uniform(0, NAPE_OFF[0] + 2), 619.0 + rng.normal(0, 3), 0.5) for t in ts])
    C.add_many(ts, P_, np.column_stack([rng.normal(0, 5, n), rng.normal(0, 5, n), rng.uniform(0.5, 3, n)]), r0=2.0, r1=rng.uniform(5, 9, n),
               life=rng.uniform(2.0, 3.0, n), rise=0.5, kind="dust", alpha=0.8, tau=0.6, color=hexrgb("#a08a6a"))
    body = [S3(-191.5 + u, 619.0, 1.5) for u in np.linspace(0.0, NAPE_OFF[0] + 1.0, 8)]
    w0, w1 = BEATS["whiteout"]
    # QA 10/27: no single white ball over the body.  g5 v2 steam approach: many smaller warm-tinted cards released
    # continuously from the body's EDGES, thrown outward low (12-34 m/s, small elevation), rising and drifting, each thinning
    # over 3.4-4.6 s; release rate tails off from ~49.5 so the shroud is thinning by ~50 and the body / nape stay readable.
    n = 460
    tt = w0 - 0.5 + rng.random(n) ** 1.7 * (w1 + 2.0 - w0)              # dense at the impact, tailing off by ~50.5
    along = rng.uniform(-1.0, NAPE_OFF[0] + 2.0, n); side = rng.choice([-1.0, 1.0], n)
    th = rng.normal(0.0, 0.55, n) + np.where(side > 0, math.pi / 2, -math.pi / 2)   # mostly N / S of the body, some along it
    el = rng.uniform(0.04, 0.45, n); spd = rng.uniform(12, 34, n)
    dirs = np.column_stack([np.cos(th) * np.cos(el) * 0.55, np.sin(th) * np.cos(el), np.sin(el)])
    P_ = np.column_stack([np.full(n, -191.5) + along, np.full(n, 619.0 - segtime.SET_OFF_Y) + side * rng.uniform(3.0, 5.0, n),
                          rng.uniform(0.8, 3.5, n)])
    C.add_many(tt, P_, dirs * spd[:, None] + np.array([0.0, 0.0, 2.5]), r0=2.5, r1=rng.uniform(7, 12, n),
               life=rng.uniform(3.4, 4.6, n), rise=3.0, kind="steam", alpha=0.30, tau=1.4, color=hexrgb("#f7f3ec"))
    n = 140                                                                 # a lower, slower skirt that rolls along the paving
    tt = w0 - 0.3 + rng.random(n) ** 1.4 * 4.5
    P_ = np.column_stack([-191.5 + rng.uniform(-2, NAPE_OFF[0] + 3, n), (619.0 - segtime.SET_OFF_Y) + rng.choice([-1.0, 1.0], n) * rng.uniform(3.5, 7.0, n), rng.uniform(0.3, 1.5, n)])
    C.add_many(tt, P_, np.column_stack([rng.normal(0, 8, n), rng.normal(0, 10, n), rng.uniform(0.5, 2.5, n)]), r0=3.0, r1=rng.uniform(8, 13, n),
               life=rng.uniform(3.4, 4.6, n), rise=1.5, kind="steam", alpha=0.26, tau=1.2, color=hexrgb("#efe8dc"))
    for i, b in enumerate(body):                                          # 8 columns from the body to the end, thinning
        ts = np.arange(w0, DUR, 0.18 if i % 2 else 0.26)
        _column(C, rng, ts, b, 12.0, alpha=0.36, rise=6.5, r=(1.5, 5.5), life=(6.0, 9.0), spread=0.06)
    ts = np.arange(w0 - 0.2, 62.0, 0.05); n = len(ts)
    C.add_many(ts, np.array([body[i % len(body)] for i in range(n)]) + rng.normal(0, 3, (n, 3)),
               np.column_stack([rng.normal(0, 1.5, n), rng.normal(0, 1.5, n), rng.uniform(3, 7, n)]), r0=0.25, r1=0.18,
               life=rng.uniform(1.5, 3.0, n), rise=1.5, kind="glow", alpha=0.9, color=hexrgb("#ffb060"), fade_in=0.2)
    C.build(coll)
    STATE["cards"] = C
    say(f"smoke cards: {C.count()}")

# ====================================================================== storeroom lights (warm torches, cage lantern, volley spike)
def build_lights(coll):
    """Warm storeroom light while the bay is open (QA 10/27: brighter so the lift and the volley read): 3 torch-height
    fills, a broad warm 'light from the hole' above the open bay (custom distance so it stays local), and the cage lantern
    (+ the 2-frame volley spike).  No shadows: the sun is kept out by the shadow proxy, these only add warmth inside."""
    L_ = []
    for k, (x, y, z, e, d, r) in enumerate(((-199, 636, 3.0, 480.0, 16.0, 0.4), (-187, 646, 3.0, 420.0, 16.0, 0.4),
                                             (-175, 636, 3.0, 480.0, 16.0, 0.4), (-187, 640, 13.0, 3600.0, 22.0, 3.0),
                                             (-187, 641, 4.4, 0.0, 30.0, 0.4))):
        ld = bpy.data.lights.new(f"G6_StoreLight{k}", "POINT"); ld.color = hexrgb("#ffb070" if k == 3 else "#ff9a40"); ld.energy = 0.0
        for a_, v_ in (("shadow_soft_size", r), ("use_shadow", False), ("use_custom_distance", True), ("cutoff_distance", d)):
            try:
                setattr(ld, a_, v_)
            except Exception:
                pass
        o = bpy.data.objects.new(f"G6_StoreLight{k}", ld); coll.objects.link(o); o.location = SV(x, y, z)
        L_.append((o, e))
    STATE["lights"] = L_

def update_lights(t):
    c = cut_frac(t)
    for k, (o, e) in enumerate(STATE["lights"]):
        if k < 4:
            o.data.energy = e * c
        else:                                                  # the cage lantern + the volley spike (2 frames, 2,000 W)
            o.location = SV(LIFT_C[0], LIFT_C[1], cage_z(t) + 3.6)
            sp = bump(t, BEATS["volley"] - 0.01, BEATS["volley"], BEATS["volley"] + 0.1, BEATS["volley"] + 0.16)
            o.data.energy = (150.0 * c + 2000.0 * sp) if c > 0 else 0.0

# ====================================================================== build / update (contract)
def build(site):
    t0 = time.time()
    STATE["site"] = site; STATE["TR"] = site["TR"]; STATE["L"] = site["L"]
    TR = STATE["TR"]
    coll = _coll("G6")
    bpy.context.view_layer.update()
    for xy in SMOKE_SITES:
        top_z(*xy)
    for fn, args in (("set_breach", (True,)), ("set_glow", (0.25,)), ("set_hq_cutaway", (0.0,)), ("set_hq_lift", (0.0,))):
        try:
            getattr(TR, fn)(*args)
        except Exception as ex:
            say(fn, "failed:", ex)
    try:                                       # g5 leaves the cart at its end state
        TR.set_wagon(True); TR.set_cart("end")
    except Exception as ex:
        say("cart hooks failed:", ex)
    try:                                       # seam g5|g6 (master v1 QA): the same set edits as g5 v3 - the Q2 dome /
        import seg_g5                          # drum -> 3.4 m well, and the 8 houses N of SS removed for the alley view
        seg_g5.STATE.setdefault("L", STATE["L"]); seg_g5.STATE.setdefault("TR", TR)
        seg_g5.fix_q2_dome(coll)
        seg_g5.clear_lots()
        seg_g5.STATE.setdefault("site", site)               # tower T as g5 leaves it: top burst off (65.5), blocks
        seg_g5.build_tower_burst(coll)                      # landed round its foot, grind scar on the shaft (static here)
        seg_g5.update_tower(segtime.DUR["g5"] + 30.0)
        say("g5 end state: Q2 well, cleared lots, tower T burst")
        bpy.context.view_layer.update(); _RC.clear()
    except Exception as ex:
        say("g5 set edits (Q2 well / cleared lots) failed:", ex)
    build_titans(coll)
    build_attack(coll)
    _pose_attack(BEATS["eren_rise"][0])
    STATE["nape_rest"] = _nape_from_bone()
    nm = STATE["nape_rest"]
    say(f"prone nape (M) {tuple(round(v, 1) for v in (nm[0], nm[1] + segtime.SET_OFF_Y, nm[2]))} (bible {EREN_NAPE})")
    STATE.pop("nape_now", None)
    build_people(coll)
    build_cards(coll)
    build_lights(coll)
    _light_capture()
    say(f"build {time.time() - t0:.1f}s")

def finish():
    """QA 10/27: the bay fade showed as grey dithered (hashed) noise.  Install trost's cut materials now (after toon) and
    switch them to a clean alpha BLEND (no overlap sorting noise); the fade itself is shortened to ~1.2 s."""
    TR = STATE["TR"]
    try:
        for n in TR.HQ_UPPER:
            o = bpy.data.objects.get(n)
            if o is None:
                continue
            TR._install_cut(o)
            for slot in o.material_slots:
                m = slot.material
                if m is None or not m.name.startswith("Cut_"):
                    continue
                for a_, v_ in (("use_transparency_overlap", False), ("use_backface_culling", True)):
                    try:
                        setattr(m, a_, v_)
                    except Exception:
                        pass
                STATE.setdefault("cut_mats", []).append(m)
        say(f"bay cutaway: clean alpha blend while fading ({len(STATE.get('cut_mats', []))} materials)")
    except Exception as ex:
        say("cutaway blend setup failed:", ex)

def update(tv):
    tv = float(tv)
    t = T_old(tv)
    TR = STATE["TR"]
    try:
        TR.set_hq_cutaway(cut_frac(t))
        TR.set_hq_lift((CAGE_Z[0] - cage_z(t)) / (CAGE_Z[0] - CAGE_Z[1]))
    except Exception as ex:
        if not STATE.get("hq_warned"):
            say("HQ hooks failed:", ex); STATE["hq_warned"] = True
    fading = 0.0 < cut_frac(t) < 0.999                    # blended only while fading (opaque roof sorts normally vs the steam)
    if STATE.get("cut_blend") != fading:
        for m in STATE.get("cut_mats", []):
            try:
                m.surface_render_method = "BLENDED" if fading else "DITHERED"
            except Exception:
                pass
        STATE["cut_blend"] = fading
    try:
        TR.set_glow(0.25 * (1 - ss(0.0, 20.0, t)))
    except Exception:
        pass
    if t < BEATS["skid"][1] - 0.1:
        STATE.pop("nape_now", None)
    _pose_attack(t)
    STATE["TT"].update(t)
    try:
        STATE["SQ"].update(t)
    except TypeError:
        STATE["SQ"].update(t + 1e-4)
    STATE["cards"].update(t, wind=(WIND[0], WIND[1]))
    update_lights(t)

def cam_shake(tv):
    p = y = 0.0
    for ts, a, d in SHAKES:
        if ts <= tv < ts + d:
            u = (tv - ts) / d; e = a * (1 - u) ** 2
            p += e * math.sin(tv * 63.0); y += e * 0.7 * math.sin(tv * 51.0 + 1.3)
    return p, y

# ---------------------------------------------------------------------- light (sun, sky, exposure) - one key table (VIDEO clock)
# t: sun elevation (deg), compass azimuth (deg), sun energy, sun rgb, zenith rgb, horizon rgb, world strength
# 0 = g5's end (breaking overcast); clearing to a bright blue afternoon with cumulus (ep08 09:16+); warm gold 27 deg, az 250
# at the g7 hand-off (bible g7: golden light 255).
LIGHT_KEYS = [
    (0.0,  49.0, 143, 2.1, (1.00, 0.92, 0.80), (0.33, 0.42, 0.56), (0.70, 0.70, 0.68), 0.90),   # = g5 70.0
    (12.0, 45.0, 168, 2.8, (1.00, 0.95, 0.88), (0.22, 0.37, 0.64), (0.70, 0.76, 0.84), 0.96),   # clearing
    (30.0, 40.0, 205, 3.3, (1.00, 0.96, 0.90), (0.13, 0.31, 0.72), (0.72, 0.80, 0.92), 1.00),   # bright afternoon
    (48.0, 33.0, 232, 3.1, (1.00, 0.89, 0.72), (0.16, 0.32, 0.66), (0.80, 0.78, 0.74), 0.96),   # warming
    (69.5, 27.0, 250, 2.8, (1.00, 0.84, 0.62), (0.18, 0.31, 0.60), (0.86, 0.76, 0.62), 0.92),   # warm gold
]
GRADE_KEYS = [
    (0.0,  (1.01, 0.98, 0.93), -0.25),       # = g5 70.0
    (12.0, (1.00, 0.99, 0.97), -0.10),
    (30.0, (1.00, 1.00, 1.00), 0.00),
    (48.0, (1.02, 0.99, 0.94), -0.04),
    (69.5, (1.04, 0.98, 0.89), -0.08),
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
    t = float(tv)
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

# ====================================================================== HUD trackers (M) + self checks
def _p_set_to_M(p):
    return (float(p[0]), float(p[1]) + segtime.SET_OFF_Y, float(p[2]))

def _sq(name, t0=-1e9, t1=1e9):
    def f(t):
        if not (t0 <= t < t1): return None
        st = STATE["SQ"].state(name, t)
        return _p_set_to_M(st["pos"] + np.array([0, 0, 2.0])) if st["vis"] > 0 else None
    return f

def _mikasa(t):
    if t < BEATS["trio"][1]: return _sq("mikasa_a")(t)
    if t < BEATS["inside_gone"]: return _sq("mikasa")(t)
    return _sq("mikasa_b")(t)

def _armin(t):
    if t < BEATS["trio"][1]: return _sq("armin_a")(t)
    if t < BEATS["breakout"]: return None
    return _sq("armin_b")(t)

def _at_head(t):
    if t >= BEATS["fall"][0]: return None
    st = at_state(t)
    return (float(st["pos"][0]), float(st["pos"][1]), 16.0 + at_z(t))

_TRACK0 = {"AttackTitan": _at_head, "Eren": lambda t: _sq("eren")(t) if t >= BEATS["eren_rise"][0] else None,
           "Mikasa": _mikasa, "Armin": _armin, "Jean": lambda t: _sq("jean")(t) if t < 4.5 else None}
TRACK = {k: (lambda f: (lambda tv: f(T_old(tv))))(f) for k, f in _TRACK0.items()}

def check():
    """Self checks: the AT hand-off from g5 (position / heading / speed at 0), the prone nape vs the bible anchor, every
    hook anchor <= HOP_MAX from its soldier, the titans staying out of the storeroom (AT outside), the camera seams."""
    st = at_state(0.0); v = at_vel(0.0, 0.04)
    hd = (math.degrees(math.atan2(v[0], v[1])) + 360) % 360
    say(f"CHECK AT at 0: pos {tuple(np.round(st['pos'], 2))} heading {hd:.0f} deg speed {np.linalg.norm(v):.2f} m/s "
        f"(g5 end: {SEAM5['pos']} {SEAM5['heading']} deg {SEAM5['v']} m/s)")
    n = nape_M(DUR)
    say(f"CHECK prone nape (pure) {tuple(np.round(n, 1))} vs bible {EREN_NAPE}")
    if "nape_rest" in STATE:
        q = STATE["nape_rest"]; say(f"CHECK prone nape (bone) {(round(q[0], 1), round(q[1] + segtime.SET_OFF_Y, 1), round(q[2], 1))}")
    worst = max(((float(np.linalg.norm(A - (p0 + np.array([0, 0, 0.9])))), nm, t0) for nm, t0, p0, A in HOOKS), default=(0, "", 0))
    bad = [(nm, round(t0, 2), round(float(np.linalg.norm(A - (p0 + np.array([0, 0, 0.9])))), 1)) for nm, t0, p0, A in HOOKS
           if np.linalg.norm(A - (p0 + np.array([0, 0, 0.9]))) > HOP_MAX + 0.5]
    say(f"CHECK hooks: {len(HOOKS)}, longest wire {worst[0]:.1f} m ({worst[1]} @ {worst[2]:.2f}); over {HOP_MAX} m: {bad[:8]}")
    ins = [round(t, 1) for t in np.arange(0, DUR, 0.25) if BAY[0] - 2 < at_state(t)["pos"][0] < BAY[1] + 2 and BAY[2] - 1 < at_state(t)["pos"][1] < BAY[3]]
    say(f"CHECK AT inside the storeroom footprint: {len(ins)} samples {ins[:5]}")
    for nm, tt in (("g5_g6", 0.0), ("g6_g7", DUR)):
        s = segtime.seam(nm); loc, look, lens = CAM.eval(tt); vv = CAM.vel(min(max(tt, 0.01), DUR - 0.01))
        say(f"CHECK seam {nm}: pos {tuple(np.round(loc, 2))} vs {s['pos']} | look {tuple(np.round(look, 2))} vs {s['look']} | "
            f"lens {lens:.2f} vs {s['lens']} | vel {tuple(np.round(vv, 2))} vs {s['vel']}")

if __name__ == "__main__":
    r = camchan.check(CAM, 0.0, DUR, limits=dict(name="g6 CAM", **CAM_LIMITS))
    for t in (0.0, 0.5, 2.6, 6.6, 11.9, 45.0):
        s = at_state(t); print(t, np.round(s["pos"], 2), s["mode"], np.round(at_vel(t), 2))
