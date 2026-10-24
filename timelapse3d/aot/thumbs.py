"""Thumbnail candidate cameras + per-shot dressing for the AoT S1 3D timelapse (PREVIEW stills only).

Plug-in for scene.py, meant to run LAST together with the other 845 plug-ins:
    AOT_PLUGINS=cast845,states845,flight,thumbs AOT_EVENT=... AOT_STATE=... bash render.sh <cam> out.png 960x540 32

Cameras (and the plug-in state each one is designed for):
    thumb_colossal   AOT_EVENT=colossal AOT_STATE=intact   MAIN: the Colossal's head + hand over the south wall,
                                                           seen from a rooftop inside the town, low backlit sun
    thumb_colossal_back  same state                         alt: over-the-shoulder like the S1E1 still (looking north)
    thumb_overview   AOT_EVENT=colossal AOT_STATE=kicked   high oblique of the U, hill-tree foliage framing the top left
    thumb_armored    AOT_EVENT=armored  AOT_STATE=armored  the Armored bursting north through the inner gate
    thumb_night      AOT_EVENT=armored  AOT_STATE=night    titan silhouettes in the burning town, from the inner wall

build() only changes things when the scene's --cam is one of these cameras, so enabling the module costs
nothing for other shots.  Tuning env vars: TH_LOC / TH_TGT ("x,y,z" absolute) or TH_OFF ("dx,dy,dz" relative
to the cam's anchor), TH_LENS, TH_SUN_AZ, TH_SUN_EL, TH_SUN_E.

Title overlay (system python with Pillow, no Blender):
    python thumbs.py title in.png out.png "SHIGANSHINA" "845" "THROUGH EREN'S EYES"
"""
import math, os, random, sys

try:
    import bpy, bmesh
    from mathutils import Vector
    import aotlib as L
except ImportError:          # plain python: only the title overlay is available
    bpy = None

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(os.path.dirname(HERE), "fonts")


LOGF = os.environ.get("TH_LOG", "")


def log(*a):
    print("[thumbs]", *a, flush=True)
    if LOGF:
        with open(LOGF, "a", encoding="utf8") as fh:
            fh.write(" ".join(str(x) for x in a) + chr(10))


def _vec(name, default):
    s = os.environ.get(name)
    return tuple(float(v) for v in s.split(",")) if s else default


def _f(name, default):
    return float(os.environ.get(name, default))


if bpy is not None:
    CAM = (getattr(getattr(L, "A", None), "cam", "") or "")
    SHOT = CAM if CAM.startswith("thumb_") else ""

    def cast():
        return sys.modules.get("cast845")

    def cast_state(key):
        c = cast()
        return c.STATE.get(key) if c and hasattr(c, "STATE") else None

    # ------------------------------------------------------------------ lighting
    def set_sun(ctx, az, el, color=(1, 1, 1), energy=None, sky=None, haze=None, haze_mul=None):
        """az: compass angle of the sun position (deg, scene.py convention: sun at (cos az, sin az)), el: elevation."""
        so = ctx.get("sun")
        if so:
            a, e = math.radians(az), math.radians(el)
            d = Vector((-math.cos(e) * math.cos(a), -math.cos(e) * math.sin(a), -math.sin(e)))
            so.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
            so.data.color = color
            if energy is not None:
                so.data.energy = energy
        w = ctx.get("world")
        if w:
            for n in w.node_tree.nodes:
                if n.type == "TEX_SKY":
                    try:
                        n.sun_elevation = math.radians(max(el, 1)); n.sun_rotation = math.radians(az)
                    except Exception:
                        pass
                if n.type == "VALTORGB" and sky:
                    e = n.color_ramp.elements
                    e[0].color = (*sky[0], 1); e[1].color = (*sky[1], 1)
                    if len(sky) > 2:
                        e[1].position = sky[2]
        hz = bpy.data.objects.get("Haze")
        if hz and hz.data.materials and (haze or haze_mul):
            pv = next((n for n in hz.data.materials[0].node_tree.nodes if n.type == "PRINCIPLED_VOLUME"), None)
            if pv:
                if haze:
                    pv.inputs["Color"].default_value = (*haze, 1)
                if haze_mul:
                    pv.inputs["Density"].default_value *= haze_mul

    # ------------------------------------------------------------------ helpers
    def steam(name, c, size, dens, noise=6.0, col=(1.0, 0.95, 0.9), emis=0.9, ecol=(1.0, 0.86, 0.7)):
        """Billowy steam box (titans.steam) with density-tied emission so it reads bright."""
        import titans as T
        s = T.steam(name, c, size, density=dens, noise_scale=noise)
        nt = s.data.materials[0].node_tree; N = nt.nodes; Lk = nt.links
        for n in N:
            if n.type == "TEX_NOISE":
                n.inputs["Detail"].default_value = 12
                try:
                    n.inputs["Roughness"].default_value = 0.62
                    n.inputs["Distortion"].default_value = 0.4
                except Exception:
                    pass
        pv = next(n for n in N if n.type == "PRINCIPLED_VOLUME")
        pv.inputs["Color"].default_value = (*col, 1)
        if emis and pv.inputs["Density"].is_linked:
            src = pv.inputs["Density"].links[0].from_socket
            mul = N.new("ShaderNodeMath"); mul.operation = "MULTIPLY"; mul.inputs[1].default_value = emis
            Lk.new(src, mul.inputs[0]); Lk.new(mul.outputs[0], pv.inputs["Emission Strength"])
            pv.inputs["Emission Color"].default_value = (*ecol, 1)
        s.visible_shadow = False
        return s

    def steam_plume(name, base, height, r0, r1, n=14, lean=(0.15, -0.1), dens=0.22, seed=4, emis=0.9,
                    col=(1.0, 0.95, 0.9), ecol=(1.0, 0.86, 0.7)):
        """Billowing column: n overlapping steam puffs up a leaning path, radius r0 -> r1, jittered sideways,
        so the silhouette is lumpy like the anime steam instead of one smooth ellipsoid."""
        rnd = random.Random(seed)
        out = []
        for i in range(n):
            t = i / max(1, n - 1)
            r = r0 + (r1 - r0) * t ** 1.3
            c = Vector(base) + Vector((lean[0] * height * t + rnd.uniform(-0.35, 0.35) * r,
                                       lean[1] * height * t + rnd.uniform(-0.35, 0.35) * r, height * t))
            sz = (r * 2 * rnd.uniform(0.9, 1.3), r * 2 * rnd.uniform(0.9, 1.3), r * 2 * rnd.uniform(0.75, 1.05))
            out.append(steam(f"{name}{i:02d}", c, sz, dens * rnd.uniform(0.8, 1.2), rnd.uniform(2.6, 3.6), col, emis, ecol))
        return out

    def dust(name, c, size, dens, col=(0.78, 0.66, 0.52), emis=0.25):
        """Dense tan dust: noise volume with a soft ellipsoid falloff (its own material, more opaque than steam)."""
        bpy.ops.mesh.primitive_cube_add(size=1, location=c)
        ob = bpy.context.active_object; ob.name = name; ob.scale = size
        m = bpy.data.materials.new(name); m.use_nodes = True
        nt = m.node_tree; N = nt.nodes; Lk = nt.links
        N.remove(N["Principled BSDF"])
        pv = N.new("ShaderNodeVolumePrincipled"); pv.inputs["Color"].default_value = (*col, 1)
        tc = N.new("ShaderNodeTexCoord")
        nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 3.5; nz.inputs["Detail"].default_value = 10
        Lk.new(tc.outputs["Object"], nz.inputs["Vector"])
        ln = N.new("ShaderNodeVectorMath"); ln.operation = "LENGTH"
        Lk.new(tc.outputs["Object"], ln.inputs[0])          # object space: the cube spans -0.5..0.5
        fall = N.new("ShaderNodeMapRange"); fall.inputs["From Min"].default_value = 0.5; fall.inputs["From Max"].default_value = 0.15
        Lk.new(ln.outputs["Value"], fall.inputs["Value"])
        mul = N.new("ShaderNodeMath"); mul.operation = "MULTIPLY"
        Lk.new(nz.outputs["Fac"], mul.inputs[0]); Lk.new(fall.outputs["Result"], mul.inputs[1])
        mr = N.new("ShaderNodeMapRange"); mr.inputs["From Min"].default_value = 0.2; mr.inputs["From Max"].default_value = 0.5
        mr.inputs["To Max"].default_value = dens
        Lk.new(mul.outputs[0], mr.inputs["Value"]); Lk.new(mr.outputs["Result"], pv.inputs["Density"])
        e = N.new("ShaderNodeMath"); e.operation = "MULTIPLY"; e.inputs[1].default_value = emis
        Lk.new(mr.outputs["Result"], e.inputs[0]); Lk.new(e.outputs[0], pv.inputs["Emission Strength"])
        pv.inputs["Emission Color"].default_value = (1.0, 0.75, 0.5, 1)
        Lk.new(pv.outputs[0], N["Material Output"].inputs["Volume"]); ob.data.materials.append(m)
        ob.visible_shadow = False
        return ob

    def emissive(name, col, strength):
        m = bpy.data.materials.new(name); m.use_nodes = True
        b = m.node_tree.nodes["Principled BSDF"]
        b.inputs["Base Color"].default_value = (*col, 1)
        b.inputs["Emission Color"].default_value = (*col, 1)
        b.inputs["Emission Strength"].default_value = strength
        return m

    def specks(name, centre, spread, n, size, mat, seed=1, zmin=None):
        """Cloud of small tetra/ico specks (embers, flying debris) as one mesh."""
        rnd = random.Random(seed)
        bm = bmesh.new()
        for _ in range(n):
            p = Vector((rnd.gauss(0, spread[0]), rnd.gauss(0, spread[1]), rnd.gauss(0, spread[2]))) + Vector(centre)
            if zmin is not None:
                p.z = max(p.z, zmin)
            s = size * rnd.uniform(0.4, 1.4)
            r = bmesh.ops.create_icosphere(bm, subdivisions=0, radius=s)
            sq = Vector((rnd.uniform(0.6, 1.5), rnd.uniform(0.6, 1.5), rnd.uniform(0.5, 1.2)))
            q = Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1))).to_track_quat("Z", "Y")
            for v in r["verts"]:
                v.co = Vector((v.co.x * sq.x, v.co.y * sq.y, v.co.z * sq.z))
                v.co.rotate(q)
                v.co += p
        ob = L.obj_from_bm(name, bm, [mat])
        return ob

    def gable_house(bm, c, w, d, eave, rh, rot, mi_wall=0, mi_roof=1, z0=0.0, chimney=True, rnd=None):
        """Wall box from z0 to eave + a steep gable roof (ridge along local x) with overhangs, into bm."""
        from mathutils import Euler
        L.box(bm, (c[0], c[1], (z0 + eave) / 2), (w, d, eave - z0), rot, mi_wall)
        q = Euler((0, 0, rot)).to_matrix()
        ov = 0.6
        def P(x, y, z):
            return bm.verts.new(q @ Vector((x, y, 0)) + Vector((c[0], c[1], z)))
        hw, hd = w / 2 + ov, d / 2 + ov
        a = [P(-hw, -hd, eave - 0.4), P(hw, -hd, eave - 0.4), P(hw, hd, eave - 0.4), P(-hw, hd, eave - 0.4)]
        r0, r1 = P(-hw, 0, eave + rh), P(hw, 0, eave + rh)
        for f in ((a[0], a[1], r1, r0), (a[2], a[3], r0, r1), (a[3], a[2], a[1], a[0])):
            bm.faces.new(f).material_index = mi_roof
        for f in ((a[0], r0, a[3]), (a[1], a[2], r1)):          # gable ends: plaster
            bm.faces.new(f).material_index = mi_wall
        if chimney and rnd:
            cx = rnd.uniform(-w / 3, w / 3); cy = rnd.uniform(0.2, d / 3)
            pc = q @ Vector((cx, cy, 0)) + Vector((c[0], c[1], 0))
            L.box(bm, (pc.x, pc.y, eave + rh * 0.75), (0.7, 0.7, rh * 0.7), rot, 3)

    def tile_mat():
        """Clay roof tiles: small brick rows in world space, colour drifting red -> brown over the town."""
        m = bpy.data.materials.get("ThRoofTile")
        if m:
            return m
        m = bpy.data.materials.new("ThRoofTile"); m.use_nodes = True
        nt = m.node_tree; N = nt.nodes; Lk = nt.links
        b = N["Principled BSDF"]; b.inputs["Roughness"].default_value = 0.75
        tc = N.new("ShaderNodeTexCoord")
        br = N.new("ShaderNodeTexBrick"); br.inputs["Scale"].default_value = 0.85
        br.inputs["Mortar Size"].default_value = 0.06; br.inputs["Row Height"].default_value = 0.3; br.inputs["Brick Width"].default_value = 0.4
        br.inputs["Color1"].default_value = (0.42, 0.13, 0.06, 1); br.inputs["Color2"].default_value = (0.30, 0.10, 0.05, 1)
        br.inputs["Mortar"].default_value = (0.10, 0.04, 0.03, 1)
        Lk.new(tc.outputs["Object"], br.inputs["Vector"])
        nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 0.08
        Lk.new(tc.outputs["Object"], nz.inputs["Vector"])
        mx = N.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.blend_type = "MULTIPLY"
        Lk.new(nz.outputs["Fac"], mx.inputs["Factor"]); Lk.new(br.outputs["Color"], mx.inputs["A"])
        mx.inputs["B"].default_value = (0.75, 0.62, 0.5, 1)
        Lk.new(mx.outputs["Result"], b.inputs["Base Color"])
        bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.9
        Lk.new(br.outputs["Fac"], bp.inputs["Height"]); Lk.new(bp.outputs["Normal"], b.inputs["Normal"])
        return m

    def timber_mat():
        """Cream plaster with dark half-timber framing (brick texture mortar = beams), projected on the wall plane."""
        m = bpy.data.materials.get("ThTimber")
        if m:
            return m
        m = bpy.data.materials.new("ThTimber"); m.use_nodes = True
        nt = m.node_tree; N = nt.nodes; Lk = nt.links
        b = N["Principled BSDF"]; b.inputs["Roughness"].default_value = 0.9
        tc = N.new("ShaderNodeTexCoord"); sp = N.new("ShaderNodeSeparateXYZ"); Lk.new(tc.outputs["Object"], sp.inputs[0])
        ca = N.new("ShaderNodeCombineXYZ"); cb = N.new("ShaderNodeCombineXYZ")
        Lk.new(sp.outputs["X"], ca.inputs["X"]); Lk.new(sp.outputs["Z"], ca.inputs["Y"])
        Lk.new(sp.outputs["Y"], cb.inputs["X"]); Lk.new(sp.outputs["Z"], cb.inputs["Y"])
        def brick(vec):
            br = N.new("ShaderNodeTexBrick"); br.offset = 0.0
            br.inputs["Scale"].default_value = 0.5; br.inputs["Mortar Size"].default_value = 0.09
            br.inputs["Brick Width"].default_value = 1.2; br.inputs["Row Height"].default_value = 1.4
            br.inputs["Color1"].default_value = (0.78, 0.70, 0.55, 1); br.inputs["Color2"].default_value = (0.72, 0.64, 0.50, 1)
            br.inputs["Mortar"].default_value = (0.09, 0.05, 0.03, 1)
            Lk.new(vec, br.inputs["Vector"]); return br
        b1, b2 = brick(ca.outputs[0]), brick(cb.outputs[0])
        g = N.new("ShaderNodeNewGeometry"); sn = N.new("ShaderNodeSeparateXYZ"); Lk.new(g.outputs["Normal"], sn.inputs[0])
        ab = N.new("ShaderNodeMath"); ab.operation = "ABSOLUTE"; Lk.new(sn.outputs["X"], ab.inputs[0])
        mx = N.new("ShaderNodeMix"); mx.data_type = "RGBA"
        Lk.new(ab.outputs[0], mx.inputs["Factor"]); Lk.new(b1.outputs["Color"], mx.inputs["A"]); Lk.new(b2.outputs["Color"], mx.inputs["B"])
        Lk.new(mx.outputs["Result"], b.inputs["Base Color"])
        return m

    def foreground_roofs(loc, tgt, rows, seed=2, name="ThRoofs"):
        """Steep rooftops just below the camera (camera-relative layout: (fwd, side, ridge_drop, w, d, rot))."""
        M = MAT
        f, r, u = cam_basis(loc, tgt)
        fh = Vector((f.x, f.y, 0)).normalized(); rh_ = Vector((r.x, r.y, 0)).normalized()
        rnd = random.Random(seed)
        bm = bmesh.new()
        yaw = math.atan2(fh.y, fh.x)
        for fw, sd, drop, w, d, rot in rows:
            c = Vector(loc) + fh * fw + rh_ * sd
            ridge = loc[2] - drop
            rh = d * 0.85
            gable_house(bm, (c.x, c.y), w, d, ridge - rh, rh, yaw + rot, rnd.choice((0, 0, 4)), rnd.choice((1, 2, 1, 1)),
                        z0=L.height(c.x, c.y) - 1, rnd=rnd)
        tile = tile_mat()
        tim = timber_mat()
        mats = [tim, tile, tile, M.get("roof_dark") or tile, M.get("plaster_w") or M.get("plaster")]
        ob = L.obj_from_bm(name, bm, mats)
        return ob

    def scale_colossal(k, inner=False):
        """Anime cheat for the thumbnail: the S1E1 shots exaggerate the Colossal's head over the wall, so the rig
        is scaled k about a pivot on the outer wall face below it (the chest stays against the wall), then the
        hand is put back on the wall top with colossal.pose_wall_grip (same goal as cast845 uses)."""
        c = cast()
        rig, hand = cast_state("colossal"), cast_state("colossal_hand")
        if not rig or hand is None or abs(k - 1) < 1e-3:
            log("scale_colossal: no rig/hand", rig, hand)
            return
        log("before scale: head", tuple(round(v, 1) for v in _head()), "hand", tuple(round(v, 1) for v in hand))
        pv = Vector((rig.location.x, L.district_ymin(rig.location.x) - 10.5, 0.0))
        rig.location = pv + (rig.location - pv) * k
        rig.scale = rig.scale * k
        bpy.context.view_layer.update()
        try:
            import colossal as C
            hx = c.COLOSSAL_X - float(os.environ.get("COL_HAND_DX", "15")) * k
            gy = L.district_ymin(hx) + float(os.environ.get("COL_HAND_DY", "1.0"))
            zt = c.wall_top_at(hx, gy) or 50.0
            if inner:   # knuckles on the inner parapet edge (z ~50.5), fingers then curl down the inner face
                gi = L.district_ymin(hx) + _f("TH_GRIP_IN", 3.4)
                zi = c.wall_top_at(hx, gi - 0.6) or zt
                C.pose_wall_grip(rig, zi - 1.4, gi + 4.0, side="L", lean=_f("TH_COL_LEAN", c.COLOSSAL_LEAN), hand_x=hx)
                log(f"inner grip goal ({hx:.1f}, {gi:.1f}, {zi + 0.6:.1f})")
            else:
                C.pose_wall_grip(rig, zt, gy + 4.0, side="L", lean=_f("TH_COL_LEAN", c.COLOSSAL_LEAN), hand_x=hx)
            P = rig.pose.bones
            P["head"].rotation_euler.x += _f("TH_COL_HEAD", -0.12)
        except Exception as ex:
            import traceback; traceback.print_exc(); log("re-grip failed", ex)
        bpy.context.view_layer.update()
        P = rig.pose.bones
        hb = rig.matrix_world @ P["head"].head
        c.STATE["colossal_head"] = hb
        hd = rig.matrix_world @ P["metacarpal3.L"].tail
        c.STATE["colossal_hand"] = hd
        log(f"Colossal scaled x{k}: head {tuple(round(v, 1) for v in hb)} hand {tuple(round(v, 1) for v in hd)}")

    def cam_basis(loc, tgt):
        f = (Vector(tgt) - Vector(loc)).normalized()
        r = f.cross(Vector((0, 0, 1))).normalized()
        u = r.cross(f)
        return f, r, u

    def clear_houses(p0, p1, r, year, names=("Town", "TownTrees")):
        """Hide scatter houses (and town trees) within r of the 2D segment p0-p1 by lowering their 'dead' attribute."""
        a, b = Vector((p0[0], p0[1])), Vector((p1[0], p1[1]))
        ab = b - a
        n = 0
        for nm in names:
            ob = bpy.data.objects.get(nm)
            if not ob or "dead" not in ob.data.attributes:
                continue
            dead = ob.data.attributes["dead"].data
            for i, v in enumerate(ob.data.vertices):
                q = Vector((v.co.x, v.co.y))
                t = max(0.0, min(1.0, (q - a).dot(ab) / ab.length_squared))
                if (a + ab * t - q).length < r:
                    dead[i].value = min(dead[i].value, float(year)); n += 1
            ob.data.update()
        log(f"cleared {n} scatter points along the view")

    def carve(coll_name, centre, r, zmax):
        """Delete mesh pieces (rubble chunks) of a collection whose vertices fall inside a cylinder."""
        co = bpy.data.collections.get(coll_name)
        if not co:
            return 0
        n = 0
        c = Vector((centre[0], centre[1]))
        for ob in co.all_objects:
            if ob.type != "MESH" or len(ob.data.vertices) < 50 or any(k in ob.name for k in ("Scar", "Crater", "Decal")):
                continue
            mw = ob.matrix_world
            bm = bmesh.new(); bm.from_mesh(ob.data)
            kill = [v for v in bm.verts if (lambda w: (Vector((w.x, w.y)) - c).length < r and w.z < zmax)(mw @ v.co)]
            if kill:
                isl = set()
                for v in kill:          # whole connected chunk
                    stack = [v]
                    while stack:
                        x = stack.pop()
                        if x in isl:
                            continue
                        isl.add(x)
                        stack.extend(e.other_vert(x) for e in x.link_edges)
                        if len(isl) > 400000:
                            break
                bmesh.ops.delete(bm, geom=list(isl), context="VERTS"); n += len(isl)
                bm.to_mesh(ob.data)
            bm.free()
        log(f"carved {n} rubble verts around {centre}")
        return n

    def no_shadow(obs):
        for o in obs:
            o.visible_shadow = False

    # ------------------------------------------------------------------ v2 helpers (art-director pass)
    TH = {}

    def lin(hexs):
        """'#RRGGBB' (sRGB) -> linear RGB tuple."""
        h = hexs.lstrip("#")
        c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
        return tuple(v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c)

    def grade_world(ctx, mul=1.0, sky=None):
        """Scale both world backgrounds (lighting + camera-ray sky) and optionally recolour the camera sky ramp."""
        w = ctx.get("world")
        if not w:
            return
        for n in w.node_tree.nodes:
            if n.type == "BACKGROUND":
                n.inputs[1].default_value *= mul
            if n.type == "VALTORGB" and sky:
                e = n.color_ramp.elements
                e[0].color = (*sky[0], 1); e[1].color = (*sky[1], 1)

    def haze_abs(density, col):
        """Absolute density for the scene's Haze box (scene default is 4e-6/m, which is optically ~nothing over the
        town, so multipliers cannot reach the anime's blown haze)."""
        hz = bpy.data.objects.get("Haze")
        if not hz or not hz.data.materials:
            return
        pv = next((n for n in hz.data.materials[0].node_tree.nodes if n.type == "PRINCIPLED_VOLUME"), None)
        if pv:
            pv.inputs["Density"].default_value = density
            pv.inputs["Color"].default_value = (*col, 1)

    def aim_at_screen(loc, p, sx, sy, lens, aspect=16 / 9, sensor=36.0):
        """Target point so that world point p lands at screen (sx, sy) (0..1, from the top-left)."""
        loc, p = Vector(loc), Vector(p)
        tx = sensor / 2 / lens; ty = tx / aspect
        u = (sx - 0.5) * 2 * tx; v = (0.5 - sy) * 2 * ty
        d = (p - loc).normalized(); f = d.copy()
        for _ in range(40):
            r = f.cross(Vector((0, 0, 1))).normalized(); up = r.cross(f)
            z = d.dot(f)
            px, py = d.dot(r) / z, d.dot(up) / z
            f = (f + r * (px - u) * 0.7 + up * (py - v) * 0.7).normalized()
        return tuple(loc + f * 100.0)

    def ndc(loc, tgt, lens, p, aspect=16 / 9, sensor=36.0):
        f, r, u = cam_basis(loc, tgt)
        d = Vector(p) - Vector(loc)
        z = d.dot(f)
        if z <= 0:
            return None
        tx = sensor / 2 / lens; ty = tx / aspect
        return (round(0.5 + d.dot(r) / z / tx / 2, 3), round(0.5 - d.dot(u) / z / ty / 2, 3))

    def bone_w(rig, name, tail=False):
        pb = rig.pose.bones.get(name)
        if not pb:
            return None
        return rig.matrix_world @ (pb.tail if tail else pb.head)

    def col_body(rig):
        ms = [c for c in rig.children if c.type == "MESH"]
        return max(ms, key=lambda o: len(o.data.vertices)) if ms else None

    def pale_head(rig, thr=0.55, full=0.80):
        """S1E1 over-the-shoulder still: the whole skull reads as a pale cream dome.  Raise the 'white' channel of
        colossal.py's cmask attribute on vertices with high headness (alpha channel), keeping the cavities."""
        body = col_body(rig)
        at = body.data.color_attributes.get("cmask") if body else None
        if not at:
            log("pale_head: no cmask"); return
        import numpy as np
        a = np.zeros(len(at.data) * 4, dtype=np.float32); at.data.foreach_get("color", a)
        a = a.reshape(-1, 4)
        k = np.clip((a[:, 3] - thr) / max(1e-3, full - thr), 0, 1)
        a[:, 0] = np.maximum(a[:, 0], k)
        at.data.foreach_set("color", a.ravel()); body.data.update()
        log(f"pale_head: {int((k > 0.5).sum())} verts whitened")

    def fill_strip(xc_fn, half, y0, y1, step=12.0, seed=11, year=845, name="Town"):
        """Add scatter houses (copies of random existing house points) over a strip of the town, e.g. to hide the
        main avenue in a thumbnail (the anime's overview still shows no avenue)."""
        ob = bpy.data.objects.get(name)
        if not ob:
            return 0
        me = ob.data
        n0 = len(me.vertices)
        born = me.attributes["born"].data; dead = me.attributes["dead"].data
        rnd = random.Random(seed)
        src = [i for i in range(0, n0, 3) if born[i].value <= year < dead[i].value]
        spots = []
        y = y0
        while y > y1:
            xc = xc_fn(y)
            for sx in (-1, 1):
                spots.append((xc + sx * half * 0.5 + rnd.uniform(-0.8, 0.8), y + rnd.uniform(-1.5, 1.5)))
            y -= step * rnd.uniform(0.85, 1.1)
        if not src or not spots:
            return 0
        pick = [rnd.choice(src) for _ in spots]
        me.vertices.add(len(spots))
        for j, ((x, y), s) in enumerate(zip(spots, pick)):
            i = n0 + j
            me.vertices[i].co = (x, y, L.height(x, y))
            for at in me.attributes:
                if at.domain != "POINT" or at.name == "position" or at.name.startswith("."):
                    continue
                try:
                    d = at.data
                    if hasattr(d[s], "vector"):
                        d[i].vector = d[s].vector
                    elif hasattr(d[s], "color"):
                        d[i].color = d[s].color
                    elif hasattr(d[s], "value"):
                        d[i].value = d[s].value
                except Exception:
                    pass
            me.attributes["rot"].data[i].vector = (0, 0, rnd.choice((0.0, math.pi)) + rnd.uniform(-0.05, 0.05))
            born[i].value = -1e4; dead[i].value = 1e5
        me.update()
        log(f"fill_strip: +{len(spots)} houses y {y0}..{y1}")
        return len(spots)

    def inner_keep(M, c=(0.0, -9.0)):
        """Tall pale gate keep over the inner gate (the S1E1 still shows a white castle-like gatehouse at the far
        wall; the base gatehouse is only a thickened wall block)."""
        bm = bmesh.new()
        x0, y0 = c
        L.box(bm, (x0, y0, 31), (36, 14, 62), mi=0)
        L.box(bm, (x0, y0, 62.6), (38, 15.5, 1.4), mi=0)
        for i in range(-5, 6):
            L.box(bm, (x0 + i * 3.4, y0 - 7.2, 64.2), (1.7, 1.2, 2.0), mi=0)
        for sx in (-1, 1):
            tx = x0 + sx * 21
            L.cyl(bm, (tx, y0, 0), (tx, y0, 74), 6.5, 6.0, seg=12, mi=0)
            L.cyl(bm, (tx, y0, 74), (tx, y0, 76), 7.2, 7.2, seg=12, mi=0)
            L.cyl(bm, (tx, y0, 76), (tx, y0, 88), 7.0, 0.3, seg=12, mi=1)
        L.box(bm, (x0, y0, 70), (12, 10, 16), mi=0)
        L.cyl(bm, (x0, y0, 78), (x0, y0, 90), 6.5, 0.3, seg=4, mi=1)
        for zz in (24, 38, 50):
            for i in (-2, -1, 0, 1, 2):
                L.box(bm, (x0 + i * 6, y0 - 7.05, zz), (1.4, 0.3, 3.2), mi=2)
        stone = bpy.data.materials.get("WallStone") or M.get("stone")
        ob = L.obj_from_bm("ThInnerKeep", bm, [M.get("stone_light") or stone, M.get("roof_dark") or stone, M.get("iron") or stone])
        return ob

    def darken_mat(m, k, tint=(1, 1, 1), name=None):
        """Copy of material m with its base colour multiplied by k*tint (works when Base Color is node-linked)."""
        m2 = m.copy(); m2.name = name or (m.name + "_dk")
        if not m2.node_tree:
            return m2
        N = m2.node_tree.nodes; Lk = m2.node_tree.links
        for b in [n for n in N if n.type == "BSDF_PRINCIPLED"]:
            bc = b.inputs["Base Color"]
            mul = (k * tint[0], k * tint[1], k * tint[2], 1)
            if bc.is_linked:
                src = bc.links[0].from_socket
                mx = N.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.blend_type = "MULTIPLY"
                mx.inputs["Factor"].default_value = 1.0; mx.inputs["B"].default_value = mul
                Lk.new(src, mx.inputs["A"]); Lk.new(mx.outputs["Result"], bc)
            else:
                v = bc.default_value
                bc.default_value = (v[0] * mul[0], v[1] * mul[1], v[2] * mul[2], 1)
            try:
                b.inputs["Subsurface Weight"].default_value = 0.0
            except Exception:
                pass
        return m2

    def darken_objects(obs, k, tint=(1, 1, 1)):
        cache = {}
        for o in obs:
            if o.type != "MESH":
                continue
            for s in o.material_slots:
                m0 = s.material
                if m0:
                    if m0.name not in cache:
                        cache[m0.name] = darken_mat(m0, k, tint)
                    s.link = "OBJECT"; s.material = cache[m0.name]

    def area_light(name, loc, tgt, energy, col, size):
        ld = bpy.data.lights.new(name, "AREA"); ld.energy = energy; ld.color = col; ld.size = size
        lo = bpy.data.objects.new(name, ld); bpy.context.scene.collection.objects.link(lo)
        lo.location = loc
        lo.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
        return lo

    def streaks(name, centre, n, mat, seed=1, smin=0.15, smax=3.0, alpha=2.2, spread=(8, 6, 6), stretch=3.5,
                zmin=None, vel=(0, 1, 0.4)):
        """Flying debris with power-law sizes (many grit specks, few big blocks), each chunk stretched along its
        velocity (radial from centre + a common throw direction) to fake motion blur."""
        rnd = random.Random(seed)
        bm = bmesh.new()
        c0 = Vector(centre); vt = Vector(vel)
        for _ in range(n):
            u = rnd.random()
            s = smin * (1 - u * (1 - (smin / smax) ** (alpha - 1))) ** (-1 / (alpha - 1))     # Pareto in [smin, smax]
            p = c0 + Vector((rnd.gauss(0, spread[0]), rnd.gauss(0, spread[1]), rnd.gauss(0, spread[2])))
            if zmin is not None:
                p.z = max(p.z, zmin)
            v = ((p - c0).normalized() + vt).normalized()
            r = bmesh.ops.create_icosphere(bm, subdivisions=1 if s > 0.8 else 0, radius=s)
            k = 1 + stretch * (1.0 if s < 0.6 else 0.25)
            q = v.to_track_quat("Z", "Y")
            j = [rnd.uniform(0.7, 1.3) for _ in range(3)]
            for vv in r["verts"]:
                co = Vector((vv.co.x * j[0], vv.co.y * j[1], vv.co.z * j[2] * k))
                co += Vector((rnd.uniform(-0.18, 0.18) * s, rnd.uniform(-0.18, 0.18) * s, 0))
                co.rotate(q); vv.co = co + p
        return L.obj_from_bm(name, bm, [mat])

    def rocks(name, pts, mat, seed=3):
        """Few big wall chunks: noise-displaced, flattened icospheres with flat shading (broken-stone facets)."""
        from mathutils import noise as mn
        rnd = random.Random(seed)
        bm = bmesh.new()
        for (x, y, z, s) in pts:
            r = bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0)
            o = Vector((rnd.uniform(-50, 50), rnd.uniform(-50, 50), 0))
            sq = Vector((rnd.uniform(1.0, 1.6), rnd.uniform(0.8, 1.3), rnd.uniform(0.45, 0.8))) * s
            rz = rnd.uniform(0, math.tau)
            for v in r["verts"]:
                co = v.co.copy()
                co += co * 0.28 * mn.noise(co * 1.6 + o)
                co.z = max(co.z, -0.35)
                co = Vector((co.x * sq.x, co.y * sq.y, co.z * sq.z))
                co = Vector((co.x * math.cos(rz) - co.y * math.sin(rz), co.x * math.sin(rz) + co.y * math.cos(rz), co.z))
                v.co = co + Vector((x, y, z))
        return L.obj_from_bm(name, bm, [mat])

    # ------------------------------------------------------------------ cameras
    def _head():
        h = cast_state("colossal_head")
        return Vector(h) if h is not None else Vector((-26.0, -735.0, 56.0))

    def _cam_colossal():
        """ALT: face over the wall from a low rooftop inside the town, tilted up so head + plume dominate."""
        h = _head()
        off = _vec("TH_OFF", (-4.0, 120.0, 0.0))
        loc = Vector(h) + Vector(off); loc.z = L.height(loc.x, loc.y) + _f("TH_CAM_Z", 14.0)
        lens = _f("TH_LENS", 40)
        if os.environ.get("TH_TGT"):
            return tuple(loc), _vec("TH_TGT", None), lens
        return tuple(loc), aim_at_screen(loc, h + Vector((0, 0, 3.0)), _f("TH_SX", 0.50), _f("TH_SY", 0.32), lens), lens

    def _cam_colossal_back():
        """MAIN: S1E1 over-the-shoulder.  Camera behind/above the upper back, head placed at x 0.44 / y 0.40."""
        h = _head()
        nb = TH.get("neck", h - Vector((0, -2.0, 6.0)))
        lens = _f("TH_LENS", 24)
        if os.environ.get("TH_LOC"):
            loc = Vector(_vec("TH_LOC", None))
        else:
            loc = nb + Vector(_vec("TH_OFF", (3.0, -45.0, 22.0)))
        if os.environ.get("TH_TGT"):
            return tuple(loc), _vec("TH_TGT", None), lens
        hc = TH.get("head_c", h + Vector((0, 0, 4.0)))
        tgt = aim_at_screen(loc, hc, _f("TH_SX", 0.44), _f("TH_SY", 0.40), lens)
        rig = cast_state("colossal")
        if rig:
            for b in ("upperarm01.L", "upperarm01.R", "shoulder01.L", "shoulder01.R", "spine01", "neck01"):
                p = bone_w(rig, b)
                if p is not None:
                    log("  ndc", b, ndc(loc, tgt, lens, p))
            log("  ndc head_c", ndc(loc, tgt, lens, hc), "cam", tuple(round(v, 1) for v in loc))
        return tuple(loc), tgt, lens

    def _cam_overview():
        return _vec("TH_LOC", (-400.0, 150.0, 180.0)), _vec("TH_TGT", (30.0, -420.0, -20.0)), _f("TH_LENS", 24)

    def _cam_armored():
        return _vec("TH_LOC", (9.0, 47.0, 7.5)), _vec("TH_TGT", (-1.0, 14.0, 13.5)), _f("TH_LENS", 22)

    def _cam_night():
        return _vec("TH_LOC", (2.0, -92.0, 5.0)), _vec("TH_TGT", (-12.0, -190.0, 14.0)), _f("TH_LENS", 34)

    CAMS = {
        "thumb_colossal": _cam_colossal,
        "thumb_colossal_back": _cam_colossal_back,
        "thumb_overview": _cam_overview,
        "thumb_armored": _cam_armored,
        "thumb_night": _cam_night,
    }

    # ------------------------------------------------------------------ per-shot dressing
    def hide(names):
        for n in names:
            o = bpy.data.objects.get(n)
            if o:
                o.hide_render = True

    def strip_merlons(name="OuterGate", zcut=53.25):
        """Delete the crenellations of a gatehouse (verts above zcut) for a shot."""
        ob = bpy.data.objects.get(name)
        if not ob:
            return
        bm = bmesh.new(); bm.from_mesh(ob.data)
        kill = [v for v in bm.verts if v.co.z > zcut]
        bmesh.ops.delete(bm, geom=kill, context="VERTS")
        bm.to_mesh(ob.data); bm.free()
        log(f"strip_merlons {name}: {len(kill)} verts")

    def big_hand(rig, k=1.3, curl=(1.15, 1.35, 1.05)):
        """Bigger gripping hand: scale the wrist chain and curl the fingers further over the edge."""
        P = rig.pose.bones
        if "wrist.L" in P:
            P["wrist.L"].scale = (k, k, k)
        for f in range(2, 6):
            for j, a in zip((1, 2, 3), curl):
                bn = f"finger{f}-{j}.L"
                if bn in P:
                    P[bn].rotation_euler.x = a
        bpy.context.view_layer.update()
        tip = bone_w(rig, "finger3-3.L", tail=True)
        log("big_hand fingertip", tuple(round(v, 1) for v in tip) if tip else None)

    def dress_colossal(M, ctx):
        back = SHOT == "thumb_colossal_back"
        scale_colossal(_f("TH_COL_K", 1.35), inner=not back)
        rig = cast_state("colossal")
        h = _head()
        GOLD = (1.0, 0.82, 0.55)
        if back:
            # grading: backlit cream-gold haze (sun low in the north-east, ahead of the camera), blown sky
            set_sun(ctx, _f("TH_SUN_AZ", 40), _f("TH_SUN_EL", 12), GOLD, _f("TH_SUN_E", 7.5))
            grade_world(ctx, _f("TH_WORLD", 2.0), sky=((1.0, 0.84, 0.56), (1.0, 0.78, 0.48)))
            haze_abs(_f("TH_HAZE_D", 0.0014), (1.0, 0.80, 0.50))
            if rig:
                try:
                    t = _f("TH_COL_TURN", -0.6)          # -y twist turns the face east (toward this camera)
                    rig.pose.bones["head"].rotation_euler.y += t
                    rig.pose.bones["neck02"].rotation_euler.y += t * 0.4
                    bpy.context.view_layer.update()
                except Exception as ex:
                    log("head turn failed", ex)
                pale_head(rig, _f("TH_PALE_T", 0.55), _f("TH_PALE_F", 0.80))
                # anime cheat #3: the still's shoulders are a huge red tent across the frame; widen the upper chest
                # (spine01) and keep the neck/head at their own scale
                try:
                    B = rig.data.bones
                    log("parents:", {b: (B[b].parent.name if B[b].parent else None) for b in
                                     ("neck01", "shoulder01.L", "spine01", "spine02", "clavicle.L") if b in B})
                    kw, kd = _f("TH_CHEST_W", 1.6), _f("TH_CHEST_D", 1.2)
                    if kw != 1.0 and "spine01" in rig.pose.bones:
                        rig.pose.bones["spine01"].scale = (kw, 1.0, kd)
                        B["neck01"].inherit_scale = "NONE"
                        bpy.context.view_layer.update()
                except Exception as ex:
                    log("chest widen failed", ex)
                TH["neck"] = bone_w(rig, "neck01")
                hb, ht = bone_w(rig, "head"), bone_w(rig, "head", True)
                TH["head_c"] = hb + (ht - hb) * 0.45
                log("neck", tuple(round(v, 1) for v in TH["neck"]), "head_c", tuple(round(v, 1) for v in TH["head_c"]))
            # every cast845 puff around the body would sit in or next to the close camera
            for o in bpy.data.objects:
                if o.name.startswith(("Colossal_steam", "ColossalColumn", "ColossalCap")):
                    o.hide_render = True
            steam("ThShoulderSteamL", (h.x - 26, h.y - 4, h.z - 14), (26, 22, 22), 0.30, 6.5,
                  col=(1.0, 0.93, 0.82), ecol=(1.0, 0.85, 0.62))
            steam_plume("ThPlume", (h.x - 48, h.y - 26, 46), 230, 22, 70, n=8, lean=(-0.2, -0.15), dens=0.20, seed=8,
                        col=(1.0, 0.92, 0.80), ecol=(1.0, 0.84, 0.6))
            # the avenue is hidden by roofs in the still: fill it with scatter houses for this shot
            from mathutils import noise as mn
            fill_strip(lambda y: mn.noise(Vector((0, y / 200, 7))) * 4,
                       15.0, -20.0, L.OUTER_GATE[1] + 40, 11.0, year=MAT.get("_year", 845))
            inner_keep(M)
        else:
            # ALT: from the town; golden haze, pink-tan back-lit plume
            set_sun(ctx, _f("TH_SUN_AZ", 165), _f("TH_SUN_EL", 13), GOLD, _f("TH_SUN_E", 4.4))
            grade_world(ctx, _f("TH_WORLD", 1.0), sky=((1.0, 0.74, 0.44), (0.80, 0.56, 0.40)))
            haze_abs(_f("TH_HAZE_D", 0.00022), (1.0, 0.85, 0.6))
            strip_merlons("OuterGate")
            if rig:
                big_hand(rig, _f("TH_HAND_K", 1.3))
            hide(("ColossalColumn", "ColossalCap"))
            PT = (0.86, 0.66, 0.56); PE = (1.0, 0.72, 0.55)
            steam_plume("ThPlume", (h.x + 6, h.y - 22, 50), 260, 26, 90, n=15, lean=(0.10, -0.3), dens=0.20, seed=8,
                        col=PT, ecol=PE, emis=0.6)
            steam("ThSteamL", (h.x - 30, h.y + 2, 60), (34, 22, 22), 0.30, 7.5, col=PT, ecol=PE, emis=0.6)
            steam("ThSteamR", (h.x + 24, h.y - 4, 62), (36, 22, 26), 0.28, 7.5, col=PT, ecol=PE, emis=0.6)
            # face steam: puffs rising off the cheeks/temples and the shoulders
            for i, (dx, dy, dz, s) in enumerate(((-8, -1, 4, 9), (8, -1, 5, 9), (-4, -3, 11, 8), (5, -3, 12, 7),
                                                  (-14, -2, -6, 10), (14, -2, -5, 10))):
                steam(f"ThFaceSteam{i}", (h.x + dx, h.y + dy, h.z + dz), (s, s * 0.8, s * 1.2), 0.32, 9.0,
                      col=(1.0, 0.9, 0.8), ecol=PE, emis=0.7)
        em = emissive("ThEmber", (1.0, 0.36, 0.06), 9.0)
        specks("ThEmbers", (h.x + 8, h.y + 40, h.z - 6), (40, 28, 14), 110 if back else 220, 0.05 if back else 0.07, em, seed=3)
        if not back:
            specks("ThEmbersFace", (h.x, h.y + 10, h.z + 2), (12, 8, 8), 90, 0.06, em, seed=7)
            loc, tgt, lens = _cam_colossal()
            fw = Vector(tgt) - Vector(loc); fw.z = 0; fw.normalize()
            clear_houses(loc, tuple(Vector(loc) + fw * 22), 12.0, MAT.get("_year", 845))
            # two depth layers of roofs for parallax: near (just below the lens) and a mid row
            # (camera ~14 m up: ridges slightly above the lens so the roofs rise into the bottom of the tilted frame)
            foreground_roofs(loc, tgt, [(16, -8, -4.6, 9, 9, 0.0), (18, 3, -5.4, 8, 9, 1.57), (17, 13, -4.2, 9, 8, 0.1), (15, -18, -3.8, 8, 8, 1.5)],
                             seed=2, name="ThRoofsNear")
            foreground_roofs(loc, tgt, [(30, -16, -8.2, 10, 10, 1.5), (34, -3, -9.6, 10, 10, 0.05), (32, 10, -8.6, 10, 9, 1.6),
                                        (40, 21, -9.8, 11, 10, 0.0), (44, -24, -10.4, 11, 10, 1.4), (46, 6, -11.2, 11, 10, 1.57)],
                             seed=5, name="ThRoofsMid")
        return h

    def dress_overview(M, ctx):
        set_sun(ctx, _f("TH_SUN_AZ", 180), _f("TH_SUN_EL", 15), (1.0, 0.80, 0.58), _f("TH_SUN_E", 7.0),
                sky=((1.0, 0.78, 0.55), (0.30, 0.42, 0.66), 0.42), haze=(1.0, 0.82, 0.62))
        grade_world(ctx, _f("TH_WORLD", 0.55))
        haze_abs(_f("TH_HAZE_D", 0.00012), (1.0, 0.84, 0.66))
        hide(("ColossalCap", "ColossalColumn"))
        h = _head()
        PC = lin("#C9A08A"); PE = (1.0, 0.74, 0.58)
        top = steam_plume("ThOvPlume", (h.x + 4, h.y - 20, 40), 250, 30, 75, n=12, lean=(0.10, -0.18), dens=0.16,
                          col=PC, ecol=PE, emis=0.18)
        # mushroom cap ~300 m across on top of the column (z ~330 so it stays in this lower camera's frame)
        cx, cy = h.x + 4 + 0.10 * 250, h.y - 20 - 0.18 * 250
        rnd = random.Random(21)
        for i in range(9):
            a = i / 9 * math.tau + rnd.uniform(-0.2, 0.2)
            rr = 0 if i == 0 else rnd.uniform(70, 110)
            steam(f"ThOvCap{i}", (cx + rr * math.cos(a), cy + rr * math.sin(a), _f("TH_CAP_Z", 330) + rnd.uniform(-15, 20)),
                  (rnd.uniform(110, 150), rnd.uniform(110, 150), rnd.uniform(60, 85)), 0.10, 2.8, col=PC, ecol=PE, emis=0.15)
        # thicker dark smoke columns over the impact points
        st = sys.modules.get("states845")
        imp = list(getattr(st, "IMPACTS", []) or [])[:4]
        for i, it in enumerate(imp):
            x, y = it[0], it[1]
            steam_plume(f"ThSmoke{i}_", (x, y, 5), 230, 14, 45, n=7, lean=(0.35, 0.12), dens=0.22, seed=30 + i,
                        col=(0.10, 0.09, 0.085), emis=0.0)
        log(f"overview smoke columns at {[(round(it[0]), round(it[1])) for it in imp]}")
        # the oversized pale farm houses north of Wall Maria (bottom-left of the frame) are dropped for this shot;
        # the framing tree crown is gone too (it read as a pasted-on green tree): a post vignette frames instead
        loc, tgt, lens = _cam_overview()
        ob = bpy.data.objects.get("Town")
        if ob and "dead" in ob.data.attributes:
            dead = ob.data.attributes["dead"].data; n = 0
            c = Vector((loc[0], loc[1]))
            for i, v in enumerate(ob.data.vertices):
                if v.co.y > 5 and (Vector((v.co.x, v.co.y)) - c).length < _f("TH_FARM_R", 420):
                    dead[i].value = min(dead[i].value, float(MAT.get("_year", 845))); n += 1
            ob.data.update(); log(f"overview: dropped {n} farm houses")

    def dress_armored(M, ctx):
        # sun low behind the wall (south-west): the north wall face goes dark, the hole glows behind the Armored
        set_sun(ctx, _f("TH_SUN_AZ", 235), _f("TH_SUN_EL", 11), (1.0, 0.62, 0.36), _f("TH_SUN_E", 4.4),
                sky=((1.0, 0.58, 0.32), (0.26, 0.28, 0.40), 0.45), haze=(0.95, 0.70, 0.50), haze_mul=0.6)
        grade_world(ctx, _f("TH_WORLD", 0.6))
        _dedupe_cast_rubble()
        loc, tgt, lens = _cam_armored()
        clear_houses(loc, (0, 12), _f("TH_CLEAR_R", 22), MAT.get("_year", 845))
        # dark wall faces (#363530) so the silhouette pops
        wk = _f("TH_WALL_K", 0.30)
        wallmats = {}
        for o in bpy.data.objects:
            if o.type == "MESH" and (o.name.startswith(("Wall", "InnerGate")) or o.name in ("InnerGate",)):
                for s in o.material_slots:
                    m0 = s.material
                    if m0:
                        if m0.name not in wallmats:
                            wallmats[m0.name] = darken_mat(m0, wk, (0.98, 0.97, 0.9))
                        s.link = "OBJECT"; s.material = wallmats[m0.name]
        log("darkened wall mats:", list(wallmats))
        rig = cast_state("armored")
        ay = _f("TH_ARM_Y", 15.0)
        # clear the states845 rubble in the near half of the frame (camera to just in front of the Armored)
        carve("States845", (0.0, ay + 4), _f("TH_CARVE_R", 12.0), 30.0)
        for t in (0.15, 0.35, 0.55, 0.75):
            p = Vector(loc).lerp(Vector((0, ay + 6, 0)), t)
            carve("States845", (p.x, p.y), _f("TH_CARVE_R2", 10.0), 30.0)
        if rig:
            rig.location = (_f("TH_ARM_X", 0.0), ay, L.height(0, ay) - 0.3)
            P = rig.pose.bones
            try:   # charge, not duck: chest forward, chin up looking at the camera
                for bn, a in (("spine03", 0.10), ("spine02", 0.08), ("neck01", -0.18), ("head", -0.28)):
                    if bn in P:
                        P[bn].rotation_mode = "XYZ"; P[bn].rotation_euler.x += a
            except Exception as ex:
                log("armored pose tweak failed", ex)
            for o in bpy.data.objects:
                if o.name == "ArmoredDust":
                    o.location = (0, 2, 4)
            bpy.context.view_layer.update()
        # inflow titans: the two edge-cut ones are dropped, the rest go far out in the farmland
        inflow = [r for r in (cast_state("inflow") or []) if "smiling" not in r.name]
        spots = [(-75, 150, 0.4), (90, 170, -0.5), (-140, 240, 0.6), (150, 260, -0.7)]
        for k, rr in enumerate(inflow):
            if k < 2:
                for ch in rr.children_recursive:
                    ch.hide_render = True
                continue
            if k - 2 < len(spots):
                x, y, yaw = spots[k - 2]
                rr.location = (x, y, L.height(x, y) - 0.05); rr.rotation_euler.z = math.pi + yaw
        stone = bpy.data.materials.get("WallStone") or M.get("stone")
        dstone = darken_mat(stone, 0.45, name="ThRubbleStone")
        # backlight: a warm emissive card deep in the hole + an area light behind the Armored
        bm = bmesh.new(); L.box(bm, (0, -6, 12), (22, 0.5, 26), mi=0)
        card = L.obj_from_bm("ThHoleCard", bm, [emissive("ThHoleGlow", (1.0, 0.70, 0.42), _f("TH_CARD_E", 4.0))])
        card.visible_shadow = False
        area_light("ThRimArmored", (0, ay - 9, 14), (0, ay + 4, 10), _f("TH_RIM_W", 2500), (1.0, 0.72, 0.45), 10)
        # debris: power-law sizes, streaked along the throw
        streaks("ThBurstDebris", (0, 12, 20), 260, stone, seed=5, smin=0.10, smax=2.2, spread=(8, 5, 5), zmin=10.0,
                vel=(0, 0.9, 0.5))
        streaks("ThBurstDebrisDark", (2, 26, 14), 160, dstone, seed=9, smin=0.08, smax=1.4, spread=(10, 9, 5), zmin=4.0,
                vel=(0, 1.0, 0.1))
        # a few big, dark wall chunks low at the frame edges (the near rubble), camera stays above them
        rocks("ThNearRubble", [(-6.5, 37.0, 0.3, 2.2), (8.5, 34.0, 0.2, 1.8), (-12, 28, 0.5, 2.8), (13, 26, 0.4, 2.4),
                               (-2.0, 30.0, 0.0, 1.0), (4.0, 39.0, 0.0, 0.9)], dstone)
        dust("ThHoleDust", (0, 6, 13), (34, 10, 30), 1.6, emis=0.9)
        dust("ThHoleDustTop", (0, 4, 30), (44, 22, 22), 0.12)
        steam("ThBurstDust", (0, 0, 18), (56, 14, 36), 0.30, 4.5, col=(0.82, 0.70, 0.56), emis=0.35, ecol=(1.0, 0.7, 0.45))
        steam("ThBurstDustL", (-30, 16, 8), (36, 22, 18), 0.6, 5.0, col=(0.62, 0.52, 0.42), emis=0.15, ecol=(1.0, 0.7, 0.45))
        steam("ThBurstDustR", (32, 14, 8), (36, 22, 18), 0.6, 5.0, col=(0.62, 0.52, 0.42), emis=0.15, ecol=(1.0, 0.7, 0.45))

    def fix_ember_cracks():
        """states845 'Embers': break the regular Voronoi cells with a noise-distorted lookup (distortion 2.0)."""
        m = bpy.data.materials.get("Embers")
        if not m:
            return
        N = m.node_tree.nodes; Lk = m.node_tree.links
        vz = next((n for n in N if n.type == "TEX_VORONOI"), None)
        if not vz or not vz.inputs["Vector"].is_linked:
            return
        src = vz.inputs["Vector"].links[0].from_socket
        nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 0.9; nz.inputs["Detail"].default_value = 4
        Lk.new(src, nz.inputs["Vector"])
        sub = N.new("ShaderNodeVectorMath"); sub.operation = "SUBTRACT"; sub.inputs[1].default_value = (0.5, 0.5, 0.5)
        Lk.new(nz.outputs["Color"], sub.inputs[0])
        sc_ = N.new("ShaderNodeVectorMath"); sc_.operation = "SCALE"; sc_.inputs["Scale"].default_value = 2.0
        Lk.new(sub.outputs[0], sc_.inputs[0])
        ad = N.new("ShaderNodeVectorMath"); ad.operation = "ADD"
        Lk.new(src, ad.inputs[0]); Lk.new(sc_.outputs[0], ad.inputs[1])
        Lk.new(ad.outputs[0], vz.inputs["Vector"])
        try:
            vz.inputs["Randomness"].default_value = 1.0
        except Exception:
            pass
        log("ember cracks distorted")

    def drop_near_roof_fires(loc, r=48.0, zmin=7.0):
        """Remove roof flames (z > zmin) within r of the camera (one of them floated over a cropped house)."""
        obs = [o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith("Fires")]
        log("fire meshes:", [o.name for o in obs])
        for ob in obs:
            _drop_fires(ob, loc, r, zmin)

    def _drop_fires(ob, loc, r, zmin):
        bm = bmesh.new(); bm.from_mesh(ob.data)
        bm.verts.ensure_lookup_table()
        seen, kill = set(), []
        c = Vector((loc[0], loc[1]))
        for v in bm.verts:
            if v in seen:
                continue
            isl, stack = [], [v]
            while stack:
                x = stack.pop()
                if x in seen:
                    continue
                seen.add(x); isl.append(x)
                stack.extend(e.other_vert(x) for e in x.link_edges)
            zmin_i = min(w.co.z for w in isl)
            cx = sum((w.co.x for w in isl), 0.0) / len(isl); cy = sum((w.co.y for w in isl), 0.0) / len(isl)
            if zmin_i > zmin and (Vector((cx, cy)) - c).length < r:
                kill += isl
        bmesh.ops.delete(bm, geom=kill, context="VERTS")
        bm.to_mesh(ob.data); bm.free()
        log(f"dropped {len(kill)} near roof-fire verts")

    def dress_night(M, ctx):
        hide(("ArmoredDust",))
        loc, tgt, lens = _cam_night()
        drop_near_roof_fires(loc)
        fix_ember_cracks()
        inflow = [r for r in (cast_state("inflow") or [])]
        spots = [(-22, -200, 2.9, 1.15), (22, -235, -2.9, 1.05), (-8, -285, 3.0, 1.1), (30, -330, 3.1, 1.0)]
        moved = sorted(inflow, key=lambda o: -o.dimensions.z)[:len(spots)]
        for rr, (x, y, yaw, k) in zip(moved, spots):
            rr.location = (x, y, L.height(x, y) - 0.05)
            rr.rotation_euler.z = yaw
            rr.scale = rr.scale * k
        # pure titans as near-black silhouettes against the smoke glow
        darken_objects([c for rr in inflow for c in rr.children_recursive], _f("TH_TITAN_K", 0.3))
        # Armored: hot orange rim from behind
        rig = cast_state("armored")
        if rig:
            p = rig.matrix_world.translation
            area_light("ThArmoredRim", (p.x + 2, p.y - 9, p.z + 8), (p.x, p.y, p.z + 9), _f("TH_RIM_W", 2000),
                       (1.0, 0.45, 0.12), 6)
            log("armored at", tuple(round(v, 1) for v in p))

    def _dedupe_cast_rubble():
        """cast845 (armored) builds its own outer-gate rubble; states845 already does: hide cast's copy."""
        if bpy.data.collections.get("States845"):
            for n in ("GateRubble", "BreachDust"):
                o = bpy.data.objects.get(n)
                if o:
                    o.hide_render = True; o.hide_viewport = True

    MAT = {}

    def build(M, year, ctx):
        if not SHOT:
            return
        MAT.update(M); MAT["_year"] = year
        log("dressing for", SHOT)
        if SHOT.startswith("thumb_colossal"):
            dress_colossal(M, ctx)
        elif SHOT == "thumb_overview":
            dress_overview(M, ctx)
        elif SHOT == "thumb_armored":
            dress_armored(M, ctx)
        elif SHOT == "thumb_night":
            _dedupe_cast_rubble()
            dress_night(M, ctx)


# ---------------------------------------------------------------------- title overlay (Pillow)
def title(src, dst, big="SHIGANSHINA", big2="845", small="ATTACK ON TITAN  -  THROUGH EREN'S EYES", pos="top"):
    """Big Pirata One title + red year + small Pirata One kicker (all SIL OFL).
    pos: 'top' (dark gradient from the top edge, text top-right) or 'left' (dark band on the left)."""
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    im = Image.open(src).convert("RGBA")
    W, H = im.size
    # all-OFL title: Pirata One (Google Fonts, SIL OFL 1.1) throughout; the Ditty demo font is personal-use only
    f_big = ImageFont.truetype(os.path.join(FONTS, "PirataOne-Regular.ttf"), int(H * 0.21))
    f_num = ImageFont.truetype(os.path.join(FONTS, "PirataOne-Regular.ttf"), int(H * 0.25))
    f_small = ImageFont.truetype(os.path.join(FONTS, "PirataOne-Regular.ttf"), int(H * 0.062))
    band = Image.new("L", im.size, 0); bd = ImageDraw.Draw(band)
    if pos == "left":
        bd.rectangle((0, 0, int(W * 0.55), H), fill=150)
    else:
        bd.rectangle((0, 0, W, int(H * 0.34)), fill=140)
    band = band.filter(ImageFilter.GaussianBlur(W * 0.06))
    im = Image.composite(Image.new("RGBA", im.size, (12, 6, 3, 255)), im, band)
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    def text(xy, s, f, fill, stroke=6):
        sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).text((xy[0] + 4, xy[1] + 6), s, font=f, fill=(0, 0, 0, 210), stroke_width=stroke, stroke_fill=(0, 0, 0, 210))
        ov.alpha_composite(sh.filter(ImageFilter.GaussianBlur(5)))
        ImageDraw.Draw(ov).text(xy, s, font=f, fill=fill, stroke_width=stroke, stroke_fill=(24, 8, 4, 255))
    bw = d.textbbox((0, 0), big, font=f_big, stroke_width=6)
    nw = d.textbbox((0, 0), big2, font=f_num, stroke_width=7)
    sw = d.textbbox((0, 0), small, font=f_small, stroke_width=3)
    if pos == "left":
        x0, y0 = int(W * 0.04), int(H * 0.05)
        text((x0, y0), small, f_small, (238, 216, 178, 255), 3)
        yb = y0 + int(H * 0.085)
        text((x0, yb), big, f_big, (250, 244, 232, 255))
        text((x0, yb + bw[3] + int(H * 0.005)), big2, f_num, (228, 50, 28, 255), 7)
    else:
        total = bw[2] + int(W * 0.02) + nw[2]
        x0 = W - total - int(W * 0.035); y0 = int(H * 0.035)
        text((x0, y0 + int(H * 0.02)), big, f_big, (250, 244, 232, 255))
        text((x0 + bw[2] + int(W * 0.02), y0 - int(H * 0.025)), big2, f_num, (228, 50, 28, 255), 7)
        text((W - sw[2] - int(W * 0.04), y0 + bw[3] + int(H * 0.045)), small, f_small, (238, 216, 178, 255), 3)
    im.alpha_composite(ov)
    im.convert("RGB").save(dst)
    return dst


def vignette(src, dst, strength=0.55, warm=(18, 10, 4)):
    """Dark soft vignette (post), the framing job the overview's foreground crown used to do."""
    from PIL import Image, ImageDraw, ImageFilter
    strength = float(strength)
    im = Image.open(src).convert("RGB")
    W, H = im.size
    m = Image.new("L", im.size, 0)
    ImageDraw.Draw(m).ellipse((-W * 0.12, -H * 0.18, W * 1.12, H * 1.18), fill=255)
    m = m.filter(ImageFilter.GaussianBlur(W * 0.09))
    m = m.point(lambda v: int(255 - (255 - v) * strength))
    im = Image.composite(im, Image.new("RGB", im.size, warm), m)
    im.save(dst)
    return dst


if __name__ == "__main__" and bpy is None and len(sys.argv) > 3 and sys.argv[1] == "title":
    title(*sys.argv[2:])
if __name__ == "__main__" and bpy is None and len(sys.argv) > 3 and sys.argv[1] == "vignette":
    vignette(*sys.argv[2:])
