"""Thumbnail-candidate stills for the AoT S1 3D timelapse (anime-into-3D look).

Run:  blender -b -P shot_thumbs.py -- --shot T2|T3|T4 --out x.png [--res 1280x720] [--samples 32]
          [--cam "x,y,z,tx,ty,tz,lens"] [--clay] [--lite] [--save x.blend] [--no-titans] [--variant canal (T3 alt)]

  T2  high oblique aerial of Shiganshina in 845 (matches ref/shiganshina_anime_ref.png).
  T3  dusk: the Armored Titan bursts through the inner gate; dust, debris, pure titans spilling into
      the Wall Maria farmland, crowded ferry boats on the canal.
  T4  morning drone view: pure titans roaming the green fields outside the 50 m wall, district behind.

Builds on the repo modules without changing them: district.py (U layout, canal, streets), walls.py
(slab walls, arched gates, wall-top props), scene.py (house/church/tree meshes, scatter, materials,
terrain material), pure_titans.py and shifters.py (titans).

Layout note: district.py puts the canal on the west wall; the design bible (1.5, conflict table) and the
anime aerial put it on the EAST wall. This file mirrors district.py in x (x -> -x), so the canal runs
inside the east wall. Wall Maria is the x axis, the district sticks out to -y, inner gate (0, 0),
outer gate (0, -TIP).
Materials: Principled BSDF + procedural nodes only (aerial haze is folded into Principled emission).
"""
import bpy, bmesh, math, random, sys, os, argparse, time
from mathutils import Vector, Matrix, Euler, noise

HERE = os.path.dirname(os.path.abspath(__file__))
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ap = argparse.ArgumentParser()
ap.add_argument("--shot", default="T2", choices=("T2", "T3", "T4"))
ap.add_argument("--out", default="")
ap.add_argument("--res", default="1280x720")
ap.add_argument("--samples", type=int, default=32)
ap.add_argument("--cam", default="", help="override: x,y,z,tx,ty,tz,lens")
ap.add_argument("--clay", action="store_true", help="fast layout pass: no trees, no titans")
ap.add_argument("--no-titans", action="store_true")
ap.add_argument("--variant", default="", help="T3: hero (default) | canal")
ap.add_argument("--lite", action="store_true", help="skip town and forest (titan/prop iteration)")
ap.add_argument("--save", default="")
A = ap.parse_args(argv)

sys.path.insert(0, HERE)
_argv = sys.argv
sys.argv = [sys.argv[0]]            # scene.py parses sys.argv at import time; hide our flags from it
import scene as SC
sys.argv = _argv
import district as D
import walls as W

T0 = time.time()
def log(*a):
    print(f"[thumbs {time.time() - T0:6.1f}s]", *a, flush=True)

# ------------------------------------------------------------------ mirrored district layout
WD, LS, TIP = D.WD, D.LS, D.TIP
CX = -D.CANAL_X                     # canal centre line (east side)
CW = D.CANAL_W
PLAZA = (-D.PLAZA[0], D.PLAZA[1])
def MX(p):
    return (-p[0], p[1])
OUTLINE = [MX(p) for p in D.outline()]                   # east end -> tip -> west end
CANAL = [MX(p) for p in D.canal_path()]
STREETS = [([MX(p) for p in pts], hw) for pts, hw in D.street_network()]
in_district = D.in_district                               # symmetric in x
CANAL_EXIT = (CX, D.canal_exit_y())
rnd = random.Random(845)

# ------------------------------------------------------------------ per-shot look
SHOTS = {
    # sun: (azimuth deg, measured from +x toward +y, of the direction TO the sun; elevation deg; energy; colour)
    "T2": dict(sun=(32, 16, 5.0, (1.0, 0.95, 0.86)), sky=((0.66, 0.78, 0.90), (0.30, 0.52, 0.86)),
               amb=0.5, haze=((0.70, 0.79, 0.88), 3000.0, 0.4), expo=0.15, haze_e=0.45,
               cam=((-520, 400, 780), (-30, -380, 0), 31)),
    "T3": dict(sun=(150, 7, 5.0, (1.0, 0.55, 0.26)), sky=((0.98, 0.62, 0.38), (0.22, 0.26, 0.50)),
               amb=0.45, haze=((0.86, 0.60, 0.42), 1800.0, 0.6), expo=-0.1, haze_e=0.5,
               cam=((-30, 62, 4), (70, 0, 23), 22), cloud=(1.0, 0.72, 0.52), cloud_lo=0.58),
    "T4": dict(sun=(-12, 9, 4.6, (1.0, 0.84, 0.62)), sky=((0.90, 0.88, 0.84), (0.42, 0.60, 0.86)),
               amb=0.55, haze=((0.86, 0.87, 0.88), 900.0, 0.62), expo=-0.05, haze_e=0.55,
               cam=((55, -1365, 1.7), (0, -1080, 44), 24), cloud=(0.98, 0.97, 0.95)),
}
S = SHOTS[A.shot]
if A.shot == "T3" and A.variant == "canal":
    S["cam"] = ((330, 640, 38), (40, 0, 20), 30)
elif A.shot == "T3" and A.variant != "hero":
    # round 2 default: low (3.5 m) from beyond the canal, looking west along Wall Maria to the breach
    S["cam"] = ((560, 175, 16), (30, 40, 15), 60)
CAM_LOC = Vector(S["cam"][0])
if A.cam:
    v = [float(t) for t in A.cam.split(",")]
    S["cam"] = ((v[0], v[1], v[2]), (v[3], v[4], v[5]), v[6]); CAM_LOC = Vector(S["cam"][0])

# ------------------------------------------------------------------ helpers
def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def link(ob, coll=None):
    (coll or bpy.context.scene.collection).objects.link(ob)
    return ob

def bm_ob(name, bm, mats=(), coll=None, smooth=False):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for m in mats:
        me.materials.append(m)
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
    return link(bpy.data.objects.new(name, me), coll)

def box(bm, c, size, rot=0.0, mi=0, tilt=None):
    r = bmesh.ops.create_cube(bm, size=1)
    M = Matrix.Translation(c) @ Matrix.Rotation(rot, 4, "Z")
    if tilt is not None:
        M = M @ tilt.to_matrix().to_4x4()
    M = M @ Matrix.Diagonal((*size, 1))
    bmesh.ops.transform(bm, matrix=M, verts=r["verts"])
    for f in {f for v in r["verts"] for f in v.link_faces}:
        f.material_index = mi
    return r

def smooth01(a, b, x):
    t = max(0.0, min(1.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)

def lin(c):
    """sRGB hex -> linear tuple."""
    c = c.lstrip("#")
    out = []
    for i in (0, 2, 4):
        v = int(c[i:i + 2], 16) / 255
        out.append(v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4)
    return tuple(out)

# ------------------------------------------------------------------ aerial haze (Principled only)
def add_haze(m, strength_mul=1.0):
    """Fold aerial perspective into the Principled BSDF: base colour fades to black and emission rises to the
    haze colour with view distance (works the same in Eevee)."""
    col, dist, strength = S["haze"]
    if not m.use_nodes:
        return m
    N, L = m.node_tree.nodes, m.node_tree.links
    b = next((n for n in N if n.type == "BSDF_PRINCIPLED"), None)
    if b is None or b.get("hazed"):
        return m
    b["hazed"] = 1
    cam = N.new("ShaderNodeCameraData")
    d = N.new("ShaderNodeMath"); d.operation = "DIVIDE"; d.inputs[1].default_value = -dist
    L.new(cam.outputs["View Distance"], d.inputs[0])
    e = N.new("ShaderNodeMath"); e.operation = "EXPONENT"; L.new(d.outputs[0], e.inputs[0])
    f = N.new("ShaderNodeMath"); f.operation = "SUBTRACT"; f.inputs[0].default_value = 1.0; L.new(e.outputs[0], f.inputs[1])
    k = N.new("ShaderNodeMath"); k.operation = "MULTIPLY"; k.inputs[1].default_value = strength * strength_mul
    k.use_clamp = True; L.new(f.outputs[0], k.inputs[0])
    bc = b.inputs["Base Color"]
    mix = N.new("ShaderNodeMix"); mix.data_type = "RGBA"
    L.new(k.outputs[0], mix.inputs["Factor"])
    if bc.links:
        L.new(bc.links[0].from_socket, mix.inputs["A"])
    else:
        mix.inputs["A"].default_value = bc.default_value[:]
    mix.inputs["B"].default_value = (0, 0, 0, 1)
    L.new(mix.outputs["Result"], bc)
    b.inputs["Emission Color"].default_value = (*col, 1)
    em = N.new("ShaderNodeMath"); em.operation = "MULTIPLY"; em.inputs[1].default_value = S.get("haze_e", 0.4)
    L.new(k.outputs[0], em.inputs[0])
    L.new(em.outputs[0], b.inputs["Emission Strength"])
    return m

def pmat(name, col, rough=0.8, spec=0.3, emit=None, estr=0.0, alpha=None):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*col, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Specular IOR Level"].default_value = spec
    if emit:
        b.inputs["Emission Color"].default_value = (*emit, 1); b.inputs["Emission Strength"].default_value = estr
    if alpha is not None:
        b.inputs["Alpha"].default_value = alpha
    return m

def noise_mat(name, c1, c2, scale=0.05, rough=0.85, stretch=(1, 1, 1), detail=6, lo=0.35, hi=0.65, bump=0.0,
              grime=None):
    """Two-colour noise material on object coords; optional darkening toward z=0 (grime=(col, height))."""
    m = bpy.data.materials.new(name); m.use_nodes = True
    N, L = m.node_tree.nodes, m.node_tree.links
    b = N["Principled BSDF"]; b.inputs["Roughness"].default_value = rough
    b.inputs["Specular IOR Level"].default_value = 0.25
    tc = N.new("ShaderNodeTexCoord")
    st = N.new("ShaderNodeVectorMath"); st.operation = "MULTIPLY"; st.inputs[1].default_value = stretch
    L.new(tc.outputs["Object"], st.inputs[0])
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = scale; nz.inputs["Detail"].default_value = detail
    L.new(st.outputs[0], nz.inputs["Vector"])
    r = N.new("ShaderNodeValToRGB"); e = r.color_ramp.elements
    e[0].position, e[0].color = lo, (*c1, 1); e[1].position, e[1].color = hi, (*c2, 1)
    L.new(nz.outputs["Fac"], r.inputs["Fac"])
    out = r.outputs["Color"]
    if grime:
        gc, gh = grime
        xyz = N.new("ShaderNodeSeparateXYZ"); L.new(tc.outputs["Object"], xyz.inputs[0])
        mr = N.new("ShaderNodeMapRange"); mr.inputs["From Min"].default_value = 0; mr.inputs["From Max"].default_value = gh
        mr.inputs["To Min"].default_value = 0.75; mr.inputs["To Max"].default_value = 0.0
        L.new(xyz.outputs["Z"], mr.inputs["Value"])
        mx = N.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.inputs["B"].default_value = (*gc, 1)
        L.new(mr.outputs["Result"], mx.inputs["Factor"]); L.new(out, mx.inputs["A"])
        out = mx.outputs["Result"]
    L.new(out, b.inputs["Base Color"])
    if bump:
        bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = bump
        L.new(nz.outputs["Fac"], bp.inputs["Height"]); L.new(bp.outputs["Normal"], b.inputs["Normal"])
    return m

def wall_mat():
    """Pale weathered wall stone (bible 2.3): albedo ~#A39A86, vertical streaks, darker base."""
    m = bpy.data.materials.new("WallStone"); m.use_nodes = True
    N, L = m.node_tree.nodes, m.node_tree.links
    b = N["Principled BSDF"]; b.inputs["Roughness"].default_value = 0.9; b.inputs["Specular IOR Level"].default_value = 0.2
    tc = N.new("ShaderNodeTexCoord")
    st = N.new("ShaderNodeVectorMath"); st.operation = "MULTIPLY"; st.inputs[1].default_value = (1.0, 1.0, 0.08)
    L.new(tc.outputs["Object"], st.inputs[0])
    n1 = N.new("ShaderNodeTexNoise"); n1.inputs["Scale"].default_value = 0.35; n1.inputs["Detail"].default_value = 8
    L.new(st.outputs[0], n1.inputs["Vector"])
    r = N.new("ShaderNodeValToRGB"); e = r.color_ramp.elements
    e[0].position, e[0].color = 0.3, (*lin("A39C8A"), 1); e[1].position, e[1].color = 0.62, (*lin("D2CBB8"), 1)
    L.new(n1.outputs["Fac"], r.inputs["Fac"])
    n2 = N.new("ShaderNodeTexNoise"); n2.inputs["Scale"].default_value = 0.04; n2.inputs["Detail"].default_value = 3
    L.new(tc.outputs["Object"], n2.inputs["Vector"])
    ov = N.new("ShaderNodeMix"); ov.data_type = "RGBA"; ov.blend_type = "MULTIPLY"; ov.inputs["Factor"].default_value = 0.25
    L.new(r.outputs["Color"], ov.inputs["A"]); L.new(n2.outputs["Color"], ov.inputs["B"])
    xyz = N.new("ShaderNodeSeparateXYZ"); L.new(tc.outputs["Object"], xyz.inputs[0])
    mr = N.new("ShaderNodeMapRange"); mr.inputs["From Min"].default_value = -2; mr.inputs["From Max"].default_value = 14
    mr.inputs["To Min"].default_value = 0.55; mr.inputs["To Max"].default_value = 0.0
    L.new(xyz.outputs["Z"], mr.inputs["Value"])
    gm = N.new("ShaderNodeMix"); gm.data_type = "RGBA"; gm.inputs["B"].default_value = (*lin("4E4A3C"), 1)
    L.new(mr.outputs["Result"], gm.inputs["Factor"]); L.new(ov.outputs["Result"], gm.inputs["A"])
    L.new(gm.outputs["Result"], b.inputs["Base Color"])
    bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.15
    L.new(n1.outputs["Fac"], bp.inputs["Height"]); L.new(bp.outputs["Normal"], b.inputs["Normal"])
    return m

def wall_mat_courses(name="WallStoneCourses"):
    """Round-2 wall surface: huge dressed stone in horizontal courses (2.4 m) with faint staggered vertical joints,
    per-block tone variation, isotropic mottling (no vertical streaks), a dark weathered base and a lighter band
    under the parapet. Object coords = world for walls.py meshes; u runs along x + y so it works on every wall."""
    m = bpy.data.materials.new(name); m.use_nodes = True
    N, L = m.node_tree.nodes, m.node_tree.links
    b = N["Principled BSDF"]; b.inputs["Roughness"].default_value = 0.92; b.inputs["Specular IOR Level"].default_value = 0.15
    def math_(op, a, bb=None, clamp=False):
        n = N.new("ShaderNodeMath"); n.operation = op; n.use_clamp = clamp
        for i, v in enumerate((a, bb)):
            if v is None:
                continue
            if isinstance(v, (int, float)):
                n.inputs[i].default_value = v
            else:
                L.new(v, n.inputs[i])
        return n.outputs[0]
    def mrange(v, a, bb, c, d):
        n = N.new("ShaderNodeMapRange"); n.clamp = True
        n.inputs["From Min"].default_value, n.inputs["From Max"].default_value = a, bb
        n.inputs["To Min"].default_value, n.inputs["To Max"].default_value = c, d
        L.new(v, n.inputs["Value"]); return n.outputs["Result"]
    def mix(fac, a, bb, blend="MIX"):
        n = N.new("ShaderNodeMix"); n.data_type = "RGBA"; n.blend_type = blend
        for sock, v in (("Factor", fac), ("A", a), ("B", bb)):
            if isinstance(v, tuple):
                n.inputs[sock].default_value = v if len(v) == 4 else (*v, 1)
            elif isinstance(v, (int, float)):
                n.inputs[sock].default_value = v
            else:
                L.new(v, n.inputs[sock])
        return n.outputs["Result"]
    tc = N.new("ShaderNodeTexCoord")
    xyz = N.new("ShaderNodeSeparateXYZ"); L.new(tc.outputs["Object"], xyz.inputs[0])
    X, Y, Z = xyz.outputs["X"], xyz.outputs["Y"], xyz.outputs["Z"]
    H, Wb = 2.4, 6.5
    zc = math_("DIVIDE", Z, H)
    ci = math_("FLOOR", zc); fz = math_("FRACT", zc)
    u = math_("DIVIDE", math_("ADD", X, Y), Wb)
    stag = math_("MULTIPLY", math_("FRACT", math_("MULTIPLY", ci, 0.5)), 1.0)           # 0 or 0.5
    bu = math_("ADD", u, stag)
    bi = math_("FLOOR", bu); fu = math_("FRACT", bu)
    # seams
    seam_h = mrange(fz, 0.0, 0.03, 1.0, 0.0)
    seam_v = math_("MAXIMUM", mrange(fu, 0.0, 0.012, 1.0, 0.0), mrange(fu, 0.988, 1.0, 0.0, 1.0))
    seam = math_("MAXIMUM", seam_h, math_("MULTIPLY", seam_v, 0.45))
    # per-block tone
    cb = N.new("ShaderNodeCombineXYZ"); L.new(bi, cb.inputs["X"]); L.new(ci, cb.inputs["Y"])
    wn = N.new("ShaderNodeTexWhiteNoise"); wn.noise_dimensions = "3D"; L.new(cb.outputs[0], wn.inputs["Vector"])
    tone = mrange(wn.outputs["Value"], 0.0, 1.0, 0.9, 1.08)
    # mottled stone (isotropic, two scales)
    n1 = N.new("ShaderNodeTexNoise"); n1.inputs["Scale"].default_value = 0.09; n1.inputs["Detail"].default_value = 6
    L.new(tc.outputs["Object"], n1.inputs["Vector"])
    r = N.new("ShaderNodeValToRGB"); e = r.color_ramp.elements
    e[0].position, e[0].color = 0.35, (*lin("9E9684"), 1); e[1].position, e[1].color = 0.65, (*lin("C4BCA8"), 1)
    L.new(n1.outputs["Fac"], r.inputs["Fac"])
    tone_rgb = N.new("ShaderNodeCombineColor")
    for k in ("Red", "Green", "Blue"):
        L.new(tone, tone_rgb.inputs[k])
    col = mix(1.0, r.outputs["Color"], tone_rgb.outputs[0], "MULTIPLY")
    # weathered base: darker, warm grime up to ~12 m with a ragged upper edge; faint stains higher up
    n2 = N.new("ShaderNodeTexNoise"); n2.inputs["Scale"].default_value = 0.06; n2.inputs["Detail"].default_value = 5
    L.new(tc.outputs["Object"], n2.inputs["Vector"])
    zz = math_("ADD", Z, math_("MULTIPLY", math_("SUBTRACT", n2.outputs["Fac"], 0.5), 10.0))
    grime = mrange(zz, 0.0, 13.0, 0.62, 0.0)
    col = mix(grime, col, lin("4F4A3D"))
    stain = mrange(n2.outputs["Fac"], 0.5, 0.85, 0.0, 0.10)
    col = mix(stain, col, lin("7C7462"))
    # lighter band under the parapet
    top = mrange(Z, 45.6, 46.2, 0.0, 1.0)
    col = mix(math_("MULTIPLY", top, 0.55), col, lin("DAD3C2"))
    top_line = math_("MULTIPLY", mrange(Z, 45.5, 45.6, 0.0, 1.0), mrange(Z, 45.6, 45.75, 1.0, 0.0))
    seam = math_("MAXIMUM", seam, top_line)
    col = mix(math_("MULTIPLY", seam, 0.55), col, lin("3A362E"))
    L.new(col, b.inputs["Base Color"])
    bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.35; bp.inputs["Distance"].default_value = 0.08
    L.new(math_("SUBTRACT", math_("MULTIPLY", n1.outputs["Fac"], 0.3), seam), bp.inputs["Height"])
    L.new(bp.outputs["Normal"], b.inputs["Normal"])
    return m

def ground_mat():
    """scene.terrain_mat() (farm patchwork inside Wall Maria) with brighter anime meadow greens."""
    m = SC.terrain_mat()
    for n in m.node_tree.nodes:
        if n.type == "TEX_NOISE" and abs(n.inputs["Scale"].default_value - 0.0012) < 1e-6:
            n.inputs["Scale"].default_value = 0.0032; n.inputs["Roughness"].default_value = 0.62
        if n.type == "VALTORGB" and len(n.color_ramp.elements) == 3:          # meadow ramp
            cols = [lin("4E7A2C"), lin("7FA43E"), lin("B4C274")]
            for el, c, pos in zip(n.color_ramp.elements, cols, (0.40, 0.50, 0.60)):
                el.color = (*c, 1); el.position = pos
        if n.type == "VALTORGB" and len(n.color_ramp.elements) == 6:          # farm field palette
            cols = [lin("B8B079"), lin("7FA046"), lin("A08A55"), lin("6A8E35"), lin("C9B878"), lin("8CA552")]
            for el, c in zip(n.color_ramp.elements, cols):
                el.color = (*c, 1)
    # painted mid-scale variation: darker lush patches and sun-bleached ones
    N, L = m.node_tree.nodes, m.node_tree.links
    b = N["Principled BSDF"]
    src = b.inputs["Base Color"].links[0].from_socket
    tc = N.new("ShaderNodeTexCoord")
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 0.011; nz.inputs["Detail"].default_value = 5
    nz.inputs["Roughness"].default_value = 0.6
    L.new(tc.outputs["Object"], nz.inputs["Vector"])
    rp = N.new("ShaderNodeValToRGB"); e = rp.color_ramp.elements
    e[0].position, e[0].color = 0.36, (0.70, 0.74, 0.62, 1); e[1].position, e[1].color = 0.66, (1.18, 1.14, 1.0, 1)
    L.new(nz.outputs["Fac"], rp.inputs["Fac"])
    mm = N.new("ShaderNodeMix"); mm.data_type = "RGBA"; mm.blend_type = "MULTIPLY"; mm.inputs["Factor"].default_value = 1.0
    L.new(src, mm.inputs["A"]); L.new(rp.outputs["Color"], mm.inputs["B"])
    # fine grass texture (wind-combed strokes) for the low drone views
    st = N.new("ShaderNodeVectorMath"); st.operation = "MULTIPLY"; st.inputs[1].default_value = (1.0, 3.5, 1.0)
    L.new(tc.outputs["Object"], st.inputs[0])
    nf = N.new("ShaderNodeTexNoise"); nf.inputs["Scale"].default_value = 0.45; nf.inputs["Detail"].default_value = 4
    L.new(st.outputs[0], nf.inputs["Vector"])
    rf = N.new("ShaderNodeValToRGB"); e2 = rf.color_ramp.elements
    e2[0].position, e2[0].color = 0.3, (0.78, 0.8, 0.7, 1); e2[1].position, e2[1].color = 0.7, (1.1, 1.08, 1.0, 1)
    L.new(nf.outputs["Fac"], rf.inputs["Fac"])
    m2 = N.new("ShaderNodeMix"); m2.data_type = "RGBA"; m2.blend_type = "MULTIPLY"; m2.inputs["Factor"].default_value = 1.0
    L.new(mm.outputs["Result"], m2.inputs["A"]); L.new(rf.outputs["Color"], m2.inputs["B"])
    L.new(m2.outputs["Result"], b.inputs["Base Color"])
    return m

def puff_mat(name, col, alpha=0.85, emit=None, estr=0.0):
    """Soft anime dust: Principled with alpha fading at grazing angles."""
    m = bpy.data.materials.new(name); m.use_nodes = True
    N, L = m.node_tree.nodes, m.node_tree.links
    b = N["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*col, 1); b.inputs["Roughness"].default_value = 1.0
    b.inputs["Specular IOR Level"].default_value = 0.0
    lw = N.new("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = 0.55
    inv = N.new("ShaderNodeMath"); inv.operation = "SUBTRACT"; inv.inputs[0].default_value = 1.0
    L.new(lw.outputs["Facing"], inv.inputs[1])
    pw = N.new("ShaderNodeMath"); pw.operation = "POWER"; pw.inputs[1].default_value = 2.2
    L.new(inv.outputs[0], pw.inputs[0])
    mul = N.new("ShaderNodeMath"); mul.operation = "MULTIPLY"; mul.inputs[1].default_value = alpha
    L.new(pw.outputs[0], mul.inputs[0]); L.new(mul.outputs[0], b.inputs["Alpha"])
    if emit:
        b.inputs["Emission Color"].default_value = (*emit, 1); b.inputs["Emission Strength"].default_value = estr
    return m

# ------------------------------------------------------------------ terrain height
_CANAL_IDX = {}
for _x, _y in CANAL:
    _CANAL_IDX.setdefault((int(_x // 100), int(_y // 100)), []).append((_x, _y))

def canal_dist(x, y):
    gx, gy = int(x // 100), int(y // 100)
    best = 1e9
    for i in (-2, -1, 0, 1, 2):
        for j in (-2, -1, 0, 1, 2):
            for px, py in _CANAL_IDX.get((gx + i, gy + j), ()):
                d = (px - x) ** 2 + (py - y) ** 2
                if d < best:
                    best = d
    return math.sqrt(best)

def district_dist(x, y):
    """0 inside the district, else distance to it."""
    if y > 0:
        dy = y
        dx = max(0.0, abs(x) - WD)
        return math.hypot(dx, dy)
    if y > -LS:
        return max(0.0, abs(x) - WD)
    return max(0.0, math.hypot(x, y + LS) - WD)

def height(x, y):
    dd = district_dist(x, y)
    f = smooth01(160, 900, min(dd, abs(y) * 1.4 + 0.0 if abs(x) > WD else dd))
    f *= smooth01(30, 260, canal_dist(x, y))
    h = (noise.noise(Vector((x / 1300, y / 1300, 0.3))) * 26 + noise.noise(Vector((x / 330, y / 330, 1.7))) * 5) * f
    r = math.hypot(x, y + 500)
    far = smooth01(5500, 8800, r) * (1.0 if y < 0 else 0.25)          # mountains beyond the Titan side only
    h += far * (noise.noise(Vector((x / 1800, y / 1800, 9.1))) * 0.5 + 0.5) ** 1.5 * 900
    hd = math.hypot(x - SC.HILL.x, y - SC.HILL.y)
    h += 26 * math.exp(-(hd / 150) ** 2)
    return h

def build_terrain(mat_ground, center=(0, -400), size=9000.0, n=240):
    bm = bmesh.new()
    cx, cy = center
    def coord(i, c):
        t = i / n * 2 - 1
        return c + math.copysign(abs(t) ** 1.7, t) * size
    vs = [[bm.verts.new((coord(i, cx), coord(j, cy), 0)) for j in range(n + 1)] for i in range(n + 1)]
    for row in vs:
        for v in row:
            v.co.z = height(v.co.x, v.co.y)
    for i in range(n):
        for j in range(n):
            bm.faces.new((vs[i][j], vs[i + 1][j], vs[i + 1][j + 1], vs[i][j + 1]))
    return bm_ob("Terrain", bm, [mat_ground], smooth=True)

def ribbon(name, pts, width, m, z=0.15, follow=True, coll=None):
    bm = bmesh.new()
    L, R = [], []
    n = len(pts)
    for k in range(n):
        a = Vector(pts[max(k - 1, 0)]); b = Vector(pts[min(k + 1, n - 1)])
        t = b - a
        if t.length == 0:
            continue
        t.normalize(); nr = Vector((-t.y, t.x)) * width / 2
        p = Vector(pts[k])
        zz = (height(p.x, p.y) if follow else 0) + z
        L.append(bm.verts.new((*(p + nr), zz))); R.append(bm.verts.new((*(p - nr), zz)))
    for k in range(len(L) - 1):
        f = bm.faces.new((L[k], R[k], R[k + 1], L[k + 1]))
        f.normal_update()
        if f.normal.z < 0:
            f.normal_flip()
    return bm_ob(name, bm, [m], coll)

def wall_strip(name, pts, off, width, h, m, z0=-1.0):
    """Low embankment wall along a polyline at lateral offset `off`."""
    bm = bmesh.new()
    prev = None
    n = len(pts)
    for k in range(n):
        a = Vector(pts[max(k - 1, 0)]); b = Vector(pts[min(k + 1, n - 1)])
        t = (b - a).normalized(); nr = Vector((-t.y, t.x))
        p = Vector(pts[k]) + nr * off
        zz = height(p.x, p.y)
        ring = [bm.verts.new((*(p - nr * width / 2), zz + z0)), bm.verts.new((*(p + nr * width / 2), zz + z0)),
                bm.verts.new((*(p + nr * width / 2), zz + h)), bm.verts.new((*(p - nr * width / 2), zz + h))]
        if prev:
            for e in range(4):
                bm.faces.new((prev[e], prev[(e + 1) % 4], ring[(e + 1) % 4], ring[e]))
        prev = ring
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm_ob(name, bm, [m])

# ------------------------------------------------------------------ walls
GATE_W, GATE_H = 10.0, 14.0
def gate_skip(width):
    r = width / 2 + W.SLAB_L / 2 + 0.5
    return r, 2 * r + 18

def build_walls(M, broken=False):
    stone = M["stone"]
    mats = {"stone": stone, "gate": M["gatewood"], "iron": M["iron"], "keg": M["keg"]}
    # Wall Maria along x (outside of Maria = south = right of +x walking direction)
    maria = [(x, 0.0) for x in range(-7000, 7001, 16)]
    gw = 18.0 if broken else GATE_W
    gr, gbl = gate_skip(gw)
    wr, wbl = gate_skip(18.0)
    W.build_wall("WallMaria", maria, stone, skip=[(0, 0, gr), (CX, 0, wr)], outward=1)
    if broken:
        broken_gate(stone)
    else:
        clean_gate("InnerGate", (0, 0), 0.0, GATE_W, GATE_H, gbl / 2, stone, M["gatewood"])
    clean_gate("WaterGateN", (CX, 0), 0.0, 18.0, 10.0, wbl / 2, stone)
    # district wall (mirrored outline walks east end -> tip -> west end; outside is on the LEFT)
    ex, ey = CANAL_EXIT
    ang_exit = math.atan2(ey + LS, ex) + math.pi / 2
    W.build_wall("WallShiganshina", OUTLINE, stone, skip=[(0, -TIP, gr if not broken else gate_skip(GATE_W)[0]),
                                                           (ex, ey, wr)], outward=-1)
    ogr, ogbl = gate_skip(GATE_W)
    clean_gate("OuterGate", (0, -TIP), 0.0, GATE_W, GATE_H, ogbl / 2, stone, M["gatewood"])
    clean_gate("WaterGateS", (ex, ey), ang_exit, 18.0, 10.0, wbl / 2, stone)
    add_piers("MariaPiers", maria, stone, 1, skip=[(0, 0, gr), (CX, 0, wr)])
    add_piers("ShigPiers", OUTLINE, stone, -1, skip=[(0, -TIP, ogr), (ex, ey, wr)])
    wall_cap("MariaCap", maria, M["walkway"], 1)
    wall_cap("ShigCap", OUTLINE, M["walkway"], -1)
    near = [p for p in maria if abs(p[0]) < 1600]
    W.wall_top_props("MariaTop", near, mats, outward=1, every=2, skip=[(0, 0, gr), (CX, 0, wr)])
    W.wall_top_props("ShigTop", OUTLINE, mats, outward=-1, every=1, skip=[(0, -TIP, ogr), (ex, ey, wr)])

def clean_gate(name, center, ang, width, height, half, stone, door_mat=None, col=0.7):
    """Gate block with a round-topped arch tunnel through the full wall depth, built from columns (walls.arch_gate's
    EXACT boolean drops the block's upper half in this Blender build)."""
    bm = bmesh.new()
    n = int(2 * half / col)
    w2 = width / 2
    for i in range(n):
        x = -half + (i + 0.5) * col
        if abs(x) < w2:
            top = (height - w2) + math.sqrt(max(0.0, w2 * w2 - x * x))
            h = W.WALL_H - top
            box(bm, Vector((x, 0, top + h / 2)), (col + 0.01, 18.0, h))
        else:
            box(bm, Vector((x, 0, (W.WALL_H + 6) / 2 - 6)), (col + 0.01, 18.0, W.WALL_H + 6))
    # arch surround on both faces
    for sgn in (-1, 1):
        for k in range(25):
            a = math.pi * k / 24
            c = Vector((math.cos(a) * (w2 + 1.1), sgn * 9.3, (height - w2) + math.sin(a) * (w2 + 1.1)))
            box(bm, c, (1.6, 0.8, 1.6), 0, 0, Euler((0, -a, 0)))
        for sx in (-1, 1):
            box(bm, Vector((sx * (w2 + 1.1), sgn * 9.3, (height - w2) / 2)), (1.6, 0.8, height - w2), 0)
    ob = bm_ob(name, bm, [stone])
    ob.location = (center[0], center[1], 0); ob.rotation_euler.z = ang
    if door_mat is not None:
        db = bmesh.new()
        box(db, Vector((0, 2.0, (height - w2) / 2)), (width + 0.2, 1.6, height - w2 + 0.2))
        cyl = bmesh.ops.create_cone(db, cap_ends=True, segments=24, radius1=w2 + 0.1, radius2=w2 + 0.1, depth=1.6)
        bmesh.ops.rotate(db, cent=(0, 0, 0), matrix=Matrix.Rotation(math.pi / 2, 3, "X"), verts=cyl["verts"])
        bmesh.ops.translate(db, vec=(0, 2.0, height - w2), verts=cyl["verts"])
        for k in range(1, 6):
            box(db, Vector((0, 1.05, k * height / 6.5)), (width + 0.2, 0.3, 0.6))
        d = bm_ob(name + "_door", db, [door_mat])
        d.location = ob.location; d.rotation_euler.z = ang
    return ob

def broken_gate(stone, half=26.0, col=1.3):
    """The inner gate after the Armored Titan's charge (bible 1.4): a tall rough pointed-arch hole through the
    wall block, built from narrow full-depth columns with jittered breaks (no booleans)."""
    r = random.Random(845)
    bm = bmesh.new()
    n = int(2 * half / col)
    for i in range(n):
        x = -half + (i + 0.5) * col
        hw = 9.5 + r.uniform(-1.2, 1.2)
        if abs(x) < hw:
            top = 24.0 * (1 - (abs(x) / 10.5) ** 2) ** 0.55 + r.uniform(-1.5, 2.0)
            top = max(top, 4.0)
            h = W.WALL_H - top
            box(bm, Vector((x, r.uniform(-0.6, 0.6), top + h / 2)), (col + 0.02, 18.0, h))
        else:
            box(bm, Vector((x, 0, (W.WALL_H + 6) / 2 - 6)), (col + 0.02, 18.0, W.WALL_H + 6))
    # jagged chunks clinging to the hole rim
    for k in range(40):
        a = r.uniform(0.05, math.pi - 0.05)
        rr = r.uniform(9.0, 11.0)
        c = Vector((math.cos(a) * rr, r.uniform(-9, 9.5), 1.0 + math.sin(a) * 23.5 * (rr / 10.5) ** 0.3))
        box(bm, c, (r.uniform(0.8, 2.6), r.uniform(0.8, 2.6), r.uniform(0.8, 2.6)), r.uniform(0, 3), 0,
            Euler((r.uniform(0, 3), r.uniform(0, 3), 0)))
    return bm_ob("InnerGateBroken", bm, [stone])

def add_piers(name, pts, m, outward=1, skip=()):
    """Bible 2.2: a full-height pier at every panel joint, projecting from the outer face, plus slim
    pilasters on the inner face (walls.py only has a thin strip mid-panel)."""
    bm = bmesh.new()
    def skipped(p):
        return any((p.x - x) ** 2 + (p.y - y) ** 2 < (r + 3) ** 2 for x, y, r in skip)
    for i, (p, ang) in enumerate(W._walk(pts, W.SLAB_L)):
        t = Vector((math.cos(ang), math.sin(ang)))
        n = Vector((math.sin(ang), -math.cos(ang))) * outward
        q = p + t * (W.SLAB_L / 2)
        if skipped(q):
            continue
        c = q + n * 10.6
        if A.shot == "T2" or i % 2 == 1:
            box(bm, Vector((c.x, c.y, (W.WALL_H + 1.8) / 2 - 2)), (2.8, 3.2, W.WALL_H + 1.8 + 4), ang)
        else:                                                          # flush filler: only a faint seam
            f = q + n * 8.7
            box(bm, Vector((f.x, f.y, W.WALL_H / 2 - 2)), (1.6, 1.4, W.WALL_H + 4), ang)
        c = q - n * 5.5
        if i % 2 == 0:
            box(bm, Vector((c.x, c.y, (W.WALL_H + 0.8) / 2 - 2)), (2.6, 1.2, W.WALL_H + 0.8 + 4), ang)
        c = p - n * 5.3                                               # string course ~1/3 up (bible 2.2)
        if not skipped(p):
            box(bm, Vector((c.x, c.y, 16.5)), (W.SLAB_L + 0.2, 0.7, 1.4), ang)
    return bm_ob(name, bm, [m])

def wall_cap(name, pts, m, outward=1):
    """Sandy walkway cap over the wall top (bible 2.4). Also hides walls.py's coplanar core/slab tops, which
    otherwise shadow-acne into black patches in Cycles."""
    bm = bmesh.new()
    Lv, Rv = [], []
    n = len(pts)
    for k in range(n):
        a = Vector(pts[max(k - 1, 0)]); b = Vector(pts[min(k + 1, n - 1)])
        t = (b - a)
        if t.length == 0:
            continue
        t.normalize()
        nr = Vector((t.y, -t.x)) * outward                          # toward the outside face
        p = Vector(pts[k])
        Lv.append(bm.verts.new((*(p - nr * 5.3), W.WALL_H + 0.08)))
        Rv.append(bm.verts.new((*(p + nr * 9.7), W.WALL_H + 0.08)))
    for k in range(len(Lv) - 1):
        f = bm.faces.new((Lv[k], Rv[k], Rv[k + 1], Lv[k + 1]))
        f.normal_update()
        if f.normal.z < 0:
            f.normal_flip()
    return bm_ob(name, bm, [m])

def gatehouse(M):
    """Pale castle-like gatehouse against the district side of the inner gate (bible 1.4)."""
    bm = bmesh.new()
    box(bm, Vector((0, -20, 15)), (70, 22, 30))                      # main block
    box(bm, Vector((0, -18, 27)), (20, 20, 54))                      # central tower
    for sx in (-33, 33):
        box(bm, Vector((sx, -24, 21)), (11, 11, 42))                 # corner towers
    for x in range(-34, 35, 4):                                      # crenels
        box(bm, Vector((x, -31.2, 30.8)), (2.0, 1.2, 1.6))
    roof = bmesh.new()
    def pyramid(cx, cy, z0, hw, h):
        v = [roof.verts.new(c) for c in ((cx - hw, cy - hw, z0), (cx + hw, cy - hw, z0), (cx + hw, cy + hw, z0),
                                         (cx - hw, cy + hw, z0), (cx, cy, z0 + h))]
        for fv in ((0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4)):
            roof.faces.new([v[i] for i in fv])
    pyramid(0, -18, 54, 11.0, 14)
    for sx in (-33, 33):
        pyramid(sx, -24, 42, 6.5, 13)
    # cut the gate tunnel visually: dark slot
    ob = bm_ob("Gatehouse", bm, [M["gatehouse"]])
    bm_ob("GatehouseRoof", roof, [M["roof_slate"]])
    slot = bmesh.new(); box(slot, Vector((0, -31.4, 7)), (GATE_W, 0.6, 14))
    bm_ob("GatehouseSlot", slot, [M["shadow"]])
    return ob

# ------------------------------------------------------------------ town
def road_index(streets):
    grid = {}
    for pts, hw in streets:
        for k in range(len(pts) - 1):
            ax, ay = pts[k]; bx, by = pts[k + 1]
            n = max(1, int(math.hypot(bx - ax, by - ay) / 2.5))
            for t in range(n + 1):
                x, y = ax + (bx - ax) * t / n, ay + (by - ay) * t / n
                grid.setdefault((int(x // 20), int(y // 20)), []).append((x, y, hw))
    return grid
ROADS = road_index(STREETS)

def blocked(x, y, pad=0.0):
    if abs(x - CX) < CW / 2 + 5 + pad:                                # canal + quays
        return True
    if math.hypot(x - PLAZA[0], y - PLAZA[1]) < 40 + pad:            # plaza
        return True
    if abs(x) < 40 and -38 < y < 0:                                   # gatehouse
        return True
    if abs(x) < 26 and y < -TIP + 40:                                 # outer gate square
        return True
    gx, gy = int(x // 20), int(y // 20)
    for i in (-1, 0, 1):
        for j in (-1, 0, 1):
            for px, py, hw in ROADS.get((gx + i, gy + j), ()):
                if (px - x) ** 2 + (py - y) ** 2 < (hw + pad) ** 2:
                    return True
    return False

def town_points(widths):
    r = random.Random(21)
    pts = []
    occ = {}
    nv = len(widths)
    def free(x, y, rad):
        gx, gy = int(x // 12), int(y // 12)
        for i in (-1, 0, 1):
            for j in (-1, 0, 1):
                for ox, oy, orad in occ.get((gx + i, gy + j), ()):
                    if (ox - x) ** 2 + (oy - y) ** 2 < (rad + orad) ** 2:
                        return False
        return True
    def put(x, y, ang, v, rad):
        pts.append((x, y, 0.0, ang, r.uniform(0.92, 1.1), v, -1e4, 1e5))
        occ.setdefault((int(x // 12), int(y // 12)), []).append((x, y, rad))
    for spts, hw in STREETS:
        for k in range(len(spts) - 1):
            ax, ay = spts[k]; bx, by = spts[k + 1]
            seg = math.hypot(bx - ax, by - ay)
            if seg == 0:
                continue
            tx, ty = (bx - ax) / seg, (by - ay) / seg
            nx, ny = -ty, tx
            t = 0.0
            while t < seg:
                v = r.randrange(nv); w, dpt = widths[v]
                for side in (1, -1):
                    off = hw + dpt / 2 + 0.6
                    x = ax + tx * t + nx * off * side; y = ay + ty * t + ny * off * side
                    if r.random() < 0.05 or not in_district(x, y, 14) or blocked(x, y, dpt / 2 - 0.5):
                        continue
                    rad = min(w, dpt) * 0.5
                    if free(x, y, rad):
                        put(x, y, math.atan2(ty, tx) + (0 if side > 0 else math.pi), v, rad)
                t += w + r.uniform(0.1, 1.0)
    # back lots: dense fill aligned with the nearest street direction
    for _ in range(60000):
        x, y = r.uniform(-WD, WD), r.uniform(-TIP, 0)
        if not in_district(x, y, 14) or blocked(x, y, 3.5):
            continue
        v = r.randrange(nv); w, dpt = widths[v]
        if free(x, y, max(w, dpt) * 0.5):
            a = math.atan2(y - PLAZA[1], x - PLAZA[0]) + noise.noise(Vector((x / 200, y / 200, 2.5))) * 0.5
            put(x, y, a, v, max(w, dpt) * 0.5)
    return pts, occ

def town_trees(occ):
    """Garden trees between the houses (the green flecks in the anime aerial)."""
    r = random.Random(5)
    pts = []
    for _ in range(30000):
        x, y = r.uniform(-WD, WD), r.uniform(-TIP, 0)
        if not in_district(x, y, 12) or blocked(x, y, 2):
            continue
        gx, gy = int(x // 12), int(y // 12)
        ok = True
        for i in (-1, 0, 1):
            for j in (-1, 0, 1):
                for ox, oy, orad in occ.get((gx + i, gy + j), ()):
                    if (ox - x) ** 2 + (oy - y) ** 2 < (orad + 1.5) ** 2:
                        ok = False
        if ok:
            pts.append((x, y, 0.0, r.uniform(0, 6.28), r.uniform(0.9, 1.5), r.randrange(7), -1e4, 1e5))
    return pts

def house_variants(M, coll):
    r = random.Random(9)
    walls = ["plaster", "plaster_w", "plaster_o", "timber", "stone_h"]
    roofs = ["roof_a", "roof_b", "roof_c", "roof_d", "roof_e", "roof_g", "roof_b", "roof_f", "roof_g", "roof_c", "roof_d", "roof_a", "roof_e", "roof_g", "roof_c", "roof_b", "roof_e", "roof_slate"]
    widths = []
    for i in range(48):
        w = r.uniform(6.5, 10.5); d = r.uniform(9, 14); h = r.choice((7, 9, 10, 12, 12, 14, 16))
        me = SC.house_mesh(f"H{i}", w, d, h, d * r.uniform(0.5, 0.62), M, walls[i % 5], roofs[(i * 7 + i // 5) % len(roofs)])
        coll.objects.link(bpy.data.objects.new(f"H{i}", me))
        widths.append((w, d))
    return widths

def monument(M):
    """White monument in the central plaza (anime aerial)."""
    bm = bmesh.new()
    px, py = PLAZA
    box(bm, Vector((px, py, 1.0)), (30, 30, 2.0))
    box(bm, Vector((px, py, 3.5)), (20, 20, 3.0))
    box(bm, Vector((px, py, 9.0)), (11, 11, 8.0))
    box(bm, Vector((px, py, 20.0)), (6.5, 6.5, 16.0))
    v = [bm.verts.new(c) for c in ((px - 3.6, py - 3.6, 28), (px + 3.6, py - 3.6, 28), (px + 3.6, py + 3.6, 28),
                                   (px - 3.6, py + 3.6, 28), (px, py, 37))]
    for fv in ((0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4)):
        bm.faces.new([v[i] for i in fv])
    bm_ob("Monument", bm, [M["white"]])
    pl = bmesh.new()
    c = bmesh.ops.create_circle(pl, cap_ends=True, segments=48, radius=41)
    bmesh.ops.translate(pl, vec=(px, py, 0.2), verts=c["verts"])
    bm_ob("Plaza", pl, [M["paving"]])

def build_town(M, trees_coll):
    hc = bpy.data.collections.new("HouseVariants"); bpy.context.scene.collection.children.link(hc)
    bpy.context.view_layer.layer_collection.children["HouseVariants"].exclude = True
    widths = house_variants(M, hc)
    pts, occ = town_points(widths)
    log("houses", len(pts))
    SC.scatter("Town", hc, pts, 845)
    tp = town_trees(occ)
    log("town trees", len(tp))
    SC.scatter("TownTrees", trees_coll["broad"], tp, 845)
    # streets
    for k, (spts, hw) in enumerate(STREETS):
        ribbon(f"Street{k}", spts, hw * 2, M["street"], z=0.12 + k * 0.002, follow=False)
    # churches
    for (x, y, a) in ((-120, -300, 0.3), (150, -760, -0.4)):
        if blocked(x, y, 0):
            pass
        ch = link(bpy.data.objects.new("Church", SC.church_mesh(M)))
        ch.location = (x, y, 0); ch.rotation_euler.z = a
    monument(M)
    gatehouse(M)

# ------------------------------------------------------------------ canal
def build_canal(M):
    pts = CANAL
    ribbon("CanalWater", pts, CW, M["water"], z=0.35)
    for s in (-1, 1):
        wall_strip(f"CanalBank{s}", pts, s * (CW / 2 + 1.0), 2.0, 1.6, M["quay"])
        ribbon(f"CanalWalk{s}", [(x + s * (CW / 2 + 6.5), y) for x, y in pts], 9.0, M["paving"], z=0.2)

# ------------------------------------------------------------------ forest and fields
def tree_variants(M):
    tc = {"broad": bpy.data.collections.new("TreesBroad"), "conifer": bpy.data.collections.new("TreesConifer")}
    for k, c in tc.items():
        bpy.context.scene.collection.children.link(c)
        bpy.context.view_layer.layer_collection.children[c.name].exclude = True
    for i in range(7):
        tc["broad"].objects.link(bpy.data.objects.new(f"TB{i}", SC.tree_mesh(f"TB{i}", "broad", M, i)))
    for i in range(5):
        tc["conifer"].objects.link(bpy.data.objects.new(f"TC{i}", SC.tree_mesh(f"TC{i}", "conifer", M, 7 + i)))
    return tc

def forest_points(bounds, density=0.012):
    x0, x1, y0, y1 = bounds
    n = int((x1 - x0) * (y1 - y0) * density)
    r = random.Random(77)
    con, brd = [], []
    for _ in range(n):
        x, y = r.uniform(x0, x1), r.uniform(y0, y1)
        dd = district_dist(x, y)
        if dd < 45 or abs(y) < 45:
            continue
        if canal_dist(x, y) < 40:
            continue
        if abs(x) < 18 and (y > 0 or y < -TIP):                       # roads out of the gates
            continue
        dx, dy = x - CAM_LOC.x, y - CAM_LOC.y
        if math.hypot(dx, dy) < (330 if A.shot == "T4" else 160):    # low-poly trees never right at the lens
            continue
        if A.shot == "T3" and A.variant != "hero":                     # view corridor to the breach
            ux, uy = -CAM_LOC.x, -CAM_LOC.y
            t = (dx * ux + dy * uy) / (ux * ux + uy * uy)
            if 0 < t < 1 and abs(dx * uy - dy * ux) / math.hypot(ux, uy) < 160 + 120 * t:
                continue
        if A.shot == "T4":                                             # keep the titans' meadow open
            if math.hypot(dx, dy) < 700:                              # foreground handled by shot_T4's spruces
                continue
        f = noise.noise(Vector((x / 650, y / 650, 4.2))) + 0.45 * noise.noise(Vector((x / 170, y / 170, 1.1)))
        inside = y > 0
        if inside:
            keep = f > 0.42 or (f > 0.0 and r.random() < 0.012)
        else:
            keep = f > 0.12 or (f > -0.05 and r.random() < 0.05) or r.random() < 0.002
        if not keep:
            continue
        z = height(x, y) - 0.3
        p = (x, y, z, r.uniform(0, 6.28), r.uniform(0.85, 1.55), 0, -1e4, 1e5)
        if inside and r.random() < 0.7 or (not inside and r.random() < 0.35):
            brd.append(p[:5] + (r.randrange(7),) + p[6:])
        else:
            con.append(p[:5] + (r.randrange(5),) + p[6:])
    return con, brd

def build_forest(tc, bounds, density):
    con, brd = forest_points(bounds, density)
    log("forest", len(con), len(brd))
    SC.scatter("ForestConifer", tc["conifer"], con, 845)
    SC.scatter("ForestBroad", tc["broad"], brd, 845)

def roads_outside(M):
    north = [(0, 6)] + [(math.sin(t / 9) * 120 * (t / 40), 6 + t * 60) for t in range(1, 120)]
    ribbon("RoadNorth", north, 9, M["dirt"], z=0.25)
    south = [(0, -TIP - 6)] + [(math.sin(t / 7) * 90 * (t / 30), -TIP - 6 - t * 60) for t in range(1, 100)]
    ribbon("RoadSouth", south, 8, M["dirt"], z=0.25)

def hamlets(M, hc_widths=None):
    """Small red-roofed hamlets inside Wall Maria near the inner gate (anime aerial, bottom left)."""
    hc = bpy.data.collections["HouseVariants"]
    r = random.Random(31)
    pts = []
    spots = ((-420, 260, 26), (250, 380, 18), (-160, 820, 22), (600, 700, 16), (-900, 520, 20), (90, 140, 14))
    if A.shot == "T3":
        spots = ((-420, 360, 26), (-160, 820, 22), (600, 900, 16), (-900, 520, 20))
    for cx, cy, n in spots:
        for _ in range(n * 3):
            x, y = cx + r.gauss(0, 45), cy + r.gauss(0, 35)
            if abs(x) < 12 or canal_dist(x, y) < 30 or y < 40:
                continue
            if any((x - p[0]) ** 2 + (y - p[1]) ** 2 < 150 for p in pts):
                continue
            pts.append((x, y, height(x, y) - 0.4, r.uniform(0, 6.28) if r.random() < 0.3 else 0.0, r.uniform(0.9, 1.05),
                        r.randrange(48), -1e4, 1e5))
            if len([p for p in pts if abs(p[0] - cx) < 200 and abs(p[1] - cy) < 200]) >= n:
                break
    SC.scatter("Hamlets", hc, pts, 845)

# ------------------------------------------------------------------ world, light, camera, render
def build_world():
    sc = bpy.context.scene
    w = bpy.data.worlds.new("Sky"); sc.world = w; w.use_nodes = True
    nt = w.node_tree; N, L = nt.nodes, nt.links
    bg = N["Background"]
    az, el, energy, scol = S["sun"]
    hor, zen = S["sky"]
    # lighting: flat-ish sky ambient (horizon/zenith blend by direction)
    tc = N.new("ShaderNodeTexCoord"); sz = N.new("ShaderNodeSeparateXYZ"); L.new(tc.outputs["Generated"], sz.inputs[0])
    gr = N.new("ShaderNodeValToRGB"); ge = gr.color_ramp.elements
    ge[0].position, ge[0].color = 0.0, (*hor, 1)
    ge[1].position, ge[1].color = 0.42, (*zen, 1)
    mr = N.new("ShaderNodeMapRange"); mr.inputs["From Min"].default_value = -0.05; mr.inputs["From Max"].default_value = 1.0
    L.new(sz.outputs["Z"], mr.inputs["Value"]); L.new(mr.outputs["Result"], gr.inputs[0])
    # sun glow on the sky for camera rays
    sd = Vector((math.cos(math.radians(az)) * math.cos(math.radians(el)), math.sin(math.radians(az)) * math.cos(math.radians(el)),
                 math.sin(math.radians(el))))
    dot = N.new("ShaderNodeVectorMath"); dot.operation = "DOT_PRODUCT"; dot.inputs[1].default_value = sd
    L.new(tc.outputs["Generated"], dot.inputs[0])
    pw = N.new("ShaderNodeMath"); pw.operation = "POWER"; pw.inputs[1].default_value = 24.0; pw.use_clamp = True
    cl = N.new("ShaderNodeMath"); cl.operation = "MAXIMUM"; cl.inputs[1].default_value = 0.0
    L.new(dot.outputs["Value"], cl.inputs[0]); L.new(cl.outputs[0], pw.inputs[0])
    gm = N.new("ShaderNodeMix"); gm.data_type = "RGBA"; gm.inputs["B"].default_value = (*[min(1, c * 1.2) for c in scol], 1)
    L.new(pw.outputs[0], gm.inputs["Factor"]); L.new(gr.outputs["Color"], gm.inputs["A"])
    # painted cumulus: noise on a cloud plane (direction.xy / direction.z), only above the horizon
    nrm = N.new("ShaderNodeVectorMath"); nrm.operation = "NORMALIZE"; L.new(tc.outputs["Generated"], nrm.inputs[0])
    sz2 = N.new("ShaderNodeSeparateXYZ"); L.new(nrm.outputs["Vector"], sz2.inputs[0])
    zc = N.new("ShaderNodeMath"); zc.operation = "ADD"; zc.inputs[1].default_value = 0.06; L.new(sz2.outputs["Z"], zc.inputs[0])
    px_ = N.new("ShaderNodeMath"); px_.operation = "DIVIDE"; L.new(sz2.outputs["X"], px_.inputs[0]); L.new(zc.outputs[0], px_.inputs[1])
    py_ = N.new("ShaderNodeMath"); py_.operation = "DIVIDE"; L.new(sz2.outputs["Y"], py_.inputs[0]); L.new(zc.outputs[0], py_.inputs[1])
    cp = N.new("ShaderNodeCombineXYZ"); L.new(px_.outputs[0], cp.inputs["X"]); L.new(py_.outputs[0], cp.inputs["Y"])
    cn = N.new("ShaderNodeTexNoise"); cn.inputs["Scale"].default_value = S.get("cloud_scale", 1.3)
    cn.inputs["Detail"].default_value = 7; cn.inputs["Roughness"].default_value = 0.62
    L.new(cp.outputs[0], cn.inputs["Vector"])
    cr = N.new("ShaderNodeMapRange"); cr.inputs["From Min"].default_value = S.get("cloud_lo", 0.56)
    cr.inputs["From Max"].default_value = S.get("cloud_lo", 0.56) + 0.12
    L.new(cn.outputs["Fac"], cr.inputs["Value"])
    hz_ = N.new("ShaderNodeMapRange"); hz_.inputs["From Min"].default_value = 0.0; hz_.inputs["From Max"].default_value = 0.12
    L.new(sz2.outputs["Z"], hz_.inputs["Value"])
    cm = N.new("ShaderNodeMath"); cm.operation = "MULTIPLY"; L.new(cr.outputs["Result"], cm.inputs[0]); L.new(hz_.outputs["Result"], cm.inputs[1])
    cmx = N.new("ShaderNodeMix"); cmx.data_type = "RGBA"; cmx.inputs["B"].default_value = (*S.get("cloud", (0.95, 0.95, 0.96)), 1)
    L.new(cm.outputs[0], cmx.inputs["Factor"]); L.new(gm.outputs["Result"], cmx.inputs["A"])
    bg2 = N.new("ShaderNodeBackground"); bg2.inputs["Strength"].default_value = 1.0
    L.new(cmx.outputs["Result"], bg2.inputs["Color"])
    L.new(gr.outputs["Color"], bg.inputs["Color"]); bg.inputs["Strength"].default_value = S["amb"]
    lp = N.new("ShaderNodeLightPath"); mx = N.new("ShaderNodeMixShader")
    L.new(lp.outputs["Is Camera Ray"], mx.inputs[0]); L.new(bg.outputs[0], mx.inputs[1]); L.new(bg2.outputs[0], mx.inputs[2])
    L.new(mx.outputs[0], N["World Output"].inputs["Surface"])
    sun = bpy.data.lights.new("Sun", "SUN"); sun.energy = energy; sun.color = scol; sun.angle = math.radians(1.0)
    so = link(bpy.data.objects.new("Sun", sun))
    so.rotation_euler = sd.to_track_quat("Z", "Y").to_euler()
    return sd

def build_camera():
    loc, tgt, lens = S["cam"]
    cd = bpy.data.cameras.new("Cam"); cd.lens = lens; cd.clip_start = 1.0; cd.clip_end = 40000
    co = link(bpy.data.objects.new("Cam", cd))
    co.location = loc
    co.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.camera = co
    return co

def render_setup():
    sc = bpy.context.scene
    w, h = map(int, A.res.split("x"))
    sc.render.resolution_x, sc.render.resolution_y = w, h; sc.render.resolution_percentage = 100
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"; sc.cycles.samples = A.samples
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 4; sc.cycles.diffuse_bounces = 2; sc.cycles.glossy_bounces = 1
    sc.cycles.transparent_max_bounces = 16
    sc.cycles.use_adaptive_sampling = True
    sc.render.threads_mode = "FIXED"; sc.render.threads = 4
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"
    sc.view_settings.exposure = S["expo"]
    sc.render.image_settings.file_format = "PNG"

# ------------------------------------------------------------------ materials
def materials():
    M = {
        "stone": wall_mat() if A.shot == "T2" else wall_mat_courses(),
        "gatewood": pmat("GateWood", lin("3B2A20"), 0.8),
        "iron": pmat("Iron", lin("4A4A50"), 0.5, 0.5),
        "keg": pmat("Keg", lin("53311B"), 0.8),
        "window": pmat("Window", lin("2A2622"), 0.6),          # scene.house_mesh now expects mats["window"]
        "plaster": pmat("Plaster", lin("D8CDB4"), 0.9),
        "plaster_w": pmat("PlasterW", lin("E4DCCB"), 0.9),
        "plaster_o": pmat("PlasterO", lin("C9B48E"), 0.9),
        "timber": pmat("Timber", lin("8A6E55"), 0.9),
        "stone_h": pmat("StoneH", lin("C1B59D"), 0.9),
        "roof_a": noise_mat("RoofA", lin("8A5038"), lin("A06446"), 0.6),
        "roof_b": noise_mat("RoofB", lin("74483A"), lin("8C5C48"), 0.6),
        "roof_c": noise_mat("RoofC", lin("965A42"), lin("A86A4E"), 0.6),
        "roof_d": noise_mat("RoofD", lin("6E5246"), lin("806252"), 0.6),
        "roof_e": noise_mat("RoofE", lin("8A6650"), lin("9E7860"), 0.6),
        "roof_f": noise_mat("RoofF", lin("5E4238"), lin("745446"), 0.6),
        "roof_slate": pmat("RoofSlate", lin("6B7C8F"), 0.6),
        "roof_g": noise_mat("RoofG", lin("7D6660"), lin("917550"), 0.6),
        "bark": pmat("Bark", lin("3A2A1E"), 0.9),
        "leaf": noise_mat("Leaf", lin("3F6A2A"), lin("6E9A3A"), 0.5),
        "leaf2": noise_mat("Leaf2", lin("2F5A2A"), lin("527E32"), 0.5),
        "leaf3": noise_mat("Leaf3", lin("4C7230"), lin("7FA046"), 0.5),
        "leaf_dark": noise_mat("LeafDark", lin("335F3E"), lin("62904E"), 0.5),
        "street": noise_mat("Street", lin("A39272"), lin("B9A884"), 0.1),
        "walkway": noise_mat("Walkway", lin("A89F86"), lin("C2B79A"), 0.3),
        "paving": noise_mat("Paving", lin("998E73"), lin("ADA286"), 0.2),
        "dirt": noise_mat("Dirt", lin("A08B62"), lin("B59D6D"), 0.08),
        "quay": noise_mat("Quay", lin("6D6C5D"), lin("8A8775"), 0.3),
        "water": pmat("Water", lin("3E6E78"), 0.12, 0.5),
        "white": pmat("White", lin("E6E2D6"), 0.6),
        "gatehouse": noise_mat("Gatehouse", lin("B9B6AE"), lin("CFCCC4"), 0.2),
        "shadow": pmat("Shadow", (0.01, 0.01, 0.01), 1.0),
        "ground": ground_mat(),
        "district_ground": noise_mat("DistrictGround", lin("6B7B3A"), lin("8E8A5A"), 0.03),
        "plaster_c": pmat("PlasterC", lin("D8CDB4"), 0.9),
    }
    return M

def haze_all(skip=()):
    for m in bpy.data.materials:
        if m.name in skip:
            continue
        add_haze(m)

# ------------------------------------------------------------------ T3 / T4 props
def boat(name, M, seed, crowd=True):
    r = random.Random(seed)
    bm = bmesh.new()
    Lb, Bb = r.uniform(13, 17), r.uniform(3.6, 4.2)
    # hull: tapered box (flat bottom, square stern, pointed-ish bow)
    hull = box(bm, Vector((0, 0, 0.45)), (Lb, Bb, 1.3), mi=0)
    for v in hull["verts"]:
        if v.co.x > Lb * 0.3:
            v.co.y *= 0.55
        if v.co.z < 0:
            v.co.y *= 0.8
    box(bm, Vector((0, 0, 1.12)), (Lb - 0.6, Bb - 0.5, 0.06), mi=1)
    # people: small capsules approximated by stacked boxes (body + head)
    if crowd:
        cols = 0
        for i in range(int(Lb * Bb * 1.3)):
            x, y = r.uniform(-Lb / 2 + 1.0, Lb / 2 - 1.5), r.uniform(-Bb / 2 + 0.5, Bb / 2 - 0.5)
            mi = 2 + r.randrange(5)
            hgt = r.uniform(1.35, 1.75)
            box(bm, Vector((x, y, 1.15 + hgt * 0.4)), (0.45, 0.32, hgt * 0.8), r.uniform(0, 3), mi)
            box(bm, Vector((x, y, 1.15 + hgt * 0.9)), (0.24, 0.24, 0.24), 0, 7)
    ob = bm_ob(name, bm, [M["boat"], M["deck"], M["cloth1"], M["cloth2"], M["cloth3"], M["cloth4"], M["cloth5"], M["skin"]])
    return ob

def place_on_canal(ob, s_from_wall, side=0.0):
    """Put an object on the canal north of Wall Maria, at path distance s from the wall, heading north."""
    pts = [p for p in CANAL if p[1] > 0]
    acc = 0.0
    for k in range(len(pts) - 1):
        a, b = Vector(pts[k]), Vector(pts[k + 1])
        seg = (b - a).length
        if acc + seg >= s_from_wall:
            t = (s_from_wall - acc) / seg
            p = a.lerp(b, t)
            d = (b - a).normalized()
            n = Vector((-d.y, d.x))
            p += n * side
            ob.location = (p.x, p.y, 0.35)
            ob.rotation_euler.z = math.atan2(d.y, d.x)
            return
        acc += seg

def place_in_district_canal(ob, y, side=0.0):
    ob.location = (CX + side, y, 0.35); ob.rotation_euler.z = math.pi / 2

def dust_cloud(name, center, radius, n, m, seed, flat=0.6, up=0.0, coll=None):
    r = random.Random(seed)
    bm = bmesh.new()
    for i in range(n):
        rr = r.uniform(0.35, 1.0) * radius * 0.45
        c = Vector((r.gauss(0, radius * 0.45), r.gauss(0, radius * 0.45) * 0.8, 0))
        c.z = abs(r.gauss(0, radius * 0.25)) * flat + rr * 0.6 + up * r.random()
        s = bmesh.ops.create_icosphere(bm, subdivisions=3, radius=rr)
        for v in s["verts"]:
            v.co.z *= 0.8
            v.co += Vector((noise.noise(v.co * 0.15 + Vector((i, 0, 0))), noise.noise(v.co * 0.15 + Vector((0, i, 3))),
                            noise.noise(v.co * 0.15 + Vector((5, 1, i))))) * rr * 0.25
            v.co += c + Vector(center)
    ob = bm_ob(name, bm, [m], coll, smooth=True)
    return ob

def debris(name, center, n, M, seed, spread=(60, 70, 30), size=(1.0, 5.0), dirn=Vector((0, 1, 0.4)), air=0.5):
    """Irregular wall chunks: jittered low-poly rocks, most on the ground, some in flight."""
    r = random.Random(seed)
    bm = bmesh.new()
    for i in range(n):
        s = r.uniform(*size) * (r.random() ** 1.5 * 0.8 + 0.2)
        t = r.random()
        p = Vector(center) + dirn * t * spread[1] + Vector((r.gauss(0, spread[0] * 0.25 * (0.3 + t)), r.uniform(-4, 4),
                                                            r.uniform(0, spread[2]) * (1 - t * 0.6)))
        if r.random() > air:
            p.z = r.uniform(0, 0.8) + s * 0.25                              # on the ground
        res = bmesh.ops.create_icosphere(bm, subdivisions=1, radius=1.0)
        sx, sy, sz = r.uniform(0.7, 1.6), r.uniform(0.6, 1.3), r.uniform(0.4, 0.9)
        rot = Euler((r.uniform(0, 3), r.uniform(0, 3), r.uniform(0, 3))).to_matrix()
        mi = 0 if r.random() < 0.85 else 1
        for v in res["verts"]:
            q = Vector((v.co.x * sx, v.co.y * sy, v.co.z * sz)) * (1 + r.uniform(-0.25, 0.25))
            v.co = p + (rot @ q) * s * 0.6
        for f in {f for v in res["verts"] for f in v.link_faces}:
            f.material_index = mi
    return bm_ob(name, bm, [M["stone"], M["gatewood"]])

def pose_armored(rig):
    """Shoulder charge out through the gate (bible 3.5 / S1E2): leaning hard forward, arms tucked, stride."""
    P = rig.pose.bones
    def rot(bn, x=0.0, y=0.0, z=0.0):
        b = P.get(bn)
        if b:
            b.rotation_mode = "XYZ"; b.rotation_euler = (x, y, z)
    for bn, x in (("spine05", 0.30), ("spine04", 0.32), ("spine03", 0.28), ("spine02", 0.2), ("spine01", 0.15)):
        rot(bn, x)
    rot("neck01", -0.5); rot("head", -0.55)
    rot("upperleg01.L", -0.95); rot("lowerleg01.L", 1.25); rot("foot.L", -0.2)
    rot("upperleg01.R", 0.35); rot("lowerleg01.R", 0.6); rot("foot.R", 0.4)
    rot("upperarm01.L", -0.6, 0.0, -0.6); rot("lowerarm01.L", 1.2)
    rot("upperarm01.R", 0.5, 0.0, 0.85); rot("lowerarm01.R", 0.9)
    rot("root", 0.0)

def ground_rig(rig, z0=0.0):
    """Drop a posed rig so its lowest body vertex touches z0."""
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    lo = 1e9
    for ob in rig.children:
        if ob.type == "MESH" and ob.name.endswith("_body"):
            ev = ob.evaluated_get(dg)
            me = ev.to_mesh()
            mw = ob.matrix_world
            lo = min(lo, min((mw @ v.co).z for v in me.vertices))
            ev.to_mesh_clear()
    if lo < 1e8:
        rig.location.z += z0 - lo

def titan_on_ground(rig, x, y, heading, frame_offset=0, walk=True):
    import pure_titans as PT
    if walk:
        PT.walk_action(rig, cycle_frames=48, offset=frame_offset, travel=False)
    else:
        PT.idle_pose(rig)
    rig.location = (x, y, height(x, y) - 0.2)
    rig.rotation_euler.z = heading

PALE_SKINS = [(0.80, 0.56, 0.45), (0.84, 0.62, 0.52), (0.78, 0.50, 0.44), (0.82, 0.60, 0.50), (0.76, 0.54, 0.46)]

def make_pures(spots, pale=False):
    import pure_titans as PT
    out = []
    if pale:                                             # round 2: pale beige / pink skins instead of orange
        for k, key in enumerate(list(PT.PRESETS.keys())):
            PT.PRESETS[key] = dict(PT.PRESETS[key], skin=PALE_SKINS[k % len(PALE_SKINS)])
    for i, (preset, x, y, heading, hgt, off) in enumerate(spots):
        kw = dict(preset=preset) if preset not in ("smiling",) else {}
        rig = PT.make_pure("smiling" if preset == "smiling" else "generic", seed=40 + i, height=hgt, **kw)
        titan_on_ground(rig, x, y, heading, off)
        out.append(rig)
        log("pure", preset, hgt)
    return out

def heading_to(x, y, tx, ty):
    """rig local -Y faces forward: heading so that -Y points from (x,y) toward (tx,ty)."""
    return math.atan2(ty - y, tx - x) + math.pi / 2

# ------------------------------------------------------------------ shots
def shot_common(M, forest_bounds, forest_density):
    sc = bpy.context.scene
    sc.frame_set(1)
    build_terrain(M["ground"])
    build_walls(M, broken=(A.shot == "T3"))
    build_canal(M)
    roads_outside(M)
    tc = tree_variants(M)
    if A.lite:
        return
    build_town(M, tc)
    hamlets(M)
    if not A.clay:
        build_forest(tc, forest_bounds, forest_density)

def shot_T3(M):
    # light pouring through the broken gate (bible 1.4: tall rough arch hole full of bright light)
    gl = bmesh.new(); box(gl, Vector((0, -6, 12)), (19, 0.4, 24))
    bm_ob("GateGlow", gl, [pmat("GateGlowM", (1, 0.8, 0.55), 1.0, 0.0, emit=(1.0, 0.78, 0.5), estr=9.0)])
    # anime dust: sunlit beige billows hugging the ground in front of the wall, thinner plumes above
    dlit = puff_mat("Dust", lin("D2C2A6"), alpha=0.9, emit=(0.80, 0.62, 0.48), estr=0.12)
    dthin = puff_mat("DustThin", lin("DCCDB2"), alpha=0.5, emit=(0.80, 0.62, 0.48), estr=0.12)
    dust_cloud("DustGate", (4, 16, -2), 20, 18, dlit, 3, flat=0.2)
    dust_cloud("DustL", (-30, 14, -2), 22, 14, dlit, 13, flat=0.2)
    dust_cloud("DustR", (36, 13, -2), 20, 12, dlit, 23, flat=0.2)
    dust_cloud("DustHigh", (2, 10, 14), 12, 8, dthin, 4, flat=0.5, up=8)
    dust_cloud("DustFeet", (-2, 26, -3), 10, 8, dthin, 5, flat=0.1)
    if A.variant != "hero":
        dust_cloud("Plume", (0, 18, 8), 46, 22, dlit, 9, flat=0.6, up=38)
        dust_cloud("PlumeTop", (4, 12, 40), 34, 12, dthin, 19, flat=0.5, up=18)
        dust_cloud("DustRoll", (-40, 30, -3), 70, 22, dlit, 29, flat=0.15)
    else:
        dust_cloud("HeroPlume", (14, 12, 12), 22, 14, dthin, 9, flat=0.5, up=22)
        dust_cloud("HeroRollL", (-55, 22, -3), 30, 14, dlit, 39, flat=0.15)
        dust_cloud("HeroRollR", (70, 20, -3), 30, 12, dthin, 49, flat=0.15)
    if True:
        # chunks thrown out of the breach, flying toward the camera
        tc_ = Vector((CAM_LOC.x, CAM_LOC.y, 0)) - Vector((0, 10, 0))
        dirn = Vector((tc_.x, tc_.y, 0)).normalized()
        dirn.z = 0.12
        reach = (CAM_LOC.to_2d() - Vector((0, 10))).length * 0.8
        debris("Flying", (0, 14, 12), 160 if A.variant != "hero" else 70, M, 17,
               spread=(150 if A.variant != "hero" else 30, reach, 30 if A.variant != "hero" else 16),
               size=(1.0, 4.5) if A.variant != "hero" else (0.4, 1.6), dirn=dirn, air=0.85)
        near = bmesh.new()
        rn = random.Random(5)
        for k in range(9):
            dist = rn.uniform(45, 140) if A.variant != "hero" else rn.uniform(14, 40)
            p = Vector((CAM_LOC.x, CAM_LOC.y, 0)) + (Vector((0, 10, 0)) - Vector((CAM_LOC.x, CAM_LOC.y, 0))).normalized() * dist
            p += Vector((rn.uniform(-0.3, 0.3) * dist * 0.4, rn.uniform(-0.3, 0.3) * dist * 0.4, 0))
            p.z = rn.uniform(4, 14) if A.variant != "hero" else rn.uniform(2, 9)
            sz = rn.uniform(0.5, 1.4) if A.variant != "hero" else rn.uniform(0.25, 0.7)
            res = bmesh.ops.create_icosphere(near, subdivisions=2, radius=sz)
            rot = Euler((rn.uniform(0, 3), rn.uniform(0, 3), rn.uniform(0, 3))).to_matrix()
            for v in res["verts"]:
                q = Vector((v.co.x * 1.3, v.co.y, v.co.z * 0.7))
                q += Vector((noise.noise(q * 1.5 + Vector((k, 0, 0))), noise.noise(q * 1.5 + Vector((0, k, 0))), 0)) * sz * 0.3
                v.co = p + rot @ q
        bm_ob("NearChunks", near, [M["stone"]])
    debris("Debris", (0, 8, 3), 240, M, 7, spread=(50, 60, 14), size=(0.4, 2.4), air=0.2)
    debris("DoorBits", (0, 9, 4), 30, M, 8, spread=(26, 44, 10), size=(1.2, 4), air=0.3)
    # ferry boats leaving through the water gate (and still loading inside)
    bm_mats(M)
    boat_s = (22, 48, 76, 105, 140, 178, 220, 265)
    if A.variant not in ("hero", "canal"):
        boat_s = (6, 20, 34, 48, 62, 78)
    if A.variant == "canal":
        boat_s = (30, 70, 115, 170, 230, 300, 370, 430, 480, 525, 565)
    for i, s_ in enumerate(boat_s):
        b = boat(f"Boat{i}", M, 100 + i)
        place_on_canal(b, s_, side=(-5 if i % 2 else 5))
    for i, y in enumerate((-30, -62, -95)):
        b = boat(f"BoatIn{i}", M, 200 + i)
        place_in_district_canal(b, y, side=(-5 if i % 2 else 5))
    if not (A.no_titans or A.clay):
        import shifters
        rig = shifters.make_armored()
        pose_armored(rig)
        rig.location = (-4, 30, 0.0); rig.rotation_euler = (0.22, 0.0, heading_to(-4, 30, 10, 200))
        if A.variant != "hero":
            rig.location = (46, 58, 0.0); rig.rotation_euler = (0.22, 0.0, heading_to(46, 58, 90, 300))
            dust_cloud("ChargeTrail", (22, 34, -3), 26, 14, puff_mat("Trail", lin("D2C2A6"), alpha=0.7, emit=(0.8, 0.62, 0.48), estr=0.12), 33, flat=0.12)
        ground_rig(rig, 0.4)
        spots = [("smiling", 6, 4, heading_to(6, 4, 60, 200), 14, 21),
                 ("bald_grinner", 62, 58, heading_to(62, 58, -60, 400), 13, 3),
                 ("ruddy_brute", 170, 120, heading_to(170, 120, 260, 520), 12, 17),
                 ("blond_sleeper", 230, 60, heading_to(230, 60, 300, 300), 10, 29),
                 ("pale_starer", 60, 95, heading_to(60, 95, 100, 400), 8, 9),
                 ("messy_gaper", 130, 210, heading_to(130, 210, 200, 500), 7, 37),
                 ("potbelly", 35, 50, heading_to(35, 50, 80, 300), 5, 11),
                 ("runt", 110, 85, heading_to(110, 85, 150, 300), 3.5, 41)]
        if A.variant != "hero":
            spots = [("smiling", 4, 4, heading_to(4, 4, 80, 200), 14, 21),
                     ("bald_grinner", 95, 70, heading_to(95, 70, 300, 200), 13, 3),
                     ("ruddy_brute", 150, 40, heading_to(150, 40, 280, 120), 12, 17),
                     ("blond_sleeper", 60, 120, heading_to(60, 120, 200, 300), 10, 29),
                     ("pale_starer", 200, 95, heading_to(200, 95, 300, 160), 8, 9),
                     ("messy_gaper", 125, 160, heading_to(125, 160, 300, 260), 7, 37),
                     ("potbelly", 40, 60, heading_to(40, 60, 140, 140), 5, 11),
                     ("runt", 230, 150, heading_to(230, 150, 330, 200), 3.5, 41)]
        make_pures(spots, pale=True)

def bm_mats(M):
    M["boat"] = pmat("Boat", lin("6B4E35"), 0.8)
    M["deck"] = pmat("Deck", lin("8A6A4A"), 0.85)
    for i, c in enumerate(("6F5A44", "4E5A6A", "8A7A5A", "6A3A2E", "B8AE96")):
        M[f"cloth{i + 1}"] = pmat(f"Cloth{i + 1}", lin(c), 0.9)
    M["skin"] = pmat("SkinH", lin("D8A888"), 0.7)

def grass_clump_mesh(name, m, seed, blades=28, h=(0.6, 1.4)):
    r = random.Random(seed)
    bm = bmesh.new()
    for _ in range(blades):
        a = r.uniform(0, 6.28); rr = r.uniform(0, 0.35)
        base = Vector((math.cos(a) * rr, math.sin(a) * rr, 0))
        hh = r.uniform(*h); w = r.uniform(0.03, 0.06)
        lean = Vector((math.cos(a), math.sin(a), 0)) * r.uniform(0.1, 0.45) * hh
        side = Vector((-math.sin(a + 1.2), math.cos(a + 1.2), 0)) * w
        prev = [bm.verts.new(base - side), bm.verts.new(base + side)]
        for k in range(1, 4):
            t = k / 3
            c = base + lean * t * t + Vector((0, 0, hh * t))
            sw = side * (1 - t * 0.85)
            cur = [bm.verts.new(c - sw), bm.verts.new(c + sw)]
            bm.faces.new((prev[0], prev[1], cur[1], cur[0]))
            prev = cur
    return bm_ob(name, bm, [m], None, smooth=True)

def conifer_mesh(name, m_leaf, m_bark, seed, tiers=9, h=18.0):
    """Anime-style spruce: stacked drooping tiers with jagged rims."""
    r = random.Random(seed)
    bm = bmesh.new()
    tr = bmesh.ops.create_cone(bm, cap_ends=True, segments=6, radius1=0.4, radius2=0.2, depth=h * 0.3)
    for v in tr["verts"]:
        v.co.z += h * 0.15
    for f in {f for v in tr["verts"] for f in v.link_faces}:
        f.material_index = 1
    for t in range(tiers):
        z0 = h * (0.12 + 0.82 * t / tiers)
        rad = (1 - t / tiers) * h * 0.2 + 0.4
        seg = 14
        ring = []
        for k in range(seg):
            a = 6.283 * k / seg + r.uniform(-0.1, 0.1)
            rk = rad * (1.0 if k % 2 == 0 else 0.72) * r.uniform(0.85, 1.1)
            ring.append(bm.verts.new((math.cos(a) * rk, math.sin(a) * rk, z0 - rad * 0.25)))
        tip = bm.verts.new((r.uniform(-.1, .1), r.uniform(-.1, .1), z0 + rad * 0.9))
        for k in range(seg):
            bm.faces.new((ring[k], ring[(k + 1) % seg], tip))
        bm.faces.new(list(reversed(ring)))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm_ob(name, bm, [m_leaf, m_bark], None)

def proto_coll(name):
    c = bpy.data.collections.new(name); bpy.context.scene.collection.children.link(c)
    bpy.context.view_layer.layer_collection.children[name].exclude = True
    return c

def shot_T4(M):
    loc, tgt, lens = S["cam"]
    d = Vector((tgt[0] - loc[0], tgt[1] - loc[1])).normalized()
    rgt = Vector((d.y, -d.x))
    c0 = Vector(loc[:2])
    def at(dist, lat):
        return c0 + d * dist + rgt * lat
    # (preset, distance, lateral (+ right), height m, walk direction relative to 'toward camera' deg, cycle offset)
    lay = [("bald_grinner", 27, -3, 15.0, 10, 18), ("smiling", 60, 20, 13.0, -15, 7), ("messy_gaper", 50, -26, 7.0, 30, 5),
           ("runt", 85, 6, 4.0, 25, 31),
           ("bald_grinner", 120, 34, 12, -60, 9), ("blond_sleeper", 150, -48, 10, 40, 27),
           ("ruddy_brute", 185, 8, 11, 120, 40), ("pale_starer", 210, -95, 8, -90, 2)]
    spots = []
    for pre, dist, lat, hgt, rel, off in lay:
        p = at(dist, lat)
        tw = (c0 - p).normalized()
        a = math.radians(-rel)
        w = Vector((tw.x * math.cos(a) - tw.y * math.sin(a), tw.x * math.sin(a) + tw.y * math.cos(a)))
        spots.append((pre, p.x, p.y, heading_to(p.x, p.y, p.x + w.x * 100, p.y + w.y * 100), hgt, off))
    r = random.Random(4)
    # tall grass in the foreground
    gm = noise_mat("GrassBlade", lin("5E8636"), lin("A9B860"), 0.8, rough=0.7)
    gc = proto_coll("GrassProtos")
    for k in range(4):
        gc.objects.link(grass_clump_mesh(f"G{k}", gm, k, h=(0.2, 0.4) if k < 2 else (0.3, 0.6)))
        bpy.context.scene.collection.objects.unlink(bpy.data.objects[f"G{k}"])
    pts = []
    for _ in range(9000):
        dist = 2.5 + r.random() ** 1.8 * 70
        lat = r.uniform(-0.75, 0.75) * dist
        p = at(dist, lat)
        if noise.noise(Vector((p.x / 9, p.y / 9, 3))) < -0.25:
            continue
        pts.append((p.x, p.y, height(p.x, p.y) - 0.05, r.uniform(0, 6.28), r.uniform(0.8, 1.15), r.randrange(4), -1e4, 1e5))
    SC.scatter("TallGrass", gc, pts, 845)
    # human-scale cues: a split-rail fence, an abandoned hay cart, a small farmhouse
    wood = pmat("FenceWood", lin("6B5040"), 0.85)
    fb = bmesh.new()
    for k in range(16):
        p = at(9 + k * 0.9, -14 + k * 2.4)
        box(fb, Vector((p.x, p.y, height(p.x, p.y) + 0.6)), (0.14, 0.14, 1.3), r.uniform(-.1, .1))
        if k < 15:
            q = at(9 + (k + 0.5) * 0.9, -14 + (k + 0.5) * 2.4)
            ang = math.atan2((at(10, -11.6) - at(9, -14)).y, (at(10, -11.6) - at(9, -14)).x)
            for zz in (0.55, 1.0):
                box(fb, Vector((q.x, q.y, height(q.x, q.y) + zz)), (2.6, 0.08, 0.1), ang)
    bm_ob("Fence", fb, [wood])
    cb = bmesh.new()
    cp = at(13, 5.0); ca = 0.6
    gz = height(cp.x, cp.y)
    box(cb, Vector((cp.x, cp.y, gz + 0.85)), (2.8, 1.4, 0.35), ca)                      # bed
    for sy in (-0.68, 0.68):                                                           # side boards
        o = Vector((-math.sin(ca), math.cos(ca))) * sy
        box(cb, Vector((cp.x + o.x, cp.y + o.y, gz + 1.15)), (2.8, 0.08, 0.5), ca)
    hay = bmesh.ops.create_icosphere(cb, subdivisions=2, radius=1.0)
    for v in hay["verts"]:
        v.co = Vector((v.co.x * 1.25, v.co.y * 0.7, max(v.co.z, -0.2) * 0.55))
        v.co.rotate(Euler((0, 0, ca)))
        v.co += Vector((cp.x, cp.y, gz + 1.25))
    for f in {f for v in hay["verts"] for f in v.link_faces}:
        f.material_index = 1
    for sx in (-0.9, 0.9):
        for sy in (-0.8, 0.8):
            w_ = Vector((cp.x, cp.y)) + Vector((math.cos(ca), math.sin(ca))) * sx + Vector((-math.sin(ca), math.cos(ca))) * sy
            wh = bmesh.ops.create_cone(cb, cap_ends=True, segments=16, radius1=0.6, radius2=0.6, depth=0.1)
            R = Matrix.Rotation(ca, 3, "Z") @ Matrix.Rotation(math.pi / 2, 3, "X")
            bmesh.ops.rotate(cb, cent=(0, 0, 0), matrix=R, verts=wh["verts"])
            bmesh.ops.translate(cb, vec=(w_.x, w_.y, gz + 0.6), verts=wh["verts"])
    pole = Vector((cp.x, cp.y)) + Vector((math.cos(ca), math.sin(ca))) * 2.4
    box(cb, Vector((pole.x, pole.y, gz + 0.55)), (2.2, 0.08, 0.08), ca)
    bm_ob("Cart", cb, [wood, pmat("Hay", lin("C2A35A"), 0.95)])
    fh = link(bpy.data.objects.new("Farmhouse", SC.house_mesh("FarmhouseM", 7.0, 9.0, 4.2, 3.6, M, "plaster", "roof_b")))
    hp = at(40, -13); fh.location = (hp.x, hp.y, height(hp.x, hp.y) - 0.3); fh.rotation_euler.z = 0.5
    sh = link(bpy.data.objects.new("Shed", SC.house_mesh("ShedM", 4.0, 5.0, 2.6, 1.8, M, "timber", "roof_d")))
    hp = at(36, -6.5); sh.location = (hp.x, hp.y, height(hp.x, hp.y) - 0.2); sh.rotation_euler.z = 0.3
    # rocks
    rk = bmesh.new()
    for (dist, lat, sz) in ((6, -3.0, 0.45), (8, 3.5, 0.3), (20, -9, 0.9), (24, 13, 0.7), (44, 20, 1.2), (14, 1.5, 0.25)):
        p = at(dist, lat)
        res = bmesh.ops.create_icosphere(rk, subdivisions=2, radius=sz)
        for v in res["verts"]:
            v.co.z *= 0.62
            v.co += Vector((noise.noise(v.co * 0.8 + Vector((dist, 0, 0))), noise.noise(v.co * 0.8 + Vector((0, lat, 0))),
                            noise.noise(v.co * 0.8 + Vector((3, 3, dist))))) * sz * 0.28
            v.co += Vector((p.x, p.y, height(p.x, p.y) + sz * 0.15))
    bm_ob("Rocks", rk, [noise_mat("Rock", lin("6E6A5E"), lin("A39C88"), 0.6, rough=0.9, bump=0.4)], smooth=False)
    # forest edge on the right (anime spruces) and a few on the far left
    leaf = noise_mat("Spruce", lin("1F3F2E"), lin("3E6A42"), 0.35, rough=0.85)
    bark = pmat("SpruceBark", lin("3A2A1E"), 0.9)
    fc = proto_coll("SpruceProtos")
    for k in range(4):
        ob = conifer_mesh(f"SP{k}", leaf, bark, k, h=18.0)
        bpy.context.scene.collection.objects.unlink(ob); fc.objects.link(ob)
    tp = []
    for _ in range(700):
        dist = r.uniform(25, 340)
        edge = 0.42 * dist + 20 + noise.noise(Vector((dist / 60, 0, 1))) * 14
        lat = edge + r.uniform(0, 140)
        p = at(dist, lat)
        tp.append((p.x, p.y, height(p.x, p.y) - 0.3, r.uniform(0, 6.28), r.uniform(0.75, 1.3), r.randrange(4), -1e4, 1e5))
    for _ in range(160):
        dist = r.uniform(240, 420)
        lat = -(0.5 * dist + r.uniform(0, 160))
        p = at(dist, lat)
        tp.append((p.x, p.y, height(p.x, p.y) - 0.3, r.uniform(0, 6.28), r.uniform(0.75, 1.2), r.randrange(4), -1e4, 1e5))
    # scale trees right beside the titans: 15-20 m spruces (a 13-15 m titan ~ tree height, the 7 m one ~ half)
    for (dist, lat, hgt) in ((70, 34, 18), (66, 40, 16), (74, 44, 20), (61, 8, 15), (54, -36, 15), (57, -40, 17),
                             (52, -44, 14), (29, -21, 17), (34, -25, 19), (31, 15, 16), (90, -10, 18), (95, 18, 19)):
        p = at(dist, lat)
        tp.append((p.x, p.y, height(p.x, p.y) - 0.3, r.uniform(0, 6.28), hgt / 18.0, r.randrange(4), -1e4, 1e5))
    SC.scatter("ForestEdge", fc, tp, 845)
    if not (A.no_titans or A.clay):                      # last: MPFB building purges unused materials
        make_pures(spots, pale=True)

def main():
    reset()
    M = materials()
    build_world()
    cam = build_camera()
    if A.shot == "T2":
        shot_common(M, (-2600, 1600, -2800, 1400), 0.016)
    elif A.shot == "T3":
        shot_common(M, (-2200, 2000, -900, 3200), 0.014)
        shot_T3(M)
    else:
        shot_common(M, (-2400, 2400, -4200, 300), 0.016)
        shot_T4(M)
    haze_all(skip=("Shadow", "GateGlowM"))
    render_setup()
    if A.shot in ("T3", "T4"):
        bpy.context.scene.frame_set(20)
    log("scene built")
    if A.save:
        bpy.ops.wm.save_as_mainfile(filepath=A.save)
    if A.out:
        bpy.context.scene.render.filepath = A.out
        bpy.ops.render.render(write_still=True)
        log("rendered", A.out)

if __name__ == "__main__":
    main()
