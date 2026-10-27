"""g4 TROST 850 ESTABLISHING (SCENE_BIBLE_v2 g4, 20.0 s, frame M).  SEG=g4 bash render_seg.sh
Every frame is a pure function of the local time t (0..DUR).  All times live in BEATS (+ the key tables built from it).

  0-2.4   graduation night at the 104th camp (camp104.py, shared with g3): deep-blue moonlight, lit windows, braziers
  1-3     the Survey Corps column starts down the main avenue AV: 120 riders 2 abreast (people_kit scouts riding, green cape
          quads over the horses so the line reads green) + 3 hooded wagons at the rear, one continuous ~305 m line moving at
          one shared speed; ~600 civilians line AV Y 150-450 and raise their arms as it passes; the outer gate O is open
  3.4-7.2 time-lapse golden sunrise: low sun in the east (el 1.5 -> 11 deg, long shadows), pink -> orange horizon band in
          the mist, warm grade; chimney wisps from ~40 houses; light morning mist, crisp blue by 9.8
  6       the wall-top roster of g5 t 0 (7 cadets incl. Eren, 20 Garrison gunners, 30 vanguard on the GS roofs) takes post
  7.5-15  the column leaves through O and runs down the south road with a low dust trail; the camera (G2 -> G3 -> G3b) frames
          the avenue, the gate and the road (lens 34 -> 44); tail through the gate at 15.0
  15-17   the column speeds away (time-lapse) and dwindles 310-470 m out: all gone by 18.5; the gate closes 15.6-18.0
  16.4-19.75 Eren (EREN tag 16.8-19.7, hud2) on the wall top above O: raised-fist pose looking over the town, then turns
          to face south as g5 has him
  20.0    = g5 t 0: the bolt (g5 frame 0 is the yellow spike) and the Colossal's skull.
SEAM g4 -> g5: camera G5 = g5 C0 (camkeys, look-at at rest both sides); light = g5 LIGHT_KEYS[0] / GRADE_KEYS[0]; gate intact and
closed, slabs at rest, cart hidden here (g5 shows it in the arch, out of frame); the people and titans visible in g5's first
frame are g5's own objects: seg_g5.build_titans / build_people are run here and evaluated at g5 time tau = t - DUR (< 0) with
extra g4 segments (the roster's posts, Eren's pose) and the 12 field titans walking at their g5 t 0 velocity.
Reused: seg_g5 (titans, ODM people, contact shadows, Q2 well fix), camp104 (new), people_kit (scouts riding, horses),
swarm845 (civilian figures), smokecards (chimney wisps), trost.py set objects (OuterGate_Door / OuterGate_Iron poses).
"""
import math, os, random, re, sys, time
import numpy as np

try:
    import bpy, bmesh
    from mathutils import Vector, Matrix
except ImportError:                       # pure-python use (camera / corps checks outside Blender)
    bpy = None

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import camchan
import camkeys
import segtime

DUR = segtime.DUR["g4"]                    # 20.0

# ====================================================================== BEATS (local seconds) - ONE re-time table
BEATS = dict(
    # time of day: key times of LIGHT_KEYS / GRADE_KEYS / HAZE_KEYS below
    night=0.0, night2=2.4, predawn=3.4, sunrise=5.0, golden=7.2, early=9.8, morning=13.0, late=16.5, seam=DUR,
    lamps=(2.6, 4.0),             # camp lamps fade out (the camp has left the frame by then)
    lamp_tint=(0.0, 0.0),         # camp lamp tint ease (0 = none: camp104's final night defaults ARE the warm values; code path kept)
    gate_open=(0.6, 2.4),         # outer gate opens (camera 1.6 km away at the camp)
    corps_go=(1.0, 3.0),          # the column starts / reaches cruise speed
    corps_tail_out=15.0,          # the last wagon passes the gate (sets the column's start position)
    corps_away=(15.0, 17.0),      # the whole column speeds away down the south road (time-lapse) and dwindles out
    dust=(6.0, 17.0),             # dust trail emitted behind the units on the dirt road (cards die by 19.5)
    chimneys=(2.6, 12.5),         # chimney wisps are emitted (cards live <= 5 s: none left at the seam)
    roster=6.0,                   # g5's t 0 wall-top + vanguard roster takes post (camera > 1 km away)
    gate_close=(15.6, 18.0),      # door swings shut, iron leaf down (tail out at 15.0, see check())
    eren_fist=(16.4, 19.15),      # Eren's raised-fist pose on the rail (facing the town)
    eren_turn=(19.15, 19.75),     # he turns to face south (g5 t 0 stance)
    tag=(16.8, 19.7),             # EREN name tag (graphics_timelines/g4_tags.json)
    bolt=DUR)                     # = g5 t 0

# Survey Corps column (frame M).  Speeds are time-lapse speeds; s = arc length along CORPS_ROUTE.
# v1 = the column's cruise speed (all units together: a continuous 2-row line ~305 m long), v2 = after corps_away;
# units fade out between fade[0] and fade[1] metres past the gate.
CORPS = dict(rows=60, gap=4.6, half=1.1, wagons=3, wagon_gap=11.0, v1=40.0, v2=175.0, fade=(310.0, 470.0))
# AV -> ring road outside the avenue-mouth slab arc (r 77.5 about O, bearings 0..45) -> round the pit east of P1 -> through the
# gap sector of the C trenches -> the big strap door (X 3.5) -> O -> the main road (world road M (-60,-530), (-260,-1530))
CORPS_ROUTE = [(-60.0, 470.0), (-15.0, 300.0), (-3.0, 110.0), (0.0, 86.0)] + \
    [(77.5 * math.sin(math.radians(b)), 77.5 * math.cos(math.radians(b))) for b in (7.5, 15.0, 22.5, 30.0, 37.5, 45.0)] + \
    [(42.0, 36.0), (24.0, 22.0), (12.0, 19.0), (3.5, 16.0), (3.5, 0.0), (3.5, -12.0), (0.0, -60.0), (-25.0, -250.0),
     (-60.0, -530.0), (-160.0, -1030.0), (-260.0, -1530.0)]
GATE_Y_OUT = -12.0                # past this the rider is outside the wall

AV = [(0.0, 78.0), (-15.0, 300.0), (-60.0, 470.0), (-128.0, 735.0), (-153.0, 803.0)]
CROWD = dict(n=600, y=(150.0, 450.0), off=(5.4, 6.7), seed=404)
N_CHIMNEYS = 40
WIND = np.array([2.6, 1.2, 0.0])                 # = g5 drift

# ====================================================================== camera = bible g4 keys (camkeys.G4, G0b/G1 re-keyed for yaw)
CAM_KEYS = list(camkeys.G4)
CAM = camchan.CamPath(**camkeys.cam("g4"))
CAM_LIMITS = dict(speed=150.0, yaw=30.0, hmin=90.0, hmax=380.0, pitch=(17.0, 45.0), lens=(27.0, 50.0))

# ====================================================================== light / grade / haze keys (times from BEATS)
# t: sun elevation (deg), compass azimuth (deg), sun energy, sun rgb, zenith rgb, horizon rgb, world (lighting) strength
# (night: the "sun" is a weak blue moon from the WSW; the grade does the darkness, the toon pass bands the lighting)
def _g5_light0():
    try:
        import seg_g5 as S5
        return S5.LIGHT_KEYS[0][1:], S5.GRADE_KEYS[0][1:]
    except Exception:
        return ((47.0, 135, 3.6, (1.00, 0.96, 0.90), (0.10, 0.28, 0.75), (0.70, 0.80, 0.93), 1.00), ((1.0, 1.0, 1.0), 0.0))
_L5, _G5 = _g5_light0()
LIGHT_KEYS = [
    (BEATS["night"],   35.0, 245, 0.45, (0.50, 0.62, 1.00), (0.004, 0.008, 0.030), (0.020, 0.035, 0.090), 0.30),  # moon, deep blue
    (BEATS["night2"],  35.0, 245, 0.45, (0.50, 0.62, 1.00), (0.004, 0.008, 0.030), (0.020, 0.035, 0.090), 0.30),
    (BEATS["predawn"],  1.5,  76, 0.80, (1.00, 0.55, 0.40), (0.10, 0.12, 0.30), (0.85, 0.45, 0.38), 0.50),
    (BEATS["sunrise"],  5.0,  80, 2.60, (1.00, 0.62, 0.35), (0.22, 0.32, 0.60), (1.00, 0.62, 0.42), 0.80),   # golden sunrise, E
    (BEATS["golden"],  11.0,  88, 3.00, (1.00, 0.78, 0.55), (0.16, 0.32, 0.66), (0.95, 0.78, 0.62), 0.90),
    (BEATS["early"],   22.0, 100, 3.20, (0.98, 0.95, 0.94), (0.12, 0.30, 0.70), (0.72, 0.80, 0.92), 0.95),   # crisp blue (Corps)
    (BEATS["morning"], 34.0, 116, 3.40, (1.00, 0.96, 0.92), (0.10, 0.28, 0.74), (0.70, 0.80, 0.93), 1.00),
    (BEATS["late"],    46.0, 133, 3.58, (1.00, 0.96, 0.90), (0.10, 0.28, 0.75), (0.70, 0.80, 0.93), 1.00),
    (BEATS["seam"],) + tuple(_L5),                                                                            # = g5 t 0
]
GRADE_KEYS = [                    # t: (gain r, g, b), exposure offset (stops)
    (BEATS["night"],   (0.45, 0.60, 1.35), -0.9),        # blue night (autopilot 10/28: lifted from -1.8, g4 v5 opened near black)
    (BEATS["night2"],  (0.45, 0.60, 1.35), -0.9),
    (BEATS["predawn"], (0.90, 0.76, 0.95), -0.6),        # violet-pink first light
    (BEATS["sunrise"], (1.24, 0.96, 0.70), -0.30),       # golden sunrise
    (BEATS["golden"],  (1.14, 1.00, 0.84), -0.12),
    (BEATS["early"],   (1.00, 1.00, 1.02), -0.06),
    (BEATS["morning"], (0.99, 1.00, 1.01), -0.04),
    (BEATS["late"],    (1.00, 1.00, 1.00), 0.0),
    (BEATS["seam"],) + tuple(_G5),
]
# compositor mist (scene.eevee_haze): depth (m), amount, haze rgb; the seam value = scene.py defaults (g5 never changes them)
HAZE0 = (float(os.environ.get("EEVEE_MIST_DEPTH", "5000")), float(os.environ.get("EEVEE_MIST", "0.45")), (0.62, 0.70, 0.82))
HAZE_KEYS = [
    (BEATS["night"],   3000.0, 0.60, (0.03, 0.05, 0.14)),
    (BEATS["night2"],  3000.0, 0.60, (0.03, 0.05, 0.14)),
    (BEATS["predawn"], 2300.0, 0.78, (0.72, 0.46, 0.50)),      # pink band on the horizon
    (BEATS["sunrise"], 2000.0, 0.85, (1.00, 0.68, 0.48)),      # orange band
    (BEATS["golden"],  2200.0, 0.80, (0.94, 0.80, 0.68)),
    (BEATS["early"],   2600.0, 0.75, (0.79, 0.83, 0.87)),      # #c9d4dd morning haze
    (BEATS["morning"], 3600.0, 0.62, (0.72, 0.78, 0.86)),
    (BEATS["late"],    HAZE0[0], HAZE0[1], HAZE0[2]),
    (BEATS["seam"],    HAZE0[0], HAZE0[1], HAZE0[2]),
]

# ====================================================================== small pure helpers
def ss(a, b, x):
    u = min(1.0, max(0.0, (x - a) / (b - a))) if b != a else float(x >= b)
    return u * u * (3 - 2 * u)

def lerp(a, b, u):
    return a + (b - a) * u

def _keyed(K, t):
    if t <= K[0][0]:
        return K[0], K[0], 0.0
    for a, b in zip(K, K[1:]):
        if a[0] <= t < b[0]:
            return a, b, ss(a[0], b[0], t)
    return K[-1], K[-1], 0.0

def _mix(a, b, u):
    if isinstance(a, tuple):
        return tuple(lerp(p, q, u) for p, q in zip(a, b))
    return lerp(a, b, u)

def poly_len(P):
    P = np.asarray(P, float)
    return np.concatenate([[0.0], np.cumsum(np.hypot(*np.diff(P, axis=0).T))])

def _chaikin(P, n=2):
    P = np.asarray(P, float)
    for _ in range(n):
        Q = [P[0]]
        for a, b in zip(P[:-1], P[1:]):
            Q += [0.75 * a + 0.25 * b, 0.25 * a + 0.75 * b]
        Q.append(P[-1]); P = np.array(Q)
    return P

def _resample(P, step=1.0):
    P = np.asarray(P, float); S = poly_len(P)
    s = np.arange(0.0, S[-1], step)
    return np.column_stack([np.interp(s, S, P[:, 0]), np.interp(s, S, P[:, 1])]), s

# ====================================================================== the Survey Corps column (pure kinematics, frame M)
ROUTE_P, ROUTE_S = _resample(_chaikin(CORPS_ROUTE, 2), 0.5)
_TAN = np.gradient(ROUTE_P, axis=0); _TAN /= np.maximum(np.linalg.norm(_TAN, axis=1), 1e-9)[:, None]
S_OUT = float(ROUTE_S[np.argmax(ROUTE_P[:, 1] < GATE_Y_OUT)])          # arc length where the route leaves the wall

def route_at(s):
    s = np.clip(s, 0.0, ROUTE_S[-1])
    x = np.interp(s, ROUTE_S, ROUTE_P[:, 0]); y = np.interp(s, ROUTE_S, ROUTE_P[:, 1])
    tx = np.interp(s, ROUTE_S, _TAN[:, 0]); ty = np.interp(s, ROUTE_S, _TAN[:, 1])
    n = np.maximum(np.hypot(tx, ty), 1e-9)
    return x, y, tx / n, ty / n

def _speed(t):
    """Column speed (m/s, every unit): start ramp corps_go -> v1, then corps_away -> v2 (time-lapse)."""
    return CORPS["v1"] * ss(*BEATS["corps_go"], t) + (CORPS["v2"] - CORPS["v1"]) * ss(*BEATS["corps_away"], t)

def _corps_units():
    """Column units, head first: (kind, s offset behind the head, lateral offset).  Riders 2 abreast, wagons at the rear."""
    U = []
    for k in range(CORPS["rows"]):
        for side in (-1, 1):
            U.append(("rider", k * CORPS["gap"], side * CORPS["half"]))
    back = (CORPS["rows"] - 1) * CORPS["gap"]
    for w in range(CORPS["wagons"]):
        U.append(("wagon", back + (w + 1) * CORPS["wagon_gap"], 0.0))
    return U
UNITS = _corps_units()
_LC = max(u[1] for u in UNITS)

def _integrate():
    """D(t) = distance the column has moved (1/120 s grid); the tail starts where it reaches the gate at corps_tail_out."""
    dt = 1.0 / 120.0
    T = np.arange(0.0, DUR + 0.5, dt)
    D = np.concatenate([[0.0], np.cumsum([_speed(t + 0.5 * dt) * dt for t in T[:-1]])])
    tail0 = S_OUT - float(np.interp(BEATS["corps_tail_out"], T, D))
    s0 = tail0 + _LC - np.array([u[1] for u in UNITS])
    return T, s0[None, :] + D[:, None], tail0
_CT, _CS, TAIL0 = _integrate()

def corps_s(t):
    """Arc length of every unit at time t (linear in the 1/120 s table)."""
    t = min(max(t, 0.0), _CT[-1])
    i = min(len(_CT) - 2, int(t * 120.0)); u = t * 120.0 - i
    return _CS[i] * (1 - u) + _CS[i + 1] * u

def corps_state(t):
    """(x, y, yaw (rad, ccw from +Y), vis scale) per unit in M."""
    s = corps_s(t)
    x, y, tx, ty = route_at(s)
    lat = np.array([u[2] for u in UNITS])
    x = x + ty * lat; y = y - tx * lat                    # right-hand normal (ty, -tx)
    yaw = np.arctan2(-tx, ty)
    f0, f1 = CORPS["fade"]
    w = (s - S_OUT - f0) / (f1 - f0); w = np.clip(w, 0.0, 1.0); vis = 1.0 - w * w * (3 - 2 * w)
    return x, y, yaw, vis, s

def tail_out_time():
    """First time the last unit is outside the wall, and the time every unit is fully faded."""
    t_out = t_gone = None
    for t in np.arange(0.0, DUR + 0.01, 0.05):
        s = corps_s(t)
        if t_out is None and s.min() > S_OUT:
            t_out = round(float(t), 2)
        if t_gone is None and s.min() > S_OUT + CORPS["fade"][1]:
            t_gone = round(float(t), 2)
    return t_out, t_gone

# ====================================================================== Blender side
STATE = {}

def say(*a):
    print("[seg g4]", *a, flush=True)

def hexrgb(h):
    h = h.lstrip("#"); c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c)

def _coll(name):
    c = bpy.data.collections.get(name)
    return c if c else STATE["L"].new_coll(name)

def _hide(ob, h):
    if ob is not None and (ob.hide_render != h or ob.hide_viewport != h):
        ob.hide_render = ob.hide_viewport = h

def S3(x, y=None, z=0.0):
    if y is None:
        p = x; x, y, z = float(p[0]), float(p[1]), float(p[2]) if len(p) > 2 else 0.0
    return np.array([float(x), float(y) - segtime.SET_OFF_Y, float(z)])

def G(x, y):
    return STATE["site"]["ground_M"](float(x), float(y))

def _dark_mat(name):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True; N = m.node_tree.nodes
    for n in list(N):
        if n.type != "OUTPUT_MATERIAL":
            N.remove(n)
    em = N.new("ShaderNodeEmission"); em.inputs["Color"].default_value = (0.012, 0.010, 0.010, 1.0); em.inputs["Strength"].default_value = 1.0
    m.node_tree.links.new(em.outputs[0], next(n for n in N if n.type == "OUTPUT_MATERIAL").inputs["Surface"])
    m["toon"] = 1
    return m

# ---------------------------------------------------------------------- g5's titans + people, evaluated at tau = t - DUR
def _fist_pose():
    """odm pose 'fist' (Eren's 'I can do it'): right fist raised high, left hand on the hip.  Opt-in for this process only."""
    import odm
    if getattr(odm, "_g4_fist", False):
        return
    orig = odm._pose_arrays
    def _pose_arrays(pose, t, i, st):
        if pose == "fist":
            Ar = np.zeros(8); Ae = np.zeros(8)
            Ar[4] = 2.75; Ae[5] = 0.45                 # right arm up, slight elbow bend
            Ar[3] = 0.35; Ae[6] = 1.7                  # left hand on the hip
            Ar[7] = -0.12 - 0.04 * math.sin(t * 2.0)   # cloak stirring
            return Ar, Ae, 0.04
        return orig(pose, t, i, st)
    odm._pose_arrays = _pose_arrays
    odm._g4_fist = True

def _inject(SQ):
    """Extra g4 segments (negative g5 time) for g5's t 0 roster: wall-top cadets wc*/eren, gunners gun*, vanguard v*_*."""
    import odm
    tau_on = BEATS["roster"] - DUR
    yaw_n = odm.yaw_of(np.array([0.0, 1.0, 0.0])); yaw_s = odm.yaw_of(np.array([0.0, -1.0, 0.0]))
    n = 0
    for f in SQ.flyers:
        if not (f.name == "eren" or f.name.startswith(("wc", "gun")) or re.match(r"v\d+_\d+$", f.name)):
            continue
        st = f.state(0.0)
        if st["vis"] <= 0:
            continue
        p0 = np.array(st["pos"], float).copy()
        if f.name == "eren":
            a, b = BEATS["eren_fist"][0] - DUR, BEATS["eren_fist"][1] - DUR
            c, d = BEATS["eren_turn"][0] - DUR, BEATS["eren_turn"][1] - DUR
            f.stand(tau_on, a, p0, yaw_n, "stand")
            f.stand(a, b, p0, yaw_n, "fist")
            ye = float(st["yaw"])
            f.follow(c, d, lambda t, p0=p0: p0, yaw_fn=lambda t, c=c, d=d, ye=ye: yaw_n + (ye - yaw_n) * ss(c, d, t), pose="stand")
            f.stand(d, 0.0, p0, st["yaw"], "stand")
            STATE["eren_p0"] = p0; STATE["eren_yaw0"] = st["yaw"]
        else:
            f.stand(tau_on, 0.0, p0, st["yaw"], st["pose"])
        n += 1
    say(f"g5 roster posted from t {BEATS['roster']}: {n} flyers")

def build_g5_cast(site):
    """Run seg_g5's titan + people builders (their own RNG streams -> identical to g5's t 0) and adapt them to tau < 0."""
    import seg_g5 as S5
    import odm
    S5.STATE.update(site=site, TR=site["TR"], L=site["L"])
    coll = S5._coll("G5")
    bpy.context.view_layer.update()
    S5.fix_q2_dome(coll)                               # owner QA: no brown disc N of Q2 (visible in the overview)
    t0 = time.time()
    S5.build_titans(coll)
    S5.build_shadows(coll)
    _fist_pose()
    ob_build = odm.Squads.build
    def _build(self, coll=None, gas_dt=0.07):
        if self.name == "G5Squads":
            _inject(self)
        return ob_build(self, coll, gas_dt)
    odm.Squads.build = _build
    try:
        S5.build_people(coll)
    finally:
        odm.Squads.build = ob_build
    STATE["S5"] = S5
    _patch_titans(S5)
    say(f"g5 cast built {time.time() - t0:.1f}s")

def _patch_titans(S5):
    """TT.poses(tau < 0): the 12 field titans out* walk at their g5 t 0 velocity (extrapolated back); everyone else hidden."""
    import odm
    TT = S5.STATE["TT"]
    orig = TT.poses
    js = [j for j, sp in enumerate(TT.specs) if re.match(r"out\d+$", sp["name"])]
    import trost_action as TA
    dt = TA.DT
    v0 = {}
    for j in js:
        v0[j] = np.array([TT.TX[1, j] - TT.TX[0, j], TT.TY[1, j] - TT.TY[0, j]]) / dt
    STATE["field_titans"] = js
    def poses(t):
        if t >= 0.0:
            return orig(t)
        if TT._cache_t == t:
            return TT._cache
        R0 = orig(0.0)
        Ar, Ae, lean, vis, yaw, pos, pitch = [np.array(a, float).copy() for a in R0]
        vis[:] = 0.0
        H = TT.H
        for j in js:
            v = v0[j]; sp = float(np.linalg.norm(v))
            p = np.array([TT.TX[0, j], TT.TY[0, j]]) + v * t
            pos[j, 0], pos[j, 1] = p
            pos[j, 2] = TT.site.g((p[0], p[1]))
            vis[j] = 1.0
            yaw[j] = math.atan2(-v[0], v[1]) if sp > 1e-6 else yaw[j]
            td = TT.TD[0, j] + sp * t
            ph = 2 * np.pi * td / (0.55 * H[j] + 0.5)
            sw = math.sin(ph) * 0.42 * min(1.0, sp)
            Ar[j, 1] = sw; Ar[j, 2] = -sw; Ar[j, 3] = -0.7 * sw; Ar[j, 4] = 0.7 * sw
            Ae[j, 5] = Ae[j, 6] = 0.25 + 0.15 * min(1.0, sp)
            lean[j] = -0.06 - 0.06 * min(1.0, sp) + 0.03 * math.sin(t * 0.7 + j)
        R = (Ar, Ae, lean, vis, yaw, pos, pitch)
        TT._cache_t = t; TT._cache = R
        TT._rig = odm.deform(TT.RX, Ar, Ae, lean, vis, yaw, pos, pitch, None, np.zeros(len(vis))).reshape(len(vis), 4, 3)
        return R
    TT.poses = poses

# ---------------------------------------------------------------------- the Survey Corps (people_kit scouts riding, wagons)
def build_corps(coll):
    import people_kit as PK
    rnd = random.Random(1850)
    M2S = STATE["site"]["M2S"]
    x, y, yaw, vis, s = corps_state(0.0)
    insts = []
    coats = ["horse_bay", "horse_bay", "horse_chestnut", "horse_dark", "horse_grey"]
    looks = [(f"scout:{k % 6}", (0.0, 3.1)[k % 2], coats[k % len(coats)]) for k in range(10)]   # 10 prototypes, instanced
    for i, u in enumerate(UNITS):
        if u[0] == "rider":
            pre, ph, coat = looks[rnd.randrange(len(looks))]
            e = PK.person(pre, tuple(M2S((x[i], y[i], G(x[i], y[i])))), yaw=float(yaw[i]), pose="ride", phase=ph, coat=coat)
            insts.append([e])
        else:
            insts.append(_wagon(coll, i, PK, rnd))
    STATE["corps"] = insts
    build_capes(coll)
    build_dust(coll)
    say(f"corps: {sum(1 for u in UNITS if u[0] == 'rider')} riders + {CORPS['wagons']} wagons; route {ROUTE_S[-1]:.0f} m, "
        f"gate at s {S_OUT:.0f}; tail out / gone {tail_out_time()}")

def _wagon(coll, i, PK, rnd):
    """Hooded supply wagon (origin at the axle centre, +Y forward) + 2 horses (people_kit instances)."""
    L = STATE["L"]
    bm = bmesh.new()
    L.box(bm, (0, 0, 1.15), (2.0, 4.2, 0.6), mi=0)
    for yy in (-1.6, 1.4):
        for sx in (-1, 1):
            L.cyl(bm, (sx * 1.08, yy, 0.62), (sx * 1.18, yy, 0.62), 0.62, 0.62, seg=10, mi=1)
    n = 10
    ring0, ring1 = [], []
    for k in range(n + 1):
        a = math.pi * k / n
        ring0.append(bm.verts.new((1.05 * math.cos(a), -2.0, 1.45 + 1.05 * math.sin(a))))
        ring1.append(bm.verts.new((1.05 * math.cos(a), 2.0, 1.45 + 1.05 * math.sin(a))))
    for k in range(n):
        f = bm.faces.new((ring0[k], ring0[k + 1], ring1[k + 1], ring1[k])); f.material_index = 2
    L.box(bm, (0, 3.1, 1.0), (0.12, 2.6, 0.12), mi=1)
    mats = [L.mat("G4_WagonBody", hexrgb("#6a4a30"), 0.9), L.mat("G4_WagonWheel", hexrgb("#3a2a1e"), 0.9),
            L.mat("G4_WagonHood", hexrgb("#ddd2b8"), 0.95)]
    w = L.obj_from_bm(f"G4_Wagon{i}", bm, mats, coll)
    hs = [PK.horse_only((0.0, 0.0, -500.0), 0.0, coat=("horse_bay", "horse_dark")[k], phase=(0.0, 3.1)[k]) for k in range(2)]
    return [w] + hs

CAPE = dict(w=1.05, l=1.35, z=2.05, drop=0.55, col="#2f5f36")     # Wings-of-Freedom cape green, over the horse's back

def build_capes(coll):
    """One green cape quad per rider, draped back over the horse (the column must read GREEN from 300-600 m)."""
    L = STATE["L"]
    nr = sum(1 for u in UNITS if u[0] == "rider")
    me = bpy.data.meshes.new("G4_CorpsCapes")
    me.from_pydata(np.zeros((4 * nr, 3)).tolist(), [], [[4 * k, 4 * k + 1, 4 * k + 2, 4 * k + 3] for k in range(nr)])
    me.materials.append(L.mat("G4_CapeGreen", hexrgb(CAPE["col"]), 0.85)); me.update()
    ob = bpy.data.objects.new("G4_CorpsCapes", me); coll.objects.link(ob)
    STATE["capes"] = (ob, np.array([i for i, u in enumerate(UNITS) if u[0] == "rider"]))

def update_capes(x, y, yaw, vis):
    ob, idx = STATE["capes"]
    xs, ys, yw, vs = x[idx], y[idx], yaw[idx], vis[idx]
    fx, fy = -np.sin(yw), np.cos(yw); rx, ry = np.cos(yw), np.sin(yw)
    z0 = np.array([G(a, b) for a, b in zip(xs, ys)])
    w, l, h, dr = CAPE["w"] / 2, CAPE["l"], CAPE["z"], CAPE["drop"]
    V = np.zeros((len(idx), 4, 3))
    for q, (a, b, dz) in enumerate(((-w, 0.15, 0.0), (w, 0.15, 0.0), (w * 1.15, -l, -dr), (-w * 1.15, -l, -dr))):
        V[:, q, 0] = xs + (rx * a + fx * b) * vs
        V[:, q, 1] = ys + (ry * a + fy * b) * vs - segtime.SET_OFF_Y
        V[:, q, 2] = z0 + (h + dz) * vs
    V[vs < 0.01] = (0.0, 0.0, -800.0)
    ob.data.vertices.foreach_set("co", V.reshape(-1).astype(np.float32)); ob.data.update()

def build_dust(coll):
    """Low dust trail behind the column on the dirt road outside the gate (pure: cards precomputed from corps_state)."""
    import smokecards as SC
    rng = np.random.default_rng(1851)
    rows = []
    a, b = BEATS["dust"]
    for t in np.arange(a, b, 0.12):
        x, y, yaw, vis, s = corps_state(float(t))
        out = (s > S_OUT + 8.0) & (vis > 0.25)
        for i in np.where(out)[0][::3]:
            fx, fy = -math.sin(yaw[i]), math.cos(yaw[i])
            rows.append((t + rng.uniform(0, 0.12), x[i] - fx * 2.5 + rng.normal(0, 1.0), y[i] - fy * 2.5 + rng.normal(0, 1.0), vis[i]))
    if not rows:
        STATE["dust"] = None; return
    R = np.array(rows); n = len(R)
    life = np.minimum(rng.uniform(2.2, 3.2, n), 19.5 - R[:, 0])
    pos = np.column_stack([R[:, 1], R[:, 2] - segtime.SET_OFF_Y, [G(p, q) + 0.6 for p, q in R[:, 1:3]]])
    C = SC.SmokeCards("G4CorpsDust")
    C.add_many(R[:, 0], pos, np.column_stack([rng.normal(0, 0.6, n), rng.normal(0, 0.6, n), rng.uniform(0.1, 0.5, n)]),
               r0=1.8, r1=rng.uniform(6.0, 9.0, n), life=life, rise=0.35, kind="dust", alpha=0.55 * R[:, 3],
               color=(0.66, 0.57, 0.43), tau=0.8, fade_in=0.25)
    C.build(coll)
    STATE["dust"] = C
    say(f"corps dust: {n} cards")

def update_corps(t):
    M2S = STATE["site"]["M2S"]
    x, y, yaw, vis, s = corps_state(t)
    update_capes(x, y, yaw, vis)
    if STATE.get("dust") is not None:
        STATE["dust"].update(t, wind=(WIND[0], WIND[1]))
    for i, (u, objs) in enumerate(zip(UNITS, STATE["corps"])):
        on = vis[i] > 0.01
        if u[0] == "rider":
            e = objs[0]
            if not on:
                e.location = (0.0, 0.0, -800.0); continue
            e.location = Vector(tuple(M2S((x[i], y[i], G(x[i], y[i])))))
            e.rotation_euler = (0.0, 0.0, float(yaw[i])); e.scale = (float(vis[i]),) * 3
            continue
        w, h1, h2 = objs
        if not on:
            for o in objs:
                o.location = (0.0, 0.0, -800.0)
            continue
        c, sn = math.cos(yaw[i]), math.sin(yaw[i])
        fwd = np.array([-sn, c])
        w.location = Vector(tuple(M2S((x[i], y[i], G(x[i], y[i]) + 0.0))))
        w.rotation_euler = (0.0, 0.0, float(yaw[i])); w.scale = (float(vis[i]),) * 3
        for k, h in enumerate((h1, h2)):
            q = np.array([x[i], y[i]]) + fwd * 5.4 * vis[i] + np.array([c, sn]) * (0.75 if k else -0.75) * vis[i]
            h.location = Vector(tuple(M2S((q[0], q[1], G(q[0], q[1])))))
            h.rotation_euler = (0.0, 0.0, float(yaw[i])); h.scale = (float(vis[i]),) * 3

# ---------------------------------------------------------------------- civilians lining AV (swarm845 minimal figures)
SHIRTS = ["#b5553f", "#c49a4a", "#3f7f8a", "#4d6a9a", "#6b8a4e", "#c97a42", "#7d5a8e", "#b86a52", "#4f8a6e", "#a8483a",
          "#d1b35a", "#6a94b8", "#9a4a78", "#d8cfbb", "#86a04a"]
PANTS = ["#2b4162", "#5c3c2a", "#3f4a3c", "#6b4f3a", "#2e2e3a", "#7a3b32"]
SKINS = ["#d8a888", "#c49474", "#a87a5a"]
HAIRS = ["#1c1814", "#3a2a1e", "#6a4a2a", "#8a6a3a", "#5a3a28", "#8a8a84"]

def build_crowd(coll):
    import swarm845 as SW
    L = STATE["L"]; TR = STATE["site"]["TR"]
    rng = np.random.default_rng(CROWD["seed"]); rnd = random.Random(CROWD["seed"])
    P, S = _resample(AV, 0.5)
    _, s_av = None, S
    tan = np.gradient(P, axis=0); tan /= np.linalg.norm(tan, axis=1)[:, None]
    pts, face, sref = [], [], []
    tries = 0
    while len(pts) < CROWD["n"] and tries < 20000:
        tries += 1
        k = rng.integers(len(P))
        if not (CROWD["y"][0] <= P[k, 1] <= CROWD["y"][1]):
            continue
        side = rng.choice([-1.0, 1.0])
        off = rng.uniform(*CROWD["off"])
        nrm = np.array([tan[k, 1], -tan[k, 0]]) * side
        q = P[k] + nrm * off + tan[k] * rng.normal(0, 0.3)
        if not TR.walkable_m(float(q[0]), float(q[1])):
            continue
        if any(abs(q[0] - a[0]) < 0.55 and abs(q[1] - a[1]) < 0.55 for a in pts[-40:]):
            continue
        pts.append(q); face.append(math.atan2(nrm[0], -nrm[1])); sref.append(k)
    n = len(pts)
    g = SW.Geo(); fm = []
    hg = np.clip(rng.normal(1.66, 0.07, n), 1.45, 1.85); hg[rng.random(n) < 0.08] = rng.uniform(1.05, 1.3)
    ns, npa, nsk, nha = len(SHIRTS), len(PANTS), len(SKINS), len(HAIRS)
    for i in range(n):
        n0 = len(g.fc)
        SW.person_geo(g, i, hg[i], rnd.random() < 0.35, rnd)
        base = [rnd.randrange(ns), ns + rnd.randrange(npa), ns + npa + rnd.randrange(nsk), ns + npa + nsk + rnd.randrange(nha)]
        fm += [base[c] for c in g.fc[n0:]]
    mats = [L.mat(f"G4_shirt{i}", hexrgb(c), 0.85) for i, c in enumerate(SHIRTS)] + \
           [L.mat(f"G4_pants{i}", hexrgb(c), 0.9) for i, c in enumerate(PANTS)] + \
           [L.mat(f"G4_skin{i}", hexrgb(c), 0.6) for i, c in enumerate(SKINS)] + \
           [L.mat(f"G4_hair{i}", hexrgb(c), 0.7) for i, c in enumerate(HAIRS)]
    R = g.finish()
    ob = SW._mesh("G4_AVSpectators", R, g.f, fm, mats, coll)
    P2 = np.array(pts)
    # arc length of each spectator projected on the corps route (for "the column is passing me")
    d = (ROUTE_P[None, :, 0] - P2[:, None, 0]) ** 2 + (ROUTE_P[None, :, 1] - P2[:, None, 1]) ** 2
    s_on = ROUTE_S[np.argmin(d, axis=1)]
    z = np.array([G(p[0], p[1]) + 0.06 for p in P2])
    STATE["crowd"] = dict(R=R, ob=ob, P=P2, yaw=np.array(face), z=z, s_on=s_on, ph=rng.uniform(0, math.tau, n), n=n)
    say(f"AV spectators: {n}")

def update_crowd(t):
    import swarm845 as SW
    C = STATE["crowd"]; n = C["n"]
    s = corps_s(t)
    near = (C["s_on"] > s.min() - 12.0) & (C["s_on"] < s.max() + 25.0)
    w = np.where(near, 1.0, 0.0)
    Ar = np.zeros((n, 7)); Ae = np.zeros((n, 7)); lean = np.zeros(n)
    wave = np.sin(t * 7.0 + C["ph"])
    Ar[:, 4] = w * (2.5 + 0.35 * wave) + (1 - w) * 0.06 * np.sin(t * 1.3 + C["ph"])
    Ar[:, 3] = w * (0.4 + 1.6 * (C["ph"] > 3.0)) * (0.8 + 0.2 * wave)
    lean[:] = 0.03 * np.sin(t * 0.9 + C["ph"])
    pos = np.column_stack([C["P"][:, 0], C["P"][:, 1] - segtime.SET_OFF_Y, C["z"]])
    yaw = C["yaw"] + 0.25 * np.sin(t * 0.5 + C["ph"]) * (1 - w)
    co = SW._deform(C["R"], Ar, Ae, lean, np.ones(n), yaw, pos)
    ob = C["ob"]; ob.data.vertices.foreach_set("co", co.astype(np.float32).ravel()); ob.data.update()

# ---------------------------------------------------------------------- chimney wisps
def build_chimneys(coll):
    import smokecards as SC
    S5 = STATE["S5"]; TR = STATE["site"]["TR"]
    rng = np.random.default_rng(4040)
    sites = []
    tries = 0
    while len(sites) < N_CHIMNEYS and tries < 4000:
        tries += 1
        X = rng.uniform(-430, 430); Y = rng.uniform(60, 840)
        if not TR.in_district_m(X, Y, 20.0) or TR.on_road_m(X, Y, 3.0):
            continue
        z = S5.top_z(X, Y)
        if z < 9.0 or z > 26.0:
            continue
        if any(math.hypot(X - a, Y - b) < 60 for a, b, _ in sites):
            continue
        sites.append((X, Y, z))
    C = SC.SmokeCards("G4Chimneys")
    t0, t1 = BEATS["chimneys"]
    for X, Y, z in sites:
        ts = np.arange(t0 + rng.uniform(0, 0.6), t1, rng.uniform(0.28, 0.42)); m = len(ts)
        C.add_many(ts, S3(X, Y, z + 1.5)[None, :] + rng.normal(0, 0.4, (m, 3)),
                   np.column_stack([rng.normal(0.4, 0.3, m), rng.normal(0.2, 0.3, m), rng.uniform(1.2, 2.0, m)]),
                   r0=0.7, r1=rng.uniform(3.0, 4.8, m), life=rng.uniform(3.4, 4.6, m), rise=1.6, kind="smoke", alpha=0.32,
                   color=(0.80, 0.80, 0.79), tau=1.2)
    C.build(coll)
    STATE["chimneys"] = C
    say(f"chimney wisps: {len(sites)} houses, {C.count()} cards")

# ---------------------------------------------------------------------- g5's first embers (te < 0 in g5) -> same cards here
def build_embers(coll):
    """seg_g5.build_cards draws its Colossal embers first from default_rng(55) with te in [-2, 10): the ones born before g5 t 0
    are alive in g5's first frame around the gatehouse top.  Re-draw that block identically and keep te < 0 (shifted +DUR)."""
    import smokecards as SC
    rng = np.random.default_rng(55)
    n = 160
    te = rng.uniform(-2.0, 10.0, n)
    pos = S3(0, -8, 45)[None, :] + np.column_stack([rng.normal(0, 18, n), rng.normal(0, 10, n), rng.uniform(-5, 20, n)])
    vel = np.column_stack([rng.normal(1.5, 1.5, n), rng.normal(0.5, 1.5, n), rng.uniform(2.0, 5.0, n)])
    life = rng.uniform(3.0, 6.0, n)
    k = te < 0.0
    C = SC.SmokeCards("G4Embers")
    C.add_many(te[k] + DUR, pos[k], vel[k], r0=0.9, r1=0.6, life=life[k], rise=0.5, kind="glow", alpha=0.9,
               color=hexrgb("#ff9a3c"), fade_in=0.3)
    C.build(coll)
    STATE["embers"] = C
    say(f"g5 pre-bolt embers: {int(k.sum())} (born {DUR - 2.0:.1f}-{DUR:.1f})")

# ---------------------------------------------------------------------- the outer gate: door swing + iron leaf, dark passage
def build_gate(coll):
    L = STATE["L"]
    d = bpy.data.objects.get("OuterGate_Door"); ir = bpy.data.objects.get("OuterGate_Iron")
    dm = _dark_mat("G4_PassageDark")
    bm = bmesh.new()
    L.box(bm, tuple(S3(3.5, 15.12, 3.1)), (7.3, 0.06, 6.2))
    L.cyl(bm, tuple(S3(3.5, 15.09, 6.2)), tuple(S3(3.5, 15.15, 6.2)), 3.62, 3.62, seg=14)
    din = L.obj_from_bm("G4_DoorDark", bm, [dm], coll)
    bm = bmesh.new()
    L.box(bm, (0.0, 0.0, 10.5), (10.8, 0.06, 21.0))
    dout = L.obj_from_bm("G4_IronDark", bm, [dm], coll)
    dout.location = Vector(tuple(S3(0.0, -5.02, 0.0)))
    STATE["gate"] = dict(door=d, iron=ir, M0d=d.matrix_world.copy() if d else None, M0i=ir.matrix_world.copy() if ir else None,
                         din=din, dout=dout, hinge=Vector(tuple(S3(7.25, 15.35, 0.0))))
    say("gate objects:", d.name if d else None, ir.name if ir else None)

def gate_frac(t):
    return ss(*BEATS["gate_open"], t) * (1.0 - ss(*BEATS["gate_close"], t))

def update_gate(t):
    g = STATE["gate"]; f = gate_frac(t)
    if g["door"] is not None:
        h = g["hinge"]
        R = Matrix.Translation(h) @ Matrix.Rotation(math.radians(-100.0) * f, 4, "Z") @ Matrix.Translation(-h)
        g["door"].matrix_world = R @ g["M0d"] if f > 0 else g["M0d"]
    if g["iron"] is not None:
        g["iron"].matrix_world = Matrix.Translation((0.0, 0.0, 21.5 * f)) @ g["M0i"] if f > 0 else g["M0i"]
    _hide(g["din"], f < 0.02)
    _hide(g["dout"], f < 0.02)
    g["dout"].scale = (1.0, 1.0, max(f, 0.01))

# ---------------------------------------------------------------------- build / update (contract)
# camp lamps under the deep-blue night grade (gain 0.30/0.48/1.50, -1.8 EV): camp104's own colours / strengths clip to
# white-blue.  t 0 shows camp104's look exactly (= g3's last frame, which uses set_night unmodified); over BEATS["lamp_tint"] the
# g4-only runtime tint eases in (camp104.py untouched): pre-compensated orange, unclipped strengths.
LAMP_WARM = dict(win=((1.0, 0.30, 0.06), 11.0), fire=((1.0, 0.24, 0.03), 16.0), glow=((1.0, 0.28, 0.05), 5.0))
LAMP_CAMP = dict(win=11.0, fire=16.0, glow=5.0)          # camp104.set_night strengths at f = 1 (final camp104 = LAMP_WARM)

def _camp_lamp_capture(st):
    st["_orig_cols"] = {k: tuple(st[k].inputs["Color"].default_value)[:3] for k in LAMP_WARM if st.get(k) is not None}

def update_camp_lamps(t):
    import camp104
    st = STATE["camp"]
    f = 1.0 - ss(*BEATS["lamps"], t)
    camp104.set_night(st, f)
    w = ss(*BEATS["lamp_tint"], t)
    for k, (col, stren) in LAMP_WARM.items():
        n = st.get(k)
        if n is None or k not in st.get("_orig_cols", {}):
            continue
        c0 = st["_orig_cols"][k]
        n.inputs["Color"].default_value = (*(lerp(a, b, w) for a, b in zip(c0, col)), 1.0)
        n.inputs["Strength"].default_value = lerp(LAMP_CAMP[k], stren, w) * f

def build(site):
    t0 = time.time()
    STATE["site"] = site; STATE["L"] = site["L"]
    TR = site["TR"]
    coll = _coll("G4")
    try:
        TR.set_breach(False); TR.set_glow(0.0); TR.set_wagon(False)
    except Exception as ex:
        say("set hooks failed:", ex)
    build_g5_cast(site)
    import camp104
    tb = time.time()
    STATE["camp"] = camp104.build(site["L"], site["M2S"], site["ground_M"], _coll("G4Camp"))
    _camp_lamp_capture(STATE["camp"])
    for nm, fn in (("camp", None), ("corps", build_corps), ("crowd", build_crowd), ("chimneys", build_chimneys), ("embers", build_embers), ("gate", build_gate)):
        if fn is not None:
            fn(coll)
        say(f"  {nm} {time.time() - tb:.1f}s"); tb = time.time()
    _light_capture()
    say(f"build {time.time() - t0:.1f}s")

def finish():
    pass

def update(t):
    t = float(t)
    tau = t - DUR
    S5 = STATE["S5"]
    S5.STATE["TT"].update(tau)
    S5.update_shadows(tau)
    SQ = S5.STATE["SQ"]
    try:
        SQ.update(tau)
    except TypeError:
        SQ.update(tau + 1e-4)
    import camp104
    update_camp_lamps(t)
    update_corps(t)
    update_crowd(t)
    STATE["chimneys"].update(t, wind=(WIND[0], WIND[1]))
    STATE["embers"].update(t, wind=(WIND[0], WIND[1]))
    update_gate(t)

# ---------------------------------------------------------------------- light (sun, sky, exposure, haze)
def _light_capture():
    sc = bpy.context.scene
    suns = [o for o in bpy.data.objects if o.type == "LIGHT" and o.data.type == "SUN"]
    w = sc.world
    nodes = w.node_tree.nodes if (w and w.use_nodes) else []
    hz = bpy.data.node_groups.get("EeveeHaze")
    hk = hm = None
    if hz is not None:
        hk = next((n for n in hz.nodes if n.type == "MATH" and n.operation == "MULTIPLY"), None)
        hm = next((n for n in hz.nodes if n.type == "MIX"), None)
    STATE["light0"] = dict(suns=suns, exp0=sc.view_settings.exposure,
                           ramps=[n for n in nodes if n.type == "VALTORGB"], skies=[n for n in nodes if n.type == "TEX_SKY"],
                           bgs=[(n, n.inputs[1].default_value) for n in nodes if n.type == "BACKGROUND"], hk=hk, hm=hm,
                           mist=(w.mist_settings if w else None))
    say("light capture:", len(suns), "suns,", len(STATE["light0"]["ramps"]), "ramps,", len(STATE["light0"]["skies"]), "skies,",
        len(STATE["light0"]["bgs"]), "bgs, haze", hk is not None)

def light_values(t):
    """Pure: sun dir (M), energy, rgb, zenith, horizon, world strength, elevation, grade gain, exposure offset, haze."""
    a, b, u = _keyed(LIGHT_KEYS, t)
    def sdir(k):
        el, az = math.radians(k[1]), math.radians(k[2])
        return np.array([math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el)])
    d = sdir(a) * (1 - u) + sdir(b) * u; d /= np.linalg.norm(d)
    ga, gb, gu = _keyed(GRADE_KEYS, t)
    ha, hb, hu = _keyed(HAZE_KEYS, t)
    return dict(d=d, en=_mix(a[3], b[3], u), col=_mix(a[4], b[4], u), zen=_mix(a[5], b[5], u), hor=_mix(a[6], b[6], u),
                ws=_mix(a[7], b[7], u), el=_mix(a[1], b[1], u), gain=_mix(ga[1], gb[1], gu), gex=_mix(ga[2], gb[2], gu),
                mist_depth=_mix(ha[1], hb[1], hu), mist_k=_mix(ha[2], hb[2], hu), mist_rgb=_mix(ha[3], hb[3], hu))

def light(t):
    t = float(t)
    v = light_values(t)
    L0 = STATE["light0"]
    d = v["d"]
    for o in L0["suns"]:
        o.rotation_euler = Vector(tuple(-d)).to_track_quat("-Z", "Y").to_euler()
        o.data.energy = v["en"]; o.data.color = v["col"]
    for r in L0["ramps"]:
        el = r.color_ramp.elements
        el[0].color = (*v["hor"], 1); el[-1].color = (*v["zen"], 1)
    for s in L0["skies"]:
        try:
            s.sun_elevation = math.radians(v["el"]); s.sun_rotation = math.atan2(d[1], d[0])
        except Exception:
            pass
    for n, s0 in L0["bgs"]:
        n.inputs[1].default_value = s0 * v["ws"]
    vs = bpy.context.scene.view_settings
    vs.exposure = L0["exp0"] + v["gex"]
    try:
        vs.use_curve_mapping = True
        cm = vs.curve_mapping
        cm.white_level = tuple(1.0 / max(g, 1e-3) for g in v["gain"])
        cm.black_level = (0.0, 0.0, 0.0)
        cm.update()
    except Exception as ex_:
        if not STATE.get("grade_warned"):
            say("colour grade failed:", ex_); STATE["grade_warned"] = True
    if L0["hk"] is not None:
        L0["hk"].inputs[1].default_value = v["mist_k"]
    if L0["hm"] is not None:
        L0["hm"].inputs["B"].default_value = (*v["mist_rgb"], 1.0)
    if L0["mist"] is not None:
        L0["mist"].depth = v["mist_depth"]

# ====================================================================== HUD trackers (M) + self checks
def _eren(t):
    S5 = STATE.get("S5")
    if S5 is None:
        return None
    st = S5.STATE["SQ"].state("eren", t - DUR)
    if st["vis"] <= 0:
        return None
    p = st["pos"]
    return (float(p[0]), float(p[1]) + segtime.SET_OFF_Y, float(p[2]) + 2.0)

TRACK = {"Eren": _eren}

def check():
    """Seam checks against seg_g5 (camera, light, Eren, gate, corps) + corps timing."""
    import seg_g5 as S5
    a = CAM.eval(DUR); b = S5.CAM.eval(0.0)
    h = 1e-3
    va = (CAM.eval(DUR)[0] - CAM.eval(DUR - h)[0]) / h; vb = (S5.CAM.eval(h)[0] - S5.CAM.eval(0.0)[0]) / h
    la = (CAM.eval(DUR)[1] - CAM.eval(DUR - h)[1]) / h; lb = (S5.CAM.eval(h)[1] - S5.CAM.eval(0.0)[1]) / h
    say("CHECK seam cam pos %s / %s  look %s / %s  lens %.2f / %.2f" % (np.round(a[0], 3), np.round(b[0], 3), np.round(a[1], 3),
        np.round(b[1], 3), a[2], b[2]))
    say("CHECK seam cam vel %s / %s  look vel %s / %s" % (np.round(va, 2), np.round(vb, 2), np.round(la, 2), np.round(lb, 2)))
    lv = light_values(DUR)
    say("CHECK light at 20.0 = g5 LIGHT_KEYS[0]:", LIGHT_KEYS[-1][1:] == tuple(S5.LIGHT_KEYS[0][1:]),
        "GRADE:", GRADE_KEYS[-1][1:] == tuple(S5.GRADE_KEYS[0][1:]), "haze:", (lv["mist_depth"], lv["mist_k"], lv["mist_rgb"]) == HAZE0)
    say("CHECK corps tail out / all gone (s):", tail_out_time(), " gate closes", BEATS["gate_close"], " gate frac at 20:",
        round(gate_frac(DUR), 4))
    x, y, yaw, vis, s = corps_state(DUR - 1.0 / 15.0)
    say("CHECK corps visible units on the last frame:", int((vis > 0.01).sum()))
    if "eren_p0" in STATE:
        p5 = S5.STATE["SQ"].state("eren", 0.0); p4 = S5.STATE["SQ"].state("eren", -1.0 / 15.0)
        say("CHECK Eren g4 last frame", np.round(p4["pos"], 2), p4["pose"], round(p4["yaw"], 2), " g5 t0", np.round(p5["pos"], 2),
            p5["pose"], round(p5["yaw"], 2))

if __name__ == "__main__":
    camchan.check(CAM, 0.0, DUR, limits=dict(name="g4 CAM", **CAM_LIMITS))
    print("route length %.0f m, gate at s %.0f, column length %.0f m" % (ROUTE_S[-1], S_OUT, _LC))
    print("tail out / all gone:", tail_out_time())
    for t in (0.0, 3.0, 6.0, 8.0, 10.8, 13.0, 16.0, 19.9):
        x, y, yaw, vis, s = corps_state(t)
        print("t %5.1f head (%.0f, %.0f) tail (%.0f, %.0f) visible %d" % (t, x[0], y[0], x[-1], y[-1], (vis > 0.01).sum()))
