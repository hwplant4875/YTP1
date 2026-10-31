"""Autopilot 10/28: burn NAME TAGS (hud2 el_tag, Russo One, max 3 at once) into a rendered segment preview, from the
per-frame camera dumps render_seg.py writes (frames/_cam/NNNNN.json with the TRACK points).  CPU only.

    python tag_burn.py SEG FRAMES_DIR OUT_MP4 [--size 854x480]

Windows: part 2-3 segments (f*, s*) tag a tracker while it is valid (their TRACK functions return None outside the beat);
part 1 segments use the beat windows in PART1 below (segment-LOCAL seconds -> video seconds via segtime.to_video).
"""
import argparse, glob, os, subprocess, sys
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "aot"))
import hud2, hudcam  # noqa: E402
import segtime       # noqa: E402

TITANS = {"FEMALE", "ANNIE", "AttackTitan", "ARMORED TITAN", "COLOSSAL"}
# part 1: (tag text, tracker name, local t0, local t1) - from graphics_timelines/*_tags.json + the bible beats
PART1 = {
    "g2": [],                                 # v18: the Armored Titan gets the bottom-centre TITLE (like the Colossal), no tag
    "g3": [],                                 # v17 (FEEDBACK_v15): NO name tags on the training ground (empty list = none; absent = tracker tags)
    "g4": [("EREN", "Eren", 16.8, 19.7)],
    "g5": [("MIKASA", "Mikasa", 33.8, 39.0), ("MIKASA", "Mikasa", 50.0, 54.0)],
    "g6": [("EREN", "Eren", 48.6, 53.0), ("MIKASA", "Mikasa", 50.6, 53.5)],
    "g7": [("EREN", "EREN", 9.4, 13.4), ("MIKASA", "MIKASA", 9.8, 13.8), ("ARMIN", "ARMIN", 10.6, 14.6),
           ("PYXIS", "PYXIS", 14.0, 18.0), ("PYXIS", "PYXIS", 33.4, 37.4)],
    "g8": [("ARMIN", "Armin", 12.0, 15.0), ("LEVI", "Levi", 50.5, 54.5)],   # v14: ARMIN wakes Titan Eren
}


# v18 (FEEDBACK_v17): the COMPLETE on-screen text, in VIDEO seconds of each segment (segtime v18 clocks), canon order
# (SCENE_BIBLE_v2): bottom-centre captions (New Rocker) / titles, place + year HUD top-left (Share Tech), the 846 counter
# top-right; never two bottom-centre lines at once.
def _cap(t0, t1, text, size=26):
    return dict(type="caption", t0=t0, t1=t1, text=text, size=size)
def _title(t0, t1, text, sub=None, size=50):
    e = dict(type="title", text=text, t0=t0, t1=t1, size=size, y=0.86, shadow=True, scale_in=True)
    if sub:
        e["sub"] = sub
    return e
def _place(t0, t1, place, year):
    return dict(type="place", t0=t0, t1=t1, place=place, year=year, pos="tl")
CAPTIONS = {
    "g1": [_place(0.3, 4.2, "SHIGANSHINA DISTRICT", 845),
           _cap(0.6, 3.8, "Shiganshina, the southern tip of Wall Maria"),
           _title(5.6, 8.4, "Colossal Titan"),
           _cap(9.4, 12.4, "It kicks a hole in the outer gate"),
           _cap(12.8, 15.7, "Titans pour into the district")],
    "g2": [_cap(0.3, 2.8, "The survivors flee to the boats"),
           _title(3.2, 6.4, "Armored Titan"),
           _cap(7.7, 10.8, "The inner gate is broken. Wall Maria has fallen"),
           _cap(11.3, 14.6, "Humanity retreats behind Wall Rose")],
    "g3": [_place(2.6, 5.3, "TROST DISTRICT  ·  WALL ROSE", 846),
           _cap(2.9, 5.3, "Refugees clear new farmland to survive"),
           _cap(5.6, 8.6, "250,000 refugees are sent to retake Wall Maria"),
           dict(type="counter", t0=8.6, t1=19.2, **{"from": 250000}, to=200, run=[9.8, 17.6], mode="linear", round=10,
                label="Still marching", label_end="Came back", approx_end=True, color_end="red", bar=True, pos="tr", scale=1.0),
           _cap(15.9, 18.9, "Almost all of them are eaten"),
           _place(22.6, 25.6, "104TH TRAINING CORPS", 847),
           _cap(23.4, 25.5, "Eren, Mikasa and Armin enlist"),
           _cap(25.8, 27.6, "850: the 104th graduates")],
    "g4": [_place(0.2, 3.2, "TROST DISTRICT", 850),
           _cap(0.4, 3.4, "The Survey Corps rides out of Trost")],
    "g5": [_cap(0.3, 3.3, "Five years later, the Colossal Titan returns"),
           _cap(3.8, 6.8, "Trost's outer gate is broken"),
           _cap(7.3, 10.4, "The cadets of the 104th are thrown into the fight"),
           _cap(18.8, 21.8, "Mikasa clears the jammed inner gate"),
           _title(30.3, 33.3, "Attack Titan", sub="a titan that hunts titans"),
           _cap(33.8, 37.0, "Eren's titan form")],
    "g6": [_place(0.2, 3.2, "SUPPLY HEADQUARTERS", 850),
           _cap(2.4, 5.6, "The cadets lure the titans into the supply depot"),
           _cap(6.0, 8.6, "Seven shots, seven napes"),
           _cap(10.2, 13.4, "Eren comes out of the titan's nape")],
    "g7": [_cap(1.9, 4.7, "The Garrison opens fire. Eren's half-shift shields them"),
           _cap(5.3, 8.4, "Commander Pyxis takes over"),
           _cap(12.5, 15.6, "The plan: seal the breach with a boulder")],
    "g8": [_cap(2.3, 5.2, "Eren transforms and loses control"),
           _cap(6.0, 9.0, "Armin wakes him up"),
           _cap(9.9, 13.2, "Eren carries the boulder to the gate"),
           _cap(16.8, 20.0, "The breach is sealed. Humanity's first victory"),
           _cap(23.8, 27.2, "The titans left in Trost are wiped out"),
           _cap(27.8, 32.6, "The fallen are burned"),
           _title(33.6, 37.0, "Wall Maria  ·  Wall Rose  ·  Wall Sina", size=40),
           _cap(37.1, 39.0, "Trost is recaptured. The fight goes on")],
}

def valid(cam, nm):
    p = hudcam.point(cam, nm) if cam else None
    return p is not None and p[2] > -900.0

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("seg"); ap.add_argument("frames"); ap.add_argument("out")
    ap.add_argument("--size", default="854x480"); ap.add_argument("--fps", type=int, default=15)
    A = ap.parse_args()
    W, H = map(int, A.size.split("x"))
    files = sorted(glob.glob(os.path.join(A.frames, "f_*.png"))) or sorted(glob.glob(os.path.join(A.frames, A.seg + "_*.png")))
    idx = [int(os.path.splitext(os.path.basename(f))[0].split("_")[-1]) for f in files]
    cams, last = {}, None
    for i in idx:
        c = hudcam.load(A.frames, i)
        last = c or last
        cams[i] = last
    tracks = []
    if A.seg in PART1:
        for name, obj, a, b in PART1[A.seg]:
            tracks.append(dict(type="tag", name=name, obj=obj, t0=segtime.to_video(A.seg, a), t1=segtime.to_video(A.seg, b)))
    else:                                     # validity spans (gaps < 0.4 s merged, spans < 0.8 s dropped)
        names = sorted({n for c in cams.values() if c for n in (c.get("points") or {})})
        for nm in names:
            spans, cur = [], None
            for i in idx:
                t = i / A.fps
                if not valid(cams[i], nm):
                    continue
                if cur is not None and t - cur[1] < 0.4:
                    cur[1] = t
                else:
                    if cur is not None:
                        spans.append(cur)
                    cur = [t, t]
            if cur is not None:
                spans.append(cur)
            for a, b in spans:
                if b - a >= 0.8:
                    tracks.append(dict(type="tag", name=nm.upper(), obj=nm, t0=a, t1=b))
    for e in tracks:
        e.update(color="red" if e["obj"] in TITANS else "cream", len=30, size=15)
    extra = []
    extra += [dict(e) for e in CAPTIONS.get(A.seg, [])]      # v18: the complete caption / title / place / counter table
    if A.seg == "g3" and A.seg not in CAPTIONS:                        # captions + the 250,000 "Still marching" counter + place label (owner 10/27)
        import json, numpy as np
        tl = json.load(open(os.path.join(HERE, "graphics_timelines", "g3_tags.json"), encoding="utf8"))
        k6 = segtime.ramp_knots(segtime.DUR["g3"], [(segtime.G3_MARCH[0], segtime.G3_MARCH[1], 1.0)], ramp=1.0)   # the v6 clock
        def remap(tv):
            loc = float(np.interp(tv, [a for a, b in k6], [b for a, b in k6]))
            return segtime.to_video("g3", loc)
        for e in tl["tracks"]:
            if e["type"] != "tag":
                e = dict(e); e["t0"], e["t1"] = remap(e["t0"]), remap(e["t1"]); extra.append(e)
        print("[tags] g3 extras: " + ", ".join(f"{e['type']} {e['t0']:.1f}-{e['t1']:.1f}" for e in extra), flush=True)
    print(f"[tags] {A.seg}: " + ", ".join(f"{e['name']} {e['t0']:.1f}-{e['t1']:.1f}" for e in tracks), flush=True)
    ff = subprocess.Popen(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                           "-s", f"{W}x{H}", "-r", str(A.fps), "-i", "-", "-c:v", "libx264", "-crf", "26", "-pix_fmt", "yuv420p",
                           A.out], stdin=subprocess.PIPE)
    for f, i in zip(files, idx):
        t = i / A.fps
        img = Image.open(f).convert("RGB")
        if img.size != (W, H):
            img = img.resize((W, H), Image.BILINEAR)
        cam = cams[i]
        act = [e for e in tracks if e["t0"] - 0.05 <= t <= e["t1"] + 0.4 and ("screen" in e or valid(cam, e["obj"]))]
        act = sorted(act, key=lambda e: e["t0"])[:3]          # max 3 tags on screen
        act = [dict(e, len=28 + 20 * k, lean=(14 if k % 2 == 0 else -14)) for k, e in enumerate(act)]   # de-clutter stacked tags
        ex = [e for e in extra if e["t0"] - 0.05 <= t <= e["t1"] + 0.5]
        if (act and (cam or all("screen" in e for e in act))) or ex:
            if cam:
                cam = dict(cam); cam["res"] = [W, H]
            img = hud2.compose(dict(fps=A.fps, tracks=act + ex), img, i, t=t, cam=cam)
        ff.stdin.write(img.tobytes())
    ff.stdin.close(); ff.wait()
    print(f"[tags] -> {A.out}", flush=True)

if __name__ == "__main__":
    main()
