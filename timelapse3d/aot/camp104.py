"""104th TRAINING CORPS CAMP (SCENE_BIBLE_v2 g3 layout) as a light set piece for the Trost-set segments.

Built by seg_g4 (the camp is in frame for g4's first ~2 s: the g3 -> g4 seam looks at it at graduation night).  The g3 build
can import it too, so both sides of the seam show the same camp:
    import camp104 as CP
    st = CP.build(L, M2S, ground_M, coll)        # once (L = aotlib, M2S / ground_M = render_seg site helpers)
    CP.set_night(st, f)                          # f 1 = graduation night (lit windows, braziers, lanterns), 0 = day
Frame M, centre C = (-1450, 1520), u east, v north (bible g3): sunken quarry bowl (floor ellipse 230 x 170 m, rim 14 m, 18-22 m
SW, fluted cliffs, inner rock step), back terrace huts (v +70), lattice watchtower 20 m (u -45, v +70) with a stair box on its
east face, east-terrace huts (u +70..+110), mess hall 26 x 8 m (u -15, v -45) with an 8-window band, veranda, porch lantern,
chimney and the graduation stair (14 steps x 30 m) + 2 tripod braziers on its front, pole field 16 x 8 (u +25, v +5),
4 A-frame rigs (v +38; u -10/+12/+34/+56), huts (u -95, v -50) and (u -110, v -5), barbed post fence W -> mid-N, pointed
palisade mid-N -> E continuing 320 m east.
PROXY NOTES: the bowl is a raised cliff ring on the world relief (the trost set has no terrain hook this late in the build), the
lake and the cliff-cut road are left out.
"""
import math, random
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
    M = dict(floor=L.mat("CP_Floor", _hex("#e2d8c2"), 0.95, var=0.25, var_scale=0.08, color2=_hex("#cfc3aa")),
             cliff=L.mat("CP_Cliff", _hex("#b0a08e"), 0.95, var=0.3, var_scale=0.05, color2=_hex("#8a7c74")),
             rock=L.mat("CP_RockStep", _hex("#9a8c80"), 0.95),
             timber=L.mat("CP_Timber", _hex("#7a5a3e"), 0.9), dark=L.mat("CP_DarkTimber", _hex("#4a3426"), 0.9),
             roof=L.mat("CP_Roof", _hex("#5b4a40"), 0.85), slate=L.mat("CP_Slate", _hex("#4f5058"), 0.85),
             stone=L.mat("CP_Stone", _hex("#9b9486"), 0.9), steel=L.mat("CP_Steel", _hex("#5c6570"), 0.6),
             pole=L.mat("CP_Pole", _hex("#6b5038"), 0.9), wall=L.mat("CP_HutWall", _hex("#b8a888"), 0.9),
             grass=L.mat("CP_RimGrass", _hex("#5f7a3e"), 0.95, var=0.3, var_scale=0.05, color2=_hex("#4c6634")))
    win_m, win_em = _emit("CP_Window", (1.0, 0.62, 0.26), 0.0)
    fire_m, fire_em = _emit("CP_Fire", (1.0, 0.45, 0.10), 0.0)
    st = dict(win=win_em, fire=fire_em, lights=[], objs=[])
    # ---------------------------------------------------------------- floor (ellipse fan following the relief)
    bm = bmesh.new()
    NA, NR = 72, 7
    rows = []
    for i in range(NR + 1):
        s = i / NR
        ring = []
        for k in range(NA if i else 1):
            a = 2 * math.pi * k / NA
            u, v = A_U * s * math.cos(a), B_V * s * math.sin(a)
            ring.append(bm.verts.new(P(u, v, max(gz(u, v), g0 - 1.0) + 0.15)))
        rows.append(ring)
    for k in range(NA):
        bm.faces.new((rows[0][0], rows[1][k], rows[1][(k + 1) % NA]))
    for i in range(1, NR):
        for k in range(NA):
            bm.faces.new((rows[i][k], rows[i + 1][k], rows[i + 1][(k + 1) % NA], rows[i][(k + 1) % NA]))
    st["objs"].append(L.obj_from_bm("CP_Floor", bm, [M["floor"]], coll))
    # ---------------------------------------------------------------- rim: fluted cliff ring, inner rock step, outer slope
    bm = bmesh.new()
    NA2 = 240
    prof = []
    for k in range(NA2):
        a = 2 * math.pi * k / NA2
        sw = max(0.0, math.cos(a - math.radians(225.0)))           # taller to the SW (18-22 m)
        h = RIM_H + 6.0 * sw ** 2 + 1.2 * math.sin(a * 7.0 + 1.3)
        fl = 0.9 * math.sin(a * 63.0) + 0.5 * math.sin(a * 151.0)    # vertical flutes
        def e(s, z, a=a):
            u, v = A_U * s * math.cos(a), B_V * s * math.sin(a)
            return bm.verts.new(P(u, v, gz(u, v) + z))
        prof.append([e(0.955, 0.15), e(0.955, 2.2), e(0.985, 2.4), e(0.99 + fl / 400.0, 2.4), e(1.0 + fl / 260.0, h * 0.55),
                     e(1.012 + fl / 300.0, h), e(1.10, h + 0.6), e(1.30, 0.0)])
    for k in range(NA2):
        a_, b_ = prof[k], prof[(k + 1) % NA2]
        for j in range(len(a_) - 1):
            f = bm.faces.new((a_[j], b_[j], b_[j + 1], a_[j + 1]))
            f.material_index = 1 if j < 3 else (0 if j < 5 else 2)      # step rock | fluted cliff | grassy top + outer slope
    st["objs"].append(L.obj_from_bm("CP_Cliffs", bm, [M["cliff"], M["rock"], M["grass"]], coll))
    def rim_top(a):
        sw = max(0.0, math.cos(a - math.radians(225.0)))
        h = RIM_H + 6.0 * sw ** 2 + 1.2 * math.sin(a * 7.0 + 1.3)
        u, v = A_U * 1.06 * math.cos(a), B_V * 1.06 * math.sin(a)
        return u, v, gz(u, v) + h + 0.5
    # ---------------------------------------------------------------- buildings
    bm = bmesh.new(); wb = bmesh.new()
    def hut(u, v, w=8.0, d=5.0, h=3.0, rot=0.0, z=None, win=2):
        z0 = (gz(u, v) + 0.15) if z is None else z
        c = Vector(P(u, v, z0))
        L.box(bm, (c.x, c.y, c.z + h / 2), (w, d, h), rot=rot, mi=0)
        L.box(bm, (c.x, c.y, c.z + h + 0.9), (w + 0.8, d + 0.8, 1.8), rot=rot, mi=1, taper=(1.0, 0.08))
        ca, sa = math.cos(rot), math.sin(rot)
        for k in range(win):
            x = (k - (win - 1) / 2) * w / win
            for sy in (-1, 1):
                L.box(wb, (c.x + ca * x - sa * sy * (d / 2 + 0.06), c.y + sa * x + ca * sy * (d / 2 + 0.06), c.z + 1.6),
                      (1.0, 0.12, 0.9), rot=rot)
    for u in (-100, -78, -5, 17, 39, 61):                         # back terrace (v +70)
        hut(u, 70.0 - 4.0 * (abs(u) > 90), rot=0.0)
    for k, v in enumerate((-48, -32, -16, 0, 16, 32, 48)):         # east terrace (u +70..+110)
        um = A_U * math.sqrt(max(0.0, 1 - (v / B_V) ** 2))
        hut(min(0.86 * um, 100.0) - 4.0, v, w=7.0, d=5.0, rot=math.pi / 2)
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
    for x in np.linspace(-11.0, 11.0, 8):
        L.box(wb, (c.x + x, c.y + 4.06, c.z + 2.6), (1.4, 0.12, 1.3))
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
    # pole field 16 x 8 poles centred (u +25, v +5)
    for i in range(16):
        for j in range(8):
            u, v = 25.0 + (i - 7.5) * 3.0, 5.0 + (j - 3.5) * 3.0
            q = Vector(P(u, v, gz(u, v)))
            L.cyl(bm, (q.x, q.y, q.z), (q.x, q.y, q.z + 6.0 + 1.5 * ((i * 7 + j * 3) % 3)), 0.14, 0.12, seg=4, mi=6)
    ob = L.obj_from_bm("CP_Buildings", bm, [M["wall"], M["roof"], M["stone"], M["dark"], M["steel"], M["steel"], M["pole"]], coll)
    st["objs"].append(ob)
    st["objs"].append(L.obj_from_bm("CP_Windows", wb, [win_m], coll))
    st["objs"].append(L.obj_from_bm("CP_BrazierFire", fb, [fire_m], coll))
    # ---------------------------------------------------------------- fence W -> mid-N (posts), palisade mid-N -> E (+320 m east)
    bm = bmesh.new()
    for a in np.radians(np.arange(180.0, 90.0, -3.0)):
        u, v, z = rim_top(a)
        q = Vector(P(u, v, z - 0.5))
        L.cyl(bm, tuple(q), (q.x, q.y, q.z + 2.2), 0.08, 0.06, seg=4, mi=0)
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
    st["win"].inputs["Strength"].default_value = 26.0 * f
    st["fire"].inputs["Strength"].default_value = 60.0 * f
    for ld, e in st["lights"]:
        ld.energy = e * f
    for n in ("CP_Windows", "CP_BrazierFire"):
        o = bpy.data.objects.get(n)
        if o is not None:
            h = f <= 0.002
            if o.hide_render != h:
                o.hide_render = o.hide_viewport = h
