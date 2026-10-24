"""EP1 opening flight + the episode-1 hill set (plug-in for scene.py).

Enable with AOT_PLUGINS=flight.  Owns: the hill with the big tree ~330 m north of Wall Maria (replaces scene.py's
HILL at (330, 820)), the kids (Eren asleep -> sits up -> stands, Mikasa standing with her red scarf), the farm
props between the tree and the wall (windmills, red-roof farmhouses, cypress groves, broad-leaf clumps), a watch
tower on the wall top, and the opening camera flight.

Flight (30 fps, frames are flight frames, 0 = first frame of chapter 2 "A Very Long Dream"):
  move A   f0   -> f300  very high over Shiganshina (whole U) gliding north over the inner wall into the
                         oblique map view of refs/user/shiganshina_aerial.png
  hold     f300 -> f330
  move B   f330 -> f720  swoop down and south onto the hill, the tree rises into frame, Wall Maria rises behind it
  hold     f720 -> f900  end framing = refs/user/ep1_tree_hill_wall.png; Eren wakes (lie f750, sits f810, stands f870)
Cameras exposed to scene.py: "flight_f0000" ... "flight_f0900" (opening, every frame), "flight_end", and
"ep1_g00750" ... "ep1_g07200": the whole of set B (chapters 2-9) in global EP1 frames, see camera_flight_ep1.md.
build_flight_camera() / build_setb_camera() make the animated cameras for a real animation render; state_at(g)
gives the AOT_STATE / AOT_EVENT / AOT_ARC_T values for a frame.  Stills: --cam flight_fNNNN (kids follow the frame).
Recommended light for chapter 2: SUN_AZ=-102 (sun behind the wall, front-right, as in the anime still).
Env: FL_NOKIDS, FL_NOGRASS, FL_LEAFY=0, FL_MOUNTAINS=0, FL_CLOUDS=0, FL_TREE=eren (use characters.eren_tree).
"""
import bpy, bmesh, math, random, sys, os
from mathutils import Vector, Matrix, noise
import aotlib as L

REPLACES = {"hill", "kids"}

# ---------------------------------------------------------------- end framing (matched to ep1_tree_hill_wall.png)
YAW = math.radians(float(os.environ.get("FL_YAW", "28")))     # view turned from due south toward +x (east)
F = Vector((math.sin(YAW), -math.cos(YAW)))                       # forward (horizontal)
R = Vector((F.y, -F.x))                                           # screen right
CAM_XY = Vector((float(os.environ.get("FL_CX", "-480")), float(os.environ.get("FL_CY", "338"))))
EYE = 0.55                                                        # camera height above the flower bank
LENS_END = 50.0
HFOV = 2 * math.atan(18.0 / LENS_END)

def loc2w(a, b):
    """Local (a = metres forward, b = metres right) of the end camera -> world xy."""
    return CAM_XY + F * a + R * b

def w2loc(x, y):
    d = Vector((x, y)) - CAM_XY
    return d.dot(F), d.dot(R)

def screen2w(u, dist):
    """Point at screen column u (0 left .. 1 right) at horizontal distance dist from the end camera."""
    th = math.atan((u - 0.5) * 2 * math.tan(HFOV / 2))
    return loc2w(dist * math.cos(th), dist * math.sin(th))

TREE_AB = (24.0, -5.7)                       # trunk base in local coords (screen u ~0.17, ~24 m away)
TREE = loc2w(*TREE_AB)

# ---------------------------------------------------------------- terrain
def _g(a, b, ca, cb, ra, rb):
    return math.exp(-(((a - ca) / ra) ** 2 + ((b - cb) / rb) ** 2))

def _smax(p, q, k=1.0):
    m = max(p, q)
    return m + k * math.log(math.exp((p - m) / k) + math.exp((q - m) / k))

HC = 5.0                                     # camera bank top above the valley floor at the wall foot

def hill_bump(a, b):
    """Height added to the flat valley floor (z = 0 near the wall). Local coords of the end camera."""
    ta, tb = TREE_AB
    knoll = (HC + EYE + 1.9) * _g(a, b, ta + 6, tb - 13, 45, 30)  # the tree's rise: crest left of / behind the trunk
    left = 9.0 * _g(a, b, 60, -60, 70, 40)                         # ground keeps climbing to the left
    fa = max(0.0, a - 3.5)
    bank = HC - 0.07 * fa * fa - 0.012 * b * b if a > -40 else 0.0  # the flower bank under the camera, dropping ahead
    bank = max(bank, 0.0) * _g(a, b, 0, 0, 60, 40) ** 0.2
    ridge = 0.0                                                    # pale sunny slope in the lower right
    for t in range(6):
        ra, rb = 38 + t * 11, 13 + t * 6.0
        ridge = max(ridge, (3.2 - t * 0.36) * _g(a, b, ra, rb, 14, 9))
    z = _smax(knoll, left, 0.4)
    z = _smax(z, bank, 0.25)
    z = _smax(z, ridge, 0.3)
    z += 0.25 * noise.noise(Vector((a / 14, b / 14, 4.2))) * min(1.0, z / 2)
    return z

def valley(a, b):
    """Gentle undulation of the meadows between the hill and the wall (fades out at the wall)."""
    x, y = loc2w(a, b)
    fade = min(1.0, max(0.0, (y - 30) / 80))
    return fade * (0.9 * noise.noise(Vector((x / 90, y / 90, 7.7))) + 0.25 * noise.noise(Vector((x / 25, y / 25, 1.3))))

def height_patch(x, y, h):
    a, b = w2loc(x, y)
    d = math.hypot(a - 40, b + 10)
    if d > 700:
        return h
    m = 1.0 - min(1.0, max(0.0, (d - 420) / 250))
    m = m * m * (3 - 2 * m)
    return h + m * (hill_bump(a, b) + valley(a, b))

# fine terrain patch (the base terrain is ~27 m per quad here, far too coarse for a camera 0.55 m above the grass)
PATCH_X = (-430.0, 430.0)          # around CAM_XY.x
PATCH_Y = (14.0, 260.0)            # absolute y min (just clear of the wall foot), y max above CAM_XY.y

def _warp(t, lo, hi):
    """t in [-1, 1] -> offset, dense at 0."""
    s = abs(t) ** 1.9
    return (hi if t > 0 else lo) * s

def build_patch(M, terrain):
    tm = terrain.data.materials[0]
    x0, x1 = CAM_XY.x + PATCH_X[0], CAM_XY.x + PATCH_X[1]
    y0, y1 = PATCH_Y[0], CAM_XY.y + PATCH_Y[1]
    # cut the coarse terrain under the patch (also keeps scene.py's forest scatter off the hill)
    me = terrain.data
    bm = bmesh.new(); bm.from_mesh(me)
    kill = []
    for f in bm.faces:
        c = f.calc_center_median()
        if x0 + 30 < c.x < x1 - 30 and y0 + 30 < c.y < y1 - 30:
            kill.append(f)
    bmesh.ops.delete(bm, geom=kill, context="FACES_ONLY")
    bm.to_mesh(me); bm.free()
    N = 300
    xs = sorted(set(CAM_XY.x + _warp(i / N * 2 - 1, x0 - CAM_XY.x, x1 - CAM_XY.x) for i in range(N + 1)))
    ys = sorted(set(CAM_XY.y + _warp(j / N * 2 - 1, y0 - CAM_XY.y, y1 - CAM_XY.y) for j in range(N + 1)))
    bm = bmesh.new()
    grid = [[bm.verts.new((x, y, L.height(x, y) + 0.06)) for y in ys] for x in xs]
    for i in range(len(xs) - 1):
        for j in range(len(ys) - 1):
            f = bm.faces.new((grid[i][j], grid[i + 1][j], grid[i + 1][j + 1], grid[i][j + 1]))
            f.smooth = True
    ob = L.obj_from_bm("HillGround", bm, [meadow_mat(tm)])
    return ob

def meadow_mat(tm):
    """Copy of the terrain material with a sunny anime meadow (yellow-green, pale dry patches, darker swales)
    mixed in around the hill; fades back to the base terrain colours 230-400 m from the end camera."""
    m = tm.copy(); m.name = "FL_Meadow"
    nt = m.node_tree; N = nt.nodes; Ln = nt.links
    b = N["Principled BSDF"]
    src = b.inputs["Base Color"].links[0].from_socket
    tc = N.new("ShaderNodeTexCoord")
    n1 = N.new("ShaderNodeTexNoise"); n1.inputs["Scale"].default_value = 0.018; n1.inputs["Detail"].default_value = 5
    Ln.new(tc.outputs["Object"], n1.inputs["Vector"])
    rp = N.new("ShaderNodeValToRGB"); e = rp.color_ramp.elements
    e[0].position, e[0].color = 0.38, (0.075, 0.16, 0.025, 1)
    e[1].position, e[1].color = 0.66, (0.40, 0.42, 0.12, 1)
    mid = rp.color_ramp.elements.new(0.52); mid.color = (0.17, 0.28, 0.045, 1)
    Ln.new(n1.outputs["Fac"], rp.inputs["Fac"])
    n2 = N.new("ShaderNodeTexNoise"); n2.inputs["Scale"].default_value = 0.6; n2.inputs["Detail"].default_value = 3
    Ln.new(tc.outputs["Object"], n2.inputs["Vector"])
    ov = N.new("ShaderNodeMix"); ov.data_type = "RGBA"; ov.blend_type = "OVERLAY"; ov.inputs["Factor"].default_value = 0.3
    Ln.new(rp.outputs["Color"], ov.inputs["A"]); Ln.new(n2.outputs["Color"], ov.inputs["B"])
    dv = N.new("ShaderNodeVectorMath"); dv.operation = "DISTANCE"; dv.inputs[1].default_value = (CAM_XY.x, CAM_XY.y, 0)
    sep = N.new("ShaderNodeSeparateXYZ"); Ln.new(tc.outputs["Object"], sep.inputs[0])
    cmb = N.new("ShaderNodeCombineXYZ"); Ln.new(sep.outputs["X"], cmb.inputs["X"]); Ln.new(sep.outputs["Y"], cmb.inputs["Y"])
    Ln.new(cmb.outputs[0], dv.inputs[0])
    fd = N.new("ShaderNodeMapRange"); fd.inputs["From Min"].default_value = 400; fd.inputs["From Max"].default_value = 230
    Ln.new(dv.outputs["Value"], fd.inputs["Value"])
    mx = N.new("ShaderNodeMix"); mx.data_type = "RGBA"
    Ln.new(fd.outputs["Result"], mx.inputs["Factor"]); Ln.new(src, mx.inputs["A"]); Ln.new(ov.outputs["Result"], mx.inputs["B"])
    Ln.new(mx.outputs["Result"], b.inputs["Base Color"])
    return m

# ---------------------------------------------------------------- materials
def flat(name, col, rough=0.8, var=0.0, col2=None, scale=0.5):
    if var:
        return L.mat(name, col, rough, var=var, var_scale=scale, color2=col2)
    return L.mat(name, col, rough)

def leaf_mat(name, c_dark, c_light, scale=1.2, bump=0.6):
    """Foliage with clumpy light/dark patches (voronoi cells) so blobs read as painted leaf masses."""
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; N = nt.nodes; Ln = nt.links; b = N["Principled BSDF"]
    tc = N.new("ShaderNodeTexCoord")
    vo = N.new("ShaderNodeTexVoronoi"); vo.inputs["Scale"].default_value = scale
    Ln.new(tc.outputs["Object"], vo.inputs["Vector"])
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = scale * 0.3; nz.inputs["Detail"].default_value = 3
    Ln.new(tc.outputs["Object"], nz.inputs["Vector"])
    mx = N.new("ShaderNodeMath"); mx.operation = "MULTIPLY_ADD"; mx.inputs[1].default_value = 0.7
    Ln.new(vo.outputs["Distance"], mx.inputs[0]); Ln.new(nz.outputs["Fac"], mx.inputs[2])
    rp = N.new("ShaderNodeValToRGB"); e = rp.color_ramp.elements
    e[0].position, e[0].color = 0.35, (*c_dark, 1); e[1].position, e[1].color = 0.85, (*c_light, 1)
    Ln.new(mx.outputs[0], rp.inputs["Fac"]); Ln.new(rp.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.85
    bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = bump
    Ln.new(vo.outputs["Distance"], bp.inputs["Height"]); Ln.new(bp.outputs["Normal"], b.inputs["Normal"])
    return m

# ---------------------------------------------------------------- props
def spindle(bm, base, h, r, seg=10, rings=12, wob=0.15, seed=0, mi=0):
    """Cypress: pointed spindle with lumpy foliage."""
    rr = random.Random(seed); ph = rr.uniform(0, 6)
    prev = None
    for i in range(rings + 1):
        t = i / rings
        rad = r * (math.sin(math.pi * min(1, t * 1.05)) ** 0.7) * (1.0 - 0.3 * t) + 0.03
        ring = []
        for k in range(seg):
            a = k / seg * math.tau
            w = 1 + wob * math.sin(a * 3 + ph + i * 1.7) * math.sin(i * 2.3 + ph)
            ring.append(bm.verts.new(base + Vector((math.cos(a) * rad * w, math.sin(a) * rad * w, t * h))))
        if prev:
            for k in range(seg):
                bm.faces.new((prev[k], prev[(k + 1) % seg], ring[(k + 1) % seg], ring[k])).material_index = mi
        prev = ring
    tip = bm.verts.new(base + Vector((0, 0, h * 1.04)))
    for k in range(seg):
        bm.faces.new((prev[k], prev[(k + 1) % seg], tip)).material_index = mi

def blob_cluster(bm, center, n, rad, spread, seed, squash=0.8, mi=0, trunk_mi=None):
    rr = random.Random(seed)
    for k in range(n):
        off = Vector((rr.uniform(-1, 1) * spread[0], rr.uniform(-1, 1) * spread[1], rr.uniform(0.3, 1) * spread[2]))
        r = rad * rr.uniform(0.6, 1.1)
        ico = bmesh.ops.create_icosphere(bm, subdivisions=2, radius=r)
        for v in ico["verts"]:
            nn = noise.noise(v.co * 1.3 + Vector((seed, k, 0)))
            v.co = center + off + Vector((v.co.x, v.co.y, v.co.z * squash)) * (1 + 0.2 * nn)
        for f in {f for v in ico["verts"] for f in v.link_faces}:
            f.material_index = mi

def farmhouse(bm, x, y, rot, w=6.5, dpt=4.5, hgt=3.4):
    """Small farmhouse: pale plaster box with a steep red gable roof (mi 0 wall, 1 roof)."""
    z = L.height(x, y) - 0.3
    Rm = Matrix.Rotation(rot, 4, "Z")
    r = bmesh.ops.create_cube(bm, size=1)
    bmesh.ops.transform(bm, matrix=Matrix.Translation((x, y, z + hgt / 2)) @ Rm @ Matrix.Diagonal((w, dpt, hgt, 1)), verts=r["verts"])
    rh = dpt * 0.62
    v = [Vector(p) for p in ((-w / 2 - .35, -dpt / 2 - .45, hgt), (w / 2 + .35, -dpt / 2 - .45, hgt), (w / 2 + .35, dpt / 2 + .45, hgt),
                              (-w / 2 - .35, dpt / 2 + .45, hgt), (-w / 2 - .35, 0, hgt + rh), (w / 2 + .35, 0, hgt + rh))]
    Mt = Matrix.Translation((x, y, z)) @ Rm
    vv = [bm.verts.new(Mt @ p) for p in v]
    for f in ((0, 1, 5, 4), (2, 3, 4, 5), (0, 4, 3), (1, 2, 5), (0, 3, 2, 1)):
        bm.faces.new([vv[i] for i in f]).material_index = 1
    if random.random() < 0.6:                                     # chimney
        r = bmesh.ops.create_cube(bm, size=1)
        bmesh.ops.transform(bm, matrix=Mt @ Matrix.Translation((w * 0.3, dpt * 0.15, hgt + rh * 0.8)) @ Matrix.Diagonal((0.6, 0.6, 1.6, 1)), verts=r["verts"])

def windmill(bm, x, y, rot, s=1.0):
    """Tower mill: tapered round tower (mi 0), conical cap (mi 1), four lattice sails (mi 2)."""
    z = L.height(x, y) - 0.3
    prev = None
    for i in range(7):
        t = i / 6; rad = (2.6 - 0.9 * t) * s
        ring = [bm.verts.new((x + math.cos(a) * rad, y + math.sin(a) * rad, z + t * 10.5 * s)) for a in [k / 10 * math.tau for k in range(10)]]
        if prev:
            for k in range(10):
                bm.faces.new((prev[k], prev[(k + 1) % 10], ring[(k + 1) % 10], ring[k]))
        prev = ring
    tip = bm.verts.new((x, y, z + 13.6 * s))
    for k in range(10):
        bm.faces.new((prev[k], prev[(k + 1) % 10], tip)).material_index = 1
    hub = Vector((x, y, z + 11.2 * s)) + Matrix.Rotation(rot, 3, "Z") @ Vector((0, -2.3 * s, 0))
    for k in range(4):
        a = k * math.pi / 2 + 0.45
        for part, (wd, ln, off) in enumerate(((0.25, 9.0, 4.5), (1.5, 7.0, 5.2))):
            r = bmesh.ops.create_cube(bm, size=1)
            Mx = (Matrix.Translation(hub) @ Matrix.Rotation(rot, 4, "Z") @ Matrix.Rotation(a, 4, "Y")
                  @ Matrix.Translation(((0.85 * s if part else 0), 0, off * s)) @ Matrix.Diagonal((wd * s, 0.12, ln * s, 1)))
            bmesh.ops.transform(bm, matrix=Mx, verts=r["verts"])
            for f in {f for v in r["verts"] for f in v.link_faces}:
                f.material_index = 2

def build_farms(M):
    rnd = random.Random(5)
    random.seed(9)
    wallm = flat("FL_HouseWall", (0.66, 0.60, 0.50), 0.9)
    roof = flat("FL_HouseRoof", (0.45, 0.085, 0.04), 0.75, var=0.15, col2=(0.55, 0.14, 0.06), scale=0.3)
    sail = flat("FL_MillSail", (0.78, 0.75, 0.68), 0.9)
    bm = bmesh.new()
    # farmhouses scattered in the valley near the wall foot (screen u, distance from the end camera)
    for u, dist, rot in ((0.43, 268, 0.3), (0.455, 262, -0.2), (0.47, 275, 0.2), (0.665, 270, 0.4), (0.70, 258, -0.3),
                         (0.735, 280, 0.1), (0.78, 262, 0.5), (0.80, 290, 0.2), (0.62, 300, 0.0), (0.58, 248, 0.7)):
        p = screen2w(u, dist)
        farmhouse(bm, p.x, p.y, rot + YAW + rnd.uniform(-0.2, 0.2), w=rnd.uniform(5.5, 8), dpt=rnd.uniform(4, 5))
    for u, dist, s in ((0.595, 285, 0.95), (0.715, 300, 0.9)):
        p = screen2w(u, dist)
        windmill(bm, p.x, p.y, YAW + 0.35, s)
    ob = L.obj_from_bm("FL_Farms", bm, [wallm, roof, sail])
    # cypress groves on the right, dark broad-leaf clumps mid valley, woods at the wall foot on the right
    cyp = leaf_mat("FL_Cypress", (0.010, 0.040, 0.020), (0.05, 0.12, 0.04), scale=1.5)
    fol = leaf_mat("FL_Foliage", (0.012, 0.045, 0.018), (0.07, 0.15, 0.04), scale=0.8)
    bm = bmesh.new(); k = 0
    for g in range(12):
        u = 0.84 + g * 0.02 + rnd.uniform(-0.01, 0.01)
        dist = 195 + g * 10 + rnd.uniform(-8, 8)
        c = screen2w(min(u, 1.05), dist)
        for j in range(rnd.randint(5, 9)):
            x = c.x + rnd.gauss(0, 3.0); y = c.y + rnd.gauss(0, 3.0)
            spindle(bm, Vector((x, y, L.height(x, y) - 0.6)), rnd.uniform(8, 14), rnd.uniform(1.6, 2.3), seed=k, wob=0.2); k += 1
    L.obj_from_bm("FL_Cypresses", bm, [cyp])
    bm = bmesh.new()
    c = screen2w(0.62, 118); blob_cluster(bm, Vector((c.x, c.y, L.height(c.x, c.y) - 0.8)), 30, 2.6, (7, 5, 6.5), 3, squash=0.9)
    c = screen2w(0.70, 130); blob_cluster(bm, Vector((c.x, c.y, L.height(c.x, c.y) - 0.8)), 14, 2.4, (5, 4, 5), 4, squash=0.9)
    c = screen2w(0.50, 200); blob_cluster(bm, Vector((c.x, c.y, L.height(c.x, c.y) - 0.6)), 6, 2.2, (4, 3, 3), 7)
    for k in range(22):                                       # woods along the wall foot, right side of frame
        p = screen2w(0.86 + k * 0.012, 300 - k * 4)
        blob_cluster(bm, Vector((p.x, p.y, L.height(p.x, p.y) - 1)), 4, 5.0, (5, 3, 6), 50 + k)
    for k in range(8):                                        # hedges / single trees left of centre
        p = screen2w(0.30 + k * 0.03, 310 + rnd.uniform(-20, 20))
        blob_cluster(bm, Vector((p.x, p.y, L.height(p.x, p.y) - 1)), 3, 3.4, (4, 3, 3), 80 + k)
    woods = L.obj_from_bm("FL_Woods", bm, [fol])
    if os.environ.get("FL_LEAFY", "1") != "0":
        try:
            leafy(woods, 1.2, scale=(4.0, 6.5), name="FL_WoodsLeafy")
        except Exception as ex:
            print("[flight] woods leafy failed", ex)
    return ob

def wall_seams(M, x0=-760.0, x1=-40.0, every=12.0):
    """Dark vertical joints between the wall's slabs (north face), the strongest pattern of the anime wall."""
    m = L.mat("FL_WallJoint", (0.05, 0.055, 0.07), 0.9)
    bm = bmesh.new()
    x = x0
    while x < x1:
        if abs(x) > 12:
            hw = 0.32
            yo = 0.0 if abs(x) <= L.W + 1 else (L.W ** 2 - x * x) / 32000.0     # scene.py's slight bend of Wall Maria
            ys = lambda z: yo + 5.0 - 1.2 * (z + 4) / 54.0 + 0.06    # wall north face (tapered profile) + offset
            v = [bm.verts.new((x - hw, ys(-2), -2)), bm.verts.new((x + hw, ys(-2), -2)),
                 bm.verts.new((x + hw, ys(49.6), 49.6)), bm.verts.new((x - hw, ys(49.6), 49.6))]
            bm.faces.new(v)
        x += every
    return L.obj_from_bm("FL_WallSeams", bm, [m])

def wall_tower(M):
    """Small square watch tower on the Wall Maria walk (seen near the frame centre in the anime still)."""
    # intersect the ray through screen column u = 0.54 (just right of the crown) with the wall line (y ~ 0 here)
    th = math.atan((0.54 - 0.5) * 2 * math.tan(HFOV / 2))
    dr = F * math.cos(th) + R * math.sin(th)
    t = (CAM_XY.y - 0.0) / -dr.y
    x = CAM_XY.x + dr.x * t
    bm = bmesh.new()
    z = L.WALL_H
    L.box(bm, (x, 0, z + 5.0), (7.0, 7.0, 10.0))
    L.box(bm, (x, 0, z + 10.4), (8.0, 8.0, 0.9))
    for dx in (-2.8, 0, 2.8):
        for dy in (-3.4, 3.4):
            L.box(bm, (x + dx, dy, z + 11.6), (1.6, 1.2, 1.6))
    L.box(bm, (x, 3.55, z + 6.5), (1.0, 0.2, 2.4), mi=1)
    L.box(bm, (x - 2.2, 3.55, z + 6.5), (0.8, 0.2, 2.0), mi=1)
    return L.obj_from_bm("FL_WallTower", bm, [M["stone"], M["window"]])

# ---------------------------------------------------------------- grass close to the camera
def grass_protos(M):
    coll = L.new_coll("FL_GrassProtos")
    gm = bpy.data.materials.new("FL_Blade"); gm.use_nodes = True
    nt = gm.node_tree; N = nt.nodes; Ln = nt.links; b = N["Principled BSDF"]
    oi = N.new("ShaderNodeObjectInfo")
    rp = N.new("ShaderNodeValToRGB"); e = rp.color_ramp.elements
    e[0].color = (0.11, 0.22, 0.03, 1); e[1].color = (0.36, 0.46, 0.09, 1)
    Ln.new(oi.outputs["Random"], rp.inputs["Fac"]); Ln.new(rp.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.7
    b.inputs["Subsurface Weight"].default_value = 0.15
    rnd = random.Random(3)
    for v in range(6):
        bm = bmesh.new()
        for k in range(rnd.randint(5, 9)):
            h = rnd.uniform(0.12, 0.32) * (1.4 if v >= 4 else 1.0)
            a = rnd.uniform(0, math.tau); lean = rnd.uniform(0.1, 0.5)
            d = Vector((math.cos(a), math.sin(a), 0))
            side = Vector((-d.y, d.x, 0)) * rnd.uniform(0.006, 0.012)
            o = d * rnd.uniform(0, 0.04)
            pts = [o + d * lean * h * (t * t) + Vector((0, 0, h * t)) for t in (0, 0.35, 0.7, 1.0)]
            wid = [1.0, 0.8, 0.5, 0.0]
            vs = []
            for p, w in zip(pts, wid):
                vs.append((bm.verts.new(p - side * w), bm.verts.new(p + side * w)))
            for i in range(3):
                if i < 2:
                    bm.faces.new((vs[i][0], vs[i][1], vs[i + 1][1], vs[i + 1][0]))
                else:
                    bm.faces.new((vs[i][0], vs[i][1], vs[i + 1][1]))
        ob = L.obj_from_bm(f"FL_P{v}_tuft", bm, [gm], coll=coll)
    # flowers: small white / yellow heads in drifts, blue bellflowers on the bank right in front of the camera
    fw = flat("FL_FlowerW", (0.85, 0.85, 0.80), 0.6); fy = flat("FL_FlowerY", (0.80, 0.62, 0.06), 0.6)
    for v, m in enumerate((fw, fy)):
        bm = bmesh.new()
        for k in range(4):
            o = Vector((rnd.uniform(-0.06, 0.06), rnd.uniform(-0.06, 0.06), rnd.uniform(0.10, 0.2)))
            bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.016, matrix=Matrix.Translation(o) @ Matrix.Diagonal((1, 1, 0.5, 1)))
        L.obj_from_bm(f"FL_P{6 + v}_flower", bm, [m], coll=coll)
    blue = bpy.data.materials.new("FL_Bellflower"); blue.use_nodes = True
    bb = blue.node_tree.nodes["Principled BSDF"]
    oi = blue.node_tree.nodes.new("ShaderNodeObjectInfo")
    rp = blue.node_tree.nodes.new("ShaderNodeValToRGB"); e = rp.color_ramp.elements
    e[0].color = (0.16, 0.18, 0.70, 1); e[1].color = (0.45, 0.50, 1.0, 1)
    blue.node_tree.links.new(oi.outputs["Random"], rp.inputs["Fac"]); blue.node_tree.links.new(rp.outputs["Color"], bb.inputs["Base Color"])
    bb.inputs["Roughness"].default_value = 0.5; bb.inputs["Subsurface Weight"].default_value = 0.3
    stem = flat("FL_Stem", (0.06, 0.16, 0.03), 0.7)
    for v in range(2):
        bm = bmesh.new()
        for k in range(2 + v):
            h = rnd.uniform(0.16, 0.30)
            top = Vector((rnd.uniform(-0.08, 0.08), rnd.uniform(-0.08, 0.08), h))
            L.cyl(bm, (top.x * 0.3, top.y * 0.3, 0), top, 0.004, 0.003, seg=4, mi=1)
            tilt = Matrix.Rotation(rnd.uniform(0.3, 1.1), 4, Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), 0)).normalized())
            n = 10; ring0 = []; ring1 = []
            for i in range(n):
                a = i / n * math.tau
                r1 = 0.058 if i % 2 == 0 else 0.040                   # five pointed petals
                ring0.append(bm.verts.new(Matrix.Translation(top) @ tilt @ Vector((math.cos(a) * 0.008, math.sin(a) * 0.008, 0))))
                ring1.append(bm.verts.new(Matrix.Translation(top) @ tilt @ Vector((math.cos(a) * r1, math.sin(a) * r1, 0.03 if i % 2 == 0 else 0.022))))
            for i in range(n):
                bm.faces.new((ring0[i], ring0[(i + 1) % n], ring1[(i + 1) % n], ring1[i])).material_index = 0
        L.obj_from_bm(f"FL_P{8 + v}_bell", bm, [blue, stem], coll=coll)
    bpy.context.view_layer.layer_collection.children["FL_GrassProtos"].exclude = True
    return coll

def build_grass(M, center, radius, density, near=7.0):
    """Disc of grass tufts around center; density falls off as (near/d)^2 so screen density stays even."""
    coll = grass_protos(M)
    bm = bmesh.new(); n = 64; rings = 40
    cv = bm.verts.new((center.x, center.y, L.height(center.x, center.y) + 0.06))
    vs = []
    for r in range(1, rings + 1):
        rr = radius * (r / rings) ** 1.5
        vs.append([bm.verts.new((center.x + math.cos(k / n * math.tau) * rr, center.y + math.sin(k / n * math.tau) * rr,
                                 0)) for k in range(n)])
        for v in vs[-1]:
            v.co.z = L.height(v.co.x, v.co.y) + 0.06
    for k in range(n):
        bm.faces.new((cv, vs[0][k], vs[0][(k + 1) % n]))
    for r in range(rings - 1):
        for k in range(n):
            bm.faces.new((vs[r][k], vs[r + 1][k], vs[r + 1][(k + 1) % n], vs[r][(k + 1) % n]))
    ob = L.obj_from_bm("FL_GrassDisc", bm, [])
    ng = bpy.data.node_groups.new("FL_GrassGN", "GeometryNodeTree")
    ng.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    N = ng.nodes; Ln = ng.links
    gi = N.new("NodeGroupInput"); go = N.new("NodeGroupOutput")
    dp = N.new("GeometryNodeDistributePointsOnFaces"); dp.inputs["Density"].default_value = density
    Ln.new(gi.outputs[0], dp.inputs["Mesh"])
    pos = N.new("GeometryNodeInputPosition")
    sp = N.new("ShaderNodeSeparateXYZ"); Ln.new(pos.outputs[0], sp.inputs[0])
    fl = N.new("ShaderNodeCombineXYZ"); Ln.new(sp.outputs["X"], fl.inputs["X"]); Ln.new(sp.outputs["Y"], fl.inputs["Y"])
    dc = N.new("ShaderNodeVectorMath"); dc.operation = "DISTANCE"; dc.inputs[1].default_value = (CAM_XY.x, CAM_XY.y, 0)
    Ln.new(fl.outputs[0], dc.inputs[0])
    mx = N.new("ShaderNodeMath"); mx.operation = "MAXIMUM"; mx.inputs[1].default_value = near
    Ln.new(dc.outputs["Value"], mx.inputs[0])
    dv = N.new("ShaderNodeMath"); dv.operation = "DIVIDE"; dv.inputs[0].default_value = near
    Ln.new(mx.outputs[0], dv.inputs[1])
    pw = N.new("ShaderNodeMath"); pw.operation = "POWER"; pw.inputs[1].default_value = 2.0
    Ln.new(dv.outputs[0], pw.inputs[0])
    rv = N.new("FunctionNodeRandomValue"); rv.data_type = "FLOAT"
    keep = N.new("FunctionNodeCompare"); keep.operation = "LESS_THAN"
    Ln.new(rv.outputs["Value"], keep.inputs[0]); Ln.new(pw.outputs[0], keep.inputs[1])
    ci = N.new("GeometryNodeCollectionInfo"); ci.inputs["Collection"].default_value = coll
    ci.inputs["Separate Children"].default_value = True; ci.inputs["Reset Children"].default_value = True
    iop = N.new("GeometryNodeInstanceOnPoints"); iop.inputs["Pick Instance"].default_value = True
    nobj = len(coll.objects)                    # 0..5 tufts, 6 white, 7 yellow, 8-9 bellflowers
    def rint(lo, hi, seed):
        r = N.new("FunctionNodeRandomValue"); r.data_type = "INT"; r.inputs["Min"].default_value = lo
        r.inputs["Max"].default_value = hi; r.inputs["Seed"].default_value = seed; return r.outputs[0]
    def rbool(p, seed):
        r = N.new("FunctionNodeRandomValue"); r.data_type = "BOOLEAN"; r.inputs["Probability"].default_value = p
        r.inputs["Seed"].default_value = seed; return r.outputs[0]
    def band(x, y):
        b = N.new("FunctionNodeBooleanMath"); b.operation = "AND"; Ln.new(x, b.inputs[0]); Ln.new(y, b.inputs[1]); return b.outputs[0]
    def switch(c, f, t):
        sw = N.new("GeometryNodeSwitch"); sw.input_type = "INT"
        Ln.new(c, sw.inputs["Switch"]); Ln.new(f, sw.inputs["False"]); Ln.new(t, sw.inputs["True"]); return sw.outputs[0]
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 0.15; Ln.new(pos.outputs[0], nz.inputs["Vector"])
    fmask = N.new("FunctionNodeCompare"); fmask.operation = "GREATER_THAN"; fmask.inputs[1].default_value = 0.58
    Ln.new(nz.outputs["Fac"], fmask.inputs[0])
    close = N.new("FunctionNodeCompare"); close.operation = "LESS_THAN"; close.inputs[1].default_value = 6.5
    dl = N.new("ShaderNodeVectorMath"); dl.operation = "DISTANCE"
    dl.inputs[1].default_value = (CAM_XY.x - R.x * 2.5, CAM_XY.y - R.y * 2.5, 0)    # the bed sits a little left
    Ln.new(fl.outputs[0], dl.inputs[0])
    Ln.new(dl.outputs["Value"], close.inputs[0])
    idx = switch(band(fmask.outputs[0], rbool(0.10, 5)), rint(0, 5, 1), rint(6, 7, 2))
    idx = switch(band(close.outputs[0], rbool(0.42, 6)), idx, rint(8, 9, 3))
    Ln.new(idx, iop.inputs["Instance Index"])
    rr = N.new("FunctionNodeRandomValue"); rr.data_type = "FLOAT_VECTOR"
    rr.inputs["Min"].default_value = (-0.15, -0.15, 0); rr.inputs["Max"].default_value = (0.15, 0.15, 6.28)
    Ln.new(rr.outputs["Value"], iop.inputs["Rotation"])
    rs = N.new("FunctionNodeRandomValue"); rs.data_type = "FLOAT"; rs.inputs["Min"].default_value = 0.6; rs.inputs["Max"].default_value = 1.05
    Ln.new(rs.outputs[0], iop.inputs["Scale"])
    far = N.new("FunctionNodeCompare"); far.operation = "GREATER_THAN"; far.inputs[1].default_value = 1.7
    Ln.new(dc.outputs["Value"], far.inputs[0])
    Ln.new(dp.outputs["Points"], iop.inputs["Points"]); Ln.new(band(keep.outputs[0], far.outputs[0]), iop.inputs["Selection"])
    Ln.new(ci.outputs[0], iop.inputs["Instance"])
    Ln.new(iop.outputs[0], go.inputs[0])
    ob.modifiers.new("Grass", "NODES").node_group = ng
    return ob

# ---------------------------------------------------------------- the tree and the kids
F_KIDS = 750          # flight frame at which Eren starts waking (lie 750-780, sit 810, crouch 850, stand 870)

def _tube(bm, pts, radii, seg=12, wob=0.0, seed=0, mi=0):
    n = len(pts); prev = None
    for i, (p, r) in enumerate(zip(pts, radii)):
        tng = (pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)]).normalized()
        q = tng.to_track_quat("Z", "Y").to_matrix()
        ring = []
        for k in range(seg):
            a = k / seg * math.tau
            w = 1 + wob * (math.sin(a * 4 + seed) * 0.6 + math.sin(a * 7 + i * 0.7 + seed) * 0.4)
            ring.append(bm.verts.new(p + q @ Vector((math.cos(a) * r * w, math.sin(a) * r * w, 0))))
        if prev:
            for k in range(seg):
                bm.faces.new((prev[k], prev[(k + 1) % seg], ring[(k + 1) % seg], ring[k])).material_index = mi
        prev = ring
    tip = bm.verts.new(pts[-1] + (pts[-1] - pts[-2]).normalized() * radii[-1])
    for k in range(seg):
        bm.faces.new((prev[k], prev[(k + 1) % seg], tip)).material_index = mi

def _bez(a, b, c, n=8):
    return [a * (1 - t) ** 2 + b * 2 * t * (1 - t) + c * t * t for t in [i / (n - 1) for i in range(n)]]

def leaf_sprig(name, mat, seed):
    """A sprig of 7 pointed oval leaves (real geometry, no alpha), ~0.25 m across."""
    rr = random.Random(seed)
    bm = bmesh.new()
    for k in range(7):
        Lf = rr.uniform(0.16, 0.24); Wd = Lf * 0.45
        yaw = k / 7 * math.tau + rr.uniform(-0.3, 0.3); pitch = rr.uniform(0.15, 0.6)
        Mx = Matrix.Rotation(yaw, 4, "Z") @ Matrix.Rotation(-pitch, 4, "X") @ Matrix.Translation((0, 0.04, 0))
        prof = [(Wd * 0.5, Lf * 0.15), (Wd * 0.62, Lf * 0.4), (Wd * 0.5, Lf * 0.68), (Wd * 0.22, Lf * 0.9)]
        left = [bm.verts.new(Mx @ Vector((x, y, 0.15 * x))) for x, y in prof]
        right = [bm.verts.new(Mx @ Vector((-x, y, 0.15 * x))) for x, y in prof]
        mid = [bm.verts.new(Mx @ Vector((0, y, -0.015))) for _, y in prof]
        b0 = bm.verts.new(Mx @ Vector((0, 0, -0.01))); tip = bm.verts.new(Mx @ Vector((0, Lf, 0.02)))
        bm.faces.new((b0, left[0], mid[0])); bm.faces.new((b0, mid[0], right[0]))
        for i in range(len(mid) - 1):
            bm.faces.new((mid[i], left[i], left[i + 1], mid[i + 1])); bm.faces.new((mid[i], mid[i + 1], right[i + 1], right[i]))
        bm.faces.new((mid[-1], left[-1], tip)); bm.faces.new((mid[-1], tip, right[-1]))
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(mat)
    for p in me.polygons:
        p.use_smooth = True
    return bpy.data.objects.new(name, me)

def leafy(crown, density, scale=(1.8, 2.8), name="FL_Leafy"):
    """Leaf sprigs scattered over the crown clumps, facing out along the surface normal (GN instances)."""
    coll = bpy.data.collections.get("FL_SprigProtos")
    if coll is not None:
        return _leafy_gn(crown, density, scale, coll, name)
    coll = L.new_coll("FL_SprigProtos")
    m = bpy.data.materials.new("FL_Sprig"); m.use_nodes = True
    nt = m.node_tree; N = nt.nodes; Ln = nt.links; b = N["Principled BSDF"]
    oi = N.new("ShaderNodeObjectInfo")
    rp = N.new("ShaderNodeValToRGB"); e = rp.color_ramp.elements
    e[0].position, e[0].color = 0.0, (0.025, 0.08, 0.03, 1); e[1].position, e[1].color = 1.0, (0.24, 0.42, 0.08, 1)
    mid = rp.color_ramp.elements.new(0.55); mid.color = (0.08, 0.20, 0.05, 1)
    Ln.new(oi.outputs["Random"], rp.inputs["Fac"]); Ln.new(rp.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.6; b.inputs["Subsurface Weight"].default_value = 0.2
    for k in range(4):
        coll.objects.link(leaf_sprig(f"FL_Sprig{k}", m, 10 + k))
    bpy.context.view_layer.layer_collection.children["FL_SprigProtos"].exclude = True
    return _leafy_gn(crown, density, scale, coll, name)

def _leafy_gn(crown, density, scale, coll, name):
    ng = bpy.data.node_groups.new(name + "GN", "GeometryNodeTree")
    ng.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    N = ng.nodes; Ln = ng.links
    gi = N.new("NodeGroupInput"); go = N.new("NodeGroupOutput")
    dp = N.new("GeometryNodeDistributePointsOnFaces"); dp.inputs["Density"].default_value = density
    Ln.new(gi.outputs[0], dp.inputs["Mesh"])
    al = N.new("FunctionNodeAlignRotationToVector"); al.axis = "Z"
    Ln.new(dp.outputs["Normal"], al.inputs["Vector"])
    jit = N.new("FunctionNodeRandomValue"); jit.data_type = "FLOAT_VECTOR"
    jit.inputs["Min"].default_value = (-0.6, -0.6, -3.14); jit.inputs["Max"].default_value = (0.6, 0.6, 3.14)
    e2r = N.new("FunctionNodeEulerToRotation"); Ln.new(jit.outputs[0], e2r.inputs[0])
    rot = N.new("FunctionNodeRotateRotation"); Ln.new(al.outputs[0], rot.inputs[0]); Ln.new(e2r.outputs[0], rot.inputs[1])
    ci = N.new("GeometryNodeCollectionInfo"); ci.inputs["Collection"].default_value = coll
    ci.inputs["Separate Children"].default_value = True; ci.inputs["Reset Children"].default_value = True
    iop = N.new("GeometryNodeInstanceOnPoints"); iop.inputs["Pick Instance"].default_value = True
    pk = N.new("FunctionNodeRandomValue"); pk.data_type = "INT"; pk.inputs["Min"].default_value = 0; pk.inputs["Max"].default_value = 3
    Ln.new(pk.outputs[0], iop.inputs["Instance Index"])
    sc = N.new("FunctionNodeRandomValue"); sc.data_type = "FLOAT"; sc.inputs["Min"].default_value = scale[0]; sc.inputs["Max"].default_value = scale[1]
    Ln.new(sc.outputs[0], iop.inputs["Scale"])
    Ln.new(dp.outputs["Points"], iop.inputs["Points"]); Ln.new(ci.outputs[0], iop.inputs["Instance"])
    Ln.new(rot.outputs[0], iop.inputs["Rotation"])
    jg = N.new("GeometryNodeJoinGeometry"); Ln.new(gi.outputs[0], jg.inputs[0]); Ln.new(iop.outputs[0], jg.inputs[0])
    Ln.new(jg.outputs[0], go.inputs[0])
    crown.modifiers.new("Leafy", "NODES").node_group = ng

def hill_tree(base, seed=4):
    """The episode-1 tree: a broad, low-crowned deciduous tree (~10 m), trunk leaning right with a fork at ~2.5 m,
    heavy limbs spreading wide, the crown a broad dome of leaf clumps that starts ~2 m up and droops low on the right
    (as in ep1_tree_hill_wall.png). Local frame: +x = screen right of the end camera, +y = away from it.
    Returns (trunk object, crown object)."""
    rnd = random.Random(seed)
    X = Vector((R.x, R.y, 0)); Y = Vector((F.x, F.y, 0)); Z = Vector((0, 0, 1))
    def W(v):
        return base + X * v[0] + Y * v[1] + Z * v[2]
    bark = None
    try:
        import characters
        bark = characters._bark()
    except Exception:
        bark = L.mat("FL_Bark", (0.07, 0.055, 0.04), 0.9, bump=0.5, scale=3.0, var=0.3, var_scale=2.0)
    bm = bmesh.new()
    fork = Vector((0.55, 0.15, 2.5))
    tr = _bez(Vector((0, 0, -0.6)), Vector((0.05, 0.05, 1.4)), fork, 9)
    _tube(bm, [W(p) for p in tr], [0.62, 0.50, 0.44, 0.41, 0.40, 0.39, 0.38, 0.37, 0.36], seg=16, wob=0.12, seed=1)
    for k in range(6):                                         # root flare
        a = k / 6 * math.tau + rnd.uniform(-0.3, 0.3)
        d = Vector((math.cos(a), math.sin(a), 0))
        _tube(bm, [W(Vector((0, 0, 0.9))), W(d * 0.7 + Vector((0, 0, 0.15))), W(d * 1.5 + Vector((0, 0, -0.35)))],
              [0.2, 0.16, 0.06], seg=7)
    ends = []
    limbs = [(-35, 3.3, 2.3), (-80, 4.6, 3.6), (15, 3.0, 1.5), (70, 3.0, 2.6), (140, 4.8, 2.8), (200, 5.0, 3.0), (105, 3.0, 4.2)]
    for ang, reach, rise in limbs:                            # ang: 0 = screen right, 90 = away from the camera
        a = math.radians(ang + rnd.uniform(-8, 8))
        d = Vector((math.cos(a), math.sin(a), 0))
        mid = fork + d * reach * 0.45 + Vector((0, 0, rise * 0.75))
        end = fork + d * reach + Vector((0, 0, rise - (1.2 if -60 < ang < 30 else 0)))
        pts = _bez(fork, mid, end, 7)
        _tube(bm, [W(p) for p in pts], [0.27 - 0.035 * i for i in range(7)], seg=9, wob=0.06)
        ends.append((pts, d))
        for j in range(2):                                    # secondary branches
            p0 = pts[3 + j]
            d2 = (d + Vector((rnd.uniform(-0.8, 0.8), rnd.uniform(-0.8, 0.8), rnd.uniform(0.1, 0.8)))).normalized()
            _tube(bm, [W(p0), W(p0 + d2 * 1.2), W(p0 + d2 * 2.4 + Vector((0, 0, 0.3)))], [0.09, 0.06, 0.03], seg=6)
    trunk = L.obj_from_bm("HillTree_trunk", bm, [bark])
    for p in trunk.data.polygons:
        p.use_smooth = True
    # foliage: clumps along the outer limbs plus a broad dome shell, flattened underneath
    cb = bmesh.new()
    def clump(c, r, sq=0.75):
        ico = bmesh.ops.create_icosphere(cb, subdivisions=2, radius=r)
        sd = rnd.uniform(0, 50)
        for v in ico["verts"]:
            nn = noise.noise(v.co * 1.6 + Vector((sd, 0, 0)))
            v.co = W(c + Vector((v.co.x, v.co.y, v.co.z * sq)) * (1 + 0.28 * nn))
    for pts, d in ends:
        for i in range(2, 7):
            for j in range(3):
                c = pts[i] + Vector((rnd.gauss(0, 0.9), rnd.gauss(0, 0.9), rnd.gauss(0.2, 0.5)))
                clump(c, rnd.uniform(0.6, 1.1))
    C = Vector((-2.2, 0.8, 5.6))
    for k in range(620):
        th = rnd.uniform(0, math.tau); ph = math.acos(rnd.uniform(-0.25, 1.0))
        rx, ry, rz = 5.9, 5.2, 3.3
        c = C + Vector((math.sin(ph) * math.cos(th) * rx, math.sin(ph) * math.sin(th) * ry, math.cos(ph) * rz))
        if c.x > 0:
            c.x *= 0.55
        if c.x > 2.0:                                          # the right side droops toward the kids
            c.z -= (c.x - 2.0) * 0.4
        c.z = max(c.z, 2.7 + max(0.0, -c.x) * 0.12)
        clump(c, rnd.uniform(0.6, 1.15))
    me = bpy.data.meshes.new("HillTree_crown"); cb.to_mesh(me); cb.free()
    for p in me.polygons:
        p.use_smooth = True
    me.materials.append(leaf_mat("FL_TreeLeaf", (0.02, 0.07, 0.025), (0.20, 0.38, 0.07), scale=2.2, bump=0.8))
    crown = bpy.data.objects.new("HillTree_crown", me); bpy.context.scene.collection.objects.link(crown)
    if os.environ.get("FL_LEAFY", "1") != "0":
        try:
            leafy(crown, float(os.environ.get("FL_LEAF_DENS", "14")))
        except Exception as ex:
            import traceback; traceback.print_exc(); print("[flight] leafy failed:", ex)
    return trunk, crown

def build_rock(a=8.6, b=0.4, size=1.9):
    path = os.path.join("E:/YTP2/3D Timelapse/assets/polyhaven", "boulder_01", "boulder_01_1k.blend")
    p = loc2w(a, b)
    if not os.path.exists(path):
        return None
    with bpy.data.libraries.load(path) as (src, dst):
        dst.objects = [n for n in src.objects]
    obs = [o for o in dst.objects if o and o.type == "MESH" and o.name.endswith("LOD0")]
    for o in obs:
        bpy.context.scene.collection.objects.link(o)
        dim = max(o.dimensions.x, o.dimensions.y) or 1.0
        k = size / dim
        o.scale = (k, k * 0.9, k * 0.55)
        o.rotation_euler.z = YAW + 0.4
        zmin = min(v.co.z for v in o.data.vertices) * k * 0.55
        o.location = (p.x, p.y, L.height(p.x, p.y) + 0.15 - zmin)
    return obs

def build_tree_and_kids(M):
    base = Vector((TREE.x, TREE.y, L.height(TREE.x, TREE.y) - 0.2))
    trunk = crown = None
    try:
        if os.environ.get("FL_TREE") == "eren":                    # the cloud's tree, scaled to the still
            import characters
            trunk, crown, r0 = characters.eren_tree(base, height=17.0)
            k = float(os.environ.get("FL_TREE_S", "0.6"))
            for ob in (trunk, crown):
                ob.scale = (k, k, k * 0.95)
        else:
            trunk, crown = hill_tree(base)
        bpy.context.view_layer.update()
    except Exception as ex:
        import traceback; traceback.print_exc()
        print("[flight] eren_tree failed:", ex)
    if os.environ.get("FL_NOKIDS"):
        return trunk
    try:
        import characters
        to_cam = (CAM_XY - TREE).normalized()
        fwd = (to_cam * 0.55 + R * 1.0).normalized()                 # Eren on the camera-right side of the trunk
        facing = math.atan2(fwd.x, -fwd.y)
        scn = bpy.context.scene
        eren, mik, f1, f2 = characters.place_opening(base, trunk_r=0.5, facing=facing, trunk=trunk, start=F_KIDS)
        mik.location = mik.location - Vector((R.x, R.y, 0)) * 0.9 + Vector((F.x, F.y, 0)) * 0.6
        mik.location.z = L.height(mik.location.x, mik.location.y) - 0.04
    except Exception as ex:
        import traceback; traceback.print_exc()
        print("[flight] place_opening failed:", ex)
    return trunk


# ---------------------------------------------------------------- scene tweaks for this set
def hide_town_north(xmax=-105.0):
    """scene.py's little settlement inside Wall Maria has tall town houses; the hill shot wants open farmland,
    so the settlement's west tail (in the end frame) never shows (dead < born)."""
    ob = bpy.data.objects.get("Town")
    if not ob:
        return 0
    me = ob.data
    n = len(me.vertices)
    co = [0.0] * (3 * n); me.vertices.foreach_get("co", co)
    dead = [0.0] * n; me.attributes["dead"].data.foreach_get("value", dead)
    k = 0
    for i in range(n):
        x, y = co[3 * i], co[3 * i + 1]
        if y > 12 and x < xmax:
            dead[i] = -99999.0; k += 1
    me.attributes["dead"].data.foreach_set("value", dead)
    me.update()
    return k

def haze_mat(name, c0, c1, haze=(0.42, 0.58, 0.86), dist=3500.0, scale=0.0015):
    """Painted far landscape: noise between two greens, fading to sky blue with camera-ray length."""
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; N = nt.nodes; Ln = nt.links; b = N["Principled BSDF"]
    tc = N.new("ShaderNodeTexCoord")
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = scale; nz.inputs["Detail"].default_value = 6
    Ln.new(tc.outputs["Object"], nz.inputs["Vector"])
    rp = N.new("ShaderNodeValToRGB"); e = rp.color_ramp.elements
    e[0].position, e[0].color = 0.4, (*c0, 1); e[1].position, e[1].color = 0.62, (*c1, 1)
    Ln.new(nz.outputs["Fac"], rp.inputs["Fac"])
    lp = N.new("ShaderNodeLightPath")
    f = N.new("ShaderNodeMath"); f.operation = "DIVIDE"; f.inputs[1].default_value = -dist
    Ln.new(lp.outputs["Ray Length"], f.inputs[0])
    ex = N.new("ShaderNodeMath"); ex.operation = "EXPONENT"; Ln.new(f.outputs[0], ex.inputs[0])
    inv = N.new("ShaderNodeMath"); inv.operation = "SUBTRACT"; inv.inputs[0].default_value = 1.0; Ln.new(ex.outputs[0], inv.inputs[1])
    mx = N.new("ShaderNodeMix"); mx.data_type = "RGBA"
    Ln.new(inv.outputs[0], mx.inputs["Factor"]); Ln.new(rp.outputs["Color"], mx.inputs["A"]); mx.inputs["B"].default_value = (*haze, 1)
    Ln.new(mx.outputs["Result"], b.inputs["Base Color"])
    em = N.new("ShaderNodeMath"); em.operation = "MULTIPLY"; em.inputs[1].default_value = 0.25
    Ln.new(inv.outputs[0], em.inputs[0])
    Ln.new(mx.outputs["Result"], b.inputs["Emission Color"]); Ln.new(em.outputs[0], b.inputs["Emission Strength"])
    b.inputs["Roughness"].default_value = 0.95
    return m

def _mt(u, d, alpha, r):
    """A peak at screen column u of the end frame, distance d, rising alpha radians above the end camera's eye."""
    return (u, d, alpha * d + 5.8, r)

MOUNTAINS = [  # far ranges (10-19 km, beyond scene.py's terrain): a green hill just clearing the wall top a little left
               # of centre and a blue range on the right that only just clears it (anime still); open sky on the left
    _mt(0.46, 10000, 0.138, 1700), _mt(0.56, 11000, 0.140, 1600), _mt(0.66, 14000, 0.142, 2500),
    _mt(0.80, 17000, 0.150, 3400), _mt(0.95, 19000, 0.156, 3800), _mt(1.15, 19000, 0.160, 4000),
]

def build_clouds(z=1900.0, size=90000.0):
    """A high layer of soft cumulus (camera-only, casts no shadow) so the sky above the wall is not empty."""
    if os.environ.get("FL_CLOUDS", "1") == "0":
        return None
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=size / 2, matrix=Matrix.Translation((CAM_XY.x, CAM_XY.y, z)))
    m = bpy.data.materials.new("FL_Cloud"); m.use_nodes = True
    nt = m.node_tree; N = nt.nodes; Ln = nt.links
    for n in list(N):
        if n.type != "OUTPUT_MATERIAL":
            N.remove(n)
    out = [n for n in N if n.type == "OUTPUT_MATERIAL"][0]
    tc = N.new("ShaderNodeTexCoord")
    mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1.0, 1.6, 1.0)
    Ln.new(tc.outputs["Object"], mp.inputs["Vector"])
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 0.00042; nz.inputs["Detail"].default_value = 7
    nz.inputs["Roughness"].default_value = 0.62
    Ln.new(mp.outputs["Vector"], nz.inputs["Vector"])
    rp = N.new("ShaderNodeMapRange"); rp.inputs["From Min"].default_value = 0.50; rp.inputs["From Max"].default_value = 0.64
    Ln.new(nz.outputs["Fac"], rp.inputs["Value"])
    em = N.new("ShaderNodeEmission"); em.inputs["Strength"].default_value = float(os.environ.get("FL_CLOUD_E", "3.2"))
    sh = N.new("ShaderNodeMix"); sh.data_type = "RGBA"; Ln.new(rp.outputs["Result"], sh.inputs["Factor"])
    sh.inputs["A"].default_value = (0.62, 0.70, 0.82, 1); sh.inputs["B"].default_value = (1.0, 1.0, 1.0, 1)
    Ln.new(sh.outputs["Result"], em.inputs["Color"])
    tr = N.new("ShaderNodeBsdfTransparent")
    mx = N.new("ShaderNodeMixShader"); Ln.new(rp.outputs["Result"], mx.inputs[0])
    Ln.new(tr.outputs[0], mx.inputs[1]); Ln.new(em.outputs[0], mx.inputs[2])
    Ln.new(mx.outputs[0], out.inputs["Surface"])
    ob = L.obj_from_bm("FL_Clouds", bm, [m])
    for attr in ("visible_shadow", "visible_diffuse", "visible_glossy", "visible_transmission", "visible_volume_scatter"):
        if hasattr(ob, attr):
            setattr(ob, attr, False)
    return ob

def build_mountains():
    if os.environ.get("FL_MOUNTAINS", "1") == "0":
        return None
    bumps = [(screen2w(u, d), h, r) for u, d, h, r in MOUNTAINS]
    def hgt(x, y):
        z = 0.0
        for p, h, r in bumps:
            q = ((x - p.x) ** 2 + (y - p.y) ** 2) / (r * r)
            if q < 9:
                rdg = 1.0 - abs(noise.noise(Vector((x / 2600, y / 2600, 3.3))))          # ridged: sharper crests
                z = max(z, h * math.exp(-q) * (0.72 + 0.32 * rdg) + 120 * noise.noise(Vector((x / 700, y / 700, 8.1))) * math.exp(-q))
        return z
    bm = bmesh.new()
    na, nr = 200, 110
    rows = []
    for i in range(nr + 1):
        d = 8500 + 17500 * (i / nr) ** 1.2
        row = []
        for j in range(na + 1):
            th = math.radians(-60 + 120 * j / na)
            p = CAM_XY + F * (d * math.cos(th)) + R * (d * math.sin(th))
            z = hgt(p.x, p.y)
            row.append(bm.verts.new((p.x, p.y, max(L.height(p.x, p.y), z) - 6.0)))
        rows.append(row)
    for i in range(nr):
        for j in range(na):
            f = bm.faces.new((rows[i][j], rows[i][j + 1], rows[i + 1][j + 1], rows[i + 1][j])); f.smooth = True
    m = haze_mat("FL_Mountain", (0.03, 0.12, 0.04), (0.10, 0.24, 0.07), haze=(0.16, 0.32, 0.66), dist=20000.0)
    return L.obj_from_bm("FL_Mountains", bm, [m])

# ---------------------------------------------------------------- build
def build(M, year, ctx):
    build_patch(M, ctx["terrain"])
    build_farms(M)
    wall_tower(M)
    wall_seams(M)
    print('[flight] hid', hide_town_north(), 'settlement houses')
    build_mountains()
    build_clouds()
    if not os.environ.get("FL_NOGRASS"):
        build_grass(M, CAM_XY + F * 14, 48.0, float(os.environ.get("FL_GRASS", "160")))
    build_tree_and_kids(M)
    try:
        build_rock()
    except Exception as ex:
        print('[flight] rock failed', ex)
    sc = bpy.context.scene
    sc.render.fps = 30

# ---------------------------------------------------------------- camera flight
def _eye_end():
    return L.height(CAM_XY.x, CAM_XY.y) + EYE

def keys():
    """(frame, loc, look_at, lens) control points.  Built lazily (needs L.height)."""
    ez = _eye_end()
    end = (CAM_XY.x, CAM_XY.y, ez)
    look_end = (*(CAM_XY + F * 400), ez + float(os.environ.get("FL_TILT", "0")))
    return [
        # move A: very high over the north end of the district, glide north over the inner wall
        [(0, (-250, -20, 1560), (15, -470, 0), 26),
         (300, (-470, 660, 760), (10, -420, 0), 30)],
        # move B: swoop down onto the hill, ending on the anime framing
        [(330, (-470, 660, 760), (10, -420, 0), 30),
         (560, (-560, 560, 120), (-300, 40, 30), 40),
         (720, end, look_end, LENS_END)],
    ]

HOLDS = [(300, 330), (720, 99999)]
F_END = 900

def _cr(p0, p1, p2, p3, t):
    t2, t3 = t * t, t * t * t
    return 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3)

def _spline(pts, u):
    """Uniform Catmull-Rom through pts, u in [0, 1] over all segments."""
    pts = [Vector(p) for p in pts]
    n = len(pts) - 1
    ext = [2 * pts[0] - pts[1]] + pts + [2 * pts[-1] - pts[-2]]
    s = min(max(u, 0.0), 1.0) * n
    i = min(int(s), n - 1); t = s - i
    return _cr(ext[i], ext[i + 1], ext[i + 2], ext[i + 3], t)

def _ease(t):
    t = min(max(t, 0.0), 1.0)
    return t * t * t * (t * (t * 6 - 15) + 10)            # smootherstep: slow in, slow out

_TABLES = {}
def _move_table(mi, mv):
    key = (mi, mv[0][0], mv[-1][0])
    """Perceived-distance reparametrisation: speed proportional to height above ground, so the high glide is fast
    and the last metres over the grass are slow."""
    if key in _TABLES:
        return _TABLES[key]
    locs = [k[1] for k in mv]
    us = [i / 400 for i in range(401)]
    acc = [0.0]
    prev = _spline(locs, 0)
    for u in us[1:]:
        p = _spline(locs, u)
        agl = max(1.0, p.z - L.height(p.x, p.y))
        acc.append(acc[-1] + (p - prev).length / (agl + 25.0))
        prev = p
    tot = acc[-1] or 1.0
    _TABLES[key] = (us, [a / tot for a in acc])
    return _TABLES[key]

def _u_of(mi, mv, s):
    us, acc = _move_table(mi, mv)
    lo, hi = 0, len(acc) - 1
    while hi - lo > 1:
        m = (lo + hi) // 2
        if acc[m] < s: lo = m
        else: hi = m
    a0, a1 = acc[lo], acc[hi]
    t = 0 if a1 == a0 else (s - a0) / (a1 - a0)
    return us[lo] + (us[hi] - us[lo]) * t

def flight_at(frame):
    """(loc, look_at, lens) of the opening flight at a flight frame (holds between and after the moves)."""
    return eval_moves(keys(), frame)

def _timed_u(ts, t):
    """Monotone cubic (Fritsch-Carlson) map from key frames ts to spline parameter k/n, zero slope at both ends."""
    n = len(ts) - 1
    us = [k / n for k in range(n + 1)]
    d = [(us[k + 1] - us[k]) / (ts[k + 1] - ts[k]) for k in range(n)]
    m = [0.0] + [0.0 if d[k - 1] * d[k] <= 0 else 2 / (1 / d[k - 1] + 1 / d[k]) for k in range(1, n)] + [0.0]
    k = max(0, min(n - 1, max(i for i in range(n) if ts[i] <= t)))
    h = ts[k + 1] - ts[k]; x = (t - ts[k]) / h
    h00 = 2 * x ** 3 - 3 * x ** 2 + 1; h10 = x ** 3 - 2 * x ** 2 + x; h01 = -2 * x ** 3 + 3 * x ** 2; h11 = x ** 3 - x ** 2
    return h00 * us[k] + h10 * h * m[k] + h01 * us[k + 1] + h11 * h * m[k + 1]

def eval_moves(mvs, frame):
    """Evaluate a list of eased moves at a frame; holds on the last key between moves and after the end."""
    last = mvs[0][0]
    for mi, mv in enumerate(mvs):
        f0, f1 = mv[0][0], mv[-1][0]
        if frame < f0:
            break
        if frame <= f1:
            if len(mv) > 2:                   # waypoints are timed: hit each key at its frame, ease only at the ends
                u = _timed_u([k[0] for k in mv], frame)
            else:                             # single move: ease in/out on the perceived distance
                u = _u_of(mi, mv, _ease((frame - f0) / (f1 - f0)))
            loc = _spline([k[1] for k in mv], u)
            tgt = _spline([k[2] for k in mv], u)
            lens = _spline([(k[3], 0, 0) for k in mv], u).x
            return tuple(loc), tuple(tgt), lens
        last = mv[-1]
    return tuple(last[1]), tuple(last[2]), last[3]

def _set_frame(n):
    try:
        bpy.context.scene.frame_set(int(n))
    except Exception:
        pass

def _cam_cb(n):
    def f():
        _set_frame(n)
        return flight_at(n)
    return f

def build_flight_camera(f0=0, f1=F_END, step=1, name="FlightCam"):
    """Animated camera for an animation render: one key per frame (linear), scene range f0..f1."""
    sc = bpy.context.scene
    cd = bpy.data.cameras.new(name); cd.clip_start = 0.05; cd.clip_end = 30000
    co = bpy.data.objects.new(name, cd); sc.collection.objects.link(co)
    for n in range(f0, f1 + 1, step):
        loc, tgt, lens = flight_at(n)
        co.location = loc
        co.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
        cd.lens = lens
        co.keyframe_insert("location", frame=n); co.keyframe_insert("rotation_euler", frame=n)
        cd.keyframe_insert("lens", frame=n)
    for fc in list(co.animation_data.action.fcurves if hasattr(co.animation_data.action, "fcurves") else []):
        for kp in fc.keyframe_points:
            kp.interpolation = "LINEAR"
    sc.camera = co; sc.frame_start, sc.frame_end = f0, f1; sc.render.fps = 30
    return co

# ---------------------------------------------------------------- set B: chapters 2-9 as one continuous flight
# Global frames of the EP1 video (30 fps). Chapter 2 starts at 0:25 = g750, so opening frame f = g - G0.
# The table matches camera_flight_ep1.md; cameras that frame another plug-in's titan use that plug-in's
# default positions (cast845: Colossal at the outer gate, Armored on the avenue; states845: Yeager house).
G0 = 750
OG = L.OUTER_GATE
YEAGER = (-72.0, -118.0)                       # states845.YEAGER_HOUSE

def setb_moves():
    o = [[(G0 + k[0], k[1], k[2], k[3]) for k in mv] for mv in keys()]     # ch2 opening
    end = o[-1][-1]
    E = (end[1], end[2], end[3])
    def mv(*ks):
        return list(ks)
    return o + [
        # ch3 The Survey Corps Return: rise straight up off the hill, over Wall Maria, to the outer gate from inside
        mv((1650, *E), (1760, (-490, 352, 32), (-290, -30, 26), 42), (1950, (-170, -90, 165), (0, -600, 10), 30),
           (2100, (40, OG[1] + 260, 70), (0, OG[1], 18), 32)),
        # ch3: turn to follow the green-cloak column north up the main avenue
        mv((2100, (40, OG[1] + 260, 70), (0, OG[1], 18), 32), (2400, (-40, -430, 30), (0, -300, 4), 30)),
        # ch4 Father's Promise: drift north-west to the Yeager block (states845 "yeager" framing)
        mv((2400, (-40, -430, 30), (0, -300, 4), 30), (2700, (-20, -70, 38), (YEAGER[0], YEAGER[1], 3), 32)),
        # ch5 Armin by the River: east to the canal, then low and slow south along it in golden light
        mv((2700, (-20, -70, 38), (YEAGER[0], YEAGER[1], 3), 32), (2820, (150, -100, 30), (L.CX, -300, 4), 30),
           (3150, (L.CX - 23, -480, 12), (L.CX, -700, 6), 28)),
        # ch6 The Colossal Titan: rise to the hold looking south over the roofs at the outer wall
        mv((3150, (L.CX - 23, -480, 12), (L.CX, -700, 6), 28), (3450, (60, -330, 38), (0, OG[1] - 20, 62), 28)),
        # ch6: slow push toward the head over the wall (ends near cast845 "colossal_town")
        mv((3450, (60, -330, 38), (0, OG[1] - 20, 62), 28), (4050, (32, OG[1] + 195, 25), (-6, OG[1] - 15, 49), 45)),
        # ch6: the kick - ease back and up to the breach view while the blocks fly (states845 "breach_inside")
        mv((4050, (32, OG[1] + 195, 25), (-6, OG[1] - 15, 49), 45), (4500, (46, OG[1] + 270, 80), (-2, OG[1] + 10, 6), 30)),
        # ch7 Mother: push north-west to the crushed Yeager house; the Smiling Titan walks in
        mv((4500, (46, OG[1] + 270, 80), (-2, OG[1] + 10, 6), 30), (4950, (-20, -70, 38), (YEAGER[0], YEAGER[1], 3), 32)),
        # ch8 The Armored Titan: swing over the roofs onto the Armored charging up the avenue (cast845 "armored_gate")
        mv((5400, (-20, -70, 38), (YEAGER[0], YEAGER[1], 3), 32), (5700, (62, -385, 26), (-6, -505, 9), 30)),
        # ch8: follow it north to the gate, climb over Wall Maria and look back as the gate bursts (states845 "inner_burst")
        mv((5700, (62, -385, 26), (-6, -505, 9), 30), (6000, (62, -120, 30), (0, -40, 15), 30),
           (6150, (60, 60, 95), (0, -20, 22), 30), (6300, (52, 215, 26), (-2, 0, 15), 30)),
        # ch9 Wall Maria Is Lost: night pull-up over the burning town, then north along the river toward Wall Rose
        mv((6300, (52, 215, 26), (-2, 0, 15), 30), (6750, (-470, 330, 330), (40, -360, 0), 27),
           (7200, (230, 1400, 2200), (L.CX, 6000, 0), 26)),
    ]

SETB_END = 7200

def setb_at(g):
    """(loc, look_at, lens) of the set-B flight at global frame g."""
    return eval_moves(setb_moves(), g)

def state_at(g):
    """Plug-in state for global frame g (env values for cast845 / states845, the chapter, the time of day)."""
    st = {"AOT_STATE": "intact", "AOT_EVENT": "intact", "AOT_ARC_T": None, "chapter": 2, "light": "morning"}
    for g0, ch, light in ((750, 2, "morning"), (1650, 3, "morning"), (2400, 4, "midday"), (2700, 5, "late afternoon"),
                          (3150, 6, "golden hour"), (4500, 7, "late afternoon"), (5400, 8, "dusk"), (6300, 9, "night")):
        if g >= g0:
            st["chapter"], st["light"] = ch, light
    if g >= 3450:
        st["AOT_EVENT"] = "colossal"
    if g >= 4080:
        st["AOT_STATE"] = "kicked"
        st["AOT_ARC_T"] = round(min(1.0, (g - 4080) / 90.0), 3)          # blocks in the air for 3 s
    if g >= 4290:
        st["AOT_EVENT"] = "armored"                                      # Colossal gone, titans pour in
    if g >= 6060:
        st["AOT_STATE"] = "armored"                                      # inner gate burst
    if g >= 6300:
        st["AOT_STATE"] = "night"
    return st

def _g_cb(g):
    def f():
        _set_frame(g - G0)                 # kids / opening animation are keyed in flight frames
        return setb_at(g)
    return f

def build_setb_camera(g0=G0, g1=SETB_END, step=1, name="EP1Cam"):
    """Animated camera for the whole of set B (global frames; the scene frame range is set to g0..g1)."""
    sc = bpy.context.scene
    cd = bpy.data.cameras.new(name); cd.clip_start = 0.05; cd.clip_end = 30000
    co = bpy.data.objects.new(name, cd); sc.collection.objects.link(co)
    for n in range(g0, g1 + 1, step):
        loc, tgt, lens = setb_at(n)
        co.location = loc
        co.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
        cd.lens = lens
        co.keyframe_insert("location", frame=n); co.keyframe_insert("rotation_euler", frame=n)
        cd.keyframe_insert("lens", frame=n)
    sc.camera = co; sc.frame_start, sc.frame_end = g0, g1; sc.render.fps = 30
    return co

CAMS = {f"flight_f{n:04d}": _cam_cb(n) for n in range(0, F_END + 1)}
CAMS["flight_end"] = _cam_cb(F_END)
CAMS.update({f"ep1_g{g:05d}": _g_cb(g) for g in range(G0, SETB_END + 1)})

LABELS = {"THE HILL": (TREE.x, TREE.y, None)}
