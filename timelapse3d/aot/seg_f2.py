"""f2 FOREST CHASE -> TRAP -> CAPTURE -> SCREAM (bible beats f7-f10, 36 s, forest set, frame W; layout in frame F).
SEG=f2 bash aot/forest/render_part2.sh

  0-13.7  the centre line enters the forest road; Levi squad (6 riders, Eren) gallops north down the trunk colonnade with the
          Female 30-40 m behind; she swats the reinforcements riding in from the sides; chase-cam ahead looking back, below the canopy
  13.7-20 they pass between the launcher racks; she leaps; the radial harpoon volley (3 salvos) pins her standing in the
          clearing, hands over her nape
  20-26   capture tableau: fingers harden, Levi lands on her head, blue then green signal smoke up through the canopy gap
  26-36   the SCREAM: pure titans pour in from every side, ignore the soldiers on the branches and devour her; steam fills the
          clearing; the camera pulls up through the gap (f3 opens above the canopy at sunset)
"""
import math, os, sys, random
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from forest import common as C
from forest import layout as LY
import camchan
import seg_f1 as F1
try:
    import bpy
except ImportError:
    bpy = None

DUR = 36.0
BEATS = dict(chase=(0.0, 13.7), swats=(4.5, 7.0, 9.5), leap=13.9, volley=(14.3, 14.9, 15.5), nape=16.0, stop=18.5,
             harden=(20.0, 24.0), levi=(21.0, 22.2), blue=23.0, green=24.4, scream=26.0, pour=(26.0, 31.0),
             eat=(30.5, 35.0), steam=(30.0, 36.0))
F = C.F

def _W(fx, fy, dz=0.0):
    w = F(fx, fy)
    return (w[0], w[1], C.G(w[0], w[1]) + dz)

# ---------------------------------------------------------------- road arc length (f1's road table, frame F)
def _s_of(px, py):
    pts, S = F1.road()
    i = int(np.argmin(np.hypot(pts[:, 0] - px, pts[:, 1] - py)))
    return float(S[i])
S_ENTRY = _s_of(0.0, 0.0)
S_TRAP = _s_of(*LY.TRAP_F)
# Levi squad lead: f1 end speed (~500 m/s time-lapse) -> 100 m/s by 2.5 s -> past the trap -> stop 250 m beyond (dismount)
_T = np.arange(0.0, DUR + 2.0, 0.01)
_V = np.interp(_T, [0.0, 2.5, 13.0, 15.0, 18.5, 40.0], [480.0, 72.0, 72.0, 50.0, 0.0, 0.0])
_X = np.concatenate([[0.0], np.cumsum(_V[:-1] * 0.01)])
S0 = _s_of(0.0, -300.0 - 330.0)                       # f1 t 48: dome (40, -300) + Levi slot (0, -330)
def lead_s(t):
    return S0 + float(np.interp(t, _T, _X))
T_PASS = float(np.interp(S_TRAP, [lead_s(x) for x in _T], _T))
# the Female: 38 m behind the lead until she reaches the trap centre; then pinned there
def fem_s(t):
    return lead_s(t) - 38.0
T_VOLLEY = float(np.interp(S_TRAP, [fem_s(x) for x in _T], _T))
BEATS["volley"] = (T_VOLLEY, T_VOLLEY + 0.6, T_VOLLEY + 1.2)
BEATS["leap"] = T_VOLLEY - 0.45

SQUAD = [("levi", 0.0, 0.0), ("eren", -2.0, -7.0), ("petra", 2.5, -9.0), ("oluo", -3.0, -13.0), ("gunther", 2.0, -16.0), ("erd", -1.0, -19.0)]
def squad_F(k, t):
    nm, dx, ds = SQUAD[k]
    s = lead_s(t) + ds
    p, yaw = F1.road_at(s)
    return float(p[0] + dx * math.cos(yaw)), float(p[1] + dx * math.sin(yaw)), yaw

def fem_F(t):
    if t >= T_VOLLEY:
        return LY.TRAP_F[0], LY.TRAP_F[1], 0.0
    p, yaw = F1.road_at(fem_s(t))
    return float(p[0]), float(p[1]), yaw

# reinforcements riding in from the sides (killed by her swats)
REINF = []
for k, ts in enumerate(BEATS["swats"]):
    side = 1 if k % 2 == 0 else -1
    REINF.append(dict(ts=ts, side=side))
def reinf_F(k, t):
    r = REINF[k]
    ts = r["ts"]
    te = min(t, ts)
    fx, fy, yaw = fem_F(te)
    # comes in from the side over 3 s, ends 10 m beside her at ts
    u = C.ss(ts - 3.0, ts, te)
    off = r["side"] * (70.0 - 60.0 * u)
    x = fx + off * math.cos(yaw) - (12.0 - 14 * u) * math.sin(yaw)
    y = fy + off * math.sin(yaw) + (12.0 - 14 * u) * math.cos(yaw)
    return x, y, yaw

# soldiers on the branches round the clearing (the 104th + Erwin's officers), Levi's flight to her head
def ring_soldiers():
    rnd = random.Random(104)
    out = []
    for k in range(34):
        a = rnd.uniform(0, math.tau); r = rnd.uniform(45, 160)
        out.append((LY.TRAP_F[0] + r * math.cos(a), LY.TRAP_F[1] + r * math.sin(a), rnd.choice((14.0, 22.0, 30.0, 38.0))))
    return out
RING = ring_soldiers()

# the screaming: pure titans converge from every direction, then cluster on her
def titan_plan():
    rnd = random.Random(20)
    out = []
    for k in range(22):
        a = k * math.tau / 22 + rnd.uniform(-0.1, 0.1)
        r0 = rnd.uniform(500, 1000)
        H = rnd.choice((5.0, 7.0, 8.0, 10.0, 12.0, 13.0, 15.0))
        t_arr = rnd.uniform(29.4, 32.5)
        out.append(dict(a=a, r0=r0, H=H, t_arr=t_arr, ring=rnd.uniform(5.5, 9.5), skin=k % 7, hair=(k % 4) if k % 3 else None,
                        g=rnd.uniform(0.8, 1.5), climb=rnd.random() < 0.35))
    return out
TPLAN = titan_plan()
def titan_F(p, t):
    a = p["a"]
    u = C.ss(BEATS["pour"][0], p["t_arr"], t)
    r = p["r0"] + (p["ring"] - p["r0"]) * (u ** 0.85)
    x = LY.TRAP_F[0] + r * math.cos(a); y = LY.TRAP_F[1] + r * math.sin(a)
    return x, y, C.yaw_of(-math.cos(a), -math.sin(a))

# ---------------------------------------------------------------- camera
SEAM_IN = F1.SEAM_F2
def _side_key(t, lat, z):
    p, yaw = F1.road_at(lead_s(t) + 10.0)
    q, _ = F1.road_at(lead_s(t) - 20.0)
    return (t, F(p[0] + lat * math.cos(yaw), p[1] + lat * math.sin(yaw), z), F(q[0], q[1], 5.0), 30.0)
def _chase_key(t, side):
    p, yaw = F1.road_at(lead_s(t) + 75.0)
    q, _ = F1.road_at(lead_s(t) - 30.0)
    px, py = p[0] + side * 14 * math.cos(yaw), p[1] + side * 14 * math.sin(yaw)
    return (t, F(px, py, 44.0), F(q[0], q[1], 8.0), 30.0)
TX, TY = LY.TRAP_F
SEAM_F3 = dict(pos=F(-120.0, 690.0, 240.0), look=F(0.0, 960.0, 40.0), lens=30.0, vel=(0.0, 4.0, 6.0))
# v8 (FEEDBACK_v13 §2): video clock with FROZEN tableaux (flat knots): sprint (riders + the Female at full sprint), the
# pinned Female (hands over the nape), then NO scream animation: the camera rises to the sky and the titans swarm in
STORY_DUR = 36.0
TMAP = [(0.0, 0.0), (1.7, 1.7), (2.2, 8.0), (4.4, 8.0), (5.0, 19.0), (7.4, 19.0), (8.0, 26.0), (11.5, 34.5), (12.5, 36.0)]
DUR = TMAP[-1][0]
TAB = dict(sprint=(2.2, 4.4), trap=(5.0, 7.4))
def story(t):
    return float(np.interp(t, [k[0] for k in TMAP], [k[1] for k in TMAP]))
def _shots(lift=False):
    from forest import tableau as TB
    lx, ly, _ = squad_F(1, 8.0); fx, fy, yaw = fem_F(8.0)
    front = math.degrees(yaw) + 90.0
    sh = [TB.Shot("sprint", *TAB["sprint"], F((lx + 2 * fx) / 3, (ly + 2 * fy) / 3, 7.0), az=(front + 55, front + 30), dist=(64, 50),
                  el=(7, 11), lens=32),
          TB.Shot("trap", *TAB["trap"], F(TX, TY, 9.0), az=(205, 240), dist=(60, 48), el=(16, 22), lens=40)]
    if lift:
        for s_ in sh:
            x, y, z = s_.target; s_.target = (x, y, z + C.G(x, y))
    return sh
CAM_KEYS = [
    (0.0, F(*SEAM_IN["pos"]), F(*SEAM_IN["look"]), SEAM_IN["lens"]),
    _side_key(1.7, 70.0, 70.0),
    (7.9, F(TX - 30, TY - 60, 110.0), F(TX, TY, 5.0), 28.0),            # up out of the clearing
    (9.8, F(TX - 30, TY - 55, 200.0), F(TX, TY, 0.0), 30.0),           # sky: the titans swarm into the clearing (looking down into the gap)
    (DUR, SEAM_F3["pos"], SEAM_F3["look"], SEAM_F3["lens"]),
]
def _cam(lift):
    from forest import tableau as TB
    keys = C.lift_keys(CAM_KEYS) if lift else CAM_KEYS
    return TB.make_cam(keys + _shots(lift), v_in=SEAM_IN["vel"], v_out=SEAM_F3["vel"])
CAM = _cam(False)
CAM_LIMITS = dict(speed=1500.0, yaw=300.0, hmin=8.0, hmax=320.0, pitch=(0.0, 85.0), lens=(27.0, 44.0))
PLAN = [(0.0, "day"), (20.0, "day"), (DUR, "afternoon")]
LIGHT = C.LightRig(*C.light_plan(PLAN))
TRACK = {}
S = {}

# ---------------------------------------------------------------- build
def build(site):
    global CAM
    CAM = _cam(True)                                                                              # z above ground -> absolute
    from forest import fset
    import flares
    flares.COLORS.setdefault("blue", ((0.05, 0.16, 0.75), (0.35, 0.55, 1.0)))
    S["fset"] = fset
    c = C.coll("F2")
    B = C.Batch("F2_Riders", C.RIDER_MATS)
    S["sq"] = [B.new(pivot=1.2) for _ in SQUAD]
    for j in S["sq"]:
        C.rider_geo(B.g, j)
    S["rf"] = [B.new(pivot=1.2) for _ in REINF]
    for j in S["rf"]:
        C.rider_geo(B.g, j)
    # the rest of the centre line ahead (already through, tied horses at the clearing edge)
    S["tied"] = []
    rnd = random.Random(9)
    for k in range(18):
        j = B.new(pivot=1.2); C.rider_geo(B.g, j, rider=False)
        a = rnd.uniform(0, math.tau); r = rnd.uniform(60, 140)
        S["tied"].append((j, TX + r * math.cos(a), TY + 200 + r * math.sin(a) * 0.5, rnd.uniform(0, math.tau)))
    B.build(c); S["B"] = B
    P = C.Batch("F2_People", C.RIDER_MATS)
    S["ring"] = [P.new(pivot=0.9) for _ in RING]
    for j in S["ring"]:
        C.person_geo(P.g, j)
    S["levi_p"] = P.new(pivot=0.9); C.person_geo(P.g, S["levi_p"])
    P.build(c); S["P"] = P
    TT = C.Batch("F2_Titans", C.titan_mats())
    S["tt"] = [C.titan_add(TT, dict(H=p["H"], skin=p["skin"], hair=p["hair"], g=p["g"])) for p in TPLAN]
    TT.build(c); S["TT"] = TT
    S["fem"] = C.Female("F2_Female")
    S["wires"] = C.Wires("F2_Harpoons", 48, C.mat("F2_Wire", (0.10, 0.10, 0.11), 0.4), c, r=0.10)
    S["lwire"] = C.Wires("F2_LeviWire", 2, C.mat("F2_Wire", (0.10, 0.10, 0.11), 0.4), c, r=0.08)
    # harpoon plan: rack -> body point (height on her body, angle round her)
    racks = fset.STATE.get("racks") or [_W(TX + 35 * math.cos(a), TY + 35 * math.sin(a), 2.0) for a in np.linspace(0, math.tau, 14, endpoint=False)]
    rnd = random.Random(48)
    S["harp"] = []
    for k in range(48):
        rk = racks[k % len(racks)]
        salvo = 0 if k < 22 else (1 if k < 36 else 2)
        S["harp"].append(dict(rack=np.array(rk) + np.array((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(0, 1.5))),
                              h=rnd.uniform(3.0, 12.5), ang=math.atan2(rk[1] - C.F(TX, TY)[1], rk[0] - C.F(TX, TY)[0]) + rnd.uniform(-0.3, 0.3),
                              t0=BEATS["volley"][salvo] + rnd.uniform(0, 0.12)))
    fs = flares.FlareSet("F2_Flares")
    fs.add(BEATS["blue"], _W(TX - 30, TY + 40, 34.0), "blue", up=140, width=2.0, seed=3)
    fs.add(BEATS["green"], _W(TX + 25, TY + 60, 34.0), "green", up=140, width=2.0, seed=4)
    fs.build(c); S["fs"] = fs
    steam = flares.PuffField("F2_Steam", kind="steam", alpha=0.8)
    te, pos, vel = [], [], []
    for k in range(260):
        tt = random.uniform(BEATS["steam"][0], BEATS["steam"][1] - 0.5)
        a = random.uniform(0, math.tau); r = random.uniform(0, 12)
        te.append(tt); pos.append(_W(TX + r * math.cos(a), TY + r * math.sin(a), random.uniform(2, 14)))
        vel.append((random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(5, 10)))
    steam.add_many(te, pos, vel, r0=3.0, r1=14.0, life=4.0, rise=4.0, alpha=0.7)
    steam.build(c); S["steam"] = steam
    dust = flares.PuffField("F2_Dust", kind="dust", color=(0.32, 0.26, 0.18), alpha=0.6)
    te, pos, vel = [], [], []
    for tt in np.arange(0.0, T_VOLLEY, 0.12):
        fx, fy, _ = fem_F(float(tt))
        te.append(float(tt)); pos.append(_W(fx, fy, 1.0)); vel.append((0, 0, 1.0))
    for k in range(30):                                           # the landing in the clearing
        te.append(T_VOLLEY + 0.4 + 0.02 * k); pos.append(_W(TX + random.uniform(-8, 8), TY + random.uniform(-8, 8), 1.0)); vel.append((0, 0, 2.0))
    dust.add_many(te, pos, vel, r0=2.5, r1=8.0, life=2.0, rise=1.0, alpha=0.5)
    dust.build(c); S["dust"] = dust
    TRACK.update(LEVI=lambda t: _W(*squad_F(0, story(t))[:2], 4.0) if story(t) < 12.0 else None,
                 EREN=lambda t: _W(*squad_F(1, story(t))[:2], 4.0) if story(t) < 12.0 else None)

# ---------------------------------------------------------------- per frame
def fem_pose(t):
    from forest import tableau as TB
    run = C.fem_run(2 * math.pi * 2.8 * t, lean=30.0)
    if abs(t - 8.0) < 1e-6:                                       # v8 frozen tableau: full sprint
        return TB.POSE_F["sprint"], 0.0, 0.0
    if t < BEATS["leap"] - 0.3:
        P = run
        for ts in BEATS["swats"]:
            w = C.bump(t, ts - 0.3, ts - 0.05, ts + 0.15, ts + 0.45)
            if w > 0:
                P = C.fpose_blend(P, C.FPOSE["swat"], w)
        return P, 0.0, 0.0
    tv = T_VOLLEY
    if t < tv + 0.5:                                              # leap: crouch then airborne
        u = C.ss(BEATS["leap"] - 0.3, BEATS["leap"], t)
        P = C.fpose_blend(run, C.FPOSE["crouch"], u * (1 - C.ss(BEATS["leap"], tv, t)))
        air = 7.0 * math.sin(math.pi * C.ss(BEATS["leap"], tv + 0.5, t))
        return P, 0.0, air
    if t < BEATS["scream"]:                                       # pinned standing, hands to the nape (guard -> nape)
        P = C.fpose_blend(C.FPOSE["guard"], TB.POSE_F["nape"], C.ss(tv + 0.5, BEATS["nape"], t))
        return P, 0.0, 0.0
    P = TB.POSE_F["nape"]                                         # v8: no scream animation (hidden by the sky pull-out)
    sink = C.ss(BEATS["eat"][0], BEATS["eat"][1], t)              # the titans drag her down
    P = C.fpose_blend(P, C.FPOSE["kneel"], sink)
    return P, C.FZ["kneel"] * sink, 0.0

def update(t):
    _update(story(t))

def _update(t):
    B, P, TT = S["B"], S["P"], S["TT"]
    cam = bpy.context.scene.camera
    # autopilot 10/28 (see seg_f3): canopy-grazing views can exceed the GPU driver timeout -> far clip 900 m in the forest
    if "_clip0" not in S:
        S["_clip0"] = cam.data.clip_end
    cam.data.clip_end = (float(os.environ.get("F_CLIP", "350")) if t < 30.5 else 900.0) if t > 2.6 else S["_clip0"]   # 900 m still crashed at 24.2 (480p)
    C.forest_dim(C.ss(2.6, 3.4, t) * (1 - C.ss(29.8, 30.5, t)))
    for k, j in enumerate(S["sq"]):
        x, y, yaw = squad_F(k, t)
        B.pos[j] = _W(x, y); B.yaw[j] = yaw
        mv = 1.0 if t < BEATS["stop"] else 0.0
        ph = 2 * math.pi * 2.3 * t + k
        B.Ar[j, 1] = 0.55 * math.sin(ph) * mv; B.Ar[j, 2] = -0.55 * math.sin(ph) * mv
    for k, j in enumerate(S["rf"]):
        x, y, yaw = reinf_F(k, t)
        ts = REINF[k]["ts"]
        B.pos[j] = _W(x, y); B.yaw[j] = yaw
        B.roll[j] = -1.45 * C.ss(ts, ts + 0.4, t) * REINF[k]["side"]
        B.vis[j] = 1.0 if t > ts - 3.0 else 0.0
    for j, x, y, yaw in S["tied"]:
        B.pos[j] = _W(x, y); B.yaw[j] = yaw
    B.push()
    # the Female
    fem = S["fem"]
    fx, fy, yaw = fem_F(t)
    if t >= T_VOLLEY:
        yaw = fem_F(T_VOLLEY - 0.01)[2]
    pose, dz, air = fem_pose(t)
    fem.pose(pose)
    w = _W(fx, fy, dz + air)
    fem.place(w[0], w[1], w[2], yaw)
    fem.hardening(C.ss(*BEATS["harden"], t))
    show = t < BEATS["eat"][1] + 0.6
    fem.show(show)
    bpy.context.view_layer.update()
    # harpoons
    segs = []
    base = np.array(w)
    for h in S["harp"]:
        if t < h["t0"]:
            continue
        u = C.ss(h["t0"], h["t0"] + 0.18, t)
        tgt = base + np.array((2.2 * math.cos(h["ang"]), 2.2 * math.sin(h["ang"]), h["h"] + dz))
        a = h["rack"]
        segs.append((tuple(a), tuple(a + (tgt - a) * u)))
    if t > BEATS["eat"][1]:
        segs = []
    S["wires"].update(segs, cam.location)
    # soldiers on the branches, Levi lands on her head
    for k, j in enumerate(S["ring"]):
        x, y, z = RING[k]
        if t < 12.0:
            P.vis[j] = 0.0
        P.pos[j] = _W(x, y, z); P.yaw[j] = C.yaw_of(TX - x, TY - y); C.person_pose(P, j, "stand")
    lj = S["levi_p"]
    head = fem.bone_world("head", tail=True)
    l0, l1 = BEATS["levi"]
    start = np.array(_W(TX - 40, TY - 30, 30.0))
    if t < l0:
        P.vis[lj] = 0.0; P.pos[lj] = start
        S["lwire"].update([], cam.location)
    else:
        u = C.ss(l0, l1, t)
        hp = np.array((head.x, head.y, head.z + 0.3))
        p = start + (hp - start) * u + np.array((0, 0, 10 * math.sin(math.pi * u)))
        P.vis[lj] = 1.0 if t < BEATS["eat"][0] else 0.0
        P.pos[lj] = p; C.person_pose(P, lj, "fly" if u < 1 else "stand")
        S["lwire"].update([(tuple(p + np.array((0, 0, 1))), tuple(hp + np.array((0, 0, 3))))] if u < 1 else [], cam.location)
    P.push()
    # titans
    for p, j in zip(TPLAN, S["tt"]):
        x, y, yaw = titan_F(p, t)
        on = t >= BEATS["pour"][0] - 0.1
        TT.vis[j] = 1.0 if on else 0.0
        z = 0.0
        if t > p["t_arr"]:
            if p["climb"]:
                z = 3.0 * C.ss(p["t_arr"], p["t_arr"] + 1.0, t)
            TT.lean[j] = -0.6 * C.ss(p["t_arr"], p["t_arr"] + 0.4, t)
            TT.Ar[j, 3] = TT.Ar[j, 4] = TT.Ar[j, 5] = TT.Ar[j, 6] = 2.2 + 0.3 * math.sin(t * 6 + j)
            TT.Ar[j, 1] = TT.Ar[j, 2] = 0.0
        else:
            C.titan_walk(TT, j, t * 6.0 + j, 0.6, run=True)
        TT.pos[j] = _W(x, y, z); TT.yaw[j] = yaw
        if t > BEATS["eat"][1] + 1.0:                         # after the feast the titans wander off (lean back, step out)
            TT.lean[j] = 0.0
    TT.push()
    S["fs"].update(t, wind=(1.0, 0.5)); S["steam"].update(t, wind=(0.6, 0.3)); S["dust"].update(t, wind=(0.8, 0.4))

def light(t):
    LIGHT.apply(story(t))

def check():
    print(f"[f2] S_ENTRY {S_ENTRY:.0f} S_TRAP {S_TRAP:.0f} S0 {S0:.0f}  lead passes the trap at {T_PASS:.2f}, volley {T_VOLLEY:.2f}")
    for t in (0.0, 3.0, 8.0, 12.0, 14.0, 18.0):
        x, y, _ = squad_F(0, t); fx, fy, _ = fem_F(t)
        print(f"[f2] t {t:4.1f} Levi F ({x:6.0f} {y:6.0f})  Female F ({fx:6.0f} {fy:6.0f})")
