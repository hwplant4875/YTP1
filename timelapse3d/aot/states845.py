"""845 destruction states of Shiganshina (environment only, no titans) as a scene.py plug-in.

Enable with AOT_PLUGINS=states845 (usually AOT_PLUGINS=cast845,states845) and pick the state with
AOT_STATE = intact (default, adds nothing) | kicked | armored | night
  kicked  (S1E1-2): outer gate blown in (jagged hole + rubble fan), 9 wall blocks thrown into the town
                    in arcs, crushed houses, craters, dust plumes, a few small fires, Yeager house collapsed.
  armored (S1E2):   kicked + inner gate burst open with debris fanning north into the settlement,
                    more smoke, fires spreading.
  night   (S1E2 end): armored + night (dark blue sky, low moon), the town burning, smoke columns lit from below.
Optional env:
  AOT_ARC_T=0..1    put the thrown blocks part-way along their arcs (0.5 = mid-flight) for the kick shot.
                    Blocks still in the air have not crushed anything yet. Unset / 1 = all landed.
  AOT_FIRE_GAIN     multiplies fire light power (default 1).
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
INNER_HOLE = (0.0, 0.0, 10.5, 25.0)

LABELS = {}
if state() != "intact":
    LABELS = {"BREACH": (OG.x, OG.y, 40), "YEAGER HOUSE": (YEAGER_HOUSE[0], YEAGER_HOUSE[1], 22)}

def _cam_breach():
    return ((46, OG.y + 270, 80), (-2, OG.y + 10, 6), 30)

CAMS = {
    "breach_inside": _cam_breach,                                          # from the town, looking south
    "town_burning": ((-560, 430, 400), (30, -380, 0), 26),                  # high oblique from the NW
    "inner_burst": ((70, 250, 62), (-4, 8, 12), 30),                       # north side, looking south at the gate
    "block_impact": ((-40, -360, 75), (-150, -455, 4), 32),                # close look at one thrown block
    "yeager": ((-38, -165, 34), (-72, -116, 4), 30),                         # the crushed Yeager house
}

# ---------------------------------------------------------------- materials
_MC = {}
def _emit_mat(name, c0, c1, strength, alpha_tip=True):
    """Flame material: colour ramp along the per-vertex attribute fz (0 base, 1 tip), tips fade out."""
    if name in _MC:
        return _MC[name]
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; N = nt.nodes; Ln = nt.links
    N.remove(N["Principled BSDF"])
    at = N.new("ShaderNodeAttribute"); at.attribute_name = "fz"
    rp = N.new("ShaderNodeValToRGB"); e = rp.color_ramp.elements
    e[0].position, e[0].color = 0.0, (*c0, 1)
    e[1].position, e[1].color = 1.0, (*c1, 1)
    Ln.new(at.outputs["Fac"], rp.inputs["Fac"])
    em = N.new("ShaderNodeEmission"); em.inputs["Strength"].default_value = strength
    Ln.new(rp.outputs["Color"], em.inputs["Color"])
    tr = N.new("ShaderNodeBsdfTransparent")
    mx = N.new("ShaderNodeMixShader")
    pw = N.new("ShaderNodeMath"); pw.operation = "POWER"; pw.inputs[1].default_value = 1.6
    Ln.new(at.outputs["Fac"], pw.inputs[0])
    Ln.new(pw.outputs[0], mx.inputs[0]); Ln.new(em.outputs[0], mx.inputs[1]); Ln.new(tr.outputs[0], mx.inputs[2])
    Ln.new(mx.outputs[0], N["Material Output"].inputs["Surface"])
    _MC[name] = m
    return m

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

def _smoke_mat(name, color, density, lean, emit=0.0, emit_col=(1.0, 0.28, 0.05), widen=0.65, base_w=0.35, nscale=(1, 1, 1)):
    """Column smoke in a sheared unit box (x, y in [-1, 1], z in [0, 1]); widens upward, fades at the top,
    optional orange emission near the base (fire glow from below)."""
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; N = nt.nodes; Ln = nt.links
    N.remove(N["Principled BSDF"])
    def math_(op, a, b=None, v=None):
        n = N.new("ShaderNodeMath"); n.operation = op
        for i, x in enumerate((a, b)):
            if x is None:
                continue
            if isinstance(x, (int, float)):
                n.inputs[i].default_value = x
            else:
                Ln.new(x, n.inputs[i])
        return n.outputs[0]
    tc = N.new("ShaderNodeTexCoord")
    sp = N.new("ShaderNodeSeparateXYZ"); Ln.new(tc.outputs["Object"], sp.inputs[0])
    x, y, z = sp.outputs[0], sp.outputs[1], sp.outputs[2]
    qx = math_("SUBTRACT", x, math_("MULTIPLY", z, lean[0]))
    qy = math_("SUBTRACT", y, math_("MULTIPLY", z, lean[1]))
    w = math_("ADD", math_("MULTIPLY", math_("POWER", z, 0.7), widen), base_w)
    r = math_("DIVIDE", math_("SQRT", math_("ADD", math_("MULTIPLY", qx, qx), math_("MULTIPLY", qy, qy))), w)
    radial = math_("MAXIMUM", math_("SUBTRACT", 1.0, r), 0.0)
    vin = math_("MINIMUM", math_("MULTIPLY", z, 25.0), 1.0)
    vout = math_("MINIMUM", math_("MULTIPLY", math_("SUBTRACT", 1.0, z), 4.0), 1.0)
    vert = math_("MULTIPLY", vin, math_("MAXIMUM", vout, 0.0))
    sc = N.new("ShaderNodeVectorMath"); sc.operation = "MULTIPLY"; sc.inputs[1].default_value = nscale
    Ln.new(tc.outputs["Object"], sc.inputs[0])
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 2.2; nz.inputs["Detail"].default_value = 6
    nz.inputs["Roughness"].default_value = 0.6
    Ln.new(sc.outputs[0], nz.inputs["Vector"])
    shape = math_("SUBTRACT", math_("MULTIPLY", radial, 2.2), math_("MULTIPLY", math_("SUBTRACT", 1.0, nz.outputs["Fac"]), 1.6))
    d = math_("MULTIPLY", math_("MAXIMUM", shape, 0.0), vert)
    dens = math_("MULTIPLY", d, density)
    pv = N.new("ShaderNodeVolumePrincipled")
    pv.inputs["Color"].default_value = (*color, 1); pv.inputs["Anisotropy"].default_value = 0.2
    Ln.new(dens, pv.inputs["Density"])
    if emit > 0:
        g = math_("POWER", math_("MAXIMUM", math_("SUBTRACT", 1.0, math_("MULTIPLY", z, 2.0)), 0.0), 2.5)
        es = math_("MULTIPLY", math_("MULTIPLY", g, d), emit)
        pv.inputs["Emission Color"].default_value = (*emit_col, 1)
        Ln.new(es, pv.inputs["Emission Strength"])
    Ln.new(pv.outputs[0], N["Material Output"].inputs["Volume"])
    return m

def smoke(name, coll, base, radius, height, color, density, lean=(0.0, 0.0), emit=0.0, widen=0.65, base_w=0.35):
    """Volume smoke column standing on base (x, y, z); lean = top offset in units of radius."""
    if os.environ.get("AOT_NOSMOKE") == "1":
        return None
    lx, ly = lean
    top_r = base_w + widen
    bm = bmesh.new()
    vs = []
    for z in (0.0, 1.0):
        rr = max(1.0, top_r * 1.05) if z else max(1.0, base_w * 1.6)
        for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            vs.append(bm.verts.new((sx * rr + lx * z, sy * rr + ly * z, z)))
    for f in ((0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)):
        bm.faces.new([vs[i] for i in f])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    m = _smoke_mat(name, color, density, lean, emit=emit, widen=widen, base_w=base_w,
                   nscale=(radius / 40.0, radius / 40.0, height / 40.0))
    ob = L.obj_from_bm(name, bm, [m], coll)
    ob.location = base; ob.scale = (radius, radius, height)
    ob.visible_shadow = True
    return ob

def _rock_template(rnd, flat=1.0, n=11):
    """Angular chunk: convex hull of random points on a squashed sphere. Returns (verts, faces) in unit size."""
    bm = bmesh.new()
    for _ in range(n):
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

class Chunks:
    """Accumulate many transformed rock templates into one mesh."""
    def __init__(self, seed, flat=1.0, ntmp=14):
        rnd = random.Random(seed)
        self.tmps = [_rock_template(rnd, flat) for _ in range(ntmp)]
        self.bm = bmesh.new()
        self.rnd = rnd
    def add(self, loc, size, mi=0, rot=None, tmp=None, squash=(1, 1, 1)):
        rnd = self.rnd
        vs, fs = self.tmps[tmp if tmp is not None else rnd.randrange(len(self.tmps))]
        rot = rot if rot is not None else (rnd.uniform(-0.5, 0.5), rnd.uniform(-0.5, 0.5), rnd.uniform(0, 6.28))
        M = Matrix.Translation(loc) @ (Matrix.Rotation(rot[2], 4, "Z") @ Matrix.Rotation(rot[1], 4, "Y") @ Matrix.Rotation(rot[0], 4, "X"))
        S = Matrix.Diagonal((size * squash[0], size * squash[1], size * squash[2], 1))
        nv = [self.bm.verts.new((M @ S) @ v) for v in vs]
        for f in fs:
            try:
                ff = self.bm.faces.new([nv[i] for i in f]); ff.material_index = mi
            except ValueError:
                pass
    def box(self, center, size, rot=(0, 0, 0), mi=0):
        r = bmesh.ops.create_cube(self.bm, size=1)
        M = Matrix.Translation(center) @ Matrix.Rotation(rot[2], 4, "Z") @ Matrix.Rotation(rot[1], 4, "Y") @ Matrix.Rotation(rot[0], 4, "X")
        bmesh.ops.transform(self.bm, matrix=M @ Matrix.Diagonal((*size, 1)), verts=r["verts"])
        for f in {f for v in r["verts"] for f in v.link_faces}:
            f.material_index = mi
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
            var = [0] * n
            if "variant" in me.attributes:
                me.attributes["variant"].data.foreach_get("value", var)
            rot = [0.0] * (3 * n); me.attributes["rot"].data.foreach_get("vector", rot)
            self.data.append({"co": co, "born": born, "dead": dead, "var": var, "rot": rot, "n": n})
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
        hh = rnd.uniform(3, 8) * s
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

def _flame(bm, layer, c, size, rnd):
    """Cluster of flame tongues (cones) at c with height ~size."""
    for _ in range(rnd.randint(4, 7)):
        ox, oy = rnd.uniform(-0.45, 0.45) * size, rnd.uniform(-0.45, 0.45) * size
        h = size * rnd.uniform(0.6, 1.4); rr = size * rnd.uniform(0.2, 0.36)
        tilt = Vector((rnd.uniform(-0.25, 0.25) + 0.15, rnd.uniform(-0.25, 0.25), 1)).normalized()
        p0 = Vector((c[0] + ox, c[1] + oy, c[2]))
        p1 = p0 + tilt * h
        r = bmesh.ops.create_cone(bm, cap_ends=True, segments=7, radius1=rr, radius2=0.0, depth=h)
        q = tilt.to_track_quat("Z", "Y").to_matrix()
        for v in r["verts"]:
            fz = (v.co.z + h / 2) / h
            v.co = q @ v.co + (p0 + p1) / 2
            v[layer] = fz

class Fires:
    def __init__(self, gain):
        self.bm = bmesh.new()
        self.layer = self.bm.verts.layers.float.new("fz")
        self.rnd = random.Random(55)
        self.gain = gain
        self.pts = []
    def add(self, x, y, z, size, light=True):
        _flame(self.bm, self.layer, (x, y, z), size, self.rnd)
        if light:
            self.pts.append((x, y, z + size * 0.6, size))
    def build(self, coll, strength, light_w):
        m = _emit_mat("Fire", (1.0, 0.52, 0.12), (0.75, 0.10, 0.01), strength)
        ob = L.obj_from_bm("Fires", self.bm, [m], coll)
        ob.visible_shadow = False
        for k, (x, y, z, s) in enumerate(self.pts):
            ld = bpy.data.lights.new(f"FireL{k}", "POINT")
            ld.energy = light_w * self.gain * (s / 6.0) ** 2
            ld.color = (1.0, 0.42, 0.12); ld.shadow_soft_size = s * 0.5
            lo = bpy.data.objects.new(f"FireL{k}", ld); lo.location = (x, y, z)
            lo.visible_volume_scatter = False      # smoke glow comes from its own emission gradient (cheaper, controllable)
            coll.objects.link(lo)
        return ob

def _hole_cutter(name, center, hw, ht, depth, seed, coll):
    """Prism with a jagged arch outline in the x-z plane, extruded along y (both faces of the gatehouse)."""
    rnd = random.Random(seed)
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
    bm = bmesh.new()
    f0 = [bm.verts.new((x, -depth, z)) for x, z in ol]
    f1 = [bm.verts.new((x, depth, z)) for x, z in ol]
    bm.faces.new(f0); bm.faces.new(list(reversed(f1)))
    for i in range(len(ol)):
        j = (i + 1) % len(ol)
        bm.faces.new((f0[i], f1[i], f1[j], f0[j]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = L.obj_from_bm(name, bm, [], coll)
    ob.location = (center[0], center[1], 0)
    ob.hide_render = True; ob.display_type = "WIRE"
    return ob, ol

def breach_gate(gname, hole, M, coll, inward, seed, ch, lm):
    """Blow a jagged hole through gatehouse gname, remove its door, return the hole outline."""
    g = bpy.data.objects.get(gname)
    d = bpy.data.objects.get(gname + "_Door")
    if d:
        d.hide_render = True; d.hide_viewport = True
    if not g:
        return
    cut, ol = _hole_cutter(gname + "_Cutter", (hole[0], hole[1]), hole[2], hole[3], 14.0, seed, coll)
    mod = g.modifiers.new("Breach", "BOOLEAN"); mod.operation = "DIFFERENCE"; mod.object = cut
    try:
        mod.solver = "EXACT"; mod.use_self = True
    except (TypeError, AttributeError):
        pass
    wall_cracks(ch, hole, ol, seed + 5, lm, half_t=g.dimensions.y / 2)
    # ragged broken stones lining the hole edges (both faces) so the cut reads as smashed masonry
    rnd = random.Random(seed + 10)
    for x, z in ol:
        if z < 0.5:
            continue
        for fy in (-8.5, -4, 0, 4, 8.5):
            if rnd.random() < 0.55:
                ch.add(Vector((hole[0] + x * 1.02, hole[1] + fy, z)), rnd.uniform(1.4, 3.2), mi=lm["stone"])
    # stubs of the door: splintered planks hanging at the sides
    for sx in (-1, 1):
        for k in range(4):
            ch.box(Vector((hole[0] + sx * (hole[2] - 1.5 - k * 0.9), hole[1] - inward * 3.0, rnd.uniform(1, 6))),
                   (0.6, 0.5, rnd.uniform(4, 9)), rot=(rnd.uniform(-0.3, 0.3), sx * rnd.uniform(0.1, 0.5), 0), mi=lm["wood"])

def wall_cracks(ch, hole, ol, seed, lm, n=14, gate_half=15.0, half_t=8.0):
    """Zig-zag cracks running out from the hole across both faces of the gatehouse and the wall next to it."""
    rnd = random.Random(seed)
    def face_y(x, z):
        if abs(x) < gate_half:
            return half_t - half_t * 0.2 * (z + 4) / 56 + 0.08
        return 5.0 - 1.2 * (z + 4) / 54 + 0.08
    pts = [p for p in ol if p[1] > 2]
    for side in (-1, 1):
        for _ in range(n):
            x, z = rnd.choice(pts)
            x *= 1.02
            ang = math.atan2(z - hole[3] * 0.3, x) + rnd.uniform(-0.5, 0.5)
            w = rnd.uniform(0.25, 0.5)
            for k in range(rnd.randint(4, 9)):
                L_ = rnd.uniform(2.5, 6.0)
                ang += rnd.uniform(-0.6, 0.6)
                nx, nz = x + math.cos(ang) * L_, z + math.sin(ang) * L_
                if nz > 49 or nz < 0.5:
                    break
                mx, mz = (x + nx) / 2, (z + nz) / 2
                yy = side * face_y(mx, mz)
                ch.box(Vector((hole[0] + mx, hole[1] + yy, mz)), (L_ + 0.2, 0.25, w),
                       rot=(0, -math.atan2(nz - z, nx - x), 0), mi=lm["crack"])
                x, z = nx, nz
                w *= 0.85

def rubble_fan(ch, origin, inward, spread, length, count, smax, seed, lm, edit, crush_frac=0.55, door=True):
    """Debris thrown through a breach: chunks densest near the hole, thinning out over `length` metres
    inside a cone of half-angle `spread` around direction `inward` (unit 2D)."""
    rnd = random.Random(seed)
    base = math.atan2(inward[1], inward[0])
    pts = []
    for _ in range(count):
        t = rnd.random() ** 1.8
        dist = 6 + t * length
        a = base + rnd.gauss(0, spread * (0.45 + 0.4 * t))
        x, y = origin[0] + math.cos(a) * dist, origin[1] + math.sin(a) * dist
        if inward[1] > 0 and origin[1] < -1 and not L.in_district(x, y, 7):
            continue
        s = smax * (1 - t) ** 1.4 * rnd.uniform(0.3, 1.0) + 0.6
        mi = rnd.choice((lm["stone"], lm["stone"], lm["dark"], lm["dark"], lm["stone_l"]))
        if door and rnd.random() < 0.08:
            ch.box(Vector((x, y, 0.4)), (rnd.uniform(3, 7), rnd.uniform(0.8, 1.6), 0.5),
                   rot=(rnd.uniform(-0.2, 0.2), rnd.uniform(-0.2, 0.2), rnd.uniform(0, 6.28)), mi=lm["wood"])
            continue
        ch.add(Vector((x, y, s * 0.18)), s, mi=mi)
        pts.append((x, y, s))
    # big pile in and just inside the hole
    for _ in range(160):
        a = base + rnd.gauss(0, 0.45); dist = rnd.uniform(-7, 40)
        x, y = origin[0] + math.cos(a) * dist + rnd.uniform(-9, 9) * abs(inward[1]), origin[1] + math.sin(a) * dist
        f = max(0.0, 1.0 - max(0, dist) / 45)
        s = rnd.uniform(3.0, 8.0) * (0.5 + f)
        ch.add(Vector((x, y, rnd.uniform(0, 7.0) * f)), s, mi=rnd.choice((lm["stone"], lm["stone_l"], lm["dark"])))
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

def rubble_decal(name, origin, inward, spread, length, m, coll, seed, z=0.22):
    """Dark ground scar under a fan (ragged polygon)."""
    rnd = random.Random(seed)
    base = math.atan2(inward[1], inward[0])
    bm = bmesh.new()
    vs = [bm.verts.new((origin[0] - inward[0] * 4, origin[1] - inward[1] * 4, z))]
    n = 26
    for k in range(n + 1):
        a = base - spread + 2 * spread * k / n
        r = length * (0.55 + 0.45 * math.cos((k / n - 0.5) * math.pi)) * rnd.uniform(0.75, 1.1)
        vs.append(bm.verts.new((origin[0] + math.cos(a) * r, origin[1] + math.sin(a) * r, z)))
    bm.faces.new(vs)
    return L.obj_from_bm(name, bm, [m], coll)

def crater_decal(bm, x, y, r, rnd, z=0.24):
    n = 18
    vs = []
    for k in range(n):
        a = k / n * 2 * math.pi
        rr = r * rnd.uniform(0.7, 1.25)
        vs.append(bm.verts.new((x + math.cos(a) * rr, y + math.sin(a) * rr, z)))
    bm.faces.new(vs)

def block_arc(x, y, t):
    """Point on the arc from the gate top to the impact (x, y) at parameter t in [0, 1]."""
    p0 = Vector((OG.x, OG.y + 4, 42.0)); p1 = Vector((x, y, 0.0))
    dist = (p1 - p0).xy.length
    hmax = 60 + dist * 0.28
    p = p0.lerp(p1, t)
    p.z = p0.z * (1 - t) + 4 * hmax * t * (1 - t) + p1.z * t
    return p

# ---------------------------------------------------------------- yeager house
def yeager_house(ch, x, y, ang, lm, rnd):
    """Modest 2-storey half-timbered house, crushed by a wall chunk: roof caved in, X-braced front fallen."""
    ca, sa = math.cos(ang), math.sin(ang)
    def P(u, v, z):
        return Vector((x + ca * u - sa * v, y + sa * u + ca * v, z))
    w, d = 9.0, 12.0
    # stone ground floor walls, broken
    for side in (-1, 1):
        ch.box(P(side * w / 2, 0, 2.2), (0.8, d, 4.4), rot=(0, 0, ang), mi=lm["stone_l"])
    ch.box(P(0, d / 2, 1.8), (w, 0.8, 3.6), rot=(0.05, 0, ang), mi=lm["stone_l"])
    ch.box(P(-2.5, -d / 2, 1.6), (4.0, 0.8, 3.2), rot=(0, 0, ang), mi=lm["stone_l"])
    # upper floor: one gable end still standing at the back, tilted
    ch.box(P(0, d / 2 - 0.2, 6.6), (w, 0.5, 4.2), rot=(-0.12, 0, ang), mi=lm["plaster"])
    for k in (-1, 1):            # X-brace timbers on the standing gable
        ch.box(P(0, d / 2 - 0.55, 6.6), (0.35, 0.3, 9.0), rot=(0, k * 0.85, ang), mi=lm["wood"])
    ch.box(P(0, d / 2 - 0.55, 8.6), (w, 0.35, 0.4), rot=(0, 0, ang), mi=lm["wood"])
    # caved roof slabs folded into the house
    ch.box(P(-2.4, 1.0, 4.2), (5.6, d * 0.9, 0.4), rot=(0.1, 0.75, ang), mi=lm["roof"])
    ch.box(P(2.6, -0.5, 3.6), (5.6, d * 0.8, 0.4), rot=(-0.15, -0.55, ang + 0.1), mi=lm["roof"])
    for _ in range(9):
        ch.box(P(rnd.uniform(-5, 5), rnd.uniform(-6, 6), rnd.uniform(1, 5)), (0.3, rnd.uniform(4, 8), 0.3),
               rot=(rnd.uniform(-1, 1), rnd.uniform(-0.6, 0.6), rnd.uniform(0, 6.3)), mi=lm["wood"])
    for _ in range(25):
        ch.add(P(rnd.uniform(-7, 7), rnd.uniform(-8, 8), 0.3), rnd.uniform(0.6, 2.0),
               mi=rnd.choice((lm["roof"], lm["stone_l"], lm["plaster"], lm["dark"])))
    # front steps with a wooden post-and-rail handrail (S3 flashback), facing the street
    for k in range(5):
        ch.box(P(2.8, -d / 2 - 1.0 - k * 0.6, 0.15 + k * 0.0), (2.4, 0.6, 0.3 + (4 - k) * 0.3), rot=(0, 0, ang), mi=lm["stone_l"])
    for k in range(3):
        ch.box(P(4.2, -d / 2 - 0.9 - k * 1.2, 0.9), (0.18, 0.18, 1.8), rot=(0, 0, ang), mi=lm["wood"])
    ch.box(P(4.2, -d / 2 - 2.1, 1.75), (0.15, 3.0, 0.15), rot=(0.3, 0, ang), mi=lm["wood"])

# ---------------------------------------------------------------- night
def night_world(ctx):
    w = ctx.get("world") or bpy.context.scene.world
    nt = w.node_tree
    bg = nt.nodes.get("Background")
    if bg:
        for lk in list(bg.inputs[0].links):
            nt.links.remove(lk)
        bg.inputs[0].default_value = (0.018, 0.026, 0.06, 1)
        bg.inputs[1].default_value = 1.0
    for n in nt.nodes:
        if n.type == "VALTORGB":
            e = n.color_ramp.elements
            e[0].position, e[0].color = 0.0, (0.10, 0.05, 0.035, 1)        # horizon reddened by the fires
            e[1].position, e[1].color = 0.30, (0.006, 0.010, 0.030, 1)
            el = n.color_ramp.elements.new(0.12); el.color = (0.03, 0.035, 0.07, 1)
        if n.type == "BACKGROUND" and n != bg:
            n.inputs[1].default_value = 1.0
    sun = ctx.get("sun") or bpy.data.objects.get("Sun")
    if sun:
        sun.data.energy = float(os.environ.get("MOON_E", "0.12"))
        sun.data.color = (0.55, 0.66, 1.0)
        el, az = math.radians(28), math.radians(-120)
        d = Vector((-math.cos(el) * math.cos(az), -math.cos(el) * math.sin(az), -math.sin(el)))
        sun.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
        # moon disc in the sky behind the town (opposite the light direction)
        mp = -d * 14000
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
    os.environ.setdefault("EXPO", "-0.8")

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
    arc_t = os.environ.get("AOT_ARC_T", "")
    arc_t = min(1.0, max(0.0, float(arc_t))) if arc_t else 1.0

    m_dark = L.mat("RubbleDark", (0.13, 0.115, 0.10), 0.95, var=0.3, var_scale=0.3, color2=(0.22, 0.2, 0.17))
    m_scar = L.mat("RubbleScar", (0.16, 0.14, 0.115), 0.95, var=0.35, var_scale=0.06, color2=(0.30, 0.27, 0.22))
    m_burnt = L.mat("Burnt", (0.035, 0.03, 0.028), 0.95, var=0.3, var_scale=0.1, color2=(0.09, 0.075, 0.06))
    m_crack = L.mat("Crack", (0.025, 0.022, 0.02), 0.9)
    mats = [M["stone"], M["stone_light"], m_dark, M["roof_red"], M["gate"], M["plaster"], M["roof_brown"], m_crack]
    lm = {"stone": 0, "stone_l": 1, "dark": 2, "roof": 3, "wood": 4, "plaster": 5, "roof2": 6, "crack": 7}
    if night:
        mats.append(_ember_mat(9.0)); lm["ember"] = 8
    ch = Chunks(seed=11)
    ruins = Chunks(seed=12, ntmp=10)
    dec = bmesh.new()
    fires = Fires(gain)
    burning = []           # ruin / house positions that may burn

    # ---- outer gate breach (kick from the south, debris into the town)
    breach_gate("OuterGate", OUTER_HOLE, M, coll, inward=1, seed=3, ch=ch, lm=lm)
    hit = rubble_fan(ch, (OG.x, OG.y + 9), (0, 1), 0.55, 230, 1900, 11.0, 31, lm, edit)
    rubble_decal("BreachScar", (OG.x, OG.y + 8), (0, 1), 0.6, 215, m_scar, coll, 4)
    for k, i in hit:
        x, y, a = edit.pos(k, i)
        if k == 0:
            _ruin_pile(ruins, x, y, a, rnd, 3, 5, 4, 2, scale=rnd.uniform(0.8, 1.0))
            burning.append((x, y))

    # ---- thrown blocks
    blocks = Chunks(seed=21, flat=1.7, ntmp=9)
    airborne = []
    for n, (x, y, s, sd) in enumerate(IMPACTS):
        tl = min(1.0, arc_t * (1.0 + n * 0.04))          # farther blocks land a moment later
        if tl < 1.0:
            p = block_arc(x, y, tl)
            blocks.add(p, s, mi=0, tmp=n, squash=(1.0, 0.8, 0.75))
            airborne.append((p, s, x, y, tl))
            continue
        rr = random.Random(sd)
        # incoming direction (from the gate): skid scar extends past the impact
        dv = Vector((x - OG.x, y - OG.y)).normalized()
        yb = math.hypot(x - YEAGER_HOUSE[0], y - YEAGER_HOUSE[1]) < 5
        blocks.add(Vector((x + dv.x * (0 if yb else 4), y + dv.y * (0 if yb else 4), s * (0.42 if yb else 0.22))), s, mi=0, tmp=n,
                   rot=(rr.uniform(-0.35, 0.35), rr.uniform(-0.35, 0.35), math.atan2(dv.y, dv.x)), squash=(1.15, 0.85, 0.85))
        for _ in range(40):      # mound of crushed masonry heaped against the block
            a = rr.uniform(0, 6.28); dd = rr.uniform(s * 0.3, s * 0.9)
            ch.add(Vector((x + dv.x * 4 + math.cos(a) * dd, y + dv.y * 4 + math.sin(a) * dd, rr.uniform(0, s * 0.15))),
                   rr.uniform(1.5, 4.0), mi=rr.choice((lm["dark"], lm["stone"], lm["roof"])))
        # a broken-off second piece and a ring of fragments
        blocks.add(Vector((x + dv.x * (s + 6) + rr.uniform(-4, 4), y + dv.y * (s + 6) + rr.uniform(-4, 4), s * 0.12)), s * 0.45, mi=1)
        for _ in range(240):
            a = rr.uniform(0, 6.28); dd = s * (0.5 + 2.3 * rr.random() ** 1.5)
            ch.add(Vector((x + math.cos(a) * dd + dv.x * dd * 0.6, y + math.sin(a) * dd + dv.y * dd * 0.6, 0.2)),
                   rr.uniform(0.8, 2.4) * (2.2 - dd / (s * 2.8)), mi=rr.choice((lm["stone"], lm["dark"], lm["dark"], lm["roof"])))
        crater_decal(dec, x + dv.x * 6, y + dv.y * 6, s * 2.8, rr)
        # crushed houses: around the impact plus a skid zone back along the arc
        killed = []
        for cx, cy, r in ((x, y, s * 2.1 + 8), (x - dv.x * s * 2.0, y - dv.y * s * 2.0, s * 1.3 + 5),
                          (x + dv.x * s * 2.2, y + dv.y * s * 2.2, s * 1.5 + 5)):
            for k, i, px, py in edit.near(cx, cy, r):
                if edit.kill(k, i) and k == 0:
                    killed.append((px, py))
        for k, i, px, py in edit.near(x, y, s * 1.8 + 6, only_alive=False):
            if k == 1:
                edit.kill(k, i)
        for px, py in killed:
            if math.hypot(px - YEAGER_HOUSE[0], py - YEAGER_HOUSE[1]) < 7:
                continue
            _ruin_pile(ruins, px, py, rr.uniform(0, 6.28), rr, 3 if rr.random() < 0.6 else 6, 5, 4, 2, scale=rr.uniform(0.8, 1.05))
            burning.append((px, py))
        if lv >= 1 and n in (0, 2, 5) or lv >= 2:
            fires.add(x - dv.x * s, y - dv.y * s, 0.5, 4.5 + rr.uniform(0, 2.5))
        # dust over the impact
        if lv <= 1 or n % 2 == 0:
            smoke(f"ImpactDust{n}", coll, (x, y, -1), s * 2.2, s * 3.5, (0.62, 0.55, 0.47), 0.018,
                  lean=(0.8, 0.1), widen=0.9, base_w=0.6)
    for p, s, x, y, tl in airborne:
        # streaks of small debris trailing each flying block
        for k in range(14):
            q = block_arc(x, y, max(0.0, tl - k * 0.006 - rnd.uniform(0, 0.006)))
            ch.add(q + Vector((rnd.gauss(0, s * 0.3), rnd.gauss(0, s * 0.3), rnd.gauss(0, s * 0.3))), rnd.uniform(0.6, 2.2) * (1 - k / 16), mi=lm["stone_l"])

    # ---- the Yeager house under a block
    yk = [(k, i, px, py) for k, i, px, py in edit.near(YEAGER_HOUSE[0], YEAGER_HOUSE[1], 14, only_alive=False) if k == 0]
    ya = edit.pos(yk[0][0], yk[0][1])[2] if yk else 0.0
    for k, i, px, py in edit.near(YEAGER_HOUSE[0], YEAGER_HOUSE[1], 10):
        edit.kill(k, i)
    if arc_t >= 1.0:
        yeager_house(ch, YEAGER_HOUSE[0], YEAGER_HOUSE[1], ya, lm, rnd)

    # ---- inner gate burst (Armored Titan, S1E2), debris fanning north into the Wall Maria settlement
    if lv >= 2:
        breach_gate("InnerGate", INNER_HOLE, M, coll, inward=-1, seed=7, ch=ch, lm=lm)
        hit2 = rubble_fan(ch, (0, 9), (0, 1), 0.5, 150, 1100, 5.5, 41, lm, edit, crush_frac=0.6)
        # a few chunks blown back south into the gate square
        hit2 += rubble_fan(ch, (0, -10), (0, -1), 0.6, 45, 160, 3.0, 42, lm, edit, door=False)
        rubble_decal("InnerScar", (0, 8), (0, 1), 0.55, 135, m_scar, coll, 6)
        for k, i in hit2:
            x, y, a = edit.pos(k, i)
            if k == 0:
                _ruin_pile(ruins, x, y, a, rnd, 3, 5, 4, 2, scale=rnd.uniform(0.75, 0.95))
                if y > 0:
                    burning.append((x, y))
        smoke("InnerDust", coll, (0, 45, -1), 55, 55, (0.62, 0.56, 0.49), 0.012, lean=(0.6, 0.4), widen=0.8, base_w=0.6)

    # ---- outer breach dust (tan, the colour of the 845 dust/steam column)
    smoke("BreachDust", coll, (OG.x + 10, OG.y + 25, -1), 55 if lv == 1 else 45, 95 if lv == 1 else 70,
          (0.72, 0.60, 0.50), 0.02 if lv == 1 else 0.012, lean=(0.9, -0.2), widen=0.9, base_w=0.6)

    # ---- fires: a few at kicked, spreading at armored, the whole south half burning at night
    rnd_f = random.Random(77)
    n_ruin_fires = {1: 6, 2: 22, 3: 70}[lv]
    rnd_f.shuffle(burning)
    for x, y in burning[:n_ruin_fires]:
        fires.add(x + rnd_f.uniform(-2, 2), y + rnd_f.uniform(-2, 2), 0.6, rnd_f.uniform(2.5, 5.0), light=rnd_f.random() < (0.35 if lv < 3 else 0.6))
    if lv >= 2:
        # spread to standing houses next to the ruins: flames on the roofs
        n_roof = {2: 30, 3: 160}[lv]
        cand = []
        for x, y, s, sd in IMPACTS:
            cand += [(k, i, px, py) for k, i, px, py in edit.near(x, y, s * 5 + 25) if k == 0]
        if lv >= 3:
            for _ in range(60):     # other burning quarters in the south half
                cx, cy = rnd_f.uniform(-240, 200), rnd_f.uniform(-700, -150)
                if L.in_district(cx, cy, 20):
                    cand += [(k, i, px, py) for k, i, px, py in edit.near(cx, cy, 22) if k == 0]
        rnd_f.shuffle(cand)
        seen = set()
        for k, i, px, py in cand:
            if (k, i) in seen or len(seen) >= n_roof:
                continue
            seen.add((k, i))
            fires.add(px, py, rnd_f.uniform(9, 15), rnd_f.uniform(3.5, 7.0), light=rnd_f.random() < (0.3 if lv < 3 else 0.45))
            if lv >= 3 and rnd_f.random() < 0.4:      # burnt out: house gone, glowing ruin
                edit.kill(k, i)
                _ruin_pile(ruins, px, py, rnd_f.uniform(0, 6.28), rnd_f, lm.get("ember", 2), 2, 2, lm.get("ember", 2), scale=0.85)

    # ---- smoke columns from the fires (dark), lit from below at night
    flying = {(a[2], a[3]) for a in airborne}
    centers = [(x, y) for x, y, s, sd in IMPACTS if (x, y) not in flying]
    if lv >= 2:
        centers += [(rnd_f.uniform(-220, 180), rnd_f.uniform(-650, -200)) for _ in range(2 if lv == 2 else 6)]
        centers += [(rnd_f.uniform(-120, 120), rnd_f.uniform(40, 160)) for _ in range(1 if lv == 2 else 2)]
    ncol = {1: 4, 2: 9, 3: len(centers)}[lv]
    for n, (x, y) in enumerate(centers[:ncol]):
        r = rnd_f.uniform(30, 45) * (1.25 if lv == 3 else 1.0)
        h = rnd_f.uniform(140, 220) * (1.25 if lv == 3 else 1.0)
        col = (0.10, 0.09, 0.085) if not night else (0.075, 0.065, 0.06)
        smoke(f"FireSmoke{n}", coll, (x, y, -1), r, h, col, 0.04 if not night else 0.03,
              lean=(1.2 + rnd_f.uniform(-0.3, 0.4), 0.35 + rnd_f.uniform(-0.3, 0.3)),
              emit=(0.06 * gain if night else 0.0), widen=1.3, base_w=0.3)

    edit.commit()
    obs = [ch.build("Rubble845", mats, coll), ruins.build("Ruins845", mats, coll)]
    bo = blocks.build("ThrownBlocks", [M["stone"], M["stone_light"]], coll)
    try:
        L.outline(bo, 0.22)
    except Exception as ex:
        print(f"[states845] outline failed: {ex!r}")
    m_crater = L.mat("Crater", (0.075, 0.065, 0.055), 0.95, var=0.35, var_scale=0.12, color2=(0.15, 0.13, 0.11))
    L.obj_from_bm("Craters845", dec, [m_burnt if night else m_crater], coll)
    fires.build(coll, strength=(5.0 if not night else 9.0) * gain, light_w=(6000.0 if not night else 2600.0))
    if night:
        night_world(ctx)
    print(f"[states845] state={st} arc_t={arc_t} fires={len(fires.pts)} lights")
