"""Shrink finished 3D renders in the cache (render.mjs writes crf 17; crf 21 is visually the same after the final
8 Mbps encode and saves ~45% disk). Cache keys do not depend on file contents, so files are replaced in place.

  python3 tools/compact_cache.py CACHE_DIR [--loop SECONDS --until FILE]
"""
import os, subprocess, sys, time

cache = sys.argv[1]
a = sys.argv[2:]
loop = float(a[a.index("--loop") + 1]) if "--loop" in a else 0
until = a[a.index("--until") + 1] if "--until" in a else None
done_p = os.path.join(cache, ".compacted")


def once():
    done = set(open(done_p).read().split("\n")) if os.path.exists(done_p) else set()
    for f in sorted(os.listdir(cache)):
        p = os.path.join(cache, f)
        if not f.startswith(("3d_", "3dpad_")) or not f.endswith(".mp4") or ".part" in f or f in done:
            continue
        if time.time() - os.path.getmtime(p) < 30:
            continue
        tmp = p + ".cmp.mp4"
        r = subprocess.run(["nice", "-n", "5", "ffmpeg", "-v", "error", "-y", "-i", p, "-c:v", "libx264", "-preset", "medium", "-crf", "21",
                            "-pix_fmt", "yuv420p", "-movflags", "+faststart", tmp])
        if r.returncode == 0 and os.path.getsize(tmp) < os.path.getsize(p):
            st = os.stat(p)
            os.replace(tmp, p)
            os.utime(p, (st.st_atime, st.st_mtime))
        elif os.path.exists(tmp):
            os.remove(tmp)
        with open(done_p, "a") as fh:
            fh.write(f + "\n")
        print("compacted", f, flush=True)


while True:
    once()
    if not loop or (until and os.path.exists(until)):
        break
    time.sleep(loop)
