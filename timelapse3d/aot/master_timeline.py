"""EP1 MASTER TIMELINE (agent G, integrator): one continuous camera take from the title to the end of Trost.

Pure Python (no bpy): importable by render_bridge.py inside Blender and by assemble_master.py / the shell outside it.

    python aot/master_timeline.py              print the master table (video in/out, source window, keys, status),
                                               the bridge check (speeds, seams) and the pace budget; writes
                                               renders/master/master_timeline.json
    python aot/master_timeline.py --fps 30     the same at the final frame rate

Model
-----
SEGMENTS is the canon order.  Each entry is either
  * a rendered SEGMENT owned by another agent: frames on disk, a source window [src_in, src_out] in the segment's own
    seconds (both ends inclusive: the frame at src_out is the bridge's start key, the frame at src_in the previous
    bridge's end key), its render command and its camera keys; or
  * a CONNECTOR (agent G, aot/render_bridge.py): a flight between two segments, rendered in one or two spans.
    STRICT ONE TAKE (HANDOFF 10/25 09:37): no clouds, wipes or dissolves.  Every seam is a matched camera: identical
    position, direction, lens and velocity on both sides.  A span is a cubic Hermite in time between two keys (a
    segment key evaluated inside Blender with that segment's own camera function, or an explicit SEAM key in world
    coordinates).  Where the flight changes Blender scene, the seam is a WORLD-ONLY frame (moderate sky height,
    looking down ~55 deg) where only aot/world.py content, identical in every scene, is in frame.
World coordinates (aot/world.py, factor WORLD_K = 0.05): the Shiganshina / scene.py frame; the Trost frame is offset
by TROST_DY = 5000 m (p_world = p_trost + (0, TROST_DY)).
Video seconds = 30 fps final; previews run at 15 fps (frame index = round(t * fps)).  Bridge durations are multiples
of 0.2 s so the keys land on frames at both 15 and 30 fps.
Missing segments become short dark placeholder cards in the preview (PLACEHOLDER_S), but the budget always counts
their planned length.
"""
import ast, glob, json, math, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
R = "E:/YTP2/3D Timelapse/renders"
MASTER = R + "/master"
BRIDGES = MASTER + "/bridges"
PLACEHOLDER_S = 2.0          # preview card length for a segment that is not rendered yet
BUDGET_S = 270.0             # title -> end of Trost (HANDOFF 17:01: ~4:30 of the 8-10 min EP)

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

# SEAM KEYS in WORLD coordinates (Trost frame: y - TROST_DY).  Headings: 90 = north, 0 = east.
SEAMS = {
    "S0": dict(note="opening -> fall: same scene, render_fast keys()[-1] = render_fall first key (lead / A)"),
    "S1": dict(loc=[8, -534, 94], look=[-34, -648, 0], lens=32.0, vel=[0, 0, 0], ddir=[0, 0, 0], dlnlens=0.0,
               note="fall (seg 2) end = fall3 start, at rest (agent A, same scene)"),
    "S2": dict(loc=[180, 165, 215], look=[232, 340, 0], lens=28.0, vel=[4, 42, 10], ddir=[0, 0, 0], dlnlens=0.0,
               note="fall3 end (A, s 12.0, sunset; SEG3_END_LIGHT) = C1 start, same scene; exact key evaluated in Blender"),
    "S3": _seam([250, 1700, 900], 90, -55, 350, note="C1 (scene.py+world) -> camps (interlude+world): WORLD-ONLY frame, 900 m up "
                                                  "over Maria territory, river (east) and road (west) as leading lines north; day light"),
    "S5": _seam([1900, 0 + TROST_DY, 650], 210, -60, 300, vz=-40,
                note="C2a (interlude) -> C2b (march scene): over Wall Rose 1.9 km east of Trost, looking SW; world-only frame"),
    "S7": _seam([-3000, 950 + TROST_DY, 900], -11.5, -68, 306, vz=-40,
                note="C3 (march scene) -> training (interlude): inside Rose, west of the training camp, world-only frame"),
    "S8": _seam([-1013, 322 + TROST_DY, 300], -37, -70, 196, vz=-15,
                note="training end (interlude, graduation night) -> Trost v=0 (render_trost, night -> dawn): steep look SE "
                     "into the 400 m world-only gap between the camp core (behind) and Trost's core (just above the frame)"),
}
TRAINING_CAMP_TROST = (-1450.0, 650.0)   # agent B's new CAMP centre (Trost frame): beside Trost, inside Rose

INT_FRAMES = R + "/interlude/raw/int_%05d.png"
SEGMENTS = [
    dict(id="opening", label="1 Opening: tree -> Colossal -> kick (LOCKED; re-render with ,world = no mountains)",
         owner="lead/A", world="shig", frames=[R + "/opening_v4/fast_%05d.png"], cams=None, src_in=0.0,
         src_out=13.0 - 1 / 15, planned=13.0, seam_out="S0",
         cmd=REPO_SH + "FPS=15 OUT='E:/YTP2/3D Timelapse/renders/opening_v4' bash render_fast.sh"),
    dict(id="fall", label="2 The fall: houses, swarm, Carla eaten (small, aerial)", owner="A", world="shig",
         frames=[R + "/fall_frames/fall_%05d.png"], cams=None, src_in=0.0, src_out=None, planned=10.6, seam_out="S1",
         cmd=REPO_SH + "FPS=15 bash render_fall.sh"),
    dict(id="fall3", label="3 Armored rams the inner gate; aerial of ferries/refugees going north", owner="A",
         world="shig", frames=[R + "/fall_frames3/fall3_%05d.png"], cams=None, src_in=0.0, src_out=None, planned=12.0,
         seam_out="S2", cmd=REPO_SH + "SEG=3 FPS=15 bash render_fall2.sh"),
    dict(id="C1", bridge=True, label="C1 long flight north across Wall Maria territory (sunset -> night -> day)",
         halves=dict(a=dict(world="shig", T=7.0, k0=dict(state=("fall3", 12.0)), k1=dict(seam="S3"),
                            state=("fall3", 12.0)))),
    dict(id="camps", label="6 Over Trost to the refugee camps; fields cleared, food runs short (846)", owner="B",
         world="interlude", frames=[INT_FRAMES], cams=R + "/interlude/raw", src_in=0.0, src_out=5.2, planned=5.2,
         seam_in="S3 (B re-keys its start)", cmd=REPO_SH + "bash render_interlude.sh", seg_time="interlude"),
    dict(id="C2", bridge=True, label="C2 camps -> over Wall Rose east of Trost -> down to Trost's outer gate",
         halves=dict(a=dict(world="interlude", T=4.6, k0=dict(state=("interlude", 5.2)), k1=dict(seam="S5"),
                            state=("interlude", 5.2)),
                     b=dict(world="march", T=3.6, k0=dict(seam="S5"), k1=dict(state=("march", 0.0)),
                            state=("march", 0.0)))),
    dict(id="march", label="7 The 250,000 march (THE key scene)", owner="F", world="march",
         frames=[R + "/march846/frames/march_%05d.png"], cams=R + "/march846/frames", src_in=0.0, src_out=18.0,
         planned=18.0, cmd=REPO_SH + "AOT_PLUGINS=world bash render_march846.sh"),
    dict(id="C3", bridge=True, label="C3 high over the emptied plain -> north over Wall Rose -> beside the training camp",
         halves=dict(a=dict(world="march", T=7.0, k0=dict(state=("march", 18.0)), k1=dict(seam="S7"),
                            state=("march", 18.0)))),
    dict(id="training", label="8 Training camp beside Trost 847-850, graduation night", owner="B", world="interlude",
         frames=[INT_FRAMES], cams=R + "/interlude/raw", src_in=7.0, src_out=307 / 15, planned=307 / 15 - 7.0,
         seam_in="S7 (B re-keys)", seam_out="S8 (B re-keys)", cmd=REPO_SH + "bash render_interlude.sh",
         seg_time="interlude"),
    dict(id="trost", label="9 Trost 850 (from S8 at night; dawn over Trost)", owner="C/D", world="trost",
         frames=[R + "/trost/frames_p1/rt_%05d.png", R + "/trost/frames_p2/rt_%05d.png", R + "/trost/frames_p3/rt_%05d.png"],
         cams=None, src_in=0.0, src_out=None, planned=None, seam_in="S8 (C re-keys v=0)",
         cmd=REPO_SH + "PART=1 bash render_trost.sh; PART=2 bash render_trost.sh; PART=3 bash render_trost.sh"),
]
SEG = {s["id"]: s for s in SEGMENTS}

# ======================================================================= frame lookup
# Fallback while an agent re-renders a segment (its frame folder is wiped at the start of a render): the segment's
# latest preview mp4, extracted by assemble_master.py into renders/master/cache/<name>/%05d.png (index = frame index).
FALLBACK_MP4 = {
    "opening": [R + "/opening_preview_v4.mp4"],
    "fall": [R + "/fall_preview.mp4", R + "/fall/fall_preview.mp4"],
    "fall3": [R + "/fall/fall3_preview.mp4"], "fall4": [R + "/fall/fall4_preview.mp4"], "fall5": [R + "/fall/fall5_preview.mp4"],
    "camps": [R + "/interlude/interlude_preview_nohud.mp4"], "training": [R + "/interlude/interlude_preview_nohud.mp4"],
    "march": [R + "/march846/march846_preview.mp4"],
    "trost": [R + "/trost/trost_part1.mp4", R + "/trost/trost_part2.mp4", R + "/trost/trost_part3.mp4"],
}
FALLBACK_START = {"trost_part2.mp4": 52 * 15, "trost_part3.mp4": 98 * 15}   # render_trost.sh PART windows (v0 * fps)
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
    if seg["id"] == "trost":
        out_planned = int(math.floor(trost_vend() * fps)) - 1
    elif seg["src_out"] is None:
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
    # documented constants (scene.py: PLAZA (-20, -360), OUTER_GATE (0, -720); render_fast keys()[-1])
    if seg_id == "opening" and t >= 12.9:
        return key_static((35, -310, 150), (0, -600, 0), 38, note="render_fast.keys()[-1] (moving; rate unknown)")
    if seg_id == "fall" and t <= 0.01:
        return key_static((35, -310, 150), (0, -600, 0), 38, note="render_fall.a_keys()[0] = render_fast last key")
    if seg_id == "trost" and t <= 0.01:
        return key_static((-250, -420, 170), (-40, -790, 25), 28, note="render_trost.cam_keys()[0] (from rest)")
    if seg_id == "march":
        if t <= 0.01:
            return key_static((170, -700, 125), (-10, -930, 0), 27, (16.7, -61.1, 5.6), "march846.CAM_IN")
        return key_static((260, -1920, 640), (0, -720, 40), 28, (0, 95, 22), "march846.CAM_OUT")
    return None

# ======================================================================= connectors: path evaluation (shared with Blender)
D_LOOK = 300.0       # look point distance used to blend the look direction with a matched rate

def seam_key(name, frame):
    """Explicit seam key, converted to the given set frame ("shig" | "trost")."""
    k = dict(SEAMS[name]); k["loc"] = w2f(k["loc"], frame); k["look"] = w2f(k["look"], frame)
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
    if state[0] == "fall3" and abs(state[1] - 12.0) < 1e-6:
        return seam_key("S2", "shig")
    return seg_key("camps" if state[0] == "interlude" else state[0], state[1])

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
        i_in, i_out, _ = seg_window(s, fps)
        sid = s["id"]; st = s.get("seg_time")
        first = seg_key(sid, s["src_in"], fps) if not st else (key_cached(f"interlude_{s['src_in']:.3f}") or key_from_dumps(s["cams"], i_in, fps))
        t_out = i_out / fps
        last = seg_key(sid, t_out, fps) if not st else (key_cached(f"interlude_{t_out:.3f}") or key_from_dumps(s["cams"], i_out, fps))
        out[sid] = dict(first=first, last=last)
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
    print(f"preview length {fmt_t(rows[-1]['m_out'])}; PLANNED length {fmt_t(planned_total)} (budget {fmt_t(BUDGET_S)})")
    print("\nKEYS (first / last of each segment)")
    for sid, k in keys.items():
        print(f"  {sid:9s} first {_fmt_key(k['first'])}\n  {'':9s} last  {_fmt_key(k['last'])}")
    print("\nSEAMS (world coordinates; Trost frame y - %.0f)" % TROST_DY)
    for nm, k in SEAMS.items():
        if "loc" in k:
            print(f"  {nm}: loc {tuple(round(c) for c in k['loc'])} look {tuple(round(c) for c in k['look'])} lens {k['lens']:.0f} "
                  f"vel {tuple(round(c) for c in k['vel'])} |v| {norm(k['vel']):.0f}  - {k['note']}")
        else:
            print(f"  {nm}: {k['note']}")
    print("\nCONNECTORS")
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
