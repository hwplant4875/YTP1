# PEEK. Paris Catacombs: first-half Blender shots.
# usage: blender -b -P shots.py -- SHOT OUT_DIR [--preview] [--frames 0,60,120]
import bpy, sys, os, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cat_lib import *

# shot: (start s, end s) on the narration timeline; each shot renders 0.5 s extra for the dissolve
SHOTS = {
    'SH01_street':       (0.0, 8.4),
    'SH02_tunnel_sign':  (8.4, 13.9),
    'SH03_cinema':       (13.9, 27.5),
    'SH04_screen':       (27.5, 30.2),
    'SH05_cinema_dark':  (30.2, 40.9),
    'SH06_descent':      (40.9, 47.6),
    'SH07_stone':        (47.6, 52.9),
    'SH08_sea':          (52.9, 61.9),
    'SH09_shaft':        (61.9, 69.2),
    'SH10_roots':        (73.7, 85.3),
    'SH11_collapse':     (85.3, 100.7),
    'SH12_pillars':      (100.7, 109.2),
}


def nframes(name):
    a, b = SHOTS[name]
    return int(math.ceil((b - a + 0.5) * FPS))


R = random.Random(7)
def init_mats():
    global CREAM, LIME, DARKROCK, ASPHALT, WIN_ON, WIN_OFF, ROOF, IRON
    CREAM = ph_mat('cream', 'beige_wall_001', 0.25, (1.0, 0.93, 0.8))
    LIME = ph_mat('lime', 'clay_plaster', 0.45, (1.35, 1.28, 1.1), 1.4)
    DARKROCK = stone('darkrock', (0.18, 0.15, 0.12), (0.36, 0.31, 0.25), 1.0, 0.6, 0.9)
    ASPHALT = ph_mat('road', 'cobblestone_01', 0.55, (0.55, 0.55, 0.6), 1.0, 0.55)
    WIN_ON = emit_mat('win_on', (1.0, 0.55, 0.22), 1.6)
    WIN_OFF = mat('win_off', (0.03, 0.04, 0.06), 0.15, 0.3)
    ROOF = mat('roof', (0.16, 0.18, 0.22), 0.5, 0.4)
    IRON = mat('iron', (0.05, 0.05, 0.05), 0.45, 0.9)


# ---------------------------------------------------------------- city pieces
def haussmann(x, y, w, d, floors, face=1, lit=0.45, rng=R):
    """one Paris block: cream stone body, balcony line, slate mansard, window grid on the street face"""
    h = floors * 3.2
    body = box((x, y, h / 2), (w, d, h), CREAM, 'block', 0.05)
    box((x, y, h + 1.2), (w - 0.6, d - 1.6, 2.4), ROOF, 'mansard', 0.4)
    box((x, y + face * (d / 2 + 0.25), 3.2 * 2 + 0.05), (w, 0.5, 0.15), IRON, 'balcony')
    cols = max(2, int(w / 2.4))
    fy = y + face * (d / 2 + 0.02)
    for f in range(1, floors):
        for c in range(cols):
            wx = x - w / 2 + (c + 0.5) * w / cols
            m = WIN_ON if rng.random() < lit else WIN_OFF
            plane((wx, fy, f * 3.2 + 1.2), (1.1, 2.0), m, rot=(math.pi / 2, 0, 0), name='win')
    return body


def street_lamp(x, y):
    cyl((x, y, 2.5), 0.08, 5, IRON)
    sphere((x, y, 5.1), 0.25, emit_mat('lamp', (1, 0.75, 0.45), 8))
    point((x, y, 4.8), 900, (1, 0.72, 0.42), 0.3)


def eiffel(x, y, scale=1.0):
    gold = emit_mat('eiffel', (1.0, 0.55, 0.18), 2.2)
    segs = [(0, 34, 24, 9.5, 0.55), (34, 40, 9.5, 4.2, 0.4), (74, 52, 4.2, 0.6, 0.3)]
    for z0, h, r1, r2, th in segs:
        t = cyl((x, y, (z0 + h / 2) * scale), r1 * scale, h * scale, gold, verts=4, r2=r2 * scale, name='eiffel')
        t.rotation_euler[2] = math.radians(45)
        bpy.ops.object.select_all(action='DESELECT'); t.select_set(True); bpy.context.view_layer.objects.active = t
        bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.subdivide(number_cuts=7); bpy.ops.object.mode_set(mode='OBJECT')
        wf = t.modifiers.new('wf', 'WIREFRAME'); wf.thickness = th * scale
    for z, r in [(34, 11), (74, 5)]:
        box((x, y, z * scale), (r * 2 * scale, r * 2 * scale, 1.2 * scale), gold, 'deck')
    sphere((x, y, 127 * scale), 1.0 * scale, emit_mat('beacon', (1, 0.9, 0.7), 30))


# ---------------------------------------------------------------- SH01 street
def sh_street(n):
    world_color((0.006, 0.012, 0.03), 1.0)
    plane((0, 60, 0), (14, 200), ASPHALT, name='road')
    box((-9, 60, 0.1), (4, 200, 0.2), stone('pave', (0.2, 0.19, 0.18), (0.32, 0.3, 0.28), 6, 0.3), 'sidewalkL')
    box((9, 60, 0.1), (4, 200, 0.2), stone('pave', (0.2, 0.19, 0.18), (0.32, 0.3, 0.28), 6, 0.3), 'sidewalkR')
    # blocks face the street: rotate by building them along y with the face toward x
    for side in (-1, 1):
        yy = -12
        while yy < 160:
            w = R.uniform(11, 17); floors = R.choice([6, 6, 7])
            h = floors * 3.2; x = side * 17
            box((x, yy + w / 2, h / 2), (12, w - 0.3, h), CREAM, 'block', 0.05)
            box((x, yy + w / 2, h + 1.2), (10.4, w - 0.9, 2.4), ROOF, 'mansard', 0.4)
            fx = x - side * 6.02
            box((x - side * 6.2, yy + w / 2, 6.45), (0.4, w - 0.3, 0.15), IRON, 'balcony')
            cols = max(3, int(w / 2.6))
            for f in range(1, floors):
                for c in range(cols):
                    wy = yy + (c + 0.5) * w / cols
                    m = WIN_ON if R.random() < 0.42 else WIN_OFF
                    plane((fx, wy, f * 3.2 + 1.3), (1.1, 2.0), m, rot=(math.pi / 2, 0, math.pi / 2), name='win')
            yy += w
    for yl in range(0, 150, 18):
        street_lamp(-7.6, yl); street_lamp(7.6, yl + 9)
    eiffel(6, 420, 1.3)
    # the open manhole with light coming up
    # open manhole: a stone shaft with iron rungs, warm light rising from below
    road = bpy.data.objects['road']
    cut = cyl((1.2, 6, 0), 0.7, 3, None, verts=32, name='holecut'); cut.hide_render = True; cut.display_type = 'WIRE'
    bm = road.modifiers.new('hole', 'BOOLEAN'); bm.object = cut; bm.operation = 'DIFFERENCE'
    sh = cyl((1.2, 6, -3), 0.72, 6, LIME, verts=32, name='shaft')
    sh.data.polygons.foreach_set('use_smooth', [True] * len(sh.data.polygons))
    bpy.ops.object.select_all(action='DESELECT'); sh.select_set(True); bpy.context.view_layer.objects.active = sh
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.flip_normals(); bpy.ops.object.mode_set(mode='OBJECT')
    sh.data.materials[0].use_backface_culling = False
    bpy.ops.mesh.primitive_torus_add(location=(1.2, 6, 0.03), major_radius=0.76, minor_radius=0.06); bpy.context.object.data.materials.append(IRON)
    for k in range(8):
        cyl((1.2, 6.62, -0.4 - k * 0.45), 0.025, 0.5, IRON, rot=(0, math.pi / 2, 0))
    cov = cyl((2.55, 5.0, 0.05), 0.78, 0.07, IRON, verts=32, name='cover')
    cov.rotation_euler = (0, math.radians(4), 0)
    point((1.2, 6, -2.0), 600, (1, 0.6, 0.3), 0.3)
    point((1.2, 6, -4.5), 900, (1, 0.6, 0.3), 0.3)
    fog((40, 220, 30), (0, 80, 14), 0.006, (0.8, 0.85, 1.0))
    sun((math.radians(60), 0, math.radians(30)), 0.35, (0.55, 0.65, 1.0))
    area((0, 40, 40), 4000, 60, (0.6, 0.7, 1.0), rot=(0, 0, 0))
    camera([(0, (-1.5, -14, 7.5)), (n - 1, (0.6, 3.4, 3.4))],
           lens=30, target_keys=[(0, (1.5, 60, 9)), (n - 1, (1.2, 6.0, -1.5))])


# ---------------------------------------------------------------- tunnels
def tunnel(length, y0=0, width=2.4, height=2.6, m=None, name='tunnel'):
    m = m or LIME
    floor = box((0, y0 + length / 2, -0.1), (width + 0.6, length, 0.2), ph_mat('gravel', 'gravel_floor', 0.6, (0.9, 0.85, 0.78)), 'floor')
    wl = rocky(box((-width / 2 - 0.3, y0 + length / 2, height / 2), (0.6, length, height + 0.4), m, 'wallL'), 0.18, 1.2, 3)
    wr = rocky(box((width / 2 + 0.3, y0 + length / 2, height / 2), (0.6, length, height + 0.4), m, 'wallR'), 0.18, 1.2, 3)
    ce = rocky(box((0, y0 + length / 2, height + 0.3), (width + 1.4, length, 0.6), m, 'ceil'), 0.15, 1.2, 3)
    return floor


def sh_tunnel_sign(n):
    world_color((0, 0, 0), 0)
    tunnel(30, -2)
    # tarp across the tunnel with the sign
    tarp = plane((0, 20, 1.3), (2.6, 2.7), mat('tarp', (0.55, 0.12, 0.05), 0.7), rot=(math.pi / 2, 0, 0), name='tarp')
    s = tarp.modifiers.new('sub', 'SUBSURF'); s.levels = s.render_levels = 4; s.subdivision_type = 'SIMPLE'
    wv = tarp.modifiers.new('wave', 'WAVE'); wv.height = 0.05; wv.width = 0.8; wv.speed = 0.02; wv.use_normal = True
    white = mat('signwhite', (0.9, 0.88, 0.82), 0.6)
    text3d('CHANTIER', (0, 19.9, 1.75), 0.42, white)
    text3d('ACCES INTERDIT', (0, 19.9, 1.15), 0.3, white)
    box((0, 19.95, 1.45), (1.9, 0.02, 0.04), white, 'line')
    # flashlight on the camera + a faint warm glow leaking from behind the tarp
    c = camera([(0, (0.2, 2, 1.55)), (n - 1, (0, 15.2, 1.45))], lens=28,
               target_keys=[(0, (0, 20, 1.4)), (n - 1, (0, 20, 1.45))], shake=0.015)
    fl = spot((0, 0, 0), 220, (1, 0.93, 0.8), 45, 0.5); fl.parent = c; fl.location = (0.25, 0.1, 0)
    point((0, 21.5, 1.0), 300, (1, 0.55, 0.25), 0.5)
    point((0, 21.5, 2.4), 120, (1, 0.55, 0.25), 0.5)
    fog((4, 30, 4), (0, 13, 1.3), 0.004)


# ---------------------------------------------------------------- the cinema cave
def cinema(dark=False):
    world_color((0, 0, 0), 0)
    rock = ph_mat('caverock', 'rock_wall_02', 0.35, (1.45, 1.3, 1.05), 1.3)
    W, D, H = 18, 22, 6.5
    rocky(box((0, 0, -0.25), (W + 2, D + 2, 0.5), rock, 'floor'), 0.05, 2, 3)
    rocky(box((-W / 2 - 0.5, 0, H / 2), (1, D, H + 1), rock, 'wL'), 0.5, 1.4, 4)
    rocky(box((W / 2 + 0.5, 0, H / 2), (1, D, H + 1), rock, 'wR'), 0.5, 1.4, 4)
    rocky(box((0, D / 2 + 0.5, H / 2), (W + 2, 1, H + 1), rock, 'wB'), 0.4, 1.4, 4)
    rocky(box((0, -D / 2 - 0.5, H / 2), (W + 2, 1, H + 1), rock, 'wF'), 0.4, 1.4, 4)
    rocky(box((0, 0, H + 0.4), (W + 2, D + 2, 0.8), rock, 'roof'), 0.5, 1.2, 4)
    # pillars left by the quarrymen
    for px, py in [(-5, -2), (5, -2), (-5, 5), (5, 5)]:
        rocky(box((px, py, H / 2), (1.2, 1.2, H), rock, 'pillar'), 0.12, 2, 3)
    # terraced seats carved into the rock, facing the screen at +y
    for i in range(5):
        y = -8 + i * 1.6; z = i * 0.45
        rocky(box((0, y - 0.6, z / 2), (12, 2.0, z + 0.45), rock, 'tier'), 0.05, 3, 2)
        box((0, y - 0.2, z + 0.5), (11, 0.7, 0.12), mat('cushion', (0.35, 0.08, 0.07), 0.8), 'cushion')
    # screen
    scr_m = emit_mat('screen_on' if not dark else 'screen_off', (0.75, 0.78, 0.82) if not dark else (0.02, 0.02, 0.02),
                     1.1 if not dark else 0.0)
    scr = plane((0, D / 2 - 0.2, 3.2), (8, 4.5), scr_m, rot=(math.pi / 2, 0, 0), name='screen')
    if not dark and 'grain' not in scr_m.name:
        nt = scr_m.node_tree; e = [x for x in nt.nodes if x.type == 'EMISSION'][0]
        tc = nt.nodes.new('ShaderNodeTexCoord'); g = nt.nodes.new('ShaderNodeTexGradient'); g.gradient_type = 'SPHERICAL'
        mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (0.9, 1.4, 1)
        nt.links.new(tc.outputs['Generated'], mp.inputs['Vector']); mp.inputs['Location'].default_value = (0.05, -0.2, 0)
        nt.links.new(mp.outputs['Vector'], g.inputs['Vector'])
        ramp = nt.nodes.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].color = (0.05, 0.05, 0.05, 1); ramp.color_ramp.elements[1].color = (0.8, 0.8, 0.82, 1)
        nt.links.new(g.outputs['Fac'], ramp.inputs['Fac']); nt.links.new(ramp.outputs['Color'], e.inputs['Color'])
        scr_m.name = 'screen_on_grain'
    box((0, D / 2 - 0.15, 3.2), (8.4, 0.05, 4.9), mat('frame', (0.02, 0.02, 0.02), 0.6), 'scrframe')
    # projector on a stand behind the seats (gone in the dark version)
    if not dark:
        box((0, -9.6, 2.9), (0.6, 0.9, 0.5), mat('proj', (0.15, 0.15, 0.17), 0.4, 0.6), 'projector')
        cyl((0, -9.1, 2.95), 0.12, 0.3, IRON, rot=(math.pi / 2, 0, 0))
        cyl((0, -9.6, 1.3), 0.06, 2.8, IRON)
    # the bar on the left
    wood = ph_mat('wood', 'dark_wooden_planks', 0.6)
    box((-7.4, -4, 0.55), (1.2, 5, 1.1), wood, 'bar', 0.03)
    box((-8.7, -4, 1.8), (0.4, 5, 0.06), wood, 'shelf')
    cols = [(0.1, 0.35, 0.08), (0.45, 0.2, 0.05), (0.6, 0.55, 0.3), (0.12, 0.12, 0.3)]
    for i in range(14):
        cyl((-8.7, -6.2 + i * 0.32, 2.0), 0.07, 0.36, mat(f'bottle{i % 4}', cols[i % 4], 0.08, 0, cols[i % 4], 0.6 if not dark else 0))
    # string lights along the walls
    if not dark:
        bulb = emit_mat('bulb', (1, 0.68, 0.35), 25)
        for side in (-1, 1):
            for i in range(16):
                t = i / 15; y = -D / 2 + 1 + t * (D - 2); z = H - 0.6 - 0.5 * math.sin(t * math.pi * 3) ** 2
                sphere((side * (W / 2 - 0.4), y, z), 0.07, bulb, 8)
            point((side * (W / 2 - 1), 0, H - 1), 500, (1, 0.65, 0.35), 2)
        point((-7.5, -4, 2.6), 300, (1, 0.6, 0.3), 0.5)
        area((0, D / 2 - 1.5, 3.2), 900, 7, (0.8, 0.85, 1.0), rot=(math.radians(90), 0, 0))
        fog((W, D, H), (0, 0, H / 2), 0.01)
    # cables along the floor
    for i in range(3):
        bpy.ops.curve.primitive_bezier_curve_add(location=(0, 0, 0))
        cu = bpy.context.object; cu.data.bevel_depth = 0.025
        pts = cu.data.splines[0].bezier_points
        pts[0].co = (-8.6 + i * 0.2, -8, 0.02); pts[1].co = (-3 + i, 9, 0.02)
        pts[0].handle_right = (-6, -2, 0.02); pts[1].handle_left = (-6, 6, 0.02)
        cu.data.materials.append(mat('cable', (0.01, 0.01, 0.01), 0.4))
    return D, H


def sh_cinema(n):
    D, H = cinema(False)
    camera([(0, (2.5, -10.6, 1.6)), (int(n * 0.45), (1.0, -6.5, 3.6)), (n - 1, (-1.5, 1.5, 2.6))], lens=22,
           target_keys=[(0, (0, 10, 2.8)), (int(n * 0.45), (0, 10, 2.8)), (n - 1, (-7.5, -4.5, 1.2))])


def sh_screen(n):
    D, H = cinema(False)
    camera([(0, (0, 2.5, 2.6)), (n - 1, (0, 4.0, 2.9))], lens=32, target_keys=[(0, (0, D / 2, 3.2))])


def sh_cinema_dark(n):
    D, H = cinema(True)
    paper = mat('paper', (0.85, 0.82, 0.74), 0.8)
    note = plane((0.8, 6.2, 0.03), (0.42, 0.3), paper, rot=(0, 0, math.radians(14)), name='note')
    ink = mat('ink', (0.02, 0.02, 0.03), 0.6)
    t = text3d('Ne cherchez pas\na nous trouver', (0.8, 6.2, 0.04), 0.05, ink, rot=(0, 0, math.radians(14)), font=hand_font())
    c = camera([(0, (2.0, -10.4, 2.0)), (int(n * 0.5), (0.6, -0.5, 1.9)), (n - 1, (0.75, 5.3, 0.95))], lens=26,
               target_keys=[(0, (0, 10, 2.5)), (int(n * 0.45), (0, 10, 2.2)), (n - 1, (0.8, 6.2, 0.03))], shake=0.012)
    fl = spot((0, 0, 0), 350, (1, 0.93, 0.8), 40, 0.45); fl.parent = c; fl.location = (0.25, 0.1, 0)
    fog((18, 22, 6.5), (0, 0, 3.25), 0.006)


# ---------------------------------------------------------------- cross-section diorama
LAYERS = [  # (top z, bottom z, c1, c2)
    (0.0, -2.0, (0.30, 0.22, 0.15), (0.42, 0.32, 0.22)),     # soil
    (-2.0, -5.5, (0.55, 0.50, 0.40), (0.70, 0.65, 0.55)),    # marl
    (-5.5, -13.0, (0.72, 0.66, 0.52), (0.86, 0.80, 0.66)),   # Lutetian limestone (quarried)
    (-13.0, -18.0, (0.45, 0.42, 0.38), (0.58, 0.55, 0.50)),  # clay / sand
]
GAL_Z = -9.2


def diorama(galleries=True, house_void=False, roots_growth=None, pillars=None, glow_lime=None, n=1):
    world_color((0.008, 0.01, 0.016), 1.0)
    W, D = 60, 22
    lime_obj = None
    for i, (zt, zb, c1, c2) in enumerate(LAYERS):
        o = box((0, 0, (zt + zb) / 2), (W, D, zt - zb), stone(f'layer{i}', c1, c2, 0.8, 0.25), f'layer{i}', 0.0)
        if i == 2: lime_obj = o
    # galleries cut into the limestone: boolean cutters
    cutters = []
    if galleries:
        rng = random.Random(3)
        segs = []
        for k in range(9):
            x = -26 + k * 6.2 + rng.uniform(-1, 1)
            segs.append(((x, 0), (0.0, 1.0)))  # along y (into the depth)
        for k in range(5):
            segs.append(((rng.uniform(-24, 24), rng.uniform(-8, 6)), (1.0, 0.0)))  # along x
        for idx, ((x, y), (dx, dy)) in enumerate(segs):
            L = 26 if dy else rng.uniform(10, 22)
            cut = box((x if dy else x, y if dx else 0, GAL_Z), ((L if dx else 2.2), (L if dy else 2.2), 2.6), None, f'cut{idx}')
            cut.display_type = 'WIRE'; cut.hide_render = True
            cutters.append(cut)
            if roots_growth is not None:
                a, b = roots_growth
                f0 = a + int((b - a) * idx / len(segs))
                key(cut, 'scale', [(0, (0.001, 0.001, 0.001)), (f0, (0.001, 0.001, 0.001)), (f0 + 30, (1, 1, 1))])
        for cut in cutters:
            m = lime_obj.modifiers.new('bool', 'BOOLEAN'); m.object = cut; m.operation = 'DIFFERENCE'
            for sv in ('FLOAT', 'FAST'):
                try: m.solver = sv; break
                except Exception: pass
        # warm lamps inside the galleries at the cut face
        for k in range(6):
            point((-25 + k * 10, -D / 2 + 0.8, GAL_Z), 30, (1, 0.6, 0.3), 0.3)
    if house_void:
        cut = box((0, -D / 2 + 4, -7.5), (9, 8, 9), None, 'void'); cut.hide_render = True; cut.display_type = 'WIRE'
        for o in [bpy.data.objects[f'layer{i}'] for i in (1, 2)]:
            m = o.modifiers.new('void', 'BOOLEAN'); m.object = cut; m.operation = 'DIFFERENCE'
    # the city on top
    cityblocks(W, D)
    if glow_lime:
        m = lime_obj.data.materials[0]; p = m.node_tree.nodes['Principled BSDF']
        p.inputs['Emission Color'].default_value = (1, 0.8, 0.45, 1)
        key_input(p.inputs['Emission Strength'], [(0, 0.0), (glow_lime[0], 0.0), (glow_lime[1], 0.6)])
    if pillars:
        a, b = pillars
        rng = random.Random(9)
        for k in range(14):
            x = -26 + (k % 7) * 8.4 + rng.uniform(-0.6, 0.6); y = -D / 2 + 1.2 + (k // 7) * 2.6
            p = box((x, y, GAL_Z), (0.9, 0.9, 2.6), stone('pillarstone', (0.62, 0.58, 0.5), (0.8, 0.75, 0.66), 3, 0.3), 'pillar')
            f0 = a + int((b - a) * k / 14)
            key(p, 'scale', [(0, (1, 1, 0.001)), (f0, (1, 1, 0.001)), (f0 + 10, (1, 1, 1))])
    sun((math.radians(50), math.radians(10), math.radians(-35)), 2.2, (1, 0.93, 0.85))
    area((0, -40, 5), 4000, 30, (0.85, 0.9, 1.0), rot=(math.radians(90), 0, 0))
    return W, D


def cityblocks(W, D):
    rng = random.Random(5)
    street = mat('street', (0.08, 0.08, 0.09), 0.5)
    box((0, 0, 0.02), (W, D, 0.04), street, 'streets')
    tree = mat('tree', (0.08, 0.2, 0.08), 0.8)
    x = -W / 2 + 1
    while x < W / 2 - 3:
        bw = rng.uniform(4, 7)
        for y in (-D / 2 + 3.2, 3.5):
            h = rng.uniform(5.5, 7.5); d = 5.5
            box((x + bw / 2, y, h / 2), (bw - 0.3, d, h), CREAM, 'cblock', 0.03)
            box((x + bw / 2, y, h + 0.6), (bw - 0.8, d - 0.8, 1.2), ROOF, 'croof', 0.25)
            for f in range(1, int(h / 1.3)):
                for c in range(int(bw / 1.1)):
                    if y < 0:
                        plane((x + 0.6 + c * 1.1, y - d / 2 - 0.01, f * 1.25), (0.45, 0.8),
                              WIN_ON if rng.random() < 0.3 else WIN_OFF, rot=(math.pi / 2, 0, 0), name='cwin')
        if rng.random() < 0.6:
            sphere((x + bw / 2, -1.5, 1.6), 0.9, tree, 10); cyl((x + bw / 2, -1.5, 0.5), 0.1, 1, wood_m())
        x += bw


def wood_m():
    return mat('wood', (0.25, 0.13, 0.06), 0.5)


def sh_descent(n):
    W, D = diorama()
    camera([(0, (22, -62, 34)), (int(n * 0.4), (10, -48, 12)), (n - 1, (2, -28, GAL_Z + 0.6))], lens=30,
           target_keys=[(0, (0, 0, -3)), (int(n * 0.4), (0, 0, -6)), (n - 1, (0, 0, GAL_Z))])


def sh_stone(n):
    W, D = diorama(glow_lime=(10, 50))
    camera([(0, (-10, -58, 4)), (n - 1, (-6, -52, 2))], lens=35, target_keys=[(0, (0, 0, -5)), (n - 1, (0, 0, -6))])


def sh_roots(n):
    W, D = diorama(roots_growth=(10, int(n * 0.7)))
    # lights fade at the end: the city forgets
    camera([(0, (14, -46, 14)), (n - 1, (-12, -44, 8))], lens=35, target_keys=[(0, (0, 0, -6)), (n - 1, (0, 0, -7))])


def sh_pillars(n):
    W, D = diorama(pillars=(12, int(n * 0.75)))
    camera([(0, (-8, -30, GAL_Z + 1)), (n - 1, (8, -30, GAL_Z + 1.5))], lens=28,
           target_keys=[(0, (-4, 0, GAL_Z)), (n - 1, (4, 0, GAL_Z))])


def sh_collapse(n):
    W, D = diorama(galleries=False, house_void=True)
    # the house on Rue d'Enfer above the void, with its ground plug
    plug = box((0, -D / 2 + 4, -0.6), (6.5, 6, 1.2), stone('plug', (0.3, 0.22, 0.15), (0.42, 0.32, 0.22), 0.8, 0.25), 'plug')
    house = box((0, -D / 2 + 4, 4), (5.5, 5, 8), CREAM, 'house', 0.05)
    roof = box((0, -D / 2 + 4, 8.6), (4.8, 4.4, 1.2), ROOF, 'hroof', 0.2)
    for o in (house, roof):
        o.parent = plug; o.matrix_parent_inverse = plug.matrix_world.inverted()
    # existing block over the void is removed from the city: hide anything under the house footprint
    for o in list(bpy.data.objects):
        if o.name.startswith(('cblock', 'croof', 'cwin')) and abs(o.location.x) < 4.5 and o.location.y < 0:
            bpy.data.objects.remove(o, do_unlink=True)
    f0 = int(n * 0.18); f1 = f0 + 30
    key(plug, 'location', [(0, plug.location.copy()), (f0, plug.location.copy()),
                           (f1, plug.location + __import__('mathutils').Vector((0, 0, -7.5)))])
    key(plug, 'rotation_euler', [(f0, (0, 0, 0)), (f1, (math.radians(9), math.radians(-6), 0))])
    rng = random.Random(4)
    for k in range(24):
        d = box((rng.uniform(-3, 3), -D / 2 + 4 + rng.uniform(-2.5, 2.5), rng.uniform(-0.8, 0.2)), (0.35, 0.35, 0.35),
                stone('plug', (0.3, 0.22, 0.15), (0.42, 0.32, 0.22), 0.8, 0.25), 'debris')
        ds = rng.uniform(0.0, 0.25)
        key(d, 'location', [(f0, d.location.copy()), (int(f0 + 6 + ds * 30), d.location + __import__('mathutils').Vector((rng.uniform(-1, 1), 0, -8.5)))])
    camera([(0, (10, -30, 6)), (f0, (9, -29, 5)), (f1 + 10, (7, -27, 0)), (n - 1, (16, -46, 6))], lens=32,
           target_keys=[(0, (0, -7, 1)), (f0, (0, -7, 0)), (f1 + 10, (0, -7, -5)), (n - 1, (0, 0, -6))], shake=0.0)
    camshake = bpy.context.scene.camera
    for fc in _fcurves(camshake.animation_data.action):
        mod = fc.modifiers.new('NOISE'); mod.scale = 3; mod.strength = 0.25
        mod.use_restricted_range = True; mod.frame_start = f0; mod.frame_end = f1 + 8; mod.blend_in = 4; mod.blend_out = 8


# ---------------------------------------------------------------- SH08 ancient sea
def sh_sea(n):
    world_color((0.02, 0.12, 0.16), 1.0)
    floor = plane((0, 0, 0), (80, 80), ph_mat('seabed', 'coast_sand_01', 0.3, (1.2, 1.15, 1.0)))
    rocky(floor, 0.4, 3, 5)
    surf = plane((0, 0, 9), (120, 120), mat('water', (0.1, 0.5, 0.55), 0.05, 0, None, 0, 0.35), name='surface')
    rocky(surf, 0.4, 2, 4)
    sun((math.radians(15), 0, 0), 4.5, (0.75, 1.0, 0.95))
    fog((80, 80, 10), (0, 0, 4.5), 0.05, (0.4, 0.9, 0.9))
    shell = mat('shell', (0.9, 0.85, 0.75), 0.4)
    rng = random.Random(11)
    for k in range(160):
        x, y = rng.uniform(-14, 14), rng.uniform(-6, 24)
        s = cyl((x, y, 0.15), rng.uniform(0.12, 0.35), 0.08, shell, rot=(rng.uniform(-0.3, 0.3), rng.uniform(-0.3, 0.3), rng.uniform(0, 6)), verts=12, r2=0.02)
        if k < 70:
            z0 = rng.uniform(6, 12); f0 = rng.randint(0, n - 40)
            key(s, 'location', [(0, (x, y, z0)), (f0, (x, y, z0)), (min(n - 1, f0 + 60), (x, y, 0.15))])
    camera([(0, (0, -10, 2.2)), (n - 1, (0, -4, 1.6))], lens=26, target_keys=[(0, (0, 10, 1.2)), (n - 1, (0, 10, 0.6))])


# ---------------------------------------------------------------- SH09 quarry shaft
def sh_shaft(n):
    world_color((0, 0, 0), 0)
    tunnel(16, -6)
    # vertical shaft up to daylight at y=4
    for dx, dy in [(-1.6, 0), (1.6, 0), (0, -1.6), (0, 1.6)]:
        rocky(box((dx, 4 + dy, 9), (0.4 if dx else 3.6, 0.4 if dy else 3.6, 14), LIME, 'shaftwall'), 0.12, 1.5, 3)
    sky = plane((0, 4, 16.2), (4, 4), emit_mat('sky', (1, 0.97, 0.9), 25), name='sky')
    area((0, 4, 15.5), 9000, 3, (1, 0.96, 0.88), rot=(math.pi, 0, 0))
    point((0.8, 0.5, 2.2), 180, (1, 0.6, 0.3), 0.3)
    fog((3.2, 3.2, 14), (0, 4, 9), 0.05)
    # stone blocks cut from the wall + one hauled up on a rope
    blk = stone('block', (0.66, 0.6, 0.48), (0.82, 0.76, 0.62), 2.5, 0.2)
    for i in range(4):
        box((-0.9 + (i % 2) * 0.95, 7.2 + (i // 2) * 0.1, 0.45 + (i // 2) * 0.9), (0.9, 0.9, 0.85), blk, 'cutblock', 0.02)
    hb = box((0, 4, 0.6), (1.0, 1.0, 0.9), blk, 'hauled', 0.02)
    rope = cyl((0, 4, 8.5), 0.025, 15, mat('rope', (0.35, 0.27, 0.15), 0.9))
    key(hb, 'location', [(0, (0, 4, 0.6)), (int(n * 0.2), (0, 4, 0.6)), (n - 1, (0, 4, 11.0))])
    point((-0.8, -3, 1.8), 120, (1, 0.6, 0.3), 0.2)
    camera([(0, (0.6, -1.5, 1.2)), (n - 1, (0.3, 2.6, 1.0))], lens=20,
           target_keys=[(0, (0, 4, 1.5)), (n - 1, (0, 4, 10))])


BUILDERS = {
    'SH01_street': sh_street, 'SH02_tunnel_sign': sh_tunnel_sign, 'SH03_cinema': sh_cinema, 'SH04_screen': sh_screen,
    'SH05_cinema_dark': sh_cinema_dark, 'SH06_descent': sh_descent, 'SH07_stone': sh_stone, 'SH08_sea': sh_sea,
    'SH09_shaft': sh_shaft, 'SH10_roots': sh_roots, 'SH11_collapse': sh_collapse, 'SH12_pillars': sh_pillars,
}

if __name__ == '__main__':
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    name, out = argv[0], argv[1]
    reset()
    init_mats()
    n = nframes(name)
    frange(n)
    BUILDERS[name](n)
    frames = None
    if '--preview' in argv: preview(True)
    if '--frames' in argv:
        fs = argv[argv.index('--frames') + 1]
        frames = [int(min(n - 1, max(0, float(v) * (n - 1)))) if '.' in v else int(v) for v in fs.split(',')]
    render(os.path.join(out, name), frames)
