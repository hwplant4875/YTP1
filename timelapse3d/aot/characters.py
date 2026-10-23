"""Child Eren and Mikasa for the 845 opening (MPFB2 / MakeHuman CC0 base mesh + default rig).

Anime S1E1: Eren (10) asleep sitting against the big tree on the hill, his firewood frame beside him;
Mikasa (9) standing over him to wake him, red scarf, long black hair.

make_eren(), make_mikasa() return the armature; firewood_frame() returns a loaded A-frame carrier;
place_opening(base, trunk_r, facing) puts all of them at the tree.
"""
import bpy, bmesh, importlib, math, os, random
from mathutils import Vector, Matrix

_mp = "bl_ext.user_default.mpfb"
HS = importlib.import_module(_mp + ".services.humanservice").HumanService
TS = importlib.import_module(_mp + ".services.targetservice").TargetService
ASSET = importlib.import_module(_mp + ".services.assetservice").AssetService

AGE = lambda years: 0.1875 * (years - 1) / 10.0          # MPFB age macro: 0 = 1 yr, 0.1875 = 11 yr

# ---------------------------------------------------------------- materials
def _cloth(name, color, fold=0.25, scale=40.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; N = nt.nodes; L = nt.links; b = N["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1); b.inputs["Roughness"].default_value = 0.85
    b.inputs["Sheen Weight"].default_value = 0.3
    tc = N.new("ShaderNodeTexCoord")
    wv = N.new("ShaderNodeTexWave"); wv.bands_direction = "Z"; wv.inputs["Scale"].default_value = scale
    wv.inputs["Distortion"].default_value = 6; wv.inputs["Detail"].default_value = 2
    L.new(tc.outputs["Object"], wv.inputs["Vector"])
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 25; nz.inputs["Detail"].default_value = 4
    L.new(tc.outputs["Object"], nz.inputs["Vector"])
    mx = N.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.blend_type = "MULTIPLY"; mx.inputs["Factor"].default_value = 0.18
    mx.inputs["A"].default_value = (*color, 1)
    L.new(nz.outputs["Color"], mx.inputs["B"]); L.new(mx.outputs["Result"], b.inputs["Base Color"])
    bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = fold
    L.new(wv.outputs["Fac"], bp.inputs["Height"]); L.new(bp.outputs["Normal"], b.inputs["Normal"])
    return m

def _flat(name, color, rough=0.6, sss=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1); b.inputs["Roughness"].default_value = rough
    if sss:
        b.inputs["Subsurface Weight"].default_value = sss
        b.inputs["Subsurface Radius"].default_value = (1.0, 0.35, 0.2); b.inputs["Subsurface Scale"].default_value = 0.01
    return m

def _textured(name, png, tint=None, rough=0.5, alpha=False):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; N = nt.nodes; L = nt.links; b = N["Principled BSDF"]
    im = N.new("ShaderNodeTexImage"); im.image = bpy.data.images.load(png, check_existing=True)
    b.inputs["Roughness"].default_value = rough
    if tint:
        mx = N.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.blend_type = "MULTIPLY"; mx.inputs["Factor"].default_value = 1.0
        L.new(im.outputs["Color"], mx.inputs["A"]); mx.inputs["B"].default_value = (*tint, 1)
        L.new(mx.outputs["Result"], b.inputs["Base Color"])
    else:
        L.new(im.outputs["Color"], b.inputs["Base Color"])
    if alpha:
        L.new(im.outputs["Alpha"], b.inputs["Alpha"])
    return m

EYE_COLOURS = {"green": (0.04, 0.30, 0.24), "grey": (0.10, 0.10, 0.12)}

def _eye_mat(name, iris):
    """Eyeball facing -Y: white, iris ring, black pupil (object-space normal, so it follows the head)."""
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; N = nt.nodes; L = nt.links; b = N["Principled BSDF"]
    tc = N.new("ShaderNodeTexCoord"); sep = N.new("ShaderNodeSeparateXYZ")
    L.new(tc.outputs["Normal"], sep.inputs[0])
    rp = N.new("ShaderNodeValToRGB"); e = rp.color_ramp.elements; rp.color_ramp.interpolation = "CONSTANT"
    e[0].position, e[0].color = 0.0, (0.01, 0.01, 0.01, 1)
    e[1].position, e[1].color = 0.035, (*iris, 1)
    e2 = rp.color_ramp.elements.new(0.12); e2.color = (0.85, 0.83, 0.8, 1)
    ad = N.new("ShaderNodeMath"); ad.operation = "ADD"; ad.inputs[1].default_value = 1.0
    L.new(sep.outputs["Y"], ad.inputs[0]); L.new(ad.outputs[0], rp.inputs["Fac"])
    L.new(rp.outputs["Color"], b.inputs["Base Color"]); b.inputs["Roughness"].default_value = 0.08
    return m

# ---------------------------------------------------------------- body
def _bake_and_clean(body):
    if body.data.shape_keys:
        TS.bake_targets(body)
    mask = next((m for m in body.modifiers if m.type == "MASK"), None)
    if mask:
        vg = body.vertex_groups.get(mask.vertex_group)
        keep = set()
        if vg:
            for v in body.data.vertices:
                for g in v.groups:
                    if g.group == vg.index and g.weight > 0.5:
                        keep.add(v.index)
        bm = bmesh.new(); bm.from_mesh(body.data); bm.verts.ensure_lookup_table()
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if (v.index in keep) == mask.invert_vertex_group], context="VERTS")
        bm.to_mesh(body.data); bm.free()
        body.modifiers.remove(mask)

def _asset(subdir, rel):
    try:
        return ASSET.find_asset_absolute_path(rel, asset_subdir=subdir)
    except Exception:
        return None

def _region(bone):
    """Clothing region of a deform bone."""
    if bone.startswith(("foot", "toe", "lowerleg02")):
        return "boots"
    if bone.startswith(("pelvis", "upperleg", "lowerleg", "root")):
        return "legs"
    if bone.startswith(("spine", "breast", "clavicle", "shoulder", "upperarm", "lowerarm")):
        return "shirt"
    return "skin"

def _paint_regions(body, mats):
    """Material index per face from the dominant bone weight of its vertices."""
    names = {g.index: g.name for g in body.vertex_groups}
    me = body.data
    order = list(mats.keys())
    for k in order:
        me.materials.append(mats[k])
    vreg = []
    for v in me.vertices:
        best, bw = "skin", 0.0
        for g in v.groups:
            n = names.get(g.group, "")
            if g.weight > bw and n and not n.startswith(("joint", "helper", "Left", "Right", "Mid", "body")) and n not in ("lips", "ears", "scalp", "nipple", "nippleTip", "fingernails", "toenails", "genitals", "JointCubes", "HelperGeometry"):
                best, bw = _region(n), g.weight
        vreg.append(best)
    for p in me.polygons:
        regs = [vreg[i] for i in p.vertices]
        r = max(set(regs), key=regs.count)
        p.material_index = order.index(r if r in mats else "skin")
        p.use_smooth = True

def _shell(body, rig, mats, regions, push=0.007, name="shell", smooth=0):
    """Loose cloth layer: copy of the body faces of the given regions pushed out along the normals."""
    sh = body.copy(); sh.data = body.data.copy(); sh.name = body.name + "_" + name
    bpy.context.scene.collection.objects.link(sh)
    idx = [list(mats.keys()).index(r) for r in regions]
    bm = bmesh.new(); bm.from_mesh(sh.data)
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.material_index not in idx], context="FACES")
    bm.to_mesh(sh.data); bm.free()
    sh.modifiers.clear()
    if smooth:
        sm = sh.modifiers.new("blur", "SMOOTH"); sm.factor = 1.0; sm.iterations = smooth
    d = sh.modifiers.new("loose", "DISPLACE"); d.strength = push; d.mid_level = 0.0
    a = sh.modifiers.new("rig", "ARMATURE"); a.object = rig
    sol = sh.modifiers.new("thick", "SOLIDIFY"); sol.thickness = 0.004; sol.offset = 1.0
    sh.parent = rig
    return sh

def _child(name, years, gender, hair, hair_col, eyes, outfit, macro=None, height=None):
    iris = EYE_COLOURS[eyes]
    md = TS.get_default_macro_info_dict()
    md.update(dict(gender=gender, age=AGE(years), muscle=0.5, weight=0.42, proportions=0.6))
    if macro:
        md.update(macro)
    body = HS.create_human(feet_on_ground=True, scale=0.1, macro_detail_dict=md)
    rig = HS.add_builtin_rig(body, "default")
    TS.bake_targets(body)
    parts = []
    f = _asset("hair", f"{hair}/{hair}.mhclo")
    if f:
        try:
            h = HS.add_mhclo_asset(f, body, asset_type="Hair", subdiv_levels=0)
            png = os.path.join(os.path.dirname(f), f"{hair}_diffuse.png")
            parts.append((h, lambda png=png: _textured(name + "_hair", png, hair_col, rough=0.45, alpha=True) if os.path.exists(png)
                          else _flat(name + "_hair", hair_col)))
        except Exception as ex:
            print("hair failed", ex)
    f = _asset("eyes", "high-poly/high-poly.mhclo")
    if f:
        try:
            e = HS.add_mhclo_asset(f, body, asset_type="Eyes", subdiv_levels=0)
            png = os.path.join(os.path.dirname(os.path.dirname(f)), "materials", f"{eyes}_eye.png")
            parts.append((e, lambda: _eye_mat(name + "_eyes", iris)))
        except Exception as ex:
            print("eyes failed", ex)
    f = _asset("eyebrows", "eyebrow010/eyebrow010.mhclo")
    if f:
        try:
            eb = HS.add_mhclo_asset(f, body, asset_type="Eyebrows", subdiv_levels=0)
            png = os.path.join(os.path.dirname(f), "eyebrow010.png")
            parts.append((eb, lambda png=png: _textured(name + "_brows", png, hair_col, alpha=True)))
        except Exception as ex:
            print("brows failed", ex)
    _bake_and_clean(body)
    for ob, mk in parts:
        ob.data.materials.clear(); ob.data.materials.append(mk())
    rig.name = name; body.name = name + "_body"
    body.data.materials.clear()
    mats = {"skin": _flat(name + "_skin", (0.66, 0.44, 0.33), rough=0.5, sss=0.15)}
    outfit = outfit()                                  # built late: MPFB purges unused materials while building
    mats.update(outfit)
    _paint_regions(body, mats)
    _shell(body, rig, mats, [r for r in ("shirt", "legs") if r in outfit], name="clothes")
    if "boots" in outfit:
        boots(name, rig, body, outfit["boots"])
    if height:
        s = height / body.dimensions.z
        rig.scale = (s, s, s)
    return rig, body

def make_eren(name="Eren"):
    """Eren, 10: messy dark-brown hair, green eyes, off-white long-sleeved shirt, dark brown trousers, brown boots."""
    rig, body = _child(name, 10, 1.0, "short02", (0.10, 0.055, 0.03), "green",
                       lambda: {"shirt": _cloth(name + "_shirt", (0.78, 0.74, 0.64)),
                                "legs": _cloth(name + "_trousers", (0.16, 0.11, 0.07), scale=30),
                                "boots": _flat(name + "_boots", (0.11, 0.055, 0.025), rough=0.45)}, height=1.38)
    return rig

def make_mikasa(name="Mikasa"):
    """Mikasa, 9: long black hair, grey eyes, cream long-sleeved blouse, long brown skirt, red scarf."""
    rig, body = _child(name, 9, 0.0, "long01", (0.018, 0.017, 0.02), "grey",
                       lambda: {"shirt": _cloth(name + "_blouse", (0.80, 0.74, 0.66)),
                                "legs": _cloth(name + "_stockings", (0.12, 0.08, 0.06), scale=30),
                                "boots": _flat(name + "_boots", (0.12, 0.06, 0.03), rough=0.45)},
                       macro=dict(proportions=0.7), height=1.33)
    skirt(name, rig)
    scarf(name, rig)
    return rig

def _bone_world(rig, bone, at="head"):
    bpy.context.view_layer.update()
    pb = rig.pose.bones[bone]
    return rig.matrix_world @ (pb.head if at == "head" else pb.tail)

def skirt(name, rig, color=(0.30, 0.17, 0.09)):
    """A-line skirt from the waist to mid-calf, bone-parented to the pelvis."""
    hip = rig.data.bones["upperleg01.L"].head_local.z
    hw = abs(rig.data.bones["upperleg01.L"].head_local.x)
    bm = bmesh.new()
    rows = [(hip + 0.06, hw + 0.06), (hip - 0.02, hw + 0.085), (hip * 0.78, hw + 0.10), (hip * 0.56, hw + 0.115), (hip * 0.42, hw + 0.12)]
    n = 28
    vs = []
    for z, r in rows:
        ring = []
        for k in range(n):
            a = k / n * 2 * math.pi
            rr = r * (1 + 0.05 * math.sin(a * 7)) if z < 0.7 else r                      # soft pleats
            ring.append(bm.verts.new((math.cos(a) * rr, math.sin(a) * rr * 0.82, z)))
        vs.append(ring)
    for i in range(len(vs) - 1):
        for k in range(n):
            bm.faces.new((vs[i][k], vs[i][(k + 1) % n], vs[i + 1][(k + 1) % n], vs[i + 1][k]))
    me = bpy.data.meshes.new(name + "_skirt"); bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = True
    me.materials.append(_cloth(name + "_skirt", color, fold=0.4, scale=18))
    ob = bpy.data.objects.new(name + "_skirt", me); bpy.context.scene.collection.objects.link(ob)
    sol = ob.modifiers.new("thick", "SOLIDIFY"); sol.thickness = 0.006
    _bind(ob, rig, "spine05")
    return ob

def scarf(name, rig, color=(0.55, 0.035, 0.03)):
    """Mikasa's red scarf: a thick loop round the neck with one tail hanging down the front."""
    bm = bmesh.new()
    n, m = 24, 8
    def tube(path, rad):
        rings = []
        for i, (p, t) in enumerate(path):
            t = t.normalized(); u = t.orthogonal().normalized(); w = t.cross(u)
            rings.append([bm.verts.new(p + (u * math.cos(a) * rad[0] + w * math.sin(a) * rad[1]))
                          for a in (k / m * 2 * math.pi for k in range(m))])
        for i in range(len(rings) - 1):
            for k in range(m):
                bm.faces.new((rings[i][k], rings[i][(k + 1) % m], rings[i + 1][(k + 1) % m], rings[i + 1][k]))
    nb = rig.data.bones["neck01"]
    neck_z = nb.head_local.z + 0.01; ny = nb.head_local.y
    body = bpy.data.objects[name + "_body"]
    ring = [v.co for v in body.data.vertices if abs(v.co.z - neck_z) < 0.012]
    rx = max(abs(p.x) for p in ring) + 0.022 if ring else 0.07
    ry = max(abs(p.y - ny) for p in ring) + 0.022 if ring else 0.065
    loop = []
    for k in range(n + 1):
        a = k / n * 2 * math.pi
        p = Vector((math.cos(a) * rx, ny + math.sin(a) * ry, neck_z - 0.01 + 0.012 * math.sin(a * 2)))
        t = Vector((-math.sin(a), math.cos(a), 0))
        loop.append((p, t))
    tube(loop, (0.035, 0.03))
    tail = [(Vector((0.045 + 0.008 * k, ny - ry - 0.01 - 0.006 * k, neck_z - 0.03 - 0.045 * k)), Vector((0.1, -0.1, -1))) for k in range(6)]
    tube(tail, (0.038, 0.012))
    me = bpy.data.meshes.new(name + "_scarf"); bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = True
    me.materials.append(_cloth(name + "_scarf", color, fold=0.5, scale=60))
    ob = bpy.data.objects.new(name + "_scarf", me); bpy.context.scene.collection.objects.link(ob)
    _bind(ob, rig, "spine01")
    return ob

def boots(name, rig, body, m):
    """Leather ankle boots: a rounded shoe over each foot plus a shaft up the shin."""
    out = []
    for side, sg in (("L", 1), ("R", -1)):
        feet = [v.co for v in body.data.vertices if v.co.z < 0.075 and v.co.x * sg > 0.02]
        if not feet:
            continue
        x0, x1 = min(p.x for p in feet), max(p.x for p in feet)
        y0, y1 = min(p.y for p in feet), max(p.y for p in feet)
        bm = bmesh.new()
        sph = bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=10, radius=1.0)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        for v in sph["verts"]:
            v.co = Vector((cx + v.co.x * ((x1 - x0) / 2 + 0.012), cy - 0.006 + v.co.y * ((y1 - y0) / 2 + 0.02),
                           max(0.0, 0.035 + v.co.z * 0.045)))
        ank = rig.data.bones[f"lowerleg02.{side}"]
        a, b = ank.tail_local, ank.tail_local.lerp(ank.head_local, 0.55)
        ring = [v.co for v in body.data.vertices if abs(v.co.z - (a.z + b.z) / 2) < 0.015 and v.co.x * sg > 0.02]
        r = max((Vector((p.x, p.y)) - Vector((a.x, a.y))).length for p in ring) + 0.012 if ring else 0.045
        cyl = bmesh.ops.create_cone(bm, cap_ends=False, segments=16, radius1=r, radius2=r * 1.08, depth=(b.z - a.z) + 0.04)
        bmesh.ops.translate(bm, vec=(a.x, a.y, (a.z + b.z) / 2 - 0.01), verts=cyl["verts"])
        me = bpy.data.meshes.new(f"{name}_boot{side}"); bm.to_mesh(me); bm.free()
        for p in me.polygons:
            p.use_smooth = True
        me.materials.append(m)
        ob = bpy.data.objects.new(f"{name}_boot{side}", me); bpy.context.scene.collection.objects.link(ob)
        foot = ob.vertex_groups.new(name=f"foot.{side}"); shin = ob.vertex_groups.new(name=f"lowerleg02.{side}")
        for v in me.vertices:
            (shin if v.co.z > 0.07 else foot).add([v.index], 1.0, "REPLACE")
        ob.modifiers.new("rig", "ARMATURE").object = rig
        ob.parent = rig
        out.append(ob)
    return out

def _bind(ob, rig, bone):
    """Deform a prop rigidly with one bone (armature modifier, all vertices weighted to it)."""
    vg = ob.vertex_groups.new(name=bone); vg.add(range(len(ob.data.vertices)), 1.0, "REPLACE")
    ob.modifiers.new("rig", "ARMATURE").object = rig
    ob.parent = rig

# ---------------------------------------------------------------- poses
def _rot(rig, bone, x=0.0, y=0.0, z=0.0):
    pb = rig.pose.bones.get(bone)
    if pb:
        pb.rotation_mode = "XYZ"; pb.rotation_euler = (x, y, z)

def pose_asleep(rig):
    """Sitting on the grass leaning back against the trunk, legs out, head dropped to one side."""
    for s in ("L", "R"):
        _rot(rig, f"upperleg01.{s}", x=-1.45, z=(0.12 if s == "L" else -0.12))
    _rot(rig, "lowerleg01.L", x=0.25); _rot(rig, "lowerleg01.R", x=0.75)          # right knee a little up
    _rot(rig, "spine05", x=-0.32)
    _rot(rig, "neck01", x=0.3, z=0.15); _rot(rig, "head", x=0.15, z=0.3)
    for s, sg in (("L", -1), ("R", 1)):
        _rot(rig, f"upperarm01.{s}", x=-0.25, z=sg * 0.85)
        _rot(rig, f"lowerarm01.{s}", x=0.55)
    for s in ("L", "R"):                                                             # eyes shut
        _rot(rig, f"orbicularis03.{s}", x=-0.45)

def pose_standing(rig, look_down=0.35):
    """Standing, looking down at Eren, hands together in front."""
    _rot(rig, "neck01", x=look_down * 0.6); _rot(rig, "head", x=look_down * 0.4)
    for s, sg in (("L", -1), ("R", 1)):
        _rot(rig, f"upperarm01.{s}", x=-0.1, z=sg * 0.8)
        _rot(rig, f"lowerarm01.{s}", x=0.35)

# ---------------------------------------------------------------- props
def firewood_frame(name, loaded=True, seed=0):
    """Wooden A-frame back carrier with a bundle of firewood tied on with rope (as carried in S1E1)."""
    rnd = random.Random(seed)
    bm = bmesh.new()
    def stick(a, b, r, mi):
        a, b = Vector(a), Vector(b); d = b - a
        c = bmesh.ops.create_cone(bm, cap_ends=True, segments=7, radius1=r, radius2=r * 0.9, depth=d.length)
        q = d.to_track_quat("Z", "Y")
        bmesh.ops.transform(bm, matrix=Matrix.Translation((a + b) / 2) @ q.to_matrix().to_4x4(), verts=c["verts"])
        for v in c["verts"]:
            for f in v.link_faces:
                f.material_index = mi
    for x in (-0.17, 0.17):                                                  # posts
        stick((x, 0, 0), (x * 0.8, 0.02, 0.95), 0.018, 0)
    for z in (0.12, 0.45, 0.8):                                              # cross bars
        stick((-0.19, 0.0, z), (0.19, 0.0, z), 0.012, 0)
    if loaded:
        for k in range(26):                                                  # firewood logs across the frame
            x0 = rnd.uniform(-0.12, 0.12); z0 = rnd.uniform(0.15, 0.78); y0 = rnd.uniform(0.04, 0.2)
            L = rnd.uniform(0.55, 0.75)
            stick((-L / 2 + x0 * 0.3, y0, z0), (L / 2 + x0 * 0.3, y0 + rnd.uniform(-0.03, 0.03), z0 + rnd.uniform(-0.04, 0.04)),
                  rnd.uniform(0.018, 0.032), 1)
        for z in (0.3, 0.62):                                                # rope bands
            for x in (-0.12, 0.12):
                c = bmesh.ops.create_cone(bm, cap_ends=False, segments=10, radius1=0.13, radius2=0.13, depth=0.025)
                bmesh.ops.transform(bm, matrix=Matrix.Translation((x, 0.11, z)) @ Matrix.Rotation(math.pi / 2, 4, "Y") @ Matrix.Diagonal((1, 1, 1, 1)), verts=c["verts"])
                for v in c["verts"]:
                    for f in v.link_faces:
                        f.material_index = 2
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    me.materials.append(_flat(name + "_frame", (0.30, 0.19, 0.10), 0.8))
    me.materials.append(_cloth(name + "_logs", (0.36, 0.25, 0.15), fold=0.6, scale=12))
    me.materials.append(_flat(name + "_rope", (0.55, 0.47, 0.32), 0.9))
    ob = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(ob)
    return ob

def _surface(trunk, base, fwd, z, fallback):
    """Distance from the trunk axis to its bark along fwd at height z (ray cast from outside)."""
    if trunk is None:
        return fallback
    bpy.context.view_layer.update()
    inv = trunk.matrix_world.inverted()
    o = inv @ (base + fwd * 20 + Vector((0, 0, z))); d = (inv.to_3x3() @ -fwd).normalized()
    hit, loc, n, i = trunk.ray_cast(o, d)
    return (trunk.matrix_world @ loc - (base + Vector((0, 0, z)))).length if hit else fallback

def place_opening(base, trunk_r=1.6, facing=0.0, trunk=None):
    """Eren asleep against the trunk, Mikasa standing at his side, two firewood frames on the grass.
    base: trunk centre on the ground (Vector); facing: direction Eren faces (radians about Z, 0 = -Y);
    trunk: the trunk object, if given its bark is found by ray casting."""
    base = Vector(base)
    rot = Matrix.Rotation(facing, 4, "Z")
    fwd = (rot @ Vector((0, -1, 0, 0))).to_3d(); side = (rot @ Vector((1, 0, 0, 0))).to_3d()
    trunk_r = max(_surface(trunk, base, fwd, z, trunk_r) for z in (0.3, 0.6, 0.9))
    eren = make_eren(); pose_asleep(eren)
    eren.location = base + fwd * (trunk_r + 0.02) + Vector((0, 0, -0.62)); eren.rotation_euler = (0.0, 0.0, facing)
    mik = make_mikasa(); pose_standing(mik)
    mik.location = base + fwd * (trunk_r + 1.35) + side * 0.7; mik.rotation_euler = (0.0, 0.0, facing + math.pi * 1.15)
    f1 = firewood_frame("Firewood_Eren", seed=1)
    f1.location = base + fwd * (trunk_r + 0.25) - side * 1.35 + Vector((0, 0, 0.03)); f1.rotation_euler = (1.5, 0, facing + 1.2)
    f2 = firewood_frame("Firewood_Mikasa", seed=2)
    f2.location = base + fwd * (trunk_r - 0.05) + side * 1.6; f2.rotation_euler = (0.32, 0, facing - 0.35)      # leaning on the trunk
    return eren, mik, f1, f2


def _bark():
    m = bpy.data.materials.new("ErenTree_bark"); m.use_nodes = True
    nt = m.node_tree; N = nt.nodes; L = nt.links; b = N["Principled BSDF"]
    tc = N.new("ShaderNodeTexCoord")
    mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (7.0, 7.0, 0.8)     # vertical bark fissures
    L.new(tc.outputs["Object"], mp.inputs["Vector"])
    wv = N.new("ShaderNodeTexNoise"); wv.inputs["Scale"].default_value = 2.2; wv.inputs["Detail"].default_value = 8
    wv.inputs["Roughness"].default_value = 0.65
    L.new(mp.outputs["Vector"], wv.inputs["Vector"])
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 0.9; nz.inputs["Detail"].default_value = 6
    L.new(tc.outputs["Object"], nz.inputs["Vector"])
    moss = N.new("ShaderNodeMapRange"); moss.inputs["From Min"].default_value = 0.48; moss.inputs["From Max"].default_value = 0.6
    L.new(nz.outputs["Fac"], moss.inputs["Value"])
    mx = N.new("ShaderNodeMix"); mx.data_type = "RGBA"
    L.new(moss.outputs["Result"], mx.inputs["Factor"])
    rp = N.new("ShaderNodeValToRGB"); e = rp.color_ramp.elements
    e[0].position, e[0].color = 0.35, (0.06, 0.05, 0.035, 1); e[1].position, e[1].color = 0.65, (0.23, 0.20, 0.16, 1)
    L.new(wv.outputs["Fac"], rp.inputs["Fac"]); L.new(rp.outputs["Color"], mx.inputs["A"])
    mx.inputs["B"].default_value = (0.13, 0.20, 0.05, 1)                      # moss / ivy
    L.new(mx.outputs["Result"], b.inputs["Base Color"]); b.inputs["Roughness"].default_value = 0.9
    bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.6
    L.new(wv.outputs["Fac"], bp.inputs["Height"]); L.new(bp.outputs["Normal"], b.inputs["Normal"])
    return m

def eren_tree(base, seed=3, height=17.0):
    """The big broad-leaved tree on the hill (S1E1 / final episode): thick mossy trunk, flared roots,
    heavy limbs and a wide rounded crown. Returns (trunk object, crown object, trunk radius at the base)."""
    rnd = random.Random(seed)
    base = Vector(base)
    bm = bmesh.new()
    def limb(a, b, r0, r1, seg=10, rings=6, wob=0.0):
        a, b = Vector(a), Vector(b); d = b - a
        q = d.to_track_quat("Z", "Y").to_matrix()
        prev = None
        for i in range(rings + 1):
            t = i / rings
            r = r0 + (r1 - r0) * t
            ring = []
            for k in range(seg):
                ang = k / seg * 2 * math.pi
                rr = r * (1 + wob * math.sin(ang * 5 + i) * (1 - t))
                ring.append(bm.verts.new(a + d * t + q @ Vector((math.cos(ang) * rr, math.sin(ang) * rr, 0))))
            if prev:
                for k in range(seg):
                    bm.faces.new((prev[k], prev[(k + 1) % seg], ring[(k + 1) % seg], ring[k]))
            prev = ring
    R0 = 0.85
    limb((0, 0, -0.5), (0.2, 0.1, height * 0.42), R0 * 1.25, R0 * 0.62, seg=18, rings=10, wob=0.22)   # trunk with root flare
    crown = []
    top = Vector((0.2, 0.1, height * 0.42))
    for k in range(6):                                                         # main limbs
        ang = k / 6 * 2 * math.pi + rnd.uniform(-0.3, 0.3)
        reach = rnd.uniform(4.5, 6.5)
        end = top + Vector((math.cos(ang) * reach, math.sin(ang) * reach, rnd.uniform(3.0, 5.5)))
        limb(top - Vector((0, 0, 0.8)), end, R0 * 0.38, 0.12, seg=8, rings=4)
        crown.append(end)
    crown.append(top + Vector((0, 0, 7.0)))
    me = bpy.data.meshes.new("ErenTree_trunk"); bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = True
    me.materials.append(_bark())
    trunk = bpy.data.objects.new("ErenTree_trunk", me); bpy.context.scene.collection.objects.link(trunk)
    trunk.location = base
    cb = bmesh.new()
    for c in crown:                                                            # leaf clumps around each limb end
        for j in range(5):
            r = rnd.uniform(2.4, 3.6)
            ico = bmesh.ops.create_icosphere(cb, subdivisions=3, radius=r)
            off = Vector((rnd.uniform(-2.2, 2.2), rnd.uniform(-2.2, 2.2), rnd.uniform(-0.8, 1.6)))
            for v in ico["verts"]:
                v.co = c + off + Vector((v.co.x, v.co.y, v.co.z * 0.72)) + Vector((rnd.uniform(-.25, .25), rnd.uniform(-.25, .25), rnd.uniform(-.25, .25)))
    cme = bpy.data.meshes.new("ErenTree_crown"); cb.to_mesh(cme); cb.free()
    leaf = bpy.data.materials.new("ErenTree_leaf"); leaf.use_nodes = True
    nt = leaf.node_tree; N = nt.nodes; L = nt.links; b = N["Principled BSDF"]
    tc = N.new("ShaderNodeTexCoord"); vo = N.new("ShaderNodeTexVoronoi"); vo.inputs["Scale"].default_value = 2.5
    L.new(tc.outputs["Object"], vo.inputs["Vector"])
    rp = N.new("ShaderNodeValToRGB"); e = rp.color_ramp.elements
    e[0].color = (0.05, 0.13, 0.02, 1); e[1].color = (0.22, 0.42, 0.07, 1)
    L.new(vo.outputs["Distance"], rp.inputs["Fac"]); L.new(rp.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.8
    b.inputs["Subsurface Weight"].default_value = 0.1
    bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.9
    L.new(vo.outputs["Distance"], bp.inputs["Height"]); L.new(bp.outputs["Normal"], b.inputs["Normal"])
    cme.materials.append(leaf)
    cr = bpy.data.objects.new("ErenTree_crown", cme); bpy.context.scene.collection.objects.link(cr)
    tx = bpy.data.textures.new("ErenTree_leafnoise", "CLOUDS"); tx.noise_scale = 0.9
    dm = cr.modifiers.new("clumps", "DISPLACE"); dm.texture = tx; dm.strength = 0.9
    cr.location = base
    return trunk, cr, R0
