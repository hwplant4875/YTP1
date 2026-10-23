"""You, Elsewhere EP2 - Voldemort's room in the Riddle House (Blender 5.2, Cycles).

Builds the whole scene from scratch with CC0 Poly Haven assets (run fetch_assets.py first),
saves voldemort_room.blend and renders a still.

  blender -b --factory-startup -P voldemort_room.py -- [--res 100] [--samples 256] [--out name] [--snake]
"""
import bpy, bmesh, glob, math, os, random, sys, time
from mathutils import Vector, Matrix, Euler

HERE = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(HERE, "assets")
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
def arg(k, d):
    return type(d)(argv[argv.index(k) + 1]) if k in argv else d
RES = arg("--res", 100)
SAMPLES = arg("--samples", 256)
OUT = arg("--out", "voldemort_room_look_v1")
SNAKE = "--snake" in argv
NORENDER = "--norender" in argv
rnd = random.Random(7)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# ---------------------------------------------------------------- room layout (metres, Z up)
X0, X1, Y0, Y1, H = -2.8, 3.0, -3.2, 2.6, 3.1      # inner faces of walls, ceiling height
T = 0.22                                             # wall thickness
FX = -0.55                                           # fireplace centre x
BREAST = 2.2                                         # chimney-breast face y
OW, OH = 0.9, 0.88                                   # fire opening
WX0, WX1, WZ0, WZ1 = 1.35, 2.45, 0.62, 2.45          # window opening in back wall


# ---------------------------------------------------------------- helpers
def link(nt, a, b):
    nt.links.new(a, b)

def sock(n, name, out=False):
    for s in (n.outputs if out else n.inputs):
        if s.name == name and s.enabled:
            return s
    raise KeyError(name)

def mixrgb(nt, fac, a, b, blend="MIX"):
    m = nt.nodes.new("ShaderNodeMix"); m.data_type = "RGBA"; m.blend_type = blend
    for s, v in ((sock(m, "Factor"), fac), (sock(m, "A"), a), (sock(m, "B"), b)):
        if isinstance(v, (int, float)): s.default_value = v
        elif isinstance(v, tuple): s.default_value = v
        else: link(nt, v, s)
    return sock(m, "Result", True)

def math_node(nt, op, a, b=None, clamp=False):
    m = nt.nodes.new("ShaderNodeMath"); m.operation = op; m.use_clamp = clamp
    for i, v in enumerate((a, b)):
        if v is None: continue
        if isinstance(v, (int, float)): m.inputs[i].default_value = v
        else: link(nt, v, m.inputs[i])
    return m.outputs[0]

def new_mat(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree
    return m, nt, nt.nodes["Principled BSDF"]

def texfile(folder, key):
    f = glob.glob(os.path.join(A, "textures", folder, f"*_{key}_*.jpg"))
    return f[0] if f else None

def img(nt, path, coord, noncolor=False, box=True):
    n = nt.nodes.new("ShaderNodeTexImage")
    n.image = bpy.data.images.load(path, check_existing=True)
    if noncolor: n.image.colorspace_settings.name = "Non-Color"
    if box: n.projection = "BOX"; n.projection_blend = 0.25
    link(nt, coord, n.inputs["Vector"])
    return n

def coord_node(nt, scale, rot=0.0, offset=(0, 0, 0)):
    tc = nt.nodes.new("ShaderNodeTexCoord"); mp = nt.nodes.new("ShaderNodeMapping")
    link(nt, tc.outputs["Object"], mp.inputs["Vector"])
    mp.inputs["Scale"].default_value = (scale, scale, scale) if not isinstance(scale, tuple) else scale
    mp.inputs["Rotation"].default_value = (0, 0, rot)
    mp.inputs["Location"].default_value = offset
    return mp.outputs["Vector"]

def pbr(name, folder, scale, tint=None, rough_mul=1.0, bump=1.0, box=True, sat=1.0, val=1.0, rot=0.0):
    """Image-based PBR material using world-space box projection (objects are built in world coords)."""
    m, nt, p = new_mat(name)
    co = coord_node(nt, scale, rot)
    d = img(nt, texfile(folder, "diff"), co, box=box)
    col = d.outputs["Color"]
    if sat != 1.0 or val != 1.0:
        hsv = nt.nodes.new("ShaderNodeHueSaturation")
        hsv.inputs["Saturation"].default_value = sat; hsv.inputs["Value"].default_value = val
        link(nt, col, hsv.inputs["Color"]); col = hsv.outputs["Color"]
    if tint: col = mixrgb(nt, 1.0, col, tint + (1,), "MULTIPLY")
    link(nt, col, p.inputs["Base Color"])
    r = texfile(folder, "rough")
    if r:
        rn = img(nt, r, co, True, box)
        link(nt, math_node(nt, "MULTIPLY", rn.outputs["Color"], rough_mul, True), p.inputs["Roughness"])
    nf = texfile(folder, "nor_gl")
    if nf and bump > 0:
        nn = img(nt, nf, co, True, box)
        nm = nt.nodes.new("ShaderNodeNormalMap"); nm.inputs["Strength"].default_value = bump
        link(nt, nn.outputs["Color"], nm.inputs["Color"]); link(nt, nm.outputs["Normal"], p.inputs["Normal"])
    return m

def add_dust(mat, amount=0.6, color=(0.36, 0.34, 0.31), up_power=2.0, scale=6.0):
    """Layer grey dust over upward-facing parts of any Principled material."""
    nt = mat.node_tree
    ps = [n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"]
    if not ps: return
    p = ps[0]
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ"); link(nt, geo.outputs["Normal"], sep.inputs[0])
    up = math_node(nt, "POWER", math_node(nt, "MAXIMUM", sep.outputs["Z"], 0.0), up_power)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = scale
    nz.inputs["Detail"].default_value = 8.0
    link(nt, tc.outputs["Object"], nz.inputs["Vector"])
    patch = math_node(nt, "MULTIPLY", math_node(nt, "SUBTRACT", nz.outputs["Fac"], 0.25), 2.2, True)
    fac = math_node(nt, "MULTIPLY", math_node(nt, "MULTIPLY", up, patch), amount, True)
    fac = math_node(nt, "ADD", fac, amount * 0.18, True)       # a thin film everywhere
    bc = p.inputs["Base Color"]
    src = bc.links[0].from_socket if bc.links else tuple(bc.default_value)
    link(nt, mixrgb(nt, fac, src, color + (1,)), bc)
    rc = p.inputs["Roughness"]
    rsrc = rc.links[0].from_socket if rc.links else rc.default_value
    rm = nt.nodes.new("ShaderNodeMix"); rm.data_type = "FLOAT"
    link(nt, fac, sock(rm, "Factor"))
    if isinstance(rsrc, float): sock(rm, "A").default_value = rsrc
    else: link(nt, rsrc, sock(rm, "A"))
    sock(rm, "B").default_value = 0.95
    link(nt, sock(rm, "Result", True), rc)

def mesh_obj(name, verts, faces, mat=None, smooth=False):
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces); me.update()
    ob = bpy.data.objects.new(name, me); scene.collection.objects.link(ob)
    if mat: me.materials.append(mat)
    if smooth:
        for f in me.polygons: f.use_smooth = True
    return ob

def box(name, x0, x1, y0, y1, z0, z1, mat=None):
    v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    f = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    ob = mesh_obj(name, v, f, mat)
    bev = ob.modifiers.new("bevel", "BEVEL"); bev.width = 0.004; bev.segments = 2
    return ob

def cut(ob, x0, x1, y0, y1, z0, z1):
    c = box("_cutter", x0, x1, y0, y1, z0, z1)
    c.modifiers.clear()
    b = ob.modifiers.new("cut", "BOOLEAN"); b.object = c; b.operation = "DIFFERENCE"; b.solver = "EXACT"
    ob.modifiers.move(len(ob.modifiers) - 1, 0)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.modifier_apply(modifier="cut")
    bpy.data.objects.remove(c)

def import_model(name, loc, rot_z=0.0, scale=(1, 1, 1), keep=None, dust=0.6):
    path = glob.glob(os.path.join(A, "models", name, "*.gltf"))[0]
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=path)
    new = [o for o in bpy.data.objects if o not in before]
    if keep:
        for o in list(new):
            if o.type == "MESH" and not keep(o.name):
                new.remove(o); bpy.data.objects.remove(o)
    root = bpy.data.objects.new(name + "_root", None); scene.collection.objects.link(root)
    for o in new:
        if o.parent is None: o.parent = root
    root.location = loc; root.rotation_euler = (0, 0, math.radians(rot_z)); root.scale = scale
    for o in new:
        if o.type == "MESH":
            for s in o.material_slots:
                if s.material and not s.material.get("dusted"):
                    add_dust(s.material, dust); s.material["dusted"] = True
    return root, new

def look_at(ob, target):
    d = Vector(target) - ob.location
    ob.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()


# ---------------------------------------------------------------- materials
M = {}
M["wall"] = pbr("wallpaper", "decrepit_wallpaper", 0.9, tint=(0.66, 0.68, 0.58), bump=0.6, sat=0.8)
# peel the paper off in patches to show plaster underneath
def peel(mat, under_folder):
    nt = mat.node_tree; p = nt.nodes["Principled BSDF"]
    co = coord_node(nt, 0.5)
    u = img(nt, texfile(under_folder, "diff"), co)
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 1.6
    nz.inputs["Detail"].default_value = 12; nz.inputs["Roughness"].default_value = 0.7
    link(nt, coord_node(nt, 1.0), nz.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.60; ramp.color_ramp.elements[1].position = 0.63
    link(nt, nz.outputs["Fac"], ramp.inputs["Fac"])
    # lower wall + corners stained darker (damp)
    tc = nt.nodes.new("ShaderNodeTexCoord"); sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    link(nt, tc.outputs["Object"], sep.inputs[0])
    damp = math_node(nt, "SUBTRACT", 1.0, math_node(nt, "DIVIDE", sep.outputs["Z"], 0.9), True)
    under = mixrgb(nt, 1.0, u.outputs["Color"], (0.75, 0.72, 0.66, 1), "MULTIPLY")
    base = p.inputs["Base Color"].links[0].from_socket
    c = mixrgb(nt, ramp.outputs["Color"], base, under)
    c = mixrgb(nt, math_node(nt, "MULTIPLY", damp, 0.55), c, (0.18, 0.15, 0.11, 1), "MULTIPLY")
    link(nt, c, p.inputs["Base Color"])
peel(M["wall"], "worn_plaster_wall")
M["plaster"] = pbr("ceiling_plaster", "worn_plaster_wall", 0.5, tint=(0.62, 0.6, 0.56), bump=0.5)
M["floor"] = pbr("floorboards", "old_wooden_floor_02", 0.45, tint=(0.85, 0.8, 0.75), rough_mul=1.15, bump=1.0, box=False)
M["darkwood"] = pbr("dark_wood", "dark_wood", 1.2, tint=(0.75, 0.68, 0.6), rough_mul=1.1)
M["paintwood"] = pbr("window_wood", "wood_cabinet_worn_long", 1.5, tint=(0.55, 0.52, 0.48), rough_mul=1.2, sat=0.6)
M["boards"] = pbr("boards", "weathered_planks", 1.4, tint=(0.8, 0.76, 0.7), rough_mul=1.2)
M["brick"] = pbr("firebrick", "medieval_red_brick", 1.4, tint=(0.55, 0.45, 0.38), rough_mul=1.0, bump=1.2)
M["hearth"] = pbr("hearthstone", "medieval_red_brick", 0.9, tint=(0.35, 0.33, 0.31), sat=0.25, rough_mul=1.0)
M["rug"] = pbr("hearthrug", "dirty_carpet", 1.3, tint=(0.55, 0.16, 0.1), sat=1.3, rough_mul=1.0, box=False)
M["bark"] = pbr("bark", "bark_brown_01", 2.5, tint=(0.55, 0.5, 0.45), bump=1.5)
M["ground"] = pbr("ground", "forest_floor", 0.15, tint=(0.4, 0.4, 0.4), box=False)
for k in ("wall", "floor", "darkwood", "paintwood", "boards", "hearth", "rug"):
    add_dust(M[k], {"floor": 0.4, "darkwood": 0.7, "hearth": 0.7, "rug": 0.1}.get(k, 0.45), scale=2.5 if k == "floor" else 6.0)

# soot on the firebrick (darker towards the top of the firebox)
nt = M["brick"].node_tree; p = nt.nodes["Principled BSDF"]
tc = nt.nodes.new("ShaderNodeTexCoord"); sep = nt.nodes.new("ShaderNodeSeparateXYZ")
link(nt, tc.outputs["Object"], sep.inputs[0])
soot = math_node(nt, "ADD", 0.55, math_node(nt, "MULTIPLY", sep.outputs["Z"], 0.6), True)
link(nt, mixrgb(nt, soot, p.inputs["Base Color"].links[0].from_socket, (0.02, 0.018, 0.016, 1)), p.inputs["Base Color"])

def simple(name, color, rough=0.5, metal=0.0, **kw):
    m, nt, p = new_mat(name)
    p.inputs["Base Color"].default_value = color + (1,)
    p.inputs["Roughness"].default_value = rough; p.inputs["Metallic"].default_value = metal
    for k, v in kw.items(): p.inputs[k].default_value = v
    return m
M["iron"] = simple("cast_iron", (0.025, 0.023, 0.022), 0.75, 0.9)
add_dust(M["iron"], 0.3)
M["gold"] = simple("locket_gold", (0.85, 0.62, 0.3), 0.32, 1.0)
add_dust(M["gold"], 0.5, scale=60)
M["web"] = simple("cobweb", (0.75, 0.74, 0.72), 0.6, **{"Transmission Weight": 0.3})
M["stone"] = simple("gravestone", (0.18, 0.18, 0.18), 0.85)
M["leaf"] = simple("ivy_leaf", (0.02, 0.05, 0.015), 0.25, **{"Subsurface Weight": 0.0})
M["mote"] = simple("dust_mote", (0.9, 0.85, 0.8), 0.9)
M["ash"] = simple("ash", (0.09, 0.085, 0.08), 0.95)

# rain-on-glass: dirty, wet window glass
m, nt, p = new_mat("rain_glass")
p.inputs["Transmission Weight"].default_value = 1.0; p.inputs["IOR"].default_value = 1.5
p.inputs["Base Color"].default_value = (0.8, 0.82, 0.8, 1)
tc = nt.nodes.new("ShaderNodeTexCoord")
mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1, 1, 1)
link(nt, tc.outputs["Object"], mp.inputs["Vector"])
drops = nt.nodes.new("ShaderNodeTexVoronoi"); drops.inputs["Scale"].default_value = 70
drops.inputs["Randomness"].default_value = 1.0
link(nt, mp.outputs["Vector"], drops.inputs["Vector"])
dh = math_node(nt, "SUBTRACT", 1.0, math_node(nt, "DIVIDE", drops.outputs["Distance"], 0.32), True)
dh = math_node(nt, "POWER", dh, 0.6)
dmask = nt.nodes.new("ShaderNodeTexNoise"); dmask.inputs["Scale"].default_value = 9
link(nt, mp.outputs["Vector"], dmask.inputs["Vector"])
dh = math_node(nt, "MULTIPLY", dh, math_node(nt, "MULTIPLY", math_node(nt, "SUBTRACT", dmask.outputs["Fac"], 0.42), 4.0, True))
streak_map = nt.nodes.new("ShaderNodeMapping"); streak_map.inputs["Scale"].default_value = (40, 40, 1.2)
link(nt, tc.outputs["Object"], streak_map.inputs["Vector"])
streaks = nt.nodes.new("ShaderNodeTexWave"); streaks.wave_type = "BANDS"; streaks.bands_direction = "X"
streaks.inputs["Scale"].default_value = 1.0; streaks.inputs["Distortion"].default_value = 6
link(nt, streak_map.outputs["Vector"], streaks.inputs["Vector"])
sh = math_node(nt, "MULTIPLY", math_node(nt, "SUBTRACT", streaks.outputs["Fac"], 0.85), 5.0, True)
height = math_node(nt, "MAXIMUM", dh, sh)
bump = nt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.8
bump.inputs["Distance"].default_value = 0.002
link(nt, height, bump.inputs["Height"]); link(nt, bump.outputs["Normal"], p.inputs["Normal"])
grime = nt.nodes.new("ShaderNodeTexNoise"); grime.inputs["Scale"].default_value = 3; grime.inputs["Detail"].default_value = 10
link(nt, tc.outputs["Object"], grime.inputs["Vector"])
gr = math_node(nt, "MULTIPLY", grime.outputs["Fac"], 0.12)
link(nt, math_node(nt, "MULTIPLY", math_node(nt, "SUBTRACT", 1.0, height, True), gr), p.inputs["Roughness"])
M["glass"] = m


# ---------------------------------------------------------------- shell: floor, walls, ceiling
fl = mesh_obj("floor", [(X0, Y0, 0), (X1, Y0, 0), (X1, Y1, 0), (X0, Y1, 0)], [(0, 1, 2, 3)], M["floor"])
me = fl.data; me.uv_layers.new()
for li, l in enumerate(me.loops):
    v = me.vertices[l.vertex_index].co; me.uv_layers[0].data[li].uv = (v.x, v.y)
# floor uses UV = metres (box=False) -> rotate via mapping scale only
fl.modifiers.new("sub", "SUBSURF").subdivision_type = "SIMPLE"; fl.modifiers["sub"].levels = 6
fl.modifiers["sub"].render_levels = 6
tx = bpy.data.textures.new("warp", "CLOUDS"); tx.noise_scale = 0.6
dm = fl.modifiers.new("warp", "DISPLACE"); dm.texture = tx; dm.strength = 0.012; dm.mid_level = 0.5
for nm in ("rug", "ground"):
    pass

back = box("wall_back", X0 - T, X1 + T, Y1, Y1 + T, 0, H + 0.01, M["wall"])
cut(back, WX0, WX1, Y1 - 0.1, Y1 + T + 0.1, WZ0, WZ1)
box("wall_left", X0 - T, X0, Y0 - T, Y1 + T, 0, H + 0.01, M["wall"])
box("wall_right", X1, X1 + T, Y0 - T, Y1 + T, 0, H + 0.01, M["wall"])
box("wall_front", X0 - T, X1 + T, Y0 - T, Y0, 0, H + 0.01, M["wall"])
box("ceiling", X0 - T, X1 + T, Y0 - T, Y1 + T, H, H + 0.1, M["plaster"])
# cornice + skirting
for nm, a in (("back", (X0, X1, Y1 - 0.02, Y1)), ("left", (X0, X0 + 0.02, Y0, Y1)), ("right", (X1 - 0.02, X1, Y0, Y1))):
    box("skirt_" + nm, a[0] - (0.0 if nm != "back" else 0), a[1], a[2], a[3], 0, 0.2, M["darkwood"])
    box("cornice_" + nm, a[0], a[1], a[2] - (0.06 if nm == "back" else 0), a[3], H - 0.12, H, M["plaster"])
for o in [o for o in bpy.data.objects if o.name.startswith(("skirt_", "cornice_"))]:
    if o.name.endswith("left"): o.data.transform(Matrix.Translation((0, 0, 0)))
# picture rail
box("picture_rail", X0, X1, Y1 - 0.025, Y1, 2.35, 2.38, M["darkwood"])

# ---------------------------------------------------------------- fireplace
L, R = FX - OW / 2, FX + OW / 2
box("breast_l", FX - 0.95, L, BREAST, Y1, 0, H, M["wall"])
box("breast_r", R, FX + 0.95, BREAST, Y1, 0, H, M["wall"])
box("breast_top", L, R, BREAST, Y1, OH, H, M["wall"])
box("firebox_back", L, R, Y1 - 0.06, Y1, 0, OH, M["brick"])
box("firebox_l", L, L + 0.05, BREAST, Y1, 0, OH, M["brick"])
box("firebox_r", R - 0.05, R, BREAST, Y1, 0, OH, M["brick"])
box("firebox_top", L, R, BREAST, Y1, OH - 0.04, OH, M["brick"])
box("firebox_floor", L, R, BREAST, Y1, 0, 0.03, M["hearth"])
# mantelpiece
box("pilaster_l", FX - 0.78, L, BREAST - 0.09, BREAST, 0, 1.08, M["darkwood"])
box("pilaster_r", R, FX + 0.78, BREAST - 0.09, BREAST, 0, 1.08, M["darkwood"])
box("frieze", FX - 0.78, FX + 0.78, BREAST - 0.09, BREAST, OH, 1.15, M["darkwood"])
box("mantel_shelf", FX - 0.88, FX + 0.88, BREAST - 0.24, BREAST + 0.01, 1.15, 1.21, M["darkwood"])
box("mantel_mould", FX - 0.82, FX + 0.82, BREAST - 0.14, BREAST, 1.10, 1.15, M["darkwood"])
box("plinth_l", FX - 0.8, L - 0.0, BREAST - 0.11, BREAST, 0, 0.16, M["darkwood"])
box("plinth_r", R, FX + 0.8, BREAST - 0.11, BREAST, 0, 0.16, M["darkwood"])
box("hearth", FX - 0.9, FX + 0.9, BREAST - 0.5, BREAST, 0, 0.03, M["hearth"])
# cast-iron grate
for i, z in enumerate((0.08, 0.16, 0.24)):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.008, depth=0.62, location=(FX, BREAST + 0.12 - i * 0.0, z), rotation=(0, math.radians(90), 0))
    bpy.context.object.name = "firebox_grate_bar"; bpy.context.object.data.materials.append(M["iron"])
for x in (-0.28, 0.28):
    box("firebox_grate_leg", FX + x - 0.012, FX + x + 0.012, BREAST + 0.06, BREAST + 0.35, 0, 0.26, M["iron"])
box("firebox_grate_basket", FX - 0.3, FX + 0.3, BREAST + 0.08, BREAST + 0.34, 0.05, 0.065, M["iron"])

# logs
log_specs = [((FX - 0.08, BREAST + 0.22, 0.13), (0, 90, 8), 0.055, 0.55),
             ((FX + 0.1, BREAST + 0.17, 0.14), (0, 90, -12), 0.05, 0.5),
             ((FX + 0.0, BREAST + 0.21, 0.22), (8, 72, 20), 0.045, 0.48),
             ((FX - 0.15, BREAST + 0.25, 0.21), (-10, 105, -30), 0.04, 0.4)]
m, nt, p = new_mat("burning_log")
co = coord_node(nt, 2.5)
d = img(nt, texfile("bark_brown_01", "diff"), co)
nn = img(nt, texfile("bark_brown_01", "nor_gl"), co, True)
nm = nt.nodes.new("ShaderNodeNormalMap"); link(nt, nn.outputs["Color"], nm.inputs["Color"])
link(nt, nm.outputs["Normal"], p.inputs["Normal"])
ltc = nt.nodes.new("ShaderNodeTexCoord")
warp = nt.nodes.new("ShaderNodeTexNoise"); warp.inputs["Scale"].default_value = 9; warp.inputs["Detail"].default_value = 4
link(nt, ltc.outputs["Object"], warp.inputs["Vector"])
wv = nt.nodes.new("ShaderNodeMix"); wv.data_type = "VECTOR"; sock(wv, "Factor").default_value = 0.35
link(nt, ltc.outputs["Object"], sock(wv, "A")); link(nt, warp.outputs["Color"], sock(wv, "B"))
char = nt.nodes.new("ShaderNodeTexVoronoi"); char.feature = "DISTANCE_TO_EDGE"; char.inputs["Scale"].default_value = 40
link(nt, sock(wv, "Result", True), char.inputs["Vector"])
patch = nt.nodes.new("ShaderNodeTexNoise"); patch.inputs["Scale"].default_value = 6
link(nt, ltc.outputs["Object"], patch.inputs["Vector"])
crack = math_node(nt, "SUBTRACT", 1.0, math_node(nt, "DIVIDE", char.outputs["Distance"], 0.035), True)
crack = math_node(nt, "MULTIPLY", crack, math_node(nt, "MULTIPLY", math_node(nt, "SUBTRACT", patch.outputs["Fac"], 0.45), 4.0, True))
geo = nt.nodes.new("ShaderNodeNewGeometry"); sp = nt.nodes.new("ShaderNodeSeparateXYZ")
link(nt, geo.outputs["Normal"], sp.inputs[0])
under = math_node(nt, "SUBTRACT", 0.4, sp.outputs["Z"], True)
glow = math_node(nt, "MULTIPLY", crack, math_node(nt, "ADD", under, 0.25))
link(nt, mixrgb(nt, 0.75, d.outputs["Color"], (0.015, 0.012, 0.01, 1)), p.inputs["Base Color"])
p.inputs["Roughness"].default_value = 0.9
bb = nt.nodes.new("ShaderNodeBlackbody"); bb.inputs["Temperature"].default_value = 1250
link(nt, bb.outputs["Color"], p.inputs["Emission Color"])
link(nt, math_node(nt, "MULTIPLY", math_node(nt, "POWER", glow, 1.5), 10.0), p.inputs["Emission Strength"])
M["log"] = m
for (loc, rot, r, ln) in log_specs:
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=r, depth=ln, location=loc,
                                        rotation=tuple(math.radians(a) for a in rot))
    o = bpy.context.object; o.name = "fire_log"; o.data.materials.append(M["log"])
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    o.modifiers.new("b", "BEVEL").width = 0.01
    s = o.modifiers.new("s", "SUBSURF"); s.levels = 2; s.render_levels = 2
    dsp = o.modifiers.new("d", "DISPLACE"); dsp.texture = tx; dsp.strength = 0.012
    bpy.ops.object.shade_smooth()

# ember bed + ash
m, nt, p = new_mat("embers")
tc = nt.nodes.new("ShaderNodeTexCoord")
v = nt.nodes.new("ShaderNodeTexVoronoi"); v.inputs["Scale"].default_value = 45
link(nt, tc.outputs["Object"], v.inputs["Vector"])
nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 12; nz.inputs["Detail"].default_value = 6
link(nt, tc.outputs["Object"], nz.inputs["Vector"])
heat = math_node(nt, "MULTIPLY", math_node(nt, "SUBTRACT", nz.outputs["Fac"], 0.42), 3.5, True)
heat = math_node(nt, "MULTIPLY", heat, math_node(nt, "SUBTRACT", 1.0, math_node(nt, "MULTIPLY", v.outputs["Distance"], 1.5), True))
p.inputs["Base Color"].default_value = (0.05, 0.045, 0.04, 1); p.inputs["Roughness"].default_value = 0.95
bb = nt.nodes.new("ShaderNodeBlackbody"); link(nt, math_node(nt, "ADD", 900, math_node(nt, "MULTIPLY", heat, 500)), bb.inputs["Temperature"])
link(nt, bb.outputs["Color"], p.inputs["Emission Color"])
link(nt, math_node(nt, "MULTIPLY", math_node(nt, "POWER", heat, 2.0), 8.0), p.inputs["Emission Strength"])
bm = bmesh.new()
for i in range(260):
    x = FX + rnd.uniform(-0.27, 0.27); y = BREAST + rnd.uniform(0.09, 0.33); z = rnd.uniform(0.065, 0.1)
    bmesh.ops.create_icosphere(bm, subdivisions=1, radius=rnd.uniform(0.008, 0.022),
                               matrix=Matrix.Translation((x, y, z)) @ Matrix.Diagonal((1, 1, 0.6, 1)))
me = bpy.data.meshes.new("embers"); bm.to_mesh(me); bm.free()
eo = bpy.data.objects.new("embers", me); scene.collection.objects.link(eo); me.materials.append(m)
bm = bmesh.new()
for i in range(300):
    x = FX + rnd.uniform(-0.42, 0.42); y = BREAST + rnd.uniform(0.02, 0.38); z = 0.03
    bmesh.ops.create_icosphere(bm, subdivisions=1, radius=rnd.uniform(0.006, 0.02),
                               matrix=Matrix.Translation((x, y, z)) @ Matrix.Diagonal((1, 1, 0.35, 1)))
me = bpy.data.meshes.new("ash"); bm.to_mesh(me); bm.free()
ao = bpy.data.objects.new("ash", me); scene.collection.objects.link(ao); me.materials.append(M["ash"])

# volumetric flames
m = bpy.data.materials.new("flames"); m.use_nodes = True; nt = m.node_tree
nt.nodes.remove(nt.nodes["Principled BSDF"])
out = nt.nodes["Material Output"]
tc = nt.nodes.new("ShaderNodeTexCoord"); sep = nt.nodes.new("ShaderNodeSeparateXYZ")
link(nt, tc.outputs["Object"], sep.inputs[0])
mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (5.0, 5.0, 1.6)
link(nt, tc.outputs["Object"], mp.inputs["Vector"])
nz = nt.nodes.new("ShaderNodeTexNoise"); nz.noise_dimensions = "4D"
nz.inputs["Scale"].default_value = 1.4; nz.inputs["Detail"].default_value = 5; nz.inputs["Distortion"].default_value = 1.5
nz.inputs["W"].default_value = 3.3
link(nt, mp.outputs["Vector"], nz.inputs["Vector"])
h = math_node(nt, "MULTIPLY", math_node(nt, "ADD", sep.outputs["Z"], 1.0), 0.5)               # 0 bottom .. 1 top
ax = math_node(nt, "ABSOLUTE", sep.outputs["X"]); ay = math_node(nt, "ABSOLUTE", sep.outputs["Y"])
taper = math_node(nt, "ADD", math_node(nt, "MULTIPLY", ax, 0.55), math_node(nt, "MULTIPLY", ay, 0.6))
field = math_node(nt, "SUBTRACT", math_node(nt, "MULTIPLY", math_node(nt, "SUBTRACT", nz.outputs["Fac"], 0.42), 3.2),
                  math_node(nt, "ADD", math_node(nt, "MULTIPLY", h, 0.85), math_node(nt, "MULTIPLY", taper, 0.75)))
field = math_node(nt, "MULTIPLY", field, 3.0, True)
vol = nt.nodes.new("ShaderNodeVolumePrincipled")
link(nt, math_node(nt, "MULTIPLY", field, 1.5), vol.inputs["Density"])
vol.inputs["Color"].default_value = (0.02, 0.02, 0.02, 1)
bb = nt.nodes.new("ShaderNodeBlackbody")
link(nt, math_node(nt, "ADD", 1000, math_node(nt, "MULTIPLY", field, 1000)), bb.inputs["Temperature"])
link(nt, bb.outputs["Color"], vol.inputs["Emission Color"])
link(nt, math_node(nt, "MULTIPLY", math_node(nt, "POWER", field, 2.0), 40.0), vol.inputs["Emission Strength"])
link(nt, vol.outputs[0], out.inputs["Volume"])
M["flames"] = m
fo = box("flames", FX - 0.3, FX + 0.3, BREAST + 0.05, BREAST + 0.36, 0.08, 0.72, m); fo.modifiers.clear()
fo.data.transform(Matrix.Translation(-Vector((FX, BREAST + 0.205, 0.40))))
fo.location = (FX, BREAST + 0.205, 0.40)
fo.data.transform(Matrix.Diagonal((1 / 0.3, 1 / 0.155, 1 / 0.32, 1)))
fo.scale = (0.3, 0.155, 0.32)

# fire lights (the real illumination)
def light(name, kind, loc, energy, color, size=0.1, rot=None):
    ld = bpy.data.lights.new(name, kind); ld.energy = energy; ld.color = color
    if kind == "AREA": ld.size = size[0]; ld.size_y = size[1]; ld.shape = "RECTANGLE"
    elif kind in ("POINT", "SPOT"): ld.shadow_soft_size = size
    ob = bpy.data.objects.new(name, ld); scene.collection.objects.link(ob); ob.location = loc
    ob.visible_camera = False
    if kind == "AREA": ob.visible_glossy = False
    if rot: ob.rotation_euler = rot
    return ob
FIRE = (1.0, 0.42, 0.13)
light("fire_a", "POINT", (FX - 0.1, BREAST - 0.06, 0.32), 80, FIRE, 0.12)
light("fire_b", "POINT", (FX + 0.12, BREAST - 0.05, 0.4), 60, (1.0, 0.5, 0.18), 0.1)
light("fire_glow", "AREA", (FX, BREAST - 0.02, 0.35), 90, (1.0, 0.45, 0.16), (0.6, 0.45), (math.radians(-90), 0, 0))
light("fire_floor", "POINT", (FX, BREAST + 0.2, 0.12), 12, (1.0, 0.35, 0.1), 0.1)

# ---------------------------------------------------------------- window
FY = Y1 + T * 0.5
frame_parts = [(WX0, WX0 + 0.07, WZ0, WZ1), (WX1 - 0.07, WX1, WZ0, WZ1), (WX0, WX1, WZ0, WZ0 + 0.08),
               (WX0, WX1, WZ1 - 0.07, WZ1), (WX0, WX1, (WZ0 + WZ1) / 2 - 0.035, (WZ0 + WZ1) / 2 + 0.035)]
for i, (a, b, c, d) in enumerate(frame_parts):
    box(f"wframe{i}", a, b, FY - 0.04, FY + 0.03, c, d, M["paintwood"])
mx = (WX0 + WX1) / 2
for zc in ((WZ0 + (WZ0 + WZ1) / 2) / 2, ((WZ0 + WZ1) / 2 + WZ1) / 2):
    box("glazing_v", mx - 0.015, mx + 0.015, FY - 0.025, FY + 0.015, WZ0, WZ1, M["paintwood"])
    box("glazing_h", WX0, WX1, FY - 0.025, FY + 0.015, zc - 0.012, zc + 0.012, M["paintwood"])
gl = box("glass", WX0 + 0.05, WX1 - 0.05, FY - 0.004, FY + 0.0, WZ0 + 0.05, WZ1 - 0.05, M["glass"]); gl.modifiers.clear()
gl.visible_shadow = False
box("sill", WX0 - 0.1, WX1 + 0.1, Y1 - 0.14, Y1 + 0.02, WZ0 - 0.05, WZ0, M["paintwood"])
# boards nailed over part of the window (inside face)
board_specs = [(1.05, 0.0, 0.18), (1.32, 0.06, 0.15), (2.18, -0.05, 0.17), (0.82, 0.5, 0.15)]
for i, (z, ang, w) in enumerate(board_specs):
    o = box(f"board{i}", -0.72, 0.72, -0.012, 0.012, -w / 2, w / 2, M["boards"])
    o.data.transform(Matrix.Rotation(ang, 4, "Y"))
    o.data.transform(Matrix.Translation((mx + rnd.uniform(-0.04, 0.04), Y1 - 0.03, z)))
    for sx in (-0.62, 0.62):
        p0 = Matrix.Rotation(ang, 4, "Y") @ Vector((sx, 0, 0)) + Vector((mx, Y1 - 0.045, z))
        bpy.ops.mesh.primitive_cylinder_add(radius=0.006, depth=0.006, location=p0, rotation=(math.radians(90), 0, 0))
        bpy.context.object.data.materials.append(M["iron"])
# (boards 0 and 1 overlap: one crooked over another; board 3 runs diagonal across the lower sash)

# ivy pressing on the glass, outside
leaf_v = [(0, 0, 0), (0.35, 0, 0.25), (0.5, 0, 0.62), (0.22, 0, 0.62), (0, 0, 1.0), (-0.22, 0, 0.62), (-0.5, 0, 0.62), (-0.35, 0, 0.25)]
bm = bmesh.new()
for i in range(700):
    x = rnd.uniform(WX0 - 0.4, WX1 + 0.4); z = rnd.uniform(WZ0 - 0.4, WZ1 + 0.5)
    inside = WX0 + 0.25 < x < WX1 - 0.25 and WZ0 + 0.3 < z < WZ1 - 0.1
    if inside and rnd.random() < 0.8: continue
    if z < WZ0 + 0.5 and rnd.random() < 0.5: continue
    s = rnd.uniform(0.045, 0.085)
    mtx = (Matrix.Translation((x, Y1 + T + 0.02 + rnd.uniform(0, 0.12), z)) @ Matrix.Rotation(rnd.uniform(-0.5, 0.5), 4, "X")
           @ Matrix.Rotation(rnd.uniform(0, 6.28), 4, "Y") @ Matrix.Rotation(rnd.uniform(-0.4, 0.4), 4, "Z") @ Matrix.Diagonal((s, s, s, 1)))
    vs = [bm.verts.new(mtx @ Vector(c)) for c in leaf_v]
    bm.faces.new(vs)
me = bpy.data.meshes.new("ivy"); bm.to_mesh(me); bm.free()
iv = bpy.data.objects.new("ivy", me); scene.collection.objects.link(iv); me.materials.append(M["leaf"])
# outer wall face around the window so the ivy has something to cling to
outer = box("outer_wall", WX0 - 1.0, WX1 + 1.0, Y1 + T, Y1 + T + 0.01, WZ0 - 1.0, WZ1 + 0.8, M["plaster"])
cut(outer, WX0, WX1, Y1, Y1 + T + 0.1, WZ0, WZ1)

# far below: the village graveyard and its yew under moonlight
gnd = mesh_obj("ground", [(-80, 8, -7), (80, 8, -7), (80, 160, -7), (-80, 160, -7)], [(0, 1, 2, 3)], M["ground"])
gnd.data.uv_layers.new()
for li, l in enumerate(gnd.data.loops):
    vv = gnd.data.vertices[l.vertex_index].co; gnd.data.uv_layers[0].data[li].uv = (vv.x, vv.y)
for i in range(40):
    gx = rnd.uniform(5, 30); gy = rnd.uniform(45, 75); w = rnd.uniform(0.45, 0.7); hh = rnd.uniform(0.7, 1.2)
    o = box("grave", gx - w / 2, gx + w / 2, gy - 0.08, gy + 0.08, -7, -7 + hh, M["stone"])
    o.data.transform(Matrix.Translation((-gx, -gy, 7)))
    o.location = (gx, gy, -7); o.rotation_euler = (rnd.uniform(-0.12, 0.12), rnd.uniform(-0.15, 0.15), rnd.uniform(-0.2, 0.2))
# yew trees: dense dark blobs on short trunks (silhouettes only)
ytx = bpy.data.textures.new("yew", "CLOUDS"); ytx.noise_scale = 0.9
M["yew"] = simple("yew", (0.01, 0.014, 0.01), 0.8)
for (yx, yy, ys) in ((15, 58, 4.5), (24, 66, 3.2), (6, 70, 3.0)):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=5, radius=ys, location=(yx, yy, -7 + ys * 1.05))
    yo = bpy.context.object; yo.scale = (1.0, 0.9, 1.15); yo.data.materials.append(M["yew"])
    dd = yo.modifiers.new("d", "DISPLACE"); dd.texture = ytx; dd.strength = ys * 0.45
# church silhouette
box("church_nave", 34, 46, 92, 98, -7, 0.5, M["stone"]); box("church_tower", 29, 33, 93, 97, -7, 6.5, M["stone"])

# ---------------------------------------------------------------- furniture & props
chair, _ = import_model("GreenChair_01", (FX + 0.72, 1.2, 0), 180 + 48, (1.08, 1.08, 1.22), dust=0.55)
table, _ = import_model("round_wooden_table_01", (FX + 1.32, 0.95, 0), 15, (0.33, 0.33, 0.66), dust=0.8)
TT = 1.004 * 0.66                                    # table top height
books, bobs = import_model("book_encyclopedia_set_01", (0, 0, 0), 0, dust=0.9,
                           keep=lambda n: n.endswith(("book03", "book07", "book11")))
for i, o in enumerate(sorted([o for o in bobs if o.type == "MESH"], key=lambda o: o.name)):
    o.parent = None
    bpy.context.view_layer.objects.active = o; o.select_set(True)
    bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS"); o.select_set(False)
    o.rotation_euler = (0, math.radians(90), math.radians(10 + i * 23))
    o.location = (FX + 1.32 + 0.05 + i * 0.01, 0.98 + i * 0.012, TT + 0.014 + i * 0.027)
cand, _ = import_model("brass_candleholders", (FX + 1.32 - 0.13, 0.86, TT), 0, (1, 1, 1), dust=0.9,
                       keep=lambda n: n.endswith("_01"))
# find and centre the single candlestick on the table
bpy.context.view_layer.update()
cm = [o for o in _ if o.type == "MESH"]
if cm:
    bb_ = [cm[0].matrix_world @ Vector(c) for c in cm[0].bound_box]
    cx = sum(p.x for p in bb_) / 8; cy = sum(p.y for p in bb_) / 8
    cand.location.x -= cx - (FX + 1.32 - 0.14); cand.location.y -= cy - 0.86
# the locket, half hidden in dust on the table
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.013, location=(FX + 1.32 + 0.12, 0.84, TT + 0.004))
lk = bpy.context.object; lk.scale = (1, 1.25, 0.28); lk.data.materials.append(M["gold"]); bpy.ops.object.shade_smooth()
bpy.ops.mesh.primitive_torus_add(major_radius=0.004, minor_radius=0.0012, location=(FX + 1.32 + 0.12, 0.84 + 0.019, TT + 0.004))
bpy.context.object.data.materials.append(M["gold"])
cpts = [(FX + 1.32 + 0.12 + 0.01 * math.sin(t * 0.7) + t * 0.004, 0.86 + t * 0.006, TT + 0.0015) for t in range(22)]
cu = bpy.data.curves.new("chain", "CURVE"); cu.dimensions = "3D"; cu.bevel_depth = 0.0009
sp_ = cu.splines.new("POLY"); sp_.points.add(len(cpts) - 1)
for i, c in enumerate(cpts): sp_.points[i].co = c + (1,)
co_ = bpy.data.objects.new("chain", cu); scene.collection.objects.link(co_); cu.materials.append(M["gold"])

# mantel dressing
import_model("mantel_clock_01", (FX + 0.05, BREAST - 0.11, 1.21), 0, dust=0.9)
ch, chobs = import_model("brass_candleholders", (0, 0, 0), 0, dust=0.9, keep=lambda n: n.endswith("_02"))
bpy.context.view_layer.update()
cm = [o for o in chobs if o.type == "MESH"]
if cm:
    bb_ = [cm[0].matrix_world @ Vector(c) for c in cm[0].bound_box]
    cx = sum(p.x for p in bb_) / 8; cy = sum(p.y for p in bb_) / 8
    ch.location = (FX - 0.6 - cx, BREAST - 0.11 - cy, 1.21)
import_model("ornate_mirror_01", (FX, BREAST - 0.005, 1.95), 0, (1.75, 1.75, 1.75), dust=0.5)
# old, half-desilvered mirror: darker and hazier than new glass
nt = bpy.data.materials["ornate_mirror_01"].node_tree; p = nt.nodes["Principled BSDF"]
bc = p.inputs["Base Color"]; link(nt, mixrgb(nt, 1.0, bc.links[0].from_socket, (0.42, 0.4, 0.37, 1), "MULTIPLY"), bc)
rc = p.inputs["Roughness"]
if rc.links: link(nt, math_node(nt, "MAXIMUM", rc.links[0].from_socket, 0.22), rc)
# left of the breast: commode with a picture above
import_model("GothicCommode_01", (-2.05, Y1 - 0.3, 0), 0, dust=0.8)
pic, _ = import_model("fancy_picture_frame_01", (-2.05, Y1 - 0.0, 1.85), 0, (1.15, 1.15, 1.15), dust=0.6)
pic.rotation_euler = (0, math.radians(3.5), 0)

# hearthrug
rug = mesh_obj("hearthrug", [(-0.8, -0.5, 0), (0.8, -0.5, 0), (0.8, 0.5, 0), (-0.8, 0.5, 0)], [(0, 1, 2, 3)], M["rug"])
rug.data.uv_layers.new()
for li, l in enumerate(rug.data.loops):
    vv = rug.data.vertices[l.vertex_index].co; rug.data.uv_layers[0].data[li].uv = (vv.x * 0.8, vv.y * 0.8)
rug.location = (FX + 0.1, 1.0, 0.012); rug.rotation_euler = (0, 0, math.radians(-4))
s = rug.modifiers.new("sub", "SUBSURF"); s.subdivision_type = "SIMPLE"; s.levels = s.render_levels = 5
tx2 = bpy.data.textures.new("rugwrinkle", "CLOUDS"); tx2.noise_scale = 0.25
dsp = rug.modifiers.new("wr", "DISPLACE"); dsp.texture = tx2; dsp.strength = 0.012
sol = rug.modifiers.new("sol", "SOLIDIFY"); sol.thickness = 0.008

# ---------------------------------------------------------------- cobwebs
def cobweb(corner, d1, d2, d3, n=14, reach=0.55):
    pts = [Vector(corner)]
    anchors = []
    for d in (d1, d2, d3):
        for k in range(4):
            anchors.append(Vector(corner) + Vector(d) * rnd.uniform(0.08, reach))
    cu = bpy.data.curves.new("web", "CURVE"); cu.dimensions = "3D"; cu.bevel_depth = 0.00045
    def strand(a, b, sag):
        sp = cu.splines.new("POLY"); sp.points.add(7)
        for i in range(8):
            t = i / 7; p = a.lerp(b, t); p.z -= sag * 4 * t * (1 - t)
            sp.points[i].co = (p.x, p.y, p.z, 1)
    for a in anchors: strand(Vector(corner), a, 0.01)
    for _ in range(n):
        a, b = rnd.sample(anchors, 2)
        strand(a, b, rnd.uniform(0.01, 0.06))
    o = bpy.data.objects.new("cobweb", cu); scene.collection.objects.link(o); cu.materials.append(M["web"])
cobweb((X0 + 0.01, Y1 - 0.01, H - 0.01), (1, 0, 0), (0, -1, 0), (0, 0, -1), 22, 0.7)
cobweb((X1 - 0.01, Y1 - 0.01, H - 0.01), (-1, 0, 0), (0, -1, 0), (0, 0, -1), 22, 0.7)
cobweb((FX - 0.95 + 0.01, BREAST + 0.01, H - 0.01), (-1, 0, 0), (0, 1, 0), (0, 0, -1), 10, 0.3)
cobweb((WX1 - 0.01, Y1 - 0.06, WZ1 - 0.01), (-1, 0, 0), (0, 0, -1), (0, -1, 0), 12, 0.35)
cobweb((FX + 0.88, BREAST - 0.2, 1.21), (0, 0, 1), (-1, 0, 0), (0, 1, 0), 8, 0.25)

# ---------------------------------------------------------------- atmosphere
m = bpy.data.materials.new("haze"); m.use_nodes = True; nt = m.node_tree
nt.nodes.remove(nt.nodes["Principled BSDF"])
vol = nt.nodes.new("ShaderNodeVolumePrincipled")
nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 0.8; nz.inputs["Detail"].default_value = 3
link(nt, nt.nodes.new("ShaderNodeTexCoord").outputs["Object"], nz.inputs["Vector"])
link(nt, math_node(nt, "MULTIPLY", math_node(nt, "ADD", nz.outputs["Fac"], 0.2), 0.003), vol.inputs["Density"])
vol.inputs["Color"].default_value = (0.85, 0.82, 0.78, 1); vol.inputs["Anisotropy"].default_value = 0.45
link(nt, vol.outputs[0], nt.nodes["Material Output"].inputs["Volume"])
hz = box("haze", X0 + 0.02, X1 - 0.02, Y0 + 0.02, Y1 - 0.02, 0.005, H - 0.02, m); hz.modifiers.clear()
hz.visible_shadow = False

bm = bmesh.new()
for i in range(350):
    p = Vector((rnd.uniform(FX - 0.7, FX + 0.9), rnd.uniform(0.6, 2.0), rnd.uniform(0.3, 1.6)))
    bmesh.ops.create_icosphere(bm, subdivisions=1, radius=rnd.uniform(0.0006, 0.0014), matrix=Matrix.Translation(p))
me = bpy.data.meshes.new("motes"); bm.to_mesh(me); bm.free()
mo = bpy.data.objects.new("dust_motes", me); scene.collection.objects.link(mo); me.materials.append(M["mote"])
mo.visible_shadow = False

# ---------------------------------------------------------------- moon + world
world = bpy.data.worlds.new("night"); scene.world = world; world.use_nodes = True; nt = world.node_tree
env = nt.nodes.new("ShaderNodeTexEnvironment")
env.image = bpy.data.images.load(glob.glob(os.path.join(A, "hdri", "*.hdr"))[0])
mpw = nt.nodes.new("ShaderNodeMapping"); mpw.inputs["Rotation"].default_value = (0, 0, math.radians(110))
link(nt, nt.nodes.new("ShaderNodeTexCoord").outputs["Generated"], mpw.inputs["Vector"])
link(nt, mpw.outputs["Vector"], env.inputs["Vector"])
hsv = nt.nodes.new("ShaderNodeHueSaturation"); hsv.inputs["Saturation"].default_value = 0.6
link(nt, env.outputs["Color"], hsv.inputs["Color"])
bg = nt.nodes["Background"]; bg.inputs["Strength"].default_value = 0.32
link(nt, mixrgb(nt, 1.0, hsv.outputs["Color"], (0.55, 0.65, 0.95, 1), "MULTIPLY"), bg.inputs["Color"])
moon = light("moon", "SUN", (0, 0, 10), 0.5, (0.5, 0.64, 1.0))
moon.data.angle = math.radians(0.8)
moon.rotation_euler = Vector((-0.25, -0.85, -0.5)).to_track_quat("-Z", "Y").to_euler()
light("moon_fill", "AREA", (mx, Y1 - 0.05, (WZ0 + WZ1) / 2), 2.5, (0.6, 0.7, 1.0), (1.0, 1.7), (math.radians(-90), 0, 0))
# rain falling outside (a few streaks in the moonlight)
m = simple("rain", (0.8, 0.85, 0.9), 0.1, **{"Transmission Weight": 1.0})
bm = bmesh.new()
for i in range(500):
    p = Vector((rnd.uniform(WX0 - 2, WX1 + 2), rnd.uniform(Y1 + 0.6, Y1 + 6), rnd.uniform(-1, 5)))
    bmesh.ops.create_cone(bm, cap_ends=False, segments=3, radius1=0.0012, radius2=0.0012, depth=rnd.uniform(0.15, 0.35),
                          matrix=Matrix.Translation(p) @ Matrix.Rotation(0.08, 4, "Y"))
me = bpy.data.meshes.new("rain"); bm.to_mesh(me); bm.free()
ro = bpy.data.objects.new("rain", me); scene.collection.objects.link(ro); me.materials.append(m)
ro.visible_shadow = False

# ---------------------------------------------------------------- optional: Nagini coiled on the rug
if SNAKE:
    m, nt, p = new_mat("snake_skin")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sm = nt.nodes.new("ShaderNodeMapping"); sm.inputs["Scale"].default_value = (110, 110, 110)
    link(nt, tc.outputs["Object"], sm.inputs["Vector"])
    sc = nt.nodes.new("ShaderNodeTexVoronoi"); sc.feature = "DISTANCE_TO_EDGE"; sc.inputs["Scale"].default_value = 1
    link(nt, sm.outputs["Vector"], sc.inputs["Vector"])
    pat = nt.nodes.new("ShaderNodeTexNoise"); pat.inputs["Scale"].default_value = 4; pat.inputs["Detail"].default_value = 4
    pm = nt.nodes.new("ShaderNodeMapping"); pm.inputs["Scale"].default_value = (2.5, 2.5, 2.5)
    link(nt, tc.outputs["Object"], pm.inputs["Vector"]); link(nt, pm.outputs["Vector"], pat.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeValToRGB"); link(nt, pat.outputs["Fac"], ramp.inputs["Fac"])
    ramp.color_ramp.elements[0].position = 0.42; ramp.color_ramp.elements[0].color = (0.008, 0.01, 0.006, 1)
    ramp.color_ramp.elements[1].position = 0.55; ramp.color_ramp.elements[1].color = (0.05, 0.06, 0.03, 1)
    edge = math_node(nt, "MULTIPLY", sc.outputs["Distance"], 5, True)
    link(nt, mixrgb(nt, math_node(nt, "SUBTRACT", 1, edge, True), ramp.outputs["Color"], (0.01, 0.01, 0.008, 1)), p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = 0.32; p.inputs["Coat Weight"].default_value = 0.3
    bmp = nt.nodes.new("ShaderNodeBump"); bmp.inputs["Distance"].default_value = 0.002
    link(nt, edge, bmp.inputs["Height"]); link(nt, bmp.outputs["Normal"], p.inputs["Normal"])
    cu = bpy.data.curves.new("nagini", "CURVE"); cu.dimensions = "3D"; cu.bevel_depth = 1.0
    cu.bevel_resolution = 6; cu.resolution_u = 24; cu.use_fill_caps = True
    sp = cu.splines.new("NURBS"); n = 46
    sp.points.add(n - 1)
    cx, cy = FX - 0.12, 1.42
    for i in range(n):
        t = i / (n - 1)
        if t < 0.78:                       # spiral coil
            a = t / 0.78 * 2.2 * 2 * math.pi; r = 0.34 - 0.2 * (t / 0.78) + 0.03 * math.sin(3.0 * a)
            x, y, z = cx + r * math.cos(a), cy + r * math.sin(a), 0.06 + 0.07 * (t / 0.78)
        else:                              # head lifts off the coil, towards the fire
            u = (t - 0.78) / 0.22
            x, y, z = cx + 0.12 + 0.16 * u, cy - 0.02 + 0.2 * u, 0.12 + 0.22 * math.sin(u * 2.0)
        rad = 0.055 * (0.35 + 0.65 * math.sin(math.pi * min(1, t * 1.25 + 0.06))) if t < 0.96 else 0.03
        sp.points[i].co = (x, y, z, 1); sp.points[i].radius = rad
    sp.use_endpoint_u = True; sp.order_u = 4
    sn = bpy.data.objects.new("nagini", cu); scene.collection.objects.link(sn); cu.materials.append(m)
    # tail starts outside: reverse so the tail end is thin
    sp.points[0].radius = 0.004
    # wedge-shaped head at the raised end, pointing along the body
    hp = Vector(sp.points[n - 1].co[:3]); hd = (hp - Vector(sp.points[n - 3].co[:3])).normalized()
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=1, location=hp + hd * 0.035)
    hd_o = bpy.context.object; hd_o.name = "nagini_head"
    hd_o.rotation_euler = hd.to_track_quat("X", "Z").to_euler(); hd_o.scale = (0.065, 0.04, 0.026)
    hd_o.data.materials.append(m); bpy.ops.object.shade_smooth()

# ---------------------------------------------------------------- camera + render settings
cam_d = bpy.data.cameras.new("cam"); cam_d.lens = 35; cam_d.sensor_width = 36
cam = bpy.data.objects.new("cam", cam_d); scene.collection.objects.link(cam); scene.camera = cam
cam.location = (-0.35, -2.55, 1.2); look_at(cam, (0.45, 2.6, 1.02))
cam_d.dof.use_dof = True; cam_d.dof.focus_distance = 3.55; cam_d.dof.aperture_fstop = 4.0

r = scene.render; r.engine = "CYCLES"; r.resolution_x = 1920; r.resolution_y = 1080; r.resolution_percentage = RES
r.image_settings.file_format = "PNG"; r.image_settings.color_depth = "16"
c = scene.cycles
prefs = bpy.context.preferences.addons["cycles"].preferences
for dt in ("OPTIX", "CUDA"):
    try:
        prefs.compute_device_type = dt; prefs.get_devices()
        gpus = [d for d in prefs.devices if d.type == dt]
        if gpus:
            for d in prefs.devices: d.use = d.type == dt
            c.device = "GPU"; print("device", dt, [d.name for d in gpus]); break
    except Exception as e:
        print("no", dt, e)
c.samples = SAMPLES; c.use_adaptive_sampling = True; c.adaptive_threshold = 0.015
c.use_denoising = True
try: c.denoiser = "OPENIMAGEDENOISE"
except Exception: pass
c.max_bounces = 6; c.diffuse_bounces = 3; c.glossy_bounces = 3; c.transmission_bounces = 6
c.volume_bounces = 0; c.transparent_max_bounces = 8; c.caustics_reflective = False; c.caustics_refractive = False
c.sample_clamp_indirect = 6.0; c.blur_glossy = 1.0
if hasattr(c, "volume_step_rate"): c.volume_step_rate = 2.0
if hasattr(c, "volume_max_steps"): c.volume_max_steps = 512
# fire point lights skip the haze and the firebox walls (flames + embers light those)
hz_coll = bpy.data.collections.new("haze_only"); hz_coll.objects.link(hz)
for o in bpy.data.objects:
    if o.name.startswith(("firebox_", "fire_log", "embers")): hz_coll.objects.link(o)
for ln in ("fire_a", "fire_b", "fire_floor"):
    lo = bpy.data.objects[ln]; lo.light_linking.receiver_collection = hz_coll
    for co in hz_coll.collection_objects: co.light_linking.link_state = "EXCLUDE"
vs = scene.view_settings; vs.view_transform = "AgX"
for look in ("AgX - Medium Low Contrast", "Medium Low Contrast"):
    try: vs.look = look; break
    except Exception: pass
vs.exposure = arg("--exposure", 0.6)

bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, "voldemort_room.blend"))
if "--border" in argv:
    bx = [float(v) for v in argv[argv.index("--border") + 1].split(",")]
    r.use_border = True; r.use_crop_to_border = True
    r.border_min_x, r.border_max_x, r.border_min_y, r.border_max_y = bx
if not NORENDER:
    r.filepath = os.path.join(HERE, OUT + ".png")
    t0 = time.time()
    bpy.ops.render.render(write_still=True)
    print(f"RENDER_TIME {time.time() - t0:.1f}s -> {r.filepath}")
