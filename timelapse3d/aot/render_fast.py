"""Fast-paced opening (user spec 2026-10-24 09:06 UTC), timed in VIDEO SECONDS at 24 fps:
  0-2 s   tree: Eren wakes (sits up, stands), Mikasa beside him
  2 s     camera leaves the tree, whooshes through the inner gate to the plaza full of people
  5 s     the Colossal's head appears over the outer wall, its hand already gripping the wall top (anime)
  5-8 s   the head rises
  8-11 s  camera lifts to see the gate; the right leg winds up behind the wall
  11 s    the kick: the outer gate bursts, blocks fly into the town; then steam
Run after scene.py in the same session (see render_fast.sh). One session renders one time window with a fixed
destruction state; the shell script chains windows (intact before 11 s, kicked with growing AOT_ARC_T after).
"""
import bpy, bmesh, math, os, random, sys, time, argparse
from mathutils import Vector, noise

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ap = argparse.ArgumentParser()
ap.add_argument("--fast-out", required=True)
ap.add_argument("--t0", type=float, default=0.0)
ap.add_argument("--t1", type=float, default=11.0)
ap.add_argument("--fps", type=float, default=24.0)
ap.add_argument("--fast-samples", type=int, default=8)
ap.add_argument("--index0", type=int, default=0)
B, _ = ap.parse_known_args(argv)

import aotlib as L
CA = sys.modules.get("colossal_asset")
FL = sys.modules.get("flight")
GX, GY = L.OUTER_GATE
HEAD = Vector((float(os.environ.get("COL_DX", "-7")), GY - 16, 64))
PLAZA = Vector(L.PLAZA[:2])

def smooth(a, b, t):
    u = min(1.0, max(0.0, (t - a) / (b - a))); return u * u * (3 - 2 * u)

# ---------------------------------------------------------------- camera keys in seconds: (t, loc, look_at, lens)
def keys():
    l0, t0, n0 = FL.flight_at(900) if FL else ((-480, 338, 6), (-300, 0, 10), 50)
    return [
        (0.0, l0, t0, n0),
        (2.0, l0, t0, n0),                                       # hold on the tree while Eren gets up
        (2.7, (-430, 290, 28), (-150, 120, 14), 32),             # leave the tree: whoosh up and toward the gate
        (3.5, (-120, 150, 22), (0, 0, 10), 28),
        (4.1, (0, 20, 11), (0, -120, 12), 26),                   # through the inner gate tunnel
        (4.7, (PLAZA.x + 6, PLAZA.y + 70, 24), (PLAZA.x, PLAZA.y - 40, 10), 30),   # over the plaza crowd
        (5.0, (PLAZA.x + 8, PLAZA.y + 40, 20), tuple(HEAD + Vector((0, 0, -6))), 40),  # looking up at the wall: head appears
        (8.0, (PLAZA.x + 10, PLAZA.y + 20, 22), tuple(HEAD + Vector((0, 0, 2))), 62),  # slow push while it rises
        (10.0, (PLAZA.x + 40, PLAZA.y + 30, 120), (GX, GY + 30, 18), 40),             # lift: gate and wall in frame
        (11.0, (PLAZA.x + 45, PLAZA.y + 35, 128), (GX, GY + 40, 16), 40),
        (13.0, (PLAZA.x + 55, PLAZA.y + 50, 150), (GX, GY + 120, 0), 38),             # debris arcs into the town
    ]

def _cr(p0, p1, p2, p3, u):
    return 0.5 * ((2 * p1) + (-p0 + p2) * u + (2 * p0 - 5 * p1 + 4 * p2 - p3) * u * u + (-p0 + 3 * p1 - 3 * p2 + p3) * u ** 3)

def cam_at(t):
    ks = keys()
    t = min(max(t, ks[0][0]), ks[-1][0])
    i = max(j for j in range(len(ks)) if ks[j][0] <= t)
    if i == len(ks) - 1:
        return ks[-1][1:]
    a, b = ks[i], ks[i + 1]
    u = (t - a[0]) / (b[0] - a[0])
    P = [Vector(ks[max(0, min(len(ks) - 1, j))][1]) for j in (i - 1, i, i + 1, i + 2)]
    T = [Vector(ks[max(0, min(len(ks) - 1, j))][2]) for j in (i - 1, i, i + 1, i + 2)]
    loc, tgt = _cr(*P, u), _cr(*T, u)
    if 11.0 <= t < 12.0:                                          # impact shake
        k = (12.0 - t) * 3.0
        loc = loc + Vector((noise.noise(Vector((t * 40, 0, 0))), noise.noise(Vector((0, t * 40, 3))), noise.noise(Vector((5, 1, t * 40))))) * k
    return tuple(loc), tuple(tgt), a[3] + (b[3] - a[3]) * u

def colossal_at(t):
    """(show, rise, kick, fade). Hand grips the wall from the start (IK), the head rises 5-8 s, wind-up 8.8-10.3, strike to 11."""
    show = 4.6 <= t < 13.5
    rise = smooth(5.0, 8.0, t)
    if t < 8.8:
        kick = 0.0
    elif t < 10.3:
        kick = -smooth(8.8, 10.3, t)
    else:
        kick = -1.0 + 2.0 * smooth(10.3, 11.0, t)
    fade = smooth(11.6, 13.0, t)
    return show, rise, kick, fade

def kids_frame(t):
    """Flight-module frames for the kids: lie 750 -> sit 810 -> crouch 850 -> stand 870, compressed into 0-2 s."""
    return int(780 + 90 * smooth(0.0, 2.0, t))

# ---------------------------------------------------------------- plaza crowd (cheap: low-poly figures, varied colours)
def crowd(n=160, seed=4):
    rnd = random.Random(seed)
    bm = bmesh.new()
    cols = [(0.35, 0.22, 0.12), (0.55, 0.48, 0.38), (0.18, 0.2, 0.24), (0.45, 0.1, 0.08), (0.62, 0.6, 0.55), (0.25, 0.3, 0.18)]
    mats = [L.mat(f"Crowd{i}", c, 0.9) for i, c in enumerate(cols)] + [L.mat("CrowdSkin", (0.7, 0.5, 0.38), 0.6)]
    for k in range(n):
        a = rnd.uniform(0, math.tau); r = math.sqrt(rnd.random()) * (L.PLAZA[2] - 3)
        x, y = PLAZA.x + math.cos(a) * r, PLAZA.y + math.sin(a) * r
        h = rnd.uniform(1.5, 1.85); mi = rnd.randrange(len(cols))
        L.cyl(bm, (x, y, 0.1), (x, y, h * 0.82), 0.24, 0.19, seg=6, mi=mi)
        ico = bmesh.ops.create_icosphere(bm, subdivisions=1, radius=0.13)
        for v in ico["verts"]:
            v.co += Vector((x, y, h * 0.9))
        for f in {f for v in ico["verts"] for f in v.link_faces}:
            f.material_index = len(cols)
    L.obj_from_bm("PlazaCrowd", bm, mats)

# ---------------------------------------------------------------- render loop
sc = bpy.context.scene
cam = sc.camera
if sc.render.engine.startswith("BLENDER_EEVEE"):
    sc.eevee.taa_render_samples = B.fast_samples
else:
    sc.cycles.samples = B.fast_samples; sc.cycles.use_adaptive_sampling = True
sc.render.image_settings.file_format = "PNG"
os.makedirs(B.fast_out, exist_ok=True)
crowd()
col_coll = bpy.data.collections.get("ColossalTitan")
i, n = B.index0, int(round((B.t1 - B.t0) * B.fps))
t_start = time.time()
for j in range(n):
    t = B.t0 + j / B.fps
    show, rise, kick, fade = colossal_at(t)
    if col_coll:
        col_coll.hide_render = not show
        if show and CA and CA.STATE:
            CA.set_pose(kick, rise, fade)
    loc, tgt, lens = cam_at(t)
    cam.location = loc; cam.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat("-Z", "Y").to_euler(); cam.data.lens = lens
    sc.frame_set(kids_frame(t))
    sc.render.filepath = os.path.join(B.fast_out, f"fast_{i:05d}.png")
    bpy.ops.render.render(write_still=True)
    print(f"[fast] t={t:.2f}s -> {i} ({time.time() - t_start:.0f}s)")
    i += 1
