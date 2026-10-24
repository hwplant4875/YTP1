"""Test preview for aot/trost_action.py on the Shiganshina town (stand-in for agent C's Trost set, same scale).
Run after scene.py in the same Blender session (see render_trost_action.sh).  Every frame is a pure function of its
Trost time t: the shot list maps video time -> (Trost t, camera), so any frame / still renders on its own.

Stand-in site: the outer gate (0, -720) is Trost's breached south gate, the plaza gets a placeholder supply HQ
(walls + a roof that hides for the cutaway), the boulder lies on the main avenue, pyres on the inner gate square,
roof perches are read back from the scattered town houses.  Swap site() for agent C's Trost site dict to integrate.
"""
import bpy, bmesh, math, os, sys, time, argparse
import numpy as np
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ap = argparse.ArgumentParser()
ap.add_argument("--ta-out", required=True)
ap.add_argument("--fps", type=float, default=15.0)
ap.add_argument("--ta-samples", type=int, default=2)
ap.add_argument("--stills", default="", help="comma list of shot:frac (e.g. eaten:0.6) or T values (e.g. 62.2@cannon)")
ap.add_argument("--shots", default="", help="comma list of shot names to render (default all)")
ap.add_argument("--dry", action="store_true")
ap.add_argument("--speed", type=float, default=1.0, help="video duration multiplier")
B, _ = ap.parse_known_args(argv)

import aotlib as L
import trost_action as TA

OGX, OGY = L.OUTER_GATE

def roofs_from_town():
    ob = bpy.data.objects.get("Town")
    me = ob.data
    n = len(me.vertices)
    co = np.zeros(n * 3); me.vertices.foreach_get("co", co); co = co.reshape(n, 3)
    var = np.zeros(n, np.int32); me.attributes["variant"].data.foreach_get("value", var)
    scl = np.zeros(n * 3); me.attributes["scl"].data.foreach_get("vector", scl); scl = scl.reshape(n, 3)[:, 0]
    tops = {}
    for o in bpy.data.collections["HouseVariants"].objects:
        k = int(o.name[1:]) if o.name[1:].isdigit() else None
        if k is not None:
            tops[k] = max(v.co.z for v in o.data.vertices)
    R = []
    for i in range(n):
        x, y = co[i, 0], co[i, 1]
        if not L.in_district(x, y, 20) or y > -60:
            continue
        top = tops.get(int(var[i]), 14.0) * scl[i]
        R.append((x, y, L.height(x, y) + top - 0.2))
    return np.array(R)

def hq_placeholder(c, w, d, h):
    m = L.mat("TA_HQwall", (0.62, 0.55, 0.45), 0.85); r = L.mat("TA_HQroof", (0.35, 0.12, 0.07), 0.8)
    bm = bmesh.new()
    t = 1.2
    for s in (-1, 1):
        L.box(bm, (c[0], c[1] + s * (d / 2), h / 2), (w, t, h))
        L.box(bm, (c[0] + s * (w / 2), c[1], h / 2), (t, d, h))
    walls = L.obj_from_bm("TA_HQ_Walls", bm, [m])
    bm = bmesh.new()
    L.box(bm, (c[0], c[1], h + 0.4), (w + 1.5, d + 1.5, 0.8))
    L.box(bm, (c[0], c[1], h + 3.0), (w + 1.0, 2.0, 4.4), taper=(0.1, 1.0))
    roof = L.obj_from_bm("TA_HQ_Roof", bm, [r])
    fl = bmesh.new(); L.box(fl, (c[0], c[1], 0.2), (w - 1, d - 1, 0.3))
    L.obj_from_bm("TA_HQ_Floor", fl, [L.mat("TA_HQfloor", (0.3, 0.27, 0.22), 0.9)])
    return [roof]

def site():
    for n in ("OuterGate_Door", "Monument", "PlazaCrowd"):
        o = bpy.data.objects.get(n)
        if o:
            o.hide_render = o.hide_viewport = True
    hq = (L.PLAZA[0], L.PLAZA[1])
    w, d, h = 34.0, 26.0, 13.0
    roof = hq_placeholder(hq, w, d, h)
    roofs = roofs_from_town()
    keep = (np.abs(roofs[:, 0] - hq[0]) > w / 2 + 4) | (np.abs(roofs[:, 1] - hq[1]) > d / 2 + 4)
    roofs = roofs[keep]
    def walk(x, y):
        if abs(x - L.CX) < L.CANAL_W / 2 + 3:
            return False
        if abs(x - hq[0]) < w / 2 + 1 and abs(y - hq[1]) < d / 2 + 1:
            return False
        if abs(x) < 7 and OGY - 12 <= y <= OGY + 12:           # the gate passage
            return True
        if y < OGY - 6:                                          # outside the gate
            return abs(x) < 26 + (OGY - 6 - y) * 0.6 and y > OGY - 140
        return L.in_district(x, y, 6.0) and L.on_road(x, y)
    def ground(x, y):
        g = L.height(x, y)
        return max(g, 0.0) + 0.16 if L.in_district(x, y, 0.0) else g
    wall_pts = []
    for a in (-0.12, 0.12, -0.2, 0.2, -0.28, 0.28, -0.36, 0.36):
        x, y = 288.0 * math.sin(a), -L.S - 288.0 * math.cos(a)
        wall_pts.append((x, y, L.WALL_H + 0.3))
    return dict(gate=(OGX, OGY), inward=(0.0, 1.0), wall_z=L.WALL_H, hq=hq, hq_size=(w, d, h), hq_roof=roof,
                boulder=(2.0, -560.0), roofs=roofs, ground=ground, walkable=walk, bounds=(-290.0, 290.0, OGY - 140.0, -8.0),
                pyre=(0.0, -40.0), wall_pts=wall_pts)

# ---------------------------------------------------------------- shots: name, T0, T1, video seconds, cam(u) -> (loc, tgt, lens)
def _ease(u):
    return u * u * (3 - 2 * u)

def lerp_cam(a, b):
    def f(u):
        e = _ease(u)
        loc = Vector(a[0]).lerp(Vector(b[0]), e); tgt = Vector(a[1]).lerp(Vector(b[1]), e)
        lens = a[2] + (b[2] - a[2]) * e
        return loc, tgt, lens
    return f

def P3(xy, z=0.0):
    return (float(xy[0]), float(xy[1]), float(z))

def shots():
    S = TA.STATE; C = S["C"]; site = S["site"]
    g, inw, side, hq = site.gate, site.inw, site.side, site.hq
    er, ar = C["e_roof"], C["a_roof"]
    M, A0, Q, cxy = C["M"], C["A0"], C["Q"], C["cannon_xy"]
    stop, sp, P0 = C["stop"], C["shift_pt"], site.pyre
    eye = (er[:2] + ar[:2]) / 2
    at = lambda t: S["ATD"].state(t)[0]
    L_ = []
    L_.append(("flood", 3.0, 12.0, 1.6, lerp_cam((P3(g - inw * 60 + side * 120, 190), P3(g + inw * 120, 0), 30),
                                                  (P3(g - inw * 10 + side * 110, 170), P3(g + inw * 170, 0), 30))))
    L_.append(("eaten", 7.6, 13.7, 2.4, lerp_cam((P3(eye - side * 55 - inw * 45, er[2] + 48), P3(eye + inw * 6, er[2] - 4), 34),
                                                  (P3(eye - side * 45 - inw * 30, er[2] + 40), P3(eye, er[2] - 2), 40))))
    wr = TA.STATE["SQ"].pos("w1", 15.0)
    L_.append(("wiped", 14.9, 17.4, 1.1, lerp_cam((P3(wr[:2] - inw * 50 + side * 30, wr[2] + 40), P3(wr[:2], wr[2] - 4), 36),
                                                   (P3(wr[:2] - inw * 42 + side * 22, wr[2] + 36), P3(wr[:2], wr[2] - 6), 36))))
    L_.append(("hq_despair", 17.0, 21.0, 1.1, lerp_cam((P3(hq - inw * 120 + side * 60, 130), P3(hq, 0), 32),
                                                        (P3(hq - inw * 100 + side * 30, 115), P3(hq, 0), 32))))
    L_.append(("mikasa", 21.6, 27.0, 1.5, lerp_cam((P3(M + side * 80 - inw * 20, 90), P3((M + hq) / 2, 0), 30),
                                                    (P3(M + side * 60 - inw * 40, 70), P3(M, 2), 32))))
    L_.append(("attack", 26.4, 30.0, 1.6, lerp_cam((P3(A0 + side * 70 - inw * 50, 60), P3(A0, 8), 30),
                                                    (P3(A0 + side * 60 - inw * 60, 52), P3((A0 + M) / 2, 6), 30))))
    L_.append(("at_kills", 33.0, 37.5, 1.0, lambda u: (Vector(P3(at(33 + 4.5 * u) + side * 70 - inw * 50, 75)),
                                                        Vector(P3(at(33 + 4.5 * u), 6)), 30)))
    L_.append(("lift", 46.4, 52.2, 2.0, lerp_cam((P3(hq - inw * 26 + side * 14, 58), P3(hq, 1), 30),
                                                  (P3(hq - inw * 22 + side * 10, 50), P3(hq, 1), 30))))
    Cp = C["C_pt"]
    L_.append(("emerge", 56.2, 58.8, 1.0, lerp_cam((P3(Cp + side * 45 - inw * 40, 48), P3(Cp, 4), 32),
                                                    (P3(Cp + side * 38 - inw * 34, 42), P3(Q, 3), 32))))
    mid = (Q + cxy) / 2
    perp = np.array([C["cdir"][1], -C["cdir"][0]])
    L_.append(("cannon", 61.5, 63.2, 1.5, lerp_cam((P3(mid + perp * 40, 62), P3(mid, 5), 32), (P3(mid + perp * 36, 58), P3(Q, 6), 34))))
    L_.append(("salute", 64.3, 66.8, 1.0, lerp_cam((P3(Q + perp * 14 - C["cdir"] * 22, 52), P3(Q + C["cdir"] * 5, 2), 34),
                                                    (P3(Q + perp * 12 - C["cdir"] * 18, 46), P3(Q + C["cdir"] * 5, 2), 40))))
    L_.append(("boulder", 75.5, 104.0, 3.2, lambda u: (Vector(P3(at(75.5 + 28.5 * u) + side * 75 + inw * 45, 135)),
                                                        Vector(P3(at(75.5 + 28.5 * u) - inw * 20, 10)), 28)))
    L_.append(("levi", 105.0, 109.0, 1.4, lerp_cam((P3(stop - inw * -40 + side * 55, 55), P3(stop + inw * 22, 6), 32),
                                                    (P3(stop - inw * -36 + side * 45, 48), P3(stop + inw * 24, 4), 34))))
    mp = C["mpos"]
    L_.append(("pyres", 116.0, 120.6, 1.6, lerp_cam((P3(P0 - inw * 60 + side * 50, 60), P3(P0 + inw * 8, 0), 30),
                                                     (P3(mp - inw * 30 + side * 22, 30), P3(mp, 0), 34))))
    return L_

# ---------------------------------------------------------------- render loop
sc = bpy.context.scene
cy = sc.cycles
cy.samples = B.ta_samples; cy.use_adaptive_sampling = True; cy.use_denoising = True
try:
    cy.denoiser = "OPENIMAGEDENOISE"
except Exception:
    pass
cy.max_bounces, cy.diffuse_bounces, cy.glossy_bounces, cy.transmission_bounces = 3, 1, 1, 2
cy.volume_bounces = 0; cy.volume_step_rate = 6; cy.volume_max_steps = 96
sc.render.use_persistent_data = True
sc.render.use_simplify = True; sc.render.simplify_subdivision_render = 0
cy.texture_limit_render = "1024"
for n in ("Haze",):
    o = bpy.data.objects.get(n)
    if o:
        o.hide_render = True
sc.render.image_settings.file_format = "PNG"
os.makedirs(B.ta_out, exist_ok=True)

t0 = time.time()
TA.setup(site(), light=True)
print(f"[ta] setup {time.time() - t0:.1f}s", TA.info())
cam = sc.camera
if B.dry:
    tq = time.time()
    for T in np.arange(0.0, 126.0, 0.5):
        TA.update(float(T))
    print(f"[ta] dry: 252 updates {time.time() - tq:.1f}s")
    SH = shots()
    for nm, T0, T1, dur, cf in SH:
        print("[ta] shot", nm, T0, T1, [round(v, 1) for v in cf(0.0)[0]])
    for nm in ("eren", "mikasa", "armin", "levi", "attack", "boulder"):
        print("[ta] hero", nm, [None if TA.hero_pos(nm, T) is None else [round(float(v), 1) for v in TA.hero_pos(nm, T)] for T in (10, 25, 50, 62, 90, 108)])
    sys.exit(0)
SH = shots()
if B.shots:
    want = set(B.shots.split(","))
    SH = [s for s in SH if s[0] in want]
jobs = []        # (filename, T, cam fn, u)
if B.stills:
    byname = {s[0]: s for s in SH}
    for tok in B.stills.split(","):
        nm, fr = tok.split(":")
        s = byname[nm]; u = float(fr)
        jobs.append((f"still_{nm}_{u:.2f}.png", s[1] + (s[2] - s[1]) * u, s[4], u))
else:
    k = 0
    for nm, T0, T1, dur, cf in SH:
        n = max(2, int(round(dur * B.speed * B.fps)))
        for j in range(n):
            u = j / (n - 1)
            jobs.append((f"ta_{k:05d}.png", T0 + (T1 - T0) * u, cf, u)); k += 1
tr = time.time()
for i, (fn, T, cf, u) in enumerate(jobs):
    TA.update(T)
    loc, tgt, lens = cf(u)
    cam.location = loc; cam.rotation_euler = (tgt - loc).to_track_quat("-Z", "Y").to_euler(); cam.data.lens = lens
    cam.data.clip_start = 0.5
    sc.render.filepath = os.path.join(B.ta_out, fn)
    bpy.ops.render.render(write_still=True)
    el = time.time() - tr
    print(f"[ta] {i + 1}/{len(jobs)} T={T:.2f} -> {fn} ({el:.0f}s, {el / (i + 1):.1f}s/f)")
