"""Shifter Titans (Season 1 anime look): Armored (15 m), Female (14 m), Attack / Eren (15 m).

    import sys; sys.path.insert(0, "/home/user/YTP1/timelapse3d/aot")
    import shifters
    rig = shifters.make_armored()      # or make_female(), make_attack()

Each function returns the MPFB2 "default" armature with the body (and hair, eyes, teeth) skinned to it,
the rig scaled so the titan stands at its canon height with its feet at the rig origin.

How it is built (all procedural, Principled BSDF + procedural nodes only, Eevee friendly):
  * MPFB2 / MakeHuman CC0 base body with macro + face targets, helper geometry removed, one level of
    subdivision applied (~55k quads).
  * Every face gets a region label from rules written in the rig's bone space (dominant bone, position
    along the bone, angle around it). Labels are armour plates / pale skin patches / exposed muscle.
  * A geodesic distance-to-region-border field drives a real relief (raised bevelled plates, sunken
    muscle) and point attributes the materials read (sh_skin, sh_edge, sh_cav, sh_eye, sh_hair, sh_fib...).
  * Anime "chunky lock" hair, eyes and (Attack Titan) cheek teeth are generated meshes on the same rig.
"""
import bpy, bmesh, math, os, sys, random, heapq, importlib
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import titans

HS, TS, ASSET = titans.HS, titans.TS, titans.ASSET
TDIR = titans.TDIR
HEIGHT = {"armored": 15.0, "female": 14.0, "attack": 15.0}


# ------------------------------------------------------------------ small helpers
def _ss(a, b, x):
    if a == b:
        return 1.0 if x >= b else 0.0
    t = max(0.0, min(1.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


def _lr(t, w):
    return [(t.format(s="l"), w), (t.format(s="r"), w)]


def _load_targets(body, items):
    for t, w in items:
        p = os.path.join(TDIR, t + ".target.gz")
        if os.path.exists(p) and abs(w) > 1e-4:
            TS.load_target(body, p, weight=w)
        else:
            print("[shifters] missing target", t)


def _group_pts(body, name, thr=0.5):
    g = body.vertex_groups.get(name)
    if not g:
        return []
    gi = g.index
    return [v.co.copy() for v in body.data.vertices for x in v.groups if x.group == gi and x.weight > thr]


def _center(pts):
    c = Vector()
    for p in pts:
        c += p
    return c / max(1, len(pts))


def _apply_subsurf(obj, levels=1):
    m = obj.modifiers.new("sh_sub", "SUBSURF")
    m.levels = levels; m.render_levels = levels; m.quality = 3
    with bpy.context.temp_override(object=obj, active_object=obj, selected_objects=[obj]):
        bpy.ops.object.modifier_move_to_index(modifier=m.name, index=0)
        bpy.ops.object.modifier_apply(modifier=m.name)


def _skin_to_rig(obj, rig, weights):
    """weights: dict group-name -> list of per-vertex weights (or a single float for all)."""
    for gname, w in weights.items():
        g = obj.vertex_groups.new(name=gname)
        if isinstance(w, (int, float)):
            g.add(list(range(len(obj.data.vertices))), float(w), "REPLACE")
        else:
            for i, wi in enumerate(w):
                if wi > 1e-4:
                    g.add([i], wi, "REPLACE")
    obj.parent = rig
    md = obj.modifiers.new("Armature", "ARMATURE"); md.object = rig


def _new_obj(name, verts, faces, coll=None):
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in verts], [], faces)
    me.update()
    ob = bpy.data.objects.new(name, me)
    (coll or bpy.context.scene.collection).objects.link(ob)
    for p in me.polygons:
        p.use_smooth = True
    return ob


def _set_attr(me, name, vals, kind="FLOAT"):
    a = me.attributes.get(name)
    if a:
        me.attributes.remove(a)
    a = me.attributes.new(name, kind, "POINT")
    if kind == "FLOAT":
        a.data.foreach_set("value", vals)
    else:
        flat = [c for v in vals for c in v]
        a.data.foreach_set("vector", flat)


# ------------------------------------------------------------------ base body
def _build_body(name, macro, face, pre_sub=None):
    md = TS.get_default_macro_info_dict()
    md.update(macro)
    body = HS.create_human(feet_on_ground=True, scale=0.1, macro_detail_dict=md)
    _load_targets(body, face)
    rig = HS.add_builtin_rig(body, "default")
    TS.bake_targets(body)
    eyes = {}
    for s, gn in (("L", "helper-l-eye"), ("R", "helper-r-eye")):
        pts = _group_pts(body, gn)
        c = _center(pts)
        r = max((p - c).length for p in pts) if pts else 0.014
        eyes[s] = (c, r)
    titans._bake_and_clean(body)
    rig.name = name; body.name = name + "_body"
    if pre_sub:
        pre_sub(body, rig)
    _apply_subsurf(body, 1)
    return rig, body, eyes


# ------------------------------------------------------------------ per-vertex / per-face features
_DEFORM_SKIP = set()


def _features(body, rig):
    """Dominant bone, position along the bone (t), angle around the bone for every vertex."""
    me = body.data
    gnames = {g.index: g.name for g in body.vertex_groups}
    bones = rig.data.bones
    dom = []
    for v in me.vertices:
        best, bw = None, 0.0
        for g in v.groups:
            n = gnames[g.group]
            if g.weight > bw and n in bones:
                best, bw = n, g.weight
        dom.append(best or "root")
    return dom


def _bone_frame(rig, bname):
    B = rig.data.bones[bname]
    h, t = B.head_local.copy(), B.tail_local.copy()
    return h, t


def _limb_coords(p, h, t, out_ref, front_ref=Vector((0, -1, 0))):
    """t along bone (0..1), angle (deg): 0 = front, +90 = outer side, +-180 = back, -90 = inner side."""
    ax = t - h; L = ax.length; a = ax / L
    d = p - h; s = d.dot(a)
    r = d - a * s
    f = front_ref - a * front_ref.dot(a); f.normalize()
    o = out_ref - a * out_ref.dot(a) - f * out_ref.dot(f); o.normalize()
    ang = math.degrees(math.atan2(r.dot(o), r.dot(f)))
    return s / L, ang, r.length


# ------------------------------------------------------------------ relief + attributes
def _relief(body, labels, plate_set, params, face_lab_extra=None):
    """labels: per-face int (0 = muscle / sunken).  plate_set: labels that are raised plates/skin.
    params: dict(h=plate height, w=bevel width, pillow, pw, sink, sw, edge=line width)
    Writes vertex offsets along the normal, and the attributes sh_skin, sh_edge, sh_dist."""
    me = body.data
    bm = bmesh.new(); bm.from_mesh(me)
    bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table()
    nv = len(bm.verts)
    vlab = [None] * nv
    border = [False] * nv
    for v in bm.verts:
        labs = {labels[f.index] for f in v.link_faces}
        if len(labs) == 1:
            vlab[v.index] = labs.pop()
        else:
            border[v.index] = True
            vlab[v.index] = max(labs, key=lambda l: (l in plate_set, l))
    # geodesic distance to the nearest region border
    INF = 1e9
    dist = [INF] * nv
    pq = []
    for i in range(nv):
        if border[i]:
            dist[i] = 0.0; pq.append((0.0, i))
    heapq.heapify(pq)
    while pq:
        d, i = heapq.heappop(pq)
        if d > dist[i]:
            continue
        v = bm.verts[i]
        for e in v.link_edges:
            o = e.other_vert(v); j = o.index
            nd = d + e.calc_length()
            if nd < dist[j] and nd < 0.2:
                dist[j] = nd; heapq.heappush(pq, (nd, j))
    # smooth the distance field so seams follow soft curves instead of the quad stair-steps
    nb = [[e.other_vert(v).index for e in v.link_edges] for v in bm.verts]
    for _ in range(params.get("smooth", 2)):
        dist = [0.5 * dist[i] + 0.5 * sum(dist[j] for j in nb[i]) / len(nb[i]) if nb[i] else dist[i]
                for i in range(nv)]
    # re-pin the border to zero after smoothing
    bvals = sorted(dist[i] for i in range(nv) if border[i])
    d0 = bvals[len(bvals) // 2] if bvals else 0.0
    dist = [max(0.0, d - d0) for d in dist]
    h, w = params.get("h", 0.0), params.get("w", 0.01)
    pil, pw = params.get("pillow", 0.0), params.get("pw", 0.03)
    sink, sw = params.get("sink", 0.0), params.get("sw", 0.01)
    edge = params.get("edge", 0.004)
    per = params.get("per_label", {})
    skin, edgev, rim, sd = [0.0] * nv, [0.0] * nv, [0.0] * nv, [0.0] * nv
    bm.normal_update()
    for v in bm.verts:
        i = v.index; d = dist[i]; lab = vlab[i]
        if lab in plate_set:
            pr = per.get(lab, (h, w, pil, pw))
            hh, ww, pp, ppw = pr[:4]
            off = hh * _ss(0, ww, d) + pp * _ss(0, ppw, d)
            skin[i] = 1.0
        else:
            off = -sink * _ss(0, sw, d)
            skin[i] = 0.0
        ed = per[lab][4] if lab in per and len(per[lab]) > 4 else edge
        edgev[i] = 1.0 - _ss(ed * 0.5, ed, d)
        sd[i] = (d / ed) if lab in plate_set else -(d / ed)
        if lab in plate_set:
            rim[i] = _ss(ed * 0.9, ed * 1.4, d) * (1.0 - _ss(ed * 1.8, ed * 3.0, d))
        v.co += v.normal * off
    bm.to_mesh(me); bm.free()
    _set_attr(me, "sh_skin", skin)
    _set_attr(me, "sh_edge", edgev)
    _set_attr(me, "sh_rim", rim)
    _set_attr(me, "sh_sd", sd)      # signed border distance in line widths: crisp iso-lines in the shader
    return vlab, dist


def _cavity(body, iters=3, gain=6.0):
    """Per-vertex concavity (anime-style shading in creases), smoothed; written to sh_cav (0..1)."""
    me = body.data
    bm = bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table(); bm.normal_update()
    nv = len(bm.verts)
    c = [0.0] * nv
    for v in bm.verts:
        s, n = 0.0, 0
        for e in v.link_edges:
            o = e.other_vert(v); d = o.co - v.co; L = d.length
            if L > 1e-9:
                s += v.normal.dot(d) / L; n += 1
        c[v.index] = s / max(1, n)
    nb = [[e.other_vert(v).index for e in v.link_edges] for v in bm.verts]
    for _ in range(iters):
        c = [0.5 * c[i] + 0.5 * sum(c[j] for j in nb[i]) / max(1, len(nb[i])) for i in range(nv)]
    bm.free()
    vals = [max(0.0, min(1.0, x * gain)) for x in c]
    _set_attr(me, "sh_cav", vals)
    return vals


# ------------------------------------------------------------------ face / bone region helpers
_ARM = ("shoulder01", "upperarm01", "upperarm02", "lowerarm01", "lowerarm02")
_LEG = ("upperleg01", "upperleg02", "lowerleg01", "lowerleg02")
_TORSO = ("root", "spine01", "spine02", "spine03", "spine04", "spine05", "breast", "pelvis", "clavicle")


def _base(bn):
    return bn.split(".")[0]


def _side(bn, x):
    if bn.endswith(".L"):
        return 1
    if bn.endswith(".R"):
        return -1
    return 1 if x >= 0 else -1


def _is_head_bone(bn):
    b = _base(bn)
    return not (b in _TORSO or b in _ARM or b in _LEG or b in ("neck01", "neck02", "wrist", "foot")
                or b.startswith(("finger", "metacarpal", "toe")))


class _Ctx:
    def __init__(self, body, rig, eyes):
        self.body, self.rig, self.eyes = body, rig, eyes
        B = rig.data.bones
        self.B = B
        self.z = {n: B[n].head_local.z for n in ("neck01", "head", "spine01", "spine02", "spine03", "spine04",
                                                   "spine05", "upperleg01.L", "upperleg02.L", "clavicle.L")}
        lips = _group_pts(body, "lips")
        self.lips = _center(lips) if lips else Vector((0, -0.15, 1.547))
        self.eye = eyes["L"][0]
        self.dom = _features(body, rig)
        ears = _group_pts(body, "ears")
        self.ear_x = max(abs(p.x) for p in ears) if ears else 0.085
        scalp = _group_pts(body, "scalp", 0.3)
        self.head_top = max(p.z for p in scalp) if scalp else self.B["head"].tail_local.z

    def face_dom(self, f):
        cnt = {}
        for vi in f.vertices:
            b = self.dom[vi]; cnt[b] = cnt.get(b, 0) + 1
        return max(cnt, key=cnt.get)

    def limb(self, bn, p):
        h, t = _bone_frame(self.rig, bn)
        s = _side(bn, p.x)
        b = _base(bn)
        if b in _ARM or b in ("wrist",):
            out = Vector((0, 0, 1))      # A-pose arm: the outer (deltoid / triceps-lateral) side faces up
        else:
            out = Vector((s, 0, 0))
        return _limb_coords(p, h, t, out)


def _label_faces(body, rig, eyes, rule):
    ctx = _Ctx(body, rig, eyes)
    me = body.data
    keys = {}
    labels = []
    for f in me.polygons:
        bn = ctx.face_dom(f)
        k = rule(ctx, bn, f.center.copy(), f.normal.copy())
        if k not in keys:
            keys[k] = len(keys)
        labels.append(keys[k])
    labels = _mode_filter(me, labels, iters=2)
    return labels, keys, ctx


def _mode_filter(me, labels, iters=2):
    """Smooth region borders: a face takes the label most of its edge-neighbours have (removes stair steps)."""
    bm = bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table()
    nb = [[o.index for e in f.edges for o in e.link_faces if o.index != f.index] for f in bm.faces]
    bm.free()
    for _ in range(iters):
        new = labels[:]
        for i, ns in enumerate(nb):
            cnt = {}
            for j in ns:
                cnt[labels[j]] = cnt.get(labels[j], 0) + 1
            best = max(cnt, key=cnt.get) if cnt else labels[i]
            if best != labels[i] and cnt[best] >= 3:
                new[i] = best
        labels = new
    return labels


def _face_seed_label(p, seeds, xw=1.0):
    best, bd = None, 1e9
    for k, (sx, sz) in seeds.items():
        for sgn in ((1, -1) if sx > 0 else (1,)):
            d = (xw * (abs(p.x) - abs(sx)) if sgn else 0) ** 2
            d = (xw * (p.x - sgn * sx)) ** 2 + (p.z - sz) ** 2
            if d < bd:
                bd = d; best = k + ("" if sx == 0 else ("L" if sgn > 0 else "R"))
    return best


# ------------------------------------------------------------------ materials
def _nodes(m):
    m.use_nodes = True
    nt = m.node_tree
    return nt, nt.nodes, nt.links, nt.nodes["Principled BSDF"]


def _attr(N, name, kind="GEOMETRY"):
    a = N.new("ShaderNodeAttribute"); a.attribute_name = name; a.attribute_type = kind
    return a


def _mix(N, L, fac, a, b, blend="MIX"):
    m = N.new("ShaderNodeMix"); m.data_type = "RGBA"; m.blend_type = blend
    for inp, val in ((m.inputs["Factor"], fac), (m.inputs["A"], a), (m.inputs["B"], b)):
        if isinstance(val, (tuple, list)):
            inp.default_value = tuple(val) + ((1.0,) if len(val) == 3 else ())
        elif isinstance(val, (int, float)):
            inp.default_value = val if inp.name == "Factor" else (val, val, val, 1.0)
        else:
            L.new(val, inp)
    return m.outputs["Result"]


def _mrange(N, L, src, a, b, c=0.0, d=1.0):
    r = N.new("ShaderNodeMapRange")
    r.inputs["From Min"].default_value = a; r.inputs["From Max"].default_value = b
    r.inputs["To Min"].default_value = c; r.inputs["To Max"].default_value = d
    L.new(src, r.inputs["Value"])
    return r.outputs["Result"]


def _math(N, L, op, a, b=None):
    m = N.new("ShaderNodeMath"); m.operation = op
    for i, v in enumerate((a, b)):
        if v is None:
            continue
        if isinstance(v, (int, float)):
            m.inputs[i].default_value = v
        else:
            L.new(v, m.inputs[i])
    return m.outputs[0]


def _mat_body(name, skin_col, muscle_col, edge_col, *, skin_rough=0.5, skin_var=0.12, plate_mode=False,
              hair_col=None, eye_col=(0.02, 0.01, 0.01), eye_amt=0.0, cav_amt=0.55, fib_scale=180.0,
              harden=False, muscle_hi=(0.75, 0.25, 0.18), rim_col=None, alt_col=None):
    """One material for the whole body, driven by the sh_* attributes."""
    m = bpy.data.materials.new(name)
    nt, N, L, b = _nodes(m)
    sdv = _attr(N, "sh_sd").outputs["Fac"]
    skin = _mrange(N, L, sdv, -0.3, 0.3)
    edge = _mrange(N, L, _math(N, L, "ABSOLUTE", sdv), 0.4, 0.7, 1.0, 0.0)
    cav = _attr(N, "sh_cav").outputs["Fac"]
    rest = _attr(N, "sh_rest").outputs["Vector"]
    fib = _attr(N, "sh_fib").outputs["Vector"]
    # --- skin / plate colour with large-scale mottling
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 9.0; nz.inputs["Detail"].default_value = 4
    L.new(rest, nz.inputs["Vector"])
    skc = _mix(N, L, _mrange(N, L, nz.outputs["Fac"], 0.3, 0.7, 0, skin_var), skin_col,
               tuple(c * 0.7 for c in skin_col))
    if plate_mode:
        # fine stony speckle on armour
        nz2 = N.new("ShaderNodeTexNoise"); nz2.inputs["Scale"].default_value = 140.0; nz2.inputs["Detail"].default_value = 3
        L.new(rest, nz2.inputs["Vector"])
        skc = _mix(N, L, _mrange(N, L, nz2.outputs["Fac"], 0.35, 0.75, 0, 0.18), skc, (0.25, 0.2, 0.12))
    # --- muscle: striations along the fibre coordinate
    wv = N.new("ShaderNodeTexWave"); wv.wave_type = "BANDS"; wv.bands_direction = "X"
    wv.inputs["Scale"].default_value = fib_scale; wv.inputs["Distortion"].default_value = 2.5
    wv.inputs["Detail"].default_value = 3; wv.inputs["Detail Scale"].default_value = 1.5
    L.new(fib, wv.inputs["Vector"])
    mus = _mix(N, L, _mrange(N, L, wv.outputs["Fac"], 0.15, 0.95), tuple(c * 0.45 for c in muscle_col), muscle_col)
    mus = _mix(N, L, _mrange(N, L, wv.outputs["Fac"], 0.85, 1.0, 0, 0.35), mus, muscle_hi)
    if alt_col is not None:
        skc = _mix(N, L, _attr(N, "sh_alt").outputs["Fac"], skc, alt_col)
    if rim_col is not None:
        rimf = _math(N, L, "MULTIPLY", _mrange(N, L, sdv, 0.7, 1.0), _mrange(N, L, sdv, 1.2, 2.2, 1.0, 0.0))
        skc = _mix(N, L, _math(N, L, "MULTIPLY", rimf, 0.45), skc, rim_col)
    col = _mix(N, L, _mrange(N, L, skin, 0.35, 0.65), mus, skc)
    # --- outline at region borders and crease darkening
    col = _mix(N, L, edge, col, edge_col)
    col = _mix(N, L, _math(N, L, "MULTIPLY", cav, cav_amt), col, tuple(c * 0.25 for c in skin_col), "MULTIPLY")
    if hair_col is not None:
        col = _mix(N, L, _attr(N, "sh_hair").outputs["Fac"], col, hair_col)
    if eye_amt > 0:
        col = _mix(N, L, _math(N, L, "MULTIPLY", _attr(N, "sh_eye").outputs["Fac"], eye_amt), col, eye_col)
    rough = _mix(N, L, skin, 0.42, skin_rough)
    if eye_amt > 0:
        rough = _mix(N, L, _attr(N, "sh_eye").outputs["Fac"], rough, 0.9)
    if harden:
        # Female Titan crystal hardening: value node "Hardening" (0..1) x attribute sh_hard
        hv = N.new("ShaderNodeValue"); hv.name = hv.label = "Hardening"; hv.outputs[0].default_value = 0.0
        hf = _math(N, L, "MULTIPLY", _attr(N, "sh_hard").outputs["Fac"], hv.outputs[0])
        vo = N.new("ShaderNodeTexVoronoi"); vo.inputs["Scale"].default_value = 60.0
        L.new(rest, vo.inputs["Vector"])
        cry = _mix(N, L, _mrange(N, L, vo.outputs["Distance"], 0.0, 0.6), (0.55, 0.75, 0.95), (0.12, 0.18, 0.45))
        col = _mix(N, L, hf, col, cry)
        rough = _mix(N, L, hf, rough, 0.08)
        L.new(hf, b.inputs["Coat Weight"])
    L.new(col, b.inputs["Base Color"])
    L.new(rough, b.inputs["Roughness"])
    b.inputs["Subsurface Weight"].default_value = 0.08
    b.inputs["Subsurface Radius"].default_value = (1.0, 0.3, 0.2)
    b.inputs["Subsurface Scale"].default_value = 0.05
    # bump: muscle fibres + fine skin noise
    bump_h = _math(N, L, "MULTIPLY", wv.outputs["Fac"], _math(N, L, "SUBTRACT", 1.0, skin))
    bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.35; bp.inputs["Distance"].default_value = 0.002
    L.new(bump_h, bp.inputs["Height"]); L.new(bp.outputs["Normal"], b.inputs["Normal"])
    return m


def _mat_simple(name, col, rough=0.5, emit=None, strength=0.0):
    m = bpy.data.materials.new(name)
    nt, N, L, b = _nodes(m)
    b.inputs["Base Color"].default_value = (*col, 1); b.inputs["Roughness"].default_value = rough
    if emit:
        b.inputs["Emission Color"].default_value = (*emit, 1); b.inputs["Emission Strength"].default_value = strength
    return m


def _mat_eye(name, iris, glow=0.0, white=(0.8, 0.78, 0.72), pupil=True, iris_r=0.55):
    """Eye ball facing -Y (object space normal). Iris disc + dark pupil, optional glow."""
    m = bpy.data.materials.new(name)
    nt, N, L, b = _nodes(m)
    tc = N.new("ShaderNodeTexCoord")
    sep = N.new("ShaderNodeSeparateXYZ"); L.new(tc.outputs["Normal"], sep.inputs[0])
    fy = _math(N, L, "MULTIPLY", sep.outputs["Y"], -1.0)
    ir = _mrange(N, L, fy, iris_r * 1.0 + 0.0, iris_r + 0.06)          # 0 outside iris, 1 inside
    pu = _mrange(N, L, fy, 0.93, 0.95)
    col = _mix(N, L, ir, white, iris)
    if pupil:
        col = _mix(N, L, pu, col, (0.01, 0.01, 0.01))
    ring = _mrange(N, L, fy, iris_r - 0.04, iris_r)
    ring2 = _mrange(N, L, fy, iris_r + 0.02, iris_r + 0.08, 1, 0)
    col = _mix(N, L, _math(N, L, "MULTIPLY", ring, ring2), col, (0.02, 0.02, 0.02))
    L.new(col, b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.08; b.inputs["Coat Weight"].default_value = 0.6
    if glow > 0:
        L.new(col, b.inputs["Emission Color"])
        b.inputs["Emission Strength"].default_value = glow
    return m


def _mat_hair(name, col, hi, root_dark=0.35, rough=0.4):
    m = bpy.data.materials.new(name)
    nt, N, L, b = _nodes(m)
    t = _attr(N, "sh_hairt").outputs["Fac"]
    lay = _attr(N, "sh_hairl").outputs["Fac"]
    base = _mix(N, L, _mrange(N, L, t, 0.0, 0.35), tuple(c * root_dark for c in col), col)
    # anime highlight band part-way down each lock
    band = _math(N, L, "MULTIPLY", _mrange(N, L, t, 0.12, 0.22), _mrange(N, L, t, 0.3, 0.42, 1, 0))
    base = _mix(N, L, _math(N, L, "MULTIPLY", band, 0.6), base, hi)
    base = _mix(N, L, _math(N, L, "MULTIPLY", lay, 0.5), base, tuple(c * 0.4 for c in col), "MIX")
    L.new(base, b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = rough
    b.inputs["Coat Weight"].default_value = 0.05
    return m


def _mat_teeth(name):
    m = bpy.data.materials.new(name)
    nt, N, L, b = _nodes(m)
    b.inputs["Base Color"].default_value = (0.66, 0.56, 0.43, 1)    # bible: teeth ~#d4c0ab
    b.inputs["Roughness"].default_value = 0.35
    b.inputs["Coat Weight"].default_value = 0.3
    b.inputs["Subsurface Weight"].default_value = 0.1
    return m


# ------------------------------------------------------------------ fibre coordinates + rest attr
def _fibre_coords(body, ctx):
    """sh_fib: (arc length around the dominant bone, distance along it, 0) so wave bands run along limbs."""
    me = body.data
    out = []
    for i, v in enumerate(me.vertices):
        bn = ctx.dom[i]
        p = v.co
        b = _base(bn)
        if b in ("neck01", "neck02", "neck03") or _is_head_bone(bn) or b in _TORSO:
            # torso / neck: fibres roughly along a fan from the sternum; use x + slight z shear
            a = math.atan2(p.x, -(p.y - 0.02))
            out.append((a * 0.12 + 0.15 * (p.z - 1.3) * p.x, p.z, 0.0))
        else:
            h, t = _bone_frame(ctx.rig, bn)
            tt, ang, r = ctx.limb(bn, p)
            ax = (t - h).length
            out.append((math.radians(ang) * max(r, 0.02), tt * ax, 0.0))
    _set_attr(me, "sh_fib", out, "FLOAT_VECTOR")
    _set_attr(me, "sh_rest", [tuple(v.co) for v in me.vertices], "FLOAT_VECTOR")


def _eye_mask(body, eyes, rx, rz, soft, below=0.0, outer=0.0, name="sh_eye"):
    """Dark eye-surround mask: ellipse around each eye (+ optional drop below / to the outside)."""
    me = body.data
    vals = []
    for v in me.vertices:
        p = v.co; m = 0.0
        if p.y < eyes["L"][0].y + 0.04:
            for s in ("L", "R"):
                c = eyes[s][0]
                dx = (p.x - c.x); dz = (p.z - c.z)
                sgn = 1 if c.x > 0 else -1
                ox = dx * sgn
                ex = rx + (outer if ox > 0 else 0.0)
                ez = rz + (below if dz < 0 else 0.0)
                d = math.sqrt((dx / ex) ** 2 + (dz / ez) ** 2)
                m = max(m, 1.0 - _ss(1.0 - soft, 1.0, d))
        vals.append(m)
    _set_attr(me, name, vals)
    return vals


def _hairline(ctx, front=0.045, back=-0.015, nape=None):
    """Mask function: hair above a line that sits `front` above the eyes at the forehead, `back` at the sides."""
    e = ctx.eye
    def f(p, hc):
        k = _ss(-0.06, -0.1, p.y)                     # 1 at the forehead, 0 from the temples back
        zl = e.z + back + (front - back) * k
        if nape is not None and p.y > 0.0:
            zl = min(zl, e.z + nape)
        return _ss(zl, zl + 0.008, p.z)
    return f


def _hair_mask(body, ctx, hairline):
    """sh_hair: 1 on the scalp (paint the scalp the hair colour so gaps between locks never show skin)."""
    me = body.data
    hc = ctx.B["head"].head_local
    vals = []
    for v in me.vertices:
        p = v.co
        if not _is_head_bone(ctx.dom[v.index]) and _base(ctx.dom[v.index]) not in ("neck03",):
            vals.append(0.0); continue
        vals.append(hairline(p, hc))
    _set_attr(me, "sh_hair", vals)


# ------------------------------------------------------------------ eyes
def _add_eyes(rig, body, eyes, mat, scale=1.0, push=0.0, squash=1.0):
    objs = []
    for s in ("L", "R"):
        c, r = eyes[s]
        r *= 0.92 * scale
        bm = bmesh.new()
        bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=16, radius=r)
        for v in bm.verts:
            v.co.z *= squash
        bmesh.ops.translate(bm, verts=bm.verts, vec=c + Vector((0, push, 0)))
        me = bpy.data.meshes.new(f"{rig.name}_eye{s}")
        bm.to_mesh(me); bm.free()
        ob = bpy.data.objects.new(me.name, me)
        bpy.context.scene.collection.objects.link(ob)
        for p in me.polygons:
            p.use_smooth = True
        me.materials.append(mat)
        _skin_to_rig(ob, rig, {"head": 1.0})
        objs.append(ob)
    return objs


# ------------------------------------------------------------------ anime lock hair
def _head_bvh(body, ctx, skip_ears=False):
    """BVH of the head/neck part of the body (rest pose)."""
    me = body.data
    keep = set(i for i in range(len(me.vertices))
               if _is_head_bone(ctx.dom[i]) or _base(ctx.dom[i]) in ("neck01", "neck02", "neck03"))
    if skip_ears and "ears" in body.vertex_groups:
        gi = body.vertex_groups["ears"].index
        keep -= {v.index for v in me.vertices for g in v.groups if g.group == gi and g.weight > 0.2}
    verts = [v.co.copy() for v in me.vertices]
    polys = [tuple(p.vertices) for p in me.polygons if all(i in keep for i in p.vertices)]
    return BVHTree.FromPolygons(verts, polys)


def _make_hair(rig, body, ctx, name, locks, mat, seed=1, cap=0.0, skip_ears=False, cap_noise=0.0):
    """locks: list of dicts {az, el, len, w, droop, out, curl, sweep, thick}.
    az: azimuth (0 = front/-Y, +90 = character's left/+X), el: polar angle of the root from the crown (deg)."""
    rnd = random.Random(seed)
    bvh = _head_bvh(body, ctx, skip_ears)
    hb = ctx.B["head"]
    hm = body.data.attributes.get("sh_hair")
    hmask = [d.value for d in hm.data] if hm else None
    kd_bvh = BVHTree.FromPolygons([v.co.copy() for v in body.data.vertices], [tuple(p.vertices) for p in body.data.polygons])
    c = hb.head_local.lerp(hb.tail_local, 0.42) + Vector((0, 0.012, 0))
    verts, faces, tval, lval = [], [], [], []
    NS = 6
    for li, lk in enumerate(locks):
        az, el = math.radians(lk["az"]), math.radians(lk["el"])
        d0 = Vector((math.sin(el) * math.sin(az), -math.sin(el) * math.cos(az), math.cos(el)))
        hit = bvh.ray_cast(c + d0 * 0.4, -d0, 0.8)
        if hit[0] is None:
            continue
        if lk.get("in_hairline") and hmask is not None:
            loc2, n2, pi, dd2 = kd_bvh.find_nearest(hit[0])
            if pi is None or sum(hmask[i] for i in body.data.polygons[pi].vertices) / len(body.data.polygons[pi].vertices) < 0.6:
                continue
        root = hit[0] + hit[1] * lk.get("lift", 0.002)
        # initial growth direction: tangent pointing away from the crown, blended with 'out'
        el2 = el + 0.2
        d1 = Vector((math.sin(el2) * math.sin(az), -math.sin(el2) * math.cos(az), math.cos(el2)))
        tang = (d1 - d0); tang -= hit[1] * tang.dot(hit[1]); tang.normalize()
        if "dir" in lk:
            dv = Vector(lk["dir"]); dv -= hit[1] * dv.dot(hit[1])
            if dv.length > 1e-4:
                tang = dv.normalized()
        sweep = lk.get("sweep", 0.0)
        if abs(sweep) > 1e-4:
            side = hit[1].cross(tang).normalized()
            tang = (tang + side * sweep).normalized()
        hn = hit[1] if hit[1].dot(hit[0] - c) > 0 else -hit[1]
        dirv = (tang + hn * lk.get("out", 0.1)).normalized()
        L = lk["len"]; n = max(6, int(L / 0.008) + 3)
        ds = L / n
        pts = [root]
        p = root.copy()
        offs = lk.get("off", 0.006)
        for k in range(1, n + 1):
            f = k / n
            g = lk.get("droop", 1.0) * (0.3 + 1.0 * f)
            dirv = (dirv + Vector((0, 0, -g * ds * 30))).normalized()
            if lk.get("curl", 0):
                dirv = (dirv + hn * lk["curl"] * f * ds * 30).normalized()
            dirv += Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1))) * lk.get("jitter", 0.05)
            dirv.normalize()
            pn = p + dirv * ds
            loc, nrm, idx, dd = bvh.find_nearest(pn, 0.2)
            want = offs + lk.get("vol", 0.004) * f
            if loc is not None:
                if nrm.dot(loc - c) < 0:
                    nrm = -nrm
                dv = pn - loc
                hgt = dv.dot(nrm)
                cl = lk.get("cling", 0.012)       # locks hug the skull up to this height, then hang free
                tip = want + lk.get("tip", 0.0) * f ** 2
                if hgt < want:
                    pn = loc + nrm * want
                    if dirv.dot(nrm) < 0:
                        dirv = (dirv - nrm * dirv.dot(nrm)).normalized()
                elif hgt > tip and hgt < tip + cl:
                    pn = loc + nrm * tip
                    dirv = (dirv - nrm * dirv.dot(nrm)).normalized()
            p = pn
            pts.append(p.copy())
        # sweep a lens-shaped section
        w0 = lk["w"]; th = lk.get("thick", 0.35)
        base_i = len(verts)
        for k, q in enumerate(pts):
            f = k / (len(pts) - 1)
            T = (pts[min(k + 1, len(pts) - 1)] - pts[max(k - 1, 0)]).normalized()
            loc, nrm, idx, dd = bvh.find_nearest(q, 0.5)
            out = (q - loc).normalized() if loc is not None else (q - c).normalized()
            S = T.cross(out).normalized()
            Nn = S.cross(T).normalized()
            wf = w0 * min(1.0, 0.6 + f * 4) * (1 - f ** lk.get("taper", 2.0)) if k < len(pts) - 1 else 0.0
            for j in range(NS):
                a = 2 * math.pi * j / NS
                verts.append(q + S * (math.cos(a) * wf) + Nn * (math.sin(a) * wf * th))
                tval.append(f); lval.append(lk.get("layer", 0.0))
        for k in range(len(pts) - 1):
            for j in range(NS):
                a0 = base_i + k * NS + j; a1 = base_i + k * NS + (j + 1) % NS
                faces.append((a0, a1, a1 + NS, a0 + NS))
        # cap the root
        faces.append(tuple(base_i + j for j in range(NS))[::-1])
    if cap:
        # hair 'cap': the hair-masked scalp faces, lifted off the head, under the locks
        me = body.data
        hm = me.attributes["sh_hair"].data
        vin = [hm[i].value > 0.5 for i in range(len(me.vertices))]
        remap = {}
        for p in me.polygons:
            if all(vin[i] for i in p.vertices):
                ids = []
                for i in p.vertices:
                    if i not in remap:
                        v = me.vertices[i]
                        remap[i] = len(verts)
                        hh = cap * (0.6 + rnd.random() ** 2 * cap_noise)
                        verts.append(v.co + v.normal * hh + Vector((0, 0, hh * 0.3)))
                        tval.append(0.15 + 0.25 * rnd.random()); lval.append(0.5 * rnd.random())
                    ids.append(remap[i])
                faces.append(tuple(ids))
    ob = _new_obj(name, verts, faces)
    _set_attr(ob.data, "sh_hairt", tval)
    _set_attr(ob.data, "sh_hairl", lval)
    ob.data.materials.append(mat)
    _skin_to_rig(ob, rig, {"head": 1.0})
    return ob


def _lock_ring(az0, az1, n, el, length, w, rnd, **kw):
    out = []
    for i in range(n):
        az = az0 + (az1 - az0) * (i + rnd.uniform(-0.3, 0.3)) / max(1, n - 1 if n > 1 else 1)
        d = dict(az=az, el=el + rnd.uniform(-3, 3), len=length(az) * rnd.uniform(0.88, 1.1), w=w * rnd.uniform(0.85, 1.15))
        d.update(kw)
        out.append(d)
    return out


# ------------------------------------------------------------------ finishing
def _finish(rig, body, kind, mats):
    me = body.data
    me.materials.clear()
    for m in mats:
        me.materials.append(m)
    for p in me.polygons:
        p.material_index = 0; p.use_smooth = True
    top = max(v.co.z for v in me.vertices); bot = min(v.co.z for v in me.vertices)
    s = HEIGHT[kind] / (top - bot)
    rig.scale = (s, s, s)
    rig["shifter"] = kind
    rig["unit_scale"] = s
    return s


def relax(rig, arm=0.8, back=-0.3, elbow=0.25):
    titans.relax_pose(rig, arm=arm, back=back)
    P = rig.pose.bones
    for side in ("L", "R"):
        b = P.get(f"lowerarm01.{side}")
        if b:
            b.rotation_mode = "XYZ"; b.rotation_euler.x = elbow


# ================================================================== ARMORED
def _armored_rule(ctx, bn, p, n):
    b = _base(bn); s = "L" if p.x >= 0 else "R"
    z = ctx.z
    if _is_head_bone(bn) or b == "neck03":
        return _armored_head(ctx, p, n, s)
    if b in ("neck01", "neck02"):
        # ribbed horizontal plates on the sides of the neck, striated muscle front and back
        return "M"
    if b == "clavicle":
        if p.z > z["clavicle.L"] + 0.004 and n.y > -0.5:
            return "trap" + s
        return "M" if abs(p.x) < 0.035 else "pec" + s
    if b in _TORSO:
        lat = abs(n.x) > 0.7
        if p.z > z["clavicle.L"] + 0.004 or (n.z > 0.55 and p.z > z["spine01"]):
            if abs(p.x) < 0.03 or (n.y < -0.2 and abs(p.x) < 0.07 and p.z > z["clavicle.L"] + 0.012):
                return "M"                                # neck base / jugular notch
            return "trap" + s                             # trapezius plates
        if n.y < -0.15:                                   # front
            if lat and p.z > z["upperleg01.L"] - 0.02:
                return "M"                                # outer flank strip, armpit to hip
            if abs(p.x) < 0.005 and p.z > z["spine02"]:
                return "M"                                # dark red seam between the pecs
            pec_bot = z["spine01"] - 0.035
            if p.z > pec_bot:
                return "pec" + s
            top_ab = pec_bot; bot_ab = z["upperleg01.L"] + 0.03
            if abs(p.x) > 0.072 and p.z > z["spine03"]:
                # serratus: 4 finger-like diagonal plates per side
                k = int((p.z - z["spine03"] - 0.35 * (abs(p.x) - 0.072)) / ((pec_bot - z["spine03"]) / 4))
                return f"ser{max(0, min(k, 3))}{s}"
            if p.z > bot_ab:
                if abs(p.x) > 0.075:
                    return "obl" + s
                fr = (top_ab - p.z) / (top_ab - bot_ab)
                if fr > 0.78:
                    return "ablow"                         # lower block
                return f"ab{min(int(fr / 0.26), 2)}{s}"    # 3 pairs
            if abs(p.x) > 0.06 and p.z > z["upperleg01.L"] - 0.05:
                return "M"                                 # inguinal crease
            return "groin"
        if lat and z["upperleg01.L"] < p.z < z["clavicle.L"] - 0.06:
            return "M"
        if p.z > z["spine02"]:
            return "ub" + s
        if p.z > z["upperleg01.L"] + 0.01:
            return "lb" + s
        return "glute" + s
    if b in _ARM:
        t, ang, r = ctx.limb(bn, p)
        inner = abs(ang + 90) < 55
        if b == "shoulder01":
            return "M" if inner and t > 0.4 else "delt" + s
        if b == "upperarm01":
            if inner:
                return "M"
            return "delt" + s if t < 0.6 else "ua" + s
        if b == "upperarm02":
            if t > 0.86:
                return "M"
            if inner:
                return "M" if t < 0.3 else "bic" + s
            return "ua" + s if abs(ang) > 70 else "uaf" + s
        if b == "lowerarm01":
            if t < 0.18:
                return "elb" + s if abs(ang) > 120 else "M"
            return ("fa1a" if ang >= -20 else "fa1b") + s
        if b == "lowerarm02":
            if t > 0.88:
                return "M"
            return ("fa2a" if ang >= -20 else "fa2b") + s
    if b == "wrist" or b.startswith("metacarpal"):
        return ("hand" if n.dot(Vector((0, 0, 1))) > -0.2 else "palm") + s
    if b.startswith("finger"):
        return bn
    if b in _LEG:
        t, ang, r = ctx.limb(bn, p)
        stripe = 62 < ang < 102
        if b == "upperleg01":
            if stripe:
                return "M"
            return "glute" + s if abs(ang) > 95 else "thf" + s
        if b == "upperleg02":
            if stripe:
                return "M"
            if t > 0.92:
                return "knee" + s if abs(ang) < 55 else "M"
            if -45 <= ang <= 62:
                return ("thf" if t < 0.55 else "thf2") + s
            if -140 <= ang < -45:
                return "thi" + s
            return "thb" + s
        if b == "lowerleg01":
            if stripe:
                return "M"
            if t < 0.12:
                return "knee" + s if abs(ang) < 55 else "M"
            if -70 <= ang <= 62:
                return "shin" + s
            return "calf" + s
        if b == "lowerleg02":
            if stripe and t < 0.6:
                return "M"
            if t > 0.9:
                return "M"
            if -70 <= ang <= 62:
                return "shin2" + s
            return "calf2" + s
    if b == "foot":
        return "foot" + s
    if b.startswith("toe"):
        return "toe" + s
    return "M"


_ARM_SEEDS = {   # (x, dz from eye centre) on the face, mirrored when x > 0
    "fh": (0.03, 0.065), "brow": (0.036, 0.02), "nose": (0.0, -0.02),
    "chk": (0.05, -0.035), "lip": (0.0, -0.06), "chin": (0.0, -0.11), "jaw": (0.05, -0.1),
}


def _armored_head(ctx, p, n, s):
    e = ctx.eye
    ex = abs(e.x)
    dx = abs(p.x); dz = p.z - e.z
    # eye slits: deep sockets
    for c in (ctx.eyes["L"][0], ctx.eyes["R"][0]):
        if ((p.x - c.x) / 0.018) ** 2 + ((p.z - c.z - 0.001) / 0.0075) ** 2 < 1.0 and p.y < c.y + 0.02:
            return "socket"
    if p.z < ctx.lips.z - 0.075 and p.y > ctx.lips.y + 0.03:
        return "M"                                         # under the jaw / throat
    front = p.y < ctx.lips.y + 0.075 and n.y < 0.1
    if dx > ctx.ear_x - 0.022 and abs(p.z - (e.z - 0.012)) < 0.045 and p.y > ctx.lips.y + 0.07:
        return "ear"
    if front and dx < 0.072:
        # cheek side strip of exposed muscle between mask and ear, from the temple to the jaw corner
        if dx > 0.056 and -0.09 < dz < 0.0:
            return "M"
        return _face_seed_label(Vector((p.x, 0, dz)), _ARM_SEEDS)
    if p.z > e.z + 0.03:
        return "scalp"
    if dz < -0.02:
        return "M" if p.y > ctx.lips.y + 0.04 else "jaw" + s
    return "M"


def make_armored(name="ArmoredTitan"):
    macro = dict(gender=1.0, muscle=1.0, weight=0.85, proportions=0.6, height=0.6, age=0.5)
    face = ([("head/head-rectangular", 1.0), ("head/head-square", 0.6), ("chin/chin-width-incr", 1.0),
             ("chin/chin-prominent-incr", 0.4), ("chin/chin-height-incr", 0.3), ("head/head-fat-decr", 0.4),
             ("nose/nose-scale-horiz-incr", 0.2), ("nose/nose-flaring-decr", 1.0), ("nose/nose-hump-incr", 0.5),
             ("nose/nose-nostrils-width-decr", 1.0), ("nose/nose-volume-decr", 0.4), ("nose/nose-point-width-decr", 0.6),
             ("mouth/mouth-scale-horiz-incr", 0.3), ("mouth/mouth-upperlip-volume-decr", 1.0),
             ("mouth/mouth-lowerlip-volume-decr", 1.0), ("forehead/forehead-trans-backward", 0.3),
             ("neck/neck-scale-horiz-incr", 1.0), ("neck/neck-scale-depth-incr", 0.8)]
            + _lr("cheek/{s}-cheek-bones-incr", 0.8) + _lr("cheek/{s}-cheek-volume-decr", 0.5)
            + _lr("eyes/{s}-eye-push1-in", 1.0) + _lr("eyes/{s}-eye-push2-in", 0.6)
            + [("eyebrows/eyebrows-trans-down", 0.6)] + [("eyebrows/eyebrows-angle-down", 0.5)]
            + [("torso/torso-scale-horiz-incr", 0.6), ("torso/torso-vshape-incr", 0.8),
               ("torso/torso-muscle-dorsi-incr", 1.0), ("torso/torso-muscle-pectoral-incr", 0.8),
               ("neck/neck-scale-vert-decr", 0.8), ("neck/measure-neck-circ-incr", 1.0)]
            + _lr("arms/{s}-upperarm-muscle-incr", 0.5) + _lr("arms/{s}-upperarm-shoulder-muscle-incr", 1.0))
    rig, body, eyes = _build_body(name, macro, face)
    labels, keys, ctx = _label_faces(body, rig, eyes, _armored_rule)
    inv = {v: k for k, v in keys.items()}
    plates = {i for k, i in keys.items() if k not in ("M", "socket")}
    plates_scalp = {keys[k] for k in ("scalp",) if k in keys}
    per = {}
    for k, i in keys.items():
        if k == "socket":
            continue
        if k in ("scalp", "ear"):
            per[i] = (0.0, 0.01, 0.0, 0.02)
        elif k.startswith("nk"):
            per[i] = (0.003, 0.004, 0.002, 0.008)
        elif k.startswith(("finger", "toe")):
            per[i] = (0.0025, 0.003, 0.0015, 0.006)
        elif k in ("fh", "browL", "browR", "nose", "lip", "chin", "chkL", "chkR", "chk2L", "chk2R", "jawL", "jawR",
                   "tmpL", "tmpR"):
            per[i] = (0.003, 0.004, 0.001, 0.015, 0.003)
        elif k.startswith(("finger", "toe", "hand", "palm", "foot")):
            per[i] = (0.003, 0.003, 0.002, 0.01, 0.004)
        else:
            per[i] = (0.008, 0.0045, 0.004, 0.03, 0.007)
    params = dict(h=0.008, w=0.0045, pillow=0.004, pw=0.03, sink=0.003, sw=0.006, edge=0.0045, per_label=per)
    vlab, dist = _relief(body, labels, plates, params)
    sock = keys.get("socket")
    if sock is not None:
        me = body.data
        for v in me.vertices:
            if vlab[v.index] == sock:
                v.co.y += 0.012 * _ss(0, 0.004, dist[v.index])
    _cavity(body)
    _fibre_coords(body, ctx)
    _eye_mask(body, eyes, 0.022, 0.011, 0.25)
    _hair_mask(body, ctx, _hairline(ctx, 0.04, 0.0, nape=-0.02))
    # design bible 3.5: plates khaki-ochre #9C8660, seams #3A3024, muscle #8A3A24 (rim #C55C30), gold plate edges
    body_mat = _mat_body(name + "_mat", (0.30, 0.215, 0.105), (0.25, 0.04, 0.018), (0.042, 0.030, 0.017),
                         plate_mode=True, skin_rough=0.35, skin_var=0.2, hair_col=(0.45, 0.42, 0.33),
                         eye_col=(0.0, 0.0, 0.0), eye_amt=1.0, cav_amt=0.7, fib_scale=260.0,
                         rim_col=(0.62, 0.48, 0.2), muscle_hi=(0.56, 0.11, 0.03))
    eye_mat = _mat_eye(name + "_eyes", (1, 0.94, 0.75), glow=6.0, white=(1, 0.94, 0.75), pupil=False)
    eobjs = _add_eyes(rig, body, eyes, eye_mat, scale=0.75, push=0.006, squash=0.38)
    # very short, slightly spiky crew cut: a hair cap plus a dense brush of short spikes standing up
    rnd = random.Random(3)
    locks = []
    for i in range(700):
        u = rnd.random()
        el = math.degrees(math.acos(1 - u * 1.22))
        az = rnd.uniform(-180, 180)
        locks.append(dict(az=az, el=el, len=rnd.uniform(0.008, 0.016), dir=(0, 0.35, 1.0),
                          w=rnd.uniform(0.0032, 0.0045), droop=-0.2, out=0.5, cling=0.0, in_hairline=True,
                          jitter=0.06, off=0.0015, vol=0.0, taper=1.0, thick=0.6, lift=0.0,
                          layer=rnd.uniform(0, 0.4)))
    hair = _make_hair(rig, body, ctx, name + "_hair", locks, cap=0.004, cap_noise=1.6, mat=
                      _mat_hair(name + "_hairmat", (0.52, 0.49, 0.4), (0.8, 0.78, 0.7), root_dark=0.35, rough=0.65))
    _finish(rig, body, "armored", [body_mat])
    relax(rig, arm=0.85, back=-0.15, elbow=0.2)
    return rig


# ================================================================== FEMALE
def _female_rule(ctx, bn, p, n):
    """Design bible 3.7 muscle map: red sleeves on the arms, red flanks, red belly strip with a 6-pack,
    red strips on the thighs, red outer shins; pale neck, chest, pelvis V, knees, hands, feet."""
    b = _base(bn); s = "L" if p.x >= 0 else "R"
    z = ctx.z
    if _is_head_bone(bn) or b == "neck03":
        return _female_head(ctx, p, n, s)
    if b in ("neck01", "neck02", "clavicle"):
        return "skin"
    if b in _TORSO:
        lat = abs(n.x) > 0.45
        if p.z > z["spine01"] + 0.05:
            return "M" if lat and p.z < z["clavicle.L"] - 0.03 else "skin"
        if lat and p.z > z["upperleg01.L"] - 0.01:
            return "M"                                    # flanks: armpit to hip
        if n.y < -0.1:
            if p.z > z["spine02"] + 0.045:
                return "skin"                             # breasts / chest
            z0 = z["upperleg01.L"] + 0.1                  # navel
            if p.z > z0 and abs(p.x) < 0.034 + 0.12 * (p.z - z0):
                # belly strip with a 6-pack: red blocks, thin pale tendon lines
                if abs(p.x) < 0.0035:
                    return "M"
                return "M"
            if abs(p.x) > 0.085 and p.z > z["upperleg01.L"] - 0.03:
                return "M"
            return "skin"
        if p.z > z["spine02"]:
            return "skin"
        return "M" if abs(p.x) > 0.04 and p.z > z["upperleg01.L"] + 0.02 else "skin"
    if b in _ARM:
        if b == "shoulder01":
            t, ang, r = ctx.limb(bn, p)
            return "skin" if (n.z > 0.75 and t < 0.25) else "M"
        return "M"
    if b == "wrist" or b.startswith("metacarpal"):
        return "skin"
    if b.startswith("finger"):
        return "bone"
    if b in _LEG:
        t, ang, r = ctx.limb(bn, p)
        if b == "upperleg01":
            return "skin" if (abs(ang) < 100 and n.y < 0.2) or abs(p.x) < 0.07 else "M"
        if b == "upperleg02":
            if t > 0.88:
                return "skin" if abs(ang) < 80 else "M"
            if t < 0.12 and -60 < ang < 50:
                return "skin"
            # long red strips separated by pale gaps: outer quad, front centre, inner
            if 32 < ang < 120 or -22 < ang < 16 or -112 < ang < -50:
                return "M"
            if abs(ang) >= 115:
                return "M"
            return "skin"
        if b == "lowerleg01":
            if t < 0.12:
                return "skin" if abs(ang) < 80 else "M"
            return "M" if ang > 25 else "skin"            # outer shin / calf red, inner pale
        if b == "lowerleg02":
            if t > 0.86:
                return "skin"
            return "M" if ang > 25 else "skin"
    if b == "foot" or b.startswith("toe"):
        return "skin" if p.x < 0 else ("M" if n.z > 0.5 or p.y > 0 else "skin")
    return "M"


def _female_head(ctx, p, n, s):
    return "skin"


def make_female(name="FemaleTitan"):
    macro = dict(gender=0.0, muscle=1.0, weight=0.42, proportions=1.0, height=0.8, age=0.45, cupsize=0.55, firmness=0.9)
    face = ([("head/head-oval", 0.7), ("head/head-fat-decr", 0.6), ("chin/chin-prominent-incr", 0.4),
             ("chin/chin-width-decr", 0.3), ("nose/nose-scale-vert-incr", 0.6), ("nose/nose-hump-incr", 0.5),
             ("nose/nose-point-width-decr", 0.4), ("nose/nose-trans-up", 0.2),
             ("mouth/mouth-upperlip-volume-incr", 0.3), ("mouth/mouth-lowerlip-volume-incr", 0.3),
             ("mouth/mouth-scale-horiz-decr", 0.2), ("neck/neck-scale-horiz-decr", 0.2)]
            + _lr("eyes/{s}-eye-height2-incr", 0.7) + _lr("eyes/{s}-eye-height1-incr", 0.4)
            + _lr("eyes/{s}-eye-corner1-up", 0.3)
            + [("eyebrows/eyebrows-trans-down", 0.4)]
            + _lr("cheek/{s}-cheek-volume-decr", 0.8) + _lr("cheek/{s}-cheek-bones-incr", 0.6)
            + [("torso/torso-scale-horiz-decr", 0.2), ("stomach/stomach-pregnant-decr", 1.0)]
            + _lr("legs/{s}-lowerleg-scale-vert-incr", 0.3) + _lr("legs/{s}-upperleg-scale-vert-incr", 0.2))
    rig, body, eyes = _build_body(name, macro, face)
    labels, keys, ctx = _label_faces(body, rig, eyes, _female_rule)
    plates = {i for k, i in keys.items() if k != "M"}
    bone_lab = keys.get("bone")
    per = {}
    for k, i in keys.items():
        if k == "face":
            per[i] = (0.0012, 0.003, 0.0, 0.01)
        elif k.startswith("hand"):
            per[i] = (0.0015, 0.003, 0.0, 0.01)
    params = dict(h=0.0025, w=0.006, pillow=0.002, pw=0.02, sink=0.0015, sw=0.006, edge=0.0025, per_label=per)
    vlab, dist = _relief(body, labels, plates, params)
    _cavity(body)
    _fibre_coords(body, ctx)
    # dark exposed-muscle rings around the eyes ("eye bags")
    _eye_mask(body, eyes, 0.019, 0.010, 0.3, below=0.035, outer=0.003)   # dark band under each eye, down the cheek
    _set_attr(body.data, "sh_alt", [1.0 if bone_lab is not None and vlab[i] == bone_lab else 0.0
                                    for i in range(len(body.data.vertices))])
    _hair_mask(body, ctx, lambda p, hc: _ss(ctx.eye.z + 0.045, ctx.eye.z + 0.06, p.z) + _ss(0.0, 0.03, p.y) * _ss(ctx.eye.z - 0.03, ctx.eye.z, p.z))
    # hardening zones: forearms + hands + nape
    me = body.data
    hv = []
    for i, v in enumerate(me.vertices):
        bb = _base(ctx.dom[i])
        hv.append(1.0 if bb in ("lowerarm01", "lowerarm02", "wrist") or bb.startswith(("metacarpal", "finger")) else 0.0)
    _set_attr(me, "sh_hard", hv)
    # design bible 3.7: skin #d9b49b, muscle #b8321f / fibres #e5734e, eye band #613f2d, bone fingers #ab9f8a
    body_mat = _mat_body(name + "_mat", (0.69, 0.46, 0.33), (0.48, 0.032, 0.014), (0.07, 0.015, 0.01),
                         skin_rough=0.5, skin_var=0.1, hair_col=(0.58, 0.44, 0.15), eye_col=(0.07, 0.025, 0.015),
                         eye_amt=0.9, cav_amt=0.6, fib_scale=230.0, harden=True, muscle_hi=(0.78, 0.17, 0.075),
                         alt_col=(0.6, 0.55, 0.45))
    eye_mat = _mat_eye(name + "_eyes", (0.12, 0.2, 0.3), glow=0.0, white=(0.75, 0.75, 0.72), iris_r=0.7)
    _add_eyes(rig, body, eyes, eye_mat, scale=1.05, push=-0.0035)
    # chin-length blond bob, long side-swept fringe over one eye (design bible 3.7)
    rnd = random.Random(7)
    locks = []
    for i in range(96):                     # outer shell: sides and back, falling to the jaw / nape
        az = -180 + 360 * (i + rnd.uniform(0, 1)) / 96
        if abs(az) < 42:
            continue
        locks.append(dict(az=az, el=rnd.uniform(28, 52), len=rnd.uniform(0.16, 0.19), w=rnd.uniform(0.022, 0.028),
                          droop=1.0, out=0.05, jitter=0.015, off=0.006, vol=0.012, taper=2.5, thick=0.25))
    for i in range(60):                     # crown layer on top
        az = rnd.uniform(-180, 180)
        if abs(az) < 30:
            continue
        locks.append(dict(az=az, el=rnd.uniform(4, 30), len=rnd.uniform(0.18, 0.22), w=0.028, droop=1.0, out=0.05,
                          jitter=0.015, off=0.01, vol=0.014, taper=2.5, thick=0.25, layer=0.25))
    for i in range(48):                     # fringe: from the crown forward, swept across to her left
        az = rnd.uniform(-50, 40)
        locks.append(dict(az=az, el=rnd.uniform(4, 34), len=rnd.uniform(0.13, 0.19), w=rnd.uniform(0.018, 0.024),
                          droop=0.8, out=0.08, sweep=0.45, jitter=0.03, off=0.009, vol=0.012, taper=1.6, thick=0.25))
    _make_hair(rig, body, ctx, name + "_hair", locks,
               _mat_hair(name + "_hairmat", (0.58, 0.44, 0.15), (0.74, 0.62, 0.3), root_dark=0.45, rough=0.55),
               skip_ears=True)
    _finish(rig, body, "female", [body_mat])
    relax(rig, arm=0.8, back=-0.2, elbow=0.3)
    return rig


def set_hardening(rig, amount=1.0):
    """Female Titan: crystal hardening on forearms/hands (0 = off, 1 = full)."""
    for ob in rig.children:
        for m in ob.data.materials if ob.type == "MESH" else []:
            if m and m.node_tree and "Hardening" in m.node_tree.nodes:
                m.node_tree.nodes["Hardening"].outputs[0].default_value = amount


# ================================================================== ATTACK
def _attack_rule(ctx, bn, p, n):
    if _is_head_bone(bn) or _base(bn) == "neck03":
        for c in (ctx.eyes["L"][0], ctx.eyes["R"][0]):
            pass
        sl = _attack_slit(ctx, p)
        if sl:
            return "slit"
    return "skin"


def _attack_slit(ctx, p):
    """Cheekless mouth: a slit from the mouth corner back towards the ear, through which the teeth show."""
    lz = ctx.lips.z
    dx = abs(p.x)
    if p.y > ctx.lips.y + 0.075:
        return False
    x0, x1 = 0.0, ctx.ear_x - 0.022
    if not (x0 < dx < x1):
        return False
    f = (dx - x0) / (x1 - x0)
    zc = lz + 0.001 + 0.008 * f ** 1.5
    hh = 0.0105 * (1 - f) ** 0.5 + 0.003
    return abs(p.z - zc) < hh


def _attack_teeth(rig, body, ctx, name):
    """Two rows of rounded teeth following the face surface along the slit."""
    me = body.data
    bvh = BVHTree.FromPolygons([v.co.copy() for v in me.vertices], [tuple(p.vertices) for p in me.polygons])
    lz = ctx.lips.z
    x1 = ctx.ear_x - 0.026
    verts, faces = [], []
    mat_idx = []
    def box(c, X, Y, Z, w, h, d):
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)
        for v in bm.verts:
            q = v.co
            # rounded tooth: taper the biting end
            v.co = c + X * (q.x * w * (1 - 0.25 * abs(q.z * 2) ** 2)) + Z * (q.z * h) + Y * (q.y * d)
        i0 = len(verts)
        bm.verts.ensure_lookup_table()
        for v in bm.verts:
            verts.append(v.co.copy())
        for f in bm.faces:
            faces.append(tuple(i0 + v.index for v in f.verts))
        bm.free()
    for sgn in (1, -1):
        for row in (1, -1):
            x = 0.004
            k = 0
            while x < x1:
                f = x / x1
                tw = 0.0072 * (1 - 0.3 * f)
                th = 0.0115 * (1 - 0.4 * f)
                zc = lz + 0.001 + 0.008 * (x / (ctx.ear_x - 0.022)) ** 1.5 + row * th * 0.5
                origin = Vector((sgn * (x + tw / 2), -0.3, zc))
                hit = bvh.ray_cast(origin, Vector((0, 1, 0)), 0.5)
                if hit[0] is None:
                    break
                nrm = hit[1].copy(); nrm.z = 0; nrm.normalize()
                if nrm.dot(Vector((hit[0].x, hit[0].y + 0.05, 0))) < 0:
                    nrm = -nrm
                Y = -nrm
                X = Vector((0, 0, 1)).cross(Y).normalized()
                c = hit[0] + nrm * 0.003
                box(c, X, Y, Vector((0, 0, 1)), tw * 0.96, th * 0.97, 0.0065)
                x += tw
                k += 1
    ob = _new_obj(name, verts, faces)
    for p in ob.data.polygons:
        p.use_smooth = False
    bv = ob.modifiers.new("round", "BEVEL"); bv.width = 0.0012; bv.segments = 2; bv.limit_method = "NONE"
    ob.data.materials.append(_mat_teeth(name + "_mat"))
    _skin_to_rig(ob, rig, {"head": 1.0})
    return ob


def _elf_ears(body, rig):
    """Long pointed ears sweeping up and back, tip near the top of the skull (~1/3 head height)."""
    g = body.vertex_groups.get("ears")
    if not g:
        return
    gi = g.index
    me = body.data
    ear = [(v, x.weight) for v in me.vertices for x in v.groups if x.group == gi and x.weight > 0.05]
    zs = [v.co.z for v, w in ear if w > 0.5]
    z0, z1 = min(zs), max(zs)
    zm = z0 + 0.45 * (z1 - z0)
    for v, w in ear:
        h = max(0.0, v.co.z - zm) / (z1 - zm)
        k = w * h ** 1.6
        v.co.z += k * 0.07
        v.co.y += k * 0.035
        v.co.x += math.copysign(k * 0.012, v.co.x)


def make_attack(name="AttackTitan"):
    macro = dict(gender=1.0, muscle=1.0, weight=0.5, proportions=1.0, height=0.7, age=0.4)
    face = ([("head/head-fat-decr", 0.8), ("head/head-oval", 0.4), ("chin/chin-prominent-incr", 0.5),
             ("chin/chin-width-incr", 0.4), ("nose/nose-scale-vert-incr", 0.4), ("nose/nose-hump-incr", 0.3),
             ("mouth/mouth-upperlip-volume-decr", 1.0), ("mouth/mouth-lowerlip-volume-decr", 1.0),
             ("mouth/mouth-scale-horiz-incr", 0.5), ("forehead/forehead-nubian-incr", 0.4),
             ("neck/neck-scale-horiz-incr", 0.4)]
            + _lr("cheek/{s}-cheek-volume-decr", 1.0) + _lr("cheek/{s}-cheek-bones-incr", 0.9)
            + _lr("cheek/{s}-cheek-inner-decr", 0.6)
            + _lr("eyes/{s}-eye-push1-in", 0.8) + _lr("eyes/{s}-eye-push2-in", 0.5)
            + [("eyebrows/eyebrows-trans-down", 0.8), ("eyebrows/eyebrows-angle-down", 0.8)]
            + _lr("ears/{s}-ear-shape-pointed", 1.0) + _lr("ears/{s}-ear-scale-vert-incr", 0.7)
            + _lr("ears/{s}-ear-rot-backward", 0.4) + _lr("ears/{s}-ear-flap-incr", 0.5)
            + [("torso/torso-vshape-incr", 0.8), ("torso/torso-muscle-pectoral-incr", 0.8),
               ("torso/torso-muscle-dorsi-incr", 0.6), ("stomach/stomach-tone-incr", 1.0)]
            + _lr("arms/{s}-upperarm-muscle-incr", 0.8) + _lr("arms/{s}-lowerarm-muscle-incr", 0.6)
            + _lr("arms/{s}-upperarm-shoulder-muscle-incr", 0.7) + _lr("arms/{s}-lowerarm-scale-vert-incr", 0.2)
            + _lr("legs/{s}-upperleg-muscle-incr", 0.6) + _lr("legs/{s}-lowerleg-muscle-incr", 0.5))
    rig, body, eyes = _build_body(name, macro, face, pre_sub=_elf_ears)
    labels, keys, ctx = _label_faces(body, rig, eyes, _attack_rule)
    plates = {keys["skin"]}
    params = dict(h=0.0, w=0.004, sink=0.008, sw=0.003, edge=0.0016)
    vlab, dist = _relief(body, labels, plates, params)
    _cavity(body, gain=22.0)
    _fibre_coords(body, ctx)
    _eye_mask(body, eyes, 0.024, 0.013, 0.5, below=0.006, outer=0.008)
    _hair_mask(body, ctx, lambda p, hc: _ss(ctx.eye.z + 0.04, ctx.eye.z + 0.055, p.z) + _ss(0.0, 0.03, p.y) * _ss(ctx.eye.z - 0.02, ctx.eye.z + 0.01, p.z))
    # design bible 3.6: skin albedo #a5806a (warm reddish), hair #2a2019, eyes glow #74a06a / core #b8e0a0
    body_mat = _mat_body(name + "_mat", (0.36, 0.19, 0.12), (0.06, 0.01, 0.008), (0.03, 0.01, 0.007),
                         skin_rough=0.62, skin_var=0.15, hair_col=(0.023, 0.014, 0.01), eye_col=(0.03, 0.01, 0.008),
                         eye_amt=0.85, cav_amt=1.0)
    eye_mat = _mat_eye(name + "_eyes", (0.17, 0.35, 0.14), glow=4.0, white=(0.45, 0.5, 0.4), iris_r=0.6)
    _add_eyes(rig, body, eyes, eye_mat)
    _attack_teeth(rig, body, ctx, name + "_teeth")
    # messy black hair grazing the shoulders, heavy fringe and strands across the face (design bible 3.6)
    rnd = random.Random(11)
    locks = []
    for i in range(100):
        az = -180 + 360 * (i + rnd.uniform(0, 1)) / 100
        if abs(az) < 42:
            continue
        locks.append(dict(az=az, el=rnd.uniform(26, 55), len=rnd.uniform(0.19, 0.26), w=rnd.uniform(0.016, 0.024),
                          droop=1.0, out=0.08, jitter=0.05, off=0.007, vol=0.016, taper=1.5, thick=0.25, curl=0.04))
    for i in range(60):
        az = rnd.uniform(-180, 180)
        if abs(az) < 30:
            continue
        locks.append(dict(az=az, el=rnd.uniform(3, 28), len=rnd.uniform(0.2, 0.26), w=0.022, droop=1.0, out=0.08,
                          jitter=0.05, off=0.011, vol=0.016, taper=1.5, thick=0.25, layer=0.25, curl=0.04))
    for i in range(34):
        az = rnd.uniform(-48, 48)
        locks.append(dict(az=az, el=rnd.uniform(8, 38), len=rnd.uniform(0.11, 0.19), w=rnd.uniform(0.01, 0.017),
                          droop=0.9, out=0.1, sweep=rnd.uniform(-0.35, 0.35), jitter=0.06, off=0.01, vol=0.012,
                          taper=1.3, thick=0.25))
    _make_hair(rig, body, ctx, name + "_hair", locks,
               _mat_hair(name + "_hairmat", (0.023, 0.014, 0.01), (0.25, 0.22, 0.2), root_dark=0.5, rough=0.6),
               skip_ears=True)
    _finish(rig, body, "attack", [body_mat])
    relax(rig, arm=0.8, back=-0.25, elbow=0.35)
    return rig
