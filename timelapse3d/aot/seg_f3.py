"""f3 RE-SHIFT -> LEVI SQUAD -> EREN vs FEMALE -> RESCUE -> RETREAT (bible beats f11-f16, 56 s, forest set, frame W; F layout).
SEG=f3 bash aot/forest/render_part2.sh

  0-8    above the canopy at sunset: a light beam strikes the trees (Annie re-shifts, ep21 7:57); the camera drops into the
         trunk colonnade; she chases Levi's squad (ODM) through the trees
  8-18   the squad blinds her and cuts her shoulders; she sits against a trunk, shams, rises and kills Erd, Petra, Oluo
  18-32  Eren bites his hand: lightning, his titan rises (swampy clearing); the duel (Eren attacks from frame right), he pins
         her against a tree, she breaks away and kicks his HEAD off on the fallen trunk
  32-38  she bites Eren out of the nape and runs off with him in her mouth; Mikasa chases
  38-48  Mikasa decoys, Levi spins and cuts, she sits against the trunk guarding her nape; Levi cuts her mouth open, Eren is
         pulled out, they fly west ("We're pulling out!")
  48-56  retreat over the plain: wagons and riders heading south, corpses dropped, abnormals behind, green smoke; the camera
         rises into a wide sky looking SW (toward Wall Sina / Stohess) = s1 frame 0
"""
import math, os, sys, random
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from forest import common as C
from forest import layout as LY
import camchan
import seg_f2 as F2
try:
    import bpy
except ImportError:
    bpy = None

DUR = 56.0
BEAM_F = (150.0, 1250.0)
SHAM_F = (255.0, 1530.0)                 # the trunk she sits against while shamming
EREN_F = (340.0, 1585.0)                 # where Eren shifts (the swampy clearing rim)
SX, SY = LY.SWAMP_F
KX, KY = LY.KICK_F
RX, RY = LY.RESCUE_F
BEATS = dict(beam=(1.4, 3.4), chase=(3.4, 8.0), blind=(8.0, 10.0), sham=(10.0, 12.6), kills=(13.2, 14.4, 16.0),
             shift=(17.6, 19.6), roar=(19.6, 20.6), charge=(20.6, 22.2), punch=22.2, kick1=23.4, pin=(25.0, 27.2),
             escape=(27.4, 30.0), headkick=30.6, bite=(32.0, 33.6), carry=(33.6, 38.0), decoy=(38.5, 41.0),
             spin=(40.4, 42.6), sit=(42.0, 43.5), mouth=44.6, out=(45.0, 48.0), retreat=(48.0, 56.0),
             drop=(50.0, 51.2), green=52.0)
F = C.F

def _W(fx, fy, dz=0.0):
    w = F(fx, fy)
    return (w[0], w[1], C.G(w[0], w[1]) + dz)

# ---------------------------------------------------------------- the Female's path (F) and pose plan
FPATH = [(0.0, BEAM_F[0], BEAM_F[1]), (3.4, BEAM_F[0], BEAM_F[1]), (6.0, 200.0, 1400.0), (8.0, 235.0, 1490.0),
         (10.0, SHAM_F[0] - 4, SHAM_F[1] - 6), (12.6, SHAM_F[0] - 4, SHAM_F[1] - 6), (14.4, 280.0, 1560.0),
         (16.0, 300.0, 1570.0), (20.6, 300.0, 1572.0), (22.2, 302.0, 1578.0), (25.0, 312.0, 1600.0), (27.2, 312.0, 1602.0),
         (30.0, KX - 18.0, KY - 12.0), (30.6, KX - 14.0, KY - 10.0), (33.6, KX - 12.0, KY - 6.0), (38.0, RX - 30.0, RY - 20.0),
         (42.0, RX - 9.0, RY - 7.5), (56.0, RX - 9.0, RY - 7.5)]   # seated clear of the rescue trunk
def fem_F(t):
    x, y, yaw = C.path_at(FPATH, t)
    return x, y

def fem_yaw(t):
    if t < 3.4:
        return 0.6
    if 8.0 <= t < 12.6:                                         # back to the trunk, facing the squad (SW)
        return 2.4
    if 16.0 <= t < 30.0:                                        # facing Eren (east, he comes from frame right)
        x, y = fem_F(t); ex, ey = eren_F(t)
        return C.yaw_of(ex - x, ey - y)
    if 30.0 <= t < 33.6:
        return C.yaw_of(1.0, 0.6)
    if t >= 42.0:                                               # seated against the rescue trunk, facing SW
        return 2.3
    x2, y2 = fem_F(t + 0.05); x1, y1 = fem_F(t - 0.05)
    return C.yaw_of(x2 - x1, y2 - y1)

def fem_pose(t):
    run = C.fem_run(2 * math.pi * 2.4 * t, lean=26.0)
    if t < BEATS["beam"][1]:
        return {}, 0.0, False
    if t < 8.0:
        return run, 0.0, True
    if t < 12.6:                                                # blinded: guard -> sit (sham) with hands over the nape
        w = C.ss(9.6, 10.4, t) * (1 - C.ss(12.2, 12.6, t))
        P = C.fpose_blend(C.FPOSE["guard"], C.FPOSE["sit"], w)
        P = C.fpose_blend(P, C.FPOSE["nape"], 0.7 * w)
        return P, C.FZ["sit"] * w, True
    if t < 16.6:                                                # rises, kills Erd / Petra / Oluo
        P = run
        for ts in BEATS["kills"]:
            P = C.fpose_blend(P, C.FPOSE["swat"], C.bump(t, ts - 0.3, ts - 0.05, ts + 0.15, ts + 0.45))
        return P, 0.0, True
    if t < 27.4:                                                # duel: guard (hardened), counter kick, pinned
        P = C.FPOSE["guard"]
        P = C.fpose_blend(P, C.FPOSE["kick"], C.bump(t, BEATS["kick1"] - 0.3, BEATS["kick1"], BEATS["kick1"] + 0.15, BEATS["kick1"] + 0.5))
        pin = C.bump(t, BEATS["pin"][0], BEATS["pin"][0] + 0.4, BEATS["pin"][1] - 0.2, BEATS["pin"][1] + 0.2)
        P = C.fpose_blend(P, C.FPOSE["crouch"], 0.6 * pin)
        return P, C.FZ["crouch"] * 0.6 * pin, True
    if t < 30.2:
        return run, 0.0, True
    if t < 32.0:                                                # the head kick
        w = C.bump(t, 30.2, BEATS["headkick"], 31.0, 31.6)
        return C.fpose_blend(C.FPOSE["stand"], C.FPOSE["kick"], w), 0.0, True
    if t < 33.6:                                                # bends to his nape, bites him out
        w = C.bump(t, 32.0, 32.5, 33.2, 33.6)
        return C.fpose_blend(C.FPOSE["stand"], C.FPOSE["crouch"], w), C.FZ["crouch"] * w, True
    if t < 42.0:
        P = run
        if t > 40.4:                                            # Levi's spin cuts: she stumbles
            P = C.fpose_blend(P, C.FPOSE["crouch"], C.ss(40.4, 42.0, t))
            return P, C.FZ["crouch"] * C.ss(40.4, 42.0, t), True
        return P, 0.0, True
    w = C.ss(42.0, 43.5, t)
    P = C.fpose_blend(C.FPOSE["crouch"], C.FPOSE["sit"], w)
    P = C.fpose_blend(P, C.FPOSE["nape"], 0.8 * w)              # hands guarding her nape
    return P, C.FZ["crouch"] * (1 - w) + C.FZ["sit"] * w, True

# ---------------------------------------------------------------- Eren's titan
EPATH = [(17.6, EREN_F[0], EREN_F[1]), (20.6, EREN_F[0], EREN_F[1]), (22.2, 316.0, 1580.0), (25.0, 322.0, 1597.0),
         (27.2, 322.0, 1600.0), (30.0, KX - 6.0, KY - 4.0), (30.6, KX - 3.0, KY - 2.0), (56.0, KX - 3.0, KY - 2.0)]
def eren_F(t):
    x, y, _ = C.path_at(EPATH, t)
    return x, y

def eren_spec(t, P, G6):
    if t < BEATS["roar"][0]:
        return P["crouch"], False
    if t < BEATS["roar"][1]:
        return G6.blend(P["crouch"], P["roar"], C.ss(BEATS["roar"][0], BEATS["roar"][0] + 0.4, t)), False
    if t < BEATS["punch"] - 0.25:
        return G6._walk_feet(P["run"], 2 * math.pi * 1.6 * t, 3.2, lift=1.4), False
    if t < BEATS["pin"][0]:
        sp = G6.blend(P["boxer"], P["jab"], C.bump(t, BEATS["punch"] - 0.25, BEATS["punch"], BEATS["punch"] + 0.1, BEATS["punch"] + 0.4))
        sp = G6.blend(sp, P["jab_l"], C.bump(t, 24.0, 24.2, 24.3, 24.6))
        return sp, False
    if t < BEATS["pin"][1]:                                     # pins her at the tree, pounding
        sp = G6.blend(P["tackle"], P["slam"], 0.5 + 0.5 * math.sin(t * 9.0))
        return sp, False
    if t < BEATS["headkick"]:
        return G6._walk_feet(P["run"], 2 * math.pi * 1.6 * t, 3.2, lift=1.4), False
    u = C.ss(BEATS["headkick"], BEATS["headkick"] + 1.2, t)     # headless: falls forward on the trunk
    return G6.blend(P["lunge"], P["lie"], u), True

# ---------------------------------------------------------------- flyers (ODM): Erd, Petra, Oluo, Eren (human), Mikasa, Levi
def _orbit(c, r, z, t, w=2.2, ph=0.0):
    return (c[0] + r * math.cos(w * t + ph), c[1] + r * math.sin(w * t + ph), z + 3 * math.sin(3 * t + ph))
def flyer_F(name, t):
    """(x, y, z above ground, visible, flying)"""
    if name in ("erd", "petra", "oluo"):
        k = ("erd", "petra", "oluo").index(name)
        death = BEATS["kills"][k]
        if t < 3.4:
            return 0, 0, 0, False, True
        if t < 8.0:                                              # fleeing NE ahead of her through the trunks
            u = (t - 3.4) / 4.6
            x = BEAM_F[0] + 60 + (SHAM_F[0] + 30 - BEAM_F[0] - 60) * u + 8 * k
            y = BEAM_F[1] + 120 + (SHAM_F[1] + 40 - BEAM_F[1] - 120) * u - 6 * k
            return x, y, 24 + 6 * math.sin(2 * t + k), True, True
        if t < death:
            fx, fy = fem_F(t)
            x, y, z = _orbit((fx, fy), 16 + 4 * k, 12 + 3 * k, t, 2.4, k * 2.1)
            return x, y, z, True, True
        fx, fy = fem_F(death)
        x, y, z = _orbit((fx, fy), 16 + 4 * k, 12 + 3 * k, death, 2.4, k * 2.1)
        fall = C.ss(death, death + 0.8, t)
        return x, y, z * (1 - fall), t < death + 3.0, False
    if name == "eren_h":
        if 3.4 <= t < 17.4:
            fx, fy = flyer_F("petra", min(t, 13.0))[:2]
            return fx - 10, fy - 6, 22, True, True
        if 33.6 <= t < BEATS["mouth"] + 0.4:                    # in her mouth (placed in update from the head bone)
            return 0, 0, 0, True, False
        if BEATS["mouth"] + 0.4 <= t < 48.0:                    # carried out by Levi (update)
            return 0, 0, 0, True, True
        return 0, 0, 0, False, True
    if name == "mikasa":
        if t < 33.6:
            return 0, 0, 0, False, True
        fx, fy = fem_F(t)
        if t < BEATS["decoy"][0]:
            u = C.ss(33.6, 38.5, t)
            return fx - 60 + 40 * u, fy - 50 + 30 * u, 20, True, True
        if t < 45.0:
            x, y, z = _orbit((fx, fy), 14, 11, t, 3.0, 0.5)
            return x, y, z, True, True
        u = C.ss(45.0, 48.0, t)
        return RX - 20 - 380 * u, RY - 30 - 120 * u, 20 + 40 * u, True, True
    if name == "levi":
        if t < 38.4:
            return 0, 0, 0, False, True
        fx, fy = fem_F(t)
        if t < BEATS["spin"][0]:
            u = C.ss(38.4, 40.4, t)
            return fx + 90 - 80 * u, fy - 70 + 60 * u, 28 - 10 * u, True, True
        if t < 44.4:
            x, y, z = _orbit((fx, fy), 7 + 4 * math.sin(t), 4 + 6 * C.ss(40.4, 44.4, t), t, 6.0, 1.0)
            return x, y, z, True, True
        if t < 45.0:
            return fx - 4, fy - 3, 7.5, True, False
        u = C.ss(45.0, 48.0, t)
        return RX - 24 - 400 * u, RY - 24 - 110 * u, 18 + 45 * u, True, True
    return 0, 0, 0, False, True
FLYERS = ("erd", "petra", "oluo", "eren_h", "mikasa", "levi")

# ---------------------------------------------------------------- the retreat column (F), from the forest's west edge south
RET_ROUTE = [(-1560.0, 1500.0), (-1650.0, 600.0), (-1700.0, -600.0), (-1650.0, -2200.0), (-1500.0, -4000.0), (-1200.0, -6000.0)]
def _ret_dense():
    pts = np.array(RET_ROUTE); s = np.concatenate([[0.0], np.cumsum(np.hypot(*np.diff(pts, axis=0).T))])
    return pts, s
RPTS, RS = _ret_dense()
def ret_at(s):
    s = max(0.0, min(RS[-1], s))
    i = max(0, min(len(RS) - 2, int(np.searchsorted(RS, s) - 1)))
    u = (s - RS[i]) / (RS[i + 1] - RS[i]); d = RPTS[i + 1] - RPTS[i]
    p = RPTS[i] + d * u
    return float(p[0]), float(p[1]), math.atan2(-d[0], d[1])
def ret_head(t):
    return 900.0 + 70.0 * (t - 48.0)                            # 70 m/s time-lapse
NRET = 34

# ---------------------------------------------------------------- camera
SEAM_IN = dict(pos=F2.SEAM_F3["pos"], look=F2.SEAM_F3["look"], lens=F2.SEAM_F3["lens"], vel=F2.SEAM_F3["vel"])
SEAM_S1 = dict(pos=F(-1300.0, -1500.0, 1100.0), look=F(-4500.0, -6000.0, 600.0), lens=28.0, vel=(-150.0, -200.0, 40.0))
def _k(t, p, l, lens):
    return (t, F(*p), F(*l), lens)
# v8 (FEEDBACK_v13 §2): video clock with FROZEN tableaux (flat knots).  From the sky: her light flash (titan hidden by the
# canopy), ~2.4 s later Eren's flash elsewhere; dive in: FROZEN face-off (EP21 08:15); slide on: FROZEN high kick (EP21
# 19:19, cut trunk in mid-air, crystal at the foot tip, smoke from Eren's neck); FROZEN slumped Female in steam (EP22 07:15,
# Mikasa / Levi gone); then up into the sky toward Stohess (the cart / corpse retreat is skipped).
STORY_DUR = 56.0
TMAP = [(0.0, 0.0), (3.0, 3.0), (3.6, 17.4), (5.2, 19.0), (5.8, 20.3), (8.2, 20.3), (8.8, 30.75), (11.2, 30.75),
        (11.7, 47.5), (14.0, 47.5), (17.0, 56.0)]
DUR = TMAP[-1][0]
TAB = dict(faceoff=(5.8, 8.2), kick=(8.8, 11.2), slump=(11.7, 14.0))
TAB_STORY = dict(faceoff=20.3, kick=30.75, slump=47.5)
def story(t):
    return float(np.interp(t, [k[0] for k in TMAP], [k[1] for k in TMAP]))
def _shots(lift=False):
    from forest import tableau as TB
    fx, fy = fem_F(20.3); ex, ey = eren_F(20.3)
    kx, ky = fem_F(30.75); sx, sy = fem_F(47.5)
    front = math.degrees(2.3) + 90.0
    sh = [TB.Shot("faceoff", *TAB["faceoff"], F((fx + ex) / 2, (fy + ey) / 2, 8.0), az=(250, 278), dist=(58, 46), el=(9, 13), lens=32),
          TB.Shot("kick", *TAB["kick"], F(kx, ky, 9.0), az=(195, 228), dist=(52, 40), el=(5, 9), lens=34),
          TB.Shot("slump", *TAB["slump"], F(sx, sy, 4.0), az=(front + 25, front - 5), dist=(40, 31), el=(8, 12), lens=38)]
    if lift:
        for s_ in sh:
            x, y, z = s_.target; s_.target = (x, y, z + C.G(x, y))
    return sh
CAM_KEYS = [
    (0.0, SEAM_IN["pos"], SEAM_IN["look"], SEAM_IN["lens"]),
    _k(2.2, (-40.0, 1020.0, 230.0), (BEAM_F[0], BEAM_F[1], 60.0), 30.0),          # sunset over the canopy: her flash
    _k(3.8, (60.0, 1230.0, 250.0), (EREN_F[0], EREN_F[1], 20.0), 30.0),           # camera moving: Eren's flash elsewhere
    _k(5.1, (220.0, 1420.0, 120.0), (EREN_F[0], EREN_F[1], 15.0), 30.0),          # dive toward the swampy clearing
    _k(14.7, (RX - 60.0, RY + 60.0, 220.0), (RX - 400.0, RY - 260.0, 0.0), 30.0),     # rise, turn west
    (DUR, SEAM_S1["pos"], SEAM_S1["look"], SEAM_S1["lens"]),
]
def _cam(lift):
    from forest import tableau as TB
    keys = C.lift_keys(CAM_KEYS, skip=(len(CAM_KEYS) - 1,)) if lift else CAM_KEYS
    return TB.make_cam(keys + _shots(lift), v_in=SEAM_IN["vel"], v_out=SEAM_S1["vel"])
CAM = _cam(False)
CAM_LIMITS = dict(speed=1500.0, yaw=300.0, hmin=8.0, hmax=1200.0, pitch=(-15.0, 75.0), lens=(27.0, 46.0))
PLAN = [(0.0, "afternoon"), (2.0, "sunset"), (5.0, "afternoon"), (46.0, "afternoon"), (51.0, "golden"), (DUR, "sunset")]   # round 3: no murky dusk tail   # readable under the canopy
LIGHT = C.LightRig(*C.light_plan(PLAN))
TRACK = {}
S = {}

# ---------------------------------------------------------------- build
def build(site):
    global CAM
    CAM = _cam(True)                                                                              # z above ground -> absolute
    import flares, attack_titan as AT
    c = C.coll("F3")
    S["AT"] = AT
    S["fem"] = C.Female("F3_Female")
    S["eren"] = C.Eren("F3_Attack")
    P = C.Batch("F3_People", C.RIDER_MATS)
    S["fj"] = {}
    for nm in FLYERS:
        S["fj"][nm] = P.new(pivot=0.9)
        C.person_geo(P.g, S["fj"][nm], hair={"eren_h": "hair", "mikasa": "hair", "levi": "hair"}.get(nm, "blond" if nm == "petra" else "hair"))
    S["corpses"] = [P.new(pivot=0.9) for _ in range(3)]
    for j in S["corpses"]:
        C.person_geo(P.g, j)
    P.build(c); S["P"] = P
    S["wires"] = C.Wires("F3_Wires", 8, C.mat("F3_Wire", (0.08, 0.08, 0.09), 0.5), c, r=0.08)
    B = C.Batch("F3_Retreat", C.RIDER_MATS)
    S["ret"] = []
    for k in range(NRET):
        j = B.new(pivot=1.2)
        if k % 4 == 1:
            C.wagon_geo(B.g, j)
        else:
            C.rider_geo(B.g, j)
        S["ret"].append(j)
    B.build(c); S["B"] = B
    TT = C.Batch("F3_Abnormals", C.titan_mats())
    S["ab"] = [C.titan_add(TT, dict(H=14.0, skin=6, g=0.7, al=1.3)), C.titan_add(TT, dict(H=9.0, skin=4, hair=0))]
    TT.build(c); S["TT"] = TT
    fs = flares.FlareSet("F3_Flares", style="column")
    x, y, _ = ret_at(ret_head(BEATS["green"]) - 120)
    fs.add(BEATS["green"], _W(x, y, 3.0), "green", up=130, width=2.4, seed=7)
    fs.build(c); S["fs"] = fs
    # autopilot 10/28 (f2|f3 seam): f2's blue + green streaks are still hanging in the sky at f2's end -> the same flares,
    # launched at their f2 times minus f2's DUR, so they continue across the seam instead of vanishing
    import seg_f2 as _F2
    flares.COLORS.setdefault("blue", ((0.05, 0.16, 0.75), (0.35, 0.55, 1.0)))     # = seg_f2 (registered in its build)
    pf = flares.FlareSet("F3_PrevFlares")
    pf.add(_F2.BEATS["blue"] - _F2.STORY_DUR, _W(_F2.TX - 30, _F2.TY + 40, 34.0), "blue", up=140, width=2.0, seed=3)
    pf.add(_F2.BEATS["green"] - _F2.STORY_DUR, _W(_F2.TX + 25, _F2.TY + 60, 34.0), "green", up=140, width=2.0, seed=4)
    pf.build(c); S["pf"] = pf
    steam = flares.PuffField("F3_Steam", kind="steam", alpha=0.45)        # v2: lighter, smaller, shorter (QA)
    te, pos, vel = [], [], []
    ex, ey = eren_F(BEATS["headkick"])
    for k in range(60):                                           # the severed neck, then the bitten-open nape
        te.append(BEATS["headkick"] + 0.05 * k); pos.append(_W(ex + random.uniform(-2, 2), ey + random.uniform(-2, 2), 4 + random.uniform(0, 4)))
        vel.append((random.uniform(-1, 1), random.uniform(-1, 1), 5.0))
    for k in range(40):                                           # the Female's eyes / shoulders regenerating, the cut mouth
        tt = random.choice((9.0, 11.0, 44.8)) + random.uniform(0, 1.5)
        fx, fy = fem_F(tt)
        te.append(tt); pos.append(_W(fx, fy, random.uniform(6, 12))); vel.append((0, 0, 3.0))
    steam.add_many(te, pos, vel, r0=1.2, r1=4.5, life=2.0, rise=3.0)
    steam.build(c); S["steam"] = steam
    TRACK.update(EREN=lambda t: _W(*eren_F(story(t)), 17.0) if 19.6 <= story(t) < 22.0 else None)
    S["flash"] = []
    for nm, (x, y), t0 in (("F3_FlashFemale", BEAM_F, BEATS["beam"][0]), ("F3_FlashEren", EREN_F, BEATS["shift"][0])):
        ld = bpy.data.lights.new(nm, "POINT"); ld.color = (1.0, 0.85, 0.45); ld.shadow_soft_size = 20.0; ld.energy = 0.0
        lo = bpy.data.objects.new(nm, ld); c.objects.link(lo); lo.location = _W(x, y, 120.0)
        S["flash"].append((lo, t0))
    # v8 kick tableau props: the cut trunk floating in mid-air, crystal hardening at her foot tip
    import bmesh
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=1.6, radius2=1.4, depth=16.0)
    S["trunk"] = C.mesh_obj("F3_CutTrunk", bm, [bpy.data.materials.get("F_Bark") or C.mat("F3_Bark", (0.2, 0.11, 0.07), 0.9)], c)
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=1.3)
    S["crystal"] = C.mesh_obj("F3_FootCrystal", bm, [C.mat("F3_Crystal", (0.55, 0.85, 1.0), 0.05, emit=(0.4, 0.8, 1.0), strength=1.5)], c)
    S["crystal"].scale = (0.8, 0.8, 1.6)
    S["kick_props"] = [S["trunk"], S["crystal"]]
    # v8 slump tableau: steam wrapping her (EP22 07:15)
    sx, sy = fem_F(47.5)
    sl = flares.PuffField("F3_SlumpSteam", kind="steam", alpha=0.7)
    sl.add_many([46.0 + 0.04 * k for k in range(36)], [_W(sx + random.uniform(-7, 7), sy + random.uniform(-7, 7), random.uniform(1, 12)) for k in range(36)],
                [(0, 0, 2.0)] * 36, r0=2.0, r1=6.0, life=3.0, rise=2.0)
    sl.build(c); S["slump_steam"] = sl

def _fly_w(nm, t):
    x, y, z, vis, _ = flyer_F(nm, t)
    return _W(x, y, z) if vis else None

# ---------------------------------------------------------------- per frame
def _shift(AT, w, u, seed):
    """v2 (QA batch1 P1): smaller (x0.6), thinner (x0.45) steam dome that fades out and is GONE after the shift (the
    shared shift_fx keeps a 36 m dome at 0.22 forever = the white / blue "bubbles" and ground discs); bolts x3 thicker."""
    fx = AT.shift_fx(w[0], w[1], min(1.0, max(0.0, u)), seed=seed, scale=0.6)
    if not fx.get("_f3"):
        for o in fx["bolts"]:
            if o.type == "CURVE":
                o.data.bevel_depth *= 3.0
        fx["_f3"] = 1
    fx["dome_d"].default_value *= 0.45 * (1.0 - C.ss(0.55, 1.0, u))
    fx["dome"].hide_render = u >= 1.0 or fx["dome"].hide_render

def update(t):
    from forest import tableau as TB
    ts = story(t)
    _update(ts)
    k = next((n for n, (a, b) in TAB.items() if a - 0.25 <= t <= b + 0.25), None)
    fem, er = S["fem"], S["eren"]
    for o in S["kick_props"]:
        C.hide(o, k != "kick")
    # v8: the two transformations read from the sky as lightning flashes over the canopy (the titans stay hidden)
    for lo, t0 in S["flash"]:
        e = C.bump(ts, t0, t0 + 0.08, t0 + 0.25, t0 + 0.9)
        lo.data.energy = 4.0e8 * e; C.hide(lo, e <= 0.0)
    if k is None:
        return
    st = TAB_STORY[k]
    fem.show(True)
    pn = {"kick": "highkick"}.get(k, k)
    fem.pose(TB.POSE_F[pn])
    x, y = fem_F(st)
    w = _W(x, y, TB.FZ_T.get(pn, 0.0))
    yaw = fem_yaw(st)
    if k == "kick":                       # the kick goes up-right past the trunk toward Eren's (severed) head
        ex, ey = eren_F(st); yaw = C.yaw_of(ex - x, ey - y) + 0.5
    fem.place(w[0], w[1], w[2], yaw)
    fem.hardening(0.0)
    if k == "faceoff":
        er.pose(TB.eren_specs(er.G6, er.P)["faceoff"])
    bpy.context.view_layer.update()
    if k == "kick":
        tip = fem.bone_world("foot.L", tail=True)
        S["crystal"].location = tip
        S["trunk"].location = (tip.x + 6.0 * math.cos(yaw), tip.y + 6.0 * math.sin(yaw), tip.z - 2.0)
        S["trunk"].rotation_euler = (0.9, 0.35, yaw)
    if k == "slump":                      # Mikasa / Levi already gone
        P = S["P"]; P.vis[:] = 0.0; P.push(); S["wires"].update([], bpy.context.scene.camera.location)

def _update(t):
    SK = os.environ.get("F3_SKIP", "")        # autopilot debug bisect: comma list of fem, eren, flyers, ret, cards
    AT = S["AT"]
    cam = bpy.context.scene.camera
    # autopilot 10/28: grazing views across the canopy (descent 4.5 s, under-canopy shots) put thousands of giant trees in the
    # frustum -> GPU time > the Windows driver timeout -> Blender died (f3 v3/v4 = duplicated frames).  Far clip 900 m there.
    if "_clip0" not in S:
        S["_clip0"] = cam.data.clip_end
    cam.data.clip_end = (600.0 if t < 6.2 else 350.0) if 3.6 < t < 46.6 else S["_clip0"]   # 480p: tighter (f2 timed out at 900 m)
    C.forest_dim(C.ss(5.4, 6.2, t) * (1 - C.ss(45.8, 46.6, t)))
    # transformation FX: her beam, Eren's lightning
    bu = (t - BEATS["beam"][0]) / 2.0
    if bu > -0.01 and not os.environ.get("F3_NOSHIFT"):
        _shift(AT, F(*BEAM_F), bu, 21)
    eu = (t - BEATS["shift"][0]) / 2.0
    if eu > -0.01:
        _shift(AT, F(*EREN_F), eu, 33)
    # the Female
    fem = S["fem"]
    pose, dz, vis = fem_pose(t)
    vis = vis and "fem" not in SK
    fem.show(vis)
    if vis:
        fem.pose(pose)
        x, y = fem_F(t)
        w = _W(x, y, dz)
        fem.place(w[0], w[1], w[2], fem_yaw(t))
        hard = max(C.bump(t, 20.6, 21.2, 27.0, 28.0), C.ss(30.0, 30.4, t) * (1 - C.ss(31.0, 32.0, t)), C.ss(42.0, 43.0, t))
        fem.hardening(hard)
    # Eren's titan
    er = S["eren"]
    if t < BEATS["shift"][0] + 0.6 or "eren" in SK:
        er.show(False)
    else:
        er.show(True)
        spec, headless = eren_spec(t, er.P, er.G6)
        er.pose(spec)
        x, y = eren_F(t)
        fx, fy = fem_F(t)
        yaw = C.yaw_of(fx - x, fy - y) if t < BEATS["headkick"] + 0.2 else C.yaw_of(fx - x + 1e-6, fy - y)
        if t >= BEATS["headkick"]:
            yaw = getattr(er, "_ky", yaw); er._ky = yaw
        rise = C.ss(BEATS["shift"][0] + 0.6, BEATS["roar"][0], t)
        w = _W(x, y, -14.0 * (1 - rise))                          # rises out of the lightning / steam dome
        er.place(w[0], w[1], w[2], yaw)
        hb = er.T.arm.pose.bones.get("Head_9")
        if hb is not None:
            s = 0.02 if headless else 1.0
            hb.scale = (s, s, s)
        er.T.eyes(0.0 if headless else 20.0)
        er.T.steam(0.6 * C.ss(BEATS["headkick"], BEATS["headkick"] + 1.0, t) + 0.5 * (1 - rise) if t > BEATS["shift"][0] else 0.0)
    bpy.context.view_layer.update()
    # flyers
    P = S["P"]; segs = []
    head = fem.bone_world("head", tail=True) if vis else None
    for nm in (FLYERS if "flyers" not in SK else ()):
        j = S["fj"][nm]
        x, y, z, v, fly = flyer_F(nm, t)
        p = np.array(_W(x, y, z))
        if nm == "eren_h" and v and 33.6 <= t < 48.0 and head is not None:
            if t < BEATS["mouth"] + 0.4:
                yw = fem_yaw(t)
                p = np.array((head.x - 1.2 * math.sin(yw), head.y + 1.2 * math.cos(yw), head.z - 1.4))
            else:
                lx, ly, lz, _, _ = flyer_F("levi", t)
                p = np.array(_W(lx, ly, lz - 0.6))
        P.vis[j] = 1.0 if v else 0.0
        P.pos[j] = p
        C.person_pose(P, j, "fly" if fly else ("stand" if nm == "levi" else "fallen"))
        x2, y2, _, _, _ = flyer_F(nm, t + 0.05)
        if abs(x2 - x) + abs(y2 - y) > 1e-6:
            P.yaw[j] = C.yaw_of(x2 - x, y2 - y)
        if v and fly and nm != "eren_h" and len(segs) < 8:      # one hook wire up into the nearest trunk / her body
            a = p + np.array((0, 0, 1.0))
            hook = (np.array((head.x, head.y, head.z)) if (head is not None and nm in ("levi", "mikasa") and 38.0 < t < 45.0)
                    else a + np.array((8.0 * math.cos(t + j), 8.0 * math.sin(t + j), 22.0)))
            segs.append((tuple(a), tuple(hook)))
    # retreat: corpses dropped off the rear wagon
    rear = S["ret"][-3]
    for k, j in enumerate(S["corpses"]):
        td = BEATS["drop"][0] + 0.4 * k
        if True:                                                   # v8: the corpse drop is skipped
            P.vis[j] = 0.0; continue
        x, y, yaw = ret_at(ret_head(td) - (NRET - 3) * 9.0)
        P.vis[j] = 1.0; P.pos[j] = _W(x + 2 * k, y, 0.3); C.person_pose(P, j, "fallen")
    P.push()
    S["wires"].update(segs, cam.location)
    # the retreat column + abnormals
    B = S["B"]
    for k, j in enumerate(S["ret"] if "ret" not in SK else ()):
        on = False                                                 # v8: retreat column skipped
        s = ret_head(max(t, 47.0)) - k * 9.0
        x, y, yaw = ret_at(s)
        B.pos[j] = _W(x, y); B.yaw[j] = yaw; B.vis[j] = 1.0 if on else 0.0
        ph = 2 * math.pi * 2.3 * t + k
        B.Ar[j, 1] = 0.55 * math.sin(ph); B.Ar[j, 2] = -0.55 * math.sin(ph)
    B.push()
    TT = S["TT"]
    for i, j in enumerate(S["ab"]):
        tail = ret_at(ret_head(max(t, 47.0)) - NRET * 9.0 - 160 - 90 * i)
        TT.pos[j] = _W(tail[0] + 40 * (i - 0.5), tail[1]); TT.yaw[j] = tail[2]
        C.titan_walk(TT, j, t * 7.0 + i, 0.7, run=True)
        TT.vis[j] = 0.0
    TT.push()
    if "cards" not in SK:
        S["fs"].update(t, wind=(1.5, 0.5)); S["steam"].update(t, wind=(0.8, 0.3)); S["pf"].update(t, wind=(1.0, 0.5))
        S["slump_steam"].update(t, wind=(0.4, 0.2))

def light(t):
    LIGHT.apply(story(t))

def check():
    for t in (2.0, 8.0, 12.0, 20.0, 25.0, 30.6, 36.0, 44.6):
        fx, fy = fem_F(t); ex, ey = eren_F(t)
        print(f"[f3] t {t:4.1f} female F ({fx:5.0f} {fy:5.0f}) eren F ({ex:5.0f} {ey:5.0f}) d {math.hypot(fx - ex, fy - ey):5.1f}")

