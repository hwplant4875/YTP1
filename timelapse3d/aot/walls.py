"""AoT-style walls: segmented stone slabs on a continuous core, arched gates, wall-top rails, cannons and barrels."""
import bpy, bmesh, math, random
from mathutils import Vector, Matrix

WALL_H = 50.0
SLAB_L = 16.0       # slab length along the wall
SLAB_T = 14.0       # slab thickness
CORE_T = 10.0

def _box(bm, center, size, rot=0.0, mi=0):
    r = bmesh.ops.create_cube(bm, size=1)
    M = Matrix.Translation(center) @ Matrix.Rotation(rot, 4, "Z") @ Matrix.Diagonal((*size, 1))
    bmesh.ops.transform(bm, matrix=M, verts=r["verts"])
    for v in r["verts"]:
        for f in v.link_faces:
            f.material_index = mi
    return r

def _walk(pts, step):
    """Yield (position, tangent angle) every `step` metres along a polyline."""
    acc = 0.0
    for k in range(len(pts) - 1):
        a, b = Vector(pts[k]), Vector(pts[k + 1])
        seg = (b - a).length
        if seg == 0:
            continue
        t = (b - a) / seg
        while acc <= seg:
            p = a + t * acc
            yield p, math.atan2(t.y, t.x)
            acc += step
        acc -= seg

def build_wall(name, pts, mat_stone, skip=(), outward=1):
    """skip: list of (x, y, radius) where no slabs are placed (gates, water gates).
    outward: +1 if the outside of the wall is to the right of the walking direction."""
    bm = bmesh.new()
    rnd = random.Random(hash(name) & 0xffff)
    def skipped(p):
        return any((p.x - x) ** 2 + (p.y - y) ** 2 < r * r for x, y, r in skip)
    for p, ang in _walk(pts, SLAB_L):
        if skipped(p):
            continue
        n = Vector((math.sin(ang), -math.cos(ang))) * outward      # unit normal toward the outside
        # core
        _box(bm, Vector((p.x, p.y, WALL_H / 2 - 3)), (SLAB_L + 0.6, CORE_T, WALL_H + 6), ang)
        # slab, pushed slightly outward, with a small random height step on top
        hz = WALL_H + rnd.choice((0.0, 0.0, 0.6))
        c = p + n * ((SLAB_T - CORE_T) / 2 + 0.4)
        _box(bm, Vector((c.x, c.y, hz / 2 - 3)), (SLAB_L - 1.1, SLAB_T, hz + 6), ang)
        # thin pilaster strip on the outer face
        c2 = p + n * (SLAB_T / 2 + (SLAB_T - CORE_T) / 2 + 0.6)
        _box(bm, Vector((c2.x, c2.y, (WALL_H - 4) / 2 - 3)), (2.2, 1.2, WALL_H - 4 + 6), ang)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    me.materials.append(mat_stone)
    ob = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(ob)
    return ob

def arch_gate(name, center, ang, width, height, mats, depth=SLAB_T + 4, block_l=None, door=True, water=False):
    """A wall block with an arched tunnel (boolean), plus a heavy wooden door or water below."""
    block_l = block_l or width + 18
    bm = bmesh.new()
    _box(bm, Vector((0, 0, WALL_H / 2 - 3)), (block_l, depth, WALL_H + 6), 0)
    # slight frame around the arch on both faces
    for s in (-1, 1):
        _box(bm, Vector((0, s * (depth / 2 + 0.4), (height + 6) / 2)), (width + 7, 0.8, height + 6), 0)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    me.materials.append(mats["stone"])
    ob = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(ob)
    # cutter: box + cylinder top = arch
    cb = bmesh.new()
    _box(cb, Vector((0, 0, (height - width / 2) / 2 - 1)), (width, depth + 6, height - width / 2 + 2), 0)
    cyl = bmesh.ops.create_cone(cb, cap_ends=True, segments=40, radius1=width / 2, radius2=width / 2, depth=depth + 6)
    bmesh.ops.rotate(cb, cent=(0, 0, 0), matrix=Matrix.Rotation(math.pi / 2, 3, "X"), verts=cyl["verts"])
    bmesh.ops.translate(cb, vec=(0, 0, height - width / 2), verts=cyl["verts"])
    cme = bpy.data.meshes.new(name + "_cut"); cb.to_mesh(cme); cb.free()
    cut = bpy.data.objects.new(name + "_cut", cme); bpy.context.scene.collection.objects.link(cut)
    mod = ob.modifiers.new("arch", "BOOLEAN"); mod.object = cut; mod.operation = "DIFFERENCE"; mod.solver = "EXACT"
    bpy.context.view_layer.objects.active = ob
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    me2 = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    ob.modifiers.clear(); ob.data = me2
    bpy.data.objects.remove(cut)
    ob.location = (center[0], center[1], 0); ob.rotation_euler.z = ang
    parts = [ob]
    if door:
        db = bmesh.new()
        _box(db, Vector((0, 0, height / 2)), (width + 0.2, 1.6, height), 0, 0)
        for k in range(1, 6):                                 # iron bands
            _box(db, Vector((0, -0.95, k * height / 6)), (width + 0.2, 0.3, 0.7), 0, 1)
        dme = bpy.data.meshes.new(name + "_door"); db.to_mesh(dme); db.free()
        dme.materials.append(mats["gate"]); dme.materials.append(mats["iron"])
        d = bpy.data.objects.new(name + "_door", dme); bpy.context.scene.collection.objects.link(d)
        d.location = ob.location; d.rotation_euler.z = ang
        parts.append(d)
    return parts

def wall_top_props(name, pts, mats, outward=1, every=4, skip=()):
    """Twin rails along the top, cannons on carriages at the outer edge, barrel clusters."""
    bm = bmesh.new()
    def skipped(p):
        return any((p.x - x) ** 2 + (p.y - y) ** 2 < r * r for x, y, r in skip)
    i = 0
    rnd = random.Random(7)
    for p, ang in _walk(pts, SLAB_L):
        i += 1
        if skipped(p):
            continue
        n = Vector((math.sin(ang), -math.cos(ang))) * outward
        z = WALL_H + 0.15
        for off in (-1.6, 1.6):                              # rails (two lines, gauge 1.4 m)
            for g in (-0.7, 0.7):
                c = p + n * (off + g)
                _box(bm, Vector((c.x, c.y, z + 0.1)), (SLAB_L, 0.12, 0.2), ang, 1)
            c = p + n * off
            for s in range(-3, 4, 2):                       # ties
                cc = c + Vector((math.cos(ang), math.sin(ang))) * s * 2.4
                _box(bm, Vector((cc.x, cc.y, z + 0.02)), (0.35, 2.0, 0.08), ang, 2)
        if i % every == 0:                                    # cannon on a carriage near the outer edge
            c = p + n * 4.6
            _box(bm, Vector((c.x, c.y, z + 0.6)), (2.0, 2.6, 1.0), ang, 2)                 # carriage
            for w in (-1.1, 1.1):
                cw = c + Vector((math.cos(ang), math.sin(ang))) * w
                _box(bm, Vector((cw.x, cw.y, z + 0.5)), (0.25, 1.2, 1.2), ang, 2)         # wheels
            barrel = bmesh.ops.create_cone(bm, cap_ends=True, segments=12, radius1=0.42, radius2=0.32, depth=3.6)
            M = Matrix.Translation(Vector((c.x, c.y, z + 1.45)) + n.to_3d() * 1.2) @ Matrix.Rotation(ang - math.pi / 2 if outward > 0 else ang + math.pi / 2, 4, "Z") @ Matrix.Rotation(math.pi / 2 - 0.08, 4, "Y")
            bmesh.ops.transform(bm, matrix=M @ Matrix.Rotation(0, 4, "X"), verts=barrel["verts"])
            for v in barrel["verts"]:
                for f in v.link_faces:
                    f.material_index = 1
        if i % 9 == 4:                                        # barrels / powder kegs
            for k in range(rnd.randint(3, 6)):
                c = p - n * 3.5 + Vector((math.cos(ang), math.sin(ang))) * (k - 2) * 1.0 + Vector((rnd.uniform(-.3, .3), rnd.uniform(-.3, .3)))
                kb = bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=0.45, radius2=0.45, depth=1.1)
                bmesh.ops.translate(bm, vec=(c.x, c.y, z + 0.55), verts=kb["verts"])
                for v in kb["verts"]:
                    for f in v.link_faces:
                        f.material_index = 3
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for m in (mats["iron"], mats["iron"], mats["gate"], mats["keg"]):
        me.materials.append(m)
    ob = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(ob)
    return ob
