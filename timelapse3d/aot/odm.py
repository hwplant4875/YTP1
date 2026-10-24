"""ODM-gear soldiers for the sky views: cadet / Garrison / Scout squads on the rooftops, flying between roofs on two
wires with gas puffs, falling, grabbed and eaten, diving onto napes, Levi's spin.  A pure function of time.

Style: the minimal, colourful, faceless figures of swarm845 (same Geo builder and rig), drawn ~2x life size
(PSCALE) so they read from 60-250 m.  What reads from the sky: the CLOAK (cadets brown, Garrison dark red-brown,
Scouts green) with its emblem patch on the back (cadet crossed swords, Garrison twin roses, Scouts' blue/white
Wings of Freedom), hair colour (Mikasa black + red scarf, Armin blond, Levi black undercut, Jean two-tone,
Eren brown), the two dark wires and the white gas.

Each soldier (Flyer) owns a TRACK: a time-sorted list of segments.  Segments (t in the caller's clock):
    stand(t0, t1, p, yaw, pose="stand")        perched / standing; pose: stand run kneel lie salute rifle aim wave crouch
    walk(t0, t1, p0, p1, pose="run")           on foot along a straight line
    hop(t0, t1, p0, p1, apex=8, gas=1.0)       ODM swing roof -> roof: arc, body pitched, cloak streaming, two wires to
                                               anchors above/around p1 for the first 75 %, gas puffs; gas<1 = the gas
                                               runs out at that fraction (puffs stop, the wires drop)
    fall(t0, t1, p0, p1, spin=1.5)             ballistic fall, tumbling, flailing (no gas / knocked off)
    dive(t0, t1, p0, p_fn)                     straight drop with blades onto a moving target p_fn(t) (a nape)
    spin(t0, t1, c_fn, r, z0, z1, turns)       Levi: helix around the moving point c_fn(t), rolling on the flight axis
    follow(t0, t1, p_fn, yaw_fn=None, pose)    position from a function (held in a titan's hand, riding a nape, ...)
    gone(t0)                                   hidden from t0 on (eaten)
Before the first segment the flyer is hidden; between segments it holds the previous end state.

API
    import odm
    sq = odm.Squads("Trost", pscale=2.0)
    f = sq.flyer("mikasa", kit="cadet", hair="black", scarf=True)        # or sq.flyer("c12", kit="garrison")
    f.stand(0, 5, (x, y, z), yaw); f.hop(5, 6.2, p0, p1); ...            # or odm.roof_route(f, t0, roofs, ...)
    sq.build(coll)                    # once: meshes for bodies, wires, gas puffs
    sq.update(t)                      # every frame
    sq.pos(name, t) -> (x, y, z)      # for cameras / name tags; sq.state(name, t) -> full state dict
Kits: cadet, garrison, scout.  Hair keys: HAIRS.  Extra figure flags: scarf, rifle, cravat, scale.
"""
import math, random
import numpy as np
import bpy

import aotlib as L
import swarm845 as SW
import flares as FX

PSCALE = 2.0
G = 9.81

def _ss(u):
    u = min(1.0, max(0.0, u)); return u * u * (3 - 2 * u)

def v3(p):
    return np.array([float(p[0]), float(p[1]), float(p[2])])

# ---------------------------------------------------------------- palette (linear RGB)
BASE = {
    "jacket": (0.40, 0.19, 0.085), "trousers": (0.80, 0.78, 0.72), "boots": (0.07, 0.035, 0.02),
    "skin": (0.80, 0.55, 0.42), "steel": (0.42, 0.43, 0.45), "scarf": (0.62, 0.02, 0.025), "wood": (0.22, 0.10, 0.04),
    "cravat": (0.95, 0.95, 0.92), "white": (0.92, 0.92, 0.88), "red": (0.75, 0.03, 0.03), "blue": (0.03, 0.12, 0.62),
    "cloth": (0.85, 0.83, 0.78),
}
HAIRS = {"black": (0.012, 0.012, 0.016), "brown": (0.10, 0.055, 0.03), "blond": (0.78, 0.58, 0.20),
         "ash": (0.45, 0.34, 0.20), "dark": (0.035, 0.028, 0.025), "red": (0.38, 0.09, 0.03), "grey": (0.5, 0.5, 0.5),
         "jean": (0.42, 0.30, 0.17), "bald": (0.80, 0.55, 0.42), "auburn": (0.22, 0.07, 0.03)}
KITS = {   # cloak colour, emblem colours (a, b)
    "cadet":    dict(cloak=(0.30, 0.15, 0.055), em=("white", "red")),
    "garrison": dict(cloak=(0.24, 0.045, 0.03), em=("white", "red")),
    "scout":    dict(cloak=(0.045, 0.19, 0.08), em=("white", "blue")),
}
# Geo face categories -> material keys (per figure: hair / cloak picked per flyer)
CATS = ["jacket", "trousers", "boots", "skin", "HAIR", "CLOAK", "EM_A", "EM_B", "steel", "scarf", "wood", "cravat", "ACCENT"]

# ---------------------------------------------------------------- figure geometry (rig: 0 body, 1/2 legs, 3/4 upper arms,
# 5/6 forearms (5 = right, x>0), 7 cloak; pivots in local (y, z), model faces +y)
def figure_geo(g, i, kit, scarf=False, rifle=False, cravat=False, H=1.7, moustache=False, accent=False):
    s = H / 1.7
    hip, sh = 0.82 * s, 1.36 * s
    for side, part in ((-1, 1), (1, 2)):
        g.box((0.09 * s * side, 0, hip * 0.62), (0.14 * s, 0.15 * s, hip * 0.76), 1, i, part, (0, hip), (0, 0), hip)
        g.box((0.09 * s * side, 0.02 * s, hip * 0.17), (0.15 * s, 0.2 * s, hip * 0.34), 2, i, part, (0, hip), (0, 0), hip)
    g.box((0, 0, 1.08 * s), (0.36 * s, 0.22 * s, 0.6 * s), 0, i, 0, hip=hip, taper=0.92)           # jacket
    g.box((0, 0, 0.86 * s), (0.33 * s, 0.2 * s, 0.14 * s), 1, i, 0, hip=hip)                       # trousers top
    for side in (-1, 1):                                                                         # ODM hip units
        g.box((0.25 * s * side, -0.02 * s, 0.86 * s), (0.11 * s, 0.34 * s, 0.13 * s), 8, i, 0, hip=hip)
    g.box((0, -0.15 * s, 0.95 * s), (0.28 * s, 0.08 * s, 0.12 * s), 8, i, 0, hip=hip)              # back housing
    if scarf:
        g.box((0, 0.0, 1.40 * s), (0.30 * s, 0.26 * s, 0.10 * s), 9, i, 0, hip=hip)
        g.box((0.06 * s, -0.16 * s, 1.22 * s), (0.08 * s, 0.05 * s, 0.32 * s), 9, i, 7, (-0.13 * s, sh), (0, 0), hip)
    if accent:        # a bright collar + cloak hem (Eren's emerald cue among the brown cadet cloaks)
        g.box((0, -0.03 * s, 1.37 * s), (0.34 * s, 0.26 * s, 0.07 * s), 12, i, 0, hip=hip)
        g.box((0, -0.18 * s, 0.6 * s), (0.42 * s, 0.03 * s, 0.09 * s), 12, i, 7, (-0.155 * s, 1.36 * s), (0, 0), hip)
    if moustache:     # Pixis: a big white moustache, the one face cue allowed (it reads as a shape, not a face)
        g.box((0, 0.12 * s, 1.50 * s), (0.22 * s, 0.06 * s, 0.05 * s), 11, i, 0, hip=hip, taper=0.6)
    if cravat:
        g.box((0, 0.11 * s, 1.33 * s), (0.1 * s, 0.05 * s, 0.12 * s), 11, i, 0, hip=hip)
    for side, pu, pf in ((-1, 3, 6), (1, 4, 5)):
        g.box((0.23 * s * side, 0, sh - 0.15 * s), (0.09 * s, 0.10 * s, 0.32 * s), 0, i, pu, (0, sh), (0, 0), hip)
        g.box((0.23 * s * side, 0, sh - 0.45 * s), (0.08 * s, 0.09 * s, 0.30 * s), 0, i, pf, (0, sh), (0, sh - 0.3 * s), hip)
        g.box((0.23 * s * side, 0.01 * s, sh - 0.63 * s), (0.07 * s, 0.08 * s, 0.07 * s), 3, i, pf, (0, sh), (0, sh - 0.3 * s), hip)
        if not rifle:   # blades: thin grey strips along the forearm, pointing back
            g.box((0.23 * s * side, -0.12 * s, sh - 0.6 * s), (0.025 * s, 0.4 * s, 0.05 * s), 8, i, pf, (0, sh), (0, sh - 0.3 * s), hip)
    if rifle:
        g.box((0.17 * s, 0.05 * s, sh - 0.6 * s), (0.05 * s, 0.06 * s, 0.95 * s), 10, i, 5, (0, sh), (0, sh - 0.3 * s), hip)
    g.sphere((0, 0, 1.56 * s), 0.13 * s, 6, 4, 3, 4, -0.15, i, 0, hip, sz=1.12)
    # cloak: a slab hanging from the shoulders behind the back + the emblem patch on it
    cz0, cz1 = 0.55 * s, sh + 0.02 * s
    yb = -0.155 * s
    g.box((0, yb, (cz0 + cz1) / 2), (0.46 * s, 0.035 * s, cz1 - cz0), 5, i, 7, (yb, sh), (0, 0), hip, taper=0.78)
    g.box((0, yb - 0.025 * s, sh - 0.27 * s), (0.2 * s, 0.02 * s, 0.2 * s), 6, i, 7, (yb, sh), (0, 0), hip)
    if kit == "scout":     # wings: white left, blue right
        g.box((0.05 * s, yb - 0.04 * s, sh - 0.27 * s), (0.09 * s, 0.02 * s, 0.17 * s), 7, i, 7, (yb, sh), (0, 0), hip)
    elif kit == "garrison":   # two red roses
        for dx in (-0.045, 0.045):
            g.box((dx * s, yb - 0.04 * s, sh - 0.25 * s), (0.06 * s, 0.02 * s, 0.07 * s), 7, i, 7, (yb, sh), (0, 0), hip)
    else:                  # crossed swords
        g.box((0, yb - 0.04 * s, sh - 0.27 * s), (0.035 * s, 0.02 * s, 0.17 * s), 7, i, 7, (yb, sh), (0, 0), hip)
        g.box((0, yb - 0.04 * s, sh - 0.27 * s), (0.14 * s, 0.02 * s, 0.035 * s), 7, i, 7, (yb, sh), (0, 0), hip)
    return hip

def finish(g):
    R = g.finish()
    R["up"] = np.isin(R["part"], (0, 3, 4, 5, 6, 7)).astype(float)
    return R

def _rot(a, b, pa, pb, c, s):
    da = a - pa; db = b - pb
    return pa + da * c - db * s, pb + da * s + db * c

def deform(R, Ar, Ae, lean, vis, yaw, pos, pitch=None, roll=None, pivot=None):
    """swarm845._deform plus whole-body pitch (about local x, - = forward/head toward +y) and roll (about the local
    forward axis) around a per-object pivot height (local z, before scaling)."""
    o, p, B = R["oid"], R["part"], R["B"]
    y, z = B[:, 1], B[:, 2]
    ce, se = np.cos(Ae)[o, p], np.sin(Ae)[o, p]
    y, z = _rot(y, z, R["pe"][:, 0], R["pe"][:, 1], ce, se)
    cr, sr = np.cos(Ar)[o, p], np.sin(Ar)[o, p]
    y, z = _rot(y, z, R["pr"][:, 0], R["pr"][:, 1], cr, sr)
    a = lean[o] * R["up"]
    y, z = _rot(y, z, 0.0, R["hip"], np.cos(a), np.sin(a))
    x = B[:, 0].copy()
    if pitch is not None:
        pz = pivot[o]
        y, z = _rot(y, z, 0.0, pz, np.cos(pitch)[o], np.sin(pitch)[o])
        if roll is not None:
            x, z = _rot(x, z, 0.0, pz, np.cos(roll)[o], np.sin(roll)[o])
    s = vis[o]
    x = x * s; y = y * s; z = z * s
    c, sn = np.cos(yaw)[o], np.sin(yaw)[o]
    out = np.empty((len(B), 3))
    out[:, 0] = c * x - sn * y + pos[o, 0]
    out[:, 1] = sn * x + c * y + pos[o, 1]
    out[:, 2] = z + pos[o, 2]
    return out

def yaw_of(d):
    return math.atan2(-d[0], d[1])

# ---------------------------------------------------------------- tracks
class Flyer:
    def __init__(self, name, kit="cadet", hair="brown", scarf=False, rifle=False, cravat=False, H=1.7, scale=1.0, seed=0, moustache=False,
                 accent=None, cloak=None):
        self.name, self.kit, self.hair, self.scarf, self.rifle, self.cravat = name, kit, hair, scarf, rifle, cravat
        self.moustache, self.accent, self.cloak = moustache, accent, cloak       # accent: emissive rgb; cloak: rgb override
        self.H, self.scale = H, scale
        self.seg = []
        self.seed = seed

    # --- segment builders (return self so they chain) ---
    def stand(self, t0, t1, p, yaw=0.0, pose="stand"):
        self.seg.append(("stand", t0, t1, v3(p), yaw, pose)); return self
    def walk(self, t0, t1, p0, p1, pose="run"):
        self.seg.append(("walk", t0, t1, v3(p0), v3(p1), pose)); return self
    def hop(self, t0, t1, p0, p1, apex=None, gas=1.0, anchors=None):
        p0, p1 = v3(p0), v3(p1)
        d = np.linalg.norm(p1[:2] - p0[:2])
        if apex is None:
            apex = 3.0 + 0.12 * d
        self.seg.append(("hop", t0, t1, p0, p1, apex, gas, anchors)); return self
    def fall(self, t0, t1, p0, p1, spin=1.5):
        self.seg.append(("fall", t0, t1, v3(p0), v3(p1), spin)); return self
    def dive(self, t0, t1, p0, p_fn):
        self.seg.append(("dive", t0, t1, v3(p0), p_fn)); return self
    def spin(self, t0, t1, c_fn, r, z0, z1, turns=2.0, a0=0.0):
        self.seg.append(("spin", t0, t1, c_fn, r, z0, z1, turns, a0)); return self
    def follow(self, t0, t1, p_fn, yaw_fn=None, pose="flail", vis_fn=None):
        self.seg.append(("follow", t0, t1, p_fn, yaw_fn, pose, vis_fn)); return self
    def gone(self, t0):
        self.seg.append(("gone", t0, 1e9)); return self

    def end_pos(self):
        """Where the last segment leaves the flyer (for chaining)."""
        s = self.seg[-1]
        return self.state(s[2] if s[0] != "gone" else s[1] - 1e-3)["pos"]

    def t_end(self):
        return self.seg[-1][2] if self.seg else 0.0

    # --- evaluation ---
    def state(self, t):
        segs = self.seg
        cur = None
        for s in segs:                                   # latest-starting segment that has begun (ties: added last)
            if s[1] <= t and (cur is None or s[1] >= cur[1]):
                cur = s
        if cur is None:
            return dict(vis=0.0, pos=np.zeros(3), yaw=0.0, pitch=0.0, roll=0.0, pose="stand", gas=False, anchors=None, u=0.0)
        tt = min(t, cur[2])
        return self._eval(cur, tt, t)

    def _eval(self, s, t, t_raw):
        k = s[0]
        st = dict(vis=1.0, yaw=0.0, pitch=0.0, roll=0.0, pose="stand", gas=False, anchors=None, u=0.0)
        if k == "gone":
            st.update(vis=0.0, pos=np.zeros(3)); return st
        t0, t1 = s[1], s[2]
        u = 0.0 if t1 <= t0 else (t - t0) / (t1 - t0)
        st["u"] = u
        if k == "stand":
            st.update(pos=s[3], yaw=s[4], pose=s[5])
        elif k == "walk":
            p = s[3] + (s[4] - s[3]) * u
            st.update(pos=p, yaw=yaw_of(s[4] - s[3]), pose=s[5] if t_raw <= t1 else "stand")
            st["phase"] = np.linalg.norm(s[4][:2] - s[3][:2]) * u
        elif k == "hop":
            p0, p1, apex, gas, anc = s[3], s[4], s[5], s[6], s[7]
            ue = _ss(u) * 0.35 + u * 0.65                       # quick launch, steady swing
            p = p0 + (p1 - p0) * ue
            p = p.copy(); p[2] += 4 * apex * ue * (1 - ue)
            d = p1 - p0
            yaw = yaw_of(d) if np.linalg.norm(d[:2]) > 1e-3 else 0.0
            flying = t_raw < t1
            pitch = -1.25 * math.sin(math.pi * min(1.0, u * 1.15)) if flying else 0.0
            st.update(pos=p, yaw=yaw, pitch=pitch, pose="fly" if flying else "stand")
            st["gas"] = flying and u < gas and u < 0.85
            if flying and u < min(0.75, gas):
                if anc is None:
                    side = np.array([math.cos(yaw), math.sin(yaw), 0.0])
                    fwd = np.array([-math.sin(yaw), math.cos(yaw), 0.0])
                    anc = [p1 + side * sx * 3.5 + fwd * 4.0 + np.array([0, 0, 7.0]) for sx in (-1, 1)]
                st["anchors"] = anc
            if gas < 1.0 and u > gas:                            # out of gas: drop out of the arc
                pass
        elif k == "fall":
            p0, p1, spin = s[3], s[4], s[5]
            p = p0 + (p1 - p0) * u
            p = p.copy()
            T = t1 - t0
            vz0 = (p1[2] - p0[2] + 0.5 * G * T * T) / T if T > 0 else 0.0
            tau = t - t0
            p[2] = p0[2] + vz0 * tau - 0.5 * G * tau * tau
            st.update(pos=p, yaw=yaw_of(p1 - p0) if np.linalg.norm((p1 - p0)[:2]) > 1e-3 else 0.0,
                      pitch=-spin * math.tau * u if t_raw < t1 else -math.pi / 2, pose="flail" if t_raw < t1 else "lie")
            if t_raw >= t1:
                st["pitch"] = -math.pi / 2; st["pose"] = "lie"
        elif k == "dive":
            p0, fn = s[3], s[4]
            tgt = v3(fn(t))
            ue = u * u
            p = p0 + (tgt - p0) * ue
            st.update(pos=p, yaw=yaw_of(tgt - p0) if np.linalg.norm((tgt - p0)[:2]) > 0.2 else 0.0,
                      pitch=-0.6 * (1 - u) if t_raw < t1 else 0.0, pose="slash" if t_raw < t1 else "crouch")
            st["gas"] = t_raw < t1 and u < 0.6
            if t_raw < t1 and u < 0.7:
                st["anchors"] = [tgt + np.array([sx * 2.0, 0, 1.5]) for sx in (-1, 1)]
            if t_raw >= t1:
                st["pos"] = v3(fn(t_raw))
        elif k == "spin":
            fn, r, z0, z1, turns, a0 = s[3], s[4], s[5], s[6], s[7], s[8]
            c = v3(fn(t))
            a = a0 + turns * math.tau * _ss(u) if t_raw < t1 else a0 + turns * math.tau
            rr = r * (1 - 0.6 * u)
            p = c + np.array([math.cos(a) * rr, math.sin(a) * rr, 0.0])
            p[2] = c[2] + z0 + (z1 - z0) * u
            tang = np.array([-math.sin(a), math.cos(a), 0.0])
            st.update(pos=p, yaw=yaw_of(tang), pitch=-1.35 if t_raw < t1 else 0.0,
                      roll=(turns * 2.0 * math.tau * u) if t_raw < t1 else 0.0, pose="slash" if t_raw < t1 else "stand")
            st["gas"] = t_raw < t1
            if t_raw < t1:
                st["anchors"] = [c + np.array([0, 0, 1.0]), c + np.array([0.5, 0.5, 2.0])]
        elif k == "follow":
            fn, yfn, pose, vfn = s[3], s[4], s[5], s[6]
            st.update(pos=v3(fn(t_raw if t_raw < t1 else t1)), yaw=yfn(t) if yfn else 0.0, pose=pose)
            if vfn:
                st["vis"] = vfn(t_raw)
        return st


def roof_route(f, t0, pts, speed=22.0, wait=(0.6, 2.5), rnd=None, start_wait=0.0, apex=None):
    """Hop a flyer through a list of perch points (x, y, z) starting at t0 (first point = where it stands).
    Returns the time it lands on the last point."""
    rnd = rnd or random.Random(hash(f.name) & 0xffff)
    t = t0
    p = v3(pts[0])
    if start_wait > 0:
        f.stand(t, t + start_wait, p, 0.0); t += start_wait
    for q in pts[1:]:
        q = v3(q)
        d = np.linalg.norm(q - p)
        dur = max(0.7, d / speed)
        f.hop(t, t + dur, p, q, apex)
        t += dur
        w = rnd.uniform(*wait)
        yaw = yaw_of(q - p) if np.linalg.norm((q - p)[:2]) > 1e-3 else 0.0
        f.stand(t, t + w, q, yaw)
        t += w
        p = q
    return t

# ---------------------------------------------------------------- the squads system
POSES = {}   # pose -> function(st, t, i) -> (Ar(8), Ae(8), lean)

def _pose_arrays(pose, t, i, st):
    Ar = np.zeros(8); Ae = np.zeros(8); lean = 0.0
    w = math.sin(t * 2.0 + i * 1.3)
    if pose == "stand":
        Ar[3] = Ar[4] = 0.05 * w; Ae[5] = Ae[6] = 0.2; Ar[7] = -0.05 - 0.05 * w
    elif pose == "run":
        ph = 2 * math.pi * st.get("phase", t * 3.0) / 2.6
        sw = math.sin(ph) * 0.8
        Ar[1], Ar[2], Ar[3], Ar[4] = sw, -sw, -0.8 * sw, 0.8 * sw; Ae[5] = Ae[6] = 0.9; lean = -0.25; Ar[7] = -0.5
    elif pose == "fly":
        # body pitched (whole-body pitch in state); legs together trailing, arms back holding the grips, cloak flaring
        Ar[1], Ar[2] = 0.25, 0.35; Ar[3] = Ar[4] = -0.55; Ae[5] = Ae[6] = 0.5
        Ar[7] = -1.25 - 0.25 * math.sin(t * 17 + i)
    elif pose == "flail":
        Ar[1], Ar[2] = 0.9 * math.sin(t * 13 + i), -0.9 * math.sin(t * 13 + i)
        Ar[3], Ar[4] = 2.6 + 0.5 * math.sin(t * 15 + i), 2.6 - 0.5 * math.sin(t * 15 + i); Ar[7] = -1.8
    elif pose == "lie":
        Ar[3], Ar[4] = 0.4, -0.3; Ar[7] = -0.2
    elif pose == "kneel":
        Ar[1], Ar[2] = 1.4, 0.2; Ae[5] = Ae[6] = 1.0; lean = -0.3; Ar[3] = Ar[4] = 0.4; Ar[7] = -0.1
    elif pose == "crouch":
        Ar[1] = Ar[2] = 1.0; lean = -0.5; Ar[3] = Ar[4] = -0.6; Ar[7] = -0.6
    elif pose == "salute":           # right fist on the heart, left hand behind the back
        Ar[4] = 0.35; Ae[5] = 2.35; Ar[3] = -0.45; Ae[6] = 0.6; Ar[7] = -0.05
    elif pose in ("rifle", "aim"):
        Ar[3] = Ar[4] = 1.5; Ae[5] = Ae[6] = 0.05; lean = -0.1; Ar[7] = -0.1
    elif pose == "slash":
        Ar[1], Ar[2] = 0.6, 0.2; Ar[3] = Ar[4] = -1.9 + 2.2 * (0.5 + 0.5 * math.sin(t * 25)); Ae[5] = Ae[6] = 0.2; Ar[7] = -1.6
    elif pose == "wave":
        Ar[4] = 2.8 + 0.3 * math.sin(t * 9); Ar[7] = -0.1
    elif pose == "carry":
        Ar[3] = Ar[4] = 0.9; Ae[5] = Ae[6] = 1.3; lean = -0.15; Ar[7] = -0.2
    if pose in ("lie",):
        pass
    return Ar, Ae, lean


class Squads:
    def __init__(self, name="ODM", pscale=None):
        self.name = name
        self.pscale = PSCALE if pscale is None else pscale
        self.flyers = []
        self.by_name = {}

    def flyer(self, name, kit="cadet", hair="brown", **kw):
        f = Flyer(name, kit, hair, seed=len(self.flyers), **kw)
        self.flyers.append(f); self.by_name[name] = f
        return f

    def __getitem__(self, name):
        return self.by_name[name]

    # ---------------- build
    def build(self, coll=None, gas_dt=0.07):
        coll = coll or L.new_coll(self.name)
        self.coll = coll
        n = len(self.flyers)
        g = SW.Geo()
        fmat = []
        mats, mkey = [], {}
        def mi(key, rgb, rough=0.8):
            if key not in mkey:
                mkey[key] = len(mats); mats.append(L.mat(f"ODM_{key}", rgb, rough))
            return mkey[key]
        hips = np.zeros(n)
        for i, f in enumerate(self.flyers):
            n0 = len(g.fc)
            hips[i] = figure_geo(g, i, f.kit, f.scarf, f.rifle, f.cravat, f.H, f.moustache, f.accent is not None)
            kit = KITS[f.kit]
            look = []
            for c in CATS:
                if c == "HAIR":
                    look.append(mi("hair_" + f.hair, HAIRS[f.hair], 0.6))
                elif c == "CLOAK":
                    look.append(mi("cloak_" + f.name, f.cloak, 0.9) if f.cloak else mi("cloak_" + f.kit, kit["cloak"], 0.9))
                elif c == "ACCENT":
                    rgb = f.accent or (0.05, 0.75, 0.3)
                    key = "accent_%.2f_%.2f_%.2f" % tuple(rgb)
                    if key not in mkey:
                        m = L.mat(f"ODM_{key}", rgb, 0.5)
                        b = m.node_tree.nodes["Principled BSDF"]
                        b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = 1.6
                        mkey[key] = len(mats); mats.append(m)
                    look.append(mkey[key])
                elif c == "EM_A":
                    look.append(mi(kit["em"][0], BASE[kit["em"][0]], 0.7))
                elif c == "EM_B":
                    look.append(mi(kit["em"][1], BASE[kit["em"][1]], 0.7))
                else:
                    look.append(mi(c, BASE[c], 0.6 if c in ("skin", "steel") else 0.8))
            fmat += [look[c] for c in g.fc[n0:]]
        self.R = finish(g)
        self.hips = hips
        self.ob = SW._mesh(self.name + "_Bodies", self.R, g.f, fmat, mats, coll)
        # wires: 2 thin boxes per flyer
        wm = L.mat("ODM_wire", (0.03, 0.03, 0.035), 0.5)
        me = bpy.data.meshes.new(self.name + "_Wires")
        nw = 2 * max(n, 1)
        cube_f = [[0, 3, 2, 1], [4, 5, 6, 7], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]]
        me.from_pydata(np.zeros((nw * 8, 3)).tolist(), [], [[a + 8 * k for a in fa] for k in range(nw) for fa in cube_f])
        me.materials.append(wm); me.update()
        self.wob = bpy.data.objects.new(me.name, me); coll.objects.link(self.wob); self.wob.visible_shadow = False
        # gas puffs: precomputed from every gas-on stretch of every track
        self.gas = FX.PuffField(self.name + "_Gas", kind="steam", color=(0.93, 0.94, 0.96), alpha=0.6, grow=1.3)
        ps = self.pscale
        for i, f in enumerate(self.flyers):
            rnd = np.random.default_rng(1000 + i)
            T = [s for s in f.seg if s[0] in ("hop", "dive", "spin")]
            for s in T:
                t0, t1 = s[1], s[2]
                ts = np.arange(t0 + rnd.random() * gas_dt, t1, gas_dt)
                rows = []
                for te in ts:
                    st = f.state(te)
                    if not st["gas"]:
                        continue
                    yaw = st["yaw"]
                    back = np.array([math.sin(yaw), -math.cos(yaw), 0.0])
                    rows.append((te, st["pos"] + back * 0.4 * ps + np.array([0, 0, 0.9 * ps * f.scale])))
                if rows:
                    te = np.array([r[0] for r in rows]); P = np.array([r[1] for r in rows])
                    m = len(te)
                    self.gas.add_many(te, P + rnd.normal(0, 0.15, (m, 3)), rnd.normal(0, 0.5, (m, 3)),
                                      r0=0.25 * ps, r1=(0.75 + 0.4 * rnd.random(m)) * ps, life=1.3 + 0.6 * rnd.random(m), rise=0.3)
                # the launch burst
                st = f.state(t0 + 1e-3)
                self.gas.add_many(t0 + rnd.random(5) * 0.12, st["pos"] + rnd.normal(0, 0.4, (5, 3)) + np.array([0, 0, 0.9 * ps]),
                                  rnd.normal(0, 1.2, (5, 3)), r0=0.4 * ps, r1=1.2 * ps, life=1.6)
        self.gas.build(coll)
        self.update(-1e9)
        return self

    def state(self, name, t):
        return self.by_name[name].state(t)

    def pos(self, name, t):
        return self.by_name[name].state(t)["pos"]

    # ---------------- per frame
    def update(self, t):
        n = len(self.flyers)
        Ar = np.zeros((n, 8)); Ae = np.zeros((n, 8)); lean = np.zeros(n)
        vis = np.zeros(n); yaw = np.zeros(n); pos = np.zeros((n, 3)); pitch = np.zeros(n); roll = np.zeros(n)
        W = np.zeros((2 * max(n, 1), 8, 3))
        ps = self.pscale
        for i, f in enumerate(self.flyers):
            st = f.state(t)
            if st["vis"] <= 0:
                continue
            a, e, l = _pose_arrays(st["pose"], t, i, st)
            Ar[i], Ae[i], lean[i] = a, e, l
            vis[i] = st["vis"] * ps * f.scale
            yaw[i] = st["yaw"]; pos[i] = st["pos"]; pitch[i] = st["pitch"]; roll[i] = st["roll"]
            if st["pose"] == "lie":                       # pitched flat about the hip: drop the hip to the ground
                pitch[i] = -math.pi / 2 + 0.05
                pos[i] = pos[i] + np.array([0, 0, -(self.hips[i] - 0.12) * vis[i]])
            if st["anchors"] is not None:
                c, sn = math.cos(yaw[i]), math.sin(yaw[i])
                for k, sx in enumerate((-1, 1)):
                    hip = st["pos"] + np.array([c * 0.25 * sx, sn * 0.25 * sx, 0.0]) * vis[i] + np.array([0, 0, 0.86 * vis[i]])
                    W[2 * i + k] = _wire_box(hip, v3(st["anchors"][k]), 0.06 * ps)
        piv = self.hips * 1.0
        co = deform(self.R, Ar, Ae, lean, vis, yaw, pos, pitch, roll, piv)
        self.ob.data.vertices.foreach_set("co", co.astype(np.float32).ravel()); self.ob.data.update()
        self.wob.data.vertices.foreach_set("co", W.reshape(-1, 3).astype(np.float32).ravel()); self.wob.data.update()
        self.gas.update(t)


def _wire_box(a, b, r):
    d = b - a
    ln = np.linalg.norm(d)
    if ln < 1e-4:
        return np.zeros((8, 3))
    d = d / ln
    u = np.cross(d, [0, 0, 1.0])
    if np.linalg.norm(u) < 1e-3:
        u = np.array([1.0, 0, 0])
    u = u / np.linalg.norm(u); w = np.cross(d, u)
    c = [(-r, -r), (r, -r), (r, r), (-r, r)]
    out = [a + u * x + w * y for x, y in c] + [b + u * x + w * y for x, y in c]
    return np.array(out)
