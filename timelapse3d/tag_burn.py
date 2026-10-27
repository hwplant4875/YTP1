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

TITANS = {"FEMALE", "ANNIE", "AttackTitan"}
# part 1: (tag text, tracker name, local t0, local t1) - from graphics_timelines/*_tags.json + the bible beats
PART1 = {
    "g3": [("SHADIS", "Shadis", 55.6, 58.6), ("EREN", "Eren", 55.8, 58.8), ("MIKASA", "Mikasa", 56.0, 58.8)],
    "g4": [("EREN", "Eren", 16.8, 19.7)],
    "g5": [("MIKASA", "Mikasa", 33.8, 39.0), ("MIKASA", "Mikasa", 50.0, 54.0)],
    "g6": [("EREN", "Eren", 48.6, 53.0), ("MIKASA", "Mikasa", 50.6, 53.5)],
    "g7": [("EREN", "EREN", 9.4, 13.4), ("MIKASA", "MIKASA", 9.8, 13.8), ("ARMIN", "ARMIN", 10.6, 14.6),
           ("PYXIS", "PYXIS", 14.0, 18.0), ("PYXIS", "PYXIS", 33.4, 37.4)],
    "g8": [("LEVI", "Levi", 50.5, 54.5)],
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
    files = sorted(glob.glob(os.path.join(A.frames, "f_*.png")))
    idx = [int(os.path.basename(f)[2:7]) for f in files]
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
        act = [e for e in tracks if e["t0"] - 0.05 <= t <= e["t1"] + 0.4 and valid(cam, e["obj"])]
        act = sorted(act, key=lambda e: e["t0"])[:3]          # max 3 tags on screen
        act = [dict(e, len=28 + 20 * k, lean=(14 if k % 2 == 0 else -14)) for k, e in enumerate(act)]   # de-clutter stacked tags
        if act and cam:
            cam = dict(cam); cam["res"] = [W, H]
            img = hud2.compose(dict(fps=A.fps, tracks=act), img, i, t=t, cam=cam)
        ff.stdin.write(img.tobytes())
    ff.stdin.close(); ff.wait()
    print(f"[tags] -> {A.out}", flush=True)

if __name__ == "__main__":
    main()
