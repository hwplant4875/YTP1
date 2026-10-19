import bpy, math, os
A = '/tmp/claude-0/vz/assets'

def reset(w=1920, h=1080, samples=96):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    s = bpy.context.scene
    s.render.engine = 'CYCLES'
    s.cycles.device = 'CPU'
    s.cycles.samples = samples
    s.cycles.use_denoising = True
    s.cycles.denoiser = 'OPENIMAGEDENOISE'
    s.cycles.max_bounces = 6
    s.render.resolution_x, s.render.resolution_y = w, h
    s.render.resolution_percentage = 100
    s.view_settings.view_transform = 'AgX'
    s.view_settings.look = 'AgX - Medium High Contrast'
    s.render.image_settings.file_format = 'PNG'
    return s

def world_hdri(name, strength=1.0, rot=0.0, bg_strength=None):
    s = bpy.context.scene
    w = bpy.data.worlds.new('W'); s.world = w; w.use_nodes = True
    nt = w.node_tree; n = nt.nodes; n.clear()
    tc = n.new('ShaderNodeTexCoord'); mp = n.new('ShaderNodeMapping')
    mp.inputs['Rotation'].default_value[2] = rot
    env = n.new('ShaderNodeTexEnvironment')
    env.image = bpy.data.images.load(f'{A}/{name}.hdr')
    bg = n.new('ShaderNodeBackground'); bg.inputs['Strength'].default_value = strength
    out = n.new('ShaderNodeOutputWorld')
    nt.links.new(tc.outputs['Generated'], mp.inputs['Vector'])
    nt.links.new(mp.outputs['Vector'], env.inputs['Vector'])
    nt.links.new(env.outputs['Color'], bg.inputs['Color'])
    if bg_strength is None:
        nt.links.new(bg.outputs[0], out.inputs[0])
    else:
        # different strength for camera rays vs lighting
        bg2 = n.new('ShaderNodeBackground'); bg2.inputs['Strength'].default_value = bg_strength
        nt.links.new(env.outputs['Color'], bg2.inputs['Color'])
        lp = n.new('ShaderNodeLightPath'); mx = n.new('ShaderNodeMixShader')
        nt.links.new(lp.outputs['Is Camera Ray'], mx.inputs[0])
        nt.links.new(bg.outputs[0], mx.inputs[1]); nt.links.new(bg2.outputs[0], mx.inputs[2])
        nt.links.new(mx.outputs[0], out.inputs[0])
    return w

def world_color(rgb, strength=1.0):
    s = bpy.context.scene
    w = bpy.data.worlds.new('W'); s.world = w; w.use_nodes = True
    bg = w.node_tree.nodes['Background']
    bg.inputs['Color'].default_value = (*rgb, 1); bg.inputs['Strength'].default_value = strength

def pbr(name, folder, scale=1.0, tint=None, rough_mul=1.0, coord='UV'):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; n = nt.nodes; L = nt.links.new
    b = n['Principled BSDF']
    tc = n.new('ShaderNodeTexCoord'); mp = n.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (scale, scale, scale)
    L(tc.outputs[coord], mp.inputs['Vector'])
    def tex(f, non_color=False):
        t = n.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(f'{A}/{folder}/{f}')
        if coord != 'UV': t.projection = 'BOX'; t.projection_blend = 0.3
        if non_color: t.image.colorspace_settings.name = 'Non-Color'
        L(mp.outputs['Vector'], t.inputs['Vector']); return t
    d = tex('Diffuse.jpg')
    if tint:
        mx = n.new('ShaderNodeMix'); mx.data_type = 'RGBA'; mx.blend_type = 'MULTIPLY'
        mx.inputs['Factor'].default_value = 1.0
        L(d.outputs['Color'], mx.inputs['A']); mx.inputs['B'].default_value = (*tint, 1)
        L(mx.outputs['Result'], b.inputs['Base Color'])
    else:
        L(d.outputs['Color'], b.inputs['Base Color'])
    if os.path.exists(f'{A}/{folder}/Rough.jpg'):
        r = tex('Rough.jpg', True)
        mth = n.new('ShaderNodeMath'); mth.operation = 'MULTIPLY'; mth.inputs[1].default_value = rough_mul
        L(r.outputs['Color'], mth.inputs[0]); L(mth.outputs[0], b.inputs['Roughness'])
    if os.path.exists(f'{A}/{folder}/nor_gl.jpg'):
        nm = tex('nor_gl.jpg', True); nn = n.new('ShaderNodeNormalMap')
        L(nm.outputs['Color'], nn.inputs['Color']); L(nn.outputs['Normal'], b.inputs['Normal'])
    return m

def mat(name, rgb, rough=0.5, metal=0.0, emit=None, emit_s=0.0, trans=0.0, ior=1.45, coat=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*rgb, 1)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    b.inputs['Transmission Weight'].default_value = trans
    b.inputs['IOR'].default_value = ior
    b.inputs['Coat Weight'].default_value = coat
    if emit:
        b.inputs['Emission Color'].default_value = (*emit, 1)
        b.inputs['Emission Strength'].default_value = emit_s
    return m

def plane(name, size, loc=(0, 0, 0), m=None, uv_scale=None):
    bpy.ops.mesh.primitive_plane_add(size=1, location=loc)
    o = bpy.context.object; o.name = name; o.scale = (size[0], size[1], 1)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if uv_scale:
        for lp in o.data.uv_layers.active.data:
            lp.uv = (lp.uv[0] * uv_scale[0], lp.uv[1] * uv_scale[1])
    if m: o.data.materials.append(m)
    return o

def box(name, dims, loc, m=None, bevel=0.0, segs=4):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object; o.name = name; o.scale = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        bv = o.modifiers.new('bv', 'BEVEL'); bv.width = bevel; bv.segments = segs
        bpy.ops.object.shade_smooth()
    if m: o.data.materials.append(m)
    return o

def gltf(name, loc=(0, 0, 0), rot=(0, 0, 0), scale=1.0):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=f'{A}/{name}/{name}.gltf')
    new = [o for o in bpy.data.objects if o not in before]
    roots = [o for o in new if o.parent is None]
    for r in roots:
        r.location = loc; r.rotation_euler = rot; r.scale = (scale,) * 3
    return roots

def camera(loc, look_at, lens=24, dof=None, fstop=2.8):
    import mathutils
    cd = bpy.data.cameras.new('C'); cd.lens = lens
    c = bpy.data.objects.new('C', cd); bpy.context.collection.objects.link(c)
    c.location = loc
    d = mathutils.Vector(look_at) - mathutils.Vector(loc)
    c.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    if dof:
        cd.dof.use_dof = True; cd.dof.focus_distance = dof; cd.dof.aperture_fstop = fstop
    bpy.context.scene.camera = c
    return c

def text(body, font, size, loc, rot, m, extrude=0.0, align='CENTER'):
    cu = bpy.data.curves.new('T', 'FONT'); cu.body = body
    cu.font = bpy.data.fonts.load(font); cu.size = size; cu.extrude = extrude
    cu.align_x = align; cu.align_y = 'CENTER'
    o = bpy.data.objects.new('T', cu); bpy.context.collection.objects.link(o)
    o.location = loc; o.rotation_euler = rot; o.data.materials.append(m)
    return o

def render(path):
    bpy.context.scene.render.filepath = path
    bpy.ops.render.render(write_still=True)

def metaball(name, elems, m=None, res=0.01):
    mb = bpy.data.metaballs.new(name); mb.resolution = res; mb.render_resolution = res
    for (co, r, sc, rot) in elems:
        e = mb.elements.new(type='ELLIPSOID'); e.co = co; e.radius = r
        e.size_x, e.size_y, e.size_z = sc
        if rot is not None:
            import mathutils; e.rotation = mathutils.Euler(rot).to_quaternion()
    o = bpy.data.objects.new(name, mb); bpy.context.collection.objects.link(o)
    bpy.context.view_layer.objects.active = o; o.select_set(True)
    bpy.ops.object.convert(target='MESH'); o = bpy.context.object
    bpy.ops.object.shade_smooth()
    if m: o.data.materials.clear(); o.data.materials.append(m)
    return o

def foot(x, y, z, m, mirror=1, scale=1.0, yaw=0.0):
    # sock foot, toes toward +y. size ~ 26 cm
    k = scale
    E = [((0, -0.10*k, 0.04*k), 0.05*k, (0.9, 1.0, 1.0), None),          # heel
         ((0.004*mirror, -0.02*k, 0.035*k), 0.05*k, (1.0, 1.3, 0.75), None),   # arch
         ((0.012*mirror, 0.06*k, 0.025*k), 0.048*k, (1.1, 1.0, 0.55), None),  # ball
         ((0.010*mirror, 0.105*k, 0.018*k), 0.035*k, (1.25, 0.9, 0.55), None), # toes
         ((0, -0.085*k, 0.13*k), 0.045*k, (0.9, 0.9, 1.6), None)]          # ankle
    o = metaball('foot', E, m)
    o.location = (x, y, z); o.rotation_euler = (0, 0, yaw)
    return o

def tube(name, pts, m=None, res=24):
    """pts: list of (x,y,z,r). smooth tapered tube via bezier curve bevel"""
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'
    cu.bevel_depth = 1.0; cu.bevel_resolution = res // 2; cu.use_fill_caps = True; cu.resolution_u = 16
    sp = cu.splines.new('BEZIER'); sp.bezier_points.add(len(pts) - 1)
    for bp, (x, y, z, r) in zip(sp.bezier_points, pts):
        bp.co = (x, y, z); bp.radius = r
        bp.handle_left_type = bp.handle_right_type = 'AUTO'
    o = bpy.data.objects.new(name, cu); bpy.context.collection.objects.link(o)
    if m: o.data.materials.append(m)
    bpy.context.view_layer.objects.active = o
    for ob in bpy.context.selected_objects: ob.select_set(False)
    o.select_set(True); bpy.ops.object.convert(target='MESH'); o = bpy.context.object
    bpy.ops.object.shade_smooth()
    return o

def foot(x, y, z, m, mirror=1, scale=1.0, yaw=0.0, pitch=0.0):
    k = scale
    P = [(0, -0.115*k, 0.045*k, 0.042*k), (0.004*mirror, -0.06*k, 0.045*k, 0.047*k), (0.008*mirror, 0.01*k, 0.04*k, 0.046*k),
         (0.012*mirror, 0.07*k, 0.03*k, 0.044*k), (0.012*mirror, 0.11*k, 0.024*k, 0.032*k), (0.01*mirror, 0.125*k, 0.022*k, 0.012*k)]
    o = tube('foot', P, m)
    o.scale = (1.25, 1.0, 0.72)
    ank = tube('ankle', [(0, -0.09*k, 0.05*k, 0.05*k), (0, -0.085*k, 0.16*k, 0.045*k)], m)
    ank.parent = o
    o.location = (x, y, z); o.rotation_euler = (pitch, 0, yaw)
    return o
