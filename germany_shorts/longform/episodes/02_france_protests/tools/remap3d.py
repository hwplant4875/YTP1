"""Re-key cached 3D renders after a scene edit that does not change the picture (e.g. a render-speed optimisation).

  python3 tools/remap3d.py SCENE OLD_SCENE_JS SCRIPT_JSON TIMELINE_JSON
Hard-links every cached shot of SCENE rendered with OLD_SCENE_JS to the key the current scene file gives it.
"""
import hashlib, json, os, sys
LF = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, LF)
import assemble as A  # noqa: E402

scene, old_js, spec_p, tl_p = sys.argv[1:5]
def shash(js_bytes):
    h = hashlib.sha1(); h.update(js_bytes)
    for f in ("scenes/lib.js", "scenes/look.js", "render.mjs"):
        p = os.path.join(LF, f)
        if os.path.exists(p):
            h.update(open(p, "rb").read())
    return h.hexdigest()[:10]
old_h = shash(open(old_js, "rb").read())
new_h = A.scene_hash(scene)
spec, tl = json.load(open(spec_p)), json.load(open(tl_p))
beats = spec["beats"][:len(tl["beats"])]
shots = []
for b, t in zip(beats, tl["beats"]):
    v = b.get("visual", "same")
    if v == "same" and shots:
        shots[-1][2] = t["end"]
    else:
        shots.append([v, t["start"], t["end"]])
shots[-1][2] = tl["total"]
for v, s, e in shots:
    if not isinstance(v, dict) or v.get("type") != "3d" or v["scene"] != scene:
        continue
    d0 = e - s   # timeline.json is rounded to 0.01 s: search the exact 3-decimal duration the cache was keyed with
    name = lambda h, d: os.path.join(A.CACHE, f"3d_{scene}_{v.get('shot', '')}_{A.key(v, round(d, 3), h, *A.SIZE_KEY)}.mp4")
    hit = [d0 + k / 1000 for k in range(-15, 16) if os.path.exists(name(old_h, d0 + k / 1000))]
    if not hit:
        print("not cached", v.get("shot"), round(d0, 2)); continue
    o, n = name(old_h, hit[0]), name(new_h, hit[0])
    if o != n and not os.path.exists(n):
        os.link(o, n); print("linked", os.path.basename(n))
    else:
        print("already keyed", v.get("shot"))
