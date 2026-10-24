"""Render loop for the 846 march (aot/march846.py): ONE Blender session, scene built once, then per frame
march846.update(t, cam) + camera + render.  Every frame is a pure function of t, so any window / still renders alone.
Run after scene.py (see render_march846.sh):
    blender -b -P aot/scene.py -P aot/render_march846.py -- --cam march_gate --engine EEVEE --res 854x480 \
        --m-out <dir> --fps 15 [--t0 0 --t1 18] [--times 0,4,9] [--m-samples 8]
Writes <dir>/march_00000.png ... (or march_tSS.ss.png for --times), per-frame camera JSON for the HUD layer
(<dir>/_cam/00000.json via hudcam.dump, with extra={"alive": n}) and <dir>/march846_alive.json (counter sidecar).
"""
import bpy, math, os, sys, time, argparse
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ap = argparse.ArgumentParser()
ap.add_argument("--m-out", required=True)
ap.add_argument("--t0", type=float, default=0.0)
ap.add_argument("--t1", type=float, default=18.0)
ap.add_argument("--fps", type=float, default=15.0)
ap.add_argument("--m-samples", type=int, default=8)
ap.add_argument("--times", default="")
ap.add_argument("--prefix", default="march")
ap.add_argument("--index0", type=int, default=0)
B, _ = ap.parse_known_args(argv)

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
import march846 as MR
import hudcam

sc = bpy.context.scene
cam = sc.camera
eng = sc.render.engine
if eng.startswith("BLENDER_EEVEE"):
    ev = sc.eevee
    ev.taa_render_samples = B.m_samples
    for k, v in (("use_raytracing", False), ("volumetric_tile_size", "16"), ("volumetric_samples", 24),
                 ("shadow_resolution_scale", 0.5), ("shadow_ray_count", 1), ("shadow_step_count", 4),
                 ("use_shadows", True), ("clamp_surface_indirect", 10.0)):
        try:
            setattr(ev, k, v)
        except Exception:
            pass
else:
    cy = sc.cycles
    cy.samples = B.m_samples; cy.use_adaptive_sampling = True; cy.use_denoising = True
    try:
        cy.denoiser = "OPENIMAGEDENOISE"; cy.denoising_use_gpu = True
    except Exception:
        pass
    cy.max_bounces, cy.diffuse_bounces, cy.glossy_bounces, cy.transmission_bounces = 3, 1, 1, 2
    cy.volume_bounces = 0; cy.transparent_max_bounces = 8
    cy.volume_step_rate = 8; cy.volume_max_steps = 96
    sc.render.use_simplify = True; sc.render.simplify_subdivision_render = 0
    cy.texture_limit_render = "1024"
sc.render.use_persistent_data = True
sc.render.image_settings.file_format = "PNG"
cam.data.clip_end = 30000
os.makedirs(B.m_out, exist_ok=True)

t_set = time.time()
MR.setup()
print(f"[march] setup {time.time() - t_set:.0f}s  engine {eng}  people {MR.STATE['N']} wagons {MR.STATE['NW']} titans {MR.STATE['NT']}")
MR.write_alive_json(os.path.join(B.m_out, "march846_alive.json"), fps=30.0)

if B.times:
    times = [float(x) for x in B.times.split(",") if x.strip()]
else:
    times = [B.t0 + j / B.fps for j in range(int(round((B.t1 - B.t0) * B.fps)) + 1)]
i = B.index0
t_start = time.time()
for t in times:
    t_fr = time.time()
    loc, tgt, lens = MR.cam_at(t)
    cam.location = loc
    cam.rotation_euler = (tgt - loc).to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = lens
    MR.update(t, loc)
    t_up = time.time() - t_fr
    name = f"{B.prefix}_{i:05d}.png" if not B.times else f"{B.prefix}_t{t:05.2f}.png"
    sc.render.filepath = os.path.join(B.m_out, name)
    bpy.ops.render.render(write_still=True)
    lst = MR.STATE.get("last", {})
    hudcam.dump(sc, i, B.m_out, t=t, extra={"alive": MR.alive(t), "segment": "march846"},
                name=None if not B.times else f"{B.prefix}_t{t:05.2f}")
    print(f"[march] t={t:.2f}s -> {name}  alive {lst.get('alive')}  agents vis {lst.get('visible')} near {lst.get('near')} "
          f"mid {lst.get('mid')} dust {lst.get('dust')}  update {t_up:.2f}s frame {time.time() - t_fr:.1f}s "
          f"({time.time() - t_start:.0f}s total)")
    i += 1
