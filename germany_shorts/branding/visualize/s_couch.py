import sys, math, os; sys.path.insert(0, '/tmp/claude-0/vz')
from vzlib import *
import bpy
a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
OUT = a[0] if a else '/tmp/claude-0/vz/out/couch.png'
s = reset(samples=int(os.environ.get('SPP', '64')))
s.render.resolution_percentage = int(os.environ.get('PCT', '100'))
world_color((0.01, 0.012, 0.02), 1.0)
plane('floor', (8, 8), m=pbr('lam', 'laminate_floor_02', tint=(0.7, 0.62, 0.55)), uv_scale=(4, 4))
wm = mat('wall', (0.22, 0.21, 0.2), 0.85)
w = plane('wallF', (8, 3), loc=(0, 3.4, 1.5), m=wm); w.rotation_euler = (math.pi/2, 0, 0)
w = plane('wallL', (8, 3), loc=(-2.4, 0, 1.5), m=wm); w.rotation_euler = (math.pi/2, 0, math.pi/2)
w = plane('wallR', (8, 3), loc=(2.6, 0, 1.5), m=wm); w.rotation_euler = (math.pi/2, 0, math.pi/2)
# TV on a low cabinet
box('cab', (1.8, 0.42, 0.45), (0, 3.15, 0.225), mat('cab', (0.06, 0.05, 0.045), 0.5), bevel=0.01)
box('tvb', (1.46, 0.04, 0.84), (0, 3.2, 1.0), mat('tvb', (0.01, 0.01, 0.01), 0.3), bevel=0.006)
scr = plane('screen', (1.42, 0.80), loc=(0, 3.165, 1.0)); scr.rotation_euler = (math.pi/2, 0, 0)
sm = bpy.data.materials.new('scr'); sm.use_nodes = True; n = sm.node_tree.nodes; n.clear()
t = n.new('ShaderNodeTexImage'); t.image = bpy.data.images.load('/tmp/claude-0/vz/out/tvshow.png')
e = n.new('ShaderNodeEmission'); e.inputs['Strength'].default_value = 2.2; o = n.new('ShaderNodeOutputMaterial')
sm.node_tree.links.new(t.outputs[0], e.inputs[0]); sm.node_tree.links.new(e.outputs[0], o.inputs[0])
scr.data.materials.append(sm)
# TV light spill
bpy.ops.object.light_add(type='AREA', location=(0, 3.05, 1.0)); L = bpy.context.object
L.rotation_euler = (-math.pi/2, 0, 0); L.visible_camera = False; L.data.shape = 'RECTANGLE'; L.data.size = 1.4; L.data.size_y = 0.8
L.data.energy = 220; L.data.color = (0.55, 0.7, 1.0)
# dim warm lamp far left
bpy.ops.object.light_add(type='POINT', location=(-2.0, 2.6, 1.3)); P = bpy.context.object
P.data.energy = 25; P.visible_camera = False; P.data.color = (1.0, 0.6, 0.3); P.data.shadow_soft_size = 0.15
# coffee table + junk
gltf('modern_coffee_table_01', loc=(0, 1.15, 0))
TZ = float(os.environ.get('TZ_TOP', '0.40'))
can = mat('can', (0.75, 0.75, 0.78), 0.25, metal=1.0)
red = mat('label', (0.55, 0.04, 0.04), 0.35, coat=1.0)
for i, (x, y, r) in enumerate([(-0.25, 1.05, 0), (-0.12, 1.18, 0), (0.32, 1.0, 1)]):
    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=0.033, depth=0.122, location=(x, y, TZ + 0.061))
    c = bpy.context.object; bpy.ops.object.shade_smooth(); c.data.materials.append(red)
    if r: c.rotation_euler = (math.pi/2, 0, 0.6); c.location.z = TZ + 0.033
# pizza box
box('pz', (0.4, 0.4, 0.045), (0.12, 1.25, TZ + 0.023), mat('card', (0.55, 0.42, 0.28), 0.9), bevel=0.003)
gltf('hamburger_buns', loc=(-0.05, 0.98, TZ), scale=1.0)
# phone face down
box('ph', (0.075, 0.155, 0.008), (0.35, 1.2, TZ + 0.004), mat('ph', (0.02, 0.02, 0.025), 0.2, coat=1.0), bevel=0.006)
# sofa under/behind camera: legs (sweatpants) stretching forward
pants = pbr('pants', 'jersey_melange', scale=5, tint=(0.22, 0.23, 0.26), coord='Object')
for x in (-0.12, 0.12):
    sg = 1 if x > 0 else -1
    pts = [(-0.2, 0.60, 0.105), (0.05, 0.61, 0.095), (0.25, 0.605, 0.08), (0.40, 0.595, 0.068),
           (0.60, 0.55, 0.064), (0.80, 0.505, 0.05), (0.93, 0.48, 0.043)]
    leg = tube('leg', [(x + sg * 0.01 * (y > 0.3), y, z, r) for (y, z, r) in pts], pants)
    tx = bpy.data.textures.new('wr', 'CLOUDS'); tx.noise_scale = 0.05
    d = leg.modifiers.new('d', 'DISPLACE'); d.texture = tx; d.strength = 0.006
    f = foot(x + sg * 0.012, 0.99, 0.53, mat('sock', (0.05, 0.05, 0.055), 0.95), sg, 1.0, -0.2 * sg, math.radians(62))
# belly bottom edge
bpy.ops.mesh.primitive_uv_sphere_add(segments=96, ring_count=48, radius=1, location=(0, -0.36, 0.70))
b = bpy.context.object; b.scale = (0.3, 0.22, 0.26); bpy.ops.object.shade_smooth()
b.data.materials.append(pbr('shirt', 'cotton_jersey', scale=5, tint=(0.12, 0.13, 0.16), coord='Object'))
camera((0.0, -0.30, 1.12), (0.0, 2.5, 0.42), lens=22, dof=2.5, fstop=2.0)
exec(open("/tmp/claude-0/vz/dbg.py").read()) if os.environ.get("DBG") else render(OUT)
