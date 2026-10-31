"""FROZEN-TABLEAU TOOLKIT (FEEDBACK_v13 principle B, v14).

From the Female Titan onward the key moments are FROZEN-TIME 3D stills posed like the anime frame.  The camera tracks the
frozen subject (look = a fixed target point = Blender "Track To" on an empty) and moves slowly for 2-3 s (partial orbit
and/or dolly, never 360 deg), then flies ULTRA-FAST to the next tableau.

  shots = [Shot("ram", 3.0, 5.6, target, az=(200, 235), dist=(90, 70), el=(14, 18), lens=40), ...]
  CAM   = TableauCam(shots, fly_keys)   camchan.CamPath through the orbit samples + free fly keys between shots
  Stage("ram", 2.6, 6.0)              object group shown only in its window (pops happen during the fast fly)
  POSE_F / POSE_E / scout_pose()      pose library for the Female (FK eulers), Eren (attack_titan IK specs), Scouts (Batch)

Everything here is plain math + bpy visibility; the seg module owns placement.  Pose check: SEG=tpose (seg_tpose.py).
"""
import math
import numpy as np
from . import common as C
try:
    import bpy
except ImportError:
    bpy = None

# ---------------------------------------------------------------- camera: orbit / dolly around a frozen target
class Shot:
    """t0..t1 video seconds; target (x, y, z) world; az (deg, CCW from +x, camera position around the target), dist (m),
    el (deg above the horizon) and lens (mm) each a scalar or (start, end).  The camera always looks at the target."""
    def __init__(self, name, t0, t1, target, az, dist, el, lens, look_dz=0.0):
        self.name, self.t0, self.t1 = name, float(t0), float(t1)
        self.target = tuple(float(v) for v in target)
        self.az, self.dist, self.el, self.lens = (_pair(az), _pair(dist), _pair(el), _pair(lens))
        self.look_dz = look_dz

    def at(self, u):
        """camera pos, look, lens at shot fraction u (0..1), eased (slow in / slow out = an edit shot)."""
        e = u * u * (3 - 2 * u) * 0.6 + u * 0.4
        a = math.radians(_lerp(self.az, e)); r = _lerp(self.dist, e); el = math.radians(_lerp(self.el, e))
        tx, ty, tz = self.target
        p = (tx + r * math.cos(el) * math.cos(a), ty + r * math.cos(el) * math.sin(a), tz + r * math.sin(el))
        return p, (tx, ty, tz + self.look_dz), _lerp(self.lens, e)

    def keys(self, n=4):
        return [(self.t0 + (self.t1 - self.t0) * k / (n - 1),) + self.at(k / (n - 1)) for k in range(n)]

def _pair(v):
    return (float(v[0]), float(v[1])) if isinstance(v, (tuple, list)) else (float(v), float(v))

def _lerp(p, u):
    return p[0] + (p[1] - p[0]) * u

def tableau_keys(items, n=4):
    """items: Shot objects and plain camera keys (t, pos, look, lens) in any order -> sorted key list for camchan.CamPath."""
    keys = []
    for it in items:
        keys += it.keys(n) if isinstance(it, Shot) else [tuple(it)]
    keys.sort(key=lambda k: k[0])
    out = []
    for k in keys:
        if out and abs(k[0] - out[-1][0]) < 1e-3:
            continue
        out.append(k)
    return out

class TrackCam:
    """CamPath for the fly + a hard Track-To inside every shot: inside [t0, t1] the look point IS the shot target (no
    spline overshoot), the position/lens come from the shot's own orbit; outside, the fly path.  eval(t) -> (loc, look, lens)."""
    def __init__(self, path, shots, ease=0.18):
        self.path, self.shots, self.ease = path, shots, ease
        self.t0, self.t1 = path.t0, path.t1
        self.notes = list(getattr(path, "notes", [])) + ["tableau.TrackCam: shots locked on their targets"]

    def eval(self, t):
        loc, look, lens = self.path.eval(t)
        for s in self.shots:
            if s.t0 - self.ease <= t <= s.t1 + self.ease:
                u = min(1.0, max(0.0, (t - s.t0) / max(1e-6, s.t1 - s.t0)))
                p, l, ln = s.at(u)
                w = C.ss(s.t0 - self.ease, s.t0, t) * (1.0 - C.ss(s.t1, s.t1 + self.ease, t))
                loc = tuple(np.array(loc) + (np.array(p) - np.array(loc)) * w)
                look = tuple(np.array(look) + (np.array(l) - np.array(look)) * w)
                lens = lens + (ln - lens) * w
                break
        return loc, look, lens

def make_cam(items, v_in=None, v_out=None, n=4):
    import camchan
    shots = [it for it in items if isinstance(it, Shot)]
    path = camchan.CamPath(tableau_keys(items, n), v_in=v_in, v_out=v_out)
    return TrackCam(path, shots)

def track_empty(name, target):
    """the Blender empty a Track-To camera would aim at (kept in the file for inspection; the driver uses its location)."""
    ob = bpy.data.objects.get(name) or bpy.data.objects.new(name, None)
    if ob.name not in bpy.context.scene.collection.objects:
        try:
            bpy.context.scene.collection.objects.link(ob)
        except RuntimeError:
            pass
    ob.location = target; ob.empty_display_size = 3.0
    return ob

# ---------------------------------------------------------------- frozen story clock
def hold_clock(segments):
    """segments [(v0, v1, s0, s1)]: video v0..v1 maps story s0..s1 (s0 == s1 = frozen).  Returns story(t)."""
    V, S = [], []
    for v0, v1, s0, s1 in segments:
        V += [v0, v1]; S += [s0, s1]
    V = np.array(V); S = np.array(S)
    def story(t):
        return float(np.interp(t, V, S))
    return story

# ---------------------------------------------------------------- stages (object groups per tableau)
class Stage:
    def __init__(self, name, t0, t1):
        self.name, self.t0, self.t1, self.objs, self.on = name, t0, t1, [], None

    def add(self, *obs):
        for o in obs:
            self.objs += list(o) if isinstance(o, (list, tuple)) else [o]
        return self

    def update(self, t):
        on = self.t0 <= t <= self.t1
        if on != self.on:
            for o in self.objs:
                C.hide(o, not on)
            self.on = on
        return on

# ---------------------------------------------------------------- pose libraries
# Female FK (degrees added to the relaxed base; signs calibrated in seg_ftest, see common.FPOSE): upperleg x+ = thigh BACK,
# lowerleg x+ = knee flex, spine x+ = lean forward, upperarm x+ = arm forward/up, lowerarm x+ = elbow flex, neck x+ = head
# down; upperarm z: L - = down / + = out-up, R + = down / - = out-up.  Checked with SEG=tpose stills (270p).
POSE_F = {
    # EP17 10:13: shoulder-ram through a Scout at a run, the other arm yanking a second Scout's wire overhead like a rod
    "ram": {"upperleg01.L": (-55, 0, 0), "lowerleg01.L": (35, 0, 0), "upperleg01.R": (30, 0, 0), "lowerleg01.R": (70, 0, 0),
            "foot.L": (-10, 0, 0), "spine01": (18, 0, 0), "spine02": (10, 0, 12), "spine03": (8, 0, 10), "neck01": (-12, 0, 0),
            "upperarm01.R": (25, 0, 35), "lowerarm01.R": (95, 0, 0),
            "upperarm01.L": (150, 0, 25), "lowerarm01.L": (35, 0, 0)},
    # lifting Armin's hood: kneeling, right hand low and forward, head bowed to look
    "hood": {"upperleg01.L": (-85, 0, 0), "lowerleg01.L": (90, 0, 0), "upperleg01.R": (-5, 0, 0), "lowerleg01.R": (118, 0, 0),
             "foot.R": (40, 0, 0), "spine01": (28, 0, 0), "spine02": (20, 0, 0), "spine03": (14, 0, 0), "neck01": (35, 0, 0),
             "head": (15, 0, 0), "upperarm01.R": (55, 0, 5), "lowerarm01.R": (25, 0, 0), "upperarm01.L": (15, 0, -10),
             "lowerarm01.L": (40, 0, 0)},
    # EP17 21:38: kneeling, looking at her smoking right palm held up before her face
    "palm": {"upperleg01.L": (-85, 0, 0), "lowerleg01.L": (90, 0, 0), "upperleg01.R": (-5, 0, 0), "lowerleg01.R": (118, 0, 0),
             "foot.R": (40, 0, 0), "spine01": (14, 0, 0), "spine02": (8, 0, 0), "neck01": (28, 0, 0), "head": (12, 0, 0),
             "upperarm01.R": (65, 0, 15), "lowerarm01.R": (115, 0, 0), "upperarm01.L": (10, 0, -5), "lowerarm01.L": (25, 0, 0)},
    # EP18 10:59: walking, the right arm raised, swinging a Scout round on his wire (fire-can spin)
    "swing": {"upperleg01.L": (-28, 0, 0), "lowerleg01.L": (15, 0, 0), "upperleg01.R": (18, 0, 0), "lowerleg01.R": (30, 0, 0),
              "spine01": (4, 0, 0), "neck01": (-6, 0, 0), "upperarm01.R": (160, 0, -20), "lowerarm01.R": (10, 0, 0),
              "upperarm01.L": (-10, 0, -8), "lowerarm01.L": (25, 0, 0)},
    # full sprint (forest chase, behind the riders)
    "sprint": {"upperleg01.L": (-70, 0, 0), "lowerleg01.L": (45, 0, 0), "upperleg01.R": (40, 0, 0), "lowerleg01.R": (95, 0, 0),
               "foot.L": (-10, 0, 0), "foot.R": (20, 0, 0), "spine01": (16, 0, 0), "spine02": (12, 0, 0), "spine03": (8, 0, 0),
               "neck01": (-22, 0, 0), "head": (-8, 0, 0), "upperarm01.L": (60, 0, 0), "lowerarm01.L": (80, 0, 0),
               "upperarm01.R": (-45, 0, 0), "lowerarm01.R": (70, 0, 0)},
    # EP20: pinned by the wire trap, both arms raised and wrapped round the back of the neck, hands overlapping on the nape
    "nape": {"upperarm01.L": (165, 0, -15), "lowerarm01.L": (155, 0, 0), "upperarm01.R": (165, 0, 15), "lowerarm01.R": (155, 0, 0),
             "neck01": (22, 0, 0), "head": (8, 0, 0), "spine01": (5, 0, 0),
             "upperleg01.L": (-6, 0, -4), "upperleg01.R": (4, 0, 4), "lowerleg01.L": (8, 0, 0), "lowerleg01.R": (8, 0, 0)},
    # EP21 08:15: facing off, fighting guard
    "faceoff": {"upperarm01.L": (85, 0, 20), "lowerarm01.L": (120, 0, 0), "upperarm01.R": (70, 0, -20), "lowerarm01.R": (125, 0, 0),
                "spine01": (10, 0, 0), "neck01": (-6, 0, 0), "upperleg01.L": (-25, 0, -6), "lowerleg01.L": (25, 0, 0),
                "upperleg01.R": (18, 0, 6), "lowerleg01.R": (22, 0, 0)},
    # EP21 19:19: right foot planted, LEFT leg in a diagonal high kick up-right, torso leaning back, fists clenched at the chest
    "highkick": {"upperleg01.L": (-125, 0, -30), "lowerleg01.L": (0, 0, 0), "foot.L": (-25, 0, 0),
                 "upperleg01.R": (8, 0, 6), "lowerleg01.R": (12, 0, 0),
                 "spine01": (-18, 0, -18), "spine02": (-8, 0, -10), "neck01": (8, 0, 0),
                 "upperarm01.L": (45, 0, 10), "lowerarm01.L": (120, 0, 0), "upperarm01.R": (35, 0, 15), "lowerarm01.R": (125, 0, 0)},
    # EP22 07:15: sitting slumped against a tree, head tipped back, jaw open, arms limp
    "slump": {"upperleg01.L": (-80, 0, -14), "lowerleg01.L": (40, 0, 0), "upperleg01.R": (-85, 0, 12), "lowerleg01.R": (70, 0, 0),
              "spine01": (-14, 0, 0), "spine02": (-8, 0, 4), "neck01": (-22, 0, 10), "head": (-12, 0, 0), "jaw": (22, 0, 0),
              "upperarm01.L": (-6, 0, -6), "lowerarm01.L": (18, 0, 0), "upperarm01.R": (-6, 0, 6), "lowerarm01.R": (18, 0, 0)},
    # Stohess: climbing the wall face (the rig is placed facing the wall), arms high on hardened finger holds
    "climb": {"upperarm01.L": (165, 0, 12), "lowerarm01.L": (20, 0, 0), "upperarm01.R": (150, 0, -10), "lowerarm01.R": (35, 0, 0),
              "upperleg01.L": (-55, 0, 0), "lowerleg01.L": (85, 0, 0), "upperleg01.R": (5, 0, 0), "lowerleg01.R": (20, 0, 0),
              "neck01": (-25, 0, 0), "spine01": (-4, 0, 0)},
    # EP24 22:00: knocked airborne by the punch, head snapped back, arms flung
    "punched": {"spine01": (-20, 0, 10), "spine02": (-12, 0, 6), "neck01": (-35, 0, 15), "head": (-10, 0, 0), "jaw": (12, 0, 0),
                "upperarm01.L": (60, 0, 50), "lowerarm01.L": (30, 0, 0), "upperarm01.R": (30, 0, -60), "lowerarm01.R": (20, 0, 0),
                "upperleg01.L": (-35, 0, 0), "lowerleg01.L": (50, 0, 0), "upperleg01.R": (20, 0, 0), "lowerleg01.R": (40, 0, 0)},
    # EP25 13:24: on her back under Eren (rig pitched +90 deg), arms out, one knee up
    "down": {"upperarm01.L": (20, 0, 50), "lowerarm01.L": (20, 0, 0), "upperarm01.R": (25, 0, -55), "lowerarm01.R": (25, 0, 0),
             "upperleg01.L": (-40, 0, -8), "lowerleg01.L": (60, 0, 0), "upperleg01.R": (-5, 0, 6), "lowerleg01.R": (8, 0, 0),
             "neck01": (-10, 0, 0), "jaw": (10, 0, 0)},
}
FZ_T = dict(hood=-3.6, palm=-3.6, slump=-5.0, nape=0.0)

def eren_specs(G6, P):
    """Eren's tableau poses (attack_titan IK specs) from seg_g6.make_poses() P."""
    return {"faceoff": P["boxer"], "punch": P["jab"], "wait": P["stand"], "mount": P["bite"], "run": P["run"],
            "headless": P["lie"]}

# Scouts (common.person_geo Batch: parts 1/2 legs, 3/4 arms; Ar = swing about x, pitch = whole-body lean, roll = side tilt)
def scout_pose(B, j, mode):
    B.Ar[j, :] = 0.0; B.Ae[j, :] = 0.0; B.lean[j] = 0.0; B.pitch[j] = 0.0; B.roll[j] = 0.0
    if mode == "flung":            # tumbling through the air, limbs spread
        B.Ar[j, 1] = 0.9; B.Ar[j, 2] = -0.6; B.Ar[j, 3] = -2.2; B.Ar[j, 4] = 1.4; B.pitch[j] = -0.9; B.roll[j] = 0.7
    elif mode == "hang":           # hanging on his wire, arms up
        B.Ar[j, 3] = B.Ar[j, 4] = -2.8; B.Ar[j, 1] = 0.3; B.Ar[j, 2] = -0.2
    elif mode == "swung":          # swung out horizontally on the wire (fire-can spin), arms toward the pivot
        B.Ar[j, 3] = B.Ar[j, 4] = -2.9; B.Ar[j, 1] = 0.25; B.Ar[j, 2] = -0.1; B.pitch[j] = -1.35
    elif mode == "run":
        B.Ar[j, 1] = 0.7; B.Ar[j, 2] = -0.7; B.Ar[j, 3] = -0.6; B.Ar[j, 4] = 0.6; B.pitch[j] = -0.2
    elif mode == "fly":
        B.Ar[j, 1] = 0.25; B.Ar[j, 2] = 0.55; B.Ar[j, 3] = B.Ar[j, 4] = -2.4; B.pitch[j] = -1.1
    elif mode == "seated":
        B.Ar[j, 1] = B.Ar[j, 2] = 1.35; B.Ar[j, 3] = B.Ar[j, 4] = 0.5
    elif mode == "fallen":
        B.Ar[j, :] = 0.3; B.pitch[j] = -1.45
    elif mode == "crouch":
        B.Ar[j, 1] = B.Ar[j, 2] = 1.2; B.Ar[j, 3] = B.Ar[j, 4] = 0.6; B.pitch[j] = -0.3
