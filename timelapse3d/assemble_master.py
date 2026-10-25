"""EP1 MASTER ASSEMBLY (agent G): segments + bridges -> one take, ONE hud2 overlay timeline, one H.264 file.

    python assemble_master.py                    full preview: 854x480, 15 fps, CRF 26 -> renders/master/master_preview.mp4
                                                 + renders/master/master_contact.jpg (one frame every 5 s)
    python assemble_master.py --no-hud           without the overlay (camera / seam check)
    python assemble_master.py --range 30,80      only master seconds 30-80 (-> master_preview_30-80.mp4)
    python assemble_master.py --fps 30 --size 1920x1080 --crf 18 --out .../master_final.mp4      (final, later)
CPU only (PIL / numpy / ffmpeg).  Steps:
  1. extracts each segment's preview mp4 into renders/master/cache/ (used only where the PNG frames are missing,
     e.g. while the owning agent re-renders);
  2. master_timeline.build(): trims every segment to its master window, slots the connectors, dark cards for missing parts;
  3. resolves master_overlay.json (segment-local times -> master seconds; tracks of missing segments are dropped);
  4. per frame: source frame (or card) -> hud2.compose with the master overlay and that frame's hudcam dump (name tags) -> ffmpeg stdin.
"""
import argparse, json, math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "aot"))
import hud2, hudcam                      # noqa: E402
import master_timeline as MT             # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--fps", type=int, default=15)
ap.add_argument("--size", default="854x480")
ap.add_argument("--crf", type=int, default=26)
ap.add_argument("--out", default=MT.MASTER + "/master_preview.mp4")
ap.add_argument("--overlay", default=os.path.join(HERE, "master_overlay.json"))
ap.add_argument("--no-hud", action="store_true")
ap.add_argument("--range", default="")
ap.add_argument("--sheet-every", type=float, default=5.0)
A = ap.parse_args()
FPS = A.fps
WW, HH = map(int, A.size.split("x"))
os.makedirs(MT.MASTER, exist_ok=True)

# ---------------------------------------------------------------- 1. mp4 fallbacks -> cache
def ensure_cache():
    for sid, lst in MT.FALLBACK_MP4.items():
        for mp4 in lst:
            if not os.path.exists(mp4):
                continue
            d = MT.cache_dir(mp4)
            stamp = os.path.join(d, ".src_mtime")
            mt = str(os.path.getmtime(mp4))
            if os.path.exists(stamp) and open(stamp).read() == mt:
                continue
            os.makedirs(d, exist_ok=True)
            for f in os.listdir(d):
                os.remove(os.path.join(d, f))
            start = MT.FALLBACK_START.get(os.path.basename(mp4), 0)
            subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", mp4, "-start_number", str(start),
                            os.path.join(d, "%05d.png")], check=True)
            open(stamp, "w").write(mt)
            print(f"[master] cached {mp4} -> {d} ({len(os.listdir(d)) - 1} frames)", flush=True)

ensure_cache()
rows = MT.build(FPS)
ROW = {r["id"]: r for r in rows}

# ---------------------------------------------------------------- 2. the master frame list
FONT = os.path.join(HERE, "fonts", "ShareTech-Regular.ttf")
def card_frame(lines, k):
    img = Image.new("RGB", (WW, HH), (16, 16, 20))
    d = ImageDraw.Draw(img)
    s = HH / 480
    f1, f2 = ImageFont.truetype(FONT, int(22 * s)), ImageFont.truetype(FONT, int(14 * s))
    d.rectangle([0, HH * 0.42 - 26 * s, WW, HH * 0.42 - 24 * s], fill=(70, 60, 40))
    d.text((WW / 2, HH * 0.42), lines[0], font=f1, fill=(214, 176, 102), anchor="mm")
    for i, ln in enumerate(lines[1:]):
        d.text((WW / 2, HH * 0.42 + (34 + 22 * i) * s), ln, font=f2, fill=(180, 174, 160), anchor="mm")
    return img

FR = []        # dicts: m (master s), src | card, cams, seg, lt (segment-local s), cloud (bridge info)
for r in rows:
    s = MT.SEG[r["id"]]
    if r["kind"] == "segment":
        cams = s.get("cams")
        if r["id"] == "opening":
            cams = MT.R + "/graphics/opening_v3_cam"
        for k in range(r["n"]):
            i = r["i_in"] + k
            FR.append(dict(src=MT.frame_path(s, i), cams=(cams, i) if cams else None, seg=r["id"], lt=i / FPS))
        if r.get("card"):
            miss = r["planned"] - r["dur"]
            lines = [f"[ {s['label']} ]",
                     f"{'missing' if r['n'] == 0 else 'not rendered yet from i=%d' % (r['i_avail'] + 1)}: {miss:.1f} s planned  ·  owner {s['owner']}",
                     "temporary placeholder card (agent G master preview)"]
            for k in range(int(round(MT.PLACEHOLDER_S * FPS))):
                FR.append(dict(card=lines, seg=r["id"], lt=None))
    else:
        for j, tb, half in MT.bridge_frames(s, FPS):
            p = f"{MT.bridge_dir(s)}/br_{j:05d}.png"
            ok = os.path.exists(p)
            FR.append(dict(src=p if ok else None, card=None if ok else [f"[ {s['label']} ]",
                           f"bridge half '{half}' ({s['halves'][half]['world']} world) not rendered yet", "bash render_bridge.sh"],
                           cams=(MT.bridge_dir(s), j) if ok else None, seg=r["id"], lt=tb))
for k, f in enumerate(FR):
    f["m"] = k / FPS
TOTAL = len(FR) / FPS

# ---------------------------------------------------------------- 3. overlay: segment-local -> master seconds
def seg_master(sid):
    """(m_in, local_in, local_avail_end) of a segment's kept frames, or None when it has none."""
    r = ROW.get(sid)
    if not r or r["kind"] != "segment" or r["n"] == 0:
        return None
    return r["m_in"], r["i_in"] / FPS, (r["i_in"] + r["n"] - 1) / FPS

def resolve_overlay(path):
    ov = json.load(open(path, encoding="utf8"))
    out = []
    for e in ov["tracks"]:
        e = dict(e); sid = e.pop("seg")
        sm = seg_master(sid)
        if sm is None:
            continue
        m_in, l_in, l_end = sm
        if "T0" in e:                                  # Trost action time -> video seconds
            e["t0"], e["t1"] = MT.trost_v(e.pop("T0")), MT.trost_v(e.pop("T1"))
            if "run" in e:
                e["run"] = [MT.trost_v(x) for x in e["run"]]
            if "note_t" in e:
                e["note_t"] = MT.trost_v(e["note_t"])
        conv = lambda x: m_in + (x - l_in)
        if e["type"] == "glitch":
            if not (l_in <= e["t"] <= l_end):
                continue
            e["t"] = conv(e["t"]); out.append(e); continue
        if e["type"] == "fade":
            for k in ("in", "out"):
                if k in e:
                    e[k] = [conv(x) for x in e[k]]
            out.append(e); continue
        t0, t1 = max(e.get("t0", l_in), l_in), min(e.get("t1", l_end + 1 / FPS), l_end + 1 / FPS)
        if t1 - t0 < 0.3:
            continue
        if e.get("t0", l_in) < l_in:
            e["fade_in"] = 0                          # the track continues from the previous material
        e["t0"], e["t1"] = conv(t0), conv(t1)
        for k in ("note_t",):
            if k in e:
                e[k] = conv(e[k])
        if "run" in e:
            e["run"] = [conv(x) for x in e["run"]]
        if e.get("alive"):
            e["_alive_seg"] = (m_in, l_in)
        out.append(e)
    return out

TRACKS = [] if A.no_hud else resolve_overlay(A.overlay)
ALIVE = None
ap_ = MT.R + "/march846/march846_alive.json"
if os.path.exists(ap_):
    j = json.load(open(ap_))
    ALIVE = (np.array([f["t"] for f in j["frames"]]), np.array([f["alive"] for f in j["frames"]], float))
json.dump(dict(fps=FPS, total=TOTAL, rows=rows, tracks=TRACKS), open(MT.MASTER + "/master_overlay_resolved.json", "w"),
          indent=1, default=str)

def _inv_ease(u):
    lo, hi = 0.0, 1.0
    for _ in range(40):
        mid = (lo + hi) / 2
        if hud2.ease(mid) < u: lo = mid
        else: hi = mid
    return (lo + hi) / 2

def tracks_at(t):
    act = []
    for e in TRACKS:
        if e["type"] == "glitch":
            if e["t"] - 0.1 <= t <= e["t"] + e.get("dur", 0.6) + 0.1:
                act.append(e)
            continue
        if e["type"] == "fade":
            if any(k in e and e[k][0] - 0.05 <= t <= e[k][1] + 0.05 for k in ("in", "out")):
                act.append(e)
            continue
        if not (e["t0"] - 0.01 <= t <= e["t1"] + 0.01):
            continue
        if e.get("alive") and ALIVE is not None:   # counter follows march846.alive(t) exactly
            m_in, l_in = e["_alive_seg"]
            n = float(np.interp(t - m_in + l_in, *ALIVE))
            u = (e["from"] - n) / (e["from"] - e["to"])
            if u >= 1 - 1e-6:
                e = dict(e, run=[t - 2.0, t - 1.0])
            else:
                raw = _inv_ease(max(0.0, u)) if u > 0 else 0.0
                e = dict(e, run=[t - raw, t - raw + 1.0])
        act.append(e)
    return act

# (4. the cloud whiteout was removed: STRICT ONE TAKE, HANDOFF 10/25 09:37 - seams are matched cameras)

# ---------------------------------------------------------------- 5. encode
r0, r1 = (0.0, TOTAL)
if A.range:
    r0, r1 = map(float, A.range.split(","))
    A.out = A.out[:-4] + f"_{int(r0)}-{int(r1)}.mp4"
TL = dict(fps=FPS, tracks=[])
sheet = []
ff = subprocess.Popen(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                       "-s", f"{WW}x{HH}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", str(A.crf),
                       "-preset", "medium", "-pix_fmt", "yuv420p", "-movflags", "+faststart", A.out], stdin=subprocess.PIPE)
last_card = None
n_out = 0
for k, f in enumerate(FR):
    if not (r0 - 1e-6 <= f["m"] < r1):
        continue
    if f.get("src"):
        img = Image.open(f["src"]).convert("RGB")
        if img.size != (WW, HH):
            img = img.resize((WW, HH), Image.LANCZOS)
    else:
        img = card_frame(f["card"], k)
    act = tracks_at(f["m"]) if f.get("src") else []
    if act:
        cam = hudcam.load(*f["cams"]) if f.get("cams") else None
        TL["tracks"] = act
        img = hud2.compose(TL, img, k, t=f["m"], cam=cam)
    ff.stdin.write(img.tobytes())
    n_out += 1
    if A.sheet_every and ((k - 8) % int(round(A.sheet_every * FPS)) == 0):
        th = img.resize((284, 160), Image.LANCZOS)
        sheet.append((th, f"{MT.fmt_t(f['m'])}  {f['seg']}" + (f" t={f['lt']:.1f}" if f.get("lt") is not None else "")))
    if n_out % 150 == 0:
        print(f"[master] {n_out} frames ({MT.fmt_t(f['m'])})", flush=True)
ff.stdin.close(); ff.wait()
print(f"[master] wrote {A.out}: {n_out} frames, {n_out / FPS:.2f} s", flush=True)

# ---------------------------------------------------------------- 6. contact sheet
if sheet:
    cols = 6; rws = (len(sheet) + cols - 1) // cols
    S = Image.new("RGB", (cols * 288 + 4, rws * 184 + 4), (12, 12, 14))
    d = ImageDraw.Draw(S); fnt = ImageFont.truetype(FONT, 13)
    for i, (th, lab) in enumerate(sheet):
        x, y = 4 + (i % cols) * 288, 4 + (i // cols) * 184
        S.paste(th, (x, y)); d.text((x + 2, y + 163), lab, font=fnt, fill=(214, 176, 102))
    sp = A.out[:-4].replace("master_preview", "master_contact") + ".jpg"
    if sp == A.out[:-4] + ".jpg":
        sp = A.out[:-4] + "_contact.jpg"
    S.save(sp, quality=86)
    print(f"[master] contact sheet {sp} ({len(sheet)} frames, every {A.sheet_every:g} s)")
