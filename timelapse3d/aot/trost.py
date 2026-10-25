"""TROST DISTRICT set (AoT S1 E3-E13) for the EP1 3D timelapse: a reusable scene plug-in.

Run (stills):  bash render_trost_set.sh            (see that script)
Use in a shot: AOT_SET=trost blender -b -P aot/scene.py -P <your_render.py> -- --cam trost_overview ...
               (AOT_PLUGINS=<your modules> may be combined; they are imported AFTER trost, so they already see the
               Trost geometry through aotlib: L.OUTER_GATE, L.PLAZA, L.on_road, L.in_district, L.street_network ...)

How it hooks in: scene.py imports the module named by $AOT_SET first (before $AOT_PLUGINS). At import this module
rebinds scene.py's district globals (W, S, R, CX, CANAL_FAR, OUTER_GATE, PLAZA, on_road, street_network) to Trost's.
scene.build() then sees build_set() and calls it instead of building Shiganshina. build_set() builds terrain, walls,
town, landmarks, light and finally calls every other plug-in's build(M, year, ctx) as scene.build() would.

Layout (metres, +x east, +y north). Same frame as Shiganshina: the main wall (here WALL ROSE) runs along y = 0,
Rose's interior is y > 0, the district bulges south (y < 0): straight sides x = +-W from y = 0 to y = -S, closed by a
half circle of radius R around (0, -S). design_bible.md 5.4: D/U bulge ~1.2 km wide, ~0.9 km deep; inner gate in
Rose, NW of centre; outer gate at the tip; canal N-S along the EAST side, out through the SE wall; church tower NW
of centre; supply HQ mid-district ~380 m in from the north wall; the boulder in an open square on the straight main
avenue NNW of the outer gate.

API (module `trost`; read the constants after import, call the functions after build):
  W, S, R                 620, 250, 620  (district half width, straight side length, round-end radius)
  INNER_GATE  (-140, 0)   gate in Wall Rose, an OPEN passage (no door); the crowd jams behind the cargo wagon; Pixis above
  OUTER_GATE  (0, -870)   gate at the tip, kicked in by the Colossal; Eren seals it with the boulder
  WATER_GATE_ROSE (556, 0), WATER_GATE_OUTER (556, ~-524); CANAL_X = 556, CANAL_W = 24
  PLAZA       (-100, -250, 42)   market square (x, y, radius) on the avenue; the bell tower stands on its west side
  BELL_TOWER  dict(xy=(-160, -250), belfry_z=(34, 43), belfry_c=(-160, -250, 38.5), top_z=64)  open octagonal belfry
  SUPPLY_HQ   dict(center, rot=0, size=(70, 30), store_z=(0, 10), roof_z=22, lift_xy, lift_z=(0.3, 10), titan_spots[7],
                   door_xy, roof_xy, keep_xy, keep_size=(30, 30, 24), keep_top_z=49, warehouse_roof_z=(26, 41), tower_xy)
              the anime complex: a crenellated sandstone KEEP (corner turrets, slate-blue pyramid roofs, arched windows,
              taller central block, clock/bell turret; object TrostHQ_Keep) joined to a 5-storey WAREHOUSE wing with a
              steep slate gable roof (center/size above = the warehouse).  Its ground floor is the storeroom (TrostHQ:
              beams, crates, gas racks, lift frame; TrostHQ_Lift platform); TrostHQ_Upper = upper storeys + slabs + roof
  CANNON_BASIN dict(center, floor=(x0, x1, y0, y1), floor_z, top_z=6, west_wall_x, wall_h=10, steps_n / steps_s = rows
              (bottom -> top) of (x, y, z) standing spots on the stepped banks, landing (raised block in the south
              flight, the salute), trio (Eren/Mikasa/Armin spot on the floor), cannon + cannon_aim (north terrace),
              terrace_n / terrace_s (x0, x1, y0, y1, z), quay, boat).  A sunken stone dock beside the canal (refs
              trost_cannon_canal / trost_armin_salute_steps); object TrostCannonBasin, TrostBoat
  ground_z(x, y) includes the basin terraces / steps (basin_z); walkable() includes the basin
  BOULDER     (-68, -450, 0)     bottom centre of the boulder; BOULDER_SIZE (15.2, 15.2, 14.5), near-sphere; object "TrostBoulder"; boulder_mesh(origin="center") for carry
  BOULDER_SQUARE (-68, -450, 40); BOULDER_ROUTE  polyline boulder -> avenue -> outer gate (Eren's carry)
  AVENUE      polyline outer gate -> inner gate (straight main street, hw 8); EVAC_ROUTE plaza -> inner gate
  INNER_GATE_SQUARE (x0, y0, x1, y1); OUTER_GATE_SQUARE (x, y, r)
  WALL_LIFTS  list of dict(name, xy, out=(nx, ny), platform=<object name>) timber-truss lifts on the wall faces
  WALLTOP_SPEECH (-140, -2, 50)  wall top above the inner gate
  street_polylines() -> [(pts, half_width)]   every street as a list of (x, y) (sampled ~6 m)
  on_road(x, y, pad=0) -> bool                streets, plaza, gate squares, boulder square (NOT the canal water)
  walkable(x, y) -> bool                      on_road inside the district + both gate passages + fields outside them
  in_district(x, y, margin) -> bool;  in_canal(x, y) -> bool;  nearest_road(x, y) -> (x, y)
  ground_z(x, y) -> terrain height (0 in town)
  set_hq_cutaway(on)        hide/show the HQ roof, upper storeys and floor slabs (sky view into the storeroom)
  set_hq_lift(frac)         0 = platform up at the 1st floor (z 10), 1 = down on the storeroom floor
  set_wagon(on)             Dimo Reeves' cargo wagon jammed in the inner gate (hidden by default)
  set_breach(on)            after the kick: OuterGate + door -> OuterGateBroken (15.6 x 15 m opening) + OuterGateRubble
  set_lift(i, frac)         wall lift i platform height, 0 = ground, 1 = wall top
Object names kept from Shiganshina so fx code can find them: OuterGate, OuterGate_Door, InnerGate (no InnerGate_Door).
World layer: agent G's world.py (AOT_PLUGINS=...,world) places this frame at world (0, 5000), keeps the set's terrain
inside the core circle (0, -435) r 1150 and trims Wall Rose beyond |x| 1000.  trost.py builds no buildings outside
the district.
Collections: TrostHQ_Upper (cutaway set), TrostGarrison (cannons, ammo), TrostLifts.
CAMS: trost_overview, trost_outer_gate, trost_boulder, trost_hq, trost_hq_cut, trost_hq_complex, trost_belltower,
      trost_inner_gate, trost_basin.
"""
import bpy, bmesh, math, random, os, sys, time
from mathutils import Vector, Euler, noise

import aotlib as L

SET_NAME = "trost"
REPLACES = {"hill", "kids", "titans"}

# ---------------------------------------------------------------- layout constants
W, S, R = 620.0, 250.0, 620.0
INNER_GATE = (-140.0, 0.0)
OUTER_GATE = (0.0, -S - R)
CANAL_X, CANAL_W = 556.0, L.CANAL_W

def district_ymin(x, margin=0.0):
    r = R - margin
    return -S - math.sqrt(max(0.0, r * r - x * x))

def in_district(x, y, margin):
    if y > -margin or abs(x) > W - margin:
        return False
    if y < -S and math.hypot(x, y + S) > R - margin:
        return False
    return True

WATER_GATE_ROSE = (CANAL_X, 0.0)
WATER_GATE_OUTER = (CANAL_X, district_ymin(CANAL_X))
PLAZA = (-100.0, -250.0, 42.0)
BOULDER = (-68.0, -450.0, 0.0)
BOULDER_SIZE = (15.2, 15.2, 14.5)     # a near-perfect grey sphere ~15 m across (ep 12-13; TA_BOULDER_R 7.6)
BOULDER_SQUARE = (-68.0, -450.0, 44.0)
INNER_GATE_SQUARE = (INNER_GATE[0] - 60, -70.0, INNER_GATE[0] + 60, -12.0)
OUTER_GATE_SQUARE = (0.0, OUTER_GATE[1] + 38, 38.0)
WALLTOP_SPEECH = (INNER_GATE[0], -2.0, L.WALL_H)

def _avenue_x(y):
    """Straight main avenue from the outer gate (0, -870) to the inner gate (-140, 0)."""
    return INNER_GATE[0] * (y - OUTER_GATE[1]) / (0 - OUTER_GATE[1])

AVENUE = [(_avenue_x(y), float(y)) for y in range(int(OUTER_GATE[1]) + 6, -5, 6)]
BOULDER_ROUTE = [(BOULDER[0], BOULDER[1])] + [(_avenue_x(y), float(y)) for y in range(int(BOULDER[1]) - 30, int(OUTER_GATE[1]) + 3, -30)] \
    + [(0.0, OUTER_GATE[1] + 4)]
EVAC_ROUTE = [(_avenue_x(y), float(y)) for y in range(int(PLAZA[1]), -11, 10)] + [(INNER_GATE[0], -6.0)]

# supply HQ: mid-district, axis-aligned, main door facing south
_HQ_C = (240.0, -380.0)
_HQ_ROT = 0.0          # axis-aligned (long side E-W, door south) so trost_action's (w, d) box matches the building
HQ_L, HQ_D = 70.0, 30.0             # warehouse wing (storeroom + lift); the keep joins its west end
HQ_KEEP = 30.0
HQ_KEEP_X = -HQ_L / 2 - HQ_KEEP / 2   # keep centre in HQ-local x
def hq_world(lx, ly):
    c, s = math.cos(_HQ_ROT), math.sin(_HQ_ROT)
    return (_HQ_C[0] + lx * c - ly * s, _HQ_C[1] + lx * s + ly * c)
def hq_local(x, y):
    c, s = math.cos(_HQ_ROT), math.sin(_HQ_ROT)
    dx, dy = x - _HQ_C[0], y - _HQ_C[1]
    return (dx * c + dy * s, -dx * s + dy * c)
_TITAN_LOCAL = [(-17, -7), (-15, 7), (-8, -9), (8, 9), (15, -7), (17, 6), (-3, 9)]   # clear of lift and racks
SUPPLY_HQ = dict(center=_HQ_C, rot=_HQ_ROT, size=(HQ_L, HQ_D), store_z=(0.0, 10.0), roof_z=22.0,
                 lift_xy=_HQ_C, lift_z=(0.3, 10.0), titan_spots=[hq_world(*p) for p in _TITAN_LOCAL],
                 door_xy=hq_world(0, -HQ_D / 2 - 2), roof_xy=_HQ_C, tower_xy=hq_world(HQ_KEEP_X + 2, 0),
                 keep_xy=hq_world(HQ_KEEP_X, 0), keep_size=(HQ_KEEP, HQ_KEEP, 24.0), keep_top_z=49.0, warehouse_roof_z=(26.0, 41.0))

_CH_C = (-185.0, -250.0)                 # church centre (nave along x, tower at the east end facing the plaza)
BELL_TOWER = dict(xy=(_CH_C[0] + 25, _CH_C[1]), belfry_z=(34.0, 43.0), belfry_c=(_CH_C[0] + 25, _CH_C[1], 38.5), top_z=64.0)

_LIFT_SPECS = [("RoseW", (-380.0, 0.0), (0, -1)), ("RoseC", (-40.0, 0.0), (0, -1)), ("RoseE", (260.0, 0.0), (0, -1))]
for _nm, _ang in (("ArcSW", 215.0), ("ArcSE", 322.0)):
    _a = math.radians(_ang)
    _LIFT_SPECS.append((_nm, (math.cos(_a) * R, -S + math.sin(_a) * R), (-math.cos(_a), -math.sin(_a))))
_LIFT_SPECS += [("SideW", (-W, -140.0), (1, 0)), ("SideE", (W, -140.0), (-1, 0))]
WALL_LIFTS = [dict(name=n, xy=p, out=o, platform=f"TrostLift_{n}_Platform") for n, p, o in _LIFT_SPECS]

# zones where streets are cut and no houses stand: (kind, params)
def _in_hq(x, y, pad):
    lx, ly = hq_local(x, y)
    return HQ_KEEP_X - HQ_KEEP / 2 - 6 - pad < lx < HQ_L / 2 + 3 + pad and abs(ly) < HQ_KEEP / 2 + 5 + pad

# ---------------- the cannon basin (refs trost_cannon_canal / trost_armin_salute_steps): a sunken stone dock beside the
# canal, dry floor at street level framed by 6 m stone terraces: stepped banks on the north and south sides (soldiers
# stand on the steps; a raised stone landing in the middle of the south flight), a tall buttressed retaining wall on the
# west, the east side open to the canal with a quay and a boat.
_BX0, _BX1, _BY0, _BY1 = 494.0, 543.0, -225.0, -175.0          # basin floor
_BTOP, _BSTEP_N, _BSTEP_H, _BSTEP_D = 6.0, 8, 0.75, 1.5
def _step_rows(side):
    rows = []
    for k in range(_BSTEP_N):
        yy = (_BY1 + (k + 0.5) * _BSTEP_D) if side > 0 else (_BY0 - (k + 0.5) * _BSTEP_D)
        rows.append([(float(x), yy, (k + 1) * _BSTEP_H) for x in range(int(_BX0) + 3, int(_BX1) - 2, 2)
                     if not (side < 0 and 512.0 < x < 522.0)])
    return rows
CANNON_BASIN = dict(center=((_BX0 + _BX1) / 2, (_BY0 + _BY1) / 2), floor=(_BX0, _BX1, _BY0, _BY1), floor_z=0.15,
                    top_z=_BTOP, west_wall_x=_BX0, wall_h=10.0,
                    steps_n=_step_rows(1), steps_s=_step_rows(-1),          # rows bottom -> top of (x, y, z) standing spots
                    landing=(517.0, _BY0 - 7.0, 4.64),                       # raised stone landing in the south flight
                    trio=(510.0, (_BY0 + _BY1) / 2, 0.15),                  # Eren / Mikasa / Armin on the basin floor
                    cannon=(522.0, _BY1 + _BSTEP_N * _BSTEP_D + 3.0, _BTOP), cannon_aim=(0.0, -1.0),
                    terrace_n=(_BX0 - 14, _BX1, _BY1 + _BSTEP_N * _BSTEP_D, _BY1 + _BSTEP_N * _BSTEP_D + 8, _BTOP),
                    terrace_s=(_BX0 - 14, _BX1, _BY0 - _BSTEP_N * _BSTEP_D - 8, _BY0 - _BSTEP_N * _BSTEP_D, _BTOP),
                    quay=(_BX1 - 1.0, (_BY0 + _BY1) / 2, 0.3), boat=(CANAL_X - 4.0, (_BY0 + _BY1) / 2 + 6.0, 0.13))
def _in_basin(x, y, pad):
    return _BX0 - 16 - pad < x < _BX1 + 2 + pad and _BY0 - _BSTEP_N * _BSTEP_D - 9 - pad < y < _BY1 + _BSTEP_N * _BSTEP_D + 9 + pad
def _in_church(x, y, pad):
    return _CH_C[0] - 30 - pad < x < _CH_C[0] + 32 + pad and abs(y - _CH_C[1]) < 10 + pad
def in_canal(x, y):
    """Canal water inside the district (between the two water gates)."""
    return abs(x - CANAL_X) < CANAL_W / 2 and WATER_GATE_OUTER[1] < y < 0

# ---------------------------------------------------------------- streets
_STREETS = None
def street_polylines():
    """All streets as [(pts, half_width)]: the avenue, ring roads following the wall (concentric arcs at the round end),
    radials from the round end's centre, E-W streets in the straight part, the wall road along Rose and canal quays."""
    global _STREETS
    if _STREETS is not None:
        return _STREETS
    raw = [(AVENUE, 8.0)]
    for d, hw in ((18, 5.0), (110, 4.5), (210, 4.5), (310, 5.0), (410, 4.5), (510, 4.0)):
        r = R - d
        pts = [(-(W - d), float(y)) for y in range(-20, int(-S), -6)]
        n = int(math.pi * r / 6)
        pts += [(math.cos(math.pi + k / n * math.pi) * r, -S + math.sin(math.pi + k / n * math.pi) * r) for k in range(n + 1)]
        pts += [((W - d), float(y)) for y in range(int(-S), -19, 6)]
        raw.append((pts, hw))
    for k in range(1, 8):
        a = math.pi + k * math.pi / 8
        raw.append(([(math.cos(a) * r, -S + math.sin(a) * r) for r in range(110, int(R) - 20, 6)], 3.8))
    for y0, hw in ((-20, 5.0), (-90, 4.0), (-170, 4.0), (-250, 4.5)):
        raw.append(([(float(x), y0 + noise.noise(Vector((x / 160, y0 / 40, 3))) * (0 if y0 == -20 else 4)) for x in range(int(-W + 20), int(W - 19), 6)], hw))
    for side in (-1, 1):                                              # canal quays
        xq = CANAL_X + side * (CANAL_W / 2 + 5)
        raw.append(([(xq, float(y)) for y in range(-20, int(district_ymin(xq, 20)), -6)], 3.0))
    out = []
    for pts, hw in raw:
        cur = []
        for x, y in pts:
            bad = (not in_district(x, y, 4)) and pts is not AVENUE
            bad = bad or _in_hq(x, y, hw) or _in_church(x, y, hw) or _in_basin(x, y, hw)
            if bad:
                if len(cur) > 2:
                    out.append((cur, hw))
                cur = []
            else:
                cur.append((x, y))
        if len(cur) > 2:
            out.append((cur, hw))
    _STREETS = out
    return out

_ROADS = None
def _road_index():
    global _ROADS
    if _ROADS is None:
        g = {}
        for pts, hw in street_polylines():
            for k in range(len(pts) - 1):
                ax, ay = pts[k]; bx, by = pts[k + 1]
                n = max(1, int(math.hypot(bx - ax, by - ay) / 2.5))
                for t in range(n + 1):
                    x, y = ax + (bx - ax) * t / n, ay + (by - ay) * t / n
                    g.setdefault((int(x // 20), int(y // 20)), []).append((x, y, hw))
        _ROADS = g
    return _ROADS

def on_road(x, y, pad=0.0):
    """True on any street, the plaza, the boulder square or the two gate squares (the canal water is not road)."""
    if INNER_GATE_SQUARE[0] - pad < x < INNER_GATE_SQUARE[2] + pad and INNER_GATE_SQUARE[1] - pad < y < INNER_GATE_SQUARE[3]:
        return True
    for cx, cy, r in (PLAZA, BOULDER_SQUARE, OUTER_GATE_SQUARE):
        if (x - cx) ** 2 + (y - cy) ** 2 < (r + pad) ** 2:
            return True
    g = _road_index()
    gx, gy = int(x // 20), int(y // 20)
    for i in (-1, 0, 1):
        for j in (-1, 0, 1):
            for px, py, hw in g.get((gx + i, gy + j), ()):
                if (px - x) ** 2 + (py - y) ** 2 < (hw + pad) ** 2:
                    return True
    return False

def nearest_road(x, y, search=3):
    """Nearest street sample point (x, y), searching +-search 20 m cells; falls back to the avenue."""
    g = _road_index(); best, bd = None, 1e18
    gx, gy = int(x // 20), int(y // 20)
    for i in range(-search, search + 1):
        for j in range(-search, search + 1):
            for px, py, hw in g.get((gx + i, gy + j), ()):
                d = (px - x) ** 2 + (py - y) ** 2
                if d < bd:
                    bd, best = d, (px, py)
    return best or min(AVENUE, key=lambda p: (p[0] - x) ** 2 + (p[1] - y) ** 2)

def walkable(x, y):
    """People nav test: district streets/squares plus the gate passages and the fields just beyond both gates."""
    ix = INNER_GATE[0]
    if abs(x - ix) < 6.0 and -14 <= y <= 12:                           # inner gate passage
        return True
    if 8 < y < 140 and abs(x - ix) < 16 + (y - 8) * 0.5:               # road/field north of the inner gate (Rose)
        return True
    oy = OUTER_GATE[1]
    if abs(x) < 6.0 and oy - 12 <= y <= oy + 12:                        # outer gate passage
        return True
    if oy - 160 < y < oy - 6 and abs(x) < 26 + (oy - 6 - y) * 0.6:      # outside the outer gate (Maria land)
        return True
    if _in_basin(x, y, 0) and x < _BX1 + 0.5:
        return True
    return in_district(x, y, 6.0) and on_road(x, y)

def ground_z(x, y):
    """Terrain height, plus the cannon basin's terraces and steps (the basin floor is at street level)."""
    h = L.height(x, y)
    if _in_basin(x, y, 0):
        h += basin_z(x, y)
    return h

def basin_z(x, y):
    """Height of the basin structures above the street at (x, y): steps, terraces, landing (0 on the floor)."""
    if x > _BX1 or x < _BX0 - 14:
        return 0.0
    if x < _BX0:
        return _BTOP + 4.0 if x > _BX0 - 3 else _BTOP
    if _BY0 <= y <= _BY1:
        return 0.0
    d = (y - _BY1) if y > _BY1 else (_BY0 - y)
    if y < _BY0 and 512.0 < x < 522.0 and d < 9.0:
        return 4.64
    return min(_BTOP, (int(d / _BSTEP_D) + 1) * _BSTEP_H) if d < _BSTEP_N * _BSTEP_D else _BTOP

# ---------------------------------------------------------------- rebind scene.py's district (import time)
def _install():
    L.W, L.S, L.R = W, S, R
    L.CX, L.CS = CANAL_X, 1
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

LABELS = {"TROST DISTRICT": (60, -480, 20), "WALL ROSE": (-1100, 0, 50), "INNER GATE": (INNER_GATE[0], 0, 50),
          "OUTER GATE": (OUTER_GATE[0], OUTER_GATE[1], 50), "SUPPLY HQ": (_HQ_C[0], _HQ_C[1], 30),
          "BELL TOWER": (BELL_TOWER["xy"][0], BELL_TOWER["xy"][1], 64), "BOULDER": (BOULDER[0], BOULDER[1], 12)}

_hq = SUPPLY_HQ
CAMS = {
    "trost_overview": ((-560, 520, 720), (80, -470, 0), 26),
    "trost_outer_gate": ((150, -610, 150), (0, OUTER_GATE[1], 20), 32),
    "trost_boulder": ((-22, -392, 46), (-66, -458, 5), 32),     # boulder square, avenue on to the outer gate
    "trost_hq": ((_HQ_C[0] - 150, _HQ_C[1] + 70, 120), (_HQ_C[0], _HQ_C[1], 6), 34),
    "trost_hq_cut": ((_HQ_C[0] - 70, _HQ_C[1] + 35, 120), (_HQ_C[0], _HQ_C[1], 0), 34),
    "trost_belltower": ((PLAZA[0] + 70, PLAZA[1] - 90, 80), (BELL_TOWER["xy"][0], BELL_TOWER["xy"][1], 30), 34),
    "trost_inner_gate": ((INNER_GATE[0] + 45, -120, 60), (INNER_GATE[0], 0, 12), 34),
    "trost_hq_complex": ((_HQ_C[0] + 60, _HQ_C[1] - 150, 95), (_HQ_C[0] - 25, _HQ_C[1], 18), 32),
    "trost_basin": ((518.0 - 70, -200.0 - 55, 60), (518.0, -200.0, 2), 34),
}

# ---------------------------------------------------------------- small mesh helpers
def _gable(bm, cx, cy, l, w, z0, h, mi, rot=0.0, over=0.6):
    """Gabled roof along local x (length l, width w) at eave z0, ridge h above."""
    q = Euler((0, 0, rot)).to_matrix()
    def v(x, y, z):
        p = q @ Vector((x, y, 0)); return bm.verts.new((cx + p.x, cy + p.y, z))
    a, b = l / 2 + over, w / 2 + over
    p = [v(-a, -b, z0), v(a, -b, z0), v(a, b, z0), v(-a, b, z0), v(-a, 0, z0 + h), v(a, 0, z0 + h)]
    for fv in [(p[0], p[1], p[5], p[4]), (p[3], p[4], p[5], p[2]), (p[0], p[4], p[3]), (p[1], p[2], p[5]), (p[0], p[3], p[2], p[1])]:
        bm.faces.new(fv).material_index = mi

def _to_world(ob, center, rot):
    ob.location = (center[0], center[1], 0); ob.rotation_euler.z = rot
    return ob

# ---------------------------------------------------------------- walls
def build_walls(M):
    WALL_H, WALL_T = L.WALL_H, L.WALL_T
    rose = [(i * 20.0, -(i * 20.0) ** 2 / (2 * 380000.0) * 30) for i in range(-450, 451)]
    rose = [(x, 0.0) if abs(x) <= W + 1 else (x, y + (W ** 2) / (2 * 380000.0) * 30) for x, y in rose]
    r_gaps = [(INNER_GATE[0], 0.0, L.GATE_W / 2 + 0.5), (CANAL_X, 0.0, CANAL_W / 2 + 0.5)]
    for gx, gy, hw in r_gaps:
        rose += [(gx - hw + 0.4, 0.0), (gx - hw * 0.5, 0.0), (gx, 0.0), (gx + hw * 0.5, 0.0), (gx + hw - 0.4, 0.0)]
    rose = sorted(set(rose))
    L.wall_ring("WallRose", rose, M, gaps=r_gaps)
    dist = L.district_outline(6.0)
    d_gaps = [(OUTER_GATE[0], OUTER_GATE[1], L.GATE_W / 2 + 0.5), (WATER_GATE_OUTER[0], WATER_GATE_OUTER[1], CANAL_W / 2 + 0.5)]
    L.wall_ring("WallTrost", dist, M, gaps=d_gaps)
    L.buttresses("ButtressRose", [p for p in rose if abs(p[0]) < 4200], r_gaps, M)
    L.buttresses("ButtressTrost", dist, d_gaps, M, every=18.0)
    rose_top = [p for p in rose if abs(p[0]) < 2600]
    L.wall_top("WallTopRose", rose_top, r_gaps, M)
    L.wall_top("WallTopTrost", dist, d_gaps, M)
    L.gatehouse("InnerGate", INNER_GATE, 0, M, door=False)   # open passage for the evacuation (HANDOFF 09:37)
    L.gatehouse("OuterGate", OUTER_GATE, 0, M, deep=8.0)
    # the BREACH (hidden until the kick, set_breach(True)): a broken ~15.6 m wide x 15 m high opening that the
    # 15.2 m boulder plugs flush, with jagged broken blocks around its edge and rubble at its foot
    br = L.gatehouse("OuterGateBroken", OUTER_GATE, 0, M, w=15.6, h=15.0, door=False)
    bm = bmesh.new(); rnd = random.Random(4)
    for k in range(26):
        a = rnd.uniform(0.0, math.pi)
        r = rnd.uniform(7.6, 9.4)
        x, z = math.cos(a) * r, 7.5 + math.sin(a) * r * 0.95
        L.box(bm, (OUTER_GATE[0] + x, OUTER_GATE[1] + rnd.uniform(-4, 4), z), (rnd.uniform(1.0, 2.6),) * 3,
              rot=rnd.uniform(0, 3), taper=(rnd.uniform(0.6, 1.0), rnd.uniform(0.6, 1.0)))
    for k in range(40):
        x, y = rnd.uniform(-12, 12), OUTER_GATE[1] + rnd.uniform(-6, 14)
        sz = rnd.uniform(0.6, 2.4)
        L.box(bm, (OUTER_GATE[0] + x, y, sz * 0.35), (sz, sz * rnd.uniform(0.6, 1.2), sz * 0.7), rot=rnd.uniform(0, 3))
    rb = L.obj_from_bm("OuterGateRubble", bm, [M["stone"]])
    for o in (br, rb):
        o.hide_render = o.hide_viewport = True
    L.gatehouse("WaterGateRose", WATER_GATE_ROSE, 0, M, w=CANAL_W, h=11, door=False)
    a = math.atan2(WATER_GATE_OUTER[1] + S, WATER_GATE_OUTER[0])
    L.gatehouse("WaterGateOuter", WATER_GATE_OUTER, a + math.pi / 2, M, w=CANAL_W, h=11, door=False)
    # Garrison: dense guns on the district bulge (design bible 2.5), sparser on Rose; keep clear of lifts/guardhouses
    gc = L.new_coll("TrostGarrison")
    cm, bmsh = L.cannon_mesh(M), L.barrels_mesh(M)
    keep = [(l["xy"][0], l["xy"][1], 5.0) for l in WALL_LIFTS]
    gh = _guardhouses(M, dist, gc)
    keep += [(x, y, 6.0) for x, y in gh]
    L.place_on_wall(dist, d_gaps + keep, cm, 14, -2.15, gc, start=8, name="TrostCannon")
    L.place_on_wall(dist, d_gaps + keep, bmsh, 70, 1.6, gc, start=30, name="TrostAmmo")
    L.place_on_wall(rose_top, r_gaps + keep, cm, 40, -2.15, gc, start=10, face_out=True, name="RoseCannon")
    return dist, rose

def _guardhouses(M, dist, coll):
    """Small half-timbered guard/winch houses on the district wall top (design bible 2.4, Trost ep4)."""
    me = L.house_mesh("WallGuardhouse", 6.0, 7.0, 4.0, 3.2, M, "timber", "roof_orange", chimney=True)
    out = []
    total = sum(math.hypot(dist[k + 1][0] - dist[k][0], dist[k + 1][1] - dist[k][1]) for k in range(len(dist) - 1))
    targets = [total * f for f in (0.12, 0.3, 0.62, 0.86)]
    for i, (p, t, nrm, s) in enumerate(L.along(dist)):
        if targets and s >= targets[0]:
            targets.pop(0)
            o = bpy.data.objects.new(f"TrostGuardhouse{len(out)}", me)
            o.location = (p.x, p.y, L.WALL_H + 0.1); o.rotation_euler.z = math.atan2(t.y, t.x)
            coll.objects.link(o); out.append((p.x, p.y))
    return out

def build_lifts(M):
    """Timber-truss lift shafts on the wall faces, wooden platform on ropes, winch house on the wall top."""
    lc = L.new_coll("TrostLifts")
    H = L.WALL_H
    for spec in WALL_LIFTS:
        bm = bmesh.new()
        y0, y1 = 5.4, 10.2                       # shaft from the wall centre line, outwards
        for sx in (-2.4, 2.4):
            for yy in (y0, y1):
                L.box(bm, (sx, yy, (H + 2) / 2), (0.45, 0.45, H + 2), mi=0)
        for z in range(4, int(H) + 1, 6):
            L.box(bm, (0, y0, z), (5.2, 0.3, 0.3), mi=0); L.box(bm, (0, y1, z), (5.2, 0.3, 0.3), mi=0)
            for sx in (-2.4, 2.4):
                L.box(bm, (sx, (y0 + y1) / 2, z), (0.3, y1 - y0, 0.3), mi=0)
            if z + 6 <= H:
                L.cyl(bm, (-2.4, y1, z), (2.4, y1, z + 6), 0.12, seg=4, mi=0)
                L.cyl(bm, (2.4, y0, z), (-2.4, y0, z + 6), 0.12, seg=4, mi=0)
        # jib over the shaft + winch house straddling the wall edge
        L.box(bm, (0, (2 + y1) / 2 + 0.5, H + 5.2), (0.6, y1 - 1, 0.6), mi=0)
        L.box(bm, (0, 1.6, H + 2.2), (6.0, 5.5, 4.4), mi=1)
        _gable(bm, 0, 1.6, 6.0, 5.5, H + 4.4, 2.4, 2, rot=0.0, over=0.4)
        for sx in (-0.8, 0.8):
            L.cyl(bm, (sx, (y0 + y1) / 2, H + 5.0), (sx, (y0 + y1) / 2, 2.0), 0.05, seg=4, mi=3)
        ob = L.obj_from_bm(f"TrostLift_{spec['name']}", bm, [M["gate"], M["timber"], M["roof_orange"], M["iron"]], lc)
        ox, oy = spec["out"]
        rot = math.atan2(oy, ox) - math.pi / 2               # local +y -> outward normal
        ob.location = (spec["xy"][0], spec["xy"][1], 0); ob.rotation_euler.z = rot
        pb = bmesh.new()
        L.box(pb, (0, 0, 0.18), (4.3, 4.3, 0.36), mi=0)
        for sx in (-2.0, 2.0):
            L.box(pb, (sx, 0, 0.75), (0.15, 4.3, 0.15), mi=0)
        L.box(pb, (0, 0, 2.4), (0.5, 0.5, 0.3), mi=1)
        po = L.obj_from_bm(spec["platform"], pb, [M["gate"], M["iron"]], lc)
        po.parent = ob; po.location = (0, (y0 + y1) / 2, 0.4)
    return lc

def set_breach(on=True):
    """After the kick: the intact OuterGate (+ door) is replaced by the broken, boulder-sized opening and rubble."""
    for n, vis in (("OuterGate", not on), ("OuterGate_Door", not on), ("OuterGateBroken", on), ("OuterGateRubble", on)):
        o = bpy.data.objects.get(n)
        if o:
            o.hide_render = o.hide_viewport = not vis

def set_lift(i, frac):
    po = bpy.data.objects.get(WALL_LIFTS[i]["platform"])
    if po:
        po.location.z = 0.4 + max(0.0, min(1.0, frac)) * (L.WALL_H - 0.6)

# ---------------------------------------------------------------- supply HQ
HQ_UPPER = []
def _merlons(bm, x0, y0, x1, y1, z, mi=0, every=2.2, size=(1.1, 0.9, 1.3)):
    """Crenellation: merlon blocks along the edge (x0, y0) -> (x1, y1) on top of a parapet at height z."""
    L_ = math.hypot(x1 - x0, y1 - y0); n = max(1, int(L_ / every))
    rot = math.atan2(y1 - y0, x1 - x0)
    for k in range(n + 1):
        u = k / n
        L.box(bm, (x0 + (x1 - x0) * u, y0 + (y1 - y0) * u, z + size[2] / 2), (size[0], size[1], size[2]), rot, mi=mi)

def _arched(bm, x, y, z, w, h, axis, mi=1):
    """Arched window inset on a wall face (axis 'x': face normal along y; 'y': normal along x)."""
    if axis == "x":
        L.box(bm, (x, y, z), (w, 0.25, h), mi=mi)
        L.cyl(bm, (x, y - 0.12, z + h / 2), (x, y + 0.12, z + h / 2), w / 2, seg=10, mi=mi)
    else:
        L.box(bm, (x, y, z), (0.25, w, h), mi=mi)
        L.cyl(bm, (x - 0.12, y, z + h / 2), (x + 0.12, y, z + h / 2), w / 2, seg=10, mi=mi)

def build_hq(M):
    """The anime supply HQ complex (refs trost_hq_keep_front / _distant_towers / _warehouse_wing, HANDOFF 10:20-10:22):
    a pale sandstone crenellated KEEP (square block with four corner turrets under slate-blue pyramid roofs, a row of
    arched windows, a taller crenellated central block, a small clock/bell turret on top) joined at its east side to a
    long, tall 5-storey sandstone WAREHOUSE wing (steep dark-slate gabled roof, rows of small square windows, a few
    arched ground-floor windows, pilaster strips on the gable end).  The warehouse ground floor is the storeroom of the
    lift operation (beams, crates, gas racks, the lift); its upper storeys, floor slabs and roof are the cutaway set
    (collection TrostHQ_Upper, set_hq_cutaway(True) opens it to the sky)."""
    up = L.new_coll("TrostHQ_Upper")
    t = 1.4
    Lx, Dy = HQ_L, HQ_D
    # ================= warehouse: ground floor storeroom (z 0..10), stays in the cutaway
    bm = bmesh.new()
    zl = 10.0
    def wall_x(y, z0, z1, door=None):
        if door is None:
            L.box(bm, (0, y, (z0 + z1) / 2), (Lx, t, z1 - z0)); return
        dw, dh = door
        seg = (Lx - dw) / 2
        for sx in (-1, 1):
            L.box(bm, (sx * (dw / 2 + seg / 2), y, (z0 + z1) / 2), (seg, t, z1 - z0))
        L.box(bm, (0, y, (dh + z1) / 2), (dw, t, z1 - dh))
    wall_x(-Dy / 2 + t / 2, 0, zl, door=(8.0, 7.0))
    wall_x(Dy / 2 - t / 2, 0, zl, door=(7.0, 6.0))
    L.box(bm, (Lx / 2 - t / 2, 0, zl / 2), (t, Dy - 2 * t, zl))                       # east gable end (west abuts the keep)
    L.box(bm, (-Lx / 2 + t / 2, 0, zl / 2), (t, Dy - 2 * t, zl))
    L.box(bm, (0, 0, 0.5), (Lx + 1.0, Dy + 1.0, 1.0))                                 # plinth
    for k in range(10):                                                               # pilaster strips, long faces
        xx = -Lx / 2 + 1 + k * (Lx - 2) / 9
        for sy in (-1, 1):
            L.box(bm, (xx, sy * (Dy / 2 + 0.25), zl / 2), (1.3, 0.6, zl))
    for k in range(9):                                                                # arched ground-floor windows
        xx = -Lx / 2 + 4 + k * (Lx - 8) / 8
        if abs(xx) > 6:
            for sy in (-1, 1):
                _arched(bm, xx, sy * (Dy / 2 + 0.05), 4.6, 2.0, 3.2, "x")
    # storeroom interior: plank floor, ceiling beams (the cadets crouch on them), crates, ODM gas racks, the lift frame
    L.box(bm, (0, 0, 0.62), (Lx - 2 * t, Dy - 2 * t, 0.25), mi=2)
    for k in range(1, 10):
        xx = -Lx / 2 + k * Lx / 10
        L.box(bm, (xx, 0, 9.0), (0.7, Dy - 2 * t, 0.9), mi=2)
    for yy in (-Dy / 4, Dy / 4):
        L.box(bm, (0, yy, 8.4), (Lx - 2 * t, 0.6, 0.6), mi=2)
    rnd = random.Random(5)
    for sy in (-1, 1):
        for k in range(12):
            xx = -19 + k * 38 / 11
            if abs(xx) < 5 and sy < 0:
                continue
            for j in range(rnd.randint(1, 3)):
                L.box(bm, (xx + rnd.uniform(-0.3, 0.3), sy * (Dy / 2 - 3.0), 0.75 + 0.8 + j * 1.6), (2.4, 2.4, 1.55), mi=3)
    for row in range(4):
        for k in range(7):
            for sx in (-1, 1):
                x0 = sx * (Lx / 2 - 3.5 - row * 3.0)
                yy = -9 + k * 3.0
                L.cyl(bm, (x0 - 1.1, yy, 1.3), (x0 + 1.1, yy, 1.3), 0.55, seg=10, mi=4)
                L.cyl(bm, (x0 - 1.1, yy, 2.5), (x0 + 1.1, yy, 2.5), 0.55, seg=10, mi=4)
        for sx in (-1, 1):
            L.box(bm, (sx * (Lx / 2 - 3.5 - row * 3.0), 0, 0.9), (0.4, 22, 0.6), mi=2)
    for sx in (-5.6, 5.6):
        for sy in (-5.6, 5.6):
            L.box(bm, (sx, sy, 7.4), (0.6, 0.6, 14.0), mi=2)
    for sy in (-5.6, 5.6):
        L.box(bm, (0, sy, 14.2), (12.0, 0.6, 0.6), mi=2)
    L.cyl(bm, (-4.5, 0, 14.6), (4.5, 0, 14.6), 0.6, seg=12, mi=5)
    low = _to_world(L.obj_from_bm("TrostHQ", bm, [M["hq_stone"], M["window"], M["plank"], M["crate"], M["gas"], M["iron"]]), _HQ_C, _HQ_ROT)
    # lift platform (moves; parented to the storeroom)
    pb = bmesh.new()
    L.box(pb, (0, 0, 0.2), (10.4, 10.4, 0.4), mi=0)
    for sx in (-5.0, 5.0):
        L.box(pb, (sx, 0, 0.9), (0.2, 10.4, 0.2), mi=1); L.box(pb, (0, sx, 0.9), (10.4, 0.2, 0.2), mi=1)
    for sx in (-4.8, 4.8):
        for sy in (-4.8, 4.8):
            L.box(pb, (sx, sy, 0.6), (0.2, 0.2, 0.8), mi=1)
    lift = L.obj_from_bm("TrostHQ_Lift", pb, [M["plank"], M["iron"]])
    lift.parent = low; lift.location = (0, 0, 10.0)
    # ================= warehouse upper storeys z 10..26, slabs, steep dark-slate gabled roof (the cutaway set)
    ub = bmesh.new()
    zt = 26.0
    for sy in (-1, 1):
        L.box(ub, (0, sy * (Dy / 2 - t / 2), (zl + zt) / 2), (Lx, t, zt - zl))
        L.box(ub, (0, sy * (Dy / 2 + 0.2), zl + 0.3), (Lx + 0.4, 0.6, 0.6))           # string course
        for k in range(10):
            xx = -Lx / 2 + 1 + k * (Lx - 2) / 9
            L.box(ub, (xx, sy * (Dy / 2 + 0.25), (zl + zt) / 2), (1.3, 0.6, zt - zl))
        for zz in (12.6, 15.8, 19.0, 22.2):                                           # rows of small square windows
            for k in range(16):
                xx = -Lx / 2 + 3 + k * (Lx - 6) / 15
                L.box(ub, (xx, sy * (Dy / 2 + 0.05), zz), (1.2, 0.2, 1.3), mi=1)
    for sx in (-1, 1):
        L.box(ub, (sx * (Lx / 2 - t / 2), 0, (zl + zt) / 2), (t, Dy - 2 * t, zt - zl))
    # east gable end: triangle up to the ridge + pilaster strips + windows
    ridge = zt + 15.0
    ge = [ub.verts.new(c) for c in ((Lx / 2, -Dy / 2, zt), (Lx / 2, Dy / 2, zt), (Lx / 2, 0, ridge))]
    ub.faces.new(ge)
    ge2 = [ub.verts.new(c) for c in ((Lx / 2 - t, -Dy / 2, zt), (Lx / 2 - t, 0, ridge), (Lx / 2 - t, Dy / 2, zt))]
    ub.faces.new(ge2)
    for xg in (-Lx / 2, -Lx / 2 + t):                                                 # west gable (above the keep)
        ub.faces.new([ub.verts.new(c) for c in ((xg, -Dy / 2, zt), (xg, 0, ridge), (xg, Dy / 2, zt))])
    for yy in (-Dy / 2 + 0.8, -5, 5, Dy / 2 - 0.8):
        top = zt + 15.0 * (1 - abs(yy) / (Dy / 2)) - 0.6
        L.box(ub, (Lx / 2 + 0.3, yy, top / 2), (0.6, 1.2, top))
    for zz in (12.6, 15.8, 19.0, 22.2, 26.5, 30.5):
        for yy in ((-9, -3, 3, 9) if zz < 26 else ((-3, 3) if zz < 30 else (0,))):
            L.box(ub, (Lx / 2 + 0.05, yy, zz), (0.2, 1.2, 1.3), mi=1)
    def slab(z, hole=6.0):
        th = 0.6
        L.box(ub, (0, -(Dy / 2 + hole) / 2, z), (Lx - 2 * t, Dy / 2 - hole - t, th), mi=2)
        L.box(ub, (0, (Dy / 2 + hole) / 2, z), (Lx - 2 * t, Dy / 2 - hole - t, th), mi=2)
        for sx in (-1, 1):
            L.box(ub, (sx * (Lx / 2 + hole) / 2, 0, z), (Lx / 2 - hole - t, 2 * hole, th), mi=2)
    slab(zl - 0.1); slab(16.0); slab(21.0)
    _gable(ub, 0, 0, Lx + 0.4, Dy, zt, 15.0, 3, over=0.9)                              # steep slate roof (~45 deg)
    for xx in (-22, 0, 22):                                                           # chimneys on the ridge
        L.box(ub, (xx, 3.0, ridge - 1.0), (1.6, 1.6, 6.0))
    upper = _to_world(L.obj_from_bm("TrostHQ_Upper", ub, [M["hq_stone"], M["window"], M["plank"], M["hq_slate"]], up), _HQ_C, _HQ_ROT)
    HQ_UPPER[:] = [upper.name]
    # ================= the keep (west end, joined to the warehouse), stays in the cutaway
    kb = bmesh.new()
    kx, K_ = HQ_KEEP_X, HQ_KEEP
    zk = 24.0
    L.box(kb, (kx, 0, zk / 2), (K_, K_, zk))                                          # main block
    L.box(kb, (kx, 0, zk + 0.8), (K_ + 0.6, K_ + 0.6, 1.6))                           # parapet
    h = K_ / 2
    for (ax, ay, bx, by) in ((-h, -h, h, -h), (h, -h, h, h), (h, h, -h, h), (-h, h, -h, -h)):
        _merlons(kb, kx + ax, ay, kx + bx, by, zk + 1.6)
    for k in range(7):                                                                # row of arched windows, 3 faces
        u = -h + 3.5 + k * (K_ - 7) / 6
        _arched(kb, kx + u, -h - 0.05, 15.0, 1.6, 3.0, "x"); _arched(kb, kx + u, h + 0.05, 15.0, 1.6, 3.0, "x")
        _arched(kb, kx - h - 0.05, u, 15.0, 1.6, 3.0, "y")
    L.box(kb, (kx - h - 0.6, 0, 3.5), (1.2, 6.0, 7.0), mi=1)                          # gate in the west face
    for sx in (-1, 1):                                                                # four corner turrets
        for sy in (-1, 1):
            cx, cy = kx + sx * h, sy * h
            L.box(kb, (cx, cy, 15.5), (7.0, 7.0, 31.0))
            L.box(kb, (cx, cy, 31.2), (7.6, 7.6, 0.6))
            L.box(kb, (cx, cy, 34.6), (8.0, 8.0, 6.2), mi=2, taper=(0.04, 0.04))      # slate-blue pyramid roof
            for k in (-1, 1):
                L.box(kb, (cx + k * 1.2, cy + sy * 3.55, 28.0), (0.4, 0.2, 2.2), mi=1)
    # taller central block with its own crenellation, and the small clock / bell turret on top
    cb = 16.0; zc = 36.0
    L.box(kb, (kx + 2, 0, zc / 2), (cb, cb, zc))
    L.box(kb, (kx + 2, 0, zc + 0.7), (cb + 0.6, cb + 0.6, 1.4))
    hb = cb / 2
    for (ax, ay, bx, by) in ((-hb, -hb, hb, -hb), (hb, -hb, hb, hb), (hb, hb, -hb, hb), (-hb, hb, -hb, -hb)):
        _merlons(kb, kx + 2 + ax, ay, kx + 2 + bx, by, zc + 1.4)
    for k in range(5):
        u = -hb + 2.5 + k * (cb - 5) / 4
        for zz in (27.0, 31.5):
            L.box(kb, (kx + 2 + u, -hb - 0.05, zz), (0.9, 0.2, 2.0), mi=1)
            L.box(kb, (kx + 2 + u, hb + 0.05, zz), (0.9, 0.2, 2.0), mi=1)
    tx = kx + 2
    L.box(kb, (tx, 0, zc + 4.5), (5.0, 5.0, 7.0))                                     # clock / bell turret
    for s in (-1, 1):
        _arched(kb, tx, s * 2.55, zc + 5.0, 1.6, 2.4, "x"); _arched(kb, tx + s * 2.55, 0, zc + 5.0, 1.6, 2.4, "y")
    L.cyl(kb, (tx, -2.56, zc + 2.8), (tx, -2.62, zc + 2.8), 0.9, seg=16, mi=3)       # clock face
    L.box(kb, (tx, 0, zc + 8.4), (5.8, 5.8, 0.8))
    L.cyl(kb, (tx, 0, zc + 8.8), (tx, 0, zc + 11.5), 2.4, 1.6, seg=12, mi=0)          # cupola
    L.cyl(kb, (tx, 0, zc + 11.5), (tx, 0, zc + 13.0), 1.0, 0.1, seg=12, mi=2)
    keep = _to_world(L.obj_from_bm("TrostHQ_Keep", kb, [M["hq_stone"], M["window"], M["roof_turret"], M["clock"]]), _HQ_C, _HQ_ROT)
    return low

def set_hq_cutaway(on=True):
    for n in HQ_UPPER:
        o = bpy.data.objects.get(n)
        if o:
            o.hide_render = bool(on); o.hide_viewport = bool(on)

def set_hq_lift(frac):
    o = bpy.data.objects.get("TrostHQ_Lift")
    if o:
        lo, hi = SUPPLY_HQ["lift_z"]
        o.location.z = hi + (lo - hi) * max(0.0, min(1.0, frac))

# ---------------------------------------------------------------- the cannon basin
def build_basin(M):
    bm = bmesh.new()
    X0, X1, Y0, Y1 = _BX0, _BX1, _BY0, _BY1
    span = X1 - X0
    L.box(bm, ((X0 + X1) / 2, (Y0 + Y1) / 2, 0.08), (span, Y1 - Y0, 0.16), mi=1)      # mossy floor
    for side in (1, -1):                                                               # stepped banks + terraces
        for k in range(_BSTEP_N):
            y0 = (Y1 + k * _BSTEP_D) if side > 0 else (Y0 - (k + 1) * _BSTEP_D)
            z = (k + 1) * _BSTEP_H
            L.box(bm, ((X0 + X1) / 2, y0 + _BSTEP_D / 2, z / 2), (span, _BSTEP_D, z), mi=0)
        yt = (Y1 + _BSTEP_N * _BSTEP_D) if side > 0 else (Y0 - _BSTEP_N * _BSTEP_D - 8)
        L.box(bm, ((X0 - 14 + X1) / 2, yt + 4, _BTOP / 2), (span + 14, 8, _BTOP), mi=0)   # terrace
        L.box(bm, ((X0 - 14 + X1) / 2, yt + (8.2 if side > 0 else -0.2), _BTOP + 0.5), (span + 14, 0.5, 1.0), mi=0)   # outer parapet
    L.box(bm, (517.0, Y0 - 4.5, 2.32), (10.0, 9.0, 4.64), mi=0)                         # the raised landing (salute)
    # west retaining wall (10 m) with three buttress piers and a walk on top, terrace behind it
    L.box(bm, (X0 - 7, (Y0 + Y1) / 2, _BTOP / 2), (14, Y1 - Y0, _BTOP), mi=0)
    L.box(bm, (X0 - 1.5, (Y0 + Y1) / 2, 5.0), (3.0, Y1 - Y0 + 2 * _BSTEP_N * _BSTEP_D, 10.0), mi=0)
    for yy in (Y0 + 6, (Y0 + Y1) / 2, Y1 - 6):
        L.box(bm, (X0 + 1.0, yy, 4.6), (2.4, 4.0, 9.2), mi=0, taper=(0.6, 0.85))
    # quay edge, bollards and mooring rings on the canal side
    L.box(bm, (X1 - 0.6, (Y0 + Y1) / 2, 0.25), (1.2, Y1 - Y0, 0.5), mi=0)
    for yy in (Y0 + 8, (Y0 + Y1) / 2, Y1 - 8):
        L.cyl(bm, (X1 - 0.8, yy, 0.4), (X1 - 0.8, yy, 1.3), 0.35, 0.28, seg=8, mi=2)
    for side in (1, -1):                                                               # dark step nosings
        for k in range(_BSTEP_N):
            yn = (Y1 + k * _BSTEP_D) if side > 0 else (Y0 - k * _BSTEP_D)
            L.box(bm, ((X0 + X1) / 2, yn, (k + 1) * _BSTEP_H - 0.03), (span, 0.14, 0.1), mi=3)
    ob = L.obj_from_bm("TrostCannonBasin", bm, [M["basin_stone"], M["moss_floor"], M["iron"], M["step_edge"]])
    # the boat at the quay
    bb = bmesh.new()
    L.box(bb, (0, 0, 0.55), (9.0, 2.6, 0.9), taper=(1.0, 1.25), mi=0)
    L.box(bb, (4.8, 0, 0.75), (1.4, 1.6, 0.9), taper=(0.2, 0.8), mi=0)
    L.box(bb, (-4.6, 0, 0.75), (0.8, 2.2, 0.9), mi=0)
    for xx in (-2.4, 0.0, 2.4):
        L.box(bb, (xx, 0, 0.9), (0.3, 2.5, 0.12), mi=1)
    bo = L.obj_from_bm("TrostBoat", bb, [M["gate"], M["plank"]])
    bx, by, bz = CANNON_BASIN["boat"]
    bo.location = (bx, by, bz - 0.25); bo.rotation_euler.z = math.pi / 2
    return ob

# ---------------------------------------------------------------- church with the bell tower
def build_church(M):
    bm = bmesh.new()
    # nave along x (-20..20), width 16, walls 15 m, steep gable; apse at the west end
    L.box(bm, (0, 0, 7.5), (40, 16, 15), mi=0)
    _gable(bm, 0, 0, 40, 16, 15, 10, 1, over=0.5)
    L.cyl(bm, (-20, 0, 0), (-20, 0, 12), 7.5, seg=12, mi=0)
    L.cyl(bm, (-20, 0, 12), (-20, 0, 18), 8.0, 0.5, seg=12, mi=1)
    for k in range(6):                                        # tall nave windows
        xx = -15 + k * 6
        for sy in (-1, 1):
            L.box(bm, (xx, sy * 8.05, 8.5), (1.6, 0.2, 6.0), mi=2)
    # square tower 10x10 to 34 m, open octagonal belfry 34..43, dark pointed octagonal cap to 64 m
    tx = 25.0
    L.box(bm, (tx, 0, 17.0), (10, 10, 34), mi=3)
    L.box(bm, (tx, 0, 34.3), (11, 11, 0.6), mi=3)
    for k in range(3):
        L.box(bm, (tx + 5.05, 0, 12 + k * 7), (0.2, 1.6, 3.4), mi=2)
    L.box(bm, (tx + 5.05, 0, 3.0), (0.3, 3.2, 6.0), mi=4)        # door to the plaza
    L.cyl(bm, (tx, 0, 34.0), (tx, 0, 34.6), 5.4, seg=8, mi=3)
    for k in range(8):
        a = math.radians(22.5 + k * 45)
        L.box(bm, (tx + math.cos(a) * 4.6, math.sin(a) * 4.6, 38.8), (0.9, 0.9, 8.4), rot=a, mi=3)
    L.cyl(bm, (tx, 0, 42.8), (tx, 0, 43.6), 5.6, seg=8, mi=3)
    L.cyl(bm, (tx, 0, 43.6), (tx, 0, 64.0), 5.8, 0.1, seg=8, mi=1)
    L.cyl(bm, (tx, 0, 39.8), (tx, 0, 36.2), 0.5, 1.7, seg=12, mi=5)    # the bell
    L.cyl(bm, (tx, 0, 42.8), (tx, 0, 39.8), 0.12, seg=4, mi=5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = L.obj_from_bm("TrostChurch", bm, [M["church_w"], M["roof_slate"], M["window"], M["stone_light"], M["gate"], M["bronze"]])
    ob.location = (_CH_C[0], _CH_C[1], 0)
    return ob

# ---------------------------------------------------------------- the boulder
def _uv_walls(N, Lk, tc):
    """(x + y, z) from object coordinates: a wall-plane coordinate that works for walls facing x or y."""
    sep = N.new("ShaderNodeSeparateXYZ"); Lk.new(tc.outputs["Object"], sep.inputs[0])
    ad = N.new("ShaderNodeMath"); ad.operation = "ADD"; Lk.new(sep.outputs["X"], ad.inputs[0]); Lk.new(sep.outputs["Y"], ad.inputs[1])
    cb = N.new("ShaderNodeCombineXYZ"); Lk.new(ad.outputs[0], cb.inputs["X"]); Lk.new(sep.outputs["Z"], cb.inputs["Y"])
    # horizontal faces (tops of steps, terraces, roofs) use (x, y) so the blocks don't smear into plank stripes
    geo = N.new("ShaderNodeNewGeometry"); sn = N.new("ShaderNodeSeparateXYZ"); Lk.new(geo.outputs["Normal"], sn.inputs[0])
    ab = N.new("ShaderNodeMath"); ab.operation = "ABSOLUTE"; Lk.new(sn.outputs["Z"], ab.inputs[0])
    gt = N.new("ShaderNodeMath"); gt.operation = "GREATER_THAN"; gt.inputs[1].default_value = 0.6; Lk.new(ab.outputs[0], gt.inputs[0])
    mx = N.new("ShaderNodeMix"); mx.data_type = "VECTOR"
    Lk.new(gt.outputs[0], mx.inputs["Factor"]); Lk.new(cb.outputs[0], mx.inputs[4]); Lk.new(tc.outputs["Object"], mx.inputs[5])
    return mx.outputs[1], sep.outputs["Z"]

def stone_block_mat(name, base, base2, mortar, scale=0.6, damp=0.0, moss=0.0):
    """Procedural stone blocks (sandstone / old dock stone): running-bond blocks ~0.8 x 0.4 m with per-block colour
    variation, grime noise and mortar bump.  damp > 0 darkens the lower walls (object z < ~4 m) with vertical moss
    streaks (the cannon basin, ref trost_cannon_canal_ref.png)."""
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; N = nt.nodes; Lk = nt.links
    bsdf = N["Principled BSDF"]; bsdf.inputs["Roughness"].default_value = 0.9
    tc = N.new("ShaderNodeTexCoord")
    uv, z = _uv_walls(N, Lk, tc)
    br = N.new("ShaderNodeTexBrick"); br.inputs["Scale"].default_value = scale
    br.inputs["Color1"].default_value = (*base, 1); br.inputs["Color2"].default_value = (*base2, 1)
    br.inputs["Mortar"].default_value = (*mortar, 1); br.inputs["Mortar Size"].default_value = 0.025
    br.inputs["Bias"].default_value = 0.0; br.offset = 0.5
    Lk.new(uv, br.inputs["Vector"])
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 0.35; nz.inputs["Detail"].default_value = 6
    Lk.new(tc.outputs["Object"], nz.inputs["Vector"])
    gr = N.new("ShaderNodeMix"); gr.data_type = "RGBA"; gr.blend_type = "MULTIPLY"; gr.inputs["Factor"].default_value = 0.35
    Lk.new(br.outputs["Color"], gr.inputs["A"]); Lk.new(nz.outputs["Color"], gr.inputs["B"])
    col = gr.outputs["Result"]
    if damp > 0:
        dz = N.new("ShaderNodeMapRange"); dz.inputs["From Min"].default_value = 4.5; dz.inputs["From Max"].default_value = 0.5
        Lk.new(z, dz.inputs["Value"])
        st = N.new("ShaderNodeVectorMath"); st.operation = "MULTIPLY"; st.inputs[1].default_value = (0.9, 0.9, 0.06)
        Lk.new(tc.outputs["Object"], st.inputs[0])
        sn = N.new("ShaderNodeTexNoise"); sn.inputs["Scale"].default_value = 1.4; sn.inputs["Detail"].default_value = 4
        Lk.new(st.outputs[0], sn.inputs["Vector"])
        streak = N.new("ShaderNodeMath"); streak.operation = "MULTIPLY"; Lk.new(sn.outputs["Fac"], streak.inputs[0])
        Lk.new(dz.outputs["Result"], streak.inputs[1])
        fac = N.new("ShaderNodeMath"); fac.operation = "MULTIPLY"; fac.inputs[1].default_value = damp * 1.6
        Lk.new(streak.outputs[0], fac.inputs[0])
        dk = N.new("ShaderNodeMix"); dk.data_type = "RGBA"; dk.blend_type = "MULTIPLY"
        Lk.new(fac.outputs[0], dk.inputs["Factor"]); Lk.new(col, dk.inputs["A"]); dk.inputs["B"].default_value = (0.25, 0.27, 0.2, 1)
        col = dk.outputs["Result"]
        if moss > 0:
            mf = N.new("ShaderNodeMath"); mf.operation = "MULTIPLY"; mf.inputs[1].default_value = moss
            Lk.new(fac.outputs[0], mf.inputs[0])
            mm = N.new("ShaderNodeMix"); mm.data_type = "RGBA"
            Lk.new(mf.outputs[0], mm.inputs["Factor"]); Lk.new(col, mm.inputs["A"]); mm.inputs["B"].default_value = (0.06, 0.09, 0.035, 1)
            col = mm.outputs["Result"]
    Lk.new(col, bsdf.inputs["Base Color"])
    bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.3
    Lk.new(br.outputs["Fac"], bp.inputs["Height"]); Lk.new(bp.outputs["Normal"], bsdf.inputs["Normal"])
    return m

def marble_mat(name="TrostBoulderMarble"):
    """Smooth grey stone with a subtle marbled surface (the anime boulder: a near-perfect grey sphere)."""
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; N = nt.nodes; Lk = nt.links
    bsdf = N["Principled BSDF"]; bsdf.inputs["Roughness"].default_value = 0.55
    tc = N.new("ShaderNodeTexCoord")
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 0.25; nz.inputs["Detail"].default_value = 8
    nz.inputs["Distortion"].default_value = 2.5
    Lk.new(tc.outputs["Object"], nz.inputs["Vector"])
    wv = N.new("ShaderNodeTexWave"); wv.inputs["Scale"].default_value = 0.12; wv.inputs["Distortion"].default_value = 9.0
    wv.inputs["Detail"].default_value = 6
    Lk.new(tc.outputs["Object"], wv.inputs["Vector"])
    rp = N.new("ShaderNodeValToRGB"); e = rp.color_ramp.elements
    e[0].position, e[0].color = 0.25, (0.26, 0.26, 0.265, 1)
    e[1].position, e[1].color = 0.8, (0.34, 0.335, 0.33, 1)
    mx = N.new("ShaderNodeMath"); mx.operation = "ADD"
    Lk.new(nz.outputs["Fac"], mx.inputs[0]); Lk.new(wv.outputs["Fac"], mx.inputs[1])
    wq = N.new("ShaderNodeMath"); wq.operation = "MULTIPLY"; wq.inputs[1].default_value = 0.25    # faint veins only
    Lk.new(wv.outputs["Fac"], wq.inputs[0])
    mx2 = N.new("ShaderNodeMath"); mx2.operation = "ADD"; Lk.new(nz.outputs["Fac"], mx2.inputs[0]); Lk.new(wq.outputs[0], mx2.inputs[1])
    hf = N.new("ShaderNodeMath"); hf.operation = "MULTIPLY"; hf.inputs[1].default_value = 0.8
    Lk.new(mx2.outputs[0], hf.inputs[0]); Lk.new(hf.outputs[0], rp.inputs["Fac"])
    Lk.new(rp.outputs["Color"], bsdf.inputs["Base Color"])
    fn = N.new("ShaderNodeTexNoise"); fn.inputs["Scale"].default_value = 6.0; fn.inputs["Detail"].default_value = 4
    Lk.new(tc.outputs["Object"], fn.inputs["Vector"])
    bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.08
    Lk.new(fn.outputs["Fac"], bp.inputs["Height"]); Lk.new(bp.outputs["Normal"], bsdf.inputs["Normal"])
    return m

def rock_mat(name="TrostRock"):
    """Rough boulder shading: grey-brown mottling, dark crevices along Voronoi cracks, moss on up-facing surfaces,
    bump from the cracks + fine grain (design bible 3.6: albedo ~#7a706a, fracture faces lighter)."""
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; N = nt.nodes; Lk = nt.links
    bsdf = N["Principled BSDF"]; bsdf.inputs["Roughness"].default_value = 0.95
    tc = N.new("ShaderNodeTexCoord")
    n1 = N.new("ShaderNodeTexNoise"); n1.inputs["Scale"].default_value = 0.22; n1.inputs["Detail"].default_value = 10
    n1.inputs["Roughness"].default_value = 0.62; Lk.new(tc.outputs["Object"], n1.inputs["Vector"])
    r1 = N.new("ShaderNodeValToRGB"); e = r1.color_ramp.elements
    e[0].position, e[0].color = 0.32, (0.105, 0.090, 0.080, 1)
    e[1].position, e[1].color = 0.70, (0.30, 0.27, 0.24, 1)
    Lk.new(n1.outputs["Fac"], r1.inputs["Fac"])
    n2 = N.new("ShaderNodeTexNoise"); n2.inputs["Scale"].default_value = 2.5; n2.inputs["Detail"].default_value = 6
    Lk.new(tc.outputs["Object"], n2.inputs["Vector"])
    grain = N.new("ShaderNodeMix"); grain.data_type = "RGBA"; grain.blend_type = "OVERLAY"; grain.inputs["Factor"].default_value = 0.35
    Lk.new(r1.outputs["Color"], grain.inputs["A"]); Lk.new(n2.outputs["Color"], grain.inputs["B"])
    # cracks: Voronoi distance-to-edge, warped by noise
    nw = N.new("ShaderNodeTexNoise"); nw.inputs["Scale"].default_value = 0.6; nw.inputs["Detail"].default_value = 4
    Lk.new(tc.outputs["Object"], nw.inputs["Vector"])
    wsc = N.new("ShaderNodeVectorMath"); wsc.operation = "SCALE"; wsc.inputs["Scale"].default_value = 3.5
    Lk.new(nw.outputs["Color"], wsc.inputs[0])
    wp = N.new("ShaderNodeVectorMath"); wp.operation = "ADD"
    Lk.new(tc.outputs["Object"], wp.inputs[0]); Lk.new(wsc.outputs[0], wp.inputs[1])
    vo = N.new("ShaderNodeTexVoronoi"); vo.feature = "DISTANCE_TO_EDGE"; vo.inputs["Scale"].default_value = 0.16; vo.inputs["Randomness"].default_value = 1.0
    Lk.new(wp.outputs[0], vo.inputs["Vector"])
    cr = N.new("ShaderNodeMapRange"); cr.inputs["From Min"].default_value = 0.0; cr.inputs["From Max"].default_value = 0.014
    cr.inputs["To Min"].default_value = 0.75; cr.inputs["To Max"].default_value = 0.0
    Lk.new(vo.outputs["Distance"], cr.inputs["Value"])
    dk = N.new("ShaderNodeMix"); dk.data_type = "RGBA"
    Lk.new(cr.outputs["Result"], dk.inputs["Factor"]); Lk.new(grain.outputs["Result"], dk.inputs["A"])
    dk.inputs["B"].default_value = (0.025, 0.022, 0.02, 1)
    # moss on up-facing surfaces, broken up by noise
    geo = N.new("ShaderNodeNewGeometry"); sep = N.new("ShaderNodeSeparateXYZ"); Lk.new(geo.outputs["Normal"], sep.inputs[0])
    n3 = N.new("ShaderNodeTexNoise"); n3.inputs["Scale"].default_value = 0.5; n3.inputs["Detail"].default_value = 5
    Lk.new(tc.outputs["Object"], n3.inputs["Vector"])
    ad = N.new("ShaderNodeMath"); ad.operation = "ADD"; Lk.new(sep.outputs["Z"], ad.inputs[0])
    sc_ = N.new("ShaderNodeMath"); sc_.operation = "MULTIPLY"; sc_.inputs[1].default_value = 0.8
    Lk.new(n3.outputs["Fac"], sc_.inputs[0]); Lk.new(sc_.outputs[0], ad.inputs[1])
    mm = N.new("ShaderNodeMapRange"); mm.inputs["From Min"].default_value = 1.25; mm.inputs["From Max"].default_value = 1.55
    Lk.new(ad.outputs[0], mm.inputs["Value"])
    moss = N.new("ShaderNodeMix"); moss.data_type = "RGBA"
    Lk.new(mm.outputs["Result"], moss.inputs["Factor"]); Lk.new(dk.outputs["Result"], moss.inputs["A"])
    moss.inputs["B"].default_value = (0.07, 0.10, 0.03, 1)
    Lk.new(moss.outputs["Result"], bsdf.inputs["Base Color"])
    bh = N.new("ShaderNodeMath"); bh.operation = "SUBTRACT"; Lk.new(n2.outputs["Fac"], bh.inputs[0]); Lk.new(cr.outputs["Result"], bh.inputs[1])
    bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.6; bp.inputs["Distance"].default_value = 0.3
    Lk.new(bh.outputs[0], bp.inputs["Height"]); Lk.new(bp.outputs["Normal"], bsdf.inputs["Normal"])
    return m

def boulder_mesh(name="TrostBoulderMesh", origin="bottom"):
    """The anime boulder: an almost perfectly round, smooth grey near-sphere (slight irregularity only, a small flat
    seat where it rests). origin = "bottom" (bottom centre) or "center"."""
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=4, radius=1.0)
    rx, ry, rz = BOULDER_SIZE[0] / 2, BOULDER_SIZE[1] / 2, BOULDER_SIZE[2] / 2
    for v in bm.verts:
        n = v.co.normalized()
        d = 1.0 + 0.025 * noise.noise(n * 1.4 + Vector((3, 1, 7))) + 0.008 * noise.noise(n * 4.0 + Vector((1, 9, 2)))
        v.co = Vector((n.x * rx * d, n.y * ry * d, n.z * rz * d))
        if v.co.z < -rz * 0.93:
            v.co.z = -rz * 0.93                                          # small flat seat
    zoff = rz * 0.93 - 0.15 if origin == "bottom" else 0.0
    for v in bm.verts:
        v.co.z += zoff
    for f in bm.faces:
        f.smooth = True
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    return me

def build_boulder(M):
    me = boulder_mesh()
    me.materials.append(M["rock"])
    ob = bpy.data.objects.new("TrostBoulder", me); bpy.context.scene.collection.objects.link(ob)
    ob.location = (BOULDER[0], BOULDER[1], ground_z(BOULDER[0], BOULDER[1]))
    ob.rotation_euler.z = math.radians(28)
    rb = bmesh.new()                                                    # rubble and loose rocks around its seat
    rnd = random.Random(13)
    for i in range(14):
        a = rnd.uniform(0, math.tau); r = rnd.uniform(8.0, 12.0); s = rnd.uniform(0.3, 0.9)
        c = bmesh.ops.create_icosphere(rb, subdivisions=1, radius=s)
        for v in c["verts"]:
            v.co.z *= 0.6
            v.co += Vector((BOULDER[0] + math.cos(a) * r, BOULDER[1] + math.sin(a) * r, 0.1))
    L.obj_from_bm("TrostBoulderRubble", rb, [M["rubble"]])
    return ob

# ---------------------------------------------------------------- cargo wagon (inner gate jam)
def build_wagon(M):
    bm = bmesh.new()
    L.box(bm, (0, 0, 1.6), (13.0, 4.6, 0.5), mi=0)
    L.box(bm, (0, 0, 3.6), (12.4, 4.4, 3.6), mi=1)                    # tarp-covered load
    L.cyl(bm, (-6.2, 0, 5.4), (6.2, 0, 5.4), 2.2, seg=10, mi=1)
    for sx in (-4.6, 4.6):
        for sy in (-2.5, 2.5):
            L.cyl(bm, (sx, sy - 0.25, 1.15), (sx, sy + 0.25, 1.15), 1.15, seg=12, mi=2)
    L.box(bm, (0, -4.6, 1.3), (0.3, 5.0, 0.2), mi=0)                  # drawbar
    ob = L.obj_from_bm("TrostCargoWagon", bm, [M["gate"], M["tarp"], M["iron"]])
    ob.location = (INNER_GATE[0] + 0.4, -6.5, 0); ob.rotation_euler.z = math.radians(4)
    ob.hide_render = ob.hide_viewport = True
    return ob

def set_wagon(on=True):
    o = bpy.data.objects.get("TrostCargoWagon")
    if o:
        o.hide_render = o.hide_viewport = not on

# ---------------------------------------------------------------- town
def _blocked(x, y, rad):
    if abs(x - CANAL_X) < CANAL_W / 2 + 4 + rad:
        return True
    if _in_hq(x, y, rad) or _in_church(x, y, rad + 2) or _in_basin(x, y, rad + 1):
        return True
    for cx, cy, r in (PLAZA, BOULDER_SQUARE, OUTER_GATE_SQUARE):
        if (x - cx) ** 2 + (y - cy) ** 2 < (r + rad) ** 2:
            return True
    if INNER_GATE_SQUARE[0] - rad < x < INNER_GATE_SQUARE[2] + rad and INNER_GATE_SQUARE[1] - rad < y:
        return True
    for l in WALL_LIFTS:                                    # foot of each lift stays clear
        if (x - l["xy"][0]) ** 2 + (y - l["xy"][1]) ** 2 < (16 + rad) ** 2:
            return True
    return False

def town_points(n_variants, widths):
    rnd = random.Random(31)
    pts, trees, occ = [], [], {}
    def free(x, y, rad):
        gx, gy = int(x // 12), int(y // 12)
        for i in (-1, 0, 1):
            for j in (-1, 0, 1):
                for ox, oy, orad in occ.get((gx + i, gy + j), ()):
                    if (ox - x) ** 2 + (oy - y) ** 2 < (rad + orad) ** 2:
                        return False
        return True
    def put(x, y, ang, v, rad):
        pts.append((x, y, 0, ang, rnd.uniform(0.92, 1.08), v, -10000.0, 99999.0))
        occ.setdefault((int(x // 12), int(y // 12)), []).append((x, y, rad))
    for spts, hw in street_polylines():
        for k in range(len(spts) - 1):
            ax, ay = spts[k]; bx, by = spts[k + 1]
            seg = math.hypot(bx - ax, by - ay)
            if seg == 0:
                continue
            tx, ty = (bx - ax) / seg, (by - ay) / seg
            nx, ny = -ty, tx
            t = 0.0
            while t < seg:
                v = rnd.randrange(n_variants); w, dpt = widths[v]
                for side in (1, -1):
                    off = hw + dpt / 2 + 0.8
                    x = ax + tx * t + nx * off * side; y = ay + ty * t + ny * off * side
                    if rnd.random() < 0.05 or not in_district(x, y, 15):
                        continue
                    rad = min(w, dpt) * 0.5
                    if _blocked(x, y, rad) or on_road(x, y, pad=dpt / 2 - 0.5):
                        continue
                    if free(x, y, rad):
                        put(x, y, math.atan2(ty, tx) + (0 if side > 0 else math.pi), v, rad)
                t += w + rnd.uniform(0.2, 1.2)
    for _ in range(40000):
        x, y = rnd.uniform(-W, W), rnd.uniform(-S - R, 0)
        if not in_district(x, y, 16) or on_road(x, y, pad=4):
            continue
        v = rnd.randrange(n_variants); w, dpt = widths[v]
        r = max(w, dpt) * 0.55
        if _blocked(x, y, r) or not free(x, y, r):
            continue
        if rnd.random() < 0.65:
            ang = (0 if y > -S else math.atan2(y + S, x)) + math.pi / 2 + noise.noise(Vector((x / 260, y / 260, 2.5))) * 0.3
            put(x, y, ang, v, r)
        elif rnd.random() < 0.5:
            trees.append((x, y, 0, rnd.uniform(0, 6.28), rnd.uniform(0.6, 0.9), rnd.randrange(7), -10000.0, 99999.0))
            occ.setdefault((int(x // 12), int(y // 12)), []).append((x, y, 3))
    return pts, trees

def build_bridges(M):
    bm = bmesh.new()
    n = 0
    for pts, hw in street_polylines():
        for k in range(len(pts) - 1):
            (ax, ay), (bx, by) = pts[k], pts[k + 1]
            if (ax - CANAL_X) * (bx - CANAL_X) < 0 and in_district(ax, ay, 0):
                f = (CANAL_X - ax) / (bx - ax); yc = ay + (by - ay) * f
                rot = math.atan2(by - ay, bx - ax)
                c = math.cos(rot)
                ln = (CANAL_W + 10) / max(0.4, abs(c))
                L.box(bm, (CANAL_X, yc, 0.55), (ln, 2 * hw + 1.2, 0.9), rot)
                for s in (-1, 1):
                    px, py = CANAL_X - math.sin(rot) * s * (hw + 0.4), yc + math.cos(rot) * s * (hw + 0.4)
                    L.box(bm, (px, py, 1.4), (ln, 0.5, 0.9), rot)
                L.box(bm, (CANAL_X, yc, -1.0), (3.0 / max(0.4, abs(c)), 2 * hw + 1.2, 2.4), rot)   # pier
                n += 1
    # one bridge just outside the SE water gate (the road along the river)
    ox, oy = WATER_GATE_OUTER
    bx = ox + math.sin(0.75) * 140 * 0.6                    # river centre 120 m south of the gate (scene.canal path)
    L.box(bm, (bx, oy - 120, L.height(bx + 30, oy - 120) + 2.9), (CANAL_W + 34, 9, 0.9), 0.0)
    L.obj_from_bm("TrostBridges", bm, [M["stone_light"]])
    return n

def build_fountain(M):
    bm = bmesh.new()
    L.cyl(bm, (0, 0, 0), (0, 0, 0.9), 6.5, seg=16)
    L.cyl(bm, (0, 0, 0.9), (0, 0, 4.0), 0.9, 0.6, seg=10)
    L.cyl(bm, (0, 0, 4.0), (0, 0, 4.6), 2.2, seg=12)
    ob = L.obj_from_bm("TrostWell", bm, [M["stone_light"]])
    ob.location = (PLAZA[0] + 14, PLAZA[1] + 10, 0)

# ---------------------------------------------------------------- world (as scene.build)
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
    el, az = math.radians(38), math.radians(float(os.environ.get("SUN_AZ", "25")))
    d = Vector((-math.cos(el) * math.cos(az), -math.cos(el) * math.sin(az), -math.sin(el)))
    so.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    if os.environ.get("TROST_HAZE", "1") != "0":
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 230)); hz = bpy.context.active_object
        hz.name = "Haze"; hz.scale = (18000, 18000, 540)
        hm = bpy.data.materials.new("Haze"); hm.use_nodes = True
        hn = hm.node_tree; hn.nodes.remove(hn.nodes["Principled BSDF"])
        pv = hn.nodes.new("ShaderNodeVolumePrincipled"); pv.inputs["Density"].default_value = float(os.environ.get("HAZE", "0.000004"))
        pv.inputs["Color"].default_value = (0.75, 0.83, 0.95, 1)
        hn.links.new(pv.outputs[0], hn.nodes["Material Output"].inputs["Volume"])
        hz.data.materials.append(hm)
    return w, so

# ---------------------------------------------------------------- build
def build_set(M, year):
    """Called by scene.build() (hook) with scene.py's material dict. Builds the whole Trost scene."""
    t0 = time.time()
    _install()
    sc = bpy.context.scene
    M["hq_stone"] = stone_block_mat("HQSandstone", (0.50, 0.38, 0.21), (0.57, 0.44, 0.26), (0.26, 0.21, 0.14), scale=0.6)
    M["hq_slate"] = L.mat("HQSlate", (0.028, 0.03, 0.034), 0.95, var=0.15, var_scale=0.6, color2=(0.045, 0.047, 0.05))
    M["basin_stone"] = stone_block_mat("BasinStone", (0.27, 0.25, 0.20), (0.32, 0.29, 0.23), (0.12, 0.11, 0.09),
                                       scale=0.55, damp=0.7, moss=0.6)
    M["step_edge"] = L.mat("StepEdge", (0.10, 0.095, 0.08), 0.9)
    for k, col in enumerate(((0.50, 0.21, 0.07), (0.42, 0.11, 0.05), (0.26, 0.13, 0.06), (0.30, 0.08, 0.05),
                             (0.46, 0.29, 0.10), (0.55, 0.27, 0.14), (0.36, 0.17, 0.08))):
        M[f"roof_t{k}"] = L.tile_roof_mat(f"RoofT{k}", col)
    M["roof_turret"] = L.mat("RoofTurret", (0.09, 0.11, 0.15), 0.75, var=0.1, var_scale=0.5)
    M["clock"] = L.mat("ClockFace", (0.85, 0.82, 0.70), 0.6)
    M["moss_floor"] = L.mat("MossFloor", (0.11, 0.13, 0.08), 0.95, var=0.25, var_scale=0.18, color2=(0.20, 0.21, 0.14))
    M["plank"] = L.mat("Plank", (0.30, 0.20, 0.11), 0.8, var=0.2, var_scale=0.6)
    M["crate"] = L.mat("Crate", (0.26, 0.15, 0.07), 0.85, var=0.2, var_scale=0.9)
    M["gas"] = L.mat("GasTank", (0.42, 0.45, 0.48), 0.35)
    M["roof_flat"] = L.mat("RoofFlat", (0.33, 0.29, 0.25), 0.9, var=0.15, var_scale=0.1)
    M["rock"] = marble_mat()
    M["rubble"] = L.mat("Rubble", (0.20, 0.18, 0.16), 0.95, var=0.2, var_scale=0.5)
    M["tarp"] = L.mat("Tarp", (0.45, 0.40, 0.28), 0.9)
    M["church_w"] = L.mat("ChurchWhite", (0.80, 0.76, 0.66), 0.85, var=0.1, var_scale=0.2)
    M["bronze"] = L.mat("Bronze", (0.30, 0.20, 0.08), 0.4)
    terrain = L.build_terrain(M)
    build_walls(M)
    build_lifts(M)
    hc = L.new_coll("HouseVariants")
    walls = ["plaster", "plaster_w", "plaster_o", "timber"]
    roofs = [f"roof_t{k}" for k in range(7)]                    # orange / red / brown variety across Trost
    rnd = random.Random(8)
    widths = []
    for i in range(40):
        w = rnd.uniform(7.5, 11); d = rnd.uniform(11, 15); h = rnd.choice((11, 14, 14, 17, 17, 20))
        me = L.house_mesh(f"TH{i}", w, d, h, d * 0.5, M, walls[i % 4], roofs[(i * 3) % 7], chimney=i % 3 == 0, hip=i % 6 == 0)
        hc.objects.link(bpy.data.objects.new(f"TH{i}", me))
        widths.append((w, d))
    pts, ttrees = town_points(len(widths), widths)
    L.scatter("Town", hc, pts, year)
    tc = L.new_coll("TreeVariants")
    for i, k in enumerate(["broad"] * 7 + ["conifer"] * 6):
        tc.objects.link(bpy.data.objects.new(f"T{i:02d}", L.tree_mesh(f"T{i:02d}", k, M, i)))
    L.gn_forest(terrain, tc)
    L.scatter("TownTrees", tc, ttrees, year)
    for o in list(hc.objects) + list(tc.objects):
        o.location = (0.0, 0.0, -5000.0)
    for k, (spts, hw) in enumerate(street_polylines()):
        L.flat_strip(f"TrostStreet{k}", spts, hw * 2, M["cobble"], z=0.10 + (k % 60) * 0.002)
    ix = INNER_GATE[0]
    L.flat_strip("RoadNorth", [(ix, 6)] + [(ix + math.sin(t / 9) * 120 * (t / 40), 6 + t * 120) for t in range(1, 60)], 9, M["dirt"])
    L.flat_strip("RoadOut", [OUTER_GATE] + [(math.sin(t / 7) * 90 * (t / 30), OUTER_GATE[1] - t * 120) for t in range(1, 50)], 8, M["dirt"])
    bmd = bmesh.new()
    cverts = [bmd.verts.new((x * 0.996, y * 0.996, 0.08)) for x, y in L.district_outline(10.0)]
    bmd.faces.new(cverts)
    L.obj_from_bm("DistrictGround", bmd, [M["dirt"]])
    L.disc_patch("Plaza", PLAZA[0], PLAZA[1], PLAZA[2], PLAZA[2], 0, M["cobble"], 0.17, round_=True)
    L.disc_patch("BoulderSquare", BOULDER_SQUARE[0], BOULDER_SQUARE[1], BOULDER_SQUARE[2], BOULDER_SQUARE[2], 0, M["cobble"], 0.17, round_=True)
    gx0, gy0, gx1, gy1 = INNER_GATE_SQUARE
    L.disc_patch("GateSquare", (gx0 + gx1) / 2, (gy0 + gy1) / 2, (gx1 - gx0) / 2, (gy1 - gy0) / 2 + 2, 0, M["cobble"], 0.17)
    L.disc_patch("OuterSquare", OUTER_GATE_SQUARE[0], OUTER_GATE_SQUARE[1], OUTER_GATE_SQUARE[2], OUTER_GATE_SQUARE[2], 0, M["cobble"], 0.17, round_=True)
    L.disc_patch("HQCourt", *hq_world(-HQ_KEEP / 2, -HQ_D / 2 - 8), (HQ_L + HQ_KEEP) / 2 + 6, 7, _HQ_ROT, M["cobble"], 0.17)
    L.canal(M)
    nb = build_bridges(M)
    build_hq(M)
    build_basin(M)
    build_church(M)
    build_boulder(M)
    build_wagon(M)
    build_fountain(M)
    w, so = _world(sc)
    try:
        L.LABEL_ANCHORS.clear(); L.LABEL_ANCHORS.update(LABELS)
    except Exception:
        pass
    print(f"[trost] set built: {len(pts)} houses, {len(street_polylines())} streets, {nb} bridges, {time.time() - t0:.1f} s")
    ctx = {"terrain": terrain, "height": L.height, "year": year, "sun": so, "world": w, "set": SET_NAME}
    for p in L.PLUGINS:
        if p is sys.modules.get(__name__) or getattr(p, "SET_NAME", None) == SET_NAME:
            continue
        if hasattr(p, "build"):
            try:
                p.build(M, year, ctx)
            except Exception as ex:
                import traceback; traceback.print_exc()
                print(f"[plugin {p.__name__}] build failed: {ex!r}")
    return M

# ---------------------------------------------------------------- stills runner (2nd -P script)
STILL_STATE = {"trost_hq_cut": dict(cutaway=True, lift=0.55), "trost_inner_gate": dict(wagon=False)}

def _stills_main():
    import argparse
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser(allow_abbrev=False)       # scene.py's --cam must not match --cams
    ap.add_argument("--stills", default="")
    ap.add_argument("--cams", default=",".join(CAMS))
    a, _ = ap.parse_known_args(argv)
    if not a.stills:
        return
    os.makedirs(a.stills, exist_ok=True)
    sc = bpy.context.scene; cam = sc.camera
    if sc.render.engine.startswith("BLENDER_EEVEE"):           # readable sky views: sun shadows + AO
        ev = sc.eevee
        for k_, v_ in (("taa_render_samples", 8), ("use_shadows", True), ("shadow_pool_size", "1024"), ("shadow_resolution_scale", 1.0),
                       ("use_raytracing", True), ("ray_tracing_method", "SCREEN"), ("use_fast_gi", True),
                       ("fast_gi_method", "AMBIENT_OCCLUSION_ONLY"), ("fast_gi_distance", 6.0)):
            try:
                setattr(ev, k_, v_)
            except Exception:
                pass
        for o in bpy.data.objects:
            if o.type == "LIGHT" and o.data.type == "SUN":
                o.data.angle = math.radians(1.2)
        for n in ("Haze",):
            o = bpy.data.objects.get(n)
            if o:
                o.hide_render = True
    for name in a.cams.split(","):
        loc, tgt, lens = CAMS[name]
        cam.location = loc; cam.data.lens = lens
        cam.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
        st = STILL_STATE.get(name, {})
        set_hq_cutaway(st.get("cutaway", False)); set_hq_lift(st.get("lift", 0.0)); set_wagon(st.get("wagon", False))
        sc.render.filepath = os.path.join(a.stills, name + ".png")
        t = time.time()
        bpy.ops.render.render(write_still=True)
        print(f"[trost] still {name}: {time.time() - t:.1f} s")

if __name__ == "__main__":
    import trost as _T
    _T._stills_main()
