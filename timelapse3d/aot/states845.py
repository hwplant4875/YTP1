"""845 destruction states of Shiganshina (environment only, no titans) as a scene.py plug-in.

Enable with AOT_PLUGINS=states845 (usually AOT_PLUGINS=cast845,states845) and pick the state with
AOT_STATE = intact (default, adds nothing) | kicked | armored | night
  kicked  (S1E1-2): outer gate blown in (ragged hole with a chipped, stepped edge and a grime halo, rubble fan,
                    tan dust cloud), 9 wall blocks thrown into the town in arcs, crushed houses, scorched craters,
                    billowing smoke, volume fires, Yeager house crushed (standing X-braced gable, roof slumped in).
  armored (S1E2):   kicked + inner gate burst open (hole full of light, dust at its foot), debris fanning north
                    into the settlement (packed-earth ground there), more smoke, fires spreading.
  night   (S1E2 end): armored + night (dark blue sky, red horizon, moon), 15-20 big blazes, an orange-lit smoke
                    canopy over the town.
Optional env:
  AOT_ARC_T=0..1    put the thrown blocks part-way along their arcs (0.5 = mid-flight) for the kick shot.
                    Blocks still in the air have not crushed anything yet. Unset / 1 = all landed.
  AOT_FIRE_GAIN     multiplies fire light power and flame brightness (default 1).
  AOT_CANOPY_E      multiplies the night smoke-canopy glow (default 1).
  AOT_DUST          multiplies the density of the tan breach / impact dust (default 1).
  AOT_NOSMOKE=1     skip all smoke / dust / flame volumes (quick layout checks).
Exports for other plug-ins (cast845): IMPACTS, YEAGER_HOUSE, OUTER_HOLE, INNER_HOLE, state().
Houses are hidden by lowering the Town point attribute "dead" to the current year, so the scatter stays one object.
"""
import bpy, bmesh, math, os, random
from mathutils import Vector, Matrix, noise
import aotlib as L

STATES = ("intact", "kicked", "armored", "night")

def state():
    s = os.environ.get("AOT_STATE", "intact").strip().lower()
    return s if s in STATES else "intact"

def level():
    return STATES.index(state())

OG = Vector((L.OUTER_GATE[0], L.OUTER_GATE[1]))
YEAGER_HOUSE = (-72.0, -118.0)
# thrown blocks: (x, y, size m, seed). Arcs start at the gate top.
IMPACTS = [(-58, -585, 16, 1), (96, -625, 13, 2), (-150, -455, 19, 3), (62, -318, 15, 4),
           (-205, -265, 13, 5), (150, -250, 17, 6), (-30, -190, 12, 7), (YEAGER_HOUSE[0] + 1, YEAGER_HOUSE[1] - 2, 12, 8),
           (125, -480, 12, 9)]
OUTER_HOLE = (0.0, L.OUTER_GATE[1], 13.0, 31.0)      # x, y, half width, height of the breach
INNER_HOLE = (0.0, 0.0, 12.5, 29.0)                  # about the Armored Titan's height

LABELS = {}
if state() != "intact":
    LABELS = {"BREACH": (OG.x, OG.y, 40), "YEAGER HOUSE": (YEAGER_HOUSE[0], YEAGER_HOUSE[1], 22)}

def _cam_breach():
    return ((46, OG.y + 270, 80), (-2, OG.y + 10, 6), 30)

CAMS = {
    "breach_inside": _cam_breach,                                          # from the town, looking south
    "town_burning": ((-560, 430, 400), (30, -380, 0), 26),                  # high oblique from the NW
    "inner_burst": ((34, 165, 37), (-2, 0, 19), 32),                       # north side, low: the wall hides the hills
    "block_impact": ((-40, -360, 75), (-150, -455, 4), 32),                # close look at one thrown block
    "yeager": ((-40, -150, 26), (-72, -117, 6), 30),                         # the crushed Yeager house
}

def lin(h):
    """sRGB hex -> linear rgb tuple."""
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c)

DUST = lin("#B59D6D")          # tan dust / packed earth
SMOKE = lin("#2A2522")         # dark billowing smoke
GRIME = lin("#363530")
TIMBER = lin("#3B2A20")
INFILL = lin("#D8CDB4")
BEIGE = lin("#C1B59D")

def nosmoke():
    return os.environ.get("AOT_NOSMOKE") == "1"

# ---------------------------------------------------------------- node helper
class G:
    """Tiny node-graph builder for the procedural materials below."""
    def __init__(self, name, keep_bsdf=False):
        m = bpy.data.materials.new(name); m.use_nodes = True
        self.m = m; self.nt = m.node_tree; self.N = self.nt.nodes; self.Ln = self.nt.links
        if not keep_bsdf:
            self.N.remove(self.N["Principled BSDF"])
        self.out = self.N["Material Output"]
    def _in(self, sock, v):
        if isinstance(v, (int, float, tuple)):
            sock.default_value = v
        else:
            self.Ln.new(v, sock)
    def m_(self, op, a, b=None, c=None, clamp=False):
        n = self.N.new("ShaderNodeMath"); n.operation = op; n.use_clamp = clamp
        for i, v in enumerate((a, b, c)):
            if v is not None:
                self._in(n.inputs[i], v)
        return n.outputs[0]
    def v_(self, op, a, b=None, scale=None):
        n = self.N.new("ShaderNodeVectorMath"); n.operation = op
        self._in(n.inputs[0], a)
        if b is not None:
            self._in(n.inputs[1], b)
        if scale is not None:
            self._in(n.inputs["Scale"], scale)
        return n.outputs[1] if op in ("LENGTH", "DOT_PRODUCT", "DISTANCE") else n.outputs[0]
    def noise(self, vec, scale=1.0, detail=4.0, rough=0.55, distortion=0.0):
        n = self.N.new("ShaderNodeTexNoise")
        n.inputs["Scale"].default_value = scale; n.inputs["Detail"].default_value = detail
        n.inputs["Roughness"].default_value = rough; n.inputs["Distortion"].default_value = distortion
        self.Ln.new(vec, n.inputs["Vector"])
        return n.outputs["Fac"]
    def sep(self, v):
        s = self.N.new("ShaderNodeSeparateXYZ"); self.Ln.new(v, s.inputs[0])
        return s.outputs
    def attr(self, name, kind="OBJECT"):
        a = self.N.new("ShaderNodeAttribute"); a.attribute_type = kind; a.attribute_name = name
        return a
    def ramp(self, fac, stops, interp="LINEAR"):
        r = self.N.new("ShaderNodeValToRGB"); r.color_ramp.interpolation = interp
        e = r.color_ramp.elements
        for k, (pos, col) in enumerate(stops):
            el = e[k] if k < 2 else e.new(pos)
            el.position = pos; el.color = (*col, 1)
        self.Ln.new(fac, r.inputs["Fac"])
        return r.outputs["Color"]
    def coords(self, kind="Object"):
        if not hasattr(self, "_tc"):
            self._tc = self.N.new("ShaderNodeTexCoord")
        return self._tc.outputs[kind]

_MC = {}

# ---------------------------------------------------------------- volume materials
def billow_mat(col=SMOKE):
    """Cauliflower puff in a unit cube (-1..1), one material per colour; object custom properties:
    dens (float), emit (float, orange glow concentrated in the lower half). (Colour custom props are not read
    by the Attribute node here, so colours are baked per material.)"""
    key = "Billow_%.3f_%.3f_%.3f" % tuple(col)
    if key in _MC:
        return _MC[key]
    g = G(key)
    p = g.coords()
    oi = g.N.new("ShaderNodeObjectInfo")
    off = g.v_("SCALE", (37.1, 91.7, 13.3), scale=oi.outputs["Random"])
    q = g.v_("ADD", g.v_("SCALE", p, scale=1.35), off)
    n = g.noise(q, 1.0, 6.0, 0.58, 0.25)
    base = g.m_("SUBTRACT", 1.0, g.v_("LENGTH", p))
    shape = g.m_("ADD", g.m_("MULTIPLY", base, 2.6), g.m_("MULTIPLY", g.m_("SUBTRACT", n, 0.5), 2.8))
    shape = g.m_("SUBTRACT", shape, 0.3, clamp=True)
    dens = g.m_("MULTIPLY", shape, g.attr("dens").outputs["Fac"])
    pz = g.sep(p)[2]
    low = g.m_("POWER", g.m_("SUBTRACT", 0.5, g.m_("MULTIPLY", pz, 0.5), clamp=True), 1.5)
    emis = g.m_("MULTIPLY", g.m_("MULTIPLY", shape, low), g.attr("emit").outputs["Fac"])
    pv = g.N.new("ShaderNodeVolumePrincipled"); pv.inputs["Anisotropy"].default_value = 0.3
    pv.inputs["Color"].default_value = (*col, 1)
    g.Ln.new(dens, pv.inputs["Density"])
    pv.inputs["Emission Color"].default_value = (1.0, 0.33, 0.08, 1)
    g.Ln.new(emis, pv.inputs["Emission Strength"])
    g.Ln.new(pv.outputs[0], g.out.inputs["Volume"])
    _MC[key] = g.m
    return g.m

def flame_mat():
    """Volume flame in a box x, y in [-1, 1], z in [0, 1]: narrowing upward, torn by stretched noise,
    emission #FFB040 in the core to #FF5010 at the edges. Object props: fstr (strength), nsc (noise scale)."""
    if "FlameVol" in _MC:
        return _MC["FlameVol"]
    g = G("FlameVol")
    p = g.coords()
    x, y, z = g.sep(p)
    oi = g.N.new("ShaderNodeObjectInfo")
    off = g.v_("SCALE", (17.3, 41.9, 7.7), scale=oi.outputs["Random"])
    q = g.v_("ADD", g.v_("SCALE", g.v_("MULTIPLY", p, (2.0, 2.0, 1.0)), scale=g.attr("nsc").outputs["Fac"]), off)
    n = g.noise(q, 1.6, 5.0, 0.6, 0.6)
    taper = g.m_("SUBTRACT", 1.0, g.m_("MULTIPLY", z, 0.7))
    r = g.m_("DIVIDE", g.m_("SQRT", g.m_("ADD", g.m_("MULTIPLY", x, x), g.m_("MULTIPLY", y, y))), taper)
    f = g.m_("SUBTRACT", g.m_("MULTIPLY", g.m_("SUBTRACT", 1.0, r), 1.7), g.m_("MULTIPLY", z, 1.15))
    f = g.m_("ADD", f, g.m_("MULTIPLY", g.m_("SUBTRACT", n, 0.5), 2.2), clamp=True)
    col = g.ramp(f, [(0.0, (1.0, 0.08, 0.006)), (0.45, lin("#FF5010")), (0.75, lin("#FFB040")), (1.0, (1.0, 0.78, 0.4))])
    es = g.m_("MULTIPLY", g.m_("POWER", f, 1.4), g.attr("fstr").outputs["Fac"])
    pv = g.N.new("ShaderNodeVolumePrincipled")
    pv.inputs["Color"].default_value = (0.05, 0.03, 0.02, 1)
    g.Ln.new(g.m_("MULTIPLY", f, 0.25), pv.inputs["Density"])
    g.Ln.new(col, pv.inputs["Emission Color"]); g.Ln.new(es, pv.inputs["Emission Strength"])
    g.Ln.new(pv.outputs[0], g.out.inputs["Volume"])
    _MC["FlameVol"] = g.m
    return g.m

_ME = {}
def _unit_mesh(kind, col=SMOKE):
    """Shared meshes: 'cube' (-1..1) for billows (one per colour), 'flame' (x,y -1..1, z 0..1)."""
    key = (kind, tuple(col)) if kind == "cube" else kind
    if key in _ME:
        return _ME[key]
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=2.0)
    if kind == "flame":
        for v in bm.verts:
            v.co.z = (v.co.z + 1) / 2
    me = bpy.data.meshes.new("Unit_" + kind); bm.to_mesh(me); bm.free()
    me.materials.append(billow_mat(col) if kind == "cube" else flame_mat())
    _ME[key] = me
    return me

def billow(name, coll, center, radii, col, dens, emit=0.0, ecol=(1.0, 0.33, 0.08), rot=(0, 0, 0)):
    if nosmoke():
        return None
    ob = bpy.data.objects.new(name, _unit_mesh("cube", tuple(round(c, 4) for c in col)))
    ob.location = center; ob.scale = radii; ob.rotation_euler = rot
    ob["dens"] = float(dens); ob["col"] = [float(c) for c in col]
    ob["emit"] = float(emit); ob["ecol"] = [float(c) for c in ecol]
    ob.visible_shadow = True
    coll.objects.link(ob)
    return ob

def smoke_column(name, coll, x, y, R, H, col, dens, lean=(0.45, 0.12), emit=0.0, rnd=None, z0=0.0):
    """Billowing column: stacked puffs growing from 0.5 R to 1.2 R, leaning downwind (lean = metres per metre up)."""
    rnd = rnd or random.Random(hash(name) & 0xffff)
    z, k = 0.0, 0
    while z < H:
        f = z / H
        rk = R * (0.5 + 0.7 * f) * rnd.uniform(0.85, 1.15)
        c = (x + lean[0] * z + rnd.uniform(-0.2, 0.2) * rk, y + lean[1] * z + rnd.uniform(-0.2, 0.2) * rk, z0 + z + rk * 0.55)
        e = emit * max(0.0, 1.0 - z / (0.5 * H)) ** 2
        billow(f"{name}_{k}", coll, c, (rk, rk * rnd.uniform(0.85, 1.1), rk * 0.8), col, dens * (1.0 - 0.45 * f), emit=e,
               rot=(0, 0, rnd.uniform(0, 6.28)))
        z += rk * 0.95; k += 1

class Fires:
    """Volume flames (one box each) + point lights + a small dark puff above the bigger ones."""
    def __init__(self, gain):
        self.rnd = random.Random(55)
        self.gain = gain
        self.items = []
    def add(self, x, y, z, size, light=True, smoke=True, radius=None, nsc=1.0, lw=1.0):
        self.items.append((x, y, z, size, light, smoke, radius or size * 0.45, nsc, lw))
    @property
    def pts(self):
        return [it for it in self.items if it[4]]
    def build(self, coll, strength, light_w, night=False):
        rnd = self.rnd
        for k, (x, y, z, s, light, smk, rad, nsc, lw) in enumerate(self.items):
            if not nosmoke():
                ob = bpy.data.objects.new(f"Flame{k}", _unit_mesh("flame"))
                ob.location = (x, y, z - 0.3); ob.scale = (rad, rad * rnd.uniform(0.8, 1.1), s * 1.35)
                ob.rotation_euler.z = rnd.uniform(0, 6.28)
                ob["fstr"] = strength * self.gain * rnd.uniform(0.8, 1.2); ob["nsc"] = nsc
                ob.visible_shadow = False
                coll.objects.link(ob)
                if smk:
                    billow(f"FlameSmoke{k}", coll, (x + s * 0.4, y, z + s * 1.7), (rad * 2.2, rad * 2.0, s * 0.9),
                           SMOKE, 0.12, emit=(0.6 if night else 0.15), ecol=(1.0, 0.3, 0.06))
            if light:
                ld = bpy.data.lights.new(f"FireL{k}", "POINT")
                ld.energy = light_w * lw * self.gain * (s / 6.0) ** 2
                ld.color = (1.0, 0.42, 0.12); ld.shadow_soft_size = max(1.0, rad)
                lo = bpy.data.objects.new(f"FireL{k}", ld); lo.location = (x, y, z + s * 0.5)
                lo.visible_volume_scatter = False      # smoke glow comes from its own emission (cheaper, controllable)
                coll.objects.link(lo)

# ---------------------------------------------------------------- surface materials
def stone_mat(M, name, k, scale=0.22):
    """Wall stone (same stains / streaks / courses as the wall) with the albedo scaled by k and finer variation,
    so rubble and blocks read as pieces of the wall."""
    m = M["stone"].copy(); m.name = name
    for n in m.node_tree.nodes:
        if n.type == "VALTORGB":
            for e in n.color_ramp.elements:
                e.color = (e.color[0] * k, e.color[1] * k, e.color[2] * k, 1)
        elif n.type == "TEX_NOISE" and abs(n.inputs["Scale"].default_value - 0.035) < 1e-4:
            n.inputs["Scale"].default_value = scale
    return m

def tile_mat():
    """Orange-red clay pan tiles with clear courses (bible 1.7)."""
    if "RoofTile845" in _MC:
        return _MC["RoofTile845"]
    g = G("RoofTile845", keep_bsdf=True)
    b = g.N["Principled BSDF"]; b.inputs["Roughness"].default_value = 0.8
    br = g.N.new("ShaderNodeTexBrick")
    br.inputs["Scale"].default_value = 1.6; br.inputs["Mortar Size"].default_value = 0.035
    br.inputs["Row Height"].default_value = 0.3; br.inputs["Brick Width"].default_value = 0.34
    br.inputs["Color1"].default_value = (*lin("#9A5A40"), 1); br.inputs["Color2"].default_value = (*lin("#B5694A"), 1)
    br.inputs["Mortar"].default_value = (*[c * 0.45 for c in lin("#6E4A3C")], 1)
    g.Ln.new(g.coords(), br.inputs["Vector"])
    n = g.noise(g.coords(), 0.6, 4, 0.6)
    mx = g.N.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.blend_type = "MULTIPLY"; mx.inputs["Factor"].default_value = 0.45
    g.Ln.new(br.outputs["Color"], mx.inputs["A"]); g.Ln.new(g.ramp(n, [(0.3, (0.55, 0.5, 0.48)), (0.7, (1, 1, 1))]), mx.inputs["B"])
    g.Ln.new(mx.outputs["Result"], b.inputs["Base Color"])
    bp = g.N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.5
    g.Ln.new(br.outputs["Fac"], bp.inputs["Height"]); g.Ln.new(bp.outputs["Normal"], b.inputs["Normal"])
    _MC["RoofTile845"] = g.m
    return g.m

def grime_mat():
    """Dark #363530 grime halo around a breach: geometry attribute 'fade' (1 at the hole, 0 outside),
    broken up by noise, with fine dark crack lines in the inner part."""
    if "Grime845" in _MC:
        return _MC["Grime845"]
    g = G("Grime845", keep_bsdf=True)
    b = g.N["Principled BSDF"]; b.inputs["Roughness"].default_value = 0.95
    fade = g.attr("fade", "GEOMETRY").outputs["Fac"]
    p = g.coords()
    n = g.noise(p, 0.09, 6, 0.65)
    a = g.m_("MULTIPLY", g.m_("POWER", fade, 1.1), g.m_("ADD", g.m_("MULTIPLY", n, 1.6), -0.15), clamp=True)
    vo = g.N.new("ShaderNodeTexVoronoi"); vo.feature = "DISTANCE_TO_EDGE"; vo.inputs["Scale"].default_value = 0.16
    g.Ln.new(p, vo.inputs["Vector"])
    crack = g.m_("SUBTRACT", 1.0, g.m_("MULTIPLY", vo.outputs["Distance"], 22.0), clamp=True)
    crack = g.m_("MULTIPLY", crack, g.m_("MULTIPLY", g.m_("SUBTRACT", fade, 0.35, clamp=True), 2.0), clamp=True)
    col = g.N.new("ShaderNodeMix"); col.data_type = "RGBA"
    col.inputs["A"].default_value = (*GRIME, 1); col.inputs["B"].default_value = (0.012, 0.011, 0.01, 1)
    g.Ln.new(crack, col.inputs["Factor"])
    g.Ln.new(col.outputs["Result"], b.inputs["Base Color"])
    g.Ln.new(g.m_("MAXIMUM", a, crack), b.inputs["Alpha"])
    _MC["Grime845"] = g.m
    return g.m

def ground_decal_mat(name, c_centre, c_mid, c_edge, alpha_edge=3.0):
    """Decal on the ground with geometry attribute 'rad' (0 centre, 1 rim): centre colour -> mid -> edge colour,
    ragged alpha towards the rim."""
    if name in _MC:
        return _MC[name]
    g = G(name, keep_bsdf=True)
    b = g.N["Principled BSDF"]; b.inputs["Roughness"].default_value = 0.97
    rad = g.attr("rad", "GEOMETRY").outputs["Fac"]
    n = g.noise(g.coords(), 0.12, 6, 0.6)
    rr = g.m_("ADD", rad, g.m_("MULTIPLY", g.m_("SUBTRACT", n, 0.5), 0.35))
    g.Ln.new(g.ramp(rr, [(0.12, c_centre), (0.5, c_mid), (0.8, c_edge)]), b.inputs["Base Color"])
    a = g.m_("ADD", g.m_("MULTIPLY", g.m_("SUBTRACT", 1.0, rr), alpha_edge), -0.1, clamp=True)
    g.Ln.new(a, b.inputs["Alpha"])
    _MC[name] = g.m
    return g.m

def earth_mat():
    """Packed earth #B59D6D for the settlement ground, alpha from geometry attribute 'earth' (house density)."""
    g = G("Earth845", keep_bsdf=True)
    b = g.N["Principled BSDF"]; b.inputs["Roughness"].default_value = 0.97
    p = g.coords()
    n1 = g.noise(p, 0.05, 6, 0.6); n2 = g.noise(p, 0.6, 3, 0.5)
    c = g.ramp(n1, [(0.3, tuple(x * 0.62 for x in DUST)), (0.55, tuple(x * 0.82 for x in DUST)), (0.75, DUST)])
    mx = g.N.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.blend_type = "OVERLAY"; mx.inputs["Factor"].default_value = 0.25
    g.Ln.new(c, mx.inputs["A"]); g.Ln.new(g.ramp(n2, [(0.0, (0, 0, 0)), (1.0, (1, 1, 1))]), mx.inputs["B"])
    g.Ln.new(mx.outputs["Result"], b.inputs["Base Color"])
    m = g.attr("earth", "GEOMETRY").outputs["Fac"]
    a = g.m_("ADD", g.m_("MULTIPLY", m, 2.2), g.m_("MULTIPLY", g.m_("SUBTRACT", n1, 0.5), 1.8))
    g.Ln.new(g.m_("SUBTRACT", a, 0.4, clamp=True), b.inputs["Alpha"])
    return g.m

def _ember_mat(strength):
    """Charred rubble with glowing cracks (night)."""
    if "Embers" in _MC:
        return _MC["Embers"]
    m = bpy.data.materials.new("Embers"); m.use_nodes = True
    nt = m.node_tree; N = nt.nodes; Ln = nt.links
    b = N["Principled BSDF"]; b.inputs["Base Color"].default_value = (0.03, 0.025, 0.02, 1); b.inputs["Roughness"].default_value = 0.95
    tc = N.new("ShaderNodeTexCoord"); vz = N.new("ShaderNodeTexVoronoi"); vz.inputs["Scale"].default_value = 0.6
    vz.feature = "DISTANCE_TO_EDGE"
    Ln.new(tc.outputs["Object"], vz.inputs["Vector"])
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 0.15
    Ln.new(tc.outputs["Object"], nz.inputs["Vector"])
    mr = N.new("ShaderNodeMapRange"); mr.inputs["From Min"].default_value = 0.08; mr.inputs["From Max"].default_value = 0.0
    Ln.new(vz.outputs["Distance"], mr.inputs["Value"])
    mr2 = N.new("ShaderNodeMapRange"); mr2.inputs["From Min"].default_value = 0.45; mr2.inputs["From Max"].default_value = 0.65
    Ln.new(nz.outputs["Fac"], mr2.inputs["Value"])
    mu = N.new("ShaderNodeMath"); mu.operation = "MULTIPLY"
    Ln.new(mr.outputs["Result"], mu.inputs[0]); Ln.new(mr2.outputs["Result"], mu.inputs[1])
    mu2 = N.new("ShaderNodeMath"); mu2.operation = "MULTIPLY"; mu2.inputs[1].default_value = strength
    Ln.new(mu.outputs[0], mu2.inputs[0])
    b.inputs["Emission Color"].default_value = (1.0, 0.32, 0.06, 1)
    Ln.new(mu2.outputs[0], b.inputs["Emission Strength"])
    _MC["Embers"] = m
    return m

# ---------------------------------------------------------------- geometry builders
def _rock_template(rnd, flat=1.0, n=11, boxy=False):
    """Angular chunk: convex hull of random points on a squashed sphere (or a box surface when boxy, which gives
    masonry-like blocks with broken corners). Returns (verts, faces) in unit size."""
    bm = bmesh.new()
    for _ in range(n):
        if boxy:
            v = Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1)))
            ax = rnd.randrange(3); v[ax] = math.copysign(1.0, v[ax])
            v.z *= 0.75 * flat
        else:
            v = Vector((rnd.gauss(0, 1), rnd.gauss(0, 1), rnd.gauss(0, 1))).normalized()
            v.x *= rnd.uniform(0.7, 1.0); v.y *= rnd.uniform(0.6, 1.0); v.z *= rnd.uniform(0.45, 0.8) * flat
        bm.verts.new(v * 0.5)
    r = bmesh.ops.convex_hull(bm, input=bm.verts)
    bmesh.ops.delete(bm, geom=[g for g in r["geom_interior"] if isinstance(g, bmesh.types.BMVert)], context="VERTS")
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    bm.verts.ensure_lookup_table()
    verts = [v.co.copy() for v in bm.verts]
    idx = {v: i for i, v in enumerate(bm.verts)}
    faces = [[idx[v] for v in f.verts] for f in bm.faces]
    bm.free()
    return verts, faces

def _euler_m(loc, rot):
    return Matrix.Translation(loc) @ (Matrix.Rotation(rot[2], 4, "Z") @ Matrix.Rotation(rot[1], 4, "Y") @ Matrix.Rotation(rot[0], 4, "X"))

class Chunks:
    """Accumulate many transformed rock templates / boxes into one mesh."""
    def __init__(self, seed, flat=1.0, ntmp=14, boxy_frac=0.4):
        rnd = random.Random(seed)
        self.tmps = [_rock_template(rnd, flat, n=rnd.choice((10, 12, 16)), boxy=rnd.random() < boxy_frac) for _ in range(ntmp)]
        self.bm = bmesh.new()
        self.rnd = rnd
    def add(self, loc, size, mi=0, rot=None, tmp=None, squash=(1, 1, 1)):
        rnd = self.rnd
        vs, fs = self.tmps[tmp if tmp is not None else rnd.randrange(len(self.tmps))]
        rot = rot if rot is not None else (rnd.uniform(-0.5, 0.5), rnd.uniform(-0.5, 0.5), rnd.uniform(0, 6.28))
        M = _euler_m(loc, rot)
        S = Matrix.Diagonal((size * squash[0], size * squash[1], size * squash[2], 1))
        nv = [self.bm.verts.new((M @ S) @ v) for v in vs]
        for f in fs:
            try:
                ff = self.bm.faces.new([nv[i] for i in f]); ff.material_index = mi
            except ValueError:
                pass
    def box(self, center, size, rot=(0, 0, 0), mi=0):
        self.box_m(_euler_m(center, rot), size, mi)
    def box_m(self, M, size, mi=0):
        r = bmesh.ops.create_cube(self.bm, size=1)
        bmesh.ops.transform(self.bm, matrix=M @ Matrix.Diagonal((*size, 1)), verts=r["verts"])
        for f in {f for v in r["verts"] for f in v.link_faces}:
            f.material_index = mi
    def beam(self, p0, p1, t=0.3, mi=0, up=Vector((0, 0, 1))):
        """Square timber from p0 to p1 (world vectors)."""
        d = p1 - p0
        q = d.to_track_quat("X", "Z").to_matrix().to_4x4()
        self.box_m(Matrix.Translation((p0 + p1) / 2) @ q, (d.length, t, t), mi)
    def prism(self, M, poly, thick, mi=0):
        """Flat polygon (list of (u, z)) in the local x-z plane, extruded along local y by thick."""
        f0 = [self.bm.verts.new(M @ Vector((u, -thick / 2, z))) for u, z in poly]
        f1 = [self.bm.verts.new(M @ Vector((u, thick / 2, z))) for u, z in poly]
        fs = [self.bm.faces.new(f0), self.bm.faces.new(list(reversed(f1)))]
        for i in range(len(poly)):
            j = (i + 1) % len(poly)
            fs.append(self.bm.faces.new((f0[j], f1[j], f1[i], f0[i])))
        for f in fs:
            f.material_index = mi
    def rough_block(self, loc, size, rot, squash, seed, mi=0, disp=0.4):
        """Big wall chunk: boxy hull, subdivided, with stepped cell-noise displacement (~disp m) so the faces
        look chipped instead of gem-like."""
        rnd = random.Random(seed * 7 + 3)
        t = bmesh.new()
        for _ in range(22):
            v = Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1)))
            ax = rnd.randrange(3); v[ax] = math.copysign(1.0, v[ax])
            t.verts.new(v * 0.5)
        r = bmesh.ops.convex_hull(t, input=t.verts)
        bmesh.ops.delete(t, geom=[g for g in r["geom_interior"] if isinstance(g, bmesh.types.BMVert)], context="VERTS")
        bmesh.ops.delete(t, geom=[v for v in t.verts if not v.link_faces], context="VERTS")
        bmesh.ops.subdivide_edges(t, edges=t.edges[:], cuts=3, use_grid_fill=True)
        t.normal_update()
        M = _euler_m(loc, rot)
        S = Matrix.Diagonal((size * squash[0], size * squash[1], size * squash[2], 1))
        R3 = M.to_3x3()
        off = Vector((seed * 13.1, seed * 7.7, seed * 3.3))
        nv = {}
        for v in t.verts:
            w = (M @ S) @ v.co
            nrm = (R3 @ v.normal).normalized()
            d = disp * (0.8 * noise.cell(w * 0.42 + off) + 0.6 * noise.fractal(w * 0.18 + off, 0.5, 2.0, 3)) \
                + 0.06 * size * noise.noise(w * 0.05 + off)
            nv[v] = self.bm.verts.new(w + nrm * d)
        for f in t.faces:
            try:
                ff = self.bm.faces.new([nv[v] for v in f.verts]); ff.material_index = mi
            except ValueError:
                pass
        t.free()
    def build(self, name, mats, coll):
        bm = self.bm
        bm.normal_update()
        ob = L.obj_from_bm(name, bm, mats, coll)
        for p in ob.data.polygons:
            p.use_smooth = False
        return ob

# ---------------------------------------------------------------- town edits
class TownEdit:
    def __init__(self, year):
        self.year = float(year)
        self.obs = [o for o in (bpy.data.objects.get("Town"), bpy.data.objects.get("TownTrees")) if o]
        self.data = []
        for o in self.obs:
            me = o.data
            n = len(me.vertices)
            co = [0.0] * (3 * n); me.vertices.foreach_get("co", co)
            born = [0.0] * n; me.attributes["born"].data.foreach_get("value", born)
            dead = [0.0] * n; me.attributes["dead"].data.foreach_get("value", dead)
            rot = [0.0] * (3 * n); me.attributes["rot"].data.foreach_get("vector", rot)
            self.data.append({"co": co, "born": born, "dead": dead, "rot": rot, "n": n})
        self.grid = {}
        for k, d in enumerate(self.data):
            for i in range(d["n"]):
                x, y = d["co"][3 * i], d["co"][3 * i + 1]
                self.grid.setdefault((int(x // 25), int(y // 25)), []).append((k, i))
    def alive(self, k, i):
        d = self.data[k]
        return d["born"][i] <= self.year < d["dead"][i]
    def near(self, x, y, r, only_alive=True):
        out = []
        for gx in range(int((x - r) // 25), int((x + r) // 25) + 1):
            for gy in range(int((y - r) // 25), int((y + r) // 25) + 1):
                for k, i in self.grid.get((gx, gy), ()):
                    d = self.data[k]
                    px, py = d["co"][3 * i], d["co"][3 * i + 1]
                    if (px - x) ** 2 + (py - y) ** 2 < r * r and (not only_alive or self.alive(k, i)):
                        out.append((k, i, px, py))
        return out
    def kill(self, k, i):
        if self.alive(k, i):
            self.data[k]["dead"][i] = self.year
            return True
        return False
    def pos(self, k, i):
        d = self.data[k]
        return d["co"][3 * i], d["co"][3 * i + 1], d["rot"][3 * i + 2]
    def commit(self):
        for o, d in zip(self.obs, self.data):
            o.data.attributes["dead"].data.foreach_set("value", d["dead"])
            o.data.update()

# ---------------------------------------------------------------- pieces
def _ruin_pile(ch, x, y, ang, rnd, mi_roof, mi_wall, mi_timber, mi_dark, scale=1.0):
    """Collapsed house: low mound of roof tiles and plaster, broken beams, a wall stub or two."""
    ca, sa = math.cos(ang), math.sin(ang)
    def P(u, v, z):
        return Vector((x + ca * u - sa * v, y + sa * u + ca * v, z))
    s = scale
    ch.add(P(0, 0, 0.3), 9.5 * s, mi=mi_dark, rot=(0, 0, ang + rnd.uniform(-0.3, 0.3)), squash=(1.0, 1.3, 0.32))
    for _ in range(rnd.randint(2, 4)):     # tilted roof slabs
        ch.box(P(rnd.uniform(-3, 3) * s, rnd.uniform(-4, 4) * s, rnd.uniform(1.0, 2.6) * s),
               (rnd.uniform(4, 7) * s, rnd.uniform(3, 5) * s, 0.35),
               rot=(rnd.uniform(-0.6, 0.6), rnd.uniform(-0.5, 0.5), ang + rnd.uniform(-0.5, 0.5)), mi=mi_roof)
    if rnd.random() < 0.75:                # wall stub with a jagged top
        side = rnd.choice((-1, 1))
        hh = rnd.uniform(2, 5) * s
        ch.box(P(side * 4.0 * s, rnd.uniform(-2, 2), hh / 2), (0.7, rnd.uniform(4, 8) * s, hh),
               rot=(rnd.uniform(-0.12, 0.12), rnd.uniform(-0.1, 0.1), ang), mi=rnd.choice((mi_wall, mi_dark, mi_dark)))
        ch.add(P(side * 4.0 * s, rnd.uniform(-3, 3), hh), 1.6 * s, mi=mi_dark)
    for _ in range(rnd.randint(2, 5)):     # beams
        ch.box(P(rnd.uniform(-4, 4) * s, rnd.uniform(-5, 5) * s, rnd.uniform(0.8, 3.5) * s),
               (0.35, rnd.uniform(5, 9) * s, 0.35),
               rot=(rnd.uniform(-0.9, 0.9), rnd.uniform(-0.4, 0.4), rnd.uniform(0, 6.28)), mi=mi_timber)
    for _ in range(rnd.randint(4, 9)):     # loose chunks
        ch.add(P(rnd.uniform(-7, 7) * s, rnd.uniform(-8, 8) * s, 0.3), rnd.uniform(0.8, 2.2) * s, mi=rnd.choice((mi_wall, mi_roof, mi_dark)))

def _arch_outline(rnd, hw, ht):
    zs = ht * 0.45
    ol = []
    for k in range(8):                          # left side, bottom to top
        z = -3 + k / 7 * (zs + 3)
        ol.append((-hw * (1 + rnd.uniform(-0.12, 0.18)), z))
    n = 22
    for k in range(1, n):                       # ragged arch
        a = math.pi - k / n * math.pi
        rj = 1 + rnd.uniform(-0.16, 0.16) + (0.12 if k % 3 == 0 else 0)
        ol.append((math.cos(a) * hw * rj, zs + math.sin(a) * (ht - zs) * rj))
    for k in range(8):                          # right side, top to bottom
        z = zs - k / 7 * (zs + 3)
        ol.append((hw * (1 + rnd.uniform(-0.12, 0.18)), z))
    return ol, zs

def _outward(x, z, zs):
    v = Vector((x, z - zs * 0.8))
    return v.normalized() if v.length > 1e-6 else Vector((0, 1))

def _face_y(x, z, half_t, gate_half=15.0):
    if abs(x) < gate_half:
        return half_t - half_t * 0.2 * (z + 4) / 56
    return 5.0 - 1.2 * (z + 4) / 54

def _hole_cutters(name, center, hw, ht, depth, seed, coll, half_t):
    """1) prism with a ragged arch outline through the gatehouse; 2) a ring of overlapping boxes on both faces
    along the edge, cut 1-3 m deep, which bevels the hole into chipped, stepped masonry."""
    rnd = random.Random(seed)
    ol, zs = _arch_outline(rnd, hw, ht)
    bm = bmesh.new()
    f0 = [bm.verts.new((x, -depth, z)) for x, z in ol]
    f1 = [bm.verts.new((x, depth, z)) for x, z in ol]
    bm.faces.new(f0); bm.faces.new(list(reversed(f1)))
    for i in range(len(ol)):
        j = (i + 1) % len(ol)
        bm.faces.new((f0[i], f1[i], f1[j], f0[j]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    cut = L.obj_from_bm(name, bm, [], coll)
    cut.location = (center[0], center[1], 0); cut.hide_render = True; cut.display_type = "WIRE"
    bm = bmesh.new()
    for i in range(len(ol)):
        x0, z0 = ol[i]; x1, z1 = ol[(i + 1) % len(ol)]
        if max(z0, z1) < 0.5:
            continue
        for t in (0.0, 0.5):
            x, z = x0 + (x1 - x0) * t, z0 + (z1 - z0) * t
            o = _outward(x, z, zs)
            for side in (-1, 1):
                for layer in range(2):          # two steps: a wide shallow one and a narrower deeper one
                    reach = rnd.uniform(1.6, 3.2) if layer == 0 else rnd.uniform(0.6, 1.6)
                    dep = rnd.uniform(1.0, 2.0) if layer == 0 else rnd.uniform(2.2, 3.4)
                    s = rnd.uniform(2.0, 4.0)
                    c = Vector((x + o.x * reach * 0.5, 0, z + o.y * reach * 0.5))
                    fy = side * _face_y(x, z, half_t)
                    r = bmesh.ops.create_cube(bm, size=1)
                    M = Matrix.Translation((c.x, fy, c.z)) @ Matrix.Rotation(rnd.uniform(-0.4, 0.4), 4, "Y")
                    bmesh.ops.transform(bm, matrix=M @ Matrix.Diagonal((s + reach, dep * 2, s + reach * 0.6, 1)), verts=r["verts"])
    chip = L.obj_from_bm(name + "Chips", bm, [], coll)
    chip.location = (center[0], center[1], 0); chip.hide_render = True; chip.display_type = "WIRE"
    return cut, chip, ol, zs

def grime_halo(name, hole, ol, zs, half_t, coll, seed):
    """Decal rings on both faces of the gate, from just outside the chipped edge to 15-25 m out."""
    rnd = random.Random(seed)
    bm = bmesh.new()
    lay = bm.verts.layers.float.new("fade")
    pts = [(x, z) for x, z in ol if z > -0.5]
    reach = [rnd.uniform(15, 25) for _ in pts]
    for k in range(2):                          # smooth the reach a little
        reach = [(reach[i - 1] + reach[i] * 2 + reach[(i + 1) % len(reach)]) / 4 for i in range(len(reach))]
    K = 6
    for side in (-1, 1):
        rows = []
        for i, (x, z) in enumerate(pts):
            o = _outward(x, z, zs)
            row = []
            for k in range(K + 1):
                s = k / K
                d = 3.0 + s * reach[i]
                X, Z = x + o.x * d, max(0.25, z + o.y * d)
                Z = min(Z, 49.0)
                fy = side * (_face_y(X, Z, half_t) + 0.2)
                v = bm.verts.new((hole[0] + X, hole[1] + fy, Z)); v[lay] = (1.0 - s)
                row.append(v)
            rows.append(row)
        for i in range(len(rows) - 1):
            for k in range(K):
                q = (rows[i][k], rows[i][k + 1], rows[i + 1][k + 1], rows[i + 1][k])
                try:
                    bm.faces.new(q if side > 0 else tuple(reversed(q)))
                except ValueError:
                    pass
    ob = L.obj_from_bm(name, bm, [grime_mat()], coll)
    ob.visible_shadow = False
    return ob

def breach_gate(gname, hole, M, coll, inward, seed, ch, lm):
    """Blow a ragged hole through gatehouse gname (chipped stepped edge, grime halo), remove its door."""
    g = bpy.data.objects.get(gname)
    d = bpy.data.objects.get(gname + "_Door")
    if d:
        d.hide_render = True; d.hide_viewport = True
    if not g:
        return None, 0
    half_t = g.dimensions.y / 2
    cut, chip, ol, zs = _hole_cutters(gname + "_Cutter", (hole[0], hole[1]), hole[2], hole[3], 14.0, seed, coll, half_t)
    for nm, ob in (("Breach", cut), ("BreachChips", chip)):
        mod = g.modifiers.new(nm, "BOOLEAN"); mod.operation = "DIFFERENCE"; mod.object = ob
        try:
            mod.solver = "EXACT"; mod.use_self = True
        except (TypeError, AttributeError):
            pass
    grime_halo(gname + "_Grime", hole, ol, zs, half_t, coll, seed + 5)
    # chipped blocks still clinging to the cut edge (boxes, partly sunk into the masonry)
    rnd = random.Random(seed + 10)
    for x, z in ol:
        if z < 0.5:
            continue
        o = _outward(x, z, zs)
        for fy in (-0.75, -0.35, 0.0, 0.35, 0.75):
            if rnd.random() < 0.45:
                s = rnd.uniform(1.2, 3.0)
                ch.box(Vector((hole[0] + x + o.x * rnd.uniform(0.5, 2.0), hole[1] + fy * half_t, z + o.y * rnd.uniform(0.5, 2.0))),
                       (s, s * rnd.uniform(0.8, 1.6), s * rnd.uniform(0.5, 0.9)),
                       rot=(rnd.uniform(-0.3, 0.3), rnd.uniform(-0.3, 0.3), rnd.uniform(-0.3, 0.3)), mi=lm["stone"])
    # stubs of the door: splintered planks hanging at the sides
    for sx in (-1, 1):
        for k in range(4):
            ch.box(Vector((hole[0] + sx * (hole[2] - 1.5 - k * 0.9), hole[1] - inward * 3.0, rnd.uniform(1, 6))),
                   (0.6, 0.5, rnd.uniform(4, 9)), rot=(rnd.uniform(-0.3, 0.3), sx * rnd.uniform(0.1, 0.5), 0), mi=lm["wood"])
    return ol, half_t

def _rubble_size(rnd, big):
    """Power-law chunk sizes: ~2 % 4-6 m, ~16 % 1.5-2.5 m, the rest 0.3-0.9 m (scaled by big)."""
    u = rnd.random()
    if u < 0.025:
        return rnd.uniform(4.0, 6.0) * big
    if u < 0.21:
        return rnd.uniform(1.5, 2.5) * big
    return rnd.uniform(0.3, 0.9) * big

def rubble_fan(ch, origin, inward, spread, length, count, big, seed, lm, edit, crush_frac=0.55, door=True):
    """Debris thrown through a breach: chunks densest near the hole, thinning out over `length` metres inside
    a cone of half-angle `spread` around direction `inward` (unit 2D). Big chunks stay closer to the hole."""
    rnd = random.Random(seed)
    base = math.atan2(inward[1], inward[0])
    for _ in range(count):
        s = _rubble_size(rnd, big)
        t = rnd.random() ** (1.8 + s * 0.25)
        dist = 6 + t * length
        a = base + rnd.gauss(0, spread * (0.45 + 0.4 * t))
        x, y = origin[0] + math.cos(a) * dist, origin[1] + math.sin(a) * dist
        if inward[1] > 0 and origin[1] < -1 and not L.in_district(x, y, 7):
            continue
        if door and rnd.random() < 0.05:
            ch.box(Vector((x, y, 0.4)), (rnd.uniform(3, 7), rnd.uniform(0.8, 1.6), 0.5),
                   rot=(rnd.uniform(-0.2, 0.2), rnd.uniform(-0.2, 0.2), rnd.uniform(0, 6.28)), mi=lm["wood"])
            continue
        mi = rnd.choice((lm["stone"], lm["stone"], lm["stone"], lm["dark"], lm["stone_l"]))
        ch.add(Vector((x, y, s * 0.15)), s, mi=mi)
    # big pile in and just inside the hole
    for _ in range(170):
        a = base + rnd.gauss(0, 0.45); dist = rnd.uniform(-7, 40)
        x, y = origin[0] + math.cos(a) * dist + rnd.uniform(-9, 9) * abs(inward[1]), origin[1] + math.sin(a) * dist
        f = max(0.0, 1.0 - max(0, dist) / 45)
        s = _rubble_size(rnd, 1.0) * (0.8 + 1.6 * f) + 0.5
        ch.add(Vector((x, y, rnd.uniform(0, 6.0) * f)), s, mi=rnd.choice((lm["stone"], lm["stone"], lm["dark"])))
    # flatten houses in the fan core
    hit = []
    for k, i, px, py in edit.near(origin[0] + inward[0] * length * 0.4, origin[1] + inward[1] * length * 0.4, length * 0.75):
        dx, dy = px - origin[0], py - origin[1]
        dist = math.hypot(dx, dy)
        da = abs((math.atan2(dy, dx) - base + math.pi) % (2 * math.pi) - math.pi)
        p = (1 - dist / (length * crush_frac * 1.6)) * (1 - da / (spread * 1.4))
        if p > rnd.random() * 0.45 and edit.kill(k, i):
            hit.append((k, i))
    return hit

class Decals:
    """Ground decals as triangle fans with a 'rad' attribute (0 centre, 1 rim)."""
    def __init__(self):
        self.bm = bmesh.new()
        self.lay = self.bm.verts.layers.float.new("rad")
    def fan(self, cx, cy, ring, z):
        c = self.bm.verts.new((cx, cy, z)); c[self.lay] = 0.0
        mids = [self.bm.verts.new((cx + (x - cx) * 0.5, cy + (y - cy) * 0.5, z)) for x, y in ring]
        outs = [self.bm.verts.new((x, y, z)) for x, y in ring]
        for v in mids:
            v[self.lay] = 0.5
        for v in outs:
            v[self.lay] = 1.0
        n = len(ring)
        for i in range(n):
            j = (i + 1) % n
            self.bm.faces.new((c, mids[i], mids[j]))
            self.bm.faces.new((mids[i], outs[i], outs[j], mids[j]))
    def crater(self, x, y, r, rnd, z=0.24):
        ring = []
        for k in range(20):
            a = k / 20 * 2 * math.pi
            rr = r * rnd.uniform(0.75, 1.2)
            ring.append((x + math.cos(a) * rr, y + math.sin(a) * rr))
        self.fan(x, y, ring, z)
    def build(self, name, m, coll):
        ob = L.obj_from_bm(name, self.bm, [m], coll)
        ob.visible_shadow = False
        return ob

def scar_ring(origin, inward, spread, length, seed):
    rnd = random.Random(seed)
    base = math.atan2(inward[1], inward[0])
    ring = [(origin[0] - inward[0] * 4 + math.cos(base + math.pi / 2) * 14, origin[1] - inward[1] * 4 + math.sin(base + math.pi / 2) * 14)]
    n = 26
    for k in range(n + 1):
        a = base - spread + 2 * spread * k / n
        r = length * (0.55 + 0.45 * math.cos((k / n - 0.5) * math.pi)) * rnd.uniform(0.75, 1.1)
        ring.append((origin[0] + math.cos(a) * r, origin[1] + math.sin(a) * r))
    ring.append((origin[0] - inward[0] * 4 - math.cos(base + math.pi / 2) * 14, origin[1] - inward[1] * 4 - math.sin(base + math.pi / 2) * 14))
    return ring

def block_arc(x, y, t):
    """Point on the arc from the gate top to the impact (x, y) at parameter t in [0, 1]."""
    p0 = Vector((OG.x, OG.y + 4, 42.0)); p1 = Vector((x, y, 0.0))
    dist = (p1 - p0).xy.length
    hmax = 60 + dist * 0.28
    p = p0.lerp(p1, t)
    p.z = p0.z * (1 - t) + 4 * hmax * t * (1 - t) + p1.z * t
    return p

# ---------------------------------------------------------------- yeager house
def yeager_house(ch, x, y, ang, lm, rnd, bs):
    """Modest 2-storey half-timbered house crushed by a wall chunk (bible 1.8): the back gable still stands with its
    dark X-braced frame on cream infill, half the tiled roof hangs from it slumped 30 deg into the block, the other
    half lies broken on the rubble."""
    H = Matrix.Translation((x, y, 0)) @ Matrix.Rotation(ang, 4, "Z")
    def P(u, v, z):
        return H @ Vector((u, v, z))
    w, d = 9.0, 12.0
    gf, eave = 3.6, 7.6
    ridge = eave + w / 2 * math.tan(math.radians(50))
    # ground floor: rough beige stone, broken
    ch.box_m(H @ Matrix.Translation((-w / 2, 0.8, gf / 2)), (0.8, d - 1.6, gf), lm["beige"])
    ch.box_m(H @ Matrix.Translation((w / 2, d / 4, gf * 0.4)), (0.8, d / 2, gf * 0.8), lm["beige"])
    ch.box_m(H @ Matrix.Translation((0, d / 2, gf / 2)), (w + 0.8, 0.8, gf), lm["beige"])
    ch.box_m(H @ Matrix.Translation((-2.6, -d / 2, gf * 0.45)), (3.8, 0.8, gf * 0.9), lm["beige"])
    # standing back gable: cream infill, top-right corner broken off along a ragged line
    gable = [(-w / 2, gf), (w / 2, gf), (w / 2, 5.4), (3.6, 6.5), (3.1, 8.3), (1.9, 9.0), (1.1, 11.4), (0.0, ridge), (-w / 2, eave)]
    GM = H @ Matrix.Translation((0, d / 2 - 0.1, 0)) @ Matrix.Rotation(-0.05, 4, "X")
    ch.prism(GM, gable, 0.45, lm["plaster"])
    # timber frame on both faces of the gable
    for fy in (-0.32, 0.32):
        def B(u0, z0, u1, z1, t=0.3):
            ch.beam(GM @ Vector((u0, fy, z0)), GM @ Vector((u1, fy, z1)), t, lm["timber"])
        B(-w / 2, gf, w / 2, gf, 0.38)                      # sill
        B(-w / 2, 5.6, 3.5, 5.6)                            # mid rail
        B(-w / 2, eave, 2.9, eave, 0.34)                    # eave plate (broken off at the right)
        for u, top in ((-w / 2, eave), (-1.5, eave), (1.5, 8.6), (w / 2, 5.4)):
            B(u, gf, u, top, 0.34)                          # posts
        B(-w / 2, gf, -1.5, 5.6); B(-1.5, gf, -w / 2, 5.6)  # X braces
        B(-w / 2, 5.6, -1.5, eave); B(-1.5, 5.6, -w / 2, eave)
        B(-1.5, gf, 1.5, 5.6); B(1.5, gf, -1.5, 5.6)
        B(1.5, gf, w / 2, 5.4)
        B(-w / 2, eave, 0.0, ridge, 0.36)                   # gable rafter
        B(0.0, eave, 0.0, ridge)                            # king post
        B(-w / 2 + 0.3, eave, 0.0, 10.4); B(0.0, 10.4, 1.4, 10.9)
        for zz in (8.6, 10.0):                              # small upper braces
            B(-2.6, eave, -1.0, zz)
        # windows: dark recesses in the panels
        for u in (-3.0, 0.0):
            ch.box_m(GM @ Matrix.Translation((u, fy * 1.05, 6.6)), (1.1, 0.12, 1.2), lm["dark"])
    # left roof slope: still hinged on the gable, the front end slumped 30 deg down into the block
    pivot = Vector((0, d / 2, ridge))
    slope = math.radians(50)
    sl = (w / 2) / math.cos(slope) + 0.9
    Rm = Matrix.Translation(pivot) @ Matrix.Rotation(math.radians(30), 4, "X") @ Matrix.Translation(-pivot)
    for part, (v0, v1) in enumerate(((d / 2 + 0.6, 0.5), (0.2, -d / 2 + 1.5))):
        vc, vl = (v0 + v1) / 2, abs(v0 - v1)
        tw = Matrix.Rotation(0.12 * part, 4, "Y") if part else Matrix.Identity(4)
        Ms = Rm @ Matrix.Translation((-w / 4 - 0.35, vc, (ridge + eave) / 2 + 0.3)) @ Matrix.Rotation(slope, 4, "Y") @ tw
        ch.box_m(H @ Ms, (sl, vl, 0.35), lm["roof"])
        for u in (-sl / 2 + 0.6, 0.0, sl / 2 - 0.6):       # rafters under the tiles, sticking out at the break
            ch.box_m(H @ Ms @ Matrix.Translation((u, -0.4, -0.35)), (0.28, vl + 1.4, 0.28), lm["timber"])
    # ridge beam hanging down from the gable
    ch.beam(P(0, d / 2, ridge - 0.3), P(0.8, -1.5, bs * 0.6), 0.4, lm["timber"])
    # right slope: broken, big pieces lying on the rubble at angles
    for k, (u, v, z, a, b) in enumerate(((4.8, 2.5, 2.6, 0.55, 0.3), (6.5, -3.0, 1.4, 0.25, -0.2), (3.0, -5.5, 3.2, -0.6, 0.5))):
        ch.box_m(H @ _euler_m(Vector((u, v, z)), (b, a, rnd.uniform(-0.3, 0.3))), (4.6, 4.5 - k * 0.6, 0.35), lm["roof"])
    for _ in range(12):
        p0 = P(rnd.uniform(-5, 6), rnd.uniform(-6, 6), rnd.uniform(0.3, 2.5))
        ch.beam(p0, p0 + Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-0.3, 0.8))).normalized() * rnd.uniform(3, 7),
                0.3, lm["timber"])
    for _ in range(45):
        ch.add(P(rnd.uniform(-8, 8), rnd.uniform(-9, 9), 0.2), rnd.uniform(0.4, 1.8),
               mi=rnd.choice((lm["roof"], lm["roof"], lm["beige"], lm["plaster"], lm["dark"])))
    # front steps with a wooden post-and-rail handrail (S3 flashback), facing the street
    for k in range(5):
        ch.box(P(2.8, -d / 2 - 1.0 - k * 0.6, (0.3 + (4 - k) * 0.3) / 2), (2.4, 0.6, 0.3 + (4 - k) * 0.3), rot=(0, 0, ang), mi=lm["beige"])
    for k in range(3):
        ch.box(P(4.2, -d / 2 - 0.9 - k * 1.2, 0.9 + (2 - k) * 0.3), (0.18, 0.18, 1.8), rot=(0, 0, ang), mi=lm["timber"])
    ch.beam(P(4.2, -d / 2 - 0.9, 2.35), P(4.2, -d / 2 - 3.3, 1.75), 0.15, lm["timber"])

# ---------------------------------------------------------------- settlement ground
def settlement_earth(edit, coll):
    """Packed-earth ground between the packed houses of the settlement north of the inner gate."""
    hs = [(edit.data[0]["co"][3 * i], edit.data[0]["co"][3 * i + 1]) for i in range(edit.data[0]["n"])
          if edit.data[0]["co"][3 * i + 1] > 1.0]
    grid = {}
    for x, y in hs:
        grid.setdefault((int(x // 20), int(y // 20)), []).append((x, y))
    step = 4.0
    xs = [-340 + step * i for i in range(int(680 / step) + 1)]
    ys = [1.0 + step * j for j in range(int(300 / step) + 1)]
    bm = bmesh.new()
    lay = bm.verts.layers.float.new("earth")
    rows = []
    for y in ys:
        row = []
        for x in xs:
            dens = 0.0
            gx, gy = int(x // 20), int(y // 20)
            for i in (-1, 0, 1):
                for j in (-1, 0, 1):
                    for hx, hy in grid.get((gx + i, gy + j), ()):
                        dd = (hx - x) ** 2 + (hy - y) ** 2
                        if dd < 400:
                            dens += 1.0 - dd / 400
            if y < 30:                      # the road / gate apron in front of the inner gate
                dens += max(0.0, 1.0 - abs(x) / 60) * 2.0
            v = bm.verts.new((x, y, L.height(x, y) + 0.3)); v[lay] = min(1.0, dens / 1.6)
            row.append(v)
        rows.append(row)
    for j in range(len(rows) - 1):
        for i in range(len(xs) - 1):
            bm.faces.new((rows[j][i], rows[j][i + 1], rows[j + 1][i + 1], rows[j + 1][i]))
    ob = L.obj_from_bm("SettlementEarth", bm, [earth_mat()], coll)
    ob.visible_shadow = False
    return ob

# ---------------------------------------------------------------- night
def night_world(ctx):
    w = ctx.get("world") or bpy.context.scene.world
    nt = w.node_tree
    bg = nt.nodes.get("Background")
    if bg:
        for lk in list(bg.inputs[0].links):
            nt.links.remove(lk)
        bg.inputs[0].default_value = (0.022, 0.03, 0.065, 1)
        bg.inputs[1].default_value = 1.0
    for n in nt.nodes:
        if n.type == "VALTORGB":
            e = n.color_ramp.elements
            e[0].position, e[0].color = 0.0, (0.22, 0.07, 0.035, 1)        # horizon reddened by the fires
            e[1].position, e[1].color = 0.30, (0.008, 0.012, 0.034, 1)
            el = n.color_ramp.elements.new(0.10); el.color = (0.07, 0.04, 0.05, 1)
        if n.type == "BACKGROUND" and n != bg:
            n.inputs[1].default_value = 1.0
    sun = ctx.get("sun") or bpy.data.objects.get("Sun")
    if sun:
        sun.data.energy = float(os.environ.get("MOON_E", "0.15"))
        sun.data.color = (0.45, 0.55, 0.9)
        el, az = math.radians(28), math.radians(-120)
        d = Vector((-math.cos(el) * math.cos(az), -math.cos(el) * math.sin(az), -math.sin(el)))
        sun.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
        mp = -d * 14000                 # moon disc in the sky behind the town (opposite the light direction)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=150, location=mp, segments=24, ring_count=12)
        mo = bpy.context.active_object; mo.name = "Moon"
        mm = bpy.data.materials.new("Moon"); mm.use_nodes = True; N = mm.node_tree.nodes
        N.remove(N["Principled BSDF"]); em = N.new("ShaderNodeEmission")
        em.inputs["Color"].default_value = (0.85, 0.9, 1.0, 1); em.inputs["Strength"].default_value = 6
        mm.node_tree.links.new(em.outputs[0], N["Material Output"].inputs["Surface"])
        mo.data.materials.append(mm); mo.visible_shadow = False
    hz = bpy.data.objects.get("Haze")
    if hz and hz.data.materials:
        pv = next((n for n in hz.data.materials[0].node_tree.nodes if n.type == "PRINCIPLED_VOLUME"), None)
        if pv:
            pv.inputs["Color"].default_value = (0.5, 0.55, 0.7, 1)
            pv.inputs["Density"].default_value = pv.inputs["Density"].default_value * 2.5
    os.environ.setdefault("EXPO", "-0.45")

def smoke_canopy(coll, blazes, gain):
    """Flat smoke ceiling over the burning town (900 x 700 x 80 m, z 150-230), lit orange from below:
    emission #FF7030 masked by an image of blurred blobs over the blazes."""
    if nosmoke():
        return
    cx, cy, hx, hy = 0.0, -360.0, 450.0, 350.0
    W_, H_ = 180, 140
    img = bpy.data.images.new("CanopyMask", W_, H_, float_buffer=True)
    px = [0.0] * (W_ * H_ * 4)
    for j in range(H_):
        wy = cy - hy + (j + 0.5) / H_ * 2 * hy
        for i in range(W_):
            wx = cx - hx + (i + 0.5) / W_ * 2 * hx
            v = 0.0
            for bx, by, br in blazes:
                dd = (wx - bx) ** 2 + (wy - by) ** 2
                s = (br * 3.0 + 40.0) ** 2
                v += math.exp(-dd / s)
            v = min(1.0, v)
            k = 4 * (j * W_ + i)
            px[k] = px[k + 1] = px[k + 2] = v; px[k + 3] = 1.0
    img.pixels.foreach_set(px)
    g = G("SmokeCanopy")
    p = g.coords()
    x, y, z = g.sep(p)
    uv = g.v_("ADD", g.v_("SCALE", p, scale=0.5), (0.5, 0.5, 0.0))
    it = g.N.new("ShaderNodeTexImage"); it.image = img; it.extension = "EXTEND"; it.interpolation = "Cubic"
    g.Ln.new(uv, it.inputs["Vector"])
    mask = g.sep(it.outputs["Color"])[0]
    n = g.noise(g.v_("MULTIPLY", p, (hx / 110, hy / 110, 40 / 60)), 1.0, 6, 0.6, 0.3)
    vert = g.m_("SUBTRACT", 1.0, g.m_("ABSOLUTE", z))
    edge = g.m_("MULTIPLY", g.m_("MULTIPLY", g.m_("SUBTRACT", 1.0, g.m_("ABSOLUTE", x)), 5.0, clamp=True),
                g.m_("MULTIPLY", g.m_("SUBTRACT", 1.0, g.m_("ABSOLUTE", y)), 5.0, clamp=True))
    shape = g.m_("MULTIPLY", g.m_("MULTIPLY", vert, edge), g.m_("SUBTRACT", g.m_("MULTIPLY", n, 2.4), 0.55, clamp=True))
    shape = g.m_("MULTIPLY", shape, g.m_("ADD", g.m_("MULTIPLY", mask, 1.2), 0.35))
    pv = g.N.new("ShaderNodeVolumePrincipled"); pv.inputs["Color"].default_value = (*SMOKE, 1)
    g.Ln.new(g.m_("MULTIPLY", shape, 0.002 * 2.0), pv.inputs["Density"])
    pv.inputs["Emission Color"].default_value = (*lin("#FF7030"), 1)
    ce = float(os.environ.get("AOT_CANOPY_E", "1")) * gain
    es = g.m_("MULTIPLY", g.m_("MULTIPLY", shape, g.m_("ADD", g.m_("MULTIPLY", mask, 1.0), 0.12)), 0.05 * ce)
    g.Ln.new(es, pv.inputs["Emission Strength"])
    g.Ln.new(pv.outputs[0], g.out.inputs["Volume"])
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=2.0)
    ob = L.obj_from_bm("SmokeCanopy", bm, [g.m], coll)
    ob.location = (cx, cy, 190.0); ob.scale = (hx, hy, 40.0)

# ---------------------------------------------------------------- build
def build(M, year, ctx):
    st = state()
    if st == "intact":
        return
    lv = level()
    night = st == "night"
    coll = L.new_coll("States845")
    rnd = random.Random(845)
    edit = TownEdit(year)
    gain = float(os.environ.get("AOT_FIRE_GAIN", "1"))
    dust_k = float(os.environ.get("AOT_DUST", "1"))
    arc_t = os.environ.get("AOT_ARC_T", "")
    arc_t = min(1.0, max(0.0, float(arc_t))) if arc_t else 1.0

    m_rock = stone_mat(M, "RubbleStone", 0.7)
    m_rock_l = stone_mat(M, "RubbleStoneL", 0.85)
    m_dark = stone_mat(M, "RubbleDark", 0.42)
    m_block = stone_mat(M, "BlockStone", 0.8, scale=0.12)
    m_beige = L.mat("Beige845", BEIGE, 0.92, var=0.2, var_scale=0.6, color2=lin("#AC9C7E"))
    m_plaster = L.mat("Infill845", INFILL, 0.9, var=0.15, var_scale=0.4, color2=tuple(c * 0.8 for c in INFILL))
    m_timber = L.mat("TimberDark845", TIMBER, 0.85, var=0.2, var_scale=1.5)
    m_tile = tile_mat()
    mats = [m_rock, m_rock_l, m_dark, m_tile, M["gate"], m_plaster, m_tile, m_timber, m_beige]
    lm = {"stone": 0, "stone_l": 1, "dark": 2, "roof": 3, "wood": 4, "plaster": 5, "roof2": 6, "timber": 7, "beige": 8}
    if night:
        mats.append(_ember_mat(9.0)); lm["ember"] = 9
    ch = Chunks(seed=11)
    ruins = Chunks(seed=12, ntmp=10)
    blocks = Chunks(seed=21, flat=1.7, ntmp=9)
    craters = Decals()
    scars = Decals()
    fires = Fires(gain)
    burning = []           # ruin / house positions that may burn

    # ---- outer gate breach (kick from the south, debris into the town)
    breach_gate("OuterGate", OUTER_HOLE, M, coll, inward=1, seed=3, ch=ch, lm=lm)
    hit = rubble_fan(ch, (OG.x, OG.y + 9), (0, 1), 0.55, 230, 3400, 1.15, 31, lm, edit)
    scars.fan(OG.x, OG.y + 60, scar_ring((OG.x, OG.y + 8), (0, 1), 0.6, 215, 4), 0.22)
    for k, i in hit:
        x, y, a = edit.pos(k, i)
        if k == 0:
            _ruin_pile(ruins, x, y, a, rnd, 3, 5, 7, 2, scale=rnd.uniform(0.8, 1.0))
            burning.append((x, y))
    # tan dust cloud bursting in through the hole right after the kick
    dd = (0.05 if lv == 1 else 0.025) * dust_k
    billow("BreachDust", coll, (OG.x + 4, OG.y + 36, 14), (40, 30, 22), DUST, dd, rot=(0, 0, 0.2))
    billow("BreachDust2", coll, (OG.x - 26, OG.y + 22, 12), (24, 20, 15), DUST, dd * 0.9)
    billow("BreachDust3", coll, (OG.x + 30, OG.y + 58, 14), (26, 22, 17), DUST, dd * 0.8)
    if lv == 1:
        billow("BreachDustHigh", coll, (OG.x + 18, OG.y + 30, 52), (30, 26, 22), DUST, dd * 0.55)

    # ---- thrown blocks
    airborne = []
    BS_AIR, BS_LAND = 1.5, 1.3
    for n, (x, y, s0, sd) in enumerate(IMPACTS):
        tl = min(1.0, arc_t * (1.0 + n * 0.04))          # farther blocks land a moment later
        if tl < 1.0:
            s = s0 * BS_AIR
            p = block_arc(x, y, tl)
            rr = random.Random(sd)
            blocks.rough_block(p, s, (rr.uniform(0, 6), rr.uniform(0, 6), rr.uniform(0, 6)), (1.0, 0.8, 0.75), sd, mi=0, disp=0.5)
            airborne.append((p, s, x, y, tl))
            continue
        s = s0 * BS_LAND
        rr = random.Random(sd)
        # incoming direction (from the gate): skid scar extends past the impact
        dv = Vector((x - OG.x, y - OG.y)).normalized()
        yb = math.hypot(x - YEAGER_HOUSE[0], y - YEAGER_HOUSE[1]) < 5
        bc = Vector((x + dv.x * (0 if yb else 4), y + dv.y * (0 if yb else 4), s * (0.36 if yb else 0.2)))
        blocks.rough_block(bc, s, (rr.uniform(-0.35, 0.35), rr.uniform(-0.35, 0.35), math.atan2(dv.y, dv.x)),
                           (1.15, 0.85, 0.85), sd, mi=0, disp=0.4)
        for _ in range(40):      # mound of crushed masonry heaped against the block
            a = rr.uniform(0, 6.28); d_ = rr.uniform(s * 0.3, s * 0.9)
            ch.add(Vector((x + dv.x * 4 + math.cos(a) * d_, y + dv.y * 4 + math.sin(a) * d_, rr.uniform(0, s * 0.15))),
                   rr.uniform(1.0, 3.5), mi=rr.choice((lm["dark"], lm["stone"], lm["roof"])))
        # a broken-off second piece and a ring of fragments (power-law sizes)
        blocks.rough_block(Vector((x + dv.x * (s + 6) + rr.uniform(-4, 4), y + dv.y * (s + 6) + rr.uniform(-4, 4), s * 0.1)),
                           s * 0.42, (rr.uniform(0, 6), rr.uniform(-0.4, 0.4), rr.uniform(0, 6)), (1, 0.9, 0.7), sd + 50, mi=0, disp=0.3)
        for _ in range(260):
            a = rr.uniform(0, 6.28); d_ = s * (0.5 + 2.3 * rr.random() ** 1.5)
            sz = _rubble_size(rr, 0.8) * (1.6 - d_ / (s * 2.8))
            ch.add(Vector((x + math.cos(a) * d_ + dv.x * d_ * 0.6, y + math.sin(a) * d_ + dv.y * d_ * 0.6, 0.15)),
                   max(0.3, sz), mi=rr.choice((lm["stone"], lm["stone"], lm["dark"], lm["roof"])))
        craters.crater(x + dv.x * 6, y + dv.y * 6, s0 * 2.6, rr)
        # crushed houses: around the impact plus a skid zone back along the arc
        killed = []
        for cx, cy, r in ((x, y, s0 * 2.1 + 8), (x - dv.x * s0 * 2.0, y - dv.y * s0 * 2.0, s0 * 1.3 + 5),
                          (x + dv.x * s0 * 2.2, y + dv.y * s0 * 2.2, s0 * 1.5 + 5)):
            for k, i, px, py in edit.near(cx, cy, r):
                if edit.kill(k, i) and k == 0:
                    killed.append((px, py))
        for k, i, px, py in edit.near(x, y, s0 * 1.8 + 6, only_alive=False):
            if k == 1:
                edit.kill(k, i)
        for px, py in killed:
            if math.hypot(px - YEAGER_HOUSE[0], py - YEAGER_HOUSE[1]) < 7:
                continue
            _ruin_pile(ruins, px, py, rr.uniform(0, 6.28), rr, 3, 5, 7, 2, scale=rr.uniform(0.8, 1.05))
            burning.append((px, py))
        if lv >= 1 and n in (0, 2, 5, 7) or lv >= 2:
            fires.add(x - dv.x * s0, y - dv.y * s0, 0.4, 5.0 + rr.uniform(0, 2.5), smoke=False)
        # tan dust over the impact
        if lv <= 1 or n % 2 == 0:
            billow(f"ImpactDust{n}", coll, (x + dv.x * 8, y + dv.y * 8, s * 0.7), (s * 2.2, s * 1.9, s * 1.3), DUST,
                   (0.035 if lv == 1 else 0.02) * dust_k, rot=(0, 0, math.atan2(dv.y, dv.x)))
    for p, s, x, y, tl in airborne:
        # 20 m tan dust streak + small debris trailing each flying block
        q0 = block_arc(x, y, max(0.0, tl - 0.02)); tang = (p - q0).normalized()
        c = p - tang * (s * 0.5 + 10)
        billow(f"BlockTrail{x}_{y}", coll, c, (s * 0.45, 10.0 + s * 0.3, s * 0.45), DUST, 0.06 * dust_k,
               rot=tang.to_track_quat("Y", "Z").to_euler())
        for k in range(14):
            q = block_arc(x, y, max(0.0, tl - k * 0.006 - rnd.uniform(0, 0.006)))
            ch.add(q + Vector((rnd.gauss(0, s * 0.3), rnd.gauss(0, s * 0.3), rnd.gauss(0, s * 0.3))), rnd.uniform(0.6, 2.2) * (1 - k / 16), mi=lm["stone"])

    # ---- the Yeager house under a block
    yk = [(k, i, px, py) for k, i, px, py in edit.near(YEAGER_HOUSE[0], YEAGER_HOUSE[1], 14, only_alive=False) if k == 0]
    ya = edit.pos(yk[0][0], yk[0][1])[2] if yk else 0.0
    for k, i, px, py in edit.near(YEAGER_HOUSE[0], YEAGER_HOUSE[1], 10):
        edit.kill(k, i)
    if arc_t >= 1.0:
        yeager_house(ch, YEAGER_HOUSE[0], YEAGER_HOUSE[1], ya, lm, rnd, 12 * BS_LAND)

    # ---- inner gate burst (Armored Titan, S1E2), debris fanning north into the Wall Maria settlement
    if lv >= 2:
        breach_gate("InnerGate", INNER_HOLE, M, coll, inward=-1, seed=7, ch=ch, lm=lm)
        hit2 = rubble_fan(ch, (0, 9), (0, 1), 0.55, 170, 1800, 0.9, 41, lm, edit, crush_frac=0.65)
        hit2 += rubble_fan(ch, (0, -10), (0, -1), 0.6, 45, 220, 0.6, 42, lm, edit, door=False)
        scars.fan(0, 50, scar_ring((0, 8), (0, 1), 0.6, 150, 6), 0.0)
        for k, i in hit2:
            x, y, a = edit.pos(k, i)
            if k == 0:
                _ruin_pile(ruins, x, y, a, rnd, 3, 5, 7, 2, scale=rnd.uniform(0.75, 0.95))
                if y > 0:
                    burning.append((x, y))
        if not night:
            # the hole full of bright daylight (bible 1.4): a warm-white card behind it, seen only by the camera
            bmc = bmesh.new()
            L.box(bmc, (0, 0, 0), (INNER_HOLE[2] * 2 + 10, 0.5, INNER_HOLE[3] + 8))
            mc = bpy.data.materials.new("HoleLight"); mc.use_nodes = True; Nc = mc.node_tree.nodes
            Nc.remove(Nc["Principled BSDF"]); em = Nc.new("ShaderNodeEmission")
            em.inputs["Color"].default_value = (1.0, 0.93, 0.8, 1); em.inputs["Strength"].default_value = 3.0
            mc.node_tree.links.new(em.outputs[0], Nc["Material Output"].inputs["Surface"])
            card = L.obj_from_bm("InnerHoleLight", bmc, [mc], coll)
            card.location = (0, -15, (INNER_HOLE[3] + 8) / 2 - 2)
            for a_ in ("visible_diffuse", "visible_glossy", "visible_transmission", "visible_volume_scatter", "visible_shadow"):
                setattr(card, a_, False)
        # tan dust at the foot of the hole, 60 m wide, spilling north
        billow("InnerDust", coll, (0, 22, 8), (30, 18, 14), DUST, 0.05 * dust_k)
        billow("InnerDust2", coll, (-22, 40, 10), (20, 16, 13), DUST, 0.035 * dust_k)
        billow("InnerDust3", coll, (20, 48, 12), (22, 18, 14), DUST, 0.03 * dust_k)
        settlement_earth(edit, coll)

    # ---- fires
    rnd_f = random.Random(77)
    blazes = []
    if not night:
        n_ruin_fires = {1: 6, 2: 18}[lv]
        rnd_f.shuffle(burning)
        for x, y in burning[:n_ruin_fires]:
            fires.add(x + rnd_f.uniform(-2, 2), y + rnd_f.uniform(-2, 2), 0.5, rnd_f.uniform(3.0, 5.5),
                      light=rnd_f.random() < 0.4, smoke=rnd_f.random() < 0.5)
        if lv >= 2:
            cand = []
            for x, y, s, sd in IMPACTS:
                cand += [(k, i, px, py) for k, i, px, py in edit.near(x, y, s * 5 + 25) if k == 0]
            rnd_f.shuffle(cand)
            seen = set()
            for k, i, px, py in cand:
                if (k, i) in seen or len(seen) >= 22:
                    continue
                seen.add((k, i))
                fires.add(px, py, rnd_f.uniform(9, 14), rnd_f.uniform(3.5, 6.0), light=rnd_f.random() < 0.3, smoke=rnd_f.random() < 0.35)
    else:
        # 18 big blazes (radius 15-30 m): around the impacts, the breach fan and other quarters of the south half
        cents = [(x, y) for x, y, s, sd in IMPACTS]
        cents += [(OG.x + 20, OG.y + 120), (-90, -600), (180, -560), (-230, -380), (40, -420), (200, -380),
                  (-120, -300), (90, -160), (-180, -150)]
        for bx, by in cents[:18]:
            br = rnd_f.uniform(15, 30)
            if not L.in_district(bx, by, br * 0.5):
                continue
            blazes.append((bx, by, br))
            houses = [(k, i, px, py) for k, i, px, py in edit.near(bx, by, br) if k == 0]
            for k, i, px, py in houses:
                if rnd_f.random() < 0.55:
                    edit.kill(k, i)
                    _ruin_pile(ruins, px, py, rnd_f.uniform(0, 6.28), rnd_f, lm["ember"], 2, 2, lm["ember"], scale=0.85)
                elif rnd_f.random() < 0.6:
                    fires.add(px, py, rnd_f.uniform(9, 14), rnd_f.uniform(4, 7), light=False, smoke=False)
            fires.add(bx, by, 0.0, br * 0.9, light=True, smoke=False, radius=br * 0.75, nsc=br / 5.0, lw=0.6)
            fires.add(bx + br * 0.5, by - br * 0.3, 0.0, br * 0.5, light=True, smoke=False, radius=br * 0.4, nsc=br / 7.0, lw=0.6)
        for x, y in burning[:12]:           # a few scattered smaller fires
            fires.add(x, y, 0.5, rnd_f.uniform(3, 5), light=False, smoke=False)

    # ---- smoke columns (dark, billowing), lit from below at night
    flying = {(a[2], a[3]) for a in airborne}
    if night:
        cols = [(bx, by, br) for bx, by, br in blazes][:12]
        cols += [(rnd_f.uniform(-120, 120), rnd_f.uniform(40, 160), 20) for _ in range(2)]
    else:
        cols = [(x, y, 0) for x, y, s, sd in IMPACTS if (x, y) not in flying]
        if lv >= 2:
            cols += [(rnd_f.uniform(-220, 180), rnd_f.uniform(-650, -200), 0) for _ in range(2)]
            cols += [(rnd_f.uniform(-120, 120), rnd_f.uniform(40, 160), 0)]
        cols = cols[:{1: 4, 2: 9}[lv]]
    for n, (x, y, br) in enumerate(cols):
        R = rnd_f.uniform(25, 40) if not night else max(25.0, br * 1.3)
        Hc = rnd_f.uniform(170, 230) if not night else 170.0
        smoke_column(f"FireSmoke{n}", coll, x, y, R, Hc, SMOKE, 0.12 if not night else 0.09,
                     lean=(0.45 + rnd_f.uniform(-0.1, 0.15), 0.12 + rnd_f.uniform(-0.1, 0.1)),
                     emit=(0.35 * gain if night else 0.0), rnd=rnd_f)

    edit.commit()
    ch.build("Rubble845", mats, coll)
    ruins.build("Ruins845", mats, coll)
    bo = blocks.build("ThrownBlocks", [m_block, m_rock_l], coll)
    try:
        L.outline(bo, 0.22)
    except Exception as ex:
        print(f"[states845] outline failed: {ex!r}")
    earth_dark = tuple(c * 0.55 for c in DUST)
    if night:
        m_cr = ground_decal_mat("Crater845N", (0.01, 0.008, 0.007), (0.03, 0.025, 0.02), (0.06, 0.05, 0.04))
    else:
        m_cr = ground_decal_mat("Crater845", (0.035, 0.03, 0.025), (0.10, 0.08, 0.055), earth_dark)
    craters.build("Craters845", m_cr, coll)
    scars.build("Scars845", ground_decal_mat("Scar845", (0.07, 0.062, 0.052), (0.13, 0.115, 0.09), tuple(c * 0.55 for c in DUST), 2.2), coll)
    fires.build(coll, strength=(14.0 if not night else 22.0), light_w=(6000.0 if not night else 3500.0), night=night)
    if night:
        smoke_canopy(coll, blazes, gain)
        night_world(ctx)
    print(f"[states845] state={st} arc_t={arc_t} flames={len(fires.items)} lights={len(fires.pts)} blazes={len(blazes)}")
