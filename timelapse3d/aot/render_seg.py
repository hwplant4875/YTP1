"""GENERIC TROST SEGMENT DRIVER (AGENTS_BRIEF "WAVE v2"): builds the trost.py set once, imports aot/seg_<SEG>.py and renders
its frames as a pure function of the segment's LOCAL time t.  Run after scene.py in the same Blender session (render_seg.sh):

    AOT_SET=trost blender -b -P aot/scene.py -P aot/render_seg.py -- --cam trost_overview --engine BLENDER_EEVEE \
        --res 854x480 --seg g8 --seg-out DIR [--t0 0 --t1 25] [--step 2] [--fps 15] [--stills 12,30] [--dry] [--check]

Segment module contract (aot/seg_<id>.py):
    DUR        segment length in seconds (local t runs 0..DUR; normally segtime.DUR[id])
    BEATS      dict of beat name -> time or (t0, t1) (ONE table at the top of the module: a re-time is a one-place edit)
    CAM        camchan.CamPath in frame M (outer gate O = (0, 0), Rose Y 870); the driver converts to set coords (X, Y-870, Z)
    build(site)          once (site: dict, see make_site below)
    update(t)            every frame, a pure function of t
    light(t)             every frame (sun, sky, exposure)
  optional:
    TRACK      dict  HUD tag name -> fn(t) -> (x, y, z) in M or None   (hudcam.dump trackers; hud2 draws the tags)
    CAM_LIMITS dict  overrides for camchan.check (e.g. dict(hmin=89))
    check()    extra self checks (collision etc.), printed by --check / --dry
    finish()   called once after toon.apply() (material tweaks that must survive the toon pass)
    cam_shake(t) -> (pitch, yaw) radians added to the camera (short impact shakes)

VIDEO CLOCK (--vclock, render_seg.sh VCLOCK=1, owner 10/27 "2x faster", 30 fps): frames / --t0 / --t1 / --stills are in
video seconds tv; the segment is evaluated at t = segtime.seg_t(seg, tv) (default t = 2 tv; per-segment TMAP knots).
Frames: <seg-out>/f_<global frame index>.png with index = round(t * fps); STEP > 1 renders every STEP-th frame
(render_seg.sh repeats frames before encoding).  Missing frames are resumed after a crash.  hudcam JSON per frame in _cam/.
"""
import bpy, math, os, sys, time, argparse, importlib
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ap = argparse.ArgumentParser(allow_abbrev=False)
ap.add_argument("--seg", required=True)
ap.add_argument("--seg-out", required=True)
ap.add_argument("--fps", type=float, default=15.0)
ap.add_argument("--t0", type=float, default=0.0)
ap.add_argument("--t1", type=float, default=1e9)
ap.add_argument("--step", type=int, default=1)
ap.add_argument("--seg-samples", type=int, default=1)
ap.add_argument("--stills", default="")
ap.add_argument("--dry", action="store_true")
ap.add_argument("--check", action="store_true", help="print camchan.check + the module's check() and exit")
ap.add_argument("--vclock", action="store_true", help="frames, --t0/--t1 and --stills on the VIDEO clock (segtime.seg_t)")
B, _ = ap.parse_known_args(argv)

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import aotlib as L
import camchan
# OPT-IN (g2 agent, 10/27): SEG_FRAME=W renders a Shiganshina-frame segment (g1/g2) on scene.py's own Shiganshina set
# (no AOT_SET, render_seg.sh SEG_SET=shiganshina): the module's CAM / TRACK are in frame W, M2S is the identity, the
# ground is scene.py's height(), and the trost-only "Haze" hiding is skipped.  Default (unset) = unchanged Trost path.
FRAME_W = os.environ.get("SEG_FRAME", "M").upper() == "W"
TR = None if FRAME_W else (sys.modules.get("trost") or importlib.import_module("trost"))

SET_DY = 870.0
def M2S(p):
    """Trost master frame M -> trost.py set frame (SEG_FRAME=W: identity)."""
    if FRAME_W:
        return Vector((float(p[0]), float(p[1]), float(p[2]) if len(p) > 2 else 0.0))
    if hasattr(TR, "M"):
        try:
            return Vector(TR.M(float(p[0]), float(p[1]), float(p[2]) if len(p) > 2 else 0.0))
        except Exception:
            pass
    return Vector((float(p[0]), float(p[1]) - SET_DY, float(p[2]) if len(p) > 2 else 0.0))

def ground_M(x, y):
    """Terrain / paving height at M (x, y) (SEG_FRAME=W: scene.py height at W (x, y))."""
    if FRAME_W:
        return float(L.height(x, y))
    xs, ys = x, y - SET_DY
    if hasattr(TR, "ground_z"):
        try:
            return float(TR.ground_z(xs, ys))
        except Exception:
            pass
    return float(L.height(xs, ys))

def make_site():
    return dict(TR=TR, L=L, M2S=M2S, ground_M=ground_M, set_dy=SET_DY, fps=B.fps, out=B.seg_out)

t_start = time.time()
SEG = importlib.import_module("seg_" + B.seg)
print(f"[seg] segment {B.seg}: DUR {SEG.DUR} s, {len(SEG.BEATS)} beats")

# ------------------------------------------------------------------ render settings (as render_trost.py)
sc = bpy.context.scene
cam = sc.camera
if cam is None:                           # scene.py's --cam may not exist in this set: make our own camera
    cd = bpy.data.cameras.new("SegCam"); cam = bpy.data.objects.new("SegCam", cd); sc.collection.objects.link(cam)
    sc.camera = cam
cam.data.clip_start = 0.5
cam.data.clip_end = 30000
if sc.render.engine.startswith("BLENDER_EEVEE"):
    ev = sc.eevee
    ev.taa_render_samples = max(1, B.seg_samples)
    for k_, v_ in (("use_shadows", True), ("shadow_pool_size", "1024"), ("shadow_resolution_scale", 1.0),
                   ("shadow_ray_count", 1), ("shadow_step_count", 6), ("use_raytracing", True), ("ray_tracing_method", "SCREEN"),
                   ("use_fast_gi", True), ("fast_gi_method", "AMBIENT_OCCLUSION_ONLY"), ("fast_gi_distance", 6.0),
                   ("fast_gi_quality", 0.25), ("fast_gi_resolution", "4")):
        try:
            setattr(ev, k_, v_)
        except Exception as ex_:
            print("[seg] eevee setting", k_, "failed:", ex_)
    for o in bpy.data.objects:
        if o.type == "LIGHT" and o.data.type == "SUN":
            for k_, v_ in (("use_shadow", True), ("angle", math.radians(1.2)), ("shadow_maximum_resolution", 0.02),
                           ("use_shadow_jitter", False), ("shadow_filter_radius", 1.5)):
                try:
                    setattr(o.data, k_, v_)
                except Exception:
                    pass
else:
    cy = sc.cycles
    cy.samples = B.seg_samples; cy.use_adaptive_sampling = True; cy.use_denoising = True
    sc.render.use_simplify = True; sc.render.simplify_subdivision_render = 0
sc.render.use_persistent_data = True
for n in (() if FRAME_W else ("Haze",)):  # Eevee smears the giant haze volume; the set's mist pass carries the depth
    o = bpy.data.objects.get(n)
    if o:
        o.hide_render = True
sc.render.image_settings.file_format = "PNG"
os.makedirs(B.seg_out, exist_ok=True)

# ------------------------------------------------------------------ segment build
SITE = make_site()
t0 = time.time()
SEG.build(SITE)
print(f"[seg] {B.seg}.build {time.time() - t0:.1f}s")

import toon
toon.apply()                              # project toon look (TOON=0 disables) after every material exists
if hasattr(SEG, "finish"):
    SEG.finish()

# debug stills only: SEG_CAMDBG="x,y,z,lx,ly,lz,lens" (M) overrides CAM for every still, or per still time:
# SEG_CAMDBG="22.5@215,225,45,283,221,12,40;40@55,80,40,112,39,12,40"
CAMDBG = {}
for _e in filter(None, os.environ.get("SEG_CAMDBG", "").split(";")):
    _k, _v = _e.split("@") if "@" in _e else ("*", _e)
    CAMDBG[_k if _k == "*" else round(float(_k), 3)] = [float(x) for x in _v.split(",")]
def cam_at(t):
    loc, look, lens = SEG.CAM.eval(min(max(t, SEG.CAM.t0), SEG.CAM.t1))
    v = CAMDBG.get(round(t, 3), CAMDBG.get("*"))
    if v:
        loc, look, lens = v[0:3], v[3:6], v[6]
    loc, look = M2S(loc), M2S(look)
    if os.environ.get("SEG_CAMPRINT"):           # autopilot debug
        print(f"[seg] cam t={t:.3f} loc={tuple(round(float(v), 1) for v in loc)} look={tuple(round(float(v), 1) for v in look)} lens={lens:.1f}", flush=True)
    rot = (look - loc).to_track_quat("-Z", "Y").to_euler()
    if hasattr(SEG, "cam_shake"):                  # optional: SEG.cam_shake(t) -> (pitch, yaw) radians (impacts)
        dx, dz = SEG.cam_shake(t)
        rot.x += dx; rot.z += dz
    return loc, rot, lens

def run_checks():
    lim = dict(name=f"{B.seg} CAM")
    lim.update(getattr(SEG, "CAM_LIMITS", {}))
    r = camchan.check(SEG.CAM, 0.0, SEG.DUR, ground=lambda x, y: ground_M(x, y), limits=lim)
    if hasattr(SEG, "check"):
        SEG.check()
    return r

import hudcam
TRACK = getattr(SEG, "TRACK", {})
TRK = {}
for nm in TRACK:
    o = bpy.data.objects.new(nm, None); sc.collection.objects.link(o); TRK[nm] = o

def trackers(t):
    for nm, fn in TRACK.items():
        p = None
        try:
            p = fn(t)
        except Exception as ex_:
            print("[seg] tracker", nm, "failed:", ex_)
        TRK[nm].location = tuple(M2S(p)) if p is not None else (0.0, 0.0, -1000.0)

import segtime
VDUR = segtime.vdur(B.seg) if B.vclock else SEG.DUR
def local_t(tv):
    """video time -> segment local time (identity without --vclock)."""
    return segtime.seg_t(B.seg, tv) if B.vclock else tv

def frame_state(t):
    SEG.update(t)
    SEG.light(t)
    loc, rot, lens = cam_at(t)
    cam.location = loc; cam.rotation_euler = rot; cam.data.lens = lens
    trackers(t)

print(f"[seg] setup total {time.time() - t_start:.1f}s")
if B.check or B.dry:
    run_checks()
if B.check:
    sys.exit(0)
if B.dry:
    for t in [x * 2.5 for x in range(int(SEG.DUR / 2.5) + 1)]:
        tu = time.time(); frame_state(t)
        print(f"[seg] dry t={t:5.1f} cam={tuple(round(c) for c in cam.location)} lens={cam.data.lens:.1f} update {time.time() - tu:.2f}s")
    sys.exit(0)

if B.stills:
    jobs = [(float(x), f"still_{B.seg}_{float(x):05.1f}.png") for x in B.stills.split(",") if x.strip()]   # video s with --vclock
else:
    n0 = int(math.ceil(B.t0 * B.fps - 1e-6)); n1 = int(math.floor(min(B.t1, VDUR) * B.fps - 1e-6)) + 1
    jobs = [(f / B.fps, f"f_{f:05d}.png") for f in range(n0, n1) if f % B.step == 0]
    jobs = [j for j in jobs if not os.path.exists(os.path.join(B.seg_out, j[1]))]      # resume after a crash
print(f"[seg] {len(jobs)} frames to render")
tr = time.time()
for i, (tv, fn) in enumerate(jobs):
    tu = time.time()
    t = local_t(tv)
    frame_state(t)
    tu = time.time() - tu
    sc.render.filepath = os.path.join(B.seg_out, fn)
    bpy.context.view_layer.update()
    try:
        hudcam.dump(sc, int(round(tv * B.fps)), B.seg_out, t=tv, track=tuple(TRK), name=None if not B.stills else fn[:-4])
    except Exception as ex_:
        print("[seg] hudcam failed:", ex_)
    bpy.ops.render.render(write_still=True)
    el = time.time() - tr
    print(f"[seg] {i + 1}/{len(jobs)} tv={tv:.2f} t={t:.2f} -> {fn} ({el:.0f}s, {el / (i + 1):.2f}s/f, update {tu:.2f}s)", flush=True)
if not B.stills:
    open(os.path.join(B.seg_out, f"_done_{B.t0:g}_{B.t1:g}"), "w").write("%d frames" % len(jobs))
