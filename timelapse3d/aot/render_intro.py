"""Fast animation render of the opening one-take (tree wake-up -> inner gate -> avenue -> Colossal -> kick) in ONE Blender
session: the scene is built once by scene.py, then this script steps the camera / Colossal pose / scene frame per frame.

  blender -b -P aot/scene.py -P aot/render_intro.py -- --cam seq --engine EEVEE --res 854x480 \
      --intro-out <dir> --intro-from 700 --intro-to 1727 --intro-step 1.25 --intro-samples 12
Env for the build (set by the caller): SEQ_F (any frame with the Colossal shown), COL_SHOW=1, AOT_STATE, AOT_EVENT,
AOT_PLUGINS=seq_colossal,flight,cast845,states845,colossal_asset,seq_colossal
"""
import bpy, os, sys, time, argparse
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ap = argparse.ArgumentParser()
ap.add_argument("--intro-out", required=True)
ap.add_argument("--intro-from", type=float, default=700)
ap.add_argument("--intro-to", type=float, default=1727)
ap.add_argument("--intro-step", type=float, default=1.25)          # 30 fps sequence frames -> 24 fps video
ap.add_argument("--intro-samples", type=int, default=12)
ap.add_argument("--intro-lite", action="store_true")         # quick preview: no volumes (steam/haze), no soft shadows
ap.add_argument("--intro-index0", type=int, default=0)             # first output file index (to append segments)
# timelapse pacing (user 10/24: the opening must be fast): "seqframe:speed,..." = playback speed from that frame on
ap.add_argument("--intro-speed", default="700:1.5,900:3.0,1270:1.5,1380:3.0,1650:1.2,1760:2.0")
B, _ = ap.parse_known_args(argv)

S = sys.modules["seq_colossal"]
CA = sys.modules.get("colossal_asset")
sc = bpy.context.scene
cam = sc.camera
if sc.render.engine.startswith("BLENDER_EEVEE"):
    sc.eevee.taa_render_samples = B.intro_samples
sc.render.image_settings.file_format = "PNG"
if B.intro_lite:
    def _is_vol(o):
        for sl in getattr(o, "material_slots", []):
            m = sl.material
            if m and m.use_nodes:
                for n in m.node_tree.nodes:
                    if n.type == "OUTPUT_MATERIAL" and n.inputs["Volume"].is_linked:
                        return True
        return False
    nv = 0
    for o in sc.objects:
        if o.type == "VOLUME" or (o.type == "MESH" and _is_vol(o)):
            o.hide_render = True; nv += 1
    if sc.world and sc.world.use_nodes:
        for n in sc.world.node_tree.nodes:
            if n.type == "OUTPUT_WORLD" and n.inputs["Volume"].is_linked:
                sc.world.node_tree.links.remove(n.inputs["Volume"].links[0])
    sc.render.use_simplify = True; sc.render.simplify_subdivision_render = 0
    for a in ("use_soft_shadows", "use_shadows", "use_gtao", "use_bloom", "use_ssr", "use_volumetric_shadows"):
        if hasattr(sc.eevee, a) and a != "use_shadows":
            setattr(sc.eevee, a, False)
    print(f"[intro] lite: hid {nv} volume objects")
os.makedirs(B.intro_out, exist_ok=True)
col_coll = bpy.data.collections.get("ColossalTitan")

SPEED = sorted((float(a), float(b)) for a, b in (kv.split(":") for kv in B.intro_speed.split(",") if kv))
def speed_at(fr):
    sp = 1.0
    for a, v in SPEED:
        if fr >= a:
            sp = v
    return sp

f = B.intro_from
i = B.intro_index0
t0 = time.time()
while f <= B.intro_to + 1e-6:
    fl = S.flags(int(round(f)))
    if col_coll:
        show = fl["COL_SHOW"] == "1"
        col_coll.hide_render = not show
        if show and CA and CA.STATE:
            CA.set_pose(float(fl["COL_KICK"]), float(fl["COL_RISE"]), float(fl["COL_FADE"]))
    loc, tgt, lens = S.cam_at(f)
    cam.location = loc
    cam.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = lens
    sc.frame_set(int(f))            # kids' wake-up animation and titan walk cycles follow the sequence frame
    sc.render.filepath = os.path.join(B.intro_out, f"intro_{i:05d}.png")
    bpy.ops.render.render(write_still=True)
    print(f"[intro] frame {f:.2f} -> {i}  ({time.time() - t0:.0f}s)")
    i += 1
    f += B.intro_step * speed_at(f)
