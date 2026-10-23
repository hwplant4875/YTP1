"""S1E1 opening shot: young Eren under the big tree on the hill, Wall Maria behind (anime-in-3D look).

Run:  blender -b -P shot_opening.py -- --out x.png [--frame 61] [--res 960x540] [--samples 32]
          [--engine CYCLES|EEVEE] [--clay] [--save x.blend] [--no-chars] [--lineart]

Units are metres. Camera at the origin looking +Y (level, 50 mm on 36 mm film), eye 0.55 m above the
flower bank. Ground at the camera is z = 0. The tree stands on a rise ~32 m ahead-left; Wall Maria runs
across the frame 300-400 m away, closer on the right. Eren sits at frame start+60 (default frame 61).
"""
import bpy, bmesh, math, random, sys, os, argparse
import numpy as np
from mathutils import Vector, Matrix, noise

HERE = os.path.dirname(os.path.abspath(__file__))
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ap = argparse.ArgumentParser()
ap.add_argument("--out", default="")
ap.add_argument("--frame", type=int, default=61)
ap.add_argument("--res", default="960x540")
ap.add_argument("--samples", type=int, default=32)
ap.add_argument("--engine", default="CYCLES")
ap.add_argument("--save", default="")
ap.add_argument("--clay", action="store_true", help="fast layout pass: no scatter, no characters")
ap.add_argument("--no-chars", action="store_true")
ap.add_argument("--lineart", action="store_true")
ap.add_argument("--comp", action="store_true", help="add the compositor glare / sun-beam pass")
A = ap.parse_args(argv)

ASSETS = "/tmp/claude-0/aot/assets/polyhaven"
CAM_Z = 0.55
LENS = 50.0
SUN_DIR = Vector((0.62, 0.42, 0.66)).normalized()      # direction TO the sun: right, behind, ~41 deg up
HAZE = (0.60, 0.74, 0.92)                              # linear haze colour (pale sky blue)
TREE = Vector((-7.1, 30.0, 0.0))                       # trunk base (z filled from terrain)
rnd = random.Random(11)
np_rng = np.random.default_rng(11)

# ------------------------------------------------------------------ scene reset
def reset():
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)
    for m in list(bpy.data.meshes):
        bpy.data.meshes.remove(m)
    for m in list(bpy.data.materials):
        bpy.data.materials.remove(m)

def link(ob, coll=None):
    (coll or bpy.context.scene.collection).objects.link(ob)
    return ob

def new_coll(name, hide=False):
    c = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(c)
    if hide:
        lc = bpy.context.view_layer.layer_collection.children[name]
        lc.exclude = True
    return c

def mesh_ob(name, bm, mats=(), coll=None, smooth=False):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for m in mats:
        me.materials.append(m)
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
    ob = bpy.data.objects.new(name, me)
    return link(ob, coll)

# ------------------------------------------------------------------ terrain height field
def _fbm(x, y, oct=3):
    x = np.asarray(x, float); y = np.asarray(y, float)
    out = np.zeros(np.broadcast(x, y).shape)
    amp, f = 1.0, 1.0
    for o in range(oct):
        out += amp * (np.sin(x * f * 1.7 + 1.3 * o) * np.cos(y * f * 1.3 - 0.7 * o) + 0.5 * np.sin((x + y) * f * 0.9 + o))
        amp *= 0.5; f *= 2.1
    return out / 2.2

def smax(a, b, k=1.0):
    m = np.maximum(a, b)
    return m + k * np.log(np.exp((a - m) / k) + np.exp((b - m) / k))

def dome(x, y, cx, cy, rx, ry, top, fall):
    q2 = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
    return top - fall * q2

def ridge(x, y, a, b, za, zb, width, drop):
    """A ridge crest from a to b (heights za..zb) falling off quadratically to both sides and past the ends."""
    ax, ay = a; bx, by = b
    dx, dy = bx - ax, by - ay; L2 = dx * dx + dy * dy
    t = ((x - ax) * dx + (y - ay) * dy) / L2
    tc = np.clip(t, 0, 1)
    px, py = ax + tc * dx, ay + tc * dy
    d2 = (x - px) ** 2 + (y - py) ** 2
    return za + (zb - za) * tc - drop * d2 / (width * width)

def height(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float)
    valley = -8.0 + 0.8 * _fbm(x / 60.0, y / 60.0)
    valley = smax(valley, dome(x, y, 95, 275, 95, 70, 2.0, 8.5), 2.0)         # raised fields with the windmills
    valley = smax(valley, dome(x, y, -90, 250, 90, 60, -4.0, 5.0), 2.0)
    # the tree's rise: crest at the trunk, climbing to the back-left, falling to the right and toward the camera
    dx = x - TREE.x; dy = y - TREE.y
    base = 1.1 + 0.13 * np.minimum(np.maximum(0, -dx), 25) * np.exp(-np.maximum(0, dy) / 40.0)
    u = np.sqrt(np.maximum(0, dx + 0.5) ** 2 + (np.maximum(0, -dy) * 0.75) ** 2 + (np.maximum(0, dy - 4) * 0.8) ** 2)
    tree = base - (0.16 * u + 0.011 * u * u) + 0.12 * _fbm(x / 7.0, y / 7.0)
    # near ridge on the right (pale sunny slope)
    right = ridge(x, y, (3.0, 31.0), (34.0, 60.0), -2.4, -0.5, 9.0, 4.0) + 0.1 * _fbm(x / 9.0, y / 9.0)
    # the flower bank the camera sits on, dropping away beyond ~6 m
    bank = 0.04 * _fbm(x / 2.0, y / 2.0) - 0.002 * x ** 2 - 0.05 * np.maximum(0, y - 5.5) ** 2
    z = smax(valley, tree, 1.0)
    z = smax(z, right, 1.0)
    z = smax(z, bank, 0.4)
    return z

def hz(x, y):
    return float(height(x, y))

# ------------------------------------------------------------------ materials
def _nodes(m):
    m.use_nodes = True
    return m.node_tree.nodes, m.node_tree.links, m.node_tree.nodes["Principled BSDF"]

def add_haze(m, dist=900.0, strength=1.0, color=HAZE, power=1.0):
    """Aerial perspective that works in Cycles and Eevee: mix toward an emissive haze colour by view distance."""
    N, L = m.node_tree.nodes, m.node_tree.links
    out = N["Material Output"]
    src = out.inputs["Surface"].links[0].from_socket
    cam = N.new("ShaderNodeCameraData")
    mth = N.new("ShaderNodeMath"); mth.operation = "DIVIDE"; mth.inputs[1].default_value = -dist
    L.new(cam.outputs["View Distance"], mth.inputs[0])
    ex = N.new("ShaderNodeMath"); ex.operation = "EXPONENT"; L.new(mth.outputs[0], ex.inputs[0])
    inv = N.new("ShaderNodeMath"); inv.operation = "SUBTRACT"; inv.inputs[0].default_value = 1.0
    L.new(ex.outputs[0], inv.inputs[1])
    pw = N.new("ShaderNodeMath"); pw.operation = "POWER"; pw.inputs[1].default_value = power
    L.new(inv.outputs[0], pw.inputs[0])
    sc = N.new("ShaderNodeMath"); sc.operation = "MULTIPLY"; sc.inputs[1].default_value = strength
    sc.use_clamp = True
    L.new(pw.outputs[0], sc.inputs[0])
    em = N.new("ShaderNodeEmission"); em.inputs["Color"].default_value = (*color, 1); em.inputs["Strength"].default_value = 1.0
    mx = N.new("ShaderNodeMixShader")
    L.new(sc.outputs[0], mx.inputs[0]); L.new(src, mx.inputs[1]); L.new(em.outputs[0], mx.inputs[2])
    L.new(mx.outputs[0], out.inputs["Surface"])
    return m

def flat(name, col, rough=0.7, haze=None, sss=0.0, spec=0.3):
    m = bpy.data.materials.new(name); N, L, b = _nodes(m)
    b.inputs["Base Color"].default_value = (*col, 1); b.inputs["Roughness"].default_value = rough
    b.inputs["Specular IOR Level"].default_value = spec
    if sss:
        b.inputs["Subsurface Weight"].default_value = sss
    if haze:
        add_haze(m, haze)
    return m

def ramp_mat(name, stops, coord="Object", scale=1.0, noise_scale=1.0, detail=2.0, rough=0.8, haze=None,
             random_mix=0.0, bump=0.0, spec=0.25, distortion=0.0, w=0.0):
    """Painted colour: a noise field through a stepped colour ramp."""
    m = bpy.data.materials.new(name); N, L, b = _nodes(m)
    tc = N.new("ShaderNodeTexCoord")
    mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (scale, scale, scale)
    if coord == "World":
        g = N.new("ShaderNodeNewGeometry"); L.new(g.outputs["Position"], mp.inputs["Vector"])
    else:
        L.new(tc.outputs[coord], mp.inputs["Vector"])
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = noise_scale
    nz.inputs["Detail"].default_value = detail; nz.inputs["Distortion"].default_value = distortion
    L.new(mp.outputs["Vector"], nz.inputs["Vector"])
    fac = nz.outputs["Fac"]
    if random_mix:
        oi = N.new("ShaderNodeObjectInfo")
        mx = N.new("ShaderNodeMix"); mx.data_type = "FLOAT"; mx.inputs["Factor"].default_value = random_mix
        L.new(fac, mx.inputs[2]); L.new(oi.outputs["Random"], mx.inputs[3]); fac = mx.outputs[0]
    rp = N.new("ShaderNodeValToRGB"); e = rp.color_ramp.elements
    rp.color_ramp.interpolation = "EASE"
    e[0].position, e[0].color = stops[0][0], (*stops[0][1], 1)
    e[1].position, e[1].color = stops[-1][0], (*stops[-1][1], 1)
    for p, c in stops[1:-1]:
        el = e.new(p); el.color = (*c, 1)
    L.new(fac, rp.inputs["Fac"]); L.new(rp.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = rough; b.inputs["Specular IOR Level"].default_value = spec
    if bump:
        bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = bump
        L.new(nz.outputs["Fac"], bp.inputs["Height"]); L.new(bp.outputs["Normal"], b.inputs["Normal"])
    if haze:
        add_haze(m, haze)
    return m

def ground_mat():
    """Painted grass: large soft patches of sunny yellow-green and cooler deep green, dry pale field patches."""
    m = bpy.data.materials.new("Ground"); N, L, b = _nodes(m)
    g = N.new("ShaderNodeNewGeometry")
    def noise_at(scale, detail=1.5, dist=0.0, w=0.0):
        n = N.new("ShaderNodeTexNoise"); n.noise_dimensions = "4D"
        n.inputs["Scale"].default_value = scale; n.inputs["Detail"].default_value = detail
        n.inputs["Distortion"].default_value = dist; n.inputs["W"].default_value = w
        L.new(g.outputs["Position"], n.inputs["Vector"])
        return n.outputs["Fac"]
    big = noise_at(0.012, 2.0, 0.3, 1.0)
    mid = noise_at(0.06, 2.0, 0.0, 4.0)
    rp = N.new("ShaderNodeValToRGB"); rp.color_ramp.interpolation = "EASE"; e = rp.color_ramp.elements
    e[0].position, e[0].color = 0.36, (0.050, 0.150, 0.022, 1)
    e[1].position, e[1].color = 0.66, (0.36, 0.50, 0.075, 1)
    el = e.new(0.50); el.color = (0.13, 0.30, 0.035, 1)
    mix = N.new("ShaderNodeMix"); mix.data_type = "FLOAT"; mix.inputs["Factor"].default_value = 0.3
    L.new(big, mix.inputs[2]); L.new(mid, mix.inputs[3])
    L.new(mix.outputs[0], rp.inputs["Fac"])
    # dry, pale straw patches far away (fields)
    dry = noise_at(0.008, 1.0, 0.0, 7.0)
    dr = N.new("ShaderNodeMapRange"); dr.inputs["From Min"].default_value = 0.56; dr.inputs["From Max"].default_value = 0.62
    L.new(dry, dr.inputs["Value"])
    cam = N.new("ShaderNodeCameraData")
    far = N.new("ShaderNodeMapRange"); far.inputs["From Min"].default_value = 60; far.inputs["From Max"].default_value = 140
    L.new(cam.outputs["View Distance"], far.inputs["Value"])
    mul = N.new("ShaderNodeMath"); mul.operation = "MULTIPLY"
    L.new(dr.outputs["Result"], mul.inputs[0]); L.new(far.outputs["Result"], mul.inputs[1])
    mx2 = N.new("ShaderNodeMix"); mx2.data_type = "RGBA"
    L.new(mul.outputs[0], mx2.inputs["Factor"]); L.new(rp.outputs["Color"], mx2.inputs[6])
    mx2.inputs[7].default_value = (0.62, 0.60, 0.25, 1)
    L.new(mx2.outputs[2], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.9; b.inputs["Specular IOR Level"].default_value = 0.15
    add_haze(m, 1100.0, 0.95)
    return m

# ------------------------------------------------------------------ terrain mesh (polar grid around the camera)
def build_terrain(mat):
    angs = np.radians(np.linspace(-80, 80, 241))
    radii = [0.3]
    while radii[-1] < 2600:
        radii.append(radii[-1] * 1.028 + 0.02)
    radii = np.array(radii)
    R, Aa = np.meshgrid(radii, angs, indexing="ij")
    X = R * np.sin(Aa); Y = R * np.cos(Aa)
    Z = height(X, Y)
    bm = bmesh.new()
    nr, na = R.shape
    vs = [[bm.verts.new((X[i, j], Y[i, j], Z[i, j])) for j in range(na)] for i in range(nr)]
    for i in range(nr - 1):
        for j in range(na - 1):
            bm.faces.new((vs[i][j], vs[i][j + 1], vs[i + 1][j + 1], vs[i + 1][j]))
    return mesh_ob("Terrain", bm, [mat], smooth=True)

# ------------------------------------------------------------------ sky
def build_world():
    w = bpy.data.worlds.new("Sky"); bpy.context.scene.world = w
    w.use_nodes = True
    N, L = w.node_tree.nodes, w.node_tree.links
    bg = N["Background"]
    tc = N.new("ShaderNodeTexCoord")
    sep = N.new("ShaderNodeSeparateXYZ"); L.new(tc.outputs["Generated"], sep.inputs[0])
    # vertical gradient (the frame only covers ~0-12 degrees of elevation, so it is tight)
    grad = N.new("ShaderNodeValToRGB"); e = grad.color_ramp.elements; grad.color_ramp.interpolation = "EASE"
    e[0].position, e[0].color = 0.0, (0.56, 0.72, 0.92, 1)
    e[1].position, e[1].color = 0.30, (0.05, 0.20, 0.62, 1)
    el = e.new(0.09); el.color = (0.20, 0.42, 0.85, 1)
    L.new(sep.outputs["Z"], grad.inputs["Fac"])
    # sun glow
    dot = N.new("ShaderNodeVectorMath"); dot.operation = "DOT_PRODUCT"; dot.inputs[1].default_value = SUN_DIR
    L.new(tc.outputs["Generated"], dot.inputs[0])
    glow = N.new("ShaderNodeMapRange"); glow.inputs["From Min"].default_value = 0.72; glow.inputs["From Max"].default_value = 1.0
    glow.interpolation_type = "SMOOTHSTEP"
    L.new(dot.outputs["Value"], glow.inputs["Value"])
    gp = N.new("ShaderNodeMath"); gp.operation = "POWER"; gp.inputs[1].default_value = 1.6
    L.new(glow.outputs["Result"], gp.inputs[0])
    sky = N.new("ShaderNodeMix"); sky.data_type = "RGBA"
    L.new(gp.outputs[0], sky.inputs["Factor"]); L.new(grad.outputs["Color"], sky.inputs[6])
    sky.inputs[7].default_value = (1.0, 0.98, 0.92, 1)
    # painted clouds on a plane: uv = xy / z
    zc = N.new("ShaderNodeMath"); zc.operation = "MAXIMUM"; zc.inputs[1].default_value = 0.03
    L.new(sep.outputs["Z"], zc.inputs[0])
    dv = N.new("ShaderNodeVectorMath"); dv.operation = "DIVIDE"
    L.new(tc.outputs["Generated"], dv.inputs[0])
    cmb = N.new("ShaderNodeCombineXYZ"); L.new(zc.outputs[0], cmb.inputs[0]); L.new(zc.outputs[0], cmb.inputs[1]); L.new(zc.outputs[0], cmb.inputs[2])
    L.new(cmb.outputs[0], dv.inputs[1])
    mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1.0, 2.2, 0.0); mp.inputs["Location"].default_value = (0.3, 0.0, 0.0)
    L.new(dv.outputs[0], mp.inputs["Vector"])
    cn = N.new("ShaderNodeTexNoise"); cn.inputs["Scale"].default_value = 0.9; cn.inputs["Detail"].default_value = 4.0
    cn.inputs["Roughness"].default_value = 0.55; cn.inputs["Distortion"].default_value = 0.25
    L.new(mp.outputs["Vector"], cn.inputs["Vector"])
    cm = N.new("ShaderNodeMapRange"); cm.inputs["From Min"].default_value = 0.56; cm.inputs["From Max"].default_value = 0.66
    cm.interpolation_type = "SMOOTHSTEP"
    L.new(cn.outputs["Fac"], cm.inputs["Value"])
    # fewer clouds right at the wall line, more higher up
    el2 = N.new("ShaderNodeMapRange"); el2.inputs["From Min"].default_value = 0.035; el2.inputs["From Max"].default_value = 0.16
    L.new(sep.outputs["Z"], el2.inputs["Value"])
    cmask = N.new("ShaderNodeMath"); cmask.operation = "MULTIPLY"
    L.new(cm.outputs["Result"], cmask.inputs[0]); L.new(el2.outputs["Result"], cmask.inputs[1])
    # cloud shading: second sample shifted toward the sun = lit rims, grey-blue bellies
    mp2 = N.new("ShaderNodeMapping"); mp2.inputs["Scale"].default_value = (1.0, 2.2, 0.0); mp2.inputs["Location"].default_value = (0.28, -0.04, 0.0)
    L.new(dv.outputs[0], mp2.inputs["Vector"])
    cn2 = N.new("ShaderNodeTexNoise"); cn2.inputs["Scale"].default_value = 0.9; cn2.inputs["Detail"].default_value = 4.0
    cn2.inputs["Roughness"].default_value = 0.55; cn2.inputs["Distortion"].default_value = 0.25
    L.new(mp2.outputs["Vector"], cn2.inputs["Vector"])
    shd = N.new("ShaderNodeMath"); shd.operation = "SUBTRACT"
    L.new(cn.outputs["Fac"], shd.inputs[0]); L.new(cn2.outputs["Fac"], shd.inputs[1])
    shr = N.new("ShaderNodeMapRange"); shr.inputs["From Min"].default_value = -0.03; shr.inputs["From Max"].default_value = 0.05
    L.new(shd.outputs[0], shr.inputs["Value"])
    ccol = N.new("ShaderNodeMix"); ccol.data_type = "RGBA"
    L.new(shr.outputs["Result"], ccol.inputs["Factor"])
    ccol.inputs[6].default_value = (0.62, 0.70, 0.86, 1); ccol.inputs[7].default_value = (1.0, 1.0, 1.0, 1)
    fin = N.new("ShaderNodeMix"); fin.data_type = "RGBA"
    L.new(cmask.outputs[0], fin.inputs["Factor"]); L.new(sky.outputs[2], fin.inputs[6]); L.new(ccol.outputs[2], fin.inputs[7])
    L.new(fin.outputs[2], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = 1.0
    return w

# ------------------------------------------------------------------ wall
WALL_P0 = Vector((-178.0, 418.0)); WALL_P1 = Vector((150.0, 296.0))
WALL_BASE = -8.0
WALL_H = WALL_BASE + 50.0          # absolute elevation of the wall top (50 m above the valley floor)

def wall_point(t):
    return WALL_P0.lerp(WALL_P1, t)

def build_wall():
    stone = ramp_mat("WallStone", [(0.3, (0.40, 0.42, 0.45)), (0.7, (0.56, 0.58, 0.60))], coord="Object",
                     noise_scale=0.08, detail=3.0, rough=0.92, bump=0.15)
    stone.node_tree.nodes["Mapping"].inputs["Scale"].default_value = (1.0, 1.0, 0.25)   # vertical streaks
    add_haze(stone, 1200.0, 0.95)
    joint = flat("WallJoint", (0.05, 0.055, 0.07), 0.9); add_haze(joint, 1200.0, 0.85)
    d = (WALL_P1 - WALL_P0); length = d.length; d.normalize()
    ang = math.atan2(d.y, d.x)
    nrm = Vector((d.y, -d.x))           # toward the camera side
    bm = bmesh.new()
    def box(c, size, mi):
        r = bmesh.ops.create_cube(bm, size=1)
        M = Matrix.Translation(c) @ Matrix.Rotation(ang, 4, "Z") @ Matrix.Diagonal((*size, 1))
        bmesh.ops.transform(bm, matrix=M, verts=r["verts"])
        for f in {f for v in r["verts"] for f in v.link_faces}:
            f.material_index = mi
    SL, PIER, SLOT = 13.5, 2.0, 0.45       # module, projecting pier, dark slot each side of the pier
    t = -260.0
    z0 = WALL_BASE - 20.0
    while t < length + 260:
        p = WALL_P0 + d * t
        top = WALL_H + rnd.choice((0.0, 0.0, 0.0, 0.4, -0.3))
        box(Vector((p.x, p.y, (top + z0) / 2)), (SL - PIER - 2 * SLOT, 7.0, top - z0), 0)               # panel
        q = p + d * (SL / 2)
        qq = q + nrm * 0.9
        box(Vector((qq.x, qq.y, (WALL_H + 0.8 + z0) / 2)), (PIER, 8.8, WALL_H + 0.8 - z0), 0)            # pier, proud of the face
        t += SL
    # dark core behind the panels shows through the slots; plain capping course on top
    c = WALL_P0 + d * (length / 2) - nrm * 2.0
    box(Vector((c.x, c.y, (WALL_H - 0.5 + z0) / 2)), (length + 520, 5.0, WALL_H - 0.5 - z0), 1)
    c2 = WALL_P0 + d * (length / 2) + nrm * 0.3
    box(Vector((c2.x, c2.y, WALL_H + 0.35)), (length + 520, 7.8, 0.7), 0)
    ob = mesh_ob("WallMaria", bm, [stone, joint])
    # watch tower on top, near the frame centre
    tp = WALL_P0 + d * (length * 0.575)
    tb = bmesh.new()
    def tbox(c, size):
        r = bmesh.ops.create_cube(tb, size=1)
        M = Matrix.Translation(c) @ Matrix.Rotation(ang, 4, "Z") @ Matrix.Diagonal((*size, 1))
        bmesh.ops.transform(tb, matrix=M, verts=r["verts"])
    tbox(Vector((tp.x, tp.y, WALL_H + 5.0)), (6.5, 6.5, 10.0))
    tbox(Vector((tp.x, tp.y, WALL_H + 10.4)), (7.4, 7.4, 0.9))
    for k in (-1, 1):                                    # parapet blocks
        o = Vector((d.x, d.y, 0)) * k * 2.6
        tbox(Vector((tp.x, tp.y, WALL_H + 11.6)) + o, (2.0, 7.4, 1.6))
    mesh_ob("WallTower", tb, [stone])
    # dark slit windows on the tower
    wb = bmesh.new()
    for k in (-1.4, 1.4):
        r = bmesh.ops.create_cube(wb, size=1)
        o = Vector((d.x, d.y, 0)) * k + Vector((nrm.x, nrm.y, 0)) * 3.3
        M = Matrix.Translation(Vector((tp.x, tp.y, WALL_H + 6.5)) + o) @ Matrix.Rotation(ang, 4, "Z") @ Matrix.Diagonal((0.9, 0.3, 2.2, 1))
        bmesh.ops.transform(wb, matrix=M, verts=r["verts"])
    mesh_ob("WallTowerWin", wb, [joint])
    return ob, ang, nrm

# ------------------------------------------------------------------ mountains
def build_mountains():
    angs = np.radians(np.linspace(-45, 45, 260))
    radii = np.linspace(900, 9000, 140)
    R, Aa = np.meshgrid(radii, angs, indexing="ij")
    X = R * np.sin(Aa); Y = R * np.cos(Aa)
    def g(cx, cy, h, r):
        return h * np.exp(-((X - cx) ** 2 + (Y - cy) ** 2) / (r * r))
    Z = (g(40, 2300, 250, 280) + g(-150, 2500, 140, 260) + g(650, 4300, 560, 800) + g(1500, 5000, 900, 1000)
         + g(2600, 5600, 1100, 1500))
    rid = np.abs(np.sin(X / 260.0 + np.cos(Y / 410.0) * 2.0) * np.cos(Y / 330.0 - X / 900.0))
    Z = Z * (0.88 + 0.22 * rid) - 10
    bm = bmesh.new()
    nr, na = R.shape
    vs = [[bm.verts.new((X[i, j], Y[i, j], Z[i, j])) for j in range(na)] for i in range(nr)]
    for i in range(nr - 1):
        for j in range(na - 1):
            bm.faces.new((vs[i][j], vs[i][j + 1], vs[i + 1][j + 1], vs[i + 1][j]))
    m = ramp_mat("Mountain", [(0.35, (0.05, 0.18, 0.05)), (0.65, (0.16, 0.34, 0.10))], coord="World",
                 noise_scale=0.004, detail=3.0, rough=0.9)
    add_haze(m, 5200.0, 0.9, color=(0.42, 0.60, 0.92))
    return mesh_ob("Mountains", bm, [m], smooth=True)

# ------------------------------------------------------------------ valley props
def spindle(bm, base, h, r, seg=10, rings=12, wob=0.12, seed=0, mi=0):
    """Cypress / poplar shape: pointed spindle with lumpy foliage."""
    prev = None
    rr = random.Random(seed)
    ph = rr.uniform(0, 6)
    for i in range(rings + 1):
        t = i / rings
        rad = r * (math.sin(math.pi * min(1, t * 1.05)) ** 0.75) * (1.0 - 0.35 * t) + 0.02
        ring = []
        for k in range(seg):
            a = k / seg * 2 * math.pi
            w = 1 + wob * math.sin(a * 3 + ph + i * 1.7) * math.sin(i * 2.3 + ph)
            ring.append(bm.verts.new(base + Vector((math.cos(a) * rad * w, math.sin(a) * rad * w, t * h))))
        if prev:
            for k in range(seg):
                f = bm.faces.new((prev[k], prev[(k + 1) % seg], ring[(k + 1) % seg], ring[k])); f.material_index = mi
        prev = ring
    tip = bm.verts.new(base + Vector((0, 0, h * 1.03)))
    for k in range(seg):
        f = bm.faces.new((prev[k], prev[(k + 1) % seg], tip)); f.material_index = mi

def blob_cluster(bm, center, n, rad, spread, seed, squash=0.8, mi=0):
    rr = random.Random(seed)
    for k in range(n):
        off = Vector((rr.uniform(-1, 1) * spread[0], rr.uniform(-1, 1) * spread[1], rr.uniform(0, 1) * spread[2]))
        r = rad * rr.uniform(0.6, 1.1)
        ico = bmesh.ops.create_icosphere(bm, subdivisions=2, radius=r)
        for v in ico["verts"]:
            nn = noise.noise(v.co * 1.3 + Vector((seed, k, 0)))
            v.co = center + off + Vector((v.co.x, v.co.y, v.co.z * squash)) * (1 + 0.18 * nn)
        for f in {f for v in ico["verts"] for f in v.link_faces}:
            f.material_index = mi

def build_valley():
    foliage = ramp_mat("FarFoliage", [(0.3, (0.012, 0.045, 0.02)), (0.7, (0.05, 0.12, 0.035))], coord="World",
                       noise_scale=0.6, detail=2.0, rough=0.85, bump=0.4)
    add_haze(foliage, 900.0, 0.9)
    cyp = ramp_mat("Cypress", [(0.3, (0.008, 0.035, 0.022)), (0.7, (0.04, 0.10, 0.04))], coord="World",
                   noise_scale=0.9, detail=2.0, rough=0.85, bump=0.5)
    add_haze(cyp, 900.0, 0.9)
    # cypress row on the right
    bm = bmesh.new()
    rr = random.Random(5)
    for k in range(26):
        x = 24 + k * 3.4 + rr.uniform(-1, 1); y = 150 + k * 2.4 + rr.uniform(-8, 8)
        h = rr.uniform(9, 15); z = hz(x, y) - 0.5
        spindle(bm, Vector((x, y, z)), h, rr.uniform(1.1, 1.6), seed=k)
    for k in range(10):                                   # second, farther rank
        x = 35 + k * 6 + rr.uniform(-2, 2); y = 205 + k * 3 + rr.uniform(-6, 6)
        spindle(bm, Vector((x, y, hz(x, y) - 0.5)), rr.uniform(10, 16), 1.5, seed=100 + k)
    mesh_ob("Cypresses", bm, [cyp], smooth=True)
    # dark broad-leaved clump mid-valley, and woods at the wall foot on the right
    bm = bmesh.new()
    blob_cluster(bm, Vector((14, 125, hz(14, 125) - 1.0)), 16, 4.2, (8, 5, 6), 3)
    blob_cluster(bm, Vector((26, 118, hz(26, 118) - 1.0)), 8, 3.5, (5, 4, 4), 4)
    for k in range(18):
        x = 60 + k * 9; y = 300 - k * 3.8
        blob_cluster(bm, Vector((x, y, hz(x, y) - 1)), 4, 5.5, (5, 3, 6), 50 + k)
    for k in range(8):                                    # a few hedges/trees left of centre valley
        x = -40 + k * 7; y = 290 + k * 2
        blob_cluster(bm, Vector((x, y, hz(x, y) - 1)), 3, 3.5, (4, 3, 3), 80 + k)
    mesh_ob("ValleyWoods", bm, [foliage], smooth=True)
    # farmhouses + windmills
    wallm = flat("HouseWall", (0.62, 0.55, 0.45), 0.9); add_haze(wallm, 900.0)
    roof = flat("HouseRoof", (0.42, 0.075, 0.035), 0.8); add_haze(roof, 900.0)
    sail = flat("MillSail", (0.75, 0.72, 0.66), 0.9); add_haze(sail, 900.0)
    bm = bmesh.new()
    def house(x, y, rot, w=7, dpt=4.5, hgt=3.2):
        z = hz(x, y) - 0.3
        R = Matrix.Rotation(rot, 4, "Z")
        r = bmesh.ops.create_cube(bm, size=1)
        bmesh.ops.transform(bm, matrix=Matrix.Translation((x, y, z + hgt / 2)) @ R @ Matrix.Diagonal((w, dpt, hgt, 1)), verts=r["verts"])
        # gable roof prism
        v = [Vector(p) for p in ((-w / 2 - .3, -dpt / 2 - .4, hgt), (w / 2 + .3, -dpt / 2 - .4, hgt), (w / 2 + .3, dpt / 2 + .4, hgt),
                                  (-w / 2 - .3, dpt / 2 + .4, hgt), (-w / 2 - .3, 0, hgt + 2.4), (w / 2 + .3, 0, hgt + 2.4))]
        M = Matrix.Translation((x, y, z)) @ R
        vv = [bm.verts.new(M @ p) for p in v]
        for f in ((0, 1, 5, 4), (2, 3, 4, 5), (0, 4, 3), (1, 2, 5), (0, 3, 2, 1)):
            ff = bm.faces.new([vv[i] for i in f]); ff.material_index = 1
    for (x, y, r) in ((-23, 345, 0.3), (-15, 350, -0.2), (-30, 352, 0.1), (32, 300, 0.4), (45, 296, -0.3), (40, 310, 0.1),
                      (58, 288, 0.5), (20, 315, 0.2), (68, 276, 0.2)):
        house(x, y, r)
    def mill(x, y, rot, s=1.0):
        z = hz(x, y) - 0.3
        prev = None
        for i in range(7):
            t = i / 6; rad = (3.0 - 1.0 * t) * s
            ring = [bm.verts.new((x + math.cos(a) * rad, y + math.sin(a) * rad, z + t * 11 * s)) for a in np.linspace(0, 2 * math.pi, 9)[:-1]]
            if prev:
                for k in range(8):
                    bm.faces.new((prev[k], prev[(k + 1) % 8], ring[(k + 1) % 8], ring[k]))
            prev = ring
        tip = bm.verts.new((x, y, z + 14.5 * s))
        for k in range(8):
            f = bm.faces.new((prev[k], prev[(k + 1) % 8], tip)); f.material_index = 1
        hub = Vector((x, y, z + 11.5 * s)) + Matrix.Rotation(rot, 3, "Z") @ Vector((0, -2.6 * s, 0))
        for k in range(4):
            a = k * math.pi / 2 + 0.5
            r = bmesh.ops.create_cube(bm, size=1)
            M = Matrix.Translation(hub) @ Matrix.Rotation(rot, 4, "Z") @ Matrix.Rotation(a, 4, "Y") @ Matrix.Translation((0, 0, 5.2 * s)) @ Matrix.Diagonal((1.4 * s, 0.15, 9.5 * s, 1))
            bmesh.ops.transform(bm, matrix=M, verts=r["verts"])
            for f in {f for v in r["verts"] for f in v.link_faces}:
                f.material_index = 2
    mill(22, 305, 0.2, 0.6)
    mill(45, 288, -0.3, 0.62)
    return mesh_ob("Farms", bm, [wallm, roof, sail], smooth=False)

# ------------------------------------------------------------------ the tree
def bark_mat():
    m = ramp_mat("Bark", [(0.3, (0.035, 0.028, 0.02)), (0.55, (0.10, 0.085, 0.06)), (0.75, (0.20, 0.17, 0.12))],
                 coord="Object", noise_scale=3.0, detail=6.0, rough=0.95, bump=0.5)
    m.node_tree.nodes["Mapping"].inputs["Scale"].default_value = (3.0, 3.0, 0.5)
    return m

def tube(bm, pts, radii, seg=14, wob=0.0, seed=0, mi=0):
    rr = random.Random(seed)
    prev = None
    n = len(pts)
    for i, (p, r) in enumerate(zip(pts, radii)):
        tng = (pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)]).normalized()
        q = tng.to_track_quat("Z", "Y").to_matrix()
        ring = []
        for k in range(seg):
            a = k / seg * 2 * math.pi
            w = 1 + wob * (math.sin(a * 4 + seed) * 0.6 + math.sin(a * 7 + i * 0.7 + seed) * 0.4)
            ring.append(bm.verts.new(p + q @ Vector((math.cos(a) * r * w, math.sin(a) * r * w, 0))))
        if prev:
            for k in range(seg):
                f = bm.faces.new((prev[k], prev[(k + 1) % seg], ring[(k + 1) % seg], ring[k])); f.material_index = mi
        prev = ring
    tip = bm.verts.new(pts[-1] + (pts[-1] - pts[-2]).normalized() * radii[-1])
    for k in range(seg):
        bm.faces.new((prev[k], prev[(k + 1) % seg], tip)).material_index = mi

def bez(a, b, c, n=8):
    return [a * (1 - t) ** 2 + b * 2 * t * (1 - t) + c * t * t for t in np.linspace(0, 1, n)]

def leaf_cluster_mesh(name, mat, seed):
    """A sprig of 6-7 pointed oval leaves (real geometry, no alpha)."""
    rr = random.Random(seed)
    bm = bmesh.new()
    for k in range(7):
        L = rr.uniform(0.16, 0.24); W = L * 0.42
        yaw = k / 7 * 2 * math.pi + rr.uniform(-0.3, 0.3); pitch = rr.uniform(0.15, 0.6)
        M = Matrix.Rotation(yaw, 4, "Z") @ Matrix.Rotation(-pitch, 4, "X") @ Matrix.Translation((0, 0.05, 0))
        prof = [(0, 0), (W * 0.5, L * 0.15), (W * 0.62, L * 0.4), (W * 0.5, L * 0.68), (W * 0.22, L * 0.9), (0, L)]
        left = [bm.verts.new(M @ Vector((x, y, 0.15 * x / W * W))) for x, y in prof[1:-1]]
        right = [bm.verts.new(M @ Vector((-x, y, 0.15 * x / W * W))) for x, y in prof[1:-1]]
        base = bm.verts.new(M @ Vector((0, 0, -0.01))); tip = bm.verts.new(M @ Vector((0, L, 0.02)))
        mid = [bm.verts.new(M @ Vector((0, y, -0.015))) for _, y in prof[1:-1]]
        bm.faces.new((base, left[0], mid[0])); bm.faces.new((base, mid[0], right[0]))
        for i in range(len(mid) - 1):
            bm.faces.new((mid[i], left[i], left[i + 1], mid[i + 1])); bm.faces.new((mid[i], mid[i + 1], right[i + 1], right[i]))
        bm.faces.new((mid[-1], left[-1], tip)); bm.faces.new((mid[-1], tip, right[-1]))
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(mat)
    for p in me.polygons:
        p.use_smooth = True
    return bpy.data.objects.new(name, me)

def scatter_object(name, pts, rots, scales, picks, proto_coll, coll=None):
    """Instance children of proto_coll on points with per-point rotation (euler), scale and variant index (GN)."""
    me = bpy.data.meshes.new(name + "_pts")
    me.vertices.add(len(pts)); me.vertices.foreach_set("co", np.asarray(pts, np.float32).ravel())
    for an, data, typ in (("rot", rots, "FLOAT_VECTOR"), ("scl", scales, "FLOAT"), ("pick", picks, "INT")):
        at = me.attributes.new(an, typ, "POINT")
        key = "vector" if typ == "FLOAT_VECTOR" else "value"
        at.data.foreach_set(key, np.asarray(data, np.int32 if typ == "INT" else np.float32).ravel())
    ob = bpy.data.objects.new(name, me); link(ob, coll)
    ng = bpy.data.node_groups.new(name + "_GN", "GeometryNodeTree")
    ng.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    N, L = ng.nodes, ng.links
    gi = N.new("NodeGroupInput"); go = N.new("NodeGroupOutput")
    m2p = N.new("GeometryNodeMeshToPoints"); L.new(gi.outputs[0], m2p.inputs["Mesh"])
    ci = N.new("GeometryNodeCollectionInfo"); ci.inputs["Collection"].default_value = proto_coll
    ci.inputs["Separate Children"].default_value = True; ci.inputs["Reset Children"].default_value = True
    ci.transform_space = "ORIGINAL"
    iop = N.new("GeometryNodeInstanceOnPoints")
    L.new(m2p.outputs[0], iop.inputs["Points"]); L.new(ci.outputs[0], iop.inputs["Instance"])
    iop.inputs["Pick Instance"].default_value = True
    def attr(nm, dt):
        a = N.new("GeometryNodeInputNamedAttribute"); a.data_type = dt; a.inputs["Name"].default_value = nm
        return a.outputs["Attribute"]
    e2r = N.new("FunctionNodeEulerToRotation"); L.new(attr("rot", "FLOAT_VECTOR"), e2r.inputs[0])
    L.new(e2r.outputs[0], iop.inputs["Rotation"])
    L.new(attr("scl", "FLOAT"), iop.inputs["Scale"])
    L.new(attr("pick", "INT"), iop.inputs["Instance Index"])
    L.new(iop.outputs[0], go.inputs[0])
    md = ob.modifiers.new("scatter", "NODES"); md.node_group = ng
    return ob

def build_tree(protos):
    base = Vector((TREE.x, TREE.y, hz(TREE.x, TREE.y) - 0.15))
    bark = bark_mat()
    bm = bmesh.new()
    # trunk: leans to the right, flared roots, forks at ~3.4 m
    tpts = bez(Vector((0, 0, -0.6)), Vector((0.1, 0.05, 1.6)), Vector((0.65, 0.2, 3.3)), 10)
    trad = [1.05, 0.78, 0.64, 0.6, 0.58, 0.56, 0.54, 0.53, 0.52, 0.5]
    tube(bm, tpts, trad, seg=18, wob=0.12, seed=1)
    for k, (dx, dy) in enumerate(((-1.0, 0.1), (0.3, -0.9), (0.8, 0.5), (-0.4, 0.9), (0.9, -0.3))):   # root flares
        a = Vector((0, 0, 0.6)); c = Vector((dx * 1.5, dy * 1.5, -0.25))
        tube(bm, bez(a, (a + c) / 2 + Vector((0, 0, 0.1)), c, 5), [0.42, 0.33, 0.24, 0.16, 0.1], seg=8, seed=k + 3)
    fork = tpts[-1]
    limbs = []
    rr = random.Random(4)
    for (dx, dy, dz, r0) in ((-3.8, -0.4, 2.2, 0.36), (-1.5, 1.2, 3.8, 0.34), (1.7, -0.5, 3.8, 0.34),
                             (3.6, -0.6, 1.6, 0.30), (0.3, -2.0, 2.6, 0.28), (-0.8, 2.2, 2.0, 0.26)):
        end = fork + Vector((dx, dy, dz))
        mid = fork + Vector((dx * 0.45, dy * 0.45, dz * 0.75))
        tube(bm, bez(fork - Vector((0, 0, 0.4)), mid, end, 7), list(np.linspace(r0, 0.08, 7)), seg=10, wob=0.06, seed=rr.randint(0, 99))
        limbs.append((fork, mid, end))
    trunk = mesh_ob("Tree_trunk", bm, [bark], smooth=True)
    trunk.location = base
    # crown: lumpy clumps on an envelope (wide, leaning right, drooping at the edges)
    ctr = Vector((0.75, 0.3, 5.1))
    clumps = []
    for (f, m, e) in limbs:
        clumps.append((e + Vector((0, 0, 0.5)), 1.8))
    k = 0
    while len(clumps) < 44:
        u = Vector((rr.uniform(-1, 1), rr.uniform(-1, 1), rr.uniform(-1, 1)))
        if u.length > 1:
            continue
        p = ctr + Vector((u.x * 4.4, u.y * 4.0, u.z * 2.6))
        if p.z < 3.9 - 0.15 * abs(p.x):              # keep the underside open around the trunk
            p.z = 3.9 - 0.15 * abs(p.x) + rr.uniform(0, 0.4)
        r = rr.uniform(1.2, 1.9) * (1.15 - 0.3 * u.length)
        clumps.append((p, r))
    # drooping outer skirts (left and right-front)
    for p in ((-4.6, -0.6, 2.6), (-3.8, -2.0, 2.3), (-2.2, -3.0, 3.0), (3.9, -1.0, 2.2), (3.0, -2.4, 2.0), (1.0, -3.2, 2.8), (4.6, 0.6, 2.8)):
        clumps.append((Vector(p), 1.25))
    inner = flat("CrownInner", (0.012, 0.04, 0.012), 0.9)
    cb = bmesh.new()
    pts, nrms = [], []
    for (c, r) in clumps:
        ico = bmesh.ops.create_icosphere(cb, subdivisions=3, radius=r)
        for v in ico["verts"]:
            nn = noise.noise(v.co * 0.9 + c)
            v.co = c + Vector((v.co.x, v.co.y, v.co.z * 0.78)) * (1 + 0.16 * nn)
    crown_core = mesh_ob("Tree_crown_core", cb, [inner], smooth=True)
    crown_core.location = base
    # leaves: sample points on each clump surface, keep the ones not buried inside other clumps
    cen = np.array([c for c, r in clumps]); rad = np.array([r for c, r in clumps])
    for (c, r) in clumps:
        n = int(4 * math.pi * r * r * 34)
        dirs = np_rng.normal(size=(n, 3)); dirs /= np.linalg.norm(dirs, axis=1)[:, None]
        p = np.array(c) + dirs * r * np.array([1, 1, 0.78]) * np_rng.uniform(0.92, 1.08, (n, 1))
        dd = np.linalg.norm(p[:, None, :] - cen[None, :, :] * np.array([1, 1, 1]), axis=2) / rad[None, :]
        buried = (dd < 0.86).sum(axis=1) > 0
        keep = ~buried
        pts.append(p[keep]); nrms.append(dirs[keep])
    pts = np.concatenate(pts); nrms = np.concatenate(nrms)
    # orientation: leaf sprig 'up' (+Z of proto) along the outward normal, random spin
    rots = []
    for nv in nrms:
        q = Vector(nv).to_track_quat("Z", "Y")
        e = (q @ Matrix.Rotation(rnd.uniform(0, 6.28), 3, "Z").to_quaternion()).to_euler()
        rots.append((e.x, e.y, e.z))
    pts = pts + np.array(base)
    sc = np_rng.uniform(1.6, 2.4, len(pts))
    pick = np_rng.integers(0, len(protos["leaf"].objects), len(pts))
    scatter_object("Tree_leaves", pts, rots, sc, pick, protos["leaf"])
    print("leaf sprigs", len(pts))
    return trunk, base

def leaf_mat():
    m = bpy.data.materials.new("Leaf"); N, L, b = _nodes(m)
    oi = N.new("ShaderNodeObjectInfo")
    rp = N.new("ShaderNodeValToRGB"); e = rp.color_ramp.elements
    e[0].color = (0.05, 0.16, 0.025, 1); e[1].color = (0.30, 0.50, 0.06, 1)
    el = e.new(0.5); el.color = (0.13, 0.33, 0.035, 1)
    L.new(oi.outputs["Random"], rp.inputs["Fac"]); L.new(rp.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.6; b.inputs["Specular IOR Level"].default_value = 0.35
    b.inputs["Subsurface Weight"].default_value = 0.0
    tr = N.new("ShaderNodeBsdfTranslucent"); tr.inputs["Color"].default_value = (0.25, 0.45, 0.04, 1)
    mx = N.new("ShaderNodeMixShader"); mx.inputs[0].default_value = 0.18
    out = N["Material Output"]
    L.new(b.outputs[0], mx.inputs[1]); L.new(tr.outputs[0], mx.inputs[2]); L.new(mx.outputs[0], out.inputs["Surface"])
    return m

# ------------------------------------------------------------------ grass blades
def blade_mesh(name, mat, h, bend, seed, n_blades=5, spread=0.06):
    rr = random.Random(seed)
    bm = bmesh.new()
    uv_l = bm.loops.layers.uv.new("UVMap")
    for b in range(n_blades):
        a = rr.uniform(0, 2 * math.pi); off = Vector((math.cos(a), math.sin(a), 0)) * rr.uniform(0, spread)
        hh = h * rr.uniform(0.6, 1.1); w = 0.012 * rr.uniform(0.8, 1.4) * (h / 0.35) ** 0.5
        lean = Vector((math.cos(a + rr.uniform(-0.5, 0.5)), math.sin(a + rr.uniform(-0.5, 0.5)), 0)) * bend * rr.uniform(0.4, 1.2)
        side = Vector((-math.sin(a), math.cos(a), 0))
        segs = 5; prev = None
        for i in range(segs + 1):
            t = i / segs
            c = off + Vector((0, 0, hh * t)) + lean * hh * t * t
            ww = w * (1 - t) ** 0.8 + 0.0008
            l = bm.verts.new(c - side * ww); r = bm.verts.new(c + side * ww)
            if prev:
                f = bm.faces.new((prev[0], prev[1], r, l))
                for lp, uvv in zip(f.loops, ((0, (i - 1) / segs), (1, (i - 1) / segs), (1, t), (0, t))):
                    lp[uv_l].uv = uvv
            prev = (l, r)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(mat)
    for p in me.polygons:
        p.use_smooth = True
    return bpy.data.objects.new(name, me)

def grass_mat():
    """Blade colour: dark root to sunny tip, tinted by the same world-space patch noise as the ground."""
    m = bpy.data.materials.new("GrassBlade"); N, L, b = _nodes(m)
    uv = N.new("ShaderNodeUVMap"); sep = N.new("ShaderNodeSeparateXYZ"); L.new(uv.outputs[0], sep.inputs[0])
    g = N.new("ShaderNodeNewGeometry")
    nz = N.new("ShaderNodeTexNoise"); nz.noise_dimensions = "4D"; nz.inputs["W"].default_value = 1.0
    nz.inputs["Scale"].default_value = 0.012; nz.inputs["Detail"].default_value = 2.0; nz.inputs["Distortion"].default_value = 0.3
    L.new(g.outputs["Position"], nz.inputs["Vector"])
    oi = N.new("ShaderNodeObjectInfo")
    mxf = N.new("ShaderNodeMix"); mxf.data_type = "FLOAT"; mxf.inputs["Factor"].default_value = 0.25
    L.new(nz.outputs["Fac"], mxf.inputs[2]); L.new(oi.outputs["Random"], mxf.inputs[3])
    rp = N.new("ShaderNodeValToRGB"); rp.color_ramp.interpolation = "EASE"; e = rp.color_ramp.elements
    e[0].position, e[0].color = 0.36, (0.06, 0.17, 0.025, 1)
    e[1].position, e[1].color = 0.66, (0.40, 0.55, 0.08, 1)
    el = e.new(0.5); el.color = (0.15, 0.33, 0.04, 1)
    L.new(mxf.outputs[0], rp.inputs["Fac"])
    root = N.new("ShaderNodeMix"); root.data_type = "RGBA"
    tipc = N.new("ShaderNodeMapRange"); tipc.inputs["From Min"].default_value = 0.0; tipc.inputs["From Max"].default_value = 0.7
    L.new(sep.outputs["Y"], tipc.inputs["Value"])
    L.new(tipc.outputs["Result"], root.inputs["Factor"])
    root.inputs[6].default_value = (0.02, 0.06, 0.012, 1); L.new(rp.outputs["Color"], root.inputs[7])
    L.new(root.outputs[2], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.55; b.inputs["Specular IOR Level"].default_value = 0.3
    tr = N.new("ShaderNodeBsdfTranslucent"); L.new(root.outputs[2], tr.inputs["Color"])
    mx = N.new("ShaderNodeMixShader"); mx.inputs[0].default_value = 0.2
    out = N["Material Output"]
    L.new(b.outputs[0], mx.inputs[1]); L.new(tr.outputs[0], mx.inputs[2]); L.new(mx.outputs[0], out.inputs["Surface"])
    add_haze(m, 1100.0, 0.95)
    return m

def in_frustum(x, y, z, margin=0.12):
    half = 18.0 / LENS
    ok = (y > 0.2) & (np.abs(x) < y * (half + margin))
    vz = (z - CAM_Z) / np.maximum(y, 0.2)
    ok &= vz < (half * 9 / 16 + margin)
    return ok

def scatter_grass(protos, avoid):
    """Blades on the terrain, density falling off with distance so screen density stays roughly even."""
    pts = []
    for (d0, d1, n) in ((1.0, 6.0, 26000), (6.0, 18.0, 70000), (18.0, 45.0, 90000), (45.0, 90.0, 45000)):
        # sample uniformly in the frustum wedge area
        u = np_rng.uniform(0, 1, n)
        r = np.sqrt(d0 * d0 + u * (d1 * d1 - d0 * d0))
        a = np_rng.uniform(-0.48, 0.48, n)
        x = r * np.sin(a); y = r * np.cos(a)
        pts.append((x, y, r))
    x = np.concatenate([p[0] for p in pts]); y = np.concatenate([p[1] for p in pts]); r = np.concatenate([p[2] for p in pts])
    z = height(x, y)
    keep = in_frustum(x, y, z)
    for (ax, ay, ar) in avoid:
        keep &= (x - ax) ** 2 + (y - ay) ** 2 > ar * ar
    x, y, z, r = x[keep], y[keep], z[keep], r[keep]
    n = len(x)
    scl = np.clip(0.75 + r / 28.0, 0.8, 3.6) * np_rng.uniform(0.75, 1.25, n)
    rots = np.stack([np_rng.normal(0, 0.12, n), np_rng.normal(0, 0.12, n), np_rng.uniform(0, 6.28, n)], 1)
    pick = np_rng.integers(0, len(protos["grass"].objects), n)
    print("grass tufts", n)
    return scatter_object("Grass", np.stack([x, y, z - 0.02], 1), rots, scl, pick, protos["grass"])

# ------------------------------------------------------------------ flowers
def flower_mats():
    pet = bpy.data.materials.new("BellPetal"); N, L, b = _nodes(pet)
    uv = N.new("ShaderNodeUVMap"); sep = N.new("ShaderNodeSeparateXYZ"); L.new(uv.outputs[0], sep.inputs[0])
    oi = N.new("ShaderNodeObjectInfo")
    # U = radial (0 centre .. 1 tip), V = 0 on the petal mid-vein .. 1 at the notch
    vein = N.new("ShaderNodeMapRange"); vein.inputs["From Min"].default_value = 0.0; vein.inputs["From Max"].default_value = 0.12
    L.new(sep.outputs["Y"], vein.inputs["Value"])
    base_ramp = N.new("ShaderNodeValToRGB"); e = base_ramp.color_ramp.elements
    e[0].position, e[0].color = 0.0, (0.60, 0.62, 0.95, 1)        # pale centre
    e[1].position, e[1].color = 1.0, (0.20, 0.22, 0.85, 1)
    el = e.new(0.32); el.color = (0.26, 0.26, 0.88, 1)
    L.new(sep.outputs["X"], base_ramp.inputs["Fac"])
    var = N.new("ShaderNodeValToRGB"); e = var.color_ramp.elements       # per-flower tint: blue .. violet .. deep purple
    e[0].color = (0.75, 0.85, 1.0, 1); e[1].color = (0.62, 0.35, 0.85, 1)
    el = e.new(0.55); el.color = (1.0, 0.95, 1.0, 1)
    L.new(oi.outputs["Random"], var.inputs["Fac"])
    tint = N.new("ShaderNodeMix"); tint.data_type = "RGBA"; tint.blend_type = "MULTIPLY"; tint.inputs["Factor"].default_value = 1.0
    L.new(base_ramp.outputs["Color"], tint.inputs[6]); L.new(var.outputs["Color"], tint.inputs[7])
    vc = N.new("ShaderNodeMix"); vc.data_type = "RGBA"
    L.new(vein.outputs["Result"], vc.inputs["Factor"])
    vc.inputs[6].default_value = (0.07, 0.05, 0.45, 1); L.new(tint.outputs[2], vc.inputs[7])
    L.new(vc.outputs[2], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.45; b.inputs["Specular IOR Level"].default_value = 0.4
    b.inputs["Sheen Weight"].default_value = 0.3
    tr = N.new("ShaderNodeBsdfTranslucent"); L.new(vc.outputs[2], tr.inputs["Color"])
    mx = N.new("ShaderNodeMixShader"); mx.inputs[0].default_value = 0.25
    out = N["Material Output"]
    L.new(b.outputs[0], mx.inputs[1]); L.new(tr.outputs[0], mx.inputs[2]); L.new(mx.outputs[0], out.inputs["Surface"])
    stem = flat("Stem", (0.07, 0.20, 0.03), 0.6, sss=0.0)
    leafm = ramp_mat("FlowerLeaf", [(0.3, (0.04, 0.13, 0.02)), (0.7, (0.12, 0.30, 0.04))], coord="Object",
                     noise_scale=4.0, rough=0.55, random_mix=0.6)
    centre = flat("BellCentre", (0.85, 0.85, 0.7), 0.5)
    bud = flat("BellBud", (0.38, 0.40, 0.90), 0.45)
    yel = flat("YellowPetal", (0.95, 0.65, 0.03), 0.5)
    yc = flat("YellowCentre", (0.55, 0.30, 0.01), 0.6)
    pink = flat("PinkPetal", (0.75, 0.10, 0.30), 0.5)
    white = flat("WhitePetal", (0.92, 0.92, 0.88), 0.5)
    return dict(pet=pet, stem=stem, leaf=leafm, centre=centre, bud=bud, yel=yel, yc=yc, pink=pink, white=white)

def star_corolla(bm, M, size, depth, uv_l, mi_pet, mi_c, petals=5, rings=7, seg_per=12, notch=0.42):
    """Balloon-flower bloom: five broad pointed petals fused into a shallow star-shaped cup. Faces +Z."""
    nseg = petals * seg_per
    centre = bm.verts.new(M @ Vector((0, 0, 0)))
    prev = None
    for i in range(1, rings + 1):
        rho = i / rings
        ring = []
        for k in range(nseg):
            th = k / nseg * 2 * math.pi
            ph = (th * petals / (2 * math.pi)) % 1.0
            t = abs(ph - 0.5) * 2               # 1 at petal centre... (0 at the notch)
            t = 1 - t                           # 0 at petal centre, 1 at notch
            shape = math.cos(t * math.pi / 2) ** 0.7
            tipc = max(0.0, 1 - t * 5) * 0.12   # pointed tip
            R = (notch + (1 - notch) * shape + tipc) * size
            # cup: rises toward the rim, petal tips flare outward and the mid-vein is a slight crease
            z = depth * size * (rho ** 1.5) - 0.25 * size * max(0.0, rho - 0.75) ** 2 * (1 - t)
            z -= 0.04 * size * rho * (1 - min(1, t * 4))
            v = bm.verts.new(M @ Vector((math.cos(th) * R * rho, math.sin(th) * R * rho, z)))
            ring.append((v, rho, t))
        if prev is None:
            for k in range(nseg):
                f = bm.faces.new((centre, ring[k][0], ring[(k + 1) % nseg][0])); f.material_index = mi_pet
                for lp in f.loops:
                    lp[uv_l].uv = (0.0, 0.5) if lp.vert is centre else next((r, t) for vv, r, t in ring if vv is lp.vert)
        else:
            for k in range(nseg):
                f = bm.faces.new((prev[k][0], prev[(k + 1) % nseg][0], ring[(k + 1) % nseg][0], ring[k][0])); f.material_index = mi_pet
                lk = {prev[k][0]: prev[k], prev[(k + 1) % nseg][0]: prev[(k + 1) % nseg], ring[(k + 1) % nseg][0]: ring[(k + 1) % nseg], ring[k][0]: ring[k]}
                for lp in f.loops:
                    _, r, t = lk[lp.vert]; lp[uv_l].uv = (r, t)
        prev = ring
    # stamens / style: a small pale column with 5 lobes
    col = bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=0.09 * size, radius2=0.05 * size, depth=0.35 * size)
    bmesh.ops.transform(bm, matrix=M @ Matrix.Translation((0, 0, 0.17 * size)), verts=col["verts"])
    for f in {f for v in col["verts"] for f in v.link_faces}:
        f.material_index = mi_c
    for k in range(5):
        a = k / 5 * 2 * math.pi
        lo = bmesh.ops.create_icosphere(bm, subdivisions=1, radius=0.045 * size)
        bmesh.ops.transform(bm, matrix=M @ Matrix.Translation((math.cos(a) * 0.06 * size, math.sin(a) * 0.06 * size, 0.36 * size)), verts=lo["verts"])
        for f in {f for v in lo["verts"] for f in v.link_faces}:
            f.material_index = mi_c

def leaf_blade(bm, M, L, W, mi, serr=True):
    """Ovate-lanceolate leaf along +Y with a folded midrib."""
    n = 8
    prev = None
    for i in range(n + 1):
        t = i / n
        w = W * math.sin(math.pi * t ** 0.8) * (1.0 + (0.08 * (i % 2) if serr else 0))
        y = L * t
        droop = -0.25 * L * t * t
        l = bm.verts.new(M @ Vector((-w, y, droop + 0.25 * w))); c = bm.verts.new(M @ Vector((0, y, droop))); r = bm.verts.new(M @ Vector((w, y, droop + 0.25 * w)))
        if prev:
            bm.faces.new((prev[0], prev[1], c, l)).material_index = mi
            bm.faces.new((prev[1], prev[2], r, c)).material_index = mi
        prev = (l, c, r)

def stem_curve(bm, pts, r, mi):
    tube(bm, pts, [r] * len(pts), seg=6, mi=mi)

def bellflower_plant(name, mats, seed, blooms=2, buds=1, height=0.45):
    """A Platycodon stem: open star blooms facing roughly forward (-Y, toward the camera), buds, alternate leaves."""
    rr = random.Random(seed)
    bm = bmesh.new(); uv_l = bm.loops.layers.uv.new("UVMap")
    MI = dict(pet=0, stem=1, leaf=2, centre=3, bud=4)
    top = Vector((rr.uniform(-0.05, 0.05), rr.uniform(-0.04, 0.02), height))
    sp = bez(Vector((0, 0, 0)), Vector((0, 0.02, height * 0.5)), top, 8)
    stem_curve(bm, sp, 0.004, MI["stem"])
    for k in range(rr.randint(4, 7)):                     # alternate leaves on the lower 2/3
        t = rr.uniform(0.1, 0.7); p = sp[int(t * 7)]
        a = k * 2.4 + rr.uniform(-0.4, 0.4)
        M = Matrix.Translation(p) @ Matrix.Rotation(a, 4, "Z") @ Matrix.Rotation(-0.9, 4, "X")
        leaf_blade(bm, M, rr.uniform(0.05, 0.08), rr.uniform(0.012, 0.02), MI["leaf"])
    heads = []
    for b in range(blooms + buds):
        if b == 0:
            hp = top
        else:
            p0 = sp[rr.randint(4, 6)]
            hp = p0 + Vector((rr.uniform(-0.09, 0.09), rr.uniform(-0.05, 0.04), rr.uniform(0.02, 0.10)))
            stem_curve(bm, bez(p0, (p0 + hp) / 2 + Vector((0, 0, 0.02)), hp, 4), 0.003, MI["stem"])
        heads.append((hp, b < blooms))
    for hp, is_bloom in heads:
        if is_bloom:
            # face toward the camera (-Y) and up, with variation
            pitch = rr.uniform(0.55, 1.15); yaw = rr.uniform(-0.6, 0.6)
            M = Matrix.Translation(hp) @ Matrix.Rotation(yaw, 4, "Z") @ Matrix.Rotation(pitch, 4, "X") @ Matrix.Rotation(rr.uniform(0, 1.26), 4, "Z")
            size = rr.uniform(0.022, 0.03)
            star_corolla(bm, M, size, 0.55, uv_l, MI["pet"], MI["centre"])
            for k in range(5):                            # green sepals
                a = (k + 0.5) / 5 * 2 * math.pi
                Ms = M @ Matrix.Rotation(a, 4, "Z") @ Matrix.Rotation(-2.2, 4, "X")
                leaf_blade(bm, Ms, size * 0.45, size * 0.08, MI["leaf"], serr=False)
        else:
            s = rr.uniform(0.010, 0.016)                  # balloon bud: inflated pentagonal ball
            ico = bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=8, radius=s)
            for v in ico["verts"]:
                a = math.atan2(v.co.y, v.co.x)
                v.co.x *= 1 + 0.12 * math.cos(5 * a); v.co.y *= 1 + 0.12 * math.cos(5 * a); v.co.z *= 1.25
            bmesh.ops.transform(bm, matrix=Matrix.Translation(hp + Vector((0, 0, s))), verts=ico["verts"])
            for f in {f for v in ico["verts"] for f in v.link_faces}:
                f.material_index = MI["bud"]; f.smooth = True
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for k in ("pet", "stem", "leaf", "centre", "bud"):
        me.materials.append(mats[k])
    for p in me.polygons:
        p.use_smooth = True
    return bpy.data.objects.new(name, me)

def small_flower_plant(name, mats, seed, petal="yel", centre="yc", n_heads=3, height=0.3, size=0.014, petals=5):
    rr = random.Random(seed)
    bm = bmesh.new(); uv_l = bm.loops.layers.uv.new("UVMap")
    for h in range(n_heads):
        top = Vector((rr.uniform(-0.06, 0.06), rr.uniform(-0.06, 0.06), height * rr.uniform(0.7, 1.0)))
        stem_curve(bm, bez(Vector((0, 0, 0)), Vector((top.x * 0.3, top.y * 0.3, top.z * 0.5)), top, 5), 0.0025, 1)
        M = Matrix.Translation(top) @ Matrix.Rotation(rr.uniform(0.3, 0.9), 4, "X") @ Matrix.Rotation(rr.uniform(-0.5, 0.5), 4, "Y")
        for k in range(petals):                          # separate rounded petals
            a = k / petals * 2 * math.pi
            Mp = M @ Matrix.Rotation(a, 4, "Z") @ Matrix.Rotation(-0.25, 4, "X")
            leaf_blade(bm, Mp, size, size * 0.42, 0, serr=False)
        c = bmesh.ops.create_icosphere(bm, subdivisions=1, radius=size * 0.28)
        bmesh.ops.transform(bm, matrix=M @ Matrix.Diagonal((1, 1, 0.6, 1)), verts=c["verts"])
        for f in {f for v in c["verts"] for f in v.link_faces}:
            f.material_index = 2
    for k in range(4):
        a = rr.uniform(0, 6.28)
        leaf_blade(bm, Matrix.Rotation(a, 4, "Z") @ Matrix.Rotation(-1.1, 4, "X"), rr.uniform(0.06, 0.1), 0.012, 3)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for k in (petal, "stem", centre, "leaf"):
        me.materials.append(mats[k])
    for p in me.polygons:
        p.use_smooth = True
    return bpy.data.objects.new(name, me)

def scatter_flowers(protos):
    """Dense bellflower bed close to the camera, yellow flowers mixed in, wildflower dots on the slopes."""
    # bed: 0.7 - 7 m, denser near the bottom of frame
    n = 2600
    u = np_rng.uniform(0, 1, n)
    r = 0.7 + 6.5 * u ** 1.25
    a = np_rng.uniform(-0.5, 0.5, n)
    x = r * np.sin(a); y = r * np.cos(a); z = height(x, y)
    keep = in_frustum(x, y, z + 0.4, 0.05)
    x, y, z, r = x[keep], y[keep], z[keep], r[keep]
    nb = len(protos["bell"].objects); ny = len(protos["small"].objects)
    is_yellow = np_rng.uniform(0, 1, len(x)) < 0.16
    pick = np.where(is_yellow, nb + np_rng.integers(0, ny, len(x)), np_rng.integers(0, nb, len(x)))
    scl = np_rng.uniform(0.8, 1.25, len(x)) * (1.0 + 0.05 * r)
    rots = np.stack([np_rng.normal(0, 0.08, len(x)), np_rng.normal(0, 0.08, len(x)),
                     np.arctan2(x, y) * 0.8 + np_rng.normal(0, 0.35, len(x))], 1)   # turn blooms toward the camera
    pts = np.stack([x, y, z - 0.01], 1)
    print("bed plants", len(x))
    scatter_object("FlowerBed", pts, rots, scl, pick, protos["bed"])
    # wildflower dots on the slopes (white and yellow), in patches
    n = 30000
    u = np_rng.uniform(0, 1, n); r = np.sqrt(64 + u * (110 ** 2 - 64)); a = np_rng.uniform(-0.45, 0.45, n)
    x = r * np.sin(a); y = r * np.cos(a); z = height(x, y)
    patch = (np.sin(x / 3.1 + np.cos(y / 4.3) * 2) * np.cos(y / 2.7 - x / 5.0)) > 0.35
    keep = in_frustum(x, y, z) & patch
    x, y, z, r = x[keep], y[keep], z[keep], r[keep]
    pick = np_rng.integers(0, len(protos["dots"].objects), len(x))
    scl = np.clip(0.7 + r / 25, 1, 4.5)
    rots = np.stack([np.zeros(len(x)), np.zeros(len(x)), np_rng.uniform(0, 6.28, len(x))], 1)
    print("wildflower dots", len(x))
    scatter_object("Wildflowers", np.stack([x, y, z], 1), rots, scl, pick, protos["dots"])

def build_protos():
    protos = {}
    fm = flower_mats()
    protos["mats"] = fm
    bed = new_coll("P_bed", hide=True)
    bell = []
    for k in range(7):
        o = bellflower_plant(f"Bell_{k}", fm, seed=k * 7 + 1, blooms=random.Random(k).choice((1, 1, 2, 2, 3)),
                             buds=random.Random(k + 9).choice((0, 1, 1, 2)), height=random.Random(k + 3).uniform(0.32, 0.5))
        bed.objects.link(o); bell.append(o)
    small = []
    for k in range(3):
        o = small_flower_plant(f"Yellow_{k}", fm, seed=100 + k, n_heads=random.Random(k).randint(2, 4), height=0.3, size=0.016)
        bed.objects.link(o); small.append(o)
    protos["bed"] = bed
    protos["bell"] = type("C", (), {"objects": bell})
    protos["small"] = type("C", (), {"objects": small})
    dots = new_coll("P_dots", hide=True)
    for k in range(4):
        col = ("white", "white", "yel", "white")[k]
        o = small_flower_plant(f"Dot_{k}", fm, seed=200 + k, petal=col, centre="yc", n_heads=4, height=0.12, size=0.03)
        dots.objects.link(o)
    protos["dots"] = dots
    grass = new_coll("P_grass", hide=True)
    gm = grass_mat()
    for k in range(6):
        o = blade_mesh(f"Blade_{k}", gm, h=(0.22, 0.3, 0.38, 0.26, 0.45, 0.33)[k], bend=0.25, seed=k, n_blades=7)
        grass.objects.link(o)
    protos["grass"] = grass
    leaf = new_coll("P_leaf", hide=True)
    lm = leaf_mat()
    for k in range(4):
        leaf.objects.link(leaf_cluster_mesh(f"Sprig_{k}", lm, seed=k))
    protos["leaf"] = leaf
    return protos

# ------------------------------------------------------------------ rock + foreground grass tufts
def build_rock():
    path = os.path.join(ASSETS, "boulder_01", "boulder_01_1k.blend")
    x, y = 0.9, 10.5
    if os.path.exists(path):
        with bpy.data.libraries.load(path) as (src, dst):
            dst.objects = [n for n in src.objects]
        obs = [o for o in dst.objects if o and o.type == "MESH"]
        for o in obs:
            link(o)
            dim = max(o.dimensions.x, o.dimensions.y)
            s = 1.7 / dim
            o.scale = (s, s * 0.8, s * 0.55)
            o.rotation_euler.z = 0.4
            o.location = (x, y, hz(x, y) - 0.15)
            for sl in o.material_slots:                    # cool, desaturate a touch for the painted look
                m = sl.material
                if m and m.use_nodes:
                    b = m.node_tree.nodes.get("Principled BSDF")
                    if b and b.inputs["Base Color"].links:
                        src_s = b.inputs["Base Color"].links[0].from_socket
                        hsv = m.node_tree.nodes.new("ShaderNodeHueSaturation")
                        hsv.inputs["Saturation"].default_value = 0.6; hsv.inputs["Value"].default_value = 0.85
                        m.node_tree.links.new(src_s, hsv.inputs["Color"]); m.node_tree.links.new(hsv.outputs[0], b.inputs["Base Color"])
        return obs
    bm = bmesh.new(); ico = bmesh.ops.create_icosphere(bm, subdivisions=3, radius=0.8)
    for v in ico["verts"]:
        v.co = Vector((v.co.x * 1.1, v.co.y * 0.8, v.co.z * 0.5)) * (1 + 0.2 * noise.noise(v.co * 2))
    o = mesh_ob("Rock", bm, [flat("RockMat", (0.25, 0.25, 0.25), 0.8)], smooth=True)
    o.location = (x, y, hz(x, y) - 0.1)
    return [o]

# ------------------------------------------------------------------ light, camera, render
def build_lights():
    sun = bpy.data.lights.new("Sun", "SUN"); sun.energy = 4.2; sun.angle = math.radians(2.0)
    sun.color = (1.0, 0.95, 0.86)
    o = bpy.data.objects.new("Sun", sun); link(o)
    o.rotation_euler = SUN_DIR.to_track_quat("Z", "Y").to_euler()

def build_camera():
    cd = bpy.data.cameras.new("Cam"); cd.lens = LENS; cd.sensor_width = 36.0; cd.sensor_fit = "HORIZONTAL"
    cd.clip_start = 0.1; cd.clip_end = 20000
    cd.shift_y = 0.0
    cam = bpy.data.objects.new("Cam", cd); link(cam)
    cam.location = (0, 0, CAM_Z)
    cam.rotation_euler = (math.radians(90.0), 0, 0)
    bpy.context.scene.camera = cam
    return cam

def render_setup():
    sc = bpy.context.scene
    w, h = map(int, A.res.split("x"))
    sc.render.resolution_x, sc.render.resolution_y = w, h; sc.render.resolution_percentage = 100
    if A.engine.upper().startswith("EEVEE"):
        sc.render.engine = "BLENDER_EEVEE"
        sc.eevee.taa_render_samples = max(16, A.samples)
    else:
        sc.render.engine = "CYCLES"
        sc.cycles.device = "CPU"; sc.cycles.samples = A.samples
        sc.cycles.use_denoising = True; sc.cycles.denoiser = "OPENIMAGEDENOISE"
        sc.cycles.max_bounces = 4; sc.cycles.diffuse_bounces = 2; sc.cycles.glossy_bounces = 1
        sc.cycles.transmission_bounces = 2; sc.cycles.transparent_max_bounces = 6
        sc.cycles.use_adaptive_sampling = True
        sc.render.threads_mode = "FIXED"; sc.render.threads = 4
    sc.view_settings.view_transform = "AgX"
    try:
        sc.view_settings.look = "AgX - Punchy"
    except Exception:
        pass
    sc.view_settings.exposure = 0.0
    sc.render.image_settings.file_format = "PNG"
    sc.frame_set(A.frame)

def compositor():
    sc = bpy.context.scene
    ng = bpy.data.node_groups.new("OpeningComp", "CompositorNodeTree")
    ng.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")
    N, L = ng.nodes, ng.links
    rl = N.new("CompositorNodeRLayers")
    rays = N.new("CompositorNodeGlare")
    rays.inputs["Type"].default_value = "Sun Beams"
    rays.inputs["Sun Position"].default_value = (1.02, 1.08)
    rays.inputs["Threshold"].default_value = 0.85; rays.inputs["Strength"].default_value = 0.35
    rays.inputs["Size"].default_value = 0.6
    L.new(rl.outputs["Image"], rays.inputs["Image"])
    bloom = N.new("CompositorNodeGlare")
    bloom.inputs["Type"].default_value = "Bloom"
    bloom.inputs["Threshold"].default_value = 0.9; bloom.inputs["Strength"].default_value = 0.25; bloom.inputs["Size"].default_value = 0.5
    L.new(rays.outputs["Image"], bloom.inputs["Image"])
    out = N.new("NodeGroupOutput")
    L.new(bloom.outputs["Image"], out.inputs[0])
    sc.compositing_node_group = ng

# ------------------------------------------------------------------ characters
def build_characters(trunk, base):
    sys.path.insert(0, HERE)
    import characters as C
    facing = 0.75
    eren, mik, f1, f2 = C.place_opening(base, 0.6, facing, trunk=trunk, start=A.frame - 60)
    # place_opening assumes flat ground at the trunk base; drop them onto the slope
    bpy.context.view_layer.update()
    def ground_drop(ob):
        return hz(ob.location.x, ob.location.y) - base.z
    mik.location.z += ground_drop(mik)
    f1.location.z += ground_drop(f1)
    if eren.animation_data and eren.animation_data.action:
        act = eren.animation_data.action
        try:
            curves = [fc for fc in act.fcurves]
        except AttributeError:
            curves = [fc for lay in act.layers for st in lay.strips for cb in st.channelbags for fc in cb.fcurves]
        xs = [fc for fc in curves if fc.data_path == "location"]
        ex = next(fc for fc in xs if fc.array_index == 0); ey = next(fc for fc in xs if fc.array_index == 1)
        dz = hz(ex.evaluate(A.frame), ey.evaluate(A.frame)) - base.z
        for fc in xs:
            if fc.array_index == 2:
                for kp in fc.keyframe_points:
                    kp.co.y += dz; kp.handle_left.y += dz; kp.handle_right.y += dz
    return eren, mik

# ------------------------------------------------------------------ line art (optional)
def lineart():
    gp = bpy.data.grease_pencils.new("LineArt") if hasattr(bpy.data, "grease_pencils") else None
    try:
        bpy.ops.object.grease_pencil_add(type="LINEART_SCENE")
        ob = bpy.context.active_object
        md = ob.modifiers[0] if ob.modifiers else None
        if md:
            md.thickness = 1
    except Exception as ex:
        print("line art failed", ex)

# ------------------------------------------------------------------ main
def main():
    reset()
    build_world()
    build_camera()
    build_lights()
    gm = ground_mat()
    build_terrain(gm)
    build_wall()
    build_mountains()
    build_valley()
    build_rock()
    if A.clay:
        trunk = mesh_ob("Tree_proxy", bmesh.new(), [])
        bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=12, radius1=0.7, radius2=0.5, depth=4)
        base = Vector((TREE.x, TREE.y, hz(TREE.x, TREE.y)))
        o = mesh_ob("TrunkProxy", bm, [flat("bk", (0.1, 0.08, 0.05))]); o.location = base + Vector((0, 0, 2))
        bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=3, radius=1)
        c = mesh_ob("CrownProxy", bm, [flat("lf", (0.1, 0.3, 0.05))]); c.location = base + Vector((0.75, 0.3, 5.1)); c.scale = (4.9, 4.4, 3.2)
        for (dx, dy, hh) in ((1.4, -1.5, 0.75), (2.8, -1.4, 1.33)):    # kid proxies
            bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
            k = mesh_ob("KidProxy", bm, [flat("kd", (0.05, 0.05, 0.05))])
            k.location = (base.x + dx, base.y + dy, hz(base.x + dx, base.y + dy) + hh / 2); k.scale = (0.35, 0.3, hh)
    else:
        protos = build_protos()
        trunk, base = build_tree(protos)
        if not A.no_chars:
            build_characters(trunk, base)
        scatter_grass(protos, avoid=[(0.9, 10.5, 0.9), (TREE.x, TREE.y, 1.0)])
        scatter_flowers(protos)
    if A.lineart:
        lineart()
    render_setup()
    if A.comp:
        compositor()
    if A.save:
        bpy.ops.wm.save_as_mainfile(filepath=A.save)
    if A.out:
        bpy.context.scene.render.filepath = A.out
        bpy.ops.render.render(write_still=True)

if __name__ == "__main__":
    main()
