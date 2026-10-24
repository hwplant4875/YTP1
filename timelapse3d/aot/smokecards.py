"""Soft camera-facing smoke / steam / dust / fire CARDS (billboards) for Eevee and Cycles. Pure functions of time.

One mesh per kind holds every card as a quad.  update(t) evaluates each card (position, radius, in-plane rotation,
alpha, tint) from its emission parameters, then orient(cam) writes the quads facing the camera, sorted back to front
(so Eevee's alpha blending composites correctly).  A render_pre handler re-orients every card set to the scene camera
just before each render, so callers may move the camera after update().
Shader: procedural 4D noise (per-card seed) x a soft radial falloff = wispy soft-edged alpha; smoke kinds are lit
(diffuse) plus a little self-light, fire / glow kinds are emissive.  Eevee: BLENDED; Cycles: transparent bounces.

API
    import smokecards as SC
    cs = SC.SmokeCards("Steam")
    cs.add(te, (x, y, z), vel=(0, 0, 0), r0=0.5, r1=3, life=3, rise=1.5, color=None, kind="steam",
           alpha=0.8, tau=0.0, spin=None, fade_in=0.1)          # tau > 0: initial velocity decays with time constant tau
    cs.add_many(te_array, pos (n,3), vel (n,3) | None, r0, r1, life, rise, color=None|(n,3)|rgb, kind, alpha, tau)
    cs.build(coll)                     # once
    cs.update(t, cam=None, wind=(0, 0))  # every frame (cam defaults to the scene camera)
Kinds: smoke (grey), steam (white), dust (warm brown-grey), fire (orange, emissive, flickers), flare_trail (coloured
wispy flare smoke, slightly self-lit), glow (soft radial emissive halo, no noise).
"""
import math
import numpy as np
import bpy

KINDS = {
    #            default colour            emit  noise thr  noise scale  lit
    "smoke":       dict(col=(0.36, 0.34, 0.31), emit=0.10, thr=0.30, ns=2.0, lit=True),
    "steam":       dict(col=(0.92, 0.92, 0.90), emit=0.40, thr=0.28, ns=1.8, lit=True),
    "dust":        dict(col=(0.46, 0.37, 0.25), emit=0.18, thr=0.30, ns=2.2, lit=True),
    "fire":        dict(col=(1.00, 0.42, 0.08), emit=9.0, thr=0.25, ns=2.6, lit=False),
    "flare_trail": dict(col=(0.85, 0.05, 0.03), emit=0.6, thr=0.18, ns=1.4, lit=True),
    "glow":        dict(col=(1.00, 0.60, 0.30), emit=14.0, thr=None, ns=1.0, lit=False),
}
_ALL = []
COLS = 24       # ... 20-22 stretch direction | 23 stretch factor (1 = round billboard)

def _ss(a, b, x):
    u = np.clip((x - a) / (b - a), 0.0, 1.0)
    return u * u * (3 - 2 * u)

def card_mat(kind):
    name = f"SC_{kind}"
    m = bpy.data.materials.get(name)
    if m is not None:
        return m
    K = KINDS[kind]
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; N = nt.nodes; Ln = nt.links
    N.remove(N["Principled BSDF"])
    def mth(op, a, b=None, clamp=False):
        n = N.new("ShaderNodeMath"); n.operation = op; n.use_clamp = clamp
        for i, x in enumerate((a, b)):
            if x is None:
                continue
            if isinstance(x, (int, float)):
                n.inputs[i].default_value = x
            else:
                Ln.new(x, n.inputs[i])
        return n.outputs[0]
    uv = N.new("ShaderNodeUVMap"); uv.uv_map = "UVMap"
    col = N.new("ShaderNodeAttribute"); col.attribute_name = "sc_col"
    seed = N.new("ShaderNodeAttribute"); seed.attribute_name = "sc_seed"
    sep = N.new("ShaderNodeSeparateXYZ"); Ln.new(uv.outputs["UV"], sep.inputs[0])
    dx = mth("SUBTRACT", sep.outputs[0], 0.5); dy = mth("SUBTRACT", sep.outputs[1], 0.5)
    d = mth("SQRT", mth("ADD", mth("MULTIPLY", dx, dx), mth("MULTIPLY", dy, dy)))
    radial = mth("SUBTRACT", 1.0, mth("MULTIPLY", d, 2.0), True)          # 1 centre .. 0 rim
    if K["thr"] is None:
        dens = mth("POWER", radial, 2.2)
    else:
        nz = N.new("ShaderNodeTexNoise"); nz.noise_dimensions = "4D"
        nz.inputs["Scale"].default_value = K["ns"]; nz.inputs["Detail"].default_value = 5.0
        nz.inputs["Roughness"].default_value = 0.62; nz.inputs["Distortion"].default_value = 0.35
        Ln.new(uv.outputs["UV"], nz.inputs["Vector"])
        Ln.new(mth("MULTIPLY", seed.outputs["Fac"], 7.31), nz.inputs["W"])
        soft = mth("POWER", radial, 1.1)
        # noise lifts the density near the centre and eats the edges -> irregular soft billow outline
        dens = mth("MULTIPLY", mth("SUBTRACT", mth("ADD", mth("MULTIPLY", nz.outputs["Fac"], 1.0), mth("MULTIPLY", soft, 0.85)), K["thr"] + 0.55), 2.2, True)
        dens = mth("MULTIPLY", dens, mth("POWER", radial, 0.5), True)
    alpha = mth("MULTIPLY", dens, col.outputs["Alpha"], True)
    em = N.new("ShaderNodeEmission"); Ln.new(col.outputs["Color"], em.inputs["Color"]); em.inputs["Strength"].default_value = K["emit"]
    if K["lit"]:
        dif = N.new("ShaderNodeBsdfDiffuse"); Ln.new(col.outputs["Color"], dif.inputs["Color"])
        sh = N.new("ShaderNodeAddShader"); Ln.new(dif.outputs[0], sh.inputs[0]); Ln.new(em.outputs[0], sh.inputs[1])
        surf = sh.outputs[0]
    else:
        surf = em.outputs[0]
    tr = N.new("ShaderNodeBsdfTransparent")
    mx = N.new("ShaderNodeMixShader")
    Ln.new(alpha, mx.inputs[0]); Ln.new(tr.outputs[0], mx.inputs[1]); Ln.new(surf, mx.inputs[2])
    Ln.new(mx.outputs[0], N["Material Output"].inputs["Surface"])
    for a, v in (("surface_render_method", "BLENDED"), ("blend_method", "BLEND"), ("use_backface_culling", False),
                 ("shadow_method", "NONE"), ("use_transparent_shadow", True)):
        try:
            setattr(m, a, v)
        except (AttributeError, TypeError):
            pass
    return m


class _Pool:
    def __init__(self, owner, kind):
        self.owner, self.kind = owner, kind
        self.rows = []
        self.ob = None

    def build(self, coll):
        A = np.array(self.rows, float).reshape(-1, COLS) if self.rows else np.zeros((0, COLS))
        self.A = A
        n = max(len(A), 1)
        self.n = n
        me = bpy.data.meshes.new(f"{self.owner.name}_{self.kind}")
        me.vertices.add(4 * n)
        me.loops.add(4 * n)
        me.polygons.add(n)
        me.loops.foreach_set("vertex_index", np.arange(4 * n, dtype=np.int32))
        me.polygons.foreach_set("loop_start", np.arange(0, 4 * n, 4, dtype=np.int32))
        me.polygons.foreach_set("loop_total", np.full(n, 4, np.int32))
        uvl = me.uv_layers.new(name="UVMap")
        uvl.data.foreach_set("uv", np.tile([0, 0, 1, 0, 1, 1, 0, 1], n).astype(np.float32))
        me.color_attributes.new("sc_col", "FLOAT_COLOR", "POINT")
        me.attributes.new("sc_seed", "FLOAT", "POINT")
        me.materials.append(card_mat(self.kind))
        me.update()
        ob = bpy.data.objects.new(me.name, me)
        (coll or bpy.context.scene.collection).objects.link(ob)
        for a in ("visible_shadow", "visible_diffuse", "visible_glossy", "visible_transmission", "visible_volume_scatter"):
            try:
                setattr(ob, a, False)
            except AttributeError:
                pass
        self.ob = ob
        self.state = None

    def evaluate(self, t, wind):
        # columns: 0 te | 1-3 pos | 4-6 vel | 7 r0 | 8 r1 | 9 life | 10 rise | 11 tau | 12 alpha | 13-15 rgb | 16 rot0 | 17 spin | 18 seed | 19 fade_in
        A = self.A
        if len(A) == 0:
            self.state = None; return
        age = t - A[:, 0]; life = A[:, 9]
        alive = (age >= 0) & (age < life)
        if not alive.any():
            self.state = None; return
        idx = np.where(alive)[0]
        B = A[idx]; ag = age[idx]; u = ag / B[:, 9]
        tau = B[:, 11]
        disp = np.where(tau[:, None] > 0, B[:, 4:7] * (tau * (1 - np.exp(-ag / np.maximum(tau, 1e-6))))[:, None], B[:, 4:7] * ag[:, None])
        c = B[:, 1:4] + disp
        c[:, 0] += wind[0] * ag; c[:, 1] += wind[1] * ag
        c[:, 2] += B[:, 10] * ag
        r = B[:, 7] + (B[:, 8] - B[:, 7]) * (1 - (1 - np.minimum(1.0, u / 0.8)) ** 2)
        a = B[:, 12] * _ss(0.0, np.maximum(B[:, 19], 1e-3), ag) * (1 - _ss(0.0, 1.0, u)) ** 1.2
        if self.kind == "fire":
            fl = 0.75 + 0.25 * np.sin(t * 31.0 + B[:, 18] * 40.0) * np.sin(t * 17.0 + B[:, 18] * 13.0)
            a = a * fl; r = r * (0.9 + 0.1 * fl)
        rot = B[:, 16] + B[:, 17] * ag
        self.state = (c, r, rot, a, B[:, 13:16], B[:, 18], B[:, 20:23], B[:, 23])

    def orient(self, cam):
        if self.ob is None:
            return
        if self.state is None:                     # nothing alive: hide (and remember that we did)
            if not self.ob.hide_render:
                self.ob.hide_render = self.ob.hide_viewport = True
                self._auto_hidden = True
            return
        if getattr(self, "_auto_hidden", False):   # only undo our own hiding; callers may hide the object too
            self.ob.hide_render = self.ob.hide_viewport = False
            self._auto_hidden = False
        c, r, rot, a, col, seed, dvec, stretch = self.state
        M = cam.matrix_world
        R = np.array(M.col[0][:3]); U = np.array(M.col[1][:3]); P = np.array(M.col[3][:3])
        order = np.argsort(-np.einsum("ij,ij->i", c - P, c - P))           # far first: Eevee blends back to front
        c, r, rot, a, col, seed, dvec, stretch = (c[order], r[order], rot[order], a[order], col[order], seed[order],
                                                  dvec[order], stretch[order])
        m = len(c); n = self.n
        cs, sn = np.cos(rot), np.sin(rot)
        e1 = cs[:, None] * R + sn[:, None] * U
        e2 = -sn[:, None] * R + cs[:, None] * U
        st = stretch > 1.001                                               # streak cards: long axis along dvec on screen
        if st.any():
            Vd = np.cross(R, U)
            dp = dvec[st] - (dvec[st] @ Vd)[:, None] * Vd
            ln = np.linalg.norm(dp, axis=1, keepdims=True)
            ok = ln[:, 0] > 1e-6
            dp = np.where(ok[:, None], dp / np.maximum(ln, 1e-9), U)
            e1[st] = dp * stretch[st][:, None]
            e2[st] = np.cross(Vd, dp)
        e1 *= r[:, None]; e2 *= r[:, None]
        V = np.zeros((n, 4, 3))
        V[:m, 0] = c - e1 - e2; V[:m, 1] = c + e1 - e2; V[:m, 2] = c + e1 + e2; V[:m, 3] = c - e1 + e2
        if m < n:
            V[m:] = c[0]                                                   # unused slots collapse to a point
        Cc = np.zeros((n, 4, 4)); Cc[:m, :, :3] = col[:, None, :]; Cc[:m, :, 3] = a[:, None]
        S = np.zeros((n, 4)); S[:m] = seed[:, None]
        me = self.ob.data
        me.vertices.foreach_set("co", V.reshape(-1).astype(np.float32))
        me.color_attributes["sc_col"].data.foreach_set("color", Cc.reshape(-1).astype(np.float32))
        me.attributes["sc_seed"].data.foreach_set("value", S.reshape(-1).astype(np.float32))
        me.update()


class SmokeCards:
    def __init__(self, name="Cards"):
        self.name = name
        self.pools = {}
        self.wind = (0.0, 0.0)
        self._rng = np.random.default_rng(abs(hash(name)) % (2 ** 31))
        _ALL.append(self)

    def _pool(self, kind):
        if kind not in self.pools:
            self.pools[kind] = _Pool(self, kind)
        return self.pools[kind]

    def add(self, te, pos, vel=(0, 0, 0), r0=0.5, r1=2.0, life=3.0, rise=0.0, color=None, kind="smoke", alpha=0.8,
            tau=0.0, spin=None, fade_in=0.1):
        self.add_many([te], [pos], [vel], r0, r1, life, rise, color, kind, alpha, tau, spin, fade_in)

    def add_many(self, te, pos, vel=None, r0=0.5, r1=2.0, life=3.0, rise=0.0, color=None, kind="smoke", alpha=0.8,
                 tau=0.0, spin=None, fade_in=0.1, dirs=None, stretch=1.0):
        te = np.asarray(te, float).reshape(-1); n = len(te)
        if n == 0:
            return
        pos = np.asarray(pos, float).reshape(n, 3)
        vel = np.zeros((n, 3)) if vel is None else np.asarray(vel, float).reshape(n, 3)
        bc = lambda v: np.broadcast_to(np.asarray(v, float), (n,)).astype(float)
        if color is None:
            color = KINDS[kind]["col"]
        col = np.asarray(color, float)
        col = np.broadcast_to(col, (n, 3)) if col.ndim == 1 else col.reshape(n, 3)
        rng = self._rng
        rot0 = rng.uniform(0, math.tau, n)
        sp = rng.uniform(-0.35, 0.35, n) if spin is None else bc(spin)
        seed = rng.uniform(0, 100, n)
        dv = np.zeros((n, 3)) if dirs is None else np.asarray(dirs, float).reshape(n, 3)
        rows = np.column_stack([te, pos, vel, bc(r0), bc(r1), bc(life), bc(rise), bc(tau), bc(alpha), col, rot0, sp, seed, bc(fade_in),
                                dv, bc(stretch)])
        self._pool(kind).rows.extend(map(tuple, rows))

    def count(self):
        return sum(len(p.rows) for p in self.pools.values())

    def build(self, coll=None):
        for p in self.pools.values():
            p.build(coll)
        sc = bpy.context.scene
        try:
            sc.cycles.transparent_max_bounces = max(sc.cycles.transparent_max_bounces, 64)
        except AttributeError:
            pass
        _install_handler()
        return self

    def update(self, t, cam=None, wind=None):
        if wind is not None:
            self.wind = wind
        cam = cam or bpy.context.scene.camera
        for p in self.pools.values():
            p.evaluate(float(t), self.wind)
            if cam is not None:
                p.orient(cam)

    def orient(self, cam):
        for p in self.pools.values():
            p.orient(cam)

    def objects(self):
        return [p.ob for p in self.pools.values() if p.ob]


def orient_all(cam=None):
    cam = cam or bpy.context.scene.camera
    if cam is None:
        return
    for s in list(_ALL):
        try:
            s.orient(cam)
        except ReferenceError:
            _ALL.remove(s)

def _pre_render(scene, *_):
    orient_all(scene.camera)

def _install_handler():
    hs = bpy.app.handlers.render_pre
    if not any(getattr(h, "__name__", "") == "_sc_pre_render" for h in hs):
        def _sc_pre_render(scene, *a):
            _pre_render(scene)
        hs.append(_sc_pre_render)
