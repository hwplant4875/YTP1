"""Signal flares and generic puff fields (smoke, gas, steam) for the sky-view timelapse. Pure functions of time.

Everything is precomputed at build time; update(t) only writes vertex positions of a few deforming meshes
(one mesh per material), so any frame renders on its own and the same t always gives the same picture.

PuffField: a pool of round puffs (low icospheres) with an emission time, start point, velocity, radius growth,
rise and life.  Used for flare smoke trails, ODM gas, titan steam, cannon smoke, pyre smoke.
    pf = PuffField("Gas", mat, detail=0)                  # detail 0 = 12-vert puffs (small), 1 = 42-vert (big)
    pf.add(te, (x, y, z), vel=(vx, vy, vz), r0=0.3, r1=1.4, life=1.6, rise=0.4)   # any number, before build()
    pf.add_many(te_array, pos_array(n,3), vel_array(n,3), r0, r1, life, rise)     # vectorised
    pf.build(coll)                                        # once
    pf.update(t)                                          # every frame

FlareSet: the Survey Corps / Garrison signal flares, canon colours: red (titan sighted / failure), green
(direction / course), yellow (operation success), black (abnormal), purple (emergency), white.
    fs = FlareSet("TrostFlares")
    fs.add(t0, (x, y, z), "red", up=120.0, lean=(4, 2), seed=1)   # z = the launch height (a wall top, a saddle)
    fs.build()                                                    # once, after all add() calls
    fs.update(t, wind=(2.0, 0.6))                                 # every frame
    fs.head_pos(i, t)                                             # flare i's burning head (for a camera / label)
A flare: a bright head shoots up (~2.4 s to `up` metres, with a slight lean), burns at the top for ~1.5 s and
fades; it leaves a thick coloured smoke trail (a puff every 0.05 s) that widens, drifts downwind and thins
out over `life` seconds (default 16).  Black smoke is dark and unlit; coloured smoke glows a little so it
reads against the town from 400 m.
emit_mat(name, rgb, strength) -> (material, strength socket) is a reusable emissive material helper.
"""
import math, random
import numpy as np
import bpy

try:
    import aotlib as L
except Exception:                       # usable outside scene.py for unit tests of the math
    L = None

COLORS = {             # linear RGB (smoke colour, head colour)
    "red":    ((0.85, 0.035, 0.02), (1.0, 0.25, 0.12)),
    "green":  ((0.05, 0.62, 0.10), (0.4, 1.0, 0.35)),
    "yellow": ((0.95, 0.72, 0.03), (1.0, 0.9, 0.35)),
    "black":  ((0.025, 0.022, 0.02), (1.0, 0.55, 0.25)),
    "purple": ((0.35, 0.05, 0.55), (0.8, 0.4, 1.0)),
    "white":  ((0.85, 0.85, 0.85), (1.0, 1.0, 1.0)),
}

def _ss(a, b, x):
    u = np.clip((x - a) / (b - a), 0.0, 1.0)
    return u * u * (3 - 2 * u)

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
    """Matte puff material; glow adds a little self-light (coloured flare smoke reads at distance)."""
    m = bpy.data.materials.get(name)
    if m is not None:
        return m
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = 1.0
    if "Specular IOR Level" in b.inputs:
        b.inputs["Specular IOR Level"].default_value = 0.0
    if glow > 0:
        b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = glow
    if alpha < 1.0:
        b.inputs["Alpha"].default_value = alpha
        if hasattr(m, "surface_render_method"):
            m.surface_render_method = "DITHERED"
    return m

def _ico(detail):
    """Unit icosphere (verts, faces) as numpy / lists."""
    t = (1 + 5 ** 0.5) / 2
    V = [(-1, t, 0), (1, t, 0), (-1, -t, 0), (1, -t, 0), (0, -1, t), (0, 1, t), (0, -1, -t), (0, 1, -t),
         (t, 0, -1), (t, 0, 1), (-t, 0, -1), (-t, 0, 1)]
    F = [(0, 11, 5), (0, 5, 1), (0, 1, 7), (0, 7, 10), (0, 10, 11), (1, 5, 9), (5, 11, 4), (11, 10, 2), (10, 7, 6),
         (7, 1, 8), (3, 9, 4), (3, 4, 2), (3, 2, 6), (3, 6, 8), (3, 8, 9), (4, 9, 5), (2, 4, 11), (6, 2, 10), (8, 6, 7), (9, 8, 1)]
    V = [np.array(v, float) / np.linalg.norm(v) for v in V]
    for _ in range(detail):
        mid = {}
        def m(a, b):
            k = (min(a, b), max(a, b))
            if k not in mid:
                p = V[a] + V[b]; V.append(p / np.linalg.norm(p)); mid[k] = len(V) - 1
            return mid[k]
        F2 = []
        for a, b, c in F:
            ab, bc, ca = m(a, b), m(b, c), m(c, a)
            F2 += [(a, ab, ca), (b, bc, ab), (c, ca, bc), (ab, bc, ca)]
        F = F2
    return np.array(V), F


class PuffField:
    """Pool of puffs; see the module doc."""
    def __init__(self, name, mat, detail=0, squash=1.0):
        self.name, self.mat, self.detail, self.squash = name, mat, detail, squash
        self._rows = []
        self.ob = None

    def add(self, te, pos, vel=(0, 0, 0), r0=0.3, r1=1.2, life=2.0, rise=0.0, fade_in=0.08):
        self._rows.append((te, *pos, *vel, r0, r1, life, rise, fade_in))

    def add_many(self, te, pos, vel=None, r0=0.3, r1=1.2, life=2.0, rise=0.0, fade_in=0.08):
        te = np.asarray(te, float); n = len(te)
        if n == 0:
            return
        pos = np.asarray(pos, float).reshape(n, 3)
        vel = np.zeros((n, 3)) if vel is None else np.asarray(vel, float).reshape(n, 3)
        bc = lambda v: np.broadcast_to(np.asarray(v, float), (n,))
        rows = np.column_stack([te, pos, vel, bc(r0), bc(r1), bc(life), bc(rise), bc(fade_in)])
        self._rows.extend(map(tuple, rows))

    def build(self, coll=None):
        A = np.array(self._rows, float).reshape(-1, 12) if self._rows else np.zeros((0, 12))
        self.A = A
        n = len(A)
        tv, tf = _ico(self.detail)
        tv = tv * np.array([1.0, 1.0, self.squash])
        self.tv = tv; nv = len(tv)
        me = bpy.data.meshes.new(self.name)
        verts = np.zeros((max(n, 1) * nv, 3))
        faces = [[a + k * nv, b + k * nv, c + k * nv] for k in range(max(n, 1)) for a, b, c in tf]
        me.from_pydata(verts.tolist(), [], faces)
        me.materials.append(self.mat)
        me.polygons.foreach_set("use_smooth", np.ones(len(me.polygons), bool))
        me.update()
        self.ob = bpy.data.objects.new(self.name, me)
        (coll or bpy.context.scene.collection).objects.link(self.ob)
        self.ob.visible_shadow = False
        self.n, self.nv = max(n, 1), nv
        self.update(-1e9)
        return self.ob

    def update(self, t):
        A = self.A
        if len(A) == 0:
            self.ob.hide_render = True
            return
        age = t - A[:, 0]
        life = A[:, 9]
        alive = (age >= 0) & (age < life)
        if not alive.any():
            self.ob.hide_render = self.ob.hide_viewport = True
            return
        self.ob.hide_render = self.ob.hide_viewport = False
        u = np.clip(age / life, 0, 1)
        r = (A[:, 7] + (A[:, 8] - A[:, 7]) * np.sqrt(u)) * _ss(0.0, np.maximum(A[:, 11], 1e-3) / life, u) * (1 - _ss(0.7, 1.0, u))
        r = np.where(alive, r, 0.0)
        c = A[:, 1:4] + A[:, 4:7] * age[:, None]
        c[:, 2] += A[:, 10] * age
        # ease the initial velocity off (puffs decelerate in air): x = v * tau * (1 - exp(-age / tau)) / age approx
        co = (c[:, None, :] + self.tv[None, :, :] * r[:, None, None]).reshape(-1, 3)
        co[np.repeat(~alive, self.nv)] = 0.0
        self.ob.data.vertices.foreach_set("co", co.astype(np.float32).ravel())
        self.ob.data.update()


class FlareSet:
    """Signal flares; see the module doc."""
    BURN = 2.4           # s from launch to the top
    TOP_HOLD = 1.6       # s the head keeps burning at the top
    def __init__(self, name="Flares", coll=None):
        self.name = name; self.coll = coll
        self.fl = []
        self.fields = {}
        self.heads = []

    def add(self, t0, pos, color="red", up=120.0, lean=None, seed=None, life=16.0, width=1.0):
        rnd = random.Random(seed if seed is not None else len(self.fl) * 7 + 3)
        if lean is None:
            lean = (rnd.uniform(-6, 6), rnd.uniform(-6, 6))
        self.fl.append(dict(t0=float(t0), p=np.array(pos, float), color=color, up=float(up), lean=np.array(lean, float),
                            life=float(life), width=float(width), seed=rnd.randrange(1 << 30)))
        return len(self.fl) - 1

    def path(self, f, tau):
        """Head position tau seconds after launch."""
        T = self.BURN
        u = min(max(tau / T, 0.0), 1.0)
        h = f["up"] * (1 - (1 - u) ** 2)                  # decelerating climb
        if tau > T:
            h -= 0.9 * (tau - T) ** 2                     # slowly sinks after burnout
        return f["p"] + np.array([f["lean"][0] * u, f["lean"][1] * u, h])

    def build(self, coll=None):
        coll = coll or self.coll or (L.new_coll(self.name) if L else bpy.context.scene.collection)
        self.coll = coll
        for col in {f["color"] for f in self.fl}:
            rgb = COLORS[col][0]
            glow = 0.0 if col == "black" else 0.9
            self.fields[col] = PuffField(f"{self.name}_{col}", smoke_mat(f"FlareSmoke_{col}", rgb, glow), detail=1)
        for i, f in enumerate(self.fl):
            rnd = np.random.default_rng(f["seed"])
            n = int(self.BURN / 0.05)
            taus = np.arange(n) * 0.05
            P = np.array([self.path(f, tau) for tau in taus])
            te = f["t0"] + taus
            jit = rnd.normal(0, 0.25, (n, 3))
            w = f["width"]
            self.fields[f["color"]].add_many(te, P + jit, rnd.normal(0, 0.15, (n, 3)), r0=0.7 * w, r1=(4.2 + 1.4 * rnd.random(n)) * w,
                                             life=f["life"] * (0.8 + 0.4 * rnd.random(n)), rise=0.25, fade_in=0.05)
            # a fatter ball of smoke where the head burns at the top
            m = 14
            top = self.path(f, self.BURN)
            self.fields[f["color"]].add_many(f["t0"] + self.BURN + rnd.random(m) * self.TOP_HOLD, top + rnd.normal(0, 1.2, (m, 3)),
                                             rnd.normal(0, 0.4, (m, 3)), r0=1.0 * w, r1=5.5 * w, life=f["life"], rise=0.2)
            hm, hs = emit_mat(f"FlareHead_{f['color']}", COLORS[f["color"]][1], 40.0)
            bm_v, bm_f = _ico(1)
            me = bpy.data.meshes.new(f"{self.name}_Head{i}")
            me.from_pydata((bm_v * 0.9).tolist(), [], bm_f); me.materials.append(hm)
            ob = bpy.data.objects.new(me.name, me); coll.objects.link(ob); ob.visible_shadow = False
            self.heads.append(ob)
        for pf in self.fields.values():
            pf.build(coll)
        self.wind = np.zeros(3)
        return self

    def head_pos(self, i, t):
        f = self.fl[i]
        return self.path(f, t - f["t0"])

    def update(self, t, wind=(1.8, 0.6)):
        wind = np.array([wind[0], wind[1], 0.0])
        for pf in self.fields.values():
            # wind drift: shift the whole field's start points by wind * age via a temporary velocity offset
            A = pf.A
            if len(A):
                if not hasattr(pf, "_v0"):
                    pf._v0 = A[:, 4:7].copy()
                A[:, 4:7] = pf._v0 + wind
            pf.update(t)
        for i, (f, ob) in enumerate(zip(self.fl, self.heads)):
            tau = t - f["t0"]
            on = 0.0 <= tau < self.BURN + self.TOP_HOLD
            ob.hide_render = ob.hide_viewport = not on
            if on:
                ob.location = tuple(self.path(f, tau))
                k = 1.0 + 0.25 * math.sin(tau * 53.0 + i)
                fade = 1.0 - max(0.0, (tau - self.BURN) / self.TOP_HOLD)
                s = (1.2 + 0.6 * (f["width"] - 1)) * k * max(0.2, fade)
                ob.scale = (s, s, s)
