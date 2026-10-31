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
    if t < BEATS["fall"][0]:                                    # v8: mid-wall (FEEDBACK_v13 §3), the frozen climb at 22.8
        return CLIMB_H * C.ss(BEATS["climb"][0], 22.8, t)
    u = (t - BEATS["fall"][0]) / (BEATS["fall"][1] - BEATS["fall"][0])
    return CLIMB_H * max(0.0, 1.0 - u * u)
CLIMB_H = 24.0

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
# v8 (FEEDBACK_v13 §3): video clock with FROZEN tableaux (flat knots).  Far sky view: Eren's lightning; FROZEN punch (EP24
# 21:57-22:00); pan along the burning houses to the wall; FROZEN climb (Mikasa on her head, Eren waiting below, slightly
# burning); huge zoom-in on Mikasa; she jumps, the Female falls; camera down: FROZEN Eren on top of her (EP25 13:24); then the
# crane up the wall to the titan face.
STORY_DUR = 40.0
TMAP = [(0.0, 0.0), (3.0, 3.6), (3.4, 4.5), (5.8, 4.5), (8.8, 22.8), (13.0, 22.8), (14.6, 26.6), (15.4, 28.4), (17.8, 28.4),
        (22.4, 38.0), (24.6, 40.0)]
DUR = TMAP[-1][0]
TAB = dict(punch=(3.4, 5.8), climb=(8.8, 13.0), mount=(15.4, 17.8))
TAB_STORY = dict(punch=4.5, climb=22.8, mount=28.4)
def story(t):
    return float(np.interp(t, [k[0] for k in TMAP], [k[1] for k in TMAP]))
def _shots(lift=False):
    from forest import tableau as TB
    fx, fy = fem_S(4.5); ex, ey = eren_S(4.5)
    side = math.degrees(math.atan2(fy - ey, fx - ex)) + 90.0
    hx, hy = FOOT
    nrm = math.degrees(math.atan2(NY, NX))
    sh = [TB.Shot("punch", *TAB["punch"], S((fx + ex) / 2, (fy + ey) / 2, 11.0), az=(side - 20, side + 10), dist=(64, 54), el=(48, 54), lens=32),
          TB.Shot("climb", 8.8, 11.0, S(hx, hy, CLIMB_H + 6.0), az=(nrm - 35, nrm - 15), dist=(105, 85), el=(18, 24), lens=(30, 36)),
          TB.Shot("zoom", 11.0, 13.0, S(hx, hy, CLIMB_H + 15.5), az=(nrm - 15, nrm - 10), dist=(85, 75), el=(20, 22), lens=(36, 190)),
          TB.Shot("mount", *TAB["mount"], S(KX, KY, 4.0), az=(nrm + 70, nrm + 45), dist=(60, 48), el=(22, 30), lens=36)]
    if lift:
        for s_ in sh:
            x, y, z = s_.target; s_.target = (x, y, z + C.G(x, y))
    return sh
CAM_KEYS = [
    (0.0, SEAM_IN["pos"], SEAM_IN["look"], SEAM_IN["lens"]),
    _k(2.2, (10.0, 420.0, 380.0), (-50.0, 40.0, 0.0), 30.0),                       # far sky: lightning under the street
    _k(6.8, (260.0, 60.0, 130.0), (330.0, -150.0, 10.0), 32.0),                     # pan along the burning houses
    _k(8.2, (480.0, 10.0, 120.0), (560.0, -190.0, 20.0), 32.0),                     # ... and the terrain to the wall
    _k(14.4, _off(SL.CLIMB, 140.0) + (70.0,), (KX, KY, 10.0), 34.0),               # she falls; the camera moves down slowly
    _k(19.6, _off(SL.CLIMB, 70.0) + (40.0,), (CX, CY, 30.0), 35.0),                 # crane up the wall face
    _k(21.4, _off(SL.CLIMB, 60.0) + (38.0,), (CX, CY, SL.FACE_Z), 42.0),
    _k(22.4, _off(SL.CLIMB, 55.0, 2.0) + (SL.FACE_Z + 2.0,), (CX, CY, SL.FACE_Z + 0.5), 45.0),   # END: the titan in the wall
    _k(DUR, _off(SL.CLIMB, 54.0, 2.0) + (SL.FACE_Z + 2.0,), (CX, CY, SL.FACE_Z + 0.5), 46.0),
]
def _cam(lift):
    from forest import tableau as TB
    keys = C.lift_keys(CAM_KEYS) if lift else CAM_KEYS
    return TB.make_cam(keys + _shots(lift), v_in=SEAM_IN["vel"], v_out=(0.0, 0.0, 0.0))
CAM = _cam(False)
CAM_LIMITS = dict(speed=1500.0, yaw=300.0, hmin=10.0, hmax=500.0, pitch=(-10.0, 70.0), lens=(29.0, 112.0))
PLAN = [(0.0, "morning"), (10.0, "day"), (30.0, "afternoon"), (34.0, "afternoon"), (38.5, "dusk"), (STORY_DUR, "dusk")]   # v8: dim purple end
LIGHT = C.LightRig(*C.light_plan(PLAN))
TRACK = {}
S_ = {}

def build(site):
    global CAM
    CAM = _cam(True); S_["CAMREF"] = CAM
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
    # v8: Mikasa (people_kit adult preset, red scarf, faceless) standing on the Female's head in the frozen climb
    mk = None
    try:
        import people_kit as PK
        mk = PK.person("mikasa", (0.0, 0.0, 0.0), yaw=WALL_YAW + math.pi, pose="stand", trail=False)
    except Exception as ex:
        print("[s2] people_kit Mikasa failed:", ex, flush=True)
    if mk is None or not hasattr(mk, "location"):
        mk = bpy.data.objects.new("S2_MikasaEmpty", None); c.objects.link(mk)
    S_["mikasa"] = mk; S_["mik0"] = (0.0, 0.0, 0.0)
    S_["mikasa_objs"] = [mk] + list(getattr(mk, "children_recursive", []))
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
    # v8 (FEEDBACK_v13 §3): houses burning along the pan to the wall (flame cones on the roofs + dark smoke columns)
    fire = C.mat("S2_Fire", (1.0, 0.45, 0.10), 0.5, emit=(1.0, 0.42, 0.08), strength=12.0)
    bm = bmesh.new(); rnd2 = random.Random(77)
    smoke = flares.PuffField("S2_FireSmoke", kind="smoke", color=(0.16, 0.14, 0.13), alpha=0.7)
    te, pos, vel = [], [], []
    for (fx_, fy_) in ((190.0, -60.0), (240.0, -120.0), (300.0, -70.0), (350.0, -135.0), (410.0, -95.0), (455.0, -165.0),
                       (130.0, -110.0), (520.0, -120.0)):
        wz = _W(fx_, fy_, 11.0)
        for q in range(3):
            res = bmesh.ops.create_cone(bm, cap_ends=True, segments=6, radius1=rnd2.uniform(3.0, 5.0), radius2=0.2, depth=rnd2.uniform(7.0, 12.0))
            bmesh.ops.translate(bm, vec=(wz[0] + rnd2.uniform(-4, 4), wz[1] + rnd2.uniform(-4, 4), wz[2] + 2.5), verts=res["verts"])
        for tt in np.arange(-4.0, 40.0, 0.35):
            te.append(float(tt)); pos.append((wz[0], wz[1], wz[2] + 5.0)); vel.append((rnd2.uniform(0.5, 1.5), 0.3, 6.0))
    C.mesh_obj("S2_Flames", bm, [fire], c).visible_shadow = False
    smoke.add_many(te, pos, vel, r0=5.0, r1=18.0, life=5.0, rise=4.0, alpha=0.75)
    smoke.build(c); S_["firesmoke"] = smoke
    steam = flares.PuffField("S2_Steam", kind="steam", alpha=0.75)
    te, pos, vel = [], [], []
    for k in range(180):
        tt = rnd.uniform(29.5, 35.5)
        base = SL.CRYSTAL if k % 2 else _off(SL.CRYSTAL, 9.0)
        te.append(tt); pos.append(_W(base[0] + rnd.uniform(-6, 6), base[1] + rnd.uniform(-6, 6), rnd.uniform(2, 10))); vel.append((0, 0, rnd.uniform(1.5, 3.5)))
    for k in range(20):                                          # the severed fingers
        te.append(BEATS["cut"] + 0.05 * k); pos.append(_W(FOOT[0], FOOT[1], 44 + 12)); vel.append((0, 0, 2))
    steam.add_many(te, pos, vel, r0=2.5, r1=10.0, life=3.5, rise=1.5)
    steam.build(c); S_["steam"] = steam
    TRACK.update(MIKASA=lambda t: tuple(S_["mikasa"].location) if 11.0 <= t < 13.4 else None)

def _mik(t):
    a = np.array(_W(*_off(SL.CLIMB, 120.0, -40.0), 20.0))
    b = np.array(_W(FOOT[0], FOOT[1], 44.0 + 13.0)) + np.array((NX * 3, NY * 3, 0))
    u = C.ss(23.4, BEATS["cut"], t)
    p = a + (b - a) * u + np.array((0, 0, 8 * math.sin(math.pi * u)))
    if t > BEATS["cut"]:
        p = b + np.array((NX * 25, NY * 25, 6)) * C.ss(BEATS["cut"], 27.0, t)
    return tuple(p), b

def update(t):
    from forest import tableau as TB
    ts = story(t)
    _update(ts)
    k = next((n for n, (a, b) in TAB.items() if a - 0.25 <= t <= b + 0.25), None)
    fem, er = S_["fem"], S_["eren"]
    mk = S_["mikasa"]
    on_head = TAB["climb"][0] - 0.3 <= t < 13.4
    if 13.4 <= t < 14.6:                                         # Mikasa jumps off her head (arc away from the wall)
        u = C.ss(13.4, 14.6, t)
        p0 = S_["mik0"]; mk.location = (p0[0] + NX * 30 * u, p0[1] + NY * 30 * u, p0[2] + 10 * math.sin(math.pi * u) - 4 * u)
    for o in S_["mikasa_objs"]:
        C.hide(o, not (on_head or 13.4 <= t < 14.6))
    if k is None:
        return
    if k == "punch":                     # Eren's right fist in her face while running; she is knocked off her feet
        er.pose(TB.eren_specs(er.G6, er.P)["punch"])
        fem.pose(TB.POSE_F["punched"])
        x, y = fem_S(4.5); w = _W(x, y, 3.0)
        fem.place(w[0], w[1], w[2], fem_yaw(4.5), pitch=-0.35)
    elif k == "climb":
        fem.pose(TB.POSE_F["climb"])
        er.pose(TB.eren_specs(er.G6, er.P)["wait"]); er.T.burning(0.35)
        bpy.context.view_layer.update()
        hd = fem.bone_world("head", tail=True)
        mk.location = (hd.x, hd.y, hd.z + 0.4); S_["mik0"] = tuple(mk.location)
        for sh in getattr(S_.get("CAMREF"), "shots", []):        # the huge zoom ends ON Mikasa
            if sh.name == "zoom":
                sh.target = (hd.x, hd.y, hd.z + 1.3)
    elif k == "mount":                   # on her back at the wall foot, Eren crouched on top of her
        fem.pose(TB.POSE_F["down"])
        w = _W(KX, KY, 2.2); fem.place(w[0], w[1], w[2], WALL_YAW, pitch=math.pi / 2)
        er.pose(er.P["crouch"])                                 # sitting astride her, crouched low
        ew = _W(KX + 2.5 * NX, KY + 2.5 * NY, -1.8); er.place(ew[0], ew[1], ew[2], WALL_YAW)

def _update(t):
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
    for o in (S_["face"] or []):
        o.hide_render = t < BEATS["face"]
    u = C.ss(*BEATS["crystal"], t)
    s = max(0.01, u)
    S_["crystal"].scale = (2.4 * s, 1.3 * s, 1.1 * s)
    P = S_["P"]; pj = S_["pj"]
    mp, hook = _mik(t)
    P.vis[pj["mikasa"]] = 0.0                                    # v8: the people_kit Mikasa stands on her head instead
    P.pos[pj["mikasa"]] = mp; C.person_pose(P, pj["mikasa"], "fly"); P.yaw[pj["mikasa"]] = WALL_YAW
    S_["wire"].update([], cam.location)
    P.vis[pj["annie"]] = 1.0 if t >= BEATS["out"] else 0.0
    P.pos[pj["annie"]] = _W(KX, KY, 0.6); C.person_pose(P, pj["annie"], "fallen"); P.yaw[pj["annie"]] = WALL_YAW
    for nm, da in (("hange", 0.010), ("nick", 0.016)):
        p, _ = SL.wall_inner(SL.CLIMB_ANG + da, -5.0)            # on the wall-top walk, above the hole
        P.vis[pj[nm]] = 1.0 if t >= BEATS["people"] else 0.0
        P.pos[pj[nm]] = _W(p[0], p[1], 50.0); C.person_pose(P, pj[nm], "stand"); P.yaw[pj[nm]] = C.yaw_of(NX, NY)
    P.push()
    S_["dust"].update(t, wind=(1.5, 0.5)); S_["steam"].update(t, wind=(0.8, 0.4))
    S_["firesmoke"].update(t, wind=(2.0, 0.6))

def light(t):
    LIGHT.apply(story(t))

def check():
    for t in (0.0, 2.6, 10.0, 14.0, 20.0, 25.6, 27.0, 30.0):
        fx, fy = fem_S(t); ex, ey = eren_S(t)
        print(f"[s2] t {t:4.1f} female S ({fx:5.0f} {fy:5.0f}) z {fem_z(t):4.1f}  eren S ({ex:5.0f} {ey:5.0f}) d {math.hypot(fx - ex, fy - ey):5.1f}")

