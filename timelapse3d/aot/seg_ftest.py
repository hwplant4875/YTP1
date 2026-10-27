"""PART 2 calibration stills (not in the cut): Female bone-sign test, Eren pose, rider + titan batches, set look.
SEG=ftest STILLS="0,1,2,3,4,5,6,7,8,9,10,11" bash aot/forest/render_part2.sh"""
import math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from forest import common as C
import camchan
try:
    import bpy
except ImportError:
    bpy = None

DUR = 12.0
BEATS = dict(test=0.0)
P0 = C.F(150.0, -8600.0)
TESTS = [{}, {"upperleg01.L": (40, 0, 0)}, {"lowerleg01.L": (40, 0, 0)}, {"spine03": (30, 0, 0)},
         {"upperarm01.L": (40, 0, 0)}, {"upperarm01.L": (0, 0, 40)}, {"lowerarm01.L": (40, 0, 0)}, {"neck01": (30, 0, 0)},
         {"upperarm01.L": (0, 40, 0)}, {}, {}, {}]
CAM = None
S = {}

def build(site):
    global CAM
    z0 = C.G(P0[0], P0[1])
    keys = []
    for i in range(9):
        keys.append((float(i), (P0[0] + 34, P0[1] - 8, z0 + 9), (P0[0], P0[1], z0 + 7), 35.0))
    keys.append((9.0, (P0[0] + 30, P0[1] + 40, z0 + 12), (P0[0] + 30, P0[1] + 10, z0 + 7), 35.0))   # Eren
    keys.append((10.0, (P0[0] + 60, P0[1] - 60, z0 + 40), (P0[0] + 60, P0[1] - 20, z0 + 2), 30.0))   # batches
    keys.append((11.0, (19300.0, 23300.0, 600.0), (19870.0, 24000.0, 30.0), 28.0))                  # Karanes
    CAM = camchan.CamPath(keys)
    globals()["CAM"] = CAM
    c = C.coll("FTest")
    S["fem"] = C.Female()
    S["fem"].place(P0[0], P0[1], z0, 0.0)
    S["eren"] = C.Eren()
    S["eren"].pose(S["eren"].P["run"]); S["eren"].place(P0[0] + 30, P0[1] + 10, z0, math.pi)
    B = C.Batch("FT_Riders", C.RIDER_MATS)
    for k in range(6):
        j = B.new(); C.rider_geo(B.g, j)
    j = B.new(); C.wagon_geo(B.g, j)
    B.build(c)
    for k in range(7):
        B.pos[k] = (P0[0] + 50 + 4 * k, P0[1] - 20, z0); B.yaw[k] = 0.0
        B.Ar[k, 1] = 0.5 * math.sin(k); B.Ar[k, 2] = -0.5 * math.sin(k)
    B.pos[6] = (P0[0] + 50, P0[1] - 35, z0)
    B.push()
    T = C.Batch("FT_Titans", C.titan_mats())
    for k in range(4):
        C.titan_add(T, dict(H=6 + 2 * k, skin=k, hair=k % 2))
    T.build(c)
    for k in range(4):
        T.pos[k] = (P0[0] + 70 + 12 * k, P0[1] - 10, z0); C.titan_walk(T, k, k * 0.8)
    T.push()
    S["light"] = C.LightRig(*C.light_plan([(0.0, "day")]))

def update(t):
    i = int(round(t))
    S["fem"].pose(TESTS[i] if i < len(TESTS) else {})

def light(t):
    S["light"].apply(t)
