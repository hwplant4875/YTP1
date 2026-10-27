"""EP1 MASTER ONE-TAKE ASSEMBLY (concat only, silent).  ffmpeg + PIL/numpy; no Blender, no GPU.

    python aot/assemble_master.py                      all 8 segments must exist (else exit 2)
    python aot/assemble_master.py --missing-ok         missing segments become a black slate (segment id) of the exact length
    python aot/assemble_master.py --missing-ok --seamcheck
    python aot/assemble_master.py --check              only verify the segment files / print the seam table (writes nothing)

Per segment renders/<g>/<g>_preview.mp4 (relative to E:/YTP2/3D Timelapse) must be 854x480 H.264 yuv420p 15 fps and last the
segtime duration +-1 frame (1/15 s).  The segments are joined with the concat demuxer (-c copy, lossless) when every stream
signature is identical (codec, profile, level, size, pix_fmt, fps, time base, avcC extradata); otherwise one re-encode to
H.264 CRF 26 yuv420p 15 fps 854x480 (a slate always forces that, its avcC differs).  No audio track.
Outputs in renders/master/: master_preview.mp4 (an old file is kept once as master_preview_old.mp4), master_sheet.jpg
(1 fps, scale=240:-1, tile=10xN), and with --seamcheck seams/seam_<a>_<b>.jpg + seams/seams.json.
Seam metric = mean absolute RGB difference (0-255) between the last frame of N and the first frame of N+1, printed beside the
normal frame-to-frame motion of each side (last two frames of N, first two of N+1) so a jump is judged against the pace.
Global seam times come from aot/segtime.py (cumulative durations).  Exit codes: 0 ok, 2 missing, 3 duration/size mismatch.
"""
import argparse, hashlib, json, math, os, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import segtime as ST                                   # noqa: E402

R = "E:/YTP2/3D Timelapse/renders"
MASTER = R + "/master"
FPS, W, H, CRF = 15, 854, 480, 26
TOL = 1.0 / FPS + 1e-4
FONT = os.path.join(os.path.dirname(HERE), "fonts", "NewRocker-Regular.ttf")


def run(cmd, **kw):
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kw)
    if r.returncode:
        raise RuntimeError("%s failed (%s): %s" % (cmd[0], r.returncode, r.stderr.decode("utf8", "replace")[-600:]))
    return r


def probe(path):
    """dict(duration, w, h, sig) of the first video stream, or None when the file is missing / unreadable."""
    if not os.path.exists(path):
        return None
    try:
        j = json.loads(run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                            "stream=codec_name,profile,level,width,height,pix_fmt,r_frame_rate,avg_frame_rate,time_base,nb_frames,duration"
                            ":format=duration", "-of", "json", path]).stdout)
        s = j["streams"][0]
        ed = run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=extradata", "-show_data",
                  "-of", "default=nw=1", path]).stdout
    except Exception as e:                              # noqa: BLE001
        print(f"  ffprobe failed for {path}: {e}")
        return None
    dur = float(s.get("duration") or j["format"]["duration"])
    nb = int(s["nb_frames"]) if s.get("nb_frames", "").isdigit() else None
    sig = [s["codec_name"], s.get("profile"), s.get("level"), s["width"], s["height"], s["pix_fmt"], s["r_frame_rate"],
           s["avg_frame_rate"], s["time_base"], hashlib.md5(ed).hexdigest()]
    return dict(duration=dur, nb=nb, w=s["width"], h=s["height"], sig=sig, fps=s["r_frame_rate"])


def make_slate(g, dur, out):
    from PIL import Image, ImageDraw, ImageFont
    os.makedirs(os.path.dirname(out), exist_ok=True)
    png = out[:-4] + ".png"
    im = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(im)
    try:
        f1, f2 = ImageFont.truetype(FONT, 120), ImageFont.truetype(FONT, 26)
    except Exception:                                   # noqa: BLE001
        f1 = f2 = ImageFont.load_default()
    for txt, f, y in ((g.upper(), f1, H // 2 - 20), (f"NOT RENDERED  -  {dur:.1f} s  -  {ST.fmt(ST.START[g])}", f2, H // 2 + 70)):
        w = d.textlength(txt, font=f)
        d.text(((W - w) / 2, y), txt, font=f, fill=(150, 150, 150), anchor="ls" if f is f1 else "ls")
    im.save(png)
    n = int(round(dur * FPS))
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-loop", "1", "-framerate", str(FPS), "-i", png, "-frames:v", str(n),
         "-c:v", "libx264", "-crf", str(CRF), "-pix_fmt", "yuv420p", "-r", str(FPS), "-an", out])


def frames_of(path, which, count=2):
    """first / last `count` frames of a video as float RGB arrays (last: decode with select on the final indices)."""
    import numpy as np
    pr = probe(path)
    n = pr["nb"] or int(round(pr["duration"] * FPS))
    idx = list(range(count)) if which == "first" else list(range(n - count, n))
    sel = "+".join(f"eq(n\\,{i})" for i in idx)
    raw = run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", path, "-vf", f"select='{sel}'", "-fps_mode", "passthrough",
               "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]).stdout
    a = np.frombuffer(raw, np.uint8)
    k = W * H * 3
    return [a[i * k:(i + 1) * k].reshape(H, W, 3).astype(np.float32) for i in range(len(a) // k)]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--missing-ok", action="store_true", help="fill a missing/unusable segment with a black slate of its exact duration")
    ap.add_argument("--seamcheck", action="store_true", help="side-by-side seam frames + mean abs diff per seam")
    ap.add_argument("--check", action="store_true", help="verify and print only, write nothing")
    ap.add_argument("--allow-mismatch", action="store_true", help="assemble even if a duration/size is out of tolerance (global times then drift)")
    ap.add_argument("--reencode", action="store_true", help="force the CRF 26 re-encode")
    ap.add_argument("--out", default=MASTER + "/master_preview.mp4")
    A = ap.parse_args()

    rows, bad = [], False
    print(f"{'seg':4} {'status':8} {'dur':>8} {'plan':>8} {'diff':>7}  size       global in -> out")
    for g in ST.ORDER:
        p = f"{R}/{g}/{g}_preview.mp4"
        pr = probe(p)
        plan = ST.DUR[g]
        r = dict(id=g, path=p, plan=plan, start=ST.START[g], end=ST.START[g] + plan, probe=pr, slate=False, issues=[])
        if pr is None:
            r["issues"].append("missing")
        else:
            if abs(pr["duration"] - plan) > TOL:
                r["issues"].append(f"duration {pr['duration']:.3f} vs {plan:.3f} ({(pr['duration'] - plan) * FPS:+.1f} frames)")
            if (pr["w"], pr["h"]) != (W, H):
                r["issues"].append(f"size {pr['w']}x{pr['h']}")
            if pr["fps"] != f"{FPS}/1":
                r["issues"].append(f"fps {pr['fps']}")
        rows.append(r)
        st = "ok" if not r["issues"] else ("MISSING" if pr is None else "MISMATCH")
        d = f"{pr['duration']:8.3f}" if pr else "       -"
        df = f"{(pr['duration'] - plan) * FPS:+6.1f}f" if pr else "      -"
        sz = f"{pr['w']}x{pr['h']}" if pr else "-"
        print(f"{g:4} {st:8} {d} {plan:8.3f} {df}  {sz:9}  {ST.fmt(r['start'])} -> {ST.fmt(r['end'])}" + ("   " + "; ".join(r["issues"]) if r["issues"] else ""))
    miss = [r for r in rows if r["probe"] is None]
    mism = [r for r in rows if r["probe"] is not None and r["issues"]]
    if miss and not A.missing_ok:
        print("missing segments:", ", ".join(r["id"] for r in miss), " (use --missing-ok for a slate)")
        return 2
    if mism and not A.allow_mismatch:
        print("duration/size mismatch:", ", ".join(r["id"] for r in mism), " (fix the render or pass --allow-mismatch)")
        return 3
    print(f"\nSEAMS (global master time; total {ST.fmt(ST.TOTAL)} = {ST.TOTAL:.1f} s)")
    for a, b in zip(rows[:-1], rows[1:]):
        print(f"  {a['id']}|{b['id']}  {b['start']:7.2f} s  ({ST.fmt(b['start'])})")
    if A.check:
        return 0

    os.makedirs(MASTER, exist_ok=True)
    for r in rows:
        if r["probe"] is None or (r["issues"] and not A.allow_mismatch):
            r["slate"] = True
            r["path"] = f"{MASTER}/slates/{r['id']}_slate.mp4"
            make_slate(r["id"], r["plan"], r["path"])
            r["probe"] = probe(r["path"])
    sigs = {json.dumps(r["probe"]["sig"]) for r in rows}
    lossless = len(sigs) == 1 and not A.reencode
    lst = MASTER + "/concat.txt"
    with open(lst, "w") as f:
        for r in rows:
            f.write("file '%s'\n" % r["path"].replace("'", "'\\''"))
    if os.path.exists(A.out) and A.out == MASTER + "/master_preview.mp4" and not os.path.exists(MASTER + "/master_preview_old.mp4"):
        shutil.copy2(A.out, MASTER + "/master_preview_old.mp4")
    base = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-an"]
    if lossless:
        print("\nconcat: identical stream signatures -> -c copy (lossless)")
        run(base + ["-c", "copy", "-movflags", "+faststart", A.out])
    else:
        why = "forced" if A.reencode else ("slate present" if any(r["slate"] for r in rows) else "stream signatures differ")
        print(f"\nconcat: re-encode H.264 CRF {CRF} yuv420p {FPS} fps ({why})")
        run(base + ["-vf", f"scale={W}:{H},fps={FPS}", "-c:v", "libx264", "-crf", str(CRF), "-pix_fmt", "yuv420p", "-movflags", "+faststart", A.out])
    out = probe(A.out)
    print(f"master: {A.out}  {out['duration']:.3f} s (planned {ST.TOTAL:.3f}, diff {(out['duration'] - ST.TOTAL) * FPS:+.1f} frames)  {out['w']}x{out['h']}")

    rowsn = math.ceil(out["duration"] / 10.0)
    sheet = MASTER + "/master_sheet.jpg"
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", A.out, "-vf", f"fps=1,scale=240:-1,tile=10x{rowsn}", "-frames:v", "1",
         "-update", "1", "-q:v", "3", sheet])
    print("sheet:", sheet)

    if A.seamcheck:
        from PIL import Image
        import numpy as np
        sd = MASTER + "/seams"
        os.makedirs(sd, exist_ok=True)
        res = []
        print(f"\nSEAMCHECK  mean abs RGB diff 0-255   (motion = frame-to-frame diff inside the segment at that end)")
        print(f"{'seam':7} {'global':>8} {'diff':>7} {'motion N':>9} {'motion N+1':>10}  note")
        for a, b in zip(rows[:-1], rows[1:]):
            fa, fb = frames_of(a["path"], "last"), frames_of(b["path"], "first")
            d = float(np.abs(fa[-1] - fb[0]).mean())
            ma = float(np.abs(fa[-1] - fa[-2]).mean()) if len(fa) > 1 else float("nan")
            mb = float(np.abs(fb[0] - fb[1]).mean()) if len(fb) > 1 else float("nan")
            note = "slate" if (a["slate"] or b["slate"]) else ("JUMP" if d > 3 * max(ma, mb, 1.0) else "")
            side = Image.new("RGB", (W * 2 + 8, H), (255, 0, 255))
            side.paste(Image.fromarray(fa[-1].astype(np.uint8)), (0, 0))
            side.paste(Image.fromarray(fb[0].astype(np.uint8)), (W + 8, 0))
            side.save(f"{sd}/seam_{a['id']}_{b['id']}.jpg", quality=88)
            res.append(dict(seam=f"{a['id']}_{b['id']}", global_s=b["start"], diff=round(d, 3), motion_a=round(ma, 3), motion_b=round(mb, 3), note=note))
            print(f"{a['id']}|{b['id']:3} {b['start']:8.2f} {d:7.2f} {ma:9.2f} {mb:10.2f}  {note}")
        json.dump(dict(seams=res, rows=[dict(id=r["id"], slate=r["slate"], issues=r["issues"]) for r in rows]), open(sd + "/seams.json", "w"), indent=1)
        print("seam images:", sd)
    return 0


if __name__ == "__main__":
    sys.exit(main())
