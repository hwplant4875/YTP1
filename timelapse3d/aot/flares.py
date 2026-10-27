"""Signal flares and puff fields (smoke, gas, steam) for the sky-view timelapse. Pure functions of time.

Since 2026-10-25 everything renders as soft camera-facing smoke CARDS (aot/smokecards.py): procedural-noise alpha,
soft edges, per-card rotation, growth and fade.  The old opaque icosphere puffs are gone (FLARE_PUFFS=spheres is not
kept; the cards work in both Eevee and Cycles).

PuffField (compat wrapper over SmokeCards, same API as before):
    pf = PuffField("Gas", mat=None, kind="steam", color=None)   # colour defaults to the kind's, or the mat's base colour
    pf.add(te, (x, y, z), vel=(vx, vy, vz), r0=0.3, r1=1.4, life=1.6, rise=0.4)
    pf.add_many(te_array, pos_array(n,3), vel_array(n,3), r0, r1, life, rise, alpha=0.75)
    pf.build(coll); pf.update(t)
  Each puff becomes one card ~1.5x the old sphere radius (the soft falloff eats the edge).

FlareSet: the signal flares, canon colours: red (titan sighted / failure), green (direction / course), yellow
(operation success), black (abnormal), purple (emergency), white.
    fs = FlareSet("TrostFlares")
    fs.add(t0, (x, y, z), "red", up=120.0, lean=(4, 2), seed=1)   # z = launch height (a wall top, a saddle)
    fs.build(); fs.update(t, wind=(2.0, 0.6)); fs.head_pos(i, t)
A flare: a small white-hot core with a big soft coloured glow shoots up (~2.4 s to `up` m), burns at the top ~1.6 s
and fades; it leaves a thin wispy trail of coloured smoke (a card every 0.03 s) that widens, drifts downwind and
thins out over `life` seconds.  Black smoke is dark and unlit.
emit_mat(name, rgb, strength) -> (material, strength socket); smoke_mat() is kept for old callers.
"""
import math, random
import numpy as np
import bpy

try:
    import aotlib as L
except Exception:
    L = None
import smokecards as SC

COLORS = {             # linear RGB (smoke colour, head/glow colour)
    "red":    ((0.80, 0.045, 0.03), (1.0, 0.18, 0.08)),
    "green":  ((0.06, 0.55, 0.12), (0.35, 1.0, 0.3)),
    "green_vivid": ((0.02, 0.85, 0.08), (0.25, 1.0, 0.2)),   # g8 after the plug (owner 10/27: clearly GREEN under the dusk grade)
    "yellow": ((0.92, 0.70, 0.05), (1.0, 0.85, 0.3)),
    "black":  ((0.03, 0.028, 0.026), (1.0, 0.5, 0.2)),
    "purple": ((0.35, 0.06, 0.55), (0.75, 0.35, 1.0)),
    "white":  ((0.85, 0.85, 0.85), (1.0, 1.0, 1.0)),
}

def emit_mat(name, rgb, strength):
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name); m.use_nodes = True
        nt = m.node_tree; N = nt.nodes; N.remove(N["Principled BSDF"])
        em = N.new("ShaderNodeEmission"); em.inputs["Color"].default_value = (*rgb, 1)
        em.inputs["Strength"].default_value = strength
        nt.links.new(em.outputs[0], N["Material Output"].inputs["Surface"])
    em = next(n for n in m.node_tree.nodes if n.type == "EMISSION")
    return m, em.inputs["Strength"]

def smoke_mat(name, rgb, glow=0.0, alpha=1.0):
    """Kept for old callers: a plain material whose base colour PuffField reads as the card tint."""
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name); m.use_nodes = True
        b = m.node_tree.nodes["Principled BSDF"]; b.inputs["Base Color"].default_value = (*rgb, 1)
    return m

def _mat_rgb(m):
    try:
        b = m.node_tree.nodes["Principled BSDF"]; return tuple(b.inputs["Base Color"].default_value[:3])
    except Exception:
        return None


class PuffField:
    def __init__(self, name, mat=None, detail=0, squash=1.0, kind=None, color=None, alpha=0.75, grow=1.5):
        self.name = name
        rgb = color or (_mat_rgb(mat) if mat is not None else None)
        if kind is None:
            kind = "steam" if (rgb is None or min(rgb) > 0.6) else "smoke"
        self.kind, self.rgb, self.alpha, self.grow = kind, rgb, alpha, grow
        self.cards = SC.SmokeCards(name)
        self.n = 0

    def add(self, te, pos, vel=(0, 0, 0), r0=0.3, r1=1.2, life=2.0, rise=0.0, fade_in=0.08, alpha=None):
        self.add_many([te], [pos], [vel], r0, r1, life, rise, fade_in, alpha)

    def add_many(self, te, pos, vel=None, r0=0.3, r1=1.2, life=2.0, rise=0.0, fade_in=0.08, alpha=None):
        te = np.asarray(te, float).reshape(-1)
        if len(te) == 0:
            return
        g = self.grow
        self.cards.add_many(te, pos, vel, np.asarray(r0, float) * g, np.asarray(r1, float) * g, life, rise,
                            color=self.rgb, kind=self.kind, alpha=self.alpha if alpha is None else alpha, fade_in=fade_in)
        self.n += len(te)

    def build(self, coll=None):
        self.cards.build(coll)
        self.update(-1e9)
        return self

    def update(self, t, wind=None):
        self.cards.update(t, wind=wind)


class FlareSet:
    BURN = 2.4           # s from launch to the top
    TOP_HOLD = 1.6       # s the head keeps burning at the top
    def __init__(self, name="Flares", coll=None):
        self.name = name; self.coll = coll
        self.fl = []
        self.heads = []

    def add(self, t0, pos, color="red", up=120.0, lean=None, seed=None, life=16.0, width=1.0):
        rnd = random.Random(seed if seed is not None else len(self.fl) * 7 + 3)
        if lean is None:
            lean = (rnd.uniform(-6, 6), rnd.uniform(-6, 6))
        self.fl.append(dict(t0=float(t0), p=np.array(pos, float), color=color, up=float(up), lean=np.array(lean, float),
                            life=float(life), width=float(width), seed=rnd.randrange(1 << 30)))
        return len(self.fl) - 1

    def path(self, f, tau):
        T = self.BURN
        u = min(max(tau / T, 0.0), 1.0)
        h = f["up"] * (1 - (1 - u) ** 2)
        if tau > T:
            h -= 0.9 * (tau - T) ** 2
        return f["p"] + np.array([f["lean"][0] * u, f["lean"][1] * u, h])

    def build(self, coll=None):
        coll = coll or self.coll or (L.new_coll(self.name) if L else bpy.context.scene.collection)
        self.coll = coll
        self.cards = SC.SmokeCards(self.name)
        for i, f in enumerate(self.fl):
            rnd = np.random.default_rng(f["seed"])
            smoke, glow = COLORS[f["color"]]
            kind = "smoke" if f["color"] == "black" else "flare_trail"
            w = f["width"]
            # one continuous soft streak: dense, overlapping cards stretched along the path tangent, widening with age
            dt = 0.012
            taus = np.arange(0.05, self.BURN + self.TOP_HOLD, dt)
            P = np.array([self.path(f, tau) for tau in taus]); n = len(taus)
            D = np.gradient(P, axis=0)
            self.cards.add_many(f["t0"] + taus, P + rnd.normal(0, 0.06, (n, 3)), rnd.normal(0, 0.12, (n, 3)),
                                r0=0.45 * w, r1=(2.2 + 1.2 * rnd.random(n)) * w, life=f["life"] * (0.8 + 0.4 * rnd.random(n)),
                                rise=0.12, color=smoke, kind=kind, alpha=0.32 if kind != "smoke" else 0.38, fade_in=0.04,
                                dirs=D, stretch=3.0, spin=0.0)
            # a few round billows along it so the widened trail still has some body
            k = slice(None, None, 9)
            self.cards.add_many(f["t0"] + taus[k], P[k], rnd.normal(0, 0.3, (len(taus[k]), 3)), r0=0.6 * w, r1=3.4 * w,
                                life=f["life"] * 0.9, rise=0.15, color=smoke, kind=kind, alpha=0.25, fade_in=0.08)
            # the burning head: a short-lived glow card re-emitted along the path (follows the head, pure in t)
            taus = np.arange(0.0, self.BURN + self.TOP_HOLD, 0.03); n = len(taus)
            P = np.array([self.path(f, tau) for tau in taus])
            fade = np.clip(1.0 - (taus - self.BURN) / self.TOP_HOLD, 0.15, 1.0)
            self.cards.add_many(f["t0"] + taus, P, None, r0=3.2 * w, r1=3.6 * w, life=0.09, rise=0.0, color=glow, kind="glow",
                                alpha=fade, fade_in=0.001)
            hm, hs = emit_mat(f"FlareCore_{f['color']}", tuple(min(1.0, c * 0.4 + 0.6) for c in glow), 60.0)
            me = bpy.data.meshes.new(f"{self.name}_Core{i}")
            import bmesh
            bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=6, radius=0.6); bm.to_mesh(me); bm.free()
            me.materials.append(hm)
            for p in me.polygons:
                p.use_smooth = True
            ob = bpy.data.objects.new(me.name, me); coll.objects.link(ob); ob.visible_shadow = False
            self.heads.append(ob)
        self.cards.build(coll)
        return self

    def head_pos(self, i, t):
        f = self.fl[i]
        return self.path(f, t - f["t0"])

    def update(self, t, wind=(1.8, 0.6)):
        self.cards.update(t, wind=(wind[0], wind[1]))
        for i, (f, ob) in enumerate(zip(self.fl, self.heads)):
            tau = t - f["t0"]
            on = 0.0 <= tau < self.BURN + self.TOP_HOLD
            ob.hide_render = ob.hide_viewport = not on
            if on:
                ob.location = tuple(self.path(f, tau))
                k = 1.0 + 0.2 * math.sin(tau * 53.0 + i)
                fade = 1.0 - max(0.0, (tau - self.BURN) / self.TOP_HOLD)
                s = k * max(0.25, fade) * f["width"]
                ob.scale = (s, s, s)
