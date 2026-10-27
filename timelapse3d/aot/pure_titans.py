"""Pure (mindless) Titans in the Season 1 anime style, for Blender 5.2 + MPFB2 (MakeHuman CC0 base mesh).

    import sys; sys.path.insert(0, "/home/user/YTP1/timelapse3d/aot")
    import pure_titans as PT
    rig = PT.make_pure("smiling")                    # Dina, the Smiling Titan (15 m)
    rig = PT.make_pure("generic", seed=3)            # seed picks a variant from GENERIC + jitter
    rig = PT.make_pure("generic", preset="potbelly", height=5)
    PT.walk_action(rig, cycle_frames=48, offset=7)   # looping walk Action on the rig

make_pure() returns the armature object. Everything (body, eyes, hair, ink outline) is ONE mesh object
parented to it, so a crowd is cheap to duplicate (rig.copy() + mesh .copy() sharing data, or make more).
Materials are Principled BSDF + procedural / attribute nodes only (Eevee-safe):
  * skin: fixed colour, muscle/crease "ink" lines from a baked concavity attribute + rib lines,
    the painted face (grin / teeth / gaping mouth) driven by a baked face-UV attribute;
  * eyes: white ball + small dark iris; hair: flat colour; outline: inverted hull (Solidify) whose
    Principled alpha hides front-facing shell faces (works in Cycles and Eevee, plus backface culling).

walk_action(rig, cycle_frames, offset, travel=True) keys a lumbering, slightly unsteady gait on the
pose bones. With travel=True the root bone walks forward (rig's local -Y) forever via a
REPEAT_OFFSET Cycles modifier, with feet planted (no sliding); with travel=False it walks in place
and rig["walk_stride_m"] tells you how far to move it per cycle (metres, world scale).
"""
import bpy, bmesh, importlib, math, os, random, sys
from mathutils import Vector, Matrix, Quaternion

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import titans as _T  # reuse MPFB service handles + mask-clean helper (titans.py is not modified)

HS, TS, ASSET = _T.HS, _T.TS, _T.ASSET
TDIR = _T.TDIR
EXPR = os.path.join(TDIR, "expression", "units", "caucasian")

# --------------------------------------------------------------------------------------------- presets
LR = lambda t, w: [(t.format(s="l"), w), (t.format(s="r"), w)]

def _ex(name, w):
    return ("@" + name, w)          # "@" = expression unit target (left/right handled by caller names)

# shared face / body building blocks for the S1 "dopey" look
WIDE_MOUTH = [("mouth/mouth-scale-horiz-incr", 1.0), ("mouth/mouth-upperlip-volume-decr", 1.0),
              ("mouth/mouth-lowerlip-volume-decr", 1.0)]
HEAVY_BROW = [("eyebrows/eyebrows-trans-forward", 1.0), ("eyebrows/eyebrows-trans-down", 0.6),
              ("forehead/forehead-nubian-incr", 0.6)]
WIDE_EYES = LR("eyes/{s}-eye-scale-incr", 1.0) + LR("eyes/{s}-eye-height2-incr", 1.0) + \
            [("@eye-left-opened-up", 1.0), ("@eye-right-opened-up", 1.0)]
LONG_ARMS = [("arms/measure-upperarm-length-incr", 1.0), ("arms/measure-lowerarm-length-incr", 1.0)]
SHORT_LEGS = [("legs/measure-upperleg-height-decr", 1.0), ("legs/measure-lowerleg-height-decr", 1.0),
              ("legs/lowerlegs-height-decr", 1.0)]
SOFT_TORSO = [("torso/torso-scale-horiz-incr", 1.0), ("torso/torso-scale-depth-incr", 0.6),
              ("stomach/stomach-pregnant-incr", 0.5), ("torso/torso-vshape-decr", 0.8), ("hip/hip-scale-horiz-incr", 0.5)]

PRESETS = {
    # Dina Fritz / "Smiling Titan" (S1E2). Design bible 3.3: very tall, male-looking, emaciated with visible
    # ribs, unusually long neck, long thin arms, forward lean; chin-length light-brown bob (custom mesh, with
    # bangs); lips pulled back showing both rows of ivory teeth + red gums; sunken grey eyes. 12-15 m [EST].
    "smiling": dict(
        height=14.0, head=1.22, gender=0.9, age=0.5, muscle=0.35, weight=0.0, proportions=0.35, cupsize=0.0,
        skin=(0.66, 0.30, 0.17), mottle=0.06,
        hair=("custom_bob", (0.22, 0.125, 0.065), dict(bangs_h=2.4, length=1.0)),
        mouth=dict(kind="grin", width=2.2, up=0.62, low=0.80, cu=0.05, cl=0.13, bite=0.04, teeth=16, gums=0.17,
                   recess=0.2),
        eyes=dict(scale=0.92, iris=0.40, iris_col=(0.22, 0.22, 0.21), push=0.0, socket=0.45), ribs=1.25,
        lines=1.15, slouch=0.42, arms=1.00, brow=0.0,
        targets=WIDE_MOUTH + [("mouth/mouth-angles-up", 0.6),
                 ("head/head-oval", 0.5), ("head/head-fat-decr", 1.0), ("chin/chin-prominent-incr", 0.5),
                 ("nose/nose-scale-vert-incr", 0.6), ("nose/nose-scale-depth-incr", 0.5),
                 ("neck/measure-neck-height-incr", 1.0), ("neck/neck-scale-vert-incr", 1.0),
                 ("neck/measure-neck-circ-decr", 0.6)] + LONG_ARMS + [
                 ("arms/measure-upperarm-circ-decr", 0.8), ("legs/measure-thigh-circ-decr", 0.6),
                 ("torso/measure-waist-circ-decr", 0.8), ("stomach/stomach-pregnant-decr", 0.6)]
                + LR("eyes/{s}-eye-push1-in", 0.5) + LR("eyes/{s}-eye-push2-in", 0.4)
                + LR("cheek/{s}-cheek-bones-incr", 1.0) + LR("cheek/{s}-cheek-volume-decr", 1.0)
                + [_ex("mouth-corner-puller", 0.6)],
        gait=dict(stride=0.58, knee=0.6, sway=0.022, bob=0.06, arm=0.22, limp=0.06)),
}
# Generic S1 pure titans (group still, S1E1-E5). Heads ~1/5-1/6 of height, soft broad torsos, short legs or
# long dangling arms, wide dopey grins, blank wide eyes, heavy brows; 3 bald, the rest short messy hair.
GENERIC = {
    # centre of the group still: bald, tall, ruddy, huge open grin full of teeth, long dangling arms
    "bald_grinner": dict(
        height=13.0, head=1.55, gender=1.0, age=0.85, muscle=0.15, weight=0.55, proportions=0.1,
        skin=(0.66, 0.20, 0.11), hair=None,
        mouth=dict(kind="open_grin", width=1.9, up=0.65, low=1.0, cu=0.04, cl=0.10, bite=0.30, teeth=13, recess=0.18),
        eyes=dict(scale=1.05, iris=0.22, push=0.004), ribs=0.6, lines=1.2, slouch=0.30, arms=1.0, brow=1.0,
        targets=WIDE_MOUTH + HEAVY_BROW + LONG_ARMS + [("head/head-oval", 1.0), ("head/head-scale-vert-incr", 0.8),
                 ("neck/measure-neck-height-incr", 0.6), ("torso/torso-scale-horiz-incr", 0.4)]
                + LR("cheek/{s}-cheek-volume-decr", 0.6) + [_ex("mouth-open", 0.4)],
        gait=dict(stride=0.54, knee=0.6, sway=0.03, bob=0.07, arm=0.32, limp=0.10)),
    # short messy blond hair, soft fat torso, short legs, sleepy half-shut eyes, dopey closed grin
    "blond_sleeper": dict(
        height=10.0, head=1.6, gender=1.0, age=0.45, muscle=0.1, weight=0.9, proportions=0.2,
        skin=(0.74, 0.33, 0.18), hair=("short02", (0.42, 0.24, 0.09), dict(messy=1.0)),
        mouth=dict(kind="grin", width=1.8, up=0.40, low=0.55, cu=0.05, cl=0.14, bite=0.04, teeth=14, recess=0.18),
        eyes=dict(scale=1.0, iris=0.30, push=-0.003, closed=0.6), ribs=0.0, lines=0.9, slouch=0.45, arms=0.85,
        brow=0.7,
        targets=WIDE_MOUTH + SOFT_TORSO + SHORT_LEGS[:2] + [("head/head-round", 0.8), ("head/head-fat-incr", 0.8),
                 ("neck/neck-double-incr", 0.6)] + [_ex("eye-left-closure", 0.6), _ex("eye-right-closure", 0.6)],
        gait=dict(stride=0.45, knee=0.45, sway=0.04, bob=0.05, arm=0.18, limp=0.04)),
    # dark short messy hair, broad square body, white staring eyes, skull grin
    "pale_starer": dict(
        height=8.0, head=1.65, gender=1.0, age=0.55, muscle=0.3, weight=0.7, proportions=0.2,
        skin=(0.76, 0.38, 0.23), hair=("short04", (0.03, 0.022, 0.018), dict(messy=1.0)),
        mouth=dict(kind="grin", width=2.0, up=0.50, low=0.62, cu=0.02, cl=0.09, bite=0.04, teeth=15, recess=0.18),
        eyes=dict(scale=1.3, iris=0.12, push=0.007), ribs=0.3, lines=1.0, slouch=0.12, arms=0.95, brow=0.9,
        targets=WIDE_MOUTH + WIDE_EYES + HEAVY_BROW + [("head/head-square", 0.7), ("torso/torso-scale-horiz-incr", 1.0),
                 ("torso/torso-scale-depth-incr", 0.4)] + LR("cheek/{s}-cheek-volume-decr", 0.5),
        gait=dict(stride=0.45, knee=0.5, sway=0.03, bob=0.05, arm=0.25, limp=0.08)),
    # bald potbellied dwarf: very short legs, enormous head, dopey wide grin, wide eyes
    "potbelly": dict(
        height=5.0, head=1.85, gender=1.0, age=0.6, muscle=0.0, weight=1.0, proportions=0.0,
        skin=(0.75, 0.34, 0.19), hair=None,
        mouth=dict(kind="grin", width=1.9, up=0.35, low=0.50, cu=0.08, cl=0.16, bite=0.04, teeth=14, recess=0.18),
        eyes=dict(scale=1.25, iris=0.18, push=0.006), ribs=0.0, lines=0.8, slouch=0.08, arms=0.7, brow=0.8,
        targets=WIDE_MOUTH + WIDE_EYES + SHORT_LEGS + [("stomach/stomach-pregnant-incr", 1.0),
                 ("head/head-round", 1.0), ("head/head-fat-incr", 1.0), ("neck/neck-double-incr", 1.0),
                 ("torso/torso-scale-horiz-incr", 0.6)],
        gait=dict(stride=0.6, knee=0.5, sway=0.05, bob=0.04, arm=0.18, limp=0.05)),
    # (was longhair_gaper) messy brown hair, gaunt chest + soft belly, gaping O mouth, very long arms, deep slouch
    "messy_gaper": dict(
        height=7.0, head=1.6, gender=1.0, age=0.5, muscle=0.1, weight=0.45, proportions=0.2,
        skin=(0.70, 0.32, 0.18), hair=("short03", (0.13, 0.07, 0.035), dict(messy=1.0)),
        mouth=dict(kind="gape", width=0.75, up=0.55, low=0.95, cu=0.0, cl=0.0, bite=0.0, teeth=0, recess=0.2),
        eyes=dict(scale=1.25, iris=0.14, push=0.006), ribs=0.8, lines=1.0, slouch=0.55, arms=1.0, brow=0.8,
        targets=WIDE_EYES + HEAVY_BROW + LONG_ARMS + [("head/head-oval", 0.6), ("stomach/stomach-pregnant-incr", 0.5)]
                + LR("cheek/{s}-cheek-volume-decr", 1.0) + [_ex("mouth-open", 1.0)],
        gait=dict(stride=0.46, knee=0.5, sway=0.02, bob=0.07, arm=0.34, limp=0.12)),
    # wide ruddy brute: barrel torso, short legs, gritted open grin, small eyes under a heavy brow
    "ruddy_brute": dict(
        height=12.0, head=1.45, gender=1.0, age=0.5, muscle=0.6, weight=1.0, proportions=0.3,
        skin=(0.58, 0.17, 0.09), hair=("short01", (0.25, 0.10, 0.045), dict(messy=1.0)),
        mouth=dict(kind="open_grin", width=1.8, up=0.45, low=0.70, cu=0.0, cl=0.06, bite=0.14, teeth=12, recess=0.18),
        eyes=dict(scale=0.85, iris=0.30, push=-0.002), ribs=0.2, lines=1.3, slouch=0.3, arms=1.15, brow=1.3,
        targets=WIDE_MOUTH + HEAVY_BROW + SOFT_TORSO + SHORT_LEGS[:1] + [("head/head-square", 0.8),
                 ("chin/chin-width-incr", 0.8)] + [_ex("mouth-retraction", 0.6)],
        gait=dict(stride=0.5, knee=0.55, sway=0.045, bob=0.06, arm=0.22, limp=0.07)),
    # 3-4 m bald runt: child proportions, giant round head, staring grin
    "runt": dict(
        height=3.5, head=1.8, gender=1.0, age=0.15, muscle=0.2, weight=0.7, proportions=0.1,
        skin=(0.76, 0.36, 0.21), hair=None,
        mouth=dict(kind="grin", width=1.7, up=0.30, low=0.45, cu=0.06, cl=0.15, bite=0.03, teeth=12, recess=0.18),
        eyes=dict(scale=1.35, iris=0.16, push=0.007), ribs=0.0, lines=0.8, slouch=0.05, arms=0.9, brow=0.6,
        targets=WIDE_MOUTH + WIDE_EYES + [("head/head-round", 1.0), ("legs/measure-upperleg-height-decr", 0.6)],
        gait=dict(stride=0.54, knee=0.6, sway=0.03, bob=0.05, arm=0.3, limp=0.05)),
}
PRESETS.update(GENERIC)
GENERIC_KEYS = list(GENERIC.keys())
PRESETS["longhair_gaper"] = GENERIC["messy_gaper"]   # old name kept as an alias
# autopilot 10/28: the titan IN THE WALL (s2 ending, seen at ~60 m): pale_starer's head without the googly white eyes /
# unibrow - sunken eyes with a big dark iris (smiling-style socket), lighter brows. Not in GENERIC (never picked by seed).
PRESETS["wall_face"] = dict(PRESETS["pale_starer"], hair=None, brow=0.35,
                            eyes=dict(scale=1.0, iris=0.46, iris_col=(0.20, 0.16, 0.12), push=0.0, socket=0.55),
                            targets=WIDE_MOUTH + [("head/head-square", 0.5)] + LR("cheek/{s}-cheek-volume-decr", 0.5))
PART_TOP = 4.5   # centre part: strands below eye_z + PART_TOP * eye_radius are moved fully off the face

# --------------------------------------------------------------------------------------------- shader helpers
class _NB:
    def __init__(s, mat):
        mat.use_nodes = True
        s.nt = mat.node_tree; s.N = s.nt.nodes; s.L = s.nt.links
        s.bsdf = s.N.get("Principled BSDF")

    def _in(s, sock, v):
        if isinstance(v, (int, float)):
            sock.default_value = v
        elif isinstance(v, tuple):
            sock.default_value = v
        else:
            s.L.new(v, sock)

    def m(s, op, a, b=0.0, c=0.0, clamp=False):
        n = s.N.new("ShaderNodeMath"); n.operation = op; n.use_clamp = clamp
        s._in(n.inputs[0], a); s._in(n.inputs[1], b); s._in(n.inputs[2], c)
        return n.outputs[0]

    add = lambda s, a, b: s.m("ADD", a, b)
    sub = lambda s, a, b: s.m("SUBTRACT", a, b)
    mul = lambda s, a, b: s.m("MULTIPLY", a, b)
    mad = lambda s, a, b, c: s.m("MULTIPLY_ADD", a, b, c)

    def attr(s, name, out="Vector"):
        n = s.N.new("ShaderNodeAttribute"); n.attribute_name = name
        return n.outputs[out]

    def sep(s, v):
        n = s.N.new("ShaderNodeSeparateXYZ"); s.L.new(v, n.inputs[0]); return n.outputs

    def step(s, d, e=0.01):
        """~1 where d > 0 (smooth over +-e)."""
        n = s.N.new("ShaderNodeMapRange"); s._in(n.inputs["Value"], d)
        n.inputs["From Min"].default_value = -e; n.inputs["From Max"].default_value = e
        return n.outputs["Result"]

    def mix(s, f, a, b):
        n = s.N.new("ShaderNodeMix"); n.data_type = "RGBA"; n.clamp_factor = True
        s._in(n.inputs["Factor"], f); s._in(n.inputs[6], a); s._in(n.inputs[7], b)
        return n.outputs[2]


def _mat_skin(name, P, rnd):
    mat = bpy.data.materials.new(name); B = _NB(mat); b = B.bsdf
    skin = tuple(min(1.0, max(0.0, c * rnd.uniform(0.94, 1.06))) for c in P["skin"])
    line_col = (skin[0] * 0.30, skin[1] * 0.16, skin[2] * 0.14, 1)
    # subtle blotchy ruddiness
    tc = B.N.new("ShaderNodeTexCoord")
    nz = B.N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 6.0; nz.inputs["Detail"].default_value = 3
    B.L.new(tc.outputs["Object"], nz.inputs["Vector"])
    ruddy = (skin[0] * 0.92, skin[1] * 0.72, skin[2] * 0.70, 1)
    base = B.mix(B.m("MULTIPLY", B.sub(nz.outputs["Fac"], 0.45), 1.6, clamp=True), (*skin, 1), ruddy)
    # ink lines: baked concavity
    cav = B.attr("cav", "Fac")
    lw = P.get("lines", 1.0)
    line = B.step(B.sub(cav, 0.42 / lw), 0.10)
    # rib lines on the flanks (rest coords normalised to body height 1)
    rx, ry, rz = B.sep(B.attr("rest"))
    ax = B.m("ABSOLUTE", rx)
    if P.get("ribs", 0) > 0:
        wave = B.m("FRACT", B.mul(B.add(rz, B.mul(ax, 0.55)), 38.0))
        thin = B.step(B.sub(0.10, wave), 0.025)
        band = B.mul(B.mul(B.step(B.sub(rz, 0.645), 0.006), B.step(B.sub(0.735, rz), 0.006)),
                     B.mul(B.step(B.sub(ax, 0.045), 0.01), B.step(B.sub(0.098, ax), 0.01)))
        ribs = B.mul(B.mul(thin, band), P["ribs"] * 0.85)
        line = B.m("MAXIMUM", line, ribs)
    groin = B.mul(B.step(B.sub(0.035, ax), 0.01), B.mul(B.step(B.sub(rz, 0.44), 0.01), B.step(B.sub(0.56, rz), 0.01)))
    line = B.mul(line, B.sub(1.0, groin))
    col = B.mix(B.mul(line, 0.85), base, line_col)
    # faint cellular vein mottling (~10% darker)
    vo = B.N.new("ShaderNodeTexVoronoi"); vo.feature = "DISTANCE_TO_EDGE"; vo.inputs["Scale"].default_value = 22.0
    B.L.new(tc.outputs["Object"], vo.inputs["Vector"])
    mot = B.mul(B.step(B.sub(0.035, vo.outputs["Distance"]), 0.02), P.get("mottle", 0.08))
    col = B.mix(mot, col, line_col)
    # eye sockets: dark rim + sunken shading around each eyeball
    ed = B.attr("eyed", "Fac")
    sk = P["eyes"].get("socket", 0.35)
    shade = B.mul(B.step(B.sub(1.9, ed), 0.4), sk * 0.4)
    rim = B.mul(B.step(B.sub(1.35, ed), 0.12), 0.9)
    col = B.mix(shade, col, line_col)
    col = B.mix(rim, col, (0.02, 0.008, 0.006, 1))
    if P.get("brow", 0) > 0:
        bw = B.attr("brow", "Fac")
        brow = B.step(B.sub(0.08 + 0.20 * P["brow"], bw), 0.03)
        col = B.mix(brow, col, (0.06, 0.025, 0.018, 1))
    # ---- painted mouth
    col = _mouth_nodes(B, col, P["mouth"], line_col)
    B.L.new(col, b.inputs["Base Color"])
    # anime-ish: matte, almost no specular, shadows lifted by a little self-emission (soft "cel" shadow)
    b.inputs["Roughness"].default_value = 0.85
    b.inputs["Specular IOR Level"].default_value = 0.12
    B.L.new(col, b.inputs["Emission Color"])
    b.inputs["Emission Strength"].default_value = P.get("lift", 0.15)
    return mat


def _mouth_nodes(B, col, M, line_col):
    fu, fv, ff = B.sep(B.attr("face"))
    kind = M["kind"]
    W = M["width"]
    u = B.mul(fu, 1.0 / W)                 # corners of the grin at |u| = 1 (approx)
    u2 = B.mul(u, u)
    front = B.step(B.sub(ff, 0.5), 0.05)
    dark = (0.035, 0.008, 0.006, 1)
    teeth_col = (0.79, 0.72, 0.53, 1)      # #E6DCC0
    gum_col = (0.40, 0.040, 0.018, 1)      # #B83D25 (sampled, lit) darkened to albedo
    e = 0.012
    if kind in ("grin", "open_grin"):
        # upper edge vu = up - (up+cu... ) shaped so the crescent closes near |u|=1
        up, low, cu, cl = M["up"], M["low"], M["cu"], M["cl"]
        vu = B.add(B.mul(u2, cu + (up * 0.0)), up)          # v units = lips half-width
        vu = B.sub(vu, B.mul(u2, up))                        # pull edges together toward the corners
        vl = B.add(B.mul(u2, cl * 4.0 + low), -low)          # lower edge rises fast -> crescent
        inside = B.mul(B.step(B.sub(vu, fv), e), B.step(B.sub(fv, vl), e))
        inside = B.mul(inside, front)
        outer = B.mul(B.step(B.sub(B.add(vu, 0.07), fv), e), B.step(B.sub(fv, B.sub(vl, 0.07)), e))
        outer = B.mul(outer, front)
        # tooth separation lines
        n = M["teeth"]
        tw = B.m("FRACT", B.add(B.mul(u, n * 0.5), 0.5))
        gap = B.step(B.sub(0.07, B.m("MINIMUM", tw, B.sub(1.0, tw))), 0.02)
        # bite / open interior
        mid = B.mul(B.add(vu, vl), 0.5)
        bite = M["bite"]
        dmid = B.m("ABSOLUTE", B.sub(fv, mid))
        half = B.mul(B.m("MAXIMUM", B.sub(vu, vl), 0.0), bite * 0.5)
        if kind == "open_grin":
            hole = B.step(B.sub(half, dmid), e)
        else:
            hole = B.step(B.sub(0.035, dmid), e)
        tcol = B.mix(gap, teeth_col, (0.32, 0.22, 0.16, 1))
        g = M.get("gums", 0.0)
        if g:
            span = B.m("MAXIMUM", B.sub(vu, vl), 0.0)
            scal = B.mul(B.m("ABSOLUTE", B.m("SINE", B.mul(u, n * math.pi * 0.5))), 0.05)
            gu = B.step(B.sub(fv, B.sub(B.sub(vu, B.mul(span, g)), scal)), e)
            gl = B.step(B.sub(B.add(B.add(vl, B.mul(span, g)), scal), fv), e)
            tcol = B.mix(B.m("MAXIMUM", gu, gl), tcol, gum_col)
        tcol = B.mix(hole, tcol, dark)
        col = B.mix(B.mul(outer, 0.9), col, line_col)        # thin dark lip outline
        col = B.mix(inside, col, tcol)
    elif kind == "gape":
        rx_, ry_ = M["width"], (M["up"] + M["low"]) * 0.5
        cy = (M["up"] - M["low"]) * 0.5
        r = B.add(B.mul(B.mul(fu, fu), 1.0 / (rx_ * rx_)),
                  B.mul(B.mul(B.sub(fv, cy), B.sub(fv, cy)), 1.0 / (ry_ * ry_)))
        hole = B.mul(B.step(B.sub(1.0, r), 0.08), front)
        ring = B.mul(B.step(B.sub(1.35, r), 0.08), front)
        col = B.mix(B.mul(ring, 0.8), col, line_col)
        col = B.mix(hole, col, dark)
    elif kind == "smile_line":
        vc = B.sub(B.mul(u2, M["cu"] * 2.0), 0.02)
        lin = B.mul(B.step(B.sub(0.045, B.m("ABSOLUTE", B.sub(fv, vc))), 0.015),
                    B.step(B.sub(1.0, B.m("ABSOLUTE", u)), 0.03))
        col = B.mix(B.mul(lin, front), col, dark)
    return col


def _mat_eye(name, iris_r, iris_col=(0.03, 0.02, 0.015)):
    mat = bpy.data.materials.new(name); B = _NB(mat); b = B.bsdf
    x, y, z = B.sep(B.attr("eye"))
    r = B.m("SQRT", B.add(B.mul(x, x), B.mul(z, z)))
    front = B.step(B.m("MULTIPLY", y, -1.0), 0.05)
    iris = B.mul(B.step(B.sub(iris_r, r), 0.02), front)
    rim = B.mul(B.step(B.sub(r, 0.93), 0.03), 1.0)
    col = B.mix(iris, (0.86, 0.82, 0.72, 1), (*iris_col, 1))
    pup = B.mul(B.step(B.sub(iris_r * 0.45, r), 0.02), front)
    col = B.mix(pup, col, (0.02, 0.015, 0.012, 1))
    col = B.mix(B.mul(rim, 0.5), col, (0.35, 0.25, 0.2, 1))
    B.L.new(col, b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.25
    return mat


def _mat_flat(name, color, rough=0.7):
    mat = bpy.data.materials.new(name); B = _NB(mat); b = B.bsdf
    nz = B.N.new("ShaderNodeTexWave"); nz.wave_type = "BANDS"; nz.bands_direction = "X"
    nz.inputs["Scale"].default_value = 60.0; nz.inputs["Distortion"].default_value = 3.0
    B.L.new(B.attr("rest"), nz.inputs["Vector"])
    b.inputs["Specular IOR Level"].default_value = 0.2
    B.L.new(B.mix(0.0, (*color, 1), (*color, 1)), b.inputs["Emission Color"])
    b.inputs["Emission Strength"].default_value = 0.15
    dk = tuple(c * 0.6 for c in color)
    B.L.new(B.mix(B.m("MULTIPLY", B.sub(nz.outputs["Fac"], 0.55), 0.55, clamp=True), (*color, 1), (*dk, 1)),
            b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = rough
    return mat


def _mat_outline(name):
    mat = bpy.data.materials.new(name); B = _NB(mat); b = B.bsdf
    b.inputs["Base Color"].default_value = (0.02, 0.008, 0.006, 1)
    b.inputs["Roughness"].default_value = 1.0
    b.inputs["Specular IOR Level"].default_value = 0.0
    g = B.N.new("ShaderNodeNewGeometry")
    lp = B.N.new("ShaderNodeLightPath")
    # visible only to camera rays on front-facing shell faces: the shell must not shadow the body it encloses
    B.L.new(B.mul(B.sub(1.0, g.outputs["Backfacing"]), lp.outputs["Is Camera Ray"]), b.inputs["Alpha"])
    mat.use_backface_culling = True
    try:
        mat.surface_render_method = "DITHERED"
    except Exception:
        pass
    return mat

# --------------------------------------------------------------------------------------------- geometry helpers
def _load_targets(body, items):
    best = {}
    for t, w in items:
        best[t] = max(w, best.get(t, 0.0))
    for t, w in best.items():
        if w <= 0:
            continue
        if t.startswith("@"):
            p = os.path.join(EXPR, t[1:] + ".target.gz")
        else:
            p = os.path.join(TDIR, t + ".target.gz")
        if os.path.exists(p):
            TS.load_target(body, p, weight=w)
        else:
            print("pure_titans: missing target", t)


def _group_verts(me, obj, gname, thr=0.5):
    g = obj.vertex_groups.get(gname)
    if not g:
        return []
    return [v for v in me.vertices if any(x.group == g.index and x.weight > thr for x in v.groups)]


def _centre(vs):
    c = Vector()
    for v in vs:
        c += v.co
    return c / max(1, len(vs))


def _smooth_region(body, centres, iters=30):
    """Laplacian-smooth everything within radius of the given centres (sexless groin / no nipples)."""
    bm = bmesh.new(); bm.from_mesh(body.data); bm.verts.ensure_lookup_table()
    for c, r in centres:
        sel = [v for v in bm.verts if (v.co - c).length < r]
        inner = [v for v in sel if (v.co - c).length < r * 0.75]
        for _ in range(iters):
            bmesh.ops.smooth_vert(bm, verts=inner, factor=0.7, use_axis_x=True, use_axis_y=True, use_axis_z=True)
        for _ in range(6):
            bmesh.ops.smooth_vert(bm, verts=sel, factor=0.4, use_axis_x=True, use_axis_y=True, use_axis_z=True)
    bm.to_mesh(body.data); bm.free()


def _apply_mod(obj, mod):
    with bpy.context.temp_override(object=obj, active_object=obj, selected_objects=[obj]):
        bpy.ops.object.modifier_move_to_index(modifier=mod.name, index=0)
        bpy.ops.object.modifier_apply(modifier=mod.name)


def _set_attr(me, name, vals, kind="FLOAT_VECTOR"):
    if name in me.attributes:
        me.attributes.remove(me.attributes[name])
    a = me.attributes.new(name, kind, "POINT")
    flat = [x for v in vals for x in v] if kind == "FLOAT_VECTOR" else list(vals)
    a.data.foreach_set("vector" if kind == "FLOAT_VECTOR" else "value", flat)


def _bake_attrs(body, H, mouth_c, mouth_w, chin_z, eyes=()):
    me = body.data
    me.update()
    bm = bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table(); bm.normal_update()
    cav = []
    for v in bm.verts:
        if not v.link_edges:
            cav.append(0.0); continue
        acc = Vector(); el = 0.0
        for e in v.link_edges:
            o = e.other_vert(v); acc += o.co; el += e.calc_length()
        acc /= len(v.link_edges); el /= len(v.link_edges)
        cav.append((acc - v.co).dot(v.normal) / max(el, 1e-6))
    # one smoothing pass and normalise so 1.0 ~ a strong crease
    sm = []
    for v in bm.verts:
        s = cav[v.index]; n = 1
        for e in v.link_edges:
            s += cav[e.other_vert(v).index]; n += 1
        sm.append(s / n)
    srt = sorted(sm); ref = srt[int(len(srt) * 0.985)] or 1.0
    cavn = [max(0.0, x / ref) for x in sm]
    rest = [(v.co.x / H, v.co.y / H, v.co.z / H) for v in bm.verts]
    face = []
    for v in bm.verts:
        u = (v.co.x - mouth_c.x) / mouth_w
        w = (v.co.z - mouth_c.z) / mouth_w
        fr = 1.0 if (v.co.y < mouth_c.y + 0.045 and v.co.z > chin_z and v.normal.y < -0.15) else 0.0
        face.append((u, w, fr))
    eyed = [min([((v.co - c).length / r) for c, r in eyes] or [99.0]) for v in bm.verts]
    brw = []
    for v in bm.verts:
        best = 99.0
        for c, r in eyes:
            dx = (v.co.x - c.x) / (1.9 * r)
            if abs(dx) < 1.0 and v.co.y < c.y + 1.2 * r and v.normal.y < -0.2:
                zc = c.z + 1.75 * r + 0.45 * r * (1.0 - dx * dx) - (0.35 * r * dx if c.x > 0 else -0.35 * r * dx)
                best = min(best, abs(v.co.z - zc) / r)
        brw.append(best)
    _set_attr(me, "brow", brw, "FLOAT")
    bm.free()
    _set_attr(me, "eyed", eyed, "FLOAT")
    _set_attr(me, "cav", cavn, "FLOAT")
    _set_attr(me, "rest", rest)
    _set_attr(me, "face", face)


def _add_eyes(body, eyes, mat_index, scale, push):
    """Append two UV spheres (eye balls) to the body mesh, 100% weighted to the head bone."""
    me = body.data
    bm = bmesh.new(); bm.from_mesh(me)
    dl = bm.verts.layers.deform.verify()
    hg = body.vertex_groups.get("head") or body.vertex_groups.new(name="head")
    new = []
    for c, r in eyes:
        rr = r * scale
        res = bmesh.ops.create_uvsphere(bm, u_segments=20, v_segments=12, radius=rr,
                                        matrix=Matrix.Translation(c + Vector((0, -push - (rr - r) * 0.6, 0))))
        vs = res["verts"]
        for v in vs:
            v[dl].clear(); v[dl][hg.index] = 1.0
        for f in {f for v in vs for f in v.link_faces}:
            f.material_index = mat_index; f.smooth = True
        new.append((vs, c + Vector((0, -push - (rr - r) * 0.6, 0)), rr))
    bm.to_mesh(me); bm.free()
    # eye-local attribute (unit sphere coords), only meaningful on eye verts
    n = len(me.vertices)
    vals = [(0.0, 0.0, 0.0)] * n
    k = n - sum(len(vs) for vs, _, _ in new)
    for vs, c, rr in new:
        for i in range(len(vs)):
            co = me.vertices[k + i].co
            vals[k + i] = tuple((co - c) / rr)
        k += len(vs)
    _set_attr(me, "eye", vals)


def _grin_depth(fu, fv, M):
    """Signed depth (in lip half-widths) inside the painted mouth shape; >0 inside. Mirrors _mouth_nodes."""
    if M["kind"] in ("grin", "open_grin"):
        u = fu / M["width"]; u2 = u * u
        vu = M["up"] + u2 * (M["cu"] - M["up"]); vl = -M["low"] + u2 * (M["cl"] * 4.0 + M["low"])
        return min(vu - fv, fv - vl)
    if M["kind"] == "gape":
        ry = (M["up"] + M["low"]) * 0.5; cy = (M["up"] - M["low"]) * 0.5
        r = (fu / M["width"]) ** 2 + ((fv - cy) / ry) ** 2
        return (1.0 - r) * ry * 0.5
    return -9.0


def _recess_mouth(body, mc, mw, M):
    """Model the grin a little: teeth set back behind the lip line, cheeks/lips bulging around it."""
    k = M.get("recess", 0.0)
    if not k:
        return
    me = body.data
    for v in me.vertices:
        if v.co.y > mc.y + 0.03 or v.normal.y > -0.1 or abs(v.co.z - mc.z) > mw * 3:
            continue
        d = _grin_depth((v.co.x - mc.x) / mw, (v.co.z - mc.z) / mw, M)
        if d > 0:
            t = min(1.0, d / 0.45); t = t * t * (3 - 2 * t)
            v.co.y += k * mw * t
        elif d > -0.5:
            t = 1.0 - abs(d + 0.25) / 0.25
            if t > 0:
                v.co.y -= 0.18 * k * mw * t * t


def _messy(hair, eyes, amt, seed):
    """Short messy hair: noisy push along the head radius so the silhouette gets tufts."""
    from mathutils import noise
    ez = sum(c.z for c, _ in eyes) / len(eyes); er = eyes[0][1]
    vs = hair.data.vertices
    cy = sum(v.co.y for v in vs) / len(vs)
    c = Vector((0.0, cy, ez + er * 1.5))
    off = Vector((seed * 1.7, seed * 0.3, 0.0))
    for v in vs:
        d = v.co - c
        n = noise.noise((v.co + off) * (9.0 / er))
        n2 = noise.noise((v.co + off) * (2.5 / er))
        v.co = v.co + d.normalized() * er * amt * (0.35 * max(0.0, n) + 0.25 * n2)


def _custom_bob(body, eyes, mc, mw, H, opt, name):
    """Smooth chin-length bob with straight-ish bangs, shrink-wrapped to this head (one shell, head-weighted)."""
    from mathutils.bvhtree import BVHTree
    me = body.data
    bvh = BVHTree.FromPolygons([v.co for v in me.vertices], [tuple(p.vertices) for p in me.polygons])
    ez = sum(c.z for c, _ in eyes) / len(eyes); er = eyes[0][1]; ey = min(c.y for c, _ in eyes)
    ex = max(abs(c.x) for c, _ in eyes)
    hv = [v.co for v in me.vertices if v.co.z > ez]
    top = max(p.z for p in hv)
    cy = (min(p.y for p in hv) + max(p.y for p in hv)) * 0.5
    c = Vector((0.0, cy, ez + 0.2 * (top - ez)))
    th = er * 1.3                                   # hair volume above the scalp
    z_brow = ez + er * opt.get("bangs_h", 2.4)
    z_chin = mc.z - mw * 1.3 * opt.get("length", 1.0)
    fx = ex + er * 1.5
    th_f = math.atan2(fx, max(1e-4, c.y - (ey - er)))   # half-angle of the bangs window
    NT, NR = 72, 28
    grid = []
    for i in range(NT):
        t = 2 * math.pi * i / NT
        tt = (t + math.pi) % (2 * math.pi) - math.pi          # -pi..pi, 0 = front (-Y)
        st, ct = math.sin(t), math.cos(t)
        pts = []; prev = None
        for k in range(41):
            ph = (k / 40) * math.pi / 2
            d = Vector((math.sin(ph) * st, -math.sin(ph) * ct, math.cos(ph)))
            hit = bvh.ray_cast(c, d)
            r = (hit[0] - c).length if hit[0] is not None else (prev or er * 6)
            prev = r
            pts.append(c + d * (r + th))
        rh = Vector((pts[-1].x - c.x, pts[-1].y - c.y)).length
        zl = z_chin - mw * 0.8
        for j in range(1, 31):
            z = c.z - j * (c.z - zl) / 30
            o = Vector((c.x, c.y, z)); d = Vector((st, -ct, 0.0))
            hit = bvh.ray_cast(o, d)
            rh *= 0.988                                       # taper in under the ears, hug the jaw
            if hit[0] is not None:
                rh = max(rh, (hit[0] - o).length + th * 0.6)
            rr = rh + th * 0.6 * (j / 30) ** 0.7             # fuller towards the ends
            pts.append(Vector((c.x + rr * st, c.y - rr * ct, z)))
        # where this column ends: bangs in front, chin length on the sides, a touch longer at the back
        w = 1.0 - min(1.0, max(0.0, (abs(tt) - th_f) / 0.22))
        w = w * w * (3 - 2 * w)
        zb_side = z_chin - mw * 0.35 * (abs(tt) / math.pi)
        zb = z_brow * w + zb_side * (1 - w)
        zb += er * 0.25 * abs(math.sin(tt * 9.0)) * (0.6 + 0.4 * w)  # soft clumps along the cut
        L = [0.0]
        for a, b2 in zip(pts, pts[1:]):
            L.append(L[-1] + (b2 - a).length)
        end = L[-1]
        for k in range(1, len(pts)):
            if pts[k].z <= zb and k > 5:
                a, b2 = pts[k - 1], pts[k]
                f = (a.z - zb) / max(1e-6, a.z - b2.z)
                end = L[k - 1] + f * (L[k] - L[k - 1]); break
        col = []
        for r_ in range(NR):
            sl = end * r_ / (NR - 1)
            for k in range(1, len(L)):
                if L[k] >= sl:
                    f = (sl - L[k - 1]) / max(1e-6, L[k] - L[k - 1])
                    col.append(pts[k - 1].lerp(pts[k], f)); break
            else:
                col.append(pts[-1].copy())
        grid.append(col)
    for _ in range(3):   # smooth around the head (ears, nose rays)
        grid = [[(grid[i - 1][r_] + grid[i][r_] * 2 + grid[(i + 1) % NT][r_]) / 4 for r_ in range(NR)]
                for i in range(NT)]
    # rounded, slightly turned-under tips (soft bob instead of a straight wig cut)
    for i in range(NT):
        col = grid[i]
        for back, f in ((1, 0.55), (2, 0.25), (3, 0.08)):
            p = col[NR - back]
            rad = Vector((p.x - c.x, p.y - c.y, 0.0))
            if rad.length > 1e-6:
                col[NR - back] = p - rad.normalized() * th * f + Vector((0, 0, er * 0.35 * f))
    hm = bpy.data.meshes.new(name + "_bob")
    verts = [p for col in grid for p in col]
    faces = []
    for i in range(NT):
        i2 = (i + 1) % NT
        for r_ in range(NR - 1):
            faces.append((i * NR + r_, i2 * NR + r_, i2 * NR + r_ + 1, i * NR + r_ + 1))
    hm.from_pydata(verts, [], faces)
    bm = bmesh.new(); bm.from_mesh(hm)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    # make sure normals point away from the head centre
    f0 = max(bm.faces, key=lambda f: f.calc_center_median().z)
    if f0.normal.z < 0:
        bmesh.ops.reverse_faces(bm, faces=bm.faces)
    bm.to_mesh(hm); bm.free()
    ob = bpy.data.objects.new(name + "_bob", hm); bpy.context.scene.collection.objects.link(ob)
    vg = ob.vertex_groups.new(name="head"); vg.add(list(range(len(hm.vertices))), 1.0, "REPLACE")
    return ob


# --------------------------------------------------------------------------------------------- builder
def make_pure(kind="generic", seed=0, height=None, preset=None, lod=0.45, outline=True, name=None):
    """Build one pure Titan; returns the armature.

    kind: "smiling" (Dina) or "generic". For generic, `preset` picks a GENERIC entry by name,
    else seed % len(GENERIC). seed also jitters skin tone, body macros and gait.
    height: metres (default from preset; generic gets +-12% jitter). lod: decimate ratio for the body (1 = full).
    """
    rnd = random.Random(seed * 7919 + 13)
    if kind == "smiling":
        key = "smiling"
    else:
        key = preset or GENERIC_KEYS[seed % len(GENERIC_KEYS)]
    P = PRESETS[key]
    jit = 0.0 if kind == "smiling" else 1.0
    height = height or P["height"] * (1.0 + jit * rnd.uniform(-0.12, 0.12))
    name = name or f"Pure_{key}_{seed}"

    md = TS.get_default_macro_info_dict()
    for k in ("gender", "age", "muscle", "weight", "proportions", "cupsize"):
        if k in P:
            md[k] = min(1.0, max(0.0, P[k] + jit * rnd.uniform(-0.08, 0.08)))
    md["height"] = 0.5
    body = HS.create_human(feet_on_ground=True, scale=0.1, macro_detail_dict=md)
    _load_targets(body, [t for t in P["targets"] if not t[0].startswith("breast/BreastSize")])
    rig = HS.add_builtin_rig(body, "default")
    hair = None
    if P.get("hair") and P["hair"][0] != "custom_bob":
        hn, hcol, hopt = P["hair"]
        try:
            f = ASSET.find_asset_absolute_path(f"{hn}/{hn}.mhclo", asset_subdir="hair")
            hair = HS.add_mhclo_asset(f, body, asset_type="Hair", subdiv_levels=0)
        except Exception as ex:
            print("pure_titans: hair failed", ex); hair = None
    TS.bake_targets(body)
    me = body.data
    # landmarks before the helper geometry is deleted
    eyes = []
    for g in ("helper-l-eye", "helper-r-eye"):
        vs = _group_verts(me, body, g)
        if vs:
            c = _centre(vs); r = max((v.co - c).length for v in vs)
            eyes.append((c.copy(), r))
    lips = _group_verts(me, body, "lips")
    mouth_c = _centre(lips).copy()
    mouth_w = (max(v.co.x for v in lips) - min(v.co.x for v in lips)) / 2
    genit = _group_verts(me, body, "genitals"); nip = _group_verts(me, body, "nipple")
    gen_c = _centre(genit).copy() if genit else None
    _T._bake_and_clean(body)
    me = body.data
    zs = [v.co.z for v in me.vertices]; H = max(zs) - min(zs)
    # sexless: smooth groin and chest points
    reg = []
    if gen_c is not None:
        reg.append((gen_c + Vector((0, 0.0, 0.0)), 0.075))
    if nip:
        cs = {}
        for v in nip:
            cs.setdefault(v.co.x > 0, []).append(v.co.copy())
        for pts in cs.values():
            c = Vector()
            for p in pts:
                c += p
            reg.append((c / len(pts), 0.035))
    if reg:
        _smooth_region(body, reg)
    _recess_mouth(body, mouth_c, mouth_w, P["mouth"])
    if P.get("hair") and P["hair"][0] == "custom_bob" and eyes:
        hair = _custom_bob(body, eyes, mouth_c, mouth_w, H, P["hair"][2], name)
    # LOD
    if lod and lod < 1.0:
        dm = body.modifiers.new("lod", "DECIMATE"); dm.ratio = lod; dm.use_symmetry = True; dm.symmetry_axis = "X"
        _apply_mod(body, dm)
    chin_z = mouth_c.z - mouth_w * 1.6
    _bake_attrs(body, H, mouth_c, mouth_w, chin_z, eyes)
    # materials: 0 skin, 1 eye, 2 hair, 3 outline
    me.materials.clear()
    me.materials.append(_mat_skin(name + "_skin", P, rnd))
    me.materials.append(_mat_eye(name + "_eye", P["eyes"].get("iris", 0.25), P["eyes"].get("iris_col", (0.03, 0.02, 0.015))))
    hcol = P["hair"][1] if P.get("hair") else (0.2, 0.1, 0.05)
    me.materials.append(_mat_flat(name + "_hair", hcol))
    if outline:
        me.materials.append(_mat_outline(name + "_ink"))
    for p in me.polygons:
        p.material_index = 0; p.use_smooth = True
    E = P["eyes"]
    if eyes:
        _add_eyes(body, eyes, 1, 0.97 if E.get("closed") else E.get("scale", 1.0) * 0.97 + 0.03,
                  E.get("push", 0.0) if not E.get("closed") else -0.002)
    if hair:
        if P["hair"][2].get("messy") and eyes:
            _messy(hair, eyes, P["hair"][2]["messy"], seed)
        _set_attr(hair.data, "rest", [(v.co.x / H, v.co.y / H, v.co.z / H) for v in hair.data.vertices])
        if lod and lod < 1.0 and len(hair.data.polygons) > 3000:
            hm = hair.modifiers.new("lod", "DECIMATE"); hm.ratio = max(lod, 0.5)
            _apply_mod(hair, hm)
        hs = P["hair"][2].get("scale", (1, 1, 1))
        if hs != (1, 1, 1):
            # scale about the head centre (bob is longer / fuller on Dina)
            hc = Vector((0, sum(v.co.y for v in hair.data.vertices) / len(hair.data.vertices),
                         max(v.co.z for v in hair.data.vertices)))
            for v in hair.data.vertices:
                d = v.co - hc
                v.co = hc + Vector((d.x * hs[0], d.y * hs[1], d.z * hs[2]))
        if P["hair"][0] == "custom_bob":
            pass
        elif eyes and P["hair"][2].get("part"):
            # centre-parted curtain: cut a triangular opening out of the fringe so the face shows,
            # strands keep hanging over the cheeks at the sides
            ez = sum(c.z for c, _ in eyes) / len(eyes); er = eyes[0][1]; ey = min(c.y for c, _ in eyes)
            ex = max(abs(c.x) for c, _ in eyes); tx = ex + er * 1.6
            hb = bmesh.new(); hb.from_mesh(hair.data)
            kill = []
            for f in hb.faces:
                c = f.calc_center_median()
                ax = abs(c.x) / tx
                if c.y < ey + er * 2.2 and ax < 1.0 and c.z < ez + er * (PART_TOP * (1.0 - ax) + 1.2 * ax):
                    kill.append(f)
            bmesh.ops.delete(hb, geom=kill, context="FACES")
            hb.to_mesh(hair.data); hb.free()
        elif eyes and P["hair"][2].get("bangs", True):
            # titans' faces must read: cut the fringe straight above the brows (bowl-cut / Dina bangs)
            ez = sum(c.z for c, _ in eyes) / len(eyes); er = eyes[0][1]; ey = min(c.y for c, _ in eyes)
            ex = max(abs(c.x) for c, _ in eyes)
            brow = ez + er * P["hair"][2].get("bang_h", 1.9)
            for v in hair.data.vertices:
                if v.co.y < ey + er * 2.5 and abs(v.co.x) < ex + er * 2.2 and v.co.z < brow:
                    v.co.z = brow
                    v.co.y = min(v.co.y, ey - er * 0.2)
        hair.data.materials.clear()
        for m in me.materials:
            hair.data.materials.append(m)
        for p in hair.data.polygons:
            p.material_index = 2; p.use_smooth = True
        for m in list(hair.modifiers):
            if m.type != "ARMATURE":
                hair.modifiers.remove(m)
        with bpy.context.temp_override(active_object=body, object=body, selected_objects=[body, hair],
                                       selected_editable_objects=[body, hair]):
            bpy.ops.object.join()
    for m in list(body.modifiers):
        if m.type not in ("ARMATURE",):
            body.modifiers.remove(m)
    if outline:
        so = body.modifiers.new("ink", "SOLIDIFY")
        so.thickness = 0.0065 * H / 1.66 * (1.0 if height > 6 else 1.3)
        so.offset = 1.0; so.use_flip_normals = True; so.use_rim = False
        so.material_offset = 3; so.material_offset_rim = 3; so.use_quality_normals = False
    rig.name = name; body.name = name + "_body"; rig.data.name = name + "_rig"
    # proportions
    pb = rig.pose.bones
    hs = P.get("head", 1.0) * (1.0 + jit * rnd.uniform(-0.05, 0.05))
    pb["head"].scale = (hs, hs, hs)
    head_h = max(v.co.z for v in me.vertices) - rig.data.bones["head"].head_local.z
    total = H + head_h * (hs - 1.0)
    s = height / total
    rig.scale = (s, s, s)
    rig["pure_preset"] = key
    rig["height_m"] = height
    g = dict(P["gait"]);
    for k2 in g:
        g[k2] *= 1.0 + jit * rnd.uniform(-0.12, 0.12)
    rig["gait"] = g
    rig["slouch"] = P.get("slouch", 0.2) * (1.0 + jit * rnd.uniform(-0.2, 0.2))
    rig["arms_out"] = P.get("arms", 1.0)
    rig["gait_seed"] = seed
    idle_pose(rig)
    bpy.context.view_layer.update()
    print(f"pure_titans: {name} {key} h={height:.1f}m tris~{sum(len(p.vertices) - 2 for p in me.polygons)}")
    return rig

# --------------------------------------------------------------------------------------------- posing / walk
def _R(x=0.0, y=0.0, z=0.0):
    return Matrix.Rotation(z, 3, "Z") @ Matrix.Rotation(y, 3, "Y") @ Matrix.Rotation(x, 3, "X")


def _Ra(x=0.0, y=0.0, z=0.0):
    """Arm order: lower about Y first, then swing about X."""
    return Matrix.Rotation(x, 3, "X") @ Matrix.Rotation(y, 3, "Y") @ Matrix.Rotation(z, 3, "Z")


def _basis(pb, R):
    M = pb.bone.matrix_local.to_3x3()
    return (M.inverted() @ R @ M).to_quaternion()


def _gait(rig, p, amp=1.0):
    """Pose at phase p (0..1) -> {bone: Matrix3 rotation in its rest frame}, root offset (armature space)."""
    G = rig.get("gait") or {}
    G = {k: float(G[k]) for k in G.keys()} if G else dict(stride=0.35, knee=0.5, sway=0.02, bob=0.05, arm=0.25, limp=0.06)
    sl = float(rig.get("slouch", 0.2)); ao = float(rig.get("arms_out", 1.0))
    sd = int(rig.get("gait_seed", 0)); r = random.Random(sd * 31 + 5)
    harm = [(r.uniform(-1, 1), r.uniform(0, 6.28)) for _ in range(6)]
    T = 2 * math.pi
    ph = T * p
    A = G["stride"] * amp; K = G["knee"] * amp; limp = G["limp"] * amp
    out = {}
    for side, sg, off in (("L", 1, 0.0), ("R", -1, math.pi)):
        q = ph + off
        a = A * (1.0 - limp if side == "R" else 1.0)
        th = -a * math.sin(q) - 0.06 * amp                          # forward = negative pitch
        kn = 0.06 + 0.08 * amp + K * max(0.0, math.cos(q)) ** 1.5 + 0.08 * amp * max(0.0, -math.sin(q))
        ft = -(th + kn) * 0.85 + 0.12 * amp * max(0.0, math.cos(q - 0.6))
        out[f"upperleg01.{side}"] = _R(x=th, z=sg * 0.03)
        out[f"lowerleg01.{side}"] = _R(x=kn)
        out[f"foot.{side}"] = _R(x=ft)
        # arms: lowered from A-pose, hang forward a bit (slouch), swing opposite to the leg with lag
        f = -G["arm"] * amp * math.sin(q - 0.45)                      # forward-ness
        lower = 0.74 - 0.30 * (1.0 - ao)
        out[f"upperarm01.{side}"] = _Ra(x=-f - sl * 0.35, y=sg * lower, z=sg * 0.05)
        el = -0.12 + 0.18 * amp * (0.5 + 0.5 * math.sin(q - 1.2))
        out[f"lowerarm01.{side}"] = _R(x=-el)
        out[f"wrist.{side}"] = _R(x=-0.15 * amp * math.sin(q - 1.8))
        out[f"shoulder01.{side}"] = _R(x=0.0, z=0.0, y=sg * 0.05)
    H = lambda k, w: harm[k][0] * math.sin(w * ph + harm[k][1])
    yaw = 0.07 * amp * math.sin(ph)
    roll = 0.05 * amp * math.cos(ph) + 0.02 * amp * H(0, 1)
    out["root"] = _R(y=-roll, z=-yaw)
    out["spine05"] = _R(x=sl * 0.15)
    out["spine04"] = _R(x=sl * 0.25, y=roll * 0.6)
    out["spine03"] = _R(x=sl * 0.25, z=yaw * 0.6)
    out["spine02"] = _R(x=sl * 0.2, y=0.03 * amp * H(1, 1), z=yaw * 0.6)
    out["spine01"] = _R(x=sl * 0.15 + 0.03 * amp * math.sin(2 * ph - 0.5), z=yaw * 0.3)
    out["neck01"] = _R(x=sl * 0.5)
    hb = G["bob"] * amp
    out["neck02"] = _R(x=-sl * 0.3 + hb * 0.4 * math.sin(2 * ph - 1.4))
    out["head"] = _R(x=-sl * 0.65 + hb * math.sin(2 * ph - 1.8) + 0.04 * amp * H(2, 1),
                     y=0.06 * amp * math.sin(ph - 0.9) + 0.04 * amp * H(3, 1), z=0.05 * amp * H(4, 1) + 0.03 * amp * H(5, 2))
    sway = G["sway"] * amp
    off = Vector((-sway * math.cos(ph), 0.0, 0.0))
    return out, off


def _apply(rig, rots, off):
    P = rig.pose.bones
    res = {}
    for bn, R in rots.items():
        pb = P.get(bn)
        if pb is None:
            continue
        pb.rotation_mode = "QUATERNION"
        pb.rotation_quaternion = _basis(pb, R)
        res[bn] = pb.rotation_quaternion.copy()
    rb = P["root"]
    rb.location = rb.bone.matrix_local.to_3x3().inverted() @ off
    return res


_FEET = [("foot.L", "head"), ("foot.L", "tail"), ("toe1-2.L", "tail"), ("toe5-3.L", "tail"),
         ("foot.R", "head"), ("foot.R", "tail"), ("toe1-2.R", "tail"), ("toe5-3.R", "tail")]


def _feet(rig):
    P = rig.pose.bones
    return [getattr(P[b], e).copy() for b, e in _FEET if b in P]


def _rest_feet(rig):
    B = rig.data.bones
    return [(B[b].head_local if e == "head" else B[b].tail_local).copy() for b, e in _FEET if b in B]


def _ground(rig, rots, off):
    """Shift the root down so the lowest foot point sits on its rest height. Returns (off, stanceL?, feet)."""
    _apply(rig, rots, off)
    bpy.context.view_layer.update()
    fp = _feet(rig); fr = _rest_feet(rig)
    d = [p.z - r.z for p, r in zip(fp, fr)]
    n = len(d) // 2
    dl, dr = min(d[:n]), min(d[n:])
    off = off + Vector((0, 0, -min(dl, dr)))
    return off, dl <= dr, fp


def idle_pose(rig):
    """Static slouched stance (arms hanging), no keys."""
    rots, off = _gait(rig, 0.0, amp=0.0)
    off, _, _ = _ground(rig, rots, off)
    _apply(rig, rots, off)


def walk_action(rig, cycle_frames=48, offset=0, travel=True, step=2):
    """Key a looping walk on the rig's pose bones as a new Action (assigned to rig).

    cycle_frames: frames per full cycle (two steps). offset: phase offset in frames (desync a crowd).
    travel: root bone advances along the rig's -Y forever (REPEAT_OFFSET cycles) with planted feet;
            False = in place (move the object yourself by rig["walk_stride_m"] per cycle).
    """
    N = max(4, int(round(cycle_frames / step)))
    samples = []
    for i in range(N + 1):
        p = (i / N + offset / cycle_frames) % 1.0 if i < N else (offset / cycle_frames) % 1.0
        rots, off = _gait(rig, p)
        off, stanceL, fp = _ground(rig, rots, off)
        n = len(fp) // 2
        fy = (fp[1].y if stanceL else fp[n + 1].y)        # foot.tail of the stance foot
        samples.append((rots, off, stanceL, fy, fp))
    # forward progress: body moves so the stance foot stays put
    ys = [0.0]
    for i in range(1, N + 1):
        r0, o0, st0, fy0, fp0 = samples[i - 1]
        _, _, _, _, fp1 = samples[i]
        n = len(fp1) // 2
        j = 1 if st0 else n + 1
        ys.append(ys[-1] - (fp1[j].y - fp0[j].y))
    stride = -ys[-1]          # armature units, positive forward
    s = rig.scale[0]
    rig["walk_stride_m"] = stride * s
    rig["walk_cycle_frames"] = cycle_frames
    # build the action
    act = bpy.data.actions.new(f"{rig.name}_walk")
    slot = act.slots.new("OBJECT", rig.name)
    layer = act.layers.new("walk")
    strip = layer.strips.new(type="KEYFRAME")
    cb = strip.channelbags.new(slot)
    keys = {}
    prevq = {}
    for i, (rots, off, _, _, _) in enumerate(samples):
        if travel:
            off = off + Vector((0, ys[i], 0))
        qs = _apply(rig, rots, off)
        fr = i * cycle_frames / N
        for bn, q in qs.items():
            if bn in prevq and prevq[bn].dot(q) < 0:
                q = -q
            prevq[bn] = q
            for c in range(4):
                keys.setdefault((f'pose.bones["{bn}"].rotation_quaternion', c, bn), []).append((fr, q[c]))
        loc = rig.pose.bones["root"].location
        for c in range(3):
            keys.setdefault(('pose.bones["root"].location', c, "root"), []).append((fr, loc[c]))
    for (path, idx, grp), kv in keys.items():
        fc = cb.fcurves.new(path, index=idx)
        try:
            fc.group = cb.groups.get(grp) or cb.groups.new(grp)
        except Exception:
            pass
        fc.keyframe_points.add(len(kv))
        fc.keyframe_points.foreach_set("co", [x for k in kv for x in k])
        for kp in fc.keyframe_points:
            kp.interpolation = "BEZIER"; kp.handle_left_type = kp.handle_right_type = "AUTO_CLAMPED"
        mod = fc.modifiers.new("CYCLES")
        if travel and "location" in path:
            mod.mode_before = mod.mode_after = "REPEAT_OFFSET"
        fc.update()
    rig.animation_data_create()
    rig.animation_data.action = act
    rig.animation_data.action_slot = slot
    if offset:
        pass  # phase already baked into the samples, keys still start at frame 0
    return act
