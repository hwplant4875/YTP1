"""Titan cast for Shiganshina, year 845 (plug-in for scene.py).

Enable:  AOT_PLUGINS=cast845  AOT_EVENT=intact|colossal|armored   (default intact)
    cd timelapse3d && AOT_PLUGINS=cast845 AOT_EVENT=colossal bash render.sh colossal_town out.png 960x540 32

States
  intact    845 morning: 12 pure titans (3-15 m, varied pure_titans presets) wander the meadow and the forest
            edges south / south-east / south-west of the outer gate (all y < -760, none inside the walls),
            each with its own looping walk Action at a different phase, facing varied directions.
  colossal  the same wanderers + the 60 m Colossal Titan just outside the south outer gate: head and
            shoulders above the 50 m wall top, leaning over it, looking north into the town, its left hand
            gripping the wall top, steam all around (colossal.colossal_steam + titans.steam), warm haze light.
  armored   after the kick: outer gate door gone, rubble and thrown wall blocks, houses near the gate
            flattened, ~18 pure titans (incl. the Smiling Titan) streaming in along the main avenue, a few
            more outside heading for the breach, and the 15 m Armored Titan charging north up the avenue
            toward the inner gate (0, 0) with dust at its feet.

Cameras: titans_outside, colossal_town (thumbnail), colossal_side, armored_gate (+ cast_debug).
Design modules (titans.py, pure_titans.py, colossal.py, shifters.py) are only called, never edited.
Every titan build is wrapped: a failure is logged and the rest of the cast still builds.
"""
import bpy, bmesh, math, os, random, sys, time, traceback
from mathutils import Vector, Matrix

import aotlib as L

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

REPLACES = {"titans"}
EVENT = (os.environ.get("AOT_EVENT") or getattr(getattr(L, "A", None), "event", "") or "intact").strip().lower()
if EVENT not in ("intact", "colossal", "armored"):
    print(f"[cast845] unknown AOT_EVENT {EVENT!r}, using intact")
    EVENT = "intact"
if EVENT == "colossal" and hasattr(L, "event_colossal"):
    # scene.py --event colossal would add its own placeholder Colossal after build(): this plug-in owns it now
    L.event_colossal = lambda: None

OG = Vector(L.OUTER_GATE)                  # (0, -720)
WALL_TOP = float(L.WALL_H)                 # 50 m
STATE = {}                                 # filled by build(): rigs, key positions (read by the camera callables)


def log(*a):
    print("[cast845]", *a, flush=True)


# ------------------------------------------------------------------------------------------ helpers
def yaw_towards(dx, dy):
    """Object Z rotation that turns an MPFB rig (front = local -Y) to face world direction (dx, dy)."""
    return math.atan2(dx, -dy)


def ground(x, y):
    return L.height(x, y)


def place(rig, x, y, yaw, sink=0.05):
    rig.location = (x, y, ground(x, y) - sink)
    rig.rotation_mode = "XYZ"
    rig.rotation_euler = (0.0, 0.0, yaw)


def preset_name(want, idx):
    """pure_titans' preset names change while its author iterates: fall back to an index."""
    import pure_titans as PT
    keys = list(getattr(PT, "GENERIC_KEYS", []))
    if want in keys:
        return want
    alias = {"longhair_gaper": "messy_gaper", "messy_gaper": "longhair_gaper"}.get(want)
    if alias in keys:
        return alias
    return keys[idx % len(keys)] if keys else None


def make_pure(kind, seed, preset, height, lod, name):
    import pure_titans as PT
    t = time.time()
    if kind == "smiling":
        rig = PT.make_pure("smiling", seed=seed, height=height, lod=lod, name=name)
    else:
        rig = PT.make_pure("generic", seed=seed, preset=preset_name(preset, seed), height=height, lod=lod, name=name)
    log(f"{name}: {rig.get('pure_preset')} {rig.get('height_m', 0):.1f} m in {time.time() - t:.1f}s")
    return rig


def walk(rig, cycle, offset, travel=True):
    import pure_titans as PT
    try:
        PT.walk_action(rig, cycle_frames=cycle, offset=offset, travel=travel)
    except Exception as ex:
        log(f"walk_action failed on {rig.name}: {ex!r}")


def coll_link(obs, coll):
    for ob in obs:
        for c in list(ob.users_collection):
            c.objects.unlink(ob)
        coll.objects.link(ob)


def tree_of(rig):
    out = [rig]
    for c in rig.children_recursive:
        out.append(c)
    return out


def instance_rig(src, name, height):
    """Cheap copy of a built pure titan: new armature object + body object sharing the mesh data."""
    rig = src.copy(); rig.name = name
    rig.animation_data_clear()
    for ob in src.users_collection:
        ob.objects.link(rig)
    s = height / float(src.get("height_m", height)) * src.scale.x
    rig.scale = (s, s, s); rig["height_m"] = height
    for ch in src.children:
        c = ch.copy(); c.name = name + "_" + ch.name.split("_")[-1]
        c.parent = rig
        for m in c.modifiers:
            if m.type == "ARMATURE":
                m.object = rig
        for col in ch.users_collection:
            col.objects.link(c)
    # same pose as the source until walk_action keys its own phase
    for pb in src.pose.bones:
        q = rig.pose.bones[pb.name]
        q.rotation_mode = pb.rotation_mode; q.rotation_quaternion = pb.rotation_quaternion
        q.rotation_euler = pb.rotation_euler; q.location = pb.location; q.scale = pb.scale
    return rig


def pure_crowd(specs, coll, tag, unique=None):
    """specs: (kind, preset, height, x, y, facing (dx, dy) or yaw-rad, seed, lod, cycle, offset).
    unique: build at most this many MPFB titans and fill the rest with shared-mesh copies (same preset when
    possible) - an MPFB build costs ~4-6 s, a copy ~0.2 s."""
    rigs, built = [], {}
    for i, (kind, preset, H, x, y, face, seed, lod, cyc, off) in enumerate(specs):
        name = f"{tag}{i:02d}_{preset if kind != 'smiling' else 'smiling'}"
        try:
            key = (kind, preset)
            if unique is not None and kind != "smiling" and (key in built or len(built) >= unique):
                src = built.get(key) or list(built.values())[i % len(built)]
                rig = instance_rig(src, name, H)
            else:
                rig = make_pure(kind, seed, preset, H, lod, name)
                built.setdefault(key, rig)
            yaw = yaw_towards(*face) if isinstance(face, tuple) else face
            place(rig, x, y, yaw)
            walk(rig, cyc, off)
            coll_link(tree_of(rig), coll)
            rigs.append(rig)
        except Exception as ex:
            traceback.print_exc()
            log(f"pure titan {name} failed: {ex!r} (continuing)")
    return rigs


# ------------------------------------------------------------------------------------------ 845 wanderers
# Meadow outside the outer gate is kept free of forest within ~560 m of (0, -1100) by scene.py's gn_forest,
# so "forest edge" titans sit near that radius.  (kind, preset, H, x, y, facing, seed, lod, cycle, offset)
OUTSIDE = [
    ("generic", "bald_grinner",   13.0,    8, -1178, (0.35, -1.0),  1, 0.45, 56, 0),
    ("generic", "blond_sleeper",  10.0,  140, -1050, (-0.6, 0.8),   2, 0.40, 50, 17),
    ("generic", "pale_starer",     8.0,  120, -1165, (-1.0, -0.35), 3, 0.40, 46, 31),
    ("generic", "potbelly",        5.0,   28, -1196, (0.9, -0.5),   4, 0.40, 40, 9),
    ("generic", "messy_gaper",     7.0,  -62, -1095, (0.7, 0.7),    5, 0.40, 48, 23),
    ("generic", "ruddy_brute",    12.0,  455, -1290, (-0.5, 0.85),  6, 0.40, 52, 40),
    ("generic", "runt",            3.5,   78, -1220, (-0.4, -1.0),  7, 0.45, 36, 5),
    ("generic", "bald_grinner",   15.0, -470, -1420, (0.45, 0.9),   8, 0.40, 60, 12),
    ("generic", "ruddy_brute",     9.0,  170, -1540, (0.95, 0.3),   9, 0.35, 50, 27),
    ("generic", "pale_starer",    11.0, -235,  -820, (1.0, 0.1),   10, 0.40, 54, 44),
    ("generic", "messy_gaper",     6.0,  525,  -935, (-0.85, 0.5), 11, 0.35, 44, 19),
    ("generic", "potbelly",        4.0, -125,  -950, (-0.2, 1.0),  12, 0.35, 38, 33),
]


def build_outside(coll, specs=OUTSIDE):
    for s in specs:
        assert s[4] < -760 and not L.in_district(s[3], s[4], -30), f"titan {s} would be inside the walls"
    return pure_crowd(specs, coll, "Out")


# ------------------------------------------------------------------------------------------ Colossal
def golden_light(ctx):
    """S1E1 colossal scene: lower, warmer sun and a golden-orange haze (anime 'colossal looming' frames)."""
    el = math.radians(float(os.environ.get("COL_SUN_EL", "20")))
    az = math.radians(float(os.environ.get("SUN_AZ", "25")))
    so = ctx.get("sun")
    if so:
        so.data.color = (1.0, 0.74, 0.50)
        d = Vector((-math.cos(el) * math.cos(az), -math.cos(el) * math.sin(az), -math.sin(el)))
        so.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    w = ctx.get("world")
    if w:
        for n in w.node_tree.nodes:
            if n.type == "TEX_SKY":
                try:
                    n.sun_elevation = el
                except Exception:
                    pass
            if n.type == "VALTORGB":                       # camera-ray sky gradient: horizon gold, zenith pale
                e = n.color_ramp.elements
                e[0].color = (1.0, 0.70, 0.40, 1)
                e[1].color = (0.42, 0.47, 0.58, 1)
    hz = bpy.data.objects.get("Haze")
    if hz and hz.data.materials:
        nt = hz.data.materials[0].node_tree
        pv = next((n for n in nt.nodes if n.type == "PRINCIPLED_VOLUME"), None)
        if pv:
            pv.inputs["Color"].default_value = (1.0, 0.80, 0.56, 1)
            pv.inputs["Density"].default_value *= float(os.environ.get("COL_HAZE", "3.0"))


def tint_steam(st, col, emis=None):
    """Recolour a titans.steam() volume; emis=(colour, k) adds emission proportional to the local density
    (so the cloud glows bright white without lighting up its whole bounding box)."""
    nt = st.data.materials[0].node_tree; N = nt.nodes; Lk = nt.links
    pv = next(n for n in N if n.type == "PRINCIPLED_VOLUME")
    pv.inputs["Color"].default_value = (*col, 1)
    if emis and not pv.inputs["Emission Strength"].is_linked and pv.inputs["Density"].is_linked:
        src = pv.inputs["Density"].links[0].from_socket
        mul = N.new("ShaderNodeMath"); mul.operation = "MULTIPLY"; mul.inputs[1].default_value = emis[1]
        Lk.new(src, mul.inputs[0]); Lk.new(mul.outputs[0], pv.inputs["Emission Strength"])
        pv.inputs["Emission Color"].default_value = (*emis[0], 1)
    return st


def eval_verts(ob):
    """World-space evaluated (posed) vertex positions of a mesh object."""
    dg = bpy.context.evaluated_depsgraph_get()
    ev = ob.evaluated_get(dg)
    me = ev.to_mesh()
    mw = ev.matrix_world.copy()
    pts = [mw @ v.co for v in me.vertices]
    ev.to_mesh_clear()
    return pts


def _ray(ob, o, d):
    inv = ob.matrix_world.inverted()
    ok, loc, nrm, idx = ob.ray_cast(inv @ Vector(o), (inv.to_3x3() @ Vector(d)).normalized())
    return (ob.matrix_world @ loc) if ok else None


def wall_hit(x, z, y_from=-900.0, names=("WallShiganshina", "ButtressShiganshina", "OuterGate")):
    """First wall surface met walking north (+Y) from y_from at (x, z): the outer face y."""
    best = None
    for nm in names:
        ob = bpy.data.objects.get(nm)
        hit = _ray(ob, (x, y_from, z), (0, 1, 0)) if ob else None
        if hit is not None:
            best = hit.y if best is None else min(best, hit.y)
    return best


def wall_top_at(x, y):
    best = None
    for nm in ("WallShiganshina", "OuterGate"):
        ob = bpy.data.objects.get(nm)
        hit = _ray(ob, (x, y, 200.0), (0, 0, -1)) if ob else None
        if hit is not None:
            best = hit.z if best is None else max(best, hit.z)
    return best


COLOSSAL_X = float(os.environ.get("COL_X", "-26"))   # just west of the outer gatehouse (cap spans x -15.5 .. 15.5)
COLOSSAL_FEET_Y = -760.0                             # provisional; snapped so the chest touches the wall
COLOSSAL_LEAN = float(os.environ.get("COL_LEAN", "0.10"))


def build_colossal(coll, ctx):
    import colossal as C, titans as T
    t = time.time()
    rig = C.make_colossal("Colossal")
    place(rig, COLOSSAL_X, COLOSSAL_FEET_Y, yaw_towards(0, 1), sink=0.6)
    body = max((c for c in rig.children if c.type == "MESH"), key=lambda o: len(o.data.vertices))
    bpy.context.view_layer.update()
    steam = []
    try:
        steam = list(C.colossal_steam(rig, density=0.5))
    except Exception as ex:
        log("colossal_steam failed", repr(ex))
    # 1) lean over (provisional grip), 2) slide it north until the chest touches the outer wall face,
    # 3) solve the real grip with the hand on the wall top beside it
    P = rig.pose.bones
    try:
        C.pose_wall_grip(rig, WALL_TOP, COLOSSAL_FEET_Y + 20, side="L", lean=COLOSSAL_LEAN, hand_x=COLOSSAL_X - 16)
    except Exception as ex:
        traceback.print_exc(); log("pose_wall_grip (lean) failed", repr(ex))
    bpy.context.view_layer.update()
    pts = eval_verts(body)
    cells = {}
    for p in pts:
        if 20.0 < p.z < WALL_TOP - 0.3 and abs(p.x - COLOSSAL_X) < 16:
            k = (int(p.x // 2), int(p.z // 3))
            cells[k] = max(cells.get(k, -1e9), p.y)
    shift = 1e9
    for (cx, cz), by in cells.items():
        wy = wall_hit(cx * 2 + 1, cz * 3 + 1.5)
        if wy is not None:
            shift = min(shift, wy - 0.4 - by)
    if shift < 1e8:
        rig.location.y += shift
        log(f"Colossal snapped {shift:+.1f} m north to touch the wall (feet y {rig.location.y:.1f})")
    bpy.context.view_layer.update()
    # real grip: knuckles on the wall top just short of the inner edge, west of the body
    hx = COLOSSAL_X - float(os.environ.get("COL_HAND_DX", "15"))
    yc = L.district_ymin(hx)
    gy = yc + float(os.environ.get("COL_HAND_DY", "1.0"))
    zt = wall_top_at(hx, gy) or WALL_TOP
    try:
        C.pose_wall_grip(rig, zt, gy + 4.0, side="L", lean=COLOSSAL_LEAN, hand_x=hx)
    except Exception as ex:
        traceback.print_exc(); log("pose_wall_grip failed", repr(ex))
    try:
        P["head"].rotation_euler.x += float(os.environ.get("COL_HEAD", "-0.12"))   # chin up, looking into the town
    except Exception:
        pass
    bpy.context.view_layer.update()
    hb = rig.matrix_world @ P["head"].head
    ht = rig.matrix_world @ P["head"].tail
    hand = rig.matrix_world @ P["metacarpal3.L"].tail if "metacarpal3.L" in P else None
    STATE["colossal_head"] = hb.copy(); STATE["colossal_hand"] = hand
    pts = eval_verts(body)
    top = max(p.z for p in pts)
    log(f"Colossal built {time.time() - t:.1f}s  head bone {tuple(round(v, 1) for v in hb)} .. {tuple(round(v, 1) for v in ht)}"
        f"  top z {top:.1f}  hand {tuple(round(v, 1) for v in hand) if hand else None}  goal ({hx:.1f}, {gy:.1f}, {zt:.1f})")
    # extra steam: one continuous column rising behind it with a wide cap (mushroom plume), puffs rolling
    # over the wall top, a low cloud at its feet.  Emission keeps the steam bright white like the anime.
    try:
        fy = rig.location.y
        specs = [("ColossalColumn", (COLOSSAL_X + 2, fy - 30, 125), (80, 64, 210), 0.16, 4.5),
                 ("ColossalCap", (COLOSSAL_X + 6, fy - 38, 225), (190, 160, 95), 0.10, 4.0),
                 ("ColossalFootSteam", (COLOSSAL_X, fy - 14, 6), (120, 60, 16), 0.06, 6.0)]
        for i, dx in enumerate((-46, -14, 18)):
            specs.append((f"ColossalWallSteam{i}", (COLOSSAL_X + dx, L.district_ymin(COLOSSAL_X + dx) - 7, WALL_TOP + 3),
                          (38, 24, 18), 0.14, 5.0))
        for nm, c, sz, dn, ns in specs:
            s = T.steam(nm, c, sz, density=dn, noise_scale=ns)
            steam.append(s)
    except Exception as ex:
        log("extra steam failed", repr(ex))
    for s in steam:                       # brighten the bone-parented steam from colossal.py as well
        try:
            for n in s.data.materials[0].node_tree.nodes:      # finer billows than the cotton-ball default
                if n.type == "TEX_NOISE" and n.inputs["Scale"].default_value < 3.0:
                    n.inputs["Scale"].default_value = 4.5
            tint_steam(s, (0.97, 0.93, 0.88), emis=((1.0, 0.93, 0.85), float(os.environ.get("STEAM_EMIS", "0.7"))))
        except Exception:
            pass
    coll_link(tree_of(rig) + [s for s in steam if s.parent is None], coll)
    if os.environ.get("COL_GOLD", "1") == "1":
        golden_light(ctx)
    STATE["colossal"] = rig
    return rig


# ------------------------------------------------------------------------------------------ after the kick
def break_outer_gate(M, coll, year):
    door = bpy.data.objects.get("OuterGate_Door")
    if door:
        door.hide_render = True; door.hide_viewport = True
    rnd = random.Random(845)
    bm = bmesh.new()
    # rubble heap in the gate passage and spilling into the square
    for _ in range(70):
        x = rnd.gauss(0, 9); y = OG.y + rnd.uniform(-6, 55)
        s = rnd.uniform(1.0, 4.5)
        L.box(bm, (x, y, s * 0.3), (s * rnd.uniform(0.7, 1.4), s * rnd.uniform(0.7, 1.4), s * rnd.uniform(0.5, 1.0)),
              rnd.uniform(0, 3.14))
    # wall blocks thrown into the town by the kick (some land on houses)
    thrown = []
    for _ in range(26):
        d = rnd.uniform(70, 420); a = rnd.gauss(0, 0.45)
        x = math.sin(a) * d; y = OG.y + math.cos(a) * d
        if not L.in_district(x, y, 15):
            continue
        s = rnd.uniform(3, 8)
        L.box(bm, (x, y, s * 0.35), (s * 1.3, s, s * 0.8), rnd.uniform(0, 3.14))
        thrown.append((x, y, s))
    ob = L.obj_from_bm("GateRubble", bm, [M["stone"]], coll)
    # flatten the houses around the breach and those hit by blocks
    town = bpy.data.objects.get("Town")
    killed = 0
    if town and "dead" in town.data.attributes:
        dead = town.data.attributes["dead"].data
        for i, v in enumerate(town.data.vertices):
            x, y = v.co.x, v.co.y
            hit = math.hypot(x - OG.x, y - (OG.y + 25)) < 60 + rnd.uniform(-10, 10)
            hit = hit or any(math.hypot(x - tx, y - ty) < s + 6 for tx, ty, s in thrown)
            if hit:
                dead[i].value = min(dead[i].value, float(year)); killed += 1
        town.data.update()
    # dust over the breach
    try:
        import titans as T
        d = T.steam("BreachDust", (0, OG.y + 40, 12), (70, 60, 26), density=0.22, noise_scale=2.2)
        tint_steam(d, (0.62, 0.52, 0.40))
        coll_link([d], coll)
    except Exception as ex:
        log("dust failed", repr(ex))
    log(f"outer gate broken: {killed} houses flattened, {len(thrown)} thrown blocks")


def avenue_x(y):
    """scene.py's main avenue wiggles by noise.noise((0, y/200, 7)) * 4."""
    from mathutils import noise
    return noise.noise(Vector((0, y / 200, 7))) * 4


# streaming in: on the avenue, in the gate square, through the gate, and still outside heading for it
def inflow_specs():
    rnd = random.Random(7)
    keys = ["bald_grinner", "blond_sleeper", "pale_starer", "potbelly", "messy_gaper", "ruddy_brute", "runt"]
    hts = {"bald_grinner": 13, "blond_sleeper": 10, "pale_starer": 8, "potbelly": 5, "messy_gaper": 7, "ruddy_brute": 12, "runt": 3.5}
    specs = []
    ys = [-300, -345, -395, -430, -470, -505, -545, -585, -620, -650, -680, -700, -735, -790, -850, -905]
    for k, y in enumerate(ys):
        p = keys[k % len(keys)]
        x = avenue_x(y) + rnd.uniform(-5, 5) if y > -705 else rnd.uniform(-6, 6)
        if y < -740:
            x = rnd.uniform(-40, 40)
        to_x = -x * 0.02 + rnd.uniform(-0.25, 0.25)
        H = hts[p] * rnd.uniform(0.85, 1.15)
        specs.append(("generic", p, H, x, y, (to_x, 1.0), 100 + k, 0.35, rnd.randint(40, 56), rnd.randint(0, 40)))
    # the Smiling Titan heads off the avenue to the west (toward the Yeager house)
    specs.append(("smiling", "smiling", 14.0, -18, -560, (-0.8, 0.6), 1, 0.45, 60, 10))
    # two in the canal-side road
    specs.append(("generic", "ruddy_brute", 11.0, L.CX - 22, -560, (0.0, 1.0), 140, 0.35, 50, 3))
    specs.append(("generic", "pale_starer", 7.5, -40, -640, (-0.5, 0.8), 141, 0.35, 46, 21))
    return specs


ARMORED_XY = (0.0, -140.0)


def charge_pose(rig):
    """Head-down shoulder-first run: reuse pure_titans' gait with a long stride and heavy forward lean."""
    import pure_titans as PT
    rig["gait"] = dict(stride=0.75, knee=1.0, sway=0.015, bob=0.04, arm=0.65, limp=0.0)
    rig["slouch"] = 0.9; rig["arms_out"] = 0.85; rig["gait_seed"] = 3
    try:
        rots, off = PT._gait(rig, 0.22)
        off, _, _ = PT._ground(rig, rots, off)
        PT._apply(rig, rots, off)
    except Exception as ex:
        log("charge pose via pure_titans gait failed", repr(ex))
    try:
        PT.walk_action(rig, cycle_frames=26, offset=6, travel=True)
    except Exception as ex:
        log("armored run action failed", repr(ex))


def build_armored(coll):
    import shifters as SH, titans as T
    t = time.time()
    rig = SH.make_armored("ArmoredTitan")
    place(rig, ARMORED_XY[0] + avenue_x(ARMORED_XY[1]), ARMORED_XY[1], yaw_towards(0, 1))
    charge_pose(rig)
    rig.rotation_euler.x = float(os.environ.get("ARM_TILT", "0.2"))     # whole-body forward lean of the charge
    obs = tree_of(rig)
    try:
        d = T.steam("ArmoredDust", (rig.location.x, rig.location.y - 14, 3.5), (30, 44, 12), density=0.7, noise_scale=4.0)
        tint_steam(d, (0.80, 0.72, 0.60), emis=((0.85, 0.76, 0.62), 0.5)); obs.append(d)
    except Exception as ex:
        log("armored dust failed", repr(ex))
    coll_link(obs, coll)
    STATE["armored"] = rig
    log(f"Armored built {time.time() - t:.1f}s at {tuple(round(v, 1) for v in rig.location)}")
    return rig


def _copies_of(pool, specs, coll):
    """Outside titans for the armored state, all copies of the inflow crowd's MPFB builds."""
    out = []
    pool = [r for r in pool if "smiling" not in r.name]
    for i, (kind, preset, H, x, y, face, seed, lod, cyc, off) in enumerate(specs):
        if not pool:
            break
        src = next((r for r in pool if r.get("pure_preset") == preset_name(preset, seed)), pool[i % len(pool)])
        try:
            rig = instance_rig(src, f"Out{i:02d}_{preset}", H)
            place(rig, x, y, yaw_towards(*face))
            walk(rig, cyc, off)
            coll_link(tree_of(rig), coll)
            out.append(rig)
        except Exception as ex:
            traceback.print_exc(); log(f"copy {i} failed {ex!r}")
    return out


# ------------------------------------------------------------------------------------------ entry point
def build(M, year, ctx):
    t0 = time.time()
    coll = L.new_coll("Cast845")
    log(f"event state: {EVENT}")
    if EVENT in ("intact", "colossal"):
        STATE["outside"] = build_outside(coll)
    if EVENT == "colossal":
        try:
            build_colossal(coll, ctx)
        except Exception as ex:
            traceback.print_exc(); log("Colossal failed", repr(ex))
    if EVENT == "armored":
        try:
            break_outer_gate(M, coll, year)
        except Exception as ex:
            traceback.print_exc(); log("gate break failed", repr(ex))
        STATE["inflow"] = pure_crowd(inflow_specs(), coll, "In", unique=int(os.environ.get("CAST_UNIQUE", "7")))
        try:
            build_armored(coll)
        except Exception as ex:
            traceback.print_exc(); log("Armored failed", repr(ex))
        # a few still outside heading for the breach
        rest = [s[:5] + ((-s[3], OG.y - s[4]),) + s[6:] for s in OUTSIDE[:6]]
        STATE["outside"] = pure_crowd(rest, coll, "Out", unique=0) if False else _copies_of(STATE.get("inflow", []), rest, coll)
    bpy.context.scene.frame_set(1)
    n = sum(1 for o in bpy.data.objects if o.type == "ARMATURE")
    log(f"{n} titan rigs in the scene")
    log(f"cast built in {time.time() - t0:.1f}s")


# ------------------------------------------------------------------------------------------ cameras
def _cam_colossal_town():
    h = STATE.get("colossal_head") or Vector((COLOSSAL_X, -735.0, 55.0))
    off = [float(v) for v in os.environ.get("CT_OFF", "32,195,-33").split(",")]
    loc = Vector((h.x + off[0], h.y + off[1], h.z + off[2]))
    tgt = Vector((h.x - 6.0, h.y, h.z - float(os.environ.get("CT_DOWN", "9"))))
    return tuple(loc), tuple(tgt), float(os.environ.get("CT_LENS", "45"))


def _cam_colossal_closeup():
    """Tight thumbnail variant: long lens from a rooftop deep in the town, head + hand + wall top fill the frame."""
    h = STATE.get("colossal_head") or Vector((COLOSSAL_X, -735.0, 55.0))
    return (h.x + 70.0, h.y + 420.0, h.z - 12.0), (h.x - 9.0, h.y, h.z - 1.5), 135


def _cam_colossal_side():
    return (COLOSSAL_X - 135.0, -880.0, 16.0), (COLOSSAL_X + 6, -738.0, 36.0), 26


def _cam_armored_gate():
    """From high behind the Armored, down the main avenue: it charges at the inner gate, Wall Maria beyond."""
    r = STATE.get("armored")
    p = Vector(r.location) if r else Vector((0, ARMORED_XY[1], 0))
    off = [float(v) for v in os.environ.get("AG_OFF", "12,-118,40").split(",")]
    loc = (p.x + off[0], p.y + off[1], off[2])
    tgt = (0.0, -10.0, float(os.environ.get("AG_TZ", "8")))
    return loc, tgt, float(os.environ.get("AG_LENS", "38"))


def _cam_armored_front():
    """Looking south down the avenue from above the inner gate square: the Armored charging at the camera,
    pure titans streaming in behind it from the broken outer gate."""
    r = STATE.get("armored")
    p = Vector(r.location) if r else Vector((0, ARMORED_XY[1], 0))
    return (p.x + 6, -42.0, 40), (p.x - 4, p.y - 30, 6), 35


CAMS = {
    "titans_outside": ((62.0, -1262.0, 4.5), (-12.0, -760.0, 30.0), 30),
    "colossal_town": _cam_colossal_town,
    "colossal_side": _cam_colossal_side,
    "colossal_closeup": _cam_colossal_closeup,
    "armored_gate": _cam_armored_gate,
    "armored_front": _cam_armored_front,
    "cast_debug": ((0.0, -1500.0, 600.0), (0.0, -900.0, 0.0), 30),
}

LABELS = {"OUTER GATE": (0.0, -720.0, 50.0)}
if EVENT == "colossal":
    LABELS["COLOSSAL TITAN"] = (COLOSSAL_X, -735.0, 64.0)
if EVENT == "armored":
    LABELS["ARMORED TITAN"] = (ARMORED_XY[0], ARMORED_XY[1], 20.0)
