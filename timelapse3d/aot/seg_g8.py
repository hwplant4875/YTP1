"""g8 BOULDER, SEAL, LEVI, MOP-UP, PYRES (SCENE_BIBLE_v2 g8, TIGHT 75.0 s, frame M) -- the owner's TOP-EFFORT beat.
Driven by aot/render_seg.py (SEG=g8 bash render_seg.sh).  Every frame is a pure function of the local time t (0..DUR).

Contents (bible g8 choreography, tight column; every time lives in BEATS / ROUTE_T / LIGHT_KEYS / CAM_KEYS below):
  0-4 hand-off, decoy mass at D, GREEN 3.0 (Rico, GF) - transformation 4.5 on the roof beside the ball - berserk: roof smash
  6.0 (Mikasa's roof caves in), miss 7.0, RED 8.0 (Rico, RF, white shock ring, lingers), self-punch 9.5, staggers and sits
  against the ball on its lawn bed 10-11 - squads on the ridges, 7 m and 12 m titans killed, Armin on the nape 12.0, stab 13.5 -
  wakes 15, stands, turns, squats, lifts overhead 15-19 - CARRY 19-47 along route BR (radial street, the 38 m wall-foot strip,
  the gate square, R5b squeeze past the east pilaster) with escort kills, the trench fall, Mitabi's and Ian's deaths (small),
  Mikasa's kill of the crouching titan - PLUG: roar 47, drop 47.5-48.5, crouch-shove 48.5-49.3, JAM 49.5 (dust burst,
  breach glow out), slump 50-52, Λ plug 50-54, 5 titans face it - YELLOW 53.0 (Rico, YF) + PY relay - Levi 55.5-57.5 at dusk -
  mop-up time-lapse 60-66 (night cannon pulses, Survey Corps day, 2 captured titans) - cleanup 66-71 (covered rows, pyres
  light one by one) - golden end hold 71-75 at rest at E2.
Reused: attack_titan (asset + poses via _apply_pose), trost_action.Titans (pure titans), odm.Squads (ODM people, wires,
gas), flares.FlareSet (thin trails), smokecards (steam / dust / smoke / fire cards), people_kit (static crowds), toon.
Placeholders built here when the set lacks them are named G8PH_* (listed by PLACEHOLDERS after build()).
"""
import math, os, random, sys, time
import numpy as np

try:
    import bpy, bmesh
    from mathutils import Vector, Matrix, Quaternion, noise
except ImportError:                       # pure-python use (camera / route checks outside Blender)
    bpy = None

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import camchan
import segtime

DUR = segtime.DUR["g8"]                    # 75.0 (tight)

# ====================================================================== BEATS + WARP (the ONE re-time place)
# BEATS are on the CHOREOGRAPHY clock.  WARP maps the segment's video time t (0..75) to that clock, piecewise linear, so a
# re-time is an edit of WARP alone: owner 10/27 "faster carry" = video 19-38 plays choreography 19-47 (x1.47, ~23.5 m/s on
# the route), and the saved time goes to the hold on the slammed-in ball, Levi and the cleanup / pyres.  Camera keys, light
# keys and the pyres are written on the VIDEO clock.
WARP = [(0.0, 0.0), (19.0, 19.0), (38.0, 47.0), (39.6, 48.6), (46.5, 53.5), (54.5, 60.0), (60.5, 66.0), (71.0, 71.0), (75.0, 75.0)]

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
    green=3.0, eren_swing=(1.0, 4.45), transform=4.5, roar1=(5.0, 5.6), smash=6.0, miss=7.0, red=8.0, selfpunch=9.5,
    stagger=(9.75, 10.45), sit=(10.4, 11.0), armin_land=12.0, t7_kill=12.6, stab=13.5, t12_kill=14.2,
    wake=15.0, standup=(15.0, 16.0), turn=(16.0, 16.6), squat=(16.6, 17.3), chest=(17.3, 18.2), overhead=(18.2, 19.0),
    carry=(19.0, 47.0), rad_kill=23.0, crawler_kill=27.6, west_street=(30.5, 37.0), trainee_kill=35.2, trench_fall=38.0,
    breach_in=(22.0, 31.0, 40.0), mitabi_grab=(40.4, 41.2), crouch_kill=43.4, ian_grab=43.5,
    roar2=(47.0, 47.9), slam=(47.9, 48.3), jam=48.3, slump=(48.5, 50.6),             # OWNER 10/27: ONE instant slam (~0.4 s)
    plug=(48.8, 52.8), face_plug=(48.8, 52.3), yellow=53.0, relay=54.5, nape_cut=(52.0, 60.0),
    levi_drop=55.5, levi_cut1=56.3, levi_cut2=56.7, levi_stand=57.5,
    night=(59.6, 62.8), day=(63.2, 66.0), survey=(62.8, 66.2), captured=64.8, d_clear=(60.2, 64.6),
    cleanup=(66.0, 71.0), rows=(66.0, 69.2), pyres=(66.4, 67.4, 68.4, 69.4), end_hold=(71.0, 75.0))

# ====================================================================== anchors (frame M; bible section C + g8 spec 2a-2d)
BALL_R = 7.0                                   # ONE radius everywhere (bible C BALL); trost.BALL_R overrides if present
B0 = (290.0, 262.0); BALL_REST0 = (290.0, 262.0, 7.4)           # ball on its lawn bed (sunk 0.2 m into the 0.6 m bed)
BALL_DROP = (0.0, 17.5, 7.0); BALL_SEAL = (0.0, 10.5, 7.0)       # slammed into the ball-sized hole (owner 10/27): wedged in the
                                                                # gatehouse opening, 2.5 m proud of the face so it reads
BERSERK = (260.0, 289.0); MIKASA_ROOF = (252.0, 300.0); MISS_ROOF = (241.0, 289.0)
SIT = (281.0, 271.0)                                            # hips on the bed kerb, back against the ball's NW face
LIFT = (290.0, 273.5)                    # stands, shuffles round to the ball's NORTH side and lifts facing south (route side):
                                         # the lift and the first carry leg read side-on from the town (west) side, never his back
ROUTE = [LIFT, (284, 232), (280, 160), (274, 117), (228, 86), (185, 64), (141, 47), (95, 35), (63, 29), (36, 21), (18, 18.5), (4, 23)]
ROUTE_NAMES = ["lift", "R1", "R2", "R3", "a1", "a2", "a3", "a4", "R4", "R5", "R5b", "R6"]
ROUTE_T = [19.0, 21.8, 26.2, 29.8, None, None, None, None, 42.8, 44.4, 45.6, 47.0]   # None = by distance (cruise)
SLAM_POS = (2.5, 20.5)                           # lunges 3 m south from R6 as he slams the ball down into the breach
KNEEL = (8.0, 19.5)                              # then slumps sideways onto its NE shoulder: the ball's front stays visible (QA)
RICO_DECK = (16.0, 36.0)                         # AUDIT 7: Rico east of the 20 m push gap (deck X 12..20, Y 32..40)
GF = (334.0, 136.0, 51.5); RF = (306.0, 300.0, 19.0); YF = (22.0, 52.0, 2.5); PY = (-20.0, 870.0, 50.5)
LV = (-40.0, 2.0, 50.5); CT = [(-45.0, 45.0), (-55.0, 32.0)]; MI = (-67.0, 18.0); IA = (-36.0, 56.0)
CROUCH = (44.0, 27.0); CROUCH_FALL = (52.0, 36.0); PIT = (0.0, 36.0)
PYRES = [(284.0, 116.0), (-60.0, 470.0), (-12.0, 250.0), (150.0, 330.0), (50.0, 55.0), (262.0, 140.0)]   # v14: + the corner corpses
PYRE_T = (60.6, 61.4, 62.4, 63.4, 64.4, 65.2)    # VIDEO clock: v14 the titan corpses burn one by one in the NIGHT sky view
D_BOX = (-475.0, -360.0, 760.0, 865.0)
HERD_KILL = 62.0                                 # owner 10/27: the herded corner group dies in one massed volley (choreo clock)
NO_SPARKLES = True                               # owner 10/27: no muzzle / shell glow cards in the mop-up
PILASTER_E = (17.0, 27.0, 11.0)                  # east pilaster X 17..27, town-side face Y 11

# ====================================================================== camera (bible g8 keys, tight column; K0 = g7 C15 seam)
_SEAM_IN = segtime.seam("g7_g8"); _SEAM_OUT = segtime.seam("g8_end")
CAM_KEYS = [
    (0.0,  tuple(_SEAM_IN["pos"]), tuple(_SEAM_IN["look"]), _SEAM_IN["lens"]),        # K0 = g7 C15
    # OWNER 10/27 16:51: "distant is actually better" -> the v1 camera distances and framing; times follow the WARP
    (6.5,  (60, 660, 205),   (252, 296, 6),   40),     # K2' green trail, transformation, roof smash (bible K2 6.0 (-40, 760, 210)
                                                       #     -> (230, 320, 0) 28 mm left the berserk at 556 m / 28 mm unreadable)
    (13.0, (60, 300, 150),   (282, 268, 8),   35),     # K3' the court from the WEST: over its open west half the sitting titan
    (15.5, (100, 250, 120),  (285, 265, 10),  42),     # K4' reads (bible K3/K4 from the NNW: blocked by the north terrace and
                                                       #     the court belfry (228, 290) at the court's NW corner)
    (19.0, (71, 304, 150),   (289, 266, 14),  40),     # v17 (FEEDBACK_v15 ~2:45): ZOOMED OUT, watched from far away     # v4 (QA batch1: carry hard to read): ~110 m, not 170     # K5' the lift side-on from the west (bible K5 (175, 395, 105) saw his back)
    (25.1, (44, 157, 150),   (276, 143, 12),  40),     # C1' carry side-on from the town (west) side
    (31.9, (-70, 132, 152),  (150, 52, 12),   38),     # C2' along the wall, front three-quarter from WNW (open strip)
    (36.6, (-60, 175, 95),   (40, 24, 12),    40),     # C3 the gate square, Mikasa's kill
    (40.0, (-75, 150, 90),   (3, 14, 12),     42),     # S1 the slam (39.3, camera shake) and the ball wedged in the breach
    (43.5, (-80, 160, 93),   (2, 13, 12),     41),     # S1b hold on the wedged ball, the plug grows, 5 titans face it
    (47.1, (-95, 225, 135),  (0, 20, 40),     32),     # S2 the Λ plug and the yellow trail (from the east plank box)
    (52.0, (-105, 245, 140), (0, 30, 15),     34),     # L1 Levi
    (55.0, (150, 250, 140), (282, 118, 8), 40),       # v14: the wall corner (east strip): the herded titans, the massed cannons
    (57.4, (175, 225, 120), (283, 118, 8), 50),       #   (HERD_KILL = local 56.5, daylight), slight zoom
    (60.2, (-180, 420, 260), (-200, 230, 0),  30),     #   then up into the sky as night falls
    (63.4, (-80, 560, 430),  (-120, 280, 0),  28),     # v14: NIGHT, full sky view: the titan corpses burning
    (71.0, (120, 680, 330),  (-90, 300, 0),   28),
    # v18 (FEEDBACK_v17): THE END - straight up from the burning town until Walls Maria, Rose and Sina are in one frame
    # (Mitras = W (0, 24000) = M (0, 19870); Maria r 24 km), hold
    (72.4, (60, 1500, 2600),     (-60, 2600, 0),    28),
    (73.6, (0, 9000, 30000),     (0, 15500, 0),     26),
    (75.0, (0, 13500, 66000),    (0, 19870, 0),     24),
    (76.0, (0, 13500, 66500),    (0, 19870, 0),     24),     # guide key (rest)
]
CAM = camchan.CamPath(CAM_KEYS, v_in=_SEAM_IN["vel"], v_out=None)
CAM_LIMITS = dict(hmin=89.0, speed=67.5, yaw=30.0)

# ====================================================================== pure kinematics (no bpy)
def ss(a, b, x):
    u = min(1.0, max(0.0, (x - a) / (b - a))) if b != a else float(x >= b)
    return u * u * (3 - 2 * u)

def lerp(a, b, u):
    return a + (b - a) * u

def bump(t, a, b, c, d):
    return ss(a, b, t) * (1 - ss(c, d, t))

def yaw_to(dx, dy):
    """Heading (radians CCW from +Y) of the direction (dx, dy) (attack_titan / odm convention)."""
    return math.atan2(-dx, dy)

def ang_lerp(a, b, u):
    d = (b - a + math.pi) % math.tau - math.pi
    return a + d * u

_RP = np.array(ROUTE, float)
_RS = np.concatenate([[0.0], np.cumsum(np.hypot(*np.diff(_RP, axis=0).T))])
ROUTE_LEN = float(_RS[-1])

def _route_knots():
    T = list(ROUTE_T)
    # cruise points: interpolate time by distance between the named neighbours
    for i, tv in enumerate(T):
        if tv is None:
            a = max(j for j in range(i) if T[j] is not None)
            b = min(j for j in range(i + 1, len(T)) if ROUTE_T[j] is not None)
            T[i] = T[a] + (ROUTE_T[b] - T[a]) * (_RS[i] - _RS[a]) / (_RS[b] - _RS[a])
    return np.array(T, float)
_RT = _route_knots()
_RM = camchan.pchip_m(list(_RT), list(_RS), 0.0, 0.0)

def route_s(t):
    """Distance walked along ROUTE at time t (monotone, starts and ends at rest)."""
    if t <= _RT[0]:
        return 0.0
    if t >= _RT[-1]:
        return ROUTE_LEN
    return float(camchan.pchip(list(_RT), list(_RS), _RM, t))

def route_t_of_s(s):
    lo, hi = _RT[0], _RT[-1]
    for _ in range(40):
        m = (lo + hi) / 2
        if route_s(m) < s: lo = m
        else: hi = m
    return (lo + hi) / 2

def route_xy(s):
    s = min(max(s, 0.0), ROUTE_LEN)
    i = int(min(len(_RS) - 2, np.searchsorted(_RS, s, side="right") - 1))
    u = (s - _RS[i]) / max(_RS[i + 1] - _RS[i], 1e-9)
    return _RP[i] + (_RP[i + 1] - _RP[i]) * u

def route_yaw(s):
    a, b = route_xy(s - 5.0), route_xy(s + 5.0)
    if s < 5.0:
        a, b = route_xy(0.0), route_xy(10.0)
    return yaw_to(b[0] - a[0], b[1] - a[1])

STEP_L = 10.5         # m per step (tight cut: 446 m in 28 s; cruise ~17 m/s -> ~2 steps/s, the bible's 'heavy jog' option)
FOOT_A = 4.9          # stride half-amplitude in the pose (feet slide < 0.6 m per step)
FOOT_W = 1.7

def foot_w(s):
    """Stance half-width: narrows to 1.0 m through the R5 -> R6 squeeze (the outer trench's east arm ends at Y 19)."""
    return FOOT_W - (FOOT_W - 1.0) * ss(_RS[8] + 4.0, _RS[9], s)

def body_south_shift(s):
    """0.9 m south of the exact R5b -> R6 line where the north foot would graze the outer trench's east-arm end."""
    return 0.9 * ss(_RS[9] + 6.0, _RS[10] - 2.0, s) * (1 - ss(_RS[10] + 4.0, _RS[11] - 2.0, s))

def ball_north_shift(s):
    """The ball rides 1 m north of the route line through R5 -> R6 (R5b squeeze: 1.5 m off the east pilaster face);
    relative to his (shifted) centre line that is 1.0-1.9 m."""
    return 1.0 * ss(_RS[8] + 6.0, _RS[9], s) + body_south_shift(s)

def _yaw(p, q):
    return yaw_to(q[0] - p[0], q[1] - p[1])

Y_BERSERK = _yaw(BERSERK, MIKASA_ROOF)              # facing Mikasa's roof (NW)
Y_SIT = _yaw(BALL_REST0, SIT)                       # sitting, facing away from the ball (NW)
Y_BALL = math.pi                                    # at the ball's north side, facing it (south)
Y_SOUTH = math.pi

def at_state(t):
    """Attack Titan state, pure in t: dict(vis, pos (x, y) M, yaw, scale, mode, u, phase, sway, zoff, eyes, burn)."""
    st = dict(vis=t >= BEATS["transform"], pos=np.array(BERSERK), yaw=Y_BERSERK, scale=1.0, mode="stand", u=0.0,
              phase=0.0, sway=0.0, zoff=0.0, eyes=28.0, burn=0.0, ball_w=0.0)
    if t < BEATS["transform"]:
        return st
    st["scale"] = 0.18 + 0.82 * ss(4.5, 5.25, t)
    st["burn"] = 0.9 * ss(BEATS["carry"][0], 33.0, t)
    sm = BEATS["smash"]; mi = BEATS["miss"]; sp = BEATS["selfpunch"]
    if t < sm - 0.6:
        st["mode"] = "roar" if t >= 4.9 else "stand"; st["u"] = bump(t, 4.9, 5.1, 5.35, 5.6)
    elif t < sm + 0.9:                                   # wind-up and smash on Mikasa's roof (one step forward)
        st["mode"] = "smash"; st["u"] = ss(sm - 0.6, sm - 0.15, t) - 0.0; st["u2"] = ss(sm - 0.15, sm, t) * (1 - ss(sm + 0.45, sm + 0.9, t))
        st["pos"] = np.array(BERSERK) + 2.0 * np.array([-math.sin(Y_BERSERK), math.cos(Y_BERSERK)]) * ss(sm - 0.3, sm, t) * (1 - ss(sm + 0.5, sm + 0.9, t))
    elif t < mi + 0.9:                                   # second swing, misses her, hits the roof where she was
        y2 = _yaw(BERSERK, MISS_ROOF)
        st["yaw"] = ang_lerp(Y_BERSERK, y2, ss(mi - 1.1, mi - 0.6, t))
        st["mode"] = "smash"; st["u"] = ss(mi - 0.75, mi - 0.15, t); st["u2"] = ss(mi - 0.15, mi, t) * (1 - ss(mi + 0.4, mi + 0.9, t))
    elif t < sp - 0.7:
        st["yaw"] = _yaw(BERSERK, MISS_ROOF); st["mode"] = "roar"; st["u"] = bump(t, 8.1, 8.3, 8.6, 8.9)
    elif t < BEATS["stagger"][0]:                        # third swing -> a fist into his own face
        st["yaw"] = ang_lerp(_yaw(BERSERK, MISS_ROOF), Y_SIT, ss(sp - 0.7, sp - 0.3, t))
        st["mode"] = "selfpunch"; st["u"] = ss(sp - 0.7, sp - 0.35, t); st["u2"] = ss(sp - 0.25, sp, t)
    elif t < BEATS["sit"][0]:                            # staggers back 4 heavy steps toward the ball
        a, b = BEATS["stagger"]
        u = ss(a, b + 0.2, t)
        st["yaw"] = Y_SIT; st["mode"] = "stagger"; st["u"] = 1.0
        st["pos"] = np.array(BERSERK) + (np.array(SIT) - np.array(BERSERK)) * (u * 0.88)
        st["phase"] = math.pi * 4.0 * u
    elif t < BEATS["wake"]:                              # sits down hard, back against the ball's NW face
        a, b = BEATS["sit"]
        st["yaw"] = Y_SIT; st["mode"] = "sit"; st["u"] = ss(a, b, t)
        st["pos"] = np.array(BERSERK) + (np.array(SIT) - np.array(BERSERK)) * (0.88 + 0.12 * ss(a, b, t))
        st["eyes"] = 28.0 * (1 - ss(a, b, t))
    elif t < BEATS["turn"][0]:                           # wakes: sit -> crouch -> stand
        a, b = BEATS["standup"]
        st["pos"] = np.array(SIT); st["yaw"] = Y_SIT; st["mode"] = "standup"; st["u"] = ss(a + 0.1, b, t)
        st["eyes"] = 28.0 + 30.0 * bump(t, 15.0, 15.15, 15.5, 16.2)
    elif t < BEATS["squat"][0]:                          # turns round and shuffles to the ball's north side
        a, b = BEATS["turn"]
        u = ss(a, b, t)
        mid = np.array([284.0, 277.5])
        st["pos"] = (np.array(SIT) * (1 - u) + mid * u) * (1 - u) + (mid * (1 - u) + np.array(LIFT) * u) * u
        st["yaw"] = Y_SIT - math.radians(225.0) * u; st["mode"] = "stand"     # turns right (NW -> N -> E -> S) as he steps east
        st["phase"] = math.pi * 3 * u
    elif t < BEATS["carry"][0]:                          # squat, heave to the chest, press overhead
        st["pos"] = np.array(LIFT)
        st["yaw"] = ang_lerp(Y_BALL, route_yaw(0.0), ss(18.3, 19.0, t))
        st["mode"] = "lift"; st["u"] = t
    elif t < BEATS["carry"][1]:                          # the carry
        s = route_s(t)
        st["pos"] = route_xy(s) - np.array([0.0, body_south_shift(s)]); st["yaw"] = route_yaw(s); st["mode"] = "carry"; st["s"] = s
        st["phase"] = math.pi * s / STEP_L
        st["ramp"] = ss(19.0, 19.8, t) * (1 - ss(46.4, 47.0, t))
        if s > _RS[-2]:
            st["yaw"] = ang_lerp(route_yaw(s), math.pi / 2, ss(_RS[-2], ROUTE_LEN, s))
    else:
        r6 = np.array(ROUTE[-1]); sp_ = np.array(SLAM_POS); kn = np.array(KNEEL)
        a, b = BEATS["slam"]
        st["yaw"] = ang_lerp(math.pi / 2, Y_SOUTH, ss(46.8, 47.6, t))
        p = r6 + (sp_ - r6) * ss(a - 0.1, b, t)
        p = p + (kn - sp_) * ss(BEATS["slump"][0], BEATS["slump"][1], t)
        st["pos"] = p
        if t < a:
            st["mode"] = "roar_carry"; st["u"] = bump(t, 47.0, 47.3, 47.6, 47.9)
        elif t < BEATS["slump"][0]:
            st["mode"] = "slam"; st["u"] = ss(a, b, t)
        else:
            st["mode"] = "slump"; st["u"] = ss(*BEATS["slump"], t)
            st["yaw"] = ang_lerp(Y_SOUTH, yaw_to(BALL_SEAL[0] + 3.0 - KNEEL[0], BALL_SEAL[1] + 4.0 - KNEEL[1]), st["u"])
            st["eyes"] = 28.0 * (1 - ss(51.0, 53.0, t))
    return st

def carry_bent_w(t):
    """v14 (FEEDBACK_v13 §1, anime ep13): 0..1 weight of the bent, struggling carry (boulder on the shoulders, face pressed to
    the rock, one heavy step at a time) - eases in after the overhead lift and back out for the roar before the slam."""
    return ss(BEATS["overhead"][1], BEATS["overhead"][1] + 1.2, t) * (1.0 - ss(BEATS["roar2"][0] - 1.0, BEATS["roar2"][0], t))

def ball_state(t, at=None, frame=None):
    """Ball centre (M) + roll angles.  Before the lift it rests on its bed; after the jam it rests at BALL_SEAL.
    While carried it rides on the titan: frame = dict(head=(f, z) titan-frame offsets) supplied by the Blender side."""
    zc = (frame or {}).get("zc", 20.6); fc = (frame or {}).get("fc", 1.0)
    rest = np.array(BALL_REST0)
    if t < BEATS["chest"][0]:
        return rest, 0.0, 0.0
    at = at or at_state(t)
    yaw = at["yaw"]; fw = np.array([-math.sin(yaw), math.cos(yaw), 0.0]); rt = np.array([math.cos(yaw), math.sin(yaw), 0.0])
    base = np.array([at["pos"][0], at["pos"][1], 0.0])
    def tf(r, f, z):
        return base + rt * r + fw * f + np.array([0, 0, z])
    bob = at.get("bob", 0.0)
    over = tf(0.0, fc, zc + bob)
    if t < BEATS["chest"][1]:
        u = ss(*BEATS["chest"], t)
        chest = tf(0.0, 5.6, 11.5)
        return rest + (chest - rest) * u, -0.4 * u, 0.0
    if t < BEATS["overhead"][1]:
        u = ss(*BEATS["overhead"], t)
        chest = tf(0.0, 5.6, 11.5)
        return chest + (over - chest) * u, -0.4 - 0.6 * u, 0.0
    if t < BEATS["slam"][0]:
        s = at.get("s", ROUTE_LEN)
        c = over + np.array([0.0, ball_north_shift(s), 0.0])
        wb = carry_bent_w(t)                                       # v14: the boulder rides on his upper back / shoulders
        c = c + (tf(0.0, -2.6, 15.2) - over) * wb
        return c, -1.0 + 0.05 * math.sin(at.get("phase", 0.0)), 0.04 * math.sin(at.get("phase", 0.0))
    seal = np.array(BALL_SEAL)
    a, b = BEATS["slam"]
    if t < b:                                                    # the slam: overhead -> into the breach, accelerating
        u = ((t - a) / (b - a)) ** 2
        top = over + np.array([0.0, 0.5, 1.5]) * math.sin(math.pi * min(1.0, (t - a) / (b - a)))
        c = top + (seal - top) * u
        return c, -1.0 - 1.6 * u, 0.0
    return seal, -2.6, 0.0

# ====================================================================== everything below needs Blender
STATE = {}
PLACEHOLDERS = []

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
    """Ground height at M (x, y)."""
    return _site()["ground_M"](float(x), float(y))

def _coll(name):
    c = bpy.data.collections.get(name)
    return c if c else STATE["L"].new_coll(name)

def emit_mat(name, rgb, strength):
    import flares as FX
    return FX.emit_mat(name, rgb, strength)

def hexrgb(h):
    h = h.lstrip("#"); c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c)

def _hide(ob, h):
    if ob is not None and (ob.hide_render != h or ob.hide_viewport != h):
        ob.hide_render = ob.hide_viewport = h

# ---------------------------------------------------------------------- roof / ground probing (before our own geometry)
_RC = {}
def top_z(x, y, default=None, zmax=400.0):
    """Highest surface under M (x, y) (roof, wall top or ground) by a scene ray cast; cached."""
    key = (round(x, 1), round(y, 1))
    if key in _RC:
        return _RC[key]
    dg = bpy.context.evaluated_depsgraph_get()
    o = SV(x, y, zmax)
    hit, loc, nrm, idx, ob, mw = bpy.context.scene.ray_cast(dg, o, Vector((0, 0, -1)))
    z = float(loc.z) if hit else (default if default is not None else G(x, y))
    if hit and ob is not None and (ob.name.startswith("Haze") or ob.name.startswith("Sky")):
        z = default if default is not None else G(x, y)
    _RC[key] = z
    return z

def perch(x, y, rnd=None, search=6.0):
    """A standing spot on top of whatever is at M (x, y): the highest of a few probes (roof ridges read best)."""
    best = None
    for dx, dy in ((0, 0), (search, 0), (-search, 0), (0, search), (0, -search)):
        z = top_z(x + dx, y + dy)
        if best is None or z > best[2] + 0.5:
            best = (x + dx, y + dy, z)
    return np.array([best[0], best[1], best[2] + 0.05])

# ====================================================================== the ball
def ball_material():
    m = bpy.data.materials.new("G8_BallStone"); m.use_nodes = True
    nt = m.node_tree; N = nt.nodes; Lk = nt.links
    b = N["Principled BSDF"]; b.inputs["Roughness"].default_value = 0.85
    tc = N.new("ShaderNodeTexCoord")
    # marbling: noise-warped wave bands -> dark charcoal veins on warm grey
    nw = N.new("ShaderNodeTexNoise"); nw.inputs["Scale"].default_value = 0.18; nw.inputs["Detail"].default_value = 4
    Lk.new(tc.outputs["Object"], nw.inputs["Vector"])
    ws = N.new("ShaderNodeVectorMath"); ws.operation = "SCALE"; ws.inputs["Scale"].default_value = 4.0
    Lk.new(nw.outputs["Color"], ws.inputs[0])
    wa = N.new("ShaderNodeVectorMath"); wa.operation = "ADD"; Lk.new(tc.outputs["Object"], wa.inputs[0]); Lk.new(ws.outputs[0], wa.inputs[1])
    wv = N.new("ShaderNodeTexWave"); wv.inputs["Scale"].default_value = 0.09; wv.inputs["Distortion"].default_value = 6.0
    wv.inputs["Detail"].default_value = 3; Lk.new(wa.outputs[0], wv.inputs["Vector"])
    vr = N.new("ShaderNodeMapRange"); vr.inputs["From Min"].default_value = 0.78; vr.inputs["From Max"].default_value = 0.95
    Lk.new(wv.outputs["Fac"], vr.inputs["Value"])
    base = N.new("ShaderNodeMix"); base.data_type = "RGBA"
    base.inputs["A"].default_value = (*hexrgb("#8f8a82"), 1); base.inputs["B"].default_value = (*hexrgb("#3b3a3a"), 1)
    Lk.new(vr.outputs["Result"], base.inputs["Factor"])
    # pale weathered patches
    npch = N.new("ShaderNodeTexNoise"); npch.inputs["Scale"].default_value = 0.35; npch.inputs["Detail"].default_value = 3
    Lk.new(tc.outputs["Object"], npch.inputs["Vector"])
    pr = N.new("ShaderNodeMapRange"); pr.inputs["From Min"].default_value = 0.58; pr.inputs["From Max"].default_value = 0.7
    pr.inputs["To Max"].default_value = 0.8; Lk.new(npch.outputs["Fac"], pr.inputs["Value"])
    pale = N.new("ShaderNodeMix"); pale.data_type = "RGBA"; pale.inputs["B"].default_value = (*hexrgb("#c9c4b8"), 1)
    Lk.new(base.outputs["Result"], pale.inputs["A"]); Lk.new(pr.outputs["Result"], pale.inputs["Factor"])
    # fine crack network (Voronoi edges, warped)
    vo = N.new("ShaderNodeTexVoronoi"); vo.feature = "DISTANCE_TO_EDGE"; vo.inputs["Scale"].default_value = 0.42
    Lk.new(wa.outputs[0], vo.inputs["Vector"])
    cr = N.new("ShaderNodeMapRange"); cr.inputs["From Min"].default_value = 0.0; cr.inputs["From Max"].default_value = 0.018
    cr.inputs["To Min"].default_value = 0.85; cr.inputs["To Max"].default_value = 0.0
    Lk.new(vo.outputs["Distance"], cr.inputs["Value"])
    crk = N.new("ShaderNodeMix"); crk.data_type = "RGBA"; crk.inputs["B"].default_value = (*hexrgb("#2a2826"), 1)
    Lk.new(pale.outputs["Result"], crk.inputs["A"]); Lk.new(cr.outputs["Result"], crk.inputs["Factor"])
    Lk.new(crk.outputs["Result"], b.inputs["Base Color"])
    fn = N.new("ShaderNodeTexNoise"); fn.inputs["Scale"].default_value = 3.0; fn.inputs["Detail"].default_value = 6
    Lk.new(tc.outputs["Object"], fn.inputs["Vector"])
    hsub = N.new("ShaderNodeMath"); hsub.operation = "SUBTRACT"; Lk.new(fn.outputs["Fac"], hsub.inputs[0]); Lk.new(cr.outputs["Result"], hsub.inputs[1])
    bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.35; bp.inputs["Distance"].default_value = 0.15
    Lk.new(hsub.outputs[0], bp.inputs["Height"]); Lk.new(bp.outputs["Normal"], b.inputs["Normal"])
    return m

def build_ball(coll):
    L = STATE["L"]
    sb = bpy.data.objects.get("TrostBoulder")
    if sb is not None and sb.type == "MESH":
        dims = sb.dimensions
        if abs(max(dims.x, dims.y) - 2 * BALL_R) < 1.0:          # the set's ball (origin at its centre, r 7): one ball
            sb.rotation_mode = "XYZ"
            STATE["ball"] = sb
            print(f"[g8] using the set's TrostBoulder ({dims.x:.1f} x {dims.y:.1f} x {dims.z:.1f} m)")
            return
        sb.hide_render = sb.hide_viewport = True
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=5, radius=1.0)
    off = Vector((3.1, 7.7, 1.3))
    for v in bm.verts:
        n = v.co.normalized()
        d = 0.25 * noise.noise(n * 1.1 + off) + 0.06 * noise.noise(n * 3.0 + off * 2)     # low frequency only: stays a ball
        v.co = Vector((n.x * (BALL_R + d), n.y * (BALL_R + d), n.z * (BALL_R * 13.6 / 14.0 + d)))
    for f in bm.faces:
        f.smooth = True
    ob = L.obj_from_bm("TrostBoulderCarry", bm, [ball_material()], coll)       # toon outline key name
    ob.rotation_mode = "XYZ"
    STATE["ball"] = ob

# ====================================================================== Attack Titan (asset) with blended, per-frame poses
def _V(r, f, z):
    import attack_titan as AT
    return AT.V(r, f, z)

def _spec_copy(s):
    import copy
    return copy.deepcopy(s)

def blend(a, b, u):
    """Blend two pose specs (attack_titan format)."""
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
    P = {k: _spec_copy(v) for k, v in AT.POSES.items() if k in ("stand", "roar", "punch", "crouch")}
    st = P["stand"]
    P["windup"] = dict(st, hips=8.5, bend=_bends(-8, -8, -4, 2, 2, (0, -10, -10, 0, 0)),
                       hands={"R": (V(1.0, -1.6, 2.8), V(1, -0.5, 0), "sh"), "L": (V(-0.9, 1.4, -3.8), V(-0.4, -1, 0), "sh")}, fist=1.0, jaw=18)
    P["smash"] = dict(st, hips=7.4, bend=_bends(14, 10, 6, -4, -6, (0, 8, 8, 0, 0)),
                      feet={"R": (V(1.6, -1.6, 0), -10), "L": (V(-1.6, 2.6, 0), 10)},
                      hands={"R": (V(-0.2, 4.6, -1.6), V(1, 0, -1), "sh"), "L": (V(-0.9, 0.4, -4.4), V(-0.4, -1, 0), "sh")}, fist=1.0, jaw=25)
    P["selfwind"] = dict(st, hips=8.4, bend=_bends(-6, -6, -2, 0, 0, (0, -6, -6, 0, 0)),
                         hands={"R": (V(1.9, -0.6, 1.2), V(1, -0.6, 0), "sh"), "L": (V(-0.9, 0.7, -4.4), V(-0.4, -1, 0), "sh")}, fist=1.0, jaw=12)
    P["selfhit"] = dict(st, hips=8.2, bend=_bends(-10, -12, -10, -14, -28),
                        hands={"R": (V(0.25, 1.6, 13.4), V(1, -0.2, -0.6), "abs"), "L": (V(-1.6, -0.6, -4.0), V(-1, -0.6, 0), "sh")}, fist=1.0, jaw=30)
    P["stagger"] = dict(st, hips=8.0, bend=_bends(-12, -10, -4, 6, 18),
                        hands={"R": (V(1.8, -0.8, -3.0), V(1, -0.6, 0), "sh"), "L": (V(-1.8, -0.8, -3.0), V(-1, -0.6, 0), "sh")}, fist=0.2, jaw=10)
    P["sit"] = dict(hips=2.1, bend=_bends(-24, -8, 10, 16, 34), feet={"R": (V(2.3, 7.4, 0), -18), "L": (V(-2.1, 7.0, 0), 18)},
                    knee=V(0, 0.3, 1.0), hands={"R": (V(4.0, 0.6, 0.6), V(1, -0.4, 0.2), "abs"), "L": (V(-4.0, 1.0, 0.6), V(-1, -0.4, 0.2), "abs")},
                    fist=0.1, jaw=6)
    P["squat"] = dict(hips=4.6, bend=_bends(26, 12, 4, -6, -10), feet={"R": (V(3.0, 0.4, 0), -22), "L": (V(-3.0, 0.4, 0), 22)},
                      knee=V(0, 1, 0.25), hands={"R": (V(5, 6, 6), V(1, -0.3, -0.5), "abs"), "L": (V(-5, 6, 6), V(-1, -0.3, -0.5), "abs")}, fist=0.2, jaw=14)
    P["chest"] = dict(hips=7.2, bend=_bends(-6, -6, -2, 4, 6), feet={"R": (V(2.6, 0.4, 0), -14), "L": (V(-2.6, 0.2, 0), 14)},
                      knee=V(0, 1, 0.1), hands={"R": (V(4, 5, 11), V(1, -0.3, -0.5), "abs"), "L": (V(-4, 5, 11), V(-1, -0.3, -0.5), "abs")}, fist=0.2, jaw=20)
    # v17 (FEEDBACK_v15 + ref/user/eren_boulder_pose_ref.png): torso UPRIGHT under the rock, the head bowed and pressed under
    # it (no neck jutting forward), the right arm raised high with the hand gripping the rock face, the left hand lower on it
    P["carry"] = dict(hips=7.15, bend=_bends(2, 2, 0, 4, 28), feet={"R": (V(FOOT_W, 0.0, 0), -6), "L": (V(-FOOT_W, 0.0, 0), 6)},
                      knee=V(0, 1, 0), hands={"R": (V(4.4, 0.6, 16.6), V(1, 0.1, -0.2), "abs"), "L": (V(-4.8, 1.2, 13.6), V(-1, 0.2, -0.4), "abs")},
                      fist=0.35, jaw=12)
    P["carry_bent"] = dict(P["carry"], hips=6.8, bend=_bends(6, 4, 2, 6, 32), jaw=20,
                           hands={"R": (V(4.5, 0.3, 16.1), V(1, 0.1, -0.2), "abs"), "L": (V(-4.9, 0.8, 13.0), V(-1, 0.2, -0.4), "abs")})
    P["roar_carry"] = dict(P["carry"], hips=7.8, bend=_bends(-4, -6, -6, -10, -6), jaw=34)
    P["drop"] = dict(hips=6.6, bend=_bends(22, 12, 6, 0, 0), feet={"R": (V(1.9, 0.8, 0), -8), "L": (V(-1.9, -0.6, 0), 8)},
                     knee=V(0, 1, 0.1), hands={"R": (V(5, 6, 10), V(1, 0.2, -0.5), "abs"), "L": (V(-5, 6, 10), V(-1, 0.2, -0.5), "abs")}, fist=0.1, jaw=16)
    P["shove"] = dict(hips=4.4, bend=_bends(34, 16, 6, -10, -16, (0, 8, 8, 0, 0)), feet={"R": (V(2.0, -1.2, 0), -10), "L": (V(-1.9, -4.6, 0), 10)},
                      knee=V(0, 1, 0.2), hands={"R": (V(3, 5, 6), V(1, -0.2, -0.6), "abs"), "L": (V(-3, 5, 6), V(-1, -0.2, -0.6), "abs")}, fist=0.1, jaw=24)
    P["slump"] = dict(hips=3.6, bend=_bends(40, 18, 8, 10, 30), feet={"R": (V(1.9, -5.2, 0), -8), "L": (V(-1.9, -4.9, 0), 8)},
                      knee=V(0, 1, -0.6), hands={"R": (V(3, 4, 7), V(1, -0.2, -0.6), "abs"), "L": (V(-3, 4, 7), V(-1, -0.2, -0.6), "abs")}, fist=0.0, jaw=8)
    P["roar"] = dict(P["roar"])
    P["slam"] = dict(hips=5.6, bend=_bends(34, 16, 8, -6, -12), feet={"R": (V(2.0, 1.4, 0), -8), "L": (V(-2.0, -2.8, 0), 8)},
                     knee=V(0, 1, 0.15), hands={"R": (V(2.6, 7.0, 3.0), V(1, 0.2, -0.5), "abs"), "L": (V(-2.6, 7.0, 3.0), V(-1, 0.2, -0.5), "abs")},
                     fist=0.2, jaw=34)
    return P

def _ball_hands(spec, c_tf, dirs, pole):
    """Hand IK targets on the ball surface (titan frame): centre c_tf + r * normalize(dir) per side."""
    out = dict(spec); h = {}
    for sd, sg in (("R", 1.0), ("L", -1.0)):
        d = Vector((dirs[0] * sg, dirs[1], dirs[2]))
        dv = _V(d.x, d.y, d.z).normalized()
        h[sd] = (c_tf + dv * (BALL_R + 0.15), _V(pole[0] * sg, pole[1], pole[2]), "abs")
    out["hands"] = h
    return out

def _to_tf(p_world_set, hol_loc, yaw):
    """World (set) point -> titan frame vector (attack_titan.V convention) for a holder at hol_loc with heading yaw."""
    d = Vector(p_world_set) - Vector(hol_loc)
    rt = Vector((math.cos(yaw), math.sin(yaw), 0)); fw = Vector((-math.sin(yaw), math.cos(yaw), 0))
    return _V(d.dot(rt), d.dot(fw), d.z)

def build_titan(coll):
    import attack_titan as AT
    t0 = time.time()
    T = AT.place_attack(0.0, -5000.0, 0.0, "stand", name="G8Attack", eyes=28.0)
    STATE["AT"] = T
    # shoulder positions (titan frame) in the stand pose, for blending "sh" <-> "abs" hand targets
    T.holder.matrix_world = Matrix.Identity(4); bpy.context.view_layer.update()
    T.pose("stand", ground=False)
    STATE["SH"] = {"L": T.wpos("upper_arm.L_32").copy(), "R": T.wpos("upper_arm.R_55").copy()}
    STATE["P"] = make_poses()
    # ball seat in the carry pose: bottom of the ball on the bowed head
    AT.POSES["_g8"] = STATE["P"]["carry"]; T.pose("_g8", ground=False)
    hd = T.wpos("Head_9", tail=True)
    head_top = hd + (hd - T.wpos("Head_9")).normalized() * 0.4
    fc = -head_top.y                      # titan frame forward = -Y native (holder at identity)
    STATE["seat"] = dict(zc=float(head_top.z) + BALL_R - 0.35, fc=float(fc))
    print(f"[g8] Attack Titan imported {time.time() - t0:.1f}s; carry seat zc={STATE['seat']['zc']:.2f} fc={fc:.2f}; "
          f"shoulders {tuple(round(c, 2) for c in STATE['SH']['R'])}")
    # skin -> red muscle as it strips (attack_titan's burn mix, recoloured): #8e2f25, dim orange sinews
    for m in T.skin_mats:
        N = m.node_tree.nodes
        d = N.get("at_dark")
        if d:
            d.inputs["B"].default_value = (*hexrgb("#8e2f25"), 1)
        for n in N:
            if n.type == "MIX" and n.data_type == "RGBA" and n.blend_type == "MULTIPLY" and tuple(round(c, 2) for c in n.inputs["B"].default_value[:3]) == (1.0, 0.32, 0.06):
                n.inputs["B"].default_value = (0.45, 0.10, 0.03, 1)
    for o in T.coll.all_objects:
        if o.name not in coll.all_objects:
            pass
    STATE["at_cache"] = None

def _pose_titan(t):
    """Pose + place the Attack Titan for time t (pure: everything from at_state / ball_state)."""
    import attack_titan as AT
    T = STATE["AT"]; P = STATE["P"]
    st = at_state(t)
    on = bool(st["vis"])
    for o in STATE["at_objs"]:
        _hide(o, not on)
    if not on:
        return st, None
    mode, u = st["mode"], st["u"]
    yaw = st["yaw"]; pos = st["pos"]
    zoff = 0.0; side = 0.0
    seat = STATE["seat"]
    if mode in ("stand", "roar"):
        spec = blend(P["stand"], P["roar"], u if mode == "roar" else 0.0)
        if st["phase"]:
            spec = _walk_feet(spec, st["phase"], 1.2)
    elif mode == "smash":
        spec = blend(blend(P["stand"], P["windup"], st["u"]), P["smash"], st.get("u2", 0.0))
    elif mode == "selfpunch":
        spec = blend(blend(P["stand"], P["selfwind"], st["u"]), P["selfhit"], st.get("u2", 0.0))
    elif mode == "stagger":
        spec = _walk_feet(P["stagger"], st["phase"], 2.2, back=True)
    elif mode == "sit":
        spec = blend(P["stagger"], P["sit"], st["u"])
        zoff = -0.3 * st["u"]
    elif mode == "standup":
        uu = st["u"]
        spec = blend(P["sit"], P["crouch"], ss(0.0, 0.55, uu)) if uu < 0.55 else blend(P["crouch"], P["stand"], ss(0.55, 1.0, uu))
        zoff = -0.3 * (1 - ss(0.0, 0.4, uu))
    elif mode in ("lift", "carry", "roar_carry", "drop", "shove", "slam", "slump"):
        spec = None
    else:
        spec = P["stand"]
    bob = 0.0
    if mode == "carry":
        ph = st["phase"]; ramp = st["ramp"]
        bob = -0.4 * (math.cos(ph) ** 2) * ramp
        side = 0.6 * math.sin(ph) * ramp
        st["bob"] = bob
    holder = S3(pos[0], pos[1], G(pos[0], pos[1]) + zoff)
    rt = np.array([math.cos(yaw), math.sin(yaw), 0.0])
    holder = holder + rt * side
    if spec is None:
        c, rx, ry = ball_state(t, st, seat)
        cs = S3(c)
        c_tf = _to_tf(cs, holder, yaw)
        if mode == "lift":
            uq = ss(*BEATS["squat"], t); uc = ss(*BEATS["chest"], t); uo = ss(*BEATS["overhead"], t)
            sp = blend(blend(blend(P["stand"], P["squat"], uq), P["chest"], uc), P["carry"], uo)
            dirs = Vector((0.82, -0.5, -0.28)).lerp(Vector((0.86, -0.25, -0.1)), uc).lerp(Vector((0.8, -0.05, -0.6)), uo)
            spec = _ball_hands(sp, c_tf, dirs, (1.0, -0.3, -0.4))
        elif mode == "carry":
            sp = blend(P["carry"], P["carry_bent"], carry_bent_w(t))
            sp = dict(sp, hips=sp["hips"] + bob)
            sp = _walk_feet(sp, st["phase"], FOOT_A * st["ramp"], sway=-side, width=foot_w(st["s"]))
            spec = _ball_hands(sp, c_tf, (0.8, -0.05, -0.6), (1.0, 0.1, -0.25))
        elif mode == "roar_carry":
            sp = blend(P["carry"], P["roar_carry"], st["u"])
            spec = _ball_hands(sp, c_tf, (0.8, -0.05, -0.6), (1.0, 0.1, -0.25))
        elif mode == "drop":
            sp = blend(P["carry"], P["drop"], ss(0.0, 0.8, st["u"]))
            dirs = Vector((0.8, -0.05, -0.6)).lerp(Vector((0.75, -0.6, 0.1)), st["u"])
            spec = _ball_hands(sp, c_tf, dirs, (1.0, 0.0, -0.4))
            if st["u"] > 0.75:                           # let go as it lands
                spec = blend(spec, P["drop"], ss(0.75, 1.0, st["u"]))
        elif mode == "shove":
            sp = _walk_feet(P["shove"], st["phase"], 1.4)
            spec = _ball_hands(sp, c_tf, (0.42, -0.9, 0.05), (1.0, -0.2, -0.6))
        elif mode == "slam":                             # ONE slam: overhead -> down into the breach in ~0.4 s
            u = st["u"]
            sp = blend(P["carry"], P["slam"], ss(0.0, 0.7, u))
            dirs = Vector((0.8, -0.05, -0.6)).lerp(Vector((0.6, -0.65, 0.3)), u)
            spec = _ball_hands(sp, c_tf, dirs, (1.0, 0.0, -0.4))
            if u > 0.7:
                spec = blend(spec, P["slam"], ss(0.7, 1.0, u))
        else:                                            # slump on the jammed ball
            sp = blend(P["slam"], P["slump"], st["u"])
            spec = _ball_hands(sp, c_tf, (0.55, -0.82, 0.2), (1.0, -0.2, -0.6))
    AT.POSES["_g8"] = spec
    T.pose("_g8", ground=False)
    T.holder.location = Vector(holder)
    T.holder.rotation_euler = (0.0, 0.0, yaw + math.pi)
    s = st["scale"]; T.holder.scale = (s, s, s)
    T.eyes(st["eyes"])
    T.burning(st["burn"])
    bpy.context.view_layer.update()
    if os.environ.get("G8_DEBUG"):
        import attack_titan as AT_
        mn, mx = AT_._bbox(T.meshes, step=7)
        print(f"[g8] DEBUG t={t:.2f} mode={mode} holder={tuple(round(c, 1) for c in T.holder.matrix_world.translation)} "
              f"scale={tuple(round(c, 2) for c in T.holder.matrix_world.to_scale())} skroot.scale={tuple(round(c, 3) for c in T.skroot.scale)} "
              f"bbox min={tuple(round(c, 1) for c in mn)} max={tuple(round(c, 1) for c in mx)} hidden={[o.hide_render for o in STATE['at_objs']][:4]}")
    return st, holder

def _walk_feet(spec, phase, amp, back=False, sway=0.0, width=None):
    """Feet targets for a stepping gait: phase pi per step; stance foot slides back, swing foot lifts and goes forward."""
    import attack_titan as AT
    out = dict(spec)
    sg = -1.0 if back else 1.0
    fr = -amp * math.cos(phase) * sg; fl = amp * math.cos(phase) * sg
    lr = 0.9 * max(0.0, math.sin(phase)); ll = 0.9 * max(0.0, -math.sin(phase))
    fe = spec["feet"]
    dw = 0.0 if width is None else width - FOOT_W
    out["feet"] = {"R": (fe["R"][0] + AT.V(sway + dw, fr, lr), fe["R"][1]), "L": (fe["L"][0] + AT.V(sway - dw, fl, ll), fe["L"][1])}
    return out

def foot_plants():
    """(t, M (x, y), side) of every foot plant during the carry (pure)."""
    out = []
    s0, s1 = 0.0, ROUTE_LEN
    k = 1
    while k * STEP_L < s1 - 1.0:
        s = k * STEP_L
        t = route_t_of_s(s)
        p = route_xy(s); yaw = route_yaw(s)
        rt = np.array([math.cos(yaw), math.sin(yaw)]); fw = np.array([-math.sin(yaw), math.cos(yaw)])
        sd = 1.0 if k % 2 == 1 else -1.0                    # odd plants: right foot lands forward
        out.append((t, p + rt * foot_w(s) * sd + fw * FOOT_A * 0.8, sd))
        k += 1
    return out

# ====================================================================== pure titans (trost_action.Titans with g8 events)
class _TSite:
    def g(self, p):
        return G(p[0], p[1] + segtime.SET_OFF_Y)

def make_titans_class():
    import trost_action as TA
    import odm

    class Titans8(TA.Titans):
        """Adds g8 events on top of trost_action.Titans: corpses that stay and shrink to 0.85 (keep), a trip into a trench
        (stays lying), a crouch, a raised clawing hand, a static lying titan, hide-after times."""
        def poses(self, t):
            if self._cache_t == t:
                return self._cache
            R = super().poses(t)
            Ar, Ae, lean, vis, yaw, pos, pitch = R
            for j, sp in enumerate(self.specs):
                x = sp.get("g8")
                if not x:
                    continue
                a, b = self.show[j]
                if not (a <= t < b):
                    continue
                d = self.ev[j]["death"]
                if d is not None and x.get("keep") and t >= d[0]:
                    vis[j] = 1.0 - 0.15 * ss(d[0] + 2.0, d[0] + 25.0, t)
                    if t >= x.get("gone", 1e9):
                        vis[j] = 0.0
                if x.get("trip") is not None and t >= x["trip"]:
                    u = ss(x["trip"], x["trip"] + 0.8, t)
                    pitch[j] = -(math.pi / 2 - 0.15) * u; pos[j, 2] -= x.get("drop", 5.0) * u
                    Ar[j, 3] = Ar[j, 4] = 1.2 * u + 0.2 * math.sin(t * 2 + j) * u
                if x.get("lying"):
                    pitch[j] = -(math.pi / 2 - 0.1); pos[j, 2] -= x.get("drop", 0.0)
                    Ar[j, 3] = 0.6; Ar[j, 4] = 1.6 + 0.1 * math.sin(t * 0.8)
                if x.get("crouch") is not None and (d is None or t < d[0]) and t >= x["crouch"]:
                    u = ss(x["crouch"], x["crouch"] + 0.8, t)
                    lean[j] = -0.75 * u; pos[j, 2] -= 0.22 * self.H[j] * u; Ar[j, 3] = Ar[j, 4] = 0.7 * u
                if x.get("claw") is not None and t >= x["claw"]:
                    u = ss(x["claw"], x["claw"] + 1.0, t)
                    Ar[j, 4] = 2.4 * u + 0.25 * math.sin(t * 1.7) * u; Ae[j, 5] = 0.5 * u
                if x.get("hands_up") is not None and t >= x["hands_up"] and (d is None or t < d[0]):
                    u = ss(x["hands_up"], x["hands_up"] + 1.5, t)
                    Ar[j, 3] = Ar[j, 4] = (2.5 + 0.25 * math.sin(t * 1.3 + j)) * u; Ae[j, 5] = Ae[j, 6] = 0.4 * u
                if x.get("pinned"):
                    Ar[j, 3] = 1.0; Ar[j, 4] = 0.9; lean[j] = -0.12
                if x.get("cling") is not None and (d is None or t < d[0]):    # v17: clinging to the wall, trying to climb
                    ph = t * 1.4 + j * 1.7
                    Ar[j, 3] = 2.75 + 0.30 * math.sin(ph); Ar[j, 4] = 2.75 - 0.30 * math.sin(ph); Ae[j, 5] = Ae[j, 6] = 0.35
                    lean[j] = -0.28; pos[j, 2] += x["cling"] * (0.85 + 0.15 * math.sin(ph * 0.5))
            self._rig = odm.deform(self.RX, Ar, Ae, lean, vis, yaw, pos, pitch, None, np.zeros(len(vis))).reshape(len(vis), 4, 3)
            return R
    return Titans8

def build_titans(coll):
    import trost_action as TA
    Titans8 = make_titans_class()
    TT = Titans8(_TSite(), seed=808)
    rnd = random.Random(808)
    STATE["TT"] = TT
    def add(name, H, keys_M, show=(-1e9, 1e9), g8=None, **sp):
        keys = [(k[0], *S3(k[1], k[2])[:2]) for k in keys_M]
        TT.add(name, H=H, keys=keys, show=show, **sp)
        TT.specs[-1]["g8"] = g8 or {}
        return name
    def kill(name, td, dirn=1, keep=True, gone=1e9):
        TT.ev[TT.j(name)]["death"] = (td, dirn)
        TT.specs[TT.j(name)].setdefault("g8", {}).update(keep=keep, gone=gone)
    def face(name, xy):
        q = S3(*xy)[:2]
        TT.specs[TT.j(name)]["face"] = (float(q[0]), float(q[1]))
    # ---- the court: a 7 m up the SW street (Ian's squad), the 12 m class from the north (Rico's squad)
    add("t7", 7.0, [(0, 214, 200), (6.0, 214, 200), (12.3, 252, 247), (99, 252, 247)], show=(0, 75), g=1.0)
    kill("t7", BEATS["t7_kill"], 1, gone=60.0)
    add("t12", 12.0, [(0, 306, 392), (7.0, 306, 392), (14.0, 300, 318), (99, 300, 318)], show=(0, 75), g=1.15, hair=1)
    kill("t12", BEATS["t12_kill"], 1, gone=60.0)
    # ---- carry escorts (12-14 mixed: 4-8 m 70 %, 9-10 m 20 %, the 12 m class above, one crawler)
    add("e_rad", 5.5, [(0, 322, 188), (17.0, 322, 188), (22.8, 293, 176), (99, 293, 176)], show=(10, 75))
    kill("e_rad", BEATS["rad_kill"], 1, gone=62.0)
    add("crawler", 6.0, [(0, 232, 152), (21.0, 232, 152), (27.4, 266, 140), (99, 266, 140)], show=(10, 75), abnormal=True, g=0.9)
    kill("crawler", BEATS["crawler_kill"], 1, gone=62.0)
    west = []
    for k, (H, g, hair, grin) in enumerate(((8.0, 1.45, None, False), (9.5, 0.85, 2, False), (6.5, 1.0, None, False), (7.0, 1.0, 3, False), (5.0, 1.1, 1, True))):
        a = (40 - 9 * k, 214 + 7 * k); m = (128 - 6 * k, 140 + 5 * k); back = (62 - 10 * k, 236 + 8 * k)
        nm = add(f"west{k}", H, [(0, *a), (24.0, *a), (BEATS["west_street"][0] + 3.5 + 0.4 * k, *m), (BEATS["west_street"][1] + 0.5, *m),
                                 (BEATS["west_street"][1] + 9.0, *back), (99, *back)], show=(15, 75), g=g, hair=hair, grin=grin)
        west.append(nm)
    kill("west1", BEATS["trainee_kill"], -1, gone=64.0)
    add("trench", 6.0, [(0, -62, 92), (28.0, -62, 92), (37.9, -14.5, 50.5), (99, -14.5, 50.5)], show=(20, 75),
        g8=dict(trip=BEATS["trench_fall"], drop=5.5))
    # ---- gate square: 5 at the pit lip (they turn to watch him, then face the plug), 1 lying in the pit, 3 entering
    lip = [("lipW", 10.0, (-27, 46), (-14, 30), dict(g=1.3), None),         # big one on the WEST
           ("thin1", 6.5, (-11, 62), (-8, 21), dict(g=0.78, al=1.15), 51.8),  # thin, centre, clawing at the plug
           ("thin2", 7.0, (9, 63), (4, 33), dict(g=0.8, al=1.1), None),       # thin, centre (Levi's first)
           ("yellow", 8.0, (26, 52), (12, 27), dict(hair=3), None),          # yellow-haired, half-crouched, EAST
           ("bald", 9.0, (30, 40), (-3, 44), dict(hair=None, g=1.1), None)]  # bald, nearer the town (Levi's second)
    for nm, H, a, b, kw, claw in lip:
        g8 = {}
        if claw: g8["claw"] = claw
        if nm == "yellow": g8["crouch"] = 52.5
        add(nm, H, [(0, *a), (BEATS["face_plug"][0], *a), (BEATS["face_plug"][1], *b), (99, *b)], show=(0, 75), g8=g8, **kw)
        TT.specs[-1]["face"] = (lambda bb: (lambda tt: tuple(S3(0, 12)[:2]) if tt > BEATS["jam"] else tuple(S3(*route_xy(route_s(min(tt, 46.9))))[:2])))(b)
    # Levi's two: thin2 (7 m) and bald (9 m) turn toward the nape group and are cut down
    k_t2 = TT.j("thin2"); TT.keys[k_t2] = [(0, *S3(9, 63)[:2]), (50.0, *S3(9, 63)[:2]), (53.5, *S3(4, 33)[:2]), (54.6, *S3(4, 33)[:2]),
                                           (56.2, *S3(3, 27)[:2]), (99, *S3(3, 27)[:2])]
    kill("thin2", BEATS["levi_cut1"], 1)
    k_b = TT.j("bald"); TT.keys[k_b] = [(0, *S3(30, 40)[:2]), (50.0, *S3(30, 40)[:2]), (53.5, *S3(-3, 44)[:2]), (54.8, *S3(-3, 44)[:2]),
                                        (56.6, *S3(-5, 33)[:2]), (99, *S3(-5, 33)[:2])]
    kill("bald", BEATS["levi_cut2"], 1)
    add("pitlying", 7.0, [(0, -4.5, 43.8), (99, -4.5, 43.8)], show=(0, 75), g8=dict(lying=True, drop=3.0))
    for k, te in enumerate(BEATS["breach_in"]):                                   # walking in through the breach from the fields
        nm = add(f"inb{k}", rnd.uniform(5, 8), [(0, 0, -90), (te - 14.0, 0, -90), (te, (k - 1) * 3, 4), (te + 6.0, -20 + 16 * k, 52 + 3 * k), (99, -20 + 16 * k, 52 + 3 * k)],
                 show=(te - 14.0, 75))
        TT.specs[-1]["face"] = (lambda tt: tuple(S3(0, 12)[:2]))
    # ---- deaths in the gate square: Mitabi's squad (two grabbed at MI), Ian at IA, the crouching titan (Mikasa)
    add("mg1", 8.5, [(0, -130, 70), (28.0, -130, 70), (39.6, -63, 25), (99, -63, 25)], show=(20, 75))
    TT.ev[-1]["grab"].append(BEATS["mitabi_grab"][0])
    add("mg2", 10.0, [(0, -150, 52), (29.0, -150, 52), (40.6, -73, 13), (99, -73, 13)], show=(20, 75), hair=0)
    TT.ev[-1]["grab"].append(BEATS["mitabi_grab"][1])
    add("iang", 11.0, [(0, -86, 104), (32.0, -86, 104), (42.8, -41, 62), (99, -41, 62)], show=(20, 75), g=1.2, hair=1)
    TT.ev[-1]["grab"].append(BEATS["ian_grab"])
    add("crouch", 11.5, [(0, 86, 66), (34.0, 86, 66), (41.6, *CROUCH), (99, *CROUCH)], show=(25, 75), g=1.25,
        g8=dict(crouch=41.6))
    TT.specs[-1]["face"] = CROUCH_FALL and tuple(S3(*CROUCH_FALL)[:2])
    kill("crouch", BEATS["crouch_kill"], 1)
    # ---- OWNER 16:53: no decoy corner D (no titan mass, no packed wall tops, no west-curve group).  The mop-up stays at the
    #      gate square: wall-top cannons round the seal shell the titans left there at night (deaths spread over the night)
    targets = ["lipW", "thin1", "yellow", "inb0", "inb1", "inb2", "mg1", "mg2", "iang", "trench", "pitlying"]
    n0, n1 = BEATS["night"]
    # owner 10/27 NEW: the titans are HERDED into the wall corner west of the seal (wall face x the west pilaster) and
    # killed there ALL AT ONCE by the massed wall-top guns (HERD_KILL); the fallen / lying ones die where they are
    def at(nm, tt):
        K = TT.keys[TT.j(nm)]
        for (ta, xa, ya), (tb, xb, yb) in zip(K, K[1:]):
            if tt <= tb:
                u = 0.0 if tb <= ta else max(0.0, (tt - ta) / (tb - ta))
                return (xa + (xb - xa) * u, ya + (yb - ya) * u)
        return K[-1][1:]
    herd = [nm for nm in targets if nm not in ("trench", "pitlying")]
    # v14 (FEEDBACK_v13 §1: the mop-up is NOT by the boulder): herded into the WEST corner of the bulge wall (angle -48 deg)
    ca, sa = math.cos(math.radians(38.0)), math.sin(math.radians(38.0))   # the open wall-foot strip, east bulge
    wx, wy = 478.0 * sa, 480.0 - 478.0 * ca
    # v17 (FEEDBACK_v15 ~3:00): no pop-in / walk-in - they are AT the wall long before the camera comes (moved there at 53.0,
    # off camera), pressed against the wall face in a line, arms up, clinging as if trying to climb it; 10 more join them
    slots = [(wx - 4.5 * sa + (k - (len(herd) - 1) / 2) * 7.5 * ca, wy + 4.5 * ca + (k - (len(herd) - 1) / 2) * 7.5 * sa)
             for k in range(len(herd))]
    h0 = 53.0
    rc = random.Random(1717)
    for nm, sl in zip(herd, slots):
        c = S3(*sl)[:2]
        TT.keys[TT.j(nm)] = [k_ for k_ in TT.keys[TT.j(nm)] if k_[0] < h0 - 0.05] + [(h0, float(c[0]), float(c[1])), (99, float(c[0]), float(c[1]))]
        TT.specs[TT.j(nm)]["face"] = tuple(S3(wx + 30 * sa, wy - 30 * ca)[:2])
        TT.specs[TT.j(nm)].setdefault("g8", {})["cling"] = rc.choice([0.0, 0.0, 1.5, 3.0])
    for k in range(10):
        off = (k - 4.5) * 7.0 + (len(herd) * 7.5 / 2 + 4.0) * (1 if k >= 5 else -1)
        sl = (wx - 4.0 * sa + off * ca, wy + 4.0 * ca + off * sa)
        nm = add(f"cling{k}", rc.choice([5.0, 7.0, 8.0, 10.0, 12.0]), [(0, *sl), (99, *sl)], show=(h0, 99), g8=dict(cling=rc.choice([0.0, 2.0, 4.0])))
        TT.specs[-1]["face"] = tuple(S3(wx + 30 * sa, wy - 30 * ca)[:2])
        targets.append(nm)
    for nm in targets:
        kill(nm, HERD_KILL + rnd.uniform(-0.12, 0.12), rnd.choice([1, -1]), keep=False)
    STATE["shell_targets"] = targets
    # ---- 2 captured titans pinned in their frames (gate square, west half)
    add("cap4", 4.0, [(0, *CT[0]), (99, *CT[0])], show=(BEATS["captured"], 99), g8=dict(pinned=True))
    TT.specs[-1]["face"] = tuple(S3(-45, 20)[:2])
    add("cap7", 7.0, [(0, *CT[1]), (99, *CT[1])], show=(BEATS["captured"], 99), g8=dict(pinned=True))
    TT.specs[-1]["face"] = tuple(S3(-35, 32)[:2])
    TT.sim(DUR + 1.0)
    TT.build(coll)
    print(f"[g8] titans: {len(TT.specs)}")

# ====================================================================== people: ODM squads (odm.Squads) + static crowds
def build_people(coll):
    import odm
    rnd = random.Random(850)
    SQ = odm.Squads("G8Squads", pscale=1.0, hook=True)          # owner 10/27: one hook per shot (fire / reel / release)
    STATE["SQ"] = SQ
    TT = STATE["TT"]
    P = lambda x, y, z: S3(x, y, z)
    def roof(x, y):
        q = perch(x, y); return S3(q[0], q[1], q[2])
    def at_xy(t):
        return at_state(t)["pos"]
    def nape_M(t):
        st = at_state(t)
        return np.array([st["pos"][0], st["pos"][1], 0.0])
    yaw_c = odm.yaw_of(np.array([-1.0, 1.0, 0.0]))
    # ---- Eren (human): ODM swing over the roofs, bites his hand mid-air at 4.45
    er = SQ.flyer("eren", "cadet", "brown", accent=(0.04, 0.8, 0.32), cloak=(0.13, 0.19, 0.07))
    p0 = roof(198, 352); p1 = roof(232, 322); p2 = P(BERSERK[0] + 2, BERSERK[1] + 6, 24.0)
    er.stand(0.0, 1.0, p0, yaw_c).hop(1.0, 2.6, p0, p1, apex=10).stand(2.6, 3.2, p1, yaw_c).hop(3.2, 4.45, p1, p2, apex=8).gone(4.5)
    # ---- Mikasa: Mikasa's roof, dodges the smash, the miss, the self-punch; shoulder at the stab; ahead on the carry; kills
    mk = SQ.flyer("mikasa", "cadet", "black", scarf=True)
    m0 = roof(*MIKASA_ROOF); m1 = roof(*MISS_ROOF); m2 = roof(226, 276); m3 = roof(244, 262)
    mk.stand(0.0, 5.75, m0, yaw_c).hop(5.75, 6.5, m0, m1, apex=6).stand(6.5, 6.85, m1, yaw_c)
    mk.hop(6.85, 7.6, m1, m2, apex=7).stand(7.6, 9.0, m2, yaw_c)
    mk.hop(9.0, 9.7, m2, P(BERSERK[0] - 3, BERSERK[1] - 2, 15.0), apex=4).hop(9.7, 10.5, P(BERSERK[0] - 3, BERSERK[1] - 2, 15.0), m3, apex=4)
    mk.stand(10.5, 11.6, m3, yaw_c)
    shoulder = lambda t: _nape_set(t) + np.array([1.5, -1.0, -0.6])
    mk.hop(11.6, 12.3, m3, shoulder(12.3), apex=4).follow(12.3, 15.1, shoulder, pose="crouch")
    k1 = roof(262, 236)
    mk.hop(15.1, 16.0, shoulder(15.1), k1, apex=5).stand(16.0, 19.5, k1, yaw_c)
    # ahead of him on the ground with Armin (F13 10:09.9), then the crawler (Mikasa) at 27.6
    g = lambda s, side: (lambda q: P(q[0], q[1], G(q[0], q[1]) + 0.1))(route_xy(s) + side)
    s_a = lambda t: min(ROUTE_LEN, route_s(t) + 32.0)
    mk.hop(19.5, 20.6, k1, g(s_a(20.6), np.array([-6.0, 0.0])), apex=6)
    mk.walk(20.6, 26.2, g(s_a(20.6), np.array([-6.0, 0.0])), g(s_a(26.2), np.array([-6.0, 0.0])), "run")
    cr_n = lambda t: TT.nape("crawler", t)
    mk.dive(26.8, BEATS["crawler_kill"], g(s_a(26.2), np.array([-6.0, 0.0])) + np.array([0, 0, 3.0]), cr_n)
    q0 = TT.nape("crawler", BEATS["crawler_kill"])
    q1 = roof(230, 105)
    mk.hop(BEATS["crawler_kill"], 28.9, q0, q1, apex=6).stand(28.9, 30.0, q1, yaw_c)
    pts = [roof(185, 92), roof(128, 70), perch_wall(88, 46), roof(70, 64)]
    t_ = 30.0; prev = q1
    for k, q in enumerate(pts):
        mk.hop(t_, t_ + 2.0, prev, q, apex=8); mk.stand(t_ + 2.0, t_ + 2.8, q, yaw_c); prev = q; t_ += 2.8
    cn = lambda t: TT.nape("crouch", t)
    mk.dive(42.5, BEATS["crouch_kill"], prev + np.array([0, 0, 4.0]), cn)
    q2 = P(36, 52, G(36, 52) + 0.1)
    mk.hop(BEATS["crouch_kill"], 44.6, TT.nape("crouch", BEATS["crouch_kill"]), q2, apex=6).stand(44.6, 50.3, q2, yaw_c)
    nape = lambda t: _nape_set(t)
    mk.hop(50.3, 51.2, q2, nape(51.2) + np.array([-1.2, 0.5, 0]), apex=5).follow(51.2, 75.0, lambda t: nape(t) + np.array([-1.2, 0.5, 0]), pose="kneel")
    # ---- Armin: court roof, lands on the nape 12.0, the stab 13.5, rides it until the wake; ahead on the ground; back on the nape
    ar = SQ.flyer("armin", "cadet", "blond", H=1.63)
    a0 = roof(276, 302)
    ar.stand(0.0, 11.3, a0, yaw_c, "kneel").hop(11.3, BEATS["armin_land"], a0, nape(BEATS["armin_land"]), apex=6)
    ar.follow(BEATS["armin_land"], 15.15, lambda t: nape(t) + np.array([0, 0, 0.15]), pose="kneel")
    a1 = roof(300, 236)
    ar.hop(15.15, 16.0, nape(15.15), a1, apex=5).stand(16.0, 19.6, a1, yaw_c)
    ar.hop(19.6, 20.8, a1, g(s_a(20.8), np.array([5.0, 0.0])), apex=6)
    t_ = 20.8
    while t_ < 44.5:                                       # runs ahead across the open ground (F13 10:17.7)
        t2 = min(44.5, t_ + 3.0)
        ar.walk(t_, t2, g(s_a(t_), np.array([5.0, 0.0])), g(s_a(t2), np.array([5.0, 0.0])), "run"); t_ = t2
    q3 = P(14, 46, G(14, 46) + 0.1)
    ar.walk(44.5, 46.0, g(s_a(44.5), np.array([5.0, 0.0])), q3, "run").stand(46.0, 50.6, q3, yaw_c)
    ar.hop(50.6, 51.6, q3, nape(51.6) + np.array([1.0, 0.3, 0]), apex=4).follow(51.6, 75.0, lambda t: nape(t) + np.array([1.0, 0.3, 0]), pose="kneel")
    # Eren (human) cut out of the nape (52-60), laid on the slumped titan's back
    er2 = SQ.flyer("eren_out", "cadet", "brown", accent=(0.04, 0.8, 0.32), cloak=(0.13, 0.19, 0.07), gear=False)
    er2.follow(57.0, 59.0, lambda t: nape(t) + np.array([0, 0, -1.0 + 1.0 * ss(57.0, 58.6, t)]), pose="flail")
    er2.follow(59.0, 75.0, lambda t: nape(59.0) + np.array([0.0, 1.2, 0.2]), pose="lie")
    # ---- Rico: GREEN from GF (3.0), drops to the court roofs, RED from RF (8.0), rear guard, YELLOW from YF (53.0)
    ri = SQ.flyer("rico", "garrison", "grey")
    gf = P(*GF); rf = P(*RF); yf = P(YF[0], YF[1], G(YF[0], YF[1]) + YF[2])
    ri.stand(0.0, 3.6, gf, odm.yaw_of(np.array([0, 1.0, 0])), "aim").hop(3.6, 5.6, gf, rf, apex=14).stand(5.6, 19.4, rf, yaw_c, "stand")
    behind = lambda t: max(0.0, route_s(t) - 48.0)
    prev = rf; t_ = 19.4
    while t_ < 46.0:
        q = route_xy(behind(t_ + 2.2)); qq = perch(q[0] + 14, q[1] + 12)
        nq = S3(*qq)
        ri.hop(t_, t_ + 1.3, prev, nq, apex=7).stand(t_ + 1.3, t_ + 2.4, nq, yaw_c, "crouch"); prev = nq; t_ += 2.4
    deck = P(RICO_DECK[0], RICO_DECK[1], G(*RICO_DECK) + 0.1)          # AUDIT 7: on the deck east of the push gap for the slump,
    ri.hop(t_, 48.6, prev, deck, apex=10).stand(48.6, 51.8, deck, odm.yaw_of(np.array([-0.4, -1.0, 0])), "stand")   # then the
    ri.hop(51.8, 52.5, deck, yf, apex=4).stand(52.5, BEATS["yellow"] + 0.6, yf, odm.yaw_of(np.array([0, -1.0, 0])), "aim")  # east box
    ri.stand(BEATS["yellow"] + 0.6, 75.0, yf, odm.yaw_of(np.array([0, -1.0, 0])), "stand")
    # ---- the elite squads: Ian (ahead), Rico's (rear; the 12 m class), Mitabi (to the gate square first)
    ian = [SQ.flyer(n, "garrison", h) for n, h in (("ian", "dark"), ("i1", "brown"), ("i2", "ash"), ("i3", "black"))]
    ric = [SQ.flyer(n, "garrison", h) for n, h in (("r1", "brown"), ("r2", "dark"), ("r3", "auburn"))]
    mit = [SQ.flyer(n, "garrison", h) for n, h in (("mitabi", "brown"), ("m1", "dark"), ("m2", "ash"), ("m3", "black"))]
    starts_i = [roof(236, 270), roof(232, 252), roof(244, 240), roof(222, 284)]
    starts_r = [roof(300, 318), roof(318, 292), roof(286, 320)]
    starts_m = [roof(320, 262), roof(322, 248), roof(312, 230), roof(326, 274)]
    # Ian's squad: i1 kills the 7 m (12.6); then 40-80 m AHEAD over the roofs; i2 kills e_rad (23.0); Ian drops into GS
    for k, f in enumerate(ian):
        f.stand(0.0, 2.0 + 0.4 * k, starts_i[k], yaw_c)
    ian[1].hop(2.4, 3.6, starts_i[1], roof(240, 238), apex=6).stand(3.6, 11.8, roof(240, 238), yaw_c, "crouch")
    ian[1].dive(11.8, BEATS["t7_kill"], roof(240, 238), lambda t: TT.nape("t7", t))
    ian[1].hop(BEATS["t7_kill"], 13.8, TT.nape("t7", BEATS["t7_kill"]), roof(250, 226), apex=5).stand(13.8, 19.5, roof(250, 226), yaw_c)
    for k, f in enumerate(ian):
        prev = f.end_pos(); t_ = max(19.5, f.t_end()) + 0.2 * k
        while t_ < 41.0:
            if k == 2 and t_ < BEATS["rad_kill"] < t_ + 2.6:
                f.dive(t_, BEATS["rad_kill"], prev + np.array([0, 0, 4.0]), lambda t: TT.nape("e_rad", t))
                prev = TT.nape("e_rad", BEATS["rad_kill"]); t_ = BEATS["rad_kill"]; continue
            q = route_xy(min(ROUTE_LEN, route_s(t_ + 2.5) + 55.0 + 8 * k)); qq = perch(q[0] - 10 + 6 * k, q[1] + 16 - 4 * k)
            nq = S3(*qq)
            f.hop(t_, t_ + 1.4, prev, nq, apex=7).stand(t_ + 1.4, t_ + 2.6, nq, yaw_c, "crouch"); prev = nq; t_ += 2.6
        if f.name == "ian":
            ia = P(IA[0], IA[1], G(*IA) + 0.1)
            f.hop(t_, 42.6, prev, ia, apex=6).stand(42.6, BEATS["ian_grab"] + 0.7, ia, yaw_c, "stand")
            f.follow(BEATS["ian_grab"] + 0.7, BEATS["ian_grab"] + 2.4, lambda t: TT.hand("iang", t), pose="flail").gone(BEATS["ian_grab"] + 2.4)
        else:
            gp = P(-30 + 22 * k, 70 - 6 * k, G(-30 + 22 * k, 70 - 6 * k) + 0.1)
            f.hop(t_, t_ + 1.6, prev, gp, apex=6).stand(t_ + 1.6, 75.0, gp, yaw_c, "stand")
    # Rico's squad: r2 kills the 12 m class (14.2); then behind
    for k, f in enumerate(ric):
        f.stand(0.0, 2.0, starts_r[k], yaw_c)
    ric[1].stand(2.0, 13.3, starts_r[1], yaw_c, "crouch").dive(13.3, BEATS["t12_kill"], starts_r[1], lambda t: TT.nape("t12", t))
    ric[1].hop(BEATS["t12_kill"], 15.6, TT.nape("t12", BEATS["t12_kill"]), roof(296, 300), apex=5).stand(15.6, 19.8, roof(296, 300), yaw_c)
    for k, f in enumerate(ric):
        prev = f.end_pos(); t_ = max(19.8, f.t_end()) + 0.3 * k
        while t_ < 47.0:
            q = route_xy(max(0.0, route_s(t_ + 2.0) - 40.0 - 8 * k)); qq = perch(q[0] + 12 - 6 * k, q[1] + 18 + 4 * k)
            nq = S3(*qq)
            f.hop(t_, t_ + 1.3, prev, nq, apex=7).stand(t_ + 1.3, t_ + 2.5, nq, yaw_c, "crouch"); prev = nq; t_ += 2.5
        gp = P(-40 + 30 * k, 76, G(-40 + 30 * k, 76) + 0.1)
        f.hop(t_, t_ + 1.5, prev, gp, apex=6).stand(t_ + 1.5, 75.0, gp, yaw_c, "stand")
    # Mitabi's squad: to the gate square ahead (wall tops), lures the lip titans west along the wall foot; 2 grabbed at MI
    for k, f in enumerate(mit):
        f.stand(0.0, 18.5 + 0.3 * k, starts_m[k], yaw_c)
        prev = starts_m[k]; t_ = 18.5 + 0.3 * k
        for q in ((300, 150), (210, 72), (110, 38), (40, 48 + 4 * k)):
            qq = perch(q[0] - 4 * k, q[1] + 3 * k); nq = S3(*qq)
            f.hop(t_, t_ + 2.4, prev, nq, apex=10).stand(t_ + 2.4, t_ + 3.6, nq, yaw_c, "crouch"); prev = nq; t_ += 3.6
        lure = P(-48 - 8 * k, 30 + 3 * k, G(-48 - 8 * k, 30 + 3 * k) + 0.1)
        f.hop(t_, t_ + 1.4, prev, lure, apex=5).stand(t_ + 1.4, 36.0, lure, yaw_c, "stand")
        mi_pt = P(MI[0] + 4 * (k - 1.5), MI[1] + 2 * (k % 2), G(*MI) + 0.1)
        f.walk(36.0, 39.6, lure, mi_pt, "run")
        if f.name in ("m1", "mitabi"):
            tg = BEATS["mitabi_grab"][0 if f.name == "m1" else 1]; gn = "mg1" if f.name == "m1" else "mg2"
            f.stand(39.6, tg + 0.7, mi_pt, yaw_c, "stand")
            f.follow(tg + 0.7, tg + 2.4, (lambda gn: lambda t: TT.hand(gn, t))(gn), pose="flail").gone(tg + 2.4)
        else:
            f.stand(39.6, 75.0, mi_pt, yaw_c, "stand")
    # ---- trainees (Jean, Connie, Annie + 3): roof ridge 60 m north of the court; on foot near (150, 120) luring titans
    tr = [SQ.flyer(n, "cadet", h) for n, h in (("jean", "jean"), ("connie", "grey"), ("annie", "blond"), ("c1", "brown"), ("c2", "dark"), ("c3", "auburn"))]
    for k, f in enumerate(tr):
        r0 = roof(270 + 8 * k, 322); f.stand(0.0, 24.0 + 0.3 * k, r0, odm.yaw_of(np.array([0, -1.0, 0])))
        gp = P(150 + 4 * (k % 3), 122 + 5 * (k // 3), G(150, 122) + 0.1)
        f.hop(24.0 + 0.3 * k, 27.5 + 0.3 * k, r0, roof(210, 210), apex=14).stand(27.5 + 0.3 * k, 28.2 + 0.3 * k, roof(210, 210), yaw_c)
        f.hop(28.2 + 0.3 * k, 30.5, roof(210, 210), gp, apex=10)
        side_st = P(96 - 6 * k, 168 + 4 * k, G(96, 168) + 0.1)
        f.stand(30.5, BEATS["west_street"][0] + 3.0, gp, odm.yaw_of(np.array([-1.0, 0.6, 0])), "stand")
        f.walk(BEATS["west_street"][0] + 3.0, BEATS["west_street"][1], gp, side_st, "run")
        if f.name == "jean":
            f.dive(BEATS["trainee_kill"] - 0.9, BEATS["trainee_kill"], side_st + np.array([0, 0, 5.0]), lambda t: TT.nape("west1", t))
            f.hop(BEATS["trainee_kill"], 36.6, TT.nape("west1", BEATS["trainee_kill"]), side_st, apex=4)
        f.stand(BEATS["west_street"][1], 75.0, side_st, odm.yaw_of(np.array([1.0, -0.6, 0])), "stand")
    # ---- Levi: the outer wall top at LV, the drop (55.5), two cuts (56.3, 56.7), stands on the second corpse (57.5)
    lv = SQ.flyer("levi", "scout", "black", H=1.6, cravat=True)
    lv0 = P(*LV)
    lv.stand(52.0, BEATS["levi_drop"], lv0, odm.yaw_of(np.array([0, 1.0, 0])))
    lv.dive(BEATS["levi_drop"], BEATS["levi_cut1"], lv0, lambda t: TT.nape("thin2", t))
    lv.spin(BEATS["levi_cut1"], BEATS["levi_cut2"], lambda t: TT.nape("bald", t), 5.0, 2.0, 0.2, turns=1.5)
    lv.follow(BEATS["levi_cut2"], 75.0, lambda t: TT.crown("bald", min(t, BEATS["levi_stand"])) + np.array([0, 0, 0.1]),
              yaw_fn=lambda t: 0.4, pose="stand")
    # ---- Survey Corps pairs zip over the district on day 2 (mop-up)
    for k in range(20):
        a0_ = (rnd.uniform(-420, 300), rnd.uniform(420, 860)); pts_ = [a0_]
        for _ in range(3):
            pts_.append((pts_[-1][0] + rnd.uniform(-160, 60), pts_[-1][1] + rnd.uniform(-120, 80)))
        for q in range(2):
            f = SQ.flyer(f"sc{k}_{q}", "scout", rnd.choice(["dark", "brown", "blond", "black", "ash"]))
            t_ = BEATS["survey"][0] + rnd.uniform(0, 0.8); prev = None
            for (x, y) in pts_:
                qq = perch(min(460, max(-460, x)) + q * 4, min(860, max(80, y)) + q * 3); nq = S3(*qq)
                if prev is None:
                    f.stand(t_ - 0.01, t_, nq, 0.0); prev = nq; continue
                f.hop(t_, t_ + 1.1, prev, nq, apex=12); prev = nq; t_ += 1.1
            f.stand(t_, BEATS["survey"][1], prev, 0.0).gone(BEATS["survey"][1])
    SQ.build(coll)
    STATE["at_nape_people"] = True
    print(f"[g8] flyers: {len(SQ.flyers)}")

def perch_wall(x, y):
    q = perch(x, y)
    return S3(*q)

def _nape_set(t):
    """Nape of the Attack Titan (set coords), pure in t (analytic: from at_state, not the posed rig)."""
    st = at_state(t)
    yaw = st["yaw"]; p = st["pos"]
    fw = np.array([-math.sin(yaw), math.cos(yaw)])
    mode = st["mode"]
    g = G(p[0], p[1])
    if mode == "sit":
        u = st["u"]; h = 12.6 + (8.2 - 12.6) * u; back = -1.0 - 1.5 * u
    elif mode == "standup":
        h = 8.2 + 4.4 * st["u"]; back = -2.5 + 1.5 * st["u"]
    elif mode in ("slump",):
        h = 9.5 - 2.0 * st["u"]; back = 1.2 + 1.8 * st["u"]
    elif mode in ("shove", "drop", "slam"):
        h = 9.5; back = 1.0
    else:
        h = 12.6; back = -1.0
    q = p + fw * back
    return S3(q[0], q[1], g + h * st["scale"])

def build_crowds():
    import people_kit as PK
    rnd = random.Random(31)
    out = []
    z = 50.3
    # Pyxis + Anka + officers on the Rose top at PY (the yellow signal is confirmed there)
    pc = S3(*PY)
    for k, (pre, dx) in enumerate((("pixis", 0.0), ("garrison:2", 1.4), ("garrison:4", -1.4), ("garrison:1", 2.8), ("garrison:6", -2.8), ("garrison:3", 4.2))):
        e = PK.person(pre, (pc[0] + dx, pc[1] - 3.0, 50.3), yaw=math.pi, pose="stand"); out.append(e)
    STATE["pyxis"] = (pc[0], pc[1] - 3.0, 52.0)
    # cleanup workers (white face cloths are below one pixel; the rows and pyres carry the beat): appear at 66
    workers = []
    for k in range(64):
        s = rnd.random()
        if k < 40:
            y = 120 + 280 * s; x = _av_x(y) + rnd.choice([-1, 1]) * rnd.uniform(4, 9)
        else:
            a = rnd.uniform(0.2, 2.9); x, y = 76 * math.cos(a), 76 * math.sin(a) + 5
        p = S3(x, y)
        e = PK.person(rnd.choice(["civilian", "garrison", "civilian:3", "garrison:5"]), (p[0], p[1]), yaw=rnd.uniform(0, math.tau),
                      pose=rnd.choice(["stand", "walk"]))
        workers.append(e)
    STATE["workers"] = workers
    STATE["crowd"] = out
    print(f"[g8] people_kit instances: {len(out) + len(workers)}")

def _av_x(y):
    """Main avenue AV centreline X at M y (polyline (0, 78) -> (-15, 300) -> (-60, 470))."""
    if y < 78: return 0.0
    if y < 300: return -15.0 * (y - 78) / 222.0
    return -15.0 - 45.0 * min(1.0, (y - 300) / 170.0)

# ====================================================================== FX: flares, transformation, steam, dust, seal, glow, plug
def build_flares(coll):
    import flares as FX
    class Flares8(FX.FlareSet):
        BURN = 2.6
        TOP_HOLD = 1.3
    FL = Flares8("G8Flares", coll, style="column")       # v4 (QA batch1): rising smoke columns with a bright head, not laser lines
    # v14 (FEEDBACK_v13 §1): no green flare before the red one (not in the story); the RED one lingers like the later green
    FL.add(BEATS["red"], S3(RF[0], RF[1], RF[2] + 1.6), "red", up=200.0, lean=(-2, 2), seed=12, life=60.0, width=2.1)
    yz = G(YF[0], YF[1]) + YF[2] + 1.6
    # owner 10/27: the flare after the plug is clearly GREEN (was yellow), relay too, a bit wider
    FL.add(BEATS["yellow"], S3(YF[0], YF[1], yz), "green_vivid", up=200.0, lean=(2, -1), seed=13, life=25.0, width=2.1)
    FL.add(BEATS["relay"], S3(PY[0], PY[1], PY[2] + 1.6), "green_vivid", up=170.0, lean=(1, 1), seed=14, life=20.0, width=1.4)
    FL.build(coll)
    STATE["FL"] = FL

def build_cards(coll):
    """Every smoke / steam / dust / fire card of the segment, precomputed in time (pure)."""
    import smokecards as SC
    rng = np.random.default_rng(88)
    C = SC.SmokeCards("G8Cards")
    W = np.array([2.2, 0.8, 0.0])                         # wind (east-north-east drift)
    # red flare shock ring (white) at the muzzle
    rp = S3(RF[0], RF[1], RF[2] + 2.0); n = 18; a = np.linspace(0, math.tau, n, endpoint=False)
    C.add_many(BEATS["red"] + 0.02 + rng.random(n) * 0.04, np.tile(rp, (n, 1)), np.column_stack([np.cos(a) * 11, np.sin(a) * 11, rng.normal(0, 1, n)]),
               r0=0.5, r1=2.6, life=3.2, rise=0.3, kind="steam", alpha=0.85, tau=0.5)
    # transformation: steam + brown dust dome 40 m wide rising to 60 m, drifting east
    tb = BEATS["transform"]; c0 = S3(BERSERK[0], BERSERK[1], G(*BERSERK) + 4.0)
    n = 50; th = rng.uniform(0, math.tau, n); rr = rng.uniform(0, 1, n) ** 0.5
    pos = c0 + np.column_stack([np.cos(th) * rr * 6, np.sin(th) * rr * 6, rng.uniform(0, 8, n)])
    vel = np.column_stack([np.cos(th) * 18 * rr, np.sin(th) * 18 * rr, rng.uniform(8, 18, n)]) + W * 4
    C.add_many(tb + rng.random(n) * 0.4, pos, vel, r0=4.0, r1=rng.uniform(9, 14, n), life=rng.uniform(2.6, 4.0, n), rise=9.0, kind="dust",
               alpha=0.55, tau=1.0, color=hexrgb("#9c8a72"))
    n = 40
    pos = c0 + np.column_stack([rng.normal(0, 4, n), rng.normal(0, 4, n), rng.uniform(4, 20, n)])
    C.add_many(tb + 0.1 + rng.random(n) * 1.0, pos, np.column_stack([rng.normal(0, 5, n), rng.normal(0, 5, n), rng.uniform(12, 22, n)]) + W * 3,
               r0=4.0, r1=rng.uniform(9, 14, n), life=rng.uniform(2.6, 4.2, n), rise=10.0, kind="steam", alpha=0.6, tau=1.2)
    # roof smash bursts (tiles + dust) at 6.0 and 7.0
    for te, xy in ((BEATS["smash"], MIKASA_ROOF), (BEATS["miss"], MISS_ROOF)):
        q = perch(*xy); p = S3(*q); n = 40
        C.add_many(te + rng.random(n) * 0.25, np.tile(p, (n, 1)) + rng.normal(0, 2, (n, 3)),
                   np.column_stack([rng.normal(0, 8, n), rng.normal(0, 8, n), rng.uniform(3, 11, n)]), r0=2.0, r1=rng.uniform(5.0, 9.0, n),
                   life=rng.uniform(1.2, 2.2, n), rise=1.5, kind="dust", alpha=0.65, tau=0.6, color=hexrgb("#a0634a"))
    # titan body steam (pure in t): around the shoulders / back, 20 per second while carrying, heavier after the seal
    ts = np.arange(5.4, DUR, 0.05)
    keep = [t for t in ts if (t < 19 and rng.random() < 0.25) or (19 <= t < 47 and rng.random() < 0.8) or (t >= 47 and rng.random() < (0.7 if t < 60 else 0.35))]
    P_ = []
    for t in keep:
        st = at_state(t); p = st["pos"]
        z = 12.0 if st["mode"] not in ("sit", "slump") else 8.0
        fw = np.array([-math.sin(st["yaw"]), math.cos(st["yaw"]), 0.0])
        q = S3(p[0], p[1], G(*p) + z) - fw * 1.5 + np.array([rng.normal(0, 1.6), rng.normal(0, 1.6), rng.normal(0, 2.0)])
        P_.append(q)
    n = len(keep)
    C.add_many(np.array(keep), np.array(P_), np.column_stack([rng.normal(0, 1.2, n), rng.normal(0, 1.2, n), rng.uniform(3, 6, n)]),
               r0=1.2, r1=rng.uniform(3.0, 5.5, n), life=rng.uniform(1.8, 2.8, n), rise=4.0, kind="steam", alpha=0.3, tau=0.8)
    # ball steam ribbons (the anime's flame-like steam off the boulder): from the upper surface while carried
    seat = STATE["seat"]
    ts = np.arange(17.4, 56.0, 0.07)
    P_, V_ = [], []
    for t in ts:
        c, _, _ = ball_state(t, None, seat)
        d = rng.normal(0, 1, 3); d[2] = abs(d[2]) + 1.2; d /= np.linalg.norm(d)
        P_.append(S3(c) + d * BALL_R * 0.95); V_.append(d * 3.0 + np.array([0, 0, 3.0]))
    n = len(ts)
    C.add_many(ts, np.array(P_), np.array(V_), r0=0.7, r1=rng.uniform(2.2, 3.6, n), life=rng.uniform(1.3, 2.1, n), rise=5.0, kind="steam",
               alpha=0.48, tau=0.7)
    # bursts: self-punch, sit dust, stab puff, wake surge, roar, seal
    def burst(te, p, n, kind, r1, life, alpha, sp, up, col=None, rise=2.0):
        C.add_many(te + rng.random(n) * 0.35, np.tile(p, (n, 1)) + rng.normal(0, 1.5, (n, 3)),
                   np.column_stack([rng.normal(0, sp, n), rng.normal(0, sp, n), rng.uniform(0.3, 1.0, n) * up]),
                   r0=1.5, r1=r1 * rng.uniform(0.7, 1.2, n), life=life * rng.uniform(0.7, 1.2, n), rise=rise, kind=kind, alpha=alpha, tau=0.7,
                   color=col)
    sp_ = at_state(BEATS["selfpunch"])["pos"]
    burst(BEATS["selfpunch"], S3(sp_[0], sp_[1], 13.5), 40, "steam", 8.0, 2.8, 0.75, 7, 7)
    burst(BEATS["sit"][1] - 0.1, S3(SIT[0], SIT[1], 1.5), 26, "dust", 7.0, 2.6, 0.6, 9, 3, hexrgb("#9c8a72"))
    burst(BEATS["stab"], _nape_set(BEATS["stab"]), 16, "steam", 3.0, 1.6, 0.8, 3, 5)
    burst(BEATS["wake"], S3(SIT[0], SIT[1], 7.0), 60, "steam", 9.0, 3.5, 0.65, 7, 10)
    for k in range(3):
        burst(16.6 + 0.4 * k, S3(B0[0], B0[1], 2.0), 10, "dust", 6.0, 2.5, 0.55, 6, 2, hexrgb("#9c8a72"))     # rubble skirt spills
    r6 = ROUTE[-1]
    burst(BEATS["roar2"][0] + 0.2, S3(r6[0], r6[1], 14.0), 60, "steam", 9.0, 3.4, 0.7, 8, 9)
    # footfall dust puffs (6 cards, r 6 m, 1.5 s) + crack decals (mesh, see build_decals)
    for (te, xy, sd) in foot_plants():
        p = S3(xy[0], xy[1], G(*xy) + 0.6)
        C.add_many(te + rng.random(6) * 0.08, np.tile(p, (6, 1)) + rng.normal(0, 0.8, (6, 3)),
                   np.column_stack([rng.normal(0, 4, 6), rng.normal(0, 4, 6), rng.uniform(0.5, 2.5, 6)]), r0=1.2, r1=rng.uniform(4.0, 6.0, 6),
                   life=rng.uniform(1.2, 1.8, 6), rise=0.6, kind="dust", alpha=0.6, tau=0.5, color=hexrgb("#9c8a72"))
    # SEAL: 40 cards out to r 30 m and up to 25 m, fading over 6 s
    j = S3(*BALL_SEAL); n = 40; th = rng.uniform(-0.2, math.pi + 0.2, n)
    C.add_many(BEATS["jam"] + rng.random(n) * 0.4, np.tile(j + np.array([0, 6.0, -4.0]), (n, 1)) + rng.normal(0, 2, (n, 3)),
               np.column_stack([np.cos(th) * rng.uniform(10, 26, n), np.sin(th) * rng.uniform(10, 26, n), rng.uniform(2, 12, n)]),
               r0=3.0, r1=rng.uniform(8, 13, n), life=rng.uniform(4.5, 6.5, n), rise=1.5, kind="dust", alpha=0.75, tau=1.0, color=hexrgb("#8a7a66"))
    # steam pouring off the slumped titan + the plug smoke
    ts = np.arange(50.0, DUR, 0.25)
    n = len(ts)
    C.add_many(ts, np.tile(S3(0, 14, 34), (n, 1)) + rng.normal(0, 2, (n, 3)), np.column_stack([rng.normal(0, 0.6, n), rng.normal(0, 0.6, n), rng.uniform(2, 4, n)]),
               r0=2.0, r1=6.0, life=5.0, rise=2.0, kind="smoke", alpha=0.25, tau=1.0)
    # blade streaks (#cfe8ff, 0.15 s) at every nape cut (stab, kills, Levi)
    TT = STATE["TT"]
    cuts = [(BEATS["stab"], _nape_set(BEATS["stab"]))]
    for nm, te in (("t7", BEATS["t7_kill"]), ("t12", BEATS["t12_kill"]), ("e_rad", BEATS["rad_kill"]), ("crawler", BEATS["crawler_kill"]),
                   ("west1", BEATS["trainee_kill"]), ("crouch", BEATS["crouch_kill"]), ("thin2", BEATS["levi_cut1"]), ("bald", BEATS["levi_cut2"])):
        cuts.append((te, TT.nape(nm, te - 0.05)))
    for te, p in cuts:
        C.add_many(te + np.array([0.0, 0.04]), np.tile(p, (2, 1)), None, r0=1.6, r1=1.8, life=0.16, rise=0.0, kind="glow", alpha=1.0,
                   color=hexrgb("#cfe8ff"), dirs=np.array([[1.0, 0.4, 0.6], [1.0, -0.5, 0.3]]), stretch=4.0, fade_in=0.01)
        C.add_many(te + 0.1 + rng.random(10) * 0.5, np.tile(p, (10, 1)) + rng.normal(0, 1, (10, 3)),
                   np.column_stack([rng.normal(0, 2, 10), rng.normal(0, 2, 10), rng.uniform(2, 5, 10)]), r0=1.0, r1=3.5, life=2.0, rise=2.5,
                   kind="steam", alpha=0.7, tau=0.5)
    # mop-up: shell bursts in the D mass (dark puffs) + muzzle smoke on the wall tops
    for ev in STATE["cannon_events"]:
        te, kind, p = ev
        if kind == "burst":
            C.add_many(te + 0.05 + rng.random(5) * 0.2, np.tile(p, (5, 1)) + rng.normal(0, 2.5, (5, 3)),
                       np.column_stack([rng.normal(0, 4, 5), rng.normal(0, 4, 5), rng.uniform(2, 6, 5)]), r0=3.0, r1=rng.uniform(9, 15, 5),
                       life=rng.uniform(2.5, 4.0, 5), rise=2.0, kind="smoke", alpha=0.6, tau=0.6, color=(0.10, 0.09, 0.08))
        else:
            C.add_many(te + 0.03 + rng.random(3) * 0.1, np.tile(p, (3, 1)) + rng.normal(0, 0.6, (3, 3)),
                       np.column_stack([rng.normal(0, 2, 3), rng.normal(0, 2, 3) - 4.0, rng.uniform(1, 3, 3)]), r0=1.0, r1=4.0,
                       life=2.4, rise=1.5, kind="smoke", alpha=0.5, tau=0.5, color=(0.42, 0.38, 0.26))
    # muzzle / burst flashes as glow cards -- owner 10/27: "remove the sparkles" (master v1 6:40 = the first night shells):
    # no glow flashes any more, the mop-up reads by its smoke puffs
    for te, kind, p in ([] if NO_SPARKLES else STATE["cannon_events"]):
        C.add_many([te], [p], None, r0=7.0 if kind == "burst" else 3.5, r1=9.0 if kind == "burst" else 4.0, life=0.16 if kind == "muzzle" else 0.24,
                   rise=0.0, kind="glow", alpha=1.0, color=hexrgb("#ffc040") if kind == "muzzle" else (1.0, 0.75, 0.45), fade_in=0.005)
    CN = SC.SmokeCards("G8CardsVideo")                    # pyres on the video clock (not warped)
    for k, (xy, te) in enumerate(zip(PYRES, PYRE_T)):
        base = S3(xy[0], xy[1], G(*xy) + 2.0)
        ts = np.arange(te, DUR, 0.05); n = len(ts)
        CN.add_many(ts, np.tile(base, (n, 1)) + np.column_stack([rng.normal(0, 1.6, n), rng.normal(0, 1.2, n), rng.uniform(0, 2.5, n)]),
                    np.column_stack([rng.normal(0, 0.5, n), rng.normal(0, 0.5, n), rng.uniform(5, 9, n)]), r0=2.8, r1=rng.uniform(4.5, 7.0, n),
                    life=rng.uniform(0.7, 1.2, n), rise=2.0, kind="fire", alpha=1.0, color=hexrgb("#ff9a2a"))
        ts = np.arange(te + 0.3, DUR, 0.15); n = len(ts)
        CN.add_many(ts, np.tile(base + np.array([0, 0, 7.0]), (n, 1)) + rng.normal(0, 1.8, (n, 3)),
                    np.column_stack([rng.normal(0, 0.8, n), rng.normal(0, 0.8, n), rng.uniform(26, 32, n)]), r0=4.0, r1=rng.uniform(18, 28, n),
                    life=rng.uniform(13, 16, n), rise=4.0, kind="smoke", alpha=0.75, tau=5.0, color=hexrgb("#2b2724"))
    CN.build(coll)
    STATE["cards_video"] = CN
    # 8 grey-brown smoke columns from burning buildings (ambient, the whole beat)
    for k in range(8):
        x, y = rng.uniform(-350, 300), rng.uniform(120, 760)
        base = S3(x, y, top_z(x, y) + 2.0); ts = np.arange(0.0, DUR, 0.5); n = len(ts)
        C.add_many(ts - 14.0, np.tile(base, (n, 1)) + rng.normal(0, 2, (n, 3)), np.column_stack([rng.normal(0, 0.6, n), rng.normal(0, 0.6, n), rng.uniform(8, 11, n)]),
                   r0=3.0, r1=rng.uniform(12, 18, n), life=15.0, rise=0.8, kind="smoke", alpha=0.35, tau=4.0, color=(0.30, 0.27, 0.24))
    C.build(coll)
    STATE["cards"] = C
    print(f"[g8] smoke cards: {C.count()}")

def build_cannon_events():
    """Mop-up cannons 'around the clock' (owner 16:53: at the gate square, no corner D): muzzle flashes on the wall top
    round the seal, shell bursts on the titans left in the gate square at night, slower fire outside by day."""
    rng = np.random.default_rng(55)
    guns = [S3(478.0 * math.sin(a), 480 - 478.0 * math.cos(a), 52.0) for a in np.radians([26, 30, 33, 36, 40, 43, 46, 50])]   # v14: massed at the corner
    TT = STATE["TT"]
    ev = []
    for nm in STATE.get("shell_targets", []):            # 2-3 shells walk onto each titan, the last one kills it
        td = TT.ev[TT.j(nm)]["death"][0]
        for q, dt in enumerate((-0.9, -0.45, 0.0)[int(rng.integers(2)):]):
            p = TT.pos(nm, td + dt - 0.35) + np.array([rng.normal(0, 2.5 if dt < 0 else 0.6), rng.normal(0, 2.5 if dt < 0 else 0.6), rng.uniform(3, 8)])
            g = guns[int(rng.integers(len(guns)))]
            ev.append((td + dt - 0.35, "muzzle", g)); ev.append((td + dt, "burst", p))
    t = BEATS["day"][0]
    while t < BEATS["day"][1]:                           # by day: slower fire from the gate guns over the fields outside
        g = guns[int(rng.integers(len(guns)))]
        ev.append((t, "muzzle", g)); ev.append((t + 0.4, "burst", S3(rng.uniform(-120, 120), rng.uniform(-260, -90), rng.uniform(3, 8))))
        t += rng.uniform(0.8, 1.6)
    ev.sort(key=lambda e: e[0])
    STATE["cannon_events"] = ev

def build_transform_fx(coll):
    """Yellow bolt (300 m, 0.15 s), white-yellow flash sphere 30 m (0.25 s), a flash light."""
    L = STATE["L"]
    rnd = random.Random(4)
    top = Vector((BERSERK[0] + 30, BERSERK[1] - 12, 300.0)); bot = Vector((BERSERK[0] + 2, BERSERK[1] + 6, 22.0))
    bm = bmesh.new()
    pts = [top]
    for k in range(1, 22):
        u = k / 21.0
        q = top.lerp(bot, u) + Vector((rnd.uniform(-9, 9), rnd.uniform(-9, 9), rnd.uniform(-4, 4))) * math.sin(math.pi * u)
        pts.append(q)
    pts[-1] = bot
    for a, b in zip(pts, pts[1:]):
        L.cyl(bm, Vector(S3(a)), Vector(S3(b)), 1.6, 1.4, seg=6)
    m, _ = emit_mat("G8_Bolt", hexrgb("#ffe14a"), 45.0)
    bolt = L.obj_from_bm("G8_Bolt", bm, [m], coll); bolt.visible_shadow = False
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=12, radius=15.0)
    fm, _ = emit_mat("G8_Flash", (1.0, 0.92, 0.6), 30.0)
    fl = L.obj_from_bm("G8_FlashSphere", bm, [fm], coll); fl.visible_shadow = False
    fl.location = SV(BERSERK[0], BERSERK[1], 16.0)
    ld = bpy.data.lights.new("G8_TransformLight", "POINT"); ld.color = (1.0, 0.82, 0.45); ld.energy = 0.0; ld.shadow_soft_size = 20
    lo = bpy.data.objects.new("G8_TransformLight", ld); lo.location = SV(BERSERK[0], BERSERK[1], 60.0); coll.objects.link(lo)
    STATE["tfx"] = (bolt, fl, ld)

def build_decals(coll):
    """Footfall crack decals (one mesh, vertices driven per frame) + Mikasa's roof hole + small dark blood decals."""
    L = STATE["L"]
    plants = foot_plants()
    n = len(plants)
    V = []; F = []
    rng = random.Random(9)
    for k, (te, xy, sd) in enumerate(plants):
        c = S3(xy[0], xy[1], G(*xy) + 0.07)
        # a jagged 6-point star crack 5 m across
        base = len(V)
        V.append(tuple(c))
        for q in range(12):
            a = q / 12 * math.tau + rng.uniform(-0.15, 0.15); r = (1.9 if q % 2 == 0 else 0.55) * rng.uniform(0.7, 1.2)
            V.append((c[0] + math.cos(a) * r, c[1] + math.sin(a) * r, c[2]))
        for q in range(12):
            F.append((base, base + 1 + q, base + 1 + (q + 1) % 12))
    me = bpy.data.meshes.new("G8_Cracks"); me.from_pydata(V, [], F); me.update()
    me.materials.append(L.mat("G8_Crack", (0.07, 0.06, 0.05), 0.95))
    ob = bpy.data.objects.new("G8_Cracks", me); coll.objects.link(ob); ob.visible_shadow = False
    STATE["cracks"] = (ob, np.array(V, float), np.array([p[0] for p in plants]))
    # Mikasa's roof caves in (10 x 8 m hole), and the second roof dented (decals appear at the hits)
    holes = []
    hits = ((BEATS["smash"], MIKASA_ROOF, 10.0, 8.0), (BEATS["miss"], MISS_ROOF, 7.0, 6.0))
    if STATE.get("roof_hook"):
        hits = hits[1:]                                  # the set has Mikasa's broken roof (set_mikasa_roof)
    for te, xy, w, d in hits:
        q = perch(*xy, search=0.0); bm = bmesh.new()
        for k in range(10):
            a = k / 10 * math.tau
            pass
        L.box(bm, (0, 0, 0), (w, d, 0.6))
        for v in bm.verts:
            v.co.x += rng.uniform(-0.8, 0.8) * (abs(v.co.x) > 1); v.co.y += rng.uniform(-0.8, 0.8) * (abs(v.co.y) > 1)
        h = L.obj_from_bm(f"G8PH_RoofHole{len(holes)}", bm, [L.mat("G8_Hole", (0.02, 0.015, 0.012), 0.95)], coll)
        h.location = SV(q[0], q[1], q[2] - 0.15); h.rotation_euler.z = Y_BERSERK; h.hide_render = True
        holes.append((te, h))
    STATE["holes"] = holes
    PLACEHOLDERS.append("G8PH_RoofHole0/1 (Mikasa's roof hole, dented roof)")
    # small dark blood decals at the grabs / kills on the ground (tasteful, 1-3 m)
    bm = bmesh.new()
    for xy in (MI, (MI[0] - 8, MI[1] - 4), IA, CROUCH_FALL, (150, 128), (266, 140), (292, 170)):
        c = S3(xy[0], xy[1], G(*xy) + 0.06)
        r = bmesh.ops.create_circle(bm, cap_ends=True, segments=10, radius=rng.uniform(0.8, 1.5))
        for v in r["verts"]:
            v.co += Vector(c)
    bl = L.obj_from_bm("G8_Blood", bm, [L.mat("G8_BloodMat", hexrgb("#5a1e1a"), 0.6)], coll); bl.visible_shadow = False
    STATE["blood"] = bl

# ====================================================================== the set pieces this beat needs (placeholders if absent)
def _has_obj(*subs):
    for o in bpy.data.objects:
        n = o.name.lower()
        if any(s.lower() in n for s in subs):
            return o
    return None

def build_set_pieces(coll):
    L = STATE["L"]; TR = STATE["TR"]
    rng = random.Random(12)
    if hasattr(TR, "set_breach"):                     # g8 is after the kick: the breach is open
        try: TR.set_breach(True)
        except Exception as ex: print("[g8] set_breach failed:", ex)
    rub = bpy.data.objects.get("OuterGateRubble")       # g8 only: the kick's rubble fan lies flatter (the ball rolls over it
    if rub is not None:                                 # into the slot; bible: fan 15 m out, chunks 0.5-2 m)
        rub.scale.z *= 0.45
        STATE["kick_rubble"] = rub; STATE["kick_rubble_z"] = rub.scale.z
    anchors = getattr(TR, "ANCHORS_M", None) or {}
    # ---- the lawn bed (octagonal, 30 m, 0.6 m kerb) + 14 dark rocks + shrubs + 2 cypress + 1 leafy tree + second rock
    if not _has_obj("LawnBed", "BoulderBed", "RockGarden"):
        bm = bmesh.new()
        r = bmesh.ops.create_circle(bm, cap_ends=True, segments=8, radius=15.0 / math.cos(math.pi / 8))
        bmesh.ops.rotate(bm, verts=r["verts"], cent=(0, 0, 0), matrix=Matrix.Rotation(math.pi / 8, 3, "Z"))
        f = bmesh.ops.extrude_face_region(bm, geom=bm.faces[:])
        for v in [e for e in f["geom"] if isinstance(e, bmesh.types.BMVert)]:
            v.co.z = 0.6
        bed = L.obj_from_bm("G8PH_LawnBed", bm, [L.mat("G8_Lawn", hexrgb("#6f8a4c"), 0.9, var=0.2, var_scale=0.3)], coll)
        bed.location = SV(B0[0], B0[1], G(*B0))
        bm = bmesh.new()                                             # stone kerb ring
        for k in range(8):
            a0 = k / 8 * math.tau + math.pi / 8; a1 = (k + 1) / 8 * math.tau + math.pi / 8
            R0 = 15.0 / math.cos(math.pi / 8)
            p0 = Vector((math.cos(a0) * R0, math.sin(a0) * R0, 0.35)); p1 = Vector((math.cos(a1) * R0, math.sin(a1) * R0, 0.35))
            mid = (p0 + p1) / 2; ln = (p1 - p0).length
            L.box(bm, mid, (ln + 0.6, 0.7, 0.7), rot=math.atan2(p1.y - p0.y, p1.x - p0.x))
        kb = L.obj_from_bm("G8PH_BedKerb", bm, [L.mat("G8_Kerb", hexrgb("#b9ab8f"), 0.85)], coll)
        kb.location = bed.location
        bm = bmesh.new()
        for k in range(14):
            a = k / 14 * math.tau + rng.uniform(-0.1, 0.1); rr = rng.uniform(12.0, 14.0); s = rng.uniform(1.0, 1.75)
            c = bmesh.ops.create_icosphere(bm, subdivisions=1, radius=s)
            for v in c["verts"]:
                v.co = Vector((v.co.x * rng.uniform(0.8, 1.3), v.co.y * rng.uniform(0.8, 1.3), v.co.z * rng.uniform(0.9, 1.4) + s * 0.6))
                v.co += Vector((math.cos(a) * rr, math.sin(a) * rr, 0.6))
        for k in range(16):                                          # rubble skirt on the bed (pale)
            a = rng.uniform(0, math.tau); rr = rng.uniform(7.5, 10.5); s = rng.uniform(0.5, 1.5)
            c = bmesh.ops.create_icosphere(bm, subdivisions=1, radius=s)
            for v in c["verts"]:
                v.co.z *= 0.7; v.co += Vector((math.cos(a) * rr, math.sin(a) * rr, 0.7))
        rk = L.obj_from_bm("G8PH_BedRocks", bm, [L.mat("G8_DarkRock", hexrgb("#4a4a48"), 0.9, var=0.2, var_scale=0.5)], coll)
        rk.location = bed.location
        bm = bmesh.new()
        for k in range(5):
            a = rng.uniform(0.6, 2.6); rr = rng.uniform(9, 12)
            c = bmesh.ops.create_icosphere(bm, subdivisions=1, radius=rng.uniform(1.2, 1.8))
            for v in c["verts"]:
                v.co += Vector((math.cos(a) * rr, math.sin(a) * rr, 1.6))
        for (dx, dy, h) in ((-10, 9, 10.0), (-7, 12, 9.0)):                          # 2 slim cypress-like trees (NW edge)
            L.cyl(bm, (dx, dy, 0.6), (dx, dy, 0.6 + h), 1.3, 0.15, seg=8)
        c = bmesh.ops.create_icosphere(bm, subdivisions=2, radius=4.0)               # 1 leafy tree
        for v in c["verts"]:
            v.co += Vector((-12.5, 5.0, 8.0))
        L.cyl(bm, (-12.5, 5.0, 0.6), (-12.5, 5.0, 5.0), 0.5, 0.4, seg=6)
        tr = L.obj_from_bm("G8PH_BedTrees", bm, [L.mat("G8_Shrub", hexrgb("#3c5a2a"), 0.9, var=0.25, var_scale=0.4)], coll)
        tr.location = bed.location
        bm = bmesh.new(); c = bmesh.ops.create_icosphere(bm, subdivisions=3, radius=3.4)
        for v in c["verts"]:
            n_ = v.co.normalized(); d = 1 + 0.18 * noise.noise(n_ * 2.0 + Vector((5, 1, 3)))
            v.co = Vector((n_.x * 3.4 * d, n_.y * 3.0 * d, n_.z * 3.4 * d + 2.8))
        sr = L.obj_from_bm("G8PH_SecondRock", bm, [STATE["ball"].data.materials[0]], coll) if not _has_obj("TrostRock2") else None
        if sr: sr.location = SV(308, 247, G(308, 247))
        PLACEHOLDERS.append("G8PH_LawnBed/BedKerb/BedRocks/BedTrees/SecondRock (Boulder Court bed at B0)")
    # ---- breach glow (orange, until the jam) - set hook if present
    STATE["glow_hook"] = getattr(TR, "set_glow", None) if bpy.data.objects.get("OuterGate_Glow") else None
    if STATE["glow_hook"] is None:
        bm = bmesh.new(); L.box(bm, (0, 0, 15.0), (15.0, 0.3, 30.0))
        gm, gs = emit_mat("G8_BreachGlow", hexrgb("#ff9a4a"), 2.2)
        g = L.obj_from_bm("G8PH_BreachGlow", bm, [gm], coll); g.location = SV(0, 4.0, G(0, 4)); g.visible_shadow = False
        ld = bpy.data.lights.new("G8_BreachLight", "SPOT"); ld.color = (1.0, 0.55, 0.25); ld.energy = 2.0e5; ld.spot_size = math.radians(70)
        lo = bpy.data.objects.new("G8_BreachLight", ld); lo.location = SV(0, 2.0, 12.0); coll.objects.link(lo)
        lo.rotation_euler = (math.radians(-80), 0, 0)
        STATE["glow"] = (g, gs, ld)
        PLACEHOLDERS.append("G8PH_BreachGlow (orange slot glow + spot light, off at the jam)")
    # ---- Λ plug: ~60 dark tendrils from the ball up to Z 38 (base 15 m) + branches over the brick - set hook if present
    STATE["plug_hook"] = getattr(TR, "set_plug", None) if bpy.data.objects.get("OuterGate_Plug") else None
    STATE["seal_hook"] = getattr(TR, "set_seal", None) if bpy.data.objects.get("OuterGate_SealRubble") else None
    STATE["roof_hook"] = getattr(TR, "set_mikasa_roof", None) if bpy.data.objects.get("TrostMikasaRoofBroken") else None
    if STATE["plug_hook"] is None:
        bm = bmesh.new()
        for k in range(60):
            x0 = rng.uniform(-7.5, 7.5); z0 = rng.uniform(4.0, 13.0)
            top = Vector((rng.uniform(-1.0, 1.0), rng.uniform(-0.5, 0.5), rng.uniform(30.0, 38.0)))
            pts = [Vector((x0, rng.uniform(-1.0, 1.5), z0))]
            for q in range(1, 7):
                u = q / 6.0
                p = pts[0].lerp(top, u) + Vector((rng.uniform(-1.2, 1.2), rng.uniform(-0.6, 0.6), 0)) * math.sin(math.pi * u)
                pts.append(p)
            for q in range(6):
                L.cyl(bm, pts[q], pts[q + 1], 0.75 * (1 - q / 7) + 0.15, 0.75 * (1 - (q + 1) / 7) + 0.12, seg=5)
            if k % 3 == 0:                                       # branches spreading 5-10 m over the brick
                a = pts[rng.randrange(2, 6)]; b = a + Vector((rng.choice([-1, 1]) * rng.uniform(5, 10), rng.uniform(0.0, 0.6), rng.uniform(-3, 5)))
                L.cyl(bm, a, b, 0.25, 0.06, seg=4)
        pm = L.mat("G8_Plug", hexrgb("#2a1f1b"), 0.95)
        pl = L.obj_from_bm("G8PH_Plug", bm, [pm], coll)
        pl.location = SV(0, 14.6, 0.0); pl.scale = (1, 1, 0.01); pl.hide_render = True
        STATE["plug"] = pl
        PLACEHOLDERS.append("G8PH_Plug (Λ tendril spire, grows 50-54)")
    # crushed-brick ring round the jammed ball + red-brick / grey rubble chunks thrown by the jam (30, baked parabolas)
    rnd = np.random.default_rng(3)
    bm = bmesh.new()
    for k in range(30):
        s = rnd.uniform(0.5, 2.0)
        r = bmesh.ops.create_icosphere(bm, subdivisions=1, radius=s)
        for v in r["verts"]:
            v.co.x *= rnd.uniform(0.7, 1.3)
    ch_all = []
    mats = [L.mat("G8_Brick", hexrgb("#8d4b3a"), 0.9), L.mat("G8_GreyRubble", hexrgb("#8e8a80"), 0.9)]
    for k in range(30):
        bmk = bmesh.new(); s = rnd.uniform(0.5, 2.0); bmesh.ops.create_icosphere(bmk, subdivisions=1, radius=s)
        for v in bmk.verts:
            v.co.x *= rnd.uniform(0.7, 1.4); v.co.z *= rnd.uniform(0.6, 1.0)
        o = L.obj_from_bm(f"G8_Chunk{k}", bmk, [mats[k % 2]], coll); o.hide_render = True
        a = rnd.uniform(-0.25, 0.45) if k % 2 else rnd.uniform(math.pi - 0.45, math.pi + 0.25)   # thrown to the sides: the
        dist = rnd.uniform(9, 26)                                                                   # ball's front stays clear
        p0 = S3(rnd.uniform(-6, 6), 15.5, rnd.uniform(2, 12)); land = S3(math.cos(a) * dist, 15 + abs(math.sin(a)) * dist, s * 0.4)
        ch_all.append(dict(ob=o, p0=p0, land=land, T=0.8 + dist / 28.0, spin=rnd.normal(0, 4, 3)))
    bm.free()
    STATE["chunks"] = ch_all
    bm = bmesh.new()
    for k in range(26):
        a = k / 26 * math.pi + rng.uniform(-0.06, 0.06); s = rng.uniform(0.4, 1.0)
        c = bmesh.ops.create_icosphere(bm, subdivisions=1, radius=s)
        for v in c["verts"]:
            v.co.z *= 0.5; v.co += Vector((math.cos(a) * 7.8, 15.0 + math.sin(a) * 1.5, 0.2))
    ring = L.obj_from_bm("G8_CrushedBrick", bm, [mats[0]], coll); ring.location = SV(0, 0, G(0, 15)); ring.location.y = SV(0, 0)[1]
    ring.hide_render = True
    STATE["ring"] = ring
    # ---- gate square props when the set has none: bollards, kick craters, small holes, ring-pit discs, spruces / bushy tree
    if not _has_obj("Bollard", "RingPit", "GatePit", "Trench"):
        bm = bmesh.new()
        for x in (-30, -25, -15, -10, 10, 15, 25):
            L.cyl(bm, (x, 30, 0), (x, 30, 1.5), 0.3, 0.3, seg=8)
        bo = L.obj_from_bm("G8PH_Bollards", bm, [L.mat("G8_Bollard", (0.13, 0.13, 0.13), 0.8)], coll); bo.location = SV(0, 0, G(0, 30))
        bo.location.y = SV(0, 0)[1]
        bm = bmesh.new()
        for (cx, cy, r) in ((-32, 20, 4.5), (34, 30, 4.5), (-34, 32, 2.0), (-30, 50, 2.0), (38, 44, 1.6)):
            c = bmesh.ops.create_circle(bm, cap_ends=True, segments=12, radius=r)
            for v in c["verts"]:
                v.co += Vector((cx, cy, 0.05))
        # the ring pit as dark C-shaped annuli (outer r 17-24, inner r 7-11), open +-45 deg toward the gate
        for (r0, r1) in ((17.0, 24.0), (7.0, 11.0)):
            a0, a1 = math.radians(-45 + 270 + 90), math.radians(225 + 90)
            segs = 28
            for q in range(segs):
                aa = math.radians(-45) + (q / segs) * math.radians(270); bb = math.radians(-45) + ((q + 1) / segs) * math.radians(270)
                # angle measured from north (+Y) clockwise is wrong; use: the gap is centred on due south (-Y)
                def pt(r, ang):
                    return Vector((PIT[0] + r * math.sin(ang + math.pi / 4 + math.pi * 0.0), PIT[1] + r * math.cos(ang + math.pi / 4), 0.05))
                vs = [bm.verts.new(pt(r0, aa)), bm.verts.new(pt(r1, aa)), bm.verts.new(pt(r1, bb)), bm.verts.new(pt(r0, bb))]
                bm.faces.new(vs)
        cr = L.obj_from_bm("G8PH_PitCraters", bm, [L.mat("G8_PitDark", hexrgb("#3b3228"), 0.95)], coll); cr.location = SV(0, 0, G(0, 36))
        cr.location.y = SV(0, 0)[1]; cr.visible_shadow = False
        bm = bmesh.new()
        for (x, y, h) in ((-34, 10, 11.0), (-40, 13, 9.0)):
            L.cyl(bm, (x, y, 0), (x, y, h), 2.4, 0.2, seg=8)
        c = bmesh.ops.create_icosphere(bm, subdivisions=2, radius=3.6)
        for v in c["verts"]:
            v.co += Vector((34, 10, 6.0))
        tr2 = L.obj_from_bm("G8PH_GateTrees", bm, [L.mat("G8_Spruce", hexrgb("#24391f"), 0.9)], coll); tr2.location = SV(0, 0, 0)
        tr2.location.y = SV(0, 0)[1]
        PLACEHOLDERS.append("G8PH_Bollards/PitCraters/GateTrees (gate-square props: bollards Y 30, craters, holes, ring pit, spruces + bushy tree)")
    # ---- the 38 m wall-foot strip (dusty open ground) along the SE curve: a ground decal when the set lacks it
    if not _has_obj("WallFootStrip", "SEStrip") and not bpy.data.collections.get("TrostStrip"):
        bm = bmesh.new()
        for q in range(30):
            a0 = math.radians(8 + (37 - 8) * q / 30); a1 = math.radians(8 + (37 - 8) * (q + 1) / 30)
            def pt(r, a):
                return Vector((r * math.sin(a), 480 - r * math.cos(a), 0.04))
            vs = [bm.verts.new(pt(437, a0)), bm.verts.new(pt(474, a0)), bm.verts.new(pt(474, a1)), bm.verts.new(pt(437, a1))]
            bm.faces.new(vs)
        ws = L.obj_from_bm("G8PH_WallFootStrip", bm, [L.mat("G8_Dust", hexrgb("#8a7a5c"), 0.95, var=0.25, var_scale=0.08, color2=hexrgb("#5f7a3e"))], coll)
        ws.location = SV(0, 0, 0); ws.location.y = SV(0, 0)[1]; ws.visible_shadow = False
        PLACEHOLDERS.append("G8PH_WallFootStrip (38 m dusty ground decal; the set must clear houses r 437..475, phi 8-37 deg)")
    # ---- captured-titan frames (12 x 8 x 10 m and 8 x 6 x 7 m, 12-16 diagonal poles + ropes): hidden until 64.8
    bm = bmesh.new()
    for (cx, cy), (w, d, h), npole in zip(CT, ((12, 8, 10), (8, 6, 7)), (16, 12)):
        for sx in (-1, 1):
            for sy in (-1, 1):
                L.cyl(bm, (cx + sx * w / 2, cy + sy * d / 2, 0), (cx + sx * w / 2, cy + sy * d / 2, h), 0.22, 0.22, seg=5)
        for sy in (-1, 1):
            L.cyl(bm, (cx - w / 2, cy + sy * d / 2, h), (cx + w / 2, cy + sy * d / 2, h), 0.2, 0.2, seg=5)
        for k in range(npole):
            a = rng.uniform(0, math.tau); r = rng.uniform(w * 0.4, w * 0.7)
            p0 = (cx + math.cos(a) * r, cy + math.sin(a) * r, 0.0)
            p1 = (cx + rng.uniform(-1.2, 1.2), cy + rng.uniform(-1.2, 1.2), h * rng.uniform(0.35, 0.8))
            L.cyl(bm, p0, p1, 0.13, 0.12, seg=4)
    fr = L.obj_from_bm("G8PH_CaptureFrames", bm, [L.mat("G8_Timber", hexrgb("#6b4a2e"), 0.85)], coll)
    fr.location = SV(0, 0, G(*CT[0])); fr.location.y = SV(0, 0)[1]; fr.hide_render = True
    STATE["frames"] = fr
    PLACEHOLDERS.append("G8PH_CaptureFrames (2 timber pole frames at CT)")
    cp = None                                            # OWNER 16:53: no cranes / hoist at D
    # ---- covered bodies in rows (AV kerbs Y 120..400 + the GS ring road), 4 batches; pyre log stacks
    batches = [bmesh.new() for _ in range(4)]
    k = 0
    for y in np.arange(122, 400, 3.0):
        for sd in (-1, 1):
            x = _av_x(y) + sd * 8.0
            b = batches[min(3, int((y - 120) / 70))]
            L.box(b, (x, y, G(x, y) + 0.18), (0.62, 2.0, 0.36)); k += 1
    for a in np.linspace(0.25, 2.9, 40):
        x, y = 74 * math.cos(a), 74 * math.sin(a) + 3
        L.box(batches[3], (x, y, G(x, y) + 0.18), (2.0, 0.62, 0.36), rot=a); k += 1
    cm = L.mat("G8_Shroud", hexrgb("#4b4038"), 0.95)
    rows = []
    for q, b in enumerate(batches):
        o = L.obj_from_bm(f"G8_BodyRows{q}", b, [cm], coll); o.location = SV(0, 0, 0); o.location.y = SV(0, 0)[1]; o.hide_render = True
        rows.append(o)
    STATE["rows"] = rows
    bm = bmesh.new()
    for (x, y) in PYRES:
        z = G(x, y)
        for lay in range(4):
            for q in range(-2, 3):
                if lay % 2 == 0:
                    L.box(bm, (x, y + q * 0.95, z + 0.3 + lay * 0.5), (6.0, 0.5, 0.45))
                else:
                    L.box(bm, (x + q * 1.4, y, z + 0.3 + lay * 0.5), (0.5, 4.0, 0.45))
    py = L.obj_from_bm("G8_PyreLogs", bm, [L.mat("G8_Logs", (0.18, 0.09, 0.04), 0.9)], coll)
    py.location = SV(0, 0, 0); py.location.y = SV(0, 0)[1]; py.hide_render = True
    STATE["pyre_logs"] = py
    STATE["mopup_hook"] = None
    if hasattr(TR, "set_mopup") and bpy.data.objects.get("TrostCapturedFrames"):     # the set has them: use the set's
        STATE["mopup_hook"] = _set_mopup_no_cranes
        for o in (fr, py):
            bpy.data.objects.remove(o, do_unlink=True)
        STATE["frames"] = STATE["pyre_logs"] = None
        PLACEHOLDERS[:] = [x for x in PLACEHOLDERS if "CaptureFrames" not in x]
        PLACEHOLDERS[:] = [x.replace("G8PH_Cranes/HoistCage (mop-up cranes and", "G8PH_HoistCage (") for x in PLACEHOLDERS]
    print(f"[g8] body rows: {k}")

def _set_mopup_no_cranes(on, pyres=None):
    """The set's mop-up props without its cranes at D (owner 16:53)."""
    _hide(bpy.data.objects.get("TrostCapturedFrames"), not on)
    _hide(bpy.data.objects.get("TrostCranesD"), True)
    _hide(bpy.data.objects.get("TrostPyres"), not (on if pyres is None else pyres))

def build_lights(coll):
    """<= 8 live point lights: 4 pyres + 4 cannon flashes (recycled)."""
    pl = []
    for k, (x, y) in enumerate(PYRES):
        ld = bpy.data.lights.new(f"G8_Pyre{k}", "POINT"); ld.color = (1.0, 0.55, 0.22); ld.energy = 0.0; ld.shadow_soft_size = 2.5
        lo = bpy.data.objects.new(f"G8_Pyre{k}", ld); lo.location = SV(x, y, G(x, y) + 5.0); coll.objects.link(lo); pl.append(ld)
    cl = []
    for k in range(4):
        ld = bpy.data.lights.new(f"G8_Cannon{k}", "POINT"); ld.color = (1.0, 0.72, 0.35); ld.energy = 0.0; ld.shadow_soft_size = 4.0
        lo = bpy.data.objects.new(f"G8_Cannon{k}", ld); coll.objects.link(lo); cl.append((lo, ld))
    STATE["pyre_lights"] = pl; STATE["cannon_lights"] = cl

def build_static_wires(coll):
    L = STATE["L"]
    bm = bmesh.new()
    for a, b in STATE["static_wires"]:
        L.cyl(bm, Vector(a), Vector(b), 0.06, 0.06, seg=4)
    o = L.obj_from_bm("G8_DecoyWires", bm, [L.mat("G8_Wire", (0.03, 0.03, 0.035), 0.5)], coll); o.visible_shadow = False
    STATE["wire_ob"] = o

# ====================================================================== build / update / light (contract)
def build(site):
    t0 = time.time()
    STATE["site"] = site; STATE["TR"] = site["TR"]; STATE["L"] = site["L"]
    global BALL_R
    BALL_R = float(getattr(site["TR"], "BALL_R", BALL_R))
    coll = _coll("G8")
    # probe roofs before any geometry of ours exists
    bpy.context.view_layer.update()
    for xy in (MIKASA_ROOF, MISS_ROOF):
        perch(*xy)
    build_ball(coll)
    build_titan(coll)
    STATE["at_objs"] = [o for o in STATE["AT"].coll.all_objects]
    build_set_pieces(coll)
    STATE["bed_trees"] = bpy.data.objects.get("TrostBedTrees") or bpy.data.objects.get("G8PH_BedTrees")
    STATE["contact_b0"] = bpy.data.objects.get("TrostBallContactB0")
    cs_ = bpy.data.objects.get("TrostBallContactSeal")               # the set's seal contact ring follows our rest point
    if cs_ is not None:
        cs_.location.y += BALL_SEAL[1] - 8.0
    build_titans(coll)
    build_people(coll)
    build_crowds()
    build_flares(coll)
    build_cannon_events()
    build_cards(coll)
    build_transform_fx(coll)
    build_decals(coll)
    build_lights(coll)
    _light_capture()
    print(f"[g8] build {time.time() - t0:.1f}s; placeholders: {PLACEHOLDERS}")

def finish():
    pass

def update(tv):
    tv = float(tv)
    if bpy.context.scene.camera is not None:                     # v18: the end rise to ~66 km needs a far clip
        bpy.context.scene.camera.data.clip_end = 250000.0 if tv > 71.2 else 30000.0
    if "hazeobs" not in STATE:                                   # v18: the horizon-haze curtain washed out the three-walls view
        STATE["hazeobs"] = [o for o in bpy.data.objects if o.type == "MESH" and any(m and m.name.startswith("WD_HorizonHaze") for m in o.data.materials)]
    for o in STATE["hazeobs"]:
        h = tv > 72.6
        if o.hide_render != h:
            o.hide_render = h
    t = T_old(tv)                                        # the choreography clock (WARP); camera / light / pyres stay on tv
    st, holder = _pose_titan(t)
    # ball
    b = STATE["ball"]
    c, rx, ry = ball_state(t, st if st["vis"] else None, STATE["seat"])
    b.location = Vector(S3(c)); b.rotation_euler = (rx, ry, 0.4 + (st["yaw"] if t >= 18.2 and t < BEATS["slam"][0] else 0.0))
    if t < BEATS["chest"][0]:
        b.location.z = G(*B0) + 0.6 + BALL_R * 13.6 / 14.0 - 0.2
    # titans, people, flares, cards
    STATE["TT"].update(t)
    STATE["SQ"].update(t)
    STATE["FL"].update(t, wind=(2.2, 0.8))
    STATE["cards"].update(t, wind=(1.5, 0.6))
    STATE["cards_video"].update(tv, wind=(1.5, 0.6))
    # transformation FX
    bolt, fl, ld = STATE["tfx"]
    tb = BEATS["transform"]
    _hide(bolt, not (tb - 0.05 <= t < tb + 0.12))
    on = tb - 0.02 <= t < tb + 0.27
    _hide(fl, not on)
    if on:
        u = (t - tb + 0.02) / 0.29; s = 0.4 + 0.8 * math.sin(math.pi * min(1, u)); fl.scale = (s, s, s)
    ld.energy = 4.0e7 * bump(t, tb - 0.05, tb, tb + 0.15, tb + 0.6)
    # decals: cracks appear at each plant and fade out by ~20 s later; roof holes
    ob, V0, tp = STATE["cracks"]
    vis = (t >= tp)
    V = V0.copy().reshape(-1, 13, 3)
    V[~vis] = V[~vis][:, :1, :] + np.array([0, 0, -50.0])
    ob.data.vertices.foreach_set("co", V.reshape(-1).astype(np.float32)); ob.data.update()
    for te, h in STATE["holes"]:
        _hide(h, t < te + 0.05)
    _hide(STATE["blood"], t < 36.0)
    bt = STATE.get("bed_trees")
    if bt is not None:
        _hide(bt, t >= BEATS["sit"][0] + 0.3)          # he sits down hard on the bed's NW edge: the trees there go down
    # breach glow until the jam
    gl = 1.0 - ss(BEATS["jam"] - 0.1, BEATS["jam"] + 0.15, t)
    if STATE.get("glow_hook"):
        try: STATE["glow_hook"](gl)
        except Exception as ex: print("[g8] breach glow hook failed:", ex)
    elif STATE.get("glow"):
        g, gs, gld = STATE["glow"]
        _hide(g, gl <= 0.01); gs.default_value = 2.2 * gl; gld.energy = 2.0e5 * gl
    # plug: owner 10/27 "remove the strange triangle rising over the gate after the plug" -> the Λ spire never grows
    pu = 0.0
    if STATE.get("plug_hook"):
        try: STATE["plug_hook"](pu)
        except Exception as ex: print("[g8] plug hook failed:", ex)
    elif STATE.get("plug") is not None:
        pl = STATE["plug"]; _hide(pl, pu <= 0.001); pl.scale = (0.6 + 0.4 * pu, 1.0, max(0.01, pu))
    if STATE.get("seal_hook"):                           # set_seal: glow off, side skirt, contact ring, plug
        _hide(STATE["ring"], True)
        try:
            STATE["seal_hook"](t >= BEATS["jam"], pu)
            if t < BEATS["jam"] and STATE.get("glow_hook"):
                STATE["glow_hook"](gl)
        except Exception as ex:
            print("[g8] seal hook failed:", ex)
    else:
        _hide(STATE["ring"], t < BEATS["jam"])
    rub = STATE.get("kick_rubble")
    if rub is not None:                                  # the ball rolls through the kick's rubble fan and presses it flat
        rub.scale.z = STATE["kick_rubble_z"] * (1.0 - 0.55 * ss(BEATS["slam"][0], BEATS["jam"], t))
    if STATE.get("roof_hook"):
        try: STATE["roof_hook"](t >= BEATS["smash"] + 0.05)
        except Exception as ex: print("[g8] mikasa roof hook failed:", ex)
    for ch in STATE["chunks"]:
        o = ch["ob"]; tt = t - BEATS["jam"]
        if tt < 0 or tt > 60:
            _hide(o, True); continue
        _hide(o, False)
        u = min(1.0, tt / ch["T"])
        p = ch["p0"] + (ch["land"] - ch["p0"]) * u
        p[2] = ch["p0"][2] * (1 - u) + ch["land"][2] * u + 4.9 * ch["T"] ** 2 * u * (1 - u)
        o.location = Vector(p); sp = min(tt, ch["T"]); o.rotation_euler = tuple(ch["spin"] * sp)
    # mop-up / cleanup props
    if STATE.get("mopup_hook"):
        try: STATE["mopup_hook"](t >= BEATS["captured"] - 0.2, pyres=t >= BEATS["cleanup"][0])
        except Exception as ex: print("[g8] mopup hook failed:", ex)
    _hide(STATE["frames"], t < BEATS["captured"] - 0.2)
    bc = STATE.get("contact_b0")
    if bc is not None:
        _hide(bc, t >= BEATS["chest"][0] + 0.2)            # the bed's contact patch goes with the ball
    for q, o in enumerate(STATE["rows"]):
        _hide(o, t < BEATS["rows"][0] + q * (BEATS["rows"][1] - BEATS["rows"][0]) / 4)
    _hide(STATE["pyre_logs"], t < BEATS["cleanup"][0])
    for e in STATE["workers"]:
        _hide(e, t < BEATS["cleanup"][0])
    # lights: pyres (flicker) + recycled cannon flashes (most recent 4)
    for k, (ld_, te) in enumerate(zip(STATE["pyre_lights"], PYRE_T)):
        ld_.energy = (15000.0 * ss(te, te + 0.8, tv) * (0.85 + 0.15 * math.sin(tv * 11 + k))) if tv >= te else 0.0
    act = [(te, p) for te, kind, p in STATE["cannon_events"] if 0.0 <= t - te < 0.22][-4:]
    for k, (lo, ld_) in enumerate(STATE["cannon_lights"]):
        if k < len(act):
            te, p = act[k]; lo.location = Vector(p) + Vector((0, 0, 3.0)); ld_.energy = 2.0e5 * (1 - (t - te) / 0.22)   # v14: less sparkle
        else:
            ld_.energy = 0.0

# ---------------------------------------------------------------------- light (sun, sky, exposure) - one key table
# AUDIT 8: az 255 / el 12 at the hand-off and the green flare, then the azimuth swings to ~200-205 during the carry
# (el 8 -> 3) so the low sun sits behind the gate by the seal and the yellow flare.
# t: sun elevation (deg), compass azimuth (deg), sun energy, sun rgb, zenith rgb, horizon rgb, world (lighting) strength, exposure offset
LIGHT_KEYS = [
    (0.0,  12.0, 255, 3.4, (1.00, 0.80, 0.56), (0.20, 0.35, 0.68), (0.96, 0.78, 0.55), 1.00, 0.00),   # golden late afternoon
    (8.0,  10.0, 254, 3.3, (1.00, 0.76, 0.50), (0.20, 0.33, 0.64), (0.98, 0.74, 0.50), 0.95, 0.00),   # red flare: still golden
    (19.0,  8.0, 248, 3.1, (1.00, 0.68, 0.42), (0.21, 0.30, 0.58), (1.00, 0.68, 0.44), 0.90, 0.00),   # carry: warmer
    (40.0,  9.0, 212, 3.1, (1.00, 0.60, 0.36), (0.22, 0.28, 0.52), (1.00, 0.60, 0.38), 0.95, 0.20),   # redder (v4 QA: sun kept
                                                                                                       # above the wall so the gate side is lit)
    (47.0,  8.0, 204, 3.0, (1.00, 0.56, 0.32), (0.22, 0.26, 0.48), (1.00, 0.58, 0.34), 0.95, 0.30),
    (53.0,  9.0, 204, 3.0, (1.00, 0.66, 0.40), (0.22, 0.28, 0.52), (1.00, 0.66, 0.42), 0.95, 0.20),   # v14: Levi in DAYLIGHT
    (58.2,  8.0, 206, 3.0, (1.00, 0.64, 0.38), (0.22, 0.27, 0.50), (1.00, 0.64, 0.40), 0.95, 0.20),   # the corner volley, still day
    (59.4,  2.0, 206, 1.6, (1.00, 0.55, 0.60), (0.20, 0.16, 0.36), (0.90, 0.50, 0.58), 0.75, 0.50),   # rising: dusk
    (60.6, 30.0, 120, 1.6, (0.55, 0.66, 1.00), (0.05, 0.08, 0.18), (0.14, 0.18, 0.32), 0.60, 0.45),  # NIGHT: the corpses burn
    (75.0, 30.0, 120, 1.6, (0.55, 0.66, 1.00), (0.05, 0.08, 0.18), (0.14, 0.18, 0.32), 0.60, 0.45),
]

# colour grade per key (the toon pass maps lighting to fixed bands, so dusk / night / warmth come from a global grade):
# t: (gain r, g, b), exposure offset (stops)
GRADE_KEYS = [
    (0.0,  (1.06, 0.98, 0.86), 0.00),     # golden late afternoon
    (19.0, (1.08, 0.96, 0.82), -0.05),
    (40.0, (1.13, 0.93, 0.76), -0.15),    # carry: warmer / redder
    (47.0, (1.15, 0.91, 0.72), -0.10),
    (53.0, (1.16, 0.95, 0.66), -0.15),    # yellow at sunset
    (58.2, (1.12, 0.94, 0.72), -0.10),    # v14: Levi + the corner volley in daylight
    (59.4, (1.04, 0.84, 1.00), -0.20),    # dusk while rising
    (60.6, (0.74, 0.84, 1.12), -0.30),    # NIGHT to the end: the corpses burning in the sky view
    (75.0, (0.74, 0.84, 1.12), -0.30),
]

def _grade(t):
    K = GRADE_KEYS
    if t <= K[0][0]: return K[0][1], K[0][2]
    for a, b in zip(K, K[1:]):
        if a[0] <= t < b[0]:
            u = ss(a[0], b[0], t)
            return tuple(lerp(x, y, u) for x, y in zip(a[1], b[1])), lerp(a[2], b[2], u)
    return K[-1][1], K[-1][2]

def _light_capture():
    sc = bpy.context.scene
    suns = [o for o in bpy.data.objects if o.type == "LIGHT" and o.data.type == "SUN"]
    w = sc.world
    nodes = w.node_tree.nodes if (w and w.use_nodes) else []
    STATE["light0"] = dict(suns=suns, e0=[o.data.energy for o in suns], exp0=sc.view_settings.exposure,
                           ramps=[n for n in nodes if n.type == "VALTORGB"], skies=[n for n in nodes if n.type == "TEX_SKY"],
                           bgs=[(n, n.inputs[1].default_value) for n in nodes if n.type == "BACKGROUND"])
    # the brightest background (camera-ray gradient) vs the lighting one: scale both with the key's world strength
    STATE["light_last"] = None

def _lkey(t):
    K = LIGHT_KEYS
    if t <= K[0][0]: return K[0], K[0], 0.0
    for a, b in zip(K, K[1:]):
        if a[0] <= t < b[0]:
            return a, b, ss(a[0], b[0], t)
    return K[-1], K[-1], 0.0

def light(tv):
    t = T_old(float(tv))                                 # light keys and the grade follow the story (choreography) clock
    a, b, u = _lkey(t)
    def mix(i):
        x, y = a[i], b[i]
        if isinstance(x, tuple):
            return tuple(lerp(p, q, u) for p, q in zip(x, y))
        return lerp(x, y, u)
    def sdir(k):
        el, az = math.radians(k[1]), math.radians(k[2])
        return np.array([math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el)])
    d = sdir(a) * (1 - u) + sdir(b) * u; d /= np.linalg.norm(d)
    if d[2] < 0.03:                                      # light from just above the horizon (the sky still glows)
        d[2] = 0.03; d /= np.linalg.norm(d)
    L0 = STATE["light0"]
    en = mix(3); col = mix(4); zen = mix(5); hor = mix(6); ws = mix(7); ex = mix(8)
    for o in L0["suns"]:
        o.rotation_euler = Vector(-d).to_track_quat("-Z", "Y").to_euler()
        o.data.energy = en; o.data.color = col
    for r in L0["ramps"]:
        el = r.color_ramp.elements
        el[0].color = (*hor, 1); el[-1].color = (*zen, 1)
    for s in L0["skies"]:
        try:
            s.sun_elevation = math.radians(max(-4.0, mix(1))); s.sun_rotation = math.atan2(d[1], d[0])
        except Exception:
            pass
    for n, s0 in L0["bgs"]:
        n.inputs[1].default_value = s0 * ws
    gain, gex = _grade(float(t))
    vs = bpy.context.scene.view_settings
    vs.exposure = L0["exp0"] + gex
    # v18b: the three-walls end goes to DAWN: a low warm sun rakes the ground and lights the wall rings, brighter grade
    du = ss(72.0, 73.6, float(tv))
    if du > 0.0:
        dd = np.array([0.80, -0.45, 0.22]); dd /= np.linalg.norm(dd)
        dd = d * (1 - du) + dd * du; dd /= np.linalg.norm(dd)
        for o in L0["suns"]:
            o.rotation_euler = Vector(-dd).to_track_quat("-Z", "Y").to_euler()
            o.data.energy = en + (5.0 - en) * du
            o.data.color = tuple(cc + (w - cc) * du for cc, w in zip(col, (1.0, 0.86, 0.70)))
        for n, s0 in L0["bgs"]:
            n.inputs[1].default_value = s0 * (ws + (1.0 - ws) * du)
        vs.exposure += 1.3 * du
    try:
        vs.use_curve_mapping = True
        cm = vs.curve_mapping
        cm.white_level = tuple(1.0 / max(g, 1e-3) for g in gain)
        cm.black_level = (0.0, 0.0, 0.0)
        cm.update()
    except Exception as ex_:
        if not STATE.get("grade_warned"):
            print("[g8] colour grade failed:", ex_); STATE["grade_warned"] = True

def cam_shake(tv):
    """Short camera shake at the slam (video clock): (pitch, yaw) radians, ~0.45 deg peak, 0.4 s, decaying."""
    tj = T_new(BEATS["jam"]); u = tv - tj
    if u < 0.0 or u > 0.45:
        return 0.0, 0.0
    a = math.radians(0.45) * (1 - u / 0.45) ** 2
    return a * math.sin(u * 2 * math.pi * 14.0), a * 0.7 * math.sin(u * 2 * math.pi * 11.0 + 1.3)

# ====================================================================== HUD trackers (M) + self checks
def _p_set_to_M(p):
    return (float(p[0]), float(p[1]) + segtime.SET_OFF_Y, float(p[2]))

def _sq(name, t0=-1e9, t1=1e9):
    def f(t):
        if not (t0 <= t < t1): return None
        st = STATE["SQ"].state(name, t)
        return _p_set_to_M(st["pos"] + np.array([0, 0, 2.0])) if st["vis"] > 0 else None
    return f

def _at_head(t):
    st = at_state(t)
    if not st["vis"] or t < 5.3: return None
    return (float(st["pos"][0]), float(st["pos"][1]), 16.0 if st["mode"] not in ("sit", "slump") else 10.0)

def _eren(t):
    if t < BEATS["transform"]:
        return _sq("eren")(t)
    if t >= 57.0:
        return _sq("eren_out")(t)
    return None

_TRACK0 = {"Eren": _eren, "AttackTitan": _at_head, "Mikasa": _sq("mikasa"), "Armin": _sq("armin"), "Rico": _sq("rico"),
           "Levi": _sq("levi", 52.0, 75.0), "Pyxis": lambda t: _p_set_to_M(STATE["pyxis"]) if 52.0 <= t < 60.0 else None}
TRACK = {k: (lambda f: (lambda tv: f(T_old(tv))))(f) for k, f in _TRACK0.items()}

def check():
    """Collision checks of the carry (bible g8 build notes): feet outside the outer trench (r 17-24 about P, outside the
    +-45 deg gap), the ball >= 1 m off the east pilaster face, ball rest flush with the gatehouse face."""
    worst_p = 1e9; worst_tr = None; bad = []
    for t in np.arange(40.0, BEATS["jam"] + 0.01, 0.05):
        st = at_state(t)
        c, _, _ = ball_state(t, None, dict(zc=20.6, fc=1.0))
        dx = max(PILASTER_E[0] - c[0], 0.0, c[0] - PILASTER_E[1]); dy = max(c[1] - PILASTER_E[2], 0.0) if c[1] > PILASTER_E[2] else 0.0
        dpil = math.hypot(dx, dy) - BALL_R if c[1] > PILASTER_E[2] else -1.0
        if PILASTER_E[0] - BALL_R - 2 < c[0] < PILASTER_E[1] + BALL_R + 2:
            worst_p = min(worst_p, dpil)
        yaw = st["yaw"]; rt = np.array([math.cos(yaw), math.sin(yaw)])
        for sd in (-1, 1):
            f = st["pos"] + rt * (foot_w(st["s"]) if "s" in st else FOOT_W) * sd
            dxp, dyp = f[0] - PIT[0], f[1] - PIT[1]; r = math.hypot(dxp, dyp)
            ang = abs(math.degrees(math.atan2(dxp, -dyp)))           # 0 = due south of P
            if 17.0 <= r <= 24.0 and ang > 45.0:
                bad.append((round(t, 2), tuple(np.round(f, 1)), round(r, 1), round(ang, 1)))
    rest = np.array(BALL_SEAL)
    print(f"[g8] CHECK route length {ROUTE_LEN:.1f} m (bible BR 438 m from B0; ours starts at the sit/lift spot); "
          f"knots {dict(zip(ROUTE_NAMES, np.round(_RT, 2)))}")
    print(f"[g8] CHECK ball vs east pilaster face: min clearance {worst_p:.2f} m (need >= 1.0)")
    print(f"[g8] CHECK feet in the outer trench: {len(bad)} samples" + (f" first {bad[:3]}" if bad else " (clear)"))
    print(f"[g8] CHECK ball rest {tuple(rest)} front Y {rest[1] + BALL_R:.1f} (gatehouse face Y 15)")
    angs, dists, pits = [], [], []
    for t in np.arange(BEATS["carry"][0], BEATS["carry"][1], 0.1):         # camera vs his facing: never behind his back
        st = at_state(t); loc, look, lens = CAM.eval(T_new(t))
        fw = np.array([-math.sin(st["yaw"]), math.cos(st["yaw"])]); d = np.array(loc[:2]) - st["pos"]; dist = float(np.linalg.norm(d))
        angs.append(math.degrees(math.acos(max(-1.0, min(1.0, float(np.dot(fw, d / dist))))))); dists.append(dist)
        pits.append(math.degrees(math.atan2(loc[2] - 12.0, dist)))
    print(f"[g8] CHECK carry camera: angle off his front {min(angs):.0f}..{max(angs):.0f} deg (90 = side, > 90 = behind), "
          f"distance {min(dists):.0f}..{max(dists):.0f} m, pitch to the ball {min(pits):.1f}..{max(pits):.1f} deg")
    vmax = max((route_s(T_old(t + 0.05)) - route_s(T_old(t))) / 0.05 for t in np.arange(19.0, 38.0, 0.05))     # video clock
    vavg = ROUTE_LEN / (T_new(BEATS["carry"][1]) - T_new(BEATS["carry"][0]))
    print(f"[g8] CHECK carry (video clock) {T_new(BEATS['carry'][0]):.1f}-{T_new(BEATS['carry'][1]):.1f} s: mean {vavg:.1f} m/s, peak {vmax:.1f} m/s, "
          f"cadence {vavg / STEP_L:.2f} (mean) .. {vmax / STEP_L:.2f} (peak) steps/s, stride {STEP_L} m")
    return dict(pilaster=worst_p, trench=len(bad))

if __name__ == "__main__":
    r = camchan.check(CAM, 0.0, DUR, limits=dict(name="g8 CAM", **CAM_LIMITS))
    check()
