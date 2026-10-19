import sys, math, os; sys.path.insert(0, '/tmp/claude-0/vz')
from vzlib import *
import bpy
a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
WEIGHT = a[0] if a else '100.0'
OUT = a[1] if len(a) > 1 else '/tmp/claude-0/vz/out/scale.png'
s = reset(samples=int(os.environ.get('SPP', '48')))
s.render.resolution_percentage = int(os.environ.get('PCT', '100'))
world_hdri('modern_bathroom', strength=0.5, rot=1.2)
plane('floor', (6, 6), m=pbr('tiles', 'long_white_tiles', scale=1.0, tint=(0.75, 0.75, 0.75)), uv_scale=(9, 9))
CY = 0.10
wl = plane('wallt', (6, 2.4), loc=(0, 0.75, 1.2), m=pbr('wtiles', 'long_white_tiles', scale=1.0, tint=(0.9, 0.9, 0.88)), uv_scale=(9, 3.6)); wl.rotation_euler = (math.pi/2, 0, 0)

box('base', (0.32, 0.32, 0.02), (0, CY, 0.012), mat('base', (0.02, 0.02, 0.024), 0.3), bevel=0.025, segs=8)
box('glass', (0.322, 0.322, 0.008), (0, CY, 0.026), mat('glass', (0.9, 0.95, 1.0), 0.03, trans=1.0, ior=1.5), bevel=0.025, segs=8)
DY = CY + 0.115
box('lcd', (0.12, 0.05, 0.002), (0, DY, 0.0225), mat('lcd', (0.008, 0.01, 0.012), 0.15))
seg = '/tmp/claude-0/vz/fonts/fonts-DSEG_v046/DSEG7-Classic/DSEG7Classic-Bold.ttf'
glow = mat('digit', (0, 0, 0), 0.5, emit=(0.7, 0.9, 1.0), emit_s=8)
ghost = mat('ghost', (0.03, 0.04, 0.045), 0.4)
text('888.8', seg, 0.036, (-0.008, DY, 0.0236), (0, 0, 0), ghost)
text(WEIGHT.rjust(5, '!'), seg, 0.036, (-0.008, DY, 0.0238), (0, 0, 0), glow)
text('kg', seg if not os.path.exists('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf') else '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 0.012, (0.05, DY - 0.008, 0.0238), (0, 0, 0), glow)
sock = mat('sock', (0.035, 0.035, 0.04), 0.9)
f1 = foot(-0.075, CY - 0.03, 0.0, sock, -1, 1.0, 0.12)
f2 = foot(0.075, CY - 0.03, 0.0, sock, 1, 1.0, -0.12)
print('FEET', [m.name for m in f1.data.materials], [m.name for m in f2.data.materials])
# shins rising toward camera (go out of frame)
for x in (-0.085, 0.085):
    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=0.055, depth=0.7, location=(x, CY - 0.13, 0.45))
    o = bpy.context.object; o.rotation_euler = (math.radians(-6), 0, 0); bpy.ops.object.shade_smooth()
    o.data.materials.append(pbr('pants', 'jersey_melange', scale=6, tint=(0.35, 0.35, 0.4), coord='Object'))
# belly (t-shirt), fills the bottom of frame
bpy.ops.mesh.primitive_uv_sphere_add(segments=96, ring_count=48, radius=1, location=(0, -0.16, 1.12))
b = bpy.context.object; b.scale = (0.26, 0.17, 0.28); bpy.ops.object.shade_smooth()
tx = bpy.data.textures.new('wr', 'CLOUDS'); tx.noise_scale = 0.12
d = b.modifiers.new('d', 'DISPLACE'); d.texture = tx; d.strength = 0.018
b.data.materials.append(pbr('shirt', 'cotton_jersey', scale=5, tint=(0.10, 0.11, 0.14), coord='Object'))
bpy.ops.object.light_add(type='AREA', location=(-0.9, -0.3, 2.4)); L = bpy.context.object
L.data.energy = 80; L.data.size = 1.0; L.data.color = (1.0, 0.93, 0.85)
camera((0, -0.05, 1.60), (0, 0.36, 0), lens=40, dof=1.62, fstop=2.8)
render(OUT)
