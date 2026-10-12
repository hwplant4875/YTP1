"""Register cached 3D renders in cache/3d_index.json (used by assemble's "reuse_3d" option) from an earlier
script.json + its timeline.json, so a retimed script can reuse them.

  LONGFORM_CACHE=... python3 tools/seed_3d_index.py SCRIPT_JSON TIMELINE_JSON [more SCRIPT TIMELINE pairs]
"""
import json, os, sys
LF = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, LF)
import assemble as A  # noqa: E402

a = sys.argv[1:]
n = 0
for spec_p, tl_p in zip(a[::2], a[1::2]):
    spec, tl = json.load(open(spec_p)), json.load(open(tl_p))
    shots = []
    for b, t in zip(spec["beats"][:len(tl["beats"])], tl["beats"]):
        v = b.get("visual", "same")
        if v == "same" and shots:
            shots[-1][2] = t["end"]
        else:
            shots.append([v, t["start"], t["end"]])
    shots[-1][2] = tl["total"]
    for v, s, e in shots:
        if not isinstance(v, dict) or v.get("type") != "3d":
            continue
        h = A.scene_hash(v["scene"])
        for k in range(-20, 21):
            d = e - s + k / 1000
            name = f"3d_{v['scene']}_{v.get('shot', '')}_{A.key(v, round(d, 3), h, *A.SIZE_KEY)}.mp4"
            if os.path.exists(os.path.join(A.CACHE, name)):
                A.record_3d(name, v, d, h); n += 1
                break
        else:
            print("not cached:", v["scene"], v.get("shot"), round(e - s, 2))
print(n, "renders indexed")
