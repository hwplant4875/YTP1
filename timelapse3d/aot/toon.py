"""TOON SHADING TEST (opt-in, Eevee only): cel-shaded materials + a subtle rim + inverted-hull outlines on key objects.

PROJECT DEFAULT since 10/26 (user chose option 2, less orange): every render script calls toon.apply() after its own
setup; TOON=0 disables it.  As a plug-in, list `toon` LAST in AOT_PLUGINS (it then also runs at the end of the build):
    TOON=1 AOT_PLUGINS=...,toon blender -b -P aot/scene.py ... --engine BLENDER_EEVEE
    TOON=1 AOT_SET=trost AOT_PLUGINS=world,toon ...        (trost.build_set calls plug-in builds at its end)
With TOON=0 the module does nothing.  Eevee only.

What it does (by code, at build time):
  * every Principled-BSDF material: lit colour -> Shader to RGB -> luminance ratio against the material's own base
    colour -> constant 3-step ramp (shadow / mid / light) -> x base colour (texture kept: the Base Color link is reused)
    -> emission; plus a rim term (Layer Weight facing) that lightens silhouettes a little.  Transparent / emissive /
    volume / card materials are left alone.
  * inverted-hull outlines (Solidify, flipped normals, a black backface-culled material) on KEY objects only: walls and
    gatehouses, the HQ, the boulder, the church, titans, the Colossal, characters.  Thickness per kind (env TOON_INK
    scales them all).
Env: TOON_REF (light level of the top band, default 3.2), TOON_STEPS ("0.28,0.62" band edges), TOON_RIM (0.35),
     TOON_INK (1.0 outline scale), TOON_SAT (1.1 colour saturation of the bands).
"""
import bpy, os, re

ON = os.environ.get("TOON", "0") == "1"           # owner 10/27 09:46: NO toon (pre-toon look); TOON=1 re-enables the test
REF = float(os.environ.get("TOON_REF", "3.2"))
EDGES = [float(x) for x in os.environ.get("TOON_STEPS", "0.28,0.62").split(",")]
RIM = float(os.environ.get("TOON_RIM", "0.25"))
INK = float(os.environ.get("TOON_INK", "1.0"))
REPLACES = set()

# key objects -> outline thickness (m)
KEYS = [
    (r"^(Wall|Buttress)", 0.30), (r"Gate", 0.25), (r"^TrostHQ", 0.12), (r"^TrostBoulder$|^TrostBoulderCarry", 0.10),
    (r"^TrostChurch|^Church", 0.10), (r"^TrostCannonBasin", 0.10),
    (r"Titan|titan|^TA_|Attack", 0.05), (r"^P_|^ODM_|Bodies|Eren|Mikasa|Armin|Crowd|People", 0.012),
]

def _convert(m):
    if not m or not m.use_nodes or m.get("toon"):
        return False
    nt = m.node_tree; N = nt.nodes; Lk = nt.links
    out = next((n for n in N if n.type == "OUTPUT_MATERIAL" and n.is_active_output), None) or N.get("Material Output")
    bsdf = next((n for n in N if n.type == "BSDF_PRINCIPLED"), None)
    if out is None or bsdf is None or not out.inputs["Surface"].is_linked:
        return False
    if out.inputs["Surface"].links[0].from_node != bsdf:          # mixes / custom shaders: leave alone
        return False
    if bsdf.inputs["Alpha"].is_linked or bsdf.inputs["Alpha"].default_value < 0.99:
        return False
    if getattr(m, "surface_render_method", "") == "BLENDED":
        return False
    bc = bsdf.inputs["Base Color"]
    if bc.is_linked:
        base = bc.links[0].from_socket
    else:
        rgb = N.new("ShaderNodeRGB"); rgb.outputs[0].default_value = tuple(bc.default_value); base = rgb.outputs[0]
    s2r = N.new("ShaderNodeShaderToRGB"); Lk.new(bsdf.outputs[0], s2r.inputs[0])
    lit = N.new("ShaderNodeRGBToBW"); Lk.new(s2r.outputs["Color"], lit.inputs[0])
    bl = N.new("ShaderNodeRGBToBW"); Lk.new(base, bl.inputs[0])
    mx = N.new("ShaderNodeMath"); mx.operation = "MAXIMUM"; mx.inputs[1].default_value = 0.02; Lk.new(bl.outputs[0], mx.inputs[0])
    rt = N.new("ShaderNodeMath"); rt.operation = "DIVIDE"; Lk.new(lit.outputs[0], rt.inputs[0]); Lk.new(mx.outputs[0], rt.inputs[1])
    nr = N.new("ShaderNodeMath"); nr.operation = "DIVIDE"; nr.inputs[1].default_value = REF; Lk.new(rt.outputs[0], nr.inputs[0])
    ramp = N.new("ShaderNodeValToRGB"); ramp.color_ramp.interpolation = "CONSTANT"
    e = ramp.color_ramp.elements
    e[0].position, e[0].color = 0.0, (0.34, 0.35, 0.39, 1)          # shadow band, barely cool
    e[1].position, e[1].color = EDGES[0], (0.66, 0.66, 0.67, 1)
    e3 = e.new(EDGES[1]); e3.color = (1.0, 1.0, 1.0, 1)             # light band, neutral (less orange, user 10/26)
    Lk.new(nr.outputs[0], ramp.inputs["Fac"])
    col = N.new("ShaderNodeMix"); col.data_type = "RGBA"; col.blend_type = "MULTIPLY"; col.inputs["Factor"].default_value = 1.0
    Lk.new(base, col.inputs["A"]); Lk.new(ramp.outputs["Color"], col.inputs["B"])
    hs = N.new("ShaderNodeHueSaturation"); hs.inputs["Saturation"].default_value = float(os.environ.get("TOON_SAT", "1.0"))
    Lk.new(col.outputs["Result"], hs.inputs["Color"])
    lw = N.new("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = 0.35
    rr = N.new("ShaderNodeMapRange"); rr.inputs["From Min"].default_value = 0.72; rr.inputs["From Max"].default_value = 0.8
    rr.inputs["To Max"].default_value = RIM; Lk.new(lw.outputs["Facing"], rr.inputs["Value"])
    rim = N.new("ShaderNodeMix"); rim.data_type = "RGBA"; rim.blend_type = "SCREEN"
    Lk.new(rr.outputs["Result"], rim.inputs["Factor"]); Lk.new(hs.outputs["Color"], rim.inputs["A"])
    rim.inputs["B"].default_value = (1.0, 1.0, 1.0, 1)
    em = N.new("ShaderNodeEmission"); em.inputs["Strength"].default_value = REF
    Lk.new(rim.outputs["Result"], em.inputs["Color"])
    Lk.new(em.outputs[0], out.inputs["Surface"])
    m["toon"] = 1
    return True

def _ink_mat():
    m = bpy.data.materials.get("ToonInk")
    if m:
        return m
    m = bpy.data.materials.new("ToonInk"); m.use_nodes = True
    nt = m.node_tree; nt.nodes.remove(nt.nodes["Principled BSDF"])
    em = nt.nodes.new("ShaderNodeEmission"); em.inputs["Color"].default_value = (0.02, 0.018, 0.022, 1)
    nt.links.new(em.outputs[0], nt.nodes["Material Output"].inputs["Surface"])
    m.use_backface_culling = True
    m["toon"] = 1
    return m

def _outline(ob, t):
    if ob.type != "MESH" or any(md.type == "SOLIDIFY" and md.name == "ToonInk" for md in ob.modifiers):
        return False
    ink = _ink_mat()
    if ink.name not in [s.material.name for s in ob.material_slots if s.material]:
        ob.data.materials.append(ink)
    md = ob.modifiers.new("ToonInk", "SOLIDIFY")
    md.thickness = t * INK; md.offset = 1.0; md.use_flip_normals = True; md.use_rim = False
    md.material_offset = len(ob.material_slots) - 1
    md.material_offset_rim = len(ob.material_slots) - 1
    return True

def apply():
    """Convert once more (idempotent): call it AFTER a render script's own setup so script-made objects convert too.
    Eevee only (Shader to RGB does not exist in Cycles): with another engine it does nothing."""
    if not ON:
        return
    eng = bpy.context.scene.render.engine
    if not eng.startswith("BLENDER_EEVEE"):
        print(f"[toon] skipped (engine {eng}; toon is Eevee-only)", flush=True)
        return
    n = sum(_convert(m) for m in list(bpy.data.materials))
    k = 0
    for ob in list(bpy.data.objects):
        if ob.type != "MESH":
            continue
        cols = [c.name for c in ob.users_collection]
        t = next((t for pat, t in KEYS if re.search(pat, ob.name)), None)
        if t is None and any(c.startswith("ColossalTitan") for c in cols):
            t = 0.08
        if t is not None and len(ob.data.polygons) > 0:
            k += _outline(ob, t)
    print(f"[toon] cel-shaded {n} materials, outlines on {k} key objects", flush=True)

def build(M, year, ctx=None):
    apply()
