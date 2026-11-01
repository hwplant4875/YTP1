# EP01 final: animated step shots. One shot = one step: leg swings forward while the body doubles, foot lands, hold.
# python3 shot.py <shot> <outdir> [pct]      env: SPP (swing frames), SPP_HOLD (last frame), NF (swing frames), ONLY=last|<i>
# Writes <outdir>/<shot>_000.png ... <shot>_NNN.png ; the last one is the hold frame (rendered at 100% / SPP_HOLD).
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
POV = os.path.join(HERE, "..", "ep01_pov")
if "--" in sys.argv: sys.argv = [sys.argv[0]] + sys.argv[sys.argv.index("--") + 1:]
shot = sys.argv[1]; outdir = sys.argv[2]; PCT = int(sys.argv[3]) if len(sys.argv) > 3 else 50
os.makedirs(outdir, exist_ok=True)
sys.argv = ["x", shot, os.path.join(outdir, "tmp.png"), str(PCT)]
KIND = "seoul" if shot.startswith("k") else ("earth" if shot.startswith("e") and shot != "end" else "park")
if KIND == "seoul":
    exec(open(os.path.join(POV, "seoul.py")).read().replace("os.path.dirname(os.path.abspath(__file__))", repr(POV)).split("\nif __name__")[0])
else:
    exec(open(os.path.join(POV, "refstyle.py")).read().split("\nif __name__")[0])
if KIND == "earth":
    exec(open(os.path.join(HERE, "earth.py")).read())

NF = int(os.environ.get("NF", "18"))
SPP = int(os.environ.get("SPP", "16")); SPP_HOLD = int(os.environ.get("SPP_HOLD", "48"))
ONLY = os.environ.get("ONLY", "")

def gpu():
    if os.environ.get("GPU", "0") != "1": return
    pr = bpy.context.preferences.addons["cycles"].preferences
    pr.compute_device_type = os.environ.get("GPU_TYPE", "CUDA"); pr.get_devices()
    for d in pr.devices: d.use = d.type != "CPU"
    S.cycles.device = "GPU"; print("GPU devices", [d.name for d in pr.devices if d.use], flush=True)

def ease(t): return t * t * (3 - 2 * t)

def swing_frames(leg):
    return (2, 16) if leg == "r" else (18, 32)

ARMB = None
def set_pose(arm, af, arms_out=True):
    global ARMB
    if ARMB is None:
        ARMB = [b.name for b in arm.pose.bones if any(k in b.name for k in ("clavicle", "upperarm", "lowerarm", "hand", "thumb", "index", "middle", "ring", "pinky"))]
    pose_mix(arm, "Walk_Loop", af % 32)

def stance_local(rig, arm, leg):
    """stance foot position relative to rig origin, for scale 1 (rig rotation applied)."""
    sl, ss = rig.location.copy(), rig.scale.copy()
    rig.location = (0, 0, 0); rig.scale = (1, 1, 1); bpy.context.view_layer.update()
    p = bone_world(arm, "foot_l" if leg == "r" else "foot_r").translation.copy()
    rig.location = sl; rig.scale = ss; bpy.context.view_layer.update()
    return p

class Step:
    """Animate one step. anchor = world position of the stance foot; land = world xy where the swing foot ends (optional)."""
    def __init__(self, rig, arm, K0, K1, leg, anchor=None, land=None, ground=0.0):
        self.rig, self.arm, self.K0, self.K1, self.leg = rig, arm, K0, K1, leg
        a0, a1 = swing_frames(leg); self.a0, self.a1 = a0, a1
        if anchor is None:   # derive the stance anchor from where the swing foot must land
            set_pose(arm, a1); sl = stance_local(rig, arm, leg)
            rig.location = (0, 0, 0); rig.scale = (1, 1, 1); bpy.context.view_layer.update()
            sw = bone_world(arm, "foot_r" if leg == "r" else "foot_l").translation.copy()
            off = (sw - sl) * K1
            anchor = Vector((land[0] - off.x, land[1] - off.y, ground))
        self.anchor = Vector(anchor)
    def apply(self, t):
        t = max(0.0, min(1.0, t)); e = ease(t)
        af = self.a0 + (self.a1 - self.a0) * e
        set_pose(self.arm, int(round(af)))
        K = self.K0 * (self.K1 / self.K0) ** e
        sl = stance_local(self.rig, self.arm, self.leg)
        self.rig.scale = (K, K, K)
        self.rig.location = (self.anchor.x - sl.x * K, self.anchor.y - sl.y * K, self.anchor.z)
        bpy.context.view_layer.update()
        return K

def render_seq(step, camfn, nf=NF, before_last=None):
    frames = list(range(nf + 1))
    if ONLY == "last": frames = [nf]
    elif ONLY: frames = [int(x) for x in ONLY.split(",")]
    gpu()
    for i in frames:
        t = i / nf
        K = step.apply(t) if step else None
        if i == nf and before_last: before_last()
        camfn(i, t)
        hold = i == nf
        S.render.resolution_percentage = int(os.environ.get("HOLDPCT", "100")) if hold else PCT
        if S.render.engine == "CYCLES": S.cycles.samples = SPP_HOLD if hold else SPP
        S.render.filepath = os.path.join(outdir, f"{shot}_{i:03d}.png")
        if os.environ.get("RESUME") == "1" and os.path.exists(S.render.filepath): continue
        bpy.ops.render.render(write_still=True)
        print("FRAME", shot, i, flush=True)

def eye(cam, arm, pitch, lens, yaw):
    return lambda i, t: eye_cam(cam, arm, pitch=pitch, lens=lens, yaw=yaw)

# ---------------------------------------------------------------- park (steps 0-9)
def extend_city():
    blds = [f"building-{c}" for c in "abcdefghijklmn"]
    sky = [f"building-skyscraper-{c}" for c in "abcde"]
    rnd = random.Random(8)
    for x in range(-7000, 2500, 70):
        for y in range(-220, -3200, -75):
            if rnd.random() < 0.25: continue
            inst(f"kenney_commercial/{rnd.choice(blds)}.glb", (x + rnd.uniform(-12, 12), y + rnd.uniform(-12, 12), 0), rnd.choice([0, 1.57]), rnd.uniform(22, 34))
    for x in range(-8000, -3000, 70):
        for y in range(1110, 3000, 90):
            if rnd.random() < 0.35: continue
            r = rnd.choice(sky if rnd.random() < 0.3 else blds)
            inst(f"kenney_commercial/{r}.glb", (x + rnd.uniform(-15, 15), y, 0), rnd.choice([0, 1.57]), rnd.uniform(25, 40))
    plane("farN", -40000, 40000, -40000, -6000, 0, M["grass"]); plane("farW", -40000, -6000, -6000, 24, 0, M["grass"])
    plane("farS", -40000, 40000, 9000, 40000, 0, M["grass"]); plane("farWW", -40000, -6000, 20, 1050, -0.9, M["water"])
    plane("farSW", -40000, -6000, 1050, 9000, 0, M["grass"])
    for i in range(10):
        lowpoly_mountain((-30000 + i * 2600, -16000 - (i % 3) * 1500), 2600 + (i % 4) * 400, 900 + (i % 3) * 300, 300 + i)
        lowpoly_mountain((-30000 + i * 2600, 17000 + (i % 3) * 1500), 2600 + (i % 4) * 400, 800 + (i % 2) * 300, 400 + i)

PARK = {  # shot: (K1, leg, pitch, lens, yaw)
    "w2": (2, "r", -66, 13, -6), "w4": (4, "l", -65, 14, 6), "w8": (8, "r", -66, 14, -6), "w16": (16, "l", -64, 14, 6),
    "w32": (32, "r", -62, 15, -6), "w128": (128, "r", -52, 15, -8), "w256": (256, "l", -48, 15, 6),
}

def park():
    lighting(); build_world(); picnic(0.0, 1.0); sky_clouds()
    rig, arm = load_char()
    if os.environ.get("CROWD", "1") == "1": crowd(arm)
    cam = camera()
    if shot in ("s1", "end"):
        rig.location = (0, -0.6, 0); pose_mix(arm, "Idle_Loop", 10)
        gpu(); S.render.resolution_percentage = 100; S.cycles.samples = SPP_HOLD
        eye_cam(cam, arm, pitch=-14, lens=20); S.render.filepath = os.path.join(outdir, f"{shot}_000.png")
        bpy.ops.render.render(write_still=True); return
    if shot in PARK:
        K1, leg, pitch, lens, yaw = PARK[shot]
        if K1 >= 128: extend_city()
        rig.rotation_euler[2] = -math.pi / 2
        st = Step(rig, arm, K1 / 2, K1, leg, land=(-2.0 * K1 - 0.3 * K1, 4.0 + (0.12 if leg == "r" else -0.12) * K1))
        render_seq(st, eye(cam, arm, pitch, lens, yaw)); return
    if shot == "s3":   # 3rd person from the walkway: a 112 m giant steps onto the park
        rig.rotation_euler[2] = math.pi + 0.5
        st = Step(rig, arm, 32, 64, "r", land=(6, -16))
        cam.location = (-46, 13.5, 1.7); look = Vector((6, -18, 52))
        cam.rotation_euler = (look - cam.location).to_track_quat("-Z", "Y").to_euler(); cam.data.lens = 18
        render_seq(st, lambda i, t: None); return
    if shot == "s_step9":   # 896 m: Lotte World Tower below the waist
        extend_city()
        st = Step(rig, arm, 256, 512, "r", land=(60, 420))
        render_seq(st, eye(cam, arm, -42, 18, -25)); return
    raise SystemExit("unknown park shot " + shot)

# ---------------------------------------------------------------- Seoul (steps 10-14)
SEOUL = {  # shot: (K1, leg, pitch, lens, yaw)
    "k1024": (1024, "r", -40, 16, -10), "k2048": (2048, "l", -48, 15, 8), "k4096": (4096, "r", -54, 15, -4),
    "k8192": (8192, "r", -60, 14, 12), "k16384": (16384, "l", -62, 14, 6),
}

def seoul_shot():
    K1, leg, pitch, lens, yaw = SEOUL[shot]
    global FOOT
    FOOT = (8.1 * KM, -1.6 * KM)
    lighting(sun_elev=34, sun_az=-55); S.world.node_tree.nodes["Background"].inputs[1].default_value = 0.45
    rig, arm = load_char(); rig.rotation_euler[2] = -math.pi / 2
    gz = height(FOOT[0] / KM, FOOT[1] / KM)
    st = Step(rig, arm, K1 / 2, K1, leg, land=FOOT, ground=gz + 8)
    st.apply(1.0)
    # two terrains: flat before the impact, dented (crater) on the landing frame
    t0 = set(bpy.data.objects); terrain(); flat = set(bpy.data.objects) - t0
    global DENT, DENT_R
    DENT = (FOOT[0] / KM, FOOT[1] / KM); DENT_R = max(0.25, 1.4 * K1 / 5000)
    t1 = set(bpy.data.objects); terrain(dent=DENT); dented = set(bpy.data.objects) - t1
    water(); bridges(); lotte(8.9 * KM, -1.0 * KM)
    city(FOOT, radius_km=16, step=0.19)
    clouds(60, FOOT, (FOOT[0] - 5 * KM, FOOT[1]))
    t2 = set(bpy.data.objects); crater(FOOT[0], FOOT[1], r=1050 * K1 / 5000); crat = set(bpy.data.objects) - t2
    for o in dented | crat: o.hide_render = True
    S.render.engine = "CYCLES"; S.cycles.use_denoising = True; S.cycles.max_bounces = 4
    cam = camera(); cam.data.clip_start = 20; cam.data.clip_end = 200000
    def land():
        for o in flat: o.hide_render = True
        for o in dented | crat: o.hide_render = False
    render_seq(st, eye(cam, arm, pitch, lens, yaw), before_last=land)

# ---------------------------------------------------------------- Earth (steps 16-25)
EARTH = {  # shot: (n, leg, cam_loc_fn(H), look_fn(H), lens)   H = giant height in km
    "e16": (16, "r", lambda H: (-1.6 * H, -2.4 * H, 1.25 * H), lambda H: (0, 0, 0.5 * H), 32),
    "e18": (18, "l", lambda H: (-2.0 * H, -3.0 * H, 0.9 * H), lambda H: (0, 0, 0.45 * H), 30),
    "e19": (19, "r", lambda H: (-1.6 * H, -2.4 * H, 1.6 * H), lambda H: (0, 0, 0.3 * H), 26),
    "e21": (21, "l", lambda H: (-1.6 * H, -3.2 * H, 0.6 * H), lambda H: (0, 0, 0.2 * H), 30),
    "e23": (23, "r", lambda H: (-1.4 * H, -3.0 * H, 0.2 * H), lambda H: (0, 0, -0.1 * H), 30),
}

def earth_shot():
    sun = space_world(Vector((-0.5, -0.7, 0.5)))
    root, e, m, core, atmo = build_earth()
    rig, arm = load_char(); rig.rotation_euler[2] = float(os.environ.get("ROT", "-1.0"))
    for o in arm.children:   # the giant's body must not throw the whole planet into shadow
        if o.type == "MESH": o.visible_shadow = False
    cam = camera(); cam.data.clip_start = 5; cam.data.clip_end = 5e6
    if shot in EARTH:
        n, leg, cl, lk, lens = EARTH[shot]
        K1 = 2 ** n / 1000.0; H = 1.75 * K1
        st = Step(rig, arm, K1 / 2, K1, leg, land=(0.15 * K1, 0.25 * K1), ground=R_E)
        if n <= 18: atmo.hide_render = True
        def camfn(i, t):
            cam.location = cl(H); look = Vector(lk(H)) + Vector((0, 0, R_E))
            cam.location = Vector(cam.location) + Vector((0, 0, R_E))
            cam.rotation_euler = (look - cam.location).to_track_quat("-Z", "Y").to_euler(); cam.data.lens = lens
        render_seq(st, camfn); return
    if shot == "e25":   # 58,720 km: the foot comes down on the Earth and it breaks
        K1 = 2 ** 25 / 1000.0; H = 1.75 * K1
        nf = int(os.environ.get("NF25", "72")); hit = 16
        cells = voronoi_shatter(e, core, n=int(os.environ.get("CELLS", "40")), center=Vector((0, 0, 1)))
        e.hide_render = True
        for o in bpy.data.objects:
            if o.name in ("clouds", "atmo"): pass
        clouds_o = bpy.data.objects.get("clouds")
        corel = uvsphere("corelight", R_E * 0.55, core, 48); corel.parent = root
        # giant: right foot comes down onto the Earth top; body above in space
        rig.rotation_euler[2] = -1.0
        set_pose(arm, 16); rig.scale = (K1, K1, K1); rig.location = (0, 0, 0); bpy.context.view_layer.update()
        fr = bone_world(arm, "foot_r").translation.copy()
        base = Vector((-fr.x, -fr.y, R_E * 0.98 - fr.z))
        rnd = random.Random(5)
        vel = {o.name: ((p.normalized() + Vector((rnd.uniform(-.3, .3), rnd.uniform(-.3, .3), rnd.uniform(-.3, .3)))).normalized() * rnd.uniform(0.6, 1.4),
                        Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1))) * 0.9) for o, p in cells}
        gpu()
        frames = range(nf + 1) if not ONLY else ([nf] if ONLY == "last" else [int(x) for x in ONLY.split(",")])
        for i in frames:
            if i <= hit:
                tt = ease(i / hit); set_pose(arm, int(round(4 + 12 * tt)))
                rig.location = base + Vector((0, -0.25 * K1 * (1 - tt), 0.35 * K1 * (1 - tt)))
            else:
                set_pose(arm, 16); rig.location = base + Vector((0, 0, -0.0008 * K1 * (i - hit)))
            rig.scale = (K1, K1, K1)
            s = max(0, i - hit) / 24.0
            for o, p in cells:
                v, w = vel[o.name]
                dist = R_E * (1.5 * s + 0.6 * s * s); o.location = v * dist
                o.rotation_euler = (w * s).to_tuple()
            if clouds_o: clouds_o.hide_render = i > hit
            atmo.hide_render = i > hit + 2
            corel.hide_render = i <= hit
            if i > hit:
                k = 1.0 + 0.5 * s; corel.scale = (k, k, k)
                core.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 3.2 * math.exp(-1.0 * s) + 1.4
            for o, p in cells: o.hide_render = i <= hit
            e.hide_render = i > hit
            bpy.context.view_layer.update()
            cam.location = Vector((-15000, -24000, 9000)); look = Vector((0, 0, 3500))
            cam.rotation_euler = (look - cam.location).to_track_quat("-Z", "Y").to_euler(); cam.data.lens = 28
            if i > hit and i < hit + 10:   # impact shake
                cam.rotation_euler[0] += rnd.uniform(-1, 1) * 0.01 * (hit + 10 - i) / 10
                cam.rotation_euler[2] += rnd.uniform(-1, 1) * 0.01 * (hit + 10 - i) / 10
            S.render.resolution_percentage = PCT; S.cycles.samples = SPP
            S.render.filepath = os.path.join(outdir, f"{shot}_{i:03d}.png")
            bpy.ops.render.render(write_still=True); print("FRAME", shot, i, flush=True)
        return
    raise SystemExit("unknown earth shot " + shot)

if KIND == "park": park()
elif KIND == "seoul": seoul_shot()
else: earth_shot()
print("DONE", shot)
