"""EP1 MASTER TIMELINE (agent G, integrator; v2 = SCENE_BIBLE_v2 A1/A2): one continuous camera take, title to the end of Trost.

Pure Python (no bpy): importable by render_bridge.py inside Blender and by assemble_master.py / the shell outside it.

    python aot/master_timeline.py              print the master table (video in/out, source window, keys, status),
                                               the seams and the pace budget; writes renders/master/master_timeline.json
    python aot/master_timeline.py --fps 30     the same at the final frame rate

Model (v2)
----------
SEGMENTS = g1..g8 in canon order, durations and global starts from aot/segtime.py (A1 TIGHT table, 7:02; one-place re-time) and
seams from segtime.SEAMS (A2).  Seams are EXACT (position, look-at, lens, velocity), so the assembly concatenates the segment
mp4s / frames directly: no connector is needed (EXACT_SEAMS = True).  Each segment renders to
renders/<seg>/<seg>_preview.mp4 (g3 contains march846 as its own run: renders/march846/march846_preview.mp4).
The old connector / bridge machinery (SEGMENTS entries with bridge=True, render_bridge.py) is kept for a segment pair whose
seam turns out not to match; add such an entry between the two segments and it is rendered and slotted in again.
Frames: W = Shiganshina world, M = Trost master (M = W - (0, 4130)), trost.py set = (X, Y - 870, Z); see segtime.py.
Video seconds = 30 fps final; previews run at 15 fps (frame index = round(t * fps)).
Missing segments become short dark placeholder cards in the preview (PLACEHOLDER_S), but the budget always counts their planned length.
"""
import ast, glob, json, math, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import segtime as ST                       # noqa: E402  (A1 table + A2 seams)
REPO = os.path.dirname(HERE)
R = "E:/YTP2/3D Timelapse/renders"
MASTER = R + "/master"
BRIDGES = MASTER + "/bridges"
PLACEHOLDER_S = 2.0          # preview card length for a segment that is not rendered yet
BUDGET_S = ST.TOTAL          # 421.9 s = 7:02, the owner's chosen cut (A1 tight); the old 4:30 budget (HANDOFF 17:01) is superseded
EXACT_SEAMS = True           # A2 seams match exactly: segments are concatenated directly, connectors are skipped

# ======================================================================= small vector helpers (no numpy needed)
def add(a, b): return [x + y for x, y in zip(a, b)]
def sub(a, b): return [x - y for x, y in zip(a, b)]
def mul(a, k): return [x * k for x in a]
def dot(a, b): return sum(x * y for x, y in zip(a, b))
def norm(a): return math.sqrt(dot(a, a))
def unit(a):
    n = norm(a); return [x / n for x in a] if n > 1e-12 else [0.0, 1.0, 0.0]

def herm(p0, m0, p1, m1, T, t):
    """Cubic Hermite in time: p(0) = p0, p'(0) = m0, p(T) = p1, p'(T) = m1 (vectors or floats)."""
    s = min(1.0, max(0.0, t / T))
    h00, h10, h01, h11 = 2 * s ** 3 - 3 * s ** 2 + 1, s ** 3 - 2 * s ** 2 + s, -2 * s ** 3 + 3 * s ** 2, s ** 3 - s ** 2
    if isinstance(p0, (int, float)):
        return h00 * p0 + h10 * T * m0 + h01 * p1 + h11 * T * m1
    return [h00 * a + h10 * T * b + h01 * c + h11 * T * d for a, b, c, d in zip(p0, m0, p1, m1)]

# ======================================================================= camera keys from hudcam dumps
def load_dump(cams_dir, idx):
    p = os.path.join(cams_dir, "_cam", f"{int(idx):05d}.json")
    if not os.path.exists(p):
        return None
    j = json.load(open(p))
    m = j["matrix_world"]
    return dict(t=j.get("t"), loc=[m[0][3], m[1][3], m[2][3]], dir=unit([-m[0][2], -m[1][2], -m[2][2]]), lens=j["lens"])

def key_from_dumps(cams_dir, idx, fps):
    """Camera key at frame idx: loc, look dir, lens and their rates (central differences, one-sided at the ends)."""
    c = load_dump(cams_dir, idx)
    if c is None:
        return None
    a, b = load_dump(cams_dir, idx - 1), load_dump(cams_dir, idx + 1)
    a_, b_, dt = (a or c), (b or c), ((1 if a else 0) + (1 if b else 0)) / fps
    if dt <= 0:
        dt = 1.0
    c["vel"] = mul(sub(b_["loc"], a_["loc"]), 1 / dt)
    c["ddir"] = mul(sub(b_["dir"], a_["dir"]), 1 / dt)
    c["dlnlens"] = (math.log(b_["lens"]) - math.log(a_["lens"])) / dt
    c["src"] = f"hudcam dump {cams_dir}/_cam/{int(idx):05d}.json"
    return c

def key_cached(name):
    """Key evaluated inside Blender by render_bridge.py (exact cam function of that world) - preferred when present."""
    p = os.path.join(BRIDGES, "keys", name + ".json")
    if os.path.exists(p):
        k = json.load(open(p)); k["src"] = "render_bridge eval " + p
        return k
    return None

def key_static(loc, look, lens, vel=(0, 0, 0), note=""):
    d = unit(sub(look, loc))
    return dict(loc=list(loc), dir=d, look_at=list(look), lens=lens, vel=list(vel), ddir=[0, 0, 0], dlnlens=0.0,
                src="documented constant " + note)

# ======================================================================= Trost video time <-> action time (render_trost.py)
def _trost_tables():
    """Reads _SP / SET_K / V_KICK from render_trost.py with ast (no bpy) and rebuilds its Tmap knots."""
    src = open(os.path.join(HERE, "render_trost.py"), encoding="utf8").read()
    tree = ast.parse(src)
    sp, setk, vk = None, float(os.environ.get("RT_SET_K", "1.25")), 14.0
    for n in tree.body:
        if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name) and n.targets[0].id == "_SP":
            sp = ast.literal_eval(n.value)
        if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Tuple):
            names = [e.id for e in n.targets[0].elts if isinstance(e, ast.Name)]
            if names == ["V_LIGHT", "V_KICK"]:
                vk = ast.literal_eval(n.value)[1]
    KV, KT = [vk], [0.0]
    for a, b, dv, s in sp:
        KV.append(KV[-1] + dv * (setk if s else 1.0)); KT.append(float(b))
    return KV, KT

def _pchip_m(T, S):
    D = [(S[i + 1] - S[i]) / (T[i + 1] - T[i]) for i in range(len(T) - 1)]
    return [D[0]] + [0.0 if D[i - 1] * D[i] <= 0 else 2 * D[i - 1] * D[i] / (D[i - 1] + D[i]) for i in range(1, len(D))] + [D[-1]]

def _pchip(T, S, m, t):
    t = min(max(t, T[0]), T[-1]); i = 0
    while i < len(T) - 2 and T[i + 1] <= t:
        i += 1
    h = T[i + 1] - T[i]; s = (t - T[i]) / h
    return (2 * s ** 3 - 3 * s ** 2 + 1) * S[i] + (s ** 3 - 2 * s ** 2 + s) * h * m[i] + (-2 * s ** 3 + 3 * s ** 2) * S[i + 1] + (s ** 3 - s ** 2) * h * m[i + 1]

_TT = {}
def trost_vend():
    if not _TT:
        KV, KT = _trost_tables(); _TT.update(KV=KV, KT=KT, KM=_pchip_m(KV, KT))
    return _TT["KV"][-1]

def trost_v(T):
    """Action time T (trost_action.BEATS) -> Trost video seconds v (inverse of render_trost.Tmap)."""
    trost_vend(); lo, hi = _TT["KV"][0], _TT["KV"][-1]
    for _ in range(60):
        mid = (lo + hi) / 2
        if _pchip(_TT["KV"], _TT["KT"], _TT["KM"], mid) < T: lo = mid
        else: hi = mid
    return (lo + hi) / 2

def trost_beats():
    tree = ast.parse(open(os.path.join(HERE, "trost_action.py"), encoding="utf8").read())
    for n in tree.body:
        if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name) and n.targets[0].id == "BEATS":
            return ast.literal_eval(n.value)
    return {}

def _const(path, name, default):
    try:
        tree = ast.parse(open(os.path.join(HERE, path), encoding="utf8").read())
        for n in tree.body:
            if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name) and n.targets[0].id == name:
                return ast.literal_eval(n.value)
    except Exception:
        pass
    return default

# ======================================================================= the segments, canon order
REPO_SH = "cd 'E:/YTP2/3D Timelapse/repo/timelapse3d' && "
WORLD_K = float(os.environ.get("WORLD_K", "0.05"))
TROST_DY = (480000.0 - 380000.0) * WORLD_K          # = world.SET_ORIGIN["trost"][1]
def frame_of(world):
    return "shig" if world in ("shig", "base_shig") else "trost"
def w2f(p, frame):
    return [p[0], p[1] - (TROST_DY if frame == "trost" else 0.0)] + list(p[2:])

def _seam(loc, heading_deg, pitch_deg, speed, vz=0.0, lens=30.0, note=""):
    h = math.radians(heading_deg); pch = math.radians(pitch_deg)
    d = [math.cos(h) * math.cos(pch), math.sin(h) * math.cos(pch), math.sin(pch)]
    t = -loc[2] / d[2] if d[2] < 0 else 300.0
    return dict(loc=list(loc), look=[loc[0] + d[0] * t, loc[1] + d[1] * t, 0.0], lens=lens,
                vel=[math.cos(h) * speed, math.sin(h) * speed, vz], ddir=[0, 0, 0], dlnlens=0.0, note=note)

TRAINING_CAMP_TROST = (-1450.0, 650.0)   # 104th camp centre in the old Trost set frame (= M (-1450, 1520)); render_interlude.py legacy

def _from_seg(k, name):
    """segtime seam -> master_timeline key dict (loc / look / lens / vel / ddir / dlnlens + frame 'W' or 'M')."""
    return dict(loc=list(k["pos"]), look=list(k["look"]), lens=k["lens"], vel=list(k["vel"]), ddir=[0, 0, 0], dlnlens=0.0,
                frame=k["frame"], t=k["t"], note=name + ": " + k["note"])
SEAMS = {n: _from_seg(ST.seam(n), n) for n in ST.SEAMS}        # A2, exact; coordinates in the seam's own frame (W or M)

# legacy S0-S8 (pre-bible-v2 connector seams, world coordinates, Trost frame y - TROST_DY); kept only so old scripts still import
LEGACY_SEAMS = {
    "S3": _seam([250, 1700, 900], 90, -55, 350, note="legacy C1 -> camps world-only frame"),
    "S5": _seam([1900, 0 + TROST_DY, 650], 210, -60, 300, vz=-40, note="legacy C2a -> C2b world-only frame"),
    "S7": _seam([-3000, 950 + TROST_DY, 900], -11.5, -68, 306, vz=-40, note="legacy C3 -> training world-only frame"),
    "S8": _seam([-1013, 322 + TROST_DY, 300], -37, -70, 196, vz=-15, note="legacy training end -> Trost v=0"),
}

def seg_frames(g): return [R + f"/{g}/frames/{g}_%05d.png"]
def seg_cmd(g): return REPO_SH + f"SEG={g} FPS=15 bash render_seg.sh" if g not in ("g1", "g2", "g3") else REPO_SH + {
    "g1": "FPS=15 OUT='E:/YTP2/3D Timelapse/renders/g1' bash render_fast.sh",
    "g2": "SEG=3 FPS=15 bash render_fall2.sh",
    "g3": "bash render_interlude.sh   # + AOT_PLUGINS=world bash render_march846.sh for the march846 run (t 31.3-49.3)"}[g]
OWNER = dict(g1="lead/A", g2="A", g3="B/F", g4="C", g5="C", g6="C", g7="C", g8="C")

SEGMENTS = [
    dict(id=g, label=f"{g} {ST.CONTENT[g]}", owner=OWNER[g], world="shig" if g in ("g1", "g2") else "trost",
         frames=seg_frames(g), cams=None, src_in=0.0, src_out=None, planned=ST.DUR[g], seam_in=(ST.seam_in(g) or {}).get("name"),
         seam_out=ST.seam_out(g)["name"], t_start=ST.START[g], cmd=seg_cmd(g))
    for g in ST.ORDER]
SEG = {s["id"]: s for s in SEGMENTS}
SEG["g3"]["parts"] = dict(march846=dict(t=ST.G3["march"], mp4=R + "/march846/march846_preview.mp4", frames=R + "/march846/frames/march_%05d.png",
                                          cams=R + "/march846/frames", cmd=REPO_SH + "AOT_PLUGINS=world bash render_march846.sh"))

# ======================================================================= frame lookup
# Fallback while an agent re-renders a segment (its frame folder is wiped at the start of a render): the segment's
# latest preview mp4, extracted by assemble_master.py into renders/master/cache/<name>/%05d.png (index = frame index).
FALLBACK_MP4 = {g: [R + f"/{g}/{g}_preview.mp4"] for g in ST.ORDER}
FALLBACK_START = {}
def cache_dir(mp4):
    return MASTER + "/cache/" + os.path.splitext(os.path.basename(os.path.dirname(mp4)))[0] + "__" + os.path.basename(mp4)[:-4]

def frame_path(seg, idx):
    for pat in seg["frames"] + [cache_dir(m) + "/%05d.png" for m in FALLBACK_MP4.get(seg["id"], [])]:
        p = pat % idx
        if os.path.exists(p):
            return p
    return None

def seg_window(seg, fps):
    """(i_in, i_out_planned, i_out_available): frame indices at the segment's source fps (15 for previews)."""
    i_in = int(round(seg["src_in"] * fps))
    if seg["src_out"] is None:
        out_planned = i_in + int(round(seg["planned"] * fps)) - 1
    else:
        out_planned = int(round(seg["src_out"] * fps))
    i = i_in
    while i <= out_planned and frame_path(seg, i):
        i += 1
    return i_in, out_planned, i - 1

# ======================================================================= segment keys (first / last)
def seg_key(seg_id, t, fps=15):
    """Camera key of segment seg_id at its own time t: in-Blender cache, else hudcam dumps, else documented constants."""
    s = SEG.get(seg_id)
    k = key_cached(f"{(s or {}).get('seg_time') or seg_id}_{t:.3f}")
    if k:
        return k
    cams = s.get("cams") if s else None
    if cams:
        k = key_from_dumps(cams, int(round(t * fps)), fps)
        if k:
            return k
    # A2 seams: the first key of a segment is its entering seam, the last key its leaving seam (exact, velocity included)
    if s and s.get("t_start") is not None:
        if t <= 0.01 and s.get("seam_in"):
            return seam_key(s["seam_in"], SEAMS[s["seam_in"]]["frame"])
        if t >= s["planned"] - 0.5 / fps and s.get("seam_out"):
            return seam_key(s["seam_out"], SEAMS[s["seam_out"]]["frame"])
    return None

# ======================================================================= connectors: path evaluation (shared with Blender)
D_LOOK = 300.0       # look point distance used to blend the look direction with a matched rate

def seam_key(name, frame="M"):
    """Seam key as a camera-key dict in `frame`: "W" | "M" | "set" (trost.py set), or legacy "shig" (= W) / "trost" (legacy S0-S8)."""
    if name in LEGACY_SEAMS:
        k = dict(LEGACY_SEAMS[name]); k["loc"] = w2f(k["loc"], frame); k["look"] = w2f(k["look"], frame)
    else:
        k = dict(SEAMS[name]); k["loc"], k["look"] = list(k["loc"]), list(k["look"])
        if k["frame"] != frame and frame in ("W", "M", "set"):
            cv = {("W", "M"): ST.W_to_M, ("M", "W"): ST.M_to_W, ("M", "set"): ST.M_to_set,
                  ("W", "set"): ST.W_to_set}[(k["frame"], frame)]
            k["loc"], k["look"] = list(cv(*k["loc"])), list(cv(*k["look"])); k["frame"] = frame
    k["dir"] = unit(sub(k["look"], k["loc"])); k["look_at"] = k["look"]; k["src"] = "seam " + name
    return k

def span_start(br, half):
    t = 0.0
    for h in sorted(br["halves"]):
        if h == half:
            return t
        t += br["halves"][h]["T"]
    return t

def bridge_total(br):
    return sum(h["T"] for h in br["halves"].values())

def bridge_eval(br, half, k0, k1, tb):
    """Camera (loc, dir, lens) at connector time tb inside span `half`, between its keys k0 -> k1 (in that span's frame).
    Position, look point (loc + D_LOOK * dir) and log-lens are Hermites with the keys' rates: C1 at both ends."""
    T = br["halves"][half]["T"]; t = tb - span_start(br, half)
    loc = herm(k0["loc"], k0["vel"], k1["loc"], k1["vel"], T, t)
    l0 = add(k0["loc"], mul(k0["dir"], D_LOOK)); l1 = add(k1["loc"], mul(k1["dir"], D_LOOK))
    m0 = add(k0["vel"], mul(k0.get("ddir", [0, 0, 0]), D_LOOK)); m1 = add(k1["vel"], mul(k1.get("ddir", [0, 0, 0]), D_LOOK))
    look = herm(l0, m0, l1, m1, T, t)
    lens = math.exp(herm(math.log(k0["lens"]), k0.get("dlnlens", 0.0), math.log(k1["lens"]), k1.get("dlnlens", 0.0), T, t))
    return loc, unit(sub(look, loc)), lens

def bridge_frames(br, fps):
    """[(j, tb, half)]: connector frames j = 1 .. N-1 (tb = 0 and the end belong to the segments).  A frame exactly on a
    mid-connector seam belongs to the later span (both scenes render the same world-only image there)."""
    n = int(round(bridge_total(br) * fps)); out = []
    for j in range(1, n):
        tb = j / fps; half = sorted(br["halves"])[0]
        for h in sorted(br["halves"]):
            if tb >= span_start(br, h) - 1e-9:
                half = h
        out.append((j, tb, half))
    return out

def bridge_dir(br):
    return f"{BRIDGES}/{br['id']}"

def state_key(state):
    """Segment key for ("interlude" | "march" | "trost" | "fall3", segment time): Blender cache, dumps, constants."""
    k = key_cached(f"{state[0]}_{state[1]:.3f}")
    if k:
        return k
    return seg_key(state[0], state[1])

def half_keys(br, half):
    fr = frame_of(br["halves"][half]["world"])
    def res(k):
        return seam_key(k["seam"], fr) if "seam" in k else state_key(k["state"])
    hd = br["halves"][half]
    return res(hd["k0"]), res(hd["k1"])

def bridge_check(br, fps=60):
    out = dict(id=br["id"], spans=[])
    for half in sorted(br["halves"]):
        k0, k1 = half_keys(br, half)
        if not k0 or not k1:
            out["spans"].append(dict(half=half, missing=True)); continue
        sp, zs, prev = [], [], None
        t0 = span_start(br, half); T = br["halves"][half]["T"]
        for j in range(int(round(T * fps)) + 1):
            loc, d, lens = bridge_eval(br, half, k0, k1, t0 + j / fps)
            if prev is not None:
                sp.append(norm(sub(loc, prev)) * fps)
            prev = loc; zs.append(loc[2])
        out["spans"].append(dict(half=half, world=br["halves"][half]["world"], T=T, v0=norm(k0["vel"]),
                                 v1=norm(k1["vel"]), v_max=max(sp), z_min=min(zs), z_max=max(zs)))
    return out

# ======================================================================= master build
def build(fps=15):
    """Resolved master timeline: [{id, kind, m_in, m_out, n, ...}] in master seconds (preview cards shortened)."""
    rows, m = [], 0.0
    for s in SEGMENTS:
        if s.get("bridge") and EXACT_SEAMS and not s.get("force"):
            continue                                   # exact seams: segments are concatenated directly
        if s.get("bridge"):
            frs = bridge_frames(s, fps)
            have = sum(1 for j, _, _ in frs if os.path.exists(f"{bridge_dir(s)}/br_{j:05d}.png"))
            planned = bridge_total(s) - 1 / fps
            r = dict(id=s["id"], kind="connector", label=s["label"], n=len(frs), have=have, planned=planned,
                     dur=len(frs) / fps, spans={h: (v["world"], v["T"]) for h, v in s["halves"].items()},
                     status="rendered" if have == len(frs) else ("partial %d/%d" % (have, len(frs)) if have else "not rendered"))
        else:
            i_in, i_out_p, i_out_a = seg_window(s, fps)
            planned = (i_out_p - i_in + 1) / fps
            avail = max(0, i_out_a - i_in + 1)
            r = dict(id=s["id"], kind="segment", label=s["label"], owner=s["owner"], i_in=i_in, i_out=i_out_p,
                     i_avail=i_out_a, n=avail, planned=planned, dur=avail / fps, cmd=s["cmd"],
                     status="complete" if i_out_a >= i_out_p else ("partial to i=%d" % i_out_a if avail else "missing"))
        r["m_in"] = m
        m += r["dur"]
        missing = r["planned"] - r["dur"]
        if missing > 0.5 / fps:
            r["card"] = PLACEHOLDER_S
            m += PLACEHOLDER_S
        r["m_out"] = m
        rows.append(r)
    return rows

def keys_table(fps=15):
    out = {}
    for s in SEGMENTS:
        if s.get("bridge"):
            continue
        sid = s["id"]
        out[sid] = dict(first=seg_key(sid, s["src_in"], fps), last=seg_key(sid, s["planned"], fps))
    return out

def _fmt_key(k):
    if not k:
        return "n/a (no dumps / not rendered)"
    f = lambda v, n=0: "(" + ", ".join(f"{x:.{n}f}" for x in v) + ")"
    look = k.get("look_at") or add(k["loc"], mul(k["dir"], 300))
    return f"loc {f(k['loc'])} look {f(look)} lens {k['lens']:.0f} vel {f(k['vel'])} |v| {norm(k['vel']):.0f}"

def fmt_t(x):
    return f"{int(x // 60)}:{x % 60:05.2f}"

def report(fps=15, write=True):
    rows = build(fps)
    keys = keys_table(fps)
    print(f"MASTER TIMELINE  ({fps} fps preview; cards {PLACEHOLDER_S}s for missing material)")
    print(f"{'id':9s} {'master in':>9s} {'out':>9s} {'have s':>7s} {'plan s':>7s}  status / label")
    planned_total = 0.0
    for r in rows:
        planned_total += r["planned"]
        print(f"{r['id']:9s} {fmt_t(r['m_in']):>9s} {fmt_t(r['m_out']):>9s} {r['dur']:7.2f} {r['planned']:7.2f}  {r['status']:16s} {r['label']}")
    print(f"preview length {fmt_t(rows[-1]['m_out'])}; PLANNED length {fmt_t(planned_total)} (A1 tight total {fmt_t(BUDGET_S)})")
    print("\nKEYS (first / last of each segment)")
    for sid, k in keys.items():
        print(f"  {sid:9s} first {_fmt_key(k['first'])}\n  {'':9s} last  {_fmt_key(k['last'])}")
    print("\nSEAMS (A2, exact; frame W = Shiganshina, M = Trost master = W - (0, 4130))")
    for nm, k in SEAMS.items():
        print(f"  {nm:9s} [{k['frame']}] @{fmt_t(k['t'])} loc {tuple(round(c, 1) for c in k['loc'])} look {tuple(round(c, 1) for c in k['look'])} "
              f"lens {k['lens']:.0f} vel {tuple(round(c, 1) for c in k['vel'])} |v| {norm(k['vel']):.0f}")
    print("\nCONNECTORS" + ("  (none: seams are exact, segments are concatenated directly)" if EXACT_SEAMS else ""))
    checks = []
    for s in SEGMENTS:
        if s.get("bridge"):
            c = bridge_check(s); checks.append(c)
            for sp in c["spans"]:
                if sp.get("missing"):
                    print(f"  {s['id']}{sp['half']}: keys need the Blender evaluation  ({s['label']})")
                else:
                    print(f"  {s['id']}{sp['half']} [{sp['world']}] {sp['T']:.1f}s |v| {sp['v0']:.0f} -> {sp['v1']:.0f} m/s, "
                          f"max {sp['v_max']:.0f}, z {sp['z_min']:.0f}..{sp['z_max']:.0f} m  ({s['label']})")
    if write:
        os.makedirs(MASTER, exist_ok=True)
        json.dump(dict(fps=fps, rows=rows, keys=keys, planned_total=planned_total,
                       connectors=checks, seams=SEAMS),
                  open(MASTER + "/master_timeline.json", "w"), indent=1, default=str)
    return rows, planned_total

if __name__ == "__main__":
    fps = 15
    if "--fps" in sys.argv:
        fps = int(sys.argv[sys.argv.index("--fps") + 1])
    report(fps)
