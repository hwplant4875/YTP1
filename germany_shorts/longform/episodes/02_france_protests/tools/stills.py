"""Preview stills of the g2d graphics in script.json without a full render.

  python3 tools/stills.py OUTDIR [beat_index ...]      (needs out/full_work/timeline.json from an --only-audio run)
For every g2d shot (or overlay) it writes a contact strip of frames at 15 / 40 / 65 / 90 % of the shot.
"""
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
import graphics2d as G  # noqa: E402
from PIL import Image  # noqa: E402

spec = json.load(open(os.path.join(HERE, "script.json")))
tl = json.load(open(os.path.join(HERE, "out/full_work/timeline.json")))
gap = spec.get("gap", 0.05)
beats = spec["beats"]
for b, t in zip(beats, tl["beats"]):
    b["_start"], b["_end"] = t["start"], t["end"]
    b["_say_at"] = t["start"] + b.get("lead", 0)
    b["_say_d"] = (t["end"] - t["start"]) - b.get("lead", 0) - b.get("hold", 0) - gap if b.get("say") else 0
spec_m = importlib.util.spec_from_file_location("graphics", os.path.join(HERE, "graphics.py"))
mod = importlib.util.module_from_spec(spec_m)
spec_m.loader.exec_module(mod)
G.GRAPHICS.update(mod.GRAPHICS)

out = sys.argv[1]
only = set(map(int, sys.argv[2:]))
os.makedirs(out, exist_ok=True)


class Grab:
    def __init__(self):
        self.ims = []

    def write(self, im):
        self.ims.append(im.convert("RGB").resize((640, 360)))


shots = []
for i, b in enumerate(beats):
    v = b.get("visual", "same")
    if v != "same":
        shots.append([i, v, [b]])
    elif shots:
        shots[-1][2].append(b)
    if b.get("overlay"):
        n = b["overlay"].get("beats", 1)
        shots.append([i, {**b["overlay"], "type": "g2d", "alpha": True}, beats[i:i + n]])
for i, v, bs in shots:
    if not isinstance(v, dict) or v.get("type") != "g2d" or (only and i not in only):
        continue
    start, end = bs[0]["_start"], bs[-1]["_end"]
    d = end - start
    timing = [{"start": x["_start"] - start, "say_at": x["_say_at"] - start, "say_d": x["_say_d"], "say": x.get("say", ""),
               "end": x["_end"] - start} for x in bs]
    G.STILLS = [d * k for k in (0.15, 0.4, 0.65, 0.92)]
    g = Grab()
    G.GRAPHICS[v["name"]](v.get("args", {}), d, timing, HERE, g)
    strip = Image.new("RGB", (640 * len(g.ims), 360))
    for k, im in enumerate(g.ims):
        strip.paste(im, (640 * k, 0))
    strip.save(os.path.join(out, f"b{i:03d}_{v['name']}.jpg"), quality=85)
    print(i, v["name"], f"{d:.1f}s")
