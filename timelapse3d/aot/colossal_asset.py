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

def build(M, year, ctx):
    if os.environ.get("AOT_EVENT", "colossal") not in ("colossal", "kick"):
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
    _ik(arm, "mixamorig_RightForeArm_034", (GX + 17, wall_y - 3.5, L.WALL_H + 1.2), (GX + 40, wall_y - 40, 20), "ColossalHandR")
    _ik(arm, "mixamorig_LeftForeArm_010", (GX - 19, wall_y - 7.0, L.WALL_H - 9), (GX - 40, wall_y - 40, 20), "ColossalHandL")
    # lean over the wall top so the chin sits about at the parapet, glaring down into the town (S1E1)
    lean = float(os.environ.get("COL_LEAN", "0"))
    for bn, deg in (("mixamorig_Spine_02", lean), ("mixamorig_Spine1_03", lean), ("mixamorig_Spine2_04", lean * 0.6),
                    ("mixamorig_Neck_05", lean * 0.4), ("mixamorig_Head_06", lean * 0.8)):
        pb = arm.pose.bones[bn]; pb.rotation_mode = "XYZ"; pb.rotation_euler = (math.radians(deg), 0, 0)
    # the model's head is ~1/11 of its height; the anime Colossal's is ~1/7.5
    arm.pose.bones["mixamorig_Head_06"].scale = (float(os.environ.get("COL_HEAD", "1.8")),) * 3
    bpy.context.view_layer.update()
    hb = arm.pose.bones["mixamorig_Head_06"]
    print("[colossal_asset] head world", tuple(round(v, 1) for v in (arm.matrix_world @ hb.head)), "scale", tuple(hb.scale))
    # steam around the body
    try:
        import titans
        titans.steam("ColossalSteam", (GX, GY - BACK + 4, 46), (70, 40, 34), density=float(os.environ.get("STEAM", "0.35")))
    except Exception as ex:
        print("[colossal_asset] steam failed:", ex)

CAMS = {
    # from the rooftops inside the town looking south: the iconic S1E1 view (thumbnail)
    "colossal_town": ((-30, GY + 115, 14), (10, GY - 16, 70), 24),
    "colossal_face": ((10, GY + 95, 66), (0, GY - 14, 60), 45),
    "colossal_wide": ((260, GY + 420, 70), (0, GY - 20, 45), 30),
}
