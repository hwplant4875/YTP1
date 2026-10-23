"""Colossal Titan (Season 1 anime look) built on titans.make_titan("colossal").

make_colossal(name)  -> armature object (body mesh parented, rig scaled so the titan is 60 m tall)
colossal_steam(rig)  -> list of steam volume objects (bone-parented to the rig)
pose_wall_grip(rig, wall_top_z, wall_face_y, side="L") -> lean over a wall and grip its top (S1E1 shot)

What it adds on top of the generic MPFB titan:
  * proportions baked into the rest pose: broad shoulders, wide chest, narrow waist, long thick neck,
    smaller head, huge hands, long arms
  * bmesh face sculpt: long gaunt face, heavy brow, hollow cheeks / high cheekbones, flat nose (nasal
    cavity only), shrunken ears, lipless mouth, prominent chin, tall bald cranium
  * separate tooth geometry (full rows back to the molars) and deep-set lidless eyeballs, skinned to the rig
  * a per-vertex "cmask" attribute (R = pale fascia/tendon, G = muscle-fibre phase, B = cavity) driving
    one Principled BSDF material: red striated muscle with pale tendon plates laid out like the anime
    (white cranium, nose bridge, cheekbone and mouth bands; red eye rings, cheeks, chin, temples, neck;
    white sternum / abs / clavicle / knee / back-diamond tendons on the body)
All materials are Principled BSDF + procedural nodes + an Attribute node, so Eevee and Cycles both work.
"""
import bpy, bmesh, math, sys, os
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import titans

HEIGHT = 60.0

# ---------------------------------------------------------------- helpers
def _ss(a, b, x):
    if a == b:
        return 1.0 if x >= b else 0.0
    t = max(0.0, min(1.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)

def _cl(x, a=0.0, b=1.0):
    return max(a, min(b, x))

def _seg_dist2d(p, a, b):
    """Distance from 2D point p to segment ab (tuples)."""
    ax, ay = a; bx, by = b; px, py = p
    dx, dy = bx - ax, by - ay
    L = dx * dx + dy * dy
    t = 0.0 if L == 0 else _cl(((px - ax) * dx + (py - ay) * dy) / L)
    qx, qy = ax + t * dx, ay + t * dy
    return math.hypot(px - qx, py - qy), t

def _group_pts(body, names, thr=0.5):
    idx = {body.vertex_groups[n].index for n in names if n in body.vertex_groups}
    return [v.co.copy() for v in body.data.vertices if any(g.group in idx and g.weight > thr for g in v.groups)]

def _centroid(pts):
    c = Vector((0, 0, 0))
    for p in pts:
        c += p
    return c / max(1, len(pts))

# ---------------------------------------------------------------- 1. proportions (baked into rest pose)
SCALES = {
    "head": (0.76, 0.76, 0.76),
    "upperleg01.L": (1.35, 0.93, 1.3), "upperleg01.R": (1.35, 0.93, 1.3), "upperleg02.L": (1.3, 0.93, 1.25), "upperleg02.R": (1.3, 0.93, 1.25),
    "lowerleg01.L": (1.2, 0.93, 1.2), "lowerleg01.R": (1.2, 0.93, 1.2), "lowerleg02.L": (1.1, 0.93, 1.1), "lowerleg02.R": (1.1, 0.93, 1.1),
    "spine03": (1.05, 1.0, 1.0), "pelvis.L": (1.1, 1.0, 1.0), "pelvis.R": (1.1, 1.0, 1.0),
    "neck01": (1.42, 1.4, 1.3), "neck02": (1.38, 1.4, 1.25), "neck03": (1.25, 1.3, 1.15),
    "spine01": (1.16, 1.06, 1.05), "spine02": (1.08, 1.04, 1.0),
    "spine04": (0.9, 1.04, 0.95), "spine05": (0.92, 1.0, 0.95),
    "clavicle.L": (1.15, 1.45, 1.15), "clavicle.R": (1.15, 1.45, 1.15),
    "shoulder01.L": (1.15, 1.2, 1.15), "shoulder01.R": (1.15, 1.2, 1.15),
    "upperarm01.L": (1.25, 1.06, 1.25), "upperarm01.R": (1.25, 1.06, 1.25),
    "upperarm02.L": (1.22, 1.06, 1.22), "upperarm02.R": (1.22, 1.06, 1.22),
    "lowerarm01.L": (1.18, 1.06, 1.18), "lowerarm01.R": (1.18, 1.06, 1.18),
    "lowerarm02.L": (1.0, 1.06, 1.0), "lowerarm02.R": (1.0, 1.06, 1.0),
    "wrist.L": (1.35, 1.35, 1.35), "wrist.R": (1.35, 1.35, 1.35),
}
KEEP_INHERIT = ("head", "wrist.L", "wrist.R")

def _reshape(rig, body):
    P = rig.pose.bones
    for pb in P:
        pb.rotation_mode = "XYZ"; pb.rotation_euler = (0, 0, 0); pb.location = (0, 0, 0); pb.scale = (1, 1, 1)
    saved = {b.name: b.inherit_scale for b in rig.data.bones}
    for b in rig.data.bones:
        if b.parent and b.parent.name in SCALES and b.parent.name not in KEEP_INHERIT:
            b.inherit_scale = "NONE"
    for n, s in SCALES.items():
        if n in P:
            P[n].scale = s
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    ev = body.evaluated_get(dg); m = ev.to_mesh()
    co = [v.co.copy() for v in m.vertices]
    ev.to_mesh_clear()
    for v, c in zip(body.data.vertices, co):
        v.co = c
    vl = bpy.context.view_layer
    for o in vl.objects:
        o.select_set(False)
    vl.objects.active = rig; rig.select_set(True)
    bpy.ops.object.mode_set(mode="POSE")
    bpy.ops.pose.select_all(action="SELECT")
    bpy.ops.pose.armature_apply(selected=False)
    bpy.ops.object.mode_set(mode="OBJECT")
    for b in rig.data.bones:
        b.inherit_scale = saved.get(b.name, "FULL")
    for pb in P:
        pb.scale = (1, 1, 1); pb.rotation_euler = (0, 0, 0); pb.location = (0, 0, 0)

# ---------------------------------------------------------------- 2. face frame
class Face:
    """Normalised face coordinates: u = x/U, v = (z - eye_z)/U, w = (y - eye_y)/U (front is -y)."""
    def __init__(self, body):
        eL = _centroid(_group_pts(body, ["orbicularis03.L", "orbicularis04.L"]))
        eR = _centroid(_group_pts(body, ["orbicularis03.R", "orbicularis04.R"]))
        lips = _group_pts(body, ["lips"])
        self.mouth = _centroid(lips)
        self.eye = (eL + eR) / 2
        self.ex = abs(eL.x - eR.x) / 2
        self.U = self.eye.z - self.mouth.z
        self.eyeL, self.eyeR = eL, eR
    def uvw(self, p):
        U = self.U
        return p.x / U, (p.z - self.eye.z) / U, (p.y - self.eye.y) / U

def _headness(body, rig):
    names = {"head"} | {b.name for b in rig.data.bones["head"].children_recursive}
    idx = {body.vertex_groups[n].index for n in names if n in body.vertex_groups}
    out = []
    for v in body.data.vertices:
        out.append(_cl(sum(g.weight for g in v.groups if g.group in idx)))
    return out

# ---------------------------------------------------------------- 3. face sculpt
def _sculpt(body, rig):
    me = body.data
    F = Face(body)
    U = F.U
    hd = _headness(body, rig)
    me.calc_normals_split() if hasattr(me, "calc_normals_split") else None
    nrm = [v.normal.copy() for v in me.vertices]
    ears = {body.vertex_groups["ears"].index} if "ears" in body.vertex_groups else set()
    earpts = {1: [], -1: []}
    earw = []
    for v in me.vertices:
        w = max([g.weight for g in v.groups if g.group in ears] or [0.0])
        earw.append(w)
        if w > 0.5:
            earpts[1 if v.co.x > 0 else -1].append(v.co.copy())
    earc = {s: _centroid(p) for s, p in earpts.items() if p}
    lips_idx = body.vertex_groups["lips"].index if "lips" in body.vertex_groups else -1
    # trapezius: fill the neck-shoulder corner so the neck slopes into the shoulders
    zc = rig.data.bones["clavicle.L"].head_local.z
    zn = rig.data.bones["neck02"].head_local.z
    shx = rig.data.bones["shoulder01.L"].tail_local.x
    for i, v in enumerate(me.vertices):
        p = v.co; n = nrm[i]
        if hd[i] < 0.5 and zc - 0.02 < p.z < zn + 0.04 and n.z > -0.2 and p.y > -0.06:
            ax = abs(p.x)
            t = _cl(1 - abs(ax - 0.42 * shx) / (0.5 * shx))
            f = _ss(zn + 0.04, zc + 0.04, p.z) * _ss(zc - 0.02, zc + 0.02, p.z)
            v.co = p + n * (0.035 * t * t * f) + Vector((0, 0, 0.012 * t * f))
    for i, v in enumerate(me.vertices):
        h = hd[i]
        if h <= 0.001:
            continue
        p = v.co.copy(); n = nrm[i]
        u, vv, w = F.uvw(p)
        au = abs(u); sx = 1 if u >= 0 else -1
        front = _ss(0.05, 0.45, -n.y)
        d = Vector((0, 0, 0))
        # long lower face: stretch everything below the cheekbones downward
        d.z -= 0.42 * U * _ss(-0.2, -1.0, vv) + 0.80 * U * _ss(-1.0, -1.7, vv)
        # heavy brow ridge (front band just above the eyes)
        brow = math.exp(-((vv - 0.36) / 0.16) ** 2) * _ss(1.45, 0.9, au) * front
        d.y -= 0.22 * U * brow
        d.z -= 0.04 * U * brow
        # deep-set eyes: push the socket area back
        for ec in (F.eyeL, F.eyeR):
            r = math.hypot((p.x - ec.x) / U, (p.z - ec.z) / U)
            d.y += 0.10 * U * math.exp(-(r / 0.30) ** 2) * front
        # cheekbones out, cheeks hollow below them
        cb = math.exp(-((au - 0.95) / 0.30) ** 2 - ((vv + 0.30) / 0.16) ** 2)
        d += n * (0.07 * U * cb)
        hol = math.exp(-((au - 0.78) / 0.30) ** 2 - ((vv + 0.80) / 0.30) ** 2) * front
        d -= n * (0.11 * U * hol)
        # flatten the nose to a skull-like nasal area
        nose = _ss(0.42, 0.16, au) * _ss(0.15, -0.05, vv) * _ss(-0.95, -0.7, vv)
        if nose > 0 and w < -0.30:
            d.y += (-0.30 - w) * U * 0.5 * nose
        # lipless mouth: lips pulled back flat
        lw = max([g.weight for g in v.groups if g.group == lips_idx] or [0.0])
        d.y += 0.09 * U * lw
        # prognathic mouth: teeth and muzzle push forward (anime profile)
        muz = math.exp(-((vv + 1.05) / 0.45) ** 2) * _ss(0.95, 0.3, au) * front
        d.y -= 0.32 * U * muz
        # strong prominent chin and wide jaw
        chin = _ss(-1.15, -1.55, vv) * front * _ss(0.8, 0.2, au)
        d.y -= 0.07 * U * chin
        jaw = _ss(-0.7, -1.3, vv) * _ss(0.4, 0.9, au)
        d.x += sx * 0.11 * U * jaw
        # wide face: broad cheekbones and jaw (S1E1 front view)
        d.x += p.x * (0.12 + 0.30 * _ss(0.3, -0.4, vv) + 0.10 * _ss(-0.2, 0.6, vv))
        d.x += p.x * 0.16 * math.exp(-((vv + 0.55) / 0.40) ** 2)       # broad cheekbones
        # domed cranium: taper the top of the (rectangular) skull toward the vertical axis
        tp = _ss(0.35, 2.3, vv) ** 1.4
        d.x -= p.x * 0.38 * tp
        d.y -= (p.y - (F.eye.y + 0.9 * U)) * 0.30 * tp
        # tall bald cranium
        d.z += 0.06 * U * _ss(0.6, 1.9, vv)
        # shrink ears toward their root
        if earw[i] > 0.0 and sx in earc:
            c = earc[sx]
            root = Vector((c.x * 0.86, c.y, c.z))
            d += (root - p) * (0.38 * earw[i])
        v.co = p + d * h

# ---------------------------------------------------------------- 4. teeth + eyes (added to the body mesh)
def _add_parts(body, rig):
    me = body.data
    F = Face(body)
    U = F.U
    bvh = BVHTree.FromPolygons([v.co for v in me.vertices], [tuple(p.vertices) for p in me.polygons])
    bm = bmesh.new(); bm.from_mesh(me)
    dl = bm.verts.layers.deform.verify()
    gi = lambda n: body.vertex_groups[n].index if n in body.vertex_groups else body.vertex_groups.new(name=n).index
    g_head, g_jaw = gi("head"), gi("jaw")
    me.materials.append(_mat_teeth("Colossal_teeth")); ti = len(me.materials) - 1
    me.materials.append(_mat_eye("Colossal_eye")); ei = len(me.materials) - 1
    mz = F.mouth.z - 0.0 * U

    yc = F.eye.y + 0.9 * U
    def surface(a, z):
        d = Vector((math.sin(a), -math.cos(a), 0))
        hit = bvh.ray_cast(Vector((0, yc, z)) + d * 4 * U, -d, 6 * U)
        return hit[0], hit[1]

    def box(center, axes, half, mat, grp):
        r = bmesh.ops.create_cube(bm, size=1.0)
        vs = r["verts"]
        M = Matrix((axes[0] * half[0] * 2, axes[1] * half[1] * 2, axes[2] * half[2] * 2)).transposed()
        for vt in vs:
            vt.co = center + M @ vt.co
            vt[dl][grp] = 1.0
        fs = list({f for vt in vs for f in vt.link_faces})
        for f in fs:
            f.material_index = mat; f.smooth = True
        edges = list({e for vt in vs for e in vt.link_edges})
        res = bmesh.ops.bevel(bm, geom=edges, offset=min(half) * 0.55, segments=2, affect="EDGES", profile=0.5)
        for f in res["faces"]:
            f.material_index = mat; f.smooth = True
        for vt in res["verts"]:
            vt[dl][grp] = 1.0
        return vs

    # teeth: rows that follow the face surface along the mouth line, back to the molars
    th = 0.13 * U          # tooth height
    eps = [p for p in _group_pts(body, ["ears"]) if p.x > 0]
    ec_ = _centroid(eps) if eps else Vector((2 * F.ex, yc, 0))
    a_end = math.atan2(abs(ec_.x), -(ec_.y - yc)) - 0.30
    for sgn in (1, -1):
        a = 0.0; k = 0
        while True:
            wdt = (0.068 + 0.004 * min(k, 8)) * U
            loc0, _ = surface(0.0 if k == 0 else a, mz)
            r_loc = (Vector((loc0.x, loc0.y - yc, 0)).length if loc0 else 1.1 * U)
            ac = a + (wdt / 2) / r_loc
            if ac > a_end:
                break
            curve = 0.10 * U * (ac / a_end) ** 2           # bite line rises slightly toward the back
            for row, grp in ((1, g_head), (-1, g_jaw)):
                hgt = th * (1.0 - 0.25 * ac / a_end)
                zc = mz + curve + row * (hgt / 2 + 0.008 * U)
                loc, nr = surface(sgn * ac, zc)
                if loc is None:
                    continue
                nr = Vector((nr.x, nr.y, 0)).normalized() if abs(nr.z) < 0.95 else Vector((0, -1, 0))
                tang = Vector((0, 0, 1)).cross(nr).normalized()
                depth = 0.07 * U
                c = loc - nr * (depth * 0.72)
                box(Vector(c), (tang, -nr, Vector((0, 0, 1))), (wdt * 0.45, depth, hgt / 2), ti, grp)
            a += wdt * 1.03 / r_loc; k += 1
        print("TEETH per side", k)
    # eyeballs: small, deep in the sockets, no lids
    eye_pts = []
    for ec, gname in ((F.eyeL, "head"), (F.eyeR, "head")):
        r = 0.105 * U
        c = Vector((ec.x * 1.0, ec.y + 0.17 * U, ec.z - 0.01 * U))
        res = bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=10, radius=r)
        for vt in res["verts"]:
            eye_pts.append((vt.co.copy().normalized(), c))
            vt.co = vt.co + c
            vt[dl][gi(gname)] = 1.0
        for f in {f for vt in res["verts"] for f in vt.link_faces}:
            f.material_index = ei; f.smooth = True
    bm.to_mesh(me); bm.free()
    body["eye_start"] = len(me.vertices) - len(eye_pts)
    return F

# ---------------------------------------------------------------- 5. mask + fibre attribute
def _paint(body, rig):
    me = body.data
    F = Face(body)
    U = F.U
    hd = _headness(body, rig)
    B = {b.name: b for b in rig.data.bones}
    hl = lambda n: B[n].head_local.copy()
    tl = lambda n: B[n].tail_local.copy()
    z_notch = hl("neck01").z
    z_xiph = hl("spine02").z + 0.25 * (hl("spine01").z - hl("spine02").z)
    z_navel = hl("spine04").z
    z_pelv = hl("spine05").z
    sh = {s: tl(f"shoulder01.{s}") for s in "LR"}
    # neck geometry for the SCM strap
    earc = {}
    for s, sg in (("L", 1), ("R", -1)):
        pts = [p for p in _group_pts(body, ["ears"]) if p.x * sg > 0]
        earc[sg] = _centroid(pts) if pts else Vector((sg * 2 * F.ex, F.eye.y + 0.6 * U, F.eye.z - 0.4 * U))
    ny = [v.co.y for v in me.vertices if abs(v.co.x) < 0.01 and abs(v.co.z - z_notch) < 0.01]
    notch = Vector((0, min(ny) if ny else hl("neck01").y - 0.05, z_notch))
    # per-bone radius for fibre phase
    gname = {g.index: g.name for g in body.vertex_groups}
    dom = []
    for v in me.vertices:
        best, bw = None, 0.0
        for g in v.groups:
            n = gname[g.group]
            if n in B and g.weight > bw:
                best, bw = n, g.weight
        dom.append(best)
    rad = {}
    for v, n in zip(me.vertices, dom):
        if n:
            loc = B[n].matrix_local.inverted() @ v.co
            r = math.hypot(loc.x, loc.z)
            a = rad.setdefault(n, [0.0, 0]); a[0] += r; a[1] += 1
    rad = {k: s / max(1, c) for k, (s, c) in rad.items()}
    yc = F.eye.y + 0.9 * U
    a_eye = math.atan2(F.ex, -(F.eye.y - yc))
    a_ear = math.atan2(abs(earc[1].x), -(earc[1].y - yc))
    hdv = _headness(body, rig)
    v_chin = min([(v.co.z - F.eye.z) / U for i, v in enumerate(me.vertices)
                  if i < len(hdv) and hdv[i] > 0.9 and v.normal.y < -0.4 and abs(v.co.x) < 0.3 * U] or [-1.7])
    print("FACE a_eye %.2f a_ear %.2f U %.4f v_chin %.2f" % (a_eye, a_ear, U, v_chin))
    TORSO = ("spine", "breast", "clavicle", "neck", "pelvis", "root")
    PER_FACE = 0.0034   # fibre period on the face (body-local units)
    PER_BODY = 0.008   # fibre period on the body
    nrm = [v.normal.copy() for v in me.vertices]
    out = []
    for i, v in enumerate(me.vertices):
        p = v.co; n = nrm[i]
        x, y, z = p
        ax = abs(x)
        white = 0.0; cav = 0.0; phase = 0.0
        # ---------------- body (fibres follow the dominant bone)
        bn = dom[i]
        if bn and not bn.startswith(TORSO):
            loc = B[bn].matrix_local.inverted() @ p
            phase = math.atan2(loc.x, -loc.z) * rad.get(bn, 0.02) / PER_BODY
        else:
            # torso and neck: near-vertical fibres, continuous around the trunk
            phase = math.atan2(x, -(y - 0.0)) * 0.13 / PER_BODY
        front = n.y < -0.15
        back = n.y > 0.15
        if front and y < 0.05:
            # sternum + manubrium star
            d, t = _seg_dist2d((x, z), (0, z_notch - 0.005), (0, z_xiph))
            white = max(white, _ss(0.011, 0.005, d))
            white = max(white, _ss(0.02, 0.008, math.hypot(x, (z - (z_notch - 0.03)) * 1.6)) * 0.95)
            for s in "LR":
                c = sh[s]
                d, t = _seg_dist2d((x, z), (0, z_notch - 0.01), (c.x * 0.66, c.z + 0.016))
                white = max(white, _ss(0.013, 0.005, d))
            # costal arch + linea alba + tendinous intersections (6-pack) + inguinal V
            for sg in (1, -1):
                d, t = _seg_dist2d((x, z), (0, z_xiph), (sg * 0.125, z_navel + 0.02))
                white = max(white, _ss(0.010, 0.004, d))
                d, t = _seg_dist2d((x, z), (sg * 0.11, z_navel + 0.01), (sg * 0.03, z_pelv - 0.06))
                white = max(white, _ss(0.015, 0.006, d))
            if z_pelv - 0.05 < z < z_xiph:
                white = max(white, _ss(0.010, 0.004, ax))
                if ax < 0.10:
                    za, zb = z_xiph, z_pelv - 0.02
                    for k in (1, 2, 3):
                        zz = za + (zb - za) * k / 4.2
                        white = max(white, _ss(0.009, 0.003, abs(z - zz)))
            # knees and shins
            for s in "LR":
                k0 = hl(f"lowerleg01.{s}"); k1 = tl(f"lowerleg02.{s}")
                d, t = _seg_dist2d((x, z), (k0.x, k0.z + 0.03), (k1.x, k1.z + 0.03))
                white = max(white, _ss(0.026 - 0.012 * t, 0.012 - 0.006 * t, d))
        if back and y > -0.02:
            # white diamond between the shoulder blades
            zc = hl("spine01").z + 0.02
            dd = ax / 0.075 + abs(z - zc) / 0.13
            white = max(white, _ss(1.0, 0.8, dd))
            # spine line
            if hl("spine05").z < z < zc:
                white = max(white, _ss(0.015, 0.006, ax) * 0.9)
        # IT band (outer thigh)
        for s, sg in (("L", 1), ("R", -1)):
            a = hl(f"upperleg01.{s}"); b2 = hl(f"lowerleg01.{s}")
            if n.x * sg > 0.55 and b2.z < z < a.z - 0.05:
                white = max(white, _ss(0.02, 0.008, abs(y - (a.y + b2.y) / 2 - 0.005)))
        # ankles (bands) and tops of the feet
        for s in "LR":
            c = tl(f"lowerleg02.{s}")
            if abs(z - c.z) < 0.03 and math.hypot(x - c.x, y - c.y) < 0.08:
                white = max(white, _ss(0.03, 0.015, abs(z - c.z)))
            if dom[i] == f"foot.{s}" and n.z > 0.55:
                white = max(white, 0.9 * _ss(0.6, 0.85, n.z))
            # outer forearm strip (top/outer side in the A-pose rest)
            if dom[i] and dom[i].startswith("lowerarm") and dom[i].endswith(s):
                sg = 1 if s == "L" else -1
                o = Vector((sg * 0.55, 0.0, 0.83)).normalized()
                white = max(white, _ss(0.86, 0.95, n.dot(o)))
            # finger tendons on the back of the hand
            if dom[i] and (dom[i].startswith("metacarpal") or dom[i].startswith("finger")) and dom[i].endswith(s):
                loc = B[dom[i]].matrix_local.inverted() @ p
                a = math.atan2(loc.x, loc.z)
                white = max(white, 0.85 * _ss(0.35, 0.15, abs(a)))
        # wrists + elbows
        for s in "LR":
            for bnm, rr in (("wrist", 0.022), ("lowerarm01", 0.03)):
                c = hl(f"{bnm}.{s}")
                if (p - c).length < rr and (bnm == "wrist" or n.y > 0.2):
                    white = max(white, 0.9 * _ss(rr, rr * 0.5, (p - c).length))
        # neck: pale SCM strap from behind the ear to the sternal notch
        if z > z_notch - 0.03 and z < F.mouth.z:
            sg = 1 if x > 0 else -1
            m0 = earc[sg] + Vector((0, 0.15 * U, -0.55 * U)); m1 = Vector((sg * 0.012, notch.y, z_notch))
            seg = m1 - m0; t = _cl((p - m0).dot(seg) / seg.length_squared)
            d = (p - (m0 + seg * t)).length
            white = max(white, _ss(0.22 * U, 0.1 * U, d) * _ss(-0.2, 0.2, abs(n.x)))
        # ---------------- head / face
        h = hd[i]
        if h > 0.01:
            u, vv, w = F.uvw(p)
            au = abs(u); sx = 1 if u >= 0 else -1
            fr = -n.y
            red = 0.0
            ue = F.ex / U
            A = math.atan2(abs(x), -(y - yc))          # unfolded angle around the head (0 = front centre)
            ae = a_eye
            # red under-eye / orbital patch (below and outside the eye; the upper lid area is dark)
            de = ((A - ae - 0.06) / 0.36) ** 2 + ((vv + 0.36) / 0.56) ** 2
            ring = _cl((1 - de) * 3)
            # masseter / cheek: from the zygomatic band down to the jaw band, nasolabial band to the ear
            ct, cb = -0.56, (v_chin + 0.16) + (-0.95 - (v_chin + 0.16)) * _cl((A - 0.55) / max(0.1, a_ear - 0.55)) ** 1.5
            cf, cbk = 0.40, a_ear - 0.22
            cheek = _cl(min(vv - cb, ct - vv, A - cf, cbk - A) * 9)
            # chin (mentalis) below the lower-lip band
            c_top, c_bot = -1.18, v_chin + 0.15
            dch = (A / 0.62) ** 2 + ((vv - (c_top + c_bot) / 2) / max(0.1, (c_top - c_bot) / 2)) ** 2
            chin = _cl((1 - dch) * 3)
            # temporalis: tall patch on the upper side of the skull, seen at the forehead edges from the front
            dt = ((A - (a_eye + 0.66)) / 0.46) ** 2 + ((vv - 0.72) / 0.70) ** 2
            temple = _cl((1 - dt) * 3)
            db = ((A - 2.55) / 0.35) ** 2 + ((vv - 0.75) / 0.45) ** 2
            temple = max(temple, _cl((1 - db) * 3))
            # gums: red strips just above the upper and below the lower teeth
            gum = 0.0
            if A < a_ear - 0.3:
                gum = _ss(0.06, 0.02, abs(vv - (-1.0 + 0.27)))
            # neck below the jaw band is muscle again
            neck = _ss(0.0, 0.06, (cb - 0.13) - vv)
            red = max(ring, cheek, chin, temple, gum, neck)
            hw = _cl(1 - red)
            # zygomatic band: pale strip along the cheekbone between the under-eye mass and the cheek block
            if A > 0.32:
                zb = _ss(0.055, 0.03, abs(vv - (-0.60 - 0.22 * (A - 0.45)))) * _ss(0.32, 0.42, A)
                hw = max(hw, zb)
            # cavities: dark eye pits (deeper above the eye), nostrils, bite line
            for ec in (F.eyeL, F.eyeR):
                r = math.hypot((x - ec.x) / U / 1.25, (z - ec.z - 0.06 * U) / U)
                cav = max(cav, _ss(0.24, 0.15, r) * _ss(-0.2, 0.3, fr))
            if fr > 0.2:
                cav = max(cav, 0.6 * _ss(0.035, 0.01, abs(u)) * _ss(0.25, 0.4, vv) * _ss(1.0, 0.7, vv))
                rs = math.hypot(u, vv - 0.32)
                if rs < 0.3:
                    spk = 0.5 + 0.5 * math.cos(9 * math.atan2(vv - 0.32, u))
                    cav = max(cav, 0.8 * _ss(0.3, 0.08, rs) * _ss(0.55, 0.9, spk))
            for sg in (1, -1):
                nas = ((u - sg * 0.09) / 0.07) ** 2 + ((vv + 0.66) / 0.05) ** 2
                cav = max(cav, _ss(1.0, 0.4, nas) * 0.9 * _ss(0, 0.3, fr))
            # fibre phase on the face
            if chin >= max(cheek, temple):
                fph = x / PER_FACE
            elif temple >= max(cheek, chin):
                ang = math.atan2(vv + 0.3, (A - a_eye - 0.62) * 1.2)
                fph = ang * 70 / (2 * math.pi)
            else:
                fph = math.copysign(A, x) * 1.1 * U / PER_FACE
            phase = fph if h > 0.25 else phase
            white = white * (1 - h) + hw * h
            cav *= h
        if i >= body.get("eye_start", 10 ** 9):
            ce = F.eyeL if x > 0 else F.eyeR
            dn = (p - Vector((ce.x, ce.y + 0.17 * U, ce.z - 0.01 * U))).normalized()
            hd[i] = 1.0
            white, phase, cav = 0.0, (1.0 if dn.dot(Vector((-0.12 * (1 if x > 0 else -1), -1, 0.05)).normalized()) > 0.9 else 0.0), 0.0
        out.append((white, phase, cav, hd[i]))
    at = me.color_attributes.get("cmask") or me.color_attributes.new("cmask", "FLOAT_COLOR", "POINT")
    for i, (a, b, c, h) in enumerate(out):
        at.data[i].color = (a, (b % 1000.0) + 1.0, c, h)     # keep the fibre phase positive

# ---------------------------------------------------------------- 6. materials
def _mat_body(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; N = nt.nodes; L = nt.links; b = N["Principled BSDF"]
    at = N.new("ShaderNodeAttribute"); at.attribute_name = "cmask"; at.attribute_type = "GEOMETRY"
    sep = N.new("ShaderNodeSeparateColor"); L.new(at.outputs["Color"], sep.inputs[0])
    tc = N.new("ShaderNodeAttribute"); tc.attribute_name = "crest"; tc.attribute_type = "GEOMETRY"   # rest position
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 30; nz.inputs["Detail"].default_value = 4
    L.new(tc.outputs["Vector"], nz.inputs["Vector"])
    nz2 = N.new("ShaderNodeTexNoise"); nz2.inputs["Scale"].default_value = 220; nz2.inputs["Detail"].default_value = 2
    L.new(tc.outputs["Vector"], nz2.inputs["Vector"])
    def math_(op, a, bb=None, v=None):
        n = N.new("ShaderNodeMath"); n.operation = op
        for k, x in enumerate((a, bb)):
            if x is None:
                continue
            if isinstance(x, (int, float)):
                n.inputs[k].default_value = x
            else:
                L.new(x, n.inputs[k])
        return n.outputs[0]
    # stripes = 0.5 + 0.5 sin(2pi*phase + jitter)
    ph = math_("MULTIPLY", sep.outputs["Green"], 2 * math.pi)
    jit = math_("MULTIPLY", math_("SUBTRACT", nz.outputs["Fac"], 0.5), 4.0)
    s = math_("SINE", math_("ADD", ph, jit))
    fib0 = math_("ADD", math_("MULTIPLY", s, 0.5), 0.5)
    # body: softer streaks (0.5..1), face: full-contrast fibre lines
    fbody = math_("ADD", math_("MULTIPLY", fib0, 0.45), 0.35)
    fmix = N.new("ShaderNodeMix"); fmix.data_type = "FLOAT"
    L.new(at.outputs["Alpha"], fmix.inputs["Factor"]); L.new(fbody, fmix.inputs["A"]); L.new(fib0, fmix.inputs["B"])
    fib = fmix.outputs["Result"]
    rp = N.new("ShaderNodeValToRGB"); e = rp.color_ramp.elements
    e[0].position, e[0].color = 0.0, (0.112, 0.010, 0.007, 1)
    e.new(0.16).color = (0.478, 0.051, 0.025, 1)
    e.new(0.75).color = (0.56, 0.075, 0.04, 1)
    e[-1].position, e[-1].color = 1.0, (0.80, 0.22, 0.13, 1)
    L.new(fib, rp.inputs["Fac"])
    # pale tendon / fascia with a noisy crisp edge
    wn = N.new("ShaderNodeTexNoise"); wn.inputs["Scale"].default_value = 30; wn.inputs["Detail"].default_value = 4
    L.new(tc.outputs["Vector"], wn.inputs["Vector"])
    wj = math_("ADD", sep.outputs["Red"], math_("MULTIPLY", math_("SUBTRACT", wn.outputs["Fac"], 0.5), 0.08))
    wm = N.new("ShaderNodeMapRange"); wm.inputs["From Min"].default_value = 0.46; wm.inputs["From Max"].default_value = 0.54
    L.new(wj, wm.inputs["Value"]); W = wm.outputs["Result"]
    wc = N.new("ShaderNodeValToRGB"); e = wc.color_ramp.elements
    e[0].position, e[0].color = 0.25, (0.56, 0.43, 0.33, 1)
    e[1].position, e[1].color = 0.6, (0.716, 0.565, 0.445, 1)
    L.new(nz2.outputs["Fac"], wc.inputs["Fac"])
    mx = N.new("ShaderNodeMix"); mx.data_type = "RGBA"
    L.new(W, mx.inputs["Factor"]); L.new(rp.outputs["Color"], mx.inputs["A"]); L.new(wc.outputs["Color"], mx.inputs["B"])
    cm = N.new("ShaderNodeMapRange"); cm.inputs["From Min"].default_value = 0.2; cm.inputs["From Max"].default_value = 0.7
    L.new(sep.outputs["Blue"], cm.inputs["Value"])
    mc = N.new("ShaderNodeMix"); mc.data_type = "RGBA"; mc.inputs["B"].default_value = (0.035, 0.016, 0.013, 1)
    L.new(cm.outputs["Result"], mc.inputs["Factor"]); L.new(mx.outputs["Result"], mc.inputs["A"])
    L.new(mc.outputs["Result"], b.inputs["Base Color"])
    ro = N.new("ShaderNodeMapRange"); ro.inputs["To Min"].default_value = 0.32; ro.inputs["To Max"].default_value = 0.6
    L.new(W, ro.inputs["Value"]); L.new(ro.outputs["Result"], b.inputs["Roughness"])
    cw = N.new("ShaderNodeMapRange"); cw.inputs["To Min"].default_value = 0.5; cw.inputs["To Max"].default_value = 0.0
    L.new(W, cw.inputs["Value"]); L.new(cw.outputs["Result"], b.inputs["Coat Weight"])
    b.inputs["Coat Roughness"].default_value = 0.18
    b.inputs["Subsurface Weight"].default_value = 0.08; b.inputs["Subsurface Radius"].default_value = (1, 0.2, 0.1)
    # bump: fibre grooves on muscle, faint pores on fascia
    inv = math_("SUBTRACT", 1.0, W)
    hgt = math_("ADD", math_("MULTIPLY", fib, inv), math_("MULTIPLY", W, math_("MULTIPLY", nz2.outputs["Fac"], 0.3)))
    hgt = math_("ADD", hgt, math_("MULTIPLY", W, 0.35))     # fascia plates sit slightly proud
    bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.45; bp.inputs["Distance"].default_value = 0.02
    L.new(hgt, bp.inputs["Height"]); L.new(bp.outputs["Normal"], b.inputs["Normal"]); L.new(bp.outputs["Normal"], b.inputs["Coat Normal"])
    return m

def _mat_teeth(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (0.761, 0.672, 0.479, 1); b.inputs["Roughness"].default_value = 0.3
    b.inputs["Coat Weight"].default_value = 0.3
    return m

def _mat_eye(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; N = nt.nodes; L = nt.links; b = N["Principled BSDF"]
    at = N.new("ShaderNodeAttribute"); at.attribute_name = "cmask"; at.attribute_type = "GEOMETRY"
    sp = N.new("ShaderNodeSeparateColor"); L.new(at.outputs["Color"], sp.inputs[0])
    mr = N.new("ShaderNodeMapRange"); mr.inputs["From Min"].default_value = 0.45; mr.inputs["From Max"].default_value = 0.55
    L.new(sp.outputs["Green"], mr.inputs["Value"])
    mx = N.new("ShaderNodeMix"); mx.data_type = "RGBA"
    mx.inputs["A"].default_value = (0.40, 0.36, 0.28, 1); mx.inputs["B"].default_value = (0.156, 0.144, 0.098, 1)
    L.new(mr.outputs["Result"], mx.inputs["Factor"]); L.new(mx.outputs["Result"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.15
    return m

# ---------------------------------------------------------------- public API
def make_colossal(name="Colossal"):
    rig = titans.make_titan("colossal", name=name, macro=dict(muscle=1.0, weight=0.45, proportions=1.0))
    body = next(c for c in rig.children if c.type == "MESH")
    s0 = rig.scale.x
    rig.scale = (1, 1, 1)
    _reshape(rig, body)
    _sculpt(body, rig)
    me = body.data
    me.materials.clear()
    me.materials.append(_mat_body(name + "_muscle"))
    for p in me.polygons:
        p.material_index = 0; p.use_smooth = True
    _add_parts(body, rig)
    me.update()
    _paint(body, rig)
    ra = me.attributes.get("crest") or me.attributes.new("crest", "FLOAT_VECTOR", "POINT")
    for i, v in enumerate(me.vertices):
        ra.data[i].vector = v.co
    sub = body.modifiers.new("subsurf", "SUBSURF"); sub.levels = 0; sub.render_levels = 1
    # scale to exactly HEIGHT
    top = max(v.co.z for v in me.vertices); bot = min(v.co.z for v in me.vertices)
    s = HEIGHT / (top - bot)
    rig.scale = (s, s, s)
    rig["colossal_unit"] = s
    stand_pose(rig)
    return rig

def stand_pose(rig):
    """Arms hanging straight at the sides (size-card pose)."""
    titans.relax_pose(rig, arm=0.70, back=-0.05)
    for s in "LR":
        rig.pose.bones[f"lowerarm01.{s}"].rotation_euler.x = 0.05

def _steam_obj(name, center, size, density=0.5, noise_scale=2.0, glow=0.0, seed=0.0):
    """Billowy steam volume: lumpy cumulus density (noise + falloff), warm glow at the bottom.
    Principled Volume + procedural noise only (Eevee and Cycles)."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0); bm.to_mesh(me); bm.free()
    st = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(st)
    st.location = center; st.scale = size
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; N = nt.nodes; L = nt.links
    N.remove(N["Principled BSDF"])
    pv = N.new("ShaderNodeVolumePrincipled")
    pv.inputs["Color"].default_value = (0.95, 0.93, 0.90, 1)       # #E8E4DE (albedo kept high so backlit steam stays bright)
    pv.inputs["Emission Color"].default_value = (1.0, 0.96, 0.9, 1)
    pv.inputs["Emission Strength"].default_value = 0.06
    pv.inputs["Anisotropy"].default_value = 0.35
    tc = N.new("ShaderNodeTexCoord")
    mp = N.new("ShaderNodeMapping"); mp.inputs["Location"].default_value = (seed, seed * 0.7, 0)
    mp.inputs["Scale"].default_value = (size[0] / max(size), size[1] / max(size), size[2] / max(size))
    L.new(tc.outputs["Generated"], mp.inputs["Vector"])
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = noise_scale
    nz.inputs["Detail"].default_value = 7; nz.inputs["Roughness"].default_value = 0.55; nz.inputs["Distortion"].default_value = 0.4
    L.new(mp.outputs["Vector"], nz.inputs["Vector"])
    ctr = N.new("ShaderNodeVectorMath"); ctr.operation = "SUBTRACT"; ctr.inputs[1].default_value = (0.5, 0.5, 0.5)
    L.new(tc.outputs["Generated"], ctr.inputs[0])
    ln = N.new("ShaderNodeVectorMath"); ln.operation = "LENGTH"; L.new(ctr.outputs[0], ln.inputs[0])
    def mth(op, a, b):
        n = N.new("ShaderNodeMath"); n.operation = op
        for k, x in enumerate((a, b)):
            if isinstance(x, (int, float)):
                n.inputs[k].default_value = x
            else:
                L.new(x, n.inputs[k])
        return n.outputs[0]
    # cumulus: (noise - 0.5) * 5 + (0.42 - r) * 6, clamped, times density
    v = mth("ADD", mth("MULTIPLY", mth("SUBTRACT", nz.outputs["Fac"], 0.5), 8.0),
            mth("MULTIPLY", mth("SUBTRACT", 0.40, ln.outputs["Value"]), 7.0))
    v = mth("MULTIPLY", mth("MINIMUM", mth("MAXIMUM", v, 0.0), 1.0), density)
    L.new(v, pv.inputs["Density"])
    if glow > 0:
        sz = N.new("ShaderNodeSeparateXYZ"); L.new(tc.outputs["Generated"], sz.inputs[0])
        mr = N.new("ShaderNodeMapRange"); mr.inputs["From Min"].default_value = 0.55; mr.inputs["From Max"].default_value = 0.0
        mr.inputs["To Max"].default_value = glow
        L.new(sz.outputs["Z"], mr.inputs["Value"]); L.new(mr.outputs["Result"], pv.inputs["Emission Strength"])
        pv.inputs["Emission Color"].default_value = (1.0, 0.45, 0.18, 1)
    L.new(pv.outputs[0], N["Material Output"].inputs["Volume"])
    me.materials.append(m)
    return st

def colossal_steam(rig, density=1.5):
    """Steam clouds around the shoulders/neck and a tall plume rising from the body (bone-parented)."""
    s = rig.scale.x
    B = rig.data.bones
    def world(bn, off):
        return rig.matrix_world @ (B[bn].head_local + Vector(off))
    specs = [
        # name,           bone,      offset (rest units),     size (rest units),      density, noise, glow
        ("steam_shoulders", "spine01", (0, 0.07, 0.04), (0.80, 0.45, 0.36), density, 5.0, 1.2),
        ("steam_neck",      "neck02",  (0.04, 0.09, 0.06), (0.45, 0.35, 0.32), density * 0.8, 5.0, 0.6),
        ("steam_plume",     "neck03",  (0.10, 0.18, 0.55), (0.6, 0.6, 1.2), density * 0.9, 4.5, 0.0),
        ("steam_back",      "spine03", (0, 0.16, 0.0), (0.65, 0.35, 0.5), density * 0.7, 4.5, 1.0),
    ]
    out = []
    for nm, bn, off, size, d, ns, glow in specs:
        c = world(bn, off)
        st = _steam_obj(f"{rig.name}_{nm}", c, tuple(x * s for x in size), density=d, noise_scale=ns, glow=glow,
                        seed=len(out) * 3.1)
        bpy.context.view_layer.update()
        mw = st.matrix_world.copy()
        st.parent = rig; st.parent_type = "BONE"; st.parent_bone = bn
        bpy.context.view_layer.update()
        st.matrix_world = mw
        out.append(st)
    return out

def _solve(rig, bones, cost, iters=80):
    """Tiny coordinate-descent IK on (bone, axis) euler channels minimising cost()."""
    P = rig.pose.bones
    def err():
        bpy.context.view_layer.update()
        return cost()
    step = 0.3
    e = err()
    for _ in range(iters):
        improved = False
        for bn, ax in bones:
            for sgn in (1, -1):
                r = P[bn].rotation_euler; old = r[ax]
                r[ax] = old + sgn * step
                e2 = err()
                if e2 < e:
                    e = e2; improved = True; break
                r[ax] = old
        if not improved:
            step *= 0.5
            if step < 0.004:
                break
    return e

def pose_wall_grip(rig, wall_top_z, wall_face_y, side="L", lean=0.22, hand_x=None, grip_depth=4.0):
    """S1E1 pose: lean the head forward over a wall (top at wall_top_z, outer face at wall_face_y, world)
    and put one hand on the wall top with the fingers curled over the inner edge."""
    P = rig.pose.bones
    for pb in P:
        pb.rotation_mode = "XYZ"
    titans.relax_pose(rig, arm=0.9, back=-0.25)
    for bn, a in (("spine02", lean * 0.5), ("spine01", lean * 0.5), ("neck01", lean * 0.4), ("neck02", lean * 0.3)):
        P[bn].rotation_euler.x = a
    sg = 1 if side == "L" else -1
    s = rig.scale.x
    bpy.context.view_layer.update()
    sh = rig.matrix_world @ P[f"upperarm01.{side}"].head
    hx = hand_x if hand_x is not None else sh.x + sg * 6.0
    goal = Vector((hx, wall_face_y - grip_depth, wall_top_z + 2.0))
    W = rig.matrix_world
    def cost():
        wr = W @ P[f"wrist.{side}"].head; tip = W @ P[f"metacarpal3.{side}"].tail
        m2 = W @ P[f"metacarpal2.{side}"].tail; m4 = W @ P[f"metacarpal4.{side}"].tail
        hd = (tip - wr).normalized()
        palm = (m4 - m2).cross(hd).normalized() * (1 if side == "L" else -1)
        want = Vector((0, -1, -0.15)).normalized()
        return (tip - goal).length + 6.0 * (1 - hd.dot(want)) + 6.0 * (1 - palm.dot(Vector((0, 0, -1))))
    chans = [(f"upperarm01.{side}", 0), (f"upperarm01.{side}", 2), (f"upperarm01.{side}", 1),
             (f"lowerarm01.{side}", 0), (f"lowerarm01.{side}", 1), (f"wrist.{side}", 0), (f"wrist.{side}", 2), (f"wrist.{side}", 1)]
    e = _solve(rig, chans, cost, iters=120)
    for pb in P:
        if pb.name.startswith(("wrist", "lower", "upperarm")) and pb.name.endswith(side):
            pass
    print("GRIP cost", round(e, 2))
    # curl the fingers down over the edge
    for f in range(2, 6):
        for j, a in ((1, 0.5), (2, 0.8), (3, 0.6)):
            bn = f"finger{f}-{j}.{side}"
            if bn in P:
                P[bn].rotation_euler.x = a
    bpy.context.view_layer.update()
    return goal

