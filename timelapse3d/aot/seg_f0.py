"""f0 TROST -> ALONG WALL ROSE -> KARANES (part 2 opener, frame M on the Trost set).  SEG=f0 bash aot/forest/render_part2.sh
One take from part 1's last frame: g8's end state is rebuilt and frozen (seg_g8.build + update(DUR)), the camera leaves g8 E2
at rest, climbs over Trost, turns east and races along Wall Rose at ~3 km/s (2-3 km up, the ring reads like the map) while the
light runs golden -> dusk -> moonlit night -> dawn -> morning (the month before the 57th expedition), then drops toward the
Karanes bulge = f1 frame 0.  The forest set's objects (Karanes, old town, village, forest) are built here too under a root at
W -> set (0, -5000), so the f0|f1 seam frame matches.
"""
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
BEATS = dict(leave=0.0, golden_end=1.0, dusk=2.8, night=(4.6, 5.6), dawn=7.6, morning=10.0, seam=DUR)

def ring_M(theta_deg, r=19000.0, z=0.0):
    a = math.radians(theta_deg)
    return (r * math.cos(a), 19870.0 + r * math.sin(a), z)

# seam with f1 (frame W): f1 reads these
SEAM_F1_W = dict(pos=(19150.0, 22900.0, 700.0), look=(19870.0, 24000.0, 0.0), lens=28.0, vel=(25.0, 40.0, -20.0))
def _wm(p):
    return (p[0], p[1] - C.M_OFF_Y, p[2])
CAM_KEYS = [
    (0.0,  (200.0, 760.0, 240.0), (-20.0, 300.0, 0.0), 28.0),             # = g8 E2 (part 1 END), at rest
    (0.8,  (300.0, 720.0, 420.0), (700.0, -300.0, 0.0), 28.0),               # swing the look SE first (no yaw flip)
    (1.6,  (520.0, 640.0, 720.0), (3300.0, 1300.0, 60.0), 28.0),          # climb, turn east along the wall
    (3.2,  ring_M(-78, 18300, 2200), ring_M(-62), 28.0),
    (5.0,  ring_M(-58, 18300, 3000), ring_M(-42), 27.0),
    (6.8,  ring_M(-36, 18300, 3000), ring_M(-20), 27.0),
    (8.6,  ring_M(-16, 18400, 2200), (19870.0, 19870.0, 0.0), 28.0),
    (10.4, (18650.0, 17600.0, 1200.0), (19870.0, 19870.0, 0.0), 28.0),
    (DUR,  _wm(SEAM_F1_W["pos"]), _wm(SEAM_F1_W["look"]), SEAM_F1_W["lens"]),
]
CAM = camchan.CamPath(CAM_KEYS, v_in=(0.0, 0.0, 0.0), v_out=SEAM_F1_W["vel"])
CAM_LIMITS = dict(speed=4500.0, yaw=60.0, hmin=60.0, hmax=3600.0, pitch=(5.0, 60.0), lens=(26.0, 30.0))
PLAN = [(0.0, "golden"), (1.0, "golden"), (2.8, "dusk"), (4.6, "night"), (5.6, "night"), (7.6, "dawn"), (10.0, "morning"), (DUR, "morning")]
LIGHT = C.LightRig(*C.light_plan(PLAN))
S = {}

def build(site):
    S["site"] = site
    try:
        import seg_g8
        seg_g8.build(site)
        seg_g8.update(seg_g8.DUR)
        S["g8"] = seg_g8
        print("[f0] g8 end state rebuilt (frozen at its DUR)", flush=True)
    except Exception as ex:
        import traceback; traceback.print_exc()
        print("[f0] g8 end state FAILED:", ex, flush=True)
    from forest import fset
    root = bpy.data.objects.new("F0_WorldRoot", None); bpy.context.scene.collection.objects.link(root)
    root.location = (0.0, -5000.0, 0.0)                      # W -> Trost set
    fset.build_all(fset.scene_mats(), root)
    fset.gate_open(0.0)

def finish():
    g8 = S.get("g8")
    if g8 is not None and hasattr(g8, "finish"):
        try:
            g8.finish()
        except Exception as ex:
            print("[f0] g8.finish failed:", ex)

def update(t):
    from forest import fset
    fset.mills(t)

def light(t):
    LIGHT.apply(t)

def check():
    for t in (0.0, 3.0, 5.0, 7.0, 9.0, 11.0, DUR):
        loc, look, lens = CAM.eval(t)
        print(f"[f0] t {t:4.1f} cam M ({loc[0]:7.0f} {loc[1]:7.0f} {loc[2]:5.0f}) lens {lens:.1f}")
