"""Carla sequence (EP1 beats S12-S14 and S18), right after the Colossal's kick (seq_colossal ends at frame 2100).

  S12  Carla trapped under the collapsed Yeager house (states845 YEAGER_HOUSE, AOT_STATE=kicked); child Eren and
       Mikasa heave at the beam on her back; Hannes (Garrison, blond, tan jacket, ODM gear) runs in with blades out;
       the Smiling Titan comes into view behind.
  S13  Hannes charges, freezes before the Smiling Titan, sheathes, scoops up the kids and runs.
  S14  The Smiling Titan lifts Carla out of the rubble and bites (stylised: red silhouette + red mist, no gore) while
       Hannes runs off with Eren (facing back, right arm stretched back over Hannes's shoulder: "Yamero", held
       ~2 s) and Mikasa. Sky camera ~40-60 m, both groups in one frame, slow pull-away, sunset light.
  S18  The oath ("I'll kill every last one", ~3 s hold): refugee boats on the canal north of Wall Maria heading
       north while the inner gate is burst (AOT_STATE=armored); the kids stand at a boat's bow; the camera cranes up.

List this module FIRST and LAST (like seq_colossal) so it sets the other plug-ins' flags before they import and
finishes the scene after they have built:
  CARLA_F=2300 AOT_PLUGINS=seq_carla,flight,cast845,states845,seq_carla bash render.sh carla out.png 640x360 16
  bash carla_preview.sh "2200 2300 2560"           (preview strip, see carla_preview.sh)
Frames continue seq_colossal's numbering (30 fps). Poses are pure functions of the frame (one process renders one
frame), so any frame can be rendered on its own.  Per-frame use in ONE session (render_fall.py): CARLA_PERFRAME=1 makes
build() call setup_carla() only; then pose_carla(f) (f may be fractional) before every render. No close-ups: every camera is a sky view at 25-60 m.
"""
import math, os, random
from mathutils import Vector, Matrix, Quaternion, noise

F = int(os.environ.get("CARLA_F", "2200"))

# ---------------------------------------------------------------- timeline (30 fps, continues seq_colossal)
T_FLY = (2100, 2190)       # from the breach view (seq_colossal end) down to the Yeager street
S12 = (2190, 2340)         # trapped, kids heave, Hannes runs in, titan walks into view
S13 = (2340, 2460)         # Hannes charges, freezes, scoops the kids up, runs
S14 = (2460, 2650)         # lift, hold up in profile, bite; "Yamero" arm hold ~2520-2600; pull-away
S18 = (2650, 2890)         # boats + burst inner gate; oath hold 2650-2750, then crane up
END = S18[1]

# Hannes
H_ARRIVE = 2325            # reaches the kids
H_CHARGE = (2340, 2362)    # a few steps toward the titan, blades out
H_FREEZE = (2362, 2398)
H_SCOOP = (2402, 2428)     # back at the kids, crouch, lift them
H_RUN = 2428               # runs off along the street (+u)
# Smiling Titan
T_WALK = (2150, 2392)      # walks in along the street (-u side) to its grab spot
T_REACH = (2398, 2445)
T_LIFT = (2452, 2515)
T_BITE = (2566, 2592)      # head forward: red silhouette, then mist
CARLA_GONE = 2588


def _ss(a, b, f):
    t = min(1.0, max(0.0, (f - a) / float(b - a)))
    return t * t * (3 - 2 * t)


def beat(f=F):
    if f < S12[0]:
        return "fly"
    if f < S13[0]:
        return "S12"
    if f < S14[0]:
        return "S13"
    if f < S18[0]:
        return "S14"
    return "S18"


def flags(f=F):
    """Environment flags for the other plug-ins at sequence frame f."""
    e = {"AOT_STATE": "armored" if f >= S18[0] else "kicked", "AOT_ARC_T": "1",
         "AOT_EVENT": "armored",          # cast845: the pure titans streaming in (+ the Smiling Titan we take over)
         "COL_SHOW": "0", "FL_NOKIDS": "1", "FL_NOGRASS": "1"}
    return e


if "CARLA_ENV_DONE" not in os.environ:
    for k, v in flags().items():
        if k not in os.environ:
            os.environ[k] = v
    os.environ["CARLA_ENV_DONE"] = "1"

STATE = {}


# ---------------------------------------------------------------- small helpers
def _srgb(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]
    return tuple(v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c)


def _R(x=0.0, y=0.0, z=0.0):
    return Matrix.Rotation(z, 3, "Z") @ Matrix.Rotation(y, 3, "Y") @ Matrix.Rotation(x, 3, "X")


def _Ra(x=0.0, y=0.0, z=0.0):
    """Arm order: Z, then lower about Y, then swing about X (armature axes: +X = character's left, -Y = front)."""
    return Matrix.Rotation(x, 3, "X") @ Matrix.Rotation(y, 3, "Y") @ Matrix.Rotation(z, 3, "Z")


def _blend(a, b, t):
    """Blend two (rots, off) poses."""
    ra, oa = a; rb, ob = b
    out = {}
    for k in set(ra) | set(rb):
        qa = (ra.get(k) or Matrix.Identity(3)).to_quaternion()
        qb = (rb.get(k) or Matrix.Identity(3)).to_quaternion()
        out[k] = qa.slerp(qb, t).to_matrix()
    return out, oa.lerp(ob, t)


def _reset(rig):
    for pb in rig.pose.bones:
        pb.rotation_mode = "QUATERNION"; pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0)


def _pose(rig, rots, off=None, ground=False):
    import pure_titans as PT
    _reset(rig)
    off = Vector(off) if off is not None else Vector((0, 0, 0))
    if ground:
        off, _, _ = PT._ground(rig, rots, off)
    PT._apply(rig, rots, off)
    return off


def solve_arm(rig, rots, off, target, side="R", start=(-1.6, -0.55, 0.25, -0.8), iters=5):
    """Coordinate-descent IK on the titan arm (upperarm x/y/z swing + elbow) so the hand (wrist tail) meets target."""
    import bpy, pure_titans as PT
    sg = 1 if side == "L" else -1
    prm = list(start)
    def ev(q):
        rots[f"upperarm01.{side}"] = _Ra(x=q[0], y=q[1], z=q[2])
        rots[f"lowerarm01.{side}"] = _R(x=q[3])
        PT._apply(rig, {f"upperarm01.{side}": rots[f"upperarm01.{side}"], f"lowerarm01.{side}": rots[f"lowerarm01.{side}"]}, off)
        bpy.context.view_layer.update()
        return (_bone_w(rig, f"wrist.{side}", "tail") - target).length
    best = ev(prm)
    lim = [(-3.0, 0.6), (-1.4, 1.4), (-1.2, 1.2), (-2.4, 0.0)]
    step = 0.4
    for _ in range(iters):
        for i in range(4):
            for dlt in (step, -step):
                q = list(prm); q[i] = min(lim[i][1], max(lim[i][0], q[i] + dlt))
                e = ev(q)
                if e < best:
                    best, prm = e, q
        step *= 0.55
    ev(prm)
    return best


def _bone_w(rig, bone, at="head"):
    import bpy
    pb = rig.pose.bones[bone]
    return rig.matrix_world @ (pb.head if at == "head" else pb.tail)


def _yaw_to(d):
    return math.atan2(d.x, -d.y)          # MPFB front = local -Y


def _place(rig, x, y, yaw, z=None):
    import aotlib as L
    rig.rotation_mode = "XYZ"
    rig.location = (x, y, L.height(x, y) if z is None else z)
    rig.rotation_euler = (0.0, 0.0, yaw)


def _ground_z(x, y):
    """Top of the rubble/ground under (x, y): ray cast down on the ruins (so feet stand on the debris)."""
    import bpy, aotlib as L
    g = L.height(x, y)
    dg = bpy.context.evaluated_depsgraph_get()
    hit, loc, *_ = bpy.context.scene.ray_cast(dg, Vector((x, y, g + 6.0)), Vector((0, 0, -1)), distance=7.0)
    return loc.z if hit and loc.z < g + 1.2 else g


# ---------------------------------------------------------------- human poses (MPFB default rig, armature space)
LOWER = 1.05           # arms from the MPFB rest A-pose down to the sides


def p_stand(arms=0.0):
    r = {}
    for s, sg in (("L", 1), ("R", -1)):
        r[f"upperarm01.{s}"] = _Ra(x=-0.1 - arms, y=sg * LOWER)
        r[f"lowerarm01.{s}"] = _R(x=-0.2)
    return r, Vector((0, 0, 0))


def p_run(p, lean=0.28, arms=True, amp=1.0):
    """Running gait at phase p (0..1)."""
    ph = 2 * math.pi * p
    r = {}
    for s, sg, o in (("L", 1, 0.0), ("R", -1, math.pi)):
        q = ph + o
        th = -0.72 * amp * math.sin(q) - 0.2 * amp
        kn = 0.25 + 1.35 * amp * max(0.0, math.cos(q - 0.5)) ** 1.3
        r[f"upperleg01.{s}"] = _R(x=th)
        r[f"lowerleg01.{s}"] = _R(x=kn)
        r[f"foot.{s}"] = _R(x=-0.25 * amp * math.sin(q))
        if arms:
            r[f"upperarm01.{s}"] = _Ra(x=0.75 * amp * math.sin(q) - 0.1, y=sg * (LOWER - 0.12))
            r[f"lowerarm01.{s}"] = _R(x=-1.35)
    r["spine05"] = _R(x=lean * 0.5); r["spine03"] = _R(x=lean * 0.3, z=0.1 * amp * math.sin(ph))
    r["neck01"] = _R(x=-lean * 0.5)
    return r, Vector((0, 0, 0))


def p_crouch(reach=0.6):
    r = {}
    for s, sg in (("L", 1), ("R", -1)):
        r[f"upperleg01.{s}"] = _R(x=-1.35, y=-sg * 0.12)
        r[f"lowerleg01.{s}"] = _R(x=1.9)
        r[f"foot.{s}"] = _R(x=-0.55)
        r[f"upperarm01.{s}"] = _Ra(x=-reach, y=sg * LOWER)
        r[f"lowerarm01.{s}"] = _R(x=-0.2)
    r["spine05"] = _R(x=0.55); r["spine03"] = _R(x=0.25); r["neck01"] = _R(x=-0.35)
    return r, Vector((0, 0, 0))


def p_heave(p):
    """Kids pulling up at the beam: bent over, arms down to it, rocking up on each heave."""
    k = 0.5 + 0.5 * math.sin(2 * math.pi * p)          # 1 = pulling up
    r = {}
    for s, sg in (("L", 1), ("R", -1)):
        r[f"upperleg01.{s}"] = _R(x=-1.0 + 0.45 * k, y=-sg * 0.15)
        r[f"lowerleg01.{s}"] = _R(x=1.25 - 0.55 * k)
        r[f"foot.{s}"] = _R(x=-0.3 + 0.1 * k)
        r[f"upperarm01.{s}"] = _Ra(x=-0.55 - 0.25 * k, y=sg * (LOWER - 0.15))
        r[f"lowerarm01.{s}"] = _R(x=-0.15 - 0.3 * k)
    r["spine05"] = _R(x=0.75 - 0.4 * k); r["spine03"] = _R(x=0.3 - 0.15 * k); r["neck01"] = _R(x=-0.4)
    return r, Vector((0, 0, 0))


def p_carry():
    """Hannes's arms wrapped round the two kids on his chest."""
    r = {}
    for s, sg in (("L", 1), ("R", -1)):
        r[f"upperarm01.{s}"] = _Ra(x=-0.75, y=sg * (LOWER - 0.15), z=-sg * 0.35)
        r[f"lowerarm01.{s}"] = _R(x=-1.55, z=-sg * 0.4)
    return r


def p_eren_carried(reach=1.0):
    """Eren on Hannes's chest facing back, legs round him, right arm stretched back over Hannes's shoulder."""
    r = {}
    for s, sg in (("L", 1), ("R", -1)):
        r[f"upperleg01.{s}"] = _R(x=-1.25, y=-sg * 0.45)
        r[f"lowerleg01.{s}"] = _R(x=1.3)
    # facing Hannes, so Eren's LEFT arm is on the outside (over Hannes's right shoulder)
    r["upperarm01.L"] = _Ra(x=-0.9 - 1.05 * reach, y=LOWER - 0.15 * reach, z=0.15 * reach)
    r["lowerarm01.L"] = _R(x=-1.0 * (1 - reach) - 0.05)
    r["upperarm01.R"] = _Ra(x=-1.0, y=-(LOWER - 0.25), z=0.3)
    r["lowerarm01.R"] = _R(x=-1.2)
    r["spine05"] = _R(x=0.05); r["spine03"] = _R(x=0.0); r["neck01"] = _R(x=-0.25, z=0.3)
    return r, Vector((0, 0, 0))


def p_mikasa_carried():
    r = {}
    for s, sg in (("L", 1), ("R", -1)):
        r[f"upperleg01.{s}"] = _R(x=-1.2, y=-sg * 0.35)
        r[f"lowerleg01.{s}"] = _R(x=1.4)
        r[f"upperarm01.{s}"] = _Ra(x=-1.1, y=sg * (LOWER - 0.4))
        r[f"lowerarm01.{s}"] = _R(x=-0.9)
    r["spine05"] = _R(x=0.25); r["neck01"] = _R(x=0.3, z=0.3)
    return r, Vector((0, 0, 0))


def p_prone(p=0.0):
    """Carla on her front under the beam, chest raised on her forearms, head up (body axis is set by the object)."""
    w = 0.08 * math.sin(2 * math.pi * p)
    r = {"spine05": _R(x=-0.12), "spine03": _R(x=-0.22 - w), "spine01": _R(x=-0.12), "neck01": _R(x=-0.45)}
    for s, sg in (("L", 1), ("R", -1)):
        r[f"upperarm01.{s}"] = _Ra(x=-1.45, y=sg * (LOWER - 0.35))
        r[f"lowerarm01.{s}"] = _R(x=-1.1, z=-sg * 0.3)
        r[f"upperleg01.{s}"] = _R(x=0.05)
    return r, Vector((0, 0, 0))


def p_held(p=0.0):
    """Carla held round the waist in the titan's fist: legs hanging and kicking, arms pushing at the fingers."""
    w = math.sin(2 * math.pi * p)
    r = {"spine05": _R(x=-0.1), "neck01": _R(x=-0.3)}
    for s, sg in (("L", 1), ("R", -1)):
        r[f"upperleg01.{s}"] = _R(x=-0.25 + sg * 0.3 * w)
        r[f"lowerleg01.{s}"] = _R(x=0.5 + 0.2 * w)
        r[f"upperarm01.{s}"] = _Ra(x=-1.9 + sg * 0.25 * w, y=sg * (LOWER - 0.6))
        r[f"lowerarm01.{s}"] = _R(x=-0.6)
    return r, Vector((0, 0, 0))


# ---------------------------------------------------------------- titan poses (pure_titans rig)
def t_walk(rig, p):
    import pure_titans as PT
    rots, off = PT._gait(rig, p)
    return rots, off


def t_idle(rig):
    import pure_titans as PT
    return PT._gait(rig, 0.0, amp=0.0)


def t_reach(rig):
    rots, off = t_idle(rig)
    rots = dict(rots)
    for s, sg in (("L", 1), ("R", -1)):
        rots[f"upperleg01.{s}"] = _R(x=-1.05, z=sg * 0.08)
        rots[f"lowerleg01.{s}"] = _R(x=1.45)
        rots[f"foot.{s}"] = _R(x=-0.45)
    for b, a in (("spine05", 0.3), ("spine04", 0.3), ("spine03", 0.28), ("spine02", 0.22), ("spine01", 0.15)):
        rots[b] = _R(x=a)
    rots["neck01"] = _R(x=-0.2); rots["neck02"] = _R(x=-0.2); rots["head"] = _R(x=-0.25)
    rots["upperarm01.R"] = _Ra(x=-0.55, y=-0.62)
    rots["lowerarm01.R"] = _R(x=-0.1)
    rots["upperarm01.L"] = _Ra(x=-0.3, y=0.7)
    return rots, off


def t_lift(rig, k=1.0):
    """k 0..1: hand from the waist up to in front of the face (Carla held up in profile)."""
    rots, off = t_idle(rig)
    rots = dict(rots)
    for b, a in (("spine05", 0.06), ("spine04", 0.04), ("spine03", 0.02)):
        rots[b] = _R(x=a)
    rots["neck01"] = _R(x=0.1); rots["neck02"] = _R(x=-0.1); rots["head"] = _R(x=-0.32)
    rots["upperarm01.R"] = _Ra(x=-1.35 - 0.55 * k, y=-0.55, z=0.25)
    rots["lowerarm01.R"] = _R(x=-0.55 - 0.35 * k)
    rots["wrist.R"] = _R(x=0.3)
    rots["upperarm01.L"] = _Ra(x=-0.2, y=0.72)
    return rots, off


def t_bite(rig):
    rots, off = t_lift(rig, 1.0)
    rots = dict(rots)
    rots["upperarm01.R"] = _Ra(x=-1.55, y=-0.45, z=0.45)
    rots["lowerarm01.R"] = _R(x=-1.35)
    rots["neck01"] = _R(x=0.3); rots["head"] = _R(x=0.15)
    rots["spine03"] = _R(x=0.12)
    return rots, off


# ---------------------------------------------------------------- characters
def _adult(name, gender, hair, hair_col, outfit, height, macro=None):
    import characters as C
    rig, body = C._child(name, 30, gender, hair, hair_col, outfit, macro=macro, height=height)
    return rig


def make_carla(name="Carla"):
    """Carla: faceless adult woman, long brown hair tied low, simple dusty-rose dress, long skirt, white apron."""
    import characters as C
    rig = _adult(name, 0.0, "ponytail01", (0.075, 0.035, 0.018),
                 lambda: {"shirt": C._cloth(name + "_dress", _srgb("9C6E5C")),
                          "legs": C._cloth(name + "_dress_l", _srgb("6E4A3C"), scale=30),
                          "boots": C._flat(name + "_shoes", (0.06, 0.04, 0.03), rough=0.5)},
                 1.66, macro=dict(weight=0.45, proportions=0.6))
    C.skirt(name, rig, color=_srgb("6E4A3C"), length=0.1)
    apron(name, rig)
    return rig


def apron(name, rig):
    """White apron: front panel of a skirt from the waist to below the knee."""
    import bpy, bmesh, characters as C
    hip = rig.data.bones["upperleg01.L"].head_local.z
    hw = abs(rig.data.bones["upperleg01.L"].head_local.x)
    bm = bmesh.new(); rows = []
    for z, r in ((hip + 0.08, hw + 0.09), (hip - 0.02, hw + 0.11), (hip * 0.7, hw + 0.13), (hip * 0.38, hw + 0.15)):
        ring = []
        for k in range(13):
            a = -math.pi / 2 - 1.05 + k / 12 * 2.1
            ring.append(bm.verts.new((math.cos(a) * r, math.sin(a) * r * 0.85 - 0.01, z)))
        rows.append(ring)
    for j in range(len(rows) - 1):
        for k in range(12):
            bm.faces.new((rows[j][k], rows[j][k + 1], rows[j + 1][k + 1], rows[j + 1][k]))
    me = bpy.data.meshes.new(name + "_apron"); bm.to_mesh(me); bm.free()
    me.materials.append(C._cloth(name + "_apron", (0.80, 0.78, 0.72), fold=0.3, scale=20))
    ob = bpy.data.objects.new(name + "_apron", me); bpy.context.scene.collection.objects.link(ob)
    ob.modifiers.new("thick", "SOLIDIFY").thickness = 0.006
    C._bind(ob, rig, "spine05")
    return ob


def make_hannes(name="Hannes"):
    """Hannes: tall, blond, tan Garrison jacket with the twin-rose patch on the back, white trousers, dark boots, ODM gear."""
    import bpy, bmesh, characters as C, aotlib as L
    rig = _adult(name, 1.0, "short02", (0.50, 0.36, 0.14),
                 lambda: {"shirt": C._cloth(name + "_jacket", _srgb("9B6947")),
                          "legs": C._cloth(name + "_trousers", (0.74, 0.72, 0.66), scale=30),
                          "boots": C._flat(name + "_boots", (0.05, 0.03, 0.02), rough=0.45)},
                 1.85, macro=dict(muscle=0.65, weight=0.5, proportions=0.7))
    B = rig.data.bones
    hip = B["upperleg01.L"].head_local; hw = abs(hip.x)
    steel = L.mat(name + "_steel", _srgb("9A9A94"), 0.35)
    dark = L.mat(name + "_harness", (0.05, 0.035, 0.025), 0.6)
    rose = L.mat(name + "_rose", _srgb("7A1F22"), 0.6)
    bm = bmesh.new()
    for sg in (1, -1):                                   # blade boxes + gas cylinder on each hip
        L.box(bm, (sg * (hw + 0.13), hip.y + 0.02, hip.z - 0.08), (0.10, 0.62, 0.16), mi=0)
        L.cyl(bm, (sg * (hw + 0.13), hip.y - 0.28, hip.z + 0.03), (sg * (hw + 0.13), hip.y + 0.30, hip.z + 0.03), 0.04, seg=8, mi=0)
    L.box(bm, (0, hip.y + 0.17, hip.z + 0.05), (0.26, 0.10, 0.18), mi=0)          # winch housing on the lower back
    L.box(bm, (0, hip.y, hip.z + 0.12), (2 * hw + 0.12, 0.30, 0.07), mi=1)          # belt
    sp = B["spine01"].head_local
    L.box(bm, (0, sp.y + 0.12, sp.z - 0.05), (0.16, 0.02, 0.18), mi=2)              # rose emblem on the back
    me_ob = L.obj_from_bm(name + "_odm", bm, [steel, dark, rose])
    C._bind(me_ob, rig, "spine05")
    return rig


def make_kids(prefix="Carla"):
    import characters as C
    e = C.make_eren(prefix + "Eren")
    m = C.make_mikasa(prefix + "Mikasa")
    return e, m


def _all_obs(rig):
    return [rig] + list(rig.children_recursive)


def _flat_red(rig):
    """Bite: Carla turns into a flat dark-red silhouette (stylised, no gore)."""
    import bpy
    m = bpy.data.materials.get("CarlaSilhouette")
    if m is None:
        m = bpy.data.materials.new("CarlaSilhouette"); m.use_nodes = True
        N = m.node_tree.nodes; N.remove(N["Principled BSDF"])
        em = N.new("ShaderNodeEmission"); em.inputs["Color"].default_value = (0.32, 0.01, 0.01, 1)
        em.inputs["Strength"].default_value = 1.0
        m.node_tree.links.new(em.outputs[0], N["Material Output"].inputs["Surface"])
    for o in _all_obs(rig):
        if o.type == "MESH":
            for i in range(len(o.data.materials)):
                o.data.materials[i] = m


def _rim_warm(rig):
    """Held against the sunset: a dusty-rose dress silhouette with a warm orange Fresnel rim (emission), so the figure
    reads against the golden sky. pose_carla restores her own materials every frame before this."""
    import bpy
    m = bpy.data.materials.get("CarlaRimWarm")
    if m is None:
        m = bpy.data.materials.new("CarlaRimWarm"); m.use_nodes = True
        N = m.node_tree.nodes; Lk = m.node_tree.links
        b = N["Principled BSDF"]; b.inputs["Base Color"].default_value = (*_srgb("7A4E42"), 1); b.inputs["Roughness"].default_value = 0.8
        lw = N.new("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = 0.35
        em = N.new("ShaderNodeEmission"); em.inputs["Color"].default_value = (1.0, 0.55, 0.22, 1); em.inputs["Strength"].default_value = 6.0
        mx = N.new("ShaderNodeMixShader")
        Lk.new(lw.outputs["Fresnel"], mx.inputs[0]); Lk.new(b.outputs[0], mx.inputs[1]); Lk.new(em.outputs[0], mx.inputs[2])
        Lk.new(mx.outputs[0], N["Material Output"].inputs["Surface"])
    for o in _all_obs(rig):
        if o.type == "MESH":
            for i in range(len(o.data.materials)):
                o.data.materials[i] = m


def red_mist(center, k, coll, seed=3):
    """Stylised blood mist: a few soft red volume puffs, k 0..1 grows and fades."""
    import bpy, bmesh, aotlib as L
    m = bpy.data.materials.new("RedMist"); m.use_nodes = True
    nt = m.node_tree; N = nt.nodes; N.remove(N["Principled BSDF"])
    pv = N.new("ShaderNodeVolumePrincipled")
    pv.inputs["Color"].default_value = (0.55, 0.02, 0.02, 1)
    pv.inputs["Density"].default_value = 2.2 * (1.0 - 0.75 * k)
    pv.inputs["Emission Strength"].default_value = 0.25
    pv.inputs["Emission Color"].default_value = (0.6, 0.04, 0.03, 1)
    nt.links.new(pv.outputs[0], N["Material Output"].inputs["Volume"])
    rnd = random.Random(seed); bm = bmesh.new()
    for i in range(9):
        c = Vector(center) + Vector((rnd.gauss(0, 0.6), rnd.gauss(0, 0.6), rnd.gauss(-0.3, 0.5))) * (0.6 + 2.2 * k)
        r = (0.35 + 0.35 * rnd.random()) * (0.6 + 1.6 * k)
        s = bmesh.ops.create_icosphere(bm, subdivisions=2, radius=r)
        bmesh.ops.translate(bm, vec=c, verts=s["verts"])
    ob = L.obj_from_bm("RedMist", bm, [m], coll)
    ob.visible_shadow = False
    return ob


# ---------------------------------------------------------------- set geometry
def house_frame(year):
    """Carla's spot in the Yeager ruin and the house axes: (C, f = toward the street, u = along the front)."""
    import states845 as ST
    e = ST.TownEdit(year)
    yk = [(k, i) for k, i, px, py in e.near(ST.YEAGER_HOUSE[0], ST.YEAGER_HOUSE[1], 14, only_alive=False) if k == 0]
    ya = e.pos(*yk[0])[2] if yk else 0.0
    ca, sa = math.cos(ya), math.sin(ya)
    hx, hy = ST.YEAGER_HOUSE
    f = Vector((sa, -ca)); u = Vector((ca, sa))
    off = [float(v) for v in os.environ.get("CARLA_SPOT", "1.2,-7.6").split(",")]
    C = Vector((hx, hy)) + u * off[0] + f * -off[1]
    # the titan faces +u with its grabbing (right) hand toward -f, so it stands in the street in front of the
    # house (not on the thrown block): flip u so that works out
    return C, f, -u, ya


def beams(C, f, u, coll, M):
    """The fallen beams and a wall slab pinning Carla's legs, plus a little debris round her."""
    import bpy, bmesh, aotlib as L
    wood = M.get("gate") or L.mat("BeamWood", (0.17, 0.11, 0.07), 0.8)
    plaster = M.get("plaster") or L.mat("Plaster", (0.8, 0.74, 0.62), 0.9)
    bm = bmesh.new()
    rot_u = math.atan2(u.y, u.x)
    g = L.height(C.x, C.y)
    p = C - f * 0.35
    L.box(bm, (p.x, p.y, g + 0.42), (5.2, 0.34, 0.34), rot=rot_u + 0.12, mi=0)        # the beam on her back
    q = C - f * 1.5 + u * 0.6
    L.box(bm, (q.x, q.y, g + 0.7), (4.2, 0.32, 0.32), rot=rot_u - 0.5, mi=0)
    s = C - f * 2.6 - u * 0.4
    L.box(bm, (s.x, s.y, g + 0.9), (4.0, 2.8, 0.35), rot=rot_u + 0.2, mi=1)           # broken wall panel over her legs
    rnd = random.Random(5)
    for _ in range(14):
        d = C - f * rnd.uniform(1.0, 3.5) + u * rnd.uniform(-2.5, 2.5)
        L.box(bm, (d.x, d.y, g + 0.2), (rnd.uniform(0.3, 0.9),) * 2 + (rnd.uniform(0.2, 0.5),), rot=rnd.uniform(0, 3), mi=1)
    ob = L.obj_from_bm("CarlaBeams", bm, [wood, plaster], coll)
    return ob


def clear_ruins(pts, names=("Ruins845",)):
    """Remove neighbouring ruin piles (states845) that would hide the figures: pts = [(xy, radius)]."""
    import bpy, bmesh
    n = 0
    for nm in names:
        ob = bpy.data.objects.get(nm)
        if not ob or ob.type != "MESH":
            continue
        bm = bmesh.new(); bm.from_mesh(ob.data)
        mw = ob.matrix_world
        kill = []
        for isl in _islands(bm):
            c = sum((mw @ v.co for v in isl), Vector()) / len(isl)
            if any((c.to_2d() - p).length < r for p, r in pts):
                kill += isl
        bmesh.ops.delete(bm, geom=kill, context="VERTS")
        n += len(kill)
        bm.to_mesh(ob.data); bm.free(); ob.data.update()
    return n


def _islands(bm):
    bm.verts.ensure_lookup_table()
    seen = set(); out = []
    for v in bm.verts:
        if v.index in seen:
            continue
        stack = [v]; isl = []; seen.add(v.index)
        while stack:
            w = stack.pop(); isl.append(w)
            for e in w.link_edges:
                o = e.other_vert(w)
                if o.index not in seen:
                    seen.add(o.index); stack.append(o)
        out.append(isl)
    return out


def clear_houses(year, paths):
    """Hide scatter houses standing on the runners' / titan's paths (polyline, radius)."""
    import bpy
    town = bpy.data.objects.get("Town")
    if not town:
        return 0
    me = town.data; dead = me.attributes["dead"].data; born = me.attributes["born"].data
    n = 0
    for i, v in enumerate(me.vertices):
        p = v.co.to_2d()
        if not (born[i].value <= year < dead[i].value):
            continue
        for pts, rad in paths:
            hit = False
            for a, b in zip(pts, pts[1:]):
                ab = b - a; t = max(0.0, min(1.0, (p - a).dot(ab) / max(ab.length_squared, 1e-6)))
                if (p - (a + ab * t)).length < rad:
                    hit = True; break
            if hit:
                dead[i].value = year - 1; n += 1; break
    me.update()
    return n


# ---------------------------------------------------------------- paths (2D, filled in build)
def hannes_xy(f):
    C, fv, u = STATE["C"], STATE["f"], STATE["u"]
    A = C + fv * 6.0 + u * 52.0
    B = C + fv * 1.6 + u * 2.2              # beside the kids
    B2 = C + fv * 3.0 - u * 2.6             # charge stop
    if f <= H_ARRIVE:
        t0 = H_ARRIVE - 52.0 / 6.2 * 30
        k = max(0.0, (f - t0) / (H_ARRIVE - t0))
        k = 1 - (1 - k) ** 1.6 if k < 1 else 1.0
        return A.lerp(B, k), (B - A), "run" if f < H_ARRIVE - 4 else "stand"
    if f < H_CHARGE[0]:
        return B, (STATE["T1"] - B), "stand"
    if f < H_CHARGE[1]:
        k = _ss(*H_CHARGE, f)
        return B.lerp(B2, k), (B2 - B), "charge"
    if f < H_FREEZE[1]:
        return B2, (STATE["T1"] - B2), "freeze"
    if f < H_SCOOP[0]:
        k = _ss(H_FREEZE[1], H_SCOOP[0], f)
        return B2.lerp(B, k), (B - B2) if k < 0.6 else (C - B), "turn"
    if f < H_RUN:
        return B, (C - B), "scoop"
    t = (f - H_RUN) / 30.0
    v = float(os.environ.get("CARLA_HV", "3.4"))
    d = min(t, 0.6) ** 2 / 1.2 * v + max(0.0, t - 0.6) * v              # accelerate to v m/s (heavy with two kids)
    P = B + u * d + fv * min(3.5, d * 0.25)
    return P, u, "flee"


def titan_xy(f):
    T0, T1 = STATE["T0"], STATE["T1"]
    k = min(1.0, max(0.0, (f - T_WALK[0]) / (T_WALK[1] - T_WALK[0])))
    k = k if k < 0.85 else 0.85 + (1 - (1 - (k - 0.85) / 0.15) ** 2) * 0.15
    return T0.lerp(T1, k), (T1 - T0)


# ---------------------------------------------------------------- build
_BUILDS = [0]


def build(M, year, ctx):
    _BUILDS[0] += 1
    if _BUILDS[0] < 2:
        return
    import bpy, aotlib as L
    coll = L.new_coll("SeqCarla")
    b = beat(F)
    # the walk cycles of the inflow crowd keep going from seq_colossal (T_INFLOW = 1800)
    bpy.context.scene.frame_set(max(1, F - 1800 + 1))
    if os.environ.get("CARLA_PERFRAME") == "1":     # render_fall.py: build once, it calls pose_carla(f) per frame
        setup_carla(M, year, ctx, coll)               # (and blends the light itself)
        pose_carla(F)
        print(f"[seq_carla] per-frame setup done (F {F})")
        return
    if b == "S18":
        build_s18(M, year, ctx, coll)
    else:
        build_carla(M, year, ctx, coll)
    sunset(ctx, b)
    os.environ.setdefault("EXPO", "-1.1")
    print(f"[seq_carla] frame {F} beat {b} flags {flags()}")


def _armored_rigs():
    import bpy
    out = []
    for o in bpy.data.objects:
        if "armored" in o.name.lower() and o.type in ("ARMATURE", "MESH", "EMPTY") and o.parent is None:
            out.append(o)
    return out


def _take_smiling():
    """Reuse cast845's Smiling Titan (inflow crowd) or build one."""
    import bpy
    rig = next((o for o in bpy.data.objects if o.type == "ARMATURE" and "smiling" in o.name.lower()), None)
    if rig is None:
        import pure_titans as PT
        rig = PT.make_pure("smiling", seed=1, height=float(os.environ.get("CARLA_TITAN_H", "14.0")), lod=0.45, name="CarlaSmiling")
    if rig.animation_data:
        rig.animation_data.action = None
    return rig


def build_carla(M, year, ctx, coll):
    """One-process path (CARLA_F): build the set once, then pose it for frame F."""
    setup_carla(M, year, ctx, coll)
    pose_carla(F)


def setup_carla(M, year, ctx, coll):
    """Build once: beams, the Smiling Titan's grab geometry, cleared paths, Carla / kids / Hannes rigs.
    Then call pose_carla(f) for every frame (one Blender session can render the whole beat, see render_fall.py)."""
    import bpy, aotlib as L
    for o in _armored_rigs():                       # the Armored belongs to the gate chapter
        for x in _all_obs(o):
            x.hide_render = True
    C, fv, u, ya = house_frame(year)
    STATE.update(C=C, f=fv, u=u)
    g = L.height(C.x, C.y)
    beams(C, fv, u, coll, M)
    # ---- the Smiling Titan: work out where it must stand so its reaching hand meets Carla
    ti = _take_smiling()
    STATE["titan"] = ti
    grab = C - fv * 0.15
    yaw_t = _yaw_to(u)                              # faces along +u (the street), Carla in front of it
    _place(ti, 0, 0, yaw_t, z=g)
    _pose(ti, *t_reach(ti), ground=True)
    bpy.context.view_layer.update()
    hand = _bone_w(ti, "wrist.R", "tail")
    off = hand.to_2d() - Vector((0.0, 0.0))
    T1 = grab - off
    T0 = T1 - u * 44.0 + fv * 4.0
    STATE.update(T0=T0, T1=T1)
    n = clear_houses(year, [([T0, T1, T1 + u * 4], 9.0), ([hannes_xy(2200)[0], hannes_xy(2330)[0]], 4.5),
                            ([hannes_xy(H_RUN)[0], hannes_xy(END)[0]], 4.5)])
    nr = clear_ruins([(C + fv * 3.0, 10.0), (C + fv * 2.0 + u * 14.0, 5.0), (C + fv * 2.0 + u * 26.0, 5.0), (T1, 6.0)])
    print(f"[seq_carla] removed {nr} ruin verts round Carla")
    print(f"[seq_carla] house yaw {math.degrees(ya):.0f} C {tuple(round(v, 1) for v in C)} cleared {n}")
    STATE.update(g=g, grab=grab, yaw_t=yaw_t, coll=coll, tmp=[])
    ca = make_carla("Carla")
    er, mk = make_kids()
    ha = make_hannes("Hannes")
    STATE["carla_s"] = ca.scale.x
    STATE.update(carla=ca, eren=er, mikasa=mk, hannes=ha,
                 carla_mats={o.name: list(o.data.materials) for o in _all_obs(ca) if o.type == "MESH"})
    for o in _all_obs(ca) + _all_obs(er) + _all_obs(mk) + _all_obs(ha):
        for c in list(o.users_collection):
            c.objects.unlink(o)
        coll.objects.link(o)


def _clear_tmp():
    """Remove the per-frame helper objects (blades, red mist) of the previous pose."""
    import bpy
    for o in STATE.get("tmp", []):
        if o is None or o.name not in bpy.data.objects:
            continue
        me = o.data; mats = [m for m in me.materials] if me else []
        bpy.data.objects.remove(o, do_unlink=True)
        if me and me.users == 0:
            bpy.data.meshes.remove(me)
        for m in mats:
            if m and m.users == 0:
                bpy.data.materials.remove(m)
    STATE["tmp"] = []


def pose_carla(F):
    """Pose the beat for seq_carla frame F (titan, Carla, Hannes, kids, blades, red mist, dust thinning).
    Pure function of F once setup_carla() has run; call it after fx845.update() so the dust thinning sticks."""
    import bpy, aotlib as L
    _clear_tmp()
    C, fv, u, g, grab, yaw_t, ti, coll = (STATE[k] for k in ("C", "f", "u", "g", "grab", "yaw_t", "titan", "coll"))
    T1 = STATE["T1"]
    # titan pose for this frame
    if F < T_WALK[1]:
        pxy, d = titan_xy(F)
        p = ((F - T_WALK[0]) / 54.0) % 1.0
        pose = t_walk(ti, p)
        blend_in = _ss(T_WALK[1] - 16, T_WALK[1], F)
        if blend_in > 0:
            pose = _blend(pose, t_idle(ti), blend_in)
    elif F < T_REACH[1]:
        pxy = T1; pose = _blend(t_idle(ti), t_reach(ti), _ss(*T_REACH, F))
    elif F < T_LIFT[0]:
        pxy = T1; pose = t_reach(ti)
    elif F < T_BITE[0]:
        pxy = T1; k = _ss(*T_LIFT, F)
        pose = _blend(t_reach(ti), t_lift(ti, 1.0), k)
    else:
        pxy = T1; pose = _blend(t_lift(ti, 1.0), t_bite(ti), _ss(*T_BITE, F))
        if F > T_BITE[1] + 20:
            pose = _blend(pose, t_lift(ti, 0.3), _ss(T_BITE[1] + 20, T_BITE[1] + 60, F))
    _place(ti, pxy.x, pxy.y, yaw_t, z=L.height(pxy.x, pxy.y) - 0.1)
    toff = _pose(ti, *pose, ground=True)
    bpy.context.view_layer.update()
    STATE["titan_head"] = _bone_w(ti, "head", "head")
    if F >= T_LIFT[0]:
        tf = Vector((math.sin(yaw_t), -math.cos(yaw_t), 0)); tr = Vector((-math.cos(yaw_t), -math.sin(yaw_t), 0))
        hb, ht = _bone_w(ti, "head", "head"), _bone_w(ti, "head", "tail")
        hs = (ht - hb).length
        G = Vector((grab.x, grab.y, g + 0.5))
        if os.environ.get("CARLA_HOLD", "high") == "high":
            # canon (S1E2 sunset): held HIGH in the fist, arm raised to the side above the head, against the sky;
            # she only goes to the mouth at the bite (T_BITE)
            hold = hb + tr * hs * 2.3 + tf * hs * 0.9 + Vector((0, 0, hs * 1.3))
        else:
            hold = hb + tf * hs * 1.25 + tr * hs * 0.15 - Vector((0, 0, hs * 0.55))
        bite = hb.lerp(ht, 0.2) + tf * hs * 0.45 - Vector((0, 0, hs * 0.75))
        if F < T_BITE[0]:
            tgt = G.lerp(hold, _ss(*T_LIFT, F))
        elif F < T_BITE[1] + 20:
            tgt = hold.lerp(bite, _ss(*T_BITE, F))
        else:
            tgt = bite.lerp(hold - Vector((0, 0, hs * 0.8)), _ss(T_BITE[1] + 20, T_BITE[1] + 60, F))
        err = solve_arm(ti, pose[0], toff, tgt, "R", iters=7)
        print(f"[seq_carla] titan arm IK error {err:.2f} m")
    # ---- Carla
    ca = STATE["carla"]
    for o in _all_obs(ca):
        o.hide_render = False
        if o.type == "MESH" and o.name in STATE["carla_mats"]:
            for i, m in enumerate(STATE["carla_mats"][o.name]):
                o.data.materials[i] = m
    if F < T_LIFT[0] + 6:
        _pose(ca, *p_prone((F - S12[0]) / 40.0))
        # lying on her front, head toward the street (+f), face down: body Z -> f, body +Y -> up, hips at C
        Zb = Vector((fv.x, fv.y, 0.0)).normalized(); Yb = Vector((0, 0, 1.0)); Xb = Yb.cross(Zb)
        R = Matrix((Xb, Yb, Zb)).transposed()
        hip_l = ca.data.bones["upperleg01.L"].head_local.copy(); hip_l.x = 0.0
        s = STATE.get("carla_s", ca.scale.x)
        want = Vector((C.x, C.y, g + 0.16 + float(os.environ.get("CARLA_DZ", "0"))))
        ca.matrix_world = Matrix.Translation(want - R @ (hip_l * s)) @ R.to_4x4() @ Matrix.Scale(s, 4)
    else:
        _pose(ca, *p_held((F - T_LIFT[0]) / 22.0))
        bpy.context.view_layer.update()
        hand = _bone_w(ti, "wrist.R", "tail")
        tf = Vector((math.sin(yaw_t), -math.cos(yaw_t), 0))          # titan front (world)
        yaw_c = yaw_t + math.pi * 0.5                                   # held side-on: Carla in profile too
        # readability while she is held up against the sky: grow ~1.8x through the lift, warm rim-lit silhouette
        s = STATE.get("carla_s", ca.scale.x) * (1.0 + (float(os.environ.get("CARLA_HELD_SCALE", "1.8")) - 1.0) * _ss(T_LIFT[0], T_LIFT[0] + 20, F))
        if F < T_BITE[0] + 8:
            _rim_warm(ca)
        ca.matrix_world = Matrix.Translation(Vector((0, 0, 0))) @ Matrix.Rotation(yaw_c, 4, "Z") @ Matrix.Scale(s, 4)
        bpy.context.view_layer.update()
        waist = _bone_w(ca, "spine04", "head")
        ca.matrix_world = Matrix.Translation(hand + tf * 0.35 - waist) @ ca.matrix_world
        if F >= T_BITE[0] + 8:
            _flat_red(ca)
        if F >= CARLA_GONE:
            for o in _all_obs(ca):
                o.hide_render = True
    # red mist at the mouth during and after the bite
    if T_BITE[0] + 6 <= F < T_BITE[1] + 70:
        bpy.context.view_layer.update()
        hd, ht = _bone_w(ti, "head", "head"), _bone_w(ti, "head", "tail")
        tf = Vector((math.sin(yaw_t), -math.cos(yaw_t), 0))
        mouth = hd.lerp(ht, 0.2) + tf * (ht - hd).length * 0.55
        STATE["tmp"].append(red_mist(mouth, _ss(T_BITE[0] + 6, T_BITE[1] + 70, F), coll))
    # ---- kids + Hannes
    er, mk, ha = STATE["eren"], STATE["mikasa"], STATE["hannes"]
    hp, hd_, mode = hannes_xy(F)
    yaw_h = _yaw_to(hd_) if hd_.length > 1e-3 else 0.0
    _place(ha, hp.x, hp.y, yaw_h, z=_ground_z(hp.x, hp.y))
    if mode == "run":
        _pose(ha, *p_run((F % 20) / 20.0), ground=True)
    elif mode == "charge":
        r, o = p_run((F % 18) / 18.0, lean=0.4, arms=False)
        for s_, sg in (("L", 1), ("R", -1)):
            r[f"upperarm01.{s_}"] = _Ra(x=-0.9, y=sg * (LOWER - 0.35)); r[f"lowerarm01.{s_}"] = _R(x=-0.4)
        _pose(ha, r, o, ground=True)
    elif mode == "freeze":
        r, o = p_stand(arms=0.8)
        tremble = 0.03 * math.sin(F * 2.3)
        r["spine05"] = _R(x=-0.12 + tremble); r["neck01"] = _R(x=-0.3)
        for s_, sg in (("L", 1), ("R", -1)):
            r[f"upperleg01.{s_}"] = _R(x=-0.15 if s_ == "L" else 0.15)
        _pose(ha, r, o, ground=True)
    elif mode in ("stand", "turn"):
        _pose(ha, *(p_stand(0.2) if mode == "stand" else p_run((F % 20) / 20.0, amp=0.6)), ground=True)
    elif mode == "scoop":
        k = _ss(*H_SCOOP, F)
        crouch = math.sin(k * math.pi)
        r, o = _blend(p_stand(0.4), p_crouch(0.9), crouch)
        if k > 0.55:
            r.update(p_carry())
        _pose(ha, r, o, ground=True)
    else:                                   # flee with both kids
        r, o = p_run(((F - H_RUN) % 18) / 18.0, lean=0.22, arms=False)
        r.update(p_carry())
        _pose(ha, r, o, ground=True)
    bpy.context.view_layer.update()
    blades = mode in ("run", "charge", "freeze", "stand") and F < H_FREEZE[1] - 6
    if blades:
        STATE["tmp"].append(hannes_blades(ha, coll))
    carried = mode == "flee" or (mode == "scoop" and _ss(*H_SCOOP, F) > 0.55)
    if carried:
        reach = 1.0 if F >= H_RUN + 10 else _ss(H_RUN - 4, H_RUN + 10, F)
        _pose(er, *p_eren_carried(reach))
        _pose(mk, *p_mikasa_carried())
        attach_carried(ha, er, mk)
    else:
        # at the beam, heaving (Eren at its +u end, Mikasa between him and Carla's head)
        ph = (F - S12[0]) / 34.0
        for kid, pos, face, phase in ((er, C + u * 2.15 - fv * 0.25, -u, ph), (mk, C + u * 1.05 + fv * 0.55, -fv * 0.6 - u * 0.8, ph + 0.18)):
            _place(kid, pos.x, pos.y, _yaw_to(face), z=_ground_z(pos.x, pos.y))
            _pose(kid, *p_heave(phase), ground=True)
    STATE["hannes"] = ha
    # thin the dust right over the ruin: the sky camera must see the figures
    for o in bpy.data.objects:
        if o.name.startswith(("ImpactDust", "BlockTrail", "FireSmoke", "FlameSmoke")) and o.type == "MESH":
            if (o.matrix_world.translation.to_2d() - C).length < float(os.environ.get("CARLA_CLEAR_R", "32")):
                o.hide_render = True
    STATE["figs"] = {"carla": (ca, "head"), "eren": (er, "head"), "mikasa": (mk, "head"), "hannes": (ha, "head"),
                     "eren_handL": (er, "wrist.L"), "titan_head": (ti, "head"), "titan_hand": (ti, "wrist.R")}
    if os.environ.get("CARLA_DEBUG"):
        bpy.context.view_layer.update()
        report_view()
        fmt = lambda v: tuple(round(x, 2) for x in v)
        print("[seq_carla dbg] titan", fmt(ti.location), "head", fmt(_bone_w(ti, "head", "tail")),
              "handR", fmt(_bone_w(ti, "wrist.R", "tail")), "footL", fmt(_bone_w(ti, "foot.L")))
        print("[seq_carla dbg] carla hip", fmt(_bone_w(ca, "upperleg01.L")), "head", fmt(_bone_w(ca, "head", "tail")))
        print("[seq_carla dbg] hannes", mode, fmt(ha.location), "neck", fmt(_bone_w(ha, "neck01")), "footL", fmt(_bone_w(ha, "foot.L")),
              "handR", fmt(_bone_w(ha, "wrist.R", "tail")), "handL", fmt(_bone_w(ha, "wrist.L", "tail")))
        for k in (er, mk):
            print("[seq_carla dbg]", k.name, "hip", fmt(_bone_w(k, "upperleg01.L")), "head", fmt(_bone_w(k, "head", "tail")),
                  "handR", fmt(_bone_w(k, "wrist.R", "tail")), "footL", fmt(_bone_w(k, "foot.L", "tail")))


def report_view():
    """Debug: where the key figures land in the frame (u, v in 0..1) and whether something hides them."""
    import bpy
    from bpy_extras.object_utils import world_to_camera_view
    loc, tgt, lens = cam_at(F)
    cd = bpy.data.cameras.new("DbgCam"); cd.lens = lens
    co = bpy.data.objects.new("DbgCam", cd); bpy.context.scene.collection.objects.link(co)
    co.location = loc; co.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    sc = bpy.context.scene
    sc.render.resolution_x, sc.render.resolution_y = 640, 360
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    for k, (rig, bone) in STATE.get("figs", {}).items():
        if rig is None or rig.hide_render:
            continue
        p = _bone_w(rig, bone, "tail")
        u, v, d = world_to_camera_view(sc, co, p)
        dirv = (p - Vector(loc)); dist = dirv.length
        o0 = Vector(loc)
        while True:
            hit, hl, _, _, ob, _ = sc.ray_cast(dg, o0, dirv.normalized(), distance=dist - (o0 - Vector(loc)).length)
            if hit and ob is not None and (ob.hide_render or (ob.parent and ob.parent.hide_render)):
                o0 = hl + dirv.normalized() * 0.05
                continue
            break
        mine = ob is not None and (ob == rig or ob in rig.children_recursive)
        occ = "clear" if (not hit or mine or (hl - p).length < 0.6) else f"HIDDEN by {ob.name} at {dist - (hl - Vector(loc)).length:.1f} m before"
        print(f"[seq_carla view] {k:11s} px ({u * 640:5.0f},{(1 - v) * 360:5.0f}) dist {dist:5.1f} {occ}")
    bpy.data.objects.remove(co)


def hannes_blades(ha, coll):
    import bmesh, aotlib as L
    m = L.mat("Blade", (0.75, 0.76, 0.78), 0.2)
    bm = bmesh.new()
    for s in ("L", "R"):
        w0 = _bone_w(ha, f"wrist.{s}", "head"); w1 = _bone_w(ha, f"wrist.{s}", "tail")
        d = (w1 - w0).normalized()
        L.cyl(bm, w1, w1 + d * 1.0 + Vector((0, 0, -0.05)), 0.025, 0.012, seg=4, mi=0)
    return L.obj_from_bm("HannesBlades", bm, [m], coll)


def attach_carried(ha, er, mk):
    import bpy
    bpy.context.view_layer.update()
    Rh = ha.matrix_world.to_3x3().normalized()
    fh = Rh @ Vector((0, -1, 0)); rh = Rh @ Vector((-1, 0, 0))       # Hannes's front / right
    neck = _bone_w(ha, "neck01", "head")
    yaw_h = ha.rotation_euler.z
    for kid, yaw, p in ((er, yaw_h + math.pi, neck + fh * 0.27 + rh * 0.2 - Vector((0, 0, 0.42))),
                        (mk, yaw_h + math.pi + 0.35, neck + fh * 0.30 - rh * 0.22 - Vector((0, 0, 0.82)))):
        s = kid.scale.x
        kid.rotation_mode = "XYZ"
        kid.matrix_world = Matrix.Rotation(yaw, 4, "Z") @ Matrix.Scale(s, 4)
        bpy.context.view_layer.update()
        hip = (_bone_w(kid, "upperleg01.L") + _bone_w(kid, "upperleg01.R")) / 2
        kid.matrix_world = Matrix.Translation(p - hip) @ kid.matrix_world


# ---------------------------------------------------------------- S18: boats
def canal_north():
    import aotlib as L
    pts = [Vector((L.CX + math.sin(t / 5) * 60 * min(1, t / 6), 8 + t * 40)) for t in range(0, 40)]
    return pts


def canal_at(s):
    """Point and heading at path distance s north of the water gate."""
    pts = canal_north()
    acc = 0.0
    for a, b in zip(pts, pts[1:]):
        seg = (b - a).length
        if acc + seg >= s:
            t = (s - acc) / seg
            return a.lerp(b, t), (b - a).normalized()
        acc += seg
    return pts[-1], (pts[-1] - pts[-2]).normalized()


def boat(name, seed, coll, crowd=True, bow_gap=0.0):
    import bpy, bmesh, aotlib as L
    r = random.Random(seed)
    mats = [L.mat("BoatHull", _srgb("6B4E35"), 0.8, var=0.15, var_scale=0.6), L.mat("BoatDeck", _srgb("8A6A4A"), 0.85)]
    cloth = [_srgb(h) for h in ("5A4A3A", "7A6A55", "3E4A5A", "8A3A2A", "B0A890", "4A5A3A", "6A5A70")]
    for i, c in enumerate(cloth):
        mats.append(L.mat(f"BoatCloth{i}", c, 0.9))
    mats.append(L.mat("BoatHair", (0.06, 0.04, 0.03), 0.6))
    bm = bmesh.new()
    Lb, Bb = r.uniform(14, 17), r.uniform(3.6, 4.1)
    res = bmesh.ops.create_cube(bm, size=1)
    for v in res["verts"]:
        x, y, z = v.co.x * Lb, v.co.y * Bb, v.co.z * 1.2
        if x > Lb * 0.3:
            y *= 1 - 0.6 * (x - Lb * 0.3) / (Lb * 0.2)
        if z < 0:
            y *= 0.82
        v.co = Vector((x, y, z + 0.3))
    L.box(bm, (0, 0, 0.92), (Lb - 0.8, Bb - 0.5, 0.06), mi=1)
    for k in (-1, 1):                                   # gunwales
        L.box(bm, (0, k * (Bb / 2 - 0.12), 1.0), (Lb * 0.78, 0.18, 0.25), mi=0)
    if crowd:
        for i in range(int(Lb * Bb * 1.1)):
            x, y = r.uniform(-Lb / 2 + 1.0, Lb / 2 - 2.2 - bow_gap), r.uniform(-Bb / 2 + 0.45, Bb / 2 - 0.45)
            hgt = r.uniform(1.4, 1.75)
            L.box(bm, (x, y, 0.95 + hgt * 0.38), (0.42, 0.34, hgt * 0.76), r.uniform(0, 3), mi=2 + r.randrange(len(cloth)))
            L.box(bm, (x, y, 0.95 + hgt * 0.86), (0.22, 0.22, 0.24), 0, mi=2 + len(cloth))
    ob = L.obj_from_bm(name, bm, mats, coll)
    return ob, Lb


def build_s18(M, year, ctx, coll):
    import bpy, aotlib as L
    # the Armored stands in the burst inner gate
    for o in _armored_rigs():
        if o.type == "ARMATURE":
            o.location = (0.0, -6.0, L.height(0, -6) - 0.1)
            o.rotation_euler = (0.12, 0.0, 0.0)
    t = (F - S18[0]) / 30.0
    rope = L.mat("Rope", (0.12, 0.09, 0.06), 0.9)
    lead = None
    for i, (s0, side) in enumerate(((18.0, -3.0), (LEAD_S0, 4.0), (72.0, -2.5), (104.0, 3.5), (140.0, -1.5))):
        s = s0 + FERRY_V * t
        p, d = canal_at(s)
        nrm = Vector((-d.y, d.x))
        p = p + nrm * side
        ob, Lb = boat(f"Ferry{i}", 30 + i, coll, bow_gap=2.0 if i == 1 else 0.0)
        z = L.height(p.x, p.y) + 2.2 - 0.55
        ob.location = (p.x, p.y, z); ob.rotation_euler.z = math.atan2(d.y, d.x)
        if i == 1:
            lead = (ob, Lb, d)
    # tow rope along the canal (rail-guided, sail-less ferries)
    import bmesh
    bm = bmesh.new()
    for a, b in zip(canal_north()[:6], canal_north()[1:6]):
        for k in (-1, 1):
            n = Vector((-(b - a).y, (b - a).x)).normalized() * 9.5 * k
            L.cyl(bm, (a.x + n.x, a.y + n.y, L.height(a.x, a.y) + 3.4), (b.x + n.x, b.y + n.y, L.height(b.x, b.y) + 3.4), 0.05, seg=4)
    L.obj_from_bm("FerryRope", bm, [rope], coll)
    # the kids at the lead boat's bow: Eren standing at the front, fist clenched, Mikasa just behind him
    ob, Lb, d = lead
    bpy.context.view_layer.update()
    er, mk = make_kids("Boat")
    mw = ob.matrix_world
    for kid, lx, ly, yo in ((er, Lb / 2 - 2.2, 0.15, 0.0), (mk, Lb / 2 - 3.1, -0.55, 0.25)):
        p = mw @ Vector((lx, ly, 0.95))
        _place(kid, p.x, p.y, _yaw_to(Vector((d.x, d.y, 0))) + yo, z=p.z)
        r, o = p_stand(0.0)
        if kid is er:
            r["upperarm01.R"] = _Ra(x=-0.25, y=-(LOWER - 0.1)); r["lowerarm01.R"] = _R(x=-1.2)
            r["neck01"] = _R(x=-0.15)
        _pose(kid, r, o, ground=True)
        for o2 in _all_obs(kid):
            for c in list(o2.users_collection):
                c.objects.unlink(o2)
            coll.objects.link(o2)
    STATE["boat"] = Vector(ob.location)
    STATE["figs"] = {"eren": (er, "head"), "mikasa": (mk, "head")}
    if os.environ.get("CARLA_DEBUG"):
        bpy.context.view_layer.update()
        report_view()
        from bpy_extras.object_utils import world_to_camera_view


# ---------------------------------------------------------------- light
def sunset(ctx, b):
    """Low warm sun, orange horizon. S12 late afternoon -> S14 sunset -> S18 dusk."""
    import bpy
    el = {"fly": 16, "S12": 14, "S13": 11, "S14": 7, "S18": 5}[b]
    el = math.radians(float(os.environ.get("CARLA_SUN_EL", el)))
    if b == "S18":
        az = math.radians(200)
    else:
        f, u = STATE["f"], STATE["u"]
        d = -u * 1.0 - f * 0.35
        az = math.atan2(d.y, d.x)                      # low from the side the titan came from: warm side light
    so = ctx.get("sun")
    if so:
        so.data.color = (1.0, 0.62, 0.38) if b != "S18" else (1.0, 0.52, 0.30)
        so.data.energy = float(os.environ.get("CARLA_SUN_E", "3.4"))
        dv = Vector((-math.cos(el) * math.cos(az), -math.cos(el) * math.sin(az), -math.sin(el)))
        so.rotation_euler = dv.to_track_quat("-Z", "Y").to_euler()
    w = ctx.get("world")
    if w:
        for n in w.node_tree.nodes:
            if n.type == "TEX_SKY":
                try:
                    n.sun_elevation = el; n.sun_rotation = az + math.pi / 2
                except Exception:
                    pass
            if n.type == "VALTORGB":
                e = n.color_ramp.elements
                e[0].position, e[0].color = 0.0, (1.0, 0.46, 0.20, 1)
                e[1].position, e[1].color = 0.42, (0.30, 0.30, 0.52, 1)
                mid = n.color_ramp.elements.new(0.12); mid.color = (0.95, 0.62, 0.42, 1)
    hz = bpy.data.objects.get("Haze")
    if hz and hz.data.materials:
        pv = next((n for n in hz.data.materials[0].node_tree.nodes if n.type == "PRINCIPLED_VOLUME"), None)
        if pv:
            pv.inputs["Color"].default_value = (1.0, 0.72, 0.52, 1)


# ---------------------------------------------------------------- cameras: (frame, loc, look_at, lens) in the house frame
def _hf(a, b, z):
    """House-frame point: a metres toward the street (f), b along the front (u), z up."""
    import aotlib as L
    C, f, u = STATE["C"], STATE["f"], STATE["u"]
    p = C + f * a + u * b
    return Vector((p.x, p.y, L.height(C.x, C.y) + z))


def cam_keys():
    k = [
        (S12[0], _hf(32, 16, 40), _hf(0, -4, 1), 32),
        (S12[1] - 20, _hf(28, 10, 32), _hf(0, -7, 4), 30),           # descend and hold; titan walks in from -u
        (S13[0] + 20, _hf(38, 2, 28), _hf(0, -3, 5), 30),            # side-on: Hannes one way, titan the other
        (S14[0],) + tuple(s14_cam(S14[0])),                          # hand over to the S14 auto-framing
    ]
    return k


def _cr(p0, p1, p2, p3, t):
    return 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3)


def _spline_keys(ks, f):
    f = min(max(f, ks[0][0]), ks[-1][0])
    i = max(j for j in range(len(ks)) if ks[j][0] <= f)
    if i == len(ks) - 1:
        return ks[-1][1], ks[-1][2], ks[-1][3]
    a, b = ks[i], ks[i + 1]
    u = (f - a[0]) / (b[0] - a[0])
    u = u * u * (3 - 2 * u)
    P = [Vector(ks[max(0, min(len(ks) - 1, j))][1]) for j in (i - 1, i, i + 1, i + 2)]
    T = [Vector(ks[max(0, min(len(ks) - 1, j))][2]) for j in (i - 1, i, i + 1, i + 2)]
    return _cr(*P, u), _cr(*T, u), a[3] + (b[3] - a[3]) * u


def s14_cam(f):
    """S14: framed on the midpoint between the titan's raised hand and Hannes, slow pull-away (both in one frame)."""
    import aotlib as L
    C, fv, u = STATE["C"], STATE["f"], STATE["u"]
    def mid(ff):
        h, _, _ = hannes_xy(ff)
        return (STATE["T1"] + h) * 0.5
    m = (mid(f - 20) + mid(f) * 2 + mid(min(f + 20, S14[1]))) / 4.0
    g = L.height(C.x, C.y)
    k = _ss(S14[0], S14[1], f)
    pull = _ss(2600, S14[1], f)
    dist = 44 + 6 * k + 18 * pull
    el = math.radians(36 + 6 * pull)
    tgt = Vector((m.x, m.y, g + 5.0))
    loc = tgt + Vector((fv.x, fv.y, 0)) * dist * math.cos(el) + Vector((0, 0, dist * math.sin(el)))
    return loc, tgt, 40 - 4 * pull


LEAD_S0 = 44.0          # lead ferry (the kids at its bow): path distance north of the water gate at S18 start
FERRY_V = 1.3           # m/s


def s18_cam(f):
    """Behind-and-above the lead ferry, looking back past it at the burst inner gate; oath hold, then crane up."""
    import aotlib as L
    t = (f - S18[0]) / 30.0
    p, d = canal_at(LEAD_S0 + FERRY_V * t)
    boat = Vector((p.x, p.y, L.height(p.x, p.y) + 1.5))
    gate = Vector((0.0, 0.0, 12.0))
    away = (boat - gate).to_2d().normalized()
    side = Vector((-away.y, away.x))
    c = _ss(S18[0] + 95, S18[1], f)                       # crane after the ~3 s oath hold
    back = 62 + 40 * c; up = 34 + 95 * c
    loc = boat + Vector((away.x, away.y, 0)) * back + Vector((side.x, side.y, 0)) * (10 + 10 * c) + Vector((0, 0, up))
    tgt = boat.lerp(gate, 0.13 + 0.17 * c); tgt.z = 2.0
    return loc, tgt, 34 - 6 * c


def s18_keys():
    return [
        (S18[0], Vector((318, 118, 34)), Vector((205, 52, 6)), 30),
        (S18[0] + 100, Vector((322, 124, 38)), Vector((203, 52, 6)), 30),       # oath hold (~3 s)
        (S18[1], Vector((360, 175, 135)), Vector((150, 10, 0)), 28),             # crane up over the ferries
    ]


def cam_at(f):
    b = beat(f)
    if b == "S18":
        loc, tgt, lens = s18_cam(f)
    elif b == "S14" and f >= S14[0]:
        loc, tgt, lens = s14_cam(f)
    elif b == "fly":
        ks = cam_keys()
        a = (Vector((40, -840, 200)), Vector((0, -360, 0)), 28.0)                 # seq_colossal's last key (2100)
        u = _ss(*T_FLY, f)
        loc = a[0].lerp(ks[0][1], u); loc.z += math.sin(u * math.pi) * 30
        tgt = a[1].lerp(ks[0][2], u ** 0.7); lens = a[2] + (ks[0][3] - a[2]) * u
    else:
        loc, tgt, lens = _spline_keys(cam_keys(), f)
    return tuple(loc), tuple(tgt), lens


def _cam():
    return cam_at(int(os.environ.get("CARLA_F", F)))


CAMS = {"carla": _cam}
LABELS = {}
