"""s1 TO STOHESS -> THE STAIRWAY -> ANNIE SHIFTS -> PLAN C -> RAMPAGE (Stohess bible s1a-s1d, 30 s, stohess set, frame W;
layout in frame S, research/stohess/STOHESS_SCENE_BIBLE.md).   SEG=s1 bash aot/forest/render_part2.sh

  0-9    from the retreat's sky end (f3) a month passes (dusk, night, dawn) while the camera flies SW over Wall Rose to Wall
         Sina; Stohess in morning light
  9-14   the decoy carriage with its MP escort rolls down the main avenue; Eren, Armin, Mikasa walk Annie to the underground
         stairway
  14-20  Annie stops at the top of the stairs and refuses; she bites her ring: the light beam in the street, the Female rises
         out of the steam, houses burst
  20-24  Plan C: harpoons from the rooftop racks pin her; she tears free
  24-30  she rampages east down the avenue, civilians flee
"""
import math, os, sys, random
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from forest import common as C
from stohess import layout as SL
from stohess.layout import S
import camchan
import seg_f3 as F3
try:
    import bpy
except ImportError:
    bpy = None

DUR = 30.0
BEATS = dict(flight=(0.0, 9.0), carriage=(9.0, 14.0), walk=(9.0, 13.2), refuse=(13.2, 16.0), ring=16.0, beam=(16.0, 18.6),
             rise=(16.6, 18.2), planc=(21.0, 23.6), free=23.6, rampage=(24.0, 30.0))

def _W(sx, sy, dz=0.0):
    w = S(sx, sy)
    return (w[0], w[1], C.G(w[0], w[1]) + dz)

# ---------------------------------------------------------------- the Female (frame S)
FPATH = [(0.0, -150.0, 60.0), (18.2, -150.0, 60.0), (20.4, -95.0, 34.0), (21.0, -90.0, 32.0), (23.6, -90.0, 32.0),
         (26.5, -20.0, 18.0), (30.0, 60.0, 10.0), (33.0, 75.0, -60.0)]
def fem_S(t):
    x, y, _ = C.path_at(FPATH, t)
    return x, y
def fem_yaw(t):
    if t < 20.0:
        return C.yaw_of(1.0, -0.4)
    if t < 23.8:
        return C.yaw_of(1.0, -0.3)
    x2, y2 = fem_S(t + 0.05); x1, y1 = fem_S(t - 0.05)
    return C.yaw_of(x2 - x1, y2 - y1)
SWATS = (25.2, 26.6, 28.0, 29.3)
def fem_pose(t):
    if t < BEATS["rise"][0]:
        return None, 0.0
    if t < 20.0:                                               # rises out of the steam, roars
        u = C.ss(*BEATS["rise"], t)
        return C.fpose_blend(C.FPOSE["crouch"], C.FPOSE["scream"], C.ss(18.0, 18.8, t) * (1 - C.ss(19.4, 20.0, t))), -14.0 * (1 - u) + C.FZ["crouch"] * (1 - C.ss(18.0, 18.8, t))
    run = C.fem_run(2 * math.pi * 2.5 * t, lean=26.0)
    if t < BEATS["planc"][0]:
        return run, 0.0
    if t < BEATS["free"] + 0.4:                                # pinned by the harpoons, straining, hands to the nape
        P = C.fpose_blend(C.FPOSE["guard"], C.FPOSE["nape"], C.ss(21.0, 21.6, t))
        return {k: (v[0] + 3 * math.sin(t * 8 + len(k)), v[1], v[2]) for k, v in P.items()}, 0.0
    P = run
    for ts in SWATS:
        P = C.fpose_blend(P, C.FPOSE["swat"], C.bump(t, ts - 0.3, ts - 0.05, ts + 0.15, ts + 0.45))
    return P, 0.0

# the walkers (frame S): Annie, Armin, Mikasa, Eren from the avenue to the stairs
WALK = {"annie": (0.0, 0.0), "armin": (-2.0, -1.5), "mikasa": (1.8, -2.0), "eren_h": (0.0, -3.2)}
def walker_S(nm, t):
    u = C.ss(*BEATS["walk"], t)
    x0, y0 = -215.0, 14.0; x1, y1 = SL.STAIRS[0], SL.STAIRS[1] - 9.0
    dx, dy = WALK[nm]
    x, y = x0 + (x1 - x0) * u + dx, y0 + (y1 - y0) * u + dy
    if nm == "eren_h" and t > BEATS["ring"]:                    # Eren goes down the stairs (stuck underground)
        return x, y + 9.0, False
    if nm == "annie" and t > BEATS["ring"]:
        return x, y, False
    if nm in ("armin", "mikasa") and t > BEATS["ring"]:        # thrown back by the blast, then ODM up onto the roofs
        k = 1 if nm == "armin" else -1
        v = C.ss(16.1, 17.0, t)
        return x - 18 * v, y + k * 14 * v, True
    return x, y, True

def carriage_S(k, t):
    """decoy carriage (k = 0) and its MP escort (k 1..6) rolling east down the avenue."""
    x = -340.0 + 12.0 * max(0.0, t - 8.0) - 9.0 * k
    return x, (3.0 if k % 2 else -3.0) if k else 0.0

# ---------------------------------------------------------------- camera (frame S, z above ground; lifted in build)
SEAM_IN = F3.SEAM_S1
SEAM_S2 = dict(pos=S(110.0, 190.0, 200.0), look=S(60.0, 10.0, 10.0), lens=30.0, vel=(12.0, -4.0, 0.0))
def _k(t, p, l, lens):
    return (t, S(*p), S(*l), lens)
CAM_KEYS = [                                                   # approach from the NE, then work from the north side
    (0.0, SEAM_IN["pos"], SEAM_IN["look"], SEAM_IN["lens"]),
    (3.2, (16500.0, 29000.0, 1800.0), (13000.0, 24500.0, 0.0), 28.0),       # SW over Wall Rose, dusk -> night
    (6.2, (14100.0, 26000.0, 1200.0), (12650.0, 24050.0, 0.0), 28.0),       # dawn: Wall Sina ahead
    _k(9.0, (-40.0, 420.0, 380.0), (-140.0, 30.0, 0.0), 30.0),             # Stohess, morning: the avenue from the north
    _k(11.6, (-150.0, 150.0, 160.0), (-175.0, 30.0, 0.0), 34.0),           # the carriage, the four walking
    _k(14.2, (-140.0, 98.0, 50.0), (SL.STAIRS[0], SL.STAIRS[1] - 4, 2.0), 42.0),   # push-in: Annie at the stairs
    _k(18.0, (-118.0, 150.0, 85.0), (-148.0, 58.0, 12.0), 34.0),           # pull back: the beam, she rises (v3: ~100 m, was 230)
    _k(21.6, (-72.0, 100.0, 58.0), (-90.0, 32.0, 10.0), 40.0),             # Plan C from the roofs (v3: ~85 m, was 160)
    _k(26.0, (-28.0, 85.0, 62.0), (-20.0, 18.0, 9.0), 38.0),               # the rampage down the avenue (v3: ~85 m on her)
    (DUR, SEAM_S2["pos"], SEAM_S2["look"], SEAM_S2["lens"]),
]
CAM = camchan.CamPath(CAM_KEYS, v_in=SEAM_IN["vel"], v_out=SEAM_S2["vel"])
CAM_LIMITS = dict(speed=1500.0, yaw=90.0, hmin=30.0, hmax=2000.0, pitch=(5.0, 70.0), lens=(27.0, 43.0))
LIFT_SKIP = (0, 1, 2)                                          # seam with f3 + the high flight keys stay absolute
PLAN = [(0.0, "dusk"), (2.2, "night"), (4.0, "night"), (6.0, "dawn"), (8.6, "morning"), (DUR, "morning")]
LIGHT = C.LightRig(*C.light_plan(PLAN))
TRACK = {}
S_ = {}

def build(site):
    global CAM
    CAM = camchan.CamPath(C.lift_keys(CAM_KEYS, skip=LIFT_SKIP), v_in=SEAM_IN["vel"], v_out=SEAM_S2["vel"])
    import flares
    from forest import fset
    from stohess import sset
    c = C.coll("S1")
    S_["fem"] = C.Female("S1_Female")
    P = C.Batch("S1_People", C.RIDER_MATS)
    S_["w"] = {nm: P.new(pivot=0.9) for nm in WALK}
    for nm, j in S_["w"].items():
        C.person_geo(P.g, j, cloak=False, odm=False, hair="blond" if nm in ("annie", "armin") else "hair")
    rnd = random.Random(1849)
    S_["civ"] = []
    for k in range(140):                                       # civilians in the streets (fleeing from t 16.4)
        j = P.new(pivot=0.9); C.person_geo(P.g, j, cloak=False, odm=False)
        while True:
            x, y = rnd.uniform(-330, 120), rnd.uniform(-60, 120)
            if SL.street(x, y) and SL.in_town(x, y):
                break
        S_["civ"].append((j, x, y, rnd.uniform(0, math.tau), rnd.uniform(5.0, 8.0)))
    S_["roof"] = []
    for k, (rx, ry, rz) in enumerate(sset.STATE.get("racks", [])):    # Survey Corps on the roofs by the racks
        j = P.new(pivot=0.9); C.person_geo(P.g, j)
        S_["roof"].append((j, (rx + 2, ry + 2, rz)))
    P.build(c); S_["P"] = P
    B = C.Batch("S1_Carriage", C.RIDER_MATS)
    S_["car"] = [B.new(pivot=1.2) for _ in range(7)]
    C.wagon_geo(B.g, S_["car"][0])
    for j in S_["car"][1:]:
        C.rider_geo(B.g, j, cloak=False)
    B.build(c); S_["B"] = B
    S_["wires"] = C.Wires("S1_Harpoons", 24, C.mat("F2_Wire", (0.10, 0.10, 0.11), 0.4), c, r=0.10)
    racks = sset.STATE.get("racks") or [_W(-95 + 40 * math.cos(a), 30 + 40 * math.sin(a), 16) for a in np.linspace(0, math.tau, 10, endpoint=False)]
    rnd = random.Random(7)
    S_["harp"] = [dict(rack=np.array(racks[k % len(racks)]), h=rnd.uniform(4, 12), ang=rnd.uniform(0, math.tau),
                       t0=BEATS["planc"][0] + 0.5 * (k // 12) + rnd.uniform(0, 0.1)) for k in range(24)]
    # houses that burst at the shift and along the rampage (real copies of the town variants, in the cleared path strip)
    v = sset.STATE.get("variants") or fset.house_variants(fset.scene_mats(), c, 6, seed=41)
    S_["smash"] = []
    spots = [(-150.0 + 15, 60.0 + 14, 17.0), (-150.0 - 14, 60.0 - 12, 17.1)]
    for ts in SWATS:
        x, y = fem_S(ts); yw = fem_yaw(ts)
        side = 12.0 * (1 if len(spots) % 2 else -1)
        spots.append((x + side * math.cos(yw), y + side * math.sin(yw), ts))
    for k, (x, y, ts) in enumerate(spots):
        ob = v[k % len(v)][0].copy(); c.objects.link(ob)
        ob.location = _W(x, y, -0.3); ob.rotation_euler = (0, 0, fem_yaw(ts)); ob.scale = (1, 1, v[k % len(v)][0].scale[2])
        S_["smash"].append((ob, ts, ob.scale[2]))
    dust = flares.PuffField("S1_Dust", kind="dust", color=(0.62, 0.58, 0.52), alpha=0.6)
    te, pos, vel = [], [], []
    for ob, ts, _ in S_["smash"]:
        for k in range(12):
            te.append(ts + 0.04 * k); pos.append(tuple(np.array(ob.location) + np.array((rnd.uniform(-7, 7), rnd.uniform(-7, 7), 2 + k))))
            vel.append((rnd.uniform(-3, 3), rnd.uniform(-3, 3), 3.0))
    for tt in np.arange(24.0, 30.0, 0.18):
        x, y = fem_S(float(tt)); te.append(float(tt)); pos.append(_W(x, y, 1.0)); vel.append((0, 0, 1.5))
    dust.add_many(te, pos, vel, r0=3.0, r1=10.0, life=2.6, rise=1.5, alpha=0.55)
    dust.build(c); S_["dust"] = dust
    TRACK.update(ANNIE=lambda t: _W(*walker_S("annie", t)[:2], 2.2) if 9.5 <= t < 15.8 else None,
                 ARMIN=lambda t: _W(*walker_S("armin", t)[:2], 2.2) if 10.5 <= t < 14.0 else None,
                 MIKASA=lambda t: _W(*walker_S("mikasa", t)[:2], 2.2) if 10.5 <= t < 14.0 else None)

def update(t):
    import attack_titan as AT
    cam = bpy.context.scene.camera
    bu = (t - BEATS["beam"][0]) / 2.6
    if bu > -0.01:
        w = S(*SL.STAIRS); AT.shift_fx(w[0], w[1], min(1.0, max(0.0, bu)), seed=41)
    fem = S_["fem"]
    pose, dz = fem_pose(t)
    fem.show(pose is not None)
    if pose is not None:
        fem.pose(pose)
        x, y = fem_S(t); w = _W(x, y, dz)
        fem.place(w[0], w[1], w[2], fem_yaw(t))
        fem.hardening(C.ss(21.2, 21.8, t) * (1 - C.ss(23.4, 24.2, t)))
    P, B = S_["P"], S_["B"]
    for nm, j in S_["w"].items():
        x, y, vis = walker_S(nm, t)
        P.vis[j] = 1.0 if vis else 0.0; P.pos[j] = _W(x, y)
        moving = BEATS["walk"][0] < t < BEATS["walk"][1]
        C.person_pose(P, j, "fly" if (nm in ("armin", "mikasa") and t > 16.1) else ("run" if moving else "stand"), t * 0.5)
        P.yaw[j] = C.yaw_of(1.0, 0.7)
    fx, fy = fem_S(t)
    for j, x, y, yw, sp in S_["civ"]:
        if t < 16.4:
            px, py = x + 0.6 * math.sin(t * 0.3 + j), y
            C.person_pose(P, j, "stand"); P.yaw[j] = yw
        else:                                                  # flee from the shift point / her, straight away
            ax, ay = x - SL.STAIRS[0], y - SL.STAIRS[1]; d = math.hypot(ax, ay) + 1e-6
            run = sp * (t - 16.4)
            px, py = x + ax / d * run, y + ay / d * run * 0.4
            P.yaw[j] = C.yaw_of(ax, ay * 0.4); C.person_pose(P, j, "run", t + j)
            if math.hypot(px - fx, py - fy) < 8.0:
                P.vis[j] = 0.0
        P.pos[j] = _W(px, py)
    for j, p in S_["roof"]:
        P.pos[j] = p; P.yaw[j] = C.yaw_of(SL.STAIRS[0] - SL.toS(p[0], p[1])[0], SL.STAIRS[1] - SL.toS(p[0], p[1])[1])
        C.person_pose(P, j, "stand"); P.vis[j] = 1.0 if t > 19.0 else 0.0
    P.push()
    for k, j in enumerate(S_["car"]):
        x, y = carriage_S(k, t)
        B.pos[j] = _W(x, y); B.yaw[j] = C.yaw_of(1.0, 0.0); B.vis[j] = 1.0 if t < 17.0 else 0.0
        ph = 2 * math.pi * 1.6 * t + k
        B.Ar[j, 1] = 0.35 * math.sin(ph); B.Ar[j, 2] = -0.35 * math.sin(ph)
    B.push()
    segs = []
    if pose is not None and t < BEATS["free"]:
        base = np.array(_W(fx, fy))
        for h in S_["harp"]:
            if t < h["t0"]:
                continue
            u = C.ss(h["t0"], h["t0"] + 0.18, t)
            tgt = base + np.array((2.2 * math.cos(h["ang"]), 2.2 * math.sin(h["ang"]), h["h"]))
            segs.append((tuple(h["rack"]), tuple(h["rack"] + (tgt - h["rack"]) * u)))
    S_["wires"].update(segs, cam.location)
    for ob, ts, sz in S_["smash"]:
        u = C.ss(ts, ts + 0.5, t)
        ob.scale = (1.0 + 0.2 * u, 1.0 + 0.2 * u, max(0.12, sz * (1.0 - 0.85 * u)))
    S_["dust"].update(t, wind=(1.5, 0.5))

def light(t):
    LIGHT.apply(t)

def check():
    for t in (9.0, 13.0, 16.0, 18.2, 21.0, 24.0, 30.0):
        print(f"[s1] t {t:4.1f} female S {tuple(round(v) for v in fem_S(t))} annie S {tuple(round(v) for v in walker_S('annie', t)[:2])}")

# v2 (QA batch1 P1): the month-passing flight over the dark plain (story 0-9) at 4x (~2.6 video s instead of 8) and the
# Plan C / rampage tail at 1.8x; slope 1 at both seams.  Video ~19.4 s
import segtime as _ST
C.install_warp(globals(), _ST.slope_knots(30.0, [(0.0, 1.0, 0.0), (0.3, 4.0, 0.6), (8.0, 1.0, 0.6), (21.5, 1.8, 0.4), (29.2, 1.0, 0.4)]))
