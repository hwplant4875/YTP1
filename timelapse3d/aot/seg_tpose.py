"""v14 POSE CHECK for the frozen-tableau toolkit (not in the cut): one still per pose, 3/4 front view, tableau.TrackCam.
SEG=tpose RES=480x270 STILLS="0,1,2,..." bash aot/forest/render_part2.sh
  0..NF-1   Female POSE_F (in order)    NF..      Eren tableau specs      last   Scouts (flung, hang, swung, run, crouch)"""
import math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from forest import common as C
from forest import tableau as TB
try:
    import bpy
except ImportError:
    bpy = None

FN = list(TB.POSE_F)
EN = ["faceoff", "punch", "mount", "wait"]
VAR = None
if os.environ.get("TP_JSON"):                 # variant sweep: [[label, {bone: [x, y, z]}, pitch_deg], ...] (Female only)
    import json
    VAR = json.load(open(os.environ["TP_JSON"]))
    FN = [v[0] for v in VAR]; EN = []
DUR = float(len(FN) + len(EN) + 1)
BEATS = dict(test=0.0)
P0 = C.F(150.0, -8600.0)
CAM = None
S = {}

def build(site):
    global CAM
    z0 = C.G(P0[0], P0[1])
    shots = []
    for i in range(int(DUR)):
        dz = 7.0 if i < len(FN) + len(EN) else 1.0
        dist = (30.0 if VAR else 42.0) if i < len(FN) + len(EN) else 9.0
        tgt = (P0[0], P0[1], z0 + dz) if i < len(FN) + len(EN) else (P0[0] + 40, P0[1], z0 + 1.0)
        shots.append(TB.Shot(f"p{i}", i - 0.3, i + 0.3, tgt, az=(55, 65), dist=dist, el=12, lens=35))
    CAM = TB.make_cam(shots)
    globals()["CAM"] = CAM
    c = C.coll("TPose")
    S["fem"] = C.Female("TP_Female")
    S["eren"] = C.Eren("TP_Eren")
    S["eren"].show(False)
    import seg_g6 as G6
    S["E"] = TB.eren_specs(G6, S["eren"].P)
    B = C.Batch("TP_Scouts", C.RIDER_MATS)
    for k in range(5):
        C.person_geo(B.g, B.new(pivot=0.9))
    B.build(c); S["B"] = B
    for k, m in enumerate(("flung", "hang", "swung", "run", "crouch")):
        B.pos[k] = (P0[0] + 36 + 2.0 * k, P0[1], z0 + 1.0); B.yaw[k] = 0.0
        TB.scout_pose(B, k, m)
    B.push()
    S["z0"] = z0
    S["light"] = C.LightRig(*C.light_plan([(0.0, "day")]))

def update(t):
    i = int(round(t)); z0 = S["z0"]
    fem, er = S["fem"], S["eren"]
    if i < len(FN):
        nm = FN[i]
        fem.show(True); er.show(False)
        if VAR:
            fem.pose({k: tuple(v) for k, v in VAR[i][1].items()})
            fem.place(P0[0], P0[1], z0 + VAR[i][3] if len(VAR[i]) > 3 else z0, 0.0, pitch=math.radians(VAR[i][2]))
        else:
            fem.pose(TB.POSE_F[nm])
            pitch = math.pi / 2 if nm == "down" else 0.0
            fem.place(P0[0], P0[1], z0 + TB.FZ_T.get(nm, 0.0) + (2.0 if nm == "down" else 0.0), 0.0, pitch=pitch)
        print(f"[tpose] {i} female {nm}")
    elif i < len(FN) + len(EN):
        nm = EN[i - len(FN)]
        fem.show(False); er.show(True)
        er.pose(S["E"][nm]); er.place(P0[0], P0[1], z0, 0.0)
        print(f"[tpose] {i} eren {nm}")
    else:
        fem.show(False); er.show(False)

def light(t):
    S["light"].apply(t)
