"""Fast-paced opening (user spec 2026-10-24 09:06 UTC, revised 15:07 feedback), timed in VIDEO SECONDS:
  0-2 s    tree: a very slow zoom-out; Eren sleeps sitting against the trunk and slowly bends forward (waking),
           Mikasa walks slowly up to him (flight.py FL_KIDS_MODE=seated)
  2-4.8 s  camera leaves the tree, over the dressed meadow (FL_FIELD=1: road, tussocks, trees, bushes), through the
           inner gate and down the avenue, decelerating smoothly over the plaza crowd (one monotone time -> progress
           curve for the whole move, so the speed never jumps)
  4.6-5 s  arrival: yellow-orange lightning strikes behind the outer gate, the scene darkens, the camera shakes;
           the Colossal's LEFT hand slams onto the wall top, fingers over the town-side edge
  5-8 s    the head rises (same speed as before) while the long lens pushes in; the RIGHT hand grips at ~6-6.7 s
  8-11 s   camera lifts to see the gate; the right leg winds up behind the wall
  11 s     the kick at gate height: the outer gate bursts, blocks fly into the town; then steam
Run after scene.py in the same session (see render_fast.sh).  Every frame is a pure function of its time t (camera,
Colossal pose, FX, kids via frame_set), so any window or single frame renders on its own.
"""
import bpy, bmesh, math, os, random, sys, time, argparse
from mathutils import Vector, Euler, noise

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ap = argparse.ArgumentParser()
ap.add_argument("--fast-out", required=True)
ap.add_argument("--t0", type=float, default=0.0)
ap.add_argument("--t1", type=float, default=11.0)
ap.add_argument("--fps", type=float, default=30.0)          # final 30, previews 15
ap.add_argument("--fast-samples", type=int, default=8)
ap.add_argument("--index0", type=int, default=0)
ap.add_argument("--times", default="", help="comma list of single times to render instead of t0..t1 (stills)")
ap.add_argument("--prefix", default="fast")
B, _ = ap.parse_known_args(argv)

import aotlib as L
CA = sys.modules.get("colossal_asset")
FL = sys.modules.get("flight")
GX, GY = L.OUTER_GATE
CDX = float(os.environ.get("COL_DX", "-7"))
HEAD = Vector((CDX - 0.5, GY - 20, 60))          # centre of the (1.8x) head at full rise (harness: neck top z 57.5, crown 66)
PLAZA = Vector(L.PLAZA[:2])
STRIKE = Vector((CDX, GY - 22, 0))
T_KICK = 11.0                                    # the foot hits the gate (fx845.update(t - T_KICK))               # lightning ground point, behind the outer gate where the Colossal appears

def smooth(a, b, t):
    u = min(1.0, max(0.0, (t - a) / (b - a))); return u * u * (3 - 2 * u)

def bump(t, a, b, c, d):
    """0 before a, ramps to 1 by b, holds to c, back to 0 by d."""
    return smooth(a, b, t) * (1 - smooth(c, d, t))

# ---------------------------------------------------------------- camera keys in seconds: (t, loc, look_at, lens)
def keys():
    l0, t0, n0 = FL.flight_at(900) if FL else ((-480, 338, 6), (-300, 0, 10), 50)
    l0, t0 = Vector(l0), Vector(t0)
    # opening: start close on the kids (Eren dozing against the trunk, Mikasa walking up), pull back along the same
    # line of sight to the loved tree framing by 2.0 s, a short beat (2.0-2.05 hold), then the whoosh
    kids = [o.matrix_world.translation for o in (bpy.data.objects.get("Eren"), bpy.data.objects.get("Mikasa")) if o]
    k0 = (sum(kids, Vector()) / len(kids) + Vector((0, 0, 0.7))) if kids else t0
    near = float(os.environ.get("FAST_NEAR", "0.74"))                  # fraction of the way from the end camera to the kids
    c0 = l0 + (k0 - l0) * near; c0.z = max(c0.z, k0.z + 1.0)
    l1 = l0 + Vector((0, 0, 1.2))
    return [
        (0.0, c0, k0, n0 * 0.9),
        (2.0, l1, t0 + Vector((0, 0, 0.6)), n0),
        (2.05, l1, t0 + Vector((0, 0, 0.6)), n0),
        (2.6, (-430, 290, 28), (-150, 120, 14), 32),                   # leave the tree: up and toward the gate
        (3.2, (-220, 170, 46), (0, 0, 45), 28),                        # over the meadow / road, climbing
        (3.55, (-85, 85, 63), (0, -150, 40), 27),
        (3.8, (-15, 18, 72), (-2, -450, 30), 27),                      # UP and OVER the inner wall top (+22 m)
        (4.35, (-3, -200, 65), (CDX, -700, 42), 30),                   # gliding down along the avenue
        (4.9, (-6, -385, 60), (CDX, GY, 52), 46),                      # past the plaza, down the gate street
        # line of sight from ~58 m over the wall top reaches ~49 m at the head: it reads as soon as it rises
        (5.45, (-6, -425, 58), (CDX, GY - 12, 56), 74),               # gentle zoom ease-in toward the face
        (8.0, (-5, -450, 56), tuple(HEAD + Vector((0, 2, -3))), float(os.environ.get("FAST_HEAD_LENS", "210"))),   # face ~55% of frame height
        (10.0, (PLAZA.x + 40, PLAZA.y + 30, 120), (GX, GY + 30, 18), 40),   # lift: gate and wall in frame
        (11.0, (PLAZA.x + 45, PLAZA.y + 35, 128), (GX, GY + 40, 16), 40),
        (13.0, (PLAZA.x + 55, PLAZA.y + 50, 150), (GX, GY + 120, 0), 38),  # debris arcs into the town
    ]

def _herm(p0, p1, p2, p3, u, dist):
    """Hermite segment p1->p2 with Catmull-Rom tangents scaled by the chord lengths (no overshoot when neighbouring
    keys are very unequally spaced, e.g. the slow 2 s zoom next to the 300 m whoosh)."""
    d01, d12, d23 = dist(p0, p1), dist(p1, p2), dist(p2, p3)
    m1 = (p2 - p0) * (d12 / (d01 + d12)) if d01 + d12 > 1e-9 else p2 - p1
    m2 = (p3 - p1) * (d12 / (d12 + d23)) if d12 + d23 > 1e-9 else p2 - p1
    h00, h10, h01, h11 = 2 * u ** 3 - 3 * u ** 2 + 1, u ** 3 - 2 * u ** 2 + u, -2 * u ** 3 + 3 * u ** 2, u ** 3 - u ** 2
    return p1 * h00 + m1 * h10 + p2 * h01 + m2 * h11

def _pchip_m(T, S):
    """Fritsch-Carlson tangents: monotone cubic through (T_i, S_i), C1, no overshoot, starts from rest."""
    D = [(S[i + 1] - S[i]) / (T[i + 1] - T[i]) for i in range(len(T) - 1)]
    return [0.0] + [0.0 if D[i - 1] * D[i] <= 0 else 2 * D[i - 1] * D[i] / (D[i - 1] + D[i]) for i in range(1, len(D))] + [D[-1]]

def _pchip(T, S, m, t):
    t = min(max(t, T[0]), T[-1])
    i = min(len(T) - 2, max(j for j in range(len(T)) if T[j] <= t))
    h = T[i + 1] - T[i]; s = (t - T[i]) / h
    h00, h10, h01, h11 = 2 * s ** 3 - 3 * s ** 2 + 1, s ** 3 - 2 * s ** 2 + s, -2 * s ** 3 + 3 * s ** 2, s ** 3 - s ** 2
    return h00 * S[i] + h10 * h * m[i] + h01 * S[i + 1] + h11 * h * m[i + 1]

class _Channel:
    """One camera channel (location or look-at point): chord-scaled Hermite path through the keys, re-timed by a
    monotone time -> arc-length curve so its speed is C1-smooth in time (no jumps at keys, no per-segment pacing)."""
    def __init__(self, T, pts):
        self.T, self.P = T, [Vector(p) for p in pts]
        n = len(pts); self.segs = []; S = [0.0]
        for i in range(n - 1):
            q = [self.P[max(0, min(n - 1, j))] for j in (i - 1, i, i + 1, i + 2)]
            acc = [0.0]; prev = q[1]
            for k in range(1, 97):
                p = _herm(*q, k / 96, lambda a, b: (a - b).length)
                acc.append(acc[-1] + (p - prev).length + 1e-7); prev = p
            self.segs.append((q, acc)); S.append(S[-1] + acc[-1])
        self.S, self.m = S, _pchip_m(T, S)
    def at(self, t):
        s = _pchip(self.T, self.S, self.m, t)
        i = min(len(self.segs) - 1, max(j for j in range(len(self.segs)) if self.S[j] <= s + 1e-9))
        q, acc = self.segs[i]; r = s - self.S[i]
        k = 0
        while k < len(acc) - 2 and acc[k + 1] < r:
            k += 1
        f = min(1.0, max(0.0, (r - acc[k]) / (acc[k + 1] - acc[k])))
        return _herm(*q, (k + f) / 96, lambda a, b: (a - b).length)

_TAB = {}
def _table():
    if not _TAB:
        ks = keys(); T = [k[0] for k in ks]
        lnl = [math.log(k[3]) for k in ks]
        _TAB.update(loc=_Channel(T, [k[1] for k in ks]), tgt=_Channel(T, [k[2] for k in ks]), T=T, lnl=lnl, ml=_pchip_m(T, lnl))
    return _TAB

# FAST_HOUSE_CAM=12.9: cut at that time to a closer camera on a house hit by a block (lands ~T_KICK + 2.14 s)
HOUSE_CAM = (float(os.environ["FAST_HOUSE_CAM"]),) if os.environ.get("FAST_HOUSE_CAM") else None

def shake(t):
    """Rotational shake amplitude (rad): the arrival (lightning) and the kick impact."""
    a = 0.011 * bump(t, 4.6 - ARR_D, 4.66 - ARR_D, 4.75 - ARR_D, 5.7 - ARR_D) + 0.006 * bump(t, 10.98, 11.02, 11.1, 12.0)
    if HOUSE_CAM:
        a += 0.005 * bump(t, T_KICK + 2.1, T_KICK + 2.16, T_KICK + 2.25, T_KICK + 2.9)
    return a

def cam_at(t):
    tb = _table()
    loc, tgt = tb["loc"].at(t), tb["tgt"].at(t)
    lens = math.exp(_pchip(tb["T"], tb["lnl"], tb["ml"], t))
    if 11.0 <= t < 12.0:                                          # impact: the camera body jolts too
        kk = (12.0 - t) * 3.0
        loc = loc + Vector((noise.noise(Vector((t * 40, 0, 0))), noise.noise(Vector((0, t * 40, 3))), noise.noise(Vector((5, 1, t * 40))))) * kk
    if HOUSE_CAM and t >= HOUSE_CAM[0]:                          # optional cut: a house crushed by a gate block
        u = smooth(HOUSE_CAM[0], HOUSE_CAM[0] + 2.6, t)
        loc = Vector((-95, -405, 55)) + Vector((-6, -6, -4)) * u; tgt = Vector((-150, -458, 3)); lens = 32 + 4 * u
    if t < 2.3:                                                    # opening push: never dip into the hill
        loc.z = max(loc.z, L.height(loc.x, loc.y) + 0.9)
    rot = (tgt - loc).to_track_quat("-Z", "Y").to_euler()
    a = shake(t)
    if a:
        rot.x += a * noise.noise(Vector((t * 31, 0.5, 7))); rot.z += a * noise.noise(Vector((2.5, t * 29, 1)))
        rot.y += 0.4 * a * noise.noise(Vector((9, 4, t * 23)))
    return loc, rot, lens

# ---------------------------------------------------------------- the Colossal
def colossal_at(t):
    """(show, rise, kick, fade, hand_l, hand_r).  Left hand slams on the wall top right after the lightning, the head
    rises 5-8 s (unchanged speed), the right hand comes up from behind the wall ~5.9-6.7 s, wind-up 8.8-10.3, strike to 11."""
    show = 4.6 - ARR_D <= t < 13.5
    u = min(1.0, max(0.0, (t - 4.62 + ARR_D) / (8.0 - 4.62 + ARR_D)))             # ease-out: the head is readable from ~5.2 s,
    rise = 1 - (1 - u) ** 3                                          # still rising slowly until 8 s (COL_RISE_DROP 14)
    if t < 8.8:
        kick = 0.0
    elif t < 10.3:
        kick = -smooth(8.8, 10.3, t)
    else:
        kick = -1.0 + 2.0 * smooth(10.3, 11.0, t)
    fade = smooth(11.6, 13.0, t)
    hand_l = smooth(4.8 - ARR_D, 5.12 - ARR_D, t)
    hand_r = smooth(5.9, 6.7, t)
    return show, rise, kick, fade, hand_l, hand_r

# ---------------------------------------------------------------- arrival FX: lightning, darkening, flash
ARR_D = float(os.environ.get("FAST_ARRIVE_EARLIER", "0.45"))   # user 10/25: the lightning (arrival) a bit earlier
FLICKER = tuple((a - ARR_D, b - ARR_D, v) for a, b, v in ((4.62, 4.70, 0), (4.74, 4.79, 1), (4.84, 4.95, 0)))      # (on, off, bolt variant)

def _bolt(name, seed, top=720.0):
    rnd = random.Random(seed)
    bm = bmesh.new()
    def channel(p, n, step, r, spread, depth=0):
        pts = [p]
        for k in range(n):
            q = pts[-1] + Vector((rnd.uniform(-spread, spread), rnd.uniform(-spread, spread), -step * rnd.uniform(0.7, 1.3)))
            if depth == 0:                                            # main channel converges on the strike point
                left = n - k
                q.x += (STRIKE.x - q.x) / max(1, left) * 0.8; q.y += (STRIKE.y - q.y) / max(1, left) * 0.8
            q.z = max(q.z, 0.0)
            pts.append(q)
        for a, b in zip(pts, pts[1:]):
            L.cyl(bm, a, b, r, r * 0.92, seg=6)
        return pts
    main = channel(Vector((STRIKE.x + rnd.uniform(-60, 60), STRIKE.y - rnd.uniform(20, 80), top)), 34, top / 34, 1.7, 14)
    for k in range(4):                                                # forks
        st = main[rnd.randrange(4, 22)]
        channel(st.copy(), rnd.randint(5, 10), rnd.uniform(14, 24), 0.8, 18, depth=1)
    m = bpy.data.materials.new(name + "Mat"); m.use_nodes = True
    nt = m.node_tree; nt.nodes.remove(nt.nodes["Principled BSDF"])
    em = nt.nodes.new("ShaderNodeEmission"); em.inputs["Color"].default_value = (1.0, 0.70, 0.22, 1)
    em.inputs["Strength"].default_value = float(os.environ.get("FAST_BOLT_E", "40"))
    nt.links.new(em.outputs[0], nt.nodes["Material Output"].inputs["Surface"])
    ob = L.obj_from_bm(name, bm, [m])
    ob.visible_shadow = False
    ob.hide_render = True
    return ob

def build_fx():
    fx = {"bolts": [_bolt("FX_Bolt0", 11), _bolt("FX_Bolt1", 23)]}
    ld = bpy.data.lights.new("FX_Flash", "POINT"); ld.color = (1.0, 0.75, 0.35); ld.shadow_soft_size = 30
    lo = bpy.data.objects.new("FX_Flash", ld); lo.location = STRIKE + Vector((0, 0, 140))
    bpy.context.scene.collection.objects.link(lo); ld.energy = 0.0
    fx["flash"] = ld
    # remember the base light levels so darkening scales them per frame (pure function of t)
    w = bpy.context.scene.world
    fx["bg"] = [(n, n.inputs[1].default_value) for n in (w.node_tree.nodes if w and w.use_nodes else []) if n.type == "BACKGROUND"]
    fx["suns"] = [(o.data, o.data.energy) for o in bpy.data.objects if o.type == "LIGHT" and o.data.type == "SUN"]
    fx["exp"] = bpy.context.scene.view_settings.exposure
    # the Colossal's steam wisps are placed for the full rise and hide the head during the reveal: show them from 8.2 s
    fx["wisps"] = [o for o in bpy.data.objects if o.name.startswith("ColossalWisp")]
    return fx

def fx_at(fx, t):
    on = [v for a, b, v in FLICKER if a <= t < b]
    for k, ob in enumerate(fx["bolts"]):
        ob.hide_render = not (on and on[0] == k)
    dark = 1.0 - float(os.environ.get("FAST_DARK", "0.72")) * bump(t, 4.45 - ARR_D, 4.6 - ARR_D, 4.95 - ARR_D, 5.6 - ARR_D)
    for n, v in fx["bg"]:
        n.inputs[1].default_value = v * dark
    for d, v in fx["suns"]:
        d.energy = v * dark
    fx["flash"].energy = float(os.environ.get("FAST_FLASH_W", "6e6")) if on else 0.0
    dk = bump(t, 4.45 - ARR_D, 4.6 - ARR_D, 4.95 - ARR_D, 5.6 - ARR_D)
    bpy.context.scene.view_settings.exposure = fx["exp"] - float(os.environ.get("FAST_DARK_EV", "1.6")) * dk + (0.7 if on else 0.0)
    for o in fx["wisps"]:
        if t < float(os.environ.get("FAST_WISPS_T", "4.72")):
            o.hide_render = True

def kids_frame(t):
    """Flight-module frame for the kids: F_KIDS + 30 fps * t over the 2 s opening (seated wake / Mikasa's walk)."""
    f0 = getattr(FL, "F_KIDS", 750) if FL else 750
    return f0 + 30.0 * min(max(t, 0.0), 2.0)

# ---------------------------------------------------------------- plaza crowd (cheap: low-poly figures, varied colours)
def crowd(n=160, seed=4):
    rnd = random.Random(seed)
    bm = bmesh.new()
    cols = [(0.35, 0.22, 0.12), (0.55, 0.48, 0.38), (0.18, 0.2, 0.24), (0.45, 0.1, 0.08), (0.62, 0.6, 0.55), (0.25, 0.3, 0.18)]
    mats = [L.mat(f"Crowd{i}", c, 0.9) for i, c in enumerate(cols)] + [L.mat("CrowdSkin", (0.7, 0.5, 0.38), 0.6)]
    for k in range(n):
        a = rnd.uniform(0, math.tau); r = math.sqrt(rnd.random()) * (L.PLAZA[2] - 3)
        x, y = PLAZA.x + math.cos(a) * r, PLAZA.y + math.sin(a) * r
        h = rnd.uniform(1.5, 1.85); mi = rnd.randrange(len(cols))
        L.cyl(bm, (x, y, 0.1), (x, y, h * 0.82), 0.24, 0.19, seg=6, mi=mi)
        ico = bmesh.ops.create_icosphere(bm, subdivisions=1, radius=0.13)
        for v in ico["verts"]:
            v.co += Vector((x, y, h * 0.9))
        for f in {f for v in ico["verts"] for f in v.link_faces}:
            f.material_index = len(cols)
    L.obj_from_bm("PlazaCrowd", bm, mats)

# ---------------------------------------------------------------- render loop
sc = bpy.context.scene
cam = sc.camera
if sc.render.engine.startswith("BLENDER_EEVEE"):
    sc.eevee.taa_render_samples = B.fast_samples
    if os.environ.get("FAST_PREVIEW") == "1":                    # preview: coarse volumes/shadows, no ray tracing
        ev = sc.eevee
        for k, v in (("use_raytracing", False), ("volumetric_tile_size", "16"), ("volumetric_samples", 32),
                     ("shadow_resolution_scale", 0.5), ("shadow_ray_count", 1), ("shadow_step_count", 4)):
            try:
                setattr(ev, k, v)
            except Exception:
                pass
        sc.render.use_persistent_data = True
        print("[fast] preview mode (Eevee): taa", ev.taa_render_samples)
else:
    sc.cycles.samples = B.fast_samples; sc.cycles.use_adaptive_sampling = True
    if os.environ.get("FAST_PREVIEW") == "1":                    # preview: few samples + denoise, short paths, no fog
        cy = sc.cycles
        cy.use_denoising = True
        try:
            cy.denoiser = "OPENIMAGEDENOISE"; cy.denoising_use_gpu = True
        except Exception:
            pass
        cy.max_bounces, cy.diffuse_bounces, cy.glossy_bounces, cy.transmission_bounces = 3, 1, 1, 2
        cy.volume_bounces = 0; cy.transparent_max_bounces = 12; cy.caustics_reflective = cy.caustics_refractive = False
        cy.volume_step_rate = 6; cy.volume_max_steps = 128
        sc.render.use_persistent_data = True
        sc.render.use_simplify = True; sc.render.simplify_subdivision_render = 0
        cy.texture_limit_render = "1024"
        for n in ("Haze",):
            ob = bpy.data.objects.get(n)
            if ob:
                ob.hide_render = True
        for ob in bpy.data.objects:
            if ob.type == "MESH" and any(m and m.name.startswith("FL_Rays") for m in ob.data.materials):
                ob.hide_render = True
        print("[fast] preview mode: samples", cy.samples)
sc.render.image_settings.file_format = "PNG"
os.makedirs(B.fast_out, exist_ok=True)
# crowd: swarm845 (same people as segment 2: plaza crowd + small groups along the streets, standing and watching
# the wall while t < 11) unless FAST_SWARM=0, then the old cheap plaza-only crowd
SW = None
if os.environ.get("FAST_SWARM", "1") != "0":
    try:
        import swarm845 as SW
        if not SW.STATE.get("people"):
            t_sw = time.time()
            SW.setup(t_end=float(os.environ.get("FAST_SWARM_TEND", "20")))
            print(f"[fast] swarm845 setup {time.time() - t_sw:.0f}s", SW.info())
    except Exception as ex:
        import traceback; traceback.print_exc(); SW = None
        print("[fast] swarm845 unavailable:", ex)
if SW is None and not bpy.data.objects.get("PlazaCrowd") and os.environ.get("FAST_CROWD", "1") != "0":
    crowd()
FX = build_fx()
col_coll = bpy.data.collections.get("ColossalTitan")
FX845 = sys.modules.get("fx845")
if FX845 is None and os.environ.get("AOT_STATE") == "kicked":
    try:
        import fx845 as FX845
    except Exception as ex:
        print("[fast] fx845 unavailable:", ex)
if FX845 is not None and not any(FX845.REG.get(k) for k in ("blocks", "mods", "houses", "appear")):
    FX845 = None                                                   # module loaded but nothing registered (intact build)
print("[fast] fx845 per-frame destruction:", "on" if FX845 else "off")
if B.times:
    times = [float(x) for x in B.times.split(",") if x.strip()]
else:
    times = [B.t0 + j / B.fps for j in range(int(round((B.t1 - B.t0) * B.fps)))]
i = B.index0
t_start = time.time()
for t in times:
    t_fr = time.time()
    kf = kids_frame(t)
    sc.frame_set(int(kf), subframe=kf - int(kf))
    show, rise, kick, fade, hl, hr = colossal_at(t)
    if col_coll:
        col_coll.hide_render = not show
        if show and CA and CA.STATE:
            CA.set_pose(kick, rise, fade, hand_l=hl, hand_r=hr, steam=smooth(4.72, 7.8, t))   # steam only after the strike
    fx_at(FX, t)
    t_fx = time.time()
    if FX845:
        FX845.update(t - T_KICK)                                   # negative = intact gate; pure function of t
    t_fx = time.time() - t_fx
    if SW is not None:
        SW.update(t - T_KICK)                                      # t < 11: standing in the plaza / streets, watching
    loc, rot, lens = cam_at(t)
    cam.location = loc; cam.rotation_euler = rot; cam.data.lens = lens
    name = f"{B.prefix}_{i:05d}.png" if not B.times else f"{B.prefix}_t{t:05.2f}.png"
    sc.render.filepath = os.path.join(B.fast_out, name)
    bpy.ops.render.render(write_still=True)
    print(f"[fast] t={t:.2f}s -> {name} ({time.time() - t_start:.0f}s total, fx845 {t_fx:.1f}s, frame {time.time() - t_fr:.1f}s)")
    i += 1
