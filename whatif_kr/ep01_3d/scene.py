# 현실파괴범 EP01 (3D): 한강공원 치맥 후 한 걸음마다 키가 2배.
# Style-frame builder: python3 scene.py <shot> <out.png> [res_pct]
import bpy, math, sys, os, random
from mathutils import Vector

ASSETS = os.environ.get("WHATIF_ASSETS", os.path.join(os.path.dirname(__file__), "assets"))
shot = sys.argv[1] if len(sys.argv) > 1 else "f1"
out = sys.argv[2] if len(sys.argv) > 2 else "/tmp/f1.png"
pct = int(sys.argv[3]) if len(sys.argv) > 3 else 50

bpy.ops.wm.read_factory_settings(use_empty=True)
S = bpy.context.scene
random.seed(7)

# ---------------- materials ----------------
def mat(name, color, rough=0.6, metal=0.0, emit=None, emit_str=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if emit:
        b.inputs["Emission Color"].default_value = (*emit, 1)
        b.inputs["Emission Strength"].default_value = emit_str
    return m

def srgb(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92 for x in c)

def building_mat(name, wall, glass_emit=0.6):
    """World-space window grid so every box gets the same 3 m floors."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    add = nt.nodes.new("ShaderNodeMath"); add.operation = "ADD"
    comb = nt.nodes.new("ShaderNodeCombineXYZ")
    brick = nt.nodes.new("ShaderNodeTexBrick")
    brick.offset = 0.0
    brick.inputs["Scale"].default_value = 1.0
    brick.inputs["Mortar Size"].default_value = 0.55
    brick.inputs["Brick Width"].default_value = 2.6
    brick.inputs["Row Height"].default_value = 3.0
    brick.inputs["Color1"].default_value = (*srgb("#2a3448"), 1)
    brick.inputs["Color2"].default_value = (*srgb("#ffcf8a"), 1)
    brick.inputs["Mortar"].default_value = (*srgb(wall), 1)
    nt.links.new(geo.outputs["Position"], sep.inputs[0])
    nt.links.new(sep.outputs["X"], add.inputs[0])
    nt.links.new(sep.outputs["Y"], add.inputs[1])
    nt.links.new(add.outputs[0], comb.inputs["X"])
    nt.links.new(sep.outputs["Z"], comb.inputs["Y"])
    nt.links.new(comb.outputs[0], brick.inputs["Vector"])
    nt.links.new(brick.outputs["Color"], b.inputs["Base Color"])
    # lit windows: a few warm ones
    noise = nt.nodes.new("ShaderNodeTexWhiteNoise")
    nt.links.new(comb.outputs[0], noise.inputs["Vector"])
    gt = nt.nodes.new("ShaderNodeMath"); gt.operation = "GREATER_THAN"; gt.inputs[1].default_value = 0.72
    nt.links.new(noise.outputs["Value"], gt.inputs[0])
    mul = nt.nodes.new("ShaderNodeMath"); mul.operation = "MULTIPLY"
    inv = nt.nodes.new("ShaderNodeMath"); inv.operation = "SUBTRACT"; inv.inputs[0].default_value = 1.0
    nt.links.new(brick.outputs["Fac"], inv.inputs[1])
    nt.links.new(gt.outputs[0], mul.inputs[0]); nt.links.new(inv.outputs[0], mul.inputs[1])
    em = nt.nodes.new("ShaderNodeMath"); em.operation = "MULTIPLY"; em.inputs[1].default_value = glass_emit
    nt.links.new(mul.outputs[0], em.inputs[0])
    b.inputs["Emission Color"].default_value = (*srgb("#ffc070"), 1)
    nt.links.new(em.outputs[0], b.inputs["Emission Strength"])
    b.inputs["Roughness"].default_value = 0.45
    return m

M = {
    "grass": mat("grass", srgb("#5f8f3e"), 0.9),
    "path": mat("path", srgb("#b9a58c"), 0.8),
    "asphalt": mat("asphalt", srgb("#3b3f45"), 0.85),
    "concrete": mat("concrete", srgb("#c8c4bd"), 0.7),
    "water": mat("water", srgb("#1c3f63"), 0.06),
    "skin": mat("skin", srgb("#f0c5a3"), 0.55),
    "hoodie": mat("hoodie", srgb("#ff6a3d"), 0.75),
    "pants": mat("pants", srgb("#25324d"), 0.8),
    "shoe": mat("shoe", srgb("#f5f5f5"), 0.5),
    "hair": mat("hair", srgb("#231c19"), 0.45),
    "matA": mat("matA", srgb("#2f6fd6"), 0.7),
    "matB": mat("matB", srgb("#f2f2f2"), 0.7),
    "box": mat("box", srgb("#f2b233"), 0.6),
    "boxR": mat("boxR", srgb("#d6402b"), 0.6),
    "can": mat("can", srgb("#c9ced6"), 0.25, 0.9),
    "canG": mat("canG", srgb("#2e7d4f"), 0.3, 0.6),
    "chicken": mat("chicken", srgb("#b8652a"), 0.5),
    "lotte": mat("lotte", srgb("#cfd8e3"), 0.15, 0.6),
    "bridge": mat("bridge", srgb("#8f99a6"), 0.6),
    "mountain": mat("mountain", srgb("#3e5a3a"), 0.95),
    "leaf": mat("leaf", srgb("#4f8a3a"), 0.8),
    "trunk": mat("trunk", srgb("#6b4a33"), 0.9),
}
BLD = [building_mat(f"bld{i}", w) for i, w in enumerate(["#d9d4cc", "#c7ccd4", "#e6e1d6", "#b9c0ca"])]

gn = M["grass"].node_tree
gnz = gn.nodes.new("ShaderNodeTexNoise"); gnz.inputs["Scale"].default_value = 0.05
gramp = gn.nodes.new("ShaderNodeValToRGB")
gramp.color_ramp.elements[0].color = (*srgb("#4e7f33"), 1); gramp.color_ramp.elements[1].color = (*srgb("#7aa64a"), 1)
gn.links.new(gnz.outputs["Fac"], gramp.inputs[0]); gn.links.new(gramp.outputs[0], gn.nodes["Principled BSDF"].inputs["Base Color"])
# water ripples
wn = M["water"].node_tree
bump = wn.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.15
nz = wn.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 0.4
wn.links.new(nz.outputs["Fac"], bump.inputs["Height"])
wn.links.new(bump.outputs["Normal"], wn.nodes["Principled BSDF"].inputs["Normal"])

# ---------------- helpers ----------------
def box(name, loc, size, m, parent=None, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object; o.name = name
    o.scale = size
    o.data.materials.append(m)
    if bevel:
        mod = o.modifiers.new("b", "BEVEL"); mod.width = bevel; mod.segments = 3
    if parent: o.parent = parent
    return o

_shared = {}
def linked_box(loc, size, m):
    key = m.name
    if key not in _shared:
        me = bpy.data.meshes.new("cube_" + key)
        import bmesh
        bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0); bm.to_mesh(me); bm.free()
        me.materials.append(m)
        _shared[key] = me
    o = bpy.data.objects.new("b", _shared[key])
    S.collection.objects.link(o)
    o.location = loc; o.scale = size
    return o

def import_glb(path, loc, scale=1.0, rot=0.0):
    bpy.ops.import_scene.gltf(filepath=path)
    objs = bpy.context.selected_objects
    root = [o for o in objs if o.parent is None]
    for r in root:
        r.location = loc; r.scale = (scale,) * 3; r.rotation_euler[2] = rot
    return root

def smooth(o, levels=2):
    for p in o.data.polygons: p.use_smooth = True
    mod = o.modifiers.new("s", "SUBSURF"); mod.levels = levels; mod.render_levels = levels

# ---------------- the person (height 1.7 m at scale 1, faceless) ----------------
def person(height, loc, rot_z=0.0, stride=0.0):
    root = bpy.data.objects.new("giant", None); S.collection.objects.link(root)
    root.location = loc; root.rotation_euler[2] = rot_z
    k = height / 1.7
    root.scale = (k, k, k)
    def part(prim, name, loc, scale, m, rot=(0, 0, 0), sub=2):
        if prim == "sphere": bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, location=loc)
        else: bpy.ops.mesh.primitive_cylinder_add(vertices=24, location=loc)
        o = bpy.context.object; o.name = name; o.scale = scale; o.rotation_euler = rot
        o.data.materials.append(m)
        for p in o.data.polygons: p.use_smooth = True
        if prim == "cyl":
            bv = o.modifiers.new("b", "BEVEL"); bv.width = 0.03; bv.segments = 4; bv.limit_method = "NONE"
        o.parent = root
        return o
    a = math.radians(stride)
    # legs (pivot at hip z=0.88)
    for side, ang in ((-1, a), (1, -a)):
        x = side * 0.085
        lz = 0.88 - 0.44 * math.cos(ang); ly = 0.44 * math.sin(ang)
        part("cyl", "leg", (x, ly, lz), (0.075, 0.075, 0.44), M["pants"], (ang, 0, 0))
        fz = 0.88 - 0.86 * math.cos(ang); fy = 0.86 * math.sin(ang)
        part("sphere", "shoe", (x, fy + 0.05, max(fz, 0.045)), (0.065, 0.13, 0.05), M["shoe"])
    # torso + hoodie
    part("cyl", "torso", (0, 0, 1.15), (0.18, 0.12, 0.3), M["hoodie"])
    part("sphere", "shoulders", (0, 0, 1.40), (0.2, 0.12, 0.08), M["hoodie"])
    part("sphere", "hood", (0, -0.07, 1.43), (0.13, 0.07, 0.07), M["hoodie"])
    # arms swing opposite to legs
    for side, ang in ((-1, -a * 0.8), (1, a * 0.8)):
        x = side * 0.235
        part("cyl", "arm", (x, 0.28 * math.sin(ang), 1.39 - 0.28 * math.cos(ang)), (0.055, 0.055, 0.28), M["hoodie"], (ang, 0, 0))
        part("sphere", "hand", (x, 0.58 * math.sin(ang), 1.40 - 0.58 * math.cos(ang)), (0.045, 0.045, 0.055), M["skin"])
    part("cyl", "neck", (0, 0, 1.5), (0.05, 0.05, 0.05), M["skin"])
    part("sphere", "head", (0, 0, 1.62), (0.105, 0.115, 0.125), M["skin"])
    part("sphere", "hair", (0, -0.012, 1.655), (0.11, 0.12, 0.105), M["hair"])
    return root

# ---------------- world ----------------
_tree_mesh = {}
def tree(loc, h):
    if not _tree_mesh:
        import bmesh
        me = bpy.data.meshes.new("canopy"); bm = bmesh.new()
        bmesh.ops.create_icosphere(bm, subdivisions=3, radius=0.5); bm.to_mesh(me); bm.free()
        for p in me.polygons: p.use_smooth = True
        me.materials.append(M["leaf"]); _tree_mesh["c"] = me
        tm = bpy.data.meshes.new("trunk"); bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=0.5, radius2=0.35, depth=1.0); bm.to_mesh(tm); bm.free()
        tm.materials.append(M["trunk"]); _tree_mesh["t"] = tm
    x, y, z = loc
    t = bpy.data.objects.new("trunk", _tree_mesh["t"]); S.collection.objects.link(t)
    t.location = (x, y, h * 0.22); t.scale = (h * 0.06, h * 0.06, h * 0.45)
    for k in range(3):
        c = bpy.data.objects.new("canopy", _tree_mesh["c"]); S.collection.objects.link(c)
        c.location = (x + random.uniform(-.15, .15) * h, y + random.uniform(-.15, .15) * h, h * (0.62 + 0.12 * k))
        r = h * random.uniform(0.42, 0.55); c.scale = (r, r, r * 0.85)

def build_world(detail=1.0):
    # park strip (north bank), river, south bank city
    box("grass", (0, -40, -0.5), (60000, 120, 1), M["grass"])
    box("path", (0, 12, -0.45), (60000, 6, 1), M["path"])
    box("bank", (0, 18, -1.2), (60000, 6, 2.5), M["concrete"])
    box("river", (0, 520, -2.0), (60000, 1000, 1), M["water"])
    box("southbank", (0, 1020, -0.6), (60000, 30, 2), M["concrete"])
    box("southland", (0, 9000, -0.5), (60000, 16000, 1), M["asphalt"])
    box("road", (0, -110, -0.48), (60000, 22, 1), M["asphalt"])
    box("northland", (0, -9000, -0.5), (60000, 17800, 1), M["asphalt"])
    # bridge across the river (Jamsil-style girder bridge)
    bx = 260
    box("deck", (bx, 520, 14), (24, 1080, 2.2), M["bridge"])
    for py in range(40, 1020, 80):
        box("pier", (bx, py, 6), (10, 4, 16), M["concrete"])
    # trees along the park
    for x in range(-600, 600, 18):
        tree((x + random.uniform(-4, 4), -28 + random.uniform(-7, 7), 0), 7 + random.uniform(-1.5, 2))
    # riverside apartments behind the park (north) and skyline across (south)
    for x in range(-6000, 6000, int(70 / detail)):
        for row in range(3):
            h = random.choice([45, 54, 66, 75])
            linked_box((x + random.uniform(-8, 8), -170 - row * 70, h / 2), (48, 14, h), random.choice(BLD))
    for gx in range(-8000, 8000, int(90 / detail)):
        for gy in range(1100, 6000, int(110 / detail)):
            if random.random() < 0.25: continue
            h = random.choice([30, 45, 60, 75, 90, 120]) * (1.5 if random.random() < 0.08 else 1)
            linked_box((gx + random.uniform(-15, 15), gy + random.uniform(-15, 15), h / 2), (random.choice([30, 45]), random.choice([14, 20, 30]), h), random.choice(BLD))
    # Lotte World Tower across the river
    bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=48, radius2=10, depth=555, location=(900, 1400, 277.5))
    lt = bpy.context.object; lt.rotation_euler[2] = math.radians(45); lt.data.materials.append(M["lotte"])
    bv = lt.modifiers.new("b", "BEVEL"); bv.width = 6; bv.segments = 4
    # distant mountains (north side, Bukhansan-ish)
    for i in range(9):
        bpy.ops.mesh.primitive_cone_add(vertices=48, radius1=2600, radius2=40, depth=700 + 120 * (i % 3), location=(-8000 + i * 2100, -9500 - (i % 2) * 1500, 300))
        o = bpy.context.object; o.data.materials.append(M["mountain"]); smooth(o, 1)

def picnic(loc):
    x, y, z = loc
    # checkered blue/white mat
    for i in range(6):
        for j in range(6):
            box("mat", (x - 0.75 + i * 0.3 + 0.15, y - 0.75 + j * 0.3 + 0.15, 0.005), (0.3, 0.3, 0.01), M["matA"] if (i + j) % 2 else M["matB"])
    box("chickenbox", (x + 0.25, y + 0.15, 0.06), (0.36, 0.3, 0.1), M["box"], bevel=0.01)
    box("lid", (x + 0.25, y + 0.44, 0.012), (0.36, 0.28, 0.02), M["boxR"], bevel=0.005)
    for (dx, dy) in [(0.18, 0.1), (0.3, 0.2), (0.22, 0.25), (0.33, 0.06)]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.04, location=(x + dx, y + dy, 0.12))
        o = bpy.context.object; o.scale = (1.4, 1, 0.8); o.data.materials.append(M["chicken"]); smooth(o, 1)
    for k, (dx, dy) in enumerate([(-0.35, 0.3), (-0.25, 0.42), (-0.45, -0.1)]):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.033, depth=0.12, location=(x + dx, y + dy, 0.06))
        o = bpy.context.object; o.data.materials.append(M["canG"] if k == 1 else M["can"])
        for p in o.data.polygons: p.use_smooth = True
    bpy.ops.mesh.primitive_cylinder_add(radius=0.033, depth=0.12, location=(x - 0.1, y - 0.45, 0.033), rotation=(math.radians(90), 0, 0.6))
    bpy.context.object.data.materials.append(M["can"])

def tiny_people(n, area, scale=1.0):
    for _ in range(n):
        x = random.uniform(*area[0]); y = random.uniform(*area[1])
        p = person(1.6 * scale + random.uniform(-0.1, 0.1), (x, y, 0), random.uniform(0, 6.28), stride=random.choice([0, 12]))
        picnic((x + 1.2, y, 0)) if random.random() < 0.25 else None

# ---------------- render setup ----------------
def setup(cam_loc, look_at, lens=24, sun_elev=7, sun_az=250):
    w = bpy.data.worlds.new("w"); S.world = w; w.use_nodes = True
    nt = w.node_tree
    sky = nt.nodes.new("ShaderNodeTexSky")
    try: sky.sky_type = "MULTIPLE_SCATTERING"
    except Exception: pass
    sky.sun_elevation = math.radians(sun_elev); sky.sun_rotation = math.radians(sun_az)
    try: sky.air_density = 1.2; sky.dust_density = 2.5
    except Exception: pass
    nt.links.new(sky.outputs[0], nt.nodes["Background"].inputs[0])
    nt.nodes["Background"].inputs[1].default_value = 0.6
    sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN")); S.collection.objects.link(sun)
    sun.data.energy = 3.0; sun.data.color = srgb("#ffc58a"); sun.data.angle = math.radians(1.5)
    sun.rotation_euler = (math.radians(90 - sun_elev), 0, math.radians(sun_az + 90))
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); S.collection.objects.link(cam)
    cam.location = cam_loc
    d = Vector(look_at) - Vector(cam_loc)
    cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = lens; cam.data.clip_start = 0.05; cam.data.clip_end = 200000
    S.camera = cam
    S.render.engine = "BLENDER_EEVEE"
    S.render.resolution_x = 1080; S.render.resolution_y = 1920; S.render.resolution_percentage = pct
    S.eevee.taa_render_samples = 24
    S.view_settings.view_transform = "AgX"; S.view_settings.look = "AgX - Punchy"
    S.render.film_transparent = False
    S.render.filepath = out
    try:
        S.world.mist_settings.start = 300
    except Exception:
        pass

# ---------------- shots ----------------
if shot == "f1":  # step 0: just stood up from the mat
    build_world(detail=0.6)
    picnic((0.9, 0.2, 0))
    person(1.7, (0, 0, 0), math.radians(-70), stride=8)
    tiny_people(10, ((-40, 40), (-14, 8)))
    setup((1.7, -2.7, 0.62), (-0.35, 0.9, 1.05), lens=22, sun_elev=2, sun_az=320)
elif shot == "f2":  # step 5: 54 m next to the bridge
    build_world(detail=0.8)
    picnic((14, -6, 0)); picnic((-18, -10, 0))
    person(54.4, (150, 4, 0), math.radians(-90), stride=18)
    tiny_people(40, ((60, 260), (-22, 8)))
    setup((40, -95, 2.0), (165, 0, 30), lens=20, sun_elev=2, sun_az=320)
elif shot == "f3":  # step 9: 870 m, Lotte World Tower below the waist
    build_world(detail=1.0)
    person(870, (700, 900, 0), math.radians(-90), stride=20)
    setup((-1400, -2600, 420), (650, 900, 420), lens=28, sun_elev=3, sun_az=320)
bpy.ops.render.render(write_still=True)
print("DONE", out)
