"""s2 v15 STOHESS CITY FIGHT FROM THE SKY (STOHESS_v15.md, user 10/31 09:20-09:23): replaces s2's brawl / tableaux.
ONE high sky camera (fixed height, slow drift, small turns), the cathedral in frame, titans x1.5 (just taller than the
houses), everything fast.   SEG=s2v15 bash aot/forest/render_part2.sh   (comes after s1v15, same sky camera at the seam)

  0.0-1.6   the Female runs south down the cleared lane; 2nd lightning: Eren's titan bursts up in the square
  1.6-3.9   chase along the square street; he cuts her off north of the cathedral
  3.9-4.3   PUNCH in the face -> she is KNOCKED FLYING south into the cathedral
  4.8-8.0   THE CATHEDRAL COLLAPSES: pre-fractured nave / drum / dome chunks fall in a wave from the impact, the bell
            tower tilts and falls south, a big dust cloud rolls out through the streets; ruin + dust stay in frame
  6.6-9.6   she climbs out of the ruin and runs east through the burning houses, Eren behind her
  9.6-12.2  she climbs Wall Sina, falls; 12.3 Eren on top of her at the wall foot; steam
  13.4-20   the camera leaves the sky for the wall-titan ending (the existing s2 face; rebuilt separately)
"""
import math, os, sys, random
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from forest import common as C
from stohess import layout as SL
from stohess.layout import S
import camchan
import seg_s2 as S2
try:
    import bpy
except ImportError:
    bpy = None

TS = 1.6                                                        # titan scale: just taller than the 8-26 m houses
DUR = 21.4
BEATS = dict(lightning=(0.2, 1.8), rise=(0.9, 1.6), punch=4.05, fly=(4.15, 4.75), impact=4.75, tower=(5.1, 6.6),
             getup=(6.4, 6.9), run=(6.9, 10.8), climb=(10.8, 12.6), fall=(12.6, 13.2), mount=13.3, face=12.2, crane=(14.6, 18.8))
NX, NY = SL.CLIMB_N
_off = S2._off
FOOT = S2.FOOT
KX, KY = SL.CRYSTAL
CX, CY = SL.CLIMB
CH = SL.CHURCH                                                   # nave x 63..97, y -193..-147 (frame S)
IMPACT = (81.0, -148.0, 12.0)

def _W(sx, sy, dz=0.0):
    w = S(sx, sy)
    return (w[0], w[1], C.G(w[0], w[1]) + dz)

# ---------------------------------------------------------------- paths (t, x, y) frame S
FPATH = [(0.0, 60.0, 10.0), (1.6, 66.0, -30.0), (3.6, 74.0, -84.0), (4.15, 75.0, -92.0)]
FRUN = [(6.9, 84.0, -150.0), (7.6, 130.0, -132.0), (8.3, 200.0, -140.0), (9.1, 330.0, -150.0), (10.2, 560.0, -190.0),
        (10.8,) + FOOT]
EPATH = [(0.0, -40.0, -60.0), (1.6, -40.0, -60.0), (2.6, 10.0, -68.0), (3.4, 56.0, -68.0), (3.9, 72.0, -74.0), (6.9, 72.0, -74.0),
         (7.7, 92.0, -122.0), (8.5, 200.0, -128.0), (9.3, 330.0, -138.0), (10.5, 540.0, -175.0), (11.3,) + _off(SL.CLIMB, 30.0),
         (13.2,) + _off(SL.CLIMB, 30.0)]
FLY0 = (75.0, -92.0); FLY1 = (82.0, -160.0)
LIE = (82.0, -163.0)

def fem_S(t):
    if t < BEATS["fly"][0]:
        x, y, _ = C.path_at(FPATH, t); return x, y
    if t < BEATS["impact"] + 0.25:
        u = C.ss(BEATS["fly"][0], BEATS["impact"] + 0.25, t) * 0.6 + 0.4 * min(1.0, (t - BEATS["fly"][0]) / 0.85)
        return FLY0[0] + (FLY1[0] - FLY0[0]) * u, FLY0[1] + (FLY1[1] - FLY0[1]) * u
    if t < FRUN[0][0]:
        return LIE
    if t < BEATS["climb"][0]:
        x, y, _ = C.path_at([(BEATS["getup"][1] - 0.2,) + LIE] + FRUN, t); return x, y
    if t < BEATS["fall"][1]:
        return FOOT if t < BEATS["fall"][0] else (FOOT[0] + (KX - FOOT[0]) * C.ss(*BEATS["fall"], t), FOOT[1] + (KY - FOOT[1]) * C.ss(*BEATS["fall"], t))
    return KX, KY
def eren_S(t):
    x, y, _ = C.path_at(EPATH, t); return x, y
WALL_YAW = S2.WALL_YAW

def fem_z(t):
    a, b = BEATS["fly"]
    if a <= t < b + 0.25:                                        # thrown: arc up, then into the nave wall at ~12 m
        u = (t - a) / (b + 0.25 - a)
        return 14.0 * math.sin(math.pi * min(u, 0.75) / 1.5) * (1 - u) + 6.0 * u
    if BEATS["climb"][0] <= t < BEATS["fall"][0]:
        return 36.0 * C.ss(BEATS["climb"][0], BEATS["climb"][1], t)
    if BEATS["fall"][0] <= t < BEATS["fall"][1]:
        u = (t - BEATS["fall"][0]) / (BEATS["fall"][1] - BEATS["fall"][0])
        return 36.0 * max(0.0, 1.0 - u * u)
    return 0.0

def fem_state(t, TB):
    """(pose, yaw, pitch, dz)"""
    run = C.fem_run(2 * math.pi * 3.2 * t, lean=26.0)
    ex, ey = eren_S(t); x, y = fem_S(t)
    face_e = C.yaw_of(ex - x, ey - y + 1e-9)
    if t < 3.5:
        x2, y2 = fem_S(t + 0.05); x1, y1 = fem_S(t - 0.05)
        return run, C.yaw_of(x2 - x1, y2 - y1 + 1e-9), 0.0, 0.0
    if t < BEATS["fly"][0]:                                      # she turns to face him, guard up
        return C.fpose_blend(run, C.FPOSE["guard"], C.ss(3.5, 3.8, t)), face_e, 0.0, 0.0
    if t < BEATS["impact"] + 0.25:                               # knocked flying backwards, head snapped back
        u = C.ss(BEATS["fly"][0], BEATS["impact"] + 0.25, t)
        return TB.POSE_F["punched"], C.yaw_of(-0.12, 1.0), -0.35 - 1.0 * u, 0.0
    if t < BEATS["getup"][0]:                                    # on her back in the ruin
        return TB.POSE_F["down"], C.yaw_of(-0.12, 1.0), math.pi / 2, 2.0
    if t < BEATS["getup"][1]:
        u = C.ss(*BEATS["getup"], t)
        return C.fpose_blend(TB.POSE_F["down"], C.FPOSE["crouch"], u), C.yaw_of(1.0, 0.2), math.pi / 2 * (1 - u), 2.0 * (1 - u) + C.FZ["crouch"] * TS * u
    if t < BEATS["climb"][0] - 0.3:
        x2, y2 = fem_S(t + 0.05); x1, y1 = fem_S(t - 0.05)
        return run, C.yaw_of(x2 - x1, y2 - y1 + 1e-9), 0.0, 0.0
    if t < BEATS["fall"][0]:
        a = math.sin(2 * math.pi * 2.2 * t)
        return {"upperarm01.L": (165 + 18 * a, 0, 20), "upperarm01.R": (165 - 18 * a, 0, -20), "lowerarm01.L": (25, 0, 0),
                "lowerarm01.R": (25, 0, 0), "upperleg01.L": (-35 - 20 * a, 0, 0), "upperleg01.R": (-35 + 20 * a, 0, 0),
                "lowerleg01.L": (70, 0, 0), "lowerleg01.R": (70, 0, 0), "neck01": (-25, 0, 0), "spine01": (-6, 0, 0)}, WALL_YAW, 0.0, 0.0
    if t < BEATS["mount"]:
        return C.FPOSE["guard"], WALL_YAW, -0.4 * C.ss(*BEATS["fall"], t), 0.0
    return TB.POSE_F["down"], WALL_YAW, math.pi / 2, 2.2 * TS

def eren_state(t, er, TB):
    P, G6 = er.P, er.G6
    if t < BEATS["rise"][1]:
        return G6.blend(P["crouch"], P["roar"], C.ss(1.2, 1.6, t))
    walk = G6._walk_feet(P["run"], 2 * math.pi * 2.6 * t, 3.2, lift=1.4)
    if t < 3.7:
        return walk
    if t < BEATS["punch"] + 0.5:                                  # the right fist into her face
        return G6.blend(P["boxer"], TB.eren_specs(G6, P)["punch"], C.bump(t, 3.75, BEATS["punch"] - 0.05, BEATS["punch"] + 0.25, BEATS["punch"] + 0.5))
    if t < 7.0:
        return G6.blend(P["boxer"], P["roar"], C.bump(t, 5.0, 5.3, 6.2, 6.6))
    if t < 11.3:
        return walk
    if t < BEATS["fall"][1]:
        return G6.blend(P["roar"], P["climb"], 0.5 + 0.5 * math.sin(t * 3.0))
    if t < BEATS["mount"]:
        return P["lunge"]
    return P["crouch"]

# ---------------------------------------------------------------- camera: ONE high sky view (frame S, z above ground)
H = 110.0                                                        # v16 (cloud QA v15): 190 m left the titans unreadable
OFF = (-150.0, 55.0)                                             # constant WNW offset: the view angle stays the same, only translates
LENS = 42.0
def _k(t, p, l, lens):
    return (t, S(*p), S(*l), lens)
def _ck(t, tx, ty, tz=0.0, lens=LENS):
    return _k(t, (tx + OFF[0], ty + OFF[1], H + tz), (tx, ty, tz), lens)
SEAM_IN = dict(pos=S(20.0 + OFF[0], -25.0 + OFF[1], H), look=S(20.0, -25.0, 0.0), lens=LENS, vel=(2.0, -16.0, 0.0))
CAM_KEYS = [
    (0.0, SEAM_IN["pos"], SEAM_IN["look"], SEAM_IN["lens"]),     # her run + Eren's lightning in the square
    _ck(1.6, 25.0, -50.0),
    _ck(3.2, 72.0, -122.0),                                      # the chase: the cathedral centred beyond them
    _ck(4.75, 84.0, -150.0),                                     # punch -> she flies into it
    _ck(6.9, 92.0, -168.0),                                      # the collapse: tower falls south, dust, the ruin
    _ck(8.3, 185.0, -140.0),                                     # the run east past the burning houses
    _ck(9.3, 330.0, -150.0),
    _ck(10.5, 530.0, -180.0),
    _ck(12.4, FOOT[0] - 6.0, FOOT[1] + 3.0, 22.0, 40.0),          # the climb up the wall
    _ck(14.2, KX, KY, 4.0, 40.0),                                # she falls; Eren on top of her
    _k(16.4, _off(SL.CLIMB, 70.0) + (40.0,), (CX, CY, 30.0), 35.0),               # up to the wall face
    _k(17.8, _off(SL.CLIMB, 60.0) + (38.0,), (CX, CY, SL.FACE_Z), 42.0),
    _k(18.8, _off(SL.CLIMB, 55.0, 2.0) + (SL.FACE_Z + 2.0,), (CX, CY, SL.FACE_Z + 0.5), 45.0),
    _k(DUR, _off(SL.CLIMB, 54.0, 2.0) + (SL.FACE_Z + 2.0,), (CX, CY, SL.FACE_Z + 0.5), 46.0),
]
CAM = camchan.CamPath(CAM_KEYS, v_in=SEAM_IN["vel"], v_out=(0.0, 0.0, 0.0))
CAM_LIMITS = dict(speed=1500.0, yaw=120.0, hmin=10.0, hmax=600.0, pitch=(-10.0, 70.0), lens=(33.0, 50.0))
PLAN = [(0.0, "morning"), (5.0, "day"), (14.0, "afternoon"), (17.0, "afternoon"), (19.5, "dusk"), (DUR, "dusk")]
LIGHT = C.LightRig(*C.light_plan(PLAN))
TRACK = {}
S_ = {}

# ---------------------------------------------------------------- the cathedral, pre-fractured
def _fracture(src, cell, c, tag):
    """split a closed mesh object (world-space verts) into solidified shell chunks on a grid of `cell` (x, y, z) m."""
    import bmesh
    from mathutils import Vector
    bm = bmesh.new(); bm.from_mesh(src.data); bm.transform(src.matrix_world)
    xs = [v.co.x for v in bm.verts]; ys = [v.co.y for v in bm.verts]; zs = [v.co.z for v in bm.verts]
    lo = Vector((min(xs), min(ys), min(zs)))
    for ax, (a, b) in enumerate(((min(xs), max(xs)), (min(ys), max(ys)), (min(zs), max(zs)))):
        k = 1
        while a + k * cell[ax] < b - 0.5:
            no = [0, 0, 0]; no[ax] = 1
            co = [0, 0, 0]; co[ax] = a + k * cell[ax]
            bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-4, plane_co=co, plane_no=no)
            k += 1
    groups = {}
    for f in bm.faces:
        if f.normal.z < -0.9 and f.calc_center_median().z < lo.z + 0.5:
            continue                                                 # the floor stays (hidden under the rubble)
        cc = f.calc_center_median()
        key = tuple(int((cc[i] - lo[i]) // cell[i]) for i in range(3))
        groups.setdefault(key, []).append(f)
    mats = list(src.data.materials)
    out = []
    for key, fs in groups.items():
        nb = bmesh.new(); vm = {}
        for f in fs:
            vs = []
            for v in f.verts:
                if v.index not in vm:
                    vm[v.index] = nb.verts.new(v.co)
                vs.append(vm[v.index])
            try:
                nf = nb.faces.new(vs); nf.material_index = f.material_index
            except ValueError:
                pass
        ctr = sum((v.co for v in nb.verts), Vector()) / max(1, len(nb.verts))
        for v in nb.verts:
            v.co -= ctr
        try:
            bmesh.ops.solidify(nb, geom=nb.faces[:], thickness=1.2)
        except Exception:
            pass
        ob = C.mesh_obj(f"S2V_{tag}_{len(out)}", nb, mats, c)
        ob.location = ctr; ob.rotation_mode = "XYZ"
        out.append(ob)
    bm.free()
    return out

def build_collapse(c):
    rnd = random.Random(1850)
    srcs = [(bpy.data.objects.get("ST_Church"), (7.0, 7.0, 6.0), "nave"), (bpy.data.objects.get("ST_ChurchDome"), (6.0, 6.0, 5.0), "dome"),
            (bpy.data.objects.get("ST_BellTower"), (10.0, 10.0, 8.0), "tower")]
    S_["church"] = [s for s, _, _ in srcs if s is not None]
    imp = np.array(_W(IMPACT[0], IMPACT[1], IMPACT[2]))
    cw = np.array(_W(*CH))
    g = 34.0                                                     # sped-up gravity (the whole sequence plays fast)
    ch = []
    for src, cell, tag in srcs:
        if src is None:
            continue
        for ob in _fracture(src, cell, c, tag):
            p0 = np.array(ob.location)
            d = float(np.linalg.norm(p0 - imp))
            gz = C.G(p0[0], p0[1])
            if tag == "tower":
                ch.append(dict(ob=ob, p0=p0, tower=True, gz=gz, spin=np.array([rnd.uniform(-2, 2) for _ in range(3)])))
                continue
            rad = p0[:2] - cw[:2]; rn = np.linalg.norm(rad) + 1e-6
            push = 16.0 * math.exp(-d / 22.0)                    # the impact side is driven in (south), the rest falls
            v = np.array((0.12 * push + rad[0] / rn * rnd.uniform(1, 5), -push + rad[1] / rn * rnd.uniform(1, 5), rnd.uniform(-1, 5)))
            if tag == "dome":
                v[:2] *= -0.4                                    # the dome caves in
            hz = gz + 1.0 + 7.0 * math.exp(-(rn / 16.0) ** 2) * rnd.uniform(0.3, 1.0)
            z0, vz = p0[2], v[2]
            disc = vz * vz + 2 * g * max(0.0, z0 - hz)
            tl = (vz + math.sqrt(disc)) / g
            ch.append(dict(ob=ob, p0=p0, v=v, tl=tl, t0=BEATS["impact"] + 0.04 + d / 70.0 + rnd.uniform(0, 0.18),
                           w=np.array([rnd.uniform(-4, 4) for _ in range(3)]), tower=False, g=g))
    S_["chunks"] = ch
    print(f"[s2v15] cathedral: {len(ch)} chunks ({sum(o['tower'] for o in ch)} tower)", flush=True)
    for o in ch:
        C.hide(o["ob"], True)
    # the tower pivots on its south base edge and falls south (screen right)
    tw = [o for o in ch if o["tower"]]
    if tw:
        P = np.array([o["p0"] for o in tw])
        S_["tpiv"] = np.array((P[:, 0].mean(), P[:, 1].min() - 4.5, min(o["gz"] for o in tw)))
    # rubble mound (grows under the falling chunks)
    import bmesh
    rub = bpy.data.materials.get("ST_Stone") or C.mat("ST_WallRubble", (0.60, 0.57, 0.50), 0.9)
    bm = bmesh.new()
    for k in range(70):
        r = 20.0 * math.sqrt(rnd.random()); a = rnd.uniform(0, math.tau)
        res = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(rnd.uniform(3, 7), rnd.uniform(3, 7), rnd.uniform(2, 5) * (1.4 - r / 20)), verts=res["verts"])
        bmesh.ops.rotate(bm, verts=res["verts"], cent=(0, 0, 0), matrix=__import__("mathutils").Matrix.Rotation(a, 3, "Z"))
        bmesh.ops.translate(bm, vec=(r * math.cos(a), 1.3 * r * math.sin(a), 0.0), verts=res["verts"])
    mo = C.mesh_obj("S2V_Rubble", bm, [rub], c); mo.location = tuple(cw[:2]) + (C.G(cw[0], cw[1]),); mo.scale = (1, 1, 0.01)
    S_["rubble"] = mo; C.hide(mo, True)

def _collapse(t):
    on = t >= BEATS["impact"]
    for o in S_["church"]:
        C.hide(o, on)
    C.hide(S_["rubble"], t < BEATS["impact"] + 0.3)
    S_["rubble"].scale = (1, 1, max(0.01, C.ss(BEATS["impact"] + 0.3, BEATS["impact"] + 2.4, t)))
    from mathutils import Matrix, Euler
    a0, a1 = BEATS["tower"]
    th = (math.pi / 2 - 0.12) * min(1.0, max(0.0, (t - a0) / (a1 - a0)) ** 2)
    hit = max(0.0, t - a1)
    piv = S_.get("tpiv")
    R = Matrix.Rotation(th, 3, "X")
    for o in S_["chunks"]:
        ob = o["ob"]
        C.hide(ob, not on)
        if not on:
            continue
        if o["tower"]:
            q = np.array(R @ __import__("mathutils").Vector(o["p0"] - piv)) + piv
            if hit > 0:                                           # it breaks up as it hits the street
                q = q + np.array((0.0, -6.0, 0.0)) * min(hit, 0.6) + o["spin"] * min(hit, 0.6) * 2.0
                q[2] = max(o["gz"] + 2.0, q[2] - 20.0 * min(hit, 0.6) ** 2)
            ob.location = tuple(q); ob.rotation_euler = (th + (o["spin"][0] * min(hit, 0.6)), o["spin"][1] * min(hit, 0.6), 0.0)
            continue
        tau = t - o["t0"]
        if tau <= 0:
            ob.location = tuple(o["p0"]); ob.rotation_euler = (0, 0, 0); continue
        tt = min(tau, o["tl"])
        p = o["p0"] + o["v"] * tt + np.array((0, 0, -0.5 * o["g"] * tt * tt))
        ob.location = tuple(p); ob.rotation_euler = tuple(o["w"] * tt)

def _flame_mat():
    """flame card: UV gradient (wide at the base, a tip at the top) x 4D noise (W animated) -> alpha; colour ramp red -> orange
    -> yellow by the same value; emission over transparent."""
    m = bpy.data.materials.new("S2V_Flame"); m.use_nodes = True
    N, Ln = m.node_tree.nodes, m.node_tree.links
    for n in list(N):
        if n.type != "OUTPUT_MATERIAL":
            N.remove(n)
    uv = N.new("ShaderNodeUVMap"); uv.uv_map = "UVMap"
    sp = N.new("ShaderNodeSeparateXYZ"); Ln.new(uv.outputs["UV"], sp.inputs[0])
    # width profile: |u - 0.5| * 2 compared with (1 - v)^0.7
    du = N.new("ShaderNodeMath"); du.operation = "SUBTRACT"; du.inputs[1].default_value = 0.5; Ln.new(sp.outputs["X"], du.inputs[0])
    ab = N.new("ShaderNodeMath"); ab.operation = "ABSOLUTE"; Ln.new(du.outputs[0], ab.inputs[0])
    a2 = N.new("ShaderNodeMath"); a2.operation = "MULTIPLY"; a2.inputs[1].default_value = 2.0; Ln.new(ab.outputs[0], a2.inputs[0])
    iv = N.new("ShaderNodeMath"); iv.operation = "SUBTRACT"; iv.inputs[0].default_value = 1.0; Ln.new(sp.outputs["Y"], iv.inputs[1])
    pw = N.new("ShaderNodeMath"); pw.operation = "POWER"; pw.inputs[1].default_value = 0.7; Ln.new(iv.outputs[0], pw.inputs[0])
    sh = N.new("ShaderNodeMath"); sh.operation = "SUBTRACT"; Ln.new(pw.outputs[0], sh.inputs[0]); Ln.new(a2.outputs[0], sh.inputs[1])
    nz = N.new("ShaderNodeTexNoise"); nz.noise_dimensions = "4D"; nz.inputs["Scale"].default_value = 3.5; nz.inputs["Detail"].default_value = 3.0
    w = nz.inputs["W"]
    mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1.0, 0.45, 1.0); Ln.new(uv.outputs["UV"], mp.inputs["Vector"])
    Ln.new(mp.outputs["Vector"], nz.inputs["Vector"])
    nm = N.new("ShaderNodeMath"); nm.operation = "MULTIPLY_ADD"; nm.inputs[1].default_value = 0.9; nm.inputs[2].default_value = -0.35
    Ln.new(nz.outputs["Fac"], nm.inputs[0])
    tot = N.new("ShaderNodeMath"); tot.operation = "ADD"; tot.use_clamp = True; Ln.new(sh.outputs[0], tot.inputs[0]); Ln.new(nm.outputs[0], tot.inputs[1])
    al = N.new("ShaderNodeMath"); al.operation = "MULTIPLY"; al.inputs[1].default_value = 2.2; al.use_clamp = True; Ln.new(tot.outputs[0], al.inputs[0])
    ramp = N.new("ShaderNodeValToRGB"); E = ramp.color_ramp.elements
    E[0].position = 0.0; E[0].color = (0.45, 0.04, 0.01, 1); E[1].position = 0.75; E[1].color = (1.0, 0.85, 0.35, 1)
    e = E.new(0.35); e.color = (1.0, 0.32, 0.03, 1)
    Ln.new(tot.outputs[0], ramp.inputs["Fac"])
    em = N.new("ShaderNodeEmission"); em.inputs["Strength"].default_value = 9.0; Ln.new(ramp.outputs["Color"], em.inputs["Color"])
    tr = N.new("ShaderNodeBsdfTransparent"); mx = N.new("ShaderNodeMixShader")
    Ln.new(al.outputs[0], mx.inputs[0]); Ln.new(tr.outputs[0], mx.inputs[1]); Ln.new(em.outputs[0], mx.inputs[2])
    Ln.new(mx.outputs[0], N.get("Material Output").inputs["Surface"])
    for attr, val in (("surface_render_method", "BLENDED"), ("blend_method", "BLEND"), ("use_shadow", False)):
        try:
            setattr(m, attr, val)
        except Exception:
            pass
    return m, w

# ---------------------------------------------------------------- build / update
def build(site):
    global CAM
    CAM = camchan.CamPath(C.lift_keys(CAM_KEYS), v_in=SEAM_IN["vel"], v_out=(0.0, 0.0, 0.0))
    import flares, bmesh
    import attack_titan as AT
    from stohess import sset
    c = C.coll("S2V")
    S_["fem"] = C.Female("S2V_Female"); S_["fem"].rig.scale = tuple(v * TS for v in S_["fem"].rig.scale)   # the rig has its own base scale
    S_["eren"] = C.Eren("S2V_Attack")
    S_["face"] = sset.STATE.get("face")
    build_collapse(c)
    rnd = random.Random(11)
    dust = flares.PuffField("S2V_Dust", kind="dust", color=(0.70, 0.65, 0.57), alpha=0.4)
    te, pos, vel = [], [], []
    for k in range(40):                                          # paving bursts as Eren comes up in the square
        te.append(0.9 + 0.02 * k); pos.append(_W(-40 + rnd.uniform(-10, 10), -60 + rnd.uniform(-10, 10), 2 + 0.3 * k)); vel.append((0, 0, 6))
    for k in range(45):                                          # the impact + the collapse column (v16: halved)
        te.append(BEATS["impact"] + 0.06 * k); pos.append(_W(CH[0] + rnd.uniform(-20, 20), CH[1] + rnd.uniform(-26, 26), rnd.uniform(4, 30)))
        vel.append((rnd.uniform(-4, 4), rnd.uniform(-4, 4), rnd.uniform(2, 7)))
    for k in range(80):                                          # the cloud ROLLS OUT through the streets
        a = rnd.uniform(0, math.tau); t0 = BEATS["impact"] + 0.3 + rnd.uniform(0, 1.8)
        te.append(t0); pos.append(_W(CH[0] + 26 * math.cos(a), CH[1] + 30 * math.sin(a), 3.0))
        sp = rnd.uniform(14, 26); vel.append((sp * math.cos(a), sp * math.sin(a), 1.0))
    for k in range(30):                                          # the tower's impact line (south)
        u = rnd.random(); te.append(BEATS["tower"][1] + rnd.uniform(0, 0.4)); pos.append(_W(CH[0] + 22 + rnd.uniform(-6, 6), CH[1] - 20 - 60 * u, 3.0))
        vel.append((rnd.uniform(-6, 6), rnd.uniform(-6, 6), 4.0))
    dust.add_many(te[:40], pos[:40], vel[:40], r0=3.0, r1=9.0, life=1.8, rise=1.5, alpha=0.5)      # the square burst: short (it hid the frame)
    dust.add_many(te[40:], pos[40:], vel[40:], r0=4.0, r1=16.0, life=3.6, rise=1.2, alpha=0.4)
    te, pos, vel = [], [], []
    for tt in np.arange(0.0, 13.0, 0.2):                         # dust trails behind both titans (read from the sky)
        for fn in (fem_S, eren_S):
            if fn is eren_S and tt < 1.6:
                continue
            x, y = fn(float(tt)); te.append(float(tt)); pos.append(_W(x, y, 2.0)); vel.append((rnd.uniform(-2, 2), rnd.uniform(-2, 2), 4.0))
    dust.add_many(te, pos, vel, r0=3.0, r1=9.0, life=1.6, rise=2.0, alpha=0.4)
    dust.build(c); S_["dust"] = dust
    # houses burning along her run to the wall (v16): crossed flame cards, 3 layers each (red base, orange body, yellow core),
    # alpha shaped by a flame gradient x animated noise (flicker per frame), dark smoke columns; lit after the collapse
    fm, fw = _flame_mat()
    S_["fire_w"] = fw
    bm = bmesh.new(); rnd2 = random.Random(77); uvl = bm.loops.layers.uv.new("UVMap")
    smoke = flares.PuffField("S2V_FireSmoke", kind="smoke", color=(0.10, 0.09, 0.09), alpha=0.8)
    te, pos, vel = [], [], []
    S_["flame_parts"] = []
    for (fx_, fy_) in ((150.0, -110.0), (190.0, -160.0), (240.0, -120.0), (300.0, -175.0), (350.0, -125.0), (410.0, -170.0),
                       (455.0, -150.0), (520.0, -210.0), (40.0, -120.0), (110.0, -210.0), (260.0, -95.0), (380.0, -200.0)):
        wz = _W(fx_, fy_, 10.0)
        for q in range(3):
            cx_, cy_ = wz[0] + rnd2.uniform(-5, 5), wz[1] + rnd2.uniform(-5, 5)
            h = rnd2.uniform(10.0, 18.0); wdt = h * 0.55
            for ang in (0.0, math.pi / 2, math.pi / 4):
                ca, sa = math.cos(ang), math.sin(ang)
                vs = [bm.verts.new((cx_ - ca * wdt / 2, cy_ - sa * wdt / 2, wz[2])), bm.verts.new((cx_ + ca * wdt / 2, cy_ + sa * wdt / 2, wz[2])),
                      bm.verts.new((cx_ + ca * wdt / 2, cy_ + sa * wdt / 2, wz[2] + h)), bm.verts.new((cx_ - ca * wdt / 2, cy_ - sa * wdt / 2, wz[2] + h))]
                f = bm.faces.new(vs)
                for lp, uv in zip(f.loops, ((0, 0), (1, 0), (1, 1), (0, 1))):
                    lp[uvl].uv = uv
        for tt in np.arange(5.6, DUR, 0.25):
            te.append(float(tt)); pos.append((wz[0], wz[1], wz[2] + 14.0)); vel.append((rnd2.uniform(1.0, 2.5), 0.5, 10.0))
    S_["flames"] = C.mesh_obj("S2V_Flames", bm, [fm], c); S_["flames"].visible_shadow = False
    smoke.add_many(te, pos, vel, r0=5.0, r1=20.0, life=5.0, rise=5.0, alpha=0.8)
    smoke.build(c); S_["firesmoke"] = smoke
    steam = flares.PuffField("S2V_Steam", kind="steam", alpha=0.75)
    te, pos, vel = [], [], []
    for k in range(120):
        tt = rnd.uniform(13.3, 17.0); base = (KX, KY) if k % 2 else _off(SL.CRYSTAL, 9.0)
        te.append(tt); pos.append(_W(base[0] + rnd.uniform(-8, 8), base[1] + rnd.uniform(-8, 8), rnd.uniform(2, 14))); vel.append((0, 0, rnd.uniform(2, 4)))
    steam.add_many(te, pos, vel, r0=3.0, r1=12.0, life=3.5, rise=1.5)
    steam.build(c); S_["steam"] = steam

def update(t):
    import attack_titan as AT
    from forest import tableau as TB
    lu = (t - BEATS["lightning"][0]) / (BEATS["lightning"][1] - BEATS["lightning"][0])
    if lu > -0.01:
        w = S(-40.0, -60.0); fx = AT.shift_fx(w[0], w[1], min(1.0, max(0.0, lu)), seed=43, scale=TS)
        if lu > 1.0:                                             # the steam dome thins away (it hid the square as a white blob)
            fx["dome_d"].default_value *= 1.0 - C.ss(1.0, 1.5, lu); fx["dome"].hide_render = lu > 1.5
    fem = S_["fem"]; fem.show(True)
    pose, yaw, pitch, dz = fem_state(t, TB)
    fem.pose(pose)
    x, y = fem_S(t); w = _W(x, y, dz + fem_z(t))
    fem.place(w[0], w[1], w[2], yaw, pitch=pitch)
    fem.hardening(C.ss(BEATS["climb"][0], BEATS["climb"][0] + 0.4, t) * (1 - C.ss(BEATS["fall"][0] - 0.2, BEATS["fall"][0], t)))
    er = S_["eren"]
    show_e = t >= BEATS["rise"][0]
    er.show(show_e)
    if show_e:
        er.pose(eren_state(t, er, TB))
        ex, ey = eren_S(t)
        if t >= BEATS["mount"]:                                  # astride her at the wall foot
            ew = _W(KX + 2.5 * TS * NX, KY + 2.5 * TS * NY, -1.8 * TS); er.place(ew[0], ew[1], ew[2], WALL_YAW); er.T.holder.scale = (TS, TS, TS)
        else:
            if t < 7.0 or t >= 11.3:
                tx, ty = fem_S(t)
            else:
                tx, ty = eren_S(t + 0.1)
            rise = C.ss(*BEATS["rise"], t)
            ew = _W(ex, ey, -23.0 * (1 - rise))
            er.place(ew[0], ew[1], ew[2], C.yaw_of(tx - ex, ty - ey + 1e-9)); er.T.holder.scale = (TS, TS, TS)
        er.T.burning(0.0)
        er.T.steam(0.6 * (1 - C.ss(*BEATS["rise"], t)) + 0.7 * C.ss(13.3, 14.5, t))
    _collapse(t)
    C.hide(S_["flames"], t < 5.6)
    S_["fire_w"].default_value = t * 2.2                         # flicker
    for o in (S_["face"] or []):
        o.hide_render = t < BEATS["face"]
    S_["dust"].update(t, wind=(2.0, 0.5)); S_["steam"].update(t, wind=(0.8, 0.4)); S_["firesmoke"].update(t, wind=(2.5, 0.6))

def light(t):
    LIGHT.apply(t)

def check():
    if bpy is not None and S_.get("fem") is not None:
        _debug_sizes()
    for t in (0.0, 1.6, 3.9, 4.15, 4.75, 6.9, 8.0, 9.6, 11.6, 12.3):
        fx, fy = fem_S(t); ex, ey = eren_S(t)
        print(f"[s2v15] t {t:5.2f} female S ({fx:5.0f} {fy:5.0f}) z {fem_z(t):4.1f}  eren S ({ex:5.0f} {ey:5.0f}) d {math.hypot(fx - ex, fy - ey):5.1f}")

def _debug_sizes(t=4.0):
    update(t); bpy.context.view_layer.update()
    for nm, objs in (("female", S_["fem"].objs), ("eren", S_["eren"].objs)):
        zs = []
        for o in objs:
            if o.type == "MESH" and not o.hide_render:
                dg = o.evaluated_get(bpy.context.evaluated_depsgraph_get())
                zs += [(dg.matrix_world @ v.co).z for v in dg.to_mesh().vertices]
        print(f"[s2v15] {nm} visible meshes z {min(zs) if zs else None} .. {max(zs) if zs else None}  n {len(zs)}", flush=True)
    print("[s2v15] fem rig scale", tuple(S_["fem"].rig.scale), "hidden", S_["fem"].rig.hide_render, "eren holder", tuple(S_["eren"].T.holder.scale), flush=True)
