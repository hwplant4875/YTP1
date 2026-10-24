"""Colossal Titan from the Sketchfab CC-BY model by Sidaivan (closest match to the anime face), as a scene.py plug-in.

Enable with AOT_PLUGINS=colossal_asset (optionally with others). The model is kept locally (not in the public repo):
  E:/YTP2/3D Timelapse/assets/sketchfab/colossal_sidaivan  (override with env AOT_COLOSSAL_GLTF)
Credit in the video description: "Colossal Titan" by Sidaivan (https://sketchfab.com/Sidaivan), CC BY 4.0,
https://sketchfab.com/3d-models/e031a57fd4bf411f8e893361676b4544

845 pose: stands just outside the south outer gate, head and shoulders about 10 m above the 50 m wall, looking north into
the town, right hand gripping the wall top (IK), left arm hanging behind the wall, wrapped in steam.
"""
import bpy, glob, math, os
from mathutils import Vector
import aotlib as L

HEIGHT = float(os.environ.get("COL_H", "74"))
SRC = os.environ.get("AOT_COLOSSAL_GLTF", "E:/YTP2/3D Timelapse/assets/sketchfab/colossal_sidaivan")
BACK = float(__import__("os").environ.get("COL_BACK", "18"))                  # distance of the body axis behind (south of) the outer wall line
GX, GY = L.OUTER_GATE
FEET = Vector((GX + float(os.environ.get("COL_DX", "14")), GY - BACK, 0.0))

def _import():
    f = (glob.glob(os.path.join(SRC, "**", "*.gltf"), recursive=True) + glob.glob(os.path.join(SRC, "**", "*.glb"), recursive=True))[0]
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=f)
    new = [o for o in bpy.data.objects if o not in before]
    for o in new:
        if o.type == "MESH" and not o.data.materials:          # stray Icosphere in the source file
            bpy.data.objects.remove(o, do_unlink=True)
    new = [o for o in bpy.data.objects if o not in before]
    root = next(o for o in new if o.parent is None)
    arm = next(o for o in new if o.type == "ARMATURE")
    meshes = [o for o in new if o.type == "MESH"]
    coll = L.new_coll("ColossalTitan")
    for o in new:
        for c in list(o.users_collection):
            c.objects.unlink(o)
        coll.objects.link(o)
    for m in meshes:
        for mt in m.data.materials:
            if mt and hasattr(mt, "surface_render_method"):
                mt.surface_render_method = "DITHERED"
    return root, arm, meshes

def _bbox(meshes):
    """World bounds of the deformed (armature-evaluated) meshes; bound_box alone is wrong for this Mixamo export."""
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    pts = []
    for m in meshes:
        ev = m.evaluated_get(dg); me = ev.to_mesh()
        mw = ev.matrix_world
        pts += [mw @ v.co for i, v in enumerate(me.vertices) if i % 7 == 0]
        ev.to_mesh_clear()
    return (Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts))),
            Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts))))

def _ik(arm, bone, target_loc, pole_loc, name):
    t = bpy.data.objects.new(name, None); t.location = target_loc
    p = bpy.data.objects.new(name + "_pole", None); p.location = pole_loc
    for e in (t, p):
        arm.users_collection[0].objects.link(e)
    pb = arm.pose.bones[bone]
    c = pb.constraints.new("IK"); c.target = t; c.pole_target = p; c.chain_count = 2; c.pole_angle = math.radians(-90)
    c.use_stretch = True                       # the hand reaches the wall top while the body is still sunk (rise < 1);
    for b in (pb, pb.parent):                  # the stretched arm stays hidden behind the wall from the town side
        b.ik_stretch = float(os.environ.get("COL_IK_STRETCH", "0.12"))
    return t

# ---------------------------------------------------------------- hands on the wall top (anime S1E1)
# The wrist sits on the wall walk just inside the outer edge, the enlarged hand lies flat pointing north and the
# fingers curl down over the town-side edge, so they read from the plaza.  A hand travels up from behind the wall
# (h=0) onto its grip (h=1); the fingers close over the last quarter of the move.
FINGERS = ("Index", "Middle", "Ring", "Pinky")
CURL = (0.12, 1.25, 0.95)                                # per finger segment (rad): flat on the walk, bent over the edge
HAND_S = float(os.environ.get("COL_HAND_S", "1.9"))
GRIP_DX = float(os.environ.get("COL_GRIP_DX", "12.5"))   # hands at shoulder width either side of the head centre
GRIP_Y = float(os.environ.get("COL_GRIP_Y", "-1.0"))     # wrist offset from the wall centre line (+ = north / town side)
PALM_AXIS = os.environ.get("COL_PALM_AXIS", "TRACK_Z")   # hand-local axis pointing out of the palm
CURL_SGN = float(os.environ.get("COL_CURL_SGN", "1"))

def _bone(arm, side, part):
    pre = f"mixamorig_{'Left' if side == 'L' else 'Right'}{part}_"
    return arm.pose.bones[next(b.name for b in arm.data.bones if b.name.startswith(pre))]

def _grip_points(side):
    sg = -1 if side == "L" else 1                                  # the Colossal faces north: its left is -x
    x = FEET.x + sg * (float(os.environ.get("COL_GRIP_DX_L", "14")) if side == "L" else GRIP_DX)   # L clears the pilaster
    # anime-style outer gate (scene.gatehouse): recessed panel |x| < 10 flush with the wall top but full thickness
    # (town-side edge GY + 5.1), flat pilasters |x| 10..17 with tops at WALL_H + 3.5 (edge GY + 7.0); elsewhere the
    # plain wall walk (parapet lip WALL_H + 0.8, inner edge GY + 3.8).  Fingers curl over the town-side edge.
    dx = abs(x - GX)
    if dx < 10.0:
        top, edge = L.WALL_H, GY + 5.1
    elif dx < 17.5:
        top, edge = L.WALL_H + 3.5, GY + 7.0
    else:
        top, edge = L.WALL_H + 1.3, GY + 3.8          # palm clear above the parapet lips / rails (no clipping)
    g = Vector((x, edge - 4.8 + GRIP_Y + 1.0 + 0.9, top + 0.5))   # +0.9: shorter fingers still reach the edge
    a0 = Vector((x + sg * 3, GY - 18, L.WALL_H - 18))              # hanging behind the wall, out of sight
    c = Vector((x + sg * 1, GY - 11, L.WALL_H + 13))               # arcs up over the outer edge
    return a0, c, g

def _hand_rig(arm, side, tgt):
    """Aim the hand north along the wall walk (damped track), palm down (locked track), enlarged."""
    hb = _bone(arm, side, "Hand")
    coll = arm.users_collection[0]
    aim = bpy.data.objects.new(f"ColossalHand{side}_aim", None); aim.parent = tgt; aim.location = (0, 12, -1.2)
    down = bpy.data.objects.new(f"ColossalHand{side}_down", None); down.parent = tgt; down.location = (0, 0, -12)
    for e in (aim, down):
        coll.objects.link(e)
    c = hb.constraints.new("DAMPED_TRACK"); c.target = aim; c.track_axis = "TRACK_Y"
    c = hb.constraints.new("LOCKED_TRACK"); c.target = down; c.lock_axis = "LOCK_Y"; c.track_axis = PALM_AXIS
    hb.scale = (HAND_S,) * 3
    fingers = [[_bone(arm, side, f"Hand{f}{i}") for i in (1, 2, 3)] for f in FINGERS]
    thumb = [_bone(arm, side, f"HandThumb{i}") for i in (1, 2, 3)]
    for pb in sum(fingers, []) + thumb:
        pb.rotation_mode = "XYZ"
    # broad, muscular anime hands instead of long claws: base segments shorter (bone Y) and thicker (X/Z);
    # the outer segments inherit it
    fl, ft = float(os.environ.get("COL_FINGER_LEN", "0.7")), float(os.environ.get("COL_FINGER_THICK", "1.3"))
    for pb in [f[0] for f in fingers] + [thumb[0]]:
        pb.scale = (ft, fl, ft)
    STATE[f"hand{side}"] = dict(tgt=tgt, fingers=fingers, thumb=thumb, pts=_grip_points(side))

def _place_hand(side, h):
    d = STATE.get(f"hand{side}")
    if not d:
        return
    h = min(1.0, max(0.0, h))
    a0, c, g = d["pts"]
    d["tgt"].location = (1 - h) ** 2 * a0 + 2 * h * (1 - h) * c + h * h * g
    cu = min(1.0, max(0.0, (h - 0.72) / 0.28)); cu = cu * cu * (3 - 2 * cu)
    for segs in d["fingers"]:
        for pb, a in zip(segs, CURL):
            pb.rotation_euler = (CURL_SGN * a * (0.25 + 0.75 * cu), 0, 0)
    for pb, a in zip(d["thumb"], (0.1, 0.5, 0.5)):
        pb.rotation_euler = (CURL_SGN * a * cu, 0, 0)

STATE = {}

def leg_angles(k):
    """Right-leg kick, k -1 (wind-up) .. +1 (impact) -> (thigh, knee) degrees; thigh + = forward, knee + = flexed.
    Env (same meaning as before): COL_KICK_BACK = wind-up thigh angle behind the body, COL_KICK_HIP = thigh angle at
    impact (negative = forward; -42 puts the straight leg's ankle ~11 m up, in the 20 m gate opening, toes through the
    wall), COL_KICK_KNEE = wind-up knee flex."""
    fwd = -float(os.environ.get("COL_KICK_HIP", "-42")); back = float(os.environ.get("COL_KICK_BACK", "55"))
    knee = float(os.environ.get("COL_KICK_KNEE", "80"))
    if k < 0:                       # wind-up: thigh back, heel folds up behind
        return -back * -k, knee * -k
    if k > 0:                       # strike: thigh swings through, knee snaps straight at impact
        return -back + (fwd + back) * k, knee * (1 - k) ** 2
    return 0.0, 0.0

def set_pose(k=0.0, rise=1.0, fade=0.0, hand_l=1.0, hand_r=1.0, steam=1.0):
    """Per-frame pose (render_fast.py / render_intro.py), a pure function of its arguments: lean, right-leg kick
    (k -1 wind-up .. +1 impact), rise, fade, hands (0 = hanging behind the wall .. 1 = gripping the wall top)."""
    arm, root = STATE["arm"], STATE["root"]
    lean = float(os.environ.get("COL_LEAN", "0"))
    for bn, deg in (("mixamorig_Spine_02", lean), ("mixamorig_Spine1_03", lean), ("mixamorig_Spine2_04", lean * 0.6),
                    ("mixamorig_Neck_05", lean * 0.4), ("mixamorig_Head_06", lean * 0.8)):
        pb = arm.pose.bones[bn]; pb.rotation_mode = "XYZ"; pb.rotation_euler = (math.radians(deg), 0, 0)
    side = os.environ.get("COL_KICK_LEG", "Right")
    ul = arm.pose.bones["mixamorig_RightUpLeg_060" if side == "Right" else "mixamorig_LeftUpLeg_056"]
    ll = arm.pose.bones["mixamorig_RightLeg_061" if side == "Right" else "mixamorig_LeftLeg_057"]
    ul.rotation_mode = ll.rotation_mode = "XYZ"
    # measured on this rig: +x on the thigh swings it FORWARD and +x on the shin hyper-extends the knee, so the old
    # mapping (+back) produced a knee-up hop in front and a backward "kick"
    thigh, knee = leg_angles(k)
    ul.rotation_euler = (math.radians(thigh), 0, 0); ll.rotation_euler = (math.radians(-knee), 0, 0)
    arm.pose.bones["mixamorig_Spine_02"].rotation_euler.x += math.radians(-8 * max(0.0, -k) + 6 * max(0.0, k))
    arm.pose.bones["mixamorig_Head_06"].scale = (float(os.environ.get("COL_HEAD", "1.8")),) * 3
    _place_hand("L", hand_l); _place_hand("R", hand_r)
    root.location = STATE["base"].copy()
    drop = (1 - rise) * float(os.environ.get("COL_RISE_DROP", "14"))
    root.location.z -= drop + fade * 30
    # steam follows the rise (not the fade-sink) and rolls outward, low and wide, as the body fades
    # steam (0..1) builds the cloud up gradually after the arrival
    g = min(1.0, max(0.0, steam))
    if "cards" in STATE:
        _set_card_steam(g, fade, drop)
    for ob, loc0, sc0 in STATE.get("wisps", ()):
        c = STATE["wisp_c"]
        sp = (0.55 + 0.45 * g) * (1 + 0.9 * fade)
        ob.hide_render = g < 0.02
        k = (0.15 + 0.85 * g)
        ob.location = (c.x + (loc0.x - c.x) * sp, c.y + (loc0.y - c.y) * sp, loc0.z - drop + 4 * fade - 3 * (1 - g))
        ob.scale = (sc0.x * k * (1 + 0.8 * fade), sc0.y * k * (1 + 0.8 * fade), sc0.z * k * (1 + 0.35 * fade))

def build(M, year, ctx):
    # shown when COL_SHOW=1, or by default for AOT_EVENT=colossal|kick (standalone use)
    show = os.environ.get("COL_SHOW")
    if (show == "0") or (show is None and os.environ.get("AOT_EVENT", "colossal") not in ("colossal", "kick")):
        return
    root, arm, meshes = _import()
    from mathutils import Matrix
    root.matrix_world = Matrix.Rotation(math.pi, 4, "Z") @ root.matrix_world     # model faces -Y; turn to face north (+Y)
    mn, mx = _bbox(meshes)
    s = HEIGHT / (mx.z - mn.z)
    root.scale = tuple(v * s for v in root.scale)
    mn, mx = _bbox(meshes)
    print("[colossal_asset] height after scale", round(mx.z - mn.z, 1))
    c = (mn + mx) / 2
    root.location += Vector((FEET.x - c.x, FEET.y - c.y, L.height(FEET.x, FEET.y) - 1.5 - mn.z))
    bpy.context.view_layer.update()
    mn, mx = _bbox(meshes)
    print("[colossal_asset] placed bbox", tuple(round(v, 1) for v in mn), tuple(round(v, 1) for v in mx))
    # both hands grip the wall top either side of the head (anime S1E1); see _grip_points / _hand_rig
    STATE.update(root=root, arm=arm, base=root.location.copy(), meshes=meshes)
    for side, bone in (("L", "mixamorig_LeftForeArm_010"), ("R", "mixamorig_RightForeArm_034")):
        sg = -1 if side == "L" else 1
        t = _ik(arm, bone, _grip_points(side)[2], (FEET.x + sg * 40, GY - 40, 20), f"ColossalHand{side}")
        _hand_rig(arm, side, t)
    set_pose(float(os.environ.get("COL_KICK", "0")), float(os.environ.get("COL_RISE", "1")), float(os.environ.get("COL_FADE", "0")))
    bpy.context.view_layer.update()
    hb = arm.pose.bones["mixamorig_Head_06"]
    print("[colossal_asset] head world", tuple(round(v, 1) for v in (arm.matrix_world @ hb.head)), "scale", tuple(hb.scale))
    # steam: thin wisps creeping off the shoulders, head and arms + a low ground mist (not a cloud box)
    if os.environ.get("COL_STEAM", "cards") == "cards":      # soft camera-facing smoke cards (Eevee + Cycles)
        card_steam(arm, float(os.environ.get("COL_FADE", "0")))
    elif os.environ.get("COL_STEAM") == "wisps":
        fade = float(os.environ.get("COL_FADE", "0"))
        wisps(arm, fade)
    elif os.environ.get("COL_STEAM") == "box":
        try:
            import titans
            titans.steam("ColossalSteam", (FEET.x, GY - BACK + 4, 46), (70, 40, 34), density=float(os.environ.get("STEAM", "0.35")))
        except Exception as ex:
            print("[colossal_asset] steam failed:", ex)

def _wisp_mat(name, density):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; N = nt.nodes; Lk = nt.links
    N.remove(N["Principled BSDF"])
    tc = N.new("ShaderNodeTexCoord")
    # stretch the noise upward so it reads as rising strands
    st = N.new("ShaderNodeMapping"); st.inputs["Scale"].default_value = (1.0, 1.0, 1.8)   # flattened billows, not strands
    Lk.new(tc.outputs["Object"], st.inputs["Vector"])
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 2.6; nz.inputs["Detail"].default_value = 10
    nz.inputs["Roughness"].default_value = 0.7; nz.inputs["Distortion"].default_value = 1.5
    Lk.new(st.outputs["Vector"], nz.inputs["Vector"])
    cr = N.new("ShaderNodeValToRGB"); e = cr.color_ramp.elements
    e[0].position, e[0].color = 0.52, (0, 0, 0, 1); e[1].position, e[1].color = 0.75, (1, 1, 1, 1)
    Lk.new(nz.outputs["Fac"], cr.inputs["Fac"])
    # fade to nothing toward the shape's edge (generated coords 0..1 -> distance from centre)
    gc = N.new("ShaderNodeVectorMath"); gc.operation = "SUBTRACT"; gc.inputs[1].default_value = (0.5, 0.5, 0.5)
    Lk.new(tc.outputs["Generated"], gc.inputs[0])
    ln = N.new("ShaderNodeVectorMath"); ln.operation = "LENGTH"; Lk.new(gc.outputs[0], ln.inputs[0])
    fo = N.new("ShaderNodeMapRange"); fo.inputs["From Min"].default_value = 0.15; fo.inputs["From Max"].default_value = 0.5
    fo.inputs["To Min"].default_value = 1.0; fo.inputs["To Max"].default_value = 0.0
    Lk.new(ln.outputs["Value"], fo.inputs["Value"])
    mul = N.new("ShaderNodeMath"); mul.operation = "MULTIPLY"
    Lk.new(cr.outputs["Color"], mul.inputs[0]); Lk.new(fo.outputs["Result"], mul.inputs[1])
    mul2 = N.new("ShaderNodeMath"); mul2.operation = "MULTIPLY"; mul2.inputs[1].default_value = density
    Lk.new(mul.outputs[0], mul2.inputs[0])
    pv = N.new("ShaderNodeVolumePrincipled"); pv.inputs["Color"].default_value = (0.95, 0.93, 0.9, 1)
    pv.inputs["Anisotropy"].default_value = 0.4
    Lk.new(mul2.outputs[0], pv.inputs["Density"])
    Lk.new(pv.outputs[0], N["Material Output"].inputs["Volume"])
    return m

def wisps(arm, fade=0.0):
    """Rising steam strands from body points (bone heads) and a thin ground mist; denser and taller when fading."""
    import random
    rnd = random.Random(5)
    coll = arm.users_collection[0]
    dens = float(os.environ.get("COL_WISP_DENS", "0.35")) * (1 + 2.5 * fade)
    mat = _wisp_mat("ColossalWisp", dens)
    pts = []
    for bn in ("mixamorig_LeftShoulder_08", "mixamorig_RightShoulder_032",           # not the head: keep the face clear
               "mixamorig_LeftArm_09", "mixamorig_RightArm_033", "mixamorig_LeftForeArm_010", "mixamorig_RightForeArm_034",
               "mixamorig_Spine2_04", "mixamorig_Spine1_03"):
        pb = arm.pose.bones.get(bn)
        if pb:
            pts.append(arm.matrix_world @ pb.head)
    # low, wide rolling steam: flattened puffs hugging the shoulders/head plus a ring spreading out at shoulder height
    # (the old tall stretched strands read as a water fountain); set_pose spreads and grows them with the fade
    cen = sum(pts, Vector()) / max(1, len(pts))
    specs = []
    for p in pts:
        for j in range(2):
            specs.append(((p.x + rnd.uniform(-5, 5), p.y + rnd.uniform(-9, -2), p.z + rnd.uniform(-3, 2)),   # behind the body
                          (rnd.uniform(6, 10), rnd.uniform(6, 10), rnd.uniform(3.5, 5.5))))
    for k in range(10):
        a = k / 10 * math.tau + rnd.uniform(-0.2, 0.2); r = rnd.uniform(13, 20)
        specs.append(((cen.x + math.cos(a) * r, cen.y + math.sin(a) * r * 0.8 - 4, cen.z - rnd.uniform(4, 10)),
                      (rnd.uniform(10, 15), rnd.uniform(9, 13), rnd.uniform(4, 6.5))))
    STATE["wisps"] = []; STATE["wisp_c"] = cen.copy()
    for i, (loc, scl) in enumerate(specs):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, radius=1, location=loc)
        o = bpy.context.active_object; o.name = f"ColossalWisp{i}"
        o.scale = scl
        o.data.materials.append(mat)
        for c in list(o.users_collection):
            c.objects.unlink(o)
        coll.objects.link(o)
        STATE["wisps"].append((o, Vector(loc), Vector(scl)))
    # thin creeping mist at the feet / along the wall foot
    bpy.ops.mesh.primitive_cube_add(size=1, location=(FEET.x, FEET.y + 8, 6))
    g = bpy.context.active_object; g.name = "ColossalMist"; g.scale = (120, 60, 12)
    g.data.materials.append(_wisp_mat("ColossalMist", dens * 0.5))
    for c in list(g.users_collection):
        c.objects.unlink(g)
    coll.objects.link(g)

CAMS = {
    # from the rooftops inside the town looking south: the iconic S1E1 view (thumbnail)
    "colossal_town": ((3, GY + 125, 19), (12, GY - 16, 68), 24),     # on the main avenue, above the street
    "colossal_face": ((10, GY + 95, 66), (0, GY - 14, 60), 45),
    "colossal_wide": ((260, GY + 420, 70), (0, GY - 20, 45), 30),
}


# ---------------------------------------------------------------- COL_STEAM=cards (default): soft smoke cards
def card_steam(arm, fade=0.0):
    """Same layout as wisps() (behind the shoulders/arms + a low ring + ground mist), drawn as many soft
    camera-facing steam cards; set_pose() spreads / grows / sinks them exactly like the wisps."""
    import random
    import numpy as np
    import smokecards as SC
    rnd = random.Random(5)
    pts = []
    for bn in ("mixamorig_LeftShoulder_08", "mixamorig_RightShoulder_032", "mixamorig_LeftArm_09", "mixamorig_RightArm_033",
               "mixamorig_LeftForeArm_010", "mixamorig_RightForeArm_034", "mixamorig_Spine2_04", "mixamorig_Spine1_03"):
        pb = arm.pose.bones.get(bn)
        if pb:
            pts.append(arm.matrix_world @ pb.head)
    cen = sum(pts, Vector()) / max(1, len(pts))
    blobs = []
    for p in pts:
        for j in range(2):
            blobs.append(((p.x + rnd.uniform(-5, 5), p.y + rnd.uniform(-9, -2), p.z + rnd.uniform(-3, 2)), rnd.uniform(6, 10), 0.75))
    for k in range(10):
        a = k / 10 * math.tau + rnd.uniform(-0.2, 0.2); r = rnd.uniform(13, 20)
        blobs.append(((cen.x + math.cos(a) * r, cen.y + math.sin(a) * r * 0.8 - 4, cen.z - rnd.uniform(4, 10)), rnd.uniform(10, 15), 0.6))
    for p in pts[:4]:                                         # steam rising off the shoulders / upper arms, above the wall top
        for j in range(3):
            blobs.append(((p.x + rnd.uniform(-6, 6), p.y + rnd.uniform(-6, 2), p.z + 4 + j * 5 + rnd.uniform(0, 3)), rnd.uniform(5, 8), 0.5 - 0.1 * j))
    for k in range(14):                                       # ground mist along the wall foot
        blobs.append(((FEET.x + rnd.uniform(-60, 60), FEET.y + 8 + rnd.uniform(-25, 25), rnd.uniform(3, 8)), rnd.uniform(10, 16), 0.35))
    P, R, A = [], [], []
    for (c, rr, al) in blobs:
        for q in range(5):                                    # several cards per blob: soft, layered billows
            P.append((c[0] + rnd.gauss(0, rr * 0.45), c[1] + rnd.gauss(0, rr * 0.45), c[2] + rnd.gauss(0, rr * 0.25)))
            R.append(rr * rnd.uniform(0.55, 0.9)); A.append(al * rnd.uniform(0.6, 1.0))
    P, R, A = np.array(P), np.array(R), np.array(A)
    cs = SC.SmokeCards("ColossalWispCards")      # name starts with ColossalWisp: render_fast hides it before 8.2 s like the wisps
    n = len(P)
    cs.add_many(np.full(n, -1e6), P, None, r0=R, r1=R, life=2e6, rise=0.0, kind="steam", alpha=A * 2.3, fade_in=0.001)
    cs.build(arm.users_collection[0])
    STATE["cards"] = (cs, P.copy(), R.copy(), A.copy(), cen.copy())
    # card heights are relative to the body: remember the root height of the build-time pose (minus its fade sink)
    STATE["cards_zb"] = STATE["root"].location.z            # the points were measured in this (possibly sunk) pose
    _set_card_steam(1.0, fade, 0.0)

def _set_card_steam(g, fade, drop):
    import numpy as np
    cs, P0, R0, A0, c = STATE["cards"]
    pool = cs.pools["steam"]
    sp = (0.55 + 0.45 * g) * (1 + 0.9 * fade)
    k = (0.15 + 0.85 * g)
    fr = bpy.context.scene.frame_current / 30.0
    A = pool.A
    A[:, 1] = c.x + (P0[:, 0] - c.x) * sp
    A[:, 2] = c.y + (P0[:, 1] - c.y) * sp
    zoff = STATE["root"].location.z + 30.0 * fade - STATE.get("cards_zb", STATE["root"].location.z)   # follows the rise, not the fade-sink
    A[:, 3] = P0[:, 2] + zoff + 4 * fade - 3 * (1 - g) + 0.6 * np.sin(fr * 0.7 + np.arange(len(P0)))
    A[:, 7] = A[:, 8] = R0 * k * (1 + 0.8 * fade)
    A[:, 12] = A0 * 2.3 * (0.0 if g < 0.02 else 1.0)
    A[:, 16] = np.arange(len(P0)) * 1.7 + 0.05 * fr
    cs.update(0.0)
