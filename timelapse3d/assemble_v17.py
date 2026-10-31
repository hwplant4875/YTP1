"""v17 full one-take (Stohess v15 sky fight s1v15 + s2v15) assembly (CPU only): name tags burnt into every segment render, plain concat (no dissolves, FEEDBACK_v13),
contact sheet + key-moment grid, copied to renders/laptop.  Waits for missing segment previews (polls).
    python assemble_v15.py [--wait]        SEGS below = (seg, render dir) in film order
"""
import os, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
R = "E:/YTP2/3D Timelapse/renders"
SEGS = [("g1", f"{R}/g1_fall_v9"), ("g2", f"{R}/g2_armored_v9"), ("g3", f"{R}/g3_flight_v14"), ("g4", f"{R}/g4_trost850_v9"),
        ("g5", f"{R}/g5_trost_v13"), ("g6", f"{R}/g6_hq_v10"), ("g7", f"{R}/g7_basin_v7"), ("g8", f"{R}/g8_boulder_v9"),
        ("f0", f"{R}/part2/f0_v7"), ("f1", f"{R}/part2/f1_v13"), ("f2", f"{R}/part2/f2_v11"), ("f3v17", f"{R}/part2/f3v17_v1"),
        ("s1v15", f"{R}/part2/s1v15_v2"), ("s2v15", f"{R}/part2/s2v15_v2")]
OUT = f"{R}/full_v17/full_onetake_v17_preview.mp4"
LAP = os.path.join(HERE, "renders", "laptop")

def dur(f):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f]).decode().strip())

def main():
    if "--wait" in sys.argv:
        while not all(os.path.exists(f"{d}/{g}_preview.mp4") for g, d in SEGS):
            time.sleep(60)
        time.sleep(30)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    ins = []
    for g, d in SEGS:
        tg = f"{d}/{g}_tagged.mp4"
        if not os.path.exists(tg) or os.path.getmtime(tg) < os.path.getmtime(f"{d}/{g}_preview.mp4"):
            r = subprocess.call([sys.executable, os.path.join(HERE, "tag_burn.py"), g, f"{d}/frames", tg])
            if r != 0 or not os.path.exists(tg):
                print(f"[v17] tags FAILED {g}, using the plain preview", flush=True); tg = f"{d}/{g}_preview.mp4"
        ins.append((g, tg))
    subprocess.check_call(["bash", os.path.join(HERE, "concat_v14.sh"), OUT] + [f for _, f in ins])
    # key moments (segment start + offset in video seconds)
    starts, t = {}, 0.0
    for g, f in ins:
        starts[g] = t; t += dur(f)
    km = [("g2", 4.0), ("g3", 3.0), ("g3", 9.0), ("g3", 20.0), ("g3", 27.5), ("g5", 2.0), ("g8", 9.0), ("g8", 24.0),
          ("f1", 5.0), ("f2", 2.0), ("f3v17", 7.2), ("f3v17", 11.6), ("s2v15", 4.4), ("s2v15", 5.6), ("s2v15", 12.0), ("s2v15", 19.5)]
    os.makedirs(f"{R}/full_v17/km", exist_ok=True)
    shots = []
    for k, (g, o) in enumerate(km):
        p = f"{R}/full_v17/km/{k:02d}.jpg"
        subprocess.call(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{starts[g] + o:.2f}", "-i", OUT, "-frames:v", "1", "-vf", "scale=427:-2", p])
        if os.path.exists(p):
            shots.append(p)
    kmj = OUT.replace("_preview.mp4", "_keymoments.jpg")
    subprocess.call([sys.executable, os.path.join(HERE, "tools_tile.py"), kmj, "4", "427"] + shots)
    import shutil
    for f in (OUT, OUT.replace("_preview.mp4", "_sheet.jpg"), kmj):
        shutil.copy(f, LAP)
    names = [os.path.basename(f) for f in (OUT, OUT.replace("_preview.mp4", "_sheet.jpg"), kmj)]
    os.chdir(HERE)
    subprocess.call(["git", "add"] + [f"renders/laptop/{n}" for n in names])
    subprocess.call(["git", "commit", "-q", "-m", "full_onetake_v17 preview (v17: FEEDBACK_v15 part 1 fixes, f1 Female cut, f3 rebuilt from the sky)\n\n"
                     "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>", "--"] + [f"renders/laptop/{n}" for n in names])
    subprocess.call(["git", "pull", "-q", "--rebase", "--autostash", "origin", "claude/project-thread-4b2beh"])
    subprocess.call(["git", "push", "-q", "origin", "claude/project-thread-4b2beh"])
    print(f"[v17] DONE {OUT} {dur(OUT):.1f} s", flush=True)

if __name__ == "__main__":
    main()
