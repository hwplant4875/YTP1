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
        br = N.new("ShaderNodeTexBrick"); br.inputs["Scale"].default_value = 2.2
        br.inputs["Mortar Size"].default_value = 0.035; br.inputs["Row Height"].default_value = 0.3; br.inputs["Brick Width"].default_value = 0.4
        br.inputs["Color1"].default_value = (0.42, 0.13, 0.06, 1); br.inputs["Color2"].default_value = (0.30, 0.10, 0.05, 1)
        br.inputs["Mortar"].default_value = (0.10, 0.04, 0.03, 1)
        Lk.new(tc.outputs["Object"], br.inputs["Vector"])
        nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 0.08
        Lk.new(tc.outputs["Object"], nz.inputs["Vector"])
        mx = N.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.blend_type = "MULTIPLY"
        Lk.new(nz.outputs["Fac"], mx.inputs["Factor"]); Lk.new(br.outputs["Color"], mx.inputs["A"])
        mx.inputs["B"].default_value = (0.75, 0.62, 0.5, 1)
        Lk.new(mx.outputs["Result"], b.inputs["Base Color"])
        bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.4
        Lk.new(br.outputs["Fac"], bp.inputs["Height"]); Lk.new(bp.outputs["Normal"], b.inputs["Normal"])
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
            gable_house(bm, (c.x, c.y), w, d, ridge - rh, rh, yaw + rot, rnd.choice((0, 0, 4)), rnd.choice((1, 2, 3, 1)),
                        z0=L.height(c.x, c.y) - 1, rnd=rnd)
        tile = tile_mat()
        mats = [M.get("plaster"), tile, tile, M.get("roof_dark") or tile, M.get("plaster_w") or M.get("plaster")]
        ob = L.obj_from_bm(name, bm, mats)
        return ob

    def scale_colossal(k):
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

    # ------------------------------------------------------------------ cameras
    def _head():
        h = cast_state("colossal_head")
        return Vector(h) if h is not None else Vector((-26.0, -735.0, 56.0))

    def _cam_colossal():
        h = _head()
        off = _vec("TH_OFF", (22.0, 65.0, -37.0))
        loc = _vec("TH_LOC", tuple(h + Vector(off)))
        tgt = _vec("TH_TGT", tuple(h + Vector((-6.0, 0.0, -25.0))))
        return loc, tgt, _f("TH_LENS", 20)

    def _cam_colossal_back():
        h = _head()
        loc = _vec("TH_LOC", tuple(h + Vector(_vec("TH_OFF", (17.0, -44.0, 10.0)))))
        tgt = _vec("TH_TGT", (h.x - 8.0, h.y + 330.0, 4.0))
        return loc, tgt, _f("TH_LENS", 30)

    def _cam_overview():
        return _vec("TH_LOC", (-560.0, 300.0, 300.0)), _vec("TH_TGT", (40.0, -430.0, 0.0)), _f("TH_LENS", 26)

    def _cam_armored():
        return _vec("TH_LOC", (9.0, 47.0, 4.5)), _vec("TH_TGT", (-1.0, 14.0, 12.5)), _f("TH_LENS", 22)

    def _cam_night():
        return _vec("TH_LOC", (6.0, -92.0, 5.0)), _vec("TH_TGT", (-2.0, -190.0, 14.0)), _f("TH_LENS", 34)

    CAMS = {
        "thumb_colossal": _cam_colossal,
        "thumb_colossal_back": _cam_colossal_back,
        "thumb_overview": _cam_overview,
        "thumb_armored": _cam_armored,
        "thumb_night": _cam_night,
    }

    # ------------------------------------------------------------------ per-shot dressing
    def dress_colossal(M, ctx):
        scale_colossal(_f("TH_COL_K", 1.35))
        h = _head()
        # golden sun low behind the Colossal (south-west): steam glows, rooftops get a warm rim
        back = SHOT == "thumb_colossal_back"
        set_sun(ctx, _f("TH_SUN_AZ", 150 if back else 160), _f("TH_SUN_EL", 7 if back else 12), (1.0, 0.66, 0.40),
                _f("TH_SUN_E", 4.2), sky=((1.0, 0.62, 0.32), (0.36, 0.40, 0.55), 0.45), haze=(1.0, 0.74, 0.50),
                haze_mul=_f("TH_HAZE", 6.0 if back else 1.0))
        if back:     # turn the face a little toward the camera (east) so one eye and the cheek read, as in the still
            rig = cast_state("colossal")
            try:
                t = _f("TH_COL_TURN", -0.8)          # -y twist turns the face east (toward this camera)
                rig.pose.bones["head"].rotation_euler.y += t
                rig.pose.bones["neck02"].rotation_euler.y += t * 0.4
                bpy.context.view_layer.update()
            except Exception as ex:
                log("head turn failed", ex)
            for n in ("Colossal_steam_neck", "Colossal_steam_shoulders"):     # these puffs sit right over the nape
                o = bpy.data.objects.get(n)
                if o:
                    o.hide_render = True
            steam("ThShoulderSteamL", (h.x - 22, h.y - 6, h.z - 18), (30, 24, 22), 0.30, 6.5)
        fy = h.y
        # boiling steam behind it plus puffs rolling off the shoulders over the wall top
        for n in ("ColossalColumn", "ColossalCap"):
            o = bpy.data.objects.get(n)
            if o:
                o.hide_render = True
        if back:     # camera is south of the head: keep the column out of the camera's own volume (render cost)
            steam_plume("ThPlume", (h.x - 40, fy - 30, 50), 220, 24, 70, n=8, lean=(-0.25, -0.2), dens=0.20, seed=8)
        else:
            steam_plume("ThPlume", (h.x + 6, fy - 22, 50), 260, 26, 90, n=15, lean=(0.10, -0.3), dens=0.20, seed=8)
        if not back:
            steam("ThSteamL", (h.x - 30, fy + 2, 60), (34, 22, 22), 0.30, 7.5)
            steam("ThSteamR", (h.x + 24, fy - 4, 62), (36, 22, 26), 0.28, 7.5)
        em = emissive("ThEmber", (1.0, 0.36, 0.06), 9.0)
        specks("ThEmbers", (h.x + 8, fy + 40, h.z - 6), (40, 28, 14), 220, 0.07, em, seed=3)
        if SHOT == "thumb_colossal":
            loc, tgt, lens = _cam_colossal()
            foreground_roofs(loc, tgt, [(12, -12, 4.2, 9, 8, 0.0), (14, 0, 3.4, 8, 8, 1.57), (13, 12, 4.4, 9, 8, 0.1),
                                        (20, -24, 4.8, 10, 9, 1.5), (24, -6, 4.4, 10, 9, 0.05), (22, 18, 5.4, 10, 9, 1.6),
                                        (30, 30, 5.8, 11, 9, 0.0), (34, -34, 6.4, 11, 9, 1.4), (36, 6, 6.0, 11, 9, 1.57),
                                        (44, -18, 7.4, 12, 9, 0.1), (46, 22, 7.6, 12, 10, 1.5)])
        return h

    def dress_overview(M, ctx):
        set_sun(ctx, _f("TH_SUN_AZ", 200), _f("TH_SUN_EL", 8), (1.0, 0.66, 0.42), _f("TH_SUN_E", 4.4),
                sky=((1.0, 0.70, 0.45), (0.22, 0.34, 0.66), 0.42), haze=(1.0, 0.80, 0.6))
        for n in ("ColossalCap", "ColossalColumn"):        # cast845's smooth mushroom plume reads as cotton from up here
            o = bpy.data.objects.get(n)
            if o:
                o.hide_render = True
        h = _head()
        steam_plume("ThOvPlume", (h.x + 4, h.y - 20, 40), 300, 34, 95, n=16, lean=(0.12, -0.25), dens=0.16)
        # hill-tree foliage framing the top-left corner (a copy of flight's tree right next to the camera)
        loc, tgt, lens = _cam_overview()
        f, r, u = cam_basis(loc, tgt)
        c = Vector(loc) + f * _f("TH_LEAF_D", 11) - r * _f("TH_LEAF_R", 8.5) + u * _f("TH_LEAF_U", 5.5)
        try:
            import flight
            base = c - Vector((0, 0, 6.0))
            before = set(bpy.data.objects)
            trunk, crown = flight.hill_tree(base, seed=9)
            trunk.hide_render = True                    # only the overhanging foliage frames the shot
            no_shadow([o for o in bpy.data.objects if o not in before])
        except Exception as ex:
            import traceback; traceback.print_exc(); log("framing tree failed", ex)

    def dress_armored(M, ctx):
        set_sun(ctx, _f("TH_SUN_AZ", 120), _f("TH_SUN_EL", 9), (1.0, 0.60, 0.36), _f("TH_SUN_E", 4.4),
                sky=((1.0, 0.55, 0.30), (0.30, 0.32, 0.45), 0.45), haze=(0.95, 0.70, 0.50), haze_mul=0.6)
        _dedupe_cast_rubble()
        loc, tgt, lens = _cam_armored()
        clear_houses(loc, (0, 12), _f("TH_CLEAR_R", 22), MAT.get("_year", 845))
        rig = cast_state("armored")
        log("armored rig:", rig, [o.name for o in bpy.data.objects if "rmored" in o.name][:12])
        if rig:
            ay = _f("TH_ARM_Y", 15.0)
            carve("States845", (0.0, ay + 4), _f("TH_CARVE_R", 12.0), 30.0)
            rig.location = (_f("TH_ARM_X", 0.0), ay, L.height(0, ay) - 0.3)
            for o in bpy.data.objects:
                if o.name == "ArmoredDust":
                    o.location = (0, 2, 4)
            bpy.context.view_layer.update()
            for ch in rig.children:
                if ch.type == "MESH":
                    bb = [ch.matrix_world @ Vector(v) for v in ch.bound_box]
                    log("  armored mesh", ch.name, "z", round(min(v.z for v in bb), 1), round(max(v.z for v in bb), 1),
                        "y", round(min(v.y for v in bb), 1), round(max(v.y for v in bb), 1), "hidden", ch.hide_render)
        # spill a few of the inflow titans into the farmland north of the gate
        inflow = [r for r in (cast_state("inflow") or []) if "smiling" not in r.name]
        spots = [(-17, 27, 0.35), (19, 22, -0.4), (-40, 14, 0.6), (44, 10, -0.7), (-20, 150, 0.2), (110, 60, -1.1)]
        for rr, (x, y, yaw) in zip(inflow[:len(spots)], spots):
            rr.location = (x, y, L.height(x, y) - 0.05)
            rr.rotation_euler.z = math.pi + yaw
        stone = bpy.data.materials.get("WallStone") or M.get("stone")
        # debris thrown up and outward around (not in front of) the Armored
        dark = bpy.data.materials.get("RubbleDark") or stone
        # debris erupting from the hole: a tight burst around its top, a jet thrown out toward the camera
        specks("ThBurstDebris", (0, 12, 20), (7, 5, 5), 110, 0.45, stone, seed=5, zmin=10.0)
        specks("ThBurstDebrisDark", (2, 26, 14), (9, 9, 5), 90, 0.38, dark, seed=9, zmin=4.0)
        specks("ThBurstDebrisBig", (0, 18, 22), (8, 6, 4), 8, 1.6, stone, seed=6, zmin=14.0)
        # the hole itself boils with dust behind the Armored (hides the town seen through it)
        dust("ThHoleDust", (0, 6, 13), (34, 10, 30), 1.6, emis=0.5)
        dust("ThHoleDustTop", (0, 4, 30), (44, 22, 22), 0.12)
        # dust billowing out of the hole behind it
        steam("ThBurstDust", (0, 0, 18), (56, 14, 36), 0.30, 4.5, col=(0.82, 0.70, 0.56), emis=0.35, ecol=(1.0, 0.7, 0.45))
        steam("ThBurstDustL", (-30, 16, 8), (36, 22, 18), 0.6, 5.0, col=(0.82, 0.70, 0.56), emis=0.3, ecol=(1.0, 0.7, 0.45))
        steam("ThBurstDustR", (32, 14, 8), (36, 22, 18), 0.6, 5.0, col=(0.82, 0.70, 0.56), emis=0.3, ecol=(1.0, 0.7, 0.45))

    def dress_night(M, ctx):
        d = bpy.data.objects.get("ArmoredDust")
        if d:
            d.hide_render = True
        # bring a few titans close enough to read as silhouettes against the fires
        inflow = [r for r in (cast_state("inflow") or [])]
        spots = [(-22, -200, 2.9, 1.15), (22, -235, -2.9, 1.05), (-8, -285, 3.0, 1.1), (30, -330, 3.1, 1.0)]
        for rr, (x, y, yaw, k) in zip(sorted(inflow, key=lambda o: -o.dimensions.z)[:len(spots)], spots):
            rr.location = (x, y, L.height(x, y) - 0.05)
            rr.rotation_euler.z = yaw
            rr.scale = rr.scale * k

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
    """Big Ditty title + red year (Pirata One: the Ditty demo font has no digits) + small Pirata One kicker.
    pos: 'top' (dark gradient from the top edge, text top-right) or 'left' (dark band on the left)."""
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    im = Image.open(src).convert("RGBA")
    W, H = im.size
    f_big = ImageFont.truetype(os.path.join(FONTS, "Ditty.ttf"), int(H * 0.19))
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


if __name__ == "__main__" and bpy is None and len(sys.argv) > 3 and sys.argv[1] == "title":
    title(*sys.argv[2:])
