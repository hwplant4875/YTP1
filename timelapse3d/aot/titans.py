"""Titan builder (MPFB2 / MakeHuman CC0 base mesh + default rig), for Blender 5.2 with the MPFB extension.

make_titan(kind, ...) returns the armature object; the body mesh is parented to it.
Kinds: pure, colossal, armored, attack, female.
"""
import bpy, importlib, math, random
from mathutils import Vector

def _find_mpfb():
    """MPFB lives in a different extension repo on the cloud box (user_default) and the laptop (blender_org)."""
    for m in ("bl_ext.user_default.mpfb", "bl_ext.blender_org.mpfb"):
        try:
            importlib.import_module(m)
            return m
        except ImportError:
            pass
    return "bl_ext.user_default.mpfb"
_mp = _find_mpfb()
HS = importlib.import_module(_mp + ".services.humanservice").HumanService
TS = importlib.import_module(_mp + ".services.targetservice").TargetService
ASSET = importlib.import_module(_mp + ".services.assetservice").AssetService

def _bake_and_clean(body):
    if body.data.shape_keys:
        TS.bake_targets(body)
    # delete helper geometry hidden by the mask modifier
    mask = next((m for m in body.modifiers if m.type == "MASK"), None)
    if mask:
        vg = body.vertex_groups.get(mask.vertex_group)
        keep = set()
        if vg:
            for v in body.data.vertices:
                for g in v.groups:
                    if g.group == vg.index and g.weight > 0.5:
                        keep.add(v.index)
        inv = mask.invert_vertex_group
        import bmesh
        bm = bmesh.new(); bm.from_mesh(body.data); bm.verts.ensure_lookup_table()
        dele = [v for v in bm.verts if ((v.index in keep) == inv)]
        bmesh.ops.delete(bm, geom=dele, context="VERTS")
        bm.to_mesh(body.data); bm.free()
        body.modifiers.remove(mask)

def _mat_skin(name, color, sss=0.15, rough=0.55):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Subsurface Weight"].default_value = sss
    b.inputs["Subsurface Radius"].default_value = (1.0, 0.35, 0.2)
    b.inputs["Subsurface Scale"].default_value = 0.5
    tc = nt.nodes.new("ShaderNodeTexCoord"); nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 3.0; nz.inputs["Detail"].default_value = 6
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.blend_type = "MULTIPLY"; mx.inputs["Factor"].default_value = 0.25
    mx.inputs["A"].default_value = (*color, 1)
    nt.links.new(nz.outputs["Color"], mx.inputs["B"]); nt.links.new(mx.outputs["Result"], b.inputs["Base Color"])
    return m

def _mat_muscle(name):
    """Skinless Colossal Titan: wet red muscle fibres with pale tendon patches."""
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; N = nt.nodes; L = nt.links; b = N["Principled BSDF"]
    tc = N.new("ShaderNodeTexCoord")
    wv = N.new("ShaderNodeTexWave"); wv.wave_type = "BANDS"; wv.bands_direction = "Z"
    wv.inputs["Scale"].default_value = 60; wv.inputs["Distortion"].default_value = 14; wv.inputs["Detail"].default_value = 6
    wv.inputs["Detail Scale"].default_value = 2.0
    L.new(tc.outputs["Object"], wv.inputs["Vector"])
    rp = N.new("ShaderNodeValToRGB"); e = rp.color_ramp.elements
    e[0].position, e[0].color = 0.1, (0.20, 0.018, 0.014, 1)
    e[1].position, e[1].color = 0.9, (0.42, 0.05, 0.04, 1)
    L.new(wv.outputs["Fac"], rp.inputs["Fac"])
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 2.2; nz.inputs["Detail"].default_value = 5
    L.new(tc.outputs["Object"], nz.inputs["Vector"])
    tm = N.new("ShaderNodeMapRange"); tm.inputs["From Min"].default_value = 0.68; tm.inputs["From Max"].default_value = 0.72
    L.new(nz.outputs["Fac"], tm.inputs["Value"])
    mx = N.new("ShaderNodeMix"); mx.data_type = "RGBA"
    L.new(tm.outputs["Result"], mx.inputs["Factor"]); L.new(rp.outputs["Color"], mx.inputs["A"])
    mx.inputs["B"].default_value = (0.75, 0.6, 0.48, 1)
    L.new(mx.outputs["Result"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.28
    b.inputs["Coat Weight"].default_value = 0.3
    b.inputs["Subsurface Weight"].default_value = 0.2; b.inputs["Subsurface Radius"].default_value = (1, 0.2, 0.1)
    bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.35
    L.new(wv.outputs["Fac"], bp.inputs["Height"]); L.new(bp.outputs["Normal"], b.inputs["Normal"])
    return m

def _mat_armor(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; N = nt.nodes; L = nt.links; b = N["Principled BSDF"]
    tc = N.new("ShaderNodeTexCoord")
    vo = N.new("ShaderNodeTexVoronoi"); vo.feature = "DISTANCE_TO_EDGE"; vo.inputs["Scale"].default_value = 4.5
    L.new(tc.outputs["Object"], vo.inputs["Vector"])
    mr = N.new("ShaderNodeMapRange"); mr.inputs["From Min"].default_value = 0.0; mr.inputs["From Max"].default_value = 0.05
    L.new(vo.outputs["Distance"], mr.inputs["Value"])
    mx = N.new("ShaderNodeMix"); mx.data_type = "RGBA"
    L.new(mr.outputs["Result"], mx.inputs["Factor"])
    mx.inputs["A"].default_value = (0.18, 0.14, 0.1, 1); mx.inputs["B"].default_value = (0.78, 0.72, 0.6, 1)
    L.new(mx.outputs["Result"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.45
    bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.8
    L.new(mr.outputs["Result"], bp.inputs["Height"]); L.new(bp.outputs["Normal"], b.inputs["Normal"])
    return m

def _mat_teeth(name):
    """Lipless mouth: vertical tooth stripes with a dark bite line."""
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; N = nt.nodes; L = nt.links; b = N["Principled BSDF"]
    tc = N.new("ShaderNodeTexCoord")
    wv = N.new("ShaderNodeTexWave"); wv.wave_type = "BANDS"; wv.bands_direction = "X"; wv.inputs["Scale"].default_value = 26
    wv.inputs["Distortion"].default_value = 0.3
    L.new(tc.outputs["Object"], wv.inputs["Vector"])
    rp = N.new("ShaderNodeValToRGB"); e = rp.color_ramp.elements
    e[0].position, e[0].color = 0.08, (0.06, 0.02, 0.015, 1)
    e[1].position, e[1].color = 0.22, (0.82, 0.76, 0.62, 1)
    L.new(wv.outputs["Fac"], rp.inputs["Fac"])
    b.inputs["Roughness"].default_value = 0.3
    L.new(rp.outputs["Color"], b.inputs["Base Color"])
    return m

def _mat_socket(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (0.03, 0.006, 0.005, 1); b.inputs["Roughness"].default_value = 0.6
    return m

def _group_center(body, gname):
    g = body.vertex_groups.get(gname)
    if not g:
        return None
    pts = [v.co for v in body.data.vertices for x in v.groups if x.group == g.index and x.weight > 0.5]
    if not pts:
        return None
    c = Vector((0, 0, 0))
    for p in pts:
        c += p
    return c / len(pts), pts

def _face_regions(body, kind, name):
    """Assign teeth and dark eye-socket materials around the mouth and eyes (Colossal / Attack Titan)."""
    lips = _group_center(body, "lips")
    if not lips:
        return
    c, pts = lips
    xs = [p.x for p in pts]; zs = [p.z for p in pts]
    hw = (max(xs) - min(xs)) / 2 * (3.0 if kind == "colossal" else 1.3)
    hh = (max(zs) - min(zs)) / 2 * (1.6 if kind == "colossal" else 1.0)
    body.data.materials.append(_mat_teeth(name + "_teeth")); ti = len(body.data.materials) - 1
    body.data.materials.append(_mat_socket(name + "_socket")); si = len(body.data.materials) - 1
    eyes = [e for e in (_group_center(body, "orbicularis03.L"), _group_center(body, "orbicularis03.R")) if e]
    print("eyes found", len(eyes))
    me = body.data
    for p in me.polygons:
        q = p.center
        if q.y < c.y + 0.02 and ((q.x - c.x) / hw) ** 2 + ((q.z - c.z) / hh) ** 2 < 1.0:
            p.material_index = ti
        for ec, _ in eyes:
            if (q - ec).length < (0.03 if kind == "colossal" else 0.018):
                p.material_index = si

def _mat_hair(name, color):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1); b.inputs["Roughness"].default_value = 0.6
    return m

PRESETS = {
    #            height  macro overrides                                                skin                head
    "pure":     (7.0,  dict(gender=1.0, muscle=0.2, weight=0.7, proportions=0.2),       (0.62, 0.42, 0.33), 1.25),
    "colossal": (60.0, dict(gender=1.0, muscle=0.9, weight=0.15, proportions=0.9),      None,               1.0),
    "armored":  (15.0, dict(gender=1.0, muscle=1.0, weight=0.8, proportions=0.7),       (0.6, 0.42, 0.33),  0.95),
    "attack":   (15.0, dict(gender=1.0, muscle=0.9, weight=0.35, proportions=0.9),      (0.58, 0.40, 0.31), 1.0),
    "female":   (14.0, dict(gender=0.0, muscle=0.8, weight=0.35, proportions=1.0),      (0.66, 0.47, 0.38), 1.0),
}

import os
TDIR = os.path.join(os.path.dirname(importlib.import_module(_mp).__file__), "data", "targets")
LR = lambda t, w: [(t.format(s="l"), w), (t.format(s="r"), w)]
FACE = {
    # gaunt, skull-like, deep sockets, huge jaw, lipless mouth
    "colossal": [("head/head-rectangular", 1.0), ("head/head-fat-decr", 1.0), ("chin/chin-width-incr", 1.0),
                 ("chin/chin-prominent-incr", 0.8), ("chin/chin-height-incr", 0.7), ("mouth/mouth-scale-horiz-incr", 1.0),
                 ("mouth/mouth-upperlip-volume-decr", 1.0), ("mouth/mouth-lowerlip-volume-decr", 1.0),
                 ("nose/nose-scale-vert-decr", 0.8), ("nose/nose-scale-depth-decr", 1.0)]
                + LR("cheek/{s}-cheek-volume-decr", 1.0) + LR("cheek/{s}-cheek-bones-incr", 1.0)
                + LR("eyes/{s}-eye-push1-in", 1.0) + LR("eyes/{s}-eye-push2-in", 1.0),
    "attack":   [("head/head-fat-decr", 0.6), ("chin/chin-prominent-incr", 0.4), ("mouth/mouth-upperlip-volume-decr", 1.0),
                 ("mouth/mouth-lowerlip-volume-decr", 1.0), ("mouth/mouth-scale-horiz-incr", 0.6)]
                + LR("cheek/{s}-cheek-volume-decr", 0.9) + LR("cheek/{s}-cheek-bones-incr", 0.8)
                + LR("eyes/{s}-eye-push1-in", 0.7) + LR("ears/{s}-ear-shape-pointed", 1.0) + LR("ears/{s}-ear-scale-vert-incr", 0.6),
    "armored":  [("head/head-rectangular", 0.8), ("chin/chin-width-incr", 0.8), ("head/head-fat-decr", 0.3)],
    "female":   [("head/head-oval", 0.6), ("mouth/mouth-upperlip-volume-decr", 0.6)] + LR("eyes/{s}-eye-push1-in", 0.5)
                + LR("cheek/{s}-cheek-volume-decr", 0.6),
    "pure":     [],
}
PURE_FACE = [("mouth/mouth-scale-horiz-incr", (0.3, 1.0)), ("head/head-round", (0.0, 1.0)), ("head/head-fat-incr", (0.0, 1.0)),
             ("chin/chin-jaw-drop-incr", (0.0, 0.6)), ("mouth/mouth-scale-vert-decr", (0.0, 0.8))]

def _apply_face(body, kind, rnd):
    items = list(FACE.get(kind, []))
    if kind == "pure":
        items += [(t, rnd.uniform(*r)) for t, r in PURE_FACE]
        items += LR("eyes/{s}-eye-scale-" + rnd.choice(("incr", "decr")), rnd.uniform(0.2, 1.0))
    for t, w in items:
        p = os.path.join(TDIR, t + ".target.gz")
        if os.path.exists(p) and w > 0:
            TS.load_target(body, p, weight=w)
        else:
            print("missing target", t)

HAIR = {"armored": ("short02", (0.55, 0.42, 0.18)), "attack": ("long01", (0.03, 0.025, 0.02)),
        "female": ("bob02", (0.55, 0.42, 0.18))}

def make_titan(kind, name=None, height=None, seed=0, macro=None, head=None, skin=None):
    h0, mac, sk, hd = PRESETS[kind]
    height = height or h0
    rnd = random.Random(seed)
    md = TS.get_default_macro_info_dict()
    md.update(mac)
    if kind == "pure":
        md.update(dict(gender=rnd.choice((0.0, 1.0, 1.0)), weight=rnd.uniform(0.1, 1.0),
                       muscle=rnd.uniform(0.0, 0.5), proportions=rnd.uniform(0.0, 0.5), age=rnd.uniform(0.3, 1.0)))
        hd = rnd.uniform(1.15, 1.8)
    if macro:
        md.update(macro)
    body = HS.create_human(feet_on_ground=True, scale=0.1, macro_detail_dict=md)
    _apply_face(body, kind, rnd)
    rig = HS.add_builtin_rig(body, "default")
    name = name or f"Titan_{kind}_{seed}"
    TS.bake_targets(body)
    if kind in HAIR:
        hn, col = HAIR[kind]
        try:
            f = ASSET.find_asset_absolute_path(f"{hn}/{hn}.mhclo", asset_subdir="hair")
        except Exception:
            f = None
        if f:
            try:
                hair = HS.add_mhclo_asset(f, body, asset_type="Hair", subdiv_levels=0)
                hair.data.materials.clear(); hair.data.materials.append(_mat_hair(name + "_hair", col))
            except Exception as ex:
                print("hair failed", ex)
    _bake_and_clean(body)
    rig.name = name; body.name = name + "_body"
    body.data.materials.clear()
    if kind == "colossal":
        body.data.materials.append(_mat_muscle(name + "_muscle"))
    else:
        body.data.materials.append(_mat_skin(name + "_skin", skin or sk))
    for p in body.data.polygons:
        p.use_smooth = True
    if kind in ("colossal", "attack"):
        _face_regions(body, kind, name)
    if kind == "armored":
        shell = body.copy(); shell.data = body.data.copy(); shell.name = name + "_armor"
        bpy.context.scene.collection.objects.link(shell)
        sol = shell.modifiers.new("plates", "DISPLACE"); sol.strength = 0.012; sol.mid_level = 0
        shell.data.materials.clear(); shell.data.materials.append(_mat_armor(name + "_armor"))
    # head size
    pb = rig.pose.bones.get("head")
    if pb and hd != 1.0:
        pb.scale = (hd, hd, hd)
    s = height / 1.66
    rig.scale = (s, s, s)
    relax_pose(rig)
    return rig

def relax_pose(rig, arm=0.75, back=-0.45):
    """Arms down from the A-pose (local Z of upperarm01 lowers the arm)."""
    P = rig.pose.bones
    for side, sgn in (("L", -1), ("R", 1)):
        b = P.get(f"upperarm01.{side}")
        if b:
            b.rotation_mode = "XYZ"; b.rotation_euler.z = sgn * arm; b.rotation_euler.x = back
        b = P.get(f"lowerarm01.{side}")
        if b:
            b.rotation_mode = "XYZ"; b.rotation_euler.x = 0.25

def walk_pose(rig, phase, stride=0.45):
    """Simple walk cycle pose at phase (radians)."""
    P = rig.pose.bones
    sw = math.sin(phase) * stride
    for side, sgn in (("L", 1), ("R", -1)):
        if f"upperleg01.{side}" in P:
            P[f"upperleg01.{side}"].rotation_mode = "XYZ"; P[f"upperleg01.{side}"].rotation_euler.x = sw * sgn
        if f"lowerleg01.{side}" in P:
            P[f"lowerleg01.{side}"].rotation_mode = "XYZ"
            P[f"lowerleg01.{side}"].rotation_euler.x = max(0.0, -math.sin(phase * sgn + 0.6)) * 0.7
        if f"upperarm01.{side}" in P:
            P[f"upperarm01.{side}"].rotation_mode = "XYZ"; P[f"upperarm01.{side}"].rotation_euler.x = -sw * sgn * 0.8


def steam(name, center, size, density=0.6, noise_scale=2.5):
    """White titan steam: a box volume with noisy density that fades to the edges."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    st = bpy.context.active_object; st.name = name; st.scale = size
    sm = bpy.data.materials.new(name); sm.use_nodes = True; nt = sm.node_tree; N = nt.nodes; L = nt.links
    N.remove(N["Principled BSDF"])
    pv = N.new("ShaderNodeVolumePrincipled"); pv.inputs["Color"].default_value = (1, 1, 1, 1); pv.inputs["Anisotropy"].default_value = 0.3
    tc = N.new("ShaderNodeTexCoord"); nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = noise_scale
    nz.inputs["Detail"].default_value = 8
    L.new(tc.outputs["Generated"], nz.inputs["Vector"])
    gr = N.new("ShaderNodeTexGradient"); gr.gradient_type = "SPHERICAL"
    mp = N.new("ShaderNodeMapping"); mp.inputs["Location"].default_value = (-1, -1, -1); mp.inputs["Scale"].default_value = (2, 2, 2)
    L.new(tc.outputs["Generated"], mp.inputs["Vector"]); L.new(mp.outputs[0], gr.inputs["Vector"])
    mul = N.new("ShaderNodeMath"); mul.operation = "MULTIPLY"
    L.new(nz.outputs["Fac"], mul.inputs[0]); L.new(gr.outputs["Fac"], mul.inputs[1])
    mr = N.new("ShaderNodeMapRange"); mr.inputs["From Min"].default_value = 0.15; mr.inputs["From Max"].default_value = 0.4
    mr.inputs["To Max"].default_value = density
    L.new(mul.outputs[0], mr.inputs["Value"]); L.new(mr.outputs["Result"], pv.inputs["Density"])
    L.new(pv.outputs[0], N["Material Output"].inputs["Volume"]); st.data.materials.append(sm)
    return st
