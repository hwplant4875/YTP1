"""g3 FLIGHT NORTH, FARM, 846 MARCH, 104th CAMP (SCENE_BIBLE_v2 B.g3; v5 local 61.8 s = 40.4 s of VIDEO; frames W -> M).
Driven by aot/render_seg.py (render_seg.sh VCLOCK=1).  Every frame is a pure function of the local time t (0..DUR); the
video plays it through segtime.TMAP["g3"]: slope 2 everywhere, eased to slope 1 (REAL time) over the march846 span.

v5 (owner 10/27 07:34, binding): farm building faster + clearly visible; NO winter (no snow / snowmelt / winter light),
straight to 846; the 250,000 march on march846.py's ORIGINAL camera (angle, path, real-time pacing); no sun glow cards /
sunset ridge hold; the camp seasons only as a quick summer -> autumn time-lapse; camp104's pole field removed.

TWO SETS (allowed by the lead: "separate sets per sub-part"), one camera:
  part A  t 0 .. BEATS["set_switch"]   SEG_SET=shiganshina (SEG_FRAME=W): the g2 end look (scene.py Shiganshina 845 + g1's
          plug-ins + g2's own canal / quays / ferries, imported from seg_g2), dusk -> night.  CAM is served in frame W.
  part B  set_switch .. DUR            AOT_SET=trost (frame M): the night flight on, dawn, the relief complex / shelter camp /
          the farm clearing at the Rose foot, the 846 gathering, march846 (its own simulation + ORIGINAL spline, re-lit), the
          flight to the 104th camp (camp104.py, shared with g4) and the camp beats.
  The switch sits at full night over open world ground; neither town core is in frame then.  Part-B windows only build what
  their window can see (PART_SPANS, from the driver's --t0/--t1; with --vclock those are VIDEO seconds and are mapped here).
    VCLOCK=1 SEG=g3 SEG_SET=shiganshina WIN=0,3 bash render_seg.sh      part A (local 0-6 = video 0-3)
    VCLOCK=1 SEG=g3 WIN=3,13.6 bash render_seg.sh  ... (part B windows) ; VCLOCK=1 SEG=g3 ENCODE_ONLY=1 bash render_seg.sh

Story (local seconds | video seconds; every time lives in BEATS + segtime.G3_MARCH):
  0-17.7    | 0-8.85    flight north (explicit profile 45 -> 369 m/s), ferries, night (HUD "845: territory reduced to Wall
                         Rose"), Trost window dots, dawn; from 13.0 the FARM: the conifer stand beyond Rose felled S -> N
  17.7-26.6 | 8.85-13.55 the farm hold (H2 small zoom-in, plots ploughed -> planted -> green), then one turn via the west over
                         the relief complex while the hooded 846 crowd fills the avenue (HUD "846: retake Wall Maria"), gate
                         opens; the clock eases 2 -> 1 into CAM_IN
  26.6-44.6 | 13.55-31.55 march846 at REAL time on its original spline; overcast, dimming as the column dies, a natural low gold
                         sun breaking through over the last ~8 s
  44.6-55.0 | 31.55-37.0 eased 1 -> 2; one night over the high crossing (846 -> 847), the camp rises; descent onto the camp
  55.0-61.8 | 37.0-40.4  enlistment (250 recruits, SHADIS) + the rigs (EREN upside down, MIKASA) at once with a small zoom-in,
                         a quick summer -> autumn time-lapse (no winter), graduation dusk/night, drifting to g4 G0 (unchanged)
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

DUR = segtime.DUR["g3"]                   # 61.6 (v5)
_GM = segtime.G3_MARCH                    # (27.0, 45.0): the march span, played at slope 1 by segtime.TMAP["g3"]
PART = "A" if os.environ.get("SEG_FRAME", "M").upper() == "W" else "B"
MW = segtime.M_OFF_Y                      # M = W - (0, 4130)

# ====================================================================== BEATS (the ONE re-time table, local seconds)
BEATS = dict(
    # ---- flight (0-17.7): FA keys and the speed profile
    FA0=0.0, FA1=3.7, FA2=7.3, FA3=10.6, FA4=12.9, H=17.7,
    prof=(45.7, 369.0, 3.7, 9.0),          # v0 (= g2 seam |v|), cruise m/s, ramp end, cruise end (decel to rest at H)
    ferries=(0.0, 3.7),                    # ferries pass below
    set_switch=6.0,                        # part A (Shiganshina set) -> part B (Trost set), at full night over open ground
    dusk_night=(0.4, 3.0), night=(3.0, 5.6), dawn=(5.6, 10.6),   # v6 (owner 10:53): short night, sunrise, Trost in MORNING light
    hud_845=(5.2, 9.0),                    # "845: territory reduced to Wall Rose"
    lights_off=(6.4, 9.6),                 # Trost window dots / torches fade (v6: dawn earlier)
    # ---- farm + 846 (17.7 - CAM_IN): the clearing beyond Rose felled + ploughed + planted (time-lapse, from 13.0 during the
    #      approach), a small zoom-in at H2, then one turn via the west to CAM_IN while the 846 crowd fills the avenue.  NO winter.
    morning=(10.6, 17.7), H2=19.6, P1=21.2, P2=22.9, P3=24.6, CAM_IN=_GM[0],
    courtyard=(14.0, 21.0),                # the relief cloister packed, ration queue busy
    fell=(13.0, 17.2),                     # the conifer stand on the clearing is felled south -> north
    crop=(15.6, 20.4),                     # plots ploughed -> planted -> green, south -> north
    workers=(13.0, 21.0),
    crowd846=(21.5, 25.5),                 # the hooded 846 crowd fills the avenue
    hud_846=(23.4, 27.4),                  # "846: retake Wall Maria"
    gate_open=(25.0, 26.6),                # v6 (owner 10:53): opens INSIDE the held high gate view; the column pours from 26.6
    # ---- march846 (segtime.G3_MARCH, real time in the video): its own clock tau = t - march[0]; natural low gold sun late
    march=_GM, gold=(_GM[0] + 9.0, _GM[1]),
    # ---- flight to the camp + the camp (march end .. DUR)
    FT0=_GM[1], FT1=_GM[1] + 4.8, FT2=_GM[1] + 8.0, FT3=_GM[1] + 10.4, FT4=57.0, FT5=58.4, FT7=DUR,
    camp_rise=(_GM[1] + 1.6, _GM[1] + 6.4),
    enlist=(54.0, 57.2), rig=(54.6, 57.4), seasons=(57.2, 58.6), grad=(58.6, DUR),
    tag_shadis=(53.8, 57.1), tag_eren=(54.2, 57.4), tag_mikasa=(54.5, 57.4),
)
B = BEATS

# ====================================================================== camera (bible keys; fixes per design_specs/camcheck_report.md)
def W2M(p):
    return (float(p[0]), float(p[1]) - MW, float(p[2]))

# flight: FA0..FA3 (W) + FA4, H (M), driven by the explicit speed profile (allowed speed exception), v_in = g2 seam direction
_S_IN = segtime.seam("g2_g3")
FLIGHT_KEYS = [(B["FA" + str(i)], W2M(c), W2M(l), ln) for i, (_, c, l, ln) in enumerate(camkeys.G3_FLIGHT_W)] + [
    (B["FA4"], (60.0, 170.0, 300.0), (-268.0, 805.0, 0.0), 30.0),          # FA4 = W (60, 4300, 300): over Wall Rose
    (B["H"], tuple(map(float, camkeys.G3_CAMPS_M[1][1])), tuple(map(float, camkeys.G3_CAMPS_M[1][2])), 28.0)]   # H (look: the clearing)
_PV = B["prof"]
V_H = (-1.5, 4.5, 1.5)          # QA 10/27: no stall at H; the flight ends in a 5 m/s drift toward H2 (was: at rest)

def speed_profile_end(v0, t_ramp, t_cruise_end, t_end, v_end, total):
    """camchan.speed_profile with an end speed: ramp v0 -> V over t_ramp, cruise to t_cruise_end, constant deceleration to
    v_end at t_end; V is solved so the distance equals `total` exactly (so v0 and v_end are the true speeds)."""
    tr, tc, te = t_ramp, t_cruise_end, t_end
    V = (total - v0 * tr / 2 - v_end * (te - tc) / 2) / (tr / 2 + (tc - tr) + (te - tc) / 2)
    d1 = (v0 + V) / 2 * tr; d2 = V * (tc - tr)
    def f(t):
        t = min(max(t, 0.0), te)
        if t <= tr: d = v0 * t + (V - v0) / tr * t * t / 2
        elif t <= tc: d = d1 + V * (t - tr)
        else:
            u = t - tc; d = d1 + d2 + V * u - (V - v_end) / (te - tc) * u * u / 2
        return d / total
    f.V = V
    return f

_FL0 = camchan.CamPath(FLIGHT_KEYS, v_in=_S_IN["vel"], v_out=V_H)
_FPROF = speed_profile_end(_PV[0], _PV[2], _PV[3], B["H"] - B["FA0"], float(np.linalg.norm(V_H)), _FL0.loc.total)
FLIGHT = camchan.CamPath(FLIGHT_KEYS, v_in=_S_IN["vel"], v_out=V_H, profile=_FPROF)

# farm + 846 (v5, owner 10/27): H .. CAM_IN.  H2 is a small zoom-in on the clearing (the farm time-lapse), then ONE turn via
# the west (~115 deg, was 160) over the relief complex and the avenue filling with the 846 crowd, to CAM_IN.  The video clock
# eases 2 -> 1 over the last 1.2 video s before CAM_IN (segtime.TMAP["g3"]), so the march starts at its own real-time speed.
CI = camkeys.CAM_IN
_CK = camkeys.G3_CAMPS_M[1:7]                                       # H, H2, P1, P2, P3, CAM_IN (positions / look-ats / lens)
CAMP_KEYS = [(B[n], tuple(map(float, k[1])), tuple(map(float, k[2])), float(k[3])) for n, k in zip(("H", "H2", "P1", "P2", "P3", "CAM_IN"), _CK)]
_LH = FLIGHT.eval(B["H"])[1] - FLIGHT.eval(B["H"] - 1e-3)[1]
CAMPS = camchan.CamPath(CAMP_KEYS, v_in=V_H, look_v_in=tuple(float(x) / 1e-3 for x in _LH), v_out=CI["vel"], look_v_out=CI["look_vel"])

# march846 camera: the ORIGINAL march846.py spline, restored (owner 10/27 07:34: "the original camera angle and speed were
# good; now it points at a weird place").  march846.CAM_KEYS + its time Hermite (_tangents / _herm, cam_at) transcribed
# 1:1 here in pure numpy (march846.py needs bpy); seg_g3.check() compares it with MR.cam_at.  march846's clock tau = t -
# march[0] runs at REAL time in the video (TMAP slope 1 over the march span), i.e. exactly the original preview's pacing.
# It breaks the A3 limits on purpose (camchan: ~458 m/s, ~57 deg/s, 81 m, pitch 11): the owner's preference wins.
# Set frame (march846's GATE = Trost outer gate (0, -870); outward = south, lateral +b = east); M = set + (0, 870).
_MG, _MF, _MR = np.array([0.0, -870.0]), np.array([0.0, -1.0]), np.array([1.0, 0.0])
def _gp(a, b, z):
    p = _MG + _MF * a + _MR * b
    return (float(p[0]), float(p[1]), float(z))
MARCH_T_END = 18.0
# g3 v6 (owner 10:53 on g3_flight_v5): "the camera must barely move" - a HIGH aerial (880-1170 m, pitch 48-67) on the
# column's west side, so the column fills the frame width; it barely drifts and the lens opens 40 -> 24 mm as the column
# lengthens; the gate is in frame from tau 0
# (the column pours out of it until march846.T_TAIL 8.6), in its last 6 s it pans slowly west toward the camp (to-camp continues the turn).
# (march846's original spline: renders before v6 / git history.)
MARCH_CAM_KEYS = [   # v7 (QA batch1 P1): NEAR TOP-DOWN hold low over the column (pitch 60-66, 520-600 m) so it crosses the
                     # whole frame and the people read; key 0 = the camps seam, key 18 = the to-camp seam (both unchanged)
    (0.0,  _gp(200, -780, 880),   _gp(300, 0, 0),    40),         # the gate in frame as the column pours out
    (3.0,  _gp(380, -170, 360),   _gp(440, 0, 0),    36),         # v8 (g3 v7 "still a thin strip"): ~230-280 m over the
    (6.0,  _gp(650, -90, 235),    _gp(700, 0, 0),    38),         # column, pitch ~68, 38 mm: the column band fills ~1/3 of
    (10.0, _gp(900, -90, 245),    _gp(950, 0, 0),    38),         # the frame height and riders / carts read
    (14.0, _gp(1050, -120, 290),  _gp(1110, 0, 0),   34),         # the titans hit, the column dies
    (18.0, _gp(760, -1080, 1150), _gp(300, -900, 0), 26),         # pan north toward the camp (to-camp needs no spin)
]
MARCH_OUT_VEL = (0.0, 50.0, -15.0)                                 # M: drifting north, easing down toward FT1

def _m_tangents(T, P, v_in=None, v_out=None):
    n = len(T); M = []
    for i in range(n):
        if i == 0:
            M.append(np.array(v_in, float) if v_in is not None else (P[1] - P[0]) / (T[1] - T[0]))
        elif i == n - 1:
            M.append(np.array(v_out, float) if v_out is not None else (P[-1] - P[-2]) / (T[-1] - T[-2]))
        else:
            d0 = (P[i] - P[i - 1]) / (T[i] - T[i - 1]); d1 = (P[i + 1] - P[i]) / (T[i + 1] - T[i])
            h0, h1 = T[i] - T[i - 1], T[i + 1] - T[i]
            M.append((d0 * h1 + d1 * h0) / (h0 + h1))
    return M

def _m_herm(T, P, M, t):
    t = min(max(t, T[0]), T[-1])
    i = min(len(T) - 2, int(np.searchsorted(T, t, side="right") - 1))
    h = T[i + 1] - T[i]; s = (t - T[i]) / h
    h00, h10, h01, h11 = 2 * s ** 3 - 3 * s ** 2 + 1, s ** 3 - 2 * s ** 2 + s, -2 * s ** 3 + 3 * s ** 2, s ** 3 - s ** 2
    return h00 * P[i] + h10 * h * M[i] + h01 * P[i + 1] + h11 * h * M[i + 1]

class _MarchCam:
    """march846.cam_at(tau) in frame M, tau = t - march[0] (local t)."""
    def __init__(self):
        T = np.array([k[0] for k in MARCH_CAM_KEYS], float)
        PL = [np.array(k[1], float) + np.array([0.0, 870.0, 0.0]) for k in MARCH_CAM_KEYS]
        PT = [np.array(k[2], float) + np.array([0.0, 870.0, 0.0]) for k in MARCH_CAM_KEYS]
        LN = [np.array([math.log(k[3])]) for k in MARCH_CAM_KEYS]
        self.T, self.PL, self.PT, self.LN = T, PL, PT, LN
        self.ML = _m_tangents(T, PL, v_out=np.array(MARCH_OUT_VEL)); self.MT = _m_tangents(T, PT)
        self.MN = _m_tangents(T, LN, v_in=np.zeros(1), v_out=np.zeros(1))
        self.notes = ["g3 v6 high top-down march hold (time Hermite), real time inside g3: height > hmax on purpose (owner)"]
    def eval_tau(self, tau):
        loc = _m_herm(self.T, self.PL, self.ML, tau); tgt = _m_herm(self.T, self.PT, self.MT, tau)
        return loc, tgt, math.exp(float(_m_herm(self.T, self.LN, self.MN, tau)[0]))
    def eval(self, t):
        return self.eval_tau(t - B["march"][0])
MARCH = _MarchCam()
MARCH_LOOK_OUT_VEL = tuple(float(x) for x in MARCH.MT[-1])                 # (0, 283.3, 13.3) = camkeys.CAM_OUT look_vel

# flight to the camp (v5): FT0 = march846.CAM_OUT with its ORIGINAL climb (0, 95, 22) and look-at rate; a high fast crossing
# (the video clock eases 1 -> 2 over the first 1.2 video s) and a descent onto the 104th camp; FT3-FT5 the camp (FT4 = a small
# zoom-in on the enlistment + the rigs), FT7 = g4 G0 (segtime g3_g4, look-at at rest: g4 starts its look-at from rest).
CO = camkeys.CAM_OUT
TOCAMP_KEYS = [(B[n], tuple(map(float, k[1])), tuple(map(float, k[2])), float(k[3]))
               for n, k in zip(("FT0", "FT1", "FT2", "FT3", "FT4", "FT5", "FT7"), camkeys.G3_TO_CAMP_M)]
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

class _VCam:
    """CAM_M on the VIDEO clock (segtime.seg_t): what the viewer sees (m/s and deg/s per video second)."""
    def __init__(self):
        self.t0, self.t1, self.notes = 0.0, segtime.vdur("g3"), []
    def eval(self, tv):
        return CAM_M.eval_m(segtime.seg_t("g3", tv))
VCAM = _VCam()

def vcheck(quiet=False):
    """camchan.check per beat on the VIDEO clock (limits = the A3 ones x SPEED: the owner's 2x)."""
    tv = lambda t: segtime.to_video("g3", t)
    runs = [("v flight", 0.0, B["H"]), ("v farm+846 (ease 2->1)", B["H"], B["CAM_IN"]), ("v march846 (real time)", *B["march"]),
            ("v to camp (ease 1->2)", B["FT0"], B["FT3"]), ("v camp", B["FT3"], DUR)]
    out = []
    for nm, a, b_ in runs:
        out.append(camchan.check(VCAM, tv(a), tv(b_), limits=dict(name=nm + " [video %.2f-%.2f s]" % (tv(a), tv(b_)), speed=None,
                                                                    yaw=60.0, flip=180.0, hmax=650.0), quiet=quiet))
    return out

def cam_report(ground=lambda x, y: 0.0, quiet=False):
    """camchan.check over the whole segment and per run; seam velocities (m/s) vs segtime / march846."""
    out = []
    for name, a, b_, lim in CAM_RUNS:
        L_ = dict(CAM_LIMITS); L_.update(lim); L_["name"] = name
        out.append(camchan.check(CAM_M, a, b_, ground=ground, limits=L_, quiet=quiet))
    L_ = dict(CAM_LIMITS); L_.update(speed=None, name="g3 whole (local 0-DUR)")
    out.append(camchan.check(CAM_M, 0.0, DUR, ground=ground, limits=L_, quiet=quiet))
    h = 1e-3
    def v(t, side):
        return (CAM_M.eval_m(t + h * (side > 0))[0] - CAM_M.eval_m(t - h * (side < 0))[0]) / h
    def lv(t, side):
        return (CAM_M.eval_m(t + h * (side > 0))[1] - CAM_M.eval_m(t - h * (side < 0))[1]) / h
    rows = [("g2->g3 in (0.0)", v(0.0, 1), np.array(_S_IN["vel"], float)),
            ("H drift (17.7) before/after", v(B["H"], -1), v(B["H"], 1)),
            ("H look before/after", lv(B["H"], -1), lv(B["H"], 1)),
            ("CAM_IN before/after", v(B["CAM_IN"], -1), v(B["CAM_IN"], 1)),
            ("CAM_IN look before/after", lv(B["CAM_IN"], -1), lv(B["CAM_IN"], 1)),
            ("CAM_OUT before/after", v(B["FT0"], -1), v(B["FT0"], 1)),
            ("CAM_OUT look before/after", lv(B["FT0"], -1), lv(B["FT0"], 1)),
            ("g3->g4 out (DUR)", v(DUR, -1), np.array(_S_OUT["vel"], float))]
    if not quiet:
        print("g3 seams (m/s):")
        for nm, a, b_ in rows:
            print("  %-30s %s | %s" % (nm, np.round(a, 1), np.round(b_, 1)))
        p0 = CAM_M.eval_m(0.0); p1 = CAM_M.eval_m(DUR)
        print("  pos 0.0  M", np.round(p0[0], 2), "look", np.round(p0[1], 2), "lens %.1f" % p0[2], "(W: +4130 y)")
        print("  pos DUR  M", np.round(p1[0], 2), "look", np.round(p1[1], 2), "lens %.1f" % p1[2], "(g4 G0", _S_OUT["pos"], _S_OUT["look"], ")")
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
# g2 v5 (owner 10/27): g2 now ENDS AT NIGHT (seg_g2.NIGHT_LIGHT / NIGHT_SKY / NIGHT_HAZE: el 24, az 205 math = 245 compass,
# e .30, (.50, .62, 1), amb .02, exposure -1.5 = EXP_BASE + 0) -> part A starts on it and settles into g4's NIGHT by 5.0
G2NIGHT = (24.0, 245.0, 0.50, (0.50, 0.62, 1.0), (0.010, 0.016, 0.045), (0.035, 0.05, 0.11), 0.035, 1.0)   # round 5: = seg_g2 NIGHT_LIFT
G2NIGHT_G, G2NIGHT_H = ((1.0, 1.0, 1.0), 0.7), (4500.0, 0.50, (0.05, 0.06, 0.11))                          # expo -1.5 + 0.7 = -0.8
MORNING = (30.0, 115.0, 3.4, (1.00, 0.96, 0.92), (0.10, 0.28, 0.74), (0.70, 0.80, 0.93), 0.25, 1.0)
SPRING = (32.0, 125.0, 3.3, (1.00, 0.96, 0.92), (0.10, 0.28, 0.74), (0.70, 0.80, 0.93), 0.25, 1.0)
SUMMER = (52.0, 165.0, 3.8, (1.00, 0.97, 0.90), (0.08, 0.26, 0.78), (0.66, 0.78, 0.94), 0.27, 1.0)
AUTUMN = (24.0, 215.0, 3.0, (1.00, 0.80, 0.58), (0.20, 0.30, 0.60), (0.88, 0.74, 0.58), 0.22, 1.0)
OVERCAST = (30.0, 160.0, 2.0, (1.00, 0.97, 0.92), (0.38, 0.42, 0.48), (0.66, 0.68, 0.70), 0.30, 1.0)
G_ID, G_AUT, G_SUM = ((1.0, 1.0, 1.0), 0.0), ((1.06, 0.98, 0.88), -0.1), ((1.02, 1.0, 0.98), 0.05)
H_OVC = (3200.0, 0.50, (0.62, 0.64, 0.68))
H_MARCH = (9000.0, 0.18, (0.66, 0.68, 0.72))
# v5 (owner 10/27): NO winter anywhere (no snow, no snowmelt, no winter light).  Farm under the clear morning; the 846 march
# overcast as march846's own mood (dimming as the column dies), then a natural low GOLD sun breaking through in the WNW for
# its last ~8 s (no glow cards / ridge hold); one night over the flight to the camp (846 -> 847); the camp: spring morning ->
# a quick summer -> autumn gold time-lapse (no winter) -> dusk -> graduation night (= g4 t 0).
GOLD = (14.0, 288.0, 3.6, (1.00, 0.78, 0.48), (0.30, 0.36, 0.58), (0.96, 0.80, 0.56), 0.20, 1.0)
DUSK2 = (6.0, 250.0, 2.6, (1.0, 0.58, 0.38), (0.22, 0.22, 0.38), (0.82, 0.50, 0.38), 0.16, 0.6)   # round 2: was elev 2 = black ground
DAWN2 = (8.0, 84.0, 2.2, (1.0, 0.72, 0.48), (0.12, 0.22, 0.52), (0.95, 0.70, 0.52), 0.19, 0.75)
NIGHT2 = (20.0, 245.0, 0.35, (0.55, 0.65, 1.0), (0.02, 0.03, 0.07), (0.06, 0.07, 0.12), 0.07, 0.3)
G_OVC, G_DIM = ((1.0, 1.0, 1.0), -0.15), ((0.98, 0.99, 1.02), -0.45)
_m0, _m1 = B["march"]
# v7 (QA batch1 P1: "first ~5 s of night nearly black"): the short flight night holds g2's end-night level with a stronger
# moon and a lifted grade instead of g4's -2.6 night (g4's NIGHT stays for the graduation night = the g4 seam)
NIGHT_A = (24.0, 245.0, 0.70, (0.55, 0.66, 1.0), (0.020, 0.032, 0.08), (0.07, 0.09, 0.18), 0.055, 1.0)   # round 2: +moon
NIGHT_AG, NIGHT_AH = ((0.95, 0.98, 1.08), 0.6), (4500.0, 0.45, (0.06, 0.08, 0.14))
LKEYS = [  # (t, light, grade, haze)
    (0.0, G2NIGHT, G2NIGHT_G, G2NIGHT_H),
    (B["night"][0], NIGHT_A, NIGHT_AG, NIGHT_AH), (B["night"][1], NIGHT_A, NIGHT_AG, NIGHT_AH),
    (7.0, (4.0, 78.0, 0.80, (1.0, 0.62, 0.45), (0.07, 0.09, 0.22), (0.62, 0.42, 0.36), 0.14, 0.45), ((1.0, 0.94, 0.95), -0.7),  # v8 lift
     (2600.0, 0.70, (0.62, 0.50, 0.52))),                                                  # v6: sunrise
    (8.8, DAWN2, ((1.05, 0.98, 0.92), -0.45), (2200.0, 0.80, (0.86, 0.76, 0.70))),
    (B["morning"][0], MORNING, G_ID, HAZE0),                                               # clear morning before Trost (FA3)
    (B["H"] - 1.5, MORNING, G_ID, HAZE0), (B["P3"], MORNING, G_ID, HAZE0),
    (_m0, OVERCAST, G_OVC, H_MARCH), (_m0 + 7.0, OVERCAST, G_OVC, H_MARCH),     # v7: no haze over the column
    (_m0 + 11.5, (24.0, 250.0, 1.5, (1.0, 0.94, 0.86), (0.34, 0.38, 0.46), (0.64, 0.64, 0.66), 0.25, 0.92), G_DIM, H_MARCH),
    (_m0 + 15.5, GOLD, ((1.10, 1.0, 0.84), -0.05), (3000.0, 0.50, (0.98, 0.84, 0.62))),
    (_m1, GOLD, ((1.10, 1.0, 0.84), -0.05), (3000.0, 0.50, (0.98, 0.84, 0.62))),
    (_m1 + 1.6, DUSK2, ((0.98, 0.92, 0.98), -0.5), (4000.0, 0.55, (0.40, 0.30, 0.34))),
    (_m1 + 3.0, NIGHT_A, NIGHT_AG, NIGHT_AH),     # the year passes: one night (846 -> 847); v8: g3's readable night (was -2.0 = black)
    (_m1 + 5.6, DAWN2, ((1.05, 0.98, 0.92), -0.45), (2200.0, 0.80, (0.86, 0.76, 0.70))),
    (B["FT3"] - 0.6, MORNING, G_ID, HAZE0), (B["seasons"][0], SPRING, G_ID, HAZE0),
    (B["seasons"][0] + 0.6, SUMMER, G_SUM, HAZE0),
    (B["seasons"][0] + 1.4, AUTUMN, G_AUT, (3200.0, 0.6, (0.86, 0.78, 0.66))),
    (B["grad"][0] + 0.4, DUSK2, ((0.98, 0.92, 0.98), -0.45), (4000.0, 0.55, (0.40, 0.30, 0.34))),
    (B["grad"][0] + 1.8, NIGHT, NIGHT_G, NIGHT_H), (DUR, NIGHT, NIGHT_G, NIGHT_H)]
# ground surface: (t, snow 0..1, autumn 0..1): snow is never used any more (v5); the camp's quick autumn only
SURF_KEYS = [(0.0, 0.0, 0.0), (B["seasons"][0] + 0.5, 0.0, 0.0), (B["seasons"][0] + 1.4, 0.0, 0.7), (B["grad"][0] + 0.6, 0.0, 0.0),
             (DUR, 0.0, 0.0)]
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
    vc = (lambda x: segtime.seg_t("g3", x)) if "--vclock" in a else (lambda x: x)   # --vclock: windows / stills in VIDEO s
    st = get("--stills", "")
    if st:
        ts = [vc(float(x)) for x in st.split(",") if x.strip()]
        return min(ts), max(ts)
    if "--check" in a or "--dry" in a:
        return 0.0, DUR
    return vc(float(get("--t0", 0.0))), min(vc(min(float(get("--t1", 1e9)), segtime.vdur("g3"))), DUR)

PART_SPANS = dict(night=(1.0, 12.5), rose=(9.0, DUR),     # v5: the planted clearing stays in view after 846 (no pop)
                   march=(B["crowd846"][0] - 0.1, B["march"][1]), camp=(B["FT0"], DUR))

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
def inject_surface(m, snow_rgb=(0.78, 0.80, 0.84), scale=1 / 90.0, bias=0.0):
    """base colour -> mix(autumn tint) -> snow.  QA 10/27: the snow is a COVERAGE mask, never a grey blend: patches of full
    snow colour whose edges shrink as the snow value drops (melt from the edges and ledges); `bias` staggers the melt per
    material (> 0 melts earlier).  Returns (snow value socket, autumn value socket)."""
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
    nz.inputs["Detail"].default_value = 5; nz.inputs["Roughness"].default_value = 0.6
    Ln.new(tc.outputs["Object"], nz.inputs["Vector"])
    # coverage = clamp((noise - (0.78 + bias) + 0.62 * snow) * 14): snow 0 -> nothing, 0.6 -> most ground, crisp patch edges
    sub = N.new("ShaderNodeMath"); sub.operation = "MULTIPLY_ADD"; Ln.new(vs.outputs[0], sub.inputs[0]); sub.inputs[1].default_value = 0.62
    sub.inputs[2].default_value = -(0.78 + bias)
    ad = N.new("ShaderNodeMath"); ad.operation = "ADD"; Ln.new(nz.outputs["Fac"], ad.inputs[0]); Ln.new(sub.outputs[0], ad.inputs[1])
    mk = N.new("ShaderNodeMath"); mk.operation = "MULTIPLY"; mk.use_clamp = True; mk.inputs[1].default_value = 14.0
    Ln.new(ad.outputs[0], mk.inputs[0])
    sn = N.new("ShaderNodeMix"); sn.data_type = "RGBA"; sn.blend_type = "MIX"
    Ln.new(mk.outputs[0], sn.inputs["Factor"]); Ln.new(au.outputs["Result"], sn.inputs["A"]); sn.inputs["B"].default_value = (*snow_rgb, 1)
    Ln.new(sn.outputs["Result"], bc)
    return vs.outputs[0], va.outputs[0]

SURF_BIAS = {"WD_Ground": 0.05, "Terrain": 0.02, "CP_Floor": -0.03}     # v5: the autumn tint only (snow is never set)

def build_surface():
    S["surf"] = []
    for nm, bias in SURF_BIAS.items():
        m = bpy.data.materials.get(nm)
        r = inject_surface(m, scale=1 / 45.0 if nm.startswith(("CP_", "G3")) else 1 / 80.0, bias=bias)
        if r:
            S["surf"].append(r)
    say("snow/autumn overlay on", len(S["surf"]), "materials")

def set_surface(t):
    sn, au = surf_values(t)
    for vs, va in S.get("surf", ()):
        vs.default_value = sn; va.default_value = au

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
    """v5 FARM (owner 10/27: faster + clearly visible, no winter): the conifer stand beyond Rose is felled south -> north, the
    9 contour benches show brown ploughed mud with furrow bands, then the plots (44 x 26 m, snapped) turn green / wheat
    one by one, south first (G3Crop 0..1 drives the mask; key = 0.6 * north fraction + 0.4 * plot noise)."""
    x0, x1, y0, y1 = CLEARING
    m = bpy.data.materials.new("G3Clearing"); m.use_nodes = True
    nt = m.node_tree; N, Ln = nt.nodes, nt.links
    b = N["Principled BSDF"]; b.inputs["Roughness"].default_value = 0.95
    tc = N.new("ShaderNodeTexCoord"); wv = N.new("ShaderNodeTexWave"); wv.wave_type = "BANDS"; wv.bands_direction = "X"
    wv.inputs["Scale"].default_value = 0.035; wv.inputs["Distortion"].default_value = 1.5
    Ln.new(tc.outputs["Object"], wv.inputs["Vector"])
    rp = N.new("ShaderNodeValToRGB"); e = rp.color_ramp.elements          # ploughed mud: dark furrow / lighter ridge
    e[0].position, e[0].color = 0.2, (*lin("#4a3524"), 1); e[1].position, e[1].color = 0.55, (*lin("#7d5b3a"), 1)
    Ln.new(wv.outputs["Fac"], rp.inputs["Fac"])
    sn = N.new("ShaderNodeVectorMath"); sn.operation = "SNAP"; sn.inputs[1].default_value = (44.0, 26.0, 1000.0)
    Ln.new(tc.outputs["Object"], sn.inputs[0])
    wn = N.new("ShaderNodeTexWhiteNoise"); wn.noise_dimensions = "3D"; Ln.new(sn.outputs["Vector"], wn.inputs["Vector"])
    sx = N.new("ShaderNodeSeparateXYZ"); Ln.new(tc.outputs["Object"], sx.inputs[0])
    ya, yb = F((0.0, y0, 0.0)).y, F((0.0, y1, 0.0)).y
    mr = N.new("ShaderNodeMapRange"); mr.inputs["From Min"].default_value = ya; mr.inputs["From Max"].default_value = yb
    Ln.new(sx.outputs["Y"], mr.inputs["Value"])
    k1 = N.new("ShaderNodeMath"); k1.operation = "MULTIPLY"; k1.inputs[1].default_value = 0.4; Ln.new(wn.outputs["Value"], k1.inputs[0])
    k2 = N.new("ShaderNodeMath"); k2.operation = "MULTIPLY_ADD"; k2.inputs[1].default_value = 0.6
    Ln.new(mr.outputs["Result"], k2.inputs[0]); Ln.new(k1.outputs[0], k2.inputs[2])
    cv = N.new("ShaderNodeValue"); cv.name = "G3Crop"; cv.outputs[0].default_value = 0.0
    sub = N.new("ShaderNodeMath"); sub.operation = "SUBTRACT"                  # mask = clamp((crop * 1.6 - key) * 9)
    mul0 = N.new("ShaderNodeMath"); mul0.operation = "MULTIPLY"; mul0.inputs[1].default_value = 1.6; Ln.new(cv.outputs[0], mul0.inputs[0])
    Ln.new(mul0.outputs[0], sub.inputs[0]); Ln.new(k2.outputs[0], sub.inputs[1])
    mk = N.new("ShaderNodeMath"); mk.operation = "MULTIPLY"; mk.use_clamp = True; mk.inputs[1].default_value = 9.0
    Ln.new(sub.outputs[0], mk.inputs[0])
    cr = N.new("ShaderNodeValToRGB"); cr.color_ramp.interpolation = "CONSTANT"; ce = cr.color_ramp.elements   # per-plot crop colour
    ce[0].position, ce[0].color = 0.0, (*lin("#5e8c36"), 1); ce[1].position, ce[1].color = 0.42, (*lin("#86a843"), 1)
    e3 = ce.new(0.76); e3.color = (*lin("#b8b14e"), 1)
    sep = N.new("ShaderNodeSeparateColor"); Ln.new(wn.outputs["Color"], sep.inputs[0])      # an independent per-plot channel
    Ln.new(sep.outputs[1], cr.inputs["Fac"])
    fr = N.new("ShaderNodeValToRGB"); fe = fr.color_ramp.elements        # crop rows: furrow shading on the green
    fe[0].position, fe[0].color = 0.2, (0.72, 0.72, 0.72, 1); fe[1].position, fe[1].color = 0.6, (1.0, 1.0, 1.0, 1)
    Ln.new(wv.outputs["Fac"], fr.inputs["Fac"])
    mu = N.new("ShaderNodeMix"); mu.data_type = "RGBA"; mu.blend_type = "MULTIPLY"; mu.inputs["Factor"].default_value = 1.0
    Ln.new(cr.outputs["Color"], mu.inputs["A"]); Ln.new(fr.outputs["Color"], mu.inputs["B"])
    mx = N.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.blend_type = "MIX"
    Ln.new(mk.outputs[0], mx.inputs["Factor"]); Ln.new(rp.outputs["Color"], mx.inputs["A"]); Ln.new(mu.outputs["Result"], mx.inputs["B"])
    Ln.new(mx.outputs["Result"], b.inputs["Base Color"])
    S["crop_v"] = cv.outputs[0]
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
    # refugees working the benches (felling, ploughing, planting): spread over the whole clearing
    S["workers"] = crowd(["civilian"], ((x0 + x1) / 2, (y0 + y1) / 2 - 20), 860, 380, 260, pose="kneel", seed=31)

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
    S["queue"].show((np.arange(len(S["queue"].e)) < int(40 * (1 - 0.6 * ss(*B["crowd846"], t)))) & on845)
    S["shelter_ppl"].show(on845)
    S["tents"].set(np.where((S["tent_key"] < 1.0 - 0.45 * ss(*B["crowd846"], t)) & on845, 1.0, 0.0))
    S["workers"].show(B["workers"][0] <= t <= B["workers"][1])
    mpv = B["crowd846"][0] <= t < B["CAM_IN"]
    S["mp"].show(mpv); S["mpfile"].show(mpv)
    fell = ss(*B["fell"], t) * 1.05                      # the conifers on the clearing are felled S -> N, the edge stays
    S["conif"].set(np.where(S["conif_fell"] > fell, S["conif_h"], 0.0))
    if S.get("crop_v") is not None:                     # ploughed plots planted and greening, south first
        S["crop_v"].default_value = ss(*B["crop"], t)

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
    if st.get("ground") is not None:                    # the sunken bowl surface: people stand on it
        _GROUND_OBS.append(st["ground"])
    g0 = gM(*CAMP_C)
    root = bpy.data.objects.new("G3CampRise", None); root.location = F((CAMP_C[0], CAMP_C[1], g0)); cl.objects.link(root)
    bpy.context.view_layer.update()
    for o in st["objs"]:                                # time-lapse construction (BEATS camp_rise): the camp rises out of the ground (847)
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
    # seasons (quick, no winter): 30 sparring pairs + a running file round the bowl
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
        S["grad_go"].append((Vector(e.location), Vector((hq.x, hq.y, e.location.z)), float(rr.uniform(B["grad"][1] - 2.0, B["grad"][1] - 0.8)), float(rr.uniform(38, 55))))

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
    rise = ss(*B["camp_rise"], t)
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
        k = 0.07                                        # g2 v5 already ends at night (seg_g2.light: dk = 0.07)
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
        try:
            patch_canal()
        except Exception:
            import traceback; traceback.print_exc(); say("canal patch FAILED")
    steps = []
    if "night" in parts:
        steps.append(("night", lambda: build_night(cl)))
    if "rose" in parts:
        steps += [("shelter", lambda: build_shelter(cl)), ("clearing", lambda: build_clearing(cl)), ("courtyard", lambda: build_courtyard(cl))]
    if "march" in parts:                                # v5: no sunset ridge / glow cards (owner: "strange light"), no snow anywhere
        steps += [("march", lambda: build_march(cl))]
    if "camp" in parts:
        steps += [("camp", lambda: build_camp(cl))]
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
    for fn in (update_rose, update_march, update_camp, update_gate):
        try:
            fn(t)
        except Exception:
            import traceback; traceback.print_exc(); say(f"UPDATE FAILED: {fn.__name__} t={t:.2f}")

def patch_canal():
    """Part B: world.py's set-core trim leaves the trost set's CanalWater / CanalBanks / CanalQuays with 0 vertices (seen 10/27
    in the g3 march end view: the canal cut through the terrain showed the gold SKY as two long white bars, M x 400 and the SE
    outflow).  If so, lay a plain water strip (+-22 m at CANAL_WATER_Z) along trost.CANAL_LINE_M so the cut reads as water.
    (Shared-set bug: reported to the lead; world.py is not touched here.)"""
    TR = SITE.get("TR") if SITE else None
    cw = bpy.data.objects.get("CanalWater")
    if TR is None or cw is None or cw.type != "MESH" or len(cw.data.vertices) > 0:
        return
    m = bpy.data.materials.get("CanalWater") or flat("G3CanalWaterFix", "#567a6c", 0.8)
    pts = [Vector((float(x), float(y))) for x, y in TR.CANAL_LINE_M]
    bm = bmesh.new(); Lr, Rr = [], []
    for k, p in enumerate(pts):
        a_, b_ = pts[max(k - 1, 0)], pts[min(k + 1, len(pts) - 1)]
        t_ = (b_ - a_).normalized(); n_ = Vector((-t_.y, t_.x))
        for o_, row in ((-22.0, Lr), (22.0, Rr)):            # wide: it sits under the quays / fill strips
            q = p + n_ * o_; row.append(bm.verts.new((q.x, q.y - segtime.SET_OFF_Y, float(TR.CANAL_WATER_Z))))
    for k in range(len(pts) - 1):
        bm.faces.new((Lr[k], Rr[k], Rr[k + 1], Lr[k + 1]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces:
        if f.normal.z < 0:
            f.normal_flip()
    ob = L.obj_from_bm("G3CanalPatch", bm, [m], coll("G3"))
    ob.visible_shadow = False
    say("canal patch: CanalWater had 0 vertices; G3CanalPatch laid along", len(pts), "points")

def matte_water():
    """v5: the low gold sun turned the canal / river into long WHITE glare bars (QA still 30.5 s: the Trost canal at M x 400
    and its SE outflow): rough, low-specular water in part B (part A keeps g2's look for the seam)."""
    if PART == "A":
        return
    hit = []
    for m in bpy.data.materials:
        if "water" not in m.name.lower() or not m.use_nodes:
            continue
        for n in m.node_tree.nodes:
            if n.type == "BSDF_PRINCIPLED":
                n.inputs["Roughness"].default_value = 0.8
                for k in ("Specular IOR Level", "Specular"):
                    if k in n.inputs:
                        n.inputs[k].default_value = 0.0
                        break
                for k in ("Coat Weight", "Transmission Weight"):
                    if k in n.inputs:
                        n.inputs[k].default_value = 0.0
                hit.append(m.name)
    say("matte water:", sorted(set(hit)))

def finish():
    """After toon.apply(): matte water (part B); no toon rim on the (unused since v5) sunset ridge ground."""
    matte_water()
    m = bpy.data.materials.get("G3RidgeGround")
    if m is not None and m.use_nodes:
        for n in m.node_tree.nodes:
            if n.type == "MAP_RANGE" and abs(n.inputs["From Min"].default_value - 0.72) < 1e-4 and abs(n.inputs["From Max"].default_value - 0.8) < 1e-4:
                n.inputs["To Max"].default_value = 0.0          # toon.py's rim map range only

def check():
    cam_report(quiet=False)
    say("parts", sorted(S.get("parts", ())), "| light 0:", {k: (np.round(v, 3) if isinstance(v, np.ndarray) else v) for k, v in light_values(0.0).items() if k in ("el", "en", "amb", "gex")},
        "| light DUR = g4 t0:", light_values(DUR)["en"] == _G4L[3] and light_values(DUR)["gex"] == _G4G[2])
    L0 = S.get("L0")
    if L0:
        say("lighting-sky s0 (trost expects 0.25 for the g4 night):", [round(s, 3) for _, s in L0["bgs"]], "exposure at build", L0["exp0"])
    MR = S.get("MR")
    if MR is not None:                                   # the restored march camera = march846.cam_at (set frame + 870 y)
        for tau in (0.0, 4.0, 9.6, 15.0, MARCH_T_END):
            l0, k0, n0 = MR.cam_at(tau); l1, k1, n1 = MARCH.eval(B["march"][0] + tau)
            say(f"march846.cam_at({tau}) set {tuple(round(x, 1) for x in l0)} | g3 M {tuple(round(float(x), 1) for x in l1)} (M = set + 870 y)")

if __name__ == "__main__":
    cam_report()
    print("video clock: g3 %.2f s (TMAP %d knots)" % (segtime.vdur("g3"), len(segtime.knots("g3"))))
    vcheck()
