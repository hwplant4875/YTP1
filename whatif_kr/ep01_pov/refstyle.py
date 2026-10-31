# 현실파괴범 EP01: AFTER THE DOOR look (Kenney + Quaternius CC0, Superhero_Male, daylight Eevee).
# python3 refstyle.py <shot> <out.png> [pct]
import bpy, math, os, sys, random
from mathutils import Vector, Matrix

A = os.environ.get("WHATIF_ASSETS", "/mnt/project-files/whatif_kr/assets")
shot = sys.argv[1] if len(sys.argv) > 1 else "s1"
out = sys.argv[2] if len(sys.argv) > 2 else "/tmp/s1.png"
pct = int(sys.argv[3]) if len(sys.argv) > 3 else 50
bpy.ops.wm.read_factory_settings(use_empty=True)
S = bpy.context.scene
random.seed(3)

def srgb(h):
    h = h.lstrip("#"); c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92 for x in c)

def mat(name, hexc, rough=0.8, metal=0.0, emit=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*srgb(hexc), 1)
    b.inputs["Roughness"].default_value = rough; b.inputs["Metallic"].default_value = metal
    if emit:
        b.inputs["Emission Color"].default_value = (*srgb(hexc), 1); b.inputs["Emission Strength"].default_value = emit
    return m

def plane(name, x0, x1, y0, y1, z, m):
    me = bpy.data.meshes.new(name)
    me.from_pydata([(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z)], [], [(0, 1, 2, 3)])
    me.materials.append(m); o = bpy.data.objects.new(name, me); S.collection.objects.link(o); return o

def box(name, loc, size, m):
    import bmesh
    me = bpy.data.meshes.new(name); bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0); bm.to_mesh(me); bm.free()
    me.materials.append(m); o = bpy.data.objects.new(name, me); S.collection.objects.link(o)
    o.location = loc; o.scale = size; return o

# ---------- asset library: import once into a hidden collection, then instance ----------
LIB = bpy.data.collections.new("LIB")  # not linked to the scene: only instanced
_lib = {}
def asset(rel):
    if rel in _lib: return _lib[rel]
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=f"{A}/{rel}")
    new = set(bpy.data.objects) - before
    c = bpy.data.collections.new(rel)
    for o in new:
        for uc in list(o.users_collection): uc.objects.unlink(o)
        c.objects.link(o)
    _lib[rel] = c
    return c

def inst(rel, loc, rot=0.0, k=1.0):
    e = bpy.data.objects.new("i", None); S.collection.objects.link(e)
    e.instance_type = "COLLECTION"; e.instance_collection = asset(rel)
    e.location = loc; e.rotation_euler[2] = rot; e.scale = (k, k, k)
    return e

# ---------- palette sampled from the reference frames ----------
M = {
    "grass": mat("grass", "#8f9a5e", 0.95),
    "walk": mat("walk", "#c9ced4", 0.85),
    "bike": mat("bike", "#4d525c", 0.85),
    "line": mat("line", "#f1f1f1", 0.8),
    "bank": mat("bank", "#c9ccd1", 0.9),
    "water": mat("water", "#3a6fb0", 0.95),
    "road": mat("road", "#454a54", 0.9),
    "mountain": mat("mountain", "#7d8fa6", 0.95),
    "snow": mat("snow", "#eef2f6", 0.9),
    "matA": mat("matA", "#3b6fd1", 0.8), "matB": mat("matB", "#f3f3f3", 0.8),
    "box": mat("box", "#f3b33a", 0.7), "boxR": mat("boxR", "#d9432f", 0.7),
    "can": mat("can", "#c9d0d8", 0.35, 0.8), "canG": mat("canG", "#2f7d4f", 0.4, 0.5),
    "lotte": mat("lotte", "#dfe6ee", 0.25, 0.4),
    "bridge": mat("bridge", "#b6bcc6", 0.8),
}
try: M["water"].node_tree.nodes["Principled BSDF"].inputs["Specular IOR Level"].default_value = 0.1
except Exception: pass
# subtle large-scale grass variation (world space)
nt = M["grass"].node_tree; geo = nt.nodes.new("ShaderNodeNewGeometry")
nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 0.03
ramp = nt.nodes.new("ShaderNodeValToRGB")
ramp.color_ramp.elements[0].color = (*srgb("#66733f"), 1); ramp.color_ramp.elements[1].color = (*srgb("#7a8749"), 1)
nt.links.new(geo.outputs["Position"], nz.inputs["Vector"]); nt.links.new(nz.outputs["Fac"], ramp.inputs[0])
nt.links.new(ramp.outputs[0], nt.nodes["Principled BSDF"].inputs["Base Color"])

def lowpoly_mountain(loc, r, h, seed):
    import bmesh
    rnd = random.Random(seed)
    me = bpy.data.meshes.new("mtn"); bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=False, segments=9, radius1=r, radius2=0, depth=h)
    bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=2, use_grid_fill=True)
    for v in bm.verts:
        if v.co.z > -h / 2 + 1:
            v.co.x += rnd.uniform(-.12, .12) * r; v.co.y += rnd.uniform(-.12, .12) * r; v.co.z += rnd.uniform(-.06, .06) * h
    bm.to_mesh(me); bm.free()
    me.materials.append(M["mountain"]); me.materials.append(M["snow"])
    for p in me.polygons:
        p.use_smooth = False
        p.material_index = 1 if p.center.z > h * 0.22 else 0
    o = bpy.data.objects.new("mtn", me); S.collection.objects.link(o); o.location = (loc[0], loc[1], h / 2 - 5)
    return o

def picnic(x, y):
    for i in range(6):
        for j in range(6):
            box("mat", (x - 0.75 + i * 0.3 + 0.15, y - 0.75 + j * 0.3 + 0.15, 0.006), (0.3, 0.3, 0.012), M["matA"] if (i + j) % 2 else M["matB"])
    box("chickenbox", (x + 0.25, y + 0.1, 0.06), (0.36, 0.3, 0.1), M["box"])
    box("lid", (x + 0.25, y + 0.42, 0.012), (0.36, 0.28, 0.02), M["boxR"])
    for k, (dx, dy) in enumerate([(-0.35, 0.3), (-0.25, 0.42), (-0.45, -0.1)]):
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.033, depth=0.12, location=(x + dx, y + dy, 0.06))
        bpy.context.object.data.materials.append(M["canG"] if k == 1 else M["can"])

def build_world():
    plane("grass", -6000, 6000, -6000, 24, 0, M["grass"])
    plane("walk", -6000, 6000, 12, 15, 0.02, M["walk"])
    plane("bike", -6000, 6000, 16, 20, 0.02, M["bike"])
    for x in range(-600, 600, 6):
        plane("dash", x, x + 3, 17.93, 18.07, 0.025, M["line"])
    # stepped concrete bank down to the water
    for i in range(4):
        box("step", (0, 20.4 + i * 0.6, -0.15 - i * 0.22), (12000, 0.6, 0.3), M["bank"])
    plane("water", -6000, 6000, 20, 1050, -0.9, M["water"])
    plane("southbank", -6000, 6000, 1050, 9000, 0.0, M["grass"])
    plane("southroad", -6000, 6000, 1070, 1090, 0.03, M["road"])
    # Olympic-ro behind the park + cars
    plane("road", -6000, 6000, -48, -30, 0.02, M["road"])
    cars = ["sedan", "suv", "taxi", "hatchback-sports", "van", "delivery", "suv-luxury", "police"]
    for x in range(-400, 400, 22):
        lane = random.choice([-44, -40, -37, -33])
        inst(f"kenney_car/{random.choice(cars)}.glb", (x + random.uniform(-6, 6), lane, 0), math.pi / 2 if lane > -39 else -math.pi / 2, 1.8)
    # riverside apartments north (Kenney commercial scaled up)
    blds = [f"building-{c}" for c in "abcdefghijklmn"]
    for x in range(-1500, 1500, 34):
        for row, y in enumerate((-80, -125, -170)):
            inst(f"kenney_commercial/{random.choice(blds)}.glb", (x + random.uniform(-4, 4), y - random.uniform(0, 10), 0), random.choice([0, math.pi]), random.uniform(22, 34))
    # south skyline across the river
    sky = [f"building-skyscraper-{c}" for c in "abcde"]
    for x in range(-3000, 3000, 55):
        for y in range(1110, 2400, 90):
            if random.random() < 0.3: continue
            if random.random() < 0.35:
                inst(f"kenney_commercial/{random.choice(sky)}.glb", (x + random.uniform(-15, 15), y, 0), random.choice([0, 1.57]), random.uniform(28, 45))
            else:
                inst(f"kenney_commercial/{random.choice(blds)}.glb", (x + random.uniform(-15, 15), y, 0), random.choice([0, 1.57]), random.uniform(25, 40))
    # Lotte World Tower (555 m), tapered low-poly
    bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=50, radius2=9, depth=555, location=(700, 1500, 277.5))
    lt = bpy.context.object; lt.rotation_euler[2] = math.radians(45); lt.data.materials.append(M["lotte"])
    # girder bridge
    box("deck", (-420, 535, 14), (26, 1060, 2.4), M["bridge"])
    for py in range(60, 1040, 90): box("pier", (-420, py, 5), (8, 4, 14), M["bridge"])
    # mountains: Bukhansan (north) and Gwanaksan (south)
    for i in range(12):
        lowpoly_mountain((-9000 + i * 1600, -7000 - (i % 3) * 900), 1400 + (i % 4) * 300, 700 + (i % 3) * 250, i)
        lowpoly_mountain((-9000 + i * 1600 + 600, 9000 + (i % 3) * 900), 1500 + (i % 4) * 300, 600 + (i % 2) * 300, 100 + i)
    # park trees + grass tufts + bushes
    trees = [f"nature/CommonTree_{i}.gltf" for i in range(1, 6)]
    for x in range(-500, 500, 14):
        for y in (-22, -12, 6):
            p = (x + random.uniform(-5, 5), y + random.uniform(-4, 4), 0)
            if math.hypot(p[0], p[1]) < 14: continue
            inst(random.choice(trees), p, random.uniform(0, 6.28), random.uniform(0.9, 1.3))
    tufts = ["nature/Grass_Common_Short.gltf", "nature/Grass_Wispy_Short.gltf", "nature/Grass_Common_Tall.gltf"]
    for _ in range(5200):
        r = 60 * math.sqrt(random.random()); a = random.uniform(0, 6.28)
        x, y = r * math.cos(a), r * math.sin(a) * 0.5 - 6
        if 11.5 < y or (abs(x) < 1.2 and abs(y - 1.0) < 1.2): continue
        inst(random.choice(tufts), (x, y, 0), random.uniform(0, 6.28), random.uniform(0.18, 0.3))
    for _ in range(40):
        inst(random.choice(["nature/Bush_Common.gltf", "nature/Bush_Common_Flowers.gltf"]), (random.uniform(-200, 200), random.uniform(-27, 9), 0), random.uniform(0, 6.28), random.uniform(0.8, 1.2))

def sky_clouds(n=40, seed=6):
    cm = bpy.data.materials.new("skycloud"); cm.use_nodes = True; nt = cm.node_tree
    b = nt.nodes["Principled BSDF"]; b.inputs["Base Color"].default_value = (1, 1, 1, 1); b.inputs["Roughness"].default_value = 1
    b.inputs["Emission Color"].default_value = (1, 1, 1, 1); b.inputs["Emission Strength"].default_value = 0.6
    tc = nt.nodes.new("ShaderNodeTexCoord"); nzc = nt.nodes.new("ShaderNodeTexNoise"); nzc.inputs["Scale"].default_value = 3.5; nzc.inputs["Detail"].default_value = 8
    gr = nt.nodes.new("ShaderNodeTexGradient"); gr.gradient_type = "SPHERICAL"
    sub = nt.nodes.new("ShaderNodeVectorMath"); sub.operation = "SUBTRACT"; sub.inputs[1].default_value = (0.5, 0.5, 0)
    nt.links.new(tc.outputs["Generated"], sub.inputs[0]); nt.links.new(sub.outputs[0], gr.inputs[0]); nt.links.new(tc.outputs["Object"], nzc.inputs["Vector"])
    mul = nt.nodes.new("ShaderNodeMath"); mul.operation = "MULTIPLY"; nt.links.new(gr.outputs["Fac"], mul.inputs[0]); nt.links.new(nzc.outputs["Fac"], mul.inputs[1])
    rp = nt.nodes.new("ShaderNodeValToRGB"); rp.color_ramp.elements[0].position = 0.1; rp.color_ramp.elements[1].position = 0.35
    nt.links.new(mul.outputs[0], rp.inputs[0]); nt.links.new(rp.outputs[0], b.inputs["Alpha"])
    rnd = random.Random(seed)
    for _ in range(n):
        x = rnd.uniform(-9000, 9000); y = rnd.uniform(1500, 14000); z = rnd.uniform(1400, 2600)
        bpy.ops.mesh.primitive_plane_add(size=1, location=(x, y, z)); o = bpy.context.object
        r = rnd.uniform(1200, 3000); o.scale = (r * 1.6, r, 1); o.data.materials.append(cm)

def lighting(sun_elev=38, sun_az=-35, strength=1.0):
    w = bpy.data.worlds.new("w"); S.world = w; w.use_nodes = True; wn = w.node_tree
    skyn = wn.nodes.new("ShaderNodeTexSky")
    try: skyn.sky_type = "MULTIPLE_SCATTERING"
    except Exception: pass
    # sun direction: az measured from +Y (camera forward) toward +X
    az = math.radians(sun_az); el = math.radians(sun_elev)
    d = Vector((math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el)))
    skyn.sun_elevation = el; skyn.sun_rotation = math.atan2(d.y, d.x) - math.pi / 2
    try: skyn.sun_disc = False
    except Exception: pass
    wn.links.new(skyn.outputs[0], wn.nodes["Background"].inputs[0]); wn.nodes["Background"].inputs[1].default_value = 0.35 * strength
    sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN")); S.collection.objects.link(sun)
    sun.data.energy = 4.2 * strength; sun.data.color = srgb("#fff1dc"); sun.data.angle = math.radians(0.6)
    sun.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
    S.render.engine = "BLENDER_EEVEE"
    S.eevee.taa_render_samples = 24
    try: S.eevee.use_shadows = True; S.eevee.shadow_ray_count = 2; S.eevee.shadow_step_count = 8
    except Exception: pass
    S.view_settings.view_transform = "AgX"; S.view_settings.look = "AgX - Base Contrast" if "AgX - Base Contrast" in [l for l in ("AgX - Base Contrast",)] else "None"
    try: S.view_settings.look = os.environ.get("LOOK", "AgX - Medium High Contrast")
    except Exception: pass
    if os.environ.get("ENGINE", "CYCLES") == "CYCLES":
        S.render.engine = "CYCLES"; S.cycles.samples = int(os.environ.get("SPP", "32")); S.cycles.use_denoising = True; S.cycles.max_bounces = 4
    S.render.resolution_x = 1920; S.render.resolution_y = 1080; S.render.resolution_percentage = pct
    S.render.filepath = out

# ---------- character ----------
def load_char():
    bpy.ops.import_scene.gltf(filepath=f"{A}/char/Superhero_Male_FullBody.gltf")
    arm = [o for o in bpy.context.selected_objects if o.type == "ARMATURE"][0]
    for o in bpy.context.selected_objects:
        if o.name.startswith("Icosphere"): o.hide_render = True
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=f"{A}/anim/UAL1_Standard.glb")
    for o in set(bpy.data.objects) - before: bpy.data.objects.remove(o, do_unlink=True)
    rig = bpy.data.objects.new("rig", None); S.collection.objects.link(rig)
    arm.parent = rig; rig.rotation_euler[2] = math.pi  # model faces -Y; turn to +Y (river)
    return rig, arm

def capture(arm, action, frame):
    act = bpy.data.actions[action]; ad = arm.animation_data or arm.animation_data_create()
    ad.action = act
    try: ad.action_slot = act.slots[0]
    except Exception: pass
    S.frame_set(frame); bpy.context.view_layer.update()
    return {pb.name: pb.matrix_basis.copy() for pb in arm.pose.bones}

def pose_mix(arm, base, frame, over=None):
    b = capture(arm, base, frame)
    for (act, f), bones in (over or {}).items():
        o = capture(arm, act, f)
        for n in bones: b[n] = o[n]
    arm.animation_data.action = None
    for pb in arm.pose.bones: pb.matrix_basis = b[pb.name]
    bpy.context.view_layer.update()

def bone_world(arm, name): return arm.matrix_world @ arm.pose.bones[name].matrix

def eye_cam(cam, arm, pitch=-15, lens=20, fwd=0.07):
    bone = arm.data.bones["Head"]
    off = bone.matrix_local.inverted() @ Vector((0, -0.07 - fwd, 1.70))
    hw = bone_world(arm, "Head"); loc = hw @ off
    rot = hw.to_3x3() @ bone.matrix_local.to_3x3().inverted()
    f = (rot @ Vector((0, -1, 0))); f.z = 0; f.normalize()
    f = (f * math.cos(math.radians(pitch)) + Vector((0, 0, math.sin(math.radians(pitch))))).normalized()
    cam.location = loc; cam.rotation_euler = f.to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = lens

def camera(loc=(0, -5, 2), look=(0, 0, 1), lens=24):
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); S.collection.objects.link(cam)
    cam.location = loc; cam.rotation_euler = (Vector(look) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = lens; cam.data.clip_start = 0.02; cam.data.clip_end = 60000; S.camera = cam
    return cam

if __name__ == "__main__":
    lighting()
    build_world()
    picnic(0.0, 1.0)
    sky_clouds()
    rig, arm = load_char()
    cam = camera()
    if shot == "s1":      # just stood up from the mat, looking at the river
        rig.location = (0, -0.6, 0)
        pose_mix(arm, "Idle_Loop", 10)
        eye_cam(cam, arm, pitch=-14, lens=20)
    elif shot == "s2":    # step 3: 14 m, looking down at the mat and the walkway
        K = 8; rig.location = (1.5, 4.0, 0); rig.scale = (K, K, K)
        pose_mix(arm, "Walk_Loop", 8)
        eye_cam(cam, arm, pitch=-50, lens=20)
    elif shot == "s3":    # 3rd person: ~110 m giant on the park, seen from the walkway
        K = 62; rig.location = (40, -60, 0); rig.scale = (K, K, K); rig.rotation_euler[2] = math.pi + 0.5
        pose_mix(arm, "Walk_Loop", 14)
        cam.location = (-60, 16, 1.7); look = Vector((40, -60, 70))
        cam.rotation_euler = (look - cam.location).to_track_quat("-Z", "Y").to_euler(); cam.data.lens = 18
    bpy.ops.render.render(write_still=True)
    print("WROTE", out)
