"""CONNECTOR FLIGHTS between EP1 segments (agent G, integrator).  ONE Blender session per scene ("world").

STRICT ONE TAKE (HANDOFF 10/25 09:37): no clouds, wipes or dissolves.  A connector (master_timeline.SEGMENTS, bridge
entries) is one or two spans; each span is a cubic Hermite in time between two keys - a segment key evaluated HERE
with that segment's own camera function (position, velocity, look direction + rate, log-lens + rate), or an explicit
SEAM key (master_timeline.SEAMS, world coordinates converted to this scene's set frame).  Where a connector changes
scene mid-flight the seam is a world-only frame (aot/world.py content only), so both scenes render the same image.
World state is frozen at the segment key time (crowds, seasons); C1 animates the sun (sunset -> night -> day).

Scenes (see render_bridge.sh for the exact environment of each; every one loads aot/world.py):
  shig       scene.py + render_fall2.py executed up to its main block (seg3_build / seg3_pose: A's segment 3)
  interlude  render_interlude.py imported as a library (build / update / cam_at)
  march      scene.py (AOT_SET=trost) + march846.setup / update / cam_at
  trost      scene.py (AOT_SET=trost) + render_trost.py executed up to its render loop (frame_state / cam_at)
  base       whatever scene.py built: --stills only
Options: --halves C2b,C3a  --br-fps 15 (30 final)  --br-keys-only  --br-js 3,10  --stills "name:x,y,z:lx,ly,lz:lens;..."
Output: renders/master/bridges/<id>/br_<j>.png (+ _cam/<j>.json), bridges/keys/<state>_<t>.json (preferred by
master_timeline.py), renders/master/world_stills/<name>__<scene>_<frame>.png.
"""
import bpy, json, math, os, sys, time, argparse
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
import master_timeline as MT
import hudcam

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ap = argparse.ArgumentParser(allow_abbrev=False)
ap.add_argument("--world", required=True, choices=["interlude", "march", "trost", "shig", "base"])
ap.add_argument("--halves", default="", help="comma list like C2a,C3b")
ap.add_argument("--stills", default="", help="name:x,y,z:lx,ly,lz:lens;...  WORLD coordinates (world.py); rendered into renders/master/world_stills")
ap.add_argument("--still-frame", default="", help="frame of the scene for --stills (shig | trost; default world.active_frame())")
ap.add_argument("--br-fps", type=float, default=15.0)
ap.add_argument("--br-samples", type=int, default=4)
ap.add_argument("--br-engine", default="")
ap.add_argument("--br-res", default="854x480")
ap.add_argument("--br-keys-only", action="store_true")
ap.add_argument("--br-js", default="")
G, _ = ap.parse_known_args(argv)
FPS = G.br_fps
HALVES = [(h[:-1], h[-1]) for h in G.halves.split(",") if h.strip()]
for bid, half in HALVES:
    br = MT.SEG[bid]
    assert br["halves"][half]["world"] == G.world, f"{bid}{half} belongs to world {br['halves'][half]['world']}"

def _exec_until(path, marker, extra_globals=None):
    """Run a render script's module-level setup (scene build, functions) but stop before its render loop."""
    src = open(path, encoding="utf8").read()
    k = src.find(marker)
    if k < 0:
        raise RuntimeError(f"marker {marker!r} not found in {path}: the script changed, update render_bridge.py")
    g = {"__name__": "bridge_exec_" + os.path.basename(path)[:-3], "__file__": path}
    if extra_globals:
        g.update(extra_globals)
    exec(compile(src[:k], path, "exec"), g)
    return g

sc = bpy.context.scene
W = {}                               # world hooks: state(t), cam(t) -> (loc, dir, lens), per_frame(t_state, cam)
t_b = time.time()
if G.world == "interlude":
    if "--out" not in argv:
        sys.argv += ["--out", os.path.join(MT.BRIDGES, "_tmp_interlude")]
    import render_interlude as RI
    st = RI.build()
    sc = bpy.context.scene          # build() resets to factory settings: the old scene handle is gone
    cd = bpy.data.cameras.new("Cam"); cd.clip_start = 0.5; cd.clip_end = 40000
    cam = bpy.data.objects.new("Cam", cd); sc.collection.objects.link(cam); sc.camera = cam
    RI.L.render_setup(G.br_engine or "CYCLES", G.br_res, G.br_samples, "GPU")
    st["expo"] = float(os.environ.get("EXPO", "-1.5")); sc.view_settings.exposure = st["expo"]
    if sc.render.engine == "CYCLES":
        cy = sc.cycles
        cy.samples = G.br_samples; cy.use_adaptive_sampling = False; cy.use_denoising = True
        try:
            cy.denoiser = os.environ.get("INT_DENOISER", "OPTIX")
        except Exception:
            cy.denoiser = "OPENIMAGEDENOISE"
        try:
            cy.denoising_use_gpu = True
        except Exception:
            pass
        cy.max_bounces, cy.diffuse_bounces, cy.glossy_bounces, cy.transmission_bounces = 3, 1, 1, 1
        cy.volume_bounces = 0; cy.transparent_max_bounces = 24
        sc.render.use_persistent_data = True
    def _state(t):
        RI.update(st, t)
        if sc.render.engine == "CYCLES":
            sc.cycles.samples = G.br_samples if RI.SI.night_at(t) < 0.3 else max(G.br_samples, int(os.environ.get("INT_NIGHT_SMP", "16")))
    def _cam(t):
        loc, rot, lens = RI.cam_at(t)
        return Vector(loc), rot.to_matrix() @ Vector((0, 0, -1)), lens
    def _pf(ts, c):
        for s in st["smoke"]:
            s.update(ts, c)
    W.update(state=_state, cam=_cam, per_frame=_pf, ground=lambda x, y: RI.H(x, y))
elif G.world == "march":
    import march846 as MR
    cam = sc.camera
    if sc.render.engine.startswith("BLENDER_EEVEE"):
        ev = sc.eevee; ev.taa_render_samples = G.br_samples
        for k, v in (("use_raytracing", False), ("volumetric_tile_size", "16"), ("volumetric_samples", 24),
                     ("shadow_resolution_scale", 0.5), ("shadow_ray_count", 1), ("shadow_step_count", 4)):
            try:
                setattr(ev, k, v)
            except Exception:
                pass
    sc.render.use_persistent_data = True
    cam.data.clip_end = 30000
    MR.setup()
    def _cam(t):
        loc, tgt, lens = MR.cam_at(t)
        return Vector(loc), (Vector(tgt) - Vector(loc)).normalized(), lens
    W.update(state=lambda t: W.__setitem__("t", t), cam=_cam, per_frame=lambda ts, c: MR.update(ts, c.location),
             ground=lambda x, y: MR.L.height(x, y))
elif G.world == "trost":
    g = _exec_until(os.path.join(HERE, "render_trost.py"), 'if B.dry and os.environ.get("RT_PROBE")')
    cam = g["cam"]
    def _cam(v):
        loc, rot, lens = g["cam_at"](v)
        return Vector(loc), rot.to_matrix() @ Vector((0, 0, -1)), lens
    W.update(state=lambda v: g["frame_state"](v), cam=_cam, per_frame=None, ground=lambda x, y: g["L"].height(x, y))
elif G.world == "base":                  # whatever scene.py built (with AOT_PLUGINS=...,world): stills only
    cam = sc.camera
    W.update(state=lambda t: None, cam=None, per_frame=None, ground=lambda x, y: 0.0)
elif G.world == "shig":
    g = _exec_until(os.path.join(HERE, "render_fall2.py"), "# ================================================================ main")
    cam = g["cam"]
    S3 = g["seg3_build"]()
    def _cam(s):
        g["seg3_pose"](S3, s); bpy.context.view_layer.update()
        m = cam.matrix_world
        return m.translation.copy(), (m.to_3x3() @ Vector((0, 0, -1))).normalized(), cam.data.lens
    W.update(state=lambda s: g["seg3_pose"](S3, s), cam=_cam, per_frame=None, ground=lambda x, y: g["L"].height(x, y),
             light=g.get("SEG3_END_LIGHT"))
    L0 = g.get("SEG3_END_LIGHT") or dict(sun_elevation_deg=4, sun_azimuth_deg=245, sun_color=(1.0, 0.5, 0.2), sun_energy=4.2,
                                         exposure=-1.5)
    DAY = dict(el=float(os.environ.get("C1_DAY_EL", "40")), az=float(os.environ.get("C1_DAY_AZ", "160")),
               col=(1.0, 0.97, 0.92), e=3.6, expo=float(os.environ.get("C1_DAY_EXPO", "-1.5")))
    def _light_at(br, tb):
        """C1 timelapse over the flight: segment 3's sunset -> a short blue night -> morning -> the interlude's daylight
        (sun 40 deg, white 3.6) by the S3 seam.  The sun keeps turning the same way (west -> under -> east -> south)."""
        T = MT.bridge_total(br); u = min(1.0, max(0.0, tb / T))
        so = bpy.data.objects.get("Sun")
        if not so:
            return
        az = L0["sun_azimuth_deg"] + (DAY["az"] + 360.0 - L0["sun_azimuth_deg"]) * u
        el = L0["sun_elevation_deg"] + (DAY["el"] - L0["sun_elevation_deg"]) * MT.herm(0.0, 0.0, 1.0, 0.0, 1.0, u) \
            - 22.0 * math.sin(math.pi * min(1.0, u / 0.7))            # dips below the horizon (night) mid-flight
        night = max(0.0, min(1.0, -el / 8.0))
        e_ = math.radians(el); a_ = math.radians(az)
        d = Vector((-math.cos(e_) * math.cos(a_), -math.cos(e_) * math.sin(a_), -math.sin(e_)))
        so.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
        warm = max(0.0, 1.0 - max(0.0, el) / 25.0)
        c0 = Vector(L0["sun_color"]); c1 = Vector(DAY["col"])
        so.data.color = tuple(c1.lerp(c0, warm))
        so.data.energy = (L0["sun_energy"] * (1 - u) + DAY["e"] * u) * (1.0 - night)
        bg = sc.world.node_tree.nodes.get("Background") if sc.world and sc.world.node_tree else None
        if bg:
            if "_c1_bg" not in W:
                W["_c1_bg"] = bg.inputs[1].default_value
            bg.inputs[1].default_value = W["_c1_bg"] * (1.0 - 0.9 * night)
        sc.view_settings.exposure = L0.get("exposure", -1.5) * (1 - u) + DAY["expo"] * u + 1.2 * night
    W["light_at"] = _light_at
sc = bpy.context.scene
sc.render.image_settings.file_format = "PNG"
print(f"[bridge] world {G.world} built in {time.time() - t_b:.0f}s, engine {sc.render.engine}", flush=True)

# ------------------------------------------------------------------ segment keys, evaluated with this world's camera
def eval_key(state, side):
    """side 'out' (outgoing segment end: backward difference) or 'in' (incoming start: forward difference)."""
    name, t = state
    h = 1.0 / 60.0
    ta, tb = (t - h, t) if side == "out" else (t, t + h)
    la, da, na = W["cam"](ta)
    lb, db, nb = W["cam"](tb)
    l0, d0, n0 = W["cam"](t)
    k = dict(state=name, t=t, loc=list(l0), dir=list(d0.normalized()), lens=float(n0),
             vel=list((lb - la) / h), ddir=list((db.normalized() - da.normalized()) / h),
             dlnlens=(math.log(nb) - math.log(na)) / h)
    k["look_at"] = list(l0 + d0.normalized() * MT.D_LOOK)
    os.makedirs(os.path.join(MT.BRIDGES, "keys"), exist_ok=True)
    json.dump(k, open(os.path.join(MT.BRIDGES, "keys", f"{name}_{t:.3f}.json"), "w"), indent=1)
    print(f"[bridge] key {name} t={t:.3f} ({side}): loc {tuple(round(c) for c in l0)} |v| {Vector(k['vel']).length:.0f} m/s "
          f"lens {n0:.1f}", flush=True)
    return k

if G.stills:                              # world stills (world coordinates -> this scene's set frame)
    WD = sys.modules.get("world") or __import__("world")
    fr = G.still_frame or WD.active_frame()
    od = os.path.join(MT.MASTER, "world_stills"); os.makedirs(od, exist_ok=True)
    cam.data.clip_end = 250000.0
    for spec in [x for x in G.stills.split(";") if x.strip()]:
        nm, a, b, ln = spec.split(":")
        loc = Vector(WD.to_set(tuple(float(v) for v in a.split(",")), fr))
        tgt = Vector(WD.to_set(tuple(float(v) for v in b.split(",")), fr))
        cam.location = loc; cam.rotation_euler = (tgt - loc).to_track_quat("-Z", "Y").to_euler(); cam.data.lens = float(ln)
        bpy.context.view_layer.update()
        sc.render.filepath = os.path.join(od, f"{nm}__{G.world}_{fr}.png")
        bpy.ops.render.render(write_still=True)
        print(f"[bridge] still {nm} ({fr} frame) -> {sc.render.filepath}", flush=True)

js_only = {int(x) for x in G.br_js.split(",") if x.strip()}
t_r = time.time(); n_done = 0
FR = "shig" if G.world == "shig" else "trost"
def resolve(k, side):
    return MT.seam_key(k["seam"], FR) if "seam" in k else eval_key(k["state"], side)
for bid, half in HALVES:
    br = MT.SEG[bid]
    hd = br["halves"][half]
    k0, k1 = resolve(hd["k0"], "out"), resolve(hd["k1"], "in")
    if G.br_keys_only:
        continue
    W["state"](hd["state"][1])
    od = MT.bridge_dir(br); os.makedirs(od, exist_ok=True)
    for j, tb, hh in MT.bridge_frames(br, FPS):
        if hh != half or (js_only and j not in js_only):
            continue
        if W.get("light_at"):
            W["light_at"](br, tb)
        loc, d, lens = MT.bridge_eval(br, half, k0, k1, tb)
        loc = Vector(loc)
        try:
            loc.z = max(loc.z, W["ground"](loc.x, loc.y) + 12.0)
        except Exception:
            pass
        cam.location = loc
        cam.rotation_euler = Vector(d).to_track_quat("-Z", "Y").to_euler()
        cam.data.lens = lens
        bpy.context.view_layer.update()
        if W.get("per_frame"):
            W["per_frame"](hd["state"][1], cam)
            bpy.context.view_layer.update()
        sc.render.filepath = os.path.join(od, f"br_{j:05d}.png")
        bpy.ops.render.render(write_still=True)
        hudcam.dump(sc, j, od, t=tb, extra={"bridge": bid, "half": half, "world": G.world})
        n_done += 1
        print(f"[bridge] {bid}{half} j={j} tb={tb:.2f} loc {tuple(round(c) for c in loc)} lens {lens:.0f} "
              f"({time.time() - t_r:.0f}s, {(time.time() - t_r) / n_done:.1f}s/f)", flush=True)
print(f"[bridge] done: {n_done} frames in {time.time() - t_r:.0f}s", flush=True)
