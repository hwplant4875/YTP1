"""fx845: per-frame destruction FX for the 845 kick. Built by states845 (AOT_STATE=kicked|armored|night);
this module only holds the registry and the per-frame update functions.

PER-FRAME API (one Blender session, build once, then for every frame before bpy.ops.render.render):
    import fx845                       # (sys.modules["fx845"] once states845 is loaded)
    fx845.update(t)                    # t = SECONDS AFTER THE KICK (the foot hits the gate), float, any order.
    fx845.update_frame(f, fps=30, f_kick=0)   # same, in frames: t = (f - f_kick) / fps
  t < 0   -> intact: gate door shown, breach boolean off, no rubble/ruins/fires, every Town house alive.
  update(t) = set_kick(t) + set_arc(t) + set_impacts(t); each can be called on its own:
    set_kick(t)     breach boolean + door, gate rubble sweeping in (0-0.5 s), breach dust burst, door-debris spray
    set_arc(t)      thrown gate blocks (smaller, ~5-8 m) and small stones on ballistic arcs with spin, skid on
                    landing, dust puffs trailing each block
    set_impacts(t)  per impact: dust/smoke puff burst, crater + rubble splash, houses collapsing progressively
                    (walls sink/tilt/crumple, roof halves cave in, rubble mound rises under the dust, 0.5-1.4 s),
                    Town instance hidden at the collapse start, fires / smoke columns growing afterwards.
  Everything is a pure function of t (no simulation state), so frames can be rendered in any order.
  Timeline: blocks launch t = 0-0.25 s and land t ~ 1.2-3.1 s (farther = later; times() lists them);
  houses swept by the gate debris fan collapse t ~ 0.05-1.5 s; all dust has faded by ~t = 9 s.
Cost: ~500-700 small objects with shared meshes (puffs are 80-face icospheres with a transparent soft-edged
  material, no volumes are created or animated per frame); Cycles transparent_max_bounces is raised to 32.
Env (read by states845):
  AOT_ARC_T=0..1   old static scripts: the build ends with update(AOT_ARC_T * times_end()); unset = settled (t=60).
  AOT_FLIGHT_K     multiplies block flight durations (default 1.0; 0.7 = snappier, 1.4 = floatier).
  AOT_FX_PUFFS     multiplies puff counts (default 1; 0 = no puffs).
"""
import bpy, bmesh, math, os, random
from mathutils import Vector, Matrix, Quaternion

Z = Vector((0, 0, 1))
REG = {}

def reset():
    REG.clear()
    REG.update({"appear": [], "mods": [], "blocks": [], "puffs": [], "houses": [], "town": [], "town_g": None,
                "flight": []})
reset()

def _cl(u):
    return 0.0 if u < 0 else 1.0 if u > 1 else u

def _ease(u):
    u = _cl(u); return u * u * (3 - 2 * u)

def _out(u):
    u = _cl(u); return 1 - (1 - u) ** 3

def _vis(ob, on):
    if ob.hide_render != (not on):
        ob.hide_render = not on; ob.hide_viewport = not on
        for c in ob.children:
            c.hide_render = not on; c.hide_viewport = not on

def puff_k():
    return float(os.environ.get("AOT_FX_PUFFS", "1"))

def flight_k():
    return float(os.environ.get("AOT_FLIGHT_K", "1"))

# ---------------------------------------------------------------- registration
def add_appear(ob, t_on, dur=0.0, s0=(1, 1, 1), t_off=None):
    """Hidden before t_on (and from t_off); grows from scale*s0 to scale over dur seconds (ease-out)."""
    if ob is None:
        return
    REG["appear"].append((ob, t_on, dur, Vector(ob.scale), Vector(s0), t_off))

def add_kick_modifier(mod):
    REG["mods"].append(mod)

def add_block(ob, launch, T, p0, p1, hmax, skid, seed, spin=(1.5, 4.0), trail=0, coll=None, col=None):
    rr = random.Random(seed)
    ax = Vector((rr.gauss(0, 1), rr.gauss(0, 1), rr.gauss(0, 1))).normalized()
    q0 = Quaternion(Vector((rr.gauss(0, 1), rr.gauss(0, 1), rr.gauss(0, 1))).normalized(), rr.uniform(0, 6.28))
    b = {"ob": ob, "launch": launch, "T": T, "p0": Vector(p0), "p1": Vector(p1), "h": hmax, "skid": Vector(skid),
         "ax": ax, "w": rr.uniform(*spin) * rr.choice((-1, 1)), "q0": q0}
    ob.rotation_mode = "QUATERNION"
    REG["blocks"].append(b)
    if trail and coll is not None:
        n = max(0, int(round(trail * puff_k())))
        for k in range(n):
            ts = launch + T * (k + 0.6) / (n + 0.5)
            p, _ = block_at(b, ts)
            add_puff(coll, p, ts, Vector((0, 0, 0)), 0.3, 0.6, 1.2 + 0.08 * hmax ** 0.5, 2.5 + 0.05 * hmax ** 0.5,
                     rr.uniform(1.0, 1.6), col or (0.46, 0.35, 0.18), 0.55)
    return b

def add_puff(coll, c, t0, v, tau, rise, r0, r1, life, col, a0=0.85):
    ob = bpy.data.objects.new("Puff", puff_mesh())
    ob.location = c
    for a in ("visible_shadow", "visible_diffuse", "visible_glossy", "visible_transmission", "visible_volume_scatter"):
        setattr(ob, a, False)
    coll.objects.link(ob)
    REG["puffs"].append({"ob": ob, "t0": t0, "c": Vector(c), "v": Vector(v), "tau": tau, "rise": rise,
                         "r0": r0, "r1": r1, "life": life, "col": tuple(col), "a0": a0})
    return ob

def add_burst(coll, center, R, t0, n, rnd, col=(0.46, 0.35, 0.18), dark=(0.13, 0.11, 0.1), dark_frac=0.25,
              speed=(5, 16), up=(0.25, 0.9), life=(2.5, 4.5), dirv=None, cone=1.0, rise=(1.0, 3.0), a0=1.0):
    """n puffs bursting from center: radial (or along dirv within cone) speed decaying with tau, rising, growing
    from 0.35 R to 1.1-2.2 R and fading out over their life."""
    n = int(round(n * puff_k()))
    for k in range(n):
        if dirv is None:
            a = rnd.uniform(0, 6.28)
            d = Vector((math.cos(a), math.sin(a), rnd.uniform(*up))).normalized()
        else:
            d = (Vector(dirv).normalized() + Vector((rnd.gauss(0, cone), rnd.gauss(0, cone), abs(rnd.gauss(0, cone)) * up[1]))).normalized()
        c = Vector(center) + Vector((rnd.gauss(0, R * 0.25), rnd.gauss(0, R * 0.25), rnd.uniform(0, R * 0.3)))
        r1 = R * rnd.uniform(1.1, 2.2)
        cl = dark if rnd.random() < dark_frac else tuple(x * rnd.uniform(0.85, 1.12) for x in col)
        add_puff(coll, c, t0 + rnd.uniform(0, 0.12), d * rnd.uniform(*speed), rnd.uniform(0.25, 0.5),
                 rnd.uniform(*rise), R * 0.35, r1, rnd.uniform(*life), cl, a0 * rnd.uniform(0.75, 1.0))

def add_town(ob, idx, orig, year, t_kill):
    REG["town"].append((ob, idx, orig, year, t_kill)); REG["town_g"] = None

def add_house(parts, ruin, t0, dur, rnd, h):
    """parts: [(ob, M_base, kind, sign, eave)] (kind 'wall' | 'roof'); ruin: object grown in under the dust."""
    a = rnd.uniform(0, 6.28)
    REG["houses"].append({"parts": parts, "ruin": ruin, "t0": t0, "dur": dur, "h": h,
                          "tax": Vector((math.cos(a), math.sin(a), 0)), "tilt": rnd.uniform(0.12, 0.35),
                          "roof": rnd.uniform(0.8, 1.25), "seed": rnd.uniform(0, 100)})
    if ruin is not None:
        add_appear(ruin, t0 + dur * 0.25, dur * 0.85, (0.85, 0.85, 0.05))

def add_flight(launch, land):
    REG["flight"].append((launch, land))

def times():
    """[(launch, land)] of the big blocks, seconds after the kick."""
    return sorted(REG["flight"], key=lambda x: x[1])

def times_end():
    return max([l for _, l in REG["flight"]] or [2.0])

# ---------------------------------------------------------------- shared assets
_PM = {}
def puff_mat():
    if "m" in _PM:
        return _PM["m"]
    m = bpy.data.materials.new("FxPuff"); m.use_nodes = True
    nt = m.node_tree; N = nt.nodes; Ln = nt.links
    N.remove(N["Principled BSDF"])
    oi = N.new("ShaderNodeObjectInfo")
    lw = N.new("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = 0.5
    tc = N.new("ShaderNodeTexCoord")
    off = N.new("ShaderNodeVectorMath"); off.operation = "SCALE"
    off.inputs[0].default_value = (17.3, 41.1, 7.7)
    Ln.new(oi.outputs["Random"], off.inputs["Scale"])
    add = N.new("ShaderNodeVectorMath"); add.operation = "ADD"
    Ln.new(tc.outputs["Object"], add.inputs[0]); Ln.new(off.outputs[0], add.inputs[1])
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 1.6; nz.inputs["Detail"].default_value = 3.0
    Ln.new(add.outputs[0], nz.inputs["Vector"])
    def mth(op, a, b, clamp=False):
        n = N.new("ShaderNodeMath"); n.operation = op; n.use_clamp = clamp
        for i, x in enumerate((a, b)):
            if isinstance(x, (int, float)):
                n.inputs[i].default_value = x
            else:
                Ln.new(x, n.inputs[i])
        return n.outputs[0]
    soft = mth("POWER", mth("SUBTRACT", 1.0, lw.outputs["Facing"], True), 0.9)        # 1 at the centre, 0 at the rim
    wisp = mth("ADD", mth("MULTIPLY", nz.outputs["Fac"], 2.4), -0.2)
    alpha = mth("MULTIPLY", mth("MULTIPLY", soft, wisp, True), oi.outputs["Alpha"], True)
    geo = N.new("ShaderNodeNewGeometry")
    alpha = mth("MULTIPLY", alpha, mth("SUBTRACT", 1.0, geo.outputs["Backfacing"]))     # front shell only
    dif = N.new("ShaderNodeBsdfDiffuse"); Ln.new(oi.outputs["Color"], dif.inputs["Color"])
    em = N.new("ShaderNodeEmission"); Ln.new(oi.outputs["Color"], em.inputs["Color"]); em.inputs["Strength"].default_value = 0.45
    adds = N.new("ShaderNodeAddShader"); Ln.new(dif.outputs[0], adds.inputs[0]); Ln.new(em.outputs[0], adds.inputs[1])
    tr = N.new("ShaderNodeBsdfTransparent")
    mx = N.new("ShaderNodeMixShader")
    Ln.new(alpha, mx.inputs[0]); Ln.new(tr.outputs[0], mx.inputs[1]); Ln.new(adds.outputs[0], mx.inputs[2])
    Ln.new(mx.outputs[0], N["Material Output"].inputs["Surface"])
    for a, v in (("surface_render_method", "BLENDED"), ("blend_method", "BLEND"), ("use_backface_culling", True)):
        try:
            setattr(m, a, v)
        except (AttributeError, TypeError):
            pass
    _PM["m"] = m
    return m

def puff_mesh():
    if "me" in _PM:
        return _PM["me"]
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0)
    for f in bm.faces:
        f.smooth = True
    me = bpy.data.meshes.new("FxPuff"); bm.to_mesh(me); bm.free()
    me.materials.append(puff_mat())
    _PM["me"] = me
    sc = bpy.context.scene
    try:
        sc.cycles.transparent_max_bounces = max(sc.cycles.transparent_max_bounces, 32)
    except AttributeError:
        pass
    return me

# ---------------------------------------------------------------- town instances -> collapse proxies
def town_instances(name="Town"):
    """{(round x, round y): [(mesh, matrix_world)]} of the evaluated Town scatter (call before any kill is committed)."""
    out = {}
    dg = bpy.context.evaluated_depsgraph_get()
    for inst in dg.object_instances:
        if inst.is_instance and inst.parent and inst.parent.original.name == name and inst.instance_object:
            M = inst.matrix_world.copy()
            out.setdefault((round(M.translation.x), round(M.translation.y)), []).append((inst.instance_object.original.data, M))
    return out

def find_instance(inst, x, y, tol=0.6):
    """(mesh, matrix) of the Town instance at (x, y) or None."""
    best, bd = None, tol
    for gx in (round(x) - 1, round(x), round(x) + 1):
        for gy in (round(y) - 1, round(y), round(y) + 1):
            for me, M in inst.get((gx, gy), ()):
                d = math.hypot(M.translation.x - x, M.translation.y - y)
                if d < bd:
                    best, bd = (me, M), d
    return best

_SPLIT = {}
def _split_house(me):
    """Walls (+ gables, windows) and the two roof halves of a house_mesh; eave hinge per half."""
    if me.name in _SPLIT:
        return _SPLIT[me.name]
    roof_mi = 1
    out = []
    for kind, sign in (("wall", 0), ("roof", -1), ("roof", 1)):
        bm = bmesh.new(); bm.from_mesh(me)
        keep = []
        for f in bm.faces:
            c = f.calc_center_median()
            isroof = f.material_index == roof_mi and abs(c.y) > 0.3 and abs(f.normal.z) > 0.2
            if kind == "wall":
                ok = not isroof
            else:
                ok = isroof and (c.y > 0) == (sign > 0)
            if not ok:
                keep.append(f)
        bmesh.ops.delete(bm, geom=keep, context="FACES")
        vs = [v.co.copy() for v in bm.verts]
        m2 = bpy.data.meshes.new(f"{me.name}_{kind}{sign}"); bm.to_mesh(m2); bm.free()
        for m in me.materials:
            m2.materials.append(m)
        eave = None
        if kind == "roof" and vs:
            eave = (max(abs(v.y) for v in vs) * sign, min(v.z for v in vs))
        out.append((m2, kind, sign, eave, max((v.z for v in vs), default=10.0)))
    _SPLIT[me.name] = out
    return out

def house_proxy(coll, me, M, name):
    parts, h = [], 1.0
    for m2, kind, sign, eave, top in _split_house(me):
        ob = bpy.data.objects.new(name + "_" + kind + str(sign), m2)
        ob.matrix_world = M
        coll.objects.link(ob)
        parts.append((ob, M.copy(), kind, sign, eave))
        h = max(h, top)
    return parts, h

# ---------------------------------------------------------------- per-frame evaluation
def block_at(b, t):
    """(location, quaternion) of a thrown block at t (None before launch)."""
    tt = t - b["launch"]
    if tt < 0:
        return None, None
    T = b["T"]
    if tt < T:
        s = tt / T
        p = b["p0"].lerp(b["p1"], s)
        p.z = b["p0"].z * (1 - s) + b["p1"].z * s + 4 * b["h"] * s * (1 - s)
        ang = b["w"] * tt
    else:
        k = 1 - math.exp(-(tt - T) / 0.16)
        p = b["p1"] + b["skid"] * k
        ang = b["w"] * (T + 0.12 * k)
    return p, Quaternion(b["ax"], ang) @ b["q0"]

def set_kick(t):
    on = t >= 0
    for mod in REG["mods"]:
        if mod.show_render != on:
            mod.show_render = on; mod.show_viewport = on

def set_arc(t):
    for b in REG["blocks"]:
        p, q = block_at(b, t)
        _vis(b["ob"], p is not None)
        if p is not None:
            b["ob"].location = p; b["ob"].rotation_quaternion = q

def _set_puffs(t):
    for p in REG["puffs"]:
        tt = t - p["t0"]
        on = 0 <= tt < p["life"]
        _vis(p["ob"], on)
        if not on:
            continue
        c = p["c"] + p["v"] * (p["tau"] * (1 - math.exp(-tt / p["tau"]))) + Z * (p["rise"] * tt)
        r = p["r0"] + (p["r1"] - p["r0"]) * _out(tt / (p["life"] * 0.7))
        a = p["a0"] * _cl(tt / 0.07) * (1 - _ease(tt / p["life"])) ** 1.3
        ob = p["ob"]
        ob.location = c; ob.scale = (r, r, r * 0.82); ob.color = (*p["col"], a)

def _set_appear(t):
    for ob, t_on, dur, S, s0, t_off in REG["appear"]:
        on = t >= t_on and (t_off is None or t < t_off)
        _vis(ob, on)
        if on and dur > 0:
            u = _out((t - t_on) / dur)
            ob.scale = (S.x * (s0.x + (1 - s0.x) * u), S.y * (s0.y + (1 - s0.y) * u), S.z * (s0.z + (1 - s0.z) * u))

def _set_town(t):
    if REG["town_g"] is None:
        g = {}
        for ob, i, orig, yr, tk in REG["town"]:
            g.setdefault(ob.name, []).append((i, orig, yr, tk))
        REG["town_g"] = g
    for name, lst in REG["town_g"].items():
        ob = bpy.data.objects.get(name)
        if not ob:
            continue
        att = ob.data.attributes["dead"]
        arr = [0.0] * len(att.data); att.data.foreach_get("value", arr)
        ch = False
        for i, orig, yr, tk in lst:
            v = yr if t >= tk else orig
            if arr[i] != v:
                arr[i] = v; ch = True
        if ch:
            att.data.foreach_set("value", arr); ob.data.update()

def _set_houses(t):
    for H in REG["houses"]:
        u = (t - H["t0"]) / H["dur"]
        on = 0 <= u < 1.0
        for ob, M, kind, sign, eave in H["parts"]:
            _vis(ob, on)
        if not on:
            continue
        e = _cl(u) ** 1.7                                       # slow start, accelerating (gravity-ish)
        h = H["h"]
        shake = 0.25 * (1 - u) * math.sin(u * 55 + H["seed"])
        Mw = (Matrix.Translation((shake, 0, -h * 0.62 * e)) @ Matrix.Rotation(H["tilt"] * e, 4, H["tax"])
              @ Matrix.Diagonal((1 + 0.12 * e, 1 + 0.12 * e, 1 - 0.65 * e, 1)))
        er = _cl(u * 1.35) ** 2
        for ob, M, kind, sign, eave in H["parts"]:
            if kind == "roof" and eave:
                hy, hz = eave
                Mh = (Matrix.Translation((0, hy, hz)) @ Matrix.Rotation(sign * 1.15 * H["roof"] * er, 4, "X")
                      @ Matrix.Translation((0, -hy, -hz - 1.5 * er)))
                ob.matrix_world = M @ Mw @ Mh
            else:
                ob.matrix_world = M @ Mw

def set_impacts(t):
    _set_town(t)
    _set_houses(t)
    _set_puffs(t)
    _set_appear(t)

def update(t):
    t = float(t)
    set_kick(t); set_arc(t); set_impacts(t)

def update_frame(f, fps=30.0, f_kick=0):
    update((f - f_kick) / float(fps))
