"""Child Eren and Mikasa for the 845 opening (MPFB2 / MakeHuman CC0 base mesh + default rig).

Anime S1E1: Eren (10) asleep sitting against the big tree on the hill, his firewood frame beside him;
Mikasa (9) standing over him to wake him, red scarf, long black hair.

make_eren(), make_mikasa() return the armature; firewood_frame() returns a loaded A-frame carrier;
place_opening(base, trunk_r, facing) puts all of them at the tree.
"""
import bpy, bmesh, importlib, math, os, random
from mathutils import Vector, Matrix

def _find_mpfb():
    """MPFB lives in a different extension repo on the cloud box (user_default) and the laptop (blender_org)."""
    for m in ("bl_ext.user_default.mpfb", "bl_ext.blender_org.mpfb"):
        try:
            importlib.import_module(m)
            return m
        except ImportError:
            pass
    return "bl_ext.user_default.mpfb"
_mp = _find_mpfb()
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

def _faceless(body, rig, name):
    """Replace the head with a smooth egg: no eyes, nose, mouth or ears (house style for 3D people).
    Smoothing the MakeHuman head left the mouth and eye openings visible, so the head faces are cut away."""
    nz = rig.data.bones["neck02"].head_local.z
    co = [v.co.copy() for v in body.data.vertices if v.co.z > nz + 0.015]
    xs = sorted(abs(c.x) for c in co); ys = sorted(c.y for c in co); zs = sorted(c.z for c in co)
    pick = lambda a, q: a[min(len(a) - 1, int(q * len(a)))]
    rx = pick(xs, 0.90); y0, y1 = pick(ys, 0.01), pick(ys, 0.99); z0, z1 = zs[0], zs[-1]
    bm = bmesh.new(); bm.from_mesh(body.data)
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if all(v.co.z > nz + 0.012 for v in f.verts)], context="FACES")
    bm.to_mesh(body.data); bm.free()
    me = bpy.data.meshes.new(name + "_head"); bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=20, radius=1.0)
    cz = (z0 + z1) / 2 + 0.004; ry = (y1 - y0) / 2 * 0.98; rz = (z1 - z0) / 2 * 0.98
    for v in bm.verts:
        x, y, z = v.co
        taper = 1.0 - 0.18 * max(0.0, -z) ** 2                         # narrower jaw, egg shape
        v.co = Vector((x * rx * 1.02 * taper, (y0 + y1) / 2 + y * ry * taper, cz + z * rz))
    bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = True
    ob = bpy.data.objects.new(name + "_head", me); bpy.context.scene.collection.objects.link(ob)
    ob["egg"] = (0.0, (y0 + y1) / 2, cz, rx * 1.02, ry, rz)
    _bind(ob, rig, "head")
    return ob

def hair_cap(name, head, rig, color, front, side, back, spikes=14, spike_amp=0.18, mess=0.05, flare=1.0, part=0.0, seed=1):
    """Anime hair as one shell over the egg head. front/side/back: hem height in head radii from the head centre
    (1 = crown, 0 = equator, below 0 hangs straight down). The hem is cut into pointed clumps."""
    cx, cy, cz, rx, ry, rz = head["egg"]
    rnd = random.Random(seed)
    n, rows = 48, 16
    jit = [1.0 + rnd.uniform(-mess, mess) for _ in range(n)]
    def hem(th):
        sn = math.sin(th)
        fr = max(0.0, -sn) ** 3                                   # narrow fringe at the face (-Y)
        bk = max(0.0, sn)
        return front * fr + back * bk + side * (1 - fr - bk)
    bm = bmesh.new(); grid = []
    for j in range(rows + 1):
        t = j / rows; ring = []
        for k in range(n):
            th = k / n * 2 * math.pi
            h = hem(th)
            if j == rows:
                h -= spike_amp if k % 2 == 0 else -spike_amp * 0.25
            z = 1.0 - t * (1.0 - h)
            if z >= 0:
                c = math.sqrt(max(0.0, 1 - z * z)); r = 1.1
            else:
                c = 1.0 + flare * 0.1 * min(1.0, -z); r = 1.1
            if j == rows:
                r *= 0.97 if k % 2 == 0 else 1.0
            r *= 1.0 + (jit[k] - 1.0) * t
            dx = part * (1 - t) * 0.0
            ring.append(bm.verts.new((cx + math.cos(th) * c * rx * r + dx, cy + math.sin(th) * c * ry * r, cz + max(z, -9) * rz * (1.1 if z > 0 else 1.0))))
        grid.append(ring)
    for j in range(rows):
        for k in range(n):
            bm.faces.new((grid[j][k], grid[j][(k + 1) % n], grid[j + 1][(k + 1) % n], grid[j + 1][k]))
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    me = bpy.data.meshes.new(name + "_hair"); bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = True
    me.materials.append(_flat(name + "_hair", color, rough=0.45))
    ob = bpy.data.objects.new(name + "_hair", me); bpy.context.scene.collection.objects.link(ob)
    sol = ob.modifiers.new("thick", "SOLIDIFY"); sol.thickness = 0.008; sol.offset = -1.0
    _bind(ob, rig, "head")
    return ob

def _shell(body, rig, mats, regions, push=0.007, name="shell", smooth=0, mat=None, open_front=0.0):
    """Loose cloth layer: copy of the body faces of the given regions pushed out along the normals.
    open_front: half width of a front opening (open coat / cardigan); mat: single material for the layer."""
    sh = body.copy(); sh.data = body.data.copy(); sh.name = body.name + "_" + name
    bpy.context.scene.collection.objects.link(sh)
    idx = [list(mats.keys()).index(r) for r in regions]
    bm = bmesh.new(); bm.from_mesh(sh.data)
    arm_x = 0.11
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.material_index not in idx or
                               (open_front and abs(f.calc_center_median().x) < open_front and f.calc_center_median().y < 0
                                and abs(f.calc_center_median().x) < arm_x)], context="FACES")
    bm.to_mesh(sh.data); bm.free()
    sh.modifiers.clear()
    if smooth:
        sm = sh.modifiers.new("blur", "SMOOTH"); sm.factor = 1.0; sm.iterations = smooth
    d = sh.modifiers.new("loose", "DISPLACE"); d.strength = push; d.mid_level = 0.0
    a = sh.modifiers.new("rig", "ARMATURE"); a.object = rig
    sol = sh.modifiers.new("thick", "SOLIDIFY"); sol.thickness = 0.004; sol.offset = 1.0
    if mat:
        sh.data.materials.clear(); sh.data.materials.append(mat)
    sh.parent = rig
    return sh

def _child(name, years, gender, hair, hair_col, outfit, macro=None, height=None, coat=None):
    md = TS.get_default_macro_info_dict()
    md.update(dict(gender=gender, age=AGE(years), muscle=0.5, weight=0.42, proportions=0.6))
    if macro:
        md.update(macro)
    body = HS.create_human(feet_on_ground=True, scale=0.1, macro_detail_dict=md)
    rig = HS.add_builtin_rig(body, "default")
    TS.bake_targets(body)
    parts = []
    f = hair and _asset("hair", f"{hair}/{hair}.mhclo")
    if f:
        try:
            h = HS.add_mhclo_asset(f, body, asset_type="Hair", subdiv_levels=0)
            png = os.path.join(os.path.dirname(f), f"{hair}_diffuse.png")
            parts.append((h, lambda png=png: _textured(name + "_hair", png, hair_col, rough=0.45, alpha=True) if os.path.exists(png)
                          else _flat(name + "_hair", hair_col)))
        except Exception as ex:
            print("hair failed", ex)
    _bake_and_clean(body)
    head = _faceless(body, rig, name)
    for ob, mk in parts:
        ob.data.materials.clear(); ob.data.materials.append(mk())
    rig.name = name; body.name = name + "_body"
    body.data.materials.clear()
    mats = {"skin": _flat(name + "_skin", (0.66, 0.44, 0.33), rough=0.5, sss=0.15)}
    head.data.materials.append(mats["skin"])
    outfit = outfit()                                  # built late: MPFB purges unused materials while building
    mats.update(outfit)
    _paint_regions(body, mats)
    _shell(body, rig, mats, [r for r in ("shirt", "legs") if r in outfit], name="clothes")
    if coat:
        coat = (coat[0](), coat[1])
        _shell(body, rig, mats, ["shirt"], push=0.016, name="coat", mat=coat[0], open_front=0.045)
        tail(name, rig, coat[0], coat[1])
    if "boots" in outfit:
        boots(name, rig, body, outfit["boots"])
    if height:
        s = height / body.dimensions.z
        rig.scale = (s, s, s)
    return rig, body

def make_eren(name="Eren", hair=None):
    """Eren, 10 (S1E1): shaggy schoolboy mop of dark-brown hair, olive-green shirt, open maroon blazer, charcoal cropped trousers."""
    rig, body = _child(name, 10, 1.0, hair, (0.03, 0.02, 0.016),
                       lambda: {"shirt": _cloth(name + "_shirt", (0.13, 0.15, 0.07)),
                                "legs": _cloth(name + "_trousers", (0.028, 0.028, 0.032), scale=30),
                                "boots": _flat(name + "_shoes", (0.03, 0.02, 0.015), rough=0.5)},
                       height=1.38, coat=(lambda: _cloth(name + "_blazer", (0.11, 0.03, 0.028), fold=0.35), 0.2))
    if not hair:
        hair_cap(name, bpy.data.objects[name + "_head"], rig, (0.03, 0.02, 0.016), front=0.32, side=-0.35, back=-0.85,
                 spike_amp=0.34, mess=0.13, flare=1.2, seed=3)
    return rig

def make_mikasa(name="Mikasa", hair=None):
    """Mikasa, 9 (S1E1): straight black shoulder-length hair with bangs, long white dress, long pale-pink cardigan, dark red scarf."""
    rig, body = _child(name, 9, 0.0, hair, (0.012, 0.012, 0.015),
                       lambda: {"shirt": _cloth(name + "_dress", (0.82, 0.79, 0.75)),
                                "legs": _cloth(name + "_dress_l", (0.82, 0.79, 0.75), scale=30),
                                "boots": _flat(name + "_shoes", (0.10, 0.06, 0.04), rough=0.5)},
                       macro=dict(proportions=0.7), height=1.33,
                       coat=(lambda: _cloth(name + "_cardigan", (0.72, 0.47, 0.44), fold=0.3), 0.5))
    skirt(name, rig, color=(0.82, 0.79, 0.75), length=0.12)
    scarf(name, rig, color=(0.20, 0.018, 0.022))
    if not hair:
        hair_cap(name, bpy.data.objects[name + "_head"], rig, (0.012, 0.012, 0.015), front=0.12, side=-1.6, back=-1.75,
                 spikes=20, spike_amp=0.08, mess=0.02, flare=0.6, seed=5)
    return rig

def tail(name, rig, m, length):
    """Hanging coat / cardigan skirt from the waist, open at the front; front panels follow the thighs."""
    hip = rig.data.bones["upperleg01.L"].head_local.z
    hw = abs(rig.data.bones["upperleg01.L"].head_local.x)
    bm = bmesh.new(); n = 30; rows = []
    zs = [hip + 0.08, hip - 0.05, hip - length * hip * 0.5, hip - length * hip]
    for j, z in enumerate(zs):
        r = hw + (0.075 + 0.02 * j if length > 0.3 else 0.058 + 0.008 * j)    # short blazer hem stays close
        ring = []
        for k in range(n + 1):
            a = -math.pi / 2 + 0.55 + k / n * (2 * math.pi - 1.1)       # leaves a gap round -Y (front)
            ring.append(bm.verts.new((math.cos(a) * r, math.sin(a) * r * 0.85, z)))
        rows.append(ring)
    for j in range(len(rows) - 1):
        for k in range(n):
            bm.faces.new((rows[j][k], rows[j][k + 1], rows[j + 1][k + 1], rows[j + 1][k]))
    me = bpy.data.meshes.new(name + "_coattail"); bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = True
    me.materials.append(m)
    ob = bpy.data.objects.new(name + "_coattail", me); bpy.context.scene.collection.objects.link(ob)
    ob.modifiers.new("thick", "SOLIDIFY").thickness = 0.006
    sp = ob.vertex_groups.new(name="spine05")
    gl = ob.vertex_groups.new(name="upperleg01.L"); gr = ob.vertex_groups.new(name="upperleg01.R")
    for v in me.vertices:
        drop = max(0.0, min(1.0, (hip + 0.02 - v.co.z) / 0.1))          # waist band stays with the spine
        front = max(0.0, -v.co.y / (hw + 0.1))
        w = drop * (0.5 + 0.5 * front)
        (gl if v.co.x > 0 else gr).add([v.index], w, "REPLACE")
        sp.add([v.index], 1.0 - w, "REPLACE")
    ob.modifiers.new("rig", "ARMATURE").object = rig
    ob.parent = rig
    return ob

def _bone_world(rig, bone, at="head"):
    bpy.context.view_layer.update()
    pb = rig.pose.bones[bone]
    return rig.matrix_world @ (pb.head if at == "head" else pb.tail)

def skirt(name, rig, color=(0.30, 0.17, 0.09), length=None):
    """A-line skirt from the waist to mid-calf, bone-parented to the pelvis."""
    hip = rig.data.bones["upperleg01.L"].head_local.z
    hw = abs(rig.data.bones["upperleg01.L"].head_local.x)
    bm = bmesh.new()
    low = length if length is not None else hip * 0.42
    rows = [(hip + 0.06, hw + 0.06), (hip - 0.02, hw + 0.085), (hip * 0.75, hw + 0.10), ((hip * 0.75 + low) / 2, hw + 0.115), (low, hw + 0.12)]
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

LR_ = (("L", -1), ("R", 1))
WAKE_POSES = {
    #          tilt  hip height  hip fwd   bones
    "lie":    (1.50, 0.07, 0.00, {"upperleg01": (-0.05, 0, 0), "lowerleg01": (0.05, 0, 0), "upperarm01": (-0.1, 0, 1.15),
                                  "lowerarm01": (0.1, 0, 0), "neck01": (0.0, 0, 0.35)}),
    "sit":    (0.00, 0.07, 0.00, {"upperleg01": (-1.45, 0, 0), "lowerleg01": (0.45, 0, 0), "upperarm01": (-0.45, 0, 0.75),
                                  "lowerarm01": (0.2, 0, 0), "spine05": (0.30, 0, 0), "neck01": (0.25, 0, 0)}),
    "crouch": (0.00, 0.30, 0.30, {"upperleg01": (-1.80, 0, 0), "lowerleg01": (2.25, 0, 0), "upperarm01": (-0.6, 0, 0.7),
                                  "lowerarm01": (0.3, 0, 0), "spine05": (0.70, 0, 0), "spine03": (0.2, 0, 0), "neck01": (-0.2, 0, 0)}),
    "stand":  (0.00, None, 0.42, {"upperarm01": (0.0, 0, 0.8), "lowerarm01": (0.2, 0, 0), "neck01": (0.1, 0, 0)}),
    # seated wake-up (render_fast opening): asleep sitting with the back against the trunk, then bending forward at the
    # waist while staying seated.  thigh = -1.45 + tilt keeps the legs flat on the grass.
    "doze":   (0.30, 0.07, -0.55, {"upperleg01": (-1.15, 0, 0.10), "lowerleg01": (0.30, 0, 0), "upperarm01": (-0.25, 0, 0.85),
                                   "lowerarm01": (0.55, 0, 0), "spine05": (-0.12, 0, 0), "neck01": (0.55, 0, 0.30)}),
    "wake":   (-0.05, 0.07, -0.55, {"upperleg01": (-1.50, 0, 0.10), "lowerleg01": (0.35, 0, 0), "upperarm01": (-0.60, 0, 0.70),
                                   "lowerarm01": (0.45, 0, 0), "spine05": (0.45, 0, 0), "spine03": (0.25, 0, 0), "neck01": (0.05, 0, 0.05)}),
}
ALL_BONES = ("upperleg01", "lowerleg01", "upperarm01", "lowerarm01", "spine05", "spine03", "neck01")

def _key_pose(rig, pose, frame, hip_ground, facing, fwd):
    tilt, hz, hf, bones = WAKE_POSES[pose]
    for b in ALL_BONES:
        rx, ry, rz = bones.get(b, (0, 0, 0))
        sides = LR_ if b in ("upperleg01", "lowerleg01", "upperarm01", "lowerarm01") else ((None, 1),)
        for side, sg in sides:
            pb = rig.pose.bones.get(f"{b}.{side}" if side else b)
            if not pb:
                continue
            pb.rotation_mode = "XYZ"; pb.rotation_euler = (rx, ry, rz * sg)
            pb.keyframe_insert("rotation_euler", frame=frame)
    s = rig.scale.x
    hl = Vector((0, rig.data.bones["upperleg01.L"].head_local.y, rig.data.bones["upperleg01.L"].head_local.z)) * s
    if hz is None:
        hz = hl.z
    rig.rotation_euler = (-tilt, 0.0, facing)
    R = rig.rotation_euler.to_matrix()
    rig.location = hip_ground + fwd * hf + Vector((0, 0, hz)) - R @ hl
    rig.keyframe_insert("location", frame=frame); rig.keyframe_insert("rotation_euler", frame=frame)

def animate_wakeup(rig, hip_ground, facing, start=1, timing=(0, 30, 60, 80, 100, 120)):
    """Eren lies asleep on his back, sits up, then gets to his feet. hip_ground: point on the ground under his hips."""
    rot = Matrix.Rotation(facing, 3, "Z"); fwd = rot @ Vector((0, -1, 0))
    f = [start + t for t in timing]
    for frame, pose in zip(f, ("lie", "lie", "sit", "sit", "crouch", "stand")):
        _key_pose(rig, pose, frame, Vector(hip_ground), facing, fwd)
    return f[-1]

def animate_wake_seated(rig, hip_ground, facing, start=1, timing=(0, 18, 60)):
    """Eren asleep sitting against the trunk; from start+timing[1] he slowly bends forward at the waist (stays seated)."""
    rot = Matrix.Rotation(facing, 3, "Z"); fwd = rot @ Vector((0, -1, 0))
    f = [start + t for t in timing]
    for frame, pose in zip(f, ("doze", "doze", "wake")):
        _key_pose(rig, pose, frame, Vector(hip_ground), facing, fwd)
    return f[-1]

def animate_walk(rig, p0, p1, f0, f1, step=8, swing=0.32):
    """Slow walk from p0 to p1 (world points, z already on the ground) over frames f0..f1: eased location keys, facing
    the walking direction, alternating thigh swing with a bent trailing knee, settling to a stand at f1."""
    p0, p1 = Vector(p0), Vector(p1); d = p1 - p0
    rig.rotation_euler = (0.0, 0.0, math.atan2(d.x, -d.y))
    rig.keyframe_insert("rotation_euler", frame=f0)
    rig.location = p0; rig.keyframe_insert("location", frame=f0)
    rig.location = p1; rig.keyframe_insert("location", frame=f1)
    n = max(1, int((f1 - f0) / step))
    for i in range(n + 1):
        fr = f0 + i * step
        amp = swing * (0.0 if i == n else (1.0 if 0 < i < n - 1 else 0.6))
        for s, sg in LR_:
            ph = sg * (1 if i % 2 else -1)
            for bone, val in ((f"upperleg01.{s}", (-amp * ph, 0, 0)), (f"lowerleg01.{s}", (amp * 0.9 * max(0, -ph), 0, 0))):
                pb = rig.pose.bones.get(bone)
                if pb:
                    pb.rotation_mode = "XYZ"; pb.rotation_euler = val; pb.keyframe_insert("rotation_euler", frame=fr)
    return f1

def place_opening(base, trunk_r=1.6, facing=0.0, trunk=None, start=1, mode="stand"):
    """Eren asleep on his back under the tree (head toward the trunk) who sits up and stands, Mikasa standing nearby
    with her firewood frame on her back, Eren's frame on the grass. base: trunk centre on the ground;
    facing: direction Eren faces once up (radians about Z, 0 = -Y); trunk: trunk object for ray casting the bark.
    mode="seated": Eren sleeps sitting against the trunk and only bends forward (animate_wake_seated); the caller
    animates Mikasa's approach with animate_walk."""
    base = Vector(base)
    rot = Matrix.Rotation(facing, 4, "Z")
    fwd = (rot @ Vector((0, -1, 0, 0))).to_3d(); side = (rot @ Vector((1, 0, 0, 0))).to_3d()
    trunk_r = max(_surface(trunk, base, fwd, z, trunk_r) for z in (0.3, 0.6, 0.9))
    eren = make_eren()
    if mode == "seated":
        end = animate_wake_seated(eren, base + fwd * (trunk_r + 0.95), facing, start=start)
    else:
        end = animate_wakeup(eren, base + fwd * (trunk_r + 0.95), facing, start=start)
    mik = make_mikasa(); pose_standing(mik, look_down=0.2)
    mik.location = base + fwd * (trunk_r + 2.3) + side * 1.1; mik.rotation_euler = (0.0, 0.0, facing + math.pi * 1.25)
    f2 = firewood_frame("Firewood_Mikasa", seed=2)                          # on her back
    f2.parent = mik; f2.location = (0, 0.17 / mik.scale.x, 0.42 / mik.scale.x); f2.scale = [1 / mik.scale.x] * 3
    f1 = firewood_frame("Firewood_Eren", seed=1)
    f1.location = base + fwd * (trunk_r + 0.5) - side * 1.8 + Vector((0, 0, 0.03)); f1.rotation_euler = (1.5, 0, facing + 1.2)
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
