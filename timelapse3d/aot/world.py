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
    """Local terrain inside the set's core, the world relief outside it: every L.height() caller (march846's agents,
    swarms, camera clamps, flight.py props) then stands on the same ground the world mesh shows."""
    fr = active_frame(); w = core_w(x, y, CORES[fr])
    o = SET_ORIGIN[fr]
    return h * w + (1.0 - w) * world_height(x + o[0], y + o[1])

# ---------------------------------------------------------------- relief (WORLD coordinates)
# Rolling hills 20-120 m with a few higher wooded ridges (to ~200 m) only in the open land far between the walls
# (rolling hills <= ~58 m from ~1.2-1.5 km off the walls, plus wooded knolls; the 100-200 m relief only 2.3-4 km+
# away from walls, towns and the valley, so the 50 m walls stay the landmark); FLAT (0) under the walls
# and their districts, inside and round both town cores and Mitras, along the river valley (river + road on its floor)
# and along the coast.  Precomputed once on a GRID_M grid (bilinear lookup), so it is cheap for every caller.
GRID_M = float(os.environ.get("WORLD_GRID_M", "100"))
_HG = {}

def _flat_mask(x, y):
    """0 = keep flat, 1 = full relief."""
    d = math.hypot(x - MITRAS[0], y - MITRAS[1])
    m = 1.0
    for r in (R_MARIA, R_ROSE, R_SINA):                       # walls and their district bulges (720 m outward)
        m = min(m, _smooth(780.0, 1450.0, abs(d - r)))      # walls + bulges flat; hills from ~1.2-1.5 km
    m = min(m, _smooth(1800.0, 3200.0, d))                    # Mitras
    for f in CORES:
        for (cx, cy), r in CORES[f]:
            o = SET_ORIGIN[f]
            m = min(m, _smooth(r + 300.0, r + 1700.0, math.hypot(x - cx - o[0], y - cy - o[1])))
    xv = valley_x(y)                                          # the river valley (river + road on its floor)
    m = min(m, _smooth(750.0, 1900.0, abs(x - xv)))
    m = min(m, _smooth(SEA_Y + 900.0, SEA_Y + 2800.0, y))     # the coast
    m = min(m, _smooth(R_MARIA + 16000.0, R_MARIA + 9000.0, d))
    return m

def _big_mask(x, y):
    """The walls stay the landmark: relief above 30 m only far from every wall, town and the valley (open land)."""
    d = math.hypot(x - MITRAS[0], y - MITRAS[1])
    m = 1.0
    for r in (R_MARIA, R_ROSE, R_SINA):
        m = min(m, _smooth(2300.0, 4200.0, abs(d - r)))
    for f in CORES:
        for (cx, cy), r in CORES[f]:
            o = SET_ORIGIN[f]
            m = min(m, _smooth(r + 2500.0, r + 4500.0, math.hypot(x - cx - o[0], y - cy - o[1])))
    return min(m, _smooth(2200.0, 3500.0, abs(x - valley_x(y))))

def valley_x(y):
    """Centre line of the river valley (between the road and the river) at world y."""
    ty = SET_ORIGIN["trost"][1]
    if y < ty + 2500:
        return 180.0 + 120.0 * _smooth(-1000.0, ty, y)
    return 200.0 * max(0.0, 1 - (y - ty - 2500) / 6000.0)

def _relief_raw(x, y):
    n1 = noise.noise(Vector((x / 6500.0, y / 6500.0, 0.37)))
    n2 = noise.noise(Vector((x / 1700.0, y / 1700.0, 3.1)))
    n3 = noise.noise(Vector((x / 750.0, y / 750.0, 5.3)))
    loc = 0.5 + 0.5 * noise.noise(Vector((x / 11000.0, y / 11000.0, 9.4)))      # shorter hills only in places
    h = 68.0 + 40.0 * n1 + (20.0 + 22.0 * loc) * n2 + 20.0 * loc * n3          # ~20-120 m rolling ground, steeper short hills in places                            # ~10-60 m rolling ground
    rg = 1.0 - abs(noise.noise(Vector((x / 9000.0, y / 9000.0, 7.7))))       # ridged: crests along noise zero lines
    sel = _smooth(0.15, 0.55, noise.noise(Vector((x / 16000.0, y / 16000.0, 11.0))))   # only a few ridges
    h += 95.0 * sel * _smooth(0.84, 0.98, rg)                                     # ridges to ~200 m
    return max(10.0, h)

NEAR_K = float(os.environ.get("WORLD_NEAR_K", "0.6"))       # near walls/towns/valley: relief x0.6 (~12-70 m rolling)
KNOLLS = []

def _knolls():
    """Wooded knolls: local steep bumps (8-15 deg flanks, 25-45 m) in the open land, deterministic."""
    if KNOLLS:
        return KNOLLS
    rk = random.Random(1847)
    for _ in range(int(os.environ.get("WORLD_KNOLLS", "260"))):
        a = rk.uniform(0, math.tau); rr = math.sqrt(rk.random()) * (R_MARIA + 9000)
        x, y = MITRAS[0] + math.cos(a) * rr, MITRAS[1] + math.sin(a) * rr
        if _flat_mask(x, y) < 0.95:
            continue
        h = rk.uniform(25.0, 45.0); r = h / math.tan(math.radians(rk.uniform(8.0, 15.0))) * 1.25
        KNOLLS.append((x, y, h, r, rk.uniform(0.6, 1.0)))
    # depth along the low stretch of the Shiganshina -> Trost flight (mid-gap, away from the walls and the valley floor):
    # forested knolls either side of the valley, and two gentle background ridgelines running N-S further out
    for x, y, h, sl in ((-2300, 1900, 34, 12), (2500, 2200, 30, 10), (-2700, 2900, 38, 13), (2900, 3200, 32, 11),
                        (-2100, 3700, 28, 9), (2300, 3900, 30, 10), (-3200, 2300, 36, 14), (3400, 2700, 34, 12)):
        KNOLLS.append((float(x), float(y), float(h), h / math.tan(math.radians(sl)) * 1.25, rk.uniform(0.7, 1.0)))
    for x, y in ((-4300.0, 2700.0), (4600.0, 3000.0)):              # ridgelines: ~45 m, long N-S (elongation 4)
        KNOLLS.append((x, y, 45.0, 420.0, 4.0))
    return KNOLLS

def _build_grid():
    import numpy as np
    x0, x1 = -R_MARIA - 17000.0, R_MARIA + 17000.0
    y0, y1 = SEA_Y - 1000.0, MITRAS[1] + R_MARIA + 17000.0
    nx, ny = int((x1 - x0) / GRID_M) + 1, int((y1 - y0) / GRID_M) + 1
    G = np.zeros((nx, ny), np.float32)
    for i in range(nx):
        x = x0 + i * GRID_M
        for j in range(ny):
            y = y0 + j * GRID_M
            m = _flat_mask(x, y)
            if m > 0:
                raw = _relief_raw(x, y)
                near = raw * NEAR_K                             # scaled (not clipped: clipping made plateaus)
                G[i, j] = m * (near + (raw - near) * _big_mask(x, y))
    import numpy as np
    for kx, ky, kh, kr, el in _knolls():                   # stamp the knolls (gaussian-ish, slightly elongated)
        i0, i1 = max(0, int((kx - 2.2 * kr - x0) / GRID_M)), min(nx, int((kx + 2.2 * kr - x0) / GRID_M) + 2)
        j0, j1 = max(0, int((ky - 2.2 * kr - y0) / GRID_M)), min(ny, int((ky + 2.2 * kr - y0) / GRID_M) + 2)
        if i0 >= i1 or j0 >= j1:
            continue
        X = x0 + np.arange(i0, i1)[:, None] * GRID_M; Y = y0 + np.arange(j0, j1)[None, :] * GRID_M
        q = ((X - kx) / kr) ** 2 + ((Y - ky) / (kr * el)) ** 2
        G[i0:i1, j0:j1] += (kh * np.exp(-q * 1.6)).astype(np.float32)
    _HG.update(G=G, x0=x0, y0=y0, nx=nx, ny=ny)

def world_height(x, y):
    """Ground height (m) at WORLD (x, y): 0 = flat (walls, towns, valley, coast), up to ~130 m on the ridges."""
    if not _HG:
        _build_grid()
    G = _HG["G"]; fx = (x - _HG["x0"]) / GRID_M; fy = (y - _HG["y0"]) / GRID_M
    i, j = int(math.floor(fx)), int(math.floor(fy))
    if i < 0 or j < 0 or i >= _HG["nx"] - 1 or j >= _HG["ny"] - 1:
        return 0.0
    u, v = fx - i, fy - j
    return float(G[i, j] * (1 - u) * (1 - v) + G[i + 1, j] * u * (1 - v) + G[i, j + 1] * (1 - u) * v + G[i + 1, j + 1] * u * v)

def world_height_np(X, Y):
    """Vectorised world_height for numpy arrays."""
    import numpy as np
    if not _HG:
        _build_grid()
    G = _HG["G"]; fx = (np.asarray(X) - _HG["x0"]) / GRID_M; fy = (np.asarray(Y) - _HG["y0"]) / GRID_M
    i = np.clip(np.floor(fx).astype(int), 0, _HG["nx"] - 2); j = np.clip(np.floor(fy).astype(int), 0, _HG["ny"] - 2)
    u = np.clip(fx - i, 0, 1); v = np.clip(fy - j, 0, 1)
    h = G[i, j] * (1 - u) * (1 - v) + G[i + 1, j] * u * (1 - v) + G[i, j + 1] * (1 - u) * v + G[i + 1, j + 1] * u * v
    out = (fx < 0) | (fy < 0) | (fx >= _HG["nx"] - 1) | (fy >= _HG["ny"] - 1)
    return np.where(out, 0.0, h)

def ground_z(x, y, frame=None):
    """Ground height at (x, y) given in a SET frame ("shig" | "trost"): world relief outside the cores (for scenes
    that build their own terrain, e.g. render_interlude: put camps / props on this outside your cores)."""
    o = SET_ORIGIN[frame or active_frame()]
    return world_height(x + o[0], y + o[1])

def _mat(name, col, rough=0.9):
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]; b.inputs["Base Color"].default_value = (*col, 1); b.inputs["Roughness"].default_value = rough
    return m

def _mr(N, Ln, sock, a, b, c=0.0, d=1.0):
    n = N.new("ShaderNodeMapRange"); n.inputs["From Min"].default_value = a; n.inputs["From Max"].default_value = b
    n.inputs["To Min"].default_value = c; n.inputs["To Max"].default_value = d
    Ln.new(sock, n.inputs["Value"]); return n.outputs["Result"]

def _mix(N, Ln, fac, A, B, blend="MIX"):
    n = N.new("ShaderNodeMix"); n.data_type = "RGBA"; n.blend_type = blend
    for sock, v in ((n.inputs["Factor"], fac), (n.inputs["A"], A), (n.inputs["B"], B)):
        if isinstance(v, (int, float)):
            sock.default_value = v
        elif isinstance(v, tuple):
            sock.default_value = v
        else:
            Ln.new(v, sock)
    return n.outputs["Result"]

def _math(N, Ln, op, a, b=None):
    n = N.new("ShaderNodeMath"); n.operation = op
    for k, x in enumerate((a, b)):
        if x is None:
            continue
        if isinstance(x, (int, float)):
            n.inputs[k].default_value = x
        else:
            Ln.new(x, n.inputs[k])
    return n.outputs[0]

def ground_mat():
    """walls_map_ref.png look, in root object space (= world metres): mostly meadow green with soft large-scale colour
    variation and darker woodland patches; along the N-S corridor (the river / road between the towns) and round the
    towns and Mitras, long rectangular STRIP FIELDS running along the road (as march846's runtime farmland), with thin
    soft hedgerows on the band edges.  No cell outlines."""
    m = bpy.data.materials.new("WD_Ground"); m.use_nodes = True
    nt = m.node_tree; N = nt.nodes; Ln = nt.links
    b = N["Principled BSDF"]; b.inputs["Roughness"].default_value = 0.95
    tc = N.new("ShaderNodeTexCoord"); P = tc.outputs["Object"]
    sep = N.new("ShaderNodeSeparateXYZ"); Ln.new(P, sep.inputs[0]); X, Y = sep.outputs["X"], sep.outputs["Y"]
    # meadow: two greens + a dry tone on big soft noise, plus mid-scale mottling
    n1 = N.new("ShaderNodeTexNoise"); n1.inputs["Scale"].default_value = 1 / 6000.0; n1.inputs["Detail"].default_value = 3
    Ln.new(P, n1.inputs["Vector"])
    n2 = N.new("ShaderNodeTexNoise"); n2.inputs["Scale"].default_value = 1 / 700.0; n2.inputs["Detail"].default_value = 4
    Ln.new(P, n2.inputs["Vector"])
    cr = N.new("ShaderNodeValToRGB"); e = cr.color_ramp.elements
    e[0].position = 0.30; e[0].color = (0.13, 0.25, 0.05, 1); e[1].position = 0.72; e[1].color = (0.30, 0.36, 0.11, 1)
    x_ = e.new(0.5); x_.color = (0.19, 0.31, 0.07, 1)
    Ln.new(n1.outputs["Fac"], cr.inputs["Fac"])
    meadow = _mix(N, Ln, _mr(N, Ln, n2.outputs["Fac"], 0.35, 0.65, 0.0, 0.18), cr.outputs["Color"], (0.10, 0.20, 0.04, 1))
    n6 = N.new("ShaderNodeTexNoise"); n6.inputs["Scale"].default_value = 1 / 2600.0; n6.inputs["Detail"].default_value = 4
    Ln.new(P, n6.inputs["Vector"])
    meadow = _mix(N, Ln, _mr(N, Ln, n6.outputs["Fac"], 0.66, 0.72, 0.0, 0.7), meadow, (0.40, 0.35, 0.15, 1))   # a few ochre patches
    # woodland: darker soft patches (the forest cones stand on most of them)
    n3 = N.new("ShaderNodeTexNoise"); n3.inputs["Scale"].default_value = 1 / 1800.0; n3.inputs["Detail"].default_value = 5
    Ln.new(P, n3.inputs["Vector"])
    meadow = _mix(N, Ln, _mr(N, Ln, n3.outputs["Fac"], 0.64, 0.70, 0.0, 0.85), meadow, (0.05, 0.12, 0.035, 1))
    # strip fields: bands of BAND m along y (the road axis) cut across x into strips of STRIP m, per-band offset
    BAND, STRIP = 300.0, 70.0
    ia = _math(N, Ln, "FLOOR", _math(N, Ln, "DIVIDE", Y, BAND))
    w1 = N.new("ShaderNodeTexWhiteNoise"); w1.noise_dimensions = "1D"; Ln.new(ia, w1.inputs["W"])
    jf = _math(N, Ln, "ADD", _math(N, Ln, "DIVIDE", X, STRIP), _math(N, Ln, "MULTIPLY", w1.outputs["Value"], 7.0))
    jb = _math(N, Ln, "FLOOR", jf)
    cmb = N.new("ShaderNodeCombineXYZ"); Ln.new(ia, cmb.inputs["X"]); Ln.new(jb, cmb.inputs["Y"])
    w2 = N.new("ShaderNodeTexWhiteNoise"); w2.noise_dimensions = "3D"; Ln.new(cmb.outputs[0], w2.inputs["Vector"])
    pal = N.new("ShaderNodeValToRGB"); pal.color_ramp.interpolation = "CONSTANT"; pe = pal.color_ramp.elements
    cols = [(0.0, (0.36, 0.33, 0.14)), (0.16, (0.17, 0.28, 0.06)), (0.30, (0.27, 0.21, 0.11)), (0.44, (0.44, 0.40, 0.18)),
            (0.58, (0.21, 0.31, 0.08)), (0.72, (0.30, 0.33, 0.12)), (0.86, (0.15, 0.25, 0.05))]
    pe[0].position, pe[0].color = cols[0][0], (*cols[0][1], 1)
    pe[1].position, pe[1].color = cols[1][0], (*cols[1][1], 1)
    for pp, cc in cols[2:]:
        x_ = pe.new(pp); x_.color = (*cc, 1)
    Ln.new(w2.outputs["Value"], pal.inputs["Fac"])
    fa = _math(N, Ln, "FRACT", _math(N, Ln, "DIVIDE", Y, BAND))
    ea = _math(N, Ln, "MULTIPLY", _math(N, Ln, "MINIMUM", fa, _math(N, Ln, "SUBTRACT", 1.0, fa)), BAND)
    hedge = _mr(N, Ln, ea, 1.0, 3.0, 0.55, 0.0)                        # soft 2-3 m hedgerow on the band edges
    fb = _math(N, Ln, "FRACT", jf)
    eb = _math(N, Ln, "MULTIPLY", _math(N, Ln, "MINIMUM", fb, _math(N, Ln, "SUBTRACT", 1.0, fb)), STRIP)
    furrow = _mr(N, Ln, eb, 0.3, 0.9, 0.12, 0.0)                       # faint strip boundaries (not lines)
    fields = _mix(N, Ln, furrow, pal.outputs["Color"], (0.12, 0.17, 0.06, 1))
    fields = _mix(N, Ln, hedge, fields, (0.05, 0.10, 0.035, 1))
    # where the farmland is: the corridor along x ~ 0..500 (river + road), wide rings round the towns and Mitras,
    # broken up by noise so the edge is ragged; woods win over fields
    ty = SET_ORIGIN["trost"][1]
    d_ax = _math(N, Ln, "ABSOLUTE", _math(N, Ln, "SUBTRACT", X, 200.0))
    corr = _mr(N, Ln, d_ax, 1500.0, 900.0)       # ~1-1.5 km either side of the river/road axis
    ylim = _math(N, Ln, "MULTIPLY", _mr(N, Ln, Y, SEA_Y + 1000, SEA_Y + 2500), _mr(N, Ln, Y, MITRAS[1] + 3000, MITRAS[1] - 500))
    corr = _math(N, Ln, "MULTIPLY", corr, ylim)
    acc = corr
    for cx, cy, r in ((0.0, -300.0, 2600.0), (0.0, ty - 400.0, 2400.0), (MITRAS[0], MITRAS[1], 2800.0)):   # ~1-2 km rims
        vm = N.new("ShaderNodeVectorMath"); vm.operation = "DISTANCE"; vm.inputs[1].default_value = (cx, cy, 0.0)
        Ln.new(P, vm.inputs[0])
        acc = _math(N, Ln, "MAXIMUM", acc, _mr(N, Ln, vm.outputs["Value"], r, r * 0.6))
    n4 = N.new("ShaderNodeTexNoise"); n4.inputs["Scale"].default_value = 1 / 2200.0; n4.inputs["Detail"].default_value = 3
    Ln.new(P, n4.inputs["Vector"])
    rag = _mr(N, Ln, n4.outputs["Fac"], 0.38, 0.46)
    fm = _math(N, Ln, "MULTIPLY", _math(N, Ln, "MULTIPLY", acc, rag), _mr(N, Ln, n3.outputs["Fac"], 0.66, 0.60))
    col = _mix(N, Ln, fm, meadow, fields)
    # very fine grain
    n5 = N.new("ShaderNodeTexNoise"); n5.inputs["Scale"].default_value = 1 / 15.0
    Ln.new(P, n5.inputs["Vector"])
    # height tint (object Z = metres): darker, cooler valleys, lighter dry crests
    sepz = N.new("ShaderNodeSeparateXYZ"); Ln.new(P, sepz.inputs[0])
    col = _mix(N, Ln, _mr(N, Ln, sepz.outputs["Z"], 12.0, 0.0, 0.0, 0.32), col, (0.07, 0.15, 0.06, 1))
    col = _mix(N, Ln, _mr(N, Ln, sepz.outputs["Z"], 35.0, 140.0, 0.0, 0.38), col, (0.42, 0.45, 0.22, 1))
    geo = N.new("ShaderNodeNewGeometry"); sz_ = N.new("ShaderNodeSeparateXYZ"); Ln.new(geo.outputs["Normal"], sz_.inputs[0])
    col = _mix(N, Ln, _mr(N, Ln, sz_.outputs["Z"], 0.9993, 0.975, 0.0, 0.55), col, (0.035, 0.07, 0.025, 1))   # darker slopes
    bc = N.new("ShaderNodeBrightContrast"); Ln.new(col, bc.inputs["Color"])
    Ln.new(_mr(N, Ln, n5.outputs["Fac"], 0.0, 1.0, -0.035, 0.035), bc.inputs["Bright"])
    Ln.new(_aerial(N, Ln, bc.outputs["Color"]), b.inputs["Base Color"])
    return m

HAZE_RGB = tuple(float(v) for v in os.environ.get("WORLD_AERIAL_RGB", "0.60,0.70,0.84").split(","))
def _aerial(N, Ln, col):
    """Gentle aerial perspective: blend toward the haze colour with camera distance (helps the far hills read)."""
    cd = N.new("ShaderNodeCameraData")
    f = _mr(N, Ln, cd.outputs["View Distance"], float(os.environ.get("WORLD_AERIAL_NEAR", "1500")),
            float(os.environ.get("WORLD_AERIAL_FAR", "70000")), 0.0, float(os.environ.get("WORLD_AERIAL_MAX", "0.35")))
    geo = N.new("ShaderNodeNewGeometry"); sp = N.new("ShaderNodeSeparateXYZ"); Ln.new(geo.outputs["Incoming"], sp.inputs[0])
    az_ = N.new("ShaderNodeMath"); az_.operation = "ABSOLUTE"; Ln.new(sp.outputs["Z"], az_.inputs[0])
    slant = _mr(N, Ln, az_.outputs[0], 0.55, 0.12, 0.0, 1.0)          # steep (top-down) rays cross little air
    f = _math(N, Ln, "MULTIPLY", f, slant)
    return _mix(N, Ln, f, col, (*HAZE_RGB, 1))

def add_aerial(m):
    """Put the distance haze into a Principled material's base colour (vegetation, farmsteads)."""
    nt = m.node_tree; N = nt.nodes; Ln = nt.links; b = N.get("Principled BSDF")
    if b is None:
        return m
    src = b.inputs["Base Color"].links[0].from_socket if b.inputs["Base Color"].links else None
    if src is None:
        rgb = N.new("ShaderNodeRGB"); rgb.outputs[0].default_value = tuple(b.inputs["Base Color"].default_value); src = rgb.outputs[0]
    Ln.new(_aerial(N, Ln, src), b.inputs["Base Color"])
    return m

def _blended(m):
    for attr, val in (("surface_render_method", "BLENDED"), ("blend_method", "BLEND")):
        try:
            setattr(m, attr, val)
        except Exception:
            pass

def far_band_mat(name, col, near=5000.0, far=14000.0, alpha=1.0):
    """Shown only far from the camera (camera distance fade): readable rings/districts from high up, invisible in the
    low sky shots and at every seam frame (cameras there are < 2 km from the ground they see)."""
    m = bpy.data.materials.new(name); m.use_nodes = True; _blended(m)
    nt = m.node_tree; N = nt.nodes; Ln = nt.links
    out = N["Material Output"]; b = N["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*col, 1); b.inputs["Roughness"].default_value = 0.9
    cd = N.new("ShaderNodeCameraData")
    f = _mr(N, Ln, cd.outputs["View Distance"], near, far, 0.0, alpha)
    tr = N.new("ShaderNodeBsdfTransparent")
    mx = N.new("ShaderNodeMixShader"); Ln.new(f, mx.inputs[0]); Ln.new(tr.outputs[0], mx.inputs[1]); Ln.new(b.outputs[0], mx.inputs[2])
    Ln.new(mx.outputs[0], out.inputs["Surface"])
    return m

def haze_mat():
    """Horizon haze curtain: sky-coloured emission, opaque at the ground, fading out by ~4 km up."""
    m = bpy.data.materials.new("WD_HorizonHaze"); m.use_nodes = True; _blended(m)
    nt = m.node_tree; N = nt.nodes; Ln = nt.links
    out = N["Material Output"]
    for n in list(N):
        if n != out:
            N.remove(n)
    tc = N.new("ShaderNodeTexCoord"); sep = N.new("ShaderNodeSeparateXYZ"); Ln.new(tc.outputs["Object"], sep.inputs[0])
    a = _mr(N, Ln, sep.outputs["Z"], 0.0, float(os.environ.get("WORLD_HAZE_H", "5000")), 1.0, 0.0)
    a = _math(N, Ln, "POWER", a, 2.2)
    em = N.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = tuple(float(v) for v in os.environ.get("WORLD_HAZE_RGB", "0.64,0.76,0.93").split(",")) + (1,)
    em.inputs["Strength"].default_value = float(os.environ.get("WORLD_HAZE_E", "0.9"))
    tr = N.new("ShaderNodeBsdfTransparent")
    mx = N.new("ShaderNodeMixShader"); Ln.new(a, mx.inputs[0]); Ln.new(tr.outputs[0], mx.inputs[1]); Ln.new(em.outputs[0], mx.inputs[2])
    Ln.new(mx.outputs[0], out.inputs["Surface"])
    return m

def _strip(bm, pts, width, z, hz=False):
    """Ribbon along a polyline (river / road / track); hz: z is an offset above the world relief."""
    left, right = [], []
    for i, p in enumerate(pts):
        a, c = pts[max(0, i - 1)], pts[min(len(pts) - 1, i + 1)]
        d = Vector((c[0] - a[0], c[1] - a[1])).normalized(); n = Vector((-d.y, d.x)) * width / 2
        zl = z + (world_height(p[0] + n.x, p[1] + n.y) if hz else 0.0)
        zr = z + (world_height(p[0] - n.x, p[1] - n.y) if hz else 0.0)
        left.append(bm.verts.new((p[0] + n.x, p[1] + n.y, zl))); right.append(bm.verts.new((p[0] - n.x, p[1] - n.y, zr)))
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
            f = bm.faces.new((r0[k], r0[(k + 1) % 4], r1[(k + 1) % 4], r1[k]))
            f.material_index = 1 if k == 2 else 0       # the walk on top: pale stone (reads from high up)

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
                if abs(xs) < join and abs(y - o[1]) < 3000:           # inside the set's own wall stretch
                    if len(cur) > 1:
                        seg.append(cur)
                    cur = []; continue
                w = _smooth(join, join + 3500.0, abs(xs)) if abs(y - o[1]) < 3000 else 1.0
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
        rad = [(Vector(c), r) for c, r in cores]       # keep only faces wholly inside a core (terrain is 0 at the rim)
        kill = [f for f in bm.faces if not any(all((v.co.to_2d() - c).length < r for v in f.verts) for c, r in rad)]
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

# ---------------------------------------------------------------- vegetation / farmsteads (instanced, low-poly)
def _proto(name, kind, col, coll):
    bm = bmesh.new()
    if kind == "conifer":                     # 7-vert cone (unit height)
        base = [bm.verts.new((0.30 * math.cos(k * math.tau / 6), 0.30 * math.sin(k * math.tau / 6), 0.12)) for k in range(6)]
        top = bm.verts.new((0, 0, 1.0))
        for k in range(6):
            bm.faces.new((base[k], base[(k + 1) % 6], top))
        bm.faces.new(base[::-1])
    else:                                     # broadleaf: low-poly blob (octahedron-ish, 8 verts), unit height
        ring = [bm.verts.new((0.42 * math.cos(k * math.tau / 6), 0.42 * math.sin(k * math.tau / 6), 0.58)) for k in range(6)]
        t, b_ = bm.verts.new((0, 0, 1.0)), bm.verts.new((0, 0, 0.18))
        for k in range(6):
            bm.faces.new((ring[k], ring[(k + 1) % 6], t)); bm.faces.new((ring[(k + 1) % 6], ring[k], b_))
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for f in me.polygons:
        f.use_smooth = kind != "conifer"
    me.materials.append(add_aerial(_mat(name + "M", col, 0.85)))
    ob = bpy.data.objects.new(name, me); coll.objects.link(ob); ob.location = (0, 0, -20000.0)
    return ob

# Vegetation level of detail, the SAME in every scene so seam frames still match:
#   WORLD_LOD=preview (default for 15 fps previews): trees thinned by distance from the active camera (full density
#   within WORLD_LOD_NEAR = 3500 m, none beyond WORLD_LOD_FAR = 6000 m; the forest-floor tint carries the far woods)
#   WORLD_LOD=final   (default when FPS >= 24 is exported): every tree.
LOD = os.environ.get("WORLD_LOD") or ("final" if float(os.environ.get("FPS", "15") or 15) >= 24 else "preview")
LOD_NEAR = float(os.environ.get("WORLD_LOD_NEAR", "3500")); LOD_FAR = float(os.environ.get("WORLD_LOD_FAR", "6000"))

def _scatter_gn(proto):
    nm = "WD_Scatter_" + proto.name + "_" + LOD
    ng = bpy.data.node_groups.get(nm)
    if ng:
        return ng
    ng = bpy.data.node_groups.new(nm, "GeometryNodeTree")
    ng.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    N = ng.nodes; Ln = ng.links
    gi, go = N.new("NodeGroupInput"), N.new("NodeGroupOutput")
    oi = N.new("GeometryNodeObjectInfo"); oi.transform_space = "ORIGINAL"
    oi.inputs["Object"].default_value = proto
    m2p = N.new("GeometryNodeMeshToPoints"); Ln.new(gi.outputs["Geometry"], m2p.inputs["Mesh"])
    pts = m2p.outputs["Points"]
    if LOD == "preview":
        # distance thinning from the ACTIVE camera (same rule in every scene -> seam frames still match): full density
        # within LOD_NEAR, thinning to 0 by LOD_FAR (the darker forest-floor patches carry the far woods)
        ac = N.new("GeometryNodeInputActiveCamera")
        ci = N.new("GeometryNodeObjectInfo"); ci.transform_space = "RELATIVE"; Ln.new(ac.outputs[0], ci.inputs["Object"])
        pos = N.new("GeometryNodeInputPosition")
        dist = N.new("ShaderNodeVectorMath"); dist.operation = "DISTANCE"
        Ln.new(pos.outputs[0], dist.inputs[0]); Ln.new(ci.outputs["Location"], dist.inputs[1])
        keep = N.new("ShaderNodeMapRange"); keep.inputs["From Min"].default_value = LOD_NEAR; keep.inputs["From Max"].default_value = LOD_FAR
        keep.inputs["To Min"].default_value = 1.0; keep.inputs["To Max"].default_value = 0.0
        Ln.new(dist.outputs["Value"], keep.inputs["Value"])
        rnd = N.new("FunctionNodeRandomValue"); rnd.data_type = "FLOAT"; rnd.inputs["Seed"].default_value = 846
        cmp_ = N.new("FunctionNodeCompare"); cmp_.data_type = "FLOAT"; cmp_.operation = "GREATER_THAN"
        Ln.new(rnd.outputs[0], cmp_.inputs[0]); Ln.new(keep.outputs["Result"], cmp_.inputs[1])
        dg = N.new("GeometryNodeDeleteGeometry"); dg.domain = "POINT"
        Ln.new(pts, dg.inputs["Geometry"]); Ln.new(cmp_.outputs["Result"], dg.inputs["Selection"])
        pts = dg.outputs["Geometry"]
    iop = N.new("GeometryNodeInstanceOnPoints"); Ln.new(pts, iop.inputs["Points"])
    Ln.new(oi.outputs["Geometry"], iop.inputs["Instance"])
    sa = N.new("GeometryNodeInputNamedAttribute"); sa.data_type = "FLOAT_VECTOR"; sa.inputs["Name"].default_value = "wd_s"
    ra = N.new("GeometryNodeInputNamedAttribute"); ra.data_type = "FLOAT"; ra.inputs["Name"].default_value = "wd_r"
    cx = N.new("ShaderNodeCombineXYZ"); Ln.new(ra.outputs["Attribute"], cx.inputs["Z"])
    Ln.new(sa.outputs["Attribute"], iop.inputs["Scale"]); Ln.new(cx.outputs[0], iop.inputs["Rotation"])
    Ln.new(iop.outputs["Instances"], go.inputs["Geometry"])
    return ng

def _points(name, P, S, Rz, proto, coll, root):
    """One point mesh (positions P (n,3), scales S (n,3), yaw Rz) instanced with `proto` by geometry nodes."""
    import numpy as np
    me = bpy.data.meshes.new(name); me.vertices.add(len(P))
    me.vertices.foreach_set("co", np.asarray(P, np.float32).ravel())
    a = me.attributes.new("wd_s", "FLOAT_VECTOR", "POINT"); a.data.foreach_set("vector", np.asarray(S, np.float32).ravel())
    b = me.attributes.new("wd_r", "FLOAT", "POINT"); b.data.foreach_set("value", np.asarray(Rz, np.float32).ravel())
    ob = bpy.data.objects.new(name, me); coll.objects.link(ob); ob.parent = root
    md = ob.modifiers.new("Scatter", "NODES"); md.node_group = _scatter_gn(proto)
    for attr in ("visible_volume_scatter",):
        if hasattr(ob, attr):
            setattr(ob, attr, False)
    return ob

def build_vegetation(coll, root, allc, mycores, river, road, M=None):
    """Forest clumps of varied size (denser on the hills and ridges), copses and tree lines along the river, hedgerow
    trees on the strip-field band edges, scattered single trees, a few farmsteads with dirt tracks to the road.
    Deterministic in world coordinates (identical in every scene); instanced by geometry nodes (cheap in Eevee)."""
    import numpy as np
    rng = np.random.default_rng(1845)
    ty = SET_ORIGIN["trost"][1]
    pc = bpy.data.collections.new("WorldProtos"); bpy.context.scene.collection.children.link(pc)
    protos = {"con": _proto("WD_TreeConifer", "conifer", (0.035, 0.10, 0.035), pc),
              "con2": _proto("WD_TreeConifer2", "conifer", (0.05, 0.13, 0.04), pc),
              "brd": _proto("WD_TreeBroad", "broad", (0.08, 0.18, 0.04), pc),
              "brd2": _proto("WD_TreeBroad2", "broad", (0.13, 0.22, 0.05), pc)}
    allr = (R_MARIA, R_ROSE, R_SINA)
    def ok(X, Y, ring_clear=110.0):
        d = np.hypot(X - MITRAS[0], Y - MITRAS[1])
        g = (Y > SEA_Y + 700) & (d < R_MARIA + 14000)
        for r in allr:
            g &= np.abs(d - r) > ring_clear
        for (cx, cy), r in allc:
            g &= np.hypot(X - cx, Y - cy) > r + 150
        g &= np.hypot(X - MITRAS[0], Y - MITRAS[1]) > 1500
        return g
    # river / road proximity (valley floor): distance to the densified polylines via a coarse lookup on y
    rv = np.array(river); rd = np.array(road)
    def near(X, Y, pl, dmax):
        out = np.full(len(X), 1e9)
        for k in range(0, len(pl), 1):
            pass
        idx = np.searchsorted(pl[:, 1], Y) if np.all(np.diff(pl[:, 1]) > 0) else None
        if idx is None:
            for p in pl[::3]:
                out = np.minimum(out, np.hypot(X - p[0], Y - p[1]))
            return out
        for off in (-3, -2, -1, 0, 1, 2):
            j = np.clip(idx + off, 0, len(pl) - 1)
            out = np.minimum(out, np.hypot(X - pl[j, 0], Y - pl[j, 1]))
        return out
    groups = {k: ([], [], []) for k in protos}
    def add(kind, X, Y, H, jitter=0.25, crown=1.9):
        n = len(X)
        Z = world_height_np(X, Y) - 0.5
        hs = H * (1 + rng.uniform(-jitter, jitter, n))
        S = np.stack([hs * crown * rng.uniform(0.85, 1.15, n), hs * crown * rng.uniform(0.85, 1.15, n), hs], 1)
        g = groups[kind]; g[0].append(np.stack([X, Y, Z], 1)); g[1].append(S); g[2].append(rng.uniform(0, math.tau, n))
    R_land = R_MARIA + 12000.0
    # 1) forest clumps, varied size, placed preferentially on hills / ridges
    nc = int(os.environ.get("WORLD_CLUMPS", "1000"))
    a = rng.uniform(0, math.tau, nc * 3); rr = np.sqrt(rng.uniform(0, 1, nc * 3)) * R_land
    CX, CY = MITRAS[0] + np.cos(a) * rr, MITRAS[1] + np.sin(a) * rr
    hgt = world_height_np(CX, CY)
    pkeep = 0.10 + 0.90 * np.clip(hgt / 90.0, 0, 1)
    sel = ok(CX, CY, 300) & (rng.uniform(0, 1, len(CX)) < pkeep)
    CX, CY, hgt = CX[sel][:nc], CY[sel][:nc], hgt[sel][:nc]
    kn = np.array([(k[0], k[1]) for k in _knolls()]) if _knolls() else np.zeros((0, 2))
    if len(kn):
        CX = np.concatenate([CX, kn[:, 0]]); CY = np.concatenate([CY, kn[:, 1]]); hgt = np.concatenate([hgt, world_height_np(kn[:, 0], kn[:, 1])])
    sizes = np.exp(rng.normal(np.log(260), 0.55, len(CX))) * (1 + hgt / 90.0)
    floors = []
    for cx, cy, sz, hh in zip(CX, CY, sizes, hgt):
        n = int(min(1600, 1.2 * sz * sz / 420.0))          # closed canopy (crowns ~11 m radius)
        X = cx + rng.normal(0, sz * 0.5, n); Y = cy + rng.normal(0, sz * 0.38, n)
        g = ok(X, Y)
        X, Y = X[g], Y[g]
        if not len(X):
            continue
        con = rng.uniform(0, 1, len(X)) < (0.35 + 0.5 * min(1.0, hh / 120.0))    # conifers on the higher ground
        bsel = ~con & (rng.uniform(0, 1, len(X)) < 0.8)
        add("con", X[con], Y[con], 21.0); add("brd", X[bsel], Y[bsel], 15.0)
        floors.append((cx, cy, sz))
    # 2) copses + tree lines along the river banks (gaps), 3) scattered single trees in the meadows
    t = np.linspace(0, 1, len(rv))
    for side in (-1, 1):
        d = np.gradient(rv, axis=0); nrm = np.stack([-d[:, 1], d[:, 0]], 1); nrm /= np.linalg.norm(nrm, axis=1, keepdims=True) + 1e-9
        P = rv + nrm * side * rng.uniform(22, 45, (len(rv), 1))
        keep = (rng.uniform(0, 1, len(P)) < 0.55) & ok(P[:, 0], P[:, 1])
        P = P[keep]
        reps = 3
        X = np.repeat(P[:, 0], reps) + rng.normal(0, 14, len(P) * reps); Y = np.repeat(P[:, 1], reps) + rng.normal(0, 14, len(P) * reps)
        add("brd2", X, Y, 13.0)
    ns = int(os.environ.get("WORLD_SINGLES", "50000"))
    a = rng.uniform(0, math.tau, ns); rr = np.sqrt(rng.uniform(0, 1, ns)) * R_land
    X, Y = MITRAS[0] + np.cos(a) * rr, MITRAS[1] + np.sin(a) * rr
    g = ok(X, Y)
    X, Y = X[g], Y[g]
    half = rng.uniform(0, 1, len(X)) < 0.7
    add("brd", X[half], Y[half], 12.0, 0.35); add("con2", X[~half], Y[~half], 16.0, 0.35)
    # 4) hedgerow trees on the strip-field band edges (y = k * 300) inside the field bands (valley + town rims)
    hx, hy = [], []
    for kb in range(int((SEA_Y + 2500) / 300), int((MITRAS[1] + 3000) / 300)):
        y = kb * 300.0
        xs = np.arange(-1700.0, 2100.0, 11.0) + valley_x(y) - 200.0
        run = (np.floor(xs / 90.0 + kb * 0.37) % 3) != 0                      # broken hedges: 2/3 planted
        hx.append(xs[run]); hy.append(np.full(run.sum(), y))
    X, Y = np.concatenate(hx), np.concatenate(hy)
    g = ok(X, Y) & (near(X, Y, rv, 60) > 40) & (near(X, Y, rd, 30) > 20) & (rng.uniform(0, 1, len(X)) < 0.75)
    add("brd2", X[g] + rng.normal(0, 2, g.sum()), Y[g] + rng.normal(0, 2, g.sum()), 9.0, 0.3)
    for k, (Ps, Ss, Rs) in groups.items():
        if Ps:
            _points("WD_Trees_" + k, np.concatenate(Ps), np.concatenate(Ss), np.concatenate(Rs), protos[k], coll, root)
    STATE["trees"] = int(sum(sum(len(p) for p in g[0]) for g in groups.values()))
    # darker forest floor under the clumps (irregular 14-gons on the relief)
    bm = bmesh.new()
    for cx, cy, sz in floors:
        ring = []
        for k in range(14):
            an = k * math.tau / 14; rr_ = sz * (0.75 + 0.25 * noise.noise(Vector((cx / 97 + k, cy / 89, 0.5))))
            x, y = cx + math.cos(an) * rr_ * 1.05, cy + math.sin(an) * rr_ * 0.8
            ring.append(bm.verts.new((x, y, world_height(x, y) - 0.15)))
        bm.faces.new(ring)
    me = bpy.data.meshes.new("WD_ForestFloor"); bm.to_mesh(me); bm.free(); me.materials.append(add_aerial(_mat("WD_ForestFloorM", (0.07, 0.14, 0.045), 0.95)))
    ob = bpy.data.objects.new("WD_ForestFloor", me); coll.objects.link(ob); ob.parent = root
    # 5) farmsteads near the strip bands + dirt tracks to the road
    rb = random.Random(1846)
    bm = bmesh.new(); bt = bmesh.new()
    roofm = _mat("WD_FarmRoof", (0.36, 0.15, 0.07), 0.85); wallm = _mat("WD_FarmWall", (0.70, 0.64, 0.52), 0.9)
    nf = 0
    for k in range(400):
        y = rb.uniform(SEA_Y + 3000, MITRAS[1] - 3500)
        x = valley_x(y) + rb.choice((-1, 1)) * rb.uniform(800, 1600)
        if not ok(np.array([x]), np.array([y]), 400)[0]:
            continue
        z0 = world_height(x, y)
        yaw = rb.uniform(0, math.pi)
        for b_ in range(rb.randint(2, 4)):                    # barn + house + sheds round a yard
            w, dd, hh = rb.uniform(7, 12), rb.uniform(12, 22), rb.uniform(5, 8)
            ox, oy = rb.uniform(-25, 25), rb.uniform(-25, 25)
            cx_, cy_ = x + ox * math.cos(yaw) - oy * math.sin(yaw), y + ox * math.sin(yaw) + oy * math.cos(yaw)
            ca, sa = math.cos(yaw + b_ * math.pi / 2), math.sin(yaw + b_ * math.pi / 2)
            def P(u, v, z):
                return bm.verts.new((cx_ + u * ca - v * sa, cy_ + u * sa + v * ca, z0 + z))
            q = [P(-w / 2, -dd / 2, -1), P(w / 2, -dd / 2, -1), P(w / 2, dd / 2, -1), P(-w / 2, dd / 2, -1)]
            t_ = [P(-w / 2, -dd / 2, hh), P(w / 2, -dd / 2, hh), P(w / 2, dd / 2, hh), P(-w / 2, dd / 2, hh)]
            r_ = [P(0, -dd / 2, hh + w * 0.45), P(0, dd / 2, hh + w * 0.45)]
            for i_ in range(4):
                bm.faces.new((q[i_], q[(i_ + 1) % 4], t_[(i_ + 1) % 4], t_[i_]))
            f1 = bm.faces.new((t_[0], t_[1], r_[0])); f2 = bm.faces.new((t_[2], t_[3], r_[1]))
            f3 = bm.faces.new((t_[1], t_[2], r_[1], r_[0])); f4 = bm.faces.new((t_[3], t_[0], r_[0], r_[1]))
            for f in (f3, f4):
                f.material_index = 1
        # dirt track from the yard to the valley road (gently winding)
        xr = valley_x(y) - 200.0 if x < valley_x(y) else valley_x(y) + 50.0
        pts = [(x + (xr - x) * u + 60 * math.sin(u * 5 + k), y + 80 * math.sin(u * 3 + k * 0.7)) for u in np.linspace(0, 1, 18)]
        _strip(bt, pts, 4.0, 0.06, hz=True)
        nf += 1
        if nf >= int(os.environ.get("WORLD_FARMS", "70")):
            break
    me = bpy.data.meshes.new("WD_Farmsteads"); bm.to_mesh(me); bm.free(); me.materials.append(wallm); me.materials.append(roofm)
    ob = bpy.data.objects.new("WD_Farmsteads", me); coll.objects.link(ob); ob.parent = root
    me = bpy.data.meshes.new("WD_Tracks"); bt.to_mesh(me); bt.free(); me.materials.append((M or {}).get("dirt") or _mat("WD_Dirt", (0.24, 0.20, 0.13), 0.95))
    ob = bpy.data.objects.new("WD_Tracks", me); coll.objects.link(ob); ob.parent = root
    STATE["farms"] = nf

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
    # ---- ground: 300 m cells with the relief over the land, 4 km flat skirt beyond; cells wholly inside this scene's
    #      cores are left to the local terrain (which fades to 0 at the core rim, where the relief is 0 too)
    gm = ground_mat()
    bm = bmesh.new()
    ix0, ix1 = -R_MARIA - 16000.0, R_MARIA + 16000.0
    iy0, iy1 = SEA_Y - 600.0, MITRAS[1] + R_MARIA + 16000.0
    cell = float(os.environ.get("WORLD_CELL", "200"))
    nx, ny = int((ix1 - ix0) / cell), int((iy1 - iy0) / cell)
    ix1, iy1 = ix0 + nx * cell, iy0 + ny * cell
    V = {}
    def vert(i, j):
        if (i, j) not in V:
            x, y = ix0 + i * cell, iy0 + j * cell
            V[(i, j)] = bm.verts.new((x, y, world_height(x, y) - 0.4))
        return V[(i, j)]
    for i in range(nx):
        for j in range(ny):
            cx_, cy_ = ix0 + (i + 0.5) * cell, iy0 + (j + 0.5) * cell
            if any(math.hypot(cx_ - c[0], cy_ - c[1]) + cell * 0.71 < 0.8 * r for c, r in mycores):
                continue
            f = bm.faces.new((vert(i, j), vert(i + 1, j), vert(i + 1, j + 1), vert(i, j + 1)))
            f.smooth = True
    sk = 4000.0
    X0, X1, Y1 = ix0 - 100000.0, ix1 + 100000.0, iy1 + 100000.0
    def quad(a, b, c, d):
        bm.faces.new([bm.verts.new((x, y, -0.4)) for x, y in (a, b, c, d)])
    quad((X0, iy0), (ix0, iy0), (ix0, Y1), (X0, Y1)); quad((ix1, iy0), (X1, iy0), (X1, Y1), (ix1, Y1))
    quad((ix0, iy1), (ix1, iy1), (ix1, Y1), (ix0, Y1))
    put("WD_Ground", bm, [gm])
    x0, x1 = X0, X1
    # ---- the sea: from a wavy coastline south to the clip distance
    bm = bmesh.new()
    xs = [x0 - 60000 + k * 800.0 for k in range(int((x1 - x0 + 120000) / 800) + 1)]
    coast = [bm.verts.new((x, SEA_Y + 380 * noise.noise(Vector((x / 5200, 0.3, 1.1))) + 160 * noise.noise(Vector((x / 900, 2.1, 0.4))), -0.05)) for x in xs]
    coast_xy = [(v.co.x, v.co.y) for v in coast]
    far = [bm.verts.new((x, SEA_Y - 200000, -0.05)) for x in xs]
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
                # a pale band drawn at wall-top height, faded in only beyond ~4-16 km camera distance (far_band_mat)
                run = []
                for p in pts + [None]:
                    if p is not None and not any(math.hypot(p[0] - c[0], p[1] - c[1]) < 0.7 * rr for c, rr in mycores):
                        run.append(p); continue
                    if len(run) > 1:
                        _strip(ba, run, float(os.environ.get('WORLD_BAND_W', '320')), 51.0)
                    run = []
            if kind != "arc":
                if (ring_name in ("maria", "rose")) and kind[2] == 0:
                    carpets.append((ring_name, pts))
                elif not any(math.hypot(pts[len(pts) // 2][0] - c[0], pts[len(pts) // 2][1] - c[1]) < 1.2 * rr for c, rr in mycores):
                    bd.faces.new([bd.verts.new((x, y, -0.2)) for x, y in pts])      # empty district: a bare yard
    put("WD_Walls", bm, [stone, _mat("WD_WallTop", (0.80, 0.77, 0.68), 0.8)])
    ap_ = put("WD_WallApron", ba, [far_band_mat("WD_Apron", (0.82, 0.79, 0.70), near=4000.0, far=16000.0, alpha=0.9)])
    for attr in ("visible_shadow", "visible_diffuse", "visible_glossy", "visible_transmission", "visible_volume_scatter"):
        if hasattr(ap_, attr):
            setattr(ap_, attr, False)
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
        _strip(bm, s_, 26.0, 0.05, hz=True)
    put("WD_River", bm, [water])
    bm = bmesh.new()
    for s_ in keep(road, 0.75):
        _strip(bm, s_, 9.0, 0.02, hz=True)
    put("WD_Road", bm, [(M or {}).get("dirt") or _mat("WD_Dirt", (0.24, 0.20, 0.13), 0.95)])
    STATE["river"], STATE["road"] = river, road
    build_vegetation(coll, root, allc, mycores, river, road, M)
    # ---- horizon haze curtain: a 64-gon cylinder round Mitras (R_MARIA + 45 km), sky-coloured, opaque at the ground
    #      and fading by ~4.5 km up; it hides every ground / sea edge and gives the far coastline its aerial perspective
    #      OPT-IN (WORLD_HAZE=1): in the QA stills the scene's own haze volume + ground/sea running out to the 140 km clip
    #      gave the cleaner horizon; the curtain left a grey band where its emission met the sky.
    bm = bmesh.new(); RH = R_MARIA + float(os.environ.get("WORLD_HAZE_R", "45000")); n_ = 64
    lo = [bm.verts.new((MITRAS[0] + RH * math.cos(k * math.tau / n_), MITRAS[1] + RH * math.sin(k * math.tau / n_), -50.0)) for k in range(n_)]
    hi = [bm.verts.new((v.co.x, v.co.y, 9000.0)) for v in lo]
    for k in range(n_):
        bm.faces.new((lo[k], lo[(k + 1) % n_], hi[(k + 1) % n_], hi[k]))
    hz = put("WD_HorizonHaze", bm, [haze_mat()])
    hz.hide_render = os.environ.get("WORLD_HAZE", "0") != "1"
    for attr in ("visible_shadow", "visible_diffuse", "visible_glossy", "visible_transmission", "visible_volume_scatter"):
        if hasattr(hz, attr):
            setattr(hz, attr, False)
    # flight.py's cloud deck (FL_Clouds, 56 km) used to end behind the mountains; now its edge would show as a grey band
    # above the horizon: grow the mesh (not the object, so the cloud pattern keeps its size) past the haze curtain
    cl = bpy.data.objects.get("FL_Clouds")
    if cl is not None and cl.type == "MESH":
        k_ = float(os.environ.get("WORLD_CLOUD_GROW", "7"))
        cen = sum((v.co for v in cl.data.vertices), Vector()) / max(1, len(cl.data.vertices))
        for v in cl.data.vertices:
            v.co = cen + (v.co - cen) * Vector((k_, k_, 1.0))
        cl.data.update()
    # scene.py's "Haze" volume box ends 18 km out: its edge read as a grey band over the horizon. Stretch it past the
    # haze curtain (centred on this scene's origin) so the aerial perspective just keeps deepening with distance.
    for hb in [o for o in bpy.data.objects if o.name.startswith("Haze") and o.type == "MESH"]:
        hb.scale = (float(os.environ.get("WORLD_HAZE_BOX", "95000")), float(os.environ.get("WORLD_HAZE_BOX", "95000")), hb.scale[2])
    # camera clip: the sea and the far rings must stay inside it
    for ob in sc.objects:
        if ob.type == "CAMERA":
            ob.data.clip_end = max(ob.data.clip_end, float(os.environ.get("WORLD_CLIP", "140000")))
    print(f"[world] frame {frame}, K {K}: Maria {R_MARIA / 1000:.1f} km, Rose {R_ROSE / 1000:.1f}, Sina {R_SINA / 1000:.1f}; "
          f"Trost frame at world y {SET_ORIGIN['trost'][1]:.0f}; cores {cores}", flush=True)
    return root

# ---------------------------------------------------------------- the SHARED LIGHT RIG (identical light at every seam)
LIGHT_PRESETS = {
    # name: sun elevation, azimuth (deg, scene.py convention: direction the light comes FROM, 0 = east, 90 = north),
    #       sun colour, sun energy, sky-light strength (world Background for non-camera rays), exposure
    "day":      dict(el=40.0, az=160.0, col=(1.0, 0.97, 0.92), e=3.6, amb=0.25, expo=-1.5),
    "low_sun":  dict(el=20.0, az=235.0, col=(1.0, 0.90, 0.76), e=3.8, amb=0.22, expo=-1.4),
    "sunset":   dict(el=4.0, az=245.0, col=(1.0, 0.50, 0.20), e=4.2, amb=0.18, expo=-1.5),
    "night":    dict(el=-12.0, az=245.0, col=(0.55, 0.65, 1.0), e=0.06, amb=0.03, expo=-0.3),
}

def light_rig(spec="day", exclusive=True, **over):
    """Set THE light of the scene from a preset (or a dict) + overrides; call it in every scene at a seam with the
    same arguments and the light matches.  Drives: the object "Sun" (created if missing; it is what scene.py,
    flight.py and the agents' scripts use), the world's Sky Texture sun angles, the lighting-sky Background strength,
    and the view exposure.  exclusive=True turns off every other SUN light (e.g. flight.py's FL_Fill, set rigs), which
    otherwise make scenes differ.  A time-of-day ramp is just light_rig(blend(a, b, u)) - see light_blend().
    Returns the dict that was applied."""
    P = dict(LIGHT_PRESETS[spec]) if isinstance(spec, str) else dict(spec)
    P.update(over)
    sc = bpy.context.scene
    so = bpy.data.objects.get("Sun")
    if so is None or so.type != "LIGHT":
        ld = bpy.data.lights.new("Sun", "SUN"); so = bpy.data.objects.new("Sun", ld); sc.collection.objects.link(so)
    so.animation_data_clear(); so.constraints.clear() if hasattr(so, "constraints") else None
    el, az = math.radians(P["el"]), math.radians(P["az"])
    d = Vector((-math.cos(el) * math.cos(az), -math.cos(el) * math.sin(az), -math.sin(el)))
    so.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    so.data.color = tuple(P["col"]); so.data.energy = P["e"]
    so.hide_render = False
    if exclusive:
        for o in bpy.data.objects:
            if o.type == "LIGHT" and o.data.type == "SUN" and o is not so:
                o.hide_render = True
    w = sc.world
    if w and w.use_nodes:
        for n in w.node_tree.nodes:
            if n.type == "TEX_SKY":
                try:
                    n.sun_elevation = max(0.0, el); n.sun_rotation = az          # flight.py convention
                except Exception:
                    pass
            if n.type == "BACKGROUND" and n.inputs[1].default_value < 1.0:     # the lighting sky (not the camera one)
                n.inputs[1].default_value = P["amb"]
    sc.view_settings.exposure = P["expo"]
    STATE["light"] = P
    return P

def light_blend(a, b, u):
    """Interpolate two light specs (names or dicts) for time-of-day ramps across a flight."""
    A = dict(LIGHT_PRESETS[a]) if isinstance(a, str) else dict(a)
    B = dict(LIGHT_PRESETS[b]) if isinstance(b, str) else dict(b)
    out = {}
    for k in A:
        if isinstance(A[k], tuple):
            out[k] = tuple(x + (y - x) * u for x, y in zip(A[k], B[k]))
        else:
            out[k] = A[k] + (B[k] - A[k]) * u
    return out

def build(M, year, ctx=None):                     # scene.py plug-in hook (runs after the base scene / set is built)
    if STATE.get("root"):                         # trost.build_set may call plug-in builds itself: attach only once
        return
    terrain = (ctx or {}).get("terrain") if isinstance(ctx, dict) else None
    STATE["root"] = attach(active_frame(), M=M, terrain=terrain)
