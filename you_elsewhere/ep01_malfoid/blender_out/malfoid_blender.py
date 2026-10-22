# You, Elsewhere EP1 (Malfoid): Blender look test.
# Builds the whole scene from one still photo and renders it.
# usage: blender -b --factory-startup -P malfoid_blender.py -- <assets_dir> <out_dir> [stills|video|both] [frames]
# The photo sits on an emission plane under a fixed orthographic camera; every effect is a mask-limited
# shader/compositor effect so the woman's pixels are never displaced (no zoom, no camera move, no beat sync).
import bpy, sys, os, math, numpy as np, aud
import math as math_

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
ASSETS = argv[0] if len(argv) > 0 else os.path.join(os.path.dirname(__file__), 'assets')
OUT = argv[1] if len(argv) > 1 else os.path.dirname(__file__)
MODE = argv[2] if len(argv) > 2 else 'stills'
FRAMES = [int(x) for x in argv[3].split(',')] if len(argv) > 3 else [91, 601]
USE_SPECTRUM = True

W, H, FPS, SECS = 1920, 1080, 30, 40
NF = FPS * SECS
IW, IH = 1672, 941                      # source photo size
PW, PH = 16.0, 16.0 * IH / IW           # plane size in world units (120 px per unit)
PX = W / PW                             # output pixels per world unit
rng = np.random.default_rng(11)

def t_of(f): return (f - 1) / FPS
def img2world(u, v): return ((u / IW - 0.5) * PW, (0.5 - v / IH) * PH)

# ---------------------------------------------------------------- scene / render settings
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = 'BLENDER_EEVEE'
sc.eevee.taa_render_samples = 16
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = W, H, 100
sc.render.fps = FPS
sc.render.filter_size = 1.0
sc.render.film_transparent = True
sc.frame_start, sc.frame_end = 1, NF
sc.view_settings.view_transform = 'Standard'
sc.view_settings.look = 'None'
sc.view_settings.exposure, sc.view_settings.gamma = 0.0, 1.0
sc.render.use_compositing = True
sc.render.use_sequencer = False

cam_data = bpy.data.cameras.new('Cam'); cam_data.type = 'ORTHO'; cam_data.ortho_scale = PW
cam = bpy.data.objects.new('Cam', cam_data); sc.collection.objects.link(cam)
cam.location = (0, 0, 10); sc.camera = cam
cam_data.clip_start, cam_data.clip_end = 0.1, 50

col_main = bpy.data.collections.new('Main'); sc.collection.children.link(col_main)
col_wm = bpy.data.collections.new('Watermark'); sc.collection.children.link(col_wm)
col_spec = bpy.data.collections.new('Spectrum'); sc.collection.children.link(col_spec)

def key_series(owner, path, values, frames=None, index=-1, interp='LINEAR'):
    """Insert one keyframe per value (frames default 1..N), then set interpolation."""
    frames = frames or list(range(1, len(values) + 1))
    for f, v in zip(frames, values):
        if index >= 0:
            getattr(owner, path)[index] = v
        else:
            setattr(owner, path, v)
        owner.keyframe_insert(path, frame=f, index=index)
    return interp

def set_interp(idblock, interp):
    ad = idblock.animation_data
    if not ad or not ad.action: return
    for layer in ad.action.layers:
        for strip in layer.strips:
            for cb in strip.channelbags:
                for fc in cb.fcurves:
                    for k in fc.keyframe_points: k.interpolation = interp
                    if interp == 'LINEAR': fc.extrapolation = 'LINEAR'

# ---------------------------------------------------------------- masks (computed in image pixel space)
yy, xx = np.mgrid[0:IH, 0:IW].astype(np.float32)
def sstep(a, b, x):
    k = np.clip((x - a) / (b - a), 0, 1); return k * k * (3 - 2 * k)
def ellipse(cx, cy, rx, ry, soft):
    d = np.sqrt(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2)
    return 1 - sstep(1 - soft, 1, d)
# R: firelight on the left wall, faded out well before the woman (her coat starts ~x 280 low down)
person_guard = np.maximum(sstep(300, 520, xx), sstep(250, 330, xx) * sstep(600, 680, yy))
fire = np.exp(-(((xx - 90) / 300) ** 2 + ((yy - 560) / 330) ** 2)) * (1 - person_guard)
# G: heat shimmer, only inside the fireplace opening
shim = (1 - sstep(170, 200, xx)) * sstep(380, 420, yy) * (1 - sstep(740, 770, yy))
# B: glass of the round windows (right window, plus the part of the left one that is clear of her hair)
win_r = ellipse(1547, 205, 116, 212, 0.06) * (1 - sstep(1610, 1630, xx) * sstep(255, 275, yy))
win_l = ellipse(1296, 190, 42, 136, 0.12) * np.maximum(sstep(1302, 1312, xx), (1 - sstep(115, 130, yy)) * sstep(1262, 1272, xx))
glass = np.clip(win_r + win_l, 0, 1)
# A: lake surface seen through the right window
water = win_r * sstep(290, 305, yy)
# vignette (display-space factor, converted to linear)
d = np.sqrt(((xx - IW / 2) / (IW / 2)) ** 2 + ((yy - IH / 2) / (IH / 2)) ** 2)
vig = (1 - 0.26 * np.clip(d - 0.45, 0, 1) ** 1.6) ** 2.2

def np_image(name, rgba):
    img = bpy.data.images.new(name, IW, IH, alpha=True, float_buffer=True)
    img.colorspace_settings.name = 'Non-Color'
    img.pixels.foreach_set(np.ascontiguousarray(rgba[::-1]).astype(np.float32).ravel())
    img.pack()
    return img
mask1 = np_image('mask_fx', np.stack([fire, shim, glass, water], -1))
mask2 = np_image('mask_grade', np.stack([vig, vig, vig, np.ones_like(vig)], -1))

# ---------------------------------------------------------------- photo plane material
photo = bpy.data.images.load(os.path.join(ASSETS, 'closeup.png')); photo.pack()
bpy.ops.mesh.primitive_plane_add(size=1)
plane = bpy.context.object; plane.name = 'Photo'
plane.scale = (PW, PH, 1)
for c in plane.users_collection: c.objects.unlink(plane)
col_main.objects.link(plane)

mat = bpy.data.materials.new('PhotoFX'); plane.data.materials.append(mat)
nt = mat.node_tree; N = nt.nodes; L = nt.links
for n in list(N): N.remove(n)
def node(t, x, y, **kw):
    n = N.new(t); n.location = (x * 220, -y * 160)
    for k, v in kw.items(): setattr(n, k, v)
    return n
def math(op, a, b=None, x=0, y=0):
    n = node('ShaderNodeMath', x, y, operation=op)
    for i, v in enumerate([a, b]):
        if v is None: continue
        if isinstance(v, (int, float)): n.inputs[i].default_value = v
        else: L.new(v, n.inputs[i])
    return n.outputs[0]
def vmath(op, a, b=None, x=0, y=0, scale=None):
    n = node('ShaderNodeVectorMath', x, y, operation=op)
    for i, v in enumerate([a, b]):
        if v is None: continue
        if isinstance(v, (tuple, list)): n.inputs[i].default_value = v
        else: L.new(v, n.inputs[i])
    if scale is not None:
        if isinstance(scale, (int, float)): n.inputs['Scale'].default_value = scale
        else: L.new(scale, n.inputs['Scale'])
    return n.outputs['Vector'] if op != 'DOT_PRODUCT' else n.outputs['Value']
def combine(x_, y_, z_, x=0, y=0):
    n = node('ShaderNodeCombineXYZ', x, y)
    for i, v in enumerate([x_, y_, z_]):
        if isinstance(v, (int, float)): n.inputs[i].default_value = v
        else: L.new(v, n.inputs[i])
    return n.outputs[0]
def noise(vec, w, scale=1.0, detail=2.0, x=0, y=0):
    n = node('ShaderNodeTexNoise', x, y, noise_dimensions='4D')
    n.inputs['Scale'].default_value = scale; n.inputs['Detail'].default_value = detail
    L.new(vec, n.inputs['Vector'])
    if isinstance(w, (int, float)): n.inputs['W'].default_value = w
    else: L.new(w, n.inputs['W'])
    return n

tc = node('ShaderNodeTexCoord', 0, 0)
uv = tc.outputs['UV']
sep = node('ShaderNodeSeparateXYZ', 1, 0); L.new(uv, sep.inputs[0])
U, V = sep.outputs[0], sep.outputs[1]
tval = node('ShaderNodeValue', 0, 2, label='time_s', name='time_s')
T = tval.outputs[0]
fval = node('ShaderNodeValue', 0, 3, label='flicker', name='flicker')
Fk = fval.outputs[0]

m1 = node('ShaderNodeTexImage', 2, 1, image=mask1, interpolation='Linear'); L.new(uv, m1.inputs[0])
msep = node('ShaderNodeSeparateColor', 3, 1); L.new(m1.outputs['Color'], msep.inputs[0])
M_FIRE, M_SHIM, M_GLASS = msep.outputs[0], msep.outputs[1], msep.outputs[2]
M_WATER = m1.outputs['Alpha']

# heat shimmer: rising noise, offsets UV inside the fireplace only (~2 px)
v_up = math('SUBTRACT', V, math('MULTIPLY', T, 0.09, 2, 4), 3, 4)
nz = noise(combine(math('MULTIPLY', U, 70.0, 3, 5), math('MULTIPLY', v_up, 38.0, 4, 5), 0, 5, 5), math('MULTIPLY', T, 0.7, 4, 6), 1.0, 3.0, 6, 5)
off_shim = vmath('SCALE', vmath('SUBTRACT', nz.outputs['Color'], (0.5, 0.5, 0.5), x=7, y=5), scale=math('MULTIPLY', M_SHIM, 0.0030, 7, 6), x=8, y=5)
# water on the glass: slow downward-drifting refraction wobble (~1 px)
v_dn = math('ADD', V, math('MULTIPLY', T, 0.012, 2, 7), 3, 7)
ng_ = noise(combine(math('MULTIPLY', U, 140.0, 3, 8), math('MULTIPLY', v_dn, 60.0, 4, 8), 0, 5, 8), math('MULTIPLY', T, 0.08, 4, 9), 1.0, 2.0, 6, 8)
off_glass = vmath('SCALE', vmath('SUBTRACT', ng_.outputs['Color'], (0.5, 0.5, 0.5), x=7, y=8), scale=math('MULTIPLY', M_GLASS, 0.0011, 7, 9), x=8, y=8)
# lake ripple: horizontal shimmer on the water surface (~1.5 px)
nw = noise(combine(math('MULTIPLY', U, 30.0, 3, 10), math('MULTIPLY', V, 260.0, 4, 10), 0, 5, 10), math('MULTIPLY', T, 0.35, 4, 11), 1.0, 2.0, 6, 10)
nws = node('ShaderNodeSeparateXYZ', 7, 10); L.new(nw.outputs['Color'], nws.inputs[0])
off_water = combine(math('MULTIPLY', math('SUBTRACT', nws.outputs[0], 0.5, 8, 10), math('MULTIPLY', M_WATER, 0.0022, 8, 11), 9, 10), 0, 0, 10, 10)
uv2 = vmath('ADD', vmath('ADD', uv, off_shim, x=9, y=5), vmath('ADD', off_glass, off_water, x=10, y=9), x=11, y=6)

ph = node('ShaderNodeTexImage', 12, 3, image=photo, interpolation='Cubic', extension='EXTEND'); L.new(uv2, ph.inputs[0])
C = ph.outputs['Color']

# rain streaks on the glass: two layers of thin, vertically stretched noise falling at different speeds
def streaks(sx, sy, speed, lo, hi, gain, row):
    vv = math('ADD', math('MULTIPLY', V, sy, 2, row), math('MULTIPLY', T, speed, 3, row), 4, row)
    n = noise(combine(math('MULTIPLY', U, sx, 5, row), vv, 0, 6, row), math('MULTIPLY', T, 0.03, 6, row + 1), 1.0, 1.0, 7, row)
    r = node('ShaderNodeMapRange', 8, row); L.new(n.outputs['Fac'], r.inputs['Value'])
    r.inputs['From Min'].default_value, r.inputs['From Max'].default_value = lo, hi
    return math('MULTIPLY', math('MULTIPLY', r.outputs['Result'], M_GLASS, 9, row), gain, 10, row)
rain = math('ADD', streaks(420.0, 4.0, 0.55, 0.64, 0.74, 0.030, 13), streaks(760.0, 7.0, 1.25, 0.66, 0.76, 0.020, 15), 11, 14)
rain_c = vmath('SCALE', (0.80, 0.95, 1.0), scale=rain, x=12, y=14)
C = vmath('ADD', C, rain_c, x=13, y=4)

# firelight breathing on the left wall (warm tinted gain), value keyframed per frame
fire_gain = vmath('SCALE', (1.0, 0.78, 0.50), scale=math('MULTIPLY', M_FIRE, Fk, 12, 7), x=13, y=7)
C = vmath('MULTIPLY', C, vmath('ADD', fire_gain, (1, 1, 1), x=14, y=7), x=14, y=4)

# grade: vignette, warm tone, slightly lifted blacks
m2 = node('ShaderNodeTexImage', 13, 0, image=mask2, interpolation='Linear'); L.new(uv, m2.inputs[0])
C = vmath('MULTIPLY', C, m2.outputs['Color'], x=15, y=3)
C = vmath('MULTIPLY', C, (1.025, 1.0, 0.965), x=16, y=3)
C = vmath('MULTIPLY_ADD', C, (0.993, 0.993, 0.993), x=17, y=3)
nt.nodes[-1].inputs[2].default_value = (0.0022, 0.0019, 0.0016)

# film grain: per-pixel mono white noise, fresh every frame (W = frame time)
pix = vmath('FLOOR', vmath('MULTIPLY', uv, (W, H, 0), x=13, y=17), x=14, y=17)
wn = node('ShaderNodeTexWhiteNoise', 15, 17, noise_dimensions='4D'); L.new(pix, wn.inputs['Vector'])
L.new(math('MULTIPLY', T, 30.0, 14, 18), wn.inputs['W'])
g = math('SUBTRACT', wn.outputs['Value'], 0.5, 16, 17)
C = vmath('MULTIPLY_ADD', C, combine(*(math('ADD', math('MULTIPLY', g, 0.16, 17, 17), 1.0, 17, 18),) * 3, x=18, y=17), x=18, y=3)
nt.nodes[-1].inputs[2].default_value = (0, 0, 0)
C = vmath('ADD', C, vmath('SCALE', (1, 1, 1), scale=math('MULTIPLY', g, 0.006, 18, 19), x=19, y=18), x=19, y=3)

em = node('ShaderNodeEmission', 20, 3); L.new(C, em.inputs['Color']); em.inputs['Strength'].default_value = 1.0
out = node('ShaderNodeOutputMaterial', 21, 3); L.new(em.outputs[0], out.inputs['Surface'])

# per-frame drivers of the photo shader
key_series(tval.outputs[0], 'default_value', [0.0, SECS], frames=[1, NF + 1])
def flicker(t):
    # layered slow sines + gentle noise: never periodic on a beat, max about +-5 %
    s = (0.55 * math_.sin(2 * math_.pi * 0.23 * t + 1.3) + 0.35 * math_.sin(2 * math_.pi * 0.61 * t + 0.4)
         + 0.25 * math_.sin(2 * math_.pi * 1.37 * t + 2.1) + 0.12 * math_.sin(2 * math_.pi * 2.9 * t + 0.7))
    return 0.045 * s / 1.27

fl = np.array([flicker(t_of(f)) for f in range(1, NF + 1)])
fl += np.convolve(rng.normal(0, 0.012, NF), np.ones(5) / 5, 'same')
key_series(fval.outputs[0], 'default_value', list(fl))
set_interp(mat.node_tree, 'LINEAR')

# ---------------------------------------------------------------- dust motes + slow light leak (additive planes)
def glow_material(name, edge_lo, edge_hi):
    m = bpy.data.materials.new(name); m.surface_render_method = 'BLENDED'
    t = m.node_tree; n_ = t.nodes; l_ = t.links
    for n in list(n_): n_.remove(n)
    co = n_.new('ShaderNodeTexCoord'); gr = n_.new('ShaderNodeTexGradient'); gr.gradient_type = 'SPHERICAL'
    l_.new(co.outputs['Object'], gr.inputs['Vector'])
    mr = n_.new('ShaderNodeMapRange'); mr.interpolation_type = 'SMOOTHSTEP'
    mr.inputs['From Min'].default_value, mr.inputs['From Max'].default_value = edge_lo, edge_hi
    l_.new(gr.outputs['Fac'], mr.inputs['Value'])
    oi = n_.new('ShaderNodeObjectInfo')
    mul = n_.new('ShaderNodeMath'); mul.operation = 'MULTIPLY'
    l_.new(mr.outputs['Result'], mul.inputs[0]); l_.new(oi.outputs['Alpha'], mul.inputs[1])
    em_ = n_.new('ShaderNodeEmission'); l_.new(oi.outputs['Color'], em_.inputs['Color']); l_.new(mul.outputs[0], em_.inputs['Strength'])
    tr = n_.new('ShaderNodeBsdfTransparent'); ad = n_.new('ShaderNodeAddShader')
    l_.new(tr.outputs[0], ad.inputs[0]); l_.new(em_.outputs[0], ad.inputs[1])
    o = n_.new('ShaderNodeOutputMaterial'); l_.new(ad.outputs[0], o.inputs['Surface'])
    return m
mote_mat = glow_material('Mote', 0.0, 0.35)   # soft-edged bokeh disc
leak_mat = glow_material('LightLeak', 0.0, 1.0)

def add_disc(name, mat_, radius_px, z):
    bpy.ops.mesh.primitive_plane_add(size=2)
    o = bpy.context.object; o.name = name
    for c in o.users_collection: c.objects.unlink(o)
    col_main.objects.link(o)
    o.data.materials.append(mat_)
    s = radius_px / PX; o.scale = (s, s, 1); o.location.z = z
    return o

# motes live only in the warm left part of the room (x < ~700 px); they fade out before reaching her
NM = 24
FACE_X0 = 640.0
key_frames = list(range(1, NF + 2, 15))
for j in range(NM):
    depth = rng.random()                       # 0 = far/sharp & small, 1 = near/defocused & big
    r_px = 1.6 + depth ** 2 * 9.0
    base_a = 0.85 * (1 - 0.75 * depth) * rng.uniform(0.6, 1.0)
    o = add_disc(f'Mote{j:02d}', mote_mat, r_px, 0.5 + depth)
    x0, y0 = rng.uniform(10, 660), rng.uniform(40, 900)
    vx, vy = rng.normal(2.5, 3.0), rng.normal(-4.0, 2.0)          # px / s, slow upward drift
    ax, ay, fx, fy, ph_ = rng.uniform(6, 16), rng.uniform(4, 10), rng.uniform(0.02, 0.06), rng.uniform(0.02, 0.05), rng.uniform(0, 6.28)
    warm = np.array([1.0, 0.86, 0.66]) * rng.uniform(0.9, 1.1)
    for f in key_frames:
        t = t_of(f)
        x = x0 + vx * t + ax * math_.sin(2 * math_.pi * fx * t + ph_)
        y = (y0 + vy * t + ay * math_.sin(2 * math_.pi * fy * t + ph_ * 1.7)) % IH
        x = x % 700
        wx, wy = img2world(x, y)
        o.location.x, o.location.y = wx, wy
        o.keyframe_insert('location', index=0, frame=f); o.keyframe_insert('location', index=1, frame=f)
        tw = 0.65 + 0.35 * math_.sin(2 * math_.pi * rng.uniform(0.05, 0.12) * t + ph_)
        edge = (1 - sstep(FACE_X0 - 140, FACE_X0, np.float32(x))) * sstep(0, 40, np.float32(x)) * sstep(0, 40, np.float32(y)) * (1 - sstep(IH - 40, IH, np.float32(y)))
        o.color = (*warm, float(base_a * tw * edge) * 0.55)
        o.keyframe_insert('color', frame=f)
    # wrap-around jumps would streak across the frame: make them hard cuts at alpha 0
    set_interp(o, 'BEZIER')
    for layer in o.animation_data.action.layers:
        for strip in layer.strips:
            for cb in strip.channelbags:
                fcs = {(fc.data_path, fc.array_index): fc for fc in cb.fcurves}
                for idx in (0, 1):
                    kp = fcs[('location', idx)].keyframe_points
                    for i in range(1, len(kp)):
                        if abs(kp[i].co.y - kp[i - 1].co.y) > 2.5:
                            kp[i - 1].interpolation = 'CONSTANT'

leak = add_disc('LightLeak', leak_mat, 640, 0.3)
leak.color = (1.0, 0.50, 0.20, 0.035)
for f in range(1, NF + 2, 30):
    t = t_of(f)
    leak.location.x, leak.location.y = img2world(-90 + 70 * math_.sin(2 * math_.pi * t / 34.0), 470 + 160 * math_.sin(2 * math_.pi * t / 52.0 + 1.0))
    leak.keyframe_insert('location', frame=f)
set_interp(leak, 'BEZIER')

# ---------------------------------------------------------------- watermark (own view layer, composited unaffected by glare/CA)
font = bpy.data.fonts.load(os.path.join(ASSETS, 'Allura.ttf'))
cu = bpy.data.curves.new('WM', 'FONT'); cu.body = 'You, Elsewhere'; cu.font = font
wm = bpy.data.objects.new('WM', cu); col_wm.objects.link(wm)
wm_mat = bpy.data.materials.new('WMText'); wm_mat.use_nodes = True
wn_ = wm_mat.node_tree.nodes; [wn_.remove(n) for n in list(wn_)]
e_ = wn_.new('ShaderNodeEmission'); e_.inputs['Color'].default_value = (*(((c / 255) ** 2.2) for c in (246, 238, 224)), 1)
o_ = wn_.new('ShaderNodeOutputMaterial'); wm_mat.node_tree.links.new(e_.outputs[0], o_.inputs['Surface'])
cu.materials.append(wm_mat)
cu.size = 1.0
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()
bb = np.array([wm.evaluated_get(dg).bound_box[i] for i in range(8)])
hgt = bb[:, 1].max() - bb[:, 1].min()
cu.size = (60 / PX) / hgt
bpy.context.view_layer.update(); dg = bpy.context.evaluated_depsgraph_get()
bb = np.array([wm.evaluated_get(dg).bound_box[i] for i in range(8)])
wm.location = (-PW / 2 + 64 / PX - bb[:, 0].min(), -H / PX / 2 + 64 / PX - bb[:, 1].min(), 2.0)
wm_right_px = (wm.location.x + bb[:, 0].max()) * PX + W / 2
wm_mid_y = wm.location.y + (bb[:, 1].min() + bb[:, 1].max()) / 2

# small, detailed audio spectrum right of the watermark (35 % opacity, max ~20 px, ~130 px wide), mirrored
# around a centre line like the v1 bars. Filled polyline with sharp vertices (pointed peaks); values baked into a float image
# (bands x frames) that a Geometry Nodes tree samples per frame, so the .blend animates on its own.
if USE_SPECTRUM:
    snd = aud.Sound(os.path.join(ASSETS, 'music_60s.mp3'))
    sr = snd.specs[0]
    data = snd.data()
    mono = data.mean(axis=1) if data.ndim > 1 else data
    NB, WIN = 64, 8192
    centers = np.geomspace(40, 1500, NB)        # where the piano and bass live
    freqs = np.fft.rfftfreq(WIN, 1 / sr)
    hann = np.hanning(WIN)
    lo_e = centers / 2 ** (1 / 2 / (NB / 7.4)); hi_e = centers * 2 ** (1 / 2 / (NB / 7.4))
    mags = np.zeros((NF, NB))
    for i in range(NF):
        c0 = int(t_of(i + 1) * sr) - WIN // 2
        seg = mono[max(c0, 0):c0 + WIN]
        if len(seg) < WIN: seg = np.pad(seg, (WIN - len(seg), 0))
        sp = np.abs(np.fft.rfft(seg * hann))
        interp = np.interp(centers, freqs, sp)
        for b in range(NB):
            sel = (freqs >= lo_e[b]) & (freqs < hi_e[b])
            mags[i, b] = max(sp[sel].max(), interp[b]) if sel.any() else interp[b]
    db = 20 * np.log10(mags + 1e-6)
    # partial tilt compensation (3/4 of each band's mean), then one global range -> rise and fall stays visible
    db = db - 0.75 * db.mean(axis=0, keepdims=True)
    lo, hi = np.percentile(db, 30), np.percentile(db, 99.3)
    v = np.clip((db - lo) / (hi - lo), 0, 1) ** 1.5
    att, rel = 1 - math_.exp(-1 / (0.05 * FPS)), 1 - math_.exp(-1 / (0.18 * FPS))
    sm = np.zeros_like(v); cur = np.zeros(NB)
    for i in range(NF):
        k = np.where(v[i] > cur, att, rel); cur = cur + (v[i] - cur) * k; sm[i] = cur
    env = np.array([min(1, t_of(f) / 3.0, max(0, (SECS - t_of(f)) / 4.0)) for f in range(1, NF + 1)])
    sm *= env[:, None]
    taper = np.minimum(1, np.minimum(np.arange(NB) + 1, NB - np.arange(NB)) / 3.0)   # ends settle to the baseline
    sm *= taper[None, :]
    spec_img = bpy.data.images.new('spectrum_bake', NB, NF, alpha=False, float_buffer=True)
    spec_img.colorspace_settings.name = 'Non-Color'
    px_ = np.zeros((NF, NB, 4), np.float32); px_[..., 0] = sm; px_[..., 3] = 1
    spec_img.pixels.foreach_set(px_.ravel()); spec_img.pack()

    X0, HMAX = wm_right_px + 26, 20.0                           # output pixels
    xs = X0 + np.arange(NB) * 2.0
    verts, faces, uvals, tops = [], [], [], []
    for b, x in enumerate(xs):
        wx, wy = (x - W / 2) / PX, wm_mid_y - 6 / PX
        verts += [(wx, wy - 0.5 / PX, 0), (wx, wy + 0.5 / PX, 0)]   # 1 px minimum line
        uvals += [(b + 0.5) / NB] * 2; tops += [-0.5, 0.5]
        if b: faces.append((2 * b - 2, 2 * b, 2 * b + 1, 2 * b - 1))
    me = bpy.data.meshes.new('Spectrum'); me.from_pydata(verts, [], faces); me.update()
    me.attributes.new('su', 'FLOAT', 'POINT').data.foreach_set('value', uvals)
    me.attributes.new('top', 'FLOAT', 'POINT').data.foreach_set('value', tops)
    so = bpy.data.objects.new('Spectrum', me); col_spec.objects.link(so); so.location.z = 2.0
    bar_mat = bpy.data.materials.new('SpecFill')
    bn = bar_mat.node_tree.nodes; [bn.remove(n) for n in list(bn)]
    be = bn.new('ShaderNodeEmission'); be.inputs['Color'].default_value = e_.inputs['Color'].default_value
    bo = bn.new('ShaderNodeOutputMaterial'); bar_mat.node_tree.links.new(be.outputs[0], bo.inputs['Surface'])
    me.materials.append(bar_mat)
    gt = bpy.data.node_groups.new('SpectrumGN', 'GeometryNodeTree')
    gt.interface.new_socket('Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')
    gt.interface.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
    gn, gl = gt.nodes, gt.links
    gi = gn.new('NodeGroupInput'); go_ = gn.new('NodeGroupOutput')
    st = gn.new('GeometryNodeInputSceneTime')
    a_su = gn.new('GeometryNodeInputNamedAttribute'); a_su.data_type = 'FLOAT'; a_su.inputs['Name'].default_value = 'su'
    a_top = gn.new('GeometryNodeInputNamedAttribute'); a_top.data_type = 'FLOAT'; a_top.inputs['Name'].default_value = 'top'
    fv = gn.new('ShaderNodeMath'); fv.operation = 'MULTIPLY_ADD'      # v = (frame - 0.5) / NF
    gl.new(st.outputs['Frame'], fv.inputs[0]); fv.inputs[1].default_value = 1 / NF; fv.inputs[2].default_value = -0.5 / NF
    cxyz = gn.new('ShaderNodeCombineXYZ'); gl.new(a_su.outputs['Attribute'], cxyz.inputs[0]); gl.new(fv.outputs[0], cxyz.inputs[1])
    it = gn.new('GeometryNodeImageTexture'); it.inputs['Image'].default_value = spec_img
    it.interpolation = 'Closest'; gl.new(cxyz.outputs[0], it.inputs['Vector'])
    sepc = gn.new('FunctionNodeSeparateColor'); gl.new(it.outputs['Color'], sepc.inputs[0])
    hm = gn.new('ShaderNodeMath'); hm.operation = 'MULTIPLY'; gl.new(sepc.outputs[0], hm.inputs[0]); hm.inputs[1].default_value = (HMAX - 1) / PX
    hm2 = gn.new('ShaderNodeMath'); hm2.operation = 'MULTIPLY'; gl.new(hm.outputs[0], hm2.inputs[0]); gl.new(a_top.outputs['Attribute'], hm2.inputs[1])
    off = gn.new('ShaderNodeCombineXYZ'); gl.new(hm2.outputs[0], off.inputs[1])
    sp_ = gn.new('GeometryNodeSetPosition'); gl.new(gi.outputs[0], sp_.inputs['Geometry']); gl.new(off.outputs[0], sp_.inputs['Offset'])
    gl.new(sp_.outputs[0], go_.inputs[0])
    mod = so.modifiers.new('Spectrum', 'NODES'); mod.node_group = gt

# ---------------------------------------------------------------- view layers
vl_main = sc.view_layers[0]; vl_main.name = 'Main'
vl_wm = sc.view_layers.new('WM')
vl_spec = sc.view_layers.new('SPEC')
vl_main.layer_collection.children['Watermark'].exclude = True
vl_main.layer_collection.children['Spectrum'].exclude = True
vl_wm.layer_collection.children['Main'].exclude = True
vl_wm.layer_collection.children['Spectrum'].exclude = True
vl_spec.layer_collection.children['Main'].exclude = True
vl_spec.layer_collection.children['Watermark'].exclude = True

# ---------------------------------------------------------------- compositor
cg = bpy.data.node_groups.new('Comp', 'CompositorNodeTree'); sc.compositing_node_group = cg
cg.interface.new_socket('Image', in_out='OUTPUT', socket_type='NodeSocketColor')
cn, cl = cg.nodes, cg.links
def cnode(t, x, y, **inputs):
    n = cn.new(t); n.location = (x * 240, -y * 200)
    for k, v in inputs.items(): n.inputs[k].default_value = v
    return n
rl = cnode('CompositorNodeRLayers', 0, 0); rl.layer = 'Main'
rw = cnode('CompositorNodeRLayers', 0, 3); rw.layer = 'WM'
glare = cnode('CompositorNodeGlare', 1, 0, Type='Bloom', Quality='High', Threshold=0.55, Smoothness=0.6, Strength=0.32, Saturation=1.0, Size=0.55)
cl.new(rl.outputs['Image'], glare.inputs['Image'])
lens = cnode('CompositorNodeLensdist', 2, 0, Type='Radial', Distortion=0.0, Dispersion=0.012, Fit=False)
cl.new(glare.outputs['Image'], lens.inputs['Image'])
fade = cnode('CompositorNodeExposure', 3, 0, Exposure=0.0); fade.name = 'Fade'
cl.new(lens.outputs['Image'], fade.inputs['Image'])
# shadow: blurred, offset watermark alpha as soft dark shape
blur = cnode('CompositorNodeBlur', 1, 4, Size=(5, 5), Type='Gaussian'); cl.new(rw.outputs['Alpha'], blur.inputs['Image'])
tr_ = cnode('CompositorNodeTranslate', 2, 4, X=2.0, Y=-3.0); cl.new(blur.outputs['Image'], tr_.inputs['Image'])
shs = cnode('CompositorNodeSeparateColor', 3, 4); cl.new(tr_.outputs['Image'], shs.inputs['Image'])
shm = cnode('ShaderNodeMath', 4, 4); shm.operation = 'MULTIPLY'; shm.inputs[1].default_value = 0.55; cl.new(shs.outputs['Red'], shm.inputs[0])
sha = cnode('CompositorNodeSetAlpha', 5, 4, Image=(0, 0, 0, 1), Type='Replace Alpha'); cl.new(shm.outputs[0], sha.inputs['Alpha'])
ao1 = cnode('CompositorNodeAlphaOver', 6, 1); cl.new(fade.outputs['Image'], ao1.inputs['Background']); cl.new(sha.outputs['Image'], ao1.inputs['Foreground'])
ao2 = cnode('CompositorNodeAlphaOver', 7, 1, Factor=0.8); cl.new(ao1.outputs['Image'], ao2.inputs['Background']); cl.new(rw.outputs['Image'], ao2.inputs['Foreground'])
rs = cnode('CompositorNodeRLayers', 0, 6); rs.layer = 'SPEC'
ao3 = cnode('CompositorNodeAlphaOver', 8, 1, Factor=0.35); cl.new(ao2.outputs['Image'], ao3.inputs['Background']); cl.new(rs.outputs['Image'], ao3.inputs['Foreground'])
go = cn.new('NodeGroupOutput'); go.location = (9 * 240, -200); cl.new(ao3.outputs['Image'], go.inputs[0])

# 60 % -> 100 % brightness over the first 5 s (smoothstep, display-referred), then constant
def fade_k(t):
    k = min(t / 5.0, 1.0); k = k * k * (3 - 2 * k)
    return 2.2 * math_.log2(0.6 + 0.4 * k)
for f in list(range(1, 5 * FPS + 2)):
    fade.inputs['Exposure'].default_value = fade_k(t_of(f))
    fade.inputs['Exposure'].keyframe_insert('default_value', frame=f)
set_interp(cg, 'LINEAR')
for fc_owner in [cg]:
    for layer in fc_owner.animation_data.action.layers:
        for strip in layer.strips:
            for cb in strip.channelbags:
                for fc in cb.fcurves: fc.extrapolation = 'CONSTANT'

# ---------------------------------------------------------------- save + render
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, 'malfoid_blender_v3.blend'), compress=True)
import time
if MODE in ('stills', 'both'):
    sc.render.image_settings.media_type = 'IMAGE'
    sc.render.image_settings.file_format = 'JPEG'; sc.render.image_settings.quality = 95
    for f in FRAMES:
        sc.frame_set(f); t0 = time.time()
        sc.render.filepath = os.path.join(OUT, f'malfoid_still_f{f:04d}_t{t_of(f):05.2f}s.jpg')
        bpy.ops.render.render(write_still=True)
        print(f'STILL frame {f} rendered in {time.time() - t0:.2f}s')
if MODE == 'frames':
    # resumable PNG sequence (skips frames already on disk), encoded with ffmpeg afterwards
    sc.render.image_settings.media_type = 'IMAGE'
    sc.render.image_settings.file_format = 'PNG'; sc.render.image_settings.compression = 15
    sc.render.use_overwrite = False; sc.render.use_placeholder = True
    sc.render.filepath = os.path.join(OUT, 'frames_v3', 'f_')
    t0 = time.time()
    bpy.ops.render.render(animation=True)
    print(f'FRAMES done in {time.time() - t0:.1f}s')
if MODE in ('video', 'both'):
    sc.render.image_settings.media_type = 'VIDEO'
    sc.render.image_settings.file_format = 'FFMPEG'
    sc.render.ffmpeg.format = 'MPEG4'; sc.render.ffmpeg.codec = 'H264'
    sc.render.ffmpeg.constant_rate_factor = 'HIGH'
    sc.render.ffmpeg.ffmpeg_preset = 'GOOD'
    sc.render.ffmpeg.audio_codec = 'NONE'
    sc.render.filepath = os.path.join(OUT, 'malfoid_blender_v3_noaudio.mp4')
    t0 = time.time()
    bpy.ops.render.render(animation=True)
    dt = time.time() - t0
    print(f'VIDEO {NF} frames in {dt:.1f}s = {dt / NF:.3f}s/frame')
