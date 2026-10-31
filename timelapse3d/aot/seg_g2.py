"""g2 ARMORED RAM + BURNING SHIGANSHINA + FERRIES (SCENE_BIBLE_v2 B.g2 + D6/D7/D21, 32.0 s local, frame W = Shiganshina world).
Driven by aot/render_seg.py with SEG_FRAME=W (SEG=g2 bash render_seg.sh builds scene.py's own Shiganshina 845 with g1's
plug-ins, see render_seg.sh).  Every frame is a pure function of the local time t (0..32).  VIDEO CLOCK: segtime.TMAP["g2"]
(linear, slope 2) -> 16.0 s of video; Reiner runs 1.5x faster in LOCAL time = 3x on screen vs v3 (owner 10/27 07:34).

Story (local seconds; all times in BEATS below, the ONE re-time place; video = local / 2):
  0     g1 seam at rest (camera on the Yeager ruin), the Armored already running up the avenue at y -400 (30 -> 43.5 m/s)
  0-4.4 swoop NE over the roofs onto the avenue; from 4.4 the camera is LOCKED on him (front three-quarter, ~150 m)
        The apron, the avenue ahead of him and the gate road are ALREADY EVACUATED (owner 07:34): no fleeing column, only
        a few distant stragglers far north on the gate road; the Garrison gun line, the wall guns and the crews stay.
  4.3-5.35 wall-top guns (x -25, +25, -60, +60): ricochets on the 1st / 3rd shot (gold streak + sparks), misses 2nd / 4th
  6.0 first field volley, 6.15 a shell glances off his FACE; 7.33 second volley + the last wall guns (x +-95)
  7.87 Garrison run across the apron, the crest leaf (drop gate) starts sliding down; 8.27 the gun crews scatter,
  8.53 a carriage is kicked over; 8.55-9.0 RIGHT-shoulder drop (torso twist, root never rotates)
  9.0 IMPACT (small zoom-in 50 -> 58 mm, side three-quarter): flash, tall narrow dark arch breach 13 x 25.5 m through the
       full depth, wings survive, cracks; 50 chunks fan north (8 big ones arc 60-80 m over the wall), a soldier flung
  9.0-10.9 he SLIDES through on momentum to y +46: feet braced and skidding, two dust furrows, rubble ploughed ahead,
       a splash over the water strip; the ochre dust ball grows to ~40 m
  10.9-12.0 he straightens; 12-32 stands steaming in the haze (seen from the north 12-15.6, small zoom-in)
  15.6-22.4 the camera climbs NW: AERIAL of BURNING Shiganshina at dusk (fires spreading roof to roof since 2 s, dense smoke
       columns bending west, fire glow on the houses), the breach and the steaming Armored small in the foreground
  22.4-32 swing east over the canal / quays / ferries and north toward Trost: hand-off to g3 (seam K15, unchanged)
Camera: camkeys.G2 (v5) through camchan.CamPath (seam in at rest, seam out = segtime g2_g3 velocity, look-at at rest).
Smoke over Shiganshina bends WEST (wind -2.2, +0.45; bible AUDIT CORRECTIONS 2).  Hamlet east-heavy = g1_set.
"""
import math, os, random, sys, time
import numpy as np

try:
    import bpy, bmesh
    from mathutils import Vector, Matrix, Euler, noise
except ImportError:                       # pure-python use (camera checks)
    bpy = None

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import camchan
import camkeys
import segtime

DUR = segtime.DUR["g2"]                   # 32.0
FRAME = "W"

# ====================================================================== BEATS (the ONE re-time place, local seconds)
BEATS = dict(
    run_v=43.5, run_v0=30.0, run_acc=1.0,  # m/s: 1.5x v3's 29 (3x on screen with the 2x clock); v0 at t 0, full speed by 1.0
    lock=4.4,                              # framing locked on him from here (camkeys K2)
    wall_fire=(4.3, 4.65, 5.0, 5.35),      # wall-top guns x -25, +25, -60, +60 (1st + 3rd ricochet, 2nd + 4th miss)
    volley1=6.0, f3_castoff=10.0, volley2=7.33,   # face hit = volley1 + SHELL_T - 0.05 (6.15)
    apron_run=7.87, leaf=(7.87, 9.0), scatter=8.27, kick_carriage=8.53,
    ram=(8.55, 9.0), impact=9.0, slide=(9.0, 10.87), straighten=(10.87, 12.0), stand=(12.0, 32.0),
    steam=10.4, light_swing=(9.0, 12.5), night=(10.5, 17.0),  # v5: dusk -> NIGHT during/after the breach (end = g3 t 0)
    vanish=(11.1, 12.1),                   # v5 (owner): steam burst, the body sinks / dissolves into steam, gone in ~1 s
    fires=(2.0, 16.0),                     # the town catches fire roof to roof (new columns ignite over this span)
    aerial=(17.0, 24.0),                   # the burning town fills the frame (camkeys K10-K11)
)
T_IMP = BEATS["impact"]
RUN_V = BEATS["run_v"]                     # m/s
STEP_LEN = 21.0                            # longer bounding stride at the faster run (~2.1 steps/s local)
SLIDE_T = BEATS["slide"][1] - BEATS["slide"][0]
GATE_FRONT_S = -13.0                      # brick gatehouse fronts y -13 (south) / +13 (north)
HOLE_HW, HOLE_H = 6.5, 25.5               # breach: tall narrow pointed arch 13 x 25.5 m
WIND = (-2.2, 0.45)                       # west wind (bible AUDIT 2)
G = 9.81

def smooth(a, b, t):
    u = min(1.0, max(0.0, (t - a) / (b - a))); return u * u * (3 - 2 * u)

def arm_y(t):
    """Run front of the Armored (his centre) on the avenue x = 0: v0 -> run_v over run_acc s, contact (y -15) at the
    impact beat, then the slide.  Start y follows from the beats (-399.75 for the defaults, = v3's -400)."""
    if t <= T_IMP:
        ta = BEATS["run_acc"]; v0 = BEATS["run_v0"]
        if t >= ta:
            return -15.0 - RUN_V * (T_IMP - t)
        a = (RUN_V - v0) / ta; y1 = -15.0 - RUN_V * (T_IMP - ta)
        return y1 - (v0 * (ta - t) + 0.5 * a * (ta * ta - t * t))
    u = min(t - T_IMP, SLIDE_T)               # v = V (1 - (u/T)^3): holds speed, then digs in and stops at y ~ +46
    return -15.0 + RUN_V * (u - u ** 4 / (4 * SLIDE_T ** 3))

def arm_v(t, h=1e-3):
    return (arm_y(t + h) - arm_y(t - h)) / (2 * h)

def t_at_y(y):
    """Inverse of arm_y on the run (bisection)."""
    lo, hi = 0.0, T_IMP + SLIDE_T
    for _ in range(50):
        m = (lo + hi) / 2
        if arm_y(m) < y: lo = m
        else: hi = m
    return (lo + hi) / 2

CAM = camchan.CamPath(**camkeys.cam("g2"))
TRACK = {"ARMORED TITAN": lambda t: (0.0, arm_y(t), 17.0)}

def cam_shake(t):
    """<= 0.25 deg for ~0.3 s local at the impact (A3 shake rule)."""
    if not (T_IMP <= t < T_IMP + 0.3) or bpy is None:
        return (0.0, 0.0)
    a = math.radians(0.25) * (1 - (t - T_IMP) / 0.3)
    return (a * noise.noise(Vector((t * 37, 0.3, 1.1))), a * noise.noise(Vector((2.1, t * 33, 0.7))))

# ====================================================================== helpers
L = None; G1 = None; PK = None; SMC = None
S = {}                                    # everything built (objects, arrays)

def lin(h):
    h = h.lstrip("#"); c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c)

def gz(x, y):
    """Ground / paving height (people_kit convention: +0.16 inside the district)."""
    g = L.height(x, y)
    if L.in_district(x, y, 0.0):
        g = max(g, 0.0) + 0.16
    return g

def emit_mat(name, col, strength=6.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    N = m.node_tree.nodes; Ln = m.node_tree.links
    N.remove(N["Principled BSDF"])
    em = N.new("ShaderNodeEmission"); em.inputs["Color"].default_value = (*col, 1); em.inputs["Strength"].default_value = strength
    Ln.new(em.outputs[0], N["Material Output"].inputs["Surface"])
    m["toon"] = 1
    return m

def put(name, bm, mats, coll):
    return L.obj_from_bm(name, bm, mats, coll)

def poly_face(bm, pts2, y, mi=0, flip=False):
    """Flat n-gon in the xz plane at depth y (pts2 = [(x, z)])."""
    vs = [bm.verts.new((x, y, z)) for x, z in pts2]
    f = bm.faces.new(vs[::-1] if flip else vs); f.material_index = mi
    return f

def arch_pts(hw, h, spring_frac=0.6, n=10, z0=0.0):
    """Pointed (gothic) arch outline, bottom-left -> up -> apex -> down -> bottom-right."""
    zs = z0 + h * spring_frac; top = z0 + h
    R_ = ((top - zs) ** 2 + (2 * hw) ** 2) / (2 * 2 * hw) if hw > 0 else 1.0     # two arcs centred on the opposite side
    left = [(-hw, z0), (-hw, zs)]
    for k in range(1, n):
        u = k / n; z = zs + (top - zs) * u
        x = hw - math.sqrt(max(0.0, R_ * R_ - (z - zs) ** 2))               # arc centred at (hw, zs) radius R_
        left.append((max(-hw, min(0.0, x)), z))
    left.append((0.0, top))
    right = [(-x, z) for x, z in left[::-1][1:]]
    return left + right

def arch_hw(z, hw=HOLE_HW, h=HOLE_H, spring_frac=0.55):
    zs = h * spring_frac
    if z <= zs:
        return hw
    if z >= h:
        return 0.0
    R_ = ((h - zs) ** 2 + (2 * hw) ** 2) / (4 * hw)
    return max(0.0, -(hw - math.sqrt(max(0.0, R_ * R_ - (z - zs) ** 2))))

# ====================================================================== the g1 hand-over state (copied from render_g1)
def settle_g1():
    """The scene as g1 leaves it: baked outer breach, terrace lifts, rock lumps, no FireSmoke / crater, Colossal gone,
    the kick FX settled, cast845's standing kit crowd hidden (it fled at the kick)."""
    FX = sys.modules.get("fx845")
    if FX is not None and not any(FX.REG.get(k_) for k_ in ("blocks", "mods", "houses", "appear")):
        FX = None
    S["fx845"] = FX
    if FX:                                   # bake_breach (render_g1): the exact boolean per frame costs ~50 s
        gate = bpy.data.objects.get("OuterGate")
        mods = [m for m in (gate.modifiers if gate else []) if m.type == "BOOLEAN"]
        if mods:
            for m in mods:
                m.show_render = m.show_viewport = True
            bpy.context.view_layer.update()
            dg = bpy.context.evaluated_depsgraph_get()
            me = bpy.data.meshes.new_from_object(gate.evaluated_get(dg), preserve_all_data_layers=True, depsgraph=dg)
            br = bpy.data.objects.new("OuterGate_Broken", me); br.matrix_world = gate.matrix_world.copy()
            for c in gate.users_collection:
                c.objects.link(br)
            for m in mods:
                FX.REG["mods"] = [x for x in FX.REG["mods"] if x != m]
                gate.modifiers.remove(m)
            FX.add_appear(gate, -1e9, t_off=0.0)
            FX.add_appear(br, 0.0)
        # terrace lifts (render_g1.lift_terrace)
        if G1:
            th = G1.terrace_h; REG = FX.REG
            skip = {id(b["ob"]) for b in REG["blocks"]} | {id(p["ob"]) for p in REG["puffs"]}
            for H in REG["houses"]:
                for part in H["parts"]:
                    skip.add(id(part[0]))
            for b in REG["blocks"]:
                b["p1"].z += th(b["p1"].x, b["p1"].y)
            for p in REG["puffs"]:
                p["c"].z += th(p["c"].x, p["c"].y)
            rows = REG.get("cards_rows")
            if rows:
                for i, r in enumerate(rows):
                    P = r[1]; h = th(P[0], P[1])
                    if h:
                        rows[i] = (r[0], (P[0], P[1], P[2] + h)) + tuple(r[2:])
                REG["cards_n"] = None
            for cn in ("States845", "FX845"):
                c = bpy.data.collections.get(cn)
                if not c:
                    continue
                for ob in c.all_objects:
                    if id(ob) in skip or ob.name.startswith(("Ruins845", "Rubble845", "Scars845", "FxDust")):
                        continue
                    h = th(ob.location.x, ob.location.y)
                    if h > 0.01:
                        ob.location.z += h
    if G1:                                   # thrown rocks -> rough lumps (render_g1.swap_rocks)
        rock = G1._mats({})["rock"]
        protos = [G1.lump_mesh(f"G2LumpProto{i}", 900 + i) for i in range(6)]
        for p in protos:
            p.materials.append(rock)
        n = 0
        for ob in list(bpy.data.objects):
            if ob.type != "MESH":
                continue
            if ob.name.startswith("ThrownBlock"):
                s_ = max(ob.dimensions) / max(1e-3, max(ob.scale))
                me = G1.lump_mesh(ob.name + "_lump", n + 40, squash=(1.0, 0.82, 0.74))
                for v in me.vertices:
                    v.co *= s_
                me.materials.append(rock); ob.data = me; n += 1
            elif ob.name.startswith(("Stone", "Spray")) and not ob.name.startswith("StoneProto"):
                ob.data = protos[n % len(protos)]; n += 1
    for o in bpy.data.objects:
        if o.name.startswith("FireSmoke") or o.name == "Crater0":
            o.hide_render = o.hide_viewport = True
    if FX:
        FX.REG["appear"] = [a for a in FX.REG["appear"] if not (a[0].name.startswith("FireSmoke") or a[0].name == "Crater0")]
    cc = bpy.data.collections.get("ColossalTitan")
    if cc:
        cc.hide_render = True
    pkc = bpy.data.collections.get("PK_People")      # cast845's plaza crowd (g1 hides it 0.4 s after the kick)
    S["cast_hidden"] = 0
    if pkc:
        for o in pkc.all_objects:
            o.hide_render = True; S["cast_hidden"] += 1
    for o in bpy.data.objects:                       # fire lights overflow Eevee's shadow pool (render_g1)
        if o.type == "LIGHT" and o.name.startswith(("FireL", "FX_Flash", "G1_Flash")):
            o.data.use_shadow = False
    # seq_carla: the Smiling Titan after the bite (g1 END frame 2640), Carla gone
    SC = sys.modules.get("seq_carla")
    S["seq_carla"] = SC if SC and SC.STATE.get("C") is not None else None
    if S["seq_carla"]:
        try:
            SC.pose_carla(2640.0)
            for k_ in ("carla",):
                for o in SC._all_obs(SC.STATE[k_]):
                    o.hide_render = True
        except Exception as ex:
            print("[g2] seq_carla pose failed:", ex)

# ====================================================================== swarm845 (the town after the pour)
SIM0, SIM_K = 33.6, 1.6                      # g1 end: (32 - 11) * 1.6 seconds after the kick, timelapse 1.6

def sim_t(t):
    return SIM0 + SIM_K * t

def swarm_setup():
    try:
        import swarm845 as SW
        if not SW.STATE.get("people"):
            SW.setup(t_end=float(os.environ.get("SWARM_TEND", "90")))
        SW.HIDE_TITANS = {"smiling"}
        SW.HIDE_PEOPLE = evacuated
        S["SW"] = SW
        print("[g2] swarm845", SW.info())
    except Exception:
        import traceback; traceback.print_exc(); S["SW"] = None

def evacuated(P):
    """Owner 10/27 07:34: the gate area is already evacuated when he charges.  Hide swarm845's people (the ones heading for
    the inner gate) on the avenue ahead of him (y > -470, out of g1's last frame), on the apron and north of the wall (the
    field / gate road) and on the market plaza beside his lane (also out of g1's last frame); the town behind him and the
    canal docks keep theirs."""
    x, y = P[:, 0], P[:, 1]
    px, py, pr = L.PLAZA if L is not None and hasattr(L, "PLAZA") else (-20.0, -360.0, 40.0)
    return ((((x - px) ** 2 + (y - py) ** 2) < (pr + 6.0) ** 2) | ((np.abs(x) < 20.0) & (y > -470.0) & (y < 0.0)) | ((np.abs(x) < 62.0) & (y > -76.0) & (y < 0.0)) |
            ((y >= 0.0) & (y < 650.0) & (np.abs(x) < 160.0)))

def swarm_update(t):
    SW = S.get("SW")
    if not SW or not SW.STATE:
        return
    ts = sim_t(t); St = SW.STATE
    k0 = min(int(max(ts, 0) / SW.DT), St["K"] - 1)
    TX, TY = St["TX"][k0], St["TY"][k0]
    hide = {"smiling"}
    SC = S.get("seq_carla")
    if SC:                                   # g1 keeps the Smiling Titan alone (no titan within 85 m of Carla)
        C2 = SC.STATE["C"]
        hide |= set(int(j) for j in np.where((TX - C2.x) ** 2 + (TY - C2.y) ** 2 < 85.0 ** 2)[0])
    ya = arm_y(t)                            # nobody stands in the Armored's lane right where he is
    hide |= set(int(j) for j in np.where((np.abs(TX) < 18.0) & (np.abs(TY - ya) < 45.0))[0])
    SW.HIDE_TITANS = hide
    SW.update(ts)

# ====================================================================== the inner gatehouse (both faces), crest leaf, breach
def build_gatehouse(coll):
    M = S["M"]
    ig = bpy.data.objects.get("InnerGate")
    stone = ig.data.materials[0] if ig and ig.data.materials else M["wall"]
    iron = ig.data.materials[1] if ig and len(ig.data.materials) > 1 else M["iron"]
    S["stone"] = stone
    d0 = bpy.data.objects.get("InnerGate_Door")
    if d0:
        d0.hide_render = True
    parts = {}
    for side in (-1, 1):                     # -1 south face, +1 north face
        tag = "S" if side < 0 else "N"
        # wings (survive the ram): brick 8.5 x 8 x 9.5, cream cornice + corner strips, tile lean-to roofs, doors
        bm = bmesh.new()
        for sx in (-1, 1):
            xc = sx * 11.75
            L.box(bm, (xc, side * 9.0, 4.75), (8.5, 8.0, 9.5), mi=0)
            L.box(bm, (xc, side * 9.1, 9.9), (9.1, 8.6, 0.8), mi=1)                 # cornice (two bands)
            L.box(bm, (xc, side * 9.15, 9.25), (8.9, 8.5, 0.35), mi=1)
            L.box(bm, (sx * 15.85, side * 12.9, 4.75), (0.7, 0.4, 9.5), mi=1)       # corner strips
            L.box(bm, (sx * 7.65, side * 12.9, 4.75), (0.7, 0.4, 9.5), mi=1)
            # lean-to roof: from the cornice at the front up to the wall face
            r = bmesh.ops.create_cube(bm, size=1)
            for v in r["verts"]:
                x, y, z = v.co
                yy = side * (5.2 + (y + 0.5) * 8.4) if side > 0 else side * (5.2 + (0.5 - y) * 8.4)
                front = abs(yy) > 9.0
                v.co = Vector((xc + x * 9.0, yy, (10.3 if front else 13.4) + (z + 0.5) * 0.5))
            for f in {f for v in r["verts"] for f in v.link_faces}:
                f.material_index = 2
        doorpts = arch_pts(1.5, 5.0, 0.62, 8)
        poly_face(bm, [(x - 11.75, z + 0.05) for x, z in doorpts], side * 13.03, mi=3, flip=side > 0)
        poly_face(bm, [(x + 11.75, z + 0.05) for x, z in arch_pts(1.6, 5.6, 0.6, 8)], side * 13.03, mi=4, flip=side > 0)
        for k in range(3):                   # barred window beside the door
            L.box(bm, (-14.2, side * 13.04, 3.0 + 0.0 * k), (1.2, 0.1, 1.6), mi=4)
        parts[f"wings{tag}"] = put(f"G2GateWings{tag}", bm, [M["brick"], M["cream"], M["tile"], M["timber"], M["dark"]], coll)
        # the central bay (breakable): brick lower panel with the small pointed passage, stone above to z 22
        bm = bmesh.new()
        L.box(bm, (0, side * 5.95, 4.75), (15.2, 0.9, 9.5), mi=0)
        L.box(bm, (0, side * 6.0, 9.85), (15.4, 1.1, 0.7), mi=1)
        L.box(bm, (0, side * 5.85, 15.9), (15.2, 0.7, 11.8), mi=2)
        poly_face(bm, [(x, z + 0.02) for x, z in arch_pts(2.85, 7.3, 0.6, 10)], side * 6.42, mi=3, flip=side > 0)   # green trim
        poly_face(bm, [(x, z + 0.02) for x, z in arch_pts(2.5, 7.0, 0.6, 10)], side * 6.46, mi=4, flip=side > 0)    # passage
        parts[f"core{tag}"] = put(f"G2GateCore{tag}", bm, [M["brick"], M["cream"], stone, M["trim"], M["dark"]], coll)
        # broken central bay: only jagged jambs survive (the hole is 13 wide, the bay 15.2)
        bm = bmesh.new(); rnd = random.Random(70 + side)
        for sx in (-1, 1):
            z = 0.0
            while z < 22.0:
                dz = rnd.uniform(0.8, 1.8); hw = arch_hw(z + dz / 2)
                inner = hw + rnd.uniform(-0.25, 0.6)
                w = 7.6 - inner
                if w > 0.15:
                    L.box(bm, (sx * (inner + w / 2), side * 5.95, z + dz / 2), (w, 0.9, dz), mi=0 if z < 9.5 else 1)
                z += dz
        parts[f"broken{tag}"] = put(f"G2BreachJamb{tag}", bm, [M["brick"], stone], coll)
        parts[f"broken{tag}"].hide_render = True
        # crest leaf (the drop gate): brick 10 x 12 x 1.3, goddess shield, corbel row, two chains
        bm = bmesh.new()
        L.box(bm, (0, 0, 6.0), (10.0, 1.3, 12.0), mi=0)
        for k in range(9):
            L.box(bm, (-4.4 + 1.1 * k, side * 0.85, 0.45), (0.55, 0.6, 0.6), mi=1)
        L.box(bm, (0, side * 0.7, 11.6), (10.4, 0.3, 0.5), mi=1)
        sh = [(-2.4, 9.6), (2.4, 9.6), (2.4, 5.6), (0.0, 3.4), (-2.4, 5.6)]
        poly_face(bm, sh, side * 0.67, mi=1, flip=side > 0)
        poly_face(bm, [(x * 0.82, 3.4 + (z - 3.4) * 0.86 + 0.25) for x, z in sh], side * 0.70, mi=2, flip=side > 0)
        poly_face(bm, [(-0.6, 8.4), (0.7, 8.6), (1.0, 7.0), (0.5, 5.3), (-0.4, 5.6), (-0.9, 7.2)], side * 0.73, mi=1, flip=side > 0)
        leaf = put(f"G2Leaf{tag}", bm, [M["brick"], M["cream"], M["shield"]], coll)
        leaf.location = (0, side * 6.95, 10.0)
        parts[f"leaf{tag}"] = leaf
        ch = []
        for sx in (-1, 1):
            bm = bmesh.new(); L.cyl(bm, (0, 0, 0), (0, 0, -1), 0.16, 0.16, seg=6, mi=0)
            for k in range(14):                  # chain links read as a beaded rod
                L.box(bm, (0, 0, -k / 14.0), (0.42, 0.18, 0.03), mi=0)
            o = put(f"G2Chain{tag}{sx}", bm, [iron], coll)
            o.location = (sx * 4.2, side * 6.95, 44.0)
            ch.append(o)
        parts[f"chains{tag}"] = ch
    # the gatehouse body (scene.py InnerGate): intact until the ram, then a hand-built broken twin (no booleans)
    parts["ig"] = ig
    if ig:
        bm = bmesh.new(); rnd = random.Random(9)
        T = L.WALL_T + 0.8; pw = 7.0; w = L.GATE_W; px = w / 2 + 3 + pw / 2; WH = L.WALL_H
        for sx in (-1, 1):
            L.box(bm, (sx * px, 0, (WH + 3.5 + 4) / 2 - 4), (pw, T + 3.2, WH + 3.5 + 4))
        top0 = HOLE_H + 0.6
        L.box(bm, (0, 0, (top0 + WH) / 2), (2 * px - pw + 0.2, T - 0.6, WH - top0))
        z = 15.0                                  # jagged arch shoulders between the hole and the pilasters
        while z < top0:
            dz = rnd.uniform(0.7, 1.4); hw = arch_hw(z + dz / 2) + rnd.uniform(-0.2, 0.9)
            xo = 2 * px - pw + 0.2
            wbl = xo / 2 - hw
            for sx in (-1, 1):
                if wbl > 0.1:
                    L.box(bm, (sx * (hw + wbl / 2), rnd.uniform(-0.3, 0.3), z + dz / 2), (wbl, T - 0.6 - rnd.uniform(0, 1.5), dz))
            z += dz
        L.box(bm, (0, 0, WH - 1.2), (2 * px - pw + 0.2, T + 0.2, 0.8))
        br = put("G2BreachBody", bm, [stone, iron], coll)
        br.hide_render = True
        parts["ig_broken"] = br
    # cracks (QA v2): thin dark-grey BRANCHING cracks radiating 15-30 m from the hole edge, on the actual face planes
    bm = bmesh.new(); rnd = random.Random(31)
    def face_y(x, z, side):
        if abs(x) < 10.0:
            return side * ((L.WALL_T + 0.8 - 0.6) / 2 + 0.07)                  # gatehouse recessed panel
        if abs(x) < 17.0:
            return side * ((L.WALL_T + 0.8 + 3.2) / 2 + 0.07)                  # gatehouse pilasters
        return side * (L.WALL_T / 2 + (L.TOP_T / 2 - L.WALL_T / 2) * (z + 4.0) / (L.WALL_H + 4.0) + 0.07)
    def crack(p, d, ln, w, side, depth=0):
        n = max(3, int(ln / 1.6)); seg = ln / n
        for k in range(n):
            d = (d + Vector((rnd.uniform(-0.28, 0.28), 0, rnd.uniform(-0.28, 0.28)))).normalized()
            q = p + d * seg
            if q.z > L.WALL_H - 1.5 or q.z < 10.5 or (abs(q.x) < 16.6 and q.z < 10.8):
                return
            ww = w * (1.0 - 0.75 * k / n)
            c = (p + q) / 2; yy = face_y(c.x, c.z, side)
            ang = math.atan2(q.z - p.z, q.x - p.x)
            r = bmesh.ops.create_cube(bm, size=1)
            for v in r["verts"]:
                x, y, z = v.co
                lx, lz = x * (seg + ww), z * ww
                v.co = Vector((c.x + lx * math.cos(ang) - lz * math.sin(ang), yy + y * 0.04, c.z + lx * math.sin(ang) + lz * math.cos(ang)))
            if depth < 2 and rnd.random() < 0.22:                              # branch
                bd = (d + Vector((rnd.uniform(-1, 1), 0, rnd.uniform(-1, 1))) * 0.9).normalized()
                crack(q, bd, ln * rnd.uniform(0.25, 0.45) * (1 - k / n), ww * 0.7, side, depth + 1)
            p = q
    for side in (-1, 1):
        for k in range(12):
            a = rnd.uniform(0.0, math.pi) if k < 10 else rnd.choice((0.05, math.pi - 0.05))
            zc = HOLE_H * 0.55
            hw = arch_hw(zc + math.sin(a) * 12.0)
            p = Vector((math.cos(a) * (hw + 0.3), 0, min(HOLE_H, zc + math.sin(a) * 12.0) + 0.2))
            if p.z < 11.0:
                p.z = 11.0 + rnd.uniform(0, 4)
            d = Vector((math.cos(a), 0, math.sin(a) * 0.6)).normalized()
            crack(p, d, rnd.uniform(15, 30), rnd.uniform(0.15, 0.22), side)
    cr = put("G2Cracks", bm, [M["crack"]], coll); cr.hide_render = True
    parts["cracks"] = cr
    # QA v3: the breach must read as a TALL DARK pointed opening on both faces: a dark sooty liner on the reveal (sides +
    # pointed vault) through the whole thickness, broken stone teeth round both mouths, rubble spilling out of both mouths
    bm = bmesh.new(); rnd = random.Random(77)
    outline = []
    for k in range(25):                                   # left foot -> apex -> right foot along the arch, jittered
        u = k / 24.0
        z = HOLE_H * (1.0 - abs(2 * u - 1)) ** 0.85 if 0 < u < 1 else 0.0
        z = min(HOLE_H - 0.3, z)
        hw = max(0.25, arch_hw(z) - 0.25)
        x = -hw if u < 0.5 else hw
        if k == 12:
            x, z = 0.0, HOLE_H - 0.35
        outline.append((x + rnd.uniform(-0.35, 0.35) * (0 < k < 24), z + rnd.uniform(-0.3, 0.3) * (0 < k < 24)))
    ys = (-6.5, -2.0, 2.0, 6.5)
    rows = [[bm.verts.new((x, yy, z)) for x, z in outline] for yy in ys]
    for r0, r1 in zip(rows, rows[1:]):
        for k in range(len(outline) - 1):
            bm.faces.new((r0[k], r0[k + 1], r1[k + 1], r1[k]))
    for f_ in bm.faces:
        f_.normal_update()
    liner = put("G2BreachLiner", bm, [M["soot"]], coll); liner.hide_render = True
    parts["liner"] = liner
    protos = [G1.lump_mesh(f"G2Tooth{i}", 500 + i) for i in range(6)] if G1 else []
    for pr in protos:
        pr.materials.append(stone)
    teeth = []
    for side in (-1, 1):                                  # broken teeth round the mouth on both faces
        for k in range(1, 24):
            x, z = outline[k]
            if z < 2.0:
                continue
            ob = bpy.data.objects.new(f"G2Tooth{side:+d}_{k}", protos[k % len(protos)] if protos else None); coll.objects.link(ob)
            sz = rnd.uniform(1.0, 2.2)
            ob.scale = (sz, sz * 0.8, sz * rnd.uniform(0.7, 1.2))
            out = Vector((x, 0, z - HOLE_H * 0.45)); out.y = 0; out = out.normalized() if out.length > 1e-3 else Vector((0, 0, 1))
            ob.location = (x + out.x * 0.6, side * rnd.uniform(5.3, 6.2), z + out.z * 0.6)
            ob.rotation_euler = (rnd.uniform(0, 6), rnd.uniform(0, 6), rnd.uniform(0, 6)); ob.hide_render = True
            teeth.append(ob)
    for side in (-1, 1):                                  # rubble spilling out of both mouths (wing to wing, low fans)
        for k in range(26):
            ob = bpy.data.objects.new(f"G2Spill{side:+d}_{k}", protos[(k + 3) % len(protos)] if protos else None); coll.objects.link(ob)
            sz = rnd.uniform(0.9, 2.8) * (1.3 if k < 6 else 1.0)
            r_ = rnd.uniform(0, 1) ** 0.6
            x = rnd.uniform(-9, 9) * (0.5 + 0.5 * r_)
            if side > 0 and abs(x) < 3.2:                 # his slide lane stays clear on the north side
                x = math.copysign(rnd.uniform(3.2, 9.0), x if x else 1.0)
            yy = side * (6.0 + r_ * rnd.uniform(4, 16))
            ob.scale = (sz, sz * 0.85, sz * 0.6)
            ob.location = (x, yy, gz(x, yy) + sz * 0.2)
            ob.rotation_euler = (rnd.uniform(0, 6), rnd.uniform(0, 6), rnd.uniform(0, 6)); ob.hide_render = True
            teeth.append(ob)
    parts["teeth"] = teeth
    S["gate"] = parts

def leaf_bottom(t):
    """Crest leaf lower edge z: 10 m (raised) -> slides down from 11.8 to 4.2 m by the impact."""
    a, b = BEATS["leaf"]
    u = min(1.0, max(0.0, (t - a) / (b - a)))
    return 10.0 - 5.8 * (u * u * (3 - 2 * u) * 0.35 + u * 0.65)

def update_gate(t):
    P = S["gate"]; burst = t >= T_IMP
    def vis(o, v):
        if o is not None and o.hide_render == v:
            o.hide_render = not v
    for tag in ("S", "N"):
        vis(P[f"core{tag}"], not burst); vis(P[f"broken{tag}"], burst)
        vis(P[f"leaf{tag}"], not burst)
        zb = leaf_bottom(t) if tag == "S" else 10.0
        P[f"leaf{tag}"].location.z = zb
        for o in P[f"chains{tag}"]:
            o.scale = (1.0, 1.0, max(0.01, 44.0 - (zb + 12.0)))
            vis(o, True)
    vis(P.get("ig"), not burst); vis(P.get("ig_broken"), burst)
    vis(P["cracks"], burst); vis(P.get("liner"), burst)
    for o in P.get("teeth", ()):
        vis(o, burst)
    if burst:                                             # the chains snap: short dangling ends
        for tag in ("S", "N"):
            for o in P[f"chains{tag}"]:
                o.scale = (1.0, 1.0, 5.0)

# ====================================================================== apron, avenue, north side (water strip, canal, quays, bridge)
def north_x(y):
    tt = max(0.0, (y - 8) / 40.0)
    return math.sin(tt / 5) * 60 * min(1, tt / 6)

def canal_cx(y):
    return L.CX + north_x(y)

def water_z(y):
    return L.height(canal_cx(y), y) + 2.2          # = scene CanalWaterN / swarm845 boat level

def ribbon(bm, pts, w0, w1, zf, mi=0):
    """Strip between lateral offsets w0..w1 (signed, metres) of a centre polyline pts; zf(p, off) -> z."""
    prev = None
    for k, p in enumerate(pts):
        a = Vector(pts[max(k - 1, 0)]); b = Vector(pts[min(k + 1, len(pts) - 1)])
        tng = (b - a).normalized(); nrm = Vector((tng.y, -tng.x))          # +nrm = east (right of north)
        pv = Vector(p)
        q0 = pv + nrm * w0; q1 = pv + nrm * w1
        v0 = bm.verts.new((q0.x, q0.y, zf(pv, w0))); v1 = bm.verts.new((q1.x, q1.y, zf(pv, w1)))
        if prev:
            f = bm.faces.new((prev[0], prev[1], v1, v0)); f.material_index = mi
            f.normal_update()
            if abs(f.normal.z) > 0.2 and f.normal.z < 0:
                f.normal_flip()
        prev = (v0, v1)

def clear_canal_veg(widen):
    """No trees standing in the canal / river: drop scatter points (vertex-only GN point clouds) inside the water
    corridor, and AND every 'Distribute Points on Faces' selection with 'outside the corridor' (x distance to the
    canal centre line, written per terrain vertex as an attribute)."""
    n_pts = 0
    for ob in bpy.data.objects:
        if ob.type != "MESH" or len(ob.data.polygons) or not any(m.type == "NODES" for m in ob.modifiers):
            continue
        if ob.name.startswith(("Town", "G2", "PK")):
            continue
        me = ob.data; mw = ob.matrix_world
        bm = bmesh.new(); bm.from_mesh(me)
        dead = []
        for v in bm.verts:
            w = mw @ v.co
            if 4.0 < w.y < 2600 and abs(w.x - canal_cx(w.y)) < widen(w) + 7.0:
                dead.append(v)
        if dead:
            bmesh.ops.delete(bm, geom=dead, context="VERTS"); bm.to_mesh(me); me.update(); n_pts += len(dead)
        bm.free()
    n_gn = 0
    for ob in bpy.data.objects:
        if ob.type != "MESH" or not len(ob.data.polygons):
            continue
        for md in ob.modifiers:
            if md.type != "NODES" or not md.node_group:
                continue
            ng = md.node_group
            dps = [n for n in ng.nodes if n.bl_idname == "GeometryNodeDistributePointsOnFaces"]
            if not dps or ng.get("g2_canal"):
                continue
            me = ob.data                                   # per-vertex 'outside the canal' mask on the terrain mesh
            a = me.attributes.get("g2_dry") or me.attributes.new("g2_dry", "FLOAT", "POINT")
            mw = ob.matrix_world; vals = []
            for v in me.vertices:
                w = mw @ v.co
                vals.append(0.0 if (4.0 < w.y < 2600 and abs(w.x - canal_cx(w.y)) < widen(w) + 10.0) else 1.0)
            a.data.foreach_set("value", vals)
            for dp in dps:
                na = ng.nodes.new("GeometryNodeInputNamedAttribute"); na.data_type = "FLOAT"; na.inputs["Name"].default_value = "g2_dry"
                cmp = ng.nodes.new("FunctionNodeCompare"); cmp.data_type = "FLOAT"; cmp.operation = "GREATER_THAN"
                cmp.inputs[1].default_value = 0.999
                ng.links.new(na.outputs["Attribute"], cmp.inputs[0])
                sel = dp.inputs["Selection"]
                if sel.is_linked:
                    src = sel.links[0].from_socket
                    an = ng.nodes.new("FunctionNodeBooleanMath"); an.operation = "AND"
                    ng.links.new(src, an.inputs[0]); ng.links.new(cmp.outputs[0], an.inputs[1])
                    ng.links.new(an.outputs[0], sel)
                else:
                    ng.links.new(cmp.outputs[0], sel)
                n_gn += 1
            ng["g2_canal"] = 1
    print(f"[g2] canal corridor cleared: {n_pts} scatter points, {n_gn} distribute nodes masked")

def build_ground(coll):
    M = S["M"]
    # houses off the apron / gatehouse wings, the avenue kept clear (g1_set's Town editor)
    if G1:
        def edit(name, x, y, z):
            if abs(x) < 60 and -68 < y < -4:
                return "hide"
            if abs(x) < 15 and -720 < y < -60:
                return "hide"
            return None
        nh, _ = G1._town_edit(edit)
        print(f"[g2] town points hidden for the apron / avenue: {nh}")
    # apron (dirt + pebbles) and the dirt avenue with ruts and grass verges
    ap = L.disc_patch("G2Apron", 0, -37.5, 55, 24.5, 0, M["dirt"], z=0.2)
    av = L.flat_strip("G2Avenue", [(0, y) for y in range(-700, -55, 15)], 24.0, M["dirt"], z=0.19)
    rt = [L.flat_strip(f"G2Rut{s}", [(s * 3.2, y) for y in range(-700, -55, 15)], 0.9, M["rut"], z=0.21) for s in (-1, 1)]
    vg = [L.flat_strip(f"G2Verge{s}", [(s * 12.5, y) for y in range(-700, -62, 15)], 2.6, M["verge"], z=0.2) for s in (-1, 1)]
    # NORTH: water strip along the wall foot + timber road bridge, the gate road
    ws = L.flat_strip("G2WaterStrip", [(x, 18.0) for x in range(-250, 150, 10)], 6.0, M["strip"], z=0.45)
    bm = bmesh.new()
    L.box(bm, (0, 18.0, 0.55), (12.0, 8.5, 0.5), mi=0)
    for sx in (-1, 1):
        L.box(bm, (sx * 6.2, 18.0, 1.4), (0.25, 8.5, 0.18), mi=0)
        for k in range(5):
            L.box(bm, (sx * 6.2, 14.2 + 1.9 * k, 1.0), (0.25, 0.25, 0.9), mi=0)
    br = put("G2StripBridge", bm, [M["timber"]], coll)
    br.location.z = L.height(0, 18.0)
    rd = L.flat_strip("G2GateRoad", [(0, y) for y in range(22, 460, 12)], 12.0, M["dirt_n"], z=0.14)
    # the canal: 30 m stone-lined, quays 20 m both sides raised 3.6 m over the water, grass embankments outside
    cw = bpy.data.objects.get("CanalWaterN")
    if cw:
        cw.hide_render = True
    ys = list(range(6, 470, 6)) + list(range(470, 2400, 20))
    pts = [(canal_cx(y), y) for y in ys]
    bm = bmesh.new()
    wzs = {}
    def wz(p, off=0.0):
        k = round(p.y, 1)
        if k not in wzs:
            wzs[k] = water_z(p.y)
        return wzs[k]
    widen = lambda p: 15.0 + max(0.0, min(1.0, (p.y - 450) / 250.0)) * 21.0
    prev = None                               # water (widening into the river north of y 450)
    for k, p in enumerate(pts):
        a = Vector(pts[max(k - 1, 0)]); b = Vector(pts[min(k + 1, len(pts) - 1)])
        tng = (b - a).normalized(); nrm = Vector((tng.y, -tng.x)); pv = Vector(p); hw = widen(pv) + 1.0
        v0 = bm.verts.new((*(pv - nrm * hw), wz(pv))); v1 = bm.verts.new((*(pv + nrm * hw), wz(pv)))
        if prev:
            f = bm.faces.new((prev[0], prev[1], v1, v0)); f.normal_update()
            if f.normal.z < 0: f.normal_flip()
        prev = (v0, v1)
    water = put("G2Canal", bm, [M["water"]], coll)
    clear_canal_veg(widen)
    qpts = [p for p in pts if p[1] <= 452]
    bm = bmesh.new()
    for s in (-1, 1):                         # quay paving, retaining wall face, damp foot, grass embankment
        ribbon(bm, qpts, s * 15.0, s * 35.0, lambda p, o: wz(p) + 3.6, mi=0)
        ribbon(bm, qpts, s * 15.0, s * 15.0001, lambda p, o: wz(p) - 0.6, mi=1)
        prevw = None
        for k, p in enumerate(qpts):          # vertical retaining wall (two rows of verts at the inner edge)
            a = Vector(qpts[max(k - 1, 0)]); b = Vector(qpts[min(k + 1, len(qpts) - 1)])
            tng = (b - a).normalized(); nrm = Vector((tng.y, -tng.x)); pv = Vector(p)
            q = pv + nrm * s * 15.0
            v0 = bm.verts.new((q.x, q.y, wz(pv) - 0.5)); v1 = bm.verts.new((q.x, q.y, wz(pv) + 3.6))
            if prevw:
                f = bm.faces.new((prevw[0], prevw[1], v1, v0)); f.material_index = 1
            prevw = (v0, v1)
        ribbon(bm, qpts, s * 35.0, s * 44.0, lambda p, o: (wz(p) + 3.6) if abs(o) < 36 else L.height(*(Vector(p))) + 0.05, mi=2)
    # v14 (FEEDBACK_v13 §1: the pale path beside the river ended at y 452 in the 0:30 view): the paved quay continues north
    # as a towpath along both river banks to y 2400, easing from quay height down onto the ground by y 700
    tpts = [p for p in pts if p[1] >= 446]
    for s in (-1, 1):
        prev = None
        for k, p in enumerate(tpts):
            a = Vector(tpts[max(k - 1, 0)]); b = Vector(tpts[min(k + 1, len(tpts) - 1)])
            tng = (b - a).normalized(); nrm = Vector((tng.y, -tng.x)); pv = Vector(p)
            w0 = widen(pv) + 0.5; w1 = w0 + 18.0
            u = max(0.0, min(1.0, (p[1] - 452.0) / 250.0))
            vs = []
            for w in (w0, w1):
                q = pv + nrm * (s * w)
                zq = (wz(pv) + 3.6) * (1 - u) + (L.height(q.x, q.y) + 0.12) * u
                vs.append(bm.verts.new((q.x, q.y, max(zq, L.height(q.x, q.y) + 0.08))))
            if prev:
                f = bm.faces.new((prev[0], prev[1], vs[1], vs[0])); f.material_index = 0; f.normal_update()
                if f.normal.z < 0: f.normal_flip()
            prev = vs
    # quay apron by the arches (x 150..213, y 8..110) at quay height
    ya = 8.0; yb = 110.0
    zq = water_z(40.0) + 3.6
    L.box(bm, ((150 + L.CX - 15) / 2, (ya + yb) / 2, zq - 2.0), (L.CX - 15 - 150, yb - ya, 4.0), mi=0)
    quay = put("G2Quays", bm, [M["quay"], M["quaywall"], M["grass_bank"]], coll)
    S["zq"] = zq
    # high bridge on three square pylons with orange pyramid caps, deck 14 m over the water (ferries pass under)
    bm = bmesh.new(); yb_ = 40.0; c = canal_cx(yb_); w0 = water_z(yb_)
    for dx in (-17.0, 0.0, 17.0):
        L.box(bm, (c + dx, yb_, w0 + 7.5), (4.0, 4.0, 17.0), mi=0)
        r = bmesh.ops.create_cone(bm, cap_ends=True, segments=4, radius1=3.4, radius2=0.05, depth=3.2)
        for v in r["verts"]:
            v.co.rotate(Euler((0, 0, math.pi / 4))); v.co += Vector((c + dx, yb_, w0 + 17.6))
        for f in {f for v in r["verts"] for f in v.link_faces}:
            f.material_index = 1
    L.box(bm, (c, yb_, w0 + 14.0), (34.0 + 4, 3.4, 0.6), mi=2)
    for s in (-1, 1):
        L.box(bm, (c, yb_ + s * 1.6, w0 + 15.0), (38.0, 0.12, 0.12), mi=3)
    put("G2HighBridge", bm, [M["pylon"], M["cap"], M["timber"], M["iron"]], coll)
    # cypresses along the quays' outer edges
    bm = bmesh.new(); rnd = random.Random(5)
    for s in (-1, 1):
        y = 20.0 + rnd.uniform(0, 10)
        while y < 440:
            p = Vector((canal_cx(y), y)); hgt = rnd.uniform(12, 16)
            if not (s < 0 and y < 112):
                L.cyl(bm, (p.x + s * 38.5, y, wz(p) + 3.4), (p.x + s * 38.5, y, wz(p) + 3.4 + hgt), 1.7, 0.15, seg=7)
            y += rnd.uniform(25, 40)
    put("G2Cypress", bm, [M["cypress"]], coll)
    # gangways to the moored ferries F3 (west landing y 60) and F4 (east landing y 100)
    bm = bmesh.new()
    for y, s in ((60.0, -1), (100.0, 1)):
        p = Vector((canal_cx(y), y))
        L.box(bm, (p.x + s * 12.0, y, water_z(y) + 2.6), (6.5, 3.0, 0.3))
    put("G2Gangways", bm, [M["timber"]], coll)
    # existing wall-top cannons at the gate -> the bible's 6 guns on pads (built in build_guns)
    for o in bpy.data.objects:
        if o.name.startswith("CannonM") and abs(o.location.x) < 140:
            o.hide_render = True

# ====================================================================== guns (6 field + 6 wall-top), crews, fire FX
FIELD_X = (-38.0, -24.0, -10.0, 10.0, 24.0, 38.0)
FIELD_Y = -34.0
WALL_GX = (-25.0, 25.0, -60.0, 60.0, -95.0, 95.0)
SHELL_T = 0.2                                # shell flight time (fire -> hit)
VOLLEY = {BEATS["volley1"] - 0.05: (-10.0, 24.0, 38.0), BEATS["volley2"]: (-38.0, -24.0, 10.0)}   # 1st shot of volley 1 = the face hit
KICKED = 10.0                                # the carriage his foot kicks over (BEATS kick_carriage)
WALL_HIT = (0, 2)                            # wall_fire shots that ricochet off him (the others miss)

def gun_mesh(M):
    bm = bmesh.new()
    L.cyl(bm, (0, -1.6, 1.30), (0, 1.45, 1.40), 0.24, 0.33, seg=10, mi=0)                 # barrel, muzzle at -y
    for yy in (-1.3, -0.2, 0.9):
        L.cyl(bm, (0, yy - 0.08, 1.33), (0, yy + 0.08, 1.33), 0.36, 0.36, seg=10, mi=0)
    L.box(bm, (0, 0.6, 0.85), (0.9, 2.4, 0.55), mi=1)                                     # box carriage
    r = bmesh.ops.create_cube(bm, size=1)
    for v in r["verts"]:
        x, y, z = v.co; v.co = Vector((x * 0.5, 2.2 + y * 2.0, 0.55 - (y + 0.5) * 0.45 + z * 0.35))
    for f in {f for v in r["verts"] for f in v.link_faces}:
        f.material_index = 1
    for sx in (-1, 1):                                                                    # spoked wheels 2.2 m
        L.cyl(bm, (sx * 0.62, 0.2, 1.1), (sx * 0.8, 0.2, 1.1), 1.1, 1.1, seg=14, mi=2)
    return bm

def build_guns(coll):
    M = S["M"]
    bm = gun_mesh(M); me = bpy.data.meshes.new("G2Gun"); bm.to_mesh(me); bm.free()
    for m in (M["bronze"], M["timber"], M["wheel"]):
        me.materials.append(m)
    S["fguns"] = []
    for x in FIELD_X:
        o = bpy.data.objects.new(f"G2FieldGun{int(x)}", me); coll.objects.link(o)
        o.location = (x, FIELD_Y, gz(x, FIELD_Y)); S["fguns"].append(o)
    S["wguns"] = []
    bmp = bmesh.new()
    for x in WALL_GX:
        o = bpy.data.objects.new(f"G2WallGun{int(x)}", me); coll.objects.link(o)
        o.location = (x, -1.6, L.WALL_H + 0.25); o.rotation_euler = (0.18, 0, 0); o.scale = (0.85,) * 3
        S["wguns"].append(o)
        r = bmesh.ops.create_circle(bmp, cap_ends=True, segments=20, radius=2.5)
        for v in r["verts"]:
            v.co += Vector((x, -1.4, L.WALL_H + 0.06))
        for sx in (-1, 1):
            L.box(bmp, (x + sx * 0.7, -1.4, L.WALL_H + 0.16), (0.22, 4.6, 0.16), mi=1)
    put("G2GunPads", bmp, [M["pad"], M["timber"]], coll)

def gun_shots():
    """(t, muzzle (x,y,z), target (x,y,z), kind) kind: 'hit' (ricochet), 'face' (big ricochet), 'miss'."""
    shots = []
    rnd = random.Random(8)
    wall_m = {x: Vector((x, -4.6, L.WALL_H + 1.6)) for x in WALL_GX}
    for k, (t, x) in enumerate(zip(BEATS["wall_fire"], WALL_GX[:4])):
        th = t + SHELL_T
        kind = "hit" if k in WALL_HIT else "miss"
        ya = arm_y(th)
        tgt = (Vector((0.8, ya - 0.6, 10.5 if k == 0 else 12.6)) if kind == "hit"
               else Vector((rnd.uniform(-8, 8), ya + rnd.uniform(8, 22), 0.0)))
        if kind == "miss":
            tgt.z = gz(tgt.x, tgt.y)
        shots.append((t, wall_m[x], tgt, kind))
    for x in WALL_GX[4:]:                            # the last wall round (x +-95) at 11.0: misses
        th = BEATS["volley2"] + SHELL_T; ya = arm_y(th)
        tgt = Vector((rnd.uniform(-9, 9), ya + rnd.uniform(-10, 10), 0.0)); tgt.z = gz(tgt.x, tgt.y)
        shots.append((BEATS["volley2"] + (0.0 if x < 0 else 0.12), wall_m[x], tgt, "miss"))
    for tv, xs in VOLLEY.items():
        for k, x in enumerate(xs):
            t = tv + 0.08 * k; th = t + SHELL_T; ya = arm_y(th)
            if tv < BEATS["volley2"] - 0.01:
                kind = "face" if k == 0 else "miss"
            else:
                kind = "hit" if k == 1 else "miss"
            if kind == "face":
                tgt = Vector((0.0, ya - 1.6, 13.8))
            elif kind == "hit":
                tgt = Vector((-1.6, ya - 0.5, 12.4))
            else:
                tgt = Vector((rnd.uniform(-9, 9), ya + rnd.uniform(-14, -4), 0.0)); tgt.z = gz(tgt.x, tgt.y)
            m = Vector((x, FIELD_Y - 1.7, gz(x, FIELD_Y) + 1.35))
            shots.append((t, m, tgt, kind))
    return sorted(shots, key=lambda s: s[0])

def build_fire_fx():
    """Muzzle flashes + smoke balls, shell tracers, ricochet gold streaks + 40 sparks, misses (fireball, embers, dirt)."""
    F = SMC.SmokeCards("G2GunFX")
    rng = np.random.default_rng(21)
    S["shots"] = shots = gun_shots()
    for t, m, tgt, kind in shots:
        m = np.array(m); tg = np.array(tgt)
        d = tg - m; dist = np.linalg.norm(d); T = SHELL_T
        F.add(t, m, r0=1.6, r1=3.6, life=0.16, kind="glow", color=(1.0, 0.92, 0.62), alpha=1.0, fade_in=0.01)
        mdir = np.array([0.0, -1.0, -0.25 if m[2] > 30 else 0.0])
        n = 5
        F.add_many(t + rng.uniform(0, 0.12, n), m + rng.normal(0, 0.6, (n, 3)), mdir * rng.uniform(6, 14, (n, 1)),
                   r0=3.5, r1=rng.uniform(11, 16, n), life=rng.uniform(4.0, 5.5, n), rise=0.8, color=(0.93, 0.91, 0.87),
                   kind="smoke", alpha=0.85, tau=0.5, fade_in=0.05)
        F.add_many([t], [m], [d / T], r0=0.45, r1=0.45, life=T, kind="glow", color=(1.0, 0.8, 0.45), alpha=0.9, fade_in=0.01,
                   dirs=[d / dist], stretch=7.0)                                       # the shell, a short tracer
        th = t + T
        if kind in ("hit", "face"):
            big = 1.6 if kind == "face" else 1.0
            out = np.array([np.sign(tg[0] + 1e-3) * 0.85, -0.55, 0.42]); out /= np.linalg.norm(out)   # ~25 deg up, sideways
            # QA v3: a SHORT gold streak (10-15 m) glancing off at an angle, 0.12 s, + ~40 sparks (09:37.4)
            F.add_many([th], [tg + out * 4.0], [out * 45.0], r0=0.65, r1=0.75, life=0.12, kind="glow", color=(1.0, 0.78, 0.30),
                       alpha=1.0, fade_in=0.005, dirs=[out], stretch=8.5)
            F.add(th, tg, r0=1.2, r1=2.6, life=0.1, kind="glow", color=(1.0, 0.86, 0.55), alpha=1.0, fade_in=0.005)
            n = 40
            v = rng.normal(0, 1, (n, 3)); v[:, 2] = np.abs(v[:, 2]); v[:, 1] -= 0.6
            v = v / np.linalg.norm(v, axis=1, keepdims=True) * rng.uniform(14, 30, (n, 1)) + out * 12.0
            F.add_many(np.full(n, th) + rng.uniform(0, 0.03, n), np.tile(tg, (n, 1)), v, r0=0.4, r1=0.25,
                       life=rng.uniform(0.12, 0.3, n), kind="glow", color=(1.0, 0.75, 0.35), alpha=1.0, fade_in=0.005)
            F.add(th + 0.03, tg, vel=(0, -2, 1), r0=1.5, r1=5.0, life=2.0, rise=1.2, kind="smoke", color=(0.55, 0.52, 0.48),
                  alpha=0.75, tau=0.5)
        else:
            F.add(th, tg + np.array([0, 0, 1.8]), r0=2.0, r1=4.2, life=0.3, kind="fire", alpha=1.0, fade_in=0.01)
            n = 14
            v = rng.normal(0, 1, (n, 3)); v[:, 2] = np.abs(v[:, 2]) * 2
            F.add_many(np.full(n, th), np.tile(tg + np.array([0, 0, 1.0]), (n, 1)), v * 9, r0=0.35, r1=0.25,
                       life=rng.uniform(0.4, 0.9, n), kind="fire", alpha=1.0, fade_in=0.01)
            n = 8
            F.add_many(th + rng.uniform(0, 0.15, n), np.tile(tg, (n, 1)) + rng.normal(0, 1.0, (n, 3)),
                       np.column_stack([rng.normal(0, 3, n), rng.normal(0, 3, n), rng.uniform(7, 14, n)]), r0=2.0,
                       r1=rng.uniform(5, 8, n), life=rng.uniform(2.5, 3.5, n), rise=0.5, color=(0.48, 0.37, 0.24),
                       kind="dust", alpha=0.9, tau=0.6, fade_in=0.03)
    F.build(S["coll"]); S["cards"].append((F, WIND))
    print(f"[g2] shots {len(shots)}: " + ", ".join(f"{s[0]:.2f}{s[3][0]}" for s in shots))

def gun_update(t):
    for o, x in zip(S["fguns"], FIELD_X):
        y = FIELD_Y; z = gz(x, y); rot = (0.0, 0.0, 0.0); xx = x
        for t0, m, tgt, kind in S["shots"]:
            if abs(m.x - x) < 0.5 and m.z < 20 and t >= t0:
                a = t - t0
                y += 1.1 * (min(1.0, a / 0.12) if a < 0.12 else max(0.0, 1 - (a - 0.12) / 1.8))      # recoil
        if x == KICKED and t >= BEATS["kick_carriage"]:
            u = smooth(BEATS["kick_carriage"], BEATS["kick_carriage"] + 1.1, t)
            xx = x + 8.0 * u; y += 3.0 * u
            rot = (0.0, -2.2 * u, 0.6 * u)
            z = gz(xx, y) + 1.0 * math.sin(math.pi * u)
        o.location = (xx, y, z); o.rotation_euler = rot
    for o, x in zip(S["wguns"], WALL_GX):
        y = -1.6
        for t0, m, tgt, kind in S["shots"]:
            if abs(m.x - x) < 0.5 and m.z > 20 and t >= t0:
                a = t - t0
                y += 0.8 * (min(1.0, a / 0.12) if a < 0.12 else max(0.0, 1 - (a - 0.12) / 1.5))
        o.location.y = y

# ====================================================================== the Armored Titan (Tripo, user pick 15:37 10/25)
TRIPO_ARMORED = os.environ.get("FALL_ARMORED_GLB", r"E:/YTP2/3D Timelapse/assets/tripo/armored_img/tripo-out/"
                               r"armored-ref-crop-png-rig-1ad3b89b/model.glb")

class TripoArmored:
    """(render_fall2.TripoArmored) rigged GLB, front = local +X, up +Z, left = +Y; true 15 m; rotations in the armature's
    rest frame."""
    def __init__(self, coll, height=15.0):
        before = set(bpy.data.objects)
        bpy.ops.import_scene.gltf(filepath=TRIPO_ARMORED)
        new = [o for o in bpy.data.objects if o not in before]
        self.arm = next(o for o in new if o.type == "ARMATURE")
        for o in new:
            if o.type == "MESH" and o.parent is None:
                bpy.data.objects.remove(o, do_unlink=True); continue
            for c in list(o.users_collection):
                c.objects.unlink(o)
            coll.objects.link(o)
        self.meshes = [o for o in self.arm.children if o.type == "MESH"]
        dec = float(os.environ.get("G2_ARMORED_DECIMATE", "0.2"))
        for me in self.meshes:
            if dec < 1.0:
                md = me.modifiers.new("Dec", "DECIMATE"); md.ratio = dec
                with bpy.context.temp_override(object=me, active_object=me, selected_objects=[me]):
                    bpy.ops.object.modifier_move_to_index(modifier="Dec", index=0)
                    bpy.ops.object.modifier_apply(modifier="Dec")
        bpy.context.view_layer.update()
        zs = [(me.matrix_world @ v.co).z for me in self.meshes for v in me.data.vertices]
        self.h0 = max(zs) - min(zs)
        self.k = height / self.h0
        self.arm.rotation_mode = "XYZ"
        self.B = {b.name: b for b in self.arm.data.bones}
        for pb in self.arm.pose.bones:
            pb.rotation_mode = "QUATERNION"
        self.feet = ("L_ToeBase", "R_ToeBase", "L_Foot", "R_Foot")
        print(f"[g2] Tripo Armored: rest height {self.h0:.3f} -> x{self.k:.2f} = {height} m, "
              f"{sum(len(m.data.vertices) for m in self.meshes)} verts, bones {len(self.B)}")

    def pose(self, R):
        for pb in self.arm.pose.bones:
            r = R.get(pb.name)
            if r is None:
                pb.matrix_basis = Matrix.Identity(4); continue
            ML = self.B[pb.name].matrix_local
            h = ML.to_translation()
            pb.matrix_basis = ML.inverted() @ (Matrix.Translation(h) @ r.to_4x4() @ Matrix.Translation(-h)) @ ML

    def place(self, x, y, yaw=0.0, lean=0.0):
        Rw = Matrix.Rotation(yaw + math.pi / 2, 4, "Z") @ Matrix.Rotation(lean, 4, "Y")
        self.arm.matrix_world = Matrix.Translation((x, y, 0.0)) @ Rw @ Matrix.Scale(self.k, 4)
        bpy.context.view_layer.update()
        zmin = min((self.arm.matrix_world @ self.arm.pose.bones[f].tail).z for f in self.feet if f in self.arm.pose.bones)
        self.arm.matrix_world = Matrix.Translation((0, 0, gz(x, y) - zmin + 0.1)) @ self.arm.matrix_world

def _R(ax=0.0, ay=0.0, az=0.0):
    return Matrix.Rotation(az, 3, "Z") @ Matrix.Rotation(ay, 3, "Y") @ Matrix.Rotation(ax, 3, "X")

def armored_weights(t):
    ram = smooth(*BEATS["ram"], t) * (1 - smooth(T_IMP + 0.4 * SLIDE_T, BEATS["slide"][1], t))
    brace = smooth(T_IMP, T_IMP + 0.35, t) * (1 - smooth(*BEATS["straighten"], t))
    run = 1.0 - smooth(T_IMP - 0.05, T_IMP + 0.35, t)
    return run, ram, brace

def armored_rots(t):
    """Bone rotations (rest frame: +X front, +Y left, +Z up; ay>0 leans the upper body forward / swings a limb BACK).
    Normal upright run; only the last 0.4 s the torso twists ~34 deg so the RIGHT shoulder leads (owner 11:38 10/26),
    the head tucks, the legs keep driving; the slide: legs braced and skidding, arms out; then straighten and stand."""
    run, ram, brace = armored_weights(t)
    d = arm_y(t) - arm_y(0.0)
    ph = 2 * math.pi * d / (2 * STEP_LEN)
    sw = math.sin(ph) * 0.62 * run
    kL = 0.95 * max(0.0, math.sin(ph + 1.6)) * run; kR = 0.95 * max(0.0, math.sin(ph + 1.6 + math.pi)) * run
    A = {}
    def add(b, ax=0.0, ay=0.0, az=0.0):
        a = A.setdefault(b, [0.0, 0.0, 0.0]); a[0] += ax; a[1] += ay; a[2] += az
    add("L_Thigh", ay=-sw); add("R_Thigh", ay=sw); add("L_Calf", ay=kL); add("R_Calf", ay=kR)
    add("L_Upperarm", ay=0.55 * sw * (1 - ram)); add("R_Upperarm", ay=-0.55 * sw * (1 - ram))
    add("L_Forearm", ay=-0.5 * run); add("R_Forearm", ay=-0.5 * run)
    add("Waist", ay=0.20 * run + 0.30 * ram); add("Spine01", ay=0.10 * run + 0.16 * ram, az=0.60 * ram)
    add("NeckTwist01", ay=0.18 * run + 0.45 * ram, az=-0.25 * ram)
    add("R_Upperarm", ax=0.55 * ram); add("R_Forearm", ay=-0.8 * ram)           # right arm tucked in, shoulder leading
    add("L_Upperarm", ay=0.6 * ram, ax=0.25 * ram)                               # left arm swung back
    # slide: front (left) leg braced forward, back (right) leg trailing, body leaning back, arms out
    add("L_Thigh", ay=-0.55 * brace); add("L_Calf", ay=0.30 * brace)
    add("R_Thigh", ay=0.45 * brace); add("R_Calf", ay=0.45 * brace)
    add("Waist", ay=-0.12 * brace); add("L_Upperarm", ax=0.75 * brace); add("R_Upperarm", ax=-0.75 * brace)
    st = 1.0 - max(run, brace)
    if st > 0:                                                                   # standing: breathing, a slow look round
        add("Spine01", ay=0.03 * math.sin(1.3 * t) * st)
        t_st = BEATS["stand"][0]
        add("NeckTwist01", az=0.22 * math.sin(0.35 * (t - t_st)) * smooth(t_st, t_st + 2.0, t), ay=0.05 * st)
        add("L_Upperarm", ax=0.12 * st); add("R_Upperarm", ax=-0.12 * st)
    return {b: _R(*a) for b, a in A.items()}

def armored_update(t):
    TA = S.get("TA")
    if not TA:
        return
    run, ram, brace = armored_weights(t)
    TA.pose(armored_rots(t))
    lean = 0.03 * run + 0.06 * ram - 0.05 * brace
    v0, v1 = BEATS["vanish"]
    gone = t >= v1
    for me in TA.meshes:
        if me.hide_render != gone:
            me.hide_render = gone
    if gone:
        return
    TA.place(0.0, arm_y(t), 0.0, lean=lean)
    u = smooth(v0, v1, t)                                    # v5: sinks into his own steam (and shrinks a little)
    if u > 0:
        TA.arm.matrix_world = Matrix.Translation((0.0, 0.0, -16.0 * u * u)) @ TA.arm.matrix_world

# ====================================================================== dust, debris, steam, slide (cards + keyframe-free objects)
def footfalls():
    """(t, x, y) of every footfall on the run (alternating feet), plus the skid furrow emitters."""
    out = []
    d_end = arm_y(T_IMP) - arm_y(0.0)
    k = 0
    while (k + 0.5) * STEP_LEN < d_end:
        d = (k + 0.5) * STEP_LEN
        t = t_at_y(arm_y(0.0) + d)
        out.append((t, 1.6 if k % 2 else -1.6, arm_y(t) + 1.0)); k += 1
    return out

def build_dust():
    rng = np.random.default_rng(13)
    # self-lit ochre dust (reads in the wall's shadow and over the brown avenue; g1 uses the same trick, "g1dust")
    SMC.KINDS.setdefault("g2dust", dict(col=lin("#dcc49a"), emit=float(os.environ.get("G2_DUST_EMIT", "0.6")), thr=0.26, ns=2.0, lit=True))
    D = SMC.SmokeCards("G2Dust")
    ochre = np.array(lin("#dcc49a")); dark = np.array(lin("#a8875e")); ball = np.array(lin("#e2c48a"))
    # footfall puffs (4 per step, 1.2 s) + scuff ring
    for t, x, y in footfalls():
        n = 4
        P = np.column_stack([x + rng.normal(0, 1.2, n), y + rng.normal(0, 1.5, n), np.full(n, 1.2)])
        V = np.column_stack([rng.normal(0, 4, n), rng.normal(-2, 3, n), rng.uniform(1, 3, n)])
        D.add_many(t + rng.uniform(0, 0.08, n), P, V, r0=3.0, r1=rng.uniform(8, 11, n), life=rng.uniform(1.2, 1.8, n), rise=1.0,
                   color=ochre * rng.uniform(0.9, 1.1, (n, 1)), kind="g2dust", alpha=0.85, tau=0.5, fade_in=0.04)
    # ground run trail behind him: lingering 6-8 s, 20-30 m wide
    te = np.arange(0.05, T_IMP, 0.22); n = len(te)
    P = np.column_stack([rng.normal(0, 3, n), [arm_y(t) - 6 for t in te], rng.uniform(2, 5, n)])
    V = np.column_stack([rng.normal(0, 2.5, n), rng.uniform(4, 9, n), rng.uniform(0.5, 1.5, n)])
    D.add_many(te, P, V, r0=7.0, r1=rng.uniform(13, 18, n), life=rng.uniform(6, 8, n), rise=0.6,
               color=ochre * 0.95, kind="g2dust", alpha=0.6, tau=1.2, fade_in=0.3)
    # IMPACT (QA v2): the burst goes mostly NORTH out of the breach - a dense lumpy ochre ball for ~1 s, then it thins
    # so he reads again by 17-18 s; the south side only gets a low ground ring (no sprite on the south face)
    n = 18
    a = rng.uniform(math.pi * 1.1, math.pi * 1.9, n)
    P = np.column_stack([np.cos(a) * 5, -15 + np.sin(a) * 2, rng.uniform(1.0, 3.5, n)])
    V = np.column_stack([np.cos(a) * rng.uniform(12, 22, n), np.sin(a) * rng.uniform(8, 16, n), rng.uniform(0.5, 2.5, n)])
    D.add_many(T_IMP + rng.uniform(0.05, 0.4, n), P, V, r0=3.5, r1=rng.uniform(8, 12, n), life=rng.uniform(3.0, 4.5, n), rise=0.4,
               color=ochre, kind="g2dust", alpha=0.6, tau=0.9, fade_in=0.05)
    n = 76                                                                   # the burst ball out of the north face
    te = T_IMP + 0.08 + rng.uniform(0, 0.75, n)
    P = np.column_stack([rng.normal(0, 3.0, n), rng.uniform(5, 13, n), rng.uniform(2, 20, n)])
    V = np.column_stack([rng.normal(0, 9, n), rng.uniform(12, 32, n), rng.uniform(2, 15, n)])
    D.add_many(te, P, V, r0=5.5, r1=rng.uniform(12, 17, n), life=rng.uniform(2.2, 3.4, n), rise=2.2,
               color=np.where(rng.random((n, 1)) < 0.3, dark, ball) * rng.uniform(0.92, 1.08, (n, 1)), kind="g2dust",
               alpha=1.0, tau=0.5, fade_in=0.05)
    n = 26                                                                   # thinning haze he stands in at 18-23 s (behind him)
    te = T_IMP + 0.9 + rng.uniform(0, 1.2, n)
    P = np.column_stack([rng.uniform(-4, 34, n), rng.uniform(28, 78, n), rng.uniform(4, 18, n)])
    D.add_many(te, P, np.column_stack([rng.normal(0, 1.5, n), rng.uniform(0, 2, n), rng.uniform(0, 1, n)]), r0=9, r1=rng.uniform(16, 24, n),
               life=rng.uniform(7, 10, n), rise=0.8, color=ball, kind="g2dust", alpha=0.24, tau=1.0, fade_in=0.6)
    # the slide: two dust furrows along his feet + rubble spray
    te = np.arange(T_IMP + 0.1, BEATS["slide"][1] - 0.15, 0.09)
    for sx in (-2.3, 2.3):
        n = len(te)
        P = np.column_stack([np.full(n, sx) + rng.normal(0, 0.5, n), [arm_y(t) + 2.0 for t in te], np.full(n, 1.0)])
        V = np.column_stack([np.sign(sx) * rng.uniform(3, 7, n), rng.uniform(4, 10, n) * np.array([arm_v(t) / RUN_V for t in te]),
                             rng.uniform(2, 5, n)])
        D.add_many(te, P, V, r0=2.5, r1=rng.uniform(6, 9, n), life=rng.uniform(4, 6, n), rise=0.8, color=ochre * 0.95,
                   kind="g2dust", alpha=0.8, tau=0.7, fade_in=0.05)
    D.build(S["coll"]); S["cards"].append((D, (WIND[0] * 0.35, WIND[1] * 0.35)))
    # flash, splash, steam (no wind on the flash)
    X = SMC.SmokeCards("G2Flash")
    X.add(T_IMP, (0, -13, 9), r0=10, r1=26, life=0.22, kind="glow", color=(1.0, 0.93, 0.72), alpha=1.0, fade_in=0.01)
    X.add(T_IMP + 0.02, (0, -10, 14), r0=6, r1=14, life=0.3, kind="glow", color=(1.0, 0.8, 0.45), alpha=1.0, fade_in=0.01)
    ts = t_at_y(16.0)
    n = 16
    X.add_many(ts + rng.uniform(0, 0.4, n), np.column_stack([rng.normal(0, 3, n), rng.uniform(15, 21, n), np.full(n, 1.0)]),
               np.column_stack([rng.normal(0, 6, n), rng.uniform(2, 8, n), rng.uniform(5, 11, n)]), r0=1.5, r1=rng.uniform(4, 6.5, n),
               life=rng.uniform(1.0, 1.6, n), rise=0.0, color=(0.82, 0.88, 0.92), kind="steam", alpha=0.9, tau=0.6, fade_in=0.02)
    X.build(S["coll"]); S["cards"].append((X, (0.0, 0.0)))
    St = SMC.SmokeCards("G2Steam")
    te = np.arange(BEATS["steam"], BEATS["vanish"][1], 0.22); n = len(te)
    ya = np.array([arm_y(t) for t in te])
    St.add_many(te, np.column_stack([rng.normal(0, 0.3, n), ya + 1.9, np.full(n, 13.3)]),
                np.column_stack([rng.normal(0, 0.6, n), np.full(n, 2.2), rng.uniform(0.5, 1.5, n)]), r0=0.6, r1=rng.uniform(2.6, 3.8, n),
                life=rng.uniform(1.8, 2.6, n), rise=2.0, kind="steam", alpha=0.85, tau=0.8)
    te = np.arange(BEATS["steam"] + 0.4, BEATS["vanish"][1], 0.35); n = len(te)
    ya = np.array([arm_y(t) for t in te]); sx = np.where(np.arange(n) % 2 == 0, -3.0, 3.0)
    St.add_many(te, np.column_stack([sx + rng.normal(0, 0.8, n), ya + rng.normal(0, 0.8, n), rng.uniform(10, 12.5, n)]),
                np.column_stack([sx * 0.4, rng.normal(0, 0.5, n), rng.uniform(1, 2, n)]), r0=1.0, r1=rng.uniform(4, 6, n),
                life=rng.uniform(2.5, 3.5, n), rise=2.8, kind="steam", alpha=0.7, tau=1.0)
    # v5 (owner): the vanish - a steam burst that swallows the body (sinks 11.1-12.1), then a lingering steam pillar
    v0, v1 = BEATS["vanish"]; ya = arm_y(v0); n = 70
    St.add_many(v0 + rng.uniform(0.0, 0.7, n), np.column_stack([rng.normal(0, 4, n), ya + rng.normal(0, 4, n), rng.uniform(1, 24, n)]),
                np.column_stack([rng.normal(0, 5, n), rng.normal(0, 5, n), rng.uniform(3, 10, n)]), r0=4.0, r1=rng.uniform(13, 20, n),
                life=rng.uniform(3.5, 5.5, n), rise=2.5, kind="steam", alpha=0.9, tau=0.9, fade_in=0.08, color=(0.88, 0.90, 0.92))
    te = np.arange(v1, DUR + 0.1, 0.3); n = len(te)
    St.add_many(te, np.column_stack([rng.normal(0, 3, n), ya + rng.normal(0, 3, n), rng.uniform(0, 4, n)]),
                np.column_stack([rng.normal(0, 1, n), rng.normal(0, 1, n), rng.uniform(4, 7, n)]), r0=3.0, r1=rng.uniform(9, 14, n),
                life=rng.uniform(4, 6, n), rise=2.0, kind="steam", alpha=0.45 * np.clip(1.0 - (te - v1) / 14.0, 0.15, 1.0), tau=1.0)
    St.build(S["coll"]); S["cards"].append((St, (-1.2, 0.3)))

def build_smoke_columns():
    """Thin wavy + thick dark columns over Shiganshina (g1's sites, pre-rolled), bending WEST up high."""
    rng = np.random.default_rng(11)
    C = SMC.SmokeCards("G2Smoke")
    sites = [(95, -470), (-100, -662), (205, -575), (35, -640), (150, -640), (62, -540), (-62, -612), (-130, -652),
             (95, -80), (60, -150)]                                      # + 2 just south-east of the inner gate (off the sightline)
    starts = [-18.2, -17.0, -15.8, -14.6, -13.4, -16.4, -12.2, -15.0, 2.0, 6.0]
    for c, ((bx, by), ton) in enumerate(zip(sites, starts)):
        bz = (G1.terrace_h(bx, by) if G1 else 0.0) + L.height(bx, by)
        dark = c in (1, 3, 6, 8)
        te = np.arange(max(ton, -12.0), DUR + 0.5, 0.12); m = len(te)
        ph = c * 1.7
        vx = 2.4 * np.sin(0.75 * te + ph); vy = 1.6 * np.cos(0.55 * te + ph * 0.7)
        P = np.column_stack([np.full(m, bx) + rng.normal(0, 1.0, m), np.full(m, by) + rng.normal(0, 1.0, m), np.full(m, bz + 3.0)])
        V = np.column_stack([vx * 1.6, vy * 1.6, rng.uniform(17.0, 21.0, m)])
        col = (0.12, 0.10, 0.09) if dark else (0.40, 0.38, 0.35)
        C.add_many(te, P, V, r0=rng.uniform(4.0, 5.5, m) * (1.6 if dark else 1.0), r1=rng.uniform(12, 17, m) * (1.3 if dark else 1.0),
                   life=11.5, rise=0.0, color=col, kind="smoke", alpha=(0.72 if dark else 0.5), fade_in=0.4)
        n = 8
        C.add_many(min(ton, -1.0) + rng.uniform(0, 1.0, n), np.column_stack([bx + rng.normal(0, 3, n), by + rng.normal(0, 3, n), np.full(n, bz + 1.0)]),
                   None, r0=1.5, r1=2.6, life=60.0, rise=0.0, kind="fire", alpha=0.8, fade_in=0.4)
    C.build(S["coll"]); S["smoke"] = C
    print(f"[g2] smoke columns {len(sites)}, cards {C.count()}")

FIRE_N = int(os.environ.get("G2_FIRES", "26"))          # new fires that ignite during g2 (owner 07:34: burning Shiganshina)
FIRE_LIGHTS = int(os.environ.get("G2_FIRE_LIGHTS", "14"))

def fire_sites():
    """New fire sites on real houses (g1_set Town points, alive) across the district, >= 50 m apart and from g1's 10
    columns, off the avenue / apron / canal; ignition times spread over BEATS fires.  Deterministic."""
    rnd = random.Random(845)
    pts = []
    ob = bpy.data.objects.get("Town")
    if ob is not None:
        me = ob.data; n = len(me.vertices)
        co = np.zeros(3 * n); me.vertices.foreach_get("co", co); co = co.reshape(-1, 3)
        born = np.full(n, -1e9); dead = np.full(n, 1e9)
        for nm, arr in (("born", born), ("dead", dead)):
            if nm in me.attributes:
                me.attributes[nm].data.foreach_get("value", arr)
        yr = float(bpy.context.scene.get("year", 845.0))
        mw = np.array(ob.matrix_world)
        co = co @ mw[:3, :3].T + mw[:3, 3]
        pts = [tuple(c) for c, b_, d in zip(co, born, dead) if b_ <= yr < d]          # houses standing in 845
    if not pts:                                              # fallback: district grid
        pts = [(x, y, L.height(x, y)) for x in range(-270, 271, 12) for y in range(-700, -60, 12)]
    old = [(95, -470), (-100, -662), (205, -575), (35, -640), (150, -640), (62, -540), (-62, -612), (-130, -652), (95, -80), (60, -150)]
    rnd.shuffle(pts)
    sites = []
    for x, y, z in pts:
        if len(sites) >= FIRE_N:
            break
        if not L.in_district(x, y, 25.0) or y > -95 or abs(x) < 22 or abs(x - L.CX) < 34:
            continue
        if any((x - a) ** 2 + (y - b) ** 2 < 50.0 ** 2 for a, b in old) or any((x - a) ** 2 + (y - b) ** 2 < 50.0 ** 2 for a, b, *_ in sites):
            continue
        sites.append((x, y, z))
    f0, f1 = BEATS["fires"]
    order = sorted(range(len(sites)), key=lambda i: sites[i][1] + rnd.uniform(-120, 120))   # roughly south (outer gate) first
    out = []
    for k, i in enumerate(order):
        x, y, z = sites[i]
        out.append((x, y, z, f0 + (f1 - f0) * k / max(1, len(order) - 1) + rnd.uniform(-0.4, 0.4)))
    return out

def build_fires(coll):
    """Owner 07:34: Shiganshina BURNING at dusk.  Every site (g1's 10 + FIRE_N new ones): a roof fire of flickering flame
    cards that grows after ignition, a soft orange glow halo, a dense dark / grey smoke column (bends west with the wind,
    reaches 150-250 m by the aerial) and, for the first FIRE_LIGHTS sites, a shadowless orange point light that warms the
    surrounding roofs.  g1's 10 sites keep their t 0 look (their existing columns) and only gain flames from 2 s on."""
    rng = np.random.default_rng(29)
    F = SMC.SmokeCards("G2Fires"); C = SMC.SmokeCards("G2FireSmoke")
    new = fire_sites()
    th = G1.terrace_h if G1 else (lambda x, y: 0.0)
    old = [(95, -470), (-100, -662), (205, -575), (35, -640), (150, -640), (62, -540), (-62, -612), (-130, -652), (95, -80), (60, -150)]
    sites = [(x, y, L.height(x, y) + th(x, y), 2.0 + 0.35 * k, True) for k, (x, y) in enumerate(old)] +             [(x, y, max(z, L.height(x, y) + th(x, y)), ton, False) for x, y, z, ton in new]
    S["fire_lights"] = []
    for k, (x, y, bz, ton, is_old) in enumerate(sites):
        roof = bz + 7.5
        # flames: 3 tiers that come in one after another (the house catches, then the roof is ablaze)
        for tier, (dt, n, r0, r1, sp) in enumerate(((0.0, 5, 1.8, 3.6, 2.5), (1.6, 7, 3.0, 6.0, 5.0), (4.0, 8, 4.0, 8.5, 7.0))):
            P = np.column_stack([x + rng.normal(0, sp, n), y + rng.normal(0, sp, n), roof + rng.uniform(-1.5, 3.0, n)])
            F.add_many(ton + dt + rng.uniform(0, 0.6, n), P, None, r0=r0, r1=rng.uniform(r1 * 0.85, r1 * 1.15, n), life=80.0,
                       rise=0.0, kind="fire", alpha=0.95, fade_in=0.8)
        F.add(ton + 1.0, (x, y, roof + 4.0), r0=10.0, r1=rng.uniform(28, 36), life=80.0, kind="glow", color=(1.0, 0.40, 0.10),
              alpha=0.42, fade_in=3.0)
        # v5 night: the smoke column lit from below (a dim orange glow card in its lower part)
        F.add(max(ton + 3.0, BEATS["night"][0]), (x, y, roof + 26.0), r0=14.0, r1=rng.uniform(34, 44), life=80.0, kind="glow",
              color=(1.0, 0.32, 0.07), alpha=0.22, fade_in=4.0)
        # smoke column (QA stills: thicker / denser): the new sites in full; g1's 10 keep their thin columns from
        # build_smoke_columns and thicken from 2 s on (a wide sparse layer around them)
        if True:
            te = np.arange(ton + 0.3, DUR + 0.5, 0.2 if is_old else 0.12); m = len(te)
            dark = k % 3 != 2
            ph = k * 1.3
            vx = 2.0 * np.sin(0.7 * te + ph); vy = 1.4 * np.cos(0.5 * te + ph * 0.7)
            age = np.clip((te - ton) / 4.0, 0.15, 1.0)                     # the column thickens as the fire grows
            P = np.column_stack([np.full(m, x) + rng.normal(0, 1.5, m), np.full(m, y) + rng.normal(0, 1.5, m), np.full(m, roof + 3.0)])
            V = np.column_stack([vx * 1.5, vy * 1.5, rng.uniform(12.0, 17.0, m)])
            col = (0.11, 0.095, 0.085) if dark else (0.34, 0.31, 0.29)
            C.add_many(te, P, V, r0=rng.uniform(6.0, 9.0, m) * age, r1=rng.uniform(30, 44, m) * (0.5 + 0.5 * age), life=13.0,
                       rise=0.0, color=col, kind="smoke", alpha=(0.6 if is_old else (0.85 if dark else 0.7)), fade_in=0.35)
        if len(S["fire_lights"]) < FIRE_LIGHTS and (not is_old or k % 2 == 0):    # g1 sites: every other one
            if True:
                ld = bpy.data.lights.new(f"G2FireL{k}", "POINT"); ld.energy = 0.0; ld.color = (1.0, 0.48, 0.16)
                ld.shadow_soft_size = 6.0; ld.use_shadow = False
                try:
                    ld.use_custom_distance = True; ld.cutoff_distance = 110.0
                except Exception:
                    pass
                lo = bpy.data.objects.new(f"G2FireL{k}", ld); coll.objects.link(lo); lo.location = (x, y, roof + 12.0)
                S["fire_lights"].append((lo, ton, k))
    F.build(S["coll"]); S["cards"].append((F, (WIND[0] * 0.2, WIND[1] * 0.2)))
    C.build(S["coll"]); S["firesmoke"] = C
    print(f"[g2] fires: {len(sites)} sites ({len(new)} new, ignite {BEATS['fires'][0]}-{BEATS['fires'][1]} s), flame cards {F.count()}, "
          f"smoke cards {C.count()}, lights {len(S['fire_lights'])}")

def fires_update(t):
    E = float(os.environ.get("G2_FIRE_E", "40000")) * (1.0 + 0.6 * smooth(*BEATS["night"], t))
    for lo, ton, k in S.get("fire_lights", ()):
        u = smooth(ton + 0.5, ton + 5.0, t)
        lo.data.energy = E * u * (0.85 + 0.15 * math.sin(7.3 * t + k * 1.7) * math.sin(3.1 * t + k))
        lo.hide_render = u <= 0.0

def smoke_wind(t):
    """g1 leaves the columns at (-0.5, 0.15); ease into the bible's west wind over the first 4 s."""
    u = smooth(0.0, 4.0, t)
    return (-0.5 + (WIND[0] + 0.5) * u, 0.15 + (WIND[1] - 0.15) * u)

def ballistic(p0, p1, apex, t0, t):
    """Position on a ballistic arc p0 -> p1 peaking at z = apex, launched at t0 (real gravity); (pos, landed, T)."""
    z0, z1 = p0.z, p1.z
    apex = max(apex, z0 + 0.5, z1 + 0.5)
    vz = math.sqrt(2 * G * (apex - z0)); T = vz / G + math.sqrt(2 * (apex - z1) / G)
    a = min(max(t - t0, 0.0), T)
    p = p0.lerp(p1, a / T); p.z = z0 + vz * a - 0.5 * G * a * a
    return p, t - t0 >= T, T

def build_debris(coll):
    """50 chunks on precomputed arcs: stone fan north (8 big ones peaking 60-80 m over the wall), brick + timber south and
    up off the gatehouse front, the two crest leaves broken into slabs; rubble ploughed ahead of his feet in the slide."""
    M = S["M"]; rnd = random.Random(213)
    protos = [G1.lump_mesh(f"G2Chunk{i}", 300 + i) for i in range(8)] if G1 else []
    for p in protos:
        p.materials.append(M["chunk"])
    D = []
    def add(ob, p0, p1, apex, t0, spin):
        ob.hide_render = True
        D.append(dict(ob=ob, p0=p0, p1=p1, apex=apex, t0=t0, ax=Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1))).normalized(),
                      w=spin, r0=Euler((rnd.uniform(0, 6), rnd.uniform(0, 6), rnd.uniform(0, 6)))))
    for k in range(40):
        big = k < 8
        size = rnd.uniform(3.2, 6.0) if big else rnd.uniform(0.9, 3.4)
        ob = bpy.data.objects.new(f"G2Debris{k}", protos[k % len(protos)] if protos else None); coll.objects.link(ob)
        ob.scale = (size, size * rnd.uniform(0.7, 1.0), size * rnd.uniform(0.6, 0.9))
        p0 = Vector((rnd.uniform(-5.5, 5.5), rnd.uniform(-6, 4), rnd.uniform(3, 23)))
        ang = math.radians(rnd.uniform(-32, 32))
        if big:
            dist = rnd.uniform(40, 90); apex = rnd.uniform(60, 80)
        else:
            dist = (rnd.uniform(20, 60) if size > 2.2 else rnd.uniform(35, 150)); apex = rnd.uniform(max(p0.z + 3, 20), 45)
        p1 = Vector((math.sin(ang) * dist, 6 + math.cos(ang) * dist, 0.0))
        p1.z = gz(p1.x, p1.y) + size * 0.3
        if abs(p1.x) < 6 and 5 < p1.y < 60:                      # keep his slide lane clear
            p1.x += 9 * (1 if p1.x >= 0 else -1)
        add(ob, p0, p1, apex, T_IMP + rnd.uniform(0, 0.12), rnd.uniform(1.5, 5.0))
    bm = bmesh.new(); L.box(bm, (0, 0, 0), (1.0, 1.0, 1.0)); brick_me = bpy.data.meshes.new("G2BrickChunk"); bm.to_mesh(brick_me); bm.free()
    brick_me.materials.append(M["brick"])
    for k in range(10):                                           # brick spray south and up off the gatehouse front
        ob = bpy.data.objects.new(f"G2Brick{k}", brick_me); coll.objects.link(ob)
        ob.scale = (rnd.uniform(1.0, 2.6), rnd.uniform(0.8, 1.6), rnd.uniform(0.6, 1.4))
        p0 = Vector((rnd.uniform(-6, 6), rnd.uniform(-12, -7), rnd.uniform(3, 9)))
        p1 = Vector((p0.x + rnd.uniform(-22, 22), rnd.uniform(-60, -22), 0.0)); p1.z = gz(p1.x, p1.y) + 0.4
        add(ob, p0, p1, rnd.uniform(14, 30), T_IMP + rnd.uniform(0, 0.08), rnd.uniform(3, 8))
    bm = bmesh.new(); L.box(bm, (0, 0, 0), (0.6, 0.6, 1.0)); tim_me = bpy.data.meshes.new("G2Beam"); bm.to_mesh(tim_me); bm.free()
    tim_me.materials.append(M["timber"])
    for k in range(6):
        ob = bpy.data.objects.new(f"G2Beam{k}", tim_me); coll.objects.link(ob); ob.scale = (1, 1, rnd.uniform(4, 8))
        p0 = Vector((rnd.uniform(-3, 3), rnd.uniform(-8, 0), rnd.uniform(2, 8)))
        p1 = Vector((rnd.uniform(-25, 25), rnd.uniform(25, 90), 0.0)); p1.z = gz(p1.x, p1.y) + 0.4
        if abs(p1.x) < 6: p1.x += 10
        add(ob, p0, p1, rnd.uniform(18, 35), T_IMP + rnd.uniform(0, 0.1), rnd.uniform(3, 9))
    for tag, side in (("S", -1), ("N", 1)):                       # the crest leaves break into 3 slabs each
        for k in range(3):
            ob = bpy.data.objects.new(f"G2LeafSlab{tag}{k}", brick_me); coll.objects.link(ob)
            ob.scale = (rnd.uniform(3.5, 5.0), 1.3, rnd.uniform(3.5, 5.0))
            zb = leaf_bottom(T_IMP) if tag == "S" else 10.0
            p0 = Vector((rnd.uniform(-3, 3), side * 6.9, zb + 2 + 4 * k))
            p1 = Vector((rnd.uniform(-20, 20), rnd.uniform(30, 75), 0.0)); p1.z = gz(p1.x, p1.y) + 1.5
            if abs(p1.x) < 7: p1.x += 11 * (1 if p1.x >= 0 else -1)
            add(ob, p0, p1, rnd.uniform(25, 45) if side < 0 else rnd.uniform(18, 30), T_IMP + 0.03 + 0.02 * k, rnd.uniform(1, 3))
    S["debris"] = D
    # rubble ploughed ahead of his feet during the slide (pushed, then left in a heap at the stop)
    R_ = []
    for k in range(12):
        ob = bpy.data.objects.new(f"G2Plough{k}", protos[k % len(protos)] if protos else None); coll.objects.link(ob)
        s_ = rnd.uniform(1.2, 2.8); ob.scale = (s_, s_ * 0.9, s_ * 0.7); ob.hide_render = True
        ob.rotation_euler = (rnd.uniform(0, 6), rnd.uniform(0, 6), rnd.uniform(0, 6))
        R_.append((ob, rnd.uniform(-4.5, 4.5), rnd.uniform(4.5, 9.0), s_))
    S["plough"] = R_
    # two dark furrows dug by the feet (grow with the slide)
    bm = bmesh.new()
    for v in [(-1.2, 0, 0), (1.2, 0, 0), (1.2, 1, 0), (-1.2, 1, 0)]:
        bm.verts.new(v)
    bm.faces.new(bm.verts[:])
    fme = bpy.data.meshes.new("G2Furrow"); bm.to_mesh(fme); bm.free(); fme.materials.append(M["furrow"])
    S["furrows"] = []
    for sx in (-2.3, 2.3):
        ob = bpy.data.objects.new(f"G2Furrow{sx:+.0f}", fme); coll.objects.link(ob)
        ob.location = (sx, 13.5, gz(sx, 30.0) + 0.08); ob.hide_render = True
        S["furrows"].append(ob)

def debris_update(t):
    for d in S["debris"]:
        ob = d["ob"]
        if t < d["t0"]:
            if not ob.hide_render: ob.hide_render = True
            continue
        if ob.hide_render: ob.hide_render = False
        p, landed, T = ballistic(d["p0"], d["p1"], d["apex"], d["t0"], t)
        ob.location = p
        a = d["w"] * min(t - d["t0"], T)
        q = d["r0"].to_quaternion() @ Matrix.Rotation(a, 3, d["ax"]).to_quaternion()
        ob.rotation_mode = "QUATERNION"; ob.rotation_quaternion = q
    ya = arm_y(t)
    for ob, x, off, s_ in S["plough"]:
        if t < T_IMP + 0.2:
            ob.hide_render = True; continue
        ob.hide_render = False
        y = max(ya + off, 13.0 + off * 0.3)
        ob.location = (x * (1 + 0.15 * smooth(T_IMP, BEATS["slide"][1], t)), y, gz(x, y) + s_ * 0.25)
    for ob in S["furrows"]:
        ln = ya + 1.0 - 13.5
        ob.hide_render = ln < 0.5 or t < T_IMP
        ob.scale = (1.0, max(0.01, ln), 1.0)

# ====================================================================== followers (3 pure titans, swarm845 style) + ferries
class Titans:
    """3 swarm845-style titans with given heights (one deforming mesh)."""
    def __init__(self, name, specs, coll):
        SW = sys.modules.get("swarm845") or __import__("swarm845")
        self.SW = SW
        g = SW.Geo(); fm = []
        mats = [L.mat(f"{name}_tskin{i}", c, 0.65) for i, c in enumerate(SW.T_SKINS)] + \
               [L.mat(f"{name}_thair{i}", c, 0.7) for i, c in enumerate(SW.T_HAIRS)] + [L.mat(f"{name}_teeth", (0.85, 0.8, 0.7), 0.5)]
        self.h = []
        for j, sp in enumerate(specs):
            n0 = len(g.fc); SW.titan_geo(g, j, sp); self.h.append(sp["H"])
            base = [sp["skin"], len(SW.T_SKINS) + (sp["hair"] or 0), len(SW.T_SKINS) + len(SW.T_HAIRS)]
            fm += [base[c] for c in g.fc[n0:]]
        self.R = g.finish(); self.n = len(specs); self.h = np.array(self.h)
        self.ob = SW._mesh(name, self.R, g.f, fm, mats, coll)

    def set(self, pos, yaw, dist, moving):
        n = self.n; Ar = np.zeros((n, 7)); Ae = np.zeros((n, 7))
        ph = 2 * np.pi * dist / (1.4 * self.h)
        sw = np.sin(ph) * 0.6 * moving
        Ar[:, 1] = sw; Ar[:, 2] = -sw; Ar[:, 3] = -0.7 * sw; Ar[:, 4] = 0.7 * sw; Ar[:, 5] = Ar[:, 4]; Ar[:, 6] = Ar[:, 3]
        p = pos.copy(); p[:, 2] += (0.5 - 0.5 * np.cos(2 * ph)) * 0.04 * self.h * moving
        co = self.SW._deform(self.R, Ar, Ae, -0.12 * moving, np.ones(n), yaw, p)
        self.ob.data.vertices.foreach_set("co", co.astype(np.float32).ravel()); self.ob.data.update()

FOLLOW = [dict(H=9.0, x=-5.0, y0=-540.0, v=9.0, skin=1, hair=0), dict(H=7.0, x=6.0, y0=-585.0, v=8.0, skin=4, hair=None),
          dict(H=5.0, x=-1.0, y0=-640.0, v=7.0, skin=2, hair=1)]

def follower_xy(f, t):
    s = f["v"] * t - max(0.0, t - 18.0) ** 2 * f["v"] / 28.0 if t < 32 else 0     # slow toward the end
    return f["x"] + 1.2 * math.sin(0.25 * t + f["H"]), f["y0"] + s

def build_followers(coll):
    specs = [dict(name=f"f{j}", H=f["H"], g=1.0 + 0.1 * j, al=1.0, hs=1.1, skin=f["skin"], hair=f["hair"]) for j, f in enumerate(FOLLOW)]
    S["followers"] = Titans("G2Followers", specs, coll)

def followers_update(t):
    F = S["followers"]; P = np.zeros((F.n, 3)); dist = np.zeros(F.n); yaw = np.zeros(F.n); mv = np.zeros(F.n)
    for j, f in enumerate(FOLLOW):
        x, y = follower_xy(f, t)
        P[j] = (x, y, gz(x, y)); dist[j] = y - f["y0"]
        x2, y2 = follower_xy(f, t + 0.05)
        yaw[j] = math.atan2(-(x2 - x), max(1e-4, y2 - y)); mv[j] = min(1.0, math.hypot(x2 - x, y2 - y) / 0.05 / 4.0)
    F.set(P, yaw, dist, mv)

def ferry_mesh(M):
    """34 x 10 m oval dark hull, 20 x 5.5 x 3 m cabin with a window row, red-brown barrel roof with 2 rows of discs, two
    long beams, A-frame end trusses with a railing above the roof, a lantern.  Local: bow +y, deck z 1.2."""
    bm = bmesh.new(); n = 28
    ring_lo, ring_hi = [], []
    for k in range(n):
        a = 2 * math.pi * k / n; c, s = math.cos(a), math.sin(a)
        r = (abs(c) ** 2.6 + abs(s) ** 2.6) ** (-1 / 2.6)
        x, y = 5.0 * c * r, 17.0 * s * r * (1 - 0.08 * abs(c))
        ring_lo.append(bm.verts.new((x * 0.8, y * 0.94, -1.3))); ring_hi.append(bm.verts.new((x, y, 1.3)))
    for k in range(n):
        f = bm.faces.new((ring_lo[k], ring_lo[(k + 1) % n], ring_hi[(k + 1) % n], ring_hi[k])); f.material_index = 0
    f = bm.faces.new(ring_hi); f.material_index = 1
    L.box(bm, (0, 0, 2.7), (5.5, 20.0, 3.0), mi=2)                                   # cabin
    for s in (-1, 1):
        for k in range(10):
            L.box(bm, (s * 2.78, -9.0 + 2.0 * k, 3.0), (0.1, 1.1, 1.3), mi=3)          # window row
    r = bmesh.ops.create_cone(bm, cap_ends=True, segments=12, radius1=3.1, radius2=3.1, depth=21.0)
    for v in r["verts"]:
        x, y, z = v.co; v.co = Vector((x, z, max(0.0, y) * 0.55 + 4.2))
    for f in {f for v in r["verts"] for f in v.link_faces}:
        f.material_index = 4
    for s in (-1, 1):
        for k in range(8):
            L.cyl(bm, (s * 1.2, -8.4 + 2.4 * k, 5.75), (s * 1.2, -8.4 + 2.4 * k, 5.9), 0.55, 0.55, seg=8, mi=5)
        L.box(bm, (s * 1.6, 0, 6.2), (0.25, 27.0, 0.25), mi=6)                        # long beams
    for e in (-1, 1):
        for s in (-1, 1):
            L.cyl(bm, (s * 4.2, e * 13.3, 1.3), (s * 0.4, e * 13.3, 6.6), 0.18, 0.18, seg=5, mi=6)
        L.box(bm, (0, e * 13.3, 6.7), (4.0, 0.25, 0.25), mi=6)
    L.box(bm, (2.9, 10.2, 4.5), (0.5, 0.5, 0.7), mi=7)                                # lantern
    me = bpy.data.meshes.new("G2Ferry"); bm.to_mesh(me); bm.free()
    for m in (M["hull"], M["deck"], M["cabin"], M["glass"], M["roof"], M["disc"], M["timber"], M["lantern"]):
        me.materials.append(m)
    return me

FERRIES = [dict(name="F1", y0=300.0, lane=0.0, v=8.0, t0=-1e9), dict(name="F2", y0=150.0, lane=2.0, v=8.0, t0=-1e9),
           dict(name="F3", y0=60.0, lane=-8.5, v=8.0, t0=BEATS["f3_castoff"]), dict(name="F4", y0=100.0, lane=8.5, v=7.0, t0=13.0),
           # v5 (owner): the evacuation readable from the air - more refugee boats already under way north on the river
           dict(name="F5", y0=470.0, lane=-9.0, v=7.5, t0=-1e9), dict(name="F6", y0=640.0, lane=8.0, v=8.5, t0=-1e9),
           dict(name="F7", y0=820.0, lane=-6.0, v=7.0, t0=-1e9), dict(name="F8", y0=1010.0, lane=7.0, v=8.0, t0=-1e9)]

def ferry_s(f, t):
    """Distance travelled along the canal (8 m/s, F3 accelerates from rest after casting off)."""
    if f["v"] == 0.0 or t < f["t0"]:
        return 0.0
    a = t - f["t0"]
    if f["t0"] < -1e8:
        return f["v"] * t
    acc = 1.6
    ta = f["v"] / acc
    return 0.5 * acc * a * a if a < ta else 0.5 * acc * ta * ta + f["v"] * (a - ta)

def ferry_pose(f, t):
    y = f["y0"] + ferry_s(f, t)
    lane = f["lane"] * (1 - smooth(f["t0"] + 1.0, f["t0"] + 7.0, t)) if f["name"] == "F3" else f["lane"]
    c = canal_cx(y); c2 = canal_cx(y + 2.0)
    yaw = math.atan2(-(c2 - c), 2.0)
    return Vector((c + lane, y, water_z(y) - 0.2 + 0.06 * math.sin(1.3 * t + f["y0"]))), yaw

def build_ferries(coll):
    me = ferry_mesh(S["M"]); S["ferries"] = []
    nper = int(int(os.environ.get("G2_DECK_N", "80")))
    for i, f in enumerate(FERRIES):
        o = bpy.data.objects.new(f"G2Ferry{f['name']}", me); coll.objects.link(o)
        if PK:
            ins = PK.crowd(["civilian"], (0, 0, 7.4, 31.0), nper, pose="stand", seed=40 + i, spacing=(0.95, 1.05), jitter=0.2)
            for e in ins:
                lx, ly = e.location.x, e.location.y
                if abs(lx) < 3.0 and abs(ly) < 10.3:             # the cabin
                    e.location = (lx + (3.3 if lx >= 0 else -3.3) * 0.62, ly, 1.3)
                e.location.z = 1.3
                ell = (e.location.x / 4.6) ** 2 + (e.location.y / 16.0) ** 2
                if ell > 1.0:
                    e.hide_render = True
                e.parent = o
        S["ferries"].append((o, f))
    # wakes behind the moving ferries
    W = SMC.SmokeCards("G2Wakes"); rng = np.random.default_rng(3)
    for f in FERRIES:
        if f["v"] == 0:
            continue
        te = np.arange(max(-6.0, f["t0"] + 1.5), DUR + 0.1, 0.4)
        for t in te:
            p, yaw = ferry_pose(f, t)
            W.add(t, (p.x + rng.normal(0, 1.0), p.y - 17.0, p.z + 0.25), vel=(rng.normal(0, 0.8), -0.5, 0), r0=1.5, r1=6.0, life=4.0,
                  kind="steam", color=(0.85, 0.92, 0.92), alpha=0.55, fade_in=0.2)
    W.build(S["coll"]); S["cards"].append((W, (0.0, 0.0)))

def ferries_update(t):
    for o, f in S["ferries"]:
        p, yaw = ferry_pose(f, t)
        o.location = p; o.rotation_euler = (0.0, 0.01 * math.sin(0.8 * t + f["y0"]), yaw)

# ====================================================================== people: Garrison (odm squads, on foot), civilians (people_kit)
def build_garrison(coll):
    import odm
    SQ = odm.Squads("G2Garrison", pscale=1.0, hook=True)
    rnd = random.Random(61)
    sc_t = BEATS["scatter"]
    for gi, x in enumerate(FIELD_X):                 # 4 crew per gun, scatter (BEATS scatter) sideways + toward the gate
        z = gz(x, FIELD_Y)
        for k in range(4):
            p = (x + (-1.3 if k % 2 else 1.3), FIELD_Y + (0.8 if k < 2 else 2.6), z)
            f = SQ.flyer(f"crew{gi}_{k}", kit="garrison", hair=rnd.choice(["brown", "black", "blond"]))
            yaw = odm.yaw_of(np.array([0.0, -1.0, 0.0]))
            t_go = sc_t + rnd.uniform(-0.15, 0.35) + (0.5 if abs(x) > 30 else 0.0)
            f.stand(0.0, t_go, p, yaw, "aim" if k == 0 else "stand")
            side = 1 if x > 0 else -1
            q = (x + side * rnd.uniform(14, 26), FIELD_Y + rnd.uniform(6, 16), 0.0); q = (q[0], q[1], gz(q[0], q[1]))
            T = math.hypot(q[0] - p[0], q[1] - p[1]) / 5.5
            f.walk(t_go, t_go + T, p, q, "run").stand(t_go + T, DUR, q, odm.yaw_of(np.array([-side * 0.3, -1.0, 0.0])), "crouch")
    for k in range(10):                              # across the apron in front of the passage (BEATS apron_run)
        y = rnd.uniform(-24, -15); x0 = rnd.choice((-1, 1)) * rnd.uniform(30, 45)
        x1 = -np.sign(x0) * rnd.uniform(18, 40) if k % 3 else rnd.uniform(-1.5, 1.5)
        y1 = y if k % 3 else -13.5
        t0 = BEATS["apron_run"] + rnd.uniform(0, 0.5)
        p0 = (x0, y, gz(x0, y)); p1 = (x1, y1, gz(x1, y1))
        f = SQ.flyer(f"apron{k}", kit="garrison", hair=rnd.choice(["brown", "black"]))
        T = math.hypot(x1 - x0, y1 - y) / 6.0
        f.stand(0.0, t0, p0, odm.yaw_of(np.array([0, -1.0, 0])), "stand").walk(t0, t0 + T, p0, p1, "run")
        if k % 3:
            f.stand(t0 + T, DUR, p1, odm.yaw_of(np.array([0, -1.0, 0])), "crouch")
        else:
            f.gone(t0 + T)
    for gi, x in enumerate(WALL_GX):                 # 12 on the wall top at the guns
        for k in range(2):
            p = (x + (-1.6 if k else 1.6), -0.2 + 0.6 * k, L.WALL_H + 0.3)
            f = SQ.flyer(f"wall{gi}_{k}", kit="garrison", hair=rnd.choice(["brown", "black", "blond"]))
            f.stand(0.0, DUR, p, odm.yaw_of(np.array([0, -1.0, 0])), "stand" if k else "aim")
    f = SQ.flyer("flung", kit="garrison", hair="brown")  # flung north with the blocks (10:07.7)
    p0 = (3.0, -15.0, gz(3, -15)); p1 = (16.0, 88.0, gz(16, 88))
    f.stand(0.0, T_IMP, p0, odm.yaw_of(np.array([0, -1.0, 0])), "stand").fall(T_IMP + 0.02, T_IMP + 4.2, (2.0, -6.0, 14.0), p1, spin=2.0)
    f.stand(T_IMP + 4.2, DUR, p1, 0.0, "lie")
    SQ.build(coll)
    S["SQ"] = SQ

def build_civilians(coll):
    """Owner 10/27 07:34: the area is ALREADY EVACUATED when he charges - no fleeing column on the apron / avenue / gate road.
    Left: the boarding crowd on the quays at the ferry landings (compresses toward the water after the impact) and a few
    distant stragglers walking away north at the far end of the gate road (y 330-450, 290+ m from his stop).  The old south
    stragglers (v3: ~150 through the gun gaps, 10 freezers) are off by default (G2_SOUTH_N to bring some back)."""
    if not PK:
        return
    rnd = random.Random(17)
    k_n = float(os.environ.get("G2_CROWD", "1.0"))
    civ = [f"civilian:{k}" for k in range(8)]
    # south stragglers (QA v2): ~150 flee through the gun gaps into the passage or break to the sides; 10 freeze at the
    # house fronts.  Pure functions of t (see civilians_update).
    St = []
    for i in range(int(int(os.environ.get("G2_SOUTH_N", "0")) * k_n)):
        pre = rnd.choice(civ)
        if i < 10:                                   # the freezers, pressed against the house fronts on the avenue
            side = 1 if i % 2 else -1
            y0 = rnd.uniform(-330, -70); x0 = side * 11.8
            c = dict(mode="freeze", x0=x0, y0=y0, side=side, v=0.0, ts=0.0, t_in=1e9, t_ap=1e9, xa=0.0)
        else:
            y0 = rnd.uniform(-270, -45); x0 = rnd.uniform(-8.0, 8.0); v = rnd.uniform(4.5, 6.5)
            ts = None
            for k in range(0, 300):
                tt = k * 0.05
                if arm_y(tt) > y0 + v * tt - 35.0:
                    ts = tt; break
            ts = 1e9 if ts is None else ts
            t_in = (-14.0 - y0) / v; t_ap = (-46.0 - y0) / v
            side = (1 if x0 > 0 else -1) if abs(x0) > 0.5 else rnd.choice((-1, 1))
            if t_in < min(ts, 13.0):
                mode = "in"
            elif ts < t_ap:
                mode = "side"
            else:
                mode = "apron"
            gap = min((0.0, 17.0, -17.0), key=lambda g: abs(g - x0))
            c = dict(mode=mode, x0=x0, y0=y0, side=side, v=v, ts=ts, t_in=t_in, t_ap=t_ap, gap=gap, xa=side * rnd.uniform(30, 50))
        c["run"] = PK.person(pre, (c["x0"], c["y0"]), yaw=0.0, pose="run")
        c["std"] = PK.person(pre, (c["x0"], c["y0"]), yaw=0.0, pose="stand")
        St.append(c)
    print("[g2] stragglers: " + ", ".join(f"{m} {sum(1 for c in St if c['mode'] == m)}" for m in ("in", "side", "apron", "freeze")))
    S["south"] = St
    # north: quays (static), apron (static + panic), gate road stream (walk -> run)
    zq = S["zq"]
    Nd = []
    def place(area, n, seed, z=None, pose="stand", stream=False):
        ins = PK.crowd(["civilian"], area, n, pose=pose, seed=seed, spacing=(1.0, 1.1), jitter=0.3, yaw_jitter=1.2)
        for e in ins:
            if z is not None:
                e.location.z = z
            Nd.append(dict(e=e, p0=Vector(e.location), stream=stream))
        return ins
    n_q = int(int(os.environ.get("G2_QUAY_N", "300")) * k_n)
    place((182.0, 62.0, 54.0, 92.0), int(n_q * 0.45), 81, z=zq)                         # apron by the arches
    for s, frac, y0_, y1_ in ((-1, 0.35, 112.0, 330.0), (1, 0.20, 20.0, 300.0)):          # west (dense) / east quays, on the curve
        for k in range(int(n_q * frac)):
            y = rnd.uniform(y0_, y1_)
            if s > 0 and abs(y - 40.0) < 4:                                               # the bridge pylon
                continue
            x = canal_cx(y) + s * rnd.uniform(16.5, 33.5 if s < 0 else 26.0)
            e = PK.person(rnd.choice(civ), (x, y, water_z(y) + 3.62), yaw=rnd.uniform(-math.pi, math.pi), pose="stand")
            Nd.append(dict(e=e, p0=Vector(e.location), stream=False))
    n_r = int(int(os.environ.get("G2_ROAD_N", "7")) * k_n)       # distant stragglers only (v3: 160 walking up the road)
    road = PK.crowd(["civilian"], (0.0, 390.0, 9.0, 120.0), n_r, pose="walk", seed=83, spacing=(6.0,), formation="scatter", yaw_jitter=0.3) if n_r else []
    for e in road:
        Nd.append(dict(e=e, p0=Vector(e.location), stream=True))
    S["north"] = Nd
    # v5 (owner): small refugee columns walking north toward Trost on the gate road and beyond (2 files, readable as
    # dotted lines from the aerial); they keep walking the whole segment (1.5 m/s local)
    Cl = []
    for ci, yh in enumerate((150.0, 290.0, 430.0, 580.0, 730.0, 880.0)):
        for j in range(int(os.environ.get("G2_COL_N", "75"))):          # 3 files x 25 (QA: 2 x 14 did not read from the air)
            dx = 1.3 * (j % 3 - 1) + rnd.uniform(-0.25, 0.25); dy = -1.6 * (j // 3) + rnd.uniform(-0.3, 0.3)
            e = PK.person(rnd.choice(civ), (dx, yh + dy), yaw=0.0, pose="walk", phase=rnd.random())
            Cl.append(dict(e=e, dx=dx, y0=yh + dy, ci=ci))
    S["columns"] = Cl
    print(f"[g2] civilians: south {len(St)} (x2 instances), north {len(Nd)}, columns {len(Cl)}")

def straggler_pos(c, t):
    """(x, y, running, yaw) of one south straggler at t."""
    m = c["mode"]
    if m == "freeze":
        return c["x0"], c["y0"], False, c["side"] * math.pi / 2
    v = c["v"]
    if m == "in":
        y = c["y0"] + v * min(t, c["t_in"])
        u = smooth(-70.0, -36.0, y); w = smooth(-34.0, -16.0, y)
        x = c["x0"] + (c["gap"] - c["x0"]) * u
        x = x + (0.0 - x) * w * 0.9
        return x, y, t < c["t_in"], 0.0
    ts = c["ts"] if m == "side" else c["t_ap"]
    y = c["y0"] + v * min(t, ts)
    u = max(0.0, t - ts)
    if m == "side":
        xg = c["side"] * 12.4; dx = abs(xg - c["x0"]); tx = dx / 4.6
        if u < tx:
            return c["x0"] + (xg - c["x0"]) * u / tx, y, True, -c["side"] * math.pi / 2
        u2 = u - tx
        return xg, y - 3.6 * u2, u2 < 9.0, math.pi                         # flee south along the house fronts
    xg = c["xa"]; dx = abs(xg - c["x0"]); tx = dx / 4.8                     # apron: break sideways across the apron
    if u < tx:
        return c["x0"] + (xg - c["x0"]) * u / tx, y, True, -c["side"] * math.pi / 2
    return xg, y, False, math.pi

def civilians_update(t):
    for c in S.get("south", ()):
        x, y, running, yaw = straggler_pos(c, t)
        vis_gone = c["mode"] == "in" and t >= c["t_in"]
        z = gz(x, y)
        for e, v in ((c["run"], running and not vis_gone), (c["std"], (not running) and not vis_gone)):
            if e.hide_render == v:
                e.hide_render = not v
            if v:
                e.location = (x, y, z); e.rotation_euler.z = yaw
    # north panic wave
    org = Vector((0.0, 30.0))
    for c in S.get("north", ()):
        e = c["e"]; p0 = c["p0"]
        d = (p0.to_2d() - org).length
        tw = T_IMP + d / 8.0
        if c["stream"]:
            y = p0.y + 1.0 * min(t, tw)                                     # shuffle north along the gate road
            x = p0.x
            if t > tw and d < 220:
                u = t - tw; dv = (Vector((p0.x, y)) - org); dv = (dv.normalized() + Vector((0.6, 1.0)).normalized()).normalized()
                x += dv.x * 3.6 * u; y += dv.y * 3.6 * u
            e.location = (x, y, gz(x, y) if x < 140 else p0.z)
            e.rotation_euler.z = 0.0 if t < tw else math.atan2(-(x - p0.x), max(1e-3, y - p0.y))
        elif t > tw and d < 260:                                           # quay crowd compresses toward the water
            u = min(1.0, (t - tw) / 6.0)
            cx = canal_cx(p0.y); s = 1 if p0.x > cx else -1
            e.location.x = p0.x + (-s) * 2.5 * u
    for c in S.get("columns", ()):
        y = c["y0"] + 1.5 * t; x = c["dx"] + 0.8 * math.sin(0.004 * y + c["ci"])
        c["e"].location = (x, y, gz(x, y)); c["e"].rotation_euler.z = 0.0
    if "SQ" in S:
        S["SQ"].update(t)

# ====================================================================== light: g1's seam light -> golden swing -> dusk
SEAM_LIGHT = dict(el=4.0, az=245.0, col=(1.0, 0.78, 0.58), e=4.2, amb=0.18, expo=-1.5)   # = render_g1.SEAM_LIGHT
GOLD_LIGHT = dict(el=6.0, az=200.0, col=(1.0, 0.76, 0.54), e=4.3, amb=0.19, expo=-1.45)  # sun swings west (north side lit)
DUSK_LIGHT = dict(el=3.0, az=190.0, col=(1.0, 0.62, 0.46), e=3.7, amb=0.15, expo=-1.35)  # = the g2 -> g3 seam light
SEAM_SKY = ((1.0, 0.62, 0.22, 1.0), (0.95, 0.66, 0.38, 1.0))
DUSK_SKY = ((0.93, 0.50, 0.34, 1.0), (0.62, 0.50, 0.60, 1.0))
# v5 (owner 10/27): burning Shiganshina at NIGHT - dark blue sky, a cool moon key, the fires carry the town.  = g3 t 0
# (seg_g3.G2NIGHT / its grade + haze literals: keep them in step when this changes).
NIGHT_LIGHT = dict(el=24.0, az=205.0, col=(0.50, 0.62, 1.0), e=0.30, amb=0.02, expo=-1.5)
NIGHT_SKY = ((0.035, 0.05, 0.11, 1.0), (0.010, 0.016, 0.045, 1.0))
NIGHT_HAZE = (4500.0, 0.50, (0.05, 0.06, 0.11))          # mist depth, amount, colour
# autopilot round 5: the flight north after the burning-town aerial (local 24.6 -> 32 = g3 t 0) was near black -> a brighter
# moon + exposure -0.8 by the seam (seg_g3.G2NIGHT / G2NIGHT_G match these end values)
NIGHT_LIFT = dict(NIGHT_LIGHT, e=0.50, amb=0.035, expo=-0.8)
LIFT_T = (24.6, 31.4)

def light_setup():
    w = bpy.context.scene.world
    S["ramp"] = []
    if w and w.use_nodes:
        for nd in w.node_tree.nodes:
            if nd.type == "VALTORGB":
                S["ramp"].append(nd.color_ramp.elements)
    S["WD"] = sys.modules.get("world")
    hz = bpy.data.node_groups.get("EeveeHaze")                # the haze (seg_g3.light_capture's nodes) -> night haze
    S["haze"] = None
    if hz is not None:
        hk = next((n for n in hz.nodes if n.type == "MATH" and n.operation == "MULTIPLY"), None)
        hm = next((n for n in hz.nodes if n.type == "MIX"), None)
        ms = w.mist_settings if w else None
        S["haze"] = (hk, hm, ms, hk.inputs[1].default_value if hk else None,
                     tuple(hm.inputs["B"].default_value)[:3] if hm else None, ms.depth if ms else None)

def light_spec(t):
    WD = S.get("WD")
    u = smooth(*BEATS["light_swing"], t); k = smooth(*BEATS["night"], t)
    P = WD.light_blend(SEAM_LIGHT, DUSK_LIGHT, u) if WD else dict(SEAM_LIGHT)
    if k > 0 and WD:
        P = WD.light_blend(P, NIGHT_LIGHT, k)
        kl = smooth(*LIFT_T, t)
        if kl > 0:
            P = WD.light_blend(P, NIGHT_LIFT, kl)
    return P, u, k

def light(t):
    P, u, k = light_spec(t)
    WD = S.get("WD")
    if WD and hasattr(WD, "light_rig"):
        WD.light_rig(P)
    if S.get("key"):                                     # light_rig hides every other sun: the linked key stays on
        S["key"].hide_render = False
    for el in S.get("ramp", ()):
        for i, e in enumerate(el[:2]):
            c = tuple(a + (b - a) * u for a, b in zip(SEAM_SKY[i], DUSK_SKY[i]))
            e.color = tuple(a + (b - a) * k for a, b in zip(c, NIGHT_SKY[i]))
    hz = S.get("haze")
    if hz:
        hk, hm, ms, k0, c0, d0 = hz
        if hk is not None: hk.inputs[1].default_value = k0 + (NIGHT_HAZE[1] - k0) * k
        if hm is not None: hm.inputs["B"].default_value = (*(a + (b - a) * k for a, b in zip(c0, NIGHT_HAZE[2])), 1.0)
        if ms is not None: ms.depth = d0 + (NIGHT_HAZE[0] - d0) * k
    if G1 and G1.STATE.get("sky_mat"):                  # the mackerel layer: g1's sunset colours -> dusk pinks -> night (dark)
        dk = 1.0 - 0.93 * k
        for nd in G1.STATE["sky_mat"].node_tree.nodes:
            if nd.type == "MIX" and nd.data_type == "RGBA":
                nd.inputs["A"].default_value = tuple(dk * (a + (b - a) * u) for a, b in zip((0.95, 0.55, 0.30), (0.78, 0.40, 0.38))) + (1.0,)
                nd.inputs["B"].default_value = tuple(dk * (a + (b - a) * u) for a, b in zip((1.0, 0.78, 0.52), (0.95, 0.60, 0.52))) + (1.0,)

# ====================================================================== build / update
def mats():
    m = lambda n, h, r=0.85, **kw: L.mat(n, lin(h), r, **kw)
    M = dict(
        brick=m("G2Brick", "#b4643f", 0.9, var=0.12, var_scale=0.8), cream=m("G2Cream", "#e3d5b5"), tile=m("G2Tile", "#9a5a3a"),
        timber=m("G2Timber", "#5a3f28"), dark=m("G2Dark", "#1a1410", 0.95), trim=m("G2Trim", "#4f7a55"),
        shield=m("G2Shield", "#3d4f78"), crack=m("G2Crack", "#5e5a54", 0.95), wall=m("G2Wall", "#cec3a6"), iron=m("G2Iron", "#26262a", 0.5),
        dirt=m("G2Dirt", "#9c8462", 0.95, var=0.25, var_scale=0.05), rut=m("G2Rut", "#6e5a40", 0.95), verge=m("G2Verge", "#6f8a4a", 0.95),
        dirt_n=m("G2RoadN", "#a08a66", 0.95), strip=m("G2StripWater", "#8fb4b8", 0.2), water=m("G2Water", "#5f8f84", 0.12),
        quay=m("G2Quay", "#cdbf9f", 0.9, var=0.15, var_scale=0.2), quaywall=m("G2QuayWall", "#a89a7e", 0.9), grass_bank=m("G2Bank", "#6f8a4a", 0.95),
        pylon=m("G2Pylon", "#b8ab8c"), cap=m("G2Cap", "#c0602c"), cypress=m("G2Cypress", "#24391f", 0.9),
        bronze=m("G2Bronze", "#5c5648", 0.45), wheel=m("G2Wheel", "#4a3424"), pad=m("G2Pad", "#b5aa8e"),
        chunk=m("G2ChunkStone", "#b59f78", 0.9, var=0.2, var_scale=0.5), furrow=m("G2Furrow", "#4e3c28", 0.95),
        hull=m("G2Hull", "#4a3526"), deck=m("G2Deck", "#6b5238"), cabin=m("G2Cabin", "#5c3e28"), glass=m("G2Glass", "#3e6b5a", 0.3),
        roof=m("G2FerryRoof", "#7a3a2a"), disc=m("G2Disc", "#d8cdb4"), soot=m("G2Soot", "#1c1814", 1.0),
    )
    M["lantern"] = emit_mat("G2Lantern", (1.0, 0.75, 0.35), 8.0)
    return M

def build(site):
    global L, G1, PK, SMC
    t0 = time.time()
    L = site["L"]
    G1 = sys.modules.get("g1_set")
    try:
        import people_kit as PK_
        PK = PK_
    except Exception as ex:
        print("[g2] people_kit unavailable:", ex)
    import smokecards as SMC_
    SMC = SMC_
    sc = bpy.context.scene
    if sc.render.engine.startswith("BLENDER_EEVEE"):             # g1's Eevee look (the seam must match render_g1)
        ev = sc.eevee
        for k_, v_ in (("use_raytracing", False), ("shadow_resolution_scale", 0.5), ("shadow_ray_count", 1), ("shadow_step_count", 4),
                       ("use_fast_gi", False)):
            try:
                setattr(ev, k_, v_)
            except Exception:
                pass
    coll = L.new_coll("G2")
    S["coll"] = coll; S["cards"] = []
    S["M"] = mats()
    steps = [("settle_g1", settle_g1), ("swarm", swarm_setup), ("gatehouse", lambda: build_gatehouse(coll)),
             ("ground", lambda: build_ground(coll)), ("guns", lambda: build_guns(coll)), ("fire_fx", build_fire_fx),
             ("dust", build_dust), ("smoke", build_smoke_columns), ("fires", lambda: build_fires(coll)),
             ("debris", lambda: build_debris(coll)),
             ("followers", lambda: build_followers(coll)), ("ferries", lambda: build_ferries(coll)),
             ("garrison", lambda: build_garrison(coll)), ("civilians", lambda: build_civilians(coll))]
    for name, fn in steps:
        ts = time.time()
        try:
            fn()
        except Exception:
            import traceback; traceback.print_exc()
            print(f"[g2] BUILD STEP FAILED: {name}")
        print(f"[g2] build {name} {time.time() - ts:.1f}s")
    ts = time.time()
    try:
        S["TA"] = TripoArmored(coll)
        S["TA"].arm.name = "ArmoredTitan"
    except Exception:
        import traceback; traceback.print_exc(); S["TA"] = None
    if S.get("TA"):
        try:
            lc = bpy.data.collections.new("G2ArmoredLit")           # light linking: a soft warm key on HIM only
            for m in S["TA"].meshes:
                lc.objects.link(m)
            ld = bpy.data.lights.new("G2ArmoredKey", "SUN"); ld.energy = float(os.environ.get("G2_KEY_E", "2.4"))
            ld.color = (1.0, 0.86, 0.62); ld.use_shadow = False
            lo = bpy.data.objects.new("G2ArmoredKey", ld); coll.objects.link(lo)
            el, az = math.radians(28), math.radians(222)            # from the camera side (SW), above
            lo.rotation_euler = Vector((-math.cos(el) * math.cos(az), -math.cos(el) * math.sin(az), -math.sin(el))).to_track_quat("-Z", "Y").to_euler()
            lo.light_linking.receiver_collection = lc
            S["key"] = lo
        except Exception:
            import traceback; traceback.print_exc()
    print(f"[g2] build armored {time.time() - ts:.1f}s")
    light_setup()
    print(f"[g2] build total {time.time() - t0:.1f}s")

def update(t):
    FX = S.get("fx845")
    if FX:
        FX.update(21.0 + t)                      # g1 kick at 11.0, g1 end 32.0 -> 21 s after the kick at the seam
    swarm_update(t)
    for fn in (update_gate, gun_update, armored_update, debris_update, followers_update, ferries_update, civilians_update,
               fires_update):
        try:
            fn(t)
        except Exception:
            import traceback; traceback.print_exc()
            print(f"[g2] UPDATE FAILED: {fn.__name__} t={t:.2f}")
    for cs, w in S["cards"]:
        cs.update(t, wind=w)
    if S.get("smoke"):
        S["smoke"].update(t, wind=smoke_wind(t))
    if S.get("firesmoke"):
        S["firesmoke"].update(t, wind=smoke_wind(t))

VLIMITS = dict(speed=300.0, yaw=60.0, pitch=(5.0, 50.0), lens=(24.0, 60.0), hmin=60.0, hmax=650.0)   # owner 10/27, VIDEO clock

class VPath:
    """CAM on the VIDEO clock (segtime.seg_t): what the viewer sees, for camchan.check."""
    def __init__(self, cam):
        self.cam = cam; self.t0 = 0.0; self.t1 = segtime.vdur("g2"); self.notes = list(cam.notes)
    def eval(self, tv):
        return self.cam.eval(segtime.seg_t("g2", tv))

def vcheck(ground=lambda x, y: 0.0):
    """camchan check of the camera on the video clock + framing / Armored speed numbers (video seconds)."""
    r = camchan.check(VPath(CAM), ground=ground, limits=dict(name="g2 CAM (video clock)", **VLIMITS))
    k = segtime.knots("g2")
    print(f"[g2] TMAP {k}: video {segtime.vdur('g2'):.2f} s, slope in {segtime.slope('g2', 0.0):.2f} out {segtime.slope('g2', segtime.vdur('g2')):.2f}")
    sv = segtime.slope("g2", segtime.to_video("g2", 5.0))
    print(f"[g2] Armored: y0 {arm_y(0):.1f}, run {RUN_V:.1f} m/s local = {RUN_V * sv:.0f} m/s on screen (v3 29 local = 29 on screen at 1x), "
          f"impact {T_IMP} local = {segtime.to_video('g2', T_IMP):.2f} video, slide to y {arm_y(BEATS['slide'][1]):.1f} by "
          f"{segtime.to_video('g2', BEATS['slide'][1]):.2f} video; footfalls {len(footfalls())}")
    return r

def check():
    print(f"[g2] Armored y: 0 {arm_y(0):.0f} | lock {BEATS['lock']} {arm_y(BEATS['lock']):.0f} | {T_IMP} {arm_y(T_IMP):.0f} | "
          f"slide end {BEATS['slide'][1]} {arm_y(BEATS['slide'][1]):.1f} | v(impact) {arm_v(T_IMP - 0.01):.1f} m/s; "
          f"leaf bottom @impact {leaf_bottom(T_IMP):.1f} m")
    ok = 0
    for t in np.arange(BEATS["lock"], T_IMP + 0.01, 0.25):
        c, l, ln = CAM.eval(t); a = np.array([0, arm_y(t), 9.0]) - c; d = np.array(l) - c
        ok = max(ok, math.degrees(math.acos(np.dot(a, d) / np.linalg.norm(a) / np.linalg.norm(d))))
    print(f"[g2] framing lock {BEATS['lock']}-{T_IMP} s: max {ok:.2f} deg off the Armored's chest")
    vcheck(ground=(lambda x, y: L.height(x, y)) if L is not None else (lambda x, y: 0.0))
    if bpy is not None and S.get("gate"):                   # breach see-through probe (rays south through the hole)
        update(20.0)
        saved = [(o, o.hide_viewport) for o in bpy.data.objects]
        cards = {id(o) for cs in SMC._ALL for o in cs.objects()}
        for o, _ in saved:
            o.hide_viewport = o.hide_render or id(o) in cards or o.name.startswith("G2Ferry")
        bpy.context.view_layer.update()
        dg = bpy.context.evaluated_depsgraph_get(); sc = bpy.context.scene
        for x0, z0 in ((0, 3), (0, 10), (0, 18), (0, 23), (-4, 8), (4, 8), (-6, 12), (6, 12)):
            hit, loc, nrm, idx, ob, mx = sc.ray_cast(dg, Vector((x0, 40.0, z0)), Vector((0, -1, 0)))
            print(f"[g2] breach ray x {x0:+} z {z0}: " + (f"HIT {ob.name} at y {loc.y:.1f}" if hit else "clear"))
        for o, h in saved:
            o.hide_viewport = h

if __name__ == "__main__":                 # python aot/seg_g2.py : camera + run numbers without Blender
    vcheck()

# ====================================================================== v14 PRELUDE (FEEDBACK_v13 §1)
# After Carla: the camera rises high into the sky over the inner gate: people at the gate being eaten by titans, the rest
# streaming out through the gate to the boats (swarm845 at 2.5x, no "evacuated" mask); then lightning between the houses
# on the avenue, Reiner's Armored rises out of it (swoosh) and sprints = g2's own clock from local PRE on (everything above
# is unchanged and keeps its own times: seg_g3 reads g2 at its internal t 32 = video end).
PRE = segtime.G2_PRE
DUR = segtime.DUR["g2"]
_core_update, _core_light, _core_shake = update, light, cam_shake
_CORE_CAM = CAM
def _pre_cam():
    ks = camkeys.cam("g2")
    keys = [tuple(ks["keys"][0]),                                          # g1 seam at rest (the Yeager ruin)
            (2.4, (-300.0, -520.0, 280.0), (-40.0, -60.0, 0.0), 28.0),     # up into the sky: the gate crowd, the titans
            (4.6, (-250.0, -420.0, 330.0), (0.0, 40.0, 0.0), 28.0),       # ... the people pouring out to the boats
            (PRE - 0.2, (-150.0, -560.0, 150.0), (0.0, -400.0, 12.0), 34.0),  # down between the houses: the lightning
            (PRE + 1.6, (-170.0, -420.0, 120.0), (0.0, -330.0, 10.0), 37.0)]  # he rises and sprints
    keys += [(k[0] + PRE,) + tuple(k[1:]) for k in ks["keys"][2:]]           # g2's own camera from its lock key (4.4) on
    return camchan.CamPath(keys, v_in=ks["v_in"], v_out=ks["v_out"], look_v_out=ks.get("look_v_out"))
CAM = _pre_cam()
TRACK = {k: (lambda f: (lambda t: f(t - PRE) if t >= PRE + 0.6 else None))(f) for k, f in TRACK.items()}

def cam_shake(t):
    return _core_shake(t - PRE) if t >= PRE else _core_shake(-10.0)

def light(t):
    _core_light(max(0.0, t - PRE))

def update(t):
    tc = t - PRE
    _core_update(max(0.0, tc))
    SW = S.get("SW")
    if tc < 1.0 and SW and SW.STATE:                     # the gate crowd is still there (eaten / fleeing at 2.5x)
        SW.HIDE_PEOPLE = None
        SW.update(max(0.0, SIM0 + SIM_K * 2.5 * tc))
    elif SW:
        SW.HIDE_PEOPLE = evacuated
    if tc < 0.0:
        try:
            ferries_update(tc)                           # the boats already pulling away north
        except Exception:
            pass
    TA = S.get("TA")
    if TA:                                               # hidden until the lightning, then he rises out of it (swoosh)
        hidden = tc < 0.05
        for me in TA.meshes:
            if me.hide_render != hidden:
                me.hide_render = hidden
        if 0.05 <= tc < 0.5:
            u = smooth(0.05, 0.5, tc)
            TA.arm.matrix_world = Matrix.Translation((0.0, 0.0, -18.0 * (1 - u))) @ TA.arm.matrix_world
    if -0.8 <= tc <= 1.4:                                # lightning strike between the houses where he appears
        try:
            import attack_titan as AT
            AT.shift_fx(0.0, arm_y(0.0) - 6.0, min(1.0, max(0.0, (tc + 0.8) / 2.2)), seed=52)
        except Exception:
            import traceback; traceback.print_exc()
