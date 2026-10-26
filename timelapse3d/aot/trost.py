"""TROST DISTRICT set v3 (AoT S1, 850) = SCENE_BIBLE_v2 section C, built as a scene.py district plug-in.

Run (stills):  bash render_trost_set.sh   or   AOT_SET=trost blender -b -P aot/scene.py -P aot/trost.py -- --stills DIR
Use in a shot: AOT_SET=trost blender -b -P aot/scene.py -P <render script> ...   (scene.build() calls build_set()).
render_seg.py builds the set once through that hook, then imports aot/seg_<id>.py.

FRAMES.  Master frame M (bible): outer gate O = (0, 0), +Y north, Wall Rose centreline Y 870, Z up, town ground Z 0.
The Blender scene uses the SET frame = (X, Y - 870, Z) (Wall Rose along set y = 0, outer gate at set (0, -870)).
    M(x, y, z=0)  -> set coords (use it for every position written in M)       to_m(x, y, z=0) -> M coords
    ANCHORS_M     every bible-C anchor in M (import it, never retype numbers)
All geometry is authored in M; static meshes carry object location (0, -870, 0); posable props have their origin at the
anchor and location = M(anchor).  Public query functions keep the OLD set-frame signatures (x, y = set coords):
ground_z, walkable, on_road, nearest_road, in_district, in_canal, street_polylines; the *_m twins take M coords.

KEY OBJECTS (names other agents use)
  OuterGate / OuterGate_Door / OuterGate_Iron      intact town-side gatehouse, its big strap door, the outside iron leaf
  OuterGateBroken / OuterGateRubble / TrostBreachTimbers   the kick breach (X -7.5..7.5, top Z 30-34) + rubble fan + broken
                     timbers / roots (was OuterGate_Beams; renamed so toon.py does not ink it with 0.25 m black hulls)
  TrostBallContactB0 / TrostBallContactSeal   darker contact patch + dust ring under the ball (bed at B0 / the seal rest;
                     the seal one shows with set_seal(True); g8 hides the B0 one when the ball is lifted)
  OuterGate_Glow     orange emissive card in the breach (set_glow(v))          OuterGate_Plug   Λ tendril plug (set_plug(f))
  OuterGate_SealRubble crushed-brick ring at the ball rest (set_seal)          GS_Crater* / GS_CraterCap* (set_breach)
  TrostSlab_P1..P6 (pit arc), TrostSlab_A1..A8 (avenue mouth): spiked slab barricades, origin = base centre, local -Y =
      spiked front (faces the gate), SLABS dict = {name: (X, Y, yaw_deg)} in M
  TrostBoulder       the ball, ORIGIN AT ITS CENTRE, BALL_R = 7.0, BOULDER_SIZE (14, 14, 13.6), at BOULDER_CENTER_M
  TrostRock2         the 6 m second rock;   TrostMikasaRoof / TrostMikasaRoofBroken (set_mikasa_roof(broken))
  TrostCart (parent empty) -> TrostCart_Body / _Load / _Horses  (set_cart(state) or pose the empty; block 6)
  TrostTowerT_Top    top 8 m of Q2 tower T (bursts)                (block 6)
  TrostHQ_* , set_hq_cutaway(frac), set_hq_lift(frac), TrostHQ_Cage   (block 7)
API  set_breach(on), set_glow(v), set_plug(frac), set_seal(on), set_mikasa_roof(broken), set_lift(i, frac),
     set_wagon(on) (= cart visible), set_hq_cutaway(frac or bool), set_hq_lift(frac), boulder_mesh(), marble_mat()
"""
import bpy, bmesh, math, random, os, sys, time
from mathutils import Vector, Euler, Matrix, noise

import aotlib as L

SET_NAME = "trost"
REPLACES = {"hill", "kids", "titans"}

# ====================================================================================== frames + anchors
DY = -870.0
def M(x, y, z=0.0):
    """M (bible master frame) -> set/Blender coords."""
    return (float(x), float(y) + DY, float(z))

def to_m(x, y, z=0.0):
    """set/Blender coords -> M."""
    return (float(x), float(y) - DY, float(z))

W, S, R = 480.0, 390.0, 480.0            # district half width, straight side length, round-end radius (set frame)
WALL_H, WALL_T = 50.0, 10.0
ARC_C = (0.0, 480.0)                     # M centre of the south half circle
BALL_R = 7.0
BOULDER_SIZE = (14.0, 14.0, 13.6)
BOULDER_CENTER_M = (290.0, 262.0, 7.4)
BALL_REST_M = (0.0, 8.0, 7.0)

BR_M = [(290, 262), (284, 232), (280, 160), (274, 117), (228, 86), (185, 64), (141, 47), (95, 35), (63, 29),
        (36, 21), (18, 18.5), (4, 23)]
BR_NAMES = ["B0", "R1", "R2", "R3", "A1", "A2", "A3", "A4", "R4", "R5", "R5b", "R6"]

TOWERS_M = {   # bell towers T: (X, Y, side, height, cap)  cap: red / copper / slate
    "T1": (-110, 470, 8, 50, "red"), "T2": (-320, 300, 8, 46, "slate"), "T3": (180, 330, 8, 48, "copper"),
    "T5": (120, 620, 8, 52, "red"), "T6": (-380, 520, 7, 44, "slate"), "T7": (-180, 235, 8, 47, "red"),
    "T8": (300, 560, 8, 50, "slate"), "TF1": (-310, 560, 7, 42, "copper"), "TF2": (60, 200, 7, 43, "slate"),
    "TF3": (205, 470, 8, 49, "red"), "TF4": (-30, 655, 7, 45, "red"), "TF5": (130, 790, 8, 47, "slate"),
    "TF6": (-430, 690, 7, 41, "copper"), "TF7": (335, 190, 7, 44, "red"), "TF8": (-170, 360, 8, 46, "slate"),
}   # + T_K (322, 818) basin, court belfry (228, 290), tower T (-218, 522) Q2, RC NE tower (-213, 845) = 19 in all

ANCHORS_M = {
    "O": (0, 0, 0), "BALL_REST": BALL_REST_M, "COL_FEET": (0, -23, 0), "COL_FIST_R": (26, 0, 50),
    "GS": (0, 0, 70), "GS_RING": (70, 78), "P": (0, 36, 0), "CRw": (-32, 20, 0), "CRe": (34, 30, 0),
    "H1": (-34, 32, 0), "H2": (-30, 50, 0), "H3": (38, 44, 0),
    "BO": [(-30, 30), (-25, 30), (-15, 30), (-10, 30), (10, 30), (15, 30), (25, 30)],
    "TR_spruce": [(-34, 10), (-40, 13)], "TR_bushy": [(34, 10)], "LG": (-62, 10, 0),
    "PLANK_BOX": [(-24, 40), (22, 52)],
    "AV": [(0, 74), (-15, 300), (-60, 470), (-128, 735), (-153, 803)], "C": (-60, 470, 45),
    "E": (-178, -102, 800, 853), "EVS": [(-102, 800), (0, 690)], "I": (-140, 870, 0), "I_ARCH": (-140, 851, 0),
    "CART_END": (-122, 842, 320.0), "CART_START": (-140, 853.5, 90.0), "AB_KILL": (-85, 782), "AB_CORPSE": (-96, 794),
    "MA": (-262, 380, 458), "MA_LAND": (-262, 400), "SS": (-257.5, -150, 418, 428), "BT": (-205, 423),
    "Q2": (-252, -222, 490, 520, 5.0), "TOWER_T": (-218, 522, 34.0), "ROOF_R": (-258, 505, 25),
    "HQ_KEEP": (-250, 640), "HQ_WING": (-234, -136, 628, 652), "HQ_STORE": (-205, -169, 631, 651),
    "HQ_LIFT": (-187, 641), "HQ_TERRACE": (-270, -230, 612, 624, 2.5), "HQ_PLAZA": (-275, -100, 570, 624),
    "HQ_WEST": (-300, -266, 570, 660), "GH_HOUSE": (-200, 566), "EREN_NAPE": (-178, 619),
    "AT_PATH": [(-222, 531), (-230, 572), (-240, 600)],
    "RC": (-268, 805), "D": (-475, -360, 760, 865),
    "K_FLOOR": (340, 385, 833, 865, -3.6), "T_K": (322, 818), "GB": (308, 338, 849, 865, 20.0),
    "K_CANNON": (318, 857, 20), "K_TRIO": (362, 852, -3.6), "K_PLINTH": (357, 367, 828, 838, -0.6),
    "K_GH": (341, 377, 792, 812), "L_K": (338, 868, 50), "K_BASKET": (342, 861, -3.6),
    "CAN": [(400, 870), (400, 345), (445, 300)], "CAN_W": 26.0, "CAN_WATER_Z": -4.2,
    "CAN_BRIDGES_Y": [420, 560, 700, 820], "WG_ROSE": (393, 411, 865, 875), "WG_EXIT": (445, 300),
    "B0": BOULDER_CENTER_M, "COURT": (225, 318, 236, 292), "BELFRY": (228, 290, 42.0), "BED": (290, 262, 15.0),
    "ROCK2": (308, 247, 6.0), "LANE": [(232, 300), (180, 360)], "COURT_EXIT": (284, 236, 16.0),
    "MIKASA_ROOF": (252, 300), "BR": BR_M, "STRIP": (437.0, 475.0, 8.0, 37.0),
    "GF": (334, 136, 50), "RF": (306, 300, 19), "YF": (-24, 40, 2.5), "PY": (-20, 870, 50),
    "LV": (-40, 2, 50), "CT": [(-45, 45), (-55, 32)], "MI": (-75, -60, 14, 22), "IA": (-36, 56),
    "CROUCH": (44, 27), "CROUCH_FALL": (52, 36),
    "PYR": [(-60, 470), (50, 55), (-12, 250), (150, 330)],
    "A": (-20, 935, 90, 60), "S1": (-120, 866, 50), "S2": (-20, 874, 50), "PYXIS_POST": (-20, 866, 50),
    "L": [(-380, 870), (-40, 870), (260, 870), (-195, 870)], "ROSE_HOISTS_X": [-60, -20, 20],
    "TOWERS": {k: v[:2] for k, v in TOWERS_M.items()},
}

# ====================================================================================== old public names (set frame)
OUTER_GATE = M(0, 0)[:2]
INNER_GATE = M(-140, 870)[:2]
CANAL_X, CANAL_W = 400.0, 26.0
CANAL_WATER_Z = -4.2
WATER_GATE_ROSE = M(402, 870)[:2]
WATER_GATE_OUTER = M(445, 300)[:2]
PLAZA = (-60.0, 470.0 + DY, 45.0)
BOULDER = (BOULDER_CENTER_M[0], BOULDER_CENTER_M[1] + DY, BOULDER_CENTER_M[2] - BOULDER_SIZE[2] / 2)   # bottom centre
BOULDER_SQUARE = (290.0, 262.0 + DY, 40.0)
BOULDER_ROUTE_M = [tuple(map(float, p)) for p in BR_M]
BOULDER_ROUTE = [M(*p)[:2] for p in BR_M]
INNER_GATE_SQUARE = (-178.0, 800.0 + DY, -102.0, 853.0 + DY)
OUTER_GATE_SQUARE = (0.0, DY + 36.0, 78.0)
WALLTOP_SPEECH = M(-20, 874, 50)
AVENUE = [M(*p)[:2] for p in ANCHORS_M["AV"]]
EVAC_ROUTE = [M(-60, 470)[:2], M(-100, 625)[:2], M(-135, 790)[:2], M(-140, 845)[:2], M(-140, 866)[:2]]
BELL_TOWER = dict(xy=M(-110, 470)[:2], belfry_z=(38.0, 45.0), belfry_c=M(-110, 470, 41.5), top_z=50.0)
WALL_LIFTS = [dict(name=n, xy=M(*p)[:2], out=o, platform=f"TrostLift_{n}_Platform")
              for n, p, o in (("RoseW", (-380, 870), (0, -1)), ("RoseC", (-40, 870), (0, -1)), ("RoseE", (260, 870), (0, -1)),
                              ("Gate", (-62, 4.0), (0.129, 0.992)),        # LG: shaft at about (-62, 10)
                              ("RoseHQ", (-195, 870), (0, -1)))]           # AUDIT 6: posts + lintel behind the HQ (ep09 21:36.8)
LABELS = {"TROST DISTRICT": M(60, 420, 20), "WALL ROSE": M(-1100, 870, 50), "INNER GATE": M(-140, 870, 50),
          "OUTER GATE": M(0, 0, 50), "SUPPLY HQ": M(-250, 640, 40), "BOULDER": M(290, 262, 16)}

# supply HQ / cannon basin data (set frame, the old dict layout; built in blocks 7/8)
SUPPLY_HQ = dict(center=M(-187, 641)[:2], rot=0.0, size=(36.0, 20.0), store_z=(0.0, 9.5), roof_z=41.0,
                 lift_xy=M(-187, 641)[:2], lift_z=(2.8, 10.0),
                 titan_spots=[M(-187 + 4.5 * math.cos(a), 641 + 4.5 * math.sin(a))[:2] for a in [k * math.tau / 7 for k in range(7)]],
                 door_xy=M(-205, 626)[:2], roof_xy=M(-185, 640)[:2], tower_xy=M(-250, 644)[:2], keep_xy=M(-250, 640)[:2],
                 keep_size=(32.0, 32.0, 28.0), keep_top_z=58.0, warehouse_roof_z=(24.0, 41.0),
                 wing=(M(-234, 628)[:2], M(-136, 652)[:2]), plaza=(M(-275, 570)[:2], M(-100, 624)[:2]))
HQ_UPPER = []

def _basin_rows():
    rows = []
    for k in range(12):                              # SB: 12 steps of 0.3 / 1.0 m from Z -3.6 (Y 833) up to Z 0 (Y 821)
        yy = 833.0 - (k + 0.5) * 1.0
        z = -3.6 + (k + 1) * 0.3
        rows.append([M(x, yy, z) for x in range(342, 384, 2) if not 356.0 < x < 368.0])
    return rows
CANNON_BASIN = dict(center=M(362, 849)[:2], floor=(340.0, 385.0, 833.0 + DY, 865.0 + DY), floor_z=-3.6, top_z=0.0,
                    steps_s=_basin_rows(), steps_n=[], landing=M(362, 833, -0.6), trio=M(362, 852, -3.6),
                    cannon=M(318, 857, 20), cannon_aim=(1.0, -0.09), plinth=M(362, 833, -0.6),
                    terrace=(300.0, 400.0, 813.0 + DY, 821.0 + DY, 0.0), quay=M(386, 849, -3.6), boat=M(389, 847, -4.2),
                    basket=M(342, 861, -3.6), derrick=M(338, 868, 50))

# ====================================================================================== district geometry (M)
def wall_dist_m(X, Y):
    """Distance from the district wall centreline, positive inside the district."""
    dr = 870.0 - Y
    if Y >= 480.0:
        ds = 480.0 - abs(X)
    else:
        ds = 480.0 - math.hypot(X, Y - 480.0)
    return min(dr, ds)

def in_district_m(X, Y, margin=0.0):
    return wall_dist_m(X, Y) > margin

def strip_phi(X, Y):
    """Compass angle (deg, from due south toward east) about the arc centre (0, 480)."""
    return math.degrees(math.atan2(X, 480.0 - Y))

def in_strip_m(X, Y, pad=0.0):
    r = math.hypot(X, Y - 480.0)
    ph = strip_phi(X, Y)
    return Y < 480 and r > 437.0 - pad and 8.0 - pad * 0.12 < ph < 37.0 + pad * 0.12

def district_outline_m(step=4.0):
    pts = [(-480.0, 870.0), (-480.0, 480.0)]
    n = int(math.pi * 480 / step)
    for s_ in range(1, n):
        a = math.pi + s_ / n * math.pi
        pts.append((math.cos(a) * 480.0, 480.0 + math.sin(a) * 480.0))
    pts += [(480.0, 480.0), (480.0, 870.0)]
    return L.resample(pts, step)

def rose_y_m(X):
    """Wall Rose centreline (M): straight Y 870 over the district, bending as world.py expects beyond |X| 480."""
    if abs(X) <= W:
        return 870.0
    return 870.0 - (X * X - W * W) / (2 * 380000.0 / 30)

# canal centreline (M): the inner run, the bend to the east-wall exit, then SE outside
def _canal_line():
    pts = [(400.0, 875.0)] + [(400.0, float(y)) for y in range(864, 380, -8)]
    P0, P1, P2, P3 = Vector((400, 380)), Vector((400, 345)), Vector((445 - 30 * 0.829, 300 + 30 * 0.559)), Vector((445, 300))
    for k in range(1, 21):
        t = k / 20
        p = (1 - t) ** 3 * P0 + 3 * (1 - t) ** 2 * t * P1 + 3 * (1 - t) * t * t * P2 + t ** 3 * P3
        pts.append((p.x, p.y))
    x, y, h = 445.0, 300.0, 124.0
    for k in range(1, 51):                       # 400 m outside, heading 124 deg -> 135 deg (bearing)
        h = min(135.0, h + 1.1)
        x += 8 * math.sin(math.radians(h)); y += 8 * math.cos(math.radians(h))
        pts.append((x, y))
    return pts
CANAL_LINE_M = _canal_line()

def _seg_dist(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    l2 = dx * dx + dy * dy
    t = 0.0 if l2 == 0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / l2))
    return math.hypot(px - ax - t * dx, py - ay - t * dy), t

def canal_dist_m(X, Y):
    if not (-20 < X < 760 and -20 < Y < 877):
        return 1e9
    if Y > 372 and abs(X - 400) < 60:
        return abs(X - 400)
    if Y > 372:
        return 1e9
    best = 1e9
    for k in range(len(CANAL_LINE_M) - 1):
        (ax, ay), (bx, by) = CANAL_LINE_M[k], CANAL_LINE_M[k + 1]
        if min(ax, bx) - 40 < X < max(ax, bx) + 40 and min(ay, by) - 40 < Y < max(ay, by) + 40:
            best = min(best, _seg_dist(X, Y, ax, ay, bx, by)[0])
    return best

def _in_rect(X, Y, r, pad=0.0):
    return r[0] - pad < X < r[1] + pad and r[2] - pad < Y < r[3] + pad

PIT_C = (0.0, 36.0)
def _pit_trench(X, Y):
    """Ring pit P: (inside_pit, floor_z) for people / ground queries."""
    dx, dy = X - PIT_C[0], Y - PIT_C[1]
    r = math.hypot(dx, dy)
    if r > 24.0:
        return False, 0.0
    a = math.degrees(math.atan2(dy, dx))
    gap = -135.0 < a < -45.0                       # the C opens toward the gate (due south +-45 deg)
    if gap:
        return True, 0.0
    if 17.0 < r <= 24.0:
        if r > 22.5:
            return True, -2.3 if r > 23.25 else -4.6
        return True, -7.0
    if 7.0 < r < 11.0:
        return True, -4.0
    return True, 0.0

CRATERS_M = [(-32.0, 20.0, 4.5), (34.0, 30.0, 4.5)]
HOLES_M = [(-34.0, 32.0, 2.0), (-30.0, 50.0, 1.8), (38.0, 44.0, 2.4)]

def ground_z_m(X, Y):
    """Walkable ground height in M (town Z 0; the pit, craters, canal water, basin, Q2 rise, E terraces)."""
    inp, z = _pit_trench(X, Y)
    if inp:
        return z
    for cx, cy, r in CRATERS_M + HOLES_M:
        d = math.hypot(X - cx, Y - cy)
        if d < r:
            return -2.0 * (1 - (d / r) ** 2) if r > 3 else -2.5
    if canal_dist_m(X, Y) < 11.5:
        return CANAL_WATER_Z
    if 340.0 <= X <= 385.0 and 821.0 <= Y <= 865.0:
        if Y >= 833.0:
            if X < 348.0 and Y < 855.0:
                return -3.6 + max(0.0, min(3.6, (348.0 - X) * 0.45))
            return -3.6
        if 357.0 <= X <= 367.0 and Y >= 828.0:
            return -0.6
        return -3.6 + min(3.6, (int((833.0 - Y) / 1.0) + 1) * 0.3)
    if 308.0 <= X <= 338.0 and 849.0 <= Y <= 865.0:
        return 20.0
    if -266.5 <= X <= -257.5 and 440.0 <= Y <= 458.0:             # MA: 5 steps (0.3 / 0.6) then the rubble foot
        return min(1.5, (int((Y - 440.0) / 0.6) + 1) * 0.3)
    # Q2 rise (floor +5) and its slopes
    dq = max(-252.0 - X, X + 222.0, 490.0 - Y, Y - 520.0, 0.0)
    if dq < 38.0:
        f = 1.0 if dq <= 0 else max(0.0, 1.0 - dq / 38.0)
        zq = 5.0 * (f * f * (3 - 2 * f))
        if X > -266.5 and Y < 458.0 and -266.5 <= X <= -257.5:
            zq = 0.0                                   # Mikasa's alley stays flat up to its end wall
        if zq > 0.01:
            return zq
    if -105.0 <= X <= -60.0 and 820.0 <= Y <= 866.0:          # E: terrace (Z 1) and grass slope (1 -> 4)
        return 1.0 if Y < 840.0 else 1.0 + 3.0 * (Y - 840.0) / 25.0
    if -133.0 <= X <= -105.0 and 849.0 <= Y <= 853.0:
        return 1.2
    return 0.0

# ====================================================================================== streets (M)
AV_PTS = [tuple(map(float, p)) for p in ANCHORS_M["AV"]]
C_XY = (-60.0, 470.0)

def _poly_resample(pts, step):
    return L.resample(pts, step)

def _street_blocked(X, Y, kind, hw):
    """Where streets may not run (kind-based exemptions)."""
    if not in_district_m(X, Y, 10.0 + hw * 0.6):
        return True
    rO = math.hypot(X, Y)
    if rO < 80.0 and kind not in ("av", "ringroad"):
        return True
    if math.hypot(X - C_XY[0], Y - C_XY[1]) < 44.0 and kind not in ("av",):
        return True
    if (_in_rect(X, Y, (-300, -100, 568, 624), hw) or _in_rect(X, Y, (-300, -266, 568, 660), hw) or _in_rect(X, Y, (-270, -136, 610, 700), hw)) and kind not in ("hq", "q2st"):
        return True
    if _in_rect(X, Y, (-182, -60, 796, 870), hw * 0.5) and kind not in ("av", "evs"):
        return True
    if _in_rect(X, Y, (219, 324, 230, 298), hw * 0.5) and kind not in ("br", "lane"):
        return True
    if canal_dist_m(X, Y) < 13.0 + hw and kind not in ("bridge",):
        return True
    if _in_rect(X, Y, (300, 400, 768, 870), hw) and kind not in ("quay",):
        return True
    if _in_rect(X, Y, (-336, -200, 757, 870), hw):
        return True
    if X < -400 and Y > 785:
        return True
    if _in_rect(X, Y, (-254, -214, 486, 528), hw) and kind not in ("q2st",):
        return True
    if _in_rect(X, Y, (-286, -236, 376, 462), 0) and kind not in ("ma", "ring", "ss"):
        return True
    if in_strip_m(X, Y, hw) and kind not in ("br",):
        return True
    return False

def _ring_pts(r, step=4.0):
    n = int(math.tau * r / step)
    return [(C_XY[0] + r * math.cos(k * math.tau / n), C_XY[1] + r * math.sin(k * math.tau / n)) for k in range(n + 1)]

def _wall_road_pts():
    out = []
    pts = district_outline_m(4.0)
    for k, p in enumerate(pts):
        a = pts[max(k - 1, 0)]; b = pts[min(k + 1, len(pts) - 1)]
        t = Vector((b[0] - a[0], b[1] - a[1])).normalized(); n = Vector((-t.y, t.x))
        out.append((p[0] + n.x * 11.0, p[1] + n.y * 11.0))
    out = [p for p in out if p[1] < 859.0]
    return out + [(470.0 - 4.0 * k, 859.0) for k in range(0, 236)]

_STREETS_M = None
def _raw_streets():
    raw = [(AV_PTS[:3], 7.0, "av"), (AV_PTS[2:], 7.0, "av")]
    for r_ in (130.0, 240.0, 350.0, 455.0):
        raw.append((_ring_pts(r_), 4.5, "ring"))
    for ang in (-50, -15, 20, 55, 140, 170, 205, 240):
        a = math.radians(ang)
        raw.append(([(C_XY[0] + math.cos(a) * r_, C_XY[1] + math.sin(a) * r_) for r_ in range(46, 700, 4)], 4.5, "radial"))
    raw += [
        ([(-102, 800), (0, 690)], 5.0, "evs"), ([(-257.5, 423), (-150, 423)], 5.0, "ss"),
        ([(-262, 380), (-262, 440)], 4.5, "ma"), ([(232, 300), (180, 360)], 3.5, "lane"),
        ([(284, 238), (280, 160), (274, 117)], 9.0, "br"), ([(-232, 518), (-232, 570)], 6.0, "q2st"),
        ([(382, 765), (382, 352)], 5.0, "quay"), ([(418, 862), (418, 340)], 5.0, "quay"),
        (_wall_road_pts(), 3.0, "wallroad"),
        ([(-150, 430), (-40, 430)], 4.0, "lane2"), ([(10, 560), (140, 560)], 4.0, "lane2"),
        ([(-20, 780), (290, 780)], 4.5, "lane2"), ([(160, 680), (370, 680)], 4.0, "lane2"),
        ([(60, 300), (200, 250)], 4.0, "lane2"), ([(-300, 640), (-420, 640)], 4.0, "lane2"),
        ([(-330, 230), (-200, 120)], 4.0, "lane2"),
    ]
    for yb in ANCHORS_M["CAN_BRIDGES_Y"]:
        raw.append(([(372.0, float(yb)), (468.0, float(yb))], 4.5, "bridge"))
    # the gate-square ring road (pale paving, r 70-78)
    raw.append(([(74 * math.cos(math.radians(a)), 74 * math.sin(math.radians(a))) for a in range(4, 177, 3)], 4.0, "ringroad"))
    return raw

def streets_m():
    """[(pts, half_width, kind)] in M, clipped to where streets may run."""
    global _STREETS_M
    if _STREETS_M is not None:
        return _STREETS_M
    out = []
    for pts, hw, kind in _raw_streets():
        pts = _poly_resample(pts, 3.0)
        cur = []
        for X, Y in pts:
            if _street_blocked(X, Y, kind, hw):
                if len(cur) > 3:
                    out.append((cur, hw, kind))
                cur = []
            else:
                cur.append((X, Y))
        if len(cur) > 3:
            out.append((cur, hw, kind))
    _STREETS_M = out
    return out

_ROADIDX = None
def _road_index():
    global _ROADIDX
    if _ROADIDX is None:
        g = {}
        for pts, hw, kind in streets_m():
            for k in range(len(pts) - 1):
                ax, ay = pts[k]; bx, by = pts[k + 1]
                n = max(1, int(math.hypot(bx - ax, by - ay) / 1.5))
                ang = math.atan2(by - ay, bx - ax)
                for t in range(n + 1):
                    x, y = ax + (bx - ax) * t / n, ay + (by - ay) * t / n
                    g.setdefault((int(x // 20), int(y // 20)), []).append((x, y, hw, ang, kind))
        _ROADIDX = g
    return _ROADIDX

OPEN_SQUARES_M = [("circle", 0.0, 0.0, 78.0), ("circle", -60.0, 470.0, 45.0), ("rect", -178, -102, 800, 853),
                  ("rect", -275, -100, 570, 624), ("rect", -300, -266, 570, 660), ("rect", -252, -222, 490, 520),
                  ("rect", 225, 318, 236, 292), ("rect", -65, 25, 905, 965)]

def on_road_m(X, Y, pad=0.0):
    for sq in OPEN_SQUARES_M:
        if sq[0] == "circle":
            if (X - sq[1]) ** 2 + (Y - sq[2]) ** 2 < (sq[3] + pad) ** 2 and (sq[1] != 0.0 or Y > 0):
                return True
        elif _in_rect(X, Y, sq[1:], pad):
            return True
    if in_strip_m(X, Y):
        return True
    g = _road_index()
    gx, gy = int(X // 20), int(Y // 20)
    for i in (-1, 0, 1):
        for j in (-1, 0, 1):
            for px, py, hw, ang, kind in g.get((gx + i, gy + j), ()):
                if (px - X) ** 2 + (py - Y) ** 2 < (hw + pad) ** 2:
                    return True
    return False

def _nearest_street(X, Y, search=2):
    g = _road_index(); best, bd = None, 1e18
    gx, gy = int(X // 20), int(Y // 20)
    for i in range(-search, search + 1):
        for j in range(-search, search + 1):
            for s_ in g.get((gx + i, gy + j), ()):
                d = (s_[0] - X) ** 2 + (s_[1] - Y) ** 2
                if d < bd:
                    bd, best = d, s_
    return best

# ---------------------------------------------------------------- public queries (set frame, old signatures)
def street_polylines():
    return [([M(x, y)[:2] for x, y in pts], hw) for pts, hw, kind in streets_m()]

def on_road(x, y, pad=0.0):
    return on_road_m(x, y - DY, pad)

def nearest_road(x, y, search=3):
    s_ = _nearest_street(x, y - DY, search)
    return M(s_[0], s_[1])[:2] if s_ else min(AVENUE, key=lambda p: (p[0] - x) ** 2 + (p[1] - y) ** 2)

def in_district(x, y, margin=0.0):
    return in_district_m(x, y - DY, margin)

def district_ymin(x, margin=0.0):
    r = R - margin
    return -S - math.sqrt(max(0.0, r * r - x * x))

def in_canal(x, y):
    X, Y = x, y - DY
    return canal_dist_m(X, Y) < 11.5 and in_district_m(X, Y, -5.0)

def ground_z(x, y):
    return ground_z_m(x, y - DY)

def walkable_m(X, Y):
    if abs(X + 140) < 2.5 and 849 <= Y <= 892:                 # inner gate tunnel + the road beyond
        return True
    if Y > 875 and abs(X + 140) < 18 + (Y - 875) * 0.4 and Y < 1010:
        return True
    if abs(X) < 7.0 and -14 <= Y <= 15:                       # outer gate passage / breach
        return True
    if -170 < Y < -6 and abs(X) < 26 + (-6 - Y) * 0.6:        # fields outside the outer gate
        return True
    if 340 <= X <= 385 and 821 <= Y <= 865:                    # cannon basin floor + bank
        return True
    return in_district_m(X, Y, 8.0) and on_road_m(X, Y) and canal_dist_m(X, Y) > 13.0

def walkable(x, y):
    return walkable_m(x, y - DY)

def height_patch(x, y, h):
    """scene.height() hook: the district floor (and square A) follow ground_z_m; outside is untouched."""
    X, Y = x, y - DY
    if wall_dist_m(X, Y) > -2.0 or (-80 < X < 40 and 875 < Y < 990):
        return ground_z_m(X, Y)
    d = math.hypot(x, y + 435.0)
    if d > 1400.0:                                  # owner: no mountains, low hills only
        cap = 6.0 + 24.0 * min(1.0, (d - 1400.0) / 3000.0)
        h = min(h, cap)
    return h

def _install():
    L.W, L.S, L.R = W, S, R
    L.CX, L.CS = 1.0e6, 1                         # scene's own straight canal carve is off; the set builds its canal
    L.CANAL_FAR = WATER_GATE_OUTER
    L.OUTER_GATE = OUTER_GATE
    L.PLAZA = PLAZA
    L.on_road = on_road
    L.street_network = street_polylines
    L.ROADS = None
    L.in_district = in_district
    L.district_ymin = district_ymin

if __name__ != "__main__":
    _install()

# ====================================================================================== material helpers
def lin(h):
    h = h.lstrip("#")
    out = []
    for i in (0, 2, 4):
        c = int(h[i:i + 2], 16) / 255.0
        out.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    return tuple(out)

def _sock(n, ident, inputs=True):
    for s_ in (n.inputs if inputs else n.outputs):
        if s_.identifier == ident:
            return s_
    for s_ in (n.inputs if inputs else n.outputs):
        if s_.name == ident and s_.enabled:
            return s_
    raise KeyError(ident)

class NB:
    """Tiny node-graph builder for Principled materials (keeps toon.py's Principled -> Output contract)."""
    def __init__(s, name, rough=0.88):
        m = bpy.data.materials.new(name); m.use_nodes = True
        s.m = m; s.nt = m.node_tree; s.N = s.nt.nodes; s.Lk = s.nt.links
        s.bsdf = s.N["Principled BSDF"]; s.bsdf.inputs["Roughness"].default_value = rough
        try:
            s.bsdf.inputs["Specular IOR Level"].default_value = 0.25
        except Exception:
            pass
        s.tc = s.N.new("ShaderNodeTexCoord")
        s._oi = None

    def set(s, sock, v):
        if isinstance(v, bpy.types.NodeSocket):
            s.Lk.new(v, sock)
        elif v is not None:
            if isinstance(v, (tuple, list)) and len(v) == 3 and sock.type == "RGBA":
                v = (*v, 1.0)
            sock.default_value = v

    def obj(s, off=None):
        o = s.tc.outputs["Object"]
        if off:
            return s.vmath("ADD", o, off)
        return o

    def rand(s):
        if s._oi is None:
            s._oi = s.N.new("ShaderNodeObjectInfo")
        return s._oi.outputs["Random"]

    def math(s, op, a, b=0.0, c=None, clamp=False):
        n = s.N.new("ShaderNodeMath"); n.operation = op; n.use_clamp = clamp
        s.set(n.inputs[0], a); s.set(n.inputs[1], b)
        if c is not None:
            s.set(n.inputs[2], c)
        return n.outputs[0]

    def vmath(s, op, a, b=None, scale=None):
        n = s.N.new("ShaderNodeVectorMath"); n.operation = op
        s.set(n.inputs[0], a)
        if b is not None:
            s.set(n.inputs[1], b)
        if scale is not None:
            s.set(n.inputs["Scale"], scale)
        return n.outputs["Value"] if op in ("LENGTH", "DOT_PRODUCT", "DISTANCE") else n.outputs["Vector"]

    def sep(s, v):
        n = s.N.new("ShaderNodeSeparateXYZ"); s.set(n.inputs[0], v)
        return n.outputs[0], n.outputs[1], n.outputs[2]

    def comb(s, x, y, z=0.0):
        n = s.N.new("ShaderNodeCombineXYZ")
        s.set(n.inputs[0], x); s.set(n.inputs[1], y); s.set(n.inputs[2], z)
        return n.outputs[0]

    def mix(s, fac, a, b, blend="MIX"):
        n = s.N.new("ShaderNodeMix"); n.data_type = "RGBA"; n.blend_type = blend
        s.set(_sock(n, "Factor_Float"), fac); s.set(_sock(n, "A_Color"), a); s.set(_sock(n, "B_Color"), b)
        return _sock(n, "Result_Color", False)

    def noise(s, vec, scale, detail=4.0, rough=0.5, distort=0.0):
        n = s.N.new("ShaderNodeTexNoise")
        n.inputs["Scale"].default_value = scale; n.inputs["Detail"].default_value = detail
        n.inputs["Roughness"].default_value = rough; n.inputs["Distortion"].default_value = distort
        s.set(n.inputs["Vector"], vec)
        return n

    def vor(s, vec, scale, feature="F1", rand=1.0):
        n = s.N.new("ShaderNodeTexVoronoi"); n.feature = feature
        n.inputs["Scale"].default_value = scale; n.inputs["Randomness"].default_value = rand
        s.set(n.inputs["Vector"], vec)
        return n

    def brick(s, vec, scale, c1, c2, mortar, msize=0.02, bw=0.5, rh=0.25, offset=0.5):
        n = s.N.new("ShaderNodeTexBrick"); n.offset = offset
        n.inputs["Scale"].default_value = scale; n.inputs["Mortar Size"].default_value = msize
        n.inputs["Brick Width"].default_value = bw; n.inputs["Row Height"].default_value = rh
        s.set(n.inputs["Color1"], c1); s.set(n.inputs["Color2"], c2); s.set(n.inputs["Mortar"], mortar)
        s.set(n.inputs["Vector"], vec)
        return n

    def ramp(s, fac, stops, const=False):
        n = s.N.new("ShaderNodeValToRGB")
        if const:
            n.color_ramp.interpolation = "CONSTANT"
        e = n.color_ramp.elements
        for i, (p, c) in enumerate(stops):
            el = e[i] if i < 2 else e.new(p)
            el.position = p; el.color = (*c, 1.0)
        s.set(n.inputs["Fac"], fac)
        return n.outputs["Color"]

    def smooth(s, x, e0, e1):
        n = s.N.new("ShaderNodeMapRange"); n.interpolation_type = "SMOOTHSTEP"
        s.set(n.inputs["Value"], x); n.inputs["From Min"].default_value = e0; n.inputs["From Max"].default_value = e1
        return n.outputs["Result"]

    def gt(s, a, b):
        return s.math("GREATER_THAN", a, b)

    def lt(s, a, b):
        return s.math("LESS_THAN", a, b)

    def band(s, x, period, width, offset=0.0):
        """1 within +-width/2 of every multiple of period (+offset)."""
        f = s.math("FRACT", s.math("DIVIDE", s.math("ADD", x, offset + width / 2.0), period))
        return s.lt(f, width / period)

    def rect(s, X, Y, x0, x1, y0, y1):
        a = s.math("MULTIPLY", s.gt(X, x0), s.lt(X, x1))
        b = s.math("MULTIPLY", s.gt(Y, y0), s.lt(Y, y1))
        return s.math("MULTIPLY", a, b)

    def disc(s, X, Y, cx, cy, r):
        d = s.vmath("LENGTH", s.comb(s.math("SUBTRACT", X, cx), s.math("SUBTRACT", Y, cy), 0.0))
        return s.lt(d, r), d

    def finish(s, col, bump=None, strength=0.25, rough=None):
        s.set(s.bsdf.inputs["Base Color"], col)
        if rough is not None:
            s.set(s.bsdf.inputs["Roughness"], rough)
        if bump is not None:
            b = s.N.new("ShaderNodeBump"); b.inputs["Strength"].default_value = strength
            s.set(b.inputs["Height"], bump); s.Lk.new(b.outputs["Normal"], s.bsdf.inputs["Normal"])
        return s.m

def flat_mat(name, hexcol, rough=0.85, var=0.08, scale=0.4):
    nb = NB(name, rough)
    c = lin(hexcol)
    if var > 0:
        n = nb.noise(nb.obj(), scale, 3.0)
        col = nb.ramp(n.outputs["Fac"], [(0.3, tuple(x * (1 - var) for x in c)), (0.7, tuple(min(1, x * (1 + var)) for x in c))])
    else:
        col = c
    return nb.finish(col)

def stone_mat(name, base, mortar_k=0.86, block=(2.4, 1.2), damp=None, moss=None, damp_z=(6.0, 12.0), var=0.07, rand_tint=0.0,
              damp_k=0.85, damp_streaks=False):
    """Ashlar / wall stone: faint block courses, broad stains, vertical grime streaks, an optional damp (darker, mossy)
    band at the foot (object z).  Block coords use (x + y, z) on walls and (x, y) on tops."""
    nb = NB(name, 0.9)
    c = lin(base)
    o = nb.obj()
    X, Y, Z = nb.sep(o)
    geo = nb.N.new("ShaderNodeNewGeometry")
    nx, ny, nz = nb.sep(geo.outputs["Normal"])
    top = nb.gt(nb.math("ABSOLUTE", nz), 0.7)
    u_side = nb.math("ADD", X, Y)
    uv_side = nb.comb(u_side, Z, 0.0)
    uv_top = nb.comb(X, Y, 0.0)
    m = nb.N.new("ShaderNodeMix"); m.data_type = "VECTOR"
    nb.set(_sock(m, "Factor_Float"), top); nb.set(_sock(m, "A_Vector"), uv_side); nb.set(_sock(m, "B_Vector"), uv_top)
    uv = _sock(m, "Result_Vector", False)
    sc = 0.5 / block[0]
    br = nb.brick(uv, sc, tuple(x * 1.02 for x in c), tuple(x * 0.95 for x in c), tuple(x * mortar_k for x in c),
                  msize=0.012, bw=0.5, rh=0.5 * block[1] / block[0])
    col = br.outputs["Color"]
    st = nb.noise(o, 0.025, 5.0, 0.6)
    col = nb.mix(nb.math("MULTIPLY", nb.smooth(st.outputs["Fac"], 0.45, 0.75), 0.6), col, tuple(x * (1 - var * 2) for x in c))
    sv = nb.vmath("MULTIPLY", o, (0.5, 0.5, 0.04))
    sn = nb.noise(sv, 0.6, 3.0)
    streak = nb.smooth(sn.outputs["Fac"], 0.55, 0.75)
    col = nb.mix(nb.math("MULTIPLY", streak, 0.25), col, tuple(x * 0.7 for x in c))
    if rand_tint > 0:
        col = nb.mix(nb.math("MULTIPLY", nb.rand(), rand_tint), col, tuple(x * 0.82 for x in c))
    if damp:
        dn = nb.noise(o, 0.15, 3.0)
        zz = nb.math("ADD", Z, nb.math("MULTIPLY", nb.math("SUBTRACT", dn.outputs["Fac"], 0.5), 5.0))
        f = nb.math("SUBTRACT", 1.0, nb.smooth(zz, damp_z[0], damp_z[1]))
        if damp_streaks:                                      # damp runs up in vertical streaks above the band
            dsv = nb.vmath("MULTIPLY", o, (0.9, 0.9, 0.035))
            dsn = nb.noise(dsv, 0.9, 3.0)
            reach = nb.math("SUBTRACT", 1.0, nb.smooth(Z, damp_z[1], damp_z[1] + 9.0))
            fs = nb.math("MULTIPLY", nb.smooth(dsn.outputs["Fac"], 0.55, 0.68), reach)
            f = nb.math("MAXIMUM", f, nb.math("MULTIPLY", fs, 0.8))
        col = nb.mix(nb.math("MULTIPLY", f, damp_k), col, lin(damp))
        if moss:
            mv = nb.vmath("MULTIPLY", o, (0.8, 0.8, 0.08))
            mn = nb.noise(mv, 1.2, 4.0)
            mf = nb.math("MULTIPLY", nb.smooth(mn.outputs["Fac"], 0.5, 0.65), f)
            col = nb.mix(nb.math("MULTIPLY", mf, 0.7), col, lin(moss))
    return nb.finish(col, bump=br.outputs["Fac"], strength=0.15)

def brick_mat(name, base="#8a4f3c", mortar="#b8aa92", scale=4.0):
    nb = NB(name, 0.9)
    c = lin(base)
    o = nb.obj()
    X, Y, Z = nb.sep(o)
    uv = nb.comb(nb.math("ADD", X, Y), Z, 0.0)
    br = nb.brick(uv, scale, tuple(x * 1.06 for x in c), tuple(x * 0.86 for x in c), lin(mortar), msize=0.06, bw=0.5, rh=0.22)
    n = nb.noise(o, 0.08, 4.0)
    col = nb.mix(nb.math("MULTIPLY", n.outputs["Fac"], 0.35), br.outputs["Color"], tuple(x * 0.7 for x in c))
    return nb.finish(col, bump=br.outputs["Fac"], strength=0.2)

def plank_mat(name, base="#3b2f25", vertical=True, post_every=2.0):
    nb = NB(name, 0.9)
    c = lin(base)
    o = nb.obj()
    X, Y, Z = nb.sep(o)
    u = nb.math("ADD", X, Y)
    lines = nb.band(u if vertical else Z, 0.35, 0.05)
    posts = nb.band(u, post_every, 0.22)
    n = nb.noise(nb.vmath("MULTIPLY", o, (0.3, 0.3, 3.0) if not vertical else (3.0, 3.0, 0.3)), 1.0, 3.0)
    col = nb.mix(nb.math("MULTIPLY", n.outputs["Fac"], 0.5), tuple(x * 1.15 for x in c), tuple(x * 0.8 for x in c))
    col = nb.mix(nb.math("MULTIPLY", nb.math("MAXIMUM", lines, posts), 0.6), col, tuple(x * 0.45 for x in c))
    return nb.finish(col, bump=lines, strength=0.2)

def roof_mat(name, tones, var_rows=True):
    """Clay-tile roof: tile rows, per-tile shade and a per-house tone (ObjectInfo Random picks from `tones`)."""
    nb = NB(name, 0.8)
    o = nb.obj()
    X, Y, Z = nb.sep(o)
    rnd = nb.rand()
    stops = [(i / max(1, len(tones) - 1), lin(h)) for i, h in enumerate(tones)]
    base = nb.ramp(rnd, stops, const=False)
    vo = nb.vor(nb.vmath("MULTIPLY", o, (2.6, 2.6, 2.2)), 1.0, "F1", 0.2)
    sh = nb.math("ADD", 0.85, nb.math("MULTIPLY", vo.outputs["Distance"], 0.35))
    col = nb.mix(1.0, base, nb.comb(sh, sh, sh), "MULTIPLY")
    rows = nb.band(Z, 0.42, 0.07)
    col = nb.mix(nb.math("MULTIPLY", rows, 0.45), col, (0.12, 0.08, 0.07))
    big = nb.noise(o, 0.12, 3.0)
    col = nb.mix(nb.math("MULTIPLY", big.outputs["Fac"], 0.25), col, (0.10, 0.09, 0.08), "MIX")
    return nb.finish(col, bump=vo.outputs["Distance"], strength=0.3)

def facade_mat(name, wall_hex, timber=False, gf="stone", timber_hex="#4a3427", gf_hex="#9b9486", rand_tint=0.10):
    """House facade (instanced terraces): window grid, optional half-timber upper storeys, ground-floor style
    (stone doors / shop arches / arcade).  Local object coords: base at z 0, ground floor 0..3.6, storeys 3.2 m."""
    nb = NB(name, 0.9)
    o = nb.obj()
    X, Y, Z = nb.sep(o)
    nx, ny, nz = nb.sep(nb.tc.outputs["Normal"])
    sel = nb.gt(nb.math("ABSOLUTE", ny), nb.math("ABSOLUTE", nx))
    h = nb.math("ADD", nb.math("MULTIPLY", X, sel), nb.math("MULTIPLY", Y, nb.math("SUBTRACT", 1.0, sel)))
    wc = lin(wall_hex)
    rt = nb.rand()
    wallc = nb.mix(nb.math("MULTIPLY", rt, rand_tint * 2), tuple(min(1, x * 1.06) for x in wc), tuple(x * 0.86 for x in wc))
    dirt = nb.noise(o, 0.35, 3.0)
    wallc = nb.mix(nb.math("MULTIPLY", nb.smooth(dirt.outputs["Fac"], 0.5, 0.8), 0.3), wallc, tuple(x * 0.7 for x in wc))
    up = nb.gt(Z, 3.6)
    # windows
    wu = nb.math("FRACT", nb.math("DIVIDE", nb.math("ADD", h, 1.2), 2.4))
    win_u = nb.lt(nb.math("ABSOLUTE", nb.math("SUBTRACT", wu, 0.5)), 0.16)
    wv = nb.math("FRACT", nb.math("DIVIDE", nb.math("SUBTRACT", Z, 3.6), 3.2))
    win_v = nb.math("MULTIPLY", nb.gt(wv, 0.28), nb.lt(wv, 0.7))
    win = nb.math("MULTIPLY", nb.math("MULTIPLY", win_u, win_v), up)
    col = wallc
    if timber:
        tc = lin(timber_hex)
        hb = nb.band(nb.math("SUBTRACT", Z, 3.6), 3.2, 0.26)
        post = nb.band(h, 2.4, 0.22, offset=1.2)
        zr = nb.math("FRACT", nb.math("DIVIDE", nb.math("SUBTRACT", Z, 3.6), 3.2))
        brace = nb.math("MULTIPLY", nb.band(nb.math("ADD", h, nb.math("MULTIPLY", zr, 2.4)), 2.4, 0.2),
                        nb.math("MULTIPLY", nb.lt(zr, 0.22), 1.0))
        beam = nb.math("MULTIPLY", nb.math("MAXIMUM", nb.math("MAXIMUM", hb, post), brace), up)
        col = nb.mix(beam, col, tc)
    else:
        sill = nb.math("MULTIPLY", nb.band(nb.math("SUBTRACT", Z, 3.6), 3.2, 0.18), up)
        col = nb.mix(nb.math("MULTIPLY", sill, 0.35), col, tuple(x * 0.72 for x in wc))
    col = nb.mix(nb.math("MULTIPLY", win, 0.85), col, lin("#34302f"))
    # ground floor
    gc = lin(gf_hex) if gf != "shop" else wc
    gcol = gc
    period, hw_, spring = {"stone": (4.8, 0.7, 2.2), "shop": (4.8, 1.2, 2.0), "arcade": (4.0, 1.45, 2.1)}[gf]
    u = nb.math("MULTIPLY", nb.math("SUBTRACT", nb.math("FRACT", nb.math("DIVIDE", h, period)), 0.5), period)
    inside_rect = nb.math("MULTIPLY", nb.lt(nb.math("ABSOLUTE", u), hw_), nb.lt(Z, spring))
    dd = nb.math("ADD", nb.math("MULTIPLY", u, u), nb.math("MULTIPLY", nb.math("SUBTRACT", Z, spring), nb.math("SUBTRACT", Z, spring)))
    inside_arch = nb.math("MULTIPLY", nb.lt(dd, hw_ * hw_), nb.gt(Z, spring))
    arch = nb.math("MULTIPLY", nb.math("MAXIMUM", inside_rect, inside_arch), nb.gt(Z, 0.0))
    if gf == "arcade":
        gcol = nb.mix(arch, gc, lin("#2a2420"))
    else:
        gcol = nb.mix(arch, gc, lin("#3a2e26" if gf == "stone" else "#2f2a26"))
    col = nb.mix(nb.math("SUBTRACT", 1.0, up), col, gcol)
    return nb.finish(col)

def ground_mat(name, yoff):
    """The town floor: pale cobbles everywhere, with the bible's paved / turf / earth areas as smooth masks (M coords:
    object coords + (0, yoff, 0))."""
    nb = NB(name, 0.95)
    o = nb.obj((0.0, yoff, 0.0)) if yoff else nb.obj()
    X, Y, Z = nb.sep(o)
    # cobbles
    vo = nb.vor(o, 1.7, "F1", 1.0)
    ve = nb.vor(o, 1.7, "DISTANCE_TO_EDGE", 1.0)
    rs, gs, bs = nb.sep(vo.outputs["Color"])
    cob = nb.ramp(rs, [(0.0, lin("#a69882")), (1.0, lin("#c4b79b"))])
    joint = nb.smooth(ve.outputs["Distance"], 0.02, 0.08)
    cob = nb.mix(joint, lin("#857862"), cob)
    big = nb.noise(o, 0.02, 4.0)
    cob = nb.mix(nb.math("MULTIPLY", nb.smooth(big.outputs["Fac"], 0.45, 0.7), 0.35), cob, lin("#9c8c70"))
    col = cob
    # large setts (paved squares)
    def setts(hexc, scale=0.9):
        c = lin(hexc)
        b = nb.brick(nb.comb(X, Y, 0.0), 1.0 / scale * 0.5, tuple(x * 1.04 for x in c), tuple(x * 0.93 for x in c),
                     tuple(x * 0.8 for x in c), msize=0.03, bw=0.5, rh=0.25)
        vn = nb.vor(nb.comb(X, Y, 0.0), 1.3, "F1", 1.0)
        rr, gg, bb_ = nb.sep(vn.outputs["Color"])
        return nb.mix(nb.math("MULTIPLY", rr, 0.45), b.outputs["Color"], tuple(x * 0.72 for x in c))
    # avenue (lighter cobbles)
    dav = None
    for k in range(len(AV_PTS) - 1):
        ax, ay = AV_PTS[k]; bx, by = AV_PTS[k + 1]
        p = nb.comb(nb.math("SUBTRACT", X, ax), nb.math("SUBTRACT", Y, ay), 0.0)
        ab = (bx - ax, by - ay, 0.0)
        t = nb.math("DIVIDE", nb.vmath("DOT_PRODUCT", p, ab), ab[0] ** 2 + ab[1] ** 2, clamp=False)
        t = nb.math("MINIMUM", nb.math("MAXIMUM", t, 0.0), 1.0)
        q = nb.vmath("SUBTRACT", p, nb.vmath("SCALE", ab, scale=t))
        d = nb.vmath("LENGTH", q)
        dav = d if dav is None else nb.math("MINIMUM", dav, d)
    col = nb.mix(nb.lt(dav, 7.0), col, nb.mix(0.55, cob, lin("#c8bb9c")))
    pale = setts("#cdbf9f")
    mC, dC = nb.disc(X, Y, -60.0, 470.0, 45.0)
    col = nb.mix(mC, col, pale)
    col = nb.mix(nb.math("MAXIMUM", nb.rect(X, Y, -275, -100, 570, 624), nb.rect(X, Y, -300, -266, 570, 660)), col, pale)
    col = nb.mix(nb.rect(X, Y, -65, 25, 905, 965), col, pale)
    col = nb.mix(nb.rect(X, Y, -178, -102, 800, 853), col, setts("#6f6c66", 0.7))
    col = nb.mix(nb.rect(X, Y, -252, -222, 490, 520), col, setts("#cfc4a8", 1.1))
    col = nb.mix(nb.rect(X, Y, -266.5, -257.5, 380, 458), col, setts("#6e6d68", 0.8))
    # earth: the SE wall-foot strip, the decoy pocket D
    gn = nb.noise(o, 0.09, 4.0)
    earth = nb.mix(nb.smooth(gn.outputs["Fac"], 0.5, 0.62), lin("#8a7a5c"), lin("#5f7a3e"))
    rP, dP = nb.disc(X, Y, 0.0, 480.0, 437.0)
    strip = nb.math("MULTIPLY", nb.gt(dP, 435.0), nb.lt(Y, 470.0))
    ang = nb.math("ARCTAN2", X, nb.math("SUBTRACT", 480.0, Y))
    strip = nb.math("MULTIPLY", strip, nb.math("MULTIPLY", nb.gt(ang, math.radians(6.5)), nb.lt(ang, math.radians(38.5))))
    col = nb.mix(strip, col, earth)
    col = nb.mix(nb.math("MULTIPLY", nb.lt(X, -400.0), nb.gt(Y, 790.0)), col, nb.mix(0.4, earth, lin("#7d6e55")))
    # gate square: turf + worn earth, pale ring road
    mGS, dO = nb.disc(X, Y, 0.0, 0.0, 70.0)
    gsm = nb.math("MULTIPLY", mGS, nb.gt(Y, -2.0))
    tn = nb.noise(o, 0.07, 5.0, 0.6)
    worn = nb.smooth(tn.outputs["Fac"], 0.48, 0.6)
    pth, dpth = nb.disc(X, Y, -26.0, 63.0, 7.0)
    turf = nb.mix(nb.math("MAXIMUM", worn, nb.math("MULTIPLY", pth, 0.8)), lin("#6f8a4c"), lin("#8a7a5c"))
    fine = nb.noise(o, 0.9, 3.0)
    turf = nb.mix(nb.math("MULTIPLY", fine.outputs["Fac"], 0.3), turf, lin("#4f6a35"))
    col = nb.mix(gsm, col, turf)
    ring = nb.math("MULTIPLY", nb.math("MULTIPLY", nb.gt(dO, 70.0), nb.lt(dO, 78.0)), nb.gt(Y, -2.0))
    col = nb.mix(ring, col, setts("#cdbf9f", 1.2))
    # inner gate: grass slope east of the bastion, paved terrace below it
    grass = nb.mix(nb.math("MULTIPLY", fine.outputs["Fac"], 0.5), lin("#5f7344"), lin("#4a5c36"))
    col = nb.mix(nb.rect(X, Y, -105, -60, 840, 868), col, grass)
    col = nb.mix(nb.rect(X, Y, -105, -60, 820, 840), col, setts("#b9ab8f", 0.9))
    return nb.finish(col, bump=joint, strength=0.12)

def water_mat(name="CanalWater"):
    nb = NB(name, 0.18)
    o = nb.obj()
    n = nb.noise(o, 0.05, 3.0)
    col = nb.mix(nb.smooth(n.outputs["Fac"], 0.4, 0.65), lin("#4e6e62"), lin("#6f9a7c"))
    fn = nb.noise(o, 1.2, 2.0)
    return nb.finish(col, bump=fn.outputs["Fac"], strength=0.05)

def marble_mat(name="TrostBoulderMarble"):
    """The ball (owner 15:29, bible g8): warm grey #8f8a82, large dark charcoal marbling #3b3a3a, pale weathered patches
    #c9c4b8, a fine black crack network #2a2826; roughness 0.85, no highlight."""
    nb = NB(name, 0.85)
    try:
        nb.bsdf.inputs["Specular IOR Level"].default_value = 0.05
    except Exception:
        pass
    o = nb.obj()
    base = lin("#8f8a82")
    n1 = nb.noise(o, 0.35, 8.0, 0.62)
    col = nb.mix(nb.smooth(n1.outputs["Fac"], 0.3, 0.72), tuple(x * 0.74 for x in base), tuple(x * 1.06 for x in base))
    pale = nb.noise(o, 0.1, 4.0)
    col = nb.mix(nb.math("MULTIPLY", nb.smooth(pale.outputs["Fac"], 0.56, 0.68), 0.6), col, lin("#c9c4b8"))
    # marbling: a warped voronoi edge network (dark charcoal veins), thick where a slow noise says so
    warp = nb.vmath("ADD", o, nb.vmath("SCALE", nb.noise(o, 0.22, 4.0).outputs["Color"], scale=6.0))
    vv = nb.vor(warp, 0.16, "DISTANCE_TO_EDGE", 1.0)
    thick = nb.math("MULTIPLY", nb.smooth(nb.noise(o, 0.15, 2.0).outputs["Fac"], 0.45, 0.7), 0.07)
    vein = nb.math("SUBTRACT", 1.0, nb.smooth(nb.math("DIVIDE", vv.outputs["Distance"], thick), 0.2, 1.0))
    blot = nb.smooth(nb.noise(o, 0.13, 5.0, 0.6).outputs["Fac"], 0.6, 0.72)
    col = nb.mix(nb.math("MULTIPLY", nb.math("MAXIMUM", vein, blot), 0.7), col, lin("#3b3a3a"))
    wp = nb.vmath("ADD", o, nb.vmath("SCALE", nb.noise(o, 0.5, 3.0).outputs["Color"], scale=2.0))
    cr = nb.vor(wp, 0.7, "DISTANCE_TO_EDGE", 1.0)
    crack = nb.math("SUBTRACT", 1.0, nb.smooth(cr.outputs["Distance"], 0.0, 0.02))
    cn = nb.noise(o, 0.3, 2.0)
    crack = nb.math("MULTIPLY", crack, nb.smooth(cn.outputs["Fac"], 0.4, 0.55))
    col = nb.mix(nb.math("MULTIPLY", crack, 0.6), col, lin("#2a2826"))
    fn = nb.noise(o, 2.5, 6.0)
    bump = nb.math("SUBTRACT", fn.outputs["Fac"], nb.math("MULTIPLY", nb.math("ADD", crack, vein), 0.5))
    return nb.finish(col, bump=bump, strength=0.4)

def rock_mat(name="TrostRock", hexc="#4a4a48"):
    nb = NB(name, 0.95)
    o = nb.obj()
    c = lin(hexc)
    n1 = nb.noise(o, 0.4, 8.0, 0.6)
    col = nb.mix(n1.outputs["Fac"], tuple(x * 0.72 for x in c), tuple(min(1, x * 1.25) for x in c))
    geo = nb.N.new("ShaderNodeNewGeometry")
    nx, ny, nz = nb.sep(geo.outputs["Normal"])
    col = nb.mix(nb.math("MULTIPLY", nb.smooth(nz, 0.5, 0.9), 0.35), col, tuple(min(1, x * 1.4) for x in c))
    return nb.finish(col, bump=n1.outputs["Fac"], strength=0.5)

def emit_mat(name, hexc, strength=4.0, alpha_grad=False):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; N = nt.nodes
    N.remove(N["Principled BSDF"])
    em = N.new("ShaderNodeEmission"); em.inputs["Color"].default_value = (*lin(hexc), 1); em.inputs["Strength"].default_value = strength
    em.name = "Glow"
    if alpha_grad:
        tc = N.new("ShaderNodeTexCoord"); sep = N.new("ShaderNodeSeparateXYZ"); nt.links.new(tc.outputs["Generated"], sep.inputs[0])
        rp = N.new("ShaderNodeValToRGB"); e = rp.color_ramp.elements
        e[0].position, e[0].color = 0.0, (1, 1, 1, 1); e[1].position, e[1].color = 1.0, (0, 0, 0, 1)
        nt.links.new(sep.outputs["Z"], rp.inputs[0])
        tr = N.new("ShaderNodeBsdfTransparent")
        mx = N.new("ShaderNodeMixShader")
        nt.links.new(rp.outputs["Color"], mx.inputs[0]); nt.links.new(tr.outputs[0], mx.inputs[1]); nt.links.new(em.outputs[0], mx.inputs[2])
        nt.links.new(mx.outputs[0], N["Material Output"].inputs["Surface"])
        try:
            m.surface_render_method = "BLENDED"
        except Exception:
            pass
    else:
        nt.links.new(em.outputs[0], N["Material Output"].inputs["Surface"])
    m["toon"] = 1
    return m

def _materials(MT):
    """Trost materials (added to scene.py's dict)."""
    if MT.get("_trost_mats"):
        return MT
    MT["_trost_mats"] = True
    # QA 10/26 (g8 agent): the toon pass multiplies the base by its light band and AgX desaturates it, so #cec3a6 rendered
    # flat pale grey-white; the base is pre-warmed so the lit wall READS #CEC3A6 on screen, with a darker damp, mossy foot
    # (#6f6a58 streaks up to 6-12 m) and lighter pilasters so their shading reads against the recessed panels.
    MT["wall_t"] = stone_mat("TrostWallStone", "#c3b18c", damp="#6f6a58", moss="#4f5a36", damp_z=(6.0, 12.0), damp_k=0.95,
                             damp_streaks=True)
    MT["pilaster"] = stone_mat("TrostPilaster", "#d8caa6", damp="#77705d", moss="#4f5a36", damp_z=(5.0, 10.0), damp_k=0.9,
                               damp_streaks=True)
    MT["walk_brick"] = brick_mat("TrostWalkBrick", "#8e5a48", "#6e4a3c", scale=1.6)
    MT["walk_lime"] = stone_mat("TrostWalkLime", "#cfc4a8", block=(1.6, 1.6))
    MT["gh_brick"] = brick_mat("TrostGateBrick", "#8a4f3c", "#b8aa92", scale=3.0)
    MT["cornice"] = stone_mat("TrostCornice", "#cfc3a6", block=(1.6, 0.8))
    MT["sandstone"] = stone_mat("TrostSandstone", "#c9b48e", damp="#8a7a62", damp_z=(3.0, 7.0))
    MT["iron_rust"] = flat_mat("TrostIronRust", "#7a3a24", 0.6, 0.15, 0.8)
    MT["iron_t"] = flat_mat("TrostIron", "#1e1c1c", 0.5, 0.05)
    MT["timber_d"] = plank_mat("TrostTimberDark", "#3b2f25")
    MT["plank_t"] = plank_mat("TrostPlankTan", "#9a7a55")
    MT["plank_h"] = plank_mat("TrostPlankH", "#3b2f25", vertical=False)
    MT["crate_t"] = flat_mat("TrostCrate", "#a88a62", 0.85, 0.1, 1.5)
    MT["window_t"] = flat_mat("TrostWindow", "#2b2a2e", 0.6, 0.0)
    MT["stone_dark"] = flat_mat("TrostStoneDark", "#4a4a48", 0.9, 0.1, 0.8)
    MT["bollard"] = flat_mat("TrostBollard", "#55524e", 0.9, 0.08, 1.0)
    MT["mud"] = flat_mat("TrostMud", "#3b3228", 0.9, 0.12, 0.3)
    MT["puddle"] = flat_mat("TrostPuddle", "#26302e", 0.15, 0.0)
    MT["turf_t"] = flat_mat("TrostTurf", "#6f8a4c", 0.95, 0.12, 0.2)
    MT["lawn"] = flat_mat("TrostLawn", "#6f8a4c", 0.95, 0.14, 0.4)
    MT["shrub"] = flat_mat("TrostShrub", "#3f5530", 0.9, 0.15, 0.8)
    MT["spruce"] = flat_mat("TrostSpruce", "#24331f", 0.9, 0.12, 0.6)
    MT["leafy"] = flat_mat("TrostLeafy", "#3d5a2c", 0.9, 0.15, 0.6)
    MT["tree_dark"] = flat_mat("TrostTreeDark", "#2f3b26", 0.9, 0.12, 0.6)
    MT["bark_t"] = flat_mat("TrostBark", "#3a2c22", 0.9, 0.1)
    MT["rubble_brick"] = flat_mat("TrostRubbleBrick", "#8d4b3a", 0.9, 0.15, 1.0)
    MT["rubble_stone"] = flat_mat("TrostRubbleStone", "#8e8a80", 0.9, 0.12, 1.0)
    MT["rubble_dark"] = flat_mat("TrostRubbleDark", "#5e3428", 0.9, 0.15, 1.0)
    MT["timber_split"] = flat_mat("TrostTimberSplit", "#4a3424", 0.9, 0.18, 1.2)
    MT["contact_dark"] = flat_mat("TrostBallContact", "#2e2a24", 0.95, 0.0)
    MT["contact_mid"] = flat_mat("TrostBallContactMid", "#4f483c", 0.95, 0.0)
    MT["dust_ring"] = flat_mat("TrostBallDust", "#9a8b6c", 0.95, 0.15, 0.6)
    MT["rock_court"] = rock_mat("TrostRockCourt", "#4a4a48")
    MT["rock_pale"] = rock_mat("TrostRockPale", "#8a867e")
    MT["rock2"] = rock_mat("TrostRock2", "#77726a")
    MT["tendril"] = flat_mat("TrostTendril", "#2a1f1b", 0.8, 0.15, 0.6)
    MT["vine"] = flat_mat("TrostVine", "#3a2e26", 0.9, 0.1)
    MT["glow"] = emit_mat("TrostBreachGlow", "#ff8a3a", 3.0, alpha_grad=True)
    MT["ball"] = marble_mat()
    MT["water_c"] = water_mat()
    MT["bank"] = stone_mat("TrostCanalBank", "#a9a291", damp="#6f6a58", moss="#4e5a3a", damp_z=(-4.5, -1.2))
    MT["quay"] = stone_mat("TrostQuay", "#bdb5a0", block=(1.2, 0.6))
    MT["canal_bed"] = flat_mat("TrostCanalBed", "#2e352e", 0.9, 0.0)
    MT["ground_set"] = ground_mat("TrostGround", -DY)
    MT["ground_m"] = ground_mat("TrostGroundM", 0.0)
    MT["flag_green"] = flat_mat("TrostFlagGreen", "#2f5a34", 0.8, 0.05)
    MT["roof_red_t"] = roof_mat("TrostRoofRed", ["#b4532f", "#a2472a"])
    MT["roof_slate_t"] = roof_mat("TrostRoofSlate", ["#56606c", "#4f5a66"])
    MT["roof_copper"] = roof_mat("TrostRoofCopper", ["#8e5a38", "#7a4e34"])
    MT["roof_town"] = roof_mat("TrostRoofTown", ["#b8643d", "#a85234", "#9a4630", "#8e4a30", "#a85234", "#b06a48", "#6e3b28"])
    MT["roof_civic"] = roof_mat("TrostRoofCivic", ["#4f5a66", "#56606c"])
    MT["tower_cream"] = stone_mat("TrostTowerCream", "#d6c7a2", block=(1.6, 0.8), damp="#a59878", damp_z=(1.0, 5.0))
    MT["tower_brick"] = brick_mat("TrostTowerBrick", "#8a5a40", "#a89878", scale=3.0)
    for k, (wh, tim, gf, gfh) in {
            "f_cream": ("#d8cbb0", False, "stone", "#9b9486"), "f_sand": ("#c9b48e", False, "shop", "#9b9486"),
            "f_grey": ("#9b9486", False, "stone", "#7f7a70"), "f_tcream": ("#dccfb2", True, "stone", "#9b9486"),
            "f_tochre": ("#d1b98a", True, "shop", "#8f8a80"), "f_arc_cream": ("#d8cbb0", False, "arcade", "#c9bfa6"),
            "f_arc_sand": ("#c9b48e", False, "arcade", "#bfb293"), "f_arc_timber": ("#dccfb2", True, "arcade", "#c9bfa6"),
            "f_brick": ("#9a6248", False, "stone", "#8f8a80")}.items():
        MT[k] = facade_mat("Trost_" + k, wh, timber=tim, gf=gf, gf_hex=gfh)
    MT["chimney"] = brick_mat("TrostChimney", "#7a4a38", "#9a8a70", scale=4.0)
    return MT

# ====================================================================================== mesh helpers
box, cyl = L.box, L.cyl

def _mk(name, bm, mats, coll=None):
    """Object from a bmesh authored in M coordinates (placed at the set offset)."""
    ob = L.obj_from_bm(name, bm, mats, coll)
    ob.location = (0.0, DY, 0.0)
    return ob

def _mk_at(name, bm, mats, xyz_m, coll=None, rot=0.0):
    """Object from a bmesh authored in LOCAL coordinates, origin placed at an M position."""
    ob = L.obj_from_bm(name, bm, mats, coll)
    ob.location = M(*xyz_m)
    ob.rotation_euler.z = rot
    return ob

def hexa(bm, pts8, mi=0):
    """Hexahedron from 8 corners: bottom quad then top quad (same order); winding is fixed to ccw automatically."""
    b = pts8[:4]
    area = sum(b[i][0] * b[(i + 1) % 4][1] - b[(i + 1) % 4][0] * b[i][1] for i in range(4))
    if area < 0:
        pts8 = [pts8[0], pts8[3], pts8[2], pts8[1], pts8[4], pts8[7], pts8[6], pts8[5]]
    v = [bm.verts.new(p) for p in pts8]
    for f in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
        bm.faces.new([v[i] for i in f]).material_index = mi

def obox(bm, c, t, n, along, across, z0, z1, mi=0, across0=None):
    """Box oriented by tangent t / normal n (2D unit Vectors) at centre c (2D): `along` x `across` x (z0..z1).
    across0: optional (a0, a1) offsets along n instead of a symmetric `across`."""
    a0, a1 = across0 if across0 else (-across / 2, across / 2)
    pts = []
    for z in (z0, z1):
        for sa, sn in ((-1, a0), (1, a0), (1, a1), (-1, a1)):
            p = c + t * (sa * along / 2) + n * sn
            pts.append((p.x, p.y, z))
    hexa(bm, pts, mi)

def tube(bm, pts, r0, r1, seg=5, mi=0):
    """Tapered tube along a 3D polyline (for tendrils / vines / roots)."""
    pts = [Vector(p) for p in pts]
    n = len(pts)
    rings = []
    for k, p in enumerate(pts):
        a = pts[max(k - 1, 0)]; b = pts[min(k + 1, n - 1)]
        d = (b - a).normalized()
        up = Vector((0, 0, 1)) if abs(d.z) < 0.9 else Vector((1, 0, 0))
        u = d.cross(up).normalized(); w = d.cross(u).normalized()
        r = r0 + (r1 - r0) * k / max(1, n - 1)
        rings.append([bm.verts.new(p + (u * math.cos(j * math.tau / seg) + w * math.sin(j * math.tau / seg)) * r) for j in range(seg)])
    for k in range(n - 1):
        for j in range(seg):
            bm.faces.new((rings[k][j], rings[k][(j + 1) % seg], rings[k + 1][(j + 1) % seg], rings[k + 1][j])).material_index = mi
    return rings

def rock_blob(bm, c, size, rnd, sub=1, mi=0, sq=0.75, jag=0.25):
    r = bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=1.0)
    sx, sy, sz = size
    off = Vector((rnd.uniform(0, 50), rnd.uniform(0, 50), rnd.uniform(0, 50)))
    for v in r["verts"]:
        nn = v.co.normalized()
        d = 1.0 + jag * noise.noise(nn * 1.7 + off)
        v.co = Vector((nn.x * sx * d, nn.y * sy * d, nn.z * sz * d * sq)) + Vector(c)
    for f in {f for v in r["verts"] for f in v.link_faces}:
        f.material_index = mi
    return r

def _coll(name, parent=None):
    c = bpy.data.collections.get(name)
    if c is None:
        c = L.new_coll(name, parent)
    return c

def _hide(ob, hidden=True):
    if ob:
        ob.hide_render = ob.hide_viewport = bool(hidden)

def _ball_contact(name, xy, z, MT, front_only=False, coll=None):
    """QA 10/26 (P2): a darker contact patch (r 2.6 / 4.2) + a pale dust ring (r 6.6-8.8) under the ball so it reads heavy.
    Flat decals (no toon ink: the name has no Gate/Boulder key).  front_only: the dust ring only on the town side (Y+)."""
    bm = bmesh.new()
    cx, cy = xy
    def ring(r0, r1, z_, mi, a0=0.0, a1=math.tau, seg=40, jag=0.0, seed=1):
        rr = random.Random(seed)
        for q in range(seg):
            u0 = a0 + (a1 - a0) * q / seg; u1 = a0 + (a1 - a0) * (q + 1) / seg
            j0 = 1 + jag * rr.uniform(-1, 1); j1 = 1 + jag * rr.uniform(-1, 1)
            ps = [(cx + math.cos(u0) * r0, cy + math.sin(u0) * r0), (cx + math.cos(u1) * r0, cy + math.sin(u1) * r0),
                  (cx + math.cos(u1) * r1 * j1, cy + math.sin(u1) * r1 * j1), (cx + math.cos(u0) * r1 * j0, cy + math.sin(u0) * r1 * j0)]
            if r0 <= 0.01:
                ps = [ps[0], ps[2], ps[3]]
            bm.faces.new([bm.verts.new((x, y, z_)) for x, y in ps]).material_index = mi
    a0, a1 = (0.0, math.pi) if front_only else (0.0, math.tau)
    ring(0.0, 2.6, z + 0.06, 0, seg=24)
    ring(2.6, 4.2, z + 0.05, 1, seg=32)
    ring(6.6, 8.8, z + 0.04, 2, a0, a1, seg=44, jag=0.18, seed=7)
    ob = _mk(name, bm, [MT["contact_dark"], MT["contact_mid"], MT["dust_ring"]], coll)
    ob.visible_shadow = False
    return ob

# ====================================================================================== terrain + town floor
def _axis(fine0, fine1, step, lo, hi, grow=1.25, cap=400.0):
    xs = [fine0 + k * step for k in range(int(round((fine1 - fine0) / step)) + 1)]
    a, s_ = fine0, step
    while a > lo:
        s_ = min(cap, s_ * grow); a -= s_; xs.insert(0, max(lo, a))
    a, s_ = fine1, step
    while a < hi:
        s_ = min(cap, s_ * grow); a += s_; xs.append(min(hi, a))
    return xs

def _hole_m(X, Y):
    """Town-floor faces removed here (the pit, craters, holes, canal, basin are their own geometry)."""
    if math.hypot(X - PIT_C[0], Y - PIT_C[1]) < 24.3:
        return True
    for cx, cy, r in CRATERS_M:
        if math.hypot(X - cx, Y - cy) < r + 0.1:
            return True
    for cx, cy, r in HOLES_M:
        if math.hypot(X - cx, Y - cy) < r + 0.1:
            return True
    if canal_dist_m(X, Y) < 13.05:
        return True
    if 340.0 < X < 385.0 and 821.0 < Y < 866.0:
        return True
    return False

def build_terrain_trost(MT):
    """Terrain + town floor as ONE tensor-grid mesh in SET coordinates (5 m cells over Trost, graded out to 9 km) so the
    floor has no z-fighting with a second ground; material 0 = scene meadow, 1 = Trost town floor (masks in M)."""
    t0 = time.time()
    xs = _axis(-600.0, 840.0, 5.0, -9000.0, 9000.0)
    ys = _axis(-140.0 + DY, 990.0 + DY, 5.0, -9000.0, 9000.0)
    nx, ny = len(xs), len(ys)
    H = [[L.height(x, y) for y in ys] for x in xs]
    verts = [(xs[i], ys[j], H[i][j]) for i in range(nx) for j in range(ny)]
    HO = [[(-30 < x < 800 and -30 < y - DY < 880 and _hole_m(x, y - DY)) for y in ys] for x in xs]
    faces, mats = [], []
    for i in range(nx - 1):
        for j in range(ny - 1):
            x0, x1, y0, y1 = xs[i], xs[i + 1], ys[j] - DY, ys[j + 1] - DY
            if HO[i][j] or HO[i + 1][j] or HO[i][j + 1] or HO[i + 1][j + 1]:
                continue
            cxm, cym = (x0 + x1) / 2, (y0 + y1) / 2
            faces.append((i * ny + j, (i + 1) * ny + j, (i + 1) * ny + j + 1, i * ny + j + 1))
            mats.append(1 if (wall_dist_m(cxm, cym) > 2.0 or (-65 < cxm < 25 and 905 < cym < 965)) else 0)
    me = bpy.data.meshes.new("Terrain")
    me.from_pydata(verts, [], faces)
    me.polygons.foreach_set("material_index", mats)
    try:
        me.polygons.foreach_set("use_smooth", [m_ == 0 for m_ in mats])
    except Exception:
        pass
    me.materials.append(L.terrain_mat()); me.materials.append(MT["ground_set"])
    ob = bpy.data.objects.new("Terrain", me); bpy.context.scene.collection.objects.link(ob)
    print(f"[trost] terrain {len(faces)} faces ({nx}x{ny}) {time.time() - t0:.1f}s", flush=True)
    return ob

def fill_ring(bm, c, r0, r1, z, seg=48, mi=0):
    vs0 = [bm.verts.new((c[0] + r0 * math.cos(k * math.tau / seg), c[1] + r0 * math.sin(k * math.tau / seg), z)) for k in range(seg)]
    vs1 = [bm.verts.new((c[0] + r1 * math.cos(k * math.tau / seg), c[1] + r1 * math.sin(k * math.tau / seg), z)) for k in range(seg)]
    for k in range(seg):
        bm.faces.new((vs0[k], vs1[k], vs1[(k + 1) % seg], vs0[(k + 1) % seg])).material_index = mi

def fill_disc(bm, c, r, z, seg=32, mi=0):
    vs = [bm.verts.new((c[0] + r * math.cos(k * math.tau / seg), c[1] + r * math.sin(k * math.tau / seg), z)) for k in range(seg)]
    bm.faces.new(vs).material_index = mi

# ====================================================================================== walls
def _sweep(bm, pts, inner_sign, prof, mis, gaps=()):
    """Sweep a closed profile [(offset_inner, z)] along a 2D polyline; segments near gaps are left out (capped)."""
    n = len(pts)
    rings = []
    for k, p in enumerate(pts):
        a = pts[max(k - 1, 0)]; b = pts[min(k + 1, n - 1)]
        t = Vector((b[0] - a[0], b[1] - a[1])).normalized()
        nr = Vector((-t.y, t.x)) * inner_sign
        rings.append([bm.verts.new((p[0] + nr.x * o, p[1] + nr.y * o, z)) for o, z in prof])
    skip = []
    for k in range(n - 1):
        mx, my = (pts[k][0] + pts[k + 1][0]) / 2, (pts[k][1] + pts[k + 1][1]) / 2
        skip.append(any(math.hypot(mx - gx, my - gy) < hw for gx, gy, hw in gaps))
    np_ = len(prof)
    for k in range(n - 1):
        if skip[k]:
            continue
        r0, r1 = rings[k], rings[k + 1]
        for e in range(np_):
            f = bm.faces.new((r0[e], r0[(e + 1) % np_], r1[(e + 1) % np_], r1[e]))
            f.material_index = mis[e]
    for k in range(n):
        left = skip[k - 1] if k > 0 else True
        right = skip[k] if k < n - 1 else True
        if left != right:
            bm.faces.new(rings[k]).material_index = 0
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

WALL_PROF = [(-5.0, -6.0), (5.0, -6.0), (5.0, 50.45), (4.6, 50.45), (4.6, 50.0), (-4.2, 50.0), (-4.2, 51.2), (-5.0, 51.2)]
WALL_MIS = [0, 0, 0, 0, 1, 0, 0, 0]
BULGE_GAPS = [(0.0, 0.0, 9.5), (445.0, 300.0, 15.0)]
ROSE_GAPS = [(-140.0, 870.0, 6.5), (402.0, 870.0, 9.5)]

def _rose_pts():
    xs = set(float(x) for x in range(-2600, 2601, 20))
    xs |= set(float(x) for x in range(-480, 481, 4))
    for gx, gy, hw in ROSE_GAPS:
        xs |= {gx - hw - 0.5, gx - hw + 0.5, gx + hw - 0.5, gx + hw + 0.5}
    return [(x, rose_y_m(x)) for x in sorted(xs)]

def _along(pts):
    s_ = 0.0
    n = len(pts)
    for k in range(n):
        a = pts[max(k - 1, 0)]; b = pts[min(k + 1, n - 1)]
        t = Vector((b[0] - a[0], b[1] - a[1])).normalized()
        if k > 0:
            s_ += math.hypot(pts[k][0] - pts[k - 1][0], pts[k][1] - pts[k - 1][1])
        yield Vector(pts[k]), t, Vector((-t.y, t.x)), s_

def _near(p, lst, r):
    return any(math.hypot(p[0] - q[0], p[1] - q[1]) < r for q in lst)

SPECIAL_PIL = [(-158.0, 870.0), (-110.0, 870.0)]
LIFT_PTS = [(-380.0, 870.0), (-40.0, 870.0), (260.0, 870.0), (-62.0, 10.0), (338.0, 870.0), (-195.0, 870.0)]

def _pilasters(bm, pts, inner_sign, start, every, skip_pts, mi_sh=0):
    """Inner-face pilasters 7 x 3 m with a flared foot and block caps 3 m above the parapet."""
    nxt = start
    out = []
    for p, t, nl, s_ in _along(pts):
        if s_ < nxt:
            continue
        if _near(p, skip_pts, 12.0):
            continue
        nxt = s_ + every
        n = nl * inner_sign
        obox(bm, p, t, n, 7.0, 0, -2.0, 50.2, mi_sh, across0=(4.9, 8.0))
        # flared foot: a wedge from 5.5 m deep at the ground to the 3 m shaft at Z 9
        c = p
        pts8 = []
        for z, d in ((-1.0, 10.5), (9.0, 8.0)):
            for sa, sn in ((-1, 4.9), (1, 4.9), (1, d), (-1, d)):
                q = c + t * (sa * 3.6) + n * sn
                pts8.append((q.x, q.y, z))
        hexa(bm, pts8, mi_sh)
        obox(bm, p, t, n, 7.0, 0, 50.0, 53.6, mi_sh, across0=(2.6, 8.0))
        obox(bm, p, t, n, 7.8, 0, 53.6, 54.2, mi_sh, across0=(2.3, 8.4))
        out.append((p.x, p.y))
    return out

def _outer_panels(bm, pts, inner_sign, skip_pts, every=20.0, groove=3.0, mi=0):
    nxt = 0.0
    for p, t, nl, s_ in _along(pts):
        if s_ < nxt:
            continue
        nxt = s_ + every
        if _near(p, skip_pts, 18.0):
            continue
        n = nl * inner_sign
        obox(bm, p + t * (every / 2), t, n, every - groove, 0, -2.0, 49.6, mi, across0=(-5.55, -4.9))

def _dead_roots(bm, pts, inner_sign, rnd, skip_pts, every=3.5, mi=0):
    """Dead leafless root tendrils hanging down the outer coping (ep09 07:59.5)."""
    nxt = 0.0
    for p, t, nl, s_ in _along(pts):
        if s_ < nxt:
            continue
        nxt = s_ + every * rnd.uniform(0.5, 1.6)
        if _near(p, skip_pts, 12.0):
            continue
        n = nl * inner_sign
        base = p + n * (-5.62) + t * rnd.uniform(-1.5, 1.5)
        ln = rnd.uniform(4.0, 16.0)
        q = [(base.x, base.y, 51.0)]
        for k in range(1, 4):
            wob = t * rnd.uniform(-0.8, 0.8)
            q.append((base.x + wob.x, base.y + wob.y, 51.0 - ln * k / 3))
        tube(bm, q, 0.18, 0.04, 3, mi)

def build_walls(MT):
    """Bulge walls (U) + Wall Rose: 50 m, 10 m thick, vertical faces, low plain outer parapet (no merlons), inner-face
    pilasters with caps, outer counterfort grooves, dead roots on the outer coping; gate blocks are separate."""
    _materials(MT)
    rnd = random.Random(11)
    mats = [MT["wall_t"], MT["walk_brick"]]
    bulge = district_outline_m(3.0)
    bm = bmesh.new()
    _sweep(bm, bulge, 1, WALL_PROF, WALL_MIS, BULGE_GAPS)
    _mk("WallTrost", bm, mats)
    rose = _rose_pts()
    bm = bmesh.new()
    _sweep(bm, rose, -1, WALL_PROF, WALL_MIS, ROSE_GAPS)
    _mk("WallRose", bm, [MT["wall_t"], MT["walk_lime"]])
    # pilasters (inner faces) and their caps
    bm = bmesh.new()
    skip_b = [(0.0, 0.0), (22.0, 3.0), (-22.0, 3.0), (445.0, 300.0)] + LIFT_PTS
    pil_b = _pilasters(bm, bulge, 1, 14.0, 28.0, skip_b + [(-480.0, 870.0), (480.0, 870.0)])
    _mk("ButtressTrost", bm, [MT["pilaster"]])
    bm = bmesh.new()
    rose_in = [p for p in rose if abs(p[0]) <= 466.0]
    skip_r = [(-140.0, 870.0), (-128.0, 870.0), (-152.0, 870.0), (402.0, 870.0), (335.0, 870.0), (389.0, 870.0)] + SPECIAL_PIL + LIFT_PTS
    pil_r = _pilasters(bm, rose_in, -1, 10.0, 28.0, skip_r)
    _mk("ButtressRose", bm, [MT["pilaster"]])
    # outer faces: counterfort grooves (bulge outside, Rose north face) + hanging dead roots
    bm = bmesh.new()
    _outer_panels(bm, bulge, 1, [(0.0, 0.0), (445.0, 300.0)])
    _outer_panels(bm, [p for p in rose if abs(p[0]) < 1000], -1, [(-140.0, 870.0), (402.0, 870.0)])
    _mk("WallPanelsTrost", bm, [MT["wall_t"]])
    bm = bmesh.new()
    _dead_roots(bm, bulge, 1, rnd, [(0.0, 0.0)])
    _mk("WallRootsTrost", bm, [MT["vine"]])
    WALL_INFO.update(bulge=bulge, rose=rose, pil_b=pil_b, pil_r=pil_r)
    return bulge, rose

WALL_INFO = {}

# ---------------------------------------------------------------- wall-top dressing
def _cannon_mesh(MT):
    me = bpy.data.meshes.get("TrostCannonMesh")
    if me:
        return me
    bm = bmesh.new()
    cyl(bm, (0, 0, 0.0), (0, 0, 0.25), 1.75, seg=20, mi=1)                  # turntable disc 3.5 m
    for k in range(6):
        a = k * math.pi / 6
        box(bm, (0, 0, 0.27), (3.4, 0.12, 0.05), rot=a, mi=2)
    box(bm, (0, 0, 0.55), (1.5, 2.6, 0.5), mi=1)                             # bogie carriage
    for sx in (-0.65, 0.65):
        box(bm, (sx, 0.1, 0.95), (0.2, 2.1, 0.75), mi=1, taper=(1, 0.6))
        for sy in (-0.8, 0.8):
            cyl(bm, (sx * 1.2, sy, 0.45), (sx * 1.2 + 0.15 * (1 if sx > 0 else -1), sy, 0.45), 0.4, seg=10, mi=0)
    cyl(bm, (0, -1.2, 1.2), (0, 2.6, 1.05), 0.38, 0.27, seg=12, mi=0)        # barrel, muzzle +y
    cyl(bm, (0, 2.45, 1.06), (0, 2.65, 1.05), 0.34, 0.34, seg=12, mi=0)
    me = bpy.data.meshes.new("TrostCannonMesh"); bm.to_mesh(me); bm.free()
    for m_ in (MT["iron_t"], MT["timber_d"], MT["plank_t"]):
        me.materials.append(m_)
    return me

def _hut_mesh(MT):
    me = bpy.data.meshes.get("TrostWallHutMesh")
    if me:
        return me
    bm = bmesh.new()
    box(bm, (0, 0, 1.6), (5.0, 5.0, 3.2), mi=0)                     # stone base
    box(bm, (0, 0, 4.4), (5.2, 5.2, 2.4), mi=1)                     # half-timbered upper storey
    p = [bm.verts.new(c) for c in ((-3.0, -3.0, 5.6), (3.0, -3.0, 5.6), (3.0, 3.0, 5.6), (-3.0, 3.0, 5.6), (0, -3.0, 8.4), (0, 3.0, 8.4))]
    for fv in ((p[0], p[1], p[4]), (p[2], p[3], p[5]), (p[1], p[2], p[5], p[4]), (p[3], p[0], p[4], p[5])):
        bm.faces.new(fv).material_index = 2
    box(bm, (0, -2.52, 1.2), (1.1, 0.1, 2.2), mi=3)
    box(bm, (1.2, 2.62, 4.4), (0.9, 0.1, 1.0), mi=3)
    me = bpy.data.meshes.new("TrostWallHutMesh"); bm.to_mesh(me); bm.free()
    for m_ in (MT["cornice"], MT["f_tcream"], MT["roof_red_t"], MT["window_t"]):
        me.materials.append(m_)
    return me

def _crates_mesh(MT):
    me = bpy.data.meshes.get("TrostCratesMesh")
    if me:
        return me
    bm = bmesh.new(); rnd = random.Random(4)
    for i in range(5):
        x, y = rnd.uniform(-1.4, 1.4), rnd.uniform(-1.0, 1.0)
        h = rnd.choice((0.9, 1.0, 1.1))
        box(bm, (x, y, h / 2), (1.0, 1.0, h), rot=rnd.uniform(-0.2, 0.2))
        if rnd.random() < 0.5:
            box(bm, (x, y, h + 0.45), (0.9, 0.9, 0.9), rot=rnd.uniform(-0.3, 0.3))
    me = bpy.data.meshes.new("TrostCratesMesh"); bm.to_mesh(me); bm.free()
    me.materials.append(MT["crate_t"])
    return me

def _flag_mesh(MT):
    me = bpy.data.meshes.get("TrostFlagMesh")
    if me:
        return me
    bm = bmesh.new()
    cyl(bm, (0, 0, 0), (0, 0, 8.0), 0.09, seg=6, mi=0)
    box(bm, (0.0, 0.9, 6.6), (0.05, 1.7, 2.6), mi=1)
    me = bpy.data.meshes.new("TrostFlagMesh"); bm.to_mesh(me); bm.free()
    me.materials.append(MT["timber_d"]); me.materials.append(MT["flag_green"])
    return me

def _link_inst(name, me, coll, xyz_m, rot):
    o = bpy.data.objects.new(name, me)
    o.location = M(*xyz_m); o.rotation_euler.z = rot
    coll.objects.link(o)
    return o

def _walltop_dress(MT, pts, inner_sign, gaps, kind, coll, rnd, zone=None):
    """Narrow-gauge track (1.5 m) on the inner half, turntable cannons on the outer half, crates, red-tile huts
    every ~150 m, green flags; `kind` "bulge" (cannons ~30 m) / "rose" (60 m; 20 m on both edges in the speech zones)."""
    bm = bmesh.new()
    cm, hm, crm, fm = _cannon_mesh(MT), _hut_mesh(MT), _crates_mesh(MT), _flag_mesh(MT)
    tracks = (2.0,) if kind == "bulge" else (1.6, -1.2)
    nxt_s = 0.0; nxt_c = 6.0; nxt_h = 70.0; nxt_k = 20.0; nxt_f = 40.0
    hut_pts = []
    ncan = 0
    for k in range(len(pts) - 1):
        a, b = Vector(pts[k]), Vector(pts[k + 1])
        mid = (a + b) / 2
        if any(math.hypot(mid.x - gx, mid.y - gy) < hw + 3 for gx, gy, hw in gaps):
            continue
        if zone and not zone(mid.x, mid.y):
            continue
        t = (b - a); ln = t.length
        if ln == 0:
            continue
        t.normalize(); n = Vector((-t.y, t.x)) * inner_sign
        for tc in tracks:
            for off in (-0.75, 0.75):
                obox(bm, mid + n * (tc + off), t, n, ln + 0.05, 0.12, 50.0, 50.22, 0)
    s_ = 0.0
    for p, t, nl, s_ in _along(pts):
        if any(math.hypot(p.x - gx, p.y - gy) < hw + 6 for gx, gy, hw in gaps):
            continue
        if zone and not zone(p.x, p.y):
            continue
        n = nl * inner_sign
        if s_ >= nxt_s:
            nxt_s = s_ + 1.2
            for tc in tracks:
                obox(bm, p + n * tc, t, n, 0.35, 2.3, 49.98, 50.1, 1)
        speech = kind == "rose" and (300 <= p.x <= 350 or -160 <= p.x <= 40)
        every = 30.0 if kind == "bulge" else (20.0 if speech else 60.0)
        if s_ >= nxt_c:
            nxt_c = s_ + every
            if not _near((p.x, p.y), hut_pts, 6.0):
                for side in ((-1,) if not speech else (-1, 1)):
                    if kind == "rose" and side == -1:
                        off = 2.6                                 # Rose: south (Trost-side) edge
                    else:
                        off = -2.6 if kind == "bulge" else -2.4   # bulge: outer edge; Rose speech zone: north edge too
                    c = p + n * off
                    face = -n if off < 0 else n
                    rot = math.atan2(face.y, face.x) - math.pi / 2
                    _link_inst(f"TrostCannon_{kind}{ncan}", cm, coll, (c.x, c.y, 50.0), rot); ncan += 1
                    # spur from the track to the turntable
                    for off2 in (-0.75, 0.75):
                        q0 = p + n * (tracks[0]) + t * off2
                        q1 = c + t * off2 * 0.6
                        dv = q1 - q0
                        if dv.length > 0.5:
                            obox(bm, (q0 + q1) / 2, dv.normalized(), Vector((-dv.y, dv.x)).normalized(), dv.length, 0.12, 50.0, 50.2, 0)
        if s_ >= nxt_h:
            nxt_h = s_ + 150.0
            c = p + n * (-1.6)
            _link_inst(f"TrostHut_{kind}{len(hut_pts)}", hm, coll, (c.x, c.y, 50.0), math.atan2(t.y, t.x)); hut_pts.append((p.x, p.y))
        if s_ >= nxt_k:
            nxt_k = s_ + rnd.uniform(35, 60)
            c = p + n * (-1.8) + t * 9.0
            if not _near((c.x, c.y), hut_pts, 8.0):
                _link_inst(f"TrostCrates_{kind}{int(s_)}", crm, coll, (c.x, c.y, 50.0), math.atan2(t.y, t.x) + rnd.uniform(-0.2, 0.2))
        if s_ >= nxt_f:
            nxt_f = s_ + (60.0 if kind == "bulge" else 45.0)
            c = p + n * (-4.5)
            _link_inst(f"TrostFlag_{kind}{int(s_)}", fm, coll, (c.x, c.y, 50.0), math.atan2(t.y, t.x))
    ob = _mk(f"WallTopTrack_{kind}", bm, [MT["iron_t"], MT["timber_d"]], coll)
    return ncan

def build_walltop(MT):
    gc = _coll("TrostGarrison")
    rnd = random.Random(21)
    bulge = WALL_INFO["bulge"]
    n1 = _walltop_dress(MT, bulge, 1, BULGE_GAPS + [(-62.0, 10.0, 4.0)], "bulge", gc, rnd)
    rose = [p for p in WALL_INFO["rose"] if abs(p[0]) <= 1000]
    rose = L.resample(rose, 3.0)
    n2 = _walltop_dress(MT, rose, -1, ROSE_GAPS + [(338.0, 870.0, 4.0), (-380.0, 870.0, 4.0), (-40.0, 870.0, 4.0), (260.0, 870.0, 4.0)],
                        "rose", gc, rnd)
    # S2: 6 dark-green banners on 8 m poles along the north parapet X -45..+5
    fm = _flag_mesh(MT)
    for k, x in enumerate(range(-45, 6, 10)):
        _link_inst(f"TrostBannerS2_{k}", fm, gc, (x, 874.6, 50.0), math.pi)
    return n1 + n2

# ====================================================================================== the outer gate O
def _gate_block_intact(bm):
    """Wall body at O between the cut ends (X -12..12, Y -5..5): passage 11 m x 26 m (to the transom)."""
    for sx in (-1, 1):
        box(bm, (sx * 8.75, 0.0, 22.6), (6.5, 10.2, 57.2))
    box(bm, (0.0, 0.0, 38.6), (11.2, 10.2, 25.2))
    box(bm, (0.0, -0.4, 51.2 - 0.6), (24.0, 9.4, 1.2))

def _iron_frame(bm, mi_iron=0, mi_dark=1):
    """Outside: rust-red riveted iron frame 20 m wide (posts 4.5 m), to Z 45, transom at Z 26."""
    for sx in (-1, 1):
        box(bm, (sx * 7.75, -5.45, 22.5), (4.5, 0.9, 45.0), mi=mi_iron)
        for z in range(2, 45, 3):
            for xx in (sx * 6.0, sx * 9.5):
                box(bm, (xx, -5.95, z), (0.35, 0.2, 0.35), mi=mi_iron)
    box(bm, (0, -5.45, 26.0), (11.2, 0.9, 2.2), mi=mi_iron)
    box(bm, (0, -5.45, 44.0), (20.0, 0.9, 2.0), mi=mi_iron)
    box(bm, (0, -5.2, 35.0), (11.0, 0.5, 16.0), mi=mi_dark)
    for x in (-3.0, 0.0, 3.0):
        box(bm, (x, -5.5, 35.0), (0.5, 0.6, 16.0), mi=mi_iron)

GH_TIERS = ((0.0, 13.6, 15.0), (13.6, 27.0, 14.8), (27.0, 40.0, 14.5))      # (z0, z1, front Y) of the 3 brick tiers

def _gh_cornices(bm, holes=None, mi=1):
    for z, fy in ((13.6, 15.0), (27.0, 14.8), (40.0, 14.5)):
        segs = [(-17.6, 17.6)]
        if holes and z < 35:
            hw_ = holes(z)
            segs = [(-17.6, -hw_), (hw_, 17.6)]
        for a, b in segs:
            if b - a > 0.3:
                box(bm, ((a + b) / 2, (5.0 + fy + 0.6) / 2, z), (b - a, fy + 0.6 - 5.0, 1.0), mi=mi)

def _gh_windows(bm, avoid=None, mi=3):
    xs = [-15.6, -13.4, -11.2, -9.0, -3.6, -1.2, 1.2, 3.6, 9.0, 11.2, 13.4, 15.6]
    rows = [(10.5, [-15.0, -12.5, 12.5, 15.0], 15.02), (22.5, xs, 14.82), (32.0, xs, 14.52), (36.4, xs, 14.52)]
    for z, xs, fy in rows:
        for x in xs:
            if avoid and avoid(x, z):
                continue
            box(bm, (x, fy, z), (1.1, 0.12, 1.7), mi=mi)
            cyl(bm, (x, fy - 0.06, z + 0.85), (x, fy + 0.06, z + 0.85), 0.55, seg=8, mi=mi)

def _gh_pilasters(bm, mi=2):
    """Sandstone pilasters X +-17..27, 6 m deep (face Y 11), curving out at the foot, block caps over the parapet."""
    for sx in (-1, 1):
        x0, x1 = sorted((sx * 17.0, sx * 27.0))
        box(bm, ((x0 + x1) / 2, 8.0, 26.6), (10.0, 6.0, 53.2), mi=mi)
        prev = None
        for z, d in ((0.0, 9.6), (3.0, 8.0), (6.5, 6.9), (11.0, 6.0)):
            if prev:
                z0, d0 = prev
                hexa(bm, [(x0, 5.0, z0), (x1, 5.0, z0), (x1, 5.0 + d0, z0), (x0, 5.0 + d0, z0),
                          (x0, 5.0, z), (x1, 5.0, z), (x1, 5.0 + d, z), (x0, 5.0 + d, z)], mi)
            prev = (z, d)
        box(bm, ((x0 + x1) / 2, 6.5, 53.9), (10.8, 9.0, 1.4), mi=mi)

def _gh_doors(bm):
    """Town-side base: 2 arched strap doors (large X -1..8, small X -12..-9) + crest plaque between."""
    for cx, w, h in ((3.5, 7.5, 9.0), (-10.5, 3.0, 5.0)):
        box(bm, (cx, 15.05, h * 0.7 / 2), (w + 1.2, 0.2, h * 0.7), mi=1)
        cyl(bm, (cx, 14.95, h * 0.7), (cx, 15.15, h * 0.7), w / 2 + 0.6, seg=14, mi=1)
    # crest plaque: shield on a pale tablet
    box(bm, (-5.6, 15.1, 6.0), (3.0, 0.3, 4.0), mi=1)
    hexa(bm, [(-6.6, 15.25, 4.6), (-4.6, 15.25, 4.6), (-4.6, 15.6, 4.6), (-6.6, 15.6, 4.6),
              (-6.9, 15.25, 7.6), (-4.3, 15.25, 7.6), (-4.3, 15.6, 7.6), (-6.9, 15.6, 7.6)], 2)
    cyl(bm, (-5.6, 15.55, 6.4), (-5.6, 15.75, 6.4), 0.7, seg=10, mi=0)

def _door_leaves(MT):
    bm = bmesh.new()
    cx, w, h = 3.5, 7.5, 9.0
    box(bm, (cx, 15.2, h * 0.7 / 2), (w, 0.3, h * 0.7), mi=0)
    cyl(bm, (cx, 15.05, h * 0.7), (cx, 15.35, h * 0.7), w / 2, seg=14, mi=0)
    for z in (1.5, 3.5, 5.5):
        box(bm, (cx, 15.4, z), (w + 0.1, 0.12, 0.35), mi=1)
    box(bm, (-10.5, 15.2, 1.75), (3.0, 0.3, 3.5), mi=0)
    cyl(bm, (-10.5, 15.05, 3.5), (-10.5, 15.35, 3.5), 1.5, seg=10, mi=0)
    d = _mk("OuterGate_Door", bm, [MT["timber_d"], MT["iron_t"]])
    bm = bmesh.new()
    box(bm, (0, -5.0, 12.5), (11.0, 0.9, 25.0), mi=0)
    for z in range(2, 25, 3):
        box(bm, (0, -5.5, z), (11.0, 0.2, 0.4), mi=1)
    _mk("OuterGate_Iron", bm, [MT["iron_rust"], MT["iron_t"]])
    return d

def _hole_half(z, rnd_tab, base=7.5, top=32.0):
    """Ragged breach outline: half width at height z (0 above the broken round top)."""
    k = int(z * 1.7) % len(rnd_tab)
    if z > top + 2.0 * rnd_tab[(k + 3) % len(rnd_tab)]:
        return 0.0
    if z < top - base:
        return base + 0.8 * rnd_tab[k]
    dz = (z - (top - base)) / base
    return max(0.0, base * math.sqrt(max(0.0, 1 - dz * dz)) + 0.9 * rnd_tab[k])

def build_outer_gate(MT):
    """O: wall block + iron frame (outside), 3-tier brick gatehouse with sandstone pilasters (town side), intact and
    breached variants, rubble fan, beams, glow card, Λ plug and seal rubble (hidden until their state)."""
    rnd = random.Random(31)
    mats = [MT["wall_t"], MT["cornice"], MT["sandstone"], MT["window_t"], MT["iron_rust"], MT["window_t"]]
    # ---- intact
    bm = bmesh.new()
    _gate_block_intact(bm)
    for z0, z1, fy in GH_TIERS:                                                # 3 brick tiers, each set back a little
        box(bm, (0.0, (5.0 + fy) / 2, (z0 + z1) / 2), (34.0, fy - 5.0, z1 - z0), mi=6)
    _gh_cornices(bm)
    _gh_windows(bm)
    _gh_doors(bm)
    _gh_pilasters(bm)
    box(bm, (3.5, 10.0, 3.2), (7.4, 9.9, 6.3), mi=3)                          # dark passage behind the big door
    gate = _mk("OuterGate", bm, mats + [MT["gh_brick"]])
    bm = bmesh.new()
    _iron_frame(bm)
    _mk("OuterGate_Frame", bm, [MT["iron_rust"], MT["window_t"]])
    _door_leaves(MT)
    # ---- breached
    tab = [rnd.uniform(-1, 1) for _ in range(97)]
    # OWNER 10/27: the breach is BOULDER-SIZED (the 14 m ball fills it snugly): 15.6 m wide through the gatehouse with a
    # broken round top at Z ~16 (was 15 x 32-34 m), stepping to ~13 m in the wall body (the step jams the ball)
    hole_gh = lambda z: _hole_half(z, tab, 7.8, 16.2)
    hole_wall = lambda z: _hole_half(z, tab[13:] + tab[:13], 6.6, 15.0)
    bm = bmesh.new()
    cell = 1.2
    ZC = 36.0                                                                  # cells below, solid above
    for side_x in (-1, 1):                                                     # wall body around the 13 m hole
        box(bm, (side_x * 10.75, 0.0, 22.6), (2.5, 10.2, 57.2), mi=0)
    box(bm, (0.0, 0.0, (ZC + 51.2) / 2), (19.0, 10.2, 51.2 - ZC), mi=0)
    box(bm, (0.0, -0.4, 51.2 - 0.6), (24.0, 9.4, 1.2), mi=0)
    for iz in range(int(ZC / cell)):
        z0 = iz * cell; zc = z0 + cell / 2
        hw_ = hole_wall(zc)
        for ix in range(math.ceil(19.0 / cell)):
            x0 = -9.5 + ix * cell; xc = x0 + cell / 2
            if abs(xc) < hw_:
                continue
            box(bm, (xc, 0.0, zc), (cell + 0.01, 10.2, cell + 0.01), mi=0)
    box(bm, (0.0, (5.0 + 14.5) / 2, (ZC + 40.0) / 2), (34.0, 9.5, 40.0 - ZC), mi=6)
    for iz in range(int(ZC / cell)):                                          # gatehouse brick around the 15 m hole
        z0 = iz * cell; zc = z0 + cell / 2
        hw_ = hole_gh(zc)
        fy = 15.0 if zc < 13.6 else 14.8 if zc < 27 else 14.5
        for ix in range(int(34.0 / cell) + 1):
            x0 = -17.0 + ix * cell; xc = x0 + cell / 2
            if xc > 17.0:
                continue
            if abs(xc) < hw_:
                continue
            ry = 0.0 if abs(abs(xc) - hw_) > cell * 1.5 else rnd.uniform(-1.2, 0.0)
            box(bm, (xc, (5.0 + fy + ry) / 2, zc), (cell + 0.01, fy + ry - 5.0, cell + 0.01), mi=6)
    _gh_cornices(bm, holes=lambda z: hole_gh(z) + rnd.uniform(0.2, 1.4))
    _gh_windows(bm, avoid=lambda x, z: abs(x) < hole_gh(z) + 1.6)
    _gh_pilasters(bm)
    for k in range(70):                                                         # broken brick edges + radiating cracks
        z = rnd.uniform(1.0, 33.0); hw_ = hole_gh(z)
        if hw_ <= 0:
            continue
        sx = rnd.choice((-1, 1))
        box(bm, (sx * (hw_ + rnd.uniform(-0.3, 0.8)), rnd.uniform(10.0, 15.6), z), (rnd.uniform(0.6, 1.6), rnd.uniform(0.6, 2.0), rnd.uniform(0.4, 1.2)),
            rot=rnd.uniform(0, 3), mi=6)
    for k in range(12):                                          # (crack tubes removed: QA 10/26) keep the random stream
        rnd.uniform(-0.6, 0.6); rnd.random(); rnd.uniform(4, 34)
        for j in range(1, 4):
            rnd.uniform(1.5, 2.5); rnd.uniform(1.0, 2.0)
    broken = _mk("OuterGateBroken", bm, mats + [MT["gh_brick"]])
    # broken floor beams + a few dead root strands.  QA 10/26: fewer, chunkier dark-brown timbers with splintered ends,
    # in an object NOT named "*Gate*" (toon.py inks every "Gate" object with a 0.25 m hull: thin tubes became black bars).
    for z in (13.0, 20.0, 27.0):                                     # keep the random stream as before
        for k in range(4):
            rnd.choice((-1, 1)); rnd.uniform(5.5, 14.5); rnd.uniform(1.5, 4.5); rnd.uniform(-0.5, 0.5); rnd.uniform(0.0, 1.8)
    for k in range(9):
        rnd.choice((-1, 1)); rnd.uniform(3.5, 6.5); rnd.uniform(18, 31); rnd.uniform(-4.5, 14.0)
        for j in range(1, 5):
            rnd.uniform(-1.2, 1.2); rnd.uniform(-1, 1); rnd.uniform(1.5, 3.0)
    bm = bmesh.new()
    brng = random.Random(77)
    for (z, sx, y, ln, droop) in ((12.6, -1, 13.6, 3.0, 0.8), (14.0, 1, 12.9, 2.6, 0.6), (15.2, -1, 14.3, 2.2, 0.4),
                                  (11.4, 1, 14.4, 3.2, 1.0), (15.6, 1, 14.0, 1.8, 0.3), (10.2, -1, 14.6, 2.4, 0.9)):
        hw_ = max(hole_gh(z), 3.0)
        x0 = sx * (hw_ + 0.6); x1 = x0 - sx * ln
        a, b = Vector((x0, y, z)), Vector((x1, y + brng.uniform(-0.6, 0.6), z - droop))
        q1 = a + (b - a) * 0.85
        tube(bm, [a, q1], 0.32, 0.28, 6, mi=0)                       # the beam (square-ish, 0.6 m)
        d = (b - a).normalized(); n_ = Vector((-d.y, d.x, 0.0))
        n_ = n_.normalized() if n_.length > 1e-3 else Vector((1, 0, 0))
        for j in range(3):                                           # splintered end: 3 thin tapering spikes
            off = n_ * brng.uniform(-0.2, 0.2) + Vector((0, 0, brng.uniform(-0.18, 0.18)))
            tip = b + d * brng.uniform(0.4, 1.4) + off * 2.0
            tube(bm, [q1 + off, tip], 0.14, 0.02, 4, mi=0)
    for k in range(5):                                               # dark dead root strands hanging in the hole
        x = brng.choice((-1, 1)) * brng.uniform(4.5, 6.5); z = brng.uniform(14.0, 16.0)
        q = [(x, brng.uniform(13.6, 14.8), z)]
        for j in range(1, 5):
            q.append((x + brng.uniform(-0.6, 0.6), q[-1][1] + brng.uniform(-0.2, 0.3), z - j * brng.uniform(0.8, 1.4)))
        tube(bm, q, 0.16, 0.05, 4, mi=1)
    _mk("TrostBreachTimbers", bm, [MT["timber_split"], MT["vine"]])
    # rubble fan 15-20 m north of the breach (3 m high at the hole)
    bm = bmesh.new()
    for k in range(190):
        a = rnd.uniform(math.radians(25), math.radians(155))
        r = 16.0 * rnd.random() ** 0.8
        x, y = math.cos(a) * r * 1.1, 14.0 + math.sin(a) * r
        if math.hypot(x, y - 36.0) < 25.0 and math.atan2(y - 36, x) < math.radians(-45) and math.atan2(y - 36, x) > math.radians(-135):
            pass
        hmax = 3.0 * (1 - r / 17.0)
        sz = rnd.uniform(0.5, 2.0)
        z = rnd.uniform(0.0, max(0.2, hmax)) + sz * 0.3
        box(bm, (x, y, z), (sz, sz * rnd.uniform(0.6, 1.3), sz * rnd.uniform(0.4, 0.9)), rot=rnd.uniform(0, 3),
            mi=0 if rnd.random() < 0.6 else 1)
    for k in range(10):                                              # (rubble timbers dropped: ink bars; QA 10/26)
        rnd.uniform(-6, 6); rnd.uniform(13, 22); rnd.uniform(0, math.pi); rnd.uniform(1.0, 3.0)
    for k in range(40):                                              # chunks out on the grass / ring road
        a = rnd.uniform(math.radians(15), math.radians(165)); r = rnd.uniform(20, 75)
        x, y = math.cos(a) * r, math.sin(a) * r
        if math.hypot(x, y - 36) < 26:
            continue
        sz = rnd.uniform(0.6, 2.4)
        box(bm, (x, y, sz * 0.3), (sz, sz * 0.8, sz * 0.6), rot=rnd.uniform(0, 3), mi=1)
    _mk("OuterGateRubble", bm, [MT["rubble_brick"], MT["rubble_stone"], MT["timber_d"]])
    # glow card inside the breach (fades with set_glow), plug (hidden), seal rubble
    bm = bmesh.new()
    vs = [bm.verts.new(p) for p in ((-6.0, -3.5, 0.2), (6.0, -3.5, 0.2), (6.0, -3.5, 8.6), (-6.0, -3.5, 8.6))]
    bm.faces.new(vs)
    arc = [bm.verts.new((6.0 * math.cos(math.pi * k / 8), -3.0, 8.6 + 6.0 * math.sin(math.pi * k / 8))) for k in range(9)]
    ctr = bm.verts.new((0.0, -3.0, 8.6))
    for k in range(8):
        bm.faces.new((ctr, arc[k], arc[k + 1]))
    glow = _mk("OuterGate_Glow", bm, [MT["glow"]])
    glow.visible_shadow = False
    _build_plug(MT, rnd)
    # QA 10/26: the crushed-brick ring hid the ball.  Now a LOW skirt only at the sides (|X| 5.6..10, under 1 m), dark
    # brick / grey stone, so the big grey ball reads wedged in the hole at the plug's base with its front face clear.
    for k in range(60):                                              # keep the random stream as before
        rnd.uniform(0, math.pi); rnd.uniform(6.8, 8.6); rnd.uniform(0.4, 1.2); rnd.uniform(0, 3)
    bm = bmesh.new()
    srng = random.Random(91)
    for k in range(46):
        sx = srng.choice((-1, 1))
        x = sx * srng.uniform(5.6, 10.0); y = srng.uniform(9.5, 17.5)
        sz = srng.uniform(0.35, 1.0) * (1.0 - 0.35 * (abs(x) - 5.6) / 4.4)
        box(bm, (x, y, sz * 0.28), (sz * srng.uniform(0.9, 1.5), sz, sz * 0.55), rot=srng.uniform(0, 3), mi=0 if k % 3 else 1)
    _mk("OuterGate_SealRubble", bm, [MT["rubble_dark"], MT["rubble_stone"]])
    _ball_contact("TrostBallContactSeal", (BALL_REST_M[0], BALL_REST_M[1]), 0.0, MT, front_only=True)
    for n_ in ("OuterGateBroken", "OuterGateRubble", "TrostBreachTimbers", "OuterGate_Glow", "OuterGate_Plug", "OuterGate_SealRubble",
               "TrostBallContactSeal"):
        _hide(bpy.data.objects.get(n_))
    return gate

def _build_plug(MT, rnd):
    """Λ plug: a dark tapering spire of titan remains from the TOP OF THE BALL (Z ~14.5) up the brick face to Z 38 (base 15 m),
    ~60 tendril curves, some spreading 5-10 m over the brick.  Origin (0, 12, 14.5) M; set_plug(frac) grows it upward
    (scale z).  OWNER 10/27: the breach is ball-sized, so the spire stands on the gatehouse face above the wedged ball."""
    Z0 = 14.5
    bm = bmesh.new()                                     # authored in M, shifted to the origin (0, 12, Z0) below
    hexa(bm, [(-6.6, 14.4, 16.2), (6.6, 14.4, 16.2), (6.6, 16.6, 16.2), (-6.6, 16.6, 16.2),      # on the face, above the hole:
              (-0.4, 14.8, 37.5), (0.4, 14.8, 37.5), (0.4, 16.0, 37.5), (-0.4, 16.0, 37.5)], 0)    # the ball's front stays clear
    for k in range(62):
        x0 = rnd.uniform(-6.8, 6.8); z0 = rnd.uniform(14.8, 17.0)
        if k >= 46:                                      # tendrils fanning sideways over the brick (5-10 m)
            sx = 1 if x0 > 0 else -1
            ln = rnd.uniform(5.0, 10.0)
            zt = rnd.uniform(14.0, 32.0)
            hw0 = 7.0 * max(0.0, 1 - (zt - 14.0) / 24.0)
            pts = [(sx * hw0 * 0.8, 15.6, zt)]
            for j in range(1, 6):
                pts.append((pts[-1][0] + sx * ln / 5 + rnd.uniform(-0.4, 0.4), 15.25 + rnd.uniform(-0.05, 0.2),
                            pts[-1][2] + rnd.uniform(-1.4, 1.2)))
            tube(bm, pts, rnd.uniform(0.25, 0.5), 0.05, 4, mi=0)
            continue
        apex_z = rnd.uniform(31.0, 38.0)
        pts = []
        for j in range(8):
            t = j / 7
            hw_ = 7.0 * (1 - t) ** 1.1
            x = x0 * (1 - t) + rnd.uniform(-0.6, 0.6) * (1 - t * 0.7)
            x = max(-hw_ - 0.5, min(hw_ + 0.5, x))
            pts.append((x, rnd.uniform(15.3, 17.0), z0 + (apex_z - z0) * t))
        tube(bm, pts, rnd.uniform(0.5, 1.2), 0.1, 5, mi=0)
    for v in bm.verts:
        v.co.y -= 12.0; v.co.z -= Z0
    ob = _mk_at("OuterGate_Plug", bm, [MT["tendril"]], (0.0, 12.0, Z0))
    return ob

# ====================================================================================== gate square GS
def _slab_mesh(MT):
    """Spiked slab barricade: trapezoid plank box 8 W x 12 H x 4 D (base), braced back frame, black spikes on the lower
    front, 4 small iron wheels.  Origin = base centre; local -Y = spiked front."""
    me = bpy.data.meshes.get("TrostSlabMesh")
    if me:
        return me
    bm = bmesh.new()
    hexa(bm, [(-4.0, -2.0, 0.6), (4.0, -2.0, 0.6), (4.0, 2.0, 0.6), (-4.0, 2.0, 0.6),
              (-3.0, -0.6, 12.0), (3.0, -0.6, 12.0), (3.0, 1.0, 12.0), (-3.0, 1.0, 12.0)], 0)
    for sx in (-1, 1):                                                        # dark frame posts + braces
        hexa(bm, [(sx * 4.05 - 0.3, -2.05, 0.6), (sx * 4.05 + 0.3, -2.05, 0.6), (sx * 4.05 + 0.3, -1.4, 0.6), (sx * 4.05 - 0.3, -1.4, 0.6),
                  (sx * 3.05 - 0.3, -0.65, 12.0), (sx * 3.05 + 0.3, -0.65, 12.0), (sx * 3.05 + 0.3, 0.0, 12.0), (sx * 3.05 - 0.3, 0.0, 12.0)], 1)
    for z in (3.2, 6.4, 9.6):
        f = z / 12.0
        hw_ = 4.0 - f * 1.0; yf = -2.0 + f * 1.4
        box(bm, (0, yf - 0.12, z), (2 * hw_ + 0.4, 0.25, 0.5), mi=1)
    for sx in (-2.5, 0.0, 2.5):
        cyl(bm, (sx, 2.1, 0.6), (sx * 0.8, 1.1, 11.0), 0.18, seg=4, mi=1)
    for row, z in enumerate((1.6, 2.8)):
        for k in range(7):
            x = -3.3 + k * 1.1 + (0.55 if row else 0)
            if abs(x) > 3.6:
                continue
            y = -2.0 + (z - 0.6) / 11.4 * 1.4
            cyl(bm, (x, y, z), (x, y - 1.6, z - 0.2), 0.16, 0.02, seg=4, mi=2)
    for sx in (-3.0, 3.0):
        for sy in (-1.4, 1.4):
            cyl(bm, (sx - 0.15, sy, 0.45), (sx + 0.15, sy, 0.45), 0.45, seg=8, mi=2)
    me = bpy.data.meshes.new("TrostSlabMesh"); bm.to_mesh(me); bm.free()
    for m_ in (MT["plank_t"], MT["timber_d"], MT["iron_t"]):
        me.materials.append(m_)
    return me

SLABS = {}
def _slab_layout():
    out = {}
    for k, a in enumerate((15, 40, 65, 90, 112, 162)):
        r = 34.0
        x, y = PIT_C[0] + r * math.cos(math.radians(a)), PIT_C[1] + r * math.sin(math.radians(a))
        yaw = a - 90.0                                     # spiked front faces the pit centre / the gate
        out[f"TrostSlab_P{k + 1}"] = (round(x, 2), round(y, 2), yaw)
    for k, b in enumerate((-35, -25, -15, -5, 5, 15, 25, 35)):
        r = 74.0
        x, y = r * math.sin(math.radians(b)), r * math.cos(math.radians(b))
        out[f"TrostSlab_A{k + 1}"] = (round(x, 2), round(y, 2), -b)
    return out
SLABS.update(_slab_layout())

def build_gate_square(MT):
    """GS: ring pit P (C-trenches, plank walls, bridge, railing, mud, puddles), 14 spiked slabs (separate objects),
    log-crib fences, bollards, spruces + bushy tree, plank boxes, craters + small holes (post-kick) with turf caps."""
    rnd = random.Random(41)
    pc = _coll("TrostGateSquare")
    # ---------------- the ring pit (polar mesh)
    bm = bmesh.new()
    seg = 144
    def prof(a_deg):     # (r, z, material of the face from the previous point): 0 town floor, 1 plank wall, 3 plank top, 6 mud
        gap = -135.0 < a_deg < -45.0
        if gap:
            return [(0.0, 0.0, 0), (24.3, 0.0, 0), (24.3, -0.2, 0), (31.5, -0.2, 0)]
        return [(0.0, 0.0, 0), (7.0, 0.0, 0), (7.0, -4.0, 1), (11.0, -4.0, 6), (11.0, 0.0, 1), (17.0, 0.0, 0), (17.0, -7.0, 1),
                (21.0, -7.0, 6), (21.0, -4.6, 1), (22.5, -4.6, 3), (22.5, -2.3, 1), (23.9, -2.3, 3), (23.9, 0.0, 1), (24.3, 0.0, 3),
                (24.3, -0.2, 0), (31.5, -0.2, 0)]
    rings = []
    for k in range(seg):
        a = -180.0 + k * 360.0 / seg
        rings.append((a, prof(a + 180.0 / seg)))
    # build per sector: each sector uses the profile of its centre angle
    for k in range(seg):
        a0 = math.radians(-180.0 + k * 360.0 / seg); a1 = math.radians(-180.0 + (k + 1) * 360.0 / seg)
        pr = rings[k][1]
        for j in range(len(pr) - 1):
            r0, z0, _ = pr[j]; r1, z1, mi = pr[j + 1]
            if r0 == r1 and z0 == z1:
                continue
            v = [bm.verts.new((PIT_C[0] + r0 * math.cos(a0), PIT_C[1] + r0 * math.sin(a0), z0)),
                 bm.verts.new((PIT_C[0] + r1 * math.cos(a0), PIT_C[1] + r1 * math.sin(a0), z1)),
                 bm.verts.new((PIT_C[0] + r1 * math.cos(a1), PIT_C[1] + r1 * math.sin(a1), z1)),
                 bm.verts.new((PIT_C[0] + r0 * math.cos(a1), PIT_C[1] + r0 * math.sin(a1), z0))]
            if r0 == r1 and v[0].co == v[1].co:
                continue
            try:
                bm.faces.new(v).material_index = mi
            except ValueError:
                pass
    # radial end walls of the C arms (the trench ends at the gap), facing into the trench
    for a, sgn in ((-45.0, 1), (-135.0, -1)):
        ar = math.radians(a)
        c, s_ = math.cos(ar), math.sin(ar)
        tccw = Vector((-s_, c, 0.0)) * sgn
        for r0, r1, d in ((17.0, 24.3, -7.0), (7.0, 11.0, -4.0)):
            vs = [bm.verts.new((PIT_C[0] + r * c, PIT_C[1] + r * s_, z)) for r, z in ((r0, 0.0), (r1, 0.0), (r1, d), (r0, d))]
            f = bm.faces.new(vs); f.material_index = 1
            f.normal_update()
            if f.normal.dot(tccw) < 0:
                f.normal_flip()
    # plank decking at the middle ring edges + coping
    for k in range(seg):
        a = math.radians(-180.0 + (k + 0.5) * 360.0 / seg)
        ad = math.degrees(a)
        if -135.0 < ad < -45.0:
            continue
        for r, wdt in ((11.6, 1.2), (16.4, 1.2), (24.6, 0.9)):
            c = Vector((PIT_C[0] + r * math.cos(a), PIT_C[1] + r * math.sin(a)))
            t = Vector((-math.sin(a), math.cos(a)))
            obox(bm, c, t, Vector((math.cos(a), math.sin(a))), r * math.tau / seg + 0.05, wdt, 0.0, 0.16, 3)
    # retaining-wall posts every 2 m on the trench walls
    for r, d in ((17.0, -7.0), (24.1, -2.3), (7.0, -4.0), (11.0, -4.0)):
        n = int(r * math.radians(270) / 2.0)
        for k in range(n + 1):
            a = math.radians(-45.0 + k * 270.0 / n)
            c = Vector((PIT_C[0] + r * math.cos(a), PIT_C[1] + r * math.sin(a)))
            obox(bm, c, Vector((-math.sin(a), math.cos(a))), Vector((math.cos(a), math.sin(a))), 0.3, 0.3, d, 0.3, 4)
    # puddles on the trench floors
    for k in range(14):
        a = math.radians(rnd.uniform(-40, 220)); r = rnd.choice((19.0, 9.0)) + rnd.uniform(-0.8, 0.8)
        zf = -7.0 if r > 15 else -4.0
        c = (PIT_C[0] + r * math.cos(a), PIT_C[1] + r * math.sin(a))
        vs = [bm.verts.new((c[0] + rnd.uniform(0.8, 1.6) * math.cos(j * 0.785), c[1] + rnd.uniform(0.8, 1.6) * math.sin(j * 0.785), zf + 0.03)) for j in range(8)]
        bm.faces.new(vs).material_index = 5
    # plank bridge 4 x 16 m at compass bearing ~28 (NNE) from P, over the outer trench onto the middle ring
    # (AUDIT CORRECTIONS 4, 10/26: ep09 F09/000003609, ep04 20:30, F11/000014506; was 315 / NW)
    ab = math.radians(90.0 - 28.0)
    d = Vector((math.cos(ab), math.sin(ab))); t = Vector((-d.y, d.x))
    c = Vector(PIT_C) + d * 21.0
    obox(bm, c, d, t, 16.0, 4.0, 0.05, 0.45, 3)
    for sgn in (-1, 1):
        obox(bm, c + t * (sgn * 1.9), d, t, 16.0, 0.15, 0.45, 1.4, 4)
    # low railing on the town-side top step
    n = 40
    for k in range(n):
        a0 = math.radians(20 + k * 140 / n); a1 = math.radians(20 + (k + 1) * 140 / n)
        if abs(math.degrees(a0) - (90.0 - 28.0)) < 6:          # gap where the bridge lands
            continue
        p0 = Vector((PIT_C[0] + 24.0 * math.cos(a0), PIT_C[1] + 24.0 * math.sin(a0)))
        p1 = Vector((PIT_C[0] + 24.0 * math.cos(a1), PIT_C[1] + 24.0 * math.sin(a1)))
        dv = p1 - p0
        obox(bm, (p0 + p1) / 2, dv.normalized(), Vector((-dv.y, dv.x)).normalized(), dv.length, 0.12, 1.0, 1.15, 4)
        obox(bm, p0, dv.normalized(), Vector((-dv.y, dv.x)).normalized(), 0.15, 0.15, 0.0, 1.15, 4)
    _mk("TrostRingPit", bm, [MT["ground_m"], MT["plank_h"], MT["timber_d"], MT["plank_t"], MT["timber_d"], MT["puddle"], MT["mud"]], pc)
    # ---------------- plank boxes, bollards, trees, log cribs
    bm = bmesh.new()
    for x, y in ANCHORS_M["PLANK_BOX"]:
        box(bm, (x, y, 1.25), (4.0, 4.0, 2.5), mi=0)
        box(bm, (x, y, 2.55), (4.3, 4.3, 0.1), mi=1)
    for x, y in ANCHORS_M["BO"]:
        cyl(bm, (x, y, 0.0), (x, y, 1.5), 0.3, 0.27, seg=10, mi=2)
        cyl(bm, (x, y, 1.5), (x, y, 1.65), 0.27, 0.12, seg=10, mi=2)
    box(bm, (0.0, 31.2, 0.12), (21.0, 1.6, 0.24), mi=0)                       # plank deck edge behind the bollards
    # log-crib fences between the pit slabs (crossed logs ~3 m)
    keys = sorted(SLABS)
    for name_a, name_b in (("TrostSlab_P1", "TrostSlab_P2"), ("TrostSlab_P2", "TrostSlab_P3"), ("TrostSlab_P3", "TrostSlab_P4"),
                           ("TrostSlab_P4", "TrostSlab_P5"), ("TrostSlab_A2", "TrostSlab_A3"), ("TrostSlab_A6", "TrostSlab_A7")):
        (xa, ya, _), (xb, yb, _) = SLABS[name_a], SLABS[name_b]
        pa, pb = Vector((xa, ya)), Vector((xb, yb))
        dv = pb - pa; ln = dv.length; dvn = dv.normalized()
        q0 = pa + dvn * 4.5; q1 = pb - dvn * 4.5
        m_ = int((q1 - q0).length / 2.2)
        for k in range(m_ + 1):
            q = q0 + (q1 - q0) * (k / max(1, m_))
            nrm = Vector((-dvn.y, dvn.x))
            for sgn in (-1, 1):
                a_ = q + nrm * 0.0 + dvn * (sgn * 1.0)
                b_ = q - dvn * (sgn * 1.0)
                cyl(bm, (a_.x, a_.y, 0.0), (b_.x, b_.y, 3.0), 0.18, seg=5, mi=3)
        for z in (0.8, 2.2):
            cyl(bm, (q0.x, q0.y, z), (q1.x, q1.y, z), 0.16, seg=5, mi=3)
    _mk("TrostGateProps", bm, [MT["crate_t"], MT["timber_d"], MT["bollard"], MT["timber_d"]], pc)
    # trees at the wall foot either side of the gatehouse
    bm = bmesh.new()
    for x, y in ANCHORS_M["TR_spruce"]:
        h = 10.5 + rnd.uniform(-1, 1.5)
        cyl(bm, (x, y, 0), (x, y, h * 0.3), 0.35, seg=6, mi=0)
        for tier in range(5):
            cyl(bm, (x, y, h * (0.2 + tier * 0.15)), (x, y, h * (0.2 + tier * 0.15) + h * 0.32), 2.6 - tier * 0.45, 0.15, seg=9, mi=1)
    for x, y in ANCHORS_M["TR_bushy"]:
        cyl(bm, (x, y, 0), (x, y, 3.5), 0.45, seg=6, mi=0)
        for k in range(5):
            rock_blob(bm, (x + rnd.uniform(-1.8, 1.8), y + rnd.uniform(-1.8, 1.8), 5.0 + rnd.uniform(0, 2.5)), (2.8, 2.8, 2.6), rnd, 2, 2, 1.0, 0.2)
    _mk("TrostGateTrees", bm, [MT["bark_t"], MT["spruce"], MT["tree_dark"]], pc)
    # ---------------- slabs (separate objects, others animate them)
    sm = _slab_mesh(MT)
    slab_c = _coll("TrostSlabs")
    for name_, (x, y, yaw) in SLABS.items():
        o = bpy.data.objects.new(name_, sm)
        o.location = M(x, y, 0.0); o.rotation_euler.z = math.radians(yaw)
        slab_c.objects.link(o)
    # ---------------- craters + small holes (post-kick) and their turf caps (pre-kick)
    for i, (cx, cy, r) in enumerate(CRATERS_M + HOLES_M):
        big = r > 3
        bm = bmesh.new()
        segc = 28
        nring = 6
        prev = None
        for j in range(nring + 1):
            f = max(j / nring, 0.0)
            rr = r * f
            if j == 0:
                prev = [bm.verts.new((cx, cy, -(2.0 if big else 2.6)))] * segc
                continue
            zz = -(2.0 if big else 2.6) * (1 - f * f)
            ring = []
            for k in range(segc):
                a = k * math.tau / segc
                jag = 1.0 + (0.18 * noise.noise(Vector((math.cos(a) * 2 + i, math.sin(a) * 2, 0.5))) if j == nring else 0.0)
                ring.append(bm.verts.new((cx + rr * jag * math.cos(a), cy + rr * jag * math.sin(a), zz)))
            if prev:
                for k in range(segc):
                    if j == 1:
                        bm.faces.new((prev[k], ring[k], ring[(k + 1) % segc])).material_index = 0
                    else:
                        bm.faces.new((prev[k], ring[k], ring[(k + 1) % segc], prev[(k + 1) % segc])).material_index = 0
            prev = ring
        fill_ring(bm, (cx, cy), r * 1.0, r + 7.5, -0.2, seg=segc, mi=2)
        for k in range(22 if big else 9):                            # splintered lip
            a = rnd.uniform(0, math.tau); rr = r * rnd.uniform(0.95, 1.25)
            p0 = (cx + rr * math.cos(a), cy + rr * math.sin(a), 0.0)
            p1 = (cx + (rr + rnd.uniform(0.6, 1.8)) * math.cos(a + rnd.uniform(-0.2, 0.2)), cy + (rr + rnd.uniform(0.6, 1.8)) * math.sin(a), rnd.uniform(0.4, 1.4))
            tube(bm, [p0, p1], rnd.uniform(0.15, 0.35), 0.03, 3, mi=1)
        ob = _mk(f"GS_Crater{i}", bm, [MT["mud"], MT["turf_t"], MT["ground_m"]], pc)
        bm = bmesh.new()
        fill_disc(bm, (cx, cy), r + 7.5, -0.1, seg=segc, mi=0)
        _mk(f"GS_CraterCap{i}", bm, [MT["ground_m"]], pc)
        _hide(ob)
    # pre-kick: slabs + cribs stand; the pale path ring-road -> bridge is in the ground shader
    return pc

# ====================================================================================== the ball + Boulder Court
def boulder_mesh(name="TrostBoulderMesh", origin="center"):
    """The ball: 14.0 x 14.0 x 13.6 near-sphere, low-frequency +-0.25 m only (stays round, owner 15:29).
    origin = "center" (default, as TrostBoulder) or "bottom" (bottom centre)."""
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=64, v_segments=32, radius=1.0)
    rx, ry, rz = BOULDER_SIZE[0] / 2, BOULDER_SIZE[1] / 2, BOULDER_SIZE[2] / 2
    for v in bm.verts:
        n = v.co.normalized()
        d = 0.25 * noise.noise(n * 0.9 + Vector((3.1, 1.7, 7.3))) + 0.08 * noise.noise(n * 2.2 + Vector((1, 9, 2)))
        v.co = Vector((n.x * (rx + d), n.y * (ry + d), n.z * (rz + d)))
    if origin == "bottom":
        zmin = min(v.co.z for v in bm.verts)
        for v in bm.verts:
            v.co.z -= zmin
    for f in bm.faces:
        f.smooth = True
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    return me

def build_boulder_court(MT):
    """B0: the ball on its raised octagonal lawn bed (kerb, 14-rock ring, shrubs, 2 cypress + 1 leafy tree), rubble skirt,
    second rock; the court's terraces/belfry/lane are placed by the town builder (explicit court houses)."""
    rnd = random.Random(51)
    cc = _coll("TrostBoulderCourt")
    bx, by, bz = BOULDER_CENTER_M
    # lawn bed: octagon 30 m across flats, 0.6 m kerb
    bm = bmesh.new()
    Rf = 15.0 / math.cos(math.radians(22.5))
    top = [bm.verts.new((bx + Rf * math.cos(math.radians(22.5 + 45 * k)), by + Rf * math.sin(math.radians(22.5 + 45 * k)), 0.6)) for k in range(8)]
    bm.faces.new(top).material_index = 0
    for k in range(8):
        a0, a1 = math.radians(22.5 + 45 * k), math.radians(22.5 + 45 * (k + 1))
        p0 = Vector((bx + (Rf + 0.25) * math.cos(a0), by + (Rf + 0.25) * math.sin(a0)))
        p1 = Vector((bx + (Rf + 0.25) * math.cos(a1), by + (Rf + 0.25) * math.sin(a1)))
        dv = p1 - p0
        obox(bm, (p0 + p1) / 2, dv.normalized(), Vector((-dv.y, dv.x)).normalized(), dv.length + 0.6, 0.6, -0.5, 0.7, 1)
    hexa(bm, [(bx - 15, by - 15, -0.5), (bx + 15, by - 15, -0.5), (bx + 15, by + 15, -0.5), (bx - 15, by + 15, -0.5),
              (bx - 15, by - 15, 0.55), (bx + 15, by - 15, 0.55), (bx + 15, by + 15, 0.55), (bx - 15, by + 15, 0.55)], 1)
    for k in range(14):                                       # ring of dark angular rocks on the rim
        a = k * math.tau / 14 + rnd.uniform(-0.08, 0.08)
        rr = Rf * 0.93
        s_ = rnd.uniform(2.0, 3.5)
        rock_blob(bm, (bx + rr * math.cos(a), by + rr * math.sin(a), 0.6 + s_ * 0.25), (s_ * 0.6, s_ * 0.5, s_ * 0.55), rnd, 1, 2, 0.9, 0.35)
    for k in range(17):                                       # rubble skirt on the bed around the ball
        a = rnd.uniform(0, math.tau); rr = rnd.uniform(7.2, 10.5)
        s_ = rnd.uniform(1.0, 3.0)
        rock_blob(bm, (bx + rr * math.cos(a), by + rr * math.sin(a), 0.6 + s_ * 0.2), (s_ * 0.55, s_ * 0.5, s_ * 0.45), rnd, 1, 3, 0.9, 0.3)
    for k in range(5):                                        # shrubs
        a = rnd.uniform(1.6, 3.6); rr = rnd.uniform(10.5, 12.5)
        rock_blob(bm, (bx + rr * math.cos(a), by + rr * math.sin(a), 1.4), (1.5, 1.5, 1.4), rnd, 2, 4, 1.0, 0.2)
    _mk("TrostBoulderBed", bm, [MT["lawn"], MT["cornice"], MT["rock_court"], MT["rock_pale"], MT["shrub"]], cc)
    # trees at the bed's NW edge: 2 slim cypress + 1 leafy
    bm = bmesh.new()
    for k, (dx, dy) in enumerate(((-9.5, 9.0), (-12.0, 5.5))):
        x, y = bx + dx, by + dy
        cyl(bm, (x, y, 0.6), (x, y, 2.0), 0.3, seg=6, mi=0)
        cyl(bm, (x, y, 1.5), (x, y, 12.5), 1.4, 0.15, seg=8, mi=1)
        rock_blob(bm, (x, y, 5.0), (1.5, 1.5, 3.6), rnd, 2, 1, 1.0, 0.1)
    x, y = bx - 7.0, by + 12.0
    cyl(bm, (x, y, 0.6), (x, y, 4.5), 0.4, seg=6, mi=0)
    for k in range(5):
        rock_blob(bm, (x + rnd.uniform(-2, 2), y + rnd.uniform(-2, 2), 6.5 + rnd.uniform(0, 2)), (3.0, 3.0, 2.6), rnd, 2, 2, 1.0, 0.2)
    _mk("TrostBedTrees", bm, [MT["bark_t"], MT["spruce"], MT["leafy"]], cc)
    # the ball (origin at its centre)
    me = boulder_mesh("TrostBoulderMesh", "center")
    me.materials.append(MT["ball"])
    ob = bpy.data.objects.new("TrostBoulder", me); cc.objects.link(ob)
    ob.location = M(*BOULDER_CENTER_M); ob.rotation_euler.z = math.radians(28)
    # the second rock (6 m, lumpy) on the cobbles
    bm = bmesh.new()
    rock_blob(bm, (0, 0, 3.0), (3.4, 3.0, 3.6), rnd, 3, 0, 0.95, 0.28)
    r2 = _mk_at("TrostRock2", bm, [MT["rock2"]], (308.0, 247.0, 0.0), cc)
    # broken, pushed-up paving within 4 m of the ball is in the bed's rubble skirt
    _ball_contact("TrostBallContactB0", (bx, by), 0.6, MT, coll=cc)          # QA 10/26: contact shadow + dust ring (heavy)
    return ob

def build_strip(MT):
    """SE wall-foot strip (r 437..475 about (0, 480), phi 8-37): open dusty ground with X-fences in short runs, plank
    ramps leaning on the wall, 4 sheds against the wall, crates, toppled spiked slabs; the carry lane r 446..464 stays
    clear."""
    rnd = random.Random(61)
    sc = _coll("TrostStrip")
    bm = bmesh.new()
    def P(r, ph):
        a = math.radians(ph)
        return Vector((480.0 * 0 + r * math.sin(a), 480.0 - r * math.cos(a)))
    def tang(ph):
        a = math.radians(ph)
        return Vector((math.cos(a), math.sin(a)))
    # X-fences: short runs on the inner edge (r 440)
    for ph0 in (10.0, 17.0, 24.5, 31.0):
        for k in range(rnd.randint(3, 5)):
            ph = ph0 + k * 0.42
            p = P(440.5 + rnd.uniform(-0.6, 0.6), ph); t = tang(ph)
            for sgn in (-1, 1):
                a_ = p + t * (sgn * 1.0); b_ = p - t * (sgn * 1.0)
                cyl(bm, (a_.x, a_.y, 0.0), (b_.x, b_.y, 2.2), 0.13, seg=5, mi=0)
            q0, q1 = p - t * 1.6, p + t * 1.6
            cyl(bm, (q0.x, q0.y, 1.1), (q1.x, q1.y, 1.1), 0.1, seg=5, mi=0)
    # sheds against the wall (r 466..472)
    for ph in (12.5, 21.0, 28.5, 34.5):
        p = P(468.0, ph); t = tang(ph); n = Vector((-math.sin(math.radians(ph)), math.cos(math.radians(ph))))
        obox(bm, p, t, n, 6.0, 4.5, 0.0, 3.0, 1)
        hexa(bm, [(*(p + t * -3.3 + n * -2.6), 3.0), (*(p + t * 3.3 + n * -2.6), 3.0), (*(p + t * 3.3 + n * 2.6), 4.4), (*(p + t * -3.3 + n * 2.6), 4.4),
                  (*(p + t * -3.3 + n * -2.6), 3.2), (*(p + t * 3.3 + n * -2.6), 3.2), (*(p + t * 3.3 + n * 2.6), 4.6), (*(p + t * -3.3 + n * 2.6), 4.6)], 2)
    # plank ramps leaning on the wall
    for ph in (9.5, 16.0, 25.5, 32.5):
        p = P(469.0, ph); t = tang(ph); n = Vector((-math.sin(math.radians(ph)), math.cos(math.radians(ph))))
        a_ = p + n * 3.0
        b_ = p + n * (-2.4)
        hexa(bm, [(*(a_ - t * 1.5), 0.0), (*(a_ + t * 1.5), 0.0), (*(a_ + t * 1.5), 0.25), (*(a_ - t * 1.5), 0.25),
                  (*(b_ - t * 1.5), 7.0), (*(b_ + t * 1.5), 7.0), (*(b_ + t * 1.5), 7.25), (*(b_ - t * 1.5), 7.25)], 3)
    # crates
    for k in range(9):
        ph = rnd.uniform(9, 36); p = P(rnd.choice((441.5, 466.0)) + rnd.uniform(-0.5, 0.5), ph)
        for j in range(rnd.randint(1, 3)):
            box(bm, (p.x + rnd.uniform(-1, 1), p.y + rnd.uniform(-1, 1), 0.5 + j * 0.0), (1.0, 1.0, 1.0), rot=rnd.uniform(0, 3), mi=4)
    _mk("TrostStripProps", bm, [MT["timber_d"], MT["plank_h"], MT["roof_red_t"], MT["plank_t"], MT["crate_t"]], sc)
    # two toppled slabs lying at the inner edge
    sm = _slab_mesh(MT)
    for k, ph in enumerate((14.0, 29.0)):
        p = P(441.0, ph)
        o = bpy.data.objects.new(f"TrostStripSlab{k}", sm)
        o.location = M(p.x, p.y, 2.0); o.rotation_euler = (math.radians(-90), 0.0, math.radians(ph + 90 + rnd.uniform(-10, 10)))
        sc.objects.link(o)
    return sc

# ====================================================================================== canal CAN (one, green)
def build_canal(MT):
    """Single canal: water Z -4.2, stepped stone banks, quay coping + bollards, fill strips over the floor's cut,
    pillar-portal bridges at Y 420/560/700/820 (+2 outside), the Rose water gate and the east-wall exit gate."""
    rnd = random.Random(71)
    cc = _coll("TrostCanal")
    pts = CANAL_LINE_M
    inside = [p for p in pts if wall_dist_m(*p) > -6.0 or p[1] > 860]
    outside = [p for p in pts if wall_dist_m(*p) <= 6.0 and p[1] < 400]
    hw = 13.0
    prof_l = [(-13.0, 0.0), (-13.0, -1.6), (-11.5, -1.6), (-11.5, -6.5)]   # (offset, z) one bank
    def bank_strip(bm, line, side):
        n = len(line)
        rows = []
        for k, p in enumerate(line):
            a = line[max(k - 1, 0)]; b = line[min(k + 1, n - 1)]
            t = Vector((b[0] - a[0], b[1] - a[1])).normalized(); nr = Vector((-t.y, t.x)) * side
            rows.append([bm.verts.new((p[0] - nr.x * o, p[1] - nr.y * o, z)) for o, z in prof_l])
        for k in range(n - 1):
            for e in range(len(prof_l) - 1):
                bm.faces.new((rows[k][e], rows[k][e + 1], rows[k + 1][e + 1], rows[k + 1][e])).material_index = 0
    def strip(bm, line, o0, o1, z, mi):
        n = len(line); L_, R_ = [], []
        for k, p in enumerate(line):
            a = line[max(k - 1, 0)]; b = line[min(k + 1, n - 1)]
            t = Vector((b[0] - a[0], b[1] - a[1])).normalized(); nr = Vector((-t.y, t.x))
            L_.append(bm.verts.new((p[0] + nr.x * o0, p[1] + nr.y * o0, z))); R_.append(bm.verts.new((p[0] + nr.x * o1, p[1] + nr.y * o1, z)))
        for k in range(n - 1):
            bm.faces.new((L_[k], R_[k], R_[k + 1], L_[k + 1])).material_index = mi
    bm = bmesh.new()
    for line in (inside, outside):
        if len(line) < 2:
            continue
        bank_strip(bm, line, 1); bank_strip(bm, line, -1)
        strip(bm, line, -11.6, 11.6, -6.4, 3)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    _mk("CanalBanks", bm, [MT["bank"], MT["quay"], MT["water_c"], MT["canal_bed"]], cc)
    bm = bmesh.new()
    for line in (inside, outside):
        if len(line) >= 2:
            strip(bm, line, -11.7, 11.7, CANAL_WATER_Z, 0)
    _mk("CanalWater", bm, [MT["water_c"]], cc)
    # quay coping + fill over the floor cut (inside: town floor material; outside: the scene meadow)
    bm = bmesh.new()
    for side in (-1, 1):
        o0, o1 = (13.0, 13.9) if side > 0 else (-13.9, -13.0)
        strip(bm, inside, o0, o1, 0.12, 0)
        strip(bm, inside, (13.9, 20.5)[0] * side if side > 0 else -20.5, 20.5 if side > 0 else -13.9, -0.2, 1)
    _mk("CanalQuays", bm, [MT["quay"], MT["ground_m"]], cc)
    bm = bmesh.new()
    terr_m = L.terrain_mat() if bpy.data.materials.get("Terrain") is None else bpy.data.materials["Terrain"]
    for side in (-1, 1):
        strip(bm, outside, 13.0 if side > 0 else -20.5, 20.5 if side > 0 else -13.0, -0.25, 0)
    for v in bm.verts:
        v.co.y += DY
    L.obj_from_bm("CanalFillOut", bm, [terr_m], cc)
    # bollards on the quays
    bm = bmesh.new()
    for line in (inside,):
        acc = 0.0
        for k in range(1, len(line)):
            acc += math.hypot(line[k][0] - line[k - 1][0], line[k][1] - line[k - 1][1])
            if acc >= 12.0:
                acc = 0.0
                a = line[k - 1]; b = line[k]
                t = Vector((b[0] - a[0], b[1] - a[1])).normalized(); nr = Vector((-t.y, t.x))
                for side in (-1, 1):
                    q = Vector(b) + nr * (side * 13.5)
                    if abs(q.y - 870) < 20:
                        continue
                    cyl(bm, (q.x, q.y, 0.1), (q.x, q.y, 1.0), 0.22, 0.18, seg=8, mi=0)
    _mk("CanalBollards", bm, [MT["iron_t"]], cc)
    # pillar-portal bridges (flat deck + paired tall pale pillars joined overhead by a beam)
    bm = bmesh.new()
    br_pts = [(400.0, float(y), 0.0) for y in ANCHORS_M["CAN_BRIDGES_Y"]]
    for frac in (0.25, 0.6):
        k = int(len(outside) * frac)
        if 0 < k < len(outside) - 1:
            a, b = outside[k - 1], outside[k + 1]
            br_pts.append((outside[k][0], outside[k][1], math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])) + 90))
    for x, y, rot_deg in br_pts:
        rot = math.radians(rot_deg)
        t = Vector((math.cos(rot), math.sin(rot))); n = Vector((-t.y, t.x))
        c = Vector((x, y))
        obox(bm, c, t, n, 30.0, 9.0, -0.9, 0.35, 0)
        for s_ in (-1, 1):
            obox(bm, c + n * (s_ * 4.7), t, n, 30.0, 0.5, 0.35, 1.3, 0)
            for e in (-1, 1):
                q = c + t * (e * 14.0) + n * (s_ * 4.9)
                obox(bm, q, t, n, 1.4, 1.4, 0.35, 9.5, 1)
                obox(bm, q, t, n, 1.8, 1.8, 9.5, 10.1, 1)
            for e in (-1, 1):
                q = c + t * (e * 14.0)
                obox(bm, q, n, t, 11.4, 1.0, 8.6, 9.6, 1)
        obox(bm, c, t, n, 3.0, 9.0, -6.0, -0.9, 0)
    _mk("CanalBridges", bm, [MT["quay"], MT["cornice"]], cc)
    # water gates: Rose (X 393..411, crown Z 2.8) with portcullis + piers narrowing the canal; east-wall exit
    bm = bmesh.new()
    box(bm, (402.0, 870.0, 27.0), (19.4, 10.2, 48.4), mi=0)
    for sx in (-1, 1):
        box(bm, (402.0 + sx * 8.9, 870.0, -2.0), (1.6, 10.2, 9.6), mi=0)
    for k in range(13):
        x = 393.0 + 0.75 + k * 1.5
        box(bm, (x, 864.6, -1.6), (0.35, 0.35, 8.8), mi=1)
    for z in (-2.5, 0.0, 2.2):
        box(bm, (402.0, 864.6, z), (18.0, 0.3, 0.3), mi=1)
    box(bm, (402.0, 869.0, -1.0), (17.6, 9.0, 7.6), mi=2)                       # dark tunnel behind the grille
    box(bm, (415.0, 861.0, -2.0), (8.0, 8.0, 9.6), mi=0)                         # east narrowing pier (mirror of PE)
    a = math.atan2(300.0 - 480.0, 445.0)
    t = Vector((-math.sin(a), math.cos(a))); n = Vector((math.cos(a), math.sin(a)))
    c = Vector((445.0, 300.0))
    obox(bm, c, t, n, 34.0, 10.3, 2.8, 51.3, 0)
    for s_ in (-1, 1):
        obox(bm, c + t * (s_ * 14.5), t, n, 5.0, 10.3, -6.0, 2.8, 0)
    for k in range(17):
        q = c + t * (-12.0 + k * 1.5) + n * 5.2
        obox(bm, q, t, n, 0.35, 0.35, -6.0, 2.6, 1)
    obox(bm, c, t, n, 24.0, 9.0, -6.0, 2.6, 2)
    _mk("WaterGates", bm, [MT["wall_t"], MT["iron_t"], MT["window_t"]], cc)
    return cc

# ====================================================================================== town fabric (terraces)
HOUSE_VARIANTS = []          # [(name, w, d, H, kind, pool)]
HOUSES = []                  # placed: dict(x, y, ang, v, sx, sy, z, w, d)
_OCC = {}

def _house_mesh(name, w, d, storeys, roof, dormers, chimneys, stepped, rnd, mats):
    gf = 3.6
    Ht = gf + (storeys - 1) * 3.2
    bm = bmesh.new()
    box(bm, (0, 0, (gf - 3.0) / 2), (w, d, gf + 3.0), mi=0)
    box(bm, (0, 0, (gf + Ht) / 2), (w, d, Ht - gf), mi=0)
    o = 0.45
    if roof in ("eave", "hip"):
        rise = d * 0.5 * rnd.uniform(0.95, 1.12)
        ins = w * 0.32 if roof == "hip" else 0.0
        p = [bm.verts.new(c) for c in ((-w / 2, -d / 2 - o, Ht - 0.35), (w / 2, -d / 2 - o, Ht - 0.35), (w / 2, d / 2 + o, Ht - 0.35),
                                        (-w / 2, d / 2 + o, Ht - 0.35), (-w / 2 + ins, 0, Ht + rise), (w / 2 - ins, 0, Ht + rise))]
        bm.faces.new((p[0], p[1], p[5], p[4])).material_index = 2
        bm.faces.new((p[3], p[4], p[5], p[2])).material_index = 2
        bm.faces.new((p[0], p[4], p[3])).material_index = 2 if roof == "hip" else 0
        bm.faces.new((p[1], p[2], p[5])).material_index = 2 if roof == "hip" else 0
        bm.faces.new((p[0], p[3], p[2], p[1])).material_index = 2
        # dormers on both slopes
        for side in (-1, 1):
            nd = dormers[0 if side < 0 else 1]
            for k in range(nd):
                x = (k - (nd - 1) / 2) * (w / max(1, nd)) * 0.85
                if abs(x) > w / 2 - 1.2:
                    continue
                yf = side * (d / 2 - d * 0.18)
                zb = Ht + rise * 0.18
                dz = 1.7
                box(bm, (x, yf + side * 0.0, zb + dz / 2 - 0.3), (1.5, 1.9, dz + 0.6), mi=0)
                q = [bm.verts.new(c) for c in ((x - 0.95, yf + side * 1.1, zb + dz), (x + 0.95, yf + side * 1.1, zb + dz), (x + 0.95, yf - side * 1.2, zb + dz),
                                               (x - 0.95, yf - side * 1.2, zb + dz), (x, yf + side * 1.1, zb + dz + 0.9), (x, yf - side * 1.2, zb + dz + 0.9))]
                bm.faces.new((q[0], q[1], q[4])).material_index = 0
                bm.faces.new((q[0], q[4], q[5], q[3])).material_index = 2
                bm.faces.new((q[1], q[2], q[5], q[4])).material_index = 2
                box(bm, (x, yf + side * 0.97, zb + dz * 0.45), (0.8, 0.06, 1.0), mi=3)
        ridge = Ht + rise
        for k in range(chimneys):
            x = rnd.uniform(-w / 2 + 1.2, w / 2 - 1.2)
            y = rnd.uniform(-d * 0.15, d * 0.15)
            box(bm, (x, y, ridge - 1.0 + 1.0), (0.9, 0.9, 3.0 + rnd.uniform(0, 1.0)), mi=4)
    else:   # gable-front: ridge along y, gable on the street face, optional crow-stepped gable
        rise = w * 0.5 * rnd.uniform(1.1, 1.3)
        p = [bm.verts.new(c) for c in ((-w / 2 - o, -d / 2, Ht - 0.35), (w / 2 + o, -d / 2, Ht - 0.35), (w / 2 + o, d / 2, Ht - 0.35),
                                        (-w / 2 - o, d / 2, Ht - 0.35), (0, -d / 2, Ht + rise), (0, d / 2, Ht + rise))]
        bm.faces.new((p[0], p[4], p[5], p[3])).material_index = 2
        bm.faces.new((p[1], p[2], p[5], p[4])).material_index = 2
        bm.faces.new((p[0], p[1], p[4])).material_index = 0
        bm.faces.new((p[2], p[3], p[5])).material_index = 0
        bm.faces.new((p[0], p[3], p[2], p[1])).material_index = 2
        if stepped:
            nst = 5
            for k in range(nst):
                f0 = k / nst; f1 = (k + 1) / nst
                for sx in (-1, 1):
                    x0 = sx * (w / 2) * (1 - f0); x1 = sx * (w / 2) * (1 - f1)
                    z1 = Ht + rise * f1 + 0.5
                    box(bm, ((x0 + x1) / 2, -d / 2 + 0.3, (Ht - 0.4 + z1) / 2), (abs(x0 - x1) + 0.05, 0.6, z1 - Ht + 0.4), mi=0)
            box(bm, (0, -d / 2 + 0.3, Ht + rise + 0.9), (0.9, 0.6, 1.2), mi=0)
        for k in range(chimneys):
            box(bm, (rnd.uniform(-w * 0.2, w * 0.2), rnd.uniform(-d * 0.2, d * 0.3), Ht + rise - 0.5), (0.9, 0.9, 3.2), mi=4)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for m_ in mats:
        me.materials.append(m_)
    return me, Ht

def _make_variants(MT, coll, meshes=True):
    rnd = random.Random(81)
    HOUSE_VARIANTS.clear()
    def add(pool, fac, gf_mat_key=None):
        st = rnd.choices((3, 4, 5), (25, 60, 15))[0]
        roof = rnd.choices(("eave", "gable", "hip"), (70, 18, 12))[0] if pool != "arcade" else rnd.choices(("eave", "hip"), (85, 15))[0]
        w = rnd.choice((8.0, 9.0, 10.0, 11.0))
        d = rnd.choice((11.0, 12.0, 13.0, 14.0))
        dorm = (rnd.randint(0, 3), rnd.randint(0, 3))
        chim = rnd.randint(1, 3)
        stepped = roof == "gable" and rnd.random() < 0.6
        civic = rnd.random() < 0.05
        name = f"TV{len(HOUSE_VARIANTS):02d}"
        Ht = 3.6 + (st - 1) * 3.2
        if meshes:
            roofm = MT["roof_civic"] if civic else MT["roof_town"]
            me, Ht = _house_mesh(name, w, d, st, roof, dorm, chim, stepped, rnd, [MT[fac], MT[fac], roofm, MT["window_t"], MT["chimney"]])
            ob = bpy.data.objects.new(name, me); coll.objects.link(ob); ob.location = (0, 0, -6000)
        else:
            rnd.random(); rnd.random()
        HOUSE_VARIANTS.append((name, w, d, Ht, roof, pool))
    for k in range(16):
        add("plain", rnd.choice(("f_cream", "f_sand", "f_grey", "f_cream", "f_sand", "f_brick")))
    for k in range(14):
        add("timber", rnd.choice(("f_tcream", "f_tochre", "f_tcream")))
    for k in range(10):
        add("arcade", rnd.choice(("f_arc_cream", "f_arc_sand", "f_arc_timber")))
    return HOUSE_VARIANTS

def _pools():
    p = {}
    for i, v in enumerate(HOUSE_VARIANTS):
        p.setdefault(v[5], []).append(i)
    return p

def _obb(x, y, w, d, ang):
    return (x, y, w / 2, d / 2, math.cos(ang), math.sin(ang))

def _obb_corners(o, shrink=0.0):
    x, y, hx, hy, c, s_ = o
    hx -= shrink; hy -= shrink
    return [(x + c * sx * hx - s_ * sy * hy, y + s_ * sx * hx + c * sy * hy) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]

def _obb_overlap(a, b, shrink=0.25):
    ca, cb = _obb_corners(a, shrink), _obb_corners(b, shrink)
    for o in (a, b):
        for ax in ((o[4], o[5]), (-o[5], o[4])):
            pa = [p[0] * ax[0] + p[1] * ax[1] for p in ca]
            pb = [p[0] * ax[0] + p[1] * ax[1] for p in cb]
            if max(pa) < min(pb) or max(pb) < min(pa):
                return False
    return True

def _occ_add(o, tag="house"):
    r = math.hypot(o[2], o[3])
    for i in range(int((o[0] - r) // 24), int((o[0] + r) // 24) + 1):
        for j in range(int((o[1] - r) // 24), int((o[1] + r) // 24) + 1):
            _OCC.setdefault((i, j), []).append(o)

def _occ_free(o):
    r = math.hypot(o[2], o[3])
    seen = set()
    for i in range(int((o[0] - r) // 24), int((o[0] + r) // 24) + 1):
        for j in range(int((o[1] - r) // 24), int((o[1] + r) // 24) + 1):
            for q in _OCC.get((i, j), ()):
                if id(q) in seen:
                    continue
                seen.add(id(q))
                if _obb_overlap(o, q):
                    return False
    return True

def _house_reserved(X, Y):
    """Places where generic terraces may not stand (plazas, squares, special builds, the canal, the carry lane)."""
    if not in_district_m(X, Y, 14.0):
        return True
    if math.hypot(X, Y) < 80.0:
        return True
    if math.hypot(X - C_XY[0], Y - C_XY[1]) < 45.0:
        return True
    if _in_rect(X, Y, (-302, -98, 566, 626)) or _in_rect(X, Y, (-302, -264, 566, 662)) or _in_rect(X, Y, (-272, -134, 610, 702)):
        return True                                                 # HQ plaza, west strip, keep/wing/back range (block 7)
    if _in_rect(X, Y, (-182, -60, 796, 870)) or _in_rect(X, Y, (-200, -178, 845, 870)):   # E, bastion, slope, terrace
        return True
    if _in_rect(X, Y, (225, 318, 236, 292)) or _in_rect(X, Y, (276, 292, 225, 238)):      # court + exit gap
        return True
    if canal_dist_m(X, Y) < 22.5:                                   # canal + quays
        return True
    if _in_rect(X, Y, (300, 400, 768, 870)):                       # cannon basin complex (block 8)
        return True
    if _in_rect(X, Y, (-336, -200, 757, 870)):                     # relief complex RC
        return True
    if X < -405 and Y > 788:                                        # decoy pocket D (open)
        return True
    if _in_rect(X, Y, (-254, -214, 486, 528)):                     # Q2 + tower T (block 6)
        return True
    if _in_rect(X, Y, (-288, -238, 376, 462)):                     # MA + its special flanks
        return True
    if in_strip_m(X, Y, 2.0):
        return True
    for _, (tx, ty, sd, h, cap) in TOWERS_M.items():
        if abs(X - tx) < sd / 2 + 2.5 and abs(Y - ty) < sd / 2 + 2.5:
            return True
    for lx, ly in LIFT_PTS:
        if math.hypot(X - lx, Y - ly) < 14.0:
            return True
    for p in ANCHORS_M["PYR"]:
        if math.hypot(X - p[0], Y - p[1]) < 6.0:
            return True
    return False

_MASK = {}
MASK_G = 2.0
def _build_mask():
    """2 m raster of the district: bit 1 = street (+0.3 m), bit 2 = reserved for special builds / open ground."""
    if _MASK:
        return _MASK
    nx, ny = int(960 / MASK_G), int(870 / MASK_G)
    m = bytearray(nx * ny)
    for iy in range(ny):
        Y = (iy + 0.5) * MASK_G
        for ix in range(nx):
            X = -480.0 + (ix + 0.5) * MASK_G
            if _house_reserved(X, Y):
                m[iy * nx + ix] = 2
    for pts, hw, kind in streets_m():
        rr = hw + 0.3
        for k in range(len(pts) - 1):
            ax, ay = pts[k]; bx, by = pts[k + 1]
            n = max(1, int(math.hypot(bx - ax, by - ay) / 1.0))
            for t in range(n + 1):
                X, Y = ax + (bx - ax) * t / n, ay + (by - ay) * t / n
                i0, i1 = int((X - rr + 480) / MASK_G), int((X + rr + 480) / MASK_G)
                j0, j1 = int((Y - rr) / MASK_G), int((Y + rr) / MASK_G)
                for j in range(max(0, j0), min(ny - 1, j1) + 1):
                    cy = (j + 0.5) * MASK_G
                    for i in range(max(0, i0), min(nx - 1, i1) + 1):
                        cx = -480.0 + (i + 0.5) * MASK_G
                        if (cx - X) ** 2 + (cy - Y) ** 2 <= rr * rr:
                            m[j * nx + i] |= 1
    _MASK.update(m=m, nx=nx, ny=ny)
    return _MASK

def _mask_bad(X, Y):
    mk = _MASK
    i, j = int((X + 480.0) / MASK_G), int(Y / MASK_G)
    if i < 0 or j < 0 or i >= mk["nx"] or j >= mk["ny"]:
        return True
    return mk["m"][j * mk["nx"] + i] != 0

def _fits(o):
    pts = _obb_corners(o, 0.35) + [(o[0], o[1])]
    x, y, hx, hy, c, s_ = o
    pts += [(x + c * hx * 0.97, y + s_ * hx * 0.97), (x - c * hx * 0.97, y - s_ * hx * 0.97),
            (x - s_ * hy * 0.97, y + c * hy * 0.97), (x + s_ * hy * 0.97, y - c * hy * 0.97),
            (x + c * hx * 0.5, y + s_ * hx * 0.5), (x - c * hx * 0.5, y - s_ * hx * 0.5)]
    for X, Y in pts:
        if _mask_bad(X, Y):
            return False
    return _occ_free(o)

def _place(x, y, ang, v, sx=1.0, sy=1.0, force=False, tag=None):
    name, w, d, Ht, roof, pool = HOUSE_VARIANTS[v]
    o = _obb(x, y, w * sx, d * sy, ang)
    if not force and not _fits(o):
        return None
    _occ_add(o)
    h = dict(x=x, y=y, ang=ang, v=v, sx=sx, sy=sy, z=ground_z_m(x, y), w=w * sx, d=d * sy, tag=tag, obb=o)
    HOUSES.append(h)
    return h

def _pick(pool, rnd, Y=0.0):
    P = _pools()
    if pool == "auto":
        pool = "timber" if rnd.random() < (0.55 if Y < 435 else 0.3) else "plain"
    return rnd.choice(P[pool])

def block_footprint(x, y, w, d, ang, tag="special"):
    """Register a special building footprint (M) so the terrace generator keeps clear of it."""
    o = _obb(x, y, w, d, ang)
    _occ_add(o, tag)
    return o

def _court_houses(rnd):
    """Boulder Court terraces facing in (eaves 13 / ridges 19 = 4 storeys) + the stepped-gable house on the north."""
    P = _pools()
    four = [i for i in P["plain"] + P["timber"] if HOUSE_VARIANTS[i][3] > 12.5 and HOUSE_VARIANTS[i][3] < 14 and HOUSE_VARIANTS[i][4] != "gable"]
    gables = [i for i in range(len(HOUSE_VARIANTS)) if HOUSE_VARIANTS[i][4] == "gable"]
    x0, x1, y0, y1 = 225.0, 318.0, 236.0, 292.0
    def run(ax, ay, bx, by, inward_ang, skip=None):
        L_ = math.hypot(bx - ax, by - ay)
        tx, ty = (bx - ax) / L_, (by - ay) / L_
        s_ = 0.0
        while s_ < L_ - 4:
            v = rnd.choice(four)
            name, w, d, Ht, roof, pool = HOUSE_VARIANTS[v]
            sx = min(1.15, max(0.85, (L_ - s_) / w)) if L_ - s_ < w * 1.3 else rnd.uniform(0.9, 1.1)
            ww = w * sx
            cx, cy = ax + tx * (s_ + ww / 2), ay + ty * (s_ + ww / 2)
            if skip and skip(cx, cy):
                s_ += 2.0; continue
            ly = (-math.sin(inward_ang), math.cos(inward_ang))        # local +y points away from the court
            cx += ly[0] * d / 2; cy += ly[1] * d / 2
            h = _place(cx, cy, inward_ang, v, sx, 1.0, force=True, tag="court")
            s_ += ww
    # south side (front faces north: local y points south => ang = pi); exit gap X 276..292 (16 m)
    run(x0 - 2, y0, x1 + 2, y0, math.pi, skip=lambda cx, cy: 270.0 < cx < 298.0)
    # north side (front faces south, ang 0); Mikasa's house (252, 300) and the stepped gable (270) are their own
    run(x0 + 14, y1, x1 + 2, y1, 0.0, skip=lambda cx, cy: 244.0 < cx < 277.0 or cx < 240.0)
    # east side (front faces west: local y points east => ang = -pi/2)
    run(x1, y0 + 2, x1, y1 - 2, -math.pi / 2)
    # west side (front faces east: ang = +pi/2), belfry at the NW corner
    run(x0, y0 + 2, x0, y1 - 12, math.pi / 2)
    if gables:
        v = gables[0]
        _place(270.5, y1 + HOUSE_VARIANTS[v][2] / 2, 0.0, v, 1.0, 1.0, force=True, tag="court_gable")

def _frontage(rnd):
    pools = _pools()
    order = {"av": 0, "ringroad": 1, "ring": 2, "radial": 3, "evs": 4, "lane": 4, "br": 4, "ss": 4, "q2st": 5, "lane2": 6,
             "quay": 6, "bridge": 7, "wallroad": 8, "ma": 9}
    sts = sorted(streets_m(), key=lambda s_: order.get(s_[2], 9))
    for pts, hw, kind in sts:
        if kind in ("ma",):
            continue
        if len(pts) < 3:
            continue
        cum = [0.0]
        for k in range(1, len(pts)):
            cum.append(cum[-1] + math.hypot(pts[k][0] - pts[k - 1][0], pts[k][1] - pts[k - 1][1]))
        total = cum[-1]
        import bisect
        def at(s_, cum=cum, pts=pts):
            k = max(1, min(len(cum) - 1, bisect.bisect_left(cum, s_)))
            a, b = pts[k - 1], pts[k]
            seg = max(1e-6, cum[k] - cum[k - 1]); f = (s_ - cum[k - 1]) / seg
            tx, ty = (b[0] - a[0]) / seg, (b[1] - a[1]) / seg
            return a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f, tx, ty
        for side in (1, -1):
            s_ = 0.0
            while s_ < total - 3:
                px, py, tx, ty = at(min(total, s_ + 4.5))
                if kind in ("av",) or math.hypot(px - C_XY[0], py - C_XY[1]) < 52:
                    pool = "arcade"
                else:
                    pool = "auto"
                v = _pick(pool, rnd, py)
                name, w, d, Ht, roof, pl = HOUSE_VARIANTS[v]
                sx = rnd.uniform(0.85, 1.2)
                ww = w * sx
                if s_ + ww > total:
                    break
                px, py, tx, ty = at(s_ + ww / 2)
                nx, ny = -ty * side, tx * side
                cx, cy = px + nx * (hw + 0.6 + d / 2), py + ny * (hw + 0.6 + d / 2)
                ang = math.atan2(-nx, ny) if True else 0.0
                # local -y must point to the street: local y = (nx, ny) -> local x = (ny, -nx)
                ang = math.atan2(-nx, ny)
                h = _place(cx, cy, ang, v, sx, 1.0)
                if h is None:
                    sx2 = 0.8
                    h = _place(cx, cy, ang, v, sx2, 1.0) if ww > 7.5 else None
                    s_ += (w * sx2) if h else 2.5
                else:
                    s_ += ww

def _back_rows(rnd, rounds=3):
    front = list(HOUSES)
    for r_ in range(rounds):
        new = []
        for h in front:
            if h.get("tag") in ("court", "court_gable"):
                continue
            ang = h["ang"]
            ly = (-math.sin(ang), math.cos(ang))
            v = _pick("auto", rnd, h["y"])
            name, w, d, Ht, roof, pl = HOUSE_VARIANTS[v]
            gap = rnd.choice((0.0, 0.0, 3.0, 5.0))
            off = h["d"] / 2 + gap + d / 2
            cx, cy = h["x"] + ly[0] * off, h["y"] + ly[1] * off
            nh = _place(cx, cy, ang, v, h["w"] / w, 1.0)
            if nh:
                new.append(nh)
        front = new

def _infill(rnd, n=26000):
    """Fill block interiors: orientation from the nearest placed house (keeps blocks coherent)."""
    for _ in range(n):
        X, Y = rnd.uniform(-470, 470), rnd.uniform(15, 865)
        if _mask_bad(X, Y):
            continue
        best, bd = None, 1e18
        gi, gj = int(X // 24), int(Y // 24)
        for i in (-1, 0, 1):
            for j in (-1, 0, 1):
                for q in _OCC.get((gi + i, gj + j), ()):
                    d = (q[0] - X) ** 2 + (q[1] - Y) ** 2
                    if d < bd:
                        bd, best = d, q
        ang = math.atan2(best[5], best[4]) if best else 0.0
        ang += rnd.choice((0.0, math.pi / 2, math.pi, -math.pi / 2)) if rnd.random() < 0.3 else 0.0
        v = _pick("auto", rnd, Y)
        _place(X, Y, ang, v, rnd.uniform(0.85, 1.15), rnd.uniform(0.8, 1.0))

def _instances(name, coll, recs):
    """GN instancer: recs = (x_set, y_set, z, rot_z, sx, sy, sz, variant)."""
    me = bpy.data.meshes.new(name + "_pts")
    me.vertices.add(len(recs))
    me.vertices.foreach_set("co", [c for r in recs for c in r[:3]])
    for an, typ in (("rot", "FLOAT_VECTOR"), ("scl", "FLOAT_VECTOR"), ("variant", "INT")):
        me.attributes.new(an, typ, "POINT")
    me.attributes["rot"].data.foreach_set("vector", [c for r in recs for c in (0.0, 0.0, r[3])])
    me.attributes["scl"].data.foreach_set("vector", [c for r in recs for c in r[4:7]])
    me.attributes["variant"].data.foreach_set("value", [r[7] for r in recs])
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    ng = bpy.data.node_groups.new(name + "_GN", "GeometryNodeTree")
    ng.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    N = ng.nodes; Lk = ng.links
    gi = N.new("NodeGroupInput"); go = N.new("NodeGroupOutput")
    def attr(n, t):
        a = N.new("GeometryNodeInputNamedAttribute"); a.data_type = t; a.inputs["Name"].default_value = n; return a
    ci = N.new("GeometryNodeCollectionInfo"); ci.transform_space = "ORIGINAL"
    ci.inputs["Collection"].default_value = coll
    ci.inputs["Separate Children"].default_value = True
    ci.inputs["Reset Children"].default_value = True
    iop = N.new("GeometryNodeInstanceOnPoints")
    Lk.new(gi.outputs["Geometry"], iop.inputs["Points"])
    Lk.new(ci.outputs[0], iop.inputs["Instance"])
    iop.inputs["Pick Instance"].default_value = True
    Lk.new(attr("variant", "INT").outputs["Attribute"], iop.inputs["Instance Index"])
    Lk.new(attr("rot", "FLOAT_VECTOR").outputs["Attribute"], iop.inputs["Rotation"])
    Lk.new(attr("scl", "FLOAT_VECTOR").outputs["Attribute"], iop.inputs["Scale"])
    Lk.new(iop.outputs["Instances"], go.inputs["Geometry"])
    mod = ob.modifiers.new("GN", "NODES"); mod.node_group = ng
    return ob

def check_route(verbose=True):
    """Collision check of the carry route BR: every house footprint must stay >= BALL_R + 0.5 m off the route
    centreline (2D); also prints the pilaster / trench clearances at R5b / R6."""
    worst = (1e9, None)
    pts = L.resample(BOULDER_ROUTE_M, 1.0)
    for h in HOUSES:
        o = h["obb"]
        cs = _obb_corners(o)
        for X, Y in pts:
            if abs(X - o[0]) > 30 or abs(Y - o[1]) > 30:
                continue
            # distance point -> OBB
            dx, dy = X - o[0], Y - o[1]
            lx = dx * o[4] + dy * o[5]; ly = -dx * o[5] + dy * o[4]
            ex = max(0.0, abs(lx) - o[2]); ey = max(0.0, abs(ly) - o[3])
            d = math.hypot(ex, ey)
            if d < worst[0]:
                worst = (d, (X, Y, h["x"], h["y"]))
    ok = worst[0] >= BALL_R + 0.5
    if verbose:
        print(f"[trost] route BR check: min house distance {worst[0]:.1f} m (need >= {BALL_R + 0.5}) -> {'OK' if ok else 'FAIL'} {worst[1]}", flush=True)
    return ok, worst

def layout_town():
    """The terrace layout (HOUSES, M coords) from HOUSE_VARIANTS dims: court terraces, street frontage, back rows, infill."""
    t0 = time.time()
    rnd = random.Random(91)
    HOUSES.clear(); _OCC.clear()
    _build_mask()
    for f in SPECIAL_FOOTPRINTS:
        block_footprint(*f)
    _court_houses(rnd)
    _frontage(rnd)
    _back_rows(rnd, 3)
    _infill(rnd)
    print(f"[trost] layout {len(HOUSES)} houses {time.time() - t0:.1f}s", flush=True)
    return HOUSES

def build_town(MT):
    """Continuous 3-5 storey terraces along every street (arcades on AV/C), back rows, infill; instanced by GN."""
    t0 = time.time()
    hc = _coll("TrostHouseVariants")
    _make_variants(MT, hc)
    layout_town()
    # drop any house that crept onto the carry lane (ball radius + 0.5)
    pts = L.resample(BOULDER_ROUTE_M[:4], 1.0)
    keep = []
    for h in HOUSES:
        o = h["obb"]; bad = False
        for X, Y in pts:
            dx, dy = X - o[0], Y - o[1]
            if abs(dx) > 30 or abs(dy) > 30:
                continue
            lx = dx * o[4] + dy * o[5]; ly = -dx * o[5] + dy * o[4]
            if math.hypot(max(0.0, abs(lx) - o[2]), max(0.0, abs(ly) - o[3])) < BALL_R + 0.5:
                bad = True; break
        if not bad:
            keep.append(h)
    HOUSES[:] = keep
    recs = [(h["x"], h["y"] + DY, h["z"], h["ang"], h["sx"], h["sy"], 1.0, h["v"]) for h in HOUSES]
    if HOUSES:
        pass
    _instances("TrostTown", hc, recs)
    print(f"[trost] town: {len(HOUSES)} terrace houses, {len(streets_m())} streets, {time.time() - t0:.1f}s", flush=True)
    check_route()
    return len(HOUSES)

SPECIAL_FOOTPRINTS = [(228.0, 290.0, 9.0, 9.0, 0.0, "belfry")]   # (x, y, w, d, ang, tag) of special builds (M)

def build_mikasa_house(MT):
    """Mikasa's house on the court's north side at (252, 300): body static, ROOF a separate object (caves in), plus the
    broken roof (10 x 8 m hole, broken rafters) hidden."""
    x, y, w, d = 252.0, 299.0, 11.0, 14.0
    Ht = 13.2; rise = 6.2
    bm = bmesh.new()
    box(bm, (x, y, (Ht - 3) / 2), (w, d, Ht + 3), mi=0)
    for k in range(3):
        for z in (5.0, 8.2, 11.4):
            box(bm, (x - 3.4 + k * 3.4, y - d / 2 - 0.04, z), (1.0, 0.1, 1.5), mi=1)
    _mk("TrostMikasaHouse", bm, [MT["f_cream"], MT["window_t"]])
    def roof_bm(broken):
        bm = bmesh.new()
        p = [bm.verts.new(c) for c in ((-w / 2, -d / 2 - 0.45, 0.0), (w / 2, -d / 2 - 0.45, 0.0), (w / 2, d / 2 + 0.45, 0.0),
                                        (-w / 2, d / 2 + 0.45, 0.0), (-w / 2, 0, rise), (w / 2, 0, rise))]
        if not broken:
            bm.faces.new((p[0], p[1], p[5], p[4])).material_index = 0
        else:
            rnd = random.Random(5)
            bm.faces.new((p[0], p[1], bm.verts.new((w / 2, -d / 2 + 2.0, rise * 0.62)), bm.verts.new((-w / 2, -d / 2 + 2.0, rise * 0.62)))).material_index = 0
            for k in range(6):                                  # broken rafters
                xx = -4.0 + k * 1.6
                tube(bm, [(xx, -d / 2 + 2.0, rise * 0.62), (xx + rnd.uniform(-0.5, 0.5), -d / 2 + 4.0 + rnd.uniform(0, 2), rise * 0.62 - rnd.uniform(0.5, 2.5))], 0.15, 0.12, 4, 2)
        bm.faces.new((p[3], p[4], p[5], p[2])).material_index = 0
        bm.faces.new((p[0], p[4], p[3])).material_index = 1
        bm.faces.new((p[1], p[2], p[5])).material_index = 1
        box(bm, (2.0, 2.0, rise - 0.5), (0.9, 0.9, 3.0), mi=3)
        return bm
    r1 = _mk_at("TrostMikasaRoof", roof_bm(False), [MT["roof_town"], MT["f_cream"], MT["timber_d"], MT["chimney"]], (x, y, Ht - 0.35))
    r2 = _mk_at("TrostMikasaRoofBroken", roof_bm(True), [MT["roof_town"], MT["f_cream"], MT["timber_d"], MT["chimney"]], (x, y, Ht - 0.35))
    _hide(r2)
    SPECIAL_FOOTPRINTS.append((x, y, w, d, 0.0, "mikasa"))
    return r1

# ====================================================================================== bell towers
def _tower_bm(bm, x, y, sd, H, cap_mi, body_mi, rnd, open_top=None):
    """Slender square bell tower: shaft, cornices, arched belfry stage, pyramid / hipped cap (no needle spires)."""
    shaft = H * 0.72
    belfry = H * 0.12
    box(bm, (x, y, (shaft - 2) / 2), (sd, sd, shaft + 2), mi=body_mi)
    for z in (shaft * 0.35, shaft * 0.7, shaft):
        box(bm, (x, y, z), (sd + 0.6, sd + 0.6, 0.6), mi=body_mi)
    z0 = shaft
    for sx in (-1, 1):
        for sy in (-1, 1):
            box(bm, (x + sx * (sd / 2 - 0.6), y + sy * (sd / 2 - 0.6), z0 + belfry / 2), (1.2, 1.2, belfry), mi=body_mi)
    box(bm, (x, y, z0 + 0.4), (sd - 1.4, sd - 1.4, 0.8), mi=body_mi)
    box(bm, (x, y, z0 + belfry * 0.5), (sd - 2.6, sd - 2.6, belfry), mi=6)            # dark inner (openings read dark)
    nop = 2 if sd >= 7.5 else 1
    for side in range(4):
        a = side * math.pi / 2
        c, s_ = math.cos(a), math.sin(a)
        for k in range(nop + 1):
            u = (k - nop / 2) * (sd / (nop + 0.0)) * 0.9
            px, py = x + c * (sd / 2 - 0.3) - s_ * u, y + s_ * (sd / 2 - 0.3) + c * u
            box(bm, (px, py, z0 + belfry / 2), (0.6 if abs(c) > 0.5 else 1.0, 1.0 if abs(c) > 0.5 else 0.6, belfry), mi=body_mi)
        px, py = x + c * (sd / 2 - 0.3), y + s_ * (sd / 2 - 0.3)
        box(bm, (px, py, z0 + belfry - 0.6), (0.6 if abs(c) > 0.5 else sd, sd if abs(c) > 0.5 else 0.6, 1.2), mi=body_mi)
    zt = z0 + belfry
    box(bm, (x, y, zt + 0.4), (sd + 0.8, sd + 0.8, 0.8), mi=body_mi)
    capH = H - zt - 0.8
    hip = rnd.random() < 0.3
    box(bm, (x, y, zt + 0.8 + capH / 2), (sd + 0.6, sd + 0.6, capH), mi=cap_mi, taper=(0.05 if not hip else 0.35, 0.05))
    cyl(bm, (x, y, H - 0.2), (x, y, H + 1.6), 0.12, seg=4, mi=3)

def build_towers(MT):
    """16-20 bell towers: T1-T8 (T4 removed), fillers; caps ~60 % red/copper, 40 % slate.  The court belfry, tower T,
    T_K and the RC tower are built by their blocks."""
    rnd = random.Random(101)
    bm = bmesh.new()
    caps = {"red": 0, "copper": 1, "slate": 2}
    for name, (x, y, sd, H, cap) in TOWERS_M.items():
        body = 4 if rnd.random() < 0.7 else 5
        _tower_bm(bm, x, y, sd, H, caps[cap], body, rnd)
    return _mk("TrostBellTowers", bm, TOWER_MATS(MT))

def TOWER_MATS(MT):
    return [MT["roof_red_t"], MT["roof_copper"], MT["roof_slate_t"], MT["iron_t"], MT["tower_cream"], MT["tower_brick"], MT["window_t"]]

def build_court_belfry(MT):
    rnd = random.Random(7)
    bm = bmesh.new()
    _tower_bm(bm, 228.0, 290.0, 8.0, 42.0, 0, 4, rnd)
    return _mk("TrostCourtBelfry", bm, TOWER_MATS(MT))

# ====================================================================================== lifts (timber truss + cage)
def build_lifts(MT):
    lc = _coll("TrostLifts")
    for spec in WALL_LIFTS:
        X, Y = to_m(*spec["xy"])[:2]
        ox, oy = spec["out"]
        if spec["name"] == "RoseHQ":                   # AUDIT 6: two tall brown posts + lintel + crossbar, near full height
            bm = bmesh.new()
            for sx in (-2.8, 2.8):
                box(bm, (sx, 6.0, 24.6), (0.7, 0.7, 49.2), mi=0)
            box(bm, (0.0, 6.0, 49.6), (7.4, 0.9, 0.9), mi=0)                      # lintel
            box(bm, (0.0, 6.0, 31.0), (5.6, 0.5, 0.5), mi=0)                      # crossbar
            for sx in (-2.8, 2.8):
                box(bm, (sx, 3.2, 49.6), (0.5, 5.6, 0.5), mi=0)                   # ties back into the wall face
            for sx in (-0.8, 0.8):
                cyl(bm, (sx, 6.0, 49.2), (sx, 6.0, 2.0), 0.05, seg=4, mi=3)      # ropes
            ob = L.obj_from_bm(f"TrostLift_{spec['name']}", bm, [MT["timber_d"], MT["f_tcream"], MT["roof_red_t"], MT["iron_t"]], lc)
            ob.location = M(X, Y, 0.0); ob.rotation_euler.z = math.atan2(oy, ox) - math.pi / 2
            pb = bmesh.new()
            box(pb, (0, 0, 0.18), (4.3, 3.6, 0.36), mi=0)
            for sx in (-2.0, 2.0):
                box(pb, (sx, 0, 0.75), (0.15, 3.6, 0.15), mi=1)
            po = L.obj_from_bm(spec["platform"], pb, [MT["plank_t"], MT["iron_t"]], lc)
            po.parent = ob; po.location = (0, 6.0, 0.4)
            continue
        bm = bmesh.new()
        y0, y1 = 5.4, 10.4
        for sx in (-2.4, 2.4):
            for yy in (y0, y1):
                box(bm, (sx, yy, 26.0), (0.45, 0.45, 52.0), mi=0)
        for z in range(4, 51, 6):
            box(bm, (0, y0, z), (5.2, 0.3, 0.3), mi=0); box(bm, (0, y1, z), (5.2, 0.3, 0.3), mi=0)
            for sx in (-2.4, 2.4):
                box(bm, (sx, (y0 + y1) / 2, z), (0.3, y1 - y0, 0.3), mi=0)
            if z + 6 <= 50:
                cyl(bm, (-2.4, y1, z), (2.4, y1, z + 6), 0.12, seg=4, mi=0)
        box(bm, (0, (2 + y1) / 2 + 0.5, 55.2), (0.6, y1 - 1, 0.6), mi=0)
        box(bm, (0, 1.6, 52.2), (6.0, 5.5, 4.4), mi=1)
        p = [bm.verts.new(c) for c in ((-3.3, -1.4, 54.4), (3.3, -1.4, 54.4), (3.3, 4.6, 54.4), (-3.3, 4.6, 54.4), (-3.3, 1.6, 56.8), (3.3, 1.6, 56.8))]
        for fv in ((p[0], p[1], p[5], p[4]), (p[3], p[4], p[5], p[2]), (p[0], p[4], p[3]), (p[1], p[2], p[5])):
            bm.faces.new(fv).material_index = 2
        cyl(bm, (3.5, 0.0, 50.0), (3.5, 6.0, 60.0), 0.25, seg=5, mi=0)       # derrick + counterweight
        box(bm, (3.5, -1.0, 52.0), (1.4, 1.4, 1.4), mi=3)
        for sx in (-0.8, 0.8):
            cyl(bm, (sx, (y0 + y1) / 2, 55.0), (sx, (y0 + y1) / 2, 2.0), 0.05, seg=4, mi=3)
        ob = L.obj_from_bm(f"TrostLift_{spec['name']}", bm, [MT["timber_d"], MT["f_tcream"], MT["roof_red_t"], MT["iron_t"]], lc)
        rot = math.atan2(oy, ox) - math.pi / 2
        ob.location = M(X, Y, 0.0); ob.rotation_euler.z = rot
        pb = bmesh.new()
        box(pb, (0, 0, 0.18), (4.3, 4.3, 0.36), mi=0)
        for sx in (-2.0, 2.0):
            box(pb, (sx, 0, 0.75), (0.15, 4.3, 0.15), mi=1); box(pb, (0, sx, 0.75), (4.3, 0.15, 0.15), mi=1)
        for sx in (-2.0, 2.0):
            for sy in (-2.0, 2.0):
                box(pb, (sx, sy, 1.2), (0.12, 0.12, 2.0), mi=1)
        box(pb, (0, 0, 2.3), (4.3, 4.3, 0.15), mi=1)
        po = L.obj_from_bm(spec["platform"], pb, [MT["plank_t"], MT["iron_t"]], lc)
        po.parent = ob; po.location = (0, (y0 + y1) / 2, 0.4)
    return lc

# ====================================================================================== state hooks
def set_breach(on=True):
    """After the kick: intact gatehouse/doors -> breached gatehouse + rubble fan + beams + craters (caps hidden);
    the glow card comes on with the breach (set_glow fades it)."""
    for n in ("OuterGate", "OuterGate_Door", "OuterGate_Iron"):
        _hide(bpy.data.objects.get(n), on)
    for n in ("OuterGateBroken", "OuterGateRubble", "TrostBreachTimbers"):
        _hide(bpy.data.objects.get(n), not on)
    for i in range(len(CRATERS_M) + len(HOLES_M)):
        _hide(bpy.data.objects.get(f"GS_Crater{i}"), not on)
        _hide(bpy.data.objects.get(f"GS_CraterCap{i}"), on)
    set_glow(1.0 if on else 0.0)

def set_glow(v):
    """Orange glow in the breach, v in [0, 1] (0 hides the card)."""
    o = bpy.data.objects.get("OuterGate_Glow")
    if not o:
        return
    _hide(o, v <= 0.001)
    m = o.data.materials[0] if o.data.materials else None
    if m and m.use_nodes and "Glow" in m.node_tree.nodes:
        m.node_tree.nodes["Glow"].inputs["Strength"].default_value = 3.0 * max(0.0, min(1.0, v))

def set_plug(frac):
    """Λ tendril plug: 0 hidden, 1 full height (Z 38)."""
    o = bpy.data.objects.get("OuterGate_Plug")
    if o:
        _hide(o, frac <= 0.001)
        o.scale = (1.0, 1.0, max(0.001, min(1.0, frac)))

def set_seal(on=True, plug=1.0):
    """Sealed state: glow off, crushed-brick ring at the ball rest, plug grown to `plug`."""
    _hide(bpy.data.objects.get("OuterGate_SealRubble"), not on)
    _hide(bpy.data.objects.get("TrostBallContactSeal"), not on)
    if on:
        set_glow(0.0)
    set_plug(plug if on else 0.0)

def set_mikasa_roof(broken=False):
    _hide(bpy.data.objects.get("TrostMikasaRoof"), broken)
    _hide(bpy.data.objects.get("TrostMikasaRoofBroken"), not broken)

def set_lift(i, frac):
    po = bpy.data.objects.get(WALL_LIFTS[i]["platform"])
    if po:
        po.location.z = 0.4 + max(0.0, min(1.0, frac)) * (WALL_H - 0.6)

def set_wagon(on=True):
    """Cart visibility (old name; block 6 builds TrostCart)."""
    for n in ("TrostCart",):
        o = bpy.data.objects.get(n)
        if o:
            for c in [o] + list(o.children_recursive):
                _hide(c, not on)

def _install_cut(ob):
    """Give the bay its own material copies ending in Mix(Transparent, <surface>) driven by a 'CutAlpha' value node,
    Dithered render method.  Installed lazily (after toon.apply has converted the copies)."""
    if ob.get("cut_installed"):
        return
    for slot in ob.material_slots:
        m = slot.material
        if not m or not m.use_nodes:
            continue
        if not m.name.startswith("Cut_"):
            m = m.copy(); m.name = "Cut_" + slot.material.name
            slot.material = m
        nt = m.node_tree; N = nt.nodes
        if "CutAlpha" in N:
            continue
        out = next((n for n in N if n.type == "OUTPUT_MATERIAL" and n.is_active_output), None)
        if out is None or not out.inputs["Surface"].is_linked:
            continue
        src = out.inputs["Surface"].links[0].from_socket
        v = N.new("ShaderNodeValue"); v.name = "CutAlpha"; v.outputs[0].default_value = 1.0
        tr = N.new("ShaderNodeBsdfTransparent"); mx = N.new("ShaderNodeMixShader")
        nt.links.new(v.outputs[0], mx.inputs[0]); nt.links.new(tr.outputs[0], mx.inputs[1]); nt.links.new(src, mx.inputs[2])
        nt.links.new(mx.outputs[0], out.inputs["Surface"])
        try:
            m.surface_render_method = "DITHERED"
        except Exception:
            pass
    ob["cut_installed"] = 1

def set_hq_cutaway(frac=True):
    """HQ storeroom cutaway (block 7): True/False or 0..1 = dithered dissolve of the 36 m bay (TrostHQ_Bay) only;
    the shadow-only proxy TrostHQ_BayShadow keeps the sun out of the storeroom."""
    f = 1.0 if frac is True else 0.0 if frac is False else max(0.0, min(1.0, float(frac)))
    for n in HQ_UPPER:
        o = bpy.data.objects.get(n)
        if not o:
            continue
        _hide(o, f >= 0.999)
        if 0.0 < f < 0.999:
            _install_cut(o)
        for slot in o.material_slots:
            m_ = slot.material
            if m_ and m_.use_nodes and "CutAlpha" in m_.node_tree.nodes:
                m_.node_tree.nodes["CutAlpha"].outputs[0].default_value = 1.0 - f

def set_hq_lift(frac):
    o = bpy.data.objects.get("TrostHQ_Cage")
    if o:
        lo, hi = SUPPLY_HQ["lift_z"]
        o.location.z = hi + (lo - hi) * max(0.0, min(1.0, frac))

# ---------------------------------------------------------------- compat stubs used by other scripts
def build_church(MT):
    """Removed (bible: no white needle church). Kept as a no-op for render_interlude.py."""
    return None

def town_points(n_variants, widths):
    """Compat for render_interlude.py: the terrace layout mapped onto the caller's variants (set coords)."""
    if not HOUSES:
        if not HOUSE_VARIANTS:
            _make_variants(None, None, meshes=False)
        layout_town()
    pts = []
    for h in HOUSES:
        v = min(range(n_variants), key=lambda i: abs(widths[i][0] - h["w"]) + abs(widths[i][1] - h["d"]))
        pts.append((h["x"], h["y"] + DY, 0.0, h["ang"], 1.0, v, -10000.0, 99999.0))
    return pts, []

# ====================================================================================== world / light
def _world(sc):
    w = bpy.data.worlds.new("Sky"); sc.world = w; w.use_nodes = True
    nt = w.node_tree; sky = nt.nodes.new("ShaderNodeTexSky")
    types = sky.bl_rna.properties["sky_type"].enum_items.keys()
    sky.sky_type = "MULTIPLE_SCATTERING" if "MULTIPLE_SCATTERING" in types else "NISHITA"
    sky.sun_elevation = math.radians(40); sky.sun_rotation = math.radians(115); sky.air_density = 1.4
    if hasattr(sky, "sun_disc"): sky.sun_disc = False
    if hasattr(sky, "dust_density"): sky.dust_density = 2.5
    if hasattr(sky, "aerosol_density"): sky.aerosol_density = 1.5
    nt.links.new(sky.outputs[0], nt.nodes["Background"].inputs[0])
    tcw = nt.nodes.new("ShaderNodeTexCoord"); sz = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tcw.outputs["Generated"], sz.inputs[0])
    gr = nt.nodes.new("ShaderNodeValToRGB"); ge = gr.color_ramp.elements
    ge[0].position, ge[0].color = 0.0, (0.70, 0.80, 0.90, 1)
    ge[1].position, ge[1].color = 0.40, (0.18, 0.38, 0.78, 1)
    nt.links.new(sz.outputs["Z"], gr.inputs[0])
    bg2 = nt.nodes.new("ShaderNodeBackground"); bg2.inputs[1].default_value = float(os.environ.get("SKYB", "4.0"))
    nt.links.new(gr.outputs[0], bg2.inputs[0])
    lp = nt.nodes.new("ShaderNodeLightPath"); mx = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(lp.outputs["Is Camera Ray"], mx.inputs[0])
    nt.links.new(nt.nodes["Background"].outputs[0], mx.inputs[1]); nt.links.new(bg2.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], nt.nodes["World Output"].inputs[0])
    nt.nodes["Background"].inputs[1].default_value = 0.25
    sun = bpy.data.lights.new("Sun", "SUN"); sun.energy = float(os.environ.get("SUN_E", "3.6")); sun.angle = math.radians(1.5)
    so = bpy.data.objects.new("Sun", sun); sc.collection.objects.link(so)
    set_sun(float(os.environ.get("SUN_AZ", "-45")), float(os.environ.get("SUN_EL", "45")))
    return w, so

def set_sun(az_deg, el_deg):
    """Sun direction: az = math angle (deg) of the sun's position in xy (0 = east, 90 = north, -45 = SE)."""
    so = bpy.data.objects.get("Sun")
    if not so:
        return
    el, az = math.radians(el_deg), math.radians(az_deg)
    d = Vector((-math.cos(el) * math.cos(az), -math.cos(el) * math.sin(az), -math.sin(el)))
    so.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()

# ====================================================================================== build
EXTRA_BUILDERS = []          # block 6-9 builders appended below: (name, fn)

def build_set(MT, year=850):
    """Called by scene.build() (hook) with scene.py's material dict. Builds the whole Trost scene once."""
    t0 = time.time()
    _install()
    sc = bpy.context.scene
    _materials(MT)
    T = {}
    def step(name, fn, *a):
        t = time.time()
        try:
            r = fn(*a)
        except Exception as ex:
            import traceback; traceback.print_exc()
            print(f"[trost] {name} FAILED: {ex!r}", flush=True)
            r = None
        T[name] = time.time() - t
        return r
    terrain = step("terrain", build_terrain_trost, MT)
    step("walls", build_walls, MT)
    step("walltop", build_walltop, MT)
    step("outer_gate", build_outer_gate, MT)
    step("gate_square", build_gate_square, MT)
    step("canal", build_canal, MT)
    step("court", build_boulder_court, MT)
    step("mikasa", build_mikasa_house, MT)
    step("belfry", build_court_belfry, MT)
    step("strip", build_strip, MT)
    step("lifts", build_lifts, MT)
    step("towers", build_towers, MT)
    for name, fn in EXTRA_BUILDERS:
        step(name, fn, MT)
    step("town", build_town, MT)
    for name, fn in globals().get("POST_TOWN_BUILDERS", []):
        step(name, fn, MT)
    w, so = _world(sc)
    try:
        L.LABEL_ANCHORS.clear(); L.LABEL_ANCHORS.update(LABELS)
    except Exception:
        pass
    print("[trost] set built in %.1f s: %s" % (time.time() - t0, ", ".join(f"{k} {v:.1f}" for k, v in T.items())), flush=True)
    ctx = {"terrain": terrain, "height": L.height, "year": year, "sun": so, "world": w, "set": SET_NAME}
    for p in L.PLUGINS:
        if p is sys.modules.get(__name__) or getattr(p, "SET_NAME", None) == SET_NAME:
            continue
        if hasattr(p, "build"):
            try:
                p.build(MT, year, ctx)
            except Exception as ex:
                import traceback; traceback.print_exc()
                print(f"[plugin {p.__name__}] build failed: {ex!r}")
    return MT

# ====================================================================================== block 6: inner gate side (g5)
CART_STATES = {"start": ((-140.0, 851.5, 0.0), 0.0), "end": ((-122.0, 842.0, 0.0), 320.0)}   # load centre M, compass yaw

def _arch_ring(bm, cx, cy_face, w, spring, depth_y, mi, nseg=9, thick=0.9, face_sign=-1):
    """Grey voussoir ring around a round arch on a south (face_sign=-1) or north face."""
    r = w / 2
    for k in range(nseg):
        a0 = math.pi * k / nseg; a1 = math.pi * (k + 1) / nseg
        am = (a0 + a1) / 2
        x = cx + math.cos(am) * (r + thick / 2); z = spring + math.sin(am) * (r + thick / 2)
        box(bm, (x, cy_face + face_sign * 0.15, z), (r * math.pi / nseg + 0.1, depth_y, thick), rot=0.0, mi=mi)

def _arch_cut_block(bm, x0, x1, y0, y1, z1, ax, aw, spring, mi):
    """Solid block X x0..x1, Y y0..y1, Z 0..z1 with a round-arched tunnel (centre X ax, width aw) along Y."""
    r = aw / 2
    box(bm, ((x0 + ax - r) / 2, (y0 + y1) / 2, z1 / 2), (ax - r - x0, y1 - y0, z1), mi=mi)
    box(bm, ((ax + r + x1) / 2, (y0 + y1) / 2, z1 / 2), (x1 - ax - r, y1 - y0, z1), mi=mi)
    top = spring + r
    box(bm, (ax, (y0 + y1) / 2, (top + z1) / 2), (aw, y1 - y0, z1 - top), mi=mi)
    n = 6
    for k in range(n):                                   # stepped haunches between spring and crown
        z0 = spring + r * math.sin(math.pi / 2 * k / n); z1_ = spring + r * math.sin(math.pi / 2 * (k + 1) / n)
        hw_ = r * math.cos(math.pi / 2 * (k + 0.5) / n)
        for sx in (-1, 1):
            xa = ax + sx * hw_; xb = ax + sx * r
            box(bm, ((xa + xb) / 2, (y0 + y1) / 2, (z0 + top) / 2), (abs(xb - xa) + 0.02, y1 - y0, top - z0), mi=mi)

def build_inner_gate(MT):
    """I: the 38 m brick bastion (central block with the OPEN 5.0 x 6.5 m arch and a dark 22 m tunnel, crest relief,
    west-wing door, east-wing door, cornices), the wall gate block, giant pale pilasters both sides, the east grass
    slope with trees, terrace + retaining edge, the ledge with steps, the west tree, E's bounding buildings (corner
    turret, pyramid-tower building)."""
    rnd = random.Random(111)
    ic = _coll("TrostInnerGate")
    brick = MT.setdefault("ig_brick", brick_mat("TrostInnerBrick", "#7a4a3a", "#5e4a3e", scale=3.2))
    quoin = MT.setdefault("ig_quoin", stone_mat("TrostQuoin", "#8d8a82", block=(1.2, 0.6)))
    crest = MT.setdefault("ig_crest", flat_mat("TrostCrestRelief", "#a9a291", 0.85, 0.06))
    tun = MT.setdefault("ig_tunnel", flat_mat("TrostTunnelDark", "#0d0c0c", 0.95, 0.0))
    mats = [MT["wall_t"], brick, quoin, crest, tun, MT["timber_d"], MT["window_t"]]
    bm = bmesh.new()
    # wall gate block (Rose body X -147..-133, Y 865..875) with the tunnel
    _arch_cut_block(bm, -147.2, -132.8, 864.9, 875.1, 51.2, -140.0, 5.0, 4.0, 0)
    # central block X -147..-133, Y 851..865, to Z 38
    _arch_cut_block(bm, -147.0, -133.0, 851.0, 865.0, 38.0, -140.0, 5.0, 4.0, 1)
    # tunnel lining (dark), far end shut by a dark curtain (no green field visible through it)
    for sx in (-1, 1):
        box(bm, (-140.0 + sx * 2.45, 862.0, 2.0), (0.1, 21.5, 4.0), mi=4)
    box(bm, (-140.0, 862.0, 6.55), (5.0, 21.5, 0.1), mi=4)
    for k in range(6):
        a = math.pi * (k + 0.5) / 6
        box(bm, (-140.0 + math.cos(a) * 2.4, 862.0, 4.0 + math.sin(a) * 2.4), (0.9, 21.5, 0.9), rot=0.0, mi=4)
    box(bm, (-140.0, 872.5, 3.3), (5.2, 0.2, 6.6), mi=4)
    box(bm, (-140.0, 862.0, 0.02), (5.0, 21.5, 0.04), mi=4)
    _arch_ring(bm, -140.0, 851.0, 5.0, 4.0, 0.5, 2)
    for sx in (-1, 1):                                       # grey jambs
        box(bm, (-140.0 + sx * 2.95, 850.8, 2.0), (0.9, 0.5, 4.0), mi=2)
    for z in (26.0, 38.0):
        box(bm, (-140.0, 850.6, z), (14.6, 1.0, 1.0), mi=2)
    for sx in (-1, 1):                                       # quoins on the central block's corners
        for k in range(16):
            box(bm, (-140.0 + sx * 6.85, 851.2, 1.0 + k * 2.3), (1.4 if k % 2 else 0.9, 0.5, 1.0), mi=2)
    # crest relief: shield 2.5 x 3 m at Z 20-23 on a pale tablet
    box(bm, (-140.0, 850.75, 21.5), (3.4, 0.3, 4.0), mi=3)
    hexa(bm, [(-141.25, 850.4, 19.6), (-138.75, 850.4, 19.6), (-138.75, 850.65, 19.6), (-141.25, 850.65, 19.6),
              (-141.45, 850.4, 23.1), (-138.55, 850.4, 23.1), (-138.55, 850.65, 23.1), (-141.45, 850.65, 23.1)], 2)
    cyl(bm, (-140.0, 850.45, 21.6), (-140.0, 850.25, 21.6), 0.75, seg=10, mi=3)
    for k in range(3):                                       # slit windows
        box(bm, (-140.0, 850.95, 11.0 + k * 4.5), (0.6, 0.12, 2.2), mi=6)
    # west wing X -153..-147 (to Z 32, cornice 14), narrow arched door 1.5 x 3.5, slit window
    box(bm, (-150.0, 859.0, 16.0), (6.0, 12.0, 32.0), mi=1)
    for z in (14.0, 32.0):
        box(bm, (-150.0, 852.6, z), (6.4, 0.9, 0.9), mi=2)
    box(bm, (-150.0, 852.95, 1.4), (1.5, 0.12, 2.8), mi=5); cyl(bm, (-150.0, 852.9, 2.8), (-150.0, 853.0, 2.8), 0.75, seg=8, mi=5)
    box(bm, (-150.0, 852.95, 9.0), (0.5, 0.12, 2.0), mi=6)
    # east wing X -133..-115 (to Z 34, cornices 18 / 30), door 3.5 x 5.5 at X -124, small square windows
    box(bm, (-124.0, 859.0, 17.0), (18.0, 12.0, 34.0), mi=1)
    for z in (18.0, 30.0, 34.0):
        box(bm, (-124.0, 852.6, z), (18.4, 0.9, 0.9), mi=2)
    box(bm, (-124.0, 852.95, 1.9), (3.5, 0.15, 3.8), mi=5)
    cyl(bm, (-124.0, 852.9, 3.75), (-124.0, 853.0, 3.75), 1.75, seg=12, mi=5)
    _arch_ring(bm, -124.0, 853.0, 3.5, 3.75, 0.4, 2, 7, 0.7)
    for row, z in enumerate((9.0, 13.0, 22.0, 26.0)):
        for x in (-130.0, -127.0, -121.0, -118.0):
            box(bm, (x, 852.95, z), (1.0, 0.12, 1.1), mi=6)
    for sx, x in ((-1, -158.0), (1, -110.0)):                 # giant pale Rose pilasters, flaring at the foot
        box(bm, (x, 860.0, 26.0), (10.0, 10.0, 52.0), mi=0)
        prev = None
        for z, d in ((0.0, 16.0), (4.0, 13.0), (9.0, 11.2), (14.0, 10.0)):
            if prev:
                z0, d0 = prev
                hexa(bm, [(x - 5, 865.0 - d0, z0), (x + 5, 865.0 - d0, z0), (x + 5, 865.0, z0), (x - 5, 865.0, z0),
                          (x - 5, 865.0 - d, z), (x + 5, 865.0 - d, z), (x + 5, 865.0, z), (x - 5, 865.0, z)], 0)
            prev = (z, d)
        box(bm, (x, 862.0, 52.8), (10.8, 8.0, 1.6), mi=0)
    ob = _mk("InnerGate", bm, mats, ic)
    # ledge X -133..-105, Y 849..853 (1.2 m) with steps; terrace retaining edges; grass slope trees + shrubs; west tree
    bm = bmesh.new()
    box(bm, (-119.0, 851.0, 0.6), (28.0, 4.0, 1.2), mi=0)
    for k in range(3):
        box(bm, (-119.0, 848.6 - k * 0.45, 0.2 + k * 0.0), (28.0, 0.45 + k * 0.0, 0.4 * (3 - k)), mi=0)
    box(bm, (-82.5, 820.0, 0.5), (45.0, 0.6, 1.2), mi=0)      # terrace retaining edge (Y 820)
    box(bm, (-82.5, 840.0, 1.25), (45.0, 0.5, 0.6), mi=0)
    box(bm, (-105.2, 842.0, 1.8), (0.6, 46.0, 1.4), mi=0)
    for k, (x, y, h) in enumerate(((-96.0, 853.0, 12.0), (-84.0, 858.0, 13.5), (-72.0, 852.0, 11.0), (-64.0, 860.0, 10.5))):
        z0 = ground_z_m(x, y)
        cyl(bm, (x, y, z0), (x, y, z0 + h * 0.4), 0.45, seg=6, mi=1)
        for j in range(5):
            rock_blob(bm, (x + rnd.uniform(-2, 2), y + rnd.uniform(-2, 2), z0 + h * 0.62 + rnd.uniform(-1, 1.5)), (3.4, 3.4, 3.0), rnd, 2, 2, 1.0, 0.2)
    for k in range(9):
        x, y = rnd.uniform(-102, -62), rnd.uniform(843, 862)
        rock_blob(bm, (x, y, ground_z_m(x, y) + 0.8), (1.2, 1.2, 1.0), rnd, 1, 3, 1.0, 0.25)
    x, y = -172.0, 858.0
    cyl(bm, (x, y, 0), (x, y, 5.0), 0.45, seg=6, mi=1)
    for j in range(5):
        rock_blob(bm, (x + rnd.uniform(-2, 2), y + rnd.uniform(-1.5, 1.5), 8.0 + rnd.uniform(-1, 2)), (3.2, 3.0, 3.0), rnd, 2, 2, 1.0, 0.2)
    _mk("InnerGateYard", bm, [MT["cornice"], MT["bark_t"], MT["tree_dark"], MT["shrub"]], ic)
    # E's bounding buildings: south block with the corner turret (-140, 790), west block, pyramid-tower building (-95, 815)
    bm = bmesh.new()
    fac = MT["f_cream"]
    def bldg(x0, x1, y0, y1, H, ridge_axis="x", mi_w=0, mi_r=1):
        box(bm, ((x0 + x1) / 2, (y0 + y1) / 2, (H - 3) / 2), (x1 - x0, y1 - y0, H + 3), mi=mi_w)
        if ridge_axis == "x":
            d = y1 - y0; rise = d * 0.55
            p = [bm.verts.new(c) for c in ((x0, y0 - 0.4, H), (x1, y0 - 0.4, H), (x1, y1 + 0.4, H), (x0, y1 + 0.4, H), (x0, (y0 + y1) / 2, H + rise), (x1, (y0 + y1) / 2, H + rise))]
            for fv, mi in (((p[0], p[1], p[5], p[4]), mi_r), ((p[3], p[4], p[5], p[2]), mi_r), ((p[0], p[4], p[3]), mi_w), ((p[1], p[2], p[5]), mi_w)):
                bm.faces.new(fv).material_index = mi
        else:
            d = x1 - x0; rise = d * 0.55
            p = [bm.verts.new(c) for c in ((x0 - 0.4, y0, H), (x1 + 0.4, y0, H), (x1 + 0.4, y1, H), (x0 - 0.4, y1, H), ((x0 + x1) / 2, y0, H + rise), ((x0 + x1) / 2, y1, H + rise))]
            for fv, mi in (((p[0], p[4], p[5], p[3]), mi_r), ((p[1], p[2], p[5], p[4]), mi_r), ((p[0], p[1], p[4]), mi_w), ((p[2], p[3], p[5]), mi_w)):
                bm.faces.new(fv).material_index = mi
    bldg(-143.0, -108.0, 786.0, 799.0, 13.2, "x")
    bldg(-143.0, -108.0, 773.0, 786.0, 10.0, "x")
    bldg(-199.0, -180.0, 800.0, 852.0, 13.2, "y")
    bldg(-104.0, -82.0, 805.0, 819.0, 13.2, "x", 2, 1)
    cyl(bm, (-140.0, 791.0, 0.0), (-140.0, 791.0, 17.0), 3.0, seg=12, mi=0)          # corner turret, conical roof
    cyl(bm, (-140.0, 791.0, 17.0), (-140.0, 791.0, 24.0), 3.4, 0.1, seg=12, mi=3)
    box(bm, (-95.0, 815.0, 13.0), (7.0, 7.0, 28.0), mi=2)                             # pyramid-roofed tower
    box(bm, (-95.0, 815.0, 30.5), (7.6, 7.6, 7.0), mi=3, taper=(0.05, 0.05))
    for k in range(5):                                                                 # stepped gable on the tower building
        box(bm, (-104.0 + 0.3, 812.0, 13.2 + k * 1.3), (0.6, 14.0 - k * 2.8, 1.3), mi=2)
    _mk("InnerGateBuildings", bm, [fac, MT["roof_town"], MT["tower_cream"], MT["roof_slate_t"]], ic)
    for f in ((-125.5, 786.0, 35.0, 26.0, 0.0), (-189.5, 826.0, 19.0, 52.0, 0.0), (-93.0, 812.0, 22.0, 14.0, 0.0), (-140.0, 791.0, 7.0, 7.0, 0.0)):
        SPECIAL_FOOTPRINTS.append((*f, "E"))
    build_cart(MT)
    return ob

def build_cart(MT):
    """The sack cart: parent empty TrostCart at the LOAD CENTRE (ground level), local +Y = forward (horses).
    Flatbed 5.4 x 4.0 m at 1.1 m, 4 spoked wheels (1.6 m, track 4.8 m), shafts, 2 dark horses, 12 burlap sacks in a
    rope lattice (5.0 L x 5.3 W x 2.8 H).  Start: wedged in the arch, horses in the tunnel; end: (-122, 842) yaw 320."""
    rnd = random.Random(121)
    cc = _coll("TrostCart")
    sack = MT.setdefault("sack", flat_mat("TrostSack", "#b4ae9f", 0.95, 0.12, 2.0))
    rope = MT.setdefault("rope", flat_mat("TrostRope", "#5b4a36", 0.9, 0.05))
    horse = MT.setdefault("horse", flat_mat("TrostHorse", "#3a2a22", 0.8, 0.08))
    harness = MT.setdefault("harness", flat_mat("TrostHarness", "#2a2018", 0.8, 0.0))
    bedm = MT.setdefault("cart_bed", plank_mat("TrostCartBed", "#5a4532", vertical=False))
    root = bpy.data.objects.new("TrostCart", None); cc.objects.link(root)
    root.empty_display_size = 3.0
    # body: bed, tailboard ladder, wheels, shafts
    bm = bmesh.new()
    box(bm, (0, 0, 1.0), (4.0, 5.4, 0.25), mi=0)
    for sx in (-1.9, 1.9):
        box(bm, (sx, 0, 1.2), (0.15, 5.4, 0.3), mi=0)
    box(bm, (0, -2.75, 1.2), (4.0, 0.15, 0.5), mi=0)
    for k in range(3):
        box(bm, (0, -2.95 - k * 0.15, 0.85 - k * 0.3), (1.2, 0.25, 0.08), mi=0)
    for sx in (-2.25, 2.25):
        for sy in (-1.8, 1.8):
            cyl(bm, (sx - 0.08, sy, 0.8), (sx + 0.08, sy, 0.8), 0.8, seg=16, mi=1)
            for k in range(6):
                a = k * math.pi / 6
                box(bm, (sx + 0.1 * (1 if sx > 0 else -1), sy, 0.8), (0.06, 1.5 * abs(math.cos(a)) + 0.06, 1.5 * abs(math.sin(a)) + 0.06), mi=0)
        box(bm, (sx * 0.9, 0, 0.8), (0.12, 3.8, 0.12), mi=1)
    for sx in (-0.95, 0.95):
        cyl(bm, (sx, 2.7, 1.0), (sx * 0.9, 6.0, 1.15), 0.08, seg=5, mi=0)
    body = _mk_at("TrostCart_Body", bm, [bedm, MT["iron_t"]], (0, 0, 0), cc)
    body.parent = root; body.location = (0, 0, 0)
    # load: 12 sacks (3 across x 2 high x 2 long), bulging to 5.3 m wide, rope lattice
    bm = bmesh.new()
    for ix in range(3):
        for iz in range(2):
            for iy in range(2):
                x = (ix - 1) * 1.72; y = (iy - 0.5) * 2.45; z = 1.75 + iz * 1.25
                rock_blob(bm, (x, y, z), (0.92, 1.28, 0.72), rnd, 2, 0, 1.0, 0.06)
    for k in range(5):
        x = -2.4 + k * 1.2
        tube(bm, [(x, -2.5, 1.2), (x * 1.05, -2.6, 3.2), (x * 0.6, 0.0, 4.0), (x * 1.05, 2.6, 3.2), (x, 2.5, 1.2)], 0.05, 0.05, 3, 1)
    for k in range(4):
        y = -1.9 + k * 1.27
        tube(bm, [(-2.65, y, 1.3), (-2.4, y, 3.4), (0, y, 4.0), (2.4, y, 3.4), (2.65, y, 1.3)], 0.05, 0.05, 3, 1)
    load = _mk_at("TrostCart_Load", bm, [sack, rope], (0, 0, 0), cc)
    load.parent = root; load.location = (0, 0, 0)
    # two dark draught horses side by side (each ~2.4 m long, 1.6 m at the withers), heads ~7.8 m ahead
    bm = bmesh.new()
    for sx in (-0.55, 0.55):
        rock_blob(bm, (sx, 5.4, 1.25), (0.42, 1.15, 0.45), rnd, 2, 0, 1.0, 0.03)
        cyl(bm, (sx, 6.35, 1.45), (sx, 7.35, 2.05), 0.22, 0.16, seg=6, mi=0)
        rock_blob(bm, (sx, 7.65, 1.95), (0.17, 0.42, 0.2), rnd, 1, 0, 1.0, 0.0)
        for lx, ly in ((-0.22, 4.6), (0.22, 4.6), (-0.22, 6.2), (0.22, 6.2)):
            cyl(bm, (sx + lx, ly, 0.0), (sx + lx, ly, 1.0), 0.09, seg=4, mi=0)
        box(bm, (sx, 6.1, 1.5), (0.95, 0.22, 0.5), mi=1)
    horses = _mk_at("TrostCart_Horses", bm, [horse, harness], (0, 0, 0), cc)
    horses.parent = root; horses.location = (0, 0, 0)
    set_cart("start")
    _hide_cart(True)
    return root

def _hide_cart(hidden):
    o = bpy.data.objects.get("TrostCart")
    if o:
        for c in [o] + list(o.children_recursive):
            _hide(c, hidden)

def set_cart(state="start", frac=None):
    """Pose the cart: state "start" / "end", or frac 0..1 between them (straight back-out then swing)."""
    root = bpy.data.objects.get("TrostCart")
    if not root:
        return
    (p0, y0), (p1, y1) = CART_STATES["start"], CART_STATES["end"]
    f = (0.0 if state == "start" else 1.0) if frac is None else max(0.0, min(1.0, frac))
    yaw0, yaw1 = y0, y1 - 360.0
    p = [p0[i] + (p1[i] - p0[i]) * f for i in range(3)]
    yaw = yaw0 + (yaw1 - yaw0) * (0.0 if f < 0.35 else (f - 0.35) / 0.65)
    root.location = M(*p)
    root.rotation_euler.z = -math.radians(yaw)

def build_alley_q2(MT):
    """MA (dead-end alley: steps, rubble heap, broken end wall, dark W face, light ashlar E face with stain), Q2 square
    on its rise (W terrace with roof R, S terrace, domed arcade on the N), tower T with its top 8 m separate."""
    rnd = random.Random(131)
    qc = _coll("TrostAlleyQ2")
    darkm = MT.setdefault("ma_dark", stone_mat("TrostMADark", "#4a4640", block=(2.0, 1.0)))
    ashm = MT.setdefault("ma_ash", stone_mat("TrostMAAshlar", "#b9b09a", block=(1.6, 0.8), damp="#8a8270", damp_z=(1.0, 6.0)))
    blk = MT.setdefault("ma_blocks", rock_mat("TrostMABlocks", "#4d4f52"))
    pale = MT["tower_cream"]
    bm = bmesh.new()
    # west face: blank dark block X -286..-266.5, Y 375..462, 20 m, cornice 14
    box(bm, (-276.25, 418.5, 8.5), (19.5, 87.0, 23.0), mi=0)
    box(bm, (-266.3, 418.5, 14.0), (0.6, 87.0, 0.8), mi=0)
    for y in range(386, 456, 7):
        for z in (15.5, 18.0):
            box(bm, (-266.42, y, z), (0.1, 1.0, 1.4), mi=4)
    # east face: light ashlar terrace X -257.5..-238 in two parts (SS between Y 418..428), 18 m, arched windows
    for y0, y1 in ((375.0, 418.0), (428.0, 462.0)):
        box(bm, (-247.75, (y0 + y1) / 2, 7.5), (19.5, y1 - y0, 21.0), mi=1)
        for y in [y0 + 3 + k * 4.0 for k in range(int((y1 - y0 - 4) / 4.0) + 1)]:
            for z in (11.0, 14.6):
                box(bm, (-257.58, y, z), (0.1, 1.0, 2.2), mi=4)
                cyl(bm, (-257.62, y, z + 1.1), (-257.52, y, z + 1.1), 0.5, seg=8, mi=4)
        for k in range(int((y1 - y0) / 1.4)):
            box(bm, (-257.4, y0 + 0.7 + k * 1.4, 18.4), (0.5, 0.7, 0.8), mi=1)
        box(bm, (-247.75, (y0 + y1) / 2, 18.05), (19.7, y1 - y0 + 0.2, 0.3), mi=1)
    box(bm, (-257.45, 445.0, 4.5), (0.08, 6.0, 8.0), mi=5)                     # dark stain at Y ~445
    for (x0, x1, y0, y1, z) in ((-286.0, -266.5, 375.0, 462.0, 20.0), (-257.5, -238.0, 375.0, 418.0, 18.0), (-257.5, -238.0, 428.0, 462.0, 18.0)):
        cx = (x0 + x1) / 2; inset = 0.0 if z > 19 else 1.0
        p = [bm.verts.new(c) for c in ((x0 + inset, y0 + inset, z), (x1 - inset, y0 + inset, z), (x1 - inset, y1 - inset, z), (x0 + inset, y1 - inset, z),
                                        (cx, y0 + inset, z + (x1 - x0) * 0.42), (cx, y1 - inset, z + (x1 - x0) * 0.42))]
        for fv, mi in (((p[0], p[4], p[5], p[3]), 6), ((p[1], p[2], p[5], p[4]), 6), ((p[0], p[1], p[4]), 0), ((p[2], p[3], p[5]), 0)):
            bm.faces.new(fv).material_index = mi
    # steps (5 treads 0.3 / 0.6 at Y 440-443), rubble heap Y 443-458 (6 m) against the broken end wall
    for k in range(5):
        h = 0.3 * (k + 1)
        box(bm, (-262.0, 440.0 + k * 0.6 + 0.3, h / 2), (9.0, 0.6, h), mi=0)
    box(bm, (-262.0, 450.5, 0.75), (9.0, 15.0, 1.5), mi=0)
    for k in range(36):
        y = rnd.uniform(443.5, 457.5); hmax = 1.5 + 4.5 * (y - 443.0) / 15.0
        s_ = rnd.uniform(0.5, 2.5)
        x = rnd.uniform(-266.0, -258.0)
        rock_blob(bm, (x, y, rnd.uniform(1.5, hmax)), (s_ * 0.6, s_ * 0.55, s_ * 0.5), rnd, 1, 2, 0.9, 0.35)
    for k in range(9):                                                         # broken end wall, jagged top 6-10 m
        x0 = -266.5 + k * 1.0
        h = rnd.uniform(6.0, 10.0)
        box(bm, (x0 + 0.5, 459.0, h / 2), (1.02, 2.0, h), mi=0)
    for k in range(12):
        x = rnd.uniform(-266, -258); z = rnd.uniform(1, 8)
        tube(bm, [(x, 457.95, z), (x + rnd.uniform(-1.5, 1.5), 457.95, z + rnd.uniform(-2, 2))], 0.06, 0.03, 3, 4)
    _mk("TrostAlleyMA", bm, [darkm, ashm, blk, MT["window_t"], MT["window_t"], MT["stone_dark"], MT["roof_town"]], qc)
    SPECIAL_FOOTPRINTS.extend([(-276.25, 418.5, 19.5, 87.0, 0.0, "MA_W"), (-247.75, 396.5, 19.5, 43.0, 0.0, "MA_E1"),
                               (-247.75, 445.0, 19.5, 34.0, 0.0, "MA_E2")])
    # Q2 surroundings (bases on the rise, sunk 4 m)
    bm = bmesh.new()
    zq = 5.0
    box(bm, (-258.0, 505.0, zq + (13.2 - 4.0) / 2 - 2.0), (12.0, 38.0, 13.2 + 4.0 + 4.0), mi=0)       # W terrace (roof R)
    box(bm, (-237.0, 483.0, 4.5 + (13.2 - 4.0) / 2 - 2.0), (30.0, 13.0, 13.2 + 8.0), mi=0)          # S terrace
    for y in range(489, 522, 3):
        for z in (zq + 5.5, zq + 8.7, zq + 11.9):
            box(bm, (-251.95, y, z), (0.1, 0.9, 1.4), mi=4)
    for x in range(-250, -224, 3):
        for z in (4.5 + 5.5, 4.5 + 8.7, 4.5 + 11.9):
            box(bm, (x, 489.55, z), (0.9, 0.1, 1.4), mi=4)
    p = [bm.verts.new(c) for c in ((-264.4, 486.0, zq + 13.2), (-251.6, 486.0, zq + 13.2), (-251.6, 524.0, zq + 13.2), (-264.4, 524.0, zq + 13.2),
                                    (-258.0, 486.0, 25.0), (-258.0, 524.0, 25.0))]
    for fv, mi in (((p[0], p[4], p[5], p[3]), 2), ((p[1], p[2], p[5], p[4]), 2), ((p[0], p[1], p[4]), 0), ((p[2], p[3], p[5]), 0)):
        bm.faces.new(fv).material_index = mi
    for k in range(4):                                                          # dormers on roof R's east slope
        y = 492.0 + k * 9.0
        box(bm, (-254.0, y, zq + 15.0), (1.6, 1.6, 1.8), mi=0)
    p = [bm.verts.new(c) for c in ((-252.4, 476.5, 17.7), (-221.6, 476.5, 17.7), (-221.6, 489.5, 17.7), (-252.4, 489.5, 17.7),
                                    (-252.4, 483.0, 24.5), (-221.6, 483.0, 24.5))]
    for fv, mi in (((p[0], p[1], p[5], p[4]), 2), ((p[3], p[4], p[5], p[2]), 2), ((p[0], p[4], p[3]), 0), ((p[1], p[2], p[5]), 0)):
        bm.faces.new(fv).material_index = mi
    # N side: pale arcaded building with a dome (X -252..-238, Y 520..534)
    box(bm, (-245.0, 527.0, zq + 3.0), (14.0, 14.0, 14.0), mi=3)
    for k in range(4):
        x = -250.5 + k * 3.6
        box(bm, (x, 519.95, zq + 2.2), (2.2, 0.15, 3.6), mi=4)
        cyl(bm, (x, 519.9, zq + 4.0), (x, 520.0, zq + 4.0), 1.1, seg=8, mi=4)
    box(bm, (-245.0, 527.0, zq + 10.4), (14.6, 14.6, 0.8), mi=3)
    dm = bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=8, radius=5.2)
    for v in dm["verts"]:
        v.co.z = max(v.co.z, 0.0)
        v.co += Vector((-245.0, 527.0, zq + 10.8))
    for f in {f for v in dm["verts"] for f in v.link_faces}:
        f.material_index = 5
    _mk("TrostQ2Buildings", bm, [MT["f_cream"], MT["f_cream"], MT["roof_town"], pale, MT["window_t"], MT["roof_copper"]], qc)
    SPECIAL_FOOTPRINTS.extend([(-258.0, 505.0, 12.0, 38.0, 0.0, "Q2_W"), (-237.0, 483.0, 30.0, 13.0, 0.0, "Q2_S"),
                               (-245.0, 527.0, 14.0, 14.0, 0.0, "Q2_N"), (-218.0, 522.0, 9.0, 9.0, 0.0, "T")])
    # tower T (-218, 522): 8 x 8, 34 m above its base; top 8 m separate (bursts)
    zb = ground_z_m(-218.0, 522.0)
    bm = bmesh.new()
    box(bm, (-218.0, 522.0, zb + 13.0 - 2.0), (8.0, 8.0, 26.0 + 4.0), mi=0)
    for z in (9.0, 18.0, 25.7):
        box(bm, (-218.0, 522.0, zb + z), (8.6, 8.6, 0.6), mi=0)
    for k in range(6):
        box(bm, (-218.0, 517.95, zb + 4.0 + k * 3.6), (0.7, 0.12, 1.6), mi=1)
    _mk("TrostTowerT", bm, [pale, MT["window_t"]], qc)
    bm = bmesh.new()                                     # local coords, origin at the top's base centre
    for sx in (-1, 1):
        for sy in (-1, 1):
            box(bm, (sx * 3.4, sy * 3.4, 2.5), (1.2, 1.2, 5.0), mi=0)
    for side in range(4):
        a = side * math.pi / 2; c, s_ = math.cos(a), math.sin(a)
        box(bm, (c * 3.6, s_ * 3.6, 0.3), (8.0 if abs(s_) > 0.5 else 0.8, 0.8 if abs(s_) > 0.5 else 8.0, 0.6), mi=0)
        box(bm, (c * 3.6, s_ * 3.6, 4.6), (8.0 if abs(s_) > 0.5 else 0.8, 0.8 if abs(s_) > 0.5 else 8.0, 0.8), mi=0)
    box(bm, (0, 0, 2.5), (5.6, 5.6, 5.0), mi=1)
    box(bm, (0, 0, 5.4), (8.8, 8.8, 0.8), mi=0)
    box(bm, (0, 0, 6.9), (8.4, 8.4, 2.4), mi=2, taper=(0.08, 0.08))
    _mk_at("TrostTowerT_Top", bm, [pale, MT["window_t"], MT["roof_red_t"]], (-218.0, 522.0, zb + 26.0), qc)
    return qc

# ====================================================================================== block 7: supply HQ (g6)
def _crenel(bm, x0, y0, x1, y1, z, mi, mw=0.8, gap=0.4, mh=1.2, th=0.6):
    L_ = math.hypot(x1 - x0, y1 - y0); n = max(1, int(L_ / (mw + gap)))
    rot = math.atan2(y1 - y0, x1 - x0)
    box(bm, ((x0 + x1) / 2, (y0 + y1) / 2, z + 0.5), (L_ + th, th, 1.0), rot, mi=mi)
    for k in range(n):
        u = (k + 0.5) / n
        box(bm, (x0 + (x1 - x0) * u, y0 + (y1 - y0) * u, z + 1.0 + mh / 2), (mw, th, mh), rot, mi=mi)

def _crenel_rect(bm, x0, x1, y0, y1, z, mi, inset=0.3):
    for a, b in (((x0, y0 + inset), (x1, y0 + inset)), ((x1 - inset, y0), (x1 - inset, y1)), ((x1, y1 - inset), (x0, y1 - inset)), ((x0 + inset, y1), (x0 + inset, y0))):
        _crenel(bm, a[0], a[1], b[0], b[1], z, mi)

def _arched_win(bm, x, y, z, w, h, face, mi, depth=0.12):
    """Round-arched window inset: face 's'/'n' (normal -/+Y) or 'e'/'w'."""
    if face in ("s", "n"):
        yy = y + (-depth / 2 if face == "s" else depth / 2)
        box(bm, (x, yy, z + (h - w / 2) / 2), (w, depth, h - w / 2), mi=mi)
        cyl(bm, (x, yy - depth / 2, z + h - w / 2), (x, yy + depth / 2, z + h - w / 2), w / 2, seg=10, mi=mi)
    else:
        xx = x + (depth / 2 if face == "e" else -depth / 2)
        box(bm, (xx, y, z + (h - w / 2) / 2), (depth, w, h - w / 2), mi=mi)
        cyl(bm, (xx - depth / 2, y, z + h - w / 2), (xx + depth / 2, y, z + h - w / 2), w / 2, seg=10, mi=mi)

def build_hq(MT):
    """Supply HQ (g6): 3-tier keep at the WEST end (-250, 640) with slate-blue turret caps, 7 arched windows, clock
    tower; terrace + stair; warehouse wing HW east (rusticated arcade, pilaster strips, dark slate roof, chimneys);
    storeroom HS interior (brick piers, rafters, groin vaults, cylinders in stalls, torches), lift cage on 4 chains +
    guide tower; the 36 m bay as its own dissolvable object + shadow-only proxy; back range; gutted house GH."""
    rnd = random.Random(141)
    hc = _coll("TrostHQ")
    up = _coll("TrostHQ_Upper")
    hqs = MT.setdefault("hq_stone", stone_mat("HQSandstone", "#cdb48a", block=(1.2, 0.6), damp="#8f8068", damp_z=(1.5, 6.0)))
    hqs2 = MT.setdefault("hq_wing", stone_mat("HQWingStone", "#c9b28a", block=(1.2, 0.6)))
    rust = MT.setdefault("hq_rust", stone_mat("HQRustic", "#6e6458", block=(1.6, 0.9), mortar_k=0.7))
    slate = MT.setdefault("hq_slate", roof_mat("HQSlateDark", ["#3d434b", "#454b52"]))
    turret = MT.setdefault("hq_turret", roof_mat("HQTurretSlate", ["#5a6b7e", "#56677a"]))
    flag = MT.setdefault("hq_flag", flat_mat("HQFlagstone", "#cfc6b0", 0.9, 0.06))
    glass = MT.setdefault("hq_glass", flat_mat("HQGlass", "#5d7894", 0.4, 0.05))
    lead = MT.setdefault("hq_lead", flat_mat("HQLeaded", "#9fb6c4", 0.4, 0.05))
    clock = MT.setdefault("hq_clock", flat_mat("HQClock", "#ece6d6", 0.6, 0.0))
    ibrick = MT.setdefault("hq_ibrick", brick_mat("HQInnerBrick", "#6b3528", "#4a2a20", scale=3.5))
    plankf = MT.setdefault("hq_floor", plank_mat("HQFloor", "#5a4636", vertical=False))
    rafter = MT.setdefault("hq_rafter", flat_mat("HQRafter", "#4a3427", 0.85, 0.06))
    gasm = MT.setdefault("hq_gas", flat_mat("HQGasCyl", "#4a4038", 0.5, 0.08))
    brass = MT.setdefault("hq_brass", flat_mat("HQBrass", "#9a8050", 0.4, 0.05))
    torch = MT.setdefault("hq_torch", emit_mat("HQTorch", "#ff9a40", 8.0))
    chim = MT["chimney"]
    mats = [hqs, hqs2, rust, slate, turret, flag, MT["window_t"], glass, lead, clock, chim]
    # ---------------- keep
    bm = bmesh.new()
    box(bm, (-250.0, 640.0, 12.5), (32.0, 32.0, 31.0), mi=0)                     # tier 1, Z -3..28
    box(bm, (-250.0, 640.0, 27.9), (31.0, 31.0, 0.2), mi=5)                       # roof walk
    _crenel_rect(bm, -266.0, -234.0, 624.0, 656.0, 28.0, 0)
    for sx in (-1, 1):
        for sy in (-1, 1):
            cx, cy = -250.0 + sx * 16.0, 640.0 + sy * 16.0
            box(bm, (cx, cy, 15.0), (6.0, 6.0, 36.0), mi=0)
            box(bm, (cx, cy, 33.2), (6.6, 6.6, 0.5), mi=0)
            box(bm, (cx, cy, 35.2), (6.6, 6.6, 3.6), mi=4, taper=(0.05, 0.05))
            for k in (-1, 1):
                box(bm, (cx + k * 1.3, cy + sy * 3.02, 29.0), (0.4, 0.1, 2.0), mi=6)
    for k in range(5):                                                           # few openings in tier 1
        x = -260.0 + k * 5.0
        box(bm, (x, 623.94, 18.0), (0.7, 0.12, 2.4), mi=6)
    box(bm, (-266.06, 640.0, 4.5), (0.12, 4.0, 6.0), mi=6)
    # tier 2: X -260..-240, Y 634..654 to Z 44, crenellation, 4 small turrets (caps to 49)
    box(bm, (-250.0, 644.0, 36.0), (20.0, 20.0, 16.0), mi=0)
    _crenel_rect(bm, -260.0, -240.0, 634.0, 654.0, 44.0, 0)
    for sx in (-1, 1):
        for sy in (-1, 1):
            cx, cy = -250.0 + sx * 9.6, 644.0 + sy * 9.6
            box(bm, (cx, cy, 40.5), (3.2, 3.2, 9.0), mi=0)
            box(bm, (cx, cy, 46.9), (3.6, 3.6, 3.8), mi=4, taper=(0.05, 0.05))
    for k in range(7):                                                           # the row of 7 round-arched windows (Z 34-37)
        x = -258.0 + k * (16.0 / 6.0)
        _arched_win(bm, x, 634.0, 34.0, 1.3, 3.0, "s", 6)
    for x in (-257.5, -242.5):                                                   # tall leaded hall windows (crash-in)
        _arched_win(bm, x, 634.0, 37.4, 2.4, 6.0 - 0.6, "s", 8)
    for y in (639.0, 649.0):
        _arched_win(bm, -240.0, y, 30.5, 2.4, 6.0, "e", 8)
    # hall hole in tier 2's south face (Z 29-33, ragged, rubble rim)
    for k in range(14):
        a = rnd.uniform(0, math.tau)
        box(bm, (-251.0 + math.cos(a) * 2.2, 633.6, 31.0 + math.sin(a) * 2.0), (rnd.uniform(0.6, 1.2), 0.9, rnd.uniform(0.5, 1.0)), rot=rnd.uniform(0, 3), mi=0)
    box(bm, (-251.0, 633.9, 31.0), (3.4, 0.3, 3.6), mi=6)
    # tier 3: clock/bell tower 10 x 10 to Z 54, belfry arches, clock face (south), pedimented cap to Z 58
    box(bm, (-250.0, 644.0, 48.0), (10.0, 10.0, 12.0), mi=0)
    box(bm, (-250.0, 644.0, 54.3), (10.8, 10.8, 0.6), mi=0)
    for face, (x, y) in (("s", (-250.0, 639.0)), ("n", (-250.0, 649.0))):
        _arched_win(bm, x, y, 44.6, 3.0, 5.0, face, 6)
    for face, (x, y) in (("e", (-245.0, 644.0)), ("w", (-255.0, 644.0))):
        _arched_win(bm, x, y, 44.6, 3.0, 5.0, face, 6)
    cyl(bm, (-250.0, 638.88, 51.6), (-250.0, 638.7, 51.6), 1.5, seg=20, mi=9)
    p = [bm.verts.new(c) for c in ((-255.4, 638.6, 54.6), (-244.6, 638.6, 54.6), (-244.6, 649.4, 54.6), (-255.4, 649.4, 54.6), (-250.0, 638.6, 58.0), (-250.0, 649.4, 58.0))]
    for fv, mi in (((p[0], p[4], p[5], p[3]), 4), ((p[1], p[2], p[5], p[4]), 4), ((p[0], p[1], p[4]), 0), ((p[2], p[3], p[5]), 0)):
        bm.faces.new(fv).material_index = mi
    # terrace HT (X -270..-230, Y 612..624, Z 2.5) on a battered podium, low crenellation, stair on its west side
    hexa(bm, [(-270.6, 611.4, -1.0), (-229.4, 611.4, -1.0), (-229.4, 624.0, -1.0), (-270.6, 624.0, -1.0),
              (-270.0, 612.0, 2.5), (-230.0, 612.0, 2.5), (-230.0, 624.0, 2.5), (-270.0, 624.0, 2.5)], 0)
    _crenel(bm, -270.0, 612.3, -230.0, 612.3, 2.5, 0, mh=0.7, th=0.5)
    for k in range(8):
        box(bm, (-274.0 + k * 0.0, 616.0, 0.16 + k * 0.31), (8.0 - k * 1.0, 6.0, 0.32), mi=0)
    keep = _mk("TrostHQ_Keep", bm, mats, hc)
    # ---------------- warehouse wing HW (static parts: everything except the 36 m bay above the storeroom)
    BX0, BX1 = -205.0, -169.0
    def wing_part(bm, xa, xb, with_ground=True, cut=False):
        """Wing slice X xa..xb: ground storey (Z 0-10 rusticated, arcade), 4 upper storeys to Z 24, roof to Z 41."""
        if with_ground:
            box(bm, ((xa + xb) / 2, 628.6, 5.0), (xb - xa, 1.2, 10.0), mi=2)
            box(bm, ((xa + xb) / 2, 651.4, 5.0), (xb - xa, 1.2, 10.0), mi=2)
        z0 = 4.5 if cut else 10.0
        box(bm, ((xa + xb) / 2, 628.6, (z0 + 24.0) / 2), (xb - xa, 1.2, 24.0 - z0), mi=1)
        box(bm, ((xa + xb) / 2, 651.4, (10.0 + 24.0) / 2), (xb - xa, 1.2, 14.0), mi=1)
        for y in (628.0, 652.0):
            s = -1 if y < 640 else 1
            for x in [xa + 1.5 + k * 3.0 for k in range(int((xb - xa - 1.0) / 3.0))]:
                for z in (12.2, 15.7, 19.2, 22.2):
                    box(bm, (x, y + s * 0.05, z), (1.1, 0.12, 1.3), mi=6)
            for x in [xa + 6.0 * k for k in range(int((xb - xa) / 6.0) + 1)]:
                if xa <= x <= xb:
                    box(bm, (x, y + s * 0.25, 17.0), (0.9, 0.5, 14.0), mi=1)
        p = [bm.verts.new(c) for c in ((xa, 627.4, 23.8), (xb, 627.4, 23.8), (xb, 652.6, 23.8), (xa, 652.6, 23.8), (xa, 640.0, 41.0), (xb, 640.0, 41.0))]
        bm.faces.new((p[0], p[1], p[5], p[4])).material_index = 3
        bm.faces.new((p[3], p[4], p[5], p[2])).material_index = 3
        return p
    bm = bmesh.new()
    for xa, xb in ((-234.0, BX0), (BX1, -136.0)):
        p = wing_part(bm, xa, xb)
        if xa == -234.0:
            bm.faces.new((p[0], p[4], p[3])).material_index = 1
        else:
            bm.faces.new((p[1], p[2], p[5])).material_index = 1
        box(bm, ((xa + xb) / 2, 640.0, 5.0), (xb - xa, 22.8, 10.0), mi=2)             # solid ground storey
        box(bm, ((xa + xb) / 2, 640.0, 17.0), (xb - xa - 0.4, 22.8, 14.0), mi=1)
    for k in range(12):                                                                # arcade: 12 round arches, 6 m tall
        x = -229.0 + k * 8.0
        if BX0 - 1 < x < BX1 + 1:
            continue
        _arched_win(bm, x, 628.0, 0.0, 4.0, 6.0, "s", 6)
    _arched_win(bm, BX0 - 3.2, 628.0, 0.0, 5.0, 7.0, "s", 6)                          # the large arched doorway (breakout)
    for y in (630.0, 650.0):                                                           # east gable: pilaster strips, windows
        box(bm, (-135.75, y, 20.0), (0.6, 1.2, 40.0), mi=1)
    for z in (14.0, 19.0, 28.0):
        box(bm, (-135.95, 640.0, z), (0.12, 1.2, 1.4), mi=6)
    for x in (-226.0, -214.0, -158.0, -146.0):                                         # chimneys
        box(bm, (x, 643.0 if x > -200 else 637.0, 40.0), (1.4, 1.4, 6.0), mi=10)
    for x in (-222.0, -152.0):
        for y, ss in ((633.0, -1), (647.0, 1)):
            box(bm, (x, y, 28.5), (1.6, 1.8, 2.2), mi=1)
            box(bm, (x, y + ss * 0.95, 28.3), (0.8, 0.1, 1.0), mi=6)
    _mk("TrostHQ_Wing", bm, mats, hc)
    # ---------------- the storeroom HS (stays): ground storey of the bay, brick interior, vaults, lift, cylinders, torches
    bm = bmesh.new()
    box(bm, ((BX0 + BX1) / 2, 628.6, 2.25), (BX1 - BX0, 1.2, 4.5), mi=2)              # south wall cut to Z 4.5
    box(bm, ((BX0 + BX1) / 2, 628.6, 4.55), (BX1 - BX0, 1.25, 0.12), mi=11)           # dark caps
    box(bm, ((BX0 + BX1) / 2, 651.4, 5.0), (BX1 - BX0, 1.2, 10.0), mi=2)
    for x in (BX0 - 0.6, BX1 + 0.6):
        box(bm, (x, 640.0, 5.0), (1.2, 24.0, 10.0), mi=2)
    box(bm, ((BX0 + BX1) / 2, 640.0, 0.05), (BX1 - BX0, 22.0, 0.1), mi=14)
    for x in [BX0 + 6.0 * k for k in range(1, 6)]:                                     # brick piers 1.2 m every 6 m
        for y in (630.4, 649.6):
            box(bm, (x, y, 3.25), (1.2, 1.2, 6.5), mi=12)
        box(bm, (x, 640.0, 6.0), (0.4, 20.0, 0.5), mi=15)                                # tie-beam rafters (N-S) at Z 6.0
    for x in (BX0 + 0.9, BX1 - 0.9):                                                   # inner brick lining
        box(bm, (x, 640.0, 4.75), (0.3, 21.6, 9.5), mi=12)
    box(bm, ((BX0 + BX1) / 2, 650.65, 4.75), (BX1 - BX0, 0.3, 9.5), mi=12)
    for side_x in (BX0 + 2.0, BX1 - 2.0):                                              # gas cylinders in timber stalls
        for k in range(14):
            y = 631.5 + k * 1.35
            cyl(bm, (side_x, y, 0.1), (side_x, y, 1.45), 0.42, seg=8, mi=16)
            cyl(bm, (side_x, y, 1.45), (side_x, y, 1.75), 0.42, 0.12, seg=8, mi=16)
            cyl(bm, (side_x, y, 1.75), (side_x, y, 1.95), 0.08, seg=6, mi=17)
        for k in range(8):
            y = 631.0 + k * 2.7
            box(bm, (side_x, y, 1.0), (1.4, 0.12, 2.0), mi=15)
        box(bm, (side_x, 640.0, 1.6), (1.4, 19.0, 0.12), mi=15)
    for k in range(10):                                                                # torches on the piers (orange flame)
        x = BX0 + 6.0 * (1 + k % 5); y = 631.2 if k < 5 else 648.8
        box(bm, (x, y, 2.3), (0.15, 0.15, 0.6), mi=15)
        rock_blob(bm, (x, y, 2.8), (0.18, 0.18, 0.32), rnd, 1, 18, 1.0, 0.1)
    # lift guide tower: 4 posts 0.4 m at the cage corners, X-braces on the lower bays; brick shaft above the vault
    lx, ly = ANCHORS_M["HQ_LIFT"]
    for sx in (-1, 1):
        for sy in (-1, 1):
            box(bm, (lx + sx * 2.95, ly + sy * 2.95, 5.0), (0.4, 0.4, 10.0), mi=15)
    for sy in (-1, 1):
        cyl(bm, (lx - 2.95, ly + sy * 2.95, 0.3), (lx + 2.95, ly + sy * 2.95, 4.5), 0.12, seg=4, mi=15)
        cyl(bm, (lx + 2.95, ly + sy * 2.95, 0.3), (lx - 2.95, ly + sy * 2.95, 4.5), 0.12, seg=4, mi=15)
    store = _mk("TrostHQ_Store", bm, mats + [MT["iron_t"], ibrick, MT["stone_dark"], plankf, rafter, gasm, brass, torch], hc)
    # ---------------- the bay above the storeroom (dissolves: set_hq_cutaway) + shadow-only proxy
    bm = bmesh.new()
    p = wing_part(bm, BX0, BX1, with_ground=False, cut=True)
    box(bm, ((BX0 + BX1) / 2, 640.0, 10.2), (BX1 - BX0, 22.8, 0.4), mi=14)          # lift-room floor (Z 10)
    for x in [BX0 + 3.0 + 6.0 * k for k in range(6)]:                                  # groin vaults (spring 6.5, crown 9.5)
        for y in (635.0, 645.0):
            for k in range(4):
                a = math.pi * (k + 0.5) / 4
                box(bm, (x + math.cos(a) * 2.6, y, 6.5 + math.sin(a) * 3.0), (1.6, 10.0, 0.4), rot=0.0, mi=12)
                box(bm, (x, y + math.cos(a) * 4.4, 6.5 + math.sin(a) * 3.0), (6.0, 1.8, 0.4), mi=12)

    for x in (BX0 + 2.0, BX1 - 2.0):
        box(bm, (x, 640.0, 15.0), (1.2, 1.2, 9.6), mi=12)
    box(bm, (lx, ly, 17.0), (7.4, 7.4, 13.6), mi=12)
    bay = _mk("TrostHQ_Bay", bm, mats + [MT["iron_t"], ibrick, MT["stone_dark"], plankf], up)
    bm = bmesh.new()
    box(bm, ((BX0 + BX1) / 2, 640.0, 24.0), (BX1 - BX0 + 0.4, 25.0, 34.0))
    proxy = _mk("TrostHQ_BayShadow", bm, [MT["stone_dark"]], hc)
    try:
        proxy.visible_camera = False; proxy.visible_diffuse = False; proxy.visible_glossy = False
        proxy.visible_shadow = True
    except Exception:
        pass
    HQ_UPPER[:] = [bay.name]
    # ---------------- the lift cage (moves): plank floor, planked lower sides + baluster rail, iron corner posts,
    # 4 chains to a pulley block 3 m above with a lantern.  Origin = cage floor centre.
    bm = bmesh.new()
    box(bm, (0, 0, 0.1), (5.5, 5.5, 0.2), mi=0)
    for sx in (-1, 1):
        box(bm, (sx * 2.7, 0, 0.55), (0.1, 5.5, 0.7), mi=0); box(bm, (0, sx * 2.7, 0.55), (5.5, 0.1, 0.7), mi=0)
        box(bm, (sx * 2.7, 0, 1.15), (0.08, 5.5, 0.08), mi=1); box(bm, (0, sx * 2.7, 1.15), (5.5, 0.08, 0.08), mi=1)
        for k in range(9):
            u = -2.4 + k * 0.6
            box(bm, (sx * 2.7, u, 1.0), (0.04, 0.04, 0.3), mi=1); box(bm, (u, sx * 2.7, 1.0), (0.04, 0.04, 0.3), mi=1)
    for sx in (-1, 1):
        for sy in (-1, 1):
            box(bm, (sx * 2.7, sy * 2.7, 0.6), (0.12, 0.12, 1.2), mi=1)
            cyl(bm, (sx * 2.7, sy * 2.7, 1.2), (0, 0, 4.2), 0.05, seg=4, mi=1)
    box(bm, (0, 0, 4.4), (0.7, 0.7, 0.5), mi=2)
    box(bm, (0, 0, 3.7), (0.3, 0.3, 0.45), mi=3)
    cage = _mk_at("TrostHQ_Cage", bm, [MT["plank_t"], MT["iron_t"], MT["timber_d"], torch], (lx, ly, 10.0), hc)
    # ---------------- back range HB (mansard slate, dormers) + courtyard tree; gutted house GH
    bm = bmesh.new()
    box(bm, (-192.0, 688.0, 5.5), (84.0, 24.0, 17.0), mi=0)
    hexa(bm, [(-234.0, 676.0, 14.0), (-150.0, 676.0, 14.0), (-150.0, 700.0, 14.0), (-234.0, 700.0, 14.0),
              (-232.0, 679.0, 20.0), (-152.0, 679.0, 20.0), (-152.0, 697.0, 20.0), (-232.0, 697.0, 20.0)], 3)
    for k in range(12):
        x = -229.0 + k * 7.0
        for y, ss in ((677.5, -1), (698.5, 1)):
            box(bm, (x, y, 16.6), (1.5, 1.5, 2.0), mi=0)
        _arched_win(bm, x, 676.0, 0.0, 3.0, 4.6, "s", 6)
    for x in range(-232, -150, 3):
        for z in (7.0, 10.5):
            box(bm, (x, 675.95, z), (1.0, 0.12, 1.4), mi=6)
    cyl(bm, (-190.0, 664.0, 0.0), (-190.0, 664.0, 4.0), 0.45, seg=6, mi=10)
    for k in range(4):
        rock_blob(bm, (-190.0 + rnd.uniform(-2, 2), 664.0 + rnd.uniform(-2, 2), 6.5), (3.2, 3.2, 2.8), rnd, 2, 5, 1.0, 0.2)
    gh_mats = [hqs2, MT["window_t"], MT["roof_town"], slate, MT["rubble_brick"], MT["leafy"], MT["window_t"], MT["window_t"],
               MT["window_t"], MT["window_t"], MT["bark_t"]]
    # gutted house GH at (-200, 566): 4 storeys, 5 m black slot through all storeys and the roof, rubble cone r 8
    for xa, xb in ((-208.0, -202.5), (-197.5, -192.0)):
        box(bm, ((xa + xb) / 2, 563.0, 5.1), (xb - xa, 14.0, 16.2), mi=0)
        p = [bm.verts.new(c) for c in ((xa, 555.6, 13.2), (xb, 555.6, 13.2), (xb, 570.4, 13.2), (xa, 570.4, 13.2), (xa, 563.0, 20.0), (xb, 563.0, 20.0))]
        bm.faces.new((p[0], p[1], p[5], p[4])).material_index = 2
        bm.faces.new((p[3], p[4], p[5], p[2])).material_index = 2
    box(bm, (-200.0, 563.0, 6.0), (5.0, 13.6, 14.0), mi=6)
    for k in range(45):
        a = rnd.uniform(0, math.pi); r = 8.0 * rnd.random() ** 0.7
        x, y = -200.0 + math.cos(a) * r, 570.0 + math.sin(a) * r * 0.8
        s_ = rnd.uniform(0.4, 1.6)
        box(bm, (x, y, s_ * 0.3 + (1 - r / 8.0) * 2.0), (s_, s_, s_ * 0.6), rot=rnd.uniform(0, 3), mi=4)
    _mk("TrostHQ_Back", bm, gh_mats, hc)
    for f in ((-192.0, 688.0, 84.0, 24.0, 0.0), (-200.0, 563.0, 16.0, 14.0, 0.0)):
        SPECIAL_FOOTPRINTS.append((*f, "HQ"))
    return keep

# ====================================================================================== block 8: cannon basin K (g7)
def build_basin(MT):
    """K: floor Z -3.6 (pale sandy south half, mossy green north half), piers PW/PE battered 8 deg, bank SB (12 steps,
    dark nosings), plinth PL with a wavy band, west flight SW, terrace TT, gun bastion GB (deck Z 20, rails, turntable,
    cannon aimed at the trio), bell tower T_K, Garrison building GH (clock oculus), half-timbered range, 2 boats,
    hoist L_K (derrick + wheel + winch hut on the Rose top, basket on 4 chains = TrostBasket_K)."""
    rnd = random.Random(151)
    kc = _coll("TrostBasin")
    old = MT.setdefault("basin_stone", stone_mat("BasinStone", "#bdb5a3", block=(1.2, 0.6), damp="#6f6a58", moss="#4e5a3a", damp_z=(4.0, 9.0)))
    bank = MT.setdefault("basin_bank", stone_mat("BasinBank", "#cdbf9a", block=(1.0, 0.3), damp="#8f8670", damp_z=(-3.0, -1.0)))
    nose = MT.setdefault("step_edge", flat_mat("StepEdge", "#5b5446", 0.9, 0.05))
    floor_m = NB("BasinFloor", 0.95)
    o = floor_m.obj(); X, Y, Z = floor_m.sep(o)
    vo = floor_m.vor(o, 1.6, "F1", 1.0)
    rs, gs, bs = floor_m.sep(vo.outputs["Color"])
    sandy = floor_m.ramp(rs, [(0.0, lin("#b8ab8a")), (1.0, lin("#cfc3a2"))])
    mossy = floor_m.ramp(rs, [(0.0, lin("#55663f")), (1.0, lin("#7a8a55"))])
    n = floor_m.noise(o, 0.12, 4.0)
    f = floor_m.smooth(floor_m.math("ADD", Y, floor_m.math("MULTIPLY", n.outputs["Fac"], 10.0)), 849.0, 856.0)
    floorc = floor_m.finish(floor_m.mix(f, sandy, mossy))
    gun = MT["iron_t"]
    mats = [old, bank, nose, floorc, MT["window_t"], MT["timber_d"], MT["roof_red_t"], MT["tower_cream"], MT["f_cream"], MT["f_tcream"],
            MT["roof_town"], MT["water_c"], MT["plank_t"], MT["iron_t"], flat_mat("BasinGreen", "#3d6b45", 0.7, 0.0), MT["hq_clock"] if "hq_clock" in MT else MT["cornice"]]
    bm = bmesh.new()
    # floor KF (+ a sub-floor under the bank)
    box(bm, (362.5, 849.0, -3.7), (45.0, 32.0, 0.2), mi=3)
    box(bm, (362.5, 836.0, -4.5), (45.6, 32.0, 1.4), mi=0)
    box(bm, (385.3, 849.0, -3.9), (0.6, 32.0, 0.6), mi=0)                  # 0.6 m lip to the water
    for y in (838.0, 845.0, 852.0, 857.0):
        cyl(bm, (385.7, y, -3.75), (385.9, y, -3.75), 0.25, seg=8, mi=13)
    # bank SB: 12 steps (0.3 / 1.0) Y 833 -> 821, Z -3.6 -> 0, dark nosings
    for k in range(12):
        y1 = 833.0 - k * 1.0
        z = -3.6 + (k + 1) * 0.3
        box(bm, (362.5, y1 - 0.5 - (11 - k) * 0.5 + (11 - k) * 0.5, (z - 4.0) / 2), (45.0, 1.0, z + 4.0), mi=1)
        box(bm, (362.5, y1 - 0.03, z - 0.04), (45.0, 0.1, 0.1), mi=2)
    for k in range(4):                                                     # east end runs on into the water
        box(bm, (387.5, 833.0 - k * 1.0 - 0.5, -3.9 + k * 0.3), (4.0, 1.0, 0.6), mi=1)
    # plinth PL X 357..367, Y 828..838, top Z -0.6, wavy band under the rim
    box(bm, (362.0, 833.0, -2.3), (10.0, 10.0, 3.4), mi=1)
    for k in range(20):
        x = 357.2 + k * 0.5
        box(bm, (x, 837.96, -1.05 + 0.08 * math.sin(k * 1.3)), (0.45, 0.12, 0.25), mi=0)
    # west flight SW: X 340..348, Y 833..855, steps down eastward from a ledge (Z 0 at X 340) to the floor
    for k in range(12):
        x0 = 340.0 + k * 0.667
        z = -k * 0.3
        box(bm, (x0 + 0.333, 844.0, (z - 4.0) / 2), (0.667, 22.0, z + 4.0), mi=1)
        box(bm, (x0 + 0.65, 844.0, z - 0.04), (0.1, 22.0, 0.1), mi=2)
    # piers PW (X 331..340) / PE (X 385..393), Y 857..865, battered 8 deg to Z 30 (7 x 4), then a pilaster to the top
    for x0, x1 in ((331.0, 340.0), (385.0, 393.0)):
        cx = (x0 + x1) / 2
        hexa(bm, [(x0, 857.0, -5.0), (x1, 857.0, -5.0), (x1, 865.2, -5.0), (x0, 865.2, -5.0),
                  (cx - 3.5, 861.0, 30.0), (cx + 3.5, 861.0, 30.0), (cx + 3.5, 865.2, 30.0), (cx - 3.5, 865.2, 30.0)], 0)
        box(bm, (cx, 862.6, 41.0), (7.0, 5.2, 22.0), mi=0)
        box(bm, (cx, 862.0, 52.6), (7.8, 6.6, 1.2), mi=0)
    # gun bastion GB: X 308..338, Y 849..865, deck Z 20, battered faces, parapet E + S, spur rails + turntable
    hexa(bm, [(307.0, 848.0, -1.0), (339.0, 848.0, -1.0), (339.0, 865.2, -1.0), (307.0, 865.2, -1.0),
              (308.0, 849.0, 20.0), (338.0, 849.0, 20.0), (338.0, 865.2, 20.0), (308.0, 865.2, 20.0)], 0)
    box(bm, (323.0, 857.0, 20.05), (29.6, 15.6, 0.1), mi=7)
    _crenel(bm, 308.0, 849.3, 338.0, 849.3, 20.0, 0, mw=30.0, gap=0.0, mh=0.2, th=0.6)
    _crenel(bm, 337.7, 849.0, 337.7, 865.0, 20.0, 0, mw=16.0, gap=0.0, mh=0.2, th=0.6)
    for xo in (-0.75, 0.75):
        box(bm, (313.0, 857.0 + xo, 20.2), (10.0, 0.12, 0.2), mi=13)
    for k in range(8):
        box(bm, (309.0 + k * 1.2, 857.0, 20.12), (0.35, 2.3, 0.1), mi=5)
    box(bm, (310.0, 851.0, 24.0), (4.0, 4.0, 8.0), mi=0)                    # stair tower (SW corner)
    box(bm, (310.0, 851.0, 28.6), (4.4, 4.4, 1.2), mi=6, taper=(0.1, 0.1))
    # terrace TT Y 813..821 (Z 0): paving + iron bollards on the canal side
    box(bm, (350.0, 817.0, -0.05), (100.0, 8.0, 0.2), mi=1)
    for y in (814.0, 817.5, 821.0):
        cyl(bm, (380.5, y, 0.0), (380.5, y, 0.9), 0.18, seg=8, mi=13)
    # bell tower T_K (322, 818): 4 storeys pale cream, belfry Z 20-26, red pyramid to Z 33
    box(bm, (322.0, 818.0, 8.5), (8.0, 8.0, 23.0), mi=7)
    for z in (5.0, 10.0, 15.0, 20.0, 26.0):
        box(bm, (322.0, 818.0, z), (8.6, 8.6, 0.5), mi=7)
    for face in range(4):
        a = face * math.pi / 2; c, s_ = math.cos(a), math.sin(a)
        for u in (-1.8, 1.8):
            _arched_win(bm, 322.0 + c * 4.0 - s_ * u, 818.0 + s_ * 4.0 + c * u, 20.6, 1.6, 4.6, "e" if c > 0.5 else "w" if c < -0.5 else "n" if s_ > 0.5 else "s", 4)
        for zz in (7.0, 12.0, 17.0):
            box(bm, (322.0 + c * 4.02, 818.0 + s_ * 4.02, zz), (0.8 if abs(s_) > 0.5 else 0.12, 0.12 if abs(s_) > 0.5 else 0.8, 1.6), mi=4)
    box(bm, (322.0, 818.0, 23.0), (7.0, 7.0, 6.0), mi=4)
    for sx in (-1, 1):
        for sy in (-1, 1):
            box(bm, (322.0 + sx * 3.4, 818.0 + sy * 3.4, 23.0), (1.2, 1.2, 6.0), mi=7)
    box(bm, (322.0, 818.0, 26.6), (8.8, 8.8, 0.8), mi=7)
    box(bm, (322.0, 818.0, 30.0), (8.6, 8.6, 6.0), mi=6, taper=(0.05, 0.05))
    # Garrison building GH: X 341..377, Y 792..812, eave 13, ridge 21, clock oculus in the west gable, green arched windows
    box(bm, (359.0, 802.0, 5.0), (36.0, 20.0, 16.0), mi=8)
    p = [bm.verts.new(c) for c in ((341.0, 791.4, 13.0), (377.0, 791.4, 13.0), (377.0, 812.6, 13.0), (341.0, 812.6, 13.0), (341.0, 802.0, 21.0), (377.0, 802.0, 21.0))]
    for fv, mi in (((p[0], p[1], p[5], p[4]), 10), ((p[3], p[4], p[5], p[2]), 10), ((p[0], p[4], p[3]), 8), ((p[1], p[2], p[5]), 8)):
        bm.faces.new(fv).material_index = mi
    cyl(bm, (340.9, 802.0, 15.6), (340.7, 802.0, 15.6), 1.4, seg=16, mi=15)
    for k in range(9):
        x = 343.5 + k * 3.8
        for z in (1.0, 5.6):
            _arched_win(bm, x, 812.0, z, 1.4, 3.4, "n", 14)
        box(bm, (x, 812.05, 10.6), (1.0, 0.12, 1.4), mi=4)
    for k in range(6):
        x = 344.0 + k * 6.0
        box(bm, (x, 809.0, 15.4), (1.6, 1.8, 2.0), mi=8)
    # half-timbered range X 377..387, Y 770..813 (4 storeys, dormers)
    box(bm, (382.0, 791.5, 5.1), (10.0, 43.0, 16.2), mi=9)
    p = [bm.verts.new(c) for c in ((376.6, 770.0, 13.2), (387.4, 770.0, 13.2), (387.4, 813.0, 13.2), (376.6, 813.0, 13.2), (382.0, 770.0, 19.5), (382.0, 813.0, 19.5))]
    for fv, mi in (((p[0], p[4], p[5], p[3]), 10), ((p[1], p[2], p[5], p[4]), 10), ((p[0], p[1], p[4]), 9), ((p[2], p[3], p[5]), 9)):
        bm.faces.new(fv).material_index = mi
    for k in range(7):
        y = 773.0 + k * 6.0
        for xx, ss in ((378.5, -1), (385.5, 1)):
            box(bm, (xx, y, 15.0), (1.6, 1.6, 2.0), mi=9)
    _mk("TrostBasin", bm, mats, kc)
    SPECIAL_FOOTPRINTS.extend([(359.0, 802.0, 36.0, 20.0, 0.0, "K_GH"), (382.0, 791.5, 10.0, 43.0, 0.0, "K_HT"),
                               (322.0, 818.0, 8.0, 8.0, 0.0, "T_K")])
    # the cannon on the bastion (turntable centre (318, 857, 20), bearing 95 deg, depression 27 deg)
    cm = _cannon_mesh(MT)
    cn = bpy.data.objects.new("TrostCannon_K", cm); kc.objects.link(cn)
    cn.location = M(318.0, 857.0, 20.0)
    cn.rotation_euler = (0.0, 0.0, -math.radians(95.0))
    # 2 rowing boats (389, 843) / (389, 851), 7 x 1.8 m, long axis N-S
    bm = bmesh.new()
    for y in (843.0, 851.0):
        hexa(bm, [(388.3, y - 3.5, -4.6), (389.7, y - 3.5, -4.6), (389.7, y + 3.5, -4.6), (388.3, y + 3.5, -4.6),
                  (388.1, y - 3.2, -3.9), (389.9, y - 3.2, -3.9), (389.9, y + 3.0, -3.9), (388.1, y + 3.0, -3.9)], 0)
        box(bm, (389.0, y + 3.25, -4.0), (0.9, 0.8, 0.4), mi=0, taper=(0.2, 1.0))
        for k in (-1.5, 0.0, 1.5):
            box(bm, (389.0, y + k, -3.95), (1.7, 0.3, 0.1), mi=1)
    _mk("TrostBoats_K", bm, [flat_mat("BoatWood", "#5a4030", 0.8, 0.08), MT["plank_t"]], kc)
    # hoist L_K: derrick + wheel + counterweight + winch hut on the Rose top (338, 868, 50); basket on 4 chains
    bm = bmesh.new()
    for sx in (-2.0, 2.0):
        cyl(bm, (338.0 + sx, 870.0, 50.0), (338.0, 866.0, 61.0), 0.25, seg=5, mi=0)
    cyl(bm, (338.0, 872.5, 50.0), (338.0, 866.0, 61.0), 0.25, seg=5, mi=0)
    cyl(bm, (338.0, 866.0, 61.0), (338.0, 862.6, 59.5), 0.2, seg=5, mi=0)
    cyl(bm, (336.8, 870.0, 53.5), (339.2, 870.0, 53.5), 1.6, seg=16, mi=0)
    box(bm, (334.0, 871.0, 51.0), (1.4, 1.4, 1.6), mi=1)
    box(bm, (344.0, 871.5, 51.6), (4.0, 3.6, 3.2), mi=2)
    box(bm, (344.0, 871.5, 54.0), (4.4, 4.0, 1.6), mi=3, taper=(1.0, 0.1))
    cyl(bm, (338.0, 862.6, 59.5), (338.0, 862.6, -2.4), 0.05, seg=4, mi=1)
    _mk("TrostHoist_K", bm, [MT["timber_d"], MT["iron_t"], MT["f_tcream"], MT["roof_red_t"]], kc)
    bm = bmesh.new()
    box(bm, (0, 0, 0.15), (4.0, 4.0, 0.3), mi=0)
    for sx in (-1, 1):
        box(bm, (sx * 1.95, 0, 0.7), (0.1, 4.0, 0.1), mi=0); box(bm, (0, sx * 1.95, 0.7), (4.0, 0.1, 0.1), mi=0)
        for sy in (-1, 1):
            box(bm, (sx * 1.95, sy * 1.95, 0.5), (0.12, 0.12, 0.8), mi=0)
            cyl(bm, (sx * 1.95, sy * 1.95, 0.8), (0, 0, 4.5), 0.04, seg=4, mi=1)
    _mk_at("TrostBasket_K", bm, [MT["plank_t"], MT["iron_t"]], (342.0, 861.0, -3.6), kc)
    return kc

def set_basket(frac):
    """Basin hoist basket: 0 on the floor (Z -3.6), 1 at the Rose top (Z 50)."""
    o = bpy.data.objects.get("TrostBasket_K")
    if o:
        o.location.z = -3.6 + 53.6 * max(0.0, min(1.0, frac))

# ====================================================================================== block 9: north of Rose + RC
def build_north(MT):
    """Square A (paved forecourt via the floor shader) with the obelisk fountain; Rose north-face hoists X -60/-20/+20;
    Pyxis's timber railing post at (-20, 866, 50).  Nothing else is built outside the walls (owner)."""
    nc = _coll("TrostNorth")
    bm = bmesh.new()
    cx, cy = -20.0, 935.0
    cyl(bm, (cx, cy, 0.0), (cx, cy, 0.8), 6.0, seg=24, mi=0)
    cyl(bm, (cx, cy, 0.8), (cx, cy, 0.85), 5.4, seg=24, mi=1)
    box(bm, (cx, cy, 1.4), (1.6, 1.6, 1.4), mi=0)
    box(bm, (cx, cy, 6.6), (1.1, 1.1, 9.0), mi=0, taper=(0.55, 0.55))
    box(bm, (cx, cy, 11.4), (0.7, 0.7, 0.8), mi=0, taper=(0.05, 0.05))
    for k in range(int(60 / 1.5)):                                     # Pyxis's railing on the wall top
        x = -45.0 + k * 1.5
        box(bm, (x, 866.4 - 0.0, 50.6), (0.12, 0.12, 1.2), mi=2)
    box(bm, (-15.0, 866.4, 51.15), (60.0, 0.12, 0.12), mi=2)
    for X in ANCHORS_M["ROSE_HOISTS_X"]:                              # north-face hoists: truss + cage + derrick
        for sx in (-2.2, 2.2):
            for yy in (875.6, 880.0):
                box(bm, (X + sx, yy, 25.0), (0.4, 0.4, 50.0), mi=2)
        for z in range(4, 51, 6):
            box(bm, (X, 880.0, z), (4.8, 0.3, 0.3), mi=2)
            cyl(bm, (X - 2.2, 880.0, z), (X + 2.2, 880.0, z + 6.0), 0.1, seg=4, mi=2)
        box(bm, (X, 877.8, 3.0), (4.0, 4.0, 0.3), mi=2)
        cyl(bm, (X + 2.0, 872.0, 50.0), (X + 2.0, 878.0, 58.0), 0.22, seg=5, mi=2)
    _mk("TrostNorthSquare", bm, [MT["cornice"], MT["water_c"], MT["timber_d"]], nc)
    return nc

def build_relief_complex(MT):
    """845 relief complex RC (-268, 805) as part of the 850 town: cloister ranges (2 storeys, arcades) round an 80 x 45
    courtyard, 3-storey east hall, NE tower ~40 m (cream, pyramid roof) at (-213, 845), NW belfry 15 m, olive sandstone,
    maroon roofs."""
    rnd = random.Random(161)
    rc = _coll("TrostRC")
    olive = MT.setdefault("rc_stone", stone_mat("RCOlive", "#9a8f74", block=(1.2, 0.6)))
    maroon = MT.setdefault("rc_roof", roof_mat("RCMaroon", ["#6b4636", "#5e3e30"]))
    bm = bmesh.new()
    def rng(x0, x1, y0, y1, H, axis):
        box(bm, ((x0 + x1) / 2, (y0 + y1) / 2, (H - 3) / 2), (x1 - x0, y1 - y0, H + 3), mi=0)
        if axis == "x":
            d = y1 - y0
            p = [bm.verts.new(c) for c in ((x0, y0 - 0.4, H), (x1, y0 - 0.4, H), (x1, y1 + 0.4, H), (x0, y1 + 0.4, H), (x0, (y0 + y1) / 2, H + d * 0.5), (x1, (y0 + y1) / 2, H + d * 0.5))]
            for fv, mi in (((p[0], p[1], p[5], p[4]), 1), ((p[3], p[4], p[5], p[2]), 1), ((p[0], p[4], p[3]), 0), ((p[1], p[2], p[5]), 0)):
                bm.faces.new(fv).material_index = mi
        else:
            d = x1 - x0
            p = [bm.verts.new(c) for c in ((x0 - 0.4, y0, H), (x1 + 0.4, y0, H), (x1 + 0.4, y1, H), (x0 - 0.4, y1, H), ((x0 + x1) / 2, y0, H + d * 0.5), ((x0 + x1) / 2, y1, H + d * 0.5))]
            for fv, mi in (((p[0], p[4], p[5], p[3]), 1), ((p[1], p[2], p[5], p[4]), 1), ((p[0], p[1], p[4]), 0), ((p[2], p[3], p[5]), 0)):
                bm.faces.new(fv).material_index = mi
    rng(-320.0, -228.0, 770.5, 782.5, 7.6, "x")
    rng(-320.0, -228.0, 827.5, 839.5, 7.6, "x")
    rng(-320.0, -308.0, 782.5, 827.5, 7.6, "y")
    rng(-228.0, -214.0, 770.5, 839.5, 11.0, "y")
    for k in range(18):                                                  # courtyard arcades
        x = -305.0 + k * 4.4
        for y, face in ((782.5, "n"), (827.5, "s")):
            _arched_win(bm, x, y, 0.0, 2.6, 3.6, face, 2)
    box(bm, (-213.0, 845.0, 18.0), (8.0, 8.0, 40.0), mi=3)                 # NE tower (~40 m), pyramid roof
    box(bm, (-213.0, 845.0, 38.4), (8.6, 8.6, 0.8), mi=3)
    box(bm, (-213.0, 845.0, 41.8), (8.4, 8.4, 6.0), mi=4, taper=(0.05, 0.05))
    for face in range(4):
        a = face * math.pi / 2; c, s_ = math.cos(a), math.sin(a)
        _arched_win(bm, -213.0 + c * 4.0, 845.0 + s_ * 4.0, 31.0, 2.0, 4.6, "e" if c > 0.5 else "w" if c < -0.5 else "n" if s_ > 0.5 else "s", 2)
    box(bm, (-316.0, 836.0, 6.5), (5.0, 5.0, 17.0), mi=0)                 # NW belfry 15 m
    box(bm, (-316.0, 836.0, 16.2), (5.4, 5.4, 3.0), mi=1, taper=(0.05, 0.05))
    cyl(bm, (-268.0, 805.0, 0.0), (-268.0, 805.0, 2.6), 1.6, seg=12, mi=0)   # well kiosk
    box(bm, (-268.0, 805.0, 3.2), (4.0, 4.0, 1.2), mi=1, taper=(0.1, 0.1))
    _mk("TrostReliefComplex", bm, [olive, maroon, MT["window_t"], MT["tower_cream"], MT["roof_red_t"]], rc)
    return rc

def build_plaza_c(MT):
    """Central plaza C (-60, 470) r 45: pale paving (floor shader), a covered well off-centre (the pyre site at the
    centre stays free), a few market stalls with canvas roofs at the edge.  No monument, no fountain disc."""
    rnd = random.Random(171)
    cc = _coll("TrostPlazaC")
    canvas = MT.setdefault("canvas", flat_mat("TrostCanvas", "#cbbf9e", 0.9, 0.1, 0.5))
    bm = bmesh.new()
    wx, wy = -44.0, 482.0
    cyl(bm, (wx, wy, 0.0), (wx, wy, 1.0), 1.6, seg=14, mi=0)
    for sx in (-1, 1):
        box(bm, (wx + sx * 1.4, wy, 1.9), (0.25, 0.25, 3.0), mi=1)
    p = [bm.verts.new(c) for c in ((wx - 2.0, wy - 1.6, 3.2), (wx + 2.0, wy - 1.6, 3.2), (wx + 2.0, wy + 1.6, 3.2), (wx - 2.0, wy + 1.6, 3.2), (wx - 2.0, wy, 4.4), (wx + 2.0, wy, 4.4))]
    for fv in ((p[0], p[1], p[5], p[4]), (p[3], p[4], p[5], p[2])):
        bm.faces.new(fv).material_index = 2
    for k in range(9):
        a = math.radians(20 + k * 32 + rnd.uniform(-5, 5)); r = 39.0
        x, y = -60.0 + r * math.cos(a), 470.0 + r * math.sin(a)
        t = Vector((-math.sin(a), math.cos(a))); n = Vector((math.cos(a), math.sin(a)))
        for e in (-1, 1):
            for s_ in (-1, 1):
                q = Vector((x, y)) + t * (e * 1.8) + n * (s_ * 1.2)
                box(bm, (q.x, q.y, 1.2), (0.15, 0.15, 2.4), mi=1)
        obox(bm, Vector((x, y)), t, n, 3.6, 1.0, 0.0, 0.9, 1)
        hexa(bm, [(*(Vector((x, y)) + t * -2.0 + n * -1.5), 2.2), (*(Vector((x, y)) + t * 2.0 + n * -1.5), 2.2),
                  (*(Vector((x, y)) + t * 2.0 + n * 1.5), 2.8), (*(Vector((x, y)) + t * -2.0 + n * 1.5), 2.8),
                  (*(Vector((x, y)) + t * -2.0 + n * -1.5), 2.3), (*(Vector((x, y)) + t * 2.0 + n * -1.5), 2.3),
                  (*(Vector((x, y)) + t * 2.0 + n * 1.5), 2.9), (*(Vector((x, y)) + t * -2.0 + n * 1.5), 2.9)], 3)
    _mk("TrostPlazaC", bm, [MT["cornice"], MT["timber_d"], MT["roof_red_t"], canvas], cc)
    return cc

def build_yard_trees(MT):
    """Small trees in yards / courtyards (about 3 % of the cover); placed in free 2 m cells after the town layout."""
    rnd = random.Random(181)
    tc = _coll("TrostYardTreeVariants")
    for i in range(6):
        me = L.tree_mesh(f"TYT{i}", "broad", MT, i + 3)
        ob = bpy.data.objects.new(f"TYT{i}", me); tc.objects.link(ob); ob.location = (0, 0, -6000)
    recs = []
    tries = 0
    while len(recs) < 170 and tries < 20000:
        tries += 1
        X, Y = rnd.uniform(-460, 460), rnd.uniform(20, 860)
        if _mask_bad(X, Y) or _mask_bad(X + 3, Y) or _mask_bad(X - 3, Y) or _mask_bad(X, Y + 3) or _mask_bad(X, Y - 3):
            continue
        if not _occ_free(_obb(X, Y, 5.0, 5.0, 0.0)):
            continue
        s_ = rnd.uniform(0.7, 1.1)
        recs.append((X, Y + DY, ground_z_m(X, Y), rnd.uniform(0, 6.28), s_, s_, s_, rnd.randrange(6)))
    _instances("TrostYardTrees", tc, recs)
    return len(recs)

def build_mopup(MT):
    """g8 day-2 props, hidden until set_mopup(True): 2 captured-titan timber frames (CT anchors) with 14 diagonal poles,
    6-8 grey crane pylons with gear wheels on the wall tops at D, pyres (6 x 4 x 2 m log stacks) at the PYR anchors."""
    rnd = random.Random(191)
    mc = _coll("TrostMopup")
    pylon = MT.setdefault("pylon", flat_mat("TrostPylon", "#7d7f80", 0.7, 0.05))
    logs = MT.setdefault("logs", flat_mat("TrostLogs", "#5a4030", 0.9, 0.12, 1.0))
    bm = bmesh.new()
    for (x, y), (w, d, h) in zip(ANCHORS_M["CT"], ((12.0, 8.0, 10.0), (8.0, 6.0, 7.0))):
        for sx in (-1, 1):
            for sy in (-1, 1):
                box(bm, (x + sx * w / 2, y + sy * d / 2, h / 2), (0.4, 0.4, h), mi=0)
        for sy in (-1, 1):
            box(bm, (x, y + sy * d / 2, h), (w + 0.4, 0.4, 0.4), mi=0)
        for sx in (-1, 1):
            box(bm, (x + sx * w / 2, y, h), (0.4, d + 0.4, 0.4), mi=0)
        for k in range(14):
            a = rnd.uniform(0, math.tau); r0 = rnd.uniform(w * 0.6, w * 0.9)
            p0 = (x + math.cos(a) * r0, y + math.sin(a) * r0 * d / w, 0.0)
            p1 = (x + math.cos(a) * 1.0, y + math.sin(a) * 0.8, rnd.uniform(h * 0.4, h * 0.9))
            cyl(bm, p0, p1, 0.13, seg=4, mi=0)
    _mk("TrostCapturedFrames", bm, [MT["timber_d"]], mc)
    bm = bmesh.new()
    for k in range(7):                                                 # crane pylons at D (Rose top + west wall top)
        if k < 4:
            X, Y = -470.0 + k * 34.0, 868.5
        else:
            X, Y = -478.5, 840.0 - (k - 4) * 34.0
        box(bm, (X, Y, 50.0 + 7.0), (0.9, 0.9, 14.0), mi=0)
        cyl(bm, (X, Y, 64.0), (X + (6.0 if k < 4 else 0.0), Y - (6.0 if k < 4 else 0.0) + (0 if k < 4 else 0), 61.0), 0.25, seg=5, mi=0)
        cyl(bm, (X - 0.3, Y, 52.5), (X + 0.3, Y, 52.5), 1.2, seg=12, mi=1)
    _mk("TrostCranesD", bm, [pylon, MT["timber_d"]], mc)
    bm = bmesh.new()
    for k, (x, y) in enumerate(ANCHORS_M["PYR"]):
        for layer in range(5):
            ang = 0.0 if layer % 2 == 0 else math.pi / 2
            n = 9 if layer % 2 == 0 else 6
            ln = 6.0 if layer % 2 == 0 else 4.0
            for j in range(n):
                off = (j - (n - 1) / 2) * (4.0 / n if layer % 2 == 0 else 6.0 / n)
                c = Vector((x, y)) + Vector((-math.sin(ang), math.cos(ang))) * off
                d = Vector((math.cos(ang), math.sin(ang))) * ln / 2
                cyl(bm, (c.x - d.x, c.y - d.y, 0.2 + layer * 0.4), (c.x + d.x, c.y + d.y, 0.2 + layer * 0.4), 0.2, seg=5, mi=0)
    _mk("TrostPyres", bm, [logs], mc)
    for o in mc.objects:
        _hide(o, True)
    return mc

def set_mopup(on=True, pyres=None):
    """Show the day-2 props (captured frames, D cranes) and the pyres (pyres=None follows `on`)."""
    _hide(bpy.data.objects.get("TrostCapturedFrames"), not on)
    _hide(bpy.data.objects.get("TrostCranesD"), not on)
    _hide(bpy.data.objects.get("TrostPyres"), not (on if pyres is None else pyres))

EXTRA_BUILDERS += [("inner_gate", build_inner_gate), ("alley_q2", build_alley_q2), ("hq", build_hq), ("basin", build_basin),
                   ("north", build_north), ("relief", build_relief_complex), ("plaza_c", build_plaza_c), ("mopup", build_mopup)]
POST_TOWN_BUILDERS = [("yard_trees", build_yard_trees)]

# ====================================================================================== stills runner (2nd -P script)
STILL_CAMS = {   # name: (loc M, look M, lens, state)
    "v3_overview": ((-760, -260, 520), (40, 430, 0), 28, {}),
    "v3_gate_square": ((-85, 165, 120), (0, 30, 6), 32, {}),
    "v3_gate_breach": ((-60, 135, 95), (0, 15, 12), 34, {"breach": True}),
    "v3_seal": ((-75, 150, 90), (3, 14, 12), 40, {"breach": True, "seal": True}),
    "v3_court": ((150, 380, 150), (285, 262, 6), 34, {}),
    "v3_strip": ((40, 230, 100), (180, 62, 12), 38, {}),
    "v3_inner_gate": ((-60, 690, 120), (-140, 840, 12), 32, {"cart": True}),
    "v3_hq": ((-345, 455, 175), (-200, 640, 15), 30, {}),
    "v3_basin": ((283, 740, 96), (361, 850, 4), 38, {}),
    "v3_town_av": ((-40, 330, 170), (0, 0, 30), 32, {}),
    "v3_hq_cut": ((-198, 565, 100), (-187, 643, 1), 38, {"cutaway": True, "lift": 0.5}),
    "v3_walltop": ((10, -2, 64), (-30, 520, 0), 30, {}),
    "dbg_gs_top": ((0, 30, 260), (0, 30.5, 0), 30, {"breach": True}),
    "dbg_breach_front": ((0, 75, 16), (0, 10, 16), 35, {"breach": True}),
    "dbg_ball": ((255, 228, 30), (290, 262, 6), 40, {}),
    "dbg_plan": ((0, 435, 1500), (0, 435.5, 0), 32, {}),
}
CAMS = {k: (M(*v[0]), M(*v[1]), v[2]) for k, v in STILL_CAMS.items()}     # scene.py camera presets (set coords)
CAMS["trost_overview"] = CAMS["v3_overview"]

def _stills_main():
    import argparse
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser(allow_abbrev=False)
    ap.add_argument("--stills", default="")
    ap.add_argument("--cams", default=",".join(STILL_CAMS))
    a, _ = ap.parse_known_args(argv)
    if not a.stills:
        return
    os.makedirs(a.stills, exist_ok=True)
    sc = bpy.context.scene; cam = sc.camera
    cam.data.clip_start = 0.5; cam.data.clip_end = 20000
    if sc.render.engine.startswith("BLENDER_EEVEE"):
        ev = sc.eevee
        for k_, v_ in (("taa_render_samples", 8), ("use_shadows", True), ("shadow_resolution_scale", 1.0),
                       ("use_raytracing", False), ("use_fast_gi", True), ("fast_gi_method", "AMBIENT_OCCLUSION_ONLY"),
                       ("fast_gi_distance", 6.0)):
            try:
                setattr(ev, k_, v_)
            except Exception:
                pass
        try:
            import toon; toon.apply()
        except Exception as ex:
            print("[trost] toon apply failed", ex)
    for name in a.cams.split(","):
        loc, tgt, lens, st = STILL_CAMS[name]
        cam.location = M(*loc); cam.data.lens = lens
        cam.rotation_euler = (Vector(M(*tgt)) - Vector(M(*loc))).to_track_quat("-Z", "Y").to_euler()
        set_breach(st.get("breach", False)); set_seal(st.get("seal", False), 1.0 if st.get("seal") else 0.0)
        set_glow(1.0 if st.get("breach") and not st.get("seal") else 0.0)
        set_wagon(st.get("cart", False)); set_hq_cutaway(st.get("cutaway", False)); set_hq_lift(st.get("lift", 0.0))
        sc.render.filepath = os.path.join(a.stills, name + ".png")
        t = time.time()
        bpy.ops.render.render(write_still=True)
        print(f"[trost] still {name}: {time.time() - t:.1f} s", flush=True)

if __name__ == "__main__":
    import trost as _T
    _T._stills_main()
