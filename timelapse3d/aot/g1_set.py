"""g1 set dressing for Shiganshina 845 (SCENE_BIBLE_v2 B.g1, D items 5 / 19 / 20) as a scene.py plug-in.

List it AFTER flight and BEFORE states845 / swarm845 in AOT_PLUGINS (render_g1.sh does): it edits the Town scatter
(raises the houses on the Yeager rock terrace, clears the stair-lane and the landmark plots, hides the polka-dot
settlement north of Wall Maria) before states845's TownEdit / fx845 read it.

Builds
  * belfry (5 x 5 m, ~36 m, arched openings, pointed cap) at (+25, -540) and the onion-spire church (~35 m) at
    (+70, -560); the white plaza Monument is hidden and the plaza is bare dirt
  * the Yeager neighbourhood: a rough rock terrace (+DZ = 4.5 m) under the house block at YH (-165, -585), a stone
    stair-lane (6 m wide, 22 steps over ~30 m) falling north from the terrace head, rock outcrops along it, a covered
    well and an 8 m tree; the 5 m rock "just beyond" the ruin (shown by render_g1 when the 9 m rock lands)
  * the rural inner-gate zone north of Wall Maria (SCENE_BIBLE_v2 g2 hamlet list): 9 low red-roof cottages + a windmill
    instead of scene.py's tall town houses
  * a gold "mackerel" altocumulus layer (camera-only card, 1.7 km up)
  * rock_lump(): rounded, faceted rock lumps (thrown rocks are never cubes) for render_g1 to swap into fx845's blocks
height_patch() returns the terrace / lane height once build() has run (the base terrain mesh is built flat first), so
seq_carla, swarm845 and render_g1 place Carla, the Smiling Titan and people on the terrace.
Env: G1_TERRACE_DZ (4.5), G1_NORTH (1: cottages instead of the settlement), G1_CLOUDS (1), AOT_YEAGER_XY.
"""
import bpy, bmesh, math, os, random
from mathutils import Vector, Matrix, noise
import aotlib as L

REPLACES = set()
YH = Vector(tuple(float(v) for v in os.environ.get("AOT_YEAGER_XY", "-165,-585").split(",")))
DZ = float(os.environ.get("G1_TERRACE_DZ", "4.5"))
R_TER = 25.0                                  # terrace top radius around YH
LANE_W, LANE_LEN, LANE_STEPS = 6.0, 30.0, 22  # stair-lane falling north from the terrace head (bible: 5-6 m, 20-25 steps / 30 m)
BELFRY = (25.0, -540.0)
CHURCH = (70.0, -560.0)
# east-heavy hamlet north of the inner gate (ep02 05:25 pan; bible AUDIT CORRECTIONS 1-3): the old west-of-road cottages
# (-60,40) (-115,70) (-45,115) (-150,125) moved east of the road; windmill stays west at (-95, 165); canal east
COTTAGES = [(40, 45), (85, 95), (35, 110), (140, 150), (55, 135), (95, 190), (130, 60), (300, 80), (325, 170)]
WINDMILL = (-95, 165)
STATE = {"active": False}

def _r_ter(a):
    """Terrace rim radius at angle a (irregular, rocky)."""
    return R_TER * (1.0 + 0.10 * noise.noise(Vector((math.cos(a) * 1.3, math.sin(a) * 1.3, 4.7))))

def lane_box():
    """(x0, x1, y0, y1) of the stair-lane (runs from the terrace rim north, downhill)."""
    y0 = YH.y + _r_ter(math.pi / 2) - 1.0
    return (YH.x - LANE_W / 2, YH.x + LANE_W / 2, y0, y0 + LANE_LEN)

def terrace_h(x, y):
    """Extra height of the terrace / lane at (x, y) (0 outside)."""
    d = Vector((x, y)) - YH.to_2d()
    r = d.length; a = math.atan2(d.y, d.x)
    rr = _r_ter(a)
    if r < rr:
        return DZ
    x0, x1, y0, y1 = lane_box()
    if x0 - 0.5 <= x <= x1 + 0.5 and y0 <= y <= y1:
        return DZ * (1.0 - (y - y0) / (y1 - y0))
    if r < rr + 2.5:                           # rock skirt
        return DZ * (1.0 - (r - rr) / 2.5)
    return 0.0

def height_patch(x, y, h):
    if not STATE["active"]:
        return h
    return h + terrace_h(x, y)

# ---------------------------------------------------------------- helpers
def _mats(M):
    if "rock" in STATE:
        return STATE
    STATE["rock"] = L.mat("G1Rock", (0.34, 0.33, 0.27), 0.92, var=0.32, var_scale=0.22, color2=(0.16, 0.19, 0.12))
    STATE["rock_l"] = L.mat("G1RockLight", (0.46, 0.44, 0.36), 0.9, var=0.3, var_scale=0.3, color2=(0.22, 0.26, 0.15))
    STATE["flag"] = L.mat("G1Flagstone", (0.44, 0.37, 0.26), 0.9, var=0.25, var_scale=0.6, color2=(0.40, 0.37, 0.30))
    STATE["onion"] = L.mat("G1Onion", (0.16, 0.20, 0.17), 0.55, var=0.15, var_scale=0.5, color2=(0.22, 0.27, 0.21))
    STATE["bell"] = L.mat("G1BelfryStone", (0.66, 0.62, 0.52), 0.85, var=0.18, var_scale=0.4, color2=(0.56, 0.52, 0.44))
    STATE["dark"] = L.mat("G1Opening", (0.03, 0.025, 0.02), 0.9)
    STATE["cott_wall"] = L.mat("G1CottWall", (0.70, 0.64, 0.54), 0.9)
    STATE["cott_roof"] = L.mat("G1CottRoof", (0.48, 0.12, 0.05), 0.75, var=0.15, var_scale=0.3, color2=(0.58, 0.18, 0.07))
    STATE["sail"] = L.mat("G1MillSail", (0.80, 0.77, 0.70), 0.9)
    STATE["mill"] = L.mat("G1MillTower", (0.42, 0.20, 0.10), 0.85)
    return STATE

def lump_mesh(name, seed, squash=(1.0, 0.88, 0.72), amp=0.18, sub=2):
    """Unit-size (diameter ~1) rough rounded rock lump, faceted (bible: rough natural lumps, never cubes)."""
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=0.5)
    off = Vector((seed * 3.71, seed * 1.37, seed * 5.13))
    for v in bm.verts:
        n = v.co.normalized()
        d = amp * noise.fractal(n * 1.4 + off, 0.6, 2.0, 4) + 0.06 * noise.noise(n * 5.0 + off)
        p = n * 0.5 * (1.0 + d)
        v.co = Vector((p.x * squash[0], p.y * squash[1], p.z * squash[2]))
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = False
    return me

def rock_lump(name, loc, size, seed, mat, coll=None, rot=None, squash=(1.0, 0.88, 0.72)):
    me = lump_mesh(name, seed, squash)
    me.materials.append(mat)
    ob = bpy.data.objects.new(name, me)
    (coll or bpy.context.scene.collection).objects.link(ob)
    ob.location = loc; ob.scale = (size, size, size)
    rr = random.Random(seed)
    ob.rotation_euler = rot or (rr.uniform(-0.3, 0.3), rr.uniform(-0.3, 0.3), rr.uniform(0, 6.28))
    return ob

def _town_edit(fn):
    """fn(i, x, y, z) -> None | 'hide' | dz for every Town / TownTrees point; writes co / dead back."""
    n_h = n_r = 0
    for name in ("Town", "TownTrees"):
        ob = bpy.data.objects.get(name)
        if not ob:
            continue
        me = ob.data; n = len(me.vertices)
        co = [0.0] * (3 * n); me.vertices.foreach_get("co", co)
        dead = [0.0] * n; me.attributes["dead"].data.foreach_get("value", dead)
        for i in range(n):
            r = fn(name, co[3 * i], co[3 * i + 1], co[3 * i + 2])
            if r == "hide":
                if dead[i] > 0:
                    dead[i] = -99999.0; n_h += 1
            elif r:
                co[3 * i + 2] += r; n_r += 1
        me.vertices.foreach_set("co", co)
        me.attributes["dead"].data.foreach_set("value", dead)
        me.update()
    return n_h, n_r

# ---------------------------------------------------------------- landmarks
def belfry(M, coll):
    """Slim pale-stone belfry (ep01 12318 / ep02 3643): 5 x 5 m shaft, arched belfry openings, pointed cap."""
    S = _mats(M); bm = bmesh.new()
    x, y = BELFRY; w = 5.2
    L.box(bm, (x, y, 0.8), (w + 1.2, w + 1.2, 1.6), mi=0)                    # plinth
    L.box(bm, (x, y, 13.5), (w, w, 27.0), mi=0)                              # shaft
    L.box(bm, (x, y, 27.3), (w + 0.7, w + 0.7, 0.6), mi=0)                   # cornice
    L.box(bm, (x, y, 30.3), (w - 0.2, w - 0.2, 5.4), mi=0)                   # belfry stage
    L.box(bm, (x, y, 33.2), (w + 0.6, w + 0.6, 0.5), mi=0)
    for s in (-1, 1):                                                         # arched openings, all 4 faces
        for k in (-0.9, 0.9):
            L.box(bm, (x + k, y + s * (w / 2 - 0.05), 30.0), (1.1, 0.4, 3.4), mi=2)
            L.box(bm, (x + s * (w / 2 - 0.05), y + k, 30.0), (0.4, 1.1, 3.4), mi=2)
    for k in range(3):                                                        # small slit windows on the shaft
        L.box(bm, (x, y - w / 2 - 0.02, 8 + k * 6.5), (0.6, 0.3, 1.6), mi=2)
    h0, h1 = 33.45, 41.0                                                      # pointed pyramid cap
    c = [bm.verts.new((x + sx * (w / 2 + 0.25), y + sy * (w / 2 + 0.25), h0)) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    top = bm.verts.new((x, y, h1))
    for i in range(4):
        bm.faces.new((c[i], c[(i + 1) % 4], top)).material_index = 1
    bm.faces.new(list(reversed(c))).material_index = 1
    return L.obj_from_bm("G1Belfry", bm, [S["bell"], M.get("roof_slate") or S["onion"], S["dark"]], coll)

def _lathe(bm, x, y, prof, seg=16, mi=0):
    """Surface of revolution from a (z, r) profile (bottom -> top)."""
    rings = []
    for z, r in prof:
        if r < 1e-3:
            rings.append([bm.verts.new((x, y, z))])
        else:
            rings.append([bm.verts.new((x + math.cos(2 * math.pi * k / seg) * r, y + math.sin(2 * math.pi * k / seg) * r, z)) for k in range(seg)])
    for a, b in zip(rings, rings[1:]):
        if len(a) == 1 and len(b) == 1:
            continue
        if len(a) == 1:
            for k in range(seg):
                bm.faces.new((a[0], b[k], b[(k + 1) % seg])).material_index = mi
        elif len(b) == 1:
            for k in range(seg):
                bm.faces.new((a[k], a[(k + 1) % seg], b[0])).material_index = mi
        else:
            for k in range(seg):
                bm.faces.new((a[k], a[(k + 1) % seg], b[(k + 1) % seg], b[k])).material_index = mi

def onion_church(M, coll):
    """Baroque church with a bulbous onion spire + lantern (ep01 18:40.9 26874), ~35 m, nave east-west."""
    S = _mats(M); bm = bmesh.new()
    x, y = CHURCH
    wall = M.get("plaster_w")
    # nave 26 x 12 m, 13 m to the eaves, steep tile roof (mi 1)
    L.box(bm, (x + 4, y, 6.5), (26, 12, 13), mi=0)
    p = [bm.verts.new(c) for c in [(x - 9.4, y - 6.4, 13), (x + 17.4, y - 6.4, 13), (x + 17.4, y + 6.4, 13), (x - 9.4, y + 6.4, 13),
                                     (x - 9.4, y, 20.5), (x + 17.4, y, 20.5)]]
    for fv in [(p[0], p[1], p[5], p[4]), (p[2], p[3], p[4], p[5]), (p[1], p[2], p[5]), (p[3], p[0], p[4])]:
        bm.faces.new(fv).material_index = 1
    # west tower 7 x 7 m to 23 m, cornice, octagonal drum, onion bulb, lantern, small spire
    tx, ty = x - 13.0, y
    L.box(bm, (tx, ty, 11.5), (7.0, 7.0, 23.0), mi=0)
    L.box(bm, (tx, ty, 23.3), (7.8, 7.8, 0.6), mi=0)
    for s in (-1, 1):
        L.box(bm, (tx, ty + s * 3.52, 19.0), (1.4, 0.3, 3.0), mi=3)
        L.box(bm, (tx + s * 3.52, ty, 19.0), (0.3, 1.4, 3.0), mi=3)
    _lathe(bm, tx, ty, [(23.6, 2.9), (25.6, 2.9)], seg=8, mi=0)              # drum
    _lathe(bm, tx, ty, [(25.6, 2.9), (26.4, 3.6), (27.6, 3.9), (28.8, 3.5), (30.0, 2.4), (30.9, 1.2), (31.4, 0.5)], seg=16, mi=2)
    _lathe(bm, tx, ty, [(31.4, 0.7), (32.9, 0.7)], seg=8, mi=0)              # lantern
    _lathe(bm, tx, ty, [(32.9, 0.8), (33.5, 0.9), (34.0, 0.5), (36.0, 0.0)], seg=8, mi=2)
    for k in range(4):                                                        # nave windows
        L.box(bm, (x - 3 + k * 6, y - 6.03, 7.5), (1.4, 0.2, 4.0), mi=3)
        L.box(bm, (x - 3 + k * 6, y + 6.03, 7.5), (1.4, 0.2, 4.0), mi=3)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return L.obj_from_bm("G1ChurchOnion", bm, [wall, M.get("roof_red"), S["onion"], S["dark"]], coll)

def gate_crest(M, coll):
    """Outer face of the outer gate (ep01 18:36.9): a small shield crest over the passage + a cornice band (P2 dressing)."""
    S = _mats(M); bm = bmesh.new()
    gx, gy = L.OUTER_GATE
    fy = gy - L.WALL_T / 2 - 0.7                       # just proud of the outer face (the face tapers: ~-725 at mid height)
    L.box(bm, (gx, fy, 25.5), (5.2, 0.8, 6.4), mi=0)                       # shield block
    L.box(bm, (gx, fy - 0.35, 26.5), (3.6, 0.3, 3.0), mi=1)                # dark emblem field
    L.box(bm, (gx, fy - 0.45, 27.0), (1.6, 0.25, 1.6), mi=0)               # boss
    L.box(bm, (gx, fy + 0.2, 22.2), (14.0, 1.2, 0.8), mi=0)                # cornice under the crest
    return L.obj_from_bm("G1GateCrest", bm, [S["bell"], S["dark"]], coll)

# ---------------------------------------------------------------- the Yeager neighbourhood
def yeager_terrace(M, coll):
    S = _mats(M)
    bm = bmesh.new()
    n = 56
    top, skirt = [], []
    for k in range(n):
        a = 2 * math.pi * k / n
        r = _r_ter(a)
        top.append(bm.verts.new((YH.x + math.cos(a) * r, YH.y + math.sin(a) * r, DZ + 0.05)))
        r2 = r + 2.0 + 1.2 * (0.5 + 0.5 * noise.noise(Vector((math.cos(a) * 3, math.sin(a) * 3, 1.9))))
        skirt.append(bm.verts.new((YH.x + math.cos(a) * r2, YH.y + math.sin(a) * r2, -0.4)))
    f = bm.faces.new(top); f.material_index = 0
    for k in range(n):
        bm.faces.new((skirt[k], skirt[(k + 1) % n], top[(k + 1) % n], top[k])).material_index = 1
    ob = L.obj_from_bm("G1YeagerTerrace", bm, [S["flag"], S["rock"]], coll)
    # rock outcrops round the rim (pale grey, mossy), half sunk
    rnd = random.Random(31)
    for k in range(44):
        a = rnd.uniform(0, 2 * math.pi)
        if abs(math.sin(a) - 1.0) < 0.05:
            continue
        r = _r_ter(a) + rnd.uniform(0.0, 2.2)
        s = rnd.uniform(2.6, 5.2)
        rock_lump(f"G1TerraceRock{k}", (YH.x + math.cos(a) * r, YH.y + math.sin(a) * r, DZ * rnd.uniform(0.25, 0.85)), s,
                  200 + k, S["rock_l"], coll)
    # stair-lane: 22 steps falling north, pale stone, rock outcrops along both sides
    x0, x1, y0, y1 = lane_box()
    bm = bmesh.new()
    d = (y1 - y0) / LANE_STEPS; rise = DZ / LANE_STEPS
    for k in range(LANE_STEPS):
        hz = DZ - k * rise
        L.box(bm, ((x0 + x1) / 2, y0 + (k + 0.5) * d, (hz - 0.4) / 2), (LANE_W, d + 0.02, hz + 0.4))
    L.obj_from_bm("G1StairLane", bm, [S["flag"]], coll)
    for k in range(14):
        side = -1 if k % 2 else 1
        yy = y0 + 2 + (k // 2) * 4.3 + rnd.uniform(-1, 1)
        hz = DZ * (1 - (yy - y0) / (y1 - y0))
        rock_lump(f"G1LaneRock{k}", (YH.x + side * (LANE_W / 2 + rnd.uniform(1.0, 2.5)), yy, hz * 0.5), rnd.uniform(1.6, 3.4) + hz * 0.4,
                  300 + k, S["rock_l"], coll)
    # covered well at the lane head (timber posts, cross braces, small pyramid roof ~2.5 m)
    wx, wy, wz = YH.x + LANE_W / 2 + 4.5, y0 - 3.5, DZ
    bm = bmesh.new()
    L.cyl(bm, (wx, wy, wz), (wx, wy, wz + 0.9), 1.3, 1.3, seg=12, mi=0)
    for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        L.box(bm, (wx + sx * 1.1, wy + sy * 1.1, wz + 1.25), (0.22, 0.22, 2.5), mi=1)
    L.box(bm, (wx, wy - 1.1, wz + 2.1), (2.4, 0.18, 0.18), mi=1); L.box(bm, (wx, wy + 1.1, wz + 2.1), (2.4, 0.18, 0.18), mi=1)
    c = [bm.verts.new((wx + sx * 1.45, wy + sy * 1.45, wz + 2.5)) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    tp = bm.verts.new((wx, wy, wz + 3.9))
    for i in range(4):
        bm.faces.new((c[i], c[(i + 1) % 4], tp)).material_index = 2
    L.obj_from_bm("G1CoveredWell", bm, [S["flag"], M.get("gate") or S["rock"], M.get("roof_dark") or S["onion"]], coll)
    # an 8 m deciduous tree beside the lane
    tx, ty = YH.x - LANE_W / 2 - 4.0, y0 + 9.0
    bm = bmesh.new()
    gz = DZ * (1 - (ty - y0) / (y1 - y0)) * 0.3
    L.cyl(bm, (tx, ty, gz - 0.3), (tx + 0.3, ty, gz + 4.5), 0.35, 0.22, seg=7, mi=1)
    for k in range(6):
        bmesh.ops.create_icosphere(bm, subdivisions=1, radius=rnd.uniform(1.6, 2.4),
                                   matrix=Matrix.Translation((tx + rnd.uniform(-1.6, 1.6), ty + rnd.uniform(-1.6, 1.6), gz + rnd.uniform(5.2, 7.2))))
    L.obj_from_bm("G1LaneTree", bm, [M.get("leaf") or S["onion"], M.get("bark") or S["rock"]], coll)
    # the second (~5 m) rock just beyond the ruin (ep01 32607); render_g1 shows it when the 9 m rock lands
    b = rock_lump("G1YHRock2", (YH.x + 4.0, YH.y - 13.0, DZ + 1.4), 5.0, 77, S["rock"], coll, squash=(1.1, 0.95, 0.7))
    b.hide_render = True
    STATE["rock2"] = b
    return ob

# ---------------------------------------------------------------- north of Wall Maria: hamlet cottages + windmill
def north_cottages(M, coll):
    S = _mats(M)
    try:
        import flight as FL
    except Exception:
        return None
    bm = bmesh.new(); rnd = random.Random(12)
    for x, y in COTTAGES:
        FL.farmhouse(bm, x, y, rnd.uniform(-0.4, 0.4) + (math.pi / 2 if rnd.random() < 0.4 else 0.0),
                     w=rnd.uniform(7.0, 9.5), dpt=rnd.uniform(5.0, 6.5), hgt=rnd.uniform(3.6, 4.6))
    FL.windmill(bm, WINDMILL[0], WINDMILL[1], 0.6, 1.25)
    return L.obj_from_bm("G1Cottages", bm, [S["cott_wall"], S["cott_roof"], S["sail"]], coll)

# ---------------------------------------------------------------- mackerel sky
def mackerel_sky(z=1700.0, size=60000.0):
    """Rippled gold altocumulus (ep01 17:36.8): wave bands x noise, camera-only, no shadows."""
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=size / 2, matrix=Matrix.Translation((0, -2000, z)))
    m = bpy.data.materials.new("G1Mackerel"); m.use_nodes = True
    nt = m.node_tree; N = nt.nodes; Ln = nt.links
    for nd in list(N):
        if nd.type != "OUTPUT_MATERIAL":
            N.remove(nd)
    out = [nd for nd in N if nd.type == "OUTPUT_MATERIAL"][0]
    tc = N.new("ShaderNodeTexCoord")
    dn = N.new("ShaderNodeTexNoise"); dn.inputs["Scale"].default_value = 0.0009; dn.inputs["Detail"].default_value = 3
    Ln.new(tc.outputs["Object"], dn.inputs["Vector"])
    wv = N.new("ShaderNodeTexWave"); wv.inputs["Scale"].default_value = float(os.environ.get("G1_CLOUD_WAVE", "0.0028")); wv.inputs["Distortion"].default_value = 7.0
    wv.inputs["Detail"].default_value = 3.0; wv.inputs["Detail Scale"].default_value = 1.6
    try:
        wv.bands_direction = "DIAGONAL"
    except Exception:
        pass
    Ln.new(tc.outputs["Object"], wv.inputs["Vector"])
    cn = N.new("ShaderNodeTexNoise"); cn.inputs["Scale"].default_value = 0.0016; cn.inputs["Detail"].default_value = 6
    cn.inputs["Roughness"].default_value = 0.6
    Ln.new(tc.outputs["Object"], cn.inputs["Vector"])
    mu = N.new("ShaderNodeMath"); mu.operation = "MULTIPLY"
    Ln.new(wv.outputs["Fac"], mu.inputs[0]); Ln.new(cn.outputs["Fac"], mu.inputs[1])
    # patchy coverage: large-scale noise switches the ripples on and off
    cov = N.new("ShaderNodeMapRange"); cov.inputs["From Min"].default_value = 0.36; cov.inputs["From Max"].default_value = 0.56
    Ln.new(dn.outputs["Fac"], cov.inputs["Value"])
    mu2 = N.new("ShaderNodeMath"); mu2.operation = "MULTIPLY"
    Ln.new(mu.outputs[0], mu2.inputs[0]); Ln.new(cov.outputs["Result"], mu2.inputs[1])
    rp = N.new("ShaderNodeMapRange"); rp.inputs["From Min"].default_value = 0.14; rp.inputs["From Max"].default_value = 0.30
    rp.inputs["To Max"].default_value = 0.85
    Ln.new(mu2.outputs[0], rp.inputs["Value"])
    sh = N.new("ShaderNodeMix"); sh.data_type = "RGBA"; Ln.new(rp.outputs["Result"], sh.inputs["Factor"])
    sh.inputs["A"].default_value = (0.78, 0.66, 0.46, 1); sh.inputs["B"].default_value = (1.0, 0.93, 0.74, 1)
    em = N.new("ShaderNodeEmission"); em.inputs["Strength"].default_value = float(os.environ.get("G1_CLOUD_E", "3.0"))
    Ln.new(sh.outputs["Result"], em.inputs["Color"])
    tr = N.new("ShaderNodeBsdfTransparent")
    mx = N.new("ShaderNodeMixShader"); Ln.new(rp.outputs["Result"], mx.inputs[0])
    Ln.new(tr.outputs[0], mx.inputs[1]); Ln.new(em.outputs[0], mx.inputs[2])
    Ln.new(mx.outputs[0], out.inputs["Surface"])
    try:
        m.surface_render_method = "BLENDED"
    except Exception:
        pass
    ob = L.obj_from_bm("G1MackerelSky", bm, [m])
    for attr in ("visible_shadow", "visible_diffuse", "visible_glossy", "visible_transmission", "visible_volume_scatter"):
        if hasattr(ob, attr):
            setattr(ob, attr, False)
    STATE["sky_mat"] = m
    return ob

# ---------------------------------------------------------------- build
def build(M, year, ctx):
    coll = L.new_coll("G1Set")
    _mats(M)
    x0, x1, y0, y1 = lane_box()
    north = os.environ.get("G1_NORTH", "1") == "1"
    def edit(name, x, y, z):
        if x0 - 3.5 <= x <= x1 + 3.5 and y0 - 2.0 <= y <= y1 + 4.0:
            return "hide"                                      # the stair-lane
        if math.hypot(x - BELFRY[0], y - BELFRY[1]) < 9.0 or (CHURCH[0] - 22 < x < CHURCH[0] + 25 and abs(y - CHURCH[1]) < 13):
            return "hide"                                      # landmark plots
        if north and name == "Town" and y > 12.0:
            return "hide"                                      # settlement north of Wall Maria -> cottages
        d = math.hypot(x - YH.x, y - YH.y)
        rr = _r_ter(math.atan2(y - YH.y, x - YH.x))
        if d < rr - 3.0:
            return DZ                                          # houses on the rock terrace
        if d < rr + 4.0:
            return "hide"                                      # nothing straddles the terrace rim
        return None
    nh, nr = _town_edit(edit)
    mo = bpy.data.objects.get("Monument")
    if mo:
        mo.hide_render = mo.hide_viewport = True
    pz = bpy.data.objects.get("Plaza")
    if pz and M.get("dirt"):
        pz.data.materials[0] = M["dirt"]                       # bare dirt plaza (ep01 18:16.5)
    dg = bpy.data.objects.get("DistrictGround")             # no flat grey void between the rows: warm packed earth
    if dg and os.environ.get("G1_GROUND", "1") == "1":       # with cobbled / trodden patches (~30 m)
        gm = L.mat("G1TownGround", (0.40, 0.31, 0.20), 0.95, var=0.28, var_scale=0.035, color2=(0.47, 0.43, 0.36))
        dg.data.materials[0] = gm
    gate_crest(M, coll)
    belfry(M, coll); onion_church(M, coll)
    yeager_terrace(M, coll)
    if north:
        north_cottages(M, coll)
    if os.environ.get("G1_CLOUDS", "1") == "1":
        mackerel_sky()
    STATE["active"] = True
    print(f"[g1_set] town points hidden {nh}, raised {nr}; terrace at {tuple(YH)} +{DZ} m; lane {tuple(round(v, 1) for v in lane_box())}")

LABELS = {"BELFRY": (BELFRY[0], BELFRY[1], 40), "YEAGER HOUSE": (YH.x, YH.y, 22)}
CAMS = {
    "g1_yeager": ((-86, -545, 117), (-160, -592, 3), 30),
    "g1_breach": ((-62, -250, 124), (-10, -680, 30), 45),
    "g1_belfry": ((80, -420, 90), (40, -560, 20), 35),
}
