"""s1 v15 (STOHESS_v15.md): the month-passing flight to Stohess, then the SAME high sky camera as s2v15 for the
Female's lightning and her rampage (no stairway walk / underground passage / Plan C close-ups; Female x1.5).
Reuses seg_s1's set pieces and animation on a new video clock.   SEG=s1v15 bash aot/forest/render_part2.sh
"""
import math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from forest import common as C
from stohess.layout import S
import camchan
import seg_s1 as S1
import seg_s2v15 as S2V

def _raw(fn):
    """seg_s1's update / light before its install_warp wrapper (story clock)."""
    cl = dict(zip(fn.__code__.co_freevars, (c.cell_contents for c in fn.__closure__ or ())))
    return cl.get("upd") or cl.get("lt") or fn
_UPD, _LT = _raw(S1.update), _raw(S1.light)

# video -> story: flight x2.8, jump over the walk, lightning + rise, jump over Plan C, rampage x2.5
TMAP = [(0.0, 0.0), (3.6, 9.0), (3.9, 15.8), (6.6, 20.8), (6.9, 24.0), (9.3, 30.0)]
DUR = TMAP[-1][0]
def story(t):
    return float(np.interp(t, [k[0] for k in TMAP], [k[1] for k in TMAP]))
BEATS = dict(flight=(0.0, 3.6), lightning=(4.0, 5.4), rampage=(6.9, 9.3))

H = S2V.H
def _k(t, p, l, lens):
    return (t, S(*p), S(*l), lens)
SEAM = S2V.SEAM_IN
CAM_KEYS = [
    (0.0, S1.SEAM_IN["pos"], S1.SEAM_IN["look"], S1.SEAM_IN["lens"]),
    (1.2, (16500.0, 29000.0, 1800.0), (13000.0, 24500.0, 0.0), 28.0),       # SW over Wall Rose, dusk -> night
    (2.3, (14100.0, 26000.0, 1200.0), (12650.0, 24050.0, 0.0), 28.0),       # dawn: Wall Sina ahead
    _k(3.8, (-380.0, 160.0, H), (-150.0, 50.0, 0.0), 38.0),                # the sky view: the stairway street
    _k(6.0, (-360.0, 90.0, H), (-130.0, 40.0, 0.0), 39.0),                 # her lightning in the street
    (DUR, SEAM["pos"], SEAM["look"], SEAM["lens"]),                        # her rampage east -> s2v15
]
LIFT_SKIP = (0, 1, 2)
CAM = camchan.CamPath(CAM_KEYS, v_in=S1.SEAM_IN["vel"], v_out=SEAM["vel"])
CAM_LIMITS = dict(speed=2500.0, yaw=120.0, hmin=30.0, hmax=2000.0, pitch=(5.0, 70.0), lens=(27.0, 43.0))
TRACK = {}

def build(site):
    global CAM
    import attack_titan as AT
    if not getattr(AT.shift_fx, "_v15", False):                  # shifter light at titan scale x1.5
        f0 = AT.shift_fx
        def sfx(x, y, t, frame=None, seed=11, scale=1.0):
            return f0(x, y, t, frame=frame, seed=seed, scale=scale * S2V.TS if scale == 1.0 else scale)
        sfx._v15 = True; AT.shift_fx = sfx
    S1.build(site)
    S1.S_["fem"].rig.scale = (S2V.TS, S2V.TS, S2V.TS)
    CAM = camchan.CamPath(C.lift_keys(CAM_KEYS, skip=LIFT_SKIP), v_in=S1.SEAM_IN["vel"], v_out=SEAM["vel"])

def update(t):
    _UPD(story(t))

def light(t):
    _LT(story(t))

def check():
    for t in (0.0, 3.2, 3.6, 5.0, 6.6, DUR):
        x, y = S1.fem_S(story(t))
        print(f"[s1v15] t {t:4.1f} story {story(t):5.1f} female S ({x:5.0f} {y:5.0f})")
