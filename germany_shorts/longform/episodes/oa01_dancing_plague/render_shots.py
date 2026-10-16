"""Render every shot of timeline.json at 720x1280, 24 fps, two Chromium processes at a time. Cached per shot+length+scene."""
import concurrent.futures as cf, hashlib, json, os, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); LF = os.path.dirname(os.path.dirname(HERE))
TL = json.load(open(os.path.join(HERE, "timeline.json"))); OUT = os.path.join(HERE, ".shots"); os.makedirs(OUT, exist_ok=True)
src = b"".join(open(os.path.join(LF, f), "rb").read() for f in ("scenes/oa_dance.js", "scenes/lib_human.js", "render.mjs"))
H = hashlib.sha1(src).hexdigest()[:8]
only = sys.argv[1:]
def job(k, sp):
    dur = round(sp["dur"] + 0.05, 3)
    out = os.path.join(OUT, f"{k:02d}_{sp['shot']}_{dur}_{H}.mp4")
    if os.path.exists(out): return out, 0
    t = time.time()
    r = subprocess.run(["node", "render.mjs", "scenes/oa_dance.js", out + ".part.mp4", "--w", "720", "--h", "1280", "--fps", "24", "--dur", str(dur),
                        "--shot", f"{sp['shot']}:{dur}"], cwd=LF, capture_output=True, text=True)
    if r.returncode: print(r.stdout[-800:], r.stderr[-800:]); raise SystemExit(sp["shot"])
    os.replace(out + ".part.mp4", out); return out, time.time() - t
T0 = time.time()
with cf.ThreadPoolExecutor(2) as ex:
    futs = {ex.submit(job, k, sp): sp for k, sp in enumerate(TL["spans"]) if not only or sp["shot"] in only}
    for f in cf.as_completed(futs):
        o, dt = f.result(); print(f"{os.path.basename(o)}  {dt:.0f}s", flush=True)
print(f"all shots {time.time() - T0:.0f}s")
