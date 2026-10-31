"""104th TRAINING CORPS CAMP (SCENE_BIBLE_v2 g3 layout) as a light set piece for the Trost-set segments.

Built by seg_g4 (the camp is in frame for g4's first ~2 s: the g3 -> g4 seam looks at it at graduation night).  The g3 build
can import it too, so both sides of the seam show the same camp:
    import camp104 as CP
    st = CP.build(L, M2S, ground_M, coll)        # once (L = aotlib, M2S / ground_M = render_seg site helpers)
    CP.set_night(st, f)                          # f 1 = graduation night (lit windows, braziers, lanterns), 0 = day
Frame M, centre C = (-1450, 1520), u east, v north (bible g3): sunken quarry bowl (floor ellipse 230 x 170 m, rim 14 m, 18-22 m
SW, fluted cliffs, inner rock step), back terrace huts (v +70), lattice watchtower 20 m (u -45, v +70) with a stair box on its
east face, east-terrace huts (u +70..+110), mess hall 26 x 8 m (u -15, v -45) with an 8-window band, veranda, porch lantern,
chimney and the graduation stair (14 steps x 30 m) + 2 tripod braziers on its front, (pole field removed 10/27, owner),
4 A-frame rigs (v +38; u -10/+12/+34/+56), huts (u -95, v -50) and (u -110, v -5), barbed post fence W -> mid-N, pointed
palisade mid-N -> E continuing 320 m east.
g3 agent 10/27 (cloud QA "reads as a stadium"): the bowl is now SUNK into the plain: build() cuts world.py's WD_Ground cells over
the camp and adds CP_Ground (st["ground"]; surface function st["gz"](u, v)), rim flush with the plain, striated fluted cliffs
(lit #a3958c / shade #4a4550), inner rock step, pale cracked-earth floor, north + east terraces; barbed wire on the fence, the
lake (u +150, v +420), conifer stands; continuous lit window bands + warm glow balls; night colours warm under the g4 night
grade.  The cliff-cut road is still left out.
"""
import math, os, random
import numpy as np
import bpy, bmesh
from mathutils import Vector

C = (-1450.0, 1520.0)
A_U, B_V = 115.0, 85.0                       # floor ellipse semi-axes
RIM_H = 14.0

def _hex(h):
    h = h.lstrip("#"); c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c)

def _emit(name, rgb, strength):
    """Pure Emission material (toon.py leaves non-Principled shaders alone, so it keeps glowing)."""
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree; N = nt.nodes
    for n in list(N):
        if n.type != "OUTPUT_MATERIAL":
            N.remove(n)
    em = N.new("ShaderNodeEmission"); em.inputs["Color"].default_value = (*rgb, 1.0); em.inputs["Strength"].default_value = strength
    out = next(n for n in N if n.type == "OUTPUT_MATERIAL")
    nt.links.new(em.outputs[0], out.inputs["Surface"])
    m["toon"] = 1
    return m, em

def build(L, M2S, ground_M, coll, seed=104):
    rnd = random.Random(seed)
    g0 = ground_M(*C)
    def gz(u, v):
        return ground_M(C[0] + u, C[1] + v)
    def P(u, v, z):                          # camp (u, v, absolute z) -> set coords
        q = M2S((C[0] + u, C[1] + v, z)); return (q[0], q[1], q[2])
    floor_z = g0 + 0.15
    M = dict(
             rock=L.mat("CP_RockStep", _hex("#9a8c80"), 0.95),
             timber=L.mat("CP_Timber", _hex("#7a5a3e"), 0.9), dark=L.mat("CP_DarkTimber", _hex("#4a3426"), 0.9),
             roof=L.mat("CP_Roof", _hex("#5b4a40"), 0.85), slate=L.mat("CP_Slate", _hex("#4f5058"), 0.85),
             stone=L.mat("CP_Stone", _hex("#9b9486"), 0.9), steel=L.mat("CP_Steel", _hex("#5c6570"), 0.6),
             pole=L.mat("CP_Pole", _hex("#6b5038"), 0.9), wall=L.mat("CP_HutWall", _hex("#b8a888"), 0.9))
    win_m, win_em = _emit("CP_Window", (1.0, 0.30, 0.06), 0.0)
    fire_m, fire_em = _emit("CP_Fire", (1.0, 0.24, 0.03), 0.0)
    st = dict(win=win_em, fire=fire_em, lights=[], objs=[])
    # ---------------------------------------------------------------- the SUNKEN quarry bowl dug into the plain (g3 agent 10/27,
    # cloud QA "reads as a stadium"): world.py's WD_Ground faces over the camp are cut out and replaced by CP_Ground, one 2.5 m
    # grid that is the plain (flush, world material, matching WD_Ground's 200 m grid edges exactly) outside the rim and drops
    # by fluted near-vertical striated cliffs (14 m N/E, 18-22 m SW) to an inner rock step and a pale cracked-earth floor with
    # the back (north) and east terraces.  gz(u, v) below is that surface; every camp object stands on it.
    import sys as _sys
    WD = _sys.modules.get("world")
    root = bpy.data.objects.get("WorldRoot"); wg = bpy.data.objects.get("WD_Ground")
    MW_Y = 4130.0                                                     # world (W) = M + (0, 4130)
    cell = float(os.environ.get("WORLD_CELL", "200"))
    if WD is not None:
        gx0, gy0 = -WD.R_MARIA - 16000.0, WD.SEA_Y - 600.0
    else:
        gx0, gy0 = -40000.0, -7320.0
    def plain_w(xw, yw):                                              # WD_Ground's surface (bilinear in its 200 m cells)
        if WD is None:
            return ground_M(xw, yw - MW_Y)
        fx, fy = (xw - gx0) / cell, (yw - gy0) / cell
        i, j = math.floor(fx), math.floor(fy); a, b = fx - i, fy - j
        x0, y0 = gx0 + i * cell, gy0 + j * cell
        h = [WD.world_height(x0 + dx * cell, y0 + dy * cell) - 0.4 for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1))]
        return h[0] * (1 - a) * (1 - b) + h[1] * a * (1 - b) + h[2] * (1 - a) * b + h[3] * a * b
    _PC = {}
    def plain(u, v):
        k = (round(u, 2), round(v, 2))
        if k not in _PC:
            _PC[k] = plain_w(C[0] + u, C[1] + v + MW_Y)
        return _PC[k]
    zc = plain(0.0, 0.0)
    def rnorm(u, v):
        a = math.atan2(v / B_V, u / A_U)
        r = math.hypot(u / A_U, v / B_V)
        fl = 0.010 * math.sin(63 * a) + 0.006 * math.sin(151 * a + 0.7) + 0.018 * math.sin(7 * a + 1.3)
        return r * (1.0 - fl), a
    def depth(a, r):
        sw = max(0.0, math.cos(a - math.radians(225.0)))
        d_rim = RIM_H + 6.0 * sw ** 2 + 1.0 * math.sin(5 * a)
        return 16.0 + (d_rim - 16.0) * min(1.0, max(0.0, (r - 0.3) / 0.6))
    def floor_at(u, v):
        r, a = rnorm(u, v)
        f = zc - depth(a, min(r, 1.0))
        # back (north) and east terraces +4 m: a concentric ledge band (r > 0.74) along the N and E walls, its edge an arc
        ang = math.degrees(a)
        sect = max(min(1.0, max(0.0, (ang + 60.0) / 20.0)) * min(1.0, max(0.0, (165.0 - ang) / 20.0)), 0.0)
        terr = sect * min(1.0, max(0.0, (r - 0.735) / 0.025))
        return f + 4.0 * terr
    def gz(u, v):
        r, a = rnorm(u, v)
        if r >= 1.0:
            return plain(u, v)
        fl = floor_at(u, v)
        if r >= 0.975:                                                # the cliff (2-3 m wide band: near vertical)
            k = (r - 0.975) / 0.025
            return (fl + 3.0) + (plain(u, v) - (fl + 3.0)) * k
        if r >= 0.955:                                                # the inner rock step (ledge 3 m up)
            return fl + 3.0
        if r >= 0.945:
            return fl + 3.0 * (r - 0.945) / 0.01
        return fl
    g0 = floor_at(0.0, 0.0)
    floor_z = g0 + 0.05
    cliff_m = bpy.data.materials.new("CP_Cliff"); cliff_m.use_nodes = True
    nt = cliff_m.node_tree; N_, Ln_ = nt.nodes, nt.links
    bs = N_["Principled BSDF"]; bs.inputs["Roughness"].default_value = 0.95
    tco = N_.new("ShaderNodeTexCoord"); sx = N_.new("ShaderNodeSeparateXYZ"); Ln_.new(tco.outputs["Object"], sx.inputs[0])
    wv = N_.new("ShaderNodeTexWave"); wv.wave_type = "BANDS"; wv.bands_direction = "Z"; wv.inputs["Scale"].default_value = 0.09
    wv.inputs["Distortion"].default_value = 2.5; wv.inputs["Detail"].default_value = 3
    Ln_.new(tco.outputs["Object"], wv.inputs["Vector"])
    nz_ = N_.new("ShaderNodeTexNoise"); nz_.inputs["Scale"].default_value = 0.35; Ln_.new(tco.outputs["Object"], nz_.inputs["Vector"])
    mxf = N_.new("ShaderNodeMath"); mxf.operation = "MULTIPLY_ADD"; Ln_.new(wv.outputs["Fac"], mxf.inputs[0])
    mxf.inputs[1].default_value = 0.6; Ln_.new(nz_.outputs["Fac"], mxf.inputs[2])
    rp = N_.new("ShaderNodeValToRGB"); el = rp.color_ramp.elements
    el[0].position, el[0].color = 0.45, (*_hex("#4a4550"), 1); el[1].position, el[1].color = 0.95, (*_hex("#a3958c"), 1)
    Ln_.new(mxf.outputs[0], rp.inputs["Fac"]); Ln_.new(rp.outputs["Color"], bs.inputs["Base Color"])
    floor_m = bpy.data.materials.new("CP_Floor"); floor_m.use_nodes = True
    nt = floor_m.node_tree; N_, Ln_ = nt.nodes, nt.links
    bs = N_["Principled BSDF"]; bs.inputs["Roughness"].default_value = 0.95
    tco = N_.new("ShaderNodeTexCoord")
    vo = N_.new("ShaderNodeTexVoronoi"); vo.feature = "DISTANCE_TO_EDGE"; vo.inputs["Scale"].default_value = 0.22
    Ln_.new(tco.outputs["Object"], vo.inputs["Vector"])
    nz_ = N_.new("ShaderNodeTexNoise"); nz_.inputs["Scale"].default_value = 0.02; Ln_.new(tco.outputs["Object"], nz_.inputs["Vector"])
    rpc = N_.new("ShaderNodeValToRGB"); el = rpc.color_ramp.elements
    el[0].position, el[0].color = 0.0, (*_hex("#7e735f"), 1); el[1].position, el[1].color = 0.06, (*_hex("#c4b79c"), 1)
    Ln_.new(vo.outputs["Distance"], rpc.inputs["Fac"])
    tint = N_.new("ShaderNodeMix"); tint.data_type = "RGBA"; tint.blend_type = "MULTIPLY"; tint.inputs["Factor"].default_value = 0.35
    Ln_.new(rpc.outputs["Color"], tint.inputs["A"])
    rpn = N_.new("ShaderNodeValToRGB"); rpn.color_ramp.elements[0].color = (0.8, 0.78, 0.72, 1); rpn.color_ramp.elements[1].color = (1, 1, 1, 1)
    Ln_.new(nz_.outputs["Fac"], rpn.inputs["Fac"]); Ln_.new(rpn.outputs["Color"], tint.inputs["B"])
    Ln_.new(tint.outputs["Result"], bs.inputs["Base Color"])
    plain_mat = wg.data.materials[0] if (wg is not None and len(wg.data.materials)) else L.mat("CP_Plain", _hex("#5f7a3e"), 0.95)
    # the cut: whole WD_Ground cells over the bowl (grid aligned so the patch meets the remaining cells edge to edge)
    cxw, cyw = C[0], C[1] + MW_Y
    HX, HY = A_U + 90.0, B_V + 90.0
    X0 = gx0 + math.floor((cxw - HX - gx0) / cell) * cell; X1 = gx0 + math.ceil((cxw + HX - gx0) / cell) * cell
    Y0 = gy0 + math.floor((cyw - HY - gy0) / cell) * cell; Y1 = gy0 + math.ceil((cyw + HY - gy0) / cell) * cell
    if wg is not None and not wg.get("cp_cut"):
        bmw = bmesh.new(); bmw.from_mesh(wg.data)
        kill = [f for f in bmw.faces if X0 < f.calc_center_median().x < X1 and Y0 < f.calc_center_median().y < Y1]
        bmesh.ops.delete(bmw, geom=kill, context="FACES"); bmw.to_mesh(wg.data); bmw.free(); wg["cp_cut"] = 1
    # world trees inside the bowl go (scatter point clouds in world coordinates)
    wc = bpy.data.collections.get("World")
    for o in (wc.all_objects if wc else []):
        if o.type == "MESH" and len(o.data.polygons) == 0 and len(o.data.vertices) and any(m.type == "NODES" for m in o.modifiers):
            bmv = bmesh.new(); bmv.from_mesh(o.data)
            dv = [v for v in bmv.verts if math.hypot((v.co.x - cxw) / A_U, (v.co.y - cyw) / B_V) < 1.12]
            if dv:
                bmesh.ops.delete(bmv, geom=dv, context="VERTS"); bmv.to_mesh(o.data); o.data.update()
            bmv.free()
    # the patch, in world coordinates under WorldRoot (so WD_Ground's object-space field texture continues seamlessly)
    step = 2.5
    nx, ny = int(round((X1 - X0) / step)), int(round((Y1 - Y0) / step))
    bm = bmesh.new()
    V = []
    for i in range(nx + 1):
        row = []
        for j in range(ny + 1):
            xw, yw = X0 + (X1 - X0) * i / nx, Y0 + (Y1 - Y0) * j / ny
            u, v = xw - cxw, yw - cyw
            edge = i in (0, nx) or j in (0, ny)
            row.append(bm.verts.new((xw, yw, plain_w(xw, yw) if edge else gz(u, v))))
        V.append(row)
    RN = [[rnorm(V[i][j].co.x - cxw, V[i][j].co.y - cyw)[0] for j in range(ny + 1)] for i in range(nx + 1)]
    for i in range(nx):
        for j in range(ny):
            q = (V[i][j], V[i + 1][j], V[i + 1][j + 1], V[i][j + 1])
            rs = (RN[i][j], RN[i + 1][j], RN[i + 1][j + 1], RN[i][j + 1])
            f = bm.faces.new(q)
            zs = [x.co.z for x in q]
            if min(rs) >= 1.0:
                f.material_index = 0
            elif max(zs) - min(zs) > 1.2 or (0.94 <= min(rs) and max(rs) < 1.0):
                f.material_index = 1
            else:
                f.material_index = 2
    gob = L.obj_from_bm("CP_Ground", bm, [plain_mat, cliff_m, floor_m], coll)
    if root is not None:
        gob.parent = root; gob.matrix_parent_inverse.identity(); gob.location = (0.0, 0.0, 0.0)
    else:                                                              # no world layer: place the patch in set coords
        gob.location = (0.0, -MW_Y - 870.0, 0.0)
    gob.visible_shadow = True
    st["ground"] = gob; st["gz"] = gz
    def rim_top(a):
        u, v = A_U * 1.045 * math.cos(a), B_V * 1.045 * math.sin(a)
        return u, v, plain(u, v) + 0.3
    # ---------------------------------------------------------------- buildings
    bm = bmesh.new(); wb = bmesh.new()
    def hut(u, v, w=8.0, d=5.0, h=3.0, rot=0.0, z=None, win=2):
        z0 = (gz(u, v) + 0.15) if z is None else z
        c = Vector(P(u, v, z0))
        L.box(bm, (c.x, c.y, c.z + h / 2), (w, d, h), rot=rot, mi=0)
        L.box(bm, (c.x, c.y, c.z + h + 0.9), (w + 0.8, d + 0.8, 1.8), rot=rot, mi=1, taper=(1.0, 0.08))
        ca, sa = math.cos(rot), math.sin(rot)
        for sy in (-1, 1):                                   # one continuous lit window band per long side (reads at night
            L.box(wb, (c.x - sa * sy * (d / 2 + 0.06), c.y + ca * sy * (d / 2 + 0.06), c.z + 1.7),   # from 300 m; g3 10/27)
                  (w * 0.78, 0.14, 1.1), rot=rot)
    for u in (-100, -78, -5, 17, 39, 61):                         # back terrace (v +70): barracks 17 x 6.5 m (g3 agent 10/27)
        hut(u, 70.0 - 4.0 * (abs(u) > 90), w=17.0, d=6.5, h=3.6, rot=0.0, win=4)
    for k, v in enumerate((-48, -32, -16, 0, 16, 32, 48)):         # east terrace (u +70..+110): barracks 13 x 6 m
        um = A_U * math.sqrt(max(0.0, 1 - (v / B_V) ** 2))
        hut(min(0.86 * um, 100.0) - 6.0, v, w=13.0, d=6.0, h=3.4, rot=math.pi / 2, win=3)
    hut(-95, -50, rot=0.3); hut(-110, -5, rot=math.pi / 2)
    # mess hall 26 x 8 m (u -15, v -45): 8-window band on its north front, veranda, chimney, porch lantern
    mu, mv = -15.0, -45.0
    mz = gz(mu, mv) + 0.15
    c = Vector(P(mu, mv, mz))
    L.box(bm, (c.x, c.y, c.z + 2.75), (26.0, 8.0, 5.5), mi=2)
    L.box(bm, (c.x, c.y, c.z + 6.6), (27.0, 9.0, 2.4), mi=1, taper=(1.0, 0.06))
    L.box(bm, (c.x + 8.0, c.y - 1.5, c.z + 8.0), (1.0, 1.0, 3.2), mi=3)                 # chimney
    L.box(bm, (c.x, c.y + 5.2, c.z + 3.0), (26.0, 2.4, 0.25), mi=1)                     # veranda roof
    for x in np.linspace(-12.5, 12.5, 6):
        L.box(bm, (c.x + x, c.y + 6.2, c.z + 1.5), (0.25, 0.25, 3.0), mi=3)
    L.box(wb, (c.x, c.y + 4.06, c.z + 2.6), (23.0, 0.14, 1.5))              # the 8-window band as one continuous lit strip
    for x in np.linspace(-11.0, 11.0, 8)[:-1] + 1.57:                      # dark mullions keep the 8 windows readable by day
        L.box(bm, (c.x + x, c.y + 4.1, c.z + 2.6), (0.3, 0.16, 1.55), mi=3)
    lan = Vector((c.x, c.y + 6.3, c.z + 2.6))
    L.box(wb, tuple(lan), (0.5, 0.5, 0.6))
    # graduation stair: 14 steps x 30 m in front of the mess hall (toward the floor centre), braziers at both ends
    for k in range(14):
        L.box(bm, (c.x, c.y + 21.6 - k * 1.0, c.z + 0.09 * (k + 1)), (30.0, 1.0, 0.18 * (k + 1)), mi=3)
    fb = bmesh.new()
    br = []
    for sx in (-1, 1):
        b = Vector((c.x + sx * 16.5, c.y + 22.5, c.z))
        for k in range(3):
            a = k * 2 * math.pi / 3
            L.cyl(bm, (b.x + 0.8 * math.cos(a), b.y + 0.8 * math.sin(a), b.z), (b.x, b.y, b.z + 1.9), 0.06, 0.05, seg=4, mi=4)
        L.cyl(bm, (b.x, b.y, b.z + 1.8), (b.x, b.y, b.z + 2.1), 0.55, 0.7, seg=8, mi=4)
        L.cyl(fb, (b.x, b.y, b.z + 2.0), (b.x, b.y, b.z + 3.4), 0.55, 0.05, seg=6)
        br.append(b + Vector((0, 0, 3.0)))
    # watchtower: lattice 20 m at (u -45, v +70), enclosed stair box on its east face
    tc = Vector(P(-45.0, 70.0, gz(-45.0, 70.0)))
    for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        L.cyl(bm, (tc.x + sx * 2.6, tc.y + sy * 2.6, tc.z), (tc.x + sx * 1.6, tc.y + sy * 1.6, tc.z + 18.0), 0.18, 0.15, seg=4, mi=3)
    for z in (4.5, 9.0, 13.5):
        f = 1.0 - z / 18.0 * 0.38
        for (ax, ay), (bx, by) in (((-1, -1), (1, 1)), ((1, -1), (-1, 1)), ((-1, -1), (1, -1)), ((-1, 1), (1, 1))):
            L.cyl(bm, (tc.x + ax * 2.6 * f, tc.y + ay * 2.6 * f, tc.z + z - 4.5), (tc.x + bx * 2.6 * f, tc.y + by * 2.6 * f, tc.z + z),
                  0.07, 0.07, seg=4, mi=3)
    L.box(bm, (tc.x, tc.y, tc.z + 18.3), (4.4, 4.4, 0.4), mi=3)
    L.box(bm, (tc.x, tc.y, tc.z + 19.3), (4.4, 4.4, 1.6), mi=0)
    L.box(bm, (tc.x, tc.y, tc.z + 21.0), (5.2, 5.2, 1.8), mi=1, taper=(0.05, 0.05))
    L.box(bm, (tc.x + 3.6, tc.y, tc.z + 9.0), (2.0, 3.0, 18.0), mi=0)
    L.box(wb, (tc.x, tc.y - 2.26, tc.z + 19.4), (1.6, 0.12, 0.8))
    # A-frame rigs (v +38; u -10/+12/+34/+56)
    for u in (-10.0, 12.0, 34.0, 56.0):
        q = Vector(P(u, 38.0, gz(u, 38.0)))
        for sx in (-1, 1):
            a_ = Vector((q.x + sx * 3.0, q.y, q.z + 7.5))
            for sy in (-1, 1):
                L.cyl(bm, (q.x + sx * 3.0, q.y + sy * 2.2, q.z), tuple(a_), 0.09, 0.08, seg=4, mi=5)
        L.cyl(bm, (q.x - 3.0, q.y, q.z + 7.4), (q.x + 3.0, q.y, q.z + 7.4), 0.08, 0.08, seg=4, mi=5)
    # (owner 10/27 07:34: the pole field 16 x 8 at (u +25, v +5) is REMOVED: "the field of many sticks"; material slot 6 kept unused)
    ob = L.obj_from_bm("CP_Buildings", bm, [M["wall"], M["roof"], M["stone"], M["dark"], M["steel"], M["steel"], M["pole"]], coll)
    st["objs"].append(ob)
    st["objs"].append(L.obj_from_bm("CP_Windows", wb, [win_m], coll))
    st["objs"].append(L.obj_from_bm("CP_BrazierFire", fb, [fire_m], coll))
    # soft warm glow balls at the braziers and the porch lantern (the toon pass drops point-light colour; g3 10/27)
    gm = bpy.data.materials.get("CP_Glow") or bpy.data.materials.new("CP_Glow")
    gm.use_nodes = True; gnt = gm.node_tree; GN = gnt.nodes
    for n in list(GN):
        if n.type != "OUTPUT_MATERIAL":
            GN.remove(n)
    gem = GN.new("ShaderNodeEmission"); gem.inputs["Color"].default_value = (1.0, 0.28, 0.05, 1.0); gem.inputs["Strength"].default_value = 0.0
    gtr = GN.new("ShaderNodeBsdfTransparent"); glw = GN.new("ShaderNodeLayerWeight"); glw.inputs["Blend"].default_value = 0.5
    gpw = GN.new("ShaderNodeMath"); gpw.operation = "POWER"; gpw.inputs[1].default_value = 2.5
    gnt.links.new(glw.outputs["Facing"], gpw.inputs[0])
    ginv = GN.new("ShaderNodeMath"); ginv.operation = "SUBTRACT"; ginv.inputs[0].default_value = 1.0; gnt.links.new(gpw.outputs[0], ginv.inputs[1])
    gmx = GN.new("ShaderNodeMixShader"); gnt.links.new(ginv.outputs[0], gmx.inputs[0])
    gnt.links.new(gtr.outputs[0], gmx.inputs[1]); gnt.links.new(gem.outputs[0], gmx.inputs[2])
    gnt.links.new(gmx.outputs[0], next(n for n in GN if n.type == "OUTPUT_MATERIAL").inputs["Surface"])
    for k_, v_ in (("surface_render_method", "BLENDED"), ("use_transparent_shadow", True)):
        try:
            setattr(gm, k_, v_)
        except Exception:
            pass
    gm["toon"] = 1
    gb = bmesh.new()
    for k, p in enumerate(br + [lan]):
        res = bmesh.ops.create_icosphere(gb, subdivisions=2, radius=3.2 if k < 2 else 1.8)
        for v in res["verts"]:
            v.co += Vector(p)
    for f in gb.faces:
        f.smooth = True
    go = L.obj_from_bm("CP_Glow", gb, [gm], coll)
    go.visible_shadow = False
    st["objs"].append(go); st["glow"] = gem
    # ---------------------------------------------------------------- fence W -> mid-N (posts), palisade mid-N -> E (+320 m east)
    bm = bmesh.new()
    posts = []
    for a in np.radians(np.arange(180.0, 90.0, -3.0)):
        u, v, z = rim_top(a)
        q = Vector(P(u, v, z - 0.5))
        L.cyl(bm, tuple(q), (q.x, q.y, q.z + 2.2), 0.08, 0.06, seg=4, mi=0)
        posts.append(q)
    for p0, p1 in zip(posts, posts[1:]):                           # barbed wire: 3 strands between the posts
        for hz in (0.9, 1.5, 2.1):
            L.cyl(bm, (p0.x, p0.y, p0.z + hz), (p1.x, p1.y, p1.z + hz), 0.03, 0.03, seg=3, mi=0)
    pal = [rim_top(a) for a in np.radians(np.arange(90.0, -1.0, -1.2))]
    u_e, v_e, z_e = pal[-1]
    for k in range(1, 50):
        u = u_e + k * 6.5
        pal.append((u, v_e, gz(u, v_e) + 0.2))
    for (u0, v0, z0), (u1, v1, z1) in zip(pal, pal[1:]):
        n = max(1, int(math.hypot(u1 - u0, v1 - v0) / 0.55))
        for k in range(n):
            f = k / n
            u, v, z = u0 + (u1 - u0) * f, v0 + (v1 - v0) * f, z0 + (z1 - z0) * f
            q = Vector(P(u, v, z - 0.4))
            hgt = 3.6 + 0.4 * ((k * 5) % 3) / 2
            L.cyl(bm, tuple(q), (q.x, q.y, q.z + hgt - 0.5), 0.24, 0.24, seg=5, mi=0)
            L.cyl(bm, (q.x, q.y, q.z + hgt - 0.5), (q.x, q.y, q.z + hgt), 0.24, 0.02, seg=5, mi=0)
    st["objs"].append(L.obj_from_bm("CP_Palisade", bm, [M["dark"]], coll))
    # ---------------------------------------------------------------- lake 250 x 150 m at (u +150, v +420) (bible g3; g3 agent 10/27)
    bm = bmesh.new()
    ring = []
    for k in range(48):
        a = 2 * math.pi * k / 48
        u, v = 150.0 + 125.0 * math.cos(a) * (1 + 0.06 * math.sin(3 * a)), 420.0 + 75.0 * math.sin(a) * (1 + 0.05 * math.cos(2 * a))
        ring.append((u, v))
    zl = min(gz(u, v) for u, v in ring + [(150.0, 420.0)]) + 0.2
    cv = bm.verts.new(P(150.0, 420.0, zl))
    rv = [bm.verts.new(P(u, v, zl)) for u, v in ring]
    for k in range(48):
        bm.faces.new((cv, rv[k], rv[(k + 1) % 48]))
    st["objs"].append(L.obj_from_bm("CP_Lake", bm, [L.mat("CP_LakeWater", _hex("#4e6e62"), 0.15)], coll))
    # conifer stands on the plain round the bowl (dark cones 12-20 m)
    bm = bmesh.new(); rc = random.Random(seed + 7)
    for cu, cv, n in ((-215.0, 60.0, 30), (-175.0, -130.0, 24), (30.0, 175.0, 26), (235.0, -55.0, 22), (-90.0, 190.0, 18)):
        for _ in range(n):
            u, v = cu + rc.gauss(0, 22), cv + rc.gauss(0, 18)
            if rnorm(u, v)[0] < 1.12:
                continue
            h = rc.uniform(12.0, 20.0); q = Vector(P(u, v, gz(u, v) - 0.3))
            L.cyl(bm, tuple(q), (q.x, q.y, q.z + h), h * 0.24, 0.0, seg=6, mi=0)
    st["objs"].append(L.obj_from_bm("CP_Conifers", bm, [L.mat("CP_Conifer", _hex("#1f2d20"), 0.9)], coll))
    # ---------------------------------------------------------------- warm point lights (braziers, porch lantern)
    for k, p in enumerate(br + [lan]):
        ld = bpy.data.lights.new(f"CP_Lamp{k}", "POINT"); ld.color = (1.0, 0.55, 0.22); ld.energy = 0.0
        ld.shadow_soft_size = 0.5
        try:
            ld.use_shadow = False
        except Exception:
            pass
        lo = bpy.data.objects.new(f"CP_Lamp{k}", ld); lo.location = p; coll.objects.link(lo)
        st["lights"].append((ld, 60000.0 if k < 2 else 15000.0))
    st["floor_z"] = floor_z
    return st

def set_night(st, f):
    """f 1 = graduation night: lit windows, braziers, lantern; 0 = day (all off)."""
    f = float(min(1.0, max(0.0, f)))
    st["win"].inputs["Strength"].default_value = 11.0 * f
    st["fire"].inputs["Strength"].default_value = 16.0 * f
    if st.get("glow") is not None:
        st["glow"].inputs["Strength"].default_value = 5.0 * f
    for ld, e in st["lights"]:
        ld.energy = e * f
    for n in ("CP_Windows", "CP_BrazierFire", "CP_Glow"):
        o = bpy.data.objects.get(n)
        if o is not None:
            h = f <= 0.002
            if o.hide_render != h:
                o.hide_render = o.hide_viewport = h
