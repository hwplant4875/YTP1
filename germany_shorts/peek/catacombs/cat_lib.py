# PEEK. Paris Catacombs: shared Blender helpers (Blender 5.2, EEVEE).
import bpy, math, random, os
from mathutils import Vector

FPS = 24


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    s = bpy.context.scene
    s.render.engine = 'BLENDER_EEVEE'
    s.render.fps = FPS
    s.render.resolution_x, s.render.resolution_y = 1920, 1080
    s.render.image_settings.file_format = 'PNG'
    s.render.image_settings.color_mode = 'RGB'
    try:
        s.eevee.taa_render_samples = 24
        s.eevee.use_shadows = True
        s.eevee.volumetric_tile_size = '8'
    except Exception:
        pass
    try:
        s.view_settings.view_transform = 'AgX'
        s.view_settings.look = 'AgX - Medium High Contrast'
    except Exception:
        pass
    w = bpy.data.worlds.new('W'); s.world = w; w.use_nodes = True
    world_color((0.004, 0.006, 0.01), 1.0)
    return s


def world_color(c, strength=1.0):
    bg = bpy.context.scene.world.node_tree.nodes['Background']
    bg.inputs[0].default_value = (*c, 1); bg.inputs[1].default_value = strength


def preview(low=True):
    s = bpy.context.scene
    if low:
        s.render.resolution_x, s.render.resolution_y = 640, 360
        try: s.eevee.taa_render_samples = 8
        except Exception: pass


# ---------------- materials ----------------
def _nodes(m):
    m.use_nodes = True; nt = m.node_tree
    return nt, nt.nodes['Principled BSDF']


def mat(name, color, rough=0.6, metal=0.0, emit=None, estr=0.0, alpha=1.0):
    m = bpy.data.materials.get(name)
    if m: return m
    m = bpy.data.materials.new(name); nt, p = _nodes(m)
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Roughness'].default_value = rough
    p.inputs['Metallic'].default_value = metal
    if emit is not None:
        p.inputs['Emission Color'].default_value = (*emit, 1)
        p.inputs['Emission Strength'].default_value = estr
    if alpha < 1:
        p.inputs['Alpha'].default_value = alpha
    return m


def stone(name, c1, c2, scale=3.0, bump=0.35, rough=0.85):
    """procedural limestone / rock: two-tone noise colour + bump"""
    m = bpy.data.materials.get(name)
    if m: return m
    m = bpy.data.materials.new(name); nt, p = _nodes(m); L = nt.links
    tc = nt.nodes.new('ShaderNodeTexCoord')
    n = nt.nodes.new('ShaderNodeTexNoise'); n.inputs['Scale'].default_value = scale
    n.inputs['Detail'].default_value = 8; n.inputs['Roughness'].default_value = 0.6
    L.new(tc.outputs['Object'], n.inputs['Vector'])
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = (*c1, 1); ramp.color_ramp.elements[1].color = (*c2, 1)
    ramp.color_ramp.elements[0].position = 0.35; ramp.color_ramp.elements[1].position = 0.7
    L.new(n.outputs['Fac'], ramp.inputs['Fac']); L.new(ramp.outputs['Color'], p.inputs['Base Color'])
    n2 = nt.nodes.new('ShaderNodeTexNoise'); n2.inputs['Scale'].default_value = scale * 6; n2.inputs['Detail'].default_value = 10
    L.new(tc.outputs['Object'], n2.inputs['Vector'])
    b = nt.nodes.new('ShaderNodeBump'); b.inputs['Strength'].default_value = bump
    L.new(n2.outputs['Fac'], b.inputs['Height']); L.new(b.outputs['Normal'], p.inputs['Normal'])
    p.inputs['Roughness'].default_value = rough
    return m


def emit_mat(name, color, strength):
    m = bpy.data.materials.get(name)
    if m: return m
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree
    nt.nodes.remove(nt.nodes['Principled BSDF'])
    e = nt.nodes.new('ShaderNodeEmission'); e.inputs[0].default_value = (*color, 1); e.inputs[1].default_value = strength
    nt.links.new(e.outputs[0], nt.nodes['Material Output'].inputs[0])
    return m


def fog(size, loc=(0, 0, 0), density=0.02, color=(1, 1, 1)):
    bpy.ops.mesh.primitive_cube_add(location=loc); o = bpy.context.object
    o.scale = (size[0] / 2, size[1] / 2, size[2] / 2); o.name = 'fog'
    m = bpy.data.materials.new('fog'); m.use_nodes = True; nt = m.node_tree
    nt.nodes.remove(nt.nodes['Principled BSDF'])
    v = nt.nodes.new('ShaderNodeVolumePrincipled'); v.inputs['Density'].default_value = density
    v.inputs['Color'].default_value = (*color, 1)
    nt.links.new(v.outputs[0], nt.nodes['Material Output'].inputs['Volume'])
    o.data.materials.append(m)
    return o


# ---------------- geometry ----------------
def box(loc, size, m=None, name='box', bevel=0.0, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=rot); o = bpy.context.object
    o.scale = (size[0] / 2, size[1] / 2, size[2] / 2); o.name = name
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        b = o.modifiers.new('bv', 'BEVEL'); b.width = bevel; b.segments = 2
    if m: o.data.materials.append(m)
    return o


def cyl(loc, r, h, m=None, rot=(0, 0, 0), verts=24, name='cyl', r2=None):
    if r2 is None:
        bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=h, location=loc, rotation=rot)
    else:
        bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r, radius2=r2, depth=h, location=loc, rotation=rot)
    o = bpy.context.object; o.name = name
    if m: o.data.materials.append(m)
    return o


def sphere(loc, r, m=None, seg=16):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=seg // 2, radius=r, location=loc)
    o = bpy.context.object
    if m: o.data.materials.append(m)
    return o


def plane(loc, size, m=None, rot=(0, 0, 0), name='plane'):
    bpy.ops.mesh.primitive_plane_add(location=loc, rotation=rot); o = bpy.context.object
    o.scale = (size[0] / 2, size[1] / 2, 1); o.name = name
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if m: o.data.materials.append(m)
    return o


def rocky(o, strength=0.4, scale=1.5, subdiv=4):
    """subdivide + displace a mesh so walls look carved out of rock"""
    s = o.modifiers.new('sub', 'SUBSURF'); s.levels = subdiv; s.render_levels = subdiv; s.subdivision_type = 'SIMPLE'
    t = bpy.data.textures.new('rk', 'CLOUDS'); t.noise_scale = scale; t.noise_depth = 3
    d = o.modifiers.new('disp', 'DISPLACE'); d.texture = t; d.strength = strength; d.texture_coords = 'GLOBAL'
    return o


def font_path():
    for p in [r'C:\Windows\Fonts\arialbd.ttf', r'C:\Windows\Fonts\impact.ttf',
              '/usr/share/fonts/opentype/inter/InterDisplay-Black.otf',
              '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf']:
        if os.path.exists(p): return p
    return None


def hand_font():
    for p in [r'C:\Windows\Fonts\segoepr.ttf', r'C:\Windows\Fonts\Inkfree.ttf', r'C:\Windows\Fonts\comic.ttf',
              '/home/user/YTP1/germany_shorts/fonts/PermanentMarker-Regular.ttf']:
        if os.path.exists(p): return p
    return font_path()


def text3d(s, loc, size, m, rot=(math.pi / 2, 0, 0), align='CENTER', extrude=0.0, font=None):
    bpy.ops.object.text_add(location=loc, rotation=rot); o = bpy.context.object
    o.data.body = s; o.data.size = size; o.data.align_x = align; o.data.align_y = 'CENTER'
    o.data.extrude = extrude
    fp = font or font_path()
    if fp:
        try: o.data.font = bpy.data.fonts.load(fp, check_existing=True)
        except Exception: pass
    o.data.materials.append(m)
    return o


# ---------------- lights ----------------
def point(loc, energy, color=(1, 0.8, 0.6), r=0.1):
    bpy.ops.object.light_add(type='POINT', location=loc); l = bpy.context.object
    l.data.energy = energy; l.data.color = color; l.data.shadow_soft_size = r
    return l


def spot(loc, energy, color=(1, 0.9, 0.75), size=40, blend=0.4, rot=(0, 0, 0)):
    bpy.ops.object.light_add(type='SPOT', location=loc, rotation=rot); l = bpy.context.object
    l.data.energy = energy; l.data.color = color; l.data.spot_size = math.radians(size); l.data.spot_blend = blend
    l.data.shadow_soft_size = 0.05
    return l


def area(loc, energy, size=4, color=(1, 1, 1), rot=(0, 0, 0)):
    bpy.ops.object.light_add(type='AREA', location=loc, rotation=rot); l = bpy.context.object
    l.data.energy = energy; l.data.size = size; l.data.color = color
    return l


def sun(rot, strength, color=(1, 1, 1)):
    bpy.ops.object.light_add(type='SUN', rotation=rot); l = bpy.context.object
    l.data.energy = strength; l.data.color = color
    return l


# ---------------- camera ----------------
def camera(keys, lens=35, target_keys=None, shake=0.0):
    """keys: [(frame, (x,y,z))]; target_keys: [(frame, (x,y,z))] the camera looks at"""
    s = bpy.context.scene
    bpy.ops.object.camera_add(); c = bpy.context.object; s.camera = c
    c.data.lens = lens; c.data.clip_end = 2000; c.data.clip_start = 0.05
    for f, p in keys:
        c.location = p; c.keyframe_insert('location', frame=f)
    bpy.ops.object.empty_add(); t = bpy.context.object; t.name = 'cam_target'
    for f, p in (target_keys or [(keys[0][0], (0, 0, 0))]):
        t.location = p; t.keyframe_insert('location', frame=f)
    con = c.constraints.new('TRACK_TO'); con.target = t; con.track_axis = 'TRACK_NEGATIVE_Z'; con.up_axis = 'UP_Y'
    for ob in (c, t):
        ad = ob.animation_data
        if ad and ad.action:
            for fc in _fcurves(ad.action):
                for k in fc.keyframe_points:
                    k.interpolation = 'BEZIER'; k.easing = 'AUTO'
                    k.handle_left_type = k.handle_right_type = 'AUTO_CLAMPED'
    if shake:
        ad = c.animation_data
        for fc in _fcurves(ad.action):
            mod = fc.modifiers.new('NOISE'); mod.scale = 40; mod.strength = shake
    return c


def _fcurves(action):
    # Blender 5 actions are layered; fall back to the legacy list
    try:
        return list(action.fcurves)
    except Exception:
        out = []
        for layer in action.layers:
            for strip in layer.strips:
                for cb in strip.channelbags:
                    out += list(cb.fcurves)
        return out


def key(o, path, frames_vals, index=-1):
    for f, v in frames_vals:
        setattr(o, path, v) if index < 0 else getattr(o, path).__setitem__(index, v)
        o.keyframe_insert(path, frame=f, index=index)


def key_input(sock, frames_vals, data_path_owner=None):
    for f, v in frames_vals:
        sock.default_value = v; sock.keyframe_insert('default_value', frame=f)


def frange(n):
    s = bpy.context.scene; s.frame_start = 0; s.frame_end = n - 1


def render(out_dir, frames=None):
    s = bpy.context.scene; os.makedirs(out_dir, exist_ok=True)
    if frames is None:
        s.render.filepath = os.path.join(out_dir, '')
        bpy.ops.render.render(animation=True)
    else:
        for f in frames:
            s.frame_set(f); s.render.filepath = os.path.join(out_dir, f'{f:04d}.png')
            bpy.ops.render.render(write_still=True)


# ---------------- Poly Haven CC0 textures (downloaded on first use) ----------------
ASSETS = os.environ.get('PEEK_ASSETS', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ph_cache'))


def ph_file(asset, kind, res='2k', ext='jpg', folder='Textures'):
    import urllib.request
    os.makedirs(ASSETS, exist_ok=True)
    fn = f'{asset}_{kind}_{res}.{ext}' if kind else f'{asset}_{res}.{ext}'; p = os.path.join(ASSETS, fn)
    if not os.path.exists(p):
        url = f'https://dl.polyhaven.org/file/ph-assets/{folder}/{ext}/{res}/{asset}/{fn}'
        if folder == 'HDRIs':
            url = f'https://dl.polyhaven.org/file/ph-assets/HDRIs/{ext}/{res}/{fn}'
        data = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'PEEKdocs/1.0'}), timeout=120).read()
        open(p, 'wb').write(data)
    return p


def ph_mat(name, asset, scale=1.0, tint=(1, 1, 1), bump=1.0, rough_mul=1.0, res='2k'):
    """PBR material from a Poly Haven texture set, box-projected in object space (no UVs needed)"""
    m = bpy.data.materials.get(name)
    if m: return m
    m = bpy.data.materials.new(name); nt, p = _nodes(m); L = nt.links
    tc = nt.nodes.new('ShaderNodeTexCoord'); mp = nt.nodes.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (scale, scale, scale)
    L.new(tc.outputs['Object'], mp.inputs['Vector'])

    def tex(kind, non_color):
        t = nt.nodes.new('ShaderNodeTexImage')
        t.image = bpy.data.images.load(ph_file(asset, kind, res), check_existing=True)
        if non_color: t.image.colorspace_settings.name = 'Non-Color'
        t.projection = 'BOX'; t.projection_blend = 0.25
        L.new(mp.outputs['Vector'], t.inputs['Vector'])
        return t
    d = tex('diff', False)
    mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'; mix.blend_type = 'MULTIPLY'
    mix.inputs['Factor'].default_value = 1.0
    L.new(d.outputs['Color'], mix.inputs['A']); mix.inputs['B'].default_value = (*tint, 1)
    L.new(mix.outputs['Result'], p.inputs['Base Color'])
    r = tex('rough', True)
    mr = nt.nodes.new('ShaderNodeMath'); mr.operation = 'MULTIPLY'; mr.inputs[1].default_value = rough_mul
    L.new(r.outputs['Color'], mr.inputs[0]); L.new(mr.outputs[0], p.inputs['Roughness'])
    n = tex('nor_gl', True)
    nm = nt.nodes.new('ShaderNodeNormalMap'); nm.inputs['Strength'].default_value = bump
    L.new(n.outputs['Color'], nm.inputs['Color']); L.new(nm.outputs['Normal'], p.inputs['Normal'])
    return m


def hdri_world(asset, strength=1.0, show=True, bg=(0, 0, 0)):
    w = bpy.context.scene.world; nt = w.node_tree; L = nt.links
    env = nt.nodes.new('ShaderNodeTexEnvironment')
    env.image = bpy.data.images.load(ph_file(asset, '', '2k', 'hdr', 'HDRIs'), check_existing=True)
    bgn = nt.nodes['Background']; L.new(env.outputs['Color'], bgn.inputs['Color']); bgn.inputs['Strength'].default_value = strength
