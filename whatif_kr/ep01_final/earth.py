# EP01 space scenes: giant on the Earth (units = km). Imported by shot.py (exec of refstyle top part first).
import bpy, math, random, bmesh
from mathutils import Vector, Matrix, Quaternion

R_E = 6371.0
KOREA = (37.0, 127.5)   # lat, lon

def ll2v(lat, lon):
    la, lo = math.radians(lat), math.radians(lon)
    # Blender sphere projection (object coords): u = 0.5 + atan2(y, -x)/2pi  -> lon 0 at -X... solved empirically below
    return Vector((math.cos(la) * math.sin(lo), math.cos(la) * math.cos(lo), math.sin(la)))

def earth_mats():
    m = bpy.data.materials.new("earth"); nt = m.node_tree if m.use_nodes else None
    m.use_nodes = True; nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    tex = nt.nodes.new("ShaderNodeTexImage"); tex.image = bpy.data.images.load(f"{A}/earth/earth_5400.jpg"); tex.projection = "SPHERE"
    mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (-1, 1, 1)
    nt.links.new(tc.outputs["Object"], mp.inputs[0]); nt.links.new(mp.outputs[0], tex.inputs[0]); nt.links.new(tex.outputs[0], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.85
    # interior (shatter caps): molten core
    core = mat("core", "#ff7a1a", 0.6, emit=6.0)
    cl = bpy.data.materials.new("clouds"); cl.use_nodes = True; nt2 = cl.node_tree; b2 = nt2.nodes["Principled BSDF"]
    tc2 = nt2.nodes.new("ShaderNodeTexCoord"); t2 = nt2.nodes.new("ShaderNodeTexImage")
    t2.image = bpy.data.images.load(f"{A}/earth/clouds_2048.jpg"); t2.projection = "SPHERE"
    mp2 = nt2.nodes.new("ShaderNodeMapping"); mp2.inputs["Scale"].default_value = (-1, 1, 1)
    nt2.links.new(tc2.outputs["Object"], mp2.inputs[0]); nt2.links.new(mp2.outputs[0], t2.inputs[0]); nt2.links.new(t2.outputs[0], b2.inputs["Alpha"])
    b2.inputs["Base Color"].default_value = (1, 1, 1, 1); b2.inputs["Roughness"].default_value = 1
    # atmosphere rim: thin blue fresnel shell
    at = bpy.data.materials.new("atmo"); at.use_nodes = True; n3 = at.node_tree; n3.nodes.remove(n3.nodes["Principled BSDF"])
    lw = n3.nodes.new("ShaderNodeLayerWeight"); lw.inputs[0].default_value = 0.5
    pw = n3.nodes.new("ShaderNodeMath"); pw.operation = "POWER"; pw.inputs[1].default_value = 3.0
    em = n3.nodes.new("ShaderNodeEmission"); em.inputs[0].default_value = (*srgb("#6fb4ff"), 1); em.inputs[1].default_value = 1.6
    tr = n3.nodes.new("ShaderNodeBsdfTransparent"); mx = n3.nodes.new("ShaderNodeMixShader")
    nt3 = n3; nt3.links.new(lw.outputs["Facing"], pw.inputs[0]); nt3.links.new(pw.outputs[0], mx.inputs[0]); nt3.links.new(tr.outputs[0], mx.inputs[1]); nt3.links.new(em.outputs[0], mx.inputs[2])
    nt3.links.new(mx.outputs[0], n3.nodes["Material Output"].inputs[0])
    return m, core, cl, at

def uvsphere(name, r, m, seg=160):
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=seg // 2, radius=r); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    me.materials.append(m); o = bpy.data.objects.new(name, me); S.collection.objects.link(o); return o

def space_world(sun_dir=Vector((-0.6, -0.5, 0.45))):
    w = bpy.data.worlds.new("space"); S.world = w; w.use_nodes = True; nt = w.node_tree
    bg = nt.nodes["Background"]; bg.inputs[1].default_value = 1.0
    # stars: sparse voronoi points on black
    tc = nt.nodes.new("ShaderNodeTexCoord"); vo = nt.nodes.new("ShaderNodeTexVoronoi"); vo.feature = "DISTANCE_TO_EDGE" if False else "F1"
    vo.inputs["Scale"].default_value = 260
    rp = nt.nodes.new("ShaderNodeValToRGB"); rp.color_ramp.elements[0].position = 0.0; rp.color_ramp.elements[0].color = (1, 1, 1, 1)
    rp.color_ramp.elements[1].position = 0.035; rp.color_ramp.elements[1].color = (0, 0, 0, 1)
    nt.links.new(tc.outputs["Generated"], vo.inputs["Vector"]); nt.links.new(vo.outputs["Distance"], rp.inputs[0])
    wn = nt.nodes.new("ShaderNodeTexWhiteNoise"); nt.links.new(tc.outputs["Generated"], wn.inputs[0])
    mul = nt.nodes.new("ShaderNodeMath"); mul.operation = "MULTIPLY"
    gt = nt.nodes.new("ShaderNodeMath"); gt.operation = "GREATER_THAN"; gt.inputs[1].default_value = 0.0
    nt.links.new(vo.outputs["Color"], gt.inputs[0])
    sep = nt.nodes.new("ShaderNodeSeparateColor"); nt.links.new(vo.outputs["Color"], sep.inputs[0])
    th = nt.nodes.new("ShaderNodeMath"); th.operation = "GREATER_THAN"; th.inputs[1].default_value = 0.55; nt.links.new(sep.outputs[0], th.inputs[0])
    nt.links.new(rp.outputs[0], mul.inputs[0]); nt.links.new(th.outputs[0], mul.inputs[1])
    s2 = nt.nodes.new("ShaderNodeMath"); s2.operation = "MULTIPLY"; s2.inputs[1].default_value = 1.2; nt.links.new(mul.outputs[0], s2.inputs[0])
    nt.links.new(s2.outputs[0], bg.inputs[0])
    sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN")); S.collection.objects.link(sun)
    sun.data.energy = 5.0; sun.data.color = srgb("#fff4e6"); sun.data.angle = math.radians(0.5)
    sun.rotation_euler = (-sun_dir.normalized()).to_track_quat("-Z", "Y").to_euler()
    S.view_settings.view_transform = "AgX"
    try: S.view_settings.look = "AgX - Medium High Contrast"
    except Exception: pass
    S.render.engine = "CYCLES"; S.cycles.samples = int(os.environ.get("SPP", "32")); S.cycles.use_denoising = True; S.cycles.max_bounces = 4
    S.render.resolution_x = 1920; S.render.resolution_y = 1080; S.render.resolution_percentage = pct; S.render.filepath = out
    return sun

def build_earth(clouds=True):
    m, core, cl, at = earth_mats()
    e = uvsphere("earth", R_E, m, 384)
    # rotate so Korea points to +Z
    k = ll2v(*KOREA); q = k.rotation_difference(Vector((0, 0, 1)))
    root = bpy.data.objects.new("earth_root", None); S.collection.objects.link(root)
    root.rotation_mode = "QUATERNION"; root.rotation_quaternion = q
    e.parent = root
    objs = [e]
    if clouds:
        c = uvsphere("clouds", R_E + 12, cl, 384); c.parent = root; objs.append(c)
    a = uvsphere("atmo", R_E + 90, at, 256); a.parent = root
    return root, e, m, core, a

def voronoi_shatter(earth, core, n=36, seed=4, center=Vector((0, 0, 1))):
    """Pre-fracture the earth mesh into n Voronoi cells (bisect + fill). Cells biased toward the impact point."""
    rnd = random.Random(seed); pts = []
    while len(pts) < n:
        v = Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1)))
        if v.length > 1: continue
        if rnd.random() < 0.5: v = (v * 0.55 + center * 0.6)
        pts.append(v * R_E)
    src = earth.data; cells = []
    earth.data.materials.append(core)
    for i, p in enumerate(pts):
        bm = bmesh.new(); bm.from_mesh(src)
        for j, q in enumerate(pts):
            if i == j: continue
            mid = (p + q) / 2; nrm = (q - p).normalized()
            geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
            r = bmesh.ops.bisect_plane(bm, geom=geom, plane_co=mid, plane_no=nrm, clear_outer=True)
            if not bm.verts: break
        if not bm.verts: bm.free(); continue
        bnd = [e for e in bm.edges if e.is_boundary]
        if bnd:
            res = bmesh.ops.holes_fill(bm, edges=bnd, sides=0)
            for f in res["faces"]: f.material_index = 1
        me = bpy.data.meshes.new(f"cell{i}"); bm.to_mesh(me); bm.free()
        for mm in src.materials: me.materials.append(mm)
        o = bpy.data.objects.new(f"cell{i}", me); S.collection.objects.link(o); o.parent = earth.parent
        cells.append((o, p))
    return cells
