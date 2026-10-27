"""PART 3 SET (AOT_SET=stohess.sset): world.py's walls / fields plus Stohess in the Wall Sina EAST district (frame S, see
layout.py and research/stohess/STOHESS_SCENE_BIBLE.md B): pale stone blocks with slate roofs (instanced), paving, the canal
with arched bridges, the domed church + bell tower, the square + statue, the MP headquarters, the underground stairway,
rooftop launcher racks (Plan C), and the WALL TITAN face patch in the bulge's inner wall face (hidden until s2 shows it).
"""
import math, os, random, sys
import numpy as np
import bpy, bmesh
from mathutils import Vector, Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from forest import common as C
from stohess.layout import *
from stohess import layout as SL

STATE = {}
CAMS = {"s_overview": ((12300.0, 23300.0, 500.0), (12700.0, 24000.0, 0.0), 28.0)}

def GS(x, y):
    w = S(x, y)
    return C.G(w[0], w[1])

def _cube(bm, c, s, rz=0.0):
    res = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=s, verts=res["verts"])
    if rz:
        bmesh.ops.rotate(bm, verts=res["verts"], cent=(0, 0, 0), matrix=Matrix.Rotation(rz, 3, "Z"))
    bmesh.ops.translate(bm, vec=c, verts=res["verts"])
    return res

def stone_mats(M):
    M2 = dict(M)
    for k, col in (("plaster", (0.78, 0.74, 0.66)), ("plaster_w", (0.86, 0.83, 0.76)), ("plaster_o", (0.74, 0.66, 0.54)),
                   ("timber", (0.70, 0.68, 0.64))):
        M2[k] = C.mat("ST_" + k, col, 0.85)
    for k, col in (("roof_red", (0.20, 0.22, 0.26)), ("roof_brown", (0.30, 0.17, 0.12)), ("roof_dark", (0.16, 0.17, 0.20)),
                   ("roof_orange", (0.24, 0.27, 0.31))):
        M2[k] = C.mat("ST_" + k, col, 0.6)
    return M2

def build_town(M, c):
    from forest import fset
    M2 = stone_mats(M)
    v = fset.house_variants(M2, c, 14, seed=31)
    for k, (ob, w, d) in enumerate(v):
        if k % 3 == 0:
            ob.scale = (1.0, 1.0, 1.55)                     # 4-5 storey blocks
    rnd = random.Random(1850)
    pts = []
    x = -345.0
    while x < 715.0:
        y = -405.0
        while y < 405.0:
            px, py = x + rnd.uniform(-1.5, 1.5), y + rnd.uniform(-1.5, 1.5)
            if in_town(px, py) and not street(px, py) and path_dist(px, py) > PATH_CLEAR:
                w = S(px, py); pts.append((w[0], w[1], 0.0 if abs((py + 420) % 64 - 32) > 16 else math.pi / 2))
            y += 15.0
        x += 13.0
    fset.place_town("ST_Town", v, pts, c)
    STATE["variants"] = v
    print(f"[stohess] {len(pts)} houses", flush=True)

def build_ground(c):
    pave = C.mat("ST_Pave", (0.46, 0.44, 0.40), 0.9)
    bm = bmesh.new(); cell = 20.0
    V = {}
    xs = np.arange(-360.0, 740.0 + 1, cell); ys = np.arange(-420.0, 420.0 + 1, cell)
    def vert(i, j):
        if (i, j) not in V:
            w = S(xs[i], ys[j]); V[(i, j)] = bm.verts.new((w[0], w[1], C.G(w[0], w[1]) + 0.18))
        return V[(i, j)]
    for i in range(len(xs) - 1):
        for j in range(len(ys) - 1):
            cx, cy = (xs[i] + xs[i + 1]) / 2, (ys[j] + ys[j + 1]) / 2
            if cx > BULGE_C[0] and math.hypot(cx - BULGE_C[0], cy) > BULGE_R - 4:
                continue
            bm.faces.new((vert(i, j), vert(i + 1, j), vert(i + 1, j + 1), vert(i, j + 1)))
    C.mesh_obj("ST_Paving", bm, [pave], c)
    # canal + bridges
    water = C.mat("ST_Canal", (0.07, 0.14, 0.17), 0.08); quay = C.mat("ST_Quay", (0.56, 0.53, 0.47), 0.85)
    bm = bmesh.new()
    y0, y1 = -405.0, 405.0
    w0, w1 = S(CANAL_X - 9, y0), S(CANAL_X + 9, y1)
    z = GS(CANAL_X, 0.0) - 1.2
    vs = [bm.verts.new((w0[0], w0[1], z)), bm.verts.new((w1[0], w0[1], z)), bm.verts.new((w1[0], w1[1], z)), bm.verts.new((w0[0], w1[1], z))]
    bm.faces.new(vs)
    C.mesh_obj("ST_CanalWater", bm, [water], c)
    bm = bmesh.new()
    for sx in (-1, 1):
        w = S(CANAL_X + sx * 9.6, 0.0); _cube(bm, (w[0], w[1], GS(CANAL_X, 0) - 0.5), (1.2, y1 - y0, 1.6))
    for by in (-200.0, 0.0, 200.0):
        w = S(CANAL_X, by); zb = GS(CANAL_X, by)
        _cube(bm, (w[0], w[1], zb + 1.6), (22.0, 14.0 if by == 0 else 9.0, 1.2))
        for px in (-4.0, 4.0):
            _cube(bm, (w[0] + px, w[1], zb - 0.2), (2.0, 8.0, 3.6))
    C.mesh_obj("ST_Quays", bm, [quay], c)

def build_landmarks(c):
    stone = C.mat("ST_Stone", (0.80, 0.77, 0.70), 0.8); dome = C.mat("ST_Dome", (0.42, 0.52, 0.48), 0.5)
    slate = C.mat("ST_Slate", (0.20, 0.22, 0.26), 0.6); dark = C.mat("ST_Dark", (0.03, 0.03, 0.03), 0.9)
    bronze = C.mat("ST_Bronze", (0.25, 0.30, 0.24), 0.4)
    # church: nave + dome + lantern, bell tower (all one object: the brawl crashes through it -> seg hides / swaps it)
    cx, cy = CHURCH; w = S(cx, cy); z = GS(cx, cy)
    bm = bmesh.new()
    _cube(bm, (w[0], w[1], z + 11), (34.0, 46.0, 22.0))
    res = bmesh.ops.create_uvsphere(bm, u_segments=20, v_segments=10, radius=14.0)
    for v in res["verts"]:
        v.co.z = max(v.co.z, 0.0)
        v.co += Vector((w[0], w[1], z + 22 + 4))
    res = bmesh.ops.create_cone(bm, cap_ends=True, segments=16, radius1=14.5, radius2=14.5, depth=6.0)
    bmesh.ops.translate(bm, vec=(w[0], w[1], z + 25), verts=res["verts"])
    church = C.mesh_obj("ST_Church", bm, [stone], c)
    bm = bmesh.new()
    res = bmesh.ops.create_uvsphere(bm, u_segments=20, v_segments=10, radius=14.0)
    for v in res["verts"]:
        v.co.z = max(v.co.z * 1.15, 0.0); v.co += Vector((w[0], w[1], z + 28))
    C.mesh_obj("ST_ChurchDome", bm, [dome], c)
    bm = bmesh.new()
    _cube(bm, (w[0] + 22, w[1] - 20, z + 26), (9.0, 9.0, 52.0))
    res = bmesh.ops.create_cone(bm, cap_ends=True, segments=4, radius1=7.0, radius2=0.3, depth=12.0)
    bmesh.ops.rotate(bm, verts=res["verts"], cent=(0, 0, 0), matrix=Matrix.Rotation(math.pi / 4, 3, "Z"))
    bmesh.ops.translate(bm, vec=(w[0] + 22, w[1] - 20, z + 58), verts=res["verts"])
    C.mesh_obj("ST_BellTower", bm, [stone], c)
    # square + statue
    sx, sy = SQUARE; w = S(sx, sy); z = GS(sx, sy)
    bm = bmesh.new(); _cube(bm, (w[0], w[1], z + 2.0), (6.0, 6.0, 4.0))
    C.mesh_obj("ST_Plinth", bm, [stone], c)
    bm = bmesh.new(); _cube(bm, (w[0], w[1], z + 6.5), (1.6, 1.6, 5.0)); _cube(bm, (w[0], w[1] + 0.4, z + 9.6), (1.0, 1.0, 1.2))
    C.mesh_obj("ST_Statue", bm, [bronze], c)
    # MP headquarters
    mx, my = MPHQ; w = S(mx, my); z = GS(mx, my)
    bm = bmesh.new(); _cube(bm, (w[0], w[1], z + 13), (60.0, 40.0, 26.0))
    C.mesh_obj("ST_MPHQ", bm, [stone], c)
    bm = bmesh.new(); _cube(bm, (w[0], w[1], z + 27.5), (62.0, 42.0, 3.0))
    C.mesh_obj("ST_MPHQRoof", bm, [slate], c)
    # underground stairway: a dark recess with a stone parapet
    tx, ty = STAIRS; w = S(tx, ty); z = GS(tx, ty)
    bm = bmesh.new(); _cube(bm, (w[0], w[1], z + 0.25), (6.0, 14.0, 0.2))
    C.mesh_obj("ST_StairsDark", bm, [dark], c)
    bm = bmesh.new()
    for px in (-3.6, 3.6):
        _cube(bm, (w[0] + px, w[1], z + 0.6), (0.8, 15.0, 1.2))
    C.mesh_obj("ST_StairsWall", bm, [stone], c)
    # rooftop launcher racks (Plan C) round the stairway square
    wood = C.mat("F_RackWood", (0.32, 0.22, 0.12), 0.8)
    bm = bmesh.new(); racks = []
    for k in range(10):
        a = k * math.tau / 10 + 0.2; r = 40.0
        px, py = -95.0 + r * math.cos(a), 30.0 + r * math.sin(a)
        w = S(px, py); z = GS(px, py) + 16.0
        _cube(bm, (w[0], w[1], z), (3.0, 2.2, 1.6), rz=a)
        racks.append((w[0], w[1], z + 1.0))
    C.mesh_obj("ST_Racks", bm, [wood], c)
    STATE["racks"] = racks

def build_wall_face(c):
    """The titan inside the wall: an irregular dark hole in the inner face at the climb line, z FACE_Z, and the face
    (skin ellipsoid, brow, nose, one open eye) set 0.6 m proud of the hole floor.  Hidden until seg_s2 shows it."""
    (fx, fy), (nx, ny) = CLIMB, CLIMB_N
    w = S(fx + 0.4 * nx, fy + 0.4 * ny)
    ang = math.atan2(ny, nx)
    R = Matrix.Rotation(ang - math.pi / 2, 4, "Z")            # local +y -> the inward normal (out of the wall)
    skin = C.mat("ST_WallTitanSkin", (0.62, 0.40, 0.30), 0.6)
    dark = C.mat("ST_HoleDark", (0.05, 0.04, 0.035), 0.95)
    white = C.mat("ST_EyeWhite", (0.86, 0.84, 0.80), 0.4)
    iris = C.mat("ST_EyeIris", (0.06, 0.05, 0.04), 0.3)
    rubble = C.mat("ST_WallRubble", (0.60, 0.57, 0.50), 0.9)
    bm = bmesh.new()
    rnd = random.Random(25)
    n = 18; rim = []
    for k in range(n):                                        # hole: an irregular dark patch ON the wall face (the world
        a = k * math.tau / n                                  # wall cannot be cut), its edge broken up by stone chunks
        r = 9.0 + rnd.uniform(-1.8, 1.8)
        rim.append(bm.verts.new((r * math.cos(a), 0.05, r * math.sin(a))))
        _cube(bm, (r * math.cos(a), 0.4, r * math.sin(a)), (rnd.uniform(1.5, 3.0), 0.9, rnd.uniform(1.2, 2.4)), rz=0.0)
    ctr = bm.verts.new((0, 0.05, 0))
    for k in range(n):
        f = bm.faces.new((ctr, rim[k], rim[(k + 1) % n])); f.material_index = 1
    res = bmesh.ops.create_uvsphere(bm, u_segments=20, v_segments=12, radius=1.0)    # the face: ellipsoid 7 x 1.6 x 8.5
    for v in res["verts"]:
        v.co = Vector((v.co.x * 6.0, max(v.co.y, -0.2) * 1.6 + 0.2, v.co.z * 7.6 - 0.8))
    for f in {f for v in res["verts"] for f in v.link_faces}:
        f.material_index = 0; f.smooth = True
    _cube(bm, (0, 1.75, 1.8), (8.0, 0.9, 1.2))                # brow ridge
    _cube(bm, (0, 2.0, -0.8), (1.6, 1.4, 3.6))                # nose
    for ex in (-2.4, 2.4):
        res = bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=8, radius=1.25)
        bmesh.ops.translate(bm, vec=(ex, 1.55, 0.6), verts=res["verts"])
        for f in {f for v in res["verts"] for f in v.link_faces}:
            f.material_index = 2
        res = bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=6, radius=0.55)
        bmesh.ops.translate(bm, vec=(ex + 0.15, 2.65, 0.55), verts=res["verts"])
        for f in {f for v in res["verts"] for f in v.link_faces}:
            f.material_index = 3
    for k in range(10):                                       # broken stone ledge under the hole
        _cube(bm, (rnd.uniform(-8, 8), rnd.uniform(0.3, 1.2), -9.5 + rnd.uniform(-1, 1)), (rnd.uniform(1, 2.5), 1.2, rnd.uniform(0.8, 1.6)))
    for f in bm.faces:
        cm_ = f.calc_center_median()
        if f.material_index == 0 and (cm_.z < -9 or math.hypot(cm_.x, cm_.z) > 6.5):
            f.material_index = 4
    face = C.mesh_obj("ST_WallTitan", bm, [skin, dark, white, iris, rubble], c)
    face.matrix_world = Matrix.Translation((w[0], w[1], GS(fx, fy) + FACE_Z)) @ R
    objs = [face]
    try:                                                      # a real MPFB pure-titan face replaces the placeholder ellipsoid
        objs = [_hole_only(face)] + _pure_face(c, (w[0], w[1], GS(fx, fy) + FACE_Z), (nx, ny))
    except Exception as ex:
        import traceback; traceback.print_exc()
        print("[stohess] MPFB wall face failed, keeping the placeholder:", ex, flush=True)
    STATE["face"] = objs
    for o in objs:
        o.hide_render = True; o.hide_viewport = True

def _hole_only(face):
    """keep only the dark hole + rubble of the placeholder (drop its ellipsoid / eyes / nose / brow)."""
    me = face.data
    bm = bmesh.new(); bm.from_mesh(me)
    kill = [f for f in bm.faces if f.material_index in (0, 2, 3) and f.calc_center_median().z > -9]
    bmesh.ops.delete(bm, geom=kill, context="FACES"); bm.to_mesh(me); bm.free()
    return face

HOLE_R = 8.4
def _pure_face(c, centre, n):
    """70 m pure titan (pure_titans.make_pure, rest pose) standing INSIDE the wall facing out of it; everything but the
    part of the face inside the hole (centred on its left eye) is deleted, the face sits 0.3 m proud of the hole."""
    import pure_titans as PT
    rig = PT.make_pure("generic", seed=2, height=70.0, lod=1.0, outline=False, name="ST_WallTitanPure")
    for pb in rig.pose.bones:
        pb.matrix_basis = Matrix.Identity(4)
    nv = Vector((n[0], n[1], 0.0)); ang = math.atan2(n[1], n[0])
    rig.location = (0, 0, 0); rig.rotation_euler = (0, 0, ang + math.pi / 2)       # MPFB front -Y -> the inward normal
    bpy.context.view_layer.update()
    meshes = [o for o in rig.children_recursive if o.type == "MESH"]
    body = max(meshes, key=lambda o: len(o.data.vertices))
    def head_pts():
        bpy.context.view_layer.update()
        nz = (rig.matrix_world @ rig.data.bones["head"].head_local).z
        P = [body.matrix_world @ v.co for v in body.data.vertices]
        return nz, [p for p in P if p.z > nz]
    neck_z, head = head_pts()
    k = 12.0 / max(1e-3, max(p.z for p in head) - min(p.z for p in head))     # a 12 m head (fills the 18 m hole)
    rig.scale = tuple(v * k for v in rig.scale)
    neck_z, head = head_pts()
    hz0, hz1 = min(p.z for p in head), max(p.z for p in head)
    side = Vector((-nv.y, nv.x, 0.0))
    hs = [p.dot(side) for p in head]; hc = (min(hs) + max(hs)) / 2
    front = max(p.dot(nv) for p in head)
    cv = Vector(centre)
    mid = side * hc + Vector((0, 0, hz0 + 0.55 * (hz1 - hz0)))            # between the eyes
    shell = 4.0
    # face shell [front - shell, front] -> [patch + 0.1, patch + 0.1 + shell]
    off = Vector((cv.x, cv.y, 0)) - side * mid.dot(side) - nv * (front - shell - 0.15) + Vector((0, 0, cv.z - mid.z))
    rig.location = off
    bpy.context.view_layer.update()
    keep = []
    for o in meshes:
        me = o.data
        bm = bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table()
        mw = o.matrix_world
        kill = []
        for v in bm.verts:
            p = mw @ v.co
            d = p - cv
            if math.hypot(d.dot(side), d.z) > HOLE_R or d.dot(nv) < 0.12 or p.z < neck_z + off.z - 0.5:
                kill.append(v)
        bmesh.ops.delete(bm, geom=kill, context="VERTS"); bm.to_mesh(me); bm.free()
        if len(me.vertices):
            keep.append(o)
        o.hide_render = True
    print(f"[stohess] wall titan face: {sum(len(o.data.vertices) for o in keep)} verts kept in {len(keep)} objects", flush=True)
    return keep

def prune_veg():
    n = 0
    for ob in list(bpy.data.objects):
        if ob.type != "MESH" or not any(m.type == "NODES" and m.name == "Scatter" for m in ob.modifiers) or ob.name.startswith(("F_", "ST_")):
            continue
        me = ob.data
        co = np.zeros(len(me.vertices) * 3); me.vertices.foreach_get("co", co); co = co.reshape(-1, 3)
        kill = [i for i, p in enumerate(co) if -420 < p[0] - SO[0] < 760 and abs(p[1] - SO[1]) < 440]
        if kill:
            bm = bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table()
            bmesh.ops.delete(bm, geom=[bm.verts[i] for i in kill], context="VERTS"); bm.to_mesh(me); bm.free()
            n += len(kill)
    print(f"[stohess] pruned {n} vegetation points", flush=True)

def build_set(M, year=850):
    import time
    t0 = time.time()
    sc = bpy.context.scene
    C.make_sky(sc)
    W = C.world_mod()
    W.build(M, year, {"terrain": None})
    sys.modules["aotlib"].height = lambda x, y: C.G(x, y)
    c = C.coll("StohessSet")
    for name, fn in (("ground", lambda: build_ground(c)), ("landmarks", lambda: build_landmarks(c)),
                     ("town", lambda: build_town(M, c)), ("wallface", lambda: build_wall_face(c)), ("prune", prune_veg)):
        t = time.time()
        try:
            fn()
        except Exception as ex:
            import traceback; traceback.print_exc()
            print(f"[stohess] {name} FAILED: {ex!r}", flush=True)
        print(f"[stohess] {name} {time.time() - t:.1f}s", flush=True)
    print(f"[stohess] set built in {time.time() - t0:.1f}s", flush=True)
    return M
