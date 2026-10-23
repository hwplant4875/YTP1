"""Shiganshina District (Attack on Titan) procedural scene for the 3D timelapse.

Run:  blender -b -P scene.py -- --year 845 --out still.png [--res 1280x720] [--samples 48] [--cam overview]
Units are metres. Wall Maria runs along the x axis at y = 0; Shiganshina is the
half-circle district protruding south (y < 0). Inside Wall Maria is y > 0.
"""
import bpy, bmesh, math, random, sys, argparse
from mathutils import Vector, noise

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ap = argparse.ArgumentParser()
ap.add_argument("--year", type=float, default=845)
ap.add_argument("--out", default="")
ap.add_argument("--res", default="1280x720")
ap.add_argument("--samples", type=int, default=48)
ap.add_argument("--cam", default="overview")
ap.add_argument("--engine", default="CYCLES")
ap.add_argument("--save", default="")
A = ap.parse_args(argv)

R = 520.0          # district radius
WALL_H = 50.0      # all three walls are 50 m
WALL_T = 10.0      # wall thickness
GATE_W, GATE_H = 12.0, 18.0
random.seed(7)

# ---------------------------------------------------------------- helpers
def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def mat(name, color, rough=0.8, bump=0.0, scale=1.0, var=0.0, var_scale=0.02, color2=None):
    """Principled material with optional noise colour variation and bump."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    bsdf.inputs["Roughness"].default_value = rough
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

# ---------------------------------------------------------------- terrain
HILL = Vector((330.0, 820.0))     # Eren's tree hill (inside Wall Maria, north of the inner gate)

def height(x, y):
    d = math.hypot(x, y)
    flat = min(1.0, max(0.0, (d - 900) / 1600))          # town area flat
    h = noise.noise(Vector((x / 1400, y / 1400, 0.3))) * 38 + noise.noise(Vector((x / 380, y / 380, 1.7))) * 6
    h = h * flat
    hd = math.hypot(x - HILL.x, y - HILL.y)
    h += 26 * math.exp(-(hd / 150) ** 2)                  # the tree hill
    return h

def build_terrain(mats):
    bm = bmesh.new()
    S, N = 9000.0, 300
    # non-uniform grid: denser near the town
    def coord(i):
        t = i / N * 2 - 1
        return math.copysign(abs(t) ** 1.6, t) * S
    verts = [[bm.verts.new((coord(i), coord(j), 0)) for j in range(N + 1)] for i in range(N + 1)]
    for row in verts:
        for v in row:
            v.co.z = height(v.co.x, v.co.y)
    for i in range(N):
        for j in range(N):
            bm.faces.new((verts[i][j], verts[i + 1][j], verts[i + 1][j + 1], verts[i][j + 1]))
    for f in bm.faces:
        f.smooth = True
    ob = obj_from_bm("Terrain", bm, [mats["grass"]])
    return ob

# ---------------------------------------------------------------- walls
def wall_ring(name, pts, mats, closed=False, gaps=()):
    """Sweep a tapered wall profile along a 2D polyline. gaps = indices of segments to skip."""
    bm = bmesh.new()
    prof = [(-WALL_T / 2, 0), (WALL_T / 2, 0), (WALL_T / 2 - 1.2, WALL_H), (-WALL_T / 2 + 1.2, WALL_H)]
    n = len(pts)
    rings = []
    for k, p in enumerate(pts):
        a = pts[k - 1] if (k > 0 or closed) else p
        b = pts[(k + 1) % n] if (k < n - 1 or closed) else p
        t = (Vector(b) - Vector(a)).normalized()
        nrm = Vector((-t.y, t.x))
        rings.append([bm.verts.new((p[0] + nrm.x * o, p[1] + nrm.y * o, z - 4)) if z == 0 else
                      bm.verts.new((p[0] + nrm.x * o, p[1] + nrm.y * o, z)) for o, z in prof])
    segs = n if closed else n - 1
    for k in range(segs):
        if k in gaps:
            continue
        r0, r1 = rings[k], rings[(k + 1) % n]
        for e in range(4):
            bm.faces.new((r0[e], r0[(e + 1) % 4], r1[(e + 1) % 4], r1[e]))
    # caps at gap edges / ends
    cap_idx = set()
    for k in gaps:
        cap_idx.add(k); cap_idx.add((k + 1) % n)
    if not closed:
        cap_idx.update({0, n - 1})
    for k in cap_idx:
        bm.faces.new(rings[k])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return obj_from_bm(name, bm, [mats["stone"]])

def gatehouse(name, center, angle, mats):
    """Block that spans a wall gap above the gate opening, plus the gate door."""
    bm = bmesh.new()
    w = GATE_W + 2
    bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts:
        v.co = Vector((v.co.x * w, v.co.y * (WALL_T + 1.5), v.co.z * (WALL_H - GATE_H) + (WALL_H + GATE_H) / 2))
    door = bmesh.new()
    ob = obj_from_bm(name, bm, [mats["stone"]])
    ob.location = (center[0], center[1], 0)
    ob.rotation_euler.z = angle
    bmesh.ops.create_cube(door, size=1)
    for v in door.verts:
        v.co = Vector((v.co.x * (GATE_W + 0.4), v.co.y * 1.2, v.co.z * GATE_H + GATE_H / 2 - 2))
    d = obj_from_bm(name + "_Door", door, [mats["gate"]])
    d.location = ob.location
    d.rotation_euler.z = angle
    return ob, d

def build_walls(mats):
    # Wall Maria: very large radius (480 km in canon), so near-straight here; slight curve for depth.
    maria = []
    for i in range(-60, 61):
        x = i * 150.0
        maria.append((x, -x * x / (2 * 480000.0) * 30))   # exaggerated gentle bend
    # gap for the inner gate around x = 0 (segment between i=-1/0 and 0/1 is 150 m; use custom points)
    maria = [p for p in maria if abs(p[0]) > 1] 
    mid = len(maria) // 2
    maria.insert(mid, (GATE_W / 2 + 1, 0)); maria.insert(mid, (-GATE_W / 2 - 1, 0))
    gi = mid  # segment index between the two gate points
    wm = wall_ring("WallMaria", maria, mats, gaps={gi})
    # Shiganshina half circle, from (-R,0) through (0,-R) to (R,0); gap at the bottom for the outer gate
    arc = []
    steps = 96
    for s in range(steps + 1):
        a = math.pi + s / steps * math.pi
        arc.append((math.cos(a) * R, math.sin(a) * R + 0.0))
    # replace the bottom vertex with a gap
    half = GATE_W / 2 + 1
    ang = half / R
    arc = [p for p in arc if abs(math.atan2(p[1], p[0]) + math.pi / 2) > ang]
    k = len(arc) // 2
    arc.insert(k, (math.cos(-math.pi / 2 + ang) * R, math.sin(-math.pi / 2 + ang) * R))
    arc.insert(k, (math.cos(-math.pi / 2 - ang) * R, math.sin(-math.pi / 2 - ang) * R))
    ws = wall_ring("WallShiganshina", arc, mats, gaps={k})
    gatehouse("InnerGate", (0, 0), 0, mats)
    gatehouse("OuterGate", (0, -R), 0, mats)
    return wm, ws

# ---------------------------------------------------------------- houses
def house_mesh(name, w, d, h, roof_h, mats, wall_m, roof_m, tower=False):
    bm = bmesh.new()
    # walls box
    bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts:
        v.co = Vector((v.co.x * w, v.co.y * d, v.co.z * h + h / 2 - 0.5))
    for f in bm.faces:
        f.material_index = 0
    # gable roof prism with overhang
    o = 0.5
    p = [bm.verts.new(c) for c in [(-w / 2 - o, -d / 2 - o, h - 0.3), (w / 2 + o, -d / 2 - o, h - 0.3),
                                   (w / 2 + o, d / 2 + o, h - 0.3), (-w / 2 - o, d / 2 + o, h - 0.3),
                                   (-w / 2 - o, 0, h + roof_h), (w / 2 + o, 0, h + roof_h)]]
    for fv in [(p[0], p[1], p[5], p[4]), (p[3], p[4], p[5], p[2]), (p[0], p[4], p[3]), (p[1], p[2], p[5]), (p[0], p[3], p[2], p[1])]:
        f = bm.faces.new(fv); f.material_index = 1
    if tower:
        tb = bmesh.new()
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    me.materials.append(mats[wall_m]); me.materials.append(mats[roof_m])
    return me

def church_mesh(mats):
    bm = bmesh.new()
    def box(cx, cy, w, d, z0, z1, mi):
        r = bmesh.ops.create_cube(bm, size=1)
        for v in r["verts"]:
            v.co = Vector((cx + v.co.x * w, cy + v.co.y * d, z0 + (v.co.z + 0.5) * (z1 - z0)))
        for f in {f for v in r["verts"] for f in v.link_faces}:
            f.material_index = mi
    box(0, 0, 14, 34, 0, 16, 0)            # nave
    box(0, 20, 8, 8, 0, 34, 0)             # tower
    # nave roof
    p = [bm.verts.new(c) for c in [(-7.5, -17.5, 16), (7.5, -17.5, 16), (7.5, 17.5, 16), (-7.5, 17.5, 16), (0, -17.5, 24), (0, 17.5, 24)]]
    for fv in [(p[0], p[1], p[4]), (p[2], p[3], p[5]), (p[1], p[2], p[5], p[4]), (p[3], p[0], p[4], p[5])]:
        f = bm.faces.new(fv); f.material_index = 1
    # spire
    q = [bm.verts.new(c) for c in [(-4.2, 15.8, 34), (4.2, 15.8, 34), (4.2, 24.2, 34), (-4.2, 24.2, 34), (0, 20, 52)]]
    for fv in [(q[0], q[1], q[4]), (q[1], q[2], q[4]), (q[2], q[3], q[4]), (q[3], q[0], q[4])]:
        f = bm.faces.new(fv); f.material_index = 1
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new("Church")
    bm.to_mesh(me); bm.free()
    me.materials.append(mats["plaster_w"]); me.materials.append(mats["roof_slate"])
    return me

def tree_mesh(name, kind, mats):
    bm = bmesh.new()
    r = bmesh.ops.create_cone(bm, cap_ends=True, segments=6, radius1=0.35, radius2=0.25, depth=4)
    for v in r["verts"]:
        v.co.z += 2
    if kind == "conifer":
        c = bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=2.6, radius2=0, depth=11)
        for v in c["verts"]:
            v.co.z += 8
    else:
        c = bmesh.ops.create_icosphere(bm, subdivisions=2, radius=3.2)
        for v in c["verts"]:
            v.co.z *= 0.85; v.co.z += 6.5
            v.co += Vector((noise.noise(v.co * 0.7), noise.noise(v.co * 0.7 + Vector((5, 1, 2))), 0)) * 0.6
    leaf = set(c["verts"])
    for f in bm.faces:
        f.material_index = 1 if all(v in leaf for v in f.verts) else 0
        f.smooth = kind != "conifer"
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    me.materials.append(mats["bark"]); me.materials.append(mats["leaf" if kind != "conifer" else "leaf_dark"])
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
    ys = ng.interface.new_socket("Year", in_out="INPUT", socket_type="NodeSocketFloat")
    ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    N = ng.nodes; L = ng.links
    gi = N.new("NodeGroupInput"); go = N.new("NodeGroupOutput")
    def attr(n, t):
        a = N.new("GeometryNodeInputNamedAttribute"); a.data_type = t; a.inputs["Name"].default_value = n; return a
    born, dead = attr("born", "FLOAT"), attr("dead", "FLOAT")
    c1 = N.new("FunctionNodeCompare"); c1.operation = "LESS_EQUAL"
    L.new(born.outputs["Attribute"], c1.inputs[0]); L.new(gi.outputs["Year"], c1.inputs[1])
    c2 = N.new("FunctionNodeCompare"); c2.operation = "GREATER_THAN"
    L.new(dead.outputs["Attribute"], c2.inputs[0]); L.new(gi.outputs["Year"], c2.inputs[1])
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
    mod[ys.identifier] = float(year)
    ob["year_socket"] = ys.identifier
    return ob

# ---------------------------------------------------------------- town layout
def in_district(x, y, margin):
    return y < -margin and math.hypot(x, y) < R - margin

def on_road(x, y):
    if abs(x) < 9:                                  # main avenue, outer gate -> inner gate
        return True
    r = math.hypot(x, y)
    if abs(r - 300) < 6 or abs(r - 150) < 5:       # ring streets
        return True
    a = math.degrees(math.atan2(-y, x))            # radial streets
    for ra in (20, 45, 135, 160):
        if abs(a - ra) < 1.4 * 60 / max(r, 60):
            return True
    if -60 < y < -18 and abs(x) < 55:              # gate square
        return True
    if abs(x) < 45 and abs(y + 300) < 30:          # market square
        return True
    return False

def town_points(n_variants):
    pts = []
    step = 11.5
    rr = 26.0
    while rr < R - 22:
        circ = math.pi * rr
        k = int(circ / step)
        for i in range(k):
            a = math.pi + (i + 0.5) / k * math.pi + random.uniform(-0.15, 0.15) / rr * step
            x, y = math.cos(a) * rr, math.sin(a) * rr
            x += random.uniform(-1.5, 1.5); y += random.uniform(-1.5, 1.5)
            if not in_district(x, y, 16) or on_road(x, y):
                continue
            if random.random() < 0.06:
                continue                       # gardens / gaps
            d = math.hypot(x, y)
            # older core near the inner gate and main avenue, newer at the edges
            born = 760 + (d / R) * 60 + abs(x) / R * 20 + random.uniform(-12, 12)
            pts.append((x, y, 0, a + math.pi / 2 + random.choice((0, math.pi)) + random.uniform(-.05, .05),
                        random.uniform(0.9, 1.1), random.randrange(n_variants), born, 99999))
        rr += 13.0
    return pts

def tree_points():
    pts = []
    rnd = random.Random(3)
    for _ in range(320000):
        x, y = rnd.uniform(-7000, 7000), rnd.uniform(-7000, 7000)
        if math.hypot(x, y) < R + 40 and y < 30:
            continue
        if abs(y) < 14:                         # wall line
            continue
        if abs(x) < 10 and y > 0:               # road north
            continue
        f = noise.noise(Vector((x / 900, y / 900, 4.2)))
        outside = y < 0                         # beyond the walls = wild forest
        dens = 0.05 if outside else 0.22
        if f < dens and rnd.random() > 0.006:
            continue
        if math.hypot(x - HILL.x, y - HILL.y) < 200:
            continue
        z = height(x, y)
        pts.append((x, y, z, rnd.uniform(0, 6.28), rnd.uniform(0.8, 1.5), rnd.randrange(3), -10000, 99999))
    return pts

# ---------------------------------------------------------------- the hill tree
def hill_tree(mats):
    bm = bmesh.new()
    r = bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=1.3, radius2=0.7, depth=9)
    for v in r["verts"]:
        v.co.z += 4.5
    leaf = []
    rnd = random.Random(11)
    for i in range(9):
        c = bmesh.ops.create_icosphere(bm, subdivisions=2, radius=rnd.uniform(3.5, 5))
        off = Vector((rnd.uniform(-5, 5), rnd.uniform(-5, 5), rnd.uniform(10, 14)))
        for v in c["verts"]:
            v.co += off
        leaf += c["verts"]
    ls = set(leaf)
    for f in bm.faces:
        f.material_index = 1 if all(v in ls for v in f.verts) else 0
        f.smooth = True
    ob = obj_from_bm("HillTree", bm, [mats["bark"], mats["leaf"]])
    ob.location = (HILL.x, HILL.y, height(HILL.x, HILL.y) - 0.5)
    return ob

# ---------------------------------------------------------------- roads & fields
def flat_strip(name, pts, width, m, z=0.15):
    bm = bmesh.new()
    prev = None
    for k in range(len(pts) - 1):
        a, b = Vector(pts[k]), Vector(pts[k + 1])
        t = (b - a).normalized(); nrm = Vector((-t.y, t.x)) * width / 2
        q = [bm.verts.new((*(a + nrm), height(*a) + z)), bm.verts.new((*(a - nrm), height(*a) + z)),
             bm.verts.new((*(b - nrm), height(*b) + z)), bm.verts.new((*(b + nrm), height(*b) + z))]
        bm.faces.new(q)
    return obj_from_bm(name, bm, [m])

def disc_patch(name, x, y, rx, ry, rot, m, z=0.12):
    bm = bmesh.new()
    r = bmesh.ops.create_grid(bm, x_segments=6, y_segments=6, size=1)
    for v in r["verts"]:
        v.co = Vector((v.co.x * rx, v.co.y * ry, 0))
        v.co.rotate(__import__("mathutils").Euler((0, 0, rot)))
        v.co.x += x; v.co.y += y
        v.co.z = height(v.co.x, v.co.y) + z
    return obj_from_bm(name, bm, [m])

# ---------------------------------------------------------------- scene
def build(year):
    reset()
    sc = bpy.context.scene
    M = {
        "grass": mat("Grass", (0.075, 0.17, 0.035), 0.95, var=0.18, var_scale=0.004, color2=(0.13, 0.24, 0.05)),
        "stone": mat("WallStone", (0.36, 0.34, 0.31), 0.85, bump=0.3, scale=0.4, var=0.2, var_scale=0.05, color2=(0.48, 0.45, 0.40)),
        "gate": mat("GateWood", (0.17, 0.11, 0.07), 0.7),
        "plaster": mat("Plaster", (0.80, 0.74, 0.62), 0.9),
        "plaster_w": mat("PlasterW", (0.86, 0.84, 0.78), 0.9),
        "plaster_o": mat("PlasterO", (0.78, 0.62, 0.42), 0.9),
        "timber": mat("Timber", (0.55, 0.42, 0.30), 0.9),
        "roof_red": mat("RoofRed", (0.55, 0.20, 0.10), 0.7, var=0.15, var_scale=0.3),
        "roof_brown": mat("RoofBrown", (0.33, 0.18, 0.10), 0.7, var=0.15, var_scale=0.3),
        "roof_slate": mat("RoofSlate", (0.20, 0.22, 0.25), 0.6),
        "bark": mat("Bark", (0.18, 0.12, 0.08), 0.9),
        "leaf": mat("Leaf", (0.13, 0.27, 0.06), 0.85, var=0.2, var_scale=0.5, color2=(0.22, 0.36, 0.08)),
        "leaf_dark": mat("LeafDark", (0.05, 0.15, 0.06), 0.85),
        "dirt": mat("Dirt", (0.42, 0.34, 0.24), 0.95, var=0.2, var_scale=0.05),
        "cobble": mat("Cobble", (0.45, 0.42, 0.38), 0.9, var=0.2, var_scale=0.2),
        "water": mat("Water", (0.05, 0.12, 0.13), 0.08),
        "wheat": mat("Wheat", (0.62, 0.52, 0.22), 0.95, var=0.2, var_scale=0.05),
        "field_g": mat("FieldG", (0.30, 0.42, 0.12), 0.95),
        "field_b": mat("FieldB", (0.36, 0.27, 0.16), 0.95),
    }
    build_terrain(M)
    build_walls(M)
    # houses
    hc = new_coll("HouseVariants")
    variants = 0
    walls = ["plaster", "plaster_w", "plaster_o", "timber"]
    roofs = ["roof_red", "roof_red", "roof_brown", "roof_slate"]
    for i in range(24):
        w = random.uniform(7, 10); d = random.uniform(8, 13); h = random.choice((6.5, 9, 9, 12))
        me = house_mesh(f"H{i}", w, d, h, w * 0.55, M, walls[i % 4], roofs[(i // 4) % 4])
        o = bpy.data.objects.new(f"H{i}", me); hc.objects.link(o); variants += 1
    pts = town_points(variants)
    scatter("Town", hc, pts, year)
    ch = bpy.data.objects.new("Church", church_mesh(M)); sc.collection.objects.link(ch)
    ch.location = (70, -300, 0); ch.rotation_euler.z = 0.0
    # trees
    tc = new_coll("TreeVariants")
    for i, k in enumerate(("broad", "broad", "conifer")):
        tc.objects.link(bpy.data.objects.new(f"T{i}", tree_mesh(f"T{i}", k, M)))
    scatter("Forest", tc, tree_points(), year)
    hill_tree(M)
    # roads: avenue through the district and the road north from the inner gate
    flat_strip("Avenue", [(0, -R + 5), (0, -5)], 14, M["cobble"])
    flat_strip("RoadNorth", [(0, 6)] + [(math.sin(t / 9) * 120 * (t / 40), 6 + t * 120) for t in range(1, 60)], 9, M["dirt"])
    flat_strip("RoadOut", [(0, -R - 6)] + [(math.sin(t / 7) * 90 * (t / 30), -R - 6 - t * 120) for t in range(1, 50)], 7, M["dirt"])
    disc_patch("Market", 0, -300, 44, 28, 0, M["cobble"], 0.17)
    disc_patch("GateSquare", 0, -38, 54, 20, 0, M["cobble"], 0.17)
    # farm fields inside Wall Maria (north of the wall)
    rnd = random.Random(5)
    for i in range(160):
        x, y = rnd.uniform(-4500, 4500), rnd.uniform(120, 5000)
        if math.hypot(x - HILL.x, y - HILL.y) < 220 or abs(x) < 25:
            continue
        disc_patch(f"Field{i}", x, y, rnd.uniform(60, 160), rnd.uniform(40, 120), rnd.uniform(-.4, .4),
                   M[rnd.choice(("wheat", "field_g", "field_b", "wheat"))])
    # world / light
    w = bpy.data.worlds.new("Sky"); sc.world = w; w.use_nodes = True
    nt = w.node_tree; sky = nt.nodes.new("ShaderNodeTexSky"); sky.sky_type = "NISHITA"
    sky.sun_elevation = math.radians(28); sky.sun_rotation = math.radians(200); sky.air_density = 1.4; sky.dust_density = 2.5
    nt.links.new(sky.outputs[0], nt.nodes["Background"].inputs[0])
    nt.nodes["Background"].inputs[1].default_value = 0.22
    sun = bpy.data.lights.new("Sun", "SUN"); sun.energy = 2.2; sun.angle = math.radians(1.5)
    so = bpy.data.objects.new("Sun", sun); sc.collection.objects.link(so)
    so.rotation_euler = (math.radians(62), 0, math.radians(200 - 180 + 90))
    # aerial haze
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 250)); hz = bpy.context.active_object
    hz.name = "Haze"; hz.scale = (18000, 18000, 500)
    hm = bpy.data.materials.new("Haze"); hm.use_nodes = True
    hn = hm.node_tree; hn.nodes.remove(hn.nodes["Principled BSDF"])
    pv = hn.nodes.new("ShaderNodeVolumePrincipled"); pv.inputs["Density"].default_value = 0.000012
    pv.inputs["Color"].default_value = (0.75, 0.83, 0.95, 1)
    hn.links.new(pv.outputs[0], hn.nodes["Material Output"].inputs["Volume"])
    hz.data.materials.append(hm)
    return M

CAMS = {
    # name: (location, look-at, lens)
    "overview": ((760, 1250, 430), (0, -300, 0), 32),
    "hill":     ((420, 980, 70), (0, -250, 20), 28),
    "outer":    ((-900, -1500, 380), (0, -200, 0), 30),
}

def camera(name):
    loc, tgt, lens = CAMS[name]
    cd = bpy.data.cameras.new("Cam"); cd.lens = lens; cd.clip_end = 30000
    co = bpy.data.objects.new("Cam", cd); bpy.context.scene.collection.objects.link(co)
    co.location = loc
    co.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.camera = co
    return co

def render_setup(engine, res, samples):
    sc = bpy.context.scene
    w, h = map(int, res.split("x"))
    sc.render.resolution_x, sc.render.resolution_y = w, h
    sc.render.engine = "CYCLES" if engine == "CYCLES" else "BLENDER_EEVEE_NEXT"
    if engine == "CYCLES":
        sc.cycles.samples = samples
        sc.cycles.use_denoising = True
        sc.cycles.device = "CPU"
        sc.cycles.volume_step_rate = 4
        sc.cycles.max_bounces = 4
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Medium High Contrast"
    sc.view_settings.exposure = -0.6

if __name__ == "__main__":
    build(A.year)
    camera(A.cam)
    render_setup(A.engine, A.res, A.samples)
    if A.save:
        bpy.ops.wm.save_as_mainfile(filepath=A.save)
    if A.out:
        bpy.context.scene.render.filepath = A.out
        bpy.ops.render.render(write_still=True)
