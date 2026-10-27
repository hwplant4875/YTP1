"""PART 2 SET (AOT_SET=forest.fset): world.py's three walls + fields, plus Karanes (Rose EAST district), the ruined old town
outside its gate, the windmill village, and the Forest of Giant Trees (frame F, FOREST_SCENE_BIBLE.md B).  Low-poly, instanced.

  scene.py calls build_set(M, year) instead of building Shiganshina; this module runs world.build itself (frame "shig" =
  world coordinates, so every coordinate here is W unless it says F).  Exposes ROAD_F, TRAP_F, SWAMP_F, RESCUE_F, ...
"""
import math, os, random, sys
import numpy as np
import bpy, bmesh
from mathutils import Vector, Matrix, noise

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from forest import common as C

from forest.layout import *          # ROAD_F, TRAP_F, SWAMP_F, ... (frame F)
from forest import layout as LY
STATE = {}
CAMS = {"f_overview": ((19300.0, 23400.0, 420.0), (19870.0, 24000.0, 0.0), 28.0)}   # scene.py --cam (render_seg drives the camera)

def road_dist_F(x, y, pts=None):
    return LY.road_dist_F(x, y, pts or STATE.get("road_dense"))

def in_forest_F(x, y):
    if not (FOREST_X[0] <= x <= FOREST_X[1] and FOREST_Y[0] <= y <= FOREST_Y[1]):
        return False
    return True

# ---------------------------------------------------------------- instancing (no LOD thinning: the forest is the hero)
def scatter_gn(proto):
    nm = "F_Scatter_" + proto.name
    ng = bpy.data.node_groups.get(nm)
    if ng:
        return ng
    ng = bpy.data.node_groups.new(nm, "GeometryNodeTree")
    ng.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    N = ng.nodes; Ln = ng.links
    gi, go = N.new("NodeGroupInput"), N.new("NodeGroupOutput")
    oi = N.new("GeometryNodeObjectInfo"); oi.transform_space = "ORIGINAL"; oi.inputs["Object"].default_value = proto
    m2p = N.new("GeometryNodeMeshToPoints"); Ln.new(gi.outputs["Geometry"], m2p.inputs["Mesh"])
    iop = N.new("GeometryNodeInstanceOnPoints"); Ln.new(m2p.outputs["Points"], iop.inputs["Points"])
    Ln.new(oi.outputs["Geometry"], iop.inputs["Instance"])
    sa = N.new("GeometryNodeInputNamedAttribute"); sa.data_type = "FLOAT_VECTOR"; sa.inputs["Name"].default_value = "f_s"
    ra = N.new("GeometryNodeInputNamedAttribute"); ra.data_type = "FLOAT"; ra.inputs["Name"].default_value = "f_r"
    cx = N.new("ShaderNodeCombineXYZ"); Ln.new(ra.outputs["Attribute"], cx.inputs["Z"])
    Ln.new(sa.outputs["Attribute"], iop.inputs["Scale"]); Ln.new(cx.outputs[0], iop.inputs["Rotation"])
    Ln.new(iop.outputs["Instances"], go.inputs["Geometry"])
    return ng

def scatter(name, P, S, Rz, proto, c):
    me = bpy.data.meshes.new(name); me.vertices.add(len(P))
    me.vertices.foreach_set("co", np.asarray(P, np.float32).ravel())
    a = me.attributes.new("f_s", "FLOAT_VECTOR", "POINT"); a.data.foreach_set("vector", np.asarray(S, np.float32).ravel())
    b = me.attributes.new("f_r", "FLOAT", "POINT"); b.data.foreach_set("value", np.asarray(Rz, np.float32).ravel())
    ob = bpy.data.objects.new(name, me); c.objects.link(ob)
    md = ob.modifiers.new("Scatter", "NODES"); md.node_group = scatter_gn(proto)
    return ob

def proto_obj(name, bm, mats, c):
    ob = C.mesh_obj(name, bm, mats, c)
    ob.location = (0, 0, -20000.0)
    return ob

# ---------------------------------------------------------------- giant trees
def tree_proto(name, seed, c, mats):
    rnd = random.Random(seed)
    bm = bmesh.new()
    H = 92.0
    n = 10
    rings = [(0.0, 4.6), (2.5, 3.6), (8.0, 3.1), (40.0, 2.6), (70.0, 2.0), (H, 1.2)]
    vs = []
    for z, r in rings:
        vs.append([bm.verts.new((r * math.cos(k * math.tau / n) * (1 + 0.08 * math.sin(k * 2.3 + seed)),
                                 r * math.sin(k * math.tau / n), z)) for k in range(n)])
    for a, b in zip(vs, vs[1:]):
        for k in range(n):
            f = bm.faces.new((a[k], a[(k + 1) % n], b[(k + 1) % n], b[k])); f.material_index = 0; f.smooth = True
    # thick horizontal limbs 18-55 m
    for i in range(7):
        z = rnd.uniform(18, 58); ang = rnd.uniform(0, math.tau); L = rnd.uniform(9, 17); r = rnd.uniform(0.6, 1.0)
        d = Vector((math.cos(ang), math.sin(ang), rnd.uniform(0.05, 0.25))).normalized()
        p0 = Vector((0, 0, z)); p1 = p0 + d * L
        res = bmesh.ops.create_cone(bm, cap_ends=True, segments=5, radius1=r, radius2=r * 0.5, depth=L)
        rot = d.to_track_quat("Z", "Y").to_matrix().to_4x4()
        bmesh.ops.transform(bm, matrix=rot, verts=res["verts"])
        bmesh.ops.translate(bm, vec=(p0 + p1) / 2, verts=res["verts"])
        for f in {f for v in res["verts"] for f in v.link_faces}:
            f.material_index = 0
    # canopy: flattened blobs 55-100 m (dark conifer-ish), one darker under-layer
    for i in range(9):
        z = rnd.uniform(56, 98); ang = rnd.uniform(0, math.tau); rr = rnd.uniform(0, 7.0) if i else 0.0
        R = rnd.uniform(9.5, 14.0) * (1.15 - (z - 56) / 110)
        res = bmesh.ops.create_icosphere(bm, subdivisions=1, radius=R)
        for v in res["verts"]:
            v.co.z *= 0.55
            v.co += Vector((rr * math.cos(ang), rr * math.sin(ang), z))
            v.co += Vector((noise.noise(v.co * 0.2) * 2.0, noise.noise(v.co * 0.2 + Vector((5, 1, 2))) * 2.0, 0))
        for f in {f for v in res["verts"] for f in v.link_faces}:
            f.material_index = 1 if i % 3 else 2
            f.smooth = True
    return proto_obj(name, bm, mats, c)

SHAM_TRUNK = (255.0, 1530.0)              # = seg_f3.SHAM_F
def _low_cam_F():
    """F xy of every f2 / f3 camera sample below 110 m (key z is above ground), every 0.1 s."""
    out = []
    try:
        import seg_f2, seg_f3
        for m in (seg_f2, seg_f3):
            for k in range(int(m.DUR * 10) + 1):
                loc, _, _ = m.CAM.eval(k / 10.0)
                if loc[2] < 110.0:
                    out.append((loc[0] - C.FO[0], loc[1] - C.FO[1]))
    except Exception as ex:
        print("[forest] camera corridor skipped:", ex, flush=True)
    return out

def build_forest(c):
    bark = C.mat("F_Bark", (0.20, 0.11, 0.07), 0.9)
    leaf = C.mat("F_Leaf", (0.040, 0.085, 0.035), 0.85)
    leaf2 = C.mat("F_Leaf2", (0.055, 0.11, 0.045), 0.85)
    protos = [tree_proto(f"F_Tree{i}", 31 + i, c, [bark, leaf, leaf2]) for i in range(4)]
    rnd = random.Random(1717)
    pts = []
    step = float(os.environ.get("F_TREE_STEP", "21"))
    x = FOREST_X[0]
    while x <= FOREST_X[1]:
        y = FOREST_Y[0]
        while y <= FOREST_Y[1]:
            px, py = x + rnd.uniform(-0.42, 0.42) * step, y + rnd.uniform(-0.42, 0.42) * step
            ok = in_forest_F(px, py)
            # ragged forest edge: trees thin out in the outer 120 m
            edge = min(px - FOREST_X[0], FOREST_X[1] - px, py - FOREST_Y[0], FOREST_Y[1] - py)
            if ok and edge < 120 and rnd.random() > edge / 120 + 0.25:
                ok = False
            if ok and road_dist_F(px, py) < 9.5:
                ok = False
            if ok and any(math.hypot(px - cx, py - cy) < r for (cx, cy), r in CLEAR):
                ok = False
            if ok:
                pts.append((px, py))
            y += step
        x += step
    # a few trunks right at the trap clearing / swamp rim (the anime frames them close)
    for (cx, cy), r in CLEAR[:2]:
        for k in range(8):
            a = k * math.tau / 8 + 0.3
            pts.append((cx + (r + 5) * math.cos(a), cy + (r + 5) * math.sin(a)))
    # the trunks she sits against (sham, rescue), and a clear corridor round every LOW camera position of f2 / f3
    pts.append((SHAM_TRUNK[0], SHAM_TRUNK[1])); pts.append((RESCUE_F[0] + 1.0, RESCUE_F[1] + 1.0))
    cam = _low_cam_F()
    if len(cam):
        P = np.array(pts)
        d = np.full(len(P), 1e9)
        for c in cam:
            d = np.minimum(d, np.hypot(P[:, 0] - c[0], P[:, 1] - c[1]))
        keep = (d > 18.0)
        keep[-2:] = True
        pts = [tuple(p) for p, k in zip(P, keep) if k]
    groups = [[] for _ in protos]
    for i, (px, py) in enumerate(pts):
        w = C.F(px, py)
        s = rnd.uniform(0.82, 1.12)
        groups[i % len(protos)].append(((w[0], w[1], C.G(w[0], w[1]) - 0.5), (s, s, s * rnd.uniform(0.9, 1.1)), rnd.uniform(0, math.tau)))
    for k, g in enumerate(groups):
        if g:
            scatter(f"F_Forest{k}", [a for a, _, _ in g], [b for _, b, _ in g], [r for _, _, r in g], protos[k], c)
    STATE["trees"] = pts
    print(f"[forest] {len(pts)} giant trees", flush=True)
    # forest floor: dark mossy carpet over the forest footprint (+ the clearings stay lighter)
    floor = C.mat("F_Floor", (0.075, 0.07, 0.035), 0.95)
    bm = bmesh.new(); cell = 25.0
    nx = int((FOREST_X[1] - FOREST_X[0] + 200) / cell); ny = int((FOREST_Y[1] - FOREST_Y[0] + 200) / cell)
    V = {}
    def vert(i, j):
        if (i, j) not in V:
            fx, fy = FOREST_X[0] - 100 + i * cell, FOREST_Y[0] - 100 + j * cell
            w = C.F(fx, fy); V[(i, j)] = bm.verts.new((w[0], w[1], C.G(w[0], w[1]) + 0.25))
        return V[(i, j)]
    for i in range(nx):
        for j in range(ny):
            bm.faces.new((vert(i, j), vert(i + 1, j), vert(i + 1, j + 1), vert(i, j + 1)))
    C.mesh_obj("F_ForestFloor", bm, [floor], c)
    # fallen logs
    logm = C.mat("F_Log", (0.17, 0.10, 0.06), 0.9)
    bm = bmesh.new()
    for i in range(260):
        px, py = rnd.uniform(*FOREST_X), rnd.uniform(*FOREST_Y)
        if road_dist_F(px, py) < 12:
            continue
        w = C.F(px, py); L = rnd.uniform(18, 40); a = rnd.uniform(0, math.pi)
        res = bmesh.ops.create_cone(bm, cap_ends=True, segments=6, radius1=1.3, radius2=1.0, depth=L)
        rot = Vector((math.cos(a), math.sin(a), 0)).to_track_quat("Z", "Y").to_matrix().to_4x4()
        bmesh.ops.transform(bm, matrix=rot, verts=res["verts"])
        bmesh.ops.translate(bm, vec=(w[0], w[1], C.G(w[0], w[1]) + 1.0), verts=res["verts"])
    C.mesh_obj("F_Logs", bm, [logm], c)
    # swamp water in the duel clearing
    water = C.mat("F_Swamp", (0.05, 0.07, 0.05), 0.08)
    bm = bmesh.new()
    w = C.F(*SWAMP_F); z = C.G(w[0], w[1]) + 0.32
    res = bmesh.ops.create_circle(bm, cap_ends=True, segments=24, radius=SWAMP_R)
    bmesh.ops.translate(bm, vec=(w[0], w[1], z), verts=res["verts"])
    C.mesh_obj("F_SwampWater", bm, [water], c)

def build_trap(c):
    """launcher racks round the trap clearing (2 x 3 barrels x 7 tubes each in the anime; here 14 racks), the exit gate."""
    wood = C.mat("F_RackWood", (0.32, 0.22, 0.12), 0.8); iron = C.mat("F_RackIron", (0.12, 0.12, 0.13), 0.4)
    white = C.mat("F_Rail", (0.86, 0.84, 0.78), 0.7)
    bm = bmesh.new()
    racks = []
    for k in range(14):
        a = k * math.tau / 14 + 0.12
        r = TRAP_R + 10 + 6 * (k % 2)
        fx, fy = TRAP_F[0] + r * math.cos(a), TRAP_F[1] + r * math.sin(a)
        zoff = [0.0, 0.0, 12.0, 24.0][k % 4]                     # on the ground, on logs, on branches
        w = C.F(fx, fy); z = C.G(w[0], w[1]) + zoff
        racks.append((w[0], w[1], z + 2.0))
        d = Vector((TRAP_F[0] - fx, TRAP_F[1] - fy, 0)).normalized()
        res = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(3.0, 2.2, 1.6), verts=res["verts"])
        rot = d.to_track_quat("Y", "Z").to_matrix().to_4x4()
        bmesh.ops.transform(bm, matrix=rot, verts=res["verts"])
        bmesh.ops.translate(bm, vec=(w[0], w[1], z + 1.2), verts=res["verts"])
        if zoff:                                                   # a platform plank under raised racks
            res = bmesh.ops.create_cube(bm, size=1.0)
            bmesh.ops.scale(bm, vec=(5.0, 5.0, 0.4), verts=res["verts"])
            bmesh.ops.translate(bm, vec=(w[0], w[1], z + 0.2), verts=res["verts"])
    C.mesh_obj("F_Racks", bm, [wood], c)
    STATE["racks"] = racks
    # exit gate: white railings across the road on a paved stretch between two huge trunks
    bm = bmesh.new()
    w = C.F(*EXIT_F); z = C.G(w[0], w[1])
    for sx in (-1, 1):
        res = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(9.0, 0.5, 1.4), verts=res["verts"])
        bmesh.ops.translate(bm, vec=(w[0] + sx * 7.5, w[1], z + 1.2), verts=res["verts"])
    C.mesh_obj("F_ExitRail", bm, [white], c)
    pave = C.mat("F_Pave", (0.42, 0.40, 0.36), 0.9)
    bm = bmesh.new()
    res = bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=1.0)
    bmesh.ops.scale(bm, vec=(6.0, 30.0, 1.0), verts=res["verts"])
    bmesh.ops.translate(bm, vec=(w[0], w[1], z + 0.4), verts=res["verts"])
    C.mesh_obj("F_Paved", bm, [pave], c)

def build_road(c):
    W = C.world_mod()
    dense = W._dense(ROAD_F, 30.0)
    STATE["road_dense"] = dense
    bm = bmesh.new()
    left, right = [], []
    for i, p in enumerate(dense):
        a, b = dense[max(0, i - 1)], dense[min(len(dense) - 1, i + 1)]
        d = Vector((b[0] - a[0], b[1] - a[1])).normalized(); n = Vector((-d.y, d.x)) * 4.5
        for side, lst in ((1, left), (-1, right)):
            fx, fy = p[0] + side * n.x, p[1] + side * n.y
            w = C.F(fx, fy)
            lst.append(bm.verts.new((w[0], w[1], C.G(w[0], w[1]) + 0.4)))
    for i in range(len(dense) - 1):
        bm.faces.new((left[i], right[i], right[i + 1], left[i + 1]))
    C.mesh_obj("F_Road", bm, [C.mat("F_Dirt", (0.30, 0.24, 0.15), 0.95)], c)

# ---------------------------------------------------------------- towns (scene.py house_mesh variants)
def house_variants(M, c, n=12, seed=5, ruined=False):
    L = sys.modules["aotlib"]
    rnd = random.Random(seed)
    walls = ["plaster", "plaster_w", "plaster_o", "timber"]
    roofs = ["roof_red", "roof_brown", "roof_dark", "roof_orange", "roof_red"]
    out = []
    for i in range(n):
        w = rnd.uniform(7.5, 11); d = rnd.uniform(11, 15); h = rnd.choice((8, 11, 11, 14, 14, 17))
        me = L.house_mesh(f"FH{seed}_{i}", w, d, h, d * 0.45, M, walls[i % 4], roofs[(i // 4) % 5], chimney=i % 3 == 0, hip=i % 5 == 0)
        ob = bpy.data.objects.new(me.name, me); c.objects.link(ob); ob.location = (0, 0, -20000.0)
        if ruined:                                             # a ruin: no roof (drop the top 30 %), darker
            ob.scale = (1.0, 1.0, 0.7)
        out.append((ob, w, d))
    return out

def place_town(name, variants, pts, c):
    """pts: [(x, y, yaw)] W."""
    groups = [[] for _ in variants]
    rnd = random.Random(len(pts))
    for i, (x, y, a) in enumerate(pts):
        k = rnd.randrange(len(variants))
        groups[k].append(((x, y, C.G(x, y) - 0.3), (1, 1, 1), a))
    for k, g in enumerate(groups):
        if g:
            ob, _, _ = variants[k]
            # keep the variant's own scale (ruins are squashed)
            sc = tuple(ob.scale)
            scatter(f"{name}{k}", [p for p, _, _ in g], [sc for _ in g], [a for _, _, a in g], ob, c)

def karanes_points():
    """house points inside the Karanes bulge (centre line along +x from the ring (19000, 24000) to the gate (19870, 24000))."""
    rnd = random.Random(1999)
    pts = []
    cx, cy = 19000.0, 24000.0
    def inside(x, y):
        dx, dy = x - cx, y - cy
        if abs(dy) > 455:
            return False
        if dx < -260 or dx > 850:
            return False
        if dx > 390 and math.hypot(dx - 390, dy) > 452:
            return False
        if dx < 0:                                              # inside Wall Rose: town continues ~250 m
            r = math.hypot(x - C.MITRAS[0], y - C.MITRAS[1])
            return r < 18990
        r = math.hypot(x - C.MITRAS[0], y - C.MITRAS[1])
        return r > 19012 or abs(dy) < 470
    x = cx - 250
    while x < cx + 850:
        y = cy - 450
        while y < cy + 450:
            px, py = x + rnd.uniform(-2, 2), y + rnd.uniform(-2, 2)
            if inside(px, py) and abs(py - cy) > 9 and abs((px - cx) % 90 - 45) > 6 and abs((py - cy) % 70) > 6:
                pts.append((px, py, math.pi / 2 if rnd.random() < 0.8 else 0.0))
            y += 17.0
        x += 14.0
    return pts

def build_karanes(M, c):
    v = house_variants(M, c, 12, seed=7)
    pts = karanes_points()
    place_town("F_Karanes", v, pts, c)
    print(f"[forest] Karanes {len(pts)} houses", flush=True)
    # outer gate: arch recess + door on the bulge tip (the world wall runs through; this sits on its outer face)
    gx, gy = C.KARANES_GATE
    stone = M.get("stone") or C.mat("F_Stone", (0.55, 0.52, 0.46), 0.85)
    dark = C.mat("F_GateDark", (0.02, 0.018, 0.016), 0.9)
    door = C.mat("F_GateDoor", (0.17, 0.11, 0.07), 0.7)
    bm = bmesh.new()
    res = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(4.0, 34.0, 30.0), verts=res["verts"])           # gatehouse frame
    bmesh.ops.translate(bm, vec=(gx + 6.5, gy, 15.0), verts=res["verts"])
    C.mesh_obj("F_KaranesGateFrame", bm, [stone], c)
    bm = bmesh.new()
    res = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(0.6, 14.0, 20.0), verts=res["verts"])
    bmesh.ops.translate(bm, vec=(gx + 8.7, gy, 10.0), verts=res["verts"])
    C.mesh_obj("F_KaranesGateDark", bm, [dark], c)
    bm = bmesh.new()
    res = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(1.0, 14.0, 20.0), verts=res["verts"])
    bmesh.ops.translate(bm, vec=(0, 0, 10.0), verts=res["verts"])
    dob = C.mesh_obj("F_KaranesGateDoor", bm, [door], c)
    dob.location = (gx + 9.3, gy, 0.0)
    STATE["gate_door"] = dob
    # apron road from the gate
    return pts

def gate_open(u):
    """0 closed .. 1 open (the door rises into the gatehouse)."""
    d = STATE.get("gate_door")
    if d:
        d.location.z = 21.0 * u

def build_oldtown(M, c):
    v = house_variants(M, c, 8, seed=11, ruined=True)
    rnd = random.Random(88)
    pts = []
    ox, oy = OLDTOWN_F
    for i in range(110):
        a = rnd.uniform(0, math.tau); r = 180 * math.sqrt(rnd.random())
        fx, fy = ox + r * math.cos(a), oy + r * math.sin(a)
        if road_dist_F(fx, fy, ROAD_F) < 10:
            continue
        w = C.F(fx, fy); pts.append((w[0], w[1], rnd.uniform(0, math.tau)))
    place_town("F_OldTown", v, pts, c)
    # old stone tower
    stone = C.mat("F_TowerStone", (0.50, 0.47, 0.42), 0.9)
    bm = bmesh.new(); w = C.F(ox + 60, oy + 40)
    res = bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=7, radius2=6, depth=34)
    bmesh.ops.translate(bm, vec=(w[0], w[1], C.G(w[0], w[1]) + 17), verts=res["verts"])
    C.mesh_obj("F_OldTower", bm, [stone], c)

def build_village(M, c):
    v = house_variants(M, c, 8, seed=13)
    rnd = random.Random(44)
    pts = []
    ox, oy = VILLAGE_F
    for i in range(60):
        a = rnd.uniform(0, math.tau); r = 140 * math.sqrt(rnd.random()) + 15
        fx, fy = ox + r * math.cos(a), oy + r * math.sin(a)
        w = C.F(fx, fy); pts.append((w[0], w[1], rnd.choice((0.0, math.pi / 2)) + rnd.uniform(-0.2, 0.2)))
    STATE["village_houses"] = pts
    place_town("F_Village", v, pts, c)
    # windmills: tower + 4 sails (sails rotate in update via STATE["sails"])
    wood = C.mat("F_MillWood", (0.42, 0.33, 0.22), 0.8); sailm = C.mat("F_Sail", (0.85, 0.82, 0.74), 0.9)
    STATE["sails"] = []
    for k, (dx, dy) in enumerate(((-170, 60), (150, -110), (40, 180))):
        w = C.F(ox + dx, oy + dy); z = C.G(w[0], w[1])
        bm = bmesh.new()
        res = bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=5.0, radius2=3.0, depth=18)
        bmesh.ops.translate(bm, vec=(w[0], w[1], z + 9), verts=res["verts"])
        C.mesh_obj(f"F_Mill{k}", bm, [wood], c)
        bm = bmesh.new()
        for a in range(4):
            res = bmesh.ops.create_cube(bm, size=1.0)
            bmesh.ops.scale(bm, vec=(0.3, 2.4, 12.0), verts=res["verts"])
            bmesh.ops.translate(bm, vec=(0, 0, 6.5), verts=res["verts"])
            bmesh.ops.rotate(bm, verts=res["verts"], cent=(0, 0, 0), matrix=Matrix.Rotation(a * math.pi / 2, 3, "X"))
        sob = C.mesh_obj(f"F_MillSail{k}", bm, [sailm], c)
        sob.location = (w[0] - 3.6, w[1], z + 16.0)
        STATE["sails"].append(sob)

def mills(t):
    for k, s in enumerate(STATE.get("sails", [])):
        s.rotation_euler = (t * 0.9 + k, 0.0, 0.0)

# ---------------------------------------------------------------- world vegetation: keep it out of my zones
def prune_world_veg():
    def bad(x, y):
        fx, fy = x - C.FO[0], y - C.FO[1]
        if FOREST_X[0] - 40 <= fx <= FOREST_X[1] + 40 and FOREST_Y[0] - 40 <= fy <= FOREST_Y[1] + 40:
            return True
        if math.hypot(fx - VILLAGE_F[0], fy - VILLAGE_F[1]) < 200 or math.hypot(fx - OLDTOWN_F[0], fy - OLDTOWN_F[1]) < 220:
            return True
        if -300 < x - 19000 < 900 and abs(y - 24000) < 520:
            return True
        if -9300 < fy < -150 and -350 < fx < 1750:            # the f1 plain: formation + Female corridor stays open
            return True
        if -2000 < fx < -1200 and -6500 < fy < 1600:          # the f3 retreat route west of the forest
            return True
        return road_dist_F(fx, fy, ROAD_F) < 14 and fy < 0
    n = 0
    for ob in list(bpy.data.objects):
        if ob.type != "MESH" or not any(m.type == "NODES" and m.name == "Scatter" for m in ob.modifiers) or ob.name.startswith("F_"):
            continue
        me = ob.data
        co = np.zeros(len(me.vertices) * 3); me.vertices.foreach_get("co", co); co = co.reshape(-1, 3)
        kill = [i for i, p in enumerate(co) if bad(p[0], p[1])]          # world._points: vertices in world coordinates
        if kill:
            bm = bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table()
            bmesh.ops.delete(bm, geom=[bm.verts[i] for i in kill], context="VERTS"); bm.to_mesh(me); bm.free()
            n += len(kill)
    print(f"[forest] pruned {n} world vegetation points", flush=True)

# ---------------------------------------------------------------- entry
MAT_NAMES = dict(plaster="Plaster", plaster_w="PlasterW", plaster_o="PlasterO", timber="Timber", roof_red="RoofRed",
                 roof_brown="RoofBrown", roof_dark="RoofDark", roof_orange="RoofOrange", roof_slate="RoofSlate",
                 stone_light="StoneLight", window="Window", stone="WallStone")
def scene_mats():
    """scene.py's material dict rebuilt from bpy.data (for builders called from a segment, e.g. seg_f0 in the Trost set)."""
    M = {}
    for k, nm in MAT_NAMES.items():
        m = bpy.data.materials.get(nm) or next((x for x in bpy.data.materials if x.name.startswith(nm)), None)
        M[k] = m or C.mat("F_" + nm, (0.6, 0.5, 0.4), 0.8)
    return M

def build_all(M, root=None, parts=("road", "forest", "trap", "karanes", "oldtown", "village", "prune")):
    """Build the part 2 objects (W coordinates).  root: an empty whose location maps W into this scene (Trost set:
    (0, -5000, 0)); every new top-level object is parented to it."""
    import time
    c = C.coll("ForestSet")
    fns = dict(road=lambda: build_road(c), forest=lambda: build_forest(c), trap=lambda: build_trap(c),
               karanes=lambda: build_karanes(M, c), oldtown=lambda: build_oldtown(M, c), village=lambda: build_village(M, c),
               prune=prune_world_veg)
    for name in parts:
        t = time.time()
        if os.environ.get("F_SKIP_" + name.upper()):
            continue
        try:
            fns[name]()
        except Exception as ex:
            import traceback; traceback.print_exc()
            print(f"[forest] {name} FAILED: {ex!r}", flush=True)
        print(f"[forest] {name} {time.time() - t:.1f}s", flush=True)
    if root is not None:
        for ob in c.all_objects:
            if ob.parent is None and ob is not root:
                ob.parent = root
    return c

def build_set(M, year=850):
    import time
    t0 = time.time()
    sc = bpy.context.scene
    C.make_sky(sc)
    W = C.world_mod()
    W.build(M, year, {"terrain": None})
    sys.modules["aotlib"].height = lambda x, y: C.G(x, y)       # render_seg ground checks / people_kit read aotlib.height
    build_all(M)
    print(f"[forest] set built in {time.time() - t0:.1f}s", flush=True)
    return M
