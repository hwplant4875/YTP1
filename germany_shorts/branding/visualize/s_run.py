import sys, math, os; sys.path.insert(0, '/tmp/claude-0/vz')
from vzlib import *
import bpy
a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
OUT = a[0] if a else '/tmp/claude-0/vz/out/run.png'
ROT = float(a[1]) if len(a) > 1 else 0.0
s = reset(samples=int(os.environ.get('SPP', '48')))
s.render.resolution_percentage = int(os.environ.get('PCT', '100'))
world_hdri('bell_park_dawn', strength=1.0, rot=ROT)

def fade(m, r0=30, r1=55):
    nt = m.node_tree; n = nt.nodes; L = nt.links.new
    out = n['Material Output']; b = n['Principled BSDF']
    geo = n.new('ShaderNodeNewGeometry'); sep = n.new('ShaderNodeSeparateXYZ')
    L(geo.outputs['Position'], sep.inputs[0])
    cmb = n.new('ShaderNodeCombineXYZ'); L(sep.outputs['X'], cmb.inputs['X']); L(sep.outputs['Y'], cmb.inputs['Y'])
    ln = n.new('ShaderNodeVectorMath'); ln.operation = 'LENGTH'; L(cmb.outputs[0], ln.inputs[0])
    mr = n.new('ShaderNodeMapRange'); mr.inputs['From Min'].default_value = r0; mr.inputs['From Max'].default_value = r1
    mr.interpolation_type = 'SMOOTHSTEP'; L(ln.outputs['Value'], mr.inputs['Value'])
    tr = n.new('ShaderNodeBsdfTransparent'); mx = n.new('ShaderNodeMixShader')
    L(mr.outputs['Result'], mx.inputs[0]); L(b.outputs[0], mx.inputs[1]); L(tr.outputs[0], mx.inputs[2])
    L(mx.outputs[0], out.inputs['Surface'])
    return m

def xfade(m, x0, x1):
    nt = m.node_tree; n = nt.nodes; L = nt.links.new
    mx = [x for x in n if x.type == 'MIX_SHADER'][0]
    geo = n.new('ShaderNodeNewGeometry'); sep = n.new('ShaderNodeSeparateXYZ'); L(geo.outputs['Position'], sep.inputs[0])
    mr = n.new('ShaderNodeMapRange'); mr.inputs['From Min'].default_value = x0; mr.inputs['From Max'].default_value = x1
    mr.interpolation_type = 'SMOOTHSTEP'; L(sep.outputs['X'], mr.inputs['Value'])
    old = mx.inputs[0].links[0].from_socket
    mm = n.new('ShaderNodeMath'); mm.operation = 'MAXIMUM'; L(old, mm.inputs[0]); L(mr.outputs['Result'], mm.inputs[1])
    L(mm.outputs[0], mx.inputs[0]); return m
gm = lambda: pbr('grassm', 'leafy_grass', tint=(0.85, 0.85, 0.75))
gl = plane('grassL', (60, 140), loc=(-31.3, 40, -0.01), m=fade(gm(), 45, 100), uv_scale=(30, 70))
gr = plane('grassR', (8, 140), loc=(5.3, 40, -0.01), m=xfade(fade(gm()), 5.5, 9.0), uv_scale=(4, 70))
p = plane('path', (2.6, 140), loc=(0, 40, 0.0), m=fade(pbr('asph', 'asphalt_02', tint=(0.8, 0.8, 0.8))), uv_scale=(1.3, 70))
for x in (-1.32, 1.32):
    plane('edge', (0.08, 140), loc=(x, 40, 0.004), m=fade(mat('edge', (0.55, 0.55, 0.52), 0.8)))
for y in [6, 30, 54]:
    gltf('street_lamp_01', loc=(-1.9, y, 0))
gltf('modular_street_seating', loc=(2.4, 16, 0), rot=(0, 0, math.pi / 2))
tuft = gltf('grass_medium_01')[0]; tuft.location = (0, -50, -5)
for g, cnt in ((gl, 40000), (gr, 7000)):
    ps = g.modifiers.new('ps', 'PARTICLE_SYSTEM').particle_system.settings
    ps.type = 'HAIR'; ps.count = cnt; ps.use_advanced_hair = True; ps.render_type = 'OBJECT'
    ps.instance_object = tuft; ps.particle_size = 2.2; ps.size_random = 0.6; ps.use_rotations = True
    ps.rotation_mode = 'GLOB_Z'; ps.phase_factor_random = 2.0; ps.hair_length = 1
camera((0.25, -0.5, 1.68), (0.1, 30, 1.2), lens=22)
s.render.use_motion_blur = False
render(OUT)
