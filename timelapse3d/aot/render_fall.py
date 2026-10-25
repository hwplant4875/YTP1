"""Segment 2: the fall (picks up where render_fast.py ends, video 13.0 s = 2.0 s after the kick), ONE Blender session.

Segment time s (0 = video 13.0 s), ~15.5 s:
  0-7.5 s   TIMELAPSE: sim time after the kick runs 2 -> 60 s on an S-curve (real speed at both ends).
            Houses collapse under the stones with dust (fx845.update), the plaza crowd panics and runs, the
            pure titans pour through the breach and start eating (swarm845.update).  Sky camera 85-150 m,
            continuing from render_fast's last key, then flying north-west to the Yeager street.
  7.5-15.5  the Carla beat (seq_carla.pose_carla(F), F mapped non-linearly): kids at the beam, Hannes arrives,
            charges, freezes, scoops the kids, runs; the Smiling Titan lifts Carla; the "Yamero" hold (~2 s,
            F 2515-2585, Eren facing back, arm over Hannes's shoulder); pull-away.  The light blends to sunset
            over s 5-8.  Swarm keeps running at real speed (sim t = 60 + (s - 7.5)).
Every frame is a pure function of s (camera, fx t, swarm t, carla F, light), so any frame or still renders alone.
Run after scene.py (see render_fall.sh):
  blender -b -P aot/scene.py -P aot/render_fall.py -- --cam seq... --fall-out DIR [--fps 15] [--times 1,5,9]
Duplicate crowds / titans are simply not loaded (no seq_colossal, render_fast crowd, cast845); the swarm's own
blocky Smiling Titan is hidden because seq_carla's MPFB Smiling Titan plays the beat.
"""
import bpy, math, os, sys, time, argparse
import numpy as np
from mathutils import Vector, noise

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ap = argparse.ArgumentParser()
ap.add_argument("--fall-out", required=True)
ap.add_argument("--fps", type=float, default=30.0)
ap.add_argument("--s0", type=float, default=0.0)
ap.add_argument("--s1", type=float, default=10.6)
ap.add_argument("--fall-samples", type=int, default=2)
ap.add_argument("--times", default="", help="comma list of segment times (stills) instead of s0..s1")
ap.add_argument("--index0", type=int, default=-1, help="first frame number (default round(s0 * fps))")
B, _ = ap.parse_known_args(argv)

import aotlib as L
SW = sys.modules.get("swarm845")
FX = sys.modules.get("fx845")
SC = sys.modules.get("seq_carla")
A_END = 7.5                      # timelapse part ends, Carla beat begins
SEG_END = 10.6
T_SIM0, T_SIM1 = 2.0, 60.0       # sim time (s after the kick) over the timelapse part

def smooth(a, b, t):
    u = min(1.0, max(0.0, (t - a) / (b - a))); return u * u * (3 - 2 * u)

# ---------------------------------------------------------------- time maps
def sim_t(s):
    """Seconds after the kick for segment time s: S-curve 2 -> 60 over 0-7.5 with real speed at both ends."""
    if s <= 0:
        return T_SIM0 + s
    if s >= A_END:
        return T_SIM1 + (s - A_END)
    u = s / A_END; d = A_END / (T_SIM1 - T_SIM0)
    h10, h01, h11 = u ** 3 - 2 * u ** 2 + u, -2 * u ** 3 + 3 * u ** 2, u ** 3 - u ** 2
    return T_SIM0 + (T_SIM1 - T_SIM0) * (h10 * d + h01 + h11 * d)

def _pchip_m(T, S):
    D = [(S[i + 1] - S[i]) / (T[i + 1] - T[i]) for i in range(len(T) - 1)]
    return [D[0]] + [0.0 if D[i - 1] * D[i] <= 0 else 2 * D[i - 1] * D[i] / (D[i - 1] + D[i]) for i in range(1, len(D))] + [D[-1]]

def _pchip(T, S, m, t):
    t = min(max(t, T[0]), T[-1])
    i = min(len(T) - 2, max(j for j in range(len(T)) if T[j] <= t))
    h = T[i + 1] - T[i]; s = (t - T[i]) / h
    h00, h10, h01, h11 = 2 * s ** 3 - 3 * s ** 2 + 1, s ** 3 - 2 * s ** 2 + s, -2 * s ** 3 + 3 * s ** 2, s ** 3 - s ** 2
    return h00 * S[i] + h10 * h * m[i] + h01 * S[i + 1] + h11 * h * m[i + 1]

# segment time -> seq_carla frame (30 fps numbering). Brisk, except the Yamero hold (~1.2x real).
F_KEYS = [(0.0, 2150), (A_END, 2330), (A_END + 1.0, 2440), (A_END + 1.7, 2515), (A_END + 2.5, 2575), (SEG_END, 2610)]   # Carla fast (user 10/25)
_FM = _pchip_m([k[0] for k in F_KEYS], [k[1] for k in F_KEYS])
def carla_f(s):
    return _pchip([k[0] for k in F_KEYS], [k[1] for k in F_KEYS], _FM, s)

# ---------------------------------------------------------------- camera
PLZ = Vector(L.PLAZA[:2]); GX, GY = L.OUTER_GATE
def _carla_cam(f):
    if SC and SC.STATE.get("C") is not None:
        l, t, n = SC.cam_at(f)
        return tuple(l), tuple(t), n
    return (-40.0, -60.0, 40.0), (-72.0, -118.0, 0.0), 32.0

def a_keys():
    """Timelapse-part keys (s, loc, look_at, lens); the first is render_fast.py's last key (video 13.0 s)."""
    return [
        (-1.0, (PLZ.x + 50, PLZ.y + 45, 146), (GX, GY + 100, 0), 38),        # (extrapolation guide only)
        (0.0, (PLZ.x + 55, PLZ.y + 50, 150), (GX, GY + 120, 0), 38),         # = render_fast keys()[-1]
        (2.4, (PLZ.x + 32, PLZ.y + 70, 92), (PLZ.x, PLZ.y - 30, 0), 34),     # down over the panicking plaza
        (4.6, (30, GY + 120, 105), (0, GY + 10, 0), 32),                     # the titans pouring through the breach
        # then a smooth aerial travel right (east) to the Yeager house (AOT_YEAGER_XY, ~210 m from the gate), where the
        # Smiling Titan eats Carla: neutral sky observer, no close-up, no Hannes / kids, no other titans nearby
        (6.6, (118, GY + 40, 100), (158, GY + 132, 0), 32),
        (A_END, (126, GY + 44, 94), (162, GY + 134, 0), 32),
        (SEG_END, (132, GY + 48, 90), (164, GY + 136, 0), 32),
        (SEG_END + 1.0, (132, GY + 48, 90), (164, GY + 136, 0), 32),      # (guide: the seam into render_fall2 is at rest)
    ]

def _cr(p0, p1, p2, p3, u, t0, t1, t2, t3):
    """Non-uniform Catmull-Rom (time-parametrised) segment p1->p2."""
    m1 = ((p2 - p1) / (t2 - t1) + (p1 - p0) / (t1 - t0)) * 0.5 * (t2 - t1)
    m2 = ((p3 - p2) / (t3 - t2) + (p2 - p1) / (t2 - t1)) * 0.5 * (t2 - t1)
    h00, h10, h01, h11 = 2 * u ** 3 - 3 * u ** 2 + 1, u ** 3 - 2 * u ** 2 + u, -2 * u ** 3 + 3 * u ** 2, u ** 3 - u ** 2
    return p1 * h00 + m1 * h10 + p2 * h01 + m2 * h11

_KS = []
def cam_at(s):
    """One spline for the whole segment (sky observer); ends at rest = render_fall2's first key."""
    return _spline_a(s)

def _carla_part(s):
    F = carla_f(s)
    loc, tgt, lens = SC.cam_at(F)
    loc, tgt = Vector(loc), Vector(tgt)
    w = smooth(2415, 2465, F)
    if w > 0:                                      # Yamero framing (see yamero_cam)
        y_loc, y_tgt, y_lens = yamero_cam(F)
        loc, tgt, lens = loc.lerp(y_loc, w), tgt.lerp(y_tgt, w), lens + (y_lens - lens) * w
    return loc, tgt, lens

def _spline_a(s):
    if not _KS:
        _KS.extend(a_keys())
    ks = _KS
    i = max(j for j in range(1, len(ks) - 2) if ks[j][0] <= s) if s >= ks[1][0] else 1
    q = [ks[j] for j in (i - 1, i, i + 1, i + 2)]
    u = (s - q[1][0]) / (q[2][0] - q[1][0])
    T = [k[0] for k in q]
    loc = _cr(*[Vector(k[1]) for k in q], u, *T)
    tgt = _cr(*[Vector(k[2]) for k in q], u, *T)
    lens = math.exp(_cr(*[math.log(k[3]) for k in q], u, *T))
    return loc, tgt, lens

def yamero_cam(F):
    """Yamero framing: low (~6 m up), ~20-30 m from Hannes as he runs at us (+u) with the kids (Eren facing back, arm
    stretched toward Carla), the Smiling Titan behind lifting her against the golden sky; slow pull-away.
    (seq_carla's own S14 camera sat behind the ruined gable and hid Carla.)"""
    St = SC.STATE; u, fv = St["u"], St["f"]
    g = L.height(St["C"].x, St["C"].y)
    hp = lambda ff: SC.hannes_xy(ff)[0]
    H = (hp(F - 8) + hp(F) * 2 + hp(F + 8)) / 4.0
    pull = smooth(2585, 2625, F)
    back = float(os.environ.get("FALL_YAM_BACK", "8")) + 4 * pull
    up = float(os.environ.get("FALL_YAM_UP", "5")) + 2 * pull
    T = St["T1"]
    loc2 = H + u * back - fv * float(os.environ.get("FALL_YAM_SIDE", "5"))
    loc = Vector((loc2.x, loc2.y, g + up))
    d = (T - loc2).normalized()                      # look along the line to the titan, pitched ~4 deg down:
    pitch = math.radians(float(os.environ.get("FALL_YAM_PITCH", "-1")))   # Hannes low in frame, Carla high
    tgt = loc + Vector((d.x * math.cos(pitch), d.y * math.cos(pitch), math.sin(pitch))) * 20.0
    return loc, tgt, float(os.environ.get("FALL_YAM_LENS", "16"))

_FIRE = []
_FIRE_OUT, _FIRE_BASE = {}, {}
def fire_tune():
    """The Yeager-house fire: flames x0.45, its smoke billows x1.5 (user: smaller and smokier)."""
    if not _FIRE:
        C = SC.STATE["C"]
        for o in bpy.data.objects:
            if o.name.startswith(("Flame", "FlameSmoke")) and (o.matrix_world.translation.to_2d() - C).length < 30:
                _FIRE.append((o, 1.5 if o.name.startswith("FlameSmoke") else 0.45))
        _FIRE.append(None)
    for it in _FIRE:
        if it:
            o, k = it
            cur = tuple(o.scale)
            if _FIRE_OUT.get(o.name) == cur:          # fx845 did not reset it this frame: undo our last change
                cur = _FIRE_BASE[o.name]
            _FIRE_BASE[o.name] = cur
            o.scale = tuple(v * k for v in cur)
            _FIRE_OUT[o.name] = tuple(o.scale)

def pscale(s):
    return float(os.environ.get("FALL_PSCALE", "1.0"))          # user rule: every human at true scale

# ---------------------------------------------------------------- light: daylight (opening) -> sunset (Carla)
def light_setup():
    so = bpy.data.objects.get("Sun")
    st = {"sun": so}
    if so:
        st["d0"] = so.matrix_world.to_3x3() @ Vector((0, 0, -1)); st["e0"] = so.data.energy; st["c0"] = Vector(so.data.color)
        el = math.radians(float(os.environ.get("FALL_SUN_EL", "4")))
        az = math.radians(float(os.environ.get("FALL_SUN_AZ", "245")))   # shared with render_fall2 (seam match)
        st["d1"] = Vector((-math.cos(el) * math.cos(az), -math.cos(el) * math.sin(az), -math.sin(el)))
        st["e1"] = float(os.environ.get("CARLA_SUN_E", "4.2")); st["c1"] = Vector(tuple(float(v) for v in os.environ.get("FALL_SUN_COL", "1.0,0.78,0.58").split(",")))   # = render_fall2 SUN_COL
    w = bpy.context.scene.world
    st["ramp"] = []
    if w and w.use_nodes:
        for n in w.node_tree.nodes:
            if n.type == "VALTORGB":
                e = n.color_ramp.elements
                st["ramp"].append((e[0], Vector(e[0].color), Vector((1.0, 0.62, 0.22, 1)), e[1], Vector(e[1].color), Vector((0.95, 0.66, 0.38, 1))))
    return st

def light_at(st, s):
    k = smooth(6.8, 8.0, s)
    so = st["sun"]
    if so:
        d = st["d0"].lerp(st["d1"], k).normalized()
        so.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
        so.data.energy = st["e0"] + (st["e1"] - st["e0"]) * k
        so.data.color = tuple(st["c0"].lerp(st["c1"], k))
    for e0, a0, b0, e1, a1, b1 in st["ramp"]:
        e0.color = tuple(a0.lerp(b0, k)); e1.color = tuple(a1.lerp(b1, k))

# ---------------------------------------------------------------- render settings (mirror render_fast's preview mode)
sc = bpy.context.scene
cam = sc.camera
sc.cycles.samples = B.fall_samples; sc.cycles.use_adaptive_sampling = True
if sc.render.engine.startswith("BLENDER_EEVEE"):
    sc.eevee.taa_render_samples = int(os.environ.get("FALL_EEVEE_SAMPLES", "8"))
    for o in bpy.data.objects:                       # dozens of fire lights overflow Eevee's shadow pool: no shadows
        if o.type == "LIGHT" and o.name.startswith(("FireL", "FX_Flash")):
            o.data.use_shadow = False
elif os.environ.get("FAST_PREVIEW", "0") == "1":
    cy = sc.cycles
    cy.use_denoising = True
    try:
        cy.denoiser = "OPENIMAGEDENOISE"; cy.denoising_use_gpu = True
    except Exception:
        pass
    cy.max_bounces, cy.diffuse_bounces, cy.glossy_bounces, cy.transmission_bounces = 3, 1, 1, 2
    cy.volume_bounces = 0; cy.transparent_max_bounces = 12; cy.caustics_reflective = cy.caustics_refractive = False
    cy.volume_step_rate = float(os.environ.get("FALL_VSTEP", "16")); cy.volume_max_steps = int(os.environ.get("FALL_VMAX", "48"))
    sc.render.use_persistent_data = True
    sc.render.use_simplify = True; sc.render.simplify_subdivision_render = 0
    cy.texture_limit_render = "1024"
    for ob in bpy.data.objects:
        if ob.name == "Haze" or (ob.type == "MESH" and any(m and m.name.startswith("FL_Rays") for m in ob.data.materials)):
            ob.hide_render = True
sc.render.image_settings.file_format = "PNG"
os.makedirs(B.fall_out, exist_ok=True)
# duplicate crowds / titans (only present if someone loaded those plug-ins anyway)
for n in ("PlazaCrowd",):
    o = bpy.data.objects.get(n)
    if o:
        o.hide_render = True
for c in ("PK_People",):
    cc = bpy.data.collections.get(c)
    if cc:
        cc.hide_render = True
col = bpy.data.collections.get("ColossalTitan")
if col:
    col.hide_render = True
if SW:
    SW.HIDE_TITANS = {"smiling"}
LST = light_setup()
# the big smoke columns over the breach / the Yeager ruin hide the beat at ~95 m: move them off to the east
_cx = SC.STATE["C"] if SC and SC.STATE.get("C") is not None else Vector((-48.0, -640.0))
for o in bpy.data.objects:
    if o.name.startswith(("FireSmoke", "FlameSmoke")):
        p2 = o.matrix_world.translation.to_2d()
        if (p2 - _cx).length < 110 or (p2 - Vector((GX, GY))).length < 110:
            o.location.x += float(os.environ.get("FALL_SMOKE_DX", "150"))
print(f"[fall] swarm {'on' if SW and SW.STATE else 'off'}, fx845 {'on' if FX else 'off'}, carla {'on' if SC and SC.STATE.get('C') is not None else 'off'}")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    import hudcam
except Exception as ex:
    hudcam = None; print("[fall] hudcam unavailable:", ex)
TAGS = {"Carla": "Carla", "Smiling Titan": "CarlaSmiling"}
def hud_dump(key, s):
    """Camera + name-tag anchors for hud2.py (<out>/_cam/<frame>.json); tags during the Carla beat (rig origin = feet)."""
    if not hudcam:
        return
    tr = [v for v in TAGS.values() if bpy.data.objects.get(v)] if s >= A_END - 1.0 else []
    hudcam.dump(sc, key if isinstance(key, int) else 0, B.fall_out, t=s, track=tr, name=None if isinstance(key, int) else key,
                extra={"segment": "fall", "labels": {k: v for k, v in TAGS.items() if v in tr}, "anchor": "rig origin = feet"})

if B.times:
    times = [float(x) for x in B.times.split(",") if x.strip()]
else:
    times = [(int(round(B.s0 * B.fps)) + j) / B.fps for j in range(int(round((B.s1 - B.s0) * B.fps)))]
t_start = time.time()
for i, s in enumerate(times):
    if os.path.exists(os.path.join(B.fall_out, "STOP")):   # touch <out>/STOP to end a long render cleanly
        print("[fall] STOP file found, ending"); break
    t0 = time.time()
    ts = sim_t(s)
    if FX:
        FX.update(ts)
    if SW and SW.STATE:
        hide = {"smiling"}                          # seq_carla's Smiling Titan plays the beat; keep the block clear
        if SC and SC.STATE.get("C") is not None and s > A_END - 2.5:
            k0 = min(int(ts / SW.DT), SW.STATE["K"] - 1); C2 = SC.STATE["C"]
            dx = SW.STATE["TX"][k0] - C2.x; dy = SW.STATE["TY"][k0] - C2.y
            hide |= set(int(j) for j in np.where(dx * dx + dy * dy < 95.0 ** 2)[0])
        SW.HIDE_TITANS = hide
        SW.update(ts, pscale=pscale(s))
    if SC and SC.STATE.get("C") is not None:
        SC.pose_carla(carla_f(s))
        fire_tune()
    light_at(LST, s)
    loc, tgt, lens = cam_at(s)
    cam.location = loc; cam.rotation_euler = (tgt - loc).to_track_quat("-Z", "Y").to_euler(); cam.data.lens = lens
    i0 = B.index0 if B.index0 >= 0 else int(round(B.s0 * B.fps))
    name = f"fall_{i0 + i:05d}.png" if not B.times else f"fall_s{s:05.2f}.png"
    sc.render.filepath = os.path.join(B.fall_out, name)
    tp = time.time() - t0
    hud_dump(i0 + i if not B.times else name[:-4], s)
    bpy.ops.render.render(write_still=True)
    print(f"[fall] s={s:.2f} sim t={ts:.1f} F={carla_f(s):.0f} -> {name} (pose {tp:.1f}s, frame {time.time() - t0:.1f}s, total {time.time() - t_start:.0f}s)")
