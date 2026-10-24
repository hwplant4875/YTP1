"""Per-frame camera dump for the graphics layer (hud2.py), plus a pure-numpy projector that needs no Blender.

In a Blender render loop, right after the camera (and any tracked objects) are set for the frame:

    import hudcam                                   # repo root must be on sys.path (see below)
    hudcam.dump(sc, i, out_dir)                     # -> <out_dir>/_cam/00042.json
    hudcam.dump(sc, i, out_dir, track=("Eren", "Mikasa"))   # also store those objects' world positions

    # sys.path: sys.path.insert(0, r"E:/YTP2/3D Timelapse/repo/timelapse3d") or os.path.dirname(__file__) + "/.."

The JSON holds the camera matrix_world (4x4, row-major), lens, sensor size/fit, shift, ortho scale, resolution and
percentage, clip range, and optional tracked points {name: [x, y, z]}. Outside Blender:

    cam = hudcam.load(out_dir, 42)                  # dict, or None when missing
    (x, y), depth = hudcam.project(cam, (0, -720, 60))   # pixel coords (origin top-left) at cam's resolution,
                                                    # depth = metres in front of the camera (<= 0: behind)
"""
import json, math, os

CAM_DIR = "_cam"


def _cam_path(out_dir, key):
    name = key if isinstance(key, str) else f"{int(key):05d}"
    return os.path.join(out_dir, CAM_DIR, name + ".json")


def dump(scene, frame_index, out_dir, track=(), name=None, t=None, extra=None):
    """Write the active camera of `scene` for this frame. `track`: object names (or objects) whose world location
    is stored too, so name tags can follow moving characters. `name` overrides the file stem (e.g. 'fast_t07.80')."""
    cam = scene.camera
    cd = cam.data
    r = scene.render
    mw = cam.matrix_world
    rec = {
        "frame": int(frame_index),
        "t": t,
        "matrix_world": [[float(mw[i][j]) for j in range(4)] for i in range(4)],
        "type": cd.type,                     # PERSP / ORTHO / PANO
        "lens": float(cd.lens),
        "sensor_width": float(cd.sensor_width),
        "sensor_height": float(cd.sensor_height),
        "sensor_fit": cd.sensor_fit,         # AUTO / HORIZONTAL / VERTICAL
        "shift_x": float(cd.shift_x), "shift_y": float(cd.shift_y),
        "ortho_scale": float(cd.ortho_scale),
        "clip": [float(cd.clip_start), float(cd.clip_end)],
        "res": [int(r.resolution_x * r.resolution_percentage / 100), int(r.resolution_y * r.resolution_percentage / 100)],
        "pixel_aspect": [float(r.pixel_aspect_x), float(r.pixel_aspect_y)],
    }
    pts = {}
    for ob in track:
        o = scene.objects.get(ob) if isinstance(ob, str) else ob
        if o is not None:
            p = o.matrix_world.translation
            pts[o.name] = [float(p.x), float(p.y), float(p.z)]
    if pts:
        rec["points"] = pts
    if extra:
        rec["extra"] = extra
    path = _cam_path(out_dir, name if name else frame_index)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(rec, f)
    return path


def load(out_dir, key):
    p = _cam_path(out_dir, key)
    if not os.path.exists(p):
        return None
    with open(p) as f:
        return json.load(f)


def _inv_rigid(m):
    """Inverse of a 4x4 camera matrix (rotation may carry uniform scale; handled via full 3x3 inverse)."""
    a = [row[:3] for row in m[:3]]
    det = (a[0][0] * (a[1][1] * a[2][2] - a[1][2] * a[2][1]) - a[0][1] * (a[1][0] * a[2][2] - a[1][2] * a[2][0])
           + a[0][2] * (a[1][0] * a[2][1] - a[1][1] * a[2][0]))
    inv = [[(a[(j + 1) % 3][(i + 1) % 3] * a[(j + 2) % 3][(i + 2) % 3] - a[(j + 1) % 3][(i + 2) % 3] * a[(j + 2) % 3][(i + 1) % 3]) / det
            for j in range(3)] for i in range(3)]
    t = [m[0][3], m[1][3], m[2][3]]
    ti = [-sum(inv[i][k] * t[k] for k in range(3)) for i in range(3)]
    return inv, ti


def project(cam, p, res=None):
    """World point -> ((x_px, y_px), depth). Matches Blender's world_to_camera_view for PERSP and ORTHO cameras.
    `res` = (W, H) to scale to another frame size (default: the camera's own render resolution)."""
    W0, H0 = cam["res"]
    W, H = res or (W0, H0)
    R, T = cam.get("_inv") or _inv_rigid(cam["matrix_world"])
    cam["_inv"] = (R, T)
    c = [sum(R[i][k] * p[k] for k in range(3)) + T[i] for i in range(3)]
    depth = -c[2]
    pa = cam.get("pixel_aspect", [1.0, 1.0])
    aspx, aspy = W0 * pa[0], H0 * pa[1]
    fit = cam.get("sensor_fit", "AUTO")
    if fit == "AUTO":
        fit = "HORIZONTAL" if aspx >= aspy else "VERTICAL"
    sens = cam["sensor_width"] if (cam.get("sensor_fit", "AUTO") in ("AUTO", "HORIZONTAL")) else cam["sensor_height"]
    big = aspx if fit == "HORIZONTAL" else aspy               # the fitted dimension, in (aspect-corrected) pixels
    if cam.get("type") == "ORTHO":
        scale = big / cam["ortho_scale"]
        u, v = c[0] * scale, c[1] * scale
    else:
        if depth <= 1e-6:
            return (float("nan"), float("nan")), depth
        f = cam["lens"] / sens * big
        u, v = c[0] / depth * f, c[1] / depth * f
    u += cam.get("shift_x", 0.0) * big
    v += cam.get("shift_y", 0.0) * big
    x = (aspx / 2 + u) / pa[0]
    y = (aspy / 2 - v) / pa[1]
    return (x * W / W0, y * H / H0), depth


def point(cam, name):
    """Tracked world point stored by dump(track=...), or None."""
    return (cam.get("points") or {}).get(name)
