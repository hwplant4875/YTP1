"""f1 KARANES -> FORMATION -> FEMALE TITAN -> REINER -> VILLAGE -> GREEN SMOKE (bible beats f1-f6, forest set, frame W).
v2 (QA batch1 P0): 26 s of VIDEO (DUR) remapped onto the 48 s story choreography (TMAP / story()); beat times below are STORY
seconds.  Camera keys are video time, low oblique (200-350 m) so riders and the Female read; flares are smoke columns.
SEG=f1 bash aot/forest/render_part2.sh     (camera / layout in frame F, converted with common.F)

  0-8    the Karanes gate opens; the 57th expedition pours out in a column past the ruined old town; the support squad flies
         (ODM) at a 10 m titan near the old town and cuts its nape (6.6-7.4)
  7.5-14 the column fans out into the long-distance scouting formation (dome ~800 m, outer arch + inner arch, command line,
         Levi squad at the rear centre, supply wagons rear right), seen from a true overhead; red smoke relayed from the right wing
  14-26  the Female Titan comes in from the RIGHT flank on a dust trail, wipes the right-wing scouts, kneels and lifts Armin's
         hood (push-in), spares him, runs inward
  26-34  Armin (remounted), Jean and Reiner ride at her; she grabs REINER in her fist (slight zoom), he cuts free, she turns
         at once toward the centre; purple smoke
  34-40  she runs through the windmill village, houses collapse
  40-48  green smoke from the command line (course change): the formation races for the forest; canopy reveal = f2 frame 0
Riders are TRUE scale (dots with dust streaks from the overhead); the Female is shifters.make_female (14 m).
"""
import math, os, sys, random
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from forest import common as C
import camchan
try:
    import bpy
    from mathutils import Vector
except ImportError:
    bpy = None

STORY_DUR = 48.0          # the choreography below runs on STORY time (bible beats f1-f6)
DUR = 28.0                # v8 (FEEDBACK_v13 §2): video time, remapped onto story time by story(t); FLAT knots = frozen tableaux
# v8: formation graphic (EP17 06:21-06:25) from a far sky view 3.0-8.5, left flank 8.5-9.6, fast pan right, then FROZEN
# tableaux (forest.tableau): ram + wire yank (EP17 10:13), hood, palm (EP17 21:38), fire-can spin (EP18 10:59)
TMAP = [(0.0, 0.0), (3.0, 8.0), (8.5, 14.0), (10.2, 18.0), (12.6, 18.0), (13.0, 20.8), (15.2, 20.8), (15.6, 31.6),
        (17.8, 31.6), (18.6, 36.5), (21.8, 36.5), (28.0, 48.0)]
TAB = dict(graphic=(3.4, 8.3), ram=(10.2, 12.6), hood=(13.0, 15.2), palm=(15.6, 17.8), spin=(18.6, 21.8))
TAB_STORY = dict(ram=18.0, hood=20.8, palm=31.6, spin=36.5)
TAB_POSE = dict(ram="ram", hood="hood", palm="palm", spin="swing")
def story(t):
    return float(np.interp(t, [k[0] for k in TMAP], [k[1] for k in TMAP]))
def video(ts):          # first video time at story ts (frozen knots: the start of the hold)
    for (v0, s0), (v1, s1) in zip(TMAP, TMAP[1:]):
        if s0 <= ts <= s1 and s1 > s0:
            return v0 + (v1 - v0) * (ts - s0) / (s1 - s0)
    return TMAP[-1][0]
BEATS = dict(gate=(0.5, 2.0), out=1.2, support_kill=(6.6, 7.4), dome=(7.5, 13.0), red=(12.0, 13.2), female_in=14.0,
             wipe=(16.8, 19.8), hood=(20.0, 22.0), chase=(26.0, 34.0), grab=(29.0, 30.6), free=30.6, purple=27.0,
             village=(34.0, 40.0), green=40.5, rush=(40.0, 48.0))
F = C.F

# ---------------------------------------------------------------- dome centre (frame F) and the column
DC = [(7.0, 640.0, -8250.0), (8.0, 600.0, -8000.0), (11.0, 470.0, -6900.0), (14.0, 420.0, -5800.0), (20.0, 410.0, -5560.0),
      (26.0, 405.0, -5330.0), (34.0, 400.0, -5030.0), (40.0, 400.0, -4800.0), (44.0, 300.0, -2900.0), (48.0, 40.0, -300.0),
      (52.0, 0.0, 700.0)]
def dc(t):
    x, y, _ = C.path_at(DC, t)
    return x, y

_ROAD = {}
def road():
    if "d" not in _ROAD:
        from forest import layout
        pts = []
        R = layout.ROAD_F
        P = [R[0]] + list(R) + [R[-1]]
        for i in range(1, len(P) - 2):
            p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
            n = max(1, int(math.hypot(p2[0] - p1[0], p2[1] - p1[1]) / 10.0))
            for k in range(n):
                u = k / n
                pts.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * u + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * u * u
                                        + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * u ** 3) for j in range(2)))
        pts = np.array(pts)
        s = np.concatenate([[0.0], np.cumsum(np.hypot(*np.diff(pts, axis=0).T))])
        _ROAD["d"] = (pts, s)
    return _ROAD["d"]

def road_at(s):
    pts, S = road()
    if s <= 0:
        d = pts[1] - pts[0]; d = d / np.linalg.norm(d)
        return pts[0] + d * s, math.atan2(-d[0], d[1])
    i = min(len(S) - 2, int(np.searchsorted(S, s) - 1)); i = max(0, i)
    u = (s - S[i]) / max(1e-6, S[i + 1] - S[i])
    d = pts[i + 1] - pts[i]
    return pts[i] + d * u, math.atan2(-d[0], d[1])

_HS = np.arange(0.0, STORY_DUR + 4, 0.02)
_HV = np.where(_HS < 1.2, 0.0, np.where(_HS < 2.6, 20.0, 20.0 + 280.0 * np.clip((_HS - 2.6) / 5.4, 0, 1) ** 2 * (3 - 2 * np.clip((_HS - 2.6) / 5.4, 0, 1))))
_HX = np.concatenate([[0.0], np.cumsum(_HV[:-1] * 0.02)])
def head_s(t):
    return float(np.interp(t, _HS, _HX)) - 12.0           # 12 m inside the gate at the start
GAP = 7.0

# ---------------------------------------------------------------- formation roster
def roster():
    rnd = random.Random(57)
    R = []
    def add(group, dx, dy, name=None, kind="rider"):
        R.append(dict(group=group, slot=(dx, dy), name=name, kind=kind, tb=7.5 + 3.0 * rnd.random(), kill=None, j=None))
    add("command", 0, 150, "erwin")
    for k in range(4):
        add("command", (-1) ** k * (6 + 4 * (k // 2)), 145 - 6 * (k // 2))
    for a in np.linspace(-100, 100, 15):                    # outer arch: 15 squads x 3
        for m in range(3):
            r = 400 + 8 * m
            add("rightwing" if a > 55 else "arch", r * math.sin(math.radians(a)) + 5 * m, r * math.cos(math.radians(a)) - 6 * m)
    for a in np.linspace(-80, 80, 9):                       # inner arch: 9 squads x 2
        for m in range(2):
            add("inner", 250 * math.sin(math.radians(a)) + 4 * m, 250 * math.cos(math.radians(a)) - 5 * m)
    for k in range(6):                                      # relay line down the centre
        add("relay", 0, 90 - 70 * k)
    for k, nm in enumerate(("levi", "eren", "petra", "oluo", "gunther", "erd")):
        add("levi", (-4, 4, -4, 4, -8, 8)[k], -330 - 5 * (k // 2), nm)
    for k in range(8):
        add("wagon", 150 + 18 * (k % 2), -230 - 26 * (k // 2), kind="wagon")
    for nm, sl in (("armin", (330, -60)), ("jean", (300, -40)), ("reiner", (310, -90))):
        add("named", sl[0], sl[1], nm, kind="horse")
    return R
ROSTER = roster()
NAMED = {r["name"]: r for r in ROSTER if r["name"]}

def col_pos(k, t):
    s = head_s(t) - k * GAP
    p, yaw = road_at(s)
    return (float(p[0]), float(p[1])), yaw, s

def base_pos(r, t):
    """rider r's planned F position (column -> dome blend), no events."""
    k = ROSTER.index(r)
    (cx, cy), _, s = col_pos(k, t)
    if t <= r["tb"]:
        return cx, cy, s
    x, y = dc(t)
    dx, dy = r["slot"]
    wob = 6.0 * math.sin(0.4 * t + k)
    u = C.ss(r["tb"], r["tb"] + 3.2, t)
    return cx + (x + dx + wob - cx) * u, cy + (y + dy - cy) * u, s

# ---------------------------------------------------------------- the Female (dome-relative path, F)
FREL = [(14.0, 1500.0, 450.0), (15.5, 900.0, 160.0), (17.0, 450.0, -40.0), (18.4, 400.0, -70.0), (19.6, 370.0, -85.0),
        (20.0, 362.0, -88.0), (22.0, 362.0, -164.0), (24.0, 270.0, -150.0), (26.0, 190.0, -132.0), (29.0, 140.0, -122.0),
        (30.6, 120.0, -115.0), (32.0, 150.0, -40.0), (34.0, 200.0, 30.0), (36.0, 250.0, 70.0), (38.0, 225.0, 40.0),
        (40.0, 80.0, -150.0), (44.0, 0.0, -360.0), (48.0, 0.0, -430.0), (52.0, 0.0, -450.0)]
def female_F(t):
    x, y = dc(t)
    rx, ry, _ = C.path_at(FREL, t)
    return x + rx, y + ry

def female_state(t):
    """(F x, y, yaw, mode, weights for blend)"""
    x, y = female_F(t)
    x2, y2 = female_F(t + 0.05); x1, y1 = female_F(t - 0.05)
    yaw = C.yaw_of(x2 - x1, y2 - y1)
    if 20.0 <= t < 22.0 or 29.0 <= t < 30.6:
        # kneel facing Armin / grab: keep the heading she arrived with
        yaw = female_state(19.95 if t < 22.0 else 28.95)[2]
    return x, y, yaw

def female_mode(t):
    """pose dict + z offset for time t."""
    run = C.fem_run(2 * math.pi * 2.8 * t)                 # constant cadence (time-lapse speeds vary 40-500 m/s)
    ws = {}
    if t < 19.6 or 22.6 <= t < 28.6 or t >= 31.2:
        P = run
        for ts in SWATS:                                      # quick swats through the right wing and the village
            w = C.bump(t, ts - 0.25, ts - 0.05, ts + 0.15, ts + 0.4)
            if w > 0:
                P = C.fpose_blend(P, C.FPOSE["swat"], w)
        return P, 0.0
    if t < 22.6:                                              # slow -> kneel, lift the hood -> rise
        w = C.ss(19.6, 20.2, t) * (1 - C.ss(22.0, 22.6, t))
        P = C.fpose_blend(run, C.FPOSE["kneel"], w)
        return P, C.FZ["kneel"] * w
    w = C.ss(28.6, 29.0, t) * (1 - C.ss(30.8, 31.2, t))      # grab Reiner, hold, he cuts free
    P = C.fpose_blend(run, C.FPOSE["reach"] if t < 29.2 else C.FPOSE["hold"], w)
    return P, 0.0
SWATS = (17.3, 18.1, 18.9, 19.5, 36.0, 37.2)

_FD = {}
def _fdist(t):
    if "T" not in _FD:
        T = np.arange(13.0, STORY_DUR + 2.0, 0.02)
        P = np.array([female_F(x) for x in T])
        D = np.concatenate([[0.0], np.cumsum(np.hypot(*np.diff(P, axis=0).T))])
        _FD["T"], _FD["D"] = T, D
    return float(np.interp(t, _FD["T"], _FD["D"]))

# kills: right-wing riders the Female passes within 22 m of during the wipe
def _kills():
    for r in ROSTER:
        if r["group"] != "rightwing":
            continue
        for t in np.arange(BEATS["wipe"][0], BEATS["wipe"][1], 0.05):
            fx, fy = female_F(t); x, y, _ = base_pos(r, t)
            if math.hypot(fx - x, fy - y) < 80.0:
                r["kill"] = float(t); break
_kills()

# named riders: Armin knocked down at 19.8 (stands by her hand 20-22.6, remounts 24.5), Jean and Reiner ride in from 23;
# 26-34 they ride abreast of her; Reiner grabbed 29.0-30.6, cut free, back on his horse 31.4
def named_F(name, t):
    r = NAMED[name]
    bx, by, _ = base_pos(r, t)
    if name == "armin":
        if t < 19.4:
            return bx, by, "seated"
        if t < 24.5:
            hx, hy = female_F(19.95); fy = female_state(19.95)[2]
            ax, ay = hx - 9.0 * math.sin(fy), hy + 9.0 * math.cos(fy)        # in front of her
            return ax, ay, "stand"
        fx, fy = female_F(t)
        u = C.ss(24.5, 26.0, t)
        hx, hy = female_F(19.95); f0 = female_state(19.95)[2]
        ax, ay = hx - 9.0 * math.sin(f0), hy + 9.0 * math.cos(f0)
        return ax + (fx - 34 - ax) * u, ay + (fy + 10 - ay) * u, "seated"
    if t < 23.0:
        return bx, by, "seated"
    fx, fy = female_F(t)
    off = {"jean": (-30.0, 14.0), "reiner": (24.0, 26.0)}[name]
    u = C.ss(23.0, 26.0, t)
    return bx + (fx + off[0] - bx) * u, by + (fy + off[1] - by) * u, "seated"

# ---------------------------------------------------------------- camera (F keys -> W)
def _k(t, p, l, lens):
    return (t, F(*p), F(*l), lens)
from seg_f0 import SEAM_F1_W
SEAM_F2 = dict(pos=(140.0, -900.0, 260.0), look=(0.0, 0.0, 60.0), lens=30.0, vel=(-10.0, 120.0, -10.0))
def _rel(t, look_t, d, lens, dz=8.0, look=None):
    lx, ly = look if look is not None else female_F(look_t)
    return _k(t, (lx + d[0], ly + d[1], d[2]), (lx, ly, dz), lens)
def _armin_spot():
    hx, hy = female_F(19.95); fy = female_state(19.95)[2]
    return hx - 9.0 * math.sin(fy), hy + 9.0 * math.cos(fy)
def _v(ts, key):
    return (video(ts),) + tuple(key[1:])
def _dk(t, ts, d, l, lens):
    x, y = dc(ts)
    return _k(t, (x + d[0], y + d[1], d[2]), (x + l[0], y + l[1], 0.0), lens)
CAM_KEYS = [   # v8 (FEEDBACK_v13 §2): video-time fly keys (z above ground); the frozen tableau shots are added in build()
    (0.0, SEAM_F1_W["pos"], SEAM_F1_W["look"], SEAM_F1_W["lens"]),
    _k(1.4, (-60.0, -9450.0, 220.0), (300.0, -9000.0, 10.0), 32.0),           # the gate opens, the first riders burst out
    _k(3.0, (498.0, -8332.0, 180.0), (600.0, -8050.0, 0.0), 32.0),            # the column fans out past the old town
    _dk(4.8, 9.9, (-520.0, -1500.0, 1150.0), (0.0, 120.0), 28.0),             # FAR SKY VIEW: the formation + its graphic
    _dk(8.1, 13.9, (-430.0, -1380.0, 1050.0), (40.0, 140.0), 28.0),           # (titan on the right -> the arrow veers left)
    _dk(9.0, 15.2, (-560.0, -130.0, 70.0), (-400.0, 50.0), 34.0),             # graphic off: the LEFT flank (the right is hidden)
    _dk(9.7, 16.9, (-530.0, -90.0, 75.0), (-360.0, 80.0), 34.0),
    _dk(24.1, 40.8, (-60.0, -560.0, 380.0), (40.0, 80.0), 30.0),               # green smoke from the command line
    _k(26.3, (350.0, -3250.0, 480.0), (160.0, -1300.0, 40.0), 28.0),          # crane forward: the forest wall
    _k(DUR, SEAM_F2["pos"], SEAM_F2["look"], SEAM_F2["lens"]),
]
CAM = camchan.CamPath(CAM_KEYS, v_in=SEAM_F1_W["vel"], v_out=SEAM_F2["vel"])
CAM_LIMITS = dict(speed=4000.0, yaw=400.0, hmin=8.0, hmax=1400.0, pitch=(3.0, 90.0), lens=(23.0, 46.0))

def _front_az(ts):
    return math.degrees(female_state(ts)[2]) + 90.0

def _shots():
    from forest import tableau as TB
    def tgt(ts, dz, look=None):
        x, y = look if look is not None else female_F(ts)
        return _W(x, y, dz)
    a = {k: _front_az(v) for k, v in TAB_STORY.items()}
    ax, ay = _armin_spot()
    return [TB.Shot("ram", *TAB["ram"], tgt(18.0, 8.0), az=(a["ram"] + 45, a["ram"] + 15), dist=(62, 48), el=(9, 15), lens=38),
            TB.Shot("hood", *TAB["hood"], tgt(20.8, 4.0, ((ax * 2 + female_F(20.8)[0]) / 3, (ay * 2 + female_F(20.8)[1]) / 3)),
                    az=(a["hood"] - 80, a["hood"] - 55), dist=(38, 30), el=(12, 18), lens=40),
            TB.Shot("palm", *TAB["palm"], tgt(31.6, 7.0), az=(a["palm"] + 25, a["palm"] + 55), dist=(64, 50), el=(8, 13), lens=38),
            TB.Shot("spin", *TAB["spin"], tgt(36.5, 9.0), az=(a["spin"] - 25, a["spin"] - 50), dist=(72, 56), el=(26, 32), lens=36)]
PLAN = [(0.0, "morning"), (14.0, "morning"), (30.0, "day"), (STORY_DUR, "day")]
LIGHT = C.LightRig(*C.light_plan(PLAN))
TRACK = {}
S = {}

def _W(fx, fy, dz=0.0):
    w = F(fx, fy)
    return (w[0], w[1], C.G(w[0], w[1]) + dz)

# ---------------------------------------------------------------- build
def build(site):
    global CAM
    from forest import tableau as TB
    S["shots"] = _shots()
    CAM = TB.make_cam(C.lift_keys(CAM_KEYS) + S["shots"], v_in=SEAM_F1_W["vel"], v_out=SEAM_F2["vel"])   # z above ground -> absolute
    from forest import fset
    import flares
    S["fset"] = fset
    c = C.coll("F1")
    # riders, wagons, named horses (riderless) in one batch; their dust streaks in another
    B = C.Batch("F1_Riders", C.RIDER_MATS)
    for r in ROSTER:
        r["j"] = B.new(pivot=1.2)
        if r["kind"] == "wagon":
            C.wagon_geo(B.g, r["j"])
        else:
            C.rider_geo(B.g, r["j"], rider=r["kind"] != "horse", hair="blond" if r["name"] in ("armin", "erwin") else "hair")
    B.build(c); S["B"] = B
    T = C.Batch("F1_Trails", C.RIDER_MATS)
    for r in ROSTER:
        C.trail_geo(T.g, T.new())
    T.build(c); S["T"] = T
    T.ob.hide_render = True; T.ob.hide_viewport = True   # autopilot 10/28: the flat streaks read as grey slabs at the low camera
    # people: Armin / Jean / Reiner on their horses, 2 support-squad ODM soldiers
    P = C.Batch("F1_People", C.RIDER_MATS)
    S["pj"] = {}
    for nm in ("armin", "jean", "reiner", "sup1", "sup2"):
        S["pj"][nm] = P.new(pivot=0.9)
        C.person_geo(P.g, S["pj"][nm], hair="blond" if nm in ("armin", "reiner") else "hair")
    P.build(c); S["P"] = P
    S["wires"] = C.Wires("F1_Wires", 4, C.mat("F1_Wire", (0.08, 0.08, 0.09), 0.5), c, r=0.12)
    # pure titans: the old-town 10 m titan + a few wanderers on the plain
    TT = C.Batch("F1_Titans", C.titan_mats())
    S["tt"] = [C.titan_add(TT, dict(H=10.0, skin=1, hair=1)),
               C.titan_add(TT, dict(H=7.0, skin=3, g=1.3)), C.titan_add(TT, dict(H=12.0, skin=2, hair=2, al=1.2)),
               C.titan_add(TT, dict(H=5.0, skin=4, g=1.6, hs=1.3)), C.titan_add(TT, dict(H=9.0, skin=0, hair=0))]
    TT.build(c); S["TT"] = TT
    # the Female
    S["fem"] = C.Female("F1_Female")
    # village houses that collapse as she runs through
    v = fset.house_variants(fset.scene_mats(), c, 4, seed=21)
    S["smash"] = []
    for k, ts in enumerate((35.4, 36.2, 37.0, 37.8)):
        fx, fy = female_F(ts); yy = female_state(ts)[2]
        side = 9.0 * (1 if k % 2 else -1)
        hx, hy = fx + side * math.cos(yy), fy + side * math.sin(yy)
        ob = v[k][0].copy(); c.objects.link(ob)
        w = _W(hx, hy, -0.3); ob.location = w; ob.rotation_euler = (0, 0, yy); ob.scale = (1, 1, 1)
        S["smash"].append((ob, ts))
    # smoke: signal flares (positions from the pure choreography), dust, steam
    fs = flares.FlareSet("F1_Flares", style="column")        # v2: rising smoke columns, not laser beams
    def wing(rel, t):
        x, y = dc(t)
        return _W(x + rel[0], y + rel[1], 3.0)
    for k, (rel, tt) in enumerate((((400, 0), 12.0), ((200, 150), 12.6), ((0, 250), 13.2))):
        fs.add(tt, wing(rel, tt), "red", up=110, width=2.6, seed=10 + k)
    ax, ay, _ = named_F("armin", 27.0)
    fs.add(27.0, _W(ax, ay, 3.0), "purple", up=110, width=2.6, seed=21)
    for k, (rel, tt) in enumerate((((0, 150), 40.5), ((-200, 120), 41.0), ((200, 120), 41.2), ((0, -100), 41.6))):
        fs.add(tt, wing(rel, tt), "green", up=120, width=2.8, seed=30 + k)
    fs.build(c); S["fs"] = fs
    dust = flares.PuffField("F1_Dust", kind="dust", color=(0.50, 0.42, 0.30), alpha=0.6)
    te, pos, vel = [], [], []
    d0 = _fdist(14.0); step = 11.0; d = d0
    T_ = np.arange(14.0, STORY_DUR, 0.02)
    D_ = np.array([_fdist(x) for x in T_])
    while d < D_[-1]:
        tt = float(np.interp(d, D_, T_))
        fx, fy = female_F(tt)
        te.append(tt); pos.append(_W(fx, fy, 1.0)); vel.append((0, 0, 1.5))
        d += step
    for ob, ts in S["smash"]:
        for k in range(10):
            te.append(ts + 0.04 * k); pos.append(tuple(np.array(ob.location) + np.array((random.uniform(-6, 6), random.uniform(-6, 6), 2 + k))))
            vel.append((random.uniform(-3, 3), random.uniform(-3, 3), 3.0))
    dust.add_many(te, pos, vel, r0=3.0, r1=11.0, life=2.6, rise=1.5, alpha=0.55)
    dust.build(c); S["dust"] = dust
    steam = flares.PuffField("F1_Steam", kind="steam", alpha=0.7)
    tx, ty = titan_F(0, BEATS["support_kill"][1])
    steam.add_many([7.4 + 0.08 * k for k in range(30)], [_W(tx + random.uniform(-4, 4), ty + random.uniform(-4, 4), 2) for k in range(30)],
                   [(0, 0, 4)] * 30, r0=2.0, r1=7.0, life=3.0, rise=3.0)
    steam.build(c); S["steam"] = steam
    def fem_trk(t):
        ts = story(t)
        if not (14.0 <= ts < 26.0):
            return None
        return _W(*female_F(ts), 16.0)
    TRACK.update(FEMALE=fem_trk, ARMIN=lambda t: _trk("armin", story(t), 20.0),
                 JEAN=lambda t: _trk("jean", story(t)), REINER=lambda t: _trk("reiner", story(t)))
    _build_graphic(c)
    _build_tableaux(c)

# ---------------------------------------------------------------- v8: formation graphic (EP17 06:21-06:25 overlay)
def _gmat(name, rgb, strength):
    m = bpy.data.materials.new(name); m.use_nodes = True
    N, Ln = m.node_tree.nodes, m.node_tree.links
    for n in list(N):
        if n.type != "OUTPUT_MATERIAL":
            N.remove(n)
    em = N.new("ShaderNodeEmission"); em.inputs["Color"].default_value = (*rgb, 1); em.inputs["Strength"].default_value = strength
    tr = N.new("ShaderNodeBsdfTransparent"); mx = N.new("ShaderNodeMixShader"); mx.inputs[0].default_value = 0.0
    Ln.new(tr.outputs[0], mx.inputs[1]); Ln.new(em.outputs[0], mx.inputs[2])
    Ln.new(mx.outputs[0], N.get("Material Output").inputs["Surface"])
    for attr, val in (("surface_render_method", "BLENDED"), ("blend_method", "BLEND"), ("use_shadow", False)):
        try:
            setattr(m, attr, val)
        except Exception:
            pass
    return m, mx

def _build_graphic(c):
    """green translucent arrow body + the big formation circle (outer ring, inner ring, spokes) floating over the riders,
    a red ring round the titan the formation veers away from.  Local frame: disc centre at 0, travel = +y."""
    import bmesh
    mg, mxg = _gmat("F1_GraphicFill", (0.25, 0.95, 0.55), 1.6)
    ml, mxl = _gmat("F1_GraphicLine", (0.85, 1.0, 0.85), 3.0)
    mr, mxr = _gmat("F1_GraphicRed", (1.0, 0.12, 0.08), 3.0)
    S["gmix"] = (mxg, mxl, mxr)
    bm = bmesh.new()
    def ring(r0, r1, mi, n=72):
        vs = [(bm.verts.new((r0 * math.cos(a), r0 * math.sin(a), 0)), bm.verts.new((r1 * math.cos(a), r1 * math.sin(a), 0)))
              for a in np.linspace(0, math.tau, n, endpoint=False)]
        for k in range(n):
            a, b = vs[k], vs[(k + 1) % n]
            bm.faces.new((a[0], b[0], b[1], a[1])).material_index = mi
    ring(0.0, 430.0, 0)                                   # disc fill
    ring(410.0, 440.0, 1); ring(240.0, 256.0, 1)          # outer + inner rings
    for a in np.linspace(0, math.tau, 12, endpoint=False):      # spokes (the anime disc pattern)
        ca, sa = math.cos(a), math.sin(a); w = 7.0
        p = [(256 * ca - w * sa, 256 * sa + w * ca), (410 * ca - w * sa, 410 * sa + w * ca), (410 * ca + w * sa, 410 * sa - w * ca), (256 * ca + w * sa, 256 * sa - w * ca)]
        bm.faces.new([bm.verts.new((x, y, 0.3)) for x, y in p]).material_index = 1
    # arrow body behind the disc (tapering toward the tail)
    P = [(-150, -1800), (150, -1800), (230, -300), (-230, -300)]
    bm.faces.new([bm.verts.new((x, y, -0.3)) for x, y in P]).material_index = 0
    ob = C.mesh_obj("F1_FormationGraphic", bm, [mg, ml], c); ob.visible_shadow = False
    S["graphic"] = ob
    bm = bmesh.new(); ring(80.0, 100.0, 0, 48)
    ob2 = C.mesh_obj("F1_TitanMark", bm, [mr], c); ob2.visible_shadow = False
    S["tmark"] = ob2

def _graphic_update(t, ts):
    a = C.ss(TAB["graphic"][0], TAB["graphic"][0] + 0.6, t) * (1 - C.ss(TAB["graphic"][1] - 0.5, TAB["graphic"][1], t))
    mxg, mxl, mxr = S["gmix"]
    mxg.inputs[0].default_value = 0.30 * a; mxl.inputs[0].default_value = 0.85 * a
    mxr.inputs[0].default_value = 0.9 * a * C.ss(4.6, 5.2, t)
    for ob in (S["graphic"], S["tmark"]):
        C.hide(ob, a <= 0.0)
    if a <= 0.0:
        return
    x, y = dc(ts); x2, y2 = dc(ts + 0.6)
    w = F(x, y)
    zt = max(C.G(w[0] + dx, w[1] + dy) for dx in (-400, 0, 400) for dy in (-400, 0, 400)) + 30.0
    S["graphic"].location = (w[0], w[1], zt)
    S["graphic"].rotation_euler = (0, 0, C.yaw_of(x2 - x, y2 - y + 1e-6))
    tx, ty = titan_F(1, ts); wt = F(tx, ty)
    S["tmark"].location = (wt[0], wt[1], C.G(wt[0], wt[1]) + 2.0)

# ---------------------------------------------------------------- v8: frozen tableaux (forest.tableau)
def _build_tableaux(c):
    B = C.Batch("F1_TScouts", C.RIDER_MATS)
    for k in range(6):
        C.person_geo(B.g, B.new(pivot=0.9))
    for k in range(2):
        C.rider_geo(B.g, B.new(pivot=1.2), rider=False)
    B.build(c); S["TS"] = B
    B.vis[:] = 0.0; B.push()
    S["twires"] = C.Wires("F1_TWires", 2, C.mat("F1_Wire", (0.08, 0.08, 0.09), 0.5), c, r=0.18)
    # smoke curling off her palm (EP17 21:38): puffs emitted just before the frozen story time -> frozen mid-curl
    import flares
    sm = flares.PuffField("F1_PalmSmoke", kind="steam", alpha=0.75)
    S["palm_smoke"] = sm
    sm_pos = _palm_pos(); S["palm0"] = np.array(sm_pos)
    ts = TAB_STORY["palm"]
    sm.add_many([ts - 0.9 + 0.05 * k for k in range(18)], [tuple(np.array(sm_pos) + np.array((0.2 * (k % 3) - 0.2, 0.15 * (k % 2), 0.0))) for k in range(18)],
                [(0.3, 0.1, 1.6)] * 18, r0=0.3, r1=1.4, life=1.6, rise=1.0)
    sm.build(c)

def _palm_pos():
    from forest import tableau as TB
    fem = S["fem"]; ts = TAB_STORY["palm"]
    x, y, yaw = female_state(ts)
    fem.pose(TB.POSE_F["palm"]); w = _W(x, y, TB.FZ_T["palm"]); fem.place(w[0], w[1], w[2], yaw)
    bpy.context.view_layer.update()
    p = fem.bone_world("lowerarm01.R", tail=True)
    return (p.x, p.y, p.z + 0.8)

def _tab_now(t):
    for k, (a, b) in TAB.items():
        if k != "graphic" and a - 0.25 <= t <= b + 0.25:
            return k
    return None

def _tableau_update(t):
    from forest import tableau as TB
    k = _tab_now(t)
    B = S["TS"]; B.vis[:] = 0.0
    segs = []
    if k is not None:
        fem = S["fem"]; ts = TAB_STORY[k]
        x, y, yaw = female_state(ts)
        fem.show(True); fem.pose(TB.POSE_F[TAB_POSE[k]])
        w = _W(x, y, TB.FZ_T.get(TAB_POSE[k], 0.0)); fem.place(w[0], w[1], w[2], yaw)
        bpy.context.view_layer.update()
        f = np.array((-math.sin(yaw), math.cos(yaw), 0.0)); r = np.array((math.cos(yaw), math.sin(yaw), 0.0))
        base = np.array(w)
        if k == "palm":                    # the smoke follows her palm as evaluated now
            p = fem.bone_world("lowerarm01.R", tail=True)
            for pl in S["palm_smoke"].cards.pools.values():
                if pl.ob is not None:
                    pl.ob.location = tuple(np.array((p.x, p.y, p.z + 0.8)) - S["palm0"])
        if k == "hood":                    # Armin stands right under her fingers
            p = fem.bone_world("lowerarm01.R", tail=True)
            P = S["P"]; j = S["pj"]["armin"]
            P.pos[j] = (p.x + 1.2 * f[0], p.y + 1.2 * f[1], C.G(p.x, p.y)); P.vis[j] = 1.0
            C.person_pose(P, j, "stand"); P.yaw[j] = yaw + math.pi; P.push()
        if k == "ram":
            sh = np.array(fem.bone_world("upperarm01.R"))
            hl = np.array(fem.bone_world("lowerarm01.L", tail=True))
            put = [(0, sh + f * 2.5 + r * 3.5 + np.array((0, 0, 1.0)), "flung", 0.4),         # rammed off her shoulder
                   (1, hl + r * -9.0 + f * -4.0 + np.array((0, 0, 7.0)), "hang", 1.9),        # yanked up on his wire
                   (2, base + f * 9.0 + r * 10.0 + np.array((0, 0, 6.5)), "flung", 2.6),
                   (3, base + f * -6.0 + r * 13.0 + np.array((0, 0, 3.2)), "flung", -1.0)]
            for j, p, m, yy in put:
                B.vis[j] = 1.0; B.pos[j] = p; B.yaw[j] = yaw + yy; TB.scout_pose(B, j, m)
            segs.append((tuple(hl), tuple(put[1][1] + np.array((0, 0, 1.6)))))
            for j, off, rl in ((6, f * 6.0 + r * 8.0, 1.2), (7, f * -2.0 + r * 15.0, -1.6)):     # riderless horses tumbling
                B.vis[j] = 1.0; B.pos[j] = base + off + np.array((0, 0, 1.5)); B.yaw[j] = yaw + 1.0; B.roll[j] = rl; B.pitch[j] = 0.3
        elif k == "spin":
            piv = np.array(fem.bone_world("lowerarm01.R", tail=True))
            th = 0.55 * (t - TAB["spin"][0]) + math.atan2(-f[1], -f[0])                         # very slow circle round her hand
            p = piv + np.array((15.0 * math.cos(th), 15.0 * math.sin(th), -3.5))
            B.vis[4] = 1.0; B.pos[4] = p; TB.scout_pose(B, 4, "swung")
            B.yaw[4] = C.yaw_of(piv[0] - p[0], piv[1] - p[1])
            segs.append((tuple(piv), tuple(p)))
    B.push()
    S["twires"].update(segs, bpy.context.scene.camera.location if bpy.context.scene.camera else (0, 0, 1000))
    S["palm_smoke"].update(story(t), wind=(0.6, 0.2))

def _trk(nm, t, t0=26.0):
    if not (t0 <= t <= 34.0):
        return None
    x, y, _ = named_F(nm, t)
    return _W(x, y, 4.0)

# pure titans (F): 0 = the old-town titan (walks at the road, killed 7.4, falls), others wander the plain
TPATH = {0: [(0.0, 760.0, -8300.0), (7.4, 690.0, -8420.0)], 1: [(0.0, 1300.0, -7000.0), (48.0, 1100.0, -6400.0)],
         2: [(0.0, -500.0, -6200.0), (48.0, -300.0, -5900.0)], 3: [(0.0, 1250.0, -3500.0), (48.0, 1000.0, -3300.0)],
         4: [(0.0, -600.0, -2600.0), (48.0, -350.0, -2200.0)]}
def titan_F(i, t):
    x, y, yaw = C.path_at(TPATH[i], t)
    return x, y

# ---------------------------------------------------------------- per frame
def update(t):
    ts = story(t)
    _update(ts)
    _graphic_update(t, ts)
    _tableau_update(t)

def _update(t):
    fset = S["fset"]
    fset.gate_open(C.ss(*BEATS["gate"], t))
    fset.mills(t)
    B, T, P, TT = S["B"], S["T"], S["P"], S["TT"]
    for r in ROSTER:
        j = r["j"]
        tk = r["kill"]
        te = min(t, tk) if tk is not None else t
        if r["kind"] == "horse":
            x, y, _ = named_F(r["name"], te)
            x2, y2, _ = named_F(r["name"], te + 0.05)
            s = base_pos(r, te)[2] if t < 19.0 else 1e9
            if r["name"] == "armin" and 19.4 <= t < 24.5:          # Armin's horse bolts on without him
                x, y, _ = base_pos(r, t); x2, y2, _ = base_pos(r, t + 0.05)
        else:
            x, y, s = base_pos(r, te)
            x2, y2, _ = base_pos(r, te + 0.05)
        vis = 1.0 if s > -3.0 else 0.0                              # still inside the gate tunnel
        sp = math.hypot(x2 - x, y2 - y) / 0.05
        yaw = C.yaw_of(x2 - x, y2 - y) if sp > 0.5 else B.yaw[j]
        w = _W(x, y)
        B.pos[j] = w; B.yaw[j] = yaw; B.vis[j] = vis
        ph = 2 * math.pi * 2.3 * t + j
        moving = tk is None or t < tk
        B.Ar[j, 1] = 0.55 * math.sin(ph) * moving; B.Ar[j, 2] = -0.55 * math.sin(ph) * moving
        B.roll[j] = 0.0
        if not moving:
            B.roll[j] = -1.45 * C.ss(tk, tk + 0.4, t)              # thrown down
        T.pos[j] = w; T.yaw[j] = yaw; T.vis[j] = vis * min(1.0, sp / 40.0) * moving
    B.push(); T.push()
    # people
    pj = S["pj"]
    for nm in ("armin", "jean", "reiner"):
        j = pj[nm]
        x, y, mode = named_F(nm, t)
        hz = 1.55 if mode == "seated" else 0.0
        P.vis[j] = 1.0
        hr = NAMED[nm]["j"]
        yaw = B.yaw[hr]
        if mode == "seated":
            x, y = C.toF(B.pos[hr][0], B.pos[hr][1])[:2]
        w = _W(x, y, hz)
        if nm == "reiner" and BEATS["grab"][0] <= t < 31.4:
            fem = S["fem"]
            bpy.context.view_layer.update()
            hpos = fem.bone_world("lowerarm01.R", tail=True)
            if t < BEATS["free"]:
                w = (hpos.x, hpos.y, hpos.z - 0.9); C.person_pose(P, j, "stand")
            else:                                                  # cuts free: drops in an arc back to his horse
                u = C.ss(BEATS["free"], 31.4, t)
                hw = B.pos[hr] + np.array((0, 0, 1.55))
                w = (hpos.x + (hw[0] - hpos.x) * u, hpos.y + (hw[1] - hpos.y) * u,
                     hpos.z + (hw[2] - hpos.z) * u + 6.0 * math.sin(math.pi * u))
                C.person_pose(P, j, "fly")
        else:
            C.person_pose(P, j, "seated" if mode == "seated" else ("stand" if t < 22.8 else "run"), t)
        if nm == "armin" and 19.4 <= t < 20.0:                     # knocked off the horse
            C.person_pose(P, j, "fallen")
        P.pos[j] = w; P.yaw[j] = yaw if mode == "seated" else female_state(19.95)[2] + math.pi
        if mode == "seated":
            P.vis[j] = B.vis[hr]
    # support squad: two ODM flyers from the column at the old-town titan's nape 6.6-7.4
    segs = []
    tx, ty = titan_F(0, min(t, 7.4))
    nape = np.array(_W(tx, ty, 9.6))
    for k, nm in enumerate(("sup1", "sup2")):
        j = pj[nm]
        t0, t1 = 6.0 + 0.2 * k, 7.0 + 0.3 * k
        (cx, cy), cy_yaw, _ = col_pos(3 + 2 * k, t0)
        start = np.array(_W(cx, cy, 1.6))
        if t < t0 or t > t1 + 0.8:
            P.vis[j] = 0.0; P.pos[j] = start; continue
        u = C.ss(t0, t1, t)
        p = start + (nape + np.array((6 * (k - 0.5), -4, 2)) - start) * u + np.array((0, 0, 12 * math.sin(math.pi * u)))
        if t > t1:
            p = nape + np.array((6 * (k - 0.5), 4 + 20 * (t - t1), 2 - 8 * (t - t1)))
        P.vis[j] = 1.0; P.pos[j] = p; C.person_pose(P, j, "fly")
        d = nape - p; P.yaw[j] = C.yaw_of(d[0], d[1])
        if t < t1:
            segs.append((tuple(p + np.array((0, 0, 1.0))), tuple(nape + np.array((3 * k, 0, 1)))))
    P.push()
    S["wires"].update(segs, bpy.context.scene.camera.location if bpy.context.scene.camera else (0, 0, 1000))
    # pure titans
    for i, j in enumerate(S["tt"]):
        x, y = titan_F(i, t)
        x2, y2 = titan_F(i, t + 0.05)
        TT.pos[j] = _W(x, y); TT.yaw[j] = C.yaw_of(x2 - x, y2 - y + 1e-9) if (x2 - x) ** 2 + (y2 - y) ** 2 > 1e-8 else TT.yaw[j]
        C.titan_walk(TT, j, t * 2.2 + i, 0.4)
        if i == 0 and t >= 7.4:                                    # cut: topples forward, then lies, steams
            TT.pitch[j] = -1.45 * C.ss(7.4, 8.4, t); TT.Ar[j, :] = 0.0
            TT.vis[j] = 1.0 - 0.3 * C.ss(9.0, 14.0, t)
        if i == 0 and t > 16.0:
            TT.vis[j] = 0.0
    TT.push()
    # the Female
    fem = S["fem"]
    if t < BEATS["female_in"] - 0.01:
        fem.show(False)
    else:
        fem.show(True)
        x, y, yaw = female_state(t)
        pose, dz = female_mode(t)
        fem.pose(pose)
        w = _W(x, y, dz)
        fem.place(w[0], w[1], w[2], yaw, pitch=0.0)
    for ob, ts in S["smash"]:
        u = C.ss(ts, ts + 0.5, t)
        ob.scale = (1.0 + 0.2 * u, 1.0 + 0.2 * u, max(0.15, 1.0 - 0.85 * u))
    cam = bpy.context.scene.camera
    S["fs"].update(t, wind=(4.0, 1.5)); S["dust"].update(t, wind=(2.0, 0.6)); S["steam"].update(t, wind=(1.5, 0.5))

def light(t):
    LIGHT.apply(story(t))

def check():
    for t in (14.0, 17.0, 20.0, 26.0, 30.0, 36.0, 40.0, 44.0, 48.0):
        fx, fy = female_F(t); x, y = dc(t)
        print(f"[f1] t {t:4.1f} dome ({x:6.0f} {y:7.0f}) female ({fx:6.0f} {fy:7.0f})  rel ({fx - x:5.0f} {fy - y:5.0f})")
    kills = [r["kill"] for r in ROSTER if r["kill"] is not None]
    print(f"[f1] right-wing kills: {len(kills)} at {sorted(round(k, 2) for k in kills)}")
    print(f"[f1] head s at 4, 6, 8: {head_s(4):.0f} {head_s(6):.0f} {head_s(8):.0f}")
