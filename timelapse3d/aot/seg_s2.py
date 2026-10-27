"""s2 EREN BURSTS UP -> BRAWL -> THE WALL CLIMB -> FALL, CRYSTAL -> THE TITAN IN THE WALL (Stohess bible s2a-s2e, 40 s,
stohess set, frame W; layout frame S).   SEG=s2 bash aot/forest/render_part2.sh

  0-6    lightning under the street: Eren's titan bursts up through the paving and tackles her
  6-18   the brawl through Stohess: punches, her kick, the crash through the domed church; berserk Eren pins her and bites
  18-26  she breaks away, runs for the district wall and climbs Wall Sina on hardened finger holds; near the top Mikasa cuts
         her fingers
  26-32  she falls; Eren pins her at the wall foot and rips her out of the nape; Annie seals herself in crystal; steam
  32-40  END: the camera cranes up the wall face to where her fingers broke it: a TITAN FACE inside the wall, one eye open;
         Hange and Pastor Nick on the wall top; hold
"""
import math, os, sys, random
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from forest import common as C
from stohess import layout as SL
from stohess.layout import S
import camchan
import seg_s1 as S1
try:
    import bpy
except ImportError:
    bpy = None

DUR = 40.0
BEATS = dict(lightning=(0.4, 3.0), rise=(1.0, 2.2), tackle=2.6, jabs=(4.5, 5.6, 7.0), kick=6.2, church=10.0, bite=(14.0, 16.5),
             run=(16.5, 20.0), climb=(20.0, 25.6), cut=25.6, fall=(25.8, 27.0), pin=(27.0, 29.5), out=29.5, crystal=(29.8, 31.2),
             face=26.0, crane=(32.0, 40.0), people=33.0)
NX, NY = SL.CLIMB_N
PX, PY = NY, -NX
def _off(p, a, b=0.0):
    return (p[0] + a * NX + b * PX, p[1] + a * NY + b * PY)
FOOT = _off(SL.CLIMB, 2.5)

def _W(sx, sy, dz=0.0):
    w = S(sx, sy)
    return (w[0], w[1], C.G(w[0], w[1]) + dz)

FPATH = [(0.0, 60.0, 10.0), (2.6, 62.0, 10.0), (3.4, 76.0, 2.0), (9.5, 82.0, -100.0), (10.2, 82.0, -150.0), (14.0, 332.0, -152.0),
         (16.5, 332.0, -152.0), (19.0, 560.0, -192.0), (20.0,) + FOOT, (27.0,) + SL.CRYSTAL, (40.0,) + SL.CRYSTAL]
EPATH = [(0.0, -60.0, 40.0), (2.2, -60.0, 40.0), (2.6, 45.0, 12.0), (3.4, 62.0, 4.0), (9.5, 68.0, -88.0), (10.2, 70.0, -135.0),
         (14.0, 318.0, -148.0), (16.5, 318.0, -148.0), (19.0, 530.0, -190.0), (20.0,) + _off(SL.CLIMB, 20.0),
         (25.6,) + _off(SL.CLIMB, 20.0), (27.0,) + _off(SL.CRYSTAL, 9.0), (40.0,) + _off(SL.CRYSTAL, 9.0)]
def fem_S(t):
    if 20.0 <= t < 27.0:                                        # on the wall: the climb line (falls straight down)
        return FOOT if t < 25.8 else (FOOT[0] + (SL.CRYSTAL[0] - FOOT[0]) * C.ss(25.8, 27.0, t), FOOT[1] + (SL.CRYSTAL[1] - FOOT[1]) * C.ss(25.8, 27.0, t))
    x, y, _ = C.path_at(FPATH, t); return x, y
def eren_S(t):
    x, y, _ = C.path_at(EPATH, t); return x, y
WALL_YAW = C.yaw_of(-NX, -NY)                                   # facing the wall (outward)

def fem_z(t):
    if t < BEATS["climb"][0]:
        return 0.0
    if t < BEATS["fall"][0]:
        return 44.0 * C.ss(BEATS["climb"][0], BEATS["cut"], t)
    u = (t - BEATS["fall"][0]) / (BEATS["fall"][1] - BEATS["fall"][0])
    return 44.0 * max(0.0, 1.0 - u * u)

def fem_pose(t):
    run = C.fem_run(2 * math.pi * 2.5 * t, lean=24.0)
    if t < 2.6:
        return run, 0.0
    if t < 9.5:
        P = C.FPOSE["guard"]
        P = C.fpose_blend(P, C.FPOSE["kick"], C.bump(t, BEATS["kick"] - 0.3, BEATS["kick"], BEATS["kick"] + 0.15, BEATS["kick"] + 0.5))
        return P, 0.0
    if t < 14.0:
        return run, 0.0
    if t < BEATS["bite"][1]:                                    # pinned, bitten
        w = C.ss(14.0, 14.4, t)
        return C.fpose_blend(run, C.FPOSE["crouch"], w), C.FZ["crouch"] * w
    if t < BEATS["climb"][0]:
        return run, 0.0
    if t < BEATS["fall"][0]:                                    # climbing: hands over hands on hardened finger holds
        a = math.sin(2 * math.pi * 1.1 * t)
        return {"upperarm01.L": (165 + 18 * a, 0, 20), "upperarm01.R": (165 - 18 * a, 0, -20), "lowerarm01.L": (25, 0, 0),
                "lowerarm01.R": (25, 0, 0), "upperleg01.L": (-35 - 20 * a, 0, 0), "upperleg01.R": (-35 + 20 * a, 0, 0),
                "lowerleg01.L": (70, 0, 0), "lowerleg01.R": (70, 0, 0), "neck01": (-25, 0, 0), "spine01": (-6, 0, 0)}, 0.0
    if t < BEATS["pin"][0]:
        return C.FPOSE["guard"], 0.0
    w = C.ss(27.0, 27.6, t)
    return C.fpose_blend(C.FPOSE["guard"], C.FPOSE["sit"], w), C.FZ["sit"] * w

def fem_yaw(t):
    if BEATS["climb"][0] - 0.4 <= t < BEATS["pin"][0]:
        return WALL_YAW
    if t >= BEATS["pin"][0]:
        return WALL_YAW + math.pi
    x2, y2 = fem_S(t + 0.05); x1, y1 = fem_S(t - 0.05)
    if 2.6 <= t < 9.5:
        ex, ey = eren_S(t); x, y = fem_S(t); return C.yaw_of(ex - x, ey - y)
    return C.yaw_of(x2 - x1, y2 - y1 + 1e-9)

def eren_spec(t, P, G6):
    if t < BEATS["rise"][1]:
        return P["crouch"]
    if t < BEATS["tackle"]:
        return G6.blend(P["roar"], P["lunge"], C.ss(2.2, 2.5, t))
    if t < 3.4:
        return P["tackle"]
    if t < 9.5:
        sp = P["boxer"]
        for k, tj in enumerate(BEATS["jabs"]):
            sp = G6.blend(sp, P["jab"] if k % 2 == 0 else P["jab_l"], C.bump(t, tj - 0.2, tj, tj + 0.08, tj + 0.35))
        return sp
    if t < 10.2:
        return P["tackle"]
    if t < 14.0 or BEATS["bite"][1] <= t < BEATS["climb"][0]:
        return G6._walk_feet(P["run"], 2 * math.pi * 1.6 * t, 3.2, lift=1.4)
    if t < BEATS["bite"][1]:
        return P["bite"]
    if t < BEATS["fall"][0]:
        return G6.blend(P["roar"], P["climb"], 0.5 + 0.5 * math.sin(t * 2.0))
    if t < BEATS["pin"][0]:
        return P["crouch"]
    if t < BEATS["out"] + 0.6:
        return P["bite"]
    return G6.blend(P["bite"], P["lie"], C.ss(30.0, 32.0, t))

# ---------------------------------------------------------------- camera (frame S, z above ground; lifted in build)
SEAM_IN = S1.SEAM_S2
def _k(t, p, l, lens):
    return (t, S(*p), S(*l), lens)
CX, CY = SL.CLIMB
KX, KY = SL.CRYSTAL
CAM_KEYS = [
    (0.0, SEAM_IN["pos"], SEAM_IN["look"], SEAM_IN["lens"]),
    _k(1.6, (20.0, 160.0, 140.0), (-60.0, 40.0, 15.0), 32.0),                          # lightning under the street
    _k(3.2, (110.0, 150.0, 120.0), (55.0, 10.0, 12.0), 34.0),                          # the tackle
    _k(7.5, (170.0, 60.0, 150.0), (78.0, -60.0, 12.0), 32.0),
    _k(10.2, (190.0, -30.0, 170.0), (82.0, -140.0, 15.0), 30.0),                       # through the church
    _k(14.8, (360.0, 30.0, 150.0), (325.0, -150.0, 12.0), 34.0),                       # berserk bite
    _k(19.0, (470.0, 60.0, 190.0), (560.0, -190.0, 20.0), 30.0),                       # she runs for the wall
    _k(23.0, _off(SL.CLIMB, 280.0) + (140.0,), (CX, CY, 30.0), 32.0),                  # the climb, wall face-on from the town
    _k(25.6, _off(SL.CLIMB, 120.0, 30.0) + (60.0,), (CX, CY, 46.0), 40.0),             # push-in: Mikasa cuts the fingers
    _k(27.5, _off(SL.CLIMB, 150.0) + (80.0,), (KX, KY, 6.0), 34.0),                    # the fall, the catch
    _k(30.0, _off(SL.CRYSTAL, 45.0, 20.0) + (30.0,), (KX, KY, 3.0), 38.0),             # ripped out, the crystal
    _k(34.0, _off(SL.CLIMB, 70.0) + (22.0,), (CX, CY, 25.0), 35.0),                    # crane up the wall face
    _k(37.0, _off(SL.CLIMB, 60.0) + (38.0,), (CX, CY, SL.FACE_Z), 42.0),
    _k(DUR, _off(SL.CLIMB, 55.0, 2.0) + (SL.FACE_Z + 2.0,), (CX, CY, SL.FACE_Z + 0.5), 45.0),   # END: the titan in the wall
]
CAM = camchan.CamPath(CAM_KEYS, v_in=SEAM_IN["vel"], v_out=(0.0, 0.0, 0.0))
CAM_LIMITS = dict(speed=200.0, yaw=90.0, hmin=15.0, hmax=300.0, pitch=(-10.0, 70.0), lens=(29.0, 46.0))
PLAN = [(0.0, "morning"), (10.0, "day"), (30.0, "afternoon"), (DUR, "afternoon")]
LIGHT = C.LightRig(*C.light_plan(PLAN))
TRACK = {}
S_ = {}

def build(site):
    global CAM
    CAM = camchan.CamPath(C.lift_keys(CAM_KEYS), v_in=SEAM_IN["vel"], v_out=(0.0, 0.0, 0.0))
    import flares
    from stohess import sset
    c = C.coll("S2")
    S_["fem"] = C.Female("S2_Female")
    S_["eren"] = C.Eren("S2_Attack")
    S_["face"] = sset.STATE.get("face")
    S_["church"] = [bpy.data.objects.get(n) for n in ("ST_Church", "ST_ChurchDome", "ST_BellTower")]
    P = C.Batch("S2_People", C.RIDER_MATS)
    S_["pj"] = {nm: P.new(pivot=0.9) for nm in ("mikasa", "annie", "hange", "nick")}
    for nm, j in S_["pj"].items():
        C.person_geo(P.g, j, cloak=nm in ("mikasa", "hange"), odm=nm in ("mikasa", "hange"), hair="blond" if nm == "annie" else "hair")
    P.build(c); S_["P"] = P
    S_["wire"] = C.Wires("S2_MikasaWire", 2, C.mat("F2_Wire", (0.10, 0.10, 0.11), 0.4), c, r=0.08)
    # Annie's crystal
    import bmesh
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0)
    cm = C.mat("S2_Crystal", (0.75, 0.88, 0.95), 0.05, emit=(0.6, 0.8, 0.95), strength=0.6, alpha=0.65)
    cr = C.mesh_obj("S2_Crystal", bm, [cm], c)
    w = _W(KX, KY, 1.0); cr.location = w; cr.rotation_euler = (0, 0, WALL_YAW); cr.scale = (0.01, 0.01, 0.01)
    S_["crystal"] = cr
    # rubble pile where the church stood, revealed as it collapses
    rub = C.mat("ST_WallRubble", (0.60, 0.57, 0.50), 0.9)
    bm = bmesh.new(); rnd = random.Random(10)
    cw = S(*SL.CHURCH); cz = C.G(cw[0], cw[1])
    for k in range(40):
        res = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(rnd.uniform(3, 8), rnd.uniform(3, 8), rnd.uniform(2, 6)), verts=res["verts"])
        bmesh.ops.translate(bm, vec=(cw[0] + rnd.uniform(-18, 18), cw[1] + rnd.uniform(-24, 24), cz + rnd.uniform(0, 3)), verts=res["verts"])
    S_["rubble"] = C.mesh_obj("S2_ChurchRubble", bm, [rub], c); S_["rubble"].hide_render = True
    # FX
    dust = flares.PuffField("S2_Dust", kind="dust", color=(0.66, 0.62, 0.55), alpha=0.6)
    te, pos, vel = [], [], []
    for k in range(50):                                          # paving bursts as Eren comes up; the church; wall chips
        te.append(1.0 + 0.03 * k); pos.append(_W(SL.EREN_UP[0] + rnd.uniform(-10, 10), SL.EREN_UP[1] + rnd.uniform(-10, 10), 2 + 0.3 * k)); vel.append((0, 0, 6))
    for k in range(60):
        te.append(BEATS["church"] + 0.03 * k); pos.append(_W(SL.CHURCH[0] + rnd.uniform(-20, 20), SL.CHURCH[1] + rnd.uniform(-25, 25), 3 + 0.4 * k)); vel.append((rnd.uniform(-3, 3), rnd.uniform(-3, 3), 4))
    for k in range(25):
        te.append(BEATS["cut"] + 0.04 * k); pos.append(_W(CX + 1.5 * NX, CY + 1.5 * NY, SL.FACE_Z + rnd.uniform(-6, 6))); vel.append((NX * 4, NY * 4, -6))
    for tt in np.arange(0.0, 20.0, 0.2):
        x, y = fem_S(float(tt)); te.append(float(tt)); pos.append(_W(x, y, 1.0)); vel.append((0, 0, 1.5))
    dust.add_many(te, pos, vel, r0=3.0, r1=11.0, life=2.6, rise=1.5, alpha=0.55)
    dust.build(c); S_["dust"] = dust
    steam = flares.PuffField("S2_Steam", kind="steam", alpha=0.75)
    te, pos, vel = [], [], []
    for k in range(180):
        tt = rnd.uniform(29.5, 39.0)
        base = SL.CRYSTAL if k % 2 else _off(SL.CRYSTAL, 9.0)
        te.append(tt); pos.append(_W(base[0] + rnd.uniform(-6, 6), base[1] + rnd.uniform(-6, 6), rnd.uniform(2, 10))); vel.append((0, 0, rnd.uniform(4, 8)))
    for k in range(20):                                          # the severed fingers
        te.append(BEATS["cut"] + 0.05 * k); pos.append(_W(FOOT[0], FOOT[1], 44 + 12)); vel.append((0, 0, 2))
    steam.add_many(te, pos, vel, r0=2.5, r1=12.0, life=4.0, rise=4.0)
    steam.build(c); S_["steam"] = steam
    TRACK.update(MIKASA=lambda t: _mik(t)[0] if 24.0 <= t < 26.2 else None,
                 HANGE=lambda t: _W(*_off(SL.wall_inner(SL.CLIMB_ANG + 0.012, -5.0)[0], 0.0), 52.0) if t >= 35.0 else None)

def _mik(t):
    a = np.array(_W(*_off(SL.CLIMB, 120.0, -40.0), 20.0))
    b = np.array(_W(FOOT[0], FOOT[1], 44.0 + 13.0)) + np.array((NX * 3, NY * 3, 0))
    u = C.ss(23.4, BEATS["cut"], t)
    p = a + (b - a) * u + np.array((0, 0, 8 * math.sin(math.pi * u)))
    if t > BEATS["cut"]:
        p = b + np.array((NX * 25, NY * 25, 6)) * C.ss(BEATS["cut"], 27.0, t)
    return tuple(p), b

def update(t):
    import attack_titan as AT
    cam = bpy.context.scene.camera
    lu = (t - BEATS["lightning"][0]) / 2.6
    if lu > -0.01:
        w = S(*SL.EREN_UP); AT.shift_fx(w[0], w[1], min(1.0, max(0.0, lu)), seed=43)
    fem = S_["fem"]
    hide_body = t >= BEATS["crystal"][0] + 0.4
    fem.show(not hide_body)
    if not hide_body:
        pose, dz = fem_pose(t)
        fem.pose(pose)
        x, y = fem_S(t)
        w = _W(x, y, dz + fem_z(t))
        fem.place(w[0], w[1], w[2], fem_yaw(t))
        fem.hardening(max(C.bump(t, 2.6, 3.0, 9.0, 9.5), C.ss(20.0, 20.5, t) * (1 - C.ss(25.6, 26.0, t))))
    er = S_["eren"]
    show_e = t >= BEATS["rise"][0]
    er.show(show_e)
    if show_e:
        er.pose(eren_spec(t, er.P, er.G6))
        x, y = eren_S(t); fx, fy = fem_S(t)
        rise = C.ss(*BEATS["rise"], t)
        w = _W(x, y, -15.0 * (1 - rise))
        er.place(w[0], w[1], w[2], C.yaw_of(fx - x, fy - y + 1e-9))
        er.T.burning(0.7 * C.bump(t, 13.6, 14.0, 17.0, 18.0))
        er.T.steam(0.6 * (1 - rise) + 0.7 * C.ss(29.5, 31.0, t))
    for o in S_["church"]:                                       # the church collapses as they crash through it
        if o is not None:
            o.hide_render = t >= BEATS["church"] + 0.3
    S_["rubble"].hide_render = t < BEATS["church"] + 0.3
    if S_["face"] is not None:
        S_["face"].hide_render = t < BEATS["face"]
    u = C.ss(*BEATS["crystal"], t)
    s = max(0.01, u)
    S_["crystal"].scale = (2.4 * s, 1.3 * s, 1.1 * s)
    P = S_["P"]; pj = S_["pj"]
    mp, hook = _mik(t)
    P.vis[pj["mikasa"]] = 1.0 if 23.4 <= t < 27.2 else 0.0
    P.pos[pj["mikasa"]] = mp; C.person_pose(P, pj["mikasa"], "fly"); P.yaw[pj["mikasa"]] = WALL_YAW
    S_["wire"].update([(tuple(np.array(mp) + np.array((0, 0, 1))), tuple(hook + np.array((-NX * 2.5, -NY * 2.5, 8))))] if 23.4 <= t < BEATS["cut"] else [], cam.location)
    P.vis[pj["annie"]] = 1.0 if t >= BEATS["out"] else 0.0
    P.pos[pj["annie"]] = _W(KX, KY, 0.6); C.person_pose(P, pj["annie"], "fallen"); P.yaw[pj["annie"]] = WALL_YAW
    for nm, da in (("hange", 0.010), ("nick", 0.016)):
        p, _ = SL.wall_inner(SL.CLIMB_ANG + da, -5.0)            # on the wall-top walk, above the hole
        P.vis[pj[nm]] = 1.0 if t >= BEATS["people"] else 0.0
        P.pos[pj[nm]] = _W(p[0], p[1], 50.0); C.person_pose(P, pj[nm], "stand"); P.yaw[pj[nm]] = C.yaw_of(NX, NY)
    P.push()
    S_["dust"].update(t, wind=(1.5, 0.5)); S_["steam"].update(t, wind=(0.8, 0.4))

def light(t):
    LIGHT.apply(t)

def check():
    for t in (0.0, 2.6, 10.0, 14.0, 20.0, 25.6, 27.0, 30.0):
        fx, fy = fem_S(t); ex, ey = eren_S(t)
        print(f"[s2] t {t:4.1f} female S ({fx:5.0f} {fy:5.0f}) z {fem_z(t):4.1f}  eren S ({ex:5.0f} {ey:5.0f}) d {math.hypot(fx - ex, fy - ey):5.1f}")
