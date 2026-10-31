"""g1 "Opening + Shiganshina fall" (SCENE_BIBLE_v2 B.g1): 32.0 s, frame W, KICK AT 11.0, ONE Blender run.

Built on render_fast.py (the owner-loved opening: the locked tree shot 0-2.05 is the same camera / kids timing) and the
pieces of render_fall.py / seq_carla.py, driven from ONE time base t (g1 seconds).  Camera = camkeys.cam("g1")
(bible keys K2-K12 + the 33.0 guide key) through camchan.CamPath; K0/K1 are replaced by the scene's exact locked tree
framing (render_fast.keys() maths).  Every frame is a pure function of t (camera, Colossal pose, FX, crowd, titans,
Carla, light), so any window / still renders on its own.  Run after scene.py (see render_g1.sh):
    blender -b -P aot/scene.py -P aot/render_g1.py -- --cam seq ... --g1-out DIR [--t0 0 --t1 32 --fps 15 --step 1]
    ... --times 2.0,4.5,7.0 (stills, g1_tSS.ss.png)
All beat times live in BEATS below (one-place re-time).
"""
import bpy, bmesh, math, os, random, shutil, sys, time, argparse
import numpy as np
from mathutils import Vector, Matrix, noise

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ap = argparse.ArgumentParser()
ap.add_argument("--g1-out", required=True)
ap.add_argument("--t0", type=float, default=0.0)
ap.add_argument("--t1", type=float, default=32.0)
ap.add_argument("--fps", type=float, default=15.0)
ap.add_argument("--step", type=int, default=1, help="render every n-th frame, copy it into the skipped slots")
ap.add_argument("--g1-samples", type=int, default=8)
ap.add_argument("--times", default="")
ap.add_argument("--prefix", default="g1")
ap.add_argument("--vclock", action="store_true", help="frames, --t0/--t1 and --times on the VIDEO clock (segtime.seg_t('g1', tv))")
B, _ = ap.parse_known_args(argv)

import aotlib as L
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
CA = sys.modules.get("colossal_asset")
FL = sys.modules.get("flight")
SC = sys.modules.get("seq_carla")
WD = sys.modules.get("world")
G1 = sys.modules.get("g1_set")
import camchan as CC
import camkeys as CK
import smokecards as SMC

GX, GY = L.OUTER_GATE
OG = Vector((GX, GY))

# ================================================================ BEATS (g1 LOCAL seconds, kick 11.0)
# g1 v4 (owner 10/27 07:34): 0-11 s are the reference opening's beats (renders/opening_preview_v4.mp4, render_fast.py @
# 791f565: bolt 4.62, left hand 4.8-5.12, head rise 4.62-8.0 ease-out^3, right hand 5.9-6.7, wind-up 8.8-10.3, kick 11.0)
# and play at real time (segtime G1_PLAN slope 1); after the kick the video clock runs 2 -> 5.5 -> 1.7 (Carla) -> 2.
BEATS = dict(
    TREE_END=2.05,            # locked tree shot 0-2.05
    BOLT=4.62,                # one thick S-curved bolt + darken (ref 4.45-5.6) + green-gold tint 0.8 s + 0.2 deg shake
    PALM_L=(5.25, 5.55),      # left palm on the wall top (v5: after the smoke column is up, ref/user/lightning_spec.md)
    RISE=(5.05, 8.0),         # head rises (ease-out, RISE_EXP) out of the smoke (v5: was 4.62)
    RISE_EXP=3.0,
    PALM_R=(5.9, 6.7),        # right hand grips
    STEAM=(8.4, 10.2),        # body steam builds AFTER the face zoom (v6 QA: no smoke over the face at the reveal)
    WIND=(8.8, 10.3),         # right-leg wind-up behind the wall (left foot planted)
    KICK=11.0,                # the foot hits the gate (fx845.update(t - KICK)); 0.2 deg shake
    LEG_BACK=(11.3, 12.2),    # kicking leg comes back down
    SPREAD=(11.9, 12.9),      # hands release, arms spread ~45 deg down: stands steaming
    VANISH=(13.6, 16.6),      # steam burst drifting WEST, body sinks away (video ~12.2-12.8)
    DINA=(12.2, 0.0),         # the Smiling (Dina) titan: from just outside the breach (hidden by the wall) she runs in through
                              # the breach and up the streets to Carla (arrives at T1 when seq_carla's walk ends, ~25.4); no pop-in
    DINA_CPS=2.2,             # her gait cycles per VIDEO second (a fast run that does not strobe at 15 fps)
    SMILE_IN=19.5,            # seq_carla frame mapping anchor (F 2200); her position before T1 comes from the DINA path
    BEND=25.5, GRAB=26.6, LIFT=(26.8, 27.6), BITE=28.4,   # Carla (bite hidden by head / hair, no blood)
    LIGHT_GOLD=(2.05, 5.0),   # locked-shot light -> golden S/SSW afternoon
    LIGHT_SEAM=(22.0, 31.5),  # golden -> render_fall2's low sunset (the g2 seam light)
    END=32.0,
)
T_KICK = BEATS["KICK"]
SIM_K = float(os.environ.get("G1_SIM_K", "1.6"))   # swarm timelapse factor after the kick (pour: ~12 inside by 21 s, 20-25 by 32 s)
def sim_t(t):
    return (t - T_KICK) * (SIM_K if t > T_KICK else 1.0)
# seq_carla frame numbering (30 fps) for g1 time: walk -> bend -> grab -> lift -> bite -> settle (piecewise linear)
F_KEYS = [(BEATS["SMILE_IN"], 2200.0), (BEATS["BEND"], 2395.0), (BEATS["GRAB"], 2445.0), (BEATS["LIFT"][0], 2452.0),
          (BEATS["LIFT"][1], 2515.0), (BEATS["BITE"], 2566.0), (BEATS["BITE"] + 0.5, 2592.0), (BEATS["END"], 2640.0)]
GOLD = dict(el=float(os.environ.get("G1_SUN_EL", "26")), az=float(os.environ.get("G1_SUN_AZ", "252")),
            col=(1.0, 0.88, 0.70), e=3.8, amb=0.22, expo=float(os.environ.get("EXPO", "-1.5")))   # sun from SSW, ~26 deg up
SEAM_LIGHT = dict(el=4.0, az=245.0, col=(1.0, 0.78, 0.58), e=4.2, amb=0.18, expo=float(os.environ.get("EXPO", "-1.5")))  # = render_fall2
SEAM_SKY = ((1.0, 0.62, 0.22, 1.0), (0.95, 0.66, 0.38, 1.0))
GOLD_SKY = ((0.95, 0.86, 0.58, 1.0), (0.44, 0.60, 0.62, 1.0))   # mackerel gold-green afternoon (ep01 17:36.8)

def smooth(a, b, t):
    u = min(1.0, max(0.0, (t - a) / (b - a))); return u * u * (3 - 2 * u)

def bump(t, a, b, c, d):
    return smooth(a, b, t) * (1 - smooth(c, d, t))

def plin(keys, t):
    if t <= keys[0][0]:
        return keys[0][1]
    for (a, fa), (b, fb) in zip(keys, keys[1:]):
        if t <= b:
            return fa + (fb - fa) * (t - a) / (b - a)
    return keys[-1][1]

# ================================================================ camera: camkeys g1 through camchan.CamPath
def tree_keys():
    """render_fast.keys() K0 / K1: start close on the kids, pull back to the loved tree framing by 2.0 s, hold to 2.05."""
    l0, t0, n0 = FL.flight_at(900) if FL else ((-480, 338, 6), (-300, 0, 10), 50)
    l0, t0 = Vector(l0), Vector(t0)
    kids = [o.matrix_world.translation for o in (bpy.data.objects.get("Eren"), bpy.data.objects.get("Mikasa")) if o]
    # v6 (QA batch1 P0): open AT the anime still (ref/hill_tree_wall_opening_ref.png: whole tree, wall top + sky), not on the
    # kids; a slight zoom-out over 2 s (back + up along the view line, wider lens), then the rise.
    back = Vector((l0.x - t0.x, l0.y - t0.y, 0.0)).normalized()
    # v14 (FEEDBACK_v13 §1: still too zoomed in): start only slightly in (anime composition), then a VERY slow, slight zoom-out
    c0 = l0 + back * 8.5 + Vector((0, 0, 2.6)); c0.z = max(c0.z, L.height(c0.x, c0.y) + 2.2)
    l1 = l0 + back * 10.0 + Vector((0, 0, 3.0)); l1.z = max(l1.z, L.height(l1.x, l1.y) + 2.5)
    tg = t0 + Vector((0, 0, 4.0))
    return [(0.0, tuple(c0), tuple(tg), n0 * 0.63), (2.0, tuple(l1), tuple(tg), n0 * 0.59),     # autopilot r4: a bit wider
            (2.05, tuple(l1), tuple(tg), n0 * 0.60)]                                         # (ref still: tree ~40 % wide)

def build_campath():
    ks = list(CK.cam("g1")["keys"])
    tk = tree_keys()
    d = max((Vector(a[1]) - Vector(b[1])).length for a, b in zip(ks[:3], tk))
    print(f"[g1] camkeys K0/K1 vs scene tree framing: max offset {d:.2f} m (K1 camkeys {ks[1][1]} scene {tuple(round(v, 2) for v in tk[1][1])})")
    ks[:3] = tk
    return CC.CamPath(ks)

def shake(t):
    """<= 0.2 deg for ~0.3 s at the bolt and at the kick (SCENE_BIBLE_v2 A3 shake rule)."""
    a = math.radians(0.2)
    return a * (bump(t, BEATS["BOLT"], BEATS["BOLT"] + 0.03, BEATS["BOLT"] + 0.15, BEATS["BOLT"] + 0.33)
                + bump(t, T_KICK, T_KICK + 0.03, T_KICK + 0.15, T_KICK + 0.33))

def cam_at(t):
    loc, tgt, lens = CAM.eval(t)
    loc, tgt = Vector(loc), Vector(tgt)
    if t < 2.3:                                           # opening push: never dip into the hill
        loc.z = max(loc.z, L.height(loc.x, loc.y) + 0.9)
    rot = (tgt - loc).to_track_quat("-Z", "Y").to_euler()
    a = shake(t)
    if a:
        rot.x += a * noise.noise(Vector((t * 31, 0.5, 7))); rot.z += a * noise.noise(Vector((2.5, t * 29, 1)))
        rot.y += 0.4 * a * noise.noise(Vector((9, 4, t * 23)))
    return loc, rot, lens

# ================================================================ the Colossal (colossal_asset plug-in, per frame)
def colossal_at(t):
    """(show, rise, kick, fade, hand_l, hand_r, spread, steam)."""
    show = BEATS["BOLT"] - 0.05 <= t < BEATS["VANISH"][1] + 0.1
    u = min(1.0, max(0.0, (t - BEATS["RISE"][0]) / (BEATS["RISE"][1] - BEATS["RISE"][0])))
    rise = 1 - (1 - u) ** BEATS["RISE_EXP"]              # ease-out: reads early, still creeping up at 8 s
    w0, w1 = BEATS["WIND"]
    if t < w0:
        kick = 0.0
    elif t < w1:
        kick = -smooth(w0, w1, t)
    elif t < T_KICK:
        u = (t - w1) / (T_KICK - w1); kick = -1.0 + 2.0 * u * u        # accelerating swing, impact at full speed
    else:
        kick = 1.0 - smooth(*BEATS["LEG_BACK"], t)
    hand_l = smooth(*BEATS["PALM_L"], t)
    hand_r = smooth(*BEATS["PALM_R"], t)
    spread = smooth(*BEATS["SPREAD"], t)
    fade = smooth(*BEATS["VANISH"], t)
    steam = smooth(*BEATS["STEAM"], t)
    return show, rise, kick, fade, hand_l, hand_r, spread, steam

COL = {}
def colossal_setup():
    if not (CA and CA.STATE):
        return
    arm = CA.STATE["arm"]
    CA.set_pose(0.0, 1.0, 0.0, hand_l=1.0, hand_r=1.0, steam=1.0)
    bpy.context.view_layer.update()
    for side, pre in (("L", "Left"), ("R", "Right")):
        a = next(b for b in arm.pose.bones if b.name.startswith(f"mixamorig_{pre}Arm_"))
        h = next(b for b in arm.pose.bones if b.name.startswith(f"mixamorig_{pre}Hand_"))
        sh = arm.matrix_world @ a.head; ln = (arm.matrix_world @ h.head - sh).length
        sg = -1 if side == "L" else 1
        COL[side] = sh + Vector((sg * math.cos(math.radians(45)), 0.15, -math.sin(math.radians(45)))).normalized() * ln * 0.95
    hb = arm.pose.bones["mixamorig_Head_06"]
    COL["head"] = arm.matrix_world @ hb.head
    mn = min((m.matrix_world @ Vector(c)).z for m in CA.STATE["meshes"] for c in m.bound_box)
    mx = max((m.matrix_world @ Vector(c)).z for m in CA.STATE["meshes"] for c in m.bound_box)
    print(f"[g1] Colossal: head (neck top) {tuple(round(v, 1) for v in COL['head'])}, bbox z {mn:.1f}..{mx:.1f}, "
          f"spread targets L {tuple(round(v, 1) for v in COL['L'])} R {tuple(round(v, 1) for v in COL['R'])}")

def colossal_pose(t):
    show, rise, kick, fade, hl, hr, spread, steam = colossal_at(t)
    col_coll = bpy.data.collections.get("ColossalTitan")
    if col_coll:
        col_coll.hide_render = not show
    if not (show and CA and CA.STATE):
        return
    CA.set_pose(kick, rise, fade, hand_l=hl, hand_r=hr, steam=steam)
    sink = Vector((0, 0, -30.0 * fade))
    for side in ("L", "R"):
        d = CA.STATE.get(f"hand{side}")
        if d and side in COL and spread > 0:
            g = d["pts"][2]
            up = Vector((0, -3.0, 6.0)) * math.sin(math.pi * spread)          # lift off the top, then down to the side
            d["tgt"].location = g.lerp(COL[side], spread) + up + sink
            for segs in d["fingers"]:
                for pb in segs:
                    pb.rotation_euler = (pb.rotation_euler.x * (1 - spread), 0, 0)
        elif d and fade > 0:
            d["tgt"].location = d["tgt"].location + sink
    _steam_west(fade)

def _steam_west(fade):
    """Colossal steam leans WEST (from inside it drifts screen-right); in the vanish it swells and drifts west."""
    st = CA.STATE.get("cards")
    if not st:
        return
    cs = st[0]; A = cs.pools["steam"].A
    hgt = np.clip(A[:, 3] - 44.0, 0.0, None)
    A[:, 1] -= hgt * 0.55 + 55.0 * fade ** 1.3
    A[:, 3] += 14.0 * fade
    A[:, 7] *= 1 + 1.3 * fade; A[:, 8] *= 1 + 1.3 * fade
    A[:, 12] *= 1 - smooth(0.75, 1.0, fade)
    cs.update(0.0)

# ================================================================ bolt, darken, flash, tint, shake (bible g1 FX)
STRIKE = Vector((-7.0, GY - 26.0, 0.0))                  # ~20 m outside the outer gate, behind the wall top
FLICKER = ((BEATS["BOLT"], BEATS["BOLT"] + 0.08), (BEATS["BOLT"] + 0.13, BEATS["BOLT"] + 0.25))   # on 0.08, off 0.05, on 0.12

def _emit_mat(name, col, strength, alpha=None):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; N = nt.nodes; Ln = nt.links
    N.remove(N["Principled BSDF"])
    em = N.new("ShaderNodeEmission"); em.inputs["Color"].default_value = (*col, 1); em.inputs["Strength"].default_value = strength
    if alpha is None:
        Ln.new(em.outputs[0], N["Material Output"].inputs["Surface"])
    else:
        tr = N.new("ShaderNodeBsdfTransparent"); mx = N.new("ShaderNodeMixShader"); mx.inputs[0].default_value = alpha
        Ln.new(tr.outputs[0], mx.inputs[1]); Ln.new(em.outputs[0], mx.inputs[2]); Ln.new(mx.outputs[0], N["Material Output"].inputs["Surface"])
        try:
            m.surface_render_method = "BLENDED"
        except Exception:
            pass
    m["toon"] = 1
    return m

def build_bolt():
    """v6 QA: radii x2.3 (read thick at ~470 m).  ONE thick, unbranched, gently S-curved yellow-white channel (ep01 17:40.5 25427), core #FCFA95 + soft glow sleeve."""
    rnd = random.Random(3)
    top = Vector((STRIKE.x + 70.0, STRIKE.y - 180.0, 760.0))
    n = 46
    pts = []
    for k in range(n + 1):
        s = k / n
        p = top.lerp(STRIKE, s)
        side = Vector((1.0, 0.25, 0.0)).normalized()
        p += side * (38.0 * math.sin(2 * math.pi * s) * (1 - 0.35 * s))            # the S
        if 0 < k < n:
            p += Vector((rnd.uniform(-4, 4), rnd.uniform(-4, 4), rnd.uniform(-3, 3)))
        pts.append(p)
    obs = []
    for name, rad, mat in (("G1_BoltCore", (6.0, 4.0), _emit_mat("G1BoltCore", (0.97, 0.955, 0.30), 60.0)),
                           ("G1_BoltGlow", (18.0, 11.0), _emit_mat("G1BoltGlow", (0.91, 0.58, 0.06), 12.0, alpha=0.30))):
        bm = bmesh.new()
        for k, (a, b) in enumerate(zip(pts, pts[1:])):
            r = rad[0] + (rad[1] - rad[0]) * k / n
            L.cyl(bm, a, b, r, r * 0.97, seg=8)
        ob = L.obj_from_bm(name, bm, [mat])
        for at in ("visible_shadow", "visible_diffuse", "visible_glossy", "visible_transmission"):
            setattr(ob, at, False)
        ob.hide_render = True
        obs.append(ob)
    return obs

ARC_N, ARC_SEG, ARC_CRAWL = 9, 14, 0.45
def build_arcs():
    """v5 (ref/user/lightning_spec.md 5): thin orange-red wavy ribbon arcs writhing down from the wall top over the darkened
    town, each split into ARC_SEG chunks that light up head-first and go out behind (a crawling strand), one material each."""
    rnd = random.Random(17); arcs = []
    for k in range(ARC_N):
        x0 = STRIKE.x + rnd.uniform(-110, 110); y0 = GY + rnd.uniform(2, 14); z0 = rnd.uniform(70, 110)
        Ln_ = rnd.uniform(230, 340); hd = math.radians(90 + rnd.uniform(-35, 35)); dz = rnd.uniform(-60, -30)
        ph, amp = rnd.uniform(0, 6.3), rnd.uniform(10, 22)
        pts = []
        for i in range(ARC_SEG * 3 + 1):
            s_ = i / (ARC_SEG * 3)
            side = Vector((-math.sin(hd), math.cos(hd), 0.0))
            p = Vector((x0 + Ln_ * s_ * math.cos(hd), y0 + Ln_ * s_ * math.sin(hd), z0 + dz * s_ - 25 * s_ * s_))
            p += side * amp * math.sin(ph + 9.0 * s_) + Vector((0, 0, 0.5 * amp * math.sin(ph * 1.7 + 13.0 * s_)))
            p += Vector((rnd.uniform(-1.5, 1.5), rnd.uniform(-1.5, 1.5), rnd.uniform(-1.5, 1.5)))
            pts.append(p)
        mat = _emit_mat(f"G1Arc{k}", (1.0, 0.20, 0.03), 0.0)
        em = next(n for n in mat.node_tree.nodes if n.type == "EMISSION")
        obs = []
        for c in range(ARC_SEG):
            bm = bmesh.new()
            for a, b in zip(pts[3 * c:3 * c + 3], pts[3 * c + 1:3 * c + 4]):
                L.cyl(bm, a, b, 2.0, 2.0, seg=6)
            ob = L.obj_from_bm(f"G1_Arc{k}_{c}", bm, [mat])
            for at in ("visible_shadow", "visible_diffuse", "visible_glossy", "visible_transmission"):
                setattr(ob, at, False)
            ob.hide_render = True; obs.append(ob)
        arcs.append((obs, em, BEATS["BOLT"] + 0.35 + 0.12 * k + rnd.uniform(0, 0.06)))
    return arcs

def build_strike_cards():
    """v5 (lightning_spec.md 3 + 6): the dome shockwave flash + upward spark streaks behind the wall top, then the big SMOKE
    column that rises right after the strike and is up BEFORE the Colossal's head (RISE 5.05) - he emerges from it."""
    rng = np.random.default_rng(23); b = BEATS["BOLT"]
    X = SMC.SmokeCards("G1Strike")
    X.add(b + 0.08, (STRIKE.x, STRIKE.y, 62.0), r0=30.0, r1=210.0, life=0.5, kind="glow", color=(1.0, 0.78, 0.32), alpha=0.95, fade_in=0.02)
    X.add(b + 0.1, (STRIKE.x, STRIKE.y, 66.0), r0=16.0, r1=90.0, life=0.35, kind="glow", color=(1.0, 0.95, 0.7), alpha=1.0, fade_in=0.02)
    n = 46
    d = np.column_stack([rng.normal(0, 0.6, n), rng.normal(0, 0.35, n), rng.uniform(0.5, 1.4, n)])
    d /= np.linalg.norm(d, axis=1)[:, None]
    X.add_many(b + 0.08 + rng.uniform(0, 0.15, n), np.tile((STRIKE.x, STRIKE.y, 60.0), (n, 1)) + rng.normal(0, 3, (n, 3)),
               d * rng.uniform(90, 220, n)[:, None], r0=3.0, r1=1.8, life=rng.uniform(0.3, 0.6, n), kind="glow",
               color=(1.0, 0.82, 0.38), alpha=1.0, fade_in=0.01, dirs=d, stretch=7.0)
    X.build(); X.wind = (0.0, 0.0); CARDS.append(X)
    Sm = SMC.SmokeCards("G1StrikeSmoke")
    n = 46                                                  # the burst: billows up past the wall top within ~0.4 s
    Sm.add_many(b + 0.05 + rng.uniform(0, 0.35, n), np.column_stack([STRIKE.x + rng.normal(0, 20, n), STRIKE.y + rng.normal(0, 8, n),
                rng.uniform(15, 50, n)]), np.column_stack([rng.normal(0, 6, n), rng.normal(0, 3, n), rng.uniform(32, 56, n)]),
                r0=rng.uniform(13, 20, n), r1=rng.uniform(42, 64, n), life=rng.uniform(7, 10, n), rise=2.0,
                color=(0.60, 0.53, 0.45), kind="steam", alpha=0.9, tau=0.9, fade_in=0.08)
    te = np.arange(b + 0.3, BEATS["KICK"], 0.08); n = len(te)       # the sustained column behind him
    Sm.add_many(te, np.column_stack([STRIKE.x + rng.normal(0, 16, n), STRIKE.y + rng.normal(0, 7, n), rng.uniform(10, 40, n)]),
                np.column_stack([rng.normal(0, 4, n), rng.normal(-1, 2, n), rng.uniform(20, 32, n)]), r0=rng.uniform(13, 18, n),
                r1=rng.uniform(40, 58, n), life=rng.uniform(7, 9, n), rise=1.5, color=(0.66, 0.60, 0.53), kind="steam", alpha=0.8,
                tau=1.0, fade_in=0.2)
    Sm.build(); Sm.wind = (-0.5, 0.15); CARDS.append(Sm)
    print(f"[g1] strike cards {X.count()}, strike smoke {Sm.count()}")

FXS = {}
def build_fx():
    FXS["bolt"] = build_bolt()
    FXS["arcs"] = build_arcs() if os.environ.get("G1_ARCS") else []      # v14: the orange arcs after the bolt are removed
    ld = bpy.data.lights.new("G1_Flash", "POINT"); ld.color = (1.0, 0.92, 0.55); ld.shadow_soft_size = 30
    lo = bpy.data.objects.new("G1_Flash", ld); lo.location = STRIKE + Vector((0, 0, 160))
    bpy.context.scene.collection.objects.link(lo); ld.energy = 0.0
    FXS["flash"] = ld
    # compositor grade: darken + green-gold tint (multiply), inserted before the EeveeHaze output
    sc = bpy.context.scene
    ng = getattr(sc, "compositing_node_group", None)
    FXS["grade"] = None
    if ng is not None:
        out = next((n for n in ng.nodes if n.type == "GROUP_OUTPUT"), None)
        if out is not None and out.inputs[0].is_linked:
            lk = out.inputs[0].links[0]; src = lk.from_socket; ng.links.remove(lk)
            mx = ng.nodes.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.blend_type = "MULTIPLY"
            mx.inputs["Factor"].default_value = 1.0; mx.inputs["B"].default_value = (1, 1, 1, 1)
            ng.links.new(src, mx.inputs["A"]); ng.links.new(mx.outputs["Result"], out.inputs[0])
            FXS["grade"] = mx
    print("[g1] compositor grade:", "on" if FXS["grade"] else "off (no compositor group)")
    # EeveeHaze mist mix: its cool blue-grey turns the pale beige walls grey-white -> warm haze in g1 (default again at the seam)
    FXS["mist"] = None
    if ng is not None:
        for nd in ng.nodes:
            if nd.type == "MIX" and nd is not FXS["grade"] and nd.blend_type == "MIX":
                FXS["mist"] = (nd, tuple(nd.inputs["B"].default_value)); break
    # weak shadowless fill from the NE: the town face of the wall is backlit by the SSW sun, the fill gives the pilasters
    # visible light / shade sides under the toon bands
    fd = bpy.data.lights.new("G1_Fill", "SUN"); fd.energy = float(os.environ.get("G1_FILL_E", "1.1")); fd.color = (1.0, 0.95, 0.86)
    fd.use_shadow = False
    fo = bpy.data.objects.new("G1_Fill", fd); bpy.context.scene.collection.objects.link(fo)
    el, az = math.radians(28), math.radians(float(os.environ.get("G1_FILL_AZ", "60")))
    fo.rotation_euler = Vector((-math.cos(el) * math.cos(az), -math.cos(el) * math.sin(az), -math.sin(el))).to_track_quat("-Z", "Y").to_euler()
    fo.hide_render = True
    FXS["fill"] = fo

def fx_at(t, light_e):
    on = any(a <= t < b for a, b in FLICKER)
    for ob in FXS["bolt"]:
        ob.hide_render = not on
    b = BEATS["BOLT"]
    dk = bump(t, b - 0.17, b - 0.02, b + 0.9, b + 1.6)          # the screen darkens (v5: holds through the ribbons)
    tint = bump(t, b + 0.2, b + 0.3, b + 1.3, b + 1.6)          # dark amber / green tint while the ribbons crawl
    wf = bump(t, b + 0.22, b + 0.25, b + 0.33, b + 0.37)         # v5: the near full-screen white-yellow flash (~2 frames)
    FXS["flash"].energy = 6e6 if on else (4e6 * wf)
    for obs, em, t0 in FXS.get("arcs", ()):
        head = (t - t0) / ARC_CRAWL * ARC_SEG
        alive = t0 <= t < t0 + ARC_CRAWL + 0.35
        em.inputs["Strength"].default_value = 7.0 * (1 - smooth(t0 + ARC_CRAWL, t0 + ARC_CRAWL + 0.35, t))
        for c, ob in enumerate(obs):
            ob.hide_render = not (alive and head - 6 <= c < head)
    sc = bpy.context.scene
    sc.view_settings.exposure = light_e - 1.8 * dk + (0.8 if on else 0.0) + 2.6 * wf
    warm_k = smooth(*BEATS["LIGHT_GOLD"], t) * (1 - smooth(*BEATS["LIGHT_SEAM"], t))
    if FXS.get("mist"):
        nd, c0 = FXS["mist"]; wcol = (0.82, 0.77, 0.64, 1.0)
        nd.inputs["B"].default_value = tuple(a + (b - a) * warm_k for a, b in zip(c0, wcol))
    if FXS.get("fill"):
        FXS["fill"].hide_render = t < BEATS["TREE_END"] or warm_k < 1e-3       # off at the g2 seam (g2 has no fill)
        FXS["fill"].data.energy = float(os.environ.get("G1_FILL_E", "1.1")) * warm_k
    g = FXS["grade"]
    if g is not None:
        tc = (0.66, 0.74, 0.40)
        warm = smooth(*BEATS["LIGHT_GOLD"], t) * (1 - smooth(*BEATS["LIGHT_SEAM"], t))   # mild golden grade, neutral at the seam
        wc = (1.0, 0.965, 0.89)
        c = [(1.0 + (tc[i] - 1.0) * 0.75 * tint) * (1.0 + (wc[i] - 1.0) * warm) for i in range(3)]
        g.inputs["B"].default_value = (*c, 1.0)

# ================================================================ cards: kick dust dome, plume, gust, dark breach, smoke columns, vanish
CARDS = []
def build_cards():
    rng = np.random.default_rng(11)
    k = T_KICK
    # (a) dust dome at the wall foot inside the gate: 90-110 m wide, parapet height (40-55 m), orange-brown
    SMC.KINDS.setdefault("g1dust", dict(col=(0.62, 0.42, 0.22), emit=float(os.environ.get("G1_DUST_EMIT", "0.75")), thr=0.26, ns=2.0, lit=True))
    D = SMC.SmokeCards("G1Dust")
    n = 230
    x = rng.normal(0, 21, n); y = GY + 6 + np.abs(rng.normal(0, 22, n)); z = rng.uniform(3, 12, n)
    d = np.stack([x, y - GY, np.zeros(n)], 1); dn = d / np.maximum(np.linalg.norm(d, axis=1, keepdims=True), 1e-6)
    v = dn * rng.uniform(7, 15, (n, 1)); v[:, 2] = rng.uniform(8, 17, n)
    col = np.array([0.70, 0.46, 0.24]) * rng.uniform(0.85, 1.12, (n, 1))
    D.add_many(k + rng.uniform(0.0, 0.6, n), np.stack([x, y, z], 1), v, r0=rng.uniform(6, 9, n), r1=rng.uniform(18, 30, n),
               life=rng.uniform(7, 10, n), rise=rng.uniform(1.6, 3.0, n), color=col, kind="g1dust", alpha=0.9, tau=1.4, fade_in=0.15)
    n = 40                                                      # outside half of the dome (seen past the wall top)
    x = rng.normal(0, 22, n); y = GY - 8 - np.abs(rng.normal(0, 18, n)); z = rng.uniform(3, 12, n)
    v = np.stack([x * 0.3, (y - GY) * 0.3, rng.uniform(4, 9, n)], 1)
    D.add_many(k + rng.uniform(0, 0.4, n), np.stack([x, y, z], 1), v, r0=6, r1=rng.uniform(16, 24, n), life=rng.uniform(8, 11, n),
               rise=1.5, color=(0.68, 0.45, 0.24), kind="g1dust", alpha=0.7, tau=1.4, fade_in=0.15)
    n = 26                                                      # (b) central plume to ~80 m
    P = np.stack([rng.normal(0, 4, n), GY + rng.uniform(4, 14, n), rng.uniform(8, 20, n)], 1)
    v = np.stack([rng.normal(0, 2, n), rng.normal(2, 2, n), rng.uniform(20, 30, n)], 1)
    D.add_many(k + 0.1 + rng.uniform(0, 0.6, n), P, v, r0=7, r1=rng.uniform(13, 19, n), life=rng.uniform(7, 10, n), rise=2.5,
               color=(0.74, 0.52, 0.30), kind="g1dust", alpha=0.75, tau=2.2, fade_in=0.2)
    n = 34                                                      # (c) street gust: dust sheets racing up the avenue ~40 m/s
    P = np.stack([rng.normal(0, 6, n), GY + rng.uniform(10, 30, n), rng.uniform(1.5, 5, n)], 1)
    v = np.stack([rng.normal(0, 4, n), rng.uniform(34, 46, n), rng.uniform(0, 2, n)], 1)
    D.add_many(k + rng.uniform(0.05, 0.4, n), P, v, r0=3, r1=9, life=rng.uniform(2.6, 3.6, n), rise=0.5,
               color=(0.72, 0.56, 0.36), kind="g1dust", alpha=0.55, tau=2.6, fade_in=0.08)
    n = 30                                                      # (d) later dark roiling sheet over the nearby roofs
    P = np.stack([rng.normal(0, 45, n), GY + rng.uniform(25, 120, n), rng.uniform(18, 34, n)], 1)
    D.add_many(k + 1.5 + rng.uniform(0, 2.5, n), P, np.zeros((n, 3)), r0=18, r1=rng.uniform(28, 38, n), life=rng.uniform(7, 10, n),
               rise=0.6, color=(0.50, 0.36, 0.22), kind="g1dust", alpha=0.16, fade_in=1.0)
    n = 12                                                      # (e) the breach reads DARK: dust hanging in the hole
    P = np.stack([rng.uniform(-6, 6, n), GY + rng.uniform(-3, 6, n), rng.uniform(3, 15, n)], 1)
    D.add_many(np.full(n, k + 0.25), P, np.zeros((n, 3)), r0=6, r1=8, life=40.0, rise=0.0, color=(0.075, 0.06, 0.05), kind="smoke",
               alpha=0.85, fade_in=0.6)
    D.build(); CARDS.append(D)
    # thin wavy smoke columns from impact sites (5-8, 2-3 near-black), one by one 16-24 s
    S = SMC.SmokeCards("G1Smoke")
    sites = [(95, -470), (-100, -662), (205, -575), (35, -640), (150, -640), (62, -540), (-62, -612), (-130, -652)]   # v2: beyond the ruin as seen from the NW camera   # 8 columns (3 near-black)
    starts = [13.8, 15.0, 16.2, 17.4, 18.6, 15.6, 19.8, 17.0]
    order = list(range(len(sites)))
    for c, (si, ton) in enumerate(zip(order, starts)):
        if si >= len(sites):
            continue
        bx, by = sites[si]
        bz = G1.terrace_h(bx, by) if G1 else 0.0
        dark = c in (1, 3, 6)
        te = np.arange(ton, 33.0, 0.10); m = len(te)
        ph = c * 1.7
        vx = 2.4 * np.sin(0.75 * te + ph); vy = 1.6 * np.cos(0.55 * te + ph * 0.7)
        P = np.stack([np.full(m, bx) + rng.normal(0, 1.0, m), np.full(m, by) + rng.normal(0, 1.0, m), np.full(m, bz + 3.0)], 1)
        V = np.stack([vx * 1.6, vy * 1.6, rng.uniform(17.0, 21.0, m)], 1)
        colc = (0.05, 0.045, 0.04) if dark else (0.36, 0.34, 0.31)
        S.add_many(te, P, V, r0=rng.uniform(4.0, 5.5, m), r1=rng.uniform(12, 17, m), life=11.5, rise=0.0, color=colc,
                   kind="smoke", alpha=(0.7 if dark else 0.5), fade_in=0.4)
        n = 10                                                  # embers / small flames at the base
        S.add_many(ton - 1.0 + rng.uniform(0, 1.0, n), np.stack([bx + rng.normal(0, 3, n), by + rng.normal(0, 3, n), np.full(n, bz + 1.0)], 1),
                   None, r0=1.5, r1=2.6, life=40.0, rise=0.0, kind="fire", alpha=0.8, fade_in=0.4)
    S.build(); S.wind = (-0.5, 0.15); CARDS.append(S)
    # the Colossal's vanishing steam burst: a 60-80 m ball drifting WEST and thinning
    V_ = SMC.SmokeCards("G1Vanish")
    n = 90; t0, t1 = BEATS["VANISH"]
    hx = COL.get("head", Vector((-7, GY - 12, 55)))
    P = np.stack([hx.x + rng.normal(0, 12, n), hx.y + rng.normal(-4, 9, n), rng.uniform(26, 60, n)], 1)
    v = np.stack([rng.normal(-3, 4, n), rng.normal(0, 3, n), rng.uniform(3, 8, n)], 1)
    V_.add_many(t0 + rng.uniform(0, 1.6, n), P, v, r0=rng.uniform(8, 12, n), r1=rng.uniform(22, 34, n), life=rng.uniform(5.5, 8.0, n),
                rise=3.0, color=(0.93, 0.92, 0.89), kind="steam", alpha=0.85, tau=2.0, fade_in=0.3)
    V_.build(); V_.wind = (-7.0, 0.6); CARDS.append(V_)
    print(f"[g1] cards: dust {D.count()} smoke {S.count()} vanish {V_.count()}")

# ================================================================ the Yeager terrace: lift the fx845 pieces that sit on it
def lift_terrace():
    FXM = sys.modules.get("fx845")
    if not (G1 and FXM):
        return 0
    th = G1.terrace_h
    REG = FXM.REG
    skip = {id(b["ob"]) for b in REG["blocks"]} | {id(p["ob"]) for p in REG["puffs"]}
    for H in REG["houses"]:
        for part in H["parts"]:
            skip.add(id(part[0]))
    for b in REG["blocks"]:
        b["p1"].z += th(b["p1"].x, b["p1"].y)
    for p in REG["puffs"]:
        p["c"].z += th(p["c"].x, p["c"].y)
    rows = REG.get("cards_rows")
    if rows:
        for i, r in enumerate(rows):
            P = r[1]
            h = th(P[0], P[1])
            if h:
                rows[i] = (r[0], (P[0], P[1], P[2] + h)) + tuple(r[2:])
        REG["cards_n"] = None                             # rebuild the dust cards from the lifted rows on the next update
    n = 0
    for cn in ("States845", "FX845"):
        c = bpy.data.collections.get(cn)
        if not c:
            continue
        for ob in c.all_objects:
            if id(ob) in skip or ob.name.startswith(("Ruins845", "Rubble845", "Scars845", "FxDust")):
                continue
            h = th(ob.location.x, ob.location.y)
            if h > 0.01:
                ob.location.z += h; n += 1
    return n

def swap_rocks():
    """Thrown gate rocks and stones -> rounded rough lumps (bible: natural rock lumps 2-10 m, never cubes)."""
    if not G1:
        return 0
    rock = G1._mats({})["rock"]
    protos = [G1.lump_mesh(f"G1LumpProto{i}", 900 + i) for i in range(6)]
    for p in protos:
        p.materials.append(rock)
    n = 0
    for ob in bpy.data.objects:
        if ob.type != "MESH":
            continue
        if ob.name.startswith("ThrownBlock"):
            dims = ob.dimensions.copy(); s = max(dims) / max(1e-3, max(ob.scale))
            me = G1.lump_mesh(ob.name + "_lump", n + 40, squash=(1.0, 0.82, 0.74))
            for v in me.vertices:
                v.co *= s
            me.materials.append(rock)
            ob.data = me; n += 1
        elif ob.name.startswith(("Stone", "Spray")) and not ob.name.startswith("StoneProto"):
            ob.data = protos[n % len(protos)]; n += 1
    return n

# ================================================================ light: locked shot -> gold S/SSW -> g2's sunset (seam)
LT = {}
def light_setup():
    if not (WD and hasattr(WD, "light_rig")):
        return
    LT["spec0"] = WD.light_capture()
    LT["suns"] = [(o, o.hide_render, o.rotation_euler.copy(), tuple(o.data.color), o.data.energy)
                  for o in bpy.data.objects if o.type == "LIGHT" and o.data.type == "SUN"]
    w0 = bpy.context.scene.world
    LT["world"] = []
    if w0 and w0.use_nodes:
        for nd in w0.node_tree.nodes:
            if nd.type == "TEX_SKY":
                LT["world"].append((nd, "sky", (nd.sun_elevation, nd.sun_rotation)))
            if nd.type == "BACKGROUND":
                LT["world"].append((nd, "bg", nd.inputs[1].default_value))
    LT["expo0"] = bpy.context.scene.view_settings.exposure
    w = bpy.context.scene.world
    LT["ramp"] = []
    if w and w.use_nodes:
        for nd in w.node_tree.nodes:
            if nd.type == "VALTORGB":
                e = nd.color_ramp.elements
                LT["ramp"].append((e[0], tuple(e[0].color), e[1], tuple(e[1].color)))

def light_at(t):
    """Returns the exposure the frame should use (fx_at adds the bolt darken / flash on top)."""
    if not LT:
        return bpy.context.scene.view_settings.exposure
    if t < BEATS["TREE_END"]:                         # the locked tree shot keeps its built light exactly
        for o, h, rot, col, en in LT["suns"]:
            o.hide_render = h; o.rotation_euler = rot; o.data.color = col; o.data.energy = en
        for nd, kind, v in LT["world"]:
            if kind == "sky":
                nd.sun_elevation, nd.sun_rotation = v
            else:
                nd.inputs[1].default_value = v
        P = dict(LT["spec0"], expo=LT["expo0"])
    else:
        u = smooth(*BEATS["LIGHT_GOLD"], t)
        P = WD.light_blend(LT["spec0"], GOLD, u)
        k = smooth(*BEATS["LIGHT_SEAM"], t)
        if k > 0:
            P = WD.light_blend(P, SEAM_LIGHT, k)
        P = WD.light_rig(P)
    k = smooth(*BEATS["LIGHT_SEAM"], t)
    g = smooth(*BEATS["LIGHT_GOLD"], t)
    for (e0, c0, e1, c1) in LT["ramp"]:                 # camera sky: built blue -> gold-green afternoon -> g2's sunset
        a0 = tuple(a + (b - a) * g for a, b in zip(c0, GOLD_SKY[0])); a1 = tuple(a + (b - a) * g for a, b in zip(c1, GOLD_SKY[1]))
        e0.color = tuple(a + (b - a) * k for a, b in zip(a0, SEAM_SKY[0]))
        e1.color = tuple(a + (b - a) * k for a, b in zip(a1, SEAM_SKY[1]))
    if G1 and G1.STATE.get("sky_mat"):                  # the mackerel layer warms toward sunset too
        for nd in G1.STATE["sky_mat"].node_tree.nodes:
            if nd.type == "MIX" and nd.data_type == "RGBA":
                nd.inputs["A"].default_value = tuple(a + (b - a) * k for a, b in zip((0.78, 0.66, 0.46, 1), (0.95, 0.55, 0.30, 1)))
                nd.inputs["B"].default_value = tuple(a + (b - a) * k for a, b in zip((1.0, 0.93, 0.74, 1), (1.0, 0.78, 0.52, 1)))
    return P["expo"]

# ================================================================ setup
sc = bpy.context.scene
cam = sc.camera
if sc.render.engine.startswith("BLENDER_EEVEE"):
    sc.eevee.taa_render_samples = B.g1_samples
    ev = sc.eevee
    for k_, v_ in (("use_raytracing", False), ("volumetric_tile_size", "16"), ("volumetric_samples", 32),
                   ("shadow_resolution_scale", 0.5), ("shadow_ray_count", 1), ("shadow_step_count", 4)):
        try:
            setattr(ev, k_, v_)
        except Exception:
            pass
    sc.render.use_persistent_data = True
    for o in bpy.data.objects:                       # dozens of fire lights overflow Eevee's shadow pool: no shadows
        if o.type == "LIGHT" and o.name.startswith(("FireL", "FX_Flash", "G1_Flash")):
            o.data.use_shadow = False
sc.render.image_settings.file_format = "PNG"
os.makedirs(B.g1_out, exist_ok=True)
t_setup = time.time()
SW = None
if os.environ.get("G1_SWARM", "1") != "0":
    try:
        import swarm845 as SW
        if not SW.STATE.get("people"):
            SW.setup(t_end=float(os.environ.get("SWARM_TEND", "36")))
            print("[g1] swarm845", SW.info())
        SW.HIDE_TITANS = {"smiling"}
    except Exception as ex:
        import traceback; traceback.print_exc(); SW = None
FX845 = sys.modules.get("fx845")
if FX845 is not None and not any(FX845.REG.get(k_) for k_ in ("blocks", "mods", "houses", "appear")):
    FX845 = None
print("[g1] fx845:", "on" if FX845 else "off", "| seq_carla:", "on" if SC and SC.STATE.get("C") is not None else "off")
def bake_breach():
    """The EXACT boolean breach re-evaluated every frame costs ~50 s/frame: bake it once into a static copy
    (OuterGate_Broken) and swap the two meshes at the kick (fx845 appear / t_off)."""
    if not FX845:
        return False
    gate = bpy.data.objects.get("OuterGate")
    mods = [m for m in (gate.modifiers if gate else []) if m.type == "BOOLEAN"]
    if not mods:
        return False
    for m in mods:
        m.show_render = m.show_viewport = True
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(gate.evaluated_get(dg), preserve_all_data_layers=True, depsgraph=dg)
    br = bpy.data.objects.new("OuterGate_Broken", me); br.matrix_world = gate.matrix_world.copy()
    for c in gate.users_collection:
        c.objects.link(br)
    for m in mods:
        FX845.REG["mods"] = [x for x in FX845.REG["mods"] if x != m]
        gate.modifiers.remove(m)
    FX845.add_appear(gate, -1e9, t_off=0.0)
    FX845.add_appear(br, 0.0)
    return True
print("[g1] breach baked:", bake_breach())
n_lift = lift_terrace(); n_rock = swap_rocks()
print(f"[g1] terrace lifts {n_lift}, rock lumps {n_rock}")
for o in bpy.data.objects:                           # thick billow smoke columns -> replaced by the thin wavy card columns;
    if o.name.startswith("FireSmoke") or o.name == "Crater0":   # no crater under the Yeager rock (it sits ON the ruin)
        o.hide_render = o.hide_viewport = True
if FX845:                                            # ...and fx845 must not show them again
    FX845.REG["appear"] = [a for a in FX845.REG["appear"] if not (a[0].name.startswith("FireSmoke") or a[0].name == "Crater0")]
colossal_setup()
build_fx()
build_cards()
build_strike_cards()
light_setup()
CAM = build_campath()
import segtime as ST
VD = ST.vdur("g1")
def local_t(tv):
    """video seconds -> g1 local seconds (identity without --vclock)."""
    return ST.seg_t("g1", tv) if B.vclock else tv
# owner 10/27 video-clock limits: speed <= 300 m/s (the reference swoosh 2-4.9 s is the explicit exception), yaw <= 60 deg/s,
# pitch <= 50, lens 24-60; checked on what the viewer sees (camchan.VideoPath)
VLIM = dict(speed=300, yaw=60, pitch=(-5, 50), lens=(24, 300), hmin=None, hmax=None, under=1.0)
for nm, a_, b_ in (("g1 video clock, all", 0.0, VD), ("g1 video clock after the swoosh", 4.9, VD)):
    r = CC.check(CC.VideoPath(CAM, "g1"), a_, b_, limits=dict(VLIM, name=nm), quiet=True)
    print(f"[g1] camchan.check {nm} ({a_:.1f}-{b_:.2f} video s): peak {r['peak_speed']:.1f} m/s @ {r['t_peak_speed']:.2f}, "
          f"yaw {r['peak_yaw']:.1f} deg/s @ {r['t_peak_yaw']:.2f}, pitch {r['pitch_min']:.0f}..{r['pitch_max']:.0f}, "
          f"lens {r['lens_min']:.1f}-{r['lens_max']:.1f}, flags {r['flags']}")
# YH landing time (the 9 m rock) for Carla / the second rock
T_YH = None
if FX845:
    for b in FX845.REG["blocks"]:
        if b["ob"].name.startswith("ThrownBlock") and G1 and (b["p1"].to_2d() - G1.YH.to_2d()).length < 8:
            T_YH = T_KICK + b["launch"] + b["T"]
print(f"[g1] Yeager rock lands at {T_YH}")
PKC = bpy.data.collections.get("PK_People")
CARLA_OBS = []
if SC and SC.STATE.get("C") is not None:
    C_ = SC.STATE["C"]
    print(f"[g1] Carla C {tuple(round(v, 1) for v in C_)} f {tuple(round(v, 2) for v in SC.STATE['f'])} u {tuple(round(v, 2) for v in SC.STATE['u'])} "
          f"T0 {tuple(round(v, 1) for v in SC.STATE['T0'])} T1 {tuple(round(v, 1) for v in SC.STATE['T1'])} g {SC.STATE['g']:.2f}")
    for k_ in ("carla",):
        CARLA_OBS += SC._all_obs(SC.STATE[k_])
    bo = bpy.data.objects.get("CarlaBeams")
    if bo:
        CARLA_OBS.append(bo)
TITAN_OBS = SC._all_obs(SC.STATE["titan"]) if SC and SC.STATE.get("titan") is not None else []

# ---------------------------------------------------------------- the Smiling (Dina) titan: no pop-in (owner 10/27)
# She starts just outside the breach (hidden by the 50 m wall from every g1 camera), runs in through it right after the kick
# and up the streets (swarm845's walkable grid, the lanes the pour uses) to seq_carla's T0 -> T1 line, arriving at T1
# exactly when seq_carla's walk ends (F 2392); from then on pose_carla() drives her (idle -> reach -> lift -> bite).
DINA = {}
def _f_inv(F):
    """g1 local time at which plin(F_KEYS) reaches seq_carla frame F."""
    for (a, fa), (b, fb) in zip(F_KEYS, F_KEYS[1:]):
        if fa <= F <= fb:
            return a + (b - a) * (F - fa) / (fb - fa) if fb > fa else a
    return F_KEYS[-1][0]
def dina_setup():
    if not (SC and SC.STATE.get("titan") is not None):
        return
    T0, T1 = SC.STATE["T0"].to_2d(), SC.STATE["T1"].to_2d()
    pts = None
    if SW is not None:
        try:
            Gd = SW.build_grid()
            goal = SW.nearest_walk(Gd, T0.x, T0.y)
            dist = SW.dijkstra(Gd, [goal])
            st = SW.nearest_walk(Gd, GX, GY + 16.0)
            cells = SW.descend(Gd, dist, *st)
            P, _s = SW.make_path(Gd, (GX, GY + 16.0), cells, (T0.x, T0.y), 0.0, random.Random(1))
            pts = [Vector((float(x), float(y))) for x, y in P]
        except Exception:
            import traceback; traceback.print_exc(); pts = None
    if not pts:
        pts = [Vector((GX, GY + 16.0)), Vector((GX, GY + 60.0)), T0]
    pts = [Vector((GX, GY - 40.0)), Vector((GX, GY - 8.0))] + pts + [T1]
    clean = [pts[0]]
    for p in pts[1:]:
        if (p - clean[-1]).length > 0.5:
            clean.append(p)
    S_ = [0.0]
    for a, b in zip(clean, clean[1:]):
        S_.append(S_[-1] + (b - a).length)
    t_a, t_b = BEATS["DINA"][0], _f_inv(SC.T_WALK[1])
    DINA.update(P=clean, S=S_, L=S_[-1], t_a=t_a, t_b=t_b)
    v = S_[-1] / (t_b - t_a)
    print(f"[g1] Dina path {len(clean)} pts, {S_[-1]:.0f} m, local {t_a:.2f} -> {t_b:.2f} s (~{v:.0f} m/s local, "
          f"video {ST.to_video('g1', t_a):.2f} -> {ST.to_video('g1', t_b):.2f} s)")
def _dina_at(s):
    P, S_ = DINA["P"], DINA["S"]
    s = min(max(s, 0.0), DINA["L"])
    for i in range(len(S_) - 1):
        if s <= S_[i + 1] or i == len(S_) - 2:
            f = (s - S_[i]) / max(1e-6, S_[i + 1] - S_[i])
            return P[i].lerp(P[i + 1], min(1.0, max(0.0, f)))
def dina_pose(t):
    """Override seq_carla's titan placement + gait for t < t_b (call after pose_carla)."""
    if not DINA or t >= DINA["t_b"]:
        return
    u = min(1.0, max(0.0, (t - DINA["t_a"]) / (DINA["t_b"] - DINA["t_a"])))
    # trapezoid: full speed from the start (behind the wall), constant, then a smooth stop over the last 18 %
    ud = 0.18; vmax = 1.0 / (1.0 - ud / 2)
    f = vmax * u if u < 1 - ud else 1.0 - vmax * (1 - u) ** 2 / (2 * ud)
    s = DINA["L"] * f
    p = _dina_at(s); q = _dina_at(s + 6.0) - _dina_at(s - 6.0)
    ti = SC.STATE["titan"]
    yaw = SC._yaw_to(q) if q.length > 1e-3 else SC.STATE["yaw_t"]
    k_end = smooth(0.9, 1.0, u)                          # face along seq_carla's yaw_t at the end, settle to idle
    dy = (SC.STATE["yaw_t"] - yaw + math.pi) % (2 * math.pi) - math.pi
    yaw += dy * k_end
    SC._place(ti, p.x, p.y, yaw, z=L.height(p.x, p.y) - 0.1)
    if os.environ.get("G1_DEBUG"):
        print(f"[g1] DEBUG Dina t={t:.2f} s={s:.0f}/{DINA['L']:.0f} m at ({p.x:.0f}, {p.y:.0f})", flush=True)
    ph =(ST.to_video("g1", t) * BEATS["DINA_CPS"]) % 1.0
    pose = SC.t_walk(ti, ph)
    if k_end > 0:
        pose = SC._blend(pose, SC.t_idle(ti), k_end)
    SC._pose(ti, *pose, ground=True)
    bpy.context.view_layer.update()
dina_setup()

# swarm titans that come within 85 m of Carla during her beat: hidden for all of g1 from their entry (the old rule hid them
# when they stepped inside the circle = on-screen pop-outs); g2 keeps its own "inside 85 m" rule
NEAR_HIDE = {}
if SW is not None and SW.STATE and SC and SC.STATE.get("C") is not None:
    S_ = SW.STATE; C2 = SC.STATE["C"]
    ka = min(int(max(sim_t(BEATS["SMILE_IN"] - 2.0), 0) / SW.DT), S_["K"] - 1)
    kb = min(int(sim_t(BEATS["END"]) / SW.DT) + 1, S_["K"] - 1)
    inside = (S_["TX"][ka:kb + 1] - C2.x) ** 2 + (S_["TY"][ka:kb + 1] - C2.y) ** 2 < 85.0 ** 2
    for j in np.where(inside.any(axis=0))[0]:
        NEAR_HIDE[int(j)] = ka + int(np.where(inside[:, j])[0].max())          # last k inside
    n_exit = sum(1 for j, kl in NEAR_HIDE.items() if kl < kb)
    print(f"[g1] swarm titans hidden near Carla: {len(NEAR_HIDE)} of {S_['nt']} ({n_exit} leave the circle before the seam)")
import toon; toon.apply()
print(f"[g1] setup after scene build {time.time() - t_setup:.0f}s")

def kids_frame(t):
    f0 = getattr(FL, "F_KIDS", 750) if FL else 750
    return f0 + 30.0 * min(max(t, 0.0), 2.0) + 30.0 * max(0.0, t - 2.0) * 0.5

def set_frame(t):
    t0 = time.time()
    kf = kids_frame(t)
    sc.frame_set(int(kf), subframe=kf - int(kf))
    colossal_pose(t)
    e = light_at(t)
    fx_at(t, e)
    if FX845:
        FX845.update(t - T_KICK)
    if PKC:
        PKC.hide_render = t >= T_KICK + 0.4                # the standing kit crowd is swallowed by the gust; swarm people flee
    if SW is not None and SW.STATE:
        hide = {"smiling"}
        if NEAR_HIDE:
            k0 = min(int(max(sim_t(t), 0) / SW.DT), SW.STATE["K"] - 1)
            hide |= {j for j, kl in NEAR_HIDE.items() if k0 <= kl}
        SW.HIDE_TITANS = hide
        SW.update(sim_t(t))
    if SC and SC.STATE.get("C") is not None:
        vis_c = T_YH is not None and t >= T_YH + 0.2
        vis_t = t >= BEATS["DINA"][0]
        if vis_c or vis_t:
            SC.pose_carla(plin(F_KEYS, t))
            if vis_t:
                dina_pose(t)
        if not vis_c:                                    # (pose_carla shows Carla, and hides her after the bite)
            for o in CARLA_OBS:
                o.hide_render = True
        else:
            bo = bpy.data.objects.get("CarlaBeams")
            if bo:
                bo.hide_render = False
        for o in TITAN_OBS:
            if o.type in ("MESH", "ARMATURE"):
                o.hide_render = not vis_t
    rk2 = G1.STATE.get("rock2") if G1 else None
    if rk2 is not None:
        rk2.hide_render = not (T_YH is not None and t >= T_YH + 0.1)
    for cs in CARDS:
        cs.update(t)
    loc, rot, lens = cam_at(t)
    cam.location = loc; cam.rotation_euler = rot; cam.data.lens = lens
    return time.time() - t0

# ================================================================ render loop
T1_ = min(B.t1, VD) if B.vclock else B.t1
if B.times:
    jobs = [(float(x), None) for x in B.times.split(",") if x.strip()]        # video s with --vclock
else:
    i0 = int(round(B.t0 * B.fps)); i1 = int(round(T1_ * B.fps))
    if B.vclock:
        i1 = min(i1, int(math.floor(VD * B.fps - 1e-6)) + 1)
    jobs = [(i / B.fps, i) for i in range(i0, i1, max(1, B.step))]
    jobs = [j for j in jobs if not os.path.exists(os.path.join(B.g1_out, f"{B.prefix}_{j[1]:05d}.png"))]   # resume
print(f"[g1] {'VIDEO clock' if B.vclock else 'local clock'}: {len(jobs)} frames, fps {B.fps:g}, video length {VD:.2f} s")
t_start = time.time()
if os.environ.get("G1_PROFILE"):                     # timing probe: which part of the post-kick scene is slow
    t = float(os.environ["G1_PROFILE"]); set_frame(t)
    def rtime(tag):
        t0 = time.time(); sc.render.filepath = os.path.join(B.g1_out, f"prof_{tag}.png")
        bpy.ops.render.render(write_still=True); print(f"[g1] PROFILE {tag}: {time.time() - t0:.1f}s", flush=True)
    rtime("warm"); rtime("base")
    gate = bpy.data.objects.get("OuterGate")
    for md in (gate.modifiers if gate else []):
        if md.type == "BOOLEAN":
            md.show_render = md.show_viewport = False
    rtime("no_boolean")
    for cs in CARDS + [c for c in SMC._ALL if c not in CARDS]:
        for o in cs.objects():
            o.hide_render = True
    rtime("no_cards")
    for cn in ("Swarm845",):
        c = bpy.data.collections.get(cn)
        if c: c.hide_render = True
    rtime("no_swarm")
    for o in bpy.data.objects:
        if o.type == "MESH" and o.data.materials and any(m and m.node_tree and any(n.type == "OUTPUT_MATERIAL" and n.inputs["Volume"].is_linked for n in m.node_tree.nodes) for m in o.data.materials if m and m.use_nodes):
            o.hide_render = True
    rtime("no_volumes")
    for o in bpy.data.objects:
        if o.type == "LIGHT" and o.data.type == "POINT":
            o.hide_render = True
    rtime("no_pointlights")
    for cn in ("States845", "FX845"):
        c = bpy.data.collections.get(cn)
        if c: c.hide_render = True
    rtime("no_states")
    for cn in ("SeqCarla", "ColossalTitan"):
        c = bpy.data.collections.get(cn)
        if c: c.hide_render = True
    rtime("no_carla_colossal")
    jobs = []
for t, i in jobs:
    if os.path.exists(os.path.join(B.g1_out, "STOP")):
        print("[g1] STOP file found"); break
    t_fr = time.time()
    tv = t; t = local_t(tv)
    tp = set_frame(t)
    name = f"{B.prefix}_t{tv:05.2f}.png" if i is None else f"{B.prefix}_{i:05d}.png"
    sc.render.filepath = os.path.join(B.g1_out, name)
    bpy.ops.render.render(write_still=True)
    if i is not None and B.step > 1:
        for j in range(i + 1, min(i + B.step, int(round(T1_ * B.fps)))):
            shutil.copyfile(sc.render.filepath, os.path.join(B.g1_out, f"{B.prefix}_{j:05d}.png"))
    if os.environ.get("G1_DEBUG") and SW is not None:
        S_ = SW.STATE; ts_ = sim_t(t); k_ = min(int(max(ts_, 0) / SW.DT), S_["K"] - 1)
        ins = int(((S_["TY"][k_] > GY) & (S_["TY"][k_] < 0)).sum())
        print(f"[g1] DEBUG titans inside {ins}/{S_['nt']} tob hide {S_['tob'].hide_render} pob hide {S_['pob'].hide_render} "
              f"titan xy0 {S_['TX'][k_][:5].round(0)} {S_['TY'][k_][:5].round(0)} cards " +
              ", ".join(f"{p.ob.name}:{'-' if p.state is None else len(p.state[0])}/{p.ob.hide_render}" for cs in CARDS for p in cs.pools.values()), flush=True)
    print(f"[g1] tv={tv:.2f} t={t:.2f}s -> {name} (pose {tp:.1f}s, frame {time.time() - t_fr:.1f}s, total {time.time() - t_start:.0f}s)", flush=True)
