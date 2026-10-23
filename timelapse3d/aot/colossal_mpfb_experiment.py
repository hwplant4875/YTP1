# Round 5 experiment: Colossal on an MPFB2 base. Kept for reference; colossal.py (round 4) reads better in the thumbnail.
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
import os
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
    "head": (1.30, 1.10, 1.18),
    "upperleg01.L": (1.35, 0.93, 1.3), "upperleg01.R": (1.35, 0.93, 1.3), "upperleg02.L": (1.3, 0.93, 1.25), "upperleg02.R": (1.3, 0.93, 1.25),
    "lowerleg01.L": (1.2, 0.93, 1.2), "lowerleg01.R": (1.2, 0.93, 1.2), "lowerleg02.L": (1.1, 0.93, 1.1), "lowerleg02.R": (1.1, 0.93, 1.1),
    "spine03": (1.05, 1.0, 1.0), "pelvis.L": (1.1, 1.0, 1.0), "pelvis.R": (1.1, 1.0, 1.0),
    "neck01": (1.30, 1.6, 1.25), "neck02": (1.12, 1.6, 1.12), "neck03": (0.95, 1.5, 1.0),
    "spine01": (1.16, 1.06, 1.05), "spine02": (1.08, 1.04, 1.0),
    "spine04": (0.9, 1.04, 0.95), "spine05": (0.92, 1.0, 0.95),
    "clavicle.L": (1.15, 1.45, 1.15), "clavicle.R": (1.15, 1.45, 1.15),
    "shoulder01.L": (1.15, 1.2, 1.15), "shoulder01.R": (1.15, 1.2, 1.15),
    "upperarm01.L": (1.25, 1.06, 1.25), "upperarm01.R": (1.25, 1.06, 1.25),
    "upperarm02.L": (1.22, 1.06, 1.22), "upperarm02.R": (1.22, 1.06, 1.22),
    "lowerarm01.L": (1.18, 1.06, 1.18), "lowerarm01.R": (1.18, 1.06, 1.18),
    "lowerarm02.L": (1.0, 1.06, 1.0), "lowerarm02.R": (1.0, 1.06, 1.0),
    "wrist.L": (1.3, 1.65, 1.3), "wrist.R": (1.3, 1.65, 1.3),
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
# Round 5: MPFB face targets carry the anatomy; the procedural sculpt only adds what targets cannot.
SCULPT = dict(stretch=0.4, skull=0.7, brow=0.3, socket=0.6, cheek=0.5, hollow=1.0, mass=0.5, nose=1.0, muzzle=0.0,
              chin=0.3, jaw=0.0, narrow=0.0, widen=0.5, taper=0.5, occiput=0.0, temporalis=0.5, ear=1.0)
LRT = lambda t, w: [(t.format(s="l"), w), (t.format(s="r"), w)]
FACE_TARGETS = ([("head/head-fat-decr", 1.0), ("head/head-age-incr", 0.7), ("head/head-scale-vert-incr", 0.5),
                 ("head/head-oval", 0.6), ("forehead/forehead-temple-decr", 1.0), ("forehead/forehead-trans-backward", 0.3),
                 ("eyebrows/eyebrows-trans-forward", 1.0), ("eyebrows/eyebrows-trans-down", 0.6),
                 ("chin/chin-height-incr", 1.0), ("chin/chin-prominent-incr", 1.0), ("chin/chin-width-incr", 0.6),
                 ("chin/chin-bones-incr", 1.0), ("chin/chin-prognathism-incr", 0.4),
                 ("nose/nose-volume-decr", 1.0), ("nose/nose-scale-depth-decr", 1.0), ("nose/nose-point-width-decr", 1.0),
                 ("mouth/mouth-scale-horiz-incr", 1.0), ("mouth/mouth-upperlip-volume-decr", 1.0),
                 ("mouth/mouth-lowerlip-volume-decr", 1.0), ("mouth/mouth-scale-vert-incr", 0.5),
                 ("neck/measure-neck-height-incr", 1.0)]
                + LRT("cheek/{s}-cheek-bones-incr", 1.0) + LRT("cheek/{s}-cheek-volume-decr", 1.0)
                + LRT("cheek/{s}-cheek-inner-decr", 0.8) + LRT("eyes/{s}-eye-push1-in", 1.0) + LRT("eyes/{s}-eye-push2-in", 1.0))

def _make_base(name):
    """MPFB2 adult male: max muscle, min weight, gaunt long face (targets), default rig. Returns the rig."""
    md = titans.TS.get_default_macro_info_dict()
    md.update(dict(gender=1.0, muscle=1.0, weight=0.0, proportions=1.0))
    body = titans.HS.create_human(feet_on_ground=True, scale=0.1, macro_detail_dict=md)
    for t, w in FACE_TARGETS:
        pth = os.path.join(titans.TDIR, t + ".target.gz")
        if os.path.exists(pth):
            titans.TS.load_target(body, pth, weight=w)
        else:
            print("missing target", t)
    rig = titans.HS.add_builtin_rig(body, "default")
    titans.TS.bake_targets(body)
    titans._bake_and_clean(body)
    rig.name = name; body.name = name + "_body"
    body.data.materials.clear()      # materials are built afterwards (MPFB purges unused materials while building)
    return rig


def _sculpt(body, rig, K=None):
    K = dict(SCULPT, **(K or {}))
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
    zn = rig.data.bones["neck03"].head_local.z
    shx = rig.data.bones["shoulder01.L"].tail_local.x
    for i, v in enumerate(me.vertices):
        p = v.co; n = nrm[i]
        if hd[i] < 0.5 and zc - 0.02 < p.z < zn + 0.04 and n.z > -0.2 and p.y > -0.06:
            ax = abs(p.x)
            t = _cl(1 - abs(ax - 0.42 * shx) / (0.5 * shx))
            f = _ss(zn + 0.04, zc + 0.04, p.z) * _ss(zc - 0.02, zc + 0.02, p.z)
            v.co = p + n * (0.085 * t * t * f) + Vector((0, 0, 0.03 * t * f))
    # neck column: narrows just under the jaw; big sternocleidomastoid bands from behind the ear to the notch
    z_notch = rig.data.bones["neck01"].head_local.z
    z_top = rig.data.bones["head"].head_local.z
    ny = [v.co.y for v in me.vertices if abs(v.co.x) < 0.01 and abs(v.co.z - z_notch) < 0.01]
    notch_y = min(ny) if ny else rig.data.bones["neck01"].head_local.y - 0.05
    ax_y = rig.data.bones["neck03"].head_local.y
    for i, v in enumerate(me.vertices):
        if hd[i] > 0.6:
            continue
        p = v.co.copy(); n = nrm[i]
        if p.z < z_notch - 0.05 or p.z > z_top + 0.4 * U:
            continue
        k = (1 - hd[i]) * _ss(z_notch + 0.02, z_top - 0.1 * U, p.z) * _ss(z_top + 0.4 * U, z_top + 0.1 * U, p.z)
        p.x -= p.x * 0.16 * k
        p.y -= (p.y - ax_y) * 0.10 * k
        for sg in (1, -1):
            if sg not in earc:
                continue
            m0 = Vector((earc[sg].x * 0.8, earc[sg].y + 0.05 * U, earc[sg].z - 0.45 * U))
            m1 = Vector((sg * 0.012, notch_y + 0.01, z_notch))
            seg = m1 - m0; t = _cl((p - m0).dot(seg) / seg.length_squared)
            dd = (p - (m0 + seg * t)).length
            if p.x * sg > -0.005:
                p += n * (0.10 * U * math.exp(-(dd / (0.17 * U)) ** 2) * _ss(0.0, 0.15, t) * (1 - hd[i]))
        v.co = p
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
        d.z -= K['stretch'] * (0.50 * U * _ss(-0.2, -1.0, vv) + 0.85 * U * _ss(-1.0, -1.7, vv))
        # lower, smoother skull: compress everything above the brow
        d.z -= K['skull'] * 0.25 * U * max(0.0, vv - 0.40) / (1.0 + 0.3 * max(0.0, vv - 0.40))
        # heavy brow ridge (front band just above the eyes)
        brow = math.exp(-((vv - 0.36) / 0.16) ** 2) * _ss(1.45, 0.9, au) * front
        d.y -= K['brow'] * 0.34 * U * brow
        d.z -= K['brow'] * 0.04 * U * brow
        # deep-set eyes: push the socket area back
        for ec in (F.eyeL, F.eyeR):
            r = math.hypot((p.x - ec.x) / U, (p.z - ec.z) / U)
            d.y += K['socket'] * 0.26 * U * math.exp(-(r / 0.40) ** 2) * front
        # cheekbones out, cheeks hollow below them
        cb = math.exp(-((au - 0.95) / 0.32) ** 2 - ((vv + 0.38) / 0.20) ** 2)
        d += n * (K['cheek'] * 0.14 * U * cb)
        hol = math.exp(-((au - 0.78) / 0.30) ** 2 - ((vv + 0.80) / 0.30) ** 2) * front
        d -= n * (K['hollow'] * 0.05 * U * hol)
        # masseter: big bulging cheek bundle from the cheekbone down to the jaw angle
        mas = math.exp(-((au - 1.05) / 0.30) ** 2 - ((vv + 1.15) / 0.45) ** 2)
        d += n * (K['mass'] * 0.12 * U * mas)
        # flatten the nose to a skull-like nasal area
        nose = _ss(0.42, 0.16, au) * _ss(0.15, -0.05, vv) * _ss(-0.95, -0.7, vv)
        if nose > 0 and w < -0.30:
            d.y += (-0.30 - w) * U * 0.9 * nose * K['nose']
        # lipless mouth: lips pulled back flat
        lw = max([g.weight for g in v.groups if g.group == lips_idx] or [0.0])
        d.y += 0.09 * U * lw
        # prognathic mouth: teeth and muzzle push forward (anime profile)
        muz = math.exp(-((vv + 1.05) / 0.45) ** 2) * _ss(0.95, 0.3, au) * front
        d.y -= K['muzzle'] * 0.10 * U * muz
        # teeth sit inside the face: recess the mouth band so the cheek panels run into the gums
        d -= n * (0.03 * U * math.exp(-((vv + 0.98) / 0.32) ** 2) * _ss(1.25, 0.9, au) * front)
        # strong prominent chin and wide jaw
        chin = _ss(-1.15, -1.55, vv) * front * _ss(1.0, 0.3, au)
        d.y -= K['chin'] * 0.20 * U * chin
        jaw = _ss(-0.7, -1.3, vv) * _ss(0.4, 0.9, au)
        d.x += K['jaw'] * sx * 0.06 * U * jaw
        d.x -= K['narrow'] * p.x * 0.34 * _ss(-1.15, -2.1, vv)          # jaw narrows to the chin
        # wide face: broad cheekbones and jaw (S1E1 front view)
        d.x += K['widen'] * p.x * (0.10 + 0.14 * _ss(0.3, -0.4, vv))
        d.x += K['widen'] * p.x * 0.24 * math.exp(-((vv + 0.45) / 0.40) ** 2)       # broad cheekbones: widest point
        # domed cranium: taper the top of the (rectangular) skull toward the vertical axis
        tp = _ss(0.05, 1.8, vv) ** 1.5
        d.x -= K['taper'] * p.x * 0.62 * tp
        d.y -= K['taper'] * (p.y - (F.eye.y + 0.9 * U)) * 0.45 * tp
        # occiput: the back of the skull bulges back past the neck
        A0 = math.atan2(abs(p.x), -(p.y - (F.eye.y + 0.9 * U)))
        d.y += K['occiput'] * 0.14 * U * _ss(1.9, 2.6, A0) * math.exp(-((vv - 0.25) / 0.45) ** 2)
        # temporalis bulges on the sides of the dome
        A_ = math.atan2(abs(p.x), -(p.y - (F.eye.y + 0.9 * U)))
        d += n * (K['temporalis'] * 0.08 * U * math.exp(-((A_ - 1.3) / 0.55) ** 2 - ((vv - 0.6) / 0.6) ** 2))
        # tall bald cranium
        # shrink ears toward their root
        if earw[i] > 0.0 and sx in earc:
            c = earc[sx]
            root = Vector((c.x * 0.80, c.y, c.z))
            d += (root - p) * (K['ear'] * earw[i])
        v.co = p + d * h

def _delete_lips(body):
    """Lipless mouth: remove the lip faces (vertices stay so vertex indices/groups are unchanged)."""
    g = body.vertex_groups.get("lips")
    if not g:
        return
    w = {}
    for v in body.data.vertices:
        for x in v.groups:
            if x.group == g.index:
                w[v.index] = x.weight
    bm = bmesh.new(); bm.from_mesh(body.data); bm.faces.ensure_lookup_table()
    dead = [f for f in bm.faces if all(w.get(v.index, 0.0) > 0.4 for v in f.verts)]
    bmesh.ops.delete(bm, geom=dead, context="FACES_ONLY")
    bm.to_mesh(body.data); bm.free()
    print("LIPS deleted faces", len(dead))

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

    def tooth(center, axes, half, mat, grp, row, pointed=False):
        """Rounded human-like tooth: a superellipsoid, slightly tapered toward the root."""
        res = bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=8, radius=1.0)
        for vt in res["verts"]:
            lx, ly, lz = vt.co
            lx = math.copysign(abs(lx) ** 0.5, lx); ly = math.copysign(abs(ly) ** 0.6, ly); lz = math.copysign(abs(lz) ** 0.35, lz)
            root = max(0.0, lz * row)                       # 0 at the bite edge, 1 at the root
            lx *= 1.0 - 0.22 * root
            if pointed and lz * row < -0.5:
                lx *= 1.0 - 0.6 * (-lz * row - 0.5)
            vt.co = center + axes[0] * (lx * half[0]) + axes[1] * (ly * half[1]) + axes[2] * (lz * half[2])
            vt[dl][grp] = 1.0
        for f in {f for vt in res["verts"] for f in vt.link_faces}:
            f.material_index = mat; f.smooth = True

    # teeth: two even rows that follow the face surface along the mouth line, incisors back to the molars
    eps = [p for p in _group_pts(body, ["ears"]) if p.x > 0]
    ec_ = _centroid(eps) if eps else Vector((2 * F.ex, yc, 0))
    a_end = math.atan2(abs(ec_.x), -(ec_.y - yc)) - 0.30
    WID = [0.072, 0.066, 0.078, 0.080, 0.080, 0.098, 0.100, 0.096, 0.090, 0.088, 0.085, 0.082, 0.080]
    HGT = [0.150, 0.145, 0.160, 0.135, 0.130, 0.120, 0.118, 0.112, 0.108, 0.104, 0.100, 0.096, 0.092]
    for sgn in (1, -1):
        a = 0.0; k = 0
        while k < len(WID):
            wdt = WID[k] * U * 1.25
            loc0, _ = surface(0.0 if k == 0 else a, mz)
            r_loc = (Vector((loc0.x, loc0.y - yc, 0)).length if loc0 else 1.1 * U)
            ac = a + (wdt / 2) / r_loc
            if ac > a_end:
                break
            curve = 0.08 * U * (ac / a_end) ** 2           # bite line rises slightly toward the back
            for row, grp in ((1, g_head), (-1, g_jaw)):
                hgt = HGT[k] * U * 1.7 * (0.92 if row < 0 else 1.0)
                zc = mz + curve + row * (hgt / 2 + 0.004 * U)
                loc, nr = surface(sgn * ac, zc)
                if loc is None:
                    continue
                nr = Vector((nr.x, nr.y, 0)).normalized() if abs(nr.z) < 0.95 else Vector((0, -1, 0))
                tang = Vector((0, 0, 1)).cross(nr).normalized()
                depth = 0.06 * U
                c = loc - nr * (depth * (0.75 + 0.6 * ac / a_end))
                tooth(Vector(c), (tang, -nr, Vector((0, 0, 1))), (wdt * 0.48, depth, hgt / 2), ti, grp, row, pointed=(k == 2))
            a += wdt * 0.93 / r_loc; k += 1
        print("TEETH per side", k)
    # eyeballs: small, deep in the sockets, no lids
    eye_pts = []
    for ec, gname in ((F.eyeL, "head"), (F.eyeR, "head")):
        r = 0.16 * U
        c = Vector((ec.x * 1.0, ec.y + 0.07 * U, ec.z - 0.01 * U))
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
            pass   # SCM cords stay red (sculpted bands); no pale strap on the throat
        # ---------------- head / face
        h = hd[i]
        if h > 0.01:
            u, vv, w = F.uvw(p)
            au = abs(u); sx = 1 if u >= 0 else -1
            fr = -n.y
            red = 0.0
            ue = F.ex / U
            A = math.atan2(abs(x), -(y - yc))          # unfolded angle around the head (0 = front centre)
            # Explicit painted regions: everything on the head is red muscle EXCEPT these pale bands.
            jaw_l = (v_chin + 0.16) + (-0.95 - (v_chin + 0.16)) * _cl((A - 0.55) / max(0.1, a_ear - 0.55)) ** 1.5
            pale = 0.0
            # Large smooth connected pale plates (anime layout); everything else on the head is red muscle.
            # 1) scalp + forehead, with red temporalis fans cut in at the sides
            dome = _ss(0.16, 0.26, vv)
            dt = ((A - 1.40) / 0.55) ** 2 + ((vv - 0.40) / 0.85) ** 2
            temporalis = _cl((1 - dt) * 3)
            pale = max(pale, dome * (1 - temporalis))
            # 2) band around each eye socket
            if fr > -0.1:
                for ec in (F.eyeL, F.eyeR):
                    re_ = math.hypot((x - ec.x) / U / 1.15, (z - ec.z) / U)
                    pale = max(pale, _ss(0.26, 0.29, re_) * _ss(0.38, 0.35, re_))
            # 3) nose bridge widening into the frame around the nasal cavity
            nb = 0.12 + 0.08 * _ss(-0.25, -0.50, vv)
            pale = max(pale, _ss(nb + 0.02, nb - 0.02, A) * _ss(-0.70, -0.64, vv) * _ss(0.30, 0.20, vv))
            # 4) cheekbone ridge from the eye band back to the ear
            zl = -0.42 - 0.10 * (A - 0.40)
            pale = max(pale, _ss(0.075, 0.05, abs(vv - zl)) * _ss(0.25, 0.35, A) * _ss(a_ear + 0.1, a_ear - 0.05, A))
            # 5) nasolabial strip from the nose wing down to the jaw line (front edge of the red cheek panel)
            cA = 0.32 + 0.10 * _cl((-0.6 - vv) / 1.0)
            pale = max(pale, _ss(0.05, 0.03, abs(A - cA)) * _ss(-0.45, -0.52, vv) * _ss(jaw_l - 0.06, jaw_l + 0.04, vv))
            # 5b) pale frame around the mouth: upper-lip band under the nose, lower-lip band under the teeth
            #     (red gums sit between these bands and the teeth)
            pale = max(pale, _ss(0.56, 0.48, A) * _ss(-0.52, -0.56, vv) * _ss(-0.70, -0.66, vv))
            pale = max(pale, _ss(0.60, 0.52, A) * _ss(-1.33, -1.37, vv) * _ss(-1.52, -1.48, vv))
            # 6) jaw / chin outline along the mandible from the ear to the chin
            # jaw edge from the geometry: where the mandible surface turns under
            pale = max(pale, _ss(-0.55, -0.25, n.z) * _ss(0.075, 0.05, abs(vv - (jaw_l - 0.02))) * _ss(a_ear + 0.05, a_ear - 0.1, A))
            hw = pale * _ss(-0.72, -0.42, n.z)      # undersides (below the jaw) stay red
            # cavities: very dark deep eye pits, big nasal cavity
            for ec in (F.eyeL, F.eyeR):
                r = math.hypot((x - ec.x) / U / 1.2, (z - ec.z - 0.05 * U) / U)
                cav = max(cav, _ss(0.28, 0.21, r) * _ss(-0.2, 0.3, fr))
            nas = (u / 0.15) ** 2 + ((vv + 0.50) / 0.14) ** 2
            cav = max(cav, _ss(1.0, 0.55, nas) * _ss(0, 0.3, fr))
            if fr > 0.2:      # dark vertical crease and star furrow at the brow centre
                cav = max(cav, 0.6 * _ss(0.035, 0.01, abs(u)) * _ss(0.25, 0.4, vv) * _ss(1.0, 0.7, vv))
                rs = math.hypot(u, vv - 0.32)
                if rs < 0.3:
                    spk = 0.5 + 0.5 * math.cos(9 * math.atan2(vv - 0.32, u))
                    cav = max(cav, 0.8 * _ss(0.3, 0.08, rs) * _ss(0.55, 0.9, spk))
            ring = _ss(0.55, 0.40, math.hypot(A - a_eye, (vv + 0.05) / 1.2))
            chin = _ss(0.55, 0.45, A) * _ss(-1.25, -1.35, vv)
            temple = temporalis * dome
            cheek = 1.0
            # fibre phase on the face
            if ring > 0.5:
                ec = F.eyeL if x > 0 else F.eyeR
                fph = math.atan2(z - ec.z, x - ec.x) * 46 / (2 * math.pi)
            elif chin > 0.5:
                fph = x / PER_FACE
            elif temple > 0.5:
                fph = math.atan2(vv + 0.45, (A - 1.30) * 1.1) * 80 / (2 * math.pi)
            else:
                fph = math.copysign(A, x) * 1.1 * U / PER_FACE
            phase = fph if h > 0.25 else phase
            white = white * (1 - h) + hw * h
            cav *= h
        if i >= body.get("eye_start", 10 ** 9):
            ce = F.eyeL if x > 0 else F.eyeR
            dn = (p - Vector((ce.x, ce.y + 0.07 * U, ce.z - 0.01 * U))).normalized()
            hd[i] = 1.0
            dd = dn.dot(Vector((-0.12 * (1 if x > 0 else -1), -1, 0.05)).normalized())
            white, phase, cav = 0.0, 0.0, (1.0 if dd > 0.975 else 0.5 if dd > 0.90 else 0.0)
        out.append((white, phase, cav, hd[i]))
    # smooth the pale mask over the mesh: merges plates into clean shapes and removes isolated specks
    estart = body.get("eye_start", 10 ** 9)
    nb_ = [[] for _ in me.vertices]
    for e in me.edges:
        i0, i1 = e.vertices
        nb_[i0].append(i1); nb_[i1].append(i0)
    wv = [o[0] for o in out]
    for _ in range(3):
        wv = [wv[i] if (i >= estart or not nb_[i]) else 0.4 * wv[i] + 0.6 * sum(wv[j] for j in nb_[i]) / len(nb_[i])
              for i in range(len(wv))]
    out = [((_cl((wv[i] - 0.25) / 0.5) if i < estart else wv[i]), o[1], o[2], o[3]) for i, o in enumerate(out)]
    at = me.color_attributes.get("cmask") or me.color_attributes.new("cmask", "FLOAT_COLOR", "POINT")
    for i, (a, b, c, h) in enumerate(out):
        at.data[i].color = (a, (b % 1000.0) + 1.0, c, h)     # keep the fibre phase positive

# ---------------------------------------------------------------- 6. materials
def _mat_body(name):
    """Anime cel-like muscle: flat saturated red bundles, darker toward bundle edges, thin dark-red seams
    between bundles, a few long bright specular strokes along the fibres; fibres only as a faint bump.
    Pale fascia: smooth off-white with soft grey shading and a thin dark outline. Principled + procedural."""
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; N = nt.nodes; L = nt.links; b = N["Principled BSDF"]
    at = N.new("ShaderNodeAttribute"); at.attribute_name = "cmask"; at.attribute_type = "GEOMETRY"
    sep = N.new("ShaderNodeSeparateColor"); L.new(at.outputs["Color"], sep.inputs[0])
    tc = N.new("ShaderNodeAttribute"); tc.attribute_name = "crest"; tc.attribute_type = "GEOMETRY"   # rest position
    def noise(scale, detail=3):
        n = N.new("ShaderNodeTexNoise"); n.inputs["Scale"].default_value = scale; n.inputs["Detail"].default_value = detail
        L.new(tc.outputs["Vector"], n.inputs["Vector"]); return n.outputs["Fac"]
    def math_(op, a, bb=None):
        n = N.new("ShaderNodeMath"); n.operation = op
        for k, x in enumerate((a, bb)):
            if x is None:
                continue
            if isinstance(x, (int, float)):
                n.inputs[k].default_value = x
            else:
                L.new(x, n.inputs[k])
        return n.outputs[0]
    def mrange(x, a0, a1, b0=0.0, b1=1.0):
        n = N.new("ShaderNodeMapRange"); n.inputs["From Min"].default_value = a0; n.inputs["From Max"].default_value = a1
        n.inputs["To Min"].default_value = b0; n.inputs["To Max"].default_value = b1
        L.new(x, n.inputs["Value"]); return n.outputs["Result"]
    def mix(f, A, B):
        n = N.new("ShaderNodeMix"); n.data_type = "RGBA"
        L.new(f, n.inputs["Factor"])
        for k, x in (("A", A), ("B", B)):
            if isinstance(x, tuple):
                n.inputs[k].default_value = (*x, 1)
            else:
                L.new(x, n.inputs[k])
        return n.outputs["Result"]
    G = sep.outputs["Green"]
    n_lo = noise(4.0, 2); n_md = noise(12.0, 3); n_hi = noise(30.0, 4)
    TAU = 2 * math.pi
    # fine fibres (bump only)
    fine = math_("SINE", math_("ADD", math_("MULTIPLY", G, TAU), math_("MULTIPLY", math_("SUBTRACT", n_hi, 0.5), 3.0)))
    # muscle bundles: every ~6 fibres a seam
    gph = math_("ADD", math_("MULTIPLY", G, TAU / 6.0), math_("MULTIPLY", math_("SUBTRACT", n_lo, 0.5), 2.5))
    gc = math_("COSINE", gph)
    seam = mrange(gc, 0.955, 0.995)                       # thin dark seam line
    edge = mrange(gc, 0.15, 0.95)                         # soft darkening toward the seam
    # sparse long specular strokes along fibres
    sph = math_("SINE", math_("ADD", math_("MULTIPLY", G, TAU * 0.5), math_("MULTIPLY", math_("SUBTRACT", n_md, 0.5), 2.0)))
    stroke = math_("MULTIPLY", mrange(sph, 0.975, 0.998), mrange(n_lo, 0.50, 0.62))
    red = mix(mrange(n_md, 0.3, 0.7), (0.50, 0.045, 0.026), (0.62, 0.065, 0.035))
    red = mix(math_("MULTIPLY", edge, 0.75), red, (0.20, 0.016, 0.010))
    red = mix(seam, red, (0.075, 0.006, 0.004))
    red = mix(math_("MULTIPLY", stroke, 0.85), red, (1.0, 0.86, 0.66))
    # pale fascia mask with a crisp, slightly wobbly edge
    wj = math_("ADD", sep.outputs["Red"], math_("MULTIPLY", math_("SUBTRACT", n_md, 0.5), 0.06))
    W = mrange(wj, 0.47, 0.53)
    pale = mix(mrange(n_lo, 0.35, 0.65), (0.60, 0.56, 0.50), (0.80, 0.75, 0.66))
    col = mix(W, red, pale)
    outline = mrange(math_("ABSOLUTE", math_("SUBTRACT", wj, 0.5)), 0.012, 0.035, 1.0, 0.0)
    col = mix(outline, col, (0.16, 0.03, 0.025))
    cav = mrange(sep.outputs["Blue"], 0.2, 0.7)
    col = mix(cav, col, (0.035, 0.016, 0.013))
    L.new(col, b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.42
    L.new(mrange(W, 0, 1, 0.32, 0.08), b.inputs["Coat Weight"])
    b.inputs["Coat Roughness"].default_value = 0.22
    b.inputs["Subsurface Weight"].default_value = 0.05; b.inputs["Subsurface Radius"].default_value = (1, 0.2, 0.1)
    inv = math_("SUBTRACT", 1.0, W)
    hgt = math_("ADD", math_("MULTIPLY", math_("ADD", math_("MULTIPLY", fine, 0.15), math_("MULTIPLY", seam, -0.6)), inv),
                math_("MULTIPLY", W, 0.3))
    bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.45; bp.inputs["Distance"].default_value = 0.03
    L.new(hgt, bp.inputs["Height"]); L.new(bp.outputs["Normal"], b.inputs["Normal"])
    return m

def _mat_teeth(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (0.70, 0.60, 0.40, 1); b.inputs["Roughness"].default_value = 0.25
    b.inputs["Coat Weight"].default_value = 0.3
    return m

def _mat_eye(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; N = nt.nodes; L = nt.links; b = N["Principled BSDF"]
    at = N.new("ShaderNodeAttribute"); at.attribute_name = "cmask"; at.attribute_type = "GEOMETRY"
    sp = N.new("ShaderNodeSeparateColor"); L.new(at.outputs["Color"], sp.inputs[0])
    rp = N.new("ShaderNodeValToRGB"); rp.color_ramp.interpolation = "CONSTANT"; e = rp.color_ramp.elements
    e[0].position, e[0].color = 0.0, (0.10, 0.085, 0.07, 1)       # sclera (deep in socket shadow)
    e[1].position, e[1].color = 0.25, (0.82, 0.82, 0.70, 1)      # pale iris
    e.new(0.75).color = (0.015, 0.015, 0.015, 1)                 # pupil
    L.new(sp.outputs["Blue"], rp.inputs["Fac"]); L.new(rp.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.15
    return m

# ---------------------------------------------------------------- public API
def make_colossal(name="Colossal"):
    rig = _make_base(name)
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
    _delete_lips(body)
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
    P = rig.pose.bones
    for n in ("neck01", "neck02", "neck03", "head"):
        P[n].rotation_mode = "XYZ"
    P["neck01"].rotation_euler.x = -0.22     # hold the long neck upright
    P["neck02"].rotation_euler.x = -0.08
    P["head"].rotation_euler.x = 0.25        # face level

def _steam_obj(name, center, size, density=0.5, noise_scale=2.0, glow=0.0, seed=0.0, tint=(0.95, 0.93, 0.90), ambient=0.0):
    """Billowy steam volume: lumpy cumulus density (noise + falloff), warm glow at the bottom.
    Principled Volume + procedural noise only (Eevee and Cycles)."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0); bm.to_mesh(me); bm.free()
    st = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(st)
    st.location = center; st.scale = size
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; N = nt.nodes; L = nt.links
    N.remove(N["Principled BSDF"])
    pv = N.new("ShaderNodeVolumePrincipled")
    pv.inputs["Color"].default_value = (*tint, 1)       # #E8E4DE by default (albedo kept high so backlit steam stays bright)
    pv.inputs["Emission Color"].default_value = (1.0, 0.96, 0.9, 1)
    pv.inputs["Emission Strength"].default_value = 0.0   # emission ignores density: any constant lights the whole box
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
            mth("MULTIPLY", mth("SUBTRACT", 0.36, ln.outputs["Value"]), 12.0))
    v = mth("MULTIPLY", mth("MINIMUM", mth("MAXIMUM", v, 0.0), 1.0), density)
    L.new(v, pv.inputs["Density"])
    if ambient > 0:      # self-lit body of the cloud (anime steam stays bright even when backlit)
        amb = mth("MULTIPLY", mth("MINIMUM", mth("MULTIPLY", v, 3.0 / max(density, 1e-3)), 1.0), ambient)
        pv.inputs["Emission Color"].default_value = (*tint, 1)
        L.new(amb, pv.inputs["Emission Strength"])
    if glow > 0:
        sz = N.new("ShaderNodeSeparateXYZ"); L.new(tc.outputs["Generated"], sz.inputs[0])
        mr = N.new("ShaderNodeMapRange"); mr.inputs["From Min"].default_value = 0.55; mr.inputs["From Max"].default_value = 0.0
        mr.inputs["To Max"].default_value = glow
        L.new(sz.outputs["Z"], mr.inputs["Value"])
        gl = mth("MULTIPLY", mr.outputs["Result"], mth("MINIMUM", mth("MULTIPLY", v, 4.0 / max(density, 1e-3)), 1.0))
        if ambient > 0:
            L.new(mth("ADD", gl, amb), pv.inputs["Emission Strength"])
            pv.inputs["Emission Color"].default_value = (tint[0], tint[1] * 0.85, tint[2] * 0.7, 1)
        else:
            L.new(gl, pv.inputs["Emission Strength"])
            pv.inputs["Emission Color"].default_value = (1.0, 0.45, 0.18, 1)
    L.new(pv.outputs[0], N["Material Output"].inputs["Volume"])
    me.materials.append(m)
    return st

def colossal_steam(rig, density=1.5, tint=(0.95, 0.93, 0.90), glow_scale=1.0, ambient=0.0):
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
        st = _steam_obj(f"{rig.name}_{nm}", c, tuple(x * s for x in size), density=d, noise_scale=ns, glow=glow * glow_scale,
                        seed=len(out) * 3.1, tint=tint, ambient=ambient)
        bpy.context.view_layer.update()
        mw = st.matrix_world.copy()
        st.parent = rig; st.parent_type = "BONE"; st.parent_bone = bn
        bpy.context.view_layer.update()
        st.matrix_world = mw
        out.append(st)
    return out

def colossal_embers(rig, count=400, radius=18.0, seed=3):
    """Glowing orange embers (#FF9A40) floating around the head and shoulders: one mesh of tiny
    emissive icospheres, bone-parented to the neck. Emission + Principled only (Eevee/Cycles)."""
    import random
    rnd = random.Random(seed)
    B = rig.data.bones
    c = rig.matrix_world @ B["neck03"].head_local
    bm = bmesh.new()
    for _ in range(count):
        d = Vector((rnd.gauss(0, 1), rnd.gauss(0, 1) * 0.8, rnd.gauss(0, 1) * 0.9))
        p = c + d.normalized() * radius * (0.35 + rnd.random() ** 0.7) + Vector((0, 0, radius * 0.25))
        r = rnd.uniform(0.025, 0.07)
        res = bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
        for v in res["verts"]:
            v.co += p
    me = bpy.data.meshes.new(rig.name + "_embers"); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(rig.name + "_embers", me); bpy.context.scene.collection.objects.link(ob)
    m = bpy.data.materials.new(rig.name + "_ember"); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (1.0, 0.33, 0.05, 1)
    b.inputs["Emission Color"].default_value = (1.0, 0.33, 0.05, 1)        # #FF9A40
    b.inputs["Emission Strength"].default_value = 6.0
    me.materials.append(m)
    bpy.context.view_layer.update()
    mw = ob.matrix_world.copy()
    ob.parent = rig; ob.parent_type = "BONE"; ob.parent_bone = "neck03"
    bpy.context.view_layer.update()
    ob.matrix_world = mw
    return ob

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

def pose_wall_grip(rig, wall_top_z, wall_face_y, side="L", lean=0.22, hand_x=None, grip_depth=4.0, elbow_out=7.0):
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
    # elbow sticks out sideways and slightly forward/down: a clearly bent arm leaning on the wall
    egoal = Vector((hx + sg * elbow_out, wall_face_y + 3.0, wall_top_z + 0.5))
    def cost():
        wr = W @ P[f"wrist.{side}"].head; tip = W @ P[f"metacarpal3.{side}"].tail
        m2 = W @ P[f"metacarpal2.{side}"].tail; m4 = W @ P[f"metacarpal4.{side}"].tail
        hd = (tip - wr).normalized()
        palm = (m4 - m2).cross(hd).normalized() * (1 if side == "L" else -1)
        want = Vector((0, -1, -0.15)).normalized()
        c = (tip - goal).length + 6.0 * (1 - hd.dot(want)) + 6.0 * (1 - palm.dot(Vector((0, 0, -1))))
        if elbow_out:
            el = W @ P[f"lowerarm01.{side}"].head
            c += 0.8 * (el - egoal).length
        return c
    chans = [(f"upperarm01.{side}", 0), (f"upperarm01.{side}", 2), (f"upperarm01.{side}", 1),
             (f"lowerarm01.{side}", 0), (f"lowerarm01.{side}", 1), (f"wrist.{side}", 0), (f"wrist.{side}", 2), (f"wrist.{side}", 1)]
    P[f"lowerarm01.{side}"].rotation_euler.x = 1.1          # start bent so the solver keeps a real elbow
    e = _solve(rig, chans, cost, iters=220)
    e2 = None
    print("GRIP elbow", tuple(round(c, 1) for c in (W @ P[f"lowerarm01.{side}"].head)), "goal", tuple(round(c, 1) for c in egoal),
          "shoulder", tuple(round(c, 1) for c in sh))
    for pb in P:
        if pb.name.startswith(("wrist", "lower", "upperarm")) and pb.name.endswith(side):
            pass
    print("GRIP cost", round(e, 2))
    # curl the fingers down over the edge
    for f in range(2, 6):
        for j, a in ((1, 0.75), (2, 1.0), (3, 0.8)):
            bn = f"finger{f}-{j}.{side}"
            if bn in P:
                P[bn].rotation_euler.x = a
    bpy.context.view_layer.update()
    return goal

