"""EP1 WORLD MAP LAYER (agent G): the three walls with their district bulges, the river, fields and forests, the sea on
the far southern horizon.  Opt-in, cheap, low-poly; the same world in every scene so a camera can fly physically from
Shiganshina to Trost and frames match across scenes at the seams (ref/user/walls_map_ref.png, HANDOFF 09:37).

USE
  as a scene.py plug-in:   AOT_PLUGINS=...,world   (with or without AOT_SET=trost)   -> build() runs attach()
  as a library (scenes that build their own terrain, e.g. render_interlude.py):
        import world as WD
        WD.attach("trost", M=None, terrain=my_terrain_obj, cores=[((x, y), r_out), ...])   # after the scene is built
        h = WD.fade(x, y, h, "trost", cores)        # use in the scene's own height() so local terrain meets the world at 0
  helpers: to_set(p_world, frame), to_world(p_set, frame), MITRAS, R_MARIA / R_ROSE / R_SINA, SEAM keys in master_timeline.py

SCALE (documented factor): WORLD_K = 0.05 (env WORLD_K).  Canon radii x 0.05: Wall Maria 24.0 km, Rose 19.0 km,
Sina 12.5 km (canon 480 / 380 / 250 km).  Buildings, walls (50 m), people and titans stay TRUE scale; only the distances
between the rings are compressed, so Shiganshina -> Trost is 5.0 km (a ~10-15 s flight at a calm sky height) instead
of 100 km, the whole map fits inside a 60 km camera clip, and the rings read on a single high aerial.
The districts keep the size of the existing sets (Shiganshina W 290 / S 430, Trost W 620 / S 250).

COORDINATES: WORLD = the Shiganshina frame (scene.py: Wall Maria along y = 0 at x = 0, Shiganshina bulges south,
outer gate (0, -720)).  Mitras is at (0, R_MARIA).  The Trost frame (trost.py: Wall Rose along y = 0, outer gate
(0, -870)) sits at world (0, R_MARIA - R_ROSE) = (0, 5000): p_world = p_trost + (0, 5000).
Every world object hangs under one root empty placed at -SET_ORIGIN[frame], so the geometry is bit-identical in all
scenes; textures use the root's object space (= world coordinates).

WHAT attach() DOES in a scene whose active set is `frame` ("shig" | "trost"):
  * the set keeps its own terrain only inside its CORE circle (faces outside are deleted, heights fade to 0 at the
    edge via height_patch); outside the cores everything is world ground (flat z = 0, quilted fields, forest clumps)
  * scene.py's far mountain ranges and flight.py's MOUNTAINS are off (FL_MOUNTAINS=0); nothing rises behind the
    Colossal; the sea lies ~6 km south of Shiganshina's outer gate
  * the set's long straight walls are cut at |x| = JOIN and the world ring continues from there, blending from the
    set's exaggerated bend into the true circle
  * the other set's district (Trost in Shiganshina scenes and vice versa) is a proxy: its wall bulge plus a roof-coloured
    "town carpet" (it only appears far away; seams are placed where neither town is in frame)
  * the 10 empty districts are plain wall bulges (no buildings)
"""
import bpy, bmesh, math, os, random, sys
from mathutils import Vector, noise

K = float(os.environ.get("WORLD_K", "0.05"))
R_MARIA, R_ROSE, R_SINA = 480000.0 * K, 380000.0 * K, 250000.0 * K
MITRAS = (0.0, R_MARIA)
SET_ORIGIN = {"shig": (0.0, 0.0), "trost": (0.0, R_MARIA - R_ROSE)}          # set frame origin in world coordinates
# core circles in each set's own frame: (centre, r_out); local terrain fades to 0 between 0.8 r_out and r_out
CORES = {"shig": [((0.0, -150.0), 1650.0)], "trost": [((0.0, -435.0), 950.0)]}
SET_RING = {"shig": ("maria", 480000.0 / 30, 1300.0), "trost": ("rose", 380000.0 / 30, 1000.0)}   # ring, set bend r, JOIN
DISTRICT = {"maria": (290.0, 430.0, 290.0), "rose": (620.0, 250.0, 620.0), "sina": (420.0, 300.0, 420.0)}  # W, S, R
SEA_Y = -720.0 - 6000.0           # coastline (world y): a band on the southern horizon behind the Colossal
WALL_H, WALL_T = 50.0, 10.0
REPLACES = set()
STATE = {}

if os.environ.get("WORLD_FL_MOUNTAINS", "0") != "1":
    os.environ["FL_MOUNTAINS"] = "0"              # flight.py reads it at build time: no ranges behind the Colossal

def active_frame():
    f = os.environ.get("AOT_WORLD_FRAME")
    if f:
        return f
    return "trost" if os.environ.get("AOT_SET") == "trost" else "shig"

def to_set(p, frame):
    o = SET_ORIGIN[frame]; return (p[0] - o[0], p[1] - o[1]) + tuple(p[2:])

def to_world(p, frame):
    o = SET_ORIGIN[frame]; return (p[0] + o[0], p[1] + o[1]) + tuple(p[2:])

def _smooth(a, b, x):
    u = min(1.0, max(0.0, (x - a) / (b - a))); return u * u * (3 - 2 * u)

def core_w(x, y, cores):
    """1 inside a core (local terrain), 0 outside (world ground)."""
    w = 0.0
    for (cx, cy), r in cores:
        w = max(w, 1.0 - _smooth(0.8 * r, r, math.hypot(x - cx, y - cy)))
    return w

def fade(x, y, h, frame=None, cores=None):
    return h * core_w(x, y, cores if cores is not None else CORES[frame or active_frame()])

def height_patch(x, y, h):                        # scene.py plug-in hook (coordinates in the active set's frame)
    return fade(x, y, h)

def world_height(x, y):
    return 0.0

# ---------------------------------------------------------------- geometry helpers
def _mat(name, col, rough=0.9):
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]; b.inputs["Base Color"].default_value = (*col, 1); b.inputs["Roughness"].default_value = rough
    return m

def ground_mat():
    """Quilted fields + meadow + darker woodland patches, in root object space (= world metres)."""
    m = bpy.data.materials.new("WD_Ground"); m.use_nodes = True
    nt = m.node_tree; N = nt.nodes; Ln = nt.links
    b = N["Principled BSDF"]; b.inputs["Roughness"].default_value = 0.95
    tc = N.new("ShaderNodeTexCoord")
    # fields: voronoi cells ~260 m, each a random tint between meadow, young crop and ripe yellow
    vo = N.new("ShaderNodeTexVoronoi"); vo.inputs["Scale"].default_value = 1 / 260.0
    Ln.new(tc.outputs["Object"], vo.inputs["Vector"])
    cr = N.new("ShaderNodeValToRGB"); e = cr.color_ramp.elements
    e[0].color = (0.13, 0.26, 0.05, 1); e[1].position = 1.0; e[1].color = (0.55, 0.47, 0.18, 1)
    el = e.new(0.35); el.color = (0.24, 0.36, 0.08, 1)
    el = e.new(0.6); el.color = (0.36, 0.42, 0.12, 1)
    el = e.new(0.82); el.color = (0.45, 0.36, 0.16, 1)
    Ln.new(vo.outputs["Color"], cr.inputs["Fac"]) if "Color" in vo.outputs else None
    sep = N.new("ShaderNodeSeparateColor"); Ln.new(vo.outputs["Color"], sep.inputs[0]); Ln.new(sep.outputs[0], cr.inputs["Fac"])
    # meadow mask: big soft noise; fields only where it is high (patchwork among pasture)
    n1 = N.new("ShaderNodeTexNoise"); n1.inputs["Scale"].default_value = 1 / 4200.0; n1.inputs["Detail"].default_value = 4
    Ln.new(tc.outputs["Object"], n1.inputs["Vector"])
    mk = N.new("ShaderNodeMapRange"); mk.inputs["From Min"].default_value = 0.44; mk.inputs["From Max"].default_value = 0.50
    Ln.new(n1.outputs["Fac"], mk.inputs["Value"])
    mx = N.new("ShaderNodeMix"); mx.data_type = "RGBA"
    mx.inputs["A"].default_value = (0.20, 0.33, 0.08, 1)
    Ln.new(mk.outputs["Result"], mx.inputs["Factor"]); Ln.new(cr.outputs["Color"], mx.inputs["B"])
    # woodland tint (under the forest clumps and beyond): darker green patches
    n2 = N.new("ShaderNodeTexNoise"); n2.inputs["Scale"].default_value = 1 / 1500.0; n2.inputs["Detail"].default_value = 6
    Ln.new(tc.outputs["Object"], n2.inputs["Vector"])
    wk = N.new("ShaderNodeMapRange"); wk.inputs["From Min"].default_value = 0.66; wk.inputs["From Max"].default_value = 0.70
    Ln.new(n2.outputs["Fac"], wk.inputs["Value"])
    mw = N.new("ShaderNodeMix"); mw.data_type = "RGBA"; mw.inputs["B"].default_value = (0.05, 0.13, 0.04, 1)
    Ln.new(wk.outputs["Result"], mw.inputs["Factor"]); Ln.new(mx.outputs["Result"], mw.inputs["A"])
    # fine grain
    n3 = N.new("ShaderNodeTexNoise"); n3.inputs["Scale"].default_value = 1 / 18.0
    Ln.new(tc.outputs["Object"], n3.inputs["Vector"])
    bc = N.new("ShaderNodeBrightContrast"); Ln.new(mw.outputs["Result"], bc.inputs["Color"])
    mr = N.new("ShaderNodeMapRange"); mr.inputs["To Min"].default_value = -0.05; mr.inputs["To Max"].default_value = 0.05
    Ln.new(n3.outputs["Fac"], mr.inputs["Value"]); Ln.new(mr.outputs["Result"], bc.inputs["Bright"])
    # hedgerows: dark lines on the field cell edges (only where the quilt is)
    ve = N.new("ShaderNodeTexVoronoi"); ve.feature = "DISTANCE_TO_EDGE"; ve.inputs["Scale"].default_value = 1 / 260.0
    Ln.new(tc.outputs["Object"], ve.inputs["Vector"])
    he = N.new("ShaderNodeMapRange"); he.inputs["From Min"].default_value = 0.02; he.inputs["From Max"].default_value = 0.035
    he.inputs["To Min"].default_value = 1.0; he.inputs["To Max"].default_value = 0.0
    Ln.new(ve.outputs["Distance"], he.inputs["Value"])
    hm = N.new("ShaderNodeMath"); hm.operation = "MULTIPLY"; Ln.new(he.outputs["Result"], hm.inputs[0]); Ln.new(mk.outputs["Result"], hm.inputs[1])
    mh = N.new("ShaderNodeMix"); mh.data_type = "RGBA"; mh.inputs["B"].default_value = (0.06, 0.12, 0.04, 1)
    Ln.new(hm.outputs["Value"], mh.inputs["Factor"]); Ln.new(bc.outputs["Color"], mh.inputs["A"])
    Ln.new(mh.outputs["Result"], b.inputs["Base Color"])
    STATE["woods_noise"] = (1 / 1500.0, 0.6)
    return m

def _strip(bm, pts, width, z):
    """Flat ribbon along a polyline (river / road)."""
    left, right = [], []
    for i, p in enumerate(pts):
        a, c = pts[max(0, i - 1)], pts[min(len(pts) - 1, i + 1)]
        d = Vector((c[0] - a[0], c[1] - a[1])).normalized(); n = Vector((-d.y, d.x)) * width / 2
        left.append(bm.verts.new((p[0] + n.x, p[1] + n.y, z))); right.append(bm.verts.new((p[0] - n.x, p[1] - n.y, z)))
    for i in range(len(pts) - 1):
        bm.faces.new((left[i], right[i], right[i + 1], left[i + 1]))

def _dense(ctrl, step):
    """Catmull-Rom through control points, resampled every ~step metres."""
    out = []
    P = [ctrl[0]] + list(ctrl) + [ctrl[-1]]
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        n = max(1, int(math.hypot(p2[0] - p1[0], p2[1] - p1[1]) / step))
        for k in range(n):
            u = k / n
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * u + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * u * u
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * u ** 3) for j in range(2)))
    out.append(tuple(ctrl[-1]))
    return out

def _wall(bm, pts, closed=False):
    """Low-poly tapered wall along a polyline: 4 verts per point (base 10 m, top 7.6 m, 50 m high)."""
    prof = [(-WALL_T / 2, -3.0), (WALL_T / 2, -3.0), (WALL_T / 2 - 1.2, WALL_H), (-WALL_T / 2 + 1.2, WALL_H)]
    n = len(pts); rings = []
    for i, p in enumerate(pts):
        a, c = pts[(i - 1) % n if closed else max(0, i - 1)], pts[(i + 1) % n if closed else min(n - 1, i + 1)]
        d = Vector((c[0] - a[0], c[1] - a[1])).normalized(); nn = Vector((-d.y, d.x))
        rings.append([bm.verts.new((p[0] + nn.x * u, p[1] + nn.y * u, z)) for u, z in prof])
    for i in range(n - 1 + (1 if closed else 0)):
        r0, r1 = rings[i], rings[(i + 1) % n]
        for k in range(4):
            bm.faces.new((r0[k], r0[(k + 1) % 4], r1[(k + 1) % 4], r1[k]))

def _district(cx, cy, ang, W, S, R, step=40.0):
    """District outline (open polyline from the ring out and back), like scene.district_outline, rotated so the bulge
    points along ang (radians, outward), placed with its wall-line centre at (cx, cy)."""
    loc = [(-W, 0.0), (-W, -S)]
    n = max(8, int(math.pi * R / step))
    for s in range(1, n):
        a = math.pi + s / n * math.pi
        loc.append((math.cos(a) * R, -S + math.sin(a) * R))
    loc += [(W, -S), (W, 0.0)]
    # local -y = outward: point = centre + x * along + (-y) * out
    ux, uy = math.cos(ang), math.sin(ang)
    tx, ty = math.cos(ang + math.pi / 2), math.sin(ang + math.pi / 2)
    return [(cx + x * tx - y * ux, cy + x * ty - y * uy) for x, y in loc]

def ring_points(r, frame, ring_name, step=120.0):
    """[(polyline, kind)] for one ring in WORLD coordinates: arcs between the four districts, and the districts.
    The active set's ring near its district is left to the set (|x_set| < JOIN) and the arc blends from the set's
    exaggerated bend into the true circle over JOIN .. JOIN + 3500 m."""
    W, S, R = DISTRICT[ring_name]
    my = SET_RING.get(frame)
    out = []
    dirs = [-math.pi / 2, 0.0, math.pi / 2, math.pi]             # S, E, N, W (outward angles); centre = Mitras
    half = math.asin(min(0.99, W / r))                           # angular half width of a district on the ring
    for k in range(4):
        a0 = dirs[k] + half; a1 = dirs[(k + 1) % 4] - half + (math.tau if k == 3 else 0)
        n = max(4, int(r * (a1 - a0) / step))
        pts = [(MITRAS[0] + r * math.cos(a0 + (a1 - a0) * i / n), MITRAS[1] + r * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]
        out.append((pts, "arc"))
    for k, a in enumerate(dirs):
        cx, cy = MITRAS[0] + r * math.cos(a), MITRAS[1] + r * math.sin(a)
        out.append((_district(cx, cy, a, W, S, R), ("district", ring_name, k)))
    if my and my[0] == ring_name:                                # the active set owns its district + the near wall
        rb, join = my[1], my[2]
        o = SET_ORIGIN[frame]
        res = []
        for pts, kind in out:
            if kind != "arc":
                if kind[2] == 0:                                 # the set's own (south) district: built by the set
                    continue
                res.append((pts, kind)); continue
            seg, cur = [], []
            for (x, y) in pts:
                xs = x - o[0]
                if abs(xs) < join and y - o[1] > -3000:           # inside the set's own wall stretch
                    if len(cur) > 1:
                        seg.append(cur)
                    cur = []; continue
                w = _smooth(join, join + 3500.0, abs(xs)) if y - o[1] > -3000 else 1.0
                ys = o[1] - (xs * xs - W * W) / (2 * rb) if abs(xs) <= join + 3500 else y
                if abs(xs) <= W + 1:
                    ys = o[1]
                cur.append((x, y * w + ys * (1 - w)))
            if len(cur) > 1:
                seg.append(cur)
            # make the cut ends start exactly at the set's wall (x = +-join on the set's parabola)
            for s_ in seg:
                for end in (0, -1):
                    xs = s_[end][0] - o[0]
                    if abs(abs(xs) - join) < step * 1.5:
                        sx = math.copysign(join, xs)
                        s_.insert(0 if end == 0 else len(s_), (o[0] + sx, o[1] - sx * sx / (2 * rb) + (W * W) / (2 * rb)))
                res.append((s_, "arc"))
        out = res
    return out

# ---------------------------------------------------------------- build
def _trim_set(frame, terrain, cores):
    """Delete local terrain outside the cores; cut the set's long walls at JOIN; drop far props of the set."""
    if terrain is not None and terrain.type == "MESH":
        bm = bmesh.new(); bm.from_mesh(terrain.data)
        rad = [(Vector(c), r + 150.0) for c, r in cores]
        kill = [f for f in bm.faces if not any((f.calc_center_median().to_2d() - c).length < r for c, r in rad)]
        bmesh.ops.delete(bm, geom=kill, context="FACES"); bm.to_mesh(terrain.data); bm.free()
    ring, rb, join = SET_RING[frame]
    names = {"shig": ("WallMaria", "ButtressMaria", "WallTopMaria"), "trost": ("WallRose", "ButtressRose", "WallTopRose")}[frame]
    for nm in names:
        ob = bpy.data.objects.get(nm)
        if ob and ob.type == "MESH":
            bm = bmesh.new(); bm.from_mesh(ob.data)
            bmesh.ops.delete(bm, geom=[v for v in bm.verts if abs(v.co.x) > join + 0.5], context="VERTS")
            bm.to_mesh(ob.data); bm.free()
    for ob in list(bpy.data.objects):             # the set's canal / roads beyond the core: the world's river / road take over
        if ob.type == "MESH" and ob.name.startswith(("Canal", "Road", "River")) and ob.data.users == 1:
            mw = ob.matrix_world
            bm = bmesh.new(); bm.from_mesh(ob.data)
            kill = [v for v in bm.verts if core_w(*(mw @ v.co).to_2d(), [(c, 0.78 * r) for c, r in cores]) <= 0]
            if kill:
                bmesh.ops.delete(bm, geom=kill, context="VERTS"); bm.to_mesh(ob.data)
            bm.free()
    for ob in list(bpy.data.objects):             # far props of the set (wall guns, the giant forest, far farms)
        if ob.parent is None and ob.type in ("MESH", "EMPTY") and ob.name.startswith(("CannonM", "GT", "FL_Mount")):
            p = ob.matrix_world.translation
            if core_w(p.x, p.y, [(c, r + 300) for c, r in cores]) <= 0:
                bpy.data.objects.remove(ob, do_unlink=True)

def attach(frame=None, M=None, terrain=None, cores=None, trim=True):
    """Add the world layer to the current scene, in the frame of its active set."""
    frame = frame or active_frame()
    cores = cores if cores is not None else CORES[frame]
    STATE.update(frame=frame, cores=cores)
    sc = bpy.context.scene
    if trim:
        _trim_set(frame, terrain if terrain is not None else bpy.data.objects.get("Terrain"), cores)
    coll = bpy.data.collections.new("World"); sc.collection.children.link(coll)
    root = bpy.data.objects.new("WorldRoot", None); coll.objects.link(root)
    o = SET_ORIGIN[frame]; root.location = (-o[0], -o[1], 0.0)
    stone = (M or {}).get("stone") or _mat("WD_Stone", (0.55, 0.52, 0.46), 0.85)
    water = (M or {}).get("water") or _mat("WD_Water", (0.10, 0.17, 0.22), 0.06)
    def put(name, bm, mats):
        me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
        for m_ in mats:
            me.materials.append(m_)
        ob = bpy.data.objects.new(name, me); coll.objects.link(ob); ob.parent = root
        return ob
    # set cores in world coordinates (both sets, so neither scene grows the other's ground into its own town)
    allc = [((c[0] + SET_ORIGIN[f][0], c[1] + SET_ORIGIN[f][1]), r) for f in CORES for c, r in CORES[f]]
    mycores = [((c[0] + o[0], c[1] + o[1]), r) for c, r in cores]
    # ---- ground: 1.2 km cells; cells wholly inside this scene's cores are left to the local terrain
    gm = ground_mat()
    bm = bmesh.new()
    x0, x1 = -R_MARIA - 60000.0, R_MARIA + 60000.0
    y0, y1 = SEA_Y - 600.0, MITRAS[1] + R_MARIA + 70000.0
    cell = 1500.0
    nx, ny = int((x1 - x0) / cell), int((y1 - y0) / cell)
    V = {}
    def vert(i, j):
        if (i, j) not in V:
            V[(i, j)] = bm.verts.new((x0 + i * cell, y0 + j * cell, -0.4))
        return V[(i, j)]
    for i in range(nx):
        for j in range(ny):
            cx_, cy_ = x0 + (i + 0.5) * cell, y0 + (j + 0.5) * cell
            if any(math.hypot(cx_ - c[0], cy_ - c[1]) + cell * 0.71 < 0.8 * r for c, r in mycores):
                continue
            bm.faces.new((vert(i, j), vert(i + 1, j), vert(i + 1, j + 1), vert(i, j + 1)))
    put("WD_Ground", bm, [gm])
    # ---- the sea: from a wavy coastline south to the clip distance
    bm = bmesh.new()
    xs = [x0 - 20000 + k * 600.0 for k in range(int((x1 - x0 + 40000) / 600) + 1)]
    coast = [bm.verts.new((x, SEA_Y + 380 * noise.noise(Vector((x / 5200, 0.3, 1.1))) + 160 * noise.noise(Vector((x / 900, 2.1, 0.4))), -0.05)) for x in xs]
    coast_xy = [(v.co.x, v.co.y) for v in coast]
    far = [bm.verts.new((x, SEA_Y - 120000, -0.05)) for x in xs]
    for k in range(len(xs) - 1):
        bm.faces.new((far[k], far[k + 1], coast[k + 1], coast[k]))
    sea = _mat("WD_Sea", (0.05, 0.16, 0.26), 0.12)
    put("WD_Sea", bm, [sea])
    bm = bmesh.new()                              # a pale beach strip along the coast
    _strip(bm, [(x, y + 70) for x, y in coast_xy], 140.0, -0.2)
    put("WD_Beach", bm, [_mat("WD_Sand", (0.55, 0.50, 0.36), 0.95)])
    # ---- the three walls with their districts
    bm = bmesh.new(); ba = bmesh.new(); bd = bmesh.new()
    carpets = []
    for ring_name, r in (("maria", R_MARIA), ("rose", R_ROSE), ("sina", R_SINA)):
        for pts, kind in ring_points(r, frame, ring_name):
            if len(pts) > 1:
                _wall(bm, pts)
                # cleared apron along the wall foot (a pale band that keeps the rings readable from the high aerials);
                # left out within 2.5 km of either town (it would look like a road from low sky heights there)
                run = []
                for p in pts + [None]:
                    if p is not None and not any(math.hypot(p[0] - c[0], p[1] - c[1]) < rr + 2500.0 for c, rr in allc):
                        run.append(p); continue
                    if len(run) > 1:
                        _strip(ba, run, 180.0, -0.25)
                    run = []
            if kind != "arc":
                if (ring_name in ("maria", "rose")) and kind[2] == 0:
                    carpets.append((ring_name, pts))
                elif not any(math.hypot(pts[len(pts) // 2][0] - c[0], pts[len(pts) // 2][1] - c[1]) < 1.2 * rr for c, rr in mycores):
                    bd.faces.new([bd.verts.new((x, y, -0.2)) for x, y in pts])      # empty district: a bare yard
    put("WD_Walls", bm, [stone])
    put("WD_WallApron", ba, [_mat("WD_Apron", (0.36, 0.38, 0.24), 0.95)])
    put("WD_DistrictYards", bd, [_mat("WD_Yard", (0.33, 0.30, 0.22), 0.95)])
    # ---- proxy town carpet for the OTHER set's district (it is only ever seen from far away)
    other = {"shig": "rose", "trost": "maria"}[frame]
    for ring_name, pts in carpets:
        if ring_name != other:
            continue
        bm = bmesh.new()
        vs = [bm.verts.new((x, y, 0.3)) for x, y in pts]
        bm.faces.new(vs)
        put("WD_TownProxy_" + ring_name, bm, [_mat("WD_Roofs", (0.30, 0.12, 0.06), 0.9)])
    # ---- the river N-S through all three rings, and the main road (sets keep their own canal / streets in their cores)
    ty = SET_ORIGIN["trost"][1]
    river = _dense([(260.0, SEA_Y - 300), (420.0, SEA_Y + 3000), (120.0, -6000), (300.0, -2400), (228.0, -609), (228.0, 0),
                    (224.0, 1300), (420.0, 2500), (300.0, 3500), (556.0, ty - 525), (556.0, ty), (560.0, ty + 1400),
                    (300.0, ty + 3500), (60.0, MITRAS[1] - R_SINA - 1200), (0.0, MITRAS[1] - R_SINA), (0.0, MITRAS[1]),
                    (0.0, MITRAS[1] + R_SINA), (-200.0, MITRAS[1] + R_ROSE), (0.0, MITRAS[1] + R_MARIA), (150.0, MITRAS[1] + R_MARIA + 30000)], 90.0)
    road = _dense([(0.0, SEA_Y + 2500), (-300.0, -5000), (0.0, -720), (0.0, 0), (-60.0, 1400), (-260.0, 2600), (-60.0, 3600),
                   (0.0, ty - 870), (-140.0, ty), (-200.0, ty + 1600), (0.0, MITRAS[1] - R_SINA - 300), (0.0, MITRAS[1] - R_SINA)], 80.0)
    def keep(pl, rf):
        segs, cur = [], []
        for p in pl:
            if any(math.hypot(p[0] - c[0], p[1] - c[1]) < rf * r for c, r in mycores):
                if len(cur) > 1:
                    segs.append(cur)
                cur = []
            else:
                cur.append(p)
        if len(cur) > 1:
            segs.append(cur)
        return segs
    bm = bmesh.new()
    for s_ in keep(river, 0.75):
        _strip(bm, s_, 26.0, 0.05)
    put("WD_River", bm, [water])
    bm = bmesh.new()
    for s_ in keep(road, 0.75):
        _strip(bm, s_, 9.0, 0.02)
    put("WD_Road", bm, [(M or {}).get("dirt") or _mat("WD_Dirt", (0.24, 0.20, 0.13), 0.95)])
    STATE["river"], STATE["road"] = river, road
    # ---- forest clumps: low-poly cones (6 sides), deterministic in world coordinates
    rnd = random.Random(1845)
    bm = bmesh.new()
    leaf = _mat("WD_Pine", (0.04, 0.12, 0.04), 0.85)
    ringsr = (R_MARIA, R_ROSE, R_SINA)
    def bad(x, y):
        if y < SEA_Y + 900:
            return True
        d = math.hypot(x - MITRAS[0], y - MITRAS[1])
        if d > R_MARIA + 9000 or any(abs(d - r) < 90 for r in ringsr):
            return True
        if any(math.hypot(x - c[0], y - c[1]) < r + 120 for c, r in allc):
            return True
        return False
    n_cl = int(os.environ.get("WORLD_CLUMPS", "420"))
    for c in range(n_cl):
        a = rnd.uniform(0, math.tau); rr = math.sqrt(rnd.random()) * (R_MARIA + 7000)
        cx_, cy_ = MITRAS[0] + math.cos(a) * rr, MITRAS[1] + math.sin(a) * rr
        if bad(cx_, cy_):
            continue
        size = rnd.uniform(120, 520); nt_ = int(size * size / 900)
        for t in range(min(nt_, 260)):
            x = cx_ + rnd.gauss(0, size * 0.5); y = cy_ + rnd.gauss(0, size * 0.35)
            if bad(x, y):
                continue
            h = rnd.uniform(14, 26); rad = h * 0.3
            base = [bm.verts.new((x + rad * math.cos(k * math.tau / 6), y + rad * math.sin(k * math.tau / 6), h * 0.15)) for k in range(6)]
            top = bm.verts.new((x, y, h))
            for k in range(6):
                bm.faces.new((base[k], base[(k + 1) % 6], top))
    put("WD_Forest", bm, [leaf])
    # camera clip: the sea and the far rings must stay inside it
    for ob in sc.objects:
        if ob.type == "CAMERA":
            ob.data.clip_end = max(ob.data.clip_end, float(os.environ.get("WORLD_CLIP", "60000")))
    print(f"[world] frame {frame}, K {K}: Maria {R_MARIA / 1000:.1f} km, Rose {R_ROSE / 1000:.1f}, Sina {R_SINA / 1000:.1f}; "
          f"Trost frame at world y {SET_ORIGIN['trost'][1]:.0f}; cores {cores}", flush=True)
    return root

def build(M, year, ctx=None):                     # scene.py plug-in hook (runs after the base scene / set is built)
    if STATE.get("root"):                         # trost.build_set may call plug-in builds itself: attach only once
        return
    terrain = (ctx or {}).get("terrain") if isinstance(ctx, dict) else None
    STATE["root"] = attach(active_frame(), M=M, terrain=terrain)
