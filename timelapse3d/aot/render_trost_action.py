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
    """Stand-in supply HQ: stone walls, a broken roof edge (parapet + snapped rafters) for the cutaway, a plank floor
    with crates, barrels and gas-tank racks.  Only the roof slab hides in the cutaway."""
    import random
    rnd = random.Random(4)
    m = L.mat("TA_HQwall", (0.55, 0.50, 0.42), 0.85, bump=0.3, var=0.15, var_scale=0.3)
    r = L.mat("TA_HQroof", (0.35, 0.12, 0.07), 0.8)
    beam = L.mat("TA_HQbeam", (0.20, 0.11, 0.05), 0.85)
    bm = bmesh.new()
    t = 1.2
    for s in (-1, 1):
        L.box(bm, (c[0], c[1] + s * (d / 2), h / 2), (w, t, h))
        L.box(bm, (c[0] + s * (w / 2), c[1], h / 2), (t, d, h))
        # parapet / cornice with a ragged top edge: blocks of varying height along the wall tops
        for k in range(int(w / 2.2)):
            x = c[0] - w / 2 + 1.1 + k * 2.2
            L.box(bm, (x, c[1] + s * (d / 2), h + 0.5 + rnd.uniform(-0.3, 0.6)), (2.0, t + 0.4, 1.0 + rnd.uniform(0, 0.8)))
        for k in range(int(d / 2.2)):
            y = c[1] - d / 2 + 1.1 + k * 2.2
            L.box(bm, (c[0] + s * (w / 2), y, h + 0.5 + rnd.uniform(-0.3, 0.6)), (t + 0.4, 2.0, 1.0 + rnd.uniform(0, 0.8)))
    walls = L.obj_from_bm("TA_HQ_Walls", bm, [m])
    bm = bmesh.new()                      # snapped rafters sticking in from the wall tops (stay in the cutaway)
    for k in range(9):
        x = c[0] - w / 2 + 3 + k * (w - 6) / 8
        for s in (-1, 1):
            ln = rnd.uniform(2.5, 7.5)
            L.box(bm, (x, c[1] + s * (d / 2 - ln / 2), h - 0.4 - rnd.uniform(0, 0.6)), (0.5, ln, 0.5))
    L.box(bm, (c[0], c[1] - d / 2 + 4, h - 1.0), (w - 2, 0.6, 0.6))
    L.obj_from_bm("TA_HQ_Rafters", bm, [beam])
    bm = bmesh.new()
    L.box(bm, (c[0], c[1], h + 0.4), (w + 1.5, d + 1.5, 0.8))
    L.box(bm, (c[0], c[1], h + 3.0), (w + 1.0, 2.0, 4.4), taper=(0.1, 1.0))
    roof = L.obj_from_bm("TA_HQ_Roof", bm, [r])
    # plank floor (boards as thin strips in two tones)
    fl = bmesh.new()
    nb = int((w - 1) / 0.9)
    for k in range(nb):
        L.box(fl, (c[0] - (w - 1) / 2 + 0.45 + k * 0.9, c[1], 0.2), (0.85, d - 1, 0.3), mi=k % 2)
    L.obj_from_bm("TA_HQ_Floor", fl, [L.mat("TA_HQboard", (0.36, 0.22, 0.11), 0.9), L.mat("TA_HQboard2", (0.30, 0.18, 0.09), 0.9)])
    props = bmesh.new()
    for k in range(26):                   # crates and barrels along the walls, gas tanks on racks
        side = rnd.choice((-1, 1))
        if rnd.random() < 0.5:
            x = c[0] + rnd.uniform(-w / 2 + 2, w / 2 - 2); y = c[1] + side * (d / 2 - 1.8)
        else:
            x = c[0] + side * (w / 2 - 1.8); y = c[1] + rnd.uniform(-d / 2 + 2, d / 2 - 2)
        if rnd.random() < 0.55:
            sz = rnd.uniform(1.0, 1.6)
            L.box(props, (x, y, 0.35 + sz / 2), (sz, sz, sz), rot=rnd.uniform(0, 1.5), mi=0)
        else:
            L.cyl(props, (x, y, 0.35), (x, y, 1.6), 0.55, 0.5, seg=10, mi=1)
    for k in range(6):
        x = c[0] - w / 2 + 4 + k * 2.0
        L.box(props, (x, c[1] - d / 2 + 3.5, 1.4), (1.6, 0.4, 2.2), mi=0)
        for q in range(3):
            L.cyl(props, (x - 0.5 + q * 0.5, c[1] - d / 2 + 3.5, 0.6), (x - 0.5 + q * 0.5, c[1] - d / 2 + 3.5, 2.3), 0.18, 0.18, seg=8, mi=2)
    L.obj_from_bm("TA_HQ_Props", props, [L.mat("TA_crate", (0.42, 0.28, 0.13), 0.85), L.mat("TA_barrel", (0.26, 0.14, 0.06), 0.8),
                                          L.mat("TA_tank", (0.45, 0.47, 0.5), 0.4)])
    return [roof]

def site():
    for n in ("OuterGate_Door", "InnerGate_Door", "Monument", "PlazaCrowd"):
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
                pyre=(60.0, -110.0), wall_pts=wall_pts,
                inner_gate=(0.0, 0.0), inner_out=(0.0, 1.0), pyxis_pt=(0.0, -2.5, L.WALL_H + 0.2),
                bell_tower=(110.0, -180.0), bell_tower_top=52.0, cannon_square=(22.0, -40.0))

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
    M, A0, Q, cxy = C["M"], C["A0"], C["Q"], C["cannon_xy"]
    stop, sp, P0 = C["stop"], C["shift_pt"], site.pyre
    at = lambda t: S["ATD"].state(t)[0]
    L_ = []
    if "inner_gate" in site.d:
        G = np.array(site.d["inner_gate"], float); out = np.array(site.d["inner_out"], float); sd = np.array([out[1], -out[0]])
        L_.append(("evac", 6.0, 21.0, 2.6, lerp_cam((P3(G - out * 85 + sd * 50, 85), P3(G - out * 22, 0), 30),
                                                   (P3(G - out * 70 + sd * 35, 70), P3(G - out * 8, 0), 30))))
        pp = np.array(site.d["pyxis_pt"], float)
        L_.append(("pyxis", 68.5, 73.8, 1.6, lerp_cam((P3(G - out * 70 + sd * 34, 100), P3(G - out * 10, 36), 32),
                                                     (P3(G - out * 58 + sd * 26, 96), P3(G - out * 6, 42), 38))))
    if "bell_tower" in site.d:
        tw = np.array(site.d["bell_tower"], float); top = site.d.get("bell_tower_top", 50.0)
        def _bt(u, tw=tw, top=top):
            a = at(27.5 + 7.0 * u)
            mid = (tw + a) / 2; d = (a - tw) / max(1e-3, np.linalg.norm(a - tw)); pp = np.array([d[1], -d[0]])
            return (Vector(P3(mid + pp * (55 - 8 * u) - d * 6, 95 - 5 * u)), Vector(P3(mid, 8)), 32)   # steep: streets visible
        L_.append(("bell_tower", 27.5, 35.0, 1.6, _bt))
    L_.append(("flood", 3.0, 12.0, 1.6, lerp_cam((P3(g - inw * 60 + side * 120, 190), P3(g + inw * 120, 0), 30),
                                                  (P3(g - inw * 10 + side * 110, 170), P3(g + inw * 170, 0), 30))))
    L_.append(("hq_despair", 17.0, 21.0, 1.1, lerp_cam((P3(hq - inw * 120 + side * 60, 130), P3(hq, 0), 32),
                                                        (P3(hq - inw * 100 + side * 30, 115), P3(hq, 0), 32))))
    L_.append(("mikasa", 21.6, 27.0, 1.5, lerp_cam((P3(M + side * 80 - inw * 20, 90), P3((M + hq) / 2, 0), 30),
                                                    (P3(M + side * 60 - inw * 40, 70), P3(M, 2), 32))))
    L_.append(("attack", 26.4, 30.0, 1.6, lerp_cam((P3(A0 + side * 40 - inw * 30, 95), P3(A0, 6), 32),
                                                    (P3(A0 + side * 34 - inw * 36, 88), P3((A0 + M) / 2, 4), 32))))
    L_.append(("at_kills", 33.0, 37.5, 1.0, lambda u: (Vector(P3(at(33 + 4.5 * u) + side * 70 - inw * 50, 75)),
                                                        Vector(P3(at(33 + 4.5 * u), 6)), 30)))
    L_.append(("lift", 46.4, 52.2, 2.0, lerp_cam((P3(hq - inw * 26 + side * 14, 58), P3(hq, 1), 30),
                                                  (P3(hq - inw * 22 + side * 10, 50), P3(hq, 1), 30))))
    Cp = C["C_pt"]
    L_.append(("emerge", 56.2, 58.8, 1.0, lerp_cam((P3(Cp + side * 45 - inw * 40, 48), P3(Cp, 4), 32),
                                                    (P3(Cp + side * 38 - inw * 34, 42), P3(Q, 3), 32))))
    mid = (Q + cxy) / 2
    Qz = site.g(Q)
    perp = np.array([C["cdir"][1], -C["cdir"][0]])
    # near-vertical cameras: the street between the cannon and the trio is never hidden by a house
    L_.append(("cannon", 61.5, 63.2, 1.5, lerp_cam((P3(mid + perp * 10 - C["cdir"] * 4, Qz + 78), P3(mid, Qz), 30),
                                                    (P3(mid + perp * 8 - C["cdir"] * 6, Qz + 70), P3(mid - C["cdir"] * 4, Qz), 32))))
    sal = Q + C["cdir"] * 6.5
    L_.append(("salute", 64.3, 67.3, 2.0, lerp_cam((P3(sal + perp * 5 + C["cdir"] * 7, Qz + 30), P3(sal - C["cdir"] * 2, Qz + 0.5), 45),
                                                    (P3(sal + perp * 4 + C["cdir"] * 6, Qz + 26), P3(sal - C["cdir"] * 2, Qz + 0.5), 52))))
    L_.append(("boulder", 75.5, 115.0, 3.2, lambda u: (Vector(P3(at(75.5 + 39.5 * u) + side * 75 + inw * 45, 135)),
                                                        Vector(P3(at(75.5 + 39.5 * u) - inw * 20, 10)), 28)))
    L_.append(("levi", 116.0, 120.0, 1.4, lerp_cam((P3(stop - inw * -40 + side * 55, 55), P3(stop + inw * 22, 6), 32),
                                                    (P3(stop - inw * -36 + side * 45, 48), P3(stop + inw * 24, 4), 34))))
    mp = C["mpos"]
    L_.append(("pyres", 127.0, 131.6, 1.6, lerp_cam((P3(P0 - inw * 60 + side * 50, 60), P3(P0 + inw * 8, 0), 30),
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
if sc.render.engine.startswith("BLENDER_EEVEE"):
    sc.eevee.taa_render_samples = int(os.environ.get("EEVEE_SAMPLES", "16"))
    try:
        sc.eevee.use_shadows = True
    except AttributeError:
        pass
sc.render.image_settings.file_format = "PNG"
os.makedirs(B.ta_out, exist_ok=True)

t0 = time.time()
if os.environ.get("TA_SITE") == "trost":            # agent C's Trost set (AOT_SET=trost): site from trost.py
    import trost as TRS
    TRS.set_hq_cutaway(False); TRS.set_wagon(True)
    _hl = bpy.data.objects.get("TrostHQ_Lift")
    if _hl:
        _hl.hide_render = _hl.hide_viewport = True
    TA.setup(TA.site_from_trost(TRS), light=True)
else:
    TA.setup(site(), light=True)
print(f"[ta] setup {time.time() - t0:.1f}s", TA.info())
cam = sc.camera
if B.dry:
    tq = time.time()
    for T in np.arange(0.0, 126.0, 0.5):
        TA.update(float(T))
    print(f"[ta] dry: 252 updates {time.time() - tq:.1f}s")
    TT_ = TA.STATE["TT"]; gy_ = TA.STATE["site"].gate[1]
    for T_ in (3.0, 5.0, 7.0, 9.0, 11.0):
        ys = [float(TT_.pos(f"f{k}", T_)[1]) - gy_ for k in range(len([s_ for s_ in TT_.specs if s_["name"].startswith("f")]))]
        print(f"[ta] flood T={T_}: inside(>5m) {sum(1 for y in ys if y > 5)}/{len(ys)}  depth max {max(ys):.0f} m")
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
