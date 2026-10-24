import bpy, sys, math
sys.path.insert(0, "/home/user/YTP1/timelapse3d/aot")
import characters as C
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
e = C.make_eren(); m = C.make_mikasa()
C.pose_standing(e, 0.1); C.pose_standing(m, 0.1)
e.location = (-0.45, 0, 0); m.location = (0.45, 0, 0)
for ob in list(bpy.data.objects):
    if ob.type == 'MESH':
        d = ob.modifiers.new("lp", 'DECIMATE'); d.ratio = 0.06
        for p in ob.data.polygons: p.use_smooth = False
        for mat in ob.data.materials:
            if mat and mat.use_nodes:
                for n in mat.node_tree.nodes:
                    if n.type == 'BSDF_PRINCIPLED':
                        n.inputs['Roughness'].default_value = 0.9
                        if 'Subsurface Weight' in n.inputs: n.inputs['Subsurface Weight'].default_value = 0
bpy.ops.mesh.primitive_plane_add(size=30); g = bpy.context.object
gm = bpy.data.materials.new("g"); gm.use_nodes = True
gm.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.32, 0.45, 0.2, 1); g.data.materials.append(gm)
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.75, 0.85, 1.0, 1)
bpy.ops.object.light_add(type='SUN', rotation=(math.radians(40), 0, math.radians(-150))); bpy.context.object.data.energy = 4
sc.render.engine = 'CYCLES'; sc.cycles.samples = 32; sc.render.resolution_x = 960; sc.render.resolution_y = 540
cams = {"back_high": ((-2.5, 4.5, 4.0), (55, 0, 208)), "side": ((-4.6, 0.6, 1.4), (82, 0, 262))}
for k, (loc, rot) in cams.items():
    bpy.ops.object.camera_add(location=loc, rotation=tuple(math.radians(a) for a in rot))
    sc.camera = bpy.context.object; bpy.context.object.data.lens = 50
    sc.render.filepath = f"/tmp/claude-0/aot/kids/lp_{k}.png"
    bpy.ops.render.render(write_still=True)
