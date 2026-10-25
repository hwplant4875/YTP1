"""INTERLUDE 846-850 (agent B): one-take flight from the Maria plains north over Trost and Wall Rose to the refugee
camps (846: fields cleared, storehouses, seasons to spring 847), then on to the 104th Training Corps camp (847: ~200
enlist; Eren hangs upside down on the balance rig; three years of seasons; 850 graduation night with torches).
Timeline and beats: seq_interlude.py (pure Python, shared with the HUD).  The 846 march is its own segment.

Run (see render_interlude.sh):
    blender -b -P aot/render_interlude.py -- --out DIR [--t0 0 --t1 20.5 --fps 15] [--times 3,11,19] [--samples 2]
It imports scene.py as a LIBRARY (aotlib) without building Shiganshina, and trost.py for the Trost bulge + Wall Rose
(trost.build_walls + its house layout; INT_TROST=0 falls back to a plain Wall Rose with one gate).  The world is
built once, then every frame is a pure function of t (camera, seasons, night, tents, trees, figures, cadets).
Per frame it writes hudcam camera dumps (+ Eren / Mikasa / Armin tracker positions) for agent E's hud2.py.

World (metres, Trost frame): Wall Rose along y = 0 (inside = +y), Trost bulges south to its outer gate (0, -870),
Trost's inner gate at X0 = -140.  Camps fill x = X0 +- 700, y = 40..760 behind the inner gate; the cleared forest /
fields are at y = 820..1700; the training camp is centred on CAMP.
SEGMENT CAMERA KEYS for the integration pass: cam_keys()[0] (start, low over the plains south of Trost looking north)
and cam_keys()[-1] (end, low oblique on the graduation rows).
"""
import bpy, bmesh, math, os, random, sys, time, json, argparse
from mathutils import Vector, Matrix, Euler, noise
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ap = argparse.ArgumentParser()
ap.add_argument("--out", required=True)
ap.add_argument("--t0", type=float, default=0.0)
ap.add_argument("--t1", type=float, default=20.5)
ap.add_argument("--fps", type=float, default=15.0)
ap.add_argument("--samples", type=int, default=2)
ap.add_argument("--res", default="854x480")
ap.add_argument("--engine", default="CYCLES")
ap.add_argument("--times", default="")
ap.add_argument("--prefix", default="int")
ap.add_argument("--dry", action="store_true", help="build + per-frame updates only, no rendering (CPU check)")
B, _ = ap.parse_known_args(argv)

sys.path.insert(0, os.path.dirname(HERE))   # repo root: hudcam (agent E's per-frame camera dump for hud2.py)
import hudcam
import scene as L            # library only: its __main__ block does not run under this name (registers 'aotlib')
import seq_interlude as SI
TR = None
if os.environ.get("INT_TROST", "1") == "1":
    try:
        import trost as TR   # rebinds aotlib's district globals to Trost (W, S, R, OUTER_GATE, district_outline ...)
    except Exception as ex:
        print("[int] trost.py unavailable, plain Wall Rose:", ex)
        TR = None

X0 = TR.INNER_GATE[0] if TR else -140.0
TW, TS, TRR = (TR.W, TR.S, TR.R) if TR else (620.0, 250.0, 620.0)
OUTER = TR.OUTER_GATE if TR else (0.0, -870.0)
PSCALE = float(os.environ.get("INT_PSCALE", "1.0"))     # user rule: every human at TRUE scale
import master_timeline as MT   # agent G: seams S3 / S7 / S8 and the camp position (pure Python)
import world as WD             # agent G: the shared world layer (walls, river, fields, sea); same in every scene
CAMP = Vector(MT.TRAINING_CAMP_TROST)                    # (-1450, 650) Trost frame: beside Trost, inside Wall Rose
RIG0 = Vector((CAMP.x - 74.0, CAMP.y - 22.0))            # first balance rig; rigs run north in 9 m steps
ERIG = 2                                                 # Eren's rig index
# local terrain only inside these cores (Trost frame); world ground everywhere else (world.fade / world.attach)
CORES = [((0.0, -435.0), 950.0), ((-140.0, 400.0), 750.0), ((CAMP.x, CAMP.y), 450.0)]
FOG_D = float(os.environ.get("INT_FOG", "22000"))     # light distance haze only (QA: no grey-blue wash)

def smooth(a, b, t):
    u = min(1.0, max(0.0, (t - a) / (b - a))); return u * u * (3 - 2 * u)

# ---------------------------------------------------------------- terrain height
def _d_district(x, y):
    """Distance outside the Trost bulge (0 inside); large north of Wall Rose."""
    if y > 0:
        return 1e9
    if y >= -TS:
        return max(abs(x) - TW, 0.0)
    return max(math.hypot(x, y + TS) - TRR, 0.0)

def H(x, y):
    flat = smooth(250.0, 1400.0, abs(y))
    if y < 0:
        flat = min(flat, smooth(120.0, 900.0, _d_district(x, y)))
    flat *= smooth(380.0, 900.0, math.hypot(x - CAMP.x, y - CAMP.y))
    h = (noise.noise(Vector((x / 1800, y / 1800, 0.3))) * 16 + noise.noise(Vector((x / 420, y / 420, 1.7))) * 3
         + noise.noise(Vector((x / 260, y / 260, 4.2))) * 0.6) * flat
    w = WD.core_w(x, y, CORES)                           # local terrain inside the cores, the world relief outside
    return h * w + (1.0 - w) * (WD.ground_z(x, y, "trost") if w < 1.0 else 0.0)

L.height = H                 # people_kit.ground() / stage() / scene helpers read aotlib.height: THIS world

# ---------------------------------------------------------------- materials
SEASON_MATS = []             # (rgb node, palette[4])  palette order: summer, autumn, winter, spring
FOG_NODES = []               # emission-strength sockets of the fog chain (scaled down at night)
FOG_COL = (0.70, 0.75, 0.82, 1)
FOG_EMIT = float(os.environ.get("INT_FOG_EMIT", "0.3"))

def _fog(nt, col_out, bsdf):
    N, Lk = nt.nodes, nt.links
    cd = N.new("ShaderNodeCameraData")
    m1 = N.new("ShaderNodeMath"); m1.operation = "DIVIDE"; m1.inputs[1].default_value = -FOG_D
    Lk.new(cd.outputs["View Distance"], m1.inputs[0])
    m2 = N.new("ShaderNodeMath"); m2.operation = "EXPONENT"; Lk.new(m1.outputs[0], m2.inputs[0])
    m3 = N.new("ShaderNodeMath"); m3.operation = "SUBTRACT"; m3.inputs[0].default_value = 1.0; Lk.new(m2.outputs[0], m3.inputs[1])
    mx = N.new("ShaderNodeMix"); mx.data_type = "RGBA"
    Lk.new(m3.outputs[0], mx.inputs["Factor"]); Lk.new(col_out, mx.inputs["A"]); mx.inputs["B"].default_value = FOG_COL
    Lk.new(mx.outputs["Result"], bsdf.inputs["Base Color"])
    bsdf.inputs["Emission Color"].default_value = FOG_COL
    m4 = N.new("ShaderNodeMath"); m4.operation = "MULTIPLY"; m4.inputs[1].default_value = FOG_EMIT
    Lk.new(m3.outputs[0], m4.inputs[0]); Lk.new(m4.outputs[0], bsdf.inputs["Emission Strength"])
    FOG_NODES.append(m4.inputs[1])

def smat(name, pal, rough=0.9, var=0.25, var_scale=0.05, fog=True):
    """Seasonal material: base colour from an RGB node set per frame, painterly noise variation, distance fog."""
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; N, Lk = nt.nodes, nt.links
    bsdf = N["Principled BSDF"]; bsdf.inputs["Roughness"].default_value = rough
    rgb = N.new("ShaderNodeRGB"); rgb.outputs[0].default_value = (*pal[0], 1)
    tc = N.new("ShaderNodeTexCoord")
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = var_scale; nz.inputs["Detail"].default_value = 5
    Lk.new(tc.outputs["Object"], nz.inputs["Vector"])
    mr = N.new("ShaderNodeMapRange"); mr.inputs["To Min"].default_value = 1 - var; mr.inputs["To Max"].default_value = 1 + var
    Lk.new(nz.outputs["Fac"], mr.inputs["Value"])
    mul = N.new("ShaderNodeMix"); mul.data_type = "RGBA"; mul.blend_type = "MULTIPLY"; mul.inputs["Factor"].default_value = 1.0
    Lk.new(rgb.outputs[0], mul.inputs["A"])
    cmb = N.new("ShaderNodeCombineColor"); Lk.new(mr.outputs[0], cmb.inputs[0]); Lk.new(mr.outputs[0], cmb.inputs[1]); Lk.new(mr.outputs[0], cmb.inputs[2])
    Lk.new(cmb.outputs[0], mul.inputs["B"])
    if fog:
        _fog(nt, mul.outputs["Result"], bsdf)
    else:
        Lk.new(mul.outputs["Result"], bsdf.inputs["Base Color"])
    SEASON_MATS.append((rgb, [tuple(c) for c in pal]))
    return m

def flat(name, col, rough=0.85, emit=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*col, 1); b.inputs["Roughness"].default_value = rough
    if emit:
        b.inputs["Emission Color"].default_value = (*col, 1); b.inputs["Emission Strength"].default_value = emit
    return m

def season_rgb(pal, p):
    p = p % 4.0; i = int(p); f = p - i; f = f * f * (3 - 2 * f)
    a, b = pal[i], pal[(i + 1) % 4]
    return tuple(a[k] * (1 - f) + b[k] * f for k in range(3))

SNOW = (0.64, 0.66, 0.72)
def build_mats():
    M = {
        "stone": L.wall_mat(),
        "iron": L.mat("Iron", (0.035, 0.035, 0.04), 0.45),
        "gate": L.mat("GateWood", (0.17, 0.11, 0.07), 0.7, var=0.2, var_scale=0.8),
        "window": L.mat("Window", (0.05, 0.04, 0.035), 0.6),
        "plaster": L.fachwerk_mat("Plaster", (0.74, 0.66, 0.50)),
        "timber": L.fachwerk_mat("Timber", (0.62, 0.50, 0.34), beam=(0.12, 0.07, 0.04)),
        "plank": L.mat("Plank", (0.30, 0.20, 0.12), 0.85, var=0.2, var_scale=0.6),
        "bark": L.mat("Bark", (0.16, 0.11, 0.075), 0.9),
        "terrain": smat("TerrainS", [(0.085, 0.19, 0.04), (0.22, 0.17, 0.055), SNOW, (0.12, 0.25, 0.045)], var=0.3, var_scale=0.004),
        "dirt": smat("DirtS", [(0.36, 0.24, 0.12), (0.34, 0.23, 0.11), (0.60, 0.61, 0.66), (0.32, 0.21, 0.10)], var=0.2, var_scale=0.08),
        "road": smat("RoadS", [(0.40, 0.31, 0.19), (0.38, 0.30, 0.18), (0.56, 0.57, 0.62), (0.37, 0.29, 0.17)], var=0.15, var_scale=0.1),
        "plot_a": smat("PlotA", [(0.16, 0.26, 0.05), (0.42, 0.32, 0.10), SNOW, (0.20, 0.14, 0.08)], var=0.2, var_scale=0.15),
        "plot_b": smat("PlotB", [(0.30, 0.30, 0.07), (0.30, 0.20, 0.10), SNOW, (0.13, 0.22, 0.05)], var=0.2, var_scale=0.15),
        "canvas": smat("CanvasS", [(0.66, 0.60, 0.48), (0.60, 0.54, 0.42), (0.80, 0.82, 0.86), (0.64, 0.58, 0.46)], var=0.12, var_scale=0.5, fog=False),
        "canvas2": smat("Canvas2S", [(0.48, 0.42, 0.32), (0.44, 0.38, 0.28), (0.76, 0.78, 0.82), (0.47, 0.41, 0.31)], var=0.12, var_scale=0.5, fog=False),
        "roof": smat("RoofS", [(0.30, 0.14, 0.07), (0.28, 0.13, 0.07), (0.76, 0.78, 0.83), (0.30, 0.14, 0.07)], var=0.15, var_scale=0.3, fog=False),
        "roof2": smat("Roof2S", [(0.22, 0.15, 0.09), (0.21, 0.14, 0.08), (0.74, 0.76, 0.81), (0.22, 0.15, 0.09)], var=0.15, var_scale=0.3, fog=False),
        "leaf": smat("LeafS", [(0.12, 0.25, 0.05), (0.55, 0.22, 0.04), (0.30, 0.26, 0.22), (0.20, 0.36, 0.07)], var=0.25, var_scale=0.5),
        "leaf2": smat("Leaf2S", [(0.08, 0.19, 0.04), (0.60, 0.36, 0.05), (0.27, 0.23, 0.19), (0.16, 0.32, 0.06)], var=0.25, var_scale=0.5),
        "leaf3": smat("Leaf3S", [(0.16, 0.27, 0.06), (0.48, 0.14, 0.04), (0.32, 0.28, 0.24), (0.26, 0.40, 0.09)], var=0.25, var_scale=0.5),
        "leaf_dark": smat("LeafDarkS", [(0.03, 0.09, 0.035), (0.035, 0.09, 0.035), (0.45, 0.50, 0.52), (0.04, 0.11, 0.04)], var=0.2, var_scale=0.3),
        "rope": L.mat("Rope", (0.55, 0.45, 0.30), 0.8),
        "fire": flat("TorchFire", (1.0, 0.45, 0.10), emit=25.0),
    }
    return M

# ---------------------------------------------------------------- terrain, roads, strips
def build_terrain(M):
    bm = bmesh.new()
    Sz, N = 15000.0, 300
    def coord(i):
        t = i / N * 2 - 1
        return math.copysign(abs(t) ** 1.6, t) * Sz
    xs = [coord(i) for i in range(N + 1)]
    oy = 900.0                                                   # densest around the camps / camp
    vs = [[bm.verts.new((xs[i] - 600.0, xs[j] + oy, 0)) for j in range(N + 1)] for i in range(N + 1)]
    for row in vs:
        for v in row:
            v.co.z = H(v.co.x, v.co.y) - 0.05
    for i in range(N):
        for j in range(N):
            bm.faces.new((vs[i][j], vs[i + 1][j], vs[i + 1][j + 1], vs[i][j + 1]))
    for f in bm.faces:
        f.smooth = True
    return L.obj_from_bm("Terrain", bm, [M["terrain"]])

def strip(name, pts, width, m, lift=0.18, step=8.0):
    """Ground-hugging ribbon along a polyline (resampled), following H."""
    P = [Vector(p) for p in pts]
    R = [P[0]]
    for a, b in zip(P, P[1:]):
        n = max(1, int((b - a).length / step))
        R += [a + (b - a) * (k / n) for k in range(1, n + 1)]
    bm = bmesh.new(); prev = None
    for k, p in enumerate(R):
        t = (R[min(k + 1, len(R) - 1)] - R[max(k - 1, 0)]).normalized()
        nrm = Vector((-t.y, t.x))
        row = [bm.verts.new((q.x, q.y, H(q.x, q.y) + lift)) for q in (p - nrm * width / 2, p + nrm * width / 2)]
        if prev:
            bm.faces.new((prev[0], prev[1], row[1], row[0]))
        prev = row
    return L.obj_from_bm(name, bm, [m])

def rect(name, cx, cy, w, d, m, lift=0.2, n=6, rot=0.0):
    bm = bmesh.new()
    c, s = math.cos(rot), math.sin(rot)
    g = [[None] * (n + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        for j in range(n + 1):
            lx, ly = (i / n - 0.5) * w, (j / n - 0.5) * d
            x, y = cx + lx * c - ly * s, cy + lx * s + ly * c
            g[i][j] = bm.verts.new((x, y, H(x, y) + lift))
    for i in range(n):
        for j in range(n):
            bm.faces.new((g[i][j], g[i + 1][j], g[i + 1][j + 1], g[i][j + 1]))
    return L.obj_from_bm(name, bm, [m])

# ---------------------------------------------------------------- geometry-node instancer (points + per-point attrs)
def instancer(name, protos, n, static=None):
    """Point cloud of n points instancing protos (list of objects, picked by int attr 'vi'); per-point float attrs
    's' (scale, 0 = hidden) and 'rz' (yaw).  Returns the object; update with set_points()."""
    coll = bpy.data.collections.new(name + "_P"); bpy.context.scene.collection.children.link(coll)
    for k, o in enumerate(protos):
        for uc in list(o.users_collection):
            uc.objects.unlink(o)
        o.name = f"{name}_{k:02d}"
        coll.objects.link(o); o.location = (0.0, 0.0, -6000.0)
    me = bpy.data.meshes.new(name + "_pts"); me.vertices.add(n)
    me.attributes.new("s", "FLOAT", "POINT"); me.attributes.new("rz", "FLOAT", "POINT"); me.attributes.new("vi", "INT", "POINT")
    ob = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(ob)
    ng = bpy.data.node_groups.new(name + "_GN", "GeometryNodeTree")
    ng.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    N, Lk = ng.nodes, ng.links
    gi = N.new("NodeGroupInput"); go = N.new("NodeGroupOutput")
    def attr(nm, t):
        a = N.new("GeometryNodeInputNamedAttribute"); a.data_type = t; a.inputs["Name"].default_value = nm; return a
    s = attr("s", "FLOAT")
    cmp = N.new("FunctionNodeCompare"); cmp.operation = "GREATER_THAN"
    Lk.new(s.outputs["Attribute"], cmp.inputs[0]); cmp.inputs[1].default_value = 0.001
    ci = N.new("GeometryNodeCollectionInfo"); ci.transform_space = "ORIGINAL"
    ci.inputs["Collection"].default_value = coll
    ci.inputs["Separate Children"].default_value = True; ci.inputs["Reset Children"].default_value = True
    xyz = N.new("ShaderNodeCombineXYZ"); Lk.new(attr("rz", "FLOAT").outputs["Attribute"], xyz.inputs[2])
    iop = N.new("GeometryNodeInstanceOnPoints")
    Lk.new(gi.outputs["Geometry"], iop.inputs["Points"]); Lk.new(cmp.outputs[0], iop.inputs["Selection"])
    Lk.new(ci.outputs[0], iop.inputs["Instance"]); iop.inputs["Pick Instance"].default_value = True
    Lk.new(attr("vi", "INT").outputs["Attribute"], iop.inputs["Instance Index"])
    Lk.new(xyz.outputs[0], iop.inputs["Rotation"]); Lk.new(s.outputs["Attribute"], iop.inputs["Scale"])
    Lk.new(iop.outputs["Instances"], go.inputs["Geometry"])
    ob.modifiers.new("GN", "NODES").node_group = ng
    if static is not None:
        set_points(ob, *static)
    return ob

_LAST = {}
def set_points(ob, xyz, s=None, rz=None, vi=None):
    """Write point positions / attrs; skipped when nothing changed (an unchanged mesh is not re-synced by Cycles)."""
    key = hash(tuple(np.asarray(v, np.float32).tobytes() if v is not None else b"" for v in (xyz, s, rz, vi)))
    if _LAST.get(ob.name) == key:
        return
    _LAST[ob.name] = key
    me = ob.data
    me.vertices.foreach_set("co", np.asarray(xyz, np.float32).ravel())
    if s is not None:
        me.attributes["s"].data.foreach_set("value", np.asarray(s, np.float32))
    if rz is not None:
        me.attributes["rz"].data.foreach_set("value", np.asarray(rz, np.float32))
    if vi is not None:
        me.attributes["vi"].data.foreach_set("value", np.asarray(vi, np.int32))
    me.update()

def Hv(x, y):
    return np.array([H(a, b) for a, b in zip(np.ravel(x), np.ravel(y))])

# ---------------------------------------------------------------- prototypes
import swarm845 as SW        # minimal faceless figure / titan geometry (same style as the 845 crowds)

def person_proto(name, shirt, pants, hair, skin, dress=False, seed=0):
    g = SW.Geo(); SW.person_geo(g, 0, 1.7, dress, random.Random(seed)); R = g.finish()
    mats = [L.mat(name + "_sh", shirt, 0.85), L.mat(name + "_pa", pants, 0.85), L.mat(name + "_sk", skin, 0.6), L.mat(name + "_ha", hair, 0.6)]
    return SW._mesh(name, R, g.f, g.fc, mats, bpy.context.scene.collection)

def civilian_protos(tag, n=10, seed=1):
    rnd = random.Random(seed); out = []
    for k in range(n):
        out.append(person_proto(f"{tag}{k}", SW.SHIRTS[(k * 5 + seed) % len(SW.SHIRTS)], rnd.choice(SW.PANTS), rnd.choice(SW.HAIRS),
                                rnd.choice(SW.SKINS), dress=k % 3 == 1, seed=k))
    return out

def cart_proto(M, name="Cart"):
    bm = bmesh.new()
    L.box(bm, (0, 0, 0.95), (1.5, 2.8, 0.45), mi=0)
    L.cyl(bm, (-0.8, -0.4, 0.55), (0.8, -0.4, 0.55), 0.55, seg=10, mi=2)
    L.box(bm, (0, -0.1, 1.55), (1.45, 2.4, 0.8), mi=1, taper=(0.55, 1.0))       # canvas cover
    L.box(bm, (0, 2.0, 1.25), (0.55, 1.6, 0.6), mi=3)                            # horse body
    L.box(bm, (0, 3.0, 1.6), (0.3, 0.7, 0.35), mi=3)                             # head / neck
    for sx in (-0.18, 0.18):
        for sy in (1.5, 2.55):
            L.box(bm, (sx, sy, 0.48), (0.13, 0.13, 0.95), mi=3)
    mats = [M["plank"], M["canvas"], M["iron"], L.mat("Horse", (0.22, 0.12, 0.06), 0.7)]
    return L.obj_from_bm(name, bm, mats)

def tent_proto(M, kind, name):
    bm = bmesh.new()
    if kind == 0:                                                 # A-frame ridge tent 3 x 4.4 m
        w, d, h = 3.0, 4.4, 2.1
        v = [bm.verts.new(c) for c in [(-w / 2, -d / 2, 0), (w / 2, -d / 2, 0), (0, -d / 2, h), (-w / 2, d / 2, 0), (w / 2, d / 2, 0), (0, d / 2, h)]]
        for f in [(v[0], v[1], v[2]), (v[3], v[5], v[4]), (v[0], v[2], v[5], v[3]), (v[1], v[4], v[5], v[2])]:
            bm.faces.new(f)
        mi = 0
    else:                                                         # square bell tent 5 x 5 m
        w, h = 5.0, 3.2
        v = [bm.verts.new(c) for c in [(-w / 2, -w / 2, 0), (w / 2, -w / 2, 0), (w / 2, w / 2, 0), (-w / 2, w / 2, 0), (0, 0, h)]]
        for k in range(4):
            bm.faces.new((v[k], v[(k + 1) % 4], v[4]))
        mi = 1
    for f in bm.faces:
        f.material_index = 0
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return L.obj_from_bm(name, bm, [M["canvas"] if kind == 0 else M["canvas2"]])

def tree_protos(M):
    out = []
    for i, k in enumerate(["broad"] * 6 + ["conifer"] * 4):
        out.append(bpy.data.objects.new(f"Tr{i}", L.tree_mesh(f"Tr{i}", k, M, i)))
        bpy.context.scene.collection.objects.link(out[-1])
    return out


# ---------------------------------------------------------------- world build
def strip_into(bm, pts, width, lift=0.16, step=8.0):
    P = [Vector(p[:2]) for p in pts]
    if len(P) < 2:
        return
    R = [P[0]]
    for a, b in zip(P, P[1:]):
        n = max(1, int((b - a).length / step))
        R += [a + (b - a) * (k / n) for k in range(1, n + 1)]
    prev = None
    for k, p in enumerate(R):
        t = (R[min(k + 1, len(R) - 1)] - R[max(k - 1, 0)])
        if t.length < 1e-6:
            continue
        t.normalize(); nrm = Vector((-t.y, t.x))
        row = [bm.verts.new((q.x, q.y, H(q.x, q.y) + lift)) for q in (p - nrm * width / 2, p + nrm * width / 2)]
        if prev:
            bm.faces.new((prev[0], prev[1], row[1], row[0]))
        prev = row

def build_trost(M):
    """Wall Rose + the Trost bulge (trost.build_walls), its houses (trost.town_points) and streets."""
    M.update({
        "plaster_w": L.fachwerk_mat("PlasterW", (0.80, 0.76, 0.64)),
        "plaster_o": L.fachwerk_mat("PlasterO", (0.70, 0.56, 0.36)),
        "roof_red": L.tile_roof_mat("RoofRed", (0.36, 0.14, 0.06)),
        "roof_brown": L.tile_roof_mat("RoofBrown", (0.26, 0.13, 0.06)),
        "roof_dark": L.tile_roof_mat("RoofDark", (0.24, 0.09, 0.05)),
        "roof_orange": L.tile_roof_mat("RoofOrange", (0.42, 0.20, 0.07)),
        "roof_slate": L.mat("RoofSlate", (0.20, 0.22, 0.25), 0.6),
        "stone_light": L.mat("StoneLight", (0.62, 0.60, 0.55), 0.85, var=0.15, var_scale=0.3),
        "church_w": L.mat("ChurchWhite", (0.80, 0.76, 0.66), 0.85),
        "bronze": L.mat("Bronze", (0.30, 0.20, 0.08), 0.4),
        "cobble": L.mat("CobbleI", (0.40, 0.36, 0.30), 0.9, var=0.2, var_scale=0.2),
    })
    TR.build_walls(M)
    hc = L.new_coll("HouseVariants")
    walls = ["plaster", "plaster_w", "plaster_o", "timber"]
    roofs = ["roof_red", "roof_orange", "roof_brown", "roof_red", "roof_dark"]
    rnd = random.Random(8); widths = []
    for i in range(30):
        w = rnd.uniform(7.5, 11); d = rnd.uniform(11, 15); h = rnd.choice((11, 14, 14, 17, 17, 20))
        me = L.house_mesh(f"TH{i}", w, d, h, d * 0.5, M, walls[i % 4], roofs[(i // 4) % 5], chimney=i % 3 == 0, hip=i % 6 == 0)
        hc.objects.link(bpy.data.objects.new(f"TH{i}", me)); widths.append((w, d))
    pts, _trees = TR.town_points(len(widths), widths)
    pts = [p for p in pts if p[1] < -12.0]               # no Trost houses north of Wall Rose (they sat in front of the camps)
    L.scatter("Town", hc, pts, 846)
    for o in hc.objects:
        o.location = (0.0, 0.0, -5000.0)
    bm = bmesh.new()
    for spts, hw in TR.street_polylines():
        strip_into(bm, spts, hw * 2, lift=0.12)
    L.obj_from_bm("TrostStreets", bm, [M["cobble"]])
    bmd = bmesh.new()
    bmd.faces.new([bmd.verts.new((x * 0.996, y * 0.996, 0.08)) for x, y in L.district_outline(10.0)])
    L.obj_from_bm("DistrictGround", bmd, [M["dirt"]])
    try:
        TR.build_church(M)
    except Exception as ex:
        print("[int] church skipped:", repr(ex))
    print(f"[int] trost: {len(pts)} houses", flush=True)

def build_plain_wall(M):
    gw = L.GATE_W / 2 + 0.5
    rose = [(float(x), 0.0) for x in np.arange(-14000.0, 14001.0, 25.0)]
    rose += [(X0 - gw + 0.4, 0.0), (X0 - gw * 0.5, 0.0), (X0, 0.0), (X0 + gw * 0.5, 0.0), (X0 + gw - 0.4, 0.0)]
    rose = sorted(set(rose)); gaps = [(X0, 0.0, gw)]
    L.wall_ring("WallRose", rose, M, gaps=gaps)
    L.buttresses("ButtressRose", [p for p in rose if abs(p[0]) < 5000], gaps, M)
    L.wall_top("WallTopRose", [p for p in rose if abs(p[0]) < 3000], gaps, M)
    L.gatehouse("InnerGate", (X0, 0), 0, M)

def build():
    L.reset()
    sc = bpy.context.scene
    M = build_mats()
    build_terrain(M)
    st = {"M": M}
    if TR:
        try:
            build_trost(M)
        except Exception as ex:
            import traceback; traceback.print_exc()
            print("[int] trost build failed, plain wall:", ex)
            build_plain_wall(M)
    else:
        build_plain_wall(M)
    rnd = random.Random(845)
    # ---- roads: north from the inner gate past the camps, branch to the training camp; south from the outer gate
    strip("RoadNorth", [(X0, 8.0)] + [(X0 + 18 * math.sin(k / 3.0) * (k / 30), 8.0 + k * 40.0) for k in range(1, 60)], 12.0, M["road"])
    strip("RoadCamp", [(X0 - 170, 300), (-700, 420), (-1050, 560), (CAMP.x + 250, CAMP.y - 68)], 8.0, M["road"])
    strip("RoadSouth", [(OUTER[0], OUTER[1] - 6)] + [(OUTER[0] + 220 * math.sin(k / 9.0) * min(1, k / 12), OUTER[1] - k * 60.0)
                                                    for k in range(1, 150)], 10.0, M["road"])
    rect("GatePlazaIn", X0, 60, 360, 90, M["dirt"], lift=0.12)
    rect("CampSquare", X0, 300, 300, 380, M["dirt"], lift=0.1)
    # ---- refugee tents: fewer, bigger tents in long rows (reads as a camp from the air), cooking-fire smoke in the lanes
    tents = []
    fires = []
    for gx in np.arange(-690.0, 691.0, 9.0):
        for gy in np.arange(50.0, 770.0, 15.0):
            ix, iy = int(round(gx / 9)), int(round((gy - 50) / 15))
            if ix % 9 == 0 or abs(gx) < 18:
                continue                                         # north-south lanes, road
            if iy % 4 == 3:
                if ix % 9 == 4 and rnd.random() < 0.7:
                    fires.append((X0 + gx, gy))                  # cooking fires in the east-west lanes
                continue
            if abs(gx) < 150 and 120 < gy < 470:
                continue                                         # the camp square
            x, y = X0 + gx + rnd.uniform(-0.6, 0.6), gy + rnd.uniform(-0.6, 0.6)
            dn = math.hypot(gx / 700, (gy - 40) / 730) / 1.42
            tents.append((x, y, math.pi / 2 + rnd.uniform(-0.04, 0.04), 1 if rnd.random() < 0.15 else 0,
                          -2.0 + 5.0 * min(1.0, dn) ** 1.6 + rnd.uniform(-0.25, 0.25)))
    T = np.array(tents)
    st["tents"] = dict(ob=instancer("Tents", [tent_proto(M, 0, "TentA"), tent_proto(M, 1, "TentB")], len(T)), T=T,
                       xyz=np.stack([T[:, 0], T[:, 1], Hv(T[:, 0], T[:, 1])], 1))
    set_points(st["tents"]["ob"], st["tents"]["xyz"], np.zeros(len(T)), T[:, 2], T[:, 3].astype(int))
    import smokecards as SC
    cs = SC.SmokeCards("CampSmoke")
    F = np.array(fires)
    te = []; pos = []
    for k, (fx_, fy_) in enumerate(F):
        for j in range(int(9.0 / 0.25)):
            te.append(-1.5 + j * 0.25 + (k % 5) * 0.05); pos.append((fx_, fy_, H(fx_, fy_) + 1.0))
    cs.add_many(np.array(te), np.array(pos), None, 3.2, 24.0, 3.4, 14.0, kind="smoke", alpha=0.9, color=(0.27, 0.22, 0.17))
    cs.build(None)
    st["smoke"] = [cs]
    st["n_fires"] = len(F)
    # ---- storehouses along the wall (rise 1.0-5.5 s)
    barns = []
    for k, x in enumerate([sx * v for v in np.arange(70.0, 700.0, 46.0) for sx in (-1, 1)]):
        me = L.house_mesh(f"Barn{k}", 34.0, 12.0, 6.0, 4.5, M, "timber", "roof" if k % 2 else "roof2")
        me.transform(Matrix.Rotation(math.pi / 2, 4, "Z"))                 # long side along the wall
        ob = bpy.data.objects.new(f"Barn{k}", me); sc.collection.objects.link(ob)
        bx = X0 + x
        barns.append((ob, Vector((bx, 25.0, H(bx, 25.0))), 0.5 + 3.6 * abs(x) / 700 + rnd.uniform(-0.3, 0.3)))
    st["barns"] = barns
    # ---- refugees milling in the lanes and on the square
    civ = civilian_protos("Civ", 10, 3)
    nref = 2600
    gx_ = np.array([rnd.uniform(-690, 690) for _ in range(nref)]); ry_ = np.array([rnd.uniform(40, 760) for _ in range(nref)])
    lane = np.round(gx_ / 56) * 56; snap = np.array([rnd.random() < 0.5 for _ in range(nref)])
    gx_ = np.where(snap, lane + np.array([rnd.uniform(-3, 3) for _ in range(nref)]), gx_)
    ry_ = np.where(~snap, np.round(ry_ / 48) * 48 + np.array([rnd.uniform(-3, 3) for _ in range(nref)]), ry_)
    dn = np.hypot(gx_ / 700, (ry_ - 40) / 730) / 1.42
    rx_ = X0 + gx_
    st["ref"] = dict(ob=instancer("Refugees", civ, nref), x=rx_, y=ry_, z=Hv(rx_, ry_), t_app=-2.0 + 5.0 * np.minimum(1, dn) ** 1.6,
                     ph=np.array([rnd.uniform(0, 6.28) for _ in range(nref)]), w=np.array([rnd.uniform(0.6, 1.6) for _ in range(nref)]),
                     vi=np.array([rnd.randrange(10) for _ in range(nref)]))
    # ---- forest north of the camps: cleared from the camp side outward (1.0-6.3 s), plots appear behind the front
    trp = tree_protos(M)
    def t_cut(x, y):
        return 0.5 + 4.4 * np.clip((np.hypot((x - X0) * 0.55, y - 760) - 60) / 900.0, 0, 1)
    fx, fy = [], []
    for gx in np.arange(-1350.0, 1351.0, 13.0):
        for gy in np.arange(820.0, 1720.0, 13.0):
            if abs(gx) < 22:
                continue
            fx.append(X0 + gx + rnd.uniform(-5, 5)); fy.append(gy + rnd.uniform(-5, 5))
    fx, fy = np.array(fx), np.array(fy)
    keep = np.hypot(fx - CAMP.x, fy - CAMP.y) > 520
    fx, fy = fx[keep], fy[keep]
    st["clear"] = dict(ob=instancer("ClearTrees", list(trp), len(fx)), tc=t_cut(fx, fy),
                       sc=np.array([rnd.uniform(0.8, 1.25) for _ in fx]), xyz=np.stack([fx, fy, Hv(fx, fy)], 1))
    set_points(st["clear"]["ob"], st["clear"]["xyz"], st["clear"]["sc"],
               np.array([rnd.uniform(0, 6.28) for _ in fx]), np.array([rnd.randrange(10) for _ in fx]))
    plots = []
    for k, gx in enumerate(np.arange(-1290.0, 1291.0, 140.0)):
        for j, gy in enumerate(np.arange(850.0, 1700.0, 52.0)):
            px = X0 + gx
            if abs(gx) < 80 or math.hypot(px - CAMP.x, gy - CAMP.y) < 560:
                continue
            ob = rect(f"Plot{k}_{j}", px, gy, 132.0, 46.0, M["plot_a" if (k + j) % 2 else "plot_b"], lift=0.14, n=4)
            plots.append((ob, float(t_cut(np.array([px]), np.array([gy]))[0]) + 0.35))
    st["plots"] = plots
    # static forest: north of the fields and round the camp, copses inside Rose, scattered trees in the Maria lands
    sx, sy = [], []
    for _ in range(26000):
        x, y = rnd.uniform(-4200, 3600), rnd.uniform(1700, 4200)
        if math.hypot(x - CAMP.x, y - CAMP.y) < 900 or abs(x - X0) < 30:
            continue
        if noise.noise(Vector((x / 700, y / 700, 2.0))) < -0.15:
            continue
        sx.append(x); sy.append(y)
    sx, sy = np.array(sx), np.array(sy)
    instancer("Forest", [bpy.data.objects.new(f"TrS{i}", o.data) for i, o in enumerate(trp)], len(sx),
              static=(np.stack([sx, sy, Hv(sx, sy)], 1), np.array([rnd.uniform(0.8, 1.3) for _ in sx]),
                      np.array([rnd.uniform(0, 6.28) for _ in sx]), np.array([rnd.randrange(10) for _ in sx])))
    # workers in the clearing (felling, hauling) near the moving front
    nw = 500
    wx = np.array([X0 + rnd.uniform(-1300, 1300) for _ in range(nw)]); wy = np.array([rnd.uniform(830, 1700) for _ in range(nw)])
    st["work"] = dict(ob=instancer("Workers", civilian_protos("Wk", 6, 7), nw), x=wx, y=wy, z=Hv(wx, wy), tc=t_cut(wx, wy),
                      vi=np.array([rnd.randrange(6) for _ in range(nw)]), ph=np.array([rnd.uniform(0, 6.28) for _ in range(nw)]))
    # carts hauling logs / grain along the north road (a moving trickle)
    st["carts"] = dict(ob=instancer("Carts", [cart_proto(M, "HaulCart")], 40), ph=np.array([rnd.random() for _ in range(40)]),
                       lane=np.array([rnd.choice((-3.0, 3.0)) for _ in range(40)]))
    build_camp(M, st, rnd)
    world(st)
    st["terrain"] = bpy.data.objects.get("Terrain")
    if os.environ.get("INT_WORLD", "1") == "1":
        WD.attach("trost", M, st["terrain"], cores=CORES)   # trims my terrain / Wall Rose outside the cores; world beyond
    st["terrain_mat"] = M["terrain"]
    wg = bpy.data.objects.get("WD_Ground")
    st["world_ground_mat"] = wg.data.materials[0] if wg else None
    st["track"] = {}
    for nm in ("Eren", "Mikasa", "Armin"):             # name-tag anchors for hud2 (obj: "Eren")
        e = bpy.data.objects.new(nm, None); sc.collection.objects.link(e)
        e.location = (0, 0, -9000); st["track"][nm] = e
    return st

def _seg_dist(px, py, a, b):
    ax, ay = a; bx, by = b
    vx, vy = bx - ax, by - ay
    u = max(0.0, min(1.0, ((px - ax) * vx + (py - ay) * vy) / (vx * vx + vy * vy)))
    return math.hypot(px - ax - u * vx, py - ay - u * vy)

def dress_camp(M, st, rnd, PK):
    """The 104th camp as a clearing in wooded hills: pine ring, fence, lookout tower, horse paddock with horses,
    haystacks, carts, the cadet-corps flag, ODM training posts and wooden titan cut-outs with marked napes."""
    sc = bpy.context.scene
    C = CAMP
    wood = M["plank"]
    hay = smat("HayS", [(0.55, 0.42, 0.16), (0.50, 0.36, 0.12), SNOW, (0.48, 0.38, 0.15)], var=0.2, var_scale=0.8, fog=False)
    board = L.mat("TitanBoard", (0.52, 0.38, 0.24), 0.85, var=0.2, var_scale=0.5)
    nape = L.mat("NapeMark", (0.62, 0.06, 0.04), 0.7)
    road = [(-1050.0, 560.0), (C.x + 250, C.y - 68)]
    # ---- fence round the compound (gap where the camp road comes in on the east side)
    x0, x1, y0, y1 = C.x - 240, C.x + 240, C.y - 160, C.y + 130
    bm = bmesh.new()

    def fence_line(a, b, gap=None):
        a, b = Vector(a), Vector(b); n = max(1, int((b - a).length / 3.5))
        prev = None
        for k in range(n + 1):
            p_ = a + (b - a) * (k / n)
            if gap and gap[0] <= p_.y <= gap[1] and abs(p_.x - x1) < 1:
                prev = None; continue
            z = H(p_.x, p_.y)
            L.cyl(bm, (p_.x, p_.y, z), (p_.x, p_.y, z + 1.5), 0.08, seg=5)
            if prev is not None:
                for hh in (0.65, 1.2):
                    L.cyl(bm, (prev.x, prev.y, H(prev.x, prev.y) + hh), (p_.x, p_.y, z + hh), 0.045, seg=4)
            prev = p_
    fence_line((x0, y0), (x1, y0)); fence_line((x1, y0), (x1, y1), gap=(C.y - 88, C.y - 48))
    fence_line((x1, y1), (x0, y1)); fence_line((x0, y1), (x0, y0))
    # horse paddock (south-east corner) with horses
    px0, px1, py0, py1 = C.x + 150, C.x + 215, C.y - 150, C.y - 105
    fence_line((px0, py0), (px0, py1)); fence_line((px0, py1), (px1, py1))
    for k in range(9):
        hx, hy = rnd.uniform(px0 + 5, px1 - 5), rnd.uniform(py0 + 5, py1 - 5)
        PK.horse_only((hx, hy, H(hx, hy)), rnd.uniform(0, 6.28), rnd.choice(["horse_bay", "horse_chestnut", "horse_grey"]))
    # ---- lookout tower (north-west corner)
    tx, ty = C.x - 222, C.y + 112; tz = H(tx, ty)
    for sx in (-1.6, 1.6):
        for sy in (-1.6, 1.6):
            L.cyl(bm, (tx + sx * 1.3, ty + sy * 1.3, tz), (tx + sx * 0.9, ty + sy * 0.9, tz + 12.5), 0.14, seg=5)
    for zz in (3.5, 7.5):
        for (ax_, ay_), (bx_, by_) in (((-1, -1), (1, 1)), ((1, -1), (-1, 1))):
            L.cyl(bm, (tx + ax_ * 1.9, ty + ay_ * 1.9, tz + zz), (tx + bx_ * 1.7, ty + by_ * 1.7, tz + zz + 3.5), 0.06, seg=4)
    L.box(bm, (tx, ty, tz + 12.6), (4.2, 4.2, 0.3))
    for sx, sy, w_, d_ in ((0, 2.0, 4.2, 0.15), (0, -2.0, 4.2, 0.15), (2.0, 0, 0.15, 4.2), (-2.0, 0, 0.15, 4.2)):
        L.box(bm, (tx + sx, ty + sy, tz + 13.3), (w_, d_, 1.1))
    v = [bm.verts.new(c) for c in [(tx - 2.6, ty - 2.6, tz + 15.0), (tx + 2.6, ty - 2.6, tz + 15.0), (tx + 2.6, ty + 2.6, tz + 15.0),
                                   (tx - 2.6, ty + 2.6, tz + 15.0), (tx, ty, tz + 17.0)]]
    for k in range(4):
        bm.faces.new((v[k], v[(k + 1) % 4], v[4]))
    for k in range(4):
        cxp, cyp = tx + (1 if k % 2 else -1) * 1.9, ty + (1 if k // 2 else -1) * 1.9
        L.cyl(bm, (cxp, cyp, tz + 12.6), (cxp, cyp, tz + 15.0), 0.07, seg=4)
    # ---- ODM training posts (south-west of the field): tall poles with cross-arms
    for k in range(10):
        ox, oy = C.x - 190 + (k % 5) * 30 + rnd.uniform(-4, 4), C.y - 128 + (k // 5) * 18 + rnd.uniform(-3, 3)
        oz = H(ox, oy)
        L.cyl(bm, (ox, oy, oz), (ox, oy, oz + 14.0), 0.2, 0.15, seg=6)
        a = rnd.uniform(0, math.pi)
        L.cyl(bm, (ox - 2.2 * math.cos(a), oy - 2.2 * math.sin(a), oz + 12.0), (ox + 2.2 * math.cos(a), oy + 2.2 * math.sin(a), oz + 12.0), 0.1, seg=5)
    # ---- carts by the mess hall
    for k in range(3):
        cxk, cyk = C.x + 140 + k * 7, C.y + 62
        o = cart_proto(M, f"CampCart{k}"); o.location = (cxk, cyk, H(cxk, cyk)); o.rotation_euler.z = 0.3 * k - 0.2
    # ---- flagpole with the training corps' crossed-swords flag (south of the HQ)
    fx, fy = C.x - 150, C.y + 22; fz = H(fx, fy)
    L.cyl(bm, (fx, fy, fz), (fx, fy, fz + 14.0), 0.1, 0.06, seg=6)
    L.obj_from_bm("CampTimber", bm, [wood])
    PK._emblem_mat("swords", N=128, field=PK.srgb("#7A1E22"))
    dm = PK.Mesh()
    for nrm in ((0, -1, 0), (0, 1, 0)):
        dm.quad(Vector((fx + 1.45, fy, fz + 12.6)), nrm, (0, 0, 1), 2.6, "emb_swords_banner")
    dm.finish("CampFlag", PK._root_coll(), ink=0)
    # ---- haystacks
    hb = bmesh.new()
    for k in range(9):
        if k < 5:
            hx, hy = C.x + 150 + rnd.uniform(0, 60), C.y - 95 + rnd.uniform(0, 20)
        else:
            hx, hy = C.x + 200 + rnd.uniform(0, 25), C.y + 40 + rnd.uniform(0, 50)
        hz = H(hx, hy); r_ = rnd.uniform(1.6, 2.4)
        L.cyl(hb, (hx, hy, hz), (hx, hy, hz + 1.8), r_, r_ * 0.95, seg=10)
        bmesh.ops.create_cone(hb, cap_ends=True, segments=10, radius1=r_ * 0.98, radius2=0.2, depth=1.8,
                              matrix=Matrix.Translation((hx, hy, hz + 2.7)))
    L.obj_from_bm("Haystacks", hb, [hay])
    # ---- wooden titan cut-outs (the ODM course in the woods south of the fence): plank silhouettes, nape marked red
    tb = bmesh.new(); cut = []
    for k in range(9):
        cx_, cy_ = C.x - 210 + k * 42 + rnd.uniform(-8, 8), C.y - 205 - rnd.uniform(0, 60)
        Ht = rnd.uniform(6.5, 9.5); yaw = rnd.uniform(-0.6, 0.6); cz = H(cx_, cy_)
        c, s_ = math.cos(yaw), math.sin(yaw)
        u = Ht / 8.0

        def B(lx, lz, w, h, mi=0, ly=0.0, d=0.35):
            L.box(tb, (cx_ + lx * c - ly * s_, cy_ + lx * s_ + ly * c, cz + lz), (w, d, h), rot=yaw, mi=mi)
        B(-0.9 * u, 1.9 * u, 0.9 * u, 3.8 * u); B(0.9 * u, 1.9 * u, 0.9 * u, 3.8 * u)            # legs
        B(0, 5.0 * u, 2.6 * u, 2.6 * u)                                                         # torso
        B(-1.8 * u, 4.6 * u, 0.7 * u, 2.8 * u); B(1.8 * u, 4.6 * u, 0.7 * u, 2.8 * u)            # arms
        B(0, 6.9 * u, 1.5 * u, 1.4 * u)                                                         # head
        B(0, 6.15 * u, 0.9 * u, 0.5 * u, mi=1, ly=0.22, d=0.12)                                 # the nape (back of the neck)
        for sx in (-0.9, 0.9):
            L.cyl(tb, (cx_ + sx * u * c + 1.2 * s_, cy_ + sx * u * s_ - 1.2 * c, cz), (cx_ + sx * u * c, cy_ + sx * u * s_, cz + 4.5 * u), 0.12, seg=4)
        cut.append((cx_, cy_))
    L.obj_from_bm("TitanCutouts", tb, [board, nape])
    # ---- pine forest round the clearing (dense conifers on the hills)
    pines = [bpy.data.objects.new(f"Pine{i}", L.tree_mesh(f"Pine{i}", "conifer", M, 20 + i)) for i in range(4)]
    for o in pines:
        sc.collection.objects.link(o)
    px, py = [], []
    for _ in range(7000):
        a = rnd.uniform(0, 2 * math.pi); r_ = 235 + 165 * rnd.random() ** 0.8
        x, y = C.x + math.cos(a) * r_ * 1.15, C.y + math.sin(a) * r_
        if abs(x - C.x) < 268 and abs(y - C.y) < 190 or x > C.x + 330:
            continue
        if _seg_dist(x, y, *road) < 14 or (C.x - 240 < x < C.x + 150 and C.y - 290 < y < C.y - 175):
            continue
        if noise.noise(Vector((x / 260, y / 260, 3.3))) < -0.35:
            continue
        px.append(x); py.append(y)
    px, py = np.array(px), np.array(py)
    instancer("CampPines", pines, len(px), static=(np.stack([px, py, Hv(px, py) - 0.2], 1), np.array([rnd.uniform(0.9, 1.6) for _ in px]),
                                                    np.array([rnd.uniform(0, 6.28) for _ in px]), np.array([rnd.randrange(4) for _ in px])))
    print(f"[int] camp dressed: {len(px)} pines, {len(cut)} titan cut-outs", flush=True)

def build_camp(M, st, rnd):
    import people_kit as PK
    PK._MATS.clear(); PK._PROTO.clear()
    sc = bpy.context.scene
    rect("DrillField", CAMP.x, CAMP.y, 190.0, 120.0, M["dirt"], lift=0.12, n=8)
    oval = [(CAMP.x + 108 * math.cos(a), CAMP.y + 72 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 90)]
    strip("Track", oval, 4.5, M["road"], lift=0.2)
    # barracks north of the field, mess hall, HQ
    for k in range(6):
        x = CAMP.x - 115 + k * 46
        me = L.house_mesh(f"Barrack{k}", 34.0, 11.0, 5.0, 4.0, M, "timber", "roof2" if k % 2 else "roof")
        me.transform(Matrix.Rotation(math.pi / 2, 4, "Z"))
        ob = bpy.data.objects.new(f"Barrack{k}", me); sc.collection.objects.link(ob)
        ob.location = (x, CAMP.y + 92, H(x, CAMP.y + 92))
    for nm, (dx, dy, w, d, h) in {"MessHall": (165, 30, 18, 40, 8), "CampHQ": (-170, 48, 16, 26, 10)}.items():
        me = L.house_mesh(nm, w, d, h, 6.0, M, "plaster", "roof")
        ob = bpy.data.objects.new(nm, me); sc.collection.objects.link(ob)
        ob.location = (CAMP.x + dx, CAMP.y + dy, H(CAMP.x + dx, CAMP.y + dy))
    # balance rigs: two posts + crossbar along y; Eren's rig ERIG
    bm = bmesh.new()
    for j in range(5):
        cx, cy = RIG0.x, RIG0.y + j * 9.0
        z0 = H(cx, cy)
        for sy in (-1.7, 1.7):
            L.cyl(bm, (cx, cy + sy, z0), (cx, cy + sy, z0 + 3.4), 0.11, seg=6)
        L.cyl(bm, (cx, cy - 1.9, z0 + 3.25), (cx, cy + 1.9, z0 + 3.25), 0.09, seg=6)
    L.obj_from_bm("BalanceRigs", bm, [M["plank"]])
    rigs = []
    for j in range(5):
        cx, cy = RIG0.x, RIG0.y + j * 9.0
        z0 = H(cx, cy)
        piv = bpy.data.objects.new(f"RigPivot{j}", None); sc.collection.objects.link(piv)
        hipz = 1.75 if j == ERIG else 1.65
        piv.location = (cx, cy, z0 + hipz)
        rb = bmesh.new()
        for sy in (-1, 1):
            L.cyl(rb, (0, sy * 0.22, 0.0), (0, sy * 1.15, 3.25 - hipz), 0.025, seg=5)
        rope = L.obj_from_bm(f"RigRope{j}", rb, [M["rope"]]); rope.parent = piv
        if j == ERIG:
            e = PK.person("eren", (0.0, 0.0, 0.86), yaw=0.0, pose="stand")
            e.rotation_euler = (0.0, math.pi, -math.pi / 2)           # upside down, facing +x (east, toward the camera)
        else:
            e = PK.person(f"cadet:{j + 2}", (0.0, 0.0, -0.86), yaw=-math.pi / 2, pose="stand")
        e.parent = piv
        rigs.append((piv, e, j))
    st["rigs"] = rigs
    rc = Vector((RIG0.x, RIG0.y + ERIG * 9.0))
    st["rig_side"] = [PK.person("mikasa", (rc.x + 2.6, rc.y - 1.3, H(rc.x + 2.6, rc.y - 1.3) + 0.12), yaw=math.pi / 2 + 0.25),
                      PK.person("armin", (rc.x + 2.4, rc.y + 1.4, H(rc.x + 2.4, rc.y + 1.4) + 0.12), yaw=math.pi / 2 - 0.3)]
    st["eren_rig"] = rigs[ERIG][1]
    # 200 cadets: formation grid facing north (the stage); trio in the front row centre
    named = ["eren", "mikasa", "armin", "jean", "marco", "connie", "sasha", "reiner", "bertholdt", "annie", "christa", "ymir"]
    cols, rows = 20, 10
    F0 = Vector((CAMP.x, CAMP.y + 2.0))
    cad = []
    for r in range(rows):
        for c in range(cols):
            k = r * cols + c
            fx = F0.x + (c - (cols - 1) / 2) * 1.7; fy = F0.y - r * 1.9
            order = [9, 10, 8, 11, 7, 12, 6, 13, 5, 14, 4, 15]
            if r == 0 and c in order[:len(named)]:
                pre = named[order.index(c)]
            else:
                pre = f"cadet:{rnd.randrange(8)}"
            cad.append(dict(pre=pre, form=Vector((fx, fy)), k=k))
    for d in cad:
        d["protos"] = {p: PK.prototype(d["pre"], p, 0.0 if p != "run" else (d["k"] % 4) * 0.8)["coll"] for p in ("stand", "run", "salute")}
        e = PK.person(d["pre"], (d["form"].x, d["form"].y, H(d["form"].x, d["form"].y) + 0.12), yaw=0.0, pose="stand")
        d["ob"] = e
        # loose crowd watching the rigs (rig beat): east of the rigs
        d["watch"] = Vector((RIG0.x + 9 + rnd.uniform(0, 26), RIG0.y - 8 + rnd.uniform(0, 52)))
        d["lap"] = rnd.random() < 0.6
        d["lap_ph"] = rnd.uniform(0, 2 * math.pi)
        d["drill"] = Vector((CAMP.x + 30 + (d["k"] % 8) * 2.2, CAMP.y - 20 + (d["k"] // 8 % 10) * 2.2))
    st["cadets"] = cad
    dress_camp(M, st, rnd, PK)
    # graduation: stage north of the formation (facing south), torches round the formation
    PK.stage((CAMP.x, CAMP.y + 26.0), yaw=math.pi, banner=False, torches=6)
    fm = bmesh.new(); pm = bmesh.new(); lights = []; tips = []
    for k in range(14):
        a = k / 14 * 2 * math.pi
        x, y = CAMP.x + 34 * math.cos(a), CAMP.y - 6 + 24 * math.sin(a)
        z = H(x, y)
        L.cyl(pm, (x, y, z), (x, y, z + 3.0), 0.06, seg=5)
        L.cyl(pm, (x, y, z + 2.95), (x, y, z + 3.25), 0.10, 0.13, seg=6)          # torch head
        bmesh.ops.create_cone(fm, cap_ends=True, segments=7, radius1=0.22, radius2=0.0, depth=0.8,
                              matrix=Matrix.Translation((x, y, z + 3.65)))
        tips.append((x, y, z + 3.7))
        if k % 7 == 0:                                   # few, big, soft lights (QA: smoother pools)
            ld = bpy.data.lights.new(f"IntTorchL{k}", "POINT"); ld.color = (1.0, 0.55, 0.22); ld.shadow_soft_size = 3.0
            lo = bpy.data.objects.new(f"IntTorchL{k}", ld); lo.location = (x, y, z + 6.0); sc.collection.objects.link(lo)
            lights.append(ld)
    ld = bpy.data.lights.new("IntGradFill", "AREA"); ld.color = (1.0, 0.6, 0.3); ld.size = 40.0
    lo = bpy.data.objects.new("IntGradFill", ld); lo.location = (CAMP.x, CAMP.y - 6, H(CAMP.x, CAMP.y) + 22.0)
    sc.collection.objects.link(lo); st["grad_fill"] = ld
    L.obj_from_bm("IntTorchPoles", pm, [M["plank"]])
    st["flames"] = [L.obj_from_bm("IntTorchFlames", fm, [M["fire"]])] + [o for o in bpy.data.objects if o.name.startswith("PK_Fires")]
    for o in bpy.data.objects:                           # people_kit's stage lights: fewer, softer
        if o.name.startswith("PK_FireLight"):
            o.data.shadow_soft_size = 2.0
    st["fire_lights"] = lights + [o.data for o in bpy.data.objects if o.name.startswith("PK_FireLight")][:4]
    for o in bpy.data.objects:
        if o.name.startswith("PK_FireLight") and o.data not in st["fire_lights"]:
            o.hide_render = True
    import smokecards as SC
    gl = SC.SmokeCards("TorchGlow")                      # soft emissive halo round every torch head
    gl.add_many(np.full(len(tips), SI.T_GRAD - 0.7), np.array(tips), None, 0.7, 0.8, 30.0, 0.0, kind="glow", alpha=0.12, fade_in=0.6, color=(1.0, 0.5, 0.18))
    gl.build(None)
    st["smoke"].append(gl)

def world(st):
    sc = bpy.context.scene
    w = bpy.data.worlds.new("Sky"); sc.world = w; w.use_nodes = True
    nt = w.node_tree; sky = nt.nodes.new("ShaderNodeTexSky")
    types = sky.bl_rna.properties["sky_type"].enum_items.keys()
    sky.sky_type = "MULTIPLE_SCATTERING" if "MULTIPLE_SCATTERING" in types else "NISHITA"
    sky.sun_elevation = math.radians(40); sky.sun_rotation = math.radians(115); sky.air_density = 1.4
    if hasattr(sky, "sun_disc"): sky.sun_disc = False
    nt.links.new(sky.outputs[0], nt.nodes["Background"].inputs[0])
    tcw = nt.nodes.new("ShaderNodeTexCoord"); sz = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tcw.outputs["Generated"], sz.inputs[0])
    gr = nt.nodes.new("ShaderNodeValToRGB"); ge = gr.color_ramp.elements
    ge[0].position, ge[0].color = 0.0, (0.70, 0.80, 0.90, 1)
    ge[1].position, ge[1].color = 0.40, (0.18, 0.38, 0.78, 1)
    nt.links.new(sz.outputs["Z"], gr.inputs[0])
    bg2 = nt.nodes.new("ShaderNodeBackground"); bg2.inputs[1].default_value = 4.0
    nt.links.new(gr.outputs[0], bg2.inputs[0])
    lp = nt.nodes.new("ShaderNodeLightPath"); mx = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(lp.outputs["Is Camera Ray"], mx.inputs[0])
    nt.links.new(nt.nodes["Background"].outputs[0], mx.inputs[1]); nt.links.new(bg2.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], nt.nodes["World Output"].inputs[0])
    nt.nodes["Background"].inputs[1].default_value = 0.25
    sun = bpy.data.lights.new("Sun", "SUN"); sun.energy = 3.6; sun.angle = math.radians(1.5)
    so = bpy.data.objects.new("Sun", sun); sc.collection.objects.link(so)
    st.update(sun=sun, sun_ob=so, bg=[(nt.nodes["Background"], 0.25), (bg2, 4.0)], ramp=gr)

def set_sun(st, el_deg, az_deg):
    el, az = math.radians(el_deg), math.radians(az_deg)
    d = Vector((-math.cos(el) * math.cos(az), -math.cos(el) * math.sin(az), -math.sin(el)))
    _put(st["sun_ob"], "rotation_euler", d.to_track_quat("-Z", "Y").to_euler(), 2e-4)

# ---------------------------------------------------------------- camera: chord-scaled Hermite + monotone retiming
def _herm(p0, p1, p2, p3, u):
    d01, d12, d23 = (p1 - p0).length, (p2 - p1).length, (p3 - p2).length
    m1 = (p2 - p0) * (d12 / (d01 + d12)) if d01 + d12 > 1e-9 else p2 - p1
    m2 = (p3 - p1) * (d12 / (d12 + d23)) if d12 + d23 > 1e-9 else p2 - p1
    h00, h10, h01, h11 = 2 * u ** 3 - 3 * u ** 2 + 1, u ** 3 - 2 * u ** 2 + u, -2 * u ** 3 + 3 * u ** 2, u ** 3 - u ** 2
    return p1 * h00 + m1 * h10 + p2 * h01 + m2 * h11

def _pchip_m(T, S):
    D = [(S[i + 1] - S[i]) / (T[i + 1] - T[i]) for i in range(len(T) - 1)]
    return [0.0] + [0.0 if D[i - 1] * D[i] <= 0 else 2 * D[i - 1] * D[i] / (D[i - 1] + D[i]) for i in range(1, len(D))] + [0.0]

def _pchip(T, S, m, t):
    t = min(max(t, T[0]), T[-1])
    i = min(len(T) - 2, max(j for j in range(len(T)) if T[j] <= t))
    h = T[i + 1] - T[i]; s = (t - T[i]) / h
    h00, h10, h01, h11 = 2 * s ** 3 - 3 * s ** 2 + 1, s ** 3 - 2 * s ** 2 + s, -2 * s ** 3 + 3 * s ** 2, s ** 3 - s ** 2
    return h00 * S[i] + h10 * h * m[i] + h01 * S[i + 1] + h11 * h * m[i + 1]

class Channel:
    def __init__(self, T, pts):
        self.T, self.P = T, [Vector(p) for p in pts]
        n = len(pts); self.segs = []; S = [0.0]
        for i in range(n - 1):
            q = [self.P[max(0, min(n - 1, j))] for j in (i - 1, i, i + 1, i + 2)]
            acc = [0.0]; prev = q[1]
            for k in range(1, 97):
                p = _herm(*q, k / 96); acc.append(acc[-1] + (p - prev).length + 1e-7); prev = p
            self.segs.append((q, acc)); S.append(S[-1] + acc[-1])
        self.S, self.m = S, _pchip_m(T, S)
    def at(self, t):
        s = _pchip(self.T, self.S, self.m, t)
        i = min(len(self.segs) - 1, max(j for j in range(len(self.segs)) if self.S[j] <= s + 1e-9))
        q, acc = self.segs[i]; r = s - self.S[i]; k = 0
        while k < len(acc) - 2 and acc[k + 1] < r:
            k += 1
        f = min(1.0, max(0.0, (r - acc[k]) / (acc[k + 1] - acc[k])))
        return _herm(*q, (k + f) / 96)

RC = Vector((RIG0.x, RIG0.y + ERIG * 9.0))
D_LOOK = 300.0                                           # look point = loc + D_LOOK * dir (same convention as master_timeline)

def _seam(name):
    k = MT.seam_key(name, "trost")
    return dict(loc=Vector(k["loc"]), dir=Vector(k["dir"]).normalized(), lens=float(k["lens"]), vel=Vector(k["vel"]),
                ddir=Vector(k.get("ddir", (0, 0, 0))), dlnlens=float(k.get("dlnlens", 0.0)))

def cam_keys():
    """Camera keys (t, key).  key: loc, dir, lens and optionally vel / ddir / dlnlens (exact rates; otherwise central
    differences of the neighbours).  SEAMS (master_timeline.py, strict one take): t = 0 is S3 (the camps segment starts
    on C1's matched camera), t = SI.T_S7 is S7 (training starts on C3's camera), t = SI.DURATION is S8 (graduation night
    hands over to Trost).  The camps segment ends at SI.T_CAMPS_END (C2 starts from this camera there)."""
    C = CAMP
    def k(loc, look, lens, vel=None):
        loc = Vector(loc); d = (Vector(look) - loc).normalized()
        out = dict(loc=loc, dir=d, lens=float(lens))
        if vel is not None:
            out.update(vel=Vector(vel), ddir=Vector((0, 0, 0)), dlnlens=0.0)
        return out
    return [
        (0.0, _seam("S3")),                                                          # START (seam S3), daylight
        (2.6, k((120, -1250, 620), (-60, 300, 0), 30)),                             # over the Trost bulge
        (4.0, k((-60, -250, 480), (X0, 700, 0), 30)),                                # over Wall Rose: the camps
        (SI.T_CAMPS_END, k((-150, 380, 420), (X0 - 60, 1250, 0), 30, vel=(-60, 480, -40))),   # camps END (C2 takes over)
        (SI.T_S7, _seam("S7")),                                                      # training START (seam S7)
        (9.6, k((C.x - 252, C.y + 140, 30), (C.x - 10, C.y - 10, 0), 30)),           # reveal over the lookout tower
        (10.9, k((RC.x + 17, RC.y - 21, 13), (RC.x, RC.y + 0.6, 1.9), 36, vel=(-0.6, 0.6, -0.3))),   # Eren upside down
        (12.6, k((RC.x + 15, RC.y - 19, 12), (RC.x, RC.y + 0.6, 1.9), 36, vel=(-0.6, 0.6, -0.3))),
        (14.9, k((C.x + 30, C.y - 470, 125), (C.x - 10, C.y - 70, 0), 30)),          # seasons: titan cut-outs, lower third
        (17.2, k((C.x + 290, C.y - 400, 140), (C.x - 10, C.y - 40, 0), 30)),         # paddock + horses
        (18.4, k((C.x + 60, C.y - 90, 60), (C.x, C.y + 14, 1.5), 32)),               # graduation night: the rows
        (19.2, k((C.x + 130, C.y - 130, 120), (C.x + 10, C.y - 10, 0), 30)),
        (SI.DURATION, _seam("S8")),                                                  # END (seam S8), night
    ]

_TAB = {}
def _prep():
    ks = cam_keys(); n = len(ks)
    T = [t for t, _ in ks]; K = [dict(kk) for _, kk in ks]
    for kk in K:
        kk["L"] = kk["loc"] + kk["dir"] * D_LOOK; kk["ln"] = math.log(kk["lens"])
    for i, kk in enumerate(K):
        a, b = max(0, i - 1), min(n - 1, i + 1)
        dt = T[b] - T[a]
        if "vel" not in kk:
            kk["vel"] = (K[b]["loc"] - K[a]["loc"]) / dt
            kk["mL"] = (K[b]["L"] - K[a]["L"]) / dt
            kk["dlnlens"] = (K[b]["ln"] - K[a]["ln"]) / dt
        else:
            kk["mL"] = kk["vel"] + kk.get("ddir", Vector((0, 0, 0))) * D_LOOK
    _TAB.update(T=T, K=K)

def _h(p0, m0, p1, m1, T, s):
    h00, h10, h01, h11 = 2 * s ** 3 - 3 * s ** 2 + 1, s ** 3 - 2 * s ** 2 + s, -2 * s ** 3 + 3 * s ** 2, s ** 3 - s ** 2
    return p0 * h00 + m0 * (h10 * T) + p1 * h01 + m1 * (h11 * T)

def cam_at(t):
    """Cubic Hermite in time per span with the keys' rates: C1 everywhere, exact position / direction / lens /
    velocity at the seam keys (what master_timeline's connectors match)."""
    if not _TAB:
        _prep()
    T, K = _TAB["T"], _TAB["K"]
    t = min(max(t, T[0]), T[-1])
    i = 0
    while i < len(T) - 2 and T[i + 1] <= t:
        i += 1
    a, b = K[i], K[i + 1]; dT = T[i + 1] - T[i]; s = (t - T[i]) / dT
    loc = _h(a["loc"], a["vel"], b["loc"], b["vel"], dT, s)
    look = _h(a["L"], a["mL"], b["L"], b["mL"], dT, s)
    lens = math.exp(_h(a["ln"], a["dlnlens"], b["ln"], b["dlnlens"], dT, s))
    seam = min(abs(t - T[0]), abs(t - SI.T_S7), abs(t - T[-1])) < 1e-6
    if not seam:
        loc.z = max(loc.z, H(loc.x, loc.y) + 6.0)
        if abs(loc.y) < 30:                              # never through Wall Rose
            loc.z = max(loc.z, L.WALL_H + 25.0)
    return loc, (look - loc).to_track_quat("-Z", "Y").to_euler(), lens

# ---------------------------------------------------------------- per-frame state (pure function of t)
def _put(owner, attr, val, tol=1e-4):
    """Assign only when the value really changes: any write tags Cycles to re-sync (shader writes recompile)."""
    cur = getattr(owner, attr)
    try:
        same = all(abs(a - b) <= tol for a, b in zip(cur, val))
    except TypeError:
        same = cur == val if isinstance(val, bool) else abs(cur - val) <= tol
    if not same:
        setattr(owner, attr, val)

def update(st, t):
    sc = bpy.context.scene
    p = SI.season_at(t)
    for rgb, pal in SEASON_MATS:
        _put(rgb.outputs[0], "default_value", (*season_rgb(pal, p), 1), 2e-3)
    nite = SI.night_at(t)
    winter = max(0.0, 1 - abs(((p - 2.0 + 2) % 4) - 2))         # 1 at mid winter
    # THE light comes from the shared rig (world.light_rig: same presets in every scene, so seam frames match):
    # "day" (S3, camps end, S7), a dimmer low winter sun in the season time-lapses, "night" at S8 (graduation)
    wint = dict(WD.LIGHT_PRESETS["day"]); wint.update(el=24.0, amb=0.19, e=3.0)
    spec = WD.light_blend(WD.light_blend("day", wint, winter), "night", nite)
    key = tuple(round(v, 4) if not isinstance(v, tuple) else tuple(round(c, 4) for c in v) for v in spec.values())
    if st.get("light_key") != key:
        WD.light_rig(spec)
        st["light_key"] = key
    _put(st["bg"][1][0].inputs[1], "default_value", st["bg"][1][1] * (1 - 0.985 * nite) * (1 - 0.25 * winter), 2e-3)  # camera sky
    for s in FOG_NODES:
        _put(s, "default_value", FOG_EMIT * (1 - 0.97 * nite), 2e-3)
    for o in st["flames"]:
        _put(o, "hide_render", nite < 0.3)
    for ld in st["fire_lights"]:
        _put(ld, "energy", 900.0 * nite, 0.5)
    _put(st["grad_fill"], "energy", 2500.0 * nite, 0.5)
    # ---- camps (only drawn while the camera is near them)
    camps_on = t < SI.T_ENL
    tn = st["tents"]
    grow = np.clip((t - tn["T"][:, 4]) / 0.3, 0, 1)
    set_points(tn["ob"], tn["xyz"], grow * (1.7 if camps_on else 0.0), tn["T"][:, 2], tn["T"][:, 3].astype(int))
    tm = st["world_ground_mat"] if (st.get("world_ground_mat") and t >= SI.DURATION - 1.3) else st["terrain_mat"]
    ter = st.get("terrain")
    if ter and ter.data.materials and ter.data.materials[0] != tm:
        ter.data.materials[0] = tm
    for ob, base, ta in st["barns"]:
        _put(ob, "hide_render", not camps_on)
        u = smooth(ta, ta + 0.6, t)
        if abs(ob.location.z - (base.z - 9.0 * (1 - u))) > 1e-4 or ob.location.x != base.x:
            ob.location = (base.x, base.y, base.z - 9.0 * (1 - u))
    rf = st["ref"]
    a = rf["ph"] + t * rf["w"] * 1.4
    x = rf["x"] + 3.0 * np.sin(a); y = rf["y"] + 3.0 * np.cos(a * 0.8)
    v = np.clip((t - rf["t_app"]) / 0.3, 0, 1) * PSCALE * (1.0 if camps_on else 0.0)
    set_points(rf["ob"], np.stack([x, y, rf["z"]], 1), v, a + math.pi / 2, rf["vi"])
    cl = st["clear"]
    set_points(cl["ob"], cl["xyz"], np.where(t < cl["tc"], cl["sc"], 0.0))
    for ob, tp in st["plots"]:
        if ob.hide_render != (t < tp):
            ob.hide_render = t < tp
    wk = st["work"]
    wv = (np.abs(t - wk["tc"]) < 0.9) & camps_on
    a = wk["ph"] + t * 2.0
    set_points(wk["ob"], np.stack([wk["x"] + 2 * np.sin(a), wk["y"] + 2 * np.cos(a), wk["z"]], 1), wv * PSCALE, a, wk["vi"])
    ca = st["carts"]
    u = (ca["ph"] + t * 0.12) % 1.0                                  # up and down the north road, 60 m .. 1700 m
    cy = 60 + u * 1640; cx = X0 + 18 * np.sin((cy - 8) / 120.0) * ((cy - 8) / 1200.0) + ca["lane"]
    set_points(ca["ob"], np.stack([cx, cy, np.full(40, 0.15)], 1), np.full(40, 1.0 if camps_on else 0.0),
               np.where(ca["lane"] > 0, 0.0, math.pi), np.zeros(40, int))
    town = bpy.data.objects.get("Town")
    if town and town.hide_render != (not camps_on):
        town.hide_render = not camps_on
    # ---- training camp
    camp_on = t > SI.T_FLY
    rig_on = SI.T_RIG - 0.4 <= t < SI.T_SEA + 0.1
    for d in st["cadets"]:
        e = d["ob"]
        hid = not camp_on or (d["pre"] in ("eren", "mikasa", "armin") and rig_on)
        if e.hide_render != hid:
            e.hide_render = hid
        pose, pos, yaw = "stand", d["form"], 0.0
        if rig_on:                                                   # rig beat: watching the rigs
            pos, yaw = d["watch"], math.pi / 2
        elif SI.T_SEA <= t < SI.T_GRAD - 0.6:                        # three years of drill
            tt = t - SI.T_SEA
            if d["lap"]:
                ang = d["lap_ph"] + tt * 2.4
                pos = Vector((CAMP.x + 108 * math.cos(ang), CAMP.y + 72 * math.sin(ang)))
                yaw = ang + math.pi; pose = "run"
            else:
                pos = d["drill"] + Vector((28 * math.sin(tt * 2.2), 14 * math.sin(tt * 1.3)))
                pose = "run"; yaw = -math.pi / 2 if math.cos(tt * 2.2) > 0 else math.pi / 2
        elif t >= SI.T_GRAD - 0.6:
            pose = "salute"
        if e.instance_collection != d["protos"][pose]:
            e.instance_collection = d["protos"][pose]
        nl = Vector((pos.x, pos.y, H(pos.x, pos.y) + 0.12))
        if (e.location - nl).length > 1e-4 or abs(e.rotation_euler.z - yaw) > 1e-5:
            e.location = nl; e.rotation_euler = (0.0, 0.0, yaw)
    for piv, e, j in st["rigs"]:
        amp = 0.16 if j == ERIG else 0.05
        piv.rotation_euler = (0.0, amp * math.sin(t * 2.3 + j), 0.0) if j == ERIG else (amp * math.sin(t * 1.7 + j), 0.0, 0.0)
        for ch in piv.children:
            ch.hide_render = not rig_on
    for e in st["rig_side"]:
        e.hide_render = not rig_on

def anchors(st, t):
    """Move the Eren / Mikasa / Armin tracker empties (hudcam -> hud2 tags) and return screen (u, v) for each."""
    from bpy_extras.object_utils import world_to_camera_view
    sc = bpy.context.scene; out = {}; pick = {}
    if t >= SI.T_FLY:
        for d in st["cadets"]:
            if d["pre"] in ("eren", "mikasa", "armin") and not d["ob"].hide_render:
                pick[d["pre"]] = d["ob"].matrix_world.translation + Vector((0, 0, 2.0))
        if SI.T_RIG - 0.4 <= t < SI.T_SEA + 0.1:
            pick["eren"] = st["eren_rig"].matrix_world.translation + Vector((0, 0, 0.2))
            for nm, e in zip(("mikasa", "armin"), st["rig_side"]):
                pick[nm] = e.matrix_world.translation + Vector((0, 0, 2.0))
    for nm, e in st["track"].items():
        e.location = pick.get(nm.lower(), Vector((0, 0, -9000)))
    for nm, wp in pick.items():
        u, v, dd = world_to_camera_view(sc, sc.camera, wp)
        if dd > 0 and 0 <= u <= 1 and 0 <= v <= 1:
            out[nm] = [round(u, 4), round(v, 4)]
    return out

# ---------------------------------------------------------------- main
if __name__ == "__main__":
    t_b = time.time()
    st = build()
    sc = bpy.context.scene
    cd = bpy.data.cameras.new("Cam"); cd.clip_start = 0.5; cd.clip_end = 60000
    cam = bpy.data.objects.new("Cam", cd); sc.collection.objects.link(cam); sc.camera = cam
    L.render_setup(B.engine, B.res, B.samples, "GPU")
    st["expo"] = float(os.environ.get("EXPO", "-1.5"))
    sc.view_settings.exposure = st["expo"]
    if sc.render.engine == "CYCLES":
        cy = sc.cycles
        cy.samples = B.samples; cy.use_adaptive_sampling = False; cy.use_denoising = True
        # OptiX denoiser: ~0.3 s/frame on the GTX 1060 vs ~2.5 s for OIDN (which dominated the frame time)
        dn = os.environ.get("INT_DENOISER", "OPTIX")
        try:
            cy.denoiser = dn
        except Exception:
            cy.denoiser = "OPENIMAGEDENOISE"
        try:
            cy.denoising_use_gpu = True
        except Exception:
            pass
        print("[int] denoiser", cy.denoiser, flush=True)
        cy.max_bounces, cy.diffuse_bounces, cy.glossy_bounces, cy.transmission_bounces = 3, 1, 1, 1
        cy.volume_bounces = 0; cy.transparent_max_bounces = 24
        cy.caustics_reflective = cy.caustics_refractive = False
        sc.render.use_persistent_data = True
    else:
        sc.eevee.taa_render_samples = max(4, B.samples)
    sc.render.image_settings.file_format = "PNG"
    os.makedirs(B.out, exist_ok=True)
    print(f"[int] built in {time.time() - t_b:.0f}s, objects {len(bpy.data.objects)}", flush=True)
    times = [float(x) for x in B.times.split(",") if x.strip()] if B.times else \
        [B.t0 + j / B.fps for j in range(int(round((B.t1 - B.t0) * B.fps)))]
    apath = os.path.join(B.out, "anchors.json")
    try:
        AN = json.load(open(apath)) if B.times else {}
    except Exception:
        AN = {}
    t_s = time.time()
    last_png = None
    for i, t in enumerate(times):
        update(st, t)
        if sc.render.engine == "CYCLES":          # the torch-lit night needs a few more samples than daylight
            sc.cycles.samples = B.samples if SI.night_at(t) < 0.3 else max(B.samples, int(os.environ.get("INT_NIGHT_SMP", "12")))
        loc, rot, lens = cam_at(t)
        cam.location = loc; cam.rotation_euler = rot; cd.lens = lens
        for c in st["smoke"]:
            c.update(t, cam)
        bpy.context.view_layer.update()
        name = f"{B.prefix}_{i:05d}.png" if not B.times else f"{B.prefix}_t{t:05.2f}.png"
        tags = anchors(st, t)
        bpy.context.view_layer.update()
        hudcam.dump(sc, i, B.out, track=("Eren", "Mikasa", "Armin"), name=None if not B.times else name[:-4], t=t)
        sc.render.filepath = os.path.join(B.out, name)
        gap = (not B.times and os.environ.get("INT_RENDER_GAP", "0") != "1"
               and SI.T_CAMPS_END + 2.5 / B.fps < t < SI.T_S7 - 2.5 / B.fps and last_png)
        if B.dry:
            pass
        elif gap:                                   # 5.2-7.0 is never used by the master (C2 / C3 bridge it): hold a frame
            import shutil
            shutil.copyfile(last_png, sc.render.filepath)
        else:
            bpy.ops.render.render(write_still=True)
            last_png = sc.render.filepath
        AN[name] = dict(t=round(t, 4), tags=tags, hud=SI.hud_at(t))
        print(f"[int] t={t:.2f}s -> {name} ({time.time() - t_s:.0f}s)", flush=True)
    json.dump(AN, open(apath, "w"), ensure_ascii=False, indent=0)

