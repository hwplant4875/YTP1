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
from mathutils import Vector, Matrix, Quaternion

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


LOGF = os.environ.get("CAST_LOG", "E:/YTP2/3D Timelapse/renders/cast845/cast845.log")


def log(*a):
    print("[cast845]", *a, flush=True)
    if LOGF:                                   # render.sh only shows the log tail: keep the full build log too
        try:
            with open(LOGF, "a", encoding="utf8") as fh:
                fh.write(" ".join(str(x) for x in a) + chr(10))
        except Exception:
            pass


def srgb(h):
    """'#RRGGBB' -> linear RGB tuple."""
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]
    return tuple(v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c)


# ------------------------------------------------------------------------------------------ steam puffs
# Many small overlapping volume puffs instead of a few big boxes: each puff is an ellipsoid whose density is a
# spherical falloff plus Object-space noise pushed through a narrow ColorRamp, so its edge is lumpy
# (cauliflower) instead of a smooth soft ball.  Colour fades with world height (pink-tan base -> white top).
_PUFF = {}


def puff_mat(key, c_lo, c_hi, z_lo, z_hi, dens, noise=8.0, emis=0.3, amp=2.0, thr=(0.45, 0.6)):
    if key in _PUFF:
        return _PUFF[key]
    m = bpy.data.materials.new("Puff_" + key); m.use_nodes = True
    nt = m.node_tree; N = nt.nodes; Lk = nt.links
    N.remove(N["Principled BSDF"])
    pv = N.new("ShaderNodeVolumePrincipled"); pv.inputs["Anisotropy"].default_value = 0.35
    tc = N.new("ShaderNodeTexCoord"); oi = N.new("ShaderNodeObjectInfo")
    # 3D noise (4D costs ~2x per volume step) shifted per object by its random value; few octaves keep the
    # per-step shader cheap, the lumps come from amp + the narrow ramp
    nz = N.new("ShaderNodeTexNoise"); nz.noise_dimensions = "3D"
    nz.inputs["Scale"].default_value = noise; nz.inputs["Detail"].default_value = float(os.environ.get("PUFF_DETAIL", "2"))
    try:
        nz.inputs["Roughness"].default_value = 0.6
    except Exception:
        pass
    sh = N.new("ShaderNodeVectorMath"); sh.operation = "SCALE"; sh.inputs[0].default_value = (9.7, 5.3, 3.1)
    Lk.new(oi.outputs["Random"], sh.inputs["Scale"])
    ad = N.new("ShaderNodeVectorMath"); ad.operation = "ADD"
    Lk.new(tc.outputs["Object"], ad.inputs[0]); Lk.new(sh.outputs[0], ad.inputs[1])
    Lk.new(ad.outputs[0], nz.inputs["Vector"])
    ln = N.new("ShaderNodeVectorMath"); ln.operation = "LENGTH"; Lk.new(tc.outputs["Object"], ln.inputs[0])
    fall = N.new("ShaderNodeMapRange")
    fall.inputs["From Min"].default_value = 0.5; fall.inputs["From Max"].default_value = 0.0
    Lk.new(ln.outputs["Value"], fall.inputs["Value"])
    nn = N.new("ShaderNodeMath"); nn.operation = "MULTIPLY_ADD"
    nn.inputs[1].default_value = amp; nn.inputs[2].default_value = -0.5 * amp
    Lk.new(nz.outputs["Fac"], nn.inputs[0])
    v = N.new("ShaderNodeMath"); v.operation = "ADD"
    Lk.new(fall.outputs["Result"], v.inputs[0]); Lk.new(nn.outputs[0], v.inputs[1])
    rp = N.new("ShaderNodeValToRGB"); e = rp.color_ramp.elements
    e[0].position = thr[0]; e[0].color = (0, 0, 0, 1); e[1].position = thr[1]; e[1].color = (1, 1, 1, 1)
    Lk.new(v.outputs[0], rp.inputs["Fac"])
    d = N.new("ShaderNodeMath"); d.operation = "MULTIPLY"; d.inputs[1].default_value = dens
    Lk.new(rp.outputs["Color"], d.inputs[0]); Lk.new(d.outputs[0], pv.inputs["Density"])
    geo = N.new("ShaderNodeNewGeometry"); sep = N.new("ShaderNodeSeparateXYZ")
    Lk.new(geo.outputs["Position"], sep.inputs[0])
    zr = N.new("ShaderNodeMapRange"); zr.inputs["From Min"].default_value = z_lo; zr.inputs["From Max"].default_value = z_hi
    Lk.new(sep.outputs["Z"], zr.inputs["Value"])
    mx = N.new("ShaderNodeMix"); mx.data_type = "RGBA"
    ia = next(i for i in mx.inputs if i.name == "A" and i.type == "RGBA")
    ib = next(i for i in mx.inputs if i.name == "B" and i.type == "RGBA")
    ia.default_value = (*c_lo, 1); ib.default_value = (*c_hi, 1)
    Lk.new(zr.outputs["Result"], mx.inputs["Factor"])
    out = next(o for o in mx.outputs if o.type == "RGBA")
    Lk.new(out, pv.inputs["Color"]); Lk.new(out, pv.inputs["Emission Color"])
    es = N.new("ShaderNodeMath"); es.operation = "MULTIPLY"; es.inputs[1].default_value = emis
    Lk.new(d.outputs[0], es.inputs[0]); Lk.new(es.outputs[0], pv.inputs["Emission Strength"])
    Lk.new(pv.outputs[0], N["Material Output"].inputs["Volume"])
    me = bpy.data.meshes.new("PuffMesh_" + key)
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.5); bm.to_mesh(me); bm.free()
    me.materials.append(m)
    _PUFF[key] = me
    return me


def puff(name, c, r, mesh, coll, squash=(1.0, 1.0, 1.0)):
    """One steam puff of radius r (m) at c using a puff_mat() mesh."""
    ob = bpy.data.objects.new(name, mesh)
    ob.location = c
    ob.scale = (2 * r * squash[0], 2 * r * squash[1], 2 * r * squash[2])
    ob.rotation_euler = (0, 0, (hash(name) % 628) / 100.0)
    ob.visible_shadow = False
    coll.objects.link(ob)
    return ob


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
    # composed for titans_outside (camera TO_CAM = (-30, -975), 3 m, 35 mm, looking at the outer gate)
    ("generic", "bald_grinner",   15.0,  -36,  -912, (0.55, 1.0),   1, 0.50, 60, 0),    # foreground, 3/4 back, toward the wall
    ("generic", "blond_sleeper",   8.5,  -47,  -890, (0.9, 0.25),   2, 0.45, 50, 17),   # left third
    ("generic", "ruddy_brute",    11.0,    4,  -888, (-0.75, 0.6),  6, 0.45, 52, 40),   # right third
    ("generic", "messy_gaper",     7.0,   22,  -800, (-0.3, 1.0),   5, 0.40, 48, 23),   # near the gate approach
    ("generic", "pale_starer",     8.0,  120, -1165, (-1.0, -0.35), 3, 0.40, 46, 31),
    ("generic", "runt",            3.5,   78, -1220, (-0.4, -1.0),  7, 0.45, 36, 5),
    ("generic", "ruddy_brute",    12.0,  455, -1290, (-0.5, 0.85),  6, 0.40, 52, 40),
    ("generic", "bald_grinner",   15.0, -470, -1420, (0.45, 0.9),   8, 0.40, 60, 12),
    ("generic", "ruddy_brute",     9.0,  170, -1540, (0.95, 0.3),   9, 0.35, 50, 27),
    ("generic", "pale_starer",    11.0, -235,  -820, (1.0, 0.1),   10, 0.40, 54, 44),
    ("generic", "messy_gaper",     6.0,  525,  -935, (-0.85, 0.5), 11, 0.35, 44, 19),
    ("generic", "potbelly",        4.0, -125,  -950, (-0.2, 1.0),  12, 0.35, 38, 33),
    ("generic", "blond_sleeper",  10.0,  140, -1050, (-0.6, 0.8),  13, 0.40, 50, 17),
]
# conifer clumps (x, y, count, radius) framing the meadow shots at 150-300 m from TO_CAM
GROVES = [(-118, -835, 9, 22), (-160, -905, 6, 16), (78, -800, 8, 20), (120, -870, 6, 16)]


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
            cam = getattr(getattr(L, "A", None), "cam", "")
            hz_def = {"colossal_closeup": "8.0", "colossal_side": "6.0"}.get(cam, "4.0")    # warm aerial haze sells the scale
            pv.inputs["Density"].default_value *= float(os.environ.get("COL_HAZE", hz_def))


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


COLOSSAL_X = float(os.environ.get("COL_X", "-58"))   # west of the outer gatehouse (cap spans x -15.5 .. 15.5), clear of it in town views
COLOSSAL_FEET_Y = -760.0                             # provisional; snapped so the chest touches the wall
COLOSSAL_LEAN = float(os.environ.get("COL_LEAN", "0.10"))


def build_colossal(coll, ctx):
    import colossal as C, titans as T
    t = time.time()
    rig = C.make_colossal("Colossal")
    place(rig, COLOSSAL_X, COLOSSAL_FEET_Y, yaw_towards(0, 1), sink=0.6)
    body = max((c for c in rig.children if c.type == "MESH"), key=lambda o: len(o.data.vertices))
    bpy.context.view_layer.update()
    # colossal.colossal_steam's bone-parented balls read as stuck-on cotton: replaced by colossal_fx()
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
    measure_colossal(rig, body)
    coll_link(tree_of(rig), coll)
    STATE["colossal"] = rig
    try:
        colossal_fx(rig, coll)
    except Exception as ex:
        traceback.print_exc(); log("colossal fx failed", repr(ex))
    if os.environ.get("COL_GOLD", "1") == "1":
        golden_light(ctx)
    return rig


def measure_colossal(rig, body):
    """Scale check against design bible 3.4: head top ~61 m (~10 m over the 50 m wall), ~19 m across the
    shoulders incl. arms.  Logged, and the head clearance is asserted."""
    pts = eval_verts(body)
    top = max(p.z for p in pts)
    band = [p for p in pts if WALL_TOP - 14 < p.z < WALL_TOP - 2]
    sw = (max(p.x for p in band) - min(p.x for p in band)) if band else 0.0
    head = [p for p in pts if p.z > top - 6.2]
    hw = (max(p.x for p in head) - min(p.x for p in head)) if head else 0.0
    STATE["colossal_top"] = top
    log(f"SCALE CHECK: top z {top:.1f} (wall {WALL_TOP:.0f}, clearance {top - WALL_TOP:.1f} m), "
        f"width at chest/arms band {sw:.1f} m, head width {hw:.1f} m, rig scale {tuple(round(v, 3) for v in rig.scale)}")
    assert top - WALL_TOP >= 8.0, f"Colossal head top z {top:.1f} is only {top - WALL_TOP:.1f} m over the wall (bible: ~10-11 m)"


def colossal_fx(rig, coll):
    """845 look (design bible 3.4 / 3.8): pink-tan mushroom column behind the wall, heavy white steam off the
    face and shoulders, low puffs along the wall foot, orange embers round the head, optional lightning bolt."""
    rnd = random.Random(int(os.environ.get("STEAM_SEED", "845")))
    P = rig.pose.bones
    mw = rig.matrix_world
    hb = mw @ P["head"].head
    fy = rig.location.y
    em = float(os.environ.get("STEAM_EMIS", "1.6"))
    tan, white = srgb("#C9A08A"), srgb("#E8E4DE")
    obs = []
    # --- mushroom column: random walk up to z ~400, radius 8 -> 25 m, then a cap spreading to ~250 m
    base = Vector((rig.location.x + 6, fy - 34, 30.0))
    m_col = puff_mat("column", tan, white, 40.0, 380.0, float(os.environ.get("PLUME_D", "0.28")), noise=7.0, emis=em)
    m_cap = puff_mat("cap", tan, white, 40.0, 380.0, float(os.environ.get("PLUME_D", "0.28")) * 0.75, noise=6.0, emis=em)
    p = base.copy()
    n = int(os.environ.get("PLUME_N", "22"))
    lean = Vector((0.05, -0.12, 0))
    for i in range(n):
        t = i / (n - 1)
        r = (14 + 22 * t ** 0.8) * rnd.uniform(0.85, 1.15)
        p = Vector((p.x + rnd.uniform(-0.45, 0.45) * r, p.y + rnd.uniform(-0.45, 0.45) * r, base.z + 345 * t)) + lean * (345 / n)
        obs.append(puff(f"PlumeCol{i:02d}", p, r, m_col, coll, (rnd.uniform(0.9, 1.25), rnd.uniform(0.9, 1.25), rnd.uniform(0.8, 1.1))))
        if i % 4 == 1:                        # side lobes so the column is not a string of beads
            a = rnd.uniform(0, 6.28); d = r * rnd.uniform(0.6, 0.9)
            obs.append(puff(f"PlumeLobe{i:02d}", p + Vector((math.cos(a) * d, math.sin(a) * d, rnd.uniform(-0.3, 0.3) * r)),
                            r * rnd.uniform(0.55, 0.8), m_col, coll))
    top = p.copy()
    STATE["plume_top"] = top
    for i in range(int(os.environ.get("CAP_N", "13"))):
        a = rnd.uniform(0, 6.28); d = 125 * math.sqrt(rnd.uniform(0.02, 1.0))
        r = rnd.uniform(28, 40)
        c = top + Vector((math.cos(a) * d, math.sin(a) * d * 0.85, rnd.uniform(-12, 22) - d * 0.12))
        obs.append(puff(f"PlumeCap{i:02d}", c, r, m_cap, coll, (1.25, 1.15, rnd.uniform(0.6, 0.8))))
    # --- low puffs along the outer wall foot (replaces the flat ground oval)
    m_gnd = puff_mat("ground", tan, white, 0.0, 60.0, 0.10, noise=8.0, emis=em * 0.8)
    for i in range(10):
        x = rig.location.x + (i - 4.5) * 13 + rnd.uniform(-4, 4)
        y = L.district_ymin(x) - rnd.uniform(9, 20)
        obs.append(puff(f"WallFootSteam{i}", (x, y, L.height(x, y) + rnd.uniform(6, 12)), 15 * rnd.uniform(0.8, 1.15), m_gnd, coll,
                        (1.3, 1.0, 0.75)))
    # --- heavy white steam pouring off the shoulders over the wall top
    m_wall = puff_mat("walltop", white, white, 0.0, 1.0, 0.30, noise=9.0, emis=em)
    for i, dx in enumerate((-30, -19, -9, 9, 19, 28)):
        x = hb.x + dx + rnd.uniform(-3, 3)
        obs.append(puff(f"WallTopSteam{i}", (x, L.district_ymin(x) - rnd.uniform(6, 12), WALL_TOP + rnd.uniform(1, 7)),
                        rnd.uniform(6, 10), m_wall, coll, (1.3, 1.0, 0.9)))
    # --- face / shoulder steam: 6 small dense puffs rising off the cheeks and shoulders
    m_face = puff_mat("face", white, white, 0.0, 1.0, 0.8, noise=9.0, emis=float(os.environ.get("FACE_EMIS", "1.0")))
    side = (mw.to_3x3() @ Vector((1, 0, 0))).normalized()
    spots = [hb + side * 2.6 + Vector((0, -1.0, 2.5)), hb - side * 2.6 + Vector((0, -1.0, 2.0))]
    for bn in ("shoulder01.L", "shoulder01.R", "upperarm01.L", "upperarm01.R"):
        if bn in P:
            spots.append(mw @ P[bn].head + Vector((0, -2.0, 4.0)))
    while len(spots) < 6:
        spots.append(hb + side * rnd.uniform(-8, 8) + Vector((0, -3, rnd.uniform(-4, 0))))
    for i, c in enumerate(spots[:6]):
        obs.append(puff(f"FaceSteam{i}", c + Vector((rnd.uniform(-1, 1), 0, rnd.uniform(0, 2))), rnd.uniform(3, 5), m_face, coll,
                        (1.0, 1.0, 1.35)))
    # --- embers: 300 small emissive icospheres in a 40 m sphere round the head
    if os.environ.get("COL_EMBERS", "1") == "1":
        ma = bpy.data.materials.new("Embers845"); ma.use_nodes = True
        b = ma.node_tree.nodes["Principled BSDF"]
        b.inputs["Base Color"].default_value = (*srgb("#FF9A40"), 1)
        b.inputs["Emission Color"].default_value = (*srgb("#FF9A40"), 1)
        b.inputs["Emission Strength"].default_value = float(os.environ.get("EMBER_E", "20"))
        bm = bmesh.new()
        for _ in range(300):
            while True:
                v = Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1)))
                if v.length <= 1:
                    break
            c = hb + v * 40.0
            c.z = max(c.z, WALL_TOP + 1)
            g = bmesh.ops.create_icosphere(bm, subdivisions=1, radius=0.15 * float(os.environ.get("EMBER_K", "1")))
            for vv in g["verts"]:
                vv.co += c
        eo = L.obj_from_bm("ColossalEmbers", bm, [ma], coll)
        eo.visible_shadow = False
        obs.append(eo)
    # --- lightning bolt down the plume's west edge (transformation frame only)
    if os.environ.get("COL_BOLT", "0") == "1":
        obs += lightning(coll, Vector((top.x - 70, top.y, top.z - 10)), Vector((base.x - 25, base.y + 4, 0.0)), rnd)
    STATE["colossal_fx"] = obs
    log(f"colossal fx: {len(obs)} objects, plume top {tuple(round(v) for v in top)}")


def lightning(coll, a, b, rnd):
    """Jagged emissive bolt (curve, bevel 0.8 m, #FFE680 x40) from a to b with two short forks."""
    ma = bpy.data.materials.new("Bolt845"); ma.use_nodes = True
    bs = ma.node_tree.nodes["Principled BSDF"]
    bs.inputs["Base Color"].default_value = (1, 1, 1, 1)
    bs.inputs["Emission Color"].default_value = (*srgb("#FFE680"), 1)
    bs.inputs["Emission Strength"].default_value = 40.0

    def path(p0, p1, n, jit):
        pts = []
        for i in range(n + 1):
            q = p0.lerp(p1, i / n)
            if 0 < i < n:
                q = q + Vector((rnd.uniform(-1, 1) * jit, rnd.uniform(-0.4, 0.4) * jit, rnd.uniform(-0.3, 0.3) * jit))
            pts.append(q)
        return pts

    main = path(a, b, 26, 11.0)
    strokes = [(main, 0.8)]
    for k in (7, 15):
        f0 = main[k]
        strokes.append((path(f0, f0 + Vector((rnd.choice((-1, 1)) * 40, 0, -70)), 7, 6.0), 0.45))
    cu = bpy.data.curves.new("Bolt845", "CURVE"); cu.dimensions = "3D"
    for pts, bev in strokes:
        sp = cu.splines.new("POLY"); sp.points.add(len(pts) - 1)
        for i, q in enumerate(pts):
            sp.points[i].co = (q.x, q.y, q.z, 1)
            sp.points[i].radius = bev / 0.8
    cu.bevel_depth = 0.8; cu.bevel_resolution = 1
    ob = bpy.data.objects.new("Bolt845", cu); ob.data.materials.append(ma); ob.visible_shadow = False
    coll.objects.link(ob)
    return [ob]


# ------------------------------------------------------------------------------------------ after the kick
def break_outer_gate(M, coll, year):
    """Gate damage for the armored state.  states845 owns the breach (rubble, crushed houses, smoke) when it is
    loaded or when AOT_STATE asks for a broken state: then cast845 adds titans only (no second debris style)."""
    if bpy.data.collections.get("States845") or os.environ.get("AOT_STATE", "intact").strip().lower() != "intact" \
            or "states845" in [p.strip() for p in os.environ.get("AOT_PLUGINS", "").split(",")]:
        log("break_outer_gate: states845 owns the breach -> titans only")
        return
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
    L.obj_from_bm("GateRubble", bm, [M["stone"]], coll)
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
    m = puff_mat("breach", srgb("#9C8A74"), srgb("#C8B497"), 0.0, 40.0, 0.25, noise=7.0, emis=0.1)
    for i in range(9):
        puff(f"BreachDust{i}", (rnd.gauss(0, 18), OG.y + 30 + rnd.uniform(-10, 40), rnd.uniform(6, 18)), rnd.uniform(9, 15), m, coll,
             (1.3, 1.1, 0.8))
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


def footfall_dust(rig, coll):
    """A trail of 8 small dust puffs behind each foot (kicked up by the last strides), growing and thinning
    with age, instead of one cloud in front of the Armored."""
    bpy.context.scene.frame_set(1); bpy.context.view_layer.update()
    P = rig.pose.bones; mw = rig.matrix_world
    back = (mw.to_3x3() @ Vector((0, 1, 0)))          # MPFB front is local -Y: +Y is behind
    back.z = 0; back.normalize()
    m = puff_mat("footdust", srgb("#A89070"), srgb("#D2C2A6"), 0.0, 12.0, 0.55, noise=8.0, emis=0.15)
    rnd = random.Random(15)
    obs = []
    for side, bn in (("L", "foot.L"), ("R", "foot.R")):
        f = (mw @ P[bn].head) if bn in P else rig.location + Vector((2.0 if side == "L" else -2.0, 0, 0))
        f.z = L.height(f.x, f.y)
        for k in range(8):
            c = f + back * (2.5 + k * 3.6) + Vector((rnd.uniform(-1, 1) * (0.5 + 0.25 * k), 0, 0.8 + 0.45 * k))
            obs.append(puff(f"FootDust{side}{k}", c, 1.3 + 0.55 * k, m, coll, (1.2, 1.2, 0.85)))
    return obs


def fleeing_people(coll, p0, n=16):
    """10-20 tiny townsfolk (1.7 m metaball figures, one-colour outfits) running north ahead of the Armored."""
    rnd = random.Random(31)
    cols = ["#6B4E3A", "#8C7A5B", "#3F4A5C", "#A39074", "#5E3B32", "#7A8270", "#D8CDB4"]
    proto = []
    for v in range(3):
        sk = v == 1
        lift = 0.25 if v != 2 else 0.18
        parts = [("E", (0, 0.10, 1.57), (0.10, 0.11, 0.12)),
                 ("E", (0, 0.05, 1.20), (0.18, 0.12, 0.26), (0.3, 0, 0)),
                 ("E", (0, 0.0, 0.93), (0.16, 0.11, 0.11)),
                 ("C", (0.09, 0, 0.9), (0.10, lift, 0.50), 0.07), ("C", (0.10, lift, 0.50), (0.10, lift - 0.05, 0.07), 0.06),
                 ("C", (-0.09, 0, 0.9), (-0.10, -0.18, 0.52), 0.07), ("C", (-0.10, -0.18, 0.52), (-0.10, -0.42, 0.28), 0.06),
                 ("C", (0.21, 0.06, 1.38), (0.24, -0.14, 1.14), 0.05), ("C", (0.24, -0.14, 1.14), (0.22, -0.12, 0.95), 0.045),
                 ("C", (-0.21, 0.06, 1.38), (-0.24, 0.24, 1.20), 0.05), ("C", (-0.24, 0.24, 1.20), (-0.20, 0.38, 1.32), 0.045)]
        if sk:
            parts.append(("E", (0, 0.02, 0.72), (0.24, 0.22, 0.30)))
        m = L.mat(f"Folk845_{v}", srgb(cols[v * 2]), 0.85)
        ob = L.mb_figure(f"Folk845_proto{v}", parts, m, res=0.04)
        proto.append(ob)
    obs = []
    for i in range(n):
        src = proto[i % 3]
        ob = src.copy() if i >= 3 else src
        if i >= 3:
            ob.data = src.data.copy()
            ob.data.materials.clear(); ob.data.materials.append(L.mat(f"Folk845_c{i}", srgb(rnd.choice(cols)), 0.85))
            bpy.context.scene.collection.objects.link(ob)
        x = avenue_x(p0.y) + rnd.uniform(-5.5, 5.5)
        y = p0.y + rnd.uniform(14, 75)
        ob.location = (x, y, L.height(x, y) + 0.1)
        ob.rotation_euler = (0, 0, rnd.uniform(-0.35, 0.35))
        s = rnd.uniform(0.92, 1.08); ob.scale = (s, s, s)
        obs.append(ob)
    coll_link(obs, coll)
    return obs


def build_armored(coll):
    import shifters as SH
    t = time.time()
    rig = SH.make_armored("ArmoredTitan")
    place(rig, ARMORED_XY[0] + avenue_x(ARMORED_XY[1]), ARMORED_XY[1], yaw_towards(0, 1))
    charge_pose(rig)
    rig.rotation_euler.x = float(os.environ.get("ARM_TILT", "0.2"))     # whole-body forward lean of the charge
    coll_link(tree_of(rig), coll)
    STATE["armored"] = rig
    try:
        footfall_dust(rig, coll)
    except Exception as ex:
        traceback.print_exc(); log("armored dust failed", repr(ex))
    try:
        fleeing_people(coll, Vector(rig.location), int(os.environ.get("FOLK_N", "16")))
    except Exception as ex:
        traceback.print_exc(); log("fleeing people failed", repr(ex))
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


# ------------------------------------------------------------------------------------------ skin + groves
SKIN_TARGETS = ["#E2BFA6", "#C99A78", "#C27C6C", "#D2AA8C"]     # bible 3.2 pale peach / peach-tan / ruddy pink


def calm_skins(rigs):
    """Pull pure-titan skins from pure_titans' saturated orange toward the bible's peach range: a per-channel
    multiply (target / preset skin) plus a mild desaturation inserted before Base Color, roughness 0.85."""
    import pure_titans as PT
    done = set()
    for k, rig in enumerate(rigs):
        pre = PT.PRESETS.get(rig.get("pure_preset") or "", {})
        sk = pre.get("skin", (0.70, 0.32, 0.18))
        tgt = srgb(SKIN_TARGETS[k % len(SKIN_TARGETS)])
        for ch in rig.children:
            for ma in (ch.data.materials if ch.type == "MESH" else []):
                if not ma or "_skin" not in ma.name or ma.name in done or not ma.use_nodes:
                    continue
                done.add(ma.name)
                nt = ma.node_tree
                b = next((n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"), None)
                if not b or not b.inputs["Base Color"].is_linked:
                    continue
                src = b.inputs["Base Color"].links[0].from_socket
                mul = nt.nodes.new("ShaderNodeVectorMath"); mul.operation = "MULTIPLY"
                mul.inputs[1].default_value = tuple(min(2.0, t / max(1e-3, s)) for t, s in zip(tgt, sk))
                hs = nt.nodes.new("ShaderNodeHueSaturation"); hs.inputs["Saturation"].default_value = float(os.environ.get("SKIN_SAT", "0.85"))
                nt.links.new(src, mul.inputs[0]); nt.links.new(mul.outputs[0], hs.inputs["Color"])
                nt.links.new(hs.outputs["Color"], b.inputs["Base Color"])
                b.inputs["Roughness"].default_value = 0.85
                try:
                    b.inputs["Specular IOR Level"].default_value = 0.25
                except Exception:
                    pass


def conifer_groves(coll, spots, seed=5):
    """Clumps of the scene's own conifer prototypes (TreeVariants T07..T12) to frame the meadow shots."""
    rnd = random.Random(seed)
    protos = [o.data for o in bpy.data.objects if o.name[:1] == "T" and o.name[1:].isdigit() and int(o.name[1:]) >= 7
              and o.type == "MESH"]
    if not protos:
        log("no conifer prototypes found"); return []
    obs = []
    for gi, (cx, cy, n, rad) in enumerate(spots):
        for i in range(n):
            a = rnd.uniform(0, 6.28); d = rad * math.sqrt(rnd.random())
            x, y = cx + math.cos(a) * d, cy + math.sin(a) * d
            ob = bpy.data.objects.new(f"Grove{gi}_{i}", rnd.choice(protos))
            s = rnd.uniform(1.2, 2.0)
            ob.location = (x, y, L.height(x, y) - 0.3); ob.scale = (s, s, s * rnd.uniform(0.95, 1.2))
            ob.rotation_euler = (0, 0, rnd.uniform(0, 6.28))
            coll.objects.link(ob); obs.append(ob)
    return obs


# ------------------------------------------------------------------------------------------ entry point
def build(M, year, ctx):
    t0 = time.time()
    coll = L.new_coll("Cast845")
    log(f"event state: {EVENT}")
    if EVENT in ("intact", "colossal"):
        STATE["outside"] = build_outside(coll)
        conifer_groves(coll, GROVES)
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
        rest = [s[:5] + ((-s[3], OG.y - s[4]),) + s[6:] for s in OUTSIDE[:6]]
        STATE["outside"] = _copies_of(STATE.get("inflow", []), rest, coll)
    try:
        calm_skins(STATE.get("outside", []) + STATE.get("inflow", []))
    except Exception as ex:
        traceback.print_exc(); log("skin recolour failed", repr(ex))
    bpy.context.scene.frame_set(1)
    if dutch_roll not in bpy.app.handlers.render_pre:
        bpy.app.handlers.render_pre.append(dutch_roll)
    n = sum(1 for o in bpy.data.objects if o.type == "ARMATURE")
    log(f"{n} titan rigs in the scene")
    log(f"cast built in {time.time() - t0:.1f}s")


def dutch_roll(scene, *a):
    """Camera roll for cams that ask for it (scene.py's camera() takes only loc / look-at / lens)."""
    r = STATE.pop("roll", 0.0)
    cam = scene.camera
    if cam and r:
        cam.rotation_euler = (cam.matrix_world.to_quaternion() @ Quaternion((0, 0, 1), math.radians(r))).to_euler()
        log(f"dutch roll {r} deg on {cam.name}")


# ------------------------------------------------------------------------------------------ cameras
def aim(loc, pt, u, v, lens):
    """Look-at point so that world point pt lands at frame offset (u, v) in [-1, 1] (u right, v up; 16:9,
    36 mm sensor width).  Small-angle composition helper for the fixed-roll camera."""
    loc, pt = Vector(loc), Vector(pt)
    d = pt - loc
    yaw = math.atan2(d.y, d.x); pitch = math.atan2(d.z, d.xy.length)
    yaw += math.atan(u * 18.0 / lens)
    pitch -= math.atan(v * 10.125 / lens)
    f = Vector((math.cos(pitch) * math.cos(yaw), math.cos(pitch) * math.sin(yaw), math.sin(pitch)))
    return tuple(loc + f * 100.0)


def _head():
    return STATE.get("colossal_head") or Vector((COLOSSAL_X, -735.0, 55.0))


def _cam_colossal_town():
    """Timelapse 'from the streets' shot (not a thumbnail): street-level camera ~315 m north of the head on the
    main avenue, 70 mm; roofs fill the lower ~30 %, the wall top line sits at ~45 % of the frame height and the
    plume rises out of the top of the frame."""
    h = _head()
    back = float(os.environ.get("CT_BACK", "315"))
    y = h.y + back
    x = avenue_x(y) + float(os.environ.get("CT_DX", "4"))
    loc = (x, y, L.height(x, y) + float(os.environ.get("CT_Z", "6")))
    lens = float(os.environ.get("CT_LENS", "70"))
    wt = (h.x, L.district_ymin(h.x), WALL_TOP)
    return loc, aim(loc, wt, float(os.environ.get("CT_U", "0.12")), float(os.environ.get("CT_V", "-0.10")), lens), lens


def _cam_colossal_closeup():
    """Thumbnail: long lens from a rooftop deep in the town.  Wall top at ~30 % from the bottom, the head left
    of centre so the gripping hand (west = frame right) is in frame; the gatehouse stays out of frame."""
    h = _head()
    lens = float(os.environ.get("CU_LENS", "135"))
    off = [float(v) for v in os.environ.get("CU_OFF", "40,420,-12").split(",")]
    loc = (h.x + off[0], h.y + off[1], h.z + off[2])
    wt = (h.x, L.district_ymin(h.x), WALL_TOP)
    return loc, aim(loc, wt, float(os.environ.get("CU_U", "-0.12")), float(os.environ.get("CU_V", "-0.40")), lens), lens


def _cam_colossal_side():
    """Outside, south-west, 60 mm, slightly raised: the 60 m figure fills ~half the frame height."""
    h = _head()
    d = float(os.environ.get("CS_DIST", "300"))
    a = math.radians(float(os.environ.get("CS_AZ", "225")))
    loc = (h.x + math.cos(a) * d, h.y + math.sin(a) * d, float(os.environ.get("CS_Z", "28")))
    lens = float(os.environ.get("CS_LENS", "60"))
    return loc, aim(loc, (h.x, h.y, 31.0), 0.0, float(os.environ.get("CS_V", "0.0")), lens), lens


def _cam_armored_gate():
    """Street level 40 m behind the Armored, 6 m to the side, 24 mm: it fills ~40 % of the frame height,
    charging at the inner gate."""
    r = STATE.get("armored")
    p = Vector(r.location) if r else Vector((0, ARMORED_XY[1], 0))
    back = float(os.environ.get("AG_BACK", "40")); dx = float(os.environ.get("AG_DX", "6"))
    x, y = p.x + dx, p.y - back
    loc = (x, y, L.height(x, y) + float(os.environ.get("AG_Z", "4")))
    lens = float(os.environ.get("AG_LENS", "24"))
    return loc, (avenue_x(-10.0) - 1.0, 0.0, float(os.environ.get("AG_TZ", "12"))), lens


def _cam_armored_front():
    """Low (12 m) in front of the Armored looking south down the avenue, 28 mm, 6 deg Dutch tilt: townsfolk
    fleeing toward the camera, the Armored charging behind them, pure titans streaming in further back."""
    r = STATE.get("armored")
    p = Vector(r.location) if r else Vector((0, ARMORED_XY[1], 0))
    STATE["roll"] = float(os.environ.get("AF_ROLL", "6"))
    y = p.y + float(os.environ.get("AF_DIST", "95"))
    x = avenue_x(y) + 2.0
    loc = (x, y, L.height(x, y) + float(os.environ.get("AF_Z", "12")))
    return loc, (p.x - 1, p.y - 25, 7.0), float(os.environ.get("AF_LENS", "28"))


TO_CAM = (-30.0, -975.0)


def _cam_titans_outside():
    """Low (3 m) on the meadow ~255 m south of the outer gate, 35 mm; a big pure titan walking away toward the
    wall in the foreground, others in the thirds, conifer groves framing the sides."""
    x, y = TO_CAM
    loc = (x, y, L.height(x, y) + 3.0)
    return loc, (0.0, -720.0, L.height(x, y) + 20.0), 35


CAMS = {
    "titans_outside": _cam_titans_outside,
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
