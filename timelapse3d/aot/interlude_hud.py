"""HUD pass for the interlude via agent E's shared compositor (hud2.py, graphics_timeline.md).
    python aot/interlude_hud.py                     all frames in renders/interlude/raw -> hud/ + interlude_preview.mp4
    python aot/interlude_hud.py --stills RAW OUT    the int_tSS.ss.png stills (t read from the file name)
Timeline: aot/interlude_timeline.json (year HUD, the 250,000 -> ~100 counter, Eren / Mikasa / Armin tags).
"""
import glob, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import hud2, hudcam
from PIL import Image

TL = os.path.join(HERE, "interlude_timeline.json")

if __name__ == "__main__":
    tl = hud2.load(TL)
    if len(sys.argv) > 1 and sys.argv[1] == "--stills":
        raw, out = sys.argv[2], sys.argv[3]
        os.makedirs(out, exist_ok=True)
        for p in sorted(glob.glob(os.path.join(raw, "int_t*.png"))):
            stem = os.path.splitext(os.path.basename(p))[0]
            t = float(re.search(r"t([\d.]+)$", stem).group(1))
            try:
                cam = hudcam.load(raw, stem)
            except Exception:
                cam = None
            hud2.compose(tl, Image.open(p).convert("RGB"), 0, t, cam=cam).save(os.path.join(out, stem + ".jpg"), quality=90)
            print("[hud]", stem)
    else:
        hud2.render(tl)
