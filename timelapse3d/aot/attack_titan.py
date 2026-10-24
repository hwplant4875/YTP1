"""Attack Titan (Eren, 15 m) from a downloaded Sketchfab model + shifter FX, as a scene.py plug-in and a library.

Asset (local only, never committed):  E:/YTP2/3D Timelapse/assets/sketchfab/attack_shaivs   (env AOT_ATTACK_GLTF)
Credit: "Eren Jaeger (Attack Titan form)" by SHAIVS (https://sketchfab.com/SHAIVS), CC BY 4.0,
        https://sketchfab.com/3d-models/d1724e3f9d68424caeb23a1fd47b6468
Chosen over three other CC-BY candidates (renders/attack_titan/candidates_*.png): Season-1 look (shoulder-length
black hair, pointed ears, lipless cheek-to-cheek teeth, lean muscle), 69-bone Rigify-style rig with jaw/eye bones,
eye glow already in an emissive texture, and an original fan model (the others are game rips).

Library use from any beat plug-in (scene.py must be the running script, so `aotlib` exists):
    import attack_titan as AT
    t = AT.place_attack(x, y, yaw, "roar")      # yaw: heading, radians CCW from +Y (north); 0 = faces north
    t.steam(0.6); t.burning(0.0); t.eyes(25)    # body steam volume, burn/dark state 0..1, eye glow strength
    t.pose("punch", frame=120)                  # re-pose; with frame= it keys every bone (blend between poses)
    AT.face(t, (tx, ty))                        # turn toward a ground point
    AT.boulder_anchor(t, r)                     # world centre for a boulder of radius r held over the shoulders
    AT.make_boulder((x, y, z), r)               # a rough rock
    AT.shift_fx(x, y, t)                        # lightning column, flash, fireball, crescents, steam dome; t 0..1
    AT.shift_fx(x, y, t, frame=f)               # call per frame/t pair to keyframe the same FX set
Poses: stand, roar, punch, carry (boulder over the shoulders), crouch, plus "rest" (the model's bind pose).
Custom poses: POSES[name] = dict(...) with the same keys as the built-ins (metres in the titan frame, see _apply_pose).

Plug-in use: AOT_PLUGINS=attack_titan  adds a demo on the Shiganshina avenue / plaza (AT_DEMO=0 disables it):
    cams  attack_demo (sky view ~85 m, roaring titan in steam)  shift_demo (lightning column mid-shift, AT_T=0.12)
    env   AT_POSE (demo pose, default roar), AT_T (shift time), AT_BURN (0..1), AT_STEAM (0..1)
"""
import bpy, bmesh, glob, math, os, random
from mathutils import Vector, Matrix, Quaternion, Euler
import aotlib as L

SRC = os.environ.get("AOT_ATTACK_GLTF", "E:/YTP2/3D Timelapse/assets/sketchfab/attack_shaivs")
HEIGHT = 15.0
SKIN_TINT = (0.98, 0.76, 0.64)        # texture is pale peach; anime S1 skin is warm reddish tan (#a5806a)
EYE_TINT = (0.62, 1.0, 0.62)          # texture ring is lime; bible emission #74a06a, core #b8e0a0
FINGERS = ("Index", "Middle", "Ring", "Pinkie")

def _ss(a, b, x):
    t = max(0.0, min(1.0, (x - a) / (b - a))) if b != a else float(x >= b)
    return t * t * (3 - 2 * t)

def V(r, f, z):
    """Titan frame (metres): r = titan's right, f = forward, z = up. The native model faces -Y, so right = -X."""
    return Vector((-r, -f, z))

# ------------------------------------------------------------------ poses (titan frame, metres, 15 m titan)
# hips: hip-joint height. bend: [(bone, pitch_deg, yaw_deg, roll_deg)] applied in order (pitch + = lean forward,
# yaw + = turn left, i.e. right shoulder forward). feet: {side: (point, yaw_deg)}, knee pole directions.
# hands: {side: (point, pole, "abs"|"sh")} "sh" = point relative to that shoulder joint. fist 0..1, jaw degrees.
POSES = {
    "stand": dict(hips=8.9, bend=[("spine.001_59", -10, 0, 0), ("spine.002_58", -8, 0, 0), ("spine.003_57", -2, 0, 0),
                                  ("spine.004_10", 4, 0, 0), ("Head_9", 8, 0, 0)],
                  feet={"R": (V(1.45, 0.4, 0), -8), "L": (V(-1.45, 0.1, 0), 8)}, knee=V(0, 1, 0.1),
                  hands={"R": (V(0.9, 0.7, -4.6), V(0.4, -1, 0), "sh"), "L": (V(-0.9, 0.7, -4.6), V(-0.4, -1, 0), "sh")},
                  fist=0.6, jaw=0),
    "roar": dict(hips=8.6, bend=[("spine.001_59", -12, 0, 0), ("spine.002_58", -12, 0, 0), ("spine.003_57", -8, 0, 0),
                                 ("spine.004_10", -14, 0, 0), ("Head_9", -26, 0, 0)],
                 feet={"R": (V(2.3, -0.6, 0), -15), "L": (V(-2.3, 0.9, 0), 15)}, knee=V(0, 1, 0.2),
                 hands={"R": (V(1.9, -1.4, -4.1), V(1, -0.6, 0), "sh"), "L": (V(-1.9, -1.4, -4.1), V(-1, -0.6, 0), "sh")},
                 fist=1.0, jaw=30),
    "punch": dict(hips=7.9, bend=[("spine.001_59", 6, 10, 0), ("spine.002_58", 6, 10, 0), ("spine.003_57", 4, 8, 0),
                                  ("spine.004_10", -2, -12, 0), ("Head_9", -4, -10, 0)],
                  feet={"R": (V(1.7, -2.7, 0), -20), "L": (V(-1.6, 2.9, 0), 10)}, knee=V(0, 1, 0),
                  hands={"R": (V(-0.4, 5.1, 0.2), V(1, 0, -1), "sh"), "L": (V(0.8, 1.7, -1.4), V(-1, 0, -1), "sh")},
                  fist=1.0, jaw=12),
    "carry": dict(hips=7.7, bend=[("spine.001_59", 14, 0, 0), ("spine.002_58", 14, 0, 0), ("spine.003_57", 10, 0, 0),
                                  ("spine.004_10", 8, 0, 0), ("Head_9", 6, 0, 0)],
                  feet={"R": (V(1.6, -1.9, 0), -6), "L": (V(-1.6, 1.6, 0), 6)}, knee=V(0, 1, 0),
                  hands={"R": (V(1.3, -1.2, 2.9), V(1, 0.4, -0.3), "sh"), "L": (V(-1.3, -1.2, 2.9), V(-1, 0.4, -0.3), "sh")},
                  fist=0.3, jaw=8),
    "crouch": dict(hips=4.6, bend=[("spine.001_59", 16, 0, 0), ("spine.002_58", 12, 0, 0), ("spine.003_57", 6, 0, 0),
                                   ("spine.004_10", -12, 0, 0), ("Head_9", -16, 0, 0)],
                   feet={"R": (V(2.2, -0.7, 0), -25), "L": (V(-2.2, 0.9, 0), 25)}, knee=V(0, 1, 0.3),
                   hands={"R": (V(1.6, 4.4, 0.5), V(1, 0, -0.2), "abs"), "L": (V(-1.7, 3.4, 4.3), V(-1, -0.3, 0), "abs")},
                   fist=0.2, jaw=10),
}

# ------------------------------------------------------------------ import
_COUNT = [0]

def _import(name):
    f = (glob.glob(os.path.join(SRC, "**", "*.gltf"), recursive=True) + glob.glob(os.path.join(SRC, "**", "*.glb"), recursive=True))[0]
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=f)
    new = [o for o in bpy.data.objects if o not in before]
    for o in new:
        if o.type == "MESH" and not o.data.materials:          # stray Icosphere in the Sketchfab export
            bpy.data.objects.remove(o, do_unlink=True)
    new = [o for o in bpy.data.objects if o not in before]
    coll = L.new_coll(name)
    for o in new:
        for c in list(o.users_collection):
            c.objects.unlink(o)
        coll.objects.link(o)
    skroot = next(o for o in new if o.parent is None)
    arm = next(o for o in new if o.type == "ARMATURE")
    meshes = [o for o in new if o.type == "MESH"]
    holder = bpy.data.objects.new(name, None); coll.objects.link(holder)
    skroot.parent = holder
    return holder, skroot, arm, meshes, coll


def _bbox(meshes, step=5):
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    pts = []
    for m in meshes:
        ev = m.evaluated_get(dg); me = ev.to_mesh(); mw = ev.matrix_world
        pts += [mw @ v.co for i, v in enumerate(me.vertices) if i % step == 0]
        ev.to_mesh_clear()
    return (Vector([min(p[k] for p in pts) for k in range(3)]), Vector([max(p[k] for p in pts) for k in range(3)]))

# ------------------------------------------------------------------ materials
def _skin_material(mt, tint):
    nt = mt.node_tree; N = nt.nodes; Lk = nt.links
    bsdf = next(n for n in N if n.type == "BSDF_PRINCIPLED")
    base_in = bsdf.inputs["Base Color"]
    src = base_in.links[0].from_socket if base_in.links else None
    mul = N.new("ShaderNodeMix"); mul.data_type = "RGBA"; mul.blend_type = "MULTIPLY"; mul.name = "at_tint"
    mul.inputs["Factor"].default_value = 1.0; mul.inputs["B"].default_value = (*tint, 1)
    if src:
        Lk.new(src, mul.inputs["A"])
    else:
        mul.inputs["A"].default_value = base_in.default_value
    # burning state: darken toward charred red-brown, orange glowing cracks (Voronoi edges) in emission
    burn = N.new("ShaderNodeValue"); burn.name = "at_burn"; burn.outputs[0].default_value = 0.0
    dark = N.new("ShaderNodeMix"); dark.data_type = "RGBA"; dark.name = "at_dark"
    dark.inputs["B"].default_value = (0.16, 0.055, 0.04, 1)
    Lk.new(mul.outputs["Result"], dark.inputs["A"]); Lk.new(burn.outputs[0], dark.inputs["Factor"])
    Lk.new(dark.outputs["Result"], base_in)
    tc = N.new("ShaderNodeTexCoord")
    vo = N.new("ShaderNodeTexVoronoi"); vo.feature = "DISTANCE_TO_EDGE"; vo.inputs["Scale"].default_value = 9.0
    Lk.new(tc.outputs["Object"], vo.inputs["Vector"])
    cr = N.new("ShaderNodeMapRange"); cr.inputs["From Min"].default_value = 0.035; cr.inputs["From Max"].default_value = 0.0
    Lk.new(vo.outputs["Distance"], cr.inputs["Value"])
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 3.0
    Lk.new(tc.outputs["Object"], nz.inputs["Vector"])
    nm = N.new("ShaderNodeMapRange"); nm.inputs["From Min"].default_value = 0.45; nm.inputs["From Max"].default_value = 0.62
    Lk.new(nz.outputs["Fac"], nm.inputs["Value"])
    m1 = N.new("ShaderNodeMath"); m1.operation = "MULTIPLY"; Lk.new(cr.outputs[0], m1.inputs[0]); Lk.new(nm.outputs[0], m1.inputs[1])
    m2 = N.new("ShaderNodeMath"); m2.operation = "MULTIPLY"; Lk.new(m1.outputs[0], m2.inputs[0]); Lk.new(burn.outputs[0], m2.inputs[1])
    crack = N.new("ShaderNodeMix"); crack.data_type = "RGBA"; crack.blend_type = "MULTIPLY"; crack.inputs["Factor"].default_value = 1
    crack.inputs["B"].default_value = (1.0, 0.32, 0.06, 1)
    Lk.new(m2.outputs[0], crack.inputs["A"])
    # eye glow: emissive texture (green ring) tinted, at strength `at_eye`; cracks added at a fixed ratio
    em_in = bsdf.inputs["Emission Color"]
    esrc = em_in.links[0].from_socket if em_in.links else None
    eye = N.new("ShaderNodeMix"); eye.data_type = "RGBA"; eye.blend_type = "MULTIPLY"; eye.inputs["Factor"].default_value = 1
    eye.inputs["B"].default_value = (*EYE_TINT, 1)
    if esrc:
        Lk.new(esrc, eye.inputs["A"])
    else:
        eye.inputs["A"].default_value = (0, 0, 0, 1)
    estr = N.new("ShaderNodeValue"); estr.name = "at_eye"; estr.outputs[0].default_value = 20.0
    ke = N.new("ShaderNodeMix"); ke.data_type = "RGBA"; ke.blend_type = "MULTIPLY"; ke.inputs["Factor"].default_value = 1
    Lk.new(eye.outputs["Result"], ke.inputs["A"])
    cv = N.new("ShaderNodeCombineXYZ")
    for i in range(3):
        Lk.new(estr.outputs[0], cv.inputs[i])
    Lk.new(cv.outputs[0], ke.inputs["B"])
    crk = N.new("ShaderNodeVectorMath"); crk.operation = "SCALE"; crk.inputs["Scale"].default_value = 6.0
    Lk.new(crack.outputs["Result"], crk.inputs[0])
    add = N.new("ShaderNodeVectorMath"); add.operation = "ADD"
    Lk.new(ke.outputs["Result"], add.inputs[0]); Lk.new(crk.outputs[0], add.inputs[1])
    Lk.new(add.outputs[0], em_in)
    bsdf.inputs["Emission Strength"].default_value = 1.0
    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = 0.08
        bsdf.inputs["Subsurface Radius"].default_value = (1.0, 0.35, 0.2)
    bsdf.inputs["Roughness"].default_value = 0.6


def _ink_material(flipped):
    m = bpy.data.materials.new("AT_Ink"); m.use_nodes = True
    nt = m.node_tree; N = nt.nodes; Lk = nt.links
    N.remove(N["Principled BSDF"])
    em = N.new("ShaderNodeEmission"); em.inputs["Color"].default_value = (0.035, 0.02, 0.015, 1)
    tr = N.new("ShaderNodeBsdfTransparent"); geo = N.new("ShaderNodeNewGeometry"); mx = N.new("ShaderNodeMixShader")
    Lk.new(geo.outputs["Backfacing"], mx.inputs[0])
    a, b = (em, tr) if flipped else (tr, em)
    Lk.new(a.outputs[0], mx.inputs[1]); Lk.new(b.outputs[0], mx.inputs[2])
    Lk.new(mx.outputs[0], N["Material Output"].inputs["Surface"])
    return m


def _volume(name, center, size, density, color=(1, 1, 1), noise_scale=2.2, edge=(0.12, 0.42), coll=None):
    """Steam box: noisy density with a spherical falloff (a half-buried box makes a dome). Returns (obj, density node)."""
    me = bpy.data.meshes.new(name); bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); (coll or bpy.context.scene.collection).objects.link(ob)
    ob.location = center; ob.scale = size
    sm = bpy.data.materials.new(name); sm.use_nodes = True; nt = sm.node_tree; N = nt.nodes; Lk = nt.links
    N.remove(N["Principled BSDF"])
    pv = N.new("ShaderNodeVolumePrincipled"); pv.inputs["Color"].default_value = (*color, 1); pv.inputs["Anisotropy"].default_value = 0.3
    tc = N.new("ShaderNodeTexCoord"); nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = noise_scale
    nz.inputs["Detail"].default_value = 6; nz.inputs["Roughness"].default_value = 0.6
    Lk.new(tc.outputs["Generated"], nz.inputs["Vector"])
    gr = N.new("ShaderNodeTexGradient"); gr.gradient_type = "SPHERICAL"
    mp = N.new("ShaderNodeMapping"); mp.inputs["Location"].default_value = (-1, -1, -1); mp.inputs["Scale"].default_value = (2, 2, 2)
    Lk.new(tc.outputs["Generated"], mp.inputs["Vector"]); Lk.new(mp.outputs[0], gr.inputs["Vector"])
    mul = N.new("ShaderNodeMath"); mul.operation = "MULTIPLY"
    Lk.new(nz.outputs["Fac"], mul.inputs[0]); Lk.new(gr.outputs["Fac"], mul.inputs[1])
    mr = N.new("ShaderNodeMapRange"); mr.inputs["From Min"].default_value = edge[0]; mr.inputs["From Max"].default_value = edge[1]
    mr.inputs["To Max"].default_value = density
    Lk.new(mul.outputs[0], mr.inputs["Value"]); Lk.new(mr.outputs["Result"], pv.inputs["Density"])
    Lk.new(pv.outputs[0], N["Material Output"].inputs["Volume"]); me.materials.append(sm)
    ob.visible_shadow = True
    return ob, mr.inputs["To Max"], pv

# ------------------------------------------------------------------ the titan
class AttackTitan:
    def __init__(self, name):
        self.name = name
        self.holder, self.skroot, self.arm, self.meshes, self.coll = _import(name)
        self.skin_mats = []
        for m in self.meshes:
            for i, mt in enumerate(m.data.materials):
                if mt is None:
                    continue
                if hasattr(mt, "surface_render_method"):
                    mt.surface_render_method = "DITHERED"
                if mt.name.startswith("Body"):
                    nm = mt.copy(); nm.name = name + "_Body"; m.data.materials[i] = nm
                    _skin_material(nm, SKIN_TINT); self.skin_mats.append(nm)
                elif mt.name.startswith("Outline"):
                    self._setup_outline(m, i)
                elif mt.name.startswith("Hair"):
                    nt = mt.node_tree
                    b = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"); b.inputs["Roughness"].default_value = 0.55
        self._steam = None
        self.rest_rot = {pb.name: pb.bone.matrix_local.to_quaternion() for pb in self.arm.pose.bones}
        # scale to 15 m measured in the "stand" pose, rest-ground the model
        mn, mx = _bbox(self.meshes)
        self.skroot.scale = [v * HEIGHT / (mx.z - mn.z) for v in self.skroot.scale]
        self._ground_rest()
        for _ in range(3):          # pose targets are in metres, so converge scale <-> stand height
            self.pose("stand", ground=False)
            mn, mx = _bbox(self.meshes, step=9)
            k = HEIGHT / (mx.z - mn.z)
            self._reset()
            self.skroot.scale = [v * k for v in self.skroot.scale]
            self._ground_rest()
        self._eye_halos()
        self.pose_name = "rest"

    def _eye_halos(self):
        """Small camera-only emissive balls on the eye bones so the green glow still reads from 60-90 m (texture eyes are ~1 px)."""
        m, self.halo_s = _emit_mat(self.name + "_EyeHalo", (0.55, 1.0, 0.5), 6.0)
        self.halos = []
        for bn in ("Eye.L_3", "Eye.R_4"):
            bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=6, radius=float(os.environ.get("AT_HALO", "0.16")))
            ob = L.obj_from_bm(self.name + "_" + bn[:5], bm, [m], self.coll)
            for a in ("visible_shadow", "visible_diffuse", "visible_glossy", "visible_transmission", "visible_volume_scatter"):
                setattr(ob, a, False)
            p = self.wpos(bn) + V(0, 0.22, -0.05)
            ob.parent = self.arm; ob.parent_type = "BONE"; ob.parent_bone = bn
            bpy.context.view_layer.update()
            ob.matrix_world = Matrix.Translation(p)
            self.halos.append(ob)

    # --- helpers -----------------------------------------------------------
    def _setup_outline(self, m, i):
        me = m.data
        c = sum((v.co for v in me.vertices), Vector()) / len(me.vertices)
        out = sum((v.normal.dot(v.co - c) for i, v in enumerate(me.vertices) if i % 50 == 0))
        flipped = out < 0
        ink = _ink_material(flipped); me.materials[i] = ink
        m.visible_shadow = False; m.visible_diffuse = False; m.visible_glossy = False
        m.visible_transmission = False; m.visible_volume_scatter = False
        if os.environ.get("LINES", "1") == "0":
            m.hide_render = True

    def _reset(self):
        for pb in self.arm.pose.bones:
            pb.matrix_basis = Matrix.Identity(4)
        bpy.context.view_layer.update()

    def _ground_rest(self):
        """Holder at identity while posing: rest model with its feet on z=0 and hip centre over the origin."""
        hm = self.holder.matrix_world.copy()
        self.holder.matrix_world = Matrix.Identity(4)
        self.skroot.location = (0, 0, 0)
        bpy.context.view_layer.update()
        mn, mx = _bbox(self.meshes)
        hp = self.wpos("spine_68", tail=False)
        self.skroot.location = Vector((-hp.x, -hp.y, -mn.z))
        bpy.context.view_layer.update()
        self.rest_z = self.skroot.location.z
        self.holder.matrix_world = hm
        bpy.context.view_layer.update()

    @property
    def scale(self):
        return self.arm.matrix_world.to_scale().x

    def wmat(self, bn):
        return self.arm.matrix_world @ self.arm.pose.bones[bn].matrix

    def wpos(self, bn, tail=False):
        pb = self.arm.pose.bones[bn]
        return self.arm.matrix_world @ (pb.tail if tail else pb.head)

    def _set_world(self, bn, rot, loc=None):
        pb = self.arm.pose.bones[bn]
        mw = self.arm.matrix_world
        l, _, s = (mw @ pb.matrix).decompose()
        if loc is not None:
            l = loc
        W = Matrix.Translation(l) @ rot.to_matrix().to_4x4() @ Matrix.Diagonal((*s, 1.0))
        pb.matrix = mw.inverted() @ W
        bpy.context.view_layer.update()

    def _rot_world(self, bn, q):
        """Rotate bone (and its children) about its head by world quaternion q."""
        _, r, _ = self.wmat(bn).decompose()
        self._set_world(bn, q @ r)

    def _frame(self, bn, ydir, xref):
        """World rotation with bone Y along ydir and bone X as close as possible to xref."""
        y = ydir.normalized()
        x = (xref - y * xref.dot(y))
        if x.length < 1e-6:
            x = y.orthogonal()
        x.normalize(); z = x.cross(y)
        return Matrix((x, y, z)).transposed().to_quaternion()

    def _rest_x(self, bn):
        """Bone's rest X axis in the titan frame (holder at identity)."""
        return (self.arm.matrix_world.to_quaternion() @ self.rest_rot[bn]) @ Vector((1, 0, 0))

    def _two_bone(self, b1, b2, target, pole):
        A = self.wpos(b1)
        l1 = (self.wpos(b1, True) - A).length; l2 = (self.wpos(b2, True) - self.wpos(b2)).length
        d = target - A; dist = min(d.length, (l1 + l2) * 0.995); dist = max(dist, abs(l1 - l2) + 1e-3)
        u = d.normalized()
        v = pole - u * pole.dot(u)
        if v.length < 1e-6:
            v = u.orthogonal()
        v.normalize()
        ca = (l1 * l1 + dist * dist - l2 * l2) / (2 * l1 * dist); ca = max(-1, min(1, ca)); sa = math.sqrt(1 - ca * ca)
        E = A + u * (l1 * ca) + v * (l1 * sa)
        T = A + u * dist
        n = v.cross(u).normalized()
        # keep the rest relation between bend-plane normal and the bones' X axes
        rn = (self.wpos(b1, True) - A).cross(self.wpos(b2, True) - self.wpos(b2))
        rx = self._rest_x(b1)
        sgn = 1.0 if (rn.length < 1e-6 or rx.dot(rn) >= 0) else -1.0
        self._set_world(b1, self._frame(b1, E - A, n * sgn))
        self._set_world(b2, self._frame(b2, T - E, n * sgn))

    def _curl(self, side, amt):
        if amt <= 0:
            return
        for f in FINGERS:
            for k, a in ((1, 50), (2, 70), (3, 60), (4, 40)):
                bn = next((b.name for b in self.arm.pose.bones if b.name.startswith(f"{f}.00{k}.{side}_")), None)
                if bn:
                    pb = self.arm.pose.bones[bn]
                    pb.rotation_quaternion = Quaternion((1, 0, 0), math.radians(a * amt)) @ pb.rotation_quaternion
        for k, a in ((2, 25), (3, 35)):
            bn = next((b.name for b in self.arm.pose.bones if b.name.startswith(f"Thumb.00{k}.{side}_")), None)
            if bn:
                pb = self.arm.pose.bones[bn]
                pb.rotation_quaternion = Quaternion((1, 0, 0), math.radians(a * amt)) @ pb.rotation_quaternion
        bpy.context.view_layer.update()

    # --- public ------------------------------------------------------------
    def pose(self, name, frame=None, ground=True):
        spec = POSES[name] if name != "rest" else None
        hm = self.holder.matrix_world.copy()
        self.holder.matrix_world = Matrix.Identity(4)
        self.skroot.location.z = self.rest_z
        self._reset()
        if spec:
            _apply_pose(self, spec)
        if ground:
            mn, mx = _bbox(self.meshes, step=9)
            self.skroot.location.z -= mn.z
        self.holder.matrix_world = hm
        bpy.context.view_layer.update()
        self.pose_name = name
        if frame is not None:
            for pb in self.arm.pose.bones:
                pb.keyframe_insert("rotation_quaternion", frame=frame)
                pb.keyframe_insert("location", frame=frame)
            self.skroot.keyframe_insert("location", frame=frame)
        return self

    def place(self, x, y, yaw=0.0, z=None, frame=None):
        self.holder.location = (x, y, L.height(x, y) if z is None else z)
        self.holder.rotation_euler = (0, 0, yaw + math.pi)          # native front -Y -> heading yaw from +Y
        if frame is not None:
            self.holder.keyframe_insert("location", frame=frame); self.holder.keyframe_insert("rotation_euler", frame=frame)
        bpy.context.view_layer.update()
        return self

    def eyes(self, strength=20.0, frame=None):
        for m in self.skin_mats:
            s = m.node_tree.nodes["at_eye"].outputs[0]; s.default_value = strength
            if frame is not None:
                s.keyframe_insert("default_value", frame=frame)
        self.halo_s.default_value = strength * 0.3
        if frame is not None:
            self.halo_s.keyframe_insert("default_value", frame=frame)
        return self

    def burning(self, amount=1.0, frame=None):
        """0 = normal skin, 1 = Ep21/25 rage state: charred dark red with orange glowing cracks (pair with steam())."""
        for m in self.skin_mats:
            s = m.node_tree.nodes["at_burn"].outputs[0]; s.default_value = amount
            if frame is not None:
                s.keyframe_insert("default_value", frame=frame)
        return self

    def steam(self, amount=0.5, frame=None):
        """White steam column hugging the body (regeneration / after-fight / burning state)."""
        if self._steam is None:
            ob, dens, _ = _volume(self.name + "_Steam", (0, 0, 8.5), (13, 13, 20), 0.0, noise_scale=3.0, coll=self.coll,
                                  edge=(0.10, 0.36))
            ob.parent = self.holder
            self._steam = (ob, dens)
        ob, dens = self._steam
        dens.default_value = 0.55 * amount
        ob.hide_render = amount <= 0 and frame is None
        if frame is not None:
            dens.keyframe_insert("default_value", frame=frame)
        return self

    def head_world(self):
        return self.wpos("Head_9")


def _apply_pose(t, s):
    """Pose spec -> bones. Order: hips height, spine/head bends, legs (2-bone IK + flat feet), arms (IK), fists, jaw."""
    up = Vector((0, 0, 1))
    hip = (t.wpos("thigh.L_63") + t.wpos("thigh.R_67")) / 2
    root = "GLTF_created_0_rootJoint"
    t._set_world(root, t.wmat(root).decompose()[1], t.wpos(root) + Vector((0, 0, s["hips"] - hip.z)))
    right, fwd = V(1, 0, 0), V(0, 1, 0)
    for bn, pitch, yaw, roll in s.get("bend", []):
        q = Quaternion(up, math.radians(yaw)) @ Quaternion(right, math.radians(-pitch)) @ Quaternion(fwd, math.radians(roll))
        t._rot_world(bn, q)
    ank = 0.75                                        # ankle height of a flat foot at 15 m
    for side, (thigh, shin, foot, toe) in (("L", ("thigh.L_63", "shin.L_62", "foot.L_61", "toe.L_60")),
                                           ("R", ("thigh.R_67", "shin.R_66", "foot.R_65", "toe.R_64"))):
        p, fyaw = s["feet"][side]
        target = Vector((p.x, p.y, p.z + ank))
        knee = s.get("knee", fwd) + (V(0.25, 0, 0) if side == "R" else V(-0.25, 0, 0))
        t._two_bone(thigh, shin, target, knee)
        qy = Quaternion(up, math.radians(fyaw))
        fdir = qy @ (fwd * 0.8 - up * 0.6)
        t._set_world(foot, t._frame(foot, fdir, qy @ t._rest_x(foot)))
        t._set_world(toe, t._frame(toe, qy @ (fwd - up * 0.05), qy @ t._rest_x(toe)))
    for side, (ua, fa) in (("L", ("upper_arm.L_32", "forearm.L_31")), ("R", ("upper_arm.R_55", "forearm.R_54"))):
        p, pole, mode = s["hands"][side]
        target = (t.wpos(ua) + p) if mode == "sh" else p
        t._two_bone(ua, fa, target, pole)
    for side in ("L", "R"):
        t._curl(side, s.get("fist", 0))
    j = s.get("jaw", 0)
    if j:
        pb = t.arm.pose.bones["Jaw_2"]
        pb.rotation_quaternion = Quaternion((1, 0, 0), math.radians(JAW_SIGN * j)) @ pb.rotation_quaternion
        bpy.context.view_layer.update()

JAW_SIGN = float(os.environ.get("AT_JAW_SIGN", "1"))


def place_attack(x, y, yaw=0.0, pose="stand", name=None, steam=0.0, burning=0.0, eyes=20.0):
    """Import one Attack Titan (15 m), pose it and stand it at ground point (x, y), heading `yaw` (radians CCW from +Y)."""
    _COUNT[0] += 1
    t = AttackTitan(name or f"AttackTitan{_COUNT[0]}")
    t.pose(pose)
    t.place(x, y, yaw)
    t.eyes(eyes)
    if burning:
        t.burning(burning)
    if steam:
        t.steam(steam)
    return t


def face(t, target, frame=None):
    """Turn titan t toward ground point target=(x, y)."""
    dx, dy = target[0] - t.holder.location.x, target[1] - t.holder.location.y
    return t.place(t.holder.location.x, t.holder.location.y, math.atan2(-dx, dy), z=t.holder.location.z, frame=frame)


def boulder_anchor(t, r=6.0):
    """World centre of a boulder of radius r resting across the back of the shoulders (carry pose)."""
    sl, sr = t.wpos("upper_arm.L_32"), t.wpos("upper_arm.R_55")
    mid = (sl + sr) / 2
    q = t.holder.matrix_world.to_quaternion()
    back = q @ V(0, -1, 0)
    return mid + Vector((0, 0, r * 0.62 + 0.4)) + back * (r * 0.38)


def make_boulder(center, r=6.0, name="Boulder", seed=3):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=4, radius=r)
    rnd = random.Random(seed); from mathutils import noise as mn
    off = Vector((rnd.random() * 50, rnd.random() * 50, rnd.random() * 50))
    for v in bm.verts:
        n = v.co.normalized()
        d = 0.18 * mn.noise(n * 1.3 + off) + 0.07 * mn.noise(n * 4 + off) + 0.03 * mn.noise(n * 11 + off)
        v.co = n * r * (1 + d) * Vector((1.25, 1.0, 0.82))
    m = L.mat("BoulderRock", (0.36, 0.33, 0.29), rough=0.95, bump=0.4, scale=0.4, var=0.12, var_scale=0.15)
    ob = L.obj_from_bm(name, bm, [m]); ob.location = center
    for f in ob.data.polygons:
        f.use_smooth = True
    return ob

# ------------------------------------------------------------------ shifter FX
_FX = {}

def _emit_mat(name, col, strength):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; N = nt.nodes; N.remove(N["Principled BSDF"])
    em = N.new("ShaderNodeEmission"); em.inputs["Color"].default_value = (*col, 1); em.inputs["Strength"].default_value = strength
    nt.links.new(em.outputs[0], N["Material Output"].inputs["Surface"])
    return m, em.inputs["Strength"]


def _bolt_pts(rnd, top, bottom, n, amp):
    pts = []
    for i in range(n + 1):
        f = i / n
        p = top.lerp(bottom, f)
        a = amp * (0.25 + 0.75 * math.sin(math.pi * min(1, f * 1.1)))
        if 0 < i < n:
            p += Vector((rnd.uniform(-a, a), rnd.uniform(-a, a), rnd.uniform(-a, a) * 0.3))
        pts.append(p)
    return pts


def _curve(name, pts, width, mat, coll):
    cu = bpy.data.curves.new(name, "CURVE"); cu.dimensions = "3D"; cu.bevel_depth = width; cu.bevel_resolution = 1
    sp = cu.splines.new("POLY"); sp.points.add(len(pts) - 1)
    for i, p in enumerate(pts):
        sp.points[i].co = (*p, 1)
    cu.materials.append(mat)
    ob = bpy.data.objects.new(name, cu); coll.objects.link(ob)
    ob.visible_shadow = False
    return ob


def _make_fx(x, y, seed):
    z0 = L.height(x, y)
    c = L.new_coll(f"ShiftFX_{len(_FX)}")
    rnd = random.Random(seed)
    base = Vector((x, y, z0))
    bolt_m, bolt_s = _emit_mat("ShiftBolt", (1.0, 0.86, 0.5), 0.0)
    bolts = []
    # main column: 2 intertwined strokes from the sky to the ground, plus branches
    for k in range(2):
        top = base + Vector((rnd.uniform(-25, 25), rnd.uniform(-25, 25), 320))
        pts = _bolt_pts(rnd, top, base + Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), 2)), 28, 9.0)
        bolts.append(_curve(f"Bolt{k}", pts, 1.1 - 0.4 * k, bolt_m, c))
        for b in range(4):
            i = rnd.randint(5, 24); p0 = pts[i]
            d = Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), -rnd.uniform(0.3, 1.0))).normalized()
            bp = _bolt_pts(rnd, p0, p0 + d * rnd.uniform(25, 60), 8, 4.0)
            bolts.append(_curve(f"Bolt{k}_{b}", bp, 0.35, bolt_m, c))
    # white-gold crescent streaks around the forming body (Ep21 frame)
    cres_m, cres_s = _emit_mat("ShiftCrescent", (1.0, 0.93, 0.72), 0.0)
    cres = []
    for k in range(14):
        rr = rnd.uniform(9, 16); az = rnd.uniform(0, 2 * math.pi); el0 = rnd.uniform(-0.3, 0.6)
        span = rnd.uniform(0.6, 1.2); tilt = rnd.uniform(-0.5, 0.5)
        pts = []
        for i in range(13):
            f = i / 12
            a = az + (f - 0.5) * span
            el = el0 + (f - 0.5) * tilt
            pts.append(base + Vector((math.cos(a) * math.cos(el) * rr, math.sin(a) * math.cos(el) * rr, 9 + math.sin(el) * rr)))
        ob = _curve(f"Crescent{k}", pts, 0.22, cres_m, c)
        ob.data.bevel_factor_mapping_start = "SPLINE"
        cres.append(ob)
    # fireball core
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=3, radius=1.0)
    core_m, core_s = _emit_mat("ShiftCore", (1.0, 0.7, 0.35), 0.0)
    core = L.obj_from_bm("ShiftCore", bm, [core_m], c); core.location = base + Vector((0, 0, 7))
    for f in core.data.polygons:
        f.use_smooth = True
    core.visible_shadow = False
    # flash light
    ld = bpy.data.lights.new("ShiftFlash", "POINT"); ld.color = (1.0, 0.84, 0.6); ld.shadow_soft_size = 6.0
    lo = bpy.data.objects.new("ShiftFlash", ld); c.objects.link(lo); lo.location = base + Vector((0, 0, 22))
    # steam dome (half-buried volume) + its warm inner glow tint via the volume emission
    dome, dome_d, dome_pv = _volume("ShiftDome", base, (2, 2, 2), 0.0, noise_scale=2.6, coll=c, edge=(0.12, 0.4))
    dome_pv.inputs["Emission Color"].default_value = (1.0, 0.55, 0.25, 1)
    fx = dict(bolts=bolts, bolt_s=bolt_s, cres=cres, cres_s=cres_s, core=core, core_s=core_s, light=ld, light_o=lo,
              dome=dome, dome_d=dome_d, dome_e=dome_pv.inputs["Emission Strength"], base=base, coll=c)
    return fx


def shift_fx(x, y, t, frame=None, seed=11, scale=1.0):
    """Shifter transformation at ground point (x, y). t 0..1:
       0.00-0.30 lightning column from the sky (flicker), 0.03-0.40 flash light + fireball core,
       0.06-0.50 white-gold crescent streaks, 0.05-1.0 steam dome grows (r 6 -> 36 m) and thins after 0.7.
       Pass frame= on repeated calls to keyframe one FX set; returns the FX dict."""
    key = (round(x, 2), round(y, 2), seed)
    if key not in _FX:
        _FX[key] = _make_fx(x, y, seed)
    fx = _FX[key]
    bolt = _ss(0.0, 0.025, t) * (1 - _ss(0.18, 0.30, t))
    flick = 0.55 + 0.45 * abs(math.sin(t * 157.0))
    flash = _ss(0.02, 0.07, t) * (1 - _ss(0.10, 0.40, t))
    crescent = _ss(0.06, 0.12, t) * (1 - _ss(0.30, 0.50, t))
    r = (6 + 30 * _ss(0.05, 0.65, t)) * scale
    dens = 0.9 * _ss(0.05, 0.16, t) * (1 - 0.75 * _ss(0.70, 1.0, t))
    fx["bolt_s"].default_value = 60.0 * bolt * flick
    fx["cres_s"].default_value = 18.0 * crescent
    fx["core_s"].default_value = 40.0 * flash
    cs = (3 + 9 * _ss(0.03, 0.3, t)) * scale
    fx["core"].scale = (cs, cs, cs * 1.3)
    fx["light"].energy = 2.5e6 * flash * scale * scale
    fx["dome"].scale = (2 * r, 2 * r, 2 * r * 0.9)
    fx["dome"].location = fx["base"] + Vector((0, 0, r * 0.25))
    fx["dome_d"].default_value = dens
    fx["dome_e"].default_value = 3.0 * flash
    vis = {"bolts": bolt > 0.001, "cres": crescent > 0.001}
    for o in fx["bolts"]:
        o.hide_render = not vis["bolts"] and frame is None
    for o in fx["cres"]:
        o.hide_render = not vis["cres"] and frame is None
    fx["core"].hide_render = flash <= 0.001 and frame is None
    fx["dome"].hide_render = dens <= 0.001 and frame is None
    if frame is not None:
        for s in ("bolt_s", "cres_s", "core_s", "dome_d", "dome_e"):
            fx[s].keyframe_insert("default_value", frame=frame)
        fx["light"].keyframe_insert("energy", frame=frame)
        fx["core"].keyframe_insert("scale", frame=frame)
        fx["dome"].keyframe_insert("scale", frame=frame); fx["dome"].keyframe_insert("location", frame=frame)
    return fx

# ------------------------------------------------------------------ plug-in demo
DEMO_A = (2.0, -232.0)          # on the main avenue (Trost-like town street), facing north up the avenue
DEMO_B = (-20.0, -360.0)        # plaza: open space for the transformation
_DEMO = {}

def build(M, year, ctx):
    if os.environ.get("AT_DEMO", "1") == "0":
        return
    burn = float(os.environ.get("AT_BURN", "0")); st = float(os.environ.get("AT_STEAM", "0.45"))
    t = place_attack(DEMO_A[0], DEMO_A[1], 0.0, os.environ.get("AT_POSE", "roar"), name="AttackDemo",
                     steam=st, burning=burn, eyes=float(os.environ.get("AT_EYE", "25")))
    if t.pose_name == "carry":
        r = 6.0; make_boulder(boulder_anchor(t, r), r)
    _DEMO["titan"] = t
    shift_fx(DEMO_B[0], DEMO_B[1], float(os.environ.get("AT_T", "0.12")))
    mn, mx = _bbox(t.meshes, 9)
    print("[attack_titan] demo titan bbox", tuple(round(v, 1) for v in mn), tuple(round(v, 1) for v in mx))


def _cam_attack():
    x, y = DEMO_A; g = L.height(x, y)
    return ((x + 48, y + 52, g + 58), (x, y, g + 8.5), 38)


def _cam_shift():
    x, y = DEMO_B; g = L.height(x, y)
    return ((x + 70, y - 62, g + 62), (x, y, g + 22), 28)

CAMS = {"attack_demo": _cam_attack, "shift_demo": _cam_shift}
LABELS = {}
