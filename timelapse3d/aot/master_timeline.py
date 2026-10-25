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
  * a BRIDGE (agent G, aot/render_bridge.py): a physical flight between two segments that do not share a scene.
    climb half (rendered in the outgoing segment's world) -> APEX inside a cloud bank -> descend half (rendered in
    the incoming segment's world).  Both halves are cubic Hermite curves in time with matched position, velocity,
    look direction (+ its rate) and log-lens (+ its rate) at the segment keys, and a shared apex position/velocity, so
    the camera is C1 through both seams.  The world swap happens at the apex under a 2D cloud whiteout
    (assemble_master.py) - no hard cut, no visible dissolve.
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
INT_FRAMES = R + "/interlude/raw/int_%05d.png"
SEGMENTS = [
    dict(id="opening", label="1 Opening: tree -> Colossal -> kick (LOCKED)", owner="lead/opening", world="shiganshina",
         frames=[R + "/opening_v4/fast_%05d.png"], cams=None, src_in=0.0, src_out=13.0 - 1 / 15, planned=13.0,
         cmd=REPO_SH + "FPS=15 OUT='E:/YTP2/3D Timelapse/renders/opening_v4' bash render_fast.sh",
         note="render_fast.py writes no hudcam dumps; renders/graphics/opening_v3_cam (v3 camera) is used for tags"),
    dict(id="fall", label="2 The fall: houses, swarm, Carla", owner="A", world="shiganshina",
         frames=[R + "/fall_frames/fall_%05d.png"], cams=None, src_in=0.0, src_out=13.2 - 1 / 15, planned=13.2,
         cmd=REPO_SH + "FPS=15 bash render_fall.sh", note="continues render_fast's last key (fall a_keys()[0])"),
    dict(id="fall3", label="3 Armored Titan, ferries, the vow", owner="A", world="shiganshina",
         frames=[R + "/fall_frames3/fall3_%05d.png"], cams=None, src_in=0.0, src_out=None, planned=12.0,
         cmd=REPO_SH + "SEG=3 FPS=15 bash render_fall2.sh"),
    dict(id="fall4", label="4 Night pull-up, burning Shiganshina, grey belt", owner="A", world="shiganshina",
         frames=[R + "/fall_frames45/seg4/fall4_%05d.png"], cams=None, src_in=0.0, src_out=None, planned=12.0,
         cmd=REPO_SH + "SEG=45 FPS=15 bash render_fall2.sh"),
    dict(id="fall5", label="5 Grisha in the forest (glitch at s 4.7)", owner="A", world="shiganshina",
         frames=[R + "/fall_frames45/seg5/fall5_%05d.png"], cams=None, src_in=0.0, src_out=None, planned=5.0,
         cmd=REPO_SH + "SEG=45 FPS=15 bash render_fall2.sh"),
    dict(id="B1", bridge=True, label="Bridge 1: Grisha's forest (night) -> clouds -> plains south of Trost (846 day)",
         a="fall5", b="camps", Ta=2.6, Tb=2.6,
         halves=dict(a=dict(world="shig", state=("fall5", 5.0), apex=dict(rel=[0.0, 520.0, 880.0])),
                     b=dict(world="interlude", state=("interlude", 0.4), apex=dict(rel=[60.0, -1320.0, 830.0]))),
         apex_vel=[0.0, 560.0, 0.0], apex_lens=28.0),
    dict(id="camps", label="6 Refugee camps 846 (interlude 0.4-5.2)", owner="B", world="interlude",
         frames=[INT_FRAMES], cams=R + "/interlude/raw", src_in=0.4, src_out=5.2, planned=4.8,
         cmd=REPO_SH + "bash render_interlude.sh", seg_time="interlude"),
    dict(id="B2", bridge=True, label="Bridge 2: camps -> climb, turn over Wall Rose -> down to Trost's outer gate",
         a="camps", b="march", Ta=2.4, Tb=2.6,
         halves=dict(a=dict(world="interlude", state=("interlude", 5.2)), b=dict(world="march", state=("march", 0.0))),
         apex=[-260.0, -60.0, 820.0], apex_vel=[160.0, -330.0, 0.0], apex_lens=28.0),
    dict(id="march", label="7 The 250,000 march (THE key scene)", owner="F", world="march",
         frames=[R + "/march846/frames/march_%05d.png"], cams=R + "/march846/frames", src_in=0.0, src_out=18.0,
         planned=18.0, cmd=REPO_SH + "bash render_march846.sh"),
    dict(id="B3", bridge=True, label="Bridge 3: over the emptied plain -> north over Trost and Wall Rose -> the fields",
         a="march", b="training", Ta=3.0, Tb=2.2,
         halves=dict(a=dict(world="march", state=("march", 18.0)), b=dict(world="interlude", state=("interlude", 7.0))),
         apex=[-260.0, -420.0, 960.0], apex_vel=[-200.0, 700.0, 0.0], apex_lens=28.0),
    dict(id="training", label="8 Training camp 847-850, graduation (interlude 7.0-20.47)", owner="B", world="interlude",
         frames=[INT_FRAMES], cams=R + "/interlude/raw", src_in=7.0, src_out=307 / 15, planned=307 / 15 - 7.0,
         cmd=REPO_SH + "bash render_interlude.sh", seg_time="interlude"),
    dict(id="B4", bridge=True, label="Bridge 4: graduation night -> climb into cloud -> dawn over Trost (850)",
         a="training", b="trost", Ta=3.0, Tb=3.0,
         halves=dict(a=dict(world="interlude", state=("interlude", 307 / 15)), b=dict(world="trost", state=("trost", 0.8))),
         apex=[-880.0, 880.0, 900.0], apex_vel=[260.0, -640.0, 0.0], apex_lens=28.0),
    dict(id="trost", label="9 Trost 850 (v 0.8 -> end)", owner="C/D", world="trost",
         frames=[R + "/trost/frames_p1/rt_%05d.png", R + "/trost/frames_p2/rt_%05d.png", R + "/trost/frames_p3/rt_%05d.png"],
         cams=None, src_in=0.8, src_out=None, planned=None,
         cmd=REPO_SH + "PART=1 bash render_trost.sh; PART=2 bash render_trost.sh; PART=3 bash render_trost.sh",
         note="frames are rt_<global index>; parts 1-3 cover v 0-52, 52-98, 98-end"),
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

# ======================================================================= bridges: path evaluation (shared with Blender)
D_LOOK = 300.0       # look point distance used to blend the look direction with a matched rate

def bridge_apex(br, half, anchor):
    """Apex (pos, vel, dir, lens) of one half in that half's world frame."""
    h = br["halves"][half]
    if "apex" in h:                      # cross-world bridge: apex relative to this half's own key
        pos = add(anchor["loc"], h["apex"]["rel"])
    else:
        pos = list(br["apex"])
    vel = list(br["apex_vel"])
    hd = unit([vel[0], vel[1], 0.0])
    d = unit([hd[0], hd[1], -0.62])      # forward and down: the cloud deck below / the land ahead
    return dict(loc=pos, vel=vel, dir=d, ddir=[0, 0, 0], lens=br.get("apex_lens", 28.0), dlnlens=0.0)

def bridge_eval(br, half, anchor, tb):
    """Camera (loc, dir, lens) at bridge time tb (0 = outgoing key, Ta = apex, Ta+Tb = incoming key) for one half.
    anchor = the segment key of that half (outgoing key for 'a', incoming key for 'b'), in that world's frame."""
    Ta, Tb = br["Ta"], br["Tb"]
    ap = bridge_apex(br, half, anchor)
    if half == "a":
        p0, p1, T, t = anchor, ap, Ta, tb
    else:
        p0, p1, T, t = ap, anchor, Tb, tb - Ta
    loc = herm(p0["loc"], p0["vel"], p1["loc"], p1["vel"], T, t)
    l0 = add(p0["loc"], mul(p0["dir"], D_LOOK)); l1 = add(p1["loc"], mul(p1["dir"], D_LOOK))
    m0 = add(p0["vel"], mul(p0.get("ddir", [0, 0, 0]), D_LOOK)); m1 = add(p1["vel"], mul(p1.get("ddir", [0, 0, 0]), D_LOOK))
    look = herm(l0, m0, l1, m1, T, t)
    lens = math.exp(herm(math.log(p0["lens"]), p0.get("dlnlens", 0.0), math.log(p1["lens"]), p1.get("dlnlens", 0.0), T, t))
    return loc, unit(sub(look, loc)), lens

def bridge_frames(br, fps):
    """[(j, tb, half)]: bridge-local frames j = 1 .. N (the keys at tb = 0 and Ta+Tb belong to the segments)."""
    n = int(round((br["Ta"] + br["Tb"]) * fps))
    return [(j, j / fps, "a" if j / fps < br["Ta"] - 1e-9 else "b") for j in range(1, n)]

def bridge_dir(br):
    return f"{BRIDGES}/{br['id']}"

def state_key(state):
    """Key of a half's anchor: ("interlude" | "march" | "trost" | "fall5", segment time)."""
    k = key_cached(f"{state[0]}_{state[1]:.3f}")
    if k:
        return k
    return seg_key("camps" if state[0] == "interlude" else state[0], state[1])

def bridge_check(br, fps=60):
    """Speeds along both halves with the best available keys (for the report)."""
    ka = seg_key(*br["halves"]["a"]["state"]) if br["halves"]["a"]["state"][0] != "interlude" else \
        seg_key("camps" if br["a"] == "camps" else "training", br["halves"]["a"]["state"][1])
    kb = seg_key(*br["halves"]["b"]["state"]) if br["halves"]["b"]["state"][0] != "interlude" else \
        seg_key("camps" if br["b"] == "camps" else "training", br["halves"]["b"]["state"][1])
    out = dict(id=br["id"], key_a=ka, key_b=kb)
    if not ka or not kb:
        return out
    sp, zs, prev, ph = [], [], None, None
    for j in range(0, int(round((br["Ta"] + br["Tb"]) * fps)) + 1):
        tb = j / fps; half = "a" if tb < br["Ta"] else "b"
        loc, d, lens = bridge_eval(br, half, ka if half == "a" else kb, tb)
        if prev is not None and half == ph:          # the halves may live in different world frames (B1)
            sp.append(norm(sub(loc, prev)) * fps)
        prev, ph = loc, half; zs.append(loc[2])
    out.update(v_max=max(sp), v_min=min(sp), z_max=max(zs), z_min=min(zs),
               v_a=norm(ka["vel"]), v_b=norm(kb["vel"]), v_apex=norm(br["apex_vel"]))
    return out

# ======================================================================= master build
def build(fps=15):
    """Resolved master timeline: [{id, kind, m_in, m_out, n, ...}] in master seconds (preview cards shortened)."""
    rows, m = [], 0.0
    for s in SEGMENTS:
        if s.get("bridge"):
            frs = bridge_frames(s, fps)
            have = sum(1 for j, _, _ in frs if os.path.exists(f"{bridge_dir(s)}/br_{j:05d}.png"))
            planned = s["Ta"] + s["Tb"] - 1 / fps
            r = dict(id=s["id"], kind="bridge", label=s["label"], n=len(frs), have=have, planned=planned,
                     dur=len(frs) / fps, Ta=s["Ta"], Tb=s["Tb"],
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
    print("\nBRIDGES")
    checks = []
    for s in SEGMENTS:
        if s.get("bridge"):
            c = bridge_check(s); checks.append(c)
            if "v_max" in c:
                print(f"  {s['id']}: {s['Ta'] + s['Tb']:.1f}s apex at {s['Ta']:.1f}s, |v| key {c['v_a']:.0f} -> apex {c['v_apex']:.0f} -> key {c['v_b']:.0f} m/s, "
                      f"max {c['v_max']:.0f}, z {c['z_min']:.0f}..{c['z_max']:.0f} m  ({s['label']})")
            else:
                print(f"  {s['id']}: keys incomplete (a={'ok' if c['key_a'] else 'eval in Blender'}, b={'ok' if c['key_b'] else 'eval in Blender'})  ({s['label']})")
    if write:
        os.makedirs(MASTER, exist_ok=True)
        json.dump(dict(fps=fps, rows=rows, keys=keys, planned_total=planned_total,
                       bridges=[{k: v for k, v in c.items()} for c in checks]),
                  open(MASTER + "/master_timeline.json", "w"), indent=1, default=str)
    return rows, planned_total

if __name__ == "__main__":
    fps = 15
    if "--fps" in sys.argv:
        fps = int(sys.argv[sys.argv.index("--fps") + 1])
    report(fps)
