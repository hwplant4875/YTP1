"""PART 2-3 shared kit (forest + Stohess segments, seg_f*.py / seg_s*.py).  Pure functions of time, no keyframes.

FRAMES  W = world.py world frame (= the Shiganshina frame; Mitras (0, 24000), Wall Rose r 19 km, Maria r 24 km).
        F = forest bible frame (FOREST_SCENE_BIBLE.md B): origin at the forest road entrance, +y = travel (north), +x = right flank.
            W = F + FO.  Karanes (Rose EAST district) outer gate = W (19870, 24000) = F (270, -9000), as the bible's (0, -9000).
        M = Trost master frame (part 1): W = M + (0, 4130).
LIGHT   LightRig(keys, grade, haze): the g8 key format (t, el, compass az, sun energy, sun rgb, zenith rgb, horizon rgb, world
        strength, exposure offset) so the part 1 end light continues exactly.
CROWDS  Batch: one mesh for many low-poly bodies (swarm845.Geo + odm.deform): riders on horses, wagons, pure titans, ODM soldiers.
SHIFTERS Female (shifters.make_female, FK pose by bone eulers), Eren (attack_titan + seg_g6 IK poses).
"""
import math, os, sys, random
import numpy as np

try:
    import bpy, bmesh
    from mathutils import Vector, Matrix, Euler
except ImportError:
    bpy = None

HERE = os.path.dirname(os.path.abspath(__file__))
AOT = os.path.dirname(HERE)
if AOT not in sys.path:
    sys.path.insert(0, AOT)

FO = (19600.0, 33000.0)
KARANES_GATE = (19870.0, 24000.0)          # W, Rose east district tip (world._district: centre (19000, 24000), S 390 + R 480)
MITRAS = (0.0, 24000.0)
M_OFF_Y = 4130.0

def F(x, y=0.0, z=0.0):
    return (x + FO[0], y + FO[1], z)
def toF(x, y, z=0.0):
    return (x - FO[0], y - FO[1], z)
def M2W(x, y, z=0.0):
    return (x, y + M_OFF_Y, z)

# ---------------------------------------------------------------- small pure helpers
def ss(a, b, x):
    u = min(1.0, max(0.0, (x - a) / (b - a))) if b != a else float(x >= b)
    return u * u * (3 - 2 * u)
def lerp(a, b, u):
    return a + (b - a) * u
def lerpv(a, b, u):
    return tuple(x + (y - x) * u for x, y in zip(a, b))
def bump(t, a, b, c, d):
    return ss(a, b, t) * (1.0 - ss(c, d, t))
def keyed(K, t):
    """K = [(t, ...), ...] -> (a, b, u) with smoothstep u."""
    if t <= K[0][0]:
        return K[0], K[0], 0.0
    for a, b in zip(K, K[1:]):
        if a[0] <= t < b[0]:
            return a, b, ss(a[0], b[0], t)
    return K[-1], K[-1], 0.0
def path_at(P, t):
    """P = [(t, x, y), ...] piecewise-linear with smooth corners (Catmull-Rom in time) -> (x, y, heading yaw)."""
    T = [p[0] for p in P]
    if t <= T[0]:
        i = 0; u = 0.0
    elif t >= T[-1]:
        i = len(P) - 2; u = 1.0
    else:
        i = max(k for k in range(len(P) - 1) if T[k] <= t); u = (t - T[i]) / (T[i + 1] - T[i])
    p0 = P[max(0, i - 1)]; p1 = P[i]; p2 = P[i + 1]; p3 = P[min(len(P) - 1, i + 2)]
    def cr(k, uu):
        a, b, c, d = p0[k], p1[k], p2[k], p3[k]
        return 0.5 * (2 * b + (-a + c) * uu + (2 * a - 5 * b + 4 * c - d) * uu * uu + (-a + 3 * b - 3 * c + d) * uu ** 3)
    x, y = cr(1, u), cr(2, u)
    e = 1e-3
    x2, y2 = cr(1, min(1.0, u + e)), cr(2, min(1.0, u + e))
    x1, y1 = cr(1, max(0.0, u - e)), cr(2, max(0.0, u - e))
    yaw = math.atan2(-(x2 - x1), (y2 - y1)) if abs(x2 - x1) + abs(y2 - y1) > 1e-9 else 0.0
    return x, y, yaw

def yaw_of(dx, dy):
    """heading (radians CCW from +y) of a direction."""
    return math.atan2(-dx, dy)

# ---------------------------------------------------------------- ground
_W = {}
def world_mod():
    if "w" not in _W:
        import world
        _W["w"] = world
    return _W["w"]
LOCAL_GROUND = []                 # [(fn(x, y) -> dz or None)] set-level patches (flattened clearings, roads)
def G(x, y):
    h = float(world_mod().world_height(x, y))
    for fn in LOCAL_GROUND:
        d = fn(x, y)
        if d is not None:
            h = d
    return h
def GF(x, y):
    """ground at frame F (x, y)."""
    return G(x + FO[0], y + FO[1])

# ---------------------------------------------------------------- materials
_MATS = {}
def mat(name, rgb, rough=0.8, emit=None, strength=0.0, alpha=None):
    if name in _MATS:
        return _MATS[name]
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (*rgb, 1.0)
    b.inputs["Roughness"].default_value = rough
    if emit is not None:
        b.inputs["Emission Color"].default_value = (*emit, 1.0); b.inputs["Emission Strength"].default_value = strength
    if alpha is not None:
        b.inputs["Alpha"].default_value = alpha
        try:
            m.surface_render_method = "BLENDED"
        except Exception:
            pass
    m.diffuse_color = (*rgb, 1.0)
    _MATS[name] = m
    return m

def coll(name):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name); bpy.context.scene.collection.children.link(c)
    return c

def mesh_obj(name, bm, mats, c):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for m_ in mats:
        me.materials.append(m_)
    ob = bpy.data.objects.new(name, me); c.objects.link(ob)
    return ob

def hide(ob, h):
    if ob.hide_render != h:
        ob.hide_render = h; ob.hide_viewport = h

# ---------------------------------------------------------------- sky (= trost._world, so part 1's light code and keys apply)
def make_sky(sc):
    w = bpy.data.worlds.new("Sky"); sc.world = w; w.use_nodes = True
    nt = w.node_tree; sky = nt.nodes.new("ShaderNodeTexSky")
    types = sky.bl_rna.properties["sky_type"].enum_items.keys()
    sky.sky_type = "MULTIPLE_SCATTERING" if "MULTIPLE_SCATTERING" in types else "NISHITA"
    sky.sun_elevation = math.radians(40); sky.sun_rotation = math.radians(115); sky.air_density = 1.4
    if hasattr(sky, "sun_disc"): sky.sun_disc = False
    if hasattr(sky, "dust_density"): sky.dust_density = 2.5
    if hasattr(sky, "aerosol_density"): sky.aerosol_density = 1.5
    nt.links.new(sky.outputs[0], nt.nodes["Background"].inputs[0])
    tcw = nt.nodes.new("ShaderNodeTexCoord"); sz = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tcw.outputs["Generated"], sz.inputs[0])
    gr = nt.nodes.new("ShaderNodeValToRGB"); ge = gr.color_ramp.elements
    ge[0].position, ge[0].color = 0.0, (0.70, 0.80, 0.90, 1)
    ge[1].position, ge[1].color = 0.40, (0.18, 0.38, 0.78, 1)
    nt.links.new(sz.outputs["Z"], gr.inputs[0])
    bg2 = nt.nodes.new("ShaderNodeBackground"); bg2.inputs[1].default_value = float(os.environ.get("SKYB", "4.0"))
    nt.links.new(gr.outputs[0], bg2.inputs[0])
    lp = nt.nodes.new("ShaderNodeLightPath"); mx = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(lp.outputs["Is Camera Ray"], mx.inputs[0])
    nt.links.new(nt.nodes["Background"].outputs[0], mx.inputs[1]); nt.links.new(bg2.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], nt.nodes["World Output"].inputs[0])
    nt.nodes["Background"].inputs[1].default_value = 0.25
    sun = bpy.data.lights.new("Sun", "SUN"); sun.energy = 3.6; sun.angle = math.radians(1.5)
    so = bpy.data.objects.new("Sun", sun); sc.collection.objects.link(so)
    return w, so

# ---------------------------------------------------------------- light rig (g8 format)
# key: (t, el deg, compass az deg, sun energy, sun rgb, zenith rgb, horizon rgb, world strength, exposure offset)
G8_END = (0.0, 10.0, 250, 3.3, (1.00, 0.75, 0.50), (0.22, 0.34, 0.62), (0.98, 0.75, 0.52), 0.95, 0.00)
G8_END_GRADE = (0.0, (1.08, 0.97, 0.84), 0.00)
HAZE0 = (0.0, 5000.0, 0.45, (0.62, 0.70, 0.82))
PRESET = dict(
    golden=G8_END[1:],
    dusk=(-2.5, 255, 0.9, (1.00, 0.55, 0.60), (0.18, 0.13, 0.32), (0.86, 0.46, 0.56), 0.45, 0.35),
    night=(30.0, 120, 1.1, (0.55, 0.66, 1.00), (0.03, 0.05, 0.12), (0.10, 0.13, 0.24), 0.30, 0.00),
    dawn=(3.0, 95, 2.4, (1.00, 0.62, 0.38), (0.20, 0.30, 0.58), (1.00, 0.64, 0.44), 0.75, 0.05),
    morning=(24.0, 110, 3.3, (1.00, 0.94, 0.86), (0.12, 0.30, 0.72), (0.74, 0.81, 0.92), 0.95, 0.00),
    day=(40.0, 160, 3.6, (1.00, 0.97, 0.92), (0.10, 0.28, 0.75), (0.70, 0.80, 0.93), 1.00, 0.00),
    afternoon=(26.0, 225, 3.3, (1.00, 0.90, 0.76), (0.14, 0.30, 0.70), (0.80, 0.80, 0.86), 0.95, 0.00),
    sunset=(6.0, 255, 3.0, (1.00, 0.58, 0.30), (0.22, 0.28, 0.55), (1.00, 0.62, 0.36), 0.80, 0.05),
    overcast=(30.0, 200, 1.6, (0.85, 0.88, 0.92), (0.40, 0.45, 0.52), (0.70, 0.72, 0.75), 1.10, 0.10),
)
GRADE = dict(golden=((1.08, 0.97, 0.84), 0.0), dusk=((1.04, 0.84, 1.00), -0.45), night=((0.66, 0.80, 1.16), -0.75),
             dawn=((1.18, 0.98, 0.80), -0.15), morning=((1.0, 1.0, 1.0), 0.0), day=((1.0, 1.0, 1.0), 0.0),
             afternoon=((1.03, 1.0, 0.94), 0.0), sunset=((1.14, 0.94, 0.76), -0.15), overcast=((0.97, 1.0, 1.02), -0.05))
HAZE = dict(golden=(5000.0, 0.45, (0.80, 0.72, 0.62)), dusk=(3800.0, 0.55, (0.55, 0.40, 0.50)),
            night=(3000.0, 0.60, (0.03, 0.05, 0.14)), dawn=(2600.0, 0.70, (0.95, 0.70, 0.55)),
            morning=(4200.0, 0.55, (0.74, 0.80, 0.88)), day=(5000.0, 0.45, (0.62, 0.70, 0.82)),
            afternoon=(4600.0, 0.50, (0.70, 0.74, 0.80)), sunset=(3600.0, 0.62, (0.96, 0.66, 0.46)),
            overcast=(2600.0, 0.70, (0.66, 0.68, 0.70)))

def light_plan(plan):
    """plan = [(t, preset name), ...] -> (LIGHT_KEYS, GRADE_KEYS, HAZE_KEYS)."""
    return ([(t,) + tuple(PRESET[n]) for t, n in plan], [(t,) + tuple(GRADE[n]) for t, n in plan],
            [(t,) + tuple(HAZE[n]) for t, n in plan])

class LightRig:
    def __init__(self, keys, grade, haze):
        self.K, self.GK, self.HK = keys, grade, haze
        self.L0 = None

    def capture(self):
        sc = bpy.context.scene
        suns = [o for o in bpy.data.objects if o.type == "LIGHT" and o.data.type == "SUN"]
        w = sc.world
        nodes = w.node_tree.nodes if (w and w.use_nodes) else []
        self.L0 = dict(suns=suns, exp0=sc.view_settings.exposure,
                       ramps=[n for n in nodes if n.type == "VALTORGB"], skies=[n for n in nodes if n.type == "TEX_SKY"],
                       bgs=[(n, n.inputs[1].default_value) for n in nodes if n.type == "BACKGROUND"])

    def apply(self, t):
        if self.L0 is None:
            self.capture()
        a, b, u = keyed(self.K, t)
        def mix(i):
            x, y = a[i], b[i]
            return lerpv(x, y, u) if isinstance(x, tuple) else lerp(x, y, u)
        def sdir(k):
            el, az = math.radians(k[1]), math.radians(k[2])
            return np.array([math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el)])
        d = sdir(a) * (1 - u) + sdir(b) * u; d /= np.linalg.norm(d)
        if d[2] < 0.03:
            d[2] = 0.03; d /= np.linalg.norm(d)
        L0 = self.L0
        en = mix(3); col = mix(4); zen = mix(5); hor = mix(6); ws = mix(7); ex = mix(8)
        for o in L0["suns"]:
            o.rotation_euler = Vector(-d).to_track_quat("-Z", "Y").to_euler()
            o.data.energy = en; o.data.color = col
        for r in L0["ramps"]:
            el = r.color_ramp.elements
            el[0].color = (*hor, 1); el[-1].color = (*zen, 1)
        for s in L0["skies"]:
            try:
                s.sun_elevation = math.radians(max(-4.0, mix(1))); s.sun_rotation = math.atan2(d[1], d[0])
            except Exception:
                pass
        for n, s0 in L0["bgs"]:
            n.inputs[1].default_value = s0 * ws
        ga, gb, gu = keyed(self.GK, t)
        gain = lerpv(ga[1], gb[1], gu); gex = lerp(ga[2], gb[2], gu)
        vs = bpy.context.scene.view_settings
        vs.exposure = L0["exp0"] + gex + ex
        try:
            vs.use_curve_mapping = True
            cm = vs.curve_mapping
            cm.white_level = tuple(1.0 / max(g, 1e-3) for g in gain)
            cm.black_level = (0.0, 0.0, 0.0)
            cm.update()
        except Exception:
            pass
        ha, hb, hu = keyed(self.HK, t)
        set_haze(lerp(ha[1], hb[1], hu), lerp(ha[2], hb[2], hu), lerpv(ha[3], hb[3], hu))

def set_haze(depth, amount, rgb):
    sc = bpy.context.scene
    w = sc.world
    if w is not None:
        w.mist_settings.depth = depth
    ng = getattr(sc, "compositing_node_group", None)
    if ng is None:
        return
    for n in ng.nodes:
        if n.bl_idname == "ShaderNodeMath" and n.operation == "MULTIPLY":
            n.inputs[1].default_value = amount
        elif n.bl_idname == "ShaderNodeMix":
            n.inputs["B"].default_value = (*rgb, 1.0)

# ---------------------------------------------------------------- batched low-poly bodies
RIDER_MATS = [("RD_horse", (0.20, 0.11, 0.06), 0.8), ("RD_horse2", (0.09, 0.06, 0.04), 0.8), ("RD_skin", (0.80, 0.56, 0.42), 0.6),
              ("RD_cloak", (0.10, 0.30, 0.12), 0.8), ("RD_white", (0.82, 0.80, 0.74), 0.8), ("RD_jacket", (0.36, 0.23, 0.12), 0.7),
              ("RD_hair", (0.06, 0.04, 0.03), 0.6), ("RD_canvas", (0.80, 0.78, 0.70), 0.9), ("RD_wood", (0.30, 0.20, 0.11), 0.85),
              ("RD_blond", (0.62, 0.48, 0.20), 0.6), ("RD_steel", (0.55, 0.57, 0.60), 0.35), ("RD_dust", (0.55, 0.47, 0.34), 0.95)]
CAT = {n[0][3:]: i for i, n in enumerate(RIDER_MATS)}

def _sw():
    import swarm845 as SW
    return SW

class Batch:
    """Many bodies in one mesh.  new() -> object id j; builders add primitives for j; build(); then per frame set
    pos/yaw/Ar/Ae/lean/vis/pitch arrays and push()."""
    def __init__(self, name, mats):
        self.name, self.mspec = name, mats
        self.g = _sw().Geo(); self.n = 0; self.pivot = []

    def new(self, pivot=0.0):
        j = self.n; self.n += 1; self.pivot.append(pivot)
        return j

    def build(self, c):
        import odm
        self.R = odm.finish(self.g)
        mats = [mat(n, col, r) for n, col, r in self.mspec]
        self.ob = _sw()._mesh(self.name, self.R, self.g.f, self.g.fc, mats, c)
        for p in self.ob.data.polygons:
            p.use_smooth = False
        n = self.n
        self.Ar = np.zeros((n, 8)); self.Ae = np.zeros((n, 8)); self.lean = np.zeros(n); self.vis = np.ones(n)
        self.yaw = np.zeros(n); self.pos = np.zeros((n, 3)); self.pitch = np.zeros(n); self.roll = np.zeros(n)
        self.piv = np.array(self.pivot, float)
        return self

    def push(self):
        import odm
        co = odm.deform(self.R, self.Ar, self.Ae, self.lean, self.vis, self.yaw, self.pos, self.pitch, self.roll, self.piv)
        self.ob.data.vertices.foreach_set("co", co.astype(np.float32).ravel()); self.ob.data.update()

def rider_geo(g, j, cloak=True, hair="hair", horse="horse", scale=1.0, rider=True):
    """Horse + rider, +y forward, ~2.4 m to the rider's head.  parts: 0 body, 1 front legs (pivot shoulder), 2 hind legs."""
    s = scale
    B = lambda c, sz, cat, part=0, pr=(0, 0), taper=1.0: g.box(tuple(v * s for v in c), tuple(v * s for v in sz), CAT[cat], j, part, (pr[0] * s, pr[1] * s), (0, 0), 1.2 * s, taper)
    B((0, 0, 1.25), (0.62, 1.9, 0.66), horse)
    B((0, 1.05, 1.62), (0.34, 0.55, 0.82), horse, taper=0.7)
    B((0, 1.42, 1.92), (0.28, 0.62, 0.30), horse)
    B((0, -1.05, 1.15), (0.12, 0.14, 0.7), "horse2")
    for sx in (-0.2, 0.2):
        B((sx, 0.72, 0.52), (0.14, 0.15, 1.05), horse, 1, (0.72, 1.05))
        B((sx, -0.72, 0.52), (0.15, 0.17, 1.05), horse, 2, (-0.72, 1.05))
    if not rider:
        return
    B((0, 0.05, 1.68), (0.62, 0.32, 0.32), "white")                  # thighs over the saddle
    g.cyl(0, 0.05 * s, 1.72 * s, 2.28 * s, 0.19 * s, 0.17 * s, 6, CAT["jacket"], j, 0, hip=1.2 * s)
    g.sphere((0, 0.07 * s, 2.42 * s), 0.13 * s, 6, 4, CAT["skin"], CAT[hair], 0.1, j, 0, 1.2 * s)
    if cloak:
        B((0, -0.20, 1.98), (0.52, 0.10, 0.78), "cloak", taper=0.8)

def wagon_geo(g, j):
    B = lambda c, sz, cat, part=0, pr=(0, 0), taper=1.0: g.box(c, sz, CAT[cat], j, part, pr, (0, 0), 1.2, taper)
    B((0, -1.6, 1.0), (1.7, 3.6, 0.5), "wood")
    B((0, -1.6, 1.95), (1.8, 3.4, 1.5), "canvas", taper=0.75)
    for wy in (-0.4, -2.8):
        for wx in (-0.95, 0.95):
            B((wx, wy, 0.55), (0.12, 1.1, 1.1), "wood")
    rider_geo(g, j, cloak=True)                                         # the driver's horse in front (horse at y 0)

def person_geo(g, j, cloak=True, hair="hair", h=1.7, odm=True):
    """standing / flying soldier (local +y forward), parts 3/4 arms, 1/2 legs."""
    k = h / 1.7
    B = lambda c, sz, cat, part=0, pr=(0, 0), taper=1.0: g.box(tuple(v * k for v in c), tuple(v * k for v in sz), CAT[cat], j, part, (pr[0] * k, pr[1] * k), (0, 0), 0.9 * k, taper)
    for sx, part in ((-0.1, 1), (0.1, 2)):
        B((sx, 0, 0.45), (0.13, 0.15, 0.9), "white", part, (0, 0.9))
    g.cyl(0, 0, 0.88 * k, 1.42 * k, 0.17 * k, 0.19 * k, 6, CAT["jacket"], j, 0, hip=0.9 * k)
    g.sphere((0, 0.02 * k, 1.56 * k), 0.12 * k, 6, 4, CAT["skin"], CAT[hair], 0.1, j, 0, 0.9 * k)
    for sx, part in ((-0.23, 3), (0.23, 4)):
        B((sx, 0, 1.12), (0.09, 0.1, 0.6), "jacket", part, (0, 1.4))
    if cloak:
        B((0, -0.16, 1.05), (0.42, 0.06, 0.75), "cloak", taper=0.8)
    if odm:
        for sx in (-0.2, 0.2):
            B((sx, -0.05, 0.86), (0.08, 0.36, 0.12), "steel")

TITAN_MATS = None
def titan_mats():
    SW = _sw()
    return [(f"FT_skin{i}", c, 0.65) for i, c in enumerate(SW.T_SKINS)] + [(f"FT_hair{i}", c, 0.7) for i, c in enumerate(SW.T_HAIRS)] \
        + [("FT_teeth", (0.85, 0.80, 0.70), 0.5), ("FT_mouth", (0.18, 0.04, 0.03), 0.6)]

def titan_add(B, spec):
    """spec: dict(H, g, al, hs, skin, hair(None|i), grin, laugh) -> j (pivot = hip height)."""
    SW = _sw()
    sp = dict(dict(g=1.0, al=1.0, hs=1.0, skin=0, hair=None), **spec)
    j = B.new(pivot=0.47 * sp["H"])
    n0 = len(B.g.fc)
    SW.titan_geo(B.g, j, sp)
    hb = len(SW.T_SKINS); nh = len(SW.T_HAIRS)
    remap = {0: sp["skin"], 1: hb + (sp["hair"] if sp.get("hair") is not None else 0), 2: hb + nh, 3: hb + nh + 1}
    B.g.fc[n0:] = [remap.get(c, sp["skin"]) for c in B.g.fc[n0:]]
    return j

def titan_walk(B, j, phase, amp=0.5, arms=0.35, run=False):
    s = math.sin(phase)
    B.Ar[j, 1] = amp * s; B.Ar[j, 2] = -amp * s
    a = arms * s * (1.6 if run else 1.0)
    B.Ar[j, 3] = -a; B.Ar[j, 6] = -a; B.Ar[j, 4] = a; B.Ar[j, 5] = a
    B.lean[j] = -0.35 if run else -0.06

# ---------------------------------------------------------------- thin lines (harpoon wires, ODM wires)
class Wires:
    def __init__(self, name, n, mat_, c, r=0.15):
        self.n, self.r = n, r
        me = bpy.data.meshes.new(name)
        V = np.zeros((n * 4, 3)); Fc = []
        for i in range(n):
            b = 4 * i; Fc += [(b, b + 1, b + 3, b + 2)]
        me.from_pydata(V.tolist(), [], Fc); me.materials.append(mat_)
        self.ob = bpy.data.objects.new(name, me); c.objects.link(self.ob)
        self.ob.visible_shadow = False

    def update(self, segs, cam_loc):
        """segs: list of (a, b) points (len <= n); unused wires collapse.  Ribbons face the camera."""
        V = np.zeros((self.n * 4, 3))
        cl = np.array(cam_loc, float)
        for i, (a, b) in enumerate(segs[:self.n]):
            a = np.array(a, float); b = np.array(b, float)
            d = b - a; m = (a + b) / 2
            side = np.cross(d, cl - m); ln = np.linalg.norm(side)
            side = side / ln * self.r if ln > 1e-9 else np.array([self.r, 0, 0])
            V[4 * i:4 * i + 4] = [a - side, a + side, b - side, b + side]
        self.ob.data.vertices.foreach_set("co", V.astype(np.float32).ravel()); self.ob.data.update()

# ---------------------------------------------------------------- Female Titan (shifters.make_female, FK by bone eulers)
FEMALE_BONES = ("spine01", "spine02", "spine03", "spine04", "spine05", "neck01", "neck02", "head", "jaw",
                "upperarm01.L", "upperarm01.R", "lowerarm01.L", "lowerarm01.R", "upperleg01.L", "upperleg01.R",
                "lowerleg01.L", "lowerleg01.R", "foot.L", "foot.R", "clavicle.L", "clavicle.R", "shoulder01.L", "shoulder01.R")

class Female:
    """rig faces -Y in its rest frame; place(x, y, z, yaw) with yaw = heading (CCW from +y).
    pose(D): D = {bone: (x, y, z) degrees} ADDED to the relaxed base pose (shifters.relax)."""
    def __init__(self, name="FemaleTitan"):
        import shifters
        self.SH = shifters
        self.rig = shifters.make_female(name)
        self.P = self.rig.pose.bones
        self.base = {}
        for pb in self.P:
            pb.rotation_mode = "XYZ"
            self.base[pb.name] = tuple(pb.rotation_euler)
        self.objs = [self.rig] + list(self.rig.children_recursive)
        self.hard = 0.0

    def pose(self, D):
        for pb in self.P:
            b = self.base[pb.name]
            d = D.get(pb.name)
            pb.rotation_euler = b if d is None else (b[0] + math.radians(d[0]), b[1] + math.radians(d[1]), b[2] + math.radians(d[2]))

    def place(self, x, y, z, yaw, pitch=0.0, roll=0.0):
        self.rig.location = (x, y, z)
        self.rig.rotation_mode = "ZXY"
        self.rig.rotation_euler = (pitch, roll, yaw + math.pi)

    def show(self, on):
        for o in self.objs:
            hide(o, not on)

    def hardening(self, a):
        if abs(a - self.hard) > 1e-3:
            self.SH.set_hardening(self.rig, a); self.hard = a

    def bone_world(self, bn, tail=False):
        pb = self.P[bn]
        return self.rig.matrix_world @ (pb.tail if tail else pb.head)

def fpose_blend(A, B_, u):
    out = {}
    for k in set(A) | set(B_):
        a = A.get(k, (0, 0, 0)); b = B_.get(k, (0, 0, 0))
        out[k] = tuple(x + (y - x) * u for x, y in zip(a, b))
    return out

# ---------------------------------------------------------------- Eren's Attack Titan (attack_titan + seg_g6 IK poses)
class Eren:
    def __init__(self, name="F_Attack"):
        import attack_titan as AT
        import seg_g6 as G6
        self.AT, self.G6 = AT, G6
        self.T = AT.place_attack(0.0, 0.0, 0.0, "stand", name=name, eyes=20.0)
        self.T.holder.matrix_world = Matrix.Identity(4); bpy.context.view_layer.update()
        self.P = G6.make_poses()
        self.objs = [o for o in self.T.coll.all_objects]

    def pose(self, spec):
        self.AT.POSES["_f"] = spec
        self.T.pose("_f", ground=False)

    def place(self, x, y, z, yaw, pitch=0.0):
        self.T.holder.location = (x, y, z)
        self.T.holder.rotation_euler = (pitch, 0.0, yaw + math.pi)

    def show(self, on):
        for o in self.objs:
            hide(o, not on)

def trail_geo(g, j, L=16.0, w=1.3):
    """flat dust streak behind a rider (cat canvas-ish tan), lies on the ground."""
    g.box((0, -L / 2 - 1.0, 0.15), (w, L, 0.1), CAT["dust"] if "dust" in CAT else CAT["canvas"], j, 0, (0, 0), (0, 0), 0.0, 1.0)

# person poses (Batch arrays): seated on a horse, running, ODM flying (pitch forward)
def person_pose(B, j, mode, t=0.0):
    if mode == "seated":
        B.Ar[j, 1] = B.Ar[j, 2] = 1.35; B.Ar[j, 3] = B.Ar[j, 4] = 0.5; B.lean[j] = 0.0; B.pitch[j] = 0.0
    elif mode == "run":
        s = math.sin(t * 9.0)
        B.Ar[j, 1] = 0.7 * s; B.Ar[j, 2] = -0.7 * s; B.Ar[j, 3] = -0.6 * s; B.Ar[j, 4] = 0.6 * s; B.lean[j] = -0.2; B.pitch[j] = 0.0
    elif mode == "fly":
        B.Ar[j, 1] = 0.25; B.Ar[j, 2] = 0.55; B.Ar[j, 3] = B.Ar[j, 4] = -2.4; B.lean[j] = 0.0; B.pitch[j] = -1.1
    elif mode == "fallen":
        B.Ar[j, :] = 0.3; B.pitch[j] = -1.45
    else:
        B.Ar[j, :] = 0.0; B.lean[j] = 0.0; B.pitch[j] = 0.0

# ---------------------------------------------------------------- Female pose library (degrees, added to the relaxed base)
# calibrated (seg_ftest 10/27): upperleg x+ = thigh BACK, lowerleg x+ = knee flex, spine x+ = lean forward,
# upperarm x+ = arm FORWARD/up, lowerarm x+ = elbow flex, neck x+ = head down; upperarm z: L - = down, R + = down.
def fem_run(phase, lean=28.0, amp=48.0):
    s = math.sin(phase); c = math.cos(phase)
    return {"upperleg01.L": (-amp * s - 12, 0, 0), "upperleg01.R": (amp * s - 12, 0, 0),
            "lowerleg01.L": (18 + 70 * max(0.0, -c) * (s < 0.4), 0, 0), "lowerleg01.R": (18 + 70 * max(0.0, c) * (s > -0.4), 0, 0),
            "foot.L": (-10, 0, 0), "foot.R": (-10, 0, 0),
            "spine01": (lean * 0.4, 0, 0), "spine02": (lean * 0.3, 0, 0), "spine03": (lean * 0.3, 0, 0),
            "neck01": (-lean * 0.7, 0, 0), "head": (-8, 0, 0),
            "upperarm01.L": (45 * s + 10, 0, 0), "upperarm01.R": (-45 * s + 10, 0, 0),
            "lowerarm01.L": (75, 0, 0), "lowerarm01.R": (75, 0, 0)}
FPOSE = {
    "stand": {},
    "kneel": {"upperleg01.L": (-85, 0, 0), "lowerleg01.L": (90, 0, 0), "upperleg01.R": (-5, 0, 0), "lowerleg01.R": (118, 0, 0),
              "foot.R": (40, 0, 0), "spine01": (20, 0, 0), "spine02": (15, 0, 0), "spine03": (12, 0, 0), "neck01": (25, 0, 0),
              "upperarm01.R": (58, 0, 10), "lowerarm01.R": (20, 0, 0), "upperarm01.L": (10, 0, 0), "lowerarm01.L": (30, 0, 0)},
    "reach": {"spine01": (18, 0, 0), "spine02": (12, 0, 0), "upperarm01.R": (95, 0, 0), "lowerarm01.R": (15, 0, 0),
              "upperleg01.L": (-25, 0, 0), "lowerleg01.L": (30, 0, 0), "upperleg01.R": (15, 0, 0), "lowerleg01.R": (25, 0, 0)},
    "hold": {"spine01": (5, 0, 0), "upperarm01.R": (70, 0, 0), "lowerarm01.R": (60, 0, 0), "neck01": (10, 0, 0)},
    "swat": {"spine01": (15, 0, -20), "spine02": (10, 0, -15), "upperarm01.R": (60, 0, -40), "lowerarm01.R": (10, 0, 0),
             "upperleg01.L": (-30, 0, 0), "lowerleg01.L": (35, 0, 0)},
    "kick": {"upperleg01.R": (-100, 0, 0), "lowerleg01.R": (5, 0, 0), "upperleg01.L": (10, 0, 0), "lowerleg01.L": (15, 0, 0),
             "spine01": (-15, 0, 25), "spine02": (-5, 0, 20), "upperarm01.L": (40, 0, -30), "upperarm01.R": (20, 0, 30)},
    "guard": {"upperarm01.L": (100, 0, 25), "lowerarm01.L": (125, 0, 0), "upperarm01.R": (100, 0, -25), "lowerarm01.R": (125, 0, 0),
              "spine01": (8, 0, 0), "upperleg01.L": (-15, 0, 0), "lowerleg01.L": (25, 0, 0), "upperleg01.R": (10, 0, 0), "lowerleg01.R": (20, 0, 0)},
    "nape": {"upperarm01.L": (160, 0, 35), "lowerarm01.L": (120, 0, 0), "upperarm01.R": (160, 0, -35), "lowerarm01.R": (120, 0, 0),
             "neck01": (25, 0, 0), "head": (10, 0, 0), "spine01": (6, 0, 0)},
    "scream": {"upperarm01.L": (150, 0, 30), "lowerarm01.L": (115, 0, 0), "upperarm01.R": (150, 0, -30), "lowerarm01.R": (115, 0, 0),
               "neck01": (-35, 0, 0), "head": (-20, 0, 0), "spine02": (-10, 0, 0), "spine03": (-10, 0, 0), "jaw": (25, 0, 0)},
    "sit": {"upperleg01.L": (-85, 0, -10), "lowerleg01.L": (70, 0, 0), "upperleg01.R": (-80, 0, 8), "lowerleg01.R": (60, 0, 0),
            "spine01": (-10, 0, 0), "spine02": (-5, 0, 0), "neck01": (30, 0, 0), "head": (15, 0, 0),
            "upperarm01.L": (5, 0, 10), "upperarm01.R": (5, 0, -10), "lowerarm01.L": (20, 0, 0), "lowerarm01.R": (20, 0, 0)},
    "crouch": {"upperleg01.L": (-70, 0, 0), "lowerleg01.L": (110, 0, 0), "upperleg01.R": (-60, 0, 0), "lowerleg01.R": (105, 0, 0),
               "foot.L": (-30, 0, 0), "foot.R": (-30, 0, 0), "spine01": (25, 0, 0), "spine02": (15, 0, 0), "neck01": (-25, 0, 0),
               "upperarm01.L": (30, 0, 0), "upperarm01.R": (30, 0, 0), "lowerarm01.L": (40, 0, 0), "lowerarm01.R": (40, 0, 0)},
}
FZ = dict(kneel=-3.6, sit=-5.6, crouch=-3.2)      # rig drop (m) for poses whose feet leave the ground plane

def fem_pose_z(weights):
    """weights: {pose name: w} (sum ~1) -> rig z offset."""
    return sum(FZ.get(k, 0.0) * w for k, w in weights.items())

# ---------------------------------------------------------------- camera keys relative to the ground
def lift_keys(keys, skip=(), dy=0.0):
    """keys [(t, pos, look, lens)] with z ABOVE THE GROUND -> absolute z (world.py relief is 12-70 m here).  skip: key
    indices left absolute (seams owned by part 1).  dy: frame offset to W (frame M: 4130)."""
    out = []
    for i, (t, p, l, lens) in enumerate(keys):
        if i in skip:
            out.append((t, p, l, lens)); continue
        out.append((t, (p[0], p[1], p[2] + G(p[0], p[1] + dy)), (l[0], l[1], l[2] + G(l[0], l[1] + dy)), lens))
    return out
