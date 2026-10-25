"""Shiganshina 845 segments 3-5, one Blender session per state (run after scene.py, see render_fall2.sh).

--seg 3  (AOT_STATE=armored, dusk, ~12 s)  The Armored Titan charges up the avenue and bursts the inner gate (s 3.4:
         breach booleans on, door gone, blocks + dust thrown north), people jam the canal bank north of the wall while
         the refugee ferries pull away north; the kids at the lead ferry's bow: the VOW HOLD s 8-11; crane up.
--seg 45 (AOT_STATE=night) segment 4 (~12 s): night pull-up from the burning town to ~1.5 km: pure titans spreading
         north over Wall Maria's land, the belt north of the wall turning grey (terrain shader mask, front moving
         north).  Then segment 5 (~5 s, frames continue in a second folder): the Grisha beat in a clearing of the
         Forest of Giant Trees: tiny faceless Grisha + Eren, a lantern, the injection (flash), the key; GLITCH marker
         at s 4.7 (written to <out>/grisha_glitch_marker.json for agent E's 2D glitch cut).
Every frame is a pure function of the segment time s.  Minimal swarm-style figures (swarm845 geometry) for crowds
and titans; seq_carla's ferry / kids builders and shifters' Armored for the named pieces.
"""
import bpy, math, os, sys, time, argparse, random, json
import numpy as np
from mathutils import Vector, Matrix, noise

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ap = argparse.ArgumentParser()
ap.add_argument("--seg", default="3")
ap.add_argument("--fall-out", required=True)
ap.add_argument("--fps", type=float, default=30.0)
ap.add_argument("--fall-samples", type=int, default=2)
ap.add_argument("--times", default="")
B, _ = ap.parse_known_args(argv)

import aotlib as L
import swarm845 as SW
FX = sys.modules.get("fx845")
import seq_carla as SC
import pure_titans as PT

def smooth(a, b, t):
    u = min(1.0, max(0.0, (t - a) / (b - a))); return u * u * (3 - 2 * u)

def look(cam, loc, tgt, lens, roll=0.0):
    cam.location = loc
    e = (Vector(tgt) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    cam.rotation_euler = e; cam.data.lens = lens

def _mono(a, b):
    """Fritsch-Carlson tangent from two neighbouring slopes: 0 at a turn, harmonic mean otherwise (no overshoot)."""
    return 0.0 if a * b <= 0 else 2 * a * b / (a + b)

def _cr(p0, p1, p2, p3, u, t0, t1, t2, t3):
    """Monotone (per component) cubic Hermite segment p1->p2, time-parametrised."""
    h00, h10, h01, h11 = 2 * u ** 3 - 3 * u ** 2 + 1, u ** 3 - 2 * u ** 2 + u, -2 * u ** 3 + 3 * u ** 2, u ** 3 - u ** 2
    def one(a0, a1, a2, a3):
        d0, d1, d2 = (a1 - a0) / (t1 - t0), (a2 - a1) / (t2 - t1), (a3 - a2) / (t3 - t2)
        m1, m2 = _mono(d0, d1) * (t2 - t1), _mono(d1, d2) * (t2 - t1)
        return a1 * h00 + m1 * h10 + a2 * h01 + m2 * h11
    if isinstance(p1, (int, float)):
        return one(p0, p1, p2, p3)
    return Vector([one(p0[i], p1[i], p2[i], p3[i]) for i in range(len(p1))])

def spline_cam(ks, s):
    """ks: [(s, loc, tgt, lens)] with a guide key at each end; time-parametrised Catmull-Rom, eased ends."""
    s = min(max(s, ks[1][0]), ks[-2][0])
    i = max(j for j in range(1, len(ks) - 2) if ks[j][0] <= s) if s > ks[1][0] else 1
    q = ks[i - 1:i + 3]; T = [k[0] for k in q]
    u = (s - T[1]) / (T[2] - T[1])
    loc = _cr(*[Vector(k[1]) for k in q], u, *T); tgt = _cr(*[Vector(k[2]) for k in q], u, *T)
    lens = math.exp(_cr(*[math.log(k[3]) for k in q], u, *T))
    return loc, tgt, lens

def guide(ks):
    """Add mirrored guide keys at both ends (zero-ish end velocity)."""
    a, b = ks[0], ks[-1]
    return [(a[0] - 1.0, a[1], a[2], a[3])] + ks + [(b[0] + 1.0, b[1], b[2], b[3])]

def set_sun(el_deg, az_deg, col, energy):
    so = bpy.data.objects.get("Sun")
    if not so:
        return
    el, az = math.radians(el_deg), math.radians(az_deg)
    d = Vector((-math.cos(el) * math.cos(az), -math.cos(el) * math.sin(az), -math.sin(el)))
    so.rotation_euler = d.to_track_quat("-Z", "Y").to_euler(); so.data.color = col; so.data.energy = energy

# ---------------------------------------------------------------- minimal crowd (swarm845 geometry, own motion)
class MiniCrowd:
    """N swarm-style figures in one deforming mesh; motion(s) -> pos (N,3), yaw (N,), dist (N,) supplied per frame."""
    def __init__(self, name, n, seed, coll, titans=None):
        rnd = random.Random(seed); self.rnd = rnd
        g = SW.Geo(); fm = []
        mats = [L.mat(f"{name}_shirt{i}", c, 0.75) for i, c in enumerate(SW.SHIRTS)] + [L.mat(f"{name}_pants{i}", c, 0.85) for i, c in enumerate(SW.PANTS)] \
            + [L.mat(f"{name}_skin{i}", c, 0.6) for i, c in enumerate(SW.SKINS)] + [L.mat(f"{name}_hair{i}", c, 0.7) for i, c in enumerate(SW.HAIRS)]
        ns, npn, nk = len(SW.SHIRTS), len(SW.PANTS), len(SW.SKINS)
        self.h = np.zeros(n)
        if titans:
            mats = [L.mat(f"{name}_tskin{i}", c, 0.65) for i, c in enumerate(SW.T_SKINS)] + [L.mat(f"{name}_thair{i}", c, 0.7) for i, c in enumerate(SW.T_HAIRS)] \
                + [L.mat(f"{name}_teeth", (0.85, 0.8, 0.7), 0.5)]
            for j in range(n):
                H = 3.0 + 12.0 * rnd.random() ** 1.25
                sp = dict(name=f"m{j}", H=H * titans, g=rnd.uniform(0.8, 1.35), al=rnd.uniform(0.9, 1.15), hs=rnd.uniform(0.9, 1.3),
                          skin=rnd.randrange(len(SW.T_SKINS)), hair=rnd.choice([None, 0, 1, 2, 3]))
                n0 = len(g.fc); SW.titan_geo(g, j, sp); self.h[j] = sp["H"]
                base = [sp["skin"], len(SW.T_SKINS) + (sp["hair"] or 0), len(SW.T_SKINS) + len(SW.T_HAIRS)]
                fm += [base[c] for c in g.fc[n0:]]
        else:
            for i in range(n):
                h = rnd.uniform(1.0, 1.3) if rnd.random() < 0.12 else rnd.uniform(1.5, 1.9)
                n0 = len(g.fc); SW.person_geo(g, i, h, rnd.random() < 0.3, rnd); self.h[i] = h
                base = [rnd.randrange(ns), ns + rnd.randrange(npn), ns + npn + rnd.randrange(nk), ns + npn + nk + rnd.choice([0, 0, 1, 1, 2, 3, 4])]
                fm += [base[c] for c in g.fc[n0:]]
        self.R = g.finish(); self.n = n
        self.ob = SW._mesh(name, self.R, g.f, fm, mats, coll)

    def set(self, pos, yaw, dist, moving, arms_up=None, vis=None, stride=None):
        n = self.n
        Ar = np.zeros((n, 7)); Ae = np.zeros((n, 7))
        st = stride if stride is not None else 1.5 * self.h
        ph = 2 * np.pi * dist / st
        sw = np.sin(ph) * 0.7 * moving
        Ar[:, 1] = sw; Ar[:, 2] = -sw; Ar[:, 3] = -0.8 * sw; Ar[:, 4] = 0.8 * sw
        if arms_up is not None:
            Ar[:, 3] += arms_up; Ar[:, 4] += arms_up
        Ar[:, 5] = Ar[:, 4]; Ar[:, 6] = Ar[:, 3]
        lean = -0.2 * moving
        p = pos.copy(); p[:, 2] += (0.5 - 0.5 * np.cos(2 * ph)) * 0.05 * self.h * moving
        co = SW._deform(self.R, Ar, Ae, lean, np.ones(n) if vis is None else vis, yaw, p)
        self.ob.data.vertices.foreach_set("co", co.astype(np.float32).ravel()); self.ob.data.update()

# ---------------------------------------------------------------- shared render settings
sc = bpy.context.scene
cam = sc.camera
OUT = B.fall_out
os.makedirs(OUT, exist_ok=True)
sc.render.image_settings.file_format = "PNG"
if sc.render.engine.startswith("BLENDER_EEVEE"):
    sc.eevee.taa_render_samples = int(os.environ.get("FALL_EEVEE_SAMPLES", "8"))
    for o in bpy.data.objects:                       # dozens of fire lights overflow Eevee's shadow pool: no shadows
        if o.type == "LIGHT" and o.name.startswith(("FireL", "FX_Flash")):
            o.data.use_shadow = False
else:
    cy = sc.cycles; cy.samples = B.fall_samples; cy.use_adaptive_sampling = True
    if os.environ.get("FAST_PREVIEW", "0") == "1":
        cy.use_denoising = True
        try:
            cy.denoiser = "OPENIMAGEDENOISE"
        except Exception:
            pass
        cy.max_bounces, cy.diffuse_bounces, cy.glossy_bounces, cy.transmission_bounces = 3, 1, 1, 2
        cy.volume_bounces = 0; cy.transparent_max_bounces = 12; cy.caustics_reflective = cy.caustics_refractive = False
        cy.volume_step_rate = float(os.environ.get("FALL_VSTEP", "16")); cy.volume_max_steps = int(os.environ.get("FALL_VMAX", "48"))
        sc.render.use_persistent_data = True
        sc.render.use_simplify = True; sc.render.simplify_subdivision_render = 0
        cy.texture_limit_render = "1024"
        hz = bpy.data.objects.get("Haze")
        if hz:
            hz.hide_render = True
coll = L.new_coll("Fall2")

def render(path):
    sc.render.filepath = path
    if os.environ.get("FALL_DRY") == "1":          # logic check without the GPU
        return
    bpy.ops.render.render(write_still=True)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    import hudcam
except Exception as ex:
    hudcam = None; print("[fall2] hudcam unavailable:", ex)
TAGS = {}                      # label -> object name (name tags for hud2.py), set per segment

def run(frames, pose, prefix, sub=""):
    """frames: list of s; pose(s) sets the scene. Writes <OUT>/<sub>/<prefix>_#####.png or stills."""
    od = os.path.join(OUT, sub) if sub else OUT
    os.makedirs(od, exist_ok=True)
    t_start = time.time()
    for i, s in enumerate(frames):
        t0 = time.time(); pose(s); tp = time.time() - t0
        i = int(round(s * B.fps)) if not B.times else i
        name = f"{prefix}_{i:05d}.png" if not B.times else f"{prefix}_s{s:05.2f}.png"
        if hudcam:                                   # camera + name-tag anchors for hud2.py (rig origin = feet)
            tr = [v for v in TAGS.values() if bpy.data.objects.get(v)]
            hudcam.dump(sc, i, od, t=s, track=tr, name=None if not B.times else name[:-4],
                        extra={"segment": prefix, "labels": {k: v for k, v in TAGS.items() if v in tr}, "anchor": "rig origin = feet"})
        render(os.path.join(od, name))
        print(f"[fall2] {prefix} s={s:.2f} -> {name} (pose {tp:.1f}s, frame {time.time() - t0:.1f}s, total {time.time() - t_start:.0f}s)")

def frame_list(s1):
    if B.times:
        return [float(x) for x in B.times.split(",") if x.strip()]
    j0 = int(round(float(os.environ.get("FALL2_S0", "0")) * B.fps))      # FALL2_S0: re-render a tail only
    return [j / B.fps for j in range(j0, int(round(s1 * B.fps)))]

# ================================================================ SEGMENT 3: the Armored, ferries, the vow
SEG3 = 12.0
# light at segment 3's end (constant over the segment): agent G's long flight starts from exactly this
SEG3_END_LIGHT = dict(sun_elevation_deg=float(os.environ.get("FALL_SUN_EL", "4")), sun_azimuth_deg=float(os.environ.get("FALL_SUN_AZ", "245")),
                      sun_color=(1.0, 0.50, 0.20), sun_energy=float(os.environ.get("CARLA_SUN_E", "4.2")),
                      exposure=float(os.environ.get("EXPO", "-1.5")),
                      sky_ramp=((1.0, 0.62, 0.22, 1.0), (0.95, 0.66, 0.38, 1.0)), view_transform="scene.py default (VT env)")
IMPACT = 5.0
FXT = 100.0              # fx845 time base: the kick FX are long settled; the inner burst is registered at FXT + IMPACT
FERRY_V = 6.0              # timelapse
LEAD_S0 = 30.0

def dress_fields(c=(0.0, 1500.0), ra=1450.0, rb=2600.0, band=240.0, strip=60.0):
    """Wall Maria farmland north of the inner wall: strip fields with hedgerows and pale tracks, mixed into the shared
    Terrain material at runtime inside an ellipse (centre c, radii ra north / rb east) -- after march846.dress_fields."""
    m = bpy.data.materials.get("Terrain")
    if m is None or not m.use_nodes:
        return
    nt = m.node_tree; N, Lk = nt.nodes, nt.links
    bsdf = next((n for n in N if n.type == "BSDF_PRINCIPLED"), None)
    if bsdf is None or not bsdf.inputs["Base Color"].is_linked:
        return
    base = bsdf.inputs["Base Color"].links[0].from_socket
    geo = N.new("ShaderNodeNewGeometry"); sep = N.new("ShaderNodeSeparateXYZ"); Lk.new(geo.outputs["Position"], sep.inputs[0])
    def M_(op, a, b=None):
        n = N.new("ShaderNodeMath"); n.operation = op
        for k, x in enumerate((a, b)):
            if x is None:
                continue
            if isinstance(x, (int, float)):
                n.inputs[k].default_value = x
            else:
                Lk.new(x, n.inputs[k])
        return n.outputs[0]
    da = M_("SUBTRACT", sep.outputs["Y"], c[1]); db = M_("SUBTRACT", sep.outputs["X"], c[0])
    ia = M_("FLOOR", M_("DIVIDE", da, band))
    wn1 = N.new("ShaderNodeTexWhiteNoise"); wn1.noise_dimensions = "1D"; Lk.new(ia, wn1.inputs["W"])
    jb_f = M_("ADD", M_("DIVIDE", db, strip), M_("MULTIPLY", wn1.outputs["Value"], 7.0)); jb = M_("FLOOR", jb_f)
    cmb = N.new("ShaderNodeCombineXYZ"); Lk.new(ia, cmb.inputs["X"]); Lk.new(jb, cmb.inputs["Y"])
    wn2 = N.new("ShaderNodeTexWhiteNoise"); wn2.noise_dimensions = "3D"; Lk.new(cmb.outputs[0], wn2.inputs["Vector"])
    pal = N.new("ShaderNodeValToRGB"); pal.color_ramp.interpolation = "CONSTANT"; pe = pal.color_ramp.elements
    cols = [(0.0, (0.40, 0.33, 0.13)), (0.16, (0.17, 0.28, 0.07)), (0.30, (0.25, 0.17, 0.10)), (0.44, (0.50, 0.42, 0.18)),
            (0.58, (0.20, 0.31, 0.08)), (0.72, (0.33, 0.32, 0.12)), (0.86, (0.14, 0.25, 0.06))]
    pe[0].position, pe[0].color = cols[0][0], (*cols[0][1], 1); pe[1].position, pe[1].color = cols[1][0], (*cols[1][1], 1)
    for pp, cc in cols[2:]:
        pal.color_ramp.elements.new(pp).color = (*cc, 1)
    Lk.new(wn2.outputs["Value"], pal.inputs["Fac"])
    fa = M_("FRACT", M_("DIVIDE", da, band)); ea = M_("MULTIPLY", M_("MINIMUM", fa, M_("SUBTRACT", 1.0, fa)), band)
    hedge = N.new("ShaderNodeMapRange"); hedge.inputs["From Min"].default_value = 1.2; hedge.inputs["From Max"].default_value = 2.6
    Lk.new(ea, hedge.inputs["Value"])
    fm = N.new("ShaderNodeMix"); fm.data_type = "RGBA"; fm.inputs["A"].default_value = (0.05, 0.09, 0.03, 1)
    Lk.new(hedge.outputs["Result"], fm.inputs["Factor"]); Lk.new(pal.outputs["Color"], fm.inputs["B"])
    e2 = M_("ADD", M_("MULTIPLY", M_("DIVIDE", da, ra), M_("DIVIDE", da, ra)), M_("MULTIPLY", M_("DIVIDE", db, rb), M_("DIVIDE", db, rb)))
    me_ = N.new("ShaderNodeMapRange"); me_.inputs["From Min"].default_value = 1.0; me_.inputs["From Max"].default_value = 0.8
    Lk.new(e2, me_.inputs["Value"])
    fin = N.new("ShaderNodeMix"); fin.data_type = "RGBA"
    Lk.new(me_.outputs["Result"], fin.inputs["Factor"]); Lk.new(base, fin.inputs["A"]); Lk.new(fm.outputs["Result"], fin.inputs["B"])
    Lk.new(fin.outputs["Result"], bsdf.inputs["Base Color"])

def seg3_build():
    S = {}
    if os.environ.get("FALL_FIELDS", "1") == "1":
        dress_fields()
    # light: the golden low sun of render_fall's end (same values: the seam must match)
    set_sun(float(os.environ.get("FALL_SUN_EL", "4")), float(os.environ.get("FALL_SUN_AZ", "245")), (1.0, 0.50, 0.20),
            float(os.environ.get("CARLA_SUN_E", "4.2")))
    w = sc.world
    if w and w.use_nodes:
        for nd in w.node_tree.nodes:
            if nd.type == "VALTORGB":
                e = nd.color_ramp.elements
                e[0].color = (1.0, 0.62, 0.22, 1); e[1].color = (0.95, 0.66, 0.38, 1)
    # the Armored Titan
    import shifters as SH
    t0 = time.time()
    rig = SH.make_armored("ArmoredTitan")
    rig["gait"] = dict(stride=0.75, knee=1.0, sway=0.015, bob=0.04, arm=0.65, limp=0.0)
    rig["slouch"] = 0.5; rig["arms_out"] = 0.85; rig["gait_seed"] = 3
    k = float(os.environ.get("FALL_ARM_SCALE", "1.3"))        # read from the sky over 8-17 m houses
    rig.scale = tuple(v * k for v in rig.scale)
    if rig.animation_data:
        rig.animation_data.action = None
    S["arm"] = rig
    print(f"[fall2] Armored built {time.time() - t0:.0f}s")
    # inner gate pieces (states845 armored build): shown only from the impact on
    S["inner_mods"] = [m for m in bpy.data.objects["InnerGate"].modifiers if m.type == "BOOLEAN"] if bpy.data.objects.get("InnerGate") else []
    S["inner_after"] = [o for o in bpy.data.objects if o.name.startswith(("InnerGate_Grime", "InnerDust"))]
    hl = bpy.data.objects.get("InnerHoleLight")      # the hole full of light (anime ep02 10:22): shown only once the dust
    S["hole_light"] = hl                             # of the ram thins (before that it reads as a white slab)
    if hl:
        hl.hide_render = True
        if FX:
            FX.REG["appear"] = [a_ for a_ in FX.REG["appear"] if a_[0] is not hl]
    S["inner_door"] = None                          # (states845's InnerGate_Door renders as a white slab: the base
    if FX:                                          #  gatehouse door shows while the booleans are off)
        FX.REG["mods"] = [m for m in FX.REG["mods"] if m not in S["inner_mods"]]     # we drive the inner breach
    d0 = bpy.data.objects.get("InnerGate_Door")
    if d0:
        d0.hide_render = True
        FX.REG["appear"] = [a for a in FX.REG["appear"] if a[0] is not d0] if FX else []
    S["smoke"] = [o for o in bpy.data.objects if o.name.startswith(("FireSmoke", "FlameSmoke", "SmokeCanopy"))]
    # the burst: blocks + dust registered in fx845 at FXT + IMPACT
    if FX:
        rnd = random.Random(12)
        stone = L.mat("Burst_stone", (0.42, 0.40, 0.37), 0.9)
        import bmesh
        for k in range(16):
            bm = bmesh.new(); sz = rnd.uniform(1.2, 3.2)
            L.box(bm, (0, 0, 0), (sz, sz * rnd.uniform(0.6, 1.0), sz * rnd.uniform(0.5, 0.9)))
            ob = L.obj_from_bm(f"BurstBlock{k}", bm, [stone], coll)
            p0 = Vector((rnd.uniform(-6, 6), rnd.uniform(-2, 3), rnd.uniform(3, 20)))
            d = rnd.uniform(40, 150); a = rnd.uniform(-0.7, 0.7)
            p1 = Vector((p0.x + math.sin(a) * d, p0.y + math.cos(a) * d, 0.0)); p1.z = L.height(p1.x, p1.y) + sz * 0.3
            FX.add_block(ob, FXT + IMPACT + rnd.uniform(0, 0.12), 0.9 + d / 110, p0, p1, rnd.uniform(8, 25),
                         Vector((math.sin(a), math.cos(a), 0)) * rnd.uniform(2, 6), 300 + k, trail=2, coll=coll)
        for k in range(26):
            c = Vector((rnd.uniform(-9, 9), rnd.uniform(-6, 14), rnd.uniform(2, 22)))
            v = Vector((rnd.uniform(-10, 10), rnd.uniform(4, 30), rnd.uniform(0, 6)))
            FX.add_puff(coll, c, FXT + IMPACT + rnd.uniform(0, 0.25), v, 0.6, 1.2, 3.0, rnd.uniform(9, 16), rnd.uniform(3.5, 6.0),
                        (0.62, 0.53, 0.40), 0.85)
    # ferries on the canal north of the water gate + the kids at the lead ferry's bow
    S["ferries"] = []
    for i, (s0, side) in enumerate(((10.0, -3.0), (LEAD_S0, 4.0), (56.0, -2.5), (84.0, 3.5), (118.0, -1.5))):
        ob, Lb = SC.boat(f"Ferry{i}", 30 + i, coll, crowd=False)      # refugees: minimal figures (below), not blocks
        rb = random.Random(30 + i); rb.uniform(14, 17); Bb = rb.uniform(3.6, 4.1)
        S["ferries"].append((ob, Lb, s0, side))
        S.setdefault("bb", []).append(Bb)
    # refugees on every ferry (minimal swarm figures riding the ferry transforms; a gap at the lead bow for the kids)
    slots = []
    rnd = random.Random(17)
    for fi, (ob, Lb, s0, side) in enumerate(S["ferries"]):
        Bb = S["bb"][fi]; gap = 0.0
        nx_, ny_ = int((Lb - 3.2 - gap) / 0.75), int((Bb - 0.9) / 0.7)
        for a in range(nx_):
            for b in range(ny_):
                x = -Lb / 2 + 1.0 + a * 0.75 + rnd.uniform(-0.15, 0.15); y = -Bb / 2 + 0.45 + b * 0.7 + rnd.uniform(-0.1, 0.1)
                slots.append((fi, x, y, rnd.uniform(-1.2, 1.2)))
    S["slots"] = np.array(slots)
    S["folk"] = MiniCrowd("FerryFolk", len(slots), 23, coll)
    # warm light behind the burst inner gate (north side): the breach reads as a bright hole
    ld = bpy.data.lights.new("BreachLight", "AREA"); ld.shape = "RECTANGLE"; ld.size, ld.size_y = 26.0, 30.0
    ld.color = (1.0, 0.72, 0.42); ld.energy = 0.0
    lo = bpy.data.objects.new("BreachLight", ld); coll.objects.link(lo)
    lo.location = (0.0, 14.0, 14.0); lo.rotation_euler = (math.radians(-90), 0.0, 0.0)     # facing south through the hole
    S["breach_light"] = ld
    # the crowd jamming the west bank of the canal north of the wall, pressing toward the water
    n = int(os.environ.get("FALL_JAM_N", "260"))
    S["jam"] = MiniCrowd("Jam", n, 7, coll)
    rnd = random.Random(3)
    J = []
    for i in range(n):
        y = rnd.uniform(14, 120); xb = SC.canal_at(max(0.0, y - 8))[0].x - L.CANAL_W / 2 - 1.0
        J.append((xb - rnd.uniform(1.5, 26) * (1 + rnd.random()), y + rnd.uniform(-3, 3), xb - rnd.uniform(0.6, 4.0), rnd.uniform(0, 6)))
    S["J"] = np.array(J)
    # crowd streaming through the burst inner gate after the impact
    S["gate"] = MiniCrowd("GateRun", 140, 9, coll)
    S["G"] = np.array([(rnd.uniform(-5, 5), rnd.uniform(-90, -12), rnd.uniform(-60, 60), rnd.uniform(30, 120), rnd.uniform(3.0, 4.5), rnd.uniform(0, 2.5))
                       for _ in range(140)])
    # a REAL gate in the flat gatehouse before the ram: plank door + iron portcullis bars (user 10/25)
    import bmesh
    wood = L.mat("Gate_wood", (0.20, 0.12, 0.06), 0.85); iron = L.mat("Gate_iron", (0.07, 0.07, 0.08), 0.5)
    bm = bmesh.new()
    gw, gh = L.GATE_W - 0.4, L.GATE_H - 0.3
    for k in range(9):                               # vertical planks
        L.box(bm, (-gw / 2 + gw * (k + 0.5) / 9, -4.2, gh / 2), (gw / 9 - 0.08, 0.5, gh), mi=0)
    for z in (2.5, 7.5, 12.5, 17.5):                 # iron bands
        L.box(bm, (0, -4.55, z), (gw, 0.2, 0.5), mi=1)
    for k in range(7):                               # portcullis bars in front
        L.box(bm, (-gw / 2 + gw * (k + 0.5) / 7, -5.0, gh / 2), (0.3, 0.3, gh), mi=1)
    door = L.obj_from_bm("InnerGateDoorReal", bm, [wood, iron], coll)
    door.location.z = L.height(0, -4) + 0.05
    S["door"] = door
    if FX:                                           # the door explodes: planks and bars thrown north with the stones
        rnd = random.Random(44)
        for k in range(22):
            bm = bmesh.new()
            if k % 3 == 2:
                L.box(bm, (0, 0, 0), (0.3, 0.3, rnd.uniform(3, 8)), mi=1)
            else:
                L.box(bm, (0, 0, 0), (rnd.uniform(1.0, 1.6), 0.5, rnd.uniform(2.5, 7)), mi=0)
            ob = L.obj_from_bm(f"DoorPlank{k}", bm, [wood, iron], coll)
            p0 = Vector((rnd.uniform(-6, 6), -4.0, rnd.uniform(2, 17)))
            dd = rnd.uniform(25, 120); a = rnd.uniform(-0.9, 0.9)
            p1 = Vector((p0.x + math.sin(a) * dd, p0.y + math.cos(a) * dd, 0.0)); p1.z = L.height(p1.x, p1.y) + 0.3
            FX.add_block(ob, FXT + IMPACT + rnd.uniform(0, 0.08), 0.7 + dd / 120, p0, p1, rnd.uniform(6, 22),
                         Vector((math.sin(a), math.cos(a), 0)) * rnd.uniform(2, 8), 400 + k, spin=(3.0, 8.0))
    try:                                             # dust CARDS bursting out of both sides of the hole
        import smokecards as SMK
        dc = SMK.SmokeCards("BreachDust")
        rnd = np.random.default_rng(5)
        n = 160
        te = IMPACT + rnd.uniform(0, 0.5, n)
        pos = np.c_[rnd.uniform(-8, 8, n), rnd.uniform(-8, 8, n), rnd.uniform(1, 20, n)]
        vel = np.c_[rnd.uniform(-14, 14, n), np.where(rnd.random(n) < 0.75, rnd.uniform(6, 30, n), rnd.uniform(-18, -4, n)), rnd.uniform(0, 7, n)]
        dc.add_many(te, pos, vel, 3.0, 16.0, 6.0, 1.5, kind="dust", alpha=0.85, tau=0.8)
        dc.build(coll); S["dustcards"] = dc
    except Exception as ex:
        print("[fall2] dust cards failed:", ex)
    # refugees fleeing north over Wall Maria's land: the road north of the gate and along the canal (true scale)
    n = int(os.environ.get("FALL_REF_N", "1400"))       # a dense stream, tight on the canal bank and the road
    S["ref"] = MiniCrowd("Refugees", n, 31, coll)
    rnd = random.Random(29)
    R = []
    for i in range(n):
        if i % 20 < 11:
            y0 = rnd.uniform(20, 560); x0 = SC.canal_at(max(0.0, y0 - 8))[0].x - L.CANAL_W / 2 - rnd.uniform(2.0, 7.5)
        else:
            y0 = rnd.uniform(30, 620); t_ = (y0 - 6) / 120; x0 = math.sin(t_ / 9) * 120 * (t_ / 40) + rnd.uniform(-3.5, 3.5)
        R.append((x0, y0, rnd.uniform(1.1, 1.6), rnd.uniform(-0.03, 0.03)))
    S["R"] = np.array(R)
    S["cam"] = seg3_cam_keys(S)
    return S

def ferry_place(ob, s0, side, s):
    p, d = SC.canal_at(s0 + FERRY_V * s)
    nrm = Vector((-d.y, d.x)); p = p + nrm * side
    ob.location = (p.x, p.y, L.height(p.x, p.y) + 2.2 - 0.55 + 0.05 * math.sin(s * 1.3 + s0))
    ob.rotation_euler = (0.0, 0.0, math.atan2(d.y, d.x))
    return p

def armored_y(s):
    if s < IMPACT:
        u = s / IMPACT
        return -190.0 + 181.0 * (0.4 * u + 0.6 * u * u)
    return -9.0 + 17.0 * (1 - math.exp(-(s - IMPACT) / 0.6))

SEAM_IN = ((8.0, L.OUTER_GATE[1] + 186, 94.0), (-34.0, L.OUTER_GATE[1] + 72, 0.0), 32.0)   # = render_fall's last key (at rest)

def seg3_cam_keys(S):
    """Sky observer at a moderate height, one take: from render_fall's last pose up the avenue behind the charge,
    the ram, over the wall, then north with the boats and the refugees (ends moving north ~40 m/s: hand-off to G)."""
    l0, t0, n0 = SEAM_IN
    ks = [
        (-1.0, l0, t0, n0),                                  # (guide: at rest at the seam)
        (0.0, l0, t0, n0),
        (3.0, (60, -300, 120), (0, -90, 0), 32),             # flying north up the avenue, the Armored charging ahead
        (3.6, (40, -118, 95), (0, -30, 8), 32),              # nearer (~130 m) for the run and the shoulder ram
        (IMPACT, (35, -100, 84), (0, -6, 12), 32),           # the ram: the gate explodes
        (6.4, (95, -45, 118), (190, 60, 0), 30),             # pull up over the wall, turning to the canal
        (8.0, (195, 10, 95), (222, 110, 0), 30),             # low (~95 m) over the canal: ferries, refugees on bank + road
        (10.0, (200, 80, 112), (228, 190, 0), 29),           # ... then climb north
        (SEG3, (180, 165, 215), (232, 340, 0), 28),
        (SEG3 + 1.0, (184, 207, 225), (234, 384, 0), 28),    # (guide: keeps moving north ~42 m/s for the hand-off)
    ]
    return ks

def seg3_pose(S, s):
    if FX:
        FX.update(FXT + s)
    burst = s >= IMPACT
    for m in S["inner_mods"]:                       # only touch on change: re-tagging re-evaluates the wall booleans
        if m.show_render != burst:
            m.show_render = m.show_viewport = burst
    for o in S["inner_after"]:
        if o.hide_render != (not burst):
            o.hide_render = not burst
    if S["door"].hide_render != burst:
        S["door"].hide_render = burst
    hl = S.get("hole_light")
    if hl and hl.hide_render != (s < IMPACT + 0.7):
        hl.hide_render = s < IMPACT + 0.7
    if S.get("dustcards"):
        S["dustcards"].update(s)
    # the Armored: charge (head down, shoulder first), then stands in the burst gate
    rig = S["arm"]; y = armored_y(s)
    dist = (y + 190.0)
    p = (dist / 26.0) % 1.0 if s < IMPACT + 0.8 else 0.22
    rots, off = PT._gait(rig, p, amp=1.0 if s < IMPACT + 0.5 else max(0.0, 1 - (s - IMPACT - 0.5) / 0.5))
    off, _, _ = PT._ground(rig, rots, off)
    PT._apply(rig, rots, off)
    rig.location = (0.0, y, L.height(0.0, y) - 0.1)
    if os.environ.get("FALL_DEBUG"):
        bpy.context.view_layer.update()
        print("[fall2 dbg] armored", tuple(round(v, 1) for v in rig.location), rig.hide_render, tuple(round(v, 2) for v in rig.scale),
              [(c.name, c.hide_render, tuple(round(v, 1) for v in c.dimensions)) for c in rig.children][:4], rig.rotation_mode)
        dg = bpy.context.evaluated_depsgraph_get()
        for c in rig.children[:1]:
            ce = c.evaluated_get(dg); me = ce.to_mesh()
            ws = [ce.matrix_world @ v.co for v in me.vertices]
            print("[fall2 dbg] body world bbox", [round(min(w[i] for w in ws), 1) for i in range(3)], [round(max(w[i] for w in ws), 1) for i in range(3)],
                  "users_collection", [cc.name for cc in c.users_collection], "visible_camera", c.visible_camera)
            ce.to_mesh_clear()
    ram = smooth(IMPACT - 1.2, IMPACT - 0.3, s) * (1 - smooth(IMPACT + 0.6, IMPACT + 1.6, s))   # lowered-shoulder ram
    lean = 0.2 if s < IMPACT + 0.4 else 0.2 * (1 - smooth(IMPACT + 0.4, IMPACT + 1.4, s))
    rig.rotation_euler = (lean + 0.15 * ram, 0.28 * ram, math.pi + 0.75 * ram)
    # swarm: the district behind (titans keep wandering / eating); sim t continues from segment 2
    SW.update(68.0 + 1.5 * s, pscale=1.0)          # user rule: true scale
    # ferries + their refugees
    for ob, Lb, s0, side in S["ferries"]:
        ferry_place(ob, s0, side, s)
    bpy.context.view_layer.update()
    sl = S["slots"]; nf = len(sl)
    P = np.zeros((nf, 3)); Y = np.zeros(nf)
    for fi, (ob, Lb, s0, side) in enumerate(S["ferries"]):
        m = sl[:, 0] == fi
        mw = np.array(ob.matrix_world)
        loc = np.c_[sl[m, 1], sl[m, 2], np.full(m.sum(), 0.97), np.ones(m.sum())] @ mw.T
        P[m] = loc[:, :3]; Y[m] = ob.rotation_euler.z - math.pi / 2 + sl[m, 3]
    S["folk"].set(P, Y, np.zeros(nf), np.zeros(nf), arms_up=np.where(np.arange(nf) % 5 == 0, 0.6 + 0.2 * np.sin(s * 3 + np.arange(nf)), 0.0))
    S["breach_light"].energy = float(os.environ.get("FALL_BREACH_W", "2.5e5")) * smooth(IMPACT, IMPACT + 0.4, s)
    # the bank crowd: pressing toward the water, jostling, arms up as the boats leave
    J = S["J"]; n = len(J)
    k = np.clip((s + J[:, 3]) / 9.0, 0, 1) ** 0.7
    x = J[:, 0] + (J[:, 2] - J[:, 0]) * k + 0.25 * np.sin(s * 2.1 + np.arange(n))
    pos = np.stack([x, J[:, 1] + 0.3 * np.cos(s * 1.7 + np.arange(n)), np.full(n, 0.0)], 1)
    pos[:, 2] = [L.height(a, b) + 0.05 for a, b in pos[:, :2]] if not hasattr(seg3_pose, "_z") else seg3_pose._z
    seg3_pose._z = pos[:, 2].copy()
    mv = np.clip(1 - k, 0.15, 1.0)
    arms = np.where(np.arange(n) % 3 == 0, 2.4 + 0.3 * np.sin(s * 6 + np.arange(n)), 0.0) * smooth(4.0, 6.0, s)
    S["jam"].set(pos, np.full(n, -math.pi / 2) + 0.3 * np.sin(np.arange(n)), x * 0 + s * 2.0 * mv, mv, arms_up=arms)
    # runners through the burst gate (north), visible after the impact
    G = S["G"]; m = len(G)
    tt = np.clip(s - IMPACT - 0.8 - G[:, 5], 0, None)
    d = tt * G[:, 4]
    start = np.stack([G[:, 0], G[:, 1]], 1); goal = np.stack([G[:, 2], G[:, 3]], 1)
    gatep = np.array([0.0, 6.0])
    l1 = np.linalg.norm(gatep - start, axis=1); l2 = np.linalg.norm(goal - gatep, axis=1)
    u1 = np.clip(d / l1, 0, 1)[:, None]; u2 = np.clip((d - l1) / l2, 0, 1)[:, None]
    P = np.where((d < l1)[:, None], start + (gatep - start) * u1, gatep + (goal - gatep) * u2)
    vis = np.where(s >= IMPACT + 0.8, 1.0, 0.0) * np.ones(m)
    dirv = np.where((d < l1)[:, None], gatep - start, goal - gatep)
    yaw = np.arctan2(-dirv[:, 0], dirv[:, 1])
    mvg = np.where((d > 0) & (d < l1 + l2), 1.0, 0.0)
    S["gate"].set(np.c_[P, np.full(m, 0.2)], yaw, d, mvg, vis=vis)
    # refugees walking north (timelapse x3)
    R = S["R"]; nr = len(R)
    yr = R[:, 1] + R[:, 2] * 3.0 * s; xr = R[:, 0] + R[:, 3] * 3.0 * s
    zr = np.array([L.height(a, b) + 0.05 for a, b in zip(xr, yr)])
    S["ref"].set(np.c_[xr, yr, zr], np.full(nr, 0.0) - R[:, 3], R[:, 2] * 3.0 * s, np.ones(nr), stride=1.5 * S["ref"].h * 3.0)
    # camera (+ impact shake)
    loc, tgt, lens = spline_cam(S["cam"], s)
    if IMPACT <= s < IMPACT + 0.8:
        a = (1 - (s - IMPACT) / 0.8) * 1.6
        loc = loc + Vector((noise.noise(Vector((s * 40, 0, 0))), noise.noise(Vector((0, s * 40, 3))), noise.noise(Vector((5, 1, s * 40))))) * a
    if os.environ.get("FALL_CAMDBG"):                # debug: a fixed camera "x,y,z,tx,ty,tz,lens"
        v = [float(x) for x in os.environ["FALL_CAMDBG"].split(",")]
        loc, tgt, lens = Vector(v[:3]), Vector(v[3:6]), v[6]
    for o in S["smoke"]:                            # never fly the camera through a smoke column
        near = (o.matrix_world.translation.to_2d() - loc.to_2d()).length < 55
        if near and not o.hide_render:
            o.hide_render = True
    look(cam, loc, tgt, lens)
    if os.environ.get("FALL_DEBUG"):
        bpy.context.view_layer.update()
        dg = bpy.context.evaluated_depsgraph_get()
        d = (tgt - loc).normalized()
        hit, hp, nn, idx, ob, mtx = sc.ray_cast(dg, loc, d)
        print(f"[fall2 dbg] s={s:.2f} cam {tuple(round(v, 1) for v in loc)} -> {tuple(round(v, 1) for v in tgt)} hit {ob.name if hit else None} at {round((hp - loc).length, 1) if hit else None}")

# ================================================================ SEGMENT 4: night pull-up, the grey belt
SEG4 = 12.0
SEG5 = 5.0
GLITCH_S = 4.7

def grey_belt():
    """Insert a mask into the terrain material: land north of Wall Maria (y > 0) south of the front turns grey."""
    ter = next((o for o in bpy.data.objects if o.type == "MESH" and o.name.lower().startswith("terrain")), None)
    if not ter or not ter.data.materials:
        print("[fall2] no terrain material for the grey belt"); return None
    m = ter.data.materials[0]; nt = m.node_tree; N = nt.nodes; Lk = nt.links
    bsdf = next((n for n in N if n.type == "BSDF_PRINCIPLED"), None)
    if bsdf is None:
        return None
    src = bsdf.inputs["Base Color"].links[0].from_socket if bsdf.inputs["Base Color"].links else None
    geo = N.new("ShaderNodeNewGeometry"); sep = N.new("ShaderNodeSeparateXYZ"); Lk.new(geo.outputs["Position"], sep.inputs[0])
    front = N.new("ShaderNodeValue"); front.outputs[0].default_value = -1000.0; front.name = "GreyFront"
    sub = N.new("ShaderNodeMath"); sub.operation = "SUBTRACT"; Lk.new(front.outputs[0], sub.inputs[0]); Lk.new(sep.outputs["Y"], sub.inputs[1])
    f1 = N.new("ShaderNodeMapRange"); Lk.new(sub.outputs[0], f1.inputs["Value"]); f1.inputs["From Min"].default_value = 0.0; f1.inputs["From Max"].default_value = 350.0
    f0 = N.new("ShaderNodeMapRange"); Lk.new(sep.outputs["Y"], f0.inputs["Value"]); f0.inputs["From Min"].default_value = 0.0; f0.inputs["From Max"].default_value = 30.0
    mul = N.new("ShaderNodeMath"); mul.operation = "MULTIPLY"; Lk.new(f1.outputs[0], mul.inputs[0]); Lk.new(f0.outputs[0], mul.inputs[1])
    mix = N.new("ShaderNodeMix"); mix.data_type = "RGBA"
    Lk.new(mul.outputs[0], mix.inputs["Factor"])
    if src:
        Lk.new(src, mix.inputs[6])
    else:
        mix.inputs[6].default_value = tuple(bsdf.inputs["Base Color"].default_value)
    mix.inputs[7].default_value = (0.20, 0.20, 0.22, 1)
    Lk.new(mix.outputs[2], bsdf.inputs["Base Color"])
    # a faint cold glow so the grey reads at night
    em = bsdf.inputs.get("Emission Color"); es = bsdf.inputs.get("Emission Strength")
    if em is not None and es is not None and not es.links:
        Lk.new(mix.outputs[2], em)
        k = N.new("ShaderNodeMath"); k.operation = "MULTIPLY"; Lk.new(mul.outputs[0], k.inputs[0]); k.inputs[1].default_value = 0.15
        Lk.new(k.outputs[0], es)
    return front

def seg45_build():
    S = {}
    S["front"] = grey_belt()
    # pure titans spreading north over Wall Maria's land (minimal swarm titans, ~1.4x so they read from high up)
    n = int(os.environ.get("FALL_NT", "70"))
    S["nt"] = MiniCrowd("NorthTitans", n, 21, coll, titans=1.4)
    rnd = random.Random(5)
    S["T"] = np.array([(rnd.uniform(-30, 30), rnd.uniform(15, 60), rnd.uniform(-0.9, 0.9), rnd.uniform(4.0, 9.0), rnd.uniform(-6, 2))
                       for _ in range(n)])
    S["tz"] = None
    # burning town without volumes (Eevee): fire + dark smoke CARDS (smokecards) at every fire light of states845
    if os.environ.get("AOT_NOSMOKE") == "1":
        import smokecards as SMK
        fires = [o.matrix_world.translation.copy() for o in bpy.data.objects if o.type == "LIGHT" and o.name.startswith("FireL")]
        rnd = random.Random(8)
        fc = SMK.SmokeCards("NightFire"); sm = SMK.SmokeCards("NightSmoke")
        for k, p in enumerate(fires):
            g = L.height(p.x, p.y) + 0.5
            big = 0.7 + 0.6 * rnd.random()
            te = np.arange(-12.0, SEG4 + 1.0, 0.22 + 0.1 * rnd.random())
            n = len(te)
            pos = np.c_[np.full(n, p.x) + np.random.uniform(-3, 3, n) * big, np.full(n, p.y) + np.random.uniform(-3, 3, n) * big, np.full(n, g)]
            fc.add_many(te, pos, None, 2.0 * big, 5.5 * big, 1.3, 4.0, kind="fire", alpha=0.9)
            te2 = np.arange(-30.0, SEG4 + 1.0, 0.7 + 0.3 * rnd.random()); n2 = len(te2)
            pos2 = np.c_[np.full(n2, p.x), np.full(n2, p.y), np.full(n2, g + 8 * big)]
            sm.add_many(te2, pos2, None, 5.0 * big, 26.0 * big, 22.0, 7.0, color=(0.13, 0.10, 0.09), kind="smoke", alpha=0.75)
        fc.build(coll); sm.build(coll)
        S["cards"] = (fc, sm)
        print(f"[fall2] night fire cards at {len(fires)} fires")
    # Grisha beat set
    S["g"] = seg5_build()
    return S

def seg4_pose(S, s):
    if FX:
        FX.update(FXT + 30.0 + s)
    for c in S.get("cards", ()):
        c.update(s, wind=(1.5, 3.0))
    SW.update(120.0 + 3.0 * s, pscale=1.0)
    if S["front"] is not None:
        S["front"].outputs[0].default_value = -400.0 + 7200.0 * smooth(2.5, SEG4, s) ** 1.3
    T = S["T"]; n = len(T)
    tt = np.clip(s - T[:, 4], 0, None) * 6.0                    # timelapse: they walk ~6x
    d = 30 + tt * T[:, 3]
    x = T[:, 0] + np.sin(T[:, 2]) * d; y = T[:, 1] + np.cos(T[:, 2]) * d
    if S["tz"] is None or s == 0:
        pass
    z = np.array([L.height(a, b) for a, b in zip(x, y)])
    S["nt"].set(np.c_[x, y, z], np.full(n, 0.0) - T[:, 2], d, np.ones(n), stride=0.55 * S["nt"].h + 0.5)
    ks = guide([
        (0.0, (80, -420, 150), (0, -250, 0), 30),           # over the burning town
        (4.0, (60, -620, 420), (0, 200, 0), 28),            # pull up and back: the wall, the burst gate, the titans
        (SEG4, (0, -1500, 1650), (0, 2600, 0), 26),          # the Maria belt turning grey to the north
    ])
    loc, tgt, lens = spline_cam(ks, s)
    can = bpy.data.objects.get("SmokeCanopy")       # the orange smoke canopy: lovely from inside the town, a blinding
    if can:                                         # slab once the camera climbs through it
        hide = loc.z > float(os.environ.get("FALL_CANOPY_Z", "130"))
        if can.hide_render != hide:
            can.hide_render = hide
    near_smoke(S, loc)
    look(cam, loc, tgt, lens)

def near_smoke(S, loc):
    for o in S.setdefault("smoke", [o for o in bpy.data.objects if o.name.startswith(("FireSmoke", "FlameSmoke"))]):
        if (o.matrix_world.translation.to_2d() - loc.to_2d()).length < 55 and not o.hide_render:
            o.hide_render = True

def seg5_build():
    import people_kit as PK
    G = {}
    gf = L.GF
    trees = [o.location.to_2d() for o in bpy.data.objects if o.name.startswith("GT")]
    best = None
    for k in range(400):                                   # a clearing near the forest edge (south side)
        a = k * 2.399; r = 120 + (k % 20) * 25
        c = Vector((gf.x + math.cos(a) * r * 1.3, gf.y + math.sin(a) * r))
        dmin = min(((c - t).length for t in trees), default=99)
        sc_ = abs(dmin - 24.0)                         # a small clearing: giant trees ~24 m away frame the figures
        if best is None or sc_ < best[0]:
            best = (sc_, c)
    C = best[1]; G["C"] = C
    zc = L.height(C.x, C.y)
    PK._PROTO.clear()
    # Grisha leading Eren in (walk phases), then standing / kneeling
    G["gw"] = [PK.person("grisha", (C.x, C.y), pose="walk", phase=k / 4) for k in range(4)]
    G["ew"] = [PK.person("eren_child", (C.x, C.y), pose="walk", phase=k / 4) for k in range(4)]
    G["gs"] = PK.person("grisha", (C.x, C.y), pose="stand")
    G["ek"] = PK.person("eren_child", (C.x, C.y), pose="kneel")
    G["es"] = PK.person("eren_child", (C.x, C.y), pose="stand")
    for e in G["gw"] + G["ew"] + [G["gs"], G["ek"], G["es"]]:
        e.hide_render = True
    # lantern, syringe glint, key
    def emis(name, col, strength, r, seg=8):
        import bmesh
        bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=seg // 2 + 1, radius=r)
        m = bpy.data.materials.new(name + "M"); m.use_nodes = True; Nn = m.node_tree.nodes; Nn.remove(Nn["Principled BSDF"])
        e = Nn.new("ShaderNodeEmission"); e.inputs["Color"].default_value = (*col, 1); e.inputs["Strength"].default_value = strength
        m.node_tree.links.new(e.outputs[0], Nn["Material Output"].inputs["Surface"])
        ob = L.obj_from_bm(name, bm, [m], coll); ob.visible_shadow = False
        return ob, e
    G["lan"], _ = emis("Lantern", (1.0, 0.62, 0.25), 25.0, 0.14)
    ld = bpy.data.lights.new("LanternLight", "POINT"); ld.color = (1.0, 0.6, 0.25); ld.energy = 900; ld.shadow_soft_size = 0.2
    lo = bpy.data.objects.new("LanternLight", ld); coll.objects.link(lo); G["lamp"] = lo
    G["syr"], G["syr_e"] = emis("SyringeGlint", (0.75, 0.9, 1.0), 0.0, 0.07)
    G["key"], G["key_e"] = emis("KeyGlint", (1.0, 0.78, 0.3), 0.0, 0.06)
    fl = bpy.data.lights.new("InjFlash", "POINT"); fl.color = (0.8, 0.9, 1.0); fl.energy = 0; fl.shadow_soft_size = 1.0
    fo = bpy.data.objects.new("InjFlash", fl); coll.objects.link(fo); G["flash"] = fo
    G["z"] = zc
    return G

def seg5_pose(S, s):
    G = S["g"]; C = G["C"]; zc = G["z"] + 0.16
    if S.get("front") is not None:
        S["front"].outputs[0].default_value = -1000.0         # (845 night: the forest floor is not part of the grey belt)
    if FX:
        FX.update(FXT + 50.0)
    fwd = Vector((0.6, 0.8)).normalized()                     # they walk in along fwd, stop at the clearing centre
    walk = s < 2.2
    k = min(1.0, s / 2.2)
    dg = (1 - (1 - k) ** 1.5) * 9.0
    gp = C - fwd * (9.0 - dg); ep = gp - fwd * 1.4 + Vector((-fwd.y, fwd.x)) * 0.6
    yaw_g = math.atan2(-fwd.x, fwd.y)
    ph = int((s * 1.6 / 0.9 * 4)) % 4
    for i in range(4):
        G["gw"][i].hide_render = not (walk and i == ph); G["ew"][i].hide_render = not (walk and i == ph)
        G["gw"][i].location = (gp.x, gp.y, zc); G["gw"][i].rotation_euler = (0, 0, yaw_g)
        G["ew"][i].location = (ep.x, ep.y, zc); G["ew"][i].rotation_euler = (0, 0, yaw_g)
    G["gs"].hide_render = walk
    kneel = s >= 3.1
    G["es"].hide_render = walk or kneel; G["ek"].hide_render = walk or not kneel
    if not walk:
        # Grisha turns to face Eren; Eren stands, then kneels as the needle goes in
        e_at = C - fwd * 1.1 + Vector((-fwd.y, fwd.x)) * 0.9
        dv = e_at - C; yaw_ge = math.atan2(-dv.x, dv.y)
        G["gs"].location = (C.x, C.y, zc); G["gs"].rotation_euler = (0, 0, yaw_ge)
        for e in (G["es"], G["ek"]):
            e.location = (e_at.x, e_at.y, zc); e.rotation_euler = (0, 0, yaw_ge + math.pi)
    # lantern: in Grisha's left hand while walking, then set down beside them
    hand = Vector((gp.x, gp.y)) + Vector((-fwd.y, fwd.x)) * -0.35 if walk else C + Vector((-fwd.y, fwd.x)) * -1.1
    lz = zc + (0.85 + 0.03 * math.sin(s * 9) if walk else 0.12)
    G["lan"].location = (hand.x, hand.y, lz); G["lamp"].location = (hand.x, hand.y, lz + 0.15)
    G["lamp"].data.energy = 900 * (1 + 0.06 * noise.noise(Vector((s * 7, 0, 0))))
    # injection: syringe glint between them 2.6-3.4, a cold flash at 3.25; the key glint passes to Eren 3.6-4.4
    mid = (C + (C - fwd * 1.1 + Vector((-fwd.y, fwd.x)) * 0.9)) * 0.5
    G["syr"].location = (mid.x, mid.y, zc + 1.0)
    G["syr_e"].inputs["Strength"].default_value = 30.0 * (smooth(2.5, 2.7, s) - smooth(3.3, 3.5, s))
    fk = math.exp(-((s - 3.25) / 0.08) ** 2)
    G["flash"].location = (mid.x, mid.y, zc + 1.4); G["flash"].data.energy = 6000 * fk
    e_at = C - fwd * 1.1 + Vector((-fwd.y, fwd.x)) * 0.9
    kp = C.lerp(e_at, smooth(3.6, 4.3, s))
    G["key"].location = (kp.x, kp.y, zc + 1.2 - 0.45 * smooth(3.6, 4.3, s))
    G["key_e"].inputs["Strength"].default_value = 40.0 * smooth(3.55, 3.7, s)
    # camera: down from above the canopy to a high oblique on the tiny figures, slow push; glitch cut at GLITCH_S
    c3 = Vector((C.x, C.y, zc))
    side = Vector((-fwd.y, fwd.x, 0)); back = Vector((-fwd.x, -fwd.y, 0))
    ks = guide([
        (0.0, c3 + back * 34 + side * 20 + Vector((0, 0, 70)), c3 + Vector((0, 0, 1)), 28),   # down through the canopy gap
        (2.4, c3 + back * 18 + side * 12 + Vector((0, 0, 22)), c3 + Vector((0, 0, 1)), 32),
        (SEG5, c3 + back * 13 + side * 9 + Vector((0, 0, 14)), c3 + Vector((0, 0, 1.2)), 36),
    ])
    look(cam, *spline_cam(ks, s))

# ================================================================ main
if B.seg == "3":
    S3 = seg3_build()
    TAGS.update({"Armored Titan": "ArmoredTitan"})
    run(frame_list(SEG3), lambda s: seg3_pose(S3, s), "fall3")
else:
    # night: the moon from states845 night_world; keep it
    S45 = seg45_build()
    if os.environ.get("FALL2_ONLY", "") != "5":
        run(frame_list(SEG4), lambda s: seg4_pose(S45, s), "fall4", "seg4")
    if os.environ.get("FALL2_ONLY", "") != "4":
        run(frame_list(SEG5), lambda s: seg5_pose(S45, s), "fall5", "seg5")
        json.dump({"segment": 5, "glitch_start_s": GLITCH_S, "glitch_frame": int(round(GLITCH_S * B.fps)), "fps": B.fps,
                   "note": "agent E: start the 2D glitch cut here; the 3D frames continue to the segment end"},
                  open(os.path.join(OUT, "grisha_glitch_marker.json"), "w"), indent=1)
        print(f"[fall2] glitch marker s={GLITCH_S}")
