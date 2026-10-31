# 현실파괴범 EP01 POV builder: Quaternius character + UAL actions, first-person camera.
# python3 pov.py <shot> <out.png> [pct]   shots: dbg_sit, dbg_walk, a_sit, b_look
import bpy, math, sys, os
from mathutils import Vector, Matrix
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = open(os.path.join(HERE, "..", "ep01_3d", "scene.py")).read().split("# ---------------- shots")[0]
exec(SRC)  # materials, build_world, picnic, tree, setup, srgb ...
A = os.environ.get("WHATIF_ASSETS", "/mnt/project-files/whatif_kr/assets")

def flat_clothes(m, top_c="#ff6a3d", pants_c="#2c3f66", skin_c="#efc3a0"):
    """Replace the suit texture with skin / hoodie / jeans / white shoes, masked by rest-pose height."""
    nt = m.node_tree; b = [n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"][0]
    tc = nt.nodes.new("ShaderNodeTexCoord"); sp = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Generated"], sp.inputs[0])
    def M_(op, a, bb=None):
        n = nt.nodes.new("ShaderNodeMath"); n.operation = op
        for i, v in enumerate((a, bb)):
            if v is None: continue
            if isinstance(v, (int, float)): n.inputs[i].default_value = v
            else: nt.links.new(v, n.inputs[i])
        return n.outputs[0]
    z, x = sp.outputs["Z"], sp.outputs["X"]
    ax = M_("ABSOLUTE", M_("SUBTRACT", x, 0.5))
    armz = M_("LESS_THAN", z, 0.848); bodyz = M_("LESS_THAN", z, 0.83)
    isarm = M_("GREATER_THAN", ax, 0.11)
    top = M_("MAXIMUM", M_("MULTIPLY", isarm, armz), bodyz)
    top = M_("MULTIPLY", top, M_("LESS_THAN", ax, 0.40))
    top = M_("MULTIPLY", top, M_("GREATER_THAN", z, 0.5))
    pants = M_("LESS_THAN", z, 0.52); shoe = M_("LESS_THAN", z, 0.055)
    col = None
    def mix(fac, c_from, c_to):
        n = nt.nodes.new("ShaderNodeMix"); n.data_type = "RGBA"
        nt.links.new(fac, n.inputs[0])
        for idx, c in ((6, c_from), (7, c_to)):
            if isinstance(c, tuple): n.inputs[idx].default_value = (*c, 1)
            else: nt.links.new(c, n.inputs[idx])
        return n.outputs[2]
    col = mix(top, srgb(skin_c), srgb(top_c))
    col = mix(pants, col, srgb(pants_c))
    col = mix(shoe, col, srgb("#f4f4f4"))
    nt.links.new(col, b.inputs["Base Color"])
    for l in list(nt.links):
        if l.to_socket in (b.inputs["Roughness"], b.inputs["Normal"]): nt.links.remove(l)
    b.inputs["Roughness"].default_value = 0.7
    b.inputs["Metallic"].default_value = 0.0

HDR = os.environ.get("WHATIF_HDR", "/tmp/claude-0/-home-user-YTP1/2467b228-e69f-511a-89d6-1349fcd7b3c8/scratchpad/assets/sunset.hdr")
def hdri_world(rot_deg=-150, strength=1.0, sun_dir=(-0.4, 0.92, 0.04)):
    nt = S.world.node_tree
    for n in list(nt.nodes):
        if n.type == "TEX_SKY": nt.nodes.remove(n)
    tc = nt.nodes.new("ShaderNodeTexCoord"); mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Rotation"].default_value = (0, 0, math.radians(rot_deg))
    env = nt.nodes.new("ShaderNodeTexEnvironment"); env.image = bpy.data.images.load(HDR)
    nt.links.new(tc.outputs["Generated"], mp.inputs[0]); nt.links.new(mp.outputs[0], env.inputs[0])
    nt.links.new(env.outputs[0], nt.nodes["Background"].inputs[0])
    nt.nodes["Background"].inputs[1].default_value = strength
    sun = bpy.data.objects["sun"]; d = Vector(sun_dir).normalized()
    sun.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
    sun.data.energy = 4.0
    try: S.eevee.use_raytracing = True
    except Exception: pass

VARIANTS = []
def load_char():
    bpy.ops.import_scene.gltf(filepath=f"{A}/char/Superhero_Male_FullBody.gltf")
    arm = [o for o in bpy.context.selected_objects if o.type == "ARMATURE"][0]
    for o in bpy.context.selected_objects:
        if o.name.startswith(("Eyes", "Eyebrows", "Icosphere")):
            o.hide_render = True; o.hide_viewport = True
    base = bpy.data.materials["MI_Superhero_Male"]
    VARIANTS.clear()
    for tc, pc in (("#3d7bff", "#222831"), ("#f2f2f2", "#4a5a7a"), ("#ffd23d", "#2b2b2b"), ("#2fbf71", "#3b4f80"), ("#e94b8a", "#1f2a44"), ("#222222", "#c9b28f")):
        v = base.copy(); flat_clothes(v, tc, pc); VARIANTS.append(v)
    flat_clothes(base)
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=f"{A}/hair/Hair_SimpleParted.gltf")
    for o in set(bpy.data.objects) - before:
        if o.type == "MESH":
            mw = o.matrix_world.copy(); o.parent = arm; o.parent_type = "BONE"; o.parent_bone = "Head"
            bpy.context.view_layer.update(); o.matrix_world = mw
    # animation library
    before = set(bpy.data.objects); acts_before = set(bpy.data.actions)
    bpy.ops.import_scene.gltf(filepath=f"{A}/anim/UAL1_Standard.glb")
    for o in set(bpy.data.objects) - before: bpy.data.objects.remove(o, do_unlink=True)
    return arm

def pose(arm, action, frame):
    act = bpy.data.actions[action]
    ad = arm.animation_data or arm.animation_data_create()
    ad.action = act
    try: ad.action_slot = act.slots[0]
    except Exception: pass
    S.frame_set(frame); bpy.context.view_layer.update()

def capture(arm, action, frame):
    pose(arm, action, frame)
    return {pb.name: pb.matrix_basis.copy() for pb in arm.pose.bones}

R_ARM = ["clavicle_r", "upperarm_r", "lowerarm_r", "hand_r"] 
def pose_mix(arm, base, frame, over=None):
    """Body from `base`, selected bones from other actions: over = {(action, frame): [bones]}."""
    b = capture(arm, base, frame)
    for (act, f), bones in (over or {}).items():
        o = capture(arm, act, f)
        for n in bones:
            if n in o: b[n] = o[n]
    arm.animation_data.action = None
    for pb in arm.pose.bones:
        pb.matrix_basis = b[pb.name]
    bpy.context.view_layer.update()

def bone_world(arm, name):
    return arm.matrix_world @ arm.pose.bones[name].matrix

def eye_cam(arm, pitch=-25, fwd=0.05, lens=22):
    """Camera at the eyes, looking where the head looks, tilted down by pitch degrees."""
    bone = arm.data.bones["Head"]
    eye_rest = Vector((0, -0.07 - fwd, 1.70))
    off = bone.matrix_local.inverted() @ eye_rest
    hw = bone_world(arm, "Head")
    loc = hw @ off
    rot = hw.to_3x3() @ bone.matrix_local.to_3x3().inverted()
    f = (rot @ Vector((0, -1, 0))).normalized()
    f.z = 0; f.normalize()
    f = (f * math.cos(math.radians(pitch)) + Vector((0, 0, math.sin(math.radians(pitch))))).normalized()
    cam = S.camera; cam.location = loc
    cam.rotation_euler = f.to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = lens; cam.data.clip_start = 0.03

def drumstick(arm, hand="hand_r"):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.045, location=(0, 0, 0))
    meat = bpy.context.object; meat.scale = (1, 1, 1.5); meat.data.materials.append(M["chicken"]); smooth(meat, 1)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.011, depth=0.09, location=(0, 0, -0.1))
    bonep = bpy.context.object; bonep.data.materials.append(mat("bone", srgb("#f1e6cf"), 0.5)); bonep.parent = meat
    hw = bone_world(arm, hand)
    meat.parent = arm; meat.parent_type = "BONE"; meat.parent_bone = hand
    bpy.context.view_layer.update()
    meat.matrix_world = hw @ Matrix.Translation((0, 0.09, 0.02)) @ Matrix.Rotation(math.radians(70), 4, "X")
    return meat

def camp_chair(loc, rot=0):
    root = bpy.data.objects.new("chair", None); S.collection.objects.link(root); root.location = loc; root.rotation_euler[2] = rot
    cloth = mat("chaircloth", srgb("#1f5f4a"), 0.8); metal = mat("chairmetal", srgb("#222222"), 0.4, 0.8)
    box("seat", (0, 0, 0.45), (0.52, 0.48, 0.04), cloth, root, 0.01)
    box("back", (0, 0.27, 0.70), (0.52, 0.05, 0.55), cloth, root, 0.01)
    for sx in (-1, 1):
        for sy in (-1, 1):
            box("leg", (sx * 0.25, sy * 0.22, 0.2), (0.025, 0.025, 0.42), metal, root)
        box("armrest", (sx * 0.29, 0.0, 0.6), (0.05, 0.48, 0.03), metal, root)
    return root

def bake(arm, action, frame, over=None):
    """Freeze the posed body + hair into one static mesh (cheap to instance)."""
    pose_mix(arm, action, frame, over)
    dg = bpy.context.evaluated_depsgraph_get()
    import bmesh
    bm = bmesh.new()
    for o in arm.children_recursive:
        if o.type != "MESH" or o.hide_render: continue
        me = bpy.data.meshes.new_from_object(o.evaluated_get(dg), depsgraph=dg)
        me.transform(arm.matrix_world.inverted() @ o.matrix_world)
        tmp = bmesh.new(); tmp.from_mesh(me)
        # keep material index: body=0, hair=1
        for f in tmp.faces: f.material_index = 1 if "Hair" in o.name or "hair" in o.name.lower() else 0
        tmp.to_mesh(me); bm.from_mesh(me); tmp.free(); bpy.data.meshes.remove(me)
    out = bpy.data.meshes.new(f"bake_{action}_{frame}"); bm.to_mesh(out); bm.free()
    for p in out.polygons: p.use_smooth = True
    out.materials.append(VARIANTS[0]); out.materials.append(bpy.data.materials.get("MI_Hair_1") or M["hair"])
    return out

def place(me, loc, rot, k=1.0, var=None):
    o = bpy.data.objects.new("npc", me); S.collection.objects.link(o)
    o.location = loc; o.rotation_euler[2] = rot; o.scale = (k, k, k)
    o.material_slots[0].link = "OBJECT"; o.material_slots[0].material = var or random.choice(VARIANTS)
    return o

def dress_park(arm, Y0, k=1.0):
    # narrower bike path (dark) + concrete steps down to the water
    p = bpy.data.objects["path"]; p.scale[1] = 4.0; p.location[1] = 13.5
    p.data.materials[0] = mat("bike", srgb("#5b5f66"), 0.8)
    box("lane", (0, 13.5, 0.06), (60000, 0.12, 0.01), mat("lane", srgb("#f2d24b"), 0.5))
    box("walk", (0, 10.3, -0.44), (60000, 2.4, 1), M["concrete"])
    for i in range(4):
        box("step", (0, 16.0 + i * 0.9, -0.1 - i * 0.35), (60000, 0.9, 0.7), M["concrete"])
    # grass in world space
    gnt = M["grass"].node_tree; geo = gnt.nodes.new("ShaderNodeNewGeometry")
    gnt.links.new(geo.outputs["Position"], gnz.inputs["Vector"]); gnz.inputs["Scale"].default_value = 0.12
    # park lamps along the walk
    lampm = mat("lamp", srgb("#30343a"), 0.4, 0.7); bulb = mat("bulb", srgb("#fff2d0"), 0.3, emit=srgb("#ffd9a0"), emit_str=8)
    for x in range(-212, 200, 25):
        box("pole", (x, 9.0, 2.0), (0.12, 0.12, 4.0), lampm); box("head", (x, 9.0, 4.05), (0.5, 0.25, 0.12), bulb)
    # people: picnics on the grass, walkers and joggers on the walk
    hb = [b.replace("_r", "_l") for b in R_ARM]
    sit = bake(arm, "Sitting_Talking_Loop", 12); sit2 = bake(arm, "Sitting_Idle_Loop", 20)
    walk = bake(arm, "Walk_Loop", 8); walk2 = bake(arm, "Walk_Loop", 22); jog = bake(arm, "Jog_Fwd_Loop", 6)
    idle = bake(arm, "Idle_Talking_Loop", 10)
    random.seed(11)
    for _ in range(26):
        x = random.uniform(-90, 90); y = random.uniform(-14, 7)
        if abs(x) < 4 and abs(y - Y0) < 4: continue
        picnic((x, y, 0))
        for j in range(random.choice([1, 2, 2, 3])):
            a = random.uniform(0, 6.28)
            place(random.choice([sit, sit2]), (x + 0.9 * math.cos(a), y + 0.9 * math.sin(a), 0.0), a + math.pi / 2 + random.uniform(-.4, .4))
    for _ in range(30):
        x = random.uniform(-120, 120)
        if abs(x) < 3: continue
        d = random.choice([1, -1])
        place(random.choice([walk, walk2, walk, jog]), (x, 10.3 + random.uniform(-0.8, 0.8), 0.06), (0 if d > 0 else math.pi) + math.pi / 2)
    for _ in range(8):
        place(idle, (random.uniform(-80, 80), random.uniform(16, 17), 0.0), math.pi + random.uniform(-.5, .5))
    pose_mix(arm, "A_TPose", 1)

if __name__ == "__main__" or True:
    gnz.inputs["Scale"].default_value = 0.9; gnz.inputs["Detail"].default_value = 6
    gramp.color_ramp.elements[0].color = (*srgb("#3f6f2a"), 1); gramp.color_ramp.elements[1].color = (*srgb("#86ad52"), 1)
    build_world(detail=0.5)
    setup((0, -3, 1.6), (0, 0, 1), lens=22, sun_elev=7, sun_az=320)
    hdri_world()
    S.render.resolution_x = 1280; S.render.resolution_y = 720; S.render.resolution_percentage = pct
    arm = load_char()
    rig = bpy.data.objects.new("rig", None); S.collection.objects.link(rig)
    arm.parent = rig; rig.rotation_euler[2] = math.pi  # model faces -Y; turn to the river (+Y)
    Y0 = 3.0  # mat position on the grass, river beyond the path
    dress_park(arm, Y0)
    if shot in ("dbg_sit", "a_sit"):
        rig.location = (0, Y0, 0)
        hand_bones = [b.replace("_r", "_l") for b in R_ARM] + [pb.name for pb in arm.pose.bones if pb.name.endswith("_l") and any(k in pb.name for k in ("thumb", "index", "middle", "ring", "pinky"))]
        pose_mix(arm, "Sitting_Talking_Loop", 12, {("Idle_Torch_Loop", 10): hand_bones})
        pel = bone_world(arm, "pelvis").translation
        camp_chair((pel.x, pel.y, 0), rot=math.pi)
        picnic((0.0, Y0 + 1.1, 0))
    else:
        K = float(os.environ.get("POV_K", "8"))
        rig.location = (0, Y0 - 2.5, 0); rig.scale = (K, K, K)
        pose(arm, "Walk_Loop", 8)
        camp_chair((-0.7, Y0 + 1.6, 0), rot=math.pi + 0.3)
        picnic((0.7, Y0 + 2.4, 0))
    drumstick(arm, "hand_l")
    if shot.startswith("dbg"):
        c = S.camera; c.location = (2.2, Y0 + 3.2, 1.4); d = Vector((0, Y0, 0.8)) - c.location
        c.rotation_euler = d.to_track_quat("-Z", "Y").to_euler(); c.data.lens = 30
    elif shot == "a_sit":
        eye_cam(arm, pitch=-14, lens=16)
    elif shot == "b_look":
        eye_cam(arm, pitch=-62, lens=16)
    S.eevee.taa_render_samples = 16
    bpy.ops.render.render(write_still=True)
    print("WROTE", out)
