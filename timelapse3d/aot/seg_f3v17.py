"""f3 v17 FOREST, FROM THE SKY (FEEDBACK_v15: everything after the titans eat her REBUILT; Principle A: far sky views +
speed where the models are weak; events implied by light, steam, toppling trees and dust).  Replaces seg_f3 in the cut.
SEG=f3v17 bash aot/forest/render_part2.sh      (seams: f2 end -> here -> s1v15 / seg_s1 frame 0 = seg_f3.SEAM_S1)

  0.0-1.8   above the canopy at sunset: a LIGHT BEAM strikes the trees (Annie shifts again), a steam column through the crowns
  1.8-4.2   the chase under the canopy, seen from above: crowns topple in a line, dust and steam burst up through the gap
  4.2-5.6   a second, golden beam on the rim of the duel clearing: Eren's titan rises in the clearing
  5.0-8.0   the duel in the open clearing: she bursts in, his punch, her high KICK - he goes down across a fallen trunk
  8.0-9.4   she crouches over his nape and bites him out (steam)
  9.4-11.0  she runs to the clearing's north edge and sits against a trunk, hands over her nape
  11.0-12.6 Levi's cuts (white slashes), steam from her mouth, two small figures fly off west with Eren
  12.6-17   the camera climbs into the wide sky looking SW (= s1's first frame)
"""
import math, os, sys, random
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from forest import common as C
from forest import layout as LY
import camchan
import seg_f3 as F3
try:
    import bpy
except ImportError:
    bpy = None

F = C.F
DUR = 17.0
TS = 1.4                                                         # titans a little over canon so they read from the sky
DX, DY = LY.DUEL_F
BEAM = F3.BEAM_F                                                 # (150, 1250): her re-shift
EREN0 = (DX + 20.0, DY - 40.0)                                   # his beam: the clearing's south side (v17c: off the camera)
SIT = (DX + 45.0, DY + 62.0)                                     # the trunk she sits against (north edge)
TRUNK = (DX + 33.0, DY + 31.0)                                   # the fallen trunk he goes down on
BEATS = dict(beam=(0.6, 2.2), chase=(1.8, 4.6), ebeam=(4.2, 5.8), rise=(4.8, 5.6), burst=5.0, punch=6.2, kick=(6.9, 7.3),
             down=(7.3, 7.9), bite=(8.0, 9.4), run=(9.4, 10.6), sit=(10.6, 11.2), cuts=(11.2, 12.2), fly=(11.8, 13.2))

def _W(fx, fy, dz=0.0):
    w = F(fx, fy)
    return (w[0], w[1], C.G(w[0], w[1]) + dz)

# ---------------------------------------------------------------- paths (frame F)
CHASE = [(1.8, BEAM[0] + 20, BEAM[1] + 40), (3.0, 220.0, 1420.0), (4.2, 270.0, 1640.0), (5.0, DX - 55, DY + 55)]   # v17c: in from the NW
FPATH = CHASE + [(5.6, DX - 5, DY + 20), (6.9, DX + 11, DY + 27), (8.0, DX + 15, DY + 29), (9.4, DX + 15, DY + 29),
                 (10.6, SIT[0] - 4, SIT[1] - 5), (17.0, SIT[0] - 4, SIT[1] - 5)]
EPATH = [(0.0,) + EREN0, (5.6,) + EREN0, (6.2, DX + 19, DY + 7), (7.3, DX + 27, DY + 17), (17.0, TRUNK[0] - 2, TRUNK[1] - 4)]
def fem_F(t):
    x, y, _ = C.path_at(FPATH, max(t, CHASE[0][0])); return x, y
def eren_F(t):
    x, y, _ = C.path_at(EPATH, t); return x, y

def fem_state(t, TB):
    """(pose, yaw, pitch, dz)"""
    x, y = fem_F(t)
    ex, ey = eren_F(t)
    face_e = C.yaw_of(ex - x, ey - y + 1e-9)
    run = C.fem_run(2 * math.pi * 3.0 * t, lean=26.0)
    def head(tt):
        x2, y2 = fem_F(tt + 0.05); x1, y1 = fem_F(tt - 0.05); return C.yaw_of(x2 - x1, y2 - y1 + 1e-9)
    if t < 5.6:
        return run, head(t), 0.0, 0.0
    if t < BEATS["punch"] + 0.4:                                  # guard up, he punches: she staggers back
        st = C.bump(t, BEATS["punch"], BEATS["punch"] + 0.12, BEATS["punch"] + 0.3, BEATS["punch"] + 0.5)
        return C.fpose_blend(C.FPOSE["guard"], TB.POSE_F["punched"], st), face_e, -0.25 * st, 0.0
    if t < BEATS["down"][1]:                                      # the high kick to his head
        u = C.bump(t, BEATS["kick"][0] - 0.3, BEATS["kick"][0], BEATS["kick"][1] + 0.2, BEATS["down"][1])
        return C.fpose_blend(C.FPOSE["guard"], TB.POSE_F["highkick"], u), face_e, 0.0, 0.0
    if t < BEATS["bite"][1]:                                      # crouched over his nape
        u = C.ss(BEATS["bite"][0], BEATS["bite"][0] + 0.4, t)
        return C.fpose_blend(C.FPOSE["guard"], C.FPOSE["crouch"], u), face_e, 0.0, C.FZ["crouch"] * TS * u
    if t < BEATS["sit"][0]:
        return run, head(t), 0.0, 0.0
    u = C.ss(*BEATS["sit"], t)                                    # sits against the trunk, hands over her nape
    P = C.fpose_blend(C.FPOSE["sit"], TB.POSE_F["nape"], 0.55)
    return C.fpose_blend(run, P, u), C.yaw_of(-0.6, -1.0), 0.0, C.FZ["sit"] * TS * u

def eren_state(t, er, TB):
    P, G6 = er.P, er.G6
    if t < BEATS["rise"][1]:
        return G6.blend(P["crouch"], P["roar"], C.ss(5.2, 5.6, t))
    if t < BEATS["punch"] - 0.3:
        return G6._walk_feet(P["run"], 2 * math.pi * 2.4 * t, 3.2, lift=1.4)
    if t < BEATS["kick"][0]:
        return G6.blend(P["boxer"], P["jab"], C.bump(t, BEATS["punch"] - 0.25, BEATS["punch"], BEATS["punch"] + 0.15, BEATS["punch"] + 0.45))
    if t < BEATS["down"][0]:
        return P["boxer"]
    return G6.blend(P["boxer"], P["lie"], C.ss(*BEATS["down"], t))

# ---------------------------------------------------------------- camera: one sky view at fixed height, translating
H = 275.0                                                        # v17b: 165 m was below the ~130 m crowns' sight line
OFF = (-75.0, -100.0)                                            # steep (~65 deg) look DOWN into the clearing from the SSW
LENS = 60.0
def _ck(t, fx, fy, lz=4.0, lens=LENS, h=H):
    return (t, F(fx + OFF[0], fy + OFF[1], h), F(fx, fy, lz), lens)
def _sweep(t, p, yaw_deg, d, dz, lens):
    a = math.radians(yaw_deg)
    return (t, F(*p), F(p[0] + d * math.cos(a), p[1] + d * math.sin(a), p[2] + dz), lens)
CAM_KEYS = [
    (0.0, F3.SEAM_IN["pos"], F3.SEAM_IN["look"], F3.SEAM_IN["lens"]),   # f2's end above the trap clearing
    _ck(1.4, BEAM[0], BEAM[1], 30.0, 36.0, 320.0),                 # her beam strikes the canopy
    _ck(3.2, 225.0, 1450.0, 20.0, 38.0, 300.0),                    # the toppling line through the crowns
    (3.9, F(DX - 38, DY - 36, 250.0), F(DX - 10, DY + 10, 8.0), 34.0),   # straight down INTO the clearing (no crowns crossed)
    # v17c (cloud QA): the duel from a LOW OBLIQUE camera standing inside the open clearing (no crowns between), ~50 m up,
    # 80-110 m off, 32-36 mm: the titans 1/5-1/3 of the frame, still far enough to hide the animation
    (5.2, F(DX - 38, DY - 36, 54.0), F(DX, DY, 12.0), 26.0),   # his golden beam on the rim, she bursts in
    (7.4, F(DX - 38, DY - 36, 50.0), F(DX + 20, DY + 20, 11.0), 27.0),     # punch, the kick, he goes down
    (9.2, F(DX - 36, DY - 36, 50.0), F(DX + 25, DY + 25, 9.0), 27.0),      # the bite
    (11.4, F(DX - 20, DY - 40, 56.0), F(SIT[0] - 2, SIT[1] - 2, 14.0), 36.0),   # the sit, Levi's cuts
    _ck(12.8, SIT[0] - 20, SIT[1] - 20, 6.0, 36.0, 310.0),
    _sweep(14.0, (SIT[0] - 75, SIT[1] - 90, 400.0), -20.0, 700.0, -120.0, 34.0),   # climbing, the view sweeps round
    _sweep(15.3, (SIT[0] - 140, SIT[1] - 190, 560.0), -80.0, 1600.0, 250.0, 30.0),  # through the south toward SW
    (DUR, F3.SEAM_S1["pos"], F3.SEAM_S1["look"], F3.SEAM_S1["lens"]),   # up into the wide sky, SW (= s1 frame 0)
]
LIFT_SKIP = (0, len(CAM_KEYS) - 1)
CAM = camchan.CamPath(CAM_KEYS, v_in=F3.SEAM_IN["vel"], v_out=F3.SEAM_S1["vel"])
CAM_LIMITS = dict(speed=2500.0, yaw=200.0, hmin=60.0, hmax=1300.0, pitch=(5.0, 80.0), lens=(24.0, 46.0))
PLAN = [(0.0, "afternoon"), (13.0, "afternoon"), (15.5, "golden"), (DUR, "sunset")]       # v17b: readable, not murky
LIGHT = C.LightRig(*C.light_plan(PLAN))
TRACK = {}
S = {}

def build(site):
    global CAM
    CAM = camchan.CamPath(C.lift_keys(CAM_KEYS, skip=LIFT_SKIP), v_in=F3.SEAM_IN["vel"], v_out=F3.SEAM_S1["vel"])
    import flares, bmesh
    from forest import fset
    c = C.coll("F3V")
    S["fem"] = C.Female("F3V_Female"); S["fem"].rig.scale = tuple(v * TS for v in S["fem"].rig.scale)
    S["eren"] = C.Eren("F3V_Attack")
    rnd = random.Random(17)
    # toppling crowns along the chase line + the fallen trunk in the clearing (copies of the forest's tree prototype)
    bark = C.mat("F_Bark", (0.20, 0.11, 0.07), 0.9)
    leaf = C.mat("F_Leaf", (0.040, 0.085, 0.035), 0.85); leaf2 = C.mat("F_Leaf2", (0.055, 0.11, 0.045), 0.85)
    proto = fset.tree_proto("F3V_TreeProto", 33, c, [bark, leaf, leaf2])
    S["fall"] = []
    for k in range(9):
        u = (k + 0.5) / 9; tt = CHASE[0][0] + u * (CHASE[-1][0] - CHASE[0][0])
        x, y = fem_F(tt)
        if math.hypot(x - DX, y - DY) < LY.DUEL_R + 15.0:          # v17c: none inside the open clearing (the duel camera stands there)
            continue
        side = 9.0 if k % 2 else -9.0
        ob = proto.copy(); c.objects.link(ob)
        p = _W(x + side, y + rnd.uniform(-4, 4), -0.5); ob.location = p
        s = rnd.uniform(0.75, 0.95); ob.scale = (s, s, s)
        ob.rotation_mode = "ZXY"; az = rnd.uniform(0, math.tau)
        S["fall"].append((ob, tt + 0.15, az, rnd.uniform(1.1, 1.5)))
    tr = proto.copy(); c.objects.link(tr)                          # the fallen trunk he goes down on
    tr.location = _W(TRUNK[0] - 4, TRUNK[1] - 4, 1.5); tr.rotation_mode = "ZXY"     # v17c: ~32 m, lying NE (away from the camera)
    tr.rotation_euler = (math.radians(88), 0, math.radians(135)); tr.scale = (0.35, 0.35, 0.35)
    st = proto.copy(); c.objects.link(st); st.location = _W(SIT[0] + 6, SIT[1] + 8, -0.5)   # the trunk she sits against
    # FX
    dust = flares.PuffField("F3V_Dust", kind="dust", color=(0.42, 0.38, 0.30), alpha=0.5)
    steam = flares.PuffField("F3V_Steam", kind="steam", alpha=0.75)
    te, pos, vel = [], [], []
    for ob, t0, az, sp in S["fall"]:                               # crowns crashing: dust + leaves burst up through the gap
        for q in range(8):
            te.append(t0 + 0.4 + 0.05 * q); p = np.array(ob.location) + np.array((rnd.uniform(-10, 10), rnd.uniform(-10, 10), 70 + 3 * q))
            pos.append(tuple(p)); vel.append((rnd.uniform(-3, 3), rnd.uniform(-3, 3), 4.0))
    for tt in np.arange(5.6, 11.0, 0.15):                          # the fight's dust in the clearing
        x, y = fem_F(float(tt)); te.append(float(tt)); pos.append(_W(x, y, 2.0)); vel.append((rnd.uniform(-2, 2), rnd.uniform(-2, 2), 3.0))
    for k in range(20):                                            # he hits the trunk
        te.append(BEATS["down"][0] + 0.02 * k); pos.append(_W(TRUNK[0] + rnd.uniform(-12, 12), TRUNK[1] + rnd.uniform(-8, 8), 3.0)); vel.append((rnd.uniform(-5, 5), rnd.uniform(-5, 5), 5.0))
    dust.add_many(te, pos, vel, r0=3.0, r1=9.0, life=2.0, rise=2.0, alpha=0.4)
    dust.build(c); S["dust"] = dust
    te, pos, vel = [], [], []
    for k in range(60):                                            # her beam: steam column up through the crowns
        te.append(BEATS["beam"][0] + 0.03 * k); pos.append(_W(BEAM[0] + rnd.uniform(-10, 10), BEAM[1] + rnd.uniform(-10, 10), 20 + 1.6 * k)); vel.append((0, 0, 8))
    for tt in np.arange(CHASE[0][0], CHASE[-1][0], 0.12):          # the chase: steam / leaf puffs above her line
        x, y = fem_F(float(tt)); te.append(float(tt)); pos.append(_W(x, y, 85.0)); vel.append((0, 0, 5))
    for k in range(35):                                            # his rise
        te.append(BEATS["ebeam"][0] + 0.025 * k); pos.append(_W(EREN0[0] + rnd.uniform(-12, 12), EREN0[1] + rnd.uniform(-12, 12), rnd.uniform(2, 30))); vel.append((0, 0, 6))
    for k in range(60):                                            # the bite (his nape)
        te.append(BEATS["bite"][0] + 0.02 * k); pos.append(_W(TRUNK[0] + rnd.uniform(-5, 5), TRUNK[1] + rnd.uniform(-5, 5), rnd.uniform(3, 12))); vel.append((0, 0, 4))
    for k in range(50):                                            # Levi's cuts: her mouth / shoulders steam
        te.append(BEATS["cuts"][0] + 0.02 * k); pos.append(_W(SIT[0] + rnd.uniform(-5, 5), SIT[1] + rnd.uniform(-5, 5), rnd.uniform(8, 18))); vel.append((0, 0, 5))
    steam.add_many(te, pos, vel, r0=2.0, r1=8.0, life=2.4, rise=2.0)
    steam.build(c); S["steam"] = steam
    # Levi's slashes: short bright streaks round her head, and two small figures (Levi carrying Eren, Mikasa) flying west
    S["slash"] = C.Wires("F3V_Slash", 6, C.mat("F3V_SlashMat", (1, 1, 1), 0.3, emit=(1, 1, 1), strength=8.0), c, r=0.25)
    P = C.Batch("F3V_People", C.RIDER_MATS)
    S["pp"] = [P.new(pivot=0.9) for _ in range(2)]
    for j in S["pp"]:
        C.person_geo(P.g, j, cloak=True, odm=True)
    P.build(c); S["P"] = P

def update(t):
    import attack_titan as AT
    from forest import tableau as TB
    cam = bpy.context.scene.camera
    for (fx_, fy_), (a, b), sc in ((BEAM, BEATS["beam"], TS), (EREN0, BEATS["ebeam"], TS)):
        u = (t - a) / (b - a)
        if u > -0.01:
            w = F(fx_, fy_); fx = AT.shift_fx(w[0], w[1], min(1.0, max(0.0, u)), seed=61 if fx_ == BEAM[0] else 62, scale=sc * 0.7)
            if u > 1.0:
                fx["dome_d"].default_value *= 1.0 - C.ss(1.0, 1.25, u); fx["dome"].hide_render = u > 1.25
    fem = S["fem"]
    vis = t >= CHASE[0][0]
    fem.show(vis)
    if vis:
        pose, yaw, pitch, dz = fem_state(t, TB)
        fem.pose(pose); x, y = fem_F(t); w = _W(x, y, dz)
        fem.place(w[0], w[1], w[2], yaw, pitch=pitch)
        fem.hardening(C.ss(BEATS["sit"][0], BEATS["sit"][1], t) * 0.7)
    er = S["eren"]
    se = t >= BEATS["rise"][0]
    er.show(se)
    if se:
        er.pose(eren_state(t, er, TB))
        x, y = eren_F(t); fx_, fy_ = fem_F(t)
        rise = C.ss(*BEATS["rise"], t)
        w = _W(x, y, -14.0 * TS * (1 - rise))
        down = C.ss(*BEATS["down"], t)
        er.place(w[0], w[1], w[2] + 2.0 * down, C.yaw_of(fx_ - x, fy_ - y + 1e-9), pitch=-1.35 * down)
        er.T.holder.scale = (TS, TS, TS)
        er.T.steam(0.6 * (1 - rise) + 0.8 * C.ss(BEATS["bite"][0], BEATS["bite"][1], t))
    for ob, t0, az, sp in S["fall"]:                               # crowns topple as she tears past
        u = min(1.0, max(0.0, (t - t0) * sp)) ** 2
        ob.rotation_euler = (math.radians(84) * u, 0.0, az)
    segs = []
    if BEATS["cuts"][0] <= t < BEATS["cuts"][1]:
        hd = fem.bone_world("head", tail=True)
        for k in range(3):
            ph = (t - BEATS["cuts"][0]) * 9.0 + k * 2.1
            a = np.array((hd.x + 7 * math.cos(ph), hd.y + 7 * math.sin(ph), hd.z - 2 + 2 * k))
            b = a + np.array((5 * math.cos(ph + 1.4), 5 * math.sin(ph + 1.4), 1.5))
            segs.append((tuple(a), tuple(b)))
    S["slash"].update(segs, cam.location)
    P = S["P"]
    u = C.ss(*BEATS["fly"], t)
    for k, j in enumerate(S["pp"]):
        p0 = np.array(_W(SIT[0], SIT[1], 16.0)); p1 = np.array(_W(SIT[0] - 160 - 15 * k, SIT[1] - 40 + 10 * k, 60.0))
        P.vis[j] = 1.0 if BEATS["fly"][0] <= t < BEATS["fly"][1] + 0.5 else 0.0
        P.pos[j] = tuple(p0 + (p1 - p0) * u + np.array((0, 0, 20 * math.sin(math.pi * u))))
        C.person_pose(P, j, "fly"); P.yaw[j] = C.yaw_of(-1.0, -0.25)
    P.push()
    S["dust"].update(t, wind=(1.5, 0.4)); S["steam"].update(t, wind=(1.0, 0.4))

def light(t):
    LIGHT.apply(t)
    bpy.context.scene.view_settings.exposure += 0.7                 # v17c: the forest floor read murky

def check():
    for t in (0.0, 1.8, 4.2, 5.6, 6.2, 7.3, 8.0, 9.4, 10.6, 12.0):
        fx, fy = fem_F(t); ex, ey = eren_F(t)
        print(f"[f3v17] t {t:5.2f} female F ({fx:5.0f} {fy:5.0f})  eren F ({ex:5.0f} {ey:5.0f}) d {math.hypot(fx - ex, fy - ey):5.1f}")
