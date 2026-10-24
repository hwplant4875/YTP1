"""Faceless people kit for the sky-view shots (plug-in for scene.py and a library for other plug-ins).

Figures read at 20-80 px tall, so recognition comes only from hair shape/colour, height/build and the
iconic outfit. Heads are smooth ovals: no eyes, nose, mouth or ears. Every figure is a cheap procedural
mesh (ellipsoids + capsules, one mesh per preset+pose with several material slots) with the same ink
hull as scene.py's figures (L.outline), plus an un-outlined decal mesh for the emblems.

Library use (from another plug-in):
    import people_kit as PK
    PK.person("erwin", (0, -20, 1.4), yaw=math.pi, pose="stand")       # returns the instance empty
    PK.crowd(["cadet"], (0, -38, 26, 14), 200, "salute", yaw=0.0, front=["mikasa", "armin"])
    PK.horse_only((x, y), yaw)                                         # riderless horse
    PK.drain(instances, waves=3, start=1, gap=48, dur=90, exit=(0, -60))  # H13 crowd drain keys

person(preset, loc, yaw=0.0, pose="stand", phase=0.0, scale=1.0, anchors=None, trail=True)
    preset  one of PRESETS (named characters) or a generic class name: cadet, garrison, scout, mp,
            civilian (each a pool of hair/height variants; "cadet:3" picks variant 3).
    loc     (x, y) puts the feet on the ground (scene terrain / district paving), (x, y, z) is absolute.
    yaw     radians, 0 = facing +y (north, toward the inner gate).
    pose    stand | walk | run | salute (right fist on the heart, left hand behind the back) |
            carry_kids (Hannes running with child Eren over his shoulder reaching back + Mikasa on his hip) |
            kneel | ride (on the kit's horse) | odm_fly (body pitched forward, blades back, two wires to
            `anchors` (world points, default ahead/up) and a gas trail behind).
crowd(preset_list, area, count, pose="stand", yaw=0.0, seed=1, spacing=None, formation="grid",
      jitter=0.15, front=(), phase_var=True)
    area = (cx, cy, width, depth[, rot]).  Instancing: every distinct preset+pose is built once into a
    hidden prototype collection; each figure is a collection-instance empty (200+ figures are cheap).
stage(loc, yaw, banner=True)   small wooden stage + Wings of Freedom banner + braziers + torches (H13/H14, R9).

Presets: erwin levi hannes carla grisha eren mikasa armin jean connie sasha reiner bertholdt christa ymir
annie marco pixis eren_child mikasa_child + generic cadet / garrison / scout / mp / civilian.
Uniform: tan cropped jacket, cream shirt, white trousers, dark hip wrap, brown knee boots, harness straps,
ODM hip units (gas cylinder + blade box) and back housing; emblems (procedural textures): cadet crossed
swords, Garrison twin roses, Scouts Wings of Freedom (over-sized, on the green hooded cape), MP unicorn.

As a plug-in (AOT_PLUGINS=people_kit) it builds its demo sets only for its own cameras:
  kit_lineup       all presets in two rows on the plaza, 25 m oblique from the south
  kit_lineup_back  the same rows from behind (capes, emblems, hair backs)
  kit_poses        every pose on the north side of the plaza
  kit_ceremony     H13/H14: 200 cadets saluting before a stage with Erwin, 40 m oblique, gate square
  kit_ceremony_hi  same set, 60 m higher crane view
Env: PK_INK (outline thickness m, default 0.022), PK_NIGHT=1 (torch-lit night for the ceremony),
     PK_DEMO=1 (build the demo sets for any camera).
"""
import bpy, bmesh, math, os, random
from mathutils import Vector, Matrix, Euler

import aotlib as L

INK = float(os.environ.get("PK_INK", "0.022"))
NIGHT = os.environ.get("PK_NIGHT", "0") == "1"

# ---------------------------------------------------------------- palette (sRGB hex from design_bible 4.6-4.8)
def srgb(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c)

COL = {
    "skin": ("#E8BC95", 0.55), "skin_pale": ("#F2D6C2", 0.55),
    "jacket": ("#A87454", 0.8), "shirt": ("#E6E2D8", 0.85), "trousers": ("#D2D0CC", 0.85),
    "wrap": ("#2E1C16", 0.8), "boots": ("#3A2218", 0.55), "harness": ("#4A2E20", 0.6),
    "cloak": ("#3F5E4C", 0.85), "steel": ("#9A9A94", 0.35), "steel_dark": ("#3A3A38", 0.4),
    "blade": ("#E0E0D8", 0.2), "white": ("#F0EEE8", 0.7), "hood_grey": ("#C8C8C4", 0.85),
    "scarf": ("#9E1E26", 0.7), "cravat": ("#F4F4F0", 0.6),
    # hair
    "h_erwin": ("#F2D97E", 0.45), "h_blond": ("#D9B866", 0.5), "h_armin": ("#E8CC78", 0.5),
    "h_christa": ("#F2DE90", 0.5), "h_annie": ("#D7C175", 0.5), "h_reiner": ("#CFB06A", 0.5),
    "h_hannes": ("#C9A55C", 0.6), "h_black": ("#141418", 0.4), "h_mikasa": ("#1C2230", 0.4),
    "h_eren": ("#3B2F28", 0.5), "h_jean": ("#A08A6C", 0.55), "h_jean_dark": ("#4A3A2C", 0.6),
    "h_connie": ("#56565A", 0.8), "h_sasha": ("#6B4A30", 0.5), "h_bert": ("#2A2220", 0.5),
    "h_ymir": ("#4A3424", 0.5), "h_marco": ("#2E2620", 0.5), "h_carla": ("#5A3A26", 0.5),
    "h_grisha": ("#2E2622", 0.5), "h_white": ("#ECECE6", 0.6), "h_shaved": ("#2E2E34", 0.8),
    "h_red": ("#7A3A22", 0.5), "h_brown": ("#5A4030", 0.5), "h_ash": ("#8A7A66", 0.5),
    # civilian / family
    "c_blouse": ("#E4D8BC", 0.85), "c_skirt": ("#8A5A3A", 0.85), "c_apron": ("#F2EEE4", 0.85),
    "c_coat": ("#6A5A48", 0.85), "c_grisha_shirt": ("#E2DED2", 0.85), "c_dark": ("#3A3430", 0.85),
    "c_bag": ("#4A2E1C", 0.6),
    "k_coat": ("#6E3A2E", 0.85), "k_shirt": ("#8C8A55", 0.85), "k_pants": ("#4A4034", 0.85),
    "k_shoes": ("#6B4A35", 0.7), "k_cardigan": ("#C99A8C", 0.85), "k_dress": ("#E8E4E2", 0.85),
    # horse
    "horse_bay": ("#6C4A34", 0.7), "horse_grey": ("#B4B0A8", 0.7), "horse_chestnut": ("#7A4A2A", 0.7),
    "horse_dark": ("#2A1E18", 0.7), "saddle": ("#3A2216", 0.5), "hoof": ("#2A2622", 0.6),
    # set
    "wood": ("#7A5636", 0.85), "wood_dark": ("#4A3220", 0.85), "iron": ("#2A2A2C", 0.5),
}
CIV_TOPS = ["#C8B48A", "#8A9A7A", "#A86A4A", "#7A8AA0", "#B0A090", "#9A7A5A", "#D0C6B0", "#6A7A5A"]
CIV_BOTTOMS = ["#5A4A3A", "#4A4034", "#6A5A48", "#3A3A40", "#7A6A50"]
CIV_SKIRTS = ["#8A5A3A", "#6A4A5A", "#5A6A7A", "#9A7A4A", "#7A4A3A"]
CIV_HAIR = ["h_brown", "h_black", "h_blond", "h_red", "h_ash", "h_eren", "h_carla"]

_MATS = {}
def mat(key):
    """Material by palette key or '#rrggbb'; cached per scene build."""
    m = _MATS.get(key)
    if m is not None and m.name in bpy.data.materials:
        return m
    if key.startswith("#"):
        hexc, rough = key, 0.85
    else:
        hexc, rough = COL[key]
    m = bpy.data.materials.get("PK_" + key) or L.mat("PK_" + key, srgb(hexc), rough)
    if key.startswith("h_"):
        b = m.node_tree.nodes["Principled BSDF"]
        b.inputs["Sheen Weight"].default_value = 0.4
        if key == "h_erwin":          # read cue: bright blond that catches the light from the air
            b.inputs["Emission Color"].default_value = (*srgb(hexc), 1)
            b.inputs["Emission Strength"].default_value = 0.12 if not NIGHT else 0.0
    _MATS[key] = m
    return m

# ---------------------------------------------------------------- emblem textures (drawn per pixel, packed)
def _shield(u, v):
    """Home-plate shield: flat top, straight sides, tapering to a point. Returns (inside, border)."""
    x = abs(u - 0.5)
    if v > 0.95 or v < 0.03:
        return False, False
    w = 0.42 if v >= 0.42 else 0.42 * (v - 0.03) / 0.39
    if x > w:
        return False, False
    return True, (x > w - 0.045 or v > 0.905 or (v < 0.42 and x > w - 0.06))

def _feather_wing(u, v, side):
    """Fan of 5 feathers from a base near the bottom centre, spreading up and out to one side."""
    bx, by = 0.5 + side * 0.04, 0.16
    for k in range(5):
        a = math.radians(14 + 13 * k)
        dx, dy = side * math.sin(a), math.cos(a)
        Lk, wk = 0.80 - 0.07 * k, 0.085 - 0.006 * k
        qx, qy = u - bx, v - by
        t = qx * dx + qy * dy
        n = abs(qx * dy - qy * dx)
        if 0 < t < Lk and n < wk * math.sqrt(max(0.0, 1 - (t / Lk) ** 2)) * (0.55 + 0.45 * t / Lk) + 0.012:
            return True, n > wk * 0.7
    return False, False

def _emblem_px(kind, u, v):
    ins, bord = _shield(u, v)
    if kind == "wings":
        lw, le = _feather_wing(u, v, -1)
        rw, re_ = _feather_wing(u, v, 1)
        if rw:
            return ((0.62, 0.62, 0.66) if re_ else (0.97, 0.97, 0.98)), 1.0
        if lw:
            return ((0.06, 0.10, 0.30) if le else (0.10, 0.17, 0.47)), 1.0
        if not ins:
            return (0, 0, 0), 0.0
        if bord:
            return (0.20, 0.20, 0.20), 1.0
        if abs(u - 0.5) < 0.012 or abs(v - 0.60) < 0.012:
            return (0.05, 0.05, 0.05), 1.0
        return (0.69, 0.68, 0.66), 1.0
    if not ins:
        return (0, 0, 0), 0.0
    if bord:
        return (0.16, 0.14, 0.12), 1.0
    if kind == "roses":
        for cx in (0.35, 0.65):
            r = math.hypot(u - cx, v - 0.62)
            if r < 0.15:
                ang = math.atan2(v - 0.62, u - cx)
                s = math.sin(r * 55 + ang * 2)
                return ((0.27, 0.07, 0.07) if s > 0.55 else (0.48, 0.12, 0.13) if r < 0.13 else (0.77, 0.52, 0.51)), 1.0
        for cx in (0.35, 0.65):     # stems
            ax, ay, bx2, by2 = 0.5, 0.12, cx, 0.5
            dx, dy = bx2 - ax, by2 - ay
            t = max(0, min(1, ((u - ax) * dx + (v - ay) * dy) / (dx * dx + dy * dy)))
            if math.hypot(u - ax - dx * t, v - ay - dy * t) < 0.018:
                return (0.78, 0.78, 0.80), 1.0
        return (0.85, 0.84, 0.80), 1.0
    if kind == "swords":
        for sgn in (-1, 1):
            ax, ay = 0.5 - sgn * 0.27, 0.16
            bx2, by2 = 0.5 + sgn * 0.27, 0.86
            dx, dy = bx2 - ax, by2 - ay
            ll = dx * dx + dy * dy
            t = ((u - ax) * dx + (v - ay) * dy) / ll
            d = math.hypot(u - ax - dx * t, v - ay - dy * t)
            if 0 <= t <= 1 and d < 0.03:
                return ((0.35, 0.25, 0.12) if t < 0.18 else (0.92, 0.92, 0.90)), 1.0
            if abs(t - 0.2) < 0.025 and d < 0.10:          # cross guard
                return (0.80, 0.70, 0.30), 1.0
        return (0.55, 0.16, 0.13), 1.0
    if kind == "unicorn":
        # head profile facing left, neck down to the right, gold horn
        hx, hy = (u - 0.42), (v - 0.62)
        c, s = math.cos(0.5), math.sin(0.5)
        rx, ry = hx * c + hy * s, -hx * s + hy * c
        if (rx / 0.18) ** 2 + (ry / 0.09) ** 2 < 1:
            return (0.96, 0.96, 0.94), 1.0
        ax, ay, bx2, by2 = 0.52, 0.60, 0.64, 0.18
        dx, dy = bx2 - ax, by2 - ay
        t = ((u - ax) * dx + (v - ay) * dy) / (dx * dx + dy * dy)
        if 0 <= t <= 1 and math.hypot(u - ax - dx * t, v - ay - dy * t) < 0.07 + 0.03 * t:
            return ((0.30, 0.30, 0.30) if u - (ax + dx * t) > 0.05 else (0.96, 0.96, 0.94)), 1.0
        ax, ay, bx2, by2 = 0.40, 0.70, 0.24, 0.90
        dx, dy = bx2 - ax, by2 - ay
        t = ((u - ax) * dx + (v - ay) * dy) / (dx * dx + dy * dy)
        if 0 <= t <= 1 and math.hypot(u - ax - dx * t, v - ay - dy * t) < 0.035 * (1 - t):
            return (0.90, 0.75, 0.30), 1.0
        return (0.24, 0.42, 0.28), 1.0
    return (0.5, 0.5, 0.5), 1.0

def _emblem_mat(kind, N=96, field=None):
    key = "emb_" + kind + ("_banner" if field else "")
    m = _MATS.get(key)
    if m is not None and m.name in bpy.data.materials:
        return m
    img = bpy.data.images.new("PK_" + key, N, N, alpha=True)
    px = [0.0] * (N * N * 4)
    for j in range(N):
        v = (j + 0.5) / N
        for i in range(N):
            u = (i + 0.5) / N
            (r, g, b), a = _emblem_px(kind, u, v)
            if field and a < 0.5:
                (r, g, b), a = field, 1.0
            k = (j * N + i) * 4
            px[k:k + 4] = (r, g, b, a)
    img.pixels = px
    img.pack()
    m = bpy.data.materials.new("PK_" + key); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    tx = nt.nodes.new("ShaderNodeTexImage"); tx.image = img; tx.interpolation = "Linear"
    nt.links.new(tx.outputs["Color"], b.inputs["Base Color"])
    nt.links.new(tx.outputs["Alpha"], b.inputs["Alpha"])
    b.inputs["Roughness"].default_value = 0.8
    b.inputs["Emission Color"].default_value = (1, 1, 1, 1)
    nt.links.new(tx.outputs["Color"], b.inputs["Emission Color"])
    b.inputs["Emission Strength"].default_value = 0.0 if NIGHT else 0.08     # keeps the decal readable in shade
    _MATS[key] = m
    return m

EMBLEM = {"cadet": "swords", "garrison": "roses", "scout": "wings", "mp": "unicorn"}

# ---------------------------------------------------------------- mesh builder
class Mesh:
    """One bmesh with a material list; primitives are transformed by the current matrix X."""
    def __init__(s):
        s.bm = bmesh.new(); s.keys = []; s.X = Matrix(); s.uv = None

    def mi(s, key):
        if key not in s.keys:
            s.keys.append(key)
        return s.keys.index(key)

    def _tag(s, verts, key, M):
        for v in verts:
            v.co = M @ v.co
        idx = s.mi(key)
        for f in {f for v in verts for f in v.link_faces}:
            f.material_index = idx; f.smooth = True

    def ell(s, c, r, key, rot=None, seg=(10, 6)):
        """Ellipsoid at c with radii r; rot = Matrix(3x3) or a direction for local z."""
        res = bmesh.ops.create_uvsphere(s.bm, u_segments=seg[0], v_segments=seg[1], radius=1.0)
        R = Matrix() if rot is None else (rot.to_4x4() if isinstance(rot, Matrix) else
                                          Vector(rot).to_track_quat("Z", "Y").to_matrix().to_4x4())
        M = s.X @ Matrix.Translation(Vector(c)) @ R @ Matrix.Diagonal((*r, 1))
        s._tag(res["verts"], key, M)

    def cap(s, p0, p1, r0, r1=None, key="skin", seg=8, ends=True):
        p0, p1 = Vector(p0), Vector(p1)
        r1 = r0 if r1 is None else r1
        d = p1 - p0
        if d.length < 1e-5:
            s.ell(p0, (r0, r0, r0), key); return
        res = bmesh.ops.create_cone(s.bm, cap_ends=False, segments=seg, radius1=r0, radius2=r1, depth=d.length)
        q = d.to_track_quat("Z", "Y").to_matrix().to_4x4()
        s._tag(res["verts"], key, s.X @ Matrix.Translation((p0 + p1) / 2) @ q)
        if ends:
            s.ell(p0, (r0, r0, r0), key, seg=(8, 5)); s.ell(p1, (r1, r1, r1), key, seg=(8, 5))

    def box(s, c, size, key, rot=None):
        res = bmesh.ops.create_cube(s.bm, size=1.0)
        R = Matrix() if rot is None else rot.to_4x4()
        M = s.X @ Matrix.Translation(Vector(c)) @ R @ Matrix.Diagonal((*size, 1))
        for v in res["verts"]:
            v.co = M @ v.co
        idx = s.mi(key)
        for f in {f for v in res["verts"] for f in v.link_faces}:
            f.material_index = idx; f.smooth = False

    def grid(s, rows, key, outward=None):
        """Sheet from a 2D list of points (rows x cols)."""
        vs = [[s.bm.verts.new(s.X @ Vector(p)) for p in row] for row in rows]
        idx = s.mi(key)
        for i in range(len(vs) - 1):
            for j in range(len(vs[0]) - 1):
                f = s.bm.faces.new((vs[i][j], vs[i][j + 1], vs[i + 1][j + 1], vs[i + 1][j]))
                f.material_index = idx; f.smooth = True
                if outward is not None:
                    f.normal_update()
                    c = f.calc_center_median()
                    if f.normal.dot(c - s.X @ Vector(outward)) < 0:
                        f.normal_flip()

    def quad(s, c, normal, up, size, key):
        """UV-mapped decal quad."""
        if s.uv is None:
            s.uv = s.bm.loops.layers.uv.verify()
        n = Vector(normal).normalized(); u = Vector(up)
        u = (u - n * u.dot(n)).normalized(); r = u.cross(n)
        c = Vector(c); h = size / 2
        corners = [c - r * h - u * h, c + r * h - u * h, c + r * h + u * h, c - r * h + u * h]
        vs = [s.bm.verts.new(s.X @ p) for p in corners]
        f = s.bm.faces.new(vs)
        f.material_index = s.mi(key)
        for lp, uvc in zip(f.loops, ((0, 0), (1, 0), (1, 1), (0, 1))):
            lp[s.uv].uv = uvc

    def finish(s, name, coll, ink=INK):
        if not s.bm.verts:
            s.bm.free(); return None
        me = bpy.data.meshes.new(name)
        s.bm.to_mesh(me); s.bm.free()
        for k in s.keys:
            if k in _MATS and (k.startswith("emb_") or k.startswith("pk_")):
                me.materials.append(_MATS[k])
            else:
                me.materials.append(_emblem_mat(k[4:]) if k.startswith("emb_") else mat(k))
        ob = bpy.data.objects.new(name, me)
        coll.objects.link(ob)
        if ink > 0:
            L.outline(ob, ink)
            for ch in ob.children:
                for uc in list(ch.users_collection):
                    uc.objects.unlink(ch)
                coll.objects.link(ch)
        return ob

# ---------------------------------------------------------------- presets
PRESETS = {
    "erwin":     dict(H=1.88, sh=1.10, hair="side_part", hc="h_erwin", outfit="scout", hs=1.12),
    "levi":      dict(H=1.60, sh=1.0, hair="undercut", hc="h_black", hc2="h_shaved", outfit="scout", cravat=True, hs=1.1),
    "hannes":    dict(H=1.80, sh=1.08, hair="messy", hc="h_hannes", outfit="garrison"),
    "carla":     dict(H=1.62, sex="f", hair="long_low", hc="h_carla", outfit="dress", odm=False),
    "grisha":    dict(H=1.82, hair="long_tied", hc="h_grisha", outfit="coat", bag=True, odm=False),
    "eren":      dict(H=1.70, hair="messy", hc="h_eren", outfit="cadet"),
    "mikasa":    dict(H=1.70, sex="f", hair="bob", hc="h_mikasa", outfit="cadet", scarf=True),
    "armin":     dict(H=1.63, sh=0.92, hair="bowl", hc="h_armin", outfit="cadet", hs=1.1),
    "jean":      dict(H=1.75, hair="two_tone", hc="h_jean", hc2="h_jean_dark", outfit="cadet"),
    "connie":    dict(H=1.58, hair="buzz", hc="h_connie", outfit="cadet"),
    "sasha":     dict(H=1.68, sex="f", hair="ponytail", hc="h_sasha", outfit="cadet"),
    "reiner":    dict(H=1.85, sh=1.22, bulk=1.15, hair="short", hc="h_reiner", outfit="cadet"),
    "bertholdt": dict(H=1.92, sh=1.02, hair="short", hc="h_bert", outfit="cadet"),
    "christa":   dict(H=1.45, sex="f", hair="long_blonde", hc="h_christa", outfit="cadet"),
    "ymir":      dict(H=1.72, sex="f", hair="low_tail", hc="h_ymir", outfit="cadet"),
    "annie":     dict(H=1.53, sex="f", hair="bun", hc="h_annie", outfit="cadet", hoodie=True),
    "marco":     dict(H=1.78, hair="side_part", hc="h_marco", outfit="cadet", hs=0.9),
    "pixis":     dict(H=1.70, hair="bald", hc="h_white", outfit="garrison", moustache=True),
    "eren_child":   dict(H=1.38, child=True, hair="messy", hc="h_eren", outfit="kid_eren", odm=False),
    "mikasa_child": dict(H=1.35, child=True, sex="f", hair="long_straight", hc="h_mikasa", outfit="kid_mikasa",
                         scarf=True, odm=False, skin="skin_pale"),
}
GENERIC = ("cadet", "garrison", "scout", "mp", "civilian")
NVAR = 8

def get_preset(name):
    """Named preset dict, or a generic variant ('cadet', 'cadet:3')."""
    if name in PRESETS:
        return dict(PRESETS[name], name=name)
    base, _, k = name.partition(":")
    if base not in GENERIC:
        raise KeyError(f"people_kit: unknown preset {name!r}")
    k = int(k or 0) % NVAR
    rnd = random.Random(hash((base, k)) & 0xFFFF)
    sex = "f" if (k % 3 == 1) else "m"
    H = rnd.uniform(1.58, 1.70) if sex == "f" else rnd.uniform(1.68, 1.84)
    styles_m = ["short", "short", "messy", "buzz", "side_part", "short"]
    styles_f = ["ponytail", "bob", "bun", "low_tail", "long_straight"]
    hair = rnd.choice(styles_f if sex == "f" else styles_m)
    hc = rnd.choice(["h_brown", "h_black", "h_eren", "h_ash", "h_blond", "h_bert", "h_red"])
    d = dict(name=f"{base}{k}", H=H, sex=sex, sh=rnd.uniform(0.96, 1.08) if sex == "m" else 0.94,
             hair=hair, hc=hc, outfit=base)
    if base == "civilian":
        d["outfit"] = "civ_f" if sex == "f" else "civ_m"
        d["odm"] = False
        d["top"] = rnd.choice(CIV_TOPS); d["bottom"] = rnd.choice(CIV_SKIRTS if sex == "f" else CIV_BOTTOMS)
        d["hc"] = rnd.choice(CIV_HAIR)
        d["apron"] = sex == "f" and rnd.random() < 0.5
    return d

# ---------------------------------------------------------------- skeleton (normalised units, H = 1)
def ik(a, t, l1, l2, pole):
    a, t, pole = Vector(a), Vector(t), Vector(pole)
    d = t - a
    dist = min(max(d.length, abs(l1 - l2) + 1e-3), (l1 + l2) * 0.999)
    dn = d.normalized() if d.length > 1e-6 else Vector((0, 0, -1))
    ca = (l1 * l1 + dist * dist - l2 * l2) / (2 * l1 * dist)
    sa = math.sqrt(max(0.0, 1 - ca * ca))
    p = pole - dn * pole.dot(dn)
    p = p.normalized() if p.length > 1e-6 else dn.orthogonal().normalized()
    return a + dn * (l1 * ca) + p * (l1 * sa), a + dn * dist

THIGH, SHIN, UARM, FARM = 0.245, 0.245, 0.165, 0.152

def skeleton(pr, pose, phase=0.0, H=1.7):
    """Joint positions in normalised units for a pose. Left = -x, right = +x, forward = +y."""
    sh = pr.get("sh", 1.0) * (0.93 if pr.get("sex") == "f" else 1.0)
    hipf = 1.08 if pr.get("sex") == "f" else 1.0
    child = pr.get("child", False)
    J = {"lean": 0.0, "hp": 0.0, "pitch": 0.0, "flow": Vector((0, -0.02, 0)), "blades": False,
         "sh": sh, "hipf": hipf}
    P = Vector((0, 0, 0.53)); lean = 0.0
    sw = 0.105 * sh; hw = 0.055 * hipf
    sp = math.sin(phase); cp = math.cos(phase)
    # defaults (stand)
    feet = [Vector((-0.06, 0.0, 0.045)), Vector((0.06, 0.0, 0.045))]
    kpole = [Vector((0, 1, 0)), Vector((0, 1, 0))]
    hands = None; epole = [Vector((-0.3, -1, 0)), Vector((0.3, -1, 0))]
    if pose == "walk":
        s = 0.13
        feet = [Vector((-0.06, s * sp, 0.045 + max(0, -s * sp) * 0.25)), Vector((0.06, -s * sp, 0.045 + max(0, s * sp) * 0.25))]
        P = Vector((0, 0, 0.52)); lean = 0.05
        hands = [Vector((-sw - 0.03, -0.10 * sp, 0.50)), Vector((sw + 0.03, 0.10 * sp, 0.50))]
        J["flow"] = Vector((0, -0.08, 0.02))
    elif pose == "run" or pose == "carry_kids":
        s = 0.22
        f = 1 if sp >= 0 else -1
        lf = Vector((-0.07, 0.20 * f, 0.10 if f > 0 else 0.20)); lf.y = 0.20 if f > 0 else -0.24
        rf = Vector((0.07, -lf.y * 0.95, 0.20 if f > 0 else 0.10))
        feet = [lf, rf]
        P = Vector((0, 0, 0.49)); lean = 0.30 if pose == "run" else 0.18
        kpole = [Vector((0, 1, 0.2)), Vector((0, 1, 0.2))]
        hands = [Vector((-sw - 0.02, -0.14 * f + 0.06, 0.62)), Vector((sw + 0.02, 0.14 * f + 0.06, 0.62))]
        epole = [Vector((-0.2, -1, -0.4)), Vector((0.2, -1, -0.4))]
        J["flow"] = Vector((0, -0.30, 0.16))
    elif pose == "salute":
        hands = [Vector((-0.03, -0.095, 0.60)), Vector((-0.04, 0.090, 0.735))]
        epole = [Vector((-1, -0.4, -0.2)), Vector((1, 0.2, -0.3))]
    elif pose == "kneel":
        P = Vector((0, 0, 0.30))
        feet = [Vector((-0.07, 0.25, 0.045)), Vector((0.07, -0.27, 0.035))]
        kpole = [Vector((0, 1, 1)), Vector((0, 0.2, -1))]
        hands = [Vector((-0.08, 0.22, 0.30)), Vector((-0.04, 0.090, 0.47))]
        epole = [Vector((-0.5, 0.5, -1)), Vector((1, 0.2, -0.3))]
        lean = 0.12; J["hp"] = 0.35
    elif pose == "ride":
        P = Vector((0, -0.04, 1.71 / H))
        feet = [Vector((-0.17 / H * 1.7, 0.10, P.z - 0.42)), Vector((0.17 / H * 1.7, 0.10, P.z - 0.42))]
        kpole = [Vector((-0.4, 1, 0)), Vector((0.4, 1, 0))]
        hands = [Vector((-0.07, 0.24, P.z + 0.13)), Vector((0.07, 0.24, P.z + 0.13))]
        epole = [Vector((-0.5, -1, -0.5)), Vector((0.5, -1, -0.5))]
        lean = 0.10
        J["flow"] = Vector((0, -0.22, 0.10))
    elif pose == "odm_fly":
        J["pitch"] = math.radians(72)
        feet = [Vector((-0.08, -0.10, 0.06)), Vector((0.09, -0.02, 0.12))]
        kpole = [Vector((0, 1, 0)), Vector((0, 1, 0))]
        hands = [Vector((-0.20, 0.06, 0.50)), Vector((0.20, 0.06, 0.50))]
        epole = [Vector((-1, -0.5, 0)), Vector((1, -0.5, 0))]
        J["flow"] = Vector((0, -0.05, -0.30))       # in body frame: trails behind the flier
        J["blades"] = True
    elif pose == "draped":                           # child over an adult's shoulder, reaching back
        P = Vector((0, 0, 0)); lean = -math.radians(105)
        feet = [Vector((-0.05, 0.16, -0.40)), Vector((0.05, 0.12, -0.42))]
        kpole = [Vector((0, 1, 0)), Vector((0, 1, 0))]
        J["reach"] = True
    elif pose == "carried_side":                     # child sitting on an adult's forearm
        P = Vector((0, 0, 0)); lean = 0.15
        feet = [Vector((-0.06, 0.26, -0.30)), Vector((0.06, 0.28, -0.28))]
        kpole = [Vector((0, 1, 0.3)), Vector((0, 1, 0.3))]
        hands = [Vector((0.05, 0.12, 0.26)), Vector((0.16, 0.10, 0.24))]
    J["lean"] = lean
    u = Vector((0, math.sin(lean), math.cos(lean)))
    fwd = Vector((0, math.cos(lean), -math.sin(lean)))
    hf = 1.22 if child else 1.0
    tor = 0.27 if child else 0.28
    J.update(P=P, u=u, fwd=fwd, hf=hf)
    J["C"] = P + u * (0.19 * tor / 0.28)
    J["Sc"] = P + u * tor
    J["N"] = P + u * (tor + 0.035)
    J["Hc"] = P + u * (tor + 0.035 + 0.075 * hf)
    J["shL"] = J["Sc"] + Vector((-sw, 0, 0)); J["shR"] = J["Sc"] + Vector((sw, 0, 0))
    J["hipL"] = P + Vector((-hw, 0, -0.03)); J["hipR"] = P + Vector((hw, 0, -0.03))
    if hands is None:
        hands = [J["shL"] + Vector((-0.025, 0.01, -0.305)), J["shR"] + Vector((0.025, 0.01, -0.305))]
    if J.get("reach"):
        hands = [J["shL"] + u * 0.05 + Vector((-0.10, 0.05, -0.30)),
                 J["shR"] + Vector((0.12, -0.55, 0.35))]
        epole = [Vector((0, 0, -1)), Vector((1, 0, 0))]
    for i, sd in enumerate("LR"):
        J["kn" + sd], J["an" + sd] = ik(J["hip" + sd], feet[i], THIGH, SHIN, kpole[i])
        J["el" + sd], J["wr" + sd] = ik(J["sh" + sd], hands[i], UARM, FARM, epole[i])
    return J

# ---------------------------------------------------------------- hair (head-local offsets in head radii)
def hair_parts(style, hc, hc2):
    """List of (offset, radii, colour key, rot_euler) ellipsoids around a unit head (x right, y front, z up)."""
    cap = ((0, -0.10, 0.16), (0.92, 0.98, 0.92), hc)
    P = []
    if style == "bald":
        return [((0, -0.35, -0.10), (0.80, 0.55, 0.45), hc2 or "skin")] if False else []
    if style == "buzz":
        return [((0, -0.08, 0.10), (0.84, 0.94, 0.93), hc)]
    if style in ("short", "messy", "side_part", "two_tone", "undercut"):
        if style == "undercut":
            P += [((0, -0.10, -0.05), (0.83, 0.93, 0.85), hc2),            # shaved sides/back
                  ((0, -0.05, 0.42), (0.98, 1.06, 0.62), hc),               # heavy top
                  ((-0.32, 0.72, 0.18), (0.28, 0.20, 0.42), hc, (0.3, 0, 0.2)),   # curtain bangs
                  ((0.32, 0.72, 0.18), (0.28, 0.20, 0.42), hc, (0.3, 0, -0.2))]
        elif style == "two_tone":
            P += [((0, -0.10, -0.02), (0.84, 0.94, 0.88), hc2),
                  ((0.05, -0.02, 0.45), (0.96, 1.04, 0.58), hc),
                  ((0.25, 0.70, 0.40), (0.45, 0.25, 0.30), hc, (0.4, 0, 0))]
        elif style == "side_part":
            P += [cap,
                  ((0.30, 0.25, 0.55), (0.70, 0.75, 0.42), hc, (0, -0.35, 0)),    # swept volume to his right
                  ((-0.52, 0.10, 0.30), (0.42, 0.75, 0.50), hc),
                  ((0.10, 0.62, 0.52), (0.62, 0.30, 0.25), hc, (0.3, 0, -0.2))]   # neat fringe off the brow
        else:
            P += [cap, ((0, 0.55, 0.45), (0.70, 0.35, 0.30), hc)]
            if style == "messy":
                rnd = random.Random(5)
                for k in range(9):
                    a = -math.pi * 0.9 + k * math.pi * 1.8 / 8
                    P.append(((math.sin(a) * 0.82, math.cos(a) * 0.85 - 0.1, 0.30 + rnd.uniform(-0.1, 0.25)),
                              (0.28, 0.28, 0.20), hc, (rnd.uniform(-0.5, 0.5), rnd.uniform(-0.5, 0.5), 0)))
                P.append(((0, -0.2, 0.85), (0.35, 0.35, 0.25), hc))
        return P
    if style in ("bowl", "bob"):
        drop = 0.75 if style == "bob" else 0.55
        P += [((0, -0.10, 0.12), (0.97, 1.02, 0.96), hc),
              ((-0.68, 0.10, -drop * 0.55), (0.34, 0.80, drop), hc),
              ((0.68, 0.10, -drop * 0.55), (0.34, 0.80, drop), hc),
              ((0, -0.55, -drop * 0.45), (0.85, 0.50, drop), hc),
              ((0, 0.60, 0.42), (0.85, 0.36, 0.30), hc)]
        if style == "bob":
            P.append(((0.25, 0.70, 0.20), (0.42, 0.22, 0.45), hc, (0.2, 0, -0.4)))   # bangs over the right eye
        return P
    P.append(cap); P.append(((0, 0.55, 0.45), (0.70, 0.35, 0.30), hc))
    if style == "bun":
        P += [((0, -0.98, 0.15), (0.40, 0.36, 0.40), hc), ((-0.45, 0.65, 0.05), (0.25, 0.20, 0.55), hc)]
    elif style == "ponytail":
        P += [((0, -0.95, 0.35), (0.22, 0.22, 0.22), hc),
              ((0, -1.12, -0.25), (0.25, 0.30, 0.65), hc, (-0.35, 0, 0))]
    elif style == "low_tail":
        P += [((0, -0.92, -0.35), (0.22, 0.22, 0.22), hc),
              ((0, -1.0, -0.95), (0.20, 0.22, 0.55), hc, (-0.15, 0, 0))]
    elif style in ("long_low", "long_straight", "long_blonde", "long_tied"):
        ln = {"long_low": 1.5, "long_straight": 1.25, "long_blonde": 0.9, "long_tied": 0.8}[style]
        P += [((0, -0.62, -0.25 - ln * 0.4), (0.82, 0.42, 0.55 + ln * 0.4), hc),
              ((-0.66, 0.0, -0.35), (0.30, 0.65, 0.65), hc), ((0.66, 0.0, -0.35), (0.30, 0.65, 0.65), hc)]
        if style == "long_low":       # Carla: loose tail over the left shoulder
            P.append(((-0.70, 0.30, -1.6), (0.28, 0.30, 0.75), hc, (0.3, 0, 0.3)))
        if style == "long_tied":      # Grisha: shoulder length tied at the nape
            P.append(((0, -0.95, -1.15), (0.22, 0.22, 0.55), hc))
    return P

# ---------------------------------------------------------------- figure geometry
def _rotx(a):
    return Matrix.Rotation(-a, 3, "X")

def build_figure(m, deco, pr, pose, phase=0.0, X=Matrix()):
    """Adds one figure (body into Mesh m, emblems into Mesh deco) at matrix X (metres). Returns hooks."""
    H = pr["H"]
    J = skeleton(pr, pose, phase, H)
    P = J["P"]
    BX = Matrix.Translation(P) @ Matrix.Rotation(-J["pitch"], 4, "X") @ Matrix.Translation(-P)
    m.X = deco.X = X @ Matrix.Scale(H, 4) @ BX
    bulk = pr.get("bulk", 1.0); sh = J["sh"]; hipf = J["hipf"]
    out = pr["outfit"]; skin = pr.get("skin", "skin")
    mil = out in EMBLEM
    u, fwd, lean = J["u"], J["fwd"], J["lean"]
    Rt = _rotx(lean)
    civ = out in ("civ_m", "civ_f", "dress", "coat", "kid_eren", "kid_mikasa")
    top = {"civ_m": pr.get("top", "#C8B48A"), "civ_f": pr.get("top", "#C8B48A"), "dress": "c_blouse",
           "coat": "c_coat", "kid_eren": "k_coat", "kid_mikasa": "k_cardigan"}.get(out, "jacket")
    sleeve = top
    legs = {"civ_m": pr.get("bottom", "#5A4A3A"), "civ_f": skin, "dress": skin, "coat": "c_dark",
            "kid_eren": "k_pants", "kid_mikasa": skin}.get(out, "trousers")
    feetk = {"civ_m": "c_dark", "civ_f": "c_dark", "dress": "c_dark", "coat": "c_dark",
             "kid_eren": "k_shoes", "kid_mikasa": "k_shoes"}.get(out, "boots")
    # --- legs
    for sd in "LR":
        hp, kn, an = J["hip" + sd], J["kn" + sd], J["an" + sd]
        m.cap(hp, kn, 0.050 * bulk * hipf, 0.036 * bulk, legs)
        m.cap(kn, an, 0.035 * bulk, 0.025 * bulk, legs)
        ff = Vector((fwd.x, max(0.3, fwd.y) if pose != "odm_fly" else 0.6, 0)).normalized()
        if pose in ("kneel",) and sd == "R":
            ff = Vector((0, 0.3, -1)).normalized()
        if mil or out == "coat":
            m.cap(an, an + (kn - an) * 0.72, 0.030 * bulk, 0.038 * bulk, feetk)        # knee boots
        m.ell(an + ff * 0.035 + Vector((0, 0, -0.018)), (0.028, 0.072, 0.024), feetk, rot=ff.to_track_quat("Y", "Z").to_matrix())
        if mil:
            mid = hp + (kn - hp) * 0.55
            m.ell(mid, (0.047 * bulk, 0.047 * bulk, 0.008), "harness", rot=(kn - hp))
    # --- pelvis / torso
    m.ell(P + u * 0.0, (0.085 * hipf * bulk, 0.062 * bulk, 0.065), legs if out not in ("dress", "civ_f", "kid_mikasa") else top, rot=Rt)
    m.ell(P + u * 0.10, (0.076 * bulk * (1.0 if pr.get("sex") != "f" else 0.92), 0.056 * bulk, 0.075), "shirt" if mil else top, rot=Rt)
    chest_r = (0.094 * sh * bulk, 0.064 * bulk, 0.098)
    C = J["C"] + u * 0.012
    m.ell(C, chest_r, top, rot=Rt)
    if mil:
        m.ell(C + fwd * 0.050 + u * 0.035, (0.030, 0.022, 0.060), "shirt", rot=Rt)      # open jacket front
        m.ell(J["C"] - u * 0.035, (chest_r[0] * 1.03, chest_r[1] * 1.06, 0.009), "harness", rot=Rt)   # chest strap
        m.ell(P + u * 0.055, (0.083 * hipf * bulk, 0.062 * bulk, 0.012), "harness", rot=Rt)          # belt
        m.ell(P + Vector((0, 0, -0.035)), (0.098 * hipf * bulk, 0.072 * bulk, 0.072), "wrap", rot=Rt)   # hip wrap
        for s_ in (-1, 1):
            a0 = J["Sc"] + Vector((s_ * 0.05 * sh, 0, 0)) + fwd * 0.055
            m.cap(a0, P + u * 0.06 + Vector((s_ * 0.05, 0, 0)) + fwd * 0.06, 0.008, 0.008, "harness", seg=5, ends=False)
    if pr.get("sex") == "f" and not pr.get("child"):
        for s_ in (-1, 1):
            m.ell(J["C"] + fwd * 0.040 + Vector((s_ * 0.036, 0, 0)) - u * 0.01, (0.032, 0.030, 0.030), top)
    # --- arms
    for sd in "LR":
        s0, el, wr = J["sh" + sd], J["el" + sd], J["wr" + sd]
        m.ell(s0, (0.040 * bulk * sh, 0.040 * bulk, 0.040 * bulk), sleeve)
        m.cap(s0, el, 0.034 * bulk, 0.029 * bulk, sleeve)
        m.cap(el, wr, 0.029 * bulk, 0.022 * bulk, sleeve)
        hd = (wr - el).normalized()
        m.ell(wr + hd * 0.025, (0.022, 0.024, 0.026), skin)
        if J["blades"]:
            b0 = wr + hd * 0.03
            bd = (Vector((0.25 if sd == "R" else -0.25, -0.15, -1.0))).normalized()
            m.cap(b0, b0 + bd * 0.06, 0.012, 0.012, "steel_dark", seg=5, ends=False)
            m.box(b0 + bd * 0.30, (0.008, 0.035, 0.48), "blade", rot=bd.to_track_quat("Z", "Y").to_matrix())
    # --- neck / head (faceless)
    hf = J["hf"]; hr = 0.066 * hf
    Rh = _rotx(lean + J["hp"])
    Hc = J["Hc"] + fwd * 0.004
    m.cap(J["N"] - u * 0.02, Hc - u * hr * 0.5, 0.024 * bulk, 0.022, skin, ends=False)
    m.ell(Hc, (hr * 0.80, hr * 0.90, hr), skin, rot=Rh)
    hs = pr.get("hs", 1.0)
    for part in hair_parts(pr["hair"], pr["hc"], pr.get("hc2")):
        off, rad, key = part[0], part[1], part[2]
        rot = Rh @ Euler(part[3]).to_matrix() if len(part) > 3 else Rh
        sc_ = hs if key == pr["hc"] else 1.0
        m.ell(Hc + Rh @ (Vector(off) * hr * (1.0 + (sc_ - 1) * 0.6)), tuple(r * hr * sc_ for r in rad), key, rot=rot)
    if pr.get("moustache"):
        for s_ in (-1, 1):
            m.ell(Hc + Rh @ (Vector((s_ * 0.38, 0.86, -0.38)) * hr), (0.42 * hr, 0.16 * hr, 0.13 * hr), "h_white",
                  rot=Rh @ Euler((0, s_ * 0.45, 0)).to_matrix())
        m.ell(Hc + Rh @ (Vector((0, -0.55, -0.2)) * hr), (0.78 * hr, 0.45 * hr, 0.35 * hr), "h_white")   # fringe of white at the back
    # --- outfit extras
    if pr.get("scarf"):
        m.ell(J["N"] + u * 0.012, (0.052, 0.052, 0.030), "scarf", rot=Rt)
        m.cap(J["N"] + fwd * 0.045 - u * 0.005, J["C"] + fwd * 0.075 - u * 0.075, 0.020, 0.016, "scarf", seg=6)
    if pr.get("cravat"):
        m.ell(J["N"] + fwd * 0.030 - u * 0.012, (0.024, 0.016, 0.032), "cravat", rot=Rt)
    if pr.get("hoodie"):
        m.ell(J["Sc"] - fwd * 0.060 + u * 0.005, (0.070, 0.032, 0.045), "hood_grey", rot=Rt)
    if out in ("dress", "civ_f", "kid_mikasa", "coat", "kid_eren"):
        top_z = (P + u * 0.10)
        if out == "coat":
            hem, r0, r1, key = 0.27, 0.085, 0.125, top
        elif out == "kid_eren":
            hem, r0, r1, key = 0.43, 0.080, 0.100, top
        elif out == "kid_mikasa":
            hem, r0, r1, key = 0.33, 0.082, 0.120, "k_cardigan"
            m.cap(P + u * 0.05, Vector((P.x, P.y, 0.30)), 0.078, 0.11, "k_dress", seg=12, ends=False)
        else:
            hem, r0, r1, key = 0.035, 0.080, 0.16, pr.get("bottom", "c_skirt") if out == "civ_f" else "c_skirt"
        if pose not in ("draped", "carried_side", "ride", "odm_fly"):
            bot = Vector((P.x, P.y + (fwd.y - 1) * 0.0, hem))
            m.cap(top_z, bot, r0, r1, key, seg=12, ends=False)
            if out == "dress" or pr.get("apron"):
                m.ell(Vector((0, (r0 + r1) / 2 + 0.006, (top_z.z + hem) / 2)), (0.075, 0.010, (top_z.z - hem) / 2 * 0.95),
                      "c_apron", rot=Matrix.Rotation(-math.atan2(r1 - r0, top_z.z - hem), 3, "X"))
        if out == "kid_eren":
            m.ell(C + fwd * 0.05 + u * 0.03, (0.032, 0.022, 0.060), "k_shirt", rot=Rt)
        if out == "coat":
            m.ell(C + fwd * 0.05 + u * 0.03, (0.030, 0.022, 0.060), "c_grisha_shirt", rot=Rt)
    if pr.get("bag"):
        wr = J["wrR"]
        m.box(wr + Vector((0.0, 0.0, -0.075)), (0.045, 0.13, 0.09), "c_bag")
    # --- ODM gear
    hooks = []
    if mil and pr.get("odm", True):
        tilt = Matrix.Rotation(math.radians(10), 3, "X")
        for s_ in (-1, 1):
            c = P + Vector((s_ * (0.098 * hipf * bulk + 0.018), -0.015, -0.075))
            m.box(c, (0.026, 0.30, 0.044), "steel", rot=tilt)
            m.cap(c + Vector((0, 0.13, 0.034)), c + Vector((0, -0.15, 0.010)), 0.013, 0.013, "steel", seg=6)
            m.box(c + Vector((0, 0.17, 0.01)), (0.022, 0.03, 0.03), "steel_dark")
            hooks.append(c + Vector((0, 0.10, 0.03)))
        m.box(P + Vector((0, -0.080, 0.025)), (0.085, 0.035, 0.055), "steel")
        m.cap(P + Vector((-0.04, -0.09, 0.05)), P + Vector((0.04, -0.09, 0.05)), 0.016, 0.016, "steel_dark", seg=6)
    # --- emblems and cape
    if mil:
        back = -fwd
        if out == "scout":
            _cape(m, deco, J, pose)
            for s_ in (-1, 1):    # shoulder badges
                deco.quad(J["sh" + ("R" if s_ > 0 else "L")] + Vector((s_ * 0.042, 0, -0.03)), (s_, 0, 0), u, 0.045, "emb_wings")
        else:
            deco.quad(J["C"] + u * 0.02 + back * (chest_r[1] + 0.006), back, u, 0.105, "emb_" + EMBLEM[out])
            deco.quad(J["C"] + u * 0.035 + fwd * (chest_r[1] + 0.004) + Vector((-0.05 * sh, 0, 0)), fwd, u, 0.04, "emb_" + EMBLEM[out])
    world = X @ Matrix.Scale(H, 4) @ BX
    return [world @ h for h in hooks], J, world

def _cape(m, deco, J, pose):
    """Green hooded cape from the shoulders to the knees, flared, with the over-sized Wings decal."""
    u, fwd, sh = J["u"], J["fwd"], J["sh"]
    top = J["Sc"] + u * 0.012 - fwd * 0.005
    flow = J["flow"]
    a0, b0 = 0.118 * sh, 0.080
    clen = 0.50 if pose != "ride" else 0.42
    nr, nc = 7, 11
    rows = []
    for i in range(nr):
        t = i / (nr - 1)
        cen = top + Vector((0, 0, -clen * t)) + flow * (t ** 1.4) * 1.6
        if pose == "odm_fly":
            cen = top - u * (clen * t) + flow * (t ** 1.4) * 1.6
        a, b = a0 * (1 + 0.55 * t), b0 * (1 + 0.85 * t)
        row = []
        for j in range(nc):
            th = math.radians(-112 + 224 * j / (nc - 1))
            r = Vector((math.sin(th) * a, -math.cos(th) * b, 0))
            if pose == "odm_fly":
                r = Vector((r.x, 0, 0)) + fwd * r.y
            row.append(cen + r)
        rows.append(row)
    m.grid(rows, "cloak", outward=top + fwd * 0.05 + Vector((0, 0, -0.2)))
    m.ell(J["N"] - fwd * 0.045 - u * 0.012, (0.085 * sh, 0.050, 0.038), "cloak", rot=_rotx(J["lean"]))    # hood bunched
    i = 2; jc = nc // 2
    p = rows[i][jc]
    du = (rows[i - 1][jc] - rows[i + 1][jc]).normalized()
    dr = (rows[i][jc + 1] - rows[i][jc - 1]).normalized()
    n = du.cross(dr).normalized()
    if n.dot(p - (top + fwd * 0.05)) < 0:
        n = -n
    deco.quad(p + n * 0.010 + du * 0.02, n, du, 0.21, "emb_wings")

def _horse(m, pr_coat="horse_bay", gait="walk", phase=0.0, X=Matrix()):
    """Simple horse in metres, facing +y, withers ~1.6 m."""
    m.X = X
    c = pr_coat
    m.ell((0, 0.05, 1.22), (0.30, 0.78, 0.33), c)
    m.ell((0, 0.62, 1.25), (0.29, 0.38, 0.36), c)
    m.ell((0, -0.58, 1.28), (0.32, 0.42, 0.35), c)
    neck0, neck1 = Vector((0, 0.80, 1.38)), Vector((0, 1.12, 1.88))
    m.cap(neck0, neck1, 0.18, 0.11, c)
    m.cap(Vector((0, 1.14, 1.92)), Vector((0, 1.48, 1.60)), 0.10, 0.07, c)
    for s_ in (-1, 1):
        m.cap(Vector((s_ * 0.05, 1.12, 2.0)), Vector((s_ * 0.06, 1.08, 2.12)), 0.025, 0.01, c, seg=5)
    m.cap(Vector((0, 0.78, 1.55)), Vector((0, 1.10, 2.02)), 0.05, 0.04, "horse_dark", seg=6)          # mane
    m.cap(Vector((0, -0.98, 1.42)), Vector((0, -1.22, 0.78)), 0.07, 0.05, "horse_dark", seg=6)         # tail
    m.ell((0, -0.05, 1.56), (0.31, 0.34, 0.07), "saddle")
    m.ell((0, -0.05, 1.50), (0.33, 0.30, 0.09), "#5A6A4A")                                              # saddle cloth
    amp = 0.35 if gait == "walk" else 0.75
    for k, (lx, ly) in enumerate([(-0.17, 0.62), (0.17, 0.62), (-0.18, -0.58), (0.18, -0.58)]):
        ph = phase + (0, math.pi, math.pi * 0.5, math.pi * 1.5)[k]
        a = math.sin(ph) * amp
        top_ = Vector((lx, ly, 1.10))
        knee = top_ + Vector((0, math.sin(a) * 0.48, -math.cos(a) * 0.48))
        bend = max(0.0, math.cos(ph)) * (0.9 if gait != "walk" else 0.5) * (1 if ly > 0 else -1)
        hoof = knee + Vector((0, math.sin(a - bend) * 0.50, -math.cos(a - bend) * 0.50))
        m.cap(top_, knee, 0.085, 0.055, c)
        m.cap(knee, hoof, 0.045, 0.040, c)
        m.cap(hoof, hoof + Vector((0, 0.03, -0.06)), 0.050, 0.055, "hoof", seg=6)
        if k < 2:
            m.cap(Vector((lx * 0.9, ly - 0.05, 1.45)), Vector((lx * 1.35, 0.0, 0.95)), 0.006, 0.006, "harness", seg=4, ends=False)

# ---------------------------------------------------------------- prototypes + instancing
_PROTO = {}

def _root_coll():
    c = bpy.data.collections.get("PK_People")
    if c is None:
        c = L.new_coll("PK_People")
    return c

def _proto_parent():
    c = bpy.data.collections.get("PK_Protos")
    if c is None:
        c = L.new_coll("PK_Protos")
        lc = bpy.context.view_layer.layer_collection.children.get("PK_Protos")
        if lc:
            lc.exclude = True
    return c

def prototype(preset, pose="stand", phase=0.0, coat=None):
    """Hidden collection holding one built figure (body + ink + decals); cached per scene."""
    key = (preset, pose, round(phase, 2), coat)
    p = _PROTO.get(key)
    if p and p["coll"].name in bpy.data.collections:
        return p
    pr = get_preset(preset)
    name = f"PK_{pr['name']}_{pose}{'' if not phase else '_%d' % int(phase * 100)}"
    coll = bpy.data.collections.new(name); _proto_parent().children.link(coll)
    m, deco = Mesh(), Mesh()
    hooks, J, wM = [], None, Matrix()
    if pose == "ride":
        _horse(m, coat or random.Random(hash(preset) & 255).choice(["horse_bay", "horse_bay", "horse_chestnut", "horse_grey"]),
               "walk", phase)
    if pose == "carry_kids":
        hooks, J, wM = build_figure(m, deco, pr, "carry_kids", phase)
        H = pr["H"]
        shR = wM @ J["shR"]; hipL = wM @ J["hipL"]
        ke = get_preset("eren_child"); km = get_preset("mikasa_child")
        build_figure(m, deco, ke, "draped", 0.0, Matrix.Translation(shR + Vector((0.0, 0.05, 0.10))))
        build_figure(m, deco, km, "carried_side", 0.0,
                     Matrix.Translation(hipL + Vector((-0.12, 0.06, 0.12))) @ Matrix.Rotation(0.5, 4, "Z"))
    else:
        hooks, J, wM = build_figure(m, deco, pr, pose, phase)
    body = m.finish(name + "_body", coll)
    deco.finish(name + "_decal", coll, ink=0)
    p = {"coll": coll, "hooks": hooks, "pr": pr, "J": J, "wM": wM}
    _PROTO[key] = p
    return p

def ground(x, y):
    g = L.height(x, y)
    if L.in_district(x, y, 0.0):
        g = max(g, 0.0) + 0.16
    return g

def _instance(p, loc, yaw, scale=1.0, name=None):
    e = bpy.data.objects.new(name or ("I_" + p["coll"].name), None)
    e.instance_type = "COLLECTION"; e.instance_collection = p["coll"]
    e.location = loc; e.rotation_euler = (0, 0, yaw); e.scale = (scale,) * 3
    _root_coll().objects.link(e)
    return e

def person(preset, loc, yaw=0.0, pose="stand", phase=0.0, scale=1.0, anchors=None, trail=True, coat=None):
    """Place one figure; returns the instance empty (see module doc)."""
    p = prototype(preset, pose, phase, coat)
    if len(loc) == 2:
        z = ground(loc[0], loc[1])
        if pose == "odm_fly":
            z += 6.0
        loc = (loc[0], loc[1], z)
    e = _instance(p, Vector(loc), yaw, scale, name=f"P_{preset}_{pose}")
    if pose == "odm_fly" and p["hooks"]:
        bpy.context.view_layer.update()
        W = e.matrix_world
        hooks = [W @ h for h in p["hooks"]]
        f = Vector((-math.sin(yaw), math.cos(yaw), 0))
        side = Vector((math.cos(yaw), math.sin(yaw), 0))
        if anchors is None:
            anchors = [Vector(loc) + f * 22 + side * s_ * 7 + Vector((0, 0, 9)) for s_ in (-1, 1)]
        wires(hooks, anchors, name=f"Wire_{preset}")
        if trail:
            gas_trail(W @ (p["wM"] @ (p["J"]["P"] + Vector((0, -0.09, 0.03)))), -f)
    return e

def wires(starts, ends, name="Wire", r=0.022):
    m = Mesh()
    for a, b in zip(starts, ends):
        m.cap(Vector(a), Vector(b), r, r, "steel_dark", seg=5, ends=False)
    return m.finish(name, _root_coll(), ink=0)

_GAS = None
def gas_trail(start, direction, length=7.0, n=12, seed=0):
    """Puffs of white gas streaming back from the ODM unit."""
    global _GAS
    if _GAS is None or _GAS.name not in bpy.data.materials:
        _GAS = bpy.data.materials.new("PK_Gas"); _GAS.use_nodes = True
        b = _GAS.node_tree.nodes["Principled BSDF"]
        b.inputs["Base Color"].default_value = (0.95, 0.96, 0.98, 1); b.inputs["Alpha"].default_value = 0.45
        b.inputs["Roughness"].default_value = 1.0
        b.inputs["Emission Color"].default_value = (1, 1, 1, 1); b.inputs["Emission Strength"].default_value = 0.15
    rnd = random.Random(seed)
    bm = bmesh.new()
    d = Vector(direction).normalized()
    for k in range(n):
        t = (k + 1) / n
        c = Vector(start) + d * (length * t) + Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-0.5, 0.8))) * 0.35 * t
        r = 0.10 + 0.55 * t
        res = bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
        for v in res["verts"]:
            v.co += c
    for f in bm.faces:
        f.smooth = True
    ob = L.obj_from_bm("PK_GasTrail", bm, [_GAS], coll=_root_coll())
    return ob

def horse_only(loc, yaw=0.0, coat="horse_bay", gait="walk", phase=0.0):
    key = ("horse", coat, gait, round(phase, 2))
    p = _PROTO.get(key)
    if not (p and p["coll"].name in bpy.data.collections):
        coll = bpy.data.collections.new(f"PK_horse_{coat}"); _proto_parent().children.link(coll)
        m = Mesh(); _horse(m, coat, gait, phase); m.finish(coll.name + "_body", coll)
        p = {"coll": coll}; _PROTO[key] = p
    if len(loc) == 2:
        loc = (loc[0], loc[1], ground(*loc))
    return _instance(p, Vector(loc), yaw)

def crowd(preset_list, area, count, pose="stand", yaw=0.0, seed=1, spacing=None, formation="grid",
          jitter=0.15, front=(), phase_var=True, yaw_jitter=0.08):
    """Instanced crowd (see module doc). Generic names expand into their variant pools."""
    rnd = random.Random(seed)
    cx, cy, w, d = area[:4]
    rot = area[4] if len(area) > 4 else yaw
    pool = []
    for n in preset_list:
        if n in GENERIC:
            pool += [f"{n}:{k}" for k in range(NVAR)]
        else:
            pool.append(n)
    cells = []
    if formation == "grid":
        sx = spacing[0] if spacing else 1.25
        sy = spacing[1] if spacing else 1.45
        ncol = max(1, int(round(w / sx)))
        nrow = int(math.ceil(count / ncol))
        for r in range(nrow):
            for c in range(ncol):
                if len(cells) >= count:
                    break
                lx = (c - (ncol - 1) / 2) * sx + rnd.uniform(-jitter, jitter)
                ly = ((nrow - 1) / 2 - r) * sy + rnd.uniform(-jitter, jitter)   # row 0 = front (+y local)
                cells.append((lx, ly, r, c, ncol))
    else:
        mind = spacing[0] if spacing else 0.9
        tries = 0
        while len(cells) < count and tries < count * 60:
            tries += 1
            lx, ly = rnd.uniform(-w / 2, w / 2), rnd.uniform(-d / 2, d / 2)
            if all((lx - a) ** 2 + (ly - b) ** 2 > mind * mind for a, b, *_ in cells):
                cells.append((lx, ly, 0, 0, 1))
    # named presets take the front-row centre cells
    order = sorted(range(len(cells)), key=lambda i: (cells[i][2], abs(cells[i][3] - (cells[i][4] - 1) / 2)))
    named = {order[k]: n for k, n in enumerate(front) if k < len(order)}
    cr, sr = math.cos(rot), math.sin(rot)
    out = []
    phases = [0.0, 0.8, 1.6, 2.4, 3.2, 4.0, 4.8, 5.6] if (phase_var and pose in ("walk", "run")) else [0.0]
    for i, (lx, ly, *_r) in enumerate(cells):
        name = named.get(i) or rnd.choice(pool)
        ph = rnd.choice(phases)
        x, y = cx + lx * cr - ly * sr, cy + lx * sr + ly * cr
        fy = rot + (rnd.uniform(-math.pi, math.pi) if formation == "scatter" and pose == "stand" else rnd.uniform(-yaw_jitter, yaw_jitter))
        p = prototype(name, pose, ph)
        e = _instance(p, Vector((x, y, ground(x, y))), fy, rnd.uniform(0.97, 1.03) if name in GENERIC or ":" in name else 1.0,
                      name=f"C_{name.replace(':', '')}_{i:03d}")
        e["pk_preset"] = name
        out.append(e)
    return out

def drain(insts, waves=3, start=1, gap=48, dur=90, exit=(0.0, -60.0), keep=20, seed=3):
    """Crowd drain (H13): all but `keep` figures leave in `waves`, walking toward exit offset, then vanish."""
    rnd = random.Random(seed)
    idx = list(range(len(insts))); rnd.shuffle(idx)
    stay = set(idx[:keep])
    leave = [i for i in idx if i not in stay]
    for k, i in enumerate(leave):
        e = insts[i]
        w = k * waves // max(1, len(leave))
        f0 = start + w * gap + rnd.randint(0, 12)
        e.keyframe_insert("location", frame=f0)
        e.keyframe_insert("scale", frame=f0)
        e.location = e.location + Vector((exit[0] + rnd.uniform(-6, 6), exit[1], 0))
        e.keyframe_insert("location", frame=f0 + dur)
        e.keyframe_insert("scale", frame=f0 + dur - 1)
        e.scale = (0.0, 0.0, 0.0)
        e.keyframe_insert("scale", frame=f0 + dur)
        e.location = e.location - Vector((exit[0], exit[1], 0))
    return [insts[i] for i in stay]

# ---------------------------------------------------------------- ceremony set
def _point_light(name, loc, energy, color=(1.0, 0.55, 0.22), radius=0.3):
    ld = bpy.data.lights.new(name, "POINT"); ld.energy = energy; ld.color = color; ld.shadow_soft_size = radius
    ob = bpy.data.objects.new(name, ld); ob.location = loc
    _root_coll().objects.link(ob)
    return ob

_FIRE = None
def _fire_mat():
    global _FIRE
    if _FIRE is None or _FIRE.name not in bpy.data.materials:
        _FIRE = bpy.data.materials.new("PK_Fire"); _FIRE.use_nodes = True
        b = _FIRE.node_tree.nodes["Principled BSDF"]
        b.inputs["Base Color"].default_value = (1.0, 0.45, 0.1, 1)
        b.inputs["Emission Color"].default_value = (1.0, 0.42, 0.08, 1)
        b.inputs["Emission Strength"].default_value = 18.0 if NIGHT else 4.0
    _MATS["pk_fire"] = _FIRE
    return _FIRE

def stage(loc, yaw=0.0, banner=True, torches=8):
    """Small wooden stage facing local +y (yaw rotates), banner behind, braziers at the front corners."""
    _fire_mat()
    gx, gy = loc[0], loc[1]
    g = ground(gx, gy)
    X = Matrix.Translation((gx, gy, g)) @ Matrix.Rotation(yaw, 4, "Z")
    m = Mesh(); m.X = X
    sw, sd, shh = 9.0, 4.5, 1.4
    m.box((0, 0, shh / 2), (sw, sd, shh), "wood")
    m.box((0, 0, shh + 0.04), (sw + 0.3, sd + 0.3, 0.08), "wood_dark")
    for k in range(4):
        m.box((0, sd / 2 + 0.35 + k * 0.35, shh * (3 - k) / 4 / 2), (2.4, 0.35, shh * (3 - k) / 4), "wood")
    for s_ in (-1, 1):
        for yy in (-sd / 2 + 0.2, sd / 2 - 0.2):
            m.box((s_ * (sw / 2 - 0.2), yy, shh / 2), (0.3, 0.3, shh), "wood_dark")
    if banner:
        for s_ in (-1, 1):
            m.cap(Vector((s_ * 3.3, -sd / 2 + 0.3, shh)), Vector((s_ * 3.3, -sd / 2 + 0.3, shh + 6.8)), 0.09, 0.07, "wood_dark", seg=6, ends=False)
        m.cap(Vector((-3.6, -sd / 2 + 0.3, shh + 6.6)), Vector((3.6, -sd / 2 + 0.3, shh + 6.6)), 0.07, 0.07, "wood_dark", seg=6)
    # braziers
    fires = []
    for s_ in (-1, 1):
        b = Vector((s_ * (sw / 2 + 1.4), sd / 2 + 0.8, 0))
        for k in range(3):
            a = k * 2 * math.pi / 3
            m.cap(b + Vector((math.cos(a) * 0.45, math.sin(a) * 0.45, 0)), b + Vector((0, 0, 1.1)), 0.04, 0.04, "iron", seg=5, ends=False)
        m.cap(b + Vector((0, 0, 1.05)), b + Vector((0, 0, 1.45)), 0.30, 0.55, "iron", seg=10, ends=False)
        fires.append((b + Vector((0, 0, 1.45)), 0.5, 1.2))
    body = m.finish("PK_Stage", _root_coll())
    # banner cloth with the Wings of Freedom on dark green
    if banner:
        _emblem_mat("wings", N=160, field=srgb("#2F4A3A"))
        dm = Mesh(); dm.X = X
        dm.quad(Vector((0, -sd / 2 + 0.36, shh + 3.6)), (0, 1, 0), (0, 0, 1), 5.8, "emb_wings_banner")
        dm.finish("PK_Banner", _root_coll(), ink=0)
    # fire tongues + lights
    fm = bmesh.new()
    rnd = random.Random(4)
    pts = [(X @ c, r, h) for c, r, h in fires]
    # torches on poles round the square in front of the stage
    for k in range(torches):
        side = -1 if k % 2 == 0 else 1
        row = k // 2
        p = Vector((side * (sw / 2 + 6 + row * 1.5), sd / 2 + 4 + row * 6.0, 0))
        tm = Mesh(); tm.X = X
        tm.cap(p, p + Vector((0, 0, 3.2)), 0.05, 0.04, "wood_dark", seg=5, ends=False)
        tm.cap(p + Vector((0, 0, 3.15)), p + Vector((0, 0, 3.45)), 0.09, 0.12, "iron", seg=6, ends=False)
        tm.finish(f"PK_Torch{k}", _root_coll(), ink=0)
        pts.append((X @ (p + Vector((0, 0, 3.45))), 0.14, 0.55))
    for c, r, h in pts:
        for j in range(3):
            res = bmesh.ops.create_cone(fm, cap_ends=True, segments=8, radius1=r * (1 - j * 0.25), radius2=0.0, depth=h * (1 - j * 0.2))
            off = Vector((rnd.uniform(-1, 1) * r * 0.3, rnd.uniform(-1, 1) * r * 0.3, h * (1 - j * 0.2) / 2))
            for v in res["verts"]:
                v.co += c + off
    L.obj_from_bm("PK_Fires", fm, [_FIRE], coll=_root_coll())
    for k, (c, r, h) in enumerate(pts):
        _point_light(f"PK_FireLight{k}", c + Vector((0, 0, h * 0.6)), (900 if r > 0.3 else 260) * (1.0 if NIGHT else 0.25))
    return {"top": X @ Vector((0, 0, shh + 0.08)), "X": X}

# ---------------------------------------------------------------- demo sets (plug-in mode)
LINEUP = ["erwin", "levi", "hannes", "pixis", "carla", "grisha", "eren_child", "mikasa_child",
          "eren", "mikasa", "armin", "jean", "connie", "sasha", "reiner", "bertholdt", "christa", "ymir",
          "annie", "marco", "cadet", "cadet:1", "garrison", "garrison:4", "scout", "scout:1", "mp", "mp:1",
          "civilian", "civilian:1"]
POSES = ["stand", "walk", "run", "salute", "kneel", "carry_kids", "ride", "odm_fly"]
PLZ = Vector((L.PLAZA[0], L.PLAZA[1]))
LINE_Y = PLZ.y - 21.0
POSE_Y = PLZ.y + 21.0
CER = Vector((0.0, -36.0))            # inner gate square
CER_STAGE = Vector((0.0, -19.0))
CER_CROWD = Vector((0.0, -38.0))

def demo_lineup():
    n = len(LINEUP); per = (n + 1) // 2
    for i, name in enumerate(LINEUP):
        r, c = divmod(i, per)
        x = PLZ.x + (c - (per - 1) / 2) * 1.75
        y = LINE_Y - r * 3.2
        person(name, (x, y), yaw=math.pi, pose="stand")

def demo_poses():
    who = {"stand": "erwin", "walk": "mikasa", "run": "eren", "salute": "armin", "kneel": "levi",
           "carry_kids": "hannes", "ride": "erwin", "odm_fly": "levi"}
    for i, pz in enumerate(POSES):
        x = PLZ.x + (i - (len(POSES) - 1) / 2) * 3.4
        yaw = 0.0 if pz not in ("ride", "odm_fly", "run", "carry_kids", "walk") else -math.pi / 2
        if pz == "odm_fly":
            person(who[pz], (x, POSE_Y, ground(x, POSE_Y) + 3.2), yaw=-math.pi / 2, pose=pz,
                   anchors=[Vector((x - 16, POSE_Y + 6, 14)), Vector((x - 16, POSE_Y - 6, 12))])
        else:
            person(who[pz], (x, POSE_Y), yaw=yaw, pose=pz, phase=1.2)
    horse_only((PLZ.x + 16.5, POSE_Y + 2.0), yaw=-0.3, coat="horse_grey")

def demo_ceremony():
    st = stage(CER_STAGE, yaw=math.pi)       # stage faces south (toward the cadets)
    top = st["top"]
    person("erwin", (top.x, top.y - 0.6, top.z), yaw=math.pi, pose="stand", scale=1.04)
    for s_ in (-1, 1):
        person("scout:%d" % (2 + s_), (top.x + s_ * 2.6, top.y + 1.2, top.z), yaw=math.pi, pose="stand")
    front = ["mikasa", "armin", "jean", "connie", "sasha", "reiner", "bertholdt", "christa", "ymir", "eren"]
    # 200 cadets facing north (+y) toward the stage
    crowd(["cadet"], (CER_CROWD.x, CER_CROWD.y, 25.0, 14.0), 200, "salute", yaw=0.0, front=front,
          spacing=(1.25, 1.45))

def night():
    """Torch-lit night: dim sun and sky (ceremony H13/H14)."""
    sc = bpy.context.scene
    for o in sc.objects:
        if o.type == "LIGHT" and o.data.type == "SUN":
            o.data.energy = 0.10; o.data.color = (0.55, 0.65, 1.0)
    w = sc.world
    if w and w.node_tree:
        for n in w.node_tree.nodes:
            if n.type == "BACKGROUND":
                n.inputs[1].default_value *= 0.02
    hz = bpy.data.objects.get("Haze")
    if hz:
        hz.hide_render = True

def build(M, year, ctx):
    _MATS.clear(); _PROTO.clear()
    cam = getattr(getattr(L, "A", None), "cam", "") or ""
    if not (cam.startswith("kit_") or os.environ.get("PK_DEMO") == "1"):
        return
    if cam.startswith("kit_lineup") or os.environ.get("PK_DEMO") == "1":
        demo_lineup()
    if cam.startswith("kit_poses") or os.environ.get("PK_DEMO") == "1":
        demo_poses()
    if cam.startswith("kit_ceremony") or os.environ.get("PK_DEMO") == "1":
        demo_ceremony()
        if NIGHT:
            night()
    print(f"[people_kit] prototypes {len(_PROTO)}, instances {len(_root_coll().objects)}")

CAMS = {
    "kit_lineup":      ((PLZ.x + 7.0, LINE_Y - 22.0, 14.0), (PLZ.x, LINE_Y - 1.6, 0.9), 26),
    "kit_lineup_back": ((PLZ.x - 9.0, LINE_Y + 14.0, 11.0), (PLZ.x, LINE_Y - 1.6, 0.9), 26),
    "kit_detail":      ((PLZ.x - 6.0, LINE_Y - 9.0, 4.5), (PLZ.x - 6.0, LINE_Y - 1.6, 1.0), 40),   # dev check only
    "kit_detail_back": ((PLZ.x - 6.0, LINE_Y + 6.0, 4.5), (PLZ.x - 6.0, LINE_Y - 1.6, 1.0), 40),
    "kit_poses":       ((PLZ.x + 5.0, POSE_Y + 15.0, 9.0), (PLZ.x, POSE_Y, 1.2), 30),
    "kit_ceremony":    ((14.0, CER_CROWD.y - 30.0, 24.0), (0.0, -30.0, 1.0), 32),
    "kit_ceremony_hi": ((20.0, CER_CROWD.y - 48.0, 52.0), (0.0, -30.0, 0.0), 32),
}
LABELS = {}
