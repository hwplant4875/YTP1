"""Shiganshina District (Attack on Titan) procedural scene for the 3D timelapse.

Run:  blender -b -P scene.py -- --year 845 --out still.png [--res 1280x720] [--samples 48] [--cam overview]
Units are metres. Wall Maria runs along the x axis at y = 0; Shiganshina is the
U-shaped district protruding south (y < 0): straight sides x = +-W from y = 0 to
y = -S, closed by a half circle of radius W around (0, -S). Inside Wall Maria is y > 0.
A canal runs along the east side of the district (x = CX) through water gates in both walls.
"""
import bpy, bmesh, math, random, sys, argparse, os
from mathutils import Vector, Euler, Quaternion, noise

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ap = argparse.ArgumentParser()
ap.add_argument("--year", type=float, default=845)
ap.add_argument("--out", default="")
ap.add_argument("--res", default="1280x720")
ap.add_argument("--samples", type=int, default=48)
ap.add_argument("--cam", default="overview")
ap.add_argument("--engine", default="CYCLES")
ap.add_argument("--device", default="GPU")
ap.add_argument("--save", default="")
ap.add_argument("--labels", default="")
ap.add_argument("--event", default="")
A, _extra = ap.parse_known_args(argv)

# ---------------------------------------------------------------- plug-in modules
# Each module in PLUGINS (same folder) may define:
#   REPLACES = {"hill", "kids", "titans", ...}  built-in features it supersedes
#   height_patch(x, y, h) -> h                    terrain edit applied inside height()
#   build(M, year, ctx)                           adds objects after the base scene is built
#   CAMS = {name: (loc, look_at, lens)} or {name: callable() -> (loc, look_at, lens)}
#   LABELS = {name: (x, y, z)}                    extra HUD label anchors
PLUGINS, REPLACED = [], set()       # filled by load_plugins() once all helpers below exist

W = 290.0          # district half width
S = 430.0          # length of the straight sides
R = W              # radius of the far end
WALL_H = 50.0      # all three walls are 50 m
WALL_T = 10.0      # wall thickness at the base
TOP_T = WALL_T - 2.4
GATE_W, GATE_H = 14.0, 20.0
CX = 228.0         # canal centre line (east side, as in the reference still)
CS = 1 if CX > 0 else -1
CANAL_W = 24.0
GF = Vector((-2600.0, 3300.0))    # Forest of Giant Trees (between Wall Maria and Wall Rose)
OUTER_GATE = (0.0, -S - R)
random.seed(7)

# ---------------------------------------------------------------- helpers
def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def mat(name, color, rough=0.8, bump=0.0, scale=1.0, var=0.0, var_scale=0.02, color2=None, sss=0.0):
    """Principled material with optional noise colour variation and bump."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    bsdf.inputs["Roughness"].default_value = rough
    if sss > 0:
        bsdf.inputs["Subsurface Weight"].default_value = sss
        bsdf.inputs["Subsurface Radius"].default_value = (0.9, 0.35, 0.2)
        bsdf.inputs["Subsurface Scale"].default_value = 0.05
    c1 = (*color, 1)
    if var > 0:
        tc = nt.nodes.new("ShaderNodeTexCoord")
        nz = nt.nodes.new("ShaderNodeTexNoise")
        nz.inputs["Scale"].default_value = var_scale
        nz.inputs["Detail"].default_value = 6
        nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
        ramp = nt.nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].position = 0.5 - var
        ramp.color_ramp.elements[1].position = 0.5 + var
        ramp.color_ramp.elements[0].color = c1
        ramp.color_ramp.elements[1].color = (*(color2 or [min(1, x * 1.25) for x in color]), 1)
        nt.links.new(nz.outputs["Fac"], ramp.inputs["Fac"])
        nt.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
        if bump > 0:
            b = nt.nodes.new("ShaderNodeBump")
            b.inputs["Strength"].default_value = bump
            nz2 = nt.nodes.new("ShaderNodeTexNoise")
            nz2.inputs["Scale"].default_value = scale
            nt.links.new(tc.outputs["Object"], nz2.inputs["Vector"])
            nt.links.new(nz2.outputs["Fac"], b.inputs["Height"])
            nt.links.new(b.outputs["Normal"], bsdf.inputs["Normal"])
    else:
        bsdf.inputs["Base Color"].default_value = c1
    return m

def wall_mat():
    """Pale stone with large weathered stains and faint horizontal courses, like the painted anime walls."""
    m = bpy.data.materials.new("WallStone"); m.use_nodes = True
    nt = m.node_tree; N = nt.nodes; L = nt.links
    bsdf = N["Principled BSDF"]; bsdf.inputs["Roughness"].default_value = 0.9
    tc = N.new("ShaderNodeTexCoord")
    st = N.new("ShaderNodeTexNoise"); st.inputs["Scale"].default_value = 0.035; st.inputs["Detail"].default_value = 8
    st.inputs["Roughness"].default_value = 0.65
    L.new(tc.outputs["Object"], st.inputs["Vector"])
    r = N.new("ShaderNodeValToRGB"); e = r.color_ramp.elements
    e[0].position, e[0].color = 0.38, (0.30, 0.29, 0.26, 1)
    e[1].position, e[1].color = 0.62, (0.62, 0.60, 0.53, 1)
    L.new(st.outputs["Fac"], r.inputs["Fac"])
    # vertical streaks: noise stretched along z
    sv = N.new("ShaderNodeVectorMath"); sv.operation = "MULTIPLY"; sv.inputs[1].default_value = (0.6, 0.6, 0.05)
    L.new(tc.outputs["Object"], sv.inputs[0])
    sn = N.new("ShaderNodeTexNoise"); sn.inputs["Scale"].default_value = 0.4; sn.inputs["Detail"].default_value = 3
    L.new(sv.outputs[0], sn.inputs["Vector"])
    mx = N.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.blend_type = "MULTIPLY"; mx.inputs["Factor"].default_value = 0.35
    L.new(r.outputs["Color"], mx.inputs["A"]); L.new(sn.outputs["Color"], mx.inputs["B"])
    L.new(mx.outputs["Result"], bsdf.inputs["Base Color"])
    # courses of masonry blocks for close-ups
    br = N.new("ShaderNodeTexBrick"); br.inputs["Scale"].default_value = 0.25
    br.inputs["Mortar Size"].default_value = 0.01; br.inputs["Row Height"].default_value = 0.5
    L.new(tc.outputs["Object"], br.inputs["Vector"])
    bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.25
    L.new(br.outputs["Fac"], bp.inputs["Height"]); L.new(bp.outputs["Normal"], bsdf.inputs["Normal"])
    return m

def obj_from_bm(name, bm, mats=(), coll=None):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for m in mats:
        me.materials.append(m)
    ob = bpy.data.objects.new(name, me)
    (coll or bpy.context.scene.collection).objects.link(ob)
    return ob

def new_coll(name, parent=None, hide=False):
    c = bpy.data.collections.new(name)
    (parent or bpy.context.scene.collection).children.link(c)
    if hide:
        bpy.context.view_layer.layer_collection.children[name].exclude = True
    return c

def box(bm, center, size, rot=0.0, mi=0, taper=None):
    """Axis box (local x along rot) into bm. taper=(sx_top, sy_top) scales the top face."""
    r = bmesh.ops.create_cube(bm, size=1)
    q = Euler((0, 0, rot)).to_matrix()
    for v in r["verts"]:
        x, y, z = v.co
        if taper and z > 0:
            x *= taper[0]; y *= taper[1]
        v.co = q @ Vector((x * size[0], y * size[1], z * size[2])) + Vector(center)
    for f in {f for v in r["verts"] for f in v.link_faces}:
        f.material_index = mi

def cyl(bm, p0, p1, r0, r1=None, seg=8, mi=0):
    """Tapered cylinder from p0 to p1."""
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    r = bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r0, radius2=r1 if r1 is not None else r0, depth=d.length)
    q = d.to_track_quat("Z", "Y").to_matrix()
    for v in r["verts"]:
        v.co = q @ v.co + (p0 + p1) / 2
    for f in {f for v in r["verts"] for f in v.link_faces}:
        f.material_index = mi

def resample(pts, step):
    out = [Vector(pts[0])]
    for k in range(len(pts) - 1):
        a, b = Vector(pts[k]), Vector(pts[k + 1])
        n = max(1, int((b - a).length / step))
        for t in range(1, n + 1):
            out.append(a + (b - a) * t / n)
    return [(p.x, p.y) for p in out]

# ---------------------------------------------------------------- district shape
def district_outline(step=6.0):
    pts = [(-W, 0.0), (-W, -S)]
    n = int(math.pi * R / step)
    for s in range(1, n):
        a = math.pi + s / n * math.pi
        pts.append((math.cos(a) * R, -S + math.sin(a) * R))
    pts += [(W, -S), (W, 0.0)]
    return resample(pts, step)

def in_district(x, y, margin):
    if y > -margin or abs(x) > W - margin:
        return False
    if y < -S and math.hypot(x, y + S) > R - margin:
        return False
    return True

def district_ymin(x, margin=0.0):
    r = R - margin
    return -S - math.sqrt(max(0.0, r * r - x * x))

CANAL_FAR = (CX, district_ymin(CX))

# ---------------------------------------------------------------- terrain
HILL = Vector((330.0, 820.0))     # Eren's tree hill (inside Wall Maria, north of the inner gate)

def height(x, y):
    d = math.hypot(x, y + S * 0.5)
    flat = min(1.0, max(0.0, (d - 1100) / 1600))          # town area flat
    h = noise.noise(Vector((x / 1400, y / 1400, 0.3))) * 38 + noise.noise(Vector((x / 380, y / 380, 1.7))) * 6
    h = h * flat
    far = min(1.0, max(0.0, (d - 3600) / 3000))
    h += far * (noise.noise(Vector((x / 2200, y / 2200, 9.1))) * 0.5 + 0.5) ** 2 * 900
    if "hill" not in REPLACED:
        hd = math.hypot(x - HILL.x, y - HILL.y)
        h += 26 * math.exp(-(hd / 150) ** 2)              # the tree hill
    # canal bed
    if abs(x - CX) < CANAL_W / 2 + 4 and y > -1600 and y < 2600:
        h = min(h, h - 3.0 * max(0.0, 1 - abs(x - CX) / (CANAL_W / 2 + 4)))
    for p in PLUGINS:
        if hasattr(p, "height_patch"):
            h = p.height_patch(x, y, h)
    return h

def build_terrain(mats):
    bm = bmesh.new()
    Sz, N = 9000.0, 320
    def coord(i):
        t = i / N * 2 - 1
        return math.copysign(abs(t) ** 1.6, t) * Sz
    verts = [[bm.verts.new((coord(i), coord(j), 0)) for j in range(N + 1)] for i in range(N + 1)]
    for row in verts:
        for v in row:
            v.co.z = height(v.co.x, v.co.y)
    for i in range(N):
        for j in range(N):
            bm.faces.new((verts[i][j], verts[i + 1][j], verts[i + 1][j + 1], verts[i][j + 1]))
    for f in bm.faces:
        f.smooth = True
    return obj_from_bm("Terrain", bm, [terrain_mat()])

def cheb(node):
    keys = node.bl_rna.properties["distance"].enum_items.keys()
    return "CHEBYCHEV" if "CHEBYCHEV" in keys else "CHEBYSHEV"

def terrain_mat():
    m = bpy.data.materials.new("Terrain"); m.use_nodes = True
    nt = m.node_tree; N = nt.nodes; L = nt.links
    bsdf = N["Principled BSDF"]; bsdf.inputs["Roughness"].default_value = 0.95
    tc = N.new("ShaderNodeTexCoord")
    # meadow: soft yellow-green with large painterly patches, like the anime backgrounds
    n1 = N.new("ShaderNodeTexNoise"); n1.inputs["Scale"].default_value = 0.0012; n1.inputs["Detail"].default_value = 8
    L.new(tc.outputs["Object"], n1.inputs["Vector"])
    r1 = N.new("ShaderNodeValToRGB"); e = r1.color_ramp.elements
    e[0].position, e[0].color = 0.32, (0.13, 0.22, 0.04, 1)
    e[1].position, e[1].color = 0.70, (0.38, 0.44, 0.13, 1)
    mid = r1.color_ramp.elements.new(0.52); mid.color = (0.23, 0.33, 0.07, 1)
    L.new(n1.outputs["Fac"], r1.inputs["Fac"])
    n2 = N.new("ShaderNodeTexNoise"); n2.inputs["Scale"].default_value = 0.05; n2.inputs["Detail"].default_value = 4
    L.new(tc.outputs["Object"], n2.inputs["Vector"])
    g = N.new("ShaderNodeMix"); g.data_type = "RGBA"; g.blend_type = "OVERLAY"; g.inputs["Factor"].default_value = 0.25
    L.new(r1.outputs["Color"], g.inputs["A"]); L.new(n2.outputs["Color"], g.inputs["B"])
    # farm fields far inside Wall Maria
    stretch = N.new("ShaderNodeVectorMath"); stretch.operation = "MULTIPLY"; stretch.inputs[1].default_value = (1.0, 2.6, 1.0)
    L.new(tc.outputs["Object"], stretch.inputs[0])
    vo = N.new("ShaderNodeTexVoronoi"); vo.distance = cheb(vo); vo.inputs["Scale"].default_value = 1 / 140
    vo.inputs["Randomness"].default_value = 0.85
    L.new(stretch.outputs[0], vo.inputs["Vector"])
    sep = N.new("ShaderNodeSeparateColor"); L.new(vo.outputs["Color"], sep.inputs["Color"])
    pal = N.new("ShaderNodeValToRGB"); pal.color_ramp.interpolation = "CONSTANT"; pe = pal.color_ramp.elements
    cols = [(0.0, (0.55, 0.42, 0.12)), (0.16, (0.22, 0.36, 0.06)), (0.33, (0.36, 0.25, 0.12)), (0.5, (0.12, 0.25, 0.04)),
            (0.66, (0.62, 0.52, 0.20)), (0.82, (0.30, 0.42, 0.10))]
    pe[0].position, pe[0].color = cols[0][0], (*cols[0][1], 1)
    pe[1].position, pe[1].color = cols[1][0], (*cols[1][1], 1)
    for p, c in cols[2:]:
        x = pal.color_ramp.elements.new(p); x.color = (*c, 1)
    L.new(sep.outputs["Red"], pal.inputs["Fac"])
    vo2 = N.new("ShaderNodeTexVoronoi"); vo2.feature = "DISTANCE_TO_EDGE"; vo2.distance = cheb(vo2)
    vo2.inputs["Scale"].default_value = 1 / 140; vo2.inputs["Randomness"].default_value = 0.85
    L.new(stretch.outputs[0], vo2.inputs["Vector"])
    hedge = N.new("ShaderNodeMapRange"); hedge.inputs["From Min"].default_value = 0.002; hedge.inputs["From Max"].default_value = 0.008
    L.new(vo2.outputs["Distance"], hedge.inputs["Value"])
    fm = N.new("ShaderNodeMix"); fm.data_type = "RGBA"
    L.new(hedge.outputs["Result"], fm.inputs["Factor"]); fm.inputs["A"].default_value = (0.05, 0.09, 0.03, 1)
    L.new(pal.outputs["Color"], fm.inputs["B"])
    # farm mask: inside Wall Maria, further than 2.6 km from the district, broken up by noise
    xyz = N.new("ShaderNodeSeparateXYZ"); L.new(tc.outputs["Object"], xyz.inputs["Vector"])
    my = N.new("ShaderNodeMapRange"); my.inputs["From Min"].default_value = 90; my.inputs["From Max"].default_value = 160
    L.new(xyz.outputs["Y"], my.inputs["Value"])
    ln = N.new("ShaderNodeVectorMath"); ln.operation = "LENGTH"; L.new(tc.outputs["Object"], ln.inputs[0])
    md = N.new("ShaderNodeMapRange"); md.inputs["From Min"].default_value = 2400; md.inputs["From Max"].default_value = 2800
    L.new(ln.outputs["Value"], md.inputs["Value"])
    n3 = N.new("ShaderNodeTexNoise"); n3.inputs["Scale"].default_value = 0.0007
    L.new(tc.outputs["Object"], n3.inputs["Vector"])
    mn = N.new("ShaderNodeMapRange"); mn.inputs["From Min"].default_value = 0.36; mn.inputs["From Max"].default_value = 0.39
    L.new(n3.outputs["Fac"], mn.inputs["Value"])
    mask = N.new("ShaderNodeMath"); mask.operation = "MULTIPLY"
    L.new(my.outputs["Result"], mask.inputs[0]); L.new(mn.outputs["Result"], mask.inputs[1])
    mask1 = N.new("ShaderNodeMath"); mask1.operation = "MULTIPLY"
    L.new(mask.outputs[0], mask1.inputs[0]); L.new(md.outputs["Result"], mask1.inputs[1])
    dg = N.new("ShaderNodeVectorMath"); dg.operation = "DISTANCE"; dg.inputs[1].default_value = (GF.x, GF.y, 0)
    L.new(tc.outputs["Object"], dg.inputs[0])
    mg = N.new("ShaderNodeMapRange"); mg.inputs["From Min"].default_value = 1300; mg.inputs["From Max"].default_value = 1700
    L.new(dg.outputs["Value"], mg.inputs["Value"])
    mask2 = N.new("ShaderNodeMath"); mask2.operation = "MULTIPLY"
    L.new(mask1.outputs[0], mask2.inputs[0]); L.new(mg.outputs["Result"], mask2.inputs[1])
    soft = N.new("ShaderNodeMix"); soft.data_type = "RGBA"; soft.inputs["Factor"].default_value = 0.45
    L.new(fm.outputs["Result"], soft.inputs["A"]); L.new(g.outputs["Result"], soft.inputs["B"])
    grain = N.new("ShaderNodeMix"); grain.data_type = "RGBA"; grain.blend_type = "MULTIPLY"; grain.inputs["Factor"].default_value = 0.5
    L.new(soft.outputs["Result"], grain.inputs["A"]); L.new(n2.outputs["Color"], grain.inputs["B"])
    fin = N.new("ShaderNodeMix"); fin.data_type = "RGBA"
    L.new(mask2.outputs[0], fin.inputs["Factor"]); L.new(g.outputs["Result"], fin.inputs["A"]); L.new(grain.outputs["Result"], fin.inputs["B"])
    L.new(fin.outputs["Result"], bsdf.inputs["Base Color"])
    return m

# ---------------------------------------------------------------- walls
def wall_ring(name, pts, mats, gaps=()):
    """Sweep a tapered wall profile along an open 2D polyline.
    gaps = [(x, y, half_width)]: segments whose midpoint lies within half_width are left open."""
    bm = bmesh.new()
    prof = [(-WALL_T / 2, -4), (WALL_T / 2, -4), (TOP_T / 2, WALL_H), (-TOP_T / 2, WALL_H)]
    n = len(pts)
    rings = []
    for k, p in enumerate(pts):
        a = pts[max(k - 1, 0)]; b = pts[min(k + 1, n - 1)]
        t = (Vector(b) - Vector(a)).normalized()
        nrm = Vector((-t.y, t.x))
        rings.append([bm.verts.new((p[0] + nrm.x * o, p[1] + nrm.y * o, z)) for o, z in prof])
    skip = []
    for k in range(n - 1):
        mx, my = (pts[k][0] + pts[k + 1][0]) / 2, (pts[k][1] + pts[k + 1][1]) / 2
        skip.append(any(math.hypot(mx - gx, my - gy) < hw for gx, gy, hw in gaps))
    for k in range(n - 1):
        if skip[k]:
            continue
        r0, r1 = rings[k], rings[k + 1]
        for e in range(4):
            bm.faces.new((r0[e], r0[(e + 1) % 4], r1[(e + 1) % 4], r1[e]))
    for k in range(n):
        left = skip[k - 1] if k > 0 else True
        right = skip[k] if k < n - 1 else True
        if left != right:
            bm.faces.new(rings[k])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return obj_from_bm(name, bm, [mats["stone"]])

def along(pts):
    """Yield (point, tangent, normal, arclength) for each vertex of a polyline."""
    s = 0.0
    n = len(pts)
    for k in range(n):
        a = Vector(pts[max(k - 1, 0)]); b = Vector(pts[min(k + 1, n - 1)])
        t = (b - a).normalized(); nrm = Vector((-t.y, t.x))
        if k > 0:
            s += (Vector(pts[k]) - Vector(pts[k - 1])).length
        yield Vector(pts[k]), t, nrm, s

def near_gap(p, gaps, extra):
    return any(math.hypot(p.x - gx, p.y - gy) < hw + extra for gx, gy, hw in gaps)

def buttresses(name, pts, gaps, mats, every=24.0):
    """Tapered pilasters on both faces, which give the walls their panelled look."""
    bm = bmesh.new()
    nxt = 0.0
    for p, t, nrm, s in along(pts):
        if s < nxt or near_gap(p, gaps, 10):
            continue
        nxt = s + every
        rot = math.atan2(t.y, t.x)
        box(bm, (p.x, p.y, (WALL_H - 1.5 - 4) / 2 - 4), (6.0, WALL_T + 7.0, WALL_H - 1.5 + 4), rot,
            taper=(0.95, (TOP_T + 5.0) / (WALL_T + 7.0)))
    return obj_from_bm(name, bm, [mats["stone"]])

def wall_top(name, pts, gaps, mats, every_cross=42.0):
    """Rails along the wall walk plus cross tracks, a low parapet lip on both edges."""
    bm = bmesh.new()
    z = WALL_H
    nxt = 0.0
    for k in range(len(pts) - 1):
        a, b = Vector(pts[k]), Vector(pts[k + 1])
        mid = (a + b) / 2
        if near_gap(mid, gaps, 2):
            continue
        t = (b - a); L = t.length; t.normalize(); nrm = Vector((-t.y, t.x)); rot = math.atan2(t.y, t.x)
        for off in (-2.2, -0.7, 1.4, 2.9):                      # two tracks (outer one for cannons)
            c = mid + nrm * off
            box(bm, (c.x, c.y, z + 0.12), (L + 0.05, 0.16, 0.24), rot, mi=1)
        for off in (-TOP_T / 2 + 0.3, TOP_T / 2 - 0.3):         # parapet lip
            c = mid + nrm * off
            box(bm, (c.x, c.y, z + 0.4), (L + 0.05, 0.6, 0.8), rot, mi=0)
    for p, t, nrm, s in along(pts):
        if s < nxt or near_gap(p, gaps, 6):
            continue
        nxt = s + every_cross
        rot = math.atan2(t.y, t.x) + math.pi / 2
        for off in (-0.75, 0.75):
            c = p + t * off
            box(bm, (c.x, c.y, z + 0.14), (TOP_T - 0.8, 0.16, 0.26), rot, mi=1)
        for q in range(-3, 4):                                    # sleepers
            c = p + nrm * q
            box(bm, (c.x, c.y, z + 0.05), (0.35, 2.2, 0.1), rot + math.pi / 2, mi=2)
    return obj_from_bm(name, bm, [mats["stone"], mats["iron"], mats["gate"]])

def gatehouse(name, center, angle, mats, w=GATE_W, h=GATE_H, deep=6.0, door=True):
    """Thickened block over a gap in the wall, with an arched opening, a heavy banded door and a lintel."""
    bm = bmesh.new()
    bw = w + 16
    T = WALL_T + deep
    # side piers
    for sx in (-1, 1):
        box(bm, (sx * (w / 2 + 4), 0, (WALL_H + 2 - 4) / 2 - 4 + 1), (8, T, WALL_H + 6), taper=(1, 0.8))
    # mass above the opening, arch approximated with stepped blocks
    box(bm, (0, 0, (h + WALL_H + 2) / 2), (w + 0.2, T, WALL_H + 2 - h), taper=(1, 0.8))
    for i in range(1, 6):
        a = i / 6 * math.pi / 2
        hw = w / 2 * math.cos(a)
        z0 = h - 3.5 + 3.5 * math.sin(a)
        box(bm, (w / 2 - (w / 2 - hw) / 2, 0, (z0 + h) / 2), (w / 2 - hw, T, h - z0 + 0.01))
        box(bm, (-w / 2 + (w / 2 - hw) / 2, 0, (z0 + h) / 2), (w / 2 - hw, T, h - z0 + 0.01))
    # crenellated cap and a cornice band
    box(bm, (0, 0, WALL_H + 2.6), (bw + 1, T * 0.82, 1.2))
    for i in range(-4, 5):
        box(bm, (i * bw / 9, 0, WALL_H + 4), (bw / 18, T * 0.82, 1.6))
    box(bm, (0, 0, h + 2.5), (w + 2, T + 0.6, 1.2), mi=0)
    ob = obj_from_bm(name, bm, [mats["stone"]])
    ob.location = (center[0], center[1], 0); ob.rotation_euler.z = angle
    if door:
        d = bmesh.new()
        box(d, (0, -T / 2 + 2.2, (h - 0.5) / 2 - 0.5), (w + 0.4, 1.6, h), mi=0)
        for z in range(2, int(h), 3):
            box(d, (0, -T / 2 + 1.25, z), (w + 0.5, 0.25, 0.45), mi=1)
        for xx in (-w / 4, w / 4):
            box(d, (xx, -T / 2 + 1.25, h / 2), (0.45, 0.25, h - 1), mi=1)
        do = obj_from_bm(name + "_Door", d, [mats["gate"], mats["iron"]])
        do.location = ob.location; do.rotation_euler.z = angle
    return ob

def cannon_mesh(mats):
    bm = bmesh.new()
    box(bm, (0, 0, 0.55), (1.6, 2.4, 0.5), mi=1)                     # carriage bed
    for sx in (-0.65, 0.65):
        box(bm, (sx, 0.1, 0.95), (0.18, 2.0, 0.7), mi=1, taper=(1, 0.6))   # cheeks
        for sy in (-0.8, 0.8):
            cyl(bm, (sx * 1.25, sy, 0.38), (sx * 1.25 + 0.15 * (1 if sx > 0 else -1), sy, 0.38), 0.38, seg=10, mi=1)
    cyl(bm, (0, -1.1, 1.15), (0, 2.4, 1.0), 0.36, 0.26, seg=12, mi=0)    # barrel, muzzle forward (+y)
    cyl(bm, (0, 2.25, 1.01), (0, 2.45, 1.0), 0.33, 0.33, seg=12, mi=0)
    cyl(bm, (0, -1.25, 1.16), (0, -1.05, 1.15), 0.2, 0.3, seg=10, mi=0)
    me = bpy.data.meshes.new("Cannon"); bm.to_mesh(me); bm.free()
    me.materials.append(mats["iron"]); me.materials.append(mats["gate"])
    return me

def barrels_mesh(mats):
    bm = bmesh.new()
    rnd = random.Random(2)
    for i in range(7):
        x, y = rnd.uniform(-1.6, 1.6), rnd.uniform(-1.6, 1.6)
        cyl(bm, (x, y, 0), (x, y, 1.1), 0.42, 0.42, seg=10, mi=0)
        cyl(bm, (x, y, 0.3), (x, y, 0.36), 0.44, seg=10, mi=1)
        cyl(bm, (x, y, 0.8), (x, y, 0.86), 0.44, seg=10, mi=1)
    for i in range(5):                                                # cannon balls
        bmesh.ops.create_icosphere(bm, subdivisions=1, radius=0.17,
                                   matrix=__import__("mathutils").Matrix.Translation((2.2 + (i % 3) * 0.36, (i // 3) * 0.36, 0.17)))
    me = bpy.data.meshes.new("Barrels"); bm.to_mesh(me); bm.free()
    me.materials.append(mats["gate"]); me.materials.append(mats["iron"])
    return me

def place_on_wall(pts, gaps, mesh, every, offset, coll, start=0.0, face_out=True, name="P"):
    """Instances of mesh along the wall top; offset across the walk (negative = outer side)."""
    nxt = start; i = 0
    for p, t, nrm, s in along(pts):
        if s < nxt or near_gap(p, gaps, 14):
            continue
        nxt = s + every
        c = p + nrm * offset
        o = bpy.data.objects.new(f"{name}{i}", mesh); i += 1
        o.location = (c.x, c.y, WALL_H)
        out = -nrm if face_out else nrm
        o.rotation_euler.z = math.atan2(out.y, out.x) - math.pi / 2
        coll.objects.link(o)

def build_walls(mats):
    # Wall Maria: very large radius (480 km in canon), so near-straight here; slight bend for depth.
    maria = [(i * 20.0, -(i * 20.0) ** 2 / (2 * 480000.0) * 30) for i in range(-450, 451)]
    # make sure Wall Maria meets the district walls exactly at x = +-W
    maria = [(x, 0.0) if abs(x) <= W + 1 else (x, y + (W ** 2) / (2 * 480000.0) * 30) for x, y in maria]
    m_gaps = [(0.0, 0.0, GATE_W / 2 + 0.5), (CX, 0.0, CANAL_W / 2 + 0.5)]
    # vertices exactly at the gap edges (the 20 m spacing would otherwise leave the inner gate walled up)
    for gx, gy, hw in m_gaps:
        maria += [(gx - hw + 0.4, 0.0), (gx - hw * 0.5, 0.0), (gx, 0.0), (gx + hw * 0.5, 0.0), (gx + hw - 0.4, 0.0)]
    maria = sorted(set(maria))
    wall_ring("WallMaria", maria, mats, gaps=m_gaps)
    dist = district_outline(6.0)
    d_gaps = [(OUTER_GATE[0], OUTER_GATE[1], GATE_W / 2 + 0.5), (CANAL_FAR[0], CANAL_FAR[1], CANAL_W / 2 + 0.5)]
    wall_ring("WallShiganshina", dist, mats, gaps=d_gaps)
    near_maria = [p for p in maria if abs(p[0]) < 4200]
    buttresses("ButtressMaria", near_maria, m_gaps, mats)
    buttresses("ButtressShiganshina", dist, d_gaps, mats)
    wall_top("WallTopMaria", [p for p in maria if abs(p[0]) < 2600], m_gaps, mats)
    wall_top("WallTopShiganshina", dist, d_gaps, mats)
    gatehouse("InnerGate", (0, 0), 0, mats)
    gatehouse("OuterGate", OUTER_GATE, 0, mats, deep=8.0)
    gatehouse("WaterGateMaria", (CX, 0), 0, mats, w=CANAL_W, h=11, door=False)
    a = math.atan2(CANAL_FAR[1] + S, CANAL_FAR[0])
    gatehouse("WaterGateOuter", CANAL_FAR, a + math.pi / 2, mats, w=CANAL_W, h=11, door=False)
    # garrison cannons and ammunition on the wall walk
    gc = new_coll("Garrison")
    cm, bmsh = cannon_mesh(mats), barrels_mesh(mats)
    place_on_wall(dist, d_gaps, cm, 38, -2.15, gc, start=12, name="Cannon")
    place_on_wall(dist, d_gaps, bmsh, 152, 1.6, gc, start=40, name="Ammo")
    place_on_wall([p for p in maria if abs(p[0]) < 2600], m_gaps, cm, 60, -2.15, gc, start=30, face_out=True, name="CannonM")
    return dist

# ---------------------------------------------------------------- houses
def house_mesh(name, w, d, h, roof_h, mats, wall_m, roof_m, chimney=False, hip=False):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts:
        v.co = Vector((v.co.x * w, v.co.y * d, v.co.z * h + h / 2 - 0.5))
    for f in bm.faces:
        f.material_index = 0
    o = 0.5
    ridge_in = w * 0.3 if hip else 0.0
    p = [bm.verts.new(c) for c in [(-w / 2 - o, -d / 2 - o, h - 0.3), (w / 2 + o, -d / 2 - o, h - 0.3),
                                   (w / 2 + o, d / 2 + o, h - 0.3), (-w / 2 - o, d / 2 + o, h - 0.3),
                                   (-w / 2 - o + ridge_in, 0, h + roof_h), (w / 2 + o - ridge_in, 0, h + roof_h)]]
    for fv in [(p[0], p[1], p[5], p[4]), (p[3], p[4], p[5], p[2]), (p[0], p[4], p[3]), (p[1], p[2], p[5]), (p[0], p[3], p[2], p[1])]:
        f = bm.faces.new(fv); f.material_index = 1
    if chimney:
        box(bm, (w * 0.25, d * 0.18, h + roof_h * 0.7), (0.9, 0.9, roof_h * 0.9), mi=0)
    # window rows (dark insets on the long walls) for close views
    for z in range(3, int(h) - 1, 3):
        for xx in [i * 2.0 - w / 2 + 1.2 for i in range(int(w / 2))]:
            for sy in (-1, 1):
                box(bm, (xx, sy * (d / 2 + 0.02), z), (0.7, 0.05, 1.1), mi=2)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    me.materials.append(mats[wall_m]); me.materials.append(mats[roof_m]); me.materials.append(mats["window"])
    return me

def church_mesh(mats):
    bm = bmesh.new()
    def bx(cx, cy, w, d, z0, z1, mi):
        box(bm, (cx, cy, (z0 + z1) / 2), (w, d, z1 - z0), mi=mi)
    bx(0, 0, 14, 34, 0, 16, 0)
    bx(0, 20, 8, 8, 0, 34, 0)
    p = [bm.verts.new(c) for c in [(-7.5, -17.5, 16), (7.5, -17.5, 16), (7.5, 17.5, 16), (-7.5, 17.5, 16), (0, -17.5, 24), (0, 17.5, 24)]]
    for fv in [(p[0], p[1], p[4]), (p[2], p[3], p[5]), (p[1], p[2], p[5], p[4]), (p[3], p[0], p[4], p[5])]:
        f = bm.faces.new(fv); f.material_index = 1
    q = [bm.verts.new(c) for c in [(-4.2, 15.8, 34), (4.2, 15.8, 34), (4.2, 24.2, 34), (-4.2, 24.2, 34), (0, 20, 52)]]
    for fv in [(q[0], q[1], q[4]), (q[1], q[2], q[4]), (q[2], q[3], q[4]), (q[3], q[0], q[4])]:
        f = bm.faces.new(fv); f.material_index = 1
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new("Church")
    bm.to_mesh(me); bm.free()
    me.materials.append(mats["plaster_w"]); me.materials.append(mats["roof_slate"])
    return me

def monument_mesh(mats):
    """Stepped plinth with a column and statue block in the central plaza."""
    bm = bmesh.new()
    for i, s in enumerate((16, 12, 8)):
        box(bm, (0, 0, i * 1.2 + 0.6), (s, s, 1.2))
    box(bm, (0, 0, 3.6 + 5), (3.2, 3.2, 10), taper=(0.8, 0.8))
    box(bm, (0, 0, 14.5), (2.6, 2.6, 2))
    cyl(bm, (0, 0, 15.5), (0, 0, 19), 0.9, 0.6, seg=10)
    me = bpy.data.meshes.new("Monument"); bm.to_mesh(me); bm.free()
    me.materials.append(mats["stone_light"])
    return me

def tree_mesh(name, kind, mats, seed=0):
    rnd = random.Random(seed)
    bm = bmesh.new()
    r = bmesh.ops.create_cone(bm, cap_ends=True, segments=6, radius1=0.35, radius2=0.25, depth=4)
    for v in r["verts"]:
        v.co.z += 2
    n0 = len(bm.faces)
    if kind == "conifer":
        verts = []
        for tier in range(4):                                  # stacked tiers read as anime conifers
            c = bmesh.ops.create_cone(bm, cap_ends=True, segments=9, radius1=2.9 - tier * 0.55, radius2=0.2, depth=5.2 - tier * 0.5)
            for v in c["verts"]:
                v.co.z += 4.5 + tier * 2.6
                v.co.x += noise.noise(v.co * 0.9 + Vector((seed, tier, 0))) * 0.3
            verts += c["verts"]
        c = {"verts": verts}
    else:
        verts = []
        for b in range(rnd.randint(2, 4)):
            c = bmesh.ops.create_icosphere(bm, subdivisions=2, radius=rnd.uniform(2.2, 3.4))
            off = Vector((rnd.uniform(-1.8, 1.8), rnd.uniform(-1.8, 1.8), rnd.uniform(5.5, 8)))
            for v in c["verts"]:
                v.co.z *= 0.85; v.co += off
                v.co += Vector((noise.noise(v.co * 0.7 + Vector((seed, 0, 0))), noise.noise(v.co * 0.7 + Vector((5, 1, 2))), 0)) * 0.6
            verts += c["verts"]
        c = {"verts": verts}
    for i, f in enumerate(bm.faces):
        f.material_index = 1 if i >= n0 else 0
        f.smooth = kind != "conifer"
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    me.materials.append(mats["bark"]); me.materials.append(mats[("leaf", "leaf2", "leaf3")[seed % 3] if kind != "conifer" else "leaf_dark"])
    return me

def scatter(name, coll, pts, year):
    """Point cloud object instancing children of coll via geometry nodes.
    pts: list of (x, y, z, rot_z, scale, variant, born, dead)."""
    me = bpy.data.meshes.new(name + "_pts")
    me.vertices.add(len(pts))
    me.vertices.foreach_set("co", [c for p in pts for c in p[:3]])
    for an, typ in (("rot", "FLOAT_VECTOR"), ("scl", "FLOAT_VECTOR"), ("variant", "INT"), ("born", "FLOAT"), ("dead", "FLOAT")):
        me.attributes.new(an, typ, "POINT")
    me.attributes["rot"].data.foreach_set("vector", [c for p in pts for c in (0, 0, p[3])])
    me.attributes["scl"].data.foreach_set("vector", [c for p in pts for c in (p[4],) * 3])
    me.attributes["variant"].data.foreach_set("value", [p[5] for p in pts])
    me.attributes["born"].data.foreach_set("value", [p[6] for p in pts])
    me.attributes["dead"].data.foreach_set("value", [p[7] for p in pts])
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    ng = bpy.data.node_groups.new(name + "_GN", "GeometryNodeTree")
    ng.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    N = ng.nodes; L = ng.links
    gi = N.new("NodeGroupInput"); go = N.new("NodeGroupOutput")
    yv = N.new("ShaderNodeValue"); yv.name = "Year"; yv.outputs[0].default_value = float(year)
    sc = bpy.context.scene
    sc["year"] = float(year)
    fc = yv.outputs[0].driver_add("default_value"); dv = fc.driver; dv.type = "AVERAGE"
    var = dv.variables.new(); var.type = "SINGLE_PROP"
    var.targets[0].id_type = "SCENE"; var.targets[0].id = sc; var.targets[0].data_path = '["year"]'
    def attr(n, t):
        a = N.new("GeometryNodeInputNamedAttribute"); a.data_type = t; a.inputs["Name"].default_value = n; return a
    born, dead = attr("born", "FLOAT"), attr("dead", "FLOAT")
    c1 = N.new("FunctionNodeCompare"); c1.operation = "LESS_EQUAL"
    L.new(born.outputs["Attribute"], c1.inputs[0]); L.new(yv.outputs[0], c1.inputs[1])
    c2 = N.new("FunctionNodeCompare"); c2.operation = "GREATER_THAN"
    L.new(dead.outputs["Attribute"], c2.inputs[0]); L.new(yv.outputs[0], c2.inputs[1])
    band = N.new("FunctionNodeBooleanMath"); band.operation = "AND"
    L.new(c1.outputs[0], band.inputs[0]); L.new(c2.outputs[0], band.inputs[1])
    ci = N.new("GeometryNodeCollectionInfo"); ci.transform_space = "ORIGINAL"
    ci.inputs["Collection"].default_value = coll
    ci.inputs["Separate Children"].default_value = True
    ci.inputs["Reset Children"].default_value = True
    iop = N.new("GeometryNodeInstanceOnPoints")
    L.new(gi.outputs["Geometry"], iop.inputs["Points"])
    L.new(band.outputs[0], iop.inputs["Selection"])
    L.new(ci.outputs[0], iop.inputs["Instance"])
    iop.inputs["Pick Instance"].default_value = True
    L.new(attr("variant", "INT").outputs["Attribute"], iop.inputs["Instance Index"])
    L.new(attr("rot", "FLOAT_VECTOR").outputs["Attribute"], iop.inputs["Rotation"])
    L.new(attr("scl", "FLOAT_VECTOR").outputs["Attribute"], iop.inputs["Scale"])
    L.new(iop.outputs["Instances"], go.inputs["Geometry"])
    mod = ob.modifiers.new("GN", "NODES"); mod.node_group = ng
    return ob

# ---------------------------------------------------------------- town layout
PLAZA = (-20.0, -360.0, 40.0)

def street_network():
    """Polylines (list of (x, y)) with half widths: main avenue gate to gate, a canal-side road,
    long streets parallel to the walls, cross lanes, and arcs at the rounded end."""
    streets = []
    yend = OUTER_GATE[1] + 6
    av = [(noise.noise(Vector((0, y / 200, 7))) * 4, y) for y in range(-8, int(yend), -6)]
    streets.append((av, 8.0))
    streets.append(([(CX - CS * (CANAL_W / 2 + 6), y) for y in range(-8, int(district_ymin(CX - CS * 18, 14)), -6)], 4.5))
    for x0 in [CS * v for v in (-232, -165, -95, 85, 160)]:
        pts = []
        for y in range(-14, -int(S + R), -6):
            x = x0 + noise.noise(Vector((x0 / 50, y / 160, 5))) * 9
            if y < district_ymin(x, 16):
                break
            pts.append((x, y))
        if len(pts) > 2:
            streets.append((pts, 4.0 if abs(x0) != 165 else 5.0))
    for y0 in range(-48, -int(S) - 1, -70):
        xa, xb = sorted((CX - CS * (CANAL_W / 2 + 4), -CS * (W - 12)))
        pts = [(x, y0 + noise.noise(Vector((x / 140, y0 / 60, 2))) * 6) for x in range(int(xa), int(xb), 6)]
        streets.append((pts, 3.5))
    for rr in (90, 165, 235):
        pts = []
        for k in range(181):
            a = math.pi + math.radians(k)
            x, y = math.cos(a) * rr, -S + math.sin(a) * rr
            if CS * (CX - x) > CANAL_W / 2 + 4:
                pts.append((x, y))
        streets.append((pts, 4.0))
    # spokes from the plaza
    for a in range(0, 360, 45):
        r0 = PLAZA[2]
        pts = [(PLAZA[0] + math.cos(math.radians(a)) * r, PLAZA[1] + math.sin(math.radians(a)) * r) for r in range(int(r0), int(r0) + 90, 5)]
        streets.append((pts, 3.5))
    # lanes in the strip between the west wall and the canal
    streets.append(([(CS * (W - 30), y) for y in range(-14, int(district_ymin(W - 30, 16)), -6)], 3.0))
    return streets

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

ROADS = None
def on_road(x, y, pad=0.0):
    global ROADS
    if ROADS is None:
        ROADS = road_index(street_network())
    if -60 < y < -14 and abs(x) < 54:                                # inner gate square
        return True
    if math.hypot(x - PLAZA[0], y - PLAZA[1]) < PLAZA[2] + pad:       # central plaza
        return True
    if abs(x) < 34 and y < OUTER_GATE[1] + 60:                         # outer gate square
        return True
    if abs(x - CX) < CANAL_W / 2 + 2 + pad:                            # canal
        return True
    gx, gy = int(x // 20), int(y // 20)
    for i in (-1, 0, 1):
        for j in (-1, 0, 1):
            for px, py, hw in ROADS.get((gx + i, gy + j), ()):
                if (px - x) ** 2 + (py - y) ** 2 < (hw + pad) ** 2:
                    return True
    return False

def town_points(n_variants, widths):
    """Row houses fronting every street, scattered back-lot houses, and garden trees."""
    rnd = random.Random(21)
    pts, trees = [], []
    occ = {}
    def free(x, y, rad):
        gx, gy = int(x // 12), int(y // 12)
        for i in (-1, 0, 1):
            for j in (-1, 0, 1):
                for ox, oy, orad in occ.get((gx + i, gy + j), ()):
                    if (ox - x) ** 2 + (oy - y) ** 2 < (rad + orad) ** 2:
                        return False
        return True
    def put(x, y, ang, v, rad):
        born = 760 + (-y / (S + R)) * 60 + abs(x) / W * 20 + rnd.uniform(-12, 12)
        pts.append((x, y, 0, ang, rnd.uniform(0.92, 1.08), v, born, 99999))
        occ.setdefault((int(x // 12), int(y // 12)), []).append((x, y, rad))
    for pts_s, hw in street_network():
        for k in range(len(pts_s) - 1):
            ax, ay = pts_s[k]; bx, by = pts_s[k + 1]
            seg = math.hypot(bx - ax, by - ay)
            if seg == 0:
                continue
            tx, ty = (bx - ax) / seg, (by - ay) / seg
            nx, ny = -ty, tx
            t = 0.0
            while t < seg:
                v = rnd.randrange(n_variants)
                w, dpt = widths[v]
                for side in (1, -1):
                    off = hw + dpt / 2 + 0.8
                    x = ax + tx * t + nx * off * side
                    y = ay + ty * t + ny * off * side
                    if rnd.random() < 0.06 or not in_district(x, y, 15):
                        continue
                    if on_road(x, y, pad=dpt / 2 - 0.5):
                        continue
                    rad = min(w, dpt) * 0.5
                    if free(x, y, rad):
                        put(x, y, math.atan2(ty, tx) + (0 if side > 0 else math.pi), v, rad)
                t += w + rnd.uniform(0.2, 1.4)
    for _ in range(14000):
        x, y = rnd.uniform(-W, W), rnd.uniform(-S - R, 0)
        if not in_district(x, y, 16) or on_road(x, y, pad=4):
            continue
        v = rnd.randrange(n_variants); w, dpt = widths[v]
        r = max(w, dpt) * 0.55
        if not free(x, y, r):
            continue
        if rnd.random() < 0.55:
            put(x, y, street_angle(x, y), v, r)
        elif rnd.random() < 0.5:
            trees.append((x, y, 0, rnd.uniform(0, 6.28), rnd.uniform(0.6, 0.9), rnd.randrange(7), -10000, 99999))
            occ.setdefault((int(x // 12), int(y // 12)), []).append((x, y, 3))
    # small settlement just inside Wall Maria around the inner gate road and along the canal
    for _ in range(9000):
        x, y = rnd.gauss(-CS * 40, 170), rnd.uniform(25, 260)
        if abs(x) < 12 or abs(x - CX) < CANAL_W / 2 + 6 or rnd.random() > math.exp(-y / 70):
            continue
        v = rnd.randrange(n_variants); w, dpt = widths[v]
        r = max(w, dpt) * 0.6
        if free(x, y, r + 2):
            put(x, y, rnd.choice((0, math.pi / 2)) + rnd.uniform(-0.2, 0.2), v, r + 2)
    return pts, trees

def street_angle(x, y):
    return (0 if y > -S else math.atan2(y + S, x)) + math.pi / 2 + noise.noise(Vector((x / 260, y / 260, 2.5))) * 0.4

def gn_forest(terrain, tree_coll):
    """Dense forests: points distributed on the terrain, masked by noise, instanced with tree variants."""
    ng = bpy.data.node_groups.new("ForestGN", "GeometryNodeTree")
    ng.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    N = ng.nodes; L = ng.links
    gi = N.new("NodeGroupInput"); go = N.new("NodeGroupOutput")
    pos = N.new("GeometryNodeInputPosition")
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 1 / 700; nz.inputs["Detail"].default_value = 4
    nz.inputs["Roughness"].default_value = 0.6
    L.new(pos.outputs[0], nz.inputs["Vector"])
    xyz = N.new("ShaderNodeSeparateXYZ"); L.new(pos.outputs[0], xyz.inputs[0])
    thr = N.new("ShaderNodeMapRange"); thr.inputs["From Min"].default_value = -20; thr.inputs["From Max"].default_value = 20
    thr.inputs["To Min"].default_value = 0.50; thr.inputs["To Max"].default_value = 0.55
    L.new(xyz.outputs["Y"], thr.inputs["Value"])
    cmp = N.new("FunctionNodeCompare"); cmp.operation = "GREATER_THAN"
    L.new(nz.outputs["Fac"], cmp.inputs[0]); L.new(thr.outputs["Result"], cmp.inputs[1])
    def dist_xy(cx, cy, sy=1.0):
        v = N.new("ShaderNodeVectorMath"); v.operation = "DISTANCE"
        v.inputs[1].default_value = (cx, cy * sy, 0)
        ys = N.new("ShaderNodeMath"); ys.operation = "MULTIPLY"; ys.inputs[1].default_value = sy
        L.new(xyz.outputs["Y"], ys.inputs[0])
        flat = N.new("ShaderNodeCombineXYZ"); L.new(xyz.outputs["X"], flat.inputs["X"]); L.new(ys.outputs[0], flat.inputs["Y"])
        L.new(flat.outputs[0], v.inputs[0]); return v.outputs["Value"]
    # keep a meadow ring around the district (ellipse around its centre), the hill and the wall line
    far_town = N.new("FunctionNodeCompare"); far_town.operation = "GREATER_THAN"
    L.new(dist_xy(0, -(S + R) / 2, W / ((S + R) / 2)), far_town.inputs[0]); far_town.inputs[1].default_value = W + 180
    far_hill = N.new("FunctionNodeCompare"); far_hill.operation = "GREATER_THAN"
    L.new(dist_xy(HILL.x, HILL.y), far_hill.inputs[0]); far_hill.inputs[1].default_value = 190
    absy = N.new("ShaderNodeMath"); absy.operation = "ABSOLUTE"; L.new(xyz.outputs["Y"], absy.inputs[0])
    far_wall = N.new("FunctionNodeCompare"); far_wall.operation = "GREATER_THAN"
    L.new(absy.outputs[0], far_wall.inputs[0]); far_wall.inputs[1].default_value = 40
    far_og = N.new("FunctionNodeCompare"); far_og.operation = "GREATER_THAN"        # meadow outside the outer gate
    L.new(dist_xy(0, OUTER_GATE[1] - 380), far_og.inputs[0]); far_og.inputs[1].default_value = 560
    far_gf = N.new("FunctionNodeCompare"); far_gf.operation = "GREATER_THAN"
    L.new(dist_xy(GF.x, GF.y), far_gf.inputs[0]); far_gf.inputs[1].default_value = 760
    acc = cmp.outputs[0]
    for c in (far_town, far_hill, far_wall, far_og):
        a = N.new("FunctionNodeBooleanMath"); a.operation = "AND"
        L.new(acc, a.inputs[0]); L.new(c.outputs[0], a.inputs[1]); acc = a.outputs[0]
    dp = N.new("GeometryNodeDistributePointsOnFaces"); dp.distribute_method = "RANDOM"
    dp.inputs["Density"].default_value = float(os.environ.get("TREE_DENS", "0.009"))
    L.new(gi.outputs[0], dp.inputs["Mesh"]); L.new(acc, dp.inputs["Selection"])
    ci = N.new("GeometryNodeCollectionInfo"); ci.inputs["Collection"].default_value = tree_coll
    ci.inputs["Separate Children"].default_value = True; ci.inputs["Reset Children"].default_value = True
    iop = N.new("GeometryNodeInstanceOnPoints"); iop.inputs["Pick Instance"].default_value = True
    rv = N.new("FunctionNodeRandomValue"); rv.data_type = "INT"; rv.inputs["Min"].default_value = 3; rv.inputs["Max"].default_value = 12
    L.new(rv.outputs["Value"], iop.inputs["Instance Index"])
    rr = N.new("FunctionNodeRandomValue"); rr.data_type = "FLOAT_VECTOR"
    rr.inputs["Min"].default_value = (0, 0, 0); rr.inputs["Max"].default_value = (0, 0, 6.28)
    L.new(rr.outputs["Value"], iop.inputs["Rotation"])
    rs = N.new("FunctionNodeRandomValue"); rs.data_type = "FLOAT"; rs.inputs["Min"].default_value = 0.8; rs.inputs["Max"].default_value = 1.7
    L.new(rs.outputs["Value"], iop.inputs["Scale"])
    L.new(dp.outputs["Points"], iop.inputs["Points"]); L.new(ci.outputs[0], iop.inputs["Instance"])
    jg = N.new("GeometryNodeJoinGeometry")
    L.new(gi.outputs[0], jg.inputs[0]); L.new(iop.outputs[0], jg.inputs[0])
    L.new(jg.outputs[0], go.inputs[0])
    mod = terrain.modifiers.new("Forest", "NODES"); mod.node_group = ng

# ---------------------------------------------------------------- Forest of Giant Trees
def giant_tree_mesh(mats, seed):
    rnd = random.Random(seed)
    bm = bmesh.new()
    H = rnd.uniform(110, 140)
    cyl(bm, (0, 0, -2), (0, 0, 10), 13, 7.5, seg=16, mi=0)               # root flare
    for k in range(6):                                                   # buttress roots
        a = k / 6 * math.tau + rnd.uniform(-0.3, 0.3)
        cyl(bm, (math.cos(a) * 15, math.sin(a) * 15, -1), (math.cos(a) * 4, math.sin(a) * 4, 14), 2.6, 1.2, seg=6, mi=0)
    cyl(bm, (0, 0, 9), (rnd.uniform(-2, 2), rnd.uniform(-2, 2), H), 7.5, 3.6, seg=16, mi=0)
    for k in range(rnd.randint(4, 7)):                                   # high limbs where soldiers anchor
        z = rnd.uniform(H * 0.45, H * 0.85); a = rnd.uniform(0, math.tau); L = rnd.uniform(14, 26)
        cyl(bm, (0, 0, z), (math.cos(a) * L, math.sin(a) * L, z + L * 0.35), 1.3, 0.5, seg=6, mi=0)
    n0 = len(bm.faces)
    for k in range(rnd.randint(14, 18)):
        a = rnd.uniform(0, math.tau); r = rnd.uniform(4, 26)
        c = bmesh.ops.create_icosphere(bm, subdivisions=3, radius=rnd.uniform(12, 19))
        off = Vector((math.cos(a) * r, math.sin(a) * r, rnd.uniform(H * 0.72, H * 1.0)))
        for v in c["verts"]:
            v.co.z *= 0.6; v.co += off
            v.co += Vector((noise.noise(v.co * 0.12 + Vector((seed, 0, 0))), noise.noise(v.co * 0.12 + Vector((0, seed, 3))), 0)) * 4
    for i, f in enumerate(bm.faces):
        f.material_index = 1 if i >= n0 else 0
        f.smooth = True
    me = bpy.data.meshes.new(f"GiantTree{seed}"); bm.to_mesh(me); bm.free()
    me.materials.append(mats["bark_giant"]); me.materials.append(mats["leaf_giant"])
    return me

def giant_forest(mats):
    coll = new_coll("ForestOfGiantTrees")
    meshes = [giant_tree_mesh(mats, s) for s in range(6)]
    rnd = random.Random(9)
    placed = []
    for _ in range(900):
        a = rnd.uniform(0, math.tau); r = math.sqrt(rnd.random()) * 700
        x, y = GF.x + math.cos(a) * r * 1.3, GF.y + math.sin(a) * r
        if any((x - px) ** 2 + (y - py) ** 2 < 58 ** 2 for px, py in placed):
            continue
        placed.append((x, y))
        o = bpy.data.objects.new(f"GT{len(placed)}", meshes[len(placed) % len(meshes)])
        o.location = (x, y, height(x, y)); o.rotation_euler.z = rnd.uniform(0, math.tau)
        s = rnd.uniform(0.85, 1.15); o.scale = (s, s, s)
        coll.objects.link(o)
    return placed

# ---------------------------------------------------------------- figures (metaballs)
MB_K = 1 / 0.574      # metaball radius -> visible surface radius at default threshold

def mb_figure(name, parts, m, res=0.03):
    """parts: list of ('E', centre, (rx, ry, rz), rot_euler) ellipsoids or ('C', p0, p1, r) capsules,
    all in surface units. One metaball family = one material."""
    mb = bpy.data.metaballs.new(name); mb.resolution = res; mb.render_resolution = res
    for p in parts:
        if p[0] == "E":
            _, c, rad, *rot = p
            rr = min(rad)
            e = mb.elements.new(type="ELLIPSOID"); e.co = c; e.radius = rr * MB_K
            e.size_x, e.size_y, e.size_z = (r / rr for r in rad)
            if rot:
                e.rotation = Euler(rot[0]).to_quaternion()
        else:
            _, p0, p1, r = p
            p0, p1 = Vector(p0), Vector(p1)
            e = mb.elements.new(type="CAPSULE"); e.co = (p0 + p1) / 2; e.radius = r * MB_K
            e.size_x = (p1 - p0).length / 2
            e.rotation = (p1 - p0).to_track_quat("X", "Z")
    mb.materials.append(m)
    ob = bpy.data.objects.new(name, mb)
    bpy.context.scene.collection.objects.link(ob)
    # bake to a mesh so it can carry the outline modifier
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    bpy.data.objects.remove(ob); bpy.data.metaballs.remove(mb)
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    me.materials.clear(); me.materials.append(m)
    for f in me.polygons:
        f.use_smooth = True; f.material_index = 0
    outline(ob, res * 0.45)
    return ob

OUTLINE_MAT = None
def outline(ob, thickness):
    """Ink line: an inflated copy whose camera-facing side is transparent, so only its far side shows past the silhouette."""
    global OUTLINE_MAT
    if os.environ.get("LINES", "1") == "0":
        return
    if OUTLINE_MAT is None:
        m = bpy.data.materials.new("Ink"); m.use_nodes = True
        nt = m.node_tree; N = nt.nodes; L = nt.links
        N.remove(N["Principled BSDF"])
        em = N.new("ShaderNodeEmission"); em.inputs["Color"].default_value = (0.03, 0.02, 0.015, 1); em.inputs["Strength"].default_value = 1
        tr = N.new("ShaderNodeBsdfTransparent")
        geo = N.new("ShaderNodeNewGeometry")
        mx = N.new("ShaderNodeMixShader")
        L.new(geo.outputs["Backfacing"], mx.inputs[0]); L.new(tr.outputs[0], mx.inputs[1]); L.new(em.outputs[0], mx.inputs[2])
        L.new(mx.outputs[0], N["Material Output"].inputs["Surface"])
        OUTLINE_MAT = m
    bm = bmesh.new(); bm.from_mesh(ob.data)
    bm.normal_update()
    for v in bm.verts:
        v.co += v.normal * thickness
    hull = obj_from_bm(ob.name + "_Ink", bm, [OUTLINE_MAT])
    hull.parent = ob
    hull.visible_shadow = False; hull.visible_diffuse = False; hull.visible_glossy = False
    hull.visible_transmission = False; hull.visible_volume_scatter = False

def characters():
    c = bpy.data.collections.get("Characters")
    return c or new_coll("Characters")

def group(obs, loc, rot_z=0.0, scale=1.0, tilt=(0.0, 0.0)):
    """Parent figure parts to an empty; all of them go to the Characters collection (outlined)."""
    cc = characters()
    root = bpy.data.objects.new(obs[0].name + "_Root", None)
    cc.objects.link(root)
    for o in obs:
        for uc in list(o.users_collection):
            uc.objects.unlink(o)
        cc.objects.link(o)
        o.parent = root
    root.location = loc; root.rotation_euler = (tilt[0], tilt[1], rot_z); root.scale = (scale,) * 3
    return root

def scale_parts(parts, H):
    out = []
    for p in parts:
        if p[0] == "E":
            out.append(("E", tuple(c * H for c in p[1]), tuple(r * H for r in p[2]), *p[3:]))
        else:
            out.append(("C", tuple(c * H for c in p[1]), tuple(c * H for c in p[2]), p[3] * H))
    return out

def titan(name, M, seed, H, loc, rot_z):
    """Pure titan: unit proportions scaled by height H. Odd proportions vary per seed."""
    rnd = random.Random(seed)
    hs = rnd.uniform(1.0, 1.55)          # head scale
    fat = rnd.uniform(0.85, 1.5)
    arm = rnd.uniform(0.9, 1.25)
    lean = rnd.uniform(-0.15, 0.25)
    sk = []
    for sx in (-1, 1):
        sk += [("C", (sx * 0.085, 0, 0.47), (sx * 0.09, 0.01, 0.27), 0.062 * fat ** 0.5),
               ("C", (sx * 0.09, 0.01, 0.26), (sx * 0.09, -0.01, 0.04), 0.048),
               ("E", (sx * 0.09, 0.035, 0.02), (0.035, 0.07, 0.022))]
        sw = rnd.uniform(-0.25, 0.35)
        sh = Vector((sx * 0.17 * fat ** 0.3, 0, 0.77))
        el = sh + Vector((sx * 0.05, 0.06 * sw, -0.21 * arm))
        hd = el + Vector((sx * 0.01, 0.10 * sw + 0.03, -0.2 * arm))
        sk += [("C", tuple(sh), tuple(el), 0.042), ("C", tuple(el), tuple(hd), 0.036), ("E", tuple(hd + Vector((0, 0, -0.03))), (0.03, 0.04, 0.05))]
    sk += [("E", (0, 0, 0.52), (0.14 * fat ** 0.5, 0.09 * fat, 0.08)),
           ("E", (0, 0.01 * fat, 0.63), (0.15 * fat ** 0.6, 0.11 * fat, 0.12)),
           ("E", (0, 0, 0.74), (0.17 * fat ** 0.3, 0.09, 0.08)),
           ("C", (0, 0, 0.77), (0, 0.01, 0.84), 0.04),
           ("E", (0, 0.015, 0.84 + 0.08 * hs), (0.07 * hs, 0.08 * hs, 0.085 * hs))]
    body = mb_figure(name, scale_parts(sk, H), M["titan_skin"], res=H * 0.007)
    # face: wide grin with teeth, dark eyes, optional hair
    hz = 0.84 + 0.08 * hs
    bm = bmesh.new()
    box(bm, (0, 0.015 + 0.078 * hs, hz - 0.03 * hs), (0.085 * hs, 0.01, 0.012 * hs), mi=0)
    for sx in (-1, 1):
        bmesh.ops.create_icosphere(bm, subdivisions=1, radius=0.011 * hs,
                                   matrix=__import__("mathutils").Matrix.Translation((sx * 0.028 * hs, 0.015 + 0.072 * hs, hz + 0.02 * hs)))
    for f in bm.faces:
        f.material_index = 0 if f.calc_center_median().z < hz else 1
    face = obj_from_bm(name + "_Face", bm, [M["teeth"], M["eye"]])
    face.scale = (H, H, H)
    parts = [body, face]
    if rnd.random() < 0.7:
        hair = mb_figure(name + "Hair", scale_parts([("E", (0, -0.005, hz + 0.03 * hs), (0.075 * hs, 0.08 * hs, 0.07 * hs))], H),
                         M[rnd.choice(("hair_brown", "hair_black", "hair_blond"))], res=H * 0.007)
        parts.append(hair)
    z = height(*loc)
    return group(parts, (loc[0], loc[1], z - 0.2), rot_z, tilt=(lean * 0.4, 0))

def face_features(name, M, c, r, closed=False, iris="eye_green", mouth_open=False):
    """Anime face on a head centred at c with radii r, looking along +y: large eyes, brows, small mouth."""
    bm = bmesh.new()
    fy = c[1] + r[1] * 0.93
    ez = c[2] - r[2] * 0.05
    for sx in (-1, 1):
        ex = c[0] + sx * r[0] * 0.40
        if closed:
            for k in range(5):                                       # downward arc of a closed lid
                t = (k - 2) / 2
                box(bm, (ex + t * r[0] * 0.17, fy - 0.004, ez - abs(t) ** 2 * r[2] * 0.04), (r[0] * 0.09, 0.012, r[2] * 0.035), mi=2)
        else:
            box(bm, (ex, fy - 0.006, ez), (r[0] * 0.34, 0.012, r[2] * 0.30), mi=0)                 # white
            box(bm, (ex + sx * r[0] * 0.02, fy, ez - r[2] * 0.02), (r[0] * 0.20, 0.012, r[2] * 0.27), mi=1)   # iris
            box(bm, (ex + sx * r[0] * 0.02, fy + 0.002, ez - r[2] * 0.02), (r[0] * 0.08, 0.012, r[2] * 0.12), mi=2)  # pupil
            box(bm, (ex - sx * r[0] * 0.04, fy + 0.004, ez + r[2] * 0.08), (r[0] * 0.06, 0.012, r[2] * 0.06), mi=0)  # highlight
            box(bm, (ex, fy - 0.004, ez + r[2] * 0.16), (r[0] * 0.38, 0.014, r[2] * 0.05), mi=2)                # upper lash line
        box(bm, (ex, fy - 0.012, ez + r[2] * 0.33), (r[0] * 0.34, 0.012, r[2] * 0.045), mi=2)                  # brow
    box(bm, (c[0], fy - 0.02, c[2] - r[2] * 0.52), (r[0] * (0.22 if not mouth_open else 0.18), 0.012, r[2] * (0.03 if not mouth_open else 0.07)), mi=3)
    box(bm, (c[0], fy + 0.005, c[2] - r[2] * 0.25), (r[0] * 0.05, 0.02, r[2] * 0.04), mi=4)                     # nose shade
    return obj_from_bm(name, bm, [M["eye_white"], M[iris], M["eye"], M["mouth"], M["skin_shade"]])

def kid_eren(M, loc, rot_z):
    """Eren (age 10) asleep sitting against the tree, legs out, head tilted."""
    skin = [("E", (0.03, -0.06, 0.80), (0.095, 0.10, 0.11)),
            ("C", (0, -0.07, 0.66), (0.02, -0.06, 0.72), 0.04),
            ("E", (0.10, 0.20, 0.25), (0.035, 0.05, 0.03)), ("E", (-0.10, 0.20, 0.25), (0.035, 0.05, 0.03))]
    shirt = [("E", (0, -0.07, 0.47), (0.145, 0.095, 0.20), (-0.25, 0, 0)),
             ("C", (0.15, -0.07, 0.6), (0.16, 0.05, 0.36), 0.045), ("C", (-0.15, -0.07, 0.6), (-0.16, 0.05, 0.36), 0.045),
             ("C", (0.16, 0.05, 0.36), (0.11, 0.17, 0.26), 0.04), ("C", (-0.16, 0.05, 0.36), (-0.11, 0.17, 0.26), 0.04)]
    pants = [("E", (0, 0.0, 0.17), (0.14, 0.12, 0.08)),
             ("C", (0.075, 0.02, 0.13), (0.085, 0.42, 0.10), 0.062), ("C", (-0.075, 0.02, 0.13), (-0.10, 0.42, 0.10), 0.062),
             ("C", (0.085, 0.42, 0.10), (0.10, 0.80, 0.07), 0.05), ("C", (-0.10, 0.42, 0.10), (-0.14, 0.79, 0.07), 0.05)]
    boots = [("E", (0.10, 0.86, 0.08), (0.045, 0.09, 0.06), (0.5, 0, 0)), ("E", (-0.14, 0.85, 0.08), (0.045, 0.09, 0.06), (0.5, 0, 0.3))]
    hair = [("E", (0.03, -0.09, 0.84), (0.105, 0.105, 0.10)), ("E", (0.03, 0.0, 0.88), (0.085, 0.06, 0.05)),
            ("E", (0.10, -0.07, 0.83), (0.03, 0.07, 0.07)), ("E", (-0.04, -0.07, 0.83), (0.03, 0.07, 0.07))]
    hair += [("E", (0.03, 0.02, 0.87), (0.09, 0.035, 0.04)), ("E", (-0.02, 0.03, 0.85), (0.03, 0.03, 0.045)),
             ("E", (0.08, 0.03, 0.85), (0.03, 0.03, 0.045))]
    obs = [face_features("ErenFace", M, (0.03, -0.06, 0.80), (0.095, 0.10, 0.11), closed=True),
           mb_figure("ErenSkin", skin, M["skin"], 0.012), mb_figure("ErenShirt", shirt, M["shirt_eren"], 0.012),
           mb_figure("ErenPants", pants, M["pants_eren"], 0.012), mb_figure("ErenBoots", boots, M["boots"], 0.012),
           mb_figure("ErenHair", hair, M["hair_eren"], 0.012)]
    return group(obs, loc, rot_z)

def kid_mikasa(M, loc, rot_z):
    """Mikasa (age 10) standing, leaning forward to wake him; red scarf, firewood on her back."""
    skin = [("E", (0, 0.05, 1.22), (0.09, 0.095, 0.105)), ("C", (0, 0.02, 1.06), (0, 0.03, 1.14), 0.035),
            ("E", (0.13, 0.20, 0.72), (0.03, 0.04, 0.045)), ("E", (-0.16, 0.05, 0.66), (0.03, 0.04, 0.045)),
            ("C", (0.06, 0.02, 0.05), (0.06, 0.02, 0.32), 0.035), ("C", (-0.06, -0.02, 0.05), (-0.06, -0.02, 0.32), 0.035)]
    top = [("E", (0, 0.02, 0.90), (0.12, 0.08, 0.17), (0.15, 0, 0)),
           ("C", (0.13, 0.03, 1.02), (0.15, 0.13, 0.84), 0.04), ("C", (0.15, 0.13, 0.84), (0.13, 0.20, 0.74), 0.035),
           ("C", (-0.13, 0.0, 1.02), (-0.16, 0.02, 0.82), 0.04), ("C", (-0.16, 0.02, 0.82), (-0.16, 0.05, 0.69), 0.035)]
    skirt = [("E", (0, 0.0, 0.64), (0.14, 0.11, 0.12)), ("E", (0, 0.0, 0.42), (0.18, 0.15, 0.16)), ("E", (0, 0.0, 0.22), (0.19, 0.16, 0.12))]
    shoes = [("E", (0.06, 0.05, 0.03), (0.04, 0.08, 0.03)), ("E", (-0.06, 0.01, 0.03), (0.04, 0.08, 0.03))]
    hair = [("E", (0, 0.02, 1.25), (0.105, 0.105, 0.11)), ("E", (0, 0.06, 1.31), (0.09, 0.08, 0.05)),
            ("E", (0.085, 0.04, 1.17), (0.03, 0.07, 0.09)), ("E", (-0.085, 0.04, 1.17), (0.03, 0.07, 0.09)),
            ("E", (0, -0.03, 1.17), (0.09, 0.05, 0.09)), ("E", (0, 0.11, 1.29), (0.085, 0.035, 0.035)),
            ("E", (0.06, 0.12, 1.25), (0.025, 0.025, 0.05)), ("E", (-0.06, 0.12, 1.25), (0.025, 0.025, 0.05))]
    scarf = [("C", (-0.09, 0.0, 1.08), (0.09, 0.0, 1.08), 0.05), ("E", (0, 0.07, 1.06), (0.08, 0.04, 0.05)),
             ("E", (0, -0.06, 1.07), (0.09, 0.04, 0.05)), ("C", (0.05, 0.08, 1.05), (0.07, 0.11, 0.86), 0.03)]
    obs = [face_features("MikasaFace", M, (0, 0.05, 1.22), (0.09, 0.095, 0.105), iris="eye_grey"),
           mb_figure("MikasaSkin", skin, M["skin"], 0.012), mb_figure("MikasaTop", top, M["shirt_mikasa"], 0.012),
           mb_figure("MikasaSkirt", skirt, M["skirt_mikasa"], 0.012), mb_figure("MikasaShoes", shoes, M["boots"], 0.012),
           mb_figure("MikasaHair", hair, M["hair_black"], 0.012), mb_figure("MikasaScarf", scarf, M["scarf"], 0.012)]
    # firewood bundle on a back frame
    bm = bmesh.new()
    rnd = random.Random(4)
    for sx in (-0.11, 0.11):                                            # carrying frame
        cyl(bm, (sx, -0.15, 0.55), (sx, -0.15, 1.30), 0.012, seg=5, mi=1)
    for z in (0.62, 0.95):
        cyl(bm, (-0.13, -0.15, z), (0.13, -0.15, z), 0.01, seg=5, mi=1)
    for i in range(16):                                                 # bundle of thin branches
        z = rnd.uniform(0.66, 1.0); y = -0.2 - rnd.uniform(0, 0.10)
        cyl(bm, (-0.32, y, z + rnd.uniform(-0.03, 0.03)), (0.32, y + rnd.uniform(-0.03, 0.03), z), rnd.uniform(0.012, 0.022), seg=5, mi=0)
    for sx in (-0.07, 0.07):                                            # straps
        cyl(bm, (sx, -0.13, 1.02), (sx, 0.07, 1.0), 0.008, seg=4, mi=1)
    obs.append(obj_from_bm("MikasaWood", bm, [M["firewood"], M["gate"]]))
    return group(obs, loc, rot_z)

def firewood_pile(M, loc, rot_z):
    bm = bmesh.new(); rnd = random.Random(8)
    for i in range(14):
        x, y = rnd.uniform(-0.3, 0.3), rnd.uniform(-0.2, 0.2)
        z = 0.04 + (i // 5) * 0.06
        cyl(bm, (x - 0.32, y, z), (x + 0.32, y + rnd.uniform(-0.05, 0.05), z), 0.025, seg=6)
    cyl(bm, (-0.1, -0.25, 0.04), (-0.1, 0.25, 0.04), 0.012, seg=4)
    ob = obj_from_bm("Firewood", bm, [M["firewood"]])
    ob.location = loc; ob.rotation_euler.z = rot_z
    return ob

# ---------------------------------------------------------------- the hill tree + grass
def hill_tree(mats):
    bm = bmesh.new()
    rnd = random.Random(11)
    cyl(bm, (0, 0, -0.5), (0.3, 0.2, 9), 1.5, 0.9, seg=14, mi=0)
    for k in range(5):                                                  # roots
        a = k / 5 * math.tau + rnd.uniform(-0.3, 0.3)
        cyl(bm, (math.cos(a) * 2.0, math.sin(a) * 2.0, -0.25), (math.cos(a) * 0.6, math.sin(a) * 0.6, 1.2), 0.28, 0.18, seg=6, mi=0)
    limbs = []
    for k in range(6):
        a = k / 6 * math.tau + rnd.uniform(-0.4, 0.4)
        p0 = Vector((0.3, 0.2, rnd.uniform(6.5, 8.5)))
        p1 = p0 + Vector((math.cos(a) * rnd.uniform(4, 6.5), math.sin(a) * rnd.uniform(4, 6.5), rnd.uniform(2.5, 4.5)))
        cyl(bm, p0, p1, 0.5, 0.2, seg=7, mi=0); limbs.append(p1)
    n0 = len(bm.faces)
    centers = limbs + [Vector((0.3, 0.2, 13.5))]
    for c0 in centers:
        for i in range(3):
            c = bmesh.ops.create_icosphere(bm, subdivisions=4, radius=rnd.uniform(2.8, 4.0))
            off = c0 + Vector((rnd.uniform(-1.8, 1.8), rnd.uniform(-1.8, 1.8), rnd.uniform(-0.5, 1.5)))
            for v in c["verts"]:
                v.co.z *= 0.8; v.co += off
                v.co += Vector((noise.noise(v.co * 0.8), noise.noise(v.co * 0.8 + Vector((3, 1, 0))), noise.noise(v.co * 0.8 + Vector((7, 2, 1))))) * 0.7
    for i, f in enumerate(bm.faces):
        f.material_index = 1 if i >= n0 else 0
        f.smooth = True
    ob = obj_from_bm("HillTree", bm, [mats["bark"], mats["leaf_hill"]])
    ob.location = (HILL.x, HILL.y, height(HILL.x, HILL.y) - 0.3)
    return ob

def grass_patch(mats, center, radius, density):
    """Instanced grass blades on a local terrain disc, for the close-up at the tree."""
    bm = bmesh.new()
    n = 48
    rings = 24
    vs = [[None] * n for _ in range(rings + 1)]
    cv = bm.verts.new((center.x, center.y, height(center.x, center.y) + 0.02))
    for r in range(1, rings + 1):
        for k in range(n):
            a = k / n * math.tau; rr = radius * r / rings
            x, y = center.x + math.cos(a) * rr, center.y + math.sin(a) * rr
            vs[r][k] = bm.verts.new((x, y, height(x, y) + 0.02))
    for k in range(n):
        bm.faces.new((cv, vs[1][k], vs[1][(k + 1) % n]))
    for r in range(1, rings):
        for k in range(n):
            bm.faces.new((vs[r][k], vs[r + 1][k], vs[r + 1][(k + 1) % n], vs[r][(k + 1) % n]))
    ground = obj_from_bm("GrassGround", bm, [mats["grass_close"]])
    bb = bmesh.new()
    for i in range(3):
        a = i / 3 * math.pi
        v0 = bb.verts.new((math.cos(a) * 0.012, math.sin(a) * 0.012, 0)); v1 = bb.verts.new((-math.cos(a) * 0.012, -math.sin(a) * 0.012, 0))
        v2 = bb.verts.new((0.01, 0.0, 0.055))
        bb.faces.new((v0, v1, v2))
    blade = obj_from_bm("Blade", bb, [mats["grass_blade"]])
    bc = new_coll("GrassBlade", hide=False); bpy.context.scene.collection.objects.unlink(blade); bc.objects.link(blade)
    bpy.context.view_layer.layer_collection.children["GrassBlade"].exclude = True
    ng = bpy.data.node_groups.new("GrassGN", "GeometryNodeTree")
    ng.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    N = ng.nodes; L = ng.links
    gi = N.new("NodeGroupInput"); go = N.new("NodeGroupOutput")
    dp = N.new("GeometryNodeDistributePointsOnFaces"); dp.inputs["Density"].default_value = density
    L.new(gi.outputs[0], dp.inputs["Mesh"])
    pos = N.new("GeometryNodeInputPosition")
    dc = N.new("ShaderNodeVectorMath"); dc.operation = "DISTANCE"; dc.inputs[1].default_value = (center.x, center.y, 0)
    fl = N.new("ShaderNodeCombineXYZ"); sp = N.new("ShaderNodeSeparateXYZ"); L.new(pos.outputs[0], sp.inputs[0])
    L.new(sp.outputs["X"], fl.inputs["X"]); L.new(sp.outputs["Y"], fl.inputs["Y"]); L.new(fl.outputs[0], dc.inputs[0])
    fall = N.new("ShaderNodeMapRange"); fall.inputs["From Min"].default_value = radius * 0.45; fall.inputs["From Max"].default_value = radius
    fall.inputs["To Min"].default_value = 1.0; fall.inputs["To Max"].default_value = 0.0
    L.new(dc.outputs["Value"], fall.inputs["Value"])
    rnd_k = N.new("FunctionNodeRandomValue"); rnd_k.data_type = "FLOAT"
    keep = N.new("FunctionNodeCompare"); keep.operation = "LESS_THAN"
    L.new(rnd_k.outputs["Value"], keep.inputs[0]); L.new(fall.outputs["Result"], keep.inputs[1])
    ci = N.new("GeometryNodeObjectInfo"); ci.inputs["Object"].default_value = blade
    iop = N.new("GeometryNodeInstanceOnPoints")
    rr = N.new("FunctionNodeRandomValue"); rr.data_type = "FLOAT_VECTOR"
    rr.inputs["Min"].default_value = (-0.25, -0.25, 0); rr.inputs["Max"].default_value = (0.25, 0.25, 6.28)
    rs = N.new("FunctionNodeRandomValue"); rs.data_type = "FLOAT"; rs.inputs["Min"].default_value = 0.6; rs.inputs["Max"].default_value = 1.6
    L.new(dp.outputs["Points"], iop.inputs["Points"]); L.new(ci.outputs["Geometry"], iop.inputs["Instance"])
    L.new(keep.outputs[0], iop.inputs["Selection"])
    L.new(rr.outputs["Value"], iop.inputs["Rotation"]); L.new(rs.outputs["Value"], iop.inputs["Scale"])
    jg = N.new("GeometryNodeJoinGeometry"); L.new(gi.outputs[0], jg.inputs[0]); L.new(iop.outputs[0], jg.inputs[0])
    L.new(jg.outputs[0], go.inputs[0])
    ground.modifiers.new("Grass", "NODES").node_group = ng
    return ground

# ---------------------------------------------------------------- roads & water
def flat_strip(name, pts, width, m, z=0.15, absolute=False):
    """Ribbon along a polyline with shared vertices (no bow-ties at bends)."""
    bm = bmesh.new()
    n = len(pts)
    left, right = [], []
    for k in range(n):
        a = Vector(pts[max(k - 1, 0)]); b = Vector(pts[min(k + 1, n - 1)])
        t = (b - a)
        if t.length == 0:
            continue
        t.normalize(); nrm = Vector((-t.y, t.x)) * width / 2
        p = Vector(pts[k])
        zz = z if absolute else height(*p) + z
        left.append(bm.verts.new((*(p + nrm), zz)))
        right.append(bm.verts.new((*(p - nrm), zz)))
    for k in range(len(left) - 1):
        f = bm.faces.new((left[k], right[k], right[k + 1], left[k + 1]))
        f.normal_update()
        if f.normal.z < 0:
            f.normal_flip()
    return obj_from_bm(name, bm, [m])

def disc_patch(name, x, y, rx, ry, rot, m, z=0.12, round_=False):
    bm = bmesh.new()
    if round_:
        r = bmesh.ops.create_circle(bm, cap_ends=True, segments=48, radius=1)
    else:
        r = bmesh.ops.create_grid(bm, x_segments=6, y_segments=6, size=1)
    for v in r["verts"]:
        v.co = Vector((v.co.x * rx, v.co.y * ry, 0))
        v.co.rotate(Euler((0, 0, rot)))
        v.co.x += x; v.co.y += y
        v.co.z = height(v.co.x, v.co.y) + z
    return obj_from_bm(name, bm, [m])

def canal(M):
    """Straight canal through the district (water gates in both walls), continuing as a river outside."""
    north = [(CX + math.sin(t / 5) * 60 * min(1, t / 6), 8 + t * 40) for t in range(0, 70)][::-1]
    inside = [(CX, y) for y in range(0, int(CANAL_FAR[1]) - 1, -10)]
    south = [(CX + math.sin(t / 4) * 140 * min(1, t / 5), CANAL_FAR[1] - t * 40) for t in range(1, 50)]
    flat_strip("CanalWaterN", north + inside[:1], CANAL_W, M["water"], z=2.2)
    flat_strip("CanalWater", inside, CANAL_W, M["water"], z=0.13, absolute=True)
    flat_strip("CanalWaterS", inside[-1:] + south, CANAL_W, M["water"], z=2.2)
    for side in (-1, 1):
        flat_strip(f"CanalBank{side}", [(x + side * (CANAL_W / 2 + 1.2), y) for x, y in inside], 2.6, M["cobble"], z=0.3, absolute=True)

# ---------------------------------------------------------------- scene
def build(year):
    reset()
    sc = bpy.context.scene
    M = {
        "grass": mat("Grass", (0.075, 0.17, 0.035), 0.95, var=0.18, var_scale=0.004, color2=(0.13, 0.24, 0.05)),
        "stone": wall_mat(),
        "stone_light": mat("StoneLight", (0.62, 0.60, 0.55), 0.85, var=0.15, var_scale=0.3),
        "iron": mat("Iron", (0.035, 0.035, 0.04), 0.45),
        "gate": mat("GateWood", (0.17, 0.11, 0.07), 0.7, var=0.2, var_scale=0.8),
        "window": mat("Window", (0.05, 0.04, 0.035), 0.6),
        "plaster": mat("Plaster", (0.80, 0.74, 0.62), 0.9),
        "plaster_w": mat("PlasterW", (0.86, 0.84, 0.78), 0.9),
        "plaster_o": mat("PlasterO", (0.78, 0.62, 0.42), 0.9),
        "timber": mat("Timber", (0.55, 0.42, 0.30), 0.9),
        "roof_red": mat("RoofRed", (0.40, 0.14, 0.07), 0.7, var=0.18, var_scale=0.3, color2=(0.5, 0.2, 0.1)),
        "roof_brown": mat("RoofBrown", (0.26, 0.13, 0.07), 0.7, var=0.18, var_scale=0.3),
        "roof_dark": mat("RoofDark", (0.30, 0.09, 0.06), 0.7, var=0.18, var_scale=0.3),
        "roof_orange": mat("RoofOrange", (0.48, 0.22, 0.08), 0.7, var=0.18, var_scale=0.3),
        "roof_slate": mat("RoofSlate", (0.20, 0.22, 0.25), 0.6),
        "bark": mat("Bark", (0.16, 0.11, 0.075), 0.9, bump=0.4, scale=3.0, var=0.2, var_scale=2.0),
        "bark_giant": mat("BarkGiant", (0.20, 0.13, 0.08), 0.9, bump=0.6, scale=0.6, var=0.25, var_scale=0.3, color2=(0.30, 0.22, 0.14)),
        "leaf": mat("Leaf", (0.13, 0.27, 0.06), 0.85, var=0.2, var_scale=0.5, color2=(0.22, 0.36, 0.08)),
        "leaf2": mat("Leaf2", (0.08, 0.20, 0.04), 0.85, var=0.2, var_scale=0.5, color2=(0.14, 0.28, 0.05)),
        "leaf3": mat("Leaf3", (0.18, 0.28, 0.07), 0.85, var=0.2, var_scale=0.5, color2=(0.26, 0.34, 0.09)),
        "leaf_dark": mat("LeafDark", (0.025, 0.085, 0.035), 0.85, var=0.2, var_scale=0.3, color2=(0.05, 0.13, 0.05)),
        "leaf_giant": mat("LeafGiant", (0.03, 0.10, 0.03), 0.85, var=0.25, var_scale=0.08, color2=(0.07, 0.17, 0.04)),
        "leaf_hill": mat("LeafHill", (0.12, 0.28, 0.05), 0.8, var=0.3, var_scale=0.6, color2=(0.28, 0.44, 0.09)),
        "grass_close": mat("GrassClose", (0.16, 0.28, 0.05), 0.95, var=0.2, var_scale=0.3, color2=(0.26, 0.36, 0.08)),
        "grass_blade": mat("GrassBlade", (0.20, 0.36, 0.06), 0.7, var=0.25, var_scale=0.4, color2=(0.34, 0.44, 0.10)),
        "dirt": mat("Dirt", (0.20, 0.17, 0.11), 0.95, var=0.25, var_scale=0.05, color2=(0.27, 0.24, 0.15)),
        "cobble": mat("Cobble", (0.42, 0.38, 0.32), 0.9, var=0.2, var_scale=0.2),
        "water": mat("Water", (0.10, 0.17, 0.22), 0.06),
        "skin": mat("Skin", (0.80, 0.55, 0.42), 0.55, sss=0.15),
        "titan_skin": mat("TitanSkin", (0.72, 0.42, 0.31), 0.6, var=0.12, var_scale=0.15, color2=(0.80, 0.50, 0.38), sss=0.1),
        "teeth": mat("Teeth", (0.85, 0.80, 0.70), 0.4),
        "eye": mat("Eye", (0.02, 0.015, 0.01), 0.3),
        "eye_white": mat("EyeWhite", (0.85, 0.85, 0.82), 0.4),
        "eye_green": mat("EyeGreen", (0.05, 0.30, 0.20), 0.3),
        "eye_grey": mat("EyeGrey", (0.10, 0.10, 0.12), 0.3),
        "mouth": mat("Mouth", (0.25, 0.08, 0.07), 0.5),
        "skin_shade": mat("SkinShade", (0.62, 0.38, 0.28), 0.6),
        "hair_brown": mat("HairBrown", (0.10, 0.05, 0.025), 0.6),
        "hair_black": mat("HairBlack", (0.012, 0.012, 0.016), 0.45),
        "hair_blond": mat("HairBlond", (0.55, 0.40, 0.18), 0.6),
        "hair_eren": mat("HairEren", (0.07, 0.035, 0.018), 0.55),
        "shirt_eren": mat("ShirtEren", (0.62, 0.62, 0.52), 0.9),
        "pants_eren": mat("PantsEren", (0.16, 0.11, 0.06), 0.9),
        "boots": mat("Boots", (0.08, 0.05, 0.03), 0.7),
        "shirt_mikasa": mat("ShirtMikasa", (0.78, 0.74, 0.66), 0.9),
        "skirt_mikasa": mat("SkirtMikasa", (0.10, 0.075, 0.06), 0.9),
        "scarf": mat("Scarf", (0.50, 0.025, 0.02), 0.85),
        "firewood": mat("Firewood", (0.30, 0.20, 0.12), 0.9),
    }
    terrain = build_terrain(M)
    build_walls(M)
    hc = new_coll("HouseVariants")
    walls = ["plaster", "plaster_w", "plaster_o", "timber"]
    roofs = ["roof_red", "roof_brown", "roof_dark", "roof_orange", "roof_red"]
    widths = []
    for i in range(40):
        w = random.uniform(7.5, 11); d = random.uniform(11, 15); h = random.choice((8, 11, 11, 14, 14, 17))
        me = house_mesh(f"H{i}", w, d, h, d * 0.45, M, walls[i % 4], roofs[(i // 4) % 5], chimney=i % 3 == 0, hip=i % 5 == 0)
        hc.objects.link(bpy.data.objects.new(f"H{i}", me))
        widths.append((w, d))
    pts, ttrees = town_points(len(widths), widths)
    scatter("Town", hc, pts, year)
    ch = bpy.data.objects.new("Church", church_mesh(M)); sc.collection.objects.link(ch)
    ch.location = (110, -200, 0)
    mo = bpy.data.objects.new("Monument", monument_mesh(M)); sc.collection.objects.link(mo)
    mo.location = (PLAZA[0], PLAZA[1], 0)
    tc = new_coll("TreeVariants")
    for i, k in enumerate(["broad"] * 7 + ["conifer"] * 6):
        tc.objects.link(bpy.data.objects.new(f"T{i:02d}", tree_mesh(f"T{i:02d}", k, M, i)))
    gn_forest(terrain, tc)
    scatter("TownTrees", tc, ttrees, year)
    # the prototypes themselves would render at the origin (= inside the inner gate); instancing resets their transforms
    for o in list(hc.objects) + list(tc.objects):
        o.location = (0.0, 0.0, -5000.0)
    giant_forest(M)
    if "hill" not in REPLACED:
        hill_tree(M)
    for k, (spts, hw) in enumerate(street_network()):
        flat_strip(f"Street{k}", spts, hw * 2, M["cobble"], z=0.10 + k * 0.002)
    flat_strip("RoadNorth", [(0, 6)] + [(math.sin(t / 9) * 120 * (t / 40), 6 + t * 120) for t in range(1, 60)], 9, M["dirt"])
    if "hill" not in REPLACED:
        flat_strip("RoadHill", [(0, 300), (90, 520), (220, 700), (HILL.x - 20, HILL.y - 60)], 3, M["dirt"], z=0.2)
    flat_strip("RoadOut", [OUTER_GATE] + [(math.sin(t / 7) * 90 * (t / 30), OUTER_GATE[1] - t * 120) for t in range(1, 50)], 8, M["dirt"])
    bmd = bmesh.new()
    cverts = [bmd.verts.new((x * 0.995, y * 0.995 + (0 if y > -1 else 0), 0.08)) for x, y in district_outline(10.0)]
    bmd.faces.new(cverts)
    obj_from_bm("DistrictGround", bmd, [M["dirt"]])
    disc_patch("Plaza", PLAZA[0], PLAZA[1], PLAZA[2], PLAZA[2], 0, M["cobble"], 0.17, round_=True)
    disc_patch("GateSquare", 0, -36, 54, 22, 0, M["cobble"], 0.17)
    disc_patch("OuterSquare", 0, OUTER_GATE[1] + 30, 34, 30, 0, M["cobble"], 0.17)
    canal(M)
    # titans roaming outside the outer gate
    oy = OUTER_GATE[1]
    for i, (H, x, y, r) in ([] if "titans" in REPLACED else enumerate([(15, -140, -170, 3.6), (7, 90, -110, 2.6), (12, 250, -300, 3.4), (4, -30, -70, 0.3),
                                      (9, -320, -250, 2.4), (13, 110, -470, 3.0), (6, 380, -140, 4.0), (10, -230, -420, 3.9)])):
        titan(f"Titan{chr(65 + i)}", M, i + 3, H, (x, oy + y), r)
    if "kids" not in REPLACED:
        # Eren asleep under the tree, Mikasa standing over him (episode 1 opening)
        tz = height(HILL.x, HILL.y)
        e_loc = Vector((HILL.x + 1.2, HILL.y - 1.5, 0)); e_loc.z = height(e_loc.x, e_loc.y) - 0.05
        kid_eren(M, e_loc, math.radians(-145))
        m_loc = Vector((e_loc.x - 0.42, e_loc.y - 1.14, 0)); m_loc.z = height(m_loc.x, m_loc.y) - 0.02
        kid_mikasa(M, m_loc, math.radians(-55))
        firewood_pile(M, (HILL.x + 2.1, HILL.y - 0.9, height(HILL.x + 2.1, HILL.y - 0.9) + 0.02), 0.6)
        M["grass_close"] = terrain.data.materials[0]
        grass_patch(M, Vector((HILL.x + 1.5, HILL.y - 2.0)), 18.0, float(os.environ.get("GRASS_DENS", "420")))
    # world / light
    w = bpy.data.worlds.new("Sky"); sc.world = w; w.use_nodes = True
    nt = w.node_tree; sky = nt.nodes.new("ShaderNodeTexSky")
    types = sky.bl_rna.properties["sky_type"].enum_items.keys()
    sky.sky_type = "MULTIPLE_SCATTERING" if "MULTIPLE_SCATTERING" in types else "NISHITA"
    sky.sun_elevation = math.radians(40); sky.sun_rotation = math.radians(115); sky.air_density = 1.4
    if hasattr(sky, "sun_disc"): sky.sun_disc = False
    if hasattr(sky, "dust_density"): sky.dust_density = 2.5
    if hasattr(sky, "aerosol_density"): sky.aerosol_density = 1.5
    nt.links.new(sky.outputs[0], nt.nodes["Background"].inputs[0])
    tcw = nt.nodes.new("ShaderNodeTexCoord"); sz = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tcw.outputs["Generated"], sz.inputs[0])
    gr = nt.nodes.new("ShaderNodeValToRGB"); ge = gr.color_ramp.elements
    ge[0].position, ge[0].color = 0.0, (0.70, 0.80, 0.90, 1)
    ge[1].position, ge[1].color = 0.40, (0.18, 0.38, 0.78, 1)
    nt.links.new(sz.outputs["Z"], gr.inputs[0])
    bg2 = nt.nodes.new("ShaderNodeBackground"); bg2.inputs[1].default_value = float(os.environ.get("SKYB", "4.0"))
    nt.links.new(gr.outputs[0], bg2.inputs[0])
    lp = nt.nodes.new("ShaderNodeLightPath"); mx = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(lp.outputs["Is Camera Ray"], mx.inputs[0])
    nt.links.new(nt.nodes["Background"].outputs[0], mx.inputs[1]); nt.links.new(bg2.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], nt.nodes["World Output"].inputs[0])
    nt.nodes["Background"].inputs[1].default_value = 0.25
    # sun from the east-north-east so the wall shadows fall to the west, as in the reference still
    sun = bpy.data.lights.new("Sun", "SUN"); sun.energy = float(os.environ.get("SUN_E", "3.6")); sun.angle = math.radians(1.5)
    so = bpy.data.objects.new("Sun", sun); sc.collection.objects.link(so)
    el, az = math.radians(38), math.radians(float(os.environ.get("SUN_AZ", "25")))
    d = Vector((-math.cos(el) * math.cos(az), -math.cos(el) * math.sin(az), -math.sin(el)))
    so.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 230)); hz = bpy.context.active_object
    hz.name = "Haze"; hz.scale = (18000, 18000, 540)       # bottom below the flat ground: no coplanar faces
    hm = bpy.data.materials.new("Haze"); hm.use_nodes = True
    hn = hm.node_tree; hn.nodes.remove(hn.nodes["Principled BSDF"])
    pv = hn.nodes.new("ShaderNodeVolumePrincipled"); pv.inputs["Density"].default_value = float(os.environ.get("HAZE", "0.000004"))
    pv.inputs["Color"].default_value = (0.75, 0.83, 0.95, 1)
    hn.links.new(pv.outputs[0], hn.nodes["Material Output"].inputs["Volume"])
    hz.data.materials.append(hm)
    ctx = {"terrain": terrain, "height": height, "year": year, "sun": so, "world": w}
    for p in PLUGINS:
        if hasattr(p, "build"):
            try:
                p.build(M, year, ctx)
            except Exception as ex:
                import traceback; traceback.print_exc()
                print(f"[plugin {p.__name__}] build failed: {ex!r}")
    return M

E_POS = Vector((HILL.x + 1.2, HILL.y - 1.5))
CAMS = {
    # name: (location, look-at, lens)
    "overview": ((-330, 600, 660), (40, -400, 0), 30),          # matches the reference still
    "titan":    ((-120, OUTER_GATE[1] - 232, 6), (-140, OUTER_GATE[1] - 170, 9.5), 30),
    "zoom":     ((-200, 1100, 380), (HILL.x, HILL.y, 20), 35),   # halfway into the close-up
    "eren":     None,                                            # computed in camera()
    "eren_wide": None,
    "walltop":  ((-W - 14, -120, WALL_H + 16), (-W + 30, -700, WALL_H - 10), 30),
    "outer":    ((20, OUTER_GATE[1] - 640, 16), (-10, OUTER_GATE[1] - 80, 20), 40),
    "giants":   ((GF.x + 1250, GF.y - 650, 30), (GF.x + 400, GF.y - 200, 75), 26),
    "gate":     ((90, 260, 60), (0, 0, 22), 30),
    "colossal": ((160, OUTER_GATE[1] + 350, 120), (0, OUTER_GATE[1] - 30, 52), 30),
}

# plug-ins import this module as `aotlib` to reuse its helpers (box, cyl, mat, mb_figure, height, constants...)
sys.modules.setdefault("aotlib", sys.modules[__name__])
import importlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
for _n in os.environ.get("AOT_PLUGINS", "").split(","):
    if _n and os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), _n + ".py")):
        try:
            PLUGINS.append(importlib.import_module(_n))
        except Exception as ex:                       # a broken plug-in must not kill the base scene
            print(f"[plugin {_n}] import failed: {ex!r}")
REPLACED.update(*[getattr(p, "REPLACES", set()) for p in PLUGINS])

for _p in PLUGINS:
    CAMS.update(getattr(_p, "CAMS", {}))

def camera(name):
    if callable(CAMS.get(name)):
        loc, tgt, lens = CAMS[name]()
    elif name in ("eren", "eren_wide"):
        g = height(E_POS.x, E_POS.y)
        if name == "eren":
            f = Vector((0.57, -0.82)); rt = Vector((-0.82, -0.57))
            c = E_POS + f * 2.7 - rt * 0.9
            t = E_POS + f * 0.45 + rt * 0.45
            loc = (c.x, c.y, g + 0.95); tgt = (t.x, t.y, g + 0.62); lens = 32
        else:
            loc = (E_POS.x + 9, E_POS.y + 11, g + 4.0); tgt = (E_POS.x - 25, E_POS.y - 120, g - 6); lens = 26
    else:
        loc, tgt, lens = CAMS[name]
    if name in ("eren", "eren_wide") and "kids" in REPLACED:
        pass
    cd = bpy.data.cameras.new("Cam"); cd.lens = lens; cd.clip_start = 0.05; cd.clip_end = 30000
    co = bpy.data.objects.new("Cam", cd); bpy.context.scene.collection.objects.link(co)
    co.location = loc
    co.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.camera = co
    return co

def render_setup(engine, res, samples, device):
    sc = bpy.context.scene
    w, h = map(int, res.split("x"))
    sc.render.resolution_x, sc.render.resolution_y = w, h
    eev = [e for e in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE") if e in sc.render.bl_rna.properties["engine"].enum_items.keys()]
    sc.render.engine = "CYCLES" if engine == "CYCLES" else eev[0]
    if engine == "CYCLES":
        sc.cycles.samples = samples
        sc.cycles.use_denoising = True
        sc.cycles.device = "CPU"
        if device == "GPU":
            pr = bpy.context.preferences.addons["cycles"].preferences
            for kind in ("OPTIX", "CUDA"):
                try:
                    pr.compute_device_type = kind; pr.get_devices()
                    gpus = [d for d in pr.devices if d.type == kind]
                    if gpus:
                        for d in pr.devices:
                            d.use = d.type == kind
                        sc.cycles.device = "GPU"
                        break
                except TypeError:
                    pass
        sc.cycles.volume_step_rate = 4
        sc.cycles.max_bounces = 4
        sc.cycles.volume_bounces = 2
    sc.view_settings.view_transform = os.environ.get("VT", "Standard")
    try:
        sc.view_settings.look = "AgX - Medium High Contrast"
    except TypeError:
        pass
    sc.view_settings.exposure = float(os.environ.get("EXPO", "-1.5"))

LABEL_ANCHORS = {"WALL MARIA": (-1100, 0, 50), "SHIGANSHINA DISTRICT": (60, -520, 20), "INNER GATE": (0, 0, 50),
                 "OUTER GATE": (0, -S - R, 50), "THE HILL": (HILL.x, HILL.y, None),
                 "FOREST OF GIANT TREES": (GF.x, GF.y, 120)}

for _p in PLUGINS:
    LABEL_ANCHORS.update(getattr(_p, "LABELS", {}))

def event_colossal():
    """845: the Colossal Titan's head and shoulders over the outer gate, wrapped in steam."""
    import titans
    r = titans.make_titan("colossal", seed=1)
    r.location = (OUTER_GATE[0], OUTER_GATE[1] - 32, 0)
    r.rotation_euler.z = 0.0          # faces north, into the district
    titans.steam("ColossalSteam", (OUTER_GATE[0], OUTER_GATE[1] - 30, 58), (75, 45, 40), density=0.5)

if __name__ == "__main__":
    build(A.year)
    if A.event == "colossal":
        event_colossal()
    camera(A.cam)
    render_setup(A.engine, A.res, A.samples, A.device)
    if A.labels:
        import json
        from bpy_extras.object_utils import world_to_camera_view
        sc = bpy.context.scene
        bpy.context.view_layer.update()
        out = {}
        for k, (x, y, z) in LABEL_ANCHORS.items():
            z = height(x, y) + 18 if z is None else z
            u, v, dpt = world_to_camera_view(sc, sc.camera, Vector((x, y, z)))
            if dpt > 0 and 0 <= u <= 1 and 0 <= v <= 1:
                out[k] = [u, v]
        json.dump(out, open(A.labels, "w"))
    if A.save:
        bpy.ops.wm.save_as_mainfile(filepath=A.save)
    if A.out:
        bpy.context.scene.render.filepath = A.out
        bpy.ops.render.render(write_still=True)
