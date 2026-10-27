"""g5 TROST BREACH, EVACUATION, MIKASA, ATTACK TITAN (SCENE_BIBLE_v2 g5, TIGHT 70.0 s, frame M).
Driven by aot/render_seg.py (SEG=g5 bash render_seg.sh).  Every frame is a pure function of the local time t (0..DUR).

Contents (bible g5 choreography, tight column; every time lives in BEATS / AT_KEYS / LIGHT_KEYS below):
  0-0.27 yellow-gold bolt with the yellow/black flicker - 0-2.5 the Colossal's skull rises (chin at the wall top, face
  outside the parapet, steam + embers) - 3.2-3.9 shoulders dip (right leg winds up behind the wall) - KICK 4.0: gatehouse
  bursts (set_breach), sepia shock ring, 60-80 m dust column, dust sheet along the wall top, debris arcs (25 chunks, 80
  medium, 150 planks), 4 soldiers flung, cadets drop down the inner face, slabs rock 2-5 m - 5.5 right-fist grip (cracks on
  the inner face) - 6.5 first titan through - pour P1-P35 (<= 3 abreast, ~2.1/s) on lanes L1-L5, 2 abnormals up AV,
  trench / crater stumbles, slabs knocked into their end state - 7-9 left-forearm sweep WEST over X 0..-35 (cannon, hut,
  flag, crates flung west), Eren runs up the forearm - 9.0 steam explosion, the Colossal is gone - vanguard engages (nape
  kills 12.5 / 16.0 / 20.0, a squad member grabbed 18.0), wall-top grapeshot from 10.5, smoke columns from 14, clouds roll
  in 12-26 - 26 Abnormal AB on EVS with its dust cloud, Mikasa + a Garrison soldier behind it - the jam at the inner gate:
  ~5,500 people, sack cart wedged in the arch, merchant + 3 guards in the gap, pushers - KILL 33.8, skid to the corpse
  (-96, 794), crowd recoils - 36.5 hop over the crowd, lane, merchant, bodyguard shoved 38.5 - 39.4-41.6 the cart is backed
  out and swung east to its end state (never drives through) - the crowd drains through the arch from 40.9 - 49-53.5 the
  104th stream with Mikasa leading, TR1 killed 51.0, gas out 52.5, FALL 53.3 into alley MA - CAP and LH climb in - 54.5 BT
  torn open in SS (small gold bolt + 25 m steam burst), the Attack Titan sprints along SS - PUNCH 57.4, roar 58.3 (green
  eyes), 3 stomps, LH stamped - Armin + Connie lift Mikasa to roof R - fight #2 in Q2 with CC: boxer stance 64.3, blows,
  TOWER SLAM 65.5 (top of tower T bursts), NAPE STAMP 66.8 - 70.0 AT walking out of Q2 up the street at (-231, 531),
  heading 349, 6 m/s = hand-off to g6 (the bible's (-222, 531) is inside a house of the set; 9 m W of it).
Light: clear late morning -> cloud roll-in 12-26 -> dark overcast at E -> breaking overcast + 3 sun shafts from 50.
Reused: colossal_asset (plug-in, imported here), attack_titan (asset + blended poses), trost_action.Titans (pure titans,
subclassed), odm.Squads (ODM people, wires, gas), swarm845 Geo / person_geo / _deform (the 5,500 crowd, minimal style,
dusty colourful palette), smokecards (steam / dust / smoke / fire / glow cards), trost.py set hooks (set_breach,
set_glow, set_wagon, set_cart, TrostSlab_*, TrostTowerT_Top), toon.
Placeholders built here: G5_* objects (debris, streak, cracks, X-stakes, pools, ribs, shafts, cloud shadow discs).
"""
import math, os, random, sys, time, types
import numpy as np

try:
    import bpy, bmesh
    from mathutils import Vector, Matrix, Euler, Quaternion
except ImportError:                       # pure-python use (camera checks outside Blender)
    bpy = None

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import camchan
import camkeys
import segtime

DUR = segtime.DUR["g5"]                    # 70.0 (tight)

# ====================================================================== BEATS (tight, local seconds) - ONE re-time table
BEATS = dict(
    bolt=(0.0, 0.27), rise=(0.5, 2.6),   # v4: the skull rises out of the strike smoke (lightning_spec.md)
    windup=(3.2, 3.85), dip=(3.3, 3.9), kick=4.0, recover=(4.0, 5.0), flung=(4.15, 5.8),
    drop_wires=(4.6, 6.2), grip=(4.9, 5.5), first_titan=6.5, pour=(6.5, 22.8), hand_up=(6.3, 7.0), sweep=(7.0, 9.0),
    eren_arm=(7.6, 9.0), steam_burst=9.0, col_fade=(9.0, 10.2), slabs_rock=(4.0, 5.2), cannons=10.5,
    vkills=(12.5, 16.0, 20.0), overrun=18.0, smoke=14.0, clouds=(12.0, 26.0), relocate=(19.0, 25.0),
    ab_run=(24.4, 33.8), ab_in=26.0, kill=33.8, skid=(33.8, 34.6), on_corpse=(34.6, 36.5), hop=(36.5, 37.5),
    lane=(37.5, 38.5), shove=38.5, cart=(39.4, 41.6), drain=40.6, back_corpse=(41.9, 42.6), mikasa_sw=44.0,
    stream=(49.0, 53.5), tr1_kill=51.0, sputter=52.5, fall=53.3, cap_in=(52.8, 56.2), lh_in=(53.8, 55.6),
    bt_torn=54.5, sprint=(54.85, 57.15), charge=(56.5, 57.3), punch=57.4, roar=(58.3, 59.0), stomps=(59.3, 59.58, 59.86),
    lh_stamp=59.86, rescue=(59.6, 62.1), to_q2=(59.95, 62.9), cc_in=(58.0, 63.6), boxer=64.3, blows=(64.7, 65.0),
    slam=65.5, cc_slide=(65.6, 66.3), nape_stamp=66.8, walk_out=(67.4, 70.0), shafts=(50.0, 70.0))

# ====================================================================== anchors (frame M; bible section C + g5 spec)
GATE = (0.0, 0.0)
COL_DX, COL_BACK = 0.0, 14.0                       # Colossal body axis X 0, 21 m south of the wall line (feet Y -18..-28)
FIST_R = (26.0, 2.6, 51.4)                        # right-fist grip on the coping (fingers over the inner edge)
SWEEP_X = (-2.0, -35.0)                            # left forearm sweep, west only (true-scale reach)
PIT = (0.0, 36.0); CRW = (-32.0, 20.0); CRE = (34.0, 30.0)
AV = [(0.0, 74.0), (-15.0, 300.0), (-60.0, 470.0), (-128.0, 735.0), (-153.0, 803.0)]
ARCH = (-140.0, 849.5)                            # arch mouth (central block face Y 851)
E_BOX = (-178.0, -102.0, 800.0, 853.0)
EVS = [(0.0, 690.0), (-102.0, 800.0)]
AB_IN = (-18.0, 709.0); AB_KILL = (-85.0, 782.0); AB_CORPSE = (-96.0, 794.0)
MIK_LAND = (-138.0, 838.0); MIK_FACE = (-140.0, 843.6); MERCHANT = (-140.0, 846.6)
CART_START = ((-140.0, 851.5), 0.0); CART_END = ((-122.0, 842.0), 320.0)
MA_X = -262.0; MA_LAND = (-262.0, 400.0); MA_HEAP = (443.0, 458.0)
BT_POS = (-205.0, 423.0); TR1_POS = (-256.0, 345.0)
TOWER = (-218.0, 522.0); ROOF_R = (-258.0, 505.0, 25.0)
AT_END = (-231.0, 531.0); AT_END_HEADING = 349.0; AT_END_V = 6.0   # bible (-222, 531) lies inside house TV25: moved 9 m W onto
                                                                   # the N-S street X -236..-228 that leaves Q2 for the HQ plaza
HQ = (-250.0, 640.0)
SMOKE_SITES = [(-62, 112), (48, 140), (-108, 186), (118, 228), (-28, 262), (-188, 142), (168, 330), (-138, 362), (64, 420),
               (-232, 262), (222, 150), (-84, 560), (-300, 420)]
WIND = np.array([2.6, 1.2, 0.0])                   # drift (m/s, set coords = M orientation)

# ====================================================================== camera = bible g5 keys (camkeys.G5, tight), A2 seams
CAM_KEYS = list(camkeys.G5)
_ck = camkeys.cam("g5")
CAM = camchan.CamPath(CAM_KEYS, v_in=_ck["v_in"], v_out=_ck["v_out"])
CAM_LIMITS = dict(speed=44.0, yaw=30.0, hmin=120.0, hmax=210.0)

# ====================================================================== small pure helpers
def ss(a, b, x):
    u = min(1.0, max(0.0, (x - a) / (b - a))) if b != a else float(x >= b)
    return u * u * (3 - 2 * u)

def lerp(a, b, u):
    return a + (b - a) * u

def bump(t, a, b, c, d):
    return ss(a, b, t) * (1 - ss(c, d, t))

def heading_yaw(compass_deg):
    """compass bearing (deg, cw from N) -> yaw (rad, ccw from +Y; attack_titan / odm / trost_action convention)."""
    return -math.radians(compass_deg)

def yaw_to(dx, dy):
    return math.atan2(-dx, dy)

def poly_len(P):
    P = np.asarray(P, float)
    return np.concatenate([[0.0], np.cumsum(np.hypot(*np.diff(P, axis=0).T))])

def poly_at(P, S, s):
    P = np.asarray(P, float); s = min(max(s, 0.0), S[-1])
    i = int(min(len(S) - 2, max(0, np.searchsorted(S, s, side="right") - 1)))
    u = (s - S[i]) / max(S[i + 1] - S[i], 1e-9)
    return P[i] + (P[i + 1] - P[i]) * u

def heap_z(x, y):
    """Extra height of MA's rubble heap (Y 443-458, 6 m) and the broken end wall (Y 458-461, <= 9 m) for titan feet."""
    if abs(x - MA_X) > 6.0:
        return 0.0
    if 443.0 <= y < 458.0:
        return 4.5 * ss(443.0, 450.0, y)
    if 458.0 <= y < 462.0:
        return 4.5 * (1 - ss(458.0, 462.0, y))
    return 0.0

# ====================================================================== the Colossal (pure state)
def col_state(t):
    u = min(1.0, max(0.0, t / 2.5)); rise = 1 - (1 - u) ** 3
    if t < BEATS["windup"][0]:
        k = 0.0
    elif t < BEATS["windup"][1]:
        k = -ss(*BEATS["windup"], t)
    elif t < BEATS["kick"]:
        k = -1.0 + 2.0 * ss(BEATS["windup"][1], BEATS["kick"], t)
    else:
        k = 1.0 - ss(*BEATS["recover"], t)
    dip = 1.5 * bump(t, BEATS["dip"][0], BEATS["dip"][1] - 0.2, BEATS["kick"], BEATS["kick"] + 0.6)
    return dict(show=t < BEATS["col_fade"][1] + 0.05, rise=rise, k=k, dip=dip, hand_r=ss(*BEATS["grip"], t),
                hand_l_up=ss(*BEATS["hand_up"], t), sweep=ss(*BEATS["sweep"], t), fade=ss(*BEATS["col_fade"], t),
                lean=2.0 + 5.0 * ss(6.3, 7.2, t), steam=ss(0.05, 1.6, t))

def sweep_hand(t):
    """Left-hand IK target (M) during the sweep: up over the parapet at X -2, then west along the wall top."""
    c = col_state(t)
    x = lerp(SWEEP_X[0], SWEEP_X[1], c["sweep"])
    yc = 480.0 - math.sqrt(480.0 ** 2 - x * x)                 # bulge wall centreline at this X
    z = 51.0 + 2.0 * math.sin(math.pi * c["sweep"])
    return np.array([x - 1.5, yc + 0.8, z])

# ====================================================================== the Attack Titan (pure keys -> state)
# (t, x, y, compass heading or None = along the motion, mode)
AT_KEYS = [
    (54.50, -205.0, 423.0, 270, "emerge"),
    (54.85, -207.0, 423.0, 270, "run"),
    (57.15, -252.0, 423.0, 268, "run"),
    (57.45, -258.5, 420.5, 215, "punch"),      # the blow travels SOUTH and slightly west (anime orientation audit)
    (57.90, -260.5, 414.0, 205, "follow"),
    (58.30, -261.0, 411.0, 200, "stand"),
    (59.05, -261.0, 410.5, 200, "roar"),
    (59.95, -261.5, 407.0, 205, "stomp"),      # stomps CAP (face down against the W wall, Y ~400) and LH beside it
    (61.30, -262.0, 438.0, 0, "run"),
    (62.90, -247.0, 496.0, 25, "smash"),       # owner 10/27: no leap - he smashes through the end wall and the houses into Q2
    (64.00, -244.5, 498.0, 50, "stand"),
    (64.30, -244.0, 498.5, 52, "boxer"),
    (65.30, -238.0, 503.0, 52, "boxer"),
    (65.60, -229.5, 510.5, 48, "slam"),
    (66.55, -235.0, 506.0, 58, "stand"),
    (66.95, -233.5, 507.0, 58, "stamp"),
    (67.40, -232.5, 509.0, 0, "stand"),
    (70.00, AT_END[0], AT_END[1], AT_END_HEADING, "walkout"),
]
AT_STEP = {"run": 10.0, "walk": 7.0, "walkout": 7.0}         # metres per step (one foot)

def _walkout_pos(u):
    """Cubic Hermite (67.4 -> 70.0) ending at AT_END with heading 349 deg at 6 m/s (the g6 hand-off)."""
    T = BEATS["walk_out"][1] - BEATS["walk_out"][0]
    p0 = np.array(AT_KEYS[-2][1:3], float); p1 = np.array(AT_END, float)
    h0 = math.radians(0.0); h1 = math.radians(AT_END_HEADING)
    m0 = np.array([math.sin(h0), math.cos(h0)]) * 4.5 * T; m1 = np.array([math.sin(h1), math.cos(h1)]) * AT_END_V * T
    h00, h10, h01, h11 = 2 * u ** 3 - 3 * u ** 2 + 1, u ** 3 - 2 * u ** 2 + u, -2 * u ** 3 + 3 * u ** 2, u ** 3 - u ** 2
    return p0 * h00 + m0 * h10 + p1 * h01 + m1 * h11

def _at_cum():
    c = [0.0]
    for a, b in zip(AT_KEYS, AT_KEYS[1:]):
        c.append(c[-1] + math.hypot(b[1] - a[1], b[2] - a[2]))
    return c
_AT_CUM = _at_cum()

def at_state(t):
    ks = AT_KEYS
    if t < ks[0][0]:
        return dict(vis=False, pos=np.array(ks[0][1:3], float), yaw=heading_yaw(ks[0][3]), mode="hidden", u=0.0, walked=0.0, eyes=0.0, z=0.0)
    if t >= ks[-1][0]:
        p = np.array(AT_END, float) + np.array([math.sin(math.radians(AT_END_HEADING)), math.cos(math.radians(AT_END_HEADING))]) * AT_END_V * (t - ks[-1][0])
        return dict(vis=True, pos=p, yaw=heading_yaw(AT_END_HEADING), mode="walkout", u=1.0, walked=_AT_CUM[-1] + AT_END_V * (t - ks[-1][0]), eyes=0.0, z=0.0)
    for i, (a, b) in enumerate(zip(ks, ks[1:])):
        if a[0] <= t < b[0]:
            break
    mode = b[4]
    lin = mode in ("run", "walk", "walkout", "leap", "smash")
    u = (t - a[0]) / (b[0] - a[0])
    ue = u if lin else u * u * (3 - 2 * u)
    if mode == "walkout":
        p = _walkout_pos(u)
        p2 = _walkout_pos(min(1.0, u + 0.01)); d = p2 - p
        if u > 0.99:
            d = np.array([math.sin(math.radians(AT_END_HEADING)), math.cos(math.radians(AT_END_HEADING))])
        yaw = yaw_to(d[0], d[1])
        walked = _AT_CUM[i] + float(np.linalg.norm(p - np.array(a[1:3])))
    else:
        p = np.array([lerp(a[1], b[1], ue), lerp(a[2], b[2], ue)])
        ya, yb = heading_yaw(a[3]), heading_yaw(b[3])
        dy = (yb - ya + math.pi) % math.tau - math.pi
        yaw = ya + dy * ss(0.0, 0.6 if lin else 1.0, u)
        walked = _AT_CUM[i] + math.hypot(b[1] - a[1], b[2] - a[2]) * ue
    eyes = 7.0 if mode in ("roar", "stomp", "stamp") else 0.0
    return dict(vis=True, pos=p, yaw=yaw, mode=mode, u=u, t0=a[0], t1=b[0], walked=walked, eyes=eyes,
                z=heap_z(p[0], p[1]))

def at_vel(t, dt=0.05):
    a = at_state(t - dt)["pos"]; b = at_state(t + dt)["pos"]
    return (b - a) / (2 * dt)

# ====================================================================== the crowd drain (pure)
V_DRAIN, C_WAVE = 10.0, 120.0          # ~6x arch flow; eased in (1 s) and out (slows from 3 s on)
_DT_TAB = np.arange(0.0, 40.0, 0.02)
_V_TAB = V_DRAIN * np.array([ss(0.0, 1.0, x) * (1.0 - 0.55 * ss(3.0, 8.0, x)) for x in _DT_TAB])
_R_TAB = np.concatenate([[0.0], np.cumsum(0.5 * (_V_TAB[1:] + _V_TAB[:-1]) * 0.02)])
def drain_R(tau):
    """Radius of the 'consumed' disk at the arch mouth tau s after the drain front reaches a person (eased in / out)."""
    return np.interp(np.maximum(tau, 0.0), _DT_TAB, _R_TAB)

def drain_speed(tau):
    return np.interp(np.maximum(tau, 0.0), _DT_TAB, _V_TAB) * (np.asarray(tau) > 0)

STEAM_WARM = (1.0, 0.88, 0.74)          # counters the blue sky fill on steam cards (owner QA: no blue steam)
WARM_SKINS = ["#f0a07a", "#e8875f", "#f4b08a", "#dd7c58", "#ee9a74", "#e48f68", "#f2a682"]   # warm, reads on beige paving

# ====================================================================== everything below needs Blender
STATE = {}
PLACEHOLDERS = []

def say(*a):
    print("[seg g5]", *a, flush=True)

def _site():
    return STATE["site"]

def S3(x, y=None, z=0.0):
    """M -> set coords (np array)."""
    if y is None:
        p = x; x, y, z = float(p[0]), float(p[1]), float(p[2]) if len(p) > 2 else 0.0
    return np.array([float(x), float(y) - segtime.SET_OFF_Y, float(z)])

def SV(x, y=None, z=0.0):
    return Vector(S3(x, y, z))

def G(x, y):
    return _site()["ground_M"](float(x), float(y))

def _coll(name):
    c = bpy.data.collections.get(name)
    return c if c else STATE["L"].new_coll(name)

def hexrgb(h):
    h = h.lstrip("#"); c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c)

def emit_mat(name, rgb, strength):
    import flares as FX
    return FX.emit_mat(name, rgb, strength)

def _hide(ob, h):
    if ob is not None and (ob.hide_render != h or ob.hide_viewport != h):
        ob.hide_render = ob.hide_viewport = h

_RC = {}
def top_z(x, y, default=None, zmax=400.0):
    """Highest surface under M (x, y) (roof, wall top or ground) by a scene ray cast; cached."""
    key = (round(x, 1), round(y, 1))
    if key in _RC:
        return _RC[key]
    dg = bpy.context.evaluated_depsgraph_get()
    hit, loc, nrm, idx, ob, mw = bpy.context.scene.ray_cast(dg, SV(x, y, zmax), Vector((0, 0, -1)))
    z = float(loc.z) if hit else (default if default is not None else G(x, y))
    if hit and ob is not None and (ob.name.startswith("Haze") or ob.name.startswith("Sky")):
        z = default if default is not None else G(x, y)
    _RC[key] = z
    return z

def perch(x, y, search=5.0):
    """A standing spot on top of whatever is at M (x, y): the highest of a few probes (roof ridges read best)."""
    best = None
    for dx, dy in ((0, 0), (search, 0), (-search, 0), (0, search), (0, -search)):
        z = top_z(x + dx, y + dy)
        if best is None or z > best[2] + 0.5:
            best = (x + dx, y + dy, z)
    return np.array([best[0], best[1], best[2] + 0.05])

def roof_set(x, y, search=5.0):
    q = perch(x, y, search); return S3(q[0], q[1], q[2])

def gnd_set(x, y, dz=0.05):
    return S3(x, y, G(x, y) + dz)

# ====================================================================== Colossal (colossal_asset, imported once here)
def build_colossal():
    env = dict(COL_H="60", COL_HEAD="1.0", COL_BACK=str(COL_BACK), COL_DX=str(COL_DX), COL_GRIP_DX=str(FIST_R[0]),
               COL_RISE_DROP="16", COL_SHOW="1", COL_LEAN="2")
    for k, v in env.items():
        os.environ.setdefault(k, v)
    CA = sys.modules.get("colossal_asset")
    if CA is None or not getattr(CA, "STATE", None):
        import colossal_asset as CA
        if not CA.STATE:
            CA.build(None, 850, None)
    STATE["CA"] = CA
    arm = CA.STATE["arm"]
    STATE["col_coll"] = arm.users_collection[0]
    STATE["col_objs"] = list(STATE["col_coll"].all_objects)
    if "cards" in CA.STATE:
        try:
            pool = CA.STATE["cards"][0].pools["steam"]
            pool.A[:, 13:16] = pool.A[:, 13:16] * np.array(STEAM_WARM)
        except Exception as ex:
            say("colossal steam tint failed:", ex)
    hb = arm.pose.bones["mixamorig_Head_06"]
    bpy.context.view_layer.update()
    say("colossal head (set)", tuple(round(v, 1) for v in (arm.matrix_world @ hb.head)), "root", tuple(round(v, 1) for v in CA.STATE["root"].location))

def update_colossal(t):
    c = col_state(t)
    on = c["show"]
    coll = STATE["col_coll"]
    if coll.hide_render == on:
        coll.hide_render = not on
    if not on:
        return
    CA = STATE["CA"]
    os.environ["COL_LEAN"] = "%.2f" % c["lean"]
    CA.set_pose(c["k"], c["rise"], c["fade"], hand_l=0.0, hand_r=c["hand_r"], steam=c["steam"] * (1 - 0.7 * c["fade"]))
    root = CA.STATE["root"]
    root.location.z += 2.0 - c["dip"]                         # crown ~60, chin at the wall top, face ~6 m outside the parapet
    # left hand: hanging behind the wall until 6.3, up over the parapet, then the sweep west along the wall top
    hl = CA.STATE.get("handL")
    if hl and c["hand_l_up"] > 0:
        a0, cc, g = hl["pts"]
        tgt = Vector(S3(sweep_hand(t)))
        h = c["hand_l_up"] * (1 - c["fade"])
        hl["tgt"].location = (1 - h) ** 2 * a0 + 2 * h * (1 - h) * cc + h * h * tgt
        for segs in hl["fingers"]:
            for pb, a in zip(segs, (0.1, 0.5, 0.4)):
                pb.rotation_euler = (a, 0, 0)
    hr = CA.STATE.get("handR")
    if hr and c["hand_r"] > 0:
        a0, cc, g = hr["pts"]
        tgt = Vector(S3(FIST_R))
        h = c["hand_r"] * (1 - c["fade"])
        hr["tgt"].location = (1 - h) ** 2 * a0 + 2 * h * (1 - h) * cc + h * h * tgt

# ====================================================================== Attack Titan (asset) with blended poses
def _V(r, f, z):
    import attack_titan as AT
    return AT.V(r, f, z)

def blend(a, b, u):
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
    P = {k: dict(v) for k, v in AT.POSES.items() if k in ("stand", "roar", "punch", "crouch")}
    st = P["stand"]
    P["run"] = dict(st, hips=8.3, bend=_bends(14, 10, 6, 2, -6),
                    hands={"R": (V(1.0, 0.6, -3.6), V(1, -0.6, 0), "sh"), "L": (V(-1.0, 0.6, -3.6), V(-1, -0.6, 0), "sh")}, fist=0.9, jaw=10)
    P["stomp_up"] = dict(st, hips=8.6, bend=_bends(8, 8, 6, 10, 18),
                         feet={"R": (V(1.5, 3.4, 3.6), -10), "L": (V(-1.4, -0.6, 0), 8)}, knee=V(0, 1, 0.3),
                         hands={"R": (V(1.8, -1.2, -3.6), V(1, -0.6, 0), "sh"), "L": (V(-1.8, -1.2, -3.6), V(-1, -0.6, 0), "sh")}, fist=1.0, jaw=26)
    P["stomp_down"] = dict(P["stomp_up"], hips=7.6, bend=_bends(16, 12, 8, 12, 20),
                           feet={"R": (V(1.5, 4.0, 0.2), -10), "L": (V(-1.4, -0.8, 0), 8)}, jaw=30)
    P["boxer"] = dict(st, hips=8.1, bend=_bends(6, 6, 4, 0, 0, (0, -8, -8, 0, 0)),
                      feet={"R": (V(1.8, -1.6, 0), -15), "L": (V(-1.6, 1.8, 0), 12)}, knee=V(0, 1, 0.25),
                      hands={"R": (V(-0.3, 2.0, 0.6), V(1, -0.2, -1), "sh"), "L": (V(0.4, 2.6, 1.0), V(-1, -0.2, -1), "sh")}, fist=1.0, jaw=8)
    P["jab"] = dict(P["boxer"], bend=_bends(10, 8, 6, 0, 0, (0, 12, 10, 0, 0)),
                    hands={"R": (V(-0.4, 5.0, 0.6), V(1, 0, -1), "sh"), "L": (V(0.5, 1.8, 0.4), V(-1, -0.2, -1), "sh")})
    P["slam"] = dict(st, hips=7.6, bend=_bends(22, 16, 8, -2, -6),
                     feet={"R": (V(1.6, -3.0, 0), -10), "L": (V(-1.6, 2.6, 0), 10)}, knee=V(0, 1, 0),
                     hands={"R": (V(-0.6, 5.0, 0.0), V(1, 0, -1), "sh"), "L": (V(0.6, 5.0, 0.0), V(-1, 0, -1), "sh")}, fist=0.4, jaw=24)
    P["emerge"] = dict(P["crouch"], jaw=20)
    return P

def _walk_feet(spec, phase, amp, lift=0.9):
    import attack_titan as AT
    out = dict(spec)
    fr = -amp * math.cos(phase); fl = amp * math.cos(phase)
    lr = lift * max(0.0, math.sin(phase)); ll = lift * max(0.0, -math.sin(phase))
    fe = spec["feet"]
    out["feet"] = {"R": (fe["R"][0] + AT.V(0, fr, lr), fe["R"][1]), "L": (fe["L"][0] + AT.V(0, fl, ll), fe["L"][1])}
    hs = dict(spec["hands"])
    if hs["R"][2] == "sh" and hs["L"][2] == "sh":       # arms counter-swing
        hs = {"R": (hs["R"][0] + AT.V(0, 0.5 * amp * math.cos(phase), 0), hs["R"][1], "sh"),
              "L": (hs["L"][0] + AT.V(0, -0.5 * amp * math.cos(phase), 0), hs["L"][1], "sh")}
        out["hands"] = hs
    return out

def build_attack(coll):
    import attack_titan as AT
    t0 = time.time()
    T = AT.place_attack(0.0, -5000.0, 0.0, "stand", name="G5Attack", eyes=0.0)
    STATE["AT"] = T
    T.holder.matrix_world = Matrix.Identity(4); bpy.context.view_layer.update()
    T.pose("stand", ground=False)
    STATE["SH"] = {"L": T.wpos("upper_arm.L_32").copy(), "R": T.wpos("upper_arm.R_55").copy()}
    STATE["P"] = make_poses()
    STATE["at_objs"] = [o for o in T.coll.all_objects]
    for o in STATE["at_objs"]:
        _hide(o, True)
    say(f"Attack Titan imported {time.time() - t0:.1f}s")

def _pose_attack(t):
    import attack_titan as AT
    T = STATE["AT"]; P = STATE["P"]
    st = at_state(t)
    for o in STATE["at_objs"]:
        _hide(o, not st["vis"])
    if not st["vis"]:
        return st
    mode, u = st["mode"], st["u"]
    if mode == "emerge":
        spec = blend(P["emerge"], P["stand"], ss(0.2, 1.0, u))
    elif mode == "run":
        spec = _walk_feet(P["run"], math.pi * st["walked"] / AT_STEP["run"], 3.2, lift=1.4)
    elif mode in ("walk", "walkout"):
        spec = _walk_feet(P["stand"], math.pi * st["walked"] / AT_STEP["walk"], 2.4)
    elif mode == "punch":
        spec = blend(P["run"], P["punch"], ss(0.0, 0.7, u))
    elif mode == "leap":
        spec = blend(P["crouch"], P["run"], bump(u, 0.0, 0.2, 0.75, 1.0))
    elif mode == "smash":                                            # shoulder-first charge: run cycle, arms half up front
        spec = blend(_walk_feet(P["run"], math.pi * st["walked"] / AT_STEP["run"], 3.2, lift=1.4), P["punch"], 0.35)
    elif mode == "follow":
        spec = blend(P["punch"], P["stand"], ss(0.3, 1.0, u))
    elif mode == "stand":
        spec = P["stand"]
    elif mode == "roar":
        spec = blend(P["stand"], P["roar"], bump(t, st["t0"], st["t0"] + 0.25, st["t1"] - 0.2, st["t1"]))
    elif mode == "stomp":
        w = 0.0
        for ts in BEATS["stomps"]:
            w = max(w, bump(t, ts - 0.2, ts - 0.08, ts + 0.02, ts + 0.12))
        dn = max(bump(t, ts - 0.06, ts, ts + 0.06, ts + 0.14) for ts in BEATS["stomps"])
        spec = blend(blend(P["stand"], P["stomp_up"], max(w, ss(st["t0"], st["t0"] + 0.15, t) * 0.6)), P["stomp_down"], dn)
    elif mode == "stamp":
        ts = BEATS["lh_stamp"] if t < 62 else BEATS["nape_stamp"]
        up = bump(t, ts - 0.3, ts - 0.1, ts + 0.05, ts + 0.25)
        dn = bump(t, ts - 0.08, ts, ts + 0.08, ts + 0.2)
        spec = blend(blend(P["stand"], P["stomp_up"], up), P["stomp_down"], dn)
    elif mode == "boxer":
        spec = blend(P["stand"] if t < BEATS["boxer"] else P["boxer"], P["boxer"], ss(st["t0"], st["t0"] + 0.25, t))
        for tb in BEATS["blows"]:
            spec = blend(spec, P["jab"], bump(t, tb - 0.1, tb, tb + 0.05, tb + 0.18))
    elif mode == "slam":
        spec = blend(P["boxer"], P["slam"], ss(0.0, 0.6, u))
    else:
        spec = P["stand"]
    AT.POSES["_g5"] = spec
    T.pose("_g5", ground=False)
    p = st["pos"]
    z = G(p[0], p[1]) + st["z"]
    if mode in ("run", "smash"):
        z += 0.35 * abs(math.sin(math.pi * st["walked"] / AT_STEP["run"]))
    if mode == "punch":
        z += 2.2 * math.sin(math.pi * min(1.0, u * 1.2))            # the leap
    if mode == "leap":
        z += 27.0 * math.sin(math.pi * u)
    T.holder.location = Vector(S3(p[0], p[1], z))
    T.holder.rotation_euler = (0.0, 0.0, st["yaw"] + math.pi)
    T.eyes(st["eyes"])
    return st

# ====================================================================== pure titans (trost_action.Titans + g5 events)
class _TSite:
    """Ground for trost_action.Titans (set coords) with MA's rubble heap; nav via a TA.Site."""
    def __init__(self, nav_site):
        self.nav_site = nav_site
    def g(self, p):
        x, y = float(p[0]), float(p[1]) + segtime.SET_OFF_Y
        return G(x, y) + heap_z(x, y)
    def nav(self):
        return self.nav_site.nav()

def make_titans_class():
    import trost_action as TA
    import swarm845 as SW
    import odm
    import flares as FX
    L = STATE["L"]

    class Titans5(TA.Titans):
        """trost_action.Titans plus g5 events: fall (face down / hurled, independent of death), keep (corpse stays and
        shrinks), stoop (reach down), climb (hands on knees), recoil, sit, kneel, lying, slack, trip, lean (HQ walls);
        build() adds long hair / crew cut / bigger bellies."""
        def poses(self, t):
            if self._cache_t == t:
                return self._cache
            R = super().poses(t)
            Ar, Ae, lean, vis, yaw, pos, pitch = R
            for j, sp in enumerate(self.specs):
                x = sp.get("g5")
                if not x:
                    continue
                a, b = self.show[j]
                if not (a <= t < b):
                    continue
                d = self.ev[j]["death"]
                dead = d is not None and t >= d[0]
                if x.get("keep") and dead:
                    vis[j] = 1.0 - (1.0 - x.get("shrink", 0.85)) * ss(d[0] + 1.5, d[0] + x.get("shrink_t", 20.0), t)
                if x.get("fall") is not None:
                    tf, dur, dirn = x["fall"]
                    if t >= tf:
                        u = ss(tf, tf + dur, t)
                        pf = -dirn * (math.pi / 2 - 0.1) * u
                        if abs(pf) > abs(pitch[j]) or not dead:
                            pitch[j] = pf
                        Ar[j, 3] = Ar[j, 4] = 1.6 * u + 0.2; Ar[j, 1] = 0.3 * u
                        pos[j, 2] -= 0.02 * self.H[j] * u
                if x.get("trip") is not None and t >= x["trip"]:
                    u = ss(x["trip"], x["trip"] + 0.8, t)
                    pitch[j] = -(math.pi / 2 - 0.15) * u
                    Ar[j, 3] = Ar[j, 4] = 1.2 * u + 0.2 * math.sin(t * 2 + j) * u
                if x.get("lying"):
                    pitch[j] = -(math.pi / 2 - 0.1); pos[j, 2] -= x.get("drop", 0.0)
                    Ar[j, 3] = 0.6; Ar[j, 4] = 1.6 + 0.1 * math.sin(t * 0.8)
                if x.get("sit") is not None and t >= x["sit"] and not dead:
                    u = ss(x["sit"], x["sit"] + 1.0, t)
                    pos[j, 2] -= 0.36 * self.H[j] * u; lean[j] = -0.15 * u; Ar[j, 3] = Ar[j, 4] = 0.5 * u
                if x.get("kneel") is not None and t >= x["kneel"] and not dead:
                    u = ss(x["kneel"], x["kneel"] + 0.6, t)
                    pos[j, 2] -= 0.22 * self.H[j] * u; lean[j] = -0.45 * u; Ar[j, 3] = Ar[j, 4] = 0.9 * u
                if x.get("stoop") is not None and t >= x["stoop"] and not dead and (x.get("fall") is None or t < x["fall"][0]):
                    u = ss(x["stoop"], x["stoop"] + 0.8, t)
                    lean[j] = -0.85 * u; Ar[j, 3] = 0.9 * u; Ar[j, 4] = (1.35 + 0.15 * math.sin(t * 3)) * u; Ae[j, 5] = 0.3 * u
                if x.get("climb") is not None:
                    c0, c1 = x["climb"]
                    w = bump(t, c0, c0 + 0.3, c1, c1 + 0.4)
                    if w > 0 and not dead:
                        lean[j] = -0.6 * w; Ar[j, 3] = Ar[j, 4] = 0.55 * w
                for tr in x.get("recoil", ()):
                    w = bump(t, tr, tr + 0.08, tr + 0.2, tr + 0.5)
                    if w > 0:
                        lean[j] = 0.35 * w; yaw[j] += 0.3 * w
                if x.get("slack") and not dead:
                    lean[j] = -0.14; Ar[j, 3] = Ar[j, 4] = 0.05
                if x.get("reach") is not None and not dead and t >= x["reach"]:
                    u = ss(x["reach"], x["reach"] + 1.0, t)
                    Ar[j, 3] = Ar[j, 4] = (2.2 + 0.2 * math.sin(t * 1.4 + j)) * u; lean[j] = -0.25 * u; Ae[j, 5] = Ae[j, 6] = 0.5 * u
            self._rig = odm.deform(self.RX, Ar, Ae, lean, vis, yaw, pos, pitch, None, np.zeros(len(vis))).reshape(len(vis), 4, 3)
            return R

        def build(self, coll):
            gt = SW.Geo(); tmat = []; rig = []
            hb = len(SW.T_SKINS)
            for j, sp in enumerate(self.specs):
                n0 = len(gt.fc)
                sx, sh, la, hip, hc, hr = SW.titan_geo(gt, j, sp)
                sp.update(sx=sx, sh=sh, la=la, hip=hip, hc=hc, hr=hr)
                if sp.get("beard"):
                    gt.box((0, hr * 0.55, hc - hr * 0.75), (hr * 1.2, hr * 0.7, hr * 0.8), 1, j, 0, (0, 0), (0, 0), hip, taper=0.6)
                if sp.get("longhair"):                      # hair to the shoulders (LH, the AT-less long-haired ones)
                    gt.box((0, -hr * 0.35, hc - hr * 1.0), (hr * 2.1, hr * 0.9, hr * 1.8), 1, j, 0, (0, 0), (0, 0), hip, taper=1.1)
                base = [sp["skin"], hb + (sp["hair"] if sp.get("hair") is not None else 0), hb + len(SW.T_HAIRS)]
                if sp.get("beard") and sp.get("hair") is None:
                    base[1] = hb + 1
                tmat += [base[c] for c in gt.fc[n0:]]
                rig.append([(sx, 0.0, sh - 2 * la, 5, (0, sh), (0, sh - la)), (0.0, hr * 0.9, hc - hr * 0.3, 0, (0, 0), (0, 0)),
                            (0.0, -hr * 0.9, hc - hr * 1.1, 0, (0, 0), (0, 0)), (0.0, 0.0, hc + hr * 1.05, 0, (0, 0), (0, 0))])
            tm = [L.mat(f"G5_tskin{i}", hexrgb(WARM_SKINS[i % len(WARM_SKINS)]), 0.65) for i in range(len(SW.T_SKINS))] + [L.mat(f"G5_thair{i}", c, 0.7) for i, c in enumerate(SW.T_HAIRS)] \
                + [L.mat("G5_tteeth", (0.85, 0.80, 0.70), 0.5)]
            self.R = gt.finish()
            self.ob = SW._mesh("TrostTitans", self.R, gt.f, tmat, tm, coll)
            Bp, oid, part, pr, pe, hipl = [], [], [], [], [], []
            for j, rr in enumerate(rig):
                for (x, y, z, p, a, b) in rr:
                    Bp.append((x, y, z)); oid.append(j); part.append(p); pr.append(a); pe.append(b); hipl.append(self.specs[j]["hip"])
            self.RX = {"B": np.array(Bp, float), "oid": np.array(oid, np.int32), "part": np.array(part, np.int32),
                       "pr": np.array(pr, float), "pe": np.array(pe, float), "hip": np.array(hipl, float)}
            self.RX["up"] = np.isin(self.RX["part"], (0, 3, 4, 5, 6)).astype(float)
            self.H = np.array([sp["H"] for sp in self.specs])
            self.steam = FX.PuffField("G5TitanSteam", kind="steam", alpha=0.55)
            rnd = np.random.default_rng(7)
            for j in range(len(self.specs)):
                d = self.ev[j]["death"]
                if not d:
                    continue
                td = d[0]; H = self.H[j]
                n = int(16 + 2.0 * H)
                te = td + 0.6 + rnd.random(n) * 9.0
                k = np.clip((te / TA.DT).astype(int), 0, self.K - 1)
                yawv = self.TYAW[k, j]; dirn = d[1]
                along = rnd.random(n) * H * 0.9
                Pp = np.stack([self.TX[k, j] - np.sin(yawv) * along * dirn, self.TY[k, j] + np.cos(yawv) * along * dirn,
                               self.TZ[k, j] + 0.25 * H * rnd.random(n)], 1)
                self.steam.add_many(te, Pp, rnd.normal(0, 0.4, (n, 3)), r0=0.06 * H, r1=(0.16 + 0.1 * rnd.random(n)) * H,
                                    life=3.5 + 2.5 * rnd.random(n), rise=1.4 + 0.1 * H)
            self.steam.build(coll)

        def override(self, name, t0, t1, p0, p1):
            """Straight path override (set coords xy) between t0 and t1 after sim (hurls, skids, slams); holds p1 after."""
            j = self.j(name)
            k0, k1 = int(round(t0 / TA.DT)), int(round(t1 / TA.DT))
            for k in range(max(0, k0), self.K):
                u = 1.0 if k >= k1 else ss(k0, k1, k)
                self.TX[k, j] = p0[0] + (p1[0] - p0[0]) * u; self.TY[k, j] = p0[1] + (p1[1] - p0[1]) * u
                self.TZ[k, j] = self.site.g((self.TX[k, j], self.TY[k, j]))
            self._cache_t = None
    return Titans5

def _keys_path(t_start, pts, v):
    """Constant-speed time keys (t, x, y) (M) along the polyline pts from t_start."""
    S = poly_len(pts)
    return [(t_start + s / v, float(p[0]), float(p[1])) for s, p in zip(S, np.asarray(pts, float))]

def build_titans(coll):
    import trost_action as TA
    Titans5 = make_titans_class()
    TR = STATE["TR"]
    nav = TA.Site(dict(gate=TR.OUTER_GATE, hq=S3(*HQ)[:2], boulder=S3(290, 262)[:2], roofs=np.zeros((1, 3)),
                       ground=lambda x, y: G(x, y + segtime.SET_OFF_Y), walkable=TR.walkable,
                       bounds=(-470.0, 470.0, -870.0 - 140.0, -870.0 + 560.0), pyre=S3(-60, 470)[:2]))
    TT = Titans5(_TSite(nav), seed=505)
    STATE["TT"] = TT
    rnd = random.Random(505)
    SPEC = {}
    def add(name, H, keys_M, show=(-1e9, 1e9), g5=None, **sp):
        keys = [(k[0], *S3(k[1], k[2])[:2]) for k in keys_M]
        keys.sort(key=lambda k: k[0])
        if keys[-1][0] < 999:
            keys.append((999.0, keys[-1][1], keys[-1][2]))
        if keys[0][0] > -1:
            keys.insert(0, (-10.0, keys[0][1], keys[0][2]))
        TT.add(name, H=H, keys=keys, show=show, **sp)
        TT.specs[-1]["g5"] = g5 or {}
        SPEC[name] = dict(H=H, keys=keys_M)
        return name
    def kill(name, td, dirn=1, keep=True, shrink=0.85, shrink_t=20.0):
        TT.ev[TT.j(name)]["death"] = (td, dirn)
        TT.specs[TT.j(name)].setdefault("g5", {}).update(keep=keep, shrink=shrink, shrink_t=shrink_t)
    def face(name, xy):
        q = S3(*xy)[:2]; TT.specs[TT.j(name)]["face"] = (float(q[0]), float(q[1]))
    def route(a, b):
        P, s = TA.path(nav, S3(*a)[:2], S3(*b)[:2], rnd.uniform(-1, 1))
        return [(float(p[0]), float(p[1]) + segtime.SET_OFF_Y) for p in P]
    # ---------------- the pour P1-P35: size mix 25 / 45 / 20 / 10 %, <= 3 abreast in the hole, ~2.1 / s
    sizes = [rnd.uniform(3.0, 4.0) for _ in range(9)] + [rnd.uniform(5.0, 7.0) for _ in range(16)] + \
            [rnd.uniform(8.0, 10.0) for _ in range(7)] + [rnd.uniform(12.0, 15.0) for _ in range(3)]
    rnd.shuffle(sizes)
    roles = ["first", "abn1", "av", "av", "ring_w", "av", "ring_e", "trench1", "av", "abn2", "av", "crater", "ring_w", "av",
             "ring_e", "prone", "av", "av", "sit", "ring_w", "av", "trench2", "ring_e", "av", "lip", "av", "ring_w", "av", "ring_e",
             "av", "mill", "ring_w", "av", "ring_e", "lip"]
    BIG = [1, 2, 3, 4, 5, 6, 7, 8]                             # 8 extra large walkers (8-15 m) right behind the first titan
    big_roles = ["av", "av", "ring_w", "av", "av", "ring_e", "av", "av"]
    for q, (pos_, r_) in enumerate(zip(BIG, big_roles)):
        roles.insert(pos_, r_ + "_big")
        sizes.insert(pos_, rnd.uniform(8.0, 15.0))
    i5 = min(range(len(sizes)), key=lambda i: abs(sizes[i] - 5.0)); sizes[0], sizes[i5] = sizes[i5], sizes[0]
    for r_ in ("abn1", "abn2"):
        k = roles.index(r_); sizes[k] = rnd.uniform(6.5, 8.5)
    lane_x = (-4.5, 0.0, 4.5)
    av_n = 0; rw = rn = lp = ml = 0
    RW = [(-150, 118), (-212, 200), (-262, 282), (-122, 182), (-300, 340), (-180, 260), (-240, 330)]
    RE = [(130, 108), (190, 188), (242, 262), (108, 180), (282, 330), (170, 250), (230, 320)]
    LIP = [(-21, 60), (22, 61), (-28, 47), (28, 48)]
    MILL = [[(-48, 32), (-55, 62), (-38, 88)], [(46, 34), (58, 60), (40, 92)], [(-10, 86), (12, 95), (30, 80)], [(-60, 20), (-70, 45), (-52, 70)]]
    pour = []
    for k, (H, role) in enumerate(zip(sizes, roles)):
        nm = f"p{k + 1}"
        th = BEATS["first_titan"] + 0.42 * k
        lx = lane_x[k % 3] + rnd.uniform(-0.6, 0.6)
        v = 3.2 * (1.0 + 0.17 * H) * rnd.uniform(0.9, 1.1)      # ~3-4x real: the pour streams up the town 12-30 s
        vh = 5.5                                           # one speed in the breach: 3 lanes x 0.42 s x 5.5 = 6.9 m nose to tail
        role = role.replace("_big", "")
        abn = role.startswith("abn")
        if abn:
            v = 15.0
        # outside: queued behind the wall (hidden from the town side), walking to the hole after the kick
        tw = BEATS["kick"] + 0.3
        D = vh * max(0.0, th - tw)
        qx = lx * (1 + 0.3 * k) + rnd.uniform(-6, 6) if D > 16.0 else lx
        keys = [(0.0, qx, -D), (tw, qx, -D)]
        if th - 14.0 / vh > tw + 0.05 and D > 14.0:
            keys.append((th - 14.0 / vh, lx, -14.0))
        keys += [(th, lx, 0.0), (th + 15.0 / vh, lx * 1.4, 15.0)]
        g5 = {}
        t_ = keys[-1][0]; p_ = (lx * 1.4, 15.0)
        if role == "first":
            pts = [p_, (-8, 40), (-22, 66), (-12, 90)]
        elif role in ("trench1", "trench2"):
            sg = 1 if role == "trench1" else -1
            pts = [p_, (sg * 10, 21), (sg * 18.5, 25.5)]
        elif role == "crater":
            pts = [p_, (-20, 18), (-31, 20)]
        elif role == "prone":
            pts = [p_, (0, 22), (0, 26)]
        elif role == "sit":
            pts = [p_, (-4, 24), (-12, 40)]
        elif abn:
            pts = [p_, (0, 50)] + [tuple(q) for q in AV][:3] + ([(-90, 590), (-118, 640)] if role == "abn1" else [(-40, 520), (-30, 640)])
        elif role == "av":
            yy = 150.0 + av_n * 22.0 + rnd.uniform(-6, 6); av_n += 1             # far targets: they keep walking 12-30+
            S = poly_len(AV); xs = poly_at(AV, S, yy - 74.0)
            pts = [p_, (0, 50), (0, 74), (float(xs[0]) + rnd.uniform(-4, 4), float(xs[1]))]
        elif role == "ring_w":
            pts = [p_] + route((-30, 50), RW[rw]); rw += 1
            pts = [p_, (-30, 50)] + pts[1:]
        elif role == "ring_e":
            pts = [p_] + route((30, 50), RE[rn]); rn += 1
            pts = [p_, (30, 50)] + pts[1:]
        elif role == "lip":
            pts = [p_, (LIP[lp][0] * 0.4, 28), LIP[lp]]; lp += 1
        else:
            pts = [p_] + MILL[ml]; ml += 1
        kk = _keys_path(t_, pts, v)[1:]
        if role == "mill":                                   # pauses between the waypoints
            kk2 = []; dt_ = 0.0
            for q in kk:
                kk2.append((q[0] + dt_, q[1], q[2])); dt_ += 2.5; kk2.append((q[0] + dt_, q[1], q[2]))
            kk = kk2
        keys += kk
        if role in ("trench1", "trench2"):
            g5["trip"] = keys[-1][0] - 0.3
        elif role == "crater":
            g5["kneel"] = keys[-1][0] - 0.2
        elif role == "sit":
            g5["sit"] = keys[-1][0] + 0.2
        elif role == "prone":
            g5["fall"] = (keys[-1][0] + 0.4, 0.7, 1)
        hair = rnd.choice([None, 0, 1, 2, 3])
        kw = dict(abnormal=abn, hair=hair)
        if role == "abn1":
            kw.update(g=0.75, al=1.25)
        add(nm, H, keys, show=(0.0, 99.0), g5=g5, **kw)
        pour.append((nm, role, th))
    STATE["pour"] = pour
    # deep abnormal runners already far up the town (in frame while the camera turns to the HQ and the inner gate)
    for k, (a, b) in enumerate((((-60, 470), (-230, 560)), ((-75, 520), (-150, 470)), ((-40, 560), (-120, 600)))):
        P_ = route(a, b)
        keys = [(0.0, *P_[0])] + [(k_[0] + 15.0 + 2.0 * k, k_[1], k_[2]) for k_ in _keys_path(0.0, P_, 9.0)]
        add(f"deep{k}", rnd.uniform(6.0, 9.0), keys, show=(14.0, 99.0), abnormal=True, hair=rnd.choice([None, 0, 1]))
    # ---------------- outside: titans crossing the fields toward the gate (beyond the wall)
    for k in range(12):
        x0 = rnd.uniform(-260, 260); y0 = rnd.uniform(-420, -170); H = 3.0 + 11.0 * rnd.random() ** 1.3
        v = 2.0 * (0.8 + 0.12 * H) * 0.6
        tgt = (x0 * 0.35, -60.0)
        dist = math.hypot(tgt[0] - x0, tgt[1] - y0)
        add(f"out{k}", H, [(0.0, x0, y0), (dist / v, *tgt)], show=(0.0, 99.0))
    # ---------------- HQ: titans at the facades (peering in), a few wandering (g6 picks them up)
    hq_spots = [((-262, 610), (-262, 622)), ((-244, 609), (-244, 622)), ((-212, 620), (-212, 630)), ((-184, 621), (-184, 630)),
                ((-152, 620), (-152, 630)), ((-272, 664), (-268, 652))]
    for k, (p, f) in enumerate(hq_spots):
        add(f"hq{k}", rnd.uniform(5.0, 10.0), [(0.0, *p)], show=(0.0, 99.0), g5=dict(reach=rnd.uniform(0.0, 20.0)))
        face(f"hq{k}", f)
        TT.ev[-1]["lean"] = (rnd.uniform(0, 30), )
    for k, (a, b) in enumerate((((-160, 592), (-120, 600)), ((-286, 596), (-284, 630)), ((-206, 588), (-180, 580)), ((-120, 610), (-100, 640)))):
        add(f"hqw{k}", rnd.uniform(4.0, 9.0), [(0.0, *a), (35.0, *b), (70.0, *a)], show=(0.0, 99.0))
    # ---------------- AB: the Abnormal at the evacuation (12.5 m, pot-bellied) - rounds into EVS at 26, killed 33.8
    ab_pts = [(22, 668), (0, 690), AB_IN, AB_KILL]
    ab_keys = [(0.0, 30, 655), (BEATS["ab_run"][0], 30, 655)]
    S = poly_len([(30, 655)] + ab_pts)
    for s, p in zip(S[1:], ab_pts):
        ab_keys.append((BEATS["ab_run"][0] + (BEATS["kill"] - BEATS["ab_run"][0]) * s / S[-1], *p))
    add("AB", 12.5, ab_keys, show=(BEATS["ab_run"][0] - 0.2, 99.0), g5=dict(fall=(BEATS["kill"], 0.75, 1)), g=1.85, al=0.9,
        hs=1.15, hair=0, grin=True, abnormal=True)
    kill("AB", BEATS["skid"][1], 1, keep=True, shrink=0.8, shrink_t=40.0)
    # ---------------- TR1 (bald 6 m) on Mikasa's route, killed 51.0
    add("TR1", 6.0, [(0.0, -246, 336), (45.0, -246, 336), (50.6, *TR1_POS)], show=(0.0, 99.0), hair=None, g=1.0)
    kill("TR1", BEATS["tr1_kill"], 1, keep=True, shrink=0.8)
    # ---------------- BT (bearded 10 m) standing slack in SS, torn open 54.5
    add("BT", 10.0, [(0.0, *BT_POS)], show=(0.0, 99.0), g5=dict(slack=True), beard=True, hair=1, g=1.15)
    face("BT", (-230, 423))
    kill("BT", BEATS["bt_torn"] + 0.05, -1, keep=True, shrink=0.42, shrink_t=14.0)
    # ---------------- CAP (stocky bowl-cut grin) climbs in over the rubble, stoops over Mikasa, punched 57.4
    c0, c1 = BEATS["cap_in"]
    add("CAP", 8.6, [(0.0, -256, 480), (c0, -256, 480), (c0 + 0.6, -253.5, 467), (c0 + 1.2, -261, 457), (c0 + 2.0, -262, 441), (c1, -262, 418)],
        show=(c0 - 0.1, 99.0), g5=dict(climb=(c0, c0 + 1.6), stoop=c1 - 0.4, fall=(BEATS["punch"] + 0.05, 0.45, 1)),
        g=1.4, al=1.05, hs=1.2, hair=0, grin=True)
    face("CAP", MA_LAND)
    kill("CAP", BEATS["stomps"][-1], 1, keep=True, shrink=0.8)
    # ---------------- LH (long-haired 7 m) climbs in behind it, stamped 60.35
    l0, l1 = BEATS["lh_in"]
    add("LH", 7.0, [(0.0, -255, 483), (l0, -255, 483), (l0 + 0.8, -253.5, 468), (l1, -261.5, 451), (57.6, -261.5, 451), (58.9, -264.5, 413)],
        show=(l0 - 0.1, 99.0), g5=dict(climb=(l0, l1 + 0.4), fall=(59.0, 0.5, 1)), g=0.85, longhair=True, hair=1)
    face("LH", (-262, 420))
    kill("LH", BEATS["lh_stamp"] + 0.05, 1, keep=True, shrink=0.8)
    # ---------------- CC (crew cut 12 m): into Q2 from the east, boxed, slammed into tower T, nape stamped
    q0, q1 = BEATS["cc_in"]
    add("CC", 12.0, [(0.0, -196, 497), (q0, -196, 497), (q1, -232, 507)], show=(q0 - 0.1, 99.0),
        g5=dict(recoil=BEATS["blows"], fall=(BEATS["cc_slide"][0] + 0.2, 0.7, 1)), g=0.95, al=1.05, hair=0)
    face("CC", (-246, 499))
    kill("CC", BEATS["nape_stamp"], 1, keep=True, shrink=0.85)
    # ---------------- sim, then the vanguard kills / grab chosen from where the pour actually is
    TT.sim(DUR + 1.0)
    # AB skid: pitches forward at the cut and slides 15 m to the corpse spot
    TT.override("AB", BEATS["kill"], BEATS["skid"][1], S3(*AB_KILL)[:2], S3(*AB_CORPSE)[:2])
    # CAP hurled west against the alley wall; CC driven into the tower's south face
    TT.override("CAP", BEATS["punch"], BEATS["punch"] + 0.45, S3(-262, 418)[:2], S3(-265.0, 401.5)[:2])
    TT.override("CC", BEATS["slam"] - 0.15, BEATS["slam"] + 0.12, S3(-232, 507)[:2], S3(-221.5, 514.5)[:2])
    def near(t, xy, roles_ok, used):
        best = None
        for nm, role, th in pour:
            if role not in roles_ok or nm in used or th > t - 2.0 or TT.H[TT.j(nm)] >= 8.0:
                continue
            p = TT.pos(nm, t); q = np.array([p[0], p[1] + segtime.SET_OFF_Y])
            d = float(np.linalg.norm(q - np.array(xy)))
            if best is None or d < best[0]:
                best = (d, nm)
        return best[1] if best else None
    used = set()
    vk = []
    for te, xy, ok in ((BEATS["vkills"][0], (0, 90), ("av", "first")), (BEATS["vkills"][1], (90, 110), ("ring_e", "av")),
                       (BEATS["vkills"][2], (-20, 60), ("lip", "mill", "av", "ring_w", "ring_e"))):
        nm = near(te, xy, ok, used)
        if nm:
            used.add(nm); TT.ev[TT.j(nm)]["death"] = (te, 1); TT.specs[TT.j(nm)].setdefault("g5", {}).update(keep=True, shrink=0.8)
            vk.append((nm, te))
    STATE["vkills"] = vk
    grab = near(BEATS["overrun"], (-150, 130), ("ring_w",), used)
    if grab:
        TT.ev[TT.j(grab)]["grab"].append(BEATS["overrun"])
        used.add(grab)
    STATE["grabber"] = grab
    TT.sim(DUR + 1.0)
    TT.override("AB", BEATS["kill"], BEATS["skid"][1], S3(*AB_KILL)[:2], S3(*AB_CORPSE)[:2])
    TT.override("CAP", BEATS["punch"], BEATS["punch"] + 0.45, S3(-262, 418)[:2], S3(-265.0, 401.5)[:2])
    TT.override("CC", BEATS["slam"] - 0.15, BEATS["slam"] + 0.12, S3(-232, 507)[:2], S3(-221.5, 514.5)[:2])
    TT.build(coll)
    say(f"titans: {len(TT.specs)}; vanguard kills {vk}; grab {grab}")

def build_shadows(coll):
    """Soft dark contact-shadow blobs under every pure titan and the Attack Titan (they read on the beige paving)."""
    n = len(STATE["TT"].specs) + 1
    V = np.zeros((4 * n, 3)); F = [[4 * k, 4 * k + 1, 4 * k + 2, 4 * k + 3] for k in range(n)]
    me = bpy.data.meshes.new("G5_ContactShadows"); me.from_pydata(V.tolist(), [], F)
    uv = me.uv_layers.new(name="UVMap"); uv.data.foreach_set("uv", np.tile([0, 0, 1, 0, 1, 1, 0, 1], n).astype(np.float32))
    m = bpy.data.materials.new("G5_ContactShadow"); m.use_nodes = True
    nt = m.node_tree; N = nt.nodes; Lk = nt.links
    N.remove(N["Principled BSDF"])
    tc = N.new("ShaderNodeTexCoord")
    sub = N.new("ShaderNodeVectorMath"); sub.operation = "SUBTRACT"; sub.inputs[1].default_value = (0.5, 0.5, 0.0)
    Lk.new(tc.outputs["UV"], sub.inputs[0])
    ln = N.new("ShaderNodeVectorMath"); ln.operation = "LENGTH"; Lk.new(sub.outputs[0], ln.inputs[0])
    mr = N.new("ShaderNodeMapRange"); mr.inputs["From Min"].default_value = 0.18; mr.inputs["From Max"].default_value = 0.5
    mr.inputs["To Min"].default_value = 0.55; mr.inputs["To Max"].default_value = 0.0; Lk.new(ln.outputs["Value"], mr.inputs["Value"])
    em = N.new("ShaderNodeEmission"); em.inputs["Color"].default_value = (0.02, 0.016, 0.012, 1.0); em.inputs["Strength"].default_value = 1.0
    tr = N.new("ShaderNodeBsdfTransparent"); mx = N.new("ShaderNodeMixShader")
    Lk.new(mr.outputs["Result"], mx.inputs[0]); Lk.new(tr.outputs[0], mx.inputs[1]); Lk.new(em.outputs[0], mx.inputs[2])
    Lk.new(mx.outputs[0], N["Material Output"].inputs["Surface"])
    try:
        m.surface_render_method = "BLENDED"
    except Exception:
        pass
    m["toon"] = 1
    me.materials.append(m); me.update()
    ob = bpy.data.objects.new("G5_ContactShadows", me); coll.objects.link(ob); ob.visible_shadow = False
    STATE["shadows"] = ob

def update_shadows(t):
    TT = STATE["TT"]; ob = STATE["shadows"]
    Ar, Ae, lean, vis, yaw, pos, pitch = TT.poses(t)
    H = TT.H
    n = len(H)
    c = pos.copy(); c[:, 2] += 0.12
    fw = np.column_stack([-np.sin(yaw), np.cos(yaw), np.zeros(n)]); rt = np.column_stack([np.cos(yaw), np.sin(yaw), np.zeros(n)])
    ly = np.abs(np.sin(pitch))
    c += fw * (0.42 * H * ly * np.sign(-pitch + 1e-9))[:, None]
    a = 0.30 * H * np.maximum(vis, 0.0); b = a * (1.0 + 1.4 * ly)
    on = vis > 0.02
    st = at_state(t)
    if st["vis"]:
        p = st["pos"]; ca = S3(p[0], p[1], G(*p) + st["z"] + 0.12)
    else:
        ca = np.array([0, 0, -500.0])
    c = np.vstack([c, ca]); a = np.append(a, 4.2); b = np.append(b, 4.2); on = np.append(on, bool(st["vis"]))
    fw = np.vstack([fw, [0, 1, 0]]); rt = np.vstack([rt, [1, 0, 0]])
    V = np.zeros((len(a), 4, 3))
    for q, (sx, sy) in enumerate(((-1, -1), (1, -1), (1, 1), (-1, 1))):
        V[:, q] = c + rt * (sx * a)[:, None] + fw * (sy * b)[:, None]
    V[~on] = np.array([0, 0, -500.0])
    ob.data.vertices.foreach_set("co", V.reshape(-1).astype(np.float32)); ob.data.update()

def titan_M(name, t, part="pos"):
    TT = STATE["TT"]
    p = getattr(TT, part)(name, t)
    return np.array([p[0], p[1] + segtime.SET_OFF_Y, p[2]])

# ====================================================================== people: ODM squads (odm.Squads)
WIRE_MAX = 32.0
def _short_hop(self, t0, t1, p0, p1, apex=None, gas=1.0, anchors=None):
    """odm Flyer.hop with wires <= WIRE_MAX: long hops become a chain of sub-hops, each hooked to a roof / wall point
    just beyond its landing (a short taut wire, retracted on arrival)."""
    import odm
    p0 = np.asarray(p0, float); p1 = np.asarray(p1, float)
    L_ = float(np.linalg.norm(p1 - p0))
    if anchors is not None:
        A = np.asarray(anchors[0], float)
        if np.linalg.norm(A - (p0 + np.array([0, 0, 0.9]))) <= WIRE_MAX + 3:
            return odm.Flyer.hop(self, t0, t1, p0, p1, apex, gas, [A])
    n = max(1, int(math.ceil(L_ / (WIRE_MAX - 6.0))))
    pts = [p0 + (p1 - p0) * (k / n) for k in range(n + 1)]
    for k in range(1, n):                                          # mid-air waypoints ride a little higher
        pts[k] = pts[k] + np.array([0.0, 0.0, 3.0])
    for k in range(n):
        a, b = pts[k], pts[k + 1]
        d = b - a; dh = np.array([d[0], d[1], 0.0]); lh = float(np.linalg.norm(dh))
        fwd = dh / lh if lh > 1e-3 else np.array([0.0, 1.0, 0.0])
        q = b + fwd * 3.0
        zr = top_z(float(q[0]), float(q[1]) + segtime.SET_OFF_Y)
        A = np.array([q[0], q[1], max(zr + 0.5, b[2] + 4.0)])
        hip = a + np.array([0, 0, 0.9])
        if np.linalg.norm(A - hip) > WIRE_MAX:                     # too far: anchor along the line
            A = hip + (A - hip) / np.linalg.norm(A - hip) * WIRE_MAX
        ta = t0 + (t1 - t0) * k / n; tb = t0 + (t1 - t0) * (k + 1) / n
        odm.Flyer.hop(self, ta, tb, a, b, apex, gas if k == n - 1 else 1.0, [A])
    return self

def build_people(coll):
    import odm
    rnd = random.Random(850)
    SQ = odm.Squads("G5Squads", pscale=1.0, hook=True)          # owner 10/27: one hook per shot
    _flyer0 = SQ.flyer
    def _flyer(*a, **k):                                           # every hop: wire <= ~32 m to a nearby anchor
        f = _flyer0(*a, **k); f.hop = types.MethodType(_short_hop, f); return f
    SQ.flyer = _flyer
    STATE["SQ"] = SQ
    TT = STATE["TT"]
    P = lambda x, y, z: S3(x, y, z)
    yaw_n = odm.yaw_of(np.array([0.0, 1.0, 0.0])); yaw_s = odm.yaw_of(np.array([0.0, -1.0, 0.0]))
    def yaw_at(a, b):
        return odm.yaw_of(np.array([b[0] - a[0], b[1] - a[1], 0.0]))
    nape = lambda nm: (lambda t: TT.nape(nm, t))
    # ---------------- wall top above O: 7 cadets (Eren among them) + Garrison pairs at the bulge guns
    cad = []
    for k, x in enumerate((-56, 0, -26, -12, 12, 30, 52)):   # owner 10/27: Eren (x 0) directly above O, the Colossal rises over him
        yc = 480.0 - math.sqrt(480.0 ** 2 - x * x)
        f = SQ.flyer("eren" if x == 0 else f"wc{k}", "cadet", "brown" if x == 0 else rnd.choice(["dark", "ash", "black", "jean"]),
                     **(dict(accent=(0.04, 0.8, 0.32), cloak=(0.13, 0.19, 0.07)) if x == 0 else {}))
        cad.append((f, P(x, yc + 1.5, 50.3)))
    flung = [0, 2, 4, 5]
    for k, (f, p0) in enumerate(cad):
        f.stand(0.0, BEATS["kick"] + 0.12, p0, yaw_s)
        if f.name == "eren":
            continue
        if k in flung:                                     # thrown up off the wall top by the shock, catch themselves on wires
            land = roof_set(p0[0] * 1.3 + rnd.uniform(-10, 10), 95 + 18 * k)
            f.hop(BEATS["kick"] + 0.12 + 0.05 * k, BEATS["flung"][1] + 0.3 * k, p0, land, apex=14).stand(BEATS["flung"][1] + 0.3 * k, DUR, land, yaw_s, "crouch")
        else:                                              # down the inner face on wires
            gp = gnd_set(p0[0], 16 + 3 * k)
            f.hop(BEATS["drop_wires"][0] + 0.2 * k, BEATS["drop_wires"][1] + 0.2 * k, p0, gp, apex=1.0,
                  anchors=(np.array([p0[0], p0[1] + 4.5, 26.0]),))
            f.stand(BEATS["drop_wires"][1] + 0.2 * k, DUR, gp, yaw_s, "stand")
    # Eren: holds on the wall top, runs at the sweeping forearm (7.6-9.0), steam burst, back on the wall top
    er = SQ.by_name["eren"]; e0 = cad[1][1]
    arm_pt = lambda t: S3(sweep_hand(t)) + np.array([3.0, -2.0, 2.0])
    er.stand(BEATS["kick"] + 0.12, BEATS["eren_arm"][0], e0, yaw_s, "crouch")
    er.hop(BEATS["eren_arm"][0], 8.3, e0, arm_pt(8.3), apex=5)
    er.follow(8.3, 8.7, lambda t: arm_pt(t) + np.array([2.0 * ss(8.3, 8.7, t), -4.0 * ss(8.3, 8.7, t), 1.5 * ss(8.3, 8.7, t)]), pose="run")
    neck = S3(-4.0, -14.0, 56.0)
    er.hop(8.7, BEATS["steam_burst"] + 0.1, arm_pt(8.7) + np.array([2.0, -4.0, 1.5]), neck, apex=3)
    eb = P(-30.0, 2.5, 50.3)
    er.hop(BEATS["steam_burst"] + 0.1, 10.4, neck, eb, apex=6).stand(10.4, DUR, eb, yaw_s, "crouch")
    for k, x in enumerate((-87, -54, 18, 48, 78, -120, 108, -150, 140, -180)):
        yc = 480.0 - math.sqrt(480.0 ** 2 - x * x)
        for q in (-1, 1):
            f = SQ.flyer(f"gun{k}_{q}", "garrison", rnd.choice(["dark", "brown", "ash", "black", "grey"]))
            f.stand(0.0, DUR, P(x + 1.6 * q, yc + 2.6, 50.3), yaw_s if x != -54 else yaw_n, "stand")
    # ---------------- vanguard: 6 squads (30) on the roofs ringing GS r 90-160 and lower AV; nape kills + a grab
    vsq = [(-120, 70), (-95, 125), (-40, 150), (55, 150), (105, 110), (135, 60)]
    vflyers = []
    for s, (cx, cy) in enumerate(vsq):
        for k in range(5):
            f = SQ.flyer(f"v{s}_{k}", "garrison", rnd.choice(["dark", "brown", "ash", "black", "grey", "auburn"]))
            p = roof_set(cx + rnd.uniform(-16, 16), cy + rnd.uniform(-16, 16))
            vflyers.append((f, p))
    killers = {}
    for (nm, te), (f, p) in zip(STATE["vkills"], [vflyers[2], vflyers[22], vflyers[13]]):
        killers[f.name] = (nm, te)
    grab_f = vflyers[6][0] if STATE.get("grabber") else None
    for idx, (f, p) in enumerate(vflyers):
        if f.name in killers:
            nm, te = killers[f.name]
            q = titan_M(nm, te - 1.6)
            st_ = roof_set(q[0] + rnd.uniform(-14, 14), q[1] + rnd.uniform(-14, 14))
            f.stand(0.0, te - 3.2, p, yaw_s, "crouch").hop(te - 3.2, te - 1.4, p, st_, apex=7)
            f.dive(te - 1.0, te, st_ + np.array([0, 0, 2.0]), nape(nm))
            land = roof_set(q[0] + rnd.uniform(-25, 25), q[1] + rnd.uniform(10, 30))
            f.hop(te, te + 1.4, TT.nape(nm, te), land, apex=8).stand(te + 1.4, DUR, land, yaw_s, "crouch")
            continue
        if grab_f is f and STATE.get("grabber"):
            g = STATE["grabber"]; tg = BEATS["overrun"]
            hp = TT.hand(g, tg - 0.05)
            spot = np.array([hp[0], hp[1], top_z(hp[0], hp[1] + segtime.SET_OFF_Y) + 0.05])
            f.stand(0.0, tg - 2.2, p, yaw_s, "crouch").hop(tg - 2.2, tg - 0.6, p, spot, apex=5).stand(tg - 0.6, tg + 0.6, spot, yaw_s, "stand")
            f.follow(tg + 0.6, tg + 2.6, lambda t, g=g: TT.hand(g, t), pose="flail").gone(tg + 2.6)
            continue
        f.stand(0.0, 9.5 + rnd.uniform(0, 3), p, yaw_s, rnd.choice(["crouch", "stand"]))
        t_ = f.t_end(); prev = p
        while t_ < 30.0:                                   # relocate over the roofs (gas puffs)
            if rnd.random() < 0.55:
                q = roof_set(prev[0] + rnd.uniform(-35, 35), prev[1] + segtime.SET_OFF_Y + rnd.uniform(-25, 30))
                d = float(np.linalg.norm(q[:2] - prev[:2])); dt = max(0.9, d / 24.0)
                f.hop(t_, t_ + dt, prev, q, apex=6); prev = q; t_ += dt
            st = rnd.uniform(1.5, 4.0); f.stand(t_, t_ + st, prev, yaw_s, rnd.choice(["crouch", "stand"])); t_ += st
        f.stand(t_, DUR, prev, yaw_s, "crouch")
    # ---------------- middle guard: 14 squads of 5 on the roof band Y 250-520 (2 relocate 19-25)
    for s in range(14):
        side = -1 if s % 2 == 0 else 1
        y = 250 + (s // 2) * 42 + rnd.uniform(-8, 8)
        x = -25 + side * rnd.uniform(40, 120) - 0.25 * (y - 250)
        for k in range(5):
            f = SQ.flyer(f"m{s}_{k}", "cadet" if k else "garrison", rnd.choice(["dark", "brown", "ash", "black", "blond", "auburn"]))
            p = roof_set(x + rnd.uniform(-10, 10), y + rnd.uniform(-10, 10))
            if s in (3, 8):
                q = roof_set(x + side * 60 + rnd.uniform(-8, 8), y + 40 + rnd.uniform(-8, 8))
                t0_ = BEATS["relocate"][0] + 0.5 * k + 2.0 * (s == 8)
                f.stand(0.0, t0_, p, yaw_s, "crouch").hop(t0_, t0_ + 2.4, p, q, apex=8).stand(t0_ + 2.4, DUR, q, yaw_s, "crouch")
            else:
                f.stand(0.0, DUR, p, yaw_s, rnd.choice(["crouch", "stand", "stand"]))
    # ---------------- rear guard: ~20 on the roofs ringing E and the HQ, 2 in E; Rose top above E: 8 watching
    for k in range(20):
        a = rnd.uniform(0, math.tau)
        c = (-140, 810) if k < 11 else HQ
        r_ = rnd.uniform(45, 75) if k < 11 else rnd.uniform(40, 70)
        x, y = c[0] + r_ * math.cos(a), min(c[1] + r_ * math.sin(a), 845.0)
        f = SQ.flyer(f"r{k}", "garrison", rnd.choice(["dark", "brown", "ash", "black", "grey"]))
        f.stand(0.0, DUR, roof_set(x, y), yaw_s, rnd.choice(["crouch", "stand"]))
    for k, p in enumerate(((-170, 808), (-106, 832))):
        f = SQ.flyer(f"rE{k}", "garrison", "dark"); f.stand(0.0, DUR, gnd_set(*p), yaw_at(p, ARCH), "stand")
    for k in range(8):
        x = -200 + 16 * k + rnd.uniform(-2, 2)
        f = SQ.flyer(f"rose{k}", "garrison", rnd.choice(["dark", "brown", "ash", "grey"]))
        f.stand(0.0, DUR, P(x, 866.5, 50.3), yaw_s, "stand")
    # ---------------- Mikasa + the Garrison soldier: chase AB (26-33.8), the kill, the corpse, the hop, the merchant
    mk = SQ.flyer("mikasa", "cadet", "black", scarf=True)
    so = SQ.flyer("soldier", "garrison", "brown")
    abp = lambda t: titan_M("AB", t)
    def chase_pt(t, lag, side, up):
        t2 = max(BEATS["ab_run"][0], t - lag)
        a = abp(t2); b = abp(t2 + 0.2); d = b[:2] - a[:2]; n = np.linalg.norm(d)
        d = d / n if n > 1e-6 else np.array([-0.7, 0.7])
        left = np.array([-d[1], d[0]])
        return S3(a[0] + left[0] * side, a[1] + left[1] * side, G(a[0], a[1]) + up)
    m0 = roof_set(24, 650); s0 = roof_set(36, 640)
    def behind(t, d_, side=0.0):
        a = abp(t); b = abp(t + 0.2); dv = b[:2] - a[:2]; nn = np.linalg.norm(dv)
        dv = dv / nn if nn > 1e-6 else np.array([-0.68, 0.73])
        q = a[:2] - dv * d_ + np.array([-dv[1], dv[0]]) * side
        return gnd_set(q[0], q[1], dz=0.1), dv
    def wall_anchor(p, dv, side):                                   # a point on the street-side facade, 10 m up
        q = p[:2] + np.array([-dv[1], dv[0]]) * side * 7.0 + dv * 8.0
        return np.array([q[0], q[1], top_z(float(q[0]), float(q[1]) + segtime.SET_OFF_Y) * 0.6 + 2.0])
    mk.stand(0.0, 29.4, m0, yaw_at((24, 650), AB_IN), "crouch"); so.stand(0.0, 29.9, s0, yaw_at((36, 640), AB_IN), "crouch")
    land1, dv1 = behind(30.5, 26.0, 2.0)
    mk.hop(29.4, 30.5, m0, land1, apex=4)                          # down into the open street behind it
    prev = land1
    for t_a, t_b, dd_ in ((30.5, 31.6, 20.0), (31.6, 32.7, 14.0)):  # skims along the street on short hooks
        q, dv = behind(t_b, dd_, 1.5)
        q = q + np.array([0.0, 0.0, 2.5])
        mk.hop(t_a, t_b, prev, q, apex=2, anchors=[wall_anchor(q, dv, 1.0)]); prev = q
    mk.dive(32.7, BEATS["kill"], prev, lambda t: TT.nape("AB", t) + np.array([0, 0, 0.6]))
    sl1, sdv = behind(31.0, 30.0, -2.0)
    so.hop(29.9, 31.0, s0, sl1, apex=4); prev = sl1
    for t_a, t_b, dd_ in ((31.0, 32.2, 26.0), (32.2, 33.6, 24.0)):
        q, dv = behind(t_b, dd_, -2.0)
        so.hop(t_a, t_b, prev, q, apex=2, anchors=[wall_anchor(q, dv, -1.0)]); prev = q
    sl = gnd_set(-82.0, 778.0)
    so.walk(33.6, 34.8, prev, sl, "run").stand(34.8, DUR, sl, yaw_at((-82, 778), AB_CORPSE), "stand")
    back = lambda t: TT.nape("AB", t) + np.array([0.0, 0.0, 0.5])
    mk.follow(BEATS["kill"], BEATS["hop"][0], back, yaw_fn=lambda t: yaw_at(AB_CORPSE, MERCHANT), pose="stand")
    land = gnd_set(*MIK_LAND)
    mk.hop(BEATS["hop"][0], BEATS["hop"][1], back(BEATS["hop"][0]), land, apex=10,
           anchors=(S3(-139, 851, 16),))
    face_p = gnd_set(*MIK_FACE)
    mk.walk(BEATS["lane"][0], BEATS["lane"][1], land, face_p, "run")
    mk.stand(BEATS["lane"][1], BEATS["back_corpse"][0], face_p, yaw_n, "stand")
    mk.hop(BEATS["back_corpse"][0], BEATS["back_corpse"][1], face_p, back(BEATS["back_corpse"][1]), apex=8)
    mk.follow(BEATS["back_corpse"][1], BEATS["mikasa_sw"], back, yaw_fn=lambda t: yaw_at(AB_CORPSE, ARCH), pose="stand")
    sw = roof_set(-176, 752)
    mk.hop(BEATS["mikasa_sw"], BEATS["mikasa_sw"] + 1.3, back(BEATS["mikasa_sw"]), sw, apex=9).gone(BEATS["mikasa_sw"] + 1.6)
    # ---------------- the 104th stream (20 + Armin, Connie, Jean, Sasha), Mikasa leading 30 m ahead
    m1 = S3(-252, 296, 26.0); kill_pt = lambda t: TT.nape("TR1", t)
    mk2 = SQ.flyer("mikasa2", "cadet", "black", scarf=True)
    pts_m = [m1, roof_set(-250, 318)]
    mk2.stand(BEATS["stream"][0] - 0.01, BEATS["stream"][0], m1, yaw_n)
    mk2.hop(BEATS["stream"][0], 50.3, m1, pts_m[1], apex=6)
    mk2.dive(50.3, BEATS["tr1_kill"], pts_m[1] + np.array([0, 0, 3.0]), kill_pt)
    q2 = roof_set(-254, 362)
    mk2.hop(BEATS["tr1_kill"], 51.9, kill_pt(BEATS["tr1_kill"]), q2, apex=6)
    q3 = S3(-258.0, 386.0, 22.0)
    mk2.hop(51.9, BEATS["sputter"] + 0.2, q2, q3, apex=4, gas=0.45)
    fall_pt = gnd_set(*MA_LAND, dz=0.1)
    mk2.fall(BEATS["sputter"] + 0.2, BEATS["fall"], q3, fall_pt, spin=0.8)
    mk2.stand(BEATS["fall"], BEATS["charge"][0], fall_pt, yaw_n, "kneel")
    cap_feet = gnd_set(-262.0, 412.0)
    mk2.walk(BEATS["charge"][0], BEATS["charge"][1], fall_pt, cap_feet, "run")
    thrown = gnd_set(-259.0, 392.0)
    mk2.fall(BEATS["punch"] + 0.02, BEATS["punch"] + 0.55, cap_feet, thrown, spin=0.6)
    mk2.stand(BEATS["punch"] + 0.55, 58.6, thrown, yaw_n, "lie")
    watch = gnd_set(-259.0, 388.5)
    mk2.walk(58.6, 59.4, thrown, watch, "run").stand(59.4, BEATS["rescue"][0] + 0.6, watch, yaw_n, "crouch")
    STATE["mikasa_names"] = ("mikasa", "mikasa2")
    ar = SQ.flyer("armin", "cadet", "blond", H=1.63); co = SQ.flyer("connie", "cadet", "grey"); je = SQ.flyer("jean", "cadet", "jean")
    sa = SQ.flyer("sasha", "cadet", "brown")
    stream = [ar, co, je, sa] + [SQ.flyer(f"c{k}", "cadet", rnd.choice(["dark", "brown", "ash", "black", "auburn", "blond"])) for k in range(18)]
    for k, f in enumerate(stream):
        lag = 1.3 + 0.18 * k + rnd.uniform(0, 0.4)
        off = np.array([rnd.uniform(-35, 35), 0.0])
        t_ = BEATS["stream"][0] + lag * 0.5
        prev = S3(-250 + off[0], 262 - 12 * k * 0.4, top_z(-250 + off[0], 262) + 6)
        f.stand(t_ - 0.01, t_, prev, yaw_n)
        ys = [300, 345, 392]
        for y in ys:
            q = roof_set(-250 + off[0] * (0.9 if f not in (ar, co) else 0.4) + rnd.uniform(-6, 6), y - 10 * (k % 3))
            f.hop(t_, t_ + 1.3, prev, q, apex=7); prev = q; t_ += 1.3
        if f in (ar, co):                                  # Armin and Connie break off and circle over MA
            for q_ in ((-246, 432) if f is ar else (-275, 438), (-247, 404) if f is ar else (-276, 396)):
                q = roof_set(*q_)
                f.hop(t_, t_ + 1.6, prev, q, apex=6).stand(t_ + 1.6, t_ + 2.4, q, yaw_at(q_, MA_LAND), "crouch"); prev = q; t_ += 2.4
            f.stand(t_, BEATS["rescue"][0], prev, yaw_at((-247, 404), MA_LAND), "crouch")
            continue
        for q_ in ((-232, 460), (-212, 520), (-196, 576)):  # on NE toward the HQ under Jean, stranded on the roofs there
            q = roof_set(q_[0] + rnd.uniform(-22, 22), q_[1] + rnd.uniform(-14, 14))
            f.hop(t_, t_ + 1.5, prev, q, apex=7); prev = q; t_ += 1.5
        f.stand(t_, DUR, prev, yaw_at((prev[0], prev[1] + 870), HQ), rnd.choice(["crouch", "stand"]))
    # the rescue: Armin dives into MA and takes Mikasa to roof R; Connie follows; the three on the ridge
    r0, r1 = BEATS["rescue"]
    a_pick = watch + np.array([1.2, 0.0, 0.0])
    ridge = S3(ROOF_R[0], ROOF_R[1], ROOF_R[2] + 0.05)
    ar.hop(r0, r0 + 0.8, ar.end_pos(), a_pick, apex=4)
    ar.hop(r0 + 1.2, r1, a_pick, ridge + np.array([1.2, -0.6, 0.0]), apex=9)
    ar.stand(r1, DUR, ridge + np.array([1.2, -0.6, 0.0]), heading_yaw(110.0), "stand")
    carry = lambda t: SQ.by_name["armin"].state(t)["pos"] + np.array([-0.7, 0.2, 0.3])
    mk2.follow(r0 + 1.2, r1, carry, pose="flail")
    mk2.stand(r1, DUR, ridge, heading_yaw(110.0), "kneel")
    co.hop(r0 + 0.6, r1 + 0.6, co.end_pos(), ridge + np.array([-1.4, 0.8, 0.0]), apex=9)
    co.stand(r1 + 0.6, DUR, ridge + np.array([-1.4, 0.8, 0.0]), heading_yaw(110.0), "stand")
    SQ.build(coll)
    if getattr(SQ, "wob", None) is not None:                       # thin LIGHT grey wires (owner QA 10/27)
        for m in SQ.wob.data.materials:
            b_ = m.node_tree.nodes.get("Principled BSDF") if m and m.use_nodes else None
            if b_:
                b_.inputs["Base Color"].default_value = (0.62, 0.62, 0.60, 1.0)
    say(f"flyers: {len(SQ.flyers)}")

# ====================================================================== the evacuation crowd (5,500 minimal figures)
SHIRTS_V2 = ["#d1495b", "#edae49", "#1d8a99", "#3e6fb0", "#6a994e", "#f28f3b", "#8e5ea2", "#e07a5f", "#3d9970", "#c8553d",
             "#f4d35e", "#5aa9e6", "#b5468a", "#e9e2d0", "#9bc53d", "#ff8c69"]
EARTH = ["#7a5a42", "#a89070", "#8a6a4a", "#6e6250", "#9a8468", "#5e5446", "#b8a688", "#7a6a56"]
def _mute(h, e, k=0.38):
    a = [int(h[q:q + 2], 16) for q in (1, 3, 5)]; b = [int(e[q:q + 2], 16) for q in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(int(round(x + (y - x) * k)) for x, y in zip(a, b))
SHIRTS_DUSTY = [_mute(h, EARTH[n % len(EARTH)]) for n, h in enumerate(SHIRTS_V2)] + EARTH[:6]   # muted colours + plain earth cloth
PANTS_DUSTY = ["#3e3a42", "#5c4632", "#4a4a3c", "#6b5440", "#3a3430", "#6a4038"]
SCARVES = ["#d8ccb0", "#b8924a", "#9a5a48", "#5a7a8e"]
HAIRS_C = ["#1c1814", "#3a2a1e", "#6a4a2a", "#8a6a3a", "#5a3a28", "#8a8a84"]
SKINS_C = ["#d8a888", "#c49474", "#a87a5a"]

def _crowd_slots(rng):
    """Jam slots in E (hex grid 0.72 m, density tight at the arch -> looser at the rear), minus the cart / gap / corpse."""
    x0, x1, y0, y1 = E_BOX
    a = 0.72
    pts = []
    ys = np.arange(y0 + 0.6, y1 - 0.4, a * 0.866)
    for r, y in enumerate(ys):
        for x in np.arange(x0 + 0.5 + (r % 2) * a / 2, x1 - 0.4, a):
            pts.append((x, y))
    P = np.array(pts) + rng.normal(0, 0.12, (len(pts), 2))
    TR = STATE["TR"]
    ok = np.array([TR.walkable_m(float(x), float(y)) and abs(TR.ground_z_m(float(x), float(y))) < 1.6 for x, y in P])
    P = P[ok]
    d = np.hypot(P[:, 0] - ARCH[0], P[:, 1] - ARCH[1])
    dens = 0.87 * np.clip(2.2 - 1.15 * (d / 70.0), 0.85, 2.2) / 2.2
    dens *= np.clip(1.2 - d / 35.0, 0.1, 1.0)               # owner 10/27: far fewer people at the rear (packed only at the arch)
    keep = rng.random(len(P)) < dens
    P = P[keep]
    # exclusions: cart (start) + merchant gap behind it, cart end footprint east of the arch, corpse + its approach
    def outside_rect(P, c, yaw_deg, hx, hy0, hy1, m=0.8):
        yaw = math.radians(-yaw_deg)
        cs, sn = math.cos(yaw), math.sin(yaw)
        dx, dy = P[:, 0] - c[0], P[:, 1] - c[1]
        lx = cs * dx + sn * dy; ly = -sn * dx + cs * dy
        return ~((np.abs(lx) < hx + m) & (ly > hy0 - m) & (ly < hy1 + m))
    m = outside_rect(P, CART_START[0], CART_START[1], 2.7, -3.0, 9.0)
    m &= ~((np.abs(P[:, 0] - MERCHANT[0]) < 5.2) & (P[:, 1] > 843.6))          # the 4-6 m gap behind the cart (rear ~848.8)
    m &= np.hypot(P[:, 0] - (-100.0), P[:, 1] - 798.0) > 7.0
    m &= ~((P[:, 0] > -133) & (P[:, 1] > 848.6))                               # the east-wing ledge
    return P[m]

def build_crowd(coll):
    import swarm845 as SW
    L = STATE["L"]
    rng = np.random.default_rng(846); rnd = random.Random(846)
    J = _crowd_slots(rng)
    nj = len(J)
    # AV tail (300 on the last ~100 m of AV) and EVS stragglers (50), arriving along their streets
    AVt = [(-60.0, 470.0), (-128.0, 735.0), (-153.0, 803.0)]
    S_av = poly_len(AVt)
    tail, tail_path = [], []
    while len(tail) < 90:                                          # owner 10/27: thin rear (was 300)
        s = S_av[-1] - rng.uniform(3.0, 95.0)
        c = poly_at(AVt, S_av, s); q = poly_at(AVt, S_av, s + 1.0) - c; q /= np.linalg.norm(q)
        p = c + np.array([-q[1], q[0]]) * rng.uniform(-5.5, 5.5)
        if STATE["TR"].walkable_m(float(p[0]), float(p[1])):
            tail.append(p); tail_path.append((0, s))
    evs, evs_path = [], []
    E_P = [EVS[0], EVS[1]]; S_e = poly_len(E_P)
    while len(evs) < 20:
        s = S_e[-1] - rng.uniform(6.0, 24.0)
        c = poly_at(E_P, S_e, s); q = np.array([-0.707, 0.707])
        p = c + np.array([-q[1], q[0]]) * rng.uniform(-4.0, 4.0)
        if np.hypot(p[0] + 100.0, p[1] - 798.0) > 7.5:
            evs.append(p); evs_path.append((1, s))
    slots = np.vstack([J, np.array(tail), np.array(evs)])
    n = len(slots)
    kind = np.array([0] * nj + [1] * len(tail) + [2] * len(evs))
    # arrival (tail / stragglers): walk in along their street, arrive at t_arr
    t_arr = np.full(n, -1e9); s_slot = np.zeros(n); vwalk = rng.uniform(3.2, 4.6, n); src = np.zeros(n, np.int32)
    for i in range(nj, n):
        if kind[i] == 1:
            k = i - nj
            src[i] = 0; s_slot[i] = tail_path[k][1]; t_arr[i] = rng.uniform(6.0, 30.0)
        else:
            k = i - nj - len(tail)
            src[i] = 1; s_slot[i] = evs_path[k][1]; t_arr[i] = rng.uniform(8.0, 23.5)
    # specials: merchant, 3 guards, 4 pushers
    spec = [("merchant", MERCHANT), ("guard", (-142.6, 845.6)), ("guard", (-137.4, 845.4)), ("guard", (-141.4, 844.2)),
            ("pusher", None), ("pusher", None), ("pusher", None), ("pusher", None)]
    ns = len(spec)
    STATE["crowd"] = dict(slots=slots, n=n, kind=kind, t_arr=t_arr, s_slot=s_slot, vwalk=vwalk, src=src,
                          paths=[(np.array(AVt), S_av), (np.array(E_P), S_e)], ns=ns, spec=spec)
    # geometry (minimal swarm845 figures, true scale ~1.65 m, dusty colourful palette)
    g = SW.Geo(); fm = []
    hg = np.clip(rng.normal(1.66, 0.07, n + ns), 1.45, 1.85)
    hg[rng.random(n + ns) < 0.06] = rng.uniform(1.05, 1.3)          # a few children
    nsh, npa, nsk, nha, nsc = len(SHIRTS_DUSTY), len(PANTS_DUSTY), len(SKINS_C), len(HAIRS_C), len(SCARVES)
    o_pa, o_sk, o_ha, o_sc = nsh, nsh + npa, nsh + npa + nsk, nsh + npa + nsk + nha
    o_x = o_sc + nsc                                                     # specials: merchant coat, guard navy, bald
    for i in range(n + ns):
        n0 = len(g.fc)
        dress = rnd.random() < 0.35
        SW.person_geo(g, i, hg[i], dress, rnd)
        if i < n:
            hair = o_sc + rnd.randrange(nsc) if rnd.random() < 0.12 else o_ha + rnd.randrange(nha)
            base = [rnd.randrange(nsh), o_pa + rnd.randrange(npa), o_sk + rnd.randrange(nsk), hair]
        else:
            k = spec[i - n][0]
            if k == "merchant":
                base = [o_x, o_x, o_sk, o_sk]
            elif k == "guard":
                base = [o_x + 1, o_x + 1, o_sk + 1, o_ha]
            else:
                base = [rnd.randrange(nsh), o_pa, o_sk + 2, o_ha + 1]
        fm += [base[c] for c in g.fc[n0:]]
    mats = [L.mat(f"G5_shirt{i}", hexrgb(c), 0.85) for i, c in enumerate(SHIRTS_DUSTY)] + \
           [L.mat(f"G5_pants{i}", hexrgb(c), 0.9) for i, c in enumerate(PANTS_DUSTY)] + \
           [L.mat(f"G5_skin{i}", hexrgb(c), 0.6) for i, c in enumerate(SKINS_C)] + \
           [L.mat(f"G5_hair{i}", hexrgb(c), 0.7) for i, c in enumerate(HAIRS_C)] + \
           [L.mat(f"G5_scarf{i}", hexrgb(c), 0.9) for i, c in enumerate(SCARVES)] + \
           [L.mat("G5_merchant", hexrgb("#5a3a2a"), 0.8), L.mat("G5_guard", hexrgb("#2e3440"), 0.8)]
    R = g.finish()
    ob = SW._mesh("G5_EvacMass", R, g.f, fm, mats, coll)
    ob.visible_shadow = True
    STATE["crowd"].update(R=R, ob=ob, hg=hg)
    # per-person drain geometry
    rel = slots - np.array(ARCH); d0 = np.maximum(np.hypot(rel[:, 0], rel[:, 1]), 0.3)
    STATE["crowd"].update(rel=rel, d0=d0, dirv=rel / d0[:, None], phase0=rng.uniform(0, math.tau, n))
    say(f"crowd: {nj} in E + {len(tail)} AV tail + {len(evs)} EVS = {n} (+{ns} merchant group / pushers)")

def _cart_frame(t):
    """Cart root (load centre) M xy + compass yaw at t (mirrors trost.set_cart's back-out-then-swing)."""
    f = ss(*BEATS["cart"], t)
    (p0, y0), (p1, y1) = CART_START, CART_END
    p = np.array(p0) + (np.array(p1) - np.array(p0)) * f
    yaw = y0 + ((y1 - 360.0) - y0) * (0.0 if f < 0.35 else (f - 0.35) / 0.65)
    return p, yaw, f

def _cart_local(t, lx, ly):
    p, yaw, _ = _cart_frame(t)
    a = math.radians(-yaw)                     # compass -> ccw
    c, s = math.cos(a), math.sin(a)
    return np.array([p[0] + c * lx - s * ly, p[1] + s * lx + c * ly]), math.radians(-yaw)

def crowd_state(t):
    C = STATE["crowd"]
    n = C["n"]
    slots = C["slots"].copy()
    yaw = np.full(n, yaw_to(0.0, 1.0)); moving = np.zeros(n); vis = np.ones(n)
    # arrival along the streets (tail / stragglers)
    late = t < C["t_arr"]
    if late.any():
        idx = np.where(late)[0]
        for src in (0, 1):
            ii = idx[C["src"][idx] == src]
            if not len(ii):
                continue
            Pp, Sp = C["paths"][src]
            s = C["s_slot"][ii] - C["vwalk"][ii] * (C["t_arr"][ii] - t)
            for i, si in zip(ii, s):
                if si < 0:
                    vis[i] = 0.0; continue
                c = poly_at(Pp, Sp, si); c2 = poly_at(Pp, Sp, si + 1.0); q = c2 - c; q /= max(np.linalg.norm(q), 1e-6)
                lat = (C["slots"][i] - poly_at(Pp, Sp, C["s_slot"][i])) @ np.array([-q[1], q[0]])
                slots[i] = c + np.array([-q[1], q[0]]) * lat
                yaw[i] = yaw_to(q[0], q[1]); moving[i] = 1.0
    jam = ~late
    # jam facing: toward the arch, small jitter
    d = np.array(ARCH) - slots
    yaw[jam] = np.arctan2(-d[jam, 0], d[jam, 1]) + 0.25 * np.sin(C["phase0"][jam] + 0.3 * t)
    # recoil from the falling Abnormal (rear edge steps back ~3 m)
    rc = ss(BEATS["kill"] + 0.1, BEATS["kill"] + 0.7, t)
    if rc > 0:
        dv = slots - np.array([-100.0, 797.0]); dist = np.maximum(np.hypot(dv[:, 0], dv[:, 1]), 1e-3)
        w = np.clip(1.0 - (dist - 7.0) / 18.0, 0.0, 1.0) * rc * jam
        slots += dv / dist[:, None] * (3.0 * w)[:, None]
    # Mikasa's landing + the lane to the merchant (people part, then stay parted)
    ln = ss(BEATS["hop"][1] - 0.3, BEATS["lane"][0] + 0.3, t)
    if ln > 0:
        a = np.array(MIK_LAND); b = np.array(MIK_FACE); ab = b - a; L2 = ab @ ab
        u = np.clip(((slots - a) @ ab) / L2, -0.3, 1.0)
        cpt = a + u[:, None] * ab; dv = slots - cpt; dist = np.maximum(np.hypot(dv[:, 0], dv[:, 1]), 1e-3)
        push = np.clip(1.9 - dist, 0.0, None) * ln
        slots += dv / dist[:, None] * push[:, None]
    # the cart backing out / swinging: push people out of its footprint
    cf = _cart_frame(t)
    if 0.0 < cf[2] < 1.0 or t > BEATS["cart"][1]:
        p, yawc, _ = cf
        a_ = math.radians(-yawc); cs, sn = math.cos(a_), math.sin(a_)
        dv = slots - p; lx = cs * dv[:, 0] + sn * dv[:, 1]; ly = -sn * dv[:, 0] + cs * dv[:, 1]
        hx, y0_, y1_ = 3.2, -3.4, 7.2
        inside = (np.abs(lx) < hx) & (ly > y0_) & (ly < y1_)
        if inside.any():
            ex = hx - np.abs(lx); e0 = ly - y0_; e1 = y1_ - ly
            m = np.argmin(np.stack([ex, e0, e1], 1), 1)
            lx2 = np.where(m == 0, np.sign(lx) * hx, lx); ly2 = np.where(m == 1, y0_, np.where(m == 2, y1_, ly))
            nx = p[0] + cs * lx2 - sn * ly2; ny = p[1] + sn * lx2 + cs * ly2
            slots[inside, 0] = nx[inside]; slots[inside, 1] = ny[inside]
    # the drain: the arch sucks the crowd in, the disk around the mouth is consumed from the arch outward
    td = t - BEATS["drain"]
    if td > 0:
        rel = slots - np.array(ARCH); d0 = np.maximum(np.hypot(rel[:, 0], rel[:, 1]), 0.3); dirv = rel / d0[:, None]
        tau = td - d0 / C_WAVE
        R = drain_R(tau); sp = drain_speed(tau)
        dd = d0 - R
        act = (R > 0) & jam
        pos = np.array(ARCH) + dirv * np.maximum(dd, 0.0)[:, None]
        sq = np.clip(dd / 9.0, 0.25, 1.0)
        pos[:, 0] = ARCH[0] + (pos[:, 0] - ARCH[0]) * sq
        inn = dd <= 0
        pos[inn, 0] = ARCH[0] + np.clip(rel[inn, 0] * 0.06, -1.8, 1.8)
        pos[inn, 1] = ARCH[1] - dd[inn]
        slots[act] = pos[act]
        vis[act & (pos[:, 1] > 868.0)] = 0.0
        mv = act & (sp > 0.3)
        yaw[mv] = np.arctan2(dirv[mv, 0], -dirv[mv, 1])
        yaw[mv & inn] = 0.0
        moving[mv] = 1.0
        C["_walk"] = R
    return slots, yaw, moving, vis

def update_crowd(t):
    import swarm845 as SW
    C = STATE["crowd"]
    n, ns = C["n"], C["ns"]
    pos2, yaw, moving, vis = crowd_state(t)
    N = n + ns
    pos = np.zeros((N, 3)); yw = np.zeros(N); vv = np.ones(N); mv = np.zeros(N)
    pos[:n, :2] = pos2; yw[:n] = yaw; vv[:n] = vis; mv[:n] = moving
    pos[:n, 2] = 0.06
    # specials: merchant + guards in the gap (facing the crowd), the shove, then with the cart; pushers at the wheels
    cart_on = t >= BEATS["cart"][0] - 0.3
    for k, (kind, p) in enumerate(C["spec"]):
        i = n + k
        if kind == "pusher":
            lx, ly = ((-3.0, -1.4), (3.0, -1.4), (-1.4, -3.6), (1.4, -3.6))[k - 4]
            q, a = _cart_local(t, lx, ly)
            pos[i, :2] = q; yw[i] = a + (math.pi if ly > -2 else 0.0)
            mv[i] = 1.0 if BEATS["cart"][0] <= t < BEATS["cart"][1] else 0.0
            continue
        q = np.array(p, float); yy = yaw_to(0.0, -1.0)
        if kind == "guard" and k == 3:                                  # the bodyguard shoved by Mikasa
            u = ss(BEATS["shove"], BEATS["shove"] + 0.45, t)
            q = q + np.array([-1.3, 0.2]) * u
        if cart_on and kind != "pusher":
            lx, ly = ((-3.6, -4.4), (3.4, -4.6), (2.6, -5.6), (-2.2, -5.8))[k]
            qc, a = _cart_local(t, lx, ly)
            u = ss(BEATS["cart"][0] - 0.3, BEATS["cart"][0] + 0.6, t)
            q = q * (1 - u) + qc * u
            yy = a + math.pi * 0.0 if u > 0.5 else yy
        pos[i, :2] = q; yw[i] = yy
    for i in range(n, N):
        pos[i, 2] = G(pos[i, 0], pos[i, 1]) + 0.06
    pos[:, 1] -= segtime.SET_OFF_Y
    hg = C["hg"]
    ph = C["phase0"] if "phase0" in C else np.zeros(n)
    phase = np.zeros(N); phase[:n] = ph + 2 * math.pi * 1.9 * t
    phase[n:] = 2 * math.pi * 1.6 * t
    Ar = np.zeros((N, 7)); Ae = np.zeros((N, 7)); lean = np.zeros(N)
    s = np.sin(phase) * 0.7 * mv
    Ar[:, 1] = s; Ar[:, 2] = -s; Ar[:, 3] = -0.8 * s; Ar[:, 4] = 0.8 * s
    lean[:] = -0.15 * mv
    # arms raised at the load / pressing (jam, before the cart moves)
    if t < BEATS["cart"][0] + 0.5:
        near = np.hypot(pos2[:, 0] - ARCH[0], pos2[:, 1] - 846.0) < 9.0
        jam_i = np.where(near & (mv[:n] < 0.5))[0]
        Ar[jam_i, 3] = 2.4 + 0.3 * np.sin(t * 3 + jam_i); Ar[jam_i, 4] = 2.6 + 0.3 * np.cos(t * 2.7 + jam_i)
    # the shoved bodyguard falls sideways
    i3 = n + 3
    u = ss(BEATS["shove"], BEATS["shove"] + 0.45, t)
    lean[i3] = -1.35 * u; yw[i3] += 1.2 * u
    # pushers lean into the wheels
    for i in range(n + 4, N):
        lean[i] = -0.45
    co = SW._deform(C["R"], Ar, Ae, lean, vv, yw, pos)
    ob = C["ob"]
    ob.data.vertices.foreach_set("co", co.astype(np.float32).ravel()); ob.data.update()

# ====================================================================== FX: cards (steam, dust, smoke, fire, glow)
def build_cards(coll):
    import smokecards as SC
    rng = np.random.default_rng(55)
    C = SC.SmokeCards("G5Cards")
    _am = C.add_many
    def _add_many(te, pos, vel=None, *a, **k):
        if k.get("kind") == "steam":
            c = k.get("color")
            base = np.array([0.92, 0.92, 0.90]) if c is None else np.asarray(c, float)
            k["color"] = base * np.array(STEAM_WARM)
        return _am(te, pos, vel, *a, **k)
    C.add_many = _add_many
    TT = STATE["TT"]
    kick = BEATS["kick"]
    # ---- Colossal: embers (orange points drifting up around the head / over the gatehouse)
    n = 160
    C.add_many(rng.uniform(-2.0, 10.0, n), S3(0, -8, 45)[None, :] + np.column_stack([rng.normal(0, 18, n), rng.normal(0, 10, n), rng.uniform(-5, 20, n)]),
               np.column_stack([rng.normal(1.5, 1.5, n), rng.normal(0.5, 1.5, n), rng.uniform(2.0, 5.0, n)]), r0=0.9, r1=0.6,
               life=rng.uniform(3.0, 6.0, n), rise=0.5, kind="glow", alpha=0.9, color=hexrgb("#ff9a3c"), fade_in=0.3)
    n = 70
    C.add_many(rng.uniform(10.0, 40.0, n), S3(0, 25, 4)[None, :] + np.column_stack([rng.normal(0, 30, n), rng.normal(0, 20, n), rng.uniform(0, 15, n)]),
               np.column_stack([rng.normal(1.5, 1.0, n), rng.normal(0.5, 1.0, n), rng.uniform(1.0, 3.0, n)]), r0=0.8, r1=0.5,
               life=rng.uniform(3.0, 5.0, n), rise=0.3, kind="glow", alpha=0.8, color=hexrgb("#ff8a30"), fade_in=0.3)
    # ---- steam rising off the skull (20-40 m above the head), continuously spawned billows
    ts = np.arange(0.3, BEATS["steam_burst"] + 0.3, 0.09); n = len(ts)
    C.add_many(ts, S3(0, -20, 58)[None, :] + np.column_stack([rng.normal(0, 9, n), rng.normal(0, 4, n), rng.uniform(-2, 4, n)]),
               np.column_stack([rng.normal(0, 1.5, n) - 1.5, rng.normal(-1.5, 1.5, n), rng.uniform(5, 9, n)]), r0=4.0, r1=rng.uniform(9, 14, n),
               life=rng.uniform(3.0, 4.5, n), rise=4.0, kind="steam", alpha=0.42, tau=1.5)
    # ---- the kick: sepia shock ring (60 m/s to r ~120), dust column, dust sheet on the wall top, smoke out of the hole
    n = 64; a = rng.uniform(-0.15, math.pi + 0.15, n); sp = rng.uniform(52, 66, n)
    C.add_many(kick + rng.random(n) * 0.12, S3(0, 12, 3)[None, :] + np.column_stack([np.cos(a) * 4, np.sin(a) * 4, rng.uniform(0, 3, n)]),
               np.column_stack([np.cos(a) * sp, np.sin(a) * sp, rng.uniform(0, 3, n)]), r0=6.0, r1=rng.uniform(18, 26, n),
               life=rng.uniform(4.0, 6.0, n), rise=1.5, kind="steam", alpha=0.85, tau=1.6, color=hexrgb("#b8a27c"))
    n = 70
    C.add_many(kick + rng.random(n) * 0.8, S3(0, 10, 8)[None, :] + rng.normal(0, 5, (n, 3)),
               np.column_stack([rng.normal(0, 5, n), rng.normal(4, 5, n), rng.uniform(16, 34, n)]), r0=8.0, r1=rng.uniform(20, 32, n),
               life=rng.uniform(6.0, 9.0, n), rise=5.0, kind="steam", alpha=0.85, tau=2.2, color=hexrgb("#b5a080"))
    n = 40; xs = rng.uniform(-8, 8, n); sg = np.sign(xs)
    C.add_many(kick + 0.15 + rng.random(n) * 0.4, np.column_stack([xs, np.full(n, -870.0 + 1.0), rng.uniform(51, 56, n)]),
               np.column_stack([sg * rng.uniform(16, 30, n), rng.normal(0, 2, n), rng.uniform(0, 3, n)]), r0=2.5, r1=rng.uniform(6, 9, n),
               life=rng.uniform(2.0, 3.0, n), rise=0.5, kind="dust", alpha=0.6, tau=1.2, color=hexrgb("#b8a684"))
    ts = np.arange(kick + 0.8, 26.0, 0.2); n = len(ts)
    C.add_many(ts, S3(0, 9, 6)[None, :] + rng.normal(0, 2.5, (n, 3)), np.column_stack([rng.normal(0, 1.5, n), rng.uniform(2, 5, n), rng.uniform(4, 8, n)]),
               r0=3.0, r1=rng.uniform(8, 12, n), life=rng.uniform(4, 6, n), rise=2.5, kind="smoke", alpha=0.32, tau=2.0, color=hexrgb("#b8b2a8"))
    # crater wisps (twisting, 15-20 m)
    for cx, cy in (CRW, CRE):
        ts = np.arange(kick + 0.6, DUR, 0.32); n = len(ts)
        C.add_many(ts, S3(cx, cy, -0.5)[None, :] + rng.normal(0, 0.8, (n, 3)),
                   np.column_stack([np.sin(ts * 1.7) * 1.2, np.cos(ts * 1.3) * 1.2, rng.uniform(3.0, 4.5, n)]), r0=1.0, r1=rng.uniform(2.6, 3.6, n),
                   life=rng.uniform(3.6, 4.6, n), rise=1.0, kind="steam", alpha=0.5, tau=0.0)
    # ---- the steam explosion (9.0): 100 m tall, 120 m wide outside the wall in 3 s, spills over, thins by 25
    te = BEATS["steam_burst"]
    n = 420
    tt = te + rng.random(n) ** 1.6 * 2.6                                   # dense at 9.0, tailing off by ~11.6
    th = rng.uniform(0, math.tau, n); el = rng.uniform(0.05, 1.2, n); spd = rng.uniform(12, 34, n)
    dirs = np.column_stack([np.cos(th) * np.cos(el), np.sin(th) * np.cos(el) * 0.8, np.sin(el)])
    C.add_many(tt, S3(0, -15, 48)[None, :] + rng.normal(0, 5, (n, 3)), dirs * spd[:, None] + np.array([0, 0, 9.0]),
               r0=4.0, r1=rng.uniform(11, 19, n), life=rng.uniform(3.4, 4.6, n), rise=4.0, kind="steam", alpha=0.5, tau=1.4,
               color=hexrgb("#f7f3ec"))
    n = 60
    C.add_many(te + 0.4 + rng.random(n) * 2.0, np.column_stack([rng.uniform(-45, 45, n), np.full(n, -870.0 - 3.0), rng.uniform(49, 58, n)]),
               np.column_stack([rng.normal(0, 3, n), rng.uniform(5, 10, n), rng.uniform(3, 8, n)]), r0=3.0, r1=rng.uniform(9, 14, n),
               life=rng.uniform(3.2, 4.2, n), rise=2.5, kind="steam", alpha=0.45, tau=1.5, color=hexrgb("#f4efe6"))
    # ---- debris landing puffs (filled in by build_debris) + sweep dust
    for (tl, p, big) in STATE.get("landings", []):
        m = 6 if big else 2
        C.add_many(tl + rng.random(m) * 0.1, np.tile(p, (m, 1)) + rng.normal(0, 1.0, (m, 3)),
                   np.column_stack([rng.normal(0, 4, m), rng.normal(0, 4, m), rng.uniform(1, 4, m)]), r0=1.5, r1=(rng.uniform(4, 7, m) if big else rng.uniform(2.5, 3.5, m)),
                   life=rng.uniform(1.5, 2.6, m), rise=1.0, kind="dust", alpha=0.6, tau=0.6, color=hexrgb("#a8987c"))
    ts = np.arange(BEATS["sweep"][0], BEATS["sweep"][1], 0.05); n = len(ts)
    P_ = np.array([S3(sweep_hand(t)) for t in ts]) + rng.normal(0, 2, (n, 3))
    C.add_many(ts, P_, np.column_stack([rng.uniform(-14, -6, n), rng.normal(2, 3, n), rng.uniform(1, 5, n)]), r0=2.5, r1=rng.uniform(6, 10, n),
               life=rng.uniform(1.8, 2.8, n), rise=1.5, kind="dust", alpha=0.6, tau=1.0, color=hexrgb("#c0a07c"))
    # ---- smoke columns: 13 thin twisting columns from t 14, one by one (dark at the source -> pale above)
    for k, (x, y) in enumerate(SMOKE_SITES):
        t0 = BEATS["smoke"] + 0.9 * k
        base = S3(x, y, top_z(x, y) + 1.0)
        ts = np.arange(t0, DUR, 0.16); n = len(ts)
        lean = WIND * (0.8 + 0.4 * rng.random())
        C.add_many(ts, base[None, :] + rng.normal(0, 1.2, (n, 3)),
                   np.column_stack([np.sin(ts * 0.9 + k) * 1.2, np.cos(ts * 0.7 + k) * 1.2, rng.uniform(8, 11, n)]) + lean * 0.5,
                   r0=3.0, r1=rng.uniform(7.0, 10.0, n), life=rng.uniform(4.5, 5.5, n), rise=1.0, kind="smoke", alpha=1.0, tau=0.0,
                   color=hexrgb("#33312f"))
        ts = np.arange(t0 + 0.5, DUR, 0.14); n = len(ts)
        C.add_many(ts, base[None, :] + np.array([0, 0, 6.0]) + rng.normal(0, 1.5, (n, 3)),
                   np.column_stack([np.sin(ts * 0.8 + k) * 1.6, np.cos(ts * 0.6 + k) * 1.6, rng.uniform(9, 12, n)]) + lean * 0.9,
                   r0=5.0, r1=rng.uniform(13, 19, n), life=rng.uniform(12.0, 15.0, n), rise=1.0, kind="smoke", alpha=0.9, tau=0.0,
                   color=hexrgb("#6e6a64"))
        # ground fire at the source
        ts = np.arange(t0, DUR, 0.12); n = len(ts)
        C.add_many(ts, base[None, :] + rng.normal(0, 1.2, (n, 3)), np.column_stack([rng.normal(0, 0.5, n), rng.normal(0, 0.5, n), rng.uniform(3, 6, n)]),
                   r0=1.4, r1=rng.uniform(2.2, 3.4, n), life=rng.uniform(0.6, 1.0, n), rise=1.0, kind="fire", alpha=0.9, color=hexrgb("#ff8a2a"))
    # ---- wall-top grapeshot from 10.5: muzzle flash + white puff, tan spurts on the GS grass
    for te, mz, hit in STATE["cannon_events"]:
        C.add_many([te], [mz], None, r0=2.2, r1=2.8, life=0.14, rise=0.0, kind="glow", alpha=1.0, color=hexrgb("#ffb347"), fade_in=0.005)
        C.add_many(te + rng.random(4) * 0.08, np.tile(mz, (4, 1)) + rng.normal(0, 0.8, (4, 3)),
                   np.column_stack([rng.normal(0, 2, 4), rng.normal(4, 2, 4), rng.uniform(1, 3, 4)]), r0=1.2, r1=rng.uniform(4.5, 6.5, 4),
                   life=rng.uniform(2.4, 3.4, 4), rise=1.0, kind="steam", alpha=0.75, tau=0.8, color=hexrgb("#e6e2da"))
        m = 5
        C.add_many(te + 0.25 + rng.random(m) * 0.15, np.tile(hit, (m, 1)) + np.column_stack([rng.normal(0, 4, m), rng.normal(0, 4, m), np.zeros(m)]),
                   np.column_stack([rng.normal(0, 2, m), rng.normal(0, 2, m), rng.uniform(4, 8, m)]), r0=0.8, r1=rng.uniform(2.5, 3.5, m),
                   life=rng.uniform(1.0, 1.6, m), rise=0.5, kind="dust", alpha=0.65, tau=0.5, color=hexrgb("#b09a72"))
    # ---- blade streaks + kill steam (vanguard, Mikasa, TR1), corpse steam columns (5-15 m, to the end)
    cuts = [(te, TT.nape(nm, te - 0.05)) for nm, te in STATE["vkills"]]
    cuts += [(BEATS["kill"], TT.nape("AB", BEATS["kill"] - 0.05)), (BEATS["tr1_kill"], TT.nape("TR1", BEATS["tr1_kill"] - 0.05))]
    for te, p in cuts:
        C.add_many(te + np.array([0.0, 0.05]), np.tile(p, (2, 1)), None, r0=1.6, r1=1.8, life=0.16, rise=0.0, kind="glow", alpha=1.0,
                   color=hexrgb("#cfe8ff"), dirs=np.array([[1.0, 0.4, 0.6], [1.0, -0.5, 0.3]]), stretch=4.0, fade_in=0.01)
        C.add_many(te + 0.1 + rng.random(10) * 0.5, np.tile(p, (10, 1)) + rng.normal(0, 1, (10, 3)),
                   np.column_stack([rng.normal(0, 2, 10), rng.normal(0, 2, 10), rng.uniform(2, 5, 10)]), r0=1.0, r1=3.5, life=2.0, rise=2.5,
                   kind="steam", alpha=0.7, tau=0.5)
    corpses = [(nm, te) for nm, te in STATE["vkills"]] + [("AB", BEATS["skid"][1]), ("TR1", BEATS["tr1_kill"] + 0.6), ("BT", BEATS["bt_torn"] + 0.4),
                                                          ("CAP", BEATS["stomps"][-1]), ("LH", BEATS["lh_stamp"]), ("CC", BEATS["nape_stamp"])]
    for nm, te in corpses:
        H = TT.H[TT.j(nm)]
        ts = np.arange(te + 0.5, DUR, 0.16 if nm in ("AB", "BT") else 0.24); n = len(ts)
        if not n:
            continue
        P_ = np.array([TT.pos(nm, min(t, te + 1.0)) for t in ts]) + np.column_stack([rng.normal(0, 0.18 * H, n), rng.normal(0, 0.18 * H, n), rng.uniform(0.5, 2.0, n)])
        C.add_many(ts, P_, np.column_stack([rng.normal(0, 0.8, n), rng.normal(0, 0.8, n), rng.uniform(3.5, 6.0, n)]), r0=0.12 * H,
                   r1=rng.uniform(0.35, 0.5, n) * H, life=rng.uniform(2.2, 3.4, n), rise=2.0, kind="steam", alpha=0.6, tau=0.6)
    # ---- the Abnormal's dust cloud (as tall as itself) + the fall / skid burst
    ts = np.arange(BEATS["ab_run"][0] + 0.5, BEATS["kill"], 0.07); n = len(ts)
    P_ = np.array([TT.pos("AB", t) for t in ts]); V_ = np.array([TT.pos("AB", t + 0.1) - TT.pos("AB", t) for t in ts]) / 0.1
    C.add_many(ts, P_ + np.column_stack([rng.normal(0, 2.5, n), rng.normal(0, 2.5, n), rng.uniform(0.5, 3.0, n)]),
               -V_ * 0.15 + np.column_stack([rng.normal(0, 2.5, n), rng.normal(0, 2.5, n), rng.uniform(2.5, 5.0, n)]), r0=3.0, r1=rng.uniform(8.0, 11.0, n),
               life=rng.uniform(2.6, 3.6, n), rise=3.0, kind="steam", alpha=0.8, tau=1.0, color=hexrgb("#a89070"))
    n = 50; c = S3(AB_CORPSE[0], AB_CORPSE[1], 2.0)
    C.add_many(BEATS["kill"] + 0.3 + rng.random(n) * 0.6, np.tile(c, (n, 1)) + rng.normal(0, 4, (n, 3)),
               np.column_stack([rng.normal(0, 9, n), rng.normal(0, 9, n), rng.uniform(1, 6, n)]), r0=3.0, r1=rng.uniform(7, 11, n),
               life=rng.uniform(2.5, 4.0, n), rise=1.5, kind="steam", alpha=0.8, tau=0.8, color=hexrgb("#a89070"))
    # ---- AT emergence (54.5): 25 m steam burst + green core; punch dust ring + chips; stomp puffs + geysers; tower burst cloud
    te = BEATS["bt_torn"]; c = S3(BT_POS[0], BT_POS[1], 6.0); n = 60
    C.add_many(te + rng.random(n) * 0.4, np.tile(c, (n, 1)) + rng.normal(0, 2.0, (n, 3)),
               np.column_stack([rng.normal(0, 9, n), rng.normal(0, 9, n), rng.uniform(5, 14, n)]), r0=3.0, r1=rng.uniform(8, 12, n),
               life=rng.uniform(2.5, 4.0, n), rise=4.0, kind="steam", alpha=0.85, tau=0.9)
    C.add_many([te + 0.02, te + 0.12], np.tile(c + np.array([0, 0, 3.0]), (2, 1)), None, r0=7.0, r1=9.0, life=0.3, rise=0.0, kind="glow", alpha=0.55,
               color=(0.35, 1.0, 0.45), fade_in=0.02)
    ts = np.arange(te + 0.3, 62.0, 0.12); n = len(ts)                    # AT body steam while he fights
    P_ = []
    for t in ts:
        st = at_state(t); p = st["pos"]
        P_.append(S3(p[0], p[1], G(*p) + st["z"] + rng.uniform(6, 13)) + np.array([rng.normal(0, 1.5), rng.normal(0, 1.5), 0]))
    C.add_many(ts, np.array(P_), np.column_stack([rng.normal(0, 1, n), rng.normal(0, 1, n), rng.uniform(2, 4, n)]), r0=1.2, r1=rng.uniform(3, 5, n),
               life=rng.uniform(1.6, 2.4, n), rise=3.0, kind="steam", alpha=0.35, tau=0.6)
    hit = S3(-261.0, 414.0, 7.0); n = 30
    C.add_many(BEATS["punch"] + rng.random(n) * 0.2, np.tile(hit, (n, 1)) + rng.normal(0, 1.5, (n, 3)),
               np.column_stack([rng.normal(0, 8, n), rng.normal(0, 8, n), rng.uniform(1, 6, n)]), r0=1.5, r1=rng.uniform(4, 6, n),
               life=rng.uniform(1.5, 2.5, n), rise=1.0, kind="dust", alpha=0.65, tau=0.6, color=hexrgb("#c8c0b0"))
    for ts_, nm in [(ts_, "CAP") for ts_ in BEATS["stomps"]] + [(BEATS["lh_stamp"], "LH"), (BEATS["nape_stamp"], "CC")]:
        q = TT.nape(nm, ts_ + 0.3); m = 14
        C.add_many(ts_ + rng.random(m) * 0.1, np.tile(q, (m, 1)) + rng.normal(0, 1.0, (m, 3)),
                   np.column_stack([rng.normal(0, 5, m), rng.normal(0, 5, m), rng.uniform(1, 3, m)]), r0=1.5, r1=rng.uniform(3.5, 5.5, m),
                   life=rng.uniform(1.2, 2.0, m), rise=0.8, kind="dust", alpha=0.6, tau=0.5, color=hexrgb("#9c8a72"))
        C.add_many(ts_ + 0.05 + rng.random(10) * 0.3, np.tile(q, (10, 1)) + rng.normal(0, 0.8, (10, 3)),
                   np.column_stack([rng.normal(0, 1, 10), rng.normal(0, 1, 10), rng.uniform(8, 14, 10)]), r0=1.0, r1=rng.uniform(3, 4.5, 10),
                   life=rng.uniform(1.8, 2.6, 10), rise=4.0, kind="steam", alpha=0.8, tau=0.7)
    tb = BEATS["slam"]; top = S3(TOWER[0], TOWER[1], 34.0); n = 44
    C.add_many(tb + rng.random(n) * 0.5, np.tile(top, (n, 1)) + rng.normal(0, 3, (n, 3)),
               np.column_stack([rng.normal(0, 7, n), rng.normal(0, 7, n), rng.uniform(-2, 6, n)]), r0=3.0, r1=rng.uniform(8, 13, n),
               life=rng.uniform(4.5, 6.5, n), rise=-0.5, kind="dust", alpha=0.75, tau=1.4, color=hexrgb("#bba987"))
    n = 16; base = S3(-222.0, 515.0, 6.0)
    C.add_many(BEATS["cc_slide"][0] + rng.random(n) * 0.8, np.tile(base, (n, 1)) + rng.normal(0, 2, (n, 3)),
               np.column_stack([rng.normal(0, 5, n), rng.normal(0, 5, n), rng.uniform(0, 3, n)]), r0=2.0, r1=rng.uniform(5, 8, n),
               life=rng.uniform(2.0, 3.0, n), rise=0.5, kind="dust", alpha=0.6, tau=0.6, color=hexrgb("#bba987"))
    q = S3(-265.8, 401.5, 4.0); n = 22                                  # CAP slammed against the W alley wall: chips + dust
    C.add_many(BEATS["punch"] + 0.42 + rng.random(n) * 0.15, np.tile(q, (n, 1)) + rng.normal(0, 1.2, (n, 3)),
               np.column_stack([rng.uniform(1, 6, n), rng.normal(0, 5, n), rng.uniform(0, 6, n)]), r0=1.0, r1=rng.uniform(3, 5, n),
               life=rng.uniform(1.2, 2.2, n), rise=0.5, kind="steam", alpha=0.8, tau=0.5, color=hexrgb("#c8c0b0"))
    # Mikasa's landing puff
    q = S3(MA_LAND[0], MA_LAND[1], 0.6); n = 8
    C.add_many(BEATS["fall"] + rng.random(n) * 0.1, np.tile(q, (n, 1)) + rng.normal(0, 0.4, (n, 3)),
               np.column_stack([rng.normal(0, 3, n), rng.normal(0, 3, n), rng.uniform(0.5, 1.5, n)]), r0=0.6, r1=1.8, life=1.4, rise=0.4,
               kind="dust", alpha=0.6, tau=0.4, color=hexrgb("#9c8a72"))
    # the smash run: a dust burst at every house he crashes through
    for tk, x, y in smash_bursts():
        n = 26; q = S3(x, y, 8.0)
        C.add_many(tk + rng.random(n) * 0.35, np.tile(q, (n, 1)) + rng.normal(0, 3, (n, 3)),
                   np.column_stack([rng.normal(0, 8, n), rng.normal(0, 8, n), rng.uniform(1, 9, n)]), r0=2.5, r1=rng.uniform(7, 12, n),
                   life=rng.uniform(2.5, 4.0, n), rise=0.8, kind="dust", alpha=0.75, tau=1.0, color=hexrgb("#bba987"))
    C.build(coll)
    STATE["cards"] = C
    say(f"smoke cards: {C.count()}")

def build_cannon_events():
    rng = np.random.default_rng(12)
    guns = []
    for o in bpy.data.objects:
        if o.name.startswith("TrostCannon_bulge"):
            p = o.location
            xm, ym = float(p.x), float(p.y) + segtime.SET_OFF_Y
            if abs(xm) < 200 and ym < 160 and not (-36.0 < xm < 0.0):
                guns.append(np.array([xm, ym, 52.2]))
    ev = []
    t = BEATS["cannons"]
    while t < DUR and guns:
        g = guns[int(rng.integers(len(guns)))]
        a = rng.uniform(0.2, math.pi - 0.2); r = rng.uniform(25, 72)
        hit = S3(r * math.cos(a), 8 + r * math.sin(a) * 0.9, 0.5)
        ev.append((t, S3(g), hit))
        t += rng.uniform(0.9, 1.8)
    STATE["cannon_events"] = ev

# ====================================================================== debris (kick), sweep flings, slabs, tower burst
def _box_corners(sx, sy, sz):
    return np.array([[x, y, z] for z in (-sz / 2, sz / 2) for (x, y) in ((-sx / 2, -sy / 2), (sx / 2, -sy / 2), (sx / 2, sy / 2), (-sx / 2, sy / 2))])

_CUBE_F = [[0, 3, 2, 1], [4, 5, 6, 7], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]]

def build_debris(coll):
    """25 big chunks (2 punch the craters), 80 medium stones (to r 150-220, onto roofs), 150 plank splinters: one mesh,
    vertices driven per frame (ballistic arcs with spin), each piece rests where it lands."""
    L = STATE["L"]
    rng = np.random.default_rng(404)
    kick = BEATS["kick"]
    pieces = []
    def piece(size, p0, land, T, mi):
        spin = rng.normal(0, 4.0, 3)
        pieces.append(dict(c=_box_corners(*size), p0=np.array(p0, float), land=np.array(land, float), T=T, spin=spin, mi=mi, t0=kick + rng.uniform(0.0, 0.12)))
    landings = []
    for k in range(25):
        s = rng.uniform(1.0, 3.0)
        if k < 2:
            xy = CRW if k == 0 else CRE
        else:
            a = math.radians(rng.uniform(-75, 75)); r = rng.uniform(20, 90)
            xy = (r * math.sin(a), 12 + r * math.cos(a))
        z = top_z(*xy) + s * 0.35
        dist = math.hypot(xy[0], xy[1] - 10); T = 0.8 + dist / 110.0
        piece((s * rng.uniform(0.8, 1.3), s, s * rng.uniform(0.6, 1.0)), S3(rng.uniform(-5.5, 5.5), rng.uniform(4, 14), rng.uniform(2, 14)), S3(xy[0], xy[1], z), T,
              int(rng.integers(0, 2)))
        landings.append((kick + T, S3(xy[0], xy[1], z), True))
    for k in range(80):
        s = rng.uniform(0.4, 1.0)
        a = math.radians(rng.uniform(-60, 60)); r = rng.uniform(40, 220) if k % 3 else rng.uniform(150, 220)
        xy = (r * math.sin(a) * 0.8 + (-15.0 * min(1.0, r / 300.0)), 12 + r * math.cos(a))
        z = top_z(*xy) + s * 0.3
        T = 0.9 + r / 95.0
        piece((s, s * rng.uniform(0.7, 1.2), s * rng.uniform(0.5, 0.9)), S3(rng.uniform(-5.5, 5.5), rng.uniform(4, 14), rng.uniform(2, 15)), S3(xy[0], xy[1], z), T,
              int(rng.integers(0, 2)))
        if k % 2 == 0:
            landings.append((kick + T, S3(xy[0], xy[1], z), False))
    for k in range(150):
        a = math.radians(rng.uniform(-80, 80)); r = rng.uniform(25, 260)
        xy = (r * math.sin(a), 12 + r * math.cos(a))
        z = top_z(*xy) + 0.08
        T = 0.9 + r / 100.0
        piece((rng.uniform(1.5, 4.0), rng.uniform(0.2, 0.35), 0.12), S3(rng.uniform(-5.5, 5.5), rng.uniform(5, 14), rng.uniform(2, 15)), S3(xy[0], xy[1], z), T, 2)
    STATE["landings"] = landings
    n = len(pieces)
    V = np.zeros((n * 8, 3)); F = []
    fmi = []
    for i, pc in enumerate(pieces):
        F += [[a + 8 * i for a in f] for f in _CUBE_F]; fmi += [pc["mi"]] * 6
    me = bpy.data.meshes.new("G5_Debris"); me.from_pydata(V.tolist(), [], F)
    for m in (L.mat("G5_DebBrick", hexrgb("#8e5040"), 0.9), L.mat("G5_DebStone", hexrgb("#8d8a82"), 0.9), L.mat("G5_DebPlank", hexrgb("#9a7a55"), 0.9)):
        me.materials.append(m)
    me.polygons.foreach_set("material_index", np.array(fmi, np.int32)); me.update()
    ob = bpy.data.objects.new("G5_Debris", me); coll.objects.link(ob)
    STATE["debris"] = dict(ob=ob, pieces=pieces)

def _rotm(v):
    ang = float(np.linalg.norm(v))
    if ang < 1e-9:
        return np.eye(3)
    k = v / ang; K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    return np.eye(3) + math.sin(ang) * K + (1 - math.cos(ang)) * K @ K

def update_debris(t):
    D = STATE["debris"]; ob = D["ob"]
    out = np.zeros((len(D["pieces"]) * 8, 3))
    for i, pc in enumerate(D["pieces"]):
        tt = t - pc["t0"]
        if tt < 0:
            out[8 * i:8 * i + 8] = np.array([0, 0, -500.0]); continue
        u = min(1.0, tt / pc["T"])
        p = pc["p0"] + (pc["land"] - pc["p0"]) * u
        p[2] = pc["p0"][2] * (1 - u) + pc["land"][2] * u + 4.9 * pc["T"] ** 2 * u * (1 - u)
        R = _rotm(pc["spin"] * min(tt, pc["T"]))
        out[8 * i:8 * i + 8] = pc["c"] @ R.T + p
    ob.data.vertices.foreach_set("co", out.astype(np.float32).ravel()); ob.data.update()

def build_walltop_props(coll):
    """Sweep zone X -35..0: the wall-top cannon, hut, flag, crates are flung west off the inner edge as the forearm passes;
    dark sweep streak (8 m) on the paving; crack decal on the inner face below the right fist."""
    L = STATE["L"]
    fl = []
    rng = np.random.default_rng(9)
    for o in bpy.data.objects:
        if o.name.startswith(("TrostCannon_bulge", "TrostHut_bulge", "TrostFlag_bulge", "TrostCrates_bulge")):
            xm, ym = float(o.location.x), float(o.location.y) + segtime.SET_OFF_Y
            if -41.0 < xm < 0.0 and ym < 12.0:
                xh = max(xm, SWEEP_X[1])
                u = (SWEEP_X[0] - xh) / (SWEEP_X[0] - SWEEP_X[1])
                th = BEATS["sweep"][0] + (BEATS["sweep"][1] - BEATS["sweep"][0]) * (math.acos(1 - 2 * min(1, max(0, u))) / math.pi)
                land = (xm - rng.uniform(22, 34), ym + rng.uniform(10, 22))
                fl.append(dict(ob=o, p0=o.location.copy(), r0=o.rotation_euler.copy(), th=th, T=rng.uniform(2.0, 2.6),
                               land=S3(land[0], land[1], top_z(*land) + 0.3), spin=rng.normal(0, 2.5, 3)))
    STATE["flings"] = fl
    for f in fl:
        STATE.setdefault("landings", []).append((f["th"] + f["T"], f["land"], True))
    say("sweep flings:", [f["ob"].name for f in fl])
    # sweep streak (#5b3a30, ~8 m wide), revealed behind the hand
    bm = bmesh.new()
    xs = np.linspace(SWEEP_X[0], SWEEP_X[1], 15)
    vs = []
    for x in xs:
        yc = 480.0 - math.sqrt(480.0 ** 2 - x * x)
        vs.append((bm.verts.new(S3(x, yc - 3.5, 50.32)), bm.verts.new(S3(x, yc + 4.0, 50.32))))
    for (a, b), (c, d) in zip(vs, vs[1:]):
        bm.faces.new((a, c, d, b))
    st = L.obj_from_bm("G5_SweepStreak", bm, [L.mat("G5_Streak", hexrgb("#5b3a30"), 0.95)], coll); st.visible_shadow = False
    STATE["streak"] = (st, np.array([v.co[:] for v in st.data.vertices]))
    # cracks below the fist on the inner face (Y ~ +5.6 at X 26), 8 m spread
    bm = bmesh.new(); rnd = random.Random(3)
    yc = 480.0 - math.sqrt(480.0 ** 2 - FIST_R[0] ** 2) + 5.05
    for k in range(9):
        x = FIST_R[0] - 4 + k * 1.0 + rnd.uniform(-0.3, 0.3); z = 50.0
        for s in range(5):
            x2 = x + rnd.uniform(-1.4, 1.4); z2 = z - rnd.uniform(1.0, 2.2)
            L.cyl(bm, S3(x, yc + 0.1, z), S3(x2, yc + 0.1, z2), 0.13, 0.08, seg=4); x, z = x2, z2
    ck = L.obj_from_bm("G5_FistCracks", bm, [L.mat("G5_Crack", (0.04, 0.035, 0.03), 0.95)], coll); ck.visible_shadow = False
    STATE["cracks"] = ck

def update_walltop_props(t):
    for f in STATE["flings"]:
        o = f["ob"]; tt = t - f["th"]
        if tt < 0:
            o.location = f["p0"]; o.rotation_euler = f["r0"]; continue
        u = min(1.0, tt / f["T"])
        p0 = np.array(f["p0"]); p1 = f["land"]
        p = p0 + (p1 - p0) * u
        p[2] = p0[2] * (1 - u) + p1[2] * u + 4.9 * f["T"] ** 2 * u * (1 - u) + 6.0 * math.sin(math.pi * u)
        o.location = Vector(p)
        sp = f["spin"] * min(tt, f["T"])
        o.rotation_euler = (f["r0"].x + sp[0], f["r0"].y + sp[1], f["r0"].z + sp[2])
    st, V0 = STATE["streak"]
    u = ss(BEATS["sweep"][0], BEATS["sweep"][1], t)
    V = V0.copy()
    if t < BEATS["sweep"][0] + 0.05:
        V[:, 2] = -50.0
    else:
        xs_end = lerp(SWEEP_X[0], SWEEP_X[1], u)
        x = V[:, 0]
        cut = x < xs_end
        V[cut, 0] = xs_end
    st.data.vertices.foreach_set("co", V.astype(np.float32).ravel()); st.data.update()
    ck = STATE["cracks"]
    g = ss(BEATS["grip"][1] - 0.1, BEATS["grip"][1] + 0.8, t)
    _hide(ck, g <= 0.01)
    if g > 0.01:
        ck.scale = (1.0, 1.0, 1.0)

def build_slabs():
    """Slab poses: rest -> rocked 2-5 m north at the kick -> knocked into the end state by the pour (bible g5 2a)."""
    rng = np.random.default_rng(14)
    S = {}
    ends = {"TrostSlab_P1": ("topple", 9.6, None), "TrostSlab_P2": ("lean", 11.0, -1), "TrostSlab_P3": ("lean", 11.3, 1),
            "TrostSlab_P4": ("shove", (10.0, 13.0), 15.0), "TrostSlab_P5": ("topple", 12.6, None), "TrostSlab_P6": ("topple", 14.2, None),
            "TrostSlab_A1": ("topple", 15.0, None), "TrostSlab_A2": ("stand", None, None), "TrostSlab_A3": ("topple", 13.4, None),
            "TrostSlab_A4": ("wreck", 11.8, (-9.0, 80.0)), "TrostSlab_A5": ("wreck", 12.4, (9.0, 80.0)), "TrostSlab_A6": ("topple", 16.2, None),
            "TrostSlab_A7": ("stand", None, None), "TrostSlab_A8": ("topple", 17.5, None)}
    for nm, e in ends.items():
        o = bpy.data.objects.get(nm)
        if o is None:
            continue
        S[nm] = dict(ob=o, loc=np.array(o.location[:]), yaw=float(o.rotation_euler.z), rock=rng.uniform(2.0, 5.0), wob=rng.uniform(4, 9) * rng.choice([-1, 1]),
                     end=e, twist=rng.uniform(-25, 25))
    STATE["slabs"] = S
    say(f"slabs: {len(S)}")

def _slab_xf(s, t):
    loc = s["loc"].copy(); yaw = s["yaw"]; tilt = 0.0; roll = 0.0
    kind, te, arg = s["end"]
    r = ss(BEATS["kick"], BEATS["kick"] + 0.8, t)
    loc[1] += s["rock"] * r
    tilt = math.radians(s["wob"]) * math.sin(math.pi * min(1.0, max(0.0, (t - BEATS["kick"]) / 1.2))) * math.exp(-max(0.0, t - BEATS["kick"]))
    fwd = np.array([-math.sin(yaw), math.cos(yaw)])           # local +Y in the world
    sgn = 1.0 if fwd[1] > 0 else -1.0                           # topple toward the north
    if kind == "topple" and t >= te:
        u = ss(te, te + 0.9, t); tilt = sgn * math.radians(90.0) * u; yaw += math.radians(s["twist"]) * u * 0.3
    elif kind == "lean" and t >= te:
        u = ss(te, te + 0.8, t); roll = arg * math.radians(28.0) * u
    elif kind == "shove":
        u = ss(te[0], te[1], t); loc[1] += arg * u; yaw += math.radians(s["twist"]) * u * 0.4
    elif kind == "wreck" and t >= te:
        u = ss(te, te + 1.2, t)
        tgt = S3(arg[0], arg[1])
        loc[0] = lerp(loc[0], tgt[0], u); loc[1] = lerp(loc[1], tgt[1], u); tilt = sgn * math.radians(32.0) * u; yaw += math.radians(s["twist"]) * u
    # pivot on the base edge (local y = +-2 for a tilt about local X, local x = +-4 for a roll about local Y)
    Rz = Matrix.Rotation(yaw, 4, "Z")
    pv = Vector((0.0, 2.0 * (1 if tilt > 0 else -1), 0.0)) if abs(tilt) > 1e-6 else Vector((4.0 * (1 if roll > 0 else -1), 0.0, 0.0))
    Rl = Matrix.Rotation(-tilt, 4, "X") @ Matrix.Rotation(roll, 4, "Y")
    off = pv - (Rl @ pv)
    M_ = Matrix.Translation(Vector(loc)) @ Rz @ Matrix.Translation(off) @ Rl
    return M_

def update_slabs(t):
    for nm, s in STATE["slabs"].items():
        s["ob"].matrix_world = _slab_xf(s, t)

def build_stakes(coll):
    """~10 crossed timber X-stakes (2 m) strewn on the middle ring and the grass after the kick."""
    L = STATE["L"]; rnd = random.Random(10)
    bm = bmesh.new()
    for k in range(11):
        a = rnd.uniform(0, math.tau); r = rnd.uniform(11, 17) if k < 5 else rnd.uniform(28, 60)
        x, y = PIT[0] + r * math.cos(a), PIT[1] + r * math.sin(a) * 0.9
        if y < 10:
            continue
        z = G(x, y) + 0.3; rot = rnd.uniform(0, math.pi)
        for s in (-1, 1):
            d = Vector((math.cos(rot + s * 0.6), math.sin(rot + s * 0.6), 0.25 * s))
            c = Vector(S3(x, y, z))
            L.cyl(bm, c - d * 1.2, c + d * 1.2, 0.12, 0.12, seg=5)
    ob = L.obj_from_bm("G5_XStakes", bm, [L.mat("G5_Stake", hexrgb("#5a4532"), 0.9)], coll)
    STATE["stakes"] = ob

def build_tower_burst(coll):
    L = STATE["L"]; rng = np.random.default_rng(522)
    top = bpy.data.objects.get("TrostTowerT_Top")
    STATE["tower_top"] = top
    tb = BEATS["slam"]
    ch = []
    m = L.mat("G5_Ashlar", hexrgb("#cfc4a8"), 0.85)
    for k in range(22):
        s = rng.uniform(0.5, 1.5)
        bm = bmesh.new(); L.box(bm, (0, 0, 0), (s * rng.uniform(0.8, 1.4), s, s * rng.uniform(0.6, 1.0)))
        ob = L.obj_from_bm(f"G5_TowerBlock{k}", bm, [m], coll); ob.hide_render = True
        p0 = S3(TOWER[0] + rng.uniform(-3, 3), TOWER[1] + rng.uniform(-3, 3), rng.uniform(31, 38))
        a = rng.uniform(0, math.tau); r = rng.uniform(4, 24)
        xy = (TOWER[0] + r * math.cos(a), TOWER[1] + r * math.sin(a))
        land = S3(xy[0], xy[1], top_z(*xy) + s * 0.3)
        ch.append(dict(ob=ob, p0=p0, land=land, T=rng.uniform(1.2, 2.2), spin=rng.normal(0, 4, 3), t0=tb + rng.uniform(0, 0.25)))
    STATE["tower_blocks"] = ch
    # grind scar on the shaft's south face
    bm = bmesh.new(); L.box(bm, S3(TOWER[0] - 1.5, TOWER[1] - 4.15, 18.0), (2.4, 0.15, 18.0))
    sc = L.obj_from_bm("G5_GrindScar", bm, [L.mat("G5_Scar", hexrgb("#6a5a4a"), 0.95)], coll); sc.visible_shadow = False
    STATE["scar"] = sc

def update_tower(t):
    tb = BEATS["slam"]
    if STATE.get("tower_top") is not None:
        _hide(STATE["tower_top"], t >= tb + 0.05)
    for c in STATE["tower_blocks"]:
        tt = t - c["t0"]
        if tt < 0:
            _hide(c["ob"], True); continue
        _hide(c["ob"], False)
        u = min(1.0, tt / c["T"])
        p = c["p0"] + (c["land"] - c["p0"]) * u
        p[2] = c["p0"][2] * (1 - u) + c["land"][2] * u + 4.9 * c["T"] ** 2 * u * (1 - u) * 0.6
        c["ob"].location = Vector(p); sp = c["spin"] * min(tt, c["T"]); c["ob"].rotation_euler = tuple(sp)
    _hide(STATE["scar"], t < BEATS["cc_slide"][0] + 0.2)

# ====================================================================== bolt (0.0), AT emergence bolt, decals, shafts, clouds
def _bolt_mesh(name, top, bot, seed, r, n=26, amp=14.0, coll=None, col="#fcfa95", strength=60.0, branches=0, glow=None):
    """Jagged lightning: one main channel top -> bot (bright core) + `branches` side channels, optional gold glow sheath."""
    L = STATE["L"]; rnd = random.Random(seed)
    top, bot = Vector(top), Vector(bot)
    chans = []
    pts = [top]
    for k in range(1, n):
        u = k / n
        sw = math.sin(u * math.pi * 1.6) * amp
        q = top.lerp(bot, u) + Vector((sw + rnd.uniform(-7, 7), rnd.uniform(-7, 7), rnd.uniform(-4, 4)))
        pts.append(q)
    pts.append(bot)
    chans.append((pts, r))
    for b in range(branches):
        i0 = rnd.randrange(3, n - 6)
        p = pts[i0].copy(); bp = [p]
        dirv = Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), 0.0)).normalized()
        step = (top.z - bot.z) / n
        for k in range(rnd.randint(4, 9)):
            p = p + dirv * rnd.uniform(8, 16) + Vector((rnd.uniform(-5, 5), rnd.uniform(-5, 5), -step * rnd.uniform(0.6, 1.2)))
            bp.append(p.copy())
        chans.append((bp, r * 0.5))
    bm = bmesh.new()
    for cp, rr in chans:
        for a, b in zip(cp, cp[1:]):
            L.cyl(bm, a, b, rr, rr * 0.9, seg=6)
    m, _ = emit_mat(name + "Mat", hexrgb(col), strength)
    ob = L.obj_from_bm(name, bm, [m], coll); ob.visible_shadow = False; ob.hide_render = True
    if glow:
        gcol, gstr, gr = glow
        gm = bpy.data.materials.new(name + "GlowMat"); gm.use_nodes = True
        nt = gm.node_tree; N = nt.nodes; Lk = nt.links
        N.remove(N["Principled BSDF"])
        em = N.new("ShaderNodeEmission"); em.inputs["Color"].default_value = (*hexrgb(gcol), 1); em.inputs["Strength"].default_value = gstr
        tr = N.new("ShaderNodeBsdfTransparent"); mx = N.new("ShaderNodeMixShader"); mx.inputs[0].default_value = 0.45
        Lk.new(tr.outputs[0], mx.inputs[1]); Lk.new(em.outputs[0], mx.inputs[2]); Lk.new(mx.outputs[0], N["Material Output"].inputs["Surface"])
        try:
            gm.surface_render_method = "BLENDED"
        except Exception:
            pass
        gm["toon"] = 1
        bm2 = bmesh.new()
        for cp, rr in chans:
            for a, b in zip(cp, cp[1:]):
                L.cyl(bm2, a, b, rr * gr, rr * gr * 0.9, seg=8)
        g = L.obj_from_bm(name + "Glow", bm2, [gm], coll); g.visible_shadow = False; g.hide_render = True
        g.parent = ob; g.matrix_parent_inverse = ob.matrix_world.inverted()
        ob["glow"] = g.name
    return ob

def build_bolts(coll):
    # v4 (owner lightning ref, g1 AND g5): ONE thick wavy golden bolt (no branches), white-yellow core, orange glow sleeve
    b0 = _bolt_mesh("G5_Bolt0", S3(-60, -260, 720), S3(0, -25, 0), 11, 2.6, n=40, amp=38.0, coll=coll, col="#fcf495", strength=60.0,
                    branches=0, glow=("#e8940f", 10.0, 2.9))
    b1 = _bolt_mesh("G5_Bolt1", S3(-52, -255, 720), S3(0, -25, 0), 12, 2.6, n=40, amp=36.0, coll=coll, col="#fcf495", strength=60.0,
                    branches=0, glow=("#e8940f", 10.0, 2.9))
    build_strike(coll)
    ld = bpy.data.lights.new("G5_BoltFlash", "POINT"); ld.color = (1.0, 0.85, 0.4); ld.energy = 0.0; ld.shadow_soft_size = 40
    lo = bpy.data.objects.new("G5_BoltFlash", ld); lo.location = SV(0, -40, 150); coll.objects.link(lo)
    ab = _bolt_mesh("G5_ATBolt", S3(BT_POS[0] + 4, BT_POS[1] - 3, 31), S3(BT_POS[0], BT_POS[1], 4), 31, 0.55, n=10, amp=2.0, coll=coll,
                    col="#ffc21a", strength=12.0)
    ld2 = bpy.data.lights.new("G5_ATFlash", "POINT"); ld2.color = (1.0, 0.82, 0.4); ld2.energy = 0.0; ld2.shadow_soft_size = 6
    lo2 = bpy.data.objects.new("G5_ATFlash", ld2); lo2.location = SV(BT_POS[0], BT_POS[1], 14); coll.objects.link(lo2)
    STATE["bolts"] = (b0, b1, ld, ab, ld2)

def flicker(t):
    """Bolt flicker: 2 frames spike, 1 frame near black, 1 spike (15 fps), then a fading yellow cast."""
    if 0.0 <= t < 0.13: return "spike0"
    if 0.13 <= t < 0.2: return "dark"
    if 0.2 <= t < 0.27: return "spike1"
    return None

def build_strike(coll):
    """v4 (ref/user/lightning_spec.md, as g1 v5): dome shockwave flash + upward spark streaks behind the wall top, thin
    orange-red ribbon arcs crawling down over the town (0.35-1.4 s), and the SMOKE column up before the skull (rise 0.5)."""
    L = STATE["L"]; rng = np.random.default_rng(23); rnd = random.Random(17)
    X = SC.SmokeCards("G5Strike")
    X.add(0.06, S3(0, -25, 40), r0=20.0, r1=120.0, life=0.42, kind="glow", color=(1.0, 0.78, 0.32), alpha=0.95, fade_in=0.02)
    X.add(0.08, S3(0, -25, 55), r0=10.0, r1=60.0, life=0.3, kind="glow", color=(1.0, 0.95, 0.7), alpha=1.0, fade_in=0.02)
    n = 46
    d = np.column_stack([rng.normal(0, 0.6, n), rng.normal(0, 0.35, n), rng.uniform(0.5, 1.4, n)]); d /= np.linalg.norm(d, axis=1)[:, None]
    X.add_many(0.06 + rng.uniform(0, 0.15, n), np.tile(S3(0, -25, 48), (n, 1)) + rng.normal(0, 3, (n, 3)), d * rng.uniform(90, 220, n)[:, None],
               r0=1.6, r1=1.0, life=rng.uniform(0.3, 0.6, n), kind="glow", color=(1.0, 0.82, 0.38), alpha=1.0, fade_in=0.01, dirs=d, stretch=7.0)
    n = 46
    X.add_many(0.04 + rng.uniform(0, 0.35, n), np.array([S3(x, y, z) for x, y, z in zip(rng.normal(0, 12, n), -25 + rng.normal(0, 8, n), rng.uniform(15, 50, n))]),
               np.column_stack([rng.normal(0, 4, n), rng.normal(0, 3, n), rng.uniform(28, 48, n)]), r0=rng.uniform(10, 16, n),
               r1=rng.uniform(32, 48, n), life=rng.uniform(6, 9, n), rise=2.0, color=(0.60, 0.53, 0.45), kind="steam", alpha=0.9, tau=0.9, fade_in=0.08)
    X.build(coll); STATE["strike"] = X
    arcs = []
    for k in range(7):
        x0 = rnd.uniform(-110, 110); y0 = rnd.uniform(2, 14); z0 = rnd.uniform(58, 82)
        Ln_ = rnd.uniform(150, 240); hd = math.radians(90 + rnd.uniform(-35, 35)); dz = rnd.uniform(-45, -20)
        ph, amp = rnd.uniform(0, 6.3), rnd.uniform(6, 14)
        pts = []
        for i in range(43):
            s_ = i / 42
            q = (x0 + Ln_ * s_ * math.cos(hd) - math.sin(hd) * amp * math.sin(ph + 9 * s_),
                 y0 + Ln_ * s_ * math.sin(hd) + math.cos(hd) * amp * math.sin(ph + 9 * s_),
                 z0 + dz * s_ - 25 * s_ * s_ + 0.5 * amp * math.sin(ph * 1.7 + 13 * s_))
            pts.append(Vector(S3(*q)))
        m, em = emit_mat(f"G5_Arc{k}", (1.0, 0.20, 0.03), 0.0)
        obs = []
        for c in range(14):
            bm = bmesh.new()
            for a, b in zip(pts[3 * c:3 * c + 3], pts[3 * c + 1:3 * c + 4]):
                L.cyl(bm, a, b, 0.75, 0.75, seg=6)
            ob = L.obj_from_bm(f"G5_Arc{k}_{c}", bm, [m], coll); ob.visible_shadow = False; ob.hide_render = True; obs.append(ob)
        arcs.append((obs, em, 0.35 + 0.12 * k + rnd.uniform(0, 0.06)))
    STATE["arcs"] = arcs

def update_bolts(t):
    if STATE.get("strike"):
        STATE["strike"].update(t, wind=(WIND[0], WIND[1]))
    for obs, em, t0 in STATE.get("arcs", ()):
        head = (t - t0) / 0.45 * 14; alive = t0 <= t < t0 + 0.8
        if em is not None:
            em.default_value = 7.0 * (1 - ss(t0 + 0.45, t0 + 0.8, t))          # (flares.emit_mat returns the Strength socket)
        for c, ob in enumerate(obs):
            _hide(ob, not (alive and head - 6 <= c < head))
    b0, b1, ld, ab, ld2 = STATE["bolts"]
    f = flicker(t)
    for b_, on_ in ((b0, f == "spike0"), (b1, f == "spike1")):
        _hide(b_, not on_)
        if b_.get("glow"):
            _hide(bpy.data.objects.get(b_["glow"]), not on_)
    ld.energy = 6e6 if f in ("spike0", "spike1") else 0.0
    te = BEATS["bt_torn"]
    on = te <= t < te + 0.2
    _hide(ab, not on)
    ld2.energy = 1.2e6 * bump(t, te - 0.01, te + 0.02, te + 0.12, te + 0.3)

def build_decals(coll):
    L = STATE["L"]; rng = random.Random(77)
    bm = bmesh.new()
    TT = STATE["TT"]
    nap = lambda nm, t: tuple(np.array(TT.nape(nm, t))[:2] + np.array([0.0, segtime.SET_OFF_Y]))
    spots = [(nap("CAP", 60.5), 1.6, BEATS["stomps"][0]), (nap("LH", 62.0), 1.3, BEATS["lh_stamp"]), ((-20, 52), 1.2, 21.0), ((24, 70), 1.0, 17.0),
             ((-6, 95), 1.4, 13.0), (nap("CC", 67.5), 1.4, BEATS["nape_stamp"])]
    objs = []
    for (xy, r, te) in spots:
        bm = bmesh.new()
        c = S3(xy[0], xy[1], G(*xy) + heap_z(*xy) + 0.07)
        res = bmesh.ops.create_circle(bm, cap_ends=True, segments=10, radius=r)
        for v in res["verts"]:
            v.co += Vector(c)
        o = L.obj_from_bm(f"G5_Blood{len(objs)}", bm, [L.mat("G5_BloodMat", hexrgb("#5a1a14"), 0.6)], coll); o.visible_shadow = False
        objs.append((te, o))
    STATE["blood"] = objs
    # BT's dark pool + a ribcage showing as the carcass evaporates
    bm = bmesh.new()
    c = S3(BT_POS[0] - 3.0, BT_POS[1], 0.06)
    res = bmesh.ops.create_circle(bm, cap_ends=True, segments=16, radius=3.6)
    rr = random.Random(5)
    for v in res["verts"]:
        if v.co.length > 0.1:
            v.co *= rr.uniform(0.65, 1.15)
        v.co += Vector(c)
    pool = L.obj_from_bm("G5_BTPool", bm, [L.mat("G5_Pool", hexrgb("#3a1410"), 0.4)], coll); pool.visible_shadow = False
    bm = bmesh.new(); cx, cy = BT_POS[0] - 3.5, BT_POS[1]
    for k in range(6):
        x = cx - 2.5 + k * 1.0
        for s in (-1, 1):
            pts = [Vector(S3(x, cy + s * 0.2 * j * j, 0.3 + 1.4 * math.sin(j * 0.55))) for j in range(5)]
            for a, b in zip(pts, pts[1:]):
                L.cyl(bm, a, b, 0.12, 0.1, seg=4)
    L.cyl(bm, Vector(S3(cx - 3.5, cy, 1.4)), Vector(S3(cx + 3.5, cy, 1.4)), 0.2, 0.2, seg=5)
    ribs = L.obj_from_bm("G5_BTRibs", bm, [L.mat("G5_Bone", hexrgb("#d8cfc0"), 0.7)], coll)
    STATE["bt_pool"] = (pool, ribs)
    bm = bmesh.new(); L.box(bm, S3(-266.35, 401.5, 4.5), (0.12, 7.0, 6.0))             # impact scar on the W alley wall
    scar = L.obj_from_bm("G5_MAScar", bm, [L.mat("G5_MAScarMat", hexrgb("#3a3430"), 0.95)], coll); scar.visible_shadow = False
    STATE["ma_scar"] = scar

def update_decals(t):
    for te, o in STATE["blood"]:
        _hide(o, t < te)
    pool, ribs = STATE["bt_pool"]
    te = BEATS["bt_torn"]
    _hide(pool, t < te + 1.0)
    if t >= te + 1.0:
        s = 0.3 + 0.7 * ss(te + 1.0, te + 8.0, t); pool.scale = (s, s, 1.0)
        c = Vector(S3(BT_POS[0] - 3.0, BT_POS[1], 0.0)); pool.location = c - Vector((c.x * s, c.y * s, 0.0))
    _hide(ribs, t < te + 6.0)
    _hide(STATE["ma_scar"], t < BEATS["punch"] + 0.45)

def build_shafts(coll):
    """2-3 warm sun shafts (additive gradient cones) through the breaking overcast over MA / Q2 (from 50)."""
    L = STATE["L"]
    m = bpy.data.materials.new("G5_Shaft"); m.use_nodes = True
    nt = m.node_tree; N = nt.nodes; Lk = nt.links
    N.remove(N["Principled BSDF"])
    em = N.new("ShaderNodeEmission"); em.inputs["Color"].default_value = (1.0, 0.9, 0.7, 1.0); em.inputs["Strength"].default_value = 1.0
    tr = N.new("ShaderNodeBsdfTransparent")
    lw = N.new("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = 0.6
    inv = N.new("ShaderNodeMath"); inv.operation = "SUBTRACT"; inv.inputs[0].default_value = 1.0; Lk.new(lw.outputs["Facing"], inv.inputs[1])
    a = N.new("ShaderNodeMath"); a.operation = "MULTIPLY"; a.name = "ShaftAlpha"; a.inputs[1].default_value = 0.0
    Lk.new(inv.outputs[0], a.inputs[0])
    mx = N.new("ShaderNodeMixShader"); Lk.new(a.outputs[0], mx.inputs[0]); Lk.new(tr.outputs[0], mx.inputs[1]); Lk.new(em.outputs[0], mx.inputs[2])
    Lk.new(mx.outputs[0], N["Material Output"].inputs["Surface"])
    try:
        m.surface_render_method = "BLENDED"
    except Exception:
        pass
    m["toon"] = 1
    obs = []
    for k, (x, y, r) in enumerate(((-262, 408, 5.0), (-238, 502, 7.0), (-200, 455, 5.5))):
        bm = bmesh.new()
        L.cyl(bm, Vector(S3(x + 90, y - 95, 260)), Vector(S3(x, y, 0)), r * 0.6, r, seg=12)
        o = L.obj_from_bm(f"G5_SunShaft{k}", bm, [m], coll); o.visible_shadow = False
        obs.append(o)
    STATE["shafts"] = (obs, a)

def update_shafts(t):
    obs, a = STATE["shafts"]
    w = ss(BEATS["shafts"][0], BEATS["shafts"][0] + 4.0, t)
    for o in obs:
        _hide(o, w <= 0.01)
    a.inputs[1].default_value = 0.13 * w

def build_cloud_shadows(coll):
    """Shadow-only discs at Z 520 drifting with the wind: cloud shadows sweep the town during the roll-in and the breaking
    overcast (camera-invisible: visible_camera False)."""
    L = STATE["L"]; rng = np.random.default_rng(21)
    obs = []
    m = L.mat("G5_CloudShadow", (0.5, 0.5, 0.5), 0.9)
    for k in range(26):
        bm = bmesh.new()
        r = rng.uniform(55, 140)
        res = bmesh.ops.create_circle(bm, cap_ends=True, segments=14, radius=r)
        for v in res["verts"]:
            v.co.x *= rng.uniform(1.0, 1.6)
        o = L.obj_from_bm(f"G5_CloudShadow{k}", bm, [m], coll)
        try:
            o.visible_camera = False; o.visible_diffuse = False; o.visible_glossy = False
        except Exception:
            pass
        obs.append((o, np.array([rng.uniform(-700, 500), rng.uniform(-300, 1100)]), rng.uniform(0.0, 1.0)))
    STATE["clouds"] = obs

def update_cloud_shadows(t, sun_dir):
    cov = ss(BEATS["clouds"][0], BEATS["clouds"][1], t) * (1 - 0.45 * ss(50.0, 56.0, t))
    drift = np.array([22.0, 9.0]) * t
    h = 520.0
    sd = np.array(sun_dir, float)
    off = sd[:2] / max(sd[2], 0.15) * h
    for o, p0, thr in STATE["clouds"]:
        on = cov > thr * 0.95 and t >= BEATS["clouds"][0]
        _hide(o, not on)
        if on:
            q = p0 + drift
            q[0] = (q[0] + 800) % 1500 - 800
            o.location = Vector(S3(q[0] + off[0], q[1] + off[1], h))

CLEAR_LOTS = [(-256.0, -200.0, 429.5, 466.0)]          # M rects (x0, x1, y0, y1): houses removed for the alley view
def clear_lots():
    """Owner QA (alley 46-62 s): the camera looks S down MA from ~230 m N; the houses N of SS hid SS and the punch."""
    o = bpy.data.objects.get("TrostTown")
    if o is None or o.type != "MESH":
        return
    import bmesh as _bm
    me = o.data; mw = o.matrix_world
    bm = _bm.new(); bm.from_mesh(me)
    dead = []
    for v in bm.verts:
        w = mw @ v.co; x, y = w.x, w.y + segtime.SET_OFF_Y
        if any(x0 <= x <= x1 and y0 <= y <= y1 for x0, x1, y0, y1 in CLEAR_LOTS):
            dead.append(v)
    _bm.ops.delete(bm, geom=dead, context="VERTS")
    bm.to_mesh(me); bm.free(); me.update()
    say(f"cleared {len(dead)} houses N of SS for the alley view")

# ---------------------------------------------------------------------- AT smash run (owner 10/27: through the houses, no leap)
SMASH_W, SMASH_BINS = 8.5, 6                            # corridor half-width (m) around his path, chunks along it
def _smash_seg():
    i = next(k for k, a in enumerate(AT_KEYS) if a[4] == "smash")
    a, b = AT_KEYS[i - 1], AT_KEYS[i]
    return np.array(a[1:3], float), np.array(b[1:3], float), a[0], b[0]

def build_smash(coll):
    """Cut the TrostTown faces in a corridor along the smash path (MA end wall Y 456 -> Q2 edge) into SMASH_BINS chunk
    objects; update_smash collapses each one as he reaches it (sink + tilt 0.3 s, then gone) with dust + flying blocks."""
    o = bpy.data.objects.get("TrostTown")
    STATE["smash"] = []
    if o is None or o.type != "MESH":
        return
    import bmesh as _bm
    A, B, ta, tb = _smash_seg()
    d = B - A; Ln = float(np.linalg.norm(d)); dn = d / Ln
    me = o.data; mw = o.matrix_world; mwi = mw.inverted()
    bm = _bm.new(); bm.from_mesh(me)
    bins = [[] for _ in range(SMASH_BINS)]
    for f in bm.faces:
        c = mw @ f.calc_center_median(); q = np.array([c.x, c.y + segtime.SET_OFF_Y])
        s_ = float(np.dot(q - A, dn)); off = abs(float(np.cross(dn, q - A)))
        if off < SMASH_W and 450.0 < q[1] < 494.0 and -4.0 < s_ < Ln:
            bins[min(SMASH_BINS - 1, max(0, int(s_ / Ln * SMASH_BINS)))].append(f)
    L = STATE["L"]; rng = np.random.default_rng(613)
    mblk = L.mat("G5_SmashBlock", hexrgb("#c9b99a"), 0.85)
    dead = set()
    for k, fs in enumerate(bins):
        if not fs:
            continue
        nb = _bm.new(); vm = {}
        for f in fs:
            vs = []
            for v in f.verts:
                if v not in vm:
                    vm[v] = nb.verts.new(v.co)
                vs.append(vm[v])
            try:
                nf = nb.faces.new(vs); nf.material_index = f.material_index; nf.smooth = f.smooth
            except ValueError:
                pass
            dead.add(f)
        nme = bpy.data.meshes.new(f"G5_Smash{k}"); nb.to_mesh(nme); nb.free()
        for m in me.materials:
            nme.materials.append(m)
        ob = bpy.data.objects.new(f"G5_Smash{k}", nme); coll.objects.link(ob); ob.matrix_world = mw.copy()
        cen = np.mean([np.array(mw @ v.co) for v in vm], axis=0)
        # pivot at the chunk's ground centre (so it sinks / tilts about its base)
        piv = Vector((float(cen[0]), float(cen[1]), float(min((mw @ v.co).z for v in vm))))
        nme.transform(Matrix.Translation(mwi @ piv).inverted()); ob.location = piv
        tk = ta + (tb - ta) * (k + 0.5) / SMASH_BINS - 0.06
        blocks = []
        for j in range(7):
            sz = rng.uniform(0.7, 1.8)
            bmb = _bm.new(); L.box(bmb, (0, 0, 0), (sz, sz * rng.uniform(0.7, 1.3), sz * rng.uniform(0.6, 1.0)))
            bo = L.obj_from_bm(f"G5_SmashBlk{k}_{j}", bmb, [mblk], coll); bo.hide_render = True
            p0 = np.array(piv) + np.array([rng.normal(0, 3), rng.normal(0, 3), rng.uniform(4, 12)])
            v0 = np.array([dn[0], dn[1], 0.0]) * rng.uniform(8, 18) + np.array([rng.normal(0, 7), rng.normal(0, 7), rng.uniform(6, 14)])
            blocks.append(dict(ob=bo, p0=p0, v0=v0, spin=rng.normal(0, 5, 3)))
        STATE["smash"].append(dict(ob=ob, t=tk, loc=piv.copy(), tilt=(float(dn[1]), float(-dn[0])), blocks=blocks,
                                   cen=(float(cen[0]), float(cen[1]) + segtime.SET_OFF_Y)))
    _bm.ops.delete(bm, geom=list(dead), context="FACES")
    bm.to_mesh(me); bm.free(); me.update()
    say(f"smash corridor: {len(dead)} faces in {len(STATE['smash'])} chunks")

def smash_bursts():
    """(t, x, y) of each chunk collapse (M) for the dust cards."""
    return [(c["t"], c["cen"][0], c["cen"][1]) for c in STATE.get("smash", [])]

def update_smash(t):
    for c in STATE.get("smash", []):
        u = ss(c["t"], c["t"] + 0.35, t)
        _hide(c["ob"], u >= 0.999)
        c["ob"].location = c["loc"] + Vector((0.0, 0.0, -9.0 * u * u))
        c["ob"].rotation_euler = (0.5 * u * c["tilt"][0], 0.5 * u * c["tilt"][1], 0.0)
        c["ob"].scale = (1.0, 1.0, 1.0 - 0.6 * u)
        for b in c["blocks"]:
            tt = t - c["t"]
            if tt < 0 or tt > 2.2:
                _hide(b["ob"], True); continue
            _hide(b["ob"], False)
            p = b["p0"] + b["v0"] * tt + np.array([0.0, 0.0, -4.9 * tt * tt])
            p[2] = max(p[2], float(c["loc"].z) + 0.4)
            b["ob"].location = Vector(p); b["ob"].rotation_euler = tuple(b["spin"] * tt)

def fix_q2_dome(coll=None):
    """Owner QA (shared with seg_g6): the domed drum on Q2's north side read as a brown disc on a square base from the
    sky.  Remove the copper dome, its cream drum and the square block under it (everything of TrostQ2Buildings within
    9 m of the dome centre), and put a small round well there: 3.4 m grey stone rim, dark water, no base."""
    import bmesh as _bm, sys as _sys
    o = bpy.data.objects.get("TrostQ2Buildings")
    if o is None or bpy.data.objects.get("G5_Q2Well") is not None:
        return
    me = o.data
    cop = {i for i, m in enumerate(me.materials) if m and m.name.startswith("TrostRoofCopper")}
    if not cop:
        return
    bm = _bm.new(); bm.from_mesh(me)
    cs = [f.calc_center_median() for f in bm.faces if f.material_index in cop]
    if not cs:
        bm.free(); return
    cx = sum(v.x for v in cs) / len(cs); cy = sum(v.y for v in cs) / len(cs)
    dead = [f for f in bm.faces if math.hypot(f.calc_center_median().x - cx, f.calc_center_median().y - cy) < 7.6]
    _bm.ops.delete(bm, geom=dead, context="FACES")
    bm.to_mesh(me); bm.free(); me.update()
    L = STATE.get("L") or _sys.modules["aotlib"]
    TRm = STATE.get("TR") or _sys.modules.get("trost")
    c = o.matrix_world @ Vector((cx, cy, 0.0))
    try:
        z0 = float(TRm.ground_z(c.x, c.y))
    except Exception:
        z0 = 0.0
    bmw = bmesh.new()
    L.cyl(bmw, (c.x, c.y, z0), (c.x, c.y, z0 + 0.85), 1.7, 1.7, seg=16)              # grey stone rim, 3.4 m across
    L.cyl(bmw, (c.x, c.y, z0 + 0.85), (c.x, c.y, z0 + 0.88), 1.2, 1.2, seg=16, mi=1)  # dark water
    mats = [L.mat("G5_WellStone", hexrgb("#8e8a84"), 0.9), L.mat("G5_WellWater", hexrgb("#14191c"), 0.3)]
    L.obj_from_bm("G5_Q2Well", bmw, mats, coll)
    print(f"[seg g5] Q2 dome / drum / base removed ({len(dead)} faces), 3.4 m well at M ({c.x:.1f}, {c.y + segtime.SET_OFF_Y:.1f})")

# ====================================================================== build / update (contract)
def build(site):
    t0 = time.time()
    STATE["site"] = site; STATE["TR"] = site["TR"]; STATE["L"] = site["L"]
    TR = STATE["TR"]
    coll = _coll("G5")
    bpy.context.view_layer.update()
    for xy in SMOKE_SITES:
        top_z(*xy)
    try:
        TR.set_breach(False); TR.set_glow(0.0)
    except Exception as ex:
        say("set_breach failed:", ex)
    try:
        TR.set_wagon(True); TR.set_cart("start")
    except Exception as ex:
        say("cart hooks failed:", ex)
    fix_q2_dome(coll)
    clear_lots(); build_smash(coll); bpy.context.view_layer.update(); _RC.clear()
    build_cannon_events()
    build_slabs()
    build_debris(coll)
    build_walltop_props(coll)
    build_stakes(coll)
    build_tower_burst(coll)
    build_titans(coll)
    build_attack(coll)
    build_shadows(coll)
    build_colossal()
    build_people(coll)
    build_crowd(coll)
    build_cards(coll)
    build_bolts(coll)
    build_decals(coll)
    build_shafts(coll)
    build_cloud_shadows(coll)
    _light_capture()
    say(f"build {time.time() - t0:.1f}s")

def finish():
    pass

def update(t):
    t = float(t)
    TR = STATE["TR"]
    kick = BEATS["kick"]
    br = t >= kick
    if STATE.get("breach") != br:
        try:
            TR.set_breach(br)
        except Exception as ex:
            say("set_breach failed:", ex)
        STATE["breach"] = br
    try:
        TR.set_glow(0.0 if not br else 0.55 * (1 - 0.6 * ss(kick + 2.0, kick + 12.0, t)))
    except Exception:
        pass
    try:
        TR.set_cart(frac=ss(*BEATS["cart"], t))
    except Exception:
        pass
    update_colossal(t)
    _pose_attack(t)
    STATE["TT"].update(t)
    update_shadows(t)
    try:
        STATE["SQ"].update(t)
    except TypeError:                     # odm one-hook hop: u ** 1.8 of a -1e-17 rounding residue -> complex; nudge t
        STATE["SQ"].update(t + 1e-4)
    update_crowd(t)
    STATE["cards"].update(t, wind=(WIND[0], WIND[1]))
    update_debris(t)
    update_walltop_props(t)
    update_slabs(t)
    _hide(STATE["stakes"], t < kick + 0.6)
    update_tower(t)
    update_smash(t)
    update_bolts(t)
    update_decals(t)
    update_shafts(t)

# ---------------------------------------------------------------------- light (sun, sky, exposure) - one key table
# t: sun elevation (deg), compass azimuth (deg), sun energy, sun rgb, zenith rgb, horizon rgb, world (lighting) strength
LIGHT_KEYS = [
    (0.0,  47.0, 135, 3.6, (1.00, 0.96, 0.90), (0.10, 0.28, 0.75), (0.70, 0.80, 0.93), 1.00),   # clear late morning
    (12.0, 47.0, 136, 3.5, (1.00, 0.96, 0.90), (0.12, 0.29, 0.72), (0.72, 0.80, 0.90), 1.00),
    (19.0, 47.5, 137, 2.4, (0.98, 0.95, 0.92), (0.22, 0.30, 0.50), (0.66, 0.70, 0.76), 0.92),   # cloud roll-in
    (26.0, 48.0, 138, 1.0, (0.90, 0.93, 1.00), (0.30, 0.34, 0.40), (0.56, 0.59, 0.63), 0.80),   # dark overcast at E
    (48.0, 48.5, 140, 0.95, (0.90, 0.93, 1.00), (0.30, 0.34, 0.40), (0.56, 0.59, 0.63), 0.80),
    (54.0, 48.5, 141, 1.9, (1.00, 0.92, 0.80), (0.34, 0.42, 0.55), (0.70, 0.70, 0.68), 0.88),   # breaking overcast, shafts
    (70.0, 49.0, 143, 2.1, (1.00, 0.92, 0.80), (0.33, 0.42, 0.56), (0.70, 0.70, 0.68), 0.90),
]
# colour grade (the toon pass maps lighting to fixed bands, so overcast / warmth come from a global grade):
# t: (gain r, g, b), exposure offset (stops)
GRADE_KEYS = [
    (0.0,  (1.00, 1.00, 1.00), 0.00),
    (12.0, (1.00, 1.00, 1.00), 0.00),
    (19.0, (0.95, 0.97, 1.02), -0.30),
    (26.0, (0.86, 0.93, 1.06), -0.78),    # dark overcast at E: cooler, much darker
    (48.0, (0.86, 0.93, 1.06), -0.78),
    (54.0, (1.00, 0.97, 0.92), -0.32),    # breaking overcast, warm shafts
    (70.0, (1.01, 0.98, 0.93), -0.25),
]

def _keyed(K, t, n):
    if t <= K[0][0]: return K[0], K[0], 0.0
    for a, b in zip(K, K[1:]):
        if a[0] <= t < b[0]:
            return a, b, ss(a[0], b[0], t)
    return K[-1], K[-1], 0.0

def _light_capture():
    sc = bpy.context.scene
    suns = [o for o in bpy.data.objects if o.type == "LIGHT" and o.data.type == "SUN"]
    w = sc.world
    nodes = w.node_tree.nodes if (w and w.use_nodes) else []
    STATE["light0"] = dict(suns=suns, exp0=sc.view_settings.exposure,
                           ramps=[n for n in nodes if n.type == "VALTORGB"], skies=[n for n in nodes if n.type == "TEX_SKY"],
                           bgs=[(n, n.inputs[1].default_value) for n in nodes if n.type == "BACKGROUND"])

def light(t):
    t = float(t)
    a, b, u = _keyed(LIGHT_KEYS, t, 8)
    def mix(i):
        x, y = a[i], b[i]
        if isinstance(x, tuple):
            return tuple(lerp(p, q, u) for p, q in zip(x, y))
        return lerp(x, y, u)
    def sdir(k):
        el, az = math.radians(k[1]), math.radians(k[2])
        return np.array([math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el)])
    d = sdir(a) * (1 - u) + sdir(b) * u; d /= np.linalg.norm(d)
    L0 = STATE["light0"]
    en = mix(3); col = mix(4); zen = mix(5); hor = mix(6); ws = mix(7)
    f = flicker(t)
    k_en, k_ws, ex_f = 1.0, 1.0, 0.0
    tint = (1.0, 1.0, 1.0)
    if f in ("spike0", "spike1"):
        k_en, k_ws, ex_f = 1.8, 2.6, 0.75; tint = (1.08, 1.0, 0.62)
    elif f == "dark":
        k_en, k_ws, ex_f = 0.05, 0.05, -4.0
    elif 0.27 <= t < 0.9:
        w = 1 - ss(0.27, 0.9, t); tint = (1.0 + 0.05 * w, 1.0, 1.0 - 0.3 * w)       # green-gold cast fading
    for o in L0["suns"]:
        o.rotation_euler = Vector(tuple(-d)).to_track_quat("-Z", "Y").to_euler()
        o.data.energy = en * k_en; o.data.color = col
    for r in L0["ramps"]:
        el = r.color_ramp.elements
        el[0].color = (*hor, 1); el[-1].color = (*zen, 1)
    for s in L0["skies"]:
        try:
            s.sun_elevation = math.radians(mix(1)); s.sun_rotation = math.atan2(d[1], d[0])
        except Exception:
            pass
    for n, s0 in L0["bgs"]:
        n.inputs[1].default_value = s0 * ws * k_ws
    ga, gb, gu = _keyed(GRADE_KEYS, t, 2)
    gain = tuple(lerp(p, q, gu) * tt for p, q, tt in zip(ga[1], gb[1], tint)); gex = lerp(ga[2], gb[2], gu)
    vs = bpy.context.scene.view_settings
    vs.exposure = L0["exp0"] + gex + ex_f
    try:
        vs.use_curve_mapping = True
        cm = vs.curve_mapping
        cm.white_level = tuple(1.0 / max(g, 1e-3) for g in gain)
        cm.black_level = (0.0, 0.0, 0.0)
        cm.update()
    except Exception as ex_:
        if not STATE.get("grade_warned"):
            say("colour grade failed:", ex_); STATE["grade_warned"] = True
    update_cloud_shadows(t, d)

# ====================================================================== HUD trackers (M) + self checks
def _p_set_to_M(p):
    return (float(p[0]), float(p[1]) + segtime.SET_OFF_Y, float(p[2]))

def _sq(name, t0=-1e9, t1=1e9):
    def f(t):
        if not (t0 <= t < t1): return None
        st = STATE["SQ"].state(name, t)
        return _p_set_to_M(st["pos"] + np.array([0, 0, 2.0])) if st["vis"] > 0 else None
    return f

def _mikasa(t):
    return _sq("mikasa")(t) if t < BEATS["mikasa_sw"] + 1.5 else _sq("mikasa2")(t)

def _at_head(t):
    st = at_state(t)
    if not st["vis"]: return None
    return (float(st["pos"][0]), float(st["pos"][1]), 16.0)

TRACK = {"Eren": lambda t: _sq("eren")(t) if t < BEATS["bt_torn"] else None, "Mikasa": _mikasa, "Armin": _sq("armin"),
         "Connie": _sq("connie"), "AttackTitan": _at_head}

def check():
    """Self checks: <= 3 titans abreast in the hole and their spacing, the AT hand-off (position / heading / speed at 70.0),
    the crowd count, camera never south of the wall while the Colossal shows."""
    TT = STATE.get("TT")
    if TT is not None:
        worst = 0; wt = None; mind = 1e9
        for t in np.arange(BEATS["kick"], BEATS["pour"][1] + 4, 0.1):
            R = TT.poses(float(t)); pos = R[5]; vis = R[3]
            P_ = np.column_stack([pos[:, 0], pos[:, 1] + segtime.SET_OFF_Y])
            inside = np.where((vis > 0) & (np.abs(P_[:, 0]) < 8) & (P_[:, 1] > -6) & (P_[:, 1] < 12))[0]
            for i in inside:
                ab = sum(1 for j in inside if abs(P_[j, 1] - P_[i, 1]) < 3.0)
                if ab > worst:
                    worst, wt = ab, round(float(t), 1)
                for j in inside:
                    if i < j and abs(P_[i, 0] - P_[j, 0]) < 2.5:
                        mind = min(mind, abs(float(P_[i, 1] - P_[j, 1])))
        say(f"CHECK breach: max {worst} titans abreast (t {wt}); min nose-to-tail centre spacing in a lane {mind:.1f} m")
    if TT is not None:
        for nm, ts_ in (("AB", (24.4, 26.0, 30.0, 33.8, 34.6)), ("CAP", (53.4, 55.0, 56.2, 57.9)), ("LH", (54.0, 55.6)), ("CC", (60.0, 63.6, 65.7, 66.4)),
                        ("BT", (54.0, 56.0)), (STATE["pour"][0][0], (7.0, 10.0, 15.0)), (STATE["pour"][2][0], (8.0, 15.0, 26.0))):
            say("CHECK", nm, [(t_, tuple(np.round(titan_M(nm, t_), 1)), round(float(TT.poses(t_)[3][TT.j(nm)]), 2)) for t_ in ts_])
    st = at_state(DUR - 1e-3); v = at_vel(DUR - 0.06, 0.05)
    hd = (math.degrees(math.atan2(v[0], v[1])) + 360) % 360
    say(f"CHECK AT at {DUR}: pos {tuple(np.round(st['pos'], 1))} heading {hd:.0f} deg speed {np.linalg.norm(v):.1f} m/s "
        f"(seam: {AT_END} {AT_END_HEADING} deg {AT_END_V} m/s)")
    if STATE.get("crowd"):
        say(f"CHECK crowd: {STATE['crowd']['n']} people")
    south = [t for t in np.arange(0, BEATS["col_fade"][1], 0.1) if CAM.eval(float(t))[0][1] < 10.0]
    say(f"CHECK camera south of the wall while the Colossal shows: {len(south)} samples")

if __name__ == "__main__":
    r = camchan.check(CAM, 0.0, DUR, limits=dict(name="g5 CAM", **CAM_LIMITS))
    for t in (69.9, 70.0):
        print(t, at_state(t)["pos"], at_vel(t - 0.06))
