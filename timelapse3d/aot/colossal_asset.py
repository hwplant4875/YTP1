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
    return t

STATE = {}

def set_pose(k=0.0, rise=1.0, fade=0.0):
    """Per-frame pose (also used by render_intro.py): lean, right-leg kick (k -1 wind-up .. +1 impact), rise, fade."""
    arm, root = STATE["arm"], STATE["root"]
    lean = float(os.environ.get("COL_LEAN", "0"))
    for bn, deg in (("mixamorig_Spine_02", lean), ("mixamorig_Spine1_03", lean), ("mixamorig_Spine2_04", lean * 0.6),
                    ("mixamorig_Neck_05", lean * 0.4), ("mixamorig_Head_06", lean * 0.8)):
        pb = arm.pose.bones[bn]; pb.rotation_mode = "XYZ"; pb.rotation_euler = (math.radians(deg), 0, 0)
    side = os.environ.get("COL_KICK_LEG", "Right")
    ul = arm.pose.bones["mixamorig_RightUpLeg_060" if side == "Right" else "mixamorig_LeftUpLeg_056"]
    ll = arm.pose.bones["mixamorig_RightLeg_061" if side == "Right" else "mixamorig_LeftLeg_057"]
    ul.rotation_mode = ll.rotation_mode = "XYZ"
    fwd = float(os.environ.get("COL_KICK_HIP", "-75")); back = float(os.environ.get("COL_KICK_BACK", "55"))   # +x = thigh back (heel up behind), -x = forward
    knee = float(os.environ.get("COL_KICK_KNEE", "80"))
    if k < 0:          # wind-up: thigh back, knee folded
        ul.rotation_euler = (math.radians(back * -k), 0, 0); ll.rotation_euler = (math.radians(knee * -k), 0, 0)
    elif k > 0:        # strike: thigh swings through, knee snaps straight at impact
        ul.rotation_euler = (math.radians(back + (fwd - back) * k), 0, 0); ll.rotation_euler = (math.radians(knee * (1 - k) ** 2), 0, 0)
    else:
        ul.rotation_euler = (0, 0, 0); ll.rotation_euler = (0, 0, 0)
    arm.pose.bones["mixamorig_Spine_02"].rotation_euler.x += math.radians(-8 * max(0.0, -k) + 6 * max(0.0, k))
    arm.pose.bones["mixamorig_Head_06"].scale = (float(os.environ.get("COL_HEAD", "1.8")),) * 3
    root.location = STATE["base"].copy()
    root.location.z -= (1 - rise) * float(os.environ.get("COL_RISE_DROP", "22")) + fade * 30

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
    # hands: right hand grips the wall top just east of the gate, left one rests lower on the outer face
    wall_y = GY                       # outer wall line at the gate (the wall runs east-west here)
    # both hands grip the wall top either side of the head (anime S1E1)
    _ik(arm, "mixamorig_RightForeArm_034", (FEET.x + 17, wall_y - 3.5, L.WALL_H + 1.2), (FEET.x + 40, wall_y - 40, 20), "ColossalHandR")
    _ik(arm, "mixamorig_LeftForeArm_010", (FEET.x - 17, wall_y - 3.5, L.WALL_H + 1.2), (FEET.x - 40, wall_y - 40, 20), "ColossalHandL")
    STATE.update(root=root, arm=arm, base=root.location.copy())
    set_pose(float(os.environ.get("COL_KICK", "0")), float(os.environ.get("COL_RISE", "1")), float(os.environ.get("COL_FADE", "0")))
    bpy.context.view_layer.update()
    hb = arm.pose.bones["mixamorig_Head_06"]
    print("[colossal_asset] head world", tuple(round(v, 1) for v in (arm.matrix_world @ hb.head)), "scale", tuple(hb.scale))
    # steam: thin wisps creeping off the shoulders, head and arms + a low ground mist (not a cloud box)
    if os.environ.get("COL_STEAM", "wisps") == "wisps":
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
    st = N.new("ShaderNodeMapping"); st.inputs["Scale"].default_value = (1.0, 1.0, 0.35)
    Lk.new(tc.outputs["Object"], st.inputs["Vector"])
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 4.0; nz.inputs["Detail"].default_value = 10
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
    for bn in ("mixamorig_Head_06", "mixamorig_Neck_05", "mixamorig_LeftShoulder_08", "mixamorig_RightShoulder_032",
               "mixamorig_LeftArm_09", "mixamorig_RightArm_033", "mixamorig_LeftForeArm_010", "mixamorig_RightForeArm_034",
               "mixamorig_Spine2_04", "mixamorig_Spine1_03"):
        pb = arm.pose.bones.get(bn)
        if pb:
            pts.append(arm.matrix_world @ pb.head)
    for i, p in enumerate(pts):
        for j in range(2):
            h = rnd.uniform(14, 26) * (1 + fade)
            bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, radius=1,
                                                 location=(p.x + rnd.uniform(-3, 3), p.y + rnd.uniform(-3, 3), p.z + h * 0.45))
            o = bpy.context.active_object; o.name = f"ColossalWisp{i}_{j}"
            o.scale = (rnd.uniform(4, 7) * (1 + fade), rnd.uniform(4, 7) * (1 + fade), h)
            o.data.materials.append(mat)
            for c in list(o.users_collection):
                c.objects.unlink(o)
            coll.objects.link(o)
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
