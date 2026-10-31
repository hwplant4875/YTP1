"""v16 full one-take (Stohess v15 sky fight s1v15 + s2v15) assembly (CPU only): name tags burnt into every segment render, plain concat (no dissolves, FEEDBACK_v13),
contact sheet + key-moment grid, copied to renders/laptop.  Waits for missing segment previews (polls).
    python assemble_v15.py [--wait]        SEGS below = (seg, render dir) in film order
"""
import os, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
R = "E:/YTP2/3D Timelapse/renders"
SEGS = [("g1", f"{R}/g1_fall_v9"), ("g2", f"{R}/g2_armored_v8"), ("g3", f"{R}/g3_flight_v13"), ("g4", f"{R}/g4_trost850_v9"),
        ("g5", f"{R}/g5_trost_v12"), ("g6", f"{R}/g6_hq_v9"), ("g7", f"{R}/g7_basin_v6"), ("g8", f"{R}/g8_boulder_v8"),
        ("f0", f"{R}/part2/f0_v7"), ("f1", f"{R}/part2/f1_v12"), ("f2", f"{R}/part2/f2_v10"), ("f3", f"{R}/part2/f3_v12"),
        ("s1v15", f"{R}/part2/s1v15_v2"), ("s2v15", f"{R}/part2/s2v15_v2")]
OUT = f"{R}/full_v16/full_onetake_v16_preview.mp4"
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
                print(f"[v16] tags FAILED {g}, using the plain preview", flush=True); tg = f"{d}/{g}_preview.mp4"
        ins.append((g, tg))
    subprocess.check_call(["bash", os.path.join(HERE, "concat_v14.sh"), OUT] + [f for _, f in ins])
    # key moments (segment start + offset in video seconds)
    starts, t = {}, 0.0
    for g, f in ins:
        starts[g] = t; t += dur(f)
    km = [("g1", 8.6), ("g2", 1.6), ("g3", 13.0), ("g5", 2.0), ("g8", 12.0), ("g8", 31.0), ("f1", 6.0), ("f1", 11.4),
          ("f1", 20.2), ("f2", 6.2), ("f3", 10.0), ("f3", 12.8), ("s1v15", 4.6), ("s2v15", 4.2), ("s2v15", 5.6), ("s2v15", 18.0)]
    os.makedirs(f"{R}/full_v16/km", exist_ok=True)
    shots = []
    for k, (g, o) in enumerate(km):
        p = f"{R}/full_v16/km/{k:02d}.jpg"
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
    subprocess.call(["git", "commit", "-q", "-m", "full_onetake_v16 preview (v16: Stohess 110 m sky fight, cathedral collapse, wall titan, f1 cuts)\n\n"
                     "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>", "--"] + [f"renders/laptop/{n}" for n in names])
    subprocess.call(["git", "pull", "-q", "--rebase", "--autostash", "origin", "claude/project-thread-4b2beh"])
    subprocess.call(["git", "push", "-q", "origin", "claude/project-thread-4b2beh"])
    print(f"[v16] DONE {OUT} {dur(OUT):.1f} s", flush=True)

if __name__ == "__main__":
    main()
