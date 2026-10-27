"""g3 FLIGHT NORTH, REFUGEE CAMPS, 846 MARCH, 104th CAMP (SCENE_BIBLE_v2 B.g3, 78.4 s; frames W -> M).
Driven by aot/render_seg.py (render_seg.sh).  Every frame is a pure function of the local time t (0..78.4).

TWO SETS (allowed by the lead: "separate sets per sub-part"), one camera:
  part A  t 0 .. BEATS["set_switch"]   SEG_SET=shiganshina (SEG_FRAME=W): the g2 end look (scene.py Shiganshina 845 + g1's
          plug-ins + g2's own canal / quays / ferries, imported from seg_g2), dusk -> night.  CAM is served in frame W.
  part B  set_switch .. 78.4           AOT_SET=trost (frame M): the night flight on, dawn, the relief complex / shelter camp /
          clearing at the Rose foot, the 846 gathering, march846 (its own simulation + spline, re-lit), the flight to the
          104th camp (camp104.py, shared with g4) and the camp beats.
  The switch sits at full night over open world ground (world.py's bit-identical layer + the g3 river, built the same way
  in both parts); neither town core is in frame then.  Part-B windows only build what their window can see (G3_PARTS, from
  the driver's --t0/--t1): march846 only for windows that touch 31.3-49.3, the camp only from 49.3 (it did not exist in 846).
    SEG=g3 SEG_SET=shiganshina WIN=0,6 bash render_seg.sh      part A
    SEG=g3 WIN=6,31.3 bash render_seg.sh  ... (part B windows) ; SEG=g3 ENCODE_ONLY=1 bash render_seg.sh

Story (group-local seconds; every time lives in BEATS, the ONE re-time table; camera keys are built from it):
  0-12.9   flight north at 240-380 m, explicit speed profile (45 -> 369 m/s by 3.7, cruise to 9.0, one deceleration to
           rest at H 17.7): ferries on the wide teal river below (0-3.7), girder bridges, night 5-9 (HUD "845: territory
           reduced to Wall Rose"), Trost window dots and wall-top torches, dawn 9-12.9
  12.9-17.7 over Wall Rose, decelerating to hover H above Trost's NW quarter
  17.7-21  clear sunny morning: the relief cloister packed with refugees, the ration booth queue, the shelter camp, the
           clearing beyond Rose (lens 28 -> 40)
  21-27.2  time-lapse winter 845 (grey overcast, snow, hoe lines) -> spring 846 while the view pans ~160 deg via the WEST;
           the avenue fills with the hooded 846 crowd (HUD "846: retake Wall Maria")
  27.2-31.3 run to CAM_IN (march846's own start)
  31.3-49.3 march846 (its simulation + its spline, unchanged), overcast, gold sunset over the SW ridge titans 42-49.3
  49.3-63.4 flight to the camp; 63.4 enlistment (250 recruits 10 x 25, SHADIS walking the front); 66.7-69.2 the rigs (EREN
           upside down on rig 2, MIKASA balanced on rig 1); 69.2-74.0 seasons x 3 (orbit); 74.0-78.4 graduation night
           (218 graduates 9 x ~23, the top 10 at the stair foot, braziers), drifting SE to the g4 seam (= g4 G0, unchanged)
"""
import math, os, random, sys, time
import numpy as np

try:
    import bpy, bmesh
    from mathutils import Vector, Matrix, Euler, noise
except ImportError:                       # pure-python use (camera checks)
    bpy = None

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import camchan
import camkeys
import segtime

DUR = segtime.DUR["g3"]                   # 78.4
PART = "A" if os.environ.get("SEG_FRAME", "M").upper() == "W" else "B"
MW = segtime.M_OFF_Y                      # M = W - (0, 4130)

# ====================================================================== BEATS (the ONE re-time table, local seconds)
BEATS = dict(
    # ---- flight (0-17.7): FA keys and the speed profile
    FA0=0.0, FA1=3.7, FA2=7.3, FA3=10.6, FA4=12.9, H=17.7,
    prof=(45.7, 369.0, 3.7, 9.0),          # v0 (= g2 seam |v|), cruise m/s, ramp end, cruise end (decel to rest at H)
    ferries=(0.0, 3.7),                    # ferries pass below
    set_switch=6.0,                        # part A (Shiganshina set) -> part B (Trost set), at full night over open ground
    dusk_night=(0.4, 5.0), night=(5.0, 9.0), dawn=(9.0, 12.9),
    hud_845=(5.2, 9.0),                    # "845: territory reduced to Wall Rose"
    lights_off=(9.6, 12.4),                # Trost window dots / torches fade
    # ---- camps (17.7-31.3)
    morning=(12.9, 17.7), H2=20.6, P1=22.4, P2=24.0, P3=25.6, H3=27.4, CAM_IN=31.3,
    courtyard=(14.0, 22.0),                # the relief cloister packed, ration queue busy
    winter=(20.2, 22.6), snow=(21.0, 24.2), spring=(23.6, 26.4),
    crowd846=(23.0, 27.2),                 # the hooded 846 crowd fills the avenue
    hud_846=(23.4, 27.2),                  # "846: retake Wall Maria"
    gate_open=(25.0, 27.0),
    # ---- march846 (31.3-49.3): its own clock tau = t - 31.3
    march=(31.3, 49.3), sunset=(41.3, 49.3),
    # ---- flight to the camp + the camp (49.3-78.4)
    FT0=49.3, FT1=55.8, FT2=60.2, FT3=63.4, FT4=66.7, FT5=69.2, FT6=74.0, FT7=78.4,
    camp_morning=(58.0, 63.4), enlist=(63.4, 66.7), rig=(66.7, 69.2), seasons=(69.2, 74.0), grad=(74.0, 78.4),
    tag_shadis=(63.8, 66.6), tag_eren=(66.9, 69.6), tag_mikasa=(67.3, 69.6),
)
B = BEATS

# ====================================================================== camera (bible keys; fixes per design_specs/camcheck_report.md)
def W2M(p):
    return (float(p[0]), float(p[1]) - MW, float(p[2]))

# flight: FA0..FA3 (W) + FA4, H (M), driven by the explicit speed profile (allowed speed exception), v_in = g2 seam direction
_S_IN = segtime.seam("g2_g3")
FLIGHT_KEYS = [(B["FA" + str(i)], W2M(c), W2M(l), ln) for i, (_, c, l, ln) in enumerate(camkeys.G3_FLIGHT_W)] + [
    (B["FA4"], (60.0, 170.0, 300.0), (-268.0, 805.0, 0.0), 30.0),          # FA4 = W (60, 4300, 300): over Wall Rose
    (B["H"], (-145.0, 605.0, 250.0), (-330.0, 1020.0, 0.0), 28.0)]          # H (at rest)
_PV = B["prof"]
FLIGHT = camchan.CamPath(FLIGHT_KEYS, v_in=_S_IN["vel"], profile=camchan.speed_profile(_PV[0], _PV[1], _PV[2], _PV[3], B["H"] - B["FA0"]))

# camps: H (rest) .. CAM_IN with the march846 entry velocity.  The pan is spread a little wider (H2 21.0 -> 20.6, P1-P3
# 22.55/24.1/25.65 -> 22.4/24.0/25.6, H3 27.2 -> 27.4; bible look-ats kept) so it peaks at 26.8 deg/s (camcheck: 31.9 at 26.4).
CI = camkeys.CAM_IN
_CK = camkeys.G3_CAMPS_M[1:8]                                       # H, H2, P1, P2, P3, H3, CAM_IN (positions / look-ats / lens)
CAMP_KEYS = [(B[n], tuple(map(float, k[1])), tuple(map(float, k[2])), float(k[3])) for n, k in zip(("H", "H2", "P1", "P2", "P3", "H3", "CAM_IN"), _CK)]
CAMPS = camchan.CamPath(CAMP_KEYS, v_in=(0.0, 0.0, 0.0), v_out=CI["vel"], look_v_out=CI["look_vel"])

# march846 camera.  march846.py's own spline (CAM_KEYS, a pure time Hermite) breaks the A3 limits inside g3 (camchan: 458 m/s,
# 57 deg/s, 81 m, pitch 11): it is re-driven HERE (march846.py untouched) on the same route with arc-length channels + an
# explicit speed profile (a flight exception like the g3 flight: ramp 64 -> ~290 m/s, slow 150-140 m/s over the low east-flank
# pass, ~290 back up, 95 m/s out), the low pass raised to 140-160 m (owner "far is better"), look-ats pulled in to keep
# pitch >= 17 and the yaw <= 30 deg/s; CAM_IN (position, look-at, lens, both velocities) and CAM_OUT (position, look-at, lens)
# are unchanged.  The CAM_OUT climb (0, 95, 22) -> level (0, 95, 0): with the climb the flight to the camp overshot 650 m
# (camcheck g3_to_camp 681 m).  Key positions: march846's (a outward from the gate = south, b lateral = east, z), set frame.
_MG, _MF, _MR = np.array([0.0, -870.0]), np.array([0.0, -1.0]), np.array([1.0, 0.0])
def _gp(a, b, z):
    p = _MG + _MF * a + _MR * b
    return (float(p[0]), float(p[1]), float(z))
MARCH_T_END = 18.0
MARCH_KEYS_SET = [                                                  # (tau, cam, look-at, lens) set frame; march846 keys in []
    (0.0,  _gp(-170, 170, 125),  _gp(60, -10, 0),    27),         # = march846 CAM_IN
    (1.8,  _gp(-60, 200, 135),   _gp(260, -10, 0),   27),         # = march846
    (3.6,  _gp(330, 240, 180),   _gp(800, -20, 0),   27),         # [3.4 (260,230,175) -> (980,-20)]
    (6.0,  _gp(1080, 340, 225),  _gp(1640, -40, 0),  28),         # [5.6 (1150,380,230) -> (2200,-40)]
    (8.0,  _gp(1720, 270, 160),  _gp(2100, -10, 0),  31),         # [7.6 (1780,260,120) -> (2080,0)]
    (10.0, _gp(2020, 200, 140),  _gp(2120, -220, 0), 33),         # [9.6 (2060,190,92) -> (2290,-15)] low east-flank pass
    (12.6, _gp(2080, 480, 350),  _gp(1950, -220, 0), 28),         # [12.2 (2150,950,400) -> (1700,-100)] rise, islands
    (15.2, _gp(1560, 520, 520),  (-300.0, -2000.0, 10.0), 28),    # [15.0 (1500,650,560) -> (700,0)]: toward the SW ridge + sun
    (18.0, _gp(1050, 260, 640),  _gp(-150, 0, 40),   28),         # = march846 CAM_OUT
]
MARCH_KNOTS = [(0.0, 63.6), (1.5, 80.0), (3.8, 300.0), (7.0, 300.0), (8.6, 150.0), (11.0, 140.0), (13.2, 290.0), (16.5, 260.0), (18.0, 95.0)]
MARCH_FREE = (2, 3, 6, 7)                                           # knots scaled so the profile covers the route exactly
MARCH_OUT_VEL = tuple(map(float, camkeys.CAM_OUT["vel"]))       # (0, 95, 0)

def shaped_profile(knots, free, total):
    """Progress fraction f(t) for a drive whose speed follows the PCHIP through knots [(t, v)] (start / end speeds fixed;
    the `free` knots are scaled by one factor so the distance equals `total`)."""
    ts = np.array([k[0] for k in knots], float)
    def build(k):
        vs = np.array([v * (k if i in free else 1.0) for i, (_, v) in enumerate(knots)])
        m = camchan.pchip_m(list(ts), list(vs)); m[0] = 0.0; m[-1] = 0.0
        tt = np.linspace(ts[0], ts[-1], 3601); vv = np.array([camchan.pchip(ts, vs, m, x) for x in tt])
        return tt, np.concatenate([[0.0], np.cumsum(0.5 * (vv[1:] + vv[:-1]) * np.diff(tt))])
    lo, hi = 0.05, 20.0
    for _ in range(50):
        k = (lo + hi) / 2
        if build(k)[1][-1] < total: lo = k
        else: hi = k
    tt, s = build((lo + hi) / 2)
    tt = tt - tt[0]; s = s / s[-1]
    return lambda t: float(np.interp(t, tt, s))

_T0M = B["march"][0]
MARCH_KEYS = [(_T0M + t, (c[0], c[1] + 870.0, c[2]), (l[0], l[1] + 870.0, l[2]), ln) for t, c, l, ln in MARCH_KEYS_SET]
_mk = dict(v_in=CI["vel"], look_v_in=CI["look_vel"], v_out=MARCH_OUT_VEL)
MARCH = camchan.CamPath(MARCH_KEYS, profile=shaped_profile(MARCH_KNOTS, MARCH_FREE, camchan.CamPath(MARCH_KEYS, **_mk).loc.total), **_mk)
MARCH_LOOK_OUT_VEL = tuple(float(x) for x in (MARCH.eval(B["march"][1])[1] - MARCH.eval(B["march"][1] - 1e-3)[1]) / 1e-3)

# flight to the camp: FT0 = march846.CAM_OUT (its velocity in, level, no overshoot: FT1 lowered 520 -> 420, FT2 20 m nearer: 294 m/s), the camp
# keys FT3-FT5 pulled BACK and UP to 150-185 m / 250-340 m out (owner 16:51 "far is better"; were 95 / 85 / 70 m), FT6-FT7 kept,
# FT7 = g4 G0 (segtime g3_g4, look-at at rest: g4 starts its look-at from rest).
CO = camkeys.CAM_OUT
TOCAMP_KEYS = [(B["FT%d" % i], tuple(map(float, k[1])), tuple(map(float, k[2])), float(k[3])) for i, k in enumerate(camkeys.G3_TO_CAMP_M)]
_S_OUT = segtime.seam("g3_g4")
TOCAMP = camchan.CamPath(TOCAMP_KEYS, v_in=MARCH_OUT_VEL, look_v_in=MARCH_LOOK_OUT_VEL, v_out=_S_OUT["vel"], look_v_out=(0.0, 0.0, 0.0))

class G3Cam:
    """The whole g3 camera in frame M (piecewise: flight profile | camps | march846 spline | to camp); off = frame shift
    added to every point (part A serves frame W = M + (0, 4130))."""
    def __init__(self, off=(0.0, 0.0, 0.0)):
        self.off = np.array(off, float); self.t0, self.t1 = 0.0, DUR
        self.notes = FLIGHT.notes + CAMPS.notes + MARCH.notes + TOCAMP.notes
    def eval_m(self, t):
        t = min(max(float(t), 0.0), DUR)
        if t <= B["H"]:
            loc, look, lens = FLIGHT.eval(t)
        elif t <= B["CAM_IN"]:
            loc, look, lens = CAMPS.eval(t)
        elif t <= B["march"][1]:
            loc, look, lens = MARCH.eval(t)
        else:
            loc, look, lens = TOCAMP.eval(t)
        return np.asarray(loc, float), np.asarray(look, float), float(lens)
    def eval(self, t):
        loc, look, lens = self.eval_m(t)
        return loc + self.off, look + self.off, lens
    def vel(self, t, h=1 / 120):
        a, b = max(self.t0, t - h), min(self.t1, t + h)
        return (self.eval(b)[0] - self.eval(a)[0]) / (b - a)

CAM_M = G3Cam()
CAM = G3Cam((0.0, MW, 0.0)) if PART == "A" else CAM_M
# the A3 limits with the bible's g3 exceptions: the flight's explicit profile (369 m/s) and the 298 m/s flight to the camp
CAM_LIMITS = dict(speed=None, yaw=30.0, pitch=(17.0, 45.0), hmin=90.0, hmax=650.0, lens=(27.0, 50.0))
CAM_RUNS = [("g3 flight (profile)", 0.0, B["H"], dict(speed=400.0)), ("g3 camps", B["H"], B["CAM_IN"], dict(speed=150.0)),
            ("g3 march846", B["march"][0], B["march"][1], dict(speed=300.0)),
            ("g3 to camp", B["FT0"], B["FT3"], dict(speed=300.0)), ("g3 camp", B["FT3"], DUR, dict(speed=150.0))]

def cam_report(ground=lambda x, y: 0.0, quiet=False):
    """camchan.check over the whole segment and per run; seam velocities (m/s) vs segtime / march846."""
    out = []
    for name, a, b_, lim in CAM_RUNS:
        L_ = dict(CAM_LIMITS); L_.update(lim); L_["name"] = name
        out.append(camchan.check(CAM_M, a, b_, ground=ground, limits=L_, quiet=quiet))
    L_ = dict(CAM_LIMITS); L_.update(speed=400.0, name="g3 whole (0-78.4)")
    out.append(camchan.check(CAM_M, 0.0, DUR, ground=ground, limits=L_, quiet=quiet))
    h = 1e-3
    def v(t, side):
        return (CAM_M.eval_m(t + h * (side > 0))[0] - CAM_M.eval_m(t - h * (side < 0))[0]) / h
    def lv(t, side):
        return (CAM_M.eval_m(t + h * (side > 0))[1] - CAM_M.eval_m(t - h * (side < 0))[1]) / h
    rows = [("g2->g3 in (0.0)", v(0.0, 1), np.array(_S_IN["vel"], float)),
            ("H rest (17.7) before/after", v(B["H"], -1), v(B["H"], 1)),
            ("CAM_IN (31.3) before/after", v(B["CAM_IN"], -1), v(B["CAM_IN"], 1)),
            ("CAM_IN look before/after", lv(B["CAM_IN"], -1), lv(B["CAM_IN"], 1)),
            ("CAM_OUT (49.3) before/after", v(B["FT0"], -1), v(B["FT0"], 1)),
            ("CAM_OUT look before/after", lv(B["FT0"], -1), lv(B["FT0"], 1)),
            ("g3->g4 out (78.4)", v(DUR, -1), np.array(_S_OUT["vel"], float))]
    if not quiet:
        print("g3 seams (m/s):")
        for nm, a, b_ in rows:
            print("  %-30s %s | %s" % (nm, np.round(a, 1), np.round(b_, 1)))
        p0 = CAM_M.eval_m(0.0); p1 = CAM_M.eval_m(DUR)
        print("  pos 0.0  M", np.round(p0[0], 2), "look", np.round(p0[1], 2), "lens %.1f" % p0[2], "(W: +4130 y)")
        print("  pos 78.4 M", np.round(p1[0], 2), "look", np.round(p1[1], 2), "lens %.1f" % p1[2], "(g4 G0", _S_OUT["pos"], _S_OUT["look"], ")")
    return out, rows


# ====================================================================== light: one key table for both parts (g4's format + amb / sky)
# (t, sun elevation deg, compass azimuth deg (0 N, 90 E), sun energy, sun rgb, zenith rgb, horizon rgb, lighting-sky strength
#  (absolute), camera-sky multiplier) | GRADE (t, gain rgb, exposure offset from -1.5) | HAZE (t, mist depth, amount, rgb)
# t 0 = g2's end light exactly (seg_g2.DUSK_LIGHT through world.light_rig: el 3, az 190 math = 260 compass, (1, .62, .46),
# 3.7, amb .15, exposure -1.35, sky ramp DUSK_SKY); t 78.4 = g4 t 0 exactly (seg_g4 LIGHT_KEYS / GRADE_KEYS / HAZE_KEYS [0]).
def _g4_first():
    try:
        import seg_g4 as S4
        return S4.LIGHT_KEYS[0], S4.GRADE_KEYS[0], S4.HAZE_KEYS[0]
    except Exception as ex:                                 # pragma: no cover
        print("[g3] seg_g4 import failed, using its night literals:", ex)
        return ((0.0, 32.0, 245, 0.35, (0.55, 0.65, 1.00), (0.008, 0.012, 0.035), (0.03, 0.04, 0.08), 0.25),
                (0.0, (0.80, 0.90, 1.18), -2.6), (0.0, 5000.0, 0.55, (0.05, 0.06, 0.12)))
_G4L, _G4G, _G4H = _g4_first()
S0_LIGHT = 0.25                                             # trost._world lighting-sky strength (g4's ws multiplies it)
NIGHT = (_G4L[1], _G4L[2], _G4L[3], tuple(_G4L[4]), tuple(_G4L[5]), tuple(_G4L[6]), S0_LIGHT * _G4L[7], _G4L[7])
NIGHT_G, NIGHT_H = (tuple(_G4G[1]), _G4G[2]), (_G4H[1], _G4H[2], tuple(_G4H[3]))
DUSK = (3.0, 260.0, 3.7, (1.0, 0.62, 0.46), (0.62, 0.50, 0.60), (0.93, 0.50, 0.34), 0.15, 1.0)
HAZE0 = (5000.0, 0.45, (0.62, 0.70, 0.82))
MORNING = (30.0, 115.0, 3.4, (1.00, 0.96, 0.92), (0.10, 0.28, 0.74), (0.70, 0.80, 0.93), 0.25, 1.0)
SPRING = (32.0, 125.0, 3.3, (1.00, 0.96, 0.92), (0.10, 0.28, 0.74), (0.70, 0.80, 0.93), 0.25, 1.0)
SUMMER = (52.0, 165.0, 3.8, (1.00, 0.97, 0.90), (0.08, 0.26, 0.78), (0.66, 0.78, 0.94), 0.27, 1.0)
AUTUMN = (24.0, 215.0, 3.0, (1.00, 0.80, 0.58), (0.20, 0.30, 0.60), (0.88, 0.74, 0.58), 0.22, 1.0)
WINTER = (20.0, 165.0, 1.2, (0.86, 0.89, 0.96), (0.40, 0.43, 0.48), (0.62, 0.64, 0.68), 0.24, 0.9)
OVERCAST = (30.0, 160.0, 2.0, (1.00, 0.97, 0.92), (0.38, 0.42, 0.48), (0.66, 0.68, 0.70), 0.30, 1.0)
SUNSET = (5.0, 285.0, 3.8, (1.00, 0.70, 0.40), (0.30, 0.36, 0.58), (0.91, 0.89, 0.61), 0.20, 1.0)      # sky #f5f2cd
G_ID, G_WIN, G_AUT, G_SUM = ((1.0, 1.0, 1.0), 0.0), ((0.95, 0.98, 1.05), -0.6), ((1.06, 0.98, 0.88), -0.1), ((1.02, 1.0, 0.98), 0.05)
H_WIN, H_OVC = (1800.0, 0.62, (0.62, 0.64, 0.68)), (3200.0, 0.50, (0.62, 0.64, 0.68))
_SEAS = [("spring", SPRING, G_ID, HAZE0), ("summer", SUMMER, G_SUM, HAZE0), ("autumn", AUTUMN, G_AUT, (3200.0, 0.6, (0.86, 0.78, 0.66))),
         ("winter", WINTER, G_WIN, H_WIN)]
SEASON_T = [B["seasons"][0] + 0.4 * k for k in range(12)]                 # 3 cycles of spring-summer-autumn-winter, 0.4 s each
LKEYS = [  # (t, light, grade, haze)
    (0.0, DUSK, ((1.0, 1.0, 1.0), 0.15), HAZE0),
    (2.6, (1.0, 262.0, 2.2, (1.0, 0.50, 0.40), (0.25, 0.20, 0.32), (0.70, 0.36, 0.30), 0.10, 0.6), ((0.95, 0.92, 1.0), -0.6),
     (4500.0, 0.50, (0.45, 0.36, 0.40))),
    (B["night"][0], NIGHT, NIGHT_G, NIGHT_H), (B["night"][1], NIGHT, NIGHT_G, NIGHT_H),
    (10.8, (4.0, 78.0, 0.60, (1.0, 0.62, 0.45), (0.05, 0.07, 0.18), (0.55, 0.36, 0.32), 0.11, 0.45), ((1.0, 0.92, 0.95), -1.4),
     (2600.0, 0.70, (0.62, 0.50, 0.52))),
    (B["FA4"], (8.0, 84.0, 2.2, (1.0, 0.72, 0.48), (0.12, 0.22, 0.52), (0.95, 0.70, 0.52), 0.19, 0.75), ((1.05, 0.98, 0.92), -0.45),
     (2200.0, 0.80, (0.86, 0.76, 0.70))),
    (B["H"], MORNING, G_ID, HAZE0), (B["winter"][0], MORNING, G_ID, HAZE0),
    (B["winter"][1] - 1.2, WINTER, G_WIN, H_WIN), (B["snow"][1] - 0.6, WINTER, G_WIN, H_WIN),
    (B["spring"][1] - 1.0, OVERCAST, ((1.0, 1.0, 1.0), -0.15), H_OVC), (B["march"][0], OVERCAST, ((1.0, 1.0, 1.0), -0.15), H_OVC),
    (B["sunset"][0] - 2.0, (26.0, 230.0, 1.6, (1.0, 0.92, 0.84), (0.34, 0.38, 0.46), (0.64, 0.64, 0.66), 0.28, 0.95),
     ((1.0, 0.99, 0.97), -0.3), H_OVC),
    (B["sunset"][0] + 2.2, SUNSET, ((1.05, 0.98, 0.90), -0.3), (2600.0, 0.70, (0.95, 0.80, 0.60))),
    (B["march"][1], (2.5, 288.0, 3.2, (1.0, 0.58, 0.32), (0.25, 0.28, 0.50), (0.95, 0.75, 0.50), 0.18, 0.9), ((1.06, 0.96, 0.88), -0.45),
     (2400.0, 0.70, (0.90, 0.66, 0.48))),
    (51.6, (20.0, 245.0, 0.35, (0.55, 0.65, 1.0), (0.02, 0.03, 0.07), (0.06, 0.07, 0.12), 0.07, 0.3), ((0.85, 0.92, 1.12), -2.0),
     (4500.0, 0.55, (0.08, 0.09, 0.15))),                   # the years pass: one night over the flight (846 -> 847)
    (54.4, (8.0, 84.0, 2.2, (1.0, 0.72, 0.48), (0.12, 0.22, 0.52), (0.95, 0.70, 0.52), 0.19, 0.75), ((1.05, 0.98, 0.92), -0.45),
     (2200.0, 0.80, (0.86, 0.76, 0.70))),
    (B["camp_morning"][0], MORNING, G_ID, HAZE0), (B["seasons"][0], SPRING, G_ID, HAZE0)] + \
    [(t_, _SEAS[k % 4][1], _SEAS[k % 4][2], _SEAS[k % 4][3]) for k, t_ in enumerate(SEASON_T[1:], 1)] + [
    (B["grad"][0] + 0.2, (2.0, 250.0, 2.4, (1.0, 0.55, 0.36), (0.18, 0.18, 0.34), (0.80, 0.46, 0.34), 0.12, 0.6), ((0.98, 0.92, 0.98), -0.9),
     (4000.0, 0.55, (0.40, 0.30, 0.34))),
    (B["grad"][0] + 1.6, NIGHT, NIGHT_G, NIGHT_H), (DUR, NIGHT, NIGHT_G, NIGHT_H)]
# ground surface: (t, snow 0..1, autumn 0..1) -- the clearing winter, the 3 seasons cycles
SURF_KEYS = [(0.0, 0.0, 0.0), (B["winter"][0], 0.0, 0.0), (B["winter"][1], 0.72, 0.0), (B["spring"][0], 0.72, 0.0), (B["spring"][1], 0.0, 0.0)]
for _k in range(12):
    _t = SEASON_T[_k]; _sn = _SEAS[_k % 4][0]
    SURF_KEYS.append((_t, 0.55 if _sn == "winter" else 0.0, 0.8 if _sn == "autumn" else 0.0))
SURF_KEYS += [(B["grad"][0] + 0.4, 0.0, 0.0), (DUR, 0.0, 0.0)]
SURF_KEYS.sort(key=lambda k: k[0])

def ss(a, b, x):
    u = min(1.0, max(0.0, (x - a) / (b - a))) if b != a else float(x >= b)
    return u * u * (3 - 2 * u)

def _mix(a, b, u):
    if isinstance(a, (tuple, list)):
        return tuple(x + (y - x) * u for x, y in zip(a, b))
    return a + (b - a) * u

def _keyed(K, t):
    if t <= K[0][0]:
        return K[0], K[0], 0.0
    for a, b_ in zip(K, K[1:]):
        if a[0] <= t < b_[0]:
            return a, b_, ss(a[0], b_[0], t)
    return K[-1], K[-1], 0.0

def light_values(t):
    """Pure: everything light(t) writes (sun direction in the module's frame = M / W: same axes)."""
    a, b_, u = _keyed(LKEYS, t)
    def sdir(k):
        el, az = math.radians(k[0]), math.radians(k[1])
        return np.array([math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el)])
    La, Lb = a[1], b_[1]
    d = sdir(La) * (1 - u) + sdir(Lb) * u; d /= np.linalg.norm(d)
    return dict(d=d, el=_mix(La[0], Lb[0], u), en=_mix(La[2], Lb[2], u), col=_mix(La[3], Lb[3], u), zen=_mix(La[4], Lb[4], u),
                hor=_mix(La[5], Lb[5], u), amb=_mix(La[6], Lb[6], u), camk=_mix(La[7], Lb[7], u),
                gain=_mix(a[2][0], b_[2][0], u), gex=_mix(a[2][1], b_[2][1], u),
                mist_depth=_mix(a[3][0], b_[3][0], u), mist_k=_mix(a[3][1], b_[3][1], u), mist_rgb=_mix(a[3][2], b_[3][2], u))

def surf_values(t):
    a, b_, u = _keyed(SURF_KEYS, t)
    return _mix(a[1], b_[1], u), _mix(a[2], b_[2], u)

def night_lights(t):
    """Trost window dots / wall-top torches 0..1 (lit through dusk, out at dawn)."""
    return ss(1.2, 4.2, t) * (1.0 - ss(*B["lights_off"], t))

# ====================================================================== HUD trackers (frame M) -- filled by build()
TRACK = {}

# ====================================================================== Blender side
S = {}                                   # everything built
L = None; PK = None; SITE = None

def say(*a):
    print("[g3]", *a, flush=True)

def lin(h):
    h = h.lstrip("#"); c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c)

def _window():
    """The driver's render window (--t0/--t1, --stills; --check/--dry = everything).  G3_PARTS=a,b overrides the parts."""
    a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    def get(k, d):
        return a[a.index(k) + 1] if k in a and a.index(k) + 1 < len(a) else d
    st = get("--stills", "")
    if st:
        ts = [float(x) for x in st.split(",") if x.strip()]
        return min(ts), max(ts)
    if "--check" in a or "--dry" in a:
        return 0.0, DUR
    return float(get("--t0", 0.0)), min(float(get("--t1", DUR)), DUR)

PART_SPANS = dict(night=(1.0, 12.5), rose=(9.0, B["CAM_IN"] - 0.02), march=(B["crowd846"][0] - 0.1, B["march"][1]), camp=(45.0, DUR))

def parts_for(t0, t1):
    env = os.environ.get("G3_PARTS")
    if env:
        return set(x.strip() for x in env.split(",") if x.strip())
    out = {k for k, (a, b_) in PART_SPANS.items() if t0 <= b_ and t1 >= a}
    if PART == "A":
        out &= {"night"}
    return out

def F(p):
    """frame M point -> the scene frame (part A: Shiganshina W; part B: the trost set)."""
    if PART == "A":
        return Vector((float(p[0]), float(p[1]) + MW, float(p[2]) if len(p) > 2 else 0.0))
    return SITE["M2S"](p)

def coll(name):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name); bpy.context.scene.collection.children.link(c)
    return c

def emit_mat(name, rgb, strength):
    m = bpy.data.materials.new(name); m.use_nodes = True
    N = m.node_tree.nodes
    for n in list(N):
        if n.type != "OUTPUT_MATERIAL":
            N.remove(n)
    em = N.new("ShaderNodeEmission"); em.inputs["Color"].default_value = (*rgb, 1.0); em.inputs["Strength"].default_value = strength
    m.node_tree.links.new(em.outputs[0], next(n for n in N if n.type == "OUTPUT_MATERIAL").inputs["Surface"])
    m["toon"] = 1
    return m, em

def flat(name, hexc, rough=0.9, **kw):
    return L.mat(name, lin(hexc), rough, **kw)

_GROUND_OBS = []
def ground_ray(x, y, z0=600.0):
    """Ground z at SCENE (x, y): ray down onto the terrain meshes only (Terrain + world ground), else the site helper."""
    best = None
    for ob in _GROUND_OBS:
        mi = ob.matrix_world.inverted()
        o = mi @ Vector((x, y, z0)); d = (mi.to_3x3() @ Vector((0, 0, -1))).normalized()
        hit, loc, nrm, idx = ob.ray_cast(o, d, distance=5000.0)
        if hit:
            z = (ob.matrix_world @ loc).z
            best = z if best is None else max(best, z)
    if best is None:
        best = float(L.height(x, y))
    return best

def gM(x, y):
    """Ground z at frame-M (x, y)."""
    q = F((x, y, 0.0))
    return ground_ray(q.x, q.y)

# ---------------------------------------------------------------------- point instancer (per-point scale, yaw) for trees / tents
def gn_instancer(name, proto, coll_):
    ng = bpy.data.node_groups.new(name, "GeometryNodeTree")
    ng.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    N, Ln = ng.nodes, ng.links
    gi, go = N.new("NodeGroupInput"), N.new("NodeGroupOutput")
    oi = N.new("GeometryNodeObjectInfo"); oi.transform_space = "ORIGINAL"; oi.inputs["Object"].default_value = proto
    m2p = N.new("GeometryNodeMeshToPoints"); Ln.new(gi.outputs["Geometry"], m2p.inputs["Mesh"])
    sa = N.new("GeometryNodeInputNamedAttribute"); sa.data_type = "FLOAT"; sa.inputs["Name"].default_value = "s"
    ra = N.new("GeometryNodeInputNamedAttribute"); ra.data_type = "FLOAT"; ra.inputs["Name"].default_value = "yaw"
    cmp_ = N.new("FunctionNodeCompare"); cmp_.data_type = "FLOAT"; cmp_.operation = "LESS_THAN"; cmp_.inputs[1].default_value = 1e-3
    Ln.new(sa.outputs["Attribute"], cmp_.inputs[0])
    dg = N.new("GeometryNodeDeleteGeometry"); dg.domain = "POINT"
    Ln.new(m2p.outputs["Points"], dg.inputs["Geometry"]); Ln.new(cmp_.outputs["Result"], dg.inputs["Selection"])
    iop = N.new("GeometryNodeInstanceOnPoints"); Ln.new(dg.outputs["Geometry"], iop.inputs["Points"])
    Ln.new(oi.outputs["Geometry"], iop.inputs["Instance"])
    cx = N.new("ShaderNodeCombineXYZ"); Ln.new(ra.outputs["Attribute"], cx.inputs["Z"])
    Ln.new(sa.outputs["Attribute"], iop.inputs["Scale"]); Ln.new(cx.outputs[0], iop.inputs["Rotation"])
    Ln.new(iop.outputs["Instances"], go.inputs["Geometry"])
    return ng

class Points:
    """One vertex cloud instanced with `proto`; set(s) writes the per-point scale (0 = hidden)."""
    def __init__(self, name, P, yaw, proto, coll_):
        me = bpy.data.meshes.new(name); me.vertices.add(len(P))
        me.vertices.foreach_set("co", np.asarray(P, np.float32).ravel())
        me.attributes.new("s", "FLOAT", "POINT"); me.attributes.new("yaw", "FLOAT", "POINT")
        me.attributes["yaw"].data.foreach_set("value", np.asarray(yaw, np.float32))
        self.ob = bpy.data.objects.new(name, me); coll_.objects.link(self.ob)
        md = self.ob.modifiers.new("Inst", "NODES"); md.node_group = gn_instancer(name + "_GN", proto, coll_)
        self.n = len(P); self.last = None
        self.set(np.ones(self.n))
    def set(self, s):
        s = np.asarray(s, np.float32)
        if self.last is not None and np.array_equal(s, self.last):
            return
        self.ob.data.attributes["s"].data.foreach_set("value", s); self.ob.data.update()
        self.ob.hide_render = not bool((s > 1e-3).any())
        self.last = s.copy()

def proto_obj(name, bm, mats, coll_):
    ob = L.obj_from_bm(name, bm, mats, coll_)
    ob.hide_render = True; ob.hide_viewport = False; ob.location = (0, 0, -30000.0)
    return ob

def cone_bm(r=0.32, h=1.0, seg=6):
    bm = bmesh.new()
    L.cyl(bm, (0, 0, 0.0), (0, 0, h), r, 0.0, seg=seg)
    return bm

# ---------------------------------------------------------------------- crowds (people_kit) with cached visibility
class Group:
    def __init__(self, insts):
        self.e = list(insts); self.vis = None
        self.base = [tuple(e.location) for e in self.e]
    def show(self, mask):
        if isinstance(mask, (bool, np.bool_)):
            mask = np.full(len(self.e), bool(mask))
        mask = np.asarray(mask, bool)
        if self.vis is not None and np.array_equal(mask, self.vis):
            return
        for e, m in zip(self.e, mask):
            if e.hide_render == m:
                e.hide_render = not m
        self.vis = mask.copy()

def crowd(presets, cM, w, d, n, pose="stand", yaw=0.0, seed=1, formation="scatter", spacing=None, front=()):
    q = F((cM[0], cM[1], 0.0))
    ins = PK.crowd(presets, (q.x, q.y, w, d, yaw), n, pose=pose, yaw=yaw, seed=seed, formation=formation, spacing=spacing,
                   front=front)
    for e in ins:
        e.location.z = ground_ray(e.location.x, e.location.y) + 0.05
    return Group(ins)

def person(preset, pM, yaw=0.0, pose="stand", z=None):
    q = F((pM[0], pM[1], 0.0))
    zz = ground_ray(q.x, q.y) + 0.05 if z is None else z
    return PK.person(preset, (q.x, q.y, zz), yaw=yaw, pose=pose)

# ====================================================================== builders
def trost_dots():
    """(window dots M (n,3), torch points M (m,3)): deterministic, the same in both parts (part A has only the proxy carpet)."""
    rnd = np.random.default_rng(845)
    P = []
    while len(P) < 900:
        x, y = rnd.uniform(-465, 465), rnd.uniform(15, 860)
        if y < 480 and math.hypot(x, y - 480) > 462:
            continue
        if math.hypot(x, y) < 85 or abs(x - 400) < 18:                # gate square, canal
            continue
        P.append((x, y, rnd.uniform(8.0, 15.0)))
    T = []
    for a in np.radians(np.arange(-178, -1, 6.0)):                 # bulge arc (centre (0, 480), r 480) + straight sides + Rose
        T.append((480 * math.cos(a), 480 + 480 * math.sin(a), 52.5))
    for y in np.arange(500, 870, 50):
        T += [(-480, y, 52.5), (480, y, 52.5)]
    for x in np.arange(-2400, 2401, 70):
        T.append((x, 870, 52.5))
    return np.array(P), np.array(T)

def build_night(cl):
    P, T = trost_dots()
    dm, dem = emit_mat("G3_WindowDot", (1.0, 0.66, 0.30), 0.0)
    tm, tem = emit_mat("G3_Torch", (1.0, 0.48, 0.16), 0.0)
    for name, pts, size, m in (("G3NightWindows", P, 3.2, dm), ("G3NightTorches", T, 2.6, tm)):
        bm = bmesh.new()
        for p in pts:
            L.box(bm, tuple(F(p)), (size, size, size * 0.8))
        o = L.obj_from_bm(name, bm, [m], cl)
        o.visible_shadow = False
        S.setdefault("night_obs", []).append(o)
    S["night_em"] = (dem, tem)

def set_night_lights(t):
    if "night_em" not in S:
        return
    f = night_lights(t)
    S["night_em"][0].inputs["Strength"].default_value = 9.0 * f
    S["night_em"][1].inputs["Strength"].default_value = 12.0 * f
    for o in S["night_obs"]:
        h = f < 0.005
        if o.hide_render != h:
            o.hide_render = h

# ---------------------------------------------------------------------- the ground surface: snow + autumn overlay on every ground material
def inject_surface(m, snow_rgb=(0.66, 0.68, 0.72), scale=1 / 90.0):
    """base colour -> mix(autumn tint) -> mix(snow, patchy noise mask); returns (snow value node, autumn value node)."""
    if m is None or not m.use_nodes:
        return None
    nt = m.node_tree; N, Ln = nt.nodes, nt.links
    b = next((n for n in N if n.type == "BSDF_PRINCIPLED"), None)
    if b is None:
        return None
    bc = b.inputs["Base Color"]
    if bc.is_linked:
        base = bc.links[0].from_socket
    else:
        rgb = N.new("ShaderNodeRGB"); rgb.outputs[0].default_value = tuple(bc.default_value); base = rgb.outputs[0]
    vs, va = N.new("ShaderNodeValue"), N.new("ShaderNodeValue"); vs.outputs[0].default_value = 0.0; va.outputs[0].default_value = 0.0
    vs.name, va.name = "G3Snow", "G3Autumn"
    au = N.new("ShaderNodeMix"); au.data_type = "RGBA"; au.blend_type = "MULTIPLY"
    Ln.new(va.outputs[0], au.inputs["Factor"]); Ln.new(base, au.inputs["A"]); au.inputs["B"].default_value = (1.35, 0.95, 0.42, 1)
    tc = N.new("ShaderNodeTexCoord"); nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = scale
    nz.inputs["Detail"].default_value = 3
    Ln.new(tc.outputs["Object"], nz.inputs["Vector"])
    # mask = clamp((noise - 0.62 + 0.62 * snow) * 6): patches first, full cover at snow 1
    sub = N.new("ShaderNodeMath"); sub.operation = "MULTIPLY_ADD"; Ln.new(vs.outputs[0], sub.inputs[0]); sub.inputs[1].default_value = 0.62
    sub.inputs[2].default_value = -0.62
    ad = N.new("ShaderNodeMath"); ad.operation = "ADD"; Ln.new(nz.outputs["Fac"], ad.inputs[0]); Ln.new(sub.outputs[0], ad.inputs[1])
    mk = N.new("ShaderNodeMath"); mk.operation = "MULTIPLY"; mk.use_clamp = True; mk.inputs[1].default_value = 6.0
    Ln.new(ad.outputs[0], mk.inputs[0])
    mk2 = N.new("ShaderNodeMath"); mk2.operation = "MULTIPLY"; mk2.use_clamp = True
    Ln.new(mk.outputs[0], mk2.inputs[0]); Ln.new(vs.outputs[0], mk2.inputs[1])
    sn = N.new("ShaderNodeMix"); sn.data_type = "RGBA"; sn.blend_type = "MIX"
    Ln.new(mk2.outputs[0], sn.inputs["Factor"]); Ln.new(au.outputs["Result"], sn.inputs["A"]); sn.inputs["B"].default_value = (*snow_rgb, 1)
    Ln.new(sn.outputs["Result"], bc)
    return vs.outputs[0], va.outputs[0]

def build_surface():
    S["surf"] = []
    names = ["Terrain", "WD_Ground", "CP_Floor", "CP_RimGrass", "G3Clearing"]
    for nm in names:
        m = bpy.data.materials.get(nm)
        r = inject_surface(m, scale=1 / 60.0 if nm.startswith(("CP_", "G3")) else 1 / 140.0)
        if r:
            S["surf"].append(r)
    say("snow/autumn overlay on", len(S["surf"]), "materials")

def set_surface(t):
    sn, au = surf_values(t)
    for vs, va in S.get("surf", ()):
        vs.default_value = sn; va.default_value = au

class Flakes:
    """Falling snow: n small octahedra in a box (frame M), positions a pure function of t; amount 0..1 scales them."""
    def __init__(self, name, box, n, size, cl, seed=7):
        rnd = np.random.default_rng(seed)
        (x0, x1), (y0, y1), (z0, z1) = box
        self.base = np.column_stack([rnd.uniform(x0, x1, n), rnd.uniform(y0, y1, n), rnd.uniform(0, 1, n)])
        self.z0, self.H = z0, z1 - z0; self.v = rnd.uniform(0.06, 0.11, n); self.ph = rnd.uniform(0, 6.28, n)
        oc = np.array([(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)], float) * size
        self.oc = oc; self.n = n
        fs = [(0, 2, 4), (2, 1, 4), (1, 3, 4), (3, 0, 4), (2, 0, 5), (1, 2, 5), (3, 1, 5), (0, 3, 5)]
        me = bpy.data.meshes.new(name)
        V = np.zeros((n * 6, 3)); me.vertices.add(n * 6); me.vertices.foreach_set("co", V.astype(np.float32).ravel())
        F_ = np.array([[a + 6 * i, b_ + 6 * i, c + 6 * i] for i in range(n) for a, b_, c in fs])
        me.loops.add(len(F_) * 3); me.polygons.add(len(F_))
        me.loops.foreach_set("vertex_index", F_.ravel()); me.polygons.foreach_set("loop_start", np.arange(0, len(F_) * 3, 3))
        me.polygons.foreach_set("loop_total", np.full(len(F_), 3)); me.update(calc_edges=True)
        m, _ = emit_mat(name + "M", (0.92, 0.94, 0.98), 1.6)
        me.materials.append(m)
        self.ob = bpy.data.objects.new(name, me); cl.objects.link(self.ob); self.ob.visible_shadow = False
    def update(self, t, amount):
        if amount < 0.01:
            self.ob.hide_render = True; return
        self.ob.hide_render = False
        zf = (self.base[:, 2] - self.v * t) % 1.0
        x = self.base[:, 0] + 3.0 * np.sin(0.7 * t + self.ph); y = self.base[:, 1] + 2.0 * np.cos(0.5 * t + self.ph)
        P = np.column_stack([x, y, self.z0 + zf * self.H])
        if PART == "B":
            P[:, 1] -= segtime.SET_OFF_Y
        V = P[:, None, :] + self.oc[None, :, :] * min(1.0, amount * 1.4)
        self.ob.data.vertices.foreach_set("co", V.astype(np.float32).ravel()); self.ob.data.update()

# ---------------------------------------------------------------------- 845-846 at the Rose foot (frame M)
RC = (-268.0, 805.0)                                   # relief complex courtyard centre (trost.py builds the complex)
SHELTER = (-500.0, -100.0, 960.0, 1130.0)              # bible: barns + <= 120 drab tents north of Rose
BARNS = [(-460, 990), (-380, 990), (-300, 995), (-220, 990), (-450, 1100), (-360, 1105), (-270, 1100), (-180, 1102)]
CLEARING = (-900.0, 100.0, 1170.0, 1630.0)
BOOTH = (-244.0, 792.0)                                # Garrison ration booth in the courtyard's SE corner
MP_DESK = (-120.0, 812.0)                              # MP enlistment desk on the inner-gate square

def build_shelter(cl):
    rnd = random.Random(1845)
    x0, x1, y0, y1 = SHELTER
    barn_w, barn_r = flat("G3BarnWall", "#8a7458"), flat("G3BarnRoof", "#5a4a3c")
    bm = bmesh.new()
    for bx, by in BARNS:
        q = F((bx, by, 0.0)); z = ground_ray(q.x, q.y)
        rot = rnd.uniform(-0.05, 0.05)
        L.box(bm, (q.x, q.y, z + 2.5), (30.0, 10.0, 5.0), rot=rot, mi=0)
        L.box(bm, (q.x, q.y, z + 6.2), (31.0, 11.0, 2.6), rot=rot, mi=1, taper=(1.0, 0.06))
    L.obj_from_bm("G3Barns", bm, [barn_w, barn_r], cl)
    tb = bmesh.new()                                   # tent: 4 x 3 m A-frame, 2.2 m ridge (unit prototype)
    vs = [tb.verts.new(c) for c in ((-3, -2.2, 0), (3, -2.2, 0), (3, 2.2, 0), (-3, 2.2, 0), (-3, 0, 2.8), (3, 0, 2.8))]   # 6 x 4.4 m
    for f in ((0, 1, 5, 4), (2, 3, 4, 5), (0, 4, 3), (1, 2, 5)):
        tb.faces.new([vs[i] for i in f])
    tproto = proto_obj("G3TentProto", tb, [flat("G3Tent", "#9c9480", 0.95)], cl)
    P, Y = [], []
    while len(P) < 116:
        x, y = rnd.uniform(x0 + 10, x1 - 10), rnd.uniform(y0 + 10, y1 - 10)
        if any(abs(x - bx) < 20 and abs(y - by) < 10 for bx, by in BARNS):
            continue
        if any((x - a) ** 2 + (y - b_) ** 2 < 100 for a, b_ in P):
            continue
        P.append((x, y)); Y.append(rnd.choice((0.0, math.pi / 2)) + rnd.uniform(-0.2, 0.2))
    PP = []
    for x, y in P:
        q = F((x, y, 0.0)); PP.append((q.x, q.y, ground_ray(q.x, q.y) + 0.2))
    S["tents"] = Points("G3Tents", PP, Y, tproto, cl)
    S["tent_key"] = np.random.default_rng(3).uniform(0, 1, len(PP))
    S["shelter_ppl"] = crowd(["civilian"], ((x0 + x1) / 2, (y0 + y1) / 2), x1 - x0 - 30, y1 - y0 - 20, 220, seed=21)

def build_clearing(cl):
    """Winter clearing beyond Rose: grey mud, 9 contour benches with dark lips, hoe-line furrows, snow overlay; the black
    conifer edge (trees standing on the clearing are felled south -> north over the winter)."""
    x0, x1, y0, y1 = CLEARING
    m = bpy.data.materials.new("G3Clearing"); m.use_nodes = True
    nt = m.node_tree; N, Ln = nt.nodes, nt.links
    b = N["Principled BSDF"]; b.inputs["Roughness"].default_value = 0.95
    tc = N.new("ShaderNodeTexCoord"); wv = N.new("ShaderNodeTexWave"); wv.wave_type = "BANDS"; wv.bands_direction = "X"
    wv.inputs["Scale"].default_value = 0.035; wv.inputs["Distortion"].default_value = 1.5
    Ln.new(tc.outputs["Object"], wv.inputs["Vector"])
    rp = N.new("ShaderNodeValToRGB"); e = rp.color_ramp.elements
    e[0].position, e[0].color = 0.2, (*lin("#4e4b47"), 1); e[1].position, e[1].color = 0.55, (*lin("#64615c"), 1)
    Ln.new(wv.outputs["Fac"], rp.inputs["Fac"]); Ln.new(rp.outputs["Color"], b.inputs["Base Color"])
    lip = flat("G3BenchLip", "#3e3a35")
    bm = bmesh.new()
    nb = 9; nx = 50
    for k in range(nb):                                # benches step down toward Rose (south)
        ya, yb = y0 + (y1 - y0) * k / nb, y0 + (y1 - y0) * (k + 1) / nb - 4.0
        row_a, row_b = [], []
        for i in range(nx + 1):
            x = x0 + (x1 - x0) * i / nx
            wob = 12.0 * math.sin(x / 140.0 + k)
            qa, qb = F((x, ya + wob, 0.0)), F((x, yb + wob, 0.0))
            za = ground_ray(qa.x, qa.y) + 0.35 + 0.25 * k; zb = ground_ray(qb.x, qb.y) + 0.35 + 0.25 * k
            row_a.append(bm.verts.new((qa.x, qa.y, za))); row_b.append(bm.verts.new((qb.x, qb.y, zb)))
        for i in range(nx):
            bm.faces.new((row_a[i], row_a[i + 1], row_b[i + 1], row_b[i]))
        if k < nb - 1:                                 # the dark lip strip up to the next bench
            for i in range(nx):
                f = bm.faces.new((row_b[i], row_b[i + 1], bm.verts.new(row_b[i + 1].co + Vector((0, 4.0, 0.25))),
                                  bm.verts.new(row_b[i].co + Vector((0, 4.0, 0.25)))))
                f.material_index = 1
    L.obj_from_bm("G3Clearing", bm, [m, lip], cl)
    # conifers: a dense black edge north of the clearing (stays) + the stand ON the clearing (felled south -> north)
    tproto = proto_obj("G3ConiferProto", cone_bm(0.30, 1.0, 6), [flat("G3Conifer", "#1e2a1e", 0.9)], cl)
    rnd = np.random.default_rng(1846)
    n_on, n_edge = 1400, 700
    xs = np.concatenate([rnd.uniform(x0, x1, n_on), rnd.uniform(x0 - 60, x1 + 60, n_edge)])
    ys = np.concatenate([rnd.uniform(y0, y1, n_on), y1 + 10 + rnd.exponential(45.0, n_edge)])
    P = []
    for x, y in zip(xs, ys):
        q = F((x, y, 0.0)); P.append((q.x, q.y, ground_ray(q.x, q.y) - 0.3))
    S["conif_h"] = rnd.uniform(14, 22, len(P))
    S["conif"] = Points("G3Conifers", P, rnd.uniform(0, 6.28, len(P)), tproto, cl)
    S["conif_fell"] = np.concatenate([(ys[:n_on] - y0) / (y1 - y0) * 0.85 + rnd.uniform(0, 0.15, n_on), np.full(n_edge, 9.0)])
    # workers with hoes on the benches (winter -> spring)
    S["workers"] = crowd(["civilian"], ((x0 + x1) / 2 + 150, y0 + 120), 600, 200, 150, pose="kneel", seed=31)

def build_courtyard(cl):
    S["court"] = crowd(["civilian"], (RC[0] + 2, RC[1]), 74, 40, 520, seed=11)
    S["court_key"] = np.random.default_rng(12).uniform(0, 1, len(S["court"].e))
    wood, cloth = flat("G3BoothWood", "#6b4a30"), flat("G3BoothCloth", "#b9ab88")
    bm = bmesh.new(); q = F((BOOTH[0], BOOTH[1], 0.0)); z = ground_ray(q.x, q.y)
    L.box(bm, (q.x, q.y, z + 0.6), (6.0, 2.0, 1.2), mi=0)
    for sx in (-2.8, 2.8):
        L.box(bm, (q.x + sx, q.y + 0.6, z + 1.5), (0.2, 0.2, 3.0), mi=0)
    L.box(bm, (q.x, q.y + 0.4, z + 3.1), (6.6, 3.2, 0.3), mi=1)
    for k in range(4):                                  # sacks
        L.box(bm, (q.x - 2.4 + 1.6 * k, q.y + 1.6, z + 0.45), (1.0, 0.8, 0.9), mi=1)
    L.obj_from_bm("G3RationBooth", bm, [wood, cloth], cl)
    S["booth"] = Group([person("garrison", (BOOTH[0] - 2 + 2 * k, BOOTH[1] + 1.8), yaw=math.pi) for k in range(3)])
    S["queue"] = crowd(["civilian"], (BOOTH[0] - 22, BOOTH[1] - 4), 40, 2.4, 40, formation="grid", spacing=(1.0, 1.2), seed=13,
                       yaw=-math.pi / 2)
    # MP enlistment desk on the inner-gate square (846): 6 MPs, a file of volunteers
    bm = bmesh.new(); q = F((MP_DESK[0], MP_DESK[1], 0.0)); z = ground_ray(q.x, q.y)
    L.box(bm, (q.x, q.y, z + 0.45), (4.0, 1.2, 0.9))
    L.obj_from_bm("G3MPDesk", bm, [wood], cl)
    S["mp"] = Group([person("mp", (MP_DESK[0] - 1.5 + 1.0 * k, MP_DESK[1] + 1.4 + 0.8 * (k % 2)), yaw=math.pi) for k in range(6)])
    S["mpfile"] = crowd(["civilian"], (MP_DESK[0], MP_DESK[1] - 22), 2.2, 38, 36, formation="grid", spacing=(1.1, 1.05), seed=14)

def update_rose(t):
    if "court" not in S:
        return
    k = S["court_key"]                                  # courtyard: packed in 845, thins as the refugees join the 846 gathering
    S["court"].show(k < 1.0 - 0.7 * ss(B["crowd846"][0], B["crowd846"][1], t))
    on845 = t < B["CAM_IN"]
    S["booth"].show(on845)
    S["queue"].show((np.arange(len(S["queue"].e)) < int(40 * (1 - 0.6 * ss(22.0, 26.0, t)))) & on845)
    S["shelter_ppl"].show(on845)
    S["tents"].set(np.where((S["tent_key"] < 1.0 - 0.45 * ss(23.0, 27.0, t)) & on845, 1.0, 0.0))
    S["workers"].show(B["winter"][0] - 0.4 <= t <= B["spring"][1])
    mpv = B["crowd846"][0] <= t < B["CAM_IN"]
    S["mp"].show(mpv); S["mpfile"].show(mpv)
    fell = ss(B["H"] + 1.0, B["spring"][0] + 1.0, t) * 1.05   # conifers on the clearing fall over the winter, the edge stays
    S["conif"].set(np.where(S["conif_fell"] > fell, S["conif_h"], 0.0))

# ---------------------------------------------------------------------- march846 (its simulation + instancers; NOT its light / mood)
def march_module():
    os.environ.setdefault("MARCH_WAGONS", "150")       # bible: <= 150 carts (march846 default 1600)
    import march846 as MR
    return MR

def build_march(cl):
    """march846.setup() minus its mood (g3 lights the march), minus open_gate / clear_plain / dress_fields (static dressings run
    in every part-B window: see build) and minus its first update."""
    MR = march_module()
    t0 = time.time()
    MR.ground_setup(); MR.simulate()
    St = MR.STATE
    mc = bpy.data.collections.get("March846") or L.new_coll("March846")
    pcoll, wcoll = MR.build_protos()
    ngp = MR._gn_instancer("MarchPeopleGN", pcoll)
    ngw = MR._gn_instancer("MarchWagonGN", wcoll)
    attrs = {"s": ("FLOAT", "POINT"), "lod": ("INT", "POINT"), "rot": ("FLOAT_VECTOR", "POINT"),
             "col": ("FLOAT_COLOR", "POINT"), "col2": ("FLOAT_COLOR", "POINT"), "hair": ("FLOAT_COLOR", "POINT")}
    pob = MR._point_cloud("MarchPeople", St["N"], attrs, ngp, mc)
    rng = np.random.default_rng(MR.SEED + 7)
    N = St["N"]; kind = St["kind"]
    col = np.array(MR.SHIRTS)[rng.integers(0, len(MR.SHIRTS), N)]
    col = np.where((kind == 1)[:, None], np.array(MR.CLOAK_SCOUT)[None, :], col)
    col = np.where((kind == 2)[:, None], np.array(MR.CLOAK_GARRISON)[None, :], col)
    col = np.where((kind == 3)[:, None], np.array(MR.CLOAK_SCOUT)[None, :], col)
    col2 = np.array(MR.PANTS)[rng.integers(0, len(MR.PANTS), N)]
    hair = np.array(MR.HAIRS)[rng.choice(len(MR.HAIRS), N, p=[0.28, 0.34, 0.16, 0.12, 0.10])]
    for nm, arr in (("col", col), ("col2", col2), ("hair", hair)):
        rgba = np.concatenate([arr, np.ones((N, 1))], 1).astype(np.float32)
        pob.data.attributes[nm].data.foreach_set("color", rgba.ravel())
    wob_ = MR._point_cloud("MarchWagons", St["NW"], {"s": ("FLOAT", "POINT"), "lod": ("INT", "POINT"), "rot": ("FLOAT_VECTOR", "POINT")}, ngw, mc)
    wob_.data.attributes["lod"].data.foreach_set("value", St["wkind"].astype(np.int32))
    MR.build_titans(mc)
    MR.build_cards(mc)
    St.update(pob=pob, wob=wob_, coll=mc, phase=rng.random(N), panicp=rng.random(N) < 0.35)
    MR.MOOD.clear()                                     # g3's light() owns the light (march846.mood() is a no-op without MOOD)
    S["MR"] = MR
    S["fill_key"] = np.random.default_rng(84).uniform(0, 1, N)
    S["wfill_key"] = np.random.default_rng(85).uniform(0, 1, St["NW"])
    say(f"march846 built {time.time() - t0:.1f}s: people {N}, wagons {St['NW']}, titans {St['NT']}")

def _march_obs():
    St = S["MR"].STATE
    return [St.get("pob"), St.get("wob"), St.get("tob")]

def update_march(t):
    MR = S.get("MR")
    if MR is None:
        return
    a, b_ = B["march"]
    show = B["crowd846"][0] - 0.05 <= t <= b_ + 1e-6
    for o in _march_obs():
        if o is not None and o.hide_render == show:
            o.hide_render = not show
    if not show:
        return
    tau = min(max(t - a, 0.0), MARCH_T_END)
    c = CAM_M.eval_m(t)[0]
    MR.update(tau, Vector((c[0], c[1] - segtime.SET_OFF_Y, c[2])))
    if t < a:                                            # the 846 gathering: the avenue fills with the column's people
        f = ss(*B["crowd846"], t)
        St = MR.STATE
        me = St["pob"].data; s_ = np.zeros(St["N"], np.float32); me.attributes["s"].data.foreach_get("value", s_)
        me.attributes["s"].data.foreach_set("value", (s_ * (S["fill_key"] < f)).astype(np.float32)); me.update()
        me = St["wob"].data; w_ = np.zeros(St["NW"], np.float32); me.attributes["s"].data.foreach_get("value", w_)
        me.attributes["s"].data.foreach_set("value", (w_ * (S["wfill_key"] < f)).astype(np.float32)); me.update()

def update_gate(t):
    d = bpy.data.objects.get("OuterGate_Door")
    if d is None:
        return
    if t < B["march"][0]:
        d.location.z = 21.0 * ss(*B["gate_open"], t)
    elif t > B["march"][1]:
        d.location.z = 0.0
    elif S.get("MR") is None:                           # march window without the simulation (stills): march846's door law
        tau = t - B["march"][0]
        d.location.z = 21.0 * (1.0 - ss(17.6, 18.0, tau))

# ---------------------------------------------------------------------- the 104th camp (camp104.py, shared with g4) + its people
CAMP_C = (-1450.0, 1520.0)
RIGS_U = (-10.0, 12.0, 34.0, 56.0)                     # v +38

def cuv(u, v):
    return (CAMP_C[0] + u, CAMP_C[1] + v)

def build_camp(cl):
    import camp104
    st = camp104.build(L, SITE["M2S"], SITE["ground_M"], coll("G3Camp"))
    S["camp"] = st; S["camp_mod"] = camp104
    g0 = gM(*CAMP_C)
    root = bpy.data.objects.new("G3CampRise", None); root.location = F((CAMP_C[0], CAMP_C[1], g0)); cl.objects.link(root)
    bpy.context.view_layer.update()
    for o in st["objs"]:                                # time-lapse construction 49.3-53: the camp rises out of the ground (847)
        mw = o.matrix_world.copy(); o.parent = root; o.matrix_parent_inverse = root.matrix_world.inverted(); o.matrix_world = mw
    S["camp_root"] = root
    # enlistment: 250 recruits (10 x 25) facing south, Shadis walking their front
    S["recruits"] = crowd(["cadet"], cuv(-52, 2), 30.0, 12.0, 250, yaw=math.pi, formation="grid", spacing=(1.2, 1.2), seed=104,
                          front=["eren", "mikasa", "armin"])
    S["shadis"] = person("shadis", cuv(-60, -9), yaw=math.pi / 2, pose="walk")
    # the rigs: Mikasa balanced on rig 1, EREN UPSIDE DOWN on rig 2, Jean / Connie balanced on rigs 3 / 4; a waiting file
    rope = flat("G3Rope", "#d8d4cc", 0.8)
    acts, bm = [], bmesh.new()
    for k, (u, who) in enumerate(zip(RIGS_U, ("mikasa", "eren", "jean", "connie"))):
        x, y = cuv(u, 38.0); q = F((x, y, 0.0)); g = ground_ray(q.x, q.y)
        if who == "eren":
            e = PK.person("eren", (q.x, q.y, g + 2.05), yaw=0.0, pose="stand")
            e.rotation_euler = (math.pi, 0.0, 0.0)          # feet up, head ~0.3 m over the ground
            hip = g + 1.15
        else:
            e = PK.person(who, (q.x, q.y, g + 0.75), yaw=0.0, pose="stand"); hip = g + 1.7
        acts.append(e)
        for sx in (-0.25, 0.25):
            L.cyl(bm, (q.x + sx * 4, q.y, g + 7.35), (q.x + sx, q.y, hip), 0.035, 0.035, seg=4)
        S.setdefault("rig_xy", {})[who] = (q.x, q.y, hip)
    S["rig_ropes"] = L.obj_from_bm("G3RigRopes", bm, [rope], cl)
    S["rig_acts"] = Group(acts)
    S["rig_file"] = crowd(["cadet"], cuv(23, 27), 56.0, 4.0, 40, yaw=0.0, formation="grid", spacing=(1.4, 1.3), seed=105)
    # seasons: 30 sparring pairs + a running file round the bowl
    rnd = random.Random(106); pairs = []
    for k in range(30):
        u, v = rnd.uniform(-95, -25), rnd.uniform(-32, 30); a = rnd.uniform(0, math.pi)
        for s_ in (-1, 1):
            pairs.append(person("cadet:%d" % rnd.randrange(8), cuv(u + s_ * 0.6 * math.cos(a), v + s_ * 0.6 * math.sin(a)),
                                yaw=a + (math.pi / 2 if s_ < 0 else -math.pi / 2), pose="walk"))
    S["spar"] = Group(pairs)
    S["runners"] = Group([person("cadet:%d" % (k % 8), cuv(0, 0), pose="run") for k in range(36)])
    # graduation night: 218 graduates (9 x ~24) facing the mess-hall stair, the top 10 in a row at the stair foot facing them
    S["grads"] = crowd(["cadet"], cuv(-15, -2), 30.0, 12.0, 218, yaw=math.pi, formation="grid", spacing=(1.25, 1.35), pose="salute",
                       seed=107)
    top = ["mikasa", "reiner", "annie", "bertholdt", "eren", "jean", "marco", "connie", "sasha", "christa"]
    S["top10"] = Group([person(n, cuv(-22.0 + 1.6 * k, -21.0), yaw=0.0, pose="salute") for k, n in enumerate(top)])
    huts = [(-100, 66), (-78, 66), (-5, 66), (17, 66), (39, 66), (61, 66), (90, -32), (92, 0), (90, 30)]
    rr = np.random.default_rng(108)
    S["grad_go"] = []                                   # (start xy, hut xy, depart time, speed) per graduate + top 10
    for e in S["grads"].e + S["top10"].e:
        h = huts[rr.integers(len(huts))]; hq = F((*cuv(*h), 0.0))
        S["grad_go"].append((Vector(e.location), Vector((hq.x, hq.y, e.location.z)), float(rr.uniform(76.3, 77.6)), float(rr.uniform(38, 55))))

def _ellipse_pt(a):
    return cuv(98.0 * math.cos(a), 70.0 * math.sin(a))

def shadis_uv(t):
    a, b_ = B["enlist"]
    ph = (t - a) * 7.0                                  # time-lapse stroll along the front, 30 m each way
    u = -67.0 + 30.0 * (1 - abs(((ph / 30.0) % 2.0) - 1.0))
    return u, -9.0, 1.0 if (int(ph / 30.0) % 2 == 0) else -1.0

def update_camp(t):
    st = S.get("camp")
    if st is None:
        return
    rise = ss(B["FT0"], B["FT0"] + 3.7, t)
    S["camp_root"].scale = (1.0, 1.0, max(1e-3, rise))
    for o in st["objs"]:
        h = rise < 0.01
        if o.hide_render != h and not (o.name in ("CP_Windows", "CP_BrazierFire", "CP_Glow")):
            o.hide_render = h
    S["camp_mod"].set_night(st, ss(B["grad"][0] + 0.4, B["grad"][0] + 1.8, t))
    en = B["enlist"]
    S["recruits"].show(en[0] - 1.5 <= t < en[1] + 0.3)
    sh = S["shadis"]
    if en[0] - 1.5 <= t < B["rig"][1]:
        u, v, d = shadis_uv(min(t, en[1]))
        if t >= en[1]:
            u, v, d = 0.0, 30.0, 1.0                       # by the rigs
        q = F((*cuv(u, v), 0.0)); sh.location = (q.x, q.y, ground_ray(q.x, q.y) + 0.05)
        sh.rotation_euler = (0, 0, -math.pi / 2 if d > 0 else math.pi / 2)
        sh.hide_render = False
    else:
        sh.hide_render = True
    rg = B["rig"]
    rv = rg[0] - 0.4 <= t < rg[1] + 0.6
    S["rig_acts"].show(rv); S["rig_file"].show(rv); S["rig_ropes"].hide_render = not rv
    sv = B["seasons"][0] <= t < B["seasons"][1]
    S["spar"].show(sv); S["runners"].show(sv)
    if sv:
        for k, e in enumerate(S["runners"].e):
            a = -(t - B["seasons"][0]) * 0.55 - k * 0.075   # a running file, clockwise round the floor
            x, y = _ellipse_pt(a); x2, y2 = _ellipse_pt(a - 0.01)
            q = F((x, y, 0.0)); e.location = (q.x, q.y, ground_ray(q.x, q.y) + 0.05)
            e.rotation_euler = (0, 0, math.atan2(-(x2 - x), (y2 - y)))
    gv = t >= B["grad"][0] + 0.2
    vis = []
    for e, (p0, p1, td, sp) in zip(S["grads"].e + S["top10"].e, S["grad_go"]):
        if not gv:
            vis.append(False); continue
        d = (p1 - p0).length; u = max(0.0, t - td) * sp / max(d, 1e-3)
        if u >= 1.0:
            vis.append(False); continue
        p = p0.lerp(p1, u); p.z = p0.z
        e.location = p; vis.append(True)
    n = len(S["grads"].e)
    S["grads"].show(np.array(vis[:n])); S["top10"].show(np.array(vis[n:]))

def _track_shadis(t):
    if S.get("shadis") is None or S["shadis"].hide_render:
        return None
    q = S["shadis"].location
    return (q.x, q.y + (0.0 if PART == "A" else segtime.SET_OFF_Y), q.z + 2.0)

def _track_rig(who):
    def f(t):
        p = S.get("rig_xy", {}).get(who)
        if p is None or not (B["rig"][0] - 0.4 <= t < B["rig"][1] + 0.6):
            return None
        return (p[0], p[1] + segtime.SET_OFF_Y, p[2] + 1.2)
    return f

TRACK.update({"Shadis": _track_shadis, "Eren": _track_rig("eren"), "Mikasa": _track_rig("mikasa")})

# ---------------------------------------------------------------------- the sunset ridge (march 11-18 s): 11 titans backlit on a crest
# bible: set (-600, -2700) = M (-600, -1830); moved to M (-850, -1750) so it stays in the re-driven march camera's frame while it
# looks WNW into the low sun (compass 285 deg) at 42-47 s.  swarm845 titan meshes (faces kept), march846's deform law.
RIDGE_C, RIDGE_HALF, RIDGE_H = (-850.0, -1750.0), (140.0, 380.0), 30.0

def ridge_h(x, y):
    u, v = (x - RIDGE_C[0]) / RIDGE_HALF[0], (y - RIDGE_C[1]) / RIDGE_HALF[1]
    return RIDGE_H * math.exp(-1.6 * (u * u + v ** 4))

def build_ridge(cl):
    import swarm845 as SW
    gm = bpy.data.materials.get("WD_Ground") or flat("G3RidgeGrass", "#55673a")
    bm = bmesh.new(); nu, nv = 36, 60
    hx, hy = RIDGE_HALF[0] * 2.4, RIDGE_HALF[1] * 1.6
    V = []
    for i in range(nu + 1):
        row = []
        for j in range(nv + 1):
            x = RIDGE_C[0] - hx + 2 * hx * i / nu; y = RIDGE_C[1] - hy + 2 * hy * j / nv
            q = F((x, y, 0.0)); row.append(bm.verts.new((q.x, q.y, ground_ray(q.x, q.y) - 0.5 + ridge_h(x, y))))
        V.append(row)
    for i in range(nu):
        for j in range(nv):
            f = bm.faces.new((V[i][j], V[i + 1][j], V[i + 1][j + 1], V[i][j + 1])); f.smooth = True
    S["ridge_hill"] = L.obj_from_bm("G3RidgeHill", bm, [gm], cl)
    rng = random.Random(1846)
    specs, gt, tmat = [], SW.Geo(), []
    NT = 11
    for j in range(NT):
        H = rng.uniform(7.0, 15.0)
        sp = dict(name=f"r{j}", H=H, g=rng.uniform(1.0, 1.3), al=rng.uniform(0.9, 1.2), hs=rng.uniform(0.9, 1.3),
                  skin=rng.randrange(len(SW.T_SKINS)), hair=rng.choice([None, 0, 1, 2]))
        n0 = len(gt.fc)
        SW.titan_geo(gt, j, sp)
        hb = len(SW.T_SKINS)
        base = [sp["skin"], hb + (sp["hair"] if sp.get("hair") is not None else 0), hb + len(SW.T_HAIRS)]
        tmat += [base[c] for c in gt.fc[n0:]]
        specs.append(sp)
    tm = [L.mat(f"G3R_tskin{i}", c, 0.6) for i, c in enumerate(SW.T_SKINS)] + [L.mat(f"G3R_thair{i}", c, 0.7) for i, c in enumerate(SW.T_HAIRS)] \
        + [L.mat("G3R_teeth", (0.85, 0.80, 0.70), 0.5)]
    RT = gt.finish()
    tob = SW._mesh("G3RidgeTitans", RT, gt.f, tmat, tm, cl)
    S["ridge"] = dict(RT=RT, tob=tob, H=np.array([s["H"] for s in specs]), v0=np.array([rng.uniform(-260, 260) for _ in range(NT)]),
                      sp=np.array([rng.uniform(1.0, 2.2) for _ in range(NT)]), ph=np.array([rng.uniform(0, 6.28) for _ in range(NT)]))

def update_ridge(t):
    R = S.get("ridge")
    if R is None:
        return
    import swarm845 as SW
    NT = len(R["H"])
    v = R["v0"] + R["sp"] * (t - 31.3) * 3.0           # wander north along the crest (time-lapse)
    x = np.full(NT, RIDGE_C[0]) + 8.0 * np.sin(v / 90.0 + R["ph"]); y = RIDGE_C[1] + v
    z = np.array([gM(a, b_) - 0.5 + ridge_h(a, b_) for a, b_ in zip(x, y)])
    ph = 2 * np.pi * (t * 1.4 + R["ph"])
    Ar = np.zeros((NT, 7)); Ae = np.zeros((NT, 7)); sw = np.sin(ph) * 0.35
    Ar[:, 1] = sw; Ar[:, 2] = -sw; Ar[:, 3] = -0.7 * sw; Ar[:, 4] = 0.7 * sw; Ar[:, 5] = Ar[:, 4]; Ar[:, 6] = Ar[:, 3]
    Ae[:, 5] = Ae[:, 6] = 0.3
    lean = np.full(NT, -0.08)
    yaw = np.zeros(NT)                                   # facing north (+y), toward Trost
    P = np.array([tuple(F((a, b_, c))) for a, b_, c in zip(x, y, z)])
    co = SW._deform(R["RT"], Ar, Ae, lean, np.ones(NT), yaw, P)
    R["tob"].data.vertices.foreach_set("co", co.astype(np.float32).ravel()); R["tob"].data.update()

# ---------------------------------------------------------------------- part A: g2's own end state (seg_g2's canal / quays / ferries)
G2_T = 32.0                                            # g3 t 0 = g2 t 32 (its end)

def build_partA(cl):
    import seg_g2 as G2M
    import smokecards
    sc = bpy.context.scene
    if sc.render.engine.startswith("BLENDER_EEVEE"):        # g2's (= g1's) Eevee look: the seam frame must match render_g1/g2
        ev = sc.eevee
        for k_, v_ in (("use_raytracing", False), ("shadow_resolution_scale", 0.5), ("shadow_ray_count", 1), ("shadow_step_count", 4),
                       ("use_fast_gi", False)):
            try:
                setattr(ev, k_, v_)
            except Exception:
                pass
    G2M.L = L; G2M.G1 = sys.modules.get("g1_set"); G2M.PK = PK; G2M.SMC = smokecards
    G2M.S["coll"] = cl; G2M.S["cards"] = []; G2M.S["M"] = G2M.mats()
    # settle_g1 first: it BAKES g1's outer-gate breach boolean (evaluated per frame it costs ~50 s/frame) and leaves the town as
    # g2 shows it (terrace lifts, lumps, Colossal / fire smoke hidden)
    for nm, fn in (("settle_g1", G2M.settle_g1), ("ground", lambda: G2M.build_ground(cl)), ("ferries", lambda: G2M.build_ferries(cl))):
        try:
            fn()
        except Exception:
            import traceback; traceback.print_exc(); say("part A: seg_g2", nm, "FAILED")
    cc = bpy.data.collections.get("ColossalTitan")
    if cc:
        cc.hide_render = True
    S["G2M"] = G2M; S["G1"] = G2M.G1

def update_partA(t):
    G2M = S.get("G2M")
    if not G2M:
        return
    try:
        G2M.ferries_update(G2_T + t)
        for cs, w in G2M.S["cards"]:
            cs.update(G2_T + t, wind=w)
    except Exception:
        import traceback; traceback.print_exc()

# ---------------------------------------------------------------------- light
EXP_BASE = -1.5                                        # scene.py's exposure in both sets (g4: exp0 + offset)

def light_capture():
    sc = bpy.context.scene; w = sc.world
    so = bpy.data.objects.get("Sun")
    if so is None or so.type != "LIGHT":
        ld = bpy.data.lights.new("Sun", "SUN"); so = bpy.data.objects.new("Sun", ld); sc.collection.objects.link(so)
    nodes = w.node_tree.nodes if (w and w.use_nodes) else []
    hz = bpy.data.node_groups.get("EeveeHaze")
    hk = hm = None
    if hz is not None:
        hk = next((n for n in hz.nodes if n.type == "MATH" and n.operation == "MULTIPLY"), None)
        hm = next((n for n in hz.nodes if n.type == "MIX"), None)
    S["L0"] = dict(sun=so, others=[o for o in bpy.data.objects if o.type == "LIGHT" and o.data.type == "SUN" and o is not so],
                   ramps=[n for n in nodes if n.type == "VALTORGB"], skies=[n for n in nodes if n.type == "TEX_SKY"],
                   bgs=[(n, n.inputs[1].default_value) for n in nodes if n.type == "BACKGROUND"], hk=hk, hm=hm,
                   mist=(w.mist_settings if w else None), exp0=sc.view_settings.exposure)
    L0 = S["L0"]
    say("light capture: exposure %.2f, bgs %s, %d ramps (%s), %d skies, haze %s, other suns %d" % (
        L0["exp0"], [round(s, 3) for _, s in L0["bgs"]], len(L0["ramps"]), [len(r.color_ramp.elements) for r in L0["ramps"]],
        len(L0["skies"]), hk is not None, len(L0["others"])))

def light(t):
    t = float(t)
    v = light_values(t); L0 = S["L0"]; d = v["d"]
    so = L0["sun"]
    so.rotation_euler = Vector(tuple(-d)).to_track_quat("-Z", "Y").to_euler()
    so.data.energy = v["en"]; so.data.color = v["col"]; so.hide_render = False
    for o in L0["others"]:
        o.hide_render = True
    for s in L0["skies"]:
        try:
            s.sun_elevation = math.radians(max(0.0, v["el"])); s.sun_rotation = math.atan2(d[1], d[0])
        except Exception:
            pass
    for n, s0 in L0["bgs"]:
        n.inputs[1].default_value = v["amb"] if s0 < 1.0 else s0 * v["camk"]
    for r in L0["ramps"]:
        el = r.color_ramp.elements
        el[0].color = (*v["hor"], 1)
        (el[1] if PART == "A" else el[-1]).color = (*v["zen"], 1)       # part A: as seg_g2.light (first two stops)
    vs = bpy.context.scene.view_settings
    vs.exposure = EXP_BASE + v["gex"]
    try:
        vs.use_curve_mapping = True
        cm = vs.curve_mapping
        cm.white_level = tuple(1.0 / max(g, 1e-3) for g in v["gain"]); cm.black_level = (0.0, 0.0, 0.0); cm.update()
    except Exception as ex_:
        if not S.get("grade_warned"):
            say("colour grade failed:", ex_); S["grade_warned"] = True
    if L0["hk"] is not None:
        L0["hk"].inputs[1].default_value = v["mist_k"]
    if L0["hm"] is not None:
        L0["hm"].inputs["B"].default_value = (*v["mist_rgb"], 1.0)
    if L0["mist"] is not None:
        L0["mist"].depth = v["mist_depth"]
    G1 = S.get("G1")
    if PART == "A" and G1 and G1.STATE.get("sky_mat"):  # g1's mackerel layer: g2's end dusk pinks, darkening into the night
        k = 1.0 - 0.93 * ss(0.4, B["night"][0], t)
        for nd in G1.STATE["sky_mat"].node_tree.nodes:
            if nd.type == "MIX" and nd.data_type == "RGBA":
                nd.inputs["A"].default_value = tuple(c * k for c in (0.78, 0.40, 0.38)) + (1.0,)
                nd.inputs["B"].default_value = tuple(c * k for c in (0.95, 0.60, 0.52)) + (1.0,)

# ---------------------------------------------------------------------- module contract (render_seg.py)
def build(site):
    global L, PK, SITE
    SITE = site; L = site["L"]
    t0 = time.time()
    import people_kit as PK_
    PK = PK_
    PK.PRESETS.setdefault("shadis", dict(H=1.74, sh=1.08, hair="bald", hc="h_white", outfit="cadet"))   # instructor (bald)
    _GROUND_OBS[:] = [o for o in (bpy.data.objects.get("Terrain"), bpy.data.objects.get("WD_Ground")) if o is not None]
    w0, w1 = _window(); parts = parts_for(w0, w1)
    S["parts"] = parts
    say(f"part {PART}, window {w0:g}-{w1:g} s, parts {sorted(parts)}, ground objects {[o.name for o in _GROUND_OBS]}")
    cl = coll("G3")
    if PART == "A":
        build_partA(cl)
    else:
        TR = site["TR"]
        try:
            TR.set_breach(False); TR.set_glow(0.0); TR.set_wagon(False)
        except Exception as ex:
            say("set hooks failed:", ex)
        MR = march_module()                             # static 846 dressings, identical in every part-B window
        MR.dress_fields(); MR.clear_plain()
    steps = []
    if "night" in parts:
        steps.append(("night", lambda: build_night(cl)))
    if "rose" in parts:
        steps += [("shelter", lambda: build_shelter(cl)), ("clearing", lambda: build_clearing(cl)), ("courtyard", lambda: build_courtyard(cl)),
                  ("snow_rose", lambda: S.__setitem__("flakes_rose", Flakes("G3SnowRose", ((-700, 250), (420, 1350), (0, 320)), 26000, 0.2, cl)))]
    if "march" in parts:
        steps += [("march", lambda: build_march(cl)), ("ridge", lambda: build_ridge(cl))]
    if "camp" in parts:
        steps += [("camp", lambda: build_camp(cl)),
                  ("snow_camp", lambda: S.__setitem__("flakes_camp", Flakes("G3SnowCamp", ((-1750, -1200), (1150, 1800), (0, 260)), 16000, 0.2, cl, seed=8)))]
    steps.append(("surface", build_surface))
    for nm, fn in steps:
        ts = time.time()
        try:
            fn()
        except Exception:
            import traceback; traceback.print_exc(); say("BUILD STEP FAILED:", nm)
        say(f"build {nm} {time.time() - ts:.1f}s")
    light_capture()
    say(f"build total {time.time() - t0:.1f}s")

def update(t):
    t = float(t)
    set_night_lights(t); set_surface(t)
    if PART == "A":
        update_partA(t)
        return
    for fn in (update_rose, update_march, update_ridge, update_camp, update_gate):
        try:
            fn(t)
        except Exception:
            import traceback; traceback.print_exc(); say(f"UPDATE FAILED: {fn.__name__} t={t:.2f}")
    sn, _ = surf_values(t)
    for k in ("flakes_rose", "flakes_camp"):
        if S.get(k):
            S[k].update(t, sn if (t < B["CAM_IN"]) == (k == "flakes_rose") else 0.0)

def check():
    cam_report(quiet=False)
    say("parts", sorted(S.get("parts", ())), "| light 0:", {k: (np.round(v, 3) if isinstance(v, np.ndarray) else v) for k, v in light_values(0.0).items() if k in ("el", "en", "amb", "gex")},
        "| light 78.4 = g4 t0:", light_values(DUR)["en"] == _G4L[3] and light_values(DUR)["gex"] == _G4G[2])
    L0 = S.get("L0")
    if L0:
        say("lighting-sky s0 (trost expects 0.25 for the g4 night):", [round(s, 3) for _, s in L0["bgs"]], "exposure at build", L0["exp0"])
    hill = S.get("ridge_hill")
    if hill is not None:
        zs = [v.co.z for v in hill.data.vertices]
        q = F((RIDGE_C[0], RIDGE_C[1], 0.0))
        say(f"ridge hill z {min(zs):.1f}..{max(zs):.1f}, ground_ray at centre {ground_ray(q.x, q.y):.1f}, L.height {float(L.height(q.x, q.y)):.1f}")
        for ob in _GROUND_OBS:
            mi = ob.matrix_world.inverted(); o = mi @ Vector((q.x, q.y, 600.0))
            say("  ray", ob.name, ob.ray_cast(o, (mi.to_3x3() @ Vector((0, 0, -1))).normalized(), distance=5000.0)[:2])
    MR = S.get("MR")
    if MR is not None:                                   # the re-driven march camera keeps march846's ends
        for tau in (0.0, MARCH_T_END):
            l0, k0, n0 = MR.cam_at(tau); l1, k1, n1 = MARCH.eval(B["march"][0] + tau)
            say(f"march846.cam_at({tau}) set {tuple(round(x, 1) for x in l0)} | g3 M {tuple(round(float(x), 1) for x in l1)} (M = set + 870 y)")

if __name__ == "__main__":
    cam_report()
