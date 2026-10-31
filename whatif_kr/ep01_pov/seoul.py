# 현실파괴범 EP01: low-poly Seoul seen from a 3.6 km giant (thumbnail + late-step shots).
# python3 seoul.py <shot> <out.png> [pct]
import os, sys
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "refstyle.py")).read().split("if __name__")[0])
import bmesh

KM = 1000.0
DENT = None
# Han River centreline through Seoul (km, x east / y north), roughly true to the map
HAN = [(-16, 7.5), (-12, 4.6), (-8.5, 2.2), (-5.5, 0.9), (-3.5, 0.4), (-1.5, -0.2), (0.5, -0.6), (2.5, -0.2),
       (4.2, 0.9), (5.8, 1.3), (7.5, 0.2), (9.2, -0.4), (11, 0.6), (13, 2.4), (16, 4.2)]
PEAKS = [(-1.0, 11.0, 1300, 2.4), (2.0, 14.5, 740, 2.0), (5.5, 13.0, 640, 1.8), (-2.2, 4.0, 338, 0.9), (-0.8, 4.9, 342, 0.8),
         (0.5, 2.5, 262, 0.7), (-2.0, -7.0, 632, 2.0), (3.0, -9.0, 618, 2.0), (9.0, 3.0, 296, 1.1), (5.0, -4.5, 306, 1.0),
         (-7.0, 9.0, 400, 1.6), (12, 9, 500, 2.0), (-9, -6, 450, 1.8), (13, -5, 480, 2.0)]

def river_dist(x, y):
    best = 1e9
    for (ax, ay), (bx, by) in zip(HAN, HAN[1:]):
        dx, dy = bx - ax, by - ay; t = max(0, min(1, ((x - ax) * dx + (y - ay) * dy) / (dx * dx + dy * dy)))
        best = min(best, math.hypot(x - ax - t * dx, y - ay - t * dy))
    return best

def height(x, y):  # km in, m out
    h = 0.0
    for px, py, ph, s in PEAKS:
        d = math.sqrt((x - px) ** 2 + (y - py) ** 2) / s
        h += ph * 2.4 * math.exp(-d * 2.2) * (1 + 0.25 * math.sin(7 * x + 3 * y) * math.cos(5 * y - 2 * x))
    return h

def terrain(half=30, cell=0.2, dent=None):
    me = bpy.data.meshes.new("terrain"); bm = bmesh.new()
    n = int(2 * half / cell) + 1; vs = []
    rnd = random.Random(5)
    for j in range(n):
        row = []
        for i in range(n):
            x = -half + i * cell; y = -half + j * cell
            h = height(x, y) + 8 + rnd.uniform(-4, 4)
            if river_dist(x, y) < 0.5: h = -70
            if dent:
                dd = math.hypot(x - dent[0], y - dent[1])
                if dd < 1.4: h = max(h - 160 * (1 - dd / 1.4) ** 1.5, -38)
            row.append(bm.verts.new((x * KM, y * KM, h)))
        vs.append(row)
    for j in range(n - 1):
        for i in range(n - 1):
            bm.faces.new((vs[j][i], vs[j][i + 1], vs[j + 1][i + 1], vs[j + 1][i]))
    bm.to_mesh(me); bm.free()
    mats = [mat("city", "#9aa27e", 0.95), mat("park", "#7f9a55", 0.95), mat("forest", "#55753f", 0.95), mat("rock", "#8a8d86", 0.95), mat("riverbed", "#c8b98f", 0.95), mat("snowtop", "#f2f4f7", 0.9), mat("dirtc", "#7a6650", 1.0)]
    for m in mats: me.materials.append(m)
    for p in me.polygons:
        c = p.center; x, y = c.x / KM, c.y / KM
        if DENT and math.hypot(x - DENT[0], y - DENT[1]) < 1.3: p.material_index = 6
        elif c.z > 1300: p.material_index = 5
        elif c.z > 700: p.material_index = 3
        elif c.z > 70: p.material_index = 2
        elif c.z < -50: p.material_index = 4
        elif river_dist(x, y) < 0.8: p.material_index = 1
        else: p.material_index = 0
    o = bpy.data.objects.new("terrain", me); S.collection.objects.link(o)
    return o

def water():
    plane("han", -30 * KM, 30 * KM, -30 * KM, 30 * KM, -45, mat("hanwater", "#3f78b5", 0.25))

def city(foot, radius_km=11, step=0.13):
    blds = [f"kenney_commercial/building-{c}.glb" for c in "abcdefghijklmn"] + [f"kenney_suburban/building-type-{c}.glb" for c in "abcdefghijklmnopqrstu"]
    tall = [f"kenney_commercial/building-skyscraper-{c}.glb" for c in "abcde"]
    trees = [f"nature/CommonTree_{i}.gltf" for i in range(1, 6)]
    rnd = random.Random(9); n = 0
    r = radius_km; y = -r
    while y < r:
        x = -r
        while x < r:
            px, py = x + rnd.uniform(-0.04, 0.04), y + rnd.uniform(-0.04, 0.04)
            x += step
            d = math.hypot(px - foot[0] / KM, py - foot[1] / KM)
            if d < 1.5 or d > r: continue
            h = height(px, py)
            if river_dist(px, py) < 0.75: continue
            if h > 150:
                if rnd.random() < 0.5: inst(rnd.choice(trees), (px * KM, py * KM, h), rnd.uniform(0, 6.28), rnd.uniform(9, 14))
                continue
            cell = (int(px / 1.3), int(py / 1.3)); dens = random.Random(hash(cell)).uniform(0.35, 1.0) if d > 4 else 1.0
            if rnd.random() > dens or rnd.random() < 0.15:
                inst(rnd.choice(trees), (px * KM, py * KM, h), rnd.uniform(0, 6.28), rnd.uniform(8, 12)); continue
            k = rnd.uniform(70, 110)
            ch = tall if (rnd.random() < 0.08 and d < 7) else blds
            inst(rnd.choice(ch), (px * KM, py * KM, h), rnd.choice([0, 1.57]), k * (1.4 if ch is tall else 1)); n += 1
        y += step
    return n

def bridges():
    m = mat("bridgeS", "#d8dbe0", 0.8)
    for bx in (-11, -8.6, -6.6, -4.6, -3.0, -1.6, -0.3, 1.0, 2.6, 3.8, 5.0, 6.4, 7.6, 8.8, 10.2, 11.8):
        # find river centre y at x
        ys = [ (ay + (by - ay) * (bx - ax) / (bx - ax2)) for (ax, ay), (ax2, by) in zip(HAN, HAN[1:]) if ax <= bx <= ax2]
        if not ys: continue
        box("br", (bx * KM, ys[0] * KM, 18), (40, 1500, 6), m)
    # Olympic-daero / Gangbyeon-buk along both banks
    rm = mat("exp", "#5a5e66", 0.9)
    for (ax, ay), (bx, by) in zip(HAN, HAN[1:]):
        L = math.hypot(bx - ax, by - ay) * KM; ang = math.atan2(by - ay, bx - ax)
        for off in (-0.62, 0.62):
            nx, ny = -math.sin(ang) * off, math.cos(ang) * off
            o = box("road", (((ax + bx) / 2 + nx) * KM, ((ay + by) / 2 + ny) * KM, 3), (L + 60, 45, 4), rm); o.rotation_euler[2] = ang

def lotte(x, y):
    bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=55, radius2=10, depth=555, location=(x, y, 277.5))
    lt = bpy.context.object; lt.rotation_euler[2] = math.radians(45); lt.data.materials.append(M["lotte"])

def clouds(n, center, avoid, seed=2, zr=(1600, 2600)):
    cm = bpy.data.materials.new("cloud"); cm.use_nodes = True; nt = cm.node_tree
    b = nt.nodes["Principled BSDF"]; b.inputs["Base Color"].default_value = (1, 1, 1, 1); b.inputs["Roughness"].default_value = 1
    b.inputs["Emission Color"].default_value = (0.85, 0.9, 1, 1); b.inputs["Emission Strength"].default_value = 0.35
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nz_ = nt.nodes.new("ShaderNodeTexNoise"); nz_.inputs["Scale"].default_value = 4.0; nz_.inputs["Detail"].default_value = 8
    gr = nt.nodes.new("ShaderNodeTexGradient"); gr.gradient_type = "SPHERICAL"
    mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Location"].default_value = (0.5, 0.5, 0)
    sub = nt.nodes.new("ShaderNodeVectorMath"); sub.operation = "SUBTRACT"; sub.inputs[1].default_value = (0.5, 0.5, 0)
    nt.links.new(tc.outputs["Generated"], sub.inputs[0]); nt.links.new(sub.outputs[0], gr.inputs[0])
    nt.links.new(tc.outputs["Object"], nz_.inputs["Vector"])
    mul = nt.nodes.new("ShaderNodeMath"); mul.operation = "MULTIPLY"
    nt.links.new(gr.outputs["Fac"], mul.inputs[0]); nt.links.new(nz_.outputs["Fac"], mul.inputs[1])
    rp = nt.nodes.new("ShaderNodeValToRGB"); rp.color_ramp.elements[0].position = 0.12; rp.color_ramp.elements[1].position = 0.42
    nt.links.new(mul.outputs[0], rp.inputs[0]); nt.links.new(rp.outputs[0], b.inputs["Alpha"])
    try: cm.surface_render_method = "BLENDED"
    except Exception: pass
    rnd = random.Random(seed)
    for _ in range(n):
        cx = center[0] + rnd.uniform(-20, 14) * KM; cy = center[1] + rnd.uniform(-16, 16) * KM
        if math.hypot(cx - avoid[0], cy - avoid[1]) < 7 * KM: continue
        for k in range(3):
            bpy.ops.mesh.primitive_plane_add(size=1, location=(cx + rnd.uniform(-300, 300), cy + rnd.uniform(-300, 300), rnd.uniform(*zr) + k * 60))
            o = bpy.context.object; r = rnd.uniform(1800, 4200); o.scale = (r * rnd.uniform(1, 1.6), r, 1)
            o.rotation_euler[2] = rnd.uniform(0, 3.14); o.data.materials.append(cm)

def crater(x, y, r=1050):
    # dark dented ground + radial cracks + dust ring
    dm = mat("dirt", "#6d5a45", 1.0)
    gz = height(x / KM, y / KM) + 8
    bowl(x, y, gz, r * 1.25)
    km = mat("crack", "#1a1410", 1.0); rnd = random.Random(4)
    for a in range(9):
        ang = a * 2 * math.pi / 9 + rnd.uniform(-.2, .2); px, py = x, y; L = 0
        for s in range(rnd.randint(6, 12)):
            seg = rnd.uniform(350, 800); ang += rnd.uniform(-.45, .45)
            nx, ny = px + math.cos(ang) * seg, py + math.sin(ang) * seg
            w = max(25, 110 - s * 9)
            c = box("crack", ((px + nx) / 2, (py + ny) / 2, height(nx / KM, ny / KM) + 28), (seg + w, w, 20), km)
            c.rotation_euler[2] = ang; px, py = nx, ny
    dust_puffs(x, y, gz, r)

def bowl(x, y, gz, R):
    rnd = random.Random(12); me = bpy.data.meshes.new("bowl"); bm = bmesh.new()
    rings, seg = 26, 72; vs = []
    for i in range(rings + 1):
        t = i / rings; row = []
        for j in range(seg):
            a = 2 * math.pi * j / seg; rr = R * t * (1 + rnd.uniform(-0.05, 0.05) * t)
            z = -70 * (1 - t * t) + 55 * math.exp(-((t - 0.9) / 0.09) ** 2) + rnd.uniform(-8, 8)
            if i == rings: z = -15
            row.append(bm.verts.new((x + rr * math.cos(a), y + rr * math.sin(a), gz + 25 + z)))
        vs.append(row)
    for i in range(rings):
        for j in range(seg):
            bm.faces.new((vs[i][j], vs[i][(j + 1) % seg], vs[i + 1][(j + 1) % seg], vs[i + 1][j]))
    bm.to_mesh(me); bm.free()
    m = bpy.data.materials.new("craterm"); m.use_nodes = True; nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord"); nzc = nt.nodes.new("ShaderNodeTexNoise"); nzc.inputs["Scale"].default_value = 6
    rp = nt.nodes.new("ShaderNodeValToRGB"); rp.color_ramp.elements[0].color = (*srgb("#5b4a3a"), 1); rp.color_ramp.elements[1].color = (*srgb("#a48f72"), 1)
    nt.links.new(tc.outputs["Generated"], nzc.inputs["Vector"]); nt.links.new(nzc.outputs["Fac"], rp.inputs[0]); nt.links.new(rp.outputs[0], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 1
    me.materials.append(m)
    o = bpy.data.objects.new("bowl", me); S.collection.objects.link(o)

def dust_puffs(x, y, gz, r):
    cm = bpy.data.materials["cloud"].copy(); cm.name = "dust"
    b = cm.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*srgb("#d9c7a8"), 1); b.inputs["Emission Color"].default_value = (*srgb("#cdb894"), 1)
    rp = [n for n in cm.node_tree.nodes if n.type == "VALTORGB"][0]; rp.color_ramp.elements[0].position = 0.06; rp.color_ramp.elements[1].position = 0.3
    rnd = random.Random(8)
    for k in range(30):
        a = rnd.uniform(0, 6.28); d = r * rnd.uniform(1.0, 1.6)
        bpy.ops.mesh.primitive_plane_add(size=1, location=(x + math.cos(a) * d, y + math.sin(a) * d, gz + rnd.uniform(40, 260)))
        o = bpy.context.object; s_ = rnd.uniform(600, 1100); o.scale = (s_ * 1.4, s_, 1); o.rotation_euler[2] = a
        o.data.materials.append(cm)

if __name__ == "__main__":
    lighting(sun_elev=34, sun_az=-55)
    S.world.node_tree.nodes["Background"].inputs[1].default_value = 0.45
    K = float(os.environ.get("K", "5000"))
    FOOT = (8.1 * KM, -1.6 * KM)  # just south of the river at Jamsil, next to Lotte World Tower
    rig, arm = load_char()
    armb = [b.name for b in arm.pose.bones if any(k in b.name for k in ("clavicle", "upperarm", "lowerarm", "hand", "thumb", "index", "middle", "ring", "pinky"))]
    pose_mix(arm, "Idle_Loop", 10, {("A_TPose", 1): armb})
    from mathutils import Matrix as _M
    pb = arm.pose.bones["thigh_r"]; pb.matrix_basis = pb.matrix_basis @ _M.Rotation(math.radians(float(os.environ.get("LUNGE", "-38"))), 4, "X")
    rig.rotation_euler[2] = float(os.environ.get("FACE", str(-math.pi / 2)))  # face west, along the river toward downtown
    rig.scale = (K, K, K)
    bpy.context.view_layer.update()
    fr = bone_world(arm, "foot_r").translation
    rig.location = (FOOT[0] - fr.x, FOOT[1] - fr.y, height(FOOT[0] / KM, FOOT[1] / KM) + 8 - (fr.z - 0.07 * K))
    bpy.context.view_layer.update()
    DENT = (FOOT[0] / KM, FOOT[1] / KM); terrain(dent=DENT); water(); bridges()
    lotte(8.9 * KM, -1.0 * KM)
    print("buildings", city(FOOT, radius_km=16, step=0.19))
    clouds(60, FOOT, (FOOT[0] - 5 * KM, FOOT[1]))
    crater(FOOT[0], FOOT[1])
    if os.environ.get("ENGINE", "CYCLES") == "CYCLES":
        S.render.engine = "CYCLES"; S.cycles.samples = int(os.environ.get("SPP", "48")); S.cycles.use_denoising = True
        S.cycles.max_bounces = 4; S.cycles.device = "CPU"
    cam = camera(); cam.data.clip_start = 20; cam.data.clip_end = 200000
    if shot == "thumb":
        eye_cam(cam, arm, pitch=float(os.environ.get("PITCH", "-50")), lens=float(os.environ.get("LENS", "15")))
    elif shot == "wide":
        eye_cam(cam, arm, pitch=-28, lens=17)
    bpy.ops.render.render(write_still=True)
    print("WROTE", out)
